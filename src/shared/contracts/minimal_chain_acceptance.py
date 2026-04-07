from __future__ import annotations

from typing import Any

from src.shared.contracts.public_chain_contract import validate_public_chain_view
from src.shared.contracts.runtime_support import load_json, load_yaml, validate_schema


ACCEPTANCE_CONTRACT_PATH = "docs/contracts/minimal_runtime_chain_acceptance.yaml"
FIXTURE_KEY_SUBSETS = {
    "stage3.project_base": ("project_id", "source_family", "region_code", "project_name", "public_chain_status"),
    "stage4.rule_hits": ("rule_hit_id", "project_id"),
    "stage4.evidences": ("evidence_id", "project_id", "evidence_grade"),
    "stage4.review_requests": ("request_id", "project_id"),
    "stage5.report_record": ("report_id", "project_id", "report_status"),
    "stage6.project_fact": ("project_id", "sale_gate_status", "review_status", "report_status"),
    "stage7.sales_context": ("project_id", "sale_gate_status"),
    "stage8.contact_context": ("project_id", "sale_gate_status"),
    "stage9.delivery_payload": ("project_id", "sale_gate_status", "report_status"),
}


def _load_acceptance_contract() -> dict[str, Any]:
    document = load_yaml(ACCEPTANCE_CONTRACT_PATH)
    return document["acceptance"]


def evaluate_minimal_chain_acceptance(output_paths: dict[str, str], scenario_id: str) -> dict[str, Any]:
    acceptance = _load_acceptance_contract()
    errors: list[str] = []

    for artifact_key in acceptance["artifacts"]:
        if artifact_key not in output_paths:
            errors.append(f"missing artifact from output map: {artifact_key}")

    for artifact_key, schema_path in acceptance["schema_checks"].items():
        payload = load_json(output_paths[artifact_key])
        if artifact_key.startswith("stage4."):
            for item in payload:
                errors.extend(validate_schema(schema_path, item))
        else:
            errors.extend(validate_schema(schema_path, payload))

    for artifact_key, fixture_pattern in acceptance["fixture_checks"].items():
        payload = load_json(output_paths[artifact_key])
        expected = load_json(fixture_pattern.format(scenario_id=scenario_id))
        if artifact_key.startswith("stage4."):
            if len(payload) != 1:
                errors.append(f"{artifact_key} must contain exactly one payload item")
                continue
            for key in FIXTURE_KEY_SUBSETS[artifact_key]:
                if payload[0].get(key) != expected.get(key):
                    errors.append(f"{artifact_key} drift on {key}")
        else:
            for key in FIXTURE_KEY_SUBSETS[artifact_key]:
                if payload.get(key) != expected.get(key):
                    errors.append(f"{artifact_key} drift on {key}")

    public_chain_view = load_json(output_paths["consumers.public_chain_view"])
    errors.extend(validate_public_chain_view(public_chain_view))
    whitelist = load_yaml(acceptance["consumer_field_whitelist"])
    allowed_fields = {
        item["field"]
        for group in whitelist["allowlist"].values()
        for item in group
    }
    unexpected = sorted(set(public_chain_view) - allowed_fields)
    if unexpected:
        errors.append(f"public_chain_view uses fields outside whitelist: {', '.join(unexpected)}")

    return {
        "policy_id": acceptance["acceptance_id"],
        "scenario_id": scenario_id,
        "accepted": not errors,
        "errors": errors,
    }
