from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from control_plane_root import load_full_clone_pool, resolve_control_plane_root
from governance_lib import configure_utf8_stdio, find_repo_root, load_task_registry, load_yaml
from roadmap_candidate_maintainer import SUMMARY_FILE, refresh_once
from roadmap_claim_next import CLAIMS_FILE


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def review_pool(control_root: Path) -> dict[str, Any]:
    summary = refresh_once(control_root)
    registry = load_task_registry(control_root)
    claims = load_yaml(control_root / CLAIMS_FILE) if (control_root / CLAIMS_FILE).exists() else {"claims": []}
    full_clone_pool = load_full_clone_pool(control_root)
    tasks = registry.get("tasks", [])
    incomplete_tasks = [
        {
            "task_id": task["task_id"],
            "status": task["status"],
            "branch": task["branch"],
            "stage": task["stage"],
        }
        for task in tasks
        if task.get("task_kind") == "execution" and task.get("status") in {"doing", "paused", "review", "blocked"}
    ]
    now = datetime.now().astimezone()
    stale_claims = []
    for claim in claims.get("claims", []):
        expires_at = _parse_iso(claim.get("expires_at"))
        if expires_at and expires_at <= now:
            stale_claims.append(
                {
                    "candidate_id": claim.get("candidate_id"),
                    "status": claim.get("status"),
                    "formal_task_id": claim.get("formal_task_id"),
                }
            )
    slot_issues = []
    for slot in full_clone_pool.get("slots", []):
        if slot.get("status") == "active" and not slot.get("current_task_id"):
            slot_issues.append(f"{slot['slot_id']} active without current_task_id")
        if slot.get("status") == "ready" and slot.get("current_task_id"):
            slot_issues.append(f"{slot['slot_id']} ready but still points at {slot['current_task_id']}")
    issues = [*slot_issues]
    status = "blocked" if stale_claims or slot_issues else "ready"
    return {
        "status": status,
        "control_plane_root": str(control_root).replace("\\", "/"),
        "summary_file": str(SUMMARY_FILE).replace("\\", "/"),
        "candidate_summary": summary,
        "incomplete_tasks": incomplete_tasks,
        "stale_claims": stale_claims,
        "slot_issues": slot_issues,
        "issues": issues,
    }


def cmd_review(args: argparse.Namespace) -> int:
    local_root = find_repo_root()
    control_root = resolve_control_plane_root(local_root)
    payload = review_pool(control_root)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "ready" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S candidate pool review")
    parser.set_defaults(func=cmd_review)
    return parser


def main() -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
