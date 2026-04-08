# TASK-GOV-051 Expand worker capacity from 4 to 9

## Task Baseline

- `task_id`: `TASK-GOV-051`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-worker-capacity-nine-v1`
- `branch`: `codex/TASK-GOV-051-worker-capacity-seven`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Expand the governed worker capacity ceiling from 4 to 9.
- Add worker-05 through worker-09 to both clone and worktree pool registries.
- Ensure existing dispatch, prewarm, and self-loop logic accepts worker-01..09.
- Provision the new clone and worktree slot directories on disk.

## Explicitly Not Doing

- Do not alter the candidate DAG or business logic under `src/`.
- Do not change current task routing rules beyond allowing a larger pool.

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

- `pytest tests/governance/test_worker_capacity_nine.py -q`
- `pytest tests/governance/test_full_clone_pool.py -q`
- `pytest tests/governance/test_worktree_pool_dispatch.py -q`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `README.md`
- `tests/contracts/`
- `tests/integration/`
- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
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
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-051-worker-capacity-seven`
- `updated_at`: `2026-04-08T10:03:23+08:00`
<!-- generated:task-meta:end -->
