# TASK-GOV-060 Candidate pool health radar and dispatch guardrails

## Task Baseline

- `task_id`: `TASK-GOV-060`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-health-radar-v1`
- `branch`: `codex/TASK-GOV-060-roadmap-health-radar`
- `size_class`: `micro`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Add health-radar fields for root coverage, closeout backlog, top blocker codes, and hard-gate backlog.
- Add dispatch guardrails so compiled-dispatch mode blocks legacy roadmap misdispatch.

## Explicitly Not Doing

- Do not add public product monitoring UI in this task.
- Do not change customer-visible contracts or business runtime behavior.

## Allowed Dirs

- `scripts/`
- `tests/governance/`
- `docs/governance/tasks/`
- `.codex/local/roadmap_candidates/`

## Planned Write Paths

- `scripts/review_candidate_pool.py`
- `scripts/task_coordination_planner.py`
- `scripts/business_autopilot.py`
- `tests/governance/test_review_candidate_pool.py`
- `tests/governance/test_roadmap_dispatch_unification.py`
- `docs/governance/tasks/TASK-GOV-060.md`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_review_candidate_pool.py -q`
- `pytest tests/governance/test_roadmap_dispatch_unification.py -q`
- `pytest tests/governance/test_task_continuation.py -q`
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

- Review-candidate-pool reports root counts, preview/formal split, closeout backlog, top blocker codes, and hard-gate backlog.
- Compiled-dispatch mode hard-blocks legacy roadmap generation paths from acquiring roadmap dispatch authority.
- Candidate pool can be judged as healthy or under-release without reading source code.

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
- `size_class`: `micro`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-060-roadmap-health-radar`
- `updated_at`: `2026-04-09T17:48:10+08:00`
<!-- generated:task-meta:end -->
