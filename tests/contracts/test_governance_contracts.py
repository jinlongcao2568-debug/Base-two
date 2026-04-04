from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_task_registry_schema_fields_present() -> None:
    registry = load_yaml(REPO_ROOT / "docs/governance/TASK_REGISTRY.yaml")
    assert registry["version"] == "3.0"
    task = registry["tasks"][0]
    required_fields = {
        "task_id",
        "title",
        "status",
        "task_kind",
        "execution_mode",
        "parent_task_id",
        "stage",
        "branch",
        "size_class",
        "automation_mode",
        "worker_state",
        "blocked_reason",
        "last_reported_at",
        "topology",
        "allowed_dirs",
        "reserved_paths",
        "planned_write_paths",
        "planned_test_paths",
        "required_tests",
        "task_file",
        "runlog_file",
        "created_at",
        "activated_at",
        "closed_at",
    }
    assert required_fields <= set(task)


def test_current_task_schema_fields_present() -> None:
    current_task = load_yaml(REPO_ROOT / "docs/governance/CURRENT_TASK.yaml")
    required_fields = {
        "current_task_id",
        "title",
        "status",
        "task_kind",
        "execution_mode",
        "parent_task_id",
        "stage",
        "branch",
        "size_class",
        "automation_mode",
        "worker_state",
        "blocked_reason",
        "last_reported_at",
        "topology",
        "allowed_dirs",
        "reserved_paths",
        "planned_write_paths",
        "planned_test_paths",
        "required_tests",
        "task_file",
        "runlog_file",
        "next_action",
        "updated_at",
    }
    assert required_fields <= set(current_task)


def test_worktree_registry_schema_fields_present() -> None:
    registry = load_yaml(REPO_ROOT / "docs/governance/WORKTREE_REGISTRY.yaml")
    assert registry["version"] == "3.0"
    entry = registry["entries"][0]
    required_fields = {
        "task_id",
        "work_mode",
        "parent_task_id",
        "branch",
        "path",
        "status",
        "cleanup_state",
        "cleanup_attempts",
        "last_cleanup_error",
        "worker_owner",
    }
    assert required_fields <= set(entry)
    assert entry["cleanup_state"] in {"not_needed", "pending", "blocked", "blocked_manual", "done"}


def test_module_map_schema_fields_present() -> None:
    payload = load_yaml(REPO_ROOT / "docs/governance/MODULE_MAP.yaml")
    assert payload["version"] == "1.0"
    for module in payload["modules"]:
        assert {
            "module_id",
            "owner_stage",
            "inputs",
            "outputs",
            "depends_on",
            "allowed_dirs",
            "reserved_paths",
            "integration_points",
            "required_tests",
        } <= set(module)


def test_test_matrix_schema_fields_present() -> None:
    payload = load_yaml(REPO_ROOT / "docs/governance/TEST_MATRIX.yaml")
    assert payload["version"] in {"1.0", "1.1"}
    assert {"micro", "standard", "heavy"} <= set(payload["size_class_gates"])
    module_rules = payload["modules"]["governance_control_plane"]
    assert {"micro", "standard", "heavy"} <= set(module_rules)
    assert "authority_critical_chains" in payload
