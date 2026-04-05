from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python
from .scenario_builders import create_review_ready_child


def _create_parent(repo: Path) -> None:
    create_parent = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-PARENT-001",
        "--title",
        "parent task",
        "--stage",
        "parallel-stage",
        "--branch",
        "main",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "src/base/",
        "tests/base/",
    )
    assert create_parent.returncode == 0, create_parent.stdout + create_parent.stderr


def test_auto_close_children_closes_review_tasks(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_parent(repo)
    create_review_ready_child(
        repo,
        "TASK-EXEC-001",
        write_path="src/exec1/",
        title="execution task",
        parent_task_id="TASK-PARENT-001",
        summary="done",
        tmp_path=tmp_path,
        with_worktree=True,
    )

    close = run_python(TASK_OPS_SCRIPT, repo, "auto-close-children", "TASK-PARENT-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-001")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-PARENT-001")

    assert close.returncode == 0, close.stdout + close.stderr
    assert child["status"] == "done"
    assert child["review_bundle_status"] == "passed"
    assert parent["status"] == "review"
    assert parent["worker_state"] == "review_pending"


def test_auto_close_children_blocks_only_failed_lane_and_parent(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_parent(repo)
    create_review_ready_child(
        repo,
        "TASK-EXEC-001",
        write_path="src/exec1/",
        title="execution pass",
        parent_task_id="TASK-PARENT-001",
        summary="done",
        tmp_path=tmp_path,
        with_worktree=True,
    )
    create_review_ready_child(
        repo,
        "TASK-EXEC-002",
        write_path="src/exec2/",
        title="execution fail",
        parent_task_id="TASK-PARENT-001",
        required_test="pytest tests/missing -q",
        summary="done",
        tmp_path=tmp_path,
        with_worktree=True,
    )

    close = run_python(TASK_OPS_SCRIPT, repo, "auto-close-children", "TASK-PARENT-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-PARENT-001")
    passed = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-001")
    failed = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-002")

    assert close.returncode == 1
    assert passed["status"] == "done"
    assert passed["review_bundle_status"] == "passed"
    assert failed["status"] == "blocked"
    assert failed["review_bundle_status"] == "failed"
    assert parent["status"] == "blocked"
    assert "child_review_bundle_failed" in parent["blocked_reason"]


def test_auto_close_children_keeps_parent_doing_when_open_children_remain(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_parent(repo)
    create_review_ready_child(
        repo,
        "TASK-EXEC-001",
        write_path="src/exec1/",
        title="execution done",
        parent_task_id="TASK-PARENT-001",
        summary="done",
        tmp_path=tmp_path,
        with_worktree=True,
    )
    create_task = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-002",
        "--title",
        "execution open",
        "--stage",
        "parallel-stage",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-PARENT-001",
        "--size-class",
        "standard",
        "--required-tests",
        "pytest tests/base -q",
        "--planned-write-paths",
        "src/exec2/",
    )
    assert create_task.returncode == 0, create_task.stdout + create_task.stderr

    close = run_python(TASK_OPS_SCRIPT, repo, "auto-close-children", "TASK-PARENT-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-PARENT-001")
    closed_child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-001")
    open_child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-002")

    assert close.returncode == 0, close.stdout + close.stderr
    assert closed_child["status"] == "done"
    assert closed_child["review_bundle_status"] == "passed"
    assert open_child["status"] == "queued"
    assert open_child["review_bundle_status"] == "not_applicable"
    assert parent["status"] == "doing"
    assert parent["worker_state"] == "running"
