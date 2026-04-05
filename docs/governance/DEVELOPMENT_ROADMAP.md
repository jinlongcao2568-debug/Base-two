---
current_phase: idle
current_task_id: null
next_recommended_task_id: TASK-GOV-016
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
automation_foundation: in_progress
---

# AX9S Development Roadmap

## Current Task

- no live current task; waiting for explicit activation or roadmap continuation.
## Recently Closed

- `TASK-GOV-013`: completed doc-driven coordination planning and explicit candidate promotion.
- `TASK-MRG-001`: promoted the governed Git publish controls into the main repository baseline.
- `TASK-OPS-001`: closed the publish-readiness integration and queued the downstream task package set.

## Current Phase Goal

- Add continuity-aware successor resolution so only one formal `immediate` top-level successor can auto-activate.
- Add local `checkpoint-task-results` support so dirty task-scoped work can be checkpointed before branch switching.
- Expose `continuation_readiness` in the control plane and make idle repo checks recoverable-predecessor aware.
- Reclassify downstream formal tasks so the queued ledger stays visible without breaking successor uniqueness.

## Explicitly Out Of Scope

- Do not make Git publish actions implicit in continuation, runner, or closeout flows.
- Do not implement the local multi-lane execution dispatcher in the current phase.
- Do not change `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/` in `TASK-GOV-015`.

## Exit Criteria For Current Phase

- `continue-roadmap` can auto-checkpoint live review tasks and recoverable predecessors before successor activation.
- `orchestration-status` contains a stable `continuation_readiness` block.
- `check_repo.py` reports continuity-specific idle diagnostics instead of generic `allowed_dirs` failures.
- The successor ledger has exactly one formal `immediate` top-level successor and the downstream queue is modeled as `backlog`.

## Next Candidate

- `TASK-GOV-016`: local multi-lane execution dispatch v1. This is the only formal `immediate` successor after `TASK-GOV-015`.
- `TASK-SOAK-001`: backlog soak / chaos / fallback validation after multi-lane dispatch lands.
- `TASK-GRAD-001`: backlog heavy-task graduation after soak validation passes.
- `TASK-BIZ-001`: backlog downstream contracts and test skeletons for `stage7-stage9`.
- `TASK-BIZ-002`: backlog governed successor generation for downstream business automation.
- `TASK-BIZ-003`: backlog minimum downstream runtime chain and smoke coverage.
