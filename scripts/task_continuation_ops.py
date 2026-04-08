from __future__ import annotations

import argparse
import copy
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
    append_runlog_bullets,
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
    load_yaml,
    sync_task_artifacts,
    task_map,
    task_required_tests_for_matrix,
    effective_successor_state,
    validate_task,
    worktree_map,
    write_roadmap,
)
from task_closeout import assess_live_closeout
from task_coordination_lease import (
    assess_coordination_lease,
    claim_coordination_lease,
    coordination_thread_id,
    current_session_id,
    ensure_closeout_write_lease,
)
from task_dirty_state import classify_task_dirty_state, classify_unscoped_dirty_state
from task_handoff import build_recovery_pack, render_recovery_lines
from task_rendering import (
    find_task,
    pause_other_doing_tasks,
    persist_idle_state,
    update_runlog_file,
    update_task_file,
    upsert_coordination_entry,
)
from task_publish_ops import checkpoint_preflight, checkpoint_task_results
from roadmap_claim_next import claim_next


ADVANCE_MODE_VALUES = {"explicit_or_generated"}
BRANCH_SWITCH_POLICY_VALUES = {"create_or_switch_if_clean"}
PRIORITY_VALUES = {"governance_automation", "authority_chain", "business_automation"}

AUTOPILOT_CAPABILITY_ID = "roadmap_autopilot_continuation"
AUTOPILOT_BLUEPRINT_ID = "roadmap_autopilot_continuation"
ROADMAP_BACKLOG_FILE = "docs/governance/ROADMAP_BACKLOG.yaml"


def _record_runtime_event(root, **kwargs) -> None:
    from orchestration_runtime import record_session_event

    record_session_event(root, **kwargs)


def _runtime_status_for_task(task: dict[str, Any] | None) -> str:
    from orchestration_runtime import runtime_status_for_task

    return runtime_status_for_task(task)


def _append_auto_takeover_note(root, task: dict[str, Any], *, reason: str, lease: dict[str, Any]) -> None:
    if not lease.get("auto_takeover"):
        return
    append_runlog_bullets(
        root,
        task,
        "Execution Log",
        [f"`{iso_now()}`: automatic lease takeover previous_owner=`{lease.get('previous_owner_session_id')}` reason=`{reason}`"],
    )


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


def _recoverable_predecessor_task(root, registry: dict[str, Any], current_payload: dict[str, Any]) -> dict[str, Any] | None:
    if not is_idle_current_payload(current_payload):
        return None
    branch = current_branch(root)
    candidates = [
        task
        for task in registry.get("tasks", [])
        if task.get("task_kind") == "coordination"
        and task.get("parent_task_id") is None
        and task.get("status") == "done"
        and task.get("branch") == branch
    ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda task: (
            task.get("closed_at") or "",
            task.get("last_reported_at") or "",
            task["task_id"],
        ),
        reverse=True,
    )
    for candidate in candidates:
        dirty = classify_task_dirty_state(root, current_payload=current_payload, task=candidate)
        if dirty["dirty_state"] != "clean":
            return candidate
    return None



def _validate_successor_candidate(
    task: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]], current_task_id: str | None
) -> None:
    if current_task_id is not None and task["task_id"] == current_task_id:
        raise GovernanceError("successor cannot equal the current task")
    if task.get("parent_task_id") is not None:
        raise GovernanceError("successor must be a top-level coordination task")
    if task.get("absorbed_by"):
        raise GovernanceError(f"successor is absorbed by {task['absorbed_by']}")
    if task["status"] == "done":
        raise GovernanceError("successor is already done")
    if task["status"] == "blocked":
        reason = task.get("blocked_reason") or "blocked without recorded reason"
        raise GovernanceError(f"successor is blocked: {reason}")
    if effective_successor_state(task) != "immediate":
        raise GovernanceError(f"successor must be immediate, got {effective_successor_state(task)!r}")
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
        and not task.get("absorbed_by")
        and task["status"] not in {"done", "blocked"}
        and effective_successor_state(task) == "immediate"
    ]
    if conflicting:
        joined = ", ".join(conflicting)
        raise GovernanceError(f"successor landscape is not unique: {successor_id} conflicts with {joined}")

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
            "python scripts/check_repo.py",
            "python scripts/check_hygiene.py src docs tests",
            "pytest tests/governance/test_task_continuation.py -q",
            "pytest tests/governance/test_automation_intent.py -q",
            "pytest tests/automation/test_automation_runner.py -q",
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
    root = find_repo_root()
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
        "lane_count": 1,
        "lane_index": None,
        "parallelism_plan_id": None,
        "review_bundle_status": "not_applicable",
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
        "depends_on_task_ids": [current_task_id] if current_task_id is not None else [],
        "generated_from_blueprint": blueprint["blueprint_id"],
    }
    if not task["required_tests"]:
        task["required_tests"] = task_required_tests_for_matrix(root, task)
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
    if _compiled_roadmap_dispatch_enabled(root):
        return None
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
    if current_task["status"] not in {"doing", "review"}:
        return
    assessment = assess_live_closeout(root, current_task=current_task, worktrees=worktrees)
    if assessment["status"] == "not_applicable":
        return
    if assessment["status"] != "ready":
        if current_task["status"] == "doing":
            return
        details = [*assessment.get("blockers", []), *assessment.get("diagnostics", [])]
        if not details:
            details = [assessment.get("summary", "current review task cannot auto-close")]
        raise GovernanceError("; ".join(details))
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
    claim_coordination_lease(root, successor, reason="continue-roadmap successor activation")
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


def _record_continue_current_event(
    root,
    *,
    task_id: str | None,
    writer_state: str,
    runtime_status: str,
    blocked_reason: str | None = None,
    safe_write: bool,
) -> None:
    _record_runtime_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="continue-current",
        mode="manual",
        writer_state=writer_state,
        current_task_id=task_id,
        continue_intent="current",
        runtime_status=runtime_status,
        blocked_reason=blocked_reason,
        safe_write=safe_write,
    )


def _readonly_continue_current(root, task: dict[str, Any], lease: dict[str, Any]) -> int:
    print(
        f"[READONLY] continue-current recovery only: active coordination lease is owned by "
        f"`{lease['owner_session_id']}`; use handoff, release, or takeover before writing."
    )
    _record_continue_current_event(
        root,
        task_id=task["task_id"],
        writer_state="readonly",
        runtime_status="readonly",
        blocked_reason=f"lease owned by {lease['owner_session_id']}",
        safe_write=False,
    )
    return 0


def _close_review_ready_current_task(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    current_payload: dict[str, Any],
    task: dict[str, Any],
    branch_action: str,
) -> int:
    assessment = assess_live_closeout(
        root,
        registry=registry,
        worktrees=worktrees,
        current_payload=current_payload,
        current_task=task,
    )
    if assessment["status"] != "ready":
        details = [*assessment.get("blockers", []), *assessment.get("diagnostics", [])]
        if not details:
            details = [assessment.get("summary", "current review task cannot auto-close")]
        raise GovernanceError("; ".join(details))
    frontmatter, body = _read_roadmap_state(root)
    _mark_task_done(task, worktrees)
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    persist_idle_state(
        root,
        registry,
        worktrees,
        frontmatter,
        body,
        [task["task_id"]],
        "continue-current closed the review-ready task and returned the control plane to idle.",
    )
    _record_continue_current_event(
        root,
        task_id=None,
        writer_state="writable",
        runtime_status="idle",
        safe_write=True,
    )
    print(f"[OK] continue-current closed {task['task_id']} to idle branch={branch_action}")
    return 0


def _close_to_idle_when_no_successor(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    current_payload: dict[str, Any],
    current_task: dict[str, Any],
) -> int:
    lease = ensure_closeout_write_lease(root, current_task, reason="continue-roadmap", allow_takeover=True)
    branch_action = _switch_or_create_branch(root, current_task["branch"])
    _append_auto_takeover_note(root, current_task, reason="continue-roadmap", lease=lease)
    return _close_review_ready_current_task(
        root,
        registry,
        worktrees,
        current_payload,
        current_task,
        branch_action,
    )


def _maybe_close_without_successor(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    current_payload: dict[str, Any],
    current_task: dict[str, Any] | None,
) -> int | None:
    if current_task is None:
        return None
    closeout = assess_live_closeout(
        root,
        registry=registry,
        worktrees=worktrees,
        current_payload=current_payload,
        current_task=current_task,
    )
    if closeout["status"] != "ready":
        return None
    return _close_to_idle_when_no_successor(root, registry, worktrees, current_payload, current_task)


def _claim_continue_roadmap_lease(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    current_payload: dict[str, Any],
    current_task: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if current_task is None:
        return None
    closeout = assess_live_closeout(
        root,
        registry=registry,
        worktrees=worktrees,
        current_payload=current_payload,
        current_task=current_task,
    )
    return ensure_closeout_write_lease(
        root,
        current_task,
        reason="continue-roadmap",
        allow_takeover=closeout["status"] == "ready",
    )


def _handle_no_successor_continue_roadmap(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    current_payload: dict[str, Any],
    current_task: dict[str, Any] | None,
) -> int:
    if _compiled_roadmap_dispatch_enabled(root):
        closeout_result = _maybe_close_without_successor(
            root,
            registry,
            worktrees,
            current_payload,
            current_task,
        )
        if closeout_result is not None:
            return _claim_roadmap_candidate_via_claim_next(root)
        if current_task is None and is_idle_current_payload(current_payload):
            return _claim_roadmap_candidate_via_claim_next(root)
        raise GovernanceError("current task is still active; continue-roadmap cannot switch until ai_guarded closeout is ready")
    if current_task is None and is_idle_current_payload(current_payload):
        raise GovernanceError("no successor is available for continue-roadmap from idle control plane")
    closeout_result = _maybe_close_without_successor(
        root,
        registry,
        worktrees,
        current_payload,
        current_task,
    )
    if closeout_result is not None:
        return closeout_result
    _record_runtime_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="continue-roadmap",
        mode="manual",
        writer_state="writable",
        current_task_id=None,
        continue_intent="roadmap",
        runtime_status="idle",
        safe_write=True,
    )
    print("[OK] continue-roadmap no successor is available; repository remains idle")
    return 0


def _advance_continue_roadmap(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    capability_map: dict[str, Any],
    task_policy: dict[str, Any],
    current_payload: dict[str, Any],
    current_task: dict[str, Any] | None,
) -> int:
    if _compiled_roadmap_dispatch_enabled(root):
        if current_task is not None:
            _close_to_idle_when_no_successor(root, registry, worktrees, current_payload, current_task)
        return _claim_roadmap_candidate_via_claim_next(root)
    frontmatter, body = _read_roadmap_state(root)
    lease = _claim_continue_roadmap_lease(
        root,
        registry,
        worktrees,
        current_payload,
        current_task,
    )
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
    if current_task is not None and lease is not None:
        _append_auto_takeover_note(root, current_task, reason="continue-roadmap", lease=lease)
    _record_runtime_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="continue-roadmap",
        mode="manual",
        writer_state="writable",
        current_task_id=successor["task_id"],
        continue_intent="roadmap",
        runtime_status=_runtime_status_for_task(successor),
        safe_write=True,
    )
    print(f"[OK] continue-roadmap advanced to {successor['task_id']} source={source} branch={branch_action}")
    return 0


def _reactivate_current_task(
    root,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    task: dict[str, Any],
    branch_action: str,
) -> int:
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
    _record_continue_current_event(
        root,
        task_id=task["task_id"],
        writer_state="writable",
        runtime_status=_runtime_status_for_task(task),
        safe_write=True,
    )
    print(f"[OK] continue-current reactivated {task['task_id']} branch={branch_action}")
    return 0

def _checkpoint_resolvable_closeout_blockers(blockers: list[str]) -> list[str]:
    filtered: list[str] = []
    for blocker in blockers:
        if blocker.startswith("dirty paths outside task checkpoint scope:"):
            continue
        filtered.append(blocker)
    return filtered


def _formal_immediate_candidates(
    registry: dict[str, Any], current_task_id: str | None
) -> list[dict[str, Any]]:
    return [
        task
        for task in registry.get("tasks", [])
        if task.get("task_kind") == "coordination"
        and task.get("parent_task_id") is None
        and task["task_id"] != current_task_id
        and not task.get("absorbed_by")
        and task["status"] != "done"
        and effective_successor_state(task) == "immediate"
    ]


def _resolve_formal_immediate_successor(
    registry: dict[str, Any], current_task_id: str | None
) -> dict[str, Any] | None:
    tasks_by_id = task_map(registry)
    candidates = _formal_immediate_candidates(registry, current_task_id)
    if not candidates:
        return None
    if len(candidates) > 1:
        joined = ", ".join(task["task_id"] for task in candidates)
        raise GovernanceError(f"successor landscape is not unique: {joined}")
    candidate = candidates[0]
    _validate_successor_candidate(candidate, tasks_by_id, current_task_id)
    return candidate


def _resolve_explicit_successor(
    registry: dict[str, Any], frontmatter: dict[str, Any], current_task_id: str | None
) -> tuple[dict[str, Any] | None, str | None]:
    explicit_id = frontmatter.get("next_recommended_task_id")
    if not explicit_id:
        return None, None
    tasks_by_id = task_map(registry)
    task = tasks_by_id.get(explicit_id)
    if task is None:
        return None, explicit_id
    try:
        _validate_successor_candidate(task, tasks_by_id, current_task_id)
        _ensure_unique_successor_landscape(registry.get("tasks", []), current_task_id, task["task_id"])
    except GovernanceError as error:
        message = str(error)
        if (
            "already done" in message
            or "not unique" in message
            or "dependency not satisfied" in message
            or "absorbed by" in message
        ):
            return None, explicit_id
        raise
    return task, None


def _resolve_roadmap_successor(
    root,
    registry: dict[str, Any],
    capability_map: dict[str, Any],
    task_policy: dict[str, Any],
    frontmatter: dict[str, Any],
    current_task_id: str | None,
):
    policy = _load_continuation_policy(frontmatter)
    explicit_successor, stale_explicit_id = _resolve_explicit_successor(registry, frontmatter, current_task_id)
    if explicit_successor is not None:
        return explicit_successor, "explicit"

    successor = _resolve_formal_immediate_successor(registry, current_task_id)
    if successor is not None:
        if stale_explicit_id is not None:
            frontmatter["next_recommended_task_id"] = successor["task_id"]
        return successor, "formal_immediate"

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
    if stale_explicit_id is not None:
        frontmatter["next_recommended_task_id"] = successor["task_id"]
    return successor, "generated"


def _dirty_for_continuation_context(
    root,
    *,
    current_payload: dict[str, Any],
    current_task: dict[str, Any] | None,
    recoverable_predecessor: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if current_task is not None:
        return classify_task_dirty_state(root, current_payload=current_payload, task=current_task), current_task
    if recoverable_predecessor is not None:
        return (
            classify_task_dirty_state(root, current_payload=current_payload, task=recoverable_predecessor),
            recoverable_predecessor,
        )
    return classify_unscoped_dirty_state(root), None


def _compiled_roadmap_dispatch_enabled(root) -> bool:
    backlog_path = root / ROADMAP_BACKLOG_FILE
    if not backlog_path.exists():
        return False
    backlog = load_yaml(backlog_path) or {}
    scheduler_policy = backlog.get("scheduler_policy") or {}
    compiler_policy = backlog.get("compiler_policy") or {}
    return (
        str(scheduler_policy.get("dispatch_authority") or "") == "compiled_candidate_graph"
        and str(compiler_policy.get("mode") or "") == "module_graph_compiler"
    )


def _claim_roadmap_candidate_via_claim_next(root) -> int:
    args = argparse.Namespace(
        write_claim=False,
        promote_task=True,
        worktree_root=None,
        worker_owner=None,
        dispatch_target="worktree_pool",
        full_clone_slot_id=None,
        window_id="continue-roadmap",
        lease_minutes=30,
        now=None,
    )
    selected, blocked = claim_next(root, args)
    if selected is None:
        reason = "; ".join(blocked[0]["blockers"]) if blocked else "no roadmap candidates are available"
        raise GovernanceError(reason)
    print(
        f"[OK] continue-roadmap claimed roadmap candidate {selected['candidate_id']} "
        f"task_id_hint={selected['task_id_hint']} takeover_mode={selected.get('takeover_mode', 'none')}"
    )
    return 0
    return classify_unscoped_dirty_state(root), None


def _base_continuation_readiness(dirty: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "blocked",
        "recoverable_predecessor_task_id": None,
        "dirty_state": dirty["dirty_state"],
        "dirty_paths_by_class": dirty["dirty_paths_by_class"],
        "checkpoint_strategy": dirty["checkpoint_strategy"],
        "checkpoint_required": dirty["checkpoint_required"],
        "checkpoint_eligible": False,
        "next_successor_task_id": None,
        "successor_source": None,
        "blockers": [],
        "recommended_action": "resolve the continuation blockers and rerun continue-roadmap",
        "checkpoint_task_id": None,
    }


def _continue_current_readiness(dirty: dict[str, Any]) -> dict[str, Any]:
    readiness = _base_continuation_readiness(dirty)
    if dirty["dirty_state"] == "unsafe_dirty":
        readiness["blockers"] = [
            f"unsafe dirty paths: {', '.join(dirty['dirty_paths_by_class']['unsafe_paths'])}"
        ]
        readiness["recommended_action"] = "clean the unsafe dirty paths before continuing the live task"
        return readiness
    readiness["status"] = "continue-current"
    readiness["recommended_action"] = "continue-current"
    return readiness


def _checkpoint_context(
    root,
    *,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    current_payload: dict[str, Any],
    current_task: dict[str, Any] | None,
    recoverable_predecessor: dict[str, Any] | None,
    dirty: dict[str, Any],
) -> tuple[list[str], dict[str, Any] | None, dict[str, Any] | None, str | None]:
    blockers: list[str] = []
    checkpoint_task: dict[str, Any] | None = None
    closeout: dict[str, Any] | None = None
    recoverable_task_id: str | None = None
    current_status = current_payload.get("status")

    if current_status == "blocked":
        reason = None if current_task is None else current_task.get("blocked_reason")
        blockers.append(f"current task is blocked: {reason or 'blocked without recorded reason'}")
    elif current_status == "done":
        blockers.append("CURRENT_TASK.yaml should not remain on a done task; repair the live control-plane state first")
    elif current_status in {"doing", "paused", "review"} and current_task is not None:
        closeout = assess_live_closeout(
            root,
            registry=registry,
            worktrees=worktrees,
            current_payload=current_payload,
            current_task=current_task,
        )
        if dirty["checkpoint_required"] and closeout["status"] in {"ready", "blocked"}:
            checkpoint_task = current_task
    elif recoverable_predecessor is not None:
        recoverable_task_id = recoverable_predecessor["task_id"]
        if dirty["checkpoint_required"]:
            checkpoint_task = recoverable_predecessor
    elif dirty["dirty_state"] != "clean":
        blockers.append("idle control plane has dirty paths but no recoverable predecessor task")

    if dirty["dirty_state"] == "unsafe_dirty":
        blockers.append(
            f"dirty paths outside task checkpoint scope: {', '.join(dirty['dirty_paths_by_class']['unsafe_paths'])}"
        )

    return blockers, checkpoint_task, closeout, recoverable_task_id


def _apply_live_task_continuation_guard(
    *,
    readiness: dict[str, Any],
    blockers: list[str],
    closeout: dict[str, Any] | None,
    current_payload: dict[str, Any],
) -> None:
    if current_payload.get("status") not in {"doing", "paused"}:
        return
    if closeout is None or closeout["status"] == "not_applicable":
        blockers.append(
            "current task is still active; continue-roadmap cannot switch until ai_guarded closeout is ready"
        )
        readiness["recommended_action"] = "continue-current"
        return
    if closeout["status"] != "ready":
        readiness["recommended_action"] = "continue-current"


def _apply_checkpoint_readiness(
    root,
    *,
    readiness: dict[str, Any],
    blockers: list[str],
    checkpoint_task: dict[str, Any] | None,
    closeout: dict[str, Any] | None,
    dirty: dict[str, Any],
) -> None:
    if dirty["checkpoint_required"] and checkpoint_task is not None and dirty["dirty_state"] != "unsafe_dirty":
        readiness["checkpoint_task_id"] = checkpoint_task["task_id"]
        checkpoint = checkpoint_preflight(root, task_id=checkpoint_task["task_id"])
        readiness["checkpoint_eligible"] = checkpoint["status"] == "ready"
        if checkpoint["status"] != "ready":
            blockers.extend(checkpoint.get("blockers", []))
    else:
        readiness["checkpoint_required"] = False

    if closeout is not None and closeout["status"] != "ready":
        closeout_blockers = list(closeout.get("blockers", []))
        if dirty["checkpoint_required"] and readiness["checkpoint_eligible"]:
            closeout_blockers = _checkpoint_resolvable_closeout_blockers(closeout_blockers)
        blockers.extend(closeout_blockers)
        blockers.extend(closeout.get("diagnostics", []))


def _preview_continuation_successor(
    root,
    *,
    readiness: dict[str, Any],
    blockers: list[str],
    registry: dict[str, Any],
    capability_map: dict[str, Any],
    task_policy: dict[str, Any],
    current_payload: dict[str, Any],
    current_task: dict[str, Any] | None,
) -> None:
    if _compiled_roadmap_dispatch_enabled(root):
        if current_task is None or (current_payload.get("status") in {"doing", "review"} and not blockers):
            args = argparse.Namespace(
                write_claim=False,
                promote_task=False,
                worktree_root=None,
                worker_owner=None,
                dispatch_target="worktree_pool",
                full_clone_slot_id=None,
                window_id="continue-roadmap-preview",
                lease_minutes=30,
                now=None,
            )
            selected, blocked_candidates = claim_next(root, args)
            if selected is not None:
                readiness["next_successor_task_id"] = selected["task_id_hint"]
                readiness["successor_source"] = "roadmap_candidate_graph"
                return
            if blocked_candidates:
                blockers.append("; ".join(blocked_candidates[0]["blockers"]))
            return
    current_task_id = current_task["task_id"] if current_task is not None and not is_idle_current_payload(current_payload) else None
    try:
        successor, source = _resolve_roadmap_successor(
            root,
            copy.deepcopy(registry),
            copy.deepcopy(capability_map),
            copy.deepcopy(task_policy),
            copy.deepcopy(_read_roadmap_state(root)[0]),
            current_task_id,
        )
        readiness["next_successor_task_id"] = successor["task_id"]
        readiness["successor_source"] = source
    except GovernanceError as error:
        message = str(error)
        if message == "no successor is available for continue-roadmap":
            readiness["status"] = "no_successor"
            readiness["recommended_action"] = "stay idle until a valid successor is available"
            if is_idle_current_payload(current_payload):
                blockers.append("no successor is available for continue-roadmap from idle control plane")
            return
        if "successor landscape is not unique" in message:
            readiness["status"] = "ambiguous"
        blockers.append(message)


def _finalize_continuation_readiness(
    *,
    readiness: dict[str, Any],
    blockers: list[str],
    dirty: dict[str, Any],
    checkpoint_task: dict[str, Any] | None,
) -> dict[str, Any]:
    readiness["blockers"] = list(dict.fromkeys(blockers))
    if readiness.get("status") == "no_successor" and not readiness["blockers"]:
        readiness["next_successor_task_id"] = None
        readiness["successor_source"] = None
        return readiness
    if readiness.get("status") == "ambiguous" and readiness["blockers"]:
        readiness["recommended_action"] = "resolve successor ambiguity or dependencies before continuing"
        return readiness
    if not readiness["blockers"]:
        readiness["status"] = "ready"
        readiness["recommended_action"] = "continue-roadmap"
        return readiness

    if dirty["dirty_state"] == "unsafe_dirty":
        readiness["recommended_action"] = "clean the unsafe dirty paths before continuing"
    elif dirty["checkpoint_required"] and checkpoint_task is not None and not readiness["checkpoint_eligible"]:
        readiness["recommended_action"] = "clean or narrow the dirty worktree to the task checkpoint scope"
    elif dirty["checkpoint_required"] and checkpoint_task is None:
        readiness["recommended_action"] = "clean the idle worktree or restore the recoverable predecessor state"
    elif readiness["next_successor_task_id"] is None:
        readiness["recommended_action"] = "resolve successor ambiguity or dependencies before continuing"
    return readiness


def assess_continuation_readiness(
    root,
    *,
    registry: dict[str, Any] | None = None,
    worktrees: dict[str, Any] | None = None,
    capability_map: dict[str, Any] | None = None,
    task_policy: dict[str, Any] | None = None,
    current_payload: dict[str, Any] | None = None,
    current_task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or load_task_registry(root)
    worktrees = worktrees or load_worktree_registry(root)
    capability_map = capability_map or load_capability_map(root)
    task_policy = task_policy or load_task_policy(root)
    current_payload = current_payload or load_current_task(root)
    if current_task is None and not is_idle_current_payload(current_payload):
        current_task = find_task(registry["tasks"], current_payload["current_task_id"])

    recoverable_predecessor = _recoverable_predecessor_task(root, registry, current_payload)
    dirty, dirty_owner = _dirty_for_continuation_context(
        root,
        current_payload=current_payload,
        current_task=current_task,
        recoverable_predecessor=recoverable_predecessor,
    )

    readiness = _base_continuation_readiness(dirty)
    blockers, checkpoint_task, closeout, recoverable_task_id = _checkpoint_context(
        root,
        registry=registry,
        worktrees=worktrees,
        current_payload=current_payload,
        current_task=current_task,
        recoverable_predecessor=recoverable_predecessor,
        dirty=dirty,
    )
    if dirty_owner is recoverable_predecessor and recoverable_predecessor is not None:
        readiness["recoverable_predecessor_task_id"] = recoverable_task_id
    _apply_checkpoint_readiness(
        root,
        readiness=readiness,
        blockers=blockers,
        checkpoint_task=checkpoint_task,
        closeout=closeout,
        dirty=dirty,
    )
    _apply_live_task_continuation_guard(
        readiness=readiness,
        blockers=blockers,
        closeout=closeout,
        current_payload=current_payload,
    )
    _preview_continuation_successor(
        root,
        readiness=readiness,
        blockers=blockers,
        registry=registry,
        capability_map=capability_map,
        task_policy=task_policy,
        current_payload=current_payload,
        current_task=current_task,
    )
    return _finalize_continuation_readiness(
        readiness=readiness,
        blockers=blockers,
        dirty=dirty,
        checkpoint_task=checkpoint_task,
    )


def cmd_continue_current(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_payload = load_current_task(root)
    if is_idle_current_payload(current_payload):
        raise GovernanceError("no live current task; use continue-roadmap or explicit activation")
    task = find_task(registry["tasks"], current_payload["current_task_id"])

    if task["status"] == "blocked":
        reason = task.get("blocked_reason") or "blocked without recorded reason"
        raise GovernanceError(f"current task is blocked: {reason}")
    if task["status"] == "done":
        raise GovernanceError("current task is already done; use continue-roadmap or explicit activation")

    dirty = classify_task_dirty_state(root, current_payload=current_payload, task=task)
    if dirty["dirty_state"] == "unsafe_dirty":
        raise GovernanceError(f"unsafe dirty paths: {', '.join(dirty['dirty_paths_by_class']['unsafe_paths'])}")

    recovery_pack, recovery_source, recovery_warnings = build_recovery_pack(root, task)
    for line in render_recovery_lines(recovery_pack, recovery_source, recovery_warnings):
        print(line)

    closeout = assess_live_closeout(
        root,
        registry=registry,
        worktrees=worktrees,
        current_payload=current_payload,
        current_task=task,
    )
    lease = assess_coordination_lease(root, task)
    if lease["enforced"] and not lease["can_write"]:
        if closeout["status"] == "ready":
            lease = ensure_closeout_write_lease(root, task, reason="continue-current", allow_takeover=True)
        else:
            return _readonly_continue_current(root, task, lease)
    elif lease["enforced"]:
        claim_coordination_lease(root, task, reason="continue-current")

    branch_action = _switch_or_create_branch(root, task["branch"])
    _append_auto_takeover_note(root, task, reason="continue-current", lease=lease)
    if closeout["status"] == "ready" and task["status"] in {"doing", "review"}:
        return _close_review_ready_current_task(root, registry, worktrees, current_payload, task, branch_action)
    if task["status"] == "review":
        details = [*closeout.get("blockers", []), *closeout.get("diagnostics", [])]
        if not details:
            details = [closeout.get("summary", "current review task cannot auto-close")]
        raise GovernanceError("; ".join(details))
    if task["status"] == "doing":
        _record_continue_current_event(
            root,
            task_id=task["task_id"],
            writer_state="writable",
            runtime_status=_runtime_status_for_task(task),
            safe_write=True,
        )
        print(f"[OK] continue-current {task['task_id']} branch={branch_action}")
        return 0

    return _reactivate_current_task(root, registry, worktrees, task, branch_action)


def cmd_continue_roadmap(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry, worktrees, capability_map, task_policy, current_task_payload, current_task = _load_continue_roadmap_state(root)

    readiness = assess_continuation_readiness(
        root,
        registry=registry,
        worktrees=worktrees,
        capability_map=capability_map,
        task_policy=task_policy,
        current_payload=current_task_payload,
        current_task=current_task,
    )
    if readiness["status"] == "no_successor":
        if readiness.get("blockers"):
            raise GovernanceError("; ".join(readiness["blockers"]))
        return _handle_no_successor_continue_roadmap(
            root,
            registry,
            worktrees,
            current_task_payload,
            current_task,
        )
    if readiness["status"] != "ready":
        raise GovernanceError("; ".join(readiness["blockers"]) or "continue-roadmap blocked")

    if readiness["checkpoint_required"]:
        checkpoint_task_id = readiness.get("checkpoint_task_id")
        if checkpoint_task_id is None:
            raise GovernanceError("continuation checkpoint task is missing")
        checkpoint_task_results(root, task_id=checkpoint_task_id)
    return _advance_continue_roadmap(
        root,
        registry,
        worktrees,
        capability_map,
        task_policy,
        current_task_payload,
        current_task,
    )
