# TASK-GOV-018 Single Total Upgrade Parent Task: ai_guarded closeout / continuation / contracts-runtime hardening

## Task Baseline

- `task_id`: `TASK-GOV-018`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-hybrid-autonomy-parented-total-upgrade-v1`
- `branch`: `feat/TASK-GOV-018-parented-stability-upgrade`
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

- Promote `TASK-GOV-018` into the only top-level parent task for the whole upgrade.
- Move top-level closeout and continuation from manual closeout to guarded `ai_guarded` behavior.
- Expand governed child workflow from governance-only paths into contracts, shared contracts, stage7-stage9 runtime, migrations, and integration validation.
- Land contract-owned runtime acceptance, minimal stage7-stage9 runtime consumers, stateless migration baseline, and runtime smoke validation without rewriting `src/stage6_facts/`.
- Graduate eligible heavy blueprints to `autonomous + parallel_parent + up to 4 lanes` only after soak validation succeeds.

## Explicitly Not Doing

- Do not create a sibling top-level task for governance, compatibility, soak, or graduation.
- Do not rewrite or back-write `src/stage6_facts/`.
- Do not create a second fact layer, second truth layer, or second customer-facing interpretation surface.
- Do not enable unconditional full autopilot.
- Do not allow ambiguous, dependency-blocked, or scope-unclear roadmap continuation.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `docs/contracts/`
- `src/shared/contracts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `db/migrations/`
- `tests/contracts/`
- `tests/integration/`
- `tests/fixtures/downstream/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `.gitignore`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `docs/contracts/`
- `src/shared/contracts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `db/migrations/`
- `tests/contracts/`
- `tests/integration/`
- `tests/fixtures/downstream/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `.gitignore`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`
- `tests/contracts/`
- `tests/integration/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `python scripts/check_authority_alignment.py`
- `python scripts/validate_contracts.py`
- `pytest tests/governance -q`
- `pytest tests/automation -q`
- `pytest tests/contracts -q`
- `pytest tests/integration -q`
- `pytest tests/stage7 -q`
- `pytest tests/stage8 -q`
- `pytest tests/stage9 -q`
- `pytest -q`

## Reserved Paths

- `src/stage1_orchestration/`
- `src/stage2_ingestion/`
- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage5_reporting/`
- `src/stage6_facts/`

## Dependencies

- `TASK-GOV-017`

## Phase Gates

### Phase 1: `phase_1_rebaseline_task_scope`

- Expand `TASK-GOV-018` into the single total-upgrade parent task.
- Absorb `TASK-BIZ-001/002/003`, `TASK-SOAK-001`, and `TASK-GRAD-001`.
- Align `CURRENT_TASK.yaml`, roadmap, task registry, worktree registry, task file, and runlog.

### Phase 2: `phase_2_top_level_ai_guarded_closeout`

- Change top-level closeout policy from `manual` to `ai_guarded`.
- Allow `continue-current` to close the current top-level task back to idle without activating a successor.
- Allow `continue-roadmap` and roadmap runner continuation only when successor uniqueness, dependencies, and boundaries are all satisfied.

### Phase 3: `phase_3_expand_child_workflow_scope`

- Apply governed child workflow gates to contracts, shared contracts, stage7-stage9 runtime, migrations, and integration tests.
- Keep `src/stage1_orchestration/` through `src/stage6_facts/` reserved.
- Keep lane ceiling fixed at `4` with single-writer rules on `db/migrations/` and each stage7/8/9 subsystem.

### Phase 4: `phase_4_runtime_contract_decoupling`

- Replace governance-owned runtime acceptance inputs with a contract-owned acceptance artifact.
- Land minimal deterministic runtime consumers for `stage7_sales`, `stage8_contact`, and `stage9_delivery`.
- Keep runtime consumption downstream-only from `stage6 project_fact`.

### Phase 5: `phase_5_migration_and_integration_hardening`

- Add an explicit stateless baseline migration pack.
- Upgrade integration validation from handoff-only checks to runtime smoke.
- Add minimal runtime and contract tests for stage7, stage8, and stage9.

### Phase 6: `phase_6_soak_and_parallel_graduation`

- Run roadmap runner soak, heartbeat, restart, orphan cleanup, and multi-lane dispatch validation.
- Graduate eligible heavy blueprints to `autonomous + parallel_parent` only after soak success.
- Keep the lane ceiling fixed at `4`.

## Absorbed Backlog

- `TASK-BIZ-001`: absorbed into phase 4 and phase 5.
- `TASK-BIZ-002`: absorbed into phase 2 and phase 3.
- `TASK-BIZ-003`: absorbed into phase 4 and phase 5.
- `TASK-SOAK-001`: absorbed into phase 6.
- `TASK-GRAD-001`: absorbed into phase 6.

## Acceptance Criteria

- All six internal gates are done.
- `TASK-GOV-018` remains the only top-level parent task throughout the upgrade.
- Top-level `ai_guarded` closeout and guarded roadmap continuation are covered by automated evidence.
- Runtime acceptance reads only the contract-owned artifact.
- Stage7-stage9 minimal runtime, stateless migration baseline, and integration smoke all pass.
- No registry drift or open child lane remains at final closeout.

## Rollback Plan

- Revert the total-upgrade rebaseline and restore the previous governance-only scope.
- Restore top-level parent closeout semantics to the prior control-plane behavior.
- Remove stage7-stage9 runtime/migration/integration additions if later phases are rolled back.
- Re-run governance baseline checks after rollback.

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
- `reserved_paths`: `src/stage1_orchestration/, src/stage2_ingestion/, src/stage3_parsing/, src/stage4_validation/, src/stage5_reporting/, src/stage6_facts/`
- `branch`: `feat/TASK-GOV-018-parented-stability-upgrade`
- `updated_at`: `2026-04-06T14:12:09+08:00`
<!-- generated:task-meta:end -->
