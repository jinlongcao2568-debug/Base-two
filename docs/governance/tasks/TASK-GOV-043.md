# TASK-GOV-043 Roadmap stale takeover and publish hardening

## Task Baseline

- `task_id`: `TASK-GOV-043`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-takeover-publish-hardening-v1`
- `branch`: `codex/TASK-GOV-043-roadmap-takeover-publish-hardening`
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

- Allow safe takeover of stale promoted roadmap tasks instead of forcing a lower-priority new claim.
- Block stale takeover when the promoted worktree is dirty or otherwise unsafe.
- Recreate a missing promoted worktree when the branch/task is still reclaimable.
- Harden publish preflight so a branch that is behind its upstream is blocked before push or publish.

## Explicitly Not Doing

- Do not implement automatic checkpointing of dirty stale worktrees; unsafe stale takeovers remain blocked.
- Do not add force-push, remote overwrite, or automatic merge behavior.
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

- `pytest tests/governance/test_roadmap_takeover.py -q`
- `pytest tests/governance/test_roadmap_claim_promotion.py -q`
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
- `branch`: `codex/TASK-GOV-043-roadmap-takeover-publish-hardening`
- `updated_at`: `2026-04-09T17:02:25+08:00`
<!-- generated:task-meta:end -->
