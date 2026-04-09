from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .helpers import init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_candidate_index import _candidate, _write_backlog


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "review_candidate_pool.py"


def test_review_candidate_pool_reports_degraded_for_expired_promoted_claim(tmp_path: Path) -> None:
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
            "allowed_dirs": ["src/governance_test/stage1-core-contract/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/governance_test/stage1-core-contract/"],
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
            "roadmap_candidate_id": "stage1-core-contract",
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "degraded"
    assert payload["stale_claims"][0]["candidate_id"] == "stage1-core-contract"
    assert payload["candidate_summary"]["takeover_claimable_count"] == 1
    assert payload["candidate_summary"]["ready_count"] == 0


def test_review_candidate_pool_ignores_closed_claim_history(tmp_path: Path) -> None:
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
                    "status": "closed",
                    "formal_task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                    "expires_at": "2026-04-08T00:00:00+08:00",
                    "closed_at": "2026-04-08T00:00:00+08:00",
                }
            ],
        },
    )

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["status"] == "ready"
    assert payload["stale_claims"] == []
    assert payload["candidate_summary"]["claim_status_counts"]["closed"] == 1


def test_review_candidate_pool_is_ready_when_parallel_supply_is_sufficient(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate("stage1-core-contract", status="planned", priority=100),
            _candidate("stage1-source-family-cn", status="planned", priority=110),
            _candidate("stage1-source-family-global", status="planned", priority=120),
            _candidate("stage1-extra-ready-1", status="planned", priority=130),
        ],
    )

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["status"] == "ready"
    assert payload["stale_claims"] == []
    assert payload["slot_issues"] == []
    assert payload["candidate_summary"]["claimable_count"] >= 4
    assert payload["candidate_summary"]["parallelism_deficit"] == 0


def test_review_candidate_pool_blocks_when_governance_runtime_is_dirty(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])
    runtime_file = repo / "scripts/review_candidate_pool.py"
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.write_text(
        "# dirty runtime change for review-pool test\n",
        encoding="utf-8",
        newline="\n",
    )

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert "governance runtime unpublished" in payload["issues"]
    assert "scripts/review_candidate_pool.py" in payload["dirty_governance_runtime_paths"]


def test_review_candidate_pool_reports_root_and_closeout_radar_fields(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate("stage1-core-contract", status="planned", priority=100),
            _candidate("stage1-source-family-cn", status="planned", priority=110),
        ],
    )

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert "root_candidate_count" in payload
    assert "formal_root_count" in payload
    assert "preview_root_count" in payload
    assert "closeout_ready_execution_count" in payload
    assert "top_unlock_value_candidates" in payload
    assert "hard_gate_backlog" in payload


def test_review_candidate_pool_blocks_ready_slot_stale_mirror(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "status": "active",
            "control_plane_root": str(repo).replace("\\", "/"),
            "slots": [
                {
                    "slot_id": "worker-01",
                    "path": str(clone_path).replace("\\", "/"),
                    "branch": "codex/worker-01-idle",
                    "idle_branch": "codex/worker-01-idle",
                    "status": "ready",
                    "current_task_id": None,
                }
            ],
        },
    )
    subprocess.run(["git", "clone", "--local", str(repo), str(clone_path)], check=True, capture_output=True, text=True)
    _write_backlog(repo, [_candidate("stage1-core-contract", status="planned", priority=100)])
    subprocess.run(
        ["git", "switch", "-c", "codex/TASK-RM-STAGE1-SOURCE-FAMILY-CN-stage1-source-family-cn"],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )
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
                    "worker_state": "running",
                    "roadmap_candidate_id": "stage1-core-contract",
                }
            ],
        },
    )

    result = run_python(SCRIPT, repo)
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["ledger_divergence_count"] >= 1
    assert payload["issues"]
