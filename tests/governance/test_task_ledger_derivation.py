from __future__ import annotations

import subprocess
from pathlib import Path

from .helpers import (
    TASK_OPS_SCRIPT,
    close_live_task_to_idle,
    init_governance_repo,
    read_roadmap,
    read_yaml,
    run_python_inline as run_python,
    write_roadmap,
    write_yaml,
)


def test_queue_and_activate_creates_and_activates_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    close_live_task_to_idle(repo, commit_after_close=True)

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "queue-and-activate",
        "TASK-QA-001",
        "--title",
        "queue activate task",
        "--stage",
        "queue-activate-stage",
        "--branch",
        "feat/TASK-QA-001",
        "--allowed-dirs",
        "docs/governance/",
        "scripts/",
        "tests/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "scripts/",
        "tests/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    roadmap_frontmatter, _ = read_roadmap(repo / "docs/governance/DEVELOPMENT_ROADMAP.md")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-QA-001")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-QA-001")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_branch == "feat/TASK-QA-001"
    assert current_task["current_task_id"] == "TASK-QA-001"
    assert current_task["status"] == "doing"
    assert task["status"] == "doing"
    assert task["worker_state"] == "running"
    assert entry["status"] == "active"
    assert roadmap_frontmatter["current_task_id"] == "TASK-QA-001"
    assert (repo / "docs/governance/tasks/TASK-QA-001.md").exists()
    assert (repo / "docs/governance/runlogs/TASK-QA-001-RUNLOG.md").exists()
    assert (repo / "docs/governance/handoffs/TASK-QA-001.yaml").exists()


def test_queue_and_activate_existing_ok_repairs_queued_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    close_live_task_to_idle(repo, commit_after_close=True)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-QA-EXISTING",
        "--title",
        "queued task",
        "--stage",
        "queue-activate-stage",
        "--branch",
        "main",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created.returncode == 0, created.stdout + created.stderr

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "queue-and-activate",
        "TASK-QA-EXISTING",
        "--title",
        "ignored for existing",
        "--stage",
        "ignored-stage",
        "--existing-ok",
    )
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-QA-EXISTING")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-QA-EXISTING"
    assert task["status"] == "doing"
    assert task["branch"] == "main"


def test_queue_and_activate_dirty_branch_switch_leaves_no_task_artifacts(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    close_live_task_to_idle(repo, commit_after_close=True)
    (repo / "docs/governance/dirty.md").write_text("dirty\n", encoding="utf-8")

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "queue-and-activate",
        "TASK-QA-DIRTY",
        "--title",
        "dirty task",
        "--stage",
        "dirty-stage",
        "--branch",
        "feat/TASK-QA-DIRTY",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task_ids = {task["task_id"] for task in registry["tasks"]}

    assert result.returncode == 1
    assert "worktree must be clean" in result.stdout
    assert "TASK-QA-DIRTY" not in task_ids
    assert not (repo / "docs/governance/tasks/TASK-QA-DIRTY.md").exists()
    assert not (repo / "docs/governance/runlogs/TASK-QA-DIRTY-RUNLOG.md").exists()


def test_derive_ledgers_from_current_task_repairs_live_ledgers(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["status"] = "paused"
    registry["tasks"][0]["worker_state"] = "idle"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    worktrees["entries"][0]["status"] = "closed"
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    roadmap_frontmatter, roadmap_body = read_roadmap(repo / "docs/governance/DEVELOPMENT_ROADMAP.md")
    roadmap_frontmatter["current_task_id"] = None
    roadmap_frontmatter["current_phase"] = "idle"
    write_roadmap(repo / "docs/governance/DEVELOPMENT_ROADMAP.md", roadmap_frontmatter, roadmap_body)

    result = run_python(TASK_OPS_SCRIPT, repo, "derive-ledgers", "--from", "current-task", "--write")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    roadmap_frontmatter, _ = read_roadmap(repo / "docs/governance/DEVELOPMENT_ROADMAP.md")

    assert result.returncode == 0, result.stdout + result.stderr
    assert registry["tasks"][0]["status"] == "doing"
    assert registry["tasks"][0]["worker_state"] == "running"
    assert worktrees["entries"][0]["status"] == "active"
    assert roadmap_frontmatter["current_task_id"] == "TASK-BASE-001"
    assert roadmap_frontmatter["current_phase"] == "base-phase"


def test_derive_ledgers_from_closed_task_file_does_not_override_other_live_current(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-CLOSED-001",
        "--title",
        "closed history",
        "--stage",
        "closed-stage",
        "--branch",
        "main",
        "--status",
        "done",
        "--worker-state",
        "completed",
        "--planned-write-paths",
        "docs/governance/",
    )
    assert created.returncode == 0, created.stdout + created.stderr

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "derive-ledgers",
        "--from",
        "task-file",
        "--task-id",
        "TASK-CLOSED-001",
        "--write",
    )
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-CLOSED-001")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-BASE-001"
    assert task["status"] == "done"


def test_derive_ledgers_from_task_file_derives_live_task_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    close_live_task_to_idle(repo, commit_after_close=True)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-LIVE-001",
        "--title",
        "live task",
        "--stage",
        "live-stage",
        "--branch",
        "main",
        "--status",
        "doing",
        "--worker-state",
        "running",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created.returncode == 0, created.stdout + created.stderr

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "derive-ledgers",
        "--from",
        "task-file",
        "--task-id",
        "TASK-LIVE-001",
        "--write",
    )
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-LIVE-001")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-LIVE-001"
    assert current_task["status"] == "doing"
    assert entry["status"] == "active"


def test_derive_ledgers_from_task_file_rejects_other_live_current(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-LIVE-CONFLICT",
        "--title",
        "live conflict",
        "--stage",
        "live-stage",
        "--branch",
        "main",
        "--status",
        "doing",
        "--worker-state",
        "running",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created.returncode == 0, created.stdout + created.stderr

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "derive-ledgers",
        "--from",
        "task-file",
        "--task-id",
        "TASK-LIVE-CONFLICT",
        "--write",
    )

    assert result.returncode == 1
    assert "live current task already exists" in result.stdout
