# TASK-GOV-046 Provision full clone worker pool

## Task Baseline

- `task_id`: `TASK-GOV-046`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-full-clone-worker-pool-v1`
- `branch`: `codex/TASK-GOV-046-full-clone-worker-pool`
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

- Add a tracked full-clone worker pool definition for four manual Codex workspaces.
- Provision four complete local git clones on disk instead of git worktree pointer directories.
- Align each clone with the current slot branch so the user can manually open them as ordinary repositories.
- Keep the main governed repository unchanged while recording the clone pool as an operator-facing companion surface.

## Explicitly Not Doing

- Do not replace the existing governed worktree pool or dispatch logic in this task.
- Do not alter business code under `src/`, contracts, migrations, stage6 facts behavior, or customer-visible outputs.
- Do not attempt GUI desktop clicking; this task only provisions complete clone directories and records them.

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
- `branch`: `codex/TASK-GOV-046-full-clone-worker-pool`
- `updated_at`: `2026-04-09T12:08:35+08:00`
<!-- generated:task-meta:end -->
