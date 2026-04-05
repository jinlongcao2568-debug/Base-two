import argparse
from pathlib import Path

from governance_lib import GovernanceError, find_repo_root, load_yaml, write_text


CATALOG_PATH = Path("docs/governance/PROMPT_MODULE_CATALOG.yaml")


def _render_profile(catalog: dict, profile: dict) -> str:
    modules_by_id = {module["module_id"]: module for module in catalog.get("modules", [])}
    role_profile = next(item for item in catalog.get("role_profiles", []) if item["role_id"] == profile["role_id"])
    policy = catalog.get("custom_instructions_policy", {})
    rendered_modules: list[str] = []
    for module_id in role_profile.get("modules", []):
        module = modules_by_id[module_id]
        module_text = (find_repo_root() / module["path"]).read_text(encoding="utf-8").strip()
        rendered_modules.append(f"## Module: {module_id}\n\n{module_text}")
    allowed = "\n".join(f"- {item}" for item in policy.get("allowed_uses", []))
    forbidden = "\n".join(f"- {item}" for item in policy.get("forbidden_uses", []))
    mission = "\n".join(f"- {item}" for item in profile.get("mission", []))
    notes = "\n".join(f"- {item}" for item in role_profile.get("notes", []))
    return (
        f"# {profile['profile_id']}\n\n"
        "This file is generated from `docs/governance/PROMPT_MODULE_CATALOG.yaml` and `docs/governance/prompt_modules/`.\n\n"
        "## Runtime Mission\n\n"
        f"{mission}\n\n"
        "## Governance Source\n\n"
        "- Prompt source of truth is the governed prompt catalog and prompt modules inside the repository.\n"
        "- App-level custom instructions are not a governance execution source.\n"
        f"- Default custom-instructions state: `{policy.get('default_state', 'empty')}`.\n\n"
        "## Custom Instructions Policy\n\n"
        "Allowed uses:\n"
        f"{allowed}\n\n"
        "Forbidden uses:\n"
        f"{forbidden}\n\n"
        "## Role Notes\n\n"
        f"{notes}\n\n"
        + "\n\n".join(rendered_modules)
        + "\n"
    )


def render_runtime_prompts(root: Path, *, check: bool) -> int:
    catalog = load_yaml(root / CATALOG_PATH)
    failures: list[str] = []
    for profile in catalog.get("runtime_profiles", []):
        content = _render_profile(catalog, profile)
        output_path = root / profile["output_path"]
        if check:
            if not output_path.exists():
                failures.append(f"missing runtime prompt: {profile['output_path']}")
                continue
            existing = output_path.read_text(encoding="utf-8")
            if existing != content:
                failures.append(f"runtime prompt drift: {profile['output_path']}")
            continue
        write_text(output_path, content)
        print(f"[OK] rendered {profile['output_path']}")
    if failures:
        for failure in failures:
            print(f"[ERROR] {failure}")
        return 1
    if check:
        print("[OK] runtime prompts are in sync")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Render governed runtime prompt profiles")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = find_repo_root()
    try:
        return render_runtime_prompts(root, check=args.check)
    except (GovernanceError, StopIteration, KeyError) as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
