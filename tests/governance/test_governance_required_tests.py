from __future__ import annotations

import sys
from pathlib import Path

from .fixture_payloads import FIXTURE_CAPABILITY_STATUS_OVERRIDES, capability_map_payload, module_map_payload
from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from governance_rules import resolve_test_matrix_commands, task_required_tests_for_matrix


def _profile_tests(repo: Path, profile_name: str) -> list[str]:
    matrix = read_yaml(repo / "docs/governance/TEST_MATRIX.yaml")
    return resolve_test_matrix_commands(matrix, matrix["governance_test_profiles"][profile_name])


def _module_tests(repo: Path, module_id: str, size_class: str) -> list[str]:
    matrix = read_yaml(repo / "docs/governance/TEST_MATRIX.yaml")
    return resolve_test_matrix_commands(matrix, matrix["modules"][module_id][size_class])


def _governance_task(*, planned_write_paths: list[str], allowed_dirs: list[str] | None = None) -> dict[str, object]:
    return {
        "module_id": "governance_control_plane",
        "size_class": "standard",
        "planned_write_paths": planned_write_paths,
        "allowed_dirs": allowed_dirs if allowed_dirs is not None else list(planned_write_paths),
    }


def test_docs_only_governance_task_uses_fast_profile_with_precise_planned_paths(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task = _governance_task(
        planned_write_paths=["docs/governance/CODE_HYGIENE_POLICY.md"],
        allowed_dirs=["docs/governance/", "scripts/", "tests/governance/", "tests/automation/"],
    )

    assert task_required_tests_for_matrix(repo, task) == _profile_tests(repo, "governance_fast")


def test_workflow_governance_task_uses_workflow_profile(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task = _governance_task(
        planned_write_paths=["scripts/task_continuation_ops.py"],
        allowed_dirs=["docs/governance/", "scripts/", "tests/governance/", "tests/automation/"],
    )

    assert task_required_tests_for_matrix(repo, task) == _profile_tests(repo, "governance_workflow")


def test_publish_governance_task_uses_publish_profile(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task = _governance_task(planned_write_paths=["scripts/task_publish_ops.py"])

    assert task_required_tests_for_matrix(repo, task) == _profile_tests(repo, "governance_publish")


def test_runner_governance_task_uses_runner_profile_without_full_governance_suite(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task = _governance_task(planned_write_paths=["scripts/automation_runner.py"])
    required_tests = task_required_tests_for_matrix(repo, task)

    assert required_tests == _profile_tests(repo, "automation_runner")
    assert "pytest tests/governance -q" not in required_tests


def test_policy_core_governance_task_uses_full_release_profile(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task = _governance_task(planned_write_paths=["docs/governance/TEST_MATRIX.yaml"])

    assert task_required_tests_for_matrix(repo, task) == _profile_tests(repo, "full_governance_release")


def test_business_stage_matrix_behavior_is_unchanged(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task = {
        "module_id": "stage4_validation",
        "size_class": "standard",
        "planned_write_paths": ["src/stage4_validation/"],
        "allowed_dirs": ["src/stage4_validation/"],
    }

    assert task_required_tests_for_matrix(repo, task) == _module_tests(repo, "stage4_validation", "standard")


def test_task_new_uses_path_triggered_governance_required_tests_when_not_explicit(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-GOV-FAST-001",
        "--title",
        "governance docs task",
        "--stage",
        "governance-docs",
        "--task-kind",
        "coordination",
        "--execution-mode",
        "shared_coordination",
        "--allowed-dirs",
        "docs/governance/",
        "scripts/",
        "tests/governance/",
        "tests/automation/",
        "--planned-write-paths",
        "docs/governance/CODE_HYGIENE_POLICY.md",
        "--planned-test-paths",
        "tests/governance/",
        "tests/automation/",
    )
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-GOV-FAST-001")

    assert result.returncode == 0, result.stdout + result.stderr
    assert task["required_tests"] == _profile_tests(repo, "governance_fast")


def test_live_governance_capability_descriptions_use_targeted_regressions(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    governance_capability = next(
        item for item in capability_map["capabilities"] if item["capability_id"] == "governance_control_plane"
    )

    assert governance_capability["tests"][:3] == [
        "python scripts/check_repo.py",
        "python scripts/check_hygiene.py src docs tests",
        "python scripts/check_authority_alignment.py",
    ]
    assert "pytest tests/governance -q" not in governance_capability["tests"]
    assert "pytest tests/automation -q" not in governance_capability["tests"]


def test_live_governance_module_baseline_uses_repo_hygiene_only(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    module_map = read_yaml(repo / "docs/governance/MODULE_MAP.yaml")
    governance_module = next(item for item in module_map["modules"] if item["module_id"] == "governance_control_plane")

    assert governance_module["required_tests"] == [
        "python scripts/check_repo.py",
        "python scripts/check_hygiene.py src docs tests",
    ]


def test_fixture_payloads_follow_live_capability_and_module_maps() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    live_capability_map = read_yaml(repo_root / "docs/governance/CAPABILITY_MAP.yaml")
    fixture_capability_map = capability_map_payload()

    for capability in live_capability_map["capabilities"]:
        override = FIXTURE_CAPABILITY_STATUS_OVERRIDES.get(capability["capability_id"])
        if override is not None:
            capability["status"] = override

    assert fixture_capability_map == live_capability_map
    assert module_map_payload() == read_yaml(repo_root / "docs/governance/MODULE_MAP.yaml")


def test_business_parallel_parent_blueprint_uses_targeted_governance_and_runner_tests(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    task_policy = read_yaml(repo / "docs/governance/TASK_POLICY.yaml")
    blueprint = next(
        item
        for item in task_policy["task_blueprints"]
        if item["blueprint_id"] == "business_parallel_parent_stage1_to_stage6"
    )

    assert blueprint["required_tests"] == [
        "python scripts/check_authority_alignment.py",
        "python scripts/validate_contracts.py",
        "python scripts/check_repo.py",
        "python scripts/check_hygiene.py src docs tests",
        "pytest tests/governance/test_task_continuation.py -q",
        "pytest tests/automation/test_automation_runner.py -q",
        "pytest tests/contracts -q",
        "pytest tests/integration -q",
    ]


def test_size_class_preflight_hygiene_commands_use_scoped_args(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    matrix = read_yaml(repo / "docs/governance/TEST_MATRIX.yaml")

    assert matrix["size_class_gates"]["micro"]["preflight"] == [
        "python scripts/check_repo.py",
        "python scripts/check_hygiene.py src docs tests",
    ]
    assert matrix["size_class_gates"]["standard"]["preflight"][:2] == [
        "python scripts/check_repo.py",
        "python scripts/check_hygiene.py src docs tests",
    ]
    assert "python scripts/check_hygiene.py src docs tests" in matrix["size_class_gates"]["heavy"]["preflight"]
