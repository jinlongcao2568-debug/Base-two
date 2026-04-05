from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from governance_runtime import (
    AUTOMATION_MODE_VALUES,
    CLEANUP_STATE_VALUES,
    EXECUTION_WORKER_OWNERS,
    EXECUTION_MODE_VALUES,
    GovernanceError,
    REVIEW_BUNDLE_STATUS_VALUES,
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
    load_test_matrix,
    read_text,
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


def collect_split_errors(
    tasks: list[dict[str, Any]],
    task_policy: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    ceiling = dynamic_lane_ceiling(task_policy)
    if len(tasks) > ceiling:
        errors.append(f"execution tasks exceed the hard limit of {ceiling}")
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
                        errors.append(
                            f"{left['task_id']} write scope overlaps {right['task_id']}: "
                            f"{left_rule.raw} <-> {right_rule.raw}"
                        )
            for left_rule in left_test_rules:
                for right_rule in right_test_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(
                            f"{left['task_id']} test scope overlaps {right['task_id']}: "
                            f"{left_rule.raw} <-> {right_rule.raw}"
                        )
            for left_rule in [*left_write_rules, *left_test_rules]:
                for right_rule in right_reserved_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(
                            f"{left['task_id']} path overlaps {right['task_id']} reserved path: "
                            f"{left_rule.raw} <-> {right_rule.raw}"
                        )
            for right_rule in [*right_write_rules, *right_test_rules]:
                for left_rule in left_reserved_rules:
                    if declared_paths_overlap(right_rule, left_rule):
                        errors.append(
                            f"{right['task_id']} path overlaps {left['task_id']} reserved path: "
                            f"{right_rule.raw} <-> {left_rule.raw}"
                        )
    return errors


def collect_active_execution_errors(
    tasks_by_id: dict[str, dict[str, Any]],
    worktree_registry: dict[str, Any],
    task_policy: dict[str, Any] | None = None,
) -> list[str]:
    active_entries = [
        entry
        for entry in worktree_registry.get("entries", [])
        if entry.get("work_mode") == "execution" and entry.get("status") == "active"
    ]
    errors: list[str] = []
    ceiling = dynamic_lane_ceiling(task_policy)
    if len(active_entries) > ceiling:
        errors.append(f"active execution worktrees exceed the hard limit of {ceiling}")
    execution_tasks: list[dict[str, Any]] = []
    for entry in active_entries:
        task = tasks_by_id.get(entry["task_id"])
        if task is None:
            errors.append(f"missing task for active worktree entry: {entry['task_id']}")
            continue
        execution_tasks.append(task)
    errors.extend(collect_split_errors(execution_tasks, task_policy))
    return errors


SUCCESSOR_STATE_VALUES = {"immediate", "backlog"}


def effective_successor_state(task: dict[str, Any]) -> str | None:
    value = task.get("successor_state")
    if task.get("task_kind") == "coordination" and task.get("parent_task_id") is None:
        return value or "immediate"
    return value


def validate_task(task: dict[str, Any]) -> None:
    task.setdefault("lane_count", 1)
    task.setdefault("lane_index", None)
    task.setdefault("parallelism_plan_id", None)
    task.setdefault("review_bundle_status", "not_applicable")
    if task.get("task_kind") == "coordination" and task.get("parent_task_id") is None:
        if task.get("successor_state") is None:
            task["successor_state"] = "immediate"
    else:
        task.setdefault("successor_state", None)
    required_fields = {
        "task_id",
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
    }
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
        (
            task["review_bundle_status"] in REVIEW_BUNDLE_STATUS_VALUES,
            f"invalid review_bundle_status: {task['review_bundle_status']}",
        ),
    ]
    for valid, message in validators:
        if not valid:
            raise GovernanceError(message)
    successor_state = task.get("successor_state")
    if task.get("task_kind") == "coordination" and task.get("parent_task_id") is None:
        if successor_state not in SUCCESSOR_STATE_VALUES:
            raise GovernanceError(f"invalid successor_state: {successor_state!r}")
    elif successor_state not in {None, *SUCCESSOR_STATE_VALUES}:
        raise GovernanceError(f"invalid successor_state: {successor_state!r}")
    if task["size_class"] == "micro" and len(task.get("planned_write_paths", [])) > 8:
        raise GovernanceError("micro task exceeds planned_write_paths hard limit of 8")
    if not isinstance(task["lane_count"], int) or task["lane_count"] < 1:
        raise GovernanceError(f"invalid lane_count: {task['lane_count']!r}")
    if task["lane_index"] is not None and (
        not isinstance(task["lane_index"], int) or task["lane_index"] < 1 or task["lane_index"] > task["lane_count"]
    ):
        raise GovernanceError(f"invalid lane_index: {task['lane_index']!r}")
    if task["parallelism_plan_id"] is not None and not isinstance(task["parallelism_plan_id"], str):
        raise GovernanceError(f"invalid parallelism_plan_id: {task['parallelism_plan_id']!r}")


def validate_worktree_entry(entry: dict[str, Any]) -> None:
    required_fields = {
        "task_id",
        "work_mode",
        "parent_task_id",
        "branch",
        "path",
        "status",
        "cleanup_state",
        "cleanup_attempts",
        "last_cleanup_error",
        "worker_owner",
    }
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


def dynamic_parallelism_policy(task_policy: dict[str, Any] | None = None) -> dict[str, Any]:
    heavy_policy = ((task_policy or {}).get("size_classes", {}) or {}).get("heavy", {})
    return {
        "parallelism_mode": heavy_policy.get("parallelism_mode", "dynamic"),
        "dynamic_lane_ceiling_v1": int(heavy_policy.get("dynamic_lane_ceiling_v1", 4)),
        "min_disjoint_write_roots": int(heavy_policy.get("min_disjoint_write_roots", 2)),
        "required_tests_complete": heavy_policy.get("required_tests_complete", True),
        "reserved_path_conflict_policy": heavy_policy.get("reserved_path_conflict_policy", "block_parallelism"),
        "auto_downgrade_to_single_worker_on_conflict": heavy_policy.get(
            "auto_downgrade_to_single_worker_on_conflict",
            True,
        ),
    }


def dynamic_lane_ceiling(task_policy: dict[str, Any] | None = None) -> int:
    return max(1, dynamic_parallelism_policy(task_policy)["dynamic_lane_ceiling_v1"])


def execution_worker_owner_choices(task_policy: dict[str, Any] | None = None) -> tuple[str, ...]:
    return EXECUTION_WORKER_OWNERS[: dynamic_lane_ceiling(task_policy)]


def task_parallelism_plan(task: dict[str, Any], task_policy: dict[str, Any] | None = None) -> dict[str, Any]:
    task_id = task.get("task_id", "task")
    if task["size_class"] == "micro":
        return {
            "topology": "single_task",
            "lane_count": 1,
            "parallelism_plan_id": None,
            "reason": "micro tasks stay in a single task context",
        }
    if task["size_class"] == "standard":
        return {
            "topology": "single_worker",
            "lane_count": 1,
            "parallelism_plan_id": None,
            "reason": "standard tasks default to one worker",
        }

    policy = dynamic_parallelism_policy(task_policy)
    roots = distinct_scope_roots(task.get("planned_write_paths", []))
    if "reserved_paths" not in task:
        return {
            "topology": "single_worker",
            "lane_count": 1,
            "parallelism_plan_id": None,
            "reason": "heavy task must declare reserved_paths before split evaluation",
        }
    if task_reserved_conflicts(task) and policy["reserved_path_conflict_policy"] == "block_parallelism":
        return {
            "topology": "single_worker",
            "lane_count": 1,
            "parallelism_plan_id": None,
            "reason": "heavy task touches reserved paths and cannot auto-split",
        }
    if not task.get("planned_write_paths"):
        return {
            "topology": "single_worker",
            "lane_count": 1,
            "parallelism_plan_id": None,
            "reason": "heavy task lacks clear write paths for split evaluation",
        }
    if policy["required_tests_complete"] and not task.get("required_tests"):
        return {
            "topology": "single_worker",
            "lane_count": 1,
            "parallelism_plan_id": None,
            "reason": "heavy task lacks required tests for safe parallelism",
        }
    if len(roots) < policy["min_disjoint_write_roots"]:
        return {
            "topology": "single_worker",
            "lane_count": 1,
            "parallelism_plan_id": None,
            "reason": "heavy task lacks enough independent write scopes for safe parallelism",
        }

    lane_count = min(len(roots), dynamic_lane_ceiling(task_policy))
    return {
        "topology": "parallel_parent",
        "lane_count": lane_count,
        "parallelism_plan_id": f"plan-{task_id}-{lane_count}",
        "reason": f"heavy task exposes {len(roots)} independent write scopes; planner selected {lane_count} lanes",
    }


def infer_default_topology(
    task: dict[str, Any],
    task_policy: dict[str, Any] | None = None,
) -> tuple[str, str]:
    plan = task_parallelism_plan(task, task_policy)
    return plan["topology"], plan["reason"]


def infer_default_automation_mode(task: dict[str, Any], task_policy: dict[str, Any] | None = None) -> str:
    if task_reserved_conflicts(task):
        return "manual"
    topology, _ = infer_default_topology(task, task_policy)
    if task["size_class"] == "heavy" and topology != "parallel_parent":
        return "manual"
    if task["size_class"] in {"micro", "standard"}:
        return "assisted"
    if task["required_tests"] and topology == "parallel_parent":
        return "autonomous"
    return "assisted"


def runner_action_gate(task: dict[str, Any]) -> dict[str, Any]:
    if task.get("status") == "idle":
        return {
            "prepare_worktrees": False,
            "auto_close_children": False,
            "reason": "idle current state has no live task to advance",
        }
    if task["automation_mode"] == "manual":
        return {
            "prepare_worktrees": False,
            "auto_close_children": False,
            "reason": "manual mode requires human coordination before automation actions",
        }
    if task["automation_mode"] == "assisted":
        return {
            "prepare_worktrees": task["topology"] == "parallel_parent",
            "auto_close_children": False,
            "reason": "assisted mode keeps automatic review and closeout disabled",
        }
    return {
        "prepare_worktrees": task["topology"] == "parallel_parent",
        "auto_close_children": task["topology"] == "parallel_parent",
        "reason": "autonomous mode allows parallel preparation and child closeout",
    }


def choose_worker_owner(
    existing_entries: list[dict[str, Any]],
    task_policy: dict[str, Any] | None = None,
) -> str:
    available = execution_worker_owner_choices(task_policy)
    active_owners = {
        entry.get("worker_owner")
        for entry in existing_entries
        if entry.get("status") == "active" and entry.get("worker_owner") in available
    }
    for owner in available:
        if owner not in active_owners:
            return owner
    return available[0]


def ensure_task_and_runlog_exist(root: Path, task: dict[str, Any]) -> None:
    for field in ("task_file", "runlog_file"):
        path = root / task[field]
        if not path.exists():
            label = "task" if field == "task_file" else "runlog"
            raise GovernanceError(f"missing {label} file: {task[field]}")
