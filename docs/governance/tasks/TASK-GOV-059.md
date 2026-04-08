# TASK-GOV-059 Candidate pool explanation commands

## Task Baseline

- `task_id`: `TASK-GOV-059`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `planned`
- `stage`: `governance-roadmap-explain-commands-v1`
- `branch`: `codex/TASK-GOV-059-roadmap-explain-commands`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`

## Primary Goals

- Add explain commands for candidate, candidate pool, claim decision, and release chain.
- Make scheduler reasoning accessible without reading source code or raw yaml artifacts.

## Explicitly Not Doing

- Do not add a GUI or web dashboard in this task.
- Do not change dispatch decisions themselves in this task.

## Allowed Dirs

- `scripts/`
- `tests/governance/`
- `docs/governance/tasks/`

## Planned Write Paths

- `scripts/roadmap_explain.py`
- `scripts/task_runtime_ops.py`
- `tests/governance/test_roadmap_explain.py`
- `docs/governance/tasks/TASK-GOV-059.md`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_roadmap_explain.py -q`
- `pytest tests/governance/test_roadmap_scheduler_eval.py -q`
- `python scripts/check_repo.py`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
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

- `explain-candidate`, `explain-candidate-pool`, `explain-claim-decision`, and `explain-release-chain` all return deterministic structured output.
- Explain commands do not implement their own second scheduler logic; they read evaluator truth only.

## Narrative Assertions

- `narrative_status`: `planned`
- `closeout_state`: `not_started`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `full_task_remaining`
- `next_gate`: `explain_command_implementation`

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `planned`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `branch`: `codex/TASK-GOV-059-roadmap-explain-commands`
- `updated_at`: `2026-04-08T16:20:00+08:00`
<!-- generated:task-meta:end -->

