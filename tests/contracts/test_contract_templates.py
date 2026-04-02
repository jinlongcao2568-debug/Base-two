from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_contract_templates_validate() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_contracts.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
