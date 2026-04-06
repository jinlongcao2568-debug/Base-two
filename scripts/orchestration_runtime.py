from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from task_publish_ops import build_publish_readiness
from governance_lib import (
    display_path,
    dump_yaml,
    dynamic_lane_ceiling,
    iso_now,
    load_current_task,
    load_task_policy,
    load_worktree_registry,
)
from governance_runtime import load_yaml


COORDINATION_RUNTIME_FILE = Path(".codex/local/COORDINATION_RUNTIME.yaml")
TASK_SOURCE_REGISTRY_FILE = Path("docs/governance/TASK_SOURCE_REGISTRY.yaml")
WORKER_REGISTRY_FILE = Path("docs/governance/WORKER_REGISTRY.yaml")
SUPPORTED_WORKER_KINDS = {"local"}
MAX_SESSION_HISTORY = 8


def _assess_continuation_readiness(root: Path) -> dict[str, Any]:
    from task_continuation_ops import assess_continuation_readiness

    readiness = assess_continuation_readiness(root)
    if readiness.get("status") == "blocked" and readiness.get("recommended_action") == "continue-current":
        readiness = dict(readiness)
        readiness["status"] = "continue-current"
    return readiness


def task_source_registry_defaults() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": None,
        "sources": [
            {
                "source_id": "doc_local",
                "kind": "doc_local",
                "enabled": True,
                "implemented": True,
                "status": "active",
                "adapter": "doc_local_v1",
                "poll_mode": "on_demand",
                "unsupported_in_v1": False,
                "notes": "Reads roadmap, ledgers, runlogs, handoffs, and policy files from the repository.",
            },
            {
                "source_id": "linear",
                "kind": "linear",
                "enabled": False,
                "implemented": False,
                "status": "disabled",
                "adapter": "planned",
                "poll_mode": "not_configured",
                "unsupported_in_v1": True,
                "notes": "Reserved for future external issue intake.",
            },
            {
                "source_id": "github_issues",
                "kind": "github_issues",
                "enabled": False,
                "implemented": False,
                "status": "disabled",
                "adapter": "planned",
                "poll_mode": "not_configured",
                "unsupported_in_v1": True,
                "notes": "Reserved for future external issue intake.",
            },
            {
                "source_id": "jira",
                "kind": "jira",
                "enabled": False,
                "implemented": False,
                "status": "disabled",
                "adapter": "planned",
                "poll_mode": "not_configured",
                "unsupported_in_v1": True,
                "notes": "Reserved for future external issue intake.",
            },
        ],
    }


def worker_registry_defaults() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": None,
        "workers": [
            {
                "worker_id": "worker-local-01",
                "kind": "local",
                "enabled": True,
                "status": "active",
                "host": "localhost",
                "workspace_root": ".",
                "capabilities": ["coordination", "execution"],
                "unsupported_in_v1": False,
                "last_heartbeat_at": None,
                "notes": "Single-machine worker used by the current coordinator.",
            }
        ],
    }


def runtime_defaults() -> dict[str, Any]:
    return {
        "version": "2.0",
        "updated_at": None,
        "session_cache": {},
        "runtime": {
            "mode": None,
            "status": "idle",
            "started_at": None,
            "last_tick_at": None,
            "last_reconcile_at": None,
            "current_command": None,
            "current_task_id": None,
            "current_lifecycle_summary": "idle",
            "stalled": False,
            "stall_reason": None,
        },
        "sessions": {
            "current_session_id": None,
            "recent_session_ids": [],
            "records": {},
        },
        "lease": {
            "current_task_id": None,
            "active_owner_session_id": None,
            "active_owner_state": "unclaimed",
            "tasks": {},
        },
        "workers": {
            "registry_file": str(WORKER_REGISTRY_FILE).replace("\\", "/"),
            "active_worker_ids": [],
            "entries": {},
        },
        "task_sources": {
            "registry_file": str(TASK_SOURCE_REGISTRY_FILE).replace("\\", "/"),
            "active_source_ids": [],
            "entries": {},
        },
        "execution": {
            "entries": {},
        },
    }


def _ensure_runtime_dir(root: Path) -> None:
    (root / COORDINATION_RUNTIME_FILE).parent.mkdir(parents=True, exist_ok=True)


def _load_registry(path: Path, defaults: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return defaults
    payload = load_yaml(path) or {}
    merged = dict(defaults)
    merged.update(payload)
    return merged


def load_task_source_registry(root: Path) -> dict[str, Any]:
    return _load_registry(root / TASK_SOURCE_REGISTRY_FILE, task_source_registry_defaults())


def load_worker_registry(root: Path) -> dict[str, Any]:
    return _load_registry(root / WORKER_REGISTRY_FILE, worker_registry_defaults())


def _normalize_runtime(root: Path, payload: dict[str, Any] | None) -> dict[str, Any]:
    runtime = runtime_defaults()
    if payload:
        runtime.update(payload)
    runtime["session_cache"] = dict(runtime.get("session_cache") or {})

    sessions = dict(runtime.get("sessions") or {})
    sessions.setdefault("current_session_id", None)
    sessions["recent_session_ids"] = list(sessions.get("recent_session_ids") or [])
    sessions["records"] = dict(sessions.get("records") or {})
    runtime["sessions"] = sessions

    lease_block = dict(runtime.get("lease") or {})
    legacy_leases = dict(runtime.get("leases") or {})
    lease_tasks = dict(lease_block.get("tasks") or {})
    if legacy_leases:
        lease_tasks.update({task_id: dict(entry or {}) for task_id, entry in legacy_leases.items()})
    lease_block["tasks"] = lease_tasks
    lease_block.setdefault("current_task_id", None)
    lease_block.setdefault("active_owner_session_id", None)
    lease_block.setdefault("active_owner_state", "unclaimed")
    runtime["lease"] = lease_block
    runtime.pop("leases", None)

    runtime_block = dict(runtime.get("runtime") or {})
    defaults = runtime_defaults()["runtime"]
    defaults.update(runtime_block)
    runtime["runtime"] = defaults

    execution_block = dict(runtime.get("execution") or {})
    execution_block["entries"] = dict(execution_block.get("entries") or {})
    runtime["execution"] = execution_block

    worker_runtime_entries = dict(((runtime.get("workers") or {}).get("entries") or {}))
    source_runtime_entries = dict(((runtime.get("task_sources") or {}).get("entries") or {}))
    runtime["workers"] = _workers_state_from_registry(load_worker_registry(root), worker_runtime_entries)
    runtime["task_sources"] = _task_sources_state_from_registry(load_task_source_registry(root), source_runtime_entries)
    return runtime


def load_orchestration_runtime(root: Path) -> dict[str, Any]:
    path = root / COORDINATION_RUNTIME_FILE
    payload = None if not path.exists() else load_yaml(path)
    return _normalize_runtime(root, payload)


def write_orchestration_runtime(root: Path, runtime: dict[str, Any]) -> None:
    _ensure_runtime_dir(root)
    normalized = _normalize_runtime(root, runtime)
    normalized["updated_at"] = iso_now()
    dump_yaml(root / COORDINATION_RUNTIME_FILE, normalized)


def current_thread_id(session_id: str | None = None) -> str:
    from os import environ

    return environ.get("CODEX_THREAD_ID") or session_id or "local-thread"


def runtime_status_for_task(task: dict[str, Any] | None) -> str:
    if task is None:
        return "idle"
    status = task.get("status")
    if status == "blocked":
        return "blocked"
    if status == "review":
        return "review_ready"
    if status in {"doing", "paused", "queued"}:
        return "active"
    if status == "done":
        return "idle"
    return "active"


def render_lifecycle_summary(current_payload: dict[str, Any]) -> str:
    if current_payload.get("status") == "idle":
        return f"idle :: {current_payload.get('next_action') or 'wait_for_successor_or_explicit_activation'}"
    return (
        f"{current_payload.get('current_task_id')} :: "
        f"{current_payload.get('status')}/{current_payload.get('worker_state')}"
    )


def refresh_lease_summary(runtime: dict[str, Any], current_task_id: str | None) -> None:
    lease_block = runtime.setdefault("lease", {})
    tasks = dict(lease_block.get("tasks") or {})
    current_task_id = current_task_id or None
    lease_block["current_task_id"] = current_task_id
    if current_task_id is None:
        lease_block["active_owner_session_id"] = None
        lease_block["active_owner_state"] = "unclaimed"
        lease_block["tasks"] = tasks
        return
    current_entry = tasks.get(current_task_id)
    if current_entry is None:
        lease_block["active_owner_session_id"] = None
        lease_block["active_owner_state"] = "unclaimed"
        lease_block["tasks"] = tasks
        return
    lease_block["active_owner_session_id"] = current_entry.get("owner_session_id")
    if current_entry.get("status") == "active":
        lease_block["active_owner_state"] = "active"
    elif current_entry.get("status") == "released":
        lease_block["active_owner_state"] = "released"
    else:
        lease_block["active_owner_state"] = current_entry.get("status") or "unclaimed"
    lease_block["tasks"] = tasks


def _task_sources_state_from_registry(
    registry: dict[str, Any], runtime_entries: dict[str, Any] | None = None
) -> dict[str, Any]:
    entries: dict[str, Any] = {}
    active_source_ids: list[str] = []
    for item in registry.get("sources", []):
        source = dict(item)
        source_id = str(source["source_id"])
        source_runtime = dict((runtime_entries or {}).get(source_id) or {})
        observed_status = "active" if source.get("enabled") and source.get("implemented") else "disabled"
        if source.get("unsupported_in_v1"):
            observed_status = "disabled"
        if source_runtime.get("observed_status"):
            observed_status = source_runtime["observed_status"]
        source.update(source_runtime)
        source["observed_status"] = observed_status
        entries[source_id] = source
        if observed_status == "active":
            active_source_ids.append(source_id)
    return {
        "registry_file": str(TASK_SOURCE_REGISTRY_FILE).replace("\\", "/"),
        "active_source_ids": active_source_ids,
        "entries": entries,
    }


def _workers_state_from_registry(
    registry: dict[str, Any], runtime_entries: dict[str, Any] | None = None
) -> dict[str, Any]:
    entries: dict[str, Any] = {}
    active_worker_ids: list[str] = []
    for item in registry.get("workers", []):
        worker = dict(item)
        worker_id = str(worker["worker_id"])
        worker_runtime = dict((runtime_entries or {}).get(worker_id) or {})
        kind = str(worker.get("kind") or "unknown")
        if not worker.get("enabled"):
            observed_status = "disabled"
        elif kind not in SUPPORTED_WORKER_KINDS or worker.get("unsupported_in_v1"):
            observed_status = "unsupported_in_v1"
        else:
            observed_status = worker.get("status") or "active"
        if worker_runtime.get("observed_status"):
            observed_status = worker_runtime["observed_status"]
        worker.update(worker_runtime)
        worker["observed_status"] = observed_status
        entries[worker_id] = worker
        if observed_status == "active":
            active_worker_ids.append(worker_id)
    return {
        "registry_file": str(WORKER_REGISTRY_FILE).replace("\\", "/"),
        "active_worker_ids": active_worker_ids,
        "entries": entries,
    }


def sync_runtime_support_surfaces(root: Path, runtime: dict[str, Any]) -> None:
    worker_runtime_entries = dict(((runtime.get("workers") or {}).get("entries") or {}))
    source_runtime_entries = dict(((runtime.get("task_sources") or {}).get("entries") or {}))
    runtime["workers"] = _workers_state_from_registry(load_worker_registry(root), worker_runtime_entries)
    runtime["task_sources"] = _task_sources_state_from_registry(load_task_source_registry(root), source_runtime_entries)


def execution_runtime_defaults() -> dict[str, Any]:
    return {
        "lane_session_id": None,
        "executor_status": "prepared",
        "started_at": None,
        "last_heartbeat_at": None,
        "last_result": None,
    }


def load_execution_runtime_entry(root: Path, task_id: str) -> dict[str, Any]:
    runtime = load_orchestration_runtime(root)
    entry = dict(runtime.get("execution", {}).get("entries", {}).get(task_id) or {})
    normalized = execution_runtime_defaults()
    normalized.update(entry)
    return normalized


def update_execution_runtime_entry(root: Path, task_id: str, **fields: Any) -> dict[str, Any]:
    runtime = load_orchestration_runtime(root)
    execution_block = runtime.setdefault("execution", {})
    entries = execution_block.setdefault("entries", {})
    entry = execution_runtime_defaults()
    entry.update(dict(entries.get(task_id) or {}))
    for key, value in fields.items():
        if value is not None:
            entry[key] = value
    entries[task_id] = entry
    write_orchestration_runtime(root, runtime)
    return entry


def record_worker_heartbeat(
    root: Path,
    worker_id: str,
    *,
    timestamp: str | None = None,
    observed_status: str | None = None,
) -> dict[str, Any]:
    runtime = load_orchestration_runtime(root)
    workers_block = runtime.setdefault("workers", {})
    entries = workers_block.setdefault("entries", {})
    entry = dict(entries.get(worker_id) or {})
    if timestamp is not None:
        entry["last_heartbeat_at"] = timestamp
    if observed_status is not None:
        entry["observed_status"] = observed_status
    entries[worker_id] = entry
    write_orchestration_runtime(root, runtime)
    return entry


def record_session_event(
    root: Path,
    *,
    session_id: str,
    thread_id: str,
    current_command: str,
    mode: str,
    writer_state: str,
    current_task_id: str | None,
    continue_intent: str | None,
    runtime_status: str,
    blocked_reason: str | None = None,
    safe_write: bool = False,
    reconcile: bool = False,
) -> None:
    runtime = load_orchestration_runtime(root)
    current_payload = load_current_task(root)
    now = iso_now()

    runtime_block = runtime["runtime"]
    if runtime_block.get("started_at") is None:
        runtime_block["started_at"] = now
    runtime_block["mode"] = mode
    runtime_block["status"] = runtime_status
    runtime_block["last_tick_at"] = now
    if reconcile:
        runtime_block["last_reconcile_at"] = now
    runtime_block["current_command"] = current_command
    runtime_block["current_task_id"] = current_task_id
    runtime_block["current_lifecycle_summary"] = render_lifecycle_summary(current_payload)
    runtime_block["stalled"] = runtime_status in {"blocked", "error"}
    runtime_block["stall_reason"] = blocked_reason if runtime_block["stalled"] else None

    sessions = runtime["sessions"]
    sessions["current_session_id"] = session_id
    recent_session_ids = [session_id, *[item for item in sessions["recent_session_ids"] if item != session_id]]
    sessions["recent_session_ids"] = recent_session_ids[:MAX_SESSION_HISTORY]

    record = dict(sessions["records"].get(session_id) or {})
    if record.get("started_at") is None:
        record["started_at"] = now
    if safe_write and record.get("last_safe_write_at") is None:
        record["last_safe_write_at"] = now
    record.update(
        {
            "session_id": session_id,
            "thread_id": thread_id,
            "mode": mode,
            "writer_state": writer_state,
            "current_task_id": current_task_id,
            "current_command": current_command,
            "continue_intent": continue_intent,
            "last_event_at": now,
            "runtime_status": runtime_status,
            "blocked_reason": blocked_reason,
        }
    )
    if safe_write:
        record["last_safe_write_at"] = now
    sessions["records"][session_id] = record

    refresh_lease_summary(runtime, current_task_id or current_payload.get("current_task_id"))
    sync_runtime_support_surfaces(root, runtime)
    write_orchestration_runtime(root, runtime)


def _candidate_summary(root: Path) -> dict[str, Any]:
    index_path = root / ".codex/local/coordination_candidates/index.yaml"
    if not index_path.exists():
        return {
            "index_file": str(index_path).replace("\\", "/"),
            "generated_at": None,
            "candidate_count": 0,
            "candidate_ids": [],
        }
    payload = load_yaml(index_path) or {}
    return {
        "index_file": str(index_path).replace("\\", "/"),
        "generated_at": payload.get("generated_at"),
        "candidate_count": int(payload.get("candidate_count") or 0),
        "candidate_ids": list(payload.get("candidate_ids") or []),
    }


def _runner_pressure(root: Path) -> dict[str, Any]:
    current_payload = load_current_task(root)
    if current_payload.get("status") == "idle":
        return {
            "lane_count": 0,
            "planner_ceiling": 0,
            "budget_cap": 0,
            "active_execution_entries": 0,
            "cleanup_pressure_count": 0,
            "cleanup_pressure_applied": False,
            "effective_lane_budget": 0,
        }

    task_policy = load_task_policy(root)
    worktrees = load_worktree_registry(root)
    lane_count = int(current_payload.get("lane_count") or 1)
    planner_ceiling = dynamic_lane_ceiling(task_policy)
    budget_cap = min(lane_count, planner_ceiling)
    active_execution_entries = len(
        [
            entry
            for entry in worktrees.get("entries", [])
            if entry.get("work_mode") == "execution" and entry.get("status") == "active"
        ]
    )
    cleanup_pressure_count = len(
        [
            entry
            for entry in worktrees.get("entries", [])
            if entry.get("work_mode") == "execution"
            and entry.get("cleanup_state") in {"blocked", "blocked_manual"}
        ]
    )
    cleanup_pressure_applied = cleanup_pressure_count > 0 and budget_cap > 1
    effective_lane_budget = budget_cap - 1 if cleanup_pressure_applied else budget_cap
    return {
        "lane_count": lane_count,
        "planner_ceiling": planner_ceiling,
        "budget_cap": budget_cap,
        "active_execution_entries": active_execution_entries,
        "cleanup_pressure_count": cleanup_pressure_count,
        "cleanup_pressure_applied": cleanup_pressure_applied,
        "effective_lane_budget": max(0, effective_lane_budget),
    }


def build_orchestration_status(root: Path) -> dict[str, Any]:
    runtime = load_orchestration_runtime(root)
    current_payload = load_current_task(root)
    refresh_lease_summary(runtime, current_payload.get("current_task_id"))
    runtime_block = dict(runtime["runtime"])
    if current_payload.get("current_task_id") and runtime_block.get("current_task_id") is None:
        runtime_block["current_task_id"] = current_payload.get("current_task_id")
        runtime_block["current_lifecycle_summary"] = render_lifecycle_summary(current_payload)
        runtime_block["status"] = runtime_status_for_task(current_payload)
        runtime_block["mode"] = runtime_block.get("mode") or "manual"
    elif current_payload.get("status") == "idle" and runtime_block.get("current_task_id") is None:
        runtime_block["current_lifecycle_summary"] = render_lifecycle_summary(current_payload)
    return {
        "runtime": runtime_block,
        "lease": runtime["lease"],
        "sessions": runtime["sessions"],
        "workers": runtime["workers"],
        "task_sources": runtime["task_sources"],
        "publish_readiness": build_publish_readiness(root),
        "continuation_readiness": _assess_continuation_readiness(root),
        "current_task": current_payload,
        "candidate_summary": _candidate_summary(root),
        "runner_pressure": _runner_pressure(root),
    }


def render_status(status: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(status, ensure_ascii=False, indent=2)
    return yaml.safe_dump(status, allow_unicode=True, sort_keys=False)
