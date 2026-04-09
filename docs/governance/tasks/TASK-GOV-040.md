# TASK-GOV-040 Roadmap claim-next locks and preflight

## Task Baseline

- `task_id`: `TASK-GOV-040`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-claim-next-preflight-v1`
- `branch`: `codex/TASK-GOV-040-roadmap-claim-next-preflight`
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

- Add a deterministic `claim-next` preflight command over the roadmap candidate index.
- Add a local scheduler lock and claim ledger under `.codex/local/roadmap_candidates/` so concurrent windows do not pick the same candidate.
- Exclude candidates blocked by dependencies, active claims, active task write-path overlap, single-writer roots, branch conflicts, or worktree registry conflicts.
- Return a clear blocker when no candidate is safe, without relying on free-form AI inference.

## Explicitly Not Doing

- Do not route the natural-language command `持续按路线图开发` into `claim-next`; that remains for `TASK-GOV-041`.
- Do not create or switch branches, create worktrees, mutate formal task packages for claimed candidates, push, open PRs, or merge.
- Do not alter business code under `src/`, contracts under `docs/contracts/`, migrations under `db/migrations/`, stage6 facts runtime behavior, or customer-visible outputs.

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

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

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
- `branch`: `codex/TASK-GOV-040-roadmap-claim-next-preflight`
- `updated_at`: `2026-04-09T16:18:58+08:00`
<!-- generated:task-meta:end -->
