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


@pytest.mark.parametrize("case_id", CASES)
def test_stage5_runtime_matches_report_record_fixture(case_id: str) -> None:
    bundle = run_minimal_runtime_chain(scenario_id=case_id, requested_at="2026-04-05T10:00:00+08:00")
    report_record = bundle["stage5"]["report_record"]
    schema = load_json(ROOT / "docs/contracts/schemas/stage5_report_record.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(report_record), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]
    expected = load_json(ROOT / f"tests/fixtures/reports/{case_id}.report_record.json")
    assert report_record == expected
