# AX9S SCHEMA_REGISTRY

Derived from the authority source:
- `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`

Conflict rule:
- This file expands the authority document for execution and contract control.
- If any entry here conflicts with the authority document, the authority document wins and this registry must be corrected.

## 1. Formal Objects

The current formal object range remains:

- `project_base`
- `bidder_candidate`
- `project_manager`
- `public_chain`
- `invalid_bid`
- `opening_record`
- `contract_performance`
- `credit_penalty`
- `evidence`
- `rule_hit`
- `review_request`
- `report_record`
- `project_fact`

## 2. Formal Global Enums

- `result_type`: `AUTO_HIT / CLUE / OBSERVATION`
- `evidence_grade`: `A / B / C`
- `sale_gate_status`: `OPEN / REVIEW / HOLD / BLOCK`
- `review_status`: `PENDING / CONFIRMED / REJECTED / OVERRIDDEN`
- `report_status`: `DRAFT / READY / ISSUED / REVOKED`
- `competitor_quality_grade`: `A / B / C / D`

## 3. Stage-6 Formal Contract

The live formal stage-6 contract is:

- schema: `docs/contracts/schemas/stage6_project_fact.schema.json`
- example: `docs/contracts/examples/project_fact.example.json`
- field semantics: `docs/contracts/field_semantics/project_fact.fields.yaml`

### 3.1 `project_fact` Required Fields

- `object_type`
- `project_id`
- `fact_version`
- `fact_refresh_trigger`
- `fact_source_summary`
- `project_base_ref`
- `rule_hit_refs`
- `public_chain_status`
- `rule_hit_summary`
- `clue_summary`
- `sale_gate_status`
- `real_competitor_count`
- `serviceable_competitor_count`
- `competitor_quality_grade`
- `price_cluster_score`
- `price_gradient_pattern`
- `fact_summary`
- `risk_summary`
- `review_status`
- `manual_override_status`
- `report_status`
- `last_fact_refreshed_at`

### 3.2 `project_fact` Hard Rules

- `object_type` must be `project_fact`.
- Top-level `additionalProperties` must remain `false`.
- `sale_gate_status`, `review_status`, `report_status`, and `competitor_quality_grade` must remain pinned to the formal authority enums.
- Any aggregate field in `project_fact` must remain traceable to the formal stage-3, stage-4, stage-5, or review-state inputs.
- Page, API, sales, and later-stage consumers must not rebuild top-level judgment outside `project_fact`.

## 4. Live Expanded Formal Contracts

The current repo-expansion set now includes the following execution-grade assets:

- `project_base`
  - schema: `docs/contracts/schemas/stage3_project_base.schema.json`
  - example: `docs/contracts/examples/project_base.example.json`
  - field semantics: `docs/contracts/field_semantics/project_base.fields.yaml`
- `rule_hit`
  - schema: `docs/contracts/schemas/stage4_rule_hit.schema.json`
  - example: `docs/contracts/examples/rule_hit.example.json`
  - field semantics: `docs/contracts/field_semantics/rule_hit.fields.yaml`
- `evidence`
  - schema: `docs/contracts/schemas/stage4_evidence.schema.json`
  - example: `docs/contracts/examples/evidence.example.json`
  - field semantics: `docs/contracts/field_semantics/evidence.fields.yaml`
- `review_request`
  - schema: `docs/contracts/schemas/stage4_review_request.schema.json`
  - example: `docs/contracts/examples/review_request.example.json`
  - field semantics: `docs/contracts/field_semantics/review_request.fields.yaml`
- `report_record`
  - schema: `docs/contracts/schemas/stage5_report_record.schema.json`
  - example: `docs/contracts/examples/report_record.example.json`
  - field semantics: `docs/contracts/field_semantics/report_record.fields.yaml`
- `project_fact`
  - schema: `docs/contracts/schemas/stage6_project_fact.schema.json`
  - example: `docs/contracts/examples/project_fact.example.json`
  - field semantics: `docs/contracts/field_semantics/project_fact.fields.yaml`

## 5. Current Interface And Schema State

- No public business API contract is registered yet; `INTERFACE_CATALOG.yaml` remains the control point for future external or customer-facing interfaces.
- `project_fact` remains the only stage-6 unified fact object and the only top-level judgment surface.
- `docs/contracts/handoff_catalog.yaml` is now the machine-readable handoff control point for the live authority-critical chain and the `stage6 -> stage7/8/9` downstream inputs.
- Formal objects outside the six live expanded contracts above remain authority-defined and must still be expanded before they are allowed to become new customer-visible or integration-critical contracts.

## 6. Change Discipline

- Change a formal object: update the authority source first, then this registry, then the contract assets, then tests.
- Change a formal field or enum: update this registry, `docs/contracts/`, and tests in the same task.
- Change any stage-6 aggregate field: update fixtures, tests, and downstream consumers in the same task.
