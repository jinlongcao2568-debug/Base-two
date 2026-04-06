from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = ROOT / "docs" / "contracts"
SCHEMAS_DIR = CONTRACTS_DIR / "schemas"
EXAMPLES_DIR = CONTRACTS_DIR / "examples"
FIELD_SEMANTICS_DIR = CONTRACTS_DIR / "field_semantics"
HANDOFF_EXAMPLES_DIR = EXAMPLES_DIR / "handoffs"
AUTHORITY_FILE = ROOT / "docs" / "baseline" / "AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md"
ROOT_DUPLICATES = [
    ROOT / "sources_registry.yaml",
    ROOT / "region_coverage_registry.yaml",
    ROOT / "customer_delivery_field_whitelist.yaml",
    ROOT / "customer_delivery_field_blacklist.yaml",
]

REGISTRY_FILES = {
    "sources_registry.yaml": "sources_registry.schema.json",
    "region_coverage_registry.yaml": "region_coverage_registry.schema.json",
    "customer_delivery_field_whitelist.yaml": "customer_delivery_field_whitelist.schema.json",
    "customer_delivery_field_blacklist.yaml": "customer_delivery_field_blacklist.schema.json",
}

PROJECT_BASE_REQUIRED_FIELDS = [
    "project_id",
    "source_family",
    "region_code",
    "project_name",
    "project_type_raw",
    "engineering_domain",
    "bid_control_price",
    "bid_eval_method",
    "public_chain_status",
    "opening_record_count",
    "invalid_bid_count",
]
RULE_HIT_REQUIRED_FIELDS = [
    "rule_hit_id",
    "project_id",
    "rule_code",
    "severity",
    "confidence",
    "result_type",
    "why_hit",
    "boundary_note",
    "evidence_refs",
    "target_entity_type",
    "target_entity_id",
    "review_status",
]
EVIDENCE_REQUIRED_FIELDS = [
    "evidence_id",
    "project_id",
    "source_url",
    "source_type",
    "capture_type",
    "capture_time",
    "page_title",
    "snippet",
    "evidence_artifact_refs",
    "structured_field_refs",
    "consumed_by_rule_codes",
    "evidence_grade",
    "evidence_hash",
]
REVIEW_REQUEST_REQUIRED_FIELDS = [
    "request_id",
    "project_id",
    "request_type",
    "reason",
    "public_basis",
    "requested_materials",
    "priority",
    "source_rule_codes",
]
PROJECT_FACT_REQUIRED_FIELDS = [
    "object_type",
    "project_id",
    "fact_version",
    "fact_refresh_trigger",
    "fact_source_summary",
    "project_base_ref",
    "rule_hit_refs",
    "public_chain_status",
    "rule_hit_summary",
    "clue_summary",
    "sale_gate_status",
    "real_competitor_count",
    "serviceable_competitor_count",
    "competitor_quality_grade",
    "price_cluster_score",
    "price_gradient_pattern",
    "fact_summary",
    "risk_summary",
    "review_status",
    "manual_override_status",
    "report_status",
    "last_fact_refreshed_at",
]
REPORT_RECORD_REQUIRED_FIELDS = [
    "report_id",
    "project_id",
    "brief_path",
    "evidence_pack_path",
    "objection_draft_path",
    "review_request_list_path",
    "review_task_status",
    "report_status",
    "written_back_at",
]
SALES_CONTEXT_REQUIRED_FIELDS = [
    "object_type",
    "context_ref",
    "project_id",
    "fact_version",
    "source_project_fact_ref",
    "sale_gate_status",
    "real_competitor_count",
    "serviceable_competitor_count",
    "competitor_quality_grade",
    "price_cluster_score",
    "price_gradient_pattern",
    "sales_readiness_bucket",
    "recommended_sales_action",
    "summary",
]
CONTACT_CONTEXT_REQUIRED_FIELDS = [
    "object_type",
    "context_ref",
    "project_id",
    "fact_version",
    "source_project_fact_ref",
    "public_chain_status",
    "sale_gate_status",
    "review_status",
    "manual_override_status",
    "contact_strategy",
    "analyst_follow_up_required",
    "summary",
]
DELIVERY_PAYLOAD_REQUIRED_FIELDS = [
    "object_type",
    "payload_ref",
    "project_id",
    "fact_version",
    "source_project_fact_ref",
    "sales_context_ref",
    "contact_context_ref",
    "report_record_ref",
    "sale_gate_status",
    "review_status",
    "report_status",
    "delivery_readiness",
    "fact_summary",
    "risk_summary",
    "payload_summary",
]
FORMAL_ENUMS = {
    "sale_gate_status": ["OPEN", "REVIEW", "HOLD", "BLOCK"],
    "review_status": ["PENDING", "CONFIRMED", "REJECTED", "OVERRIDDEN"],
    "report_status": ["DRAFT", "READY", "ISSUED", "REVOKED"],
    "competitor_quality_grade": ["A", "B", "C", "D"],
    "evidence_grade": ["A", "B", "C"],
    "result_type": ["AUTO_HIT", "CLUE", "OBSERVATION"],
    "severity": ["HIGH", "MEDIUM", "LOW"],
}
AUTHORITY_SNIPPETS = {
    "sale_gate_status": "`sale_gate_status`：仅允许 `OPEN / REVIEW / HOLD / BLOCK`",
    "review_status": "`review_status`：仅允许 `PENDING / CONFIRMED / REJECTED / OVERRIDDEN`",
    "report_status": "`report_status`：仅允许 `DRAFT / READY / ISSUED / REVOKED`",
}
HANDOFF_REQUIRED_IDS = {
    "stage3-to-stage4-project_base",
    "stage4-to-stage6-rule_hit",
    "stage5-to-stage6-report_record",
    "stage6-to-stage7-project_fact",
    "stage6-to-stage8-project_fact",
    "stage6-to-stage9-project_fact",
}
MINIMAL_ACCEPTANCE_CASES = (
    "case_review_ready",
    "case_open_issued",
    "case_hold_incomplete_chain",
    "case_block_high_risk",
)

CONTRACT_BUNDLES = [
    {"name": "project_base", "schema": SCHEMAS_DIR / "stage3_project_base.schema.json", "example": EXAMPLES_DIR / "project_base.example.json", "fields": FIELD_SEMANTICS_DIR / "project_base.fields.yaml", "object_name": "project_base", "required_fields": PROJECT_BASE_REQUIRED_FIELDS, "enum_fields": {}, "const_field": None},
    {"name": "rule_hit", "schema": SCHEMAS_DIR / "stage4_rule_hit.schema.json", "example": EXAMPLES_DIR / "rule_hit.example.json", "fields": FIELD_SEMANTICS_DIR / "rule_hit.fields.yaml", "object_name": "rule_hit", "required_fields": RULE_HIT_REQUIRED_FIELDS, "enum_fields": {"severity": FORMAL_ENUMS["severity"], "result_type": FORMAL_ENUMS["result_type"], "review_status": FORMAL_ENUMS["review_status"]}, "const_field": None},
    {"name": "evidence", "schema": SCHEMAS_DIR / "stage4_evidence.schema.json", "example": EXAMPLES_DIR / "evidence.example.json", "fields": FIELD_SEMANTICS_DIR / "evidence.fields.yaml", "object_name": "evidence", "required_fields": EVIDENCE_REQUIRED_FIELDS, "enum_fields": {"evidence_grade": FORMAL_ENUMS["evidence_grade"]}, "const_field": None},
    {"name": "review_request", "schema": SCHEMAS_DIR / "stage4_review_request.schema.json", "example": EXAMPLES_DIR / "review_request.example.json", "fields": FIELD_SEMANTICS_DIR / "review_request.fields.yaml", "object_name": "review_request", "required_fields": REVIEW_REQUEST_REQUIRED_FIELDS, "enum_fields": {}, "const_field": None},
    {"name": "project_fact", "schema": SCHEMAS_DIR / "stage6_project_fact.schema.json", "example": EXAMPLES_DIR / "project_fact.example.json", "fields": FIELD_SEMANTICS_DIR / "project_fact.fields.yaml", "object_name": "project_fact", "required_fields": PROJECT_FACT_REQUIRED_FIELDS, "enum_fields": {"sale_gate_status": FORMAL_ENUMS["sale_gate_status"], "review_status": FORMAL_ENUMS["review_status"], "report_status": FORMAL_ENUMS["report_status"], "competitor_quality_grade": FORMAL_ENUMS["competitor_quality_grade"]}, "const_field": "project_fact"},
    {"name": "report_record", "schema": SCHEMAS_DIR / "stage5_report_record.schema.json", "example": EXAMPLES_DIR / "report_record.example.json", "fields": FIELD_SEMANTICS_DIR / "report_record.fields.yaml", "object_name": "report_record", "required_fields": REPORT_RECORD_REQUIRED_FIELDS, "enum_fields": {"report_status": FORMAL_ENUMS["report_status"]}, "const_field": None},
    {"name": "sales_context", "schema": SCHEMAS_DIR / "stage7_sales_context.schema.json", "example": EXAMPLES_DIR / "stage7_sales_context.example.json", "fields": None, "object_name": "sales_context", "required_fields": SALES_CONTEXT_REQUIRED_FIELDS, "enum_fields": {"sale_gate_status": FORMAL_ENUMS["sale_gate_status"], "competitor_quality_grade": FORMAL_ENUMS["competitor_quality_grade"], "sales_readiness_bucket": ["ready", "needs_review", "hold", "blocked"]}, "const_field": "sales_context"},
    {"name": "contact_context", "schema": SCHEMAS_DIR / "stage8_contact_context.schema.json", "example": EXAMPLES_DIR / "stage8_contact_context.example.json", "fields": None, "object_name": "contact_context", "required_fields": CONTACT_CONTEXT_REQUIRED_FIELDS, "enum_fields": {"sale_gate_status": FORMAL_ENUMS["sale_gate_status"], "review_status": FORMAL_ENUMS["review_status"], "contact_strategy": ["standard_outreach", "analyst_review_required", "hold_no_outreach", "block_external_contact"]}, "const_field": "contact_context"},
    {"name": "delivery_payload", "schema": SCHEMAS_DIR / "stage9_delivery_payload.schema.json", "example": EXAMPLES_DIR / "stage9_delivery_payload.example.json", "fields": None, "object_name": "delivery_payload", "required_fields": DELIVERY_PAYLOAD_REQUIRED_FIELDS, "enum_fields": {"sale_gate_status": FORMAL_ENUMS["sale_gate_status"], "review_status": FORMAL_ENUMS["review_status"], "report_status": FORMAL_ENUMS["report_status"], "delivery_readiness": ["ready", "review_pending", "on_hold", "blocked"]}, "const_field": "delivery_payload"},
]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validator_errors(validator: Draft202012Validator, payload: dict[str, Any]) -> list[Any]:
    return sorted(validator.iter_errors(payload), key=lambda item: list(item.path))


def _format_validator_errors(path: Path, errors: list[Any]) -> list[str]:
    messages: list[str] = []
    for item in errors:
        location = ".".join(str(part) for part in item.path) or "<root>"
        messages.append(f"{path.name}:{location}: {item.message}")
    return messages


def _print_errors(header: str, errors: list[str]) -> None:
    print(f"[ERROR] {header}")
    for error in errors:
        print(f"  - {error}")


def validate_registry_files() -> list[str]:
    errors: list[str] = []
    for duplicate in ROOT_DUPLICATES:
        if duplicate.exists():
            errors.append(f"duplicate contract yaml outside docs/contracts: {duplicate}")
    for yaml_name, schema_name in REGISTRY_FILES.items():
        yaml_path = CONTRACTS_DIR / yaml_name
        schema_path = SCHEMAS_DIR / schema_name
        if not yaml_path.exists():
            errors.append(f"missing yaml: {yaml_path}")
            continue
        if not schema_path.exists():
            errors.append(f"missing schema: {schema_path}")
            continue
        file_errors = _validator_errors(Draft202012Validator(_load_json(schema_path)), _load_yaml(yaml_path))
        if file_errors:
            errors.append(f"validation failed: {yaml_name}")
            errors.extend(_format_validator_errors(yaml_path, file_errors))
            continue
        print(f"[OK] {yaml_name}")
    return errors


def validate_authority_snippets() -> list[str]:
    text = AUTHORITY_FILE.read_text(encoding="utf-8")
    return [
        f"authority document missing formal enum clause for {name}"
        for name, snippet in AUTHORITY_SNIPPETS.items()
        if snippet not in text
    ]


def _validate_bundle_assets(bundle: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for directory in (EXAMPLES_DIR,):
        if not directory.exists():
            errors.append(f"missing supporting directory: {directory}")
    field_path = bundle.get("fields")
    if field_path is not None and not FIELD_SEMANTICS_DIR.exists():
        errors.append(f"missing supporting directory: {FIELD_SEMANTICS_DIR}")
    files = [bundle["schema"], bundle["example"]]
    if field_path is not None:
        files.append(field_path)
    for file_path in files:
        if not Path(file_path).exists():
            errors.append(f"missing {bundle['name']} asset: {file_path}")
    return errors


def _validate_bundle_schema(bundle: dict[str, object], schema: dict[str, Any], example: dict[str, Any]) -> list[str]:
    errors = _format_validator_errors(Path(bundle["example"]), _validator_errors(Draft202012Validator(schema), example))
    if errors:
        return [f"{bundle['name']}.example failed schema validation", *errors]
    print(f"[OK] {Path(bundle['example']).name}")
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    contract_errors: list[str] = []
    const_field = bundle["const_field"]
    if const_field and properties.get("object_type", {}).get("const") != const_field:
        contract_errors.append(f"{Path(bundle['schema']).name} must require object_type={const_field}")
    if schema.get("additionalProperties") is not False:
        contract_errors.append(f"{Path(bundle['schema']).name} must set additionalProperties to false")
    for field in bundle["required_fields"]:
        if field not in required:
            contract_errors.append(f"{Path(bundle['schema']).name} missing required field: {field}")
    for field_name, expected_values in bundle["enum_fields"].items():
        if properties.get(field_name, {}).get("enum") != expected_values:
            contract_errors.append(f"schema enum drift for {field_name}: expected {expected_values}, got {properties.get(field_name, {}).get('enum')}")
        if example.get(field_name) not in expected_values:
            contract_errors.append(f"example enum drift for {field_name}: {example.get(field_name)}")
    return contract_errors


def _validate_bundle_fields(bundle: dict[str, object], field_semantics: dict[str, Any]) -> list[str]:
    fields = field_semantics.get("fields") or []
    if not fields:
        return [f"{bundle['name']} field semantics must declare non-empty fields"]
    indexed_fields = {item.get("name"): item for item in fields}
    errors: list[str] = []
    for field in bundle["required_fields"]:
        if field not in indexed_fields:
            errors.append(f"field semantics missing {bundle['name']} field: {field}")
    if field_semantics.get("object_name") != bundle["object_name"]:
        errors.append(f"{bundle['name']} field semantics must declare object_name={bundle['object_name']}")
    if field_semantics.get("schema_file") != f"docs/contracts/schemas/{Path(bundle['schema']).name}":
        errors.append(f"{bundle['name']} field semantics must point to the formal schema path")
    if field_semantics.get("example_file") != f"docs/contracts/examples/{Path(bundle['example']).name}":
        errors.append(f"{bundle['name']} field semantics must point to the formal example path")
    for field_name, expected_values in bundle["enum_fields"].items():
        if indexed_fields.get(field_name, {}).get("enum") != expected_values:
            errors.append(f"field semantics enum drift for {field_name}: expected {expected_values}, got {indexed_fields.get(field_name, {}).get('enum')}")
    if not errors:
        print(f"[OK] {Path(bundle['schema']).name}")
        print(f"[OK] {Path(bundle['fields']).name}")
    return errors


def validate_contract_bundle(bundle: dict[str, object]) -> list[str]:
    errors = _validate_bundle_assets(bundle)
    if errors:
        return errors
    schema = _load_json(Path(bundle["schema"]))
    example = _load_json(Path(bundle["example"]))
    bundle_errors = _validate_bundle_schema(bundle, schema, example)
    if bundle.get("fields") is None:
        return bundle_errors
    field_semantics = _load_yaml(Path(bundle["fields"]))
    return [*bundle_errors, *_validate_bundle_fields(bundle, field_semantics)]


def validate_minimal_chain_acceptance_contract() -> list[str]:
    path = CONTRACTS_DIR / "minimal_runtime_chain_acceptance.yaml"
    if not path.exists():
        return [f"missing acceptance contract: {path}"]
    document = _load_yaml(path)
    acceptance = document.get("acceptance") or {}
    errors: list[str] = []
    if not acceptance.get("acceptance_id"):
        errors.append("acceptance contract missing acceptance_id")
    for field_name in ("artifacts", "schema_checks", "fixture_checks"):
        if not acceptance.get(field_name):
            errors.append(f"acceptance contract missing {field_name}")
    for artifact_key in ("stage7.sales_context", "stage8.contact_context", "stage9.delivery_payload"):
        if artifact_key not in (acceptance.get("artifacts") or []):
            errors.append(f"acceptance contract missing artifact: {artifact_key}")
        schema_path = acceptance.get("schema_checks", {}).get(artifact_key)
        fixture_pattern = acceptance.get("fixture_checks", {}).get(artifact_key)
        if not schema_path or not (ROOT / schema_path).exists():
            errors.append(f"acceptance contract missing schema target for {artifact_key}")
        if not fixture_pattern:
            errors.append(f"acceptance contract missing fixture target for {artifact_key}")
        else:
            for case_id in MINIMAL_ACCEPTANCE_CASES:
                fixture_path = ROOT / fixture_pattern.format(scenario_id=case_id)
                if not fixture_path.exists():
                    errors.append(f"acceptance fixture missing for {artifact_key}: {fixture_path}")
    whitelist_path = acceptance.get("consumer_field_whitelist")
    if not whitelist_path or not (ROOT / whitelist_path).exists():
        errors.append("acceptance contract missing consumer_field_whitelist target")
    if not errors:
        print(f"[OK] {path.name}")
    return errors


def _validate_handoff_field_semantics(fields_path: Path) -> list[str]:
    payload = _load_yaml(fields_path)
    fields = payload.get("fields") or []
    errors: list[str] = []
    if payload.get("object_name") != "handoff_catalog":
        errors.append("handoff field semantics must declare object_name=handoff_catalog")
    if payload.get("schema_file") != "docs/contracts/schemas/handoff_catalog.schema.json":
        errors.append("handoff field semantics must point to the formal schema path")
    required_names = {"handoff_id", "producer_stage", "consumer_stage", "payload_object", "payload_schema", "payload_example", "lineage_fields", "required_payload_fields", "consumer_boundary", "customer_visible", "authority_source_section"}
    if not fields:
        errors.append("handoff field semantics must declare non-empty fields")
    else:
        indexed = {item.get("name") for item in fields}
        for field_name in required_names:
            if field_name not in indexed:
                errors.append(f"handoff field semantics missing field: {field_name}")
    if not errors:
        print(f"[OK] {fields_path.name}")
    return errors


def _validate_handoff_examples(schema: dict[str, Any], entry_ids: set[str]) -> list[str]:
    validator = Draft202012Validator(schema["$defs"]["handoff"])
    example_ids: set[str] = set()
    errors: list[str] = []
    for path in sorted(HANDOFF_EXAMPLES_DIR.glob("*.json")):
        file_errors = _format_validator_errors(path, _validator_errors(validator, _load_json(path)))
        if file_errors:
            errors.append(f"handoff example failed schema validation: {path.name}")
            errors.extend(file_errors)
            continue
        example_ids.add(_load_json(path)["handoff_id"])
        print(f"[OK] {path.name}")
    if example_ids != entry_ids:
        errors.append(f"handoff examples drift from catalog entries: expected {sorted(entry_ids)}, got {sorted(example_ids)}")
    return errors


def _validate_handoff_payload_refs(entries: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        payload_schema_path = ROOT / entry["payload_schema"]
        payload_example_path = ROOT / entry["payload_example"]
        if not payload_schema_path.exists():
            errors.append(f"handoff missing payload schema target: {entry['handoff_id']} -> {payload_schema_path}")
            continue
        if not payload_example_path.exists():
            errors.append(f"handoff missing payload example target: {entry['handoff_id']} -> {payload_example_path}")
            continue
        properties = _load_json(payload_schema_path).get("properties", {})
        for field_name in [*entry.get("lineage_fields", []), *entry.get("required_payload_fields", [])]:
            if field_name not in properties:
                errors.append(f"handoff field missing in payload schema: {entry['handoff_id']} -> {field_name}")
    return errors


def validate_handoff_catalog() -> list[str]:
    catalog_path = CONTRACTS_DIR / "handoff_catalog.yaml"
    schema_path = SCHEMAS_DIR / "handoff_catalog.schema.json"
    fields_path = FIELD_SEMANTICS_DIR / "handoff_catalog.fields.yaml"
    errors = [f"missing handoff asset: {path}" for path in (catalog_path, schema_path, fields_path) if not path.exists()]
    if not HANDOFF_EXAMPLES_DIR.exists():
        errors.append(f"missing handoff examples directory: {HANDOFF_EXAMPLES_DIR}")
    if errors:
        return errors
    schema = _load_json(schema_path)
    catalog = _load_yaml(catalog_path)
    catalog_errors = _format_validator_errors(catalog_path, _validator_errors(Draft202012Validator(schema), catalog))
    if catalog_errors:
        return ["handoff catalog failed schema validation", *catalog_errors]
    print(f"[OK] {catalog_path.name}")
    entries = catalog.get("handoffs") or []
    entry_ids = {entry["handoff_id"] for entry in entries}
    errors = []
    if entry_ids != HANDOFF_REQUIRED_IDS:
        errors.append(f"handoff catalog ids drift: expected {sorted(HANDOFF_REQUIRED_IDS)}, got {sorted(entry_ids)}")
    errors.extend(_validate_handoff_field_semantics(fields_path))
    errors.extend(_validate_handoff_examples(schema, entry_ids))
    errors.extend(_validate_handoff_payload_refs(entries))
    return errors


def main() -> int:
    errors = validate_registry_files()
    authority_errors = validate_authority_snippets()
    if authority_errors:
        _print_errors("authority enum alignment", authority_errors)
        errors.extend(authority_errors)
    else:
        print("[OK] authority enum alignment")
    for bundle in CONTRACT_BUNDLES:
        bundle_errors = validate_contract_bundle(bundle)
        if bundle_errors:
            _print_errors(f"{bundle['name']} supporting assets", bundle_errors)
            errors.extend(bundle_errors)
    handoff_errors = validate_handoff_catalog()
    if handoff_errors:
        _print_errors("handoff catalog assets", handoff_errors)
        errors.extend(handoff_errors)
    acceptance_errors = validate_minimal_chain_acceptance_contract()
    if acceptance_errors:
        _print_errors("minimal chain acceptance contract", acceptance_errors)
        errors.extend(acceptance_errors)
    return 1 if errors else 0
