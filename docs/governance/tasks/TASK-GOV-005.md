# TASK-GOV-005 自动续跑风控收口与提示词模块化

## Task Baseline

- `task_id`: `TASK-GOV-005`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-automation-risk-hardening-v1`
- `branch`: `feat/TASK-GOV-005-automation-intent-hardening`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Add a natural-language automation entrypoint that can route free-form "continue" intent into the existing control-plane commands without guessing beyond the two supported execution intents.
- Add an independent capability gate for downstream `stage7-stage9` business automation so roadmap scope alone cannot generate those successors.
- Fix Chinese path/readability issues in governance gate output and absorb the prompt memo into governed prompt modules instead of leaving it as a root-level scratch file.

## Explicitly Not Doing

- Do not modify business implementation code under `src/`.
- Do not change contracts, migrations, stage6 fact semantics, or customer-visible scope.
- Do not introduce any new execution intent beyond the existing `continue-current` and `continue-roadmap` command surfaces.

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

- `python scripts/check_authority_alignment.py`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `pytest tests/governance/test_check_repo.py tests/governance/test_task_continuation.py tests/governance/test_authority_alignment.py -q`
- `pytest tests/automation/test_automation_runner.py -q`
- `pytest tests/governance -q`
- `pytest tests/automation -q`

## Reserved Paths

- none
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
- `successor_state`: `immediate`
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-GOV-005-automation-intent-hardening`
- `updated_at`: `2026-04-09T17:02:25+08:00`
<!-- generated:task-meta:end -->
