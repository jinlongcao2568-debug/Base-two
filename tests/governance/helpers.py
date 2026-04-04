from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml


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


def roadmap_text() -> str:
    return (
        "---\n"
        "current_phase: base-phase\n"
        "current_task_id: TASK-BASE-001\n"
        "next_recommended_task_id: null\n"
        "stage_establishment:\n"
        "  stage1: not_established\n"
        "  stage2: not_established\n"
        "  stage3: not_established\n"
        "  stage4: not_established\n"
        "  stage5: not_established\n"
        "  stage6: not_established\n"
        "  stage7: not_established\n"
        "  stage8: not_established\n"
        "  stage9: not_established\n"
        "automation_foundation: not_established\n"
        "---\n\n# Roadmap\n"
    )


def module_map_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "modules": [
            {
                "module_id": "governance_control_plane",
                "owner_stage": "governance",
                "inputs": ["CURRENT_TASK"],
                "outputs": ["task updates"],
                "depends_on": [],
                "allowed_dirs": ["docs/governance/", "tests/governance/"],
                "reserved_paths": ["src/stage6_facts/"],
                "integration_points": ["tests/governance/"],
                "required_tests": ["pytest tests/base -q"],
            }
        ],
    }


def test_matrix_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "size_class_gates": {
            "micro": {"preflight": ["python scripts/check_repo.py"], "worker": ["module tests"], "closeout": []},
            "standard": {"preflight": ["python scripts/check_repo.py"], "worker": ["module tests"], "closeout": []},
            "heavy": {"preflight": ["python scripts/check_repo.py"], "worker": ["module tests"], "closeout": []},
        },
        "modules": {
            "governance_control_plane": {
                "micro": {"required_tests": ["pytest tests/base -q"]},
                "standard": {"required_tests": ["pytest tests/base -q"]},
                "heavy": {"required_tests": ["pytest tests/base -q"]},
            }
        },
    }


def base_allowed_dirs() -> list[str]:
    return [
        "src/base/",
        "tests/base/",
        "docs/governance/CURRENT_TASK.yaml",
        "docs/governance/DEVELOPMENT_ROADMAP.md",
        "docs/governance/TASK_REGISTRY.yaml",
        "docs/governance/WORKTREE_REGISTRY.yaml",
        "docs/governance/MODULE_MAP.yaml",
        "docs/governance/TEST_MATRIX.yaml",
        "docs/governance/CODE_HYGIENE_POLICY.md",
        "docs/governance/tasks/",
        "docs/governance/runlogs/",
    ]


def base_planned_write_paths() -> list[str]:
    return [
        "src/base/",
        "tests/base/",
        "docs/governance/CURRENT_TASK.yaml",
        "docs/governance/DEVELOPMENT_ROADMAP.md",
        "docs/governance/TASK_REGISTRY.yaml",
        "docs/governance/WORKTREE_REGISTRY.yaml",
        "docs/governance/MODULE_MAP.yaml",
        "docs/governance/TEST_MATRIX.yaml",
        "docs/governance/CODE_HYGIENE_POLICY.md",
        "docs/governance/tasks/",
        "docs/governance/runlogs/",
    ]


def base_task_payload() -> dict[str, Any]:
    return {
        "task_id": "TASK-BASE-001",
        "title": "base coordination task",
        "status": "doing",
        "task_kind": "coordination",
        "execution_mode": "shared_coordination",
        "parent_task_id": None,
        "stage": "base-phase",
        "branch": "main",
        "size_class": "standard",
        "automation_mode": "assisted",
        "worker_state": "running",
        "blocked_reason": None,
        "last_reported_at": "2026-04-04T00:00:00+08:00",
        "topology": "single_worker",
        "allowed_dirs": base_allowed_dirs(),
        "reserved_paths": [],
        "planned_write_paths": base_planned_write_paths(),
        "planned_test_paths": ["tests/base/"],
        "required_tests": ["pytest tests/base -q"],
        "task_file": "docs/governance/tasks/TASK-BASE-001.md",
        "runlog_file": "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md",
    }


def init_structure(repo: Path) -> None:
    (repo / "docs/governance/tasks").mkdir(parents=True, exist_ok=True)
    (repo / "docs/governance/runlogs").mkdir(parents=True, exist_ok=True)
    (repo / "src/base").mkdir(parents=True, exist_ok=True)
    (repo / "tests/base").mkdir(parents=True, exist_ok=True)
    (repo / "tests/contracts").mkdir(parents=True, exist_ok=True)
    (repo / "tests/automation").mkdir(parents=True, exist_ok=True)
    (repo / ".gitignore").write_text(".codex/local/\n__pycache__/\n", encoding="utf-8")
    (repo / "src/base/module.py").write_text("def base_value():\n    return 1\n", encoding="utf-8")
    (repo / "tests/base/test_base.py").write_text("def test_base():\n    assert True\n", encoding="utf-8")


def base_task_markdown() -> str:
    return (
        "# TASK-BASE-001 base coordination task\n\n"
        "## Task Baseline\n\n"
        "- `task_id`: `TASK-BASE-001`\n"
        "- `status`: `doing`\n"
        "- `stage`: `base-phase`\n"
        "- `branch`: `main`\n"
        "- `worker_state`: `running`\n\n"
        "## Narrative Assertions\n\n"
        "- `narrative_status`: `doing`\n"
        "- `closeout_state`: `not_ready`\n"
        "- `blocking_state`: `clear`\n"
        "- `completed_scope`: `active_progress`\n"
        "- `remaining_scope`: `active_work_remaining`\n"
        "- `next_gate`: `validation_pending`\n\n"
        "<!-- generated:task-meta:start -->\n"
        "## Generated Metadata\n\n"
        "- `status`: `doing`\n"
        "- `task_kind`: `coordination`\n"
        "- `execution_mode`: `shared_coordination`\n"
        "- `size_class`: `standard`\n"
        "- `automation_mode`: `assisted`\n"
        "- `worker_state`: `running`\n"
        "- `topology`: `single_worker`\n"
        "- `reserved_paths`: `[]`\n"
        "- `branch`: `main`\n"
        "- `updated_at`: `2026-04-04T00:00:00+08:00`\n"
        "<!-- generated:task-meta:end -->\n"
    )


def base_runlog_markdown() -> str:
    return (
        "# TASK-BASE-001 RUNLOG\n\n"
        "## Task Status\n\n"
        "- `task_id`: `TASK-BASE-001`\n"
        "- `status`: `doing`\n"
        "- `stage`: `base-phase`\n"
        "- `branch`: `main`\n"
        "- `worker_state`: `running`\n\n"
        "## Test Log\n\n"
        "- `pytest tests/base -q`\n\n"
        "## Narrative Assertions\n\n"
        "- `narrative_status`: `doing`\n"
        "- `closeout_state`: `not_ready`\n"
        "- `blocking_state`: `clear`\n"
        "- `completed_scope`: `active_progress`\n"
        "- `remaining_scope`: `active_work_remaining`\n"
        "- `next_gate`: `validation_pending`\n\n"
        "<!-- generated:runlog-meta:start -->\n"
        "## Generated Task Snapshot\n\n"
        "- `task_id`: `TASK-BASE-001`\n"
        "- `status`: `doing`\n"
        "- `stage`: `base-phase`\n"
        "- `branch`: `main`\n"
        "- `worker_state`: `running`\n"
        "<!-- generated:runlog-meta:end -->\n"
    )


def write_governance_files(repo: Path) -> None:
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap_text(), encoding="utf-8")
    (repo / "docs/governance/CODE_HYGIENE_POLICY.md").write_text("# Policy\n", encoding="utf-8")
    write_yaml(repo / "docs/governance/MODULE_MAP.yaml", module_map_payload())
    write_yaml(repo / "docs/governance/TEST_MATRIX.yaml", test_matrix_payload())
    task = base_task_payload()
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
            "tasks": [
                {
                    **task,
                    "created_at": "2026-04-04T00:00:00+08:00",
                    "activated_at": "2026-04-04T00:00:00+08:00",
                    "closed_at": None,
                }
            ],
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
