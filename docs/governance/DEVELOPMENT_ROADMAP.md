---
current_phase: idle
current_task_id: null
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
max_parallel_workers: 4
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
automation_foundation: targeted_governance_test_triggers_live
---

# AX9S Development Roadmap

## Current Task

- no live current task; waiting for explicit activation or roadmap continuation.
## Recently Closed

- `TASK-GOV-034`: narrowed governance test triggering so ordinary governance edits no longer default to the full governance and automation suites.
- `TASK-GOV-024`: closed the governed closeout/lease/runtime-contract bundle.
- `TASK-GOV-019`: corrected stale successor inputs and absorbed-backlog filtering.

## Current Phase Goal

- Establish an explicit boundary between live governance surfaces and historical audit artifacts.
- Prevent closed task files, runlogs, handoffs, and registry history from being mistaken for the current default governance test gate.
- Preserve historical evidence exactly as recorded while redirecting operator and prompt search behavior toward the live governance surfaces first.

## Internal Gates

1. `phase_1_activate_boundary_task`
   - align CURRENT_TASK, roadmap, registry, worktree entry, task file, runlog, and handoff with `TASK-GOV-035`
   - keep the task scoped to governance docs, authority checks, and governance regressions only
2. `phase_2_define_live_governance_surfaces`
   - add a live boundary document that names the canonical operator and prompt sources
   - explicitly classify closed tasks, runlogs, handoffs, and registry history as audit artifacts
3. `phase_3_align_operator_and_prompt_guidance`
   - point operator guidance and prompt governance at the live surfaces first
   - forbid treating historical required_tests records as current default gates
4. `phase_4_regression_evidence`
   - prove authority and governance checks fail if the live boundary is missing or the live-vs-historical distinction drifts
   - keep the validation set targeted; do not reintroduce full governance or automation suites as default gates

## Explicitly Out Of Scope

- Do not rewrite or delete historical task files, runlogs, handoffs, or registry rows.
- Do not touch `src/`, `docs/contracts/`, `db/migrations/`, or stage/contract/integration suites.
- Do not change the test bundles defined in `TEST_MATRIX.yaml` or weaken release-grade protections.
- Do not introduce a second governance source of truth outside the existing live control-plane documents.

## Exit Criteria

- Live governance guidance names the canonical live surfaces and classifies historical artifacts as audit-only evidence.
- Operator and prompt guidance no longer leave room to infer current default gates from historical task/runlog/handoff/registry records.
- Authority and governance regressions cover the new boundary behavior without requiring the full governance or automation suites.

## Historical Artifact Classes

- closed task files under `docs/governance/tasks/`
- closed runlogs under `docs/governance/runlogs/`
- handoff snapshots under `docs/governance/handoffs/`
- historical rows in `docs/governance/TASK_REGISTRY.yaml`

## Search Boundary

- Search and prompt loading must start from live governance surfaces:
  - `docs/product/AUTHORITY_SPEC.md`
  - `docs/governance/OPERATOR_MANUAL.md`
  - `docs/governance/CURRENT_TASK.yaml`
  - the live current task file and runlog
  - the live governance maps and policies (`MODULE_MAP`, `CAPABILITY_MAP`, `TASK_POLICY`, `TEST_MATRIX`)
- Historical artifacts remain searchable for audit and recovery, but they are not the current default gate or prompt source.
