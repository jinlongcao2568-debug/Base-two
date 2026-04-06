from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time
import traceback

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


def _run_script_inline(repo_root: Path, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(script), *args]
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    previous_argv = sys.argv[:]
    previous_cwd = Path.cwd()
    previous_sys_path = sys.path[:]
    exit_code = 0
    try:
        os.chdir(repo_root)
        sys.argv = [str(script), *args]
        script_dir = str(script.parent)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            try:
                runpy.run_path(str(script), run_name="__main__")
            except SystemExit as exc:
                code = exc.code
                if code is None:
                    exit_code = 0
                elif isinstance(code, int):
                    exit_code = code
                else:
                    exit_code = 1
                    print(code, file=sys.stderr)
    except Exception:
        exit_code = 1
        traceback.print_exc(file=stderr_buffer)
    finally:
        os.chdir(previous_cwd)
        sys.argv = previous_argv
        sys.path[:] = previous_sys_path
    return subprocess.CompletedProcess(command, exit_code, stdout_buffer.getvalue(), stderr_buffer.getvalue())


def _task_ops(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    if os.environ.get("AX9_INLINE_GOVERNANCE_SCRIPTS") == "1":
        return _run_script_inline(repo_root, SCRIPT_DIR / "task_ops.py", *args)
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
        if os.environ.get("AX9_INLINE_GOVERNANCE_SCRIPTS") == "1":
            rendered = _run_script_inline(repo_root, SCRIPT_DIR / "render_runtime_prompts.py")
        else:
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
