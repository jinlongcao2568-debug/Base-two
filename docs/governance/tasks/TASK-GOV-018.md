# TASK-GOV-018 仓库治理总控不变前提下的子任务自动执行一期

> 状态说明：本文件为任务包草案，尚未激活。未获批准前，不得更新 `CURRENT_TASK.yaml`，也不得把本任务写入 live 执行入口。

## Task Baseline

- `task_id`: `TASK-GOV-018`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `draft`
- `stage`: `governance-hybrid-autonomy-phase1-v1`
- `branch`: `feat/TASK-GOV-018-hybrid-autonomy-phase1`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `immediate`

## Primary Goals

- Keep the current top-level governance model unchanged while making child execution tasks easier to prepare and recover.
- Reduce duplicated task state maintenance by moving registry data toward script-synchronized derived indexes.
- Add the first governed child-task execution primitives: child branch/worktree preparation, baseline checks, and registry/runlog synchronization.
- Formalize and implement the first AX9-compatible batch of absorbed AI coding workflow capabilities at the child-task layer:
  - design confirmation before implementation,
  - detailed execution planning,
  - strict test-first behavior for code tasks,
  - fresh execution context per child task,
  - ordered `spec review -> code quality review`,
  - standardized child-task finish workflow with manual parent-level approval remaining intact.

## Implementation Scope

- Clarify the source-of-truth split between `CURRENT_TASK.yaml`, task files, runlogs, `TASK_REGISTRY.yaml`, and `WORKTREE_REGISTRY.yaml`.
- Design and implement script-based synchronization so task and worktree registries can be rebuilt or reconciled from true governance sources.
- Add a governed child execution preparation flow that can:
  - derive a child execution context from a parent task,
  - create a child branch,
  - create a child worktree,
  - run baseline checks before implementation begins,
  - persist the prepared state back into registry and runlog surfaces.
- Add a child-task design-confirmation gate so implementation cannot start before goals, scope, allowed dirs, tests, and risk notes are explicit.
- Add a detailed execution-plan artifact or runtime payload that enumerates files, steps, tests, and verification actions for the child task.
- Add code-task-only strict test-first enforcement semantics to the governed child flow.
- Ensure every child task runs in a fresh execution context and carries independent review/closeout metadata.
- Split child review into two ordered gates:
  - `spec_review`
  - `quality_review`
- Define and implement a standardized child finish workflow that closes only the child lane and leaves parent closeout under manual governance control.
- Keep this phase restricted to governance-layer files, scripts, and governance/automation tests.

## Explicitly Not Doing

- Do not auto-switch `CURRENT_TASK.yaml`.
- Do not auto-close top-level coordination tasks.
- Do not auto-approve exceptions.
- Do not touch `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.
- Do not implement authority-critical business-lane execution in this phase.
- Do not add remote workers or external task sources.
- Do not turn parent closeout into full autopilot.
- Do not force strict test-first on pure documentation or registry-only tasks.

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

## Acceptance Criteria

- A governance design document exists that explains the new model without relying on conversation context.
- Registry roles are explicitly split into truth sources versus derived indexes.
- There is a governed path to prepare child branch/worktree state without changing the live top-level task.
- Drift between task truth sources and registry indexes can be detected and reconciled by script.
- Governance and automation tests cover the new synchronization and child preparation behavior.
- Child execution cannot begin until a design-confirmation gate passes.
- Child execution produces a detailed plan payload with files, tests, steps, and verification actions.
- Code-task child executions enforce test-first semantics.
- Child review order is enforced as `spec_review` before `quality_review`.
- Child finish workflow closes only the child lane while preserving manual parent closeout.

## Rollback Plan

- Revert the new synchronization logic and child preparation flow in one change set.
- Restore registry behavior to the previous manual-or-direct-write model.
- Remove any new governance-only metadata fields that are not consumed by the previous runtime.
- Re-run governance baseline checks to confirm the prior control-plane behavior is restored.

## Activation Preconditions

- Current live task is formally closed or explicitly paused according to governance policy.
- The draft is reviewed and approved as the next governance task.
- No conflicting top-level coordination task is activated.

## Suggested First Commands On Activation

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance -q`
- `pytest tests/automation -q`

## Planned Deliverables

- governance design updates describing the absorbed child-task workflow capabilities
- script changes for registry synchronization and child preparation
- script or runtime changes for child design-confirmation and detailed planning
- review-state and finish-workflow updates for child lanes
- governance and automation tests for the new gates and ordering

## Narrative Assertions

- `narrative_status`: `draft`
- `closeout_state`: `not_started`
- `blocking_state`: `awaiting_activation`
- `completed_scope`: `none`
- `remaining_scope`: `full`
- `next_gate`: `approval_required`
