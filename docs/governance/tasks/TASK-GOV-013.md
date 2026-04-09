# TASK-GOV-013 文档驱动协调任务包生成与优先级编排

## Task Baseline

- `task_id`: `TASK-GOV-013`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-doc-driven-coordination-planner-v1`
- `branch`: `feat/TASK-GOV-013-coordination-planner`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Add a document-driven coordination planner that reads roadmap, ledgers, runlogs, handoffs, and policy to rank the next governed coordination candidates.
- Generate explicit candidate task packages with complete boundaries, planned write paths, planned test paths, required tests, and dependency metadata.
- Support explicit candidate promotion into formal task packages, with optional activation, while keeping planner output out of live repo-tracked ledgers until promotion.

## Explicitly Not Doing

- Do not auto-activate or auto-start a candidate unless the operator explicitly passes the activation flag during promotion.
- Do not generate planner candidates without clear boundaries, dependency checks, and overlap screening.
- Do not modify product code under `src/`, contracts, migrations, or integration business-chain paths.

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
- `python scripts/check_hygiene.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance -q`
- `pytest tests/automation -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
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
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-013-coordination-planner`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
