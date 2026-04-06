# TASK-GOV-025 治理本地并发平台化父任务：lease closeout mirror runner

## Task Baseline

- `task_id`: `TASK-GOV-025`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-local-multi-agent-platformization-v1`
- `branch`: `feat/TASK-GOV-025-local-multi-agent-platformization`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `parallel_parent`
- `lane_count`: `3`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Coordinate one local multi-agent platformization round with two first-wave implementation lanes and one second-wave runner lane.
- Keep the parent restricted to governance artifacts while child lanes own all script/test code changes.
- Return the repository to legal idle after all child lanes complete and aggregate validation passes.

## Explicitly Not Doing

- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.
- Do not include GitHub publish, PR, remote bootstrap, or release automation in this task.
- Do not introduce multi-machine worker support; this round only hardens single-machine multi-session execution.

## Acceptance Targets

- `TASK-GOV-026` and `TASK-GOV-027` can run in parallel without write-scope overlap.
- `TASK-GOV-028` runs only after the first-wave child lanes land back on the parent branch.
- Parent validation passes and the repository returns to idle with no successor activation.

## Allowed Dirs

- `docs/governance/`

## Planned Write Paths

- `docs/governance/`

## Planned Test Paths

- `tests/governance/test_coordination_lease.py`
- `tests/governance/test_parallel_closeout_pipeline.py`
- `tests/governance/test_task_continuation.py`
- `tests/governance/test_authority_alignment.py`
- `tests/governance/test_task_ops.py`
- `tests/automation/test_automation_runner.py`
- `tests/automation/test_high_throughput_runner.py`
- `tests/automation/test_orchestration_runtime_runner.py`
- `tests/automation/test_task_gov_017_runtime.py`
- `tests/automation/test_task_gov_018_runtime.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/check_repo.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_coordination_lease.py tests/governance/test_parallel_closeout_pipeline.py tests/governance/test_task_continuation.py tests/governance/test_authority_alignment.py tests/governance/test_task_ops.py -q`
- `pytest tests/automation/test_automation_runner.py tests/automation/test_high_throughput_runner.py tests/automation/test_orchestration_runtime_runner.py tests/automation/test_task_gov_017_runtime.py tests/automation/test_task_gov_018_runtime.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
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
- `topology`: `parallel_parent`
- `lane_count`: `3`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/, scripts/, tests/governance/, tests/automation/`
- `branch`: `feat/TASK-GOV-025-local-multi-agent-platformization`
- `updated_at`: `2026-04-06T19:46:52+08:00`
<!-- generated:task-meta:end -->
