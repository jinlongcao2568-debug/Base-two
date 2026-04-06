from __future__ import annotations

import importlib.util
from pathlib import Path


HELPERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "helpers.py"
SPEC = importlib.util.spec_from_file_location("gov_helpers_task_gov_018", HELPERS_PATH)
HELPERS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(HELPERS)

TASK_OPS_SCRIPT = HELPERS.TASK_OPS_SCRIPT
CHECK_REPO_SCRIPT = HELPERS.CHECK_REPO_SCRIPT
init_governance_repo = HELPERS.init_governance_repo
read_yaml = HELPERS.read_yaml
run_python = HELPERS.run_python


def test_prepare_child_execution_records_runtime_workflow_state(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-EXEC-RUNTIME-018",
        "--title",
        "runtime child lane",
        "--stage",
        "child-stage",
        "--branch",
        "feat/TASK-EXEC-RUNTIME-018",
        "--task-kind",
        "execution",
        "--execution-mode",
        "isolated_worktree",
        "--parent-task-id",
        "TASK-BASE-001",
        "--allowed-dirs",
        "docs/governance/",
        "scripts/",
        "--planned-write-paths",
        "docs/governance/",
        "scripts/",
        "--planned-test-paths",
        "tests/governance/",
        "--required-tests",
        f'python "{CHECK_REPO_SCRIPT.as_posix()}"',
    )
    assert created.returncode == 0, created.stdout + created.stderr
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-RUNTIME-018"

    prepared = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "prepare-child-execution",
        "TASK-EXEC-RUNTIME-018",
        "--path",
        str(destination),
    )

    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-EXEC-RUNTIME-018")
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")

    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    assert entry["executor_status"] == "prepared"
    assert entry["workflow_state"]["phase"] == "prepared"
    assert runtime["execution"]["entries"]["TASK-EXEC-RUNTIME-018"]["executor_status"] == "prepared"
