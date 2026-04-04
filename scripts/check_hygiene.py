from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re

from governance_lib import GovernanceError, EXECUTION_CONTEXT_FILE, find_repo_root, load_current_task


SRC_WARN = 300
SRC_BLOCK = 500
TEST_WARN = 500
TEST_BLOCK = 700
FUNC_WARN = 50
FUNC_BLOCK = 80


def iter_python_files(root: Path, declared_paths: list[str]) -> list[Path]:
    seen: set[Path] = set()
    results: list[Path] = []
    for value in declared_paths:
        candidate = (root / value).resolve()
        if candidate.is_file() and candidate.suffix == ".py":
            if candidate not in seen:
                seen.add(candidate)
                results.append(candidate)
            continue
        if candidate.is_dir():
            for path in candidate.rglob("*.py"):
                if path not in seen:
                    seen.add(path)
                    results.append(path)
    return sorted(results)


def logical_lines(source_lines: list[str], start: int, end: int) -> int:
    count = 0
    triple_only = {'"""', "'''", 'r"""', "r'''", 'u"""', "u'''", 'f"""', "f'''"}
    for line in source_lines[start - 1 : end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped in triple_only:
            continue
        count += 1
    return count


def detect_cross_stage_mix(path: Path, source: str) -> list[str]:
    normalized = str(path).replace("\\", "/")
    match = re.search(r"/src/(stage(\d+)_[^/]+)/", normalized)
    if not match:
        return []
    own_stage_num = match.group(2)
    hits: set[str] = set()
    patterns = [
        re.compile(r"from\s+src\.stage(\d+)_"),
        re.compile(r"import\s+src\.stage(\d+)_"),
        re.compile(r"from\s+stage(\d+)_"),
        re.compile(r"import\s+stage(\d+)_"),
    ]
    for pattern in patterns:
        for other_stage in pattern.findall(source):
            if other_stage != own_stage_num:
                hits.add(other_stage)
    return sorted(hits)


def classify_thresholds(path: Path) -> tuple[int | None, int | None]:
    normalized = str(path).replace("\\", "/")
    if "/src/" in normalized:
        return SRC_WARN, SRC_BLOCK
    if "/tests/" in normalized:
        return TEST_WARN, TEST_BLOCK
    return None, None


def resolve_declared_paths(root: Path, cli_paths: list[str]) -> list[str]:
    if cli_paths:
        return list(cli_paths)
    execution_context = root / EXECUTION_CONTEXT_FILE
    if execution_context.exists():
        import yaml

        context = yaml.safe_load(execution_context.read_text(encoding="utf-8"))
        return context.get("planned_write_paths", [])
    current_task = load_current_task(root)
    return current_task.get("planned_write_paths", [])


def analyze_python_file(path: Path) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    warn_limit, block_limit = classify_thresholds(path)
    if warn_limit is not None and len(lines) > warn_limit:
        warnings.append(f"{path}: file length {len(lines)} exceeds warning threshold {warn_limit}")
    if block_limit is not None and len(lines) > block_limit:
        errors.append(f"{path}: file length {len(lines)} exceeds block threshold {block_limit}")
    stage_hits = detect_cross_stage_mix(path, source)
    if stage_hits:
        errors.append(f"{path}: cross-stage imports detected -> {', '.join(stage_hits)}")
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        errors.append(f"{path}: syntax error during hygiene parse: {error}")
        return warnings, errors

    public_symbols = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                public_symbols += 1
            count = logical_lines(lines, node.lineno, node.end_lineno or node.lineno)
            if count > FUNC_WARN:
                warnings.append(f"{path}:{node.lineno} function {node.name} has {count} logical lines")
            if count > FUNC_BLOCK:
                errors.append(f"{path}:{node.lineno} function {node.name} exceeds block threshold {FUNC_BLOCK}")
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            public_symbols += 1
    if public_symbols > 6 and len(lines) > (warn_limit or SRC_WARN):
        warnings.append(f"{path}: likely multiple responsibilities ({public_symbols} public symbols)")
    return warnings, errors


def report_results(warnings: list[str], errors: list[str]) -> int:
    for item in warnings:
        print(f"[WARN] {item}")
    for item in errors:
        print(f"[ERROR] {item}")
    if errors:
        return 1
    print("[OK] hygiene checks passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AX9S code hygiene checks")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    try:
        root = find_repo_root()
        declared_paths = resolve_declared_paths(root, args.paths)
        files = iter_python_files(root, declared_paths)
        warnings: list[str] = []
        errors: list[str] = []
        for path in files:
            file_warnings, file_errors = analyze_python_file(path)
            warnings.extend(file_warnings)
            errors.extend(file_errors)
        return report_results(warnings, errors)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
