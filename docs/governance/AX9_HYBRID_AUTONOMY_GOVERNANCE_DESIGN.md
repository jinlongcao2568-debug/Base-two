# AX9 仓库治理与子任务自动执行设计

## 1. 文档目的

本文定义 AX9 仓库下一阶段的自动执行模型，目标是在不削弱现有治理红线的前提下，提高软件开发效率并保持仓库稳定。

本文是仓库内部治理设计文档，不替代以下已有约束：

- `AGENTS.md`
- `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`
- `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md`
- `docs/governance/TASK_POLICY.yaml`

若本文与上述文件冲突，以现有权威文档、执行手册和任务策略为准。

## 2. 设计目标

本设计同时追求以下两个目标：

1. 提高研发效率，减少重复性的人工操作。
2. 保持仓库稳定、边界清晰、状态可追溯、收口可回滚。

具体要求如下：

- 不放弃 `CURRENT_TASK.yaml` 的唯一 live 入口地位。
- 不绕开 `stage6_facts` 与现有领域边界。
- 不让自动化替代例外审批、客户可见边界判断和高风险放行。
- 把自动化重点放在“子任务执行层”，而不是“治理总控层”。

## 3. 总体原则

### 3.1 顶层治理继续人工控总

以下事项继续由治理控制面和人工判断控制：

- live current task 的激活与切换
- 顶层 coordination 任务 closeout
- 例外审批与回收
- authority-critical 改动的最终放行
- 路线图下一任务的正式激活

### 3.2 子任务执行允许自动化

以下动作应逐步自动化：

- 子任务创建
- 子任务 branch 创建
- 子任务 worktree 创建
- baseline 检查
- 子任务计划执行
- 子任务评审
- 子任务本地收口
- 子任务 worktree 清理
- runlog 与索引同步

### 3.3 默认采用标准工程方法

任何执行任务都应默认采用以下方法：

1. 先确认边界，再动手
2. 先写计划，再实现
3. 先写测试，再写生产代码
4. 出问题先做系统化调试
5. 先做需求符合性评审，再做代码质量评审

### 3.4 吸收的通用 AI 编码工作流能力

本设计有意吸收一组已经被证明有效的通用 AI 编码工作流能力，但只吸收到 AX9 适合的边界内，不原样照搬顶层全自动推进模式。

本设计正式吸收以下 5 项能力：

1. 编码前强制做设计确认与实现批准
2. 自动生成细粒度执行计划，细到文件、测试与验证步骤
3. 对代码型任务执行严格测试优先规则
4. 每个子任务使用独立执行上下文，并按“需求符合性评审 -> 代码质量评审”的顺序收口
5. 子任务具备标准化收口流程；顶层父任务只保留人工选择与批准，不做全自动推进

这 5 项能力都落在“子任务执行层”和“标准工程方法层”，不改变 AX9 顶层治理角色。

## 4. 真相源与派生索引

### 4.1 人工维护的真相源

以下文件继续作为人工维护的主真相源：

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/tasks/*.md`
- `docs/governance/runlogs/*.md`
- `docs/governance/TASK_POLICY.yaml`

含义如下：

- `CURRENT_TASK.yaml`：唯一 live task 指针
- `tasks/*.md`：任务定义、边界、目标、不做什么、测试与回滚
- `runlogs/*.md`：执行事实与测试证据
- `TASK_POLICY.yaml`：全局治理策略与自动执行规则

### 4.2 脚本同步的派生索引

以下文件应逐步从“人工真相”转为“脚本同步索引”：

- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`

原则如下：

- 人不重复维护已经存在于 task file、runlog 或 current task 的状态。
- registry 主要承担聚合、查询、恢复与调度输入作用。
- registry 出现漂移时，应以真相源为准，由脚本修复索引。

## 5. 任务分层与运行方式

### 5.1 轻量任务

适用：

- 小文档
- 小脚本
- 小测试
- 小修复

建议方式：

- 不强制独立 worktree
- 不强制并行
- 可采用 assisted 方式

### 5.2 标准任务

适用：

- 一般功能开发
- 一般缺陷修复
- 中等范围治理变更

建议方式：

- 允许自动创建子任务 branch/worktree
- 允许自动执行子任务评审与本地收口
- 默认单 lane

### 5.3 重型任务

适用：

- 治理底座改造
- 跨模块、跨阶段任务
- 业务主链任务

建议方式：

- 顶层父任务人工控总
- 具体执行拆成多个子任务自动运行
- 允许有限并行，但必须受目录冲突与 reserved path 规则控制

## 6. 自动化边界

### 6.1 自动化允许范围

自动化可以负责：

- 生成子任务执行上下文
- 创建 branch 和 worktree
- 跑 baseline 与 required tests
- 执行实现与评审
- 完成子分支本地合回父分支
- 清理子任务 worktree
- 同步索引与运行态

### 6.2 自动化禁止范围

自动化不得负责：

- 未获批准时切换 live current task
- 自动批准例外
- 自动推进路线图到下一个顶层任务
- 自动放行高风险业务边界改动
- 自动关闭顶层父任务

### 6.3 顶层与子任务的职责切分

顶层继续负责：

- 选择或批准 live task
- 审核任务边界是否合理
- 审核是否可以关账
- 审核是否可以继续路线图
- 审核高风险路径是否允许推进

子任务自动化负责：

- 设计确认
- 细粒度计划
- 执行上下文隔离
- 代码任务测试优先
- 两阶段评审
- 子任务标准化收口

因此，本设计不追求“顶层全自动推进一切”，而追求“顶层治理稳定 + 子任务执行高自动化”。

## 7. 风险分层门禁

### 7.1 低风险目录

- `docs/governance/`
- `scripts/`
- `tests/governance/`
- `tests/automation/`

特点：

- 适合先落地自动执行能力
- 可允许较高程度的自动收口

### 7.2 中风险目录

- 一般业务代码
- 不涉及主判断、对外交付、迁移、contracts 的代码

特点：

- 可自动执行
- 必须增强评审与测试门禁

### 7.3 高风险目录

- `src/stage6_facts/`
- `docs/contracts/`
- `db/migrations/`
- 客户可见字段相关逻辑
- 可售状态与覆盖等级相关逻辑
- 对外报告、导出、对外 API 相关逻辑

特点：

- 不允许端到端全自动放行
- 必须人工最终确认

## 8. 子任务工作流

子任务的推荐工作流如下：

1. 读取父任务边界和允许目录
2. 创建子任务独立执行上下文
3. 创建子任务 branch
4. 创建子任务 worktree
5. 跑 baseline 检查
6. 先做设计确认，未确认前不进入实现
7. 生成细粒度执行计划，明确文件、测试、步骤与验证方式
8. 若为代码任务，执行严格测试优先
9. 出现问题时先做系统化调试
10. 先做需求符合性评审
11. 再做代码质量评审
12. 跑 required tests
13. 本地合回父分支
14. 清理子任务 worktree
15. 更新 runlog 和 registry

### 8.0 长周期父任务模型

当一次升级需要跨多个治理阶段持续推进时，允许使用“单一顶层父任务 + 生成式子任务”的模式。

该模式的约束如下：

- 整个升级期间只保留一个 live top-level coordination task
- 所有执行任务都作为该父任务的 child execution task 生成
- 不新增 sibling top-level governance tasks
- 顶层父任务负责 phase gate、closeout 建议和人工批准
- child task 负责实现、评审、测试与标准化收口

这意味着长周期升级可以持续推进，但不会因为自动化而丢失顶层治理边界。

### 8.6 child prepare baseline 的固定语义

child prepare 的 baseline 不是“无条件复制所有顶层基线”，而是“稳定预检查 + 条件性 authority 对齐”：

1. 始终执行：
   - `python scripts/check_repo.py`
   - `python scripts/check_hygiene.py`
2. 仅当 authority 对齐所需文件在 child worktree 中齐备时，才追加：
   - `python scripts/check_authority_alignment.py`

这样做的目的有两个：

- 在完整仓库里保留 authority 对齐约束
- 在最小治理夹具或只包含治理子集的 child 环境里，不让 authority 资产缺失误伤 child prepare

### 8.1 设计确认门

子任务在以下条件未满足前，不得进入实现：

- 已明确目标与不做什么
- 已明确影响目录与禁止目录
- 已明确是否属于代码任务
- 已明确 required tests
- 已得到实现批准

### 8.2 细粒度执行计划

子任务执行计划至少应包含：

- 具体要修改的文件
- 每一步的操作目标
- 对应测试或验证动作
- 完成判断标准

计划必须足够细，使执行 agent 不依赖额外上下文也能按步骤推进。

### 8.3 代码任务测试优先

严格测试优先只对代码型任务生效，不强制用于纯文档、台账、runlog 或任务草案整理。

对代码型任务，至少遵循：

1. 先写失败测试
2. 确认测试确实失败
3. 再写最小实现
4. 再确认测试通过

### 8.4 独立执行上下文

每个子任务应使用独立执行上下文运行，目标是减少上下文污染与跨任务串扰。

在本仓语义里，独立执行上下文至少包括：

- 独立 branch
- 独立 worktree
- 独立任务边界
- 独立 runlog 事件记录

### 8.5 两阶段评审

评审顺序固定如下：

1. 需求符合性评审
2. 代码质量评审

未通过需求符合性评审时，不得跳过进入代码质量评审。

## 9. 子任务自动收口定义

“自动收口”只对子任务生效，不对顶层父任务生效。

子任务允许自动收口的前提：

- branch、task、runlog、registry 状态一致
- `required_tests` 全部通过
- 评审通过
- 无 authority、hygiene、contract 阻断
- 无 drift

自动收口的动作固定为：

1. 将子分支本地合回父分支
2. 删除子任务 worktree
3. 更新子任务状态
4. 同步 `TASK_REGISTRY.yaml`
5. 同步 `WORKTREE_REGISTRY.yaml`
6. 写入 runlog closeout 事件

默认不包含：

- 自动 push 远端
- 自动创建 PR
- 自动切换顶层任务
- 自动关闭父任务

### 9.2 child finish 前的临时镜像清理

child worktree 内会镜像一组治理账本文件，用于让 child baseline 与 workflow gate 在隔离环境中可运行。

这些镜像文件只服务于 child execution runtime，不属于 child 的真实实现成果。标准化 child finish 在执行 merge 前，必须先清理或还原以下临时镜像，再判断 child worktree 是否仍有真实未提交改动：

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- child task file mirror
- child runlog file mirror

finish 之后如果仍然存在非临时、非忽略的 dirty paths，必须阻断收口。

### 9.1 顶层父任务收口方式

顶层父任务不做全自动推进，但应具备标准化建议输出，至少向人工决策者提供：

1. 保持当前任务继续执行
2. 按条件关账并停在 idle
3. 在依赖满足且唯一时继续路线图
4. 发现阻断并停止推进

也就是说，子任务收口自动化，父任务收口建议标准化，但最终决定仍由人工批准。

## 10. 并行策略

并行只在有限范围内开启。

第一阶段规则：

- 默认单 worker
- 只有写入目录互不冲突时才允许并行
- 初始并行上限为 2 lane
- 以下路径默认禁止并行写：
  - `src/stage6_facts/`
  - `docs/contracts/`
  - `db/migrations/`

## 11. 推荐实施顺序

### 第一阶段：控制面减重

目标：

- 降低 registry 漂移
- 明确真相源与索引职责

动作：

- 明确 `CURRENT_TASK`、task file、runlog 的主真相地位
- 将 `TASK_REGISTRY.yaml` 与 `WORKTREE_REGISTRY.yaml` 改为脚本同步索引
- 增加 drift check

### 第二阶段：子任务环境自动准备

目标：

- 提高执行效率

动作：

- 自动 child task context
- 自动 branch/worktree
- 自动 baseline
- 自动 runlog/registry 同步
- 自动设计确认门
- 自动细粒度计划生成

### 第三阶段：子任务自动收口

目标：

- 形成受控闭环

动作：

- 代码任务测试优先门
- fresh child execution context
- 自动评审
- 先 spec review 再 quality review
- 自动 finish child branch
- 自动 cleanup

### 第四阶段：有限并行

目标：

- 在不破坏稳定性的前提下提高吞吐量

动作：

- 只开放低冲突目录并行
- 保持高风险路径人工兜底

## 11.1 与 `TASK-GOV-018` 的实施映射

当前这套设计首先落在 `TASK-GOV-018` 上，并采用以下四段 gate：

1. `truth_split`
   - 明确 `CURRENT_TASK.yaml`、task files、runlogs 为主真相源
   - 将 `TASK_REGISTRY.yaml`、`WORKTREE_REGISTRY.yaml` 视为可重建索引
   - 提供 `reconcile-ledgers` 修复路径
2. `child_preparation`
   - child execution context
   - child branch/worktree
   - stable baseline checks
   - prepared state 写回
3. `child_workflow_gates`
   - design confirmation
   - detailed execution plan
   - code-task test-first
   - ordered review gates
4. `child_finish_and_stability`
   - standardized child finish workflow
   - parent remains manual
   - rerun / blocked / edge-path testing

`TASK-GOV-018` 完成后，AX9 将具备“顶层治理人工控总、child execution 自动化收口”的稳定基础，但仍不会启用顶层 full autopilot 或多 lane rollout。

## 12. 成功标准

当以下条件同时成立时，认为本设计落地成功：

1. live current task 仍然唯一且清晰
2. 顶层治理状态不因自动化而漂移
3. 子任务可自动创建 branch/worktree 并稳定运行
4. 子任务可自动完成本地收口且不误伤父任务
5. registry 能由真相源稳定重建
6. 高风险目录仍保留人工最终放行
7. 子任务进入实现前必须经过设计确认
8. 子任务能生成细粒度执行计划
9. 代码任务能执行测试优先约束
10. 子任务评审顺序稳定为“需求符合性 -> 代码质量”

## 13. 明确不做的事

- 不把整个仓库改造成完全自动推进
- 不取消 `CURRENT_TASK.yaml` 的唯一入口地位
- 不让自动化取代 authority-critical 判断
- 不为了自动化便利而修改领域边界
- 不把现有治理体系让位给通用 AI 编码流程

## 14. 当前最优落地点

从收益和代价平衡看，最适合先落地的是：

1. registry 从人工维护转为脚本同步
2. 子任务级 branch/worktree 自动准备
3. 子任务级本地自动收口

以上三项能够在不碰业务主链代码的情况下，先拿到最大效率收益，并保持治理稳定。

## 15. TASK-GOV-018 Total Upgrade Rebaseline (2026-04-06)

This appendix records the governance decision to promote `TASK-GOV-018` into the single top-level parent task for the full upgrade.

- The parent task remains the only live top-level coordination task until all six internal gates complete.
- Top-level closeout changes from `manual` to `ai_guarded`.
- `continue-current` may close the current top-level task to `idle` but must not activate a successor.
- `continue-roadmap` and `automation_runner --continue-roadmap` may activate a successor only when successor uniqueness, dependency satisfaction, and boundary clarity are all satisfied.
- Governed child workflow scope expands beyond governance-only paths into `docs/contracts/`, `src/shared/contracts/`, `src/stage7_sales/`, `src/stage8_contact/`, `src/stage9_delivery/`, `db/migrations/`, `tests/contracts/`, `tests/integration/`, and `tests/stage7/8/9/`.
- `TASK-BIZ-001`, `TASK-BIZ-002`, `TASK-BIZ-003`, `TASK-SOAK-001`, and `TASK-GRAD-001` are absorbed into `TASK-GOV-018` and must not be reactivated as sibling top-level tasks.
- `src/stage1_orchestration/` through `src/stage6_facts/` remain reserved for this upgrade, and stage7-stage9 runtime must only consume `project_fact` without write-back.
- The migration baseline for stage7-stage9 is explicitly stateless in this upgrade.
