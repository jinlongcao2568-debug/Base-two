from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.shared.contracts.minimal_chain_pipeline import run_minimal_runtime_chain
from src.shared.contracts.runtime_support import validate_schema


def test_stage3_outputs_all_v15_structured_profiles() -> None:
    profiles = run_minimal_runtime_chain(scenario_id="case_review_ready", requested_at="2026-04-05T10:00:00+08:00")["stage3"]["structured_profiles"]
    assert len(profiles) == 7
    for payload in profiles:
        assert payload["profile_id"]
        schema_path = f"docs/contracts/schemas/stage3_{payload['object_type']}.schema.json"
        assert validate_schema(schema_path, payload) == []
