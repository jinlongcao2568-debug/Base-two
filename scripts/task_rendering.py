from __future__ import annotations

from pathlib import Path

from governance_lib import (
    CURRENT_TASK_FILE,
    GovernanceError,
    append_runlog_bullets,
    build_current_task_payload,
    collect_split_errors,
    display_path,
    dump_yaml,
    iso_now,
    load_current_task,
    read_roadmap,
    render_narrative_assertions_block,
    sync_task_artifacts,
    worktree_map,
    write_roadmap,
    write_text,
)


def render_list(items: list[str]) -> str:
    if not items:
        return "- 待补充"
    return "\n".join(f"- `{item}`" for item in items)


def render_task_markdown(task: dict) -> str:
    return f"""# {task['task_id']} {task['title']}

## 任务基线

- 任务编号：`{task['task_id']}`
- 任务类型：`{task['task_kind']}`
- 执行模式：`{task['execution_mode']}`
- 当前状态：`{task['status']}`
- 所属阶段：`{task['stage']}`
- 任务分支：`{task['branch']}`
- 任务大小：`{task['size_class']}`
- 自动化模式：`{task['automation_mode']}`
- 拓扑：`{task['topology']}`

## 主目标

- 待补充

## 不做什么

- 待补充

## 允许修改目录

{render_list(task.get('allowed_dirs', []))}

## 拟修改文件清单

{render_list(task.get('planned_write_paths', []))}

## planned test paths

{render_list(task.get('planned_test_paths', []))}

## reserved paths

{render_list(task.get('reserved_paths', []))}

## Narrative Assertions

{render_narrative_assertions_block(task)}
"""


def render_runlog_markdown(task: dict) -> str:
    return f"""# {task['task_id']} RUNLOG

## 任务状态

- `task_id`：`{task['task_id']}`
- `status`：`{task['status']}`
- `stage`：`{task['stage']}`
- `branch`：`{task['branch']}`
- `worker_state`：`{task['worker_state']}`

## 执行记录

- `{iso_now()}`：创建任务包

## 测试记录

- 待补充

## Narrative Assertions

{render_narrative_assertions_block(task)}
"""


def find_task(tasks: list[dict], task_id: str) -> dict:
    for task in tasks:
        if task["task_id"] == task_id:
            return task
    raise GovernanceError(f"unknown task: {task_id}")


def update_task_file(root: Path, task: dict) -> None:
    path = root / task["task_file"]
    if not path.exists():
        write_text(path, render_task_markdown(task))


def update_runlog_file(root: Path, task: dict) -> None:
    path = root / task["runlog_file"]
    if not path.exists():
        write_text(path, render_runlog_markdown(task))


def update_current_task_if_active(root: Path, task: dict, next_action: str) -> None:
    current_task = load_current_task(root)
    if current_task["current_task_id"] == task["task_id"]:
        dump_yaml(root / CURRENT_TASK_FILE, build_current_task_payload(task, next_action))


def enforce_execution_split_guards(registry: dict, task: dict) -> None:
    if task["task_kind"] != "execution" or not task.get("parent_task_id"):
        return
    siblings = [item for item in registry.get("tasks", []) if item.get("parent_task_id") == task["parent_task_id"] and item["task_kind"] == "execution"]
    errors = [message for message in collect_split_errors(siblings) if task["task_id"] in message]
    if errors:
        task["status"] = "blocked"
        task["worker_state"] = "blocked"
        task["blocked_reason"] = errors[0]
        task["last_reported_at"] = iso_now()
        raise GovernanceError(errors[0])


def pause_other_doing_tasks(tasks: list[dict], active_task_id: str) -> list[str]:
    touched_tasks = [active_task_id]
    for existing in tasks:
        if existing["status"] == "doing" and existing["task_id"] != active_task_id:
            existing["status"] = "paused"
            existing["worker_state"] = "idle"
            touched_tasks.append(existing["task_id"])
    return touched_tasks


def upsert_coordination_entry(worktrees: dict, task: dict, root: Path) -> None:
    entries = worktrees.setdefault("entries", [])
    for entry in entries:
        if entry.get("work_mode") == "coordination" and entry.get("status") == "active":
            entry["status"] = "paused"
    current_entry = worktree_map(worktrees).get(task["task_id"])
    if current_entry is None:
        entries.append({"task_id": task["task_id"], "work_mode": "coordination", "parent_task_id": task.get("parent_task_id"), "branch": task["branch"], "path": display_path(root), "status": "active", "cleanup_state": "not_needed", "cleanup_attempts": 0, "last_cleanup_error": None, "worker_owner": "coordinator"})
        return
    current_entry["status"] = "active"
    current_entry["branch"] = task["branch"]
    current_entry["path"] = display_path(root)
    current_entry["cleanup_state"] = "not_needed"
    current_entry["worker_owner"] = "coordinator"


def persist_activation_state(root: Path, registry: dict, worktrees: dict, task: dict, roadmap_frontmatter: dict, roadmap_body: str, touched_tasks: list[str]) -> None:
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(root / CURRENT_TASK_FILE, build_current_task_payload(task, "按任务包推进当前任务；如需切换，先保持工作树干净。"))
    roadmap_frontmatter["current_task_id"] = task["task_id"]
    roadmap_frontmatter["current_phase"] = task["stage"]
    write_roadmap(root, roadmap_frontmatter, roadmap_body)
    sync_task_artifacts(root, registry, touched_tasks)


def resolve_query_task(root: Path, task_id: str | None) -> tuple[dict, dict, dict]:
    from governance_lib import load_current_task, load_task_registry, load_worktree_registry

    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    resolved_id = task_id or current_task["current_task_id"]
    task = find_task(registry["tasks"], resolved_id)
    return task, registry, worktrees


def record_blocked_split(root: Path, registry: dict, task: dict) -> None:
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "任务 blocked；等待人工处理边界冲突。")
    append_runlog_bullets(root, task, "风险与阻塞", [f"`{iso_now()}`：{task['blocked_reason']}"])
    sync_task_artifacts(root, registry, [task["task_id"]])


def load_roadmap_state(root: Path) -> tuple[dict, str]:
    return read_roadmap(root)
