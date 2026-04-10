from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Any

from governance_lib import (
    EXECUTION_CONTEXT_FILE,
    GovernanceError,
    actual_path,
    branch_exists,
    git,
    iso_now,
    load_task_policy,
    load_task_registry,
    load_yaml,
)
from child_execution_flow import transient_child_paths
from governance_runtime import read_roadmap
from roadmap_candidate_compiler import COMPILED_GRAPH_FILE, GRAPH_VERSION
from roadmap_scope_policy import ensure_mvp_scope_matches_business_scope


ROADMAP_BACKLOG_FILE = Path("docs/governance/ROADMAP_BACKLOG.yaml")
ROADMAP_BACKLOG_SCHEMA_FILE = Path("docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml")
CLAIMS_FILE = Path(".codex/local/roadmap_candidates/claims.yaml")
REGION_COVERAGE_REGISTRY_FILE = Path("docs/contracts/region_coverage_registry.yaml")
SOURCE_REGISTRY_FILE = Path("docs/contracts/sources_registry.yaml")

EVALUATOR_VERSION = "roadmap_scheduler_eval_v2"
COMPILED_FORMAT_VERSION = "roadmap_candidate_index_v2"

TERMINAL_STATUSES = {"done", "closed"}
INDEX_STATUS_ORDER = {
    "ready": 0,
    "resumable": 1,
    "stale": 2,
    "waiting": 3,
    "claimed": 4,
    "running": 5,
    "blocked": 6,
    "review": 7,
    "done": 8,
    "closed": 9,
}
ACTIVE_TASK_CONFLICT_STATUSES = {"doing", "review"}
OPEN_FORMAL_TASK_STATUSES = {"doing", "paused", "review", "blocked"}
CLAIM_ACTIVE_STATUSES = {"claimed", "promoted", "taken_over"}

REASON_CODES = {
    "dependency_wait",
    "expected_children_wait",
    "expected_claimable_children_wait",
    "formal_task_blocked",
    "active_claim",
    "capacity_limit",
    "out_of_mvp_scope",
    "coverage_not_registered",
    "pilot_only",
    "planned_write_path_missing",
    "write_path_overlap",
    "protected_path_conflict",
    "single_writer_root_conflict",
    "branch_conflict",
    "worktree_conflict",
    "candidate_not_claimable",
    "stale_takeover_ready",
    "stale_takeover_blocked",
}


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _now(value: str | None = None) -> datetime:
    parsed = _parse_iso(value)
    if parsed is not None:
        return parsed
    return datetime.now().astimezone()


def _normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _dedupe(values: list[str]) -> list[str]:
    ordered: list[str] = []
    for value in values:
        if value not in ordered:
            ordered.append(value)
    return ordered


def _append_reason(reason_codes: list[str], code: str) -> None:
    if code not in REASON_CODES:
        raise GovernanceError(f"unknown roadmap scheduler reason code: {code}")
    if code not in reason_codes:
        reason_codes.append(code)


def _paths_overlap(left: str, right: str) -> bool:
    left_norm = _normalize(left)
    right_norm = _normalize(right)
    if not left_norm or not right_norm:
        return False
    return left_norm == right_norm or left_norm.startswith(f"{right_norm}/") or right_norm.startswith(f"{left_norm}/")


def _any_path_overlaps(left_paths: list[str], right_paths: list[str]) -> bool:
    return any(_paths_overlap(left, right) for left in left_paths for right in right_paths)


def _candidate_task_id(candidate_id: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", candidate_id.upper()).strip("-")
    return f"TASK-RM-{token}"


def _format_template(template: str, *, candidate: dict[str, Any], task_id: str) -> str:
    try:
        return template.format(
            task_id=task_id,
            candidate_id=candidate["candidate_id"],
            stage=candidate["stage"],
            module_id=candidate["module_id"],
            lane_type=candidate["lane_type"],
        )
    except KeyError as error:
        raise GovernanceError(
            f"roadmap candidate {candidate['candidate_id']} template references unsupported field: {error}"
        ) from error


def _load_yaml_map(path: Path, *, missing_ok: bool = False) -> dict[str, Any]:
    if missing_ok and not path.exists():
        return {}
    payload = load_yaml(path) or {}
    if not isinstance(payload, dict):
        raise GovernanceError(f"expected mapping payload: {path.as_posix()}")
    return payload


def _load_sellable_regions(root: Path) -> set[str]:
    payload = _load_yaml_map(root / REGION_COVERAGE_REGISTRY_FILE)
    regions = payload.get("regions") or []
    return {
        str(region.get("region_code"))
        for region in regions
        if region.get("region_code") and region.get("is_sellable") is True
    }


def _load_source_regions(root: Path) -> set[str]:
    payload = _load_yaml_map(root / SOURCE_REGISTRY_FILE)
    sources = payload.get("sources") or []
    regions: set[str] = set()
    for source in sources:
        for region in source.get("coverage_regions") or []:
            if region:
                regions.add(str(region))
    return regions


def _load_pilot_enabled_candidates(root: Path) -> set[str]:
    frontmatter, _ = read_roadmap(root)
    enabled = frontmatter.get("pilot_enabled_candidates") or []
    if not isinstance(enabled, list):
        raise GovernanceError("roadmap pilot_enabled_candidates must be a list when present")
    return {str(item) for item in enabled if item}


def _candidate_regions(candidate: dict[str, Any]) -> list[str]:
    explicit = candidate.get("coverage_regions") or candidate.get("coverage_region") or candidate.get("region_code")
    if explicit:
        if isinstance(explicit, list):
            return [str(item) for item in explicit if item]
        return [str(explicit)]
    candidate_id = str(candidate.get("candidate_id") or "").lower()
    planned_paths = [str(path).lower() for path in candidate.get("planned_write_paths") or []]
    if "global" in candidate_id or any("/global/" in path for path in planned_paths):
        return ["GLOBAL"]
    if "cn" in candidate_id or any("/cn/" in path for path in planned_paths):
        return ["CN"]
    return ["CN"]


def _missing_planned_paths(root: Path, planned_paths: list[str]) -> list[str]:
    missing: list[str] = []
    for raw in planned_paths:
        normalized = actual_path(str(raw))
        if not normalized:
            continue
        if not (root / normalized).exists():
            missing.append(normalized)
    return missing


def _load_backlog(root: Path) -> dict[str, Any]:
    path = root / ROADMAP_BACKLOG_FILE
    if not path.exists():
        raise GovernanceError(f"roadmap backlog missing: {ROADMAP_BACKLOG_FILE}")
    return _load_yaml_map(path)


def _load_schema(root: Path) -> dict[str, Any]:
    path = root / ROADMAP_BACKLOG_SCHEMA_FILE
    if not path.exists():
        raise GovernanceError(f"roadmap backlog schema missing: {ROADMAP_BACKLOG_SCHEMA_FILE}")
    return _load_yaml_map(path)


def _load_claims(root: Path) -> dict[str, Any]:
    payload = _load_yaml_map(root / CLAIMS_FILE, missing_ok=True)
    payload.setdefault("claims", [])
    return payload


def _compiler_policy(backlog: dict[str, Any]) -> dict[str, Any]:
    policy = backlog.get("compiler_policy") or {}
    return {
        "mode": str(policy.get("mode") or "inline_candidates"),
        "compiled_graph_file": str(policy.get("compiled_graph_file") or COMPILED_GRAPH_FILE.as_posix()),
        "graph_version": str(policy.get("graph_version") or GRAPH_VERSION),
    }


def _compiled_graph_path(root: Path, backlog: dict[str, Any]) -> Path:
    raw = Path(_compiler_policy(backlog)["compiled_graph_file"])
    return raw if raw.is_absolute() else (root / raw)


def _source_hashes(root: Path) -> dict[str, str]:
    return {
        "roadmap_backlog": __import__("hashlib").sha256((root / ROADMAP_BACKLOG_FILE).read_bytes()).hexdigest(),
        "module_map": __import__("hashlib").sha256((root / "docs/governance/MODULE_MAP.yaml").read_bytes()).hexdigest(),
        "task_policy": __import__("hashlib").sha256((root / "docs/governance/TASK_POLICY.yaml").read_bytes()).hexdigest(),
    }


def _load_candidate_source(root: Path, backlog: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    policy = _compiler_policy(backlog)
    if policy["mode"] == "inline_candidates":
        return list(backlog.get("candidates") or []), {
            "graph_version": GRAPH_VERSION,
            "compiled_mode": "inline_candidates",
            "compiled_at": None,
            "module_map_version": None,
            "policy_version": None,
        }
    inline_candidates = list(backlog.get("candidates") or [])
    if inline_candidates:
        raise GovernanceError("inline candidates are forbidden when compiled_mode=module_graph_compiler")
    path = _compiled_graph_path(root, backlog)
    if not path.exists():
        raise GovernanceError(f"compiled roadmap candidate graph missing: {path.as_posix()}")
    payload = _load_yaml_map(path)
    if str(payload.get("graph_version")) != policy["graph_version"]:
        raise GovernanceError("compiled roadmap candidate graph version drift detected")
    if payload.get("source_hashes") != _source_hashes(root):
        raise GovernanceError("compiled roadmap candidate graph is stale; re-run compile-roadmap-candidates")
    candidates = list(payload.get("candidates") or [])
    return candidates, {
        "graph_version": payload.get("graph_version"),
        "compiled_mode": payload.get("mode"),
        "compiled_at": payload.get("compiled_at"),
        "module_map_version": payload.get("module_map_version"),
        "policy_version": payload.get("policy_version"),
    }


def _required_list(schema: dict[str, Any], key: str) -> set[str]:
    values = schema.get(key) or []
    if not isinstance(values, list):
        raise GovernanceError(f"schema field must be a list: {key}")
    return {str(value) for value in values}


def _roadmap_scheduler_policy(task_policy: dict[str, Any] | None = None) -> dict[str, Any]:
    scheduler = (task_policy or {}).get("roadmap_scheduler") or {}
    return {
        "max_active_claims_v1": max(1, int(scheduler.get("max_active_claims_v1", 4))),
    }


def roadmap_claim_capacity(root: Path) -> int:
    return _roadmap_scheduler_policy(load_task_policy(root))["max_active_claims_v1"]


def _stale_after_minutes(root: Path) -> int:
    policy = _load_yaml_map(root / "docs/governance/HANDOFF_POLICY.yaml", missing_ok=True)
    return int(policy.get("stale_after_minutes") or 30)


def _validate_candidate_refs(candidates: list[dict[str, Any]]) -> None:
    candidate_ids = {candidate["candidate_id"] for candidate in candidates}
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        refs = list(candidate.get("depends_on") or []) + list(candidate.get("unlocks") or [])
        integration_gate = candidate.get("integration_gate")
        if integration_gate:
            refs.append(integration_gate)
        refs.extend(candidate.get("expected_children") or [])
        unresolved = [
            str(ref)
            for ref in refs
            if str(ref).startswith("stage") and str(ref) not in candidate_ids and not str(ref).startswith("TASK-")
        ]
        if unresolved:
            raise GovernanceError(
                f"roadmap candidate {candidate_id} references unknown candidate(s): {', '.join(sorted(set(unresolved)))}"
            )


def _legacy_mapping_for_candidate(backlog: dict[str, Any], candidate: dict[str, Any]) -> str | None:
    defaults = backlog.get("defaults") or {}
    explicit = candidate.get("legacy_reserved_paths_map_to")
    fallback = defaults.get("legacy_reserved_paths_map_to")
    value = explicit if explicit is not None else fallback
    if value is None:
        return None
    normalized = str(value)
    if normalized not in {"forbidden_write_paths", "protected_paths"}:
        raise GovernanceError(
            f"roadmap candidate {candidate['candidate_id']} has invalid legacy_reserved_paths_map_to: {normalized}"
        )
    return normalized


def _normalize_candidate(backlog: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(candidate)
    normalized.setdefault("candidate_kind", "integration_gate" if candidate.get("lane_type") == "integration_gate" else "lane_slice")
    normalized.setdefault("claimable", normalized["candidate_kind"] != "lane_group")
    normalized.setdefault("parent_candidate_id", None)
    normalized.setdefault("expected_children", [])
    normalized.setdefault("completion_policy", "none")
    forbidden = list(candidate.get("forbidden_write_paths") or [])
    protected = list(candidate.get("protected_paths") or [])
    legacy_reserved = list(candidate.get("reserved_paths") or [])
    if legacy_reserved:
        mapping = _legacy_mapping_for_candidate(backlog, candidate)
        if mapping is None:
            raise GovernanceError(
                f"roadmap candidate {candidate['candidate_id']} uses legacy reserved_paths without explicit mapping"
            )
        if mapping == "forbidden_write_paths":
            forbidden = [*forbidden, *legacy_reserved]
        else:
            protected = [*protected, *legacy_reserved]
    normalized["forbidden_write_paths"] = _dedupe(forbidden)
    normalized["protected_paths"] = _dedupe(protected)
    if normalized["candidate_kind"] == "lane_group" and normalized.get("claimable"):
        raise GovernanceError(f"lane_group candidate must not be claimable: {candidate['candidate_id']}")
    return normalized


def _validate_backlog_shape(backlog: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    missing_top = sorted(_required_list(schema, "required_top_level_fields") - set(backlog))
    if missing_top:
        raise GovernanceError(f"roadmap backlog missing top-level fields: {', '.join(missing_top)}")

    candidates = backlog.get("candidates") or []
    if not isinstance(candidates, list):
        raise GovernanceError("roadmap backlog field `candidates` must be a list")
    if not candidates:
        raise GovernanceError("roadmap backlog has no candidates")

    allowed_lane_types = set((schema.get("lane_types") or {}).keys())
    allowed_statuses = set(schema.get("candidate_status_values") or [])
    required_candidate_fields = _required_list(schema, "required_candidate_fields")

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise GovernanceError("roadmap backlog candidate must be a mapping")
        candidate_id = str(candidate.get("candidate_id") or "")
        if not candidate_id:
            raise GovernanceError("roadmap backlog candidate missing candidate_id")
        if candidate_id in seen:
            raise GovernanceError(f"duplicate roadmap candidate_id: {candidate_id}")
        seen.add(candidate_id)

        missing = sorted(required_candidate_fields - set(candidate))
        if missing:
            raise GovernanceError(f"roadmap candidate {candidate_id} missing fields: {', '.join(missing)}")
        if candidate.get("lane_type") not in allowed_lane_types:
            raise GovernanceError(f"roadmap candidate {candidate_id} has invalid lane_type: {candidate.get('lane_type')}")
        if candidate.get("status") not in allowed_statuses:
            raise GovernanceError(f"roadmap candidate {candidate_id} has invalid status: {candidate.get('status')}")
        if not isinstance(candidate.get("priority"), int):
            raise GovernanceError(f"roadmap candidate {candidate_id} priority must be an integer")
        for field in ("depends_on", "unlocks", "allowed_dirs", "planned_write_paths", "planned_test_paths", "required_tests"):
            if not isinstance(candidate.get(field), list):
                raise GovernanceError(f"roadmap candidate {candidate_id} field `{field}` must be a list")
        normalized_candidate = _normalize_candidate(backlog, candidate)
        if not isinstance(normalized_candidate.get("expected_children"), list):
            raise GovernanceError(f"roadmap candidate {candidate_id} field `expected_children` must be a list")
        normalized.append(normalized_candidate)

    _validate_candidate_refs(normalized)
    return normalized


def _tasks_by_candidate(root: Path, candidates: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    registry = load_task_registry(root)
    tasks = registry.get("tasks", [])
    by_candidate: dict[str, list[dict[str, Any]]] = {candidate["candidate_id"]: [] for candidate in candidates}
    task_hint_map = {candidate["candidate_id"]: _candidate_task_id(candidate["candidate_id"]) for candidate in candidates}
    for task in tasks:
        mapped = task.get("roadmap_candidate_id")
        if mapped in by_candidate:
            by_candidate[str(mapped)].append(task)
            continue
        for candidate_id, task_hint in task_hint_map.items():
            if task.get("task_id") == task_hint:
                by_candidate[candidate_id].append(task)
                break
    return by_candidate


def _primary_task(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not tasks:
        return None
    open_tasks = [task for task in tasks if task.get("status") in OPEN_FORMAL_TASK_STATUSES]
    if open_tasks:
        def _sort_key(task: dict[str, Any]) -> tuple[int, str]:
            order = {"doing": 0, "review": 1, "paused": 2, "blocked": 3}
            return order.get(str(task.get("status")), 99), str(task.get("last_reported_at") or "")

        return sorted(open_tasks, key=_sort_key)[0]
    return sorted(tasks, key=lambda task: str(task.get("last_reported_at") or ""), reverse=True)[0]


def _claim_by_candidate(claims: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(claim["candidate_id"]): claim for claim in claims.get("claims", [])}


def _claim_is_fresh(claim: dict[str, Any], now: datetime) -> bool:
    expires_at = _parse_iso(str(claim.get("expires_at") or ""))
    if expires_at is None:
        return True
    return expires_at > now


def _claim_is_stale(root: Path, claim: dict[str, Any], now: datetime) -> bool:
    if str(claim.get("status")) not in CLAIM_ACTIVE_STATUSES:
        return False
    expires_at = _parse_iso(str(claim.get("expires_at") or ""))
    if expires_at is not None and expires_at <= now:
        return True
    return False


def _takeover_blockers(
    root: Path,
    candidate: dict[str, Any],
    claim: dict[str, Any],
    primary_task: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    if primary_task is None and claim.get("formal_task_id"):
        blockers.append(f"formal task missing for stale claim: {claim.get('formal_task_id')}")
    return blockers


def _active_claim_count(root: Path, claims: dict[str, Any], now: datetime) -> int:
    return sum(
        1
        for claim in claims.get("claims", [])
        if _claim_is_fresh(claim, now)
        and not _claim_is_stale(root, claim, now)
        and str(claim.get("status")) in CLAIM_ACTIVE_STATUSES
    )


def _single_writer_roots(backlog: dict[str, Any]) -> list[str]:
    return list((backlog.get("scheduler_policy") or {}).get("single_writer_roots") or [])


def _selection_score(*, priority: int, lane_type: str, takeover_mode: str, claimable: bool) -> int:
    score = max(0, 10_000 - priority)
    if claimable:
        score += 100_000
    if takeover_mode != "none":
        score += 1_000_000
    if lane_type == "integration_gate":
        score += 40_000
    elif lane_type == "core_contract":
        score += 20_000
    return score


def _dependency_result(
    dependency_id: str,
    *,
    candidates_by_id: dict[str, dict[str, Any]],
    evaluator: "CandidateEvaluator",
) -> dict[str, Any]:
    if dependency_id in candidates_by_id:
        dependency = evaluator.evaluate(dependency_id)
        return {
            "dependency_id": dependency_id,
            "source_kind": "candidate",
            "status": dependency["effective_status"],
            "satisfied": dependency["effective_status"] in TERMINAL_STATUSES,
        }
    return {
        "dependency_id": dependency_id,
        "source_kind": "task" if dependency_id.startswith("TASK-") else "candidate",
        "status": "missing",
        "satisfied": False,
    }


class CandidateEvaluator:
    def __init__(
        self,
        *,
        root: Path,
        backlog: dict[str, Any],
        candidates: list[dict[str, Any]],
        claims: dict[str, Any],
        now: datetime,
        scope_policy: dict[str, Any],
    ) -> None:
        self.root = root
        self.backlog = backlog
        self.candidates = candidates
        self.candidates_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
        self.claims_by_candidate = _claim_by_candidate(claims)
        self.now = now
        self.mvp_stage_ids = set(scope_policy.get("mvp_stage_ids") or [])
        self.sellable_regions = set(scope_policy.get("sellable_regions") or [])
        self.source_regions = set(scope_policy.get("source_regions") or [])
        self.pilot_enabled_candidates = set(scope_policy.get("pilot_enabled_candidates") or [])
        self.single_writer_roots = _single_writer_roots(backlog)
        self.tasks_by_candidate = _tasks_by_candidate(root, candidates)
        self.active_conflict_tasks = [
            task
            for task in load_task_registry(root).get("tasks", [])
            if task.get("status") in ACTIVE_TASK_CONFLICT_STATUSES
        ]
        self._cache: dict[str, dict[str, Any]] = {}
        self._stack: set[str] = set()
        self.max_active_claims = roadmap_claim_capacity(root)
        self.active_claim_count = _active_claim_count(root, claims, now)

    def evaluate(self, candidate_id: str) -> dict[str, Any]:
        if candidate_id in self._cache:
            return self._cache[candidate_id]
        if candidate_id in self._stack:
            raise GovernanceError(f"roadmap candidate dependency cycle detected: {candidate_id}")
        self._stack.add(candidate_id)
        candidate = self.candidates_by_id[candidate_id]
        result = self._evaluate_candidate(candidate)
        self._stack.remove(candidate_id)
        self._cache[candidate_id] = result
        return result

    def _evaluate_candidate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        candidate_id = candidate["candidate_id"]
        task_id_hint = _candidate_task_id(candidate_id)
        branch = _format_template(str(candidate["branch_template"]), candidate=candidate, task_id=task_id_hint)
        worktree = _format_template(str(candidate["worktree_template"]), candidate=candidate, task_id=task_id_hint)
        dependency_status = [
            _dependency_result(str(dependency_id), candidates_by_id=self.candidates_by_id, evaluator=self)
            for dependency_id in candidate.get("depends_on") or []
        ]
        reason_codes: list[str] = []
        wait_reasons = [
            f"waiting for {dependency['dependency_id']} ({dependency['status']})"
            for dependency in dependency_status
            if not dependency["satisfied"]
        ]
        if any(not dependency["satisfied"] for dependency in dependency_status):
            _append_reason(reason_codes, "dependency_wait")
        expected_children = list(candidate.get("expected_children") or [])
        completion_policy = str(candidate.get("completion_policy") or "none")
        child_statuses = [self.evaluate(child_id) for child_id in expected_children]
        if completion_policy == "all_expected_children_done":
            for child in child_statuses:
                if child["effective_status"] not in TERMINAL_STATUSES:
                    wait_reasons.append(f"waiting for expected child {child['candidate_id']} ({child['effective_status']})")
            if any(child["effective_status"] not in TERMINAL_STATUSES for child in child_statuses):
                _append_reason(reason_codes, "expected_children_wait")
        elif completion_policy == "all_expected_claimable_children_done":
            for child in child_statuses:
                if child.get("claimable_declared", False) and child["effective_status"] not in TERMINAL_STATUSES:
                    wait_reasons.append(
                        f"waiting for expected claimable child {child['candidate_id']} ({child['effective_status']})"
                    )
            if any(
                child.get("claimable_declared", False) and child["effective_status"] not in TERMINAL_STATUSES
                for child in child_statuses
            ):
                _append_reason(reason_codes, "expected_claimable_children_wait")

        primary_task = _primary_task(self.tasks_by_candidate.get(candidate_id, []))
        claim = self.claims_by_candidate.get(candidate_id)
        takeover_mode = "none"
        blockers: list[str] = []
        active_conflict_set: list[str] = []

        stage_id = str(candidate.get("stage") or "")
        if stage_id.startswith("stage") and self.mvp_stage_ids and stage_id not in self.mvp_stage_ids:
            blockers.append(f"out of MVP scope: {stage_id}")
            _append_reason(reason_codes, "out_of_mvp_scope")

        if candidate.get("pilot_only") and candidate_id not in self.pilot_enabled_candidates:
            blockers.append("pilot-only candidate requires control-plane enablement")
            _append_reason(reason_codes, "pilot_only")

        candidate_regions = _candidate_regions(candidate)
        for region in candidate_regions:
            if region not in self.sellable_regions or region not in self.source_regions:
                blockers.append(f"coverage not registered for region {region}")
                _append_reason(reason_codes, "coverage_not_registered")

        if claim and _claim_is_stale(self.root, claim, self.now):
            stale_blockers = _takeover_blockers(self.root, candidate, claim, primary_task)
            if stale_blockers:
                blockers.extend(stale_blockers)
                _append_reason(reason_codes, "stale_takeover_blocked")
            else:
                takeover_mode = (
                    "expired_promoted_takeover"
                    if str(claim.get("status")) == "promoted" and _parse_iso(str(claim.get("expires_at") or "")) is not None
                    else "stale_claim_takeover"
                )
                _append_reason(reason_codes, "stale_takeover_ready")

        if primary_task is not None and primary_task.get("status") == "blocked" and takeover_mode == "none":
            blockers.append(f"formal task blocked: {primary_task['task_id']}")
            _append_reason(reason_codes, "formal_task_blocked")

        if claim and _claim_is_fresh(claim, self.now) and takeover_mode == "none":
            blockers.append(f"active claim by {claim.get('window_id')}")
            active_conflict_set.append(str(claim.get("window_id") or candidate_id))
            _append_reason(reason_codes, "active_claim")

        if not wait_reasons and candidate.get("claimable", True) and takeover_mode == "none" and self.active_claim_count >= self.max_active_claims:
            blockers.append(f"roadmap claim capacity reached ({self.active_claim_count}/{self.max_active_claims})")
            _append_reason(reason_codes, "capacity_limit")

        candidate_paths = list(candidate.get("planned_write_paths") or [])
        protected_paths = list(candidate.get("protected_paths") or [])
        allow_create_paths = bool(candidate.get("allow_create_paths") or candidate.get("bootstrap_required"))
        missing_paths = [] if allow_create_paths else _missing_planned_paths(self.root, candidate_paths)
        if missing_paths:
            blockers.append(f"planned write paths missing: {', '.join(missing_paths)}")
            _append_reason(reason_codes, "planned_write_path_missing")
        same_formal_task_id = primary_task.get("task_id") if primary_task else None
        for task in self.active_conflict_tasks:
            if same_formal_task_id and task.get("task_id") == same_formal_task_id:
                continue
            if _any_path_overlaps(candidate_paths, list(task.get("planned_write_paths") or [])):
                blockers.append(f"write-path overlap with {task['task_id']}")
                active_conflict_set.append(str(task["task_id"]))
                _append_reason(reason_codes, "write_path_overlap")
                break
        for task in self.active_conflict_tasks:
            if same_formal_task_id and task.get("task_id") == same_formal_task_id:
                continue
            if _any_path_overlaps(candidate_paths, list(task.get("protected_paths") or [])):
                blockers.append(f"protected-path conflict with {task['task_id']}")
                active_conflict_set.append(str(task["task_id"]))
                _append_reason(reason_codes, "protected_path_conflict")
                break
            if _any_path_overlaps(list(task.get("planned_write_paths") or []), protected_paths):
                blockers.append(f"protected-path conflict with {task['task_id']}")
                active_conflict_set.append(str(task["task_id"]))
                _append_reason(reason_codes, "protected_path_conflict")
                break

        for root in self.single_writer_roots:
            if not any(_paths_overlap(path, root) for path in candidate_paths):
                continue
            conflict = next(
                (
                    task
                    for task in self.active_conflict_tasks
                    if not (same_formal_task_id and task.get("task_id") == same_formal_task_id)
                    and any(_paths_overlap(path, root) for path in task.get("planned_write_paths") or [])
                ),
                None,
            )
            if conflict is not None:
                blockers.append("single-writer root conflict")
                active_conflict_set.append(str(conflict["task_id"]))
                _append_reason(reason_codes, "single_writer_root_conflict")
                break

        if branch and any(
            task.get("branch") == branch and not (same_formal_task_id and task.get("task_id") == same_formal_task_id)
            for task in self.active_conflict_tasks
        ):
            blockers.append("branch already owned by active task")
            _append_reason(reason_codes, "branch_conflict")
        if branch and branch_exists(self.root, branch) and takeover_mode == "none" and primary_task is None:
            blockers.append("branch already exists")
            _append_reason(reason_codes, "branch_conflict")

        declared_status = str(candidate.get("status"))
        claimable_declared = bool(candidate.get("claimable", True))
        effective_status = declared_status
        scope_blocked = "out_of_mvp_scope" in reason_codes and primary_task is None
        if declared_status in TERMINAL_STATUSES:
            claimable = False
        elif primary_task is not None and primary_task.get("status") == "done":
            effective_status = "done"
            claimable = False
        elif scope_blocked:
            effective_status = "blocked"
            claimable = False
        elif takeover_mode != "none":
            effective_status = "stale"
            claimable = not blockers and not wait_reasons
        elif primary_task is not None and primary_task.get("status") == "review":
            effective_status = "review"
            claimable = False
        elif primary_task is not None and primary_task.get("status") == "doing":
            effective_status = "running"
            claimable = False
        elif primary_task is not None and primary_task.get("status") == "paused":
            effective_status = "resumable"
            claimable = not blockers and not wait_reasons
        elif declared_status in {"claimed", "running", "stale", "resumable", "blocked", "review"}:
            effective_status = declared_status
            claimable = declared_status in {"stale", "resumable"} and not blockers and not wait_reasons
        elif wait_reasons:
            effective_status = "waiting"
            claimable = False
        elif blockers:
            effective_status = "blocked"
            claimable = False
        elif claimable_declared:
            effective_status = "ready"
            claimable = True
        else:
            effective_status = "waiting"
            claimable = False
        if not claimable_declared:
            _append_reason(reason_codes, "candidate_not_claimable")

        fresh_claimable = claimable and takeover_mode == "none" and effective_status == "ready"
        takeover_claimable = claimable and takeover_mode != "none"
        release_evidence_required = list(candidate.get("release_evidence") or [])
        release_evidence_satisfied = []
        if not any(not dependency["satisfied"] for dependency in dependency_status):
            release_evidence_satisfied.append("module_dependencies_satisfied")
        if completion_policy == "none" or not any("expected child" in reason for reason in wait_reasons):
            if completion_policy == "all_expected_children_done":
                release_evidence_satisfied.append("expected_children_done")
            elif completion_policy == "all_expected_claimable_children_done":
                release_evidence_satisfied.append("expected_claimable_children_done")
        if not blockers:
            release_evidence_satisfied.append("paths_safe")
        if not any(code == "capacity_limit" for code in reason_codes):
            release_evidence_satisfied.append("capacity_available")
        if takeover_mode != "none":
            release_evidence_satisfied.append("takeover_allowed")
        upstream_blocker_candidates = _dedupe(
            [dependency["dependency_id"] for dependency in dependency_status if not dependency["satisfied"]]
            + [
                child["candidate_id"]
                for child in child_statuses
                if child["effective_status"] not in TERMINAL_STATUSES
            ]
        )
        release_forecast = {
            "if_completed_candidate_ids": list(candidate.get("unlocks") or []),
            "unlock_count": len(list(candidate.get("unlocks") or [])),
            "passes_hard_gate": candidate.get("lane_type") in {"integration_gate", "fact_surface_gate"},
        }
        selection_score = _selection_score(
            priority=int(candidate.get("priority") or 0),
            lane_type=str(candidate.get("lane_type") or ""),
            takeover_mode=takeover_mode,
            claimable=claimable,
        )

        return {
            "candidate_id": candidate_id,
            "task_id_hint": task_id_hint,
            "title": candidate["title"],
            "stage": candidate["stage"],
            "module_id": candidate["module_id"],
            "lane_type": candidate["lane_type"],
            "candidate_kind": candidate["candidate_kind"],
            "claimable_declared": claimable_declared,
            "claimable": claimable,
            "fresh_claimable": fresh_claimable,
            "takeover_claimable": takeover_claimable,
            "declared_status": declared_status,
            "effective_status": effective_status,
            "status": effective_status,
            "priority": candidate["priority"],
            "rank": None,
            "wait_reasons": _dedupe(wait_reasons),
            "blocking_reason_codes": reason_codes,
            "blocking_reason_text": _dedupe([*wait_reasons, *blockers]),
            "blockers": _dedupe(blockers),
            "active_conflict_set": _dedupe(active_conflict_set),
            "upstream_blocker_candidates": upstream_blocker_candidates,
            "dependency_status": dependency_status,
            "depends_on": list(candidate.get("depends_on") or []),
            "unlocks": list(candidate.get("unlocks") or []),
            "allowed_dirs": list(candidate.get("allowed_dirs") or []),
            "forbidden_write_paths": list(candidate.get("forbidden_write_paths") or []),
            "protected_paths": list(candidate.get("protected_paths") or []),
            "planned_write_paths": candidate_paths,
            "planned_test_paths": list(candidate.get("planned_test_paths") or []),
            "required_tests": list(candidate.get("required_tests") or []),
            "branch_template": candidate["branch_template"],
            "worktree_template": candidate["worktree_template"],
            "candidate_branch": branch,
            "candidate_worktree": worktree,
            "integration_gate": candidate.get("integration_gate"),
            "claim_policy": dict(candidate.get("claim_policy") or {}),
            "takeover_policy": dict(candidate.get("takeover_policy") or {}),
            "parent_candidate_id": candidate.get("parent_candidate_id"),
            "expected_children": expected_children,
            "completion_policy": completion_policy,
            "takeover_mode": takeover_mode,
            "release_evidence_required": release_evidence_required,
            "release_evidence_satisfied": _dedupe(release_evidence_satisfied),
            "release_forecast": release_forecast,
            "unlock_count": release_forecast["unlock_count"],
            "source_authority": "compiled_graph" if self.backlog.get("compiler_policy", {}).get("mode") == "module_graph_compiler" else "inline_legacy",
            "legacy_mode": "legacy_candidate_compat" if "candidate_intent" not in candidate else "none",
            "selection_score": selection_score,
        }


def evaluate_roadmap_candidates(root: Path, *, now: datetime | None = None) -> dict[str, Any]:
    backlog = _load_backlog(root)
    schema = _load_schema(root)
    claims = _load_claims(root)
    candidate_source, compile_meta = _load_candidate_source(root, backlog)
    backlog_with_candidates = dict(backlog)
    backlog_with_candidates["candidates"] = candidate_source
    candidates = _validate_backlog_shape(backlog_with_candidates, schema)
    roadmap_frontmatter, _ = read_roadmap(root)
    mvp_policy = ensure_mvp_scope_matches_business_scope(root, roadmap_frontmatter.get("business_automation_scope"))
    scope_policy = {
        "mvp_scope": mvp_policy["scope"],
        "mvp_stage_ids": mvp_policy["allowed_stages"],
        "sellable_regions": _load_sellable_regions(root),
        "source_regions": _load_source_regions(root),
        "pilot_enabled_candidates": _load_pilot_enabled_candidates(root),
    }
    evaluator = CandidateEvaluator(
        root=root,
        backlog=backlog,
        candidates=candidates,
        claims=claims,
        now=now or _now(),
        scope_policy=scope_policy,
    )
    indexed = [evaluator.evaluate(candidate["candidate_id"]) for candidate in candidates]
    indexed.sort(
        key=lambda item: (
            INDEX_STATUS_ORDER.get(item["effective_status"], 99),
            -int(item["selection_score"]),
            int(item["priority"]),
            item["candidate_id"],
        )
    )
    for rank, item in enumerate(indexed, start=1):
        item["rank"] = rank

    status_counts: dict[str, int] = {}
    for item in indexed:
        status_counts[item["effective_status"]] = status_counts.get(item["effective_status"], 0) + 1

    ready_candidate_ids = [item["candidate_id"] for item in indexed if item["effective_status"] == "ready"]
    claimable_candidate_ids = [item["candidate_id"] for item in indexed if item["claimable"]]
    fresh_claimable_candidate_ids = [item["candidate_id"] for item in indexed if item["fresh_claimable"]]
    takeover_candidate_ids = [item["candidate_id"] for item in indexed if item["takeover_claimable"]]

    return {
        "version": "0.2",
        "format_version": COMPILED_FORMAT_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "generated_at": iso_now(),
        "source": str(ROADMAP_BACKLOG_FILE).replace("\\", "/"),
        "schema_source": str(ROADMAP_BACKLOG_SCHEMA_FILE).replace("\\", "/"),
        "graph_version": compile_meta.get("graph_version"),
        "compiled_mode": compile_meta.get("compiled_mode"),
        "compiled_at": compile_meta.get("compiled_at"),
        "module_map_version": compile_meta.get("module_map_version"),
        "policy_version": compile_meta.get("policy_version"),
        "candidate_count": len(indexed),
        "status_counts": status_counts,
        "candidate_ids": [item["candidate_id"] for item in indexed],
        "ready_candidate_ids": ready_candidate_ids,
        "waiting_candidate_ids": [item["candidate_id"] for item in indexed if item["effective_status"] == "waiting"],
        "claimable_candidate_ids": claimable_candidate_ids,
        "fresh_claimable_candidate_ids": fresh_claimable_candidate_ids,
        "takeover_candidate_ids": takeover_candidate_ids,
        "roadmap_claim_capacity": evaluator.max_active_claims,
        "active_claim_count": evaluator.active_claim_count,
        "candidates": indexed,
    }


__all__ = [
    "CLAIMS_FILE",
    "COMPILED_FORMAT_VERSION",
    "EVALUATOR_VERSION",
    "ROADMAP_BACKLOG_FILE",
    "ROADMAP_BACKLOG_SCHEMA_FILE",
    "evaluate_roadmap_candidates",
    "roadmap_claim_capacity",
]
