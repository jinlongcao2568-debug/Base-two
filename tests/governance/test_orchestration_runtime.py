from __future__ import annotations

import json
from pathlib import Path

from .helpers import (
    TASK_OPS_SCRIPT,
    close_live_task_to_idle,
    init_governance_repo,
    read_yaml,
    run_python,
    write_yaml,
)


SESSION_A = {"CODEX_THREAD_ID": "session-A"}


def _status_json(repo: Path) -> dict:
    result = run_python(TASK_OPS_SCRIPT, repo, "orchestration-status", "--format", "json")
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


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


def test_orchestration_status_reports_required_sections(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    payload = _status_json(repo)

    assert {
        "runtime",
        "lease",
        "sessions",
        "workers",
        "task_sources",
        "publish_readiness",
        "continuation_readiness",
        "current_task",
        "candidate_summary",
        "runner_pressure",
    }.issubset(payload)
    assert payload["runtime"]["current_task_id"] == "TASK-BASE-001"
    assert payload["runtime"]["status"] == "active"
    assert payload["task_sources"]["entries"]["linear"]["observed_status"] == "disabled"
    assert payload["workers"]["entries"]["worker-local-01"]["observed_status"] == "active"
    assert payload["publish_readiness"]["status"] == "blocked"
    assert payload["publish_readiness"]["task_id"] == "TASK-BASE-001"
    assert payload["publish_readiness"]["recommended_action"].startswith("move the live task to review or done")
    assert payload["continuation_readiness"]["status"] == "continue-current"
    assert payload["continuation_readiness"]["checkpoint_required"] is False
    assert payload["continuation_readiness"]["recommended_action"] == "continue-current"


def test_continue_current_records_session_runtime_telemetry(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    continued = run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)

    assert continued.returncode == 0, continued.stdout + continued.stderr
    payload = _status_json(repo)
    session = payload["sessions"]["records"]["session-A"]
    assert payload["runtime"]["current_command"] == "continue-current"
    assert payload["runtime"]["status"] == "active"
    assert session["thread_id"] == "session-A"
    assert session["writer_state"] == "writable"
    assert session["continue_intent"] == "current"
    assert session["current_task_id"] == "TASK-BASE-001"
    assert session["runtime_status"] == "active"


def test_plan_coordination_sets_runtime_to_planning(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    planned = run_python(TASK_OPS_SCRIPT, repo, "plan-coordination", env=SESSION_A)

    assert planned.returncode == 0, planned.stdout + planned.stderr
    payload = _status_json(repo)
    session = payload["sessions"]["records"]["session-A"]
    assert payload["runtime"]["current_command"] == "plan-coordination"
    assert payload["runtime"]["status"] == "planning"
    assert session["current_command"] == "plan-coordination"
    assert session["runtime_status"] == "planning"


def test_orchestration_status_marks_remote_worker_as_unsupported(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    registry = read_yaml(repo / "docs/governance/WORKER_REGISTRY.yaml")
    registry["workers"].append(
        {
            "worker_id": "worker-remote-01",
            "kind": "ssh",
            "enabled": True,
            "status": "active",
            "host": "192.168.1.9",
            "workspace_root": "/srv/ax9",
            "capabilities": ["execution"],
            "unsupported_in_v1": True,
            "last_heartbeat_at": None,
            "notes": "Future remote worker reservation.",
        }
    )
    write_yaml(repo / "docs/governance/WORKER_REGISTRY.yaml", registry)

    payload = _status_json(repo)

    assert payload["workers"]["entries"]["worker-remote-01"]["observed_status"] == "unsupported_in_v1"


def test_orchestration_status_publish_readiness_is_idle_without_live_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    from .helpers import set_idle_control_plane

    set_idle_control_plane(repo)
    payload = _status_json(repo)

    assert payload["publish_readiness"]["status"] == "idle"
    assert payload["publish_readiness"]["task_id"] is None
    assert payload["publish_readiness"]["task_publishable"] is False
    assert "no live current task" in payload["publish_readiness"]["blockers"][0]


def test_orchestration_status_reports_recoverable_predecessor_readiness(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_successor(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    close_live_task_to_idle(repo, commit_after_close=False)

    payload = _status_json(repo)
    readiness = payload["continuation_readiness"]

    assert readiness["status"] == "ready"
    assert readiness["recoverable_predecessor_task_id"] == "TASK-BASE-001"
    assert readiness["checkpoint_required"] is True
    assert readiness["checkpoint_eligible"] is True
    assert readiness["next_successor_task_id"] == "TASK-NEXT-001"
    assert readiness["recommended_action"] == "continue-roadmap"
