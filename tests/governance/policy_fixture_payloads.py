from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


_CANONICAL_TASK_POLICY_PATH = Path(__file__).resolve().parents[2] / "docs/governance/TASK_POLICY.yaml"


def task_policy_payload() -> dict[str, Any]:
    with _CANONICAL_TASK_POLICY_PATH.open("r", encoding="utf-8") as handle:
        return copy.deepcopy(yaml.safe_load(handle) or {})
