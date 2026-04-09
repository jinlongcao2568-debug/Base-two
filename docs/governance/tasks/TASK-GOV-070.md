# TASK-GOV-070 Governance console popup eradication and safe launcher containment

## Task Baseline

- `task_id`: `TASK-GOV-070`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-console-popup-eradication-v1`
- `branch`: `codex/TASK-GOV-070-console-popup-eradication`
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

- Identify the exact process chain that still produces visible black popup windows when the desktop AX9 governance console shortcut is clicked or left running.
- Eliminate popup-generating launcher behavior without breaking the governance console service, local `127.0.0.1:8765` UI, or operator shortcut workflow.
- Keep the final launcher path auditable and regression-tested so future console starts and auto-refresh cycles remain popup-free.

## Explicitly Not Doing

- Do not change candidate pool logic, governance task actions, refresh cadence semantics, or any Stage1-Stage9 business behavior.
- Do not modify contracts, database migrations, customer-visible delivery outputs, or any non-console runtime outside the launcher containment scope.
- Do not perform global uninstall or policy changes for third-party security software; only contain its effect on the AX9 console entry path if needed.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-070.md`
- `docs/governance/tasks/`
- `docs/governance/runlogs/TASK-GOV-070-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-070.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/WORKTREE_REGISTRY.yaml`
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
- `branch`: `codex/TASK-GOV-070-console-popup-eradication`
- `updated_at`: `2026-04-09T17:21:56+08:00`
<!-- generated:task-meta:end -->
