# TASK-GOV-069 Governance console extensionless app-mode launcher hardening

## Task Baseline

- `task_id`: `TASK-GOV-069`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-console-browser-host-hardening-v1`
- `branch`: `codex/TASK-GOV-069-console-extensionless-app-launch`
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

- Launch the governance console in a dedicated browser app window that does not load user extensions for the local `127.0.0.1:8765` surface.
- Keep the desktop shortcut and background service flow intact while steering AX9 console opens away from McAfee WebAdvisor or other extension-host command windows.
- Preserve the existing governance console HTTP/API surface and operator actions while hardening only the browser-entry behavior.

## Explicitly Not Doing

- Do not change candidate pool refresh cadence, governance task actions, or any roadmap scheduling behavior.
- Do not modify Stage1-Stage9 business logic, Stage6 facts, contracts, database migrations, or customer-visible delivery semantics.
- Do not globally uninstall, disable, or reconfigure the user's browser extensions outside the dedicated AX9 console launch path.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-069.md`
- `docs/governance/runlogs/TASK-GOV-069-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-069.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/WORKTREE_REGISTRY.yaml`
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
- `branch`: `codex/TASK-GOV-069-console-extensionless-app-launch`
- `updated_at`: `2026-04-09T17:48:10+08:00`
<!-- generated:task-meta:end -->
