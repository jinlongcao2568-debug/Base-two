# TASK-GOV-061 Thin governance operator console and desktop shortcut

## Task Baseline

- `task_id`: `TASK-GOV-061`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-operator-console-v1`
- `branch`: `codex/TASK-GOV-061-governance-console`
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

- Add a thin local governance operator console page that displays candidate pool health, claim reasoning, and release-chain explanations without introducing a second scheduler.
- Expose the existing governance commands through a minimal browser-based control surface and preserve command-driven truth.
- Create a desktop shortcut that can launch the local console at any time with one double-click.

## Explicitly Not Doing

- Do not move scheduler logic into the page or browser.
- Do not change business logic under `src/`, contracts, or DB schema.
- Do not add persistent server-side state, a new database, or a second control-plane truth source.

## Task Intake

- `primary_objective`: provide a local browser console and desktop shortcut for the governance control plane.
- `not_doing`: no product UI and no second scheduler.
- `stage_scope`: governance operator experience only.
- `impact_modules`:
  - `scripts/governance_console.py`
  - `tests/governance/test_governance_console.py`
  - desktop shortcut `C:/Users/92407/Desktop/AX9 Governance Console.lnk`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- The local governance console serves successfully on localhost and returns HTTP 200.
- Double-clicking `C:/Users/92407/Desktop/AX9 Governance Console.lnk` launches the console entrypoint.
- The page can trigger compile, refresh, close-ready-execution, and continue-roadmap actions.
- The page can display candidate pool explanation, claim decision explanation, single-candidate explanation, and release-chain explanation.

## Task Intake

- `primary_objective`: provide a thin local operator console and a desktop shortcut so the governance control plane can be opened and used without memorizing CLI commands.
- `not_doing`: no second scheduler, no business runtime changes, no product UI.
- `stage_scope`: governance operator experience only.
- `impact_modules`:
  - `scripts/governance_console.py`
  - `tests/governance/test_governance_console.py`
  - desktop shortcut `C:/Users/92407/Desktop/AX9 Governance Console.lnk`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- Double-clicking the desktop shortcut launches the local operator console.
- The console page can trigger compile, refresh, close-ready-execution, and continue-roadmap actions.
- The console can display candidate pool explanation, claim decision explanation, candidate explanation, and release-chain explanation.
- The page remains a thin control surface and does not implement a second scheduler.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/tasks/TASK-GOV-061.md`
- `docs/governance/runlogs/TASK-GOV-061-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-061.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `scripts/governance_console.py`
- `tests/governance/test_governance_console.py`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance/test_governance_console.py -q`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`

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
- `branch`: `codex/TASK-GOV-061-governance-console`
- `updated_at`: `2026-04-08T16:59:32+08:00`
<!-- generated:task-meta:end -->
