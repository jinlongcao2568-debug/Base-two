from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HELPERS_PATH = Path(__file__).resolve().parents[1] / "governance" / "helpers.py"
HELPERS_SPEC = importlib.util.spec_from_file_location("gov_helpers_orchestration_runner", HELPERS_PATH)
HELPERS = importlib.util.module_from_spec(HELPERS_SPEC)
assert HELPERS_SPEC.loader is not None
HELPERS_SPEC.loader.exec_module(HELPERS)

TASK_OPS_SCRIPT = HELPERS.TASK_OPS_SCRIPT

RUNNER_HELPERS_PATH = Path(__file__).with_name("test_high_throughput_runner.py")
RUNNER_HELPERS_SPEC = importlib.util.spec_from_file_location(
    "automation_high_throughput_helpers",
    RUNNER_HELPERS_PATH,
)
RUNNER_HELPERS = importlib.util.module_from_spec(RUNNER_HELPERS_SPEC)
assert RUNNER_HELPERS_SPEC.loader is not None
RUNNER_HELPERS_SPEC.loader.exec_module(RUNNER_HELPERS)

AUTOMATION_RUNNER_SCRIPT = RUNNER_HELPERS.AUTOMATION_RUNNER_SCRIPT
BUILDERS = RUNNER_HELPERS.BUILDERS
init_governance_repo = RUNNER_HELPERS.init_governance_repo
read_yaml = RUNNER_HELPERS.read_yaml
run_python = RUNNER_HELPERS.run_python
write_yaml = RUNNER_HELPERS.write_yaml


def _status_json(repo: Path) -> dict:
    result = run_python(TASK_OPS_SCRIPT, repo, "orchestration-status", "--format", "json")
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_runner_updates_runtime_status_after_cycle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _status_json(repo)
    current_session_id = payload["sessions"]["current_session_id"]
    assert payload["runtime"]["mode"] == "automation_runner"
    assert payload["runtime"]["current_command"] == "automation-runner"
    assert payload["runner_pressure"]["lane_count"] == 1
    assert current_session_id is not None
    assert payload["sessions"]["records"][current_session_id]["mode"] == "automation_runner"


def test_unsupported_remote_worker_does_not_change_single_machine_preparation(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    registry = read_yaml(repo / "docs/governance/WORKER_REGISTRY.yaml")
    registry["workers"].append(
        {
            "worker_id": "worker-remote-01",
            "kind": "ssh",
            "enabled": True,
            "status": "active",
            "host": "192.168.1.9",
            "workspace_root": "/srv/ax9",
            "capabilities": ["execution"],
            "unsupported_in_v1": True,
            "last_heartbeat_at": None,
            "notes": "Future remote worker reservation.",
        }
    )
    write_yaml(repo / "docs/governance/WORKER_REGISTRY.yaml", registry)
    BUILDERS.set_live_task_mode(repo, automation_mode="assisted", topology="parallel_parent", lane_count=2)
    BUILDERS.create_review_ready_children(
        repo,
        ["TASK-REMOTE-001", "TASK-REMOTE-002"],
        write_path_prefix="src/runner_remote/",
    )

    result = run_python(AUTOMATION_RUNNER_SCRIPT, repo, "once", "--prepare-worktrees")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _status_json(repo)
    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    execution_entries = [
        entry
        for entry in worktrees["entries"]
        if entry.get("task_id") in {"TASK-REMOTE-001", "TASK-REMOTE-002"}
    ]
    assert len(execution_entries) == 2
    assert payload["workers"]["entries"]["worker-remote-01"]["observed_status"] == "unsupported_in_v1"
    assert {entry["worker_owner"] for entry in execution_entries}.isdisjoint({"worker-remote-01"})
