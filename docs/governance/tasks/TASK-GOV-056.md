# TASK-GOV-056 Coordinator-driven execution closeout and worker boundary hardening

## Task Baseline

- `task_id`: `TASK-GOV-056`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `planned`
- `stage`: `governance-roadmap-execution-closeout-v1`
- `branch`: `codex/TASK-GOV-056-roadmap-execution-closeout`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_task`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`

## Primary Goals

- Finish the responsibility split so workers execute and report while the coordinator owns closeout and release.
- Ensure review-ready execution tasks are closed by coordinator flow before new roadmap claims are issued.
- Make `worker_self_loop` stop at `await-coordinator-closeout` for review-ready roadmap execution tasks.

## Explicitly Not Doing

- Do not redesign the compiled candidate graph in this task.
- Do not change human review policy or introduce a separate approval workflow.
- Do not change business code under `src/`.

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

- `pytest tests/governance/test_worker_self_loop.py -q`
- `pytest tests/governance/test_roadmap_execution_closeout.py -q`
- `pytest tests/governance/test_roadmap_takeover.py -q`
- `pytest tests/automation/test_automation_runner.py -q`
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

- Worker no longer self-closes roadmap execution tasks.
- Closing a review-ready execution task releases downstream root candidates on next refresh.
- Candidate release no longer depends on the same worker continuing after `worker-finish`.
- Coordinator closeout blockers are visible and deterministic when review-ready backlog accumulates.

## Narrative Assertions

- `narrative_status`: `planned`
- `closeout_state`: `not_started`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `full_task_remaining`
- `next_gate`: `closeout_boundary_hardening`

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
- `branch`: `codex/TASK-GOV-056-roadmap-execution-closeout`
- `updated_at`: `2026-04-08T14:40:00+08:00`
<!-- generated:task-meta:end -->
