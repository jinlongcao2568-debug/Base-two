# TASK-GOV-011 正式交接摘要与跨窗口恢复包

## Task Baseline

- `task_id`: `TASK-GOV-011`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-handoff-recovery-v1`
- `branch`: `feat/TASK-GOV-011-handoff-recovery`
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

- Add a governed handoff policy and a durable handoff artifact for each top-level coordination task.
- Persist completed work, remaining work, next step, next tests, risks, and candidate paths outside the chat window.
- Make continue-current and automation intent preflight restore the formal recovery pack before deciding the next action.

## Explicitly Not Doing

- Do not add single-writer lease, handoff/release/takeover, or takeover auditing in this task.
- Do not add planner-driven task package generation or candidate promotion in this task.
- Do not modify product code under `src/`, contracts, migrations, or integration business-chain paths.

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
- `branch`: `feat/TASK-GOV-011-handoff-recovery`
- `updated_at`: `2026-04-09T12:08:35+08:00`
<!-- generated:task-meta:end -->
