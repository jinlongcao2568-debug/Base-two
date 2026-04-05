# TASK-GOV-007 动态并行规划器与 worker 池

## Task Baseline

- `task_id`: `TASK-GOV-007`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-dynamic-lane-planner-v1`
- `branch`: `feat/TASK-GOV-007-dynamic-lane-planner`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-007-dynamic-lane-planner`
- `updated_at`: `2026-04-05T11:48:37+08:00`
<!-- generated:task-meta:end -->
