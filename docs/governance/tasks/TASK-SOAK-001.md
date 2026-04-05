# TASK-SOAK-001 连续 soak chaos fallback 验证

## Task Baseline

- `task_id`: `TASK-SOAK-001`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-soak-chaos-validation-v1`
- `branch`: `feat/TASK-SOAK-001-continuous-autonomy-validation`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Add a governed soak and chaos validation loop that exercises `continue-roadmap` and `automation_runner` across `standard`, `heavy 2 lanes`, `heavy 3 lanes`, and `heavy 4 lanes`.
- Measure ledger drift, fallback behavior, child closeout success, orphan cleanup failures, and branch/worktree mismatches in a repeatable report format.
- Establish the hard validation threshold for continuous autonomy before heavy tasks can graduate to higher default automation.

## Explicitly Not Doing

- Do not add new production execution intents.
- Do not change stage business implementation in this task.
- Do not raise the parallel ceiling beyond `4` or introduce a multi-coordinator model.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

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

- `narrative_status`: `queued`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `activation_pending`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `queued`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-SOAK-001-continuous-autonomy-validation`
- `updated_at`: `2026-04-05T19:06:16+08:00`
<!-- generated:task-meta:end -->
