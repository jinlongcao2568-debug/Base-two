from __future__ import annotations

import importlib.util
from pathlib import Path


HELPERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "helpers.py"
SPEC = importlib.util.spec_from_file_location("gov_helpers", HELPERS_PATH)
HELPERS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(HELPERS)

AUTOMATION_RUNNER_SCRIPT = HELPERS.AUTOMATION_RUNNER_SCRIPT
TASK_OPS_SCRIPT = HELPERS.TASK_OPS_SCRIPT
init_governance_repo = HELPERS.init_governance_repo
git_commit_all = HELPERS.git_commit_all
read_yaml = HELPERS.read_yaml
run_python = HELPERS.run_python
write_yaml = HELPERS.write_yaml


def sync_task_artifacts(repo: Path) -> None:
    result = run_python(TASK_OPS_SCRIPT, repo, "sync", "--write")
    assert result.returncode == 0, result.stdout + result.stderr


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


def test_runner_manual_mode_skips_parallel_actions(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["size_class"] = "heavy"
    current_task["topology"] = "parallel_parent"
    current_task["automation_mode"] = "manual"
    current_task["required_tests"] = ["pytest tests/base -q"]
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["size_class"] = "heavy"
    registry["tasks"][0]["topology"] = "parallel_parent"
    registry["tasks"][0]["automation_mode"] = "manual"
    registry["tasks"][0]["required_tests"] = ["pytest tests/base -q"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)

    for suffix in ("A", "B"):
        create = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "new",
            f"TASK-EXEC-00{suffix}",
            "--title",
            f"execution {suffix}",
            "--stage",
            "parallel-stage",
            "--task-kind",
            "execution",
            "--execution-mode",
            "isolated_worktree",
            "--parent-task-id",
            "TASK-BASE-001",
            "--size-class",
            "standard",
            "--required-tests",
            "pytest tests/base -q",
            "--planned-write-paths",
            f"src/exec{suffix.lower()}/",
        )
        assert create.returncode == 0, create.stdout + create.stderr
        finish = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "worker-finish",
            f"TASK-EXEC-00{suffix}",
            "--summary",
            "candidate ready",
            "--tests",
            "pytest tests/base -q",
        )
        assert finish.returncode == 0, finish.stdout + finish.stderr

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--prepare-worktrees")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[SKIP] prepare-worktrees skipped" in result.stdout
    assert "[SKIP] auto-close-children skipped" in result.stdout
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    assert tasks["TASK-EXEC-00A"]["status"] == "review"
    assert tasks["TASK-EXEC-00B"]["status"] == "review"


def test_runner_assisted_mode_prepares_but_does_not_close_children(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["size_class"] = "heavy"
    current_task["topology"] = "parallel_parent"
    current_task["automation_mode"] = "assisted"
    current_task["required_tests"] = ["pytest tests/base -q"]
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["size_class"] = "heavy"
    registry["tasks"][0]["topology"] = "parallel_parent"
    registry["tasks"][0]["automation_mode"] = "assisted"
    registry["tasks"][0]["required_tests"] = ["pytest tests/base -q"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)

    for suffix in ("A", "B"):
        create = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "new",
            f"TASK-EXEC-A{suffix}",
            "--title",
            f"execution {suffix}",
            "--stage",
            "parallel-stage",
            "--task-kind",
            "execution",
            "--execution-mode",
            "isolated_worktree",
            "--parent-task-id",
            "TASK-BASE-001",
            "--size-class",
            "standard",
            "--required-tests",
            "pytest tests/base -q",
            "--planned-write-paths",
            f"src/assist_{suffix.lower()}/",
        )
        assert create.returncode == 0, create.stdout + create.stderr
        finish = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "worker-finish",
            f"TASK-EXEC-A{suffix}",
            "--summary",
            "candidate ready",
            "--tests",
            "pytest tests/base -q",
        )
        assert finish.returncode == 0, finish.stdout + finish.stderr

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--prepare-worktrees")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[OK] prepared worktree for TASK-EXEC-AA" in result.stdout
    assert "[SKIP] auto-close-children skipped" in result.stdout
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    assert tasks["TASK-EXEC-AA"]["status"] == "review"
    assert tasks["TASK-EXEC-AB"]["status"] == "review"


def test_runner_prepares_and_closes_heavy_children(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["size_class"] = "heavy"
    current_task["topology"] = "parallel_parent"
    current_task["automation_mode"] = "autonomous"
    current_task["required_tests"] = ["pytest tests/base -q"]
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["size_class"] = "heavy"
    registry["tasks"][0]["topology"] = "parallel_parent"
    registry["tasks"][0]["automation_mode"] = "autonomous"
    registry["tasks"][0]["required_tests"] = ["pytest tests/base -q"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)

    for suffix in ("A", "B"):
        create = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "new",
            f"TASK-EXEC-00{suffix}",
            "--title",
            f"execution {suffix}",
            "--stage",
            "parallel-stage",
            "--task-kind",
            "execution",
            "--execution-mode",
            "isolated_worktree",
            "--parent-task-id",
            "TASK-BASE-001",
            "--size-class",
            "standard",
            "--required-tests",
            "pytest tests/base -q",
            "--planned-write-paths",
            f"src/exec{suffix.lower()}/",
        )
        assert create.returncode == 0, create.stdout + create.stderr
        finish = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "worker-finish",
            f"TASK-EXEC-00{suffix}",
            "--summary",
            "candidate ready",
            "--tests",
            "pytest tests/base -q",
        )
        assert finish.returncode == 0, finish.stdout + finish.stderr

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--prepare-worktrees")
    assert result.returncode == 0, result.stdout + result.stderr
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    assert tasks["TASK-EXEC-00A"]["status"] == "done"
    assert tasks["TASK-EXEC-00B"]["status"] == "done"


def test_runner_reports_cleanup_blocked(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    blocked_dir = tmp_path / "blocked.worktree"
    blocked_dir.mkdir()
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-EXEC-BLOCK",
            "title": "blocked cleanup child",
            "status": "done",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": "TASK-BASE-001",
            "stage": "parallel-stage",
            "branch": "feat/TASK-EXEC-BLOCK",
            "size_class": "standard",
            "automation_mode": "autonomous",
            "worker_state": "completed",
            "blocked_reason": None,
            "last_reported_at": "2026-04-04T00:00:00+08:00",
            "topology": "single_worker",
            "allowed_dirs": ["src/exec_block/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/exec_block/"],
            "planned_test_paths": [],
            "required_tests": [],
            "task_file": "docs/governance/tasks/TASK-EXEC-BLOCK.md",
            "runlog_file": "docs/governance/runlogs/TASK-EXEC-BLOCK-RUNLOG.md",
            "created_at": "2026-04-04T00:00:00+08:00",
            "activated_at": "2026-04-04T00:00:00+08:00",
            "closed_at": "2026-04-04T00:00:00+08:00",
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    (repo / "docs/governance/tasks/TASK-EXEC-BLOCK.md").write_text("# task\n", encoding="utf-8")
    (repo / "docs/governance/runlogs/TASK-EXEC-BLOCK-RUNLOG.md").write_text("# runlog\n", encoding="utf-8")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    worktrees["entries"].append(
        {
            "task_id": "TASK-EXEC-BLOCK",
            "work_mode": "execution",
            "parent_task_id": "TASK-BASE-001",
            "branch": "feat/TASK-EXEC-BLOCK",
            "path": str(blocked_dir).replace("\\", "/"),
            "status": "closed",
            "cleanup_state": "pending",
            "cleanup_attempts": 2,
            "last_cleanup_error": None,
            "worker_owner": "worker-a",
        }
    )
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once")
    assert result.returncode == 1
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-BLOCK")
    assert entry["cleanup_state"] == "blocked_manual"
