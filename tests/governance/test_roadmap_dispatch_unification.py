from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, git_commit_all, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_candidate_compiler import _write_compiler_mode_files


def _write_pool(repo: Path) -> None:
    write_yaml(
        repo / "docs/governance/WORKTREE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
            "status": "active",
            "slots": [
                {
                    "slot_id": "worker-01",
                    "worker_owner": "worker-01",
                    "path": "../worker-pool/worker-01",
                    "status": "idle",
                    "current_task_id": None,
                    "branch": "codex/worker-01-idle",
                    "last_claimed_at": None,
                    "last_released_at": None,
                    "idle_branch": "codex/worker-01-idle",
                }
            ],
        },
    )


def test_continue_roadmap_from_idle_claims_compiled_roadmap_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_compiler_mode_files(repo)
    _write_pool(repo)
    git_commit_all(repo, "enable compiled roadmap dispatch")
    compiled = run_python(TASK_OPS_SCRIPT, repo, "compile-roadmap-candidates")
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    roadmap_tasks = [task for task in registry["tasks"] if task["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"]

    assert result.returncode == 0, result.stdout + result.stderr
    assert "continue-roadmap claimed roadmap candidate stage1-core-contract" in result.stdout
    assert len(roadmap_tasks) == 1
    assert current_task["status"] == "idle"
    assert not any(task["task_id"].startswith("TASK-AUTO-") and task["status"] != "done" for task in registry["tasks"])


def test_plan_coordination_does_not_generate_roadmap_autopilot_when_compiled_dispatch_enabled(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_compiler_mode_files(repo)
    git_commit_all(repo, "enable compiled roadmap dispatch")

    result = run_python(TASK_OPS_SCRIPT, repo, "plan-coordination")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate-task-auto" not in result.stdout.lower()
