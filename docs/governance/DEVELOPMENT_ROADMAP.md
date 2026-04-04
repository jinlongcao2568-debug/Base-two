---
current_phase: automation-roadmap-continuation-v1
current_task_id: TASK-AUTO-002
next_recommended_task_id: null
advance_mode: explicit_or_generated
auto_create_missing_task: true
branch_switch_policy: create_or_switch_if_clean
priority_order:
  - governance_automation
  - authority_chain
  - business_automation
business_automation_enabled: false
stage_establishment:
  stage1: not_established
  stage2: not_established
  stage3: not_established
  stage4: not_established
  stage5: not_established
  stage6: not_established
  stage7: not_established
  stage8: not_established
  stage9: not_established
automation_foundation: in_progress
---

# AX9S Development Roadmap

## Current Task

- `TASK-AUTO-002`: implement the continuation control plane so automation can resume the live task or advance to a uniquely valid successor without guessing.

## Recently Closed

- `TASK-GOV-001`: closed authority drift, formalized contracts and handoff assets, expanded minimum regression coverage, and hardened the governance control plane.
- `TASK-AUTO-001`: landed the first automation control-plane baseline and closed the shared coordination setup for `automation-control-plane-v1`.

## Current Phase Goal

- Add formal `continue-current` and `continue-roadmap` semantics to the live governance control plane.
- Let automation close a review-ready current task, resolve or generate the next governance successor, and activate it only when the branch/worktree/dependency rules are satisfied.
- Keep roadmap advancement limited to governance scheduling gaps in v1; do not auto-pick new business implementation work.

## Explicitly Out Of Scope

- Do not auto-generate stage7-stage9 business tasks.
- Do not relax the clean-worktree requirement before switching or creating a successor branch.
- Do not create a second task ledger or second roadmap source.

## Exit Criteria For Current Phase

- `task_ops continue-current` keeps or reactivates the live task without drifting current-task state.
- `task_ops continue-roadmap` closes a review-ready live task and activates a unique successor only when roadmap policy, dependency, boundary, and branch rules are satisfied.
- `automation_runner.py once --continue-roadmap` can drive the same flow after gates pass.
- The roadmap frontmatter carries machine-readable continuation policy fields and the task policy carries the matching successor blueprint.

## Next Candidate

- v1 successor generation is limited to governance automation gaps. If no explicit or generated governance successor is available, automation must stop and report the gap.
