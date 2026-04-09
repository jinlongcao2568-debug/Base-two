from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from .helpers import TASK_OPS_SCRIPT, git_commit_all, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_claim_promotion import _stage_candidate
from .test_roadmap_candidate_index import _candidate, _write_backlog

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import governance_console as console  # noqa: E402
from control_plane_root import (  # noqa: E402
    CONTROL_PLANE_EXECUTOR_ID,
    audit_full_clone_pool,
    detect_ledger_divergences,
    load_execution_leases,
    sync_execution_lease,
)


def _write_full_clone_pool(repo: Path, clone_path: Path) -> None:
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
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
    git_commit_all(repo, "prepare full clone worker slot")
    subprocess.run(["git", "clone", "--local", str(repo), str(clone_path)], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "switch", "-c", "codex/worker-01-idle"],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )


def _dependent_stage1_candidate(candidate_id: str, *, priority: int) -> dict:
    candidate = _candidate(candidate_id, status="waiting", priority=priority, depends_on=["stage1-core-contract"])
    candidate["title"] = "Stage1 source-family integration gate"
    candidate["lane_type"] = "integration_gate"
    candidate["allowed_dirs"] = ["src/stage1_orchestration/source_families/cn/"]
    candidate["planned_write_paths"] = ["src/stage1_orchestration/source_families/cn/"]
    return candidate


def _stage1_execution_task(*, status: str, worker_state: str, reserved_paths: list[str] | None = None) -> dict:
    return {
        "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
        "title": "Stage1 orchestration contract and fixture boundary",
        "status": status,
        "task_kind": "execution",
        "execution_mode": "isolated_worktree",
        "parent_task_id": None,
        "stage": "stage1",
        "branch": "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract",
        "size_class": "standard",
        "automation_mode": "manual",
        "worker_state": worker_state,
        "blocked_reason": None,
        "last_reported_at": "2026-04-08T00:00:00+08:00",
        "topology": "single_task",
        "allowed_dirs": ["src/stage1_orchestration/"],
        "reserved_paths": list(reserved_paths or []),
        "planned_write_paths": ["src/stage1_orchestration/"],
        "planned_test_paths": ["tests/stage1/"],
        "required_tests": ["pytest tests/stage1 -q"],
        "task_file": "docs/governance/tasks/TASK-RM-STAGE1-CORE-CONTRACT.md",
        "runlog_file": "docs/governance/runlogs/TASK-RM-STAGE1-CORE-CONTRACT-RUNLOG.md",
        "lane_count": 1,
        "lane_index": None,
        "parallelism_plan_id": None,
        "review_bundle_status": "not_applicable",
        "roadmap_candidate_id": "stage1-core-contract",
    }


def _append_stage1_execution_task(
    repo: Path,
    *,
    status: str,
    worker_state: str,
    reserved_paths: list[str] | None = None,
) -> None:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        _stage1_execution_task(status=status, worker_state=worker_state, reserved_paths=reserved_paths)
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)


def _write_stage1_claim(repo: Path, *, status: str) -> None:
    write_yaml(
        repo / ".codex/local/roadmap_candidates/claims.yaml",
        {
            "version": "0.1",
            "claims": [
                {
                    "candidate_id": "stage1-core-contract",
                    "status": status,
                    "formal_task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                }
            ],
        },
    )


def _mark_slot_active(repo: Path, task_id: str) -> None:
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")
    pool["slots"][0]["status"] = "active"
    pool["slots"][0]["current_task_id"] = task_id
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", pool)


def _write_clone_stage1_registry(clone_path: Path, *, status: str, worker_state: str | None = None) -> None:
    task = {
        "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
        "status": status,
        "roadmap_candidate_id": "stage1-core-contract",
    }
    if worker_state is not None:
        task["task_kind"] = "execution"
        task["worker_state"] = worker_state
    write_yaml(
        clone_path / "docs/governance/TASK_REGISTRY.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "tasks": [task],
        },
    )


def test_clone_governance_writes_redirect_to_main_control_plane(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(
        repo,
        [
            _stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _dependent_stage1_candidate("stage1-source-family-cn", priority=110),
        ],
    )

    promoted = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--dispatch-target",
        "full_clone",
        "--full-clone-slot-id",
        "worker-01",
        "--window-id",
        "worker-01",
    )
    finished = run_python(
        TASK_OPS_SCRIPT,
        clone_path,
        "worker-finish",
        "TASK-RM-STAGE1-CORE-CONTRACT",
        "--summary",
        "review ready",
        "--tests",
        "pytest tests/stage1 -q",
    )
    closed_from_clone = run_python(TASK_OPS_SCRIPT, clone_path, "close-ready-execution-tasks")
    closed = run_python(TASK_OPS_SCRIPT, repo, "close-ready-execution-tasks")

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")
    index = read_yaml(repo / ".codex/local/roadmap_candidates/index.yaml")
    clone_registry = read_yaml(clone_path / "docs/governance/TASK_REGISTRY.yaml")
    stage1_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT")
    slot = pool["slots"][0]
    by_id = {candidate["candidate_id"]: candidate for candidate in index["candidates"]}

    assert promoted.returncode == 0, promoted.stdout + promoted.stderr
    assert finished.returncode == 0, finished.stdout + finished.stderr
    assert closed_from_clone.returncode == 1
    assert "clone-side close-ready-execution-tasks is frozen" in closed_from_clone.stdout
    assert closed.returncode == 0, closed.stdout + closed.stderr
    assert stage1_task["status"] == "done"
    assert slot["status"] == "ready"
    assert slot["current_task_id"] is None
    assert claims["claims"][0]["status"] == "closed"
    assert by_id["stage1-source-family-cn"]["status"] == "ready"
    mirrored_task = next(task for task in clone_registry["tasks"] if task["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT")
    assert mirrored_task["status"] == "done"


def test_detect_ledger_divergence_for_ready_slot_stale_mirror(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)

    _append_stage1_execution_task(repo, status="done", worker_state="completed")
    subprocess.run(
        ["git", "switch", "-c", "codex/TASK-RM-STAGE1-SOURCE-FAMILY-CN-stage1-source-family-cn"],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )
    _write_clone_stage1_registry(clone_path, status="doing", worker_state="running")
    write_yaml(
        clone_path / ".codex/local/roadmap_candidates/index.yaml",
        {
            "version": "0.1",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "candidates": [
                {"candidate_id": "stage1-source-family-lanes"},
                {"candidate_id": "stage2-core-contract"},
            ],
        },
    )

    divergences = detect_ledger_divergences(repo)

    assert len(divergences) == 1
    assert divergences[0]["slot_id"] == "worker-01"
    assert divergences[0]["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"
    assert any("ready slot 当前分支不是 idle_branch" in reason for reason in divergences[0]["reasons"])
    assert any("clone 本地账本残留非终态执行任务" in reason for reason in divergences[0]["reasons"])
    assert any("clone 候选池格式过期" in reason for reason in divergences[0]["reasons"])


def test_console_detects_ledger_divergence_and_marks_candidate(monkeypatch, tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    clone_path.mkdir(parents=True, exist_ok=True)
    _write_backlog(
        repo,
        [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])],
    )
    run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")
    _write_full_clone_pool(repo, clone_path)

    _append_stage1_execution_task(repo, status="paused", worker_state="idle", reserved_paths=["src/stage6_facts/"])
    _write_stage1_claim(repo, status="taken_over")
    _mark_slot_active(repo, "TASK-RM-STAGE1-CORE-CONTRACT")
    _write_clone_stage1_registry(clone_path, status="done")

    monkeypatch.setattr(console, "_repo_root", lambda: repo)
    divergences = console._ledger_divergences(repo)
    payload = console._cached_pool_payload()
    row = payload["visible_candidates"][0]

    assert len(divergences) == 1
    assert divergences[0]["candidate_id"] == "stage1-core-contract"
    assert divergences[0]["main_status"] == "paused"
    assert divergences[0]["clone_status"] == "done"
    assert payload["summary"]["ledger_divergence_count"] == 1
    assert row["ledger_divergence"]["slot_id"] == "worker-01"
    assert row["copy_instruction"] == "先修复主控制面与工作树台账分叉，再继续判断、续接或接单。"
    assert "主控制面" in row["operator_reason"]


def test_blocked_slot_runtime_drift_is_quarantined_not_dispatch_blocking(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)

    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")
    pool["slots"][0]["status"] = "blocked"
    pool["slots"][0]["blocked_reason"] = "preserve-before-rebuild"
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", pool)

    runtime_file = repo / "scripts/control_plane_root.py"
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.write_text(
        "# advance control runtime for quarantined slot test\n",
        encoding="utf-8",
        newline="\n",
    )
    git_commit_all(repo, "advance control runtime for quarantined slot test")

    audit = audit_full_clone_pool(repo)
    slot = audit["slots"][0]

    assert slot["runtime_drift"] is True
    assert slot["quarantined"] is True
    assert slot["dispatch_eligible"] is False
    assert slot["dispatch_blocking_runtime_drift"] is False
    assert slot["divergent"] is False
    assert audit["ledger_divergence_count"] == 0
    assert audit["stale_runtime_count"] == 0
    assert audit["quarantined_runtime_count"] == 1
    assert audit["quarantined_slot_count"] == 1
    assert detect_ledger_divergences(repo) == []


def test_current_task_is_focus_projection_while_execution_leases_track_multiple_executors(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-RM-STAGE3-CORE-CONTRACT",
            "title": "stage3 contract",
            "status": "doing",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": None,
            "stage": "stage3",
            "branch": "codex/TASK-RM-STAGE3-CORE-CONTRACT-stage3-core-contract",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "running",
            "blocked_reason": None,
            "last_reported_at": "2026-04-09T21:00:00+08:00",
            "topology": "single_task",
            "allowed_dirs": ["src/stage3_parsing/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/stage3_parsing/"],
            "planned_test_paths": ["tests/stage3/"],
            "required_tests": ["pytest tests/stage3 -q"],
            "task_file": "docs/governance/tasks/TASK-RM-STAGE3-CORE-CONTRACT.md",
            "runlog_file": "docs/governance/runlogs/TASK-RM-STAGE3-CORE-CONTRACT-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "roadmap_candidate_id": "stage3-core-contract",
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    current_payload = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    focus_task = registry["tasks"][0]
    execution_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-RM-STAGE3-CORE-CONTRACT")

    sync_execution_lease(
        repo,
        task=focus_task,
        executor_id=CONTROL_PLANE_EXECUTOR_ID,
        executor_type="control_plane",
        status="running",
        owner_session_id="session-control-plane",
        heartbeat_at="2026-04-09T21:00:00+08:00",
    )
    sync_execution_lease(
        repo,
        task=execution_task,
        executor_id="worker-02",
        executor_type="full_clone",
        status="running",
        owner_session_id="session-worker-02",
        heartbeat_at="2026-04-09T21:01:00+08:00",
    )

    leases = load_execution_leases(repo)

    assert current_payload["current_task_id"] == "TASK-BASE-001"
    assert current_payload["status"] == "doing"
    assert {lease["executor_id"] for lease in leases["leases"]} == {CONTROL_PLANE_EXECUTOR_ID, "worker-02"}
    assert {lease["task_id"] for lease in leases["leases"]} == {"TASK-BASE-001", "TASK-RM-STAGE3-CORE-CONTRACT"}
    assert detect_ledger_divergences(repo) == []
