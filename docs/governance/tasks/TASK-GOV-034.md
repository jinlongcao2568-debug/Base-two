# TASK-GOV-034 治理测试触发矩阵重构

## Task Baseline

- `task_id`: `TASK-GOV-034`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-test-trigger-matrix-v1`
- `branch`: `feat/TASK-GOV-034-governance-test-matrix`
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

- Refactor governance test triggering so `tests/governance -q` and `tests/automation -q` no longer act as broad default gates for most governance tasks.
- Keep business-stage test behavior unchanged while narrowing governance task required tests to path-triggered subsets.
- Preserve `check_authority_alignment.py` scoring and current governance semantics while changing only the trigger matrix and default test selection logic.

## Explicitly Not Doing

- Do not modify business stage logic under `src/`.
- Do not change `check_authority_alignment.py` scoring weights or pass/fail thresholds.
- Do not weaken release-grade or governance-core protections; only narrow default trigger scope.

## Acceptance Targets

- Governance control-plane tasks no longer default to full `tests/governance -q` / `tests/automation -q` for ordinary doc or narrow script changes.
- Path-based governance trigger profiles exist in `TEST_MATRIX.yaml` and are consumed by `governance_rules.task_required_tests_for_matrix()`.
- Business-stage module test selection remains unchanged.
- New governance tests prove:
  - documentation-only governance tasks trigger `governance_fast`
  - workflow tasks trigger `governance_workflow`
  - publish tasks trigger `governance_publish`
  - runner tasks trigger `automation_runner`
  - core policy tasks trigger `full_governance_release`

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_check_repo.py -q`
- `pytest tests/governance/test_task_continuation.py -q`
- `pytest tests/governance/test_parallel_closeout_pipeline.py -q`
- `pytest tests/governance/test_task_publish_ops.py -q`
- `pytest tests/governance/test_automation_intent.py -q`
- `pytest tests/automation/test_automation_runner.py -q`
- `pytest tests/automation/test_high_throughput_runner.py -q`
- `pytest tests/automation/test_orchestration_runtime_runner.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `README.md`
- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/contracts/`
- `tests/integration/`
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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/, tests/contracts/, tests/integration/`
- `branch`: `feat/TASK-GOV-034-governance-test-matrix`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
