# TASK-GOV-080 execution brief generation and worker onboarding

## Task Baseline

- `task_id`: `TASK-GOV-080`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-execution-brief-v1`
- `branch`: `codex/TASK-GOV-080-execution-brief`
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

- Generate an execution brief after `claim-next` promote succeeds.
- Ensure the execution brief includes `why_now`, `depends_on`, `blocked_by`, `allowed_dirs`, `reserved_paths`, `required_tests`, `executor_target`, `what_this_unlocks_next`, and `closeout_path`.
- Mirror the brief into the worker worktree at `.codex/local/EXECUTION_BRIEF.yaml` via `scripts/child_execution_flow.py`.

## Explicitly Not Doing

- Do not change candidate pool ranking or business priority.
- Do not alter Stage1-Stage9 business logic or customer-visible semantics.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/dispatch_briefs/`
- `scripts/roadmap_claim_next.py`
- `scripts/child_execution_flow.py`
- `scripts/task_worktree_ops.py`
- `scripts/roadmap_explain.py`
- `tests/governance/test_execution_brief.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_roadmap_claim_next.py -q`
- `pytest tests/governance/test_execution_brief.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Impact Modules

- governance dispatch pipeline
- execution brief artifacts
- worker onboarding context

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

- Generate execution briefs during `claim-next` promote on the control plane.
- Mirror the brief to worker worktrees without requiring extra ledger reads.
- Extend explain output with execution-brief reasoning fields.

## Acceptance Criteria

- After promote, the control plane generates a brief file containing all required fields.
- Worker worktrees can read the brief directly without additional ledger reads.
- Explain output includes `why_now` and `what_this_unlocks_next`.

## Rollback

- Remove brief generation and mirroring logic.
- Revert to the prior `claim-next` behavior.

## Risks

- Missing brief fields can still force workers to inspect ledgers manually.

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
- `branch`: `codex/TASK-GOV-080-execution-brief`
- `updated_at`: `2026-04-09T22:49:43+08:00`
<!-- generated:task-meta:end -->
