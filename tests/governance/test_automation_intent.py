from __future__ import annotations

import json
from pathlib import Path

import pytest

from .helpers import (
    AUTOMATION_INTENT_SCRIPT,
    TASK_OPS_SCRIPT,
    close_live_task_to_idle,
    git_commit_all,
    init_governance_repo,
    read_yaml,
    run_python,
    set_idle_control_plane,
    write_yaml,
)


def _preflight(repo: Path, utterance: str) -> tuple[int, dict]:
    result = run_python(AUTOMATION_INTENT_SCRIPT, repo, "preflight", "--utterance", utterance)
    return result.returncode, json.loads(result.stdout)


def _create_successor(repo: Path, task_id: str = "TASK-NEXT-001", *, with_boundaries: bool = True) -> None:
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
    ]
    if with_boundaries:
        args.extend(
            [
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
            ]
        )
    created = run_python(TASK_OPS_SCRIPT, repo, *args)
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
    git_commit_all(repo, "prepare review successor")


@pytest.mark.parametrize(
    ("utterance", "intent_id"),
    [
        ("继续当前任务", "continue-current"),
        ("按路线图继续推进", "continue-roadmap"),
        ("继续按照路线图开发", "continue-roadmap"),
    ],
)
def test_preflight_supports_governed_phrases(tmp_path: Path, utterance: str, intent_id: str) -> None:
    repo = init_governance_repo(tmp_path)
    if intent_id == "continue-roadmap":
        _create_successor(repo)
        roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
        roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
        (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
        _mark_review_ready(repo)

    code, payload = _preflight(repo, utterance)
    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == intent_id


def test_preflight_maps_generic_continue_to_current_when_live_task_is_active(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    code, payload = _preflight(repo, "继续开发")
    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "continue-current"
    assert payload["matched_phrase"] == "generic_active_continue"


def test_preflight_blocks_continue_current_when_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    code, payload = _preflight(repo, "继续当前任务")
    assert code == 0
    assert payload["status"] == "blocked"
    assert payload["intent_id"] == "continue-current"
    assert any("idle" in blocker for blocker in payload["blockers"])


def test_preflight_returns_unsupported_for_generic_continue_when_task_switch_risk_exists(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    close_live_task_to_idle(repo, commit_after_close=True)
    code, payload = _preflight(repo, "继续开发")
    assert code == 0
    assert payload["status"] == "unsupported"
    assert payload["intent_id"] is None


def test_preflight_blocks_dirty_worktree_and_preserves_readable_chinese_path(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "说明文档.md").write_text("dirty\n", encoding="utf-8")
    code, payload = _preflight(repo, "继续当前任务")
    assert code == 0
    assert payload["status"] == "blocked"
    assert any("说明文档.md" in blocker for blocker in payload["blockers"])


def test_preflight_routes_free_form_roadmap_request(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "按计划继续往下一步推进")
    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "continue-roadmap"


def test_preflight_continue_roadmap_blocks_when_successor_is_missing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    for capability in capability_map["capabilities"]:
        if capability["capability_id"] == "roadmap_autopilot_continuation":
            capability["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "按路线图继续推进")
    assert code == 0
    assert payload["status"] == "blocked"
    assert any("no successor" in blocker for blocker in payload["blockers"])


def test_preflight_continue_roadmap_blocks_unmet_dependency(tmp_path: Path) -> None:
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
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "按路线图继续推进")
    assert code == 0
    assert payload["status"] == "blocked"
    assert any("dependency not satisfied" in blocker for blocker in payload["blockers"])


def test_preflight_continue_roadmap_blocks_incomplete_successor_boundary(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo, with_boundaries=False)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "按路线图继续推进")
    assert code == 0
    assert payload["status"] == "blocked"
    assert any("boundary is incomplete" in blocker for blocker in payload["blockers"])
