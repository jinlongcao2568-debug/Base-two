# AX9S Operator Manual

Derived from:
- `docs/baseline/AX9S_寤鸿宸ョ▼鍩熺爺鍙慱Codex_鎵ц鎵嬪唽_涓浗钀藉湴鍞崠澧炲己鐗坃V1.4_2026-04-02.md`

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
- If `CURRENT_TASK.yaml` is in `idle`, use `continue-roadmap` or explicit activation before implementation.
- Do not modify files outside the current task's `allowed_dirs`.
- Do not bypass stage 6 or introduce a second truth surface.
- Before implementation, run the task baseline checks that match the active phase.

## Required Output Before Implementation

- task understanding
- stage and module impact
- allowed and forbidden paths
- planned file list
- planned tests
- risk summary

## Continuation Commands

- `python scripts/automation_intent.py preflight --utterance "<text>"`
  - performs a non-mutating preflight for free-form continuation requests
  - blocks instead of guessing when the request could imply a task switch
- `python scripts/automation_intent.py execute --utterance "<text>"`
  - reruns the same preflight
  - delegates only when preflight returns `ready`
- `python scripts/task_ops.py continue-current`
  - keeps or reactivates the live current task
  - may auto-close the current top-level task back to formal `idle` only when `ai_guarded` closeout requirements are satisfied
  - never activates a successor
- `python scripts/task_ops.py continue-roadmap`
  - may auto-close the current top-level task when `ai_guarded` closeout is satisfied
  - may activate the next task only when the successor is unique, dependencies are satisfied, and the boundary is explicit
  - otherwise stops and reports blockers
- `python scripts/automation_runner.py once --continue-roadmap --prepare-worktrees`
  - runs repository gates first
  - executes guarded `continue-roadmap`
  - prepares child worktrees and review-bundle closeout when the live task is a `parallel_parent`

## Business Autopilot Limits

- Automatic business successor generation follows the stage order declared in `docs/governance/MODULE_MAP.yaml` and the live roadmap policy.
- `stage7-stage9` remain downstream-only stages.
- They may consume `stage6 project_fact`, but may not rewrite `src/stage6_facts/` or create a second truth layer.
- Stage7-stage9 autonomous/parallel rollout is blocked until `TASK-GOV-018` phase 6 soak and graduation gates pass.

## Prompt Governance

- The prompt source of truth is `docs/governance/PROMPT_MODULE_CATALOG.yaml` and `docs/governance/prompt_modules/`.
- Generated runtime custom instructions live in `docs/governance/runtime_prompts/` and must stay derived from the governance catalog.
- Runtime prompt outputs remain derived artifacts and must not replace the governance source files.

## Closeout Rules

- Record executed tests in the task runlog.
- Use `python scripts/task_ops.py can-close` before closing.
- Do not leave the live current task in `done`.
- Top-level coordination closeout is `ai_guarded`, not unconditional manual closeout and not unconditional autopilot.
- `ai_guarded` closeout requires:
  - required tests fully pass
  - registry has no drift
  - no child lane remains open
  - review and closeout evidence is complete
  - task file, runlog, design doc, and CURRENT_TASK agree
  - no pending exception approval exists
  - no unresolved high-risk blocker remains
- Manual intervention is still required when:
  - development direction changes
  - scope expands or a new feature is introduced
  - a new exception is required
  - the successor is not unique
  - dependencies are not satisfied
  - a high-risk conflict remains unresolved
- Closing a live top-level coordination task without immediate successor activation must write the formal idle payload into `CURRENT_TASK.yaml`.
- Autonomous child closeout remains allowed only after the full review bundle passes.

## Exception Rule

- Any boundary exception must be registered before implementation.
- No unregistered exception may be merged into the live baseline.
