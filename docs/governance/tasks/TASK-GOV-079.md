# TASK-GOV-079 console and registry projection update for concurrent executors

## Task Baseline

- `task_id`: `TASK-GOV-079`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-concurrent-executor-projection-v1`
- `branch`: `codex/TASK-GOV-079-concurrent-executor-projection`
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

- Update operator-facing projections so the control plane can display focus task, running leases, ready executors, and quarantined executors simultaneously.
- Ensure normal concurrent execution is not reported as ledger divergence by default.
- Keep the operator console aligned with the new single-ledger concurrency model.

## Explicitly Not Doing

- Do not create a second operator truth source.
- Do not change scheduler business priority or candidate ranking.
- Do not alter Stage1-Stage9 business logic or customer-visible semantics.
- Do not modify clone-local state beyond projection consumption rules.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-079.md`
- `docs/governance/runlogs/TASK-GOV-079-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-079.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/EXECUTION_LEASES.yaml`
- `docs/governance/CONCURRENT_EXECUTION_SINGLE_LEDGER_MODEL.md`
- `scripts/review_candidate_pool.py`
- `tests/governance/test_review_candidate_pool.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_review_candidate_pool.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Scope

- Update reporting and operator projections so they distinguish focus projection, running leases, ready executors, and quarantined executors.
- Ensure the console surfaces real divergence only for true conflicts such as duplicate claim, duplicate lease, runtime drift, revision conflict, or lock conflict.
- Document the concurrency model in `docs/governance/CONCURRENT_EXECUTION_SINGLE_LEDGER_MODEL.md`.

## Acceptance Criteria

- The console and candidate-pool projections can display focus task, running leases, ready executors, and quarantined executors at the same time.
- Normal concurrent executor activity is not misreported as ledger divergence.
- True ledger conflicts remain visible and auditable.
- The design document explains the concurrency model and operator decision rules.

## Rollback

- Revert projection and reporting changes.
- Keep the underlying lease model intact.
- Fall back to raw ledger inspection while operator projections are repaired.

## Risks

- Projection logic may lag behind the new ledger semantics during migration.
- Operators may still interpret focus task as the only live task until the new projection lands everywhere.
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
- `branch`: `codex/TASK-GOV-079-concurrent-executor-projection`
- `updated_at`: `2026-04-09T21:19:18+08:00`
<!-- generated:task-meta:end -->
