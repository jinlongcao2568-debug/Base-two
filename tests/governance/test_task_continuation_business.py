from __future__ import annotations

from pathlib import Path

from .helpers import TASK_OPS_SCRIPT, init_governance_repo, read_yaml, run_python_inline as run_python, write_mvp_scope, write_yaml
from .task_continuation_scenarios import create_successor, enable_business_autopilot, mark_current_review_ready, set_business_scope


def test_continue_roadmap_generates_task_auto_002_when_gap_is_open(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo, "TASK-AUTO-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    auto_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-AUTO-001")
    auto_task["status"] = "done"
    auto_task["worker_state"] = "completed"
    auto_task["activated_at"] = "2026-04-04T00:00:00+08:00"
    auto_task["closed_at"] = "2026-04-04T00:00:00+08:00"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    capability_map = read_yaml(repo / "docs/governance/CAPABILITY_MAP.yaml")
    roadmap_text = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    autopilot = next(item for item in capability_map["capabilities"] if item["capability_id"] == "roadmap_autopilot_continuation")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-AUTO-002"
    assert tasks["TASK-AUTO-002"]["status"] == "doing"
    assert tasks["TASK-AUTO-002"]["required_tests"] == [
        "python scripts/check_repo.py",
        "python scripts/check_hygiene.py src docs tests",
        "python scripts/check_authority_alignment.py",
    ]
    assert autopilot["status"] == "in_progress"
    assert "next_recommended_task_id: TASK-AUTO-002" in roadmap_text


def test_continue_roadmap_generates_task_auto_002_from_idle(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo, "TASK-AUTO-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    auto_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-AUTO-001")
    auto_task["status"] = "done"
    auto_task["worker_state"] = "completed"
    auto_task["activated_at"] = "2026-04-04T00:00:00+08:00"
    auto_task["closed_at"] = "2026-04-04T00:00:00+08:00"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    from .helpers import close_live_task_to_idle

    close_live_task_to_idle(repo, commit_after_close=True)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-AUTO-002"
    assert tasks["TASK-AUTO-002"]["status"] == "doing"
    assert tasks["TASK-AUTO-002"]["depends_on_task_ids"] == []


def test_continue_roadmap_blocks_when_stale_dependency_pointer_leaves_no_unique_safe_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    registry["tasks"].append(
        {
            "task_id": "TASK-BLOCKER-001",
            "title": "blocker",
            "status": "queued",
            "task_kind": "coordination",
            "execution_mode": "shared_coordination",
            "parent_task_id": None,
            "stage": "blocked-phase",
            "branch": "feat/TASK-BLOCKER-001",
            "size_class": "standard",
            "automation_mode": "manual",
            "worker_state": "idle",
            "blocked_reason": None,
            "last_reported_at": "2026-04-04T00:00:00+08:00",
            "topology": "single_worker",
            "allowed_dirs": ["docs/governance/"],
            "reserved_paths": [],
            "planned_write_paths": ["docs/governance/"],
            "planned_test_paths": ["tests/governance/"],
            "required_tests": ["python scripts/check_repo.py"],
            "task_file": "docs/governance/tasks/TASK-BLOCKER-001.md",
            "runlog_file": "docs/governance/runlogs/TASK-BLOCKER-001-RUNLOG.md",
            "lane_count": 1,
            "lane_index": None,
            "parallelism_plan_id": None,
            "review_bundle_status": "not_applicable",
            "created_at": "2026-04-04T00:00:00+08:00",
            "activated_at": None,
            "closed_at": None,
        }
    )
    next_task = next(task for task in registry["tasks"] if task["task_id"] == "TASK-NEXT-001")
    next_task["depends_on_task_ids"] = ["TASK-BLOCKER-001"]
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "successor landscape is not unique" in result.stdout


def test_continue_roadmap_rejects_ambiguous_successor_landscape(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    create_successor(repo, "TASK-ALT-001")
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "not unique" in result.stdout


def test_continue_roadmap_ignores_backlog_successor_in_uniqueness_check(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    create_successor(repo, "TASK-ALT-001", successor_state="backlog")
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-ALT-001"]["status"] == "queued"
    assert tasks["TASK-ALT-001"]["successor_state"] == "backlog"


def test_continue_roadmap_skips_absorbed_explicit_successor_and_falls_back_to_live_candidate(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    create_successor(repo)
    create_successor(repo, "TASK-ABSORBED-001")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    absorbed = next(task for task in registry["tasks"] if task["task_id"] == "TASK-ABSORBED-001")
    absorbed["absorbed_by"] = "TASK-GOV-018"
    absorbed["successor_state"] = "backlog"
    write_yaml(repo / "docs/governance/TASK_REGISTRY.yaml", registry)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-ABSORBED-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    updated_roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] == "TASK-NEXT-001"
    assert tasks["TASK-ABSORBED-001"]["status"] == "queued"
    assert tasks["TASK-ABSORBED-001"]["absorbed_by"] == "TASK-GOV-018"
    assert "next_recommended_task_id: TASK-NEXT-001" in updated_roadmap


def test_continue_roadmap_rejects_boundary_unclear_successor(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    created = run_python(
        TASK_OPS_SCRIPT,
        repo,
        "new",
        "TASK-NEXT-001",
        "--title",
        "next coordination task",
        "--stage",
        "next-phase",
        "--branch",
        "feat/TASK-NEXT-001",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("next_recommended_task_id: null", "next_recommended_task_id: TASK-NEXT-001", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    assert result.returncode == 1
    assert "boundary is incomplete" in result.stdout


def test_continue_roadmap_generates_business_parent_and_child(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo)
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    tasks = {task["task_id"]: task for task in registry["tasks"]}
    parent = tasks[current_task["current_task_id"]]
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert parent["topology"] == "parallel_parent"
    assert parent["automation_mode"] == "autonomous"
    assert parent["lane_count"] == 1
    assert parent["parallelism_plan_id"] == f"plan-{parent['task_id']}-1"
    assert len(children) == 1
    assert children[0]["module_id"] == "stage1_orchestration"
    assert children[0]["lane_count"] == 1
    assert children[0]["lane_index"] == 1
    assert children[0]["parallelism_plan_id"] == f"plan-{parent['task_id']}-1"
    assert children[0]["authority_inputs"]
    assert children[0]["contract_inputs"]
    assert children[0]["review_policy"]
    assert "python scripts/check_repo.py" in children[0]["required_tests"]
    assert "python scripts/check_hygiene.py" in children[0]["required_tests"]
    assert "python scripts/validate_contracts.py" in children[0]["required_tests"]


def test_continue_roadmap_respects_bootstrap_priority_before_implementation(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    roadmap = roadmap.replace("  stage1: bootstrap_required", "  stage1: implemented", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"].startswith("TASK-AUTO-"))
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert [child["module_id"] for child in children] == ["stage2_ingestion"]
    assert parent["lane_count"] == 1
    assert children[0]["lane_index"] == 1


def test_continue_roadmap_blocks_stage7_successor_until_downstream_capability_is_implemented(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    for stage_id in ("stage1", "stage2", "stage3", "stage4", "stage5", "stage6"):
        roadmap = roadmap.replace(f"  {stage_id}: bootstrap_required", f"  {stage_id}: implemented")
        roadmap = roadmap.replace(f"  {stage_id}: implementation_ready", f"  {stage_id}: implemented")
    roadmap = roadmap.replace("  stage7: not_established", "  stage7: bootstrap_required", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert current_task["current_task_id"] is None
    assert current_task["status"] == "idle"
    assert "closed TASK-BASE-001 to idle" in result.stdout


def test_continue_roadmap_generates_stage7_successor_when_downstream_capability_is_implemented(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo, include_downstream=True)
    set_business_scope(repo, "stage1_to_stage9")
    write_mvp_scope(
        repo,
        scope="stage1_to_stage9",
        included_stages=["stage1", "stage2", "stage3", "stage4", "stage5", "stage6", "stage7", "stage8", "stage9"],
        excluded_stages=[],
    )
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    for stage_id in ("stage1", "stage2", "stage3", "stage4", "stage5", "stage6"):
        roadmap = roadmap.replace(f"  {stage_id}: bootstrap_required", f"  {stage_id}: implemented")
        roadmap = roadmap.replace(f"  {stage_id}: implementation_ready", f"  {stage_id}: implemented")
    roadmap = roadmap.replace("  stage7: not_established", "  stage7: bootstrap_required", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    current_task = read_yaml(repo / "docs/governance/CURRENT_TASK.yaml")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"] == current_task["current_task_id"])
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]

    assert result.returncode == 0, result.stdout + result.stderr
    assert parent["topology"] == "parallel_parent"
    assert [child["module_id"] for child in children] == ["stage7_sales"]


def test_continue_roadmap_fails_fast_when_mvp_scope_mismatches_business_scope(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo)
    write_mvp_scope(
        repo,
        scope="stage2_to_stage6",
        included_stages=["stage2", "stage3", "stage4", "stage5", "stage6"],
        excluded_stages=["stage1", "stage7", "stage8", "stage9"],
    )
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")

    assert result.returncode == 1
    assert "scope mismatch" in result.stdout


def test_continue_roadmap_caps_business_children_at_four(tmp_path: Path) -> None:
    repo = init_governance_repo(tmp_path)
    enable_business_autopilot(repo)
    roadmap = (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").read_text(encoding="utf-8")
    for stage_id in ("stage3", "stage4", "stage5", "stage6"):
        roadmap = roadmap.replace(f"  {stage_id}: implementation_ready", f"  {stage_id}: bootstrap_required", 1)
    (repo / "docs/governance/DEVELOPMENT_ROADMAP.md").write_text(roadmap, encoding="utf-8")
    module_map = read_yaml(repo / "docs/governance/MODULE_MAP.yaml")
    for module in module_map["modules"]:
        if module["owner_stage"] in {"stage2", "stage3", "stage4", "stage5", "stage6"}:
            module["depends_on"] = []
    write_yaml(repo / "docs/governance/MODULE_MAP.yaml", module_map)
    mark_current_review_ready(repo)

    result = run_python(TASK_OPS_SCRIPT, repo, "continue-roadmap")
    registry = read_yaml(repo / "docs/governance/TASK_REGISTRY.yaml")
    task_policy = read_yaml(repo / "docs/governance/TASK_POLICY.yaml")
    parent = next(task for task in registry["tasks"] if task["task_id"].startswith("TASK-AUTO-"))
    children = [task for task in registry["tasks"] if task.get("parent_task_id") == parent["task_id"]]
    expected_count = min(
        6,
        int(task_policy["size_classes"]["heavy"]["dynamic_lane_ceiling_v1"]),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert len(children) == expected_count
    assert parent["lane_count"] == expected_count
    assert parent["parallelism_plan_id"] == f"plan-{parent['task_id']}-{expected_count}"
    assert [child["lane_index"] for child in children] == list(range(1, expected_count + 1))
    assert all(child["lane_count"] == expected_count for child in children)
    assert all(child["parallelism_plan_id"] == f"plan-{parent['task_id']}-{expected_count}" for child in children)
