from __future__ import annotations

import pytest
pytestmark = pytest.mark.slow

import subprocess
from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane
from .test_roadmap_claim_promotion import _stage_candidate
from .test_roadmap_candidate_index import _write_backlog


def _expire_claim(repo: Path, candidate_id: str) -> None:
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")
    claim = next(item for item in claims["claims"] if item["candidate_id"] == candidate_id)
    claim["expires_at"] = "2026-04-07T00:00:00+08:00"
    with (repo / ".codex/local/roadmap_candidates/claims.yaml").open("w", encoding="utf-8", newline="\n") as handle:
        import yaml

        yaml.safe_dump(claims, handle, allow_unicode=True, sort_keys=False)


def test_claim_next_takeover_reuses_stale_promoted_task_without_duplicate_registry_row(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktree_root = tmp_path / "worktrees"
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

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
    _expire_claim(repo, "stage1-core-contract")

    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--worktree-root",
        str(worktree_root),
        "--window-id",
        "window-b",
        "--now",
        "2026-04-07T12:00:00+08:00",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert "claim-next taken-over candidate_id=stage1-core-contract" in second.stdout
    assert len([task for task in registry["tasks"] if task["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"]) == 1
    claim = claims["claims"][0]
    assert claim["status"] == "taken_over"
    assert claim["window_id"] == "window-b"


def test_claim_next_takeover_blocks_dirty_stale_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktree_root = tmp_path / "worktrees"
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    first = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--worktree-root", str(worktree_root))
    takeover_path = worktree_root / "TASK-RM-STAGE1-CORE-CONTRACT" / "src" / "stage1_orchestration"
    takeover_path.mkdir(parents=True, exist_ok=True)
    (takeover_path / "dirty.py").write_text("print('dirty')\n", encoding="utf-8")
    _expire_claim(repo, "stage1-core-contract")

    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--worktree-root",
        str(worktree_root),
        "--now",
        "2026-04-07T12:00:00+08:00",
    )

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 1
    assert "stale worktree is dirty" in second.stdout


def test_claim_next_takeover_recreates_missing_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktree_root = tmp_path / "worktrees"
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    first = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--worktree-root", str(worktree_root))
    worktree_path = worktree_root / "TASK-RM-STAGE1-CORE-CONTRACT"
    subprocess.run(["git", "worktree", "remove", "--force", str(worktree_path)], cwd=repo, check=True, capture_output=True, text=True)
    _expire_claim(repo, "stage1-core-contract")

    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--worktree-root",
        str(worktree_root),
        "--now",
        "2026-04-07T12:00:00+08:00",
    )

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert worktree_path.exists()
