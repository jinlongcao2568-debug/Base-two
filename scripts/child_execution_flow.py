from __future__ import annotations

from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any

from governance_lib import (
    CURRENT_TASK_FILE,
    ROADMAP_FILE,
    TASK_REGISTRY_FILE,
    WORKTREE_REGISTRY_FILE,
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    actual_path,
    append_runlog_bullets,
    dump_yaml,
    git,
    iso_now,
    load_yaml,
    read_text,
    safe_rmtree,
    sync_task_artifacts,
    write_text,
)

SCRIPT_ROOT = Path(__file__).resolve().parent
BASELINE_CHECKS = [
    f'python "{(SCRIPT_ROOT / "check_repo.py").as_posix()}"',
    f'python "{(SCRIPT_ROOT / "check_hygiene.py").as_posix()}"',
]
AUTHORITY_ALIGNMENT_CHECK = f'python "{(SCRIPT_ROOT / "check_authority_alignment.py").as_posix()}"'
AUTHORITY_ALIGNMENT_GUARD_FILES = (
    "README.md",
    "docs/product/AUTHORITY_SPEC.md",
    "docs/product/MVP_SCOPE.md",
    "docs/product/PRODUCT_BOUNDARIES.md",
    "docs/product/GLOSSARY.md",
    "docs/governance/README.md",
)
IMPLEMENTATION_KINDS = {"unknown", "code", "docs", "governance", "mixed"}
GATE_STATUS_VALUES = {"pending", "passed", "failed"}
PLAN_STATUS_VALUES = {"pending", "ready", "failed"}
TEST_FIRST_STATUS_VALUES = {"not_applicable", "pending", "ready", "failed"}
FINISH_STATUS_VALUES = {"pending", "ready", "blocked", "completed"}


def execution_context_path(worktree_path: Path) -> Path:
    return worktree_path / EXECUTION_CONTEXT_FILE


def execution_plan_path(worktree_path: Path) -> Path:
    return worktree_path / ".codex/local/EXECUTION_PLAN.yaml"


def test_first_path(worktree_path: Path) -> Path:
    return worktree_path / ".codex/local/TEST_FIRST.yaml"


def baseline_commands_for_worktree(worktree_path: Path) -> list[str]:
    commands = list(BASELINE_CHECKS)
    if all((worktree_path / relative).exists() for relative in AUTHORITY_ALIGNMENT_GUARD_FILES):
        commands.append(AUTHORITY_ALIGNMENT_CHECK)
    return commands


def default_child_workflow_state(
    task: dict[str, Any],
    parent_task: dict[str, Any] | None = None,
    *,
    baseline_commands: list[str] | None = None,
) -> dict[str, Any]:
    baseline_commands = list(baseline_commands or BASELINE_CHECKS)
    return {
        "phase": "preparing",
        "prepared_at": None,
        "parent_branch": parent_task.get("branch") if parent_task is not None else None,
        "baseline_checks": {
            "status": "pending",
            "commands": baseline_commands,
            "last_run_at": None,
            "results": [],
        },
        "design_confirmation": {
            "status": "pending",
            "summary": None,
            "recorded_at": None,
        },
        "execution_plan": {
            "status": "pending",
            "artifact_path": ".codex/local/EXECUTION_PLAN.yaml",
            "recorded_at": None,
        },
        "implementation": {
            "kind": task.get("implementation_kind", "unknown"),
            "test_first_status": "pending",
            "recorded_at": None,
            "commands": [],
        },
        "review": {
            "sequence": ["spec_review", "quality_review"],
            "spec_review": {
                "status": "pending",
                "summary": None,
                "recorded_at": None,
            },
            "quality_review": {
                "status": "pending",
                "summary": None,
                "recorded_at": None,
            },
        },
        "finish": {
            "status": "pending",
            "recorded_at": None,
            "merged_into_parent_at": None,
        },
    }


def ensure_child_workflow_state(
    container: dict[str, Any],
    task: dict[str, Any],
    parent_task: dict[str, Any] | None = None,
    *,
    baseline_commands: list[str] | None = None,
) -> dict[str, Any]:
    baseline_commands = list(baseline_commands or BASELINE_CHECKS)
    workflow_state = container.get("workflow_state")
    if not isinstance(workflow_state, dict):
        workflow_state = default_child_workflow_state(task, parent_task, baseline_commands=baseline_commands)
        container["workflow_state"] = workflow_state
    workflow_state.setdefault("phase", "preparing")
    workflow_state.setdefault("prepared_at", None)
    workflow_state.setdefault("parent_branch", parent_task.get("branch") if parent_task is not None else None)
    workflow_state.setdefault(
        "baseline_checks",
        {
            "status": "pending",
            "commands": baseline_commands,
            "last_run_at": None,
            "results": [],
        },
    )
    workflow_state.setdefault(
        "design_confirmation",
        {
            "status": "pending",
            "summary": None,
            "recorded_at": None,
        },
    )
    workflow_state.setdefault(
        "execution_plan",
        {
            "status": "pending",
            "artifact_path": ".codex/local/EXECUTION_PLAN.yaml",
            "recorded_at": None,
        },
    )
    implementation = workflow_state.setdefault(
        "implementation",
        {
            "kind": task.get("implementation_kind", "unknown"),
            "test_first_status": "pending",
            "recorded_at": None,
            "commands": [],
        },
    )
    implementation.setdefault("kind", task.get("implementation_kind", "unknown"))
    implementation.setdefault("test_first_status", "pending")
    implementation.setdefault("recorded_at", None)
    implementation.setdefault("commands", [])
    review = workflow_state.setdefault(
        "review",
        {
            "sequence": ["spec_review", "quality_review"],
            "spec_review": {"status": "pending", "summary": None, "recorded_at": None},
            "quality_review": {"status": "pending", "summary": None, "recorded_at": None},
        },
    )
    review.setdefault("sequence", ["spec_review", "quality_review"])
    review.setdefault("spec_review", {"status": "pending", "summary": None, "recorded_at": None})
    review.setdefault("quality_review", {"status": "pending", "summary": None, "recorded_at": None})
    workflow_state.setdefault(
        "finish",
        {
            "status": "pending",
            "recorded_at": None,
            "merged_into_parent_at": None,
        },
    )
    return workflow_state


def build_execution_context(worktree_path: Path, task: dict[str, Any], parent_task: dict[str, Any], worker_owner: str) -> dict[str, Any]:
    workflow_state = default_child_workflow_state(
        task,
        parent_task,
        baseline_commands=baseline_commands_for_worktree(worktree_path),
    )
    planned_write_paths = list(task.get("planned_write_paths", []))
    if task.get("parent_task_id") is not None and "docs/governance/" not in planned_write_paths:
        planned_write_paths = ["docs/governance/", *planned_write_paths]
    return {
        "task_id": task["task_id"],
        "parent_task_id": task.get("parent_task_id"),
        "parent_branch": parent_task["branch"],
        "branch": task["branch"],
        "worktree_path": str(worktree_path).replace("\\", "/"),
        "worker_owner": worker_owner,
        "allowed_dirs": task.get("allowed_dirs", []),
        "reserved_paths": task.get("reserved_paths", []),
        "planned_write_paths": planned_write_paths,
        "planned_test_paths": task.get("planned_test_paths", []),
        "required_tests": task.get("required_tests", []),
        "lane_count": task.get("lane_count", 1),
        "lane_index": task.get("lane_index"),
        "parallelism_plan_id": task.get("parallelism_plan_id"),
        "runtime_prompt_profile": "docs/governance/runtime_prompts/worker.md",
        "workflow_state": workflow_state,
    }


def load_execution_context(worktree_path: Path) -> dict[str, Any]:
    path = execution_context_path(worktree_path)
    if not path.exists():
        raise GovernanceError(f"missing execution context: {path}")
    return load_yaml(path) or {}


def save_execution_context(worktree_path: Path, context: dict[str, Any]) -> None:
    dump_yaml(execution_context_path(worktree_path), context)


def sync_entry_workflow_state(entry: dict[str, Any], context: dict[str, Any]) -> None:
    entry["workflow_state"] = context.get("workflow_state", {})


def mirror_governance_ledgers_to_worktree(
    root: Path,
    worktree_path: Path,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    task: dict[str, Any],
) -> None:
    dump_yaml(worktree_path / CURRENT_TASK_FILE, load_yaml(root / CURRENT_TASK_FILE))
    write_text(worktree_path / ROADMAP_FILE, read_text(root / ROADMAP_FILE))
    dump_yaml(worktree_path / TASK_REGISTRY_FILE, registry)
    dump_yaml(worktree_path / WORKTREE_REGISTRY_FILE, worktrees)
    for relative_path in {task["task_file"], task["runlog_file"]}:
        source = root / relative_path
        if source.exists():
            write_text(worktree_path / relative_path, read_text(source))


def transient_child_paths(task: dict[str, Any]) -> set[str]:
    return {
        actual_path(str(CURRENT_TASK_FILE)),
        actual_path(str(ROADMAP_FILE)),
        actual_path(str(TASK_REGISTRY_FILE)),
        actual_path(str(WORKTREE_REGISTRY_FILE)),
        actual_path(task["task_file"]),
        actual_path(task["runlog_file"]),
    }


def _status_path_from_line(line: str) -> str:
    candidate = line[3:]
    if " -> " in candidate:
        candidate = candidate.split(" -> ", 1)[1]
    return actual_path(candidate.strip('"'))


def cleanup_transient_child_artifacts(worktree_path: Path, task: dict[str, Any]) -> list[str]:
    transient_paths = transient_child_paths(task)
    status_lines = git(
        worktree_path,
        "-c",
        "core.quotepath=false",
        "status",
        "--porcelain",
        "--untracked-files=all",
    ).stdout.splitlines()
    tracked_paths: list[str] = []
    untracked_paths: list[Path] = []
    for line in status_lines:
        if not line:
            continue
        path = _status_path_from_line(line)
        if path not in transient_paths:
            continue
        if line.startswith("??"):
            untracked_paths.append(worktree_path / path)
        else:
            tracked_paths.append(path)
    if tracked_paths:
        git(worktree_path, "checkout", "--", *tracked_paths)
    for path in untracked_paths:
        if path.exists():
            safe_rmtree(path)
    remaining_lines = git(
        worktree_path,
        "-c",
        "core.quotepath=false",
        "status",
        "--porcelain",
        "--untracked-files=all",
    ).stdout.splitlines()
    dirty_paths: list[str] = []
    for line in remaining_lines:
        if not line:
            continue
        path = _status_path_from_line(line)
        if path == actual_path(str(EXECUTION_CONTEXT_FILE)) or path in transient_paths:
            continue
        dirty_paths.append(path)
    return dirty_paths


def _command_argv(command: str) -> list[str]:
    argv = shlex.split(command, posix=True)
    if not argv:
        raise GovernanceError("governance command cannot be empty")
    if any(token in {"&&", "||", "|", ";"} for token in argv):
        raise GovernanceError(f"unsupported shell syntax in governance command: {command}")
    if argv[0] == "python":
        if len(argv) == 1:
            raise GovernanceError(f"unsupported python command: {command}")
        return [sys.executable, *argv[1:]]
    if argv[0] == "pytest":
        return [sys.executable, "-m", "pytest", *argv[1:]]
    return argv


def run_shell_command(command: str, cwd: Path) -> tuple[bool, str]:
    argv = _command_argv(command)
    result = subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        capture_output=True,
        shell=False,
        encoding="utf-8",
        errors="replace",
    )
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    output = "\n".join(part for part in (stdout, stderr) if part).strip()
    return result.returncode == 0, output


def run_baseline_checks(worktree_path: Path, commands: list[str]) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    ok = True
    for command in commands:
        passed, output = run_shell_command(command, worktree_path)
        results.append({"command": command, "passed": passed, "output": output})
        ok = ok and passed
        if not passed:
            break
    return ok, results


def record_baseline_results(workflow_state: dict[str, Any], results: list[dict[str, Any]], *, passed: bool) -> None:
    baseline = workflow_state["baseline_checks"]
    baseline["status"] = "passed" if passed else "failed"
    baseline["last_run_at"] = iso_now()
    baseline["results"] = results


def set_design_confirmation(context: dict[str, Any], *, summary: str, implementation_kind: str) -> None:
    if implementation_kind not in IMPLEMENTATION_KINDS:
        raise GovernanceError(f"invalid implementation kind: {implementation_kind}")
    workflow_state = context["workflow_state"]
    workflow_state["design_confirmation"]["status"] = "passed"
    workflow_state["design_confirmation"]["summary"] = summary
    workflow_state["design_confirmation"]["recorded_at"] = iso_now()
    workflow_state["phase"] = "design_confirmed"
    workflow_state["implementation"]["kind"] = implementation_kind
    workflow_state["implementation"]["recorded_at"] = iso_now()
    if implementation_kind == "code":
        workflow_state["implementation"]["test_first_status"] = "pending"
    else:
        workflow_state["implementation"]["test_first_status"] = "not_applicable"


def set_execution_plan(
    worktree_path: Path,
    context: dict[str, Any],
    *,
    summary: str,
    files: list[str],
    steps: list[str],
    tests: list[str],
    verifications: list[str],
) -> None:
    plan_payload = {
        "task_id": context["task_id"],
        "summary": summary,
        "files": files,
        "steps": steps,
        "tests": tests,
        "verifications": verifications,
        "recorded_at": iso_now(),
    }
    dump_yaml(execution_plan_path(worktree_path), plan_payload)
    workflow_state = context["workflow_state"]
    workflow_state["execution_plan"]["status"] = "ready"
    workflow_state["execution_plan"]["recorded_at"] = plan_payload["recorded_at"]
    workflow_state["phase"] = "plan_ready"


def set_test_first(context: dict[str, Any], *, commands: list[str], note: str | None = None) -> None:
    workflow_state = context["workflow_state"]
    implementation = workflow_state["implementation"]
    if implementation.get("kind") != "code":
        raise GovernanceError("test-first gate only applies to code implementation tasks")
    if not commands:
        raise GovernanceError("at least one test-first command is required")
    implementation["test_first_status"] = "ready"
    implementation["commands"] = list(commands)
    implementation["recorded_at"] = iso_now()
    if note:
        implementation["note"] = note
    dump_yaml(test_first_path(Path(context["worktree_path"])), {"commands": commands, "note": note, "recorded_at": implementation["recorded_at"]})


def set_review_gate(context: dict[str, Any], gate_name: str, *, status: str, summary: str) -> None:
    if status not in GATE_STATUS_VALUES:
        raise GovernanceError(f"invalid review status: {status}")
    workflow_state = context["workflow_state"]
    review = workflow_state["review"]
    if gate_name == "quality_review" and review["spec_review"]["status"] != "passed":
        raise GovernanceError("quality review cannot run before spec review passes")
    gate = review[gate_name]
    gate["status"] = status
    gate["summary"] = summary
    gate["recorded_at"] = iso_now()
    workflow_state["phase"] = gate_name
    if status == "failed":
        workflow_state["finish"]["status"] = "blocked"


def validate_worker_start(context: dict[str, Any]) -> str | None:
    workflow_state = context.get("workflow_state", {})
    if workflow_state.get("baseline_checks", {}).get("status") != "passed":
        return "baseline checks must pass before worker-start"
    if workflow_state.get("design_confirmation", {}).get("status") != "passed":
        return "design confirmation must pass before worker-start"
    if workflow_state.get("execution_plan", {}).get("status") != "ready":
        return "detailed execution plan must be ready before worker-start"
    implementation = workflow_state.get("implementation", {})
    if implementation.get("kind") == "code" and implementation.get("test_first_status") != "ready":
        return "code tasks require test-first evidence before worker-start"
    return None


def validate_finish_ready(context: dict[str, Any]) -> str | None:
    workflow_state = context.get("workflow_state", {})
    implementation = workflow_state.get("implementation", {})
    if workflow_state.get("design_confirmation", {}).get("status") != "passed":
        return "finish blocked: design confirmation not passed"
    if workflow_state.get("execution_plan", {}).get("status") != "ready":
        return "finish blocked: execution plan not ready"
    if implementation.get("kind") == "code" and implementation.get("test_first_status") != "ready":
        return "finish blocked: test-first evidence missing"
    review = workflow_state.get("review", {})
    if review.get("spec_review", {}).get("status") != "passed":
        return "finish blocked: spec review not passed"
    if review.get("quality_review", {}).get("status") != "passed":
        return "finish blocked: quality review not passed"
    return None


def merge_child_into_parent(root: Path, worktree_path: Path, task: dict[str, Any], context: dict[str, Any]) -> None:
    workflow_state = context["workflow_state"]
    parent_branch = workflow_state.get("parent_branch")
    if not parent_branch:
        raise GovernanceError("missing parent branch in execution workflow state")
    child_dirty = cleanup_transient_child_artifacts(worktree_path, task)
    if child_dirty:
        raise GovernanceError("child worktree must be clean before finish merge")
    current = git(root, "branch", "--show-current").stdout.strip()
    if current != parent_branch:
        raise GovernanceError(f"parent branch mismatch: expected {parent_branch}, got {current}")
    git(root, "merge", "--no-ff", "--no-edit", task["branch"])
    git(root, "worktree", "remove", str(worktree_path))
    if worktree_path.exists():
        safe_rmtree(worktree_path)
    workflow_state["finish"]["status"] = "completed"
    workflow_state["finish"]["recorded_at"] = iso_now()
    workflow_state["finish"]["merged_into_parent_at"] = iso_now()
    workflow_state["phase"] = "child_finished"


def persist_child_workflow(
    root: Path,
    registry: dict[str, Any],
    worktrees: dict[str, Any],
    task: dict[str, Any],
    entry: dict[str, Any],
    context: dict[str, Any],
    *,
    runlog_section: str | None = None,
    bullets: list[str] | None = None,
) -> None:
    worktree_path = Path(context["worktree_path"])
    save_execution_context(worktree_path, context)
    sync_entry_workflow_state(entry, context)
    registry["updated_at"] = iso_now()
    worktrees["updated_at"] = iso_now()
    dump_yaml(root / "docs/governance/TASK_REGISTRY.yaml", registry)
    dump_yaml(root / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)
    if runlog_section and bullets:
        append_runlog_bullets(root, task, runlog_section, bullets)
    sync_task_artifacts(root, registry, [task["task_id"]])
    mirror_governance_ledgers_to_worktree(root, worktree_path, registry, worktrees, task)
