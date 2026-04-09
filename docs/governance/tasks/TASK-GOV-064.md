# TASK-GOV-064 Single-ledger control-plane hardening for full-clone workers

## Task Baseline

- `task_id`: `TASK-GOV-064`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-control-plane-single-ledger-hardening-v1`
- `branch`: `codex/TASK-GOV-064-single-ledger-hardening`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Enforce the rule that governance lifecycle writes from full-clone workers must resolve to the main control plane.
- Detect and surface ledger divergence between the main control plane and full-clone worker mirrors.
- Restore reliable roadmap auto-release by ensuring execution closeout reaches the authoritative ledgers before candidate refresh.
- Keep the governance console thin while exposing divergence warnings and trustworthy operator feedback.

## Explicitly Not Doing

- Do not introduce a second scheduler or candidate selection engine.
- Do not make clone-local ledgers a peer truth source.
- Do not modify business runtime code under `src/`.
- Do not add direct Codex desktop automation or window control.

## Task Intake

- `primary_objective`: harden the governance control plane so multi-worktree execution cannot fork the authoritative task ledgers.
- `not_doing`: no business runtime changes, no UI-driven scheduler rewrite, no desktop automation.
- `stage_scope`: governance control-plane hardening only.
- `impact_modules`:
  - `docs/governance/CONTROL_PLANE_SINGLE_LEDGER_PRINCIPLES.md`
  - `scripts/task_runtime_ops.py`
  - `scripts/task_lifecycle_ops.py`
  - `scripts/task_worker_ops.py`
  - `scripts/control_plane_root.py`
  - `scripts/governance_console.py`
  - `tests/governance/`
- `interface_change`: no
- `schema_migration`: no
- `exception_required`: no
- `stage6_fact_refresh_impact`: no
- `customer_visible_commitment_impact`: no
- `region_or_source_coverage_impact`: no
- `customer_visible_pii_expansion`: no

## Acceptance Targets

- Governance write commands executed from full-clone workers no longer produce clone-local-only lifecycle state changes.
- Closing a roadmap execution task from a worker path updates the main control-plane ledgers, releases the full-clone slot, and closes the roadmap claim.
- Candidate refresh after closeout no longer leaves downstream candidates blocked because of clone-only ledger writes.
- The governance console can detect and display ledger divergence between the main control plane and full-clone worker mirrors.
- Operator guidance clearly distinguishes scheduler blockers from ledger divergence.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`

## Planned Write Paths

- `docs/governance/CONTROL_PLANE_SINGLE_LEDGER_PRINCIPLES.md`
- `docs/governance/tasks/TASK-GOV-064.md`
- `docs/governance/runlogs/TASK-GOV-064-RUNLOG.md`
- `docs/governance/handoffs/TASK-GOV-064.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/FULL_CLONE_POOL.yaml`
- `.codex/local/roadmap_candidates/claims.yaml`
- `scripts/task_runtime_ops.py`
- `scripts/task_lifecycle_ops.py`
- `scripts/task_worker_ops.py`
- `scripts/task_coordination_ops.py`
- `scripts/task_worktree_ops.py`
- `scripts/roadmap_claim_next.py`
- `scripts/roadmap_execution_closeout.py`
- `scripts/full_clone_pool.py`
- `scripts/roadmap_candidate_maintainer.py`
- `scripts/review_candidate_pool.py`
- `scripts/control_plane_root.py`
- `scripts/governance_console.py`
- `tests/governance/`

## Planned Test Paths

- `tests/governance/`

## Required Tests

- `pytest tests/governance -q`
- `python scripts/check_repo.py`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `README.md`
- `tests/contracts/`
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

## Acceptance Notes

- A worker may execute code inside a clone, but only the main control plane may finalize governance lifecycle truth.
- Ledger divergence is treated as a control-plane fault condition, not as valid candidate-pool truth.
- Auto-release remains derived from authoritative closeout, not from manual operator unlocks.

## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, README.md, tests/contracts/, tests/integration/, tests/stage1/, tests/stage2/, tests/stage3/, tests/stage4/, tests/stage5/, tests/stage6/, tests/stage7/, tests/stage8/, tests/stage9/`
- `branch`: `codex/TASK-GOV-064-single-ledger-hardening`
- `updated_at`: `2026-04-09T11:07:00+08:00`
<!-- generated:task-meta:end -->
