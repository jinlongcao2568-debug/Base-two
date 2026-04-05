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
- If `CURRENT_TASK.yaml` is in `idle`, use `continue-roadmap` or explicit activation before implementation.
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

- `python scripts/automation_intent.py preflight --utterance "<text>"`
  - performs a non-mutating preflight for free-form continuation requests
  - may recognize broader natural-language continue requests
  - still routes only to the two formal intents below
  - blocks instead of guessing when the request could imply a task switch
- `python scripts/automation_intent.py execute --utterance "<text>"`
  - reruns the same preflight
  - delegates only when preflight returns `ready`
- `python scripts/task_ops.py continue-current`
  - keep or reactivate the live current task
  - may also close a review-ready live current task back to the formal idle state
  - fails from the formal idle state
  - never selects a successor
- `python scripts/task_ops.py continue-roadmap`
  - closes a review-ready live task when the worktree starts clean
  - may also resume directly from the formal idle state
  - then resolves the next unique successor from roadmap policy or approved blueprints
- `python scripts/automation_runner.py once --continue-roadmap --prepare-worktrees`
  - runs the normal repository gates first
  - executes `continue-roadmap`
  - prepares child worktrees and review-bundle closeout when the live task is a `parallel_parent`

## Business Autopilot Limits

- Automatic business successor generation follows the stage order declared in `docs/governance/MODULE_MAP.yaml` and the live roadmap policy.
- The formal implementation truth for business automation is:
  - baseline authority
  - formal contracts
  - the generated task package
- `stage7-stage9` are downstream-only stages; they may be generated or activated only when `stage6_facts` and any additional declared dependencies are already satisfied.
- `stage7-stage9` also require `docs/governance/CAPABILITY_MAP.yaml` to declare `stage7_to_stage9_business_automation: implemented` before automation may generate those lanes.

## Prompt Governance

- The prompt source of truth is `docs/governance/PROMPT_MODULE_CATALOG.yaml` and `docs/governance/prompt_modules/`.
- Generated runtime prompt outputs live under `docs/governance/runtime_prompts/`.
- Root-level scratch prompt notes are not live prompt inputs.
- Load only the role modules required by the active lane instead of pasting a full memo into every prompt.
- App-level custom instructions are not a governance execution source.
- Keep app-level custom instructions empty by default; if they exist, they may only carry language or output-style preferences.

## Closeout Rules

- Record executed tests in the task runlog.
- Use `python scripts/task_ops.py can-close` before closing.
- Do not leave the live current task in `done`; either keep it `doing` while work continues or move it to `review` when implementation is complete and no new writes are expected.
- Closing a live top-level coordination task without immediate successor activation must write the formal idle payload into `CURRENT_TASK.yaml`.
- The idle closeout state must also set roadmap frontmatter to `current_task_id: null` and `current_phase: idle`, and leave no active coordination worktree entry.
- Do not auto-switch to a successor when the worktree is dirty.
- Autonomous child closeout is allowed only after the full review bundle passes.

## Exception Rule

- Any boundary exception must be registered before implementation.
- No unregistered exception may be merged into the live baseline.
