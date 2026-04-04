from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_handoff_catalog_consumes_real_chain_payloads() -> None:
    catalog = load_yaml(ROOT / "docs/contracts/handoff_catalog.yaml")
    project_base = load_json(ROOT / "tests/fixtures/normalized/project_base.normalized.json")
    rule_hit = load_json(ROOT / "tests/fixtures/rules/rule_hit.normalized.json")
    project_fact = load_json(ROOT / "tests/fixtures/facts/project_fact.normalized.json")
    report_record = load_json(ROOT / "docs/contracts/examples/report_record.example.json")

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
