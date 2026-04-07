# Live Governance Boundary

This document defines which governance materials are live execution surfaces and which are historical audit artifacts.

## Live Governance Surfaces

Read these first when deciding the current default gate, prompt source, or execution boundary:

1. `docs/product/AUTHORITY_SPEC.md`
2. `docs/governance/OPERATOR_MANUAL.md`
3. `docs/governance/CURRENT_TASK.yaml`
4. the live current task file
5. the live current task runlog
6. the live governance maps and policies:
   - `docs/governance/MODULE_MAP.yaml`
   - `docs/governance/CAPABILITY_MAP.yaml`
   - `docs/governance/TASK_POLICY.yaml`
   - `docs/governance/TEST_MATRIX.yaml`
   - `docs/governance/PROMPT_MODULE_CATALOG.yaml`
   - `docs/governance/prompt_modules/`

`docs/governance/CURRENT_TASK.yaml` remains the only live execution entry.

## Historical Audit Artifacts

Historical artifacts remain searchable for audit and recovery, but they are not the current default gate or prompt source.

- Closed task files under `docs/governance/tasks/`
- Closed runlogs under `docs/governance/runlogs/`
- Handoff snapshots under `docs/governance/handoffs/`
- Historical rows in `docs/governance/TASK_REGISTRY.yaml`

`docs/governance/TASK_REGISTRY.yaml` is a live ledger for task existence and state, but closed task rows and their `required_tests` remain historical audit evidence.

## Interpretation Rules

- Live governance surfaces must be read before historical artifacts.
- Historical task files, runlogs, handoffs, and registry rows must not redefine the current default governance gate.
- Do not derive the current default gate from historical `required_tests` records.
- If live governance surfaces and historical artifacts disagree, the live governance surfaces win for current execution.
