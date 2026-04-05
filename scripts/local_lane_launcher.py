from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

from governance_lib import EXECUTION_CONTEXT_FILE, GovernanceError, find_repo_root, load_yaml, write_text


SCRIPT_DIR = Path(__file__).resolve().parent
LAUNCH_BUNDLE_FILE = Path(".codex/local/EXECUTION_LAUNCHER_BUNDLE.md")


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return max(1, int(value))
    except ValueError:
        return default


def _task_ops(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "task_ops.py"), *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def _write_launch_bundle(
    worktree_path: Path,
    *,
    context: dict,
    prompt_text: str,
    lane_session_id: str,
    worker_id: str,
) -> None:
    rendered = [
        f"# Lane Launcher Bundle: {context['task_id']}",
        "",
        f"- `task_id`: `{context['task_id']}`",
        f"- `parent_task_id`: `{context.get('parent_task_id')}`",
        f"- `branch`: `{context['branch']}`",
        f"- `worker_owner`: `{context.get('worker_owner')}`",
        f"- `worker_id`: `{worker_id}`",
        f"- `lane_session_id`: `{lane_session_id}`",
        f"- `lane_count`: `{context.get('lane_count')}`",
        f"- `lane_index`: `{context.get('lane_index')}`",
        f"- `parallelism_plan_id`: `{context.get('parallelism_plan_id')}`",
        f"- `runtime_prompt_profile`: `{context.get('runtime_prompt_profile')}`",
        "",
        "## Allowed Dirs",
        "",
        *[f"- `{item}`" for item in context.get("allowed_dirs", [])],
        "",
        "## Planned Write Paths",
        "",
        *[f"- `{item}`" for item in context.get("planned_write_paths", [])],
        "",
        "## Planned Test Paths",
        "",
        *[f"- `{item}`" for item in context.get("planned_test_paths", [])],
        "",
        "## Required Tests",
        "",
        *[f"- `{item}`" for item in context.get("required_tests", [])],
        "",
        "## Runtime Prompt",
        "",
        prompt_text.rstrip(),
        "",
    ]
    write_text(worktree_path / LAUNCH_BUNDLE_FILE, "\n".join(rendered))


def _load_context(repo_root: Path, worktree_path: Path, task_id: str) -> tuple[dict, str]:
    context_path = worktree_path / EXECUTION_CONTEXT_FILE
    if not context_path.exists():
        raise GovernanceError(f"missing execution context: {context_path}")
    context = load_yaml(context_path) or {}
    if context.get("task_id") != task_id:
        raise GovernanceError(f"execution context task mismatch: expected {task_id}, got {context.get('task_id')}")
    prompt_path = repo_root / str(context.get("runtime_prompt_profile") or "")
    if not prompt_path.exists():
        rendered = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "render_runtime_prompts.py")],
            cwd=repo_root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if rendered.returncode != 0 or not prompt_path.exists():
            detail = rendered.stdout.strip() or rendered.stderr.strip()
            raise GovernanceError(f"missing runtime prompt profile: {prompt_path}" + (f" :: {detail}" if detail else ""))
    return context, prompt_path.read_text(encoding="utf-8")


def run_launcher(args: argparse.Namespace) -> int:
    repo_root = find_repo_root(Path(args.repo_root).resolve() if args.repo_root else None)
    worktree_path = Path(args.worktree_path).resolve()
    heartbeat_interval = args.heartbeat_interval_seconds or _env_int("AX9_LAUNCHER_HEARTBEAT_INTERVAL_SECONDS", 15)
    max_runtime = args.max_runtime_seconds or _env_int("AX9_LAUNCHER_MAX_RUNTIME_SECONDS", 300)
    context, prompt_text = _load_context(repo_root, worktree_path, args.task_id)
    lane_session_id = args.lane_session_id or f"lane-{args.task_id}-{int(time.time())}"
    _write_launch_bundle(
        worktree_path,
        context=context,
        prompt_text=prompt_text,
        lane_session_id=lane_session_id,
        worker_id=args.worker_id,
    )

    worker_owner = str(context.get("worker_owner") or "worker-01")
    started = _task_ops(repo_root, "worker-start", args.task_id, "--worker-owner", worker_owner, "--path", str(worktree_path))
    if started.returncode != 0:
        raise GovernanceError(started.stdout.strip() or started.stderr.strip() or "worker-start failed")

    first_heartbeat = _task_ops(
        repo_root,
        "worker-heartbeat",
        args.task_id,
        "--worker-id",
        args.worker_id,
        "--lane-session-id",
        lane_session_id,
        "--executor-status",
        "running",
        "--result",
        "launcher-started",
    )
    if first_heartbeat.returncode != 0:
        raise GovernanceError(first_heartbeat.stdout.strip() or first_heartbeat.stderr.strip() or "worker-heartbeat failed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch a governed local execution lane")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--worktree-path", required=True)
    parser.add_argument("--repo-root")
    parser.add_argument("--worker-id", default="worker-local-01")
    parser.add_argument("--lane-session-id")
    parser.add_argument("--heartbeat-interval-seconds", type=int)
    parser.add_argument("--max-runtime-seconds", type=int)
    args = parser.parse_args()
    try:
        return run_launcher(args)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
