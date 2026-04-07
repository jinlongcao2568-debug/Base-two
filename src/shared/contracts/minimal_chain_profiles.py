from __future__ import annotations

from typing import Any


def _profile(object_type: str, profile_id: str, project_id: str, signal_summary: str, risk_flags: list[str], confidence: float) -> dict[str, Any]:
    return {
        "object_type": object_type,
        "profile_id": profile_id,
        "project_id": project_id,
        "source_refs": [f"raw_ingestion:{project_id}"],
        "signal_summary": signal_summary,
        "risk_flags": risk_flags,
        "confidence": confidence,
    }


def _stage2_inputs(**overrides: list[str]) -> dict[str, list[str]]:
    inputs = {
        "qualification_inputs": ["standard qualification terms"],
        "parameter_requirement_inputs": ["standard parameter terms"],
        "scoring_disclosure_inputs": ["score disclosure present"],
        "tender_agent_inputs": ["standard agent data"],
        "split_procurement_inputs": ["single package"],
        "post_award_inputs": ["no abnormal post-award change"],
    }
    inputs.update(overrides)
    return inputs


def _base_profiles(project_id: str, overrides: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    defaults = {
        "qualification_clause_profile": ("Qualification clauses are standard and non-discriminatory.", [], 0.6),
        "parameter_requirement_profile": ("Parameter requirements are standard and non-directional.", [], 0.6),
        "vendor_fit_profile": ("Vendor fit pattern is broad and non-restrictive.", [], 0.7),
        "scoring_anomaly_profile": ("Scoring disclosure is complete without visible anomaly.", [], 0.7),
        "tender_agent_profile": ("Tender agent behavior is unremarkable.", [], 0.55),
        "split_procurement_profile": ("No split procurement signal is visible.", [], 0.58),
        "post_award_change_profile": ("No abnormal post-award change signal is visible.", [], 0.57),
    }
    profiles: dict[str, dict[str, Any]] = {}
    for name, (summary, flags, confidence) in defaults.items():
        override = overrides.get(name, {})
        profiles[name] = _profile(
            name,
            override.get("profile_id", f"{name.replace('_', '-')}-{project_id}"),
            project_id,
            override.get("signal_summary", summary),
            override.get("risk_flags", flags),
            override.get("confidence", confidence),
        )
    return profiles


SCENARIO_PROFILES: dict[str, dict[str, Any]] = {
    "case_review_ready": {
        "project_base": {
            "project_name": "Review Ready Project",
            "project_type_raw": "building",
            "engineering_domain": "building_construction",
            "bid_control_price": 18000000,
            "bid_eval_method": "comprehensive",
            "public_chain_status": "COMPLETE",
            "opening_record_count": 1,
            "invalid_bid_count": 0,
        },
        "stage2_inputs": _stage2_inputs(
            qualification_inputs=["regional qualification wording", "non-essential hard gate"],
            parameter_requirement_inputs=["tailored parameter cluster", "single vendor fit signature"],
            scoring_disclosure_inputs=["expert scoring disclosure present", "score spread anomaly"],
            tender_agent_inputs=["repeat agent cluster"],
        ),
        "stage3_profiles": _base_profiles(
            "project-cn-review-001",
            {
                "qualification_clause_profile": {"signal_summary": "Qualification clauses include region-specific and non-essential gate wording.", "risk_flags": ["regional_restriction", "non_essential_hard_gate"], "confidence": 0.81},
                "parameter_requirement_profile": {"signal_summary": "Parameter requirements contain a tailored exclusion pattern.", "risk_flags": ["tailored_parameter", "combined_parameter_exclusion"], "confidence": 0.8},
                "vendor_fit_profile": {"signal_summary": "Vendor fit pattern suggests one likely vendor cluster.", "risk_flags": ["single_vendor_fit_pattern"], "confidence": 0.76},
                "scoring_anomaly_profile": {"signal_summary": "Expert non-price scoring shows a visible anomaly spread.", "risk_flags": ["expert_score_anomaly", "abnormal_non_price_score"], "confidence": 0.88},
                "tender_agent_profile": {"signal_summary": "Tender agent concentration is elevated but not yet blocking.", "risk_flags": ["agent_repeat_pattern"], "confidence": 0.63},
            },
        ),
        "stage4": {
            "evidence_id": "evidence-review-001", "source_url": "https://ggzy.example.cn/review/scoring", "capture_type": "html_snapshot", "capture_time": "2026-04-04T17:20:00+08:00", "page_title": "Review ready scoring disclosure", "snippet": "Public scoring disclosure shows a non-price anomaly that still needs analyst review.", "evidence_artifact_refs": ["artifact://review/scoring-disclosure.html"], "structured_field_refs": ["field://project-cn-review-001/scoring_anomaly_profile/signal_summary"], "evidence_grade": "B", "rule_hit_id": "rule-hit-review-001", "rule_code": "EXPERT_SCORE_ANOMALY_CLUE", "severity": "MEDIUM", "confidence": 0.88, "result_type": "CLUE", "why_hit": "Public scoring disclosure indicates a scoring anomaly that still needs analyst confirmation.", "boundary_note": "The signal is public and traceable but remains a clue until review closes.", "target_entity_type": "project", "target_entity_id": "project-cn-review-001", "review_status": "PENDING", "profile_keys": ["scoring_anomaly_profile", "qualification_clause_profile"], "writeback_fields": ["evaluation_integrity_risk", "award_suspicion_summary", "clue_summary"], "request_id": "review-request-review-001", "request_type": "ANALYST_SCORING_REVIEW", "request_topic": "evaluation_integrity_risk", "resolution_path": "analyst_review", "blocking_scope": "commercial_followup", "reason": "The scoring anomaly clue must be reviewed before the project can move out of REVIEW.", "public_basis": "Public scoring disclosure and qualification wording are traceable and indicate a likely evaluation integrity issue.", "requested_materials": ["scoring disclosure page", "qualification clause excerpt"], "priority": "MEDIUM",
        },
        "stage5": {
            "report_id": "report-review-001", "brief_path": "reports/review-ready/brief.md", "evidence_pack_path": "reports/review-ready/evidence-pack.zip", "objection_draft_path": "reports/review-ready/objection-draft.md", "review_request_list_path": "reports/review-ready/review-requests.json", "review_task_status": "PENDING_REVIEW", "report_status": "READY", "written_back_at": "2026-04-04T18:10:00+08:00",
        },
        "stage6": {
            "fact_version": 1, "fact_refresh_trigger": "RULE_PIPELINE_REFRESH", "fact_source_summary": "Derived from review-ready project_base, structured profiles, rule_hit, and report_record.", "rule_hit_summary": "A scoring anomaly clue remains open.", "clue_summary": "The evaluation integrity signal is pending analyst confirmation.", "sale_gate_status": "REVIEW", "real_competitor_count": 3, "serviceable_competitor_count": 2, "competitor_quality_grade": "B", "price_cluster_score": 68, "price_gradient_pattern": "NARROW_BAND", "fact_summary": "Project remains in review while the scoring anomaly clue is unresolved.", "risk_summary": "Evaluation integrity risk remains under analyst review.", "manual_override_status": "PENDING", "delivery_risk_state": "REVIEW", "tender_fairness_risk": "MEDIUM", "evaluation_integrity_risk": "HIGH", "post_award_change_risk": "LOW", "award_suspicion_summary": "Scoring anomaly clue remains under analyst review.", "last_fact_refreshed_at": "2026-04-04T18:00:00+08:00",
        },
    },
    "case_open_issued": {
        "project_base": {
            "project_name": "Open Issued Project", "project_type_raw": "municipal", "engineering_domain": "municipal_engineering", "bid_control_price": 26000000, "bid_eval_method": "lowest_price", "public_chain_status": "COMPLETE", "opening_record_count": 1, "invalid_bid_count": 0,
        },
        "stage2_inputs": _stage2_inputs(),
        "stage3_profiles": _base_profiles("project-cn-open-001", {}),
        "stage4": {
            "evidence_id": "evidence-open-001", "source_url": "https://ggzy.example.cn/open/result", "capture_type": "html_snapshot", "capture_time": "2026-04-04T17:30:00+08:00", "page_title": "Open issued notice", "snippet": "Public result notice confirms a clean, fully traceable public chain and serviceable competition.", "evidence_artifact_refs": ["artifact://open/result-notice.html"], "structured_field_refs": ["field://project-cn-open-001/vendor_fit_profile/signal_summary"], "evidence_grade": "A", "rule_hit_id": "rule-hit-open-001", "rule_code": "SERVICEABLE_COMPETITOR_IDENTIFIED", "severity": "LOW", "confidence": 0.96, "result_type": "AUTO_HIT", "why_hit": "Public chain and competition evidence confirm a serviceable competitor baseline.", "boundary_note": "The result is fully supported by public evidence and does not require additional review.", "target_entity_type": "project", "target_entity_id": "project-cn-open-001", "review_status": "CONFIRMED", "profile_keys": ["vendor_fit_profile"], "writeback_fields": ["sale_gate_status", "competitor_quality_grade"], "request_id": "review-request-open-001", "request_type": "CLOSEOUT_CONFIRMATION", "request_topic": "delivery_release", "resolution_path": "closeout_record", "blocking_scope": "none", "reason": "Final closeout confirmation is retained even though no blocking clue remains.", "public_basis": "Public result notice and report evidence are already confirmed.", "requested_materials": ["final report brief"], "priority": "LOW",
        },
        "stage5": {
            "report_id": "report-open-001", "brief_path": "reports/open-issued/brief.md", "evidence_pack_path": "reports/open-issued/evidence-pack.zip", "objection_draft_path": "reports/open-issued/objection-draft.md", "review_request_list_path": "reports/open-issued/review-requests.json", "review_task_status": "COMPLETED", "report_status": "ISSUED", "written_back_at": "2026-04-04T18:20:00+08:00",
        },
        "stage6": {
            "fact_version": 2, "fact_refresh_trigger": "REPORT_WRITEBACK", "fact_source_summary": "Derived from open-issued project_base, structured profiles, rule_hit, and issued report_record.", "rule_hit_summary": "Serviceable competition has been formally confirmed.", "clue_summary": "No unresolved clue remains.", "sale_gate_status": "OPEN", "real_competitor_count": 2, "serviceable_competitor_count": 2, "competitor_quality_grade": "A", "price_cluster_score": 82, "price_gradient_pattern": "STABLE_SPREAD", "fact_summary": "Project is open for standard downstream sales and delivery consumption.", "risk_summary": "No blocking or hold condition remains after confirmation.", "manual_override_status": "NONE", "delivery_risk_state": "OPEN", "tender_fairness_risk": "LOW", "evaluation_integrity_risk": "LOW", "post_award_change_risk": "LOW", "award_suspicion_summary": "No suspicious aggregation remains.", "last_fact_refreshed_at": "2026-04-04T18:20:00+08:00",
        },
    },
    "case_hold_incomplete_chain": {
        "project_base": {
            "project_name": "Hold Incomplete Chain Project", "project_type_raw": "highway", "engineering_domain": "transportation", "bid_control_price": 32000000, "bid_eval_method": "comprehensive", "public_chain_status": "INCOMPLETE", "opening_record_count": 0, "invalid_bid_count": 0,
        },
        "stage2_inputs": _stage2_inputs(scoring_disclosure_inputs=["scoring disclosure missing"], tender_agent_inputs=["agent data incomplete"], split_procurement_inputs=["package publication incomplete"]),
        "stage3_profiles": _base_profiles(
            "project-cn-hold-001",
            {
                "qualification_clause_profile": {"signal_summary": "Qualification clause extraction is incomplete because the public chain is incomplete.", "risk_flags": ["insufficient_public_chain"], "confidence": 0.4},
                "parameter_requirement_profile": {"signal_summary": "Parameter extraction is incomplete because key records are missing.", "risk_flags": ["insufficient_public_chain"], "confidence": 0.4},
                "vendor_fit_profile": {"signal_summary": "Vendor fit cannot be assessed until the public chain is complete.", "risk_flags": ["insufficient_public_chain"], "confidence": 0.42},
                "scoring_anomaly_profile": {"signal_summary": "Scoring disclosure is unavailable due to incomplete public chain.", "risk_flags": ["missing_scoring_disclosure"], "confidence": 0.38},
                "tender_agent_profile": {"signal_summary": "Agent data is incomplete due to missing chain records.", "risk_flags": ["insufficient_public_chain"], "confidence": 0.39},
                "split_procurement_profile": {"signal_summary": "Split procurement could not be ruled out because package publication is incomplete.", "risk_flags": ["package_publication_incomplete"], "confidence": 0.44},
                "post_award_change_profile": {"signal_summary": "Post-award change chain has not started.", "risk_flags": [], "confidence": 0.35},
            },
        ),
        "stage4": {
            "evidence_id": "evidence-hold-001", "source_url": "https://ggzy.example.cn/hold/public-chain", "capture_type": "html_snapshot", "capture_time": "2026-04-04T17:40:00+08:00", "page_title": "Incomplete chain notice", "snippet": "Public chain notice shows that an opening record is still unavailable.", "evidence_artifact_refs": ["artifact://hold/public-chain.html"], "structured_field_refs": ["field://project-cn-hold-001/public_chain_status"], "evidence_grade": "B", "rule_hit_id": "rule-hit-hold-001", "rule_code": "PUBLIC_CHAIN_INCOMPLETE", "severity": "HIGH", "confidence": 0.88, "result_type": "CLUE", "why_hit": "The public chain is incomplete and opening records are missing.", "boundary_note": "The project cannot move to OPEN until the public chain is complete.", "target_entity_type": "project", "target_entity_id": "project-cn-hold-001", "review_status": "PENDING", "profile_keys": ["split_procurement_profile", "scoring_anomaly_profile"], "writeback_fields": ["public_chain_status", "clue_summary", "sale_gate_status"], "request_id": "review-request-hold-001", "request_type": "PUBLIC_CHAIN_COMPLETION", "request_topic": "public_chain_completeness", "resolution_path": "supplement_public_evidence", "blocking_scope": "project_progression", "reason": "The public chain is incomplete and must be completed before the project can proceed.", "public_basis": "The latest public chain notice shows that required public records are missing.", "requested_materials": ["opening record", "result publication notice"], "priority": "HIGH",
        },
        "stage5": {
            "report_id": "report-hold-001", "brief_path": "reports/hold-incomplete/brief.md", "evidence_pack_path": "reports/hold-incomplete/evidence-pack.zip", "objection_draft_path": "reports/hold-incomplete/objection-draft.md", "review_request_list_path": "reports/hold-incomplete/review-requests.json", "review_task_status": "WAITING_CHAIN_COMPLETION", "report_status": "DRAFT", "written_back_at": "2026-04-04T18:30:00+08:00",
        },
        "stage6": {
            "fact_version": 3, "fact_refresh_trigger": "PUBLIC_CHAIN_REFRESH", "fact_source_summary": "Derived from incomplete-chain project_base, structured profiles, rule_hit, and draft report_record.", "rule_hit_summary": "Public chain completeness is still unresolved.", "clue_summary": "The project remains on hold until public records are complete.", "sale_gate_status": "HOLD", "real_competitor_count": 0, "serviceable_competitor_count": 0, "competitor_quality_grade": "C", "price_cluster_score": 41, "price_gradient_pattern": "UNCERTAIN", "fact_summary": "Project cannot progress while the public chain remains incomplete.", "risk_summary": "Incomplete public chain keeps the project on HOLD.", "manual_override_status": "PENDING", "delivery_risk_state": "HOLD", "tender_fairness_risk": "MEDIUM", "evaluation_integrity_risk": "MEDIUM", "post_award_change_risk": "LOW", "award_suspicion_summary": "Public chain incompleteness blocks reliable downstream judgment.", "last_fact_refreshed_at": "2026-04-04T18:30:00+08:00",
        },
    },
    "case_block_high_risk": {
        "project_base": {
            "project_name": "Block High Risk Project", "project_type_raw": "building", "engineering_domain": "building_construction", "bid_control_price": 41000000, "bid_eval_method": "comprehensive", "public_chain_status": "COMPLETE", "opening_record_count": 1, "invalid_bid_count": 2,
        },
        "stage2_inputs": _stage2_inputs(tender_agent_inputs=["agent concentration history available"], split_procurement_inputs=["multi-package history available"]),
        "stage3_profiles": _base_profiles(
            "project-cn-block-001",
            {
                "vendor_fit_profile": {"signal_summary": "Vendor fit is concentrated around a repeated cluster.", "risk_flags": ["single_vendor_fit_pattern"], "confidence": 0.72},
                "tender_agent_profile": {"signal_summary": "Tender agent concentration and history create a high-risk cluster.", "risk_flags": ["agent_high_risk_concentration", "agent_history_penalty"], "confidence": 0.92},
                "post_award_change_profile": {"signal_summary": "Post-award change chain is not yet material, but region governance is already blocking.", "risk_flags": [], "confidence": 0.49},
            },
        ),
        "stage4": {
            "evidence_id": "evidence-block-001", "source_url": "https://ggzy.example.cn/block/agent-risk", "capture_type": "pdf_snapshot", "capture_time": "2026-04-04T17:50:00+08:00", "page_title": "High-risk agent result notice", "snippet": "Public result notice and agent history indicate a high-risk concentration pattern.", "evidence_artifact_refs": ["artifact://block/agent-risk.pdf"], "structured_field_refs": ["field://project-cn-block-001/tender_agent_profile/signal_summary"], "evidence_grade": "A", "rule_hit_id": "rule-hit-block-001", "rule_code": "AGENT_HIGH_RISK_CONCENTRATION_CLUE", "severity": "HIGH", "confidence": 0.92, "result_type": "CLUE", "why_hit": "Public agent history and repeat clustering indicate a high-risk concentration pattern.", "boundary_note": "The signal remains a clue, but governance and downstream delivery must stay blocked.", "target_entity_type": "tender_agent", "target_entity_id": "tender-agent-block-001", "review_status": "CONFIRMED", "profile_keys": ["tender_agent_profile", "vendor_fit_profile"], "writeback_fields": ["award_suspicion_summary", "tender_fairness_risk"], "request_id": "review-request-block-001", "request_type": "EXTERNAL_STATEMENT_REVIEW", "request_topic": "award_suspicion_summary", "resolution_path": "external_statement_or_regulator_response", "blocking_scope": "delivery_and_sales", "reason": "A high-risk agent concentration clue requires external confirmation before any release.", "public_basis": "Public result notice and agent-history evidence indicate a high-risk concentration pattern.", "requested_materials": ["full evidence pack", "agent-history review memo", "external statement"], "priority": "HIGH",
        },
        "stage5": {
            "report_id": "report-block-001", "brief_path": "reports/block-high-risk/brief.md", "evidence_pack_path": "reports/block-high-risk/evidence-pack.zip", "objection_draft_path": "reports/block-high-risk/objection-draft.md", "review_request_list_path": "reports/block-high-risk/review-requests.json", "review_task_status": "LEGAL_REVIEW_PENDING", "report_status": "DRAFT", "written_back_at": "2026-04-04T18:40:00+08:00",
        },
        "stage6": {
            "fact_version": 4, "fact_refresh_trigger": "HIGH_RISK_RULE_HIT", "fact_source_summary": "Derived from high-risk project_base, structured profiles, rule_hit, and draft report_record.", "rule_hit_summary": "A high-risk agent concentration clue blocks the project by governance policy.", "clue_summary": "No soft clue path remains; the project is in a blocking state.", "sale_gate_status": "BLOCK", "real_competitor_count": 5, "serviceable_competitor_count": 0, "competitor_quality_grade": "D", "price_cluster_score": 14, "price_gradient_pattern": "COLLUSION_PATTERN", "fact_summary": "Project is blocked by governance and downstream delivery controls.", "risk_summary": "A confirmed high-risk agent concentration clue and suspended coverage state block sales and delivery.", "manual_override_status": "CONFIRMED", "delivery_risk_state": "BLOCK", "tender_fairness_risk": "HIGH", "evaluation_integrity_risk": "MEDIUM", "post_award_change_risk": "MEDIUM", "award_suspicion_summary": "High-risk agent concentration keeps the project blocked.", "last_fact_refreshed_at": "2026-04-04T18:40:00+08:00",
        },
    },
}


def get_scenario_profile(scenario_id: str) -> dict[str, Any]:
    try:
        return SCENARIO_PROFILES[scenario_id]
    except KeyError as error:
        raise ValueError(f"unsupported scenario_id: {scenario_id}") from error


def get_scenario_id(raw_payload: dict[str, Any]) -> str:
    scenario_id = raw_payload.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise ValueError("raw payload must include scenario_id")
    get_scenario_profile(scenario_id)
    return scenario_id
