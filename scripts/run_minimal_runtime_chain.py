from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.shared.contracts.minimal_chain_acceptance import evaluate_minimal_chain_acceptance
from src.shared.contracts.minimal_chain_pipeline import run_minimal_runtime_chain, write_runtime_outputs
from src.shared.contracts.runtime_support import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the AX9 minimal runtime chain")
    parser.add_argument("--scenario-id")
    parser.add_argument("--raw-fixture-path")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--requested-at", default="2026-04-05T10:00:00+08:00")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    bundle = run_minimal_runtime_chain(
        scenario_id=args.scenario_id,
        raw_fixture_path=args.raw_fixture_path,
        requested_at=args.requested_at,
    )
    output_paths = write_runtime_outputs(args.output_dir, bundle)
    acceptance = evaluate_minimal_chain_acceptance(output_paths, bundle["scenario_id"])
    write_json(Path(args.output_dir) / "acceptance" / "result.json", acceptance)
    if not acceptance["accepted"]:
        for error in acceptance["errors"]:
            print(f"[ERROR] {error}")
        return 1
    print(f"[OK] minimal-runtime-chain scenario={bundle['scenario_id']} output_dir={Path(args.output_dir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
