# TASK-GOV-004 治理控制面内核拆分

## Task Baseline

- `task_id`: `TASK-GOV-004`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-control-kernel-split-v1`
- `branch`: `feat/TASK-GOV-004-governance-control-kernel-split`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
## Primary Goals

- to-be-filled

## Explicitly Not Doing

- to-be-filled

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

- to-be-filled
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
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-GOV-004-governance-control-kernel-split`
- `updated_at`: `2026-04-05T08:29:27+08:00`
<!-- generated:task-meta:end -->
