# TASK-GOV-001 权威一致性收口与控制面硬化

## Task Baseline

- `task_id`: `TASK-GOV-001`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `authority-consistency-hardening`
- `branch`: `feat/TASK-GOV-001-authority-consistency-hardening`
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

- Eliminate live-task drift across current task, registry, worktree registry, task files, runlogs, and roadmap.
- Upgrade contracts into professional assets with schema, example, and field semantics for the formal `project_fact`.
- Add the minimum real `stage3 -> stage4 -> stage6` regression chain.
- Expand README, MVP, test matrix, and governance indexes from seed-level text into execution-grade documents.

## Explicitly Not Doing

- No stage-directory rename.
- No move of `docs/contracts/` to a second root location.
- No new business implementation logic in formal stage source directories.

## Allowed Dirs

- `README.md`
- `docs/product/`
- `docs/contracts/`
- `docs/governance/`
- `scripts/`
- `tests/contracts/`
- `tests/governance/`
- `tests/automation/`
- `tests/integration/`
- `tests/fixtures/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage6/`

## Planned Write Paths

- `README.md`
- `docs/product/`
- `docs/contracts/`
- `docs/governance/`
- `scripts/`
- `tests/contracts/`
- `tests/governance/`
- `tests/automation/`
- `tests/integration/`
- `tests/fixtures/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage6/`

## Required Tests

- `python scripts/check_authority_alignment.py`
- `python scripts/validate_contracts.py`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `pytest tests/contracts -q`
- `pytest tests/governance -q`
- `pytest tests/automation -q`
- `pytest tests/integration -q`
- `pytest tests/stage3 -q`
- `pytest tests/stage4 -q`
- `pytest tests/stage6 -q`
- `pytest -q`

## Acceptance

- No live-task drift across current task, registry, worktree, task file, runlog, and roadmap.
- `docs/contracts/` includes registry, schema, example, and field semantics for `project_fact`.
- `tests/integration/` contains a real, repeatable chain for `stage3 -> stage4 -> stage6`.
- README and downstream documents stop using seed or skeleton language for live controls.
- `python scripts/check_authority_alignment.py` reports all authority and automation-readiness scores at `>=95`.
- The final batch-5 validation sequence can be repeated twice without score drift.

## Rollback

- Revert governance entry files, contracts assets, tests, and scripts changed under this task.
- Restore `CURRENT_TASK.yaml`, `TASK_REGISTRY.yaml`, and `WORKTREE_REGISTRY.yaml` to the previous committed state if the hardening task must be abandoned.

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
- `reserved_paths`: `src/, docs/contracts/, tests/integration/, scripts/check_hygiene.py`
- `branch`: `feat/TASK-GOV-001-authority-consistency-hardening`
- `updated_at`: `2026-04-05T20:28:55+08:00`
<!-- generated:task-meta:end -->
