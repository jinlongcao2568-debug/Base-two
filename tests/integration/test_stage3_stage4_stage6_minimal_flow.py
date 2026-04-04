from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, payload: dict) -> None:
    schema = load_json(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_stage3_stage4_stage6_minimal_flow_is_real_consumption() -> None:
    project_base = load_json(ROOT / "tests/fixtures/normalized/project_base.normalized.json")
    rule_hit = load_json(ROOT / "tests/fixtures/rules/rule_hit.normalized.json")
    project_fact = load_json(ROOT / "tests/fixtures/facts/project_fact.normalized.json")
    golden = load_json(ROOT / "tests/fixtures/golden/stage3_stage4_stage6_minimal_flow.golden.json")

    validate(ROOT / "docs/contracts/schemas/stage3_project_base.schema.json", project_base)
    validate(ROOT / "docs/contracts/schemas/stage4_rule_hit.schema.json", rule_hit)
    validate(ROOT / "docs/contracts/schemas/stage6_project_fact.schema.json", project_fact)

    assert project_base["project_id"] == rule_hit["project_id"] == project_fact["project_id"]
    assert project_fact["project_base_ref"] == golden["expected_project_base_ref"]
    assert project_fact["rule_hit_refs"] == [golden["expected_rule_hit_ref"]]
    assert project_fact["sale_gate_status"] == golden["expected_sale_gate_status"]
    assert project_fact["review_status"] == golden["expected_review_status"]
    assert project_fact["report_status"] == golden["expected_report_status"]
    assert rule_hit["review_status"] == project_fact["review_status"]
