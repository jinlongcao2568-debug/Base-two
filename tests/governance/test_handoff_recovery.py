from __future__ import annotations

import json
from pathlib import Path

from .helpers import (
    AUTOMATION_INTENT_SCRIPT,
    TASK_OPS_SCRIPT,
    git_commit_all,
    init_governance_repo,
    read_yaml,
    run_python,
)


def test_new_top_level_coordination_task_creates_handoff_file(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-COORD-RECOVERY-001",
        "--title",
        "coordination recovery task",
        "--stage",
        "recovery-stage",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "--planned-write-paths",
        "docs/governance/",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    handoff = read_yaml(repo / "docs/governance/handoffs/TASK-COORD-RECOVERY-001.yaml")
    assert handoff["task_id"] == "TASK-COORD-RECOVERY-001"
    assert handoff["summary_status"] == "queued"
    assert handoff["candidate_write_paths"] == ["docs/governance/"]


def test_worker_report_writes_formal_handoff_fields(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-report",
        "TASK-BASE-001",
        "--note",
        "implemented recovery parser",
        "--completed-item",
        "formal parser implemented",
        "--remaining-item",
        "wire continue-current output",
        "--next-step",
        "Connect the recovery pack to continue-current.",
        "--next-test",
        "pytest tests/governance/test_handoff_recovery.py -q",
        "--risk",
        "handoff/runlog drift",
        "--candidate-write-path",
        "scripts/task_handoff.py",
        "--candidate-test-path",
        "tests/governance/test_handoff_recovery.py",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    handoff = read_yaml(repo / "docs/governance/handoffs/TASK-BASE-001.yaml")
    assert handoff["summary_status"] == "doing"
    assert handoff["completed_items"] == ["formal parser implemented"]
    assert handoff["remaining_items"] == ["wire continue-current output"]
    assert handoff["next_step"] == "Connect the recovery pack to continue-current."
    assert handoff["next_tests"] == ["pytest tests/governance/test_handoff_recovery.py -q"]
    assert handoff["current_risks"] == ["handoff/runlog drift"]
    assert handoff["candidate_write_paths"] == ["scripts/task_handoff.py"]
    assert handoff["candidate_test_paths"] == ["tests/governance/test_handoff_recovery.py"]


def test_worker_finish_writes_review_ready_recovery_pack(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-BASE-001",
        "--summary",
        "recovery pack integrated",
        "--tests",
        "pytest tests/base -q",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    handoff = read_yaml(repo / "docs/governance/handoffs/TASK-BASE-001.yaml")
    assert handoff["summary_status"] == "review"
    assert handoff["completed_items"] == ["recovery pack integrated"]
    assert "close" in handoff["next_step"].lower()
    assert handoff["next_tests"] == ["pytest tests/base -q"]


def test_worker_finish_records_all_repeated_test_flags(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-BASE-001",
        "--summary",
        "recovery pack integrated",
        "--tests",
        "python scripts/check_repo.py",
        "--tests",
        "python scripts/check_hygiene.py",
        "--tests",
        "pytest tests/base -q",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    runlog = (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").read_text(encoding="utf-8")
    assert "`python scripts/check_repo.py`" in runlog
    assert "`python scripts/check_hygiene.py`" in runlog
    assert "`pytest tests/base -q`" in runlog


def test_continue_current_restores_fallback_recovery_when_formal_handoff_missing(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(TASK_OPS_SCRIPT, repo, "continue-current")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[RECOVERY] source=task_runlog_fallback" in result.stdout
    assert "formal handoff missing" in result.stdout


def test_automation_intent_preflight_includes_recovery_pack(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-report",
        "TASK-BASE-001",
        "--completed-item",
        "formal handoff recorded",
        "--next-step",
        "Resume the scoped work.",
    )
    git_commit_all(repo, "record formal handoff")

    result = run_python(AUTOMATION_INTENT_SCRIPT, repo, "preflight", "--utterance", "继续当前任务")
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["status"] == "ready"
    assert payload["recovery_source"] == "formal_handoff"
    assert payload["recovery_pack"]["completed_items"] == ["formal handoff recorded"]
    assert payload["recovery_pack"]["next_step"] == "Resume the scoped work."
