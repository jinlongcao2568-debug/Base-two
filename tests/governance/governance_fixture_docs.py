from __future__ import annotations

from pathlib import Path

import yaml


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)


def write_live_governance_boundary(path: Path) -> None:
    path.write_text(
        (
            "# Live Governance Boundary\n\n"
            "`docs/governance/CURRENT_TASK.yaml` remains the only live execution entry.\n\n"
            "Historical artifacts remain searchable for audit and recovery, but they are not the current default gate or prompt source.\n\n"
            "- Closed task files, runlogs, handoffs, and registry rows must not redefine the current default governance gate.\n"
            "- `docs/governance/TASK_REGISTRY.yaml` is a live ledger for task existence and state, but closed task rows and their `required_tests` remain historical audit evidence.\n"
        ),
        encoding="utf-8",
    )


def write_git_publish_policy(path: Path) -> None:
    _write_yaml(
        path,
        {
            "version": "1.0",
            "updated_at": "2026-04-05T00:00:00+08:00",
            "authority_source": "docs/governance/OPERATOR_MANUAL.md",
            "publish_mode": "explicit_on_demand_only",
            "allowed_publish_statuses": ["review", "done"],
            "default_remote": "origin",
            "default_base_branch": "main",
            "default_pr_mode": "draft",
        },
    )


def write_coordination_planner_policy(path: Path) -> None:
    path.write_text(
        (
            "version: '1.0'\n"
            "updated_at: '2026-04-05T00:00:00+08:00'\n"
            "authority_source: docs/governance/README.md\n"
            "candidate_generation_mode: candidate_then_activate\n"
            "candidate_output_dir: .codex/local/coordination_candidates/\n"
            "allow_generated_blueprints_when_no_candidates: true\n"
        ),
        encoding="utf-8",
    )


def write_handoff_policy(path: Path) -> None:
    path.write_text(
        (
            "version: '1.0'\n"
            "updated_at: '2026-04-05T00:00:00+08:00'\n"
            "authority_source: docs/governance/README.md\n"
            "create_on_new_top_level_coordination_task: true\n"
            "recovery_source_of_truth: docs/governance/handoffs/\n"
            "fallback_mode: task_and_runlog\n"
            "lease_mode: strict_lease\n"
            "stale_after_minutes: 30\n"
            "takeover_rules:\n"
            "  - active_other_session_requires_explicit_takeover\n"
            "  - stale_lease_allows_reclaim_on_continue_current\n"
            "  - release_does_not_change_task_status\n"
            "required_fields:\n"
            "  - task_id\n"
            "  - summary_status\n"
            "  - last_handoff_at\n"
            "  - completed_items\n"
            "  - remaining_items\n"
            "  - next_step\n"
            "  - next_tests\n"
            "  - current_risks\n"
            "  - candidate_write_paths\n"
            "  - candidate_test_paths\n"
            "  - resume_notes\n"
        ),
        encoding="utf-8",
    )


def write_prompt_governance_files(root: Path) -> None:
    _write_prompt_catalog(root / "docs/governance/PROMPT_MODULE_CATALOG.yaml")
    _write_prompt_module_docs(root)


def _write_prompt_catalog(path: Path) -> None:
    path.write_text(
        "".join(
            [
                _prompt_catalog_header(),
                _prompt_catalog_modules_section(),
                _prompt_catalog_role_profiles_section(),
                _prompt_catalog_policy_section(),
                _prompt_catalog_runtime_profiles_section(),
            ]
        ),
        encoding="utf-8",
    )


def _prompt_catalog_header() -> str:
    return (
        "version: '1.0'\n"
        "authority_source: docs/governance/README.md\n"
        "source_root: docs/governance/prompt_modules/\n"
    )


def _prompt_catalog_modules_section() -> str:
    return (
        "modules:\n"
        "  - module_id: operator_manual\n"
        "    path: OPERATOR_MANUAL.md\n"
        "    applies_to:\n"
        "      - coordination\n"
        "      - governance\n"
        "  - module_id: module_map\n"
        "    path: MODULE_MAP.yaml\n"
        "    applies_to:\n"
        "      - coordination\n"
        "      - business_planning\n"
        "  - module_id: task_policy\n"
        "    path: TASK_POLICY.yaml\n"
        "    applies_to:\n"
        "      - coordination\n"
        "      - lifecycle\n"
        "  - module_id: capability_map\n"
        "    path: CAPABILITY_MAP.yaml\n"
        "    applies_to:\n"
        "      - business_planning\n"
        "      - automation\n"
    )


def _prompt_catalog_role_profiles_section() -> str:
    return (
        "role_profiles:\n"
        "  coordinator:\n"
        "    required_modules:\n"
        "      - operator_manual\n"
        "      - task_policy\n"
        "    optional_modules:\n"
        "      - module_map\n"
        "  planner:\n"
        "    required_modules:\n"
        "      - operator_manual\n"
        "      - module_map\n"
        "      - capability_map\n"
        "  worker:\n"
        "    required_modules:\n"
        "      - operator_manual\n"
        "      - task_policy\n"
    )


def _prompt_catalog_policy_section() -> str:
    return (
        "policy:\n"
        "  runtime_prompt_dir: docs/governance/runtime_prompts/\n"
        "  generated_profiles:\n"
        "    - coordinator.md\n"
        "    - planner.md\n"
        "    - worker.md\n"
        "  generation_mode: derived_only\n"
    )


def _prompt_catalog_runtime_profiles_section() -> str:
    return (
        "runtime_profiles:\n"
        "  - role: coordinator\n"
        "    output_path: docs/governance/runtime_prompts/coordinator.md\n"
        "  - role: planner\n"
        "    output_path: docs/governance/runtime_prompts/planner.md\n"
        "  - role: worker\n"
        "    output_path: docs/governance/runtime_prompts/worker.md\n"
    )


def _write_prompt_module_docs(root: Path) -> None:
    module_dir = root / "docs/governance/prompt_modules"
    module_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, content in _prompt_module_files().items():
        path = module_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _prompt_module_files() -> dict[str, str]:
    return {
        "operator_manual.md": "# Operator Manual Prompt\n- Follow the live operator manual.\n",
        "module_map.md": "# Module Map Prompt\n- Plan only from the live module map.\n",
        "task_policy.md": "# Task Policy Prompt\n- Respect task status, boundary, and closeout rules.\n",
        "capability_map.md": "# Capability Map Prompt\n- Use only implemented capabilities.\n",
    }
