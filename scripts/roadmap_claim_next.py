from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Any, Iterator

from governance_lib import (
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    actual_path,
    branch_exists,
    configure_utf8_stdio,
    dump_yaml,
    find_repo_root,
    git,
    iso_now,
    load_task_registry,
    load_worktree_registry,
    load_yaml,
    validate_task,
)
from roadmap_candidate_index import ROADMAP_CANDIDATES_FILE, build_roadmap_candidate_index
from child_execution_flow import transient_child_paths
from task_handoff import ensure_handoff_file
from task_rendering import update_runlog_file, update_task_file
from task_worktree_ops import cmd_worktree_create, reuse_pool_slot_worktree


CLAIMS_FILE = Path(".codex/local/roadmap_candidates/claims.yaml")
LOCK_FILE = Path(".codex/local/roadmap_candidates/scheduler.lock")
WORKTREE_POOL_FILE = Path("docs/governance/WORKTREE_POOL.yaml")
CLAIMABLE_STATUSES = {"ready", "resumable", "stale"}
ACTIVE_TASK_STATUSES = {"doing", "review"}
ACTIVE_WORKTREE_STATUSES = {"active", "paused"}
STALE_READY_STATUSES = {"claimed", "promoted", "taken_over"}


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


def _load_worktree_pool(root: Path) -> dict[str, Any]:
    path = root / WORKTREE_POOL_FILE
    if not path.exists():
        return {"version": "0.1", "slots": []}
    payload = load_yaml(path) or {}
    payload.setdefault("slots", [])
    return payload


def _write_worktree_pool(root: Path, pool: dict[str, Any]) -> None:
    pool["updated_at"] = iso_now()
    dump_yaml(root / WORKTREE_POOL_FILE, pool)


def _stale_after_minutes(root: Path) -> int:
    policy = load_yaml(root / "docs/governance/HANDOFF_POLICY.yaml") or {}
    return int(policy.get("stale_after_minutes") or 30)


def _write_claims(root: Path, claims: dict[str, Any]) -> None:
    claims["updated_at"] = iso_now()
    dump_yaml(root / CLAIMS_FILE, claims)


def _claim_by_candidate(claims: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {claim["candidate_id"]: claim for claim in claims.get("claims", [])}


def _pool_slot_by_id(pool: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {slot["slot_id"]: slot for slot in pool.get("slots", [])}


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


def _claim_is_stale(root: Path, claim: dict[str, Any], worktree_entry: dict[str, Any] | None, now: datetime) -> bool:
    if claim.get("status") not in STALE_READY_STATUSES:
        return False
    expires_at = claim.get("expires_at")
    if expires_at and _parse_iso(str(expires_at)) <= now:
        return True
    if worktree_entry and worktree_entry.get("last_heartbeat_at"):
        heartbeat = _parse_iso(str(worktree_entry["last_heartbeat_at"]))
        if heartbeat + timedelta(minutes=_stale_after_minutes(root)) <= now:
            return True
    return False


def _worktree_entry_for_claim(active_worktrees: list[dict[str, Any]], claim: dict[str, Any]) -> dict[str, Any] | None:
    formal_task_id = claim.get("formal_task_id")
    if formal_task_id:
        for entry in active_worktrees:
            if entry.get("task_id") == formal_task_id:
                return entry
    claim_path = claim.get("candidate_worktree")
    if claim_path:
        for entry in active_worktrees:
            if entry.get("path") == claim_path:
                return entry
    return None


def _worktree_dirty_paths(path: Path) -> list[str]:
    if not path.exists():
        return []
    status = git(path, "status", "--porcelain", "--untracked-files=all", check=False).stdout.splitlines()
    dirty_paths: list[str] = []
    for line in status:
        if len(line) < 4:
            continue
        dirty_paths.append(line[3:].replace("\\", "/"))
    return dirty_paths


def _remote_diverged(path: Path) -> bool:
    upstream = git(path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
    if upstream.returncode != 0:
        return False
    counts = git(path, "rev-list", "--left-right", "--count", "HEAD...@{u}", check=False)
    if counts.returncode != 0:
        return True
    parts = counts.stdout.strip().split()
    if len(parts) != 2:
        return True
    ahead, behind = (int(part) for part in parts)
    return behind > 0


def _takeover_blockers(root: Path, candidate: dict[str, Any], claim: dict[str, Any], now: datetime) -> list[str]:
    blockers: list[str] = []
    formal_task_id = claim.get("formal_task_id")
    registry = load_task_registry(root)
    tasks_by_id = {task["task_id"]: task for task in registry.get("tasks", [])}
    task = tasks_by_id.get(formal_task_id) if formal_task_id else None
    if formal_task_id and task is None:
        blockers.append(f"formal task missing for stale claim: {formal_task_id}")
        return blockers
    worktree_path = claim.get("candidate_worktree")
    if worktree_path:
        destination = Path(str(worktree_path)).resolve()
        if destination.exists():
            dirty_paths = _worktree_dirty_paths(destination)
            if dirty_paths:
                transient = set()
                if task is not None:
                    transient |= transient_child_paths(task)
                transient.add(actual_path(str(EXECUTION_CONTEXT_FILE)))
                effective_dirty = [dirty_path for dirty_path in dirty_paths if dirty_path not in transient]
                declared = list(task.get("planned_write_paths") or []) if task else list(candidate.get("planned_write_paths") or [])
                out_of_scope = [
                    dirty_path
                    for dirty_path in effective_dirty
                    if not any(_paths_overlap(dirty_path, declared_path) for declared_path in declared)
                ]
                if out_of_scope:
                    blockers.append(f"stale worktree has out-of-scope dirty paths: {', '.join(out_of_scope)}")
                elif effective_dirty:
                    blockers.append("stale worktree is dirty and requires manual checkpoint")
            if _remote_diverged(destination):
                blockers.append("remote branch has unknown commits")
    return blockers


def _single_writer_conflict(
    candidate: dict[str, Any],
    active_tasks: list[dict[str, Any]],
    roots: list[str],
    *,
    ignore_task_ids: set[str] | None = None,
) -> bool:
    candidate_paths = list(candidate.get("planned_write_paths") or [])
    ignored = ignore_task_ids or set()
    for root in roots:
        candidate_hits_root = any(_paths_overlap(path, root) for path in candidate_paths)
        if not candidate_hits_root:
            continue
        for task in active_tasks:
            if task["task_id"] in ignored:
                continue
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
    worktree_entry = _worktree_entry_for_claim(active_worktrees, claim) if claim else None
    stale_takeover_task_id = None
    if claim:
        if _claim_is_stale(root, claim, worktree_entry, now):
            stale_takeover_task_id = claim.get("formal_task_id")
            blockers.extend(_takeover_blockers(root, candidate, claim, now))
        elif _claim_is_fresh(claim, now):
            blockers.append(f"active claim by {claim.get('window_id')}")

    candidate_paths = list(candidate.get("planned_write_paths") or [])
    for task in active_tasks:
        if stale_takeover_task_id and task["task_id"] == stale_takeover_task_id:
            continue
        if _any_path_overlaps(candidate_paths, list(task.get("planned_write_paths") or [])):
            blockers.append(f"write-path overlap with {task['task_id']}")
            break

    if _single_writer_conflict(
        candidate,
        active_tasks,
        single_writer_roots,
        ignore_task_ids={stale_takeover_task_id} if stale_takeover_task_id else None,
    ):
        blockers.append("single-writer root conflict")

    candidate_branch = candidate.get("candidate_branch")
    if candidate_branch and any(
        task.get("branch") == candidate_branch and task["task_id"] != stale_takeover_task_id
        for task in active_tasks
    ):
        blockers.append("branch already owned by active task")
    if candidate_branch and branch_exists(root, str(candidate_branch)):
        if not stale_takeover_task_id:
            blockers.append("branch already exists")

    candidate_worktree = candidate.get("candidate_worktree")
    if candidate_worktree and any(
        entry.get("path") == candidate_worktree and entry.get("task_id") != stale_takeover_task_id
        for entry in active_worktrees
    ):
        blockers.append("worktree path already owned")
    if candidate_branch and any(
        entry.get("branch") == candidate_branch and entry.get("task_id") != stale_takeover_task_id
        for entry in active_worktrees
    ):
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
        "pool_slot_id": candidate.get("pool_slot_id"),
        "planned_write_paths": list(candidate.get("planned_write_paths") or []),
    }
    existing = [claim for claim in claims.get("claims", []) if claim.get("candidate_id") != candidate["candidate_id"]]
    claims["claims"] = [*existing, new_claim]


def _build_execution_task(candidate: dict[str, Any], *, now: str) -> dict[str, Any]:
    task_id = candidate["task_id_hint"]
    task = {
        "task_id": task_id,
        "title": candidate["title"],
        "status": "doing",
        "task_kind": "execution",
        "execution_mode": "isolated_worktree",
        "parent_task_id": None,
        "stage": candidate["stage"],
        "branch": candidate["candidate_branch"],
        "size_class": "standard",
        "automation_mode": "manual",
        "worker_state": "idle",
        "blocked_reason": None,
        "last_reported_at": now,
        "topology": "single_task",
        "allowed_dirs": list(candidate.get("allowed_dirs") or []),
        "reserved_paths": list(candidate.get("reserved_paths") or []),
        "planned_write_paths": list(candidate.get("planned_write_paths") or []),
        "planned_test_paths": list(candidate.get("planned_test_paths") or []),
        "required_tests": list(candidate.get("required_tests") or []),
        "task_file": f"docs/governance/tasks/{task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
        "lane_count": 1,
        "lane_index": None,
        "parallelism_plan_id": None,
        "review_bundle_status": "not_applicable",
        "successor_state": None,
        "created_at": now,
        "activated_at": now,
        "closed_at": None,
        "roadmap_candidate_id": candidate["candidate_id"],
        "integration_gate": candidate.get("integration_gate"),
    }
    validate_task(task)
    return task


def _candidate_worktree_path(root: Path, candidate: dict[str, Any], worktree_root: str | None) -> Path:
    if worktree_root:
        return (Path(worktree_root) / candidate["task_id_hint"]).resolve()
    if candidate.get("pool_slot_path"):
        raw_path = Path(str(candidate["pool_slot_path"]))
        if raw_path.is_absolute():
            return raw_path.resolve()
        return (root / raw_path).resolve()
    raw_path = Path(str(candidate["candidate_worktree"]))
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (root / raw_path).resolve()


def _update_claim_after_promotion(
    claims: dict[str, Any],
    candidate: dict[str, Any],
    *,
    destination: Path,
    now: str,
) -> None:
    for claim in claims.get("claims", []):
        if claim.get("candidate_id") != candidate["candidate_id"]:
            continue
        claim["status"] = "promoted"
        claim["promoted_at"] = now
        claim["formal_task_id"] = candidate["task_id_hint"]
        claim["candidate_worktree"] = str(destination).replace("\\", "/")
        if candidate.get("pool_slot_id"):
            claim["pool_slot_id"] = candidate["pool_slot_id"]
        return


def _update_claim_after_takeover(
    claims: dict[str, Any],
    candidate: dict[str, Any],
    *,
    args: argparse.Namespace,
    destination: Path,
    now: datetime,
) -> None:
    for claim in claims.get("claims", []):
        if claim.get("candidate_id") != candidate["candidate_id"]:
            continue
        lease_minutes = int(args.lease_minutes)
        claim["status"] = "taken_over"
        claim["window_id"] = args.window_id
        claim["claimed_at"] = _iso(now)
        claim["expires_at"] = _iso(now + timedelta(minutes=lease_minutes))
        claim["candidate_worktree"] = str(destination).replace("\\", "/")
        if candidate.get("pool_slot_id"):
            claim["pool_slot_id"] = candidate["pool_slot_id"]
        return


def _assign_pool_slot(root: Path, candidate: dict[str, Any], args: argparse.Namespace, now: datetime) -> dict[str, Any] | None:
    if args.worktree_root:
        return None
    pool = _load_worktree_pool(root)
    slots = list(pool.get("slots", []))
    if not slots:
        raise GovernanceError(f"worktree pool is missing or empty: {WORKTREE_POOL_FILE}")
    preferred = args.worker_owner
    selected = None
    if preferred:
        selected = next((slot for slot in slots if slot.get("slot_id") == preferred), None)
        if selected is None:
            raise GovernanceError(f"requested pool slot is undefined: {preferred}")
        if selected.get("status") != "idle":
            raise GovernanceError(f"requested pool slot is not idle: {preferred}")
    else:
        selected = next((slot for slot in slots if slot.get("status") == "idle"), None)
        if selected is None:
            raise GovernanceError("no idle worktree pool slot is available")
    selected["status"] = "assigned"
    selected["current_task_id"] = candidate["task_id_hint"]
    selected["branch"] = candidate["candidate_branch"]
    selected["last_claimed_at"] = _iso(now)
    _write_worktree_pool(root, pool)
    return selected


def _sync_pool_slot_active(root: Path, slot_id: str | None, *, destination: Path, task_id: str, branch: str, now: datetime) -> None:
    if not slot_id:
        return
    pool = _load_worktree_pool(root)
    slot = _pool_slot_by_id(pool).get(slot_id)
    if slot is None:
        raise GovernanceError(f"assigned worktree pool slot missing: {slot_id}")
    slot["status"] = "active"
    slot["current_task_id"] = task_id
    slot["branch"] = branch
    slot["path"] = str(destination).replace("\\", "/")
    slot["last_claimed_at"] = _iso(now)
    _write_worktree_pool(root, pool)


def _release_pool_slot(root: Path, slot_id: str | None, *, now: datetime) -> None:
    if not slot_id:
        return
    pool = _load_worktree_pool(root)
    slot = _pool_slot_by_id(pool).get(slot_id)
    if slot is None:
        return
    slot["status"] = "idle"
    slot["current_task_id"] = None
    slot["branch"] = None
    slot["last_released_at"] = _iso(now)
    _write_worktree_pool(root, pool)


def _stale_claim_for_candidate(root: Path, candidate: dict[str, Any], claims: dict[str, Any], now: datetime) -> dict[str, Any] | None:
    claim = _claim_by_candidate(claims).get(candidate["candidate_id"])
    if not claim:
        return None
    entry = _worktree_entry_for_claim(_active_worktrees(root), claim)
    if _claim_is_stale(root, claim, entry, now):
        return claim
    return None


def _takeover_stale_claim(root: Path, candidate: dict[str, Any], claim: dict[str, Any], args: argparse.Namespace, now: datetime) -> Path:
    formal_task_id = claim.get("formal_task_id")
    if not formal_task_id:
        raise GovernanceError("stale claim takeover requires a formal task id")
    destination = Path(str(claim.get("candidate_worktree") or "")).resolve()
    if not destination.exists():
        cmd_worktree_create(argparse.Namespace(task_id=formal_task_id, path=str(destination), worker_owner=args.worker_owner))
    _sync_pool_slot_active(
        root,
        claim.get("pool_slot_id"),
        destination=destination,
        task_id=formal_task_id,
        branch=claim.get("candidate_branch") or candidate["candidate_branch"],
        now=now,
    )
    return destination


def _promote_candidate_to_worktree(root: Path, candidate: dict[str, Any], args: argparse.Namespace, now: datetime) -> Path:
    registry = load_task_registry(root)
    tasks = registry.setdefault("tasks", [])
    if any(task["task_id"] == candidate["task_id_hint"] for task in tasks):
        raise GovernanceError(f"roadmap candidate task already exists: {candidate['task_id_hint']}")
    task = _build_execution_task(candidate, now=_iso(now))
    tasks.append(task)
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_task_file(root, task)
    update_runlog_file(root, task)
    ensure_handoff_file(root, task)

    pool_slot = _assign_pool_slot(root, candidate, args, now)
    if pool_slot is not None:
        candidate["pool_slot_id"] = pool_slot["slot_id"]
        candidate["pool_slot_path"] = pool_slot["path"]
    destination = _candidate_worktree_path(root, candidate, args.worktree_root)
    try:
        if candidate.get("pool_slot_id"):
            pool = _load_worktree_pool(root)
            slot = _pool_slot_by_id(pool).get(candidate["pool_slot_id"])
            if slot is None:
                raise GovernanceError(f"assigned worktree pool slot missing: {candidate['pool_slot_id']}")
            destination = reuse_pool_slot_worktree(root, task, slot, args.worker_owner)
            _write_worktree_pool(root, pool)
        else:
            cmd_worktree_create(argparse.Namespace(task_id=task["task_id"], path=str(destination), worker_owner=args.worker_owner))
    except Exception:
        _release_pool_slot(root, candidate.get("pool_slot_id"), now=now)
        raise
    _sync_pool_slot_active(root, candidate.get("pool_slot_id"), destination=destination, task_id=task["task_id"], branch=task["branch"], now=now)
    return destination


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
        stale_claim = _stale_claim_for_candidate(root, selected, claims, now)
        if args.write_claim:
            if stale_claim is None:
                _record_claim(claims, selected, args=args, now=now)
                _write_claims(root, claims)
        if getattr(args, "promote_task", False):
            if stale_claim is not None and stale_claim.get("formal_task_id"):
                destination = _takeover_stale_claim(root, selected, stale_claim, args, now)
                claims = _load_claims(root)
                _update_claim_after_takeover(claims, selected, args=args, destination=destination, now=now)
                _write_claims(root, claims)
            else:
                destination = _promote_candidate_to_worktree(root, selected, args, now)
                claims = _load_claims(root)
                _update_claim_after_promotion(claims, selected, destination=destination, now=_iso(now))
                _write_claims(root, claims)
        return selected, blocked


def cmd_claim_next(args: argparse.Namespace) -> int:
    root = find_repo_root()
    if args.promote_task:
        args.write_claim = True
    selected, blocked = claim_next(root, args)
    if selected is None:
        first_blocker = blocked[0] if blocked else {"candidate_id": "none", "blockers": ["no candidates"]}
        print(
            "[BLOCKED] no safe roadmap candidate "
            f"top_candidate={first_blocker['candidate_id']} reason={'; '.join(first_blocker['blockers'])}"
        )
        return 1
    claims = _load_claims(root)
    selected_claim = _claim_by_candidate(claims).get(selected["candidate_id"])
    takeover_mode = bool(selected_claim and selected_claim.get("status") == "taken_over")
    mode = "taken-over" if takeover_mode else ("promoted" if args.promote_task else ("claimed" if args.write_claim else "dry-run"))
    print(
        f"[OK] claim-next {mode} candidate_id={selected['candidate_id']} "
        f"task_id_hint={selected['task_id_hint']} branch={selected['candidate_branch']}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S roadmap claim-next preflight")
    parser.add_argument("--write-claim", action="store_true")
    parser.add_argument("--promote-task", action="store_true")
    parser.add_argument("--worktree-root")
    parser.add_argument("--worker-owner")
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
