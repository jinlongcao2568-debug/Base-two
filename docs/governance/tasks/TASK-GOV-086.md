# TASK-GOV-086 Documentation entry index

## Task Baseline

- `task_id`: `TASK-GOV-086`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-docs-entry-index-v1`
- `branch`: `codex/TASK-GOV-086-docs-entry-index`
- `size_class`: `standard`
- `automation_mode`: `assisted`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Add a single documentation entry index at `docs/INDEX.md` that consolidates authority order and navigation.
- Provide a "problem -> document" table mapping common questions to the correct authoritative source.
- Add a 15-minute onboarding path and a live-vs-archive note to prevent clone-side misreads.
- Link the root `README.md` to the entry index and align wording with single-ledger execution semantics.

## Explicitly Not Doing

- Do not change governance rules, scheduler behavior, or task lifecycle logic.
- Do not modify baseline authority documents under `docs/baseline/`.
- Do not introduce new status semantics beyond existing control-plane documentation.

## Allowed Dirs

- `docs/`
- `README.md`

## Planned Write Paths

- `docs/INDEX.md`
- `README.md`

## Planned Test Paths

- none (doc-only change)

## Required Tests

- none (doc-only change)

## Reserved Paths

- `src/`
- `docs/contracts/`
- `docs/governance/`
- `db/migrations/`
- `tests/`

## Impact Modules

- documentation entry navigation
- governance onboarding clarity
- single-ledger authority visibility

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

- Create a single entry index for authority priority and document routing.
- Clarify live governance entry semantics without altering governance behavior.
- Keep changes limited to documentation and README links.

## Acceptance Criteria

- `docs/INDEX.md` exists and includes: authority priority, problem-to-document index table, 15-minute onboarding path, and live vs archive note.
- The entry index explicitly states `CURRENT_TASK.yaml` is the live focus entry while `EXECUTION_LEASES.yaml` is execution occupancy truth.
- `README.md` links to `docs/INDEX.md` and does not contradict the single-ledger execution model.

## Rollback

- Remove `docs/INDEX.md` and the README link.
- Revert README wording changes to the prior baseline.

## Risks

- Entry index can drift if authority paths or governance semantics change without updates.
- Over-simplified wording could mask the `CURRENT_TASK` vs `EXECUTION_LEASES` nuance if not maintained.
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
- `automation_mode`: `assisted`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `[]`
- `branch`: `codex/TASK-GOV-086-docs-entry-index`
- `updated_at`: `2026-04-10T09:28:19+08:00`
<!-- generated:task-meta:end -->
