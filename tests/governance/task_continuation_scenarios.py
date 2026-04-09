from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, git_commit_all, read_yaml, run_python_inline as run_python, write_yaml


def create_successor(
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


def mark_current_review_ready(repo: Path) -> None:
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


def prepare_review_ready_parallel_parent(repo: Path, tmp_path: Path) -> None:
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


def enable_business_autopilot(repo: Path, *, include_downstream: bool = False) -> None:
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


def set_business_scope(repo: Path, scope: str) -> None:
    roadmap_path = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    roadmap = roadmap_path.read_text(encoding="utf-8")
    for current in ("stage1_to_stage9", "stage1_to_stage6", "stage2_to_stage6"):
        roadmap = roadmap.replace(f"business_automation_scope: {current}", f"business_automation_scope: {scope}")
    roadmap_path.write_text(roadmap, encoding="utf-8")
