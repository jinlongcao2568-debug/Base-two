from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


HELPERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "helpers.py"
SPEC = importlib.util.spec_from_file_location("gov_helpers", HELPERS_PATH)
HELPERS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(HELPERS)

BUILDERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "scenario_builders.py"
BUILDERS_SPEC = importlib.util.spec_from_file_location("gov_builders", BUILDERS_PATH)
BUILDERS = importlib.util.module_from_spec(BUILDERS_SPEC)
assert BUILDERS_SPEC.loader is not None
BUILDERS_SPEC.loader.exec_module(BUILDERS)

AUTOMATION_RUNNER_SCRIPT = HELPERS.AUTOMATION_RUNNER_SCRIPT
TASK_OPS_SCRIPT = HELPERS.TASK_OPS_SCRIPT
CHECK_REPO_SCRIPT = HELPERS.CHECK_REPO_SCRIPT
close_live_task_to_idle = HELPERS.close_live_task_to_idle
init_governance_repo = HELPERS.init_governance_repo
git_commit_all = HELPERS.git_commit_all
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


def sync_task_artifacts(repo: Path) -> None:
    result = run_python(TASK_OPS_SCRIPT, repo, "sync", "--write")
    assert result.returncode == 0, result.stdout + result.stderr


def create_successor(repo: Path, task_id: str = "TASK-NEXT-001") -> None:
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        task_id,
        "--title",
        "next coordination task",
        "--stage",
        "next-phase",
        "--branch",
        f"feat/{task_id}",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "scripts/",
        "tests/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "scripts/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def mark_review_ready(repo: Path) -> None:
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-BASE-001",
        "--summary",
        "review ready",
        "--tests",
        "pytest tests/base -q",
    )
    assert finished.returncode == 0, finished.stdout + finished.stderr
    git_commit_all(repo, "prepare roadmap continuation")


def enable_business_autopilot(repo: Path) -> None:
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    for capability in capability_map["capabilities"]:
        if capability["capability_id"] in {"roadmap_autopilot_continuation", "stage1_to_stage6_business_automation"}:
            capability["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("business_automation_enabled: false", "business_automation_enabled: true", 1)
    roadmap = roadmap.replace("  stage1: not_established", "  stage1: bootstrap_required", 1)
    roadmap = roadmap.replace("  stage2: not_established", "  stage2: bootstrap_required", 1)
    roadmap = roadmap.replace("  stage3: not_established", "  stage3: implementation_ready", 1)
    roadmap = roadmap.replace("  stage4: not_established", "  stage4: implementation_ready", 1)
    roadmap = roadmap.replace("  stage5: not_established", "  stage5: bootstrap_required", 1)
    roadmap = roadmap.replace("  stage6: not_established", "  stage6: implementation_ready", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")


def _task_status_map(repo: Path, task_ids: list[str]) -> dict[str, str]:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task["status"] for task in registry["tasks"]}
    return {task_id: tasks[task_id] for task_id in task_ids}


def _setup_parallel_parent(repo: Path, automation_mode: str, lane_count: int = 2) -> list[str]:
    task_ids = [f"TASK-EXEC-{index:03d}" for index in range(1, lane_count + 1)]
    BUILDERS.set_live_task_mode(repo, automation_mode=automation_mode, lane_count=lane_count)
    BUILDERS.create_review_ready_children(repo, task_ids, write_path_prefix="src/exec")
    return task_ids


def _setup_open_parallel_parent(repo: Path) -> list[str]:
    task_ids = ["TASK-EXEC-001", "TASK-EXEC-002"]
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=len(task_ids))
    BUILDERS.create_review_ready_child(
        repo,
        task_ids[0],
        write_path="src/exec_ready/",
        title="execution ready",
        required_test="pytest tests/base -q",
        lane_count=len(task_ids),
        lane_index=1,
    )
    BUILDERS.create_execution_task(
        repo,
        task_ids[1],
        write_path="src/exec_open/",
        title="execution open",
        required_test="pytest tests/base -q",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    open_task = next(task for task in registry["tasks"] if task["task_id"] == task_ids[1])
    open_task["lane_count"] = len(task_ids)
    open_task["lane_index"] = 2
    open_task["parallelism_plan_id"] = f"plan-TASK-BASE-001-{len(task_ids)}"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)
    return task_ids


def _setup_dispatchable_parallel_parent(repo: Path, lane_count: int) -> list[str]:
    task_ids = [f"TASK-DISPATCH-{index:03d}" for index in range(1, lane_count + 1)]
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=lane_count)
    for index, task_id in enumerate(task_ids, start=1):
        BUILDERS.create_execution_task(
            repo,
            task_id,
            write_path=f"src/dispatch_{index}/",
            title=f"dispatch lane {index}",
            required_test="pytest tests/base -q",
        )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    for index, task_id in enumerate(task_ids, start=1):
        task = next(item for item in registry["tasks"] if item["task_id"] == task_id)
        task["lane_count"] = lane_count
        task["lane_index"] = index
        task["parallelism_plan_id"] = f"plan-TASK-BASE-001-{lane_count}"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)
    return task_ids


def _setup_review_bundle_failure(repo: Path) -> list[str]:
    task_ids = ["TASK-EXEC-FAIL-1", "TASK-EXEC-FAIL-2", "TASK-EXEC-FAIL-3"]
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=len(task_ids))
    BUILDERS.create_review_ready_child(
        repo,
        task_ids[0],
        write_path="src/exec_pass_1/",
        title="execution pass one",
        required_test="pytest tests/base -q",
        lane_count=len(task_ids),
        lane_index=1,
    )
    BUILDERS.create_review_ready_child(
        repo,
        task_ids[1],
        write_path="src/exec_fail/",
        title="execution fail",
        required_test="pytest tests/missing -q",
        lane_count=len(task_ids),
        lane_index=2,
    )
    BUILDERS.create_review_ready_child(
        repo,
        task_ids[2],
        write_path="src/exec_pass_2/",
        title="execution pass two",
        required_test="pytest tests/base -q",
        lane_count=len(task_ids),
        lane_index=3,
    )
    return task_ids


def test_runner_once_succeeds_for_micro_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["size_class"] = "micro"
    current_task["topology"] = "single_task"
    current_task["planned_write_paths"] = ["src/base/", "tests/base/"]
    current_task["allowed_dirs"] = ["src/base/", "tests/base/"]
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["size_class"] = "micro"
    registry["tasks"][0]["topology"] = "single_task"
    registry["tasks"][0]["planned_write_paths"] = ["src/base/", "tests/base/"]
    registry["tasks"][0]["allowed_dirs"] = ["src/base/", "tests/base/"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)
    git_commit_all(repo, "switch to micro")
    result = run_runner(repo, "once")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("automation_mode", "expected_status", "expected_parent_status", "prepare_message", "close_message"),
    [
        ("manual", "review", "doing", "[SKIP] prepare-worktrees skipped", "[SKIP] auto-close-children skipped"),
        ("assisted", "review", "doing", "[OK] prepared worktree for TASK-EXEC-001", "[SKIP] auto-close-children skipped"),
        (
            "autonomous",
            "done",
            "review",
            "[OK] prepared worktree for TASK-EXEC-001",
            "[OK] auto-closed children: TASK-EXEC-001, TASK-EXEC-002",
        ),
    ],
)
def test_runner_heavy_parent_modes(
    tmp_path: Path,
    automation_mode: str,
    expected_status: str,
    expected_parent_status: str,
    prepare_message: str,
    close_message: str,
) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = _setup_parallel_parent(repo, automation_mode)
    result = run_runner(repo, "once", "--prepare-worktrees")
    statuses = _task_status_map(repo, task_ids)
    parent = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")["tasks"][0]
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    child_entries = [entry for entry in worktrees["entries"] if entry.get("task_id") in task_ids]

    assert result.returncode == 0, result.stdout + result.stderr
    assert prepare_message in result.stdout
    assert close_message in result.stdout
    assert statuses == {task_id: expected_status for task_id in task_ids}
    assert parent["status"] == expected_parent_status
    if automation_mode == "manual":
        assert child_entries == []
    else:
        assert len(child_entries) == len(task_ids)


def test_runner_reports_cleanup_blocked(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    blocked_dir = tmp_path / "blocked.worktree"
    blocked_dir.mkdir()
    BUILDERS.create_cleanup_orphan(repo, blocked_dir, task_id="TASK-EXEC-BLOCK")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    blocked_entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-BLOCK")
    blocked_entry["cleanup_attempts"] = 2
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    result = run_runner(repo, "once")
    assert result.returncode == 1
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-BLOCK")
    assert entry["cleanup_state"] == "blocked_manual"


def test_runner_cleans_orphaned_execution_worktree_on_success(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    orphan_dir = tmp_path / "orphan.worktree"
    orphan_dir.mkdir()
    BUILDERS.create_cleanup_orphan(repo, orphan_dir, task_id="TASK-EXEC-ORPHAN")
    orphan_dir.rmdir()

    result = run_runner(repo, "once")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-ORPHAN")

    assert result.returncode == 0, result.stdout + result.stderr
    assert entry["cleanup_state"] == "done"
    assert entry["cleanup_attempts"] == 1
    assert entry["last_cleanup_error"] is None
    assert "[METRIC] orphan_cleanup_failures=0" in result.stdout


def test_runner_continue_roadmap_advances_review_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_review_ready(repo)

    result = run_runner(repo, "once", "--continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_runner_loop_continue_roadmap_stops_after_cycle_limit(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_review_ready(repo)

    result = run_runner(repo, "loop", "--continue-roadmap", "--cycles", "1")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[CYCLE] automation-runner cycle=1" in result.stdout
    assert "[STOP] automation-runner loop stopped cycle=1 reason=cycle limit reached" in result.stdout
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert current_task["status"] == "doing"
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_runner_continue_roadmap_advances_idle_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    close_live_task_to_idle(repo, commit_after_close=True)

    result = run_runner(repo, "once", "--continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert current_task["status"] == "doing"
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_runner_continue_roadmap_fails_without_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    autopilot = next(item for item in capability_map["capabilities"] if item["capability_id"] == "roadmap_autopilot_continuation")
    autopilot["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    mark_review_ready(repo)

    result = run_runner(repo, "once", "--continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] is None
    assert current_task["status"] == "idle"
    assert "closed TASK-BASE-001 to idle" in result.stdout


def test_runner_continue_roadmap_blocks_live_task_without_ai_guarded_closeout(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    git_commit_all(repo, "prepare successor while current task is still active")

    result = run_runner(repo, "once", "--continue-roadmap")

    assert result.returncode == 1
    assert "ai_guarded closeout is ready" in result.stdout


def test_runner_continue_roadmap_fails_without_successor_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    autopilot = next(item for item in capability_map["capabilities"] if item["capability_id"] == "roadmap_autopilot_continuation")
    autopilot["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    close_live_task_to_idle(repo, commit_after_close=True)

    result = run_runner(repo, "once", "--continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] is None
    assert current_task["status"] == "idle"
    assert "no successor is available" in result.stdout


def test_runner_continue_roadmap_generates_business_parent_and_prepares_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo)
    mark_review_ready(repo)

    result = run_runner(repo, "once", "--continue-roadmap", "--prepare-worktrees")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == current_task["current_task_id"])
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert parent["topology"] == "parallel_parent"
    assert len(children) == 1
    assert parent["lane_count"] == 1
    assert children[0]["lane_count"] == 1
    assert children[0]["lane_index"] == 1
    child_entry = next(entry for entry in worktrees["entries"] if entry["task_id"] == children[0]["task_id"])
    assert child_entry["status"] == "active"
    assert "[OK] prepared worktree for" in result.stdout


def test_runner_blocks_lane_when_review_bundle_fails(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = _setup_review_bundle_failure(repo)
    result = run_runner(repo, "once", "--prepare-worktrees")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-BASE-001")
    failing = next(task for task in registry["tasks"] if task["task_id"] == task_ids[1])
    passing = [task for task in registry["tasks"] if task["task_id"] in {task_ids[0], task_ids[2]}]

    assert result.returncode == 1
    assert failing["status"] == "blocked"
    assert failing["review_bundle_status"] == "failed"
    assert "review_bundle_failed" in failing["blocked_reason"]
    assert [task["status"] for task in passing] == ["done", "done"]
    assert all(task["review_bundle_status"] == "passed" for task in passing)
    assert parent["status"] == "blocked"
    assert "[BLOCKED] TASK-EXEC-FAIL-2" in result.stdout


def test_runner_keeps_parent_doing_when_child_review_bundle_is_still_open(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = _setup_open_parallel_parent(repo)

    result = run_runner(repo, "once", "--prepare-worktrees")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-BASE-001")
    ready_child = next(task for task in registry["tasks"] if task["task_id"] == task_ids[0])
    open_child = next(task for task in registry["tasks"] if task["task_id"] == task_ids[1])

    assert result.returncode == 0, result.stdout + result.stderr
    assert ready_child["status"] == "done"
    assert ready_child["review_bundle_status"] == "passed"
    assert open_child["status"] == "doing"
    assert open_child["worker_state"] == "running"
    assert open_child["review_bundle_status"] == "not_applicable"
    assert parent["status"] == "doing"
    assert "[OK] parent still doing: TASK-BASE-001 waiting on TASK-EXEC-002" in result.stdout


@pytest.mark.parametrize("lane_count", [2, 4])
def test_runner_dispatches_local_launchers_for_parallel_parent(tmp_path: Path, lane_count: int) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = _setup_dispatchable_parallel_parent(repo, lane_count)
    env = {
        "AX9_LAUNCHER_HEARTBEAT_INTERVAL_SECONDS": "1",
        "AX9_LAUNCHER_MAX_RUNTIME_SECONDS": "2",
        "AX9_LAUNCHER_DISPATCH_SETTLE_SECONDS": "2",
        "AX9_LAUNCHER_HEARTBEAT_TIMEOUT_SECONDS": "10",
    }

    result = run_runner(repo, "once", "--prepare-worktrees", env=env)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")
    entries = [entry for entry in worktrees["entries"] if entry.get("task_id") in task_ids]
    runtime_entries = runtime["execution"]["entries"]
    tasks = [task for task in registry["tasks"] if task["task_id"] in task_ids]

    assert result.returncode == 0, result.stdout + result.stderr
    assert len(entries) == lane_count
    assert len(tasks) == lane_count
    assert all(task["status"] == "doing" for task in tasks)
    assert all(runtime_entries[task_id]["lane_session_id"] is not None for task_id in task_ids)
    assert all(runtime_entries[task_id]["executor_status"] == "running" for task_id in task_ids)
    assert all(runtime_entries[task_id]["started_at"] is not None for task_id in task_ids)
    assert all(runtime_entries[task_id]["last_heartbeat_at"] is not None for task_id in task_ids)
    assert all(f"[OK] dispatched launcher for {task_id}" in result.stdout for task_id in task_ids)


def test_runner_marks_stale_heartbeat_lane_timed_out(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=1)
    BUILDERS.create_execution_task(
        repo,
        "TASK-EXEC-TIMEOUT",
        write_path="src/timeout/",
        title="timeout lane",
        required_test="pytest tests/base -q",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-TIMEOUT")
    child["status"] = "doing"
    child["worker_state"] = "running"
    child["lane_count"] = 1
    child["lane_index"] = 1
    child["parallelism_plan_id"] = "plan-TASK-BASE-001-1"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-TIMEOUT"
    created = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", "TASK-EXEC-TIMEOUT", "--path", str(destination))
    assert created.returncode == 0, created.stdout + created.stderr
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")
    runtime["execution"]["entries"]["TASK-EXEC-TIMEOUT"] = {
        "executor_status": "running",
        "started_at": "2026-04-05T18:00:00+08:00",
        "last_heartbeat_at": "2026-04-05T18:00:00+08:00",
        "lane_session_id": "lane-timeout-1",
        "last_result": "running",
    }
    write_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml", runtime)

    env = {"AX9_LAUNCHER_HEARTBEAT_TIMEOUT_SECONDS": "1"}
    result = run_runner(repo, "once", "--prepare-worktrees", env=env)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-TIMEOUT")
    entry = runtime["execution"]["entries"]["TASK-EXEC-TIMEOUT"]

    assert result.returncode == 1
    assert child["status"] == "blocked"
    assert child["worker_state"] == "blocked"
    assert "lane_heartbeat_timeout" in child["blocked_reason"]
    assert entry["executor_status"] == "timed_out"
    assert entry["last_result"] == "timeout"
    assert "[BLOCKED] TASK-EXEC-TIMEOUT: heartbeat timeout" in result.stdout


def test_runner_restart_recovers_running_lane_from_registry_state(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=1)
    BUILDERS.create_execution_task(
        repo,
        "TASK-EXEC-RUN",
        write_path="src/running/",
        title="running lane",
        required_test="pytest tests/base -q",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-RUN")
    child["status"] = "doing"
    child["worker_state"] = "running"
    child["lane_count"] = 1
    child["lane_index"] = 1
    child["parallelism_plan_id"] = "plan-TASK-BASE-001-1"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-RUN"
    created = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", "TASK-EXEC-RUN", "--path", str(destination))
    assert created.returncode == 0, created.stdout + created.stderr
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")
    runtime["execution"]["entries"]["TASK-EXEC-RUN"] = {
        "executor_status": "running",
        "started_at": "2099-04-05T21:00:00+08:00",
        "last_heartbeat_at": "2099-04-05T21:00:00+08:00",
        "lane_session_id": "lane-running-1",
        "last_result": "running",
    }
    write_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml", runtime)

    result = run_runner(repo, "once", "--prepare-worktrees")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-RUN")
    entry = runtime["execution"]["entries"]["TASK-EXEC-RUN"]

    assert result.returncode == 0, result.stdout + result.stderr
    assert child["status"] == "doing"
    assert child["worker_state"] == "running"
    assert entry["executor_status"] == "running"
    assert entry["lane_session_id"] == "lane-running-1"


def test_runner_keeps_parent_doing_when_blocked_and_open_children_coexist(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=2)
    BUILDERS.create_execution_task(
        repo,
        "TASK-EXEC-BLOCKED",
        write_path="src/blocked_lane/",
        title="blocked lane",
        required_test="pytest tests/base -q",
    )
    BUILDERS.create_execution_task(
        repo,
        "TASK-EXEC-OPEN",
        write_path="src/open_lane/",
        title="open lane",
        required_test="pytest tests/base -q",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    for task_id, status, worker_state, lane_index in (
        ("TASK-EXEC-BLOCKED", "blocked", "blocked", 1),
        ("TASK-EXEC-OPEN", "queued", "idle", 2),
    ):
        task = next(item for item in registry["tasks"] if item["task_id"] == task_id)
        task["lane_count"] = 2
        task["lane_index"] = lane_index
        task["parallelism_plan_id"] = "plan-TASK-BASE-001-2"
        task["status"] = status
        task["worker_state"] = worker_state
        if status == "blocked":
            task["blocked_reason"] = "simulated blocker"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)

    result = run_runner(repo, "once", "--prepare-worktrees")
    parent = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")["tasks"][0]

    assert result.returncode == 0, result.stdout + result.stderr
    assert parent["status"] == "doing"
    assert parent["worker_state"] == "running"
