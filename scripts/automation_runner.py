from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import time

from governance_lib import (
    collect_active_execution_errors,
    collect_split_errors,
    dynamic_lane_ceiling,
    GovernanceError,
    find_repo_root,
    load_current_task,
    load_task_policy,
    load_task_registry,
    load_worktree_registry,
    runner_action_gate,
    task_map,
    worktree_map,
)


SCRIPT_DIR = Path(__file__).resolve().parent
METRIC_KEYS = (
    "lane_count",
    "lane_conflict_count",
    "child_closeout_success_rate",
    "fallback_count",
    "orphan_cleanup_failures",
)


def run_step(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def task_ops(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_step(root, str(SCRIPT_DIR / "task_ops.py"), *args)


def python_script(root: Path, script_name: str) -> subprocess.CompletedProcess[str]:
    return run_step(root, str(SCRIPT_DIR / script_name))


def default_worktree_root(root: Path) -> Path:
    return root.parent / f"{root.name}.worktrees"


def _emit_step_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())


def _lane_sort_key(task: dict[str, object]) -> tuple[int, int, str]:
    lane_index = task.get("lane_index")
    normalized = int(lane_index) if isinstance(lane_index, int) else sys.maxsize
    return (0 if isinstance(lane_index, int) else 1, normalized, str(task["task_id"]))


def _parallel_children(registry: dict[str, object], parent_task_id: str) -> list[dict[str, object]]:
    children = [
        task
        for task in registry.get("tasks", [])
        if task.get("parent_task_id") == parent_task_id and task.get("task_kind") == "execution"
    ]
    return sorted(children, key=_lane_sort_key)


def _active_execution_entries(worktree_registry: dict[str, object]) -> list[dict[str, object]]:
    return [
        entry
        for entry in worktree_registry.get("entries", [])
        if entry.get("work_mode") == "execution" and entry.get("status") == "active"
    ]


def _cleanup_failures(worktree_registry: dict[str, object]) -> list[dict[str, object]]:
    return [
        entry
        for entry in worktree_registry.get("entries", [])
        if entry.get("work_mode") == "execution" and entry.get("cleanup_state") in {"blocked", "blocked_manual"}
    ]


def _parallel_registry_errors(parent: dict[str, object], children: list[dict[str, object]]) -> list[str]:
    if parent.get("topology") != "parallel_parent":
        return []
    parent_lane_count = int(parent.get("lane_count") or 1)
    parent_plan_id = parent.get("parallelism_plan_id")
    seen_lane_indexes: set[int] = set()
    errors: list[str] = []
    for child in children:
        lane_count = int(child.get("lane_count") or 1)
        lane_index = child.get("lane_index")
        if lane_count != parent_lane_count:
            errors.append(
                f"{child['task_id']} lane_count {lane_count} does not match parent lane_count {parent_lane_count}"
            )
        if not isinstance(lane_index, int) or lane_index < 1 or lane_index > parent_lane_count:
            errors.append(f"{child['task_id']} lane_index is missing or outside 1..{parent_lane_count}")
            continue
        if lane_index in seen_lane_indexes:
            errors.append(f"duplicate lane_index detected for {child['task_id']}: {lane_index}")
        seen_lane_indexes.add(lane_index)
        if child.get("parallelism_plan_id") != parent_plan_id:
            errors.append(f"{child['task_id']} parallelism_plan_id does not match parent plan")
    return errors


def _print_metrics(metrics: dict[str, object]) -> None:
    for key in METRIC_KEYS:
        print(f"[METRIC] {key}={metrics[key]}")


def _base_metrics(current_task: dict[str, object]) -> dict[str, object]:
    return {
        "lane_count": int(current_task.get("lane_count") or 1),
        "lane_conflict_count": 0,
        "child_closeout_success_rate": "0.00",
        "fallback_count": 0,
        "orphan_cleanup_failures": 0,
    }


def _budget_state(
    current_task: dict[str, object],
    worktree_registry: dict[str, object],
    task_policy: dict[str, object],
) -> tuple[int, int, int, bool]:
    budget = min(int(current_task.get("lane_count") or 1), dynamic_lane_ceiling(task_policy))
    cleanup_failures = _cleanup_failures(worktree_registry)
    fallback_count = 0
    applied = False
    if cleanup_failures and budget > 1:
        budget -= 1
        fallback_count = 1
        applied = True
    return budget, fallback_count, len(cleanup_failures), applied


def _closeout_metrics(
    attempted_child_ids: list[str],
    registry: dict[str, object],
) -> tuple[str, list[str]]:
    if not attempted_child_ids:
        return "0.00", []
    tasks_by_id = task_map(registry)
    successes = 0
    failed_ids: list[str] = []
    for task_id in attempted_child_ids:
        child = tasks_by_id.get(task_id)
        if child is None:
            continue
        if child.get("status") == "done" and child.get("review_bundle_status") == "passed":
            successes += 1
        if child.get("review_bundle_status") == "failed":
            failed_ids.append(task_id)
    return f"{successes / len(attempted_child_ids):.2f}", failed_ids


def _run_repo_gates(root: Path) -> int:
    exit_code = 0
    for result in (python_script(root, "check_repo.py"), python_script(root, "check_hygiene.py")):
        _emit_step_output(result)
        if result.returncode != 0:
            exit_code = result.returncode
    return exit_code


def _maybe_continue_roadmap(
    root: Path,
    current_task: dict[str, object],
    metrics: dict[str, object],
    continue_roadmap: bool,
) -> tuple[int, dict[str, object], dict[str, object]]:
    if not continue_roadmap:
        return 0, current_task, metrics
    continuation = task_ops(root, "continue-roadmap")
    _emit_step_output(continuation)
    if continuation.returncode != 0:
        return continuation.returncode, current_task, metrics
    current_task = load_current_task(root)
    return 0, current_task, _base_metrics(current_task)


def _parallel_cycle_context(
    root: Path,
    current_task: dict[str, object],
    metrics: dict[str, object],
) -> tuple[int, bool]:
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task_policy = load_task_policy(root)
    children = _parallel_children(registry, current_task["current_task_id"])
    lane_conflicts = collect_split_errors(children, task_policy)
    metrics["lane_conflict_count"] = len(lane_conflicts)
    hard_errors = [
        *lane_conflicts,
        *_parallel_registry_errors(current_task, children),
        *collect_active_execution_errors(task_map(registry), worktrees, task_policy),
    ]
    effective_lane_budget, cleanup_fallbacks, cleanup_failures, cleanup_applied = _budget_state(
        current_task,
        worktrees,
        task_policy,
    )
    metrics["fallback_count"] = cleanup_fallbacks
    metrics["orphan_cleanup_failures"] = cleanup_failures
    if hard_errors:
        for error in hard_errors:
            print(f"[ERROR] {error}")
        _print_metrics(metrics)
        raise GovernanceError("parallel runner hard-stop")
    return effective_lane_budget, cleanup_applied


def prepare_parallel_worktrees(
    root: Path,
    current_task_id: str,
    worktree_root: Path,
    effective_lane_budget: int,
) -> tuple[list[str], bool]:
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    entries = worktree_map(worktrees)
    active_count = len(_active_execution_entries(worktrees))
    remaining_capacity = max(0, effective_lane_budget - active_count)
    created: list[str] = []
    children = _parallel_children(registry, current_task_id)
    pending_children = [task for task in children if task["task_id"] not in entries]
    if remaining_capacity == 0:
        return created, bool(pending_children)
    for task in pending_children:
        if remaining_capacity == 0:
            break
        destination = worktree_root / task["task_id"]
        result = task_ops(root, "worktree-create", task["task_id"], "--path", str(destination))
        if result.returncode != 0:
            raise GovernanceError(result.stdout.strip() or result.stderr.strip())
        created.append(task["task_id"])
        remaining_capacity -= 1
    return created, len(created) < len(pending_children)


def _maybe_prepare_worktrees(
    root: Path,
    current_task: dict[str, object],
    gate: dict[str, object],
    worktree_root: Path,
    prepare_worktrees: bool,
    effective_lane_budget: int | None,
) -> None:
    if current_task["topology"] != "parallel_parent" or not prepare_worktrees:
        return
    if not gate["prepare_worktrees"]:
        print(f"[SKIP] prepare-worktrees skipped: {gate['reason']}")
        return
    assert effective_lane_budget is not None
    created, budget_full = prepare_parallel_worktrees(
        root,
        current_task["current_task_id"],
        worktree_root,
        effective_lane_budget,
    )
    for task_id in created:
        print(f"[OK] prepared worktree for {task_id}")
    if budget_full and not created:
        active_count = len(_active_execution_entries(load_worktree_registry(root)))
        print(f"[SKIP] prepare-worktrees skipped: active execution budget reached ({active_count}/{effective_lane_budget})")


def _maybe_auto_close_children(
    root: Path,
    current_task: dict[str, object],
    gate: dict[str, object],
    metrics: dict[str, object],
) -> int:
    if current_task["topology"] != "parallel_parent":
        return 0
    if not gate["auto_close_children"]:
        print(f"[SKIP] auto-close-children skipped: {gate['reason']}")
        return 0
    before_registry = load_task_registry(root)
    before_children = _parallel_children(before_registry, current_task["current_task_id"])
    attempted_child_ids = [task["task_id"] for task in before_children if task.get("status") == "review"]
    result = task_ops(root, "auto-close-children", current_task["current_task_id"])
    _emit_step_output(result)
    after_registry = load_task_registry(root)
    success_rate, failed_child_ids = _closeout_metrics(attempted_child_ids, after_registry)
    metrics["child_closeout_success_rate"] = success_rate
    if failed_child_ids:
        budget_cap = min(int(current_task.get("lane_count") or 1), dynamic_lane_ceiling(load_task_policy(root)))
        current_fallbacks = int(metrics["fallback_count"])
        if budget_cap - current_fallbacks > 1:
            metrics["fallback_count"] = current_fallbacks + 1
    return result.returncode


def _finalize_cycle(
    root: Path,
    current_task: dict[str, object],
    metrics: dict[str, object],
    cleanup_applied: bool,
    exit_code: int,
) -> int:
    cleanup = task_ops(root, "cleanup-orphans")
    _emit_step_output(cleanup)
    cleanup_failures = len(_cleanup_failures(load_worktree_registry(root)))
    if cleanup_failures and current_task["topology"] == "parallel_parent":
        budget_cap = min(int(current_task.get("lane_count") or 1), dynamic_lane_ceiling(load_task_policy(root)))
        current_fallbacks = int(metrics["fallback_count"])
        if not cleanup_applied and budget_cap - current_fallbacks > 1:
            metrics["fallback_count"] = current_fallbacks + 1
    metrics["orphan_cleanup_failures"] = cleanup_failures
    _print_metrics(metrics)
    if cleanup.returncode != 0 and exit_code == 0:
        return cleanup.returncode
    return exit_code


def coordinator_cycle(root: Path, worktree_root: Path, prepare_worktrees: bool, continue_roadmap: bool) -> int:
    current_task = load_current_task(root)
    metrics = _base_metrics(current_task)
    exit_code = _run_repo_gates(root)
    if exit_code != 0:
        return exit_code

    exit_code, current_task, metrics = _maybe_continue_roadmap(root, current_task, metrics, continue_roadmap)
    if exit_code != 0:
        return exit_code

    gate = runner_action_gate(current_task)
    cleanup_applied = False
    effective_lane_budget: int | None = None
    if current_task["topology"] == "parallel_parent":
        try:
            effective_lane_budget, cleanup_applied = _parallel_cycle_context(root, current_task, metrics)
        except GovernanceError:
            return 1
    _maybe_prepare_worktrees(
        root,
        current_task,
        gate,
        worktree_root,
        prepare_worktrees,
        effective_lane_budget,
    )
    auto_close_exit = _maybe_auto_close_children(root, current_task, gate, metrics)
    if auto_close_exit != 0:
        exit_code = auto_close_exit
    return _finalize_cycle(root, current_task, metrics, cleanup_applied, exit_code)


def main() -> int:
    parser = argparse.ArgumentParser(description="AX9S automation runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    once_parser = subparsers.add_parser("once")
    once_parser.add_argument("--worktree-root")
    once_parser.add_argument("--prepare-worktrees", action="store_true")
    once_parser.add_argument("--continue-roadmap", action="store_true")

    loop_parser = subparsers.add_parser("loop")
    loop_parser.add_argument("--worktree-root")
    loop_parser.add_argument("--prepare-worktrees", action="store_true")
    loop_parser.add_argument("--continue-roadmap", action="store_true")
    loop_parser.add_argument("--interval-seconds", type=int, default=60)
    loop_parser.add_argument("--cycles", type=int, default=0)

    args = parser.parse_args()
    try:
        root = find_repo_root()
        worktree_root = Path(args.worktree_root).resolve() if args.worktree_root else default_worktree_root(root)
        if args.command == "once":
            return coordinator_cycle(root, worktree_root, args.prepare_worktrees, args.continue_roadmap)
        cycle = 0
        while True:
            cycle += 1
            result = coordinator_cycle(root, worktree_root, args.prepare_worktrees, args.continue_roadmap)
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
