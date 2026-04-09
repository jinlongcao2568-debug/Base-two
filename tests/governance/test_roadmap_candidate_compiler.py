from __future__ import annotations

from pathlib import Path
import subprocess

from .helpers import TASK_OPS_SCRIPT, git_commit_all, init_governance_repo, read_yaml, run_python, set_idle_control_plane, write_yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "roadmap_candidate_compiler.py"


def _write_compiler_mode_files(repo: Path) -> None:
    for relative in (
        Path("docs/governance/ROADMAP_BACKLOG.yaml"),
        Path("docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml"),
    ):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((REPO_ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")


def _write_full_clone_pool(repo: Path, clone_path: Path) -> None:
    write_yaml(
        repo / "docs/governance/FULL_CLONE_POOL.yaml",
        {
            "version": "1.0",
            "updated_at": "2026-04-08T00:00:00+08:00",
            "status": "active",
            "control_plane_root": str(repo).replace("\\", "/"),
            "slots": [
                {
                    "slot_id": "worker-01",
                    "path": str(clone_path).replace("\\", "/"),
                    "branch": "codex/worker-01-idle",
                    "idle_branch": "codex/worker-01-idle",
                    "status": "ready",
                    "current_task_id": None,
                }
            ],
        },
    )


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


def test_direct_candidate_compiler_script_from_clone_writes_only_to_control_plane(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    clone_path = tmp_path / "clone-worker-01"
    _write_full_clone_pool(repo, clone_path)
    git_commit_all(repo, "prepare full clone slot")
    subprocess.run(["git", "clone", "--local", str(repo), str(clone_path)], check=True, capture_output=True, text=True)
    _write_compiler_mode_files(repo)

    result = run_python(SCRIPT, clone_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert (repo / ".codex/local/roadmap_candidates/compiled.yaml").exists()
    assert not (clone_path / ".codex/local/roadmap_candidates/compiled.yaml").exists()
