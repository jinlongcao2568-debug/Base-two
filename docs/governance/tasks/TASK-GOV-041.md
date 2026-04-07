# TASK-GOV-041 Route roadmap continuation intent to claim-next

## Task Baseline

- `task_id`: `TASK-GOV-041`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-claim-next-routing-v1`
- `branch`: `codex/TASK-GOV-041-roadmap-claim-next-routing`
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

- Add a highest-priority automation intent for `持续按路线图开发`.
- Route that intent to `python scripts/task_ops.py claim-next --write-claim`.
- Add preflight support that uses `claim-next` dry-run and returns the selected candidate without mutating formal task ledgers.
- Preserve existing `continue-current`, `continue-roadmap`, publish, and automation runner behavior.

## Explicitly Not Doing

- Do not create formal task packages, branches, worktrees, pushes, PRs, or merges from the intent preflight.
- Do not replace the legacy `continue-roadmap` path for old phrases; only the new highest-priority claim phrase is routed to `claim-next`.
- Do not alter business code under `src/`, contracts under `docs/contracts/`, migrations, stage6 facts behavior, or customer-visible outputs.

## Allowed Dirs

- `.codex/local/roadmap_candidates/`
- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `.codex/local/roadmap_candidates/`
- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `pytest tests/governance/test_automation_intent.py -q`
- `pytest tests/automation/test_automation_runner.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`
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
- `branch`: `codex/TASK-GOV-041-roadmap-claim-next-routing`
- `updated_at`: `2026-04-07T20:24:54+08:00`
<!-- generated:task-meta:end -->
