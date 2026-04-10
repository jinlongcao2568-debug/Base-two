---
current_phase: governance-doc-entry-slimming-v1
current_task_id: TASK-GOV-088
next_recommended_task_id: null
advance_mode: explicit_or_generated
auto_create_missing_task: true
branch_switch_policy: create_or_switch_if_clean
priority_order:
- governance_automation
- authority_chain
- business_automation
business_automation_enabled: true
business_automation_scope: stage2_to_stage6
pilot_enabled_candidates: []
parallel_strategy: dependency_aware_disjoint_writes
max_parallel_workers: 9
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

- `TASK-GOV-088`: `Slim governance entry docs and route product-first` is the live coordination task for `governance-doc-entry-slimming-v1`.
## Recently Closed

- `TASK-GOV-066`: enforced compiled-only candidate source and added path/pilot gates for roadmap evaluation.
- `TASK-GOV-065`: bound MVP scope and coverage gates to roadmap evaluation and automation scope.
- `TASK-GOV-064`: enforced single-ledger control-plane writes with ledger divergence detection.
- `TASK-GOV-037`: blocked idle/no-successor roadmap continuation with a deterministic governance error instead of a ready/no-op mismatch.
- `TASK-GOV-035`: separated live governance surfaces from historical audit artifacts and search inputs.
- `TASK-GOV-034`: narrowed governance test triggering so ordinary governance edits no longer default to the full governance and automation suites.
- `TASK-GOV-024`: closed the governed closeout/lease/runtime-contract bundle.
- `TASK-GOV-019`: corrected stale successor inputs and absorbed-backlog filtering.

## Current Phase Goal

- Await next governance activation with MVP/coverage hard gates and single-ledger controls in place.

## Internal Gates

1. `phase_1_reproduce_idle_no_successor_gap`
   - confirm `automation_intent.py preflight --utterance "持续按路线图开发"` and `continue-roadmap` disagree on whether work can advance
   - keep the task scoped to governance docs, task lifecycle scripts, automation routing, and targeted regressions only
2. `phase_2_repair_continuation_decision`
   - make idle/no-successor continuation either generate/activate a governed successor or return a deterministic blocker
   - prevent absorbed or historical task artifacts from becoming the current successor source
3. `phase_3_align_intent_and_runner`
   - align automation intent preflight/execute and the one-shot runner with the repaired continuation decision
   - avoid broadening default governance or automation test gates
4. `phase_4_regression_evidence`
   - prove the repaired path no longer has a `ready`/`no successor` mismatch
   - prove historical absorbed tasks remain ignored for current successor selection

## Explicitly Out Of Scope

- Do not rewrite or delete historical task files, runlogs, handoffs, or registry rows.
- Do not touch `src/`, `docs/contracts/`, `db/migrations/`, or stage/contract/integration suites.
- Do not change the test bundles defined in `TEST_MATRIX.yaml` or weaken release-grade protections.
- Do not introduce a second governance source of truth outside the governed current-task and task-file derivation commands.

## Exit Criteria

- `continue-roadmap` from idle/no-successor no longer silently stops when roadmap policy allows missing-task creation.
- Automation intent preflight and execution no longer report a continuation path as `ready` unless the mapped runner can advance or the blocker is explicit.
- Targeted governance/automation regressions cover the mismatch and the historical/absorbed-task safety boundary.

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
