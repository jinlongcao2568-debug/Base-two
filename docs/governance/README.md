# AX9S Governance Index

This directory is the live control plane for repository execution.

Conflict rule:
- If this directory conflicts with `docs/product/AUTHORITY_SPEC.md`, the product authority wins.
- If this directory conflicts with `docs/governance/OPERATOR_MANUAL.md`, the operator manual wins for execution procedure.
- `CURRENT_TASK.yaml` remains the only live execution entry.

## Live Files

- `CURRENT_TASK.yaml`
  - the only live task execution entry
- `TASK_REGISTRY.yaml`
  - all known tasks and their current ledger state
- `WORKTREE_REGISTRY.yaml`
  - worktree and coordination ownership
- `DEVELOPMENT_ROADMAP.md`
  - live phase and current-task roadmap context
- `DIRECTORY_MAP.md`
  - repository boundary map
- `MODULE_MAP.yaml`
  - machine-readable module boundaries and reserved paths
- `TEST_MATRIX.yaml`
  - machine-readable gates by size class, module, and authority-critical chain
- `TASK_POLICY.yaml`
  - task sizing, topology, automation mode, and stop conditions
- `AUTOMATION_OPERATING_MODEL.md`
  - runner semantics and control-plane behavior
- `CODE_HYGIENE_POLICY.md`
  - repository hygiene rules
- `CAPABILITY_MAP.yaml`
  - live capability inventory and test linkage
- `SCHEMA_REGISTRY.md`
  - formal field and enum registry
- `INTERFACE_CATALOG.yaml`
  - formal interface catalog or professional zero-state
- `owners.yaml`
  - role-based ownership map for formal paths

## Execution Order

1. Read `docs/product/AUTHORITY_SPEC.md`.
2. Read `docs/governance/OPERATOR_MANUAL.md`.
3. Read `docs/governance/CURRENT_TASK.yaml`.
4. Read the current task file and runlog.
5. Run repository gates before implementation.

## Current State

- The governance control plane is live and test-backed.
- Contracts are formalized for `project_base`, `rule_hit`, and `project_fact`.
- The minimum authority-critical chain `stage3 -> stage4 -> stage6` is covered by fixtures and integration tests.
- No public business API is registered yet; the interface catalog stays in an explicit zero-state until one exists.
