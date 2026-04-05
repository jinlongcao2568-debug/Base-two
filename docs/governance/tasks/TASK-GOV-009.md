# TASK-GOV-009 自动化开发 runtime prompt 体系

## Task Baseline

- `task_id`: `TASK-GOV-009`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-runtime-prompt-profiles-v1`
- `branch`: `feat/TASK-GOV-009-runtime-prompt-profiles`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
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
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-009-runtime-prompt-profiles`
- `updated_at`: `2026-04-05T13:45:43+08:00`
<!-- generated:task-meta:end -->
