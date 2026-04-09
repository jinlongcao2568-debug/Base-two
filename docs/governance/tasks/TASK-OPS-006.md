# TASK-OPS-006 worker-01 slot recovery after preserve salvage

## Task Baseline

- `task_id`: `TASK-OPS-006`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-worker-slot-recovery-v1`
- `branch`: `codex/TASK-OPS-006-worker-01-slot-recovery`
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

- Preserve any non-governance worker-02 clone changes caused by the accidental Stage3 dispatch so the slot can be returned to a healthy idle state without losing implementation work.
- Clear the `worker-01` preserve-first blocker after confirming the Stage2 salvage branch already exists in the main control plane, then rebuild the slot back to its idle branch.
- Re-run full-clone audit, candidate-pool review, and dry-run dispatch from the main control plane until `worker-01` is healthy and the pool remains dispatchable.

## Explicitly Not Doing

- Do not absorb clone-local `docs/governance/*.yaml`, clone-local candidate caches, or clone-local closeout/runtime state into the main control-plane truth.
- Do not change Stage1-Stage9 business logic, contracts, database migrations, or customer-visible behavior.
- Do not continue Stage2 or Stage3 implementation inside this task; only preserve branch/patch state needed to restore slot health.

## Allowed Dirs

- `docs/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-OPS-006.md`
- `docs/governance/runlogs/TASK-OPS-006-RUNLOG.md`
- `docs/governance/handoffs/TASK-OPS-006.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/FULL_CLONE_POOL.yaml`
- `docs/governance/runlogs/TASK-OPS-006-worker-02-stage3-salvage.patch`

## Planned Test Paths

- `docs/governance/`

## Required Tests

- `python scripts/task_ops.py audit-full-clone-pool --slot-id worker-01`
- `python scripts/task_ops.py audit-full-clone-pool`
- `python scripts/review_candidate_pool.py`
- `python scripts/task_ops.py claim-next --now 2026-04-09T19:00:00+08:00`

## Reserved Paths

- `src/`
- `tests/stage2/`
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
- `successor_state`: `backlog`
- `reserved_paths`: `src/, tests/stage2/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `codex/TASK-OPS-006-worker-01-slot-recovery`
- `updated_at`: `2026-04-09T20:27:50+08:00`
<!-- generated:task-meta:end -->
