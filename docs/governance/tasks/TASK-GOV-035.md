# TASK-GOV-035 治理历史材料边界与检索降噪

## Task Baseline

- `task_id`: `TASK-GOV-035`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-historical-artifact-boundary-v1`
- `branch`: `feat/TASK-GOV-035-historical-governance-boundary`
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

- Define a live governance boundary that tells operators, prompts, and repo checks which documents are the current source for default gates.
- Preserve historical task/runlog/handoff/registry evidence without letting those records override the live governance surfaces.
- Add targeted regression coverage so future changes cannot silently collapse the live-vs-historical distinction.

## Explicitly Not Doing

- Do not rewrite or delete historical task files, runlogs, handoffs, or registry rows.
- Do not touch `src/`, `docs/contracts/`, `db/migrations/`, or stage/contract/integration suites.
- Do not rework test-bundle semantics in `TEST_MATRIX.yaml`; this task only clarifies which surfaces are live versus historical.

## Acceptance Targets

- A live governance boundary document exists and names the canonical live operator and prompt surfaces.
- `OPERATOR_MANUAL.md` and prompt-governance docs point search behavior to the live surfaces before historical artifacts.
- `check_authority_alignment.py` and targeted governance regressions fail when the live-vs-historical distinction drifts.

## Rollback Plan

- Revert the new live-boundary document, the operator and prompt guidance updates, the authority-alignment checks, and the related governance tests.
- Restore `TASK-GOV-035` ledgers to the pre-activation state if this task needs to be abandoned before implementation completes.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/`
- `scripts/check_authority_alignment.py`
- `tests/governance/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_check_repo.py -q`
- `pytest tests/governance/test_task_continuation.py -q`
- `pytest tests/governance/test_authority_alignment.py -q`
- `pytest tests/governance/test_governance_required_tests.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `README.md`
- `tests/automation/`
- `tests/contracts/`
- `tests/integration/`
- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/automation/, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `feat/TASK-GOV-035-historical-governance-boundary`
- `updated_at`: `2026-04-09T18:03:36+08:00`
<!-- generated:task-meta:end -->
