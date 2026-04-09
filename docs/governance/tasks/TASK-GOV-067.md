# TASK-GOV-067 Ledger divergence cleanup and governance regression

## Task Baseline

- `task_id`: `TASK-GOV-067`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `doing`
- `stage`: `governance-ledger-divergence-cleanup-v1`
- `branch`: `codex/TASK-GOV-067-ledger-divergence-cleanup`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Clean clone-only ledger divergence for `TASK-RM-STAGE1-SOURCE-FAMILY-CN` while preserving audit evidence.
- Re-run candidate pool evaluation and governance regression checks to confirm MVP gating and control-plane health.

## Explicitly Not Doing

- Do not change business runtime code under `src/`.
- Do not change contracts under `docs/contracts/` or database migrations under `db/migrations/`.
- Do not introduce new sources, coverage entries, or customer-visible fields.

## Allowed Dirs

- `docs/governance/`
- `.codex/local/roadmap_candidates/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-067.md`
- `docs/governance/runlogs/TASK-GOV-067-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-067.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `.codex/local/roadmap_candidates/index.yaml`
- `.codex/local/roadmap_candidates/summary.yaml`
- `docs/governance/handoffs/ledger_divergence/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `python scripts/check_repo.py`
- `pytest tests/governance -q`
- `python scripts/task_ops.py review-candidate-pool`

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

- `narrative_status`: `doing`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `validation_pending`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `doing`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-067-ledger-divergence-cleanup`
- `updated_at`: `2026-04-09T12:08:35+08:00`
<!-- generated:task-meta:end -->
