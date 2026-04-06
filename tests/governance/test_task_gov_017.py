from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .helpers import (
    AUTOMATION_INTENT_SCRIPT,
    TASK_OPS_SCRIPT,
    git_commit_all,
    init_governance_repo,
    read_yaml,
    run_python,
    write_yaml,
)


def _preflight(repo: Path, utterance: str) -> tuple[int, dict]:
    result = run_python(AUTOMATION_INTENT_SCRIPT, repo, "preflight", "--utterance", utterance)
    return result.returncode, json.loads(result.stdout)


def _create_successor(repo: Path, task_id: str) -> None:
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        task_id,
        "--title",
        "next coordination task",
        "--stage",
        "next-phase",
        "--branch",
        f"feat/{task_id}",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "scripts/",
        "tests/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "scripts/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created.returncode == 0, created.stdout + created.stderr


def _mark_review_ready(repo: Path) -> None:
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-BASE-001",
        "--summary",
        "review ready",
        "--tests",
        "pytest tests/base -q",
    )
    assert finished.returncode == 0, finished.stdout + finished.stderr
    git_commit_all(repo, "prepare review continuation")


def test_continue_roadmap_self_heals_stale_done_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo, "TASK-DONE-001")
    _create_successor(repo, "TASK-NEXT-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    stale = next(task for task in registry["tasks"] if task["task_id"] == "TASK-DONE-001")
    stale["status"] = "done"
    stale["worker_state"] = "completed"
    stale["activated_at"] = "2026-04-04T00:00:00+08:00"
    stale["closed_at"] = "2026-04-04T00:00:00+08:00"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    roadmap_path = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    roadmap = roadmap_path.read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-DONE-001", 1)
    roadmap_path.write_text(roadmap, encoding="utf-8")
    _mark_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    updated_roadmap = roadmap_path.read_text(encoding="utf-8")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert "next_recommended_task_id: TASK-NEXT-001" in updated_roadmap


def test_preflight_supports_continuous_roadmap_phrase(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo, "TASK-NEXT-001")
    roadmap_path = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    roadmap = roadmap_path.read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    roadmap_path.write_text(roadmap, encoding="utf-8")
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "持续按路线图开发")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "continue-roadmap-loop"


def test_preflight_continue_current_allows_governance_dirty_only(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    roadmap_path = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    roadmap_path.write_text(
        roadmap_path.read_text(encoding="utf-8") + "\n<!-- governance dirty -->\n",
        encoding="utf-8",
    )

    code, payload = _preflight(repo, "继续当前任务")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "continue-current"
