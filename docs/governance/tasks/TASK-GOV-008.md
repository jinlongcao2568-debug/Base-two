# TASK-GOV-008 多 lane 父子聚合与 closeout 流水线

## Task Baseline

- `task_id`: `TASK-GOV-008`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `review`
- `stage`: `governance-parallel-closeout-pipeline-v1`
- `branch`: `feat/TASK-GOV-008-parallel-closeout-pipeline`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Turn the existing child auto-close path into a stable parent/child closeout pipeline with explicit `review_bundle_status` lifecycle semantics.
- Keep parent aggregation derived from child task state in the live registry instead of introducing a second persisted rollup surface.
- Ensure top-level parent closeout still happens only through the existing continuation and formal closeout commands.

## Explicitly Not Doing

- Do not change business implementation code under `src/`.
- Do not change contracts, migrations, stage6 fact semantics, or customer-visible scope.
- Do not implement runtime prompt profiles or high-throughput runner fallback work in this task.

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

- `narrative_status`: `review`
- `closeout_state`: `candidate_ready`
- `blocking_state`: `clear`
- `completed_scope`: `ready_for_review`
- `remaining_scope`: `closeout_only`
- `next_gate`: `closeout_decision`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `review`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-008-parallel-closeout-pipeline`
- `updated_at`: `2026-04-05T13:43:52+08:00`
<!-- generated:task-meta:end -->
