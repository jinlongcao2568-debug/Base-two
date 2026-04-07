from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane
from .test_roadmap_candidate_index import _candidate, _write_backlog


def _stage_candidate(candidate_id: str, *, priority: int, paths: list[str]) -> dict:
    candidate = _candidate(candidate_id, status="planned", priority=priority)
    candidate["allowed_dirs"] = paths
    candidate["planned_write_paths"] = paths
    candidate["planned_test_paths"] = ["tests/stage1/"]
    candidate["required_tests"] = ["pytest tests/stage1 -q"]
    candidate["reserved_paths"] = ["src/stage6_facts/"]
    candidate["branch_template"] = f"codex/{{task_id}}-{candidate_id}"
    candidate["worktree_template"] = "../AX9.worktrees/{task_id}"
    return candidate


def test_claim_next_promotes_candidate_to_execution_task_and_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktree_root = tmp_path / "worktrees"
    _write_backlog(
        repo,
        [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--worktree-root", str(worktree_root))
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == task["task_id"])

    assert result.returncode == 0, result.stdout + result.stderr
    assert "claim-next promoted candidate_id=stage1-core-contract" in result.stdout
    assert task["task_kind"] == "execution"
    assert task["execution_mode"] == "isolated_worktree"
    assert task["status"] == "doing"
    assert task["planned_write_paths"] == ["src/stage1_orchestration/"]
    assert (repo / "docs/governance/tasks/TASK-RM-STAGE1-CORE-CONTRACT.md").exists()
    assert (worktree_root / "TASK-RM-STAGE1-CORE-CONTRACT").exists()
    assert entry["status"] == "active"
    assert entry["work_mode"] == "execution"
    assert claims["claims"][0]["status"] == "promoted"
    assert claims["claims"][0]["formal_task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"


def test_claim_next_promote_second_window_skips_active_claim_and_allocates_disjoint_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktree_root = tmp_path / "worktrees"
    _write_backlog(
        repo,
        [
            _stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _stage_candidate("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )

    first = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--worktree-root",
        str(worktree_root),
        "--window-id",
        "window-a",
    )
    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--worktree-root",
        str(worktree_root),
        "--window-id",
        "window-b",
    )
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert "candidate_id=stage1-core-contract" in first.stdout
    assert "candidate_id=stage2-core-contract" in second.stdout
    active_execution = [
        entry
        for entry in worktrees["entries"]
        if entry.get("work_mode") == "execution" and entry.get("status") == "active"
    ]
    assert {entry["task_id"] for entry in active_execution} == {
        "TASK-RM-STAGE1-CORE-CONTRACT",
        "TASK-RM-STAGE2-CORE-CONTRACT",
    }


def test_claim_next_promote_blocks_duplicate_existing_candidate_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktree_root = tmp_path / "worktrees"
    _write_backlog(
        repo,
        [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])],
    )

    first = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--worktree-root", str(worktree_root))
    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--worktree-root",
        str(worktree_root),
        "--now",
        "2026-04-07T22:00:00+08:00",
    )

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 1
    assert "no safe roadmap candidate" in second.stdout
