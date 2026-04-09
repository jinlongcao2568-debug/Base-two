from __future__ import annotations

import pytest
pytestmark = pytest.mark.slow

from pathlib import Path

from .helpers import (
    TASK_OPS_SCRIPT,
    close_live_task_to_idle,
    init_governance_repo,
    read_yaml,
    run_python_inline as run_python,
    write_yaml,
)


def test_continue_roadmap_blocks_idle_without_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    autopilot = next(
        item for item in capability_map["capabilities"] if item["capability_id"] == "roadmap_autopilot_continuation"
    )
    autopilot["status"] = "implemented"
    write_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml", capability_map)
    close_live_task_to_idle(repo, commit_after_close=True)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")

    assert result.returncode == 1
    assert (current_task["current_task_id"], current_task["status"]) == (None, "idle")
    assert "no successor is available for continue-roadmap from idle control plane" in result.stdout
