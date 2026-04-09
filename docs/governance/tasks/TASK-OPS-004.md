# TASK-OPS-004 worker-01 Stage2 salvage continuation and preserve-slot preconditions

## Task Baseline

- `task_id`: `TASK-OPS-004`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-worker-01-salvage-continuation-v1`
- `branch`: `codex/TASK-OPS-004-worker-01-salvage-continuation`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Verify that the preserved `worker-01` Stage2 implementation is already committed and that the branch can be named, audited, and retained from the main control plane.
- Record the branch disposition for `codex/TASK-RM-STAGE2-CORE-CONTRACT-stage2-core-contract` and attach it to a governed continuation path instead of leaving the preserve slot with an unnamed local-only recovery state.
- Leave `worker-01` in a recoverable preserve-first state with explicit rebuild preconditions recorded, without reopening Stage2 implementation work inside this task.

## Explicitly Not Doing

- Do not modify `src/stage2_ingestion/`, `tests/stage2/`, contracts, migrations, or any Stage1-Stage9 business logic.
- Do not absorb clone-local `docs/governance/*.yaml`, clone-local candidate caches, or clone-local closeout state into the control-plane truth.
- Do not rebuild or unlock `worker-01`, and do not refresh or rebuild `worker-02` through `worker-09` in this task.

## Allowed Dirs

- `docs/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-OPS-004.md`
- `docs/governance/runlogs/TASK-OPS-004-RUNLOG.md`
- `docs/governance/handoffs/TASK-OPS-004.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/FULL_CLONE_POOL.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`

## Planned Test Paths

- `docs/governance/`

## Required Tests

- `python scripts/task_ops.py audit-full-clone-pool --slot-id worker-01`
- `python scripts/review_candidate_pool.py`

## Reserved Paths

- `src/`
- `tests/stage2/`
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
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, tests/stage2/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `codex/TASK-OPS-004-worker-01-salvage-continuation`
- `updated_at`: `2026-04-09T19:00:47+08:00`
<!-- generated:task-meta:end -->
