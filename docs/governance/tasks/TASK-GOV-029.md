# TASK-GOV-029 治理小白化入口：统一自动化开发入口

## Task Baseline

- `task_id`: `TASK-GOV-029`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `governance-novice-entry-v1`
- `branch`: `feat/TASK-GOV-029-novice-entry`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Add one explicit novice-friendly automation entry that lets a user issue a single “continue development” style command without knowing task/lane/closeout terms.
- Keep the implementation inside the existing automation intent router instead of introducing a second parallel control surface.
- Make the novice entry route safely based on actual live state: current task, idle/no-successor, and review/closeout readiness.

## Explicitly Not Doing

- Do not modify lease semantics, closeout mechanics, or child worktree internals in this task.
- Do not add GitHub publish, PR, or remote release behavior to the novice entry.
- Do not touch `src/`, contracts, migrations, integration tests, or automation runner internals.

## Acceptance Targets

- A novice-friendly phrase maps to one safe internal action without requiring the user to know `continue-current` vs `continue-roadmap`.
- The router chooses between current-task continuation and roadmap continuation from actual repo state.
- The novice entry blocks on ambiguous/unsafe situations rather than guessing.
- Documentation explains the one-command usage in plain language.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `README.md`

## Planned Write Paths

- `docs/governance/AUTOMATION_INTENTS.yaml`
- `scripts/automation_intent.py`
- `README.md`
- `tests/governance/test_automation_intent.py`

## Planned Test Paths

- `tests/governance/test_automation_intent.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/check_repo.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_automation_intent.py -q`
- `TASK-GOV-029`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
- `tests/automation/`
## Narrative Assertions

- `narrative_status`: `queued`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `activation_pending`

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `queued`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/, tests/automation/`
- `branch`: `feat/TASK-GOV-029-novice-entry`
- `updated_at`: `2026-04-07T06:57:09+08:00`
<!-- generated:task-meta:end -->
