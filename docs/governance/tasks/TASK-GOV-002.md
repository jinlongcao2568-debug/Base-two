# TASK-GOV-002 测试热点 warning 预防性收口

## Task Baseline

- `task_id`: `TASK-GOV-002`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-test-maintainability-hardening-v1`
- `branch`: `feat/TASK-GOV-002-test-maintainability-hardening`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
## Primary Goals

- Remove the current hygiene warning hotspots in automation/governance tests without changing runtime behavior.
- Introduce stable scenario builders and assertion helpers so repeated task/worktree setup does not keep inflating individual test functions.
- Add a regression guard that keeps the current hotspot files out of future `check_hygiene.py` warning output.

## Explicitly Not Doing

- Do not change `scripts/check_hygiene.py` thresholds.
- Do not refactor runtime scripts or business implementation code.
- Do not chase low-value warnings outside the current hotspot files.

## Allowed Dirs

- `tests/governance/`
- `tests/automation/`
- `docs/governance/`

## Planned Write Paths

- `tests/governance/`
- `tests/automation/`
- `docs/governance/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `python scripts/check_authority_alignment.py`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `pytest tests/governance/test_check_hygiene.py -q`
- `pytest tests/governance -q`
- `pytest tests/automation -q`
- `pytest -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `tests/integration/`
- `scripts/check_hygiene.py`
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
- `reserved_paths`: `src/, docs/contracts/, tests/integration/, scripts/check_hygiene.py`
- `branch`: `feat/TASK-GOV-002-test-maintainability-hardening`
- `updated_at`: `2026-04-05T10:31:04+08:00`
<!-- generated:task-meta:end -->
