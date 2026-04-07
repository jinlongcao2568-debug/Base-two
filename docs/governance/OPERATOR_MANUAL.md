# AX9S Operator Manual

Derived from:
- `docs/baseline/AX9S_寤鸿宸ョ▼鍩熺爺鍙慱Codex_鎵ц鎵嬪唽_涓浗钀藉湴鍞崠澧炲己鐗坃V1.4_2026-04-02.md`

Conflict rule:
- This file is the live execution manual for repository work.
- It expands the baseline execution manual and must never weaken it.

## Read Order

1. `docs/product/AUTHORITY_SPEC.md`
2. `docs/governance/OPERATOR_MANUAL.md`
3. `docs/governance/LIVE_GOVERNANCE_BOUNDARY.md`
4. `docs/governance/CURRENT_TASK.yaml`
5. the current task file
6. the current task runlog

## Start Rules

- Do not implement without a live `current_task_id`.
- If `CURRENT_TASK.yaml` is in `idle`, use `continue-roadmap` or explicit activation before implementation.
- Do not modify files outside the current task's `allowed_dirs`.
- Do not bypass stage 6 or introduce a second truth surface.
- Before implementation, run the task baseline checks that match the active phase.

## Governance Test Trigger Rules

- `pytest tests/governance -q` is a governance-mode regression suite, not a default gate for ordinary business or low-risk governance edits.
- `pytest tests/automation -q` is an automation-runner regression suite, not a default gate for ordinary business or low-risk governance edits.
- Governance tasks must resolve tests by path-triggered profile, not by broad governance identity alone.
- Default governance trigger profiles:
  - `governance_fast`: ordinary docs, ledgers, and low-risk governance metadata
  - `governance_workflow`: continuation, lease, handoff, closeout, orchestration workflow
  - `governance_publish`: publish, preflight, automation intent, release flow
  - `automation_runner`: runner, dispatch, cleanup pressure, orchestration runtime
  - `full_governance_release`: policy-core and release-grade gate changes
- Only `full_governance_release` should require full `tests/governance -q` and `tests/automation -q` by default.
- To benefit from selective governance test triggering, governance tasks should prefer precise file-level `planned_write_paths` over only broad directory roots.

## Live vs Historical Governance Sources

- `docs/governance/LIVE_GOVERNANCE_BOUNDARY.md` is the live boundary for operator and prompt search.
- Historical task files, runlogs, handoffs, and registry rows are audit artifacts.
- `docs/governance/TASK_REGISTRY.yaml` remains a live ledger, but closed rows and their `required_tests` are still historical evidence.
- Do not derive the current default gate from historical `required_tests` records.
- If historical artifacts conflict with the live governance surfaces, the live governance surfaces win for current execution.

## Required Output Before Implementation

- task understanding
- stage and module impact
- allowed and forbidden paths
- planned file list
- planned tests
- risk summary

## Continuation Commands

- `python scripts/task_ops.py queue-and-activate TASK-ID ...`
  - preferred entry when creating and immediately activating a new top-level coordination task
  - performs branch create/switch, task package creation, current-task activation, worktree ledger sync, roadmap sync, and handoff creation in one governed command
  - fails before writing task artifacts when a branch switch is required and the worktree is dirty
  - use `--existing-ok` only to repair an already queued coordination task into the same activation path
- `python scripts/task_ops.py derive-ledgers --from current-task --write`
  - repairs live registry, worktree, roadmap, and generated task/runlog metadata from `CURRENT_TASK.yaml`
  - dry-runs unless `--write` is provided
- `python scripts/task_ops.py derive-ledgers --from task-file --task-id TASK-ID --write`
  - repairs ledger state from an existing task file and registry row
  - closed task files may repair their own historical ledger row, but must not overwrite an unrelated live `CURRENT_TASK.yaml`
  - non-closed task files may derive live state only when the control plane is idle or already points to the same task
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
- Historical task files, runlogs, handoffs, and registry rows are audit artifacts, not live prompt inputs.
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
