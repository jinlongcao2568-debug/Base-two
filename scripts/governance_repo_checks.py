from __future__ import annotations

from typing import Any

import yaml

from business_autopilot import load_business_policy
from governance_lib import (
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    WORKER_STATE_VALUES,
    collect_active_execution_errors,
    current_branch,
    ensure_task_and_runlog_exist,
    expected_narrative_assertions,
    extract_generated_fields,
    extract_markdown_fields,
    extract_narrative_assertions,
    git_status_paths,
    is_idle_current_payload,
    load_current_task,
    load_task_policy,
    path_hits_reserved,
    path_within_declared,
    read_roadmap,
    read_text,
    validate_idle_current_payload,
    validate_task,
    validate_worktree_entry,
    worktree_map,
    RUNLOG_MARKER_END,
    RUNLOG_MARKER_START,
    TASK_MARKER_END,
    TASK_MARKER_START,
)
from task_handoff import is_top_level_coordination_task


ROADMAP_ADVANCE_MODES = {"explicit_or_generated"}
ROADMAP_BRANCH_SWITCH_POLICIES = {"create_or_switch_if_clean"}
ROADMAP_PRIORITY_VALUES = {"governance_automation", "authority_chain", "business_automation"}


def _validate_registry_entries(root, registry: dict[str, Any], worktrees: dict[str, Any]) -> None:
    for task in registry.get("tasks", []):
        validate_task(task)
        ensure_task_and_runlog_exist(root, task)
    for entry in worktrees.get("entries", []):
        validate_worktree_entry(entry)


def _resolve_execution_context_task(root, tasks_by_id: dict[str, dict[str, Any]], execution_context_path):
    context = yaml.safe_load(execution_context_path.read_text(encoding="utf-8"))
    task = tasks_by_id.get(context["task_id"])
    if task is None:
        raise GovernanceError(f"execution context task missing from registry: {context['task_id']}")
    if task["task_kind"] != "execution":
        raise GovernanceError("execution context points to a non-execution task")
    branch = current_branch(root)
    if branch != context["branch"]:
        raise GovernanceError(f"branch mismatch: expected {context['branch']}, got {branch}")
    return task, context.get("allowed_dirs", []), context.get("planned_write_paths", [])


def _resolve_current_task(root, tasks_by_id: dict[str, dict[str, Any]]):
    current_task = load_current_task(root)
    if is_idle_current_payload(current_task):
        raise GovernanceError("no live current task; repository is in idle state")
    task = tasks_by_id.get(current_task["current_task_id"])
    if task is None:
        raise GovernanceError(f"current task missing from registry: {current_task['current_task_id']}")
    comparisons = {
        "current_task_id": "task_id",
        "title": "title",
        "status": "status",
        "task_kind": "task_kind",
        "execution_mode": "execution_mode",
        "stage": "stage",
        "branch": "branch",
        "size_class": "size_class",
        "automation_mode": "automation_mode",
        "worker_state": "worker_state",
        "topology": "topology",
        "reserved_paths": "reserved_paths",
        "allowed_dirs": "allowed_dirs",
        "planned_write_paths": "planned_write_paths",
        "planned_test_paths": "planned_test_paths",
        "required_tests": "required_tests",
        "task_file": "task_file",
        "runlog_file": "runlog_file",
        "lane_count": "lane_count",
        "lane_index": "lane_index",
        "parallelism_plan_id": "parallelism_plan_id",
        "review_bundle_status": "review_bundle_status",
    }
    for current_key, registry_key in comparisons.items():
        if current_task[current_key] != task[registry_key]:
            raise GovernanceError(f"current task mismatch for field {current_key}")
    if task["worker_state"] not in WORKER_STATE_VALUES:
        raise GovernanceError(f"invalid worker_state in current task: {task['worker_state']}")
    if current_task["status"] == "done":
        raise GovernanceError("current task cannot remain on a done task")
    branch = current_branch(root)
    if branch != current_task["branch"]:
        raise GovernanceError(f"branch mismatch: expected {current_task['branch']}, got {branch}")
    return task, current_task.get("allowed_dirs", []), current_task.get("planned_write_paths", [])


def _resolve_current_state(root, tasks_by_id: dict[str, dict[str, Any]]):
    current_task = load_current_task(root)
    if is_idle_current_payload(current_task):
        validate_idle_current_payload(current_task)
        return current_task, [], [], True
    task, allowed_dirs, planned_write_paths = _resolve_current_task(root, tasks_by_id)
    return task, allowed_dirs, planned_write_paths, False


def _validate_current_worktree_entry(active_task: dict[str, Any], worktrees: dict[str, Any]) -> None:
    entry = worktree_map(worktrees).get(active_task["task_id"])
    if entry is None:
        raise GovernanceError(f"current task missing worktree entry: {active_task['task_id']}")
    if entry.get("work_mode") != "coordination":
        raise GovernanceError("current task worktree entry must be coordination mode")
    if entry.get("status") != "active":
        raise GovernanceError("current task worktree entry must be active")
    if entry.get("branch") != active_task["branch"]:
        raise GovernanceError("current task worktree entry branch mismatch")


def _validate_idle_worktree_state(worktrees: dict[str, Any]) -> None:
    active_coordination = [
        entry
        for entry in worktrees.get("entries", [])
        if entry.get("work_mode") == "coordination" and entry.get("status") == "active"
    ]
    if active_coordination:
        task_ids = ", ".join(entry["task_id"] for entry in active_coordination)
        raise GovernanceError(f"idle current state cannot keep active coordination worktrees: {task_ids}")


def _validate_roadmap_policy(roadmap_frontmatter: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]]) -> None:
    if roadmap_frontmatter.get("advance_mode") not in ROADMAP_ADVANCE_MODES:
        raise GovernanceError("roadmap advance_mode is missing or invalid")
    if not isinstance(roadmap_frontmatter.get("auto_create_missing_task"), bool):
        raise GovernanceError("roadmap auto_create_missing_task must be a boolean")
    if roadmap_frontmatter.get("branch_switch_policy") not in ROADMAP_BRANCH_SWITCH_POLICIES:
        raise GovernanceError("roadmap branch_switch_policy is missing or invalid")
    priority_order = roadmap_frontmatter.get("priority_order")
    if not isinstance(priority_order, list) or not priority_order:
        raise GovernanceError("roadmap priority_order must be a non-empty list")
    if any(item not in ROADMAP_PRIORITY_VALUES for item in priority_order):
        raise GovernanceError("roadmap priority_order contains an unknown value")
    if len(set(priority_order)) != len(priority_order):
        raise GovernanceError("roadmap priority_order must not contain duplicates")
    if not isinstance(roadmap_frontmatter.get("business_automation_enabled"), bool):
        raise GovernanceError("roadmap business_automation_enabled must be a boolean")
    if roadmap_frontmatter.get("business_automation_enabled"):
        load_business_policy(roadmap_frontmatter)
    next_task_id = roadmap_frontmatter.get("next_recommended_task_id")
    if next_task_id is not None and next_task_id not in tasks_by_id:
        raise GovernanceError("roadmap next_recommended_task_id missing from registry")


def _validate_roadmap_alignment(root, current_state: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]]) -> None:
    roadmap_frontmatter, roadmap_body = read_roadmap(root)
    _validate_roadmap_policy(roadmap_frontmatter, tasks_by_id)
    if is_idle_current_payload(current_state):
        if roadmap_frontmatter.get("current_task_id") is not None:
            raise GovernanceError("roadmap current_task_id mismatch for idle current state")
        if roadmap_frontmatter.get("current_phase") != "idle":
            raise GovernanceError("roadmap current_phase mismatch for idle current state")
        if "no live current task" not in roadmap_body.lower():
            raise GovernanceError("roadmap body missing idle current-task zero-state text")
        return
    if roadmap_frontmatter.get("current_task_id") != current_state["task_id"]:
        raise GovernanceError("roadmap current_task_id mismatch")
    if roadmap_frontmatter.get("current_phase") != current_state["stage"]:
        raise GovernanceError("roadmap current_phase mismatch")


def _validate_artifact_fields(fields: dict[str, str], expected: dict[str, str], label: str) -> None:
    for key, value in expected.items():
        if fields.get(key) != value:
            raise GovernanceError(f"{label} mismatch for field {key}")


def _validate_generated_fields(
    generated: dict[str, str],
    active_task: dict[str, Any],
    label: str,
    keys: tuple[str, ...],
) -> None:
    def rendered(value: Any) -> str:
        return "null" if value is None else str(value)

    for key in keys:
        if generated.get(key) != rendered(active_task[key]):
            raise GovernanceError(f"{label} generated metadata mismatch for field {key}")


def _validate_narrative_fields(narrative: dict[str, str], active_task: dict[str, Any], label: str) -> None:
    for key, value in expected_narrative_assertions(active_task).items():
        if narrative.get(key) != value:
            raise GovernanceError(f"{label} narrative assertions mismatch for field {key}")


def _validate_task_file_alignment(root, active_task: dict[str, Any]) -> None:
    text = read_text(root / active_task["task_file"])
    fields = extract_markdown_fields(text)
    generated = extract_generated_fields(text, TASK_MARKER_START, TASK_MARKER_END)
    narrative = extract_narrative_assertions(text)
    expected = {
        "task_id": active_task["task_id"],
        "status": active_task["status"],
        "stage": active_task["stage"],
        "branch": active_task["branch"],
        "worker_state": active_task["worker_state"],
        "lane_count": str(active_task.get("lane_count", 1)),
        "lane_index": "null" if active_task.get("lane_index") is None else str(active_task.get("lane_index")),
        "parallelism_plan_id": "null"
        if active_task.get("parallelism_plan_id") is None
        else str(active_task.get("parallelism_plan_id")),
        "review_bundle_status": str(active_task.get("review_bundle_status", "not_applicable")),
    }
    _validate_artifact_fields(fields, expected, "task file")
    _validate_generated_fields(
        generated,
        active_task,
        "task",
        (
            "status",
            "task_kind",
            "execution_mode",
            "size_class",
            "automation_mode",
            "worker_state",
            "topology",
            "lane_count",
            "lane_index",
            "parallelism_plan_id",
            "review_bundle_status",
            "branch",
        ),
    )
    _validate_narrative_fields(narrative, active_task, "task")


def _validate_runlog_alignment(root, active_task: dict[str, Any]) -> None:
    text = read_text(root / active_task["runlog_file"])
    fields = extract_markdown_fields(text)
    generated = extract_generated_fields(text, RUNLOG_MARKER_START, RUNLOG_MARKER_END)
    narrative = extract_narrative_assertions(text)
    expected = {
        "task_id": active_task["task_id"],
        "status": active_task["status"],
        "stage": active_task["stage"],
        "branch": active_task["branch"],
        "worker_state": active_task["worker_state"],
        "lane_count": str(active_task.get("lane_count", 1)),
        "lane_index": "null" if active_task.get("lane_index") is None else str(active_task.get("lane_index")),
        "parallelism_plan_id": "null"
        if active_task.get("parallelism_plan_id") is None
        else str(active_task.get("parallelism_plan_id")),
        "review_bundle_status": str(active_task.get("review_bundle_status", "not_applicable")),
    }
    _validate_artifact_fields(fields, expected, "runlog")
    _validate_artifact_fields(generated, expected, "runlog generated metadata")
    _validate_narrative_fields(narrative, active_task, "runlog")


def _resolve_active_task(root, tasks_by_id: dict[str, dict[str, Any]]):
    execution_context_path = root / EXECUTION_CONTEXT_FILE
    if execution_context_path.exists():
        task, allowed_dirs, planned_write_paths = _resolve_execution_context_task(
            root,
            tasks_by_id,
            execution_context_path,
        )
        return task, allowed_dirs, planned_write_paths, True, False
    task_or_payload, allowed_dirs, planned_write_paths, idle_current = _resolve_current_state(root, tasks_by_id)
    return task_or_payload, allowed_dirs, planned_write_paths, False, idle_current


def _validate_modified_paths(
    active_task: dict[str, Any],
    modified_paths: list[str],
    allowed_dirs: list[str],
    planned_write_paths: list[str],
    in_execution_context: bool,
) -> None:
    active_handoff_path = None
    if active_task.get("task_id") is not None:
        active_handoff_path = f"docs/governance/handoffs/{active_task['task_id']}.yaml"
    if active_task["status"] == "done" and modified_paths:
        raise GovernanceError("implementation changes are not allowed when task status is done")
    for path in modified_paths:
        if (
            active_handoff_path is not None
            and
            not in_execution_context
            and is_top_level_coordination_task(active_task)
            and path == active_handoff_path
        ):
            continue
        if not path_within_declared(path, allowed_dirs):
            raise GovernanceError(f"modified path outside allowed_dirs: {path}")
        if not path_within_declared(path, planned_write_paths):
            raise GovernanceError(f"modified path outside planned_write_paths: {path}")
        if in_execution_context and path_hits_reserved(path, active_task.get("reserved_paths", [])):
            raise GovernanceError(f"execution worktree cannot touch task reserved path: {path}")
        if in_execution_context and path_hits_reserved(path):
            raise GovernanceError(f"execution worktree cannot touch reserved path: {path}")


def run_repo_checks(root, registry: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]], worktrees: dict[str, Any]) -> None:
    task_policy = load_task_policy(root)
    _validate_registry_entries(root, registry, worktrees)
    active_task, allowed_dirs, planned_write_paths, in_execution_context, idle_current = _resolve_active_task(
        root,
        tasks_by_id,
    )
    if not in_execution_context:
        if idle_current:
            _validate_idle_worktree_state(worktrees)
            _validate_roadmap_alignment(root, active_task, tasks_by_id)
        else:
            _validate_current_worktree_entry(active_task, worktrees)
            _validate_roadmap_alignment(root, active_task, tasks_by_id)
            _validate_task_file_alignment(root, active_task)
            _validate_runlog_alignment(root, active_task)
    modified_paths = git_status_paths(root)
    _validate_modified_paths(
        active_task,
        modified_paths,
        allowed_dirs,
        planned_write_paths,
        in_execution_context,
    )
    active_errors = collect_active_execution_errors(tasks_by_id, worktrees, task_policy)
    if active_errors:
        raise GovernanceError(active_errors[0])
