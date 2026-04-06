# TASK-GOV-021 idle / continuation 语义与 repo gate 对齐

## Task Baseline

- `task_id`: `TASK-GOV-021`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `blocked`
- `stage`: `governance-state-machine-idle-semantics-v1`
- `branch`: `feat/TASK-GOV-021-idle-continuation-gates`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `blocked`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `1`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Align continuation readiness and repo-gate behavior for the legal `idle + no_successor` path.
- Keep outcome semantics distinguishable across `ready`, `no_successor`, `ambiguous`, and `blocked` within the continuation / repo-check surfaces.
- Add or update narrow regression coverage for continuation and repo-gate handling only.

## Explicitly Not Doing

- Do not touch `scripts/check_authority_alignment.py` or `tests/governance/test_authority_alignment.py`.
- Do not modify `tests/governance/helpers.py` or `tests/automation/`.
- Do not expand into environment-contract hardening, subprocess portability, or roadmap-generation redesign.

## Task Intake

- `primary_objective`: repair the continuation and repo-gate semantics around legal idle / no-successor handling.
- `not_doing`: authority-alignment fixes and slow-test layering are handled by sibling lanes.
- `stage_scope`: governance control plane only.
- `impact_modules`:
  - `scripts/task_continuation_ops.py`
  - `scripts/governance_repo_checks.py`
  - `tests/governance/test_check_repo.py`
  - `tests/governance/test_task_continuation.py`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- The scoped continuation / repo-gate path treats legal idle with no successor as distinct from genuine blocking failure.
- Scoped regressions cover the continuation and repo-check paths without relying on the authority-alignment lane.
- This lane remains disjoint from sibling write scopes and can run in an isolated worktree under `TASK-GOV-020`.

## Rollback Plan

- Revert the continuation and repo-gate changes made by this lane.
- Restore the previous scoped tests if the new semantics destabilize the continuation path.
- Re-run the lane-specific checks to confirm pre-change behavior is restored.

## Allowed Dirs

- `docs/governance/`
- `scripts/task_continuation_ops.py`
- `scripts/governance_repo_checks.py`
- `tests/governance/test_check_repo.py`
- `tests/governance/test_task_continuation.py`

## Planned Write Paths

- `scripts/task_continuation_ops.py`
- `scripts/governance_repo_checks.py`
- `tests/governance/test_check_repo.py`
- `tests/governance/test_task_continuation.py`

## Planned Test Paths

- `tests/governance/test_check_repo.py`
- `tests/governance/test_task_continuation.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/check_repo.py`
- `pytest tests/governance/test_check_repo.py tests/governance/test_task_continuation.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
## Narrative Assertions

- `narrative_status`: `blocked`
- `closeout_state`: `not_ready`
- `blocking_state`: `blocked`
- `completed_scope`: `active_progress`
- `remaining_scope`: `blocked_work_remaining`
- `next_gate`: `blocking_resolution`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `blocked`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `blocked`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `1`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-021-idle-continuation-gates`
- `updated_at`: `2026-04-06T15:48:01+08:00`
<!-- generated:task-meta:end -->
