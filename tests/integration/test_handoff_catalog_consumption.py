from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml

from src.shared.contracts.minimal_chain_pipeline import run_minimal_runtime_chain


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_handoff_catalog_consumes_real_chain_payloads() -> None:
    catalog = load_yaml(ROOT / "docs/contracts/handoff_catalog.yaml")
    bundle = run_minimal_runtime_chain(
        scenario_id="case_review_ready",
        requested_at="2026-04-05T10:00:00+08:00",
    )
    project_base = bundle["stage3"]["project_base"]
    rule_hit = bundle["stage4"]["rule_hits"][0]
    project_fact = bundle["stage6"]["project_fact"]
    report_record = bundle["stage5"]["report_record"]

    payloads = {
        "stage3-to-stage4-project_base": project_base,
        "stage4-to-stage6-rule_hit": rule_hit,
        "stage5-to-stage6-report_record": report_record,
        "stage6-to-stage7-project_fact": project_fact,
        "stage6-to-stage8-project_fact": project_fact,
        "stage6-to-stage9-project_fact": project_fact,
    }

    for entry in catalog["handoffs"]:
        payload = payloads[entry["handoff_id"]]
        for field_name in entry["lineage_fields"]:
            assert field_name in payload, f"{entry['handoff_id']} missing lineage field {field_name}"
        for field_name in entry["required_payload_fields"]:
            assert field_name in payload, f"{entry['handoff_id']} missing required payload field {field_name}"

    assert project_base["project_id"] == rule_hit["project_id"] == project_fact["project_id"] == report_record["project_id"]
    assert report_record["report_status"] == project_fact["report_status"] == "READY"
    assert project_fact["project_base_ref"].startswith("project_base:")
    assert project_fact["rule_hit_refs"] == [f"rule_hit:{rule_hit['rule_hit_id']}"]
