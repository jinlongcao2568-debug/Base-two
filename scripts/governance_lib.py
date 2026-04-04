from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable

import yaml


CURRENT_TASK_FILE = Path("docs/governance/CURRENT_TASK.yaml")
TASK_REGISTRY_FILE = Path("docs/governance/TASK_REGISTRY.yaml")
WORKTREE_REGISTRY_FILE = Path("docs/governance/WORKTREE_REGISTRY.yaml")
ROADMAP_FILE = Path("docs/governance/DEVELOPMENT_ROADMAP.md")
MODULE_MAP_FILE = Path("docs/governance/MODULE_MAP.yaml")
TEST_MATRIX_FILE = Path("docs/governance/TEST_MATRIX.yaml")
CODE_HYGIENE_POLICY_FILE = Path("docs/governance/CODE_HYGIENE_POLICY.md")
EXECUTION_CONTEXT_FILE = Path(".codex/local/EXECUTION_CONTEXT.yaml")
TASK_MARKER_START = "<!-- generated:task-meta:start -->"
TASK_MARKER_END = "<!-- generated:task-meta:end -->"
RUNLOG_MARKER_START = "<!-- generated:runlog-meta:start -->"
RUNLOG_MARKER_END = "<!-- generated:runlog-meta:end -->"
RESERVED_PATHS = [
    "docs/governance/",
    "tests/integration/",
    "docs/governance/INTERFACE_CATALOG.yaml",
    "docs/governance/CURRENT_TASK.yaml",
]
STATUS_VALUES = {"queued", "doing", "blocked", "paused", "review", "done"}
TASK_KIND_VALUES = {"coordination", "execution"}
EXECUTION_MODE_VALUES = {"shared_coordination", "isolated_worktree"}
SIZE_CLASS_VALUES = {"micro", "standard", "heavy"}
AUTOMATION_MODE_VALUES = {"manual", "assisted", "autonomous"}
WORKER_STATE_VALUES = {"idle", "running", "blocked", "review_pending", "completed"}
TOPOLOGY_VALUES = {"single_task", "single_worker", "parallel_parent"}
WORKTREE_STATUS_VALUES = {"active", "paused", "closed"}
WORKER_OWNER_VALUES = {"coordinator", "worker-a", "worker-b"}
CLEANUP_STATE_VALUES = {"not_needed", "pending", "blocked", "blocked_manual", "done"}


class GovernanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeclaredPath:
    raw: str
    normalized: str
    is_dir: bool


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def find_repo_root(start: Path | None = None) -> Path:
    cursor = (start or Path.cwd()).resolve()
    for candidate in (cursor, *cursor.parents):
        if (candidate / CURRENT_TASK_FILE).exists() and (candidate / TASK_REGISTRY_FILE).exists():
            return candidate
    raise GovernanceError("unable to locate governance root from current working directory")


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def dump_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=False)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def load_current_task(root: Path) -> dict[str, Any]:
    return load_yaml(root / CURRENT_TASK_FILE)


def load_task_registry(root: Path) -> dict[str, Any]:
    return load_yaml(root / TASK_REGISTRY_FILE)


def load_worktree_registry(root: Path) -> dict[str, Any]:
    return load_yaml(root / WORKTREE_REGISTRY_FILE)


def load_module_map(root: Path) -> dict[str, Any]:
    return load_yaml(root / MODULE_MAP_FILE)


def load_test_matrix(root: Path) -> dict[str, Any]:
    return load_yaml(root / TEST_MATRIX_FILE)


def task_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["task_id"]: task for task in registry.get("tasks", [])}


def worktree_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["task_id"]: entry for entry in registry.get("entries", [])}


def normalize_path(value: str | Path) -> str:
    return str(value).replace("\\", "/").rstrip("/")


def actual_path(value: str) -> str:
    return normalize_path(value).lstrip("./")


def display_path(path: Path) -> str:
    return normalize_path(path.resolve())


def declared_path(value: str) -> DeclaredPath:
    return DeclaredPath(
        raw=value,
        normalized=actual_path(value),
        is_dir=value.endswith("/") or value.endswith("\\"),
    )


def rule_matches_path(rule: DeclaredPath, path: str) -> bool:
    normalized = actual_path(path)
    if rule.is_dir:
        return normalized == rule.normalized or normalized.startswith(f"{rule.normalized}/")
    return normalized == rule.normalized


def declared_paths_overlap(left: DeclaredPath, right: DeclaredPath) -> bool:
    if left.is_dir and right.is_dir:
        return (
            left.normalized == right.normalized
            or left.normalized.startswith(f"{right.normalized}/")
            or right.normalized.startswith(f"{left.normalized}/")
        )
    if left.is_dir:
        return rule_matches_path(left, right.normalized)
    if right.is_dir:
        return rule_matches_path(right, left.normalized)
    return left.normalized == right.normalized


def path_within_declared(path: str, declared_values: Iterable[str]) -> bool:
    return any(rule_matches_path(declared_path(value), path) for value in declared_values)


def path_hits_reserved(path: str, reserved_paths: Iterable[str] | None = None) -> bool:
    values = list(reserved_paths or RESERVED_PATHS)
    return any(rule_matches_path(declared_path(value), path) for value in values)


def task_reserved_paths(task: dict[str, Any]) -> list[str]:
    declared = list(task.get("reserved_paths", []))
    return list(dict.fromkeys([*RESERVED_PATHS, *declared]))


def task_reserved_conflicts(task: dict[str, Any]) -> list[str]:
    conflicts: list[str] = []
    reserved = task_reserved_paths(task)
    for field in ("allowed_dirs", "planned_write_paths", "planned_test_paths"):
        for path in task.get(field, []):
            if path_hits_reserved(path, reserved):
                conflicts.append(f"{field} hits reserved path: {path}")
    return conflicts


def path_to_scope_root(path: str) -> str:
    normalized = actual_path(path)
    parts = normalized.split("/")
    if len(parts) >= 2 and parts[0] in {"src", "tests", "docs"}:
        return "/".join(parts[:2])
    return parts[0]


def distinct_scope_roots(paths: Iterable[str]) -> set[str]:
    return {path_to_scope_root(path) for path in paths if path}


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise GovernanceError(stderr)
    return result


def current_branch(root: Path) -> str:
    return git(root, "branch", "--show-current").stdout.strip()


def branch_exists(root: Path, branch: str) -> bool:
    return bool(git(root, "branch", "--list", branch).stdout.strip())


def git_status_paths(root: Path) -> list[str]:
    lines = git(root, "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    paths: list[str] = []
    for line in lines:
        if not line:
            continue
        candidate = line[3:]
        if " -> " in candidate:
            candidate = candidate.split(" -> ", 1)[1]
        normalized = actual_path(candidate.strip('"'))
        if normalized == actual_path(str(EXECUTION_CONTEXT_FILE)):
            continue
        paths.append(normalized)
    return paths


def ensure_clean_worktree(root: Path) -> None:
    dirty = git_status_paths(root)
    if dirty:
        raise GovernanceError(f"worktree must be clean before this command: {', '.join(dirty)}")


def read_roadmap(root: Path) -> tuple[dict[str, Any], str]:
    text = read_text(root / ROADMAP_FILE)
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise GovernanceError("roadmap front matter is missing or malformed")
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def write_roadmap(root: Path, frontmatter: dict[str, Any], body: str) -> None:
    content = f"---\n{yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()}\n---\n\n{body.lstrip()}"
    write_text(root / ROADMAP_FILE, content)


def sync_generated_block(text: str, start_marker: str, end_marker: str, block: str) -> str:
    rendered = f"{start_marker}\n{block.rstrip()}\n{end_marker}"
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(rendered, text)
    suffix = "\n\n" if text.rstrip() else ""
    return f"{text.rstrip()}{suffix}{rendered}\n"


def render_task_metadata_block(task: dict[str, Any]) -> str:
    lines = [
        "## Generated Metadata",
        "",
        f"- `status`: `{task['status']}`",
        f"- `task_kind`: `{task['task_kind']}`",
        f"- `execution_mode`: `{task['execution_mode']}`",
        f"- `size_class`: `{task['size_class']}`",
        f"- `automation_mode`: `{task['automation_mode']}`",
        f"- `worker_state`: `{task['worker_state']}`",
        f"- `topology`: `{task['topology']}`",
        f"- `reserved_paths`: `{', '.join(task.get('reserved_paths', [])) or '[]'}`",
        f"- `branch`: `{task['branch']}`",
        f"- `updated_at`: `{iso_now()}`",
    ]
    return "\n".join(lines)


def render_runlog_metadata_block(task: dict[str, Any]) -> str:
    lines = [
        "## Generated Task Snapshot",
        "",
        f"- `task_id`: `{task['task_id']}`",
        f"- `status`: `{task['status']}`",
        f"- `stage`: `{task['stage']}`",
        f"- `branch`: `{task['branch']}`",
        f"- `worker_state`: `{task['worker_state']}`",
    ]
    return "\n".join(lines)


def sync_task_artifacts(root: Path, registry: dict[str, Any], task_ids: list[str] | None = None) -> None:
    allowed_ids = set(task_ids or [])
    for task in registry.get("tasks", []):
        if allowed_ids and task["task_id"] not in allowed_ids:
            continue
        task_path = root / task["task_file"]
        runlog_path = root / task["runlog_file"]
        if task_path.exists():
            write_text(
                task_path,
                sync_generated_block(
                    read_text(task_path),
                    TASK_MARKER_START,
                    TASK_MARKER_END,
                    render_task_metadata_block(task),
                ),
            )
        if runlog_path.exists():
            write_text(
                runlog_path,
                sync_generated_block(
                    read_text(runlog_path),
                    RUNLOG_MARKER_START,
                    RUNLOG_MARKER_END,
                    render_runlog_metadata_block(task),
                ),
            )


def insert_bullets_under_section(text: str, section: str, bullets: list[str]) -> str:
    if not bullets:
        return text
    heading = f"## {section}"
    rendered = "\n".join(f"- {bullet}" for bullet in bullets).rstrip()
    if heading not in text:
        suffix = "\n\n" if text.rstrip() else ""
        return f"{text.rstrip()}{suffix}{heading}\n\n{rendered}\n"
    pattern = re.compile(rf"({re.escape(heading)}\n\n)(.*?)(\n## |\n<!-- |\Z)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        return f"{text.rstrip()}\n\n{heading}\n\n{rendered}\n"
    existing = match.group(2).rstrip()
    replacement = f"{match.group(1)}{existing}\n{rendered}{match.group(3)}"
    return text[: match.start()] + replacement + text[match.end() :]


def append_runlog_bullets(root: Path, task: dict[str, Any], section: str, bullets: list[str]) -> None:
    path = root / task["runlog_file"]
    text = read_text(path) if path.exists() else f"# {task['task_id']} RUNLOG\n"
    write_text(path, insert_bullets_under_section(text, section, bullets))


def collect_split_errors(tasks: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if len(tasks) > 2:
        errors.append("execution tasks exceed the hard limit of 2")

    for task in tasks:
        for conflict in task_reserved_conflicts(task):
            errors.append(f"{task['task_id']} {conflict}")

    for index, left in enumerate(tasks):
        left_write_rules = [declared_path(path) for path in left.get("planned_write_paths", [])]
        left_test_rules = [declared_path(path) for path in left.get("planned_test_paths", [])]
        left_reserved_rules = [declared_path(path) for path in left.get("reserved_paths", [])]
        for right in tasks[index + 1 :]:
            right_write_rules = [declared_path(path) for path in right.get("planned_write_paths", [])]
            right_test_rules = [declared_path(path) for path in right.get("planned_test_paths", [])]
            right_reserved_rules = [declared_path(path) for path in right.get("reserved_paths", [])]
            for left_rule in left_write_rules:
                for right_rule in right_write_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(
                            f"{left['task_id']} write scope overlaps {right['task_id']}: "
                            f"{left_rule.raw} <-> {right_rule.raw}"
                        )
            for left_rule in left_test_rules:
                for right_rule in right_test_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(
                            f"{left['task_id']} test scope overlaps {right['task_id']}: "
                            f"{left_rule.raw} <-> {right_rule.raw}"
                        )
            for left_rule in [*left_write_rules, *left_test_rules]:
                for right_rule in right_reserved_rules:
                    if declared_paths_overlap(left_rule, right_rule):
                        errors.append(
                            f"{left['task_id']} path overlaps {right['task_id']} reserved path: "
                            f"{left_rule.raw} <-> {right_rule.raw}"
                        )
            for right_rule in [*right_write_rules, *right_test_rules]:
                for left_rule in left_reserved_rules:
                    if declared_paths_overlap(right_rule, left_rule):
                        errors.append(
                            f"{right['task_id']} path overlaps {left['task_id']} reserved path: "
                            f"{right_rule.raw} <-> {left_rule.raw}"
                        )
    return errors


def collect_active_execution_errors(
    tasks_by_id: dict[str, dict[str, Any]],
    worktree_registry: dict[str, Any],
) -> list[str]:
    active_entries = [
        entry
        for entry in worktree_registry.get("entries", [])
        if entry.get("work_mode") == "execution" and entry.get("status") == "active"
    ]
    errors: list[str] = []
    if len(active_entries) > 2:
        errors.append("active execution worktrees exceed the hard limit of 2")

    execution_tasks: list[dict[str, Any]] = []
    for entry in active_entries:
        task = tasks_by_id.get(entry["task_id"])
        if task is None:
            errors.append(f"missing task for active worktree entry: {entry['task_id']}")
            continue
        execution_tasks.append(task)
    errors.extend(collect_split_errors(execution_tasks))
    return errors


def build_current_task_payload(task: dict[str, Any], next_action: str) -> dict[str, Any]:
    return {
        "current_task_id": task["task_id"],
        "title": task["title"],
        "status": task["status"],
        "task_kind": task["task_kind"],
        "execution_mode": task["execution_mode"],
        "parent_task_id": task.get("parent_task_id"),
        "stage": task["stage"],
        "branch": task["branch"],
        "size_class": task["size_class"],
        "automation_mode": task["automation_mode"],
        "worker_state": task["worker_state"],
        "blocked_reason": task.get("blocked_reason"),
        "last_reported_at": task.get("last_reported_at"),
        "topology": task["topology"],
        "allowed_dirs": task.get("allowed_dirs", []),
        "reserved_paths": task.get("reserved_paths", []),
        "planned_write_paths": task.get("planned_write_paths", []),
        "planned_test_paths": task.get("planned_test_paths", []),
        "required_tests": task.get("required_tests", []),
        "task_file": task["task_file"],
        "runlog_file": task["runlog_file"],
        "next_action": next_action,
        "updated_at": iso_now(),
    }


def validate_task(task: dict[str, Any]) -> None:
    required_fields = {
        "task_id",
        "title",
        "status",
        "task_kind",
        "execution_mode",
        "stage",
        "branch",
        "size_class",
        "automation_mode",
        "worker_state",
        "topology",
        "allowed_dirs",
        "reserved_paths",
        "planned_write_paths",
        "planned_test_paths",
        "required_tests",
        "task_file",
        "runlog_file",
    }
    missing = sorted(required_fields - set(task))
    if missing:
        raise GovernanceError(f"task missing required fields: {', '.join(missing)}")
    if task["status"] not in STATUS_VALUES:
        raise GovernanceError(f"invalid task status: {task['status']}")
    if task["task_kind"] not in TASK_KIND_VALUES:
        raise GovernanceError(f"invalid task kind: {task['task_kind']}")
    if task["execution_mode"] not in EXECUTION_MODE_VALUES:
        raise GovernanceError(f"invalid execution mode: {task['execution_mode']}")
    if task["size_class"] not in SIZE_CLASS_VALUES:
        raise GovernanceError(f"invalid size_class: {task['size_class']}")
    if task["automation_mode"] not in AUTOMATION_MODE_VALUES:
        raise GovernanceError(f"invalid automation_mode: {task['automation_mode']}")
    if task["worker_state"] not in WORKER_STATE_VALUES:
        raise GovernanceError(f"invalid worker_state: {task['worker_state']}")
    if task["topology"] not in TOPOLOGY_VALUES:
        raise GovernanceError(f"invalid topology: {task['topology']}")
    if task["size_class"] == "micro" and len(task.get("planned_write_paths", [])) > 8:
        raise GovernanceError("micro task exceeds planned_write_paths hard limit of 8")


def validate_worktree_entry(entry: dict[str, Any]) -> None:
    required_fields = {
        "task_id",
        "work_mode",
        "parent_task_id",
        "branch",
        "path",
        "status",
        "cleanup_state",
        "cleanup_attempts",
        "last_cleanup_error",
        "worker_owner",
    }
    missing = sorted(required_fields - set(entry))
    if missing:
        raise GovernanceError(f"worktree entry missing required fields: {', '.join(missing)}")
    if entry["status"] not in WORKTREE_STATUS_VALUES:
        raise GovernanceError(f"invalid worktree status: {entry['status']}")
    if entry["cleanup_state"] not in CLEANUP_STATE_VALUES:
        raise GovernanceError(f"invalid cleanup_state: {entry['cleanup_state']}")
    if entry["worker_owner"] not in WORKER_OWNER_VALUES:
        raise GovernanceError(f"invalid worker_owner: {entry['worker_owner']}")


def missing_required_tests(root: Path, task: dict[str, Any]) -> list[str]:
    runlog_text = read_text(root / task["runlog_file"])
    return [command for command in task.get("required_tests", []) if command not in runlog_text]


def task_required_tests_for_matrix(root: Path, task: dict[str, Any]) -> list[str]:
    matrix = load_test_matrix(root)
    module_id = task.get("module_id") or "governance_control_plane"
    module_rules = matrix.get("modules", {}).get(module_id, {})
    return list(module_rules.get(task["size_class"], {}).get("required_tests", []))


def infer_default_topology(task: dict[str, Any]) -> tuple[str, str]:
    size_class = task["size_class"]
    if size_class == "micro":
        return "single_task", "micro tasks stay in a single task context"
    if size_class == "standard":
        return "single_worker", "standard tasks default to one worker"
    if "reserved_paths" not in task:
        return "single_worker", "heavy task must declare reserved_paths before split evaluation"
    roots = distinct_scope_roots(task.get("planned_write_paths", []))
    reserved_conflicts = task_reserved_conflicts(task)
    missing_split_inputs = not task.get("planned_write_paths") or not task.get("required_tests")
    if reserved_conflicts:
        return "single_worker", "heavy task touches reserved paths and cannot auto-split"
    if missing_split_inputs:
        return "single_worker", "heavy task lacks clear write paths or required tests"
    if len(roots) >= 2:
        return "parallel_parent", "heavy task exposes multiple independent write scopes"
    return "single_worker", "heavy task lacks enough independent write scopes for safe parallelism"


def infer_default_automation_mode(task: dict[str, Any]) -> str:
    if task_reserved_conflicts(task):
        return "manual"
    topology, _ = infer_default_topology(task)
    if task["size_class"] == "heavy" and topology != "parallel_parent":
        return "manual"
    if task["size_class"] in {"micro", "standard"}:
        return "assisted"
    if task["required_tests"] and topology == "parallel_parent":
        return "autonomous"
    return "assisted"


def runner_action_gate(task: dict[str, Any]) -> dict[str, Any]:
    mode = task["automation_mode"]
    parallel = task["topology"] == "parallel_parent"
    if mode == "manual":
        return {
            "prepare_worktrees": False,
            "auto_close_children": False,
            "reason": "manual mode requires human coordination before automation actions",
        }
    if mode == "assisted":
        return {
            "prepare_worktrees": parallel,
            "auto_close_children": False,
            "reason": "assisted mode keeps automatic review and closeout disabled",
        }
    return {
        "prepare_worktrees": parallel,
        "auto_close_children": parallel,
        "reason": "autonomous mode allows parallel preparation and child closeout",
    }


def choose_worker_owner(existing_entries: list[dict[str, Any]]) -> str:
    active_owners = {
        entry.get("worker_owner")
        for entry in existing_entries
        if entry.get("status") == "active" and entry.get("worker_owner") in {"worker-a", "worker-b"}
    }
    return "worker-b" if "worker-a" in active_owners else "worker-a"


def ensure_task_and_runlog_exist(root: Path, task: dict[str, Any]) -> None:
    task_path = root / task["task_file"]
    runlog_path = root / task["runlog_file"]
    if not task_path.exists():
        raise GovernanceError(f"missing task file: {task['task_file']}")
    if not runlog_path.exists():
        raise GovernanceError(f"missing runlog file: {task['runlog_file']}")


def safe_rmtree(path: Path) -> None:
    if not path.exists():
        return
    if path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)
