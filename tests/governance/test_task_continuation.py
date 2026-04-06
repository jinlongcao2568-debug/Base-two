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


def _create_successor(
    repo: Path,
    task_id: str = "TASK-NEXT-001",
    *,
    successor_state: str | None = None,
) -> None:
    args = [
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
        "--planned-write-paths",
        "docs/governance/",
        "scripts/",
        "--planned-test-paths",
        "tests/governance/",
        "--allowed-dirs",
        "docs/governance/",
        "scripts/",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    ]
    if successor_state is not None:
        args.extend(["--successor-state", successor_state])
    created = run_python(TASK_OPS_SCRIPT, repo, *args)
    assert created.returncode == 0, created.stdout + created.stderr


def _mark_current_review_ready(repo: Path) -> None:
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
    git_commit_all(repo, "prepare review successor")


def _prepare_review_ready_parallel_parent(repo: Path, tmp_path: Path) -> None:
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    for task in (current_task, registry["tasks"][0]):
        task["size_class"] = "heavy"
        task["topology"] = "parallel_parent"
        task["automation_mode"] = "autonomous"
        task["lane_count"] = 1
        task["parallelism_plan_id"] = "plan-TASK-BASE-001-1"
        task["review_bundle_status"] = "not_applicable"
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    sync = run_python(TASK_OPS_SCRIPT, repo, "sync", "--write")
    assert sync.returncode == 0, sync.stdout + sync.stderr
    parent_report = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-report",
        "TASK-BASE-001",
        "--note",
        "parent coordination ready for closeout",
        "--tests",
        "pytest tests/base -q",
    )
    assert parent_report.returncode == 0, parent_report.stdout + parent_report.stderr
    create_child = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-001",
        "--title",
        "execution lane",
        "--stage",
        "parallel-stage",
        "--branch",
        "feat/TASK-EXEC-001",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--size-class",
        "standard",
        "--required-tests",
        "pytest tests/base -q",
        "--planned-write-paths",
        "src/exec1/",
    )
    assert create_child.returncode == 0, create_child.stdout + create_child.stderr
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-001"
    created = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", "TASK-EXEC-001", "--path", str(destination))
    assert created.returncode == 0, created.stdout + created.stderr
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-EXEC-001",
        "--summary",
        "execution ready",
        "--tests",
        "pytest tests/base -q",
    )
    assert finished.returncode == 0, finished.stdout + finished.stderr
    closed = run_python(TASK_OPS_SCRIPT, repo, "auto-close-children", "TASK-BASE-001")
    assert closed.returncode == 0, closed.stdout + closed.stderr
    git_commit_all(repo, "prepare parallel parent closeout")


def _enable_business_autopilot(repo: Path, *, include_downstream: bool = False) -> None:
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    for capability in capability_map["capabilities"]:
        if capability["capability_id"] in {"stage1_to_stage6_business_automation", "roadmap_autopilot_continuation"}:
            capability["status"] = "implemented"
        if include_downstream and capability["capability_id"] == "stage7_to_stage9_business_automation":
            capability["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("business_automation_enabled: false", "business_automation_enabled: true", 1)
    roadmap = roadmap.replace("  stage1: not_established", "  stage1: bootstrap_required", 1)
    roadmap = roadmap.replace("  stage2: not_established", "  stage2: bootstrap_required", 1)
    roadmap = roadmap.replace("  stage3: not_established", "  stage3: implementation_ready", 1)
    roadmap = roadmap.replace("  stage4: not_established", "  stage4: implementation_ready", 1)
    roadmap = roadmap.replace("  stage5: not_established", "  stage5: bootstrap_required", 1)
    roadmap = roadmap.replace("  stage6: not_established", "  stage6: implementation_ready", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")


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
    _prepare_review_ready_parallel_parent(repo, tmp_path)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-current")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == "TASK-BASE-001")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["status"] == "idle"
    assert current_task["current_task_id"] is None
    assert parent["status"] == "done"


def test_continue_roadmap_closes_review_task_and_activates_explicit_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

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
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _prepare_review_ready_parallel_parent(repo, tmp_path)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-BASE-001"]["status"] == "done"
    assert tasks["TASK-NEXT-001"]["status"] == "doing"


def test_continue_roadmap_activates_explicit_successor_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
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
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)
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
    _create_successor(repo)
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
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)
    (repo / "docs/governance/dirty.md").write_text("dirty\n", encoding="utf-8")
    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "dirty.md" in result.stdout


def test_continue_roadmap_rejects_review_without_test_evidence(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    set_live_task_review_without_evidence(repo, commit_after_update=True)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")

    assert result.returncode == 1
    assert "required tests missing from runlog" in result.stdout


def test_continue_roadmap_rejects_live_ledger_drift(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["branch"] = "feat/drifted-branch"
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    git_commit_all(repo, "introduce live ledger drift")

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")

    assert result.returncode == 1
    assert "live ledger drift detected" in result.stdout


def test_continue_roadmap_generates_task_auto_002_when_gap_is_open(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo, "TASK-AUTO-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    auto_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-AUTO-001")
    auto_task["status"] = "done"
    auto_task["worker_state"] = "completed"
    auto_task["activated_at"] = "2026-04-04T00:00:00+08:00"
    auto_task["closed_at"] = "2026-04-04T00:00:00+08:00"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    roadmap_text = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    autopilot = next(item for item in capability_map["capabilities"] if item["capability_id"] == "roadmap_autopilot_continuation")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-AUTO-002"
    assert tasks["TASK-AUTO-002"]["status"] == "doing"
    assert autopilot["status"] == "in_progress"
    assert "next_recommended_task_id: TASK-AUTO-002" in roadmap_text


def test_continue_roadmap_generates_task_auto_002_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo, "TASK-AUTO-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    auto_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-AUTO-001")
    auto_task["status"] = "done"
    auto_task["worker_state"] = "completed"
    auto_task["activated_at"] = "2026-04-04T00:00:00+08:00"
    auto_task["closed_at"] = "2026-04-04T00:00:00+08:00"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    close_live_task_to_idle(repo, commit_after_close=True)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-AUTO-002"
    assert tasks["TASK-AUTO-002"]["status"] == "doing"
    assert tasks["TASK-AUTO-002"]["depends_on_task_ids"] == []


def test_continue_roadmap_blocks_when_stale_dependency_pointer_leaves_no_unique_safe_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-BLOCKER-001",
            "title": "blocker",
            "status": "queued",
            "task_kind": "coordination",
            "execution_mode": "shared_coordination",
            "parent_task_id": None,
            "stage": "blocked-phase",
            "branch": "feat/TASK-BLOCKER-001",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "idle",
            "blocked_reason": None,
            "last_reported_at": "2026-04-04T00:00:00+08:00",
            "topology": "single_worker",
            "allowed_dirs": ["docs/governance/"],
            "reserved_paths": [],
            "planned_write_paths": ["docs/governance/"],
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
            "task_file": "docs/governance/tasks/TASK-BLOCKER-001.md",
            "runlog_file": "docs/governance/runlogs/TASK-BLOCKER-001-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "created_at": "2026-04-04T00:00:00+08:00",
            "activated_at": None,
            "closed_at": None,
        }
    )
    next_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-NEXT-001")
    next_task["depends_on_task_ids"] = ["TASK-BLOCKER-001"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "successor landscape is not unique" in result.stdout


def test_continue_roadmap_rejects_ambiguous_successor_landscape(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    _create_successor(repo, "TASK-ALT-001")
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "not unique" in result.stdout


def test_continue_roadmap_ignores_backlog_successor_in_uniqueness_check(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    _create_successor(repo, "TASK-ALT-001", successor_state="backlog")
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-ALT-001"]["status"] == "queued"
    assert tasks["TASK-ALT-001"]["successor_state"] == "backlog"


def test_continue_roadmap_rejects_boundary_unclear_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-NEXT-001",
        "--title",
        "next coordination task",
        "--stage",
        "next-phase",
        "--branch",
        "feat/TASK-NEXT-001",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "boundary is incomplete" in result.stdout


def test_continue_roadmap_generates_business_parent_and_child(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _enable_business_autopilot(repo)
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    parent = tasks[current_task["current_task_id"]]
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert parent["topology"] == "parallel_parent"
    assert parent["automation_mode"] == "autonomous"
    assert parent["lane_count"] == 1
    assert parent["parallelism_plan_id"] == f"plan-{parent['task_id']}-1"
    assert len(children) == 1
    assert children[0]["module_id"] == "stage1_orchestration"
    assert children[0]["lane_count"] == 1
    assert children[0]["lane_index"] == 1
    assert children[0]["parallelism_plan_id"] == f"plan-{parent['task_id']}-1"
    assert children[0]["authority_inputs"]
    assert children[0]["contract_inputs"]
    assert children[0]["review_policy"]
    assert "python scripts/check_repo.py" in children[0]["required_tests"]
    assert "python scripts/check_hygiene.py" in children[0]["required_tests"]
    assert "python scripts/validate_contracts.py" in children[0]["required_tests"]


def test_continue_roadmap_respects_bootstrap_priority_before_implementation(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _enable_business_autopilot(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("  stage1: bootstrap_required", "  stage1: implemented", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"].startswith("TASK-AUTO-"))
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert [child["module_id"] for child in children] == ["stage2_ingestion"]
    assert parent["lane_count"] == 1
    assert children[0]["lane_index"] == 1


def test_continue_roadmap_blocks_stage7_successor_until_downstream_capability_is_implemented(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _enable_business_autopilot(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    for stage_id in ("stage1", "stage2", "stage3", "stage4", "stage5", "stage6"):
        roadmap = roadmap.replace(f"  {stage_id}: bootstrap_required", f"  {stage_id}: implemented")
        roadmap = roadmap.replace(f"  {stage_id}: implementation_ready", f"  {stage_id}: implemented")
    roadmap = roadmap.replace("  stage7: not_established", "  stage7: bootstrap_required", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "no successor" in result.stdout


def test_continue_roadmap_generates_stage7_successor_when_downstream_capability_is_implemented(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _enable_business_autopilot(repo, include_downstream=True)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    for stage_id in ("stage1", "stage2", "stage3", "stage4", "stage5", "stage6"):
        roadmap = roadmap.replace(f"  {stage_id}: bootstrap_required", f"  {stage_id}: implemented")
        roadmap = roadmap.replace(f"  {stage_id}: implementation_ready", f"  {stage_id}: implemented")
    roadmap = roadmap.replace("  stage7: not_established", "  stage7: bootstrap_required", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == current_task["current_task_id"])
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert parent["topology"] == "parallel_parent"
    assert [child["module_id"] for child in children] == ["stage7_sales"]


def test_continue_roadmap_caps_business_children_at_four(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _enable_business_autopilot(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    for stage_id in ("stage3", "stage4", "stage5", "stage6"):
        roadmap = roadmap.replace(f"  {stage_id}: implementation_ready", f"  {stage_id}: bootstrap_required", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    module_map = read_yaml(repo / "docs/governance/MODULE_MAP.yaml")
    for module in module_map["modules"]:
        if module["owner_stage"] in {"stage2", "stage3", "stage4", "stage5", "stage6"}:
            module["depends_on"] = []
    write_yaml(repo / "docs/governance/MODULE_MAP.yaml", module_map)
    _mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"].startswith("TASK-AUTO-"))
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert len(children) == 4
    assert parent["lane_count"] == 4
    assert parent["parallelism_plan_id"] == f"plan-{parent['task_id']}-4"
    assert [child["lane_index"] for child in children] == [1, 2, 3, 4]
    assert all(child["lane_count"] == 4 for child in children)
    assert all(child["parallelism_plan_id"] == f"plan-{parent['task_id']}-4" for child in children)
