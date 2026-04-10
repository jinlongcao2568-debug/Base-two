# TASK-RM-STAGE3-CORE-CONTRACT Stage3 parsing contract and normalized record boundary

## Task Baseline

- `task_id`: `TASK-RM-STAGE3-CORE-CONTRACT`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `paused`
- `stage`: `stage3`
- `branch`: `codex/TASK-RM-STAGE3-CORE-CONTRACT-stage3-core-contract`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Deliver `TASK-RM-STAGE3-CORE-CONTRACT`: Stage3 parsing contract and normalized record boundary for stage `stage3`.
- Execute roadmap candidate `stage3-core-contract`.
- Implement planned write paths: src/stage3_parsing/, tests/stage3/.
- Keep required tests passing: pytest tests/stage3 -q.
- Confirm dependencies complete: stage2-core-contract.
## Explicitly Not Doing

- Do not touch reserved paths: docs/governance/, tests/integration/, docs/governance/INTERFACE_CATALOG.yaml.
- Do not modify files outside allowed dirs: src/stage3_parsing/, tests/stage3/.
- Do not expand scope outside planned write paths: src/stage3_parsing/, tests/stage3/.
## Allowed Dirs

- `src/stage3_parsing/`
- `tests/stage3/`

## Planned Write Paths

- `src/stage3_parsing/`
- `tests/stage3/`

## Planned Test Paths

- `tests/stage3/`

## Required Tests

- `pytest tests/stage3 -q`

## Reserved Paths

- `docs/governance/`
- `tests/integration/`
- `docs/governance/INTERFACE_CATALOG.yaml`
## Narrative Assertions

- `narrative_status`: `paused`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `resume_required`
## Acceptance Criteria

- Required tests pass: pytest tests/stage3 -q.
- Changes limited to planned write paths: src/stage3_parsing/, tests/stage3/.
- No open blockers remain at closeout.

## Rollback

- Revert branch `codex/TASK-RM-STAGE3-CORE-CONTRACT-stage3-core-contract` to the last known good commit if needed.
- Remove or reset generated artifacts before re-dispatching the task.

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `paused`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `docs/governance/, tests/integration/, docs/governance/INTERFACE_CATALOG.yaml`
- `branch`: `codex/TASK-RM-STAGE3-CORE-CONTRACT-stage3-core-contract`
- `updated_at`: `2026-04-10T10:27:05+08:00`
<!-- generated:task-meta:end -->
