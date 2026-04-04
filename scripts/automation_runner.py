from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import time

from governance_lib import (
    GovernanceError,
    find_repo_root,
    load_current_task,
    load_task_registry,
    load_worktree_registry,
    runner_action_gate,
    worktree_map,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def run_step(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=root,
        text=True,
        capture_output=True,
    )


def task_ops(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = SCRIPT_DIR / "task_ops.py"
    return run_step(root, str(script), *args)


def python_script(root: Path, script_name: str) -> subprocess.CompletedProcess[str]:
    script = SCRIPT_DIR / script_name
    return run_step(root, str(script))


def default_worktree_root(root: Path) -> Path:
    return root.parent / f"{root.name}.worktrees"


def prepare_parallel_worktrees(root: Path, current_task_id: str, worktree_root: Path) -> list[str]:
    registry = load_task_registry(root)
    entries = worktree_map(load_worktree_registry(root))
    created: list[str] = []
    for task in registry.get("tasks", []):
        if task.get("parent_task_id") != current_task_id or task["task_kind"] != "execution":
            continue
        if task["task_id"] in entries:
            continue
        destination = worktree_root / task["task_id"]
        result = task_ops(root, "worktree-create", task["task_id"], "--path", str(destination))
        if result.returncode != 0:
            raise GovernanceError(result.stdout.strip() or result.stderr.strip())
        created.append(task["task_id"])
    return created


def coordinator_cycle(root: Path, worktree_root: Path, prepare_worktrees: bool) -> int:
    current_task = load_current_task(root)
    gate = runner_action_gate(current_task)
    results = [
        python_script(root, "check_repo.py"),
        python_script(root, "check_hygiene.py"),
    ]
    exit_code = 0
    for result in results:
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        if result.returncode != 0:
            exit_code = result.returncode
    if exit_code != 0:
        return exit_code

    if prepare_worktrees and current_task["topology"] == "parallel_parent" and gate["prepare_worktrees"]:
        created = prepare_parallel_worktrees(root, current_task["current_task_id"], worktree_root)
        for task_id in created:
            print(f"[OK] prepared worktree for {task_id}")
    elif prepare_worktrees and current_task["topology"] == "parallel_parent":
        print(f"[SKIP] prepare-worktrees skipped: {gate['reason']}")

    if current_task["topology"] == "parallel_parent" and gate["auto_close_children"]:
        result = task_ops(root, "auto-close-children", current_task["current_task_id"])
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        if result.returncode != 0:
            exit_code = result.returncode
    elif current_task["topology"] == "parallel_parent":
        print(f"[SKIP] auto-close-children skipped: {gate['reason']}")

    cleanup = task_ops(root, "cleanup-orphans")
    if cleanup.stdout.strip():
        print(cleanup.stdout.strip())
    if cleanup.stderr.strip():
        print(cleanup.stderr.strip())
    if cleanup.returncode != 0 and exit_code == 0:
        exit_code = cleanup.returncode
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="AX9S automation runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    once_parser = subparsers.add_parser("once")
    once_parser.add_argument("--worktree-root")
    once_parser.add_argument("--prepare-worktrees", action="store_true")

    loop_parser = subparsers.add_parser("loop")
    loop_parser.add_argument("--worktree-root")
    loop_parser.add_argument("--prepare-worktrees", action="store_true")
    loop_parser.add_argument("--interval-seconds", type=int, default=60)
    loop_parser.add_argument("--cycles", type=int, default=0)

    args = parser.parse_args()
    try:
        root = find_repo_root()
        worktree_root = Path(args.worktree_root).resolve() if args.worktree_root else default_worktree_root(root)
        if args.command == "once":
            return coordinator_cycle(root, worktree_root, args.prepare_worktrees)
        cycle = 0
        while True:
            cycle += 1
            result = coordinator_cycle(root, worktree_root, args.prepare_worktrees)
            if result != 0:
                return result
            if args.cycles and cycle >= args.cycles:
                return 0
            time.sleep(args.interval_seconds)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
