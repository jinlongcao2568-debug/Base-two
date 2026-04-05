from __future__ import annotations

from pathlib import Path
from typing import Any

from governance_lib import GovernanceError, dump_yaml, iso_now, read_text
from governance_markdown import extract_section_body
from governance_runtime import load_yaml


HANDOFF_POLICY_FILE = Path("docs/governance/HANDOFF_POLICY.yaml")
HANDOFFS_DIR = Path("docs/governance/handoffs")
HANDOFF_REQUIRED_FIELDS = (
    "task_id",
    "summary_status",
    "last_handoff_at",
    "completed_items",
    "remaining_items",
    "next_step",
    "next_tests",
    "current_risks",
    "candidate_write_paths",
    "candidate_test_paths",
    "resume_notes",
)


def is_top_level_coordination_task(task: dict[str, Any]) -> bool:
    return task.get("task_kind") == "coordination" and task.get("parent_task_id") is None


def handoff_path(root: Path, task_id: str) -> Path:
    return root / HANDOFFS_DIR / f"{task_id}.yaml"


def load_handoff_policy(root: Path) -> dict[str, Any]:
    path = root / HANDOFF_POLICY_FILE
    if not path.exists():
        raise GovernanceError(f"handoff policy missing: {HANDOFF_POLICY_FILE}")
    return load_yaml(path) or {}


def _dedupe(items: list[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _default_next_step(task: dict[str, Any]) -> str:
    status = task.get("status")
    if status == "queued":
        return "Activate the task and begin scoped implementation inside the allowed directories."
    if status == "doing":
        return "Continue the scoped implementation and keep the control plane aligned."
    if status == "paused":
        return "Reactivate the task before making further changes."
    if status == "blocked":
        return "Resolve the recorded blocker before continuing the task."
    if status == "review":
        return "Validate the required tests and close the review-ready task if it is eligible."
    return "No further action is required; the task is closed."


def _default_remaining_items(task: dict[str, Any]) -> list[str]:
    status = task.get("status")
    if status == "done":
        return []
    if status == "review":
        return ["Close the task after validating the review-ready evidence."]
    if status == "blocked":
        return ["Resolve the active blocker and resume the scoped work."]
    return ["Complete the remaining scoped implementation for this task."]


def default_handoff_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task["task_id"],
        "summary_status": task["status"],
        "last_handoff_at": None,
        "completed_items": [],
        "remaining_items": _default_remaining_items(task),
        "next_step": _default_next_step(task),
        "next_tests": list(task.get("required_tests") or []),
        "current_risks": [],
        "candidate_write_paths": list(task.get("planned_write_paths") or []),
        "candidate_test_paths": list(task.get("planned_test_paths") or []),
        "resume_notes": ["Formal handoff has not been recorded yet."],
    }


def _merge_handoff(task: dict[str, Any], payload: dict[str, Any] | None) -> dict[str, Any]:
    merged = default_handoff_payload(task)
    payload = payload or {}
    for field in HANDOFF_REQUIRED_FIELDS:
        if field not in payload:
            continue
        value = payload[field]
        if field in {
            "completed_items",
            "remaining_items",
            "next_tests",
            "current_risks",
            "candidate_write_paths",
            "candidate_test_paths",
            "resume_notes",
        }:
            merged[field] = _dedupe(list(value or []))
        else:
            merged[field] = value
    merged["task_id"] = task["task_id"]
    return merged


def ensure_handoff_file(root: Path, task: dict[str, Any]) -> Path | None:
    if not is_top_level_coordination_task(task):
        return None
    load_handoff_policy(root)
    path = handoff_path(root, task["task_id"])
    if not path.exists():
        dump_yaml(path, default_handoff_payload(task))
    return path


def load_handoff(root: Path, task: dict[str, Any]) -> dict[str, Any] | None:
    if not is_top_level_coordination_task(task):
        return None
    path = handoff_path(root, task["task_id"])
    if not path.exists():
        return None
    return _merge_handoff(task, load_yaml(path) or {})


def write_handoff(
    root: Path,
    task: dict[str, Any],
    *,
    summary_status: str | None = None,
    completed_items: list[str] | None = None,
    remaining_items: list[str] | None = None,
    next_step: str | None = None,
    next_tests: list[str] | None = None,
    current_risks: list[str] | None = None,
    candidate_write_paths: list[str] | None = None,
    candidate_test_paths: list[str] | None = None,
    resume_notes: list[str] | None = None,
    append_resume_notes: bool = False,
) -> Path | None:
    if not is_top_level_coordination_task(task):
        return None
    ensure_handoff_file(root, task)
    current = load_handoff(root, task) or default_handoff_payload(task)
    current["summary_status"] = summary_status or task["status"]
    current["last_handoff_at"] = iso_now()
    if completed_items is not None:
        current["completed_items"] = _dedupe(completed_items)
    if remaining_items is not None:
        current["remaining_items"] = _dedupe(remaining_items)
    if next_step is not None:
        current["next_step"] = next_step
    if next_tests is not None:
        current["next_tests"] = _dedupe(next_tests)
    if current_risks is not None:
        current["current_risks"] = _dedupe(current_risks)
    if candidate_write_paths is not None:
        current["candidate_write_paths"] = _dedupe(candidate_write_paths)
    if candidate_test_paths is not None:
        current["candidate_test_paths"] = _dedupe(candidate_test_paths)
    if resume_notes is not None:
        if append_resume_notes:
            current["resume_notes"] = _dedupe([*current.get("resume_notes", []), *resume_notes])
        else:
            current["resume_notes"] = _dedupe(resume_notes)
    path = handoff_path(root, task["task_id"])
    dump_yaml(path, current)
    return path


def _section_bullets(text: str, heading: str) -> list[str]:
    try:
        body = extract_section_body(text, heading)
    except GovernanceError:
        return []
    items: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        value = stripped[2:].strip()
        if value.startswith("`") and value.endswith("`"):
            value = value[1:-1]
        items.append(value)
    return items


def build_recovery_pack(root: Path, task: dict[str, Any]) -> tuple[dict[str, Any], str, list[str]]:
    formal = load_handoff(root, task)
    if formal is not None:
        return formal, "formal_handoff", []

    runlog_path = root / task["runlog_file"]
    warnings = ["formal handoff missing; using fallback recovery synthesized from task/runlog."]
    runlog_text = read_text(runlog_path) if runlog_path.exists() else ""
    completed_items = _section_bullets(runlog_text, "## Execution Log")
    current_risks = _section_bullets(runlog_text, "## Risk and Blockers")
    fallback = default_handoff_payload(task)
    fallback["summary_status"] = "fallback_from_task_runlog"
    fallback["completed_items"] = completed_items or fallback["completed_items"]
    fallback["current_risks"] = current_risks
    fallback["resume_notes"] = _dedupe(
        [
            "Formal handoff artifact is missing.",
            f"Fallback synthesized from `{task['task_file']}` and `{task['runlog_file']}`.",
        ]
    )
    return fallback, "task_runlog_fallback", warnings


def render_recovery_lines(pack: dict[str, Any], source: str, warnings: list[str]) -> list[str]:
    lines = [f"[RECOVERY] source={source} summary_status={pack['summary_status']}"]
    for warning in warnings:
        lines.append(f"[RECOVERY] warning={warning}")
    if pack.get("completed_items"):
        lines.append(f"[RECOVERY] completed={'; '.join(pack['completed_items'])}")
    if pack.get("remaining_items"):
        lines.append(f"[RECOVERY] remaining={'; '.join(pack['remaining_items'])}")
    if pack.get("next_step"):
        lines.append(f"[RECOVERY] next_step={pack['next_step']}")
    if pack.get("next_tests"):
        lines.append(f"[RECOVERY] next_tests={'; '.join(pack['next_tests'])}")
    if pack.get("current_risks"):
        lines.append(f"[RECOVERY] risks={'; '.join(pack['current_risks'])}")
    if pack.get("candidate_write_paths"):
        lines.append(f"[RECOVERY] candidate_write_paths={'; '.join(pack['candidate_write_paths'])}")
    if pack.get("candidate_test_paths"):
        lines.append(f"[RECOVERY] candidate_test_paths={'; '.join(pack['candidate_test_paths'])}")
    return lines
