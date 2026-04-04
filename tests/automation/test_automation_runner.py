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
init_governance_repo = HELPERS.init_governance_repo
git_commit_all = HELPERS.git_commit_all
read_yaml = HELPERS.read_yaml
run_python = HELPERS.run_python
write_yaml = HELPERS.write_yaml


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
    roadmap = roadmap.replace("  stage7: not_established", "  stage7: deferred_manual", 1)
    roadmap = roadmap.replace("  stage8: not_established", "  stage8: deferred_manual", 1)
    roadmap = roadmap.replace("  stage9: not_established", "  stage9: deferred_manual", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")


def _task_status_map(repo: Path, task_ids: list[str]) -> dict[str, str]:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task["status"] for task in registry["tasks"]}
    return {task_id: tasks[task_id] for task_id in task_ids}


def _setup_parallel_parent(repo: Path, automation_mode: str) -> list[str]:
    task_ids = ["TASK-EXEC-00A", "TASK-EXEC-00B"]
    BUILDERS.set_live_task_mode(repo, automation_mode=automation_mode)
    BUILDERS.create_review_ready_children(repo, task_ids, write_path_prefix="src/exec")
    return task_ids


def _setup_review_bundle_failure(repo: Path) -> str:
    task_id = "TASK-EXEC-FAIL"
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous")
    BUILDERS.create_review_ready_child(
        repo,
        task_id,
        write_path="src/exec_fail/",
        title="execution fail",
        required_test="pytest tests/missing -q",
    )
    return task_id


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
    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("automation_mode", "expected_status", "prepare_message", "close_message"),
    [
        ("manual", "review", "[SKIP] prepare-worktrees skipped", "[SKIP] auto-close-children skipped"),
        ("assisted", "review", "[OK] prepared worktree for TASK-EXEC-00A", "[SKIP] auto-close-children skipped"),
        ("autonomous", "done", "[OK] prepared worktree for TASK-EXEC-00A", "[OK] auto-closed children: TASK-EXEC-00A, TASK-EXEC-00B"),
    ],
)
def test_runner_heavy_parent_modes(
    tmp_path: Path,
    automation_mode: str,
    expected_status: str,
    prepare_message: str,
    close_message: str,
) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = _setup_parallel_parent(repo, automation_mode)
    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--prepare-worktrees")
    statuses = _task_status_map(repo, task_ids)

    assert result.returncode == 0, result.stdout + result.stderr
    assert prepare_message in result.stdout
    assert close_message in result.stdout
    assert statuses == {task_id: expected_status for task_id in task_ids}


def test_runner_reports_cleanup_blocked(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    blocked_dir = tmp_path / "blocked.worktree"
    blocked_dir.mkdir()
    BUILDERS.create_cleanup_orphan(repo, blocked_dir, task_id="TASK-EXEC-BLOCK")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    blocked_entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-BLOCK")
    blocked_entry["cleanup_attempts"] = 2
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once")
    assert result.returncode == 1
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-BLOCK")
    assert entry["cleanup_state"] == "blocked_manual"


def test_runner_continue_roadmap_advances_review_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_review_ready(repo)

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_runner_continue_roadmap_fails_without_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    autopilot = next(item for item in capability_map["capabilities"] if item["capability_id"] == "roadmap_autopilot_continuation")
    autopilot["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    mark_review_ready(repo)

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--continue-roadmap")
    assert result.returncode == 1
    assert "no successor" in result.stdout


def test_runner_continue_roadmap_generates_business_parent_and_prepares_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo)
    mark_review_ready(repo)

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--continue-roadmap", "--prepare-worktrees")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == current_task["current_task_id"])
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert parent["topology"] == "parallel_parent"
    assert len(children) == 1
    child_entry = next(entry for entry in worktrees["entries"] if entry["task_id"] == children[0]["task_id"])
    assert child_entry["status"] == "active"
    assert "[OK] prepared worktree for" in result.stdout


def test_runner_blocks_lane_when_review_bundle_fails(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_id = _setup_review_bundle_failure(repo)
    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--prepare-worktrees")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == task_id)

    assert result.returncode == 1
    assert child["status"] == "blocked"
    assert "review_bundle_failed" in child["blocked_reason"]
