# TASK-GOV-054 Compile roadmap candidates from module graph

## Task Baseline

- `task_id`: `TASK-GOV-054`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `planned`
- `stage`: `governance-roadmap-candidate-compiler-v1`
- `branch`: `codex/TASK-GOV-054-roadmap-candidate-compiler`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`

## Primary Goals

- Introduce a roadmap candidate compiler that reads `MODULE_MAP` plus scheduler policy and emits module-root, preview-root, and integration-gate candidates.
- Convert `ROADMAP_BACKLOG.yaml` from a hand-maintained instance pool into template or policy plus compiled output mode.
- Add version fields tying compiler output to `MODULE_MAP`, scheduler policy, and evaluator compatibility.

## Explicitly Not Doing

- Do not change claim selection, `continue-roadmap`, or worker closeout behavior in this task.
- Do not change business code under `src/` or customer-visible contracts.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `.codex/local/roadmap_candidates/`

## Planned Write Paths

- `docs/governance/ROADMAP_BACKLOG.yaml`
- `docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml`
- `docs/governance/MODULE_MAP.yaml`
- `scripts/`
- `tests/governance/`
- `.codex/local/roadmap_candidates/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_roadmap_candidate_compiler.py -q`
- `pytest tests/governance/test_roadmap_scheduler_eval.py -q`
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

## Acceptance Targets

- Fresh idle fixture exposes multiple root candidates from compiler output.
- Compiler output includes `graph_version`, `module_map_version`, `policy_version`, and `compiled_at`.
- Missing module roots, duplicate roots per `module_id + candidate_intent`, and stale compiled graph versions block dispatch.

## Narrative Assertions

- `narrative_status`: `planned`
- `closeout_state`: `not_started`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `full_task_remaining`
- `next_gate`: `compiler_implementation`

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `planned`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `branch`: `codex/TASK-GOV-054-roadmap-candidate-compiler`
- `updated_at`: `2026-04-08T14:40:00+08:00`
<!-- generated:task-meta:end -->

