from __future__ import annotations

from typing import Any

from src.shared.contracts.minimal_chain_profiles import get_scenario_id, get_scenario_profile


def build_project_base(raw_ingestion_artifact: dict[str, Any]) -> dict[str, Any]:
    raw_payload = raw_ingestion_artifact["raw_payload"]
    scenario_id = get_scenario_id(raw_payload)
    profile = get_scenario_profile(scenario_id)["project_base"]
    return {
        "project_id": raw_payload["project_id"],
        "source_family": raw_payload["source_family"],
        "region_code": raw_payload["region_code"],
        **profile,
    }


def build_structured_profiles(raw_ingestion_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    raw_payload = raw_ingestion_artifact["raw_payload"]
    scenario_id = get_scenario_id(raw_payload)
    profiles = get_scenario_profile(scenario_id)["stage3_profiles"]
    return [profiles[key] for key in sorted(profiles)]
