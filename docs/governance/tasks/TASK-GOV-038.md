# TASK-GOV-038 Modular roadmap scheduler design

## Task Baseline

- `task_id`: `TASK-GOV-038`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-modular-roadmap-scheduler-design-v1`
- `branch`: `codex/TASK-GOV-038-modular-roadmap-scheduler-design`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Freeze the modular roadmap scheduler design for multi-window Codex execution.
- Define how stages 1-9 split into parent routes, child lanes, and integration gates.
- Define the machine-readable roadmap backlog and candidate schema needed by future `claim-next` work.
- Define hard conflict gates for ledgers, runlogs, branches, worktrees, dirty state, publish, PR creation, and stale takeover.
- Split the implementation into follow-up governance tasks so later work does not drift.

## Explicitly Not Doing

- Do not implement `claim-next` or change automation runner behavior in this task.
- Do not change business code under `src/`.
- Do not change contracts, database migrations, customer-visible field lists, region/source coverage, or `stage6_facts` runtime semantics.
- Do not increase customer-visible commitments or add customer-visible personal information fields.
- Do not make historical or absorbed tasks selectable again.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`

## Planned Test Paths

- `docs/governance/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `README.md`
- `tests/contracts/`
- `tests/integration/`
- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
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
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-038-modular-roadmap-scheduler-design`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
