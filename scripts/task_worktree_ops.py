from __future__ import annotations

import argparse
from pathlib import Path

from governance_lib import (
    DEFAULT_RUNTIME_PROMPT_PROFILE,
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    branch_exists,
    choose_worker_owner,
    collect_active_execution_errors,
    current_branch,
    dynamic_lane_ceiling,
    display_path,
    dump_yaml,
    find_repo_root,
    git,
    iso_now,
    load_current_task,
    load_task_policy,
    load_task_registry,
    load_worktree_registry,
    safe_rmtree,
    sync_task_artifacts,
    task_map,
    worktree_map,
)
from child_execution_flow import (
    build_execution_context,
    cleanup_transient_child_artifacts,
    mirror_governance_ledgers_to_worktree,
    persist_child_workflow,
    record_baseline_results,
    run_baseline_checks,
    sync_entry_workflow_state,
)
from orchestration_runtime import update_execution_runtime_entry
from task_rendering import find_task


WORKTREE_POOL_FILE = Path("docs/governance/WORKTREE_POOL.yaml")


def _load_worktree_pool(root: Path) -> dict:
    path = root / WORKTREE_POOL_FILE
    if not path.exists():
        return {"version": "0.1", "slots": []}
    from governance_runtime import load_yaml

    payload = load_yaml(path) or {}
    payload.setdefault("slots", [])
    return payload


def _write_worktree_pool(root: Path, pool: dict) -> None:
    pool["updated_at"] = iso_now()
    dump_yaml(root / WORKTREE_POOL_FILE, pool)


def _pool_slot_path(root: Path, slot: dict) -> Path:
    raw_path = Path(str(slot.get("path") or ""))
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (root / raw_path).resolve()


def _pool_idle_branch(slot: dict) -> str:
    return str(slot.get("idle_branch") or f"codex/{slot['slot_id']}-idle")


def prewarm_pool_slot(root: Path, slot: dict) -> Path:
    destination = _pool_slot_path(root, slot)
    idle_branch = _pool_idle_branch(slot)
    if destination.exists() and (destination / ".git").exists():
        slot["idle_branch"] = idle_branch
        slot["branch"] = git(destination, "branch", "--show-current").stdout.strip() or idle_branch
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    if branch_exists(root, idle_branch):
        git(root, "worktree", "add", str(destination), idle_branch)
    else:
        git(root, "worktree", "add", "-b", idle_branch, str(destination), "HEAD")
    slot["idle_branch"] = idle_branch
    slot["branch"] = idle_branch
    return destination


def reuse_pool_slot_worktree(root: Path, task: dict, slot: dict, worker_owner: str | None) -> Path:
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task_policy = load_task_policy(root)
    tasks_by_id = task_map(registry)
    parent_task = resolve_parent_task_for_execution(root, tasks_by_id, task)
    destination = prewarm_pool_slot(root, slot)
    validate_worktree_create_request(root, task, tasks_by_id, worktrees, destination)
    dirty = git(destination, "status", "--porcelain", "--untracked-files=all", check=False).stdout.splitlines()
    if dirty:
        raise GovernanceError(f"pool slot worktree is dirty: {slot['slot_id']}")
    if branch_exists(root, task["branch"]):
        git(destination, "switch", task["branch"])
    else:
        git(destination, "switch", "-c", task["branch"])
    assigned_owner = worker_owner or slot.get("worker_owner")
    context = write_execution_context(destination, task, parent_task, assigned_owner)
    upsert_execution_entry(worktrees, task, destination, assigned_owner)
    sync_entry_workflow_state(worktree_map(worktrees)[task["task_id"]], context)
    mirror_governance_ledgers_to_worktree(root, destination, registry, worktrees, task)
    update_execution_runtime_entry(
        root,
        task["task_id"],
        lane_session_id=None,
        executor_status="prepared",
        started_at=None,
        last_heartbeat_at=None,
        last_result=None,
    )
    worktrees["updated_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, [task["task_id"]])
    slot["branch"] = task["branch"]
    return destination


def _release_pool_slot_for_path(root: Path, destination: Path, *, now: str) -> None:
    pool = _load_worktree_pool(root)
    updated = False
    for slot in pool.get("slots", []):
        slot_path = Path(str(slot.get("path") or "")).resolve() if slot.get("path") else None
        if slot_path != destination:
            continue
        try:
            if destination.exists():
                git(root, "worktree", "remove", "--force", str(destination))
            prewarm_pool_slot(root, slot)
        except GovernanceError:
            slot["status"] = "blocked"
            slot["last_released_at"] = now
            updated = True
            break
        slot["status"] = "idle"
        slot["current_task_id"] = None
        slot["branch"] = _pool_idle_branch(slot)
        slot["last_released_at"] = now
        updated = True
        break
    if updated:
        _write_worktree_pool(root, pool)


def cmd_prewarm_worktree_pool(args: argparse.Namespace) -> int:
    root = find_repo_root()
    pool = _load_worktree_pool(root)
    if not pool.get("slots"):
        raise GovernanceError(f"worktree pool is missing or empty: {WORKTREE_POOL_FILE}")
    warmed: list[str] = []
    for slot in pool.get("slots", []):
        if args.slot_id and slot.get("slot_id") != args.slot_id:
            continue
        if slot.get("status") not in {"idle", "assigned"}:
            continue
        destination = prewarm_pool_slot(root, slot)
        slot["status"] = "idle"
        slot["path"] = display_path(destination)
        warmed.append(slot["slot_id"])
    _write_worktree_pool(root, pool)
    if not warmed:
        print("[OK] no idle pool slots needed prewarming")
        return 0
    print(f"[OK] prewarmed worktree pool slots: {', '.join(warmed)}")
    return 0


def _reset_execution_runtime(entry: dict, worker_owner: str) -> None:
    entry["worker_owner"] = worker_owner
    entry["lane_session_id"] = None
    entry["executor_status"] = "prepared"
    entry["started_at"] = None
    entry["last_heartbeat_at"] = None
    entry["last_result"] = None


def validate_worktree_create_request(root: Path, task: dict, tasks_by_id: dict, worktrees: dict, destination: Path) -> None:
    task_policy = load_task_policy(root)
    if task["task_kind"] != "execution" or task["execution_mode"] != "isolated_worktree":
        raise GovernanceError("worktree-create only supports isolated execution tasks")
    if collect_active_execution_errors(tasks_by_id, worktrees, task_policy):
        raise GovernanceError("existing active execution conflicts must be resolved before creating a new worktree")
    active_count = sum(1 for entry in worktrees.get("entries", []) if entry.get("work_mode") == "execution" and entry.get("status") == "active")
    lane_ceiling = dynamic_lane_ceiling(task_policy)
    if active_count >= lane_ceiling:
        raise GovernanceError(f"active execution worktrees already at hard limit {lane_ceiling}")
    if destination == root.resolve() or destination.is_relative_to(root.resolve()):
        raise GovernanceError("execution worktree path must be outside the main coordination directory")


def create_worktree_checkout(root: Path, task: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if current_branch(root) and git(root, "branch", "--list", task["branch"]).stdout.strip():
        git(root, "worktree", "add", str(destination), task["branch"])
        return
    git(root, "worktree", "add", "-b", task["branch"], str(destination), "HEAD")


def write_execution_context(destination: Path, task: dict, parent_task: dict, worker_owner: str) -> dict:
    context = build_execution_context(destination, task, parent_task, worker_owner)
    context["runtime_prompt_profile"] = DEFAULT_RUNTIME_PROMPT_PROFILE
    dump_yaml(destination / EXECUTION_CONTEXT_FILE, context)
    return context


def resolve_parent_task_for_execution(root: Path, tasks_by_id: dict, task: dict) -> dict:
    parent_task = tasks_by_id.get(task.get("parent_task_id"))
    if parent_task is not None:
        return parent_task
    current_payload = load_current_task(root)
    current_task_id = current_payload.get("current_task_id")
    current_task = tasks_by_id.get(current_task_id) if current_task_id else None
    if current_task is not None:
        return current_task
    return {"branch": current_branch(root)}


def upsert_execution_entry(worktrees: dict, task: dict, destination: Path, worker_owner: str) -> None:
    current_entry = worktree_map(worktrees).get(task["task_id"])
    if current_entry is None:
        entry = {
            "task_id": task["task_id"],
            "work_mode": "execution",
            "parent_task_id": task.get("parent_task_id"),
            "branch": task["branch"],
            "path": display_path(destination),
            "status": "active",
            "cleanup_state": "pending",
            "cleanup_attempts": 0,
            "last_cleanup_error": None,
        }
        _reset_execution_runtime(entry, worker_owner)
        entry["workflow_state"] = {}
        worktrees.setdefault("entries", []).append(entry)
        return
    current_entry["work_mode"] = "execution"
    current_entry["parent_task_id"] = task.get("parent_task_id")
    current_entry["branch"] = task["branch"]
    current_entry["path"] = display_path(destination)
    current_entry["status"] = "active"
    current_entry["cleanup_state"] = "pending"
    current_entry["cleanup_attempts"] = int(current_entry.get("cleanup_attempts", 0))
    current_entry["last_cleanup_error"] = None
    _reset_execution_runtime(current_entry, worker_owner)
    current_entry.setdefault("workflow_state", {})


def cmd_worktree_create(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task_policy = load_task_policy(root)
    tasks_by_id = task_map(registry)
    task = tasks_by_id.get(args.task_id)
    if task is None:
        raise GovernanceError(f"unknown task: {args.task_id}")
    parent_task = resolve_parent_task_for_execution(root, tasks_by_id, task)
    destination = Path(args.path).resolve()
    validate_worktree_create_request(root, task, tasks_by_id, worktrees, destination)
    create_worktree_checkout(root, task, destination)
    worker_owner = args.worker_owner or choose_worker_owner(worktrees.get("entries", []), task_policy)
    context = write_execution_context(destination, task, parent_task, worker_owner)
    upsert_execution_entry(worktrees, task, destination, worker_owner)
    sync_entry_workflow_state(worktree_map(worktrees)[task["task_id"]], context)
    mirror_governance_ledgers_to_worktree(root, destination, registry, worktrees, task)
    update_execution_runtime_entry(
        root,
        task["task_id"],
        lane_session_id=None,
        executor_status="prepared",
        started_at=None,
        last_heartbeat_at=None,
        last_result=None,
    )
    worktrees["updated_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] created execution worktree for {task['task_id']} at {display_path(destination)}")
    return 0


def cmd_prepare_child_execution(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task_policy = load_task_policy(root)
    tasks_by_id = task_map(registry)
    task = tasks_by_id.get(args.task_id)
    if task is None:
        raise GovernanceError(f"unknown task: {args.task_id}")
    parent_task = tasks_by_id.get(task.get("parent_task_id"))
    if parent_task is None:
        raise GovernanceError(f"missing parent task for execution prepare: {task.get('parent_task_id')}")
    destination = Path(args.path).resolve()
    validate_worktree_create_request(root, task, tasks_by_id, worktrees, destination)
    create_worktree_checkout(root, task, destination)
    worker_owner = args.worker_owner or choose_worker_owner(worktrees.get("entries", []), task_policy)
    context = write_execution_context(destination, task, parent_task, worker_owner)
    upsert_execution_entry(worktrees, task, destination, worker_owner)
    entry = worktree_map(worktrees)[task["task_id"]]
    sync_entry_workflow_state(entry, context)
    mirror_governance_ledgers_to_worktree(root, destination, registry, worktrees, task)
    ok, results = run_baseline_checks(destination, list(context["workflow_state"]["baseline_checks"]["commands"]))
    record_baseline_results(context["workflow_state"], results, passed=ok)
    task["status"] = "doing" if ok else "blocked"
    task["worker_state"] = "idle" if ok else "blocked"
    task["blocked_reason"] = None if ok else f"child_prepare_failed: {results[-1]['command']}"
    task["last_reported_at"] = iso_now()
    context["workflow_state"]["phase"] = "prepared" if ok else "prepare_blocked"
    context["workflow_state"]["prepared_at"] = iso_now()
    update_execution_runtime_entry(
        root,
        task["task_id"],
        lane_session_id=None,
        executor_status="prepared" if ok else "dispatch_failed",
        started_at=None,
        last_heartbeat_at=None,
        last_result="prepare-child-execution" if ok else (results[-1]["output"] if results else "prepare-child-execution failed"),
    )
    bullets = [
        f"`{iso_now()}`: child prepare {'passed' if ok else 'failed'} at `{display_path(destination)}`",
        *[
            f"`{item['command']}` -> {'PASS' if item['passed'] else 'FAIL'}"
            for item in results
        ],
    ]
    persist_child_workflow(
        root,
        registry,
        worktrees,
        task,
        entry,
        context,
        runlog_section="Execution Log",
        bullets=bullets,
    )
    if not ok:
        print(f"[ERROR] child prepare failed for {task['task_id']}")
        return 1
    print(f"[OK] prepared child execution for {task['task_id']} at {display_path(destination)}")
    return 0


def cmd_worktree_release(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = task_map(registry).get(args.task_id)
    if task is None:
        raise GovernanceError(f"unknown task: {args.task_id}")
    entry = worktree_map(worktrees).get(args.task_id)
    if entry is None or entry.get("work_mode") != "execution":
        raise GovernanceError(f"no execution worktree registered for {args.task_id}")
    destination = Path(entry["path"]).resolve()
    if destination.exists():
        cleanup_transient_child_artifacts(destination, task)
        context_path = destination / EXECUTION_CONTEXT_FILE
        if context_path.exists():
            context_path.unlink()
        dirty = git(destination, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
        if dirty:
            raise GovernanceError("execution worktree has uncommitted changes; release refused")
        git(root, "worktree", "remove", str(destination))
        if destination.exists():
            safe_rmtree(destination)
    _release_pool_slot_for_path(root, destination, now=iso_now())
    entry["status"] = "closed"
    entry["cleanup_state"] = "done"
    entry["last_cleanup_error"] = None
    worktrees["updated_at"] = iso_now()
    if task["status"] != "done":
        task["status"] = "paused"
        task["worker_state"] = "idle"
        task["last_reported_at"] = iso_now()
        registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] released execution worktree for {args.task_id}")
    return 0


def cmd_cleanup_orphans(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    cleaned: list[str] = []
    blocked: list[str] = []
    for entry in worktrees.get("entries", []):
        if entry.get("work_mode") != "execution" or (args.task_id and entry["task_id"] != args.task_id):
            continue
        if entry["status"] != "closed" or entry["cleanup_state"] not in {"pending", "blocked"}:
            continue
        entry["cleanup_attempts"] = int(entry.get("cleanup_attempts", 0)) + 1
        destination = Path(entry["path"]).resolve()
        try:
            if destination.exists():
                git(root, "worktree", "remove", "--force", str(destination))
                if destination.exists():
                    safe_rmtree(destination)
            entry["cleanup_state"] = "done"
            entry["last_cleanup_error"] = None
            cleaned.append(entry["task_id"])
        except (GovernanceError, OSError) as error:
            entry["cleanup_state"] = "blocked_manual" if entry["cleanup_attempts"] >= 3 else "blocked"
            entry["last_cleanup_error"] = str(error)
            blocked.append(f"{entry['task_id']}: {error}")
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    for task_id in cleaned:
        task = task_map(registry).get(task_id)
        if task is not None:
            from governance_lib import append_runlog_bullets

            append_runlog_bullets(root, task, "执行记录", [f"`{iso_now()}`：cleanup-orphans completed"])
    print(f"[OK] cleaned orphan worktrees: {', '.join(cleaned)}" if cleaned else "[OK] no orphan worktrees cleaned")
    for item in blocked:
        print(f"[BLOCKED] {item}")
    return 0 if not blocked else 1
