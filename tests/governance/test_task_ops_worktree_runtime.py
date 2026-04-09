from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .helpers import (
    TASK_OPS_SCRIPT,
    init_governance_repo,
    read_yaml,
    run_python_inline as run_python,
    set_idle_control_plane,
    write_yaml,
)
from .scenario_builders import create_cleanup_orphan
from .test_roadmap_candidate_index import _candidate, _write_backlog


def test_worktree_create_and_release_round_trip(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_task = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-001",
        "--title",
        "execution task",
        "--stage",
        "pilot",
        "--branch",
        "feat/TASK-EXEC-001",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--planned-write-paths",
        "src/execution/",
        "--planned-test-paths",
        "tests/execution/",
    )
    assert create_task.returncode == 0, create_task.stdout + create_task.stderr
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-001"
    created = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", "TASK-EXEC-001", "--path", str(destination))
    assert created.returncode == 0, created.stdout + created.stderr
    assert (destination / ".codex/local/EXECUTION_CONTEXT.yaml").exists()
    context = read_yaml(destination / ".codex/local/EXECUTION_CONTEXT.yaml")
    assert context["lane_count"] == 1
    assert context["lane_index"] is None
    assert context["parallelism_plan_id"] is None
    assert context["runtime_prompt_profile"] == "docs/governance/runtime_prompts/worker.md"
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-001")
    assert entry["status"] == "active"
    assert entry["worker_owner"] == "worker-01"
    assert entry["executor_status"] == "prepared"
    assert entry["lane_session_id"] is None
    assert entry["started_at"] is None
    assert entry["last_heartbeat_at"] is None
    released = run_python(TASK_OPS_SCRIPT, repo, "worktree-release", "TASK-EXEC-001")
    assert released.returncode == 0, released.stdout + released.stderr
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-001")
    assert entry["status"] == "closed"
    assert entry["cleanup_state"] == "done"
    assert not destination.exists()


def test_worker_heartbeat_updates_execution_runtime_without_runlog_noise(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_task = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-HB",
        "--title",
        "execution heartbeat task",
        "--stage",
        "pilot",
        "--branch",
        "feat/TASK-EXEC-HB",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--planned-write-paths",
        "src/execution_hb/",
        "--planned-test-paths",
        "tests/execution_hb/",
    )
    assert create_task.returncode == 0, create_task.stdout + create_task.stderr
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-HB"
    created = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", "TASK-EXEC-HB", "--path", str(destination))
    assert created.returncode == 0, created.stdout + created.stderr
    before_worker_registry = (repo / "docs/governance/WORKER_REGISTRY.yaml").read_text(encoding="utf-8")

    heartbeat = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-heartbeat",
        "TASK-EXEC-HB",
        "--lane-session-id",
        "lane-heartbeat-1",
        "--executor-status",
        "running",
        "--result",
        "heartbeat",
    )
    assert heartbeat.returncode == 0, heartbeat.stdout + heartbeat.stderr

    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-HB")
    assert entry["lane_session_id"] == "lane-heartbeat-1"
    assert entry["executor_status"] == "running"
    assert entry["started_at"] is not None
    assert entry["last_heartbeat_at"] is not None
    assert entry["last_result"] == "heartbeat"

    after_worker_registry = (repo / "docs/governance/WORKER_REGISTRY.yaml").read_text(encoding="utf-8")
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")
    assert before_worker_registry == after_worker_registry
    assert runtime["workers"]["entries"]["worker-local-01"]["last_heartbeat_at"] is not None
    assert runtime["execution"]["entries"]["TASK-EXEC-HB"]["executor_status"] == "running"

    runlog_text = (repo / "docs/governance/runlogs/TASK-EXEC-HB-RUNLOG.md").read_text(encoding="utf-8")
    assert "heartbeat" not in runlog_text


def test_cleanup_orphans_marks_blocked_when_remove_fails(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    blocked_dir = tmp_path / "blocked.worktree"
    blocked_dir.mkdir()
    create_cleanup_orphan(repo, blocked_dir)
    result = run_python(TASK_OPS_SCRIPT, repo, "cleanup-orphans")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-009")
    assert result.returncode == 1
    assert entry["cleanup_state"] == "blocked"
    assert entry["cleanup_attempts"] == 1


def test_review_candidate_pool_from_clone_cwd_reads_control_plane_truth(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "status": "active",
            "control_plane_root": str(repo).replace("\\", "/"),
            "slots": [
                {
                    "slot_id": "worker-01",
                    "path": str(clone_path).replace("\\", "/"),
                    "branch": "codex/worker-01-idle",
                    "idle_branch": "codex/worker-01-idle",
                    "status": "ready",
                    "current_task_id": None,
                }
            ],
        },
    )
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])
    from .helpers import git_commit_all

    git_commit_all(repo, "prepare full clone slot")
    subprocess.run(["git", "clone", "--local", str(repo), str(clone_path)], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "switch", "-c", "codex/worker-01-idle"],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_python(TASK_OPS_SCRIPT, clone_path, "review-candidate-pool")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["control_plane_root"] == str(repo).replace("\\", "/")
    assert (repo / ".codex/local/roadmap_candidates/index.yaml").exists()
    assert not (clone_path / ".codex/local/roadmap_candidates/index.yaml").exists()
