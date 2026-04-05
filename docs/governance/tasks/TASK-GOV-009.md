# TASK-GOV-009 自动化开发 runtime prompt 体系

## Task Baseline

- `task_id`: `TASK-GOV-009`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-runtime-prompt-profiles-v1`
- `branch`: `feat/TASK-GOV-009-runtime-prompt-profiles`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Turn the governed prompt modules into generated runtime prompt profiles for coordinator, worker, and reviewer roles.
- Make the runtime prompts answerable from the repository without treating app-level custom instructions as a governance source.
- Align the governance index, operator manual, and automation operating model on prompt source of truth and custom-instruction boundaries.

## Explicitly Not Doing

- Do not replace the existing prompt modules as the source of truth.
- Do not move governance rules into app-level custom instructions.
- Do not implement high-throughput runner fallback logic in this task.

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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-009-runtime-prompt-profiles`
- `updated_at`: `2026-04-05T19:06:16+08:00`
<!-- generated:task-meta:end -->
