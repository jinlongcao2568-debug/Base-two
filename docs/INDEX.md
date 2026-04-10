# AX9S Documentation Entry Index

This page is the single routing map for AX9S documentation. It does not override authority sources; it tells you which source to read first for each question.

## Authority Priority (Highest -> Lowest)

1. `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md` (domain truth)
2. `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md` (execution discipline)
3. `docs/product/AUTHORITY_SPEC.md` (repository-scoped authority expansion)
4. `docs/governance/README.md` (live control-plane index and entrypoints)

If any downstream file drifts, fix the downstream file. Do not weaken the authority source.

## Live vs Archive (Do Not Mix)

- Live governance truth lives under `docs/governance/` in the main control plane.
- Clone worktrees must not be treated as independent governance truth sources.
- `docs/governance/CURRENT_TASK.yaml` is the live **focus entry** for the control plane.
- `docs/governance/EXECUTION_LEASES.yaml` is the live **execution occupancy** truth.

When the control plane and a clone disagree, treat it as ledger divergence and repair the main control plane first.

## Problem -> Document Index

| Problem | Authoritative Document | Notes |
| --- | --- | --- |
| Domain boundaries, objects, rule meanings | `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md` | Highest authority |
| Execution rules, governance discipline | `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md` | Required before implementation |
| Repository-scoped authority expansion | `docs/product/AUTHORITY_SPEC.md` | Must not conflict with baseline |
| Live control-plane entry & file map | `docs/governance/README.md` | Live files and execution order |
| Candidate pool + claim-next rules | `docs/governance/MODULAR_ROADMAP_SCHEDULER_DESIGN.md` | Claim rules and conflict locks |
| Candidate schema & required fields | `docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml` | Field contract and gating rules |
| Single-ledger governance rules | `docs/governance/CONTROL_PLANE_SINGLE_LEDGER_PRINCIPLES.md` | Control-plane write authority |
| Concurrent execution model | `docs/governance/CONCURRENT_EXECUTION_SINGLE_LEDGER_MODEL.md` | CURRENT_TASK vs EXECUTION_LEASES |
| Formal contracts and enums | `docs/contracts/` + `docs/governance/SCHEMA_REGISTRY.md` | Machine-readable contracts |

## 15-Minute Onboarding Path (New Contributors)

1. `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`
2. `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md`
3. `docs/governance/README.md`
4. `docs/governance/CURRENT_TASK.yaml` (focus entry)

If you need to understand concurrency or task occupancy, read `docs/governance/CONCURRENT_EXECUTION_SINGLE_LEDGER_MODEL.md` next.

## When To Update This Index

- Authority paths or versions change.
- Live ledger semantics change (for example, focus entry vs execution occupancy).
- New official entrypoints are introduced (for example, new governance commands or console panels).
