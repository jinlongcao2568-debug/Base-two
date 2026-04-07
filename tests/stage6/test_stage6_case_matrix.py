from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from jsonschema import Draft202012Validator

from src.shared.contracts.minimal_chain_pipeline import run_minimal_runtime_chain
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
    bundle = run_minimal_runtime_chain(scenario_id=case_id, requested_at="2026-04-05T10:00:00+08:00")
    project_base = bundle["stage3"]["project_base"]
    rule_hit = bundle["stage4"]["rule_hits"][0]
    report_record = bundle["stage5"]["report_record"]
    project_fact = bundle["stage6"]["project_fact"]
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
    assert project_fact["coverage_sellable_state"] in {"SELLABLE", "RESTRICTED", "SUSPENDED"}
    assert project_fact["delivery_risk_state"] in {"OPEN", "REVIEW", "HOLD", "BLOCK"}
    assert project_fact["manual_override_status"] in {"NONE", "PENDING", "CONFIRMED", "REJECTED"}
    assert project_fact["award_suspicion_summary"]
