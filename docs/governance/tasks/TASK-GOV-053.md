# TASK-GOV-053 Module-graph roadmap scheduler transition and legacy dispatch retirement

## Task Baseline

- `task_id`: `TASK-GOV-053`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-module-graph-roadmap-scheduler-v1`
- `branch`: `codex/TASK-GOV-053-module-graph-roadmap-scheduler`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `5`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-053-5`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Replace hand-maintained roadmap candidate instances with compiler-generated module-root and preview-root candidates.
- Make compiled candidate graph plus shared evaluator the only roadmap dispatch truth for `claim-next`, `continue-roadmap`, and `automation_runner`.
- Remove roadmap dispatch authority from legacy planners and business autopilot generation paths.
- Keep `stage6_facts`, `stage7_sales`, `stage8_contact`, `stage9_delivery`, and `db/migrations/` as hard single-writer gates.
- Move execution review closeout to coordinator-driven release so candidate release no longer depends on worker self-close.

## Explicitly Not Doing

- Do not change business logic under `src/`.
- Do not change customer-visible contracts, field allowlists, region/source coverage, or DB schema.
- Do not introduce human approval review or legal/compliance workflow changes.
- Do not attempt full `stage2-9` child-slice materialization in this parent task.

## Task Intake

- `primary_objective`: upgrade the roadmap candidate system from a static backlog instance pool into a compiler-generated module graph with a single dispatch authority.
- `not_doing`: no business-stage implementation, no customer-visible contract changes, and no schema migration work.
- `stage_scope`: governance scheduler, coordination dispatch, and execution closeout only.
- `impact_modules`:
  - `docs/governance/ROADMAP_BACKLOG.yaml`
  - `docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml`
  - `docs/governance/MODULE_MAP.yaml`
  - `docs/governance/TASK_POLICY.yaml`
  - `docs/governance/tasks/TASK-GOV-053.md`
  - `docs/governance/tasks/TASK-GOV-054.md`
  - `docs/governance/tasks/TASK-GOV-055.md`
  - `docs/governance/tasks/TASK-GOV-056.md`
  - `scripts/`
  - `tests/governance/`
  - `tests/automation/`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- Fresh repo fixture exposes multiple root candidates at startup without manually completing `stage1`.
- `claim-next`, `continue-roadmap`, and `automation_runner --continue-roadmap` all use the same compiled candidate graph and evaluator output.
- Legacy roadmap dispatch generation in `task_coordination_planner` and `business_autopilot` no longer creates or chooses roadmap tasks.
- Review-ready execution tasks are closed by coordinator closeout before new roadmap claims are issued.
- Drift between `MODULE_MAP`, compiler output, evaluator, and runtime artifacts is detected and blocks dispatch.

## Sequential Child Tasks

- `TASK-GOV-054`: compile roadmap candidates from module graph
- `TASK-GOV-055`: unify roadmap dispatch and retire legacy planner authority
- `TASK-GOV-056`: coordinator-driven execution closeout and worker boundary hardening

## Rollback Plan

- Revert compiler, dispatch, and closeout changes together.
- Restore the current static roadmap candidate list and current evaluator input mode.
- Re-enable legacy roadmap dispatch only if the compiled graph path is fully rolled back.
- Regenerate `.codex/local/roadmap_candidates/index.yaml` and `summary.yaml` after rollback.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/roadmap_candidates/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/roadmap_candidates/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `pytest tests/governance/test_roadmap_candidate_compiler.py -q`
- `pytest tests/governance/test_roadmap_scheduler_eval.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`
- `pytest tests/governance/test_task_continuation.py -q`
- `pytest tests/governance/test_worker_self_loop.py -q`
- `pytest tests/automation/test_automation_runner.py -q`
- `pytest tests/governance/test_automation_intent.py -q`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`

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
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `5`
- `lane_index`: `null`
- `parallelism_plan_id`: `plan-TASK-GOV-053-5`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-053-module-graph-roadmap-scheduler`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
