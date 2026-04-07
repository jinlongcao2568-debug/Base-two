from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]

PROFILE_NAMES = (
    "qualification_clause_profile",
    "parameter_requirement_profile",
    "vendor_fit_profile",
    "scoring_anomaly_profile",
    "tender_agent_profile",
    "split_procurement_profile",
    "post_award_change_profile",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_v15_profile_assets_exist_and_validate() -> None:
    for name in PROFILE_NAMES:
        schema = ROOT / f"docs/contracts/schemas/stage3_{name}.schema.json"
        example = ROOT / f"docs/contracts/examples/{name}.example.json"
        fields = ROOT / f"docs/contracts/field_semantics/{name}.fields.yaml"
        schema_payload = load_json(schema)
        example_payload = load_json(example)
        errors = sorted(Draft202012Validator(schema_payload).iter_errors(example_payload), key=lambda item: list(item.path))
        assert not errors, [f"{name}: {'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]
        field_semantics = load_yaml(fields)
        assert field_semantics["object_name"] == name
        assert field_semantics["schema_file"].endswith(f"stage3_{name}.schema.json")
        assert field_semantics["example_file"].endswith(f"{name}.example.json")
