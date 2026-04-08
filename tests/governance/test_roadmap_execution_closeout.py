from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_claim_promotion import _stage_candidate
from .test_roadmap_candidate_index import _candidate, _write_backlog


def _stage1_child(candidate_id: str, *, priority: int, path: str) -> dict:
    candidate = _candidate(candidate_id, status="waiting", priority=priority, depends_on=["stage1-core-contract"])
    candidate["planned_write_paths"] = [path]
    candidate["allowed_dirs"] = [path]
    candidate["protected_paths"] = [path]
    candidate["branch_template"] = f"codex/{{task_id}}-{candidate_id}"
    return candidate


def test_close_ready_execution_tasks_closes_review_task_and_releases_child_roots(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktree_root = tmp_path / "worktrees"
    _write_backlog(
        repo,
        [
            _stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _stage1_child("stage1-source-family-cn", priority=110, path="src/stage1_orchestration/source_families/cn/"),
            _stage1_child("stage1-source-family-global", priority=120, path="src/stage1_orchestration/source_families/global/"),
        ],
    )

    promoted = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--worktree-root", str(worktree_root))
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-RM-STAGE1-CORE-CONTRACT",
        "--summary",
        "review ready",
        "--tests",
        "pytest tests/stage1 -q",
    )
    closeout = run_python(TASK_OPS_SCRIPT, repo, "close-ready-execution-tasks")
    refreshed = run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")
    index = read_yaml(repo / ".codex/local/roadmap_candidates/index.yaml")
    stage1_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT")
    by_id = {candidate["candidate_id"]: candidate for candidate in index["candidates"]}

    assert promoted.returncode == 0, promoted.stdout + promoted.stderr
    assert finished.returncode == 0, finished.stdout + finished.stderr
    assert closeout.returncode == 0, closeout.stdout + closeout.stderr
    assert refreshed.returncode == 0, refreshed.stdout + refreshed.stderr
    assert stage1_task["status"] == "done"
    assert claims["claims"][0]["status"] == "closed"
    assert by_id["stage1-source-family-cn"]["status"] == "ready"
    assert by_id["stage1-source-family-global"]["status"] == "ready"
