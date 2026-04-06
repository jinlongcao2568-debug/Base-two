---
current_phase: idle
current_task_id: null
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
automation_foundation: single_parent_total_upgrade_in_progress
---

# AX9S Development Roadmap

## Current Task

- no live current task; waiting for explicit activation or roadmap continuation.
## Recently Closed

- `TASK-GOV-017`: closed the continuity-aware successor recovery and clean-runtime control-plane split.
- `TASK-GOV-016`: closed the local multi-agent dispatch foundation.
- `TASK-GOV-015`: closed continuity stability and continuation hardening.

## Current Phase Goal

- Rebaseline `TASK-GOV-018` into the single total-upgrade parent task.
- Move top-level closeout and continuation to `ai_guarded` instead of manual closeout.
- Expand governed child workflow into contracts, shared contracts, stage7-stage9 runtime, migrations, and integration test surfaces.
- Complete runtime acceptance decoupling, stateless migration baseline, and downstream smoke validation without touching `src/stage6_facts/`.
- Graduate eligible blueprints to `autonomous + parallel_parent` only after soak and chaos validation pass.

## Six Internal Gates

1. `phase_1_rebaseline_task_scope`
   - widen `TASK-GOV-018` scope
   - absorb `TASK-BIZ-001/002/003`, `TASK-SOAK-001`, and `TASK-GRAD-001`
   - align CURRENT_TASK, roadmap, registry, worktree registry, task file, and runlog
2. `phase_2_top_level_ai_guarded_closeout`
   - switch top-level closeout from `manual` to `ai_guarded`
   - keep `continue-current` idle-only after closeout
   - keep `continue-roadmap` guarded by uniqueness, dependencies, and boundary completeness
3. `phase_3_expand_child_workflow_scope`
   - extend governed child gates into contracts/shared-contracts/stage7-stage9/migrations/integration
   - keep `src/stage1_orchestration/` through `src/stage6_facts/` reserved
4. `phase_4_runtime_contract_decoupling`
   - move runtime acceptance to a contract-owned artifact
   - land minimal `stage7 -> stage8 -> stage9` consumer chain that only consumes `project_fact`
5. `phase_5_migration_and_integration_hardening`
   - add stateless baseline migration pack
   - upgrade integration validation to `stage6 -> stage7/8 -> stage9` runtime smoke
6. `phase_6_soak_and_parallel_graduation`
   - run soak/chaos validation for roadmap runner, heartbeat, restart, and orphan cleanup
   - only then open eligible heavy blueprints to `autonomous + parallel_parent + 4 lanes`

## Explicitly Out Of Scope

- Do not create a sibling top-level task for governance, compatibility, soak, or graduation.
- Do not rewrite `src/stage6_facts/` or create a second fact layer.
- Do not auto-switch to an ambiguous or dependency-blocked successor.
- Do not enable unconditional full autopilot.

## Exit Criteria For Current Upgrade

- All six internal gates are complete.
- `TASK-GOV-018` task file, runlog, roadmap, registry, worktree registry, and CURRENT_TASK are aligned.
- No registry drift remains.
- No child lane remains open.
- `ai_guarded` closeout and guarded `continue-roadmap` behavior are covered by automated evidence.
- Stage7-stage9 minimal runtime, contract-owned acceptance, stateless migration baseline, and integration smoke all pass.

## Absorbed Backlog

- `TASK-BIZ-001`: absorbed into `TASK-GOV-018` phase 4 and phase 5.
- `TASK-BIZ-002`: absorbed into `TASK-GOV-018` phase 2 and phase 3.
- `TASK-BIZ-003`: absorbed into `TASK-GOV-018` phase 4 and phase 5.
- `TASK-SOAK-001`: absorbed into `TASK-GOV-018` phase 6.
- `TASK-GRAD-001`: absorbed into `TASK-GOV-018` phase 6.

## Next Candidate

- `TASK-GOV-018`: continue the six internal gates until the total-upgrade parent task is fully closed.
