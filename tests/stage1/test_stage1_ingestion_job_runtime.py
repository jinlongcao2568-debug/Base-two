from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage1_orchestration.runtime import build_ingestion_job


def test_stage1_builds_ingestion_job_from_scenario_id() -> None:
    job = build_ingestion_job(
        scenario_id="case_review_ready",
        requested_at="2026-04-05T10:00:00+08:00",
    )

    assert job == {
        "job_type": "ingestion_job",
        "ingestion_job_id": "ingestion-job:case_review_ready",
        "scenario_id": "case_review_ready",
        "requested_at": "2026-04-05T10:00:00+08:00",
        "input_mode": "scenario_id",
        "raw_fixture_path": "tests/fixtures/raw/case_review_ready.raw.json",
    }


def test_stage1_builds_ingestion_job_from_explicit_raw_path() -> None:
    job = build_ingestion_job(
        raw_fixture_path="tests/fixtures/raw/case_open_issued.raw.json",
        requested_at="2026-04-05T10:00:00+08:00",
    )

    assert job["scenario_id"] == "case_open_issued"
    assert job["input_mode"] == "raw_fixture_path"
