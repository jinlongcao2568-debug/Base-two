from __future__ import annotations

import argparse

from governance_lib import (
    GovernanceError,
    append_runlog_bullets,
    dump_yaml,
    find_repo_root,
    iso_now,
    load_task_registry,
    load_worktree_registry,
    missing_required_tests,
    sync_task_artifacts,
    task_map,
    worktree_map,
)
from task_rendering import (
    enforce_execution_split_guards,
    find_task,
    record_blocked_split,
    update_current_task_if_active,
)


def cmd_worker_start(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    try:
        enforce_execution_split_guards(registry, task)
    except GovernanceError:
        record_blocked_split(root, registry, task)
        raise
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    if task["activated_at"] is None:
        task["activated_at"] = iso_now()
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is not None:
        entry["status"] = "active"
        if args.worker_owner:
            entry["worker_owner"] = args.worker_owner
        if args.path:
            entry["path"] = args.path
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    update_current_task_if_active(root, task, "worker 已接手；按当前任务包继续推进。")
    append_runlog_bullets(root, task, "执行记录", [f"`{iso_now()}`：worker-start owner=`{args.worker_owner or 'unknown'}`"])
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker started {task['task_id']}")
    return 0


def cmd_worker_report(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    task["worker_state"] = "running"
    if task["status"] == "queued":
        task["status"] = "doing"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "worker 正在推进，等待进一步回报。")
    bullets = [f"`{iso_now()}`：{note}" for note in args.note]
    if bullets:
        append_runlog_bullets(root, task, "执行记录", bullets)
    if args.tests:
        append_runlog_bullets(root, task, "测试记录", [f"`{test}`" for test in args.tests])
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker reported {task['task_id']}")
    return 0


def cmd_worker_blocked(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    task["status"] = "blocked"
    task["worker_state"] = "blocked"
    task["blocked_reason"] = args.reason
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "任务已 blocked；等待人工协调或显式解阻。")
    append_runlog_bullets(root, task, "风险与阻塞", [f"`{iso_now()}`：{args.reason}"])
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker blocked {task['task_id']}")
    return 0


def cmd_worker_finish(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    task["status"] = "review"
    task["worker_state"] = "review_pending"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "worker 已完成候选交付；等待自动收口或评审。")
    append_runlog_bullets(root, task, "执行记录", [f"`{iso_now()}`：worker-finish `{args.summary}`"])
    if args.tests:
        append_runlog_bullets(root, task, "测试记录", [f"`{test}`" for test in args.tests])
    if args.candidate_paths:
        append_runlog_bullets(root, task, "候选交付", [f"`{path}`" for path in args.candidate_paths])
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker finished {task['task_id']}")
    return 0


def cmd_auto_close_children(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    closed: list[str] = []
    skipped: list[str] = []
    for task in registry.get("tasks", []):
        if task.get("parent_task_id") != args.parent_task_id or task["task_kind"] != "execution":
            continue
        if task["worker_state"] not in {"review_pending", "completed"} or task["status"] not in {"review", "doing"}:
            continue
        missing = missing_required_tests(root, task)
        if missing:
            skipped.append(f"{task['task_id']}: missing tests {', '.join(missing)}")
            continue
        task["status"] = "done"
        task["worker_state"] = "completed"
        task["closed_at"] = iso_now()
        task["last_reported_at"] = iso_now()
        entry = worktree_map(worktrees).get(task["task_id"])
        if entry is not None:
            entry["status"] = "closed"
            entry["cleanup_state"] = "pending"
        append_runlog_bullets(root, task, "关账结论", [f"`{iso_now()}`：auto-close-children 通过"])
        closed.append(task["task_id"])
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, closed)
    print(f"[OK] auto-closed children: {', '.join(closed)}" if closed else "[OK] no child tasks closed")
    for item in skipped:
        print(f"[SKIP] {item}")
    return 0
