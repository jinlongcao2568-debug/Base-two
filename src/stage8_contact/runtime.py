from __future__ import annotations

from typing import Any


CONTACT_STRATEGY = {
    "OPEN": "standard_outreach",
    "REVIEW": "analyst_review_required",
    "HOLD": "hold_no_outreach",
    "BLOCK": "block_external_contact",
}


def build_contact_context(project_fact: dict[str, Any]) -> dict[str, Any]:
    project_id = project_fact["project_id"]
    fact_version = project_fact["fact_version"]
    sale_gate_status = project_fact["sale_gate_status"]
    manual_override_status = project_fact["manual_override_status"]
    contact_strategy = CONTACT_STRATEGY[sale_gate_status]
    analyst_follow_up_required = sale_gate_status != "OPEN" or manual_override_status != "NONE"
    return {
        "object_type": "contact_context",
        "context_ref": f"contact_context:{project_id}:{fact_version}",
        "project_id": project_id,
        "fact_version": fact_version,
        "source_project_fact_ref": f"project_fact:{project_id}:{fact_version}",
        "public_chain_status": project_fact["public_chain_status"],
        "sale_gate_status": sale_gate_status,
        "review_status": project_fact["review_status"],
        "manual_override_status": manual_override_status,
        "contact_strategy": contact_strategy,
        "analyst_follow_up_required": analyst_follow_up_required,
        "summary": (
            f"Contact stays {contact_strategy} because sale gate is {sale_gate_status} "
            f"and manual override status is {manual_override_status}."
        ),
    }
