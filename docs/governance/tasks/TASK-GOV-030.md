# TASK-GOV-030 治理红测修复与慢测治理

## Task Baseline

- `task_id`: `TASK-GOV-030`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-red-green-and-slow-tests-v1`
- `branch`: `feat/TASK-GOV-030-governance-red-green-slow-tests`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `5`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-030-5`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- to-be-filled

## Explicitly Not Doing

- to-be-filled

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
- `lane_count`: `5`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-030-5`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-030-governance-red-green-slow-tests`
- `updated_at`: `2026-04-07T08:37:31+08:00`
<!-- generated:task-meta:end -->
