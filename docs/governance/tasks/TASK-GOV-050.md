# TASK-GOV-050 Repair worker-01 runtime drift and full clone slot sync

## Task Baseline

- `task_id`: `TASK-GOV-050`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-worker-runtime-drift-repair-v1`
- `branch`: `codex/TASK-GOV-050-worker-runtime-drift-repair`
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

- Prevent `provision-full-clone-pool` from resetting an active full clone slot back to `ready`.
- Repair the live `worker-01` runtime state so `FULL_CLONE_POOL`, claims, and `TASK_REGISTRY` agree on the same execution task.
- Keep review/audit output green after the repair without altering business code.

## Explicitly Not Doing

- Do not change business code under `src/`, contracts, migrations, stage6 facts behavior, or customer-visible outputs.
- Do not expand worker capacity or alter the candidate DAG in this task.
- Do not rewrite the paused `TASK-RM-STAGE1-CORE-CONTRACT` into another lifecycle state unless required by consistency repair.

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

- `pytest tests/governance/test_review_candidate_pool.py -q`
- `pytest tests/governance/test_full_clone_pool.py -q`
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
- `branch`: `codex/TASK-GOV-050-worker-runtime-drift-repair`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
