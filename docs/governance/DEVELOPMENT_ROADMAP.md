---
current_phase: governance-automation-risk-hardening-v1
current_task_id: TASK-GOV-005
next_recommended_task_id: null
advance_mode: explicit_or_generated
auto_create_missing_task: true
branch_switch_policy: create_or_switch_if_clean
priority_order:
- governance_automation
- authority_chain
- business_automation
business_automation_enabled: true
business_automation_scope: stage1_to_stage9
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
  stage7: not_established
  stage8: not_established
  stage9: not_established
automation_foundation: in_progress
---

# AX9S Development Roadmap

## Current Task

- `TASK-GOV-005`: `自动续跑风控收口与提示词模块化` is the live coordination task for `governance-automation-risk-hardening-v1`.
## Recently Closed

- `TASK-GOV-001`: closed authority drift, formalized contracts and handoff assets, expanded minimum regression coverage, and hardened the governance control plane.
- `TASK-AUTO-001`: landed the first automation control-plane baseline and closed the shared coordination setup for `automation-control-plane-v1`.
- `TASK-AUTO-002`: formalized `continue-current` and `continue-roadmap`, successor generation, and branch switching for the live roadmap control plane.
- `TASK-GOV-003`: closed the done-but-current gap by introducing the formal idle current-task lifecycle and rehearsal coverage.

## Current Phase Goal

- Split the governance control kernel into explicit shared layers: state transitions, reusable rules, repo checks, and CLI orchestration.
- Reduce control-plane hotspot concentration so `check_hygiene.py` no longer flags the main governance hotspot files for multi-responsibility or oversized helper functions.
- Keep continuation policy aligned with the actual module order in `MODULE_MAP.yaml`, including downstream `stage7-stage9`, without claiming those downstream modules are already production-complete.

## Explicitly Out Of Scope

- Do not change business-stage implementation code under `src/`.
- Do not introduce a second task ledger, a second roadmap source, or a relaxed rule that allows `done` tasks to remain the live current task.
- Do not claim that downstream `stage7-stage9` automation is finished; this phase only removes the artificial governance restriction and keeps continuation order aligned with the development module map.

## Exit Criteria For Current Phase

- `check_hygiene.py` no longer flags `scripts/governance_controls.py`, `scripts/check_repo.py`, or `scripts/check_authority_alignment.py`.
- `check_repo.py`, `check_authority_alignment.py`, and the governance/automation regression suites remain green after the internal split.
- Shared state-machine helpers are covered by direct governance tests rather than only by CLI rehearsal tests.
- Roadmap/business policy validation accepts the downstream stage order defined in `MODULE_MAP.yaml` instead of hard-pinning `stage7-stage9` to `deferred_manual`.

## Next Candidate

- After this phase closes, the next automation phases can build execution playbooks, acceptance DSLs, release control, and runtime feedback on top of the shared kernel and the full `stage1-stage9` module order.
