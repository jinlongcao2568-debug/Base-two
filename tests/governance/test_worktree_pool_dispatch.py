from __future__ import annotations

import pytest
pytestmark = pytest.mark.slow

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_claim_promotion import _stage_candidate
from .test_roadmap_candidate_index import _write_backlog


def _write_pool(repo: Path, slots: list[dict]) -> None:
    write_yaml(
        repo / "docs/governance/WORKTREE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-07T00:00:00+08:00",
            "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
            "status": "active",
            "slots": slots,
        },
    )


def _slot(slot_id: str, path: str, *, status: str = "idle") -> dict:
    return {
        "slot_id": slot_id,
        "worker_owner": slot_id,
        "path": path,
        "status": status,
        "current_task_id": None,
        "branch": None,
        "last_claimed_at": None,
        "last_released_at": None,
    }


def test_claim_next_promote_uses_idle_pool_slot_when_no_worktree_root_is_given(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_pool(
        repo,
        [
            _slot("worker-01", "../worker-pool/worker-01"),
            _slot("worker-02", "../worker-pool/worker-02"),
        ],
    )
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task")
    pool = read_yaml(repo / "docs/governance/WORKTREE_POOL.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    slot = next(item for item in pool["slots"] if item["slot_id"] == "worker-01")
    assert slot["status"] == "active"
    assert slot["current_task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"
    assert (tmp_path / "worker-pool" / "worker-01").exists()


def test_claim_next_promote_uses_next_idle_pool_slot_for_second_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_pool(
        repo,
        [
            _slot("worker-01", "../worker-pool/worker-01"),
            _slot("worker-02", "../worker-pool/worker-02"),
        ],
    )
    _write_backlog(
        repo,
        [
            _stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _stage_candidate("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )

    first = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task")
    second = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task")
    pool = read_yaml(repo / "docs/governance/WORKTREE_POOL.yaml")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    slot_one = next(item for item in pool["slots"] if item["slot_id"] == "worker-01")
    slot_two = next(item for item in pool["slots"] if item["slot_id"] == "worker-02")
    assert slot_one["current_task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"
    assert slot_two["current_task_id"] == "TASK-RM-STAGE2-CORE-CONTRACT"


def test_claim_next_promote_blocks_when_pool_has_no_idle_slot(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_pool(repo, [_slot("worker-01", "../worker-pool/worker-01", status="active")])
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task")

    assert result.returncode == 1
    assert "no idle worktree pool slot is available" in result.stdout


def test_worktree_release_returns_pool_slot_to_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_pool(repo, [_slot("worker-01", "../worker-pool/worker-01")])
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    promoted = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task")
    released = run_python(TASK_OPS_SCRIPT, repo, "worktree-release", "TASK-RM-STAGE1-CORE-CONTRACT")
    pool = read_yaml(repo / "docs/governance/WORKTREE_POOL.yaml")

    assert promoted.returncode == 0, promoted.stdout + promoted.stderr
    assert released.returncode == 0, released.stdout + released.stderr
    slot = pool["slots"][0]
    assert slot["status"] == "idle"
    assert slot["current_task_id"] is None
