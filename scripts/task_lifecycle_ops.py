from __future__ import annotations

import argparse

from governance_lib import (
    CURRENT_TASK_FILE,
    GovernanceError,
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
    load_task_registry,
    load_worktree_registry,
    missing_required_tests,
    sync_task_artifacts,
    task_required_tests_for_matrix,
    validate_task,
    worktree_map,
)
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
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
    }
    task["automation_mode"] = task["automation_mode"] or infer_default_automation_mode(task)
    inferred_topology, _ = infer_default_topology(task)
    task["topology"] = task["topology"] or inferred_topology
    if not task["required_tests"]:
        task["required_tests"] = task_required_tests_for_matrix(root, task)
    validate_task(task)
    tasks.append(task)
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_task_file(root, task)
    update_runlog_file(root, task)
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
    print(f"[OK] activated {task['task_id']}")
    return 0


def cmd_pause(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    task = find_task(registry["tasks"], args.task_id or current_task["current_task_id"])
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
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] paused {task['task_id']}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    task = find_task(registry["tasks"], args.task_id or current_task["current_task_id"])
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
    is_live_top_level_current = (
        current_task.get("current_task_id") == task["task_id"]
        and task["task_kind"] == "coordination"
        and task.get("parent_task_id") is None
    )
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
        sync_task_artifacts(root, registry, touched_task_ids)
    print(f"[OK] closed {task['task_id']}")
    return 0


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


def cmd_split_check(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    tasks = [
        task
        for task in registry.get("tasks", [])
        if task.get("parent_task_id") == args.parent_task_id and task.get("task_kind") == "execution"
    ]
    errors = collect_split_errors(tasks)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print(f"[OK] split-check passed for {args.parent_task_id}")
    return 0


def cmd_decide_topology(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    topology, reason = infer_default_topology(task)
    task["topology"] = topology
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "Task topology updated; continue under the live task package.")
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] {task['task_id']} topology={topology} reason={reason}")
    return 0
