from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import importlib.util
import runpy
import traceback
from typing import Any

import yaml

try:
    from .automation_fixture_payloads import automation_intents_payload
    from .fixture_payloads import (
        base_runlog_markdown,
        base_task_markdown,
        base_task_payload,
        capability_map_payload,
        module_map_payload,
        roadmap_text,
        task_policy_payload,
        test_matrix_payload,
    )
    from .governance_fixture_docs import (
        write_coordination_planner_policy,
        write_git_publish_policy,
        write_handoff_policy,
        write_live_governance_boundary,
        write_prompt_governance_files,
    )
    from .runtime_fixture_payloads import task_source_registry_payload, worker_registry_payload
except ImportError:
    _AUTOMATION_FIXTURE_PATH = Path(__file__).with_name("automation_fixture_payloads.py")
    _AUTOMATION_FIXTURE_SPEC = importlib.util.spec_from_file_location(
        "gov_automation_fixture_payloads", _AUTOMATION_FIXTURE_PATH
    )
    _AUTOMATION_FIXTURE_MODULE = importlib.util.module_from_spec(_AUTOMATION_FIXTURE_SPEC)
    assert _AUTOMATION_FIXTURE_SPEC is not None and _AUTOMATION_FIXTURE_SPEC.loader is not None
    _AUTOMATION_FIXTURE_SPEC.loader.exec_module(_AUTOMATION_FIXTURE_MODULE)
    automation_intents_payload = _AUTOMATION_FIXTURE_MODULE.automation_intents_payload
    _FIXTURE_PATH = Path(__file__).with_name("fixture_payloads.py")
    _FIXTURE_SPEC = importlib.util.spec_from_file_location("gov_fixture_payloads", _FIXTURE_PATH)
    _FIXTURE_MODULE = importlib.util.module_from_spec(_FIXTURE_SPEC)
    assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
    _FIXTURE_SPEC.loader.exec_module(_FIXTURE_MODULE)
    base_runlog_markdown = _FIXTURE_MODULE.base_runlog_markdown
    base_task_markdown = _FIXTURE_MODULE.base_task_markdown
    base_task_payload = _FIXTURE_MODULE.base_task_payload
    capability_map_payload = _FIXTURE_MODULE.capability_map_payload
    module_map_payload = _FIXTURE_MODULE.module_map_payload
    roadmap_text = _FIXTURE_MODULE.roadmap_text
    task_policy_payload = _FIXTURE_MODULE.task_policy_payload
    test_matrix_payload = _FIXTURE_MODULE.test_matrix_payload
    _GOV_DOCS_PATH = Path(__file__).with_name("governance_fixture_docs.py")
    _GOV_DOCS_SPEC = importlib.util.spec_from_file_location("gov_fixture_docs", _GOV_DOCS_PATH)
    _GOV_DOCS_MODULE = importlib.util.module_from_spec(_GOV_DOCS_SPEC)
    assert _GOV_DOCS_SPEC is not None and _GOV_DOCS_SPEC.loader is not None
    _GOV_DOCS_SPEC.loader.exec_module(_GOV_DOCS_MODULE)
    write_coordination_planner_policy = _GOV_DOCS_MODULE.write_coordination_planner_policy
    write_git_publish_policy = _GOV_DOCS_MODULE.write_git_publish_policy
    write_handoff_policy = _GOV_DOCS_MODULE.write_handoff_policy
    write_live_governance_boundary = _GOV_DOCS_MODULE.write_live_governance_boundary
    write_prompt_governance_files = _GOV_DOCS_MODULE.write_prompt_governance_files
    _RUNTIME_FIXTURE_PATH = Path(__file__).with_name("runtime_fixture_payloads.py")
    _RUNTIME_FIXTURE_SPEC = importlib.util.spec_from_file_location("gov_runtime_fixture_payloads", _RUNTIME_FIXTURE_PATH)
    _RUNTIME_FIXTURE_MODULE = importlib.util.module_from_spec(_RUNTIME_FIXTURE_SPEC)
    assert _RUNTIME_FIXTURE_SPEC is not None and _RUNTIME_FIXTURE_SPEC.loader is not None
    _RUNTIME_FIXTURE_SPEC.loader.exec_module(_RUNTIME_FIXTURE_MODULE)
    task_source_registry_payload = _RUNTIME_FIXTURE_MODULE.task_source_registry_payload
    worker_registry_payload = _RUNTIME_FIXTURE_MODULE.worker_registry_payload


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_OPS_SCRIPT = REPO_ROOT / "scripts" / "task_ops.py"
AUTOMATION_INTENT_SCRIPT = REPO_ROOT / "scripts" / "automation_intent.py"
CHECK_REPO_SCRIPT = REPO_ROOT / "scripts" / "check_repo.py"
CHECK_HYGIENE_SCRIPT = REPO_ROOT / "scripts" / "check_hygiene.py"
AUTOMATION_RUNNER_SCRIPT = REPO_ROOT / "scripts" / "automation_runner.py"
RENDER_RUNTIME_PROMPTS_SCRIPT = REPO_ROOT / "scripts" / "render_runtime_prompts.py"
_TEMPLATE_REPO: Path | None = None


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=False)


def read_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def idle_current_payload(
    *,
    timestamp: str = "2026-04-04T00:00:00+08:00",
    next_action: str = "wait_for_successor_or_explicit_activation",
) -> dict[str, Any]:
    return {
        "current_task_id": None,
        "title": None,
        "status": "idle",
        "task_kind": None,
        "execution_mode": None,
        "parent_task_id": None,
        "stage": None,
        "branch": None,
        "size_class": None,
        "automation_mode": None,
        "worker_state": "idle",
        "blocked_reason": None,
        "last_reported_at": timestamp,
        "topology": None,
        "allowed_dirs": [],
        "reserved_paths": [],
        "planned_write_paths": [],
        "planned_test_paths": [],
        "required_tests": [],
        "lane_count": None,
        "lane_index": None,
        "parallelism_plan_id": None,
        "review_bundle_status": None,
        "task_file": None,
        "runlog_file": None,
        "next_action": next_action,
        "updated_at": timestamp,
    }


def read_roadmap(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError("roadmap frontmatter is missing")
    _, remainder = text.split("---\n", 1)
    frontmatter_text, body = remainder.split("\n---\n", 1)
    return yaml.safe_load(frontmatter_text) or {}, body.lstrip("\n")


def write_roadmap(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    rendered_body = body.strip()
    path.write_text(f"---\n{frontmatter_text}\n---\n\n{rendered_body}\n", encoding="utf-8", newline="\n")


def run_python(script: Path, repo: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=repo,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=merged_env,
    )


def run_python_inline(
    script: Path, repo: Path, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    command = [sys.executable, str(script), *args]
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    previous_argv = sys.argv[:]
    previous_cwd = Path.cwd()
    previous_sys_path = sys.path[:]
    previous_env = os.environ.copy()
    exit_code = 0
    try:
        os.environ.clear()
        os.environ.update(merged_env)
        os.chdir(repo)
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
        os.environ.clear()
        os.environ.update(previous_env)
        os.chdir(previous_cwd)
        sys.argv = previous_argv
        sys.path[:] = previous_sys_path
    return subprocess.CompletedProcess(command, exit_code, stdout_buffer.getvalue(), stderr_buffer.getvalue())


def _write_automation_intents_catalog(path: Path) -> None:
    write_yaml(path, automation_intents_payload())


def git_commit_all(repo: Path, message: str = "update") -> None:
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True, text=True)


def _configure_test_repo_git_identity(repo: Path) -> None:
    subprocess.run(["git", "config", "user.name", "Codex"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "codex@example.com"], cwd=repo, check=True, capture_output=True, text=True)


def _clone_template_repo(template_repo: Path, destination: Path) -> None:
    # Prefer a local clone so each test repo reuses the cached template objects
    # instead of copying the full repository payload every time.
    try:
        subprocess.run(
            ["git", "clone", "--quiet", "--local", str(template_repo), str(destination)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        shutil.copytree(template_repo, destination)
    _configure_test_repo_git_identity(destination)
    subprocess.run(
        ["git", "remote", "remove", "origin"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )


def set_idle_control_plane(
    repo: Path,
    *,
    timestamp: str = "2026-04-04T00:00:00+08:00",
    next_action: str = "wait_for_successor_or_explicit_activation",
) -> None:
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", idle_current_payload(timestamp=timestamp, next_action=next_action))

    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    for entry in worktrees.get("entries", []):
        if entry.get("work_mode") == "coordination":
            entry["status"] = "closed"
    worktrees["updated_at"] = timestamp
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)

    roadmap_path = repo / "docs/governance/DEVELOPMENT_ROADMAP.md"
    frontmatter, body = read_roadmap(roadmap_path)
    frontmatter["current_task_id"] = None
    frontmatter["current_phase"] = "idle"
    body = (
        "# Roadmap\n\n"
        "## Current Task\n\n"
        "- no live current task; waiting for explicit activation or roadmap continuation."
    )
    write_roadmap(roadmap_path, frontmatter, body)


def close_live_task_to_idle(
    repo: Path,
    *,
    task_id: str = "TASK-BASE-001",
    required_test: str = "pytest tests/base -q",
    summary: str = "review ready",
    commit_after_close: bool = False,
) -> None:
    finished = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        task_id,
        "--summary",
        summary,
        "--tests",
        required_test,
    )
    assert finished.returncode == 0, finished.stdout + finished.stderr
    git_commit_all(repo, f"prepare {task_id} closeout")
    closed = run_python(TASK_OPS_SCRIPT, repo, "close", task_id)
    assert closed.returncode == 0, closed.stdout + closed.stderr
    if commit_after_close:
        git_commit_all(repo, f"close {task_id} to idle")


def set_live_task_review_without_evidence(
    repo: Path,
    *,
    task_id: str = "TASK-BASE-001",
    commit_after_update: bool = False,
) -> None:
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == task_id)
    task["status"] = "review"
    task["worker_state"] = "review_pending"
    task["blocked_reason"] = None
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["status"] = "review"
    current_task["worker_state"] = "review_pending"
    current_task["blocked_reason"] = None
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)

    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == task_id)
    entry["status"] = "active"
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)

    runlog_path = repo / f"docs/governance/runlogs/{task_id}-RUNLOG.md"
    runlog_path.write_text(
        (
            f"# {task_id} RUNLOG\n\n"
            "## Task Status\n\n"
            f"- `task_id`: `{task_id}`\n"
            "- `status`: `review`\n"
            "- `stage`: `base-stage`\n"
            "- `branch`: `main`\n"
            "- `worker_state`: `review_pending`\n\n"
            "<!-- generated:runlog-meta:start -->\n"
            "## Generated Task Snapshot\n\n"
            f"- `task_id`: `{task_id}`\n"
            "- `status`: `review`\n"
            "- `stage`: `base-stage`\n"
            "- `branch`: `main`\n"
            "- `worker_state`: `review_pending`\n"
            "- `lane_count`: `1`\n"
            "- `lane_index`: `null`\n"
            "- `parallelism_plan_id`: `null`\n"
            "- `review_bundle_status`: `not_applicable`\n"
            "<!-- generated:runlog-meta:end -->\n"
        ),
        encoding="utf-8",
    )

    if commit_after_update:
        git_commit_all(repo, f"mark {task_id} review without evidence")


def init_structure(repo: Path) -> None:
    (repo / "docs/governance/tasks").mkdir(parents=True, exist_ok=True)
    (repo / "docs/governance/runlogs").mkdir(parents=True, exist_ok=True)
    (repo / "docs/governance/handoffs").mkdir(parents=True, exist_ok=True)
    (repo / "src/base").mkdir(parents=True, exist_ok=True)
    (repo / "tests/base").mkdir(parents=True, exist_ok=True)
    for stage_dir in (
        "src/stage1_orchestration",
        "src/stage2_ingestion",
        "src/stage3_parsing",
        "src/stage4_validation",
        "src/stage5_reporting",
        "src/stage6_facts",
        "src/stage7_sales",
        "src/stage8_contact",
        "src/stage9_delivery",
        "tests/stage1",
        "tests/stage2",
        "tests/stage3",
        "tests/stage4",
        "tests/stage5",
        "tests/stage6",
        "tests/stage7",
        "tests/stage8",
        "tests/stage9",
    ):
        (repo / stage_dir).mkdir(parents=True, exist_ok=True)
    for test_dir in ("tests/contracts", "tests/automation", "tests/integration"):
        (repo / test_dir).mkdir(parents=True, exist_ok=True)
    (repo / ".gitignore").write_text(".codex/local/\n__pycache__/\n", encoding="utf-8")
    (repo / "src/base/module.py").write_text("def base_value():\n    return 1\n", encoding="utf-8")
    (repo / "tests/base/test_base.py").write_text("def test_base():\n    assert True\n", encoding="utf-8")
    for stage_name in ("stage1", "stage2", "stage3", "stage4", "stage5", "stage6", "stage7", "stage8", "stage9"):
        (repo / f"tests/{stage_name}/test_{stage_name}.py").write_text(
            f"def test_{stage_name}():\n    assert True\n",
            encoding="utf-8",
        )
    (repo / "tests/integration/test_smoke.py").write_text(
        "def test_integration_smoke():\n    assert True\n",
        encoding="utf-8",
    )


def _write_governance_catalogs(repo: Path) -> None:
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap_text(), encoding="utf-8")
    write_live_governance_boundary(repo / "docs/governance/LIVE_GOVERNANCE_BOUNDARY.md")
    (repo / "docs/governance/CODE_HYGIENE_POLICY.md").write_text("# Policy\n", encoding="utf-8")
    _write_automation_intents_catalog(repo / "docs/governance/AUTOMATION_INTENTS.yaml")
    write_git_publish_policy(repo / "docs/governance/GIT_PUBLISH_POLICY.yaml")
    write_handoff_policy(repo / "docs/governance/HANDOFF_POLICY.yaml")
    write_coordination_planner_policy(repo / "docs/governance/COORDINATION_PLANNER_POLICY.yaml")
    write_prompt_governance_files(repo)
    write_yaml(repo / "docs/governance/MODULE_MAP.yaml", module_map_payload())
    write_yaml(repo / "docs/governance/TEST_MATRIX.yaml", test_matrix_payload())
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map_payload())
    write_yaml(repo / "docs/governance/TASK_POLICY.yaml", task_policy_payload())
    write_yaml(repo / "docs/governance/TASK_SOURCE_REGISTRY.yaml", task_source_registry_payload())


def _write_governance_ledgers(repo: Path, task: dict[str, Any]) -> None:
    worker_registry = worker_registry_payload()
    worker_registry["workers"][0]["last_heartbeat_at"] = "2026-04-04T00:00:00+08:00"
    write_yaml(repo / "docs/governance/WORKER_REGISTRY.yaml", worker_registry)
    write_yaml(
        repo / "docs/governance/CURRENT_TASK.yaml",
        {
            **task,
            "current_task_id": task["task_id"],
            "next_action": "implement base task",
            "updated_at": "2026-04-04T00:00:00+08:00",
        },
    )
    write_yaml(
        repo / "docs/governance/TASK_REGISTRY.yaml",
        {
            "version": "3.0",
            "updated_at": "2026-04-04T00:00:00+08:00",
            "tasks": [{**task, "created_at": "2026-04-04T00:00:00+08:00", "activated_at": "2026-04-04T00:00:00+08:00", "closed_at": None}],
        },
    )
    write_yaml(
        repo / "docs/governance/WORKTREE_REGISTRY.yaml",
        {
            "version": "3.0",
            "updated_at": "2026-04-04T00:00:00+08:00",
            "entries": [
                {
                    "task_id": "TASK-BASE-001",
                    "work_mode": "coordination",
                    "parent_task_id": None,
                    "branch": "main",
                    "path": str(repo).replace("\\", "/"),
                    "status": "active",
                    "cleanup_state": "not_needed",
                    "cleanup_attempts": 0,
                    "last_cleanup_error": None,
                    "worker_owner": "coordinator",
                }
            ],
        },
    )


def _write_product_contract_fixtures(repo: Path) -> None:
    (repo / "docs/product").mkdir(parents=True, exist_ok=True)
    (repo / "docs/contracts").mkdir(parents=True, exist_ok=True)
    write_mvp_scope(
        repo,
        scope="stage1_to_stage9",
        included_stages=["stage1", "stage2", "stage3", "stage4", "stage5", "stage6", "stage7", "stage8", "stage9"],
        excluded_stages=[],
    )
    write_yaml(
        repo / "docs/contracts/region_coverage_registry.yaml",
        {
            "version": "1.0",
            "regions": [
                {
                    "region_code": "CN",
                    "is_sellable": True,
                }
            ],
        },
    )


def write_governance_files(repo: Path) -> None:
    task = base_task_payload()
    _write_governance_catalogs(repo)
    _write_governance_ledgers(repo, task)
    _write_product_contract_fixtures(repo)


def write_mvp_scope(repo: Path, *, scope: str, included_stages: list[str], excluded_stages: list[str]) -> None:
    payload = [
        "---",
        f"mvp_scope: {scope}",
        "included_stages:",
        *[f"- {stage_id}" for stage_id in included_stages],
        "excluded_stages:",
        *[f"- {stage_id}" for stage_id in excluded_stages],
        "updated_at: '2026-04-04T00:00:00+08:00'",
        "---",
        "",
        "# MVP Scope",
        "",
    ]
    (repo / "docs/product/MVP_SCOPE.md").write_text("\n".join(payload), encoding="utf-8")
    write_yaml(
        repo / "docs/contracts/sources_registry.yaml",
        {
            "version": "1.0",
            "sources": [
                {
                    "source_id": "TEST-SOURCE",
                    "coverage_regions": ["CN"],
                }
            ],
        },
    )
    (repo / "docs/governance/tasks/TASK-BASE-001.md").write_text(base_task_markdown(), encoding="utf-8")
    (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").write_text(base_runlog_markdown(), encoding="utf-8")


def init_governance_repo(tmp_path: Path) -> Path:
    global _TEMPLATE_REPO
    repo = tmp_path / "repo"
    if _TEMPLATE_REPO is None or not _TEMPLATE_REPO.exists():
        template_root = Path(tempfile.mkdtemp(prefix="ax9-governance-template-"))
        template_repo = template_root / "repo"
        init_structure(template_repo)
        write_governance_files(template_repo)
        subprocess.run(["git", "init", "-b", "main"], cwd=template_repo, check=True, capture_output=True, text=True)
        _configure_test_repo_git_identity(template_repo)
        subprocess.run(["git", "add", "."], cwd=template_repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=template_repo, check=True, capture_output=True, text=True)
        _TEMPLATE_REPO = template_repo
    _clone_template_repo(_TEMPLATE_REPO, repo)
    return repo
