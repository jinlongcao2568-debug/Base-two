from __future__ import annotations

import argparse

from governance_lib import EXECUTION_WORKER_OWNERS, GovernanceError
from task_continuation_ops import cmd_continue_current, cmd_continue_roadmap
from task_lifecycle_ops import (
    cmd_activate,
    cmd_can_close,
    cmd_can_start,
    cmd_close,
    cmd_decide_topology,
    cmd_new,
    cmd_pause,
    cmd_split_check,
    cmd_sync,
)
from task_worker_ops import (
    cmd_auto_close_children,
    cmd_worker_blocked,
    cmd_worker_finish,
    cmd_worker_report,
    cmd_worker_start,
)
from task_worktree_ops import cmd_cleanup_orphans, cmd_worktree_create, cmd_worktree_release


def add_task_lifecycle_commands(subparsers) -> None:
    new_parser = subparsers.add_parser("new")
    new_parser.add_argument("task_id")
    new_parser.add_argument("--title", required=True)
    new_parser.add_argument("--stage", required=True)
    new_parser.add_argument("--branch")
    new_parser.add_argument("--task-kind", default="coordination", choices=["coordination", "execution"])
    new_parser.add_argument("--execution-mode", choices=["shared_coordination", "isolated_worktree"])
    new_parser.add_argument("--parent-task-id")
    new_parser.add_argument("--status", default="queued", choices=["queued", "doing", "blocked", "paused", "review", "done"])
    new_parser.add_argument("--size-class", default="standard", choices=["micro", "standard", "heavy"])
    new_parser.add_argument("--automation-mode", choices=["manual", "assisted", "autonomous"])
    new_parser.add_argument("--worker-state", default="idle", choices=["idle", "running", "blocked", "review_pending", "completed"])
    new_parser.add_argument("--topology", choices=["single_task", "single_worker", "parallel_parent"])
    new_parser.add_argument("--allowed-dirs", nargs="*", default=[])
    new_parser.add_argument("--reserved-paths", nargs="*", default=[])
    new_parser.add_argument("--planned-write-paths", nargs="*", default=[])
    new_parser.add_argument("--planned-test-paths", nargs="*", default=[])
    new_parser.add_argument("--required-tests", nargs="*", default=[])
    new_parser.set_defaults(func=cmd_new)

    activate_parser = subparsers.add_parser("activate")
    activate_parser.add_argument("task_id")
    activate_parser.set_defaults(func=cmd_activate)

    pause_parser = subparsers.add_parser("pause")
    pause_parser.add_argument("task_id", nargs="?")
    pause_parser.set_defaults(func=cmd_pause)

    close_parser = subparsers.add_parser("close")
    close_parser.add_argument("task_id", nargs="?")
    close_parser.set_defaults(func=cmd_close)

    can_start_parser = subparsers.add_parser("can-start")
    can_start_parser.add_argument("task_id", nargs="?")
    can_start_parser.set_defaults(func=cmd_can_start)

    can_close_parser = subparsers.add_parser("can-close")
    can_close_parser.add_argument("task_id", nargs="?")
    can_close_parser.set_defaults(func=cmd_can_close)

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("--write", action="store_true")
    sync_parser.set_defaults(func=cmd_sync)

    split_parser = subparsers.add_parser("split-check")
    split_parser.add_argument("parent_task_id")
    split_parser.set_defaults(func=cmd_split_check)

    topology_parser = subparsers.add_parser("decide-topology")
    topology_parser.add_argument("task_id")
    topology_parser.set_defaults(func=cmd_decide_topology)

    continue_current_parser = subparsers.add_parser("continue-current")
    continue_current_parser.set_defaults(func=cmd_continue_current)

    continue_roadmap_parser = subparsers.add_parser("continue-roadmap")
    continue_roadmap_parser.set_defaults(func=cmd_continue_roadmap)


def add_worktree_commands(subparsers) -> None:
    create_parser = subparsers.add_parser("worktree-create")
    create_parser.add_argument("task_id")
    create_parser.add_argument("--path", required=True)
    create_parser.add_argument("--worker-owner", choices=list(EXECUTION_WORKER_OWNERS))
    create_parser.set_defaults(func=cmd_worktree_create)

    release_parser = subparsers.add_parser("worktree-release")
    release_parser.add_argument("task_id")
    release_parser.set_defaults(func=cmd_worktree_release)

    cleanup_parser = subparsers.add_parser("cleanup-orphans")
    cleanup_parser.add_argument("--task-id")
    cleanup_parser.set_defaults(func=cmd_cleanup_orphans)


def add_worker_commands(subparsers) -> None:
    worker_start_parser = subparsers.add_parser("worker-start")
    worker_start_parser.add_argument("task_id")
    worker_start_parser.add_argument("--worker-owner", choices=["coordinator", *EXECUTION_WORKER_OWNERS])
    worker_start_parser.add_argument("--path")
    worker_start_parser.set_defaults(func=cmd_worker_start)

    worker_report_parser = subparsers.add_parser("worker-report")
    worker_report_parser.add_argument("task_id")
    worker_report_parser.add_argument("--note", action="append", default=[])
    worker_report_parser.add_argument("--tests", nargs="*", default=[])
    worker_report_parser.set_defaults(func=cmd_worker_report)

    worker_blocked_parser = subparsers.add_parser("worker-blocked")
    worker_blocked_parser.add_argument("task_id")
    worker_blocked_parser.add_argument("--reason", required=True)
    worker_blocked_parser.set_defaults(func=cmd_worker_blocked)

    worker_finish_parser = subparsers.add_parser("worker-finish")
    worker_finish_parser.add_argument("task_id")
    worker_finish_parser.add_argument("--summary", required=True)
    worker_finish_parser.add_argument("--tests", nargs="*", default=[])
    worker_finish_parser.add_argument("--candidate-paths", nargs="*", default=[])
    worker_finish_parser.set_defaults(func=cmd_worker_finish)

    auto_close_parser = subparsers.add_parser("auto-close-children")
    auto_close_parser.add_argument("parent_task_id")
    auto_close_parser.set_defaults(func=cmd_auto_close_children)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S governance task operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_task_lifecycle_commands(subparsers)
    add_worktree_commands(subparsers)
    add_worker_commands(subparsers)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1
