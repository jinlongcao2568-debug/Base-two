# TASK-GOV-055 Unify roadmap dispatch and retire legacy planner authority

## Task Baseline

- `task_id`: `TASK-GOV-055`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `planned`
- `stage`: `governance-roadmap-dispatch-unification-v1`
- `branch`: `codex/TASK-GOV-055-roadmap-dispatch-unification`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`

## Primary Goals

- Make compiled graph plus evaluator the only dispatch authority for roadmap work.
- Route `claim-next`, `continue-roadmap`, and `automation_runner --continue-roadmap` through the same compiled candidate graph and evaluator output.
- Remove roadmap dispatch authority from `task_coordination_planner` and `business_autopilot`.

## Explicitly Not Doing

- Do not redesign candidate compiler output in this task.
- Do not change worker finish or coordinator closeout behavior in this task.
- Do not change business logic under `src/`.

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

- `pytest tests/governance/test_roadmap_claim_next.py -q`
- `pytest tests/governance/test_task_continuation.py -q`
- `pytest tests/automation/test_automation_runner.py -q`
- `pytest tests/governance/test_automation_intent.py -q`
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

- No roadmap task is created or ranked by legacy planner code paths.
- Same fixture yields identical selectable sets across `claim-next`, `continue-roadmap`, and `automation_runner`.
- Dual dispatch path activation is explicitly blocked instead of silently coexisting.

## Narrative Assertions

- `narrative_status`: `planned`
- `closeout_state`: `not_started`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `full_task_remaining`
- `next_gate`: `dispatch_unification`

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
- `branch`: `codex/TASK-GOV-055-roadmap-dispatch-unification`
- `updated_at`: `2026-04-08T14:40:00+08:00`
<!-- generated:task-meta:end -->

