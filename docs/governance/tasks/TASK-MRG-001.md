# TASK-MRG-001 主线收口 Git 发布能力

## Task Baseline

- `task_id`: `TASK-MRG-001`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-git-publish-mainline-v1`
- `branch`: `feat/TASK-MRG-001-promote-git-publish-mainline`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Promote the governed Git publish controls from the main reintegration source into the main AX9 repository baseline.
- Preserve the existing `TASK-GOV-014` orchestration and runtime foundations while adding explicit `commit`, `push`, `create draft PR`, and end-to-end publish entrypoints.
- Keep the main repository governance ledgers clean so the publish capability becomes a first-class mainline capability instead of an external clone-only feature.

## Explicitly Not Doing

- Do not import `TASK-GIT-001` or `TASK-GIT-002` handoffs, runlogs, task packages, or closeout metadata into the main repository baseline.
- Do not change `src/`, contracts, migrations, integration tests, or any stage1-stage9 business implementation in this task.
- Do not make Git publishing implicit in continuation, runner, or closeout flows; the publish controls remain explicit operator-triggered actions.

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
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-MRG-001-promote-git-publish-mainline`
- `updated_at`: `2026-04-06T14:12:09+08:00`
<!-- generated:task-meta:end -->
