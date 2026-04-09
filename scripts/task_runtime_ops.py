from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
from pathlib import Path

from governance_lib import EXECUTION_WORKER_OWNERS, GovernanceError, configure_utf8_stdio
from control_plane_root import resolve_control_plane_root
from task_publish_ops import (
    PUBLISH_ACTIONS,
    cmd_checkpoint_task_results,
    cmd_commit_task_results,
    cmd_create_task_pr,
    cmd_publish_preflight,
    cmd_publish_task_results,
    cmd_push_task_branch,
)
from task_continuation_ops import cmd_continue_current, cmd_continue_roadmap
from task_coordination_ops import cmd_handoff, cmd_release, cmd_takeover
from task_coordination_planner import cmd_plan_coordination, cmd_promote_candidate
from task_lifecycle_ops import (
    cmd_activate,
    cmd_can_close,
    cmd_can_start,
    cmd_close,
    cmd_decide_topology,
    cmd_derive_ledgers,
    cmd_new,
    cmd_pause,
    cmd_queue_and_activate,
    cmd_reconcile_ledgers,
    cmd_split_check,
    cmd_sync,
)
from task_orchestration_ops import cmd_orchestration_status
from roadmap_candidate_index import cmd_plan_roadmap_candidates
from roadmap_candidate_compiler import cmd_compile as cmd_compile_roadmap_candidates
from roadmap_explain import (
    cmd_explain_candidate,
    cmd_explain_claim_decision,
    cmd_explain_pool,
    cmd_explain_release_chain,
)
from roadmap_claim_next import cmd_claim_next
from roadmap_execution_closeout import main as roadmap_closeout_main, close_ready_execution_tasks
from full_clone_pool import (
    cmd_audit_full_clone_pool,
    cmd_provision_full_clone_pool,
    cmd_rebuild_full_clone_pool,
    cmd_refresh_full_clone_pool,
)
from roadmap_candidate_maintainer import cmd_refresh
from worker_self_loop import cmd_once as cmd_worker_self_loop_once, cmd_loop as cmd_worker_self_loop_loop
from review_candidate_pool import cmd_review
from task_worker_ops import (
    cmd_auto_close_children,
    cmd_worker_design_confirm,
    cmd_worker_blocked,
    cmd_worker_finish,
    cmd_worker_heartbeat,
    cmd_worker_plan,
    cmd_worker_quality_review,
    cmd_worker_report,
    cmd_worker_spec_review,
    cmd_worker_start,
    cmd_worker_test_first,
)
from task_worktree_ops import (
    cmd_cleanup_orphans,
    cmd_prepare_child_execution,
    cmd_prewarm_worktree_pool,
    cmd_worktree_create,
    cmd_worktree_release,
)

LOCAL_EXECUTION_COMMANDS = {
    "close-ready-execution-tasks",
    "checkpoint-task-results",
    "commit-task-results",
    "push-task-branch",
    "create-task-pr",
    "publish-task-results",
    "publish-preflight",
    "worker-self-loop-once",
    "worker-self-loop-loop",
}


def _ensure_control_plane_only(command_name: str) -> None:
    current = Path.cwd().resolve()
    control_root = resolve_control_plane_root(current)
    if current != control_root:
        raise GovernanceError(f"{command_name} must run from the main control plane; clone-side {command_name} is frozen")


def _cmd_close_ready_execution_tasks(args: argparse.Namespace) -> int:
    _ensure_control_plane_only("close-ready-execution-tasks")
    return roadmap_closeout_main()


def _command_cwd(args: argparse.Namespace) -> Path:
    current = Path.cwd().resolve()
    if getattr(args, "command", None) in LOCAL_EXECUTION_COMMANDS:
        return current
    try:
        return resolve_control_plane_root(current)
    except GovernanceError:
        return current


@contextmanager
def _command_root(args: argparse.Namespace):
    current = Path.cwd().resolve()
    target = _command_cwd(args)
    if target != current:
        os.chdir(target)
    try:
        yield
    finally:
        if target != current:
            os.chdir(current)


def add_coordination_commands(subparsers) -> None:
    planner_parser = subparsers.add_parser("plan-coordination")
    planner_parser.set_defaults(func=cmd_plan_coordination)

    roadmap_candidates_parser = subparsers.add_parser("plan-roadmap-candidates")
    roadmap_candidates_parser.add_argument("--output", default=".codex/local/roadmap_candidates/index.yaml")
    roadmap_candidates_parser.set_defaults(func=cmd_plan_roadmap_candidates)

    compile_candidates_parser = subparsers.add_parser("compile-roadmap-candidates")
    compile_candidates_parser.set_defaults(func=cmd_compile_roadmap_candidates)

    refresh_candidates_parser = subparsers.add_parser("refresh-roadmap-candidates")
    refresh_candidates_parser.add_argument("--loop", action="store_true")
    refresh_candidates_parser.add_argument("--interval-seconds", type=int, default=60)
    refresh_candidates_parser.add_argument("--cycles", type=int, default=0)
    refresh_candidates_parser.set_defaults(func=cmd_refresh)

    review_pool_parser = subparsers.add_parser("review-candidate-pool")
    review_pool_parser.set_defaults(func=cmd_review)

    explain_candidate_parser = subparsers.add_parser("explain-candidate")
    explain_candidate_parser.add_argument("candidate_id")
    explain_candidate_parser.set_defaults(func=cmd_explain_candidate)

    explain_pool_parser = subparsers.add_parser("explain-candidate-pool")
    explain_pool_parser.set_defaults(func=cmd_explain_pool)

    explain_claim_parser = subparsers.add_parser("explain-claim-decision")
    explain_claim_parser.set_defaults(func=cmd_explain_claim_decision)

    explain_release_parser = subparsers.add_parser("explain-release-chain")
    explain_release_parser.add_argument("candidate_id")
    explain_release_parser.set_defaults(func=cmd_explain_release_chain)

    close_ready_execution_parser = subparsers.add_parser("close-ready-execution-tasks")
    close_ready_execution_parser.set_defaults(func=_cmd_close_ready_execution_tasks)

    claim_next_parser = subparsers.add_parser("claim-next")
    claim_next_parser.add_argument("--write-claim", action="store_true")
    claim_next_parser.add_argument("--promote-task", action="store_true")
    claim_next_parser.add_argument("--worktree-root")
    claim_next_parser.add_argument("--worker-owner", choices=list(EXECUTION_WORKER_OWNERS))
    claim_next_parser.add_argument("--dispatch-target", choices=["worktree_pool", "full_clone"], default="worktree_pool")
    claim_next_parser.add_argument("--full-clone-slot-id")
    claim_next_parser.add_argument("--window-id", default="window-local")
    claim_next_parser.add_argument("--lease-minutes", type=int, default=30)
    claim_next_parser.add_argument("--now")
    claim_next_parser.set_defaults(func=cmd_claim_next)

    promote_parser = subparsers.add_parser("promote-candidate")
    promote_parser.add_argument("candidate_id")
    promote_parser.add_argument("--activate", action="store_true")
    promote_parser.set_defaults(func=cmd_promote_candidate)

    handoff_parser = subparsers.add_parser("handoff")
    handoff_parser.add_argument("task_id")
    handoff_parser.add_argument("--completed-item", action="append", default=[])
    handoff_parser.add_argument("--remaining-item", action="append", default=[])
    handoff_parser.add_argument("--next-step")
    handoff_parser.add_argument("--next-test", action="append", default=[])
    handoff_parser.add_argument("--risk", action="append", default=[])
    handoff_parser.add_argument("--candidate-write-path", action="append", default=[])
    handoff_parser.add_argument("--candidate-test-path", action="append", default=[])
    handoff_parser.add_argument("--resume-note", action="append", default=[])
    handoff_parser.set_defaults(func=cmd_handoff)

    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("task_id")
    release_parser.add_argument("--next-test", action="append", default=[])
    release_parser.set_defaults(func=cmd_release)

    takeover_parser = subparsers.add_parser("takeover")
    takeover_parser.add_argument("task_id")
    takeover_parser.add_argument("--next-step")
    takeover_parser.add_argument("--next-test", action="append", default=[])
    takeover_parser.add_argument("--risk", action="append", default=[])
    takeover_parser.add_argument("--candidate-write-path", action="append", default=[])
    takeover_parser.add_argument("--candidate-test-path", action="append", default=[])
    takeover_parser.add_argument("--resume-note", action="append", default=[])
    takeover_parser.set_defaults(func=cmd_takeover)

    status_parser = subparsers.add_parser("orchestration-status")
    status_parser.add_argument("--format", choices=["yaml", "json"], default="yaml")
    status_parser.set_defaults(func=cmd_orchestration_status)


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
    new_parser.add_argument("--successor-state", choices=["immediate", "backlog"])
    new_parser.add_argument("--allowed-dirs", nargs="*", default=[])
    new_parser.add_argument("--reserved-paths", nargs="*", default=[])
    new_parser.add_argument("--planned-write-paths", nargs="*", default=[])
    new_parser.add_argument("--planned-test-paths", nargs="*", default=[])
    new_parser.add_argument("--required-tests", nargs="*", default=[])
    new_parser.set_defaults(func=cmd_new)

    queue_activate_parser = subparsers.add_parser("queue-and-activate")
    queue_activate_parser.add_argument("task_id")
    queue_activate_parser.add_argument("--title", required=True)
    queue_activate_parser.add_argument("--stage", required=True)
    queue_activate_parser.add_argument("--branch")
    queue_activate_parser.add_argument("--task-kind", default="coordination", choices=["coordination", "execution"])
    queue_activate_parser.add_argument("--execution-mode", choices=["shared_coordination", "isolated_worktree"])
    queue_activate_parser.add_argument("--parent-task-id")
    queue_activate_parser.add_argument("--size-class", default="standard", choices=["micro", "standard", "heavy"])
    queue_activate_parser.add_argument("--automation-mode", choices=["manual", "assisted", "autonomous"])
    queue_activate_parser.add_argument("--topology", choices=["single_task", "single_worker", "parallel_parent"])
    queue_activate_parser.add_argument("--successor-state", choices=["immediate", "backlog"])
    queue_activate_parser.add_argument("--allowed-dirs", nargs="*", default=[])
    queue_activate_parser.add_argument("--reserved-paths", nargs="*", default=[])
    queue_activate_parser.add_argument("--planned-write-paths", nargs="*", default=[])
    queue_activate_parser.add_argument("--planned-test-paths", nargs="*", default=[])
    queue_activate_parser.add_argument("--required-tests", nargs="*", default=[])
    queue_activate_parser.add_argument("--existing-ok", action="store_true")
    queue_activate_parser.set_defaults(func=cmd_queue_and_activate)

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

    reconcile_parser = subparsers.add_parser("reconcile-ledgers")
    reconcile_parser.add_argument("--write", action="store_true")
    reconcile_parser.set_defaults(func=cmd_reconcile_ledgers)

    derive_parser = subparsers.add_parser("derive-ledgers")
    derive_parser.add_argument("--from", dest="source", required=True, choices=["current-task", "task-file"])
    derive_parser.add_argument("--task-id")
    derive_parser.add_argument("--write", action="store_true")
    derive_parser.set_defaults(func=cmd_derive_ledgers)

    split_parser = subparsers.add_parser("split-check")
    split_parser.add_argument("parent_task_id")
    split_parser.set_defaults(func=cmd_split_check)

    topology_parser = subparsers.add_parser("decide-topology")
    topology_parser.add_argument("task_id")
    topology_parser.set_defaults(func=cmd_decide_topology)

    add_continuation_commands(subparsers)
    add_coordination_commands(subparsers)
    add_publish_commands(subparsers)


def add_continuation_commands(subparsers) -> None:
    continue_current_parser = subparsers.add_parser("continue-current")
    continue_current_parser.set_defaults(func=cmd_continue_current)

    continue_roadmap_parser = subparsers.add_parser("continue-roadmap")
    continue_roadmap_parser.set_defaults(func=cmd_continue_roadmap)


def add_publish_commands(subparsers) -> None:
    publish_preflight_parser = subparsers.add_parser("publish-preflight")
    publish_preflight_parser.add_argument("--action", default="publish-task-results", choices=PUBLISH_ACTIONS)
    publish_preflight_parser.add_argument("--task-id")
    publish_preflight_parser.set_defaults(func=cmd_publish_preflight)

    checkpoint_parser = subparsers.add_parser("checkpoint-task-results")
    checkpoint_parser.add_argument("--task-id")
    checkpoint_parser.add_argument("--message")
    checkpoint_parser.set_defaults(func=cmd_checkpoint_task_results)

    commit_parser = subparsers.add_parser("commit-task-results")
    commit_parser.add_argument("--task-id")
    commit_parser.add_argument("--message")
    commit_parser.set_defaults(func=cmd_commit_task_results)

    push_parser = subparsers.add_parser("push-task-branch")
    push_parser.add_argument("--task-id")
    push_parser.set_defaults(func=cmd_push_task_branch)

    pr_parser = subparsers.add_parser("create-task-pr")
    pr_parser.add_argument("--task-id")
    pr_parser.add_argument("--title")
    pr_parser.add_argument("--body")
    pr_parser.add_argument("--base-branch")
    pr_parser.set_defaults(func=cmd_create_task_pr)

    publish_parser = subparsers.add_parser("publish-task-results")
    publish_parser.add_argument("--task-id")
    publish_parser.add_argument("--message")
    publish_parser.add_argument("--title")
    publish_parser.add_argument("--body")
    publish_parser.add_argument("--base-branch")
    publish_parser.set_defaults(func=cmd_publish_task_results)


def add_worktree_commands(subparsers) -> None:
    clone_pool_parser = subparsers.add_parser("provision-full-clone-pool")
    clone_pool_parser.add_argument("--slot-id")
    clone_pool_parser.add_argument("--refresh", action="store_true")
    clone_pool_parser.set_defaults(func=cmd_provision_full_clone_pool)

    audit_clone_pool_parser = subparsers.add_parser("audit-full-clone-pool")
    audit_clone_pool_parser.add_argument("--slot-id")
    audit_clone_pool_parser.set_defaults(func=cmd_audit_full_clone_pool)

    refresh_clone_pool_parser = subparsers.add_parser("refresh-full-clone-pool")
    refresh_clone_pool_parser.add_argument("--slot-id")
    refresh_clone_pool_parser.set_defaults(func=cmd_refresh_full_clone_pool)

    rebuild_clone_pool_parser = subparsers.add_parser("rebuild-full-clone-pool")
    rebuild_clone_pool_parser.add_argument("--slot-id")
    rebuild_clone_pool_parser.set_defaults(func=cmd_rebuild_full_clone_pool)

    prewarm_parser = subparsers.add_parser("prewarm-worktree-pool")
    prewarm_parser.add_argument("--slot-id")
    prewarm_parser.set_defaults(func=cmd_prewarm_worktree_pool)

    prepare_parser = subparsers.add_parser("prepare-child-execution")
    prepare_parser.add_argument("task_id")
    prepare_parser.add_argument("--path", required=True)
    prepare_parser.add_argument("--worker-owner", choices=list(EXECUTION_WORKER_OWNERS))
    prepare_parser.set_defaults(func=cmd_prepare_child_execution)

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

    worker_loop_once = subparsers.add_parser("worker-self-loop-once")
    worker_loop_once.add_argument("--task-id")
    worker_loop_once.set_defaults(func=cmd_worker_self_loop_once)

    worker_loop = subparsers.add_parser("worker-self-loop-loop")
    worker_loop.add_argument("--task-id")
    worker_loop.add_argument("--interval-seconds", type=int, default=60)
    worker_loop.add_argument("--cycles", type=int, default=0)
    worker_loop.set_defaults(func=cmd_worker_self_loop_loop)


def _add_worker_state_commands(subparsers) -> None:
    worker_start_parser = subparsers.add_parser("worker-start")
    worker_start_parser.add_argument("task_id")
    worker_start_parser.add_argument("--worker-owner", choices=["coordinator", *EXECUTION_WORKER_OWNERS])
    worker_start_parser.add_argument("--path")
    worker_start_parser.set_defaults(func=cmd_worker_start)

    worker_report_parser = subparsers.add_parser("worker-report")
    worker_report_parser.add_argument("task_id")
    worker_report_parser.add_argument("--note", action="append", default=[])
    worker_report_parser.add_argument("--tests", nargs="+", action="append", default=[])
    worker_report_parser.add_argument("--completed-item", action="append", default=[])
    worker_report_parser.add_argument("--remaining-item", action="append", default=[])
    worker_report_parser.add_argument("--next-step")
    worker_report_parser.add_argument("--next-test", action="append", default=[])
    worker_report_parser.add_argument("--risk", action="append", default=[])
    worker_report_parser.add_argument("--candidate-write-path", action="append", default=[])
    worker_report_parser.add_argument("--candidate-test-path", action="append", default=[])
    worker_report_parser.add_argument("--resume-note", action="append", default=[])
    worker_report_parser.set_defaults(func=cmd_worker_report)

    worker_blocked_parser = subparsers.add_parser("worker-blocked")
    worker_blocked_parser.add_argument("task_id")
    worker_blocked_parser.add_argument("--reason", required=True)
    worker_blocked_parser.add_argument("--remaining-item", action="append", default=[])
    worker_blocked_parser.add_argument("--next-step")
    worker_blocked_parser.add_argument("--next-test", action="append", default=[])
    worker_blocked_parser.add_argument("--risk", action="append", default=[])
    worker_blocked_parser.add_argument("--candidate-write-path", action="append", default=[])
    worker_blocked_parser.add_argument("--candidate-test-path", action="append", default=[])
    worker_blocked_parser.add_argument("--resume-note", action="append", default=[])
    worker_blocked_parser.set_defaults(func=cmd_worker_blocked)

    worker_finish_parser = subparsers.add_parser("worker-finish")
    worker_finish_parser.add_argument("task_id")
    worker_finish_parser.add_argument("--summary", required=True)
    worker_finish_parser.add_argument("--tests", nargs="+", action="append", default=[])
    worker_finish_parser.add_argument("--candidate-paths", nargs="*", default=[])
    worker_finish_parser.add_argument("--completed-item", action="append", default=[])
    worker_finish_parser.add_argument("--remaining-item", action="append", default=[])
    worker_finish_parser.add_argument("--next-step")
    worker_finish_parser.add_argument("--next-test", action="append", default=[])
    worker_finish_parser.add_argument("--risk", action="append", default=[])
    worker_finish_parser.add_argument("--candidate-write-path", action="append", default=[])
    worker_finish_parser.add_argument("--candidate-test-path", action="append", default=[])
    worker_finish_parser.add_argument("--resume-note", action="append", default=[])
    worker_finish_parser.set_defaults(func=cmd_worker_finish)


def _add_worker_gate_commands(subparsers) -> None:
    worker_design_confirm_parser = subparsers.add_parser("worker-design-confirm")
    worker_design_confirm_parser.add_argument("task_id")
    worker_design_confirm_parser.add_argument("--summary", required=True)
    worker_design_confirm_parser.add_argument(
        "--implementation-kind",
        required=True,
        choices=["unknown", "code", "docs", "governance", "mixed"],
    )
    worker_design_confirm_parser.set_defaults(func=cmd_worker_design_confirm)

    worker_plan_parser = subparsers.add_parser("worker-plan")
    worker_plan_parser.add_argument("task_id")
    worker_plan_parser.add_argument("--summary", required=True)
    worker_plan_parser.add_argument("--file", action="append", default=[])
    worker_plan_parser.add_argument("--step", action="append", default=[])
    worker_plan_parser.add_argument("--test", action="append", default=[])
    worker_plan_parser.add_argument("--verify", action="append", default=[])
    worker_plan_parser.set_defaults(func=cmd_worker_plan)

    worker_test_first_parser = subparsers.add_parser("worker-test-first")
    worker_test_first_parser.add_argument("task_id")
    worker_test_first_parser.add_argument("--command", action="append", default=[])
    worker_test_first_parser.add_argument("--note")
    worker_test_first_parser.set_defaults(func=cmd_worker_test_first)

    worker_spec_review_parser = subparsers.add_parser("worker-spec-review")
    worker_spec_review_parser.add_argument("task_id")
    worker_spec_review_parser.add_argument("--status", required=True, choices=["passed", "failed"])
    worker_spec_review_parser.add_argument("--summary", required=True)
    worker_spec_review_parser.set_defaults(func=cmd_worker_spec_review)

    worker_quality_review_parser = subparsers.add_parser("worker-quality-review")
    worker_quality_review_parser.add_argument("task_id")
    worker_quality_review_parser.add_argument("--status", required=True, choices=["passed", "failed"])
    worker_quality_review_parser.add_argument("--summary", required=True)
    worker_quality_review_parser.set_defaults(func=cmd_worker_quality_review)


def _add_worker_runtime_commands(subparsers) -> None:
    worker_heartbeat_parser = subparsers.add_parser("worker-heartbeat")
    worker_heartbeat_parser.add_argument("task_id")
    worker_heartbeat_parser.add_argument("--worker-id", default="worker-local-01")
    worker_heartbeat_parser.add_argument("--lane-session-id")
    worker_heartbeat_parser.add_argument("--executor-status")
    worker_heartbeat_parser.add_argument("--result")
    worker_heartbeat_parser.set_defaults(func=cmd_worker_heartbeat)

    auto_close_parser = subparsers.add_parser("auto-close-children")
    auto_close_parser.add_argument("parent_task_id")
    auto_close_parser.set_defaults(func=cmd_auto_close_children)


def add_worker_commands(subparsers) -> None:
    _add_worker_state_commands(subparsers)
    _add_worker_gate_commands(subparsers)
    _add_worker_runtime_commands(subparsers)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9S governance task operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_task_lifecycle_commands(subparsers)
    add_worktree_commands(subparsers)
    add_worker_commands(subparsers)
    return parser


def main() -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args()
    try:
        with _command_root(args):
            return args.func(args)
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1
