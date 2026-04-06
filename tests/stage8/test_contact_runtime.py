from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage8_contact.runtime import build_contact_context
from src.shared.contracts.runtime_support import validate_schema


CASES = (
    "case_review_ready",
    "case_open_issued",
    "case_hold_incomplete_chain",
    "case_block_high_risk",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_id", CASES)
def test_build_contact_context_matches_fixture(case_id: str) -> None:
    project_fact = load_json(ROOT / f"tests/fixtures/facts/{case_id}.project_fact.json")
    expected = load_json(ROOT / f"tests/fixtures/downstream/{case_id}.contact_context.json")
    payload = build_contact_context(project_fact)

    assert payload == expected
    assert validate_schema("docs/contracts/schemas/stage8_contact_context.schema.json", payload) == []
