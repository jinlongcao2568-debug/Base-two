# TASK-GOV-007 动态并行规划器与 worker 池

## Task Baseline

- `task_id`: `TASK-GOV-007`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-dynamic-lane-planner-v1`
- `branch`: `feat/TASK-GOV-007-dynamic-lane-planner`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Upgrade topology and automation inference from fixed two-lane assumptions to a dynamic planner that can safely choose `1..4` execution lanes for heavy tasks.
- Replace the fixed `worker-a` / `worker-b` model with a dynamic worker pool such as `worker-01..worker-04`, and align active execution limits with the planner ceiling.
- Record lane metadata and dynamic parallelism controls in machine-readable governance files without changing business implementation code.

## Explicitly Not Doing

- Do not change business implementation code under `src/`.
- Do not change contracts, migrations, stage6 fact semantics, or customer-visible scope.
- Do not enable unlimited parallelism in this phase; the v1 implementation ceiling stays at 4 lanes.

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

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-007-dynamic-lane-planner`
- `updated_at`: `2026-04-05T19:06:16+08:00`
<!-- generated:task-meta:end -->
