# TASK-GOV-020 治理并行修复父任务：状态机、权威对齐与慢测试分层

## Task Baseline

- `task_id`: `TASK-GOV-020`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-parallel-repair-bundle-v1`
- `branch`: `feat/TASK-GOV-020-governance-repair-parent`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `parallel_parent`
- `lane_count`: `3`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Coordinate three disjoint child lanes under one governed repair bundle: continuation semantics, authority-alignment regression sync, and slow-test layering.
- Keep the repair auditable by making the parent responsible only for orchestration, split integrity, child-worktree preparation, and final aggregate validation.
- Keep the parent limited to governance coordination artifacts while the three child lanes own implementation in isolated worktrees.

## Explicitly Not Doing

- Do not implement governance script or test changes in the parent coordination worktree.
- Do not merge child-lane code or auto-close the bundle before all three lanes finish and aggregate validation passes.
- Do not bundle Python environment contract cleanup or subprocess portability cleanup into this repair bundle.
- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.

## Task Intake

- `primary_objective`: execute the parent coordination lane for the already-split governance repair bundle and prepare three isolated child worktrees.
- `not_doing`: child-lane implementation, environment-contract hardening, and subprocess portability remain outside this parent coordination step.
- `stage_scope`: governance coordination and control-plane alignment only; no business-stage logic changes.
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
- The parent task is explicitly activated in `CURRENT_TASK.yaml` and `DEVELOPMENT_ROADMAP.md`.
- Three child execution worktrees are prepared under the parent with baseline checks recorded in the control plane.
- Parent handoff, task file, and runlog describe the active child topology and aggregate verification gates.

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
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `parallel_parent`
- `lane_count`: `3`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-020-3`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/, scripts/, tests/governance/, tests/automation/`
- `branch`: `feat/TASK-GOV-020-governance-repair-parent`
- `updated_at`: `2026-04-09T17:02:25+08:00`
<!-- generated:task-meta:end -->
