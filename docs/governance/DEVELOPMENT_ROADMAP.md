---
current_phase: governance-hybrid-autonomy-parented-upgrade-v1
current_task_id: TASK-GOV-018
next_recommended_task_id: TASK-GOV-018
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
max_parallel_workers: 4
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
automation_foundation: parented_upgrade_in_progress
---

# AX9S Development Roadmap

## Current Task

- `TASK-GOV-018`: `单一顶层父任务下的分段稳定升级` is the live coordination task for `governance-hybrid-autonomy-parented-upgrade-v1`.
## Recently Closed

- `TASK-GOV-017`: closed the continuity-aware successor recovery and clean-runtime control-plane split.
- `TASK-GOV-013`: completed doc-driven coordination planning and explicit candidate promotion.
- `TASK-MRG-001`: promoted the governed Git publish controls into the main repository baseline.
- `TASK-OPS-001`: closed the publish-readiness integration and queued the downstream task package set.

## Current Phase Goal

- Keep `TASK-GOV-018` as the only top-level governance parent until the child-task automation upgrade is fully runnable.
- Split control-plane truth sources from derived registries and add a scriptable reconciliation path.
- Land child execution preparation, design confirmation, detailed planning, code-task test-first gating, ordered review gates, and standardized child finish workflow.
- Finish this upgrade without enabling top-level full autopilot or multi-lane child execution rollout.

## Explicitly Out Of Scope

- Do not auto-close the top-level parent task.
- Do not auto-switch to another top-level task after this task closes.
- Do not implement top-level full autopilot or parent-task auto-close.
- Do not enable multi-lane or multi-agent execution rollout in this phase.
- Do not change `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/` in `TASK-GOV-018`.

## Exit Criteria For Current Phase

- `TASK-GOV-018` remains the only live top-level governance parent for the whole upgrade.
- Registry drift can be detected and reconciled from `CURRENT_TASK.yaml`, task files, and runlogs.
- Child execution preparation can generate execution context, branch/worktree state, baseline evidence, and prepared-state registry/runlog updates.
- Child workflow gates enforce design confirmation, detailed execution plans, code-task test-first, `spec_review -> quality_review`, and a standardized child finish path.
- Governance and automation regressions pass with `TASK-GOV-018` active.

## Next Candidate

- `TASK-GOV-018`: the only active top-level governance parent for the current upgrade.
- `TASK-SOAK-001`: backlog soak / chaos / fallback validation after multi-lane dispatch lands.
- `TASK-GRAD-001`: backlog heavy-task graduation after soak validation passes.
- `TASK-BIZ-001`: backlog downstream contracts and test skeletons for `stage7-stage9`.
- `TASK-BIZ-002`: backlog governed successor generation for downstream business automation.
- `TASK-BIZ-003`: backlog minimum downstream runtime chain and smoke coverage.
