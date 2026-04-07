from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, write_yaml


def _pool(repo: Path) -> dict:
    return {
        "version": "1.0",
        "updated_at": "2026-04-07T00:00:00+08:00",
        "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
        "status": "active",
        "root_path": str((repo.parent / "clones").resolve()).replace("\\", "/"),
        "slots": [
            {
                "slot_id": "worker-01",
                "path": str((repo.parent / "clones" / "worker-01").resolve()).replace("\\", "/"),
                "branch": "main",
                "status": "pending",
                "last_provisioned_at": None,
            },
            {
                "slot_id": "worker-02",
                "path": str((repo.parent / "clones" / "worker-02").resolve()).replace("\\", "/"),
                "branch": "main",
                "status": "pending",
                "last_provisioned_at": None,
            },
        ],
    }


def test_provision_full_clone_pool_creates_complete_clone_directories(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", _pool(repo))

    result = run_python(TASK_OPS_SCRIPT, repo, "provision-full-clone-pool")
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "worker-01" in result.stdout and "worker-02" in result.stdout
    assert (tmp_path / "clones" / "worker-01" / ".git").exists()
    assert (tmp_path / "clones" / "worker-02" / ".git").exists()
    assert pool["slots"][0]["status"] == "ready"
    assert pool["slots"][1]["status"] == "ready"
