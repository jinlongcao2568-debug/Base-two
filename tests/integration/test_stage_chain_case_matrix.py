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
def test_stage_chain_case_matrix_consumes_multi_sample_flow(case_id: str) -> None:
    bundle = run_minimal_runtime_chain(scenario_id=case_id, requested_at="2026-04-05T10:00:00+08:00")
    raw_payload = bundle["stage2"]["raw_ingestion_artifact"]["raw_payload"]
    project_base = bundle["stage3"]["project_base"]
    rule_hit = bundle["stage4"]["rule_hits"][0]
    evidence = bundle["stage4"]["evidences"][0]
    review_request = bundle["stage4"]["review_requests"][0]
    report_record = bundle["stage5"]["report_record"]
    project_fact = bundle["stage6"]["project_fact"]
    public_chain_view = bundle["consumers"]["public_chain_view"]
    golden = load_json(ROOT / f"tests/fixtures/golden/{case_id}.stage_chain.json")

    validate("stage3_project_base.schema.json", project_base)
    validate("stage4_rule_hit.schema.json", rule_hit)
    validate("stage4_evidence.schema.json", evidence)
    validate("stage4_review_request.schema.json", review_request)
    validate("stage5_report_record.schema.json", report_record)
    validate("stage6_project_fact.schema.json", project_fact)

    assert raw_payload["project_id"] == project_base["project_id"] == rule_hit["project_id"]
    assert project_base["project_id"] == evidence["project_id"] == review_request["project_id"] == report_record["project_id"] == project_fact["project_id"]
    assert project_fact["project_base_ref"] == golden["expected_project_base_ref"]
    assert project_fact["rule_hit_refs"] == [golden["expected_rule_hit_ref"]]
    assert project_fact["report_record_ref"] == golden["expected_report_record_ref"]
    assert project_fact["public_chain_status"] == golden["expected_public_chain_status"]
    assert project_fact["sale_gate_status"] == golden["expected_sale_gate_status"]
    assert project_fact["review_status"] == golden["expected_review_status"]
    assert project_fact["report_status"] == golden["expected_report_status"]
    assert rule_hit["evidence_refs"] == [f"evidence:{evidence['evidence_id']}"]
    assert review_request["source_rule_codes"] == [rule_hit["rule_code"]]
    assert evidence["evidence_grade"] == golden["expected_evidence_grade"]
    assert public_chain_view["project_name"] == project_base["project_name"]
    assert public_chain_view["public_chain_status"] == project_fact["public_chain_status"]
    assert public_chain_view["sale_gate_status"] == project_fact["sale_gate_status"]
