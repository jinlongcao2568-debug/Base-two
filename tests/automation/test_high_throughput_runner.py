from __future__ import annotations

import importlib.util
from pathlib import Path


HELPERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "helpers.py"
HELPERS_SPEC = importlib.util.spec_from_file_location("gov_helpers_high_throughput", HELPERS_PATH)
HELPERS = importlib.util.module_from_spec(HELPERS_SPEC)
assert HELPERS_SPEC.loader is not None
HELPERS_SPEC.loader.exec_module(HELPERS)

BUILDERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "scenario_builders.py"
BUILDERS_SPEC = importlib.util.spec_from_file_location("gov_builders_high_throughput", BUILDERS_PATH)
BUILDERS = importlib.util.module_from_spec(BUILDERS_SPEC)
assert BUILDERS_SPEC.loader is not None
BUILDERS_SPEC.loader.exec_module(BUILDERS)


AUTOMATION_RUNNER_SCRIPT = HELPERS.AUTOMATION_RUNNER_SCRIPT
init_governance_repo = HELPERS.init_governance_repo
read_yaml = HELPERS.read_yaml
run_python = HELPERS.run_python_inline
write_yaml = HELPERS.write_yaml

RUNNER_ENV = {
    "AX9_INLINE_LANE_LAUNCHER": "1",
    "AX9_INLINE_GOVERNANCE_SCRIPTS": "1",
}


def run_runner(repo: Path, *args: str, env: dict[str, str] | None = None):
    merged_env = dict(RUNNER_ENV)
    if env:
        merged_env.update(env)
    return run_python(AUTOMATION_RUNNER_SCRIPT, repo, *args, env=merged_env)


def _runner_metrics(stdout: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    prefix = "[METRIC] "
    for line in stdout.splitlines():
        if not line.startswith(prefix):
            continue
        key, value = line[len(prefix) :].split("=", 1)
        metrics[key] = value
    return metrics


def _child_worktree_entries(repo: Path, task_ids: list[str]) -> list[dict]:
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    return [entry for entry in worktrees["entries"] if entry.get("task_id") in task_ids]


def _set_child_parallel_metadata(repo: Path, task_id: str, lane_count: int, lane_index: int) -> None:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == task_id)
    task["lane_count"] = lane_count
    task["lane_index"] = lane_index
    task["parallelism_plan_id"] = f"plan-TASK-BASE-001-{lane_count}"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    BUILDERS.sync_task_artifacts(repo)


def _create_conflicting_children(repo: Path) -> list[str]:
    task_ids = ["TASK-CONFLICT-001", "TASK-CONFLICT-002"]
    BUILDERS.set_live_task_mode(repo, automation_mode="assisted", lane_count=len(task_ids))
    for index, task_id in enumerate(task_ids, start=1):
        BUILDERS.create_execution_task(
            repo,
            task_id,
            write_path="src/conflict/",
            title=f"conflict {index}",
            required_test="pytest tests/base -q",
        )
        _set_child_parallel_metadata(repo, task_id, len(task_ids), index)
    return task_ids


def _mark_cleanup_pressure(repo: Path, tmp_path: Path, cleanup_state: str, attempts: int) -> Path:
    blocked_dir = tmp_path / f"{cleanup_state}.worktree"
    blocked_dir.mkdir()
    BUILDERS.create_cleanup_orphan(repo, blocked_dir, task_id=f"TASK-CLEANUP-{cleanup_state.upper()}")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == f"TASK-CLEANUP-{cleanup_state.upper()}")
    task["parent_task_id"] = "TASK-ORPHAN-PARENT"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == f"TASK-CLEANUP-{cleanup_state.upper()}")
    entry["parent_task_id"] = "TASK-ORPHAN-PARENT"
    entry["cleanup_state"] = cleanup_state
    entry["cleanup_attempts"] = attempts
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    return blocked_dir


def test_runner_reports_metrics_for_dynamic_lane_counts(tmp_path: Path) -> None:
    for lane_count in (2, 3, 4):
        repo = init_governance_repo(tmp_path / f"lanes-{lane_count}")
        task_ids = [f"TASK-LANE-{lane_count}-{index:03d}" for index in range(1, lane_count + 1)]
        BUILDERS.set_live_task_mode(repo, automation_mode="assisted", lane_count=lane_count)
        BUILDERS.create_review_ready_children(repo, task_ids, write_path_prefix=f"src/lanes_{lane_count}/")

        result = run_runner(repo, "once", "--prepare-worktrees")
        metrics = _runner_metrics(result.stdout)

        assert result.returncode == 0, result.stdout + result.stderr
        assert len(_child_worktree_entries(repo, task_ids)) == lane_count
        assert metrics["lane_count"] == str(lane_count)
        assert metrics["lane_conflict_count"] == "0"
        assert metrics["fallback_count"] == "0"


def test_runner_respects_effective_budget_under_cleanup_pressure(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = [f"TASK-BUDGET-{index:03d}" for index in range(1, 5)]
    BUILDERS.set_live_task_mode(repo, automation_mode="assisted", lane_count=len(task_ids))
    BUILDERS.create_review_ready_children(repo, task_ids, write_path_prefix="src/budget/")
    for task_id in task_ids[:3]:
        BUILDERS.create_worktree(repo, tmp_path, task_id)
    blocked_dir = _mark_cleanup_pressure(repo, tmp_path, cleanup_state="blocked", attempts=1)
    blocked_dir.rmdir()

    result = run_runner(repo, "once", "--prepare-worktrees")
    metrics = _runner_metrics(result.stdout)
    child_entry_ids = {entry["task_id"] for entry in _child_worktree_entries(repo, task_ids)}

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[SKIP] prepare-worktrees skipped: active execution budget reached (3/3)" in result.stdout
    assert task_ids[3] not in child_entry_ids
    assert metrics["fallback_count"] == "1"


def test_runner_reports_cleanup_failures_as_fallback_metrics(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    BUILDERS.set_live_task_mode(repo, automation_mode="assisted", lane_count=4)
    _mark_cleanup_pressure(repo, tmp_path, cleanup_state="pending", attempts=2)

    result = run_runner(repo, "once")
    metrics = _runner_metrics(result.stdout)

    assert result.returncode == 1
    assert metrics["fallback_count"] == "1"
    assert int(metrics["orphan_cleanup_failures"]) >= 1


def test_runner_tracks_review_bundle_failure_in_metrics(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=3)
    BUILDERS.create_review_ready_child(
        repo,
        "TASK-REVIEW-PASS-001",
        write_path="src/review_pass_1/",
        required_test="pytest tests/base -q",
        lane_count=3,
        lane_index=1,
    )
    BUILDERS.create_review_ready_child(
        repo,
        "TASK-REVIEW-FAIL-002",
        write_path="src/review_fail/",
        required_test="pytest tests/missing -q",
        lane_count=3,
        lane_index=2,
    )
    BUILDERS.create_review_ready_child(
        repo,
        "TASK-REVIEW-PASS-003",
        write_path="src/review_pass_2/",
        required_test="pytest tests/base -q",
        lane_count=3,
        lane_index=3,
    )

    result = run_runner(repo, "once", "--prepare-worktrees")
    metrics = _runner_metrics(result.stdout)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-BASE-001")

    assert result.returncode == 1
    assert parent["status"] == "blocked"
    assert metrics["fallback_count"] == "1"
    assert metrics["child_closeout_success_rate"] == "0.67"


def test_runner_stops_on_lane_conflicts(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = _create_conflicting_children(repo)

    result = run_runner(repo, "once", "--prepare-worktrees")
    metrics = _runner_metrics(result.stdout)

    assert result.returncode == 1
    assert int(metrics["lane_conflict_count"]) > 0
    assert _child_worktree_entries(repo, task_ids) == []
