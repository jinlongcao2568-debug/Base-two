from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from governance_runtime import (
    AUTOMATION_MODE_VALUES,
    CLEANUP_STATE_VALUES,
    CURRENT_STATUS_VALUES,
    EXECUTION_MODE_VALUES,
    GovernanceError,
    RESERVED_PATHS,
    SIZE_CLASS_VALUES,
    STATUS_VALUES,
    TASK_KIND_VALUES,
    TOPOLOGY_VALUES,
    WORKER_OWNER_VALUES,
    WORKER_STATE_VALUES,
    WORKTREE_STATUS_VALUES,
    actual_path,
    declared_path,
    iso_now,
    load_test_matrix,
    read_text,
)


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


def rule_matches_path(rule, path: str) -> bool:
    normalized = actual_path(path)
    if rule.is_dir:
        return normalized == rule.normalized or normalized.startswith(f"{rule.normalized}/")
    return normalized == rule.normalized


def declared_paths_overlap(left, right) -> bool:
    if left.is_dir and right.is_dir:
        return (
            left.normalized == right.normalized
            or left.normalized.startswith(f"{right.normalized}/")
            or right.normalized.startswith(f"{left.normalized}/")
        )
    if left.is_dir:
        return rule_matches_path(left, right.normalized)
    if right.is_dir:
        return rule_matches_path(right, left.normalized)
    return left.normalized == right.normalized


def path_within_declared(path: str, declared_values: Iterable[str]) -> bool:
    return any(rule_matches_path(declared_path(value), path) for value in declared_values)


def path_hits_reserved(path: str, reserved_paths: Iterable[str] | None = None) -> bool:
    values = list(reserved_paths or RESERVED_PATHS)
    return any(rule_matches_path(declared_path(value), path) for value in values)


def task_reserved_paths(task: dict[str, Any]) -> list[str]:
    declared = list(task.get("reserved_paths", []))
    return list(dict.fromkeys([*RESERVED_PATHS, *declared]))


def task_reserved_conflicts(task: dict[str, Any]) -> list[str]:
    conflicts: list[str] = []
    reserved = task_reserved_paths(task)
    for field in ("allowed_dirs", "planned_write_paths", "planned_test_paths"):
        for path in task.get(field, []):
            if path_hits_reserved(path, reserved):
                conflicts.append(f"{field} hits reserved path: {path}")
    return conflicts


def path_to_scope_root(path: str) -> str:
    normalized = actual_path(path)
    parts = normalized.split("/")
    if len(parts) >= 2 and parts[0] in {"src", "tests", "docs"}:
        return "/".join(parts[:2])
    return parts[0]


def distinct_scope_roots(paths: Iterable[str]) -> set[str]:
    return {path_to_scope_root(path) for path in paths if path}


def collect_split_errors(tasks: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if len(tasks) > 2:
        errors.append("execution tasks exceed the hard limit of 2")
    for task in tasks:
        for conflict in task_reserved_conflicts(task):
            errors.append(f"{task['task_id']} {conflict}")
    for index, left in enumerate(tasks):
        left_write_rules = [declared_path(path) for path in left.get("planned_write_paths", [])]
        left_test_rules = [declared_path(path) for path in left.get("planned_test_paths", [])]
        left_reserved_rules = [declared_path(path) for path in left.get("reserved_paths", [])]
        for right in tasks[index + 1 :]:
            right_write_rules = [declared_path(path) for path in right.get("planned_write_paths", [])]
            right_test_rules = [declared_path(path) for path in right.get("planned_test_paths", [])]
            right_reserved_rules = [declared_path(path) for path in right.get("reserved_paths", [])]
            for left_rule in left_write_rules:
                for right_rule in right_write_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(f"{left['task_id']} write scope overlaps {right['task_id']}: {left_rule.raw} <-> {right_rule.raw}")
            for left_rule in left_test_rules:
                for right_rule in right_test_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(f"{left['task_id']} test scope overlaps {right['task_id']}: {left_rule.raw} <-> {right_rule.raw}")
            for left_rule in [*left_write_rules, *left_test_rules]:
                for right_rule in right_reserved_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(f"{left['task_id']} path overlaps {right['task_id']} reserved path: {left_rule.raw} <-> {right_rule.raw}")
            for right_rule in [*right_write_rules, *right_test_rules]:
                for left_rule in left_reserved_rules:
                    if declared_paths_overlap(right_rule, left_rule):
                        errors.append(f"{right['task_id']} path overlaps {left['task_id']} reserved path: {right_rule.raw} <-> {left_rule.raw}")
    return errors


def collect_active_execution_errors(tasks_by_id: dict[str, dict[str, Any]], worktree_registry: dict[str, Any]) -> list[str]:
    active_entries = [entry for entry in worktree_registry.get("entries", []) if entry.get("work_mode") == "execution" and entry.get("status") == "active"]
    errors: list[str] = []
    if len(active_entries) > 2:
        errors.append("active execution worktrees exceed the hard limit of 2")
    execution_tasks: list[dict[str, Any]] = []
    for entry in active_entries:
        task = tasks_by_id.get(entry["task_id"])
        if task is None:
            errors.append(f"missing task for active worktree entry: {entry['task_id']}")
            continue
        execution_tasks.append(task)
    errors.extend(collect_split_errors(execution_tasks))
    return errors


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


def validate_task(task: dict[str, Any]) -> None:
    required_fields = {"task_id", "title", "status", "task_kind", "execution_mode", "stage", "branch", "size_class", "automation_mode", "worker_state", "topology", "allowed_dirs", "reserved_paths", "planned_write_paths", "planned_test_paths", "required_tests", "task_file", "runlog_file"}
    missing = sorted(required_fields - set(task))
    if missing:
        raise GovernanceError(f"task missing required fields: {', '.join(missing)}")
    validators = [
        (task["status"] in STATUS_VALUES, f"invalid task status: {task['status']}"),
        (task["task_kind"] in TASK_KIND_VALUES, f"invalid task kind: {task['task_kind']}"),
        (task["execution_mode"] in EXECUTION_MODE_VALUES, f"invalid execution mode: {task['execution_mode']}"),
        (task["size_class"] in SIZE_CLASS_VALUES, f"invalid size_class: {task['size_class']}"),
        (task["automation_mode"] in AUTOMATION_MODE_VALUES, f"invalid automation_mode: {task['automation_mode']}"),
        (task["worker_state"] in WORKER_STATE_VALUES, f"invalid worker_state: {task['worker_state']}"),
        (task["topology"] in TOPOLOGY_VALUES, f"invalid topology: {task['topology']}"),
    ]
    for valid, message in validators:
        if not valid:
            raise GovernanceError(message)
    if task["size_class"] == "micro" and len(task.get("planned_write_paths", [])) > 8:
        raise GovernanceError("micro task exceeds planned_write_paths hard limit of 8")


def validate_worktree_entry(entry: dict[str, Any]) -> None:
    required_fields = {"task_id", "work_mode", "parent_task_id", "branch", "path", "status", "cleanup_state", "cleanup_attempts", "last_cleanup_error", "worker_owner"}
    missing = sorted(required_fields - set(entry))
    if missing:
        raise GovernanceError(f"worktree entry missing required fields: {', '.join(missing)}")
    validators = [
        (entry["status"] in WORKTREE_STATUS_VALUES, f"invalid worktree status: {entry['status']}"),
        (entry["cleanup_state"] in CLEANUP_STATE_VALUES, f"invalid cleanup_state: {entry['cleanup_state']}"),
        (entry["worker_owner"] in WORKER_OWNER_VALUES, f"invalid worker_owner: {entry['worker_owner']}"),
    ]
    for valid, message in validators:
        if not valid:
            raise GovernanceError(message)


def missing_required_tests(root: Path, task: dict[str, Any]) -> list[str]:
    runlog_text = read_text(root / task["runlog_file"])
    return [command for command in task.get("required_tests", []) if command not in runlog_text]


def task_required_tests_for_matrix(root: Path, task: dict[str, Any]) -> list[str]:
    matrix = load_test_matrix(root)
    module_id = task.get("module_id") or "governance_control_plane"
    module_rules = matrix.get("modules", {}).get(module_id, {})
    return list(module_rules.get(task["size_class"], {}).get("required_tests", []))


def infer_default_topology(task: dict[str, Any]) -> tuple[str, str]:
    if task["size_class"] == "micro":
        return "single_task", "micro tasks stay in a single task context"
    if task["size_class"] == "standard":
        return "single_worker", "standard tasks default to one worker"
    if "reserved_paths" not in task:
        return "single_worker", "heavy task must declare reserved_paths before split evaluation"
    roots = distinct_scope_roots(task.get("planned_write_paths", []))
    if task_reserved_conflicts(task):
        return "single_worker", "heavy task touches reserved paths and cannot auto-split"
    if not task.get("planned_write_paths") or not task.get("required_tests"):
        return "single_worker", "heavy task lacks clear write paths or required tests"
    if len(roots) >= 2:
        return "parallel_parent", "heavy task exposes multiple independent write scopes"
    return "single_worker", "heavy task lacks enough independent write scopes for safe parallelism"


def infer_default_automation_mode(task: dict[str, Any]) -> str:
    if task_reserved_conflicts(task):
        return "manual"
    topology, _ = infer_default_topology(task)
    if task["size_class"] == "heavy" and topology != "parallel_parent":
        return "manual"
    if task["size_class"] in {"micro", "standard"}:
        return "assisted"
    if task["required_tests"] and topology == "parallel_parent":
        return "autonomous"
    return "assisted"


def runner_action_gate(task: dict[str, Any]) -> dict[str, Any]:
    if task.get("status") == "idle":
        return {"prepare_worktrees": False, "auto_close_children": False, "reason": "idle current state has no live task to advance"}
    if task["automation_mode"] == "manual":
        return {"prepare_worktrees": False, "auto_close_children": False, "reason": "manual mode requires human coordination before automation actions"}
    if task["automation_mode"] == "assisted":
        return {"prepare_worktrees": task["topology"] == "parallel_parent", "auto_close_children": False, "reason": "assisted mode keeps automatic review and closeout disabled"}
    return {"prepare_worktrees": task["topology"] == "parallel_parent", "auto_close_children": task["topology"] == "parallel_parent", "reason": "autonomous mode allows parallel preparation and child closeout"}


def choose_worker_owner(existing_entries: list[dict[str, Any]]) -> str:
    active_owners = {entry.get("worker_owner") for entry in existing_entries if entry.get("status") == "active" and entry.get("worker_owner") in {"worker-a", "worker-b"}}
    return "worker-b" if "worker-a" in active_owners else "worker-a"


def ensure_task_and_runlog_exist(root: Path, task: dict[str, Any]) -> None:
    for field in ("task_file", "runlog_file"):
        path = root / task[field]
        if not path.exists():
            raise GovernanceError(f"missing {'task' if field == 'task_file' else 'runlog'} file: {task[field]}")
