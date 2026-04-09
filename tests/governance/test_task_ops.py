from __future__ import annotations

from pathlib import Path

from .helpers import (
    CHECK_REPO_SCRIPT,
    TASK_OPS_SCRIPT,
    close_live_task_to_idle,
    git_commit_all,
    init_governance_repo,
    read_roadmap,
    read_yaml,
    run_python_inline as run_python,
    write_yaml,
)
from .scenario_builders import create_review_ready_child


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


def test_close_moves_live_coordination_task_to_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    close_live_task_to_idle(repo)

    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    roadmap_frontmatter, roadmap_body = read_roadmap(repo / "docs/governance/DEVELOPMENT_ROADMAP.md")

    assert current_task["status"] == "idle"
    assert current_task["current_task_id"] is None
    assert current_task["stage"] is None
    assert current_task["branch"] is None
    assert current_task["task_file"] is None
    assert current_task["runlog_file"] is None
    assert current_task["allowed_dirs"] == []
    assert current_task["planned_write_paths"] == []
    assert current_task["required_tests"] == []
    assert current_task["worker_state"] == "idle"
    assert roadmap_frontmatter["current_task_id"] is None
    assert roadmap_frontmatter["current_phase"] == "idle"
    assert "no live current task" in roadmap_body.lower()
    assert registry["tasks"][0]["status"] == "done"
    assert registry["tasks"][0]["worker_state"] == "completed"
    assert worktrees["entries"][0]["status"] == "closed"


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


def test_split_check_detects_single_writer_root_conflict(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    first = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-101",
        "--title",
        "stage7 execution one",
        "--stage",
        "stage7",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--allowed-dirs",
        "src/stage7_sales/",
        "tests/stage7/",
        "--planned-write-paths",
        "src/stage7_sales/",
        "--planned-test-paths",
        "tests/stage7/",
    )
    second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-102",
        "--title",
        "stage7 execution two",
        "--stage",
        "stage7",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--allowed-dirs",
        "src/stage7_sales/",
        "tests/stage7/",
        "--planned-write-paths",
        "src/stage7_sales/runtime.py",
        "--planned-test-paths",
        "tests/stage7/",
    )

    assert first.returncode == 0
    assert second.returncode == 0
    result = run_python(TASK_OPS_SCRIPT, repo, "split-check", "TASK-BASE-001")
    assert result.returncode == 1
    assert "single-writer root" in result.stdout
    assert "src/stage7_sales/" in result.stdout


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
        "scripts/",
        "--required-tests",
        "python scripts/check_repo.py",
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
    assert tasks["TASK-HEAVY-001"]["lane_count"] == 2
    assert tasks["TASK-HEAVY-001"]["parallelism_plan_id"] == "plan-TASK-HEAVY-001-2"


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
    assert task["lane_count"] == 1
    assert task["parallelism_plan_id"] is None


def test_decide_topology_scales_to_three_lanes(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-HEAVY-003",
        "--title",
        "heavy task with three roots",
        "--stage",
        "heavy-stage",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "src/base/",
        "scripts/",
        "docs/base/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    result = run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-HEAVY-003")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-HEAVY-003")
    assert result.returncode == 0, result.stdout + result.stderr
    assert task["topology"] == "parallel_parent"
    assert task["lane_count"] == 3
    assert task["parallelism_plan_id"] == "plan-TASK-HEAVY-003-3"


def test_decide_topology_caps_at_four_lanes(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-HEAVY-004",
        "--title",
        "heavy task with five roots",
        "--stage",
        "heavy-stage",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "src/base/",
        "scripts/",
        "docs/base/",
        "tools/",
        "configs/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    result = run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-HEAVY-004")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-HEAVY-004")
    assert result.returncode == 0, result.stdout + result.stderr
    assert task["topology"] == "parallel_parent"
    assert task["lane_count"] == 4
    assert task["parallelism_plan_id"] == "plan-TASK-HEAVY-004-4"


def test_decide_topology_downgrades_when_required_tests_missing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-HEAVY-005",
        "--title",
        "heavy task without tests",
        "--stage",
        "heavy-stage",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "src/base/",
        "scripts/",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-HEAVY-005")
    task["required_tests"] = []
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    result = run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-HEAVY-005")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-HEAVY-005")
    assert result.returncode == 0, result.stdout + result.stderr
    assert task["topology"] == "single_worker"
    assert task["lane_count"] == 1
    assert task["parallelism_plan_id"] is None


def test_decide_topology_downgrades_when_reserved_path_hit(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-HEAVY-006",
        "--title",
        "heavy task on reserved path",
        "--stage",
        "heavy-stage",
        "--size-class",
        "heavy",
        "--planned-write-paths",
        "scripts/",
        "docs/base/",
        "--reserved-paths",
        "scripts/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    result = run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-HEAVY-006")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-HEAVY-006")
    assert result.returncode == 0, result.stdout + result.stderr
    assert task["topology"] == "single_worker"
    assert task["lane_count"] == 1
    assert task["parallelism_plan_id"] is None


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


def test_worktree_create_caps_active_execution_entries_at_four(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_ids = [f"TASK-EXEC-00{index}" for index in range(1, 6)]
    for index, task_id in enumerate(task_ids, start=1):
        create_task = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "new",
            task_id,
            "--title",
            f"execution task {index}",
            "--stage",
            "pilot",
            "--branch",
            f"feat/{task_id}",
            "--task-kind",
            "execution",
            "--execution-mode",
            "isolated_worktree",
            "--planned-write-paths",
            f"src/execution{index}/",
            "--planned-test-paths",
            f"tests/execution{index}/",
        )
        assert create_task.returncode == 0, create_task.stdout + create_task.stderr
    for task_id in task_ids[:4]:
        destination = tmp_path / "repo.worktrees" / task_id
        created = run_python(
            TASK_OPS_SCRIPT,
            repo,
            "worktree-create",
            task_id,
            "--path",
            str(destination),
        )
        assert created.returncode == 0, created.stdout + created.stderr
    rejected = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worktree-create",
        task_ids[4],
        "--path",
        str(tmp_path / "repo.worktrees" / task_ids[4]),
    )
    assert rejected.returncode == 1
    assert "already at hard limit 4" in rejected.stdout
