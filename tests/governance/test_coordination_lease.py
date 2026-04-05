from __future__ import annotations

import subprocess
from pathlib import Path

from .helpers import (
    AUTOMATION_INTENT_SCRIPT,
    TASK_OPS_SCRIPT,
    init_governance_repo,
    read_yaml,
    run_python,
    write_yaml,
)


SESSION_A = {"CODEX_THREAD_ID": "session-A"}
SESSION_B = {"CODEX_THREAD_ID": "session-B"}


def _runtime_payload(repo: Path) -> dict:
    return read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")


def test_continue_current_allows_only_owner_to_write(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    first = run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)
    second = run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_B)

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert "[READONLY]" in second.stdout
    runtime = _runtime_payload(repo)
    assert runtime["leases"]["TASK-BASE-001"]["owner_session_id"] == "session-A"


def test_release_allows_second_session_to_continue_writing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)
    released = run_python(TASK_OPS_SCRIPT, repo, "release", "TASK-BASE-001", env=SESSION_A)
    resumed = run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_B)

    assert released.returncode == 0, released.stdout + released.stderr
    assert resumed.returncode == 0, resumed.stdout + resumed.stderr
    assert "[READONLY]" not in resumed.stdout
    runtime = _runtime_payload(repo)
    assert runtime["leases"]["TASK-BASE-001"]["owner_session_id"] == "session-B"


def test_takeover_requires_explicit_command_when_other_session_is_active(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)
    blocked = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-report",
        "TASK-BASE-001",
        "--note",
        "blocked by lease",
        env=SESSION_B,
    )
    takeover = run_python(TASK_OPS_SCRIPT, repo, "takeover", "TASK-BASE-001", env=SESSION_B)

    assert blocked.returncode == 1
    assert "active coordination lease" in blocked.stdout
    assert takeover.returncode == 0, takeover.stdout + takeover.stderr
    runtime = _runtime_payload(repo)
    assert runtime["leases"]["TASK-BASE-001"]["owner_session_id"] == "session-B"
    runlog = (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").read_text(encoding="utf-8")
    assert "takeover session=`session-B` previous_owner=`session-A`" in runlog


def test_stale_lease_can_be_reclaimed_by_continue_current(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)
    runtime_path = repo / ".codex/local/COORDINATION_RUNTIME.yaml"
    runtime = read_yaml(runtime_path)
    runtime["leases"]["TASK-BASE-001"]["last_seen_at"] = "2026-04-05T00:00:00+08:00"
    write_yaml(runtime_path, runtime)

    reclaimed = run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_B)

    assert reclaimed.returncode == 0, reclaimed.stdout + reclaimed.stderr
    assert "[READONLY]" not in reclaimed.stdout
    runtime = _runtime_payload(repo)
    assert runtime["leases"]["TASK-BASE-001"]["owner_session_id"] == "session-B"


def test_handoff_and_release_leave_auditable_records(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)
    handoff = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "handoff",
        "TASK-BASE-001",
        "--next-step",
        "Resume after takeover.",
        "--next-test",
        "python scripts/check_repo.py",
        env=SESSION_A,
    )
    release = run_python(TASK_OPS_SCRIPT, repo, "release", "TASK-BASE-001", env=SESSION_A)

    assert handoff.returncode == 0, handoff.stdout + handoff.stderr
    assert release.returncode == 0, release.stdout + release.stderr
    handoff_payload = read_yaml(repo / "docs/governance/handoffs/TASK-BASE-001.yaml")
    assert handoff_payload["next_step"] == "A new session may continue-current or takeover before further writes occur."
    runlog = (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").read_text(encoding="utf-8")
    assert "handoff session=`session-A`" in runlog
    assert "release session=`session-A`" in runlog


def test_coordination_runtime_is_git_ignored(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    assert ".codex/local" not in status.stdout


def test_automation_intent_execute_respects_active_lease(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    run_python(TASK_OPS_SCRIPT, repo, "continue-current", env=SESSION_A)
    catalog = read_yaml(repo / "docs/governance/AUTOMATION_INTENTS.yaml")
    utterance = catalog["supported_intents"][0]["canonical_phrase"]
    result = run_python(
        AUTOMATION_INTENT_SCRIPT,
        repo,
        "execute",
        "--utterance",
        utterance,
        env=SESSION_B,
    )

    assert result.returncode == 1
    assert "写租约" in result.stdout
