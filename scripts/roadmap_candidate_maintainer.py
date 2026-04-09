from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import time
from typing import Any

from control_plane_root import FULL_CLONE_POOL_FILE, load_full_clone_pool, resolve_control_plane_root
from governance_lib import configure_utf8_stdio, dump_yaml, load_yaml
from control_plane_root import resolve_control_plane_root
from roadmap_candidate_compiler import write_compiled_roadmap_candidates
from roadmap_candidate_index import ROADMAP_CANDIDATES_FILE, build_roadmap_candidate_index
from roadmap_claim_next import CLAIMS_FILE


SUMMARY_FILE = Path(".codex/local/roadmap_candidates/summary.yaml")
WORKTREE_POOL_FILE = Path("docs/governance/WORKTREE_POOL.yaml")


def _load_optional(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_yaml(path) or {}


def _count_status(items: list[dict[str, Any]]) -> dict[str, int]:
    counter = Counter(str(item.get("status") or "unknown") for item in items)
    return dict(counter)


def refresh_once(root: Path) -> dict[str, Any]:
    write_compiled_roadmap_candidates(root)
    index = build_roadmap_candidate_index(root)
    dump_yaml(root / ROADMAP_CANDIDATES_FILE, index)
    claims = _load_optional(root / CLAIMS_FILE)
    worktree_pool = _load_optional(root / WORKTREE_POOL_FILE)
    full_clone_pool = load_full_clone_pool(root)
    top_candidate = index["candidates"][0] if index.get("candidates") else None
    idle_worktree_slots = sum(1 for slot in worktree_pool.get("slots", []) if slot.get("status") == "idle")
    idle_full_clone_slots = sum(1 for slot in full_clone_pool.get("slots", []) if slot.get("status") == "ready")
    idle_slot_count = max(idle_worktree_slots, idle_full_clone_slots)
    fresh_claimable_count = len(index.get("fresh_claimable_candidate_ids", []))
    takeover_claimable_count = len(index.get("takeover_candidate_ids", []))
    claimable_count = len(index.get("claimable_candidate_ids", []))
    useful_parallel_supply = fresh_claimable_count + takeover_claimable_count
    parallelism_deficit = max(0, min(idle_slot_count, int(index.get("roadmap_claim_capacity") or 1)) - useful_parallel_supply)
    summary = {
        "generated_at": index["generated_at"],
        "format_version": index.get("format_version"),
        "evaluator_version": index.get("evaluator_version"),
        "control_plane_root": str(root).replace("\\", "/"),
        "candidate_count": index["candidate_count"],
        "ready_count": len(index.get("ready_candidate_ids", [])),
        "waiting_count": len(index.get("waiting_candidate_ids", [])),
        "claimable_count": claimable_count,
        "fresh_claimable_count": fresh_claimable_count,
        "takeover_claimable_count": takeover_claimable_count,
        "roadmap_claim_capacity": index.get("roadmap_claim_capacity"),
        "active_claim_count": index.get("active_claim_count"),
        "idle_slot_count": idle_slot_count,
        "parallelism_deficit": parallelism_deficit,
        "top_candidate_id": None if top_candidate is None else top_candidate["candidate_id"],
        "top_candidate_status": None if top_candidate is None else top_candidate["status"],
        "claim_status_counts": _count_status(list(claims.get("claims", []))),
        "worktree_pool_status_counts": _count_status(list(worktree_pool.get("slots", []))),
        "full_clone_pool_status_counts": _count_status(list(full_clone_pool.get("slots", []))),
    }
    dump_yaml(root / SUMMARY_FILE, summary)
    return summary


def cmd_refresh(args: argparse.Namespace) -> int:
    local_root = resolve_control_plane_root()
    control_root = resolve_control_plane_root(local_root)
    if not args.loop:
        summary = refresh_once(control_root)
        print(
            f"[OK] refreshed roadmap candidates ready={summary['ready_count']} "
            f"waiting={summary['waiting_count']} claimable={summary['claimable_count']} top={summary['top_candidate_id']}"
        )
        return 0

    cycles = int(args.cycles)
    interval = max(1, int(args.interval_seconds))
    count = 0
    while True:
        count += 1
        summary = refresh_once(control_root)
        print(
            f"[OK] refresh-roadmap-candidates cycle={count} ready={summary['ready_count']} "
            f"waiting={summary['waiting_count']} claimable={summary['claimable_count']} top={summary['top_candidate_id']}"
        )
        if cycles and count >= cycles:
            return 0
        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S roadmap candidate maintainer")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--cycles", type=int, default=0)
    parser.set_defaults(func=cmd_refresh)
    return parser


def main() -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
