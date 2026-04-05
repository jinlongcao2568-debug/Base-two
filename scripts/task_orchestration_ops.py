from __future__ import annotations

import argparse

from governance_lib import find_repo_root
from orchestration_runtime import build_orchestration_status, render_status


def cmd_orchestration_status(args: argparse.Namespace) -> int:
    root = find_repo_root()
    status = build_orchestration_status(root)
    print(render_status(status, args.format).rstrip())
    return 0
