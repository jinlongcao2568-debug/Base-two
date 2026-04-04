# AX9S Operator Manual

Derived from:
- `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md`

Conflict rule:
- This file is the live execution manual for repository work.
- It expands the baseline execution manual and must never weaken it.

## Read Order

1. `docs/product/AUTHORITY_SPEC.md`
2. `docs/governance/OPERATOR_MANUAL.md`
3. `docs/governance/CURRENT_TASK.yaml`
4. the current task file
5. the current task runlog

## Start Rules

- Do not implement without a live `current_task_id`.
- Do not modify files outside the current task's `allowed_dirs`.
- Do not bypass stage 6 or introduce a second truth surface.
- Run:
  - `python scripts/validate_contracts.py`
  - `python scripts/check_repo.py`
  - `python scripts/check_hygiene.py`

## Required Output Before Implementation

- task understanding
- stage and module impact
- allowed and forbidden paths
- planned file list
- planned tests
- risk summary

## Closeout Rules

- Record executed tests in the task runlog.
- Use `python scripts/task_ops.py can-close` before closing.
- Do not leave the live current task in `done`; either keep it `doing` while work continues or move it to `review` when implementation is complete and no new writes are expected.

## Exception Rule

- Any boundary exception must be registered before implementation.
- No unregistered exception may be merged into the live baseline.
