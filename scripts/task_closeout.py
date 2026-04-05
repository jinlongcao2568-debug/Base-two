from __future__ import annotations

from pathlib import Path
from typing import Any

from governance_lib import (
    current_branch,
    git_status_paths,
    is_idle_current_payload,
    load_current_task,
    load_task_registry,
    load_worktree_registry,
    missing_required_tests,
    worktree_map,
)
from task_rendering import find_task


CURRENT_PAYLOAD_SYNC_FIELDS = (
    "title",
    "status",
    "task_kind",
    "execution_mode",
    "parent_task_id",
    "stage",
    "branch",
    "size_class",
    "automation_mode",
    "worker_state",
    "blocked_reason",
    "topology",
    "allowed_dirs",
    "reserved_paths",
    "planned_write_paths",
    "planned_test_paths",
    "required_tests",
    "task_file",
    "runlog_file",
)


def _append_unique(items: list[str], value: str | None) -> None:
    if value and value not in items:
        items.append(value)


def _append_many(items: list[str], values: list[str]) -> None:
    for value in values:
        _append_unique(items, value)


def _payload_diagnostics(current_payload: dict[str, Any], current_task: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    if current_payload.get("current_task_id") != current_task["task_id"]:
        diagnostics.append(
            "CURRENT_TASK.yaml current_task_id 与 TASK_REGISTRY live 任务不一致："
            f"{current_payload.get('current_task_id')} != {current_task['task_id']}"
        )
    for field in CURRENT_PAYLOAD_SYNC_FIELDS:
        if current_payload.get(field) != current_task.get(field):
            diagnostics.append(
                f"CURRENT_TASK.yaml 字段 `{field}` 与 TASK_REGISTRY 不一致："
                f"{current_payload.get(field)!r} != {current_task.get(field)!r}"
            )
    return diagnostics


def _worktree_diagnostics(root: Path, current_task: dict[str, Any], worktrees: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    entry = worktree_map(worktrees).get(current_task["task_id"])
    if entry is None:
        diagnostics.append(f"WORKTREE_REGISTRY 缺少 live 任务 `{current_task['task_id']}` 的记录。")
        return diagnostics
    if entry.get("work_mode") != "coordination":
        diagnostics.append(
            f"WORKTREE_REGISTRY 记录的 work_mode 不正确：{entry.get('work_mode')!r} != 'coordination'"
        )
    if entry.get("parent_task_id") != current_task.get("parent_task_id"):
        diagnostics.append(
            "WORKTREE_REGISTRY 记录的 parent_task_id 与 TASK_REGISTRY 不一致："
            f"{entry.get('parent_task_id')!r} != {current_task.get('parent_task_id')!r}"
        )
    if entry.get("branch") != current_task["branch"]:
        diagnostics.append(
            f"WORKTREE_REGISTRY 记录的 branch 不一致：{entry.get('branch')!r} != {current_task['branch']!r}"
        )
    if entry.get("worker_owner") != "coordinator":
        diagnostics.append(
            f"WORKTREE_REGISTRY 记录的 worker_owner 不正确：{entry.get('worker_owner')!r} != 'coordinator'"
        )
    if current_task["status"] == "review" and entry.get("status") != "active":
        diagnostics.append(
            f"review 任务的主协调 worktree 应为 active，当前为 {entry.get('status')!r}"
        )
    if current_branch(root) != current_task["branch"]:
        diagnostics.append(
            f"当前分支与 live 任务 branch 不一致：{current_branch(root)!r} != {current_task['branch']!r}"
        )
    return diagnostics


def _assessment(
    *,
    status: str,
    task_id: str | None,
    task_status: str,
    eligible: bool,
    summary: str,
    blockers: list[str],
    diagnostics: list[str],
) -> dict[str, Any]:
    return {
        "status": status,
        "task_id": task_id,
        "task_status": task_status,
        "eligible": eligible,
        "summary": summary,
        "blockers": blockers,
        "diagnostics": diagnostics,
    }


def _base_closeout_blockers(root: Path, current_task: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if current_task.get("task_kind") != "coordination" or current_task.get("parent_task_id") is not None:
        _append_unique(blockers, "自动关账只支持 live top-level coordination task。")
    if current_task["status"] == "blocked":
        reason = current_task.get("blocked_reason") or "blocked without recorded reason"
        _append_unique(blockers, f"当前任务已阻塞：{reason}")
    if current_task["status"] == "done":
        _append_unique(blockers, "CURRENT_TASK.yaml 不应指向已 done 的 live 任务。")
    dirty = git_status_paths(root)
    if dirty:
        _append_unique(blockers, f"工作区不干净：{', '.join(dirty)}")
    return blockers


def _non_review_assessment(
    current_task: dict[str, Any], blockers: list[str], diagnostics: list[str]
) -> dict[str, Any]:
    if diagnostics:
        return _assessment(
            status="blocked",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary="live 台账存在漂移，需先修复后再继续。",
            blockers=["live ledger drift detected"],
            diagnostics=diagnostics,
        )
    if blockers:
        return _assessment(
            status="blocked",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary="当前任务不能进入自动关账路径。",
            blockers=blockers,
            diagnostics=[],
        )
    return _assessment(
        status="not_applicable",
        task_id=current_task["task_id"],
        task_status=current_task["status"],
        eligible=False,
        summary=f"当前任务 `{current_task['task_id']}` 状态为 `{current_task['status']}`，暂不进入自动关账判定。",
        blockers=[],
        diagnostics=[],
    )


def _review_assessment(
    root: Path, current_task: dict[str, Any], blockers: list[str], diagnostics: list[str]
) -> dict[str, Any]:
    missing = missing_required_tests(root, current_task)
    if missing:
        _append_unique(blockers, f"required tests missing from runlog: {', '.join(missing)}")
    if diagnostics:
        _append_unique(blockers, "live ledger drift detected")
    if blockers:
        return _assessment(
            status="blocked",
            task_id=current_task["task_id"],
            task_status=current_task["status"],
            eligible=False,
            summary=f"当前 review 任务 `{current_task['task_id']}` 还不能自动关账。",
            blockers=blockers,
            diagnostics=diagnostics,
        )
    return _assessment(
        status="ready",
        task_id=current_task["task_id"],
        task_status=current_task["status"],
        eligible=True,
        summary=f"当前 review 任务 `{current_task['task_id']}` 满足自动关账前置条件。",
        blockers=[],
        diagnostics=[],
    )


def assess_live_closeout(
    root: Path,
    *,
    registry: dict[str, Any] | None = None,
    worktrees: dict[str, Any] | None = None,
    current_payload: dict[str, Any] | None = None,
    current_task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or load_task_registry(root)
    worktrees = worktrees or load_worktree_registry(root)
    current_payload = current_payload or load_current_task(root)
    if current_task is None and not is_idle_current_payload(current_payload):
        current_task = find_task(registry.get("tasks", []), current_payload["current_task_id"])

    if is_idle_current_payload(current_payload) or current_task is None:
        return _assessment(
            status="not_applicable",
            task_id=None,
            task_status="idle",
            eligible=False,
            summary="当前没有 live coordination task，不存在自动关账对象。",
            blockers=[],
            diagnostics=[],
        )

    diagnostics = _payload_diagnostics(current_payload, current_task)
    diagnostics.extend(_worktree_diagnostics(root, current_task, worktrees))
    blockers = _base_closeout_blockers(root, current_task)

    if current_task["status"] != "review":
        return _non_review_assessment(current_task, blockers, diagnostics)
    return _review_assessment(root, current_task, blockers, diagnostics)
