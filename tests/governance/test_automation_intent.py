from __future__ import annotations

import json
from pathlib import Path
import subprocess

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
from .test_roadmap_candidate_index import _candidate, _write_backlog


def _preflight(repo: Path, utterance: str) -> tuple[int, dict]:
    result = run_python(AUTOMATION_INTENT_SCRIPT, repo, "preflight", "--utterance", utterance)
    return result.returncode, json.loads(result.stdout)


def _create_successor(repo: Path, task_id: str = "TASK-NEXT-001") -> None:
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
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
    )
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


def _write_full_clone_pool(repo: Path, clone_path: Path) -> None:
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
            "status": "active",
            "root_path": str(clone_path.parent).replace("\\", "/"),
            "control_plane_root": str(repo).replace("\\", "/"),
            "slots": [
                {
                    "slot_id": "worker-01",
                    "path": str(clone_path).replace("\\", "/"),
                    "branch": "codex/worker-01-idle",
                    "idle_branch": "codex/worker-01-idle",
                    "status": "ready",
                    "current_task_id": None,
                    "last_provisioned_at": None,
                    "last_claimed_at": None,
                    "last_released_at": None,
                }
            ],
        },
    )


def _clone_repo(repo: Path, clone_path: Path) -> None:
    git_commit_all(repo, "prepare full clone pool")
    subprocess.run(["git", "clone", "--local", str(repo), str(clone_path)], check=True, capture_output=True, text=True)


@pytest.mark.parametrize(
    ("utterance", "intent_id"),
    [
        ("继续当前任务", "continue-current"),
        ("按路线图继续推进", "continue-roadmap"),
        ("持续按路线图开发", "claim-next"),
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
    if intent_id == "claim-next":
        set_idle_control_plane(repo)
        candidate = _candidate("stage1-core-contract", status="planned", priority=100)
        candidate["allowed_dirs"] = ["src/stage1_orchestration/", "tests/stage1/"]
        candidate["planned_write_paths"] = ["src/stage1_orchestration/", "tests/stage1/"]
        candidate["planned_test_paths"] = ["tests/stage1/"]
        _write_backlog(repo, [candidate])

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


def test_preflight_routes_highest_priority_roadmap_phrase_to_claim_next(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    candidate = _candidate("stage1-core-contract", status="planned", priority=100)
    candidate["allowed_dirs"] = ["src/stage1_orchestration/", "tests/stage1/"]
    candidate["planned_write_paths"] = ["src/stage1_orchestration/", "tests/stage1/"]
    candidate["planned_test_paths"] = ["tests/stage1/"]
    _write_backlog(repo, [candidate])

    code, payload = _preflight(repo, "持续按路线图开发")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "claim-next"
    assert payload["mapped_command"] == "python scripts/task_ops.py claim-next --promote-task"
    assert payload["claim_next_candidate"]["candidate_id"] == "stage1-core-contract"


def test_preflight_routes_free_form_roadmap_request(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "按计划推进到下一步")
    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "continue-roadmap"


def test_preflight_roadmap_reports_ready_closeout_recommendation(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "按路线图继续推进")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["closeout_recommendation"]["status"] == "ready"
    assert payload["closeout_recommendation"]["task_id"] == "TASK-BASE-001"


def test_preflight_continue_roadmap_blocks_idle_without_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    for capability in capability_map["capabilities"]:
        if capability["capability_id"] == "roadmap_autopilot_continuation":
            capability["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    close_live_task_to_idle(repo, commit_after_close=True)
    code, payload = _preflight(repo, "按路线图继续推进")
    assert code == 0
    assert payload["status"] == "blocked"
    assert payload["intent_id"] == "continue-roadmap"


def test_preflight_routes_worker_phrase_to_worker_self_loop_in_clone(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)

    code, payload = _preflight(clone_path, "恢复当前窗口任务")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "worker-self-loop"
    assert payload["mapped_command"] == "python scripts/worker_self_loop.py once"
    assert payload["worker_loop_decision"]["mode"] == "claim-next"
