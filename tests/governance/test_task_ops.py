from __future__ import annotations

from pathlib import Path

from .helpers import CHECK_REPO_SCRIPT, TASK_OPS_SCRIPT, git_commit_all, init_governance_repo, read_yaml, run_python, write_yaml


def test_pause_moves_active_task_to_paused(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(TASK_OPS_SCRIPT, repo, "pause")
    assert result.returncode == 0, result.stdout + result.stderr
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    assert current_task["status"] == "paused"
    assert registry["tasks"][0]["status"] == "paused"
    assert worktrees["entries"][0]["status"] == "paused"


def test_can_start_succeeds_for_live_current_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(TASK_OPS_SCRIPT, repo, "can-start")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "can-start TASK-BASE-001" in result.stdout


def test_can_close_requires_required_tests_in_runlog(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").write_text(
        "# TASK-BASE-001 RUNLOG\n",
        encoding="utf-8",
    )
    result = run_python(TASK_OPS_SCRIPT, repo, "can-close")
    assert result.returncode == 1
    assert "required tests missing from runlog" in result.stdout


def test_new_task_templates_include_narrative_assertions(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-COORD-002",
        "--title",
        "coordination task",
        "--stage",
        "coord-stage",
        "--planned-write-paths",
        "docs/governance/",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    task_file = (repo / "docs/governance/tasks/TASK-COORD-002.md").read_text(encoding="utf-8")
    runlog = (repo / "docs/governance/runlogs/TASK-COORD-002-RUNLOG.md").read_text(encoding="utf-8")
    assert "## Narrative Assertions" in task_file
    assert "## Narrative Assertions" in runlog
    assert "- `narrative_status`: `queued`" in task_file
    assert "- `next_gate`: `activation_pending`" in runlog


def test_activate_rejects_execution_task_in_main_worktree(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-001",
        "--title",
        "execution task",
        "--stage",
        "exec-stage",
        "--branch",
        "main",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--allowed-dirs",
        "src/exec/",
        "--planned-write-paths",
        "src/exec/",
        "--planned-test-paths",
        "tests/exec/",
    )
    assert create.returncode == 0, create.stdout + create.stderr
    activate = run_python(TASK_OPS_SCRIPT, repo, "activate", "TASK-EXEC-001")
    assert activate.returncode == 1
    assert "only coordination tasks" in activate.stdout


def test_split_check_detects_overlap_and_reserved_conflict(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    first = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-001",
        "--title",
        "execution one",
        "--stage",
        "pilot",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--planned-write-paths",
        "src/shared/",
        "docs/governance/CURRENT_TASK.yaml",
        "--planned-test-paths",
        "tests/shared/",
    )
    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-002",
        "--title",
        "execution two",
        "--stage",
        "pilot",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--planned-write-paths",
        "src/shared/utils/",
        "--planned-test-paths",
        "tests/shared/",
    )
    assert first.returncode == 0
    assert second.returncode == 0
    result = run_python(TASK_OPS_SCRIPT, repo, "split-check", "TASK-BASE-001")
    assert result.returncode == 1
    assert "reserved path" in result.stdout
    assert "overlaps" in result.stdout


def test_decide_topology_respects_size_class(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    micro = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-MICRO-001",
        "--title",
        "micro task",
        "--stage",
        "micro-stage",
        "--size-class",
        "micro",
        "--planned-write-paths",
        "src/base/",
    )
    heavy = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-HEAVY-001",
        "--title",
        "heavy task",
        "--stage",
        "heavy-stage",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "src/base/",
        "tests/base/",
    )
    assert micro.returncode == 0
    assert heavy.returncode == 0
    result_micro = run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-MICRO-001")
    result_heavy = run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-HEAVY-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    assert result_micro.returncode == 0
    assert result_heavy.returncode == 0
    assert tasks["TASK-MICRO-001"]["topology"] == "single_task"
    assert tasks["TASK-HEAVY-001"]["topology"] == "parallel_parent"


def test_decide_topology_requires_reserved_paths_field_for_heavy(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-HEAVY-002",
        "--title",
        "heavy task without reserved paths field",
        "--stage",
        "heavy-stage",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "src/base/",
        "tests/base/",
    )
    assert create.returncode == 0
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-HEAVY-002")
    task.pop("reserved_paths", None)
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    result = run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-HEAVY-002")
    assert result.returncode == 0
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-HEAVY-002")
    assert task["topology"] == "single_worker"


def test_worker_state_transitions(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    start = run_python(TASK_OPS_SCRIPT, repo, "worker-start", "TASK-BASE-001", "--worker-owner", "coordinator")
    report = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-report",
        "TASK-BASE-001",
        "--note",
        "first progress",
        "--tests",
        "pytest tests/base -q",
    )
    finish = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-BASE-001",
        "--summary",
        "candidate ready",
        "--tests",
        "pytest tests/base -q",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = registry["tasks"][0]
    git_commit_all(repo, "worker-finish sync")
    repo_gate = run_python(CHECK_REPO_SCRIPT, repo)
    assert start.returncode == 0
    assert report.returncode == 0
    assert finish.returncode == 0
    assert repo_gate.returncode == 0, repo_gate.stdout + repo_gate.stderr
    assert task["status"] == "review"
    assert task["worker_state"] == "review_pending"


def test_auto_close_children_closes_review_tasks(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-001"
    create_parent = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-PARENT-001",
        "--title",
        "parent task",
        "--stage",
        "parallel-stage",
        "--branch",
        "main",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "src/base/",
        "tests/base/",
    )
    create_child = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-001",
        "--title",
        "execution task",
        "--stage",
        "parallel-stage",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-PARENT-001",
        "--required-tests",
        "pytest tests/base -q",
        "--planned-write-paths",
        "src/exec1/",
    )
    assert create_parent.returncode == 0
    assert create_child.returncode == 0
    create_worktree = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worktree-create",
        "TASK-EXEC-001",
        "--path",
        str(destination),
    )
    assert create_worktree.returncode == 0, create_worktree.stdout + create_worktree.stderr
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-EXEC-001",
        "--summary",
        "done",
        "--tests",
        "pytest tests/base -q",
    )
    assert finished.returncode == 0
    close = run_python(TASK_OPS_SCRIPT, repo, "auto-close-children", "TASK-PARENT-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-001")
    assert close.returncode == 0
    assert child["status"] == "done"


def test_split_check_detects_task_reserved_path_conflict(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    first = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-R1",
        "--title",
        "execution one",
        "--stage",
        "pilot",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--planned-write-paths",
        "src/exec1/",
        "--reserved-paths",
        "src/shared_lock/",
    )
    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-R2",
        "--title",
        "execution two",
        "--stage",
        "pilot",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--planned-write-paths",
        "src/shared_lock/",
    )
    assert first.returncode == 0
    assert second.returncode == 0
    result = run_python(TASK_OPS_SCRIPT, repo, "split-check", "TASK-BASE-001")
    assert result.returncode == 1
    assert "reserved path" in result.stdout


def test_worktree_create_and_release_round_trip(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_task = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-001",
        "--title",
        "execution task",
        "--stage",
        "pilot",
        "--branch",
        "feat/TASK-EXEC-001",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--planned-write-paths",
        "src/execution/",
        "--planned-test-paths",
        "tests/execution/",
    )
    assert create_task.returncode == 0, create_task.stdout + create_task.stderr
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-001"
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worktree-create",
        "TASK-EXEC-001",
        "--path",
        str(destination),
    )
    assert created.returncode == 0, created.stdout + created.stderr
    assert (destination / ".codex/local/EXECUTION_CONTEXT.yaml").exists()
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-001")
    assert entry["status"] == "active"
    released = run_python(TASK_OPS_SCRIPT, repo, "worktree-release", "TASK-EXEC-001")
    assert released.returncode == 0, released.stdout + released.stderr
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-001")
    assert entry["status"] == "closed"
    assert entry["cleanup_state"] == "done"
    assert not destination.exists()


def test_cleanup_orphans_marks_blocked_when_remove_fails(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    blocked_dir = tmp_path / "blocked.worktree"
    blocked_dir.mkdir()
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-EXEC-009",
            "title": "closed child",
            "status": "done",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": "TASK-BASE-001",
            "stage": "pilot",
            "branch": "feat/TASK-EXEC-009",
            "size_class": "standard",
            "automation_mode": "autonomous",
            "worker_state": "completed",
            "blocked_reason": None,
            "last_reported_at": "2026-04-04T00:00:00+08:00",
            "topology": "single_worker",
            "allowed_dirs": ["src/exec9/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/exec9/"],
            "planned_test_paths": [],
            "required_tests": [],
            "task_file": "docs/governance/tasks/TASK-EXEC-009.md",
            "runlog_file": "docs/governance/runlogs/TASK-EXEC-009-RUNLOG.md",
            "created_at": "2026-04-04T00:00:00+08:00",
            "activated_at": "2026-04-04T00:00:00+08:00",
            "closed_at": "2026-04-04T00:00:00+08:00",
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    (repo / "docs/governance/tasks/TASK-EXEC-009.md").write_text("# task\n", encoding="utf-8")
    (repo / "docs/governance/runlogs/TASK-EXEC-009-RUNLOG.md").write_text("# runlog\n", encoding="utf-8")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    worktrees["entries"].append(
        {
            "task_id": "TASK-EXEC-009",
            "work_mode": "execution",
            "parent_task_id": "TASK-BASE-001",
            "branch": "feat/TASK-EXEC-009",
            "path": str(blocked_dir).replace("\\", "/"),
            "status": "closed",
            "cleanup_state": "pending",
            "cleanup_attempts": 0,
            "last_cleanup_error": None,
            "worker_owner": "worker-a",
        }
    )
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    result = run_python(TASK_OPS_SCRIPT, repo, "cleanup-orphans")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-009")
    assert result.returncode == 1
    assert entry["cleanup_state"] == "blocked"
    assert entry["cleanup_attempts"] == 1
