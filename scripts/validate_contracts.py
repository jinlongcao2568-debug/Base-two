from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = ROOT / "docs" / "contracts"
SCHEMAS_DIR = CONTRACTS_DIR / "schemas"
EXAMPLES_DIR = CONTRACTS_DIR / "examples"
FIELD_SEMANTICS_DIR = CONTRACTS_DIR / "field_semantics"
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
FORMAL_ENUMS = {
    "sale_gate_status": ["OPEN", "REVIEW", "HOLD", "BLOCK"],
    "review_status": ["PENDING", "CONFIRMED", "REJECTED", "OVERRIDDEN"],
    "report_status": ["DRAFT", "READY", "ISSUED", "REVOKED"],
    "competitor_quality_grade": ["A", "B", "C", "D"],
    "result_type": ["AUTO_HIT", "CLUE", "OBSERVATION"],
    "severity": ["HIGH", "MEDIUM", "LOW"],
}
AUTHORITY_SNIPPETS = {
    "sale_gate_status": "`sale_gate_status`：仅允许 `OPEN / REVIEW / HOLD / BLOCK`",
    "review_status": "`review_status`：仅允许 `PENDING / CONFIRMED / REJECTED / OVERRIDDEN`",
    "report_status": "`report_status`：仅允许 `DRAFT / READY / ISSUED / REVOKED`",
}
CONTRACT_BUNDLES = [
    {
        "name": "project_base",
        "schema": SCHEMAS_DIR / "stage3_project_base.schema.json",
        "example": EXAMPLES_DIR / "project_base.example.json",
        "fields": FIELD_SEMANTICS_DIR / "project_base.fields.yaml",
        "object_name": "project_base",
        "required_fields": PROJECT_BASE_REQUIRED_FIELDS,
        "enum_fields": {},
        "const_field": None,
    },
    {
        "name": "rule_hit",
        "schema": SCHEMAS_DIR / "stage4_rule_hit.schema.json",
        "example": EXAMPLES_DIR / "rule_hit.example.json",
        "fields": FIELD_SEMANTICS_DIR / "rule_hit.fields.yaml",
        "object_name": "rule_hit",
        "required_fields": RULE_HIT_REQUIRED_FIELDS,
        "enum_fields": {
            "severity": FORMAL_ENUMS["severity"],
            "result_type": FORMAL_ENUMS["result_type"],
            "review_status": FORMAL_ENUMS["review_status"],
        },
        "const_field": None,
    },
    {
        "name": "project_fact",
        "schema": SCHEMAS_DIR / "stage6_project_fact.schema.json",
        "example": EXAMPLES_DIR / "project_fact.example.json",
        "fields": FIELD_SEMANTICS_DIR / "project_fact.fields.yaml",
        "object_name": "project_fact",
        "required_fields": PROJECT_FACT_REQUIRED_FIELDS,
        "enum_fields": {
            "sale_gate_status": FORMAL_ENUMS["sale_gate_status"],
            "review_status": FORMAL_ENUMS["review_status"],
            "report_status": FORMAL_ENUMS["report_status"],
            "competitor_quality_grade": FORMAL_ENUMS["competitor_quality_grade"],
        },
        "const_field": "project_fact",
    },
]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def print_errors(header: str, errors: list[str]) -> None:
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

        data = load_yaml(yaml_path)
        schema = load_json(schema_path)
        validator = Draft202012Validator(schema)
        file_errors = sorted(validator.iter_errors(data), key=lambda item: list(item.path))
        if file_errors:
            errors.append(f"validation failed: {yaml_name}")
            for item in file_errors:
                path = ".".join(str(part) for part in item.path) or "<root>"
                errors.append(f"{yaml_name}:{path}: {item.message}")
        else:
            print(f"[OK] {yaml_name}")
    return errors


def validate_authority_snippets() -> list[str]:
    text = AUTHORITY_FILE.read_text(encoding="utf-8")
    errors: list[str] = []
    for name, snippet in AUTHORITY_SNIPPETS.items():
        if snippet not in text:
            errors.append(f"authority document missing formal enum clause for {name}")
    return errors


def validate_contract_bundle(bundle: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for path in (EXAMPLES_DIR, FIELD_SEMANTICS_DIR):
        if not path.exists():
            errors.append(f"missing supporting directory: {path}")
    for file_path in (bundle["schema"], bundle["example"], bundle["fields"]):
        if not file_path.exists():
            errors.append(f"missing {bundle['name']} asset: {file_path}")
    if errors:
        return errors

    schema = load_json(bundle["schema"])
    example = load_json(bundle["example"])
    field_semantics = load_yaml(bundle["fields"])

    validator = Draft202012Validator(schema)
    example_errors = sorted(validator.iter_errors(example), key=lambda item: list(item.path))
    if example_errors:
        errors.append(f"{bundle['name']}.example failed schema validation")
        for item in example_errors:
            path = ".".join(str(part) for part in item.path) or "<root>"
            errors.append(f"{Path(bundle['example']).name}:{path}: {item.message}")
    else:
        print(f"[OK] {Path(bundle['example']).name}")

    properties = schema.get("properties", {})
    required = schema.get("required", [])
    if bundle["const_field"] and properties.get("object_type", {}).get("const") != bundle["const_field"]:
        errors.append(f"{Path(bundle['schema']).name} must require object_type={bundle['const_field']}")
    if schema.get("additionalProperties") is not False:
        errors.append(f"{Path(bundle['schema']).name} must set additionalProperties to false")
    for field in bundle["required_fields"]:
        if field not in required:
            errors.append(f"{Path(bundle['schema']).name} missing required field: {field}")
    for field_name, expected_values in bundle["enum_fields"].items():
        actual = properties.get(field_name, {}).get("enum")
        if actual != expected_values:
            errors.append(f"schema enum drift for {field_name}: expected {expected_values}, got {actual}")
        if example.get(field_name) not in expected_values:
            errors.append(f"example enum drift for {field_name}: {example.get(field_name)}")

    fields = field_semantics.get("fields") or []
    if not fields:
        errors.append(f"{bundle['name']} field semantics must declare non-empty fields")
        return errors
    indexed_fields = {item.get("name"): item for item in fields}
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
        semantics_values = indexed_fields.get(field_name, {}).get("enum")
        if semantics_values != expected_values:
            errors.append(f"field semantics enum drift for {field_name}: expected {expected_values}, got {semantics_values}")
    if not errors:
        print(f"[OK] {Path(bundle['schema']).name}")
        print(f"[OK] {Path(bundle['fields']).name}")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(validate_registry_files())
    authority_errors = validate_authority_snippets()
    if authority_errors:
        print_errors("authority enum alignment", authority_errors)
        errors.extend(authority_errors)
    else:
        print("[OK] authority enum alignment")

    for bundle in CONTRACT_BUNDLES:
        bundle_errors = validate_contract_bundle(bundle)
        if bundle_errors:
            print_errors(f"{bundle['name']} supporting assets", bundle_errors)
            errors.extend(bundle_errors)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
