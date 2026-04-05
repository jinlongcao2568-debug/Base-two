from pathlib import Path

from .helpers import RENDER_RUNTIME_PROMPTS_SCRIPT, init_governance_repo, run_python


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_render_runtime_prompts_writes_profiles_from_catalog(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    result = run_python(RENDER_RUNTIME_PROMPTS_SCRIPT, repo)
    coordinator = (repo / "docs/governance/runtime_prompts/coordinator.md").read_text(encoding="utf-8")
    worker = (repo / "docs/governance/runtime_prompts/worker.md").read_text(encoding="utf-8")
    reviewer = (repo / "docs/governance/runtime_prompts/reviewer.md").read_text(encoding="utf-8")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "coordinator_profile" in coordinator
    assert "Route tasks, validate boundaries, manage ledgers, and decide closeout gates." in coordinator
    assert "worker_profile" in worker
    assert "Execute only inside the assigned task or lane scope." in worker
    assert "reviewer_profile" in reviewer
    assert "Review for bugs, regressions, missing tests, and weak rollback stories." in reviewer


def test_render_runtime_prompts_check_detects_drift(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    render = run_python(RENDER_RUNTIME_PROMPTS_SCRIPT, repo)
    assert render.returncode == 0, render.stdout + render.stderr

    target = repo / "docs/governance/runtime_prompts/coordinator.md"
    target.write_text("drifted\n", encoding="utf-8")
    check = run_python(RENDER_RUNTIME_PROMPTS_SCRIPT, repo, "--check")

    assert check.returncode == 1
    assert "runtime prompt drift" in check.stdout


def test_live_docs_align_on_runtime_prompt_governance() -> None:
    readme = (REPO_ROOT / "docs/governance/README.md").read_text(encoding="utf-8")
    manual = (REPO_ROOT / "docs/governance/OPERATOR_MANUAL.md").read_text(encoding="utf-8")
    operating_model = (REPO_ROOT / "docs/governance/AUTOMATION_OPERATING_MODEL.md").read_text(encoding="utf-8")

    for content in (readme, manual, operating_model):
        assert "runtime_prompts" in content
        assert "custom instructions" in content
