# TASK-GOV-030 治理红测修复与慢测治理

## Task Baseline

- `task_id`: `TASK-GOV-030`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `review`
- `stage`: `governance-red-green-and-slow-tests-v1`
- `branch`: `feat/TASK-GOV-030-governance-red-green-slow-tests`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
- `lane_count`: `5`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-030-5`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Restore the governance control-plane test chain to green by fixing the child execution prepare regression and the publish-flow fixture drift.
- Reduce local feedback time for the governance and automation suites by removing avoidable repo/bootstrap overhead before touching broader behavior.
- Keep the fix scoped to governance scripts, governance/automation tests, and operator-facing docs without changing stage1-stage9 business semantics.

## Explicitly Not Doing

- Do not modify `src/stage1_orchestration/` through `src/stage9_delivery/` business logic or contract semantics in this task.
- Do not expand the publish feature set, add new automation capabilities, or change roadmap successor policy beyond what is required to restore existing tests.
- Do not touch `docs/contracts/`, `db/migrations/`, or `tests/integration/`.

## Acceptance Targets

- `pytest tests/governance/test_task_gov_018.py::test_stage7_scope_uses_governed_child_workflow -q` passes.
- `pytest tests/governance/test_task_publish_ops.py -q` passes.
- `pytest tests/governance -q` passes.
- `pytest tests/automation -q` remains green and completes faster than the current 2m33s baseline.
- `python scripts/check_repo.py`, `python scripts/check_hygiene.py src scripts tests`, and `python scripts/check_authority_alignment.py` remain green after the repair.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `README.md`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `README.md`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src scripts tests`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_task_gov_018.py::test_stage7_scope_uses_governed_child_workflow -q`
- `pytest tests/governance/test_task_publish_ops.py -q`
- `pytest tests/automation -q`
- `pytest tests/governance -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
## Narrative Assertions

- `narrative_status`: `review`
- `closeout_state`: `candidate_ready`
- `blocking_state`: `clear`
- `completed_scope`: `ready_for_review`
- `remaining_scope`: `closeout_only`
- `next_gate`: `closeout_decision`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `review`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
- `lane_count`: `5`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-030-5`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-030-governance-red-green-slow-tests`
- `updated_at`: `2026-04-07T08:56:59+08:00`
<!-- generated:task-meta:end -->
