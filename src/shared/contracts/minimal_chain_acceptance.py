from __future__ import annotations

from typing import Any

from src.shared.contracts.public_chain_contract import validate_public_chain_view
from src.shared.contracts.runtime_support import load_json, load_yaml, validate_schema


ACCEPTANCE_CONTRACT_PATH = "docs/contracts/minimal_runtime_chain_acceptance.yaml"


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
            if payload != [expected]:
                errors.append(f"{artifact_key} does not match expected fixture payload")
        elif payload != expected:
            errors.append(f"{artifact_key} does not match expected fixture payload")

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
