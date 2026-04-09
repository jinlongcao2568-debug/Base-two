# TASK-GOV-047 Roadmap candidate refresh and worker self-loop

## Task Baseline

- `task_id`: `TASK-GOV-047`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-candidate-refresh-worker-loop-v1`
- `branch`: `codex/TASK-GOV-047-roadmap-candidate-refresh-worker-loop`
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

- Add a control-plane-root resolver so full clone workers always read and write the main governance root.
- Add a roadmap candidate maintainer script and task_ops wrapper for one-shot and loop refresh.
- Add a worker self-loop command that can resume, close, reclaim, and claim the next task from a full clone slot.
- Add worker recovery intents for clone windows without changing the coordination intent path.

## Explicitly Not Doing

- Do not alter business code under `src/`, contracts under `docs/contracts/`, migrations, stage6 facts behavior, or customer-visible outputs.
- Do not replace the existing main coordination workflow with autonomous coding; this task only automates lifecycle routing.
- Do not remove the existing worktree pool compatibility layer.

## Allowed Dirs

- `.codex/local/roadmap_candidates/`
- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `.codex/local/roadmap_candidates/`
- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `pytest tests/governance/test_candidate_refresh_loop.py -q`
- `pytest tests/governance/test_worker_self_loop.py -q`
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
- `branch`: `codex/TASK-GOV-047-roadmap-candidate-refresh-worker-loop`
- `updated_at`: `2026-04-09T17:02:25+08:00`
<!-- generated:task-meta:end -->
