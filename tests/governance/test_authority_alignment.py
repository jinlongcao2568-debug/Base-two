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
        encoding="utf-8",
        errors="replace",
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


def write_stale_roadmap(repo: Path) -> None:
    roadmap = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    text = roadmap.read_text(encoding="utf-8")
    text = text.replace("current_phase: governance-parallel-repair-bundle-v1", "current_phase: idle")
    text = text.replace("current_task_id: TASK-GOV-020", "current_task_id: null")
    text = text.replace(
        "- `TASK-GOV-020`: `",
        "- no live current task; waiting for explicit activation or roadmap continuation.\n",
    )
    roadmap.write_text(text, encoding="utf-8")


def test_authority_alignment_passes_on_current_repo() -> None:
    result = run_alignment(REPO_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "project_fact: 对齐" in result.stdout
    assert "综合评分: 100" in result.stdout


def test_authority_alignment_fails_when_roadmap_is_stale_after_activation(tmp_path: Path) -> None:
    repo = init_alignment_repo(tmp_path)
    write_stale_roadmap(repo)
    result = run_alignment(repo)
    assert result.returncode == 1
    assert "[ERROR] 一致性: 80" in result.stdout
    assert "roadmap current_task_id conflicts with CURRENT_TASK.yaml" in result.stdout
    assert "roadmap current_phase conflicts with CURRENT_TASK.yaml" in result.stdout
    assert "roadmap body does not mention the live current task" in result.stdout
    assert "综合评分: 96" in result.stdout
