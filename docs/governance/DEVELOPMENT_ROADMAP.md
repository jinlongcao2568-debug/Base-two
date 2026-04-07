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

- `TASK-GOV-035`: separated live governance surfaces from historical audit artifacts and search inputs.
- `TASK-GOV-034`: narrowed governance test triggering so ordinary governance edits no longer default to the full governance and automation suites.
- `TASK-GOV-024`: closed the governed closeout/lease/runtime-contract bundle.
- `TASK-GOV-019`: corrected stale successor inputs and absorbed-backlog filtering.

## Current Phase Goal

- Make new-task activation a single governed operation instead of a manual multi-ledger sequence.
- Provide an explicit ledger derivation command for drift repair without weakening the live-vs-historical boundary.
- Preserve closed task files as historical evidence while allowing task-file repair under governed constraints.

## Internal Gates

1. `phase_1_activate_ledger_command_task`
   - align CURRENT_TASK, roadmap, registry, worktree entry, task file, runlog, and handoff with `TASK-GOV-036`
   - keep the task scoped to governance docs, task lifecycle scripts, and governance regressions only
2. `phase_2_queue_and_activate`
   - add a command that creates or repairs a queued coordination task and activates it with branch and ledger sync
   - preserve clean-worktree branch-switch safety
3. `phase_3_derive_ledgers`
   - add explicit source selection for current-task and task-file derivation
   - prevent closed historical task files from overwriting unrelated live current-task state
4. `phase_4_regression_evidence`
   - prove the new commands repair expected drift and reject unsafe historical/live overwrites
   - keep the validation set targeted to lifecycle command behavior

## Explicitly Out Of Scope

- Do not rewrite or delete historical task files, runlogs, handoffs, or registry rows.
- Do not touch `src/`, `docs/contracts/`, `db/migrations/`, or stage/contract/integration suites.
- Do not change the test bundles defined in `TEST_MATRIX.yaml` or weaken release-grade protections.
- Do not introduce a second governance source of truth outside the governed current-task and task-file derivation commands.

## Exit Criteria

- `queue-and-activate` creates or repairs coordination-task activation without leaving half-synced ledgers.
- `derive-ledgers` repairs current-task and task-file drift with dry-run by default and guarded write behavior.
- Governance regressions cover current-task derivation, task-file derivation, closed historical safety, and live-task conflict blocking.

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
