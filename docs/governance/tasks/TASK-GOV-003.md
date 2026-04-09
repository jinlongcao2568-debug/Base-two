# TASK-GOV-003 任务生命周期闭环补齐

## Task Baseline

- `task_id`: `TASK-GOV-003`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-task-lifecycle-closure-v1`
- `branch`: `feat/TASK-GOV-003-governance-task-lifecycle-closure`
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

- Introduce a formal idle current-task state so closeout no longer leaves the control plane red when no successor is immediately active.
- Make `close`, `continue-roadmap`, and the live repo gates treat `review -> done -> idle -> successor` as a valid lifecycle.
- Prove the lifecycle with governance and automation rehearsal tests that cover idle recovery and successor activation.

## Explicitly Not Doing

- Do not change contracts, business-stage implementation code, or `stage7-stage9` automation policy.
- Do not introduce a second task ledger, second roadmap source, or a relaxed rule that allows `done` tasks to remain live current tasks.
- Do not auto-activate a successor during closeout unless an explicit continuation command requests it.

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

- `python scripts/check_authority_alignment.py`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `pytest tests/governance -q`
- `pytest tests/automation -q`
- `pytest tests/contracts -q`
- `pytest tests/integration -q`
- `pytest -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
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
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-GOV-003-governance-task-lifecycle-closure`
- `updated_at`: `2026-04-09T16:18:58+08:00`
<!-- generated:task-meta:end -->
