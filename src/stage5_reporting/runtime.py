from __future__ import annotations

from typing import Any

from src.shared.contracts.minimal_chain_profiles import get_scenario_profile


def build_report_record(project_base: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    profile = get_scenario_profile(scenario_id)["stage5"]
    return {
        "report_id": profile["report_id"],
        "project_id": project_base["project_id"],
        "brief_path": profile["brief_path"],
        "evidence_pack_path": profile["evidence_pack_path"],
        "objection_draft_path": profile["objection_draft_path"],
        "review_request_list_path": profile["review_request_list_path"],
        "review_task_status": profile["review_task_status"],
        "report_status": profile["report_status"],
        "written_back_at": profile["written_back_at"],
    }
