from __future__ import annotations

import json
from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, git_commit_all, init_governance_repo, run_python, set_idle_control_plane


def test_activate_blocks_when_task_package_incomplete(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-COMP-001",
        "--title",
        "incomplete task",
        "--stage",
        "governance-test",
        "--branch",
        "main",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    git_commit_all(repo, "prepare incomplete task package")

    result = run_python(TASK_OPS_SCRIPT, repo, "activate", "TASK-COMP-001")

    assert result.returncode == 1
    assert "task package incomplete" in result.stdout


def test_audit_task_packages_reports_incomplete(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-COMP-002",
        "--title",
        "incomplete audit task",
        "--stage",
        "governance-test",
        "--branch",
        "main",
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "audit-task-packages")
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["incomplete_count"] >= 1
    assert "TASK-COMP-002" in {item["task_id"] for item in payload["incomplete_tasks"]}
