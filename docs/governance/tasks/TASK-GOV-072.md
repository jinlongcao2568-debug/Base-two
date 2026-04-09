# TASK-GOV-072 Candidate pool stale-claim cleanup and governance test hygiene remediation

## Task Baseline

- `task_id`: `TASK-GOV-072`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-candidate-pool-hygiene-remediation-v1`
- `branch`: `codex/TASK-GOV-072-candidate-pool-hygiene-remediation`
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

- Clear stale closed claim handling from candidate-pool review and closeout claim state without changing live candidate ordering.
- Split the governance test hotspots that were tripping hygiene block thresholds, while leaving `src/` untouched.
- Reclassify the current `worker-01` full-clone drift as an explicit preserve-first isolation state and refresh the idle full clones to the current governance runtime stamp.

## Explicitly Not Doing

- Do not modify `src/` or `tests/stage2/` implementation files.
- Do not merge, discard, or otherwise absorb the preserved `worker-01` Stage2 local implementation state.
- Do not fix the legacy lane-cap failures in `tests/governance/test_task_ops.py`.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/roadmap_candidates/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-072.md`
- `docs/governance/runlogs/TASK-GOV-072-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-072.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/FULL_CLONE_POOL.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `.codex/local/roadmap_candidates/claims.yaml`
- `scripts/review_candidate_pool.py`
- `scripts/task_lifecycle_ops.py`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `pytest tests/governance/test_review_candidate_pool.py -q`
- `pytest tests/governance/test_control_plane_single_ledger.py -q`
- `pytest tests/governance/test_full_clone_pool.py -q`
- `pytest tests/governance/test_task_continuation.py tests/governance/test_task_continuation_business.py -q`
- `pytest tests/governance/test_task_ops_worktree_runtime.py -q`
- `pytest tests/governance/test_task_ops_worktree_runtime.py::test_review_candidate_pool_from_clone_cwd_reads_control_plane_truth -q`

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
- `branch`: `codex/TASK-GOV-072-candidate-pool-hygiene-remediation`
- `updated_at`: `2026-04-09T18:34:12+08:00`
<!-- generated:task-meta:end -->
