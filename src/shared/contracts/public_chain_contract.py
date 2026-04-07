from __future__ import annotations

from typing import Any


PUBLIC_CHAIN_VIEW_FIELDS = (
    "project_name",
    "region_code",
    "source_family",
    "public_chain_status",
    "sale_gate_status",
    "coverage_sellable_state",
    "delivery_risk_state",
    "real_competitor_count",
    "serviceable_competitor_count",
    "competitor_quality_grade",
    "price_cluster_score",
    "price_gradient_pattern",
    "fact_summary",
    "risk_summary",
    "tender_fairness_risk",
    "evaluation_integrity_risk",
    "post_award_change_risk",
    "award_suspicion_summary",
    "manual_override_status",
    "report_status",
    "last_fact_refreshed_at",
)


def validate_public_chain_view(payload: dict[str, Any]) -> list[str]:
    expected = set(PUBLIC_CHAIN_VIEW_FIELDS)
    actual = set(payload)
    errors: list[str] = []
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"unexpected fields: {', '.join(extra)}")
    for name in PUBLIC_CHAIN_VIEW_FIELDS:
        if name not in payload:
            continue
        if payload[name] in (None, ""):
            errors.append(f"{name} must be non-empty")
    return errors
