# AX9 Control Plane Single-Ledger Governance Principles

## Status

- `status`: `draft`
- `owner_domain`: `governance`
- `scope`: `control_plane`, `candidate_pool`, `full_clone_workers`
- `updated_at`: `2026-04-08T22:10:00+08:00`

## Purpose

This document fixes the control-plane authority boundary for the AX9 roadmap candidate pool and full-clone worker model.

It defines which artifacts are the single source of truth, which artifacts are only execution signals, and which upgrades are required to prevent ledger divergence between the main control plane and clone worktrees.

## Core Principle

AX9 uses **single-ledger governance with multi-worktree execution**.

That means:

- governance truth must exist in exactly one control-plane ledger set;
- multiple worker worktrees may execute tasks in parallel;
- worker worktrees may report runtime state;
- worker worktrees must not become independent governance truth sources.

## Source Of Truth

The main control plane under the primary repository root is the only governance truth source.

Authoritative ledgers:

- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/FULL_CLONE_POOL.yaml`
- `.codex/local/roadmap_candidates/claims.yaml`

The candidate pool, closeout flow, claim selection, worker allocation, and release evaluation must read governance truth only from the main control plane.

## Execution Signals

Full-clone worker repositories may expose execution signals, but not independent governance truth.

Allowed worker-side signals:

- current git branch
- worktree cleanliness or dirty paths
- local heartbeat
- local execution context
- local test output
- local runlog fragments
- finish intent or close intent

Forbidden worker-side authority:

- independently deciding final task status
- independently closing roadmap claims
- independently releasing full-clone slots
- independently unblocking downstream roadmap candidates
- acting as an alternative candidate-pool truth source

## Control-Plane Rule

Every governance write that changes task lifecycle or roadmap scheduling state must execute against the main control plane.

This includes:

- `worker-start`
- `worker-finish`
- `pause`
- `close`
- `sync`
- `claim-next`
- claim closeout
- full-clone slot release

If a worker runs a governance write command from inside a clone, the command must either:

1. resolve the control-plane root and write there; or
2. fail fast with an explicit error.

Silent local-only ledger writes are forbidden.

## Candidate Pool Rule

The candidate pool may inspect all worker execution signals, but it must not merge multiple clone ledgers into a synthetic truth model.

The candidate pool should:

- read one governance truth source;
- observe many worker runtime signals;
- derive claimability and release from the main ledger plus worker signals;
- reject ambiguous states as divergence, not as valid multi-ledger truth.

## Divergence Definition

Ledger divergence exists when the main control plane and a clone disagree on governance state for the same execution task.

Examples:

- main ledger says `paused`, clone ledger says `done`
- main full-clone pool says slot `active`, clone says task closed
- main claim says `taken_over`, clone says task closed

When divergence exists:

- candidate-pool results are operationally suspect;
- downstream auto-release must not be trusted;
- the console should surface an explicit divergence warning;
- operators must repair the main control plane before interpreting stale candidates as scheduler failures.

## Why Multi-Ledger Truth Is Rejected

AX9 must not attempt to treat every clone ledger as peer truth.

Reasons:

- write ordering is not stable across clones;
- a clone may be partially updated;
- different windows may close or resume the same task at different times;
- candidate-pool logic would become a second scheduler;
- governance auditability would be lost.

The system should prefer one main ledger plus many execution observers, not many ledgers plus a reconciliation guesser.

## Required Upgrades

### P0 Hardening

- Force governance write commands executed inside full clones to resolve and write through the main control plane.
- Prevent clone-local ledger writes from being accepted as valid closeout.
- Ensure `worker-finish -> can-close -> close -> release slot -> close claim -> refresh candidates` is completed in the main control plane.

### P1 Safety

- Add ledger-divergence detection between main ledgers and full-clone mirrors.
- Surface divergence warnings in the governance console.
- Refuse candidate interpretation that depends on a divergent task until repaired.

### P1 Refresh

- Add lightweight automatic page refresh for operator visibility.
- Refresh snapshots on an interval and after successful actions.
- Keep candidate compilation explicit or event-driven, not high-frequency polling.

### P2 Worker UX

- Standardize worker-side finish intent reporting.
- Make full-clone workers report status without claiming authority over final governance state.

## Non-Goals

- Do not introduce a second scheduler.
- Do not make the console directly control Codex desktop windows.
- Do not reuse `handoffs/` as the execution dispatch inbox.
- Do not move business truth into UI code or clone-local scripts.

## Operator Interpretation Rule

If a task appears stale or resumable after a worker reports completion, operators should first check whether the closeout reached the main control plane before changing scheduler policy.

The first suspicion should be ledger divergence, not roadmap dependency logic.

## Implementation Guidance

When upgrading the control plane:

- keep one governance truth source;
- let workers submit runtime evidence, not final truth;
- let the main control plane declare final task state;
- let candidate release remain derived behavior, not a manual operator action.

## Decision

AX9 will use **single-ledger governance, multi-worktree execution, and control-plane-owned lifecycle writes** as the permanent operating model.
