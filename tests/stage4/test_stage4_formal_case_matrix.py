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
def test_stage4_case_matrix_contracts_and_lineage(case_id: str) -> None:
    bundle = run_minimal_runtime_chain(scenario_id=case_id, requested_at="2026-04-05T10:00:00+08:00")
    project_base = bundle["stage3"]["project_base"]
    structured_profiles = bundle["stage3"]["structured_profiles"]
    rule_hit = bundle["stage4"]["rule_hits"][0]
    evidence = bundle["stage4"]["evidences"][0]
    review_request = bundle["stage4"]["review_requests"][0]
    golden = load_json(ROOT / f"tests/fixtures/golden/{case_id}.stage_chain.json")

    validate("stage4_rule_hit.schema.json", rule_hit)
    validate("stage4_evidence.schema.json", evidence)
    validate("stage4_review_request.schema.json", review_request)

    assert project_base["project_id"] == rule_hit["project_id"] == evidence["project_id"] == review_request["project_id"]
    assert rule_hit["evidence_refs"] == [f"evidence:{evidence['evidence_id']}"]
    assert rule_hit["rule_code"] in evidence["consumed_by_rule_codes"]
    assert rule_hit["rule_code"] in review_request["source_rule_codes"]
    assert evidence["evidence_grade"] == golden["expected_evidence_grade"]
    assert rule_hit["profile_refs"]
    assert review_request["profile_refs"]
    available_profile_refs = {f"{item['object_type']}:{item['profile_id']}" for item in structured_profiles}
    assert set(rule_hit["profile_refs"]).issubset(available_profile_refs)
    assert set(review_request["profile_refs"]).issubset(available_profile_refs)
    assert rule_hit["writeback_fields"]
    assert review_request["request_topic"]
    assert review_request["resolution_path"]
    assert review_request["blocking_scope"]
