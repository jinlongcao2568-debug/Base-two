# TASK-GOV-036 Ledger Activation Command Hardening

## Task Baseline

- `task_id`: `TASK-GOV-036`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-ledger-activation-commands-v1`
- `branch`: `feat/TASK-GOV-036-ledger-activation-commands`
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

- Add `task_ops queue-and-activate` so task creation, branch switching, activation, and ledger sync can be performed as one governed operation.
- Add `task_ops derive-ledgers` so current-task or task-file sources can repair task registry, worktree registry, roadmap state, and generated metadata without manual YAML edits.
- Preserve the live governance boundary: closed historical task files may repair their own historical ledger row but must not redefine the live current task.

## Explicitly Not Doing

- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or non-governance test suites.
- Do not change business stage logic, interface contracts, migrations, stage 6 fact refresh, customer-visible commitments, region/source coverage, or personal-information fields.
- Do not make historical task files a higher-priority source than live `CURRENT_TASK.yaml`.

## Acceptance Targets

- `queue-and-activate` can create and activate a new coordination task from idle with aligned branch, current task, registry, worktree, roadmap, task file, runlog, and handoff state.
- `queue-and-activate --existing-ok` can repair an existing queued coordination task into the live activation path.
- `derive-ledgers --from current-task` repairs live ledger drift only when explicitly run with `--write`.
- `derive-ledgers --from task-file --task-id TASK-ID` supports task-file repair while preventing closed historical task files from overwriting an unrelated live current task.
- Targeted governance tests cover the new commands and the live-vs-historical safety boundary.

## Rollback Plan

- Revert the new command registrations and lifecycle implementations in `scripts/`.
- Revert the added governance tests and documentation guidance.
- Restore `CURRENT_TASK.yaml`, `TASK_REGISTRY.yaml`, `WORKTREE_REGISTRY.yaml`, and `DEVELOPMENT_ROADMAP.md` to the pre-`TASK-GOV-036` idle control-plane state if the task is abandoned before closeout.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/`
- `scripts/task_lifecycle_ops.py`
- `scripts/task_runtime_ops.py`
- `tests/governance/test_task_ops.py`
- `tests/governance/test_task_ledger_derivation.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_task_ops.py -q`
- `pytest tests/governance/test_task_ledger_derivation.py -q`
- `pytest tests/governance/test_task_continuation.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `README.md`
- `tests/automation/`
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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/automation/, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `feat/TASK-GOV-036-ledger-activation-commands`
- `updated_at`: `2026-04-09T17:48:10+08:00`
<!-- generated:task-meta:end -->
