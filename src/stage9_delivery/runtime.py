from __future__ import annotations

from typing import Any


def _delivery_readiness(project_fact: dict[str, Any]) -> str:
    coverage_sellable_state = project_fact["coverage_sellable_state"]
    delivery_risk_state = project_fact["delivery_risk_state"]
    sale_gate_status = project_fact["sale_gate_status"]
    report_status = project_fact["report_status"]
    if coverage_sellable_state != "SELLABLE" or delivery_risk_state == "BLOCK":
        return "blocked"
    if delivery_risk_state == "HOLD" or sale_gate_status == "HOLD":
        return "on_hold"
    if delivery_risk_state == "REVIEW" or sale_gate_status == "REVIEW":
        return "review_pending"
    if sale_gate_status == "OPEN" and report_status in {"READY", "ISSUED"}:
        return "ready"
    return "blocked"


def build_delivery_payload(
    project_fact: dict[str, Any],
    sales_context: dict[str, Any],
    contact_context: dict[str, Any],
) -> dict[str, Any]:
    project_id = project_fact["project_id"]
    fact_version = project_fact["fact_version"]
    delivery_readiness = _delivery_readiness(project_fact)
    return {
        "object_type": "delivery_payload",
        "payload_ref": f"delivery_payload:{project_id}:{fact_version}",
        "project_id": project_id,
        "fact_version": fact_version,
        "source_project_fact_ref": f"project_fact:{project_id}:{fact_version}",
        "sales_context_ref": sales_context["context_ref"],
        "contact_context_ref": contact_context["context_ref"],
        "report_record_ref": project_fact["report_record_ref"],
        "sale_gate_status": project_fact["sale_gate_status"],
        "coverage_sellable_state": project_fact["coverage_sellable_state"],
        "delivery_risk_state": project_fact["delivery_risk_state"],
        "review_status": project_fact["review_status"],
        "report_status": project_fact["report_status"],
        "delivery_readiness": delivery_readiness,
        "fact_summary": project_fact["fact_summary"],
        "risk_summary": project_fact["risk_summary"],
        "payload_summary": (
            f"Delivery payload is {delivery_readiness} based on coverage {project_fact['coverage_sellable_state']}, "
            f"delivery risk {project_fact['delivery_risk_state']}, sale gate {project_fact['sale_gate_status']}, "
            f"and report status {project_fact['report_status']}."
        ),
    }
