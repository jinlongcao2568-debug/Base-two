from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from governance_lib import GovernanceError, configure_utf8_stdio, dump_yaml, find_repo_root, git, iso_now, load_yaml


FULL_CLONE_POOL_FILE = Path("docs/governance/FULL_CLONE_POOL.yaml")


def _load_pool(root: Path) -> dict[str, Any]:
    path = root / FULL_CLONE_POOL_FILE
    if not path.exists():
        raise GovernanceError(f"full clone pool missing: {FULL_CLONE_POOL_FILE}")
    payload = load_yaml(path) or {}
    payload.setdefault("slots", [])
    payload.setdefault("control_plane_root", str(root).replace("\\", "/"))
    return payload


def _write_pool(root: Path, pool: dict[str, Any]) -> None:
    pool["updated_at"] = iso_now()
    pool.setdefault("control_plane_root", str(root).replace("\\", "/"))
    dump_yaml(root / FULL_CLONE_POOL_FILE, pool)


def _provision_slot(root: Path, slot: dict[str, Any], *, refresh: bool) -> None:
    destination = Path(str(slot["path"])).resolve()
    branch = str(slot["branch"])
    idle_branch = str(slot.get("idle_branch") or branch)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        git(root, "clone", "--local", str(root), str(destination))
    if refresh:
        git(destination, "fetch", "--all", check=False)
    checkout = git(destination, "switch", branch, check=False)
    if checkout.returncode != 0:
        create = git(destination, "switch", "-c", branch, f"origin/{branch}", check=False)
        if create.returncode != 0:
            raise GovernanceError(create.stderr.strip() or create.stdout.strip() or f"unable to switch clone slot to {branch}")
    slot["status"] = "ready"
    slot["idle_branch"] = idle_branch
    slot.setdefault("current_task_id", None)
    slot.setdefault("last_claimed_at", None)
    slot.setdefault("last_released_at", None)
    slot["last_provisioned_at"] = iso_now()


def cmd_provision_full_clone_pool(args: argparse.Namespace) -> int:
    root = find_repo_root()
    pool = _load_pool(root)
    provisioned: list[str] = []
    for slot in pool.get("slots", []):
        if args.slot_id and slot.get("slot_id") != args.slot_id:
            continue
        _provision_slot(root, slot, refresh=args.refresh)
        provisioned.append(slot["slot_id"])
    _write_pool(root, pool)
    if not provisioned:
        print("[OK] no full clone slot matched the request")
        return 0
    print(f"[OK] provisioned full clone slots: {', '.join(provisioned)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S full clone worker pool provisioner")
    parser.add_argument("--slot-id")
    parser.add_argument("--refresh", action="store_true")
    parser.set_defaults(func=cmd_provision_full_clone_pool)
    return parser


def main() -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
