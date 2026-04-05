# AX9S Automation Operating Model

## Scope

- The live automation layer now supports:
  - `automation_intent preflight/execute`
  - `continue-current`
  - `continue-roadmap`
  - dependency-aware business successor generation that follows the ordered stages in `docs/governance/MODULE_MAP.yaml`

## Intent Router

- `python scripts/automation_intent.py preflight --utterance "<text>"`
  - performs a non-mutating continuation preflight
  - supports governed free-form intent recognition
  - may resolve only to `continue-current` or `continue-roadmap`
  - must return `unsupported` or `blocked` when intent is ambiguous
- `python scripts/automation_intent.py execute --utterance "<text>"`
  - reruns the same preflight
  - executes the mapped command only when the preflight result is `ready`

## Continuation Semantics

### `continue-current`

- `doing`: keep the live current task and switch back to its branch if the worktree is clean enough to do so.
- `paused`: reactivate the live current task and restore its branch/worktree alignment.
- `blocked`: stop immediately and report the blocker.
- `idle`: stop immediately and require `continue-roadmap` or explicit activation.
- `review`: if the live task satisfies formal closeout rules, close it to the formal idle state and stop without selecting a successor.
- `done`: never remain as the live current state; require explicit repair or roadmap continuation.

### `continue-roadmap`

- `doing` or `paused`: continue the live current task; do not skip ahead.
- `blocked`: stop immediately and report the blocker.
- `review`: if `can-close` is satisfied and the worktree starts clean, close the live task and then resolve the next successor.
- `idle`: resolve the next successor directly without requiring a close step first.
- `done`: never remain as the live current state; closeout must already have written the formal idle payload.

## Successor Resolution Rules

- The roadmap frontmatter is the only live continuation policy source.
- Resolution order is:
  1. use `next_recommended_task_id` when it exists and is valid;
  2. otherwise generate a governance successor when the governance automation gap is still open;
  3. otherwise generate a business successor round when business automation is enabled and the business autopilot capability is implemented;
  4. otherwise stop with a no-successor report.
- A generated business successor round must:
  - obey `MODULE_MAP.yaml` dependency order;
  - respect the live roadmap scope and stage establishment policy;
  - keep `stage7-stage9` closed unless `stage7_to_stage9_business_automation` is implemented in `CAPABILITY_MAP.yaml`;
  - select at most 2 child execution lanes;
  - declare authority inputs, contract inputs, module scope, and review policy on each child task.

## Branch Switching Rules

- Automation may switch or create the target branch only when the worktree is clean before the continuation command starts.
- Automation must never auto-stash, auto-reset, or auto-discard dirty files.
- Target-branch behavior is:
  - existing branch: `git switch`
  - missing branch: `git switch -c`

## Review Bundle Rules

- Autonomous child closeout is allowed only after the review bundle passes inside the execution worktree.
- The review bundle must include:
  - `python scripts/check_repo.py`
  - `python scripts/check_hygiene.py`
  - `python scripts/validate_contracts.py` when the child touches contracts or formal objects
  - module tests from `TEST_MATRIX.yaml`
  - authority-critical integration tests when the child touches the live stage chain
- Review bundle failure must block only the failing lane unless every remaining lane is also closed or blocked.

## Prompt Runtime

- Prompt source of truth remains `docs/governance/PROMPT_MODULE_CATALOG.yaml` and `docs/governance/prompt_modules/`.
- Generated runtime prompts live under `docs/governance/runtime_prompts/`.
- Runtime prompts are derived artifacts and must be regenerated from the catalog instead of edited by hand.
- App-level custom instructions are not a governance execution source.
- Keep app-level custom instructions empty by default; if they are present, restrict them to language and output-style preferences.

## Automation Runner

- `python scripts/automation_runner.py once --continue-roadmap --prepare-worktrees` now means:
  1. run `check_repo.py`;
  2. run `check_hygiene.py`;
  3. execute `continue-roadmap` when requested, including from the formal idle state;
  4. prepare worktrees for the live `parallel_parent` task when allowed by automation mode;
  5. run `auto-close-children` for review-ready child lanes when allowed by automation mode;
  6. run the existing orphan cleanup logic.
- The runner still honors `manual`, `assisted`, and `autonomous` gating for parallel worktree preparation and child closeout.

## Stop Conditions

- dirty worktree before branch switch or successor activation
- blocked current task
- roadmap policy drift or missing continuation fields
- idle current payload drift or idle/worktree mismatch
- explicit successor missing from the registry
- multiple open top-level coordination successors
- unmet successor dependency
- incomplete successor boundary declaration
- review bundle failure on an autonomous child lane
