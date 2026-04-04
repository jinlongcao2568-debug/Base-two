# TASK-AUTO-001 自动化开发一期：主干控制面 + 按任务大小自动分流

## 任务基线

- 任务编号：`TASK-AUTO-001`
- 任务类型：`coordination`
- 执行模式：`shared_coordination`
- 当前状态：`doing`
- 所属阶段：`automation-control-plane-v1`
- 任务分支：`feat/TASK-AUTO-001-automation-control-plane`
- 任务大小：`standard`
- 自动化模式：`manual`
- 拓扑：`single_worker`

## 主目标

- 把自动化控制面正式落到 `main`。
- 固化 `micro / standard / heavy` 三档任务模型。
- 增加模块地图、测试矩阵和代码整洁度门禁。
- 让 worker 具备主动回报、blocked 登记、完成回报和 cleanup 状态。
- 提供第一版协调器 runner，用于轮询、自动收口子任务和重试清理 worktree。
- 本轮补齐 `automation_mode` runner 门禁与 `heavy reserved_paths` 拆分条件。

## 不做什么

- 不开发新的业务阶段逻辑。
- 不自动切换到下一个父任务。
- 不自动删除父任务分支或治理分支。
- 不宣称已经具备全天无人值守能力。
- 不修改 `src/stage*` 或 `src/domain/engineering/*` 业务源码。

## 允许修改目录

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- `docs/governance/MODULE_MAP.yaml`
- `docs/governance/TEST_MATRIX.yaml`
- `docs/governance/CODE_HYGIENE_POLICY.md`
- `docs/governance/AUTOMATION_OPERATING_MODEL.md`
- `docs/governance/tasks/`
- `docs/governance/runlogs/`
- `scripts/`
- `tests/governance/`
- `tests/contracts/`
- `tests/automation/`

## 禁止修改目录

- `src/stage1_orchestration/`
- `src/stage2_ingestion/`
- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage5_reporting/`
- `src/stage6_facts/`
- `src/stage7_sales/`
- `src/stage8_contact/`
- `src/stage9_delivery/`
- `src/domain/engineering/`
- `docs/contracts/`
- `db/migrations/`

## 拟修改文件清单

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/AUTOMATION_OPERATING_MODEL.md`
- `docs/governance/tasks/TASK-AUTO-001.md`
- `docs/governance/runlogs/TASK-AUTO-001-RUNLOG.md`
- `scripts/governance_lib.py`
- `scripts/task_ops.py`
- `scripts/check_repo.py`
- `scripts/automation_runner.py`
- `tests/governance/`
- `tests/contracts/`
- `tests/automation/`

## planned test paths

- `tests/governance/`
- `tests/contracts/`
- `tests/automation/`

## 是否涉及接口变更

- 否，不修改业务接口契约。

## 是否涉及表结构迁移

- 否。

## 是否涉及例外审批

- 否。

## 是否影响阶段 6 事实刷新 / 回写

- 否，本任务只处理治理与执行控制面。

## 是否影响客户可见承诺

- 否。

## 是否影响地区 / 源族覆盖等级

- 否。

## 是否新增或扩大客户可见个人信息字段

- 否。

## 必须新增的测试

- `tests/governance/`：验证 `automation_mode` runner 门禁、`heavy reserved_paths` 拓扑判断和 split guard。
- `tests/contracts/`：验证 `reserved_paths` 已进入 `TASK_REGISTRY.yaml` 和 `CURRENT_TASK.yaml` schema。
- `tests/automation/`：验证 `manual / assisted / autonomous` 三档 runner 行为。

## 验收标准

- `automation_mode` 真正参与 `automation_runner.py` 的自动推进门禁。
- `reserved_paths` 成为任务 schema 正式字段，并进入 `heavy` 拓扑判断与 split guard。
- `manual / assisted / autonomous` 三档 runner 行为均有自动化测试覆盖。
- 治理、合同、自动化回归测试通过。

## 回滚方式

- 回退本任务引入的治理文件、脚本和测试变更。
- 将 `CURRENT_TASK.yaml`、`TASK_REGISTRY.yaml` 恢复到本任务之前的状态。

<!-- generated:task-meta:start -->
## Generated Metadata

- `status`: `done`
- `task_kind`: `coordination`
- `execution_mode`: `shared_coordination`
- `size_class`: `standard`
- `automation_mode`: `manual`
- `worker_state`: `completed`
- `topology`: `single_worker`
- `reserved_paths`: `[]`
- `branch`: `feat/TASK-AUTO-001-automation-control-plane`
- `updated_at`: `2026-04-04T14:04:17+08:00`
<!-- generated:task-meta:end -->
