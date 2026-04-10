from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import governance_console as console  # noqa: E402
import governance_console_launcher as launcher  # noqa: E402


def test_render_index_html_contains_task_center_navigation() -> None:
    html = console._render_index_html()
    assert "AX9 治理操作员控制台" in html
    assert "可领取任务" in html
    assert "当前任务" in html
    assert "已完成任务" in html
    assert "任务总页面" in html
    assert "高级诊断" in html
    assert "前台自动刷新：开启" in html
    assert "/api/intake" in html
    assert "/api/current-task" in html
    assert "/api/completed-tasks" in html
    assert "/api/task-catalog" in html
    assert "/api/diagnostics" in html
    assert "worker-01" not in html
    assert "AX9 console" not in html


def test_run_task_ops_returns_structured_result() -> None:
    payload = console._run_task_ops("review-candidate-pool")
    assert "argv" in payload
    assert "returncode" in payload
    assert "stdout" in payload


def test_console_url_is_localhost() -> None:
    assert console._console_url("127.0.0.1", 8765) == "http://127.0.0.1:8765/"


def test_build_current_task_payload_returns_live_task() -> None:
    payload = console._build_current_task_payload(console._repo_root())
    assert payload["page"] == "current"
    assert payload["summary"]["active"] is True
    assert payload["rows"][0]["task_id"] == "TASK-GOV-089"
    assert payload["rows"][0]["page_status"] == "in_progress"


def test_build_completed_tasks_payload_uses_task_registry_only() -> None:
    payload = console._build_completed_tasks_payload(console._repo_root())
    assert payload["page"] == "completed"
    assert payload["summary"]["completed_count"] >= 1
    assert all(row["page_status"] == "completed" for row in payload["rows"])
    assert all(row["source"] == "任务登记" for row in payload["rows"])


def test_build_task_catalog_payload_includes_route_status_mapping() -> None:
    payload = console._build_task_catalog_payload(console._repo_root())
    row = next(item for item in payload["rows"] if item["candidate_id"] == "stage2-source-family-lanes")
    assert row["page_status"] == "available"
    assert row["module_id"] == "stage2_ingestion"
    assert row["source"] == "路线图总表"


def test_build_intake_payload_exposes_claimable_task_fields() -> None:
    payload = console._build_intake_payload(console._repo_root())
    assert payload["page"] == "intake"
    assert payload["summary"]["total_rows"] >= 1
    row = payload["rows"][0]
    assert row["page_status"] == "available"
    assert row["candidate_id"]
    assert row["write_paths"]
    assert row["required_tests"]


def test_build_diagnostics_payload_keeps_governance_details() -> None:
    payload = console._build_diagnostics_payload(console._repo_root())
    assert payload["page"] == "diagnostics"
    assert "diagnostic_row_count" in payload["summary"]
    assert isinstance(payload["rows"], list)


def test_candidate_index_payload_prefers_cached_index(monkeypatch, tmp_path) -> None:
    cache_dir = tmp_path / ".codex" / "local" / "roadmap_candidates"
    cache_dir.mkdir(parents=True)
    (cache_dir / "index.yaml").write_text(
        "candidates:\n- candidate_id: cached-task\n  title: Cached task\n  stage: stage2\n  module_id: stage2_ingestion\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(console, "build_roadmap_candidate_index", lambda root: (_ for _ in ()).throw(AssertionError("should not rebuild")))
    payload = console._candidate_index_payload(tmp_path)
    assert payload["candidates"][0]["candidate_id"] == "cached-task"


def test_decorate_claim_payload_hides_slot_wording_in_blockers() -> None:
    root = console._repo_root()
    payload = console._decorate_claim_payload(root, console.explain_claim_decision(root))
    assert payload["selected_candidate_id"] == "stage2-source-family-lanes"
    blocked = payload["blocked_candidates"][0]
    assert blocked["blockers_zh"]
    assert all("worker-" not in reason for reason in blocked["blockers_zh"])
    assert all("slot" not in reason.lower() for reason in blocked["blockers_zh"])


def test_start_console_opens_browser_only_for_new_server(monkeypatch) -> None:
    opened = []
    created = []

    class DummyServer:
        def __init__(self, address, handler):
            created.append((address, handler))

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            return None

    monkeypatch.setattr(console, "_port_in_use", lambda host, port: False)
    monkeypatch.setattr(console, "ThreadingHTTPServer", DummyServer)
    monkeypatch.setattr(console, "_open_console_url", lambda url: opened.append(url))

    result = console.start_console(open_browser=True)

    assert result == 0
    assert created == [(("127.0.0.1", 8765), console.GovernanceConsoleHandler)]
    assert opened == ["http://127.0.0.1:8765/"]


def test_start_console_does_not_open_browser_when_console_already_running(monkeypatch) -> None:
    opened = []
    monkeypatch.setattr(console, "_port_in_use", lambda host, port: True)
    monkeypatch.setattr(console, "_open_console_url", lambda url: opened.append(url))

    result = console.start_console(open_browser=True)

    assert result == 0
    assert opened == []


def test_launcher_restarts_stale_console_before_opening(monkeypatch) -> None:
    events: list[str] = []
    monkeypatch.setattr(launcher, "is_console_reachable", lambda url: True if not events else False)
    monkeypatch.setattr(launcher, "console_requires_restart", lambda url: True)
    monkeypatch.setattr(launcher, "terminate_console_service", lambda port: events.append(f"kill:{port}") or True)
    monkeypatch.setattr(launcher, "launch_background_service", lambda: events.append("launch"))
    monkeypatch.setattr(launcher, "wait_for_console", lambda url: True)
    monkeypatch.setattr(launcher, "open_console_window", lambda url: events.append(f"open:{url}"))

    result = launcher.main()

    assert result == 0
    assert events == ["kill:8765", "launch", "open:http://127.0.0.1:8765/"]


def test_launcher_port_owner_pid_uses_hidden_subprocess_on_windows(monkeypatch) -> None:
    captured = {}

    def fake_run(*args, **kwargs):
        captured["creationflags"] = kwargs.get("creationflags")

        class Result:
            stdout = "  TCP    127.0.0.1:8765    0.0.0.0:0    LISTENING    4321\n"

        return Result()

    monkeypatch.setattr(launcher.subprocess, "run", fake_run)

    assert launcher.port_owner_pid(8765) == 4321
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW


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
