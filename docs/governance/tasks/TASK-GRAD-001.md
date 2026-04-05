# TASK-GRAD-001 heavy 默认策略毕业到受控自动化

## Task Baseline

- `task_id`: `TASK-GRAD-001`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-heavy-autonomy-graduation-v1`
- `branch`: `feat/TASK-GRAD-001-autonomy-graduation`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Graduate heavy-task default automation from `manual` to governed `assisted` once the soak thresholds and publish readiness gates are proven.
- Encode the autonomous entry gate so heavy tasks only become `autonomous` when planner, tests, publish readiness, lane conflict, and graduation capability checks all pass.
- Record the final policy and capability updates that define the `9.5+` default operating mode.

## Explicitly Not Doing

- Do not open `5+` lanes.
- Do not introduce silent auto-publish.
- Do not enable `autonomous` heavy execution when the graduation gate is not fully satisfied.

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
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GRAD-001-autonomy-graduation`
- `updated_at`: `2026-04-05T20:28:55+08:00`
<!-- generated:task-meta:end -->
