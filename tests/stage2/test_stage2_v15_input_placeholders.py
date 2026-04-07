from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage1_orchestration.runtime import build_ingestion_job
from src.stage2_ingestion.runtime import build_raw_ingestion_artifact


def test_stage2_exposes_v15_placeholder_inputs() -> None:
    job = build_ingestion_job(scenario_id="case_review_ready", requested_at="2026-04-05T10:00:00+08:00")
    artifact = build_raw_ingestion_artifact(job)
    assert artifact["qualification_inputs"]
    assert artifact["parameter_requirement_inputs"]
    assert artifact["scoring_disclosure_inputs"]
    assert artifact["tender_agent_inputs"]
    assert artifact["split_procurement_inputs"] is not None
    assert artifact["post_award_inputs"] is not None
