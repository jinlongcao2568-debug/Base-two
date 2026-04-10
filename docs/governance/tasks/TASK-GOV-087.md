# TASK-GOV-087 Documentation entry index acceptance gates

## Task Baseline

- `task_id`: `TASK-GOV-087`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-docs-entry-index-v1.1`
- `branch`: `codex/TASK-GOV-087-docs-entry-index-gates`
- `size_class`: `micro`
- `automation_mode`: `assisted`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Deliver `TASK-GOV-087`: Documentation entry index acceptance gates for stage `governance-docs-entry-index-v1.1`.
- Implement planned write paths: docs/INDEX.md, README.md, and docs/governance/ ledger updates.
- Add an acceptance/gate index row that points to `docs/governance/PR_CHECKLIST.md` and `docs/governance/TEST_MATRIX.yaml`.
- Verify `README.md` still routes to `docs/INDEX.md` without contradicting single-ledger semantics.
- Keep required tests passing: python scripts/check_repo.py, python scripts/check_hygiene.py src docs tests.
## Explicitly Not Doing

- Do not touch reserved paths: docs/contracts/, src/, db/migrations/, tests/.
- Do not modify files outside allowed dirs: docs/, README.md.
- Do not expand scope outside planned write paths: docs/INDEX.md, README.md, and docs/governance/ ledger updates.
## Allowed Dirs

- `docs/`
- `README.md`

## Planned Write Paths

- `docs/INDEX.md`
- `README.md`
- `docs/governance/`

## Planned Test Paths

- `none` (doc-only change)

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`

## Reserved Paths

- `docs/contracts/`
- `src/`
- `db/migrations/`
- `tests/`
## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`
## Acceptance Criteria

- Required tests pass: python scripts/check_repo.py, python scripts/check_hygiene.py src docs tests.
- Changes limited to the planned write paths listed above.
- `docs/INDEX.md` includes an acceptance/gate row linking `docs/governance/PR_CHECKLIST.md` and `docs/governance/TEST_MATRIX.yaml`.
- `README.md` continues to link `docs/INDEX.md` and remains aligned with single-ledger execution wording.
- No open blockers remain at closeout.

## Rollback

- Revert branch `codex/TASK-GOV-087-docs-entry-index-gates` to the last known good commit if needed.
- Remove or reset generated artifacts before re-dispatching the task.

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `micro`
- `automation_mode`: `assisted`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `docs/contracts/, src/, db/migrations/, tests/`
- `branch`: `codex/TASK-GOV-087-docs-entry-index-gates`
- `updated_at`: `2026-04-10T09:51:24+08:00`
<!-- generated:task-meta:end -->
