from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from governance_lib import (
    GovernanceError,
    build_current_task_payload,
    current_branch,
    dump_yaml,
    effective_successor_state,
    find_repo_root,
    iso_now,
    load_capability_map,
    load_current_task,
    load_task_policy,
    load_task_registry,
    load_worktree_registry,
    read_roadmap,
    sync_task_artifacts,
    task_parallelism_plan,
    validate_task,
)
from orchestration_runtime import record_session_event, runtime_status_for_task
from task_coordination_lease import coordination_thread_id, current_session_id
from task_handoff import ensure_handoff_file
from task_rendering import (
    find_task,
    pause_other_doing_tasks,
    persist_activation_state,
    update_runlog_file,
    update_task_file,
    upsert_coordination_entry,
)


PLANNER_POLICY_FILE = Path("docs/governance/COORDINATION_PLANNER_POLICY.yaml")
CANDIDATES_DIR = Path(".codex/local/coordination_candidates")
INDEX_FILE = "index.yaml"


def load_planner_policy(root: Path) -> dict[str, Any]:
    path = root / PLANNER_POLICY_FILE
    if not path.exists():
        raise GovernanceError(f"planner policy missing: {PLANNER_POLICY_FILE}")
    from governance_runtime import load_yaml

    return load_yaml(path) or {}


def _ensure_candidates_dir(root: Path) -> Path:
    path = root / CANDIDATES_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _clear_candidate_outputs(root: Path) -> None:
    candidates_dir = _ensure_candidates_dir(root)
    for path in candidates_dir.glob("*.yaml"):
        path.unlink()


def _next_auto_task_id(tasks: list[dict[str, Any]]) -> str:
    highest = 0
    for task in tasks:
        match = re.match(r"^TASK-AUTO-(\d{3})$", task.get("task_id", ""))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"TASK-AUTO-{highest + 1:03d}"


def _boundary_complete(task: dict[str, Any]) -> bool:
    for field in ("allowed_dirs", "planned_write_paths", "planned_test_paths", "required_tests"):
        if not task.get(field):
            return False
    return True


def _dependencies_satisfied(task: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]]) -> bool:
    for dependency_id in task.get("depends_on_task_ids", []):
        dependency = tasks_by_id.get(dependency_id)
        if dependency is None or dependency.get("status") != "done":
            return False
    return True


def _serial_or_parallel(task: dict[str, Any], task_policy: dict[str, Any]) -> str:
    plan = task_parallelism_plan(task, task_policy)
    if plan["topology"] != "parallel_parent":
        return "serial"
    reserved_paths = set(task.get("reserved_paths") or [])
    write_paths = list(task.get("planned_write_paths") or [])
    if any(path in reserved_paths for path in write_paths):
        return "serial"
    return "parallel"


def _priority_score(task: dict[str, Any], roadmap_frontmatter: dict[str, Any]) -> int:
    score = 0
    if task["task_id"] == roadmap_frontmatter.get("next_recommended_task_id"):
        score += 1000
    if task.get("status") == "queued":
        score += 100
    if task.get("size_class") == "heavy":
        score += 20
    return score


def _candidate_from_existing_task(
    task: dict[str, Any],
    *,
    priority_score: int,
    task_policy: dict[str, Any],
) -> dict[str, Any]:
    serial_or_parallel = _serial_or_parallel(task, task_policy)
    child_candidates = list(task.get("child_task_ids") or [])
    return {
        "candidate_id": f"candidate-{task['task_id'].lower()}",
        "source_kind": "existing_task",
        "promotion_mode": "use_existing_task",
        "priority_score": priority_score,
        "reason": "ranked from roadmap + registry + dependency state",
        "serial_or_parallel": serial_or_parallel,
        "parent_candidate": task["task_id"] if serial_or_parallel == "parallel" else None,
        "child_candidates": child_candidates,
        "task_id": task["task_id"],
        "title": task["title"],
        "stage": task["stage"],
        "task_kind": task["task_kind"],
        "execution_mode": task["execution_mode"],
        "size_class": task["size_class"],
        "automation_mode": task["automation_mode"],
        "topology": task["topology"],
        "allowed_dirs": list(task.get("allowed_dirs") or []),
        "planned_write_paths": list(task.get("planned_write_paths") or []),
        "planned_test_paths": list(task.get("planned_test_paths") or []),
        "required_tests": list(task.get("required_tests") or []),
        "depends_on_task_ids": list(task.get("depends_on_task_ids") or []),
        "candidate_branch": task["branch"],
    }


def _autopilot_capability_open(capability_map: dict[str, Any]) -> bool:
    capability = next(
        (
            item
            for item in capability_map.get("capabilities", [])
            if item.get("capability_id") == "roadmap_autopilot_continuation"
        ),
        None,
    )
    if capability is None:
        return True
    return capability.get("status") != "implemented"


def _build_blueprint_candidate(
    registry: dict[str, Any],
    task_policy: dict[str, Any],
    capability_map: dict[str, Any],
) -> dict[str, Any] | None:
    if not _autopilot_capability_open(capability_map):
        return None
    blueprint = next(
        (
            item
            for item in task_policy.get("task_blueprints", [])
            if item.get("blueprint_id") == "roadmap_autopilot_continuation"
        ),
        None,
    )
    if blueprint is None:
        return None
    task_id = _next_auto_task_id(registry.get("tasks", []))
    branch = blueprint["branch_template"].format(task_id=task_id)
    return {
        "candidate_id": f"candidate-{task_id.lower()}",
        "source_kind": "generated_blueprint",
        "promotion_mode": "create_new_task",
        "priority_score": 50,
        "reason": "roadmap autopilot capability gap detected from capability map",
        "serial_or_parallel": "parallel" if blueprint.get("topology") == "parallel_parent" else "serial",
        "parent_candidate": task_id if blueprint.get("topology") == "parallel_parent" else None,
        "child_candidates": [],
        "task_id": task_id,
        "title": blueprint["title"],
        "stage": blueprint["stage"],
        "task_kind": blueprint["task_kind"],
        "execution_mode": blueprint["execution_mode"],
        "size_class": blueprint["size_class"],
        "automation_mode": blueprint["automation_mode"],
        "topology": blueprint["topology"],
        "allowed_dirs": list(blueprint["allowed_dirs"]),
        "planned_write_paths": list(blueprint["planned_write_paths"]),
        "planned_test_paths": list(blueprint["planned_test_paths"]),
        "required_tests": list(blueprint["required_tests"]),
        "depends_on_task_ids": [],
        "candidate_branch": branch,
    }


def _rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(candidates, key=lambda item: (-item["priority_score"], item["task_id"]))
    for index, candidate in enumerate(ordered, start=1):
        candidate["priority_rank"] = index
    return ordered


def _candidate_file(root: Path, candidate_id: str) -> Path:
    return _ensure_candidates_dir(root) / f"{candidate_id}.yaml"


def _write_candidates(root: Path, candidates: list[dict[str, Any]]) -> None:
    _clear_candidate_outputs(root)
    candidates_dir = _ensure_candidates_dir(root)
    index_payload = {
        "generated_at": iso_now(),
        "candidate_count": len(candidates),
        "candidate_ids": [candidate["candidate_id"] for candidate in candidates],
    }
    dump_yaml(candidates_dir / INDEX_FILE, index_payload)
    for candidate in candidates:
        dump_yaml(_candidate_file(root, candidate["candidate_id"]), candidate)


def build_coordination_candidates(root: Path) -> list[dict[str, Any]]:
    policy = load_planner_policy(root)
    registry = load_task_registry(root)
    task_policy = load_task_policy(root)
    capability_map = load_capability_map(root)
    current_payload = load_current_task(root)
    roadmap_frontmatter, _ = read_roadmap(root)
    tasks_by_id = {task["task_id"]: task for task in registry.get("tasks", [])}

    candidates: list[dict[str, Any]] = []
    for task in registry.get("tasks", []):
        if task.get("task_kind") != "coordination":
            continue
        if task.get("parent_task_id") is not None:
            continue
        if task.get("absorbed_by"):
            continue
        if task["task_id"] == current_payload.get("current_task_id"):
            continue
        if task.get("status") in {"done", "blocked"}:
            continue
        if effective_successor_state(task) != "immediate":
            continue
        if not _boundary_complete(task):
            continue
        if not _dependencies_satisfied(task, tasks_by_id):
            continue
        candidates.append(
            _candidate_from_existing_task(
                task,
                priority_score=_priority_score(task, roadmap_frontmatter),
                task_policy=task_policy,
            )
        )

    if not candidates and policy.get("allow_generated_blueprints_when_no_candidates", True):
        generated = _build_blueprint_candidate(registry, task_policy, capability_map)
        if generated is not None:
            candidates.append(generated)

    return _rank_candidates(candidates)


def cmd_plan_coordination(args: argparse.Namespace) -> int:
    root = find_repo_root()
    candidates = build_coordination_candidates(root)
    _write_candidates(root, candidates)
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="plan-coordination",
        mode="manual",
        writer_state="writable",
        current_task_id=load_current_task(root).get("current_task_id"),
        continue_intent=None,
        runtime_status="planning",
        safe_write=True,
        reconcile=True,
    )
    if not candidates:
        print("[OK] no coordination candidates generated")
        return 0
    print(f"[OK] generated {len(candidates)} coordination candidates")
    for candidate in candidates:
        print(
            f"[CANDIDATE] rank={candidate['priority_rank']} id={candidate['candidate_id']} "
            f"task_id={candidate['task_id']} mode={candidate['serial_or_parallel']}"
        )
    return 0


def _load_candidate(root: Path, candidate_id: str) -> dict[str, Any]:
    path = _candidate_file(root, candidate_id)
    if not path.exists():
        raise GovernanceError(f"coordination candidate missing: {candidate_id}")
    from governance_runtime import load_yaml

    return load_yaml(path) or {}


def _build_task_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    task = {
        "task_id": candidate["task_id"],
        "title": candidate["title"],
        "status": "queued",
        "task_kind": candidate["task_kind"],
        "execution_mode": candidate["execution_mode"],
        "parent_task_id": None,
        "stage": candidate["stage"],
        "branch": candidate["candidate_branch"],
        "size_class": candidate["size_class"],
        "automation_mode": candidate["automation_mode"],
        "worker_state": "idle",
        "blocked_reason": None,
        "last_reported_at": iso_now(),
        "topology": candidate["topology"],
        "allowed_dirs": list(candidate["allowed_dirs"]),
        "reserved_paths": [],
        "planned_write_paths": list(candidate["planned_write_paths"]),
        "planned_test_paths": list(candidate["planned_test_paths"]),
        "required_tests": list(candidate["required_tests"]),
        "task_file": f"docs/governance/tasks/{candidate['task_id']}.md",
        "runlog_file": f"docs/governance/runlogs/{candidate['task_id']}-RUNLOG.md",
        "lane_count": 1,
        "lane_index": None,
        "parallelism_plan_id": None,
        "review_bundle_status": "not_applicable",
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
        "depends_on_task_ids": list(candidate.get("depends_on_task_ids") or []),
    }
    validate_task(task)
    return task


def _activate_promoted_task(root: Path, registry: dict[str, Any], task: dict[str, Any]) -> None:
    if current_branch(root) != task["branch"]:
        raise GovernanceError(
            f"promote-candidate --activate requires the current branch to match `{task['branch']}`"
        )
    worktrees = load_worktree_registry(root)
    roadmap_frontmatter, roadmap_body = read_roadmap(root)
    touched_tasks = pause_other_doing_tasks(registry["tasks"], task["task_id"])
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


def cmd_promote_candidate(args: argparse.Namespace) -> int:
    root = find_repo_root()
    candidate = _load_candidate(root, args.candidate_id)
    registry = load_task_registry(root)
    tasks = registry.setdefault("tasks", [])
    existing = next((task for task in tasks if task["task_id"] == candidate["task_id"]), None)

    if candidate.get("promotion_mode") == "use_existing_task":
        if existing is None:
            raise GovernanceError(f"existing-task candidate missing registry entry: {candidate['task_id']}")
        sync_task_artifacts(root, registry, [existing["task_id"]])
        if args.activate:
            _activate_promoted_task(root, registry, existing)
        record_session_event(
            root,
            session_id=current_session_id(root),
            thread_id=coordination_thread_id(root),
            current_command="promote-candidate",
            mode="manual",
            writer_state="writable",
            current_task_id=existing["task_id"] if args.activate else load_current_task(root).get("current_task_id"),
            continue_intent=None,
            runtime_status=runtime_status_for_task(existing) if args.activate else "planning",
            safe_write=True,
            reconcile=True,
        )
        print(
            f"[OK] promoted existing candidate {args.candidate_id} task_id={existing['task_id']} "
            f"activate={str(args.activate).lower()}"
        )
        return 0

    if existing is not None:
        raise GovernanceError(f"candidate task already exists in registry: {candidate['task_id']}")

    task = _build_task_from_candidate(candidate)
    tasks.append(task)
    registry["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    update_task_file(root, task)
    update_runlog_file(root, task)
    ensure_handoff_file(root, task)
    sync_task_artifacts(root, registry, [task["task_id"]])
    if args.activate:
        _activate_promoted_task(root, registry, task)
    record_session_event(
        root,
        session_id=current_session_id(root),
        thread_id=coordination_thread_id(root),
        current_command="promote-candidate",
        mode="manual",
        writer_state="writable",
        current_task_id=task["task_id"] if args.activate else load_current_task(root).get("current_task_id"),
        continue_intent=None,
        runtime_status=runtime_status_for_task(task) if args.activate else "planning",
        safe_write=True,
        reconcile=True,
    )
    print(
        f"[OK] promoted candidate {args.candidate_id} task_id={task['task_id']} "
        f"activate={str(args.activate).lower()}"
    )
    return 0
