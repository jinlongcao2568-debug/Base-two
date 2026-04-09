from __future__ import annotations

from typing import Any

from governance_lib import GovernanceError, load_task_registry, missing_required_tests
from control_plane_root import resolve_control_plane_root


def list_closeout_ready_execution_tasks(root) -> list[dict[str, Any]]:
    registry = load_task_registry(root)
    candidates: list[dict[str, Any]] = []
    for task in registry.get("tasks", []):
        if task.get("task_kind") != "execution":
            continue
        if task.get("parent_task_id") is not None:
            continue
        if not task.get("roadmap_candidate_id"):
            continue
        if task.get("status") != "review":
            continue
        if missing_required_tests(root, task):
            continue
        candidates.append(task)
    return sorted(candidates, key=lambda item: str(item.get("last_reported_at") or ""))


def close_ready_execution_tasks(root) -> dict[str, Any]:
    closed: list[str] = []
    blocked: list[str] = []
    import argparse
    from task_lifecycle_ops import cmd_close

    for task in list_closeout_ready_execution_tasks(root):
        try:
            cmd_close(argparse.Namespace(task_id=task["task_id"]))
            closed.append(task["task_id"])
        except GovernanceError as error:
            blocked.append(f"{task['task_id']}: {error}")
    return {"closed_task_ids": closed, "blocked": blocked}


def main() -> int:
    root = resolve_control_plane_root()
    payload = close_ready_execution_tasks(root)
    if payload["closed_task_ids"]:
        print(f"[OK] closed ready execution tasks: {', '.join(payload['closed_task_ids'])}")
    else:
        print("[OK] no ready execution tasks closed")
    for item in payload["blocked"]:
        print(f"[BLOCKED] {item}")
    return 0 if not payload["blocked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
