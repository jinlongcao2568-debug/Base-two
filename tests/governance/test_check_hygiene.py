from __future__ import annotations

from pathlib import Path

from .helpers import CHECK_HYGIENE_SCRIPT, init_governance_repo, read_yaml, run_python, write_yaml


def test_check_hygiene_passes_on_small_files(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(CHECK_HYGIENE_SCRIPT, repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_hygiene_blocks_oversized_src_file(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    oversized = "\n".join(f"line_{index} = {index}" for index in range(0, 505))
    (repo / "src/base/too_big.py").write_text(oversized, encoding="utf-8")
    result = run_python(CHECK_HYGIENE_SCRIPT, repo)
    assert result.returncode == 1
    assert "file length" in result.stdout


def test_check_hygiene_blocks_cross_stage_imports(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    (repo / "src/stage7_demo").mkdir(parents=True, exist_ok=True)
    (repo / "src/stage7_demo/mixed.py").write_text(
        "from src.stage6_other import thing\n\n"
        "def run():\n"
        "    return thing\n",
        encoding="utf-8",
    )
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current_task["allowed_dirs"] = ["src/stage7_demo/"]
    current_task["planned_write_paths"] = ["src/stage7_demo/"]
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current_task)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"][0]["allowed_dirs"] = ["src/stage7_demo/"]
    registry["tasks"][0]["planned_write_paths"] = ["src/stage7_demo/"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    result = run_python(CHECK_HYGIENE_SCRIPT, repo)
    assert result.returncode == 1
    assert "cross-stage imports" in result.stdout


def test_check_hygiene_no_longer_flags_control_plane_hotspots(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(
        CHECK_HYGIENE_SCRIPT,
        repo,
        "scripts/check_authority_alignment.py",
        "scripts/check_repo.py",
        "scripts/governance_lib.py",
        "scripts/governance_controls.py",
        "scripts/task_ops.py",
        "scripts/validate_contracts.py",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "scripts/check_authority_alignment.py" not in result.stdout
    assert "scripts/check_repo.py" not in result.stdout
    assert "scripts/governance_lib.py" not in result.stdout
    assert "scripts/governance_controls.py" not in result.stdout
    assert "scripts/task_ops.py" not in result.stdout
    assert "scripts/validate_contracts.py" not in result.stdout


def test_check_hygiene_no_longer_flags_test_hotspot_files(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    result = run_python(
        CHECK_HYGIENE_SCRIPT,
        repo,
        "tests/automation/test_automation_runner.py",
        "tests/governance/fixture_payloads.py",
        "tests/governance/test_check_repo.py",
        "tests/governance/test_task_ops.py",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "tests/automation/test_automation_runner.py" not in result.stdout
    assert "tests/governance/fixture_payloads.py" not in result.stdout
    assert "tests/governance/test_check_repo.py" not in result.stdout
    assert "tests/governance/test_task_ops.py" not in result.stdout
