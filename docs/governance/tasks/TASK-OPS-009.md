# TASK-OPS-009 Harden full-clone slot release and worker state transitions

## Task Baseline

- `task_id`: `TASK-OPS-009`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `paused`
- `stage`: `governance-full-clone-slot-release-hardening-v1`
- `branch`: `codex/TASK-OPS-009-full-clone-slot-release-hardening`
- `size_class`: `standard`
- `automation_mode`: `assisted`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Prevent full-clone worker slots from being marked `ready` before the real clone runtime has been explicitly released.
- Make `worker-start` reject terminal tasks and synchronize full-clone slot state when a governed worker starts.
- Add one explicit slot-release path that transitions full-clone workers through `releasing` before they can return to `ready`.
- Keep candidate selection and claim-next ranking semantics unchanged while removing slot-readiness dependence on idle-branch inspection.

## Explicitly Not Doing

- Do not change roadmap candidate ranking, claim-next selection order, or executor fairness semantics.
- Do not modify business-stage source code under `src/stage1_*` through `src/stage9_*`.
- Do not add database migrations, customer-visible field changes, or contract/version changes.
- Do not introduce a second scheduler or a second ledger outside the governed control-plane files and scripts.

## Allowed Dirs

- `scripts/`
- `tests/`
- `docs/governance/`

## Planned Write Paths

- `scripts/`
- `tests/governance/`
- `docs/governance/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_worker_self_loop.py -q`
- `pytest tests/governance/test_full_clone_pool.py -q`
- `python scripts/check_repo.py`

## Reserved Paths

- `src/`
- `db/migrations/`
- `docs/contracts/`
- `docs/governance/exceptions/`
## Narrative Assertions

- `narrative_status`: `paused`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `resume_required`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `paused`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `assisted`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `[]`
- `branch`: `codex/TASK-OPS-009-full-clone-slot-release-hardening`
- `updated_at`: `2026-04-10T14:15:52+08:00`
<!-- generated:task-meta:end -->

## Acceptance Criteria

- Required tests pass: pytest tests/governance/test_worker_self_loop.py -q, pytest tests/governance/test_full_clone_pool.py -q, python scripts/check_repo.py.
- Changes limited to planned write paths: scripts/, tests/governance/, docs/governance/.
- No open blockers remain at closeout.

## Rollback

- Revert branch `codex/TASK-OPS-009-full-clone-slot-release-hardening` to the last known good commit if needed.
- Remove or reset generated artifacts before re-dispatching the task.
