# AX9S Automation Operating Model

## Scope

- The live automation layer now supports:
  - `continue-current`
  - `continue-roadmap`
  - dependency-aware `stage1-stage6` business successor generation
- The live automation layer must not auto-generate `stage7-stage9` business work.

## Continuation Semantics

### `continue-current`

- `doing`: keep the live current task and switch back to its branch if the worktree is clean enough to do so.
- `paused`: reactivate the live current task and restore its branch/worktree alignment.
- `blocked`: stop immediately and report the blocker.
- `review` or `done`: do not select a successor; instruct the operator or automation runner to use `continue-roadmap`.

### `continue-roadmap`

- `doing` or `paused`: continue the live current task; do not skip ahead.
- `blocked`: stop immediately and report the blocker.
- `review`: if `can-close` is satisfied and the worktree starts clean, close the live task and then resolve the next successor.
- `done`: resolve the next successor directly.

## Successor Resolution Rules

- The roadmap frontmatter is the only live continuation policy source.
- Resolution order is:
  1. use `next_recommended_task_id` when it exists and is valid;
  2. otherwise generate a governance successor when the governance automation gap is still open;
  3. otherwise generate a `stage1-stage6` business successor round when business automation is enabled and the business autopilot capability is implemented;
  4. otherwise stop with a no-successor report.
- A generated business successor round must:
  - stay within `stage1-stage6`;
  - obey `MODULE_MAP.yaml` dependency order;
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

## Automation Runner

- `python scripts/automation_runner.py once --continue-roadmap --prepare-worktrees` now means:
  1. run `check_repo.py`;
  2. run `check_hygiene.py`;
  3. execute `continue-roadmap` when requested;
  4. prepare worktrees for the live `parallel_parent` task when allowed by automation mode;
  5. run `auto-close-children` for review-ready child lanes when allowed by automation mode;
  6. run the existing orphan cleanup logic.
- The runner still honors `manual`, `assisted`, and `autonomous` gating for parallel worktree preparation and child closeout.

## Stop Conditions

- dirty worktree before branch switch or successor activation
- blocked current task
- roadmap policy drift or missing continuation fields
- explicit successor missing from the registry
- multiple open top-level coordination successors
- unmet successor dependency
- incomplete successor boundary declaration
- review bundle failure on an autonomous child lane
