from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

from governance_lib import GovernanceError, configure_utf8_stdio, find_repo_root, git, load_task_registry
from governance_lib import hidden_subprocess_kwargs
from control_plane_root import resolve_control_plane_root

SCRIPT_DIR = Path(__file__).resolve().parent


def _run_task_ops(control_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python", str(SCRIPT_DIR / "task_ops.py"), *args],
        cwd=control_root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        **hidden_subprocess_kwargs(),
    )


def _task_by_branch(registry: dict[str, Any], branch: str) -> dict[str, Any] | None:
    for task in registry.get("tasks", []):
        if task.get("branch") == branch:
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


def _worker_id(local_root: Path) -> str:
    name = local_root.name.strip()
    return name or "worker-local"


def _task_summary(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task.get("task_id"),
        "status": task.get("status"),
        "branch": task.get("branch"),
        "stage": task.get("stage"),
        "planned_write_paths": list(task.get("planned_write_paths") or []),
        "required_tests": list(task.get("required_tests") or []),
    }


def preview_worker_action(local_root: Path, *, explicit_task_id: str | None = None) -> dict[str, Any]:
    control_root = resolve_control_plane_root(local_root)
    registry = load_task_registry(control_root)
    current_branch = _current_branch(local_root)
    task = _task_by_branch(registry, current_branch)
    if task is None and explicit_task_id:
        task = _task_by_id(registry, explicit_task_id)

    if task is None:
        return {
            "status": "ready",
            "mode": "claim-next",
            "worker_id": _worker_id(local_root),
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": "this clone can claim the next task through the main task ledger",
            "task": None,
        }
    if task.get("status") in {"doing", "paused"}:
        if current_branch != task.get("branch"):
            return {
                "status": "ready",
                "mode": "switch-and-resume",
                "worker_id": _worker_id(local_root),
                "control_root": str(control_root).replace("\\", "/"),
                "explanation": f"switch to `{task['branch']}` and continue `{task['task_id']}`",
                "task": _task_summary(task),
            }
        return {
            "status": "ready",
            "mode": "resume-current",
            "worker_id": _worker_id(local_root),
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"continue `{task['task_id']}` in the current clone",
            "task": _task_summary(task),
        }
    if task.get("status") == "blocked":
        return {
            "status": "blocked",
            "mode": "blocked-current",
            "worker_id": _worker_id(local_root),
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"task `{task['task_id']}` is blocked",
            "task": _task_summary(task),
            "blockers": [task.get("blocked_reason") or "blocked without recorded reason"],
        }
    if task.get("status") == "review":
        return {
            "status": "blocked",
            "mode": "await-review-closeout",
            "worker_id": _worker_id(local_root),
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"task `{task['task_id']}` is awaiting closeout",
            "task": _task_summary(task),
        }
    if task.get("status") == "done":
        return {
            "status": "ready",
            "mode": "claim-next",
            "worker_id": _worker_id(local_root),
            "control_root": str(control_root).replace("\\", "/"),
            "explanation": f"task `{task['task_id']}` is done; this clone can claim the next task",
            "task": _task_summary(task),
        }
    return {
        "status": "blocked",
        "mode": "unsupported",
        "worker_id": _worker_id(local_root),
        "control_root": str(control_root).replace("\\", "/"),
        "explanation": f"task `{task['task_id']}` is in unsupported state `{task.get('status')}`",
        "task": _task_summary(task),
        "blockers": [f"unsupported task status: {task.get('status')}"],
    }


def _claim_next_for_clone(control_root: Path, local_root: Path) -> subprocess.CompletedProcess[str]:
    return _run_task_ops(
        control_root,
        "claim-next",
        "--promote-task",
        "--dispatch-target",
        "main_ledger",
        "--worktree-root",
        str(local_root),
        "--window-id",
        _worker_id(local_root),
    )


def run_worker_once(local_root: Path, *, explicit_task_id: str | None = None) -> dict[str, Any]:
    control_root = resolve_control_plane_root(local_root)
    decision = preview_worker_action(local_root, explicit_task_id=explicit_task_id)
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
    if mode == "claim-next":
        claim = _claim_next_for_clone(control_root, local_root)
        if claim.returncode != 0:
            return {
                "status": "blocked",
                "mode": "claim-blocked",
                "worker_id": _worker_id(local_root),
                "control_root": str(control_root).replace("\\", "/"),
                "explanation": "this clone could not claim a new task",
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
    parser = argparse.ArgumentParser(description="AX9 clone worker self-loop")
    subparsers = parser.add_subparsers(dest="command", required=True)
    once = subparsers.add_parser("once")
    once.add_argument("--task-id")
    once.set_defaults(func=cmd_once)
    loop = subparsers.add_parser("loop")
    loop.add_argument("--task-id")
    loop.add_argument("--cycles", type=int, default=0)
    loop.add_argument("--interval-seconds", type=int, default=30)
    loop.set_defaults(func=cmd_loop)
    return parser


def main() -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
