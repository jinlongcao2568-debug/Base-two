# TASK-GOV-075 quarantined full-clone slot semantics and candidate-pool compatibility

## Task Baseline

- `task_id`: `TASK-GOV-075`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `doing`
- `stage`: `governance-quarantined-slot-compatibility-v1`
- `branch`: `codex/TASK-GOV-075-quarantined-slot-compatibility`
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

- Distinguish quarantined full-clone slots from dispatch-blocking ready-slot divergences, so a preserved or otherwise isolated slot no longer degrades healthy pool dispatch by itself.
- Align `review_candidate_pool.py` and `claim-next` with the same dispatchability contract: only healthy ready slots should gate new claims, while quarantined slots remain visible but non-blocking.
- Add governance regression coverage proving a quarantined slot can coexist with healthy ready slots without freezing the candidate pool.

## Explicitly Not Doing

- Do not rebuild, refresh, or salvage any specific worker slot in this task; this task only changes scheduling and audit semantics.
- Do not change preserve-slot maintenance guards; those were completed in `TASK-GOV-074`.
- Do not modify Stage1-Stage9 business logic, contracts, migrations, or customer-visible outputs.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-075.md`
- `docs/governance/runlogs/TASK-GOV-075-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-075.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `scripts/control_plane_root.py`
- `scripts/review_candidate_pool.py`
- `scripts/roadmap_claim_next.py`
- `tests/governance/test_control_plane_single_ledger.py`
- `tests/governance/test_review_candidate_pool.py`
- `tests/governance/test_roadmap_claim_next.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_control_plane_single_ledger.py -q`
- `pytest tests/governance/test_review_candidate_pool.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
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
- `reserved_paths`: `src/, tests/stage2/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `codex/TASK-GOV-075-quarantined-slot-compatibility`
- `updated_at`: `2026-04-09T19:27:38+08:00`
<!-- generated:task-meta:end -->
