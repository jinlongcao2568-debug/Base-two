# TASK-GOV-067 Control-plane full-clone runtime hardening and stale-mirror containment

## Task Baseline

- `task_id`: `TASK-GOV-067`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-control-plane-full-clone-runtime-hardening-v2`
- `branch`: `codex/TASK-GOV-067-full-clone-runtime-hardening`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Seal clone-local governance writer entrypoints so control-plane writes always resolve to the main ledger.
- Expand ledger divergence detection to catch ready-slot stale mirrors, runtime drift, and clone-local residual execution state.
- Require live runtime validation before full-clone dispatch and add explicit operator commands for audit and rebuild.

## Explicitly Not Doing

- Do not repair clone-local ledger history in place.
- Do not modify business-stage logic, customer-visible semantics, or interface contracts.
- Do not touch `src/`, `tests/stage1/` through `tests/stage9/`, or `db/migrations/`.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/CONTROL_PLANE_FULL_CLONE_RUNTIME_HARDENING_EXECUTION_PLAN_V2.md`
- `docs/governance/FULL_CLONE_POOL.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/tasks/TASK-GOV-067.md`
- `docs/governance/runlogs/TASK-GOV-067-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-067.yaml`
- `scripts/control_plane_root.py`
- `scripts/full_clone_pool.py`
- `scripts/roadmap_candidate_index.py`
- `scripts/roadmap_candidate_compiler.py`
- `scripts/roadmap_claim_next.py`
- `scripts/review_candidate_pool.py`
- `scripts/task_runtime_ops.py`
- `scripts/task_continuation_ops.py`
- `scripts/worker_self_loop.py`
- `tests/governance/test_control_plane_single_ledger.py`
- `tests/governance/test_full_clone_pool.py`
- `tests/governance/test_roadmap_claim_next.py`
- `tests/governance/test_roadmap_candidate_index.py`
- `tests/governance/test_roadmap_candidate_compiler.py`
- `tests/governance/test_review_candidate_pool.py`
- `tests/governance/test_worker_self_loop.py`
- `tests/governance/test_task_ops.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_control_plane_single_ledger.py -q`
- `pytest tests/governance/test_full_clone_pool.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`
- `pytest tests/governance/test_roadmap_candidate_index.py -q`
- `pytest tests/governance/test_roadmap_candidate_compiler.py -q`
- `pytest tests/governance/test_review_candidate_pool.py -q`
- `pytest tests/governance/test_worker_self_loop.py -q`
- `pytest tests/governance/test_task_ops.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
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
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-067-full-clone-runtime-hardening`
- `updated_at`: `2026-04-09T15:48:06+08:00`
<!-- generated:task-meta:end -->
