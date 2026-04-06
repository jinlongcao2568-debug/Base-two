from __future__ import annotations

from typing import Any


def automation_intents_payload() -> dict[str, Any]:
    return {
        "version": "1.1",
        "recognition_mode": "heuristic_free_form",
        "generic_continue_signals": ["继续", "接着", "恢复", "继续开发", "继续推进"],
        "supported_intents": [
            {
                "intent_id": "continue-current",
                "canonical_phrase": "继续当前任务",
                "mapped_command": "python scripts/task_ops.py continue-current",
                "command_argv": ["python", "scripts/task_ops.py", "continue-current"],
                "examples": ["继续当前任务", "回到现在这个任务继续做"],
                "action_any": ["继续", "接着", "恢复", "继续开发"],
                "context_any": ["当前任务", "手头任务", "现在这个任务"],
                "disallow_any": ["路线图", "roadmap", "下一步"],
            },
            {
                "intent_id": "continue-roadmap",
                "canonical_phrase": "按路线图继续推进",
                "mapped_command": "python scripts/automation_runner.py once --continue-roadmap --prepare-worktrees",
                "command_argv": [
                    "python",
                    "scripts/automation_runner.py",
                    "once",
                    "--continue-roadmap",
                    "--prepare-worktrees",
                ],
                "examples": ["按路线图继续推进", "继续按照路线图开发"],
                "action_any": ["继续", "接着", "恢复", "推进", "按计划", "按路线"],
                "context_any": ["路线图", "roadmap", "下一步", "下一个任务", "后续任务", "按计划", "按路线"],
            },
            {
                "intent_id": "continue-roadmap-loop",
                "canonical_phrase": "持续按路线图开发",
                "mapped_command": "python scripts/automation_runner.py loop --continue-roadmap --prepare-worktrees",
                "command_argv": [
                    "python",
                    "scripts/automation_runner.py",
                    "loop",
                    "--continue-roadmap",
                    "--prepare-worktrees",
                ],
                "examples": ["持续按路线图开发", "持续按路线图推进", "一直按路线图开发"],
                "action_any": ["持续", "一直", "循环", "连续", "推进", "开发"],
                "context_any": ["路线图", "roadmap", "按路线图", "后续任务", "下一个任务"],
            },
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
        ],
    }
