# TASK-GOV-024 治理收口升级：closeout lease 自动闭环与运行契约统一

## Task Baseline

- `task_id`: `TASK-GOV-024`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-closeout-lease-runtime-contracts-v1`
- `branch`: `feat/TASK-GOV-024-closeout-lease-runtime-contracts`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
## Primary Goals

- Implement the remaining governance upgrades in one bounded task: automatic closeout/lease closure, child closeout ledger reconciliation, and Python/runtime execution contract unification.
- Remove the need for operator-side manual `takeover` knowledge during closeout-ready flows.
- Stabilize governed child execution so mirrored governance files and missing worktree paths no longer produce false blocked states.

## Explicitly Not Doing

- Do not change customer-visible APIs, business-stage semantics, or any data contracts under `docs/contracts/`.
- Do not modify `src/` business logic, migrations, or `tests/integration/`.
- Do not roll back the already-landed idle semantics, authority-alignment regression, or slow-test optimizations from `TASK-GOV-021/022/023`.

## Task Intake

- `primary_objective`: finish the remaining governance bundle by closing the closeout/lease gap and formalizing the runtime/subprocess contract.
- `not_doing`: no customer-visible behavior changes, contract changes, migrations, or business-stage logic edits.
- `stage_scope`: governance control-plane and test/runtime support only.
- `impact_modules`:
  - `scripts/task_coordination_lease.py`
  - `scripts/task_lifecycle_ops.py`
  - `scripts/task_continuation_ops.py`
  - `scripts/task_worker_ops.py`
  - `scripts/task_worktree_ops.py`
  - `scripts/child_execution_flow.py`
  - `scripts/governance_repo_checks.py`
  - `scripts/task_handoff.py`
  - `README.md`
  - `pyproject.toml`
  - `requirements-dev.txt`
  - `tests/governance/test_coordination_lease.py`
  - `tests/governance/test_parallel_closeout_pipeline.py`
  - `tests/governance/test_task_continuation.py`
  - `tests/governance/test_authority_alignment.py`
  - `tests/governance/test_task_ops.py`
  - `tests/automation/test_automation_runner.py`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- Closeout-ready `continue-current` / `continue-roadmap` / `close` no longer require a manual pre-`takeover`.
- `auto-close-children` succeeds when a child worktree is missing but the child branch is already merged and review evidence is complete.
- Governed child execution contexts and mirrored governance files no longer trigger false authority/repo failures.
- Root runtime contract is formally declared via `pyproject.toml`, and governance Python subprocesses run via the current interpreter without `shell=True`.

## Rollback Plan

- Revert the governance control-plane scripts and tests changed by this task.
- Remove `pyproject.toml` and restore `README.md` / `requirements-dev.txt` to the pre-task runtime contract text if the new contract causes breakage.
- Re-run the required governance and automation tests to confirm the repository returns to the pre-task behavior.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `README.md`
- `pyproject.toml`
- `requirements-dev.txt`

## Planned Write Paths

- `docs/governance/`
- `scripts/task_coordination_lease.py`
- `scripts/task_lifecycle_ops.py`
- `scripts/task_continuation_ops.py`
- `scripts/task_worker_ops.py`
- `scripts/task_worktree_ops.py`
- `scripts/child_execution_flow.py`
- `scripts/governance_repo_checks.py`
- `scripts/task_handoff.py`
- `README.md`
- `pyproject.toml`
- `requirements-dev.txt`
- `tests/governance/test_coordination_lease.py`
- `tests/governance/test_parallel_closeout_pipeline.py`
- `tests/governance/test_task_continuation.py`
- `tests/governance/test_authority_alignment.py`
- `tests/governance/test_task_ops.py`
- `tests/automation/test_automation_runner.py`

## Planned Test Paths

- `tests/governance/test_coordination_lease.py`
- `tests/governance/test_parallel_closeout_pipeline.py`
- `tests/governance/test_task_continuation.py`
- `tests/governance/test_authority_alignment.py`
- `tests/governance/test_task_ops.py`
- `tests/automation/test_automation_runner.py`
- `tests/automation/test_high_throughput_runner.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/task_ops.py split-check TASK-GOV-024`
- `python scripts/check_repo.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_coordination_lease.py tests/governance/test_parallel_closeout_pipeline.py tests/governance/test_task_continuation.py tests/governance/test_authority_alignment.py tests/governance/test_task_ops.py -q`
- `pytest tests/automation/test_automation_runner.py tests/automation/test_high_throughput_runner.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
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
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-024-closeout-lease-runtime-contracts`
- `updated_at`: `2026-04-09T12:08:35+08:00`
<!-- generated:task-meta:end -->
