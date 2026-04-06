# TASK-GOV-020 治理状态机闭环与 idle 语义修复

## Task Baseline

- `task_id`: `TASK-GOV-020`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-state-machine-idle-semantics-v1`
- `branch`: `feat/TASK-GOV-020-state-machine-idle-semantics`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Close the governance state-machine gap so the control plane can distinguish `idle + no_successor` from genuine continuation failure.
- Make `check_repo.py`, `check_authority_alignment.py`, and continuation readiness share the same semantics for `ready`, `no_successor`, `ambiguous`, and `blocked`.
- Remove the current authority-alignment drift where live idle state fails governance checks and the corresponding regression tests.
- Keep the repair inside governance control-plane code and regression coverage without expanding into product-stage implementation.

## Explicitly Not Doing

- Do not redesign roadmap generation, planner ranking, or successor creation strategy beyond the minimum state-semantics repair.
- Do not bundle Python environment contract cleanup, subprocess portability cleanup, or slow-test optimization into this task.
- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.
- Do not activate the new task automatically or switch the repository out of the current idle state as part of drafting this package.

## Task Intake

- `primary_objective`: close the governance state-machine loop around idle / continuation semantics.
- `not_doing`: environment-contract hardening, slow-test splitting, and subprocess portability remain follow-up work.
- `stage_scope`: governance control plane only; no business-stage logic changes.
- `impact_modules`:
  - `scripts/task_continuation_ops.py`
  - `scripts/governance_repo_checks.py`
  - `scripts/check_authority_alignment.py`
  - `tests/governance/`
  - `tests/automation/`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- `idle` with no valid successor is treated as a legal steady state by governance checks.
- `continue-roadmap` readiness exposes distinguishable outcomes for `ready`, `no_successor`, `ambiguous`, and `blocked` paths.
- `python scripts/check_repo.py` and `python scripts/check_authority_alignment.py` can both pass on the legal idle control-plane state.
- `tests/governance/test_authority_alignment.py` asserts the real failure surface rather than stale stdout expectations.
- No current-task activation occurs while drafting or closing this repair task.

## Rollback Plan

- Revert the governance scripts and regression changes introduced by this task.
- Restore the prior continuation-readiness interpretation if the new state semantics destabilize closeout or continuation flow.
- Re-run governance checks and targeted regression tests to confirm the repository returns to the pre-change behavior.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_authority_alignment.py -q`
- `pytest tests/governance/test_task_continuation.py -q`
- `pytest tests/governance -q`
- `pytest tests/automation -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
## Narrative Assertions

- `narrative_status`: `queued`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `activation_pending`

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `queued`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-020-state-machine-idle-semantics`
- `updated_at`: `2026-04-06T15:15:46+08:00`
<!-- generated:task-meta:end -->
