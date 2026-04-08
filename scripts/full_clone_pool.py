from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from governance_lib import (
    GovernanceError,
    configure_utf8_stdio,
    dump_yaml,
    find_repo_root,
    git,
    iso_now,
    load_task_registry,
    load_worktree_registry,
    load_yaml,
)


FULL_CLONE_POOL_FILE = Path("docs/governance/FULL_CLONE_POOL.yaml")
CLAIMS_FILE = Path(".codex/local/roadmap_candidates/claims.yaml")


def _load_pool(root: Path) -> dict[str, Any]:
    path = root / FULL_CLONE_POOL_FILE
    if not path.exists():
        raise GovernanceError(f"full clone pool missing: {FULL_CLONE_POOL_FILE}")
    payload = load_yaml(path) or {}
    payload.setdefault("slots", [])
    payload.setdefault("control_plane_root", str(root).replace("\\", "/"))
    return payload


def _write_pool(root: Path, pool: dict[str, Any]) -> None:
    pool["updated_at"] = iso_now()
    pool.setdefault("control_plane_root", str(root).replace("\\", "/"))
    dump_yaml(root / FULL_CLONE_POOL_FILE, pool)


def _load_claims(root: Path) -> dict[str, Any]:
    path = root / CLAIMS_FILE
    if not path.exists():
        return {"version": "0.1", "claims": []}
    payload = load_yaml(path) or {}
    payload.setdefault("claims", [])
    return payload


def _write_claims(root: Path, claims: dict[str, Any]) -> None:
    claims["updated_at"] = iso_now()
    dump_yaml(root / CLAIMS_FILE, claims)


def _stale_after_minutes(root: Path) -> int:
    policy = load_yaml(root / "docs/governance/HANDOFF_POLICY.yaml") or {}
    return int(policy.get("stale_after_minutes") or 30)


def _claims_by_task(claims: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {}
    for claim in claims.get("claims", []):
        task_id = claim.get("formal_task_id")
        if task_id:
            items[str(task_id)] = claim
    return items


def _sync_claim_for_slot(root: Path, slot: dict[str, Any], task: dict[str, Any]) -> None:
    claims = _load_claims(root)
    by_task = _claims_by_task(claims)
    claim = by_task.get(task["task_id"])
    now = datetime.now().astimezone()
    if claim is None:
        claim = {
            "candidate_id": task.get("roadmap_candidate_id"),
            "task_id_hint": task["task_id"],
            "window_id": slot["slot_id"],
            "status": "promoted",
            "claimed_at": now.isoformat(timespec="seconds"),
            "expires_at": (now + timedelta(minutes=_stale_after_minutes(root))).isoformat(timespec="seconds"),
            "candidate_branch": task["branch"],
            "candidate_worktree": slot["path"],
            "pool_slot_id": slot["slot_id"],
            "planned_write_paths": list(task.get("planned_write_paths") or []),
            "promoted_at": task.get("activated_at") or now.isoformat(timespec="seconds"),
            "formal_task_id": task["task_id"],
            "dispatch_target": "full_clone",
        }
        claims.setdefault("claims", []).append(claim)
    else:
        claim["window_id"] = slot["slot_id"]
        claim["status"] = "promoted"
        claim["candidate_branch"] = task["branch"]
        claim["candidate_worktree"] = slot["path"]
        claim["pool_slot_id"] = slot["slot_id"]
        claim["dispatch_target"] = "full_clone"
        claim["expires_at"] = (now + timedelta(minutes=_stale_after_minutes(root))).isoformat(timespec="seconds")
    _write_claims(root, claims)


def _sync_worktree_registry_for_slot(root: Path, slot: dict[str, Any], task: dict[str, Any]) -> None:
    worktrees = load_worktree_registry(root)
    entries = worktrees.setdefault("entries", [])
    entry = next((item for item in entries if item.get("task_id") == task["task_id"]), None)
    payload = {
        "task_id": task["task_id"],
        "work_mode": "execution",
        "parent_task_id": task.get("parent_task_id"),
        "branch": task["branch"],
        "path": slot["path"],
        "status": "active",
        "cleanup_state": "not_needed",
        "cleanup_attempts": 0,
        "last_cleanup_error": None,
        "worker_owner": slot["slot_id"],
        "pool_kind": "full_clone",
    }
    if entry is None:
        entries.append(payload)
    else:
        entry.update(payload)
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)


def _reconcile_slot(root: Path, slot: dict[str, Any]) -> None:
    idle_branch = str(slot.get("idle_branch") or f"codex/{slot['slot_id']}-idle")
    registry = load_task_registry(root)
    tasks = {task["task_id"]: task for task in registry.get("tasks", [])}
    task = tasks.get(str(slot.get("current_task_id") or ""))
    if task is None:
        slot["status"] = "ready"
        slot["current_task_id"] = None
        slot["branch"] = idle_branch
        return
    if task.get("status") in {"doing", "paused", "review", "blocked"}:
        slot["status"] = "active"
        slot["branch"] = task["branch"]
        slot["current_task_id"] = task["task_id"]
        _sync_claim_for_slot(root, slot, task)
        _sync_worktree_registry_for_slot(root, slot, task)
        return
    slot["status"] = "ready"
    slot["current_task_id"] = None
    slot["branch"] = idle_branch


def _provision_slot(root: Path, slot: dict[str, Any], *, refresh: bool) -> None:
    destination = Path(str(slot["path"])).resolve()
    idle_branch = str(slot.get("idle_branch") or slot.get("branch") or f"codex/{slot['slot_id']}-idle")
    slot["idle_branch"] = idle_branch
    _reconcile_slot(root, slot)
    branch = str(slot["branch"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        git(root, "clone", "--local", str(root), str(destination))
    if refresh:
        git(destination, "fetch", "--all", check=False)
    checkout = git(destination, "switch", branch, check=False)
    if checkout.returncode != 0:
        create = git(destination, "switch", "-c", branch, f"origin/{branch}", check=False)
        if create.returncode != 0:
            local_create = git(destination, "switch", "-c", branch, check=False)
            if local_create.returncode != 0:
                raise GovernanceError(
                    local_create.stderr.strip()
                    or local_create.stdout.strip()
                    or create.stderr.strip()
                    or create.stdout.strip()
                    or f"unable to switch clone slot to {branch}"
                )
    slot["status"] = "ready"
    slot["idle_branch"] = idle_branch
    slot.setdefault("current_task_id", None)
    slot.setdefault("last_claimed_at", None)
    slot.setdefault("last_released_at", None)
    slot["last_provisioned_at"] = iso_now()
    _reconcile_slot(root, slot)


def cmd_provision_full_clone_pool(args: argparse.Namespace) -> int:
    root = find_repo_root()
    pool = _load_pool(root)
    provisioned: list[str] = []
    for slot in pool.get("slots", []):
        if args.slot_id and slot.get("slot_id") != args.slot_id:
            continue
        _provision_slot(root, slot, refresh=args.refresh)
        provisioned.append(slot["slot_id"])
    _write_pool(root, pool)
    if not provisioned:
        print("[OK] no full clone slot matched the request")
        return 0
    print(f"[OK] provisioned full clone slots: {', '.join(provisioned)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S full clone worker pool provisioner")
    parser.add_argument("--slot-id")
    parser.add_argument("--refresh", action="store_true")
    parser.set_defaults(func=cmd_provision_full_clone_pool)
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
