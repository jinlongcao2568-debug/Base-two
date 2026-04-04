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
CHECK_REPO_SCRIPT = REPO_ROOT / "scripts" / "check_repo.py"
CHECK_HYGIENE_SCRIPT = REPO_ROOT / "scripts" / "check_hygiene.py"
AUTOMATION_RUNNER_SCRIPT = REPO_ROOT / "scripts" / "automation_runner.py"


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=False)


def read_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def run_python(script: Path, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=repo,
        text=True,
        capture_output=True,
    )


def git_commit_all(repo: Path, message: str = "update") -> None:
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True, text=True)


def init_structure(repo: Path) -> None:
    (repo / "docs/governance/tasks").mkdir(parents=True, exist_ok=True)
    (repo / "docs/governance/runlogs").mkdir(parents=True, exist_ok=True)
    (repo / "src/base").mkdir(parents=True, exist_ok=True)
    (repo / "tests/base").mkdir(parents=True, exist_ok=True)
    for stage_dir in (
        "src/stage1_orchestration",
        "src/stage2_ingestion",
        "src/stage3_parsing",
        "src/stage4_validation",
        "src/stage5_reporting",
        "src/stage6_facts",
        "tests/stage1",
        "tests/stage2",
        "tests/stage3",
        "tests/stage4",
        "tests/stage5",
        "tests/stage6",
    ):
        (repo / stage_dir).mkdir(parents=True, exist_ok=True)
    for test_dir in ("tests/contracts", "tests/automation", "tests/integration"):
        (repo / test_dir).mkdir(parents=True, exist_ok=True)
    (repo / ".gitignore").write_text(".codex/local/\n__pycache__/\n", encoding="utf-8")
    (repo / "src/base/module.py").write_text("def base_value():\n    return 1\n", encoding="utf-8")
    (repo / "tests/base/test_base.py").write_text("def test_base():\n    assert True\n", encoding="utf-8")
    for stage_name in ("stage1", "stage2", "stage3", "stage4", "stage5", "stage6"):
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
