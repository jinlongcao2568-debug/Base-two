from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_stage4_rule_hit_fixture_matches_schema_and_project_base() -> None:
    project_base = load_json(ROOT / "tests/fixtures/normalized/project_base.normalized.json")
    rule_hit = load_json(ROOT / "tests/fixtures/rules/rule_hit.normalized.json")
    schema = load_json(ROOT / "docs/contracts/schemas/stage4_rule_hit.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(rule_hit), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]
    assert rule_hit["project_id"] == project_base["project_id"]
    assert rule_hit["evidence_refs"]
    assert rule_hit["review_status"] == "PENDING"
