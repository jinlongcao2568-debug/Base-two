# CONCURRENT_EXECUTION_SINGLE_LEDGER_MODEL

## Why

AX9 needs one truth source for roadmap scheduling, task lifecycle, and executor occupancy.
That does not require one global live task.
The previous model overloaded `CURRENT_TASK.yaml` with two different meanings:

- control-plane focus task
- global live-task truth for every executor

That coupling breaks as soon as `control-plane-main` and `worker-01..09` run in parallel.

## Single Truth Does Not Mean Single Live Task

One control-plane ledger can safely describe multiple concurrent executors.
The control-plane still owns the only writable governance truth.
The change is semantic separation:

- `CURRENT_TASK.yaml` answers "what is the control-plane focused on right now"
- `EXECUTION_LEASES.yaml` answers "who is actively executing what right now"

This preserves the single-ledger rule while allowing concurrent work.

## Ledger Responsibilities

### `CURRENT_TASK.yaml`

Purpose:
- focus projection for the active top-level coordination task

Must not be used as:
- the only global live-task source
- the only executor occupancy source

### `TASK_REGISTRY.yaml`

Purpose:
- task definitions
- lifecycle state
- stage, branch, required tests, closeout result

### `claims.yaml`

Purpose:
- candidate occupancy
- pre-execution claim state
- stale/resumable takeover detection

### `EXECUTION_LEASES.yaml`

Purpose:
- authoritative executor-to-task binding ledger
- concurrent execution truth under one control plane

Minimum fields:
- `lease_id`
- `task_id`
- `task_kind`
- `stage`
- `branch`
- `candidate_id`
- `executor_id`
- `executor_type`
- `status`
- `owner_session_id`
- `started_at`
- `heartbeat_at`
- `closed_at`

### `FULL_CLONE_POOL.yaml`

Purpose:
- full-clone slot health
- runtime parity
- slot readiness / quarantine
- slot-to-task attachment for pool dispatch

### `WORKTREE_REGISTRY.yaml`

Purpose:
- worktree path ownership
- execution workspace lifecycle
- cleanup state
- worker owner / pool metadata

## State Machines

### Executor State Machine

Executors include:
- `control-plane-main`
- `worker-01` through `worker-09`
- existing local execution workers where legacy paths still need them

Primary states:
- `idle`
- `running`
- `paused`
- `blocked`
- `review_pending`
- `closed`

Truth source:
- `EXECUTION_LEASES.yaml`

### Candidate State Machine

Primary states:
- `ready`
- `claimed`
- `running`
- `review`
- `done`
- `blocked`
- `stale`

Truth sources:
- `claims.yaml`
- `TASK_REGISTRY.yaml`
- `EXECUTION_LEASES.yaml`

Interpretation rule:
- a candidate is occupied if it has a live claim or a live execution lease

### Focus Task State Machine

Primary states:
- `idle`
- `doing`
- `paused`
- `review`
- `blocked`

Truth source:
- `CURRENT_TASK.yaml`

Interpretation rule:
- focus state is an operator projection, not the sole source of concurrent execution truth

## Write Lock And Revision Rules

Control-plane writes must be transactional.
Every governance write path must:

1. acquire the control-plane write lock
2. reload latest control-plane state under lock
3. validate the current revision
4. update all affected ledgers together
5. fail fast on lock conflict or revision mismatch

Expected conflict classes:
- write lock already held
- revision mismatch
- duplicate claim
- duplicate execution lease
- stale runtime / unpublished runtime

Conflict handling rule:
- fail explicitly
- do not silently overwrite another window's governance write
- do not infer success from partially updated YAML files

## How Candidate Pool Knows "Who Started But Has Not Finished"

The candidate pool must stop inferring liveness from `CURRENT_TASK`.
It should read:

- `TASK_REGISTRY.yaml`
- `claims.yaml`
- `EXECUTION_LEASES.yaml`
- `FULL_CLONE_POOL.yaml`
- `WORKTREE_REGISTRY.yaml`

Dispatch interpretation:

- if a candidate has a live claim, it is occupied
- if a task has a live execution lease, it is actively executing
- if an executor has a running lease, that executor is not dispatchable
- if a slot is quarantined, only that slot is blocked
- if runtime drift or revision conflict exists on a ready executor, dispatch blocks for that executor

This lets the pool know a task was started and is still unfinished without forcing the whole system into a false ledger divergence.

## Operator Projection Rules

The operator console should project, not invent, concurrency state.
Its preferred display groups are:

- `focus_current_task`
- `running_execution_leases`
- `ready_executors`
- `quarantined_executors`

Projection rules:

- `focus_current_task` comes from `CURRENT_TASK.yaml`
- `running_execution_leases` comes from live rows in `EXECUTION_LEASES.yaml`
- `ready_executors` comes from `control-plane-main` idle state plus dispatch-eligible full-clone slots
- `quarantined_executors` comes from full-clone audit rows where `quarantined=true`

Normal concurrency is not ledger divergence.
Ledger divergence is reserved for:

- write-lock conflicts
- revision mismatches
- duplicate claims
- duplicate execution leases
- runtime drift on dispatch-eligible executors
- ready-slot / mirror inconsistencies reported by the full-clone audit

## Migration Plan

### Stage 1

- keep `CURRENT_TASK.yaml`
- introduce `EXECUTION_LEASES.yaml`
- dual-write focus task and execution lease state

### Stage 2

- move candidate review and `claim-next` occupancy logic to leases + claims + slot health

### Stage 3

- keep `CURRENT_TASK.yaml` as focus projection only
- remove the last implicit assumption that one live current task equals one live executor

## Non-Goals

- no clone-local governance truth
- no second scheduler
- no change to Stage1-Stage9 business semantics
- no bypass of `stage6_facts`
