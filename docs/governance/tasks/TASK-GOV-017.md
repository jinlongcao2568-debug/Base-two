# TASK-GOV-017 连续自治续跑与干净工作区治理

## Task Baseline

- `task_id`: `TASK-GOV-017`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-continuous-autonomy-clean-runtime-v1`
- `branch`: `feat/TASK-GOV-017-continuous-autonomy-clean-runtime`
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

- Introduce a continuation-aware dirty classifier so `continue-current`, review closeout, and `continue-roadmap` can distinguish governance-only drift, task-scoped checkpointable drift, and truly unsafe drift.
- Split tracked governance ledgers from runtime observation state by moving heartbeat, runner tick, and source observation data into `.codex/local/COORDINATION_RUNTIME.yaml` without changing formal closeout authority.
- Keep the existing single-cycle roadmap continuation entrypoint intact while adding an explicit continuous roadmap loop entrypoint and stop-reason reporting.
- Self-heal stale roadmap successor pointers and allow local checkpoint commits before cross-task continuation without pushing, opening PRs, stashing, or resetting.

## Implementation Scope

- Add dirty classification and checkpoint strategy reporting to continuation readiness and repository gate checks.
- Preserve tracked ledgers for formal task state, review closeout, and successor activation while moving heartbeat-style observation writes to the runtime layer.
- Harden `continue-roadmap` successor selection so stale explicit pointers fall back to formal immediate or generated successors instead of hard-failing on already-done pointers.
- Reduce governance and automation suite wall-clock time by caching initialized governance repos and replacing redundant test subprocess launches with opt-in inline test runners.

## Explicitly Not Doing

- Do not modify `src/`, `docs/contracts/`, `db/migrations/`, or `tests/integration/`.
- Do not change Stage 6 fact authority, publish rules, or customer-visible contracts.
- Do not introduce coordination worktrees, remote workers, or any implicit publish/push/PR flow for continuation.
- Do not let `.codex/local/` replace tracked ledgers as the source of truth for formal task state, closeout, or successor decisions.

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
- `branch`: `feat/TASK-GOV-017-continuous-autonomy-clean-runtime`
- `updated_at`: `2026-04-06T09:23:00+08:00`
<!-- generated:task-meta:end -->
