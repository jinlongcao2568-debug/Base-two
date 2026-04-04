from __future__ import annotations

from pathlib import Path

from .helpers import CHECK_REPO_SCRIPT, git_commit_all, init_governance_repo, read_yaml, run_python, write_yaml


def test_check_repo_passes_on_clean_repo(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_repo_fails_when_governance_file_missing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "docs/governance/CURRENT_TASK.yaml").unlink()
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1


def test_check_repo_fails_on_branch_mismatch(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["branch"] = "feat/wrong-branch"
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "branch" in result.stdout


def test_check_repo_fails_on_modified_path_outside_allowed_dirs(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "oops.txt").write_text("x", encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "outside allowed_dirs" in result.stdout


def test_check_repo_fails_on_modified_path_outside_planned_write_paths(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["allowed_dirs"] = ["docs/governance/"]
    current_task["planned_write_paths"] = ["docs/governance/CURRENT_TASK.yaml"]
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["allowed_dirs"] = ["docs/governance/"]
    registry["tasks"][0]["planned_write_paths"] = ["docs/governance/CURRENT_TASK.yaml"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    (repo / "docs/governance/unplanned.md").write_text("x", encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "outside planned_write_paths" in result.stdout


def test_check_repo_fails_when_execution_touches_reserved_path(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-EXEC-001",
            "title": "execution task",
            "status": "doing",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": "TASK-BASE-001",
            "stage": "pilot",
            "branch": "main",
            "size_class": "micro",
            "automation_mode": "autonomous",
            "worker_state": "running",
            "blocked_reason": None,
            "last_reported_at": "2026-04-04T00:00:00+08:00",
            "topology": "single_task",
            "allowed_dirs": ["src/execution/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/execution/"],
            "planned_test_paths": ["tests/execution/"],
            "required_tests": [],
            "task_file": "docs/governance/tasks/TASK-EXEC-001.md",
            "runlog_file": "docs/governance/runlogs/TASK-EXEC-001-RUNLOG.md",
            "created_at": "2026-04-04T00:00:00+08:00",
            "activated_at": "2026-04-04T00:00:00+08:00",
            "closed_at": None,
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    (repo / "docs/governance/tasks/TASK-EXEC-001.md").write_text("# TASK-EXEC-001\n", encoding="utf-8")
    (repo / "docs/governance/runlogs/TASK-EXEC-001-RUNLOG.md").write_text("# RUNLOG\n", encoding="utf-8")
    write_yaml(
        repo / ".codex/local/EXECUTION_CONTEXT.yaml",
        {
            "task_id": "TASK-EXEC-001",
            "parent_task_id": "TASK-BASE-001",
            "branch": "main",
            "worktree_path": str(repo).replace("\\", "/"),
            "allowed_dirs": ["src/execution/"],
            "planned_write_paths": ["src/execution/"],
            "planned_test_paths": ["tests/execution/"],
            "required_tests": [],
        },
    )
    (repo / "docs/governance/hack.md").write_text("x", encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "outside allowed_dirs" in result.stdout or "reserved path" in result.stdout


def test_check_repo_fails_when_active_execution_limit_exceeded(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    for index in range(3):
        task_id = f"TASK-EXEC-00{index + 1}"
        registry["tasks"].append(
            {
                "task_id": task_id,
                "title": task_id,
                "status": "doing",
                "task_kind": "execution",
                "execution_mode": "isolated_worktree",
                "parent_task_id": "TASK-BASE-001",
                "stage": "pilot",
                "branch": f"feat/{task_id}",
                "size_class": "standard",
                "automation_mode": "autonomous",
                "worker_state": "running",
                "blocked_reason": None,
                "last_reported_at": "2026-04-04T00:00:00+08:00",
                "topology": "single_worker",
                "allowed_dirs": [f"src/exec{index}/"],
                "reserved_paths": [],
                "planned_write_paths": [f"src/exec{index}/"],
                "planned_test_paths": [f"tests/exec{index}/"],
                "required_tests": [],
                "task_file": f"docs/governance/tasks/{task_id}.md",
                "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
                "created_at": "2026-04-04T00:00:00+08:00",
                "activated_at": "2026-04-04T00:00:00+08:00",
                "closed_at": None,
            }
        )
        worktrees["entries"].append(
            {
                "task_id": task_id,
                "work_mode": "execution",
                "parent_task_id": "TASK-BASE-001",
                "branch": f"feat/{task_id}",
                "path": f"D:/tmp/{task_id}",
                "status": "active",
                "cleanup_state": "pending",
                "cleanup_attempts": 0,
                "last_cleanup_error": None,
                "worker_owner": "worker-a" if index % 2 == 0 else "worker-b",
            }
        )
        (repo / f"docs/governance/tasks/{task_id}.md").write_text("# task\n", encoding="utf-8")
        (repo / f"docs/governance/runlogs/{task_id}-RUNLOG.md").write_text("# runlog\n", encoding="utf-8")
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    git_commit_all(repo, "add execution entries")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "hard limit of 2" in result.stdout
