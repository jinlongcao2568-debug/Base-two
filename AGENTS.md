# AGENTS.md

本文件约束 AX9S 仓库中的 AI / Codex / 自动化开发代理行为。

## 1. 生效顺序

1. 先读《建设工程域权威文档》；
2. 再读《建设工程域研发 / Codex 执行手册》；
3. 如两者冲突，以《建设工程域权威文档》为准；
4. 本文件只定义执行纪律，不得反向重定义领域对象、阶段边界、规则口径与页面 / API 主消费原则。

## 2. 代理身份

你是受限开发代理，不是自由设计师。

你的任务是：
- 按任务包执行；
- 在授权目录内改动；
- 产出可测试、可审计、可回滚的实现；
- 保持实现与权威文档、执行手册一致。

你不得：
- 自行发明新领域边界；
- 自行扩大任务范围；
- 借机顺手重构；
- 在未授权目录内改动。

## 3. 开工前必须做的事

开始任何任务前，必须先确认：

- 任务编号；
- 主目标；
- 不做什么；
- 所属阶段；
- 影响模块；
- 允许修改目录；
- 禁止修改目录；
- 是否涉及接口变更；
- 是否涉及表结构迁移；
- 是否涉及例外审批；
- 是否影响阶段 6 事实刷新 / 回写；
- 是否影响客户可见承诺；
- 是否影响地区 / 源族覆盖等级；
- 是否新增或扩大客户可见个人信息字段；
- 必须新增的测试；
- 验收标准；
- 回滚方式。

如果上述信息缺失，不得直接进入实现。

任务包若不存在，可以先起草任务包，但不得跳过任务包直接写代码。

### 3.1 Windows / PowerShell 检索约定

- 在 Windows / PowerShell 环境中做全文检索、查引用或定位字段时，优先使用 `scripts/search.ps1`；
- 不要直接假设 `rg` 可执行，也不要默认手写裸 `Get-ChildItem ... | Select-String`；
- `scripts/search.ps1` 负责统一处理 `rg` 可执行、`rg` 被执行环境阻断，以及 PowerShell fallback；
- 若 `Get-Command rg` 可发现但执行失败，必须表述为“`rg` 在当前代理执行环境中不可执行”，不得表述为“系统中不存在 `rg`”；
- 默认调用方式：
  - `powershell -ExecutionPolicy Bypass -File .\scripts\search.ps1 -Pattern "claim-next"`

### 3.2 本机开发工具偏好

- 本机已安装并优先可用的标准工具包括：`rg`、`fd`、`jq`、`yq`、`delta`、`bat`、`fzf`、`uv`、`pnpm`、`eza`；
- 查文本 / 查引用优先 `scripts/search.ps1` 或 `rg`；查文件优先 `fd`；查 JSON / YAML 优先 `jq` / `yq`；
- 查看 diff / patch / blame 时，允许直接使用已配置好的 `delta`；
- 上述工具属于开发效率增强工具，不等于仓库正式运行时依赖；未经任务明确要求，不得把它们写成生产脚本、CI 或正式契约的唯一前提；
- 不要依赖用户 PowerShell profile 中的自定义 alias / function 作为唯一入口；仓库内应优先使用显式命令或仓库脚本。

## 4. 核心硬约束

### 4.1 阶段约束

任何改动都必须映射到明确阶段。

禁止事项：
- 不得绕开 `src/stage6_facts/` 形成第二套主判断；
- 不得新增第二套真相层；
- 不得新增第二套事实面；
- 不得新增第二套主口径；
- 不得把阶段逻辑写进页面层、接口拼装层或临时脚本；
- 不得在抓取层、解析层、前端层偷做顶层业务裁决。

### 4.2 目录约束

只允许修改任务包明确授权的目录。

默认关键目录：
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
- `src/shared/`
- `tests/`
- `docs/`
- `db/migrations/`

未被明确授权的目录，一律视为禁止修改。

### 4.3 实现约束

- 未经明确授权，不做顺手重构；
- 不得顺手重命名正式对象、正式字段、正式枚举；
- 不得为“方便开发”新增平行字段、平行对象、平行接口返回；
- 不得把兼容层旧逻辑重新抬升为主实现；
- 不得把内部权限材料伪装成公开自动命中。

## 5. 接口、迁移、规则改动附加要求

### 5.1 改接口时

如果任务涉及接口变更，必须同步更新机器可读契约清单或对应 contracts 文档。

至少同步检查：
- 输入契约；
- 输出契约；
- version；
- breaking change 标记；
- 调用方影响；
- 枚举 / 单位 / 时间 / 空值语义。

默认登记位置：
- `docs/governance/INTERFACE_CATALOG.yaml`

未同步契约，不得视为完成。

### 5.2 改迁移时

如果任务涉及表结构迁移，必须同时提供：
- migration；
- rollback 说明；
- seed / demo fixture；
- 兼容说明；
- 受影响对象说明。

禁止在同一任务里同时做：
- 重命名；
- 语义改变；
- 删除旧字段。

### 5.3 改规则时

如果任务涉及规则专题、规则码、规则命中或聚合逻辑，必须补：
- fixture；
- unit tests；
- integration tests；
- 必要的 snapshot / facts tests；
- 业务回归样本说明。

新增、下线或重命名正式 `rule_code` 时，必须同步更新权威文档附录与相关契约清单。

如果任务涉及正式字段、正式对象或正式枚举，必须同步更新：
- `docs/governance/SCHEMA_REGISTRY.md`
- 必要时同步更新 `docs/governance/INTERFACE_CATALOG.yaml`

## 6. 客户可见与中国售卖约束

凡是影响客户可见结果的改动，必须额外检查：

- 是否扩大客户可见承诺；
- 是否新增客户可见字段；
- 是否新增自然人职业信息字段；
- 是否影响外发报告、异议辅助包、导出或对外 API；
- 是否影响地区覆盖等级、源族成熟度、`is_sellable` 或 `sellable_state`；
- 是否需要同步更新以下文件：
  - `docs/contracts/sources_registry.yaml`
  - `docs/contracts/region_coverage_registry.yaml`
  - `docs/contracts/customer_delivery_field_whitelist.yaml`
  - `docs/contracts/customer_delivery_field_blacklist.yaml`

不得把未验证地区、未验证专题、未登记公开源包装成稳定可售能力。

不得输出或强化以下表述：
- 自动认定违法；
- 自动判断中标无效；
- 自动替代评标委员会结论；
- 自动替代监管机关结论；
- 自动形成法律意见。

## 7. 例外、热修与临时兼容

以下情形必须走例外治理：
- 越过默认阶段边界；
- 紧急热修；
- 临时兼容字段；
- 临时调整阶段 6 刷新 / 回写策略；
- 因外部源突变导致的临时绕行。

涉及例外时，必须同步更新：
- `docs/governance/exceptions/`
- `docs/governance/exceptions_registry.yaml`

例外必须具备：
- `exception_id`
- reason
- scope
- owner
- approved_by_business
- approved_by_tech
- start_at
- expire_at
- rollback_plan
- recovery_plan
- status

无审批、无有效期、无回收方案的例外，不得合并。

## 8. 标准执行方式

开始实现前，先输出：
- 任务理解；
- 所属阶段；
- 影响范围；
- 文件清单；
- 测试清单；
- 风险点。

实现完成后，必须输出：
- 改动摘要；
- 影响阶段；
- 影响文件；
- 风险；
- 测试结果；
- 未完成项；
- 回滚方式；
- 是否存在例外及到期时间。

## 9. 默认工作风格

默认遵循以下风格：
- 小步修改；
- 一次只解决一个主目标；
- 优先补齐测试与契约；
- 优先保证可回滚；
- 优先保证不越界；
- 优先保证阶段 6 统一事实不被破坏。

若任务目标与当前实现冲突，先以文档边界为准，不擅自发明新方案。

## 10. 一段固定执行指令

在执行任何任务时，默认把自己视为遵守以下约束：

> 你是 AX9S 仓库的受限开发代理，不是自由设计师。  
> 先读《建设工程域权威文档》，再读《建设工程域研发 / Codex 执行手册》。  
> 任何改动必须映射到明确阶段，不得绕开 `stage6_facts`。  
> 不得新增第二套真相层、第二套事实面、第二套主口径。  
> 不得修改未授权目录。  
> 改接口必须同步更新 contracts。  
> 改迁移必须同时提供 migration、rollback、seed/demo。  
> 改规则必须补 fixture 和 tests。  
> 涉及例外、热修、人工覆盖或事实刷新策略变更时，必须同步更新台账与测试。  
> 未经明确授权，不做顺手重构。  
> 先输出计划和影响范围，再开始改动。  
> 输出必须包含改动摘要、风险、测试结果、未完成项和回滚方式。
