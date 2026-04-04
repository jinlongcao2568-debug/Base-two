from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_stage6_project_fact_fixture_matches_schema_and_lineage() -> None:
    project_base = load_json(ROOT / "tests/fixtures/normalized/project_base.normalized.json")
    rule_hit = load_json(ROOT / "tests/fixtures/rules/rule_hit.normalized.json")
    project_fact = load_json(ROOT / "tests/fixtures/facts/project_fact.normalized.json")
    schema = load_json(ROOT / "docs/contracts/schemas/stage6_project_fact.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(project_fact), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]
    assert project_fact["project_base_ref"] == f"project_base:{project_base['project_id']}"
    assert project_fact["rule_hit_refs"] == [f"rule_hit:{rule_hit['rule_hit_id']}"]
    assert project_fact["sale_gate_status"] == "REVIEW"
