# TASK-OPS-001 Git publish readiness

## Task Baseline

- `task_id`: `TASK-OPS-001`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-git-publish-readiness-v1`
- `branch`: `feat/TASK-OPS-001-publish-readiness`
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

- Add a governed `publish_readiness` block to `orchestration-status` so operators can see whether the live task can be committed, pushed, or opened as a draft PR.
- Keep Git publishing explicit-only while making publish blockers visible through the runtime status surface and operator documentation.
- Queue the next 9.5+ phase task packages so the control plane does not fall back to an idle planning gap after this task closes.

## Explicitly Not Doing

- Do not make Git publish actions run automatically from continuation, runner, or closeout flows.
- Do not implement `stage7-stage9` business automation in this task; only queue the downstream task packages.
- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/` in this task.

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
- `branch`: `feat/TASK-OPS-001-publish-readiness`
- `updated_at`: `2026-04-09T17:48:10+08:00`
<!-- generated:task-meta:end -->
