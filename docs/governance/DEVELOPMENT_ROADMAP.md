---
current_phase: governance-novice-entry-v1
current_task_id: TASK-GOV-029
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
max_parallel_workers: 20
spec_source_policy: baseline_contracts_task_package
business_gap_priority:
- bootstrap_required
- implementation_ready
- integration_expansion
stage_establishment:
  stage1: deferred_manual
  stage2: deferred_manual
  stage3: deferred_manual
  stage4: deferred_manual
  stage5: deferred_manual
  stage6: deferred_manual
  stage7: deferred_manual
  stage8: deferred_manual
  stage9: deferred_manual
automation_foundation: stale_successor_inputs_under_correction
---

# AX9S Development Roadmap

## Current Task

- `TASK-GOV-029`: `治理小白化入口：统一自动化开发入口` is the live coordination task for `governance-novice-entry-v1`.
## Recently Closed

- `TASK-GOV-018`: closed the parented total-upgrade track and left stale successor inputs that must now be cleaned.
- `TASK-GOV-017`: closed the continuity-aware successor recovery and clean-runtime control-plane split.
- `TASK-GOV-016`: closed the local multi-agent dispatch foundation.

## Current Phase Goal

- Clear stale roadmap successor inputs left behind after `TASK-GOV-018` closeout.
- Keep `continue-roadmap` and generated successor recommendation available when a valid direction exists.
- Permanently exclude absorbed backlog from planner and continuation successor landscapes.
- Ensure the system returns `no successor` when no valid successor remains instead of reviving stale tasks.

## Internal Gates

1. `phase_1_rebaseline_live_task`
   - keep `TASK-GOV-019` as the only live current task
   - align roadmap, task package, and runlog with the scoped correction objective
2. `phase_2_clear_stale_roadmap_inputs`
   - remove the stale explicit pointer to `TASK-GOV-018`
   - neutralize stale `stage_establishment` values so they no longer imply a successor round
3. `phase_3_filter_absorbed_backlog`
   - exclude `TASK-BIZ-001/002/003`, `TASK-SOAK-001`, and `TASK-GRAD-001` from planner candidates
   - exclude absorbed tasks from explicit successor validation and uniqueness checks
4. `phase_4_clean_local_candidate_cache`
   - clear `.codex/local/coordination_candidates/` of absorbed backlog artifacts
   - keep only still-valid recommendation outputs
5. `phase_5_regression_evidence`
   - prove absorbed backlog does not re-enter `plan-coordination`
   - prove stale absorbed explicit pointers do not block valid fallback successors

## Explicitly Out Of Scope

- Do not remove `continue-roadmap`, `plan-coordination`, or generated successor capability.
- Do not create a replacement sibling task for governance, business automation, soak, or graduation.
- Do not rewrite `src/stage6_facts/` or create a second fact layer.
- Do not reopen absorbed backlog as top-level successor candidates.
- Do not auto-switch to an ambiguous or dependency-blocked successor.

## Exit Criteria

- `next_recommended_task_id` is empty or points to a live, non-absorbed, immediate successor.
- `stage_establishment` no longer causes stale business successor generation.
- Absorbed backlog is excluded from planner candidates, continuation fallback, and uniqueness checks.
- Local candidate cache no longer contains absorbed backlog artifacts.
- Governance and automation regression tests cover the corrected behavior.

## Absorbed Backlog

- `TASK-BIZ-001`: absorbed by `TASK-GOV-018`; must stay out of successor selection.
- `TASK-BIZ-002`: absorbed by `TASK-GOV-018`; must stay out of successor selection.
- `TASK-BIZ-003`: absorbed by `TASK-GOV-018`; must stay out of successor selection.
- `TASK-SOAK-001`: absorbed by `TASK-GOV-018`; must stay out of successor selection.
- `TASK-GRAD-001`: absorbed by `TASK-GOV-018`; must stay out of successor selection.

## Next Candidate

- No valid successor is currently declared.
- `continue-roadmap` may still recommend a future successor when the roadmap, candidate cache, and capability state become valid again.
