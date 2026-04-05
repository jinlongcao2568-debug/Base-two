from __future__ import annotations

from pathlib import Path
from typing import Any

from src.domain.engineering.public_chain.runtime import build_public_chain_view
from src.stage1_orchestration.runtime import build_ingestion_job
from src.stage2_ingestion.runtime import build_raw_ingestion_artifact
from src.stage3_parsing.runtime import build_project_base
from src.stage4_validation.runtime import evaluate_formal_objects
from src.stage5_reporting.runtime import build_report_record
from src.stage6_facts.runtime import build_project_fact
from src.shared.contracts.runtime_support import write_json


def run_minimal_runtime_chain(
    *,
    scenario_id: str | None = None,
    raw_fixture_path: str | None = None,
    requested_at: str | None = None,
) -> dict[str, Any]:
    ingestion_job = build_ingestion_job(
        scenario_id=scenario_id,
        raw_fixture_path=raw_fixture_path,
        requested_at=requested_at,
    )
    raw_ingestion_artifact = build_raw_ingestion_artifact(ingestion_job)
    resolved_scenario_id = raw_ingestion_artifact["scenario_id"]
    project_base = build_project_base(raw_ingestion_artifact)
    stage4_outputs = evaluate_formal_objects(raw_ingestion_artifact, project_base)
    report_record = build_report_record(project_base, resolved_scenario_id)
    project_fact = build_project_fact(
        project_base,
        stage4_outputs["rule_hits"],
        report_record,
        resolved_scenario_id,
    )
    public_chain_view = build_public_chain_view(project_base, project_fact)
    return {
        "scenario_id": resolved_scenario_id,
        "stage1": {"ingestion_job": ingestion_job},
        "stage2": {"raw_ingestion_artifact": raw_ingestion_artifact},
        "stage3": {"project_base": project_base},
        "stage4": stage4_outputs,
        "stage5": {"report_record": report_record},
        "stage6": {"project_fact": project_fact},
        "consumers": {"public_chain_view": public_chain_view},
    }


def write_runtime_outputs(output_dir: str | Path, bundle: dict[str, Any]) -> dict[str, str]:
    base_dir = Path(output_dir)
    artifacts = {
        "stage1.ingestion_job": base_dir / "stage1" / "ingestion_job.json",
        "stage2.raw_ingestion_artifact": base_dir / "stage2" / "raw_ingestion_artifact.json",
        "stage3.project_base": base_dir / "stage3" / "project_base.json",
        "stage4.rule_hits": base_dir / "stage4" / "rule_hits.json",
        "stage4.evidences": base_dir / "stage4" / "evidences.json",
        "stage4.review_requests": base_dir / "stage4" / "review_requests.json",
        "stage5.report_record": base_dir / "stage5" / "report_record.json",
        "stage6.project_fact": base_dir / "stage6" / "project_fact.json",
        "consumers.public_chain_view": base_dir / "consumers" / "public_chain_view.json",
    }
    write_json(artifacts["stage1.ingestion_job"], bundle["stage1"]["ingestion_job"])
    write_json(artifacts["stage2.raw_ingestion_artifact"], bundle["stage2"]["raw_ingestion_artifact"])
    write_json(artifacts["stage3.project_base"], bundle["stage3"]["project_base"])
    write_json(artifacts["stage4.rule_hits"], bundle["stage4"]["rule_hits"])
    write_json(artifacts["stage4.evidences"], bundle["stage4"]["evidences"])
    write_json(artifacts["stage4.review_requests"], bundle["stage4"]["review_requests"])
    write_json(artifacts["stage5.report_record"], bundle["stage5"]["report_record"])
    write_json(artifacts["stage6.project_fact"], bundle["stage6"]["project_fact"])
    write_json(artifacts["consumers.public_chain_view"], bundle["consumers"]["public_chain_view"])
    return {name: path.as_posix() for name, path in artifacts.items()}
