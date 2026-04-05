---
current_phase: governance-task-lifecycle-closure-v1
current_task_id: TASK-GOV-003
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

- `TASK-GOV-003`: formalize the idle current-task lifecycle so `review -> done -> idle -> successor` remains green and recoverable.

## Recently Closed

- `TASK-GOV-001`: closed authority drift, formalized contracts and handoff assets, expanded minimum regression coverage, and hardened the governance control plane.
- `TASK-AUTO-001`: landed the first automation control-plane baseline and closed the shared coordination setup for `automation-control-plane-v1`.
- `TASK-AUTO-002`: formalized `continue-current` and `continue-roadmap`, successor generation, and branch switching for the live roadmap control plane.

## Current Phase Goal

- Introduce a formal idle current-task payload in `CURRENT_TASK.yaml` without creating a second control-plane ledger.
- Make closeout, repo gates, authority scoring, and roadmap continuation accept `idle` as the only legal zero-state after a live task is closed without an immediate successor.
- Prove the lifecycle with governance and automation rehearsals that cover `review -> done -> idle -> successor`.

## Explicitly Out Of Scope

- Do not change contracts, business-stage implementation code, or `stage7-stage9` automation policy.
- Do not introduce a second task ledger, a second roadmap source, or a relaxed rule that allows `done` tasks to remain live current tasks.
- Do not auto-activate a successor during closeout unless an explicit continuation command requests it.

## Exit Criteria For Current Phase

- `check_repo.py` passes after a live current task is closed into the formal idle state.
- `check_authority_alignment.py` returns all category scores to `100`, including consistency, single source of truth, and development control.
- `continue-roadmap` can safely activate an explicit or generated successor from the idle state.
- Governance and automation rehearsal tests prove the full `review -> done -> idle -> successor` lifecycle without manual ledger edits.

## Next Candidate

- After this phase closes, roadmap continuation can resume `stage1-stage6` business successor generation from either a freshly closed review task or the formal idle state.
