from __future__ import annotations

import pytest
pytestmark = pytest.mark.slow

from pathlib import Path

from .helpers import (
    TASK_OPS_SCRIPT,
    git_commit_all,
    init_governance_repo,
    read_yaml,
    run_python,
    set_idle_control_plane,
    write_yaml,
)


def _candidate(repo: Path, candidate_id: str) -> dict:
    return read_yaml(repo / f".codex/local/coordination_candidates/{candidate_id}.yaml")


def _write_generated_candidate(repo: Path, candidate_id: str, task_id: str, *, branch: str) -> None:
    candidate_dir = repo / ".codex/local/coordination_candidates"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    write_yaml(
        candidate_dir / f"{candidate_id}.yaml",
        {
            "candidate_id": candidate_id,
            "source_kind": "generated_blueprint",
            "promotion_mode": "create_new_task",
            "priority_rank": 1,
            "reason": "test candidate",
            "serial_or_parallel": "serial",
            "parent_candidate": None,
            "child_candidates": [],
            "task_id": task_id,
            "title": "generated coordination task",
            "stage": "coordination-stage",
            "task_kind": "coordination",
            "execution_mode": "shared_coordination",
            "size_class": "standard",
            "automation_mode": "manual",
            "topology": "single_worker",
            "allowed_dirs": ["docs/governance/", "scripts/"],
            "planned_write_paths": ["docs/governance/", "scripts/"],
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
            "depends_on_task_ids": [],
            "candidate_branch": branch,
        },
    )


def _mark_task_absorbed(repo: Path, task_id: str, *, absorbed_by: str = "TASK-GOV-018") -> None:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == task_id)
    task["absorbed_by"] = absorbed_by
    task["absorbed_phase"] = "phase-test"
    task["absorbed_reason"] = "absorbed regression fixture"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)


def test_plan_coordination_ranks_roadmap_preferred_candidate_first(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle state")

    created_first = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-PLAN-001",
        "--title",
        "first candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-PLAN-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    created_second = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-PLAN-002",
        "--title",
        "second candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-PLAN-002",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created_first.returncode == 0, created_first.stdout + created_first.stderr
    assert created_second.returncode == 0, created_second.stdout + created_second.stderr

    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-PLAN-002", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")

    planned = run_python(TASK_OPS_SCRIPT, repo, "plan-coordination")
    index = read_yaml(repo / ".codex/local/coordination_candidates/index.yaml")
    top_candidate = _candidate(repo, index["candidate_ids"][0])

    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert top_candidate["task_id"] == "TASK-PLAN-002"
    assert top_candidate["priority_rank"] == 1


def test_plan_coordination_distinguishes_parallel_and_serial_candidates(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle state")

    created_parallel = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-PAR-001",
        "--title",
        "parallel candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-PAR-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--size-class",
        "heavy",
        "--allowed-dirs",
        "docs/base/",
        "scripts/",
        "--planned-write-paths",
        "docs/base/",
        "scripts/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    created_serial = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-SER-001",
        "--title",
        "serial candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-SER-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--size-class",
        "heavy",
        "--allowed-dirs",
        "docs/governance/",
        "scripts/",
        "--planned-write-paths",
        "docs/governance/",
        "scripts/",
        "--reserved-paths",
        "scripts/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert created_parallel.returncode == 0, created_parallel.stdout + created_parallel.stderr
    assert created_serial.returncode == 0, created_serial.stdout + created_serial.stderr

    run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-PAR-001")
    run_python(TASK_OPS_SCRIPT, repo, "decide-topology", "TASK-SER-001")
    planned = run_python(TASK_OPS_SCRIPT, repo, "plan-coordination")

    parallel_candidate = _candidate(repo, "candidate-task-par-001")
    serial_candidate = _candidate(repo, "candidate-task-ser-001")

    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert parallel_candidate["serial_or_parallel"] == "parallel"
    assert serial_candidate["serial_or_parallel"] == "serial"
    assert parallel_candidate["allowed_dirs"]
    assert parallel_candidate["planned_write_paths"]
    assert parallel_candidate["planned_test_paths"]
    assert parallel_candidate["required_tests"]


def test_promote_candidate_creates_formal_task_without_activation(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle state")
    _write_generated_candidate(repo, "candidate-manual-001", "TASK-MANUAL-001", branch="main")

    promoted = run_python(TASK_OPS_SCRIPT, repo, "promote-candidate", "candidate-manual-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")

    assert promoted.returncode == 0, promoted.stdout + promoted.stderr
    assert any(task["task_id"] == "TASK-MANUAL-001" for task in registry["tasks"])
    assert current_task["current_task_id"] is None
    assert (repo / "docs/governance/tasks/TASK-MANUAL-001.md").exists()
    assert (repo / "docs/governance/runlogs/TASK-MANUAL-001-RUNLOG.md").exists()


def test_promote_candidate_activate_updates_current_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle state")
    _write_generated_candidate(repo, "candidate-manual-002", "TASK-MANUAL-002", branch="main")

    promoted = run_python(TASK_OPS_SCRIPT, repo, "promote-candidate", "candidate-manual-002", "--activate")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")

    assert promoted.returncode == 0, promoted.stdout + promoted.stderr
    assert current_task["current_task_id"] == "TASK-MANUAL-002"
    assert current_task["status"] == "doing"


def test_plan_coordination_skips_incomplete_boundary_candidates(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle state")

    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-INCOMPLETE-001",
        "--title",
        "incomplete candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-INCOMPLETE-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
    )
    assert created.returncode == 0, created.stdout + created.stderr

    planned = run_python(TASK_OPS_SCRIPT, repo, "plan-coordination")
    index = read_yaml(repo / ".codex/local/coordination_candidates/index.yaml")

    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert "candidate-task-incomplete-001" not in index["candidate_ids"]


def test_plan_coordination_skips_absorbed_candidates_even_when_roadmap_points_to_them(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle state")

    absorbed = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-ABSORBED-001",
        "--title",
        "absorbed candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-ABSORBED-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    keep = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-KEEP-001",
        "--title",
        "keep candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-KEEP-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert absorbed.returncode == 0, absorbed.stdout + absorbed.stderr
    assert keep.returncode == 0, keep.stdout + keep.stderr

    _mark_task_absorbed(repo, "TASK-ABSORBED-001")
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-ABSORBED-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")

    planned = run_python(TASK_OPS_SCRIPT, repo, "plan-coordination")
    index = read_yaml(repo / ".codex/local/coordination_candidates/index.yaml")

    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert "candidate-task-keep-001" in index["candidate_ids"]
    assert "candidate-task-absorbed-001" not in index["candidate_ids"]
    assert not (repo / ".codex/local/coordination_candidates/candidate-task-absorbed-001.yaml").exists()


def test_plan_coordination_excludes_absorbed_backlog_candidates(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "set idle state")

    live_created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-LIVE-001",
        "--title",
        "live candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-LIVE-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    absorbed_created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-ABSORBED-001",
        "--title",
        "absorbed candidate",
        "--stage",
        "coord-stage",
        "--branch",
        "feat/TASK-ABSORBED-001",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        "python scripts/check_repo.py",
    )
    assert live_created.returncode == 0, live_created.stdout + live_created.stderr
    assert absorbed_created.returncode == 0, absorbed_created.stdout + absorbed_created.stderr

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    absorbed = next(task for task in registry["tasks"] if task["task_id"] == "TASK-ABSORBED-001")
    absorbed["absorbed_by"] = "TASK-GOV-018"
    absorbed["successor_state"] = "backlog"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    planned = run_python(TASK_OPS_SCRIPT, repo, "plan-coordination")
    index = read_yaml(repo / ".codex/local/coordination_candidates/index.yaml")

    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert "candidate-task-live-001" in index["candidate_ids"]
    assert "candidate-task-absorbed-001" not in index["candidate_ids"]
    assert not (repo / ".codex/local/coordination_candidates/candidate-task-absorbed-001.yaml").exists()
