# TASK-GOV-018 单一顶层父任务下的分段稳定升级

## Task Baseline

- `task_id`: `TASK-GOV-018`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `doing`
- `stage`: `governance-hybrid-autonomy-parented-upgrade-v1`
- `branch`: `feat/TASK-GOV-018-parented-stability-upgrade`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`

## Primary Goals

- Keep `TASK-GOV-018` as the only top-level governance parent for the whole upgrade until child-task automation is runnable and stable.
- Move task and worktree registries toward script-synchronized derived indexes while preserving `CURRENT_TASK.yaml`, task files, and runlogs as truth sources.
- Land governed child execution preparation and the full first batch of AX9-compatible child workflow gates inside the governance layer.
- Finish this upgrade without turning on top-level full autopilot or multi-lane child execution rollout.

## Implementation Scope

- Formalize `TASK-GOV-018` as a long-running parent task with four explicit phase gates.
- Add registry drift detection and a reconciliation path driven by truth sources.
- Add child execution preparation that generates execution context, branch/worktree state, baseline evidence, and prepared-state registry/runlog updates.
- Add governed child workflow gates for:
  - design confirmation,
  - detailed execution planning,
  - code-task test-first,
  - fresh execution context,
  - ordered `spec_review -> quality_review`,
  - standardized child finish workflow.
- Keep all implementation inside `docs/governance/`, `scripts/`, `tests/governance/`, `tests/automation/`, and `.gitignore`.

## Explicitly Not Doing

- Do not auto-close the top-level parent task.
- Do not auto-switch to another top-level task after this task closes.
- Do not enable multi-lane or multi-agent child execution rollout in this task.
- Do not touch `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.
- Do not move authority-critical business execution into the governed child workflow in this phase.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.gitignore`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.gitignore`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance -q`
- `pytest tests/automation -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Dependencies

- `TASK-GOV-017`

## Phase Gates

### Phase 1: Control-Plane Truth Split

- `CURRENT_TASK.yaml`, task files, and runlogs are treated as primary truth sources.
- `TASK_REGISTRY.yaml` and `WORKTREE_REGISTRY.yaml` are treated as derived indexes with a reconciliation path.
- Drift detection and reconciliation are covered by governance tests.

### Phase 2: Child Preparation Flow

- Child execution preparation can derive execution context from the parent task.
- Child branch/worktree creation is automated inside the allowed dirs.
- Baseline checks run before implementation begins.
- Prepared state is written back into registry and runlog surfaces.

### Phase 3: Child Workflow Gates

- Child implementation cannot start before design confirmation passes.
- Child execution emits a detailed plan artifact or runtime payload.
- Code tasks enforce a test-first gate before implementation starts.
- Child review order is enforced as `spec_review` before `quality_review`.

### Phase 4: Child Finish and Stability Hardening

- Child finish runs through a standardized workflow that does not auto-close the parent task.
- Child closeout keeps top-level parent closeout under manual governance control.
- Recovery, rerun, blocked-lane, and edge-path behaviors are covered by tests.

## Acceptance Criteria

- `TASK-GOV-018` stays the only live top-level governance parent for the whole upgrade.
- A script can reconcile registry drift from `CURRENT_TASK.yaml`, task files, and runlogs.
- Child execution preparation can materialize execution context, worktree state, baseline evidence, and prepared-state metadata.
- Design confirmation, detailed planning, code-task test-first, ordered review, and child finish are all enforced by script or runtime gates.
- Governance and automation regressions pass with `TASK-GOV-018` active.

## Rollback Plan

- Revert the new reconciliation and child workflow gate logic in one change set.
- Restore the previous registry handling model and child execution lifecycle behavior.
- Re-run governance baseline checks to confirm the control plane returns to the previous behavior.

## Narrative Assertions

- `narrative_status`: `doing`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `validation_pending`

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `doing`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `branch`: `feat/TASK-GOV-018-parented-stability-upgrade`
<!-- generated:task-meta:end -->
