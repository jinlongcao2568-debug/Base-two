# TASK-OPS-008 Release closed execution worktree for TASK-RM-STAGE2-INTEGRATION-GATE

## Task Baseline

- `task_id`: `TASK-OPS-008`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-worktree-cleanup-v1`
- `branch`: `codex/TASK-OPS-008-worktree-cleanup`
- `size_class`: `micro`
- `automation_mode`: `assisted`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Deliver `TASK-OPS-008`: Release closed execution worktree for TASK-RM-STAGE2-INTEGRATION-GATE for stage `governance-worktree-cleanup-v1`.
- Implement planned write paths: docs/governance/.
- Keep required tests passing: python scripts/check_repo.py.
## Explicitly Not Doing

- Do not modify files outside allowed dirs: docs/governance/.
- Do not expand scope outside planned write paths: docs/governance/.
## Allowed Dirs

- `docs/governance/`

## Planned Write Paths

- `docs/governance/`

## Planned Test Paths

- to-be-filled

## Required Tests

- `python scripts/check_repo.py`

## Reserved Paths

- to-be-filled
## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`
## Acceptance Criteria

- Required tests pass: python scripts/check_repo.py.
- Changes limited to planned write paths: docs/governance/.
- No open blockers remain at closeout.

## Rollback

- Revert branch `codex/TASK-OPS-008-worktree-cleanup` to the last known good commit if needed.
- Remove or reset generated artifacts before re-dispatching the task.

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `micro`
- `automation_mode`: `assisted`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `[]`
- `branch`: `codex/TASK-OPS-008-worktree-cleanup`
- `updated_at`: `2026-04-10T10:28:29+08:00`
<!-- generated:task-meta:end -->
