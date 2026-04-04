# AX9S Automation Operating Model

## Scope

- The live automation layer does not auto-invent business implementation work.
- The live automation layer now supports two continuation semantics:
  - `continue-current`
  - `continue-roadmap`
- v1 roadmap continuation may only auto-advance governance scheduling work. It must not auto-select stage7-stage9 business work.

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
  2. otherwise generate a successor only when roadmap policy allows it and the highest-priority gap is a governance automation gap;
  3. otherwise stop with a no-successor report.
- A successor is valid only when:
  - it exists in `TASK_REGISTRY.yaml` or can be generated from `TASK_POLICY.yaml`;
  - it is unique among open top-level coordination tasks;
  - its dependencies are already satisfied;
  - its `allowed_dirs`, `planned_write_paths`, and `required_tests` are all explicit;
  - it does not remain blocked or already done.

## Branch Switching Rules

- Automation may switch or create the target branch only when the worktree is clean before the continuation command starts.
- Automation must never auto-stash, auto-reset, or auto-discard dirty files.
- Target-branch behavior is:
  - existing branch: `git switch`
  - missing branch: `git switch -c`

## Automation Runner

- `python scripts/automation_runner.py once --continue-roadmap` now means:
  1. run `check_repo.py`;
  2. run `check_hygiene.py`;
  3. run the existing worktree cleanup logic;
  4. call `task_ops continue-roadmap`.
- The runner still honors `manual`, `assisted`, and `autonomous` gating for parallel worktree preparation and child closeout.
- `--continue-roadmap` does not bypass any existing gate.

## Stop Conditions

- dirty worktree before branch switch or successor activation
- blocked current task
- roadmap policy drift or missing continuation fields
- explicit successor missing from the registry
- multiple open top-level coordination successors
- unmet successor dependency
- incomplete successor boundary declaration
