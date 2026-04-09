from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml

from governance_lib import GovernanceError


MVP_SCOPE_FILE = Path("docs/product/MVP_SCOPE.md")


def _read_frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise GovernanceError(f"missing required frontmatter file: {path.as_posix()}")
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise GovernanceError(f"frontmatter missing or malformed: {path.as_posix()}")
    return yaml.safe_load(match.group(1)) or {}


def load_mvp_scope_policy(root: Path) -> dict[str, Any]:
    frontmatter = _read_frontmatter(root / MVP_SCOPE_FILE)
    scope = str(frontmatter.get("mvp_scope") or "").strip()
    included = [str(stage) for stage in (frontmatter.get("included_stages") or []) if stage]
    if included:
        allowed = set(included)
    elif scope == "stage2_to_stage6":
        allowed = {"stage2", "stage3", "stage4", "stage5", "stage6"}
    elif scope == "stage1_to_stage6":
        allowed = {"stage1", "stage2", "stage3", "stage4", "stage5", "stage6"}
    elif scope == "stage1_to_stage9":
        allowed = {"stage1", "stage2", "stage3", "stage4", "stage5", "stage6", "stage7", "stage8", "stage9"}
    else:
        raise GovernanceError("MVP scope frontmatter is missing or invalid")
    return {"scope": scope or "custom", "allowed_stages": allowed}


def ensure_mvp_scope_matches_business_scope(root: Path, business_scope: Any) -> dict[str, Any]:
    mvp_policy = load_mvp_scope_policy(root)
    scope = str(business_scope or "").strip()
    if not scope:
        raise GovernanceError("roadmap business_automation_scope is missing or invalid")
    if mvp_policy["scope"] != scope:
        raise GovernanceError(
            "scope mismatch: "
            f"{MVP_SCOPE_FILE.as_posix()} mvp_scope={mvp_policy['scope']} "
            f"but docs/governance/DEVELOPMENT_ROADMAP.md business_automation_scope={scope}"
        )
    return mvp_policy
