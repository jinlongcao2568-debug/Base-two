from __future__ import annotations

from pathlib import Path

import pytest

from .helpers import (
    CHECK_REPO_SCRIPT,
    TASK_OPS_SCRIPT,
    git_commit_all,
    init_governance_repo,
    read_roadmap,
    read_yaml,
    run_python,
    set_idle_control_plane,
    write_roadmap,
    write_yaml,
)
from .scenario_builders import (
    append_registry_task,
    append_worktree_entry,
    execution_task_record,
    execution_worktree_entry,
    write_execution_context,
)


def test_check_repo_passes_on_clean_repo(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_repo_fails_when_governance_file_missing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "docs/governance/CURRENT_TASK.yaml").unlink()
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1


def test_check_repo_fails_on_branch_mismatch(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["branch"] = "feat/wrong-branch"
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "branch" in result.stdout


def test_check_repo_fails_on_modified_path_outside_allowed_dirs(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "oops.txt").write_text("x", encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "outside allowed_dirs" in result.stdout


def test_check_repo_fails_on_modified_path_outside_planned_write_paths(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["allowed_dirs"] = ["docs/governance/"]
    current_task["planned_write_paths"] = ["docs/governance/CURRENT_TASK.yaml"]
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["allowed_dirs"] = ["docs/governance/"]
    registry["tasks"][0]["planned_write_paths"] = ["docs/governance/CURRENT_TASK.yaml"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    (repo / "docs/governance/unplanned.md").write_text("x", encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "outside planned_write_paths" in result.stdout


def test_check_repo_fails_when_current_task_is_done(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["status"] = "done"
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["status"] = "done"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "cannot remain on a done task" in result.stdout


def test_check_repo_passes_when_current_state_is_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle current state")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("branch", "main", "idle current task field must be null: branch"),
        ("task_file", "docs/governance/tasks/TASK-BASE-001.md", "idle current task field must be null: task_file"),
        ("allowed_dirs", ["docs/governance/"], "idle current task field must be empty: allowed_dirs"),
    ],
)
def test_check_repo_rejects_invalid_idle_payload_fields(
    tmp_path: Path,
    field: str,
    value: object,
    expected: str,
) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task[field] = value
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert expected in result.stdout


def test_check_repo_rejects_idle_roadmap_drift(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    roadmap_path = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    frontmatter, body = read_roadmap(roadmap_path)
    frontmatter["current_task_id"] = "TASK-BASE-001"
    write_roadmap(roadmap_path, frontmatter, body)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "roadmap current_task_id mismatch for idle current state" in result.stdout


def test_check_repo_rejects_active_coordination_worktree_during_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    worktrees["entries"][0]["status"] = "active"
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "idle current state cannot keep active coordination worktrees" in result.stdout


def test_check_repo_fails_when_roadmap_current_task_drifts(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(
        "---\n"
        "current_phase: wrong-phase\n"
        "current_task_id: TASK-WRONG-001\n"
        "next_recommended_task_id: null\n"
        "advance_mode: explicit_or_generated\n"
        "auto_create_missing_task: true\n"
        "branch_switch_policy: create_or_switch_if_clean\n"
        "priority_order:\n"
        "  - governance_automation\n"
        "  - authority_chain\n"
        "  - business_automation\n"
        "business_automation_enabled: false\n"
        "stage_establishment:\n"
        "  stage1: not_established\n"
        "  stage2: not_established\n"
        "  stage3: not_established\n"
        "  stage4: not_established\n"
        "  stage5: not_established\n"
        "  stage6: not_established\n"
        "  stage7: not_established\n"
        "  stage8: not_established\n"
        "  stage9: not_established\n"
        "automation_foundation: not_established\n"
        "---\n\n# Roadmap\n",
        encoding="utf-8",
    )
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "roadmap current_task_id mismatch" in result.stdout


def test_check_repo_fails_when_roadmap_policy_is_invalid(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("advance_mode: explicit_or_generated", "advance_mode: invalid_mode", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "advance_mode" in result.stdout


def test_check_repo_fails_when_next_recommended_task_is_missing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-MISSING-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "next_recommended_task_id" in result.stdout


def test_check_repo_fails_when_business_policy_is_invalid(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("business_automation_enabled: false", "business_automation_enabled: true", 1)
    roadmap = roadmap.replace(
        "business_automation_scope: stage1_to_stage6",
        "business_automation_scope: stage1_to_stage9",
        1,
    )
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "business_automation_scope" in result.stdout


def test_check_repo_fails_when_task_file_status_drifts(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_file = repo / "docs/governance/tasks/TASK-BASE-001.md"
    task_file.write_text(
        task_file.read_text(encoding="utf-8").replace("- `status`: `doing`", "- `status`: `review`", 1),
        encoding="utf-8",
    )
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "task file mismatch for field status" in result.stdout


def test_check_repo_allows_review_state_with_in_scope_candidate_changes(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
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
    assert finish.returncode == 0, finish.stdout + finish.stderr
    (repo / "src/base/review_candidate.py").write_text("candidate = True\n", encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_repo_fails_when_task_narrative_assertions_missing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_file = repo / "docs/governance/tasks/TASK-BASE-001.md"
    task_file.write_text(
        task_file.read_text(encoding="utf-8").replace(
            "## Narrative Assertions\n\n"
            "- `narrative_status`: `doing`\n"
            "- `closeout_state`: `not_ready`\n"
            "- `blocking_state`: `clear`\n"
            "- `completed_scope`: `active_progress`\n"
            "- `remaining_scope`: `active_work_remaining`\n"
            "- `next_gate`: `validation_pending`\n\n",
            "",
            1,
        ),
        encoding="utf-8",
    )
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "missing section: ## Narrative Assertions" in result.stdout


def test_check_repo_fails_when_runlog_narrative_assertions_drift(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    runlog = repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md"
    runlog.write_text(
        runlog.read_text(encoding="utf-8").replace(
            "- `next_gate`: `validation_pending`",
            "- `next_gate`: `closeout_decision`",
            1,
        ),
        encoding="utf-8",
    )
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "runlog narrative assertions mismatch for field next_gate" in result.stdout


def test_check_repo_fails_when_execution_touches_reserved_path(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    append_registry_task(
        repo,
        execution_task_record(
            "TASK-EXEC-001",
            branch="main",
            allowed_dirs=["src/execution/"],
            planned_write_paths=["src/execution/"],
            planned_test_paths=["tests/execution/"],
            size_class="micro",
            topology="single_task",
        ),
        task_text="# TASK-EXEC-001\n",
        runlog_text="# RUNLOG\n",
    )
    write_execution_context(
        repo,
        "TASK-EXEC-001",
        branch="main",
        allowed_dirs=["src/execution/"],
        planned_write_paths=["src/execution/"],
        planned_test_paths=["tests/execution/"],
    )
    (repo / "docs/governance/hack.md").write_text("x", encoding="utf-8")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "outside allowed_dirs" in result.stdout or "reserved path" in result.stdout


def test_check_repo_fails_when_active_execution_limit_exceeded(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    for index in range(3):
        task_id = f"TASK-EXEC-00{index + 1}"
        append_registry_task(
            repo,
            execution_task_record(
                task_id,
                branch=f"feat/{task_id}",
                allowed_dirs=[f"src/exec{index}/"],
                planned_write_paths=[f"src/exec{index}/"],
                planned_test_paths=[f"tests/exec{index}/"],
            ),
        )
        append_worktree_entry(
            repo,
            execution_worktree_entry(
                task_id,
                branch=f"feat/{task_id}",
                path=f"D:/tmp/{task_id}",
                worker_owner="worker-a" if index % 2 == 0 else "worker-b",
            ),
        )
    git_commit_all(repo, "add execution entries")
    result = run_python(CHECK_REPO_SCRIPT, repo)
    assert result.returncode == 1
    assert "hard limit of 2" in result.stdout
