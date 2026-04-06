from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_project_base_example_matches_stage3_schema() -> None:
    schema = load_json(REPO_ROOT / "docs/contracts/schemas/stage3_project_base.schema.json")
    example = load_json(REPO_ROOT / "docs/contracts/examples/project_base.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_rule_hit_example_matches_stage4_schema() -> None:
    schema = load_json(REPO_ROOT / "docs/contracts/schemas/stage4_rule_hit.schema.json")
    example = load_json(REPO_ROOT / "docs/contracts/examples/rule_hit.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_stage7_sales_context_example_matches_schema() -> None:
    schema = load_json(REPO_ROOT / "docs/contracts/schemas/stage7_sales_context.schema.json")
    example = load_json(REPO_ROOT / "docs/contracts/examples/stage7_sales_context.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_stage8_contact_context_example_matches_schema() -> None:
    schema = load_json(REPO_ROOT / "docs/contracts/schemas/stage8_contact_context.schema.json")
    example = load_json(REPO_ROOT / "docs/contracts/examples/stage8_contact_context.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_stage9_delivery_payload_example_matches_schema() -> None:
    schema = load_json(REPO_ROOT / "docs/contracts/schemas/stage9_delivery_payload.schema.json")
    example = load_json(REPO_ROOT / "docs/contracts/examples/stage9_delivery_payload.example.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_stage_chain_field_semantics_present() -> None:
    project_base_fields = load_yaml(REPO_ROOT / "docs/contracts/field_semantics/project_base.fields.yaml")
    rule_hit_fields = load_yaml(REPO_ROOT / "docs/contracts/field_semantics/rule_hit.fields.yaml")
    assert project_base_fields["object_name"] == "project_base"
    assert rule_hit_fields["object_name"] == "rule_hit"
    assert len(project_base_fields["fields"]) >= 11
    assert len(rule_hit_fields["fields"]) >= 12
