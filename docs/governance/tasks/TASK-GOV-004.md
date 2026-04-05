# TASK-GOV-004 治理控制面内核拆分

## Task Baseline

- `task_id`: `TASK-GOV-004`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-control-kernel-split-v1`
- `branch`: `feat/TASK-GOV-004-governance-control-kernel-split`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
## Primary Goals

- Split the governance control plane into shared state-machine, reusable rule, repo-check, and CLI orchestration layers without changing the live command surface.
- Remove the main hygiene hotspot warnings on `scripts/governance_controls.py`, `scripts/check_repo.py`, and `scripts/check_authority_alignment.py`.
- Align roadmap/business policy handling with the actual module order in `docs/governance/MODULE_MAP.yaml`, including downstream `stage7-stage9`, without claiming those stages are already implemented.

## Explicitly Not Doing

- Do not modify business implementation code under `src/`.
- Do not introduce a second control-plane ledger or a second roadmap source.
- Do not claim that `stage7-stage9` automation is production-complete; this task only removes the hard governance restriction and keeps ordering and policy consistent.

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

- none

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
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-GOV-004-governance-control-kernel-split`
- `updated_at`: `2026-04-05T11:29:09+08:00`
<!-- generated:task-meta:end -->
