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

## Continuation Commands

- `python scripts/task_ops.py continue-current`
  - keep or reactivate the live current task
  - never selects a successor
- `python scripts/task_ops.py continue-roadmap`
  - closes a review-ready live task when the worktree starts clean
  - then resolves the next unique successor from roadmap policy or the approved governance blueprint
- `python scripts/automation_runner.py once --continue-roadmap`
  - runs the normal repository gates first
  - then executes `continue-roadmap`

## Closeout Rules

- Record executed tests in the task runlog.
- Use `python scripts/task_ops.py can-close` before closing.
- Do not leave the live current task in `done`; either keep it `doing` while work continues or move it to `review` when implementation is complete and no new writes are expected.
- Do not auto-switch to a successor when the worktree is dirty.
- Do not auto-generate business implementation tasks from the roadmap in v1.

## Exception Rule

- Any boundary exception must be registered before implementation.
- No unregistered exception may be merged into the live baseline.
