from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from governance_runtime import GovernanceError, iso_now, read_text, write_text


TASK_MARKER_START = "<!-- generated:task-meta:start -->"
TASK_MARKER_END = "<!-- generated:task-meta:end -->"
RUNLOG_MARKER_START = "<!-- generated:runlog-meta:start -->"
RUNLOG_MARKER_END = "<!-- generated:runlog-meta:end -->"
TASK_BASELINE_HEADING = "## Task Baseline"
RUNLOG_STATUS_HEADING = "## Task Status"
NARRATIVE_ASSERTIONS_HEADING = "## Narrative Assertions"
NARRATIVE_ASSERTION_FIELDS = (
    "narrative_status",
    "closeout_state",
    "blocking_state",
    "completed_scope",
    "remaining_scope",
    "next_gate",
)
STATUS_NARRATIVE_RULES = {
    "queued": {"closeout_state": "not_ready", "completed_scope": "not_started", "remaining_scope": "active_work_remaining", "next_gate": "activation_pending"},
    "doing": {"closeout_state": "not_ready", "completed_scope": "active_progress", "remaining_scope": "active_work_remaining", "next_gate": "validation_pending"},
    "paused": {"closeout_state": "not_ready", "completed_scope": "active_progress", "remaining_scope": "active_work_remaining", "next_gate": "resume_required"},
    "blocked": {"closeout_state": "not_ready", "completed_scope": "active_progress", "remaining_scope": "blocked_work_remaining", "next_gate": "blocking_resolution"},
    "review": {"closeout_state": "candidate_ready", "completed_scope": "ready_for_review", "remaining_scope": "closeout_only", "next_gate": "closeout_decision"},
    "done": {"closeout_state": "closed", "completed_scope": "closed", "remaining_scope": "none", "next_gate": "closed"},
}
TASK_PACKAGE_REQUIRED_SECTIONS = (
    "## Primary Goals",
    "## Explicitly Not Doing",
    "## Allowed Dirs",
    "## Required Tests",
    "## Acceptance Criteria",
    "## Rollback",
)
TASK_PACKAGE_PLACEHOLDERS = ("to-be-filled", "to be filled", "tbd", "todo", "null")


def extract_markdown_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for key, value in re.findall(r"-\s+`([^`]+)`:\s+`([^`]*)`", text):
        fields.setdefault(key, value)
    return fields


def extract_generated_fields(text: str, start_marker: str, end_marker: str) -> dict[str, str]:
    pattern = re.compile(re.escape(start_marker) + r"\n(.*?)\n" + re.escape(end_marker), re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise GovernanceError(f"missing generated block: {start_marker}")
    return extract_markdown_fields(match.group(1))


def extract_section_body(text: str, heading: str) -> str:
    pattern = re.compile(rf"{re.escape(heading)}\n\n(.*?)(?=\n## |\n<!-- |\Z)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise GovernanceError(f"missing section: {heading}")
    return match.group(1).rstrip()


def find_section_body(text: str, heading: str) -> str | None:
    pattern = re.compile(rf"{re.escape(heading)}\n\n(.*?)(?=\n## |\n<!-- |\Z)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).rstrip()


def _normalize_section_lines(body: str) -> list[str]:
    return [line.strip() for line in body.splitlines() if line.strip()]


def section_has_placeholder(body: str) -> bool:
    lines = _normalize_section_lines(body)
    if not lines:
        return True
    normalized = [line.lstrip("-* ").strip() for line in lines]
    for line in normalized:
        lowered = line.lower()
        if any(token in lowered for token in TASK_PACKAGE_PLACEHOLDERS):
            return True
    return False


def task_package_gaps(text: str, *, required_sections: tuple[str, ...] = TASK_PACKAGE_REQUIRED_SECTIONS) -> dict[str, list[str]]:
    missing: list[str] = []
    placeholder: list[str] = []
    for heading in required_sections:
        body = find_section_body(text, heading)
        if body is None:
            missing.append(heading.replace("## ", ""))
            continue
        if section_has_placeholder(body):
            placeholder.append(heading.replace("## ", ""))
    return {"missing": missing, "placeholder": placeholder}


def _render_bullets(items: list[str], *, wrap_backticks: bool = False) -> str:
    if not items:
        return ""
    if wrap_backticks:
        return "\n".join(f"- `{item}`" for item in items)
    return "\n".join(f"- {item}" for item in items)


def _autofill_primary_goals(task: dict[str, Any], candidate: dict[str, Any] | None) -> list[str]:
    lines = [f"Deliver `{task['task_id']}`: {task['title']} for stage `{task.get('stage')}`."]
    if candidate and candidate.get("candidate_id"):
        lines.append(f"Execute roadmap candidate `{candidate['candidate_id']}`.")
    planned_paths = list(task.get("planned_write_paths") or [])
    if planned_paths:
        lines.append(f"Implement planned write paths: {', '.join(planned_paths)}.")
    required_tests = list(task.get("required_tests") or [])
    if required_tests:
        lines.append(f"Keep required tests passing: {', '.join(required_tests)}.")
    depends_on = list((candidate or {}).get("depends_on") or [])
    if depends_on:
        lines.append(f"Confirm dependencies complete: {', '.join(depends_on)}.")
    return lines


def _autofill_explicitly_not_doing(task: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    reserved = list(task.get("reserved_paths") or [])
    if reserved:
        lines.append(f"Do not touch reserved paths: {', '.join(reserved)}.")
    allowed_dirs = list(task.get("allowed_dirs") or [])
    if allowed_dirs:
        lines.append(f"Do not modify files outside allowed dirs: {', '.join(allowed_dirs)}.")
    planned_paths = list(task.get("planned_write_paths") or [])
    if planned_paths:
        lines.append(f"Do not expand scope outside planned write paths: {', '.join(planned_paths)}.")
    if not lines:
        lines.append("Do not expand scope beyond the declared task boundaries.")
    return lines


def _autofill_acceptance_criteria(task: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    required_tests = list(task.get("required_tests") or [])
    if required_tests:
        lines.append(f"Required tests pass: {', '.join(required_tests)}.")
    planned_paths = list(task.get("planned_write_paths") or [])
    if planned_paths:
        lines.append(f"Changes limited to planned write paths: {', '.join(planned_paths)}.")
    lines.append("No open blockers remain at closeout.")
    return lines


def _autofill_rollback(task: dict[str, Any]) -> list[str]:
    branch = task.get("branch") or "current branch"
    return [
        f"Revert branch `{branch}` to the last known good commit if needed.",
        "Remove or reset generated artifacts before re-dispatching the task.",
    ]


def autofill_task_package(text: str, task: dict[str, Any], *, candidate: dict[str, Any] | None = None) -> str:
    updates = {
        "## Primary Goals": _autofill_primary_goals(task, candidate),
        "## Explicitly Not Doing": _autofill_explicitly_not_doing(task),
        "## Allowed Dirs": list(task.get("allowed_dirs") or []),
        "## Required Tests": list(task.get("required_tests") or []),
        "## Acceptance Criteria": _autofill_acceptance_criteria(task),
        "## Rollback": _autofill_rollback(task),
    }
    updated = text
    for heading, lines in updates.items():
        body = find_section_body(updated, heading)
        if body is not None and not section_has_placeholder(body):
            continue
        if heading in {"## Allowed Dirs", "## Required Tests"}:
            rendered = _render_bullets(lines, wrap_backticks=True)
        else:
            rendered = _render_bullets(lines, wrap_backticks=False)
        if not rendered:
            continue
        updated = sync_named_section(updated, heading, rendered)
    return updated


def extract_narrative_assertions(text: str) -> dict[str, str]:
    fields = extract_markdown_fields(extract_section_body(text, NARRATIVE_ASSERTIONS_HEADING))
    missing = [field for field in NARRATIVE_ASSERTION_FIELDS if field not in fields]
    if missing:
        raise GovernanceError(f"missing narrative assertions fields: {', '.join(missing)}")
    return fields


def sync_generated_block(text: str, start_marker: str, end_marker: str, block: str) -> str:
    rendered = f"{start_marker}\n{block.rstrip()}\n{end_marker}"
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(rendered, text)
    suffix = "\n\n" if text.rstrip() else ""
    return f"{text.rstrip()}{suffix}{rendered}\n"


def sync_named_section(text: str, heading: str, body: str) -> str:
    rendered = f"{heading}\n\n{body.rstrip()}"
    pattern = re.compile(rf"{re.escape(heading)}\n\n.*?(?=\n## |\n<!-- |\Z)", re.DOTALL)
    if pattern.search(text):
        return pattern.sub(rendered, text)
    suffix = "\n\n" if text.rstrip() else ""
    return f"{text.rstrip()}{suffix}{rendered}\n"


def expected_narrative_assertions(task: dict[str, Any]) -> dict[str, str]:
    status = task["status"]
    if status not in STATUS_NARRATIVE_RULES:
        raise GovernanceError(f"unsupported task status for narrative assertions: {status}")
    rules = STATUS_NARRATIVE_RULES[status]
    blocking_state = "blocked" if status == "blocked" or task.get("worker_state") == "blocked" or task.get("blocked_reason") else "clear"
    return {
        "narrative_status": status,
        "closeout_state": rules["closeout_state"],
        "blocking_state": blocking_state,
        "completed_scope": rules["completed_scope"],
        "remaining_scope": rules["remaining_scope"],
        "next_gate": rules["next_gate"],
    }


def render_narrative_assertions_block(task: dict[str, Any]) -> str:
    assertions = expected_narrative_assertions(task)
    return "\n".join(f"- `{field}`: `{assertions[field]}`" for field in NARRATIVE_ASSERTION_FIELDS)


def _markdown_scalar(value: Any) -> str:
    return "null" if value is None else str(value)


def render_task_metadata_block(task: dict[str, Any]) -> str:
    lines = [
        "## Generated Metadata",
        "",
        f"- `status`: `{task['status']}`",
        f"- `task_kind`: `{task['task_kind']}`",
        f"- `execution_mode`: `{task['execution_mode']}`",
        f"- `size_class`: `{task['size_class']}`",
        f"- `automation_mode`: `{task['automation_mode']}`",
        f"- `worker_state`: `{task['worker_state']}`",
        f"- `topology`: `{task['topology']}`",
        f"- `lane_count`: `{_markdown_scalar(task.get('lane_count', 1))}`",
        f"- `lane_index`: `{_markdown_scalar(task.get('lane_index'))}`",
        f"- `parallelism_plan_id`: `{_markdown_scalar(task.get('parallelism_plan_id'))}`",
        f"- `review_bundle_status`: `{_markdown_scalar(task.get('review_bundle_status', 'not_applicable'))}`",
        f"- `reserved_paths`: `{', '.join(task.get('reserved_paths', [])) or '[]'}`",
        f"- `branch`: `{task['branch']}`",
        f"- `updated_at`: `{iso_now()}`",
    ]
    if task.get("task_kind") == "coordination" and task.get("parent_task_id") is None:
        lines.insert(13, f"- `successor_state`: `{task.get('successor_state') or 'immediate'}`")
    return "\n".join(lines)


def render_task_baseline_section(task: dict[str, Any]) -> str:
    lines = [
        f"- `task_id`: `{task['task_id']}`",
        f"- `task_kind`: `{task['task_kind']}`",
        f"- `execution_mode`: `{task['execution_mode']}`",
        f"- `status`: `{task['status']}`",
        f"- `stage`: `{task['stage']}`",
        f"- `branch`: `{task['branch']}`",
        f"- `size_class`: `{task['size_class']}`",
        f"- `automation_mode`: `{task['automation_mode']}`",
        f"- `worker_state`: `{task['worker_state']}`",
        f"- `topology`: `{task['topology']}`",
        f"- `lane_count`: `{_markdown_scalar(task.get('lane_count', 1))}`",
        f"- `lane_index`: `{_markdown_scalar(task.get('lane_index'))}`",
        f"- `parallelism_plan_id`: `{_markdown_scalar(task.get('parallelism_plan_id'))}`",
        f"- `review_bundle_status`: `{_markdown_scalar(task.get('review_bundle_status', 'not_applicable'))}`",
    ]
    if task.get("task_kind") == "coordination" and task.get("parent_task_id") is None:
        lines.append(f"- `successor_state`: `{task.get('successor_state') or 'immediate'}`")
    return "\n".join(lines)


def render_runlog_metadata_block(task: dict[str, Any]) -> str:
    lines = [
        "## Generated Task Snapshot",
        "",
        f"- `task_id`: `{task['task_id']}`",
        f"- `status`: `{task['status']}`",
        f"- `stage`: `{task['stage']}`",
        f"- `branch`: `{task['branch']}`",
        f"- `worker_state`: `{task['worker_state']}`",
        f"- `lane_count`: `{_markdown_scalar(task.get('lane_count', 1))}`",
        f"- `lane_index`: `{_markdown_scalar(task.get('lane_index'))}`",
        f"- `parallelism_plan_id`: `{_markdown_scalar(task.get('parallelism_plan_id'))}`",
        f"- `review_bundle_status`: `{_markdown_scalar(task.get('review_bundle_status', 'not_applicable'))}`",
    ]
    return "\n".join(lines)


def render_runlog_status_section(task: dict[str, Any]) -> str:
    lines = [
        f"- `task_id`: `{task['task_id']}`",
        f"- `status`: `{task['status']}`",
        f"- `stage`: `{task['stage']}`",
        f"- `branch`: `{task['branch']}`",
        f"- `worker_state`: `{task['worker_state']}`",
        f"- `lane_count`: `{_markdown_scalar(task.get('lane_count', 1))}`",
        f"- `lane_index`: `{_markdown_scalar(task.get('lane_index'))}`",
        f"- `parallelism_plan_id`: `{_markdown_scalar(task.get('parallelism_plan_id'))}`",
        f"- `review_bundle_status`: `{_markdown_scalar(task.get('review_bundle_status', 'not_applicable'))}`",
    ]
    return "\n".join(lines)


def sync_task_artifacts(root: Path, registry: dict[str, Any], task_ids: list[str] | None = None) -> None:
    allowed_ids = set(task_ids or [])
    for task in registry.get("tasks", []):
        if allowed_ids and task["task_id"] not in allowed_ids:
            continue
        task_path = root / task["task_file"]
        runlog_path = root / task["runlog_file"]
        if task_path.exists():
            write_text(
                task_path,
                sync_generated_block(
                    sync_named_section(
                        sync_named_section(read_text(task_path), TASK_BASELINE_HEADING, render_task_baseline_section(task)),
                        NARRATIVE_ASSERTIONS_HEADING,
                        render_narrative_assertions_block(task),
                    ),
                    TASK_MARKER_START,
                    TASK_MARKER_END,
                    render_task_metadata_block(task),
                ),
            )
        if runlog_path.exists():
            write_text(
                runlog_path,
                sync_generated_block(
                    sync_named_section(
                        sync_named_section(read_text(runlog_path), RUNLOG_STATUS_HEADING, render_runlog_status_section(task)),
                        NARRATIVE_ASSERTIONS_HEADING,
                        render_narrative_assertions_block(task),
                    ),
                    RUNLOG_MARKER_START,
                    RUNLOG_MARKER_END,
                    render_runlog_metadata_block(task),
                ),
            )


def insert_bullets_under_section(text: str, section: str, bullets: list[str]) -> str:
    if not bullets:
        return text
    heading = f"## {section}"
    rendered = "\n".join(f"- {bullet}" for bullet in bullets).rstrip()
    if heading not in text:
        suffix = "\n\n" if text.rstrip() else ""
        return f"{text.rstrip()}{suffix}{heading}\n\n{rendered}\n"
    pattern = re.compile(rf"({re.escape(heading)}\n\n)(.*?)(\n## |\n<!-- |\Z)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        return f"{text.rstrip()}\n\n{heading}\n\n{rendered}\n"
    existing = match.group(2).rstrip()
    replacement = f"{match.group(1)}{existing}\n{rendered}{match.group(3)}"
    return text[: match.start()] + replacement + text[match.end() :]


def append_runlog_bullets(root: Path, task: dict[str, Any], section: str, bullets: list[str]) -> None:
    path = root / task["runlog_file"]
    text = read_text(path) if path.exists() else f"# {task['task_id']} RUNLOG\n"
    write_text(path, insert_bullets_under_section(text, section, bullets))
