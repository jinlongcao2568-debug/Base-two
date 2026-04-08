from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_compiler_mode_files(repo: Path) -> None:
    for relative in (
        Path("docs/governance/ROADMAP_BACKLOG.yaml"),
        Path("docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml"),
    ):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((REPO_ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")


def test_compile_roadmap_candidates_generates_multi_root_graph(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_compiler_mode_files(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "compile-roadmap-candidates")
    compiled = read_yaml(repo / ".codex/local/roadmap_candidates/compiled.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert compiled["graph_version"] == "roadmap_compiled_graph_v1"
    assert len(compiled["candidates"]) > 1
    root_candidates = [
        candidate
        for candidate in compiled["candidates"]
        if candidate.get("candidate_intent") in {"module_root", "module_preview_root"}
        and candidate.get("parent_candidate_id") is None
    ]
    assert len(root_candidates) > 1


def test_module_map_change_without_recompile_blocks_dispatch(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    _write_compiler_mode_files(repo)
    compiled = run_python(TASK_OPS_SCRIPT, repo, "compile-roadmap-candidates")
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr

    module_map = read_yaml(repo / "docs/governance/MODULE_MAP.yaml")
    module_map["updated_at"] = "2099-01-01T00:00:00+08:00"
    write_yaml(repo / "docs/governance/MODULE_MAP.yaml", module_map)

    result = run_python(TASK_OPS_SCRIPT, repo, "plan-roadmap-candidates")

    assert result.returncode == 1
    assert "compiled roadmap candidate graph is stale" in result.stdout
