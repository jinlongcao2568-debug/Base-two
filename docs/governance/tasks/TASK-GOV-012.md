# TASK-GOV-012 coordination 单写者治理与安全接管

## Task Baseline

- `task_id`: `TASK-GOV-012`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-coordination-lease-v1`
- `branch`: `feat/TASK-GOV-012-coordination-lease`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
## Primary Goals

- Add a strict single-writer lease for top-level coordination tasks without persisting live lease state in repo-tracked ledgers.
- Implement governed `handoff`, `release`, and `takeover` commands with local runtime state and auditable task/runlog evidence.
- Make `continue-current` and `automation_intent execute` restore the recovery pack first, then block writes unless the current session owns the lease, the lease is stale, or an explicit takeover occurs.

## Explicitly Not Doing

- Do not change execution child isolation, worktree ownership, or parent/child closeout flow in this task.
- Do not persist live lease heartbeat/session state inside `CURRENT_TASK.yaml`, `TASK_REGISTRY.yaml`, or `WORKTREE_REGISTRY.yaml`.
- Do not modify product code under `src/`, contracts, migrations, or integration business-chain paths.

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
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-012-coordination-lease`
- `updated_at`: `2026-04-05T15:49:54+08:00`
<!-- generated:task-meta:end -->
