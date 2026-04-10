from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import automation_runner as automation_runner_module  # noqa: E402


def test_run_step_uses_hidden_subprocess_on_windows(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run(*args, **kwargs):
        captured["creationflags"] = kwargs.get("creationflags")

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(automation_runner_module.subprocess, "run", fake_run)

    result = automation_runner_module.run_step(tmp_path, "scripts/task_ops.py", "review-candidate-pool")

    assert result.returncode == 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW
