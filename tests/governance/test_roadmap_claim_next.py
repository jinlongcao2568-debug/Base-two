from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_candidate_index import _candidate, _write_backlog


def _candidate_with_paths(candidate_id: str, *, priority: int, paths: list[str]) -> dict:
    candidate = _candidate(candidate_id, status="planned", priority=priority)
    candidate["planned_write_paths"] = paths
    candidate["allowed_dirs"] = paths
    candidate["branch_template"] = f"codex/{{task_id}}-{candidate_id}"
    return candidate


def _append_active_task(repo: Path, *, task_id: str, branch: str, paths: list[str]) -> None:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": task_id,
            "title": "active task",
            "status": "doing",
            "task_kind": "coordination",
            "execution_mode": "shared_coordination",
            "parent_task_id": None,
            "stage": "governance-test",
            "branch": branch,
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "running",
            "blocked_reason": None,
            "last_reported_at": "2026-04-07T00:00:00+08:00",
            "topology": "single_worker",
            "allowed_dirs": paths,
            "reserved_paths": [],
            "planned_write_paths": paths,
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
            "task_file": f"docs/governance/tasks/{task_id}.md",
            "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "successor_state": "backlog",
            "created_at": "2026-04-07T00:00:00+08:00",
            "activated_at": "2026-04-07T00:00:00+08:00",
            "closed_at": None,
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)


def test_claim_next_dry_run_selects_top_ready_candidate_without_claim_file(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _candidate_with_paths("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate_id=stage1-core-contract" in result.stdout
    assert not (repo / ".codex/local/roadmap_candidates/claims.yaml").exists()


def test_claim_next_write_claim_makes_second_window_choose_next_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _candidate_with_paths("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )

    first = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--write-claim", "--window-id", "window-a")
    second = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--write-claim", "--window-id", "window-b")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert "candidate_id=stage1-core-contract" in first.stdout
    assert "candidate_id=stage2-core-contract" in second.stdout
    assert [claim["candidate_id"] for claim in claims["claims"]] == [
        "stage1-core-contract",
        "stage2-core-contract",
    ]


def test_claim_next_blocks_when_active_task_overlaps_ready_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
        ],
    )
    _append_active_task(
        repo,
        task_id="TASK-ACTIVE-001",
        branch="codex/TASK-ACTIVE-001",
        paths=["src/stage1_orchestration/"],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 1
    assert "no safe roadmap candidate" in result.stdout
    assert "write-path overlap with TASK-ACTIVE-001" in result.stdout
