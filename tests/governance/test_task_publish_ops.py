from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .helpers import (
    AUTOMATION_INTENT_SCRIPT,
    TASK_OPS_SCRIPT,
    git_commit_all,
    init_governance_repo,
    read_yaml,
    run_python,
    set_idle_control_plane,
    write_yaml,
)


def _mark_review_ready(repo: Path) -> None:
    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "worker-finish",
        "TASK-BASE-001",
        "--summary",
        "review ready",
        "--tests",
        "pytest tests/base -q",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    git_commit_all(repo, "prepare review-ready task")


def _move_live_task_to_branch(repo: Path, branch: str) -> None:
    subprocess.run(["git", "switch", "-c", branch], cwd=repo, check=True, capture_output=True, text=True)
    current = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    current["branch"] = branch
    write_yaml(repo / "docs/governance/CURRENT_TASK.yaml", current)

    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task = next(item for item in registry["tasks"] if item["task_id"] == "TASK-BASE-001")
    task["branch"] = branch
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)

    worktrees = read_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml")
    entry = next(item for item in worktrees["entries"] if item["task_id"] == "TASK-BASE-001")
    entry["branch"] = branch
    write_yaml(repo / "docs/governance/WORKTREE_REGISTRY.yaml", worktrees)


def _run_preflight(repo: Path, action: str, env: dict[str, str] | None = None) -> dict:
    result = run_python(TASK_OPS_SCRIPT, repo, "publish-preflight", "--action", action, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def _add_origin_remote(repo: Path, tmp_path: Path) -> Path:
    remote = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", remote.as_posix()], check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", remote.as_posix()], cwd=repo, check=True, capture_output=True, text=True)
    return remote


def _install_fake_gh(
    tmp_path: Path,
    *,
    authenticated: bool = True,
    existing_pr: bool = False,
    pr_url: str = "https://example.com/pr/1",
) -> dict[str, str]:
    bin_dir = tmp_path / "fake-gh-bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "fake_gh.py"
    script.write_text(
        "\n".join(
            [
                "import json, os, sys",
                "args = sys.argv[1:]",
                "if args[:2] == ['auth', 'status']:",
                "    if os.environ.get('FAKE_GH_AUTH', '1') != '1':",
                "        print('not logged in', file=sys.stderr)",
                "        raise SystemExit(1)",
                "    print('Logged in to github.com')",
                "    raise SystemExit(0)",
                "if args[:2] == ['pr', 'list']:",
                "    if os.environ.get('FAKE_GH_EXISTING_PR', '0') == '1':",
                "        url = os.environ.get('FAKE_GH_PR_URL', 'https://example.com/pr/9')",
                "        print(json.dumps([{'number': 9, 'url': url}]))",
                "    else:",
                "        print('[]')",
                "    raise SystemExit(0)",
                "if args[:2] == ['pr', 'create']:",
                "    print(os.environ.get('FAKE_GH_PR_URL', 'https://example.com/pr/1'))",
                "    raise SystemExit(0)",
                "print('unsupported gh call: ' + ' '.join(args), file=sys.stderr)",
                "raise SystemExit(1)",
            ]
        ),
        encoding="utf-8",
    )
    launcher = bin_dir / "gh.cmd"
    launcher.write_text(f'@echo off\r\n"{sys.executable}" "%~dp0fake_gh.py" %*\r\n', encoding="utf-8")
    env = {
        "PATH": f"{bin_dir}{os.pathsep}" + os.environ.get("PATH", ""),
        "FAKE_GH_AUTH": "1" if authenticated else "0",
        "FAKE_GH_EXISTING_PR": "1" if existing_pr else "0",
        "FAKE_GH_PR_URL": pr_url,
    }
    return env


def _automation_preflight(repo: Path, utterance: str, env: dict[str, str] | None = None) -> dict:
    result = run_python(AUTOMATION_INTENT_SCRIPT, repo, "preflight", "--utterance", utterance, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_publish_preflight_ready_for_review_task_with_scoped_dirty_changes(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)
    (repo / "src/base/module.py").write_text("def base_value():\n    return 2\n", encoding="utf-8")

    payload = _run_preflight(repo, "commit-task-results")

    assert payload["status"] == "ready"
    assert payload["task_id"] == "TASK-BASE-001"
    assert "src/base/module.py" in payload["staged_candidate_paths"]


def test_publish_preflight_blocks_non_publishable_statuses(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)

    blocked_payload = _run_preflight(repo, "publish-task-results")
    assert blocked_payload["status"] == "blocked"
    assert any("require one of done, review" in blocker or "require one of review, done" in blocker for blocker in blocked_payload["blockers"])


def test_publish_actions_block_when_idle_without_explicit_task_id(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    set_idle_control_plane(repo)
    git_commit_all(repo, "idle control plane")

    for command in ("commit-task-results", "push-task-branch", "create-task-pr", "publish-task-results"):
        result = run_python(TASK_OPS_SCRIPT, repo, command)
        assert result.returncode == 1
        assert "no live current task" in (result.stdout + result.stderr)


def test_commit_task_results_blocks_out_of_scope_dirty_paths(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)
    (repo / "src/base/module.py").write_text("def base_value():\n    return 2\n", encoding="utf-8")
    (repo / "src/outside.py").write_text("print('outside')\n", encoding="utf-8")

    result = run_python(TASK_OPS_SCRIPT, repo, "commit-task-results")

    assert result.returncode == 1
    assert "outside task publish scope" in (result.stdout + result.stderr)


def test_commit_task_results_blocks_when_no_scoped_changes_exist(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "commit-task-results")

    assert result.returncode == 1
    assert "no task-scoped changes" in (result.stdout + result.stderr)


def test_push_task_branch_blocks_without_origin_remote(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "push-task-branch")

    assert result.returncode == 1
    assert "remote `origin` is not configured" in (result.stdout + result.stderr)


def test_create_task_pr_blocks_without_gh(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)
    _move_live_task_to_branch(repo, "feat/task-base-pr")
    _add_origin_remote(repo, tmp_path)

    result = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "create-task-pr",
        env={"AX9_GH_CLI": "gh-does-not-exist"},
    )

    assert result.returncode == 1
    assert "GitHub CLI `gh` is not available" in (result.stdout + result.stderr)


def test_create_task_pr_blocks_when_gh_is_not_authenticated(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)
    _move_live_task_to_branch(repo, "feat/task-base-pr")
    _add_origin_remote(repo, tmp_path)
    env = _install_fake_gh(tmp_path, authenticated=False)

    result = run_python(TASK_OPS_SCRIPT, repo, "create-task-pr", env=env)

    assert result.returncode == 1
    assert "not authenticated" in (result.stdout + result.stderr)


def test_create_task_pr_blocks_when_pr_already_exists(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)
    _move_live_task_to_branch(repo, "feat/task-base-pr")
    _add_origin_remote(repo, tmp_path)
    env = _install_fake_gh(tmp_path, authenticated=True, existing_pr=True)

    result = run_python(TASK_OPS_SCRIPT, repo, "create-task-pr", env=env)

    assert result.returncode == 1
    assert "already exists" in (result.stdout + result.stderr)


def test_publish_task_results_runs_full_chain_with_mocked_git_and_gh(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)
    _move_live_task_to_branch(repo, "feat/task-base-publish")
    _add_origin_remote(repo, tmp_path)
    env = _install_fake_gh(tmp_path, authenticated=True, existing_pr=False, pr_url="https://example.com/pr/42")
    (repo / "src/base/module.py").write_text("def base_value():\n    return 42\n", encoding="utf-8")

    result = run_python(TASK_OPS_SCRIPT, repo, "publish-task-results", env=env)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "https://example.com/pr/42" in result.stdout
    assert "publish TASK-BASE-001" in subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    runlog = (repo / "docs/governance/runlogs/TASK-BASE-001-RUNLOG.md").read_text(encoding="utf-8")
    assert "## Publish Log" in runlog
    assert "commit requested" in runlog


def test_publish_intents_map_to_four_actions(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    _mark_review_ready(repo)
    _move_live_task_to_branch(repo, "feat/task-base-intents")
    _add_origin_remote(repo, tmp_path)
    env = _install_fake_gh(tmp_path, authenticated=True, existing_pr=False)
    (repo / "src/base/module.py").write_text("def base_value():\n    return 3\n", encoding="utf-8")

    commit_payload = _automation_preflight(repo, "提交当前任务成果")
    push_payload = _automation_preflight(repo, "推送当前任务分支")
    pr_payload = _automation_preflight(repo, "为当前任务开PR", env=env)
    publish_payload = _automation_preflight(repo, "发布当前任务成果", env=env)

    assert commit_payload["intent_id"] == "commit-task-results"
    assert push_payload["intent_id"] == "push-task-branch"
    assert pr_payload["intent_id"] == "create-task-pr"
    assert publish_payload["intent_id"] == "publish-task-results"
