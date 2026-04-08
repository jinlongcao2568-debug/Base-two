from __future__ import annotations

import json
from pathlib import Path

from .helpers import init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_candidate_index import _candidate, _write_backlog


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "review_candidate_pool.py"


def test_review_candidate_pool_reports_stale_claims_and_incomplete_tasks(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])
    write_yaml(
        repo / ".codex/local/roadmap_candidates/claims.yaml",
        {
            "version": "0.1",
            "claims": [
                {
                    "candidate_id": "stage1-core-contract",
                    "status": "promoted",
                    "formal_task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                    "expires_at": "2026-04-08T00:00:00+08:00",
                }
            ],
        },
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
            "title": "stage1 contract",
            "status": "review",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": None,
            "stage": "stage1",
            "branch": "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "review_pending",
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
            "review_bundle_status": "pending",
            "successor_state": None,
            "created_at": "2026-04-08T00:00:00+08:00",
            "activated_at": "2026-04-08T00:00:00+08:00",
            "closed_at": None,
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["stale_claims"][0]["candidate_id"] == "stage1-core-contract"
    assert payload["incomplete_tasks"][0]["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"


def test_review_candidate_pool_is_ready_after_full_clone_slot_is_reconciled(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "control_plane_root": str(repo).replace("\\", "/"),
            "slots": [
                {
                    "slot_id": "worker-01",
                    "path": str((repo.parent / "clone-01").resolve()).replace("\\", "/"),
                    "branch": "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract",
                    "idle_branch": "codex/worker-01-idle",
                    "status": "active",
                    "current_task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                }
            ],
        },
    )
    write_yaml(
        repo / ".codex/local/roadmap_candidates/claims.yaml",
        {
            "version": "0.1",
            "claims": [
                {
                    "candidate_id": "stage1-core-contract",
                    "status": "promoted",
                    "formal_task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                    "dispatch_target": "full_clone",
                    "expires_at": "2099-04-08T00:00:00+08:00",
                }
            ],
        },
    )
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

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["status"] == "ready"
    assert payload["stale_claims"] == []
    assert payload["slot_issues"] == []
