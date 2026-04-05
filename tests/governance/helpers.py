from __future__ import annotations

from pathlib import Path
import importlib.util
import subprocess
import sys
from typing import Any

import yaml

try:
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
except ImportError:
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


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_OPS_SCRIPT = REPO_ROOT / "scripts" / "task_ops.py"
AUTOMATION_INTENT_SCRIPT = REPO_ROOT / "scripts" / "automation_intent.py"
CHECK_REPO_SCRIPT = REPO_ROOT / "scripts" / "check_repo.py"
CHECK_HYGIENE_SCRIPT = REPO_ROOT / "scripts" / "check_hygiene.py"
AUTOMATION_RUNNER_SCRIPT = REPO_ROOT / "scripts" / "automation_runner.py"
RENDER_RUNTIME_PROMPTS_SCRIPT = REPO_ROOT / "scripts" / "render_runtime_prompts.py"


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


def run_python(script: Path, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=repo,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def _write_automation_intents(path: Path) -> None:
    path.write_text(
        (
            "version: '1.0'\n"
            "recognition_mode: heuristic_free_form\n"
            "generic_continue_signals:\n"
            "  - 继续\n"
            "  - 接着\n"
            "supported_intents:\n"
            "  - intent_id: continue-current\n"
            "    canonical_phrase: 继续当前任务\n"
            "    mapped_command: python scripts/task_ops.py continue-current\n"
            "    command_argv:\n"
            "      - python\n"
            "      - scripts/task_ops.py\n"
            "      - continue-current\n"
            "    examples:\n"
            "      - 继续当前任务\n"
            "    action_any:\n"
            "      - 继续\n"
            "      - 接着\n"
            "    context_any:\n"
            "      - 当前任务\n"
            "      - 手头任务\n"
            "    disallow_any:\n"
            "      - 路线图\n"
            "      - 下一步\n"
            "  - intent_id: continue-roadmap\n"
            "    canonical_phrase: 按路线图继续推进\n"
            "    mapped_command: python scripts/automation_runner.py once --continue-roadmap --prepare-worktrees\n"
            "    command_argv:\n"
            "      - python\n"
            "      - scripts/automation_runner.py\n"
            "      - once\n"
            "      - --continue-roadmap\n"
            "      - --prepare-worktrees\n"
            "    examples:\n"
            "      - 按路线图继续推进\n"
            "    action_any:\n"
            "      - 继续\n"
            "      - 推进\n"
            "    context_any:\n"
            "      - 路线图\n"
            "      - 下一步\n"
        ),
        encoding="utf-8",
    )


def _write_prompt_governance_files(root: Path) -> None:
    _write_prompt_catalog(root)
    _write_prompt_module_docs(root)


def _write_prompt_catalog(root: Path) -> None:
    (root / "docs/governance/PROMPT_MODULE_CATALOG.yaml").write_text(_prompt_catalog_text(), encoding="utf-8")


def _prompt_catalog_text() -> str:
    return "".join(
        [
            _prompt_catalog_header(),
            _prompt_catalog_modules_section(),
            _prompt_catalog_role_profiles_section(),
            _prompt_catalog_policy_section(),
            _prompt_catalog_runtime_profiles_section(),
        ]
    )


def _prompt_catalog_header() -> str:
    return (
        "version: '1.0'\n"
        "authority_source: docs/governance/README.md\n"
        "source_root: docs/governance/prompt_modules/\n"
    )


def _prompt_catalog_modules_section() -> str:
    return (
        "modules:\n"
        "  - module_id: boundary_first\n"
        "    path: docs/governance/prompt_modules/boundary_first.md\n"
        "    purpose: Define forbidden actions and scope boundaries before execution steps.\n"
        "    roles:\n"
        "      - coordinator\n"
        "      - worker\n"
        "      - reviewer\n"
        "  - module_id: reporting_discipline\n"
        "    path: docs/governance/prompt_modules/reporting_discipline.md\n"
        "    purpose: Keep status reporting factual, bounded, and stop-aware.\n"
        "    roles:\n"
        "      - coordinator\n"
        "      - worker\n"
        "      - reviewer\n"
        "  - module_id: tool_boundaries\n"
        "    path: docs/governance/prompt_modules/tool_boundaries.md\n"
        "    purpose: Bind tools to explicit scenarios and preserve auditability.\n"
        "    roles:\n"
        "      - worker\n"
        "      - reviewer\n"
        "  - module_id: role_overrides\n"
        "    path: docs/governance/prompt_modules/role_overrides.md\n"
        "    purpose: Add role-specific prompt overrides for coordinator, worker, and reviewer lanes.\n"
        "    roles:\n"
        "      - coordinator\n"
        "      - worker\n"
        "      - reviewer\n"
    )


def _prompt_catalog_role_profiles_section() -> str:
    return (
        "role_profiles:\n"
        "  - role_id: coordinator\n"
        "    modules:\n"
        "      - boundary_first\n"
        "      - reporting_discipline\n"
        "      - role_overrides\n"
        "    notes:\n"
        "      - Resolve scope before execution.\n"
        "      - Report blockers early.\n"
        "      - Do not auto-expand into adjacent work.\n"
        "  - role_id: worker\n"
        "    modules:\n"
        "      - boundary_first\n"
        "      - tool_boundaries\n"
        "      - role_overrides\n"
        "    notes:\n"
        "      - Stay inside allowed paths.\n"
        "      - Read before editing.\n"
        "      - Do not infer missing requirements.\n"
        "  - role_id: reviewer\n"
        "    modules:\n"
        "      - boundary_first\n"
        "      - reporting_discipline\n"
        "      - tool_boundaries\n"
        "      - role_overrides\n"
        "    notes:\n"
        "      - Default to finding gaps, not approving by inertia.\n"
        "      - Keep review claims evidence-backed.\n"
    )


def _prompt_catalog_policy_section() -> str:
    return (
        "custom_instructions_policy:\n"
        "  governance_source: repo_governance_only\n"
        "  default_state: empty\n"
        "  allowed_uses:\n"
        "    - language preference\n"
        "    - output style preference\n"
        "  forbidden_uses:\n"
        "    - task switching rules\n"
        "    - successor selection rules\n"
        "    - parallelism policy\n"
        "    - closeout policy\n"
        "    - scope or authority boundaries\n"
    )


def _prompt_catalog_runtime_profiles_section() -> str:
    return (
        "runtime_profiles:\n"
        "  - profile_id: coordinator_profile\n"
        "    role_id: coordinator\n"
        "    output_path: docs/governance/runtime_prompts/coordinator.md\n"
        "    mission:\n"
        "      - Route tasks, validate boundaries, manage ledgers, and decide closeout gates.\n"
        "      - Do not implement large feature work directly inside the coordinator lane.\n"
        "  - profile_id: worker_profile\n"
        "    role_id: worker\n"
        "    output_path: docs/governance/runtime_prompts/worker.md\n"
        "    mission:\n"
        "      - Execute only inside the assigned task or lane scope.\n"
        "      - Do not expand scope, invent interfaces, or perform opportunistic refactors.\n"
        "  - profile_id: reviewer_profile\n"
        "    role_id: reviewer\n"
        "    output_path: docs/governance/runtime_prompts/reviewer.md\n"
        "    mission:\n"
        "      - Review for bugs, regressions, missing tests, and weak rollback stories.\n"
        "      - Do not approve work by inertia or because a diff appears small.\n"
    )


def _write_prompt_module_docs(root: Path) -> None:
    prompt_root = root / "docs/governance/prompt_modules"
    prompt_root.mkdir(parents=True, exist_ok=True)
    for relative_path, content in _prompt_module_files().items():
        (prompt_root / relative_path).write_text(content, encoding="utf-8")


def _prompt_module_files() -> dict[str, str]:
    return {
        "README.md": (
            "# Prompt Modules\n\n"
            "This directory is the governed prompt source of truth for AX9 automation roles.\n\n"
            "Root-level scratch notes are not a live prompt source.\n"
        ),
        "boundary_first.md": "# Boundary First\n\n- State forbidden actions before desired actions.\n",
        "reporting_discipline.md": "# Reporting Discipline\n\n- Report facts before interpretation.\n",
        "tool_boundaries.md": (
            "# Tool Boundaries\n\n"
            "- Match tools to scenarios instead of using every available tool by default.\n"
        ),
        "role_overrides.md": (
            "# Role Overrides\n\n"
            "## Coordinator\n\n"
            "- Resolve ownership, scope, and next gate before assigning work.\n"
        ),
    }


def _write_handoff_policy(path: Path) -> None:
    path.write_text(
        (
            "version: '1.0'\n"
            "updated_at: '2026-04-05T00:00:00+08:00'\n"
            "authority_source: docs/governance/README.md\n"
            "create_on_new_top_level_coordination_task: true\n"
            "recovery_source_of_truth: docs/governance/handoffs/\n"
            "fallback_mode: task_and_runlog\n"
            "required_fields:\n"
            "  - task_id\n"
            "  - summary_status\n"
            "  - last_handoff_at\n"
            "  - completed_items\n"
            "  - remaining_items\n"
            "  - next_step\n"
            "  - next_tests\n"
            "  - current_risks\n"
            "  - candidate_write_paths\n"
            "  - candidate_test_paths\n"
            "  - resume_notes\n"
        ),
        encoding="utf-8",
    )


def git_commit_all(repo: Path, message: str = "update") -> None:
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True, text=True)


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


def write_governance_files(repo: Path) -> None:
    task = base_task_payload()
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap_text(), encoding="utf-8")
    (repo / "docs/governance/CODE_HYGIENE_POLICY.md").write_text("# Policy\n", encoding="utf-8")
    _write_automation_intents(repo / "docs/governance/AUTOMATION_INTENTS.yaml")
    _write_handoff_policy(repo / "docs/governance/HANDOFF_POLICY.yaml")
    _write_prompt_governance_files(repo)
    write_yaml(repo / "docs/governance/MODULE_MAP.yaml", module_map_payload())
    write_yaml(repo / "docs/governance/TEST_MATRIX.yaml", test_matrix_payload())
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map_payload())
    write_yaml(repo / "docs/governance/TASK_POLICY.yaml", task_policy_payload())
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
    (repo / "docs/governance/tasks/TASK-BASE-001.md").write_text(base_task_markdown(), encoding="utf-8")
    (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").write_text(base_runlog_markdown(), encoding="utf-8")


def init_governance_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    init_structure(repo)
    write_governance_files(repo)
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "codex@example.com"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo
