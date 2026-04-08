from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_candidate_index import _candidate, _write_backlog


def _claims_payload() -> dict:
    return {
        "version": "0.1",
        "updated_at": "2026-04-08T00:00:00+08:00",
        "claims": [
            {"candidate_id": "stage1-core-contract", "status": "claimed"},
            {"candidate_id": "stage2-core-contract", "status": "taken_over"},
        ],
    }


def _worktree_pool_payload() -> dict:
    return {
        "version": "1.0",
        "updated_at": "2026-04-08T00:00:00+08:00",
        "slots": [
            {"slot_id": "worker-01", "status": "active"},
            {"slot_id": "worker-02", "status": "idle"},
        ],
    }


def _full_clone_pool_payload(repo: Path) -> dict:
    return {
        "version": "1.0",
        "updated_at": "2026-04-08T00:00:00+08:00",
        "control_plane_root": str(repo).replace("\\", "/"),
        "slots": [
            {"slot_id": "worker-01", "status": "active", "path": str((repo.parent / "clone-01").resolve()).replace("\\", "/")},
            {"slot_id": "worker-02", "status": "ready", "path": str((repo.parent / "clone-02").resolve()).replace("\\", "/")},
        ],
    }


def test_refresh_roadmap_candidates_once_writes_summary(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])
    write_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml", _claims_payload())
    write_yaml(repo / "docs/governance/WORKTREE_POOL.yaml", _worktree_pool_payload())
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", _full_clone_pool_payload(repo))

    result = run_python(TASK_OPS_SCRIPT, repo, "refresh-roadmap-candidates")
    summary = read_yaml(repo / ".codex/local/roadmap_candidates/summary.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert summary["top_candidate_id"] == "stage1-core-contract"
    assert summary["claim_status_counts"]["claimed"] == 1
    assert summary["claim_status_counts"]["taken_over"] == 1
    assert summary["worktree_pool_status_counts"]["active"] == 1
    assert summary["full_clone_pool_status_counts"]["ready"] == 1


def test_refresh_roadmap_candidates_loop_runs_multiple_cycles(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])

    result = run_python(TASK_OPS_SCRIPT, repo, "refresh-roadmap-candidates", "--loop", "--cycles", "2", "--interval-seconds", "1")
    summary = read_yaml(repo / ".codex/local/roadmap_candidates/summary.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "cycle=2" in result.stdout
    assert summary["candidate_count"] == 1
