# TASK-GOV-068 Governance console background launch split and launcher decoupling

## Task Baseline

- `task_id`: `TASK-GOV-068`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-console-background-launch-hardening-v1`
- `branch`: `codex/TASK-GOV-068-console-launcher-background-split`
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

- Split governance console launch responsibilities so the Python service does not reclaim browser focus when a listener already exists.
- Keep the desktop shortcut as the operator entrypoint while preventing duplicate `pythonw` service launches.
- Preserve the existing governance console HTTP/API surface and candidate-pool action wiring.

## Explicitly Not Doing

- Do not change candidate pool evaluation, review, claim, closeout, or single-ledger governance behavior.
- Do not change auto-refresh intervals, task action identifiers, or any business-stage runtime code.
- Do not introduce a second scheduler, second persistence layer, or any new customer-facing UI/API contract.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-068.md`
- `docs/governance/runlogs/TASK-GOV-068-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-068.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `scripts/governance_console.py`
- `scripts/governance_console_launcher.vbs`
- `tests/governance/test_governance_console.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_governance_console.py -q`
- `python scripts/check_repo.py`

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
- `branch`: `codex/TASK-GOV-068-console-launcher-background-split`
- `updated_at`: `2026-04-09T18:03:36+08:00`
<!-- generated:task-meta:end -->
