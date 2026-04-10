# TASK-GOV-088 Slim governance entry docs and route product-first

## Task Baseline

- `task_id`: `TASK-GOV-088`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `doing`
- `stage`: `governance-doc-entry-slimming-v1`
- `branch`: `codex/TASK-OPS-009-full-clone-slot-release-hardening`
- `size_class`: `standard`
- `automation_mode`: `assisted`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Deliver `TASK-GOV-088`: Slim governance entry docs and route product-first for stage `governance-doc-entry-slimming-v1`.
- Implement planned write paths: README.md, docs/INDEX.md, docs/governance/README.md, docs/governance/tasks/TASK-GOV-088.md, docs/governance/runlogs/TASK-GOV-088-RUNLOG.md, docs/governance/handoffs/TASK-GOV-088.yaml, docs/governance/TASK_REGISTRY.yaml, docs/governance/CURRENT_TASK.yaml, docs/governance/WORKTREE_REGISTRY.yaml.
- Keep required tests passing: python scripts/check_authority_alignment.py, python scripts/check_repo.py.
## Explicitly Not Doing

- Do not touch reserved paths: src/, scripts/, tests/, db/migrations/, docs/contracts/, docs/product/.
- Do not modify files outside allowed dirs: README.md, docs/.
- Do not expand scope outside planned write paths: README.md, docs/INDEX.md, docs/governance/README.md, docs/governance/tasks/TASK-GOV-088.md, docs/governance/runlogs/TASK-GOV-088-RUNLOG.md, docs/governance/handoffs/TASK-GOV-088.yaml, docs/governance/TASK_REGISTRY.yaml, docs/governance/CURRENT_TASK.yaml, docs/governance/WORKTREE_REGISTRY.yaml.
## Allowed Dirs

- `README.md`
- `docs/`

## Planned Write Paths

- `README.md`
- `docs/INDEX.md`
- `docs/governance/README.md`
- `docs/governance/tasks/TASK-GOV-088.md`
- `docs/governance/runlogs/TASK-GOV-088-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-088.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`

## Planned Test Paths

- `README.md`
- `docs/INDEX.md`
- `docs/governance/README.md`

## Required Tests

- `python scripts/check_authority_alignment.py`
- `python scripts/check_repo.py`

## Reserved Paths

- `src/`
- `scripts/`
- `tests/`
- `db/migrations/`
- `docs/contracts/`
- `docs/product/`
## Narrative Assertions

- `narrative_status`: `doing`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `validation_pending`
## Acceptance Criteria

- Required tests pass: python scripts/check_authority_alignment.py, python scripts/check_repo.py.
- Changes limited to planned write paths: README.md, docs/INDEX.md, docs/governance/README.md, docs/governance/tasks/TASK-GOV-088.md, docs/governance/runlogs/TASK-GOV-088-RUNLOG.md, docs/governance/handoffs/TASK-GOV-088.yaml, docs/governance/TASK_REGISTRY.yaml, docs/governance/CURRENT_TASK.yaml, docs/governance/WORKTREE_REGISTRY.yaml.
- No open blockers remain at closeout.

## Rollback

- Revert branch `codex/TASK-OPS-009-full-clone-slot-release-hardening` to the last known good commit if needed.
- Remove or reset generated artifacts before re-dispatching the task.

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `doing`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `assisted`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, scripts/, tests/, db/migrations/, docs/contracts/, docs/product/`
- `branch`: `codex/TASK-OPS-009-full-clone-slot-release-hardening`
- `updated_at`: `2026-04-10T14:15:52+08:00`
<!-- generated:task-meta:end -->
