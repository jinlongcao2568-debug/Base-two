# TASK-BIZ-001 stage7-stage9 下游契约与测试骨架

## Task Baseline

- `task_id`: `TASK-BIZ-001`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `business-stage7-9-contracts-v1`
- `branch`: `feat/TASK-BIZ-001-stage7-9-contracts`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Define the formal downstream contracts for `stage7_sales_context`, `stage8_contact_context`, and `stage9_customer_delivery`.
- Add the minimum fixtures, contract checks, and stage test skeletons needed to make downstream business automation auditable before implementation opens.
- Keep `stage6_facts` as the only unified fact layer while documenting how stage7-stage9 consume its outputs.

## Explicitly Not Doing

- Do not implement runtime business logic under `src/` in this task.
- Do not declare `stage7_to_stage9_business_automation` established in this task.
- Do not introduce a second fact layer, second truth layer, or stage6 write-back path.

## Allowed Dirs

- `docs/governance/`
- `docs/contracts/`
- `tests/contracts/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/integration/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/`
- `docs/contracts/`
- `tests/contracts/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/integration/`
- `tests/governance/`

## Planned Test Paths

- `tests/contracts/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/integration/`
- `tests/governance/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `python scripts/check_authority_alignment.py`
- `python scripts/validate_contracts.py`
- `pytest tests/contracts -q`
- `pytest tests/stage7 -q`
- `pytest tests/stage8 -q`
- `pytest tests/stage9 -q`
- `pytest tests/integration -q`
- `pytest tests/governance -q`

## Reserved Paths

- `src/`
- `db/migrations/`
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
- `reserved_paths`: `src/, db/migrations/`
- `branch`: `feat/TASK-BIZ-001-stage7-9-contracts`
- `updated_at`: `2026-04-05T19:06:16+08:00`
<!-- generated:task-meta:end -->
