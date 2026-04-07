from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import yaml


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
    text = text.replace("current_phase: authority-consistency-hardening", "current_phase: idle")
    text = text.replace("current_task_id: TASK-GOV-001", "current_task_id: null")
    text = text.replace(
        "- `TASK-GOV-001`: `",
        "- no live current task; waiting for explicit activation or roadmap continuation.\n",
    )
    roadmap.write_text(text, encoding="utf-8")


def activate_live_task(repo: Path, task_id: str = "TASK-GOV-001") -> None:
    registry_path = repo / "docs/governance/TASK_REGISTRY.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    task = next(item for item in registry["tasks"] if item["task_id"] == task_id)
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    registry_path.write_text(yaml.safe_dump(registry, allow_unicode=True, sort_keys=False), encoding="utf-8")

    current_task_path = repo / "docs/governance/CURRENT_TASK.yaml"
    current_task = yaml.safe_load(current_task_path.read_text(encoding="utf-8"))
    current_task.update(
        {
            "current_task_id": task["task_id"],
            "title": task["title"],
            "status": task["status"],
            "task_kind": task["task_kind"],
            "execution_mode": task["execution_mode"],
            "parent_task_id": task["parent_task_id"],
            "stage": task["stage"],
            "branch": task["branch"],
            "size_class": task["size_class"],
            "automation_mode": task["automation_mode"],
            "worker_state": task["worker_state"],
            "blocked_reason": task["blocked_reason"],
            "topology": task["topology"],
            "allowed_dirs": task["allowed_dirs"],
            "reserved_paths": task["reserved_paths"],
            "planned_write_paths": task["planned_write_paths"],
            "planned_test_paths": task["planned_test_paths"],
            "required_tests": task["required_tests"],
            "task_file": task["task_file"],
            "runlog_file": task["runlog_file"],
            "lane_count": task["lane_count"],
            "lane_index": task["lane_index"],
            "parallelism_plan_id": task["parallelism_plan_id"],
            "review_bundle_status": task["review_bundle_status"],
        }
    )
    current_task_path.write_text(yaml.safe_dump(current_task, allow_unicode=True, sort_keys=False), encoding="utf-8")

    roadmap = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    text = roadmap.read_text(encoding="utf-8")
    text = text.replace("current_phase: idle", f"current_phase: {task['stage']}", 1)
    text = text.replace("current_task_id: null", f"current_task_id: {task_id}", 1)
    text = text.replace(
        "- no live current task; waiting for explicit activation or roadmap continuation.",
        f"- `{task_id}`: `synthetic live task` is the live coordination task for `{task['stage']}`.",
        1,
    )
    roadmap.write_text(text, encoding="utf-8")


def test_authority_alignment_passes_on_current_repo() -> None:
    result = run_alignment(REPO_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "project_fact: 对齐" in result.stdout
    assert "综合评分: 100" in result.stdout


def test_authority_alignment_fails_when_roadmap_is_stale_after_activation(tmp_path: Path) -> None:
    repo = init_alignment_repo(tmp_path)
    activate_live_task(repo)
    write_stale_roadmap(repo)
    result = run_alignment(repo)
    assert result.returncode == 1
    assert "[ERROR] 一致性: 80" in result.stdout
    assert "roadmap current_task_id conflicts with CURRENT_TASK.yaml" in result.stdout
    assert "roadmap current_phase conflicts with CURRENT_TASK.yaml" in result.stdout
    assert "roadmap body does not mention the live current task" in result.stdout
    assert "综合评分: 96" in result.stdout


def test_authority_alignment_fails_when_live_boundary_doc_is_missing(tmp_path: Path) -> None:
    repo = init_alignment_repo(tmp_path)
    (repo / "docs/governance/LIVE_GOVERNANCE_BOUNDARY.md").unlink()

    result = run_alignment(repo)

    assert result.returncode == 1
    assert "missing required file: docs/governance/LIVE_GOVERNANCE_BOUNDARY.md" in result.stdout
