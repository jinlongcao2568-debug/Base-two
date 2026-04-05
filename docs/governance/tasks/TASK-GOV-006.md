# TASK-GOV-006 自动关账与续跑判定升级

## Task Baseline

- `task_id`: `TASK-GOV-006`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-closeout-autopilot-v2`
- `branch`: `feat/TASK-GOV-006-closeout-autopilot-v2`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
## Primary Goals

- Add a read-only closeout eligibility judge that explains whether the live top-level coordination task can auto-close.
- Upgrade roadmap continuation so closeout depends on task status, required test coverage, runlog evidence, clean worktree, and ledger consistency together.
- Expose explicit closeout recommendations and ledger-drift blockers through the automation intent preflight path without adding any new execution intent.

## Explicitly Not Doing

- Do not change business implementation code under `src/`.
- Do not change contracts, migrations, stage6 fact semantics, or customer-visible scope.
- Do not add any third execution intent beyond `continue-current` and `continue-roadmap`.

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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-006-closeout-autopilot-v2`
- `updated_at`: `2026-04-05T11:29:09+08:00`
<!-- generated:task-meta:end -->
