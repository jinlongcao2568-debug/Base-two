# TASK-OPS-002 worker-01 preserved full-clone recovery

## Task Baseline

- `task_id`: `TASK-OPS-002`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `full-clone-worker01-manual-recovery-v1`
- `branch`: `feat/TASK-OPS-002-worker01-recovery`
- `size_class`: `micro`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Preserve the latest committed `worker-01` local implementation before any rebuild so the manual recovery branch is not lost.
- Restore `worker-01` from `preserve-before-rebuild` to a standard ready idle full-clone slot aligned with the control-plane runtime.
- Verify `worker-01` matches `worker-02` through `worker-09` for full-clone pool readiness and clone-cwd `claim-next` behavior.

## Explicitly Not Doing

- Do not modify Stage1 business logic or merge the preserved worker-01 implementation branch in this task.
- Do not rewrite other full-clone slots beyond the minimum audit needed to confirm pool parity.
- Do not change roadmap candidate evaluation, contracts, database migrations, or customer-visible behavior.

## Allowed Dirs

- `docs/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-OPS-002.md`
- `docs/governance/runlogs/TASK-OPS-002-RUNLOG.md`
- `docs/governance/handoffs/TASK-OPS-002.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/FULL_CLONE_POOL.yaml`

## Planned Test Paths

- `docs/governance/`

## Required Tests

- `python scripts/task_ops.py audit-full-clone-pool`

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
- `size_class`: `micro`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/`
- `branch`: `feat/TASK-OPS-002-worker01-recovery`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
