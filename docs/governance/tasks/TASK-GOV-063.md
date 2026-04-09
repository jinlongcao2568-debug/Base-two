# TASK-GOV-063 Governance console refresh, localization, and action verification

## Task Baseline

- `task_id`: `TASK-GOV-063`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-console-refresh-fix-v1`
- `branch`: `codex/TASK-GOV-063-console-refresh-no-window-fix`
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

- Refresh the thin governance console UI so the operator-facing page reads naturally in Chinese and presents candidate tasks in bilingual Chinese/English form.
- Reshape the page into a single contained operator surface instead of an obvious browser-shell document while keeping the implementation as a thin wrapper over existing governance commands.
- Verify that every operator button exposed by the page still works end-to-end against the existing governance control plane.
- Restore automation intent phrase parsing for roadmap execution windows so related worker prompts no longer fail on invalid governance YAML.

## Explicitly Not Doing

- Do not introduce a second scheduler, second state source, or any browser-side orchestration logic.
- Do not modify business runtime code under `src/`, contracts under `docs/contracts/`, or database assets under `db/migrations/`.
- Do not add product-facing UI, customer-facing fields, or any new persistence layer for the governance console.

## Task Intake

- `primary_objective`: localize and restyle the thin governance console while proving the existing control-plane actions still work from the page.
- `not_doing`: no second scheduler, no business runtime changes, no new persistence, no product UI.
- `stage_scope`: governance operator experience only.
- `impact_modules`:
  - `docs/governance/AUTOMATION_INTENTS.yaml`
  - `scripts/governance_console.py`
  - `tests/governance/test_governance_console.py`
  - `docs/governance/tasks/TASK-GOV-063.md`
  - `docs/governance/runlogs/TASK-GOV-063-RUNLOG.md`
  - `docs/governance/handoffs/TASK-GOV-063.yaml`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- The governance console first screen is fully operator-oriented Chinese UI and no longer reads like a generic browser-shell page.
- Candidate pool rows can show candidate tasks with Chinese labels and English identifiers together.
- The existing compile, refresh, close-ready-execution, continue-roadmap, explain-claim-decision, explain-candidate, explain-release-chain, and review-candidate-pool flows remain reachable from the console.
- Real browser verification confirms the page buttons successfully call the existing governance control-plane actions without adding a second scheduler.
- The automation intent catalog remains valid YAML so task-window and roadmap-window phrases can still be preflighted from execution windows.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-063.md`
- `docs/governance/runlogs/TASK-GOV-063-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-063.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/AUTOMATION_INTENTS.yaml`
- `scripts/governance_console.py`
- `scripts/governance_runtime.py`
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
- `branch`: `codex/TASK-GOV-063-console-refresh-no-window-fix`
- `updated_at`: `2026-04-09T18:03:36+08:00`
<!-- generated:task-meta:end -->
