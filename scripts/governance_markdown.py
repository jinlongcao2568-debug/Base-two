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
        f"- `reserved_paths`: `{', '.join(task.get('reserved_paths', [])) or '[]'}`",
        f"- `branch`: `{task['branch']}`",
        f"- `updated_at`: `{iso_now()}`",
    ]
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
    ]
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
    ]
    return "\n".join(lines)


def render_runlog_status_section(task: dict[str, Any]) -> str:
    lines = [
        f"- `task_id`: `{task['task_id']}`",
        f"- `status`: `{task['status']}`",
        f"- `stage`: `{task['stage']}`",
        f"- `branch`: `{task['branch']}`",
        f"- `worker_state`: `{task['worker_state']}`",
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
