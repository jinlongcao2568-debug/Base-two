# TASK-GOV-076 concurrent execution lease ledger

## Task Baseline

- `task_id`: `TASK-GOV-076`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-concurrent-execution-ledger-v1`
- `branch`: `codex/TASK-GOV-076-concurrent-execution-lease-ledger`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Introduce `docs/governance/EXECUTION_LEASES.yaml` as the main-control-plane truth for concurrent executor-to-task bindings.
- Downgrade `CURRENT_TASK.yaml` from "global single live task" to "control-plane focus projection" for the active coordination task only.
- Model `control-plane-main` and `worker-01` through `worker-09` as peer executors under a single control-plane ledger.
- Keep clone-local governance ledgers and clone-local candidate caches out of the truth model.

## Explicitly Not Doing

- Do not introduce clone-local truth or a second scheduler.
- Do not change Stage1-Stage9 business logic, customer-visible semantics, or contracts.
- Do not change roadmap evaluator business ranking.
- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-076.md`
- `docs/governance/runlogs/TASK-GOV-076-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-076.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/EXECUTION_LEASES.yaml`
- `docs/governance/CONCURRENT_EXECUTION_SINGLE_LEDGER_MODEL.md`
- `scripts/control_plane_root.py`
- `scripts/task_lifecycle_ops.py`
- `scripts/task_worker_ops.py`
- `tests/governance/test_control_plane_single_ledger.py`
- `tests/governance/test_task_ops.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_control_plane_single_ledger.py -q`
- `pytest tests/governance/test_task_ops.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Scope

- Refactor governance state modeling so concurrent running executors are represented by `TASK_REGISTRY + claims + EXECUTION_LEASES + FULL_CLONE_POOL + WORKTREE_REGISTRY`.
- Keep `CURRENT_TASK.yaml` as a projection for the focus coordination task instead of the only live-task source.
- Add or update regression coverage for lease lifecycle and concurrent executor visibility.

## Acceptance Criteria

- `EXECUTION_LEASES.yaml` exists and is treated as main-control-plane truth.
- `control-plane-main` and `worker-01..09` can each hold an independent running lease without creating ledger divergence.
- The system can reconstruct concurrent executor state without promoting any clone-local governance artifact to truth.
- `CURRENT_TASK.yaml` no longer encodes the only live task in the system.

## Rollback

- Revert `EXECUTION_LEASES` introduction and its read/write code paths.
- Restore the pre-change `CURRENT_TASK` assumptions.
- Keep concurrent dispatch frozen until a replacement concurrency model is available.

## Risks

- Partial dual-write coverage may create temporary projection drift during migration.
- Hidden helper code may still assume `CURRENT_TASK` is the only live task.
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
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, tests/stage2/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `codex/TASK-GOV-076-concurrent-execution-lease-ledger`
- `updated_at`: `2026-04-09T20:52:47+08:00`
<!-- generated:task-meta:end -->
