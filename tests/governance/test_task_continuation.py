from __future__ import annotations

import subprocess
from pathlib import Path

from .helpers import (
    CHECK_REPO_SCRIPT,
    TASK_OPS_SCRIPT,
    close_live_task_to_idle,
    git_commit_all,
    init_governance_repo,
    read_yaml,
    run_python_inline as run_python,
    set_live_task_review_without_evidence,
    set_idle_control_plane,
    write_yaml,
)
from .task_continuation_scenarios import create_successor, mark_current_review_ready, prepare_review_ready_parallel_parent


def test_continue_current_keeps_live_task_when_doing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(TASK_OPS_SCRIPT, repo, "continue-current")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-BASE-001"
    assert current_task["status"] == "doing"


def test_continue_current_reactivates_paused_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    paused = run_python(TASK_OPS_SCRIPT, repo, "pause")
    assert paused.returncode == 0, paused.stdout + paused.stderr
    result = run_python(TASK_OPS_SCRIPT, repo, "continue-current")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["status"] == "doing"
    assert registry["tasks"][0]["worker_state"] == "running"


def test_continue_current_rejects_blocked_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    blocked = run_python(TASK_OPS_SCRIPT, repo, "worker-blocked", "TASK-BASE-001", "--reason", "waiting on dependency")
    assert blocked.returncode == 0, blocked.stdout + blocked.stderr
    result = run_python(TASK_OPS_SCRIPT, repo, "continue-current")
    assert result.returncode == 1
    assert "blocked" in result.stdout


def test_continue_current_rejects_idle_state(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    result = run_python(TASK_OPS_SCRIPT, repo, "continue-current")
    assert result.returncode == 1
    assert "no live current task" in result.stdout


def test_continue_current_closes_review_ready_parallel_parent_to_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    prepare_review_ready_parallel_parent(repo, tmp_path)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-current")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-BASE-001")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["status"] == "idle"
    assert current_task["current_task_id"] is None
    assert parent["status"] == "done"
    assert "closed TASK-BASE-001 to idle" in result.stdout


def test_continue_roadmap_closes_review_task_and_activates_explicit_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-BASE-001"]["status"] == "done"
    assert tasks["TASK-NEXT-001"]["status"] == "doing"
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_continue_roadmap_closes_review_ready_parallel_parent_and_activates_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    prepare_review_ready_parallel_parent(repo, tmp_path)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-BASE-001"]["status"] == "done"
    assert tasks["TASK-NEXT-001"]["status"] == "doing"


def test_continue_roadmap_blocks_live_parent_until_ai_guarded_closeout_is_ready(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    git_commit_all(repo, "prepare successor while current task is still active")

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")

    assert result.returncode == 1
    assert "ai_guarded closeout is ready" in result.stdout


def test_continue_roadmap_activates_explicit_successor_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    close_live_task_to_idle(repo, commit_after_close=True)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert current_task["status"] == "doing"
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_continue_roadmap_auto_checkpoints_live_review_task_with_in_scope_changes(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)
    (repo / "src/base/module.py").write_text("def base_value():\n    return 7\n", encoding="utf-8")

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    last_commit = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-BASE-001"]["status"] == "done"
    assert "checkpoint TASK-BASE-001" in last_commit
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_continue_roadmap_auto_checkpoints_recoverable_predecessor_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    close_live_task_to_idle(repo, commit_after_close=False)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    last_commit = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-BASE-001"]["status"] == "done"
    assert "checkpoint TASK-BASE-001" in last_commit
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr


def test_continue_roadmap_rejects_dirty_review_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)
    (repo / "docs/governance/dirty.md").write_text("dirty\n", encoding="utf-8")
    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "dirty.md" in result.stdout


def test_continue_roadmap_rejects_review_without_test_evidence(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    set_live_task_review_without_evidence(repo, commit_after_update=True)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")

    assert result.returncode == 1
    assert "required tests missing from runlog" in result.stdout


def test_continue_roadmap_rejects_live_ledger_drift(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["branch"] = "feat/drifted-branch"
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    git_commit_all(repo, "introduce live ledger drift")

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")

    assert result.returncode == 1
    assert "live ledger drift detected" in result.stdout
