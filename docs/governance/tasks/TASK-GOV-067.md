# TASK-GOV-067 Ledger divergence cleanup + console flicker fix + slow-test fastlane

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
- Prevent Windows background runner flicker by hiding subprocess windows in automation runner and lane launcher.
- Split slow tests into a dedicated marker and provide a fast test entrypoint.

## Explicitly Not Doing

- Do not change business runtime code under `src/`.
- Do not change contracts under `docs/contracts/` or database migrations under `db/migrations/`.
- Do not introduce new sources, coverage entries, or customer-visible fields.
- Do not alter MVP/coverage policy or candidate gating logic.

## Allowed Dirs

- `docs/governance/`
- `.codex/local/roadmap_candidates/`
- `scripts/`
- `tests/`
- `pyproject.toml`

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
- `scripts/automation_runner.py`
- `scripts/local_lane_launcher.py`
- `scripts/run_tests_fast.py`
- `pyproject.toml`
- `tests/automation/`
- `tests/integration/`
- `tests/governance/test_candidate_refresh_loop.py`
- `tests/governance/test_parallel_closeout_pipeline.py`
- `tests/governance/test_worktree_pool_dispatch.py`
- `tests/governance/test_worktree_pool_prewarm.py`
- `tests/governance/test_worker_self_loop.py`
- `tests/governance/test_task_ops.py`
- `tests/governance/test_task_publish_ops.py`
- `tests/governance/test_roadmap_claim_next.py`
- `tests/governance/test_roadmap_execution_closeout.py`
- `tests/governance/test_roadmap_takeover.py`
- `tests/governance/test_roadmap_claim_promotion.py`
- `tests/governance/test_orchestration_runtime.py`
- `tests/governance/test_coordination_planner.py`
- `tests/governance/test_full_clone_pool.py`
- `tests/governance/test_handoff_recovery.py`
- `tests/governance/test_task_continuation.py`
- `tests/governance/test_task_continuation_idle_successor.py`
- `tests/governance/test_control_plane_single_ledger.py`

## Planned Test Paths

- `tests/`

## Required Tests

- `python scripts/run_tests_fast.py`
- `pytest tests/governance/test_governance_console.py -q`
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
- `updated_at`: `2026-04-09T12:39:17+08:00`
<!-- generated:task-meta:end -->
