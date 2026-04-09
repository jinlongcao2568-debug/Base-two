# TASK-GOV-016 本地多 Lane 执行调度

## Task Baseline

- `task_id`: `TASK-GOV-016`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-local-multi-agent-dispatch-v1`
- `branch`: `feat/TASK-GOV-016-local-multi-agent-dispatch`
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

- Turn prepared execution worktrees into dispatched local lane agents with bounded prompts and runtime tracking.
- Extend `automation_runner` from orchestration-only behavior into local multi-lane dispatch, monitoring, and closeout handling.
- Keep the v1 scope limited to one machine, one physical worker registry entry, and up to four lanes.

## Implementation Scope

- Add execution-lane runtime fields to `WORKTREE_REGISTRY.yaml` so the runner can recover from registry state alone.
- Extend `.codex/local/EXECUTION_CONTEXT.yaml` with lane metadata and the governed worker runtime prompt profile.
- Add `worker-heartbeat` as a runtime-only command that updates liveness without polluting runlog narrative sections.
- Add a governed local launcher that materializes execution context, emits `worker-start`, and records the first heartbeat.
- Extend `automation_runner` to dispatch launchers, detect stale lane heartbeats, and preserve parent isolation when only one lane fails.

## Explicitly Not Doing

- Do not add remote workers or external task sources in v1.
- Do not change Git publish policy or make publish implicit.
- Do not broaden execution beyond the governed local multi-worktree topology.

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
- `branch`: `feat/TASK-GOV-016-local-multi-agent-dispatch`
- `updated_at`: `2026-04-09T18:03:36+08:00`
<!-- generated:task-meta:end -->
