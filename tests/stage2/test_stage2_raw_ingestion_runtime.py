from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage1_orchestration.runtime import build_ingestion_job
from src.stage2_ingestion.runtime import build_raw_ingestion_artifact


def test_stage2_builds_raw_ingestion_artifact_from_job() -> None:
    job = build_ingestion_job(
        scenario_id="case_hold_incomplete_chain",
        requested_at="2026-04-05T10:00:00+08:00",
    )

    artifact = build_raw_ingestion_artifact(job)

    assert artifact["artifact_type"] == "raw_ingestion_artifact"
    assert artifact["scenario_id"] == "case_hold_incomplete_chain"
    assert artifact["project_id"] == "project-cn-hold-001"
    assert artifact["captured_at"] == "2026-04-05T10:00:00+08:00"
    assert artifact["raw_payload"]["notice_state"] == "hold_incomplete_chain"
