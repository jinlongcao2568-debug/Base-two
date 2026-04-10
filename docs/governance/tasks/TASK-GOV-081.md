# TASK-GOV-081 task package completeness gate

## Task Baseline

- `task_id`: `TASK-GOV-081`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-task-package-completeness-v1`
- `branch`: `codex/TASK-GOV-081-task-package-completeness`
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

- Enforce task package completeness before activate or promote.
- Require `Primary Goals`, `Explicitly Not Doing`, `Allowed Dirs`, `Required Tests`, `Acceptance Criteria`, and `Rollback`.
- Provide a read-only audit command to list historical incomplete task packages.

## Explicitly Not Doing

- Do not change the task template section layout.
- Do not modify business logic or candidate ranking.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `scripts/governance_markdown.py`
- `scripts/task_lifecycle_ops.py`
- `scripts/roadmap_claim_next.py`
- `scripts/task_runtime_ops.py`
- `tests/governance/test_task_package_completeness.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_task_ops.py -q`
- `pytest tests/governance/test_task_package_completeness.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Impact Modules

- task package validation
- task lifecycle activation gates
- governance audit tooling

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

- Block activate or promote for incomplete task packages with explicit missing fields.
- Add an audit command that reports historical incomplete task packages without mutating them.

## Acceptance Criteria

- Activate or promote blocks incomplete task packages and reports missing fields.
- Audit command lists incomplete task packages for follow-up.

## Rollback

- Remove the completeness gate and keep a warning-only check.

## Risks

- Historical task packages may be blocked and require remediation or exceptions.

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
- `branch`: `codex/TASK-GOV-081-task-package-completeness`
- `updated_at`: `2026-04-10T08:31:12+08:00`
<!-- generated:task-meta:end -->
