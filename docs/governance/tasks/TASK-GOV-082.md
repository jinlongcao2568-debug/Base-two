# TASK-GOV-082 runtime rollout closed loop

## Task Baseline

- `task_id`: `TASK-GOV-082`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-runtime-rollout-loop-v1`
- `branch`: `codex/TASK-GOV-082-runtime-rollout-loop`
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

- Mark `rollout_pending` after governance runtime changes.
- On closeout or publish, trigger `refresh-full-clone-pool` then `audit-full-clone-pool` before unblocking dispatch.
- When dispatch is blocked, provide explicit remediation instructions for runtime rollout.

## Explicitly Not Doing

- Do not alter the runtime hash or drift detection logic.
- Do not change candidate scoring logic.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `scripts/control_plane_root.py`
- `scripts/full_clone_pool.py`
- `scripts/task_runtime_ops.py`
- `scripts/review_candidate_pool.py`
- `docs/governance/CONTROL_PLANE_FULL_CLONE_RUNTIME_HARDENING_EXECUTION_PLAN_V2.md`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_review_candidate_pool.py -q`
- `pytest tests/governance/test_full_clone_pool.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Impact Modules

- runtime rollout gating
- clone pool refresh and audit
- dispatch readiness enforcement

## Interface Changes

- `interface_change`: `no`

## Schema Migration

- `schema_migration`: `no`

## Exception Approval

- `exception_approval`: `no`

## Stage6 Facts Impact

- `stage6_facts_impact`: `no`

## Customer Commitment Impact

- `customer_commitment_impact`: `no`

## Coverage Impact

- `coverage_impact`: `no`

## Personal Info Impact

- `personal_info_impact`: `no`

## Scope

- Track runtime rollout state and block dispatch until refresh and audit complete.
- Automate refresh and audit after runtime changes during closeout or publish.
- Surface clear remediation guidance when runtime rollout is pending.

## Acceptance Criteria

- Runtime changes block dispatch until refresh and audit complete.
- Successful refresh automatically unblocks dispatch without manual ledger edits.

## Rollback

- Remove rollout pending tracking and the automatic refresh chain.
- Return to manual refresh and audit procedures.

## Risks

- Refresh failures will block dispatch until resolved with explicit instructions.

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
- `branch`: `codex/TASK-GOV-082-runtime-rollout-loop`
- `updated_at`: `2026-04-09T22:49:43+08:00`
<!-- generated:task-meta:end -->
