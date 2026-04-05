from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from governance_lib import (
    CURRENT_TASK_FILE,
    GovernanceError,
    ROADMAP_FILE,
    TASK_REGISTRY_FILE,
    WORKTREE_REGISTRY_FILE,
    actual_path,
    append_runlog_bullets,
    current_branch,
    find_repo_root,
    git,
    git_status_paths,
    iso_now,
    is_idle_current_payload,
    load_current_task,
    load_yaml,
    missing_required_tests,
    path_within_declared,
    task_map,
)
from task_handoff import handoff_path, is_top_level_coordination_task
from task_rendering import find_task


GIT_PUBLISH_POLICY_FILE = Path("docs/governance/GIT_PUBLISH_POLICY.yaml")
PUBLISH_ACTIONS = (
    "commit-task-results",
    "push-task-branch",
    "create-task-pr",
    "publish-task-results",
)
PUSH_ACTIONS = {"push-task-branch", "create-task-pr", "publish-task-results"}
PR_ACTIONS = {"create-task-pr", "publish-task-results"}
COMMIT_ACTIONS = {"commit-task-results", "publish-task-results"}
LEDGER_SYNC_FIELDS = (
    "title",
    "status",
    "branch",
    "task_file",
    "runlog_file",
    "stage",
)


def _gh_command() -> str:
    return os.environ.get("AX9_GH_CLI", "gh")


def _gh_executable() -> str | None:
    return shutil.which(_gh_command())


def _gh_argv(*args: str) -> list[str]:
    executable = _gh_executable()
    if executable is None:
        return [_gh_command(), *args]
    suffix = Path(executable).suffix.lower()
    if suffix in {".cmd", ".bat"}:
        return ["cmd", "/c", executable, *args]
    return [executable, *args]


def _run_command(root: Path, argv: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        argv,
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise GovernanceError(stderr)
    return result


def _gh_available() -> bool:
    return _gh_executable() is not None


def _gh_authenticated(root: Path) -> bool:
    if not _gh_available():
        return False
    result = _run_command(root, _gh_argv("auth", "status"), check=False)
    return result.returncode == 0


def _origin_url(root: Path, remote: str) -> tuple[bool, str | None]:
    result = git(root, "remote", "get-url", remote, check=False)
    if result.returncode != 0:
        return False, None
    return True, result.stdout.strip() or None


def _branch_upstream_exists(root: Path) -> bool:
    result = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
    return result.returncode == 0


def _existing_pr(root: Path, branch: str) -> tuple[bool, str | None]:
    if not _gh_available() or not _gh_authenticated(root):
        return False, None
    result = _run_command(
        root,
        _gh_argv("pr", "list", "--state", "open", "--head", branch, "--json", "number,url"),
        check=False,
    )
    if result.returncode != 0:
        return False, None
    try:
        payload = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return False, None
    if not payload:
        return False, None
    first = payload[0]
    return True, first.get("url")


def _load_publish_policy(root: Path) -> dict[str, Any]:
    path = root / GIT_PUBLISH_POLICY_FILE
    if not path.exists():
        raise GovernanceError(f"git publish policy missing: {GIT_PUBLISH_POLICY_FILE}")
    return load_yaml(path) or {}


def _resolve_publish_task(root: Path, task_id: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    current_payload = load_current_task(root)
    registry = load_yaml(root / TASK_REGISTRY_FILE) or {}
    tasks_by_id = task_map(registry)
    if task_id is None:
        if is_idle_current_payload(current_payload):
            raise GovernanceError("no live current task; --task-id is required when CURRENT_TASK.yaml is idle")
        return current_payload, find_task(registry.get("tasks", []), current_payload["current_task_id"])

    task = tasks_by_id.get(task_id)
    if task is None:
        raise GovernanceError(f"unknown task: {task_id}")
    live_task_id = current_payload.get("current_task_id")
    if not is_idle_current_payload(current_payload) and live_task_id not in {None, task_id}:
        raise GovernanceError(
            f"live current task is `{live_task_id}`; explicit publish only supports the live task or idle control plane"
        )
    return current_payload, task


def _direct_governance_paths(root: Path, current_payload: dict[str, Any], task: dict[str, Any]) -> list[str]:
    paths = [
        actual_path(task["task_file"]),
        actual_path(task["runlog_file"]),
        actual_path(str(TASK_REGISTRY_FILE)),
        actual_path(str(WORKTREE_REGISTRY_FILE)),
        actual_path(str(ROADMAP_FILE)),
    ]
    if current_payload.get("current_task_id") == task["task_id"]:
        paths.append(actual_path(str(CURRENT_TASK_FILE)))
    if is_top_level_coordination_task(task):
        task_handoff = handoff_path(root, task["task_id"])
        if task_handoff.exists():
            paths.append(actual_path(task_handoff.relative_to(root)))
    deduped: list[str] = []
    for value in paths:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _classify_dirty_paths(root: Path, current_payload: dict[str, Any], task: dict[str, Any]) -> tuple[list[str], list[str]]:
    dirty_paths = git_status_paths(root)
    scope = list(task.get("planned_write_paths") or task.get("allowed_dirs") or [])
    direct_paths = set(_direct_governance_paths(root, current_payload, task))
    staged_candidate_paths: list[str] = []
    out_of_scope_paths: list[str] = []
    for path in dirty_paths:
        normalized = actual_path(path)
        if normalized in direct_paths or path_within_declared(normalized, scope):
            if normalized not in staged_candidate_paths:
                staged_candidate_paths.append(normalized)
            continue
        out_of_scope_paths.append(normalized)
    return staged_candidate_paths, out_of_scope_paths


def _ledger_blockers(root: Path, current_payload: dict[str, Any], task: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if current_payload.get("current_task_id") != task["task_id"]:
        return blockers
    for field in LEDGER_SYNC_FIELDS:
        if current_payload.get(field) != task.get(field):
            blockers.append(
                f"CURRENT_TASK.yaml field `{field}` differs from TASK_REGISTRY: "
                f"{current_payload.get(field)!r} != {task.get(field)!r}"
            )
    worktrees = load_yaml(root / WORKTREE_REGISTRY_FILE) or {}
    entry = next((item for item in worktrees.get("entries", []) if item.get("task_id") == task["task_id"]), None)
    if entry is None:
        blockers.append(f"WORKTREE_REGISTRY is missing the live task entry for `{task['task_id']}`")
    else:
        if entry.get("branch") != task["branch"]:
            blockers.append(
                f"WORKTREE_REGISTRY branch differs from TASK_REGISTRY: {entry.get('branch')!r} != {task['branch']!r}"
            )
    if current_branch(root) != task["branch"]:
        blockers.append(f"current branch does not match task branch: {current_branch(root)!r} != {task['branch']!r}")
    return blockers


def _allowed_statuses(policy: dict[str, Any]) -> set[str]:
    return set(policy.get("allowed_publish_statuses") or ["review", "done"])


def _preflight_explanation(action: str, task: dict[str, Any], blocked: bool) -> str:
    if blocked:
        return f"`{action}` is blocked for task `{task['task_id']}` until the publish gates pass."
    return f"`{action}` is ready for task `{task['task_id']}` on branch `{task['branch']}`."


def publish_preflight(root: Path, *, action: str, task_id: str | None = None) -> dict[str, Any]:
    if action not in PUBLISH_ACTIONS:
        raise GovernanceError(f"unsupported publish action: {action}")
    policy = _load_publish_policy(root)
    current_payload, task = _resolve_publish_task(root, task_id)
    staged_candidate_paths, out_of_scope_paths = _classify_dirty_paths(root, current_payload, task)
    blockers: list[str] = []
    if task["status"] not in _allowed_statuses(policy):
        blockers.append(
            f"task `{task['task_id']}` is `{task['status']}`; publish actions require one of "
            f"{', '.join(sorted(_allowed_statuses(policy)))}"
        )
    missing_tests = missing_required_tests(root, task)
    if missing_tests:
        blockers.append(f"required tests missing from runlog: {', '.join(missing_tests)}")
    blockers.extend(_ledger_blockers(root, current_payload, task))
    if out_of_scope_paths:
        blockers.append(f"dirty paths outside task publish scope: {', '.join(out_of_scope_paths)}")

    remote = policy.get("default_remote", "origin")
    base_branch = policy.get("default_base_branch", "main")
    has_remote_origin, remote_url = _origin_url(root, remote)
    gh_available = _gh_available()
    gh_authenticated = _gh_authenticated(root) if gh_available else False
    existing_pr_detected = False
    existing_pr_url = None

    if action in COMMIT_ACTIONS and not staged_candidate_paths:
        blockers.append("no task-scoped changes are available to commit")
    if action in PUSH_ACTIONS and not has_remote_origin:
        blockers.append(f"remote `{remote}` is not configured")
    if action in PR_ACTIONS:
        if task["branch"] == base_branch:
            blockers.append(f"task branch `{task['branch']}` cannot open a PR against the same base branch")
        if not has_remote_origin:
            blockers.append(f"remote `{remote}` is not configured")
        if not gh_available:
            blockers.append("GitHub CLI `gh` is not available")
        elif not gh_authenticated:
            blockers.append("GitHub CLI `gh` is not authenticated")
        else:
            existing_pr_detected, existing_pr_url = _existing_pr(root, task["branch"])
            if existing_pr_detected:
                blockers.append(f"an open PR already exists for `{task['branch']}`")

    return {
        "status": "blocked" if blockers else "ready",
        "action": action,
        "task_id": task["task_id"],
        "branch": task["branch"],
        "target_remote": remote,
        "target_remote_url": remote_url,
        "target_base_branch": base_branch,
        "blockers": blockers,
        "staged_candidate_paths": staged_candidate_paths,
        "has_remote_origin": has_remote_origin,
        "gh_available": gh_available,
        "gh_authenticated": gh_authenticated,
        "existing_pr_detected": existing_pr_detected,
        "existing_pr_url": existing_pr_url,
        "explanation": _preflight_explanation(action, task, bool(blockers)),
    }


def build_publish_readiness(root: Path) -> dict[str, Any]:
    policy = _load_publish_policy(root)
    remote = policy.get("default_remote", "origin")
    base_branch = policy.get("default_base_branch", "main")
    has_remote_origin, remote_url = _origin_url(root, remote)
    gh_available = _gh_available()
    gh_authenticated = _gh_authenticated(root) if gh_available else False
    current_payload = load_current_task(root)

    if is_idle_current_payload(current_payload):
        blockers = ["no live current task; activate a review-ready task before publishing"]
        return {
            "status": "idle",
            "task_id": None,
            "branch": current_branch(root),
            "target_remote": remote,
            "target_remote_url": remote_url,
            "target_base_branch": base_branch,
            "has_remote_origin": has_remote_origin,
            "gh_available": gh_available,
            "gh_authenticated": gh_authenticated,
            "existing_pr_detected": False,
            "task_publishable": False,
            "missing_required_tests": [],
            "blockers": blockers,
            "recommended_action": "activate a review or done task, or run publish-preflight with --task-id",
        }

    _, task = _resolve_publish_task(root, None)
    preflight_result = publish_preflight(root, action="publish-task-results", task_id=task["task_id"])
    missing_tests = missing_required_tests(root, task)

    if preflight_result["status"] == "ready":
        recommended_action = "publish-task-results"
    elif task["status"] not in _allowed_statuses(policy):
        recommended_action = "move the live task to review or done before publishing"
    elif missing_tests:
        recommended_action = "record the required tests in the runlog before publishing"
    elif not has_remote_origin:
        recommended_action = "configure the origin remote before pushing or creating a draft PR"
    elif not gh_available:
        recommended_action = "install GitHub CLI `gh` before creating a draft PR"
    elif not gh_authenticated:
        recommended_action = "authenticate GitHub CLI `gh` before creating a draft PR"
    elif preflight_result["existing_pr_detected"]:
        recommended_action = "update the existing PR instead of creating a duplicate"
    else:
        recommended_action = "resolve the publish blockers and rerun publish-preflight"

    return {
        "status": preflight_result["status"],
        "task_id": preflight_result["task_id"],
        "branch": preflight_result["branch"],
        "target_remote": preflight_result["target_remote"],
        "target_remote_url": preflight_result["target_remote_url"],
        "target_base_branch": preflight_result["target_base_branch"],
        "has_remote_origin": preflight_result["has_remote_origin"],
        "gh_available": preflight_result["gh_available"],
        "gh_authenticated": preflight_result["gh_authenticated"],
        "existing_pr_detected": preflight_result["existing_pr_detected"],
        "task_publishable": preflight_result["status"] == "ready",
        "missing_required_tests": missing_tests,
        "blockers": list(dict.fromkeys(preflight_result["blockers"])),
        "recommended_action": recommended_action,
    }


def _default_commit_message(task: dict[str, Any]) -> str:
    return f"chore(governance): publish {task['task_id']}"


def _stage_paths(root: Path, paths: list[str]) -> None:
    if not paths:
        raise GovernanceError("no paths available to stage")
    git(root, "add", "--", *paths)


def _default_pr_title(task: dict[str, Any]) -> str:
    return f"{task['task_id']}: {task['title']}"


def _default_pr_body(root: Path, task: dict[str, Any]) -> str:
    from task_handoff import build_recovery_pack

    recovery_pack, _, _ = build_recovery_pack(root, task)
    sections: list[str] = [
        f"## Task\n- `{task['task_id']}`: {task['title']}",
        "## Completed",
    ]
    completed = recovery_pack.get("completed_items") or ["to-be-filled"]
    sections.extend(f"- {item}" for item in completed)
    sections.append("\n## Remaining")
    remaining = recovery_pack.get("remaining_items") or ["to-be-filled"]
    sections.extend(f"- {item}" for item in remaining)
    sections.append("\n## Next Tests")
    next_tests = recovery_pack.get("next_tests") or list(task.get("required_tests") or []) or ["to-be-filled"]
    sections.extend(f"- `{item}`" for item in next_tests)
    return "\n".join(sections)


def _append_publish_log(root: Path, task: dict[str, Any], entry: str) -> None:
    append_runlog_bullets(root, task, "Publish Log", [f"`{iso_now()}`: {entry}"])


def _commit_task_results(
    root: Path,
    task: dict[str, Any],
    preflight_result: dict[str, Any],
    *,
    message: str | None,
) -> str:
    commit_message = message or _default_commit_message(task)
    _append_publish_log(root, task, f"commit requested message=`{commit_message}`")
    stage_paths = list(preflight_result["staged_candidate_paths"])
    runlog_path = actual_path(task["runlog_file"])
    if runlog_path not in stage_paths:
        stage_paths.append(runlog_path)
    _stage_paths(root, stage_paths)
    git(root, "commit", "-m", commit_message)
    return git(root, "rev-parse", "HEAD").stdout.strip()


def _push_task_branch(root: Path, task: dict[str, Any], *, remote: str) -> None:
    branch = task["branch"]
    if _branch_upstream_exists(root):
        git(root, "push", remote, branch)
        return
    git(root, "push", "-u", remote, branch)


def _create_task_pr(
    root: Path,
    task: dict[str, Any],
    *,
    base_branch: str,
    title: str | None,
    body: str | None,
) -> str:
    pr_title = title or _default_pr_title(task)
    pr_body = body or _default_pr_body(root, task)
    result = _run_command(
        root,
        _gh_argv(
            "pr",
            "create",
            "--draft",
            "--base",
            base_branch,
            "--head",
            task["branch"],
            "--title",
            pr_title,
            "--body",
            pr_body,
        ),
    )
    output = result.stdout.strip() or result.stderr.strip()
    for line in reversed(output.splitlines()):
        stripped = line.strip()
        if stripped.startswith("http://") or stripped.startswith("https://"):
            return stripped
    return output


def _blocked_publish_error(preflight_result: dict[str, Any]) -> GovernanceError:
    blockers = preflight_result.get("blockers") or ["publish preflight blocked"]
    return GovernanceError("; ".join(blockers))


def cmd_publish_preflight(args: argparse.Namespace) -> int:
    root = find_repo_root()
    result = publish_preflight(root, action=args.action, task_id=args.task_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_commit_task_results(args: argparse.Namespace) -> int:
    root = find_repo_root()
    preflight_result = publish_preflight(root, action="commit-task-results", task_id=args.task_id)
    if preflight_result["status"] != "ready":
        raise _blocked_publish_error(preflight_result)
    _, task = _resolve_publish_task(root, args.task_id)
    commit_hash = _commit_task_results(root, task, preflight_result, message=args.message)
    print(f"[OK] committed {task['task_id']} hash={commit_hash}")
    return 0


def cmd_push_task_branch(args: argparse.Namespace) -> int:
    root = find_repo_root()
    preflight_result = publish_preflight(root, action="push-task-branch", task_id=args.task_id)
    if preflight_result["status"] != "ready":
        raise _blocked_publish_error(preflight_result)
    _, task = _resolve_publish_task(root, args.task_id)
    _push_task_branch(root, task, remote=preflight_result["target_remote"])
    print(f"[OK] pushed {task['branch']} to {preflight_result['target_remote']}")
    return 0


def cmd_create_task_pr(args: argparse.Namespace) -> int:
    root = find_repo_root()
    preflight_result = publish_preflight(root, action="create-task-pr", task_id=args.task_id)
    if preflight_result["status"] != "ready":
        raise _blocked_publish_error(preflight_result)
    _, task = _resolve_publish_task(root, args.task_id)
    _push_task_branch(root, task, remote=preflight_result["target_remote"])
    pr_url = _create_task_pr(
        root,
        task,
        base_branch=args.base_branch or preflight_result["target_base_branch"],
        title=args.title,
        body=args.body,
    )
    print(f"[OK] created draft PR {pr_url}")
    return 0


def cmd_publish_task_results(args: argparse.Namespace) -> int:
    root = find_repo_root()
    preflight_result = publish_preflight(root, action="publish-task-results", task_id=args.task_id)
    if preflight_result["status"] != "ready":
        raise _blocked_publish_error(preflight_result)
    _, task = _resolve_publish_task(root, args.task_id)
    commit_hash = _commit_task_results(root, task, preflight_result, message=args.message)
    try:
        _push_task_branch(root, task, remote=preflight_result["target_remote"])
    except GovernanceError as error:
        raise GovernanceError(f"publish stopped after commit `{commit_hash}`: {error}") from error
    try:
        pr_url = _create_task_pr(
            root,
            task,
            base_branch=args.base_branch or preflight_result["target_base_branch"],
            title=args.title,
            body=args.body,
        )
    except GovernanceError as error:
        raise GovernanceError(
            f"publish stopped after commit `{commit_hash}` and push to `{preflight_result['target_remote']}`: {error}"
        ) from error
    print(
        f"[OK] published {task['task_id']} commit={commit_hash} "
        f"remote={preflight_result['target_remote']} pr={pr_url}"
    )
    return 0
