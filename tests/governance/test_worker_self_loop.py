from __future__ import annotations

import json
from pathlib import Path
import subprocess

from .helpers import git_commit_all, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml
from .test_roadmap_claim_promotion import _stage_candidate
from .test_roadmap_candidate_index import _write_backlog


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "worker_self_loop.py"
TASK_OPS_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "task_ops.py"


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


def _run_loop(clone_path: Path, *args: str):
    result = run_python(SCRIPT, clone_path, *args)
    return result.returncode, json.loads(result.stdout)


def test_worker_self_loop_claims_next_for_idle_clone(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    code, payload = _run_loop(clone_path, "once")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["task"]["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"
    assert subprocess.run(["git", "branch", "--show-current"], cwd=clone_path, check=True, capture_output=True, text=True).stdout.strip() == "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract"


def test_worker_self_loop_resumes_blocked_task_without_claiming_new_one(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--dispatch-target", "full_clone", "--full-clone-slot-id", "worker-01")
    blocked = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-blocked",
        "TASK-RM-STAGE1-CORE-CONTRACT",
        "--reason",
        "manual blocker",
    )
    assert blocked.returncode == 0, blocked.stdout + blocked.stderr

    code, payload = _run_loop(clone_path, "once")

    assert code == 1
    assert payload["status"] == "blocked"
    assert payload["task"]["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"
    assert "manual blocker" in payload["blockers"][0]


def test_worker_self_loop_hands_review_task_back_to_coordinator_closeout(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(
        repo,
        [
            _stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _stage_candidate("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )
    run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--dispatch-target", "full_clone", "--full-clone-slot-id", "worker-01")
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-RM-STAGE1-CORE-CONTRACT",
        "--summary",
        "review ready",
        "--tests",
        "pytest tests/stage1 -q",
    )
    assert finished.returncode == 0, finished.stdout + finished.stderr

    code, payload = _run_loop(clone_path, "once")

    assert code == 0
    assert payload["mode"] == "await-coordinator-closeout"
    assert payload["task"]["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"


def test_worker_self_loop_releases_done_task_before_next_claim(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(
        repo,
        [
            _stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _stage_candidate("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )
    claimed = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--dispatch-target",
        "full_clone",
        "--full-clone-slot-id",
        "worker-01",
    )
    assert claimed.returncode == 0, claimed.stdout + claimed.stderr

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT")
    task["status"] = "done"
    task["worker_state"] = "completed"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    clone_registry = read_yaml(clone_path / "docs/governance/TASK_REGISTRY.yaml")
    clone_task = next(item for item in clone_registry["tasks"] if item["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT")
    clone_task["status"] = "done"
    clone_task["worker_state"] = "completed"
    write_yaml(clone_path / "docs/governance/TASK_REGISTRY.yaml", clone_registry)
    subprocess.run(
        ["git", "switch", "-c", task["branch"]],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )

    code, payload = _run_loop(clone_path, "once")
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT")

    assert code == 0
    assert payload["status"] == "ready"
    assert payload["mode"] == "claim-next"
    assert pool["slots"][0]["status"] == "ready"
    assert pool["slots"][0]["current_task_id"] is None
    assert entry["status"] == "closed"
    assert entry["cleanup_state"] == "not_needed"
    assert subprocess.run(["git", "branch", "--show-current"], cwd=clone_path, check=True, capture_output=True, text=True).stdout.strip() == "codex/worker-01-idle"


def test_worker_self_loop_supports_explicit_task_id_fallback(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--dispatch-target", "full_clone", "--full-clone-slot-id", "worker-01")
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")
    pool["slots"][0]["current_task_id"] = None
    pool["slots"][0]["status"] = "active"
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", pool)
    subprocess.run(["git", "switch", "codex/worker-01-idle"], cwd=clone_path, check=False, capture_output=True, text=True)

    code, payload = _run_loop(clone_path, "once", "--task-id", "TASK-RM-STAGE1-CORE-CONTRACT")

    assert code == 0
    assert payload["task"]["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"


def test_worker_self_loop_resumes_paused_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(repo, [_stage_candidate("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--promote-task", "--dispatch-target", "full_clone", "--full-clone-slot-id", "worker-01")
    paused = run_python(TASK_OPS_SCRIPT, repo, "pause", "TASK-RM-STAGE1-CORE-CONTRACT")
    assert paused.returncode == 0, paused.stdout + paused.stderr

    code, payload = _run_loop(clone_path, "once")

    assert code == 0
    assert payload["mode"] == "resume-current"
    assert payload["task"]["status"] == "paused"


def test_worker_self_loop_blocks_when_full_clone_pool_is_frozen(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")
    pool["status"] = "blocked"
    write_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml", pool)

    code, payload = _run_loop(clone_path, "once")

    assert code == 1
    assert payload["status"] == "blocked"
    assert payload["mode"] == "pool-frozen"
