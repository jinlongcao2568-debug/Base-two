# TASK-RM-STAGE1-SOURCE-FAMILY-CN Stage1 source-family China slice

## Task Baseline

- `task_id`: `TASK-RM-STAGE1-SOURCE-FAMILY-CN`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `done`
- `stage`: `stage1`
- `branch`: `codex/TASK-RM-STAGE1-SOURCE-FAMILY-CN-stage1-source-family-cn`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `pending`
## Primary Goals

- Add a Stage1 China source-family orchestration slice builder for `ggzy_national` raw fixtures.
- Keep the Stage1 core `ingestion_job` contract stable while exposing source-family routing metadata inside Stage1 scope.
- Add regression coverage for China-slice acceptance and boundary rejection paths within `tests/stage1/`.

## Explicitly Not Doing

- Do not change Stage2 ingestion behavior or mutate `src/stage2_ingestion/`.
- Do not introduce a second truth layer, fact surface, or downstream decision path.
- Do not change customer-visible fields, public delivery semantics, or Stage6 writeback behavior.

## Allowed Dirs

- `src/stage1_orchestration/`
- `tests/stage1/`

## Planned Write Paths

- `src/stage1_orchestration/`
- `tests/stage1/`

## Planned Test Paths

- `tests/stage1/`

## Required Tests

- `pytest tests/stage1 -q`

## Reserved Paths

- `src/stage2_ingestion/`
- `src/stage6_facts/`

## Acceptance Criteria

- Stage1 can derive a China source-family orchestration lane from a valid `ingestion_job` built from `ggzy_national` fixtures.
- The China slice rejects non-`CN-` regions and unsupported source families with deterministic Stage1 validation errors.
- `pytest tests/stage1 -q` passes without any Stage2 or Stage6 code changes.

## Rollback Plan

- Revert `src/stage1_orchestration/runtime.py`.
- Revert `tests/stage1/test_stage1_ingestion_job_runtime.py`.
- Revert this task package if the China slice is returned to backlog.
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
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `pending`
- `reserved_paths`: `src/stage2_ingestion/, src/stage6_facts/`
- `branch`: `codex/TASK-RM-STAGE1-SOURCE-FAMILY-CN-stage1-source-family-cn`
- `updated_at`: `2026-04-08T22:04:18+08:00`
<!-- generated:task-meta:end -->
