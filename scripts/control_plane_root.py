from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
from typing import Any

from child_execution_flow import transient_child_paths
from governance_lib import (
    CURRENT_TASK_FILE,
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    TASK_REGISTRY_FILE,
    WORKTREE_REGISTRY_FILE,
    actual_path,
    current_branch,
    dump_yaml,
    find_repo_root,
    git,
    git_status_paths,
    iso_now,
    load_yaml,
)


FULL_CLONE_POOL_FILE = Path("docs/governance/FULL_CLONE_POOL.yaml")
EXECUTION_LEASES_FILE = Path("docs/governance/EXECUTION_LEASES.yaml")
CLAIMS_FILE = Path(".codex/local/roadmap_candidates/claims.yaml")
ROADMAP_CANDIDATES_FILE = Path(".codex/local/roadmap_candidates/index.yaml")
GOVERNANCE_RUNTIME_STAMP_FILE = Path(".codex/local/governance_runtime/stamp.yaml")
GOVERNANCE_RUNTIME_ROLLOUT_STATE_FILE = Path(".codex/local/governance_runtime/rollout_state.yaml")

GOVERNANCE_RUNTIME_VERSION = "control_plane_runtime_v1"
CANDIDATE_INDEX_FORMAT_VERSION = "roadmap_candidate_index_v2"
TERMINAL_TASK_STATUSES = {"done", "closed"}
NON_TERMINAL_EXECUTION_STATUSES = {"doing", "paused", "blocked", "review"}
CONTROL_PLANE_EXECUTOR_ID = "control-plane-main"
EXECUTION_LEASE_TERMINAL_STATUSES = {"closed"}
GOVERNANCE_RUNTIME_FILES = (
    Path("scripts/control_plane_root.py"),
    Path("scripts/full_clone_pool.py"),
    Path("scripts/roadmap_candidate_compiler.py"),
    Path("scripts/roadmap_candidate_index.py"),
    Path("scripts/roadmap_claim_next.py"),
    Path("scripts/roadmap_scope_policy.py"),
    Path("scripts/review_candidate_pool.py"),
    Path("scripts/task_continuation_ops.py"),
    Path("scripts/task_coordination_planner.py"),
    Path("scripts/task_lifecycle_ops.py"),
    Path("scripts/task_runtime_ops.py"),
    Path("scripts/task_worker_ops.py"),
    Path("scripts/worker_self_loop.py"),
)


def load_full_clone_pool(root: Path) -> dict[str, Any]:
    path = root / FULL_CLONE_POOL_FILE
    if not path.exists():
        return {}
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"full clone pool must be a mapping: {FULL_CLONE_POOL_FILE}")
    payload.setdefault("slots", [])
    return payload


def save_full_clone_pool(root: Path, pool: dict[str, Any]) -> None:
    pool["updated_at"] = iso_now()
    dump_yaml(root / FULL_CLONE_POOL_FILE, pool)


def update_full_clone_slot(
    root: Path,
    slot_id: str,
    *,
    status: str,
    current_task_id: str | None,
    branch: str | None,
    blocked_reason: str | None = None,
    stale_runtime: bool | None = None,
    claimed_at: str | None = None,
    released_at: str | None = None,
) -> dict[str, Any]:
    pool = load_full_clone_pool(root)
    slot = slot_by_id(pool, slot_id)
    if slot is None:
        raise GovernanceError(f"unknown full clone slot: {slot_id}")
    slot["status"] = status
    slot["current_task_id"] = current_task_id
    slot["branch"] = branch
    slot["blocked_reason"] = blocked_reason
    if stale_runtime is not None:
        slot["stale_runtime"] = stale_runtime
    if claimed_at is not None:
        slot["last_claimed_at"] = claimed_at
    if released_at is not None:
        slot["last_released_at"] = released_at
    save_full_clone_pool(root, pool)
    return slot


def set_full_clone_slot_active(root: Path, slot_id: str, *, task_id: str, branch: str, now: str) -> dict[str, Any]:
    return update_full_clone_slot(
        root,
        slot_id,
        status="active",
        current_task_id=task_id,
        branch=branch,
        blocked_reason=None,
        stale_runtime=False,
        claimed_at=now,
    )


def set_full_clone_slot_releasing(root: Path, slot_id: str, *, task_id: str, branch: str) -> dict[str, Any]:
    return update_full_clone_slot(
        root,
        slot_id,
        status="releasing",
        current_task_id=task_id,
        branch=branch,
        blocked_reason=None,
        stale_runtime=False,
    )


def set_full_clone_slot_ready(root: Path, slot_id: str, *, now: str) -> dict[str, Any]:
    pool = load_full_clone_pool(root)
    slot = slot_by_id(pool, slot_id)
    if slot is None:
        raise GovernanceError(f"unknown full clone slot: {slot_id}")
    idle_branch = str(slot.get("idle_branch") or default_full_clone_idle_branch(slot_id))
    return update_full_clone_slot(
        root,
        slot_id,
        status="ready",
        current_task_id=None,
        branch=idle_branch,
        blocked_reason=None,
        stale_runtime=False,
        released_at=now,
    )


def set_full_clone_slot_blocked(
    root: Path,
    slot_id: str,
    *,
    reason: str,
    task_id: str | None = None,
    branch: str | None = None,
    stale_runtime: bool = False,
) -> dict[str, Any]:
    return update_full_clone_slot(
        root,
        slot_id,
        status="blocked",
        current_task_id=task_id,
        branch=branch,
        blocked_reason=reason,
        stale_runtime=stale_runtime,
    )


def execution_leases_defaults() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": None,
        "revision": 0,
        "leases": [],
    }


def load_execution_leases(root: Path) -> dict[str, Any]:
    path = root / EXECUTION_LEASES_FILE
    if not path.exists():
        return execution_leases_defaults()
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"execution leases must be a mapping: {EXECUTION_LEASES_FILE}")
    merged = execution_leases_defaults()
    merged.update(payload)
    merged["revision"] = int(merged.get("revision") or 0)
    merged["leases"] = [dict(lease or {}) for lease in (merged.get("leases") or [])]
    return merged


def _lease_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value)
    slug = slug.strip("-")
    return slug or "unknown"


def _execution_lease_matches(
    lease: dict[str, Any],
    *,
    task_id: str | None = None,
    executor_id: str | None = None,
    include_closed: bool = True,
) -> bool:
    if task_id is not None and str(lease.get("task_id") or "") != task_id:
        return False
    if executor_id is not None and str(lease.get("executor_id") or "") != executor_id:
        return False
    if not include_closed and str(lease.get("status") or "") in EXECUTION_LEASE_TERMINAL_STATUSES:
        return False
    return True


def find_execution_leases(
    payload: dict[str, Any],
    *,
    task_id: str | None = None,
    executor_id: str | None = None,
    include_closed: bool = True,
) -> list[dict[str, Any]]:
    return [
        lease
        for lease in (payload.get("leases") or [])
        if _execution_lease_matches(
            lease,
            task_id=task_id,
            executor_id=executor_id,
            include_closed=include_closed,
        )
    ]


def _write_execution_leases(root: Path, payload: dict[str, Any]) -> None:
    payload["revision"] = int(payload.get("revision") or 0) + 1
    payload["updated_at"] = iso_now()
    dump_yaml(root / EXECUTION_LEASES_FILE, payload)


def sync_execution_lease(
    root: Path,
    *,
    task: dict[str, Any],
    executor_id: str,
    executor_type: str,
    status: str,
    owner_session_id: str | None = None,
    heartbeat_at: str | None = None,
) -> dict[str, Any]:
    payload = load_execution_leases(root)
    existing = find_execution_leases(
        payload,
        task_id=str(task.get("task_id") or ""),
        executor_id=executor_id,
    )
    lease = existing[0] if existing else None
    now = heartbeat_at or iso_now()
    if lease is None:
        lease = {
            "lease_id": f"lease-{_lease_slug(str(task.get('task_id') or 'task'))}-{_lease_slug(executor_id)}",
            "task_id": task.get("task_id"),
            "task_kind": task.get("task_kind"),
            "stage": task.get("stage"),
            "branch": task.get("branch"),
            "candidate_id": task.get("roadmap_candidate_id"),
            "executor_id": executor_id,
            "executor_type": executor_type,
            "status": status,
            "owner_session_id": owner_session_id,
            "started_at": now,
            "heartbeat_at": now,
            "closed_at": None,
        }
        payload.setdefault("leases", []).append(lease)
    else:
        lease["task_kind"] = task.get("task_kind")
        lease["stage"] = task.get("stage")
        lease["branch"] = task.get("branch")
        lease["candidate_id"] = task.get("roadmap_candidate_id")
        lease["executor_type"] = executor_type
        lease["status"] = status
        if owner_session_id is not None:
            lease["owner_session_id"] = owner_session_id
        lease["started_at"] = lease.get("started_at") or now
        lease["heartbeat_at"] = now
    if status in EXECUTION_LEASE_TERMINAL_STATUSES:
        lease["closed_at"] = lease.get("closed_at") or now
    else:
        lease["closed_at"] = None
    _write_execution_leases(root, payload)
    return dict(lease)


def close_execution_leases(
    root: Path,
    *,
    task_id: str,
    executor_id: str | None = None,
    owner_session_id: str | None = None,
) -> list[dict[str, Any]]:
    payload = load_execution_leases(root)
    now = iso_now()
    changed: list[dict[str, Any]] = []
    for lease in payload.get("leases", []):
        if not _execution_lease_matches(
            lease,
            task_id=task_id,
            executor_id=executor_id,
            include_closed=False,
        ):
            continue
        lease["status"] = "closed"
        lease["closed_at"] = now
        lease["heartbeat_at"] = now
        if owner_session_id is not None:
            lease["owner_session_id"] = owner_session_id
        changed.append(dict(lease))
    if changed:
        _write_execution_leases(root, payload)
    return changed


def _load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"expected mapping payload: {path.as_posix()}")
    return payload


def _tasks_by_id(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        str(task.get("task_id")): task
        for task in (payload or {}).get("tasks", []) or []
        if task.get("task_id")
    }


def _claims_by_candidate(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        str(claim.get("candidate_id")): claim
        for claim in (payload or {}).get("claims", []) or []
        if claim.get("candidate_id")
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_runtime_files(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in GOVERNANCE_RUNTIME_FILES:
        path = root / relative
        if not path.exists():
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
        digest.update(b"\0")
    return digest.hexdigest()


def _published_runtime_file_bytes(root: Path, relative: Path) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative.as_posix()}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.replace(b"\r\n", b"\n")


def _hash_published_runtime_files(root: Path) -> str:
    if _git_head(root) is None:
        return _hash_runtime_files(root)
    digest = hashlib.sha256()
    for relative in GOVERNANCE_RUNTIME_FILES:
        payload = _published_runtime_file_bytes(root, relative)
        if payload is None:
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")
    return digest.hexdigest()


def _git_head(root: Path) -> str | None:
    result = git(root, "rev-parse", "HEAD", check=False)
    head = (result.stdout or "").strip()
    if result.returncode != 0 or not head:
        return None
    return head


def published_governance_runtime_dirty_paths(root: Path) -> list[str]:
    runtime_paths = {actual_path(str(relative)) for relative in GOVERNANCE_RUNTIME_FILES}
    return [path for path in git_status_paths(root) if actual_path(path) in runtime_paths]


def build_governance_runtime_stamp(root: Path) -> dict[str, Any]:
    return {
        "governance_runtime_version": GOVERNANCE_RUNTIME_VERSION,
        "candidate_index_format_version": CANDIDATE_INDEX_FORMAT_VERSION,
        "governance_scripts_hash": _hash_published_runtime_files(root),
        "control_plane_head": _git_head(root),
    }


def write_governance_runtime_stamp(root: Path) -> dict[str, Any]:
    stamp = build_governance_runtime_stamp(root)
    dump_yaml(root / GOVERNANCE_RUNTIME_STAMP_FILE, stamp)
    return stamp


def runtime_rollout_state_defaults() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": None,
        "revision": 0,
        "rollout_pending": False,
        "pending_since": None,
        "required_runtime_hash": None,
        "required_control_plane_head": None,
        "last_successful_hash": None,
        "last_successful_head": None,
        "last_refresh_at": None,
        "last_audit_at": None,
        "last_error": None,
        "last_detected_reason": None,
    }


def load_runtime_rollout_state(root: Path) -> dict[str, Any]:
    path = root / GOVERNANCE_RUNTIME_ROLLOUT_STATE_FILE
    if not path.exists():
        return runtime_rollout_state_defaults()
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"runtime rollout state must be a mapping: {GOVERNANCE_RUNTIME_ROLLOUT_STATE_FILE}")
    merged = runtime_rollout_state_defaults()
    merged.update(payload)
    merged["revision"] = int(merged.get("revision") or 0)
    return merged


def write_runtime_rollout_state(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    payload["revision"] = int(payload.get("revision") or 0) + 1
    payload["updated_at"] = iso_now()
    dump_yaml(root / GOVERNANCE_RUNTIME_ROLLOUT_STATE_FILE, payload)
    return payload


def _load_previous_runtime_stamp(root: Path) -> dict[str, Any] | None:
    path = root / GOVERNANCE_RUNTIME_STAMP_FILE
    if not path.exists():
        return None
    payload = load_yaml(path) or {}
    return payload if isinstance(payload, dict) else None


def sync_runtime_rollout_state(root: Path, *, reason: str | None = None) -> dict[str, Any]:
    previous_stamp = _load_previous_runtime_stamp(root)
    current_stamp = build_governance_runtime_stamp(root)
    dump_yaml(root / GOVERNANCE_RUNTIME_STAMP_FILE, current_stamp)
    state = load_runtime_rollout_state(root)
    now = iso_now()
    if not state.get("last_successful_hash") and not state.get("rollout_pending"):
        baseline_hash = None
        baseline_head = None
        if previous_stamp:
            baseline_hash = previous_stamp.get("governance_scripts_hash")
            baseline_head = previous_stamp.get("control_plane_head")
        state["last_successful_hash"] = baseline_hash or current_stamp.get("governance_scripts_hash")
        state["last_successful_head"] = baseline_head or current_stamp.get("control_plane_head")
    required_hash = current_stamp.get("governance_scripts_hash")
    if required_hash and required_hash != state.get("last_successful_hash"):
        previous_required = state.get("required_runtime_hash")
        state["rollout_pending"] = True
        state["required_runtime_hash"] = required_hash
        state["required_control_plane_head"] = current_stamp.get("control_plane_head")
        if not state.get("pending_since") or previous_required != required_hash:
            state["pending_since"] = now
        state["last_detected_reason"] = reason
    write_runtime_rollout_state(root, state)
    return state


def mark_runtime_rollout_pending(root: Path, *, stamp: dict[str, Any] | None = None, reason: str | None = None) -> dict[str, Any]:
    state = load_runtime_rollout_state(root)
    stamp = stamp or build_governance_runtime_stamp(root)
    required_hash = stamp.get("governance_scripts_hash")
    previous_required = state.get("required_runtime_hash")
    now = iso_now()
    state["rollout_pending"] = True
    state["required_runtime_hash"] = required_hash
    state["required_control_plane_head"] = stamp.get("control_plane_head")
    if not state.get("pending_since") or previous_required != required_hash:
        state["pending_since"] = now
    state["last_detected_reason"] = reason
    write_runtime_rollout_state(root, state)
    return state


def clear_runtime_rollout_pending(
    root: Path,
    *,
    stamp: dict[str, Any] | None = None,
    last_refresh_at: str | None = None,
    last_audit_at: str | None = None,
) -> dict[str, Any]:
    state = load_runtime_rollout_state(root)
    stamp = stamp or build_governance_runtime_stamp(root)
    state["rollout_pending"] = False
    state["pending_since"] = None
    state["required_runtime_hash"] = stamp.get("governance_scripts_hash")
    state["required_control_plane_head"] = stamp.get("control_plane_head")
    state["last_successful_hash"] = stamp.get("governance_scripts_hash")
    state["last_successful_head"] = stamp.get("control_plane_head")
    if last_refresh_at:
        state["last_refresh_at"] = last_refresh_at
    if last_audit_at:
        state["last_audit_at"] = last_audit_at
    state["last_error"] = None
    write_runtime_rollout_state(root, state)
    return state


def note_runtime_rollout_refresh(root: Path, *, reason: str | None = None) -> dict[str, Any]:
    state = sync_runtime_rollout_state(root, reason=reason)
    state["last_refresh_at"] = iso_now()
    state["last_error"] = None
    write_runtime_rollout_state(root, state)
    return state


def note_runtime_rollout_audit(root: Path, *, audit: dict[str, Any], reason: str | None = None) -> dict[str, Any]:
    stamp = build_governance_runtime_stamp(root)
    state = sync_runtime_rollout_state(root, reason=reason)
    state["last_audit_at"] = iso_now()
    if audit.get("status") == "ready":
        return clear_runtime_rollout_pending(
            root,
            stamp=stamp,
            last_refresh_at=state.get("last_refresh_at"),
            last_audit_at=state.get("last_audit_at"),
        )
    state["last_error"] = f"audit blocked: {audit.get('status')}"
    write_runtime_rollout_state(root, state)
    return state


def _runtime_stamp_reasons(control_stamp: dict[str, Any], clone_root: Path) -> list[str]:
    clone_stamp = build_governance_runtime_stamp(clone_root)
    reasons: list[str] = []
    for field in (
        "governance_runtime_version",
        "candidate_index_format_version",
        "governance_scripts_hash",
    ):
        if control_stamp.get(field) != clone_stamp.get(field):
            reasons.append(
                f"治理运行时标记不一致: {field} control={control_stamp.get(field)} clone={clone_stamp.get(field)}"
            )
    return reasons


def _control_candidate_ids(root: Path) -> set[str] | None:
    path = root / ROADMAP_CANDIDATES_FILE
    if not path.exists():
        return None
    payload = load_yaml(path) or {}
    return {
        str(candidate.get("candidate_id"))
        for candidate in payload.get("candidates", []) or []
        if candidate.get("candidate_id")
    }


def _candidate_cache_issues(control_candidate_ids: set[str] | None, clone_root: Path) -> list[str]:
    path = clone_root / ROADMAP_CANDIDATES_FILE
    if not path.exists():
        return []
    payload = load_yaml(path) or {}
    issues: list[str] = []
    format_version = str(payload.get("format_version") or "")
    if format_version != CANDIDATE_INDEX_FORMAT_VERSION:
        legacy_version = payload.get("version")
        issues.append(
            f"clone 候选池格式过期: format_version={format_version or 'missing'} version={legacy_version or 'missing'}"
        )
    if control_candidate_ids is not None:
        clone_candidate_ids = {
            str(candidate.get("candidate_id"))
            for candidate in payload.get("candidates", []) or []
            if candidate.get("candidate_id")
        }
        retired = sorted(clone_candidate_ids - control_candidate_ids)
        if retired:
            sample = ", ".join(retired[:3])
            suffix = "" if len(retired) <= 3 else f" (+{len(retired) - 3} more)"
            issues.append(f"clone 候选池仍含已淘汰 candidate: {sample}{suffix}")
    return issues


def _effective_dirty_paths(slot_path: Path, clone_task: dict[str, Any] | None) -> list[str]:
    dirty_paths = git_status_paths(slot_path)
    transient = {actual_path(str(EXECUTION_CONTEXT_FILE))}
    if clone_task is not None:
        transient |= transient_child_paths(clone_task)
    return [path for path in dirty_paths if path not in transient]


def _non_terminal_execution_tasks(clone_tasks_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for task in clone_tasks_by_id.values():
        task_id = str(task.get("task_id") or "")
        status = str(task.get("status") or "")
        task_kind = str(task.get("task_kind") or "")
        if status not in NON_TERMINAL_EXECUTION_STATUSES:
            continue
        if task_kind != "execution" and not task_id.startswith("TASK-RM-"):
            continue
        items.append(task)
    return items


def assess_full_clone_slot_runtime(
    root: Path,
    slot: dict[str, Any],
    *,
    tasks_by_id: dict[str, dict[str, Any]] | None = None,
    claims_by_candidate: dict[str, dict[str, Any]] | None = None,
    control_stamp: dict[str, Any] | None = None,
    control_candidate_ids: set[str] | None = None,
) -> dict[str, Any]:
    registry = _load_registry(root / TASK_REGISTRY_FILE) if tasks_by_id is None else None
    tasks_by_id = tasks_by_id or _tasks_by_id(registry)
    claims = _load_registry(root / CLAIMS_FILE) if claims_by_candidate is None else None
    claims_by_candidate = claims_by_candidate or _claims_by_candidate(claims)
    control_stamp = control_stamp or write_governance_runtime_stamp(root)
    if control_candidate_ids is None:
        control_candidate_ids = _control_candidate_ids(root)

    slot_id = str(slot.get("slot_id") or "-")
    slot_status = str(slot.get("status") or "-")
    slot_path_raw = str(slot.get("path") or "").strip()
    idle_branch = str(slot.get("idle_branch") or default_full_clone_idle_branch(slot_id))
    current_task_id = str(slot.get("current_task_id") or "").strip() or None
    slot_path = Path(slot_path_raw).resolve() if slot_path_raw else None

    observed_branch: str | None = None
    dirty_paths: list[str] = []
    clone_registry: dict[str, Any] = {}
    clone_tasks_by_id: dict[str, dict[str, Any]] = {}
    clone_only_task_ids: list[str] = []
    non_terminal_tasks: list[dict[str, Any]] = []
    runtime_stamp_reasons: list[str] = []
    candidate_cache_issues: list[str] = []
    reasons: list[str] = []
    divergence_reasons: list[str] = []

    if slot_path is None or not slot_path.exists():
        reasons.append("full clone slot 路径缺失")
    else:
        clone_registry = _load_registry(slot_path / TASK_REGISTRY_FILE)
        clone_tasks_by_id = _tasks_by_id(clone_registry)
        clone_only_task_ids = [task_id for task_id in clone_tasks_by_id if task_id not in tasks_by_id]
        if clone_only_task_ids:
            sample = ", ".join(clone_only_task_ids[:3])
            suffix = "" if len(clone_only_task_ids) <= 3 else f" (+{len(clone_only_task_ids) - 3} more)"
            reasons.append(f"clone 台账存在主控缺失任务: {sample}{suffix}")
        non_terminal_tasks = _non_terminal_execution_tasks(clone_tasks_by_id)
        try:
            observed_branch = current_branch(slot_path)
        except GovernanceError as error:
            reasons.append(f"无法读取 clone 当前分支: {error}")
        clone_task = clone_tasks_by_id.get(current_task_id) if current_task_id else None
        try:
            dirty_paths = _effective_dirty_paths(slot_path, clone_task)
        except GovernanceError as error:
            reasons.append(f"无法读取 clone 工作树状态: {error}")
        runtime_stamp_reasons = _runtime_stamp_reasons(control_stamp, slot_path)
        candidate_cache_issues = _candidate_cache_issues(control_candidate_ids, slot_path)

    if slot_status == "ready":
        branch_drift_from_idle = observed_branch is not None and observed_branch != idle_branch
        if current_task_id:
            message = f"ready slot 仍指向 current_task_id={current_task_id}"
            reasons.append(message)
            divergence_reasons.append(message)
        if dirty_paths:
            sample = ", ".join(dirty_paths[:4])
            suffix = "" if len(dirty_paths) <= 4 else f" (+{len(dirty_paths) - 4} more)"
            message = f"ready slot 存在非 transient tracked dirty files: {sample}{suffix}"
            reasons.append(message)
            divergence_reasons.append(message)
        if non_terminal_tasks and (current_task_id is not None or branch_drift_from_idle):
            sample = ", ".join(f"{task.get('task_id')}:{task.get('status')}" for task in non_terminal_tasks[:3])
            suffix = "" if len(non_terminal_tasks) <= 3 else f" (+{len(non_terminal_tasks) - 3} more)"
            message = f"clone 本地账本残留非终态执行任务: {sample}{suffix}"
            reasons.append(message)
            divergence_reasons.append(message)
        if clone_only_task_ids:
            sample = ", ".join(clone_only_task_ids[:3])
            suffix = "" if len(clone_only_task_ids) <= 3 else f" (+{len(clone_only_task_ids) - 3} more)"
            message = f"clone 台账存在主控缺失任务: {sample}{suffix}"
            if message not in divergence_reasons:
                divergence_reasons.append(message)

    main_task = tasks_by_id.get(current_task_id or "") if current_task_id else None
    clone_task = clone_tasks_by_id.get(current_task_id or "") if current_task_id else None
    candidate_id = None
    if main_task:
        candidate_id = main_task.get("roadmap_candidate_id")
    elif clone_task:
        candidate_id = clone_task.get("roadmap_candidate_id")
    elif non_terminal_tasks:
        candidate_id = non_terminal_tasks[0].get("roadmap_candidate_id")

    if current_task_id:
        if main_task is None:
            message = "主控制面缺少当前 slot task 记录"
            reasons.append(message)
            divergence_reasons.append(message)
        if clone_task is None:
            message = "clone 台账缺少当前 slot task 记录"
            reasons.append(message)
            divergence_reasons.append(message)
        if main_task and clone_task and main_task.get("status") != clone_task.get("status"):
            message = f"主账本状态={main_task.get('status')} clone 状态={clone_task.get('status')}"
            reasons.append(message)
            divergence_reasons.append(message)
        if main_task and clone_task and main_task.get("worker_state") != clone_task.get("worker_state"):
            message = (
                f"主账本 worker_state={main_task.get('worker_state')} clone worker_state={clone_task.get('worker_state')}"
            )
            reasons.append(message)
            divergence_reasons.append(message)
        if main_task and main_task.get("status") == "done":
            if slot_status != "ready" or current_task_id:
                message = "主账本已完成，但 full-clone slot 尚未释放"
                reasons.append(message)
                divergence_reasons.append(message)
            claim = claims_by_candidate.get(str(candidate_id)) if candidate_id else None
            if claim and claim.get("status") != "closed":
                message = f"主账本已完成，但 claim 仍为 {claim.get('status') or 'unknown'}"
                reasons.append(message)
                divergence_reasons.append(message)
        if clone_task and clone_task.get("status") == "done" and main_task and main_task.get("status") != "done":
            message = "clone 已完成当前任务，但主控制面尚未完成同一任务"
            reasons.append(message)
            divergence_reasons.append(message)

    for extra_reason in runtime_stamp_reasons:
        if extra_reason not in reasons:
            reasons.append(extra_reason)
        if slot_status == "ready" and extra_reason not in divergence_reasons:
            divergence_reasons.append(extra_reason)
    for extra_reason in candidate_cache_issues:
        if extra_reason not in reasons:
            reasons.append(extra_reason)
        if slot_status == "ready" and extra_reason not in divergence_reasons:
            divergence_reasons.append(extra_reason)

    task_for_divergence = current_task_id
    if not task_for_divergence and non_terminal_tasks:
        task_for_divergence = str(non_terminal_tasks[0].get("task_id") or "") or None
    if not task_for_divergence and clone_only_task_ids:
        task_for_divergence = clone_only_task_ids[0]

    if candidate_id is None and task_for_divergence:
        task_payload = tasks_by_id.get(task_for_divergence) or clone_tasks_by_id.get(task_for_divergence) or {}
        candidate_id = task_payload.get("roadmap_candidate_id")

    claim = claims_by_candidate.get(str(candidate_id)) if candidate_id else None
    summary = divergence_reasons[0] if divergence_reasons else (reasons[0] if reasons else "状态一致")
    dispatch_eligible = slot_status == "ready"
    quarantined = slot_status in {"blocked", "releasing"}
    dispatch_blocking_runtime_drift = bool(runtime_stamp_reasons) and dispatch_eligible
    return {
        "slot_id": slot_id,
        "slot_status": slot_status,
        "dispatch_eligible": dispatch_eligible,
        "quarantined": quarantined,
        "slot_path": None if slot_path is None else str(slot_path).replace("\\", "/"),
        "idle_branch": idle_branch,
        "observed_branch": observed_branch,
        "current_task_id": current_task_id,
        "task_id": task_for_divergence,
        "candidate_id": candidate_id,
        "main_status": None if task_for_divergence is None else tasks_by_id.get(task_for_divergence, {}).get("status"),
        "clone_status": None if task_for_divergence is None else clone_tasks_by_id.get(task_for_divergence, {}).get("status"),
        "claim_status": None if claim is None else claim.get("status"),
        "effective_dirty_paths": dirty_paths,
        "runtime_stamp_reasons": runtime_stamp_reasons,
        "candidate_cache_issues": candidate_cache_issues,
        "clone_only_task_ids": clone_only_task_ids,
        "non_terminal_execution_tasks": [
            {
                "task_id": task.get("task_id"),
                "status": task.get("status"),
                "roadmap_candidate_id": task.get("roadmap_candidate_id"),
            }
            for task in non_terminal_tasks
        ],
        "runtime_drift": bool(runtime_stamp_reasons),
        "dispatch_blocking_runtime_drift": dispatch_blocking_runtime_drift,
        "divergent": bool(divergence_reasons),
        "reasons": reasons,
        "divergence_reasons": divergence_reasons,
        "summary_zh": summary,
    }


def audit_full_clone_pool(root: Path) -> dict[str, Any]:
    pool = load_full_clone_pool(root)
    registry = _load_registry(root / TASK_REGISTRY_FILE)
    claims = _load_registry(root / CLAIMS_FILE)
    tasks_by_id = _tasks_by_id(registry)
    claims_by_candidate = _claims_by_candidate(claims)
    control_stamp = write_governance_runtime_stamp(root)
    dirty_runtime_paths = published_governance_runtime_dirty_paths(root)
    control_candidate_ids = _control_candidate_ids(root)
    slots = [
        assess_full_clone_slot_runtime(
            root,
            slot,
            tasks_by_id=tasks_by_id,
            claims_by_candidate=claims_by_candidate,
            control_stamp=control_stamp,
            control_candidate_ids=control_candidate_ids,
        )
        for slot in (pool.get("slots", []) or [])
    ]
    divergence_count = sum(1 for slot in slots if slot["divergent"])
    stale_runtime_count = sum(1 for slot in slots if slot["dispatch_blocking_runtime_drift"])
    quarantined_runtime_count = sum(1 for slot in slots if slot["quarantined"] and slot["runtime_drift"])
    quarantined_slot_count = sum(1 for slot in slots if slot["quarantined"])
    pool_status = str(pool.get("status") or "active")
    status = "blocked" if pool_status != "active" or divergence_count else "ready"
    return {
        "status": status,
        "pool_status": pool_status,
        "control_plane_root": str(root).replace("\\", "/"),
        "governance_runtime_stamp_file": str(GOVERNANCE_RUNTIME_STAMP_FILE).replace("\\", "/"),
        "governance_runtime_stamp": control_stamp,
        "governance_runtime_published": not bool(dirty_runtime_paths),
        "dirty_governance_runtime_paths": dirty_runtime_paths,
        "ledger_divergence_count": divergence_count,
        "stale_runtime_count": stale_runtime_count,
        "quarantined_runtime_count": quarantined_runtime_count,
        "quarantined_slot_count": quarantined_slot_count,
        "slots": slots,
    }


def detect_ledger_divergences(root: Path) -> list[dict[str, Any]]:
    audit = audit_full_clone_pool(root)
    return [
        {
            "slot_id": slot["slot_id"],
            "slot_status": slot["slot_status"],
            "slot_path": slot["slot_path"],
            "task_id": slot["task_id"],
            "candidate_id": slot["candidate_id"],
            "main_status": slot["main_status"],
            "clone_status": slot["clone_status"],
            "claim_status": slot["claim_status"],
            "reasons": list(slot["reasons"]),
            "summary_zh": slot["summary_zh"],
        }
        for slot in audit["slots"]
        if slot["divergent"]
    ]


def _valid_control_plane_root(path: Path) -> bool:
    return (path / CURRENT_TASK_FILE).exists() and (path / TASK_REGISTRY_FILE).exists()


def default_full_clone_idle_branch(slot_id: str) -> str:
    return f"codex/{slot_id}-idle"


def _origin_control_plane_root(local_root: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=local_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    raw = (result.stdout or "").strip()
    if result.returncode != 0 or not raw:
        return None
    if raw.startswith("file://"):
        raw = raw[7:]
    candidate = Path(raw).resolve()
    if candidate == local_root:
        return None
    return candidate if _valid_control_plane_root(candidate) else None


def resolve_control_plane_root(start: Path | None = None) -> Path:
    override = os.environ.get("AX9_CONTROL_PLANE_ROOT")
    if override:
        override_path = Path(override).resolve()
        if _valid_control_plane_root(override_path):
            return override_path
        raise GovernanceError(f"AX9_CONTROL_PLANE_ROOT is invalid: {override_path}")

    local_root = find_repo_root(start)
    current_path = (start or Path.cwd()).resolve()
    pool = load_full_clone_pool(local_root)
    control_plane_root = pool.get("control_plane_root")
    if not control_plane_root:
        origin_root = _origin_control_plane_root(local_root)
        return origin_root or local_root

    control_root = Path(str(control_plane_root)).resolve()
    if not _valid_control_plane_root(control_root):
        raise GovernanceError(f"full clone control_plane_root is invalid: {control_root}")

    for slot in pool.get("slots", []):
        slot_path = Path(str(slot.get("path") or "")).resolve()
        try:
            current_path.relative_to(slot_path)
        except ValueError:
            continue
        return control_root
    origin_root = _origin_control_plane_root(local_root)
    return origin_root or local_root


def find_full_clone_slot(pool: dict[str, Any], path: Path) -> dict[str, Any] | None:
    current_path = path.resolve()
    for slot in pool.get("slots", []):
        slot_path = Path(str(slot.get("path") or "")).resolve()
        try:
            current_path.relative_to(slot_path)
        except ValueError:
            continue
        return slot
    return None


def slot_by_id(pool: dict[str, Any], slot_id: str) -> dict[str, Any] | None:
    for slot in pool.get("slots", []):
        if slot.get("slot_id") == slot_id:
            return slot
    return None
