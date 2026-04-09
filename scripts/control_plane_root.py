from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any

from governance_lib import CURRENT_TASK_FILE, GovernanceError, TASK_REGISTRY_FILE, find_repo_root, load_yaml


FULL_CLONE_POOL_FILE = Path("docs/governance/FULL_CLONE_POOL.yaml")
CLAIMS_FILE = Path(".codex/local/roadmap_candidates/claims.yaml")


def load_full_clone_pool(root: Path) -> dict[str, Any]:
    path = root / FULL_CLONE_POOL_FILE
    if not path.exists():
        return {}
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"full clone pool must be a mapping: {FULL_CLONE_POOL_FILE}")
    payload.setdefault("slots", [])
    return payload


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


def detect_ledger_divergences(root: Path) -> list[dict[str, Any]]:
    registry = _load_registry(root / TASK_REGISTRY_FILE)
    pool = load_full_clone_pool(root)
    claims = _load_registry(root / CLAIMS_FILE)
    tasks_by_id = _tasks_by_id(registry)
    claims_by_candidate = {
        str(claim.get("candidate_id")): claim
        for claim in (claims or {}).get("claims", []) or []
        if claim.get("candidate_id")
    }
    divergences: list[dict[str, Any]] = []
    seen: set[tuple[str, str | None, str | None]] = set()

    def _record(slot_id: str, task_id: str | None, candidate_id: str | None, summary: str, reasons: list[str]) -> None:
        key = (slot_id, task_id, summary)
        if key in seen:
            return
        seen.add(key)
        claim = claims_by_candidate.get(str(candidate_id)) if candidate_id else None
        divergences.append(
            {
                "slot_id": slot_id,
                "slot_status": slot_status,
                "slot_path": None if slot_path is None else str(slot_path).replace("\\", "/"),
                "task_id": task_id,
                "candidate_id": candidate_id,
                "main_status": None if task_id is None else tasks_by_id.get(task_id, {}).get("status"),
                "clone_status": None if task_id is None else clone_tasks_by_id.get(task_id, {}).get("status"),
                "claim_status": None if claim is None else claim.get("status"),
                "reasons": reasons,
                "summary_zh": summary,
            }
        )

    for slot in (pool or {}).get("slots", []) or []:
        slot_id = str(slot.get("slot_id") or "-")
        slot_status = str(slot.get("status") or "-")
        slot_path_raw = str(slot.get("path") or "").strip()
        slot_path = Path(slot_path_raw).resolve() if slot_path_raw else None
        clone_registry = _load_registry(slot_path / TASK_REGISTRY_FILE) if slot_path else {}
        clone_tasks_by_id = _tasks_by_id(clone_registry)
        clone_only_task_ids = [task_id for task_id in clone_tasks_by_id if task_id not in tasks_by_id]
        for task_id in clone_only_task_ids:
            clone_task = clone_tasks_by_id.get(task_id) or {}
            candidate_id = clone_task.get("roadmap_candidate_id")
            summary = "主控制面缺少 clone-only 任务记录。"
            _record(
                slot_id,
                task_id,
                candidate_id,
                summary,
                [summary],
            )

        task_id = str(slot.get("current_task_id") or "")
        if not task_id:
            continue
        main_task = tasks_by_id.get(task_id)
        clone_task = clone_tasks_by_id.get(task_id)
        candidate_id = None
        if main_task:
            candidate_id = main_task.get("roadmap_candidate_id")
        elif clone_task:
            candidate_id = clone_task.get("roadmap_candidate_id")
        reasons: list[str] = []
        if main_task is None:
            reasons.append("主控制面缺少当前执行任务记录。")
        if clone_task is None:
            reasons.append("工作树镜像里缺少当前执行任务记录。")
        if main_task and clone_task and main_task.get("status") != clone_task.get("status"):
            reasons.append(f"主账本状态为 {main_task.get('status')}，工作树状态为 {clone_task.get('status')}。")
        if main_task and clone_task and main_task.get("worker_state") != clone_task.get("worker_state"):
            reasons.append(
                f"主账本 worker_state 为 {main_task.get('worker_state')}，工作树为 {clone_task.get('worker_state')}。"
            )
        if main_task and main_task.get("status") == "done":
            if slot_status != "ready" or slot.get("current_task_id"):
                reasons.append("主账本已关闭，但 full clone slot 尚未释放。")
            claim = claims_by_candidate.get(str(candidate_id)) if candidate_id else None
            if claim and claim.get("status") != "closed":
                reasons.append(f"主账本已关闭，但 claim 仍为 {claim.get('status') or 'unknown'}。")
        if clone_task and clone_task.get("status") == "done" and main_task and main_task.get("status") != "done":
            reasons.append("工作树已关闭，但主控制面尚未完成同一任务。")
        if reasons:
            _record(
                slot_id,
                task_id,
                candidate_id,
                reasons[0],
                reasons,
            )
    return divergences


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
