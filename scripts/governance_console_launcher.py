from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

from control_plane_root import build_governance_runtime_stamp, resolve_control_plane_root


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
WAIT_ATTEMPTS = 50
WAIT_SLEEP_SECONDS = 0.1
SCRIPT_ROOT = Path(__file__).resolve().parent
CONSOLE_SCRIPT = SCRIPT_ROOT / "governance_console.py"


def console_url(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return f"http://{host}:{port}/"


def browser_profile_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    return Path(local_app_data) / "AX9" / "GovernanceConsoleBrowser"


def is_console_reachable(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=0.35) as response:
            return int(getattr(response, "status", 200)) > 0
    except (OSError, urllib.error.URLError, ValueError):
        return False


def _fetch_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=0.5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, ValueError, json.JSONDecodeError):
        return None


def console_requires_restart(url: str) -> bool:
    payload = _fetch_json(f"{url.rstrip('/')}/api/review")
    if not payload:
        return False
    runtime_stamp = (((payload.get("full_clone_pool_audit") or {}).get("governance_runtime_stamp")) or {})
    current_stamp = build_governance_runtime_stamp(resolve_control_plane_root())
    return (
        runtime_stamp.get("control_plane_head") != current_stamp.get("control_plane_head")
        or runtime_stamp.get("governance_scripts_hash") != current_stamp.get("governance_scripts_hash")
    )


def _windows_hidden_creationflags() -> int:
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        return subprocess.CREATE_NO_WINDOW
    return 0


def _run_hidden_command(argv: list[str], *, cwd: Path | None = None, text: bool = True) -> subprocess.CompletedProcess:
    kwargs = {
        "cwd": cwd,
        "check": False,
        "capture_output": True,
    }
    creationflags = _windows_hidden_creationflags()
    if creationflags:
        kwargs["creationflags"] = creationflags
    if text:
        kwargs.update(
            {
                "text": True,
                "encoding": "utf-8",
                "errors": "replace",
            }
        )
    return subprocess.run(argv, **kwargs)


def port_owner_pid(port: int) -> int | None:
    try:
        result = _run_hidden_command(["netstat", "-ano", "-p", "tcp"])
    except OSError:
        return None
    target = f":{port}"
    for line in (result.stdout or "").splitlines():
        normalized = " ".join(line.split())
        if "LISTENING" not in normalized or target not in normalized:
            continue
        parts = normalized.split()
        if len(parts) < 5:
            continue
        local_addr = parts[1]
        if not local_addr.endswith(target):
            continue
        try:
            return int(parts[-1])
        except ValueError:
            return None
    return None


def terminate_console_service(port: int) -> bool:
    pid = port_owner_pid(port)
    if pid is None:
        return False
    try:
        if os.name == "nt":
            _run_hidden_command(["taskkill", "/PID", str(pid), "/F"])
        else:
            os.kill(pid, 15)
    except OSError:
        return False
    return True


def launch_background_service() -> None:
    creationflags = _windows_hidden_creationflags()
    subprocess.Popen(
        [sys.executable, str(CONSOLE_SCRIPT), "--no-browser"],
        cwd=SCRIPT_ROOT.parent,
        creationflags=creationflags,
        close_fds=True,
    )


def wait_for_console(url: str, attempts: int = WAIT_ATTEMPTS, sleep_seconds: float = WAIT_SLEEP_SECONDS) -> bool:
    for _ in range(attempts):
        if is_console_reachable(url):
            return True
        time.sleep(sleep_seconds)
    return False


def detect_browser_path() -> Path | None:
    candidates = [
        Path(os.environ.get("ProgramFiles", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
    ]
    for candidate in candidates:
        if str(candidate) and candidate.exists():
            return candidate
    return None


def build_browser_command(browser_path: Path, url: str, profile_dir: Path) -> list[str]:
    return [
        str(browser_path),
        f"--app={url}",
        f"--user-data-dir={profile_dir}",
        "--disable-extensions",
        "--disable-component-extensions-with-background-pages",
        "--new-window",
        "--no-first-run",
        "--no-default-browser-check",
    ]


def open_console_window(url: str) -> None:
    browser_path = detect_browser_path()
    if browser_path is None:
        if os.name == "nt":
            os.startfile(url)
        else:
            webbrowser.open(url)
        return

    profile_dir = browser_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)
    subprocess.Popen(
        build_browser_command(browser_path, url, profile_dir),
        cwd=browser_path.parent,
        close_fds=True,
    )


def main() -> int:
    url = console_url()
    if is_console_reachable(url) and console_requires_restart(url):
        terminate_console_service(DEFAULT_PORT)
        time.sleep(0.4)
    if not is_console_reachable(url):
        launch_background_service()
        wait_for_console(url)
    open_console_window(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
