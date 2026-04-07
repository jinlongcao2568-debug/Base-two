from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.shared.contracts.minimal_chain_pipeline import run_minimal_runtime_chain


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_stage6_project_fact_runtime_matches_schema_and_lineage() -> None:
    bundle = run_minimal_runtime_chain(scenario_id="case_review_ready", requested_at="2026-04-05T10:00:00+08:00")
    project_base = bundle["stage3"]["project_base"]
    rule_hit = bundle["stage4"]["rule_hits"][0]
    project_fact = bundle["stage6"]["project_fact"]
    schema = load_json(ROOT / "docs/contracts/schemas/stage6_project_fact.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(project_fact), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]
    assert project_fact["project_base_ref"] == f"project_base:{project_base['project_id']}"
    assert project_fact["rule_hit_refs"] == [f"rule_hit:{rule_hit['rule_hit_id']}"]
    assert project_fact["coverage_sellable_state"] == "SELLABLE"
    assert project_fact["delivery_risk_state"] == "REVIEW"
    assert project_fact["sale_gate_status"] == "REVIEW"
