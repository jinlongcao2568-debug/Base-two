from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import governance_console as console  # noqa: E402


def test_render_index_html_contains_core_controls() -> None:
    html = console._render_index_html()
    assert "AX9 Governance Operator Console" in html
    assert "Compile Candidates" in html
    assert "Explain Claim Decision" in html
    assert "/api/pool" in html


def test_run_task_ops_returns_structured_result() -> None:
    payload = console._run_task_ops("review-candidate-pool")
    assert "argv" in payload
    assert "returncode" in payload
    assert "stdout" in payload


def test_console_url_is_localhost() -> None:
    assert console._console_url("127.0.0.1", 8765) == "http://127.0.0.1:8765/"
