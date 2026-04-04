from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_stage3_project_base_fixture_matches_schema_and_raw_source() -> None:
    raw_notice = load_json(ROOT / "tests/fixtures/raw/project_notice.raw.json")
    project_base = load_json(ROOT / "tests/fixtures/normalized/project_base.normalized.json")
    schema = load_json(ROOT / "docs/contracts/schemas/stage3_project_base.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(project_base), key=lambda item: list(item.path))
    assert not errors, [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in errors]
    assert project_base["project_id"] == raw_notice["project_id"]
    assert project_base["project_name"] == raw_notice["project_name"]
    assert project_base["public_chain_status"] == raw_notice["public_chain_status"]
