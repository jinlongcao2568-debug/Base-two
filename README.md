# AX9S Authority-Aligned Engineering Baseline

This repository is the formal implementation baseline for the AX9S China engineering domain.

Conflict rule:
- Domain truth is owned by `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`.
- Execution discipline is owned by `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md`.
- The live execution entry is `docs/governance/CURRENT_TASK.yaml`.
- If any downstream file drifts, fix the downstream file. Do not weaken the authority source.

## Live Sources Of Truth

- Authority index: `docs/product/AUTHORITY_SPEC.md`
- Operator manual: `docs/governance/OPERATOR_MANUAL.md`
- Live task entry: `docs/governance/CURRENT_TASK.yaml`
- Task and worktree ledgers: `docs/governance/TASK_REGISTRY.yaml`, `docs/governance/WORKTREE_REGISTRY.yaml`
- Structure and module boundaries: `docs/governance/DIRECTORY_MAP.md`, `docs/governance/MODULE_MAP.yaml`
- Test gates: `docs/governance/TEST_MATRIX.yaml`
- Formal contracts: `docs/contracts/`

## What Is Already Real

- Governance control plane:
  - `scripts/check_repo.py`
  - `scripts/check_hygiene.py`
  - `scripts/task_ops.py`
  - `scripts/automation_runner.py`
- Formal contract assets:
  - `project_base`
  - `rule_hit`
  - `project_fact`
- Authority-critical regression chain:
  - `tests/stage3/`
  - `tests/stage4/`
  - `tests/stage6/`
  - `tests/integration/test_stage3_stage4_stage6_minimal_flow.py`

## Product Scope Snapshot

- China MVP formal scope is stage 2 through stage 6.
- Stage 7 through stage 9 are downstream consumers and optional business extensions in the current MVP.
- Stage 6 remains the only formal unified fact surface.
- Page, API, sales, contact, and delivery consumers must not rebuild top-level judgment outside `project_fact`.

## Local Validation

```powershell
python scripts/check_authority_alignment.py
python scripts/validate_contracts.py
python scripts/check_repo.py
python scripts/check_hygiene.py
pytest tests/contracts -q
pytest tests/governance -q
pytest tests/automation -q
pytest tests/integration -q
pytest -q
```

## Runtime Contract

- Python baseline: `>=3.10`
- Runtime dependencies: `PyYAML`, `jsonschema`
- Dev dependency baseline: `pytest`

Recommended local setup:

```powershell
python -m pip install -e .[dev]
```

If editable installs are not available, the compatible fallback is:

```powershell
python -m pip install -r requirements-dev.txt
```

Governance subprocess rule:

- Governance command strings may still be recorded as `python scripts/...` or `pytest ...`
- Actual subprocess execution must reuse the current interpreter (`sys.executable`)
- Governance Python subprocesses must not rely on `shell=True`

## Novice Entry

If you do not want to remember the governance terms, use this one command:

```powershell
python scripts/automation_intent.py execute --utterance "自动继续开发"
```

It will safely choose between:
- continue the live current task
- continue by roadmap when the repository is idle or the current task is review-ready
- stop with a clear blocker when the repo state is unsafe or ambiguous

## Repository Layout

- `docs/baseline/`: authority and execution baseline documents
- `docs/product/`: derived product-facing execution documents
- `docs/contracts/`: formal registries, schemas, examples, and field semantics
- `docs/governance/`: live control-plane documents
- `scripts/`: repository governance and validation entry points
- `tests/`: governance, contracts, automation, stage, and integration tests

## Current Non-Goals

- No stage-directory renaming.
- No second contracts root.
- No new business-stage implementation logic under the current governance hardening task.
