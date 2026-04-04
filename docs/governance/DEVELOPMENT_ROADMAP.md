---
current_phase: governance-test-maintainability-hardening-v1
current_task_id: TASK-GOV-002
next_recommended_task_id: null
advance_mode: explicit_or_generated
auto_create_missing_task: true
branch_switch_policy: create_or_switch_if_clean
priority_order:
- governance_automation
- authority_chain
- business_automation
business_automation_enabled: true
business_automation_scope: stage1_to_stage6
parallel_strategy: dependency_aware_disjoint_writes
max_parallel_workers: 2
spec_source_policy: baseline_contracts_task_package
business_gap_priority:
- bootstrap_required
- implementation_ready
- integration_expansion
stage_establishment:
  stage1: bootstrap_required
  stage2: bootstrap_required
  stage3: implementation_ready
  stage4: implementation_ready
  stage5: bootstrap_required
  stage6: implementation_ready
  stage7: deferred_manual
  stage8: deferred_manual
  stage9: deferred_manual
automation_foundation: in_progress
---

# AX9S Development Roadmap

## Current Task

- `TASK-GOV-002`: reduce the current automation/governance test warning hotspots by introducing reusable scenario builders and a hygiene regression guard.

## Recently Closed

- `TASK-GOV-001`: closed authority drift, formalized contracts and handoff assets, expanded minimum regression coverage, and hardened the governance control plane.
- `TASK-AUTO-001`: landed the first automation control-plane baseline and closed the shared coordination setup for `automation-control-plane-v1`.
- `TASK-AUTO-002`: formalized `continue-current` and `continue-roadmap`, successor generation, and branch switching for the live roadmap control plane.

## Current Phase Goal

- Remove the current automation/governance test hotspot warnings without loosening hygiene thresholds.
- Consolidate repetitive task/worktree setup behind reusable scenario builders so new review-bundle and continuation tests do not keep growing long setup bodies.
- Add a hygiene regression guard that keeps the current hotspot files out of future warning output.

## Explicitly Out Of Scope

- Do not change `check_hygiene.py` thresholds or warning semantics.
- Do not refactor runtime scripts or business implementation code.
- Do not chase low-value warnings outside the current hotspot test files.

## Exit Criteria For Current Phase

- `check_hygiene.py` no longer reports warnings for `tests/automation/test_automation_runner.py`.
- `check_hygiene.py` no longer reports warnings for `tests/governance/fixture_payloads.py`, `tests/governance/test_check_repo.py`, and `tests/governance/test_task_ops.py`.
- Governance and automation tests keep passing after scenario-builder extraction and builder-backed assertions.
- A dedicated regression test fails if those hotspot files reappear in future hygiene warning output.

## Next Candidate

- After this phase closes, roadmap continuation can resume `stage1-stage6` business successor generation on top of a cleaner automation/governance test base.
