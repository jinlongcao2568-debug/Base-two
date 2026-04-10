# AX9S Product Engineering Baseline

This repository is the implementation baseline for the AX9S China engineering domain.

Conflict rule:
- Domain truth is owned by `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`.
- Execution guidance is derived from the baseline documents under `docs/baseline/`.
- If any downstream file drifts, fix the downstream file. Do not weaken the authority source.

## Start Here

Default reading order:
- `docs/product/AUTHORITY_SPEC.md`
- `docs/product/MVP_SCOPE.md`
- `docs/product/PRODUCT_BOUNDARIES.md`
- `docs/contracts/`
- `docs/INDEX.md`

## What Stays Core

High-value repository content:
- `docs/baseline/`
- `docs/product/`
- `docs/contracts/`
- `src/domain/engineering/`
- `src/shared/`
- `src/stage2_ingestion/` to `src/stage6_facts/`
- `tests/contracts/`
- `tests/integration/`
- `tests/stage2/` to `tests/stage6/`

## Product Scope Snapshot

- China MVP formal scope is stage 2 through stage 6.
- Stage 7 through stage 9 are downstream consumers and optional business extensions in the current MVP.
- Stage 6 remains the only formal unified fact surface.
- Page, API, sales, contact, and delivery consumers must not rebuild top-level judgment outside `project_fact`.

## Local Validation

```powershell
python scripts/validate_contracts.py
pytest tests/contracts -q
pytest tests/integration/test_stage3_stage4_stage6_minimal_flow.py -q
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

## Repository Layout

- `docs/baseline/`: authority and execution baseline documents
- `docs/product/`: product-facing execution documents
- `docs/contracts/`: registries, schemas, examples, and field semantics
- `scripts/`: retained product and validation entry points
- `src/`: domain, shared, and stage implementation code
- `tests/`: contract, integration, and stage regression tests

## Current Non-Goals

- No stage-directory renaming.
- No second contracts root.
- No new business-stage implementation logic outside the formal stage chain.
