# TASK-GOV-023 governance / automation 慢测试分层与降耗

## Task Baseline

- `task_id`: `TASK-GOV-023`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `done`
- `stage`: `governance-slow-test-layering-v1`
- `branch`: `feat/TASK-GOV-023-slow-test-layering`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `3`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `passed`
## Primary Goals

- Separate the slow governance / automation regression work into an isolated lane with its own helper and automation-suite scope.
- Reduce repeated temp-repo and git churn inside the targeted slow tests without changing continuation or authority semantics.
- Keep the lane narrowly focused on test layering, helper reuse, and local regression cost.

## Explicitly Not Doing

- Do not modify `scripts/task_continuation_ops.py`, `scripts/governance_repo_checks.py`, or `scripts/check_authority_alignment.py`.
- Do not change `tests/governance/test_check_repo.py`, `tests/governance/test_task_continuation.py`, or `tests/governance/test_authority_alignment.py`.
- Do not introduce environment-contract hardening or product-stage runtime changes.

## Task Intake

- `primary_objective`: isolate and reduce the slow-test burden in governance / automation suites.
- `not_doing`: state semantics and authority-alignment fixes are delegated to sibling lanes.
- `stage_scope`: governance and automation test infrastructure only.
- `impact_modules`:
  - `tests/governance/helpers.py`
  - `tests/automation/`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- Slow-test restructuring remains isolated to the helper and automation-suite surfaces owned by this lane.
- The lane maintains disjoint write and test scopes from sibling lanes under `TASK-GOV-020`.
- The parent task retains responsibility for aggregate final verification after this lane completes.

## Rollback Plan

- Revert the helper and automation-suite changes introduced by this lane.
- Restore the previous slow-test structure if the reduction work causes regression instability.
- Re-run the lane-specific automation checks to confirm rollback.

## Allowed Dirs

- `docs/governance/`
- `tests/governance/helpers.py`
- `tests/automation/`

## Planned Write Paths

- `tests/governance/helpers.py`
- `tests/automation/`

## Planned Test Paths

- `tests/automation/test_automation_runner.py`
- `tests/automation/test_high_throughput_runner.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `pytest tests/automation/test_automation_runner.py -q`
- `pytest tests/automation/test_high_throughput_runner.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `blocked`
- `completed_scope`: `active_progress`
- `remaining_scope`: `blocked_work_remaining`
- `next_gate`: `blocking_resolution`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `3`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `passed`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-023-slow-test-layering`
- `updated_at`: `2026-04-06T17:02:23+08:00`
<!-- generated:task-meta:end -->
