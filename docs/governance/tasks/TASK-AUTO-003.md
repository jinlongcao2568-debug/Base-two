# TASK-AUTO-003 Stage1-Stage6 业务自动推进与并行评审层

## 任务基线

- 任务编号：`TASK-AUTO-003`
- 任务类型：`coordination`
- 执行模式：`shared_coordination`
- 当前状态：`review`
- 所属阶段：`automation-business-autopilot-stage1-stage6-v1`
- 任务分支：`feat/TASK-AUTO-003-business-autopilot-stage1-stage6`
- 任务大小：`heavy`
- 自动化模式：`manual`
- 拓扑：`single_worker`
- worker 状态：`review_pending`

## 主目标

- 将 `continue-roadmap` 从治理 successor 扩展到 `stage1-stage6` 业务 successor 生成与激活。
- 将业务自动推进限定为 `baseline + contracts + task package` 三类正式图纸输入。
- 建立依赖感知并行与 review bundle 自动评审，允许 child lane 在硬门禁通过后自动关账。
- 明确 `stage7-stage9` 在本阶段保持 `deferred_manual`，拒绝自动生成和自动激活。

## 不做什么

- 不自动生成 `stage7-stage9` 业务任务。
- 不直接实现具体业务功能代码，只补业务自动推进调度层。
- 不新增第二套路线图、第二套任务台账或第二套事实面。

## 允许修改目录

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `docs/contracts/`
- `tests/integration/`

## 拟修改文件清单

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`
- `docs/contracts/`
- `tests/integration/`

## planned test paths

- `tests/governance/`
- `tests/automation/`
- `tests/contracts/`
- `tests/integration/`

## reserved paths

- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `tests/stage7/`
- `tests/stage8/`
- `tests/stage9/`

## Narrative Assertions

- `narrative_status`: `done`
- `closeout_state`: `closed`
- `blocking_state`: `clear`
- `completed_scope`: `closed`
- `remaining_scope`: `none`
- `next_gate`: `closed`
## Task Baseline

- `task_id`: `TASK-AUTO-003`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `status`: `done`
- `stage`: `automation-business-autopilot-stage1-stage6-v1`
- `branch`: `feat/TASK-AUTO-003-business-autopilot-stage1-stage6`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `heavy`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `lane_count`: `1`
- `lane_index`: `null`
- `parallelism_plan_id`: `null`
- `review_bundle_status`: `not_applicable`
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-AUTO-003-business-autopilot-stage1-stage6`
- `updated_at`: `2026-04-05T19:06:16+08:00`
<!-- generated:task-meta:end -->
