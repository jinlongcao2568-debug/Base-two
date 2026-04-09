# TASK-GOV-077 control-plane transactional write lock and revision guard

## Task Baseline

- `task_id`: `TASK-GOV-077`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-transactional-write-lock-v1`
- `branch`: `codex/TASK-GOV-077-write-lock-and-revision-guard`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Add control-plane write locking so concurrent governance writes from multiple windows cannot overlap unsafely.
- Add revision/version guards to governance writers so stale writers fail fast instead of silently overwriting state.
- Make related governance writes transactional and atomic across the affected ledgers.

## Explicitly Not Doing

- Do not alter business scheduling priority or roadmap ranking.
- Do not relax single truth source rules.
- Do not repair clone-local ledgers in place.
- Do not modify Stage1-Stage9 business logic or customer-visible semantics.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-077.md`
- `docs/governance/runlogs/TASK-GOV-077-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-077.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/EXECUTION_LEASES.yaml`
- `scripts/control_plane_root.py`
- `scripts/task_lifecycle_ops.py`
- `scripts/task_worker_ops.py`
- `scripts/task_runtime_ops.py`
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

- Harden control-plane write flows for `activate`, `worker-start`, `worker-finish`, `pause`, `close`, `claim-next`, and related lease / registry updates.
- Ensure each governance write path acquires a lock, re-reads state under lock, validates revisions, and writes atomically.
- Surface conflicts as explicit governance failures rather than silent ledger drift.

## Acceptance Criteria

- Two windows cannot silently overwrite the same governance state.
- One writer wins; conflicting writers receive explicit conflict errors such as revision mismatch or lease conflict.
- Task, lease, and focus projection state do not end up half-synchronized after failed concurrent writes.
- The new write guard applies to all relevant governance write entrypoints in scope.

## Rollback

- Revert write-lock and revision-guard logic.
- Return to serialized manual governance operations.
- Keep multi-window dispatch disabled until concurrency writes are rehardened.

## Risks

- Missing even one governance write path will leave a concurrency hole.
- Lock cleanup and stale-lock handling must be conservative to avoid dead sessions blocking progress.
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
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, tests/stage2/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `codex/TASK-GOV-077-write-lock-and-revision-guard`
- `updated_at`: `2026-04-09T20:39:40+08:00`
<!-- generated:task-meta:end -->
