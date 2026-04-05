# TASK-AUTO-004 最小真实业务链与自动开发基线

## Task Baseline

- `task_id`: `TASK-AUTO-004`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `queued`
- `stage`: `automation-minimal-runtime-chain-v1`
- `branch`: `feat/TASK-AUTO-004-minimal-runtime-chain`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
## Primary Goals

- to-be-filled

## Explicitly Not Doing

- to-be-filled

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

- to-be-filled
## Narrative Assertions

- `narrative_status`: `queued`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `not_started`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `activation_pending`

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `queued`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `idle`
- `topology`: `single_worker`
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-AUTO-004-minimal-runtime-chain`
- `updated_at`: `2026-04-05T09:29:01+08:00`
<!-- generated:task-meta:end -->
