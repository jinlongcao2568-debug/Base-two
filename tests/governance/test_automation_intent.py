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


def test_preflight_supports_fixed_window_phrases(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    candidate = _candidate("stage1-core-contract", status="planned", priority=100)
    candidate["allowed_dirs"] = ["src/stage1_orchestration/", "tests/stage1/"]
    candidate["planned_write_paths"] = ["src/stage1_orchestration/", "tests/stage1/"]
    candidate["planned_test_paths"] = ["tests/stage1/"]
    _write_backlog(repo, [candidate])

    review_code, review_payload = _preflight(
        repo,
        "审查窗口：候选池有没有出错或者不合理或者开发上遗漏或不兼容，排查哪些任务是执行一半未完成",
    )
    coord_code, coord_payload = _preflight(repo, "协调窗口：定时更新候选池")
    claim_code, claim_payload = _preflight(repo, "持续按路线图开发")

    assert review_code == 0
    assert review_payload["intent_id"] == "review-candidate-pool"
    assert coord_code == 0
    assert coord_payload["intent_id"] == "coordinator-refresh-loop"
    assert claim_code == 0
    assert claim_payload["intent_id"] == "claim-next"


def test_preflight_worker_window_phrase_routes_to_worker_self_loop(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)

    code, payload = _preflight(clone_path, "任务窗口：领取任务执行完毕持续领取持续开发")

    assert code == 0
    assert payload["intent_id"] == "worker-self-loop"
    assert payload["mapped_command"] == "python scripts/worker_self_loop.py loop --interval-seconds 60"


def test_preflight_recover_task_extracts_explicit_task_id(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)

    code, payload = _preflight(clone_path, "恢复：TASK-RM-STAGE1-CORE-CONTRACT")

    assert code == 0
    assert payload["intent_id"] == "recover-task-explicit"
    assert payload["resolved_task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"


def test_preflight_continue_roadmap_reports_ready_closeout_recommendation(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    _mark_review_ready(repo)

    code, payload = _preflight(repo, "按路线图继续推进")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["intent_id"] == "continue-roadmap"
    assert payload["closeout_recommendation"]["status"] == "ready"


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
