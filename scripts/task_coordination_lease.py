from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from governance_lib import GovernanceError, dump_yaml, iso_now
from governance_runtime import load_yaml
from task_handoff import is_top_level_coordination_task, load_handoff_policy


COORDINATION_RUNTIME_FILE = Path(".codex/local/COORDINATION_RUNTIME.yaml")
SESSION_CACHE_DIR = Path(".codex/local/session_cache")
DEFAULT_LEASE_MODE = "strict_lease"
DEFAULT_STALE_AFTER_MINUTES = 30


def _runtime_defaults() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": None,
        "session_cache": {},
        "leases": {},
    }


def _ensure_local_runtime_dir(root: Path) -> None:
    (root / COORDINATION_RUNTIME_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / SESSION_CACHE_DIR).mkdir(parents=True, exist_ok=True)


def _load_runtime(root: Path) -> dict[str, Any]:
    path = root / COORDINATION_RUNTIME_FILE
    if not path.exists():
        return _runtime_defaults()
    payload = load_yaml(path) or {}
    runtime = _runtime_defaults()
    runtime.update(payload)
    runtime["session_cache"] = dict(runtime.get("session_cache") or {})
    runtime["leases"] = dict(runtime.get("leases") or {})
    return runtime


def _write_runtime(root: Path, runtime: dict[str, Any]) -> None:
    _ensure_local_runtime_dir(root)
    runtime["updated_at"] = iso_now()
    dump_yaml(root / COORDINATION_RUNTIME_FILE, runtime)


def _session_fingerprint(root: Path) -> str:
    payload = f"{root.resolve()}::{os.getppid()}::{os.environ.get('COMPUTERNAME', '')}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def current_session_id(root: Path) -> str:
    thread_id = os.environ.get("CODEX_THREAD_ID")
    if thread_id:
        return thread_id

    runtime = _load_runtime(root)
    fingerprint = _session_fingerprint(root)
    cached = runtime["session_cache"].get(fingerprint)
    if cached:
        return str(cached)

    session_id = f"local-{uuid.uuid4().hex[:12]}"
    runtime["session_cache"][fingerprint] = session_id
    _write_runtime(root, runtime)
    return session_id


def lease_policy(root: Path) -> dict[str, Any]:
    policy = load_handoff_policy(root)
    stale_after = int(policy.get("stale_after_minutes", DEFAULT_STALE_AFTER_MINUTES))
    if stale_after <= 0:
        raise GovernanceError("handoff policy stale_after_minutes must be positive")
    return {
        "lease_mode": policy.get("lease_mode", DEFAULT_LEASE_MODE),
        "stale_after_minutes": stale_after,
        "takeover_rules": list(policy.get("takeover_rules") or []),
    }


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _lease_is_stale(lease: dict[str, Any] | None, stale_after_minutes: int) -> bool:
    if not lease or lease.get("status") != "active":
        return False
    last_seen = _parse_timestamp(lease.get("last_seen_at") or lease.get("acquired_at"))
    if last_seen is None:
        return True
    return datetime.now(last_seen.tzinfo) - last_seen > timedelta(minutes=stale_after_minutes)


def assess_coordination_lease(root: Path, task: dict[str, Any]) -> dict[str, Any]:
    session_id = current_session_id(root)
    if not is_top_level_coordination_task(task):
        return {
            "enforced": False,
            "session_id": session_id,
            "can_write": True,
            "lease_status": "not_applicable",
            "owner_session_id": None,
            "is_owner": True,
            "is_stale": False,
            "stale_after_minutes": None,
            "runtime_file": str(COORDINATION_RUNTIME_FILE).replace("\\", "/"),
        }

    runtime = _load_runtime(root)
    policy = lease_policy(root)
    lease = runtime["leases"].get(task["task_id"])
    owner_session_id = None if lease is None else lease.get("owner_session_id")
    is_owner = owner_session_id == session_id and lease is not None and lease.get("status") == "active"
    is_stale = _lease_is_stale(lease, policy["stale_after_minutes"])
    if lease is None or lease.get("status") != "active":
        lease_status = "unclaimed"
        can_write = True
    elif is_owner:
        lease_status = "owned_by_current_session"
        can_write = True
    elif is_stale:
        lease_status = "stale"
        can_write = True
    else:
        lease_status = "owned_by_other_session"
        can_write = False

    return {
        "enforced": True,
        "session_id": session_id,
        "lease_status": lease_status,
        "can_write": can_write,
        "owner_session_id": owner_session_id,
        "is_owner": is_owner,
        "is_stale": is_stale,
        "stale_after_minutes": policy["stale_after_minutes"],
        "lease_mode": policy["lease_mode"],
        "runtime_file": str(COORDINATION_RUNTIME_FILE).replace("\\", "/"),
    }


def _lease_entry(
    task: dict[str, Any],
    *,
    owner_session_id: str,
    acquired_at: str,
    status: str = "active",
) -> dict[str, Any]:
    return {
        "task_id": task["task_id"],
        "lock_mode": DEFAULT_LEASE_MODE,
        "status": status,
        "owner_session_id": owner_session_id,
        "acquired_at": acquired_at,
        "last_seen_at": iso_now(),
        "released_at": None,
    }


def _write_or_refresh_lease(
    root: Path,
    task: dict[str, Any],
    *,
    previous_lease: dict[str, Any] | None,
    owner_session_id: str,
) -> None:
    runtime = _load_runtime(root)
    acquired_at = (
        previous_lease.get("acquired_at")
        if previous_lease
        and previous_lease.get("status") == "active"
        and previous_lease.get("owner_session_id") == owner_session_id
        else iso_now()
    )
    runtime["leases"][task["task_id"]] = _lease_entry(
        task,
        owner_session_id=owner_session_id,
        acquired_at=acquired_at,
    )
    _write_runtime(root, runtime)


def claim_coordination_lease(root: Path, task: dict[str, Any], *, reason: str) -> dict[str, Any]:
    assessment = assess_coordination_lease(root, task)
    if not assessment["enforced"]:
        return assessment

    runtime = _load_runtime(root)
    previous_lease = runtime["leases"].get(task["task_id"])
    if assessment["lease_status"] == "owned_by_other_session":
        raise GovernanceError(
            f"{reason} blocked by active coordination lease: owner_session_id={assessment['owner_session_id']}; "
            "use handoff, release, or takeover"
        )
    _write_or_refresh_lease(
        root,
        task,
        previous_lease=previous_lease,
        owner_session_id=assessment["session_id"],
    )
    updated = assess_coordination_lease(root, task)
    updated["previous_owner_session_id"] = assessment["owner_session_id"]
    if assessment["lease_status"] == "stale":
        updated["claim_result"] = "reclaimed_stale_lease"
    elif assessment["lease_status"] == "unclaimed":
        updated["claim_result"] = "acquired_new_lease"
    else:
        updated["claim_result"] = "refreshed_current_lease"
    return updated


def release_coordination_lease(root: Path, task: dict[str, Any], *, reason: str) -> dict[str, Any]:
    assessment = assess_coordination_lease(root, task)
    if not assessment["enforced"]:
        return assessment
    runtime = _load_runtime(root)
    lease = runtime["leases"].get(task["task_id"])
    if lease is None or lease.get("status") != "active":
        assessment["release_result"] = "no_active_lease"
        return assessment
    if lease.get("owner_session_id") != assessment["session_id"]:
        raise GovernanceError(
            f"{reason} blocked by active coordination lease: owner_session_id={assessment['owner_session_id']}; "
            "only the owner session can release it"
        )
    lease["status"] = "released"
    lease["released_at"] = iso_now()
    lease["last_seen_at"] = iso_now()
    runtime["leases"][task["task_id"]] = lease
    _write_runtime(root, runtime)
    released = assess_coordination_lease(root, task)
    released["release_result"] = "released"
    released["previous_owner_session_id"] = assessment["owner_session_id"]
    return released


def takeover_coordination_lease(root: Path, task: dict[str, Any], *, reason: str) -> dict[str, Any]:
    assessment = assess_coordination_lease(root, task)
    if not assessment["enforced"]:
        return assessment

    runtime = _load_runtime(root)
    previous_lease = runtime["leases"].get(task["task_id"])
    _write_or_refresh_lease(
        root,
        task,
        previous_lease=None,
        owner_session_id=assessment["session_id"],
    )
    updated = assess_coordination_lease(root, task)
    updated["previous_owner_session_id"] = assessment["owner_session_id"]
    if assessment["lease_status"] in {"owned_by_other_session", "stale"}:
        updated["takeover_result"] = "took_over_existing_lease"
    elif assessment["lease_status"] == "unclaimed":
        updated["takeover_result"] = "acquired_unclaimed_lease"
    else:
        updated["takeover_result"] = "refreshed_current_lease"
    return updated
