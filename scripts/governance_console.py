from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import subprocess
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse
import webbrowser

from governance_lib import GovernanceError, configure_utf8_stdio, find_repo_root
from roadmap_explain import (
    explain_candidate,
    explain_candidate_pool,
    explain_claim_decision,
    explain_release_chain,
)
from review_candidate_pool import review_pool


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
PAGE_TITLE = "AX9 Governance Operator Console"


def _repo_root() -> Path:
    return find_repo_root()


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _console_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/"


def _run_task_ops(*args: str) -> dict[str, Any]:
    root = _repo_root()
    result = subprocess.run(
        [sys.executable, str(_script_dir() / "task_ops.py"), *args],
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "argv": ["python", "scripts/task_ops.py", *args],
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _review_pool_payload() -> dict[str, Any]:
    root = _repo_root()
    return review_pool(root)


def _snapshot_payload() -> dict[str, Any]:
    root = _repo_root()
    return {
        "pool": explain_candidate_pool(root),
        "claim_decision": explain_claim_decision(root),
        "review": _review_pool_payload(),
    }


def _render_index_html() -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PAGE_TITLE}</title>
  <style>
    body {{
      margin: 0;
      font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
      background: #0d1117;
      color: #e6edf3;
    }}
    .wrap {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 30px;
    }}
    p.sub {{
      margin: 0 0 20px;
      color: #9fb0c0;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }}
    .card {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 8px 24px rgba(0,0,0,.18);
    }}
    .metric {{
      font-size: 28px;
      font-weight: 700;
      margin: 8px 0 4px;
    }}
    .label {{
      color: #8b949e;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 18px;
    }}
    button {{
      border: 1px solid #2f81f7;
      background: #1f6feb;
      color: #fff;
      border-radius: 10px;
      padding: 10px 14px;
      cursor: pointer;
      font-weight: 600;
    }}
    button.secondary {{
      background: #21262d;
      border-color: #30363d;
    }}
    .split {{
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid #30363d;
      vertical-align: top;
    }}
    th {{
      color: #8b949e;
      font-weight: 600;
    }}
    .pill {{
      display: inline-block;
      border: 1px solid #30363d;
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 12px;
      margin-right: 6px;
      margin-bottom: 6px;
      color: #9fb0c0;
    }}
    .row {{
      margin-bottom: 14px;
    }}
    .candidate-tools {{
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
    }}
    input {{
      background: #0d1117;
      color: #e6edf3;
      border: 1px solid #30363d;
      border-radius: 10px;
      padding: 10px 12px;
      width: 100%;
    }}
    pre {{
      background: #0d1117;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 14px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.45;
    }}
    .status-ready {{ color: #3fb950; }}
    .status-degraded {{ color: #d29922; }}
    .status-blocked {{ color: #f85149; }}
    @media (max-width: 980px) {{
      .grid, .split {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>{PAGE_TITLE}</h1>
    <p class="sub">薄控制台：只展示和调用现有 governance 控制面，不实现第二套调度逻辑。</p>

    <div class="actions">
      <button onclick="runAction('compile-roadmap-candidates')">Compile Candidates</button>
      <button onclick="runAction('refresh-roadmap-candidates')">Refresh Candidate Pool</button>
      <button onclick="runAction('close-ready-execution-tasks')">Close Ready Execution Tasks</button>
      <button onclick="runAction('continue-roadmap')">Continue Roadmap</button>
      <button class="secondary" onclick="loadAll()">Reload Snapshot</button>
    </div>

    <div class="grid">
      <div class="card"><div class="label">Candidate Count</div><div class="metric" id="candidate_count">-</div></div>
      <div class="card"><div class="label">Fresh Claimable</div><div class="metric" id="fresh_claimable_count">-</div></div>
      <div class="card"><div class="label">Takeover Claimable</div><div class="metric" id="takeover_claimable_count">-</div></div>
      <div class="card"><div class="label">Parallelism Deficit</div><div class="metric" id="parallelism_deficit">-</div></div>
    </div>

    <div class="split">
      <div class="card">
        <div class="row">
          <div class="label">Candidate Pool</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Status</th>
              <th>Intent</th>
              <th>Unlock</th>
              <th>Blockers</th>
            </tr>
          </thead>
          <tbody id="candidate_rows"></tbody>
        </table>
      </div>

      <div class="card">
        <div class="row">
          <div class="label">Decision / Detail</div>
        </div>

        <div class="candidate-tools">
          <input id="candidate_id" placeholder="candidate_id，例如 stage1-core-contract">
          <button class="secondary" onclick="loadCandidate()">Explain Candidate</button>
        </div>
        <div class="candidate-tools">
          <input id="release_candidate_id" placeholder="release chain candidate_id">
          <button class="secondary" onclick="loadReleaseChain()">Explain Release Chain</button>
        </div>
        <div class="candidate-tools">
          <button class="secondary" onclick="loadClaimDecision()">Explain Claim Decision</button>
          <button class="secondary" onclick="loadReview()">Review Candidate Pool</button>
        </div>
        <pre id="detail">Loading...</pre>
      </div>
    </div>

    <div class="card" style="margin-top:18px;">
      <div class="label">Last Action</div>
      <pre id="action_output">No action yet.</pre>
    </div>
  </div>

  <script>
    async function fetchJson(path, options) {{
      const res = await fetch(path, options);
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.error || JSON.stringify(payload));
      return payload;
    }}

    function metric(id, value) {{
      document.getElementById(id).textContent = value ?? '-';
    }}

    function summarizeReasons(candidate) {{
      const codes = candidate.blocking_reason_codes || [];
      if (!codes.length) return '-';
      return codes.slice(0, 2).join(', ');
    }}

    function renderPool(pool) {{
      metric('candidate_count', pool.summary.candidate_count);
      metric('fresh_claimable_count', pool.summary.fresh_claimable_count);
      metric('takeover_claimable_count', pool.summary.takeover_claimable_count);
      metric('parallelism_deficit', pool.summary.parallelism_deficit);
      const rows = (pool.top_waiting || []).map(row => `
        <tr>
          <td>${{row.candidate_id}}</td>
          <td>${{(row.status || 'waiting')}}</td>
          <td>${{(row.candidate_intent || '-')}}</td>
          <td>${{(row.unlock_count ?? '-')}}</td>
          <td>${{(row.blocking_reason_codes || []).slice(0,2).join(', ') || '-'}}</td>
        </tr>
      `).join('');
      document.getElementById('candidate_rows').innerHTML = rows;
    }}

    async function loadAll() {{
      const payload = await fetchJson('/api/pool');
      renderPool(payload);
      document.getElementById('detail').textContent = JSON.stringify(payload, null, 2);
    }}

    async function loadCandidate() {{
      const candidateId = document.getElementById('candidate_id').value.trim();
      if (!candidateId) return;
      const payload = await fetchJson(`/api/candidate?candidate_id=${{encodeURIComponent(candidateId)}}`);
      document.getElementById('detail').textContent = JSON.stringify(payload, null, 2);
    }}

    async function loadReleaseChain() {{
      const candidateId = document.getElementById('release_candidate_id').value.trim();
      if (!candidateId) return;
      const payload = await fetchJson(`/api/release-chain?candidate_id=${{encodeURIComponent(candidateId)}}`);
      document.getElementById('detail').textContent = JSON.stringify(payload, null, 2);
    }}

    async function loadClaimDecision() {{
      const payload = await fetchJson('/api/claim-decision');
      document.getElementById('detail').textContent = JSON.stringify(payload, null, 2);
    }}

    async function loadReview() {{
      const payload = await fetchJson('/api/review');
      document.getElementById('detail').textContent = JSON.stringify(payload, null, 2);
    }}

    async function runAction(action) {{
      const payload = await fetchJson(`/api/action/${{action}}`, {{ method: 'POST' }});
      document.getElementById('action_output').textContent = JSON.stringify(payload, null, 2);
      await loadAll();
    }}

    loadAll().catch(error => {{
      document.getElementById('detail').textContent = String(error);
    }});
  </script>
</body>
</html>"""


class GovernanceConsoleHandler(BaseHTTPRequestHandler):
    def _write_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._write_html(_render_index_html())
                return
            if parsed.path == "/api/pool":
                self._write_json(_snapshot_payload()["pool"])
                return
            if parsed.path == "/api/review":
                self._write_json(_review_pool_payload())
                return
            if parsed.path == "/api/claim-decision":
                self._write_json(explain_claim_decision(_repo_root()))
                return
            if parsed.path == "/api/candidate":
                candidate_id = parse_qs(parsed.query).get("candidate_id", [""])[0]
                self._write_json(explain_candidate(_repo_root(), candidate_id))
                return
            if parsed.path == "/api/release-chain":
                candidate_id = parse_qs(parsed.query).get("candidate_id", [""])[0]
                self._write_json(explain_release_chain(_repo_root(), candidate_id))
                return
            self._write_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        except GovernanceError as error:
            self._write_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as error:  # noqa: BLE001
            self._write_json({"error": f"internal error: {error}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if not parsed.path.startswith("/api/action/"):
                self._write_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            action = parsed.path.split("/api/action/", 1)[1]
            mapping = {
                "compile-roadmap-candidates": ("compile-roadmap-candidates",),
                "refresh-roadmap-candidates": ("refresh-roadmap-candidates",),
                "close-ready-execution-tasks": ("close-ready-execution-tasks",),
                "continue-roadmap": ("continue-roadmap",),
            }
            if action not in mapping:
                self._write_json({"error": f"unsupported action: {action}"}, status=HTTPStatus.BAD_REQUEST)
                return
            self._write_json(_run_task_ops(*mapping[action]))
        except Exception as error:  # noqa: BLE001
            self._write_json({"error": f"internal error: {error}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def start_console(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, *, open_browser: bool = True) -> int:
    url = _console_url(host, port)
    if _port_in_use(host, port):
        if open_browser:
            webbrowser.open(url)
        print(f"[OK] governance console already running at {url}")
        return 0

    server = ThreadingHTTPServer((host, port), GovernanceConsoleHandler)
    if open_browser:
        webbrowser.open(url)
    print(f"[OK] governance console serving at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9 Governance Operator Console")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    return parser


def main() -> int:
    configure_utf8_stdio()
    args = build_parser().parse_args()
    return start_console(args.host, args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
