# TASK-GOV-066 Candidate source unification and path materialization gate

## Task Baseline

- `task_id`: `TASK-GOV-066`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `done`
- `stage`: `governance-candidate-source-gate-v1`
- `branch`: `codex/TASK-GOV-066-candidate-source-gate`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Enforce a single candidate source of truth when `compiled_mode=module_graph_compiler` by blocking inline candidates in `ROADMAP_BACKLOG.yaml`.
- Add a planned write-path materialization gate so candidates whose `planned_write_paths` do not exist are blocked unless explicitly allowed.
- Align governance tests with the current stage1 candidate IDs (remove `stage1-source-family-lanes`).
- Add a pilot gate flag so stage1 child slices stay blocked unless explicitly enabled by control-plane policy.

## Explicitly Not Doing

- Do not change business runtime code under `src/`.
- Do not change contracts under `docs/contracts/`.
- Do not change database migrations under `db/migrations/`.
- Do not change stage6 fact semantics or customer-visible delivery fields.

## Task Intake

- `primary_objective`: unify candidate source of truth and enforce path/pilot gates in the roadmap evaluator.
- `not_doing`: no business runtime changes, no contracts/migrations, no stage6 fact changes.
- `stage_scope`: governance candidate evaluation only.
- `impact_modules`:
  - `docs/governance/ROADMAP_BACKLOG.yaml`
  - `docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml`
  - `scripts/roadmap_scheduler_eval.py`
  - `scripts/roadmap_candidate_compiler.py`
  - `tests/governance/test_roadmap_candidate_index.py`
  - `tests/governance/test_roadmap_scheduler_eval.py`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- When `compiled_mode=module_graph_compiler`, inline candidates in `ROADMAP_BACKLOG.yaml` are rejected with a clear governance error.
- Candidates with missing `planned_write_paths` are blocked unless `allow_create_paths=true` (or equivalent) is explicitly set.
- Stage1 pilot child slices are blocked by default unless a control-plane toggle explicitly enables the pilot.
- Governance tests reference current stage1 candidate IDs and no longer mention `stage1-source-family-lanes`.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-066.md`
- `docs/governance/ROADMAP_BACKLOG.yaml`
- `docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml`
- `scripts/roadmap_scheduler_eval.py`
- `scripts/roadmap_candidate_compiler.py`
- `tests/governance/test_roadmap_candidate_index.py`
- `tests/governance/test_roadmap_scheduler_eval.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_roadmap_candidate_index.py -q`
- `pytest tests/governance/test_roadmap_scheduler_eval.py -q`
- `pytest tests/governance/test_review_candidate_pool.py -q`
- `python scripts/check_repo.py`

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

## Rollback

- Restore prior candidate-source behavior and remove the materialization gate.
- Revert any pilot gate fields and restore the previous stage1 candidate readiness behavior.
- Regenerate `.codex/local/roadmap_candidates/index.yaml` if evaluator format changes require it.

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-066-candidate-source-gate`
- `updated_at`: `2026-04-09T17:02:25+08:00`
<!-- generated:task-meta:end -->

## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`