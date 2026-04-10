# AX9S Governance Index

This directory is the live control plane for repository execution. It is not the default onboarding path for ordinary product development.

Conflict rule:
- If this directory conflicts with `docs/product/AUTHORITY_SPEC.md`, the product authority wins.
- If this directory conflicts with `docs/governance/OPERATOR_MANUAL.md`, the operator manual wins for execution procedure.
- `CURRENT_TASK.yaml` remains the only live execution entry.
- `CURRENT_TASK.yaml` remains the only live execution focus entry.

## When To Enter Governance

Read governance documents first only when one of the following is true:
- you are activating, continuing, or closing a governed task
- you need live task occupancy or worktree ownership
- you are changing governance scripts, policies, or control-plane ledgers
- you are auditing a historical task or recovering from governance drift

For ordinary product and contract work, start from `docs/INDEX.md` and the product docs instead.

## Minimum Live Surfaces

These are the high-value governance files that should stay in the daily operator path:
- `OPERATOR_MANUAL.md`
  - the live execution procedure
- `CURRENT_TASK.yaml`
  - the only live focus entry
- `TASK_REGISTRY.yaml`
  - the live task ledger
- `WORKTREE_REGISTRY.yaml`
  - the live worktree and coordination ownership ledger
- `DIRECTORY_MAP.md`
  - repository boundary map when allowed paths are unclear
- `TEST_MATRIX.yaml`
  - the live gate map when test scope is unclear

Use additional files only when the current task or the active operator action requires them.

Additional live references that are still valid, but should be opened on demand instead of by default:
- `docs/governance/LIVE_GOVERNANCE_BOUNDARY.md`
- `docs/governance/AUTOMATION_INTENTS.yaml`
- `docs/governance/PROMPT_MODULE_CATALOG.yaml`

## Historical But Retained

These governance surfaces still matter for audit and recovery, but they are not part of the default read path:
- `tasks/`
- `runlogs/`
- `handoffs/`
- `dispatch_briefs/`
- `runtime_prompts/`
- historical design, transition, and scheduler documents in this directory

Retention rule:
- keep them searchable
- do not treat them as the first document a developer must read
- do not let them override the live control-plane files

## Execution Order

1. Read `docs/product/AUTHORITY_SPEC.md`.
2. Read `docs/governance/OPERATOR_MANUAL.md`.
3. Read `docs/governance/CURRENT_TASK.yaml`.
4. Read the current task file and runlog only for the live task you are working on.
5. Run the required task gates before implementation.

## Current State

- The governance control plane is live and test-backed.
- `CURRENT_TASK.yaml` is the only live focus entry; task files and runlogs are supporting evidence, not a second live truth.
- Product docs and contracts remain the primary route for domain understanding.
- Historical governance artifacts remain available for audit, recovery, and postmortem work, but they should not be the default developer entrance.
