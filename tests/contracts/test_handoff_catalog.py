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


def test_handoff_catalog_and_examples_match_schema() -> None:
    schema = load_json(ROOT / "docs/contracts/schemas/handoff_catalog.schema.json")
    catalog = load_yaml(ROOT / "docs/contracts/handoff_catalog.yaml")
    validator = Draft202012Validator(schema)
    catalog_errors = sorted(validator.iter_errors(catalog), key=lambda item: list(item.path))
    assert not catalog_errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in catalog_errors]

    handoff_validator = Draft202012Validator(schema["$defs"]["handoff"])
    example_dir = ROOT / "docs/contracts/examples/handoffs"
    example_ids: set[str] = set()
    for path in sorted(example_dir.glob("*.json")):
        payload = load_json(path)
        example_errors = sorted(handoff_validator.iter_errors(payload), key=lambda item: list(item.path))
        assert not example_errors, [f"{path.name}:{'.'.join(str(part) for part in error.path)}: {error.message}" for error in example_errors]
        example_ids.add(payload["handoff_id"])

    catalog_ids = {entry["handoff_id"] for entry in catalog["handoffs"]}
    assert example_ids == catalog_ids


def test_handoff_catalog_required_fields_exist_in_payload_contracts() -> None:
    catalog = load_yaml(ROOT / "docs/contracts/handoff_catalog.yaml")
    for entry in catalog["handoffs"]:
        payload_schema = load_json(ROOT / entry["payload_schema"])
        properties = payload_schema.get("properties", {})
        for field_name in entry["lineage_fields"]:
            assert field_name in properties, f"{entry['handoff_id']} missing lineage field {field_name}"
        for field_name in entry["required_payload_fields"]:
            assert field_name in properties, f"{entry['handoff_id']} missing required field {field_name}"
