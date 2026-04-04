# TASK-AUTO-002 路线图自动推进编排层

## Task Baseline

- `task_id`: `TASK-AUTO-002`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `review`
- `stage`: `automation-roadmap-continuation-v1`
- `branch`: `feat/TASK-AUTO-002-roadmap-autopilot-continuation`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
## Primary Goals

- Add formal `continue-current` semantics to the control plane so the live task can be resumed without guessing.
- Add formal `continue-roadmap` semantics so a review-ready current task can close and advance to one unique successor.
- Make successor resolution machine-readable from roadmap policy, task policy blueprints, and live capability state.
- Extend the automation runner so the same roadmap continuation flow can run after repository gates.

## Explicitly Not Doing

- No automatic business-stage task generation in stage7-stage9.
- No second roadmap or second task ledger.
- No relaxation of the clean-worktree requirement before branch switching.

## Allowed Dirs

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Write Paths

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

## Planned Test Paths

- `tests/governance/`
- `tests/automation/`

## Required Tests

- `python scripts/check_authority_alignment.py`
- `python scripts/check_repo.py`
- `python scripts/check_hygiene.py`
- `pytest tests/governance -q`
- `pytest tests/automation -q`
- `pytest -q`

## Acceptance

- `task_ops continue-current` behaves correctly for `doing`, `paused`, `blocked`, and `review/done`.
- `task_ops continue-roadmap` closes a review-ready current task, selects or generates a unique valid successor, and activates it.
- `automation_runner.py once --continue-roadmap` drives the same flow after the normal gates pass.
- Roadmap continuation policy and task blueprints are machine-readable and validated by repository gates.

## Rollback

- Revert the governance scripts, task policy, roadmap, capability map, and continuation tests changed under this task.
- If continuation control must be abandoned, restore `CURRENT_TASK.yaml`, `TASK_REGISTRY.yaml`, and `WORKTREE_REGISTRY.yaml` to the previous committed state and reactivate the prior manual task flow.

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
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `review_pending`
- `topology`: `single_worker`
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-AUTO-002-roadmap-autopilot-continuation`
- `updated_at`: `2026-04-04T22:26:50+08:00`
<!-- generated:task-meta:end -->
