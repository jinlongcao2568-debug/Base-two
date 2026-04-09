from __future__ import annotations

import pytest
pytestmark = pytest.mark.slow

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane
from .test_roadmap_claim_promotion import _stage_candidate
from .test_roadmap_candidate_index import _write_backlog
from .test_worktree_pool_dispatch import _slot, _write_pool


def test_prewarm_worktree_pool_creates_idle_git_worktrees(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_pool(
        repo,
        [
            _slot("worker-01", "../worker-pool/worker-01"),
            _slot("worker-02", "../worker-pool/worker-02"),
        ],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "prewarm-worktree-pool")
    pool = read_yaml(repo / "docs/governance/WORKTREE_POOL.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "worker-01" in result.stdout and "worker-02" in result.stdout
    assert (tmp_path / "worker-pool" / "worker-01" / ".git").exists()
    assert (tmp_path / "worker-pool" / "worker-02" / ".git").exists()
    assert pool["slots"][0]["branch"] == "codex/worker-01-idle"
    assert pool["slots"][1]["branch"] == "codex/worker-02-idle"


def test_claim_next_promote_reuses_prewarmed_idle_slot(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_pool(repo, [_slot("worker-01", "../worker-pool/worker-01")])
    prewarm = run_python(TASK_OPS_SCRIPT, repo, "prewarm-worktree-pool")
    assert prewarm.returncode == 0, prewarm.stdout + prewarm.stderr
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task")
    pool = read_yaml(repo / "docs/governance/WORKTREE_POOL.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert pool["slots"][0]["status"] == "active"
    assert pool["slots"][0]["branch"] == "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract"


def test_worktree_release_rewarms_idle_pool_slot(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_pool(repo, [_slot("worker-01", "../worker-pool/worker-01")])
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    promoted = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task")
    released = run_python(TASK_OPS_SCRIPT, repo, "worktree-release", "TASK-RM-STAGE1-CORE-CONTRACT")
    pool = read_yaml(repo / "docs/governance/WORKTREE_POOL.yaml")

    assert promoted.returncode == 0, promoted.stdout + promoted.stderr
    assert released.returncode == 0, released.stdout + released.stderr
    assert (tmp_path / "worker-pool" / "worker-01" / ".git").exists()
    assert pool["slots"][0]["status"] == "idle"
    assert pool["slots"][0]["branch"] == "codex/worker-01-idle"
