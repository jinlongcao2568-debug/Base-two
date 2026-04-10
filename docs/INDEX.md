# AX9S Documentation Entry Index

This page is the single routing map for AX9S documentation. It does not override authority sources; it keeps default reading paths focused on product work first and governance only when needed.

## Default Reading Routes

Product development default route:
1. `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`
2. `docs/product/AUTHORITY_SPEC.md`
3. `docs/product/MVP_SCOPE.md`
4. `docs/product/PRODUCT_BOUNDARIES.md`
5. `docs/contracts/`

Governance execution route:
1. `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md`
2. `docs/governance/OPERATOR_MANUAL.md`
3. `docs/governance/CURRENT_TASK.yaml`
4. the current task file and runlog when you are working inside the live governed task

If any downstream file drifts, fix the downstream file. Do not weaken the authority source.

## Keep vs Historical

Keep in the daily entry path:
- `docs/product/`
- `docs/contracts/`
- `docs/governance/OPERATOR_MANUAL.md`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/DIRECTORY_MAP.md`
- `docs/governance/TEST_MATRIX.yaml`

Retain for audit and recovery, but do not route ordinary development through them first:
- `docs/governance/tasks/`
- `docs/governance/runlogs/`
- `docs/governance/handoffs/`
- historical transition and scheduler design documents under `docs/governance/`

## Problem -> Document Index

| Problem | Read First | Notes |
| --- | --- | --- |
| Domain boundaries, stages, formal objects, rule meanings | `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md` | Highest authority |
| Repository-scoped authority expansion | `docs/product/AUTHORITY_SPEC.md` | Product-facing execution boundary |
| MVP scope and non-claims | `docs/product/MVP_SCOPE.md` | Use for scope and shipping discussions |
| Customer-visible and implementation boundaries | `docs/product/PRODUCT_BOUNDARIES.md` | Use before page/API/business changes |
| Formal schemas, registries, and field semantics | `docs/contracts/` | Machine-readable contract truth |
| How to work inside a governed task | `docs/governance/OPERATOR_MANUAL.md` | Read before implementation under live task control |
| Which task is live right now | `docs/governance/CURRENT_TASK.yaml` | Live focus entry only |
| Live task and occupancy state | `docs/governance/TASK_REGISTRY.yaml`, `docs/governance/WORKTREE_REGISTRY.yaml` | Control-plane truth, not product onboarding |
| Historical audit trail for a past task | `docs/governance/tasks/`, `docs/governance/runlogs/`, `docs/governance/handoffs/` | Audit only, not default route |

## 10-Minute Onboarding Path

1. `docs/product/AUTHORITY_SPEC.md`
2. `docs/product/MVP_SCOPE.md`
3. `docs/product/PRODUCT_BOUNDARIES.md`
4. `docs/contracts/`
5. `docs/governance/CURRENT_TASK.yaml` only if you are about to implement inside the governed workflow

If you need live operator procedure, read `docs/governance/OPERATOR_MANUAL.md` next. If you only need product context, stop before the governance ledgers.

## When To Update This Index

- Authority paths or versions change.
- Product-first onboarding changes.
- The minimum live governance entry set changes.
- A historical governance surface becomes a live default entry, or a live surface is demoted to audit-only.
