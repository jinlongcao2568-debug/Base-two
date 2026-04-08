from __future__ import annotations

from pathlib import Path
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import governance_console as console  # noqa: E402


def test_render_index_html_contains_core_controls() -> None:
    html = console._render_index_html()
    assert "AX9 治理操作员控制台" in html
    assert "编译候选池" in html
    assert "解释认领决策" in html
    assert "控制台总览" in html
    assert "复制任务" in html
    assert "feedback_toast" in html
    assert "当前任务如下：" in html
    assert "自动化开发底座" not in html
    assert "/api/pool" in html


def test_run_task_ops_returns_structured_result() -> None:
    payload = console._run_task_ops("review-candidate-pool")
    assert "argv" in payload
    assert "returncode" in payload
    assert "stdout" in payload


def test_console_url_is_localhost() -> None:
    assert console._console_url("127.0.0.1", 8765) == "http://127.0.0.1:8765/"


def test_translate_candidate_title_to_chinese() -> None:
    assert (
        console._translate_candidate_title("Stage8 contact-context parallel lanes")
        == "阶段8 联系上下文并行泳道"
    )
    assert (
        console._translate_candidate_title("Stage2 ingestion integration gate")
        == "阶段2 数据采集集成闸门"
    )
    assert (
        console._translate_candidate_title("domain_project_manager preview root")
        == "项目经理领域预览根"
    )


def test_status_and_blocker_labels_translate_to_chinese() -> None:
    assert console._status_label_zh("stale") == "陈旧"
    assert console._blocking_reason_labels(["stale_takeover_ready"]) == ["陈旧候选可接管"]


def test_candidate_summary_marks_stale_takeover_as_resume_only() -> None:
    payload = console._candidate_summary(
        {
            "candidate_id": "stage1-core-contract",
            "title": "Stage1 orchestration contract and fixture boundary",
            "stage": "stage1",
            "module_id": "stage1_orchestration",
            "status": "resumable",
            "claimable": False,
            "fresh_claimable": False,
            "takeover_claimable": False,
            "blocking_reason_codes": ["stale_takeover_blocked"],
            "blocking_reason_text": ["stale worktree is dirty and requires manual checkpoint"],
            "upstream_blocker_candidates": [],
        }
    )
    assert payload["copy_instruction"] == "任务池发现旧任务续接点，先处理该任务，不要重复新开同任务。"
    assert payload["copy_reason"] == "旧任务已暂停，旧工作树还有未收口改动，当前不能直接接管。"


def test_candidate_summary_marks_dependency_wait_as_not_manual_release() -> None:
    payload = console._candidate_summary(
        {
            "candidate_id": "stage2-core-contract",
            "title": "Stage2 ingestion contract and raw payload fixture boundary",
            "stage": "stage2",
            "module_id": "stage2_ingestion",
            "status": "waiting",
            "claimable": False,
            "fresh_claimable": False,
            "takeover_claimable": False,
            "blocking_reason_codes": ["dependency_wait"],
            "blocking_reason_text": ["waiting for stage1-core-contract (resumable)"],
            "upstream_blocker_candidates": ["stage1-core-contract"],
        }
    )
    assert payload["copy_instruction"] == "当前任务尚未解锁，先检查阻塞原因；解除后再回任务池接单。"
    assert payload["operator_reason"] == "前置候选未完成：stage1-core-contract。当前不是人工释放问题。"


def test_run_task_ops_uses_hidden_subprocess_on_windows(monkeypatch) -> None:
    captured = {}

    def fake_run(*args, **kwargs):
        captured["creationflags"] = kwargs.get("creationflags")
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    console._run_task_ops("review-candidate-pool")
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW


def test_cached_pool_payload_reads_cache_without_refresh(monkeypatch, tmp_path) -> None:
    root = tmp_path
    cache_dir = root / ".codex" / "local" / "roadmap_candidates"
    cache_dir.mkdir(parents=True)
    (cache_dir / "summary.yaml").write_text("candidate_count: 1\nfresh_claimable_count: 0\n", encoding="utf-8")
    (cache_dir / "index.yaml").write_text(
        "candidates:\n- candidate_id: stage1-core-contract\n  title: Stage1 orchestration contract and fixture boundary\n  stage: stage1\n  module_id: stage1_orchestration\n  status: waiting\n  candidate_intent: module_root\n  unlock_count: 2\n  blocking_reason_codes: [dependency_wait]\n  upstream_blocker_candidates: [stage0]\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(console, "_repo_root", lambda: root)
    payload = console._cached_pool_payload()
    assert payload["summary"]["candidate_count"] == 1
    assert payload["visible_candidates"][0]["candidate_id"] == "stage1-core-contract"
    assert payload["visible_candidates"][0]["title_zh"] == "阶段1 编排契约与夹具边界"
    assert payload["visible_candidates"][0]["status_zh"] == "等待中"
