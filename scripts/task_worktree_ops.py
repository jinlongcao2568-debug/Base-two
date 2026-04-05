from __future__ import annotations

import argparse
from pathlib import Path

from governance_lib import (
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    choose_worker_owner,
    collect_active_execution_errors,
    current_branch,
    dynamic_lane_ceiling,
    display_path,
    dump_yaml,
    find_repo_root,
    git,
    iso_now,
    load_task_policy,
    load_task_registry,
    load_worktree_registry,
    safe_rmtree,
    sync_task_artifacts,
    task_map,
    worktree_map,
)
from task_rendering import find_task


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


def write_execution_context(destination: Path, task: dict, worker_owner: str) -> None:
    dump_yaml(
        destination / EXECUTION_CONTEXT_FILE,
        {
            "task_id": task["task_id"],
            "parent_task_id": task.get("parent_task_id"),
            "branch": task["branch"],
            "worktree_path": display_path(destination),
            "worker_owner": worker_owner,
            "allowed_dirs": task.get("allowed_dirs", []),
            "reserved_paths": task.get("reserved_paths", []),
            "planned_write_paths": task.get("planned_write_paths", []),
            "planned_test_paths": task.get("planned_test_paths", []),
            "required_tests": task.get("required_tests", []),
        },
    )


def upsert_execution_entry(worktrees: dict, task: dict, destination: Path, worker_owner: str) -> None:
    current_entry = worktree_map(worktrees).get(task["task_id"])
    if current_entry is None:
        worktrees.setdefault("entries", []).append({"task_id": task["task_id"], "work_mode": "execution", "parent_task_id": task.get("parent_task_id"), "branch": task["branch"], "path": display_path(destination), "status": "active", "cleanup_state": "pending", "cleanup_attempts": 0, "last_cleanup_error": None, "worker_owner": worker_owner})
        return
    current_entry["work_mode"] = "execution"
    current_entry["parent_task_id"] = task.get("parent_task_id")
    current_entry["branch"] = task["branch"]
    current_entry["path"] = display_path(destination)
    current_entry["status"] = "active"
    current_entry["cleanup_state"] = "pending"
    current_entry["worker_owner"] = worker_owner


def cmd_worktree_create(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task_policy = load_task_policy(root)
    tasks_by_id = task_map(registry)
    task = tasks_by_id.get(args.task_id)
    if task is None:
        raise GovernanceError(f"unknown task: {args.task_id}")
    destination = Path(args.path).resolve()
    validate_worktree_create_request(root, task, tasks_by_id, worktrees, destination)
    create_worktree_checkout(root, task, destination)
    worker_owner = args.worker_owner or choose_worker_owner(worktrees.get("entries", []), task_policy)
    write_execution_context(destination, task, worker_owner)
    upsert_execution_entry(worktrees, task, destination, worker_owner)
    worktrees["updated_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] created execution worktree for {task['task_id']} at {display_path(destination)}")
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
        context_path = destination / EXECUTION_CONTEXT_FILE
        if context_path.exists():
            context_path.unlink()
        dirty = git(destination, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
        if dirty:
            raise GovernanceError("execution worktree has uncommitted changes; release refused")
        git(root, "worktree", "remove", str(destination))
        if destination.exists():
            safe_rmtree(destination)
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
