from __future__ import annotations

import argparse

from governance_lib import GovernanceError, append_runlog_bullets, dump_yaml, iso_now, load_task_registry
from control_plane_root import resolve_control_plane_root
from orchestration_runtime import record_session_event, runtime_status_for_task
from task_coordination_lease import (
    assess_coordination_lease,
    claim_coordination_lease,
    current_session_id,
    coordination_thread_id,
    release_coordination_lease,
    takeover_coordination_lease,
)
from task_handoff import write_handoff
from task_rendering import find_task, update_current_task_if_active


def _reported_next_tests(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "next_test", []) or [])
    return items or None


def _reported_candidate_write_paths(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "candidate_write_path", []) or [])
    return items or None


def _reported_candidate_test_paths(args: argparse.Namespace) -> list[str] | None:
    items = list(getattr(args, "candidate_test_path", []) or [])
    return items or None


def _touch_task_artifacts(root, registry: dict, task: dict) -> None:
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)


def cmd_handoff(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    if not assess_coordination_lease(root, task)["enforced"]:
        raise GovernanceError("handoff only supports top-level coordination tasks")
    lease = claim_coordination_lease(root, task, reason="handoff")
    session_id = current_session_id(root)

    append_runlog_bullets(
        root,
        task,
        "Execution Log",
        [f"`{iso_now()}`: handoff session=`{session_id}`"],
    )
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        completed_items=list(getattr(args, "completed_item", []) or []) or None,
        remaining_items=list(getattr(args, "remaining_item", []) or []) or None,
        next_step=getattr(args, "next_step", None),
        next_tests=_reported_next_tests(args),
        current_risks=list(getattr(args, "risk", []) or []) or None,
        candidate_write_paths=_reported_candidate_write_paths(args),
        candidate_test_paths=_reported_candidate_test_paths(args),
        resume_notes=[f"Handoff recorded by session `{session_id}`.", *(list(getattr(args, "resume_note", []) or []))],
        append_resume_notes=True,
    )
    update_current_task_if_active(root, task, "Formal handoff recorded; write lease remains with the current session.")
    _touch_task_artifacts(root, registry, task)
    record_session_event(
        root,
        session_id=session_id,
        thread_id=coordination_thread_id(root),
        current_command="handoff",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] handoff {task['task_id']} session={session_id} lease={lease['claim_result']}")
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    if not assess_coordination_lease(root, task)["enforced"]:
        raise GovernanceError("release only supports top-level coordination tasks")
    lease = release_coordination_lease(root, task, reason="release")
    session_id = current_session_id(root)

    append_runlog_bullets(
        root,
        task,
        "Execution Log",
        [f"`{iso_now()}`: release session=`{session_id}`"],
    )
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        next_step="A new session may continue-current or takeover before further writes occur.",
        next_tests=_reported_next_tests(args) or list(task.get("required_tests") or []),
        resume_notes=[f"Write lease released by session `{session_id}`."],
        append_resume_notes=True,
    )
    update_current_task_if_active(root, task, "Write lease released; another session may take over the coordination task.")
    _touch_task_artifacts(root, registry, task)
    record_session_event(
        root,
        session_id=session_id,
        thread_id=coordination_thread_id(root),
        current_command="release",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] release {task['task_id']} session={session_id} result={lease.get('release_result', 'released')}")
    return 0


def cmd_takeover(args: argparse.Namespace) -> int:
    root = resolve_control_plane_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    if not assess_coordination_lease(root, task)["enforced"]:
        raise GovernanceError("takeover only supports top-level coordination tasks")
    before = assess_coordination_lease(root, task)
    lease = takeover_coordination_lease(root, task, reason="takeover")
    session_id = current_session_id(root)
    previous_owner = before.get("owner_session_id")

    append_runlog_bullets(
        root,
        task,
        "Execution Log",
        [
            f"`{iso_now()}`: takeover session=`{session_id}` previous_owner=`{previous_owner or 'none'}`",
        ],
    )
    write_handoff(
        root,
        task,
        summary_status=task["status"],
        next_step=getattr(args, "next_step", None) or "Resume the coordination task under the new owner session.",
        next_tests=_reported_next_tests(args) or list(task.get("required_tests") or []),
        current_risks=list(getattr(args, "risk", []) or []) or None,
        candidate_write_paths=_reported_candidate_write_paths(args),
        candidate_test_paths=_reported_candidate_test_paths(args),
        resume_notes=[
            f"Takeover completed by session `{session_id}` from `{previous_owner or 'no previous owner'}`.",
            *(list(getattr(args, "resume_note", []) or [])),
        ],
        append_resume_notes=True,
    )
    update_current_task_if_active(root, task, "Coordination write lease transferred to the new session owner.")
    _touch_task_artifacts(root, registry, task)
    record_session_event(
        root,
        session_id=session_id,
        thread_id=coordination_thread_id(root),
        current_command="takeover",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"],
        continue_intent=None,
        runtime_status=runtime_status_for_task(task),
        safe_write=True,
    )
    print(
        f"[OK] takeover {task['task_id']} session={session_id} previous_owner={previous_owner or 'none'} "
        f"result={lease.get('takeover_result', 'took_over_existing_lease')}"
    )
    return 0
