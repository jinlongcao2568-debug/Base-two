from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from governance_lib import (
    GovernanceError,
    configure_utf8_stdio,
    dump_yaml,
    find_repo_root,
    iso_now,
    load_task_registry,
    load_yaml,
)


ROADMAP_BACKLOG_FILE = Path("docs/governance/ROADMAP_BACKLOG.yaml")
ROADMAP_CANDIDATES_FILE = Path(".codex/local/roadmap_candidates/index.yaml")
ROADMAP_BACKLOG_SCHEMA_FILE = Path("docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml")

CONTROLLED_STATUSES = {"claimed", "running", "stale", "resumable", "blocked", "review", "done", "closed"}
TERMINAL_STATUSES = {"done", "closed"}
INDEX_STATUS_ORDER = {
    "ready": 0,
    "resumable": 1,
    "stale": 2,
    "waiting": 3,
    "claimed": 4,
    "running": 5,
    "blocked": 6,
    "review": 7,
    "done": 8,
    "closed": 9,
}


def _required_list(schema: dict[str, Any], key: str) -> set[str]:
    values = schema.get(key) or []
    if not isinstance(values, list):
        raise GovernanceError(f"schema field must be a list: {key}")
    return {str(value) for value in values}


def _load_backlog(root: Path) -> dict[str, Any]:
    path = root / ROADMAP_BACKLOG_FILE
    if not path.exists():
        raise GovernanceError(f"roadmap backlog missing: {ROADMAP_BACKLOG_FILE}")
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError("roadmap backlog must be a mapping")
    return payload


def _load_schema(root: Path) -> dict[str, Any]:
    path = root / ROADMAP_BACKLOG_SCHEMA_FILE
    if not path.exists():
        raise GovernanceError(f"roadmap backlog schema missing: {ROADMAP_BACKLOG_SCHEMA_FILE}")
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError("roadmap backlog schema must be a mapping")
    return payload


def _validate_backlog_shape(backlog: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    missing_top = sorted(_required_list(schema, "required_top_level_fields") - set(backlog))
    if missing_top:
        raise GovernanceError(f"roadmap backlog missing top-level fields: {', '.join(missing_top)}")

    candidates = backlog.get("candidates") or []
    if not isinstance(candidates, list):
        raise GovernanceError("roadmap backlog field `candidates` must be a list")
    if not candidates:
        raise GovernanceError("roadmap backlog has no candidates")

    allowed_lane_types = set((schema.get("lane_types") or {}).keys())
    allowed_statuses = set(schema.get("candidate_status_values") or [])
    required_candidate_fields = _required_list(schema, "required_candidate_fields")

    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise GovernanceError("roadmap backlog candidate must be a mapping")
        candidate_id = str(candidate.get("candidate_id") or "")
        if not candidate_id:
            raise GovernanceError("roadmap backlog candidate missing candidate_id")
        if candidate_id in seen:
            raise GovernanceError(f"duplicate roadmap candidate_id: {candidate_id}")
        seen.add(candidate_id)

        missing = sorted(required_candidate_fields - set(candidate))
        if missing:
            raise GovernanceError(f"roadmap candidate {candidate_id} missing fields: {', '.join(missing)}")

        lane_type = candidate.get("lane_type")
        if lane_type not in allowed_lane_types:
            raise GovernanceError(f"roadmap candidate {candidate_id} has invalid lane_type: {lane_type}")
        status = candidate.get("status")
        if status not in allowed_statuses:
            raise GovernanceError(f"roadmap candidate {candidate_id} has invalid status: {status}")
        if not isinstance(candidate.get("priority"), int):
            raise GovernanceError(f"roadmap candidate {candidate_id} priority must be an integer")
        for field in (
            "depends_on",
            "unlocks",
            "allowed_dirs",
            "reserved_paths",
            "planned_write_paths",
            "planned_test_paths",
            "required_tests",
        ):
            if not isinstance(candidate.get(field), list):
                raise GovernanceError(f"roadmap candidate {candidate_id} field `{field}` must be a list")

    _validate_candidate_refs(candidates)
    return candidates


def _validate_candidate_refs(candidates: list[dict[str, Any]]) -> None:
    candidate_ids = {candidate["candidate_id"] for candidate in candidates}
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        refs = list(candidate.get("depends_on") or []) + list(candidate.get("unlocks") or [])
        integration_gate = candidate.get("integration_gate")
        if integration_gate:
            refs.append(integration_gate)
        unresolved = [
            str(ref)
            for ref in refs
            if str(ref).startswith("stage") and str(ref) not in candidate_ids and not str(ref).startswith("TASK-")
        ]
        if unresolved:
            raise GovernanceError(
                f"roadmap candidate {candidate_id} references unknown candidate(s): {', '.join(sorted(set(unresolved)))}"
            )


def _task_registry_by_id(root: Path) -> dict[str, dict[str, Any]]:
    registry = load_task_registry(root)
    return {str(task["task_id"]): task for task in registry.get("tasks", [])}


def _candidate_task_id(candidate_id: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", candidate_id.upper()).strip("-")
    return f"TASK-RM-{token}"


def _format_template(template: str, *, candidate: dict[str, Any], task_id: str) -> str:
    try:
        return template.format(
            task_id=task_id,
            candidate_id=candidate["candidate_id"],
            stage=candidate["stage"],
            module_id=candidate["module_id"],
            lane_type=candidate["lane_type"],
        )
    except KeyError as error:
        raise GovernanceError(
            f"roadmap candidate {candidate['candidate_id']} template references unsupported field: {error}"
        ) from error


def _dependency_status(
    candidate: dict[str, Any],
    *,
    candidates_by_id: dict[str, dict[str, Any]],
    tasks_by_id: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    details: list[dict[str, Any]] = []
    wait_reasons: list[str] = []
    for dependency_id in candidate.get("depends_on") or []:
        dependency_id = str(dependency_id)
        if dependency_id in candidates_by_id:
            dependency = candidates_by_id[dependency_id]
            dependency_status = str(dependency.get("status"))
            satisfied = dependency_status in TERMINAL_STATUSES
            source_kind = "candidate"
        elif dependency_id in tasks_by_id:
            dependency = tasks_by_id[dependency_id]
            dependency_status = str(dependency.get("status"))
            satisfied = dependency_status == "done"
            source_kind = "task"
        elif dependency_id.startswith("TASK-"):
            dependency_status = "missing"
            satisfied = False
            source_kind = "task"
        else:
            dependency_status = "missing"
            satisfied = False
            source_kind = "candidate"
        if not satisfied:
            wait_reasons.append(f"waiting for {dependency_id} ({dependency_status})")
        details.append(
            {
                "dependency_id": dependency_id,
                "source_kind": source_kind,
                "status": dependency_status,
                "satisfied": satisfied,
            }
        )
    return details, wait_reasons


def _derive_status(candidate: dict[str, Any], wait_reasons: list[str]) -> str:
    declared_status = str(candidate.get("status"))
    if declared_status in CONTROLLED_STATUSES:
        return declared_status
    if wait_reasons:
        return "waiting"
    return "ready"


def _indexed_candidate(
    candidate: dict[str, Any],
    *,
    candidates_by_id: dict[str, dict[str, Any]],
    tasks_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    dependency_details, wait_reasons = _dependency_status(
        candidate,
        candidates_by_id=candidates_by_id,
        tasks_by_id=tasks_by_id,
    )
    status = _derive_status(candidate, wait_reasons)
    task_id = _candidate_task_id(candidate["candidate_id"])
    branch = _format_template(str(candidate["branch_template"]), candidate=candidate, task_id=task_id)
    worktree = _format_template(str(candidate["worktree_template"]), candidate=candidate, task_id=task_id)
    return {
        "candidate_id": candidate["candidate_id"],
        "task_id_hint": task_id,
        "title": candidate["title"],
        "stage": candidate["stage"],
        "module_id": candidate["module_id"],
        "lane_type": candidate["lane_type"],
        "declared_status": candidate["status"],
        "status": status,
        "priority": candidate["priority"],
        "rank": None,
        "wait_reasons": wait_reasons,
        "dependency_status": dependency_details,
        "depends_on": list(candidate.get("depends_on") or []),
        "unlocks": list(candidate.get("unlocks") or []),
        "allowed_dirs": list(candidate.get("allowed_dirs") or []),
        "reserved_paths": list(candidate.get("reserved_paths") or []),
        "planned_write_paths": list(candidate.get("planned_write_paths") or []),
        "planned_test_paths": list(candidate.get("planned_test_paths") or []),
        "required_tests": list(candidate.get("required_tests") or []),
        "branch_template": candidate["branch_template"],
        "worktree_template": candidate["worktree_template"],
        "candidate_branch": branch,
        "candidate_worktree": worktree,
        "integration_gate": candidate.get("integration_gate"),
        "claim_policy": dict(candidate.get("claim_policy") or {}),
        "takeover_policy": dict(candidate.get("takeover_policy") or {}),
    }


def build_roadmap_candidate_index(root: Path) -> dict[str, Any]:
    backlog = _load_backlog(root)
    schema = _load_schema(root)
    candidates = _validate_backlog_shape(backlog, schema)
    candidates_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
    tasks_by_id = _task_registry_by_id(root)

    indexed = [
        _indexed_candidate(candidate, candidates_by_id=candidates_by_id, tasks_by_id=tasks_by_id)
        for candidate in candidates
    ]
    indexed.sort(key=lambda item: (INDEX_STATUS_ORDER.get(item["status"], 99), item["priority"], item["candidate_id"]))
    for rank, item in enumerate(indexed, start=1):
        item["rank"] = rank

    status_counts: dict[str, int] = {}
    for item in indexed:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    return {
        "version": "0.1",
        "generated_at": iso_now(),
        "source": str(ROADMAP_BACKLOG_FILE).replace("\\", "/"),
        "schema_source": str(ROADMAP_BACKLOG_SCHEMA_FILE).replace("\\", "/"),
        "candidate_count": len(indexed),
        "status_counts": status_counts,
        "candidate_ids": [item["candidate_id"] for item in indexed],
        "ready_candidate_ids": [item["candidate_id"] for item in indexed if item["status"] == "ready"],
        "waiting_candidate_ids": [item["candidate_id"] for item in indexed if item["status"] == "waiting"],
        "candidates": indexed,
    }


def cmd_plan_roadmap_candidates(args: argparse.Namespace) -> int:
    root = find_repo_root()
    index = build_roadmap_candidate_index(root)
    output_path = root / Path(args.output)
    dump_yaml(output_path, index)
    print(
        f"[OK] generated {index['candidate_count']} roadmap candidates "
        f"ready={len(index['ready_candidate_ids'])} waiting={len(index['waiting_candidate_ids'])} "
        f"output={Path(args.output).as_posix()}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S roadmap candidate index generator")
    parser.add_argument("--output", default=str(ROADMAP_CANDIDATES_FILE).replace("\\", "/"))
    parser.set_defaults(func=cmd_plan_roadmap_candidates)
    return parser


def main() -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
