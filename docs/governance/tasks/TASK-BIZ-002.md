# TASK-BIZ-002 stage7-stage9 successor generation

## Task Baseline

- `task_id`: `TASK-BIZ-002`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-stage7-9-autopilot-v1`
- `branch`: `feat/TASK-BIZ-002-stage7-9-autopilot`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Open governed successor generation for `stage7_sales`, `stage8_contact`, and `stage9_delivery` behind capability gates.
- Keep downstream generation dependent on `stage6_facts` and on upstream/downstream capability readiness instead of bypassing stage boundaries.
- Extend continuation and runner governance so downstream tasks can be created in the correct order without weakening existing hard gates.

## Explicitly Not Doing

- Do not implement `src/stage7_sales/`, `src/stage8_contact/`, or `src/stage9_delivery/` business code in this task.
- Do not allow `stage9_delivery` to start directly from `stage6_facts` without `stage7_sales` and `stage8_contact`.
- Do not alter continuation command names or add a new execution intent.

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
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-BIZ-002-stage7-9-autopilot`
- `updated_at`: `2026-04-05T19:06:16+08:00`
<!-- generated:task-meta:end -->
