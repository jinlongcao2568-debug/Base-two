from __future__ import annotations

import argparse
from pathlib import Path

from control_plane_root import resolve_control_plane_root
from governance_lib import GovernanceError, configure_utf8_stdio, dump_yaml, find_repo_root
from roadmap_scheduler_eval import evaluate_roadmap_candidates


ROADMAP_CANDIDATES_FILE = Path(".codex/local/roadmap_candidates/index.yaml")


def build_roadmap_candidate_index(root: Path) -> dict[str, object]:
    return evaluate_roadmap_candidates(root)


def cmd_plan_roadmap_candidates(args: argparse.Namespace) -> int:
    local_root = find_repo_root()
    root = resolve_control_plane_root(local_root)
    index = build_roadmap_candidate_index(root)
    requested = Path(args.output)
    output_path = requested.resolve() if requested.is_absolute() else (root / requested).resolve()
    if local_root != root:
        try:
            output_path.relative_to(local_root.resolve())
        except ValueError:
            pass
        else:
            raise GovernanceError("clone 内禁止写本地候选池产物；请写入主控制面输出路径")
    try:
        output_path.relative_to(root.resolve())
    except ValueError as error:
        raise GovernanceError("roadmap candidate index output must stay under the control plane root") from error
    dump_yaml(output_path, index)
    print(
        f"[OK] generated {index['candidate_count']} roadmap candidates "
        f"ready={len(index['ready_candidate_ids'])} waiting={len(index['waiting_candidate_ids'])} "
        f"output={output_path.as_posix()}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S roadmap candidate index generator")
    parser.add_argument("--output", default=str(ROADMAP_CANDIDATES_FILE).replace("\\", "/"))
    parser.set_defaults(func=cmd_plan_roadmap_candidates)
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
