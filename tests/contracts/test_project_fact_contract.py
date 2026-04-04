from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "docs/contracts/schemas/stage6_project_fact.schema.json"
EXAMPLE_PATH = REPO_ROOT / "docs/contracts/examples/project_fact.example.json"
FIELD_SEMANTICS_PATH = REPO_ROOT / "docs/contracts/field_semantics/project_fact.fields.yaml"
FORMAL_ENUMS = {
    "sale_gate_status": ["OPEN", "REVIEW", "HOLD", "BLOCK"],
    "review_status": ["PENDING", "CONFIRMED", "REJECTED", "OVERRIDDEN"],
    "report_status": ["DRAFT", "READY", "ISSUED", "REVOKED"],
    "competitor_quality_grade": ["A", "B", "C", "D"],
}
REQUIRED_FIELDS = {
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
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_project_fact_example_matches_formal_schema() -> None:
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_project_fact_schema_pins_formal_enums_and_required_fields() -> None:
    schema = load_json(SCHEMA_PATH)
    assert schema["properties"]["object_type"]["const"] == "project_fact"
    assert schema["additionalProperties"] is False
    assert REQUIRED_FIELDS <= set(schema["required"])
    for field_name, expected_values in FORMAL_ENUMS.items():
        assert schema["properties"][field_name]["enum"] == expected_values


def test_project_fact_field_semantics_tracks_schema_and_example() -> None:
    semantics = load_yaml(FIELD_SEMANTICS_PATH)
    assert semantics["object_name"] == "project_fact"
    assert semantics["schema_file"] == "docs/contracts/schemas/stage6_project_fact.schema.json"
    assert semantics["example_file"] == "docs/contracts/examples/project_fact.example.json"
    fields = {item["name"]: item for item in semantics["fields"]}
    assert REQUIRED_FIELDS <= set(fields)
    for field_name, expected_values in FORMAL_ENUMS.items():
        assert fields[field_name]["enum"] == expected_values
