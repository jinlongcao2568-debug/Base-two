from __future__ import annotations

from typing import Any

from src.shared.contracts.minimal_chain_profiles import get_scenario_id, get_scenario_profile


def _build_evidence(profile: dict[str, Any], raw_payload: dict[str, Any], project_id: str) -> dict[str, Any]:
    return {
        "evidence_id": profile["evidence_id"],
        "project_id": project_id,
        "source_url": profile["source_url"],
        "source_type": raw_payload["source_type"],
        "capture_type": profile["capture_type"],
        "capture_time": profile["capture_time"],
        "page_title": profile["page_title"],
        "snippet": profile["snippet"],
        "evidence_artifact_refs": profile["evidence_artifact_refs"],
        "structured_field_refs": profile["structured_field_refs"],
        "consumed_by_rule_codes": [profile["rule_code"]],
        "evidence_grade": profile["evidence_grade"],
        "evidence_hash": f"sha256:{profile['evidence_id']}",
    }


def _build_rule_hit(profile: dict[str, Any], project_id: str, evidence_id: str) -> dict[str, Any]:
    return {
        "rule_hit_id": profile["rule_hit_id"],
        "project_id": project_id,
        "rule_code": profile["rule_code"],
        "severity": profile["severity"],
        "confidence": profile["confidence"],
        "result_type": profile["result_type"],
        "why_hit": profile["why_hit"],
        "boundary_note": profile["boundary_note"],
        "evidence_refs": [f"evidence:{evidence_id}"],
        "profile_refs": profile["profile_refs"],
        "writeback_fields": profile["writeback_fields"],
        "target_entity_type": profile["target_entity_type"],
        "target_entity_id": profile["target_entity_id"],
        "review_status": profile["review_status"],
    }


def _build_review_request(profile: dict[str, Any], project_id: str) -> dict[str, Any]:
    return {
        "request_id": profile["request_id"],
        "project_id": project_id,
        "request_type": profile["request_type"],
        "request_topic": profile["request_topic"],
        "resolution_path": profile["resolution_path"],
        "blocking_scope": profile["blocking_scope"],
        "reason": profile["reason"],
        "public_basis": profile["public_basis"],
        "requested_materials": profile["requested_materials"],
        "priority": profile["priority"],
        "source_rule_codes": [profile["rule_code"]],
        "profile_refs": profile["profile_refs"],
    }


def evaluate_formal_objects(
    raw_ingestion_artifact: dict[str, Any],
    project_base: dict[str, Any],
    structured_profiles: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    raw_payload = raw_ingestion_artifact["raw_payload"]
    scenario_id = get_scenario_id(raw_payload)
    profile = get_scenario_profile(scenario_id)["stage4"]
    key_map = get_scenario_profile(scenario_id)["stage3_profiles"]
    object_types = {key_map[key]["object_type"] for key in profile["profile_keys"]}
    profile = {
        **profile,
        "profile_refs": [
            f"{item['object_type']}:{item['profile_id']}"
            for item in structured_profiles
            if item["object_type"] in object_types
        ],
    }
    evidence = _build_evidence(profile, raw_payload, project_base["project_id"])
    rule_hit = _build_rule_hit(profile, project_base["project_id"], evidence["evidence_id"])
    review_request = _build_review_request(profile, project_base["project_id"])
    return {
        "rule_hits": [rule_hit],
        "evidences": [evidence],
        "review_requests": [review_request],
    }
