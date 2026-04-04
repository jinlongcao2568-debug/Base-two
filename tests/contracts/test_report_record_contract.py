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


def test_report_record_example_matches_stage5_schema() -> None:
    schema = load_json(ROOT / "docs/contracts/schemas/stage5_report_record.schema.json")
    example = load_json(ROOT / "docs/contracts/examples/report_record.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_report_record_field_semantics_cover_required_fields() -> None:
    field_semantics = load_yaml(ROOT / "docs/contracts/field_semantics/report_record.fields.yaml")
    assert field_semantics["object_name"] == "report_record"
    assert field_semantics["schema_file"] == "docs/contracts/schemas/stage5_report_record.schema.json"
    assert field_semantics["example_file"] == "docs/contracts/examples/report_record.example.json"
    indexed_fields = {item["name"]: item for item in field_semantics["fields"]}
    for field_name in (
        "report_id",
        "project_id",
        "brief_path",
        "evidence_pack_path",
        "objection_draft_path",
        "review_request_list_path",
        "review_task_status",
        "report_status",
        "written_back_at",
    ):
        assert field_name in indexed_fields
    assert indexed_fields["report_status"]["enum"] == ["DRAFT", "READY", "ISSUED", "REVOKED"]
