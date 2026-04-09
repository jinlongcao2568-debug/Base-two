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
        "version": "1.1",
        "updated_at": "2026-04-08T00:00:00+08:00",
        "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
        "status": "draft",
        "lane_types": LANE_TYPES,
        "candidate_status_values": STATUS_VALUES,
        "required_top_level_fields": REQUIRED_TOP_LEVEL_FIELDS,
        "required_candidate_fields": REQUIRED_CANDIDATE_FIELDS,
    }


def _candidate(
    candidate_id: str,
    *,
    status: str,
    priority: int,
    depends_on: list[str] | None = None,
    candidate_kind: str = "lane_slice",
    claimable: bool = True,
    stage: str = "stage2",
    allow_create_paths: bool = True,
    pilot_only: bool = False,
    coverage_regions: list[str] | None = None,
) -> dict:
    scope_path = f"src/governance_test/{candidate_id}/"
    payload = {
        "candidate_id": candidate_id,
        "title": candidate_id,
        "stage": stage,
        "module_id": "stage1_orchestration",
        "candidate_kind": candidate_kind,
        "claimable": claimable,
        "parent_candidate_id": None,
        "lane_type": "integration_gate" if "integration" in candidate_id else ("core_contract" if "core" in candidate_id else "stage_internal_parallel"),
        "status": status,
        "priority": priority,
        "depends_on": list(depends_on or []),
        "unlocks": [],
        "allowed_dirs": [scope_path],
        "forbidden_write_paths": ["src/stage6_facts/"],
        "protected_paths": [],
        "planned_write_paths": [scope_path],
        "planned_test_paths": ["tests/governance/"],
        "required_tests": ["python scripts/check_repo.py"],
        "allow_create_paths": allow_create_paths,
        "pilot_only": pilot_only,
        "branch_template": "codex/{task_id}",
        "worktree_template": "../AX9.worktrees/{task_id}",
        "integration_gate": None,
        "expected_children": [],
        "completion_policy": "none",
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

    payload["coverage_regions"] = coverage_regions if coverage_regions is not None else ["CN"]
    return payload


def _write_backlog(repo: Path, candidates: list[dict]) -> None:
    write_yaml(repo / "docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml", _schema())
    write_yaml(
        repo / "docs/governance/ROADMAP_BACKLOG.yaml",
        {
            "version": "0.2",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
            "defaults": {"legacy_reserved_paths_map_to": "forbidden_write_paths"},
            "compiler_policy": {"mode": "inline_candidates"},
            "scheduler_policy": {
                "entrypoint": "claim-next",
                "claim_capacity_source": "docs/governance/TASK_POLICY.yaml#roadmap_scheduler.max_active_claims_v1",
                "single_writer_roots": [],
            },
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
            _candidate("stage1-source-family-cn", status="waiting", priority=110, depends_on=["stage1-core-contract"]),
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
    assert index["fresh_claimable_candidate_ids"] == ["stage1-core-contract"]
    assert _candidate_by_id(index, "stage1-source-family-cn")["status"] == "waiting"
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
            _candidate("stage1-source-family-cn", status="waiting", priority=110, depends_on=["stage1-core-contract"]),
        ],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")
    index = read_yaml(repo / ".codex/local/roadmap_candidates/index.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert _candidate_by_id(index, "stage1-core-contract")["status"] == "done"
    assert _candidate_by_id(index, "stage1-source-family-cn")["status"] == "ready"
    assert _candidate_by_id(index, "stage1-source-family-cn")["wait_reasons"] == []


def test_plan_roadmap_candidates_marks_expired_promoted_claim_as_takeover_not_ready(tmp_path: Path) -> None:
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
                    "candidate_worktree": str((repo / "missing-worktree").resolve()).replace("\\", "/"),
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
            "branch": "codex/TASK-RM-STAGE1-CORE-CONTRACT",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "idle",
            "blocked_reason": None,
            "last_reported_at": "2026-04-08T00:00:00+08:00",
            "topology": "single_task",
                "allowed_dirs": ["src/governance_test/stage1-core-contract/"],
                "reserved_paths": [],
                "planned_write_paths": ["src/governance_test/stage1-core-contract/"],
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
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
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    result = run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")
    index = read_yaml(repo / ".codex/local/roadmap_candidates/index.yaml")
    candidate = _candidate_by_id(index, "stage1-core-contract")

    assert result.returncode == 0, result.stdout + result.stderr
    assert index["ready_candidate_ids"] == []
    assert index["fresh_claimable_candidate_ids"] == []
    assert index["takeover_candidate_ids"] == ["stage1-core-contract"]
    assert candidate["status"] == "stale"
    assert candidate["takeover_mode"] == "expired_promoted_takeover"


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
