from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = ROOT / "docs" / "contracts"
SCHEMAS_DIR = CONTRACTS_DIR / "schemas"
ROOT_DUPLICATES = [
    ROOT / "sources_registry.yaml",
    ROOT / "region_coverage_registry.yaml",
    ROOT / "customer_delivery_field_whitelist.yaml",
    ROOT / "customer_delivery_field_blacklist.yaml",
]

FILES = {
    "sources_registry.yaml": "sources_registry.schema.json",
    "region_coverage_registry.yaml": "region_coverage_registry.schema.json",
    "customer_delivery_field_whitelist.yaml": "customer_delivery_field_whitelist.schema.json",
    "customer_delivery_field_blacklist.yaml": "customer_delivery_field_blacklist.schema.json",
}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    has_error = False

    for duplicate in ROOT_DUPLICATES:
        if duplicate.exists():
            has_error = True
            print(f"[ERROR] duplicate contract yaml outside docs/contracts: {duplicate}")

    for yaml_name, schema_name in FILES.items():
        yaml_path = CONTRACTS_DIR / yaml_name
        schema_path = SCHEMAS_DIR / schema_name

        if not yaml_path.exists():
            print(f"[ERROR] missing yaml: {yaml_path}")
            has_error = True
            continue
        if not schema_path.exists():
            print(f"[ERROR] missing schema: {schema_path}")
            has_error = True
            continue

        data = load_yaml(yaml_path)
        schema = load_json(schema_path)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

        if errors:
            has_error = True
            print(f"[ERROR] validation failed: {yaml_name}")
            for err in errors:
                path = ".".join(str(x) for x in err.path) or "<root>"
                print(f"  - {path}: {err.message}")
        else:
            print(f"[OK] {yaml_name}")

    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
