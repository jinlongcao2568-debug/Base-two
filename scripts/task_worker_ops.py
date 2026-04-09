from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from governance_lib import (
    EXECUTOR_STATUS_VALUES,
    GovernanceError,
    append_runlog_bullets,
    dump_yaml,
    # find_repo_root removed; control-plane writes must resolve the main root.
    git,
    iso_now,
    load_task_registry,
    load_task_policy,
    load_worktree_registry,
    missing_required_tests,
    safe_rmtree,
    sync_task_artifacts,
    worktree_map,
)
from child_execution_flow import (
    cleanup_transient_child_artifacts,
    load_execution_context,
    merge_child_into_parent,
    mirror_governance_ledgers_to_worktree,
    persist_child_workflow,
    run_shell_command,
    set_design_confirmation,
    set_execution_plan,
    set_review_gate,
    set_test_first,
    validate_finish_ready,
    validate_worker_start,
)
from governance_rules import is_governed_child_task
from orchestration_runtime import (
    load_execution_runtime_entry,
    record_session_event,
    record_worker_heartbeat,
    runtime_status_for_task,
    update_execution_runtime_entry,
)
from task_coordination_lease import claim_coordination_lease, coordination_thread_id, current_session_id
from control_plane_root import CONTROL_PLANE_EXECUTOR_ID, resolve_control_plane_root, sync_execution_lease
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


def _task_executor_identity(
    task: dict,
    entry: dict | None,
    *,
    explicit_owner: str | None = None,
) -> tuple[str, str]:
    if task.get("task_kind") == "coordination":
        return CONTROL_PLANE_EXECUTOR_ID, "control_plane"
    owner = str(explicit_owner or (entry or {}).get("worker_owner") or "").strip() or LOCAL_WORKER_ID
    if entry is not None and entry.get("pool_kind") == "full_clone":
        return owner, "full_clone"
    return owner, "execution_worker"


def _sync_full_clone_mirror(root: Path, registry: dict, worktrees: dict, task: dict) -> None:
    entry = _execution_entry(worktrees, task["task_id"])
    if entry is None or entry.get("pool_kind") != "full_clone":
        return
    worktree_path = Path(str(entry.get("path") or "")).resolve()
    if not worktree_path.exists():
        return
    mirror_governance_ledgers_to_worktree(root, worktree_path, registry, worktrees, task)


def _requires_governed_child_workflow(root: Path, task: dict) -> bool:
    return is_governed_child_task(task, load_task_policy(root))


def _load_child_bundle(root: Path, registry: dict, worktrees: dict, task_id: str) -> tuple[dict, dict, dict, Path]:
    task = find_task(registry["tasks"], task_id)
    entry = _execution_entry(worktrees, task_id)
    if entry is None:
        raise GovernanceError(f"missing execution worktree entry for {task_id}")
    worktree_path = Path(entry["path"]).resolve()
    if not worktree_path.exists():
        raise GovernanceError(f"missing execution worktree path for {task_id}: {entry['path']}")
    context = load_execution_context(worktree_path)
    return task, entry, context, worktree_path


def _block_governed_child(
    root: Path,
    registry: dict,
    worktrees: dict,
    task: dict,
    entry: dict,
    context: dict,
    reason: str,
) -> None:
    now = iso_now()
    task["status"] = "blocked"
    task["worker_state"] = "blocked"
    task["blocked_reason"] = reason
    task["last_reported_at"] = now
    persist_child_workflow(
        root,
        registry,
        worktrees,
        task,
        entry,
        context,
        runlog_section="Risk and Blockers",
        bullets=[f"`{now}`: {reason}"],
    )


def _mark_task_review_ready(task: dict, now: str) -> None:
    task["status"] = "review"
    task["worker_state"] = "review_pending"
    task["blocked_reason"] = None
    task["last_reported_at"] = now
    if task["task_kind"] == "execution":
        task["review_bundle_status"] = "pending"


def _record_finish_artifacts(root: Path, task: dict, args: argparse.Namespace, now: str) -> None:
    roadmap_closeout_note = (
        "Run closeout from the main control plane so the roadmap claim, full-clone slot, and candidate cache are released together."
        if task.get("roadmap_candidate_id")
        else None
    )
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
        or roadmap_closeout_note
        or "Review the required tests and use continue-current or close to finish the task.",
        next_tests=_reported_next_tests(args) or list(task.get("required_tests") or []),
        current_risks=_reported_risks(args) or [],
        candidate_write_paths=_reported_candidate_write_paths(args),
        candidate_test_paths=_reported_candidate_test_paths(args),
        resume_notes=_reported_resume_notes(
            args,
            roadmap_closeout_note if roadmap_closeout_note else f"Worker finish summary: {args.summary}",
        ),
        append_resume_notes=True,
    )


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
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    claim_coordination_lease(root, task, reason="worker-start")
    try:
        enforce_execution_split_guards(registry, task)
    except GovernanceError:
        record_blocked_split(root, registry, task)
        raise
    if _requires_governed_child_workflow(root, task):
        _, entry, context, _ = _load_child_bundle(root, registry, worktrees, task["task_id"])
        start_error = validate_worker_start(context)
        if start_error:
            _block_governed_child(root, registry, worktrees, task, entry, context, start_error)
            raise GovernanceError(start_error)
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
    executor_id, executor_type = _task_executor_identity(task, entry, explicit_owner=args.worker_owner)
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
    sync_execution_lease(
        root,
        task=task,
        executor_id=executor_id,
        executor_type=executor_type,
        status="running",
        owner_session_id=current_session_id(root),
        heartbeat_at=now,
    )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    _sync_full_clone_mirror(root, registry, worktrees, task)
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
    root = resolve_control_plane_root()
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
    executor_id, executor_type = _task_executor_identity(task, entry)
    _mark_execution_runtime(
        root,
        task["task_id"],
        now=now,
        current_entry=entry,
        lane_session_id=entry.get("lane_session_id") if entry is not None else None,
        executor_status="running" if entry is not None else None,
        last_result="worker-report",
    )
    sync_execution_lease(
        root,
        task=task,
        executor_id=executor_id,
        executor_type=executor_type,
        status="running",
        owner_session_id=current_session_id(root),
        heartbeat_at=now,
    )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    _sync_full_clone_mirror(root, registry, worktrees, task)
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
    root = resolve_control_plane_root()
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
    executor_id, executor_type = _task_executor_identity(task, entry)
    _mark_execution_runtime(
        root,
        task["task_id"],
        now=now,
        current_entry=entry,
        lane_session_id=entry.get("lane_session_id") if entry is not None else None,
        executor_status="blocked" if entry is not None else None,
        last_result=args.reason,
    )
    sync_execution_lease(
        root,
        task=task,
        executor_id=executor_id,
        executor_type=executor_type,
        status="blocked",
        owner_session_id=current_session_id(root),
        heartbeat_at=now,
    )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    _sync_full_clone_mirror(root, registry, worktrees, task)
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
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    from task_coordination_lease import ensure_closeout_write_lease

    lease = ensure_closeout_write_lease(root, task, reason="worker-finish", allow_takeover=True)
    entry = _execution_entry(worktrees, task["task_id"])
    context = None
    if _requires_governed_child_workflow(root, task):
        task, entry, context, _ = _load_child_bundle(root, registry, worktrees, task["task_id"])
        finish_error = validate_finish_ready(context)
        if finish_error:
            _block_governed_child(root, registry, worktrees, task, entry, context, finish_error)
            raise GovernanceError(finish_error)
    now = iso_now()
    if lease.get("auto_takeover"):
        append_runlog_bullets(
            root,
            task,
            "Execution Log",
            [
                f"`{now}`: automatic lease takeover previous_owner=`{lease.get('previous_owner_session_id')}` reason=`worker-finish`"
            ],
        )
    _mark_task_review_ready(task, now)
    if context is not None:
        context["workflow_state"]["finish"]["status"] = "ready"
        context["workflow_state"]["finish"]["recorded_at"] = now
        context["workflow_state"]["phase"] = "finish_ready"
    executor_id, executor_type = _task_executor_identity(task, entry)
    _mark_execution_runtime(
        root,
        task["task_id"],
        now=now,
        current_entry=entry,
        lane_session_id=entry.get("lane_session_id") if entry is not None else None,
        executor_status="completed" if entry is not None else None,
        last_result=args.summary,
    )
    sync_execution_lease(
        root,
        task=task,
        executor_id=executor_id,
        executor_type=executor_type,
        status="review_pending",
        owner_session_id=current_session_id(root),
        heartbeat_at=now,
    )
    record_worker_heartbeat(root, LOCAL_WORKER_ID, timestamp=now, observed_status="active")
    registry["updated_at"] = now
    worktrees["updated_at"] = now
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    _sync_full_clone_mirror(root, registry, worktrees, task)
    _record_finish_artifacts(root, task, args, now)
    if context is not None and entry is not None:
        persist_child_workflow(root, registry, worktrees, task, entry, context)
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


def cmd_worker_design_confirm(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task, entry, context, _ = _load_child_bundle(root, registry, worktrees, args.task_id)
    claim_coordination_lease(root, task, reason="worker-design-confirm")
    set_design_confirmation(context, summary=args.summary, implementation_kind=args.implementation_kind)
    task["last_reported_at"] = iso_now()
    persist_child_workflow(
        root,
        registry,
        worktrees,
        task,
        entry,
        context,
        runlog_section="Execution Log",
        bullets=[f"`{iso_now()}`: design confirmation passed kind=`{args.implementation_kind}` summary=`{args.summary}`"],
    )
    print(f"[OK] design confirmation recorded for {task['task_id']}")
    return 0


def cmd_worker_plan(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task, entry, context, worktree_path = _load_child_bundle(root, registry, worktrees, args.task_id)
    claim_coordination_lease(root, task, reason="worker-plan")
    set_execution_plan(
        worktree_path,
        context,
        summary=args.summary,
        files=list(args.file or []),
        steps=list(args.step or []),
        tests=list(args.test or []),
        verifications=list(args.verify or []),
    )
    task["last_reported_at"] = iso_now()
    persist_child_workflow(
        root,
        registry,
        worktrees,
        task,
        entry,
        context,
        runlog_section="Execution Log",
        bullets=[f"`{iso_now()}`: detailed execution plan recorded summary=`{args.summary}`"],
    )
    print(f"[OK] execution plan recorded for {task['task_id']}")
    return 0


def cmd_worker_test_first(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task, entry, context, _ = _load_child_bundle(root, registry, worktrees, args.task_id)
    claim_coordination_lease(root, task, reason="worker-test-first")
    set_test_first(context, commands=list(args.command or []), note=args.note)
    task["last_reported_at"] = iso_now()
    persist_child_workflow(
        root,
        registry,
        worktrees,
        task,
        entry,
        context,
        runlog_section="Execution Log",
        bullets=[f"`{iso_now()}`: test-first gate recorded commands=`{', '.join(args.command or [])}`"],
    )
    print(f"[OK] test-first gate recorded for {task['task_id']}")
    return 0


def cmd_worker_spec_review(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task, entry, context, _ = _load_child_bundle(root, registry, worktrees, args.task_id)
    claim_coordination_lease(root, task, reason="worker-spec-review")
    set_review_gate(context, "spec_review", status=args.status, summary=args.summary)
    task["last_reported_at"] = iso_now()
    if args.status == "failed":
        task["status"] = "blocked"
        task["worker_state"] = "blocked"
        task["blocked_reason"] = f"spec_review_failed: {args.summary}"
    persist_child_workflow(
        root,
        registry,
        worktrees,
        task,
        entry,
        context,
        runlog_section="Review Bundle",
        bullets=[f"`{iso_now()}`: spec_review `{args.status}` `{args.summary}`"],
    )
    print(f"[OK] spec review {args.status} for {task['task_id']}")
    return 0


def cmd_worker_quality_review(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task, entry, context, _ = _load_child_bundle(root, registry, worktrees, args.task_id)
    claim_coordination_lease(root, task, reason="worker-quality-review")
    set_review_gate(context, "quality_review", status=args.status, summary=args.summary)
    task["last_reported_at"] = iso_now()
    if args.status == "failed":
        task["status"] = "blocked"
        task["worker_state"] = "blocked"
        task["blocked_reason"] = f"quality_review_failed: {args.summary}"
    persist_child_workflow(
        root,
        registry,
        worktrees,
        task,
        entry,
        context,
        runlog_section="Review Bundle",
        bullets=[f"`{iso_now()}`: quality_review `{args.status}` `{args.summary}`"],
    )
    print(f"[OK] quality review {args.status} for {task['task_id']}")
    return 0


def cmd_worker_heartbeat(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
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
    try:
        return run_shell_command(command, path)
    except GovernanceError as error:
        return False, str(error)


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


def _reconcile_missing_governed_child(root: Path, worktrees: dict, task: dict) -> str | None:
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is None:
        return "review_bundle_failed: missing execution worktree entry"
    workflow = entry.get("workflow_state") or {}
    finish = workflow.get("finish") or {}
    review = workflow.get("review") or {}
    if finish.get("status") not in {"ready", "completed"}:
        return f"review_bundle_failed: missing worktree path {entry['path']}"
    if ((review.get("spec_review") or {}).get("status")) != "passed":
        return "review_bundle_failed: spec review not passed"
    if ((review.get("quality_review") or {}).get("status")) != "passed":
        return "review_bundle_failed: quality review not passed"
    missing = missing_required_tests(root, task)
    if missing:
        return f"review_bundle_failed: missing tests {', '.join(missing)}"
    parent_branch = workflow.get("parent_branch") or git(root, "branch", "--show-current").stdout.strip()
    merged = git(root, "merge-base", "--is-ancestor", task["branch"], parent_branch, check=False).returncode == 0
    if not merged:
        return f"review_bundle_failed: missing worktree path {entry['path']}"
    entry["cleanup_state"] = "done"
    entry["status"] = "closed"
    entry["last_cleanup_error"] = None
    workflow["phase"] = "child_finished"
    finish["status"] = "completed"
    finish["recorded_at"] = finish.get("recorded_at") or iso_now()
    finish["merged_into_parent_at"] = finish.get("merged_into_parent_at") or iso_now()
    entry["workflow_state"] = workflow
    _mark_child_done(task, entry)
    append_runlog_bullets(
        root,
        task,
        "Closeout Conclusion",
        [f"`{iso_now()}`: reconciled merged child without local worktree"],
    )
    return None


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


def _mark_child_done(task: dict, entry: dict | None = None) -> None:
    task["status"] = "done"
    task["worker_state"] = "completed"
    task["blocked_reason"] = None
    task["review_bundle_status"] = "passed"
    task["closed_at"] = iso_now()
    task["last_reported_at"] = iso_now()
    if entry is not None:
        entry["status"] = "closed"
        entry["cleanup_state"] = entry.get("cleanup_state", "pending")


def _mark_review_bundle_pending(root: Path, task: dict) -> None:
    task["review_bundle_status"] = "pending"
    task["last_reported_at"] = iso_now()
    append_runlog_bullets(root, task, "Review Bundle", [f"`{iso_now()}`: pending"])


def _merge_legacy_child_into_parent(root: Path, worktree_path: Path, task: dict) -> str | None:
    child_dirty = cleanup_transient_child_artifacts(worktree_path, task)
    if child_dirty:
        return "child_finish_failed: child worktree must be clean before finish merge"
    try:
        git(root, "merge", "--no-ff", "--no-edit", task["branch"])
        git(root, "worktree", "remove", str(worktree_path))
    except GovernanceError as error:
        return f"child_finish_failed: {error}"
    if worktree_path.exists():
        safe_rmtree(worktree_path)
    return None


def _close_legacy_child(root: Path, worktrees: dict, task: dict) -> str | None:
    worktree_path, error = _resolve_execution_worktree(worktrees, task)
    if worktree_path is None:
        missing = missing_required_tests(root, task)
        if missing:
            return error or f"review_bundle_failed: missing tests {', '.join(missing)}"
        _mark_child_done(task)
        append_runlog_bullets(root, task, "Closeout Conclusion", [f"`{iso_now()}`: legacy auto-close passed without execution worktree"])
        return None
    _mark_review_bundle_pending(root, task)
    failure = _run_review_bundle(root, task, worktree_path)
    if failure:
        return failure
    merge_error = _merge_legacy_child_into_parent(root, worktree_path, task)
    if merge_error:
        return merge_error
    entry = worktree_map(worktrees)[task["task_id"]]
    entry["cleanup_state"] = "done"
    entry["status"] = "closed"
    entry["last_cleanup_error"] = None
    entry["path"] = str(worktree_path).replace("\\", "/")
    _mark_child_done(task, entry)
    append_runlog_bullets(root, task, "Closeout Conclusion", [f"`{iso_now()}`: legacy auto-close-children passed"])
    return None


def _close_ready_child(root: Path, worktrees: dict, task: dict) -> str | None:
    if not _requires_governed_child_workflow(root, task):
        return _close_legacy_child(root, worktrees, task)
    worktree_path, error = _resolve_execution_worktree(worktrees, task)
    if error:
        if error.startswith("review_bundle_failed: missing worktree path"):
            return _reconcile_missing_governed_child(root, worktrees, task)
        return error
    context = load_execution_context(worktree_path)
    finish_error = validate_finish_ready(context)
    if finish_error:
        return finish_error
    _mark_review_bundle_pending(root, task)
    failure = _run_review_bundle(root, task, worktree_path)
    if failure:
        return failure
    try:
        merge_child_into_parent(root, worktree_path, task, context)
    except GovernanceError as error:
        return f"child_finish_failed: {error}"
    entry = worktree_map(worktrees)[task["task_id"]]
    entry["cleanup_state"] = "done"
    entry["status"] = "closed"
    entry["last_cleanup_error"] = None
    entry["path"] = str(worktree_path).replace("\\", "/")
    entry["workflow_state"] = context["workflow_state"]
    _mark_child_done(task, entry)
    append_runlog_bullets(root, task, "Closeout Conclusion", [f"`{iso_now()}`: auto-close-children passed"])
    return None


def _mark_parent_governed_children_done(root: Path, parent: dict) -> str:
    parent["status"] = "doing"
    parent["worker_state"] = "running"
    parent["blocked_reason"] = None
    parent["last_reported_at"] = iso_now()
    append_runlog_bullets(
        root,
        parent,
        "Execution Log",
        [f"`{iso_now()}`: all child lanes finished; parent is now an ai_guarded closeout candidate"],
    )
    update_current_task_if_active(
        root,
        parent,
        "All child lanes finished; the top-level task stays live until ai_guarded closeout is explicitly continued.",
    )
    write_handoff(
        root,
        parent,
        summary_status=parent["status"],
        remaining_items=["Validate the aggregate evidence and use ai_guarded continue-current or continue-roadmap when the parent is ready to close."],
        next_step="Use continue-current to close this parent back to idle, or continue-roadmap only when a unique successor is explicitly ready.",
        next_tests=list(parent.get("required_tests") or []),
        current_risks=[],
        resume_notes=["All child lanes finished; parent is an ai_guarded closeout candidate."],
        append_resume_notes=True,
    )
    return "doing"


def _mark_parent_legacy_review_ready(root: Path, parent: dict) -> str:
    parent["status"] = "review"
    parent["worker_state"] = "review_pending"
    parent["blocked_reason"] = None
    parent["last_reported_at"] = iso_now()
    parent["review_bundle_status"] = "not_applicable"
    append_runlog_bullets(root, parent, "Execution Log", [f"`{iso_now()}`: all child lanes finished; parent review bundle is ready"])
    update_current_task_if_active(root, parent, "All child lanes finished; parent task returned to review-ready state.")
    write_handoff(
        root,
        parent,
        summary_status=parent["status"],
        remaining_items=["Review the aggregate child evidence and close the parent task if eligible."],
        next_step="Review the aggregate child evidence and decide whether to close the parent task.",
        next_tests=list(parent.get("required_tests") or []),
        current_risks=[],
        resume_notes=["All child lanes finished; parent task is review-ready under legacy closeout semantics."],
        append_resume_notes=True,
    )
    return "review"


def _mark_parent_waiting_on_children(root: Path, parent: dict, open_children: list[str], blocked: list[str]) -> str:
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
    return "doing"


def _mark_parent_blocked_by_children(root: Path, parent: dict, blocked: list[str]) -> str:
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
    return "blocked"


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
    governed_parent = all(_requires_governed_child_workflow(root, task) for task in children)
    blocked = [task["task_id"] for task in children if task["status"] == "blocked"]
    open_children = [task["task_id"] for task in children if task["status"] not in {"done", "blocked"}]
    if all(task["status"] == "done" for task in children):
        parent_state = _mark_parent_governed_children_done(root, parent) if governed_parent else _mark_parent_legacy_review_ready(root, parent)
        return parent_state, [], []
    if open_children:
        return _mark_parent_waiting_on_children(root, parent, open_children, blocked), [], open_children
    if blocked:
        return _mark_parent_blocked_by_children(root, parent, blocked), blocked, open_children
    return None, [], []


def cmd_auto_close_children(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    parent = find_task(registry["tasks"], args.parent_task_id)
    from task_coordination_lease import ensure_closeout_write_lease

    lease = ensure_closeout_write_lease(root, parent, reason="auto-close-children", allow_takeover=True)
    if lease.get("auto_takeover"):
        append_runlog_bullets(
            root,
            parent,
            "Execution Log",
            [
                f"`{iso_now()}`: automatic lease takeover previous_owner=`{lease.get('previous_owner_session_id')}` reason=`auto-close-children`"
            ],
        )
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
        if open_children:
            print(f"[OK] parent still doing: {args.parent_task_id} waiting on {', '.join(open_children)}")
        else:
            print(f"[OK] parent still doing: {args.parent_task_id} ai_guarded closeout candidate after child finish")
    for item in blocked:
        print(f"[BLOCKED] {item}")
    if parent_state == "blocked":
        print(f"[BLOCKED] parent {args.parent_task_id}: child review bundle failure")
    return 0 if not blocked and parent_state != "blocked" else 1
