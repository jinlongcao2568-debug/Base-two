# TASK-GOV-044 Roadmap worktree pool dispatch

## Task Baseline

- `task_id`: `TASK-GOV-044`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-worktree-pool-dispatch-v1`
- `branch`: `codex/TASK-GOV-044-roadmap-worktree-pool-dispatch`
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

- Add a tracked `WORKTREE_POOL.yaml` registry for fixed worker slots.
- Allocate promoted roadmap tasks from idle pool slots instead of ad-hoc paths.
- Block promotion when no idle pool slot is available.
- Release pool slots back to `idle` when execution worktrees are released.

## Explicitly Not Doing

- Do not change business code under `src/`, contracts, migrations, stage6 facts behavior, or customer-visible outputs.
- Do not add more than the default tracked pool definition and dispatch logic.
- Do not bypass the existing execution worktree validation rules.

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

- `pytest tests/governance/test_worktree_pool_dispatch.py -q`
- `pytest tests/governance/test_roadmap_claim_promotion.py -q`
- `pytest tests/governance/test_roadmap_takeover.py -q`
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
- `branch`: `codex/TASK-GOV-044-roadmap-worktree-pool-dispatch`
- `updated_at`: `2026-04-09T16:18:58+08:00`
<!-- generated:task-meta:end -->
