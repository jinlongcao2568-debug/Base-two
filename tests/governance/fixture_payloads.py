from __future__ import annotations

from typing import Any


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


def _capability(
    capability_id: str,
    status: str,
    source_of_truth: list[str],
    scripts: list[str],
    tests: list[str],
) -> dict[str, Any]:
    return {
        "capability_id": capability_id,
        "status": status,
        "source_of_truth": source_of_truth,
        "scripts": scripts,
        "tests": tests,
    }


def _governance_capability_entries() -> list[dict[str, Any]]:
    return [*_governance_control_capabilities(), *_governance_prompt_capabilities()]


def _governance_control_capabilities() -> list[dict[str, Any]]:
    return [
        _capability(
            "governance_control_plane",
            "implemented",
            [
                "docs/governance/CURRENT_TASK.yaml",
                "docs/governance/TASK_REGISTRY.yaml",
                "docs/governance/WORKTREE_REGISTRY.yaml",
            ],
            ["scripts/task_ops.py", "scripts/automation_runner.py"],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
        _capability(
            "closeout_autopilot_v2",
            "implemented",
            [
                "docs/governance/CURRENT_TASK.yaml",
                "docs/governance/TASK_REGISTRY.yaml",
                "docs/governance/WORKTREE_REGISTRY.yaml",
                "docs/governance/runlogs/",
            ],
            [
                "scripts/task_closeout.py",
                "scripts/task_continuation_ops.py",
                "scripts/automation_runner.py",
            ],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
        _capability(
            "roadmap_autopilot_continuation",
            "not_implemented",
            [
                "docs/governance/DEVELOPMENT_ROADMAP.md",
                "docs/governance/TASK_POLICY.yaml",
                "docs/governance/CAPABILITY_MAP.yaml",
            ],
            [
                "scripts/automation_intent.py",
                "scripts/task_ops.py",
                "scripts/task_continuation_ops.py",
                "scripts/automation_runner.py",
            ],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
    ]


def _governance_prompt_capabilities() -> list[dict[str, Any]]:
    return [
        _capability(
            "dynamic_parallel_execution_control",
            "not_implemented",
            [
                "docs/governance/TASK_POLICY.yaml",
                "docs/governance/TASK_REGISTRY.yaml",
                "docs/governance/WORKTREE_REGISTRY.yaml",
            ],
            [
                "scripts/governance_rules.py",
                "scripts/task_worktree_ops.py",
                "scripts/business_autopilot.py",
            ],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
        _capability(
            "parallel_closeout_pipeline_v1",
            "not_implemented",
            [
                "docs/governance/TASK_REGISTRY.yaml",
                "docs/governance/WORKTREE_REGISTRY.yaml",
                "docs/governance/CURRENT_TASK.yaml",
            ],
            [
                "scripts/task_worker_ops.py",
                "scripts/task_continuation_ops.py",
                "scripts/automation_runner.py",
            ],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
        _capability(
            "runtime_prompt_profiles",
            "not_implemented",
            [
                "docs/governance/PROMPT_MODULE_CATALOG.yaml",
                "docs/governance/prompt_modules/",
                "docs/governance/runtime_prompts/",
            ],
            ["scripts/render_runtime_prompts.py"],
            ["pytest tests/governance -q"],
        ),
        _capability(
            "high_throughput_runner_v1",
            "not_implemented",
            [
                "docs/governance/DEVELOPMENT_ROADMAP.md",
                "docs/governance/AUTOMATION_OPERATING_MODEL.md",
                "docs/governance/TASK_POLICY.yaml",
                "docs/governance/WORKTREE_REGISTRY.yaml",
            ],
            [
                "scripts/automation_runner.py",
                "scripts/task_worktree_ops.py",
                "scripts/task_worker_ops.py",
            ],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
    ]


def _business_capability_entries() -> list[dict[str, Any]]:
    return [
        _capability(
            "stage1_to_stage6_business_automation",
            "not_implemented",
            [
                "docs/governance/DEVELOPMENT_ROADMAP.md",
                "docs/governance/TASK_POLICY.yaml",
                "docs/governance/MODULE_MAP.yaml",
                "docs/governance/TEST_MATRIX.yaml",
            ],
            [
                "scripts/business_autopilot.py",
                "scripts/task_continuation_ops.py",
                "scripts/task_worker_ops.py",
                "scripts/automation_runner.py",
            ],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
        _capability(
            "stage7_to_stage9_business_automation",
            "not_established",
            [
                "docs/governance/DEVELOPMENT_ROADMAP.md",
                "docs/governance/TASK_POLICY.yaml",
                "docs/governance/MODULE_MAP.yaml",
            ],
            [
                "scripts/business_autopilot.py",
                "scripts/task_continuation_ops.py",
                "scripts/automation_runner.py",
            ],
            ["pytest tests/governance -q", "pytest tests/automation -q"],
        ),
    ]


def capability_map_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-05T12:30:00+08:00",
        "authority_source": "docs/product/AUTHORITY_SPEC.md",
        "capabilities": [*_governance_capability_entries(), *_business_capability_entries()],
    }


def _roadmap_blueprint() -> dict[str, Any]:
    return {
        "blueprint_id": "roadmap_autopilot_continuation",
        "title": "路线图自动续跑编排层",
        "task_kind": "coordination",
        "execution_mode": "shared_coordination",
        "stage": "automation-roadmap-continuation-v1",
        "size_class": "heavy",
        "automation_mode": "manual",
        "topology": "single_worker",
        "allowed_dirs": ["docs/governance/", "scripts/", "tests/governance/", "tests/automation/"],
        "planned_write_paths": ["docs/governance/", "scripts/", "tests/governance/", "tests/automation/"],
        "planned_test_paths": ["tests/governance/", "tests/automation/"],
        "required_tests": [
            "python scripts/check_repo.py",
            "python scripts/check_hygiene.py",
            "pytest tests/governance -q",
            "pytest tests/automation -q",
            "pytest -q",
        ],
        "branch_template": "feat/{task_id}-roadmap-autopilot-continuation",
    }


def _business_parent_blueprint() -> dict[str, Any]:
    return {
        "blueprint_id": "business_parallel_parent_stage1_to_stage6",
        "title": "Business automation round",
        "task_kind": "coordination",
        "execution_mode": "shared_coordination",
        "stage": "business-full-chain-round",
        "size_class": "heavy",
        "automation_mode": "autonomous",
        "topology": "parallel_parent",
        "allowed_dirs": [
            "docs/governance/",
            "scripts/",
            "tests/governance/",
            "tests/automation/",
            "docs/contracts/",
            "tests/integration/",
        ],
        "planned_write_paths": [
            "docs/governance/",
            "scripts/",
            "tests/governance/",
            "tests/automation/",
            "docs/contracts/",
            "tests/integration/",
        ],
        "planned_test_paths": [
            "tests/governance/",
            "tests/automation/",
            "tests/contracts/",
            "tests/integration/",
        ],
        "required_tests": [
            "python scripts/check_authority_alignment.py",
            "python scripts/validate_contracts.py",
            "python scripts/check_repo.py",
            "python scripts/check_hygiene.py",
            "pytest tests/governance -q",
            "pytest tests/automation -q",
            "pytest tests/contracts -q",
            "pytest tests/integration -q",
        ],
        "branch_template": "feat/{task_id}-business-automation-round",
    }


def _business_lane_blueprint(blueprint_id: str, title: str, stage: str, suffix: str) -> dict[str, Any]:
    return {
        "blueprint_id": blueprint_id,
        "title": title,
        "task_kind": "execution",
        "execution_mode": "isolated_worktree",
        "stage": stage,
        "size_class": "standard",
        "automation_mode": "autonomous",
        "topology": "single_worker",
        "branch_template": f"feat/{{task_id}}-{{module_slug}}-{suffix}",
    }


def task_blueprints_payload() -> list[dict[str, Any]]:
    return [
        _roadmap_blueprint(),
        _business_parent_blueprint(),
        _business_lane_blueprint(
            "business_stage_bootstrap_execution",
            "Stage bootstrap lane",
            "business-bootstrap-lane",
            "bootstrap",
        ),
        _business_lane_blueprint(
            "business_stage_implementation_execution",
            "Stage implementation lane",
            "business-implementation-lane",
            "implementation",
        ),
    ]


def task_policy_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "authority_source": "docs/product/AUTHORITY_SPEC.md",
        "operator_source": "docs/governance/OPERATOR_MANUAL.md",
        "size_classes": {
            "micro": {
                "target_duration": "<=45m",
                "max_scope_roots": 1,
                "default_topology": "single_task",
                "default_automation_mode": "assisted",
                "split_allowed": False,
            },
            "standard": {
                "target_duration": "45m-4h",
                "max_scope_roots": 2,
                "default_topology": "single_worker",
                "default_automation_mode": "assisted",
                "split_allowed": False,
            },
            "heavy": {
                "target_duration": ">4h",
                "max_scope_roots": "2+",
                "default_topology": "single_worker",
                "default_automation_mode": "manual",
                "split_allowed": True,
                "parallelism_mode": "dynamic",
                "dynamic_lane_ceiling_v1": 4,
                "min_disjoint_write_roots": 2,
                "required_tests_complete": True,
                "reserved_path_conflict_policy": "block_parallelism",
                "auto_downgrade_to_single_worker_on_conflict": True,
            },
        },
        "automation_modes": {
            "manual": {"description": "Manual coordination."},
            "assisted": {"description": "Assisted coordination."},
            "autonomous": {"description": "Autonomous coordination."},
        },
        "stop_conditions": [
            "current_task drift across registry, roadmap, task file, runlog, or worktree entry",
            "contract validation failure",
            "hygiene hard failure",
        ],
        "closeout_rules": [
            "required_tests must appear in the runlog",
            "task status must not remain doing after formal closeout",
        ],
        "task_blueprints": task_blueprints_payload(),
    }


def _stage_module(
    module_id: str,
    owner_stage: str,
    inputs: list[str],
    outputs: list[str],
    depends_on: list[str],
    allowed_dirs: list[str],
    integration_points: list[str],
    required_tests: list[str],
) -> dict[str, Any]:
    return {
        "module_id": module_id,
        "owner_stage": owner_stage,
        "inputs": inputs,
        "outputs": outputs,
        "depends_on": depends_on,
        "allowed_dirs": allowed_dirs,
        "reserved_paths": [
            "docs/governance/",
            "tests/integration/",
            "docs/governance/INTERFACE_CATALOG.yaml",
        ],
        "integration_points": integration_points,
        "required_tests": required_tests,
    }


def _core_stage_modules() -> list[dict[str, Any]]:
    return [
        _stage_module("stage1_orchestration", "stage1", ["source scheduling requests"], ["ingestion jobs"], [], ["src/stage1_orchestration/", "tests/stage1/"], ["stage2_ingestion"], ["pytest tests/stage1 -q"]),
        _stage_module("stage2_ingestion", "stage2", ["ingestion jobs"], ["raw source payloads"], ["stage1_orchestration"], ["src/stage2_ingestion/", "tests/stage2/"], ["stage3_parsing"], ["pytest tests/stage2 -q"]),
        _stage_module("stage3_parsing", "stage3", ["raw source payloads"], ["project_base"], ["stage2_ingestion"], ["src/stage3_parsing/", "tests/stage3/"], ["stage4_validation"], ["pytest tests/stage3 -q"]),
        _stage_module("stage4_validation", "stage4", ["project_base"], ["rule_hit", "evidence", "review_request"], ["stage3_parsing"], ["src/stage4_validation/", "tests/stage4/"], ["stage5_reporting", "stage6_facts"], ["pytest tests/stage4 -q"]),
        _stage_module("stage5_reporting", "stage5", ["validated findings"], ["report_record"], ["stage4_validation"], ["src/stage5_reporting/", "tests/stage5/"], ["stage6_facts"], ["pytest tests/stage5 -q"]),
        _stage_module("stage6_facts", "stage6", ["validated findings", "report artifacts"], ["project_fact"], ["stage4_validation", "stage5_reporting"], ["src/stage6_facts/", "tests/stage6/"], ["stage7_sales", "stage8_contact", "stage9_delivery"], ["pytest tests/stage6 -q"]),
    ]


def _downstream_stage_modules() -> list[dict[str, Any]]:
    return [
        _stage_module("stage7_sales", "stage7", ["project_fact"], ["sales_context"], ["stage6_facts"], ["src/stage7_sales/", "tests/stage7/"], ["tests/integration/"], ["pytest tests/stage7 -q"]),
        _stage_module("stage8_contact", "stage8", ["project_fact"], ["contact_context"], ["stage6_facts"], ["src/stage8_contact/", "tests/stage8/"], ["tests/integration/"], ["pytest tests/stage8 -q"]),
        _stage_module("stage9_delivery", "stage9", ["project_fact", "downstream contexts"], ["delivery_payloads"], ["stage6_facts", "stage7_sales", "stage8_contact"], ["src/stage9_delivery/", "tests/stage9/"], ["tests/integration/"], ["pytest tests/stage9 -q"]),
    ]


def _governance_control_module() -> dict[str, Any]:
    return {
        "module_id": "governance_control_plane",
        "owner_stage": "governance",
        "inputs": ["CURRENT_TASK"],
        "outputs": ["task updates"],
        "depends_on": [],
        "allowed_dirs": ["docs/governance/", "tests/governance/"],
        "reserved_paths": ["src/stage6_facts/"],
        "integration_points": ["tests/governance/"],
        "required_tests": ["pytest tests/base -q"],
    }


def module_map_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "modules": [*_core_stage_modules(), *_downstream_stage_modules(), _governance_control_module()],
    }


def _matrix_entry(*required_tests: str) -> dict[str, Any]:
    return {
        "micro": {"required_tests": [required_tests[0]]},
        "standard": {"required_tests": list(required_tests[:2]) if len(required_tests) > 1 else [required_tests[0]]},
        "heavy": {"required_tests": list(required_tests)},
    }


def test_matrix_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "size_class_gates": {
            "micro": {"preflight": ["python scripts/check_repo.py"], "worker": ["module tests"], "closeout": []},
            "standard": {"preflight": ["python scripts/check_repo.py"], "worker": ["module tests"], "closeout": []},
            "heavy": {"preflight": ["python scripts/check_repo.py"], "worker": ["module tests"], "closeout": []},
        },
        "modules": {
            "stage1_orchestration": _matrix_entry("pytest tests/stage1 -q", "pytest tests/stage1 -q", "pytest tests/stage1 -q", "pytest -q"),
            "stage2_ingestion": _matrix_entry("pytest tests/stage2 -q", "pytest tests/stage2 -q", "pytest tests/stage2 -q", "pytest -q"),
            "stage3_parsing": _matrix_entry("pytest tests/stage3 -q", "pytest tests/stage3 -q", "pytest tests/integration -q", "pytest -q"),
            "stage4_validation": _matrix_entry("pytest tests/stage4 -q", "pytest tests/stage4 -q", "pytest tests/integration -q", "pytest -q"),
            "stage5_reporting": _matrix_entry("pytest tests/stage5 -q", "pytest tests/stage5 -q", "pytest tests/integration -q", "pytest -q"),
            "stage6_facts": _matrix_entry("pytest tests/stage6 -q", "pytest tests/stage6 -q", "pytest tests/integration -q", "pytest -q"),
            "stage7_sales": _matrix_entry("pytest tests/stage7 -q", "pytest tests/stage7 -q", "pytest tests/integration -q", "pytest -q"),
            "stage8_contact": _matrix_entry("pytest tests/stage8 -q", "pytest tests/stage8 -q", "pytest tests/integration -q", "pytest -q"),
            "stage9_delivery": _matrix_entry("pytest tests/stage9 -q", "pytest tests/stage9 -q", "pytest tests/integration -q", "pytest -q"),
            "governance_control_plane": _matrix_entry("pytest tests/base -q", "pytest tests/base -q", "pytest tests/base -q"),
        },
        "single_machine_practical_matrix": {
            "single_machine_lifecycle": {
                "description": "Single-machine lifecycle from active coordination to review or idle.",
                "required_tests": ["pytest tests/governance -q", "pytest tests/automation -q"],
            },
            "single_machine_recovery": {
                "description": "Formal handoff, fallback recovery, release, and takeover on one machine.",
                "required_tests": ["pytest tests/governance -q"],
            },
            "single_machine_write_safety": {
                "description": "Lease-protected write safety and continuation guardrails.",
                "required_tests": ["pytest tests/governance -q"],
            },
            "single_machine_runner_fallback": {
                "description": "Cleanup pressure, lane conflict, and review-bundle fallback on one machine.",
                "required_tests": ["pytest tests/automation -q"],
            },
            "single_machine_orchestrator_runtime": {
                "description": "Runtime tick, reconcile, telemetry, and registry-backed runtime state.",
                "required_tests": ["pytest tests/governance -q", "pytest tests/automation -q"],
            },
            "single_machine_observability": {
                "description": "Stable orchestration-status output for operator-facing runtime inspection.",
                "required_tests": ["pytest tests/governance -q"],
            },
        },
        "future_scale_interface_matrix": {
            "task_source_adapter_contract": {
                "description": "Task-source adapters must expose enabled/implemented/unsupported state explicitly.",
                "required_tests": ["pytest tests/governance -q"],
            },
            "worker_registry_contract": {
                "description": "Worker registry must keep local worker execution explicit and auditable.",
                "required_tests": ["pytest tests/governance -q", "pytest tests/automation -q"],
            },
            "remote_worker_guardrails": {
                "description": "Unsupported remote workers must never be silently scheduled in v1.",
                "required_tests": ["pytest tests/governance -q", "pytest tests/automation -q"],
            },
            "disabled_external_source_visibility": {
                "description": "Disabled external sources must remain visible in orchestration status output.",
                "required_tests": ["pytest tests/governance -q"],
            },
        },
    }
def base_allowed_dirs() -> list[str]:
    return [
        "src/base/",
        "tests/base/",
        "docs/governance/CURRENT_TASK.yaml",
        "docs/governance/DEVELOPMENT_ROADMAP.md",
        "docs/governance/AUTOMATION_INTENTS.yaml",
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
