# Preserve-First Full-Clone Recovery SOP

## Purpose

Use this SOP when a full-clone slot is marked `preserve-before-rebuild` or otherwise cannot be returned to the dispatch pool through the standard `rebuild-full-clone-pool` path without first salvaging local work.

This SOP is for governance recovery only. It does not authorize clone-local ledger repair, clone-local closeout, or any second source of truth outside the main control plane.

## When To Use

- `audit-full-clone-pool` reports a slot as `blocked` or `stale_runtime=true`
- the slot is on a non-idle branch
- the slot contains unmerged or operator-owned local commits
- the slot was explicitly isolated with a preserve-first reason
- automated rebuild refuses the slot because `preserve_before_rebuild` is set or the runtime is still dirty

## Hard Rules

- Run all governance write actions from the main control plane only.
- Treat clone-local `docs/governance/*.yaml` and clone-local candidate caches as execution leftovers, never as truth.
- Do not delete, rebuild, or unlock a preserve-first slot until local commits are either salvaged or explicitly discarded by operator decision.
- If the main control plane and clone runtime disagree, report `ledger divergence` first and recover second.

## Recovery Steps

### 1. Audit and classify the slot

Run from the main control plane:

```powershell
python scripts/task_ops.py audit-full-clone-pool --slot-id <slot-id>
```

Record:

- observed branch
- effective dirty paths
- runtime stamp reasons
- candidate cache issues
- whether the slot still has a live `current_task_id`

### 2. Decide salvage or discard

For any non-idle branch or local commit:

- salvage: keep the implementation by copying the branch into the main control plane
- discard: explicitly approve deleting the branch tail and resetting the slot

Do not continue until one of those two outcomes is chosen.

### 3. Salvage the branch before rebuild

If local commits must be preserved, copy the branch into the main control plane before touching the slot:

```powershell
git -C <control-plane-root> fetch <clone-path> <branch>:refs/heads/<branch>
```

Then verify the branch exists in the main control plane:

```powershell
git -C <control-plane-root> branch --list <branch>
```

If the branch is being discarded instead, record the branch name and last commit hash in the recovery task runlog before deleting the ref.

### 4. Clear preserve-first handling

Only after salvage or explicit discard:

- remove the preserve-first blocker in the main control plane ledger
- ensure the slot is no longer treated as `preserve_before_rebuild`

### 5. Reprovision the slot

Preferred path:

```powershell
python scripts/task_ops.py rebuild-full-clone-pool --slot-id <slot-id>
```

If Windows keeps the old slot path open and automated rebuild cannot remove the directory:

1. confirm the salvage step is complete
2. manually re-clone the main control plane into the slot path
3. reset the slot to its idle branch at the control-plane `HEAD`
4. clean untracked files
5. update the main control plane pool record back to `ready` only after validation succeeds

### 6. Revalidate runtime parity

Run:

```powershell
python scripts/task_ops.py audit-full-clone-pool --slot-id <slot-id>
```

Acceptance for the recovered slot:

- `slot_status=ready`
- `observed_branch=<idle_branch>`
- `runtime_drift=false`
- `divergent=false`
- no candidate cache issues
- no non-terminal execution tasks

### 7. Verify candidate behavior from the clone

From the recovered clone:

```powershell
python scripts/task_ops.py claim-next --now 2026-04-09T13:05:00+08:00
```

Expected result: clone-cwd unified CLI matches control-plane truth or fails fast. It must not revive clone-local candidate truth.

### 8. Close the recovery task

The recovery is not complete until:

- the salvage or discard decision is recorded
- the recovered slot passes audit
- the recovery task handoff is written
- the recovery task is closed in the main control plane

## Branch Disposition Rules

- If the preserved branch should continue, convert it into a formal governed task or merge path.
- If the preserved branch should not continue, delete the main-control-plane local ref after recording the last commit hash in the recovery runlog.
- Do not leave preserved implementation branches unnamed or untracked after slot recovery.

## Forbidden Actions

- running clone-local `claim-next`, `closeout`, or ledger repair scripts as truth
- reopening a preserve-first slot without salvage or explicit discard
- rebuilding a slot while live local commits are still the only copy
- treating stale clone-local candidate caches as a recovery input
