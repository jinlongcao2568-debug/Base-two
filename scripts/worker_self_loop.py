from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

from control_plane_root import default_full_clone_idle_branch, find_full_clone_slot, load_full_clone_pool, resolve_control_plane_root
from governance_lib import GovernanceError, configure_utf8_stdio, find_repo_root, git, load_task_registry

SCRIPT_DIR = Path(__file__).resolve().parent


def _run_task_ops(control_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python", str(SCRIPT_DIR / "task_ops.py"), *args],
        cwd=control_root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def _task_by_branch(registry: dict[str, Any], branch: str) -> dict[str, Any] | None:
    for task in registry.get("tasks", []):
        if task.get("task_kind") == "execution" and task.get("branch") == branch:
            return task
    return None


def _task_by_id(registry: dict[str, Any], task_id: str | None) -> dict[str, Any] | None:
    if not task_id:
        return None
    for task in registry.get("tasks", []):
        if task.get("task_id") == task_id:
            return task
    return None


def _current_branch(local_root: Path) -> str:
    return git(local_root, "branch", "--show-current").stdout.strip()


def _switch_branch(local_root: Path, branch: str) -> None:
    git(local_root, "fetch", "--all", check=False)
    result = git(local_root, "switch", branch, check=False)
    if result.returncode == 0:
        return
    create = git(local_root, "switch", "-c", branch, check=False)
    if create.returncode != 0:
        raise GovernanceError(create.stderr.strip() or create.stdout.strip() or f"unable to switch clone to {branch}")


def _idle_branch(slot: dict[str, Any]) -> str:
    return str(slot.get("idle_branch") or default_full_clone_idle_branch(slot["slot_id"]))


def _task_summary(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task["task_id"],
        "status": task["status"],
        "branch": task["branch"],
        "stage": task["stage"],
        "planned_write_paths": list(task.get("planned_write_paths") or []),
        "required_tests": list(task.get("required_tests") or []),
    }


def preview_worker_action(local_root: Path, *, explicit_task_id: str | None = None) -> dict[str, Any]:
    control_root = resolve_control_plane_root(local_root)
    pool = load_full_clone_pool(control_root)
    slot = find_full_clone_slot(pool, local_root)
    if slot is None:
        raise GovernanceError("current directory is not a configured full clone worker slot")

    registry = load_task_registry(control_root)
    current_branch = _current_branch(local_root)
    task = _task_by_branch(registry, current_branch)
    if task is None and slot.get("current_task_id"):
        task = _task_by_id(registry, str(slot["current_task_id"]))
    if task is None and explicit_task_id:
        task = _task_by_id(registry, explicit_task_id)
    if task is None:
        return {
            "status": "ready",
            "mode": "claim-next",
            "slot_id": slot["slot_id"],
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"slot `{slot['slot_id']}` is idle and can claim the next roadmap task",
            "task": None,
        }
    if task["status"] in {"doing", "paused"}:
        if current_branch != task["branch"]:
            return {
                "status": "ready",
                "mode": "switch-and-resume",
                "slot_id": slot["slot_id"],
                "control_root": str(control_root).replace("\\", "/"),
                "explanation": f"slot `{slot['slot_id']}` should switch from `{current_branch}` to `{task['branch']}`",
                "task": _task_summary(task),
            }
        return {
            "status": "ready",
            "mode": "resume-current",
            "slot_id": slot["slot_id"],
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"resume current task `{task['task_id']}`",
            "task": _task_summary(task),
        }
    if task["status"] == "blocked":
        return {
            "status": "blocked",
            "mode": "blocked-current",
            "slot_id": slot["slot_id"],
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"task `{task['task_id']}` is blocked",
            "task": _task_summary(task),
            "blockers": [task.get("blocked_reason") or "blocked without recorded reason"],
        }
    if task["status"] == "review":
        can_close = _run_task_ops(control_root, "can-close", task["task_id"])
        if can_close.returncode == 0:
            return {
                "status": "ready",
                "mode": "await-coordinator-closeout",
                "slot_id": slot["slot_id"],
                "control_root": str(control_root).replace("\\", "/"),
                "explanation": f"task `{task['task_id']}` is review-ready and awaiting coordinator closeout",
                "task": _task_summary(task),
            }
        return {
            "status": "blocked",
            "mode": "review-blocked",
            "slot_id": slot["slot_id"],
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"task `{task['task_id']}` is in review but cannot close yet",
            "task": _task_summary(task),
            "blockers": [can_close.stdout.strip() or can_close.stderr.strip() or "can-close failed"],
        }
    if task["status"] == "done":
        return {
            "status": "ready",
            "mode": "claim-next",
            "slot_id": slot["slot_id"],
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"task `{task['task_id']}` is already done; switch to idle branch and claim next",
            "task": _task_summary(task),
        }
    return {
        "status": "blocked",
        "mode": "unsupported",
        "slot_id": slot["slot_id"],
        "control_root": str(control_root).replace("\\", "/"),
        "explanation": f"task `{task['task_id']}` is in unsupported worker state `{task['status']}`",
        "task": _task_summary(task),
        "blockers": [f"unsupported task status: {task['status']}"],
    }


def _claim_next_for_slot(control_root: Path, slot: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    return _run_task_ops(
        control_root,
        "claim-next",
        "--promote-task",
        "--dispatch-target",
        "full_clone",
        "--full-clone-slot-id",
        slot["slot_id"],
        "--window-id",
        slot["slot_id"],
    )


def _refresh_slot(control_root: Path, local_root: Path) -> dict[str, Any]:
    pool = load_full_clone_pool(control_root)
    slot = find_full_clone_slot(pool, local_root)
    if slot is None:
        raise GovernanceError("current directory is not a configured full clone worker slot")
    return slot


def run_worker_once(local_root: Path, *, explicit_task_id: str | None = None) -> dict[str, Any]:
    control_root = resolve_control_plane_root(local_root)
    decision = preview_worker_action(local_root, explicit_task_id=explicit_task_id)
    slot = _refresh_slot(control_root, local_root)
    mode = decision["mode"]
    if decision["status"] != "ready":
        return decision
    if mode == "switch-and-resume":
        task = decision["task"]
        _switch_branch(local_root, task["branch"])
        decision["mode"] = "resume-current"
        decision["explanation"] = f"switched to `{task['branch']}` and resumed `{task['task_id']}`"
        return decision
    if mode == "resume-current":
        return decision
    if mode == "await-coordinator-closeout":
        return decision
    if mode == "claim-next":
        idle_branch = _idle_branch(slot)
        if _current_branch(local_root) != idle_branch:
            _switch_branch(local_root, idle_branch)
        claim = _claim_next_for_slot(control_root, slot)
        if claim.returncode != 0:
            return {
                "status": "blocked",
                "mode": "claim-blocked",
                "slot_id": slot["slot_id"],
                "control_root": str(control_root).replace("\\", "/"),
                "explanation": "slot could not claim a new roadmap task",
                "blockers": [claim.stdout.strip() or claim.stderr.strip() or "claim-next failed"],
            }
        updated = preview_worker_action(local_root)
        if updated.get("task"):
            _switch_branch(local_root, updated["task"]["branch"])
        return updated
    return decision


def cmd_once(args: argparse.Namespace) -> int:
    local_root = find_repo_root()
    result = run_worker_once(local_root, explicit_task_id=args.task_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready" else 1


def cmd_loop(args: argparse.Namespace) -> int:
    local_root = find_repo_root()
    cycles = int(args.cycles)
    interval = max(1, int(args.interval_seconds))
    cycle = 0
    while True:
        cycle += 1
        result = run_worker_once(local_root, explicit_task_id=args.task_id)
        print(json.dumps({"cycle": cycle, **result}, ensure_ascii=False, indent=2))
        if cycles and cycle >= cycles:
            return 0 if result["status"] == "ready" else 1
        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S clone worker self-loop")
    subparsers = parser.add_subparsers(dest="command", required=True)
    once = subparsers.add_parser("once")
    once.add_argument("--task-id")
    once.set_defaults(func=cmd_once)

    loop = subparsers.add_parser("loop")
    loop.add_argument("--task-id")
    loop.add_argument("--interval-seconds", type=int, default=60)
    loop.add_argument("--cycles", type=int, default=0)
    loop.set_defaults(func=cmd_loop)
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
