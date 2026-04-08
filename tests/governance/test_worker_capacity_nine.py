from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, run_python


def test_worker_capacity_expands_to_nine_slots(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    runtime = (repo_root / "scripts/governance_runtime.py").read_text(encoding="utf-8")
    import yaml
    policy = yaml.safe_load((repo_root / "docs/governance/TASK_POLICY.yaml").read_text(encoding="utf-8"))

    assert "range(1, 10)" in runtime
    assert policy["size_classes"]["heavy"]["dynamic_lane_ceiling_v1"] == 9


def test_pool_registries_include_worker_09(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    import yaml
    full_clone_pool = yaml.safe_load((repo_root / "docs/governance/FULL_CLONE_POOL.yaml").read_text(encoding="utf-8"))
    worktree_pool = yaml.safe_load((repo_root / "docs/governance/WORKTREE_POOL.yaml").read_text(encoding="utf-8"))

    assert any(slot["slot_id"] == "worker-09" for slot in full_clone_pool["slots"])
    assert any(slot["slot_id"] == "worker-09" for slot in worktree_pool["slots"])


def test_task_ops_accepts_worker_09_for_worktree_commands(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    help_result = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", "--help")

    assert help_result.returncode == 0
    assert "worker-09" in help_result.stdout
