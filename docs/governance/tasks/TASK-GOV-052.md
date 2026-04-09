# TASK-GOV-052 Roadmap live evaluator and stage1 child-lane pilot

## Task Baseline

- `task_id`: `TASK-GOV-052`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `governance-roadmap-live-evaluator-stage1-pilot-v1`
- `branch`: `codex/TASK-GOV-052-roadmap-live-evaluator-stage1-pilot`
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

- Introduce one shared live evaluator for roadmap candidates so candidate index, refresh summary, `claim-next`, and `review-candidate-pool` derive status from the same control-plane truth.
- Split overloaded backlog path semantics into `forbidden_write_paths` and `protected_paths`, while keeping a governed transition path for legacy `reserved_paths`.
- Convert `stage1` internal parallel work from one monolithic parent lane into one non-claimable lane group plus the minimum claimable child-slice pilot.
- Move roadmap claim capacity governance out of dead backlog-local configuration and into a single governed policy source separate from runner lane ceiling.
- Prove the model with a smallest-safe pilot: two disjoint `stage1` child slices plus one `stage1` integration gate.

## Explicitly Not Doing

- Do not change business logic under `src/`.
- Do not change `stage6_facts` fact refresh, write-back policy, or unified fact semantics.
- Do not change customer-visible contracts, delivery allowlists or blacklists, region coverage, source coverage, or customer-visible personal information fields.
- Do not change database schema, add migrations, or modify `db/migrations/`.
- Do not bulk-roll out `stage2` through `stage8` child-slice materialization in this task.
- Do not introduce a second truth layer, second fact surface, second top-level judgment path, or page/API-side replacement logic.

## Governance Impact Checks

- `interface_change`: `false`
- `schema_migration`: `false`
- `exception_required`: `false`
- `stage6_fact_refresh_impact`: `false`
- `customer_visible_commitment_impact`: `false`
- `region_or_source_coverage_impact`: `false`
- `customer_visible_pii_expansion`: `false`

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `.codex/local/roadmap_candidates/`

## Planned Write Paths

- `docs/governance/ROADMAP_BACKLOG.yaml`
- `docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml`
- `docs/governance/TASK_POLICY.yaml`
- `docs/governance/tasks/TASK-GOV-052.md`
- `scripts/roadmap_scheduler_eval.py`
- `scripts/roadmap_candidate_index.py`
- `scripts/roadmap_candidate_maintainer.py`
- `scripts/review_candidate_pool.py`
- `scripts/roadmap_claim_next.py`
- `scripts/governance_rules.py`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `pytest tests/governance/test_roadmap_scheduler_eval.py -q`
- `pytest tests/governance/test_roadmap_candidate_index.py -q`
- `pytest tests/governance/test_roadmap_claim_next.py -q`
- `pytest tests/governance/test_review_candidate_pool.py -q`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py src docs tests`
- `python scripts/check_authority_alignment.py`

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

## Schema Upgrade Requirements

- Backlog candidate shape must add `candidate_kind`, `claimable`, `parent_candidate_id`, `forbidden_write_paths`, and `protected_paths`.
- `candidate_kind` in this task is limited to `lane_group`, `lane_slice`, and `integration_gate`.
- Child completion semantics in this task must use `all_expected_children_done` or `all_expected_claimable_children_done`; do not introduce looser completion wording.
- Evaluator output must include `declared_status`, `effective_status`, `claimable`, `takeover_mode`, `blockers`, `active_conflict_set`, `expected_children`, and `selection_score`.
- Any compiled candidate artifact written by this task must declare a format version and must be rejected when evaluator and artifact format versions do not match.

## Legacy Field Migration Rules

- `reserved_paths` enters controlled deprecation in this task and must not remain an overloaded primary field.
- Transition policy is `double-read single-write`.
- Evaluator read compatibility in this task may inspect `forbidden_write_paths`, `protected_paths`, and legacy `reserved_paths`.
- New backlog writes, examples, fixtures, and generated artifacts must write only `forbidden_write_paths` and `protected_paths`.
- If legacy `reserved_paths` appears in a candidate fixture or backlog entry, the mapping target must be explicit; silent inference is not allowed.
- Legacy field sunset target is `TASK-GOV-053`; this task must leave the deprecation boundary machine-readable.

## Capacity Governance Rules

- Roadmap candidate claim capacity and execution-lane ceiling must not reuse one ambiguous policy key.
- `claim-next` must consume a governed roadmap scheduler cap such as `roadmap_scheduler.max_active_claims_v1`.
- Runner parallel lane logic must continue to consume execution-lane ceiling policy separately.
- The task is not complete if claim capacity and runner lane ceiling still drift or are read from the same unclear key.

## Stage1 Pilot Materialization

- Replace direct claiming of `stage1-source-family-lanes` with one non-claimable parent lane group.
- Materialize only the minimum pilot set:
- `stage1-source-family-group`
- `stage1-source-family-cn`
- `stage1-source-family-global`
- `stage1-source-family-integration-gate`
- Parent lane group must stay non-claimable.
- The two child slices must use disjoint `planned_write_paths` and disjoint `protected_paths`.
- The integration gate must depend on the expected child set rather than on a monolithic parent lane claim.

## Script Change Order

- Add `scripts/roadmap_scheduler_eval.py` first and make it the only place that computes effective candidate state.
- Update `scripts/roadmap_candidate_index.py` to render evaluator output instead of deriving status locally.
- Update `scripts/review_candidate_pool.py` next so degraded or blocked pool health is computed from evaluator output before claim mutation changes land.
- Update `scripts/roadmap_candidate_maintainer.py` so summary counts come from evaluator-backed index output.
- Update `scripts/roadmap_claim_next.py` after the read-side has stabilized, and switch selection and hard gates to evaluator-backed truth.
- Update `docs/governance/ROADMAP_BACKLOG_SCHEMA.yaml` and `docs/governance/ROADMAP_BACKLOG.yaml` with the new schema fields and the `stage1` child-slice pilot.
- Update `docs/governance/TASK_POLICY.yaml` and `scripts/governance_rules.py` last to bind claim capacity and runner capacity to separate governed keys.

## Acceptance Fixtures

- `Fixture A: expired promoted claim`
- `stage1-core-contract` has a `promoted` claim that is expired.
- Candidate index must not report it as `ready`.
- `claim-next` must report takeover eligibility via `takeover_mode=expired_promoted_takeover` or the equivalent evaluator result.
- Review pool must count it as takeover-claimable rather than healthy-ready.
- `Fixture B: two stage1 children can run in parallel`
- `stage1-source-family-group` is `claimable=false`.
- `stage1-source-family-cn` and `stage1-source-family-global` have disjoint write roots.
- Both child slices are effective claimable at the same time.
- Parent group does not appear in the ready or claimable set.
- `Fixture C: protected path gate`
- Child slice A is active.
- Child slice B planned write paths intersect A protected paths.
- Child slice B must be blocked with a protected-path conflict reason.
- `Fixture D: capacity split`
- Global roadmap cap and runner lane ceiling are configured to different values.
- `claim-next` must obey only the roadmap cap.
- Runner parallel logic must obey only the runner lane ceiling.
- Both components must remain deterministic under the same fixture.

## Acceptance Criteria

- Under the same fixture, candidate index ready set, refresh summary ready count, and `claim-next` fresh-claimable set must agree.
- A fresh claimed, promoted, or active-takeover candidate must not still be reported as `ready` by candidate index or refresh summary.
- `claim-next` must enforce active write overlap, `protected_paths`, single-writer roots, branch locks, worktree locks, and governed roadmap claim capacity.
- `review-candidate-pool` must be able to distinguish at least `ready`, `degraded`, and `blocked` based on evaluator-backed pool truth rather than stale-claim-only heuristics.
- `stage1-source-family-group` must be non-claimable, and at least two `stage1` child slices must be safe to claim concurrently when their roots are disjoint.
- The integration gate must not unlock until the expected child set satisfies the declared completion policy.
- No customer-visible contract, schema, stage6 fact behavior, or coverage registry may change as a side effect of this task.

## Risks and Review Gates

- `legacy_path_field_ambiguity`: old `reserved_paths` entries may not be classifiable without explicit mapping; any ambiguous fixture must fail fast.
- `expired_claim_truth_mismatch`: claim ledger, formal task registry, and worktree registry may disagree until evaluator becomes the single source of truth.
- `stage1_slice_root_overlap`: hidden shared files may still make child slices unsafe even if directory names look disjoint.
- `policy_migration_drift`: roadmap claim capacity and execution-lane ceiling may diverge during policy migration if wrappers still read old keys.

## Rollback Plan

- Revert backlog, schema, policy, evaluator, and wrapper script changes together as one control-plane rollback.
- Remove or revert the `stage1` child-slice materialization and restore the pre-pilot monolithic `stage1` lane entries if the pilot proves unsafe.
- Regenerate `.codex/local/roadmap_candidates/index.yaml` and `.codex/local/roadmap_candidates/summary.yaml` after rollback.
- Revert any compiled candidate artifact together with its evaluator format version; do not allow a new evaluator to read an old compiled format or an old evaluator to read a new compiled format.
- If rollback occurs after partial promotion or stale-takeover tests, clear or regenerate the affected local roadmap candidate artifacts before re-enabling automation.

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
- `branch`: `codex/TASK-GOV-052-roadmap-live-evaluator-stage1-pilot`
- `updated_at`: `2026-04-09T16:18:58+08:00`
<!-- generated:task-meta:end -->
