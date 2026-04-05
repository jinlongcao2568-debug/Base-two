# AX9S Orchestrator Runtime Model

## Purpose

- Define the single-machine runtime foundation for AX9 governance automation.
- Keep runtime state, session telemetry, worker registry, and task-source registry in one governed model.
- Reserve future multi-machine and external-issue interfaces without claiming they are implemented today.

## Current Implementation

- Runtime file: `.codex/local/COORDINATION_RUNTIME.yaml`
- Registry files:
  - `docs/governance/TASK_SOURCE_REGISTRY.yaml`
  - `docs/governance/WORKER_REGISTRY.yaml`
- Status command:
  - `python scripts/task_ops.py orchestration-status --format yaml`
  - `python scripts/task_ops.py orchestration-status --format json`

The runtime file is a local derived state surface. It is not a second task ledger and must not replace:

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`

## Runtime Blocks

- `runtime`
  - coordinator mode
  - last tick and reconcile timestamps
  - last command
  - current task summary
  - stalled or blocked signal
- `sessions`
  - current and recent session telemetry
  - writer state
  - continue intent
  - last safe write timestamp
- `lease`
  - top-level coordination write ownership summary
  - per-task lease state
- `workers`
  - registry-backed worker runtime view
  - current implementation supports only `local`
- `task_sources`
  - registry-backed task-source runtime view
  - current implementation supports only `doc_local`
- `publish_readiness`
  - live-task Git publish gate summary
  - remote / `gh` / existing PR visibility
  - missing required test visibility for explicit publish actions

## Single-Machine Scope

- `doc_local` is the only enabled task source in v1.
- `worker-local-01` is the only enabled worker in v1.
- The coordinator and worker run on the same machine.
- Single-writer lease rules still control repository writes.

## Reserved Future Interfaces

- External task sources:
  - `linear`
  - `github_issues`
  - `jira`
- Remote worker kinds:
  - `ssh`
  - `remote_agent`

These are reserved interfaces only. In v1 they must remain visibly disabled or unsupported.

## Guardrails

- Do not route real work to a worker whose `kind` is not `local` in v1.
- Do not treat a disabled external source as active input.
- Do not use runtime telemetry as a replacement for runlog or handoff evidence.
- Do not infer token or cost telemetry that the repository cannot observe.
