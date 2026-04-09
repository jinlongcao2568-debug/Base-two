# TASK-GOV-074 full-clone refresh/rebuild preserve guard hardening

## Task Baseline

- `task_id`: `TASK-GOV-074`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-preserve-guard-hardening-v1`
- `branch`: `codex/TASK-GOV-074-preserve-guard-hardening`
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

- Make `refresh-full-clone-pool` and `rebuild-full-clone-pool` share the same preserve-slot guard, so `preserve_before_rebuild` slots always fail fast instead of being reset by a refresh path.
- Keep preserve-slot handling explicit and auditable in the control plane, without weakening existing idle-slot rebuild and refresh recovery for healthy workers.
- Add governance regression coverage that proves preserve slots are protected on both entrypoints while normal idle slots remain recoverable.

## Explicitly Not Doing

- Do not recover or rebuild any specific worker slot in this task; this task only hardens the guardrail logic.
- Do not change candidate-pool scheduling semantics or quarantined-slot dispatch behavior; that belongs to `TASK-GOV-075`.
- Do not modify Stage1-Stage9 business logic, contracts, migrations, or customer-visible outputs.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-074.md`
- `docs/governance/runlogs/TASK-GOV-074-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-074.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `scripts/full_clone_pool.py`
- `tests/governance/test_full_clone_pool.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

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
- `branch`: `codex/TASK-GOV-074-preserve-guard-hardening`
- `updated_at`: `2026-04-09T19:21:55+08:00`
<!-- generated:task-meta:end -->
