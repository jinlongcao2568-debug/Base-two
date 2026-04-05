# AX9S Governance Index

This directory is the live control plane for repository execution.

Conflict rule:
- If this directory conflicts with `docs/product/AUTHORITY_SPEC.md`, the product authority wins.
- If this directory conflicts with `docs/governance/OPERATOR_MANUAL.md`, the operator manual wins for execution procedure.
- `CURRENT_TASK.yaml` remains the only live execution entry.
  - It may hold either a live current-task payload or the formal `idle` zero-state.

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
  - task sizing, topology, automation mode, stop conditions, and blueprints
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
- Contracts are formalized for `project_base`, `rule_hit`, `evidence`, `review_request`, `report_record`, and `project_fact`.
- The minimum authority-critical chain `stage3 -> stage4 -> stage6` is covered by fixtures and integration tests.
- No public business API is registered yet; the interface catalog stays in an explicit zero-state until one exists.
- Continuation now has two formal entry points:
  - `continue-current` resumes only the live current task.
  - `continue-roadmap` closes a review-ready live task or resumes from the formal idle state, then resolves the next valid successor.
- Closing a live top-level coordination task without an immediately activated successor now moves the repository into a legal idle control-plane state.
- Roadmap continuation now follows the module order in `docs/governance/MODULE_MAP.yaml`, starting with early-stage gaps and extending downstream when policy and dependencies allow.
- `stage7-stage9` are no longer hard-pinned to a governance-only deferred state; they remain downstream stages that may advance only when their dependencies, task package boundaries, and required tests are satisfied.
