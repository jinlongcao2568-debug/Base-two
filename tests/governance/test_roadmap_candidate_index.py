from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml


LANE_TYPES = {
    "core_contract": {"parallel_policy": "single_writer"},
    "stage_internal_parallel": {"parallel_policy": "disjoint_paths_required"},
    "integration_gate": {"parallel_policy": "single_writer"},
}
STATUS_VALUES = [
    "planned",
    "ready",
    "waiting",
    "claimed",
    "running",
    "stale",
    "resumable",
    "blocked",
    "review",
    "done",
    "closed",
]
REQUIRED_TOP_LEVEL_FIELDS = [
    "version",
    "updated_at",
    "authority_source",
    "scheduler_policy",
    "stages",
    "candidates",
]
REQUIRED_CANDIDATE_FIELDS = [
    "candidate_id",
    "title",
    "stage",
    "module_id",
    "lane_type",
    "status",
    "priority",
    "depends_on",
    "unlocks",
    "allowed_dirs",
    "reserved_paths",
    "planned_write_paths",
    "planned_test_paths",
    "required_tests",
    "branch_template",
    "worktree_template",
    "integration_gate",
    "claim_policy",
    "takeover_policy",
]


def _schema() -> dict:
    return {
        "version": "1.0",
        "updated_at": "2026-04-07T00:00:00+08:00",
        "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
        "status": "draft",
        "lane_types": LANE_TYPES,
        "candidate_status_values": STATUS_VALUES,
        "required_top_level_fields": REQUIRED_TOP_LEVEL_FIELDS,
        "required_candidate_fields": REQUIRED_CANDIDATE_FIELDS,
    }


def _candidate(candidate_id: str, *, status: str, priority: int, depends_on: list[str] | None = None) -> dict:
    return {
        "candidate_id": candidate_id,
        "title": candidate_id,
        "stage": "stage1",
        "module_id": "stage1_orchestration",
        "lane_type": "core_contract" if "core" in candidate_id else "stage_internal_parallel",
        "status": status,
        "priority": priority,
        "depends_on": list(depends_on or []),
        "unlocks": [],
        "allowed_dirs": ["docs/governance/"],
        "reserved_paths": ["src/"],
        "planned_write_paths": ["docs/governance/"],
        "planned_test_paths": ["tests/governance/"],
        "required_tests": ["python scripts/check_repo.py"],
        "branch_template": "codex/{task_id}",
        "worktree_template": "../AX9.worktrees/{task_id}",
        "integration_gate": None,
        "claim_policy": {
            "one_window_one_candidate": True,
            "conflict_policy": "choose_next_safe_candidate",
            "scheduler_lock_required": True,
        },
        "takeover_policy": {
            "stale_after_minutes_source": "docs/governance/HANDOFF_POLICY.yaml",
            "clean_worktree_takeover": "allow",
            "scoped_dirty_checkpoint": "allow_before_takeover",
            "out_of_scope_dirty_policy": "block_for_human_decision",
        },
    }


def _write_backlog(repo: Path, candidates: list[dict]) -> None:
    write_yaml(repo / "docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml", _schema())
    write_yaml(
        repo / "docs/governance/ROADMAP_BACKLOG.yaml",
        {
            "version": "0.1",
            "updated_at": "2026-04-07T00:00:00+08:00",
            "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
            "scheduler_policy": {"entrypoint": "claim-next"},
            "stages": [{"stage": "stage1", "module_id": "stage1_orchestration"}],
            "candidates": candidates,
        },
    )


def _candidate_by_id(index: dict, candidate_id: str) -> dict:
    return next(candidate for candidate in index["candidates"] if candidate["candidate_id"] == candidate_id)


def test_plan_roadmap_candidates_derives_ready_waiting_and_controlled_statuses(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate("stage1-core-contract", status="planned", priority=100),
            _candidate("stage1-source-family-lanes", status="waiting", priority=110, depends_on=["stage1-core-contract"]),
            _candidate("stage1-blocked-lane", status="blocked", priority=120),
            _candidate("stage1-claimed-lane", status="claimed", priority=130),
            _candidate("stage1-stale-lane", status="stale", priority=140),
        ],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")
    index = read_yaml(repo / ".codex/local/roadmap_candidates/index.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert index["candidate_count"] == 5
    assert index["ready_candidate_ids"] == ["stage1-core-contract"]
    assert _candidate_by_id(index, "stage1-source-family-lanes")["status"] == "waiting"
    assert _candidate_by_id(index, "stage1-blocked-lane")["status"] == "blocked"
    assert _candidate_by_id(index, "stage1-claimed-lane")["status"] == "claimed"
    assert _candidate_by_id(index, "stage1-stale-lane")["status"] == "stale"


def test_plan_roadmap_candidates_unlocks_dependency_after_candidate_done(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate("stage1-core-contract", status="done", priority=100),
            _candidate("stage1-source-family-lanes", status="waiting", priority=110, depends_on=["stage1-core-contract"]),
        ],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")
    index = read_yaml(repo / ".codex/local/roadmap_candidates/index.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert _candidate_by_id(index, "stage1-core-contract")["status"] == "done"
    assert _candidate_by_id(index, "stage1-source-family-lanes")["status"] == "ready"
    assert _candidate_by_id(index, "stage1-source-family-lanes")["wait_reasons"] == []


def test_plan_roadmap_candidates_rejects_unknown_stage_candidate_reference(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate("stage1-core-contract", status="planned", priority=100, depends_on=["stage1-missing-gate"]),
        ],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")

    assert result.returncode == 1
    assert "references unknown candidate" in result.stdout
