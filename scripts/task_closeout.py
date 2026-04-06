from __future__ import annotations

from pathlib import Path
from typing import Any

from governance_lib import (
    GovernanceError,
    current_branch,
    extract_generated_fields,
    extract_markdown_fields,
    is_idle_current_payload,
    load_current_task,
    load_task_registry,
    load_yaml,
    load_worktree_registry,
    missing_required_tests,
    read_roadmap,
    read_text,
    RUNLOG_MARKER_END,
    RUNLOG_MARKER_START,
    TASK_MARKER_END,
    TASK_MARKER_START,
    worktree_map,
)
from task_dirty_state import classify_task_dirty_state
from task_rendering import find_task


CURRENT_PAYLOAD_SYNC_FIELDS = (
    "title",
    "status",
    "task_kind",
    "execution_mode",
    "parent_task_id",
    "stage",
    "branch",
    "size_class",
    "automation_mode",
    "worker_state",
    "blocked_reason",
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
)

ARTIFACT_SYNC_FIELDS = (
    "task_id",
    "status",
    "stage",
    "branch",
    "worker_state",
    "lane_count",
    "lane_index",
    "parallelism_plan_id",
    "review_bundle_status",
)
GENERATED_SYNC_FIELDS = (
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
)
AI_GUARDED_CLOSEOUT_MARKER = "ai_guarded closeout candidate"
PENDING_EXCEPTION_STATUSES = {"pending", "pending_approval", "draft", "submitted"}


def _append_unique(items: list[str], value: str | None) -> None:
    if value and value not in items:
        items.append(value)


def _payload_diagnostics(current_payload: dict[str, Any], current_task: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    if current_payload.get("current_task_id") != current_task["task_id"]:
        diagnostics.append(
            "CURRENT_TASK.yaml current_task_id differs from TASK_REGISTRY: "
            f"{current_payload.get('current_task_id')!r} != {current_task['task_id']!r}"
        )
    for field in CURRENT_PAYLOAD_SYNC_FIELDS:
        if current_payload.get(field) != current_task.get(field):
            diagnostics.append(
                f"CURRENT_TASK.yaml field `{field}` differs from TASK_REGISTRY: "
                f"{current_payload.get(field)!r} != {current_task.get(field)!r}"
            )
    return diagnostics


def _worktree_diagnostics(root: Path, current_task: dict[str, Any], worktrees: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    entry = worktree_map(worktrees).get(current_task["task_id"])
    if entry is None:
        diagnostics.append(f"WORKTREE_REGISTRY is missing the live task entry for `{current_task['task_id']}`")
        return diagnostics
    if entry.get("work_mode") != "coordination":
        diagnostics.append(
            f"WORKTREE_REGISTRY work_mode differs from coordination: {entry.get('work_mode')!r}"
        )
    if entry.get("parent_task_id") != current_task.get("parent_task_id"):
        diagnostics.append(
            "WORKTREE_REGISTRY parent_task_id differs from TASK_REGISTRY: "
            f"{entry.get('parent_task_id')!r} != {current_task.get('parent_task_id')!r}"
        )
    if entry.get("branch") != current_task["branch"]:
        diagnostics.append(
            f"WORKTREE_REGISTRY branch differs from TASK_REGISTRY: {entry.get('branch')!r} != {current_task['branch']!r}"
        )
    if entry.get("worker_owner") != "coordinator":
        diagnostics.append(
            f"WORKTREE_REGISTRY worker_owner differs from coordinator: {entry.get('worker_owner')!r}"
        )
    if current_task["status"] == "review" and entry.get("status") != "active":
        diagnostics.append(f"review task worktree must stay active, got {entry.get('status')!r}")
    if current_branch(root) != current_task["branch"]:
        diagnostics.append(
            f"current branch differs from live task branch: {current_branch(root)!r} != {current_task['branch']!r}"
        )
    return diagnostics


def _artifact_diagnostics(root: Path, current_task: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    for label, path_value, start_marker, end_marker in (
        ("task file", current_task["task_file"], TASK_MARKER_START, TASK_MARKER_END),
        ("runlog", current_task["runlog_file"], RUNLOG_MARKER_START, RUNLOG_MARKER_END),
    ):
        try:
            text = read_text(root / path_value)
            fields = extract_markdown_fields(text)
            generated = extract_generated_fields(text, start_marker, end_marker)
        except GovernanceError as error:
            diagnostics.append(f"{label} alignment failed: {error}")
            continue
        for key in ARTIFACT_SYNC_FIELDS:
            expected = "null" if current_task.get(key) is None else str(current_task.get(key))
            if fields.get(key) != expected:
                diagnostics.append(f"{label} mismatch for field `{key}`")
        generated_keys = GENERATED_SYNC_FIELDS if label == "task file" else ARTIFACT_SYNC_FIELDS
        for key in generated_keys:
            expected = "null" if current_task.get(key) is None else str(current_task.get(key))
            if generated.get(key) != expected:
                diagnostics.append(f"{label} generated metadata mismatch for field `{key}`")
    return diagnostics


def _roadmap_diagnostics(root: Path, current_task: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    frontmatter, _ = read_roadmap(root)
    if frontmatter.get("current_task_id") != current_task["task_id"]:
        diagnostics.append("roadmap current_task_id mismatch")
    if frontmatter.get("current_phase") != current_task["stage"]:
        diagnostics.append("roadmap current_phase mismatch")
    return diagnostics


def _exception_blockers(root: Path) -> list[str]:
    path = root / "docs/governance/exceptions_registry.yaml"
    if not path.exists():
        return []
    document = load_yaml(path) or {}
    blockers: list[str] = []
    for item in document.get("exceptions", []):
        status = str(item.get("status") or "").lower()
        if status in PENDING_EXCEPTION_STATUSES:
            exception_id = item.get("exception_id") or "unknown-exception"
            blockers.append(f"pending exception approval exists: {exception_id}")
    return blockers


def _child_lane_blockers(registry: dict[str, Any], current_task: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    children = [
        task
        for task in registry.get("tasks", [])
        if task.get("parent_task_id") == current_task["task_id"] and task.get("task_kind") == "execution"
    ]
    blocked = [task["task_id"] for task in children if task.get("status") == "blocked"]
    open_children = [task["task_id"] for task in children if task.get("status") != "done"]
    if blocked:
        blockers.append(f"blocked child lanes remain open: {', '.join(blocked)}")
    elif open_children:
        blockers.append(f"open child lanes remain: {', '.join(open_children)}")
    return blockers


def _is_ai_guarded_top_level_task(current_task: dict[str, Any]) -> bool:
    return current_task.get("task_kind") == "coordination" and current_task.get("parent_task_id") is None


def _has_ai_guarded_closeout_marker(root: Path, current_task: dict[str, Any]) -> bool:
    if current_task.get("status") == "review":
        return True
    for path_value in (
        current_task.get("task_file"),
        current_task.get("runlog_file"),
        f"docs/governance/handoffs/{current_task['task_id']}.yaml",
    ):
        if not path_value:
            continue
        path = root / path_value
        if path.exists() and AI_GUARDED_CLOSEOUT_MARKER in read_text(path).lower():
            return True
    return False


def _assessment(
    *,
    status: str,
    task_id: str | None,
    task_status: str,
    eligible: bool,
    summary: str,
    blockers: list[str],
    diagnostics: list[str],
    dirty_state: str = "clean",
    dirty_paths_by_class: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "task_id": task_id,
        "task_status": task_status,
        "eligible": eligible,
        "summary": summary,
        "blockers": blockers,
        "diagnostics": diagnostics,
        "dirty_state": dirty_state,
        "dirty_paths_by_class": dirty_paths_by_class
        or {"governance_paths": [], "task_scoped_paths": [], "unsafe_paths": []},
    }


def _base_closeout_blockers(
    root: Path, current_payload: dict[str, Any], current_task: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    if current_task.get("task_kind") != "coordination" or current_task.get("parent_task_id") is not None:
        _append_unique(blockers, "automatic closeout only supports the live top-level coordination task")
    if current_task["status"] == "blocked":
        reason = current_task.get("blocked_reason") or "blocked without recorded reason"
        _append_unique(blockers, f"current task is blocked: {reason}")
    if current_task["status"] == "done":
        _append_unique(blockers, "CURRENT_TASK.yaml should not remain on a done live task")
    dirty = classify_task_dirty_state(root, current_payload=current_payload, task=current_task)
    unsafe_paths = dirty["dirty_paths_by_class"]["unsafe_paths"]
    if unsafe_paths:
        _append_unique(blockers, f"unsafe dirty paths: {', '.join(unsafe_paths)}")
    return blockers, dirty


def _non_review_assessment(
    current_task: dict[str, Any],
    blockers: list[str],
    diagnostics: list[str],
    dirty: dict[str, Any],
) -> dict[str, Any]:
    if diagnostics:
        return _assessment(
            status="blocked",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary="live ledger drift detected; repair the control-plane state before auto-closeout",
            blockers=["live ledger drift detected"],
            diagnostics=diagnostics,
            dirty_state=dirty["dirty_state"],
            dirty_paths_by_class=dirty["dirty_paths_by_class"],
        )
    if blockers:
        return _assessment(
            status="blocked",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary="the live task cannot enter automatic closeout yet",
            blockers=blockers,
            diagnostics=[],
            dirty_state=dirty["dirty_state"],
            dirty_paths_by_class=dirty["dirty_paths_by_class"],
        )
    return _assessment(
        status="not_applicable",
        task_id=current_task["task_id"],
        task_status=current_task["status"],
        eligible=False,
        summary=f"live task `{current_task['task_id']}` is `{current_task['status']}`; auto-closeout is not applicable",
        blockers=[],
        diagnostics=[],
        dirty_state=dirty["dirty_state"],
        dirty_paths_by_class=dirty["dirty_paths_by_class"],
    )


def _review_assessment(
    root: Path,
    current_task: dict[str, Any],
    blockers: list[str],
    diagnostics: list[str],
    dirty: dict[str, Any],
) -> dict[str, Any]:
    missing = missing_required_tests(root, current_task)
    if missing:
        _append_unique(blockers, f"required tests missing from runlog: {', '.join(missing)}")
    if diagnostics:
        _append_unique(blockers, "live ledger drift detected")
    if blockers:
        return _assessment(
            status="blocked",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary=f"review task `{current_task['task_id']}` is not ready for automatic closeout",
            blockers=blockers,
            diagnostics=diagnostics,
            dirty_state=dirty["dirty_state"],
            dirty_paths_by_class=dirty["dirty_paths_by_class"],
        )
    return _assessment(
        status="ready",
        task_id=current_task["task_id"],
        task_status=current_task["status"],
        eligible=True,
        summary=f"review task `{current_task['task_id']}` is ready for automatic closeout",
        blockers=[],
        diagnostics=[],
        dirty_state=dirty["dirty_state"],
        dirty_paths_by_class=dirty["dirty_paths_by_class"],
    )


def _ai_guarded_top_level_assessment(
    root: Path,
    registry: dict[str, Any],
    current_task: dict[str, Any],
    blockers: list[str],
    diagnostics: list[str],
    dirty: dict[str, Any],
) -> dict[str, Any]:
    if current_task["status"] not in {"doing", "review"}:
        return _assessment(
            status="not_applicable",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary=f"live task `{current_task['task_id']}` is `{current_task['status']}`; ai_guarded closeout is not applicable",
            blockers=[],
            diagnostics=diagnostics,
            dirty_state=dirty["dirty_state"],
            dirty_paths_by_class=dirty["dirty_paths_by_class"],
        )

    diagnostics.extend(_roadmap_diagnostics(root, current_task))
    diagnostics.extend(_artifact_diagnostics(root, current_task))

    if not _has_ai_guarded_closeout_marker(root, current_task):
        if diagnostics:
            return _assessment(
                status="blocked",
                task_id=current_task["task_id"],
                task_status=current_task["status"],
                eligible=False,
                summary="top-level task has control-plane drift and cannot be evaluated for ai_guarded closeout",
                blockers=["live ledger drift detected"],
                diagnostics=diagnostics,
                dirty_state=dirty["dirty_state"],
                dirty_paths_by_class=dirty["dirty_paths_by_class"],
            )
        return _assessment(
            status="not_applicable",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary=f"live task `{current_task['task_id']}` is still active work; ai_guarded closeout evidence is not recorded yet",
            blockers=[],
            diagnostics=[],
            dirty_state=dirty["dirty_state"],
            dirty_paths_by_class=dirty["dirty_paths_by_class"],
        )

    blockers.extend(_child_lane_blockers(registry, current_task))
    blockers.extend(_exception_blockers(root))
    missing = missing_required_tests(root, current_task)
    if missing:
        blockers.append(f"required tests missing from runlog: {', '.join(missing)}")
    if diagnostics:
        blockers.append("live ledger drift detected")
    if blockers:
        return _assessment(
            status="blocked",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary=f"top-level task `{current_task['task_id']}` is not ready for ai_guarded closeout",
            blockers=list(dict.fromkeys(blockers)),
            diagnostics=diagnostics,
            dirty_state=dirty["dirty_state"],
            dirty_paths_by_class=dirty["dirty_paths_by_class"],
        )
    return _assessment(
        status="ready",
        task_id=current_task["task_id"],
        task_status=current_task["status"],
        eligible=True,
        summary=f"top-level task `{current_task['task_id']}` is ready for ai_guarded closeout",
        blockers=[],
        diagnostics=[],
        dirty_state=dirty["dirty_state"],
        dirty_paths_by_class=dirty["dirty_paths_by_class"],
    )


def assess_live_closeout(
    root: Path,
    *,
    registry: dict[str, Any] | None = None,
    worktrees: dict[str, Any] | None = None,
    current_payload: dict[str, Any] | None = None,
    current_task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or load_task_registry(root)
    worktrees = worktrees or load_worktree_registry(root)
    current_payload = current_payload or load_current_task(root)
    if current_task is None and not is_idle_current_payload(current_payload):
        current_task = find_task(registry.get("tasks", []), current_payload["current_task_id"])

    if is_idle_current_payload(current_payload) or current_task is None:
        return _assessment(
            status="not_applicable",
            task_id=None,
            task_status="idle",
            eligible=False,
            summary="there is no live coordination task to close out",
            blockers=[],
            diagnostics=[],
        )

    diagnostics = _payload_diagnostics(current_payload, current_task)
    diagnostics.extend(_worktree_diagnostics(root, current_task, worktrees))
    blockers, dirty = _base_closeout_blockers(root, current_payload, current_task)

    if _is_ai_guarded_top_level_task(current_task):
        return _ai_guarded_top_level_assessment(root, registry, current_task, blockers, diagnostics, dirty)

    if current_task["status"] != "review":
        return _non_review_assessment(current_task, blockers, diagnostics, dirty)
    return _review_assessment(root, current_task, blockers, diagnostics, dirty)
