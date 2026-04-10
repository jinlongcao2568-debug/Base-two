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
    assert "可领取任务" in html
    assert "当前任务" in html
    assert "已完成任务" in html
    assert "任务总页面" in html
    assert "高级诊断" in html
    assert "/api/intake" in html
    assert "/api/task-catalog" in html


def test_build_current_task_payload_returns_live_task() -> None:
    payload = console._build_current_task_payload(console._repo_root())
    assert payload["page"] == "current"
    assert payload["summary"]["active"] is True
    assert payload["rows"][0]["task_id"] == "TASK-GOV-089"


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
