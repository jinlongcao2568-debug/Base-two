from __future__ import annotations

import importlib.util
from pathlib import Path


_HELPERS_PATH = Path(__file__).with_name("helpers.py")
_HELPERS_SPEC = importlib.util.spec_from_file_location("gov_helpers_for_builders", _HELPERS_PATH)
_HELPERS = importlib.util.module_from_spec(_HELPERS_SPEC)
assert _HELPERS_SPEC is not None and _HELPERS_SPEC.loader is not None
_HELPERS_SPEC.loader.exec_module(_HELPERS)

TASK_OPS_SCRIPT = _HELPERS.TASK_OPS_SCRIPT
read_yaml = _HELPERS.read_yaml
run_python = _HELPERS.run_python
write_yaml = _HELPERS.write_yaml

DEFAULT_TEST = "pytest tests/base -q"


def sync_task_artifacts(repo: Path) -> None:
    result = run_python(TASK_OPS_SCRIPT, repo, "sync", "--write")
    assert result.returncode == 0, result.stdout + result.stderr


def set_live_task_mode(
    repo: Path,
    *,
    size_class: str = "heavy",
    topology: str = "parallel_parent",
    automation_mode: str = "manual",
    required_tests: list[str] | None = None,
    lane_count: int = 1,
) -> None:
    required_tests = required_tests or [DEFAULT_TEST]
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    for task in (current_task, registry["tasks"][0]):
        task["size_class"] = size_class
        task["topology"] = topology
        task["automation_mode"] = automation_mode
        task["required_tests"] = list(required_tests)
        task["lane_count"] = lane_count
        task["lane_index"] = None
        task["parallelism_plan_id"] = f"plan-{task['task_id']}-{lane_count}" if topology == "parallel_parent" else None
        task["review_bundle_status"] = "not_applicable"
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)


def create_execution_task(
    repo: Path,
    task_id: str,
    *,
    write_path: str,
    title: str | None = None,
    stage: str = "parallel-stage",
    parent_task_id: str = "TASK-BASE-001",
    required_test: str = DEFAULT_TEST,
) -> None:
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        task_id,
        "--title",
        title or task_id.lower(),
        "--stage",
        stage,
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        parent_task_id,
        "--size-class",
        "standard",
        "--required-tests",
        required_test,
        "--planned-write-paths",
        write_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def finish_task(
    repo: Path,
    task_id: str,
    *,
    summary: str = "candidate ready",
    test: str = DEFAULT_TEST,
) -> None:
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        task_id,
        "--summary",
        summary,
        "--tests",
        test,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def create_worktree(repo: Path, tmp_path: Path, task_id: str) -> Path:
    destination = tmp_path / "repo.worktrees" / task_id
    result = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", task_id, "--path", str(destination))
    assert result.returncode == 0, result.stdout + result.stderr
    return destination


def create_review_ready_child(
    repo: Path,
    task_id: str,
    *,
    write_path: str,
    title: str | None = None,
    parent_task_id: str = "TASK-BASE-001",
    stage: str = "parallel-stage",
    required_test: str = DEFAULT_TEST,
    summary: str = "candidate ready",
    tmp_path: Path | None = None,
    with_worktree: bool = False,
    lane_count: int = 1,
    lane_index: int | None = None,
) -> None:
    create_execution_task(
        repo,
        task_id,
        write_path=write_path,
        title=title,
        stage=stage,
        parent_task_id=parent_task_id,
        required_test=required_test,
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == task_id)
    task["lane_count"] = lane_count
    task["lane_index"] = lane_index
    task["parallelism_plan_id"] = f"plan-{parent_task_id}-{lane_count}" if lane_count > 1 else None
    task["review_bundle_status"] = "not_applicable"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    sync_task_artifacts(repo)
    if with_worktree:
        assert tmp_path is not None
        create_worktree(repo, tmp_path, task_id)
    finish_task(repo, task_id, summary=summary, test=required_test)


def create_review_ready_children(
    repo: Path,
    task_ids: list[str],
    *,
    write_path_prefix: str,
    required_test: str = DEFAULT_TEST,
    summary: str = "candidate ready",
    tmp_path: Path | None = None,
    with_worktrees: bool = False,
) -> None:
    lane_count = len(task_ids)
    for index, task_id in enumerate(task_ids):
        create_review_ready_child(
            repo,
            task_id,
            write_path=f"{write_path_prefix}{index}/",
            title=f"execution {index}",
            required_test=required_test,
            summary=summary,
            tmp_path=tmp_path,
            with_worktree=with_worktrees,
            lane_count=lane_count,
            lane_index=index + 1,
        )


def execution_task_record(
    task_id: str,
    *,
    branch: str,
    allowed_dirs: list[str],
    planned_write_paths: list[str],
    planned_test_paths: list[str],
    status: str = "doing",
    size_class: str = "standard",
    automation_mode: str = "autonomous",
    worker_state: str = "running",
    topology: str = "single_worker",
    parent_task_id: str = "TASK-BASE-001",
    stage: str = "pilot",
    lane_count: int = 1,
    lane_index: int | None = None,
    parallelism_plan_id: str | None = None,
) -> dict:
    return {
        "task_id": task_id,
        "title": task_id,
        "status": status,
        "task_kind": "execution",
        "execution_mode": "isolated_worktree",
        "parent_task_id": parent_task_id,
        "stage": stage,
        "branch": branch,
        "size_class": size_class,
        "automation_mode": automation_mode,
        "worker_state": worker_state,
        "blocked_reason": None,
        "last_reported_at": "2026-04-04T00:00:00+08:00",
        "topology": topology,
        "allowed_dirs": allowed_dirs,
        "reserved_paths": [],
        "planned_write_paths": planned_write_paths,
        "planned_test_paths": planned_test_paths,
        "required_tests": [],
        "task_file": f"docs/governance/tasks/{task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
        "lane_count": lane_count,
        "lane_index": lane_index,
        "parallelism_plan_id": parallelism_plan_id,
        "review_bundle_status": "not_applicable",
        "created_at": "2026-04-04T00:00:00+08:00",
        "activated_at": "2026-04-04T00:00:00+08:00",
        "closed_at": None,
    }


def append_registry_task(repo: Path, task: dict, *, task_text: str = "# task\n", runlog_text: str = "# runlog\n") -> None:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(task)
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    (repo / task["task_file"]).write_text(task_text, encoding="utf-8")
    (repo / task["runlog_file"]).write_text(runlog_text, encoding="utf-8")


def append_worktree_entry(repo: Path, entry: dict) -> None:
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    worktrees["entries"].append(entry)
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)


def execution_worktree_entry(
    task_id: str,
    *,
    branch: str,
    path: str,
    status: str = "active",
    cleanup_state: str = "pending",
    cleanup_attempts: int = 0,
    worker_owner: str = "worker-01",
    parent_task_id: str = "TASK-BASE-001",
) -> dict:
    return {
        "task_id": task_id,
        "work_mode": "execution",
        "parent_task_id": parent_task_id,
        "branch": branch,
        "path": path,
        "status": status,
        "cleanup_state": cleanup_state,
        "cleanup_attempts": cleanup_attempts,
        "last_cleanup_error": None,
        "worker_owner": worker_owner,
        "lane_session_id": None,
        "executor_status": "completed" if status == "closed" else "prepared",
        "started_at": None,
        "last_heartbeat_at": None,
        "last_result": None,
    }


def write_execution_context(
    repo: Path,
    task_id: str,
    *,
    branch: str,
    allowed_dirs: list[str],
    planned_write_paths: list[str],
    planned_test_paths: list[str],
    required_tests: list[str] | None = None,
    parent_task_id: str = "TASK-BASE-001",
) -> None:
    write_yaml(
        repo / ".codex/local/EXECUTION_CONTEXT.yaml",
        {
            "task_id": task_id,
            "parent_task_id": parent_task_id,
            "branch": branch,
            "worktree_path": str(repo).replace("\\", "/"),
            "worker_owner": "worker-01",
            "allowed_dirs": allowed_dirs,
            "reserved_paths": [],
            "planned_write_paths": planned_write_paths,
            "planned_test_paths": planned_test_paths,
            "required_tests": required_tests or [],
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "runtime_prompt_profile": "docs/governance/runtime_prompts/worker.md",
        },
    )


def create_cleanup_orphan(repo: Path, blocked_dir: Path, *, task_id: str = "TASK-EXEC-009") -> None:
    task = execution_task_record(
        task_id,
        branch=f"feat/{task_id}",
        allowed_dirs=["src/exec9/"],
        planned_write_paths=["src/exec9/"],
        planned_test_paths=[],
        status="done",
        worker_state="completed",
    )
    task["closed_at"] = "2026-04-04T00:00:00+08:00"
    append_registry_task(repo, task)
    append_worktree_entry(
        repo,
        execution_worktree_entry(
            task_id,
            branch=f"feat/{task_id}",
            path=str(blocked_dir).replace("\\", "/"),
            status="closed",
            cleanup_attempts=0,
        ),
    )
