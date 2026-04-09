# TASK-GOV-042 Roadmap claim promotion and worktree allocation

## Task Baseline

- `task_id`: `TASK-GOV-042`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-claim-promotion-worktree-v1`
- `branch`: `codex/TASK-GOV-042-roadmap-claim-promotion-worktree`
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

- Add `claim-next --promote-task` to turn a selected roadmap candidate into a formal `execution` task package.
- Allocate a unique branch and isolated worktree for the promoted candidate without switching the main coordination worktree.
- Update local claim metadata with the promoted task id and worktree path.
- Preserve `claim-next` dry-run and local-only `--write-claim` behavior.

## Explicitly Not Doing

- Do not implement stale takeover, remote divergence recovery, publish, PR, or merge behavior; those remain for `TASK-GOV-043`.
- Do not run business implementation in the promoted worker task.
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

- `pytest tests/governance/test_roadmap_claim_promotion.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`
- `pytest tests/governance/test_roadmap_candidate_index.py -q`
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
- `branch`: `codex/TASK-GOV-042-roadmap-claim-promotion-worktree`
- `updated_at`: `2026-04-09T18:03:36+08:00`
<!-- generated:task-meta:end -->
