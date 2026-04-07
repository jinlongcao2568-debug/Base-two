from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python_inline as run_python, write_yaml


def test_worktree_create_caps_active_execution_entries_at_twenty(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = [f"TASK-EXEC-{index:03d}" for index in range(1, 22)]
    for index, task_id in enumerate(task_ids, start=1):
        create_task = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "new",
            task_id,
            "--title",
            f"execution task {index}",
            "--stage",
            "pilot",
            "--branch",
            f"feat/{task_id}",
            "--task-kind",
            "execution",
            "--execution-mode",
            "isolated_worktree",
            "--planned-write-paths",
            f"src/execution{index}/",
            "--planned-test-paths",
            f"tests/execution{index}/",
        )
        assert create_task.returncode == 0, create_task.stdout + create_task.stderr
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    worktrees["entries"].extend(
        {
            "task_id": task_id,
            "work_mode": "execution",
            "parent_task_id": None,
            "branch": f"feat/{task_id}",
            "path": str(tmp_path / "repo.worktrees" / task_id).replace("\\", "/"),
            "status": "active",
            "cleanup_state": "pending",
            "cleanup_attempts": 0,
            "last_cleanup_error": None,
            "worker_owner": "worker-01",
            "lane_session_id": None,
            "executor_status": "prepared",
            "started_at": None,
            "last_heartbeat_at": None,
            "last_result": None,
        }
        for task_id in task_ids[:20]
    )
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    rejected = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worktree-create",
        task_ids[20],
        "--path",
        str(tmp_path / "repo.worktrees" / task_ids[20]),
    )
    assert rejected.returncode == 1
    assert "already at hard limit 20" in rejected.stdout
