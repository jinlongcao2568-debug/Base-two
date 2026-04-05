from __future__ import annotations

import argparse
import re
from typing import Any

from business_autopilot import (
    BUSINESS_AUTOPILOT_CAPABILITY_ID,
    build_business_successor_round,
    capability_is_open,
    load_business_policy,
)
from governance_lib import (
    GovernanceError,
    branch_exists,
    build_current_task_payload,
    current_branch,
    dump_yaml,
    ensure_clean_worktree,
    find_repo_root,
    git,
    is_idle_current_payload,
    iso_now,
    load_capability_map,
    load_current_task,
    load_task_policy,
    load_task_registry,
    load_worktree_registry,
    missing_required_tests,
    sync_task_artifacts,
    task_map,
    validate_task,
    worktree_map,
    write_roadmap,
)
from task_rendering import (
    find_task,
    pause_other_doing_tasks,
    update_runlog_file,
    update_task_file,
    upsert_coordination_entry,
)


ADVANCE_MODE_VALUES = {"explicit_or_generated"}
BRANCH_SWITCH_POLICY_VALUES = {"create_or_switch_if_clean"}
PRIORITY_VALUES = {"governance_automation", "authority_chain", "business_automation"}

AUTOPILOT_CAPABILITY_ID = "roadmap_autopilot_continuation"
AUTOPILOT_BLUEPRINT_ID = "roadmap_autopilot_continuation"


def _read_roadmap_state(root):
    from governance_lib import read_roadmap

    return read_roadmap(root)


def _load_continuation_policy(frontmatter: dict[str, Any]) -> dict[str, Any]:
    policy = {
        "advance_mode": frontmatter.get("advance_mode"),
        "auto_create_missing_task": frontmatter.get("auto_create_missing_task"),
        "branch_switch_policy": frontmatter.get("branch_switch_policy"),
        "priority_order": frontmatter.get("priority_order"),
        "business_automation_enabled": frontmatter.get("business_automation_enabled"),
    }
    if policy["advance_mode"] not in ADVANCE_MODE_VALUES:
        raise GovernanceError("roadmap advance_mode is missing or invalid")
    if not isinstance(policy["auto_create_missing_task"], bool):
        raise GovernanceError("roadmap auto_create_missing_task must be a boolean")
    if policy["branch_switch_policy"] not in BRANCH_SWITCH_POLICY_VALUES:
        raise GovernanceError("roadmap branch_switch_policy is missing or invalid")
    if not isinstance(policy["priority_order"], list) or not policy["priority_order"]:
        raise GovernanceError("roadmap priority_order must be a non-empty list")
    if any(item not in PRIORITY_VALUES for item in policy["priority_order"]):
        raise GovernanceError("roadmap priority_order contains an unknown value")
    if len(set(policy["priority_order"])) != len(policy["priority_order"]):
        raise GovernanceError("roadmap priority_order must not contain duplicates")
    if not isinstance(policy["business_automation_enabled"], bool):
        raise GovernanceError("roadmap business_automation_enabled must be a boolean")
    if policy["business_automation_enabled"]:
        load_business_policy(frontmatter)
    return policy


def _switch_or_create_branch(root, branch: str) -> str:
    if current_branch(root) == branch:
        return "current"
    ensure_clean_worktree(root)
    if branch_exists(root, branch):
        git(root, "switch", branch)
        return "switched"
    git(root, "switch", "-c", branch)
    return "created"


def _mark_task_done(task: dict[str, Any], worktrees: dict[str, Any]) -> None:
    task["status"] = "done"
    task["worker_state"] = "completed"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    task["closed_at"] = iso_now()
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is not None:
        entry["status"] = "closed"


def _activate_task(task: dict[str, Any]) -> None:
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    if task.get("activated_at") is None:
        task["activated_at"] = iso_now()


def _task_boundary_error(task: dict[str, Any]) -> str | None:
    if task.get("task_kind") != "coordination":
        return "successor must be a coordination task"
    if task.get("execution_mode") != "shared_coordination":
        return "successor must stay in shared_coordination mode"
    for field in ("allowed_dirs", "planned_write_paths", "required_tests"):
        if not task.get(field):
            return f"successor boundary is incomplete: missing {field}"
    return None


def _dependency_errors(task: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for dependency_id in task.get("depends_on_task_ids", []):
        dependency = tasks_by_id.get(dependency_id)
        if dependency is None:
            errors.append(f"successor dependency missing from registry: {dependency_id}")
        elif dependency.get("status") != "done":
            errors.append(f"successor dependency not satisfied: {dependency_id}")
    return errors


def _validate_successor_candidate(
    task: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]], current_task_id: str | None
) -> None:
    if current_task_id is not None and task["task_id"] == current_task_id:
        raise GovernanceError("successor cannot equal the current task")
    if task.get("parent_task_id") is not None:
        raise GovernanceError("successor must be a top-level coordination task")
    if task["status"] == "done":
        raise GovernanceError("successor is already done")
    if task["status"] == "blocked":
        reason = task.get("blocked_reason") or "blocked without recorded reason"
        raise GovernanceError(f"successor is blocked: {reason}")
    boundary_error = _task_boundary_error(task)
    if boundary_error:
        raise GovernanceError(boundary_error)
    dependency_errors = _dependency_errors(task, tasks_by_id)
    if dependency_errors:
        raise GovernanceError(dependency_errors[0])


def _ensure_unique_successor_landscape(
    tasks: list[dict[str, Any]], current_task_id: str | None, successor_id: str
) -> None:
    excluded_ids = {successor_id}
    if current_task_id is not None:
        excluded_ids.add(current_task_id)
    conflicting = [
        task["task_id"]
        for task in tasks
        if task.get("task_kind") == "coordination"
        and task["task_id"] not in excluded_ids
        and task.get("parent_task_id") is None
        and task["status"] not in {"done", "blocked"}
    ]
    if conflicting:
        joined = ", ".join(conflicting)
        raise GovernanceError(f"successor landscape is not unique: {successor_id} conflicts with {joined}")


def _resolve_explicit_successor(
    registry: dict[str, Any], frontmatter: dict[str, Any], current_task_id: str | None
):
    explicit_id = frontmatter.get("next_recommended_task_id")
    if not explicit_id:
        return None
    tasks_by_id = task_map(registry)
    task = tasks_by_id.get(explicit_id)
    if task is None:
        raise GovernanceError(f"roadmap next_recommended_task_id missing from registry: {explicit_id}")
    _validate_successor_candidate(task, tasks_by_id, current_task_id)
    _ensure_unique_successor_landscape(registry.get("tasks", []), current_task_id, task["task_id"])
    return task


def _find_blueprint(task_policy: dict[str, Any], blueprint_id: str) -> dict[str, Any]:
    for blueprint in task_policy.get("task_blueprints", []):
        if blueprint.get("blueprint_id") == blueprint_id:
            return blueprint
    raise GovernanceError(f"task blueprint missing: {blueprint_id}")


def _next_auto_task_id(tasks: list[dict[str, Any]]) -> str:
    highest = 0
    for task in tasks:
        match = re.match(r"^TASK-AUTO-(\d{3})$", task.get("task_id", ""))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"TASK-AUTO-{highest + 1:03d}"


def _autopilot_gap_open(capability_map: dict[str, Any]) -> bool:
    capability = next(
        (item for item in capability_map.get("capabilities", []) if item.get("capability_id") == AUTOPILOT_CAPABILITY_ID),
        None,
    )
    if capability is None:
        return True
    return capability.get("status") != "implemented"


def _default_autopilot_capability() -> dict[str, Any]:
    return {
        "capability_id": AUTOPILOT_CAPABILITY_ID,
        "status": "in_progress",
        "source_of_truth": [
            "docs/governance/DEVELOPMENT_ROADMAP.md",
            "docs/governance/TASK_POLICY.yaml",
            "docs/governance/CAPABILITY_MAP.yaml",
        ],
        "scripts": [
            "scripts/task_ops.py",
            "scripts/task_continuation_ops.py",
            "scripts/automation_runner.py",
        ],
        "tests": [
            "pytest tests/governance -q",
            "pytest tests/automation -q",
        ],
    }


def _mark_capability_in_progress(capability_map: dict[str, Any]) -> None:
    capabilities = capability_map.setdefault("capabilities", [])
    for capability in capabilities:
        if capability.get("capability_id") == AUTOPILOT_CAPABILITY_ID:
            capability["status"] = "in_progress"
            return
    capabilities.append(_default_autopilot_capability())


def _build_generated_task(
    registry: dict[str, Any], blueprint: dict[str, Any], current_task_id: str | None
) -> dict[str, Any]:
    task_id = _next_auto_task_id(registry.get("tasks", []))
    task = {
        "task_id": task_id,
        "title": blueprint["title"],
        "status": "queued",
        "task_kind": blueprint["task_kind"],
        "execution_mode": blueprint["execution_mode"],
        "parent_task_id": None,
        "stage": blueprint["stage"],
        "branch": blueprint["branch_template"].format(task_id=task_id),
        "size_class": blueprint["size_class"],
        "automation_mode": blueprint["automation_mode"],
        "worker_state": "idle",
        "blocked_reason": None,
        "last_reported_at": iso_now(),
        "topology": blueprint["topology"],
        "allowed_dirs": list(blueprint["allowed_dirs"]),
        "reserved_paths": list(blueprint.get("reserved_paths", [])),
        "planned_write_paths": list(blueprint["planned_write_paths"]),
        "planned_test_paths": list(blueprint["planned_test_paths"]),
        "required_tests": list(blueprint["required_tests"]),
        "task_file": f"docs/governance/tasks/{task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
        "depends_on_task_ids": [current_task_id] if current_task_id is not None else [],
        "generated_from_blueprint": blueprint["blueprint_id"],
    }
    validate_task(task)
    return task


def _resolve_generated_successor(
    root,
    registry: dict[str, Any],
    capability_map: dict[str, Any],
    task_policy: dict[str, Any],
    policy: dict[str, Any],
    current_task_id: str | None,
):
    if not policy["auto_create_missing_task"]:
        return None
    for gap_type in policy["priority_order"]:
        if gap_type == "business_automation" and not policy["business_automation_enabled"]:
            continue
        if gap_type == "governance_automation" and _autopilot_gap_open(capability_map):
            blueprint = _find_blueprint(task_policy, AUTOPILOT_BLUEPRINT_ID)
            task = _build_generated_task(registry, blueprint, current_task_id)
            registry.setdefault("tasks", []).append(task)
            _mark_capability_in_progress(capability_map)
            return task
        if gap_type == "business_automation" and not capability_is_open(
            capability_map, BUSINESS_AUTOPILOT_CAPABILITY_ID
        ):
            generated = build_business_successor_round(root, registry, task_policy)
            if generated is None:
                continue
            parent_task, child_tasks, _ = generated
            parent_task["depends_on_task_ids"] = [current_task_id] if current_task_id is not None else []
            registry.setdefault("tasks", []).append(parent_task)
            registry.setdefault("tasks", []).extend(child_tasks)
            return parent_task
    return None


def _persist_activation(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    frontmatter: dict[str, Any],
    body: str,
    capability_map: dict[str, Any],
    task: dict[str, Any],
    touched_task_ids: list[str],
    next_action: str,
) -> None:
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(root / "docs/governance/CURRENT_TASK.yaml", build_current_task_payload(task, next_action))
    dump_yaml(root / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    frontmatter["current_task_id"] = task["task_id"]
    frontmatter["current_phase"] = task["stage"]
    write_roadmap(root, frontmatter, body)
    update_task_file(root, task)
    update_runlog_file(root, task)
    sync_task_artifacts(root, registry, touched_task_ids)


def _load_continue_roadmap_state(root):
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    capability_map = load_capability_map(root)
    task_policy = load_task_policy(root)
    current_task_payload = load_current_task(root)
    current_task = None
    if not is_idle_current_payload(current_task_payload):
        current_task = find_task(registry["tasks"], current_task_payload["current_task_id"])
    return registry, worktrees, capability_map, task_policy, current_task_payload, current_task


def _close_review_task_if_needed(root, current_task: dict[str, Any] | None, worktrees: dict[str, Any]) -> None:
    if current_task is None:
        return
    ensure_clean_worktree(root)
    if current_branch(root) != current_task["branch"]:
        _switch_or_create_branch(root, current_task["branch"])
    if current_task["status"] != "review":
        return
    missing = missing_required_tests(root, current_task)
    if missing:
        missing_text = ", ".join(missing)
        raise GovernanceError(f"required tests missing from runlog: {missing_text}")
    _mark_task_done(current_task, worktrees)


def _resolve_roadmap_successor(
    root,
    registry: dict[str, Any],
    capability_map: dict[str, Any],
    task_policy: dict[str, Any],
    frontmatter: dict[str, Any],
    current_task_id: str | None,
):
    policy = _load_continuation_policy(frontmatter)
    successor = _resolve_explicit_successor(registry, frontmatter, current_task_id)
    if successor is not None:
        return successor, "explicit"
    successor = _resolve_generated_successor(
        root,
        registry,
        capability_map,
        task_policy,
        policy,
        current_task_id,
    )
    if successor is None:
        raise GovernanceError("no successor is available for continue-roadmap")
    return successor, "generated"


def _activate_successor(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    capability_map: dict[str, Any],
    frontmatter: dict[str, Any],
    body: str,
    current_task: dict[str, Any] | None,
    successor: dict[str, Any],
) -> str:
    tasks_by_id = task_map(registry)
    current_task_id = current_task["task_id"] if current_task is not None else None
    _validate_successor_candidate(successor, tasks_by_id, current_task_id)
    _ensure_unique_successor_landscape(registry["tasks"], current_task_id, successor["task_id"])
    branch_action = _switch_or_create_branch(root, successor["branch"])
    touched_task_ids = pause_other_doing_tasks(registry["tasks"], successor["task_id"])
    if current_task_id is not None and current_task_id not in touched_task_ids:
        touched_task_ids.append(current_task["task_id"])
    _activate_task(successor)
    update_task_file(root, successor)
    update_runlog_file(root, successor)
    for child_task_id in successor.get("child_task_ids", []):
        child_task = tasks_by_id[child_task_id]
        update_task_file(root, child_task)
        update_runlog_file(root, child_task)
        touched_task_ids.append(child_task_id)
    upsert_coordination_entry(worktrees, successor, root)
    frontmatter["next_recommended_task_id"] = successor["task_id"]
    _persist_activation(
        root,
        registry,
        worktrees,
        frontmatter,
        body,
        capability_map,
        successor,
        touched_task_ids,
        "Continue by roadmap; the current task is closed and the next coordination task is active.",
    )
    return branch_action


def cmd_continue_current(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    if is_idle_current_payload(current_task):
        raise GovernanceError("no live current task; use continue-roadmap or explicit activation")
    task = find_task(registry["tasks"], current_task["current_task_id"])

    if task["status"] == "blocked":
        reason = task.get("blocked_reason") or "blocked without recorded reason"
        raise GovernanceError(f"current task is blocked: {reason}")
    if task["status"] in {"review", "done"}:
        raise GovernanceError("current task is in review/done state; use continue-roadmap")

    branch_action = _switch_or_create_branch(root, task["branch"])
    if task["status"] == "doing":
        print(f"[OK] continue-current {task['task_id']} branch={branch_action}")
        return 0

    frontmatter, body = _read_roadmap_state(root)
    capability_map = load_capability_map(root)
    touched_task_ids = pause_other_doing_tasks(registry["tasks"], task["task_id"])
    _activate_task(task)
    upsert_coordination_entry(worktrees, task, root)
    _persist_activation(
        root,
        registry,
        worktrees,
        frontmatter,
        body,
        capability_map,
        task,
        touched_task_ids,
        "Continue the live current task and keep the branch/control-plane state aligned.",
    )
    print(f"[OK] continue-current reactivated {task['task_id']} branch={branch_action}")
    return 0


def cmd_continue_roadmap(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry, worktrees, capability_map, task_policy, current_task_payload, current_task = _load_continue_roadmap_state(root)

    if current_task_payload["status"] in {"doing", "paused"}:
        return cmd_continue_current(args)
    if current_task_payload["status"] == "blocked":
        reason = current_task.get("blocked_reason") or "blocked without recorded reason"
        raise GovernanceError(f"current task is blocked: {reason}")

    frontmatter, body = _read_roadmap_state(root)
    _close_review_task_if_needed(root, current_task, worktrees)
    successor, source = _resolve_roadmap_successor(
        root,
        registry,
        capability_map,
        task_policy,
        frontmatter,
        current_task["task_id"] if current_task is not None else None,
    )
    branch_action = _activate_successor(
        root,
        registry,
        worktrees,
        capability_map,
        frontmatter,
        body,
        current_task,
        successor,
    )
    print(f"[OK] continue-roadmap advanced to {successor['task_id']} source={source} branch={branch_action}")
    return 0
