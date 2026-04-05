from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.shared.contracts.runtime_support import load_json, repo_root, to_repo_relative


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def build_ingestion_job(
    *,
    scenario_id: str | None = None,
    raw_fixture_path: str | None = None,
    requested_at: str | None = None,
) -> dict[str, Any]:
    if not scenario_id and not raw_fixture_path:
        raise ValueError("scenario_id or raw_fixture_path is required")
    if raw_fixture_path is None:
        raw_fixture_path = f"tests/fixtures/raw/{scenario_id}.raw.json"
    raw_path = Path(raw_fixture_path)
    raw_payload = load_json(raw_path)
    resolved_scenario_id = scenario_id or raw_payload["scenario_id"]
    return {
        "job_type": "ingestion_job",
        "ingestion_job_id": f"ingestion-job:{resolved_scenario_id}",
        "scenario_id": resolved_scenario_id,
        "requested_at": requested_at or _iso_now(),
        "input_mode": "scenario_id" if scenario_id else "raw_fixture_path",
        "raw_fixture_path": to_repo_relative((repo_root() / raw_path).resolve()),
    }
