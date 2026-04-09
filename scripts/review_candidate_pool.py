from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from control_plane_root import (
    audit_full_clone_pool,
    detect_ledger_divergences,
    load_execution_leases,
    load_full_clone_pool,
    published_governance_runtime_dirty_paths,
    resolve_control_plane_root,
)
from governance_lib import configure_utf8_stdio, find_repo_root, load_current_task, load_task_registry, load_yaml
from roadmap_candidate_maintainer import SUMMARY_FILE, refresh_once
from roadmap_execution_closeout import list_closeout_ready_execution_tasks
from roadmap_claim_next import CLAIMS_FILE


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _stale_claims(claim_rows: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
    stale_claims: list[dict[str, Any]] = []
    for claim in claim_rows:
        if claim.get("status") == "closed":
            continue
        expires_at = _parse_iso(claim.get("expires_at"))
        if expires_at and expires_at <= now:
            stale_claims.append(
                {
                    "candidate_id": claim.get("candidate_id"),
                    "status": claim.get("status"),
                    "formal_task_id": claim.get("formal_task_id"),
                }
            )
    return stale_claims


def review_pool(control_root: Path) -> dict[str, Any]:
    summary = refresh_once(control_root)
    pool_audit = audit_full_clone_pool(control_root)
    dirty_runtime_paths = published_governance_runtime_dirty_paths(control_root)
    current_task = load_current_task(control_root)
    registry = load_task_registry(control_root)
    claims = load_yaml(control_root / CLAIMS_FILE) if (control_root / CLAIMS_FILE).exists() else {"claims": []}
    execution_leases = load_execution_leases(control_root)
    full_clone_pool = load_full_clone_pool(control_root)
    tasks = registry.get("tasks", [])
    candidates = (
        load_yaml(control_root / ".codex/local/roadmap_candidates/index.yaml") or {}
    ).get("candidates", [])
    live_execution_leases = [
        dict(lease)
        for lease in execution_leases.get("leases", [])
        if str(lease.get("status") or "") != "closed"
    ]
    focus_current_task = None
    if str(current_task.get("status") or "") != "idle":
        focus_current_task = {
            "task_id": current_task.get("current_task_id"),
            "title": current_task.get("title"),
            "status": current_task.get("status"),
            "stage": current_task.get("stage"),
            "branch": current_task.get("branch"),
            "worker_state": current_task.get("worker_state"),
        }
    live_leases_by_task_id = {
        str(lease.get("task_id")): lease for lease in live_execution_leases if lease.get("task_id")
    }
    incomplete_task_rows: list[dict[str, Any]] = []
    seen_task_ids: set[str] = set()
    for task in tasks:
        if task.get("task_kind") != "execution":
            continue
        lease = live_leases_by_task_id.get(str(task.get("task_id") or ""))
        if task.get("status") not in {"doing", "paused", "review", "blocked"} and lease is None:
            continue
        seen_task_ids.add(str(task["task_id"]))
        incomplete_task_rows.append(
            {
                "task_id": task["task_id"],
                "status": task["status"],
                "branch": task["branch"],
                "stage": task["stage"],
                "executor_id": None if lease is None else lease.get("executor_id"),
                "lease_status": None if lease is None else lease.get("status"),
            }
        )
    for lease in live_execution_leases:
        task_id = str(lease.get("task_id") or "")
        if not task_id or task_id in seen_task_ids:
            continue
        incomplete_task_rows.append(
            {
                "task_id": task_id,
                "status": "lease_only",
                "branch": lease.get("branch"),
                "stage": lease.get("stage"),
                "executor_id": lease.get("executor_id"),
                "lease_status": lease.get("status"),
            }
        )
    now = datetime.now().astimezone()
    stale_claims = _stale_claims(list(claims.get("claims", [])), now)
    slot_issues = []
    for slot in full_clone_pool.get("slots", []):
        if slot.get("status") == "active" and not slot.get("current_task_id"):
            slot_issues.append(f"{slot['slot_id']} active without current_task_id")
        if slot.get("status") == "ready" and slot.get("current_task_id"):
            slot_issues.append(f"{slot['slot_id']} ready but still points at {slot['current_task_id']}")
    root_candidates = [candidate for candidate in candidates if candidate.get("candidate_intent") in {"module_root", "module_preview_root"}]
    formal_roots = [candidate for candidate in root_candidates if candidate.get("root_kind") == "formal_root"]
    preview_roots = [candidate for candidate in root_candidates if candidate.get("root_kind") == "preview_root"]
    legacy_candidates = [candidate for candidate in candidates if candidate.get("legacy_mode") not in {None, "none"}]
    closeout_ready = list_closeout_ready_execution_tasks(control_root)
    closeout_blocked = [
        {
            "task_id": task["task_id"],
            "blocked_reason": task.get("blocked_reason"),
        }
        for task in tasks
        if task.get("task_kind") == "execution" and task.get("status") == "review" and task["task_id"] not in {item["task_id"] for item in closeout_ready}
    ]
    blocker_counts: dict[str, int] = {}
    for candidate in candidates:
        for code in candidate.get("blocking_reason_codes") or []:
            blocker_counts[code] = blocker_counts.get(code, 0) + 1
    top_unlock = sorted(
        [
            {
                "candidate_id": candidate["candidate_id"],
                "unlock_count": int(candidate.get("unlock_count") or 0),
            }
            for candidate in candidates
        ],
        key=lambda item: (-item["unlock_count"], item["candidate_id"]),
    )[:5]
    hard_gate_backlog = [
        candidate["candidate_id"]
        for candidate in candidates
        if candidate.get("root_kind") == "hard_gate" and candidate.get("status") in {"waiting", "blocked", "stale"}
    ]
    ledger_divergences = detect_ledger_divergences(control_root)
    quarantined_slots = [
        {
            "slot_id": slot["slot_id"],
            "slot_status": slot["slot_status"],
            "runtime_drift": slot["runtime_drift"],
            "summary_zh": slot["summary_zh"],
        }
        for slot in pool_audit.get("slots", [])
        if slot.get("quarantined")
    ]
    ready_executors: list[dict[str, Any]] = []
    if focus_current_task is None:
        ready_executors.append(
            {
                "executor_id": "control-plane-main",
                "executor_type": "control_plane",
                "status": "ready",
            }
        )
    ready_executors.extend(
        {
            "executor_id": slot["slot_id"],
            "executor_type": "full_clone",
            "status": "ready",
            "branch": slot.get("observed_branch") or slot.get("idle_branch"),
        }
        for slot in pool_audit.get("slots", [])
        if slot.get("dispatch_eligible")
    )
    quarantined_executors = [
        {
            "executor_id": slot["slot_id"],
            "executor_type": "full_clone",
            "status": "quarantined",
            "summary_zh": slot["summary_zh"],
            "runtime_drift": slot["runtime_drift"],
        }
        for slot in pool_audit.get("slots", [])
        if slot.get("quarantined")
    ]
    issues = [*slot_issues]
    if ledger_divergences:
        issues.append("ledger divergence detected")
    if str(pool_audit.get("pool_status") or "active") != "active":
        issues.append("full clone pool is frozen")
    if dirty_runtime_paths:
        issues.append("governance runtime unpublished")
    if int(pool_audit.get("stale_runtime_count") or 0) > 0:
        issues.append("stale runtime detected")
    if legacy_candidates:
        issues.append(f"legacy candidate compatibility still present: {len(legacy_candidates)}")
    if ledger_divergences:
        status = "blocked"
    elif str(pool_audit.get("pool_status") or "active") != "active":
        status = "blocked"
    elif dirty_runtime_paths:
        status = "blocked"
    elif slot_issues:
        status = "blocked"
    elif stale_claims or int(summary.get("parallelism_deficit") or 0) > 0:
        status = "degraded"
    else:
        status = "ready"
    return {
        "status": status,
        "control_plane_root": str(control_root).replace("\\", "/"),
        "summary_file": str(SUMMARY_FILE).replace("\\", "/"),
        "candidate_summary": summary,
        "focus_current_task": focus_current_task,
        "root_candidate_count": len(root_candidates),
        "formal_root_count": len(formal_roots),
        "preview_root_count": len(preview_roots),
        "legacy_candidate_count": len(legacy_candidates),
        "closeout_ready_execution_count": len(closeout_ready),
        "closeout_blocked_execution_count": len(closeout_blocked),
        "top_unlock_value_candidates": top_unlock,
        "top_blocker_codes": blocker_counts,
        "hard_gate_backlog": hard_gate_backlog,
        "incomplete_tasks": incomplete_task_rows,
        "live_execution_lease_count": len(live_execution_leases),
        "live_execution_leases": live_execution_leases,
        "running_execution_leases": live_execution_leases,
        "ready_executors": ready_executors,
        "quarantined_executors": quarantined_executors,
        "stale_claims": stale_claims,
        "slot_issues": slot_issues,
        "closeout_ready_execution_tasks": closeout_ready,
        "closeout_blocked_execution_tasks": closeout_blocked,
        "ledger_divergences": ledger_divergences,
        "ledger_divergence_count": len(ledger_divergences),
        "dirty_governance_runtime_paths": dirty_runtime_paths,
        "stale_runtime_count": int(pool_audit.get("stale_runtime_count") or 0),
        "quarantined_runtime_count": int(pool_audit.get("quarantined_runtime_count") or 0),
        "quarantined_slot_count": int(pool_audit.get("quarantined_slot_count") or 0),
        "quarantined_slots": quarantined_slots,
        "full_clone_pool_audit": pool_audit,
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
