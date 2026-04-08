from __future__ import annotations

import argparse
from pathlib import Path

from governance_lib import GovernanceError, configure_utf8_stdio, dump_yaml, find_repo_root
from roadmap_scheduler_eval import evaluate_roadmap_candidates


ROADMAP_CANDIDATES_FILE = Path(".codex/local/roadmap_candidates/index.yaml")


def build_roadmap_candidate_index(root: Path) -> dict[str, object]:
    return evaluate_roadmap_candidates(root)


def cmd_plan_roadmap_candidates(args: argparse.Namespace) -> int:
    root = find_repo_root()
    index = build_roadmap_candidate_index(root)
    output_path = root / Path(args.output)
    dump_yaml(output_path, index)
    print(
        f"[OK] generated {index['candidate_count']} roadmap candidates "
        f"ready={len(index['ready_candidate_ids'])} waiting={len(index['waiting_candidate_ids'])} "
        f"output={Path(args.output).as_posix()}"
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
