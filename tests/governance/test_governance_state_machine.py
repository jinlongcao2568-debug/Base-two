from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from governance_state_machine import (
    build_current_task_payload,
    build_idle_current_task_payload,
    is_idle_current_payload,
    mark_task_active,
    mark_task_done,
    mark_task_review_ready,
    pause_other_doing_tasks,
    validate_idle_current_payload,
)


def _task(task_id: str, *, status: str = "queued", worker_state: str = "idle") -> dict[str, object]:
    return {
        "task_id": task_id,
        "title": f"title-{task_id}",
        "status": status,
        "task_kind": "coordination",
        "execution_mode": "shared_coordination",
        "parent_task_id": None,
        "stage": "test-phase",
        "branch": f"feat/{task_id}",
        "size_class": "standard",
        "automation_mode": "manual",
        "worker_state": worker_state,
        "blocked_reason": None,
        "last_reported_at": "2026-04-05T00:00:00+08:00",
        "topology": "single_worker",
        "allowed_dirs": ["docs/governance/"],
        "reserved_paths": [],
        "planned_write_paths": ["docs/governance/"],
        "planned_test_paths": ["tests/governance/"],
        "required_tests": ["python scripts/check_repo.py"],
        "task_file": f"docs/governance/tasks/{task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
    }


def test_idle_payload_shape_is_formal_zero_state() -> None:
    payload = build_idle_current_task_payload("wait_for_successor_or_explicit_activation")

    assert is_idle_current_payload(payload) is True
    validate_idle_current_payload(payload)
    assert payload["current_task_id"] is None
    assert payload["status"] == "idle"
    assert payload["worker_state"] == "idle"
    assert payload["allowed_dirs"] == []


def test_state_machine_marks_review_and_done_consistently() -> None:
    task = _task("TASK-STATE-001")

    mark_task_active(task)
    assert task["status"] == "doing"
    assert task["worker_state"] == "running"

    mark_task_review_ready(task)
    assert task["status"] == "review"
    assert task["worker_state"] == "review_pending"

    mark_task_done(task)
    assert task["status"] == "done"
    assert task["worker_state"] == "completed"
    assert task["closed_at"] is not None


def test_pause_other_doing_tasks_returns_touched_ids() -> None:
    active = _task("TASK-STATE-001", status="doing", worker_state="running")
    sibling = _task("TASK-STATE-002", status="doing", worker_state="running")
    queued = _task("TASK-STATE-003")

    touched = pause_other_doing_tasks([active, sibling, queued], "TASK-STATE-001")

    assert touched == ["TASK-STATE-001", "TASK-STATE-002"]
    assert sibling["status"] == "paused"
    assert sibling["worker_state"] == "idle"
    assert queued["status"] == "queued"


def test_current_payload_tracks_live_task_fields() -> None:
    task = _task("TASK-STATE-004", status="doing", worker_state="running")

    payload = build_current_task_payload(task, "keep-working")

    assert payload["current_task_id"] == "TASK-STATE-004"
    assert payload["status"] == "doing"
    assert payload["branch"] == "feat/TASK-STATE-004"
    assert payload["next_action"] == "keep-working"
