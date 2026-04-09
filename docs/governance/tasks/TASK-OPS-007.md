# TASK-OPS-007 full-clone runtime parity and stale claim recovery

## Task Baseline

- `task_id`: `TASK-OPS-007`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `doing`
- `stage`: `governance-runtime-parity-recovery-v1`
- `branch`: `codex/TASK-OPS-007-runtime-parity-and-stale-claim-recovery`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
## Primary Goals

- Refresh `worker-01..09` so every ready full-clone slot matches the current published governance runtime.
- Re-run full-clone and candidate-pool audits until runtime drift is cleared from dispatch-eligible slots.
- Resolve the stale promoted claim and incomplete execution record for `TASK-RM-STAGE2-SOURCE-FAMILY-LANES`.
- Restore the control plane to an idle, claimable state after the refresh-and-closeout cycle completes.

## Explicitly Not Doing

- Do not modify `src/`, `tests/stage2/`, `docs/contracts/`, `db/migrations/`, or business-stage logic.
- Do not change candidate ranking, claim-next scheduling semantics, or the concurrent single-ledger model.
- Do not repair clone-local ledgers by hand outside the supported control-plane commands.
- Do not create a replacement execution task for `stage2-source-family-lanes` if the existing formal task can be legally closed or continued.

## Allowed Dirs

- `docs/governance/`
- `.codex/local/roadmap_candidates/`
- `.codex/local/governance_runtime/`

## Planned Write Paths

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/FULL_CLONE_POOL.yaml`
- `docs/governance/tasks/TASK-OPS-007.md`
- `docs/governance/runlogs/TASK-OPS-007-RUNLOG.md`
- `docs/governance/handoffs/TASK-OPS-007.yaml`
- `.codex/local/roadmap_candidates/claims.yaml`
- `.codex/local/roadmap_candidates/index.yaml`
- `.codex/local/roadmap_candidates/summary.yaml`
- `.codex/local/governance_runtime/stamp.yaml`

## Planned Test Paths

- `docs/governance/`
- `.codex/local/roadmap_candidates/`

## Required Tests

- `python scripts/task_ops.py audit-full-clone-pool`
- `python scripts/review_candidate_pool.py`
- `python scripts/task_ops.py claim-next --now 2026-04-09T21:40:00+08:00`

## Reserved Paths

- `src/`
- `tests/stage2/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`

## Scope

- Runtime parity recovery for the ready full-clone worker pool.
- Candidate-pool recovery only as needed to remove the stale `stage2-source-family-lanes` claim chain.
- Governance-only closeout and audit updates required to make dispatch legal again.

## Acceptance Criteria

- `python scripts/task_ops.py audit-full-clone-pool` reports `ledger_divergence_count=0` and `stale_runtime_count=0`.
- `python scripts/review_candidate_pool.py` no longer reports runtime drift for ready full-clone slots.
- `TASK-RM-STAGE2-SOURCE-FAMILY-LANES` no longer appears as an incomplete execution task with a stale promoted claim.
- `python scripts/task_ops.py claim-next --now 2026-04-09T21:40:00+08:00` succeeds as a dry-run without runtime-drift blockers.

## Rollback

- Revert the task-package-only governance edits for `TASK-OPS-007`.
- If a refresh/recovery command leaves a slot in an unexpected state, stop and restore that slot via the existing full-clone rebuild / audit workflow instead of hand-editing clone ledgers.
- Do not roll back business-stage tasks or unrelated governance runtime commits as part of this recovery task.

## Risks

- A subset of full-clone slots may need `rebuild` instead of `refresh` if refresh cannot reconcile their runtime.
- The stale `stage2-source-family-lanes` task may require closeout or takeover logic depending on its current formal state.
- Candidate-pool status can remain degraded until both runtime parity and the stale Stage2 claim chain are cleared.
## Narrative Assertions

- `narrative_status`: `doing`
- `closeout_state`: `not_ready`
- `blocking_state`: `clear`
- `completed_scope`: `active_progress`
- `remaining_scope`: `active_work_remaining`
- `next_gate`: `validation_pending`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `doing`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `running`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `successor_state`: `backlog`
- `reserved_paths`: `[]`
- `branch`: `codex/TASK-OPS-007-runtime-parity-and-stale-claim-recovery`
- `updated_at`: `2026-04-09T21:35:25+08:00`
<!-- generated:task-meta:end -->
