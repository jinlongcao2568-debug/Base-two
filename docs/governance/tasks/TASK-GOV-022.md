# TASK-GOV-022 authority alignment 失败面与回归对齐

## Task Baseline

- `task_id`: `TASK-GOV-022`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `done`
- `stage`: `governance-authority-alignment-sync-v1`
- `branch`: `feat/TASK-GOV-022-authority-alignment-sync`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `2`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `passed`
## Primary Goals

- Align `check_authority_alignment.py` with the real live failure surface instead of stale idle/continuation assumptions.
- Update the authority-alignment regression to assert the actual scoped behavior rather than outdated stdout expectations.
- Keep this lane isolated from continuation semantics and slow-test restructuring.

## Explicitly Not Doing

- Do not modify `scripts/task_continuation_ops.py` or `scripts/governance_repo_checks.py`.
- Do not change `tests/governance/helpers.py` or `tests/automation/`.
- Do not broaden into environment-contract hardening or generalized planner redesign.

## Task Intake

- `primary_objective`: sync authority-alignment script behavior with its regression coverage.
- `not_doing`: continuation semantics and slow-test layering are delegated to sibling lanes.
- `stage_scope`: governance validation surface only.
- `impact_modules`:
  - `scripts/check_authority_alignment.py`
  - `tests/governance/test_authority_alignment.py`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- The authority-alignment lane validates the real scoped failure surface instead of stale stdout-only behavior.
- `tests/governance/test_authority_alignment.py` is owned solely by this lane and remains disjoint from sibling write/test scopes.
- The lane can be dispatched independently in an isolated worktree under `TASK-GOV-020`.

## Rollback Plan

- Revert the authority-alignment script and regression updates made by this lane.
- Restore the previous test assertions if the new path proves incompatible with the intended control-plane semantics.
- Re-run the lane-specific validation commands to confirm the rollback.

## Allowed Dirs

- `docs/governance/`
- `scripts/check_authority_alignment.py`
- `tests/governance/test_authority_alignment.py`

## Planned Write Paths

- `scripts/check_authority_alignment.py`
- `tests/governance/test_authority_alignment.py`

## Planned Test Paths

- `tests/governance/test_authority_alignment.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_authority_alignment.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`
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
- `lane_index`: `2`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `passed`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-022-authority-alignment-sync`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
