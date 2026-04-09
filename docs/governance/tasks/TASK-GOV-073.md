# TASK-GOV-073 published governance runtime stamp and dirty-runtime dispatch freeze

## Task Baseline

- `task_id`: `TASK-GOV-073`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-published-runtime-stamp-v1`
- `branch`: `codex/TASK-GOV-073-published-runtime-stamp`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Change the governance runtime stamp contract from live control-plane worktree content to a published-runtime baseline that full-clone workers can actually converge on.
- Freeze `claim-next` and related dispatch entrypoints when governance runtime files are dirty or otherwise unpublished, so the control plane fails fast instead of generating clone-unreachable runtime hashes.
- Add governance regression coverage that proves dirty runtime blocks dispatch while published runtime preserves stable parity semantics for healthy workers.

## Explicitly Not Doing

- Do not rebuild or refresh any full-clone slot in this task; slot recovery remains scoped to later tasks.
- Do not modify Stage1-Stage9 business logic, contracts, migrations, or customer-visible delivery semantics.
- Do not change preserve-slot guard behavior or quarantined-slot scheduling semantics in this task; those belong to `TASK-GOV-074` and `TASK-GOV-075`.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-073.md`
- `docs/governance/runlogs/TASK-GOV-073-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-073.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `scripts/control_plane_root.py`
- `scripts/roadmap_claim_next.py`
- `scripts/review_candidate_pool.py`
- `tests/governance/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_control_plane_single_ledger.py -q`
- `pytest tests/governance/test_full_clone_pool.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
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
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, tests/stage2/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `codex/TASK-GOV-073-published-runtime-stamp`
- `updated_at`: `2026-04-09T19:11:08+08:00`
<!-- generated:task-meta:end -->
