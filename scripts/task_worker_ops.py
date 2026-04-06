from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from governance_lib import (
    EXECUTOR_STATUS_VALUES,
    GovernanceError,
    append_runlog_bullets,
    dump_yaml,
    find_repo_root,
    iso_now,
    load_task_registry,
    load_worktree_registry,
    missing_required_tests,
    sync_task_artifacts,
    worktree_map,
)
from orchestration_runtime import (
    load_execution_runtime_entry,
    record_session_event,
    record_worker_heartbeat,
    runtime_status_for_task,
    update_execution_runtime_entry,
)
from task_coordination_lease import claim_coordination_lease, coordination_thread_id, current_session_id
from task_handoff import write_handoff
from task_rendering import (
    enforce_execution_split_guards,
    find_task,
    record_blocked_split,
    update_current_task_if_active,
)

LOCAL_WORKER_ID = "worker-local-01"


def _execution_entry(worktrees: dict, task_id: str) -> dict | None:
    entry = worktree_map(worktrees).get(task_id)
    if entry is None or entry.get("work_mode") != "execution":
        return None
    return entry


def _mark_execution_runtime(
    root: Path,
    task_id: str,
    *,
    now: str,
    current_entry: dict | None = None,
    lane_session_id: str | None = None,
    executor_status: str | None = None,
    last_result: str | None = None,
) -> dict[str, object]:
    entry = load_execution_runtime_entry(root, task_id)
    if current_entry is not None:
        entry["status"] = current_entry.get("status", entry.get("status"))
    if lane_session_id is not None:
        entry["lane_session_id"] = lane_session_id
    if entry.get("started_at") is None and executor_status in {"launching", "running", "completed", "blocked"}:
        entry["started_at"] = now
    if executor_status is not None:
        entry["executor_status"] = executor_status
    if executor_status in {"running", "completed", "blocked"}:
        entry["last_heartbeat_at"] = now
    if last_result is not None:
        entry["last_result"] = last_result
    if current_entry is not None:
        current_entry["lane_session_id"] = entry["lane_session_id"]
        current_entry["executor_status"] = entry["executor_status"]
        current_entry["started_at"] = entry["started_at"]
        current_entry["last_heartbeat_at"] = entry["last_heartbeat_at"]
        current_entry["last_result"] = entry["last_result"]
    update_execution_runtime_entry(root, task_id, **entry)
    return entry


def _reported_completed_items(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "completed_item", []) or [])
    return items or None


def _reported_remaining_items(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "remaining_item", []) or [])
    return items or None


def _reported_next_tests(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "next_test", []) or [])
    return items or None


def _reported_tests(args: argparse.Namespace) -> list[str]:
    raw_tests = getattr(args, "tests", []) or []
    flattened: list[str] = []
    for entry in raw_tests:
        if isinstance(entry, list):
            flattened.extend(str(item) for item in entry)
        else:
            flattened.append(str(entry))
    return flattened


def _reported_risks(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "risk", []) or [])
    return items or None


def _reported_candidate_write_paths(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "candidate_write_path", []) or [])
    if items:
        return items
    legacy = list(getattr(args, "candidate_paths", []) or [])
    return legacy or None


def _reported_candidate_test_paths(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "candidate_test_path", []) or [])
    return items or None


def _reported_resume_notes(args: argparse.Namespace, fallback_note: str | None = None) -> list[str] | None:
    items = list(getattr(args, "resume_note", []) or [])
    if fallback_note:
        items.append(fallback_note)
    return items or None


def cmd_worker_start(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    claim_coordination_lease(root, task, reason="worker-start")
    try:
        enforce_execution_split_guards(registry, task)
    except GovernanceError:
        record_blocked_split(root, registry, task)
        raise
    now = iso_now()
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = now
    if task["task_kind"] == "execution":
        task["review_bundle_status"] = "not_applicable"
    if task["activated_at"] is None:
        task["activated_at"] = now
    entry = _execution_entry(worktrees, task["task_id"])
    if entry is not None:
        entry["status"] = "active"
        if args.worker_owner:
            entry["worker_owner"] = args.worker_owner
        if args.path:
            entry["path"] = args.path
        _mark_execution_runtime(
            root,
            task["task_id"],
            now=now,
            current_entry=entry,
            lane_session_id=entry.get("lane_session_id") or current_session_id(root),
            executor_status="running",
            last_result="worker-start",
        )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    update_current_task_if_active(root, task, "Worker started and the task is actively running.")
    append_runlog_bullets(root, task, "Execution Log", [f"`{now}`: worker-start owner=`{args.worker_owner or 'unknown'}`"])
    sync_task_artifacts(root, registry, [task["task_id"]])
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="worker-start",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] worker started {task['task_id']}")
    return 0


def cmd_worker_report(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    claim_coordination_lease(root, task, reason="worker-report")
    now = iso_now()
    task["worker_state"] = "running"
    if task["status"] == "queued":
        task["status"] = "doing"
    task["blocked_reason"] = None
    task["last_reported_at"] = now
    entry = _execution_entry(worktrees, task["task_id"])
    _mark_execution_runtime(
        root,
        task["task_id"],
        now=now,
        current_entry=entry,
        lane_session_id=entry.get("lane_session_id") if entry is not None else None,
        executor_status="running" if entry is not None else None,
        last_result="worker-report",
    )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    update_current_task_if_active(root, task, "Worker progress was recorded for the live task.")
    bullets = [f"`{now}`: {note}" for note in args.note]
    if bullets:
        append_runlog_bullets(root, task, "Execution Log", bullets)
    reported_tests = _reported_tests(args)
    if reported_tests:
        append_runlog_bullets(root, task, "Test Log", [f"`{test}`" for test in reported_tests])
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        completed_items=_reported_completed_items(args),
        remaining_items=_reported_remaining_items(args),
        next_step=getattr(args, "next_step", None),
        next_tests=_reported_next_tests(args),
        current_risks=_reported_risks(args),
        candidate_write_paths=_reported_candidate_write_paths(args),
        candidate_test_paths=_reported_candidate_test_paths(args),
        resume_notes=_reported_resume_notes(args, "Worker progress was reported."),
        append_resume_notes=True,
    )
    sync_task_artifacts(root, registry, [task["task_id"]])
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="worker-report",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] worker reported {task['task_id']}")
    return 0


def cmd_worker_blocked(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    claim_coordination_lease(root, task, reason="worker-blocked")
    now = iso_now()
    task["status"] = "blocked"
    task["worker_state"] = "blocked"
    task["blocked_reason"] = args.reason
    task["last_reported_at"] = now
    entry = _execution_entry(worktrees, task["task_id"])
    _mark_execution_runtime(
        root,
        task["task_id"],
        now=now,
        current_entry=entry,
        lane_session_id=entry.get("lane_session_id") if entry is not None else None,
        executor_status="blocked" if entry is not None else None,
        last_result=args.reason,
    )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    update_current_task_if_active(root, task, "Task blocked; waiting for blocker resolution before more changes.")
    append_runlog_bullets(root, task, "Risk and Blockers", [f"`{now}`: {args.reason}"])
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        remaining_items=_reported_remaining_items(args) or ["Resolve the active blocker and resume the scoped work."],
        next_step=getattr(args, "next_step", None) or "Resolve the blocker before continuing the task.",
        next_tests=_reported_next_tests(args) or list(task.get("required_tests") or []),
        current_risks=_reported_risks(args) or [args.reason],
        candidate_write_paths=_reported_candidate_write_paths(args),
        candidate_test_paths=_reported_candidate_test_paths(args),
        resume_notes=_reported_resume_notes(args, f"Task blocked: {args.reason}"),
        append_resume_notes=True,
    )
    sync_task_artifacts(root, registry, [task["task_id"]])
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="worker-blocked",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status="blocked",
        blocked_reason=args.reason,
        safe_write=True,
    )
    print(f"[OK] worker blocked {task['task_id']}")
    return 0


def cmd_worker_finish(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    claim_coordination_lease(root, task, reason="worker-finish")
    now = iso_now()
    task["status"] = "review"
    task["worker_state"] = "review_pending"
    task["blocked_reason"] = None
    task["last_reported_at"] = now
    if task["task_kind"] == "execution":
        task["review_bundle_status"] = "not_applicable"
    entry = _execution_entry(worktrees, task["task_id"])
    _mark_execution_runtime(
        root,
        task["task_id"],
        now=now,
        current_entry=entry,
        lane_session_id=entry.get("lane_session_id") if entry is not None else None,
        executor_status="completed" if entry is not None else None,
        last_result=args.summary,
    )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    update_current_task_if_active(root, task, "Worker finished implementation; the task is now review-ready.")
    append_runlog_bullets(root, task, "Execution Log", [f"`{now}`: worker-finish `{args.summary}`"])
    reported_tests = _reported_tests(args)
    if reported_tests:
        append_runlog_bullets(root, task, "Test Log", [f"`{test}`" for test in reported_tests])
    if args.candidate_paths:
        append_runlog_bullets(root, task, "Candidate Paths", [f"`{path}`" for path in args.candidate_paths])
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        completed_items=_reported_completed_items(args) or [args.summary],
        remaining_items=_reported_remaining_items(args)
        or ["Validate the review-ready evidence and close the task if eligible."],
        next_step=getattr(args, "next_step", None)
        or "Review the required tests and use continue-current or close to finish the task.",
        next_tests=_reported_next_tests(args) or list(task.get("required_tests") or []),
        current_risks=_reported_risks(args) or [],
        candidate_write_paths=_reported_candidate_write_paths(args),
        candidate_test_paths=_reported_candidate_test_paths(args),
        resume_notes=_reported_resume_notes(args, f"Worker finish summary: {args.summary}"),
        append_resume_notes=True,
    )
    sync_task_artifacts(root, registry, [task["task_id"]])
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="worker-finish",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] worker finished {task['task_id']}")
    return 0


def cmd_worker_heartbeat(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    claim_coordination_lease(root, task, reason="worker-heartbeat")
    now = iso_now()
    entry = _execution_entry(worktrees, task["task_id"])
    if entry is None:
        raise GovernanceError(f"worker-heartbeat requires an execution worktree: {task['task_id']}")
    current_runtime = load_execution_runtime_entry(root, task["task_id"])
    executor_status = args.executor_status or current_runtime.get("executor_status") or "running"
    if executor_status not in EXECUTOR_STATUS_VALUES:
        raise GovernanceError(f"invalid executor_status: {executor_status}")
    entry = _mark_execution_runtime(
        root,
        task["task_id"],
        now=now,
        current_entry=entry,
        lane_session_id=args.lane_session_id or current_runtime.get("lane_session_id") or current_session_id(root),
        executor_status=executor_status,
        last_result=args.result or current_runtime.get("last_result"),
    )
    if task["status"] not in {"done", "blocked"}:
        task["last_reported_at"] = now
    record_worker_heartbeat(root, args.worker_id, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    print(f"[OK] worker heartbeat {task['task_id']} executor_status={entry['executor_status']}")
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
        write_handoff(
            root,
            parent,
            summary_status=parent["status"],
            remaining_items=["Close the parent task after validating the aggregated review evidence."],
            next_step="Review the parent task and close it when the required tests are satisfied.",
            next_tests=list(parent.get("required_tests") or []),
            current_risks=[],
            resume_notes=["All child review bundles passed; the parent task is review-ready."],
            append_resume_notes=True,
        )
        return "review", [], []
    if open_children:
        parent["status"] = "doing"
        parent["worker_state"] = "running"
        parent["blocked_reason"] = None
        parent["last_reported_at"] = iso_now()
        append_runlog_bullets(root, parent, "Execution Log", [f"`{iso_now()}`: waiting on child review bundles `{', '.join(open_children)}`"])
        update_current_task_if_active(root, parent, "Child review bundles are still running; coordination task remains active.")
        write_handoff(
            root,
            parent,
            summary_status=parent["status"],
            remaining_items=[f"Wait for child review bundles: {', '.join(open_children)}"],
            next_step="Wait for the remaining child review bundles to finish and rerun auto-close-children.",
            next_tests=list(parent.get("required_tests") or []),
            current_risks=[f"blocked child lanes: {', '.join(blocked)}"] if blocked else [],
            resume_notes=["Parent task is still waiting on child review bundles."],
            append_resume_notes=True,
        )
        return "doing", [], open_children
    if blocked:
        parent["status"] = "blocked"
        parent["worker_state"] = "blocked"
        parent["blocked_reason"] = f"child_review_bundle_failed: {', '.join(blocked)}"
        parent["last_reported_at"] = iso_now()
        append_runlog_bullets(root, parent, "Risk and Blockers", [f"`{iso_now()}`: child review bundle blocked `{', '.join(blocked)}`"])
        update_current_task_if_active(root, parent, "Child review bundle failed; coordination task is blocked pending repair.")
        write_handoff(
            root,
            parent,
            summary_status=parent["status"],
            remaining_items=["Repair the blocked child review bundle before resuming the parent task."],
            next_step="Repair the blocked child lane and rerun auto-close-children.",
            next_tests=list(parent.get("required_tests") or []),
            current_risks=[f"child review bundle blocked: {', '.join(blocked)}"],
            resume_notes=["Parent task blocked by a child review bundle failure."],
            append_resume_notes=True,
        )
        return "blocked", blocked, open_children
    return None, [], []


def cmd_auto_close_children(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    parent = find_task(registry["tasks"], args.parent_task_id)
    claim_coordination_lease(root, parent, reason="auto-close-children")
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
