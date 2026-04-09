from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from control_plane_root import resolve_control_plane_root
from governance_lib import GovernanceError, configure_utf8_stdio, dump_yaml, find_repo_root, iso_now, load_task_policy, load_yaml


ROADMAP_BACKLOG_FILE = Path("docs/governance/ROADMAP_BACKLOG.yaml")
MODULE_MAP_FILE = Path("docs/governance/MODULE_MAP.yaml")
TASK_POLICY_FILE = Path("docs/governance/TASK_POLICY.yaml")
COMPILED_GRAPH_FILE = Path(".codex/local/roadmap_candidates/compiled.yaml")
GRAPH_VERSION = "roadmap_compiled_graph_v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_map(path: Path) -> dict[str, Any]:
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"expected mapping payload: {path.as_posix()}")
    return payload


def _load_backlog(root: Path) -> dict[str, Any]:
    return _load_map(root / ROADMAP_BACKLOG_FILE)


def _load_module_map(root: Path) -> dict[str, Any]:
    return _load_map(root / MODULE_MAP_FILE)


def _compiler_policy(backlog: dict[str, Any]) -> dict[str, Any]:
    policy = backlog.get("compiler_policy") or {}
    return {"mode": str(policy.get("mode") or "inline_candidates")}


def _module_by_id(module_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(module["module_id"]): module for module in module_map.get("modules", [])}


def _candidate(
    *,
    candidate_id: str,
    title: str,
    stage: str,
    module_id: str,
    lane_type: str,
    status: str,
    priority: int,
    depends_on: list[str],
    unlocks: list[str],
    allowed_dirs: list[str],
    forbidden_write_paths: list[str],
    protected_paths: list[str],
    planned_write_paths: list[str],
    planned_test_paths: list[str],
    required_tests: list[str],
    branch_suffix: str,
    integration_gate: str | None,
    candidate_kind: str = "lane_slice",
    claimable: bool = True,
    parent_candidate_id: str | None = None,
    expected_children: list[str] | None = None,
    completion_policy: str = "none",
    candidate_intent: str | None = None,
    root_kind: str | None = None,
    release_evidence: list[str] | None = None,
    pilot_only: bool | None = None,
    allow_create_paths: bool | None = None,
    coverage_regions: list[str] | None = None,
) -> dict[str, Any]:
    conflict_policy = "require_disjoint_child_slice" if lane_type == "stage_internal_parallel" else "choose_next_safe_candidate"
    if candidate_kind == "integration_gate" or lane_type == "fact_surface_gate":
        conflict_policy = "strict_single_writer"
    payload = {
        "candidate_id": candidate_id,
        "title": title,
        "stage": stage,
        "module_id": module_id,
        "candidate_kind": candidate_kind,
        "claimable": claimable,
        "parent_candidate_id": parent_candidate_id,
        "lane_type": lane_type,
        "status": status,
        "priority": priority,
        "depends_on": depends_on,
        "unlocks": unlocks,
        "allowed_dirs": allowed_dirs,
        "forbidden_write_paths": forbidden_write_paths,
        "protected_paths": protected_paths,
        "planned_write_paths": planned_write_paths,
        "planned_test_paths": planned_test_paths,
        "required_tests": required_tests,
        "branch_template": f"codex/{{task_id}}-{branch_suffix}",
        "worktree_template": "../AX9.worktrees/{task_id}",
        "integration_gate": integration_gate,
        "expected_children": expected_children or [],
        "completion_policy": completion_policy,
        "claim_policy": {
            "one_window_one_candidate": True,
            "conflict_policy": conflict_policy,
            "scheduler_lock_required": True,
        },
        "takeover_policy": {
            "stale_after_minutes_source": "docs/governance/HANDOFF_POLICY.yaml",
            "clean_worktree_takeover": "allow",
            "scoped_dirty_checkpoint": "allow_before_takeover",
            "out_of_scope_dirty_policy": "block_for_human_decision",
            "remote_divergence_policy": "block",
        },
        "candidate_intent": candidate_intent or candidate_kind,
        "root_kind": root_kind or candidate_kind,
        "release_evidence": release_evidence or [],
    }
    if pilot_only is not None:
        payload["pilot_only"] = pilot_only
    if allow_create_paths is not None:
        payload["allow_create_paths"] = allow_create_paths
    if coverage_regions is not None:
        payload["coverage_regions"] = coverage_regions
    return payload


def _module_test_paths(module: dict[str, Any]) -> list[str]:
    return [path for path in module.get("allowed_dirs", []) if str(path).startswith("tests/")]


def _module_root(
    module: dict[str, Any],
    *,
    candidate_id: str,
    title: str,
    stage: str,
    priority: int,
    depends_on: list[str],
    unlocks: list[str],
    integration_gate: str | None,
) -> dict[str, Any]:
    return _candidate(
        candidate_id=candidate_id,
        title=title,
        stage=stage,
        module_id=module["module_id"],
        lane_type="core_contract",
        status="waiting" if depends_on else "planned",
        priority=priority,
        depends_on=depends_on,
        unlocks=unlocks,
        allowed_dirs=list(module.get("allowed_dirs") or []),
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=[],
        planned_write_paths=list(module.get("allowed_dirs") or []),
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix=candidate_id,
        integration_gate=integration_gate,
        candidate_intent="module_root",
        root_kind="formal_root",
        release_evidence=["module_dependencies_satisfied"],
    )


def _preview_root(
    module: dict[str, Any],
    *,
    candidate_id: str,
    title: str,
    stage: str,
    priority: int,
    depends_on: list[str],
    preview_path: str,
    integration_gate: str | None,
    release_evidence: list[str],
) -> dict[str, Any]:
    return _candidate(
        candidate_id=candidate_id,
        title=title,
        stage=stage,
        module_id=module["module_id"],
        lane_type="downstream_fixture_preview",
        status="waiting",
        priority=priority,
        depends_on=depends_on,
        unlocks=[],
        allowed_dirs=list(module.get("allowed_dirs") or []),
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=[preview_path],
        planned_write_paths=[preview_path],
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix=candidate_id,
        integration_gate=integration_gate,
        candidate_intent="module_preview_root",
        root_kind="preview_root",
        release_evidence=release_evidence,
    )


def _legacy_lane(
    module: dict[str, Any],
    *,
    candidate_id: str,
    title: str,
    stage: str,
    priority: int,
    depends_on: list[str],
    unlocks: list[str],
    integration_gate: str,
    branch_suffix: str,
) -> dict[str, Any]:
    return _candidate(
        candidate_id=candidate_id,
        title=title,
        stage=stage,
        module_id=module["module_id"],
        lane_type="stage_internal_parallel",
        status="waiting",
        priority=priority,
        depends_on=depends_on,
        unlocks=unlocks,
        allowed_dirs=list(module.get("allowed_dirs") or []),
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=[],
        planned_write_paths=list(module.get("allowed_dirs") or []),
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix=branch_suffix,
        integration_gate=integration_gate,
        candidate_intent="module_slice",
        root_kind="legacy_lane",
    )


def _integration_gate(
    module: dict[str, Any],
    *,
    candidate_id: str,
    title: str,
    stage: str,
    priority: int,
    depends_on: list[str],
    unlocks: list[str],
    lane_type: str = "integration_gate",
    release_evidence: list[str] | None = None,
) -> dict[str, Any]:
    return _candidate(
        candidate_id=candidate_id,
        title=title,
        stage=stage,
        module_id=module["module_id"],
        candidate_kind="integration_gate",
        lane_type=lane_type,
        status="waiting",
        priority=priority,
        depends_on=depends_on,
        unlocks=unlocks,
        allowed_dirs=list(module.get("allowed_dirs") or []),
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=list(module.get("allowed_dirs") or []),
        planned_write_paths=list(module.get("allowed_dirs") or []),
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix=candidate_id,
        integration_gate=candidate_id,
        candidate_intent="module_integration_gate" if lane_type == "integration_gate" else "fact_surface_gate",
        root_kind="hard_gate" if lane_type == "fact_surface_gate" else "integration_gate",
        release_evidence=release_evidence or [],
    )


def _compile_stage1(module: dict[str, Any]) -> list[dict[str, Any]]:
    root = _module_root(
        module,
        candidate_id="stage1-core-contract",
        title="Stage1 orchestration contract and fixture boundary",
        stage="stage1",
        priority=100,
        depends_on=[],
        unlocks=[
            "stage1-source-family-group",
            "stage1-source-family-cn",
            "stage1-source-family-global",
            "stage1-source-family-integration-gate",
            "stage2-core-contract",
        ],
        integration_gate="stage1-source-family-integration-gate",
    )
    group = _candidate(
        candidate_id="stage1-source-family-group",
        title="Stage1 source-family orchestration lane group",
        stage="stage1",
        module_id=module["module_id"],
        candidate_kind="lane_group",
        claimable=False,
        lane_type="stage_internal_parallel",
        status="waiting",
        priority=110,
        depends_on=["stage1-core-contract"],
        unlocks=["stage1-source-family-cn", "stage1-source-family-global", "stage1-source-family-integration-gate"],
        allowed_dirs=list(module.get("allowed_dirs") or []),
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=[],
        planned_write_paths=[],
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix="stage1-source-family-group",
        integration_gate="stage1-source-family-integration-gate",
        expected_children=["stage1-source-family-cn", "stage1-source-family-global"],
        completion_policy="none",
        candidate_intent="lane_group",
        root_kind="lane_group",
    )
    cn = _candidate(
        candidate_id="stage1-source-family-cn",
        title="Stage1 source-family China slice",
        stage="stage1",
        module_id=module["module_id"],
        lane_type="stage_internal_parallel",
        status="waiting",
        priority=111,
        depends_on=["stage1-core-contract"],
        unlocks=["stage1-source-family-integration-gate"],
        allowed_dirs=["src/stage1_orchestration/source_families/cn/", "tests/stage1/source_families/cn/"],
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=["src/stage1_orchestration/source_families/cn/", "tests/stage1/source_families/cn/"],
        planned_write_paths=["src/stage1_orchestration/source_families/cn/", "tests/stage1/source_families/cn/"],
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix="stage1-source-family-cn",
        integration_gate="stage1-source-family-integration-gate",
        parent_candidate_id="stage1-source-family-group",
        candidate_intent="module_slice",
        root_kind="child_slice",
        release_evidence=["stage1_core_contract_done"],
        pilot_only=True,
        coverage_regions=["CN"],
    )
    global_slice = _candidate(
        candidate_id="stage1-source-family-global",
        title="Stage1 source-family global slice",
        stage="stage1",
        module_id=module["module_id"],
        lane_type="stage_internal_parallel",
        status="waiting",
        priority=112,
        depends_on=["stage1-core-contract"],
        unlocks=["stage1-source-family-integration-gate"],
        allowed_dirs=["src/stage1_orchestration/source_families/global/", "tests/stage1/source_families/global/"],
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=["src/stage1_orchestration/source_families/global/", "tests/stage1/source_families/global/"],
        planned_write_paths=["src/stage1_orchestration/source_families/global/", "tests/stage1/source_families/global/"],
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix="stage1-source-family-global",
        integration_gate="stage1-source-family-integration-gate",
        parent_candidate_id="stage1-source-family-group",
        candidate_intent="module_slice",
        root_kind="child_slice",
        release_evidence=["stage1_core_contract_done"],
        pilot_only=True,
        coverage_regions=["GLOBAL"],
    )
    gate = _candidate(
        candidate_id="stage1-source-family-integration-gate",
        title="Stage1 source-family integration gate",
        stage="stage1",
        module_id=module["module_id"],
        candidate_kind="integration_gate",
        lane_type="integration_gate",
        status="waiting",
        priority=190,
        depends_on=["stage1-core-contract"],
        unlocks=["stage2-core-contract"],
        allowed_dirs=list(module.get("allowed_dirs") or []),
        forbidden_write_paths=list(module.get("reserved_paths") or []),
        protected_paths=list(module.get("allowed_dirs") or []),
        planned_write_paths=list(module.get("allowed_dirs") or []),
        planned_test_paths=_module_test_paths(module),
        required_tests=list(module.get("required_tests") or []),
        branch_suffix="stage1-source-family-integration-gate",
        integration_gate="stage1-source-family-integration-gate",
        parent_candidate_id="stage1-source-family-group",
        expected_children=["stage1-source-family-cn", "stage1-source-family-global"],
        completion_policy="all_expected_children_done",
        candidate_intent="module_integration_gate",
        root_kind="integration_gate",
        release_evidence=["stage1_children_done"],
    )
    return [root, group, cn, global_slice, gate]


def _compile_mainline_module(
    module: dict[str, Any],
    *,
    stage: str,
    root_id: str,
    root_title: str,
    root_priority: int,
    root_depends_on: list[str],
    preview_id: str | None,
    preview_title: str | None,
    preview_priority: int | None,
    preview_depends_on: list[str] | None,
    preview_path: str | None,
    preview_release_evidence: list[str] | None,
    lane_id: str | None,
    lane_title: str | None,
    lane_priority: int | None,
    lane_depends_on: list[str] | None,
    lane_unlocks: list[str] | None,
    gate_id: str,
    gate_title: str,
    gate_priority: int,
    gate_depends_on: list[str],
    gate_unlocks: list[str],
    gate_lane_type: str = "integration_gate",
    gate_release_evidence: list[str] | None = None,
) -> list[dict[str, Any]]:
    candidates = [
        _module_root(
            module,
            candidate_id=root_id,
            title=root_title,
            stage=stage,
            priority=root_priority,
            depends_on=root_depends_on,
            unlocks=([preview_id] if preview_id else []) + ([lane_id] if lane_id else []) + [gate_id] + gate_unlocks,
            integration_gate=gate_id,
        )
    ]
    if preview_id and preview_title and preview_priority is not None and preview_depends_on is not None and preview_path:
        candidates.append(
            _preview_root(
                module,
                candidate_id=preview_id,
                title=preview_title,
                stage=stage,
                priority=preview_priority,
                depends_on=preview_depends_on,
                preview_path=preview_path,
                integration_gate=gate_id,
                release_evidence=preview_release_evidence or [],
            )
        )
    if lane_id and lane_title and lane_priority is not None and lane_depends_on is not None:
        candidates.append(
            _legacy_lane(
                module,
                candidate_id=lane_id,
                title=lane_title,
                stage=stage,
                priority=lane_priority,
                depends_on=lane_depends_on,
                unlocks=lane_unlocks or [gate_id],
                integration_gate=gate_id,
                branch_suffix=lane_id.replace("stage_internal_parallel", "lane"),
            )
        )
    candidates.append(
        _integration_gate(
            module,
            candidate_id=gate_id,
            title=gate_title,
            stage=stage,
            priority=gate_priority,
            depends_on=gate_depends_on,
            unlocks=gate_unlocks,
            lane_type=gate_lane_type,
            release_evidence=gate_release_evidence or [],
        )
    )
    return candidates


def _preview_path_for_tests(module: dict[str, Any], suffix: str = "preview_root") -> str:
    tests = _module_test_paths(module)
    if tests:
        path = tests[0].rstrip("/")
        return f"{path}/{suffix}/"
    return f"tests/generated/{module['module_id']}/{suffix}/"


def _compile_module_graph(root: Path, backlog: dict[str, Any], module_map: dict[str, Any], task_policy: dict[str, Any]) -> dict[str, Any]:
    modules = _module_by_id(module_map)
    candidates: list[dict[str, Any]] = []
    candidates.extend(_compile_stage1(modules["stage1_orchestration"]))
    candidates.extend(
        _compile_mainline_module(
            modules["stage2_ingestion"],
            stage="stage2",
            root_id="stage2-core-contract",
            root_title="Stage2 ingestion contract and raw payload fixture boundary",
            root_priority=200,
            root_depends_on=["stage1-core-contract"],
            preview_id="stage2-payload-preview-root",
            preview_title="Stage2 raw payload preview root",
            preview_priority=205,
            preview_depends_on=["stage1-core-contract"],
            preview_path=_preview_path_for_tests(modules["stage2_ingestion"]),
            preview_release_evidence=["stage1_contract_frozen"],
            lane_id="stage2-source-family-lanes",
            lane_title="Stage2 source-family ingestion lanes",
            lane_priority=210,
            lane_depends_on=["stage2-core-contract"],
            lane_unlocks=["stage2-integration-gate"],
            gate_id="stage2-integration-gate",
            gate_title="Stage2 ingestion integration gate",
            gate_priority=290,
            gate_depends_on=["stage2-core-contract", "stage2-source-family-lanes"],
            gate_unlocks=["stage3-core-contract"],
            gate_release_evidence=["stage2_children_done"],
        )
    )
    candidates.extend(
        _compile_mainline_module(
            modules["stage3_parsing"],
            stage="stage3",
            root_id="stage3-core-contract",
            root_title="Stage3 parsing contract and normalized record boundary",
            root_priority=300,
            root_depends_on=["stage2-core-contract"],
            preview_id="stage3-normalized-preview-root",
            preview_title="Stage3 normalized record preview root",
            preview_priority=305,
            preview_depends_on=["stage2-core-contract"],
            preview_path=_preview_path_for_tests(modules["stage3_parsing"]),
            preview_release_evidence=["stage2_contract_frozen"],
            lane_id="stage3-parser-family-lanes",
            lane_title="Stage3 parser-family lanes",
            lane_priority=310,
            lane_depends_on=["stage3-core-contract"],
            lane_unlocks=["stage3-integration-gate"],
            gate_id="stage3-integration-gate",
            gate_title="Stage3 parsing integration gate",
            gate_priority=390,
            gate_depends_on=["stage3-core-contract", "stage3-parser-family-lanes"],
            gate_unlocks=["stage4-core-contract"],
            gate_release_evidence=["stage3_children_done"],
        )
    )
    candidates.extend(
        _compile_mainline_module(
            modules["stage4_validation"],
            stage="stage4",
            root_id="stage4-core-contract",
            root_title="Stage4 validation rule-hit contract and topic boundary",
            root_priority=400,
            root_depends_on=["stage3-core-contract"],
            preview_id="stage4-validation-preview-root",
            preview_title="Stage4 validation preview root",
            preview_priority=405,
            preview_depends_on=["stage3-core-contract"],
            preview_path=_preview_path_for_tests(modules["stage4_validation"]),
            preview_release_evidence=["stage3_contract_frozen"],
            lane_id="stage4-rule-topic-lanes",
            lane_title="Stage4 rule-topic validation lanes",
            lane_priority=410,
            lane_depends_on=["stage4-core-contract"],
            lane_unlocks=["stage4-integration-gate"],
            gate_id="stage4-integration-gate",
            gate_title="Stage4 validation integration gate",
            gate_priority=490,
            gate_depends_on=["stage4-core-contract", "stage4-rule-topic-lanes"],
            gate_unlocks=["stage5-core-contract", "stage6-fact-surface-gate"],
            gate_release_evidence=["stage4_children_done"],
        )
    )
    candidates.extend(
        _compile_mainline_module(
            modules["stage5_reporting"],
            stage="stage5",
            root_id="stage5-core-contract",
            root_title="Stage5 reporting artifact contract and snapshot boundary",
            root_priority=500,
            root_depends_on=["stage4-core-contract"],
            preview_id="stage5-report-preview-root",
            preview_title="Stage5 report artifact preview root",
            preview_priority=505,
            preview_depends_on=["stage4-core-contract"],
            preview_path=_preview_path_for_tests(modules["stage5_reporting"]),
            preview_release_evidence=["stage4_contract_frozen"],
            lane_id="stage5-formatter-lanes",
            lane_title="Stage5 formatter and report snapshot lanes",
            lane_priority=510,
            lane_depends_on=["stage5-core-contract"],
            lane_unlocks=["stage5-integration-gate"],
            gate_id="stage5-integration-gate",
            gate_title="Stage5 reporting integration gate",
            gate_priority=590,
            gate_depends_on=["stage5-core-contract", "stage5-formatter-lanes"],
            gate_unlocks=["stage6-fact-surface-gate"],
            gate_release_evidence=["stage5_children_done"],
        )
    )
    candidates.append(
        _integration_gate(
            modules["stage6_facts"],
            candidate_id="stage6-fact-surface-gate",
            title="Stage6 project_fact single-writer fact surface gate",
            stage="stage6",
            priority=600,
            depends_on=["stage4-integration-gate", "stage5-integration-gate"],
            unlocks=[
                "stage7-core-contract",
                "stage8-core-contract",
                "domain-public-chain-preview-root",
                "domain-project-manager-preview-root",
                "domain-competitor-analysis-preview-root",
                "domain-evidence-preview-root",
                "domain-review-requests-preview-root",
            ],
            lane_type="fact_surface_gate",
            release_evidence=["stage4_and_stage5_integrated"],
        )
    )
    candidates.extend(
        _compile_mainline_module(
            modules["stage7_sales"],
            stage="stage7",
            root_id="stage7-core-contract",
            root_title="Stage7 sales context contract",
            root_priority=700,
            root_depends_on=["stage6-fact-surface-gate"],
            preview_id="stage7-sales-preview-root",
            preview_title="Stage7 sales context preview root",
            preview_priority=705,
            preview_depends_on=["stage6-fact-surface-gate"],
            preview_path=_preview_path_for_tests(modules["stage7_sales"]),
            preview_release_evidence=["project_fact_frozen"],
            lane_id="stage7-sales-parallel-lanes",
            lane_title="Stage7 sales-context parallel lanes",
            lane_priority=720,
            lane_depends_on=["stage7-core-contract"],
            lane_unlocks=["stage7-integration-gate"],
            gate_id="stage7-integration-gate",
            gate_title="Stage7 sales-context integration gate",
            gate_priority=790,
            gate_depends_on=["stage7-core-contract", "stage7-sales-parallel-lanes"],
            gate_unlocks=["stage9-final-delivery-gate", "stage9-delivery-preview-root"],
            gate_release_evidence=["stage7_children_done"],
        )
    )
    candidates.extend(
        _compile_mainline_module(
            modules["stage8_contact"],
            stage="stage8",
            root_id="stage8-core-contract",
            root_title="Stage8 contact context contract",
            root_priority=710,
            root_depends_on=["stage6-fact-surface-gate"],
            preview_id="stage8-contact-preview-root",
            preview_title="Stage8 contact context preview root",
            preview_priority=715,
            preview_depends_on=["stage6-fact-surface-gate"],
            preview_path=_preview_path_for_tests(modules["stage8_contact"]),
            preview_release_evidence=["project_fact_frozen"],
            lane_id="stage8-contact-parallel-lanes",
            lane_title="Stage8 contact-context parallel lanes",
            lane_priority=730,
            lane_depends_on=["stage8-core-contract"],
            lane_unlocks=["stage8-integration-gate"],
            gate_id="stage8-integration-gate",
            gate_title="Stage8 contact-context integration gate",
            gate_priority=795,
            gate_depends_on=["stage8-core-contract", "stage8-contact-parallel-lanes"],
            gate_unlocks=["stage9-final-delivery-gate", "stage9-delivery-preview-root"],
            gate_release_evidence=["stage8_children_done"],
        )
    )
    candidates.append(
        _preview_root(
            modules["stage9_delivery"],
            candidate_id="stage9-delivery-preview-root",
            title="Stage9 delivery preview root",
            stage="stage9",
            priority=890,
            depends_on=["stage6-fact-surface-gate", "stage7-core-contract", "stage8-core-contract"],
            preview_path=_preview_path_for_tests(modules["stage9_delivery"]),
            integration_gate="stage9-final-delivery-gate",
            release_evidence=["project_fact_frozen", "downstream_context_contracts_frozen"],
        )
    )
    candidates.append(
        _integration_gate(
            modules["stage9_delivery"],
            candidate_id="stage9-final-delivery-gate",
            title="Stage9 final customer-visible delivery gate",
            stage="stage9",
            priority=900,
            depends_on=["stage6-fact-surface-gate", "stage7-integration-gate", "stage8-integration-gate"],
            unlocks=[],
            release_evidence=["stage7_and_stage8_integrated"],
        )
    )
    for module_id, priority in (
        ("domain_public_chain", 805),
        ("domain_project_manager", 810),
        ("domain_competitor_analysis", 815),
        ("domain_evidence", 820),
        ("domain_review_requests", 825),
    ):
        module = modules[module_id]
        candidates.append(
            _preview_root(
                module,
                candidate_id=f"{module_id.replace('_', '-')}-preview-root",
                title=f"{module_id} preview root",
                stage="consumer",
                priority=priority,
                depends_on=["stage6-fact-surface-gate"],
                preview_path=_preview_path_for_tests(module),
                integration_gate=None,
                release_evidence=["project_fact_frozen"],
            )
        )

    return {
        "graph_version": GRAPH_VERSION,
        "mode": "module_graph_compiler",
        "compiled_at": iso_now(),
        "module_map_version": str(module_map.get("updated_at") or module_map.get("version") or "unknown"),
        "policy_version": str(task_policy.get("updated_at") or task_policy.get("version") or "unknown"),
        "source_hashes": {
            "roadmap_backlog": _sha256(root / ROADMAP_BACKLOG_FILE),
            "module_map": _sha256(root / MODULE_MAP_FILE),
            "task_policy": _sha256(root / TASK_POLICY_FILE),
        },
        "candidates": candidates,
    }


def compile_roadmap_candidates(root: Path) -> dict[str, Any]:
    backlog = _load_backlog(root)
    module_map = _load_module_map(root)
    task_policy = load_task_policy(root)
    policy = _compiler_policy(backlog)
    if policy["mode"] == "inline_candidates":
        return {
            "graph_version": GRAPH_VERSION,
            "mode": "inline_candidates",
            "compiled_at": iso_now(),
            "module_map_version": str(module_map.get("updated_at") or module_map.get("version") or "unknown"),
            "policy_version": str(task_policy.get("updated_at") or task_policy.get("version") or "unknown"),
            "source_hashes": {
                "roadmap_backlog": _sha256(root / ROADMAP_BACKLOG_FILE),
                "module_map": _sha256(root / MODULE_MAP_FILE),
                "task_policy": _sha256(root / TASK_POLICY_FILE),
            },
            "candidates": list(backlog.get("candidates") or []),
        }
    return _compile_module_graph(root, backlog, module_map, task_policy)


def write_compiled_roadmap_candidates(root: Path) -> dict[str, Any]:
    payload = compile_roadmap_candidates(root)
    dump_yaml(root / COMPILED_GRAPH_FILE, payload)
    return payload


def cmd_compile(args: argparse.Namespace) -> int:
    local_root = find_repo_root()
    root = resolve_control_plane_root(local_root)
    if local_root != root:
        local_output = (local_root / COMPILED_GRAPH_FILE).resolve()
        if local_output.exists():
            raise GovernanceError("clone 内禁止复用本地 compiled candidate graph；请改在主控制面编译")
    payload = write_compiled_roadmap_candidates(root)
    print(
        f"[OK] compiled roadmap candidate graph count={len(payload['candidates'])} "
        f"mode={payload['mode']} output={COMPILED_GRAPH_FILE.as_posix()}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile roadmap candidates from module graph")
    parser.set_defaults(func=cmd_compile)
    return parser


def main() -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
