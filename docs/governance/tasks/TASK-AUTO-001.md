# TASK-AUTO-001 自动化开发一期：主干控制面 + 按任务大小自动分流

## Task Baseline

- `task_id`: `TASK-AUTO-001`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `automation-control-plane-v1`
- `branch`: `feat/TASK-AUTO-001-automation-control-plane`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Land the first automation control-plane baseline on the main coordination worktree.
- Formalize `micro / standard / heavy` task sizing and the minimum runner gate.
- Add the initial module map, test matrix, hygiene policy, and automation operating model.
- Provide the first coordinator runner for check, gate, and cleanup commands.

## Out Of Scope

- No business-stage implementation work in `src/stage*_*/`.
- No automatic switch to the next task.
- No claim of unattended all-day automation readiness.

## Allowed Dirs

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/MODULE_MAP.yaml`
- `docs/governance/TEST_MATRIX.yaml`
- `docs/governance/CODE_HYGIENE_POLICY.md`
- `docs/governance/AUTOMATION_OPERATING_MODEL.md`
- `docs/governance/tasks/`
- `docs/governance/runlogs/`
- `scripts/`
- `tests/governance/`
- `tests/contracts/`
- `tests/automation/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `pytest tests/governance -q`
- `pytest tests/contracts -q`
- `pytest tests/automation -q`
- `pytest -q`

## Acceptance

- Automation mode gates participate in the coordinator runner.
- Governance, contracts, and automation smoke suites pass.
- The task is closed and no longer acts as the live execution entry.

## Closeout

- Closed on `2026-04-04`.
- Live execution ownership transferred to `TASK-GOV-001` for authority alignment hardening.

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
- `reserved_paths`: `src/, docs/contracts/, tests/integration/, scripts/check_hygiene.py`
- `branch`: `feat/TASK-AUTO-001-automation-control-plane`
- `updated_at`: `2026-04-05T12:54:52+08:00`
<!-- generated:task-meta:end -->

## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`