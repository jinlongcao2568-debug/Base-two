from __future__ import annotations

import re
from typing import Any

from governance_lib import GovernanceError, iso_now, load_module_map, task_required_tests_for_matrix, validate_task


BUSINESS_AUTOPILOT_CAPABILITY_ID = "stage1_to_stage6_business_automation"
BUSINESS_PARENT_BLUEPRINT_ID = "business_parallel_parent_stage1_to_stage6"
BUSINESS_BOOTSTRAP_BLUEPRINT_ID = "business_stage_bootstrap_execution"
BUSINESS_IMPLEMENTATION_BLUEPRINT_ID = "business_stage_implementation_execution"
BUSINESS_SCOPE_VALUES = {"stage1_to_stage6"}
PARALLEL_STRATEGY_VALUES = {"dependency_aware_disjoint_writes"}
SPEC_SOURCE_POLICY_VALUES = {"baseline_contracts_task_package"}
BUSINESS_GAP_PRIORITY_VALUES = {"bootstrap_required", "implementation_ready", "integration_expansion"}
STAGE_ESTABLISHMENT_VALUES = {
    "not_established",
    "bootstrap_required",
    "implementation_ready",
    "integration_expansion",
    "implemented",
    "deferred_manual",
}
BUSINESS_STAGE_IDS = ("stage1", "stage2", "stage3", "stage4", "stage5", "stage6")
DEFERRED_STAGE_IDS = ("stage7", "stage8", "stage9")
AUTHORITY_INPUTS = [
    "docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md",
    "docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md",
    "docs/product/AUTHORITY_SPEC.md",
]
REVIEW_POLICY = [
    "review_bundle_hard_gate",
    "allowed_dirs_only",
    "reserved_paths_forbidden",
    "authority_chain_tests_when_required",
]
CONTRACT_INPUTS_BY_MODULE = {
    "stage1_orchestration": [
        "docs/contracts/sources_registry.yaml",
        "docs/contracts/region_coverage_registry.yaml",
    ],
    "stage2_ingestion": [
        "docs/contracts/sources_registry.yaml",
        "docs/contracts/region_coverage_registry.yaml",
    ],
    "stage3_parsing": [
        "docs/contracts/handoff_catalog.yaml",
        "docs/contracts/schemas/stage3_project_base.schema.json",
        "docs/contracts/examples/project_base.example.json",
        "docs/contracts/field_semantics/project_base.fields.yaml",
    ],
    "stage4_validation": [
        "docs/contracts/handoff_catalog.yaml",
        "docs/contracts/schemas/stage4_rule_hit.schema.json",
        "docs/contracts/examples/rule_hit.example.json",
        "docs/contracts/field_semantics/rule_hit.fields.yaml",
        "docs/contracts/schemas/stage4_evidence.schema.json",
        "docs/contracts/examples/evidence.example.json",
        "docs/contracts/field_semantics/evidence.fields.yaml",
        "docs/contracts/schemas/stage4_review_request.schema.json",
        "docs/contracts/examples/review_request.example.json",
        "docs/contracts/field_semantics/review_request.fields.yaml",
    ],
    "stage5_reporting": [
        "docs/contracts/handoff_catalog.yaml",
        "docs/contracts/schemas/stage5_report_record.schema.json",
        "docs/contracts/examples/report_record.example.json",
        "docs/contracts/field_semantics/report_record.fields.yaml",
    ],
    "stage6_facts": [
        "docs/contracts/handoff_catalog.yaml",
        "docs/contracts/schemas/stage6_project_fact.schema.json",
        "docs/contracts/examples/project_fact.example.json",
        "docs/contracts/field_semantics/project_fact.fields.yaml",
        "docs/contracts/customer_delivery_field_whitelist.yaml",
        "docs/contracts/customer_delivery_field_blacklist.yaml",
    ],
}


def load_business_policy(frontmatter: dict[str, Any]) -> dict[str, Any]:
    scope = frontmatter.get("business_automation_scope")
    parallel_strategy = frontmatter.get("parallel_strategy")
    max_parallel_workers = frontmatter.get("max_parallel_workers")
    spec_source_policy = frontmatter.get("spec_source_policy")
    gap_priority = frontmatter.get("business_gap_priority")
    stage_establishment = frontmatter.get("stage_establishment")
    if scope not in BUSINESS_SCOPE_VALUES:
        raise GovernanceError("roadmap business_automation_scope is missing or invalid")
    if parallel_strategy not in PARALLEL_STRATEGY_VALUES:
        raise GovernanceError("roadmap parallel_strategy is missing or invalid")
    if max_parallel_workers != 2:
        raise GovernanceError("roadmap max_parallel_workers must stay pinned to 2")
    if spec_source_policy not in SPEC_SOURCE_POLICY_VALUES:
        raise GovernanceError("roadmap spec_source_policy is missing or invalid")
    if not isinstance(gap_priority, list) or not gap_priority:
        raise GovernanceError("roadmap business_gap_priority must be a non-empty list")
    if any(item not in BUSINESS_GAP_PRIORITY_VALUES for item in gap_priority):
        raise GovernanceError("roadmap business_gap_priority contains an unknown value")
    if len(set(gap_priority)) != len(gap_priority):
        raise GovernanceError("roadmap business_gap_priority must not contain duplicates")
    if not isinstance(stage_establishment, dict):
        raise GovernanceError("roadmap stage_establishment must be a mapping")
    for stage_id in (*BUSINESS_STAGE_IDS, *DEFERRED_STAGE_IDS):
        value = stage_establishment.get(stage_id)
        if value not in STAGE_ESTABLISHMENT_VALUES:
            raise GovernanceError(f"roadmap stage_establishment invalid for {stage_id}")
    for stage_id in DEFERRED_STAGE_IDS:
        if stage_establishment.get(stage_id) != "deferred_manual":
            raise GovernanceError(f"roadmap {stage_id} must stay deferred_manual while business automation is limited to stage1-stage6")
    return {
        "scope": scope,
        "parallel_strategy": parallel_strategy,
        "max_parallel_workers": max_parallel_workers,
        "spec_source_policy": spec_source_policy,
        "gap_priority": gap_priority,
        "stage_establishment": stage_establishment,
    }


def _find_blueprint(task_policy: dict[str, Any], blueprint_id: str) -> dict[str, Any]:
    for blueprint in task_policy.get("task_blueprints", []):
        if blueprint.get("blueprint_id") == blueprint_id:
            return blueprint
    raise GovernanceError(f"task blueprint missing: {blueprint_id}")


def _next_auto_task_id(tasks: list[dict[str, Any]]) -> str:
    highest = 0
    for task in tasks:
        match = re.match(r"^TASK-AUTO-(\d{3})$", task.get("task_id", ""))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"TASK-AUTO-{highest + 1:03d}"


def _next_exec_task_id(tasks: list[dict[str, Any]], parent_task_id: str, module_id: str) -> str:
    match = re.match(r"^TASK-AUTO-(\d{3})$", parent_task_id)
    stem = match.group(1) if match else parent_task_id.replace("TASK-", "")
    module_suffix = module_id.replace("_", "-").upper()
    candidate = f"TASK-EXEC-{stem}-{module_suffix}"
    existing_ids = {task.get("task_id") for task in tasks}
    if candidate not in existing_ids:
        return candidate
    index = 2
    while f"{candidate}-{index}" in existing_ids:
        index += 1
    return f"{candidate}-{index}"


def _modules_by_stage(root) -> dict[str, dict[str, Any]]:
    module_map = load_module_map(root)
    stage_modules: dict[str, dict[str, Any]] = {}
    for module in module_map.get("modules", []):
        stage_id = module.get("owner_stage")
        if stage_id in BUSINESS_STAGE_IDS:
            stage_modules[stage_id] = module
    return stage_modules


def _dependency_ready(module: dict[str, Any], modules_by_id: dict[str, dict[str, Any]], stage_establishment: dict[str, str]) -> bool:
    for dependency_id in module.get("depends_on", []):
        dependency = modules_by_id.get(dependency_id)
        if dependency is None:
            continue
        dependency_stage = dependency.get("owner_stage")
        if dependency_stage in BUSINESS_STAGE_IDS and stage_establishment.get(dependency_stage) != "implemented":
            return False
    return True


def _eligible_modules(root, policy: dict[str, Any], gap_kind: str) -> list[dict[str, Any]]:
    stage_modules = _modules_by_stage(root)
    modules_by_id = {module["module_id"]: module for module in stage_modules.values()}
    stage_establishment = policy["stage_establishment"]
    eligible: list[dict[str, Any]] = []
    for stage_id in BUSINESS_STAGE_IDS:
        if stage_establishment.get(stage_id) != gap_kind:
            continue
        module = stage_modules.get(stage_id)
        if module is None:
            continue
        if _dependency_ready(module, modules_by_id, stage_establishment):
            eligible.append(module)
    return eligible[: policy["max_parallel_workers"]]


def _review_bundle_commands(root, task: dict[str, Any]) -> list[str]:
    commands = [
        "python scripts/check_repo.py",
        "python scripts/check_hygiene.py",
    ]
    if task.get("contract_inputs"):
        commands.append("python scripts/validate_contracts.py")
    matrix_commands = task_required_tests_for_matrix(root, task)
    commands.extend(matrix_commands)
    if task.get("module_id") in {"stage3_parsing", "stage4_validation", "stage5_reporting", "stage6_facts"}:
        commands.append("pytest tests/integration -q")
    deduped: list[str] = []
    for command in commands:
        if command not in deduped:
            deduped.append(command)
    return deduped


def _module_scope(module: dict[str, Any]) -> list[str]:
    scope = [f"module_id={module['module_id']}", f"owner_stage={module['owner_stage']}"]
    scope.extend(f"writes={path}" for path in module.get("allowed_dirs", []))
    scope.extend(f"outputs={output}" for output in module.get("outputs", []))
    return scope


def _child_contract_inputs(module_id: str) -> list[str]:
    return list(CONTRACT_INPUTS_BY_MODULE.get(module_id, []))


def _child_allowed_dirs(module: dict[str, Any], contract_inputs: list[str]) -> list[str]:
    return [*module.get("allowed_dirs", []), *contract_inputs]


def _child_planned_write_paths(module: dict[str, Any], contract_inputs: list[str]) -> list[str]:
    return [*module.get("allowed_dirs", []), *contract_inputs]


def _child_planned_test_paths(module: dict[str, Any]) -> list[str]:
    return [path for path in module.get("allowed_dirs", []) if path.startswith("tests/")]


def _child_branch(blueprint: dict[str, Any], task_id: str, module: dict[str, Any]) -> str:
    return blueprint["branch_template"].format(
        task_id=task_id,
        module_slug=module["module_id"].replace("_", "-"),
        stage=module["owner_stage"],
    )


def _child_task_payload(
    task_id: str,
    parent_task: dict[str, Any],
    module: dict[str, Any],
    gap_kind: str,
    blueprint: dict[str, Any],
    policy: dict[str, Any],
    contract_inputs: list[str],
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "title": f"{module['module_id']} {gap_kind} lane",
        "status": "queued",
        "task_kind": blueprint["task_kind"],
        "execution_mode": blueprint["execution_mode"],
        "parent_task_id": parent_task["task_id"],
        "stage": module["owner_stage"],
        "branch": _child_branch(blueprint, task_id, module),
        "size_class": blueprint["size_class"],
        "automation_mode": blueprint["automation_mode"],
        "worker_state": "idle",
        "blocked_reason": None,
        "last_reported_at": iso_now(),
        "topology": blueprint["topology"],
        "allowed_dirs": _child_allowed_dirs(module, contract_inputs),
        "reserved_paths": list(module.get("reserved_paths", [])),
        "planned_write_paths": _child_planned_write_paths(module, contract_inputs),
        "planned_test_paths": _child_planned_test_paths(module),
        "required_tests": [],
        "task_file": f"docs/governance/tasks/{task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
        "generated_from_blueprint": blueprint["blueprint_id"],
        "module_id": module["module_id"],
        "gap_kind": gap_kind,
        "spec_source_policy": policy["spec_source_policy"],
        "authority_inputs": list(AUTHORITY_INPUTS),
        "contract_inputs": contract_inputs,
        "module_scope": _module_scope(module),
        "review_policy": list(REVIEW_POLICY),
    }


def _build_parent_task(tasks: list[dict[str, Any]], blueprint: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    task_id = _next_auto_task_id(tasks)
    task = {
        "task_id": task_id,
        "title": blueprint["title"],
        "status": "queued",
        "task_kind": blueprint["task_kind"],
        "execution_mode": blueprint["execution_mode"],
        "parent_task_id": None,
        "stage": blueprint["stage"],
        "branch": blueprint["branch_template"].format(task_id=task_id),
        "size_class": blueprint["size_class"],
        "automation_mode": blueprint["automation_mode"],
        "worker_state": "idle",
        "blocked_reason": None,
        "last_reported_at": iso_now(),
        "topology": blueprint["topology"],
        "allowed_dirs": list(blueprint["allowed_dirs"]),
        "reserved_paths": list(blueprint.get("reserved_paths", [])),
        "planned_write_paths": list(blueprint["planned_write_paths"]),
        "planned_test_paths": list(blueprint["planned_test_paths"]),
        "required_tests": list(blueprint["required_tests"]),
        "task_file": f"docs/governance/tasks/{task_id}.md",
        "runlog_file": f"docs/governance/runlogs/{task_id}-RUNLOG.md",
        "created_at": iso_now(),
        "activated_at": None,
        "closed_at": None,
        "generated_from_blueprint": blueprint["blueprint_id"],
        "spec_source_policy": policy["spec_source_policy"],
        "authority_inputs": list(AUTHORITY_INPUTS),
        "contract_inputs": ["docs/contracts/handoff_catalog.yaml"],
        "module_scope": ["scope=stage1-stage6-business-round"],
        "review_policy": list(REVIEW_POLICY),
    }
    validate_task(task)
    return task


def _build_child_task(
    root,
    tasks: list[dict[str, Any]],
    parent_task: dict[str, Any],
    module: dict[str, Any],
    gap_kind: str,
    blueprint: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    task_id = _next_exec_task_id(tasks, parent_task["task_id"], module["module_id"])
    contract_inputs = _child_contract_inputs(module["module_id"])
    task = _child_task_payload(task_id, parent_task, module, gap_kind, blueprint, policy, contract_inputs)
    task["required_tests"] = _review_bundle_commands(root, task)
    validate_task(task)
    return task


def build_business_successor_round(root, registry: dict[str, Any], task_policy: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], str] | None:
    frontmatter = {}
    from governance_lib import read_roadmap

    frontmatter, _ = read_roadmap(root)
    policy = load_business_policy(frontmatter)
    parent_blueprint = _find_blueprint(task_policy, BUSINESS_PARENT_BLUEPRINT_ID)
    tasks = registry.setdefault("tasks", [])
    for gap_kind in policy["gap_priority"]:
        eligible = _eligible_modules(root, policy, gap_kind)
        if not eligible:
            continue
        parent_task = _build_parent_task(tasks, parent_blueprint, policy)
        child_blueprint_id = (
            BUSINESS_BOOTSTRAP_BLUEPRINT_ID
            if gap_kind == "bootstrap_required"
            else BUSINESS_IMPLEMENTATION_BLUEPRINT_ID
        )
        child_blueprint = _find_blueprint(task_policy, child_blueprint_id)
        child_tasks = [
            _build_child_task(root, tasks, parent_task, module, gap_kind, child_blueprint, policy)
            for module in eligible
        ]
        parent_task["child_task_ids"] = [task["task_id"] for task in child_tasks]
        return parent_task, child_tasks, gap_kind
    return None


def capability_is_open(capability_map: dict[str, Any], capability_id: str) -> bool:
    capability = next(
        (item for item in capability_map.get("capabilities", []) if item.get("capability_id") == capability_id),
        None,
    )
    if capability is None:
        return True
    return capability.get("status") != "implemented"


def mark_capability_status(capability_map: dict[str, Any], capability_id: str, status: str, scripts: list[str], tests: list[str], source_of_truth: list[str]) -> None:
    capabilities = capability_map.setdefault("capabilities", [])
    for capability in capabilities:
        if capability.get("capability_id") == capability_id:
            capability["status"] = status
            capability["scripts"] = list(scripts)
            capability["tests"] = list(tests)
            capability["source_of_truth"] = list(source_of_truth)
            return
    capabilities.append(
        {
            "capability_id": capability_id,
            "status": status,
            "source_of_truth": list(source_of_truth),
            "scripts": list(scripts),
            "tests": list(tests),
        }
    )
