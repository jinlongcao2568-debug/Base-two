from __future__ import annotations

from typing import Any

from governance_runtime import CURRENT_STATUS_VALUES, GovernanceError, iso_now


IDLE_CURRENT_NULL_FIELDS = (
    "current_task_id",
    "title",
    "task_kind",
    "execution_mode",
    "parent_task_id",
    "stage",
    "branch",
    "size_class",
    "automation_mode",
    "task_file",
    "runlog_file",
)
IDLE_CURRENT_EMPTY_LIST_FIELDS = (
    "allowed_dirs",
    "reserved_paths",
    "planned_write_paths",
    "planned_test_paths",
    "required_tests",
)


def build_current_task_payload(task: dict[str, Any], next_action: str) -> dict[str, Any]:
    return {
        "current_task_id": task["task_id"],
        "title": task["title"],
        "status": task["status"],
        "task_kind": task["task_kind"],
        "execution_mode": task["execution_mode"],
        "parent_task_id": task.get("parent_task_id"),
        "stage": task["stage"],
        "branch": task["branch"],
        "size_class": task["size_class"],
        "automation_mode": task["automation_mode"],
        "worker_state": task["worker_state"],
        "blocked_reason": task.get("blocked_reason"),
        "last_reported_at": task.get("last_reported_at"),
        "topology": task["topology"],
        "allowed_dirs": task.get("allowed_dirs", []),
        "reserved_paths": task.get("reserved_paths", []),
        "planned_write_paths": task.get("planned_write_paths", []),
        "planned_test_paths": task.get("planned_test_paths", []),
        "required_tests": task.get("required_tests", []),
        "task_file": task["task_file"],
        "runlog_file": task["runlog_file"],
        "next_action": next_action,
        "updated_at": iso_now(),
    }


def build_idle_current_task_payload(next_action: str) -> dict[str, Any]:
    now = iso_now()
    return {
        "current_task_id": None,
        "title": None,
        "status": "idle",
        "task_kind": None,
        "execution_mode": None,
        "parent_task_id": None,
        "stage": None,
        "branch": None,
        "size_class": None,
        "automation_mode": None,
        "worker_state": "idle",
        "blocked_reason": None,
        "last_reported_at": now,
        "topology": None,
        "allowed_dirs": [],
        "reserved_paths": [],
        "planned_write_paths": [],
        "planned_test_paths": [],
        "required_tests": [],
        "task_file": None,
        "runlog_file": None,
        "next_action": next_action,
        "updated_at": now,
    }


def is_idle_current_payload(current_task: dict[str, Any]) -> bool:
    return current_task.get("status") == "idle"


def validate_idle_current_payload(current_task: dict[str, Any]) -> None:
    if current_task.get("status") not in CURRENT_STATUS_VALUES:
        raise GovernanceError(f"invalid current task status: {current_task.get('status')}")
    if current_task.get("status") != "idle":
        raise GovernanceError("current task payload is not idle")
    for field in IDLE_CURRENT_NULL_FIELDS:
        if current_task.get(field) is not None:
            raise GovernanceError(f"idle current task field must be null: {field}")
    if current_task.get("worker_state") != "idle":
        raise GovernanceError("idle current task worker_state must be idle")
    if current_task.get("topology") is not None:
        raise GovernanceError("idle current task topology must be null")
    if current_task.get("blocked_reason") is not None:
        raise GovernanceError("idle current task blocked_reason must be null")
    for field in IDLE_CURRENT_EMPTY_LIST_FIELDS:
        if current_task.get(field) != []:
            raise GovernanceError(f"idle current task field must be empty: {field}")
    if not current_task.get("next_action"):
        raise GovernanceError("idle current task next_action must be present")


def mark_task_active(task: dict[str, Any]) -> None:
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    if task.get("activated_at") is None:
        task["activated_at"] = iso_now()


def mark_task_paused(task: dict[str, Any]) -> None:
    task["status"] = "paused"
    task["worker_state"] = "idle"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()


def mark_task_blocked(task: dict[str, Any], reason: str) -> None:
    task["status"] = "blocked"
    task["worker_state"] = "blocked"
    task["blocked_reason"] = reason
    task["last_reported_at"] = iso_now()


def mark_task_review_ready(task: dict[str, Any]) -> None:
    task["status"] = "review"
    task["worker_state"] = "review_pending"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()


def mark_task_done(task: dict[str, Any]) -> None:
    task["status"] = "done"
    task["worker_state"] = "completed"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    task["closed_at"] = iso_now()


def mark_task_reported(task: dict[str, Any]) -> None:
    if task["status"] == "queued":
        task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()


def close_worktree_entry(entry: dict[str, Any]) -> None:
    entry["status"] = "closed"
    if entry.get("work_mode") == "execution":
        entry["cleanup_state"] = "pending"


def pause_other_doing_tasks(tasks: list[dict[str, Any]], active_task_id: str) -> list[str]:
    touched_tasks = [active_task_id]
    for existing in tasks:
        if existing["status"] == "doing" and existing["task_id"] != active_task_id:
            mark_task_paused(existing)
            touched_tasks.append(existing["task_id"])
    return touched_tasks
