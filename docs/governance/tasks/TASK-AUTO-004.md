# TASK-AUTO-004 最小真实业务链与自动开发基线

## Task Baseline

- `task_id`: `TASK-AUTO-004`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `automation-minimal-runtime-chain-v1`
- `branch`: `feat/TASK-AUTO-004-minimal-runtime-chain`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
## Primary Goals

- implement the first deterministic local runtime chain across `stage1 -> stage2 -> stage3 -> stage4 -> stage5 -> stage6 -> domain_public_chain`
- replace fixture-only consumption tests with `src/` runtime calls that still validate against the existing formal schemas and case fixtures
- add one explicit local execution entrypoint plus task-scoped execution playbook and acceptance policy for this chain only

## Explicitly Not Doing

- no external API or webhook registration; `docs/governance/INTERFACE_CATALOG.yaml` remains zero-state
- no release control plane, deploy orchestration, or runtime feedback loop in this task
- no `stage7/stage8/stage9` implementation work beyond preserving downstream compatibility with `stage6` facts

## Allowed Dirs

- `src/stage1_orchestration/`
- `src/stage2_ingestion/`
- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage5_reporting/`
- `src/stage6_facts/`
- `src/domain/engineering/public_chain/`
- `src/shared/contracts/`
- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/contracts/`
- `tests/integration/`
- `docs/governance/`
- `scripts/`

## Planned Write Paths

- `src/stage1_orchestration/`
- `src/stage2_ingestion/`
- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage5_reporting/`
- `src/stage6_facts/`
- `src/domain/engineering/public_chain/`
- `src/shared/contracts/`
- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/contracts/`
- `tests/integration/`
- `docs/governance/`
- `scripts/`

## Planned Test Paths

- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/contracts/`
- `tests/integration/`

## Required Tests

- `python scripts/check_authority_alignment.py`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `pytest tests/governance -q`
- `pytest tests/automation -q`
- `pytest tests/contracts -q`
- `pytest tests/integration -q`
- `pytest -q`

## Reserved Paths

- none
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
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-AUTO-004-minimal-runtime-chain`
- `updated_at`: `2026-04-05T11:29:09+08:00`
<!-- generated:task-meta:end -->
