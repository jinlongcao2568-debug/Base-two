# TASK-GOV-032 V1.5全量对齐实施

## Task Baseline

- `task_id`: `TASK-GOV-032`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-v15-full-alignment-implementation-v1`
- `branch`: `feat/TASK-GOV-032-v15-full-alignment`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Align governance indexes, contract assets, runtime outputs, downstream consumers, and tests to the V1.5 authority baseline.
- Eliminate the current split where V1.5 is authoritative in baseline docs but governance indexes, schemas, examples, and runtimes still reflect V1.4-era or minimal-chain assumptions.
- Establish independent governance assets for coverage governance, field policy, and delivery object matrix so later implementation does not depend on embedded or duplicate structures.
- Finish this task only when the repo can truthfully claim stage2/stage3/stage4/stage6/stage7/stage8/stage9 minimal chain alignment to V1.5, not just documentation alignment.

## Explicitly Not Doing

- Do not modify `db/migrations/` or `README.md`.
- Do not introduce a formal web framework or fake HTTP handlers; interface work in this task is catalog- and contract-level because no web/API framework exists in the repo.
- Do not weaken V1.5 rules to fit old minimal-chain assumptions; contract and runtime changes must move toward the authority document, not the reverse.
- Do not leave new formal objects or governance fields as code-only concepts without contract assets.

## Acceptance Targets

- `SCHEMA_REGISTRY.md` and `INTERFACE_CATALOG.yaml` match the V1.5 baseline and no longer expose V1.4 authority references or zero-state API assumptions.
- Independent governance assets exist for `coverage_governance_registry`, `field_policy_dictionary`, and `delivery_object_matrix`, and customer delivery whitelist/blacklist content references them without duplicate semantics.
- Stage4/stage6 contract assets and examples reflect V1.5 rule codes, governance fields, and review-request semantics.
- Stage2/stage3/stage4/stage6 runtimes and stage7/stage8/stage9 consumer runtimes emit/consume the new V1.5 fields without rebuilding top-level judgment outside stage6.
- The minimal chain contract pipeline and scoped tests prove the new stage4/stage6/stage7/stage8/stage9 artifacts include `coverage_sellable_state`, `delivery_risk_state`, `manual_override_status`, and at least one new-topic rule hit.

## Allowed Dirs

- `docs/baseline/`
- `docs/governance/`
- `docs/contracts/`
- `src/domain/engineering/public_chain/`
- `scripts/`
- `src/stage2_ingestion/`
- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage6_facts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `src/shared/contracts/`
- `tests/contracts/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/integration/`
- `tests/governance/`

## Planned Write Paths

- `docs/baseline/`
- `docs/governance/`
- `docs/contracts/`
- `src/domain/engineering/public_chain/`
- `scripts/`
- `src/stage2_ingestion/`
- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage6_facts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `src/shared/contracts/`
- `tests/contracts/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/integration/`
- `tests/governance/`

## Planned Test Paths

- `tests/contracts/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `tests/integration/`
- `tests/governance/`

## Required Tests

- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`
- `pytest tests/contracts -q`
- `pytest tests/stage3 -q`
- `pytest tests/stage4 -q`
- `pytest tests/stage6 -q`
- `pytest tests/stage7 -q`
- `pytest tests/stage8 -q`
- `pytest tests/stage9 -q`
- `pytest tests/integration -q`

## Reserved Paths

- `db/migrations/`
- `README.md`
## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `db/migrations/, README.md`
- `branch`: `feat/TASK-GOV-032-v15-full-alignment`
- `updated_at`: `2026-04-07T10:09:30+08:00`
<!-- generated:task-meta:end -->
