# TASK-GOV-019 治理收口与后继清理

## Task Baseline

- `task_id`: `TASK-GOV-019`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `doing`
- `stage`: `governance-closeout-artifact-alignment-v1`
- `branch`: `feat/TASK-GOV-019-closeout-artifact-alignment`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Clear the stale roadmap pointer that still recommends `TASK-GOV-018`.
- Remove absorbed backlog from planner and continuation successor selection.
- Clean `.codex/local/coordination_candidates/` so it only reflects live candidates.
- Add regression coverage for absorbed-task filtering and stale explicit-pointer fallback.

## Explicitly Not Doing

- Do not remove `continue-roadmap`, `plan-coordination`, or generated successor support.
- Do not reopen `TASK-BIZ-001/002/003`, `TASK-SOAK-001`, or `TASK-GRAD-001` as top-level successors.
- Do not expand into `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.
- Do not add a new successor mechanism or refactor unrelated governance flows.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/coordination_candidates/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/coordination_candidates/`

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

- `narrative_status`: `doing`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `validation_pending`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `doing`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-019-closeout-artifact-alignment`
- `updated_at`: `2026-04-06T14:12:09+08:00`
<!-- generated:task-meta:end -->
