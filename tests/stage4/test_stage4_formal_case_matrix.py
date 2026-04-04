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
def test_stage4_case_matrix_contracts_and_lineage(case_id: str) -> None:
    project_base = load_json(ROOT / f"tests/fixtures/normalized/{case_id}.project_base.json")
    rule_hit = load_json(ROOT / f"tests/fixtures/rules/{case_id}.rule_hit.json")
    evidence = load_json(ROOT / f"tests/fixtures/rules/{case_id}.evidence.json")
    review_request = load_json(ROOT / f"tests/fixtures/rules/{case_id}.review_request.json")
    golden = load_json(ROOT / f"tests/fixtures/golden/{case_id}.stage_chain.json")

    validate("stage4_rule_hit.schema.json", rule_hit)
    validate("stage4_evidence.schema.json", evidence)
    validate("stage4_review_request.schema.json", review_request)

    assert project_base["project_id"] == rule_hit["project_id"] == evidence["project_id"] == review_request["project_id"]
    assert rule_hit["evidence_refs"] == [f"evidence:{evidence['evidence_id']}"]
    assert rule_hit["rule_code"] in evidence["consumed_by_rule_codes"]
    assert rule_hit["rule_code"] in review_request["source_rule_codes"]
    assert evidence["evidence_grade"] == golden["expected_evidence_grade"]
