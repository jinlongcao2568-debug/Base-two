from __future__ import annotations

import argparse
import json
from typing import Any

from governance_lib import GovernanceError, configure_utf8_stdio, find_repo_root
from roadmap_candidate_index import build_roadmap_candidate_index
from roadmap_claim_next import build_unlock_summary, build_why_now_summary, claim_next
from roadmap_candidate_maintainer import refresh_once


def _candidate_by_id(index: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for candidate in index.get("candidates", []):
        if candidate["candidate_id"] == candidate_id:
            return candidate
    raise GovernanceError(f"unknown roadmap candidate: {candidate_id}")


def explain_candidate(root, candidate_id: str) -> dict[str, Any]:
    index = build_roadmap_candidate_index(root)
    candidate = _candidate_by_id(index, candidate_id)
    return {
        "candidate_id": candidate["candidate_id"],
        "title": candidate["title"],
        "module_id": candidate["module_id"],
        "stage": candidate["stage"],
        "candidate_intent": candidate.get("candidate_intent"),
        "root_kind": candidate.get("root_kind"),
        "status": candidate["status"],
        "claimable": candidate["claimable"],
        "takeover_mode": candidate.get("takeover_mode"),
        "why_now": build_why_now_summary(candidate),
        "blocking_reason_codes": candidate.get("blocking_reason_codes", []),
        "blocking_reason_text": candidate.get("blocking_reason_text", []),
        "upstream_blocker_candidates": candidate.get("upstream_blocker_candidates", []),
        "release_evidence_required": candidate.get("release_evidence_required", []),
        "release_evidence_satisfied": candidate.get("release_evidence_satisfied", []),
        "release_forecast": candidate.get("release_forecast", {}),
        "what_this_unlocks_next": build_unlock_summary(candidate),
        "active_conflict_set": candidate.get("active_conflict_set", []),
        "source_authority": candidate.get("source_authority"),
        "legacy_mode": candidate.get("legacy_mode"),
    }


def explain_candidate_pool(root) -> dict[str, Any]:
    index = build_roadmap_candidate_index(root)
    summary = refresh_once(root)
    candidates = index.get("candidates", [])
    return {
        "summary": summary,
        "fresh_claimable": [candidate["candidate_id"] for candidate in candidates if candidate.get("fresh_claimable")],
        "takeover_claimable": [candidate["candidate_id"] for candidate in candidates if candidate.get("takeover_claimable")],
        "top_waiting": [
            {
                "candidate_id": candidate["candidate_id"],
                "blocking_reason_codes": candidate.get("blocking_reason_codes", []),
                "upstream_blocker_candidates": candidate.get("upstream_blocker_candidates", []),
            }
            for candidate in candidates
            if candidate["status"] == "waiting"
        ][:10],
    }


def explain_claim_decision(root) -> dict[str, Any]:
    args = argparse.Namespace(
        write_claim=False,
        promote_task=False,
        worktree_root=None,
        worker_owner=None,
        dispatch_target="worktree_pool",
        full_clone_slot_id=None,
        window_id="explain-claim-decision",
        lease_minutes=30,
        now=None,
    )
    index = build_roadmap_candidate_index(root)
    selected, blocked = claim_next(root, args)
    candidates = index.get("candidates", [])
    return {
        "selected_candidate_id": None if selected is None else selected["candidate_id"],
        "selected_takeover_mode": None if selected is None else selected.get("takeover_mode"),
        "selected_why_now": None if selected is None else build_why_now_summary(selected),
        "selected_unlocks": [] if selected is None else build_unlock_summary(selected),
        "safe_candidates": [
            {
                "candidate_id": candidate["candidate_id"],
                "selection_score": candidate.get("selection_score"),
                "claimable": candidate.get("claimable"),
            }
            for candidate in candidates
            if candidate.get("claimable")
        ],
        "blocked_candidates": blocked[:5],
    }


def explain_release_chain(root, candidate_id: str) -> dict[str, Any]:
    index = build_roadmap_candidate_index(root)
    candidate = _candidate_by_id(index, candidate_id)
    downstream = []
    queue = list(candidate.get("unlocks") or [])
    seen = set(queue)
    while queue:
        current_id = queue.pop(0)
        current = _candidate_by_id(index, current_id)
        downstream.append(
            {
                "candidate_id": current_id,
                "status": current["status"],
                "root_kind": current.get("root_kind"),
            }
        )
        for unlock in current.get("unlocks") or []:
            if unlock not in seen:
                seen.add(unlock)
                queue.append(unlock)
    return {
        "candidate_id": candidate["candidate_id"],
        "depends_on": list(candidate.get("depends_on") or []),
        "release_forecast": candidate.get("release_forecast", {}),
        "downstream_chain": downstream,
    }


def _print_json(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_explain_candidate(args: argparse.Namespace) -> int:
    return _print_json(explain_candidate(find_repo_root(), args.candidate_id))


def cmd_explain_pool(args: argparse.Namespace) -> int:
    return _print_json(explain_candidate_pool(find_repo_root()))


def cmd_explain_claim_decision(args: argparse.Namespace) -> int:
    return _print_json(explain_claim_decision(find_repo_root()))


def cmd_explain_release_chain(args: argparse.Namespace) -> int:
    return _print_json(explain_release_chain(find_repo_root(), args.candidate_id))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explain roadmap candidate decisions")
    subparsers = parser.add_subparsers(dest="command", required=True)
    candidate = subparsers.add_parser("candidate")
    candidate.add_argument("candidate_id")
    candidate.set_defaults(func=cmd_explain_candidate)
    pool = subparsers.add_parser("pool")
    pool.set_defaults(func=cmd_explain_pool)
    claim = subparsers.add_parser("claim-decision")
    claim.set_defaults(func=cmd_explain_claim_decision)
    chain = subparsers.add_parser("release-chain")
    chain.add_argument("candidate_id")
    chain.set_defaults(func=cmd_explain_release_chain)
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
