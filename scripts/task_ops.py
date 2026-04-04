from __future__ import annotations

import argparse
from pathlib import Path

from governance_lib import (
    CURRENT_TASK_FILE,
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    append_runlog_bullets,
    branch_exists,
    build_current_task_payload,
    choose_worker_owner,
    collect_active_execution_errors,
    collect_split_errors,
    current_branch,
    display_path,
    dump_yaml,
    ensure_clean_worktree,
    find_repo_root,
    git,
    infer_default_automation_mode,
    infer_default_topology,
    iso_now,
    load_current_task,
    load_task_registry,
    load_worktree_registry,
    missing_required_tests,
    read_roadmap,
    safe_rmtree,
    sync_task_artifacts,
    task_map,
    task_required_tests_for_matrix,
    validate_task,
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
    siblings = [
        item
        for item in registry.get("tasks", [])
        if item.get("parent_task_id") == task["parent_task_id"] and item["task_kind"] == "execution"
    ]
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
        entries.append(
            {
                "task_id": task["task_id"],
                "work_mode": "coordination",
                "parent_task_id": task.get("parent_task_id"),
                "branch": task["branch"],
                "path": display_path(root),
                "status": "active",
                "cleanup_state": "not_needed",
                "cleanup_attempts": 0,
                "last_cleanup_error": None,
                "worker_owner": "coordinator",
            }
        )
        return
    current_entry["status"] = "active"
    current_entry["branch"] = task["branch"]
    current_entry["path"] = display_path(root)
    current_entry["cleanup_state"] = "not_needed"
    current_entry["worker_owner"] = "coordinator"


def persist_activation_state(
    root: Path,
    registry: dict,
    worktrees: dict,
    task: dict,
    roadmap_frontmatter: dict,
    roadmap_body: str,
    touched_tasks: list[str],
) -> None:
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(
        root / CURRENT_TASK_FILE,
        build_current_task_payload(task, "按任务包推进当前任务；如需切换，先保持工作树干净。"),
    )
    roadmap_frontmatter["current_task_id"] = task["task_id"]
    roadmap_frontmatter["current_phase"] = task["stage"]
    write_roadmap(root, roadmap_frontmatter, roadmap_body)
    sync_task_artifacts(root, registry, touched_tasks)


def validate_worktree_create_request(root: Path, task: dict, tasks_by_id: dict, worktrees: dict, destination: Path) -> None:
    if task["task_kind"] != "execution" or task["execution_mode"] != "isolated_worktree":
        raise GovernanceError("worktree-create only supports isolated execution tasks")
    if collect_active_execution_errors(tasks_by_id, worktrees):
        raise GovernanceError("existing active execution conflicts must be resolved before creating a new worktree")
    active_count = sum(
        1
        for entry in worktrees.get("entries", [])
        if entry.get("work_mode") == "execution" and entry.get("status") == "active"
    )
    if active_count >= 2:
        raise GovernanceError("active execution worktrees already at hard limit 2")
    if destination == root.resolve() or destination.is_relative_to(root.resolve()):
        raise GovernanceError("execution worktree path must be outside the main coordination directory")


def create_worktree_checkout(root: Path, task: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if branch_exists(root, task["branch"]):
        git(root, "worktree", "add", str(destination), task["branch"])
        return
    git(root, "worktree", "add", "-b", task["branch"], str(destination), "HEAD")


def write_execution_context(destination: Path, task: dict, worker_owner: str) -> None:
    dump_yaml(
        destination / EXECUTION_CONTEXT_FILE,
        {
            "task_id": task["task_id"],
            "parent_task_id": task.get("parent_task_id"),
            "branch": task["branch"],
            "worktree_path": display_path(destination),
            "worker_owner": worker_owner,
            "allowed_dirs": task.get("allowed_dirs", []),
            "reserved_paths": task.get("reserved_paths", []),
            "planned_write_paths": task.get("planned_write_paths", []),
            "planned_test_paths": task.get("planned_test_paths", []),
            "required_tests": task.get("required_tests", []),
        },
    )


def upsert_execution_entry(worktrees: dict, task: dict, destination: Path, worker_owner: str) -> None:
    current_entry = worktree_map(worktrees).get(task["task_id"])
    if current_entry is None:
        worktrees.setdefault("entries", []).append(
            {
                "task_id": task["task_id"],
                "work_mode": "execution",
                "parent_task_id": task.get("parent_task_id"),
                "branch": task["branch"],
                "path": display_path(destination),
                "status": "active",
                "cleanup_state": "pending",
                "cleanup_attempts": 0,
                "last_cleanup_error": None,
                "worker_owner": worker_owner,
            }
        )
        return
    current_entry["work_mode"] = "execution"
    current_entry["parent_task_id"] = task.get("parent_task_id")
    current_entry["branch"] = task["branch"]
    current_entry["path"] = display_path(destination)
    current_entry["status"] = "active"
    current_entry["cleanup_state"] = "pending"
    current_entry["worker_owner"] = worker_owner


def cmd_new(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    tasks = registry.setdefault("tasks", [])
    if any(task["task_id"] == args.task_id for task in tasks):
        raise GovernanceError(f"task already exists: {args.task_id}")

    task = {
        "task_id": args.task_id,
        "title": args.title,
        "status": args.status,
        "task_kind": args.task_kind,
        "execution_mode": args.execution_mode
        or ("shared_coordination" if args.task_kind == "coordination" else "isolated_worktree"),
        "parent_task_id": args.parent_task_id,
        "stage": args.stage,
        "branch": args.branch or f"feat/{args.task_id}-work",
        "size_class": args.size_class,
        "automation_mode": args.automation_mode or "",
        "worker_state": args.worker_state,
        "blocked_reason": None,
        "last_reported_at": iso_now(),
        "topology": args.topology or "",
        "allowed_dirs": args.allowed_dirs,
        "reserved_paths": args.reserved_paths,
        "planned_write_paths": args.planned_write_paths,
        "planned_test_paths": args.planned_test_paths,
        "required_tests": args.required_tests,
        "task_file": f"docs/governance/tasks/{args.task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{args.task_id}-RUNLOG.md",
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
    }
    task["automation_mode"] = task["automation_mode"] or infer_default_automation_mode(task)
    inferred_topology, _ = infer_default_topology(task)
    task["topology"] = task["topology"] or inferred_topology
    if not task["required_tests"]:
        task["required_tests"] = task_required_tests_for_matrix(root, task)
    validate_task(task)
    tasks.append(task)
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_task_file(root, task)
    update_runlog_file(root, task)
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] created task {args.task_id}")
    return 0


def cmd_activate(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    roadmap_frontmatter, roadmap_body = read_roadmap(root)
    tasks = registry["tasks"]
    task = find_task(tasks, args.task_id)
    if task["task_kind"] != "coordination":
        raise GovernanceError("only coordination tasks can be activated in the main worktree")
    ensure_clean_worktree(root)
    branch = current_branch(root)
    if branch != task["branch"]:
        raise GovernanceError(f"branch mismatch: expected {task['branch']}, got {branch}")

    touched_tasks = pause_other_doing_tasks(tasks, task["task_id"])
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    if task["activated_at"] is None:
        task["activated_at"] = iso_now()
    registry["updated_at"] = iso_now()
    upsert_coordination_entry(worktrees, task, root)
    worktrees["updated_at"] = iso_now()
    persist_activation_state(root, registry, worktrees, task, roadmap_frontmatter, roadmap_body, touched_tasks)
    print(f"[OK] activated {task['task_id']}")
    return 0


def cmd_pause(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    task = find_task(registry["tasks"], args.task_id or current_task["current_task_id"])
    task["status"] = "paused"
    task["worker_state"] = "idle"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is not None:
        entry["status"] = "paused"
        worktrees["updated_at"] = iso_now()
        dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    if current_task["current_task_id"] == task["task_id"]:
        dump_yaml(
            root / CURRENT_TASK_FILE,
            build_current_task_payload(task, "任务已暂停；等待显式激活下一个任务。"),
        )
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] paused {task['task_id']}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    task = find_task(registry["tasks"], args.task_id or current_task["current_task_id"])
    missing = missing_required_tests(root, task)
    if missing:
        raise GovernanceError(f"required tests missing from runlog: {', '.join(missing)}")
    task["status"] = "done"
    task["worker_state"] = "completed"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    task["closed_at"] = iso_now()
    registry["updated_at"] = iso_now()
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is not None:
        entry["status"] = "closed"
        if entry["work_mode"] == "execution":
            entry["cleanup_state"] = "pending"
        worktrees["updated_at"] = iso_now()
        dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    if current_task["current_task_id"] == task["task_id"]:
        dump_yaml(root / CURRENT_TASK_FILE, build_current_task_payload(task, "等待显式切换到下一个任务"))
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] closed {task['task_id']}")
    return 0


def resolve_query_task(root: Path, task_id: str | None) -> tuple[dict, dict, dict]:
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    resolved_id = task_id or current_task["current_task_id"]
    task = find_task(registry["tasks"], resolved_id)
    return task, registry, worktrees


def cmd_can_start(args: argparse.Namespace) -> int:
    root = find_repo_root()
    task, _, worktrees = resolve_query_task(root, args.task_id)
    current = load_current_task(root)
    if task["task_id"] != current["current_task_id"]:
        raise GovernanceError("can-start only supports the live current task")
    if task["status"] in {"done", "review"}:
        raise GovernanceError("current task is not startable in done/review state")
    if current_branch(root) != task["branch"]:
        raise GovernanceError("current branch does not match the live task branch")
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is None or entry.get("status") != "active":
        raise GovernanceError("live current task does not have an active worktree entry")
    print(f"[OK] can-start {task['task_id']}")
    return 0


def cmd_can_close(args: argparse.Namespace) -> int:
    root = find_repo_root()
    task, _, _ = resolve_query_task(root, args.task_id)
    if task["status"] in {"queued", "paused", "blocked"}:
        raise GovernanceError("task cannot close from queued/paused/blocked state")
    missing = missing_required_tests(root, task)
    if missing:
        raise GovernanceError(f"required tests missing from runlog: {', '.join(missing)}")
    print(f"[OK] can-close {task['task_id']}")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    if args.write:
        sync_task_artifacts(root, registry)
        dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
        print("[OK] synced task and runlog metadata blocks")
    else:
        print("[OK] sync dry run: no files written")
    return 0


def cmd_split_check(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    tasks = [
        task
        for task in registry.get("tasks", [])
        if task.get("parent_task_id") == args.parent_task_id and task.get("task_kind") == "execution"
    ]
    errors = collect_split_errors(tasks)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    print(f"[OK] split-check passed for {args.parent_task_id}")
    return 0


def cmd_decide_topology(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    topology, reason = infer_default_topology(task)
    task["topology"] = topology
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "已更新任务拓扑；继续按当前任务包推进。")
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] {task['task_id']} topology={topology} reason={reason}")
    return 0


def cmd_worktree_create(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    tasks_by_id = task_map(registry)
    task = tasks_by_id.get(args.task_id)
    if task is None:
        raise GovernanceError(f"unknown task: {args.task_id}")
    destination = Path(args.path).resolve()
    validate_worktree_create_request(root, task, tasks_by_id, worktrees, destination)
    create_worktree_checkout(root, task, destination)
    worker_owner = args.worker_owner or choose_worker_owner(worktrees.get("entries", []))
    write_execution_context(destination, task, worker_owner)
    upsert_execution_entry(worktrees, task, destination, worker_owner)
    worktrees["updated_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] created execution worktree for {task['task_id']} at {display_path(destination)}")
    return 0


def cmd_worktree_release(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = task_map(registry).get(args.task_id)
    if task is None:
        raise GovernanceError(f"unknown task: {args.task_id}")
    entry = worktree_map(worktrees).get(args.task_id)
    if entry is None or entry.get("work_mode") != "execution":
        raise GovernanceError(f"no execution worktree registered for {args.task_id}")

    destination = Path(entry["path"]).resolve()
    if destination.exists():
        context_path = destination / EXECUTION_CONTEXT_FILE
        if context_path.exists():
            context_path.unlink()
        dirty = git(destination, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
        if dirty:
            raise GovernanceError("execution worktree has uncommitted changes; release refused")
        git(root, "worktree", "remove", str(destination))
        if destination.exists():
            safe_rmtree(destination)
    entry["status"] = "closed"
    entry["cleanup_state"] = "done"
    entry["last_cleanup_error"] = None
    worktrees["updated_at"] = iso_now()
    if task["status"] != "done":
        task["status"] = "paused"
        task["worker_state"] = "idle"
        task["last_reported_at"] = iso_now()
        registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] released execution worktree for {args.task_id}")
    return 0


def cmd_worker_start(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    try:
        enforce_execution_split_guards(registry, task)
    except GovernanceError:
        registry["updated_at"] = iso_now()
        dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
        update_current_task_if_active(root, task, "任务 blocked；等待人工处理边界冲突。")
        append_runlog_bullets(root, task, "风险与阻塞", [f"`{iso_now()}`：{task['blocked_reason']}"])
        sync_task_artifacts(root, registry, [task["task_id"]])
        raise
    task["status"] = "doing"
    task["worker_state"] = "running"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    if task["activated_at"] is None:
        task["activated_at"] = iso_now()
    entry = worktree_map(worktrees).get(task["task_id"])
    if entry is not None:
        entry["status"] = "active"
        if args.worker_owner:
            entry["worker_owner"] = args.worker_owner
        if args.path:
            entry["path"] = display_path(Path(args.path))
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    update_current_task_if_active(root, task, "worker 已接手；按当前任务包继续推进。")
    append_runlog_bullets(
        root,
        task,
        "执行记录",
        [f"`{iso_now()}`：worker-start owner=`{args.worker_owner or 'unknown'}`"],
    )
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker started {task['task_id']}")
    return 0


def cmd_worker_report(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    task["worker_state"] = "running"
    if task["status"] == "queued":
        task["status"] = "doing"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "worker 正在推进，等待进一步回报。")
    bullets = [f"`{iso_now()}`：{note}" for note in args.note]
    if bullets:
        append_runlog_bullets(root, task, "执行记录", bullets)
    if args.tests:
        append_runlog_bullets(root, task, "测试记录", [f"`{test}`" for test in args.tests])
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker reported {task['task_id']}")
    return 0


def cmd_worker_blocked(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    task["status"] = "blocked"
    task["worker_state"] = "blocked"
    task["blocked_reason"] = args.reason
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "任务已 blocked；等待人工协调或显式解阻。")
    append_runlog_bullets(
        root,
        task,
        "风险与阻塞",
        [f"`{iso_now()}`：{args.reason}"],
    )
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker blocked {task['task_id']}")
    return 0


def cmd_worker_finish(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    task = find_task(registry["tasks"], args.task_id)
    task["status"] = "review"
    task["worker_state"] = "review_pending"
    task["blocked_reason"] = None
    task["last_reported_at"] = iso_now()
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "worker 已完成候选交付；等待自动收口或评审。")
    append_runlog_bullets(
        root,
        task,
        "执行记录",
        [f"`{iso_now()}`：worker-finish `{args.summary}`"],
    )
    if args.tests:
        append_runlog_bullets(root, task, "测试记录", [f"`{test}`" for test in args.tests])
    if args.candidate_paths:
        append_runlog_bullets(root, task, "候选交付", [f"`{path}`" for path in args.candidate_paths])
    sync_task_artifacts(root, registry, [task["task_id"]])
    print(f"[OK] worker finished {task['task_id']}")
    return 0


def cmd_auto_close_children(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    closed: list[str] = []
    skipped: list[str] = []
    for task in registry.get("tasks", []):
        if task.get("parent_task_id") != args.parent_task_id or task["task_kind"] != "execution":
            continue
        if task["worker_state"] not in {"review_pending", "completed"} or task["status"] not in {"review", "doing"}:
            continue
        missing = missing_required_tests(root, task)
        if missing:
            skipped.append(f"{task['task_id']}: missing tests {', '.join(missing)}")
            continue
        task["status"] = "done"
        task["worker_state"] = "completed"
        task["closed_at"] = iso_now()
        task["last_reported_at"] = iso_now()
        entry = worktree_map(worktrees).get(task["task_id"])
        if entry is not None:
            entry["status"] = "closed"
            entry["cleanup_state"] = "pending"
        append_runlog_bullets(root, task, "关账结论", [f"`{iso_now()}`：auto-close-children 通过"])
        closed.append(task["task_id"])
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    sync_task_artifacts(root, registry, closed)
    if closed:
        print(f"[OK] auto-closed children: {', '.join(closed)}")
    else:
        print("[OK] no child tasks closed")
    for item in skipped:
        print(f"[SKIP] {item}")
    return 0


def cmd_cleanup_orphans(args: argparse.Namespace) -> int:
    root = find_repo_root()
    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    cleaned: list[str] = []
    blocked: list[str] = []
    for entry in worktrees.get("entries", []):
        if entry.get("work_mode") != "execution":
            continue
        if args.task_id and entry["task_id"] != args.task_id:
            continue
        if entry["status"] != "closed":
            continue
        if entry["cleanup_state"] not in {"pending", "blocked"}:
            continue
        entry["cleanup_attempts"] = int(entry.get("cleanup_attempts", 0)) + 1
        destination = Path(entry["path"]).resolve()
        try:
            if destination.exists():
                git(root, "worktree", "remove", "--force", str(destination))
                if destination.exists():
                    safe_rmtree(destination)
            entry["cleanup_state"] = "done"
            entry["last_cleanup_error"] = None
            cleaned.append(entry["task_id"])
        except (GovernanceError, OSError) as error:
            entry["cleanup_state"] = "blocked_manual" if entry["cleanup_attempts"] >= 3 else "blocked"
            entry["last_cleanup_error"] = str(error)
            blocked.append(f"{entry['task_id']}: {error}")
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    for task_id in cleaned:
        task = task_map(registry).get(task_id)
        if task is not None:
            append_runlog_bullets(root, task, "执行记录", [f"`{iso_now()}`：cleanup-orphans completed"])
    if cleaned:
        print(f"[OK] cleaned orphan worktrees: {', '.join(cleaned)}")
    else:
        print("[OK] no orphan worktrees cleaned")
    for item in blocked:
        print(f"[BLOCKED] {item}")
    return 0 if not blocked else 1


def add_task_lifecycle_commands(subparsers) -> None:
    new_parser = subparsers.add_parser("new")
    new_parser.add_argument("task_id")
    new_parser.add_argument("--title", required=True)
    new_parser.add_argument("--stage", required=True)
    new_parser.add_argument("--branch")
    new_parser.add_argument("--task-kind", default="coordination", choices=["coordination", "execution"])
    new_parser.add_argument("--execution-mode", choices=["shared_coordination", "isolated_worktree"])
    new_parser.add_argument("--parent-task-id")
    new_parser.add_argument("--status", default="queued", choices=["queued", "doing", "blocked", "paused", "review", "done"])
    new_parser.add_argument("--size-class", default="standard", choices=["micro", "standard", "heavy"])
    new_parser.add_argument("--automation-mode", choices=["manual", "assisted", "autonomous"])
    new_parser.add_argument("--worker-state", default="idle", choices=["idle", "running", "blocked", "review_pending", "completed"])
    new_parser.add_argument("--topology", choices=["single_task", "single_worker", "parallel_parent"])
    new_parser.add_argument("--allowed-dirs", nargs="*", default=[])
    new_parser.add_argument("--reserved-paths", nargs="*", default=[])
    new_parser.add_argument("--planned-write-paths", nargs="*", default=[])
    new_parser.add_argument("--planned-test-paths", nargs="*", default=[])
    new_parser.add_argument("--required-tests", nargs="*", default=[])
    new_parser.set_defaults(func=cmd_new)

    activate_parser = subparsers.add_parser("activate")
    activate_parser.add_argument("task_id")
    activate_parser.set_defaults(func=cmd_activate)

    pause_parser = subparsers.add_parser("pause")
    pause_parser.add_argument("task_id", nargs="?")
    pause_parser.set_defaults(func=cmd_pause)

    close_parser = subparsers.add_parser("close")
    close_parser.add_argument("task_id", nargs="?")
    close_parser.set_defaults(func=cmd_close)

    can_start_parser = subparsers.add_parser("can-start")
    can_start_parser.add_argument("task_id", nargs="?")
    can_start_parser.set_defaults(func=cmd_can_start)

    can_close_parser = subparsers.add_parser("can-close")
    can_close_parser.add_argument("task_id", nargs="?")
    can_close_parser.set_defaults(func=cmd_can_close)

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("--write", action="store_true")
    sync_parser.set_defaults(func=cmd_sync)

    split_parser = subparsers.add_parser("split-check")
    split_parser.add_argument("parent_task_id")
    split_parser.set_defaults(func=cmd_split_check)

    topology_parser = subparsers.add_parser("decide-topology")
    topology_parser.add_argument("task_id")
    topology_parser.set_defaults(func=cmd_decide_topology)


def add_worktree_commands(subparsers) -> None:
    create_parser = subparsers.add_parser("worktree-create")
    create_parser.add_argument("task_id")
    create_parser.add_argument("--path", required=True)
    create_parser.add_argument("--worker-owner", choices=["worker-a", "worker-b"])
    create_parser.set_defaults(func=cmd_worktree_create)

    release_parser = subparsers.add_parser("worktree-release")
    release_parser.add_argument("task_id")
    release_parser.set_defaults(func=cmd_worktree_release)

    cleanup_parser = subparsers.add_parser("cleanup-orphans")
    cleanup_parser.add_argument("--task-id")
    cleanup_parser.set_defaults(func=cmd_cleanup_orphans)


def add_worker_commands(subparsers) -> None:
    worker_start_parser = subparsers.add_parser("worker-start")
    worker_start_parser.add_argument("task_id")
    worker_start_parser.add_argument("--worker-owner", choices=["coordinator", "worker-a", "worker-b"])
    worker_start_parser.add_argument("--path")
    worker_start_parser.set_defaults(func=cmd_worker_start)

    worker_report_parser = subparsers.add_parser("worker-report")
    worker_report_parser.add_argument("task_id")
    worker_report_parser.add_argument("--note", action="append", default=[])
    worker_report_parser.add_argument("--tests", nargs="*", default=[])
    worker_report_parser.set_defaults(func=cmd_worker_report)

    worker_blocked_parser = subparsers.add_parser("worker-blocked")
    worker_blocked_parser.add_argument("task_id")
    worker_blocked_parser.add_argument("--reason", required=True)
    worker_blocked_parser.set_defaults(func=cmd_worker_blocked)

    worker_finish_parser = subparsers.add_parser("worker-finish")
    worker_finish_parser.add_argument("task_id")
    worker_finish_parser.add_argument("--summary", required=True)
    worker_finish_parser.add_argument("--tests", nargs="*", default=[])
    worker_finish_parser.add_argument("--candidate-paths", nargs="*", default=[])
    worker_finish_parser.set_defaults(func=cmd_worker_finish)

    auto_close_parser = subparsers.add_parser("auto-close-children")
    auto_close_parser.add_argument("parent_task_id")
    auto_close_parser.set_defaults(func=cmd_auto_close_children)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S governance task operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_task_lifecycle_commands(subparsers)
    add_worktree_commands(subparsers)
    add_worker_commands(subparsers)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
