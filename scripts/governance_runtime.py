from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

import yaml


CURRENT_TASK_FILE = Path("docs/governance/CURRENT_TASK.yaml")
TASK_REGISTRY_FILE = Path("docs/governance/TASK_REGISTRY.yaml")
WORKTREE_REGISTRY_FILE = Path("docs/governance/WORKTREE_REGISTRY.yaml")
TASK_SOURCE_REGISTRY_FILE = Path("docs/governance/TASK_SOURCE_REGISTRY.yaml")
WORKER_REGISTRY_FILE = Path("docs/governance/WORKER_REGISTRY.yaml")
ROADMAP_FILE = Path("docs/governance/DEVELOPMENT_ROADMAP.md")
MODULE_MAP_FILE = Path("docs/governance/MODULE_MAP.yaml")
TEST_MATRIX_FILE = Path("docs/governance/TEST_MATRIX.yaml")
TASK_POLICY_FILE = Path("docs/governance/TASK_POLICY.yaml")
CAPABILITY_MAP_FILE = Path("docs/governance/CAPABILITY_MAP.yaml")
CODE_HYGIENE_POLICY_FILE = Path("docs/governance/CODE_HYGIENE_POLICY.md")
EXECUTION_CONTEXT_FILE = Path(".codex/local/EXECUTION_CONTEXT.yaml")
RESERVED_PATHS = [
    "tests/integration/",
    "docs/governance/INTERFACE_CATALOG.yaml",
    "docs/governance/CURRENT_TASK.yaml",
]
STATUS_VALUES = {"queued", "doing", "blocked", "paused", "review", "done"}
CURRENT_STATUS_VALUES = STATUS_VALUES | {"idle"}
TASK_KIND_VALUES = {"coordination", "execution"}
EXECUTION_MODE_VALUES = {"shared_coordination", "isolated_worktree"}
SIZE_CLASS_VALUES = {"micro", "standard", "heavy"}
AUTOMATION_MODE_VALUES = {"manual", "assisted", "autonomous"}
WORKER_STATE_VALUES = {"idle", "running", "blocked", "review_pending", "completed"}
TOPOLOGY_VALUES = {"single_task", "single_worker", "parallel_parent"}
WORKTREE_STATUS_VALUES = {"active", "paused", "closed"}
CLEANUP_STATE_VALUES = {"not_needed", "pending", "blocked", "blocked_manual", "done"}
EXECUTION_WORKER_OWNERS = tuple(f"worker-{index:02d}" for index in range(1, 5))
WORKER_OWNER_VALUES = {"coordinator", *EXECUTION_WORKER_OWNERS}
REVIEW_BUNDLE_STATUS_VALUES = {"not_applicable", "pending", "passed", "failed"}
EXECUTOR_STATUS_VALUES = {"prepared", "launching", "running", "completed", "blocked", "timed_out", "dispatch_failed"}
DEFAULT_RUNTIME_PROMPT_PROFILE = "docs/governance/runtime_prompts/worker.md"


class GovernanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeclaredPath:
    raw: str
    normalized: str
    is_dir: bool


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def configure_utf8_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")
        except ValueError:
            continue


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


def load_task_source_registry(root: Path) -> dict[str, Any]:
    return load_yaml(root / TASK_SOURCE_REGISTRY_FILE)


def load_worker_registry(root: Path) -> dict[str, Any]:
    return load_yaml(root / WORKER_REGISTRY_FILE)


def load_module_map(root: Path) -> dict[str, Any]:
    return load_yaml(root / MODULE_MAP_FILE)


def load_test_matrix(root: Path) -> dict[str, Any]:
    return load_yaml(root / TEST_MATRIX_FILE)


def load_task_policy(root: Path) -> dict[str, Any]:
    return load_yaml(root / TASK_POLICY_FILE)


def load_capability_map(root: Path) -> dict[str, Any]:
    return load_yaml(root / CAPABILITY_MAP_FILE)


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


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
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
    lines = git(
        root,
        "-c",
        "core.quotepath=false",
        "status",
        "--porcelain",
        "--untracked-files=all",
    ).stdout.splitlines()
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


def safe_rmtree(path: Path) -> None:
    if not path.exists():
        return
    if path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)
