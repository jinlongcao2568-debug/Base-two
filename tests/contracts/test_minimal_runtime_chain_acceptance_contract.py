from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    "case_review_ready",
    "case_open_issued",
    "case_hold_incomplete_chain",
    "case_block_high_risk",
)


def test_acceptance_contract_references_downstream_outputs() -> None:
    payload = yaml.safe_load((ROOT / "docs/contracts/minimal_runtime_chain_acceptance.yaml").read_text(encoding="utf-8"))
    acceptance = payload["acceptance"]
    for artifact_key in ("stage7.sales_context", "stage8.contact_context", "stage9.delivery_payload"):
        assert artifact_key in acceptance["artifacts"]
        assert artifact_key in acceptance["schema_checks"]
        assert artifact_key in acceptance["fixture_checks"]
    for case_id in CASES:
        for artifact_key in ("stage7.sales_context", "stage8.contact_context", "stage9.delivery_payload"):
            fixture_path = ROOT / acceptance["fixture_checks"][artifact_key].format(scenario_id=case_id)
            assert fixture_path.exists(), fixture_path
