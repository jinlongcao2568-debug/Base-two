from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage8_contact.runtime import build_contact_context
from src.shared.contracts.minimal_chain_pipeline import run_minimal_runtime_chain
from src.shared.contracts.runtime_support import validate_schema


CASES = (
    "case_review_ready",
    "case_open_issued",
    "case_hold_incomplete_chain",
    "case_block_high_risk",
)


@pytest.mark.parametrize("case_id", CASES)
def test_build_contact_context_matches_fixture(case_id: str) -> None:
    project_fact = run_minimal_runtime_chain(scenario_id=case_id, requested_at="2026-04-05T10:00:00+08:00")["stage6"]["project_fact"]
    payload = build_contact_context(project_fact)
    assert validate_schema("docs/contracts/schemas/stage8_contact_context.schema.json", payload) == []
    assert payload["delivery_risk_state"] == project_fact["delivery_risk_state"]
    assert payload["manual_override_status"] == project_fact["manual_override_status"]
