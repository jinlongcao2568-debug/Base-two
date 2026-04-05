---
current_phase: idle
current_task_id: null
next_recommended_task_id: TASK-BIZ-001
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

## Current Phase Goal

- Add a governed `publish_readiness` block to `orchestration-status` so operators can see whether the live task is ready for `commit`, `push`, and `draft PR`.
- Reuse the existing `publish-preflight` checks instead of inventing a second Git publish gate.
- Queue the downstream 9.5+ phases as formal task packages so the control plane has a single next candidate after `TASK-OPS-001` closes.

## Explicitly Out Of Scope

- Do not make Git publish actions implicit in continuation, runner, or closeout flows.
- Do not implement `stage7-stage9` business automation in the current phase.
- Do not change `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/` in `TASK-OPS-001`.

## Exit Criteria For Current Phase

- `orchestration-status` contains a stable `publish_readiness` block.
- `publish_readiness` matches the live `publish-preflight` result for blocked and ready cases.
- The Phase 3 to Phase 5 tasks exist as queued task packages with scoped task files, runlogs, and handoffs.

## Next Candidate

- `TASK-BIZ-001`: downstream contracts and test skeletons for `stage7-stage9`.
- `TASK-BIZ-002`: governed successor generation for downstream business automation.
- `TASK-BIZ-003`: minimum downstream runtime chain and smoke coverage.
- `TASK-SOAK-001`: continuous soak / chaos / fallback validation.
- `TASK-GRAD-001`: heavy default policy graduation to the 9.5+ operating mode.
