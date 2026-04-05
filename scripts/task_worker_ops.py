from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

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
    if task["task_kind"] == "execution":
        task["review_bundle_status"] = "not_applicable"
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
    update_current_task_if_active(root, task, "worker 宸叉帴鎵嬶紱鎸夊綋鍓嶄换鍔″寘缁х画鎺ㄨ繘銆?")
    append_runlog_bullets(root, task, "Execution Log", [f"`{iso_now()}`: worker-start owner=`{args.worker_owner or 'unknown'}`"])
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
    update_current_task_if_active(root, task, "worker 姝ｅ湪鎺ㄨ繘锛岀瓑寰呰繘涓€姝ュ洖鎶ャ€?")
    bullets = [f"`{iso_now()}`: {note}" for note in args.note]
    if bullets:
        append_runlog_bullets(root, task, "Execution Log", bullets)
    if args.tests:
        append_runlog_bullets(root, task, "Test Log", [f"`{test}`" for test in args.tests])
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
    update_current_task_if_active(root, task, "浠诲姟宸?blocked锛涚瓑寰呬汉宸ュ崗璋冩垨鏄惧紡瑙ｉ樆銆?")
    append_runlog_bullets(root, task, "Risk and Blockers", [f"`{iso_now()}`: {args.reason}"])
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
    if task["task_kind"] == "execution":
        task["review_bundle_status"] = "not_applicable"
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "worker 宸插畬鎴愬€欓€変氦浠橈紱绛夊緟鑷姩鏀跺彛鎴栬瘎瀹°€?")
    append_runlog_bullets(root, task, "Execution Log", [f"`{iso_now()}`: worker-finish `{args.summary}`"])
    if args.tests:
        append_runlog_bullets(root, task, "Test Log", [f"`{test}`" for test in args.tests])
    if args.candidate_paths:
        append_runlog_bullets(root, task, "Candidate Paths", [f"`{path}`" for path in args.candidate_paths])
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker finished {task['task_id']}")
    return 0


def _run_review_command(path: Path, command: str) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=path, text=True, capture_output=True, shell=True)
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part).strip()
    return result.returncode == 0, output


def _mark_review_bundle_failure(root: Path, task: dict, reason: str) -> None:
    task["status"] = "blocked"
    task["worker_state"] = "blocked"
    task["blocked_reason"] = reason
    task["review_bundle_status"] = "failed"
    task["last_reported_at"] = iso_now()
    append_runlog_bullets(root, task, "Review Bundle", [f"`{iso_now()}`: blocked `{reason}`"])


def _resolve_execution_worktree(worktrees: dict, task: dict) -> tuple[Path | None, str | None]:
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is None:
        return None, "review_bundle_failed: missing execution worktree entry"
    worktree_path = Path(entry["path"]).resolve()
    if not worktree_path.exists():
        return None, f"review_bundle_failed: missing worktree path {entry['path']}"
    return worktree_path, None


def _record_review_bundle_pass(root: Path, task: dict, command: str) -> None:
    append_runlog_bullets(root, task, "Test Log", [f"`{command}`"])
    append_runlog_bullets(root, task, "Review Bundle", [f"`{iso_now()}`: passed `{command}`"])


def _review_bundle_failure_reason(command: str, output: str) -> str:
    reason = f"review_bundle_failed: `{command}`"
    return f"{reason} :: {output}" if output else reason


def _run_review_bundle(root: Path, task: dict, worktree_path: Path) -> str | None:
    for command in task.get("required_tests", []):
        ok, output = _run_review_command(worktree_path, command)
        if ok:
            _record_review_bundle_pass(root, task, command)
            continue
        return _review_bundle_failure_reason(command, output)
    missing = missing_required_tests(root, task)
    if missing:
        return f"review_bundle_failed: missing tests {', '.join(missing)}"
    return None


def _mark_child_done(task: dict, worktrees: dict) -> None:
    task["status"] = "done"
    task["worker_state"] = "completed"
    task["blocked_reason"] = None
    task["review_bundle_status"] = "passed"
    task["closed_at"] = iso_now()
    task["last_reported_at"] = iso_now()
    entry = worktree_map(worktrees)[task["task_id"]]
    entry["status"] = "closed"
    entry["cleanup_state"] = "pending"


def _mark_review_bundle_pending(root: Path, task: dict) -> None:
    task["review_bundle_status"] = "pending"
    task["last_reported_at"] = iso_now()
    append_runlog_bullets(root, task, "Review Bundle", [f"`{iso_now()}`: pending"])


def _close_ready_child(root: Path, worktrees: dict, task: dict) -> str | None:
    worktree_path, error = _resolve_execution_worktree(worktrees, task)
    if error:
        return error
    _mark_review_bundle_pending(root, task)
    failure = _run_review_bundle(root, task, worktree_path)
    if failure:
        return failure
    _mark_child_done(task, worktrees)
    append_runlog_bullets(root, task, "Closeout Conclusion", [f"`{iso_now()}`: auto-close-children passed"])
    return None


def _promote_parent_after_children(
    root: Path,
    registry: dict,
    parent_task_id: str,
) -> tuple[str | None, list[str], list[str]]:
    parent = find_task(registry["tasks"], parent_task_id)
    children = [
        task
        for task in registry.get("tasks", [])
        if task.get("parent_task_id") == parent_task_id and task["task_kind"] == "execution"
    ]
    if not children:
        return None, [], []
    blocked = [task["task_id"] for task in children if task["status"] == "blocked"]
    open_children = [task["task_id"] for task in children if task["status"] not in {"done", "blocked"}]
    if all(task["status"] == "done" for task in children):
        parent["status"] = "review"
        parent["worker_state"] = "review_pending"
        parent["blocked_reason"] = None
        parent["last_reported_at"] = iso_now()
        append_runlog_bullets(root, parent, "Closeout Conclusion", [f"`{iso_now()}`: all child review bundles passed"])
        update_current_task_if_active(root, parent, "All child review bundles passed; coordination task is review-ready.")
        return "review", [], []
    if blocked:
        parent["status"] = "blocked"
        parent["worker_state"] = "blocked"
        parent["blocked_reason"] = f"child_review_bundle_failed: {', '.join(blocked)}"
        parent["last_reported_at"] = iso_now()
        append_runlog_bullets(root, parent, "Risk and Blockers", [f"`{iso_now()}`: child review bundle blocked `{', '.join(blocked)}`"])
        update_current_task_if_active(root, parent, "Child review bundle failed; coordination task is blocked pending repair.")
        return "blocked", blocked, open_children
    if open_children:
        parent["status"] = "doing"
        parent["worker_state"] = "running"
        parent["blocked_reason"] = None
        parent["last_reported_at"] = iso_now()
        append_runlog_bullets(root, parent, "Execution Log", [f"`{iso_now()}`: waiting on child review bundles `{', '.join(open_children)}`"])
        update_current_task_if_active(root, parent, "Child review bundles are still running; coordination task remains active.")
        return "doing", [], open_children
    return None, [], []


def cmd_auto_close_children(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    closed: list[str] = []
    blocked: list[str] = []
    open_children: list[str] = []
    for task in registry.get("tasks", []):
        if task.get("parent_task_id") != args.parent_task_id or task["task_kind"] != "execution":
            continue
        if task["worker_state"] not in {"review_pending", "completed"} or task["status"] not in {"review", "doing"}:
            continue
        failure = _close_ready_child(root, worktrees, task)
        if failure:
            _mark_review_bundle_failure(root, task, failure)
            blocked.append(f"{task['task_id']}: {failure.split(' :: ', 1)[0]}")
            continue
        closed.append(task["task_id"])
    parent_state, parent_blocked, open_children = _promote_parent_after_children(root, registry, args.parent_task_id)
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    touched_ids = [*closed]
    if parent_state is not None:
        touched_ids.append(args.parent_task_id)
    if blocked or parent_blocked:
        touched_ids.extend(item.split(":", 1)[0] for item in blocked)
    if touched_ids:
        sync_task_artifacts(root, registry, touched_ids)
    print(f"[OK] auto-closed children: {', '.join(closed)}" if closed else "[OK] no child tasks closed")
    if parent_state == "review":
        print(f"[OK] parent review-ready: {args.parent_task_id}")
    if parent_state == "doing":
        print(f"[OK] parent still doing: {args.parent_task_id} waiting on {', '.join(open_children)}")
    for item in blocked:
        print(f"[BLOCKED] {item}")
    if parent_state == "blocked":
        print(f"[BLOCKED] parent {args.parent_task_id}: child review bundle failure")
    return 0 if not blocked and parent_state != "blocked" else 1
