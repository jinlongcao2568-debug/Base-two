# TASK-GOV-071 Governance console periodic flash diagnosis and containment

## Task Baseline

- `task_id`: `TASK-GOV-071`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-console-periodic-flash-containment-v1`
- `branch`: `codex/TASK-GOV-071-console-periodic-flash`
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

- Confirm whether the recurring visible flash is caused by the governance console foreground auto-refresh loop.
- Contain the flash without breaking the local console service, operator actions, or hidden-window/background refresh behavior.
- Keep the resulting refresh behavior explicit and operator-controlled so the console can still be refreshed on demand.

## Explicitly Not Doing

- Do not change candidate pool business decisions, task action semantics, or any Stage1-Stage9 pipeline logic.
- Do not modify contracts, migrations, customer-visible delivery outputs, or unrelated desktop/browser software outside the AX9 console path.
- Do not remove the existing manual refresh capability or the hidden-window background refresh path.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-071.md`
- `docs/governance/runlogs/TASK-GOV-071-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-071.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `scripts/governance_console.py`
- `scripts/governance_console_launcher.py`
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
- `branch`: `codex/TASK-GOV-071-console-periodic-flash`
- `updated_at`: `2026-04-09T18:03:36+08:00`
<!-- generated:task-meta:end -->
