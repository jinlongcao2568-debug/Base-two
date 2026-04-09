from __future__ import annotations

import json
from pathlib import Path
import sys

from .helpers import TASK_OPS_SCRIPT, git_commit_all, init_governance_repo, read_yaml, run_python, write_yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from control_plane_root import build_governance_runtime_stamp, published_governance_runtime_dirty_paths  # noqa: E402


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


def test_provision_full_clone_pool_preserves_active_slot_metadata(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    pool = _pool(repo)
    pool["slots"][0]["branch"] = "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract"
    pool["slots"][0]["status"] = "ready"
    pool["slots"][0]["current_task_id"] = "TASK-RM-STAGE1-CORE-CONTRACT"
    pool["slots"][0]["idle_branch"] = "codex/worker-01-idle"
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", pool)

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
            "title": "stage1 contract",
            "status": "paused",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": None,
            "stage": "stage1",
            "branch": "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "idle",
            "blocked_reason": None,
            "last_reported_at": "2026-04-08T00:00:00+08:00",
            "topology": "single_task",
            "allowed_dirs": ["src/stage1_orchestration/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/stage1_orchestration/"],
            "planned_test_paths": ["tests/stage1/"],
            "required_tests": ["pytest tests/stage1 -q"],
            "task_file": "docs/governance/tasks/TASK-RM-STAGE1-CORE-CONTRACT.md",
            "runlog_file": "docs/governance/runlogs/TASK-RM-STAGE1-CORE-CONTRACT-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "successor_state": None,
            "created_at": "2026-04-08T00:00:00+08:00",
            "activated_at": "2026-04-08T00:00:00+08:00",
            "closed_at": None,
            "roadmap_candidate_id": "stage1-core-contract",
            "integration_gate": "stage1-integration-gate",
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    result = run_python(TASK_OPS_SCRIPT, repo, "provision-full-clone-pool", "--refresh")
    repaired_pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert repaired_pool["slots"][0]["status"] == "active"
    assert repaired_pool["slots"][0]["current_task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"
    assert claims["claims"][0]["dispatch_target"] == "full_clone"


def test_audit_full_clone_pool_reports_ready_slot_runtime_drift(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    pool = _pool(repo)
    pool["slots"][0]["status"] = "ready"
    pool["slots"][0]["branch"] = "codex/worker-01-idle"
    pool["slots"][0]["idle_branch"] = "codex/worker-01-idle"
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", pool)
    clone_path = Path(pool["slots"][0]["path"])
    clone_path.mkdir(parents=True, exist_ok=True)
    (clone_path / ".git").mkdir()
    write_yaml(
        clone_path / "docs/governance/TASK_REGISTRY.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "tasks": [
                {
                    "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                    "status": "doing",
                    "task_kind": "execution",
                    "roadmap_candidate_id": "stage1-core-contract",
                }
            ],
        },
    )
    write_yaml(
        clone_path / ".codex/local/roadmap_candidates/index.yaml",
        {
            "version": "0.1",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "candidates": [{"candidate_id": "stage1-source-family-lanes"}],
        },
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "audit-full-clone-pool")
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["ledger_divergence_count"] >= 1
    slot = next(item for item in payload["slots"] if item["slot_id"] == "worker-01")
    assert slot["divergent"] is True
    assert slot["non_terminal_execution_tasks"]
    assert slot["candidate_cache_issues"]


def test_rebuild_full_clone_pool_restores_runtime_stamp_parity_for_idle_slot(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", _pool(repo))
    git_commit_all(repo, "prepare committed runtime parity")

    rebuilt = run_python(TASK_OPS_SCRIPT, repo, "rebuild-full-clone-pool", "--slot-id", "worker-01")
    audit = run_python(TASK_OPS_SCRIPT, repo, "audit-full-clone-pool", "--slot-id", "worker-01")
    payload = json.loads(audit.stdout)
    slot = payload["slots"][0]

    assert rebuilt.returncode == 0, rebuilt.stdout + rebuilt.stderr
    assert audit.returncode == 0, audit.stdout + audit.stderr
    assert slot["runtime_drift"] is False
    assert slot["divergent"] is False


def test_governance_runtime_stamp_uses_published_head_not_dirty_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    baseline = build_governance_runtime_stamp(repo)
    runtime_file = repo / "scripts/review_candidate_pool.py"
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.write_text(
        "# dirty runtime change for published stamp test\n",
        encoding="utf-8",
        newline="\n",
    )

    updated = build_governance_runtime_stamp(repo)
    dirty_paths = published_governance_runtime_dirty_paths(repo)

    assert "scripts/review_candidate_pool.py" in dirty_paths
    assert updated["governance_scripts_hash"] == baseline["governance_scripts_hash"]
    assert updated["control_plane_head"] == baseline["control_plane_head"]
