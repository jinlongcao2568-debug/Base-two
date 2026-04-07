from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_v15_governance_assets_are_independent_and_referenced() -> None:
    coverage = load_yaml(ROOT / "docs/contracts/coverage_governance_registry.yaml")
    field_policy = load_yaml(ROOT / "docs/contracts/field_policy_dictionary.yaml")
    object_matrix = load_yaml(ROOT / "docs/contracts/delivery_object_matrix.yaml")
    whitelist = load_yaml(ROOT / "docs/contracts/customer_delivery_field_whitelist.yaml")
    blacklist = load_yaml(ROOT / "docs/contracts/customer_delivery_field_blacklist.yaml")
    interface_catalog = load_yaml(ROOT / "docs/governance/INTERFACE_CATALOG.yaml")

    assert coverage["registry_name"] == "coverage_governance_registry"
    assert field_policy["registry_name"] == "field_policy_dictionary"
    assert object_matrix["registry_name"] == "delivery_object_matrix"
    assert whitelist["field_policy_dictionary_source"] == "docs/contracts/field_policy_dictionary.yaml"
    assert whitelist["delivery_object_matrix_source"] == "docs/contracts/delivery_object_matrix.yaml"
    assert blacklist["field_policy_dictionary_source"] == "docs/contracts/field_policy_dictionary.yaml"
    assert blacklist["delivery_object_matrix_source"] == "docs/contracts/delivery_object_matrix.yaml"
    assert interface_catalog["status"] == "registered_formal_catalog"
    assert len(interface_catalog["interfaces"]) == 10
    assert {item["implementation_status"] for item in interface_catalog["interfaces"]} == {"contract_only"}
