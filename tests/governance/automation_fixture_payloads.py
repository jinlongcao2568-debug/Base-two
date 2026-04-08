from __future__ import annotations

from typing import Any


def _continue_current_intent() -> dict[str, Any]:
    return {
        "intent_id": "continue-current",
        "canonical_phrase": "继续当前任务",
        "mapped_command": "python scripts/task_ops.py continue-current",
        "command_argv": ["python", "scripts/task_ops.py", "continue-current"],
        "examples": ["继续当前任务", "恢复当前任务", "继续手头任务"],
        "action_any": ["继续", "接着", "恢复"],
        "context_any": ["当前任务", "手头任务", "本任务", "这个任务"],
        "disallow_any": ["路线图", "总路线图", "候选池", "下一个任务"],
    }


def _worker_self_loop_intent() -> dict[str, Any]:
    return {
        "intent_id": "worker-self-loop",
        "canonical_phrase": "恢复当前窗口任务",
        "mapped_command": "python scripts/worker_self_loop.py once",
        "command_argv": ["python", "scripts/worker_self_loop.py", "once"],
        "examples": ["恢复当前窗口任务", "继续当前窗口任务", "当前窗口持续开发"],
        "action_any": ["恢复", "继续", "持续开发"],
        "context_any": ["当前窗口", "当前窗口任务", "worker", "clone"],
        "disallow_any": ["路线图", "总路线图", "候选池"],
    }


def _continue_roadmap_intent() -> dict[str, Any]:
    return {
        "intent_id": "continue-roadmap",
        "canonical_phrase": "按路线图继续推进",
        "mapped_command": "python scripts/automation_runner.py once --continue-roadmap --prepare-worktrees",
        "command_argv": ["python", "scripts/automation_runner.py", "once", "--continue-roadmap", "--prepare-worktrees"],
        "examples": ["按路线图继续推进", "继续按路线图开发", "按计划推进到下一步"],
        "action_any": ["继续", "接着", "恢复", "推进", "按计划", "按路线图"],
        "context_any": ["路线图", "roadmap", "下一步", "下一个任务", "后续任务", "按计划"],
    }


def _claim_next_intent() -> dict[str, Any]:
    return {
        "intent_id": "claim-next",
        "canonical_phrase": "持续按路线图开发",
        "mapped_command": "python scripts/task_ops.py claim-next --promote-task",
        "command_argv": ["python", "scripts/task_ops.py", "claim-next", "--promote-task"],
        "examples": ["持续按路线图开发", "持续按路线图推进", "按总路线图自动领取下一个任务"],
        "action_any": ["持续", "继续", "自动领取", "领取", "推进", "开发"],
        "context_any": ["路线图", "总路线图", "roadmap", "候选池", "下一个任务", "多窗口"],
        "disallow_any": ["当前任务", "当前窗口"],
    }


def _continue_roadmap_loop_intent() -> dict[str, Any]:
    return {
        "intent_id": "continue-roadmap-loop",
        "canonical_phrase": "持续按路线图循环推进",
        "mapped_command": "python scripts/automation_runner.py loop --continue-roadmap --prepare-worktrees",
        "command_argv": ["python", "scripts/automation_runner.py", "loop", "--continue-roadmap", "--prepare-worktrees"],
        "examples": ["持续按路线图循环推进", "一直按路线图开发", "路线图循环推进"],
        "action_any": ["持续", "一直", "循环", "推进"],
        "context_any": ["路线图", "roadmap", "后续任务", "下一个任务"],
    }


def _publish_intents() -> list[dict[str, Any]]:
    return [
        {
            "intent_id": "commit-task-results",
            "canonical_phrase": "提交当前任务成果",
            "mapped_command": "python scripts/task_ops.py commit-task-results",
            "command_argv": ["python", "scripts/task_ops.py", "commit-task-results"],
            "examples": ["提交当前任务成果"],
        },
        {
            "intent_id": "push-task-branch",
            "canonical_phrase": "推送当前任务分支",
            "mapped_command": "python scripts/task_ops.py push-task-branch",
            "command_argv": ["python", "scripts/task_ops.py", "push-task-branch"],
            "examples": ["推送当前任务分支"],
        },
        {
            "intent_id": "create-task-pr",
            "canonical_phrase": "为当前任务开PR",
            "mapped_command": "python scripts/task_ops.py create-task-pr",
            "command_argv": ["python", "scripts/task_ops.py", "create-task-pr"],
            "examples": ["为当前任务开PR"],
        },
        {
            "intent_id": "publish-task-results",
            "canonical_phrase": "发布当前任务成果",
            "mapped_command": "python scripts/task_ops.py publish-task-results",
            "command_argv": ["python", "scripts/task_ops.py", "publish-task-results"],
            "examples": ["发布当前任务成果"],
        },
    ]


def automation_intents_payload() -> dict[str, Any]:
    intents = [
        _continue_current_intent(),
        _worker_self_loop_intent(),
        _continue_roadmap_intent(),
        _claim_next_intent(),
        _continue_roadmap_loop_intent(),
        *_publish_intents(),
    ]
    return {
        "version": "1.2",
        "recognition_mode": "heuristic_free_form",
        "generic_continue_signals": ["继续", "接着", "恢复", "继续开发", "继续推进"],
        "supported_intents": intents,
    }
