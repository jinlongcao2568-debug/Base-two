from __future__ import annotations

from pathlib import Path

from governance_lib import (
    CURRENT_TASK_FILE,
    GovernanceError,
    append_runlog_bullets,
    build_current_task_payload,
    build_idle_current_task_payload,
    collect_split_errors,
    display_path,
    dump_yaml,
    iso_now,
    load_current_task,
    read_roadmap,
    render_narrative_assertions_block,
    sync_named_section,
    sync_task_artifacts,
    worktree_map,
    write_roadmap,
    write_text,
)


def render_list(items: list[str]) -> str:
    if not items:
        return "- to-be-filled"
    return "\n".join(f"- `{item}`" for item in items)


def render_optional_section(heading: str, items: list[str] | None) -> str:
    if not items:
        return ""
    return f"\n## {heading}\n\n{render_list(items)}\n"


def render_scalar(value) -> str:
    return "null" if value is None else str(value)


def render_task_markdown(task: dict) -> str:
    return f"""# {task['task_id']} {task['title']}

## Task Baseline

- `task_id`: `{task['task_id']}`
- `task_kind`: `{task['task_kind']}`
- `execution_mode`: `{task['execution_mode']}`
- `status`: `{task['status']}`
- `stage`: `{task['stage']}`
- `branch`: `{task['branch']}`
- `size_class`: `{task['size_class']}`
- `automation_mode`: `{task['automation_mode']}`
- `worker_state`: `{task['worker_state']}`
- `topology`: `{task['topology']}`
- `lane_count`: `{render_scalar(task.get('lane_count', 1))}`
- `lane_index`: `{render_scalar(task.get('lane_index'))}`
- `parallelism_plan_id`: `{render_scalar(task.get('parallelism_plan_id'))}`
- `review_bundle_status`: `{render_scalar(task.get('review_bundle_status', 'not_applicable'))}`

## Primary Goals

- to-be-filled

## Explicitly Not Doing

- to-be-filled

## Allowed Dirs

{render_list(task.get('allowed_dirs', []))}

## Planned Write Paths

{render_list(task.get('planned_write_paths', []))}

## Planned Test Paths

{render_list(task.get('planned_test_paths', []))}

## Required Tests

{render_list(task.get('required_tests', []))}

## Reserved Paths

{render_list(task.get('reserved_paths', []))}{render_optional_section('Authority Inputs', task.get('authority_inputs'))}{render_optional_section('Contract Inputs', task.get('contract_inputs'))}{render_optional_section('Module Scope', task.get('module_scope'))}{render_optional_section('Review Policy', task.get('review_policy'))}
## Narrative Assertions

{render_narrative_assertions_block(task)}
"""


def render_runlog_markdown(task: dict) -> str:
    return f"""# {task['task_id']} RUNLOG

## Task Status

- `task_id`: `{task['task_id']}`
- `status`: `{task['status']}`
- `stage`: `{task['stage']}`
- `branch`: `{task['branch']}`
- `worker_state`: `{task['worker_state']}`
- `lane_count`: `{render_scalar(task.get('lane_count', 1))}`
- `lane_index`: `{render_scalar(task.get('lane_index'))}`
- `parallelism_plan_id`: `{render_scalar(task.get('parallelism_plan_id'))}`
- `review_bundle_status`: `{render_scalar(task.get('review_bundle_status', 'not_applicable'))}`

## Execution Log

- `{iso_now()}`: task package created

## Test Log

- to-be-filled

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
    if current_task.get("current_task_id") == task["task_id"]:
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
    roadmap_body = sync_named_section(
        roadmap_body,
        "## Current Task",
        f"- `{task['task_id']}`: `{task['title']}` is the live coordination task for `{task['stage']}`.",
    )
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(
        root / CURRENT_TASK_FILE,
        build_current_task_payload(
            task,
            "Implement the live task package and keep branch/control-plane state aligned.",
        ),
    )
    roadmap_frontmatter["current_task_id"] = task["task_id"]
    roadmap_frontmatter["current_phase"] = task["stage"]
    write_roadmap(root, roadmap_frontmatter, roadmap_body)
    sync_task_artifacts(root, registry, touched_tasks)


def persist_idle_state(
    root: Path,
    registry: dict,
    worktrees: dict,
    roadmap_frontmatter: dict,
    roadmap_body: str,
    touched_tasks: list[str],
    next_action: str = "wait_for_successor_or_explicit_activation",
) -> None:
    roadmap_body = sync_named_section(
        roadmap_body,
        "## Current Task",
        "- no live current task; waiting for explicit activation or roadmap continuation.",
    )
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    dump_yaml(root / CURRENT_TASK_FILE, build_idle_current_task_payload(next_action))
    roadmap_frontmatter["current_task_id"] = None
    roadmap_frontmatter["current_phase"] = "idle"
    write_roadmap(root, roadmap_frontmatter, roadmap_body)
    sync_task_artifacts(root, registry, touched_tasks)


def resolve_query_task(root: Path, task_id: str | None) -> tuple[dict, dict, dict]:
    from governance_lib import load_current_task, load_task_registry, load_worktree_registry

    registry = load_task_registry(root)
    worktrees = load_worktree_registry(root)
    current_task = load_current_task(root)
    if task_id is None and current_task.get("current_task_id") is None:
        raise GovernanceError("no live current task; task_id is required")
    resolved_id = task_id or current_task["current_task_id"]
    task = find_task(registry["tasks"], resolved_id)
    return task, registry, worktrees


def record_blocked_split(root: Path, registry: dict, task: dict) -> None:
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_current_task_if_active(root, task, "Task blocked; waiting for manual scope-conflict resolution.")
    append_runlog_bullets(root, task, "Risk and Blockers", [f"`{iso_now()}`: {task['blocked_reason']}"])
    sync_task_artifacts(root, registry, [task["task_id"]])


def load_roadmap_state(root: Path) -> tuple[dict, str]:
    return read_roadmap(root)
