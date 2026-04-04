---
current_phase: automation-business-autopilot-stage1-stage6-v1
current_task_id: TASK-AUTO-003
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

- `TASK-AUTO-003`: extend the live control plane so automation can generate dependency-aware `stage1-stage6` business successors, parallel child tasks, and review-bundle closeout.

## Recently Closed

- `TASK-GOV-001`: closed authority drift, formalized contracts and handoff assets, expanded minimum regression coverage, and hardened the governance control plane.
- `TASK-AUTO-001`: landed the first automation control-plane baseline and closed the shared coordination setup for `automation-control-plane-v1`.
- `TASK-AUTO-002`: formalized `continue-current` and `continue-roadmap`, successor generation, and branch switching for the live roadmap control plane.

## Current Phase Goal

- Add machine-readable `stage1-stage6` business automation policy to the live roadmap.
- Let automation resolve business successors from real stage gaps, module boundaries, and dependency order.
- Reuse the existing `parallel_parent + worktree + auto-close-children` base for business child execution and review-bundle closeout.

## Explicitly Out Of Scope

- Do not auto-generate or auto-activate `stage7-stage9` business tasks.
- Do not relax the clean-worktree requirement before switching or creating a successor branch.
- Do not create a second task ledger or second roadmap source.

## Exit Criteria For Current Phase

- `continue-roadmap` can generate a `stage1-stage6` business parent successor when governance successor generation is exhausted.
- Generated business parents carry dependency-aware child execution tasks with explicit scope, contracts, authority inputs, and review bundle tests.
- `automation_runner.py once --continue-roadmap --prepare-worktrees` can prepare child worktrees and auto-close only those children whose review bundle passes.
- `stage7-stage9` remain deferred manual stages in both roadmap policy and generated successor selection.

## Next Candidate

- After this phase, roadmap continuation may auto-generate only `stage1-stage6` business successor rounds; `stage7-stage9` stay manual until a separate downstream blueprint phase lands.
