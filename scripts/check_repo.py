from __future__ import annotations

import yaml

from governance_lib import (
    CURRENT_TASK_FILE,
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    WORKER_STATE_VALUES,
    collect_active_execution_errors,
    current_branch,
    ensure_task_and_runlog_exist,
    find_repo_root,
    git_status_paths,
    load_current_task,
    load_task_registry,
    load_worktree_registry,
    path_hits_reserved,
    path_within_declared,
    task_map,
    validate_task,
    validate_worktree_entry,
)


def validate_registry_entries(root, registry: dict, worktrees: dict) -> None:
    for task in registry.get("tasks", []):
        validate_task(task)
        ensure_task_and_runlog_exist(root, task)
    for entry in worktrees.get("entries", []):
        validate_worktree_entry(entry)


def resolve_execution_context_task(root, tasks_by_id: dict, execution_context_path):
    context = yaml.safe_load(execution_context_path.read_text(encoding="utf-8"))
    task = tasks_by_id.get(context["task_id"])
    if task is None:
        raise GovernanceError(f"execution context task missing from registry: {context['task_id']}")
    if task["task_kind"] != "execution":
        raise GovernanceError("execution context points to a non-execution task")
    branch = current_branch(root)
    if branch != context["branch"]:
        raise GovernanceError(f"branch mismatch: expected {context['branch']}, got {branch}")
    return task, context.get("allowed_dirs", []), context.get("planned_write_paths", [])


def resolve_current_task(root, tasks_by_id: dict):
    current_task = load_current_task(root)
    task = tasks_by_id.get(current_task["current_task_id"])
    if task is None:
        raise GovernanceError(f"current task missing from registry: {current_task['current_task_id']}")
    comparisons = {
        "current_task_id": "task_id",
        "title": "title",
        "status": "status",
        "task_kind": "task_kind",
        "execution_mode": "execution_mode",
        "stage": "stage",
        "branch": "branch",
        "size_class": "size_class",
        "automation_mode": "automation_mode",
        "worker_state": "worker_state",
        "topology": "topology",
        "reserved_paths": "reserved_paths",
    }
    for current_key, registry_key in comparisons.items():
        if current_task[current_key] != task[registry_key]:
            raise GovernanceError(f"current task mismatch for field {current_key}")
    if task["worker_state"] not in WORKER_STATE_VALUES:
        raise GovernanceError(f"invalid worker_state in current task: {task['worker_state']}")
    branch = current_branch(root)
    if branch != current_task["branch"]:
        raise GovernanceError(f"branch mismatch: expected {current_task['branch']}, got {branch}")
    return task, current_task.get("allowed_dirs", []), current_task.get("planned_write_paths", [])


def resolve_active_task(root, tasks_by_id: dict):
    execution_context_path = root / EXECUTION_CONTEXT_FILE
    if execution_context_path.exists():
        task, allowed_dirs, planned_write_paths = resolve_execution_context_task(
            root,
            tasks_by_id,
            execution_context_path,
        )
        return task, allowed_dirs, planned_write_paths, True
    task, allowed_dirs, planned_write_paths = resolve_current_task(root, tasks_by_id)
    return task, allowed_dirs, planned_write_paths, False


def validate_modified_paths(
    active_task: dict,
    modified_paths: list[str],
    allowed_dirs: list[str],
    planned_write_paths: list[str],
    in_execution_context: bool,
) -> None:
    if active_task["status"] in {"done", "review"} and modified_paths:
        raise GovernanceError("implementation changes are not allowed when task status is done/review")
    for path in modified_paths:
        if not path_within_declared(path, allowed_dirs):
            raise GovernanceError(f"modified path outside allowed_dirs: {path}")
        if not path_within_declared(path, planned_write_paths):
            raise GovernanceError(f"modified path outside planned_write_paths: {path}")
        if in_execution_context and path_hits_reserved(path, active_task.get("reserved_paths", [])):
            raise GovernanceError(f"execution worktree cannot touch task reserved path: {path}")
        if in_execution_context and path_hits_reserved(path):
            raise GovernanceError(f"execution worktree cannot touch reserved path: {path}")


def main() -> int:
    try:
        root = find_repo_root()
        registry = load_task_registry(root)
        tasks_by_id = task_map(registry)
        worktrees = load_worktree_registry(root)
        validate_registry_entries(root, registry, worktrees)
        active_task, allowed_dirs, planned_write_paths, in_execution_context = resolve_active_task(root, tasks_by_id)
        modified_paths = git_status_paths(root)
        validate_modified_paths(
            active_task,
            modified_paths,
            allowed_dirs,
            planned_write_paths,
            in_execution_context,
        )

        active_errors = collect_active_execution_errors(tasks_by_id, worktrees)
        if active_errors:
            raise GovernanceError(active_errors[0])
        print("[OK] governance checks passed")
        return 0
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
