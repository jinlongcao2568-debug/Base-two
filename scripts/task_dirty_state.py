from __future__ import annotations

from pathlib import Path
from typing import Any

from governance_lib import (
    CURRENT_TASK_FILE,
    ROADMAP_FILE,
    TASK_REGISTRY_FILE,
    WORKTREE_REGISTRY_FILE,
    actual_path,
    git_status_paths,
    path_hits_reserved,
    path_within_declared,
)
from task_handoff import handoff_path, is_top_level_coordination_task


DIRTY_STATE_VALUES = {"clean", "governance_dirty_only", "checkpointable_dirty", "unsafe_dirty"}


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def governance_scope_paths(root: Path, current_payload: dict[str, Any], task: dict[str, Any]) -> list[str]:
    paths = [
        actual_path(str(CURRENT_TASK_FILE)),
        actual_path(str(TASK_REGISTRY_FILE)),
        actual_path(str(WORKTREE_REGISTRY_FILE)),
        actual_path(str(ROADMAP_FILE)),
        actual_path(task["task_file"]),
        actual_path(task["runlog_file"]),
    ]
    if is_top_level_coordination_task(task):
        task_handoff = handoff_path(root, task["task_id"])
        if task_handoff.exists():
            paths.append(actual_path(task_handoff.relative_to(root)))
    if current_payload.get("current_task_id") != task["task_id"] and task.get("status") != "done":
        paths = [path for path in paths if path != actual_path(str(CURRENT_TASK_FILE))]
    return _dedupe(paths)


def classify_task_dirty_state(
    root: Path,
    *,
    current_payload: dict[str, Any],
    task: dict[str, Any],
    dirty_paths: list[str] | None = None,
) -> dict[str, Any]:
    dirty = [actual_path(path) for path in (dirty_paths if dirty_paths is not None else git_status_paths(root))]
    governance_paths: list[str] = []
    task_scoped_paths: list[str] = []
    unsafe_paths: list[str] = []
    direct_governance_paths = set(governance_scope_paths(root, current_payload, task))
    scope = list(task.get("planned_write_paths") or task.get("allowed_dirs") or [])
    reserved = list(task.get("reserved_paths") or [])

    for dirty_path in dirty:
        if dirty_path in direct_governance_paths:
            governance_paths.append(dirty_path)
            continue
        if reserved and path_hits_reserved(dirty_path, reserved):
            unsafe_paths.append(dirty_path)
            continue
        if path_within_declared(dirty_path, scope):
            task_scoped_paths.append(dirty_path)
            continue
        unsafe_paths.append(dirty_path)

    governance_paths = _dedupe(governance_paths)
    task_scoped_paths = _dedupe(task_scoped_paths)
    unsafe_paths = _dedupe(unsafe_paths)
    checkpointable_paths = _dedupe([*governance_paths, *task_scoped_paths])

    if unsafe_paths:
        dirty_state = "unsafe_dirty"
        checkpoint_strategy = "blocked_unsafe_dirty"
    elif task_scoped_paths:
        dirty_state = "checkpointable_dirty"
        checkpoint_strategy = "local_checkpoint_commit"
    elif governance_paths:
        dirty_state = "governance_dirty_only"
        checkpoint_strategy = "local_checkpoint_commit"
    else:
        dirty_state = "clean"
        checkpoint_strategy = "not_needed"

    return {
        "dirty_state": dirty_state,
        "dirty_paths": dirty,
        "dirty_paths_by_class": {
            "governance_paths": governance_paths,
            "task_scoped_paths": task_scoped_paths,
            "unsafe_paths": unsafe_paths,
        },
        "checkpointable_paths": checkpointable_paths,
        "checkpoint_required": dirty_state in {"governance_dirty_only", "checkpointable_dirty"},
        "checkpoint_strategy": checkpoint_strategy,
    }


def classify_unscoped_dirty_state(root: Path, dirty_paths: list[str] | None = None) -> dict[str, Any]:
    dirty = [actual_path(path) for path in (dirty_paths if dirty_paths is not None else git_status_paths(root))]
    dirty = _dedupe(dirty)
    dirty_state = "unsafe_dirty" if dirty else "clean"
    checkpoint_strategy = "manual_cleanup_required" if dirty else "not_needed"
    return {
        "dirty_state": dirty_state,
        "dirty_paths": dirty,
        "dirty_paths_by_class": {
            "governance_paths": [],
            "task_scoped_paths": [],
            "unsafe_paths": dirty,
        },
        "checkpointable_paths": [],
        "checkpoint_required": False,
        "checkpoint_strategy": checkpoint_strategy,
    }
