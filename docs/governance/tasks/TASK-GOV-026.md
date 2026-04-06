# TASK-GOV-026 Lease 与 closeout 自动闭环

## Task Baseline

- `task_id`: `TASK-GOV-026`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `doing`
- `stage`: `governance-local-multi-agent-platformization-v1`
- `branch`: `feat/TASK-GOV-026-lease-closeout-closure`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `1`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Remove manual takeover knowledge from closeout-ready paths.
- Unify lease resolution for `close`, `continue-current`, `continue-roadmap`, `worker-finish`, and `auto-close-children`.
- Keep the lane strictly inside lease / continuation / lifecycle logic and its scoped regressions.

## Explicitly Not Doing

- Do not modify child execution mirror logic, worktree reconciliation, or handoff parsing.
- Do not change `automation_runner.py` or any automation tests.
- Do not touch contracts, migrations, or product-stage source code.

## Allowed Dirs

- `docs/governance/`
- `scripts/task_coordination_lease.py`
- `scripts/task_continuation_ops.py`
- `scripts/task_lifecycle_ops.py`
- `scripts/task_worker_ops.py`
- `tests/governance/test_coordination_lease.py`
- `tests/governance/test_task_continuation.py`

## Planned Write Paths

- `scripts/task_coordination_lease.py`
- `scripts/task_continuation_ops.py`
- `scripts/task_lifecycle_ops.py`
- `scripts/task_worker_ops.py`
- `tests/governance/test_coordination_lease.py`
- `tests/governance/test_task_continuation.py`

## Planned Test Paths

- `tests/governance/test_coordination_lease.py`
- `tests/governance/test_task_continuation.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/check_repo.py`
- `pytest tests/governance/test_coordination_lease.py tests/governance/test_task_continuation.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
## Narrative Assertions

- `narrative_status`: `doing`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `validation_pending`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `doing`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `1`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-026-lease-closeout-closure`
- `updated_at`: `2026-04-06T19:58:50+08:00`
<!-- generated:task-meta:end -->
