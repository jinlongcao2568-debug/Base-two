from __future__ import annotations

from typing import Any

from src.shared.contracts.minimal_chain_profiles import get_scenario_profile
from src.shared.contracts.runtime_support import load_json, resolve_repo_path, to_repo_relative


def build_raw_ingestion_artifact(ingestion_job: dict[str, Any]) -> dict[str, Any]:
    raw_path = resolve_repo_path(ingestion_job["raw_fixture_path"])
    raw_payload = load_json(raw_path)
    stage2_inputs = get_scenario_profile(raw_payload["scenario_id"])["stage2_inputs"]
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
        "qualification_inputs": stage2_inputs["qualification_inputs"],
        "parameter_requirement_inputs": stage2_inputs["parameter_requirement_inputs"],
        "scoring_disclosure_inputs": stage2_inputs["scoring_disclosure_inputs"],
        "tender_agent_inputs": stage2_inputs["tender_agent_inputs"],
        "split_procurement_inputs": stage2_inputs["split_procurement_inputs"],
        "post_award_inputs": stage2_inputs["post_award_inputs"],
        "raw_payload": raw_payload,
    }
