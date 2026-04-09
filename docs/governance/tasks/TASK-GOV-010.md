# TASK-GOV-010 高吞吐多 Agent runner 与回退策略

## Task Baseline

- `task_id`: `TASK-GOV-010`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-high-throughput-runner-v1`
- `branch`: `feat/TASK-GOV-010-high-throughput-runner`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Upgrade the automation runner to enforce an effective lane budget instead of preparing every child worktree at once.
- Add governed fallback behavior for cleanup pressure and child review-bundle failures while keeping logical lane conflicts as hard-stop errors.
- Emit stable high-throughput runner metrics for lane count, lane conflicts, child closeout success, fallback count, and orphan cleanup failures.

## Explicitly Not Doing

- Do not open 5+ execution lanes in this task; the v1 safety ceiling remains 4.
- Do not change the public continuation command names or add a new execution intent.
- Do not implement stage7-stage9 business automation or modify product/runtime code under `src/`.

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
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-010-high-throughput-runner`
- `updated_at`: `2026-04-09T16:18:58+08:00`
<!-- generated:task-meta:end -->
