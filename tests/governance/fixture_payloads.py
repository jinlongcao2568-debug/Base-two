from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

import yaml

try:
    from .policy_fixture_payloads import task_policy_payload
except ImportError:
    _POLICY_FIXTURE_PATH = Path(__file__).with_name("policy_fixture_payloads.py")
    _POLICY_FIXTURE_SPEC = importlib.util.spec_from_file_location("gov_policy_fixture_payloads", _POLICY_FIXTURE_PATH)
    _POLICY_FIXTURE_MODULE = importlib.util.module_from_spec(_POLICY_FIXTURE_SPEC)
    assert _POLICY_FIXTURE_SPEC is not None and _POLICY_FIXTURE_SPEC.loader is not None
    _POLICY_FIXTURE_SPEC.loader.exec_module(_POLICY_FIXTURE_MODULE)
    task_policy_payload = _POLICY_FIXTURE_MODULE.task_policy_payload


def roadmap_text() -> str:
    return (
        "---\n"
        "current_phase: base-phase\n"
        "current_task_id: TASK-BASE-001\n"
        "next_recommended_task_id: null\n"
        "advance_mode: explicit_or_generated\n"
        "auto_create_missing_task: true\n"
        "branch_switch_policy: create_or_switch_if_clean\n"
        "priority_order:\n"
        "  - governance_automation\n"
        "  - authority_chain\n"
        "  - business_automation\n"
        "business_automation_enabled: false\n"
        "business_automation_scope: stage1_to_stage9\n"
        "parallel_strategy: dependency_aware_disjoint_writes\n"
        "max_parallel_workers: 4\n"
        "spec_source_policy: baseline_contracts_task_package\n"
        "business_gap_priority:\n"
        "  - bootstrap_required\n"
        "  - implementation_ready\n"
        "  - integration_expansion\n"
        "stage_establishment:\n"
        "  stage1: not_established\n"
        "  stage2: not_established\n"
        "  stage3: not_established\n"
        "  stage4: not_established\n"
        "  stage5: not_established\n"
        "  stage6: not_established\n"
        "  stage7: not_established\n"
        "  stage8: not_established\n"
        "  stage9: not_established\n"
        "automation_foundation: not_established\n"
        "---\n\n# Roadmap\n\n"
        "## Current Task\n\n"
        "- `TASK-BASE-001`: `base coordination task` is the live coordination task for `base-phase`.\n"
    )


def _load_canonical_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return copy.deepcopy(yaml.safe_load(handle) or {})


_CANONICAL_CAPABILITY_MAP_PATH = Path(__file__).resolve().parents[2] / "docs/governance/CAPABILITY_MAP.yaml"
_CANONICAL_MODULE_MAP_PATH = Path(__file__).resolve().parents[2] / "docs/governance/MODULE_MAP.yaml"
_CANONICAL_TEST_MATRIX_PATH = Path(__file__).resolve().parents[2] / "docs/governance/TEST_MATRIX.yaml"
FIXTURE_CAPABILITY_STATUS_OVERRIDES = {
    "roadmap_autopilot_continuation": "not_implemented",
    "dynamic_parallel_execution_control": "not_implemented",
    "parallel_closeout_pipeline_v1": "not_implemented",
    "runtime_prompt_profiles": "not_implemented",
    "high_throughput_runner_v1": "not_implemented",
    "stage1_to_stage6_business_automation": "not_implemented",
    "stage7_to_stage9_business_automation": "not_established",
}


def capability_map_payload() -> dict[str, Any]:
    payload = _load_canonical_yaml(_CANONICAL_CAPABILITY_MAP_PATH)
    for capability in payload.get("capabilities", []):
        override = FIXTURE_CAPABILITY_STATUS_OVERRIDES.get(capability.get("capability_id"))
        if override is not None:
            capability["status"] = override
    return payload


def module_map_payload() -> dict[str, Any]:
    return _load_canonical_yaml(_CANONICAL_MODULE_MAP_PATH)


def test_matrix_payload() -> dict[str, Any]:
    return _load_canonical_yaml(_CANONICAL_TEST_MATRIX_PATH)


def base_allowed_dirs() -> list[str]:
    return [
        "src/base/",
        "tests/base/",
        "docs/governance/CURRENT_TASK.yaml",
        "docs/governance/DEVELOPMENT_ROADMAP.md",
        "docs/governance/AUTOMATION_INTENTS.yaml",
        "docs/governance/GIT_PUBLISH_POLICY.yaml",
        "docs/governance/PROMPT_MODULE_CATALOG.yaml",
        "docs/governance/prompt_modules/",
        "docs/governance/runtime_prompts/",
        "docs/governance/TASK_REGISTRY.yaml",
        "docs/governance/WORKTREE_REGISTRY.yaml",
        "docs/governance/TASK_SOURCE_REGISTRY.yaml",
        "docs/governance/WORKER_REGISTRY.yaml",
        "docs/governance/ORCHESTRATOR_RUNTIME_MODEL.md",
        "docs/governance/MODULE_MAP.yaml",
        "docs/governance/TEST_MATRIX.yaml",
        "docs/governance/CODE_HYGIENE_POLICY.md",
        "docs/governance/tasks/",
        "docs/governance/runlogs/",
    ]


def base_planned_write_paths() -> list[str]:
    return list(base_allowed_dirs())


def base_task_payload() -> dict[str, Any]:
    return {
        "task_id": "TASK-BASE-001",
        "title": "base coordination task",
        "status": "doing",
        "task_kind": "coordination",
        "execution_mode": "shared_coordination",
        "parent_task_id": None,
        "stage": "base-phase",
        "branch": "main",
        "size_class": "standard",
        "automation_mode": "assisted",
        "worker_state": "running",
        "blocked_reason": None,
        "last_reported_at": "2026-04-04T00:00:00+08:00",
        "topology": "single_worker",
        "allowed_dirs": base_allowed_dirs(),
        "reserved_paths": [],
        "planned_write_paths": base_planned_write_paths(),
        "planned_test_paths": ["tests/base/"],
        "required_tests": ["pytest tests/base -q"],
        "task_file": "docs/governance/tasks/TASK-BASE-001.md",
        "runlog_file": "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md",
        "lane_count": 1,
        "lane_index": None,
        "parallelism_plan_id": None,
        "review_bundle_status": "not_applicable",
    }


def base_task_markdown() -> str:
    return (
        "# TASK-BASE-001 base coordination task\n\n"
        "## Task Baseline\n\n"
        "- `task_id`: `TASK-BASE-001`\n"
        "- `status`: `doing`\n"
        "- `stage`: `base-phase`\n"
        "- `branch`: `main`\n"
        "- `worker_state`: `running`\n\n"
        "## Narrative Assertions\n\n"
        "- `narrative_status`: `doing`\n"
        "- `closeout_state`: `not_ready`\n"
        "- `blocking_state`: `clear`\n"
        "- `completed_scope`: `active_progress`\n"
        "- `remaining_scope`: `active_work_remaining`\n"
        "- `next_gate`: `validation_pending`\n\n"
        "<!-- generated:task-meta:start -->\n"
        "## Generated Metadata\n\n"
        "- `status`: `doing`\n"
        "- `task_kind`: `coordination`\n"
        "- `execution_mode`: `shared_coordination`\n"
        "- `size_class`: `standard`\n"
        "- `automation_mode`: `assisted`\n"
        "- `worker_state`: `running`\n"
        "- `topology`: `single_worker`\n"
        "- `lane_count`: `1`\n"
        "- `lane_index`: `null`\n"
        "- `parallelism_plan_id`: `null`\n"
        "- `review_bundle_status`: `not_applicable`\n"
        "- `reserved_paths`: `[]`\n"
        "- `branch`: `main`\n"
        "- `updated_at`: `2026-04-04T00:00:00+08:00`\n"
        "<!-- generated:task-meta:end -->\n"
    )


def base_runlog_markdown() -> str:
    return (
        "# TASK-BASE-001 RUNLOG\n\n"
        "## Task Status\n\n"
        "- `task_id`: `TASK-BASE-001`\n"
        "- `status`: `doing`\n"
        "- `stage`: `base-phase`\n"
        "- `branch`: `main`\n"
        "- `worker_state`: `running`\n\n"
        "## Test Log\n\n"
        "- `pytest tests/base -q`\n\n"
        "## Narrative Assertions\n\n"
        "- `narrative_status`: `doing`\n"
        "- `closeout_state`: `not_ready`\n"
        "- `blocking_state`: `clear`\n"
        "- `completed_scope`: `active_progress`\n"
        "- `remaining_scope`: `active_work_remaining`\n"
        "- `next_gate`: `validation_pending`\n\n"
        "<!-- generated:runlog-meta:start -->\n"
        "## Generated Task Snapshot\n\n"
        "- `task_id`: `TASK-BASE-001`\n"
        "- `status`: `doing`\n"
        "- `stage`: `base-phase`\n"
        "- `branch`: `main`\n"
        "- `worker_state`: `running`\n"
        "- `lane_count`: `1`\n"
        "- `lane_index`: `null`\n"
        "- `parallelism_plan_id`: `null`\n"
        "- `review_bundle_status`: `not_applicable`\n"
        "<!-- generated:runlog-meta:end -->\n"
    )
