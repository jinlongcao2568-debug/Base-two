from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

from .helpers import init_governance_repo, read_yaml, set_idle_control_plane, write_mvp_scope, write_yaml
from .test_roadmap_candidate_index import _candidate, _write_backlog


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "roadmap_scheduler_eval.py"
if str(SCRIPT_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_PATH.parent))
SPEC = importlib.util.spec_from_file_location("roadmap_scheduler_eval", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _set_business_scope(repo: Path, scope: str) -> None:
    roadmap_path = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    roadmap = roadmap_path.read_text(encoding="utf-8")
    for current in ("stage1_to_stage9", "stage1_to_stage6", "stage2_to_stage6"):
        roadmap = roadmap.replace(f"business_automation_scope: {current}", f"business_automation_scope: {scope}")
    roadmap_path.write_text(roadmap, encoding="utf-8")


def test_evaluator_marks_lane_group_non_claimable_and_children_claimable(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    group = _candidate("stage1-source-family-group", status="waiting", priority=110, candidate_kind="lane_group", claimable=False)
    group["expected_children"] = ["stage1-source-family-cn", "stage1-source-family-global"]
    group["planned_write_paths"] = []
    cn = _candidate("stage1-source-family-cn", status="waiting", priority=111, depends_on=["stage1-core-contract"])
    cn["planned_write_paths"] = ["src/stage1_orchestration/source_families/cn/"]
    cn["protected_paths"] = ["src/stage1_orchestration/source_families/cn/"]
    global_slice = _candidate("stage1-source-family-global", status="waiting", priority=112, depends_on=["stage1-core-contract"])
    global_slice["planned_write_paths"] = ["src/stage1_orchestration/source_families/global/"]
    global_slice["protected_paths"] = ["src/stage1_orchestration/source_families/global/"]
    gate = _candidate("stage1-source-family-integration-gate", status="waiting", priority=190)
    gate["candidate_kind"] = "integration_gate"
    gate["lane_type"] = "integration_gate"
    gate["depends_on"] = ["stage1-core-contract"]
    gate["expected_children"] = ["stage1-source-family-cn", "stage1-source-family-global"]
    gate["completion_policy"] = "all_expected_children_done"
    _write_backlog(repo, [_candidate("stage1-core-contract", status="done", priority=100), group, cn, global_slice, gate])

    payload = MODULE.evaluate_roadmap_candidates(repo)
    by_id = {candidate["candidate_id"]: candidate for candidate in payload["candidates"]}

    assert by_id["stage1-source-family-group"]["claimable"] is False
    assert by_id["stage1-source-family-cn"]["claimable"] is True
    assert by_id["stage1-source-family-global"]["claimable"] is True
    assert by_id["stage1-source-family-integration-gate"]["status"] == "waiting"


def test_evaluator_blocks_stage1_gate_out_of_mvp_scope_even_when_expected_children_are_waiting(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _set_business_scope(repo, "stage2_to_stage6")
    write_mvp_scope(
        repo,
        scope="stage2_to_stage6",
        included_stages=["stage2", "stage3", "stage4", "stage5", "stage6"],
        excluded_stages=["stage1", "stage7", "stage8", "stage9"],
    )
    group = _candidate("stage1-source-family-group", status="waiting", priority=110, candidate_kind="lane_group", claimable=False, stage="stage1")
    group["expected_children"] = ["stage1-source-family-cn", "stage1-source-family-global"]
    group["planned_write_paths"] = []
    cn = _candidate("stage1-source-family-cn", status="waiting", priority=111, depends_on=["stage1-core-contract"], stage="stage1")
    global_slice = _candidate("stage1-source-family-global", status="waiting", priority=112, depends_on=["stage1-core-contract"], stage="stage1")
    gate = _candidate("stage1-source-family-integration-gate", status="waiting", priority=190, stage="stage1")
    gate["candidate_kind"] = "integration_gate"
    gate["lane_type"] = "integration_gate"
    gate["depends_on"] = ["stage1-core-contract"]
    gate["expected_children"] = ["stage1-source-family-cn", "stage1-source-family-global"]
    gate["completion_policy"] = "all_expected_children_done"
    _write_backlog(repo, [_candidate("stage1-core-contract", status="done", priority=100, stage="stage1"), group, cn, global_slice, gate])

    payload = MODULE.evaluate_roadmap_candidates(repo)
    by_id = {candidate["candidate_id"]: candidate for candidate in payload["candidates"]}

    assert by_id["stage1-source-family-integration-gate"]["status"] == "blocked"
    assert "expected_children_wait" in by_id["stage1-source-family-integration-gate"]["blocking_reason_codes"]
    assert "out_of_mvp_scope" in by_id["stage1-source-family-integration-gate"]["blocking_reason_codes"]


def test_evaluator_blocks_candidate_when_protected_paths_overlap_active_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    protected = _candidate("stage1-source-family-cn", status="planned", priority=100)
    protected["planned_write_paths"] = ["src/stage1_orchestration/source_families/cn/"]
    protected["protected_paths"] = ["src/stage1_orchestration/source_families/cn/"]
    blocked = _candidate("stage1-source-family-global", status="planned", priority=110)
    blocked["planned_write_paths"] = ["src/stage1_orchestration/source_families/cn/subscope/"]
    _write_backlog(repo, [protected, blocked])
    task_registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task_registry["tasks"].append(
        {
            "task_id": "TASK-ACTIVE-001",
            "title": "active child",
            "status": "doing",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": None,
            "stage": "stage1",
            "branch": "codex/TASK-ACTIVE-001",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "running",
            "blocked_reason": None,
            "last_reported_at": "2026-04-08T00:00:00+08:00",
            "topology": "single_task",
            "allowed_dirs": ["src/stage1_orchestration/source_families/cn/"],
            "reserved_paths": [],
            "protected_paths": ["src/stage1_orchestration/source_families/cn/"],
            "planned_write_paths": ["src/stage1_orchestration/source_families/cn/"],
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
            "task_file": "docs/governance/tasks/TASK-ACTIVE-001.md",
            "runlog_file": "docs/governance/runlogs/TASK-ACTIVE-001-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "successor_state": None,
            "created_at": "2026-04-08T00:00:00+08:00",
            "activated_at": "2026-04-08T00:00:00+08:00",
            "closed_at": None,
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", task_registry)

    payload = MODULE.evaluate_roadmap_candidates(repo)
    by_id = {candidate["candidate_id"]: candidate for candidate in payload["candidates"]}

    assert by_id["stage1-source-family-global"]["claimable"] is False
    assert "protected-path conflict" in " ".join(by_id["stage1-source-family-global"]["blockers"])
    assert "protected_path_conflict" in by_id["stage1-source-family-global"]["blocking_reason_codes"]


def test_evaluator_exposes_reason_taxonomy_and_release_forecast(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    parent = _candidate("stage1-core-contract", status="planned", priority=100)
    parent["unlocks"] = ["stage1-source-family-cn", "stage1-source-family-global"]
    child = _candidate("stage1-source-family-cn", status="waiting", priority=110, depends_on=["stage1-core-contract"])
    child_two = _candidate("stage1-source-family-global", status="waiting", priority=120, depends_on=["stage1-core-contract"])
    _write_backlog(repo, [parent, child, child_two])

    payload = MODULE.evaluate_roadmap_candidates(repo)
    by_id = {candidate["candidate_id"]: candidate for candidate in payload["candidates"]}

    assert by_id["stage1-core-contract"]["release_forecast"]["unlock_count"] == 2
    assert by_id["stage1-source-family-cn"]["blocking_reason_codes"] == ["dependency_wait"]
    assert by_id["stage1-source-family-cn"]["upstream_blocker_candidates"] == ["stage1-core-contract"]


def test_evaluator_blocks_out_of_mvp_scope(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _set_business_scope(repo, "stage2_to_stage6")
    write_mvp_scope(
        repo,
        scope="stage2_to_stage6",
        included_stages=["stage2", "stage3", "stage4", "stage5", "stage6"],
        excluded_stages=["stage1", "stage7", "stage8", "stage9"],
    )
    out_of_scope = _candidate("stage9-core-contract", status="planned", priority=100, stage="stage9")
    _write_backlog(repo, [out_of_scope])

    payload = MODULE.evaluate_roadmap_candidates(repo)
    candidate = next(item for item in payload["candidates"] if item["candidate_id"] == "stage9-core-contract")

    assert candidate["status"] == "blocked"
    assert "out_of_mvp_scope" in candidate["blocking_reason_codes"]


def test_evaluator_blocks_out_of_mvp_scope_even_when_dependency_is_waiting(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _set_business_scope(repo, "stage2_to_stage6")
    write_mvp_scope(
        repo,
        scope="stage2_to_stage6",
        included_stages=["stage2", "stage3", "stage4", "stage5", "stage6"],
        excluded_stages=["stage1", "stage7", "stage8", "stage9"],
    )
    _write_backlog(
        repo,
        [
            _candidate("stage6-fact-surface-gate", status="waiting", priority=100, stage="stage6"),
            _candidate("stage7-core-contract", status="planned", priority=200, stage="stage7", depends_on=["stage6-fact-surface-gate"]),
        ],
    )

    payload = MODULE.evaluate_roadmap_candidates(repo)
    candidate = next(item for item in payload["candidates"] if item["candidate_id"] == "stage7-core-contract")

    assert candidate["status"] == "blocked"
    assert "dependency_wait" in candidate["blocking_reason_codes"]
    assert "out_of_mvp_scope" in candidate["blocking_reason_codes"]


def test_evaluator_rejects_scope_mismatch_between_mvp_and_roadmap(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    write_mvp_scope(
        repo,
        scope="stage2_to_stage6",
        included_stages=["stage2", "stage3", "stage4", "stage5", "stage6"],
        excluded_stages=["stage1", "stage7", "stage8", "stage9"],
    )
    _write_backlog(repo, [_candidate("stage2-core-contract", status="planned", priority=100, stage="stage2")])

    with pytest.raises(MODULE.GovernanceError, match="scope mismatch"):
        MODULE.evaluate_roadmap_candidates(repo)


def test_evaluator_blocks_unregistered_coverage(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    candidate = _candidate(
        "stage2-global-slice",
        status="planned",
        priority=100,
        coverage_regions=["GLOBAL"],
    )
    _write_backlog(repo, [candidate])

    payload = MODULE.evaluate_roadmap_candidates(repo)
    item = next(item for item in payload["candidates"] if item["candidate_id"] == "stage2-global-slice")

    assert item["status"] == "blocked"
    assert "coverage_not_registered" in item["blocking_reason_codes"]


def test_evaluator_blocks_pilot_only_without_enablement(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    candidate = _candidate("stage2-pilot-slice", status="planned", priority=100, pilot_only=True)
    _write_backlog(repo, [candidate])

    payload = MODULE.evaluate_roadmap_candidates(repo)
    item = next(item for item in payload["candidates"] if item["candidate_id"] == "stage2-pilot-slice")

    assert item["status"] == "blocked"
    assert "pilot_only" in item["blocking_reason_codes"]


def test_evaluator_blocks_missing_planned_write_paths(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    candidate = _candidate(
        "stage2-missing-path-slice",
        status="planned",
        priority=100,
        allow_create_paths=False,
    )
    candidate["planned_write_paths"] = ["src/missing_path/"]
    _write_backlog(repo, [candidate])

    payload = MODULE.evaluate_roadmap_candidates(repo)
    item = next(item for item in payload["candidates"] if item["candidate_id"] == "stage2-missing-path-slice")

    assert item["status"] == "blocked"
    assert "planned_write_path_missing" in item["blocking_reason_codes"]


def test_evaluator_rejects_inline_candidates_when_compiled_mode(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate("stage2-core-contract", status="planned", priority=100)])
    backlog = read_yaml(repo / "docs/governance/ROADMAP_BACKLOG.yaml")
    backlog["compiler_policy"]["mode"] = "module_graph_compiler"
    write_yaml(repo / "docs/governance/ROADMAP_BACKLOG.yaml", backlog)

    with pytest.raises(MODULE.GovernanceError):
        MODULE.evaluate_roadmap_candidates(repo)
