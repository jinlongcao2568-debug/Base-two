from __future__ import annotations

import importlib.util
from pathlib import Path


HELPERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "helpers.py"
SPEC = importlib.util.spec_from_file_location("gov_helpers_runtime", HELPERS_PATH)
HELPERS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(HELPERS)

BUILDERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "scenario_builders.py"
BUILDERS_SPEC = importlib.util.spec_from_file_location("gov_builders_runtime", BUILDERS_PATH)
BUILDERS = importlib.util.module_from_spec(BUILDERS_SPEC)
assert BUILDERS_SPEC.loader is not None
BUILDERS_SPEC.loader.exec_module(BUILDERS)

AUTOMATION_RUNNER_SCRIPT = HELPERS.AUTOMATION_RUNNER_SCRIPT
TASK_OPS_SCRIPT = HELPERS.TASK_OPS_SCRIPT
init_governance_repo = HELPERS.init_governance_repo
read_yaml = HELPERS.read_yaml
run_python = HELPERS.run_python
write_yaml = HELPERS.write_yaml


def test_worker_heartbeat_updates_runtime_not_worker_registry(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    BUILDERS.set_live_task_mode(repo, automation_mode="autonomous", lane_count=1)
    BUILDERS.create_execution_task(
        repo,
        "TASK-EXEC-HEARTBEAT",
        write_path="src/heartbeat/",
        title="heartbeat lane",
        required_test="pytest tests/base -q",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    child = next(task for task in registry["tasks"] if task["task_id"] == "TASK-EXEC-HEARTBEAT")
    child["lane_count"] = 1
    child["lane_index"] = 1
    child["parallelism_plan_id"] = "plan-TASK-BASE-001-1"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    destination = tmp_path / "repo.worktrees" / "TASK-EXEC-HEARTBEAT"
    created = run_python(TASK_OPS_SCRIPT, repo, "worktree-create", "TASK-EXEC-HEARTBEAT", "--path", str(destination))
    assert created.returncode == 0, created.stdout + created.stderr
    before_worker_registry = (repo / "docs/governance/WORKER_REGISTRY.yaml").read_text(encoding="utf-8")

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-heartbeat",
        "TASK-EXEC-HEARTBEAT",
        "--worker-id",
        "worker-local-01",
        "--executor-status",
        "running",
    )
    after_worker_registry = (repo / "docs/governance/WORKER_REGISTRY.yaml").read_text(encoding="utf-8")
    runtime = read_yaml(repo / ".codex/local/COORDINATION_RUNTIME.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert before_worker_registry == after_worker_registry
    assert runtime["workers"]["entries"]["worker-local-01"]["last_heartbeat_at"] is not None
    assert runtime["execution"]["entries"]["TASK-EXEC-HEARTBEAT"]["executor_status"] == "running"


def test_runner_loop_reports_stop_reason(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "loop", "--cycles", "1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[CYCLE] automation-runner cycle=1" in result.stdout
    assert "[STOP] automation-runner loop stopped cycle=1 reason=cycle limit reached" in result.stdout
