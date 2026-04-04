# AX9S Authority Spec

Derived from:
- `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`

Conflict rule:
- This file expands the baseline for repository execution.
- It does not redefine the baseline.
- If any detail here drifts from the baseline, the baseline wins.

## Non-Negotiable Rules

- Stage 6 is the only formal unified fact surface.
- No implementation may build a second top-level judgment path outside stage 6.
- Stage 7, stage 8, stage 9, pages, APIs, and business consumers must consume formal stage-6 facts rather than rebuild them.
- Any new capability must declare input, processing stage, output, consumer, public-boundary impact, and stage-6 impact.

## Formal Stage Chain

- Stage 2: public-source ingestion and public-chain discovery
- Stage 3: structured parsing into `project_base` and related formal objects
- Stage 4: rule validation into `rule_hit`, `evidence`, and review-request objects
- Stage 5: report and review outputs into `report_record`
- Stage 6: unified `project_fact`, sellability state, and downstream consumption
- Stage 7 to Stage 9: downstream consumption only; they do not redefine the core judgment

## Formal Objects Used By The Current Baseline

- `project_base`
- `rule_hit`
- `evidence`
- `review_request`
- `report_record`
- `project_fact`

## Formal Enums Currently Enforced In Repo Contracts

- `sale_gate_status`: `OPEN / REVIEW / HOLD / BLOCK`
- `review_status`: `PENDING / CONFIRMED / REJECTED / OVERRIDDEN`
- `report_status`: `DRAFT / READY / ISSUED / REVOKED`
- `competitor_quality_grade`: `A / B / C / D`
- `evidence_grade`: `A / B / C`
- `result_type`: `AUTO_HIT / CLUE / OBSERVATION`
- `severity`: `HIGH / MEDIUM / LOW`

## Consumption Rule

- `project_fact` is the only formal stage-6 unified fact object.
- Page and API layers must not bypass `project_fact`.
- Business-facing sellability and review state must remain visible through formal stage-6 fields.

## Current Repository Expansion

- Formal contracts live in `docs/contracts/`.
- Formal field and enum registry lives in `docs/governance/SCHEMA_REGISTRY.md`.
- Authority-critical regression proof currently covers `stage3 -> stage4 -> stage6`.
- The live formal contract set now covers `project_base`, `rule_hit`, `evidence`, `review_request`, `report_record`, and `project_fact`.
- The live handoff contract set now covers `stage3 -> stage4`, `stage4 -> stage6`, `stage5 -> stage6`, and `stage6 -> stage7/8/9`.
- Multi-sample regression proof now covers `case_review_ready`, `case_open_issued`, `case_hold_incomplete_chain`, and `case_block_high_risk`.
