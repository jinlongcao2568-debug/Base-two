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
def test_stage3_project_base_runtime_matches_case_fixture(case_id: str) -> None:
    project_base = run_minimal_runtime_chain(
        scenario_id=case_id,
        requested_at="2026-04-05T10:00:00+08:00",
    )["stage3"]["project_base"]
    raw_notice = load_json(ROOT / f"tests/fixtures/raw/{case_id}.raw.json")
    expected = load_json(ROOT / f"tests/fixtures/normalized/{case_id}.project_base.json")
    schema = load_json(ROOT / "docs/contracts/schemas/stage3_project_base.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(project_base), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]
    assert project_base["project_id"] == raw_notice["project_id"]
    assert project_base["source_family"] == raw_notice["source_family"]
    assert project_base["region_code"] == raw_notice["region_code"]
    assert project_base == expected
