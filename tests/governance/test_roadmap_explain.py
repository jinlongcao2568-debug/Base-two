from __future__ import annotations

import json
from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, run_python, set_idle_control_plane
from .test_roadmap_candidate_compiler import _write_compiler_mode_files


def test_explain_candidate_returns_reason_taxonomy_and_release_forecast(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_compiler_mode_files(repo)
    compile_result = run_python(TASK_OPS_SCRIPT, repo, "compile-roadmap-candidates")
    assert compile_result.returncode == 0, compile_result.stdout + compile_result.stderr

    result = run_python(TASK_OPS_SCRIPT, repo, "explain-candidate", "stage1-core-contract")
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["candidate_id"] == "stage1-core-contract"
    assert "release_forecast" in payload
    assert "source_authority" in payload
    assert "blocking_reason_codes" in payload


def test_explain_claim_decision_returns_selected_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_compiler_mode_files(repo)
    compile_result = run_python(TASK_OPS_SCRIPT, repo, "compile-roadmap-candidates")
    assert compile_result.returncode == 0, compile_result.stdout + compile_result.stderr

    result = run_python(TASK_OPS_SCRIPT, repo, "explain-claim-decision")
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["selected_candidate_id"] is not None
    assert isinstance(payload["safe_candidates"], list)


def test_explain_release_chain_returns_downstream_chain(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_compiler_mode_files(repo)
    compile_result = run_python(TASK_OPS_SCRIPT, repo, "compile-roadmap-candidates")
    assert compile_result.returncode == 0, compile_result.stdout + compile_result.stderr

    result = run_python(TASK_OPS_SCRIPT, repo, "explain-release-chain", "stage1-core-contract")
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["candidate_id"] == "stage1-core-contract"
    assert isinstance(payload["downstream_chain"], list)
