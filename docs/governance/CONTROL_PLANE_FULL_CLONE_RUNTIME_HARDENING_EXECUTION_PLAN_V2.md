# AX9 Control Plane Full-Clone Runtime Hardening Execution Plan v2

## Status

- `status`: `draft`
- `owner_domain`: `governance`
- `scope`: `control_plane`, `candidate_pool`, `full_clone_workers`
- `updated_at`: `2026-04-09T00:00:00+08:00`

## Positioning

This document is a dedicated execution plan for the AX9 control-plane consistency incident discovered on `2026-04-09`.

It does not create or modify governance truth by itself.

It is an implementation playbook that complements:

- `docs/governance/CONTROL_PLANE_SINGLE_LEDGER_PRINCIPLES.md`
- `docs/governance/OPERATOR_MANUAL.md`

If this document conflicts with the single-ledger principles, the single-ledger principles win.

## Task Understanding

The goal is not to repair business logic.

The goal is to harden governance consistency so that:

- clones cannot misjudge roadmap candidates from stale local ledgers;
- the main control plane can detect stale mirrors even when a full-clone slot is marked `ready`;
- full-clone dispatch requires both ledger readiness and live runtime readiness;
- full-clone refresh and rebuild become explicit operator actions instead of ad-hoc manual repair.

## Phase Mapping

- domain: `governance`
- execution phase: `control-plane hardening`
- non-business scope: no Stage1-Stage9 product behavior change

## Impact Boundary

### Allowed Modification Scope

- `scripts/`
- `tests/governance/`
- `docs/governance/`

### Forbidden Modification Scope

- `src/`
- `tests/stage1/` through `tests/stage9/`
- `db/migrations/`

## Explicit Non-Goals

- Do not repair clone-local ledger history in place.
- Do not perform governance closeout inside clones.
- Do not change business rules, stage boundaries, interface contracts, or customer-visible semantics.
- Do not re-elevate clone-local candidate caches into a truth source.
- Do not introduce a second scheduler or a clone-side reconciliation model.

## Root Problem Statement

The incident is not a real business dependency block.

It is a governance-runtime consistency failure caused by a combination of:

- stale full-clone governance scripts;
- stale clone-local ledgers and candidate caches;
- direct script entrypoints that can still write governance artifacts from clone roots;
- divergence detection that misses `ready` slots whose clone runtime is no longer actually idle.

## P0 Containment

### Immediate Freeze

- Freeze full-clone dispatch for `worker-01` through `worker-09`.
- Stop clone-side `claim-next`, `worker-self-loop`, and automatic clone-local `closeout`.
- Treat the incident as `ledger divergence`, not as a business blocker.

### Worker Segmentation

#### worker-01

- Isolate `worker-01` immediately.
- Preserve the current branch and uncommitted changes before any rebuild decision.
- Do not return `worker-01` to the dispatch pool until a human explicitly clears it.

#### worker-02 through worker-09

- Treat `worker-02` through `worker-09` as stale mirrors.
- Do not perform local ledger repair inside those clones.
- Rebuild or refresh them only from the main control plane.

### Temporary Operator Rule

During containment, governance actions must use the unified CLI entrypoint only.

Direct execution of governance sub-scripts from inside clones is forbidden.

## P1 Code Hardening

### 1. Seal Direct Writer Entrypoints

Update the following scripts so they resolve the main control plane root instead of the local repo root:

- `scripts/roadmap_candidate_index.py`
- `scripts/roadmap_candidate_compiler.py`

For governance-writing or candidate-artifact-writing scripts:

- if executed inside a full clone, they must either resolve to the control plane root or fail fast;
- they must not silently write `.codex/local/roadmap_candidates/*` into clone-local state.

### 2. Expand Ledger Divergence Detection

Extend `detect_ledger_divergences()` in `scripts/control_plane_root.py`.

It must detect stale mirrors even when a full-clone slot is already marked `ready`.

At minimum, detect these cases:

- slot is `ready` but clone current branch is not `idle_branch`;
- slot is `ready` but clone has non-transient tracked dirty files;
- clone-local `TASK_REGISTRY.yaml` still contains non-terminal execution tasks;
- clone governance runtime stamp is older than the control plane runtime stamp;
- clone candidate cache is missing, legacy-formatted, or still contains retired candidates.

### 3. Add Live Runtime Validation Before Full-Clone Dispatch

Before `_assign_full_clone_slot()` in `scripts/roadmap_claim_next.py` accepts a slot, validate the live clone runtime.

Required checks:

- clone path exists;
- current branch equals `idle_branch`;
- tracked working tree state is clean after transient/runtime-file filtering;
- governance runtime stamp matches the control plane;
- clone-local governance state does not expose non-terminal execution leftovers.

If any check fails:

- reject dispatch;
- surface the result as `ledger divergence`;
- keep the slot out of the `ready` dispatch path.

### 4. Introduce Governance Runtime Stamp

The runtime gate must not use the entire repository `HEAD` as the sole blocking key.

Use a governance-specific machine-readable runtime stamp instead.

Recommended fields:

- `governance_runtime_version`
- `candidate_index_format_version`
- `governance_scripts_hash`

Optional audit-only field:

- `control_plane_head`

`control_plane_head` may be recorded for traceability, but it must not be the only hard gate because valid business branches may differ from main `HEAD`.

### 5. Scan Remaining Governance Write Entrypoints

Do not stop at the two direct writer scripts.

Review any script that can still initiate governance writes from clone roots, with priority on:

- `scripts/worker_self_loop.py`
- `scripts/task_continuation_ops.py`
- `scripts/task_coordination_planner.py`

Any surviving clone-side governance write path must be redirected to the control plane or blocked.

## P2 Operationalization

### New Control-Plane Commands

Add operator-facing commands that run only against the main control plane:

- `audit-full-clone-pool`
- `refresh-full-clone-pool` or `rebuild-full-clone-pool`

### Full-Clone Policy

- clone-local candidate caches are execution leftovers only;
- governance consumers must ignore clone-local candidate truth entirely;
- every governance-runtime upgrade must include full-clone refresh or rebuild as part of release procedure.

### Console Visibility

The governance console should surface at least:

- `ledger_divergence_count`
- `stale_runtime_count`

### Worker Self-Loop Constraint

`worker-self-loop` may report runtime signals only.

It must not become an alternative governance authority or local scheduler.

## Implementation Order

1. Freeze full-clone dispatch.
2. Preserve and isolate `worker-01`; do not rebuild it yet.
3. Create the formal governance task package in the main control plane.
4. Implement the P1 hardening changes.
5. Rebuild `worker-02` through `worker-09`.
6. Run regression verification from both control-plane and clone contexts.
7. Decide whether `worker-01` should be rebuilt after its preserved state is reviewed.
8. Restore full-clone dispatch only after divergence returns to zero.

## Verification Plan

### Governance Tests To Update

- `tests/governance/test_control_plane_single_ledger.py`
  - cover `ready-slot stale mirror` divergence detection
- `tests/governance/test_full_clone_pool.py`
  - cover `ready` slot rejection for non-idle or non-transient dirty runtime
- `tests/governance/test_roadmap_claim_next.py`
  - cover fail-fast behavior when a clone runtime is stale
- `tests/governance/test_roadmap_candidate_index.py`
  - cover direct script refusal to write local clone candidate artifacts
- `tests/governance/test_roadmap_candidate_compiler.py`
  - cover direct script refusal to write local clone candidate artifacts
- `tests/governance/test_review_candidate_pool.py`
  - cover `worker-01` and `worker-02` style divergence visibility

### Recommended Additional Coverage

- `tests/governance/test_worker_self_loop.py`
  - cover stale runtime and stale slot rejection
- `tests/governance/test_task_ops.py`
  - cover clone-cwd unified CLI resolution to the control plane

### Manual Regression Checklist

- main control plane `claim-next` dry-run still selects `stage2-core-contract`;
- clone-cwd unified CLI either matches control-plane truth or fails fast;
- `review-candidate-pool` reports `worker-01` / `worker-02` style divergence;
- a `ready` slot with non-idle or dirty runtime cannot be dispatched;
- rebuilt full clones report governance runtime/version parity with the control plane.

## Minimum Acceptance Criteria

- No governance command executed from a clone may treat clone-local ledgers as truth.
- `worker-02` style stale mirrors are detected by the main control plane.
- `worker-01` style `ready-on-ledger / not-ready-in-runtime` slots cannot be assigned.
- Rebuilt `worker-02` through `worker-09` match the control-plane governance runtime stamp.
- `worker-01` remains isolated until explicitly cleared.
- The main control plane `claim-next` dry-run continues to choose `stage2-core-contract`.

## Risks

- `worker-01` contains unmerged local state and cannot be rebuilt blindly.
- Hardening only direct writer scripts without adding runtime slot validation will allow recurrence.
- Warning-only divergence handling is insufficient; stale paths must fail fast.
- Using whole-repo `HEAD` as the only runtime gate would over-block legitimate business branches.

## Rollback

- All changes remain limited to governance scripts, governance tests, and governance documentation.
- If the new gates make scheduling unusable, revert the governance hardening changes and keep full-clone dispatch frozen.
- Do not discard or roll back `worker-01` preserved local state; it is the manual recovery anchor.

## Proposed Task Package Primary Goal

`AX9 control plane single-ledger / full-clone runtime hardening: seal clone-local governance entrypoints, detect stale mirrors under ready slots, and require live runtime validation before full-clone dispatch.`
