# TASK-GOV-028 Runner 与本地多 agent 编排收口

## Task Baseline

- `task_id`: `TASK-GOV-028`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `queued`
- `stage`: `governance-local-multi-agent-platformization-v1`
- `branch`: `feat/TASK-GOV-028-runner-local-platformization`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `3`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Align local runner behavior with the stabilized lease and child-closeout semantics from the first-wave lanes.
- Ensure automation runtime tests observe idle/no-successor and missing-worktree reconciliation as success states, not false failures.
- Keep the lane limited to `automation_runner.py` and automation tests.

## Explicitly Not Doing

- Do not change lease semantics directly.
- Do not change child mirror or handoff parsing directly.
- Do not touch contracts, migrations, product-stage source code, or governance tests.

## Allowed Dirs

- `docs/governance/`
- `scripts/automation_runner.py`
- `tests/automation/`

## Planned Write Paths

- `scripts/automation_runner.py`
- `tests/automation/`

## Planned Test Paths

- `tests/automation/test_automation_runner.py`
- `tests/automation/test_high_throughput_runner.py`
- `tests/automation/test_orchestration_runtime_runner.py`
- `tests/automation/test_task_gov_017_runtime.py`
- `tests/automation/test_task_gov_018_runtime.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `pytest tests/automation/test_automation_runner.py tests/automation/test_high_throughput_runner.py tests/automation/test_orchestration_runtime_runner.py tests/automation/test_task_gov_017_runtime.py tests/automation/test_task_gov_018_runtime.py -q`

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
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `3`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/, scripts/task_coordination_lease.py, scripts/task_continuation_ops.py, scripts/task_lifecycle_ops.py, scripts/task_worker_ops.py, scripts/task_worktree_ops.py, scripts/child_execution_flow.py, scripts/governance_repo_checks.py, scripts/task_handoff.py, tests/governance/`
- `branch`: `feat/TASK-GOV-028-runner-local-platformization`
- `updated_at`: `2026-04-06T19:46:52+08:00`
<!-- generated:task-meta:end -->
