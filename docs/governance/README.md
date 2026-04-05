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
- `AUTOMATION_INTENTS.yaml`
  - natural-language intent routing policy for governed continuation entrypoints in `docs/governance/AUTOMATION_INTENTS.yaml`
- `DIRECTORY_MAP.md`
  - repository boundary map
- `PROMPT_MODULE_CATALOG.yaml`
  - governed prompt module catalog and role assembly in `docs/governance/PROMPT_MODULE_CATALOG.yaml`
- `runtime_prompts/`
  - generated runtime prompts for coordinator, worker, and reviewer roles
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
- `prompt_modules/`
  - governed prompt rule modules for coordinator, worker, and reviewer roles

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
  - `continue-current` keeps or reactivates the live current task and may close a review-ready live task back to formal idle.
  - `continue-roadmap` closes a review-ready live task or resumes from the formal idle state, then resolves the next valid successor.
- `python scripts/automation_intent.py preflight --utterance "<text>"` is the governed free-form continuation entrypoint.
  - It may recognize broader natural-language continue requests.
  - It still routes only to `continue-current` or `continue-roadmap`.
  - Ambiguous requests must stop instead of guessing through a task switch.
- Closing a live top-level coordination task without an immediately activated successor now moves the repository into a legal idle control-plane state.
- Roadmap continuation now follows the module order in `docs/governance/MODULE_MAP.yaml`, starting with early-stage gaps and extending downstream when policy and dependencies allow.
- `stage7-stage9` remain downstream-only stages and now require both dependency satisfaction and `stage7_to_stage9_business_automation=implemented` before automation may generate them.
- Prompt source of truth now lives under `docs/governance/prompt_modules/`; root-level scratch notes are not live prompt inputs.
- Generated runtime prompts now live under `docs/governance/runtime_prompts/`; they are derived artifacts, not a second prompt authority.
- App-level custom instructions are not part of the governance control plane and should stay empty unless they are only carrying language or output-style preferences.
