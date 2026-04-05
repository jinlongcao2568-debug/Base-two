from __future__ import annotations

from typing import Any

from src.shared.contracts.runtime_support import load_json, resolve_repo_path, to_repo_relative


def build_raw_ingestion_artifact(ingestion_job: dict[str, Any]) -> dict[str, Any]:
    raw_path = resolve_repo_path(ingestion_job["raw_fixture_path"])
    raw_payload = load_json(raw_path)
    return {
        "artifact_type": "raw_ingestion_artifact",
        "artifact_id": f"raw-ingestion:{raw_payload['project_id']}",
        "ingestion_job_id": ingestion_job["ingestion_job_id"],
        "scenario_id": raw_payload["scenario_id"],
        "project_id": raw_payload["project_id"],
        "source_family": raw_payload["source_family"],
        "source_type": raw_payload["source_type"],
        "captured_at": ingestion_job["requested_at"],
        "raw_fixture_path": to_repo_relative(raw_path),
        "raw_payload": raw_payload,
    }
