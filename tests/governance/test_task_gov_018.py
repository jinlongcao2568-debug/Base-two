from __future__ import annotations

from pathlib import Path

from .helpers import CHECK_REPO_SCRIPT, TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python_inline as run_python, write_yaml


def _create_execution_child(repo: Path, task_id: str, *, required_test: str | None = None) -> None:
    required_test = required_test or f'python "{CHECK_REPO_SCRIPT.as_posix()}"'
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        task_id,
        "--title",
        f"{task_id} child lane",
        "--stage",
        "child-stage",
        "--branch",
        f"feat/{task_id}",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
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
        required_test,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_reconcile_ledgers_repairs_registry_from_current_truth(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["status"] = "paused"
    registry["tasks"][0]["worker_state"] = "idle"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    worktrees["entries"][0]["status"] = "closed"
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)

    result = run_python(TASK_OPS_SCRIPT, repo, "reconcile-ledgers", "--write")

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    assert result.returncode == 0, result.stdout + result.stderr
    assert registry["tasks"][0]["status"] == "doing"
    assert registry["tasks"][0]["worker_state"] == "running"
    assert worktrees["entries"][0]["status"] == "active"


def test_prepare_child_execution_creates_workflow_state_and_baseline(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_execution_child(repo, "TASK-EXEC-018A")
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-018A"

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "prepare-child-execution",
        "TASK-EXEC-018A",
        "--path",
        str(destination),
    )

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    context = read_yaml(destination / ".codex/local/EXECUTION_CONTEXT.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-EXEC-018A")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-018A")
    assert result.returncode == 0, result.stdout + result.stderr
    assert context["parent_branch"] == "main"
    assert context["workflow_state"]["baseline_checks"]["status"] == "passed"
    assert context["workflow_state"]["phase"] == "prepared"
    assert task["status"] == "doing"
    assert task["worker_state"] == "idle"
    assert entry["status"] == "active"
    assert entry["workflow_state"]["baseline_checks"]["status"] == "passed"


def test_worker_start_requires_design_plan_and_test_first_for_code_tasks(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_execution_child(repo, "TASK-EXEC-018B")
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-018B"
    prepared = run_python(TASK_OPS_SCRIPT, repo, "prepare-child-execution", "TASK-EXEC-018B", "--path", str(destination))
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr

    blocked = run_python(TASK_OPS_SCRIPT, repo, "worker-start", "TASK-EXEC-018B", "--worker-owner", "worker-01")
    design = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-design-confirm",
        "TASK-EXEC-018B",
        "--summary",
        "code child confirmed",
        "--implementation-kind",
        "code",
    )
    plan = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-plan",
        "TASK-EXEC-018B",
        "--summary",
        "implement the code child",
        "--file",
        "scripts/example.py",
        "--step",
        "write the smallest implementation",
        "--test",
        f'python "{CHECK_REPO_SCRIPT.as_posix()}"',
        "--verify",
        "run governance baseline",
    )
    still_blocked = run_python(TASK_OPS_SCRIPT, repo, "worker-start", "TASK-EXEC-018B", "--worker-owner", "worker-01")
    test_first = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-test-first",
        "TASK-EXEC-018B",
        "--command",
        f'python "{CHECK_REPO_SCRIPT.as_posix()}"',
        "--note",
        "recorded code-task test-first gate",
    )
    started = run_python(TASK_OPS_SCRIPT, repo, "worker-start", "TASK-EXEC-018B", "--worker-owner", "worker-01")

    assert blocked.returncode == 1
    assert "design confirmation must pass" in blocked.stdout
    assert design.returncode == 0, design.stdout + design.stderr
    assert plan.returncode == 0, plan.stdout + plan.stderr
    assert still_blocked.returncode == 1
    assert "test-first evidence" in still_blocked.stdout
    assert test_first.returncode == 0, test_first.stdout + test_first.stderr
    assert started.returncode == 0, started.stdout + started.stderr


def test_quality_review_requires_spec_review_first(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_execution_child(repo, "TASK-EXEC-018C")
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-018C"
    prepared = run_python(TASK_OPS_SCRIPT, repo, "prepare-child-execution", "TASK-EXEC-018C", "--path", str(destination))
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    design = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-design-confirm",
        "TASK-EXEC-018C",
        "--summary",
        "governance child confirmed",
        "--implementation-kind",
        "governance",
    )
    plan = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-plan",
        "TASK-EXEC-018C",
        "--summary",
        "governance child plan",
        "--file",
        "docs/governance/example.md",
        "--step",
        "update the governance artifact",
        "--test",
        f'python "{CHECK_REPO_SCRIPT.as_posix()}"',
        "--verify",
        "run baseline checks",
    )
    assert design.returncode == 0, design.stdout + design.stderr
    assert plan.returncode == 0, plan.stdout + plan.stderr

    quality_first = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-quality-review",
        "TASK-EXEC-018C",
        "--status",
        "passed",
        "--summary",
        "quality looks good",
    )
    spec = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-spec-review",
        "TASK-EXEC-018C",
        "--status",
        "passed",
        "--summary",
        "scope matches the child task",
    )
    quality = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-quality-review",
        "TASK-EXEC-018C",
        "--status",
        "passed",
        "--summary",
        "quality looks good",
    )

    assert quality_first.returncode == 1
    assert "quality review cannot run before spec review passes" in quality_first.stdout
    assert spec.returncode == 0, spec.stdout + spec.stderr
    assert quality.returncode == 0, quality.stdout + quality.stderr


def _prepare_finished_governance_child(repo: Path, task_id: str, destination: Path) -> dict[str, object]:
    prepared = run_python(TASK_OPS_SCRIPT, repo, "prepare-child-execution", task_id, "--path", str(destination))
    design = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-design-confirm",
        task_id,
        "--summary",
        "governance child confirmed",
        "--implementation-kind",
        "governance",
    )
    plan = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-plan",
        task_id,
        "--summary",
        "governance child plan",
        "--file",
        "docs/governance/example.md",
        "--step",
        "update the governance artifact",
        "--test",
        f'python "{CHECK_REPO_SCRIPT.as_posix()}"',
        "--verify",
        "run governance baseline",
    )
    started = run_python(TASK_OPS_SCRIPT, repo, "worker-start", task_id, "--worker-owner", "worker-01")
    spec = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-spec-review",
        task_id,
        "--status",
        "passed",
        "--summary",
        "scope matches the child task",
    )
    quality = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-quality-review",
        task_id,
        "--status",
        "passed",
        "--summary",
        "quality looks good",
    )
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        task_id,
        "--summary",
        "child lane ready for standardized finish",
        "--tests",
        f'python "{CHECK_REPO_SCRIPT.as_posix()}"',
    )
    return {
        "prepared": prepared,
        "design": design,
        "plan": plan,
        "started": started,
        "spec": spec,
        "quality": quality,
        "finished": finished,
    }


def test_auto_close_children_merges_child_and_marks_parent_ai_guarded_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _create_execution_child(repo, "TASK-EXEC-018D")
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-018D"
    steps = _prepare_finished_governance_child(repo, "TASK-EXEC-018D", destination)
    closed = run_python(TASK_OPS_SCRIPT, repo, "auto-close-children", "TASK-BASE-001")

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    parent = next(item for item in registry["tasks"] if item["task_id"] == "TASK-BASE-001")
    child = next(item for item in registry["tasks"] if item["task_id"] == "TASK-EXEC-018D")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-018D")

    for key in ("prepared", "design", "plan", "started", "spec", "quality", "finished"):
        result = steps[key]
        assert result.returncode == 0, result.stdout + result.stderr
    assert closed.returncode == 0, closed.stdout + closed.stderr
    assert child["status"] == "done"
    assert child["review_bundle_status"] == "passed"
    assert entry["status"] == "closed"
    assert entry["cleanup_state"] == "done"
    assert parent["status"] == "doing"
    assert parent["worker_state"] == "running"
    runlog = (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").read_text(encoding="utf-8")
    assert "ai_guarded closeout candidate" in runlog
    assert "ai_guarded closeout candidate after child finish" in closed.stdout


def test_stage7_scope_uses_governed_child_workflow(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-018E",
        "--title",
        "stage7 child lane",
        "--stage",
        "stage7",
        "--branch",
        "feat/TASK-EXEC-018E",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--allowed-dirs",
        "src/stage7_sales/",
        "docs/contracts/",
        "tests/stage7/",
        "--planned-write-paths",
        "src/stage7_sales/",
        "docs/contracts/",
        "--planned-test-paths",
        "tests/stage7/",
        "--required-tests",
        f'python "{CHECK_REPO_SCRIPT.as_posix()}"',
    )
    assert created.returncode == 0, created.stdout + created.stderr
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-018E"
    prepared = run_python(TASK_OPS_SCRIPT, repo, "prepare-child-execution", "TASK-EXEC-018E", "--path", str(destination))
    blocked = run_python(TASK_OPS_SCRIPT, repo, "worker-start", "TASK-EXEC-018E", "--worker-owner", "worker-01")

    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    assert blocked.returncode == 1
    assert "design confirmation must pass" in blocked.stdout
