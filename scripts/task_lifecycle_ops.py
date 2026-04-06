from __future__ import annotations

import argparse

from governance_lib import (
    CURRENT_TASK_FILE,
    GovernanceError,
    append_runlog_bullets,
    build_current_task_payload,
    collect_split_errors,
    current_branch,
    dump_yaml,
    ensure_clean_worktree,
    find_repo_root,
    infer_default_automation_mode,
    infer_default_topology,
    iso_now,
    load_current_task,
    load_task_policy,
    load_task_registry,
    load_worktree_registry,
    missing_required_tests,
    sync_task_artifacts,
    task_map,
    task_parallelism_plan,
    task_required_tests_for_matrix,
    read_text,
    validate_task,
    worktree_map,
)
from governance_markdown import extract_markdown_fields
from orchestration_runtime import record_session_event, runtime_status_for_task
from task_closeout import assess_live_closeout
from task_coordination_lease import (
    claim_coordination_lease,
    coordination_thread_id,
    current_session_id,
    ensure_closeout_write_lease,
    release_coordination_lease,
)
from task_handoff import ensure_handoff_file, write_handoff
from task_rendering import (
    find_task,
    load_roadmap_state,
    pause_other_doing_tasks,
    persist_activation_state,
    persist_idle_state,
    resolve_query_task,
    update_current_task_if_active,
    update_runlog_file,
    update_task_file,
    upsert_coordination_entry,
)


def cmd_new(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task_policy = load_task_policy(root)
    tasks = registry.setdefault("tasks", [])
    if any(task["task_id"] == args.task_id for task in tasks):
        raise GovernanceError(f"task already exists: {args.task_id}")
    task = {
        "task_id": args.task_id,
        "title": args.title,
        "status": args.status,
        "task_kind": args.task_kind,
        "execution_mode": args.execution_mode
        or ("shared_coordination" if args.task_kind == "coordination" else "isolated_worktree"),
        "parent_task_id": args.parent_task_id,
        "stage": args.stage,
        "branch": args.branch or f"feat/{args.task_id}-work",
        "size_class": args.size_class,
        "automation_mode": args.automation_mode or "",
        "worker_state": args.worker_state,
        "blocked_reason": None,
        "last_reported_at": iso_now(),
        "topology": args.topology or "",
        "allowed_dirs": args.allowed_dirs,
        "reserved_paths": args.reserved_paths,
        "planned_write_paths": args.planned_write_paths,
        "planned_test_paths": args.planned_test_paths,
        "required_tests": args.required_tests,
        "task_file": f"docs/governance/tasks/{args.task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{args.task_id}-RUNLOG.md",
        "lane_count": 1,
        "lane_index": None,
        "parallelism_plan_id": None,
        "review_bundle_status": "not_applicable",
        "successor_state": args.successor_state,
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
    }
    if not task["required_tests"]:
        task["required_tests"] = task_required_tests_for_matrix(root, task)
    task["automation_mode"] = task["automation_mode"] or infer_default_automation_mode(task, task_policy)
    plan = task_parallelism_plan(task, task_policy)
    task["topology"] = task["topology"] or plan["topology"]
    if task["task_kind"] == "coordination":
        task["lane_count"] = plan["lane_count"]
        task["parallelism_plan_id"] = plan["parallelism_plan_id"]
    validate_task(task)
    tasks.append(task)
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_task_file(root, task)
    update_runlog_file(root, task)
    ensure_handoff_file(root, task)
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] created task {args.task_id}")
    return 0


def cmd_activate(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    roadmap_frontmatter, roadmap_body = load_roadmap_state(root)
    task = find_task(registry["tasks"], args.task_id)
    if task["task_kind"] != "coordination":
        raise GovernanceError("only coordination tasks can be activated in the main worktree")
    ensure_clean_worktree(root)
    if current_branch(root) != task["branch"]:
        raise GovernanceError(f"branch mismatch: expected {task['branch']}, got {current_branch(root)}")
    claim_coordination_lease(root, task, reason="activate")
    touched_tasks = pause_other_doing_tasks(registry["tasks"], task["task_id"])
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    if task["activated_at"] is None:
        task["activated_at"] = iso_now()
    registry["updated_at"] = iso_now()
    upsert_coordination_entry(worktrees, task, root)
    worktrees["updated_at"] = iso_now()
    persist_activation_state(root, registry, worktrees, task, roadmap_frontmatter, roadmap_body, touched_tasks)
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        next_step="Continue the scoped implementation and keep the control plane aligned.",
        next_tests=list(task.get("required_tests") or []),
        candidate_write_paths=list(task.get("planned_write_paths") or []),
        candidate_test_paths=list(task.get("planned_test_paths") or []),
        resume_notes=["Task activated in the main coordination worktree."],
        append_resume_notes=True,
    )
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="activate",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] activated {task['task_id']}")
    return 0


def cmd_pause(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    task = find_task(registry["tasks"], args.task_id or current_task["current_task_id"])
    claim_coordination_lease(root, task, reason="pause")
    task["status"] = "paused"
    task["worker_state"] = "idle"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is not None:
        entry["status"] = "paused"
        worktrees["updated_at"] = iso_now()
        dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    if current_task["current_task_id"] == task["task_id"]:
        dump_yaml(root / CURRENT_TASK_FILE, build_current_task_payload(task, "Task paused; waiting for explicit reactivation."))
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        next_step="Reactivate the task before making further changes.",
        next_tests=list(task.get("required_tests") or []),
        resume_notes=["Task paused; resume requires explicit reactivation."],
        append_resume_notes=True,
    )
    sync_task_artifacts(root, registry, [task["task_id"]])
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="pause",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] paused {task['task_id']}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    task = find_task(registry["tasks"], args.task_id or current_task["current_task_id"])
    is_live_top_level_current = (
        current_task.get("current_task_id") == task["task_id"]
        and task["task_kind"] == "coordination"
        and task.get("parent_task_id") is None
    )
    lease = _close_command_lease(root, registry, worktrees, current_task, task, is_live_top_level_current)
    if lease.get("auto_takeover"):
        append_runlog_bullets(
            root,
            task,
            "Execution Log",
            [f"`{iso_now()}`: automatic lease takeover previous_owner=`{lease.get('previous_owner_session_id')}` reason=`close`"],
        )
    missing = missing_required_tests(root, task)
    if missing:
        raise GovernanceError(f"required tests missing from runlog: {', '.join(missing)}")
    task["status"] = "done"
    task["worker_state"] = "completed"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    task["closed_at"] = iso_now()
    registry["updated_at"] = iso_now()
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is not None:
        entry["status"] = "closed"
        if entry["work_mode"] == "execution":
            entry["cleanup_state"] = "pending"
    worktrees["updated_at"] = iso_now()
    touched_task_ids = [task["task_id"]]
    if is_live_top_level_current:
        roadmap_frontmatter, roadmap_body = load_roadmap_state(root)
        persist_idle_state(root, registry, worktrees, roadmap_frontmatter, roadmap_body, touched_task_ids)
    else:
        dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
        dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
        if current_task.get("current_task_id") == task["task_id"]:
            dump_yaml(
                root / CURRENT_TASK_FILE,
                build_current_task_payload(task, "Waiting for explicit successor activation."),
            )
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        remaining_items=[],
        next_step="No further implementation is required; this task is closed.",
        current_risks=[],
        resume_notes=["Task closed."],
        append_resume_notes=True,
    )
    release_coordination_lease(root, task, reason="close")
    sync_task_artifacts(root, registry, touched_task_ids)
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="close",
        mode="manual",
        writer_state="writable",
        current_task_id=None if is_live_top_level_current else task["task_id"],
        continue_intent=None,
        runtime_status="idle" if is_live_top_level_current else runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] closed {task['task_id']}")
    return 0


def _close_command_lease(
    root,
    registry: dict,
    worktrees: dict,
    current_task: dict,
    task: dict,
    is_live_top_level_current: bool,
) -> dict[str, object]:
    allow_takeover = False
    if is_live_top_level_current:
        closeout = assess_live_closeout(
            root,
            registry=registry,
            worktrees=worktrees,
            current_payload=current_task,
            current_task=task,
        )
        allow_takeover = closeout["status"] == "ready"
    return ensure_closeout_write_lease(root, task, reason="close", allow_takeover=allow_takeover)


def cmd_can_start(args: argparse.Namespace) -> int:
    root = find_repo_root()
    task, _, worktrees = resolve_query_task(root, args.task_id)
    current = load_current_task(root)
    if current.get("current_task_id") is None:
        raise GovernanceError("no live current task is startable")
    if task["task_id"] != current["current_task_id"]:
        raise GovernanceError("can-start only supports the live current task")
    if task["status"] in {"done", "review"}:
        raise GovernanceError("current task is not startable in done/review state")
    if current_branch(root) != task["branch"]:
        raise GovernanceError("current branch does not match the live task branch")
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is None or entry.get("status") != "active":
        raise GovernanceError("live current task does not have an active worktree entry")
    print(f"[OK] can-start {task['task_id']}")
    return 0


def cmd_can_close(args: argparse.Namespace) -> int:
    root = find_repo_root()
    task, _, _ = resolve_query_task(root, args.task_id)
    if task["status"] in {"queued", "paused", "blocked"}:
        raise GovernanceError("task cannot close from queued/paused/blocked state")
    missing = missing_required_tests(root, task)
    if missing:
        raise GovernanceError(f"required tests missing from runlog: {', '.join(missing)}")
    print(f"[OK] can-close {task['task_id']}")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    if args.write:
        sync_task_artifacts(root, registry)
        dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
        print("[OK] synced task and runlog metadata blocks")
    else:
        print("[OK] sync dry run: no files written")
    return 0


def _coerce_reconciled_value(key: str, value: str):
    if value == "null":
        return None
    if key == "lane_count":
        return int(value)
    if key == "lane_index":
        return None if value == "null" else int(value)
    return value


def cmd_reconcile_ledgers(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    tasks_by_id = task_map(registry)
    touched: list[str] = []
    for task in registry.get("tasks", []):
        task_path = root / task["task_file"]
        if not task_path.exists():
            continue
        fields = extract_markdown_fields(read_text(task_path))
        changed = False
        for key in ("status", "stage", "branch", "worker_state", "lane_count", "lane_index", "parallelism_plan_id", "review_bundle_status"):
            if key not in fields:
                continue
            value = _coerce_reconciled_value(key, fields[key])
            if task.get(key) != value:
                task[key] = value
                changed = True
        if changed:
            task["last_reported_at"] = iso_now()
            touched.append(task["task_id"])
    if current_task.get("current_task_id") is not None:
        task = find_task(registry["tasks"], current_task["current_task_id"])
        for key in (
            "title",
            "status",
            "task_kind",
            "execution_mode",
            "stage",
            "branch",
            "size_class",
            "automation_mode",
            "worker_state",
            "topology",
            "allowed_dirs",
            "reserved_paths",
            "planned_write_paths",
            "planned_test_paths",
            "required_tests",
            "task_file",
            "runlog_file",
            "lane_count",
            "lane_index",
            "parallelism_plan_id",
            "review_bundle_status",
        ):
            if task.get(key) != current_task.get(key):
                task[key] = current_task.get(key)
                if task["task_id"] not in touched:
                    touched.append(task["task_id"])
        from task_rendering import upsert_coordination_entry

        upsert_coordination_entry(worktrees, task, root)
    else:
        for entry in worktrees.get("entries", []):
            if entry.get("work_mode") == "coordination" and entry.get("status") == "active":
                entry["status"] = "closed"
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    if args.write:
        dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
        dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
        if touched:
            sync_task_artifacts(root, registry, touched)
        print(f"[OK] reconciled ledgers from truth sources for: {', '.join(touched) if touched else 'no task fields changed'}")
    else:
        print(f"[OK] reconcile dry run: {', '.join(touched) if touched else 'no task fields changed'}")
    return 0


def cmd_split_check(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task_policy = load_task_policy(root)
    tasks = [
        task
        for task in registry.get("tasks", [])
        if task.get("parent_task_id") == args.parent_task_id and task.get("task_kind") == "execution"
    ]
    errors = collect_split_errors(tasks, task_policy)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print(f"[OK] split-check passed for {args.parent_task_id}")
    return 0


def cmd_decide_topology(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task_policy = load_task_policy(root)
    task = find_task(registry["tasks"], args.task_id)
    plan = task_parallelism_plan(task, task_policy)
    task["topology"] = plan["topology"]
    if task["task_kind"] == "coordination":
        task["lane_count"] = plan["lane_count"]
        task["parallelism_plan_id"] = plan["parallelism_plan_id"]
    topology, reason = task["topology"], plan["reason"]
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "Task topology updated; continue under the live task package.")
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] {task['task_id']} topology={topology} reason={reason}")
    return 0
