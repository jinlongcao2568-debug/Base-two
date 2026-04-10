# TASK-GOV-089 Delete non-essential governance surfaces and keep product chain only

## Task Baseline

- `task_id`: `TASK-GOV-089`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `doing`
- `stage`: `governance-surface-removal-v1`
- `branch`: `codex/TASK-OPS-009-full-clone-slot-release-hardening`
- `size_class`: `heavy`
- `automation_mode`: `assisted`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Deliver `TASK-GOV-089`: delete non-essential governance surfaces and keep product chain only for stage `governance-surface-removal-v1`.
- Preserve `AX9 治理操作员控制台` and its runtime chain while removing historical governance burden.
- Refactor the operator console into a task-centric surface: default `可领取任务`, plus `当前任务 / 已完成任务 / 任务总页面 / 高级诊断`.
- Implement planned write paths: docs/governance/, docs/product/, src/governance/, tests/contracts/, tests/governance/, scripts/, .codex/, output/, README.md, docs/INDEX.md.
- Keep required tests passing: python scripts/validate_contracts.py, pytest tests/contracts -q, pytest tests/integration/test_stage3_stage4_stage6_minimal_flow.py -q.

## Explicitly Not Doing

- Do not delete or weaken the operator console stack: `scripts/governance_console.py`, `scripts/governance_console_launcher.py`, `scripts/governance_console_launcher.vbs`, `scripts/task_ops.py`, and retained live control-plane ledgers.
- Do not touch reserved paths: docs/contracts/, src/domain/, src/shared/, src/stage1_orchestration/, src/stage2_ingestion/, src/stage3_parsing/, src/stage4_validation/, src/stage5_reporting/, src/stage6_facts/, src/stage7_sales/, src/stage8_contact/, src/stage9_delivery/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/, db/migrations/, AGENTS.md.
- Do not modify files outside allowed dirs: docs/governance/, docs/product/, src/governance/, tests/contracts/, tests/governance/, scripts/, .codex/, output/, README.md, docs/INDEX.md.
- Do not expand scope outside planned write paths: docs/governance/, docs/product/, src/governance/, tests/contracts/, tests/governance/, scripts/, .codex/, output/, README.md, docs/INDEX.md.

## Allowed Dirs

- `docs/governance/`
- `docs/product/`
- `src/governance/`
- `tests/contracts/`
- `tests/governance/`
- `scripts/`
- `.codex/`
- `output/`
- `README.md`
- `docs/INDEX.md`

## Planned Write Paths

- `docs/governance/`
- `docs/product/`
- `src/governance/`
- `tests/contracts/`
- `tests/governance/`
- `scripts/`
- `.codex/`
- `output/`
- `README.md`
- `docs/INDEX.md`

## Planned Test Paths

- `docs/contracts/`
- `tests/contracts/`
- `tests/integration/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage6/`

## Required Tests

- `python scripts/validate_contracts.py`
- `pytest tests/contracts -q`
- `pytest tests/integration/test_stage3_stage4_stage6_minimal_flow.py -q`

## Additional Validation

- `python -m py_compile scripts/governance_console.py scripts/review_candidate_pool.py scripts/roadmap_claim_next.py scripts/roadmap_scheduler_eval.py scripts/worker_self_loop.py`
- Open the operator console page and verify the task-center navigation manually

## Reserved Paths

- `docs/contracts/`
- `src/domain/`
- `src/shared/`
- `src/stage1_orchestration/`
- `src/stage2_ingestion/`
- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage5_reporting/`
- `src/stage6_facts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `tests/integration/`
- `tests/stage1/`
- `tests/stage2/`
- `tests/stage3/`
- `tests/stage4/`
- `tests/stage5/`
- `tests/stage6/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`
- `db/migrations/`
- `AGENTS.md`

## Narrative Assertions

- `narrative_status`: `doing`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `validation_pending`
## Execution Notes

- Historical governance task packages, runlogs, and handoffs were pruned; the live `TASK-GOV-089` package was retained.
- Governance-only policy ledgers, stale output artifacts, and non-runtime prompt files were removed.
- The AX9 operator console, launcher chain, live control-plane files, and console verification test were preserved by explicit user instruction.
- Deletion pass removed `342` files and `4` directories inside the approved scope.
- Follow-up cleanup removed two stale `dispatch_briefs` files plus their residual rows in `TASK_REGISTRY.yaml`, `WORKTREE_REGISTRY.yaml`, `WORKTREE_POOL.yaml`, and `EXECUTION_LEASES.yaml`.
- Console read models and UI were reworked so the main path no longer centers `worker-01..09` slot semantics; slot or lease details remain only in `高级诊断`.
- The task catalog now prefers the cached roadmap candidate snapshot, so the total-page view behaves like a static board with light ledger overlay instead of full live recomputation.
- Main-path lease dependency was removed; `EXECUTION_LEASES.yaml` is now an empty shell and no longer participates in console or claim decisions.
- Governance long-suite defaults were retired; governance verification now stays on repo hygiene, targeted smoke, and manual page-open checks.

## Acceptance Criteria

- Required tests pass: python scripts/validate_contracts.py, pytest tests/contracts -q, pytest tests/integration/test_stage3_stage4_stage6_minimal_flow.py -q.
- Console runtime and launcher chain remain usable after governance cleanup.
- Changes limited to planned write paths: docs/governance/, docs/product/, src/governance/, tests/contracts/, tests/governance/, scripts/, .codex/, output/, README.md, docs/INDEX.md.
- No open blockers remain at closeout.

## Rollback

- Revert branch `codex/TASK-OPS-009-full-clone-slot-release-hardening` to the last known good commit if needed.
- Restore deleted governance files from git history if any preserved runtime path or operator flow is found missing.
- Remove or reset generated artifacts before re-dispatching the task.

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `doing`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `assisted`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `docs/contracts/, src/domain/, src/shared/, src/stage1_orchestration/, src/stage2_ingestion/, src/stage3_parsing/, src/stage4_validation/, src/stage5_reporting/, src/stage6_facts/, src/stage7_sales/, src/stage8_contact/, src/stage9_delivery/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/, db/migrations/, AGENTS.md`
- `branch`: `codex/TASK-OPS-009-full-clone-slot-release-hardening`
- `updated_at`: `2026-04-10T14:46:09+08:00`
<!-- generated:task-meta:end -->
