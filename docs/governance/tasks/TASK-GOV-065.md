# TASK-GOV-065 MVP scope and coverage hard-gate alignment

## Task Baseline

- `task_id`: `TASK-GOV-065`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `done`
- `stage`: `governance-mvp-scope-gate-v1`
- `branch`: `codex/TASK-GOV-065-mvp-scope-gate`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Enforce MVP scope and coverage gates in the roadmap evaluator so out-of-scope candidates are blocked with explicit reason codes.
- Add `stage2_to_stage6` as a supported business automation scope and bind the roadmap frontmatter to this MVP gate.
- Keep candidate pool evaluation authoritative by applying scope/coverage gates in `roadmap_scheduler_eval` (not only in review/summary scripts).

## Explicitly Not Doing

- Do not change contracts under `docs/contracts/`.
- Do not change database migrations under `db/migrations/`.
- Do not change stage6 fact semantics or customer-visible delivery fields.
- Do not add new sources or region coverage entries.

## Task Intake

- `primary_objective`: harden MVP and coverage scope gates for roadmap evaluation and automation scope.
- `not_doing`: no contracts/migrations, no stage6 fact changes, no customer-visible field expansions.
- `stage_scope`: governance scope gating only.
- `impact_modules`:
  - `docs/product/MVP_SCOPE.md`
  - `docs/governance/DEVELOPMENT_ROADMAP.md`
  - `scripts/roadmap_scheduler_eval.py`
  - `scripts/business_autopilot.py`
  - `tests/governance/test_roadmap_scheduler_eval.py`
  - `tests/governance/test_review_candidate_pool.py`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- Candidates outside MVP (`stage2`-`stage6`) are blocked with reason code `out_of_mvp_scope` (or equivalent) in evaluator output.
- Candidates whose coverage or sources are not registered are blocked with `coverage_not_registered` (or equivalent).
- `stage2_to_stage6` is accepted by `business_autopilot`, and roadmap frontmatter uses it as the MVP automation scope.
- Review output surfaces the same MVP/coverage blockers as evaluator output.

## Allowed Dirs

- `docs/governance/`
- `docs/product/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-065.md`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/product/MVP_SCOPE.md`
- `scripts/roadmap_scheduler_eval.py`
- `scripts/business_autopilot.py`
- `tests/governance/test_roadmap_scheduler_eval.py`
- `tests/governance/test_review_candidate_pool.py`
- `tests/governance/helpers.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

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

- Revert the evaluator scope/coverage gates and restore the previous automation scope values.
- Restore `DEVELOPMENT_ROADMAP.md` frontmatter to the prior scope value.
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
- `branch`: `codex/TASK-GOV-065-mvp-scope-gate`
- `updated_at`: `2026-04-09T18:03:36+08:00`
<!-- generated:task-meta:end -->

## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`