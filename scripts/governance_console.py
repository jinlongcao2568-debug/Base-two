from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import re
import socket
import subprocess
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse
import webbrowser

from governance_lib import GovernanceError, configure_utf8_stdio
from control_plane_root import detect_ledger_divergences, resolve_control_plane_root
from governance_runtime import load_yaml
from roadmap_explain import (
    explain_candidate,
    explain_claim_decision,
    explain_release_chain,
)
from review_candidate_pool import review_pool


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
PAGE_TITLE = "AX9 治理操作员控制台"
INDEX_FILE = Path(".codex/local/roadmap_candidates/index.yaml")
SUMMARY_FILE = Path(".codex/local/roadmap_candidates/summary.yaml")
TASK_REGISTRY_FILE = Path("docs/governance/TASK_REGISTRY.yaml")
FULL_CLONE_POOL_FILE = Path("docs/governance/FULL_CLONE_POOL.yaml")
CLAIMS_FILE = Path(".codex/local/roadmap_candidates/claims.yaml")
AUTO_REFRESH_FOREGROUND_SECONDS = 20
AUTO_REFRESH_BACKGROUND_SECONDS = 60

ACTION_COMMANDS: dict[str, tuple[str, ...]] = {
    "compile-roadmap-candidates": ("compile-roadmap-candidates",),
    "refresh-roadmap-candidates": ("refresh-roadmap-candidates",),
    "close-ready-execution-tasks": ("close-ready-execution-tasks",),
    "continue-roadmap": ("continue-roadmap",),
}

ACTION_LABELS_ZH: dict[str, str] = {
    "compile-roadmap-candidates": "编译候选池",
    "refresh-roadmap-candidates": "刷新候选池",
    "close-ready-execution-tasks": "关闭已就绪执行任务",
    "continue-roadmap": "继续路线图",
}

STATUS_LABELS_ZH: dict[str, str] = {
    "ready": "就绪",
    "resumable": "可续接",
    "waiting": "等待中",
    "blocked": "阻塞",
    "degraded": "降级",
    "doing": "进行中",
    "review": "待复核",
    "done": "已完成",
    "idle": "空闲",
    "stale": "陈旧",
}

INTENT_LABELS_ZH: dict[str, str] = {
    "module_root": "模块主根",
    "module_preview_root": "模块预览根",
    "integration_gate": "集成闸门",
    "parallel_lanes": "并行泳道",
    "hard_gate": "硬闸门",
    "lane_slice": "泳道切片",
}

ROOT_KIND_LABELS_ZH: dict[str, str] = {
    "formal_root": "正式主根",
    "preview_root": "预览主根",
    "hard_gate": "硬闸门",
}

BLOCKER_LABELS_ZH: dict[str, str] = {
    "active_claim": "已有窗口占用",
    "dependency_wait": "等待上游依赖",
    "expected_children_wait": "等待子候选完成",
    "capacity_exhausted": "并行窗口已满",
    "scope_conflict": "作用域冲突",
    "manual_gate": "需要人工确认",
    "out_of_mvp_scope": "超出MVP范围",
    "coverage_not_registered": "覆盖未登记",
    "pilot_only": "试点候选未启用",
    "planned_write_path_missing": "计划路径未物化",
    "stale_takeover_ready": "陈旧候选可接管",
    "stale_takeover_blocked": "陈旧候选接管受阻",
}

STAGE_TITLE_SUFFIX_TRANSLATIONS: dict[str, str] = {
    "orchestration contract and fixture boundary": "编排契约与夹具边界",
    "source-family integration gate": "源族集成闸门",
    "ingestion integration gate": "数据采集集成闸门",
    "parsing integration gate": "解析集成闸门",
    "validation integration gate": "校验集成闸门",
    "reporting integration gate": "报告集成闸门",
    "sales-context integration gate": "销售上下文集成闸门",
    "contact-context integration gate": "联系上下文集成闸门",
    "final customer-visible delivery gate": "最终客户可见交付闸门",
    "ingestion contract and raw payload fixture boundary": "数据采集契约与原始载荷夹具边界",
    "parsing contract and normalized record boundary": "解析契约与规范记录边界",
    "validation rule-hit contract and topic boundary": "校验规则命中契约与专题边界",
    "reporting artifact contract and snapshot boundary": "报告产物契约与快照边界",
    "sales context contract": "销售上下文契约",
    "contact context contract": "联系上下文契约",
    "source-family orchestration lane group": "源族编排泳道组",
    "source-family china slice": "源族中国切片",
    "source-family global slice": "源族全球切片",
    "raw payload preview root": "原始载荷预览根",
    "source-family ingestion lanes": "源族采集泳道",
    "normalized record preview root": "规范记录预览根",
    "parser-family lanes": "解析器族泳道",
    "validation preview root": "校验预览根",
    "rule-topic validation lanes": "规则专题校验泳道",
    "report artifact preview root": "报告产物预览根",
    "formatter and report snapshot lanes": "格式化与报告快照泳道",
    "project_fact single-writer fact surface gate": "project_fact 单写事实面闸门",
    "sales context preview root": "销售上下文预览根",
    "contact context preview root": "联系上下文预览根",
    "sales-context parallel lanes": "销售上下文并行泳道",
    "contact-context parallel lanes": "联系上下文并行泳道",
    "delivery preview root": "交付预览根",
}

DOMAIN_TITLE_TRANSLATIONS: dict[str, str] = {
    "domain_public_chain preview root": "公开链领域预览根",
    "domain_project_manager preview root": "项目经理领域预览根",
    "domain_competitor_analysis preview root": "竞对分析领域预览根",
    "domain_evidence preview root": "证据领域预览根",
    "domain_review_requests preview root": "复核请求领域预览根",
}


def _repo_root() -> Path:
    return resolve_control_plane_root()


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _console_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/"


def _run_task_ops(*args: str) -> dict[str, Any]:
    root = _repo_root()
    creationflags = 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        creationflags = subprocess.CREATE_NO_WINDOW
    result = subprocess.run(
        [sys.executable, str(_script_dir() / "task_ops.py"), *args],
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
    )
    return {
        "argv": ["python", "scripts/task_ops.py", *args],
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _status_label_zh(value: str | None) -> str:
    if not value:
        return "-"
    return STATUS_LABELS_ZH.get(value, value)


def _stage_label_zh(stage: str | None) -> str:
    if not stage:
        return "-"
    match = re.fullmatch(r"stage(\d+)", stage)
    if match:
        return f"阶段{match.group(1)}"
    if stage.startswith("domain"):
        return "领域层"
    return stage


def _candidate_intent_zh(value: str | None) -> str:
    if not value:
        return "-"
    return INTENT_LABELS_ZH.get(value, value)


def _root_kind_zh(value: str | None) -> str:
    if not value:
        return "-"
    return ROOT_KIND_LABELS_ZH.get(value, value)


def _blocking_reason_labels(codes: list[str] | None) -> list[str]:
    return [BLOCKER_LABELS_ZH.get(code, code) for code in (codes or [])]


def _first_reason_text(candidate: dict[str, Any]) -> str:
    for key in ("blocking_reason_text", "wait_reasons"):
        for value in candidate.get(key, []) or []:
            text = str(value).strip()
            if text:
                return text
    return ""


def _candidate_operator_reason(candidate: dict[str, Any]) -> str:
    status = str(candidate.get("status") or "")
    codes = list(candidate.get("blocking_reason_codes") or [])
    upstream = [str(item) for item in candidate.get("upstream_blocker_candidates") or [] if item]

    if "stale_takeover_blocked" in codes:
        return "旧任务已暂停，旧工作树还有未收口改动，当前不能直接接管。"
    if candidate.get("takeover_claimable") or "stale_takeover_ready" in codes:
        return "这是一条旧任务续接点，可直接接管，不要重复新开同任务。"
    if candidate.get("fresh_claimable") or status == "ready":
        return "已解锁，可直接接单执行。"
    if "dependency_wait" in codes and upstream:
        return f"前置候选未完成：{upstream[0]}。当前不是人工释放问题。"
    if "expected_children_wait" in codes:
        return "还在等待预期子候选完成，当前不是人工释放问题。"
    if "candidate_not_claimable" in codes:
        return "路线图当前不允许直接认领这条候选。"
    if status == "resumable":
        return "存在暂停中的正式任务，先续接该任务，不要重复新开。"
    if status == "waiting":
        return "依赖尚未满足，暂时不能释放。"
    if status == "blocked":
        return "当前被治理规则阻塞，先处理阻塞原因。"
    return _first_reason_text(candidate) or "当前暂无额外说明。"


def _candidate_copy_instruction(candidate: dict[str, Any]) -> str:
    status = str(candidate.get("status") or "")
    codes = list(candidate.get("blocking_reason_codes") or [])

    if candidate.get("fresh_claimable") or status == "ready":
        return "去任务池接单并执行，完成后回任务池继续接单并重复此流程。"
    if candidate.get("takeover_claimable") or "stale_takeover_ready" in codes:
        return "任务池发现旧任务续接点，可直接接管执行；完成后回任务池继续接单并重复此流程。"
    if status in {"resumable", "stale"} or "stale_takeover_blocked" in codes:
        return "任务池发现旧任务续接点，先处理该任务，不要重复新开同任务。"
    return "当前任务尚未解锁，先检查阻塞原因；解除后再回任务池接单。"


def _candidate_copy_reason(candidate: dict[str, Any]) -> str:
    if candidate.get("fresh_claimable") or str(candidate.get("status") or "") == "ready":
        return ""
    return _candidate_operator_reason(candidate)


def _translate_candidate_title(title: str | None) -> str:
    if not title:
        return "-"
    lowered = title.strip().lower()
    stage_match = re.fullmatch(r"stage(\d+)\s+(.+)", lowered)
    if stage_match:
        stage_no, suffix = stage_match.groups()
        if suffix in STAGE_TITLE_SUFFIX_TRANSLATIONS:
            return f"阶段{stage_no} {STAGE_TITLE_SUFFIX_TRANSLATIONS[suffix]}"
    if lowered in DOMAIN_TITLE_TRANSLATIONS:
        return DOMAIN_TITLE_TRANSLATIONS[lowered]
    return title


def _load_candidate_index(root: Path) -> dict[str, Any]:
    if (root / INDEX_FILE).exists():
        payload = load_yaml(root / INDEX_FILE) or {}
        if payload.get("candidates"):
            return payload
    return {"candidates": []}


def _candidate_lookup(root: Path, candidate_id: str) -> dict[str, Any] | None:
    for candidate in _load_candidate_index(root).get("candidates", []):
        if candidate.get("candidate_id") == candidate_id:
            return candidate
    return None


def _candidate_summary(candidate: dict[str, Any]) -> dict[str, Any]:
    title = candidate.get("title") or candidate.get("candidate_id") or "-"
    title_zh = _translate_candidate_title(title)
    status = candidate.get("status")
    operator_reason = _candidate_operator_reason(candidate)
    return {
        "candidate_id": candidate.get("candidate_id"),
        "title": title,
        "title_zh": title_zh,
        "display_name": f"{title_zh} / {title}",
        "stage": candidate.get("stage"),
        "stage_zh": _stage_label_zh(candidate.get("stage")),
        "module_id": candidate.get("module_id"),
        "status": status,
        "status_zh": _status_label_zh(status),
        "candidate_intent": candidate.get("candidate_intent"),
        "candidate_intent_zh": _candidate_intent_zh(candidate.get("candidate_intent")),
        "root_kind": candidate.get("root_kind"),
        "root_kind_zh": _root_kind_zh(candidate.get("root_kind")),
        "unlock_count": candidate.get("unlock_count"),
        "claimable": candidate.get("claimable"),
        "fresh_claimable": candidate.get("fresh_claimable"),
        "takeover_claimable": candidate.get("takeover_claimable"),
        "takeover_mode": candidate.get("takeover_mode"),
        "blocking_reason_codes": candidate.get("blocking_reason_codes", []),
        "blocking_reason_text": candidate.get("blocking_reason_text", []),
        "blocking_reason_labels": _blocking_reason_labels(candidate.get("blocking_reason_codes", [])),
        "wait_reasons": candidate.get("wait_reasons", []),
        "upstream_blocker_candidates": candidate.get("upstream_blocker_candidates", []),
        "operator_reason": operator_reason,
        "copy_instruction": _candidate_copy_instruction(candidate),
        "copy_reason": _candidate_copy_reason(candidate),
    }


def _tasks_by_id(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        str(task.get("task_id")): task
        for task in (payload or {}).get("tasks", []) or []
        if task.get("task_id")
    }


def _ledger_divergences(root: Path) -> list[dict[str, Any]]:
    return detect_ledger_divergences(root)


def _apply_divergence_to_candidate(summary: dict[str, Any], divergence_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate_id = str(summary.get("candidate_id") or "")
    direct = divergence_map.get(candidate_id)
    upstream = [str(item) for item in summary.get("upstream_blocker_candidates", []) if item]
    inherited = next((divergence_map[item] for item in upstream if item in divergence_map), None)
    divergence = direct or inherited
    if divergence is None:
        return summary

    if direct is not None:
        reason = f"主控制面与 {divergence['slot_id']} 工作树账本不一致：{divergence['summary_zh']}"
    else:
        blocker_id = str(inherited.get("candidate_id") or upstream[0])
        reason = f"上游候选 {blocker_id} 存在账本分叉：{inherited['summary_zh']}。先修复主控制面，再判断当前候选。"
    summary["operator_reason"] = reason
    summary["copy_instruction"] = "先修复主控制面与工作树台账分叉，再继续判断、续接或接单。"
    summary["copy_reason"] = reason
    summary["ledger_divergence"] = divergence
    return summary


def _decorate_candidate_payload(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    candidate = _candidate_lookup(root, payload.get("candidate_id", ""))
    if candidate:
        payload.update(_candidate_summary(candidate))
    else:
        payload["title_zh"] = _translate_candidate_title(payload.get("title"))
        payload["status_zh"] = _status_label_zh(payload.get("status"))
        payload["stage_zh"] = _stage_label_zh(payload.get("stage"))
        payload["candidate_intent_zh"] = _candidate_intent_zh(payload.get("candidate_intent"))
        payload["root_kind_zh"] = _root_kind_zh(payload.get("root_kind"))
    payload["blocking_reason_labels"] = _blocking_reason_labels(payload.get("blocking_reason_codes", []))
    payload.setdefault("operator_reason", _candidate_operator_reason(payload))
    payload.setdefault("copy_instruction", _candidate_copy_instruction(payload))
    payload.setdefault("copy_reason", _candidate_copy_reason(payload))
    divergence_map = {
        str(item.get("candidate_id")): item
        for item in _ledger_divergences(root)
        if item.get("candidate_id")
    }
    return _apply_divergence_to_candidate(payload, divergence_map)


def _decorate_claim_payload(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    selected_candidate_id = payload.get("selected_candidate_id")
    if selected_candidate_id:
        candidate = _candidate_lookup(root, selected_candidate_id)
        if candidate:
            payload["selected_candidate_title"] = candidate.get("title")
            payload["selected_candidate_title_zh"] = _translate_candidate_title(candidate.get("title"))
    safe_candidates = []
    for item in payload.get("safe_candidates", []):
        candidate = _candidate_lookup(root, item.get("candidate_id", ""))
        decorated = dict(item)
        if candidate:
            decorated.update(
                {
                    "title": candidate.get("title"),
                    "title_zh": _translate_candidate_title(candidate.get("title")),
                    "status": candidate.get("status"),
                    "status_zh": _status_label_zh(candidate.get("status")),
                }
            )
        safe_candidates.append(decorated)
    payload["safe_candidates"] = safe_candidates
    return payload


def _decorate_release_chain_payload(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    candidate = _candidate_lookup(root, payload.get("candidate_id", ""))
    if candidate:
        payload["title"] = candidate.get("title")
        payload["title_zh"] = _translate_candidate_title(candidate.get("title"))
        payload["status"] = candidate.get("status")
        payload["status_zh"] = _status_label_zh(candidate.get("status"))
    downstream_chain = []
    for item in payload.get("downstream_chain", []):
        downstream_candidate = _candidate_lookup(root, item.get("candidate_id", ""))
        decorated = dict(item)
        if downstream_candidate:
            decorated.update(
                {
                    "title": downstream_candidate.get("title"),
                    "title_zh": _translate_candidate_title(downstream_candidate.get("title")),
                    "status_zh": _status_label_zh(downstream_candidate.get("status")),
                }
            )
        downstream_chain.append(decorated)
    payload["downstream_chain"] = downstream_chain
    return payload


def _review_pool_payload() -> dict[str, Any]:
    root = _repo_root()
    payload = review_pool(root)
    divergences = _ledger_divergences(root)
    payload["ledger_divergence_count"] = len(divergences)
    payload["ledger_divergences"] = divergences
    if divergences:
        issues = list(payload.get("issues") or [])
        issues.append(f"检测到 {len(divergences)} 条主控制面与工作树账本分叉。")
        payload["issues"] = issues
        if payload.get("status") == "healthy":
            payload["status"] = "degraded"
    payload["status_zh"] = _status_label_zh(payload.get("status"))
    return payload


def _cached_pool_payload() -> dict[str, Any]:
    root = _repo_root()
    summary = load_yaml(root / SUMMARY_FILE) if (root / SUMMARY_FILE).exists() else {}
    index = _load_candidate_index(root)
    candidates = index.get("candidates", [])
    divergences = _ledger_divergences(root)
    divergence_map = {
        str(item.get("candidate_id")): item
        for item in divergences
        if item.get("candidate_id")
    }
    visible_candidates = [
        _apply_divergence_to_candidate(_candidate_summary(candidate), divergence_map)
        for candidate in candidates[:12]
    ]
    summary["generated_at"] = summary.get("generated_at") or index.get("generated_at")
    summary["ledger_divergence_count"] = len(divergences)
    return {
        "summary": summary,
        "ledger_divergences": divergences,
        "fresh_claimable": [candidate["candidate_id"] for candidate in candidates if candidate.get("fresh_claimable")],
        "takeover_claimable": [candidate["candidate_id"] for candidate in candidates if candidate.get("takeover_claimable")],
        "visible_candidates": visible_candidates,
        "top_waiting": [candidate for candidate in visible_candidates if candidate.get("status") == "waiting"][:10],
        "top_candidate": None if not visible_candidates else visible_candidates[0],
    }


def _snapshot_payload() -> dict[str, Any]:
    root = _repo_root()
    return {
        "pool": _cached_pool_payload(),
        "claim_decision": explain_claim_decision(root),
        "review": _review_pool_payload(),
    }


def _render_index_html() -> str:
    return (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{PAGE_TITLE}</title>"
        f"{_render_style_block()}</head><body>{_render_shell_html()}{_render_script_block()}</body></html>"
    )


def _render_style_block() -> str:
    return """<style>
    :root {
      color-scheme: light;
      --app-width: min(1920px, calc(100vw - 24px));
      --app-height: min(1240px, calc(100svh - 24px));
      --ink: #172033;
      --ink-soft: #5a6780;
      --panel: rgba(255,255,255,0.72);
      --line: rgba(115,133,171,0.2);
      --shadow: 0 28px 60px rgba(35,52,86,0.16);
      --radius-xl: 30px;
      --radius-lg: 24px;
      --radius-md: 18px;
      --radius-sm: 14px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100svh;
      overflow: hidden;
      font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(129,165,255,0.36), transparent 34%),
        radial-gradient(circle at 82% 12%, rgba(108,216,208,0.22), transparent 26%),
        linear-gradient(180deg, #edf2f7 0%, #d9e5f1 100%);
    }
    .shell {
      width: var(--app-width);
      min-height: var(--app-height);
      max-height: calc(100svh - 24px);
      margin: 12px auto;
      padding: 14px;
      display: grid;
      grid-template-rows: auto auto auto minmax(0, 1fr);
      gap: 14px;
      border-radius: var(--radius-xl);
      background: rgba(255,255,255,0.28);
      border: 1px solid rgba(255,255,255,0.38);
      box-shadow: var(--shadow);
      backdrop-filter: blur(20px);
    }
    .surface {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      box-shadow: 0 14px 28px rgba(53,69,103,0.08);
      backdrop-filter: blur(16px);
    }
    .hero {
      padding: 12px 18px;
      display: flex;
      align-items: center;
      background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(241,245,251,0.74));
    }
    h1 {
      margin: 0;
      font-size: clamp(24px, 2.4vw, 32px);
      line-height: 1.1;
    }
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 12px;
      background: rgba(255,255,255,0.6);
    }
    .status-banner {
      display: none;
      align-items: center;
      gap: 10px;
      padding: 12px 16px;
      color: var(--ink);
      background: rgba(255,255,255,0.72);
    }
    .status-banner.visible {
      display: flex;
    }
    .status-banner.warning {
      border: 1px solid rgba(185, 96, 28, 0.24);
      background: linear-gradient(135deg, rgba(255,244,227,0.95), rgba(255,238,213,0.86));
    }
    .status-banner strong {
      font-size: 14px;
    }
    .status-banner span {
      color: var(--ink-soft);
      font-size: 13px;
    }
    button {
      appearance: none;
      border: 0;
      border-radius: var(--radius-sm);
      padding: 11px 14px;
      cursor: pointer;
      font: inherit;
      color: #ffffff;
      background: linear-gradient(135deg, #4f6df5, #5e8bff);
      box-shadow: 0 12px 22px rgba(79,109,245,0.22);
      transition: transform 140ms ease, box-shadow 140ms ease;
    }
    button:hover { transform: translateY(-1px); }
    button.secondary {
      color: var(--ink);
      background: rgba(255,255,255,0.8);
      border: 1px solid rgba(115,133,171,0.18);
      box-shadow: none;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .metric-card {
      padding: 14px 16px;
      display: grid;
      gap: 4px;
    }
    .metric-card .label {
      color: var(--ink-soft);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .metric-card .label.zh {
      letter-spacing: 0.02em;
      text-transform: none;
      font-size: 13px;
    }
    .metric {
      font-size: 32px;
      font-weight: 700;
      line-height: 1;
    }
    .workspace {
      display: grid;
      grid-template-columns: minmax(330px, 0.82fr) minmax(520px, 1.14fr) minmax(340px, 0.86fr);
      gap: 14px;
      min-height: 0;
    }
    .focus-panel,
    .ops-panel {
      min-width: 0;
    }
    .panel {
      min-height: 0;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .panel-header {
      padding: 16px 18px 12px;
      border-bottom: 1px solid rgba(115,133,171,0.14);
    }
    .panel-title {
      font-size: 18px;
      font-weight: 700;
    }
    .panel-subtitle {
      margin-top: 4px;
      color: var(--ink-soft);
      font-size: 13px;
    }
    .panel-meta {
      margin-top: 6px;
      color: var(--ink-soft);
      font-size: 12px;
    }
    .candidate-list {
      padding: 10px 12px 14px;
      display: grid;
      gap: 10px;
      overflow: auto;
    }
    .candidate-row {
      width: 100%;
      padding: 13px 14px;
      display: grid;
      gap: 10px;
      text-align: left;
      color: var(--ink);
      background: rgba(255,255,255,0.72);
      border: 1px solid rgba(115,133,171,0.16);
      border-radius: 18px;
      box-shadow: none;
      cursor: pointer;
      transition: border-color 140ms ease, background 140ms ease, transform 140ms ease;
    }
    .candidate-row:hover {
      transform: translateY(-1px);
      border-color: rgba(79,109,245,0.28);
      background: rgba(255,255,255,0.88);
    }
    .candidate-row.active {
      border-color: rgba(79,109,245,0.44);
      background: linear-gradient(180deg, rgba(246,249,255,0.98), rgba(255,255,255,0.82));
      box-shadow: inset 0 0 0 1px rgba(79,109,245,0.08);
    }
    .candidate-row:focus-visible {
      outline: 2px solid rgba(79,109,245,0.5);
      outline-offset: 2px;
    }
    .candidate-top {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: flex-start;
    }
    .candidate-main {
      min-width: 0;
      flex: 1;
    }
    .candidate-side {
      display: grid;
      gap: 8px;
      justify-items: end;
      flex-shrink: 0;
    }
    .candidate-title {
      font-size: 15px;
      font-weight: 700;
      line-height: 1.3;
    }
    .candidate-sub {
      margin-top: 4px;
      color: var(--ink-soft);
      font-size: 12px;
      line-height: 1.45;
      word-break: break-word;
    }
    .candidate-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .candidate-note {
      color: var(--ink-soft);
      font-size: 12px;
      line-height: 1.55;
      margin-top: -2px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(79,109,245,0.08);
      color: var(--ink-soft);
      font-size: 12px;
    }
    .status-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 78px;
      padding: 7px 11px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      color: #ffffff;
      background: linear-gradient(135deg, #8796ad, #6e7d93);
    }
    .status-ready { background: linear-gradient(135deg, #1f8f64, #3bab7f); }
    .status-resumable { background: linear-gradient(135deg, #4965f1, #6f88ff); }
    .status-waiting { background: linear-gradient(135deg, #b97819, #d49a43); }
    .status-blocked { background: linear-gradient(135deg, #bf4758, #d86f7e); }
    .status-degraded { background: linear-gradient(135deg, #c0842c, #d8a551); }
    .status-stale { background: linear-gradient(135deg, #7e5bd6, #9a74f0); }
    .copy-shortcut {
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(115,133,171,0.18);
      background: rgba(255,255,255,0.86);
      color: var(--ink-soft);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.01em;
      box-shadow: none;
    }
    .copy-shortcut:hover {
      transform: none;
      color: var(--ink);
      border-color: rgba(79,109,245,0.24);
    }
    .quick-tools {
      padding: 12px 18px 16px;
      display: grid;
      gap: 10px;
      border-bottom: 1px solid rgba(115,133,171,0.14);
      background: linear-gradient(180deg, rgba(248,250,253,0.88), rgba(255,255,255,0.7));
    }
    .tool-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
    }
    .tool-actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    label {
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      color: var(--ink-soft);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    input {
      width: 100%;
      border: 1px solid rgba(115,133,171,0.18);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
      font: inherit;
      color: var(--ink);
      background: rgba(255,255,255,0.86);
    }
    .detail-body {
      min-height: 0;
      padding: 14px 18px 18px;
      overflow: auto;
      display: grid;
      gap: 12px;
      align-content: start;
    }
    .detail-card {
      padding: 13px 14px;
      border-radius: 18px;
      background: rgba(255,255,255,0.72);
      border: 1px solid rgba(115,133,171,0.12);
    }
    .detail-key {
      color: var(--ink-soft);
      font-size: 12px;
      margin-bottom: 6px;
      letter-spacing: 0.03em;
    }
    .detail-value {
      font-size: 14px;
      line-height: 1.55;
      word-break: break-word;
    }
    .raw-title {
      font-size: 12px;
      color: var(--ink-soft);
      letter-spacing: 0.06em;
      text-transform: none;
      margin-bottom: 8px;
    }
    .raw-block {
      border-radius: 18px;
      border: 1px solid rgba(115,133,171,0.14);
      background: rgba(246,249,252,0.92);
      overflow: hidden;
    }
    .raw-block summary {
      list-style: none;
      cursor: pointer;
      padding: 12px 14px;
      color: var(--ink-soft);
      font-size: 12px;
      letter-spacing: 0.04em;
    }
    .raw-block summary::-webkit-details-marker {
      display: none;
    }
    .raw-block[open] summary {
      border-bottom: 1px solid rgba(115,133,171,0.14);
    }
    pre {
      margin: 0;
      padding: 14px;
      border-radius: 18px;
      background: rgba(21,34,57,0.92);
      color: #e8f0ff;
      font-size: 12px;
      line-height: 1.55;
      white-space: pre-wrap;
      word-break: break-word;
      overflow: auto;
    }
    code {
      padding: 2px 6px;
      border-radius: 8px;
      background: rgba(79,109,245,0.08);
      font-family: "Consolas", "SFMono-Regular", monospace;
      font-size: 12px;
    }
    .log-panel {
      display: grid;
      gap: 10px;
    }
    .ops-body {
      min-height: 0;
      padding: 14px 18px 18px;
      overflow: auto;
      display: grid;
      gap: 12px;
      align-content: start;
    }
    .summary-grid {
      display: grid;
      gap: 10px;
    }
    .summary-card {
      padding: 13px 14px;
      border-radius: 18px;
      background: rgba(255,255,255,0.72);
      border: 1px solid rgba(115,133,171,0.12);
    }
    .summary-card .detail-key {
      margin-bottom: 4px;
    }
    .section-kicker {
      font-size: 12px;
      color: var(--ink-soft);
      letter-spacing: 0.04em;
      margin-bottom: 2px;
    }
    .feedback-toast {
      position: fixed;
      top: 18px;
      right: 18px;
      z-index: 999;
      max-width: min(420px, calc(100vw - 32px));
      padding: 10px 14px;
      border-radius: 16px;
      background: rgba(24,36,59,0.92);
      color: #eef4ff;
      font-size: 13px;
      line-height: 1.45;
      box-shadow: 0 20px 42px rgba(21,34,57,0.24);
      opacity: 0;
      pointer-events: none;
      transform: translateY(-10px);
      transition: opacity 140ms ease, transform 140ms ease;
    }
    .feedback-toast.visible {
      opacity: 1;
      transform: translateY(0);
    }
    .feedback-toast.pending { background: rgba(49,71,120,0.94); }
    .feedback-toast.success { background: rgba(22,111,79,0.94); }
    .feedback-toast.error { background: rgba(153,45,61,0.96); }
    .placeholder {
      display: grid;
      place-items: center;
      min-height: 160px;
      border-radius: 20px;
      color: var(--ink-soft);
      background: rgba(255,255,255,0.48);
      border: 1px dashed rgba(115,133,171,0.22);
      text-align: center;
      padding: 20px;
      line-height: 1.6;
    }
    @media (max-width: 1480px) {
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .workspace { grid-template-columns: minmax(320px, 0.92fr) minmax(0, 1.08fr); }
      .ops-panel { grid-column: 1 / -1; }
    }
    @media (max-width: 1080px) {
      body { overflow: auto; }
      .shell { width: min(100vw - 16px, 100%); max-height: none; }
      .workspace { grid-template-columns: 1fr; }
    }
    @media (max-width: 640px) {
      .metrics { grid-template-columns: 1fr; }
      .tool-row { grid-template-columns: 1fr; }
      .tool-actions { grid-template-columns: 1fr; }
    }
    </style>"""


def _render_shell_html() -> str:
    return f"""<main class="shell">
    <div id="feedback_toast" class="feedback-toast" aria-live="polite"></div>
    <section class="surface hero">
      <h1>{PAGE_TITLE}</h1>
    </section>

    <section class="surface toolbar">
      <button type="button" onclick="runAction('compile-roadmap-candidates', this)">编译候选池</button>
      <button type="button" onclick="runAction('refresh-roadmap-candidates', this)">刷新候选池</button>
      <button type="button" onclick="runAction('close-ready-execution-tasks', this)">关闭已就绪执行任务</button>
      <button type="button" onclick="runAction('continue-roadmap', this)">继续路线图</button>
      <button type="button" class="secondary" onclick="loadAll(this)">重载页面快照</button>
      <button type="button" class="secondary" onclick="loadClaimDecision(this)">解释认领决策</button>
      <button type="button" class="secondary" onclick="loadReview(this)">复核候选池</button>
    </section>

    <section id="divergence_banner" class="surface status-banner" aria-live="polite"></section>

    <section class="metrics">
      <article class="surface metric-card">
        <div class="label zh">候选任务总数</div>
        <div class="metric" id="candidate_count">-</div>
      </article>
      <article class="surface metric-card">
        <div class="label zh">新鲜可认领</div>
        <div class="metric" id="fresh_claimable_count">-</div>
      </article>
      <article class="surface metric-card">
        <div class="label zh">接管可认领</div>
        <div class="metric" id="takeover_claimable_count">-</div>
      </article>
      <article class="surface metric-card">
        <div class="label zh">并行缺口</div>
        <div class="metric" id="parallelism_deficit">-</div>
      </article>
    </section>

    <section class="workspace">
      <article class="surface panel">
        <div class="panel-header">
          <div class="panel-title">候选池任务</div>
        </div>
        <div class="candidate-list" id="candidate_rows">
          <div class="placeholder">正在加载候选池快照…</div>
        </div>
      </article>

      <article class="surface panel focus-panel">
        <div class="panel-header">
          <div class="panel-title" id="detail_title">操作者焦点</div>
        </div>
        <div class="quick-tools">
          <div>
            <label for="candidate_id">候选任务解释</label>
            <div class="tool-row">
              <input id="candidate_id" placeholder="例如：stage1-core-contract">
              <button type="button" class="secondary" onclick="loadCandidate(this)">解释候选任务</button>
            </div>
          </div>
          <div>
            <label for="release_candidate_id">释放链解释</label>
            <div class="tool-row">
              <input id="release_candidate_id" placeholder="例如：stage1-core-contract">
              <button type="button" class="secondary" onclick="loadReleaseChain(this)">解释释放链</button>
            </div>
          </div>
          <div class="tool-actions">
            <button type="button" class="secondary" onclick="loadClaimDecision(this)">解释认领决策</button>
            <button type="button" class="secondary" onclick="loadReview(this)">复核候选池</button>
          </div>
        </div>
        <div class="detail-body" id="detail_body">
          <div class="placeholder">默认会自动展开头号候选任务。你也可以点左侧候选项，或在这里输入 candidate_id 聚焦指定对象。</div>
        </div>
      </article>

      <article class="surface panel ops-panel">
        <div class="panel-header">
          <div class="panel-title">控制台总览</div>
          <div class="panel-meta" id="refresh_meta">最后刷新：-</div>
        </div>
        <div class="ops-body">
          <div class="summary-grid" id="snapshot_body">
            <div class="placeholder">正在建立控制台快照…</div>
          </div>
          <div class="log-panel">
            <div>
              <div class="section-kicker">最近动作</div>
              <div class="panel-subtitle">页面只调用现有 control-plane 命令，不在前端复写调度逻辑。</div>
            </div>
            <pre id="action_output">尚未执行页面动作。</pre>
          </div>
        </div>
      </article>
    </section>
  </main>"""


def _render_script_block() -> str:
    action_labels = json.dumps(ACTION_LABELS_ZH, ensure_ascii=False)
    return f"""<script>
    const ACTION_LABELS = {action_labels};
    const AUTO_REFRESH_FOREGROUND_MS = {AUTO_REFRESH_FOREGROUND_SECONDS * 1000};
    const AUTO_REFRESH_BACKGROUND_MS = {AUTO_REFRESH_BACKGROUND_SECONDS * 1000};
    let currentCandidateId = new URL(window.location.href).searchParams.get('candidate_id') || '';
    let currentDetailMode = 'candidate';
    let feedbackTimer = null;
    let autoRefreshTimer = null;
    let lastRefreshAt = null;
    let focusInitialized = false;
    window.__candidateRows = {{}};
    window.__lastCopiedShortcut = '';
    window.__lastFeedback = null;
    window.__lastPoolPayload = null;

    function escapeHtml(value) {{
      return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }}

    async function fetchJson(path, options) {{
      const res = await fetch(path, options);
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.error || JSON.stringify(payload));
      return payload;
    }}

    function metric(id, value) {{
      document.getElementById(id).textContent = value ?? '-';
    }}

    function statusClass(status) {{
      return `status-${{(status || '').toLowerCase()}}`;
    }}

    function formatTimestamp(value) {{
      if (!value) return '-';
      const timestamp = value instanceof Date ? value : new Date(value);
      if (Number.isNaN(timestamp.getTime())) {{
        return String(value);
      }}
      return timestamp.toLocaleString('zh-CN', {{
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }});
    }}

    function currentRefreshIntervalMs() {{
      return document.hidden ? AUTO_REFRESH_BACKGROUND_MS : AUTO_REFRESH_FOREGROUND_MS;
    }}

    function scheduleAutoRefresh() {{
      if (autoRefreshTimer) {{
        window.clearTimeout(autoRefreshTimer);
      }}
      autoRefreshTimer = window.setTimeout(() => {{
        loadAll(null, true).catch(() => {{}});
      }}, currentRefreshIntervalMs());
    }}

    function showFeedback(kind, message, persist = false) {{
      const toast = document.getElementById('feedback_toast');
      if (!toast) return;
      toast.textContent = message;
      toast.className = `feedback-toast ${{kind}} visible`;
      window.__lastFeedback = {{ kind, message }};
      if (feedbackTimer) {{
        window.clearTimeout(feedbackTimer);
        feedbackTimer = null;
      }}
      if (!persist) {{
        feedbackTimer = window.setTimeout(() => {{
          toast.className = 'feedback-toast';
        }}, 1800);
      }}
    }}

    function setCandidateQuery(candidateId) {{
      const url = new URL(window.location.href);
      if (candidateId) {{
        url.searchParams.set('candidate_id', candidateId);
      }} else {{
        url.searchParams.delete('candidate_id');
      }}
      window.history.replaceState({{}}, '', url);
    }}

    function highlightCandidateRow(candidateId) {{
      let active = null;
      document.querySelectorAll('.candidate-row').forEach((row) => {{
        const matched = !!candidateId && row.dataset.candidateId === candidateId;
        row.classList.toggle('active', matched);
        if (matched) {{
          active = row;
        }}
      }});
      active?.scrollIntoView({{ block: 'nearest' }});
    }}

    function withTemporaryButtonLabel(button, label, duration = 1200) {{
      if (!button) return;
      const original = button.dataset.originalLabel || button.textContent;
      button.dataset.originalLabel = original;
      button.textContent = label;
      window.setTimeout(() => {{
        button.textContent = original;
      }}, duration);
    }}

    function setBusyState(button, busy, pendingLabel = '处理中…') {{
      if (!button || !(button instanceof HTMLButtonElement)) return;
      if (busy) {{
        if (!button.dataset.originalLabel) {{
          button.dataset.originalLabel = button.textContent;
        }}
        button.disabled = true;
        button.textContent = pendingLabel;
      }} else {{
        button.disabled = false;
        if (button.dataset.originalLabel) {{
          button.textContent = button.dataset.originalLabel;
        }}
      }}
    }}

    async function writeClipboardText(text) {{
      try {{
        await navigator.clipboard.writeText(text);
        return true;
      }} catch (_error) {{
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', 'readonly');
        textarea.style.position = 'fixed';
        textarea.style.top = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        const copied = document.execCommand('copy');
        document.body.removeChild(textarea);
        return copied;
      }}
    }}

    function buildCandidateShortcut(row) {{
      const lines = [
        row.copy_instruction || '当前任务尚未解锁，先检查阻塞原因；解除后再回任务池接单。',
      ];
      if (row.copy_reason) {{
        lines.push(`当前原因：${{row.copy_reason}}`);
      }}
      lines.push('当前任务如下：');
      lines.push(row.title_zh || row.candidate_id);
      lines.push(`${{row.title || row.candidate_id}} · ${{row.candidate_id}}`);
      return lines.join('\\n');
    }}

    async function copyCandidateShortcut(event, candidateId, button) {{
      event.preventDefault();
      event.stopPropagation();
      const row = window.__candidateRows[candidateId];
      if (!row) {{
        showFeedback('error', `复制失败：未找到候选 ${{candidateId}}`, true);
        return;
      }}
      const shortcut = buildCandidateShortcut(row);
      window.__lastCopiedShortcut = shortcut;
      const copied = await writeClipboardText(shortcut);
      if (!copied) {{
        showFeedback('error', `复制失败：${{candidateId}}`, true);
        return;
      }}
      withTemporaryButtonLabel(button, '已复制');
      showFeedback('success', `已复制：${{row.title_zh || candidateId}}`, false);
    }}

    function handleCandidateRowKey(event, candidateId, element) {{
      if (event.key === 'Enter' || event.key === ' ') {{
        event.preventDefault();
        loadCandidateById(candidateId, element);
      }}
    }}

    function renderJsonBlock(payload) {{
      return `<details class="raw-block"><summary>展开原始载荷</summary><pre>${{escapeHtml(JSON.stringify(payload, null, 2))}}</pre></details>`;
    }}

    function renderKeyValueCards(items) {{
      return items.map(item => `<div class="detail-card"><div class="detail-key">${{escapeHtml(item.label)}}</div><div class="detail-value">${{escapeHtml(item.value || '无')}}</div></div>`).join('');
    }}

    function renderRuntimeSignals(pool) {{
      window.__lastPoolPayload = pool;
      lastRefreshAt = new Date();
      const summary = pool.summary || {{}};
      const divergences = pool.ledger_divergences || [];
      const refreshMeta = document.getElementById('refresh_meta');
      if (refreshMeta) {{
        const parts = [
          `最后刷新：${{formatTimestamp(lastRefreshAt)}}`,
          `候选快照：${{formatTimestamp(summary.generated_at)}}`,
          `自动刷新：${{document.hidden ? {AUTO_REFRESH_BACKGROUND_SECONDS} : {AUTO_REFRESH_FOREGROUND_SECONDS}}} 秒`,
        ];
        if (divergences.length) {{
          parts.push(`账本分叉：${{divergences.length}}`);
        }}
        refreshMeta.textContent = parts.join(' · ');
      }}
      const banner = document.getElementById('divergence_banner');
      if (!banner) return;
      if (!divergences.length) {{
        banner.className = 'surface status-banner';
        banner.innerHTML = '';
        return;
      }}
      const preview = divergences
        .slice(0, 2)
        .map(item => `${{escapeHtml(item.slot_id || '-')}}：${{escapeHtml(item.summary_zh || '状态不一致')}}`)
        .join('；');
      const extra = divergences.length > 2 ? `；另有 ${{divergences.length - 2}} 条` : '';
      banner.className = 'surface status-banner warning visible';
      banner.innerHTML = `<strong>检测到 ${{divergences.length}} 条账本分叉</strong><span>先修复主控制面与工作树状态，再判断接单、续接和自动释放。${{preview ? ` ${{preview}}${{extra}}` : ''}}</span>`;
    }}

    function renderPool(pool) {{
      const summary = pool.summary || {{}};
      metric('candidate_count', summary.candidate_count);
      metric('fresh_claimable_count', summary.fresh_claimable_count);
      metric('takeover_claimable_count', summary.takeover_claimable_count);
      metric('parallelism_deficit', summary.parallelism_deficit);
      window.__candidateRows = Object.fromEntries((pool.visible_candidates || []).map(row => [row.candidate_id, row]));
      const rows = (pool.visible_candidates || []).map(row => `
        <div
          class="candidate-row${{currentCandidateId === row.candidate_id ? ' active' : ''}}"
          data-candidate-id="${{escapeHtml(row.candidate_id)}}"
          role="button"
          tabindex="0"
          onclick="loadCandidateById('${{escapeHtml(row.candidate_id)}}', this)"
          onkeydown="handleCandidateRowKey(event, '${{escapeHtml(row.candidate_id)}}', this)"
        >
          <div class="candidate-top">
            <div class="candidate-main">
              <div class="candidate-title">${{escapeHtml(row.title_zh)}}</div>
              <div class="candidate-sub">${{escapeHtml(row.title)}} · <code>${{escapeHtml(row.candidate_id)}}</code></div>
            </div>
            <div class="candidate-side">
              <span class="status-pill ${{statusClass(row.status)}}">${{escapeHtml(row.status_zh || row.status || '-')}}</span>
              <button
                type="button"
                class="copy-shortcut"
                onclick="copyCandidateShortcut(event, '${{escapeHtml(row.candidate_id)}}', this)"
              >复制任务</button>
            </div>
          </div>
          <div class="candidate-meta">
            <span class="pill">${{escapeHtml(row.stage_zh || row.stage || '-')}}</span>
            <span class="pill">${{escapeHtml(row.candidate_intent_zh || row.candidate_intent || '-')}}</span>
            <span class="pill">解锁数 ${{escapeHtml(row.unlock_count ?? '-')}}</span>
            ${{(row.blocking_reason_labels || []).slice(0, 2).map(label => `<span class="pill">${{escapeHtml(label)}}</span>`).join('')}}
          </div>
          <div class="candidate-note">${{escapeHtml(row.operator_reason || '当前暂无额外说明。')}}</div>
        </div>
      `).join('');
      document.getElementById('candidate_rows').innerHTML = rows || '<div class="placeholder">没有可展示候选。</div>';
      highlightCandidateRow(currentCandidateId);
    }}

    function renderPoolSnapshot(pool) {{
      const summary = pool.summary || {{}};
      const topCandidate = pool.top_candidate;
      document.getElementById('snapshot_body').innerHTML = renderKeyValueCards([
        {{ label: '控制面根目录', value: summary.control_plane_root || 'D:/Base One/Base-two/AX9' }},
        {{ label: '候选任务总数', value: String(summary.candidate_count ?? '-') }},
        {{ label: '活动认领数', value: String(summary.active_claim_count ?? '-') }},
        {{ label: '新鲜可认领', value: String(summary.fresh_claimable_count ?? '-') }},
        {{ label: '接管可认领', value: String(summary.takeover_claimable_count ?? '-') }},
        {{ label: '并行缺口', value: String(summary.parallelism_deficit ?? '-') }},
        {{ label: '账本分叉', value: String(summary.ledger_divergence_count ?? 0) }},
        {{ label: '候选快照时间', value: summary.generated_at || '-' }},
        {{ label: '头号候选任务', value: topCandidate ? `${{topCandidate.title_zh}} / ${{topCandidate.title}}` : '无' }},
        {{ label: '头号候选英文标识', value: topCandidate ? topCandidate.candidate_id : '无' }},
      ]) + renderJsonBlock(pool);
    }}

    function renderCandidateDetail(payload) {{
      currentDetailMode = 'candidate';
      focusInitialized = true;
      document.getElementById('detail_title').textContent = '候选任务解释';
      document.getElementById('detail_body').innerHTML = renderKeyValueCards([
        {{ label: '候选任务', value: `${{payload.title_zh || payload.title || payload.candidate_id}} / ${{payload.title || payload.candidate_id}}` }},
        {{ label: '英文标识', value: payload.candidate_id }},
        {{ label: '当前状态', value: payload.status_zh || payload.status || '-' }},
        {{ label: '处理建议', value: payload.copy_instruction || '-' }},
        {{ label: '真实原因', value: payload.operator_reason || '当前暂无额外说明。' }},
        {{ label: '所在阶段', value: payload.stage_zh || payload.stage || '-' }},
        {{ label: '模块标识', value: payload.module_id || '-' }},
        {{ label: '候选意图', value: payload.candidate_intent_zh || payload.candidate_intent || '-' }},
        {{ label: '主根类型', value: payload.root_kind_zh || payload.root_kind || '-' }},
        {{ label: '是否可认领', value: payload.claimable ? '是' : '否' }},
        {{ label: '接管模式', value: payload.takeover_mode || '-' }},
        {{ label: '阻塞原因', value: (payload.blocking_reason_labels || payload.blocking_reason_text || []).join('；') || '无' }},
        {{ label: '上游阻塞候选', value: (payload.upstream_blocker_candidates || []).join('、') || '无' }},
      ]) + renderJsonBlock(payload);
    }}

    function renderClaimDecision(payload) {{
      currentDetailMode = 'claim';
      focusInitialized = true;
      document.getElementById('detail_title').textContent = '认领决策解释';
      const selected = payload.selected_candidate_id
        ? `${{payload.selected_candidate_title_zh || payload.selected_candidate_id}} / ${{payload.selected_candidate_title || payload.selected_candidate_id}}`
        : '当前没有可安全认领候选';
      const safeCandidates = (payload.safe_candidates || []).map(item => item.title_zh ? `${{item.title_zh}} (${{item.candidate_id}})` : item.candidate_id).join('、') || '无';
      const blocked = (payload.blocked_candidates || []).map(item => typeof item === 'string' ? item : JSON.stringify(item, null, 2)).join('\\n') || '无';
      document.getElementById('detail_body').innerHTML = renderKeyValueCards([
        {{ label: '当前选中候选', value: selected }},
        {{ label: '选中接管模式', value: payload.selected_takeover_mode || '无' }},
        {{ label: '安全候选集合', value: safeCandidates }},
        {{ label: '阻塞候选摘要', value: blocked }},
      ]) + renderJsonBlock(payload);
    }}

    function renderReleaseChain(payload) {{
      currentDetailMode = 'release';
      focusInitialized = true;
      document.getElementById('detail_title').textContent = '释放链解释';
      const chain = (payload.downstream_chain || []).map(item => `${{item.title_zh || item.candidate_id}} / ${{item.candidate_id}} (${{item.status_zh || item.status || '-'}})`).join(' → ') || '无';
      document.getElementById('detail_body').innerHTML = renderKeyValueCards([
        {{ label: '候选任务', value: `${{payload.title_zh || payload.candidate_id || '-'}} / ${{payload.title || payload.candidate_id || '-'}}` }},
        {{ label: '英文标识', value: payload.candidate_id || '-' }},
        {{ label: '当前状态', value: payload.status_zh || payload.status || '-' }},
        {{ label: '依赖项', value: (payload.depends_on || []).join('、') || '无' }},
        {{ label: '释放链', value: chain }},
      ]) + renderJsonBlock(payload);
    }}

    function renderReview(payload) {{
      const staleClaims = (payload.stale_claims || []).map(item => `${{item.candidate_id || '-'}} -> ${{item.formal_task_id || '-'}}`).join('；') || '无';
      const incompleteTasks = (payload.incomplete_tasks || []).map(item => `${{item.task_id || '-'}} (${{item.status || '-'}})`).join('；') || '无';
      const divergenceSummary = (payload.ledger_divergences || [])
        .map(item => `${{item.slot_id || '-'}} / ${{item.candidate_id || item.task_id || '-'}} / ${{item.summary_zh || '状态不一致'}}`)
        .join('；') || '无';
      currentDetailMode = 'review';
      focusInitialized = true;
      document.getElementById('detail_title').textContent = '候选池复核';
      document.getElementById('detail_body').innerHTML = renderKeyValueCards([
        {{ label: '控制面状态', value: payload.status_zh || payload.status || '-' }},
        {{ label: '正式主根数量', value: String(payload.formal_root_count ?? '-') }},
        {{ label: '预览主根数量', value: String(payload.preview_root_count ?? '-') }},
        {{ label: '遗留兼容候选', value: String(payload.legacy_candidate_count ?? '-') }},
        {{ label: '账本分叉数量', value: String(payload.ledger_divergence_count ?? 0) }},
        {{ label: '账本分叉详情', value: divergenceSummary }},
        {{ label: '待人工续接/清理', value: staleClaims }},
        {{ label: '未完正式任务', value: incompleteTasks }},
        {{ label: '就绪关闭执行任务', value: String(payload.closeout_ready_execution_count ?? '-') }},
        {{ label: '待阻塞执行任务', value: String(payload.closeout_blocked_execution_count ?? '-') }},
        {{ label: '问题摘要', value: (payload.issues || []).join('；') || '无' }},
      ]) + renderJsonBlock(payload);
    }}

    function renderActionOutput(action, payload) {{
      const label = ACTION_LABELS[action] || action;
      const stdout = payload.stdout ? `stdout:\\n${{payload.stdout}}` : 'stdout: <empty>';
      const stderr = payload.stderr ? `stderr:\\n${{payload.stderr}}` : 'stderr: <empty>';
      document.getElementById('action_output').textContent = [`动作：${{label}}`, `命令：${{(payload.argv || []).join(' ')}}`, `返回码：${{payload.returncode}}`, '', stdout, '', stderr].join('\\n');
    }}

    async function loadAll(triggerButton = null, quietError = false) {{
      if (triggerButton) {{
        setBusyState(triggerButton, true, '刷新中…');
        showFeedback('pending', '正在刷新页面快照…', true);
      }}
      try {{
        const payload = await fetchJson('/api/pool');
        renderPool(payload);
        renderRuntimeSignals(payload);
        renderPoolSnapshot(payload);
        let nextCandidateId = null;
        if (currentDetailMode === 'candidate') {{
          nextCandidateId = currentCandidateId || payload.top_candidate?.candidate_id;
        }} else if (!focusInitialized) {{
          nextCandidateId = currentCandidateId || payload.top_candidate?.candidate_id;
        }}
        if (nextCandidateId) {{
          try {{
            await loadCandidateById(nextCandidateId, null, true);
          }} catch (error) {{
            currentCandidateId = '';
            setCandidateQuery('');
            if (payload.top_candidate?.candidate_id && payload.top_candidate.candidate_id !== nextCandidateId) {{
              await loadCandidateById(payload.top_candidate.candidate_id, null, true);
            }} else {{
              document.getElementById('detail_title').textContent = '操作者焦点';
              document.getElementById('detail_body').innerHTML = `<div class="placeholder">${{escapeHtml(String(error))}}</div>`;
            }}
          }}
        }} else if (!focusInitialized) {{
          focusInitialized = true;
        }}
        if (triggerButton) {{
          showFeedback('success', '页面快照已刷新');
        }}
      }} catch (error) {{
        if (!quietError) {{
          showFeedback('error', `刷新失败：${{String(error)}}`, true);
        }}
        throw error;
      }} finally {{
        setBusyState(triggerButton, false);
        scheduleAutoRefresh();
      }}
    }}

    async function loadCandidateById(candidateId, triggerElement = null, silentFeedback = false) {{
      currentDetailMode = 'candidate';
      currentCandidateId = candidateId;
      setCandidateQuery(candidateId);
      highlightCandidateRow(candidateId);
      document.getElementById('candidate_id').value = candidateId;
      document.getElementById('release_candidate_id').value = candidateId;
      try {{
        const payload = await fetchJson(`/api/candidate?candidate_id=${{encodeURIComponent(candidateId)}}`);
        renderCandidateDetail(payload);
        highlightCandidateRow(candidateId);
        if (!silentFeedback) {{
          showFeedback('success', `已打开：${{payload.title_zh || candidateId}}`);
        }}
      }} catch (error) {{
        if (!silentFeedback) {{
          showFeedback('error', `打开失败：${{candidateId}}`, true);
        }}
        throw error;
      }}
    }}

    async function loadCandidate(triggerButton = null) {{
      const candidateId = document.getElementById('candidate_id').value.trim();
      if (!candidateId) return;
      setBusyState(triggerButton, true, '加载中…');
      showFeedback('pending', `正在加载候选：${{candidateId}}`, true);
      try {{
        await loadCandidateById(candidateId);
      }} finally {{
        setBusyState(triggerButton, false);
      }}
    }}

    async function loadReleaseChain(triggerButton = null) {{
      const candidateId = document.getElementById('release_candidate_id').value.trim();
      if (!candidateId) return;
      currentDetailMode = 'release';
      currentCandidateId = candidateId;
      setCandidateQuery(candidateId);
      highlightCandidateRow(candidateId);
      document.getElementById('candidate_id').value = candidateId;
      setBusyState(triggerButton, true, '加载中…');
      showFeedback('pending', `正在解释释放链：${{candidateId}}`, true);
      try {{
        const payload = await fetchJson(`/api/release-chain?candidate_id=${{encodeURIComponent(candidateId)}}`);
        renderReleaseChain(payload);
        showFeedback('success', `已打开释放链：${{payload.title_zh || candidateId}}`);
      }} catch (error) {{
        showFeedback('error', `释放链解释失败：${{candidateId}}`, true);
        throw error;
      }} finally {{
        setBusyState(triggerButton, false);
      }}
    }}

    async function loadClaimDecision(triggerButton = null) {{
      currentDetailMode = 'claim';
      focusInitialized = true;
      currentCandidateId = '';
      setCandidateQuery('');
      highlightCandidateRow('');
      setBusyState(triggerButton, true, '加载中…');
      showFeedback('pending', '正在解释认领决策…', true);
      try {{
        const payload = await fetchJson('/api/claim-decision');
        renderClaimDecision(payload);
        showFeedback('success', '已打开认领决策解释');
      }} catch (error) {{
        showFeedback('error', '认领决策解释失败', true);
        throw error;
      }} finally {{
        setBusyState(triggerButton, false);
      }}
    }}

    async function loadReview(triggerButton = null) {{
      currentDetailMode = 'review';
      focusInitialized = true;
      currentCandidateId = '';
      setCandidateQuery('');
      highlightCandidateRow('');
      setBusyState(triggerButton, true, '复核中…');
      showFeedback('pending', '正在复核候选池…', true);
      try {{
        const payload = await fetchJson('/api/review');
        renderReview(payload);
        showFeedback('success', '候选池复核完成');
      }} catch (error) {{
        showFeedback('error', '候选池复核失败', true);
        throw error;
      }} finally {{
        setBusyState(triggerButton, false);
      }}
    }}

    async function runAction(action, triggerButton = null) {{
      setBusyState(triggerButton, true, '执行中…');
      showFeedback('pending', `正在执行：${{ACTION_LABELS[action] || action}}`, true);
      try {{
        const payload = await fetchJson(`/api/action/${{action}}`, {{ method: 'POST' }});
        renderActionOutput(action, payload);
        if (payload.returncode === 0) {{
          showFeedback('success', `执行完成：${{ACTION_LABELS[action] || action}}`);
        }} else {{
          showFeedback('error', `执行返回非零：${{ACTION_LABELS[action] || action}}`, true);
        }}
        await loadAll();
      }} catch (error) {{
        showFeedback('error', `执行失败：${{ACTION_LABELS[action] || action}}`, true);
        throw error;
      }} finally {{
        setBusyState(triggerButton, false);
      }}
    }}

    document.addEventListener('visibilitychange', () => {{
      if (window.__lastPoolPayload) {{
        renderRuntimeSignals(window.__lastPoolPayload);
      }}
      scheduleAutoRefresh();
    }});

    loadAll().catch(error => {{
      document.getElementById('detail_title').textContent = '加载失败';
      document.getElementById('detail_body').innerHTML = `<div class="placeholder">${{escapeHtml(String(error))}}</div>`;
      showFeedback('error', `加载失败：${{String(error)}}`, true);
    }});
  </script>"""


class GovernanceConsoleHandler(BaseHTTPRequestHandler):
    def _write_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _write_empty(self, status: int = HTTPStatus.NO_CONTENT) -> None:
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            root = _repo_root()
            if parsed.path == "/favicon.ico":
                self._write_empty()
                return
            if parsed.path == "/":
                self._write_html(_render_index_html())
                return
            if parsed.path == "/api/pool":
                payload = _cached_pool_payload()
                payload["summary"]["control_plane_root"] = str(root).replace("\\", "/")
                self._write_json(payload)
                return
            if parsed.path == "/api/review":
                self._write_json(_review_pool_payload())
                return
            if parsed.path == "/api/claim-decision":
                self._write_json(_decorate_claim_payload(root, explain_claim_decision(root)))
                return
            if parsed.path == "/api/candidate":
                candidate_id = parse_qs(parsed.query).get("candidate_id", [""])[0]
                self._write_json(_decorate_candidate_payload(root, explain_candidate(root, candidate_id)))
                return
            if parsed.path == "/api/release-chain":
                candidate_id = parse_qs(parsed.query).get("candidate_id", [""])[0]
                self._write_json(_decorate_release_chain_payload(root, explain_release_chain(root, candidate_id)))
                return
            self._write_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        except GovernanceError as error:
            self._write_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as error:  # noqa: BLE001
            self._write_json({"error": f"internal error: {error}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if not parsed.path.startswith("/api/action/"):
                self._write_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            action = parsed.path.split("/api/action/", 1)[1]
            if action not in ACTION_COMMANDS:
                self._write_json({"error": f"unsupported action: {action}"}, status=HTTPStatus.BAD_REQUEST)
                return
            payload = _run_task_ops(*ACTION_COMMANDS[action])
            payload["action"] = action
            payload["action_label_zh"] = ACTION_LABELS_ZH[action]
            self._write_json(payload)
        except Exception as error:  # noqa: BLE001
            self._write_json({"error": f"internal error: {error}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def start_console(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, *, open_browser: bool = True) -> int:
    url = _console_url(host, port)
    if _port_in_use(host, port):
        if open_browser:
            if os.name == "nt":
                os.startfile(url)
            else:
                webbrowser.open(url)
        print(f"[OK] governance console already running at {url}")
        return 0

    server = ThreadingHTTPServer((host, port), GovernanceConsoleHandler)
    if open_browser:
        if os.name == "nt":
            os.startfile(url)
        else:
            webbrowser.open(url)
    print(f"[OK] governance console serving at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AX9 Governance Operator Console")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    return parser


def main() -> int:
    configure_utf8_stdio()
    args = build_parser().parse_args()
    return start_console(args.host, args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    raise SystemExit(main())
