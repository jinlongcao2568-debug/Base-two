from __future__ import annotations

from typing import Any


def build_public_chain_view(project_base: dict[str, Any], project_fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_name": project_base["project_name"],
        "region_code": project_base["region_code"],
        "source_family": project_base["source_family"],
        "public_chain_status": project_fact["public_chain_status"],
        "sale_gate_status": project_fact["sale_gate_status"],
        "real_competitor_count": project_fact["real_competitor_count"],
        "serviceable_competitor_count": project_fact["serviceable_competitor_count"],
        "competitor_quality_grade": project_fact["competitor_quality_grade"],
        "price_cluster_score": project_fact["price_cluster_score"],
        "price_gradient_pattern": project_fact["price_gradient_pattern"],
        "fact_summary": project_fact["fact_summary"],
        "risk_summary": project_fact["risk_summary"],
        "manual_override_status": project_fact["manual_override_status"],
        "report_status": project_fact["report_status"],
        "last_fact_refreshed_at": project_fact["last_fact_refreshed_at"],
    }
