from __future__ import annotations

import io
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

from governance_repo_checks import run_repo_checks
from governance_lib import (
    GovernanceError,
    configure_utf8_stdio,
    find_repo_root,
    is_idle_current_payload,
    load_current_task,
    load_task_registry,
    load_worktree_registry,
    read_roadmap,
    read_text,
    task_map,
)
from validate_contracts import (
    CONTRACT_BUNDLES,
    validate_authority_snippets,
    validate_contract_bundle,
    validate_registry_files,
)


AUTHORITY_SPEC = "docs/product/AUTHORITY_SPEC.md"
OPERATOR_MANUAL = "docs/governance/OPERATOR_MANUAL.md"
CURRENT_TASK_FILE = "docs/governance/CURRENT_TASK.yaml"

REQUIRED_PRODUCT_FILES = [
    "docs/product/AUTHORITY_SPEC.md",
    "docs/product/MVP_SCOPE.md",
    "docs/product/PRODUCT_BOUNDARIES.md",
    "docs/product/GLOSSARY.md",
]
REQUIRED_GOVERNANCE_FILES = [
    "docs/governance/README.md",
    "docs/governance/DEVELOPMENT_ROADMAP.md",
    "docs/governance/DIRECTORY_MAP.md",
    "docs/governance/AUTOMATION_INTENTS.yaml",
    "docs/governance/PROMPT_MODULE_CATALOG.yaml",
    "docs/governance/prompt_modules/README.md",
    "docs/governance/MODULE_MAP.yaml",
    "docs/governance/TEST_MATRIX.yaml",
    "docs/governance/TASK_POLICY.yaml",
    "docs/governance/CAPABILITY_MAP.yaml",
    "docs/governance/SCHEMA_REGISTRY.md",
    "docs/governance/INTERFACE_CATALOG.yaml",
    "docs/governance/OPERATOR_MANUAL.md",
]
REQUIRED_AUTOMATION_SCRIPTS = [
    "scripts/automation_intent.py",
    "scripts/check_repo.py",
    "scripts/check_hygiene.py",
    "scripts/task_ops.py",
    "scripts/task_continuation_ops.py",
    "scripts/automation_runner.py",
    "scripts/validate_contracts.py",
    "scripts/check_authority_alignment.py",
]
REQUIRED_AUTOMATION_TESTS = [
    "tests/governance/test_automation_intent.py",
    "tests/governance/test_check_repo.py",
    "tests/governance/test_task_continuation.py",
    "tests/governance/test_task_ops.py",
    "tests/governance/test_authority_alignment.py",
    "tests/automation/test_automation_runner.py",
]
REQUIRED_QUALITY_TESTS = [
    "tests/contracts/test_project_fact_contract.py",
    "tests/contracts/test_report_record_contract.py",
    "tests/contracts/test_stage4_formal_objects.py",
    "tests/contracts/test_handoff_catalog.py",
    "tests/contracts/test_stage_chain_contracts.py",
    "tests/integration/test_stage3_stage4_stage6_minimal_flow.py",
    "tests/integration/test_handoff_catalog_consumption.py",
    "tests/integration/test_stage_chain_case_matrix.py",
    "tests/stage3/test_stage3_project_base_contract.py",
    "tests/stage4/test_stage4_rule_hit_contract.py",
    "tests/stage4/test_stage4_formal_case_matrix.py",
    "tests/stage6/test_stage6_project_fact_contract.py",
    "tests/stage6/test_stage6_case_matrix.py",
]
FIXTURE_DIRS = [
    "tests/fixtures/raw",
    "tests/fixtures/normalized",
    "tests/fixtures/rules",
    "tests/fixtures/reports",
    "tests/fixtures/facts",
    "tests/fixtures/golden",
]
KEY_FORMAL_OBJECTS = ("project_base", "rule_hit", "evidence", "review_request", "report_record", "project_fact")


@dataclass
class _CategoryResult:
    name: str
    errors: list[str]

    @property
    def score(self) -> int:
        return 100 if not self.errors else 80

    @property
    def ok(self) -> bool:
        return self.score >= 95


def _run_quietly(callback: Callable, *args):
    sink = io.StringIO()
    with redirect_stdout(sink):
        return callback(*args)


def _append_missing(paths: list[str], root: Path, errors: list[str]) -> None:
    for relative in paths:
        if not (root / relative).exists():
            errors.append(f"missing required file: {relative}")


def _load_text(root: Path, relative: str, errors: list[str]) -> str:
    path = root / relative
    if not path.exists():
        errors.append(f"missing required file: {relative}")
        return ""
    return read_text(path)


def _load_yaml_file(root: Path, relative: str, errors: list[str]) -> dict:
    path = root / relative
    if not path.exists():
        errors.append(f"missing required file: {relative}")
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except yaml.YAMLError as error:
        errors.append(f"invalid yaml: {relative}: {error}")
        return {}


def _require_snippets(text: str, snippets: list[str], label: str, errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{label} missing snippet: {snippet}")


def _reject_legacy_words(text: str, label: str, errors: list[str]) -> None:
    lowered = text.lower()
    for word in ("seed", "skeleton"):
        if word in lowered:
            errors.append(f"{label} still contains legacy wording: {word}")


def _dir_has_payload(path: Path) -> bool:
    return any(item.is_file() and item.name != ".gitkeep" for item in path.rglob("*"))


def _file_has_tests(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "def test_" in text or "class Test" in text


def _collect_contract_state() -> tuple[list[str], list[str], dict[str, str], dict[str, list[str]]]:
    registry_errors = _run_quietly(validate_registry_files)
    authority_enum_errors = _run_quietly(validate_authority_snippets)
    statuses: dict[str, str] = {}
    bundle_errors: dict[str, list[str]] = {}
    for bundle in CONTRACT_BUNDLES:
        errors = _run_quietly(validate_contract_bundle, bundle)
        if not errors:
            statuses[bundle["name"]] = "对齐"
            continue
        statuses[bundle["name"]] = "缺失" if any("missing" in error for error in errors) else "明显不一致"
        bundle_errors[bundle["name"]] = errors
    return registry_errors, authority_enum_errors, statuses, bundle_errors


def _collect_live_task_alignment_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        registry = load_task_registry(root)
        tasks_by_id = task_map(registry)
        worktrees = load_worktree_registry(root)
        run_repo_checks(root, registry, tasks_by_id, worktrees)
        idle_current = is_idle_current_payload(load_current_task(root))
        active_coordination = [
            entry
            for entry in worktrees.get("entries", [])
            if entry.get("work_mode") == "coordination" and entry.get("status") == "active"
        ]
        expected_active = 0 if idle_current else 1
        if len(active_coordination) != expected_active:
            errors.append(
                f"coordination worktree count drift: expected {expected_active} active entry, got {len(active_coordination)}"
            )
    except GovernanceError as error:
        errors.append(str(error))
    return errors


def _append_authority_doc_checks(
    authority_spec: str,
    mvp_scope: str,
    product_boundaries: str,
    glossary: str,
    errors: list[str],
) -> None:
    _require_snippets(
        authority_spec,
        [
            "Derived from:",
            "Stage 6 is the only formal unified fact surface.",
            "`project_fact` is the only formal stage-6 unified fact object.",
        ],
        "docs/product/AUTHORITY_SPEC.md",
        errors,
    )
    _require_snippets(
        mvp_scope,
        [
            "Formal China MVP Scope",
            "Stage 6 unified `project_fact`",
            "`stage3 -> stage4 -> stage6` has a real integration regression path.",
        ],
        "docs/product/MVP_SCOPE.md",
        errors,
    )
    _require_snippets(
        product_boundaries,
        [
            "Do not create a second fact surface outside stage 6.",
            "Do not present automatic findings as legal or regulatory conclusions.",
            "Formal contracts live only in `docs/contracts/`.",
        ],
        "docs/product/PRODUCT_BOUNDARIES.md",
        errors,
    )
    _require_snippets(
        glossary,
        [
            "`project_base`",
            "`rule_hit`",
            "`project_fact`",
            "`current task`",
        ],
        "docs/product/GLOSSARY.md",
        errors,
    )


def _evaluate_authority(
    root: Path,
    authority_enum_errors: list[str],
    bundle_statuses: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    _append_missing(REQUIRED_PRODUCT_FILES, root, errors)
    authority_spec = _load_text(root, "docs/product/AUTHORITY_SPEC.md", errors)
    mvp_scope = _load_text(root, "docs/product/MVP_SCOPE.md", errors)
    product_boundaries = _load_text(root, "docs/product/PRODUCT_BOUNDARIES.md", errors)
    glossary = _load_text(root, "docs/product/GLOSSARY.md", errors)
    _append_authority_doc_checks(authority_spec, mvp_scope, product_boundaries, glossary, errors)
    errors.extend(authority_enum_errors)
    for object_name in KEY_FORMAL_OBJECTS:
        if bundle_statuses.get(object_name) != "对齐":
            errors.append(f"formal object not aligned: {object_name}={bundle_statuses.get(object_name, '缺失')}")
    return errors


def _append_consistency_doc_checks(readme: str, governance_readme: str, errors: list[str]) -> None:
    _require_snippets(
        readme,
        [
            "Conflict rule:",
            "docs/product/AUTHORITY_SPEC.md",
            "docs/governance/CURRENT_TASK.yaml",
            "Stage 6 remains the only formal unified fact surface.",
        ],
        "README.md",
        errors,
    )
    _require_snippets(
        governance_readme,
        [
            "CURRENT_TASK.yaml` remains the only live execution entry.",
            "docs/product/AUTHORITY_SPEC.md",
            "docs/governance/OPERATOR_MANUAL.md",
            "docs/governance/AUTOMATION_INTENTS.yaml",
            "docs/governance/PROMPT_MODULE_CATALOG.yaml",
        ],
        "docs/governance/README.md",
        errors,
    )
    _reject_legacy_words(readme, "README.md", errors)
    _reject_legacy_words(governance_readme, "docs/governance/README.md", errors)


def _append_current_task_consistency(
    current_task: dict[str, object],
    roadmap_frontmatter: dict[str, object],
    roadmap_body: str,
    errors: list[str],
) -> None:
    if is_idle_current_payload(current_task):
        if roadmap_frontmatter.get("current_task_id") is not None:
            errors.append("roadmap current_task_id conflicts with idle CURRENT_TASK.yaml")
        if roadmap_frontmatter.get("current_phase") != "idle":
            errors.append("roadmap current_phase conflicts with idle CURRENT_TASK.yaml")
        if "no live current task" not in roadmap_body.lower():
            errors.append("roadmap body does not describe the idle current-task state")
    else:
        if roadmap_frontmatter.get("current_task_id") != current_task.get("current_task_id"):
            errors.append("roadmap current_task_id conflicts with CURRENT_TASK.yaml")
        if roadmap_frontmatter.get("current_phase") != current_task.get("stage"):
            errors.append("roadmap current_phase conflicts with CURRENT_TASK.yaml")
        if current_task.get("current_task_id") not in roadmap_body:
            errors.append("roadmap body does not mention the live current task")


def _append_authority_source_consistency(
    capability_map: dict[str, object],
    task_policy: dict[str, object],
    interface_catalog: dict[str, object],
    errors: list[str],
) -> None:
    if capability_map.get("authority_source") != AUTHORITY_SPEC:
        errors.append("CAPABILITY_MAP authority_source drift")
    if task_policy.get("authority_source") != AUTHORITY_SPEC:
        errors.append("TASK_POLICY authority_source drift")
    if interface_catalog.get("authority_source") != AUTHORITY_SPEC:
        errors.append("INTERFACE_CATALOG authority_source drift")


def _evaluate_consistency(root: Path, live_task_errors: list[str]) -> list[str]:
    errors = list(live_task_errors)
    readme = _load_text(root, "README.md", errors)
    governance_readme = _load_text(root, "docs/governance/README.md", errors)
    roadmap_frontmatter, roadmap_body = read_roadmap(root)
    current_task = load_current_task(root)
    capability_map = _load_yaml_file(root, "docs/governance/CAPABILITY_MAP.yaml", errors)
    task_policy = _load_yaml_file(root, "docs/governance/TASK_POLICY.yaml", errors)
    interface_catalog = _load_yaml_file(root, "docs/governance/INTERFACE_CATALOG.yaml", errors)

    _append_consistency_doc_checks(readme, governance_readme, errors)
    _append_current_task_consistency(current_task, roadmap_frontmatter, roadmap_body, errors)
    _append_authority_source_consistency(capability_map, task_policy, interface_catalog, errors)
    return errors


def _evaluate_completeness(
    root: Path,
    registry_errors: list[str],
    bundle_errors: dict[str, list[str]],
) -> list[str]:
    errors: list[str] = list(registry_errors)
    _append_missing(REQUIRED_PRODUCT_FILES + REQUIRED_GOVERNANCE_FILES, root, errors)
    for relative in FIXTURE_DIRS:
        path = root / relative
        if not path.exists():
            errors.append(f"missing fixture directory: {relative}")
            continue
        if not _dir_has_payload(path):
            errors.append(f"fixture directory is empty: {relative}")

    integration_path = root / "tests/integration/test_stage3_stage4_stage6_minimal_flow.py"
    if not _file_has_tests(integration_path):
        errors.append("tests/integration missing real test functions for the stage3->stage4->stage6 chain")

    for relative in (
        "tests/stage3/test_stage3_project_base_contract.py",
        "tests/stage4/test_stage4_rule_hit_contract.py",
        "tests/stage6/test_stage6_project_fact_contract.py",
    ):
        if not _file_has_tests(root / relative):
            errors.append(f"missing stage contract test file: {relative}")

    for object_name, object_errors in bundle_errors.items():
        errors.extend(f"{object_name}: {error}" for error in object_errors)
    return errors


def _evaluate_professionalization(root: Path) -> list[str]:
    errors: list[str] = []
    schema_registry = _load_text(root, "docs/governance/SCHEMA_REGISTRY.md", errors)
    readme = _load_text(root, "README.md", errors)
    governance_readme = _load_text(root, "docs/governance/README.md", errors)
    capability_map = _load_yaml_file(root, "docs/governance/CAPABILITY_MAP.yaml", errors)
    task_policy = _load_yaml_file(root, "docs/governance/TASK_POLICY.yaml", errors)
    interface_catalog = _load_yaml_file(root, "docs/governance/INTERFACE_CATALOG.yaml", errors)

    _reject_legacy_words(schema_registry, "docs/governance/SCHEMA_REGISTRY.md", errors)
    _reject_legacy_words(readme, "README.md", errors)
    _reject_legacy_words(governance_readme, "docs/governance/README.md", errors)
    _require_snippets(
        schema_registry,
        [
            "docs/contracts/schemas/stage6_project_fact.schema.json",
            "docs/contracts/examples/project_fact.example.json",
            "docs/contracts/field_semantics/project_fact.fields.yaml",
        ],
        "docs/governance/SCHEMA_REGISTRY.md",
        errors,
    )
    if interface_catalog.get("status") != "no_business_api_registered":
        errors.append("INTERFACE_CATALOG must stay in explicit zero-state until a business API exists")
    if interface_catalog.get("interfaces") != []:
        errors.append("INTERFACE_CATALOG zero-state must keep interfaces empty")
    if not interface_catalog.get("last_reviewed_at"):
        errors.append("INTERFACE_CATALOG missing last_reviewed_at")
    if not interface_catalog.get("next_update_trigger"):
        errors.append("INTERFACE_CATALOG missing next_update_trigger")

    capabilities = capability_map.get("capabilities") or []
    if not capabilities:
        errors.append("CAPABILITY_MAP must declare live capabilities")
    for item in capabilities:
        if item.get("status") == "implemented":
            if not item.get("scripts"):
                errors.append(f"implemented capability missing scripts: {item.get('capability_id')}")
            if not item.get("tests"):
                errors.append(f"implemented capability missing tests: {item.get('capability_id')}")

    if not task_policy.get("stop_conditions"):
        errors.append("TASK_POLICY missing stop_conditions")
    if not task_policy.get("closeout_rules"):
        errors.append("TASK_POLICY missing closeout_rules")
    return errors


def _evaluate_single_source(root: Path, live_task_errors: list[str], registry_errors: list[str]) -> list[str]:
    errors = list(live_task_errors)
    errors.extend(registry_errors)
    current_task = load_current_task(root)
    if current_task.get("status") == "done":
        errors.append("CURRENT_TASK.yaml cannot point at a done task")
    product_boundaries = _load_text(root, "docs/product/PRODUCT_BOUNDARIES.md", errors)
    _require_snippets(
        product_boundaries,
        ["Formal contracts live only in `docs/contracts/`."],
        "docs/product/PRODUCT_BOUNDARIES.md",
        errors,
    )
    return errors


def _evaluate_product_layer(root: Path) -> list[str]:
    errors: list[str] = []
    readme = _load_text(root, "README.md", errors)
    authority_spec = _load_text(root, "docs/product/AUTHORITY_SPEC.md", errors)
    mvp_scope = _load_text(root, "docs/product/MVP_SCOPE.md", errors)
    product_boundaries = _load_text(root, "docs/product/PRODUCT_BOUNDARIES.md", errors)
    glossary = _load_text(root, "docs/product/GLOSSARY.md", errors)

    _require_snippets(
        readme,
        [
            "China MVP formal scope is stage 2 through stage 6.",
            "Stage 6 remains the only formal unified fact surface.",
            "No new business-stage implementation logic under the current governance hardening task.",
        ],
        "README.md",
        errors,
    )
    _reject_legacy_words(readme, "README.md", errors)
    _reject_legacy_words(authority_spec, "docs/product/AUTHORITY_SPEC.md", errors)
    _reject_legacy_words(mvp_scope, "docs/product/MVP_SCOPE.md", errors)
    _reject_legacy_words(product_boundaries, "docs/product/PRODUCT_BOUNDARIES.md", errors)
    _reject_legacy_words(glossary, "docs/product/GLOSSARY.md", errors)
    return errors


def _evaluate_structure_layer(root: Path) -> list[str]:
    errors: list[str] = []
    directory_map = _load_text(root, "docs/governance/DIRECTORY_MAP.md", errors)
    module_map = _load_yaml_file(root, "docs/governance/MODULE_MAP.yaml", errors)
    capability_map = _load_yaml_file(root, "docs/governance/CAPABILITY_MAP.yaml", errors)
    test_matrix = _load_yaml_file(root, "docs/governance/TEST_MATRIX.yaml", errors)

    _require_snippets(
        directory_map,
        [
            "`src/stage6_facts/`",
            "`tests/integration/`",
            "`docs/contracts/`",
        ],
        "docs/governance/DIRECTORY_MAP.md",
        errors,
    )
    module_ids = {item.get("module_id") for item in module_map.get("modules", [])}
    for module_id in ("stage3_parsing", "stage4_validation", "stage6_facts", "governance_control_plane"):
        if module_id not in module_ids:
            errors.append(f"MODULE_MAP missing module: {module_id}")
    governance_module = next(
        (item for item in module_map.get("modules", []) if item.get("module_id") == "governance_control_plane"),
        None,
    )
    if governance_module is not None:
        required_tests = governance_module.get("required_tests") or []
        for command in ("python scripts/check_repo.py", "python scripts/check_hygiene.py src docs tests"):
            if command not in required_tests:
                errors.append(f"governance_control_plane module missing required test: {command}")
        for command in ("pytest tests/governance -q", "pytest tests/automation -q"):
            if command in required_tests:
                errors.append(f"governance_control_plane module still lists full-suite gate: {command}")

    capability_ids = {item.get("capability_id") for item in capability_map.get("capabilities", [])}
    for capability_id in (
        "governance_control_plane",
        "roadmap_autopilot_continuation",
        "contracts_registry_validation",
        "stage3_stage4_stage6_minimal_chain",
        "formal_handoff_catalog",
        "stage4_stage5_stage6_extended_chain",
    ):
        if capability_id not in capability_ids:
            errors.append(f"CAPABILITY_MAP missing capability: {capability_id}")

    chains = test_matrix.get("authority_critical_chains", {})
    if "stage3_stage4_stage6_minimal" not in chains:
        errors.append("TEST_MATRIX missing authority-critical chain: stage3_stage4_stage6_minimal")
    if "stage4_stage5_stage6_case_matrix" not in chains:
        errors.append("TEST_MATRIX missing authority-critical chain: stage4_stage5_stage6_case_matrix")
    return errors


def _evaluate_development_control_layer(root: Path, live_task_errors: list[str]) -> list[str]:
    errors = list(live_task_errors)
    operator_manual = _load_text(root, OPERATOR_MANUAL, errors)
    task_policy = _load_yaml_file(root, "docs/governance/TASK_POLICY.yaml", errors)
    current_task = _load_yaml_file(root, CURRENT_TASK_FILE, errors)

    _require_snippets(
        operator_manual,
        [
            "Use `python scripts/task_ops.py can-close` before closing.",
            "Do not leave the live current task in `done`",
            "Do not modify files outside the current task's `allowed_dirs`.",
            "python scripts/automation_intent.py preflight",
            "prompt source of truth",
        ],
        OPERATOR_MANUAL,
        errors,
    )
    stop_conditions = task_policy.get("stop_conditions") or []
    for required in (
        "current_task drift across registry, roadmap, task file, runlog, or worktree entry",
        "contract validation failure",
        "integration chain failure on authority-critical paths",
    ):
        if required not in stop_conditions:
            errors.append(f"TASK_POLICY missing stop condition: {required}")
    required_tests = current_task.get("required_tests") or []
    if is_idle_current_payload(current_task):
        if required_tests:
            errors.append("idle CURRENT_TASK required_tests must stay empty")
    elif not required_tests:
        errors.append("live CURRENT_TASK required_tests must not be empty")
    return errors


def _evaluate_quality_layer(
    root: Path,
    registry_errors: list[str],
    bundle_errors: dict[str, list[str]],
) -> list[str]:
    errors: list[str] = list(registry_errors)
    for object_name, object_errors in bundle_errors.items():
        errors.extend(f"{object_name}: {error}" for error in object_errors)
    _append_missing(REQUIRED_QUALITY_TESTS, root, errors)
    for relative in FIXTURE_DIRS:
        if not _dir_has_payload(root / relative):
            errors.append(f"quality fixture directory is empty or missing: {relative}")
    if not _file_has_tests(root / "tests/integration/test_stage3_stage4_stage6_minimal_flow.py"):
        errors.append("integration chain test is missing test functions")
    return errors


def _evaluate_automation_layer(root: Path) -> list[str]:
    errors: list[str] = []
    _append_missing(REQUIRED_AUTOMATION_SCRIPTS + REQUIRED_AUTOMATION_TESTS, root, errors)
    capability_map = _load_yaml_file(root, "docs/governance/CAPABILITY_MAP.yaml", errors)
    governance_capability = next(
        (item for item in capability_map.get("capabilities", []) if item.get("capability_id") == "governance_control_plane"),
        None,
    )
    if governance_capability is None:
        errors.append("CAPABILITY_MAP missing governance_control_plane capability")
    else:
        scripts = governance_capability.get("scripts") or []
        tests = governance_capability.get("tests") or []
        if "scripts/automation_intent.py" not in scripts:
            errors.append("governance_control_plane capability must list scripts/automation_intent.py")
        if "scripts/check_authority_alignment.py" not in scripts:
            errors.append("governance_control_plane capability must list scripts/check_authority_alignment.py")
        if "scripts/task_continuation_ops.py" not in scripts:
            errors.append("governance_control_plane capability must list scripts/task_continuation_ops.py")
        for command in (
            "python scripts/check_repo.py",
            "python scripts/check_hygiene.py src docs tests",
            "python scripts/check_authority_alignment.py",
            "pytest tests/governance/test_task_continuation.py -q",
            "pytest tests/automation/test_automation_runner.py -q",
        ):
            if command not in tests:
                errors.append(f"governance_control_plane capability missing test command: {command}")
        for command in ("pytest tests/governance -q", "pytest tests/automation -q"):
            if command in tests:
                errors.append(f"governance_control_plane capability still lists full-suite gate: {command}")
    return errors


def _print_category(result: _CategoryResult) -> None:
    prefix = "[OK]" if result.ok else "[ERROR]"
    print(f"{prefix} {result.name}: {result.score}")
    for error in result.errors:
        print(f"  - {error}")


def main() -> int:
    configure_utf8_stdio()
    root = find_repo_root()
    registry_errors, authority_enum_errors, bundle_statuses, bundle_errors = _collect_contract_state()
    live_task_errors = _collect_live_task_alignment_errors(root)

    core_results = [
        _CategoryResult("权威性", _evaluate_authority(root, authority_enum_errors, bundle_statuses)),
        _CategoryResult("一致性", _evaluate_consistency(root, live_task_errors)),
        _CategoryResult("完整度", _evaluate_completeness(root, registry_errors, bundle_errors)),
        _CategoryResult("专业化", _evaluate_professionalization(root)),
        _CategoryResult("单一真源程度", _evaluate_single_source(root, live_task_errors, registry_errors)),
    ]
    layer_results = [
        _CategoryResult("产品层", _evaluate_product_layer(root)),
        _CategoryResult("结构层", _evaluate_structure_layer(root)),
        _CategoryResult("开发控制层", _evaluate_development_control_layer(root, live_task_errors)),
        _CategoryResult("质量层", _evaluate_quality_layer(root, registry_errors, bundle_errors)),
        _CategoryResult("自动化层", _evaluate_automation_layer(root)),
    ]
    comprehensive_score = round(sum(result.score for result in layer_results) / len(layer_results))

    print("关键对象状态")
    for object_name in KEY_FORMAL_OBJECTS:
        status = bundle_statuses.get(object_name, "缺失")
        print(f"- {object_name}: {status}")
    print("")

    for result in core_results:
        _print_category(result)
    for result in layer_results:
        _print_category(result)
    comprehensive_prefix = "[OK]" if comprehensive_score >= 95 else "[ERROR]"
    print(f"{comprehensive_prefix} 综合评分: {comprehensive_score}")

    failed_categories = [result for result in core_results + layer_results if result.score < 95]
    failed_key_objects = [name for name, status in bundle_statuses.items() if status != "对齐"]
    failed = bool(failed_categories or failed_key_objects or comprehensive_score < 95)
    print("")
    print(f"结论: {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
