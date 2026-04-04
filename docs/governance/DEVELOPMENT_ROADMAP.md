---
current_phase: authority-consistency-hardening
current_task_id: TASK-GOV-001
next_recommended_task_id: null
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

- `TASK-GOV-001`: close authority drift across governance entry files, contracts assets, tests, and downstream execution documents before any next automation phase is opened.

## Recently Closed

- `TASK-AUTO-001`: landed the first automation control-plane baseline and closed the shared coordination setup for `automation-control-plane-v1`.

## Current Phase Goal

- Make the current repository obey one live execution source at a time.
- Upgrade contracts from registry-only assets to professional contracts with schema, example, and field semantics.
- Add a real `stage3 -> stage4 -> stage6` integration proof so stage establishment is backed by downstream consumption.
- Expand README, MVP, test matrix, and governance indexes from seed-level text into execution-grade documents.

## Explicitly Out Of Scope

- Do not rename the formal stage directories.
- Do not move `docs/contracts/` to the repository root.
- Do not expand into new business-stage implementation work.

## Exit Criteria For Current Phase

- `CURRENT_TASK.yaml`, `TASK_REGISTRY.yaml`, `WORKTREE_REGISTRY.yaml`, roadmap, task file, and runlog stay fully aligned for the live task.
- `docs/contracts/` contains registry assets, schemas, examples, and field semantics for the stage-6 `project_fact` contract.
- `tests/integration/` stops being empty and proves the minimum `stage3 -> stage4 -> stage6` chain.
- README and downstream governance/product documents stop using seed or skeleton wording for live controls.
- `python scripts/check_authority_alignment.py` reports every authority and automation readiness score at `>=95`.
- The fixed batch-5 validation sequence passes twice in a row without score drift.

## Next Candidate

- No next task will be activated automatically. The next task must be created explicitly after `TASK-GOV-001` reaches `review`.
