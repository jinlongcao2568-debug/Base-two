from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_alignment(repo: Path) -> subprocess.CompletedProcess[str]:
    script = repo / "scripts" / "check_authority_alignment.py"
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=repo,
        text=True,
        capture_output=True,
    )


def init_alignment_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    for relative in ("README.md", "docs", "scripts", "tests"):
        source = REPO_ROOT / relative
        target = repo / relative
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    subprocess.run(
        ["git", "init", "-b", "feat/TASK-GOV-001-authority-consistency-hardening"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "config", "user.name", "Codex"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def test_authority_alignment_passes_on_current_repo() -> None:
    result = run_alignment(REPO_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "project_fact: 对齐" in result.stdout
    assert "综合评分: 100" in result.stdout


def test_authority_alignment_fails_when_capability_map_missing(tmp_path: Path) -> None:
    repo = init_alignment_repo(tmp_path)
    (repo / "docs/governance/CAPABILITY_MAP.yaml").unlink()
    result = run_alignment(repo)
    assert result.returncode == 1
    assert "missing required file: docs/governance/CAPABILITY_MAP.yaml" in result.stdout
    assert "展开完整度: 80" in result.stdout
