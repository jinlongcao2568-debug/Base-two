# TASK-GOV-027 Child closeout 自愈与 governance mirror 收口

## Task Baseline

- `task_id`: `TASK-GOV-027`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `status`: `review`
- `stage`: `governance-local-multi-agent-platformization-v1`
- `branch`: `feat/TASK-GOV-027-child-closeout-mirror`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `2`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `pending`
## Primary Goals

- Make governed child execution self-healing when mirrored governance files or missing worktree paths would otherwise leave false blocked states.
- Ensure child execution contexts always admit mirrored governance files as legal planned writes.
- Keep the lane isolated to child closeout, governance mirror, repo checks, and handoff parsing.
- Fold the approved `20 lane` expansion into this same lane because it changes governance runtime ceilings and the repo/task checks that enforce them.

## Explicitly Not Doing

- Do not modify lease semantics, lifecycle closeout semantics, or `automation_runner.py`.
- Do not change `tests/automation/`.
- Do not touch contracts, migrations, or product-stage source code.

## Allowed Dirs

- `docs/governance/`
- `docs/governance/TASK_POLICY.yaml`
- `docs/governance/AUTOMATION_OPERATING_MODEL.md`
- `scripts/child_execution_flow.py`
- `scripts/task_worktree_ops.py`
- `scripts/governance_repo_checks.py`
- `scripts/governance_rules.py`
- `scripts/governance_runtime.py`
- `scripts/task_handoff.py`
- `tests/governance/fixture_payloads.py`
- `tests/governance/policy_fixture_payloads.py`
- `tests/governance/test_check_repo.py`
- `tests/governance/test_parallel_closeout_pipeline.py`
- `tests/governance/test_authority_alignment.py`
- `tests/governance/test_task_ops.py`

## Planned Write Paths

- `docs/governance/TASK_POLICY.yaml`
- `docs/governance/AUTOMATION_OPERATING_MODEL.md`
- `scripts/child_execution_flow.py`
- `scripts/task_worktree_ops.py`
- `scripts/governance_repo_checks.py`
- `scripts/governance_rules.py`
- `scripts/governance_runtime.py`
- `scripts/task_handoff.py`
- `tests/governance/fixture_payloads.py`
- `tests/governance/policy_fixture_payloads.py`
- `tests/governance/test_check_repo.py`
- `tests/governance/test_parallel_closeout_pipeline.py`
- `tests/governance/test_authority_alignment.py`
- `tests/governance/test_task_ops.py`

## Planned Test Paths

- `tests/governance/test_check_repo.py`
- `tests/governance/test_parallel_closeout_pipeline.py`
- `tests/governance/test_authority_alignment.py`
- `tests/governance/test_task_ops.py`

## Required Tests

- `python scripts/check_hygiene.py`
- `python scripts/check_repo.py`
- `python scripts/check_authority_alignment.py`
- `pytest tests/governance/test_check_repo.py tests/governance/test_parallel_closeout_pipeline.py tests/governance/test_authority_alignment.py tests/governance/test_task_ops.py -q`

## Reserved Paths

- `src/`
- `docs/contracts/`
- `db/migrations/`
- `tests/integration/`
## Narrative Assertions

- `narrative_status`: `review`
- `closeout_state`: `candidate_ready`
- `blocking_state`: `clear`
- `completed_scope`: `ready_for_review`
- `remaining_scope`: `closeout_only`
- `next_gate`: `closeout_decision`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `review`
- `task_kind`: `execution`
- `execution_mode`: `isolated_worktree`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_task`
- `lane_count`: `3`
- `lane_index`: `2`
- `parallelism_plan_id`: `plan-TASK-GOV-025-3`
- `review_bundle_status`: `pending`
- `reserved_paths`: `src/, docs/contracts/, db/migrations/, tests/integration/`
- `branch`: `feat/TASK-GOV-027-child-closeout-mirror`
- `updated_at`: `2026-04-06T20:27:23+08:00`
<!-- generated:task-meta:end -->
