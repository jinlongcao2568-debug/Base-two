# TASK-GOV-037 Roadmap idle successor generation repair

## Task Baseline

- `task_id`: `TASK-GOV-037`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-idle-successor-generation-v1`
- `branch`: `feat/TASK-GOV-037-roadmap-idle-successor-generation`
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

- Repair the roadmap continuation gap where `CURRENT_TASK.yaml` is idle, `DEVELOPMENT_ROADMAP.md` has `auto_create_missing_task: true`, and `continue-roadmap` still exits with `no successor is available`.
- Align `automation_intent.py` preflight/execute behavior with the actual continuation path so free-form "continue roadmap" requests cannot report `ready` while the governed runner cannot advance.
- Preserve the live governance boundary by generating or reporting the missing successor through the existing task lifecycle/planner surfaces instead of inventing a second source of truth.

## Explicitly Not Doing

- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, `README.md`, contract tests, integration tests, or stage-specific tests.
- Do not change business stage logic, interface contracts, schema migrations, stage 6 fact refresh/writeback policy, customer-visible commitments, region/source coverage, or customer-visible personal information fields.
- Do not rewrite, delete, or reinterpret historical task files, runlogs, handoffs, or absorbed task registry rows except for strictly necessary live ledger entries for `TASK-GOV-037`.

## Governance Scope Confirmation

- `task_id`: `TASK-GOV-037`
- `main_objective`: `roadmap idle successor generation repair`
- `stage`: `governance-roadmap-idle-successor-generation-v1`
- `affected_modules`: `task lifecycle operations`, `roadmap continuation`, `automation intent routing`, `automation runner continuation`
- `interface_change`: `no`
- `migration_change`: `no`
- `exception_required`: `no`
- `stage6_facts_refresh_or_writeback_impact`: `no`
- `customer_visible_commitment_impact`: `no`
- `region_or_source_coverage_impact`: `no`
- `customer_visible_personal_information_impact`: `no`

## Acceptance Targets

- `continue-roadmap` from a clean idle control plane with no successor must not silently stop when roadmap policy allows missing-task creation; it must either create/activate a governed successor or return a deterministic blocker explaining why generation is unavailable.
- `automation_intent.py preflight --utterance "持续按路线图开发"` must not return `ready` for a continuation path that the mapped execution cannot actually advance.
- `automation_runner.py once --continue-roadmap --prepare-worktrees` must preserve clean governance state and report the same continuation outcome as the task lifecycle command.
- Regression tests must cover the idle/no-successor mismatch and the repaired path without broadening release-grade governance gates.

## Rollback Plan

- Revert the `TASK-GOV-037` lifecycle, automation intent, runner, test, and governance documentation changes.
- Restore `CURRENT_TASK.yaml`, `TASK_REGISTRY.yaml`, `WORKTREE_REGISTRY.yaml`, `DEVELOPMENT_ROADMAP.md`, and the `TASK-GOV-037` task/runlog/handoff files to the pre-task idle state if the task is abandoned before closeout.
- Keep business stage files, contracts, migrations, and historical absorbed tasks untouched.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_task_continuation.py -q`
- `pytest tests/governance/test_task_continuation_idle_successor.py -q`
- `pytest tests/governance/test_task_ops.py -q`
- `pytest tests/governance/test_automation_intent.py -q`
- `pytest tests/automation/test_automation_runner.py -q`

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
- `branch`: `feat/TASK-GOV-037-roadmap-idle-successor-generation`
- `updated_at`: `2026-04-09T17:02:25+08:00`
<!-- generated:task-meta:end -->
