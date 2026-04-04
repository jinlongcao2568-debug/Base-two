---
current_phase: automation-control-plane-v1
current_task_id: TASK-AUTO-001
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

## 当前任务

- `TASK-AUTO-001`：把自动化控制面稳定落到 `main`，并引入按任务大小自动分流的一期控制面。

## 当前阶段目标

- 一期的目标不是让系统自己决定做什么，而是让系统能可靠执行“已经定义清楚的任务”。
- 建立主干唯一可信的自动化控制面。
- 固化 `micro / standard / heavy` 三档任务模型。
- 让 worker 主动回报状态，让协调器自动轮询、自动收口子任务、自动重试清理 worktree。
- 把治理检查、代码整洁度检查和自动化烟雾测试纳入仓库。

## 当前不做

- 不自动切换到下一个父任务。
- 不自动删除父任务分支或治理分支。
- 不把业务阶段开发混入本轮治理任务。
- 不宣称已经具备全天无人值守能力。

## 自动化一期范围

- 主干治理入口：
  - `docs/governance/CURRENT_TASK.yaml`
  - `docs/governance/TASK_REGISTRY.yaml`
  - `docs/governance/WORKTREE_REGISTRY.yaml`
  - `docs/governance/DEVELOPMENT_ROADMAP.md`
- 自动化治理资产：
  - `docs/governance/MODULE_MAP.yaml`
  - `docs/governance/TEST_MATRIX.yaml`
  - `docs/governance/CODE_HYGIENE_POLICY.md`
  - `docs/governance/AUTOMATION_OPERATING_MODEL.md`
- 自动化脚本：
  - `scripts/governance_lib.py`
  - `scripts/task_ops.py`
  - `scripts/check_repo.py`
  - `scripts/check_hygiene.py`
  - `scripts/automation_runner.py`
- 自动化测试：
  - `tests/governance/`
  - `tests/contracts/`
  - `tests/automation/`

## 任务大小策略

- `micro`：预计 `<=45` 分钟，只改 `1` 个模块，不触碰共享保留区；`planned_write_paths` 建议 `<=5`，硬上限 `8`；不建 worktree。
- `standard`：预计 `45` 分钟到 `4` 小时，改 `1-2` 个相邻模块；默认单 worker，仅在风险隔离、实验性实现或需要随时丢弃时才建 `1` 个 worktree。
- `heavy`：预计 `>4` 小时，或存在 `2` 个以上明确独立写域；只有 `planned_write_paths`、`required_tests`、`reserved_paths` 都能拆清时，才允许进入父任务 + 最多 `2` 个 execution worktree 的并行模式。

## 自动化模式规则

- `manual`：治理升级、共享保留区冲突、拆分条件不清晰或显式要求人工控制。
- `assisted`：边界清楚的 `micro / standard` 任务，可自动执行检查和准备动作，但保留人工 review。
- `autonomous`：模块地图完整、测试完备、边界清楚且满足并行前提的任务，可自动推进并主动回报。

## runner 行为门禁

- `manual`：协调器只执行 `check_repo.py`、`check_hygiene.py` 和 `cleanup-orphans`，跳过 worktree 准备与 `auto-close-children`。
- `assisted`：协调器可准备 execution worktree，但不会自动关闭子任务；子任务停在 `review_pending`。
- `autonomous`：协调器可准备 execution worktree，并在 required tests 满足后自动执行 `auto-close-children`。

## 下一阶段候选

- `TASK-AUTO-002`：长时自动化运行、父任务自动关账和恢复策略。

## 说明

- `main` 是自动化协调器唯一可信的控制面来源。
- worker 必须主动回报状态，协调器轮询只作为兜底。
- 第一期自动化目标是稳定运行 `2-4` 小时，不以全天无人值守为验收口径。
