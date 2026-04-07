# TASK-GOV-031 V1.5权威文档基线落库与开发手册重建

## Task Baseline

- `task_id`: `TASK-GOV-031`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `review`
- `stage`: `governance-v15-authority-baseline-and-dev-manual-v1`
- `branch`: `feat/TASK-GOV-031-v15-authority-dev-manual`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Use `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.5_全量规则码版.md` as the sole authority baseline for the engineering domain.
- Remove prior-version carry-over language from the authority baseline where the user explicitly wants a fresh start rather than an inherited history trail.
- Generate a fresh V1.5-aligned development / Codex manual under `docs/baseline/` that follows the authority document and does not inherit V1.4 narrative framing.
- Keep all changes confined to baseline documentation and the minimum governance ledgers required to activate and track the task.

## Explicitly Not Doing

- Do not modify `src/`, `tests/`, `scripts/`, `db/migrations/`, or `docs/contracts/`.
- Do not align schemas, examples, interfaces, or implementation code in this task; this round is documentation-only.
- Do not preserve V1.4 comparison narratives in the new baseline manual unless strictly required for current governance control.
- Do not delete archival baseline files unless a later explicit cleanup task authorizes it.

## Acceptance Targets

- The V1.5 authority document in `docs/baseline/` reads as the current sole baseline and no longer frames itself as an incremental carry-over from V1.4.
- A new V1.5 development / Codex manual exists in `docs/baseline/` and stays within execution-discipline scope rather than redefining domain rules.
- The authority document and development manual agree on role split: authority doc defines domain truth; dev manual defines repository execution and delivery discipline.
- Governance ledgers (`CURRENT_TASK`, `DEVELOPMENT_ROADMAP`, `TASK_REGISTRY`, `WORKTREE_REGISTRY`, task file, runlog) are aligned to `TASK-GOV-031`.

## Allowed Dirs

- `docs/baseline/`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/handoffs/`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/tasks/`
- `docs/governance/runlogs/`

## Planned Write Paths

- `docs/baseline/`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/handoffs/TASK-GOV-031.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/tasks/TASK-GOV-031.md`
- `docs/governance/runlogs/TASK-GOV-031-RUNLOG.md`

## Planned Test Paths

- `docs/baseline/`

## Required Tests

- `文档结构完整性检查`
- `交叉引用一致性检查`
- `权威文档与开发手册职责边界检查`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/`
- `scripts/`
- `README.md`
## Narrative Assertions

- `narrative_status`: `review`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `baseline_and_manual_ready_for_review`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `review_decision`

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `review`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/, scripts/, README.md`
- `branch`: `feat/TASK-GOV-031-v15-authority-dev-manual`
- `updated_at`: `2026-04-07T09:24:12+08:00`
<!-- generated:task-meta:end -->
