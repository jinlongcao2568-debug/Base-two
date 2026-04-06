from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml

from check_hygiene import analyze_python_file, iter_python_files, resolve_declared_paths
from governance_lib import (
    GovernanceError,
    configure_utf8_stdio,
    find_repo_root,
    git_status_paths,
    load_capability_map,
    load_current_task,
    load_task_policy,
    load_task_registry,
    load_worktree_registry,
    read_roadmap,
    task_map,
)
from governance_repo_checks import run_repo_checks
from task_closeout import assess_live_closeout
from task_coordination_lease import assess_coordination_lease
from task_continuation_ops import _resolve_roadmap_successor
from task_continuation_ops import assess_continuation_readiness
from task_dirty_state import classify_task_dirty_state
from task_handoff import build_recovery_pack
from task_publish_ops import PUBLISH_ACTIONS, publish_preflight
from task_rendering import find_task


INTENTS_FILE = Path("docs/governance/AUTOMATION_INTENTS.yaml")
NORMALIZE_PATTERN = re.compile(r"[\s\-_，。！？!?,.;；：:\"'`()（）【】\[\]<>《》/\\]+")


def _normalize_text(text: str) -> str:
    return NORMALIZE_PATTERN.sub("", text.strip().lower())


def _load_catalog(root: Path) -> dict[str, Any]:
    path = root / INTENTS_FILE
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _intent_map(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {intent["intent_id"]: intent for intent in catalog.get("supported_intents", [])}


def _contains_any(normalized_text: str, values: list[str]) -> list[str]:
    hits: list[str] = []
    for value in values:
        normalized_value = _normalize_text(value)
        if normalized_value and normalized_value in normalized_text:
            hits.append(value)
    return hits


def _active_task_status(root: Path) -> str:
    current_payload = load_current_task(root)
    if current_payload.get("status") == "idle":
        return "idle"
    registry = load_task_registry(root)
    current_task = find_task(registry.get("tasks", []), current_payload["current_task_id"])
    return current_task["status"]


def _generic_continue_detected(catalog: dict[str, Any], normalized_text: str) -> bool:
    return bool(_contains_any(normalized_text, catalog.get("generic_continue_signals", [])))


def _recognize_intent(root: Path, catalog: dict[str, Any], utterance: str) -> tuple[dict[str, Any] | None, str | None, str]:
    normalized_text = _normalize_text(utterance)
    if not normalized_text:
        return None, None, "输入为空，无法识别自动化意图。"

    novice_intent = next(
        (intent for intent in catalog.get("supported_intents", []) if intent.get("intent_id") == "novice-continue"),
        None,
    )
    if novice_intent is not None:
        novice_examples = [novice_intent["canonical_phrase"], *(novice_intent.get("examples") or [])]
        for example in novice_examples:
            if _normalize_text(example) == normalized_text:
                return novice_intent, example, f"精确匹配到 `{example}`。"

    candidates: list[tuple[int, dict[str, Any], str]] = []
    for intent in catalog.get("supported_intents", []):
        examples = [intent["canonical_phrase"], *(intent.get("examples") or [])]
        for example in examples:
            if _normalize_text(example) == normalized_text:
                return intent, example, f"精确匹配到 `{example}`。"

        if _contains_any(normalized_text, intent.get("disallow_any", [])):
            continue

        action_hits = _contains_any(normalized_text, intent.get("action_any", []))
        context_hits = _contains_any(normalized_text, intent.get("context_any", []))
        if not context_hits:
            continue
        score = len(action_hits) * 2 + len(context_hits) * 4
        matched_phrase = context_hits[0] if context_hits else action_hits[0]
        candidates.append((score, intent, matched_phrase))

    candidates.sort(key=lambda item: item[0], reverse=True)
    if candidates:
        top_score, top_intent, top_phrase = candidates[0]
        if len(candidates) > 1 and top_score - candidates[1][0] < 2:
            return None, None, "检测到多个可行意图，但当前表达不足以安全区分。"
        return top_intent, top_phrase, f"根据自由表达信号匹配到 `{top_intent['intent_id']}`。"

    if not _generic_continue_detected(catalog, normalized_text):
        return None, None, "未识别到可执行的继续类意图。"

    current_status = _active_task_status(root)
    intents_by_id = _intent_map(catalog)
    if current_status in {"doing", "paused"}:
        intent = intents_by_id["continue-current"]
        return intent, "generic_active_continue", "检测到泛化“继续”表达，且当前 live 任务仍在进行中，安全归入继续当前任务。"
    return None, None, "检测到泛化“继续”表达，但当前状态可能触发任务切换；请补充“当前任务”或“路线图/下一步”等边界词。"


def _dirty_blockers(
    root: Path, current_payload: dict[str, Any] | None, current_task: dict[str, Any] | None
) -> tuple[list[str], dict[str, Any] | None]:
    if current_payload is None or current_task is None:
        dirty = git_status_paths(root)
        if not dirty:
            return [], None
        return [f"unsafe dirty paths: {', '.join(dirty)}"], None
    classified = classify_task_dirty_state(root, current_payload=current_payload, task=current_task)
    if classified["dirty_state"] != "unsafe_dirty":
        return [], classified
    return [f"unsafe dirty paths: {', '.join(classified['dirty_paths_by_class']['unsafe_paths'])}"], classified


def _dedupe_items(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _run_repo_gate(root: Path) -> list[str]:
    try:
        registry = load_task_registry(root)
        worktrees = load_worktree_registry(root)
        run_repo_checks(root, registry, task_map(registry), worktrees)
        return []
    except GovernanceError as error:
        return [str(error)]


def _run_hygiene_gate(root: Path) -> list[str]:
    declared_paths = resolve_declared_paths(root, [])
    warnings: list[str] = []
    errors: list[str] = []
    for path in iter_python_files(root, declared_paths):
        file_warnings, file_errors = analyze_python_file(path)
        warnings.extend(file_warnings)
        errors.extend(file_errors)
    return errors


def _load_live_task(root: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    current_payload = load_current_task(root)
    if current_payload.get("status") == "idle":
        return current_payload, None
    registry = load_task_registry(root)
    task = find_task(registry.get("tasks", []), current_payload["current_task_id"])
    return current_payload, task


def _preview_roadmap_successor(root: Path, current_task_id: str | None) -> tuple[dict[str, Any], str]:
    registry = copy.deepcopy(load_task_registry(root))
    capability_map = copy.deepcopy(load_capability_map(root))
    task_policy = copy.deepcopy(load_task_policy(root))
    frontmatter, _ = read_roadmap(root)
    return _resolve_roadmap_successor(
        root,
        registry,
        capability_map,
        task_policy,
        copy.deepcopy(frontmatter),
        current_task_id,
    )


def _preflight_continue_current(root: Path, intent: dict[str, Any], matched_phrase: str | None) -> dict[str, Any]:
    current_payload, current_task = _load_live_task(root)
    blockers, dirty = _dirty_blockers(root, current_payload, current_task)
    closeout = assess_live_closeout(root, current_payload=current_payload, current_task=current_task)
    recovery_pack = None
    recovery_source = None
    recovery_warnings: list[str] = []
    lease = None
    if current_task is not None:
        recovery_pack, recovery_source, recovery_warnings = build_recovery_pack(root, current_task)
        lease = assess_coordination_lease(root, current_task)
    if current_payload.get("status") == "idle":
        blockers.append("CURRENT_TASK.yaml 当前为 idle；请改用路线图推进，或先显式激活任务。")
    elif current_task is not None:
        if current_task["status"] == "blocked":
            reason = current_task.get("blocked_reason") or "blocked without recorded reason"
            blockers.append(f"当前任务已阻塞：{reason}")
        elif current_task["status"] == "done":
            blockers.append("当前任务已关账；请改用路线图推进，或显式激活下一个任务。")
        elif current_task["status"] == "review" and closeout["status"] != "ready":
            blockers.extend(closeout.get("blockers", []))
            blockers.extend(closeout.get("diagnostics", []))
        if lease is not None and lease["enforced"] and not lease["can_write"]:
            blockers.append(
                f"当前任务写租约已被其他窗口持有：{lease['owner_session_id']}；默认仅允许只读恢复，请先执行 release 或 takeover"
            )

    if blockers:
        return {
            "status": "blocked",
            "matched_phrase": matched_phrase,
            "intent_id": intent["intent_id"],
            "mapped_command": intent["mapped_command"],
            "explanation": "已识别为继续当前任务，但前置条件不满足。",
            "blockers": _dedupe_items(blockers),
            "closeout_recommendation": closeout,
            "recovery_pack": recovery_pack,
            "recovery_source": recovery_source,
            "recovery_warnings": recovery_warnings,
            "dirty_state": None if dirty is None else dirty["dirty_state"],
            "dirty_paths_by_class": None if dirty is None else dirty["dirty_paths_by_class"],
        }

    task_id = current_task["task_id"] if current_task is not None else current_payload.get("current_task_id")
    task_status = current_task["status"] if current_task is not None else current_payload.get("status")
    if closeout["status"] == "ready" and current_task is not None and current_task["status"] in {"doing", "review"}:
        explanation = (
            f"将对 live 当前任务 `{task_id}` 执行 ai_guarded 关账；当前状态为 `{task_status}`，符合条件时会直接回到 idle。"
        )
    else:
        explanation = f"将继续 live 当前任务 `{task_id}`，当前状态为 `{task_status}`，不会选择后继任务。"
    return {
        "status": "ready",
        "matched_phrase": matched_phrase,
        "intent_id": intent["intent_id"],
        "mapped_command": intent["mapped_command"],
        "explanation": explanation,
        "blockers": [],
        "closeout_recommendation": closeout,
        "recovery_pack": recovery_pack,
        "recovery_source": recovery_source,
        "recovery_warnings": recovery_warnings,
        "dirty_state": None if dirty is None else dirty["dirty_state"],
        "dirty_paths_by_class": None if dirty is None else dirty["dirty_paths_by_class"],
    }


def _preflight_continue_roadmap(root: Path, intent: dict[str, Any], matched_phrase: str | None) -> dict[str, Any]:
    blockers: list[str] = []
    blockers.extend(_run_repo_gate(root))
    blockers.extend(_run_hygiene_gate(root))

    current_payload, current_task = _load_live_task(root)
    status = current_payload.get("status")
    closeout = assess_live_closeout(root, current_payload=current_payload, current_task=current_task)
    readiness = assess_continuation_readiness(root, current_payload=current_payload, current_task=current_task)
    blockers.extend(readiness.get("blockers", []))

    successor_summary = None
    if readiness.get("next_successor_task_id"):
        successor_summary = (
            f"后继任务将解析为 `{readiness['next_successor_task_id']}`，"
            f"来源 `{readiness['successor_source']}`。"
        )

    if blockers:
        return {
            "status": "blocked",
            "matched_phrase": matched_phrase,
            "intent_id": intent["intent_id"],
            "mapped_command": intent["mapped_command"],
            "explanation": "已识别为按路线图推进，但当前前置条件不满足。",
            "blockers": _dedupe_items(blockers),
            "closeout_recommendation": closeout,
        }

    if readiness["status"] == "continue-current" and current_task is not None:
        explanation = (
            f"live 当前任务 `{current_task['task_id']}` 仍在 `{current_task['status']}`，"
            "continue-roadmap 将退化为继续当前任务，不会跳到后继。"
        )
    elif closeout["status"] == "ready":
        explanation = (
            f"{closeout['summary']} 执行 continue-roadmap 时将先自动关账当前任务，"
            f"随后解析后继。{(' ' + successor_summary) if successor_summary else ''}"
        ).strip()
    else:
        explanation = successor_summary or "路线图前置检查通过，可以继续执行自动推进。"
    return {
        "status": "ready",
        "matched_phrase": matched_phrase,
        "intent_id": intent["intent_id"],
        "mapped_command": intent["mapped_command"],
        "explanation": explanation,
        "blockers": [],
        "closeout_recommendation": closeout,
    }


def _preflight_publish_action(root: Path, intent: dict[str, Any], matched_phrase: str | None) -> dict[str, Any]:
    action = intent["intent_id"]
    if action not in PUBLISH_ACTIONS:
        raise GovernanceError(f"unsupported publish intent_id: {action}")
    result = publish_preflight(root, action=action)
    result.update(
        {
            "matched_phrase": matched_phrase,
            "intent_id": action,
            "mapped_command": intent["mapped_command"],
            "closeout_recommendation": None,
            "recovery_pack": None,
            "recovery_source": None,
            "recovery_warnings": [],
        }
    )
    return result


def _decorate_novice_payload(
    payload: dict[str, Any],
    *,
    intent: dict[str, Any],
    matched_phrase: str | None,
    resolved_intent: dict[str, Any],
) -> dict[str, Any]:
    decorated = dict(payload)
    decorated["matched_phrase"] = matched_phrase
    decorated["intent_id"] = intent["intent_id"]
    decorated["mapped_command"] = intent["mapped_command"]
    decorated["resolved_intent_id"] = resolved_intent["intent_id"]
    decorated["resolved_mapped_command"] = resolved_intent["mapped_command"]
    decorated["novice_entry"] = True
    if decorated["status"] == "ready":
        decorated["explanation"] = (
            f"小白入口已根据当前仓库状态自动选择 `{resolved_intent['intent_id']}`。"
        )
    return decorated


def _preflight_novice_continue(root: Path, intent: dict[str, Any], matched_phrase: str | None) -> dict[str, Any]:
    catalog = _load_catalog(root)
    intents_by_id = _intent_map(catalog)
    current_payload, current_task = _load_live_task(root)
    if current_payload.get("status") == "idle":
        payload = _preflight_continue_roadmap(root, intents_by_id["continue-roadmap"], matched_phrase)
        return _decorate_novice_payload(
            payload,
            intent=intent,
            matched_phrase=matched_phrase,
            resolved_intent=intents_by_id["continue-roadmap"],
        )
    if current_task is not None and current_task.get("status") in {"doing", "paused", "blocked"}:
        payload = _preflight_continue_current(root, intents_by_id["continue-current"], matched_phrase)
        return _decorate_novice_payload(
            payload,
            intent=intent,
            matched_phrase=matched_phrase,
            resolved_intent=intents_by_id["continue-current"],
        )
    payload = _preflight_continue_roadmap(root, intents_by_id["continue-roadmap"], matched_phrase)
    return _decorate_novice_payload(
        payload,
        intent=intent,
        matched_phrase=matched_phrase,
        resolved_intent=intents_by_id["continue-roadmap"],
    )


def preflight(root: Path, utterance: str) -> dict[str, Any]:
    catalog = _load_catalog(root)
    intent, matched_phrase, explanation = _recognize_intent(root, catalog, utterance)
    if intent is None:
        return {
            "status": "unsupported",
            "matched_phrase": matched_phrase,
            "intent_id": None,
            "mapped_command": None,
            "explanation": explanation,
            "blockers": [],
            "closeout_recommendation": None,
            "recovery_pack": None,
            "recovery_source": None,
            "recovery_warnings": [],
        }
    if intent["intent_id"] == "continue-current":
        return _preflight_continue_current(root, intent, matched_phrase)
    if intent["intent_id"] == "novice-continue":
        return _preflight_novice_continue(root, intent, matched_phrase)
    if intent["intent_id"] in {"continue-roadmap", "continue-roadmap-loop"}:
        return _preflight_continue_roadmap(root, intent, matched_phrase)
    if intent["intent_id"] in PUBLISH_ACTIONS:
        return _preflight_publish_action(root, intent, matched_phrase)
    raise GovernanceError(f"unsupported intent_id in catalog: {intent['intent_id']}")


def _command_argv(intent: dict[str, Any]) -> list[str]:
    argv = list(intent.get("command_argv") or [])
    if not argv:
        raise GovernanceError(f"intent command_argv missing: {intent['intent_id']}")
    if argv[0] == "python":
        argv[0] = sys.executable
        if len(argv) > 1 and argv[1].startswith("scripts/"):
            argv[1] = str((Path(__file__).resolve().parent / Path(argv[1]).name))
    return argv


def execute(root: Path, utterance: str) -> int:
    catalog = _load_catalog(root)
    preflight_result = preflight(root, utterance)
    if preflight_result["status"] != "ready":
        print(json.dumps(preflight_result, ensure_ascii=False, indent=2))
        return 1

    intents_by_id = _intent_map(catalog)
    intent = intents_by_id[preflight_result["intent_id"]]
    if preflight_result["intent_id"] == "novice-continue":
        resolved_intent = intents_by_id[preflight_result["resolved_intent_id"]]
        print(
            f"[OK] automation-intent resolved `{preflight_result['intent_id']}` "
            f"from `{preflight_result['matched_phrase']}` -> `{resolved_intent['intent_id']}`"
        )
        result = subprocess.run(
            _command_argv(resolved_intent),
            cwd=root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        return result.returncode
    print(
        f"[OK] automation-intent resolved `{preflight_result['intent_id']}` "
        f"from `{preflight_result['matched_phrase']}`"
    )
    result = subprocess.run(
        _command_argv(intent),
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="AX9S automation intent router")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight_parser = subparsers.add_parser("preflight")
    preflight_parser.add_argument("--utterance", required=True)

    execute_parser = subparsers.add_parser("execute")
    execute_parser.add_argument("--utterance", required=True)

    args = parser.parse_args()
    try:
        configure_utf8_stdio()
        root = find_repo_root()
        if args.command == "preflight":
            print(json.dumps(preflight(root, args.utterance), ensure_ascii=False, indent=2))
            return 0
        return execute(root, args.utterance)
    except GovernanceError as error:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "matched_phrase": None,
                    "intent_id": None,
                    "mapped_command": None,
                    "explanation": "自动化意图执行前检查失败。",
                    "blockers": [str(error)],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
