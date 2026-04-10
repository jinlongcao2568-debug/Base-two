from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane
from .test_roadmap_candidate_index import _candidate, _write_backlog


def test_claim_next_promote_generates_execution_brief_and_mirrors(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])
    worktree_root = tmp_path / "worktrees"

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--worktree-root",
        str(worktree_root),
        "--window-id",
        "brief-test",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(task for task in registry["tasks"] if task.get("roadmap_candidate_id") == "stage1-core-contract")
    brief_path = repo / "docs/governance/dispatch_briefs" / f"{task['task_id']}.yaml"
    assert brief_path.exists()
    brief = read_yaml(brief_path)
    for field in (
        "why_now",
        "depends_on",
        "blocked_by",
        "allowed_dirs",
        "reserved_paths",
        "required_tests",
        "executor_target",
        "what_this_unlocks_next",
        "closeout_path",
    ):
        assert field in brief
    assert brief["formal_task_id"] == task["task_id"]
    assert brief["allowed_dirs"] == task["allowed_dirs"]

    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == task["task_id"])
    mirrored_path = Path(entry["path"]) / ".codex/local/EXECUTION_BRIEF.yaml"
    assert mirrored_path.exists()
    mirrored = read_yaml(mirrored_path)
    assert mirrored["formal_task_id"] == task["task_id"]
