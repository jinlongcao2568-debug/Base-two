from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_evidence_example_matches_stage4_schema() -> None:
    schema = load_json(ROOT / "docs/contracts/schemas/stage4_evidence.schema.json")
    example = load_json(ROOT / "docs/contracts/examples/evidence.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_review_request_example_matches_stage4_schema() -> None:
    schema = load_json(ROOT / "docs/contracts/schemas/stage4_review_request.schema.json")
    example = load_json(ROOT / "docs/contracts/examples/review_request.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_stage4_formal_field_semantics_cover_required_fields() -> None:
    evidence_fields = load_yaml(ROOT / "docs/contracts/field_semantics/evidence.fields.yaml")
    review_request_fields = load_yaml(ROOT / "docs/contracts/field_semantics/review_request.fields.yaml")

    evidence_index = {item["name"]: item for item in evidence_fields["fields"]}
    for field_name in (
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
    ):
        assert field_name in evidence_index
    assert evidence_index["evidence_grade"]["enum"] == ["A", "B", "C"]

    review_request_index = {item["name"]: item for item in review_request_fields["fields"]}
    for field_name in (
        "request_id",
        "project_id",
        "request_type",
        "reason",
        "public_basis",
        "requested_materials",
        "priority",
        "source_rule_codes",
    ):
        assert field_name in review_request_index
