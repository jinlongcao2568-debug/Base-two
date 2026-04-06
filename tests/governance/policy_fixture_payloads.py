from __future__ import annotations

from typing import Any


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


def _task_policy_size_classes() -> dict[str, dict[str, Any]]:
    return {
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
    }


def _task_policy_child_workflow() -> dict[str, Any]:
    return {
        "parent_closeout_policy": {
            "top_level_parent_mode": "ai_guarded",
            "auto_promote_after_children_close": False,
            "auto_activate_successor_after_close": False,
            "closeout_requirements": [
                "required tests fully pass",
                "registry has no drift",
                "no child lane remains open",
                "review and closeout evidence is complete",
                "task file, runlog, design doc, and CURRENT_TASK are aligned",
                "no pending exception approval exists",
                "no unresolved high-risk blocker remains",
            ],
            "continue_current_behavior": "close the current top-level task to idle when ai_guarded closeout is satisfied; never auto-activate a successor",
            "continue_roadmap_behavior": "auto-activate the next top-level task only when the successor is unique, dependencies are satisfied, and the boundary is explicit; otherwise stop with blockers",
        }
    }


def task_policy_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "authority_source": "docs/product/AUTHORITY_SPEC.md",
        "operator_source": "docs/governance/OPERATOR_MANUAL.md",
        "size_classes": _task_policy_size_classes(),
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
            "child execution auto-close may not auto-close the top-level coordination parent",
        ],
        "child_execution_workflow": _task_policy_child_workflow(),
        "governed_scope_paths": [
            "docs/governance/",
            "scripts/",
            "tests/governance/",
            "tests/automation/",
            "docs/contracts/",
            "src/shared/contracts/",
            "src/stage7_sales/",
            "src/stage8_contact/",
            "src/stage9_delivery/",
            "db/migrations/",
            "tests/contracts/",
            "tests/integration/",
            "tests/stage7/",
            "tests/stage8/",
            "tests/stage9/",
            ".gitignore",
        ],
        "single_writer_roots": [
            "db/migrations/",
            "src/stage7_sales/",
            "src/stage8_contact/",
            "src/stage9_delivery/",
        ],
        "task_blueprints": task_blueprints_payload(),
    }
