# TASK-GOV-058 Evaluator explanation contract and release forecast

## Task Baseline

- `task_id`: `TASK-GOV-058`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-explanation-contract-v1`
- `branch`: `codex/TASK-GOV-058-roadmap-explanation-contract`
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

- Extend the shared evaluator output into a stable explanation contract.
- Add reason taxonomy, release evidence reporting, and release forecast so explanation and audit tooling can consume evaluator output without recomputing logic.
- Keep explanation data consistent across candidate index, claim-next, review-candidate-pool, and future explain commands.

## Explicitly Not Doing

- Do not add user-facing UI in this task.
- Do not redesign compiled candidate generation or dispatch entrypoints in this task.
- Do not change business logic under `src/`, contracts, or DB schema.

## Task Intake

- `primary_objective`: establish a complete explanation contract on top of the compiled roadmap scheduler evaluator.
- `not_doing`: no public product UI, no human review workflow, no business-stage implementation.
- `stage_scope`: governance scheduler explanation contract only.
- `impact_modules`:
  - `scripts/roadmap_scheduler_eval.py`
  - `scripts/review_candidate_pool.py`
  - `tests/governance/test_roadmap_scheduler_eval.py`
  - `tests/governance/test_review_candidate_pool.py`
  - `docs/governance/tasks/TASK-GOV-058.md`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- Evaluator output includes controlled reason codes, human-readable reason text, release evidence required and satisfied, release forecast, unlock count, source authority, and legacy mode.
- Waiting and blocked candidates can be explained without any second inference layer.
- Release forecast for upstream roots correctly predicts downstream candidate unlock sets.

## Rollback Plan

- Revert evaluator and review-pool explanation fields together.
- Restore prior lightweight evaluator output contract if downstream scripts cannot consume the new fields.
- Regenerate candidate index and summary after rollback.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/roadmap_candidates/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/roadmap_candidates/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `pytest tests/governance/test_roadmap_scheduler_eval.py -q`
- `pytest tests/governance/test_roadmap_candidate_compiler.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `README.md`
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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-058-roadmap-explanation-contract`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
