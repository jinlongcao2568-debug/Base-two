from __future__ import annotations

from typing import Any

from src.shared.contracts.minimal_chain_profiles import get_scenario_profile


def build_project_fact(
    project_base: dict[str, Any],
    rule_hits: list[dict[str, Any]],
    report_record: dict[str, Any],
    scenario_id: str,
) -> dict[str, Any]:
    profile = get_scenario_profile(scenario_id)["stage6"]
    primary_rule_hit = rule_hits[0]
    return {
        "object_type": "project_fact",
        "project_id": project_base["project_id"],
        "fact_version": profile["fact_version"],
        "fact_refresh_trigger": profile["fact_refresh_trigger"],
        "fact_source_summary": profile["fact_source_summary"],
        "project_base_ref": f"project_base:{project_base['project_id']}",
        "rule_hit_refs": [f"rule_hit:{primary_rule_hit['rule_hit_id']}"],
        "report_record_ref": f"report_record:{report_record['report_id']}",
        "public_chain_status": project_base["public_chain_status"],
        "rule_hit_summary": profile["rule_hit_summary"],
        "clue_summary": profile["clue_summary"],
        "sale_gate_status": profile["sale_gate_status"],
        "real_competitor_count": profile["real_competitor_count"],
        "serviceable_competitor_count": profile["serviceable_competitor_count"],
        "competitor_quality_grade": profile["competitor_quality_grade"],
        "price_cluster_score": profile["price_cluster_score"],
        "price_gradient_pattern": profile["price_gradient_pattern"],
        "fact_summary": profile["fact_summary"],
        "risk_summary": profile["risk_summary"],
        "review_status": primary_rule_hit["review_status"],
        "manual_override_status": profile["manual_override_status"],
        "report_status": report_record["report_status"],
        "last_fact_refreshed_at": profile["last_fact_refreshed_at"],
    }
