from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Any, Iterator

from governance_lib import (
    GovernanceError,
    branch_exists,
    configure_utf8_stdio,
    dump_yaml,
    find_repo_root,
    iso_now,
    load_task_registry,
    load_worktree_registry,
    load_yaml,
)
from roadmap_candidate_index import ROADMAP_CANDIDATES_FILE, build_roadmap_candidate_index


CLAIMS_FILE = Path(".codex/local/roadmap_candidates/claims.yaml")
LOCK_FILE = Path(".codex/local/roadmap_candidates/scheduler.lock")
CLAIMABLE_STATUSES = {"ready", "resumable", "stale"}
ACTIVE_TASK_STATUSES = {"doing", "review"}
ACTIVE_WORKTREE_STATUSES = {"active", "paused"}


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _now(value: str | None) -> datetime:
    if value:
        return _parse_iso(value)
    return datetime.now().astimezone()


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _paths_overlap(left: str, right: str) -> bool:
    left_norm = _normalize(left)
    right_norm = _normalize(right)
    if not left_norm or not right_norm:
        return False
    return left_norm == right_norm or left_norm.startswith(f"{right_norm}/") or right_norm.startswith(f"{left_norm}/")


def _any_path_overlaps(left_paths: list[str], right_paths: list[str]) -> bool:
    return any(_paths_overlap(left, right) for left in left_paths for right in right_paths)


@contextmanager
def _scheduler_lock(root: Path) -> Iterator[None]:
    lock_path = root / LOCK_FILE
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise GovernanceError(f"roadmap scheduler lock already exists: {LOCK_FILE}") from error
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _load_claims(root: Path) -> dict[str, Any]:
    path = root / CLAIMS_FILE
    if not path.exists():
        return {"version": "0.1", "updated_at": None, "claims": []}
    payload = load_yaml(path) or {}
    payload.setdefault("version", "0.1")
    payload.setdefault("claims", [])
    return payload


def _write_claims(root: Path, claims: dict[str, Any]) -> None:
    claims["updated_at"] = iso_now()
    dump_yaml(root / CLAIMS_FILE, claims)


def _claim_by_candidate(claims: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {claim["candidate_id"]: claim for claim in claims.get("claims", [])}


def _active_registry_tasks(root: Path) -> list[dict[str, Any]]:
    registry = load_task_registry(root)
    return [task for task in registry.get("tasks", []) if task.get("status") in ACTIVE_TASK_STATUSES]


def _active_worktrees(root: Path) -> list[dict[str, Any]]:
    worktrees = load_worktree_registry(root)
    return [entry for entry in worktrees.get("entries", []) if entry.get("status") in ACTIVE_WORKTREE_STATUSES]


def _claim_is_fresh(claim: dict[str, Any], now: datetime) -> bool:
    expires_at = claim.get("expires_at")
    if not expires_at:
        return True
    return _parse_iso(str(expires_at)) > now


def _single_writer_conflict(candidate: dict[str, Any], active_tasks: list[dict[str, Any]], roots: list[str]) -> bool:
    candidate_paths = list(candidate.get("planned_write_paths") or [])
    for root in roots:
        candidate_hits_root = any(_paths_overlap(path, root) for path in candidate_paths)
        if not candidate_hits_root:
            continue
        for task in active_tasks:
            if any(_paths_overlap(path, root) for path in task.get("planned_write_paths") or []):
                return True
    return False


def _candidate_blockers(
    root: Path,
    candidate: dict[str, Any],
    *,
    claims_by_candidate: dict[str, dict[str, Any]],
    active_tasks: list[dict[str, Any]],
    active_worktrees: list[dict[str, Any]],
    single_writer_roots: list[str],
    now: datetime,
) -> list[str]:
    blockers: list[str] = []
    if candidate.get("status") not in CLAIMABLE_STATUSES:
        blockers.append(f"status={candidate.get('status')}")

    claim = claims_by_candidate.get(candidate["candidate_id"])
    if claim and _claim_is_fresh(claim, now):
        blockers.append(f"active claim by {claim.get('window_id')}")

    candidate_paths = list(candidate.get("planned_write_paths") or [])
    for task in active_tasks:
        if _any_path_overlaps(candidate_paths, list(task.get("planned_write_paths") or [])):
            blockers.append(f"write-path overlap with {task['task_id']}")
            break

    if _single_writer_conflict(candidate, active_tasks, single_writer_roots):
        blockers.append("single-writer root conflict")

    candidate_branch = candidate.get("candidate_branch")
    if candidate_branch and any(task.get("branch") == candidate_branch for task in active_tasks):
        blockers.append("branch already owned by active task")
    if candidate_branch and branch_exists(root, str(candidate_branch)):
        blockers.append("branch already exists")

    candidate_worktree = candidate.get("candidate_worktree")
    if candidate_worktree and any(entry.get("path") == candidate_worktree for entry in active_worktrees):
        blockers.append("worktree path already owned")
    if candidate_branch and any(entry.get("branch") == candidate_branch for entry in active_worktrees):
        blockers.append("worktree branch already owned")

    return blockers


def _ranked_safe_candidates(
    root: Path,
    *,
    index: dict[str, Any],
    claims: dict[str, Any],
    single_writer_roots: list[str],
    now: datetime,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    claims_by_candidate = _claim_by_candidate(claims)
    active_tasks = _active_registry_tasks(root)
    active_worktrees = _active_worktrees(root)
    safe: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for candidate in index.get("candidates", []):
        blockers = _candidate_blockers(
            root,
            candidate,
            claims_by_candidate=claims_by_candidate,
            active_tasks=active_tasks,
            active_worktrees=active_worktrees,
            single_writer_roots=single_writer_roots,
            now=now,
        )
        if blockers:
            blocked.append({"candidate_id": candidate["candidate_id"], "blockers": blockers})
            continue
        safe.append(candidate)
    return safe, blocked


def _single_writer_roots(index: dict[str, Any]) -> list[str]:
    # The index intentionally stays small; look up the policy from the source backlog.
    root = find_repo_root()
    backlog = load_yaml(root / "docs/governance/ROADMAP_BACKLOG.yaml") or {}
    return list((backlog.get("scheduler_policy") or {}).get("single_writer_roots") or [])


def _record_claim(claims: dict[str, Any], candidate: dict[str, Any], *, args: argparse.Namespace, now: datetime) -> None:
    lease_minutes = int(args.lease_minutes)
    expires_at = now + timedelta(minutes=lease_minutes)
    new_claim = {
        "candidate_id": candidate["candidate_id"],
        "task_id_hint": candidate["task_id_hint"],
        "window_id": args.window_id,
        "status": "claimed",
        "claimed_at": _iso(now),
        "expires_at": _iso(expires_at),
        "candidate_branch": candidate.get("candidate_branch"),
        "candidate_worktree": candidate.get("candidate_worktree"),
        "planned_write_paths": list(candidate.get("planned_write_paths") or []),
    }
    existing = [claim for claim in claims.get("claims", []) if claim.get("candidate_id") != candidate["candidate_id"]]
    claims["claims"] = [*existing, new_claim]


def claim_next(root: Path, args: argparse.Namespace) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    now = _now(args.now)
    with _scheduler_lock(root):
        index = build_roadmap_candidate_index(root)
        dump_yaml(root / ROADMAP_CANDIDATES_FILE, index)
        claims = _load_claims(root)
        safe, blocked = _ranked_safe_candidates(
            root,
            index=index,
            claims=claims,
            single_writer_roots=_single_writer_roots(index),
            now=now,
        )
        if not safe:
            return None, blocked
        selected = safe[0]
        if args.write_claim:
            _record_claim(claims, selected, args=args, now=now)
            _write_claims(root, claims)
        return selected, blocked


def cmd_claim_next(args: argparse.Namespace) -> int:
    root = find_repo_root()
    selected, blocked = claim_next(root, args)
    if selected is None:
        first_blocker = blocked[0] if blocked else {"candidate_id": "none", "blockers": ["no candidates"]}
        print(
            "[BLOCKED] no safe roadmap candidate "
            f"top_candidate={first_blocker['candidate_id']} reason={'; '.join(first_blocker['blockers'])}"
        )
        return 1
    mode = "claimed" if args.write_claim else "dry-run"
    print(
        f"[OK] claim-next {mode} candidate_id={selected['candidate_id']} "
        f"task_id_hint={selected['task_id_hint']} branch={selected['candidate_branch']}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S roadmap claim-next preflight")
    parser.add_argument("--write-claim", action="store_true")
    parser.add_argument("--window-id", default="window-local")
    parser.add_argument("--lease-minutes", type=int, default=30)
    parser.add_argument("--now")
    parser.set_defaults(func=cmd_claim_next)
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
