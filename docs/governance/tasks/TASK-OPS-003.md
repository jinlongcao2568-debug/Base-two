# TASK-OPS-003 governance ledger residual cleanup and preserve-first recovery SOP

## Task Baseline

- `task_id`: `TASK-OPS-003`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-ledger-residual-cleanup-v1`
- `branch`: `feat/TASK-OPS-003-ledger-residual-cleanup`
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

- Remove the preserved `worker-01` salvage branch tail from the main control plane after the operator explicitly decided to discard it.
- Normalize `TASK-BIZ-002` and `TASK-BIZ-003` from absorbed backlog placeholders into absorbed-and-closed ledger entries so they stop appearing as queued or paused residual work.
- Publish a permanent preserve-first full-clone recovery SOP under `docs/governance/` so future slot recovery follows one governed operator path.

## Explicitly Not Doing

- Do not modify `src/`, Stage1-Stage9 business logic, contracts, database migrations, or customer-visible delivery semantics.
- Do not reopen `TASK-BIZ-002` or `TASK-BIZ-003` as standalone execution work; they remain historically absorbed by `TASK-GOV-018`.
- Do not alter candidate-pool scheduling rules or full-clone dispatch semantics beyond documenting the existing recovery procedure.

## Allowed Dirs

- `docs/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-OPS-003.md`
- `docs/governance/runlogs/TASK-OPS-003-RUNLOG.md`
- `docs/governance/handoffs/TASK-OPS-003.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/tasks/TASK-BIZ-002.md`
- `docs/governance/tasks/TASK-BIZ-003.md`
- `docs/governance/runlogs/TASK-BIZ-002-RUNLOG.md`
- `docs/governance/runlogs/TASK-BIZ-003-RUNLOG.md`
- `docs/governance/handoffs/TASK-BIZ-002.yaml`
- `docs/governance/handoffs/TASK-BIZ-003.yaml`
- `docs/governance/PRESERVE_FIRST_FULL_CLONE_RECOVERY_SOP.md`

## Planned Test Paths

- `docs/governance/`

## Required Tests

- `python scripts/task_ops.py audit-full-clone-pool`
- `python scripts/check_repo.py`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/`
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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/`
- `branch`: `feat/TASK-OPS-003-ledger-residual-cleanup`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
