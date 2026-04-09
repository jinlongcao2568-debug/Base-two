# TASK-GOV-039 Roadmap backlog candidate index generator

## Task Baseline

- `task_id`: `TASK-GOV-039`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-backlog-candidate-index-v1`
- `branch`: `codex/TASK-GOV-039-roadmap-backlog-candidate-index`
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

- Implement a deterministic candidate index generator for `ROADMAP_BACKLOG.yaml`.
- Validate core candidate dependencies, lane types, write paths, and hard gate metadata before generating the index.
- Emit a machine-readable `ROADMAP_CANDIDATES.yaml` snapshot that later `claim-next` work can read without re-parsing the full roadmap.
- Add focused governance regression tests for ready/waiting/blocked/claimed/stale candidate status derivation.

## Explicitly Not Doing

- Do not implement `claim-next`, scheduler locks, branch creation, worktree creation, push/publish behavior, or stale takeover mutation.
- Do not alter business code under `src/`, contracts under `docs/contracts/`, migrations under `db/migrations/`, or stage 1-9 runtime behavior.
- Do not change interface contracts, customer-visible delivery fields, region/source coverage registries, or stage6 facts semantics.

## Allowed Dirs

- `docs/governance/`
- `.codex/local/roadmap_candidates/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`
- `.codex/local/roadmap_candidates/`
- `scripts/`
- `tests/governance/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

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
- `branch`: `codex/TASK-GOV-039-roadmap-backlog-candidate-index`
- `updated_at`: `2026-04-09T17:21:54+08:00`
<!-- generated:task-meta:end -->
