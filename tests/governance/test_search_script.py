from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SEARCH_SCRIPT = ROOT / "scripts" / "search.ps1"


def run_search(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SEARCH_SCRIPT),
            *args,
        ],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_search_script_auto_finds_visible_matches_and_skips_git_noise(tmp_path: Path) -> None:
    visible = tmp_path / "visible.txt"
    visible.write_text("needle value\n", encoding="utf-8")
    hidden_git = tmp_path / ".git"
    hidden_git.mkdir()
    (hidden_git / "ignored.txt").write_text("needle value\n", encoding="utf-8")

    result = run_search("-Pattern", "needle value", "-Path", str(tmp_path), cwd=ROOT)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "visible.txt:1:needle value" in result.stdout
    assert "ignored.txt" not in result.stdout


def test_search_script_selectstring_backend_supports_regex_and_no_match_exit(tmp_path: Path) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text("task_id = 'TASK-GOV-075'\n", encoding="utf-8")

    matched = run_search(
        "-Pattern",
        "TASK-GOV-[0-9]{3}",
        "-Path",
        str(tmp_path),
        "-Backend",
        "SelectString",
        "-Regex",
        cwd=ROOT,
    )

    assert matched.returncode == 0, matched.stdout + matched.stderr
    assert "sample.py:1:task_id = 'TASK-GOV-075'" in matched.stdout

    missing = run_search(
        "-Pattern",
        "TASK-GOV-999",
        "-Path",
        str(tmp_path),
        "-Backend",
        "SelectString",
        cwd=ROOT,
    )

    assert missing.returncode == 1, missing.stdout + missing.stderr
