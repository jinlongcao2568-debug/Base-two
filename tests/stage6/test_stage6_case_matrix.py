from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    "case_review_ready",
    "case_open_issued",
    "case_hold_incomplete_chain",
    "case_block_high_risk",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, payload: dict) -> None:
    schema = load_json(ROOT / f"docs/contracts/schemas/{schema_name}")
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


@pytest.mark.parametrize("case_id", CASES)
def test_stage6_case_matrix_matches_refs_and_status(case_id: str) -> None:
    project_base = load_json(ROOT / f"tests/fixtures/normalized/{case_id}.project_base.json")
    rule_hit = load_json(ROOT / f"tests/fixtures/rules/{case_id}.rule_hit.json")
    report_record = load_json(ROOT / f"tests/fixtures/reports/{case_id}.report_record.json")
    project_fact = load_json(ROOT / f"tests/fixtures/facts/{case_id}.project_fact.json")
    golden = load_json(ROOT / f"tests/fixtures/golden/{case_id}.stage_chain.json")

    validate("stage5_report_record.schema.json", report_record)
    validate("stage6_project_fact.schema.json", project_fact)

    assert project_fact["project_base_ref"] == golden["expected_project_base_ref"]
    assert project_fact["rule_hit_refs"] == [golden["expected_rule_hit_ref"]]
    assert project_fact["report_record_ref"] == golden["expected_report_record_ref"]
    assert project_fact["public_chain_status"] == golden["expected_public_chain_status"]
    assert project_fact["sale_gate_status"] == golden["expected_sale_gate_status"]
    assert project_fact["review_status"] == golden["expected_review_status"]
    assert project_fact["report_status"] == golden["expected_report_status"]
    assert project_base["project_id"] == rule_hit["project_id"] == report_record["project_id"] == project_fact["project_id"]
