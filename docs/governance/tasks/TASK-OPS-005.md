# TASK-OPS-005 full-clone parity restoration and dispatch re-enable for worker-02..09

## Task Baseline

- `task_id`: `TASK-OPS-005`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-full-clone-parity-restoration-v1`
- `branch`: `codex/TASK-OPS-005-full-clone-parity-restoration`
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

- Refresh or rebuild `worker-02` through `worker-09` until their published governance runtime matches the main control plane and the slots return to `ready` parity.
- Re-run full-clone audit and candidate-pool review from the main control plane, proving that dispatch can resume without touching `worker-01` preserve handling.
- Validate the restored pool by running a dry-run `claim-next` from the main control plane after parity is back within policy.

## Explicitly Not Doing

- Do not salvage, rebuild, or otherwise modify `worker-01`; that slot remains preserve-before-rebuild outside this task scope.
- Do not change governance runtime semantics, preserve guards, or candidate-pool rules; those were completed in `TASK-GOV-073` through `TASK-GOV-075`.
- Do not modify Stage1-Stage9 business logic, customer-visible contracts, migrations, or clone-local governance mirrors.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-OPS-005.md`
- `docs/governance/runlogs/TASK-OPS-005-RUNLOG.md`
- `docs/governance/handoffs/TASK-OPS-005.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/FULL_CLONE_POOL.yaml`

## Planned Test Paths

- `tests/governance/`

## Required Tests

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
- `branch`: `codex/TASK-OPS-005-full-clone-parity-restoration`
- `updated_at`: `2026-04-09T19:56:12+08:00`
<!-- generated:task-meta:end -->
