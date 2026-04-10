from __future__ import annotations

from pathlib import Path
import sys
import subprocess

from .helpers import TASK_OPS_SCRIPT, read_yaml, run_python, set_idle_control_plane, write_mvp_scope, write_yaml, init_governance_repo
from .test_roadmap_candidate_index import _candidate, _write_backlog

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from control_plane_root import build_governance_runtime_stamp  # noqa: E402


def _candidate_with_paths(candidate_id: str, *, priority: int, paths: list[str], protected_paths: list[str] | None = None) -> dict:
    candidate = _candidate(candidate_id, status="planned", priority=priority)
    candidate["planned_write_paths"] = paths
    candidate["allowed_dirs"] = paths
    candidate["protected_paths"] = list(protected_paths or [])
    candidate["branch_template"] = f"codex/{{task_id}}-{candidate_id}"
    return candidate


def _append_active_task(
    repo: Path,
    *,
    task_id: str,
    branch: str,
    paths: list[str],
    protected_paths: list[str] | None = None,
    candidate_id: str | None = None,
    executor_id: str = "worker-02",
    status: str = "doing",
    worker_state: str = "running",
) -> None:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": task_id,
            "title": "active task",
            "status": status,
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": None,
            "stage": "governance-test",
            "branch": branch,
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": worker_state,
            "blocked_reason": None,
            "last_reported_at": "2026-04-07T00:00:00+08:00",
            "topology": "single_worker",
            "allowed_dirs": paths,
            "reserved_paths": [],
            "protected_paths": list(protected_paths or []),
            "planned_write_paths": paths,
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
            "task_file": f"docs/governance/tasks/{task_id}.md",
            "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "successor_state": "backlog",
            "roadmap_candidate_id": candidate_id,
            "created_at": "2026-04-07T00:00:00+08:00",
            "activated_at": "2026-04-07T00:00:00+08:00",
            "closed_at": None,
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    write_yaml(
        repo / "docs/governance/EXECUTION_LEASES.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-07T00:00:00+08:00",
            "revision": 1,
            "leases": [
                {
                    "lease_id": f"lease-{task_id.lower()}-{executor_id}",
                    "task_id": task_id,
                    "task_kind": "execution",
                    "stage": "governance-test",
                    "branch": branch,
                    "candidate_id": candidate_id,
                    "executor_id": executor_id,
                    "executor_type": "full_clone",
                    "status": "running",
                    "owner_session_id": "test-session",
                    "started_at": "2026-04-07T00:00:00+08:00",
                    "heartbeat_at": "2026-04-07T00:00:00+08:00",
                    "closed_at": None,
                }
            ],
        },
    )


def _write_full_clone_pool(repo: Path, clone_path: Path) -> None:
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "status": "active",
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
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "prepare full clone slot"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "clone", "--local", str(repo), str(clone_path)], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "switch", "-c", "codex/worker-01-idle"],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )


def _clone_repo_on_idle_branch(repo: Path, clone_path: Path, idle_branch: str) -> None:
    subprocess.run(["git", "clone", "--local", str(repo), str(clone_path)], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "switch", "-c", idle_branch],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )


def _write_two_slot_full_clone_pool(repo: Path, blocked_clone: Path, ready_clone: Path) -> None:
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "status": "active",
            "control_plane_root": str(repo).replace("\\", "/"),
            "slots": [
                {
                    "slot_id": "worker-01",
                    "path": str(blocked_clone).replace("\\", "/"),
                    "branch": "codex/TASK-RM-STAGE2-CORE-CONTRACT-stage2-core-contract",
                    "idle_branch": "codex/worker-01-idle",
                    "status": "blocked",
                    "current_task_id": None,
                    "blocked_reason": "preserve-before-rebuild",
                    "last_provisioned_at": None,
                    "last_claimed_at": None,
                    "last_released_at": None,
                },
                {
                    "slot_id": "worker-02",
                    "path": str(ready_clone).replace("\\", "/"),
                    "branch": "codex/worker-02-idle",
                    "idle_branch": "codex/worker-02-idle",
                    "status": "ready",
                    "current_task_id": None,
                    "last_provisioned_at": None,
                    "last_claimed_at": None,
                    "last_released_at": None,
                },
            ],
        },
    )


def test_claim_next_dry_run_selects_top_ready_candidate_without_claim_file(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _candidate_with_paths("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate_id=stage1-core-contract" in result.stdout
    assert "takeover_mode=none" in result.stdout
    assert not (repo / ".codex/local/roadmap_candidates/claims.yaml").exists()


def test_claim_next_write_claim_makes_second_window_choose_next_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _candidate_with_paths("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )

    first = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--write-claim", "--window-id", "window-a")
    second = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--write-claim", "--window-id", "window-b")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert "candidate_id=stage1-core-contract" in first.stdout
    assert "candidate_id=stage2-core-contract" in second.stdout
    assert [claim["candidate_id"] for claim in claims["claims"]] == [
        "stage1-core-contract",
        "stage2-core-contract",
    ]


def test_claim_next_blocks_when_active_task_overlaps_ready_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
        ],
    )
    _append_active_task(
        repo,
        task_id="TASK-ACTIVE-001",
        branch="codex/TASK-ACTIVE-001",
        paths=["src/stage1_orchestration/"],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 1
    assert "no safe roadmap candidate" in result.stdout
    assert "write-path overlap with TASK-ACTIVE-001" in result.stdout


def test_claim_next_blocks_when_protected_paths_overlap_active_task(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(
        repo,
        [
            _candidate_with_paths(
                "stage1-global-slice",
                priority=100,
                paths=["src/stage1_orchestration/source_families/cn/subscope/"],
            ),
        ],
    )
    _append_active_task(
        repo,
        task_id="TASK-ACTIVE-002",
        branch="codex/TASK-ACTIVE-002",
        paths=["src/stage1_orchestration/source_families/cn/"],
        protected_paths=["src/stage1_orchestration/source_families/cn/"],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 1
    assert "protected-path conflict with TASK-ACTIVE-002" in result.stdout


def test_claim_next_prefers_expired_promoted_takeover(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    write_yaml(
        repo / ".codex/local/roadmap_candidates/claims.yaml",
        {
            "version": "0.1",
            "claims": [
                {
                    "candidate_id": "stage1-core-contract",
                    "status": "promoted",
                    "formal_task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                    "candidate_worktree": str((repo / "missing-worktree").resolve()).replace("\\", "/"),
                    "expires_at": "2026-04-08T00:00:00+08:00",
                }
            ],
        },
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
            "title": "stage1 contract",
            "status": "paused",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": None,
            "stage": "stage1",
            "branch": "codex/TASK-RM-STAGE1-CORE-CONTRACT",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "idle",
            "blocked_reason": None,
            "last_reported_at": "2026-04-08T00:00:00+08:00",
            "topology": "single_task",
            "allowed_dirs": ["src/stage1_orchestration/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/stage1_orchestration/"],
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
            "task_file": "docs/governance/tasks/TASK-RM-STAGE1-CORE-CONTRACT.md",
            "runlog_file": "docs/governance/runlogs/TASK-RM-STAGE1-CORE-CONTRACT-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "successor_state": None,
            "created_at": "2026-04-08T00:00:00+08:00",
            "activated_at": "2026-04-08T00:00:00+08:00",
            "closed_at": None,
            "roadmap_candidate_id": "stage1-core-contract",
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate_id=stage1-core-contract" in result.stdout
    assert "takeover_mode=expired_promoted_takeover" in result.stdout


def test_claim_next_obeys_roadmap_claim_capacity_not_runner_lane_ceiling(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    policy = read_yaml(repo / "docs/governance/TASK_POLICY.yaml")
    policy["roadmap_scheduler"]["max_active_claims_v1"] = 1
    policy["size_classes"]["heavy"]["dynamic_lane_ceiling_v1"] = 9
    write_yaml(repo / "docs/governance/TASK_POLICY.yaml", policy)
    _write_backlog(
        repo,
        [
            _candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"]),
            _candidate_with_paths("stage2-core-contract", priority=200, paths=["src/stage2_ingestion/"]),
        ],
    )

    first = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--write-claim", "--window-id", "window-a")
    second = run_python(TASK_OPS_SCRIPT, repo, "claim-next", "--window-id", "window-b")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 1
    assert "roadmap claim capacity reached (1/1)" in second.stdout


def test_claim_next_blocks_candidate_with_live_execution_lease_even_without_fresh_claim(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate_with_paths("stage3-core-contract", priority=100, paths=["src/stage3_parsing/"])])
    _append_active_task(
        repo,
        task_id="TASK-RM-STAGE3-CORE-CONTRACT",
        branch="codex/TASK-RM-STAGE3-CORE-CONTRACT-stage3-core-contract",
        paths=["src/stage3_parsing/"],
        candidate_id="stage3-core-contract",
        executor_id="worker-02",
        status="done",
        worker_state="completed",
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 1
    assert "no safe roadmap candidate" in result.stdout
    assert "top_candidate=stage3-core-contract" in result.stdout


def test_claim_next_from_clone_side_task_ops_resolves_control_plane_truth(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    result = run_python(TASK_OPS_SCRIPT, clone_path, "claim-next")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate_id=stage1-core-contract" in result.stdout


def test_claim_next_blocks_when_governance_runtime_is_dirty(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    runtime_file = repo / "scripts/review_candidate_pool.py"
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.write_text(
        "# dirty runtime change for claim-next test\n",
        encoding="utf-8",
        newline="\n",
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 1
    assert "governance runtime unpublished" in result.stdout
    assert "scripts/review_candidate_pool.py" in result.stdout


def test_claim_next_blocks_when_runtime_rollout_pending(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    baseline = build_governance_runtime_stamp(repo)
    write_yaml(
        repo / ".codex/local/governance_runtime/rollout_state.yaml",
        {
            "version": "1.0",
            "rollout_pending": False,
            "last_successful_hash": baseline["governance_scripts_hash"],
            "last_successful_head": baseline.get("control_plane_head"),
        },
    )
    runtime_file = repo / "scripts/review_candidate_pool.py"
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.write_text(
        "# runtime change for rollout pending claim-next test\n",
        encoding="utf-8",
        newline="\n",
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "runtime change for rollout pending claim-next test"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 1
    assert "runtime rollout pending" in result.stdout


def test_claim_next_fails_fast_when_mvp_scope_mismatches_business_automation_scope(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    write_mvp_scope(
        repo,
        scope="stage2_to_stage6",
        included_stages=["stage2", "stage3", "stage4", "stage5", "stage6"],
        excluded_stages=["stage1", "stage7", "stage8", "stage9"],
    )

    result = run_python(TASK_OPS_SCRIPT, repo, "claim-next")

    assert result.returncode == 1
    assert "scope mismatch" in result.stdout


def test_claim_next_blocks_ready_full_clone_slot_with_live_runtime_drift(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])
    subprocess.run(
        ["git", "switch", "-c", "codex/TASK-RM-STAGE1-SOURCE-FAMILY-CN-stage1-source-family-cn"],
        cwd=clone_path,
        check=True,
        capture_output=True,
        text=True,
    )
    write_yaml(
        clone_path / "docs/governance/TASK_REGISTRY.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "tasks": [
                {
                    "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                    "status": "doing",
                    "task_kind": "execution",
                    "worker_state": "running",
                    "roadmap_candidate_id": "stage1-core-contract",
                }
            ],
        },
    )

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--dispatch-target",
        "full_clone",
        "--full-clone-slot-id",
        "worker-01",
    )
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")

    assert result.returncode == 1
    assert "ledger divergence detected" in result.stdout
    assert pool["slots"][0]["status"] == "blocked"
    assert pool["slots"][0]["blocked_reason"]


def test_claim_next_allows_healthy_ready_slot_when_another_slot_is_quarantined(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    blocked_clone = tmp_path / "clone-worker-01"
    _clone_repo(repo, blocked_clone)
    ready_clone = tmp_path / "clone-worker-02"
    _clone_repo_on_idle_branch(repo, ready_clone, "codex/worker-02-idle")
    subprocess.run(
        ["git", "switch", "-c", "codex/TASK-RM-STAGE2-CORE-CONTRACT-stage2-core-contract"],
        cwd=blocked_clone,
        check=True,
        capture_output=True,
        text=True,
    )
    _write_two_slot_full_clone_pool(repo, blocked_clone, ready_clone)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "claim-next",
        "--promote-task",
        "--dispatch-target",
        "full_clone",
        "--full-clone-slot-id",
        "worker-02",
        "--window-id",
        "worker-02",
    )
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate_id=stage1-core-contract" in result.stdout
    assert pool["slots"][0]["status"] == "blocked"
    assert pool["slots"][1]["status"] == "active"
    assert pool["slots"][1]["current_task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"


def test_claim_next_promote_reuses_resumable_formal_task_without_duplicate_registry_row(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    _clone_repo(repo, clone_path)
    _write_backlog(repo, [_candidate_with_paths("stage1-core-contract", priority=100, paths=["src/stage1_orchestration/"])])

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
            "title": "stage1 contract",
            "status": "paused",
            "task_kind": "execution",
            "execution_mode": "isolated_worktree",
            "parent_task_id": None,
            "stage": "stage1",
            "branch": "codex/TASK-RM-STAGE1-CORE-CONTRACT-stage1-core-contract",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "idle",
            "blocked_reason": None,
            "last_reported_at": "2026-04-08T00:00:00+08:00",
            "topology": "single_task",
            "allowed_dirs": ["src/stage1_orchestration/"],
            "reserved_paths": [],
            "planned_write_paths": ["src/stage1_orchestration/"],
            "planned_test_paths": ["tests/stage1/"],
            "required_tests": ["pytest tests/stage1 -q"],
            "task_file": "docs/governance/tasks/TASK-RM-STAGE1-CORE-CONTRACT.md",
            "runlog_file": "docs/governance/runlogs/TASK-RM-STAGE1-CORE-CONTRACT-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "successor_state": None,
            "created_at": "2026-04-08T00:00:00+08:00",
            "activated_at": "2026-04-08T00:00:00+08:00",
            "closed_at": None,
            "roadmap_candidate_id": "stage1-core-contract",
        }
    )
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    write_yaml(
        repo / ".codex/local/roadmap_candidates/claims.yaml",
        {
            "version": "0.1",
            "claims": [
                {
                    "candidate_id": "stage1-core-contract",
                    "status": "closed",
                    "formal_task_id": "TASK-RM-STAGE1-CORE-CONTRACT",
                    "closed_at": "2026-04-08T00:00:00+08:00",
                    "expires_at": "2026-04-08T00:00:00+08:00",
                }
            ],
        },
    )

    result = run_python(
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
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    claims = read_yaml(repo / ".codex/local/roadmap_candidates/claims.yaml")
    pool = read_yaml(repo / "docs/governance/FULL_CLONE_POOL.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "claim-next taken-over candidate_id=stage1-core-contract" in result.stdout
    assert len([task for task in registry["tasks"] if task["task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"]) == 1
    assert claims["claims"][0]["status"] == "taken_over"
    assert claims["claims"][0]["window_id"] == "worker-01"
    assert pool["slots"][0]["status"] == "active"
    assert pool["slots"][0]["current_task_id"] == "TASK-RM-STAGE1-CORE-CONTRACT"
