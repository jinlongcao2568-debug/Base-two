from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from governance_lib import CURRENT_TASK_FILE, GovernanceError, TASK_REGISTRY_FILE, find_repo_root, load_yaml


FULL_CLONE_POOL_FILE = Path("docs/governance/FULL_CLONE_POOL.yaml")


def load_full_clone_pool(root: Path) -> dict[str, Any]:
    path = root / FULL_CLONE_POOL_FILE
    if not path.exists():
        return {}
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"full clone pool must be a mapping: {FULL_CLONE_POOL_FILE}")
    payload.setdefault("slots", [])
    return payload


def _valid_control_plane_root(path: Path) -> bool:
    return (path / CURRENT_TASK_FILE).exists() and (path / TASK_REGISTRY_FILE).exists()


def default_full_clone_idle_branch(slot_id: str) -> str:
    return f"codex/{slot_id}-idle"


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
        return local_root

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
    return local_root


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
