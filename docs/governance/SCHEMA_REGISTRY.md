# AX9S SCHEMA_REGISTRY

Derived from the authority source:
- `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.5_全量规则码版.md`

Conflict rule:
- This file expands the authority baseline for execution and contract control.
- If any entry here conflicts with the authority document, the authority document wins and this registry must be corrected.

## 1. Formal Objects

The current formal object range is:

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
- `qualification_clause_profile`
- `parameter_requirement_profile`
- `vendor_fit_profile`
- `scoring_anomaly_profile`
- `tender_agent_profile`
- `split_procurement_profile`
- `post_award_change_profile`

## 2. Formal Global Enums

- `result_type`: `AUTO_HIT / CLUE / OBSERVATION`
- `evidence_grade`: `A / B / C`
- `sale_gate_status`: `OPEN / REVIEW / HOLD / BLOCK`
- `review_status`: `PENDING / CONFIRMED / REJECTED / OVERRIDDEN`
- `report_status`: `DRAFT / READY / ISSUED / REVOKED`
- `competitor_quality_grade`: `A / B / C / D`
- `coverage_sellable_state`: `NOT_READY / VALIDATING / SELLABLE / RESTRICTED / SUSPENDED / RECOVERING`
- `delivery_risk_state`: `OPEN / REVIEW / HOLD / BLOCK`
- `manual_override_status`: `NONE / PENDING / CONFIRMED / REJECTED`

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
- `report_record_ref`
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
- `coverage_sellable_state`
- `delivery_risk_state`
- `tender_fairness_risk`
- `evaluation_integrity_risk`
- `post_award_change_risk`
- `award_suspicion_summary`
- `report_status`
- `last_fact_refreshed_at`

### 3.2 `project_fact` Hard Rules

- `object_type` must be `project_fact`.
- Top-level `additionalProperties` must remain `false`.
- `sale_gate_status`, `review_status`, `report_status`, `competitor_quality_grade`, `coverage_sellable_state`, `delivery_risk_state`, and `manual_override_status` must remain pinned to the formal enums.
- `coverage_sellable_state` must come from `docs/contracts/coverage_governance_registry.yaml`.
- `delivery_risk_state` must only express delivery, approval, masking, evidence-grade, or audit blocking state.
- Page, API, sales, and later-stage consumers must not rebuild top-level judgment outside `project_fact`.

## 4. Formal Governance Assets

The live governance-side machine-readable assets are:

- `docs/contracts/coverage_governance_registry.yaml`
- `docs/contracts/field_policy_dictionary.yaml`
- `docs/contracts/delivery_object_matrix.yaml`
- `docs/contracts/customer_delivery_field_whitelist.yaml`
- `docs/contracts/customer_delivery_field_blacklist.yaml`
- `docs/contracts/region_coverage_registry.yaml`
- `docs/contracts/sources_registry.yaml`

## 5. Live Expanded Formal Contracts

The current repo-expansion set includes the following execution-grade assets:

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
- all 7 stage-3 profile objects
  - schema: `docs/contracts/schemas/stage3_*_profile.schema.json`
  - example: `docs/contracts/examples/*_profile.example.json`
  - field semantics: `docs/contracts/field_semantics/*_profile.fields.yaml`
- downstream consumers
  - schema: `docs/contracts/schemas/stage7_sales_context.schema.json`
  - schema: `docs/contracts/schemas/stage8_contact_context.schema.json`
  - schema: `docs/contracts/schemas/stage9_delivery_payload.schema.json`

## 6. Current Interface And Schema State

- Formal interfaces are now registered in `docs/governance/INTERFACE_CATALOG.yaml` as contract-level interfaces.
- `project_fact` remains the only stage-6 unified fact object and the only top-level judgment surface.
- Coverage, delivery, field-policy, and object-matrix governance are formal machine-readable assets and are not allowed to remain embedded-only semantics.
- The stage2/stage3/stage4/stage6/stage7/stage8/stage9 minimal chain must remain aligned with these formal contract assets.

## 7. Change Discipline

- Change a formal object: update the authority source first, then this registry, then the contract assets, then runtime and tests.
- Change a formal field or enum: update this registry, `docs/contracts/`, runtime, and tests in the same task.
- Change any stage-6 aggregate field: update fixtures, tests, and downstream consumers in the same task.
- Change any governance-side machine-readable asset: update the source YAML, its schema, and at least one contract/governance test in the same task.
