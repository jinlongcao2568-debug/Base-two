from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jsonschema import Draft202012Validator

from src.shared.contracts.minimal_chain_pipeline import run_minimal_runtime_chain


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, payload: dict) -> None:
    schema = load_json(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]


def test_stage3_stage4_stage6_minimal_flow_is_real_consumption() -> None:
    bundle = run_minimal_runtime_chain(
        raw_fixture_path="tests/fixtures/raw/case_review_ready.raw.json",
        requested_at="2026-04-05T10:00:00+08:00",
    )
    project_base = bundle["stage3"]["project_base"]
    rule_hit = bundle["stage4"]["rule_hits"][0]
    project_fact = bundle["stage6"]["project_fact"]
    golden = load_json(ROOT / "tests/fixtures/golden/case_review_ready.stage_chain.json")

    validate(ROOT / "docs/contracts/schemas/stage3_project_base.schema.json", project_base)
    validate(ROOT / "docs/contracts/schemas/stage4_rule_hit.schema.json", rule_hit)
    validate(ROOT / "docs/contracts/schemas/stage6_project_fact.schema.json", project_fact)

    assert project_base["project_id"] == rule_hit["project_id"] == project_fact["project_id"]
    assert project_fact["project_base_ref"] == golden["expected_project_base_ref"]
    assert project_fact["rule_hit_refs"] == [golden["expected_rule_hit_ref"]]
    assert project_fact["report_record_ref"] == golden["expected_report_record_ref"]
    assert project_fact["public_chain_status"] == golden["expected_public_chain_status"]
    assert project_fact["sale_gate_status"] == golden["expected_sale_gate_status"]
    assert project_fact["review_status"] == golden["expected_review_status"]
    assert project_fact["report_status"] == golden["expected_report_status"]
    assert rule_hit["review_status"] == project_fact["review_status"]
