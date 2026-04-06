from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CASES = (
    "case_review_ready",
    "case_open_issued",
    "case_hold_incomplete_chain",
    "case_block_high_risk",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_id", CASES)
def test_cli_runs_minimal_runtime_chain_and_accepts(case_id: str, tmp_path: Path) -> None:
    output_dir = tmp_path / case_id
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_minimal_runtime_chain.py"),
            "--scenario-id",
            case_id,
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    acceptance = load_json(output_dir / "acceptance" / "result.json")
    assert acceptance["accepted"] is True
    assert load_json(output_dir / "stage6" / "project_fact.json")["project_id"].startswith("project-cn-")
    assert load_json(output_dir / "stage7" / "sales_context.json")["project_id"].startswith("project-cn-")
    assert load_json(output_dir / "stage8" / "contact_context.json")["project_id"].startswith("project-cn-")
    assert load_json(output_dir / "stage9" / "delivery_payload.json")["project_id"].startswith("project-cn-")
