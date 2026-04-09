from __future__ import annotations

import subprocess
import sys


def _creationflags() -> int:
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        return subprocess.CREATE_NO_WINDOW
    return 0


def main() -> int:
    args = sys.argv[1:]
    command = [sys.executable, "-m", "pytest", "-m", "not slow", *args]
    result = subprocess.run(command, text=True, encoding="utf-8", errors="replace", creationflags=_creationflags())
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
