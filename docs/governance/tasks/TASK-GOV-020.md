# TASK-GOV-020 治理并行修复父任务：状态机、权威对齐与慢测试分层

## Task Baseline

- `task_id`: `TASK-GOV-020`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-parallel-repair-bundle-v1`
- `branch`: `feat/TASK-GOV-020-governance-repair-parent`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `parallel_parent`
- `lane_count`: `3`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Coordinate three disjoint child lanes under one governed repair bundle: continuation semantics, authority-alignment regression sync, and slow-test layering.
- Keep the repair auditable by making the parent responsible only for orchestration, split integrity, and final aggregate validation.
- Preserve the repository in explicit idle state during drafting; no implementation or activation happens in this task-package step.

## Explicitly Not Doing

- Do not activate `TASK-GOV-020` or any child task automatically.
- Do not implement governance script or test changes in this drafting step.
- Do not bundle Python environment contract cleanup or subprocess portability cleanup into this repair bundle.
- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.

## Task Intake

- `primary_objective`: split the governance repair into one parent task and three execution lanes with disjoint write scopes.
- `not_doing`: activation, implementation, environment-contract hardening, and subprocess portability remain outside this drafting step.
- `stage_scope`: governance coordination and task-package topology only; no business-stage logic changes.
- `impact_modules`:
  - `docs/governance/tasks/TASK-GOV-020.md`
  - `docs/governance/runlogs/TASK-GOV-020-RUNLOG.md`
  - `docs/governance/handoffs/TASK-GOV-020.yaml`
  - `docs/governance/TASK_REGISTRY.yaml`
  - `docs/governance/tasks/TASK-GOV-021.md`
  - `docs/governance/tasks/TASK-GOV-022.md`
  - `docs/governance/tasks/TASK-GOV-023.md`
  - `docs/governance/runlogs/TASK-GOV-021-RUNLOG.md`
  - `docs/governance/runlogs/TASK-GOV-022-RUNLOG.md`
  - `docs/governance/runlogs/TASK-GOV-023-RUNLOG.md`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- `TASK-GOV-020` is a `parallel_parent` package with `lane_count: 3` and a shared `parallelism_plan_id`.
- `TASK-GOV-021/022/023` exist as execution child packages with disjoint planned write and test scopes.
- Parent handoff, task file, and runlog describe the child topology and aggregate verification gates.
- No change is made to `CURRENT_TASK.yaml`; the repo remains idle until explicit activation.

## Rollback Plan

- Remove child task packages `TASK-GOV-021/022/023`.
- Restore `TASK-GOV-020` to the prior single-worker draft package if the split topology is rejected.
- Re-run lightweight governance validation to confirm the registry and task artifacts return to the pre-split state.

## Allowed Dirs

- `docs/governance/`

## Planned Write Paths

- `docs/governance/`

## Planned Test Paths

- `tests/governance/test_check_repo.py`
- `tests/governance/test_task_continuation.py`
- `tests/governance/test_authority_alignment.py`
- `tests/automation/test_automation_runner.py`
- `tests/automation/test_high_throughput_runner.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/task_ops.py split-check TASK-GOV-020`
- `python scripts/check_repo.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_check_repo.py tests/governance/test_task_continuation.py tests/governance/test_authority_alignment.py -q`
- `pytest tests/automation/test_automation_runner.py tests/automation/test_high_throughput_runner.py -q`

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
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/, scripts/, tests/governance/, tests/automation/`
- `branch`: `feat/TASK-GOV-020-governance-repair-parent`
- `updated_at`: `2026-04-06T15:29:51+08:00`
<!-- generated:task-meta:end -->
