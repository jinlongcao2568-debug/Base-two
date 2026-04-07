from __future__ import annotations

from typing import Any


SALES_READINESS_BUCKET = {
    "OPEN": "ready",
    "REVIEW": "needs_review",
    "HOLD": "hold",
    "BLOCK": "blocked",
}

RECOMMENDED_SALES_ACTION = {
    "OPEN": "prioritize_standard_follow_up",
    "REVIEW": "escalate_manual_review",
    "HOLD": "wait_for_public_chain_completion",
    "BLOCK": "do_not_sell_escalate_risk",
}


def build_sales_context(project_fact: dict[str, Any]) -> dict[str, Any]:
    project_id = project_fact["project_id"]
    fact_version = project_fact["fact_version"]
    sale_gate_status = project_fact["sale_gate_status"]
    return {
        "object_type": "sales_context",
        "context_ref": f"sales_context:{project_id}:{fact_version}",
        "project_id": project_id,
        "fact_version": fact_version,
        "source_project_fact_ref": f"project_fact:{project_id}:{fact_version}",
        "sale_gate_status": sale_gate_status,
        "real_competitor_count": project_fact["real_competitor_count"],
        "serviceable_competitor_count": project_fact["serviceable_competitor_count"],
        "competitor_quality_grade": project_fact["competitor_quality_grade"],
        "price_cluster_score": project_fact["price_cluster_score"],
        "price_gradient_pattern": project_fact["price_gradient_pattern"],
        "coverage_sellable_state": project_fact["coverage_sellable_state"],
        "tender_fairness_risk": project_fact["tender_fairness_risk"],
        "evaluation_integrity_risk": project_fact["evaluation_integrity_risk"],
        "post_award_change_risk": project_fact["post_award_change_risk"],
        "award_suspicion_summary": project_fact["award_suspicion_summary"],
        "sales_readiness_bucket": SALES_READINESS_BUCKET[sale_gate_status],
        "recommended_sales_action": RECOMMENDED_SALES_ACTION[sale_gate_status],
        "summary": (
            f"{sale_gate_status} gate, coverage {project_fact['coverage_sellable_state']}, "
            f"and suspicion summary '{project_fact['award_suspicion_summary']}'."
        ),
    }
