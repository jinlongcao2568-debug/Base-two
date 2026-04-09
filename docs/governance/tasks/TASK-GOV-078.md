# TASK-GOV-078 candidate pool and claim-next concurrency refactor

## Task Baseline

- `task_id`: `TASK-GOV-078`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-candidate-pool-concurrency-refactor-v1`
- `branch`: `codex/TASK-GOV-078-candidate-pool-concurrency-refactor`
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

- Refactor candidate-pool review and `claim-next` to use `TASK_REGISTRY + claims + EXECUTION_LEASES + FULL_CLONE_POOL + WORKTREE_REGISTRY`.
- Remove the assumption that a single global `CURRENT_TASK` is the occupancy source for all live work.
- Preserve strict candidate exclusivity while allowing multiple executors to run concurrently under one truth model.

## Explicitly Not Doing

- Do not change roadmap evaluator business ranking.
- Do not allow duplicate claims or duplicate execution leases.
- Do not modify business-stage logic, contracts, or customer-visible semantics.
- Do not promote clone-local state to dispatch truth.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-078.md`
- `docs/governance/runlogs/TASK-GOV-078-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-078.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/EXECUTION_LEASES.yaml`
- `scripts/control_plane_root.py`
- `scripts/review_candidate_pool.py`
- `scripts/roadmap_claim_next.py`
- `tests/governance/test_review_candidate_pool.py`
- `tests/governance/test_roadmap_claim_next.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_review_candidate_pool.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Scope

- Update candidate occupancy rules and executor availability rules to depend on claims, leases, and executor health instead of the single-live-task model.
- Update `review_candidate_pool.py` and `roadmap_claim_next.py` to report and enforce the new concurrency contract.
- Add regression tests proving multiple running executors do not create false ledger divergence and do not allow duplicate candidate assignment.

## Acceptance Criteria

- A claimed candidate cannot be reassigned while its claim or lease remains live.
- Multiple running executors do not produce false ledger divergence by themselves.
- `claim-next` still returns the correct next candidate while other executors are already running.
- `CURRENT_TASK` focus switching does not invalidate unrelated running executor state.

## Rollback

- Revert candidate-pool and claim-next concurrency logic.
- Restore the old occupancy gate.
- Freeze dispatch until concurrency occupancy semantics are corrected.

## Risks

- Old helper code may still read `CURRENT_TASK` as the only occupancy source.
- Claim and lease conflict rules must remain strict to prevent duplicate assignment.
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
- `branch`: `codex/TASK-GOV-078-candidate-pool-concurrency-refactor`
- `updated_at`: `2026-04-09T20:39:51+08:00`
<!-- generated:task-meta:end -->
