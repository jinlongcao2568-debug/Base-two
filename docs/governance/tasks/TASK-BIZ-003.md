# TASK-BIZ-003 stage7-stage9 最小闭环

## Task Baseline

- `task_id`: `TASK-BIZ-003`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `business-stage7-9-smoke-v1`
- `branch`: `feat/TASK-BIZ-003-stage7-9-smoke`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Deliver the minimum runnable downstream implementation for `stage7_sales`, `stage8_contact`, and `stage9_delivery`.
- Prove the smallest `stage6 -> stage7/8 -> stage9` chain through integration smoke while preserving the stage6 fact boundary.
- Promote `stage7_to_stage9_business_automation` to `implemented` only after the downstream smoke path and governance gates pass.

## Explicitly Not Doing

- Do not rewrite or override `src/stage6_facts/`.
- Do not expand beyond the minimum downstream contexts and customer delivery result needed for the smoke chain.
- Do not weaken customer-delivery whitelist, blacklist, disclaimer, or outbound approval constraints.

## Allowed Dirs

- `docs/governance/`
- `docs/contracts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/contracts/`
- `tests/integration/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`
- `docs/contracts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/contracts/`
- `tests/integration/`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/contracts/`
- `tests/integration/`
- `tests/governance/`
- `tests/automation/`

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
- `pytest tests/automation -q`

## Reserved Paths

- `src/stage6_facts/`
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
- `successor_state`: `backlog`
- `reserved_paths`: `src/stage6_facts/, db/migrations/`
- `branch`: `feat/TASK-BIZ-003-stage7-9-smoke`
- `updated_at`: `2026-04-05T21:52:29+08:00`
<!-- generated:task-meta:end -->
