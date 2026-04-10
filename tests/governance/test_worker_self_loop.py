from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from .helpers import git_commit_all, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "worker_self_loop.py"
TASK_OPS_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "task_ops.py"

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import worker_self_loop as worker_self_loop_module  # noqa: E402


def _candidate(
    candidate_id: str,
    *,
    status: str,
    priority: int,
    depends_on: list[str] | None = None,
    candidate_kind: str = "lane_slice",
    claimable: bool = True,
    stage: str = "stage2",
    allow_create_paths: bool = True,
    pilot_only: bool = False,
    coverage_regions: list[str] | None = None,
) -> dict:
    scope_path = f"src/governance_test/{candidate_id}/"
    payload = {
        "candidate_id": candidate_id,
        "title": candidate_id,
        "stage": stage,
        "module_id": "stage1_orchestration",
        "candidate_kind": candidate_kind,
        "claimable": claimable,
        "parent_candidate_id": None,
        "lane_type": "integration_gate" if "integration" in candidate_id else ("core_contract" if "core" in candidate_id else "stage_internal_parallel"),
        "status": status,
        "priority": priority,
        "depends_on": list(depends_on or []),
        "unlocks": [],
        "allowed_dirs": [scope_path],
        "forbidden_write_paths": ["src/stage6_facts/"],
        "protected_paths": [],
        "planned_write_paths": [scope_path],
        "planned_test_paths": ["tests/governance/"],
        "required_tests": ["python scripts/check_repo.py"],
        "allow_create_paths": allow_create_paths,
        "pilot_only": pilot_only,
        "branch_template": "codex/{task_id}",
        "worktree_template": "../AX9.worktrees/{task_id}",
        "integration_gate": None,
        "expected_children": [],
        "completion_policy": "none",
        "claim_policy": {
            "one_window_one_candidate": True,
            "conflict_policy": "choose_next_safe_candidate",
            "scheduler_lock_required": True,
        },
        "takeover_policy": {
            "stale_after_minutes_source": "docs/governance/HANDOFF_POLICY.yaml",
            "clean_worktree_takeover": "allow",
            "scoped_dirty_checkpoint": "allow_before_takeover",
            "out_of_scope_dirty_policy": "block_for_human_decision",
        },
    }
    payload["coverage_regions"] = coverage_regions if coverage_regions is not None else ["CN"]
    return payload


def _write_backlog(repo: Path, candidates: list[dict]) -> None:
    write_yaml(
        repo / "docs/governance/ROADMAP_BACKLOG.yaml",
        {
            "version": "0.2",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "authority_source": "docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md",
            "defaults": {"legacy_reserved_paths_map_to": "forbidden_write_paths"},
            "compiler_policy": {"mode": "inline_candidates"},
            "scheduler_policy": {
                "entrypoint": "claim-next",
                "claim_capacity_source": "docs/governance/TASK_POLICY.yaml#roadmap_scheduler.max_active_claims_v1",
                "single_writer_roots": [],
            },
            "stages": [{"stage": "stage1", "module_id": "stage1_orchestration"}],
            "candidates": candidates,
        },
    )


def _stage_candidate(candidate_id: str, *, priority: int, paths: list[str]) -> dict:
    candidate = _candidate(candidate_id, status="planned", priority=priority)
    candidate["allowed_dirs"] = paths
    candidate["planned_write_paths"] = paths
    candidate["planned_test_paths"] = ["tests/stage1/"]
    candidate["required_tests"] = ["pytest tests/stage1 -q"]
    candidate["forbidden_write_paths"] = ["src/stage6_facts/"]
    candidate["protected_paths"] = []
    candidate["branch_template"] = f"codex/{{task_id}}-{candidate_id}"
    candidate["worktree_template"] = "../AX9.worktrees/{task_id}"
    return candidate


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


def test_worker_self_loop_task_ops_use_hidden_subprocess_on_windows(monkeypatch, tmp_path: Path) -> None:
    captured = {}

    def fake_run(*args, **kwargs):
        captured["creationflags"] = kwargs.get("creationflags")

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(worker_self_loop_module.subprocess, "run", fake_run)

    result = worker_self_loop_module._run_task_ops(tmp_path, "can-close", "TASK-BASE-001")

    assert result.returncode == 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW
