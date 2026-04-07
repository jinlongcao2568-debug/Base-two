# AX9S 建设工程域研发 / Codex 执行手册（中国落地售卖增强版，V1.5 对齐版）

- 文档 ID：AX9S-CE-DEVMANUAL-CN-V1_5
- 状态：EFFECTIVE
- 文档定位：建设工程域仓库执行规范与 AI / Codex 操作手册
- 适用范围：AX9S 仓库中的建设工程域研发、测试、联调、迁移、回滚、审查、AI / Codex 执行任务
- 唯一上游权威源：`docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.5_全量规则码版.md`
- 责任边界：本文只规定“怎么在仓库里动手”，不重定义建设工程域的阶段边界、正式对象、规则边界、页面 / API 主消费原则、客户交付边界或可售边界
- 冲突规则：如本文与权威文档冲突，以权威文档为准

---

## 1. 文档目标与边界

本文档用于回答以下问题：

1. 研发与 AI / Codex 在开始任务前必须完成哪些准备；
2. 一个任务包至少应包含哪些字段；
3. 哪些目录、文档、接口、迁移、测试属于允许修改范围；
4. 如何防止越界改动、防止文档与实现漂移、防止治理台账失真；
5. 何时必须同步契约、字段语义、对象级交付矩阵、字段策略字典、覆盖登记表和例外台账；
6. 何时必须停止实施并先补治理信息。

本文档不回答以下问题：

- 建设工程域九阶段如何定义；
- `project_base`、`rule_hit`、`project_fact` 等正式对象如何定义；
- 哪些规则码属于正式规则码；
- 哪些结论可以自动命中，哪些只能形成线索、观察或请求核验；
- 客户交付、售卖范围、公开证据边界的制度定义。

这些问题只由权威文档回答。

## 2. 生效规则与单一真源

### 2.1 单一真源

本仓库中，建设工程域的单一领域真源固定为：

- [权威文档](D:/Base%20One/Base-two/AX9/docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.5_全量规则码版.md)

执行动作、目录边界、任务纪律、CI 门禁、例外回收、输出模板的单一执行真源固定为本文。

### 2.2 基本执行原则

任何建设工程域任务都必须遵守以下原则：

1. 先读权威文档，再读当前任务包与 runlog；
2. 任何改动必须映射到明确阶段；
3. 不得绕开阶段 6 建第二套主判断；
4. 不得新增第二套真相层、第二套事实面、第二套主口径；
5. 未经任务包明确授权，不做顺手重构；
6. 输出必须可测试、可审计、可回滚、可追溯；
7. 涉及例外、热修、临时兼容、客户可见字段变更、可售状态变更时，必须同步台账；
8. 权威文档定义领域边界，本文只定义仓库动作。

### 2.3 当前基线模式

当前基线模式固定为：

- `authority_mode = V1.5_single_source`
- `history_mode = no_legacy_carry_forward`

含义如下：

1. 当前建设工程域总文档只以 V1.5 为准；
2. 新建开发手册、任务包、专项说明默认不继承旧版历史叙述；
3. 若确需引用旧文档，只能作为归档材料，不得作为现行执行依据；
4. 未在 V1.5 中保留的旧口径，不得通过旧执行手册、旧注释或旧任务备注复活。

## 3. 开工前固定动作

开始任何任务前，必须先确认以下信息：

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

若上述信息缺失，不得直接进入实现。

## 4. 任务包与治理台账

### 4.1 任务包最小要求

每个任务至少要有：

- `CURRENT_TASK.yaml` 中的当前任务指针；
- `TASK_REGISTRY.yaml` 中的任务主记录；
- `WORKTREE_REGISTRY.yaml` 中的工作区记录；
- 任务文件；
- runlog；
- 必要时的 handoff。

### 4.2 当前任务是唯一执行入口

`docs/governance/CURRENT_TASK.yaml` 是唯一执行入口。

规则如下：

1. 若 `current_task_id` 为空，不进入实现；
2. 若任务包已创建但未激活，不进入实现；
3. 若当前分支与当前任务分支不一致，先处理治理漂移；
4. 若当前工作区存在不属于当前任务范围的脏文件，先解释并收敛风险，再继续。

### 4.3 任务切换规则

显式切换到新任务时，必须同步更新：

- `docs/governance/CURRENT_TASK.yaml`
- `docs/governance/DEVELOPMENT_ROADMAP.md`
- `docs/governance/TASK_REGISTRY.yaml`
- `docs/governance/WORKTREE_REGISTRY.yaml`
- 新任务的 task 文件
- 新任务的 runlog
- 必要时的 handoff

## 5. 目录边界与允许修改规则

### 5.1 默认关键目录

建设工程域默认关键目录如下：

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

### 5.2 目录硬约束

1. 未在任务包中授权的目录，一律视为禁止修改；
2. 页面层、接口拼装层、临时脚本不得代替正式阶段逻辑；
3. 不得在抓取层、解析层或前端层偷做顶层业务裁决；
4. 不得让兼容层旧逻辑重新上升为主实现；
5. 不得用文档任务顺手改代码，不得用代码任务顺手改大段制度文档。

### 5.3 文档专项任务的特殊边界

若任务属于“权威文档 / 开发手册 / 治理台账”专项：

1. 默认只允许修改 `docs/baseline/` 与必要的治理台账文件；
2. 不得顺手同步代码、schema、fixtures、contracts，除非任务包明确授权；
3. 文档中可以定义“后续应同步哪些资产”，但本任务不等于已经完成同步；
4. 文档专项任务必须明确哪些是“现行制度”，哪些是“后续对齐要求”。

## 6. 文档变更的同步清单

### 6.1 改权威文档时

如果任务改动权威文档中的正式对象、正式字段、正式枚举、正式规则码、正式接口、正式客户交付边界，后续任务必须同步检查：

- `docs/governance/INTERFACE_CATALOG.yaml`
- `docs/governance/SCHEMA_REGISTRY.md`
- `docs/contracts/field_semantics/`
- `docs/contracts/schemas/`
- `docs/contracts/examples/`
- `docs/contracts/customer_delivery_field_whitelist.yaml`
- `docs/contracts/customer_delivery_field_blacklist.yaml`
- `docs/contracts/region_coverage_registry.yaml`
- `docs/contracts/sources_registry.yaml`

### 6.2 改开发手册时

如果任务改动开发手册中的执行纪律、任务生命周期、回滚要求、门禁要求或输出模板，必须同步检查：

- `docs/governance/TASK_POLICY.yaml`
- `docs/governance/REVIEW_POLICY.md`
- `docs/governance/PR_CHECKLIST.md`
- `docs/governance/TEST_MATRIX.yaml`
- 自动化与治理脚本是否仍与本文一致

### 6.3 文档不能假装已落地

文档可以规定后续动作，但不得把“应同步”写成“已同步”。

最低要求如下：

1. 若 schema / examples / registry 尚未更新，文档必须明确写为“后续对齐要求”；
2. 若当前仅完成基线制定，不得宣称仓库已完全按该基线落地；
3. 若变更具有破坏性，必须在文档中保留实施风险提示。

## 7. 接口、字段、交付与可售治理联动

### 7.1 接口变更

改接口时，至少同步检查：

- 输入契约；
- 输出契约；
- version；
- breaking change 标记；
- 调用方影响；
- 枚举 / 单位 / 时间 / 空值语义。

### 7.2 字段与对象变更

改正式字段、正式对象或正式枚举时，至少同步检查：

- `SCHEMA_REGISTRY.md`
- 对应 field semantics
- 对应 schema
- 对应 example

### 7.3 规则码变更

新增、下线或重命名正式 `rule_code` 时，至少同步检查：

- 权威文档中的规则码总表；
- fixture；
- unit tests；
- integration tests；
- 必要的 snapshot / facts tests；
- 业务回归样本说明。

### 7.4 客户可见与中国售卖联动

凡是影响客户可见结果的改动，必须额外检查：

- 是否扩大客户可见承诺；
- 是否新增客户可见字段；
- 是否新增自然人职业信息字段；
- 是否影响外发报告、异议辅助包、导出或对外 API；
- 是否影响地区覆盖等级、源族成熟度、`is_sellable` 或 `coverage_sellable_state`；
- 是否影响字段策略字典、对象级交付矩阵、审计留痕要求。

## 8. 测试、校验与验收

### 8.1 文档专项任务最低校验

文档专项任务至少要做以下检查：

- 文档结构完整性检查；
- 交叉引用一致性检查；
- 权威文档与开发手册职责边界检查；
- 当前任务治理台账一致性检查。

### 8.2 代码任务最低校验

代码任务至少要按任务包运行：

- repo check
- hygiene check
- authority alignment check
- 任务范围内的单测 / 集成测试 / 契约测试

### 8.3 发布前附加检查

若任务会影响中国客户可见口径，还必须检查：

- 覆盖登记是否需要更新；
- 客户交付白名单 / 黑名单是否需要更新；
- 字段策略字典是否需要更新；
- 对象级交付矩阵是否需要更新；
- 对外免责声明、演示口径和售卖边界是否仍一致。

## 9. 例外、热修与临时兼容

以下情形必须走例外治理：

- 越过默认阶段边界；
- 紧急热修；
- 临时兼容字段；
- 临时调整阶段 6 刷新 / 回写策略；
- 因外部源突变导致的临时绕行。

涉及例外时，必须同步更新：

- `docs/governance/exceptions/`
- `docs/governance/exceptions_registry.yaml`

无审批、无有效期、无回收方案的例外，不得合并。

## 10. Codex 固定执行约束

在执行任何建设工程域任务时，默认遵守以下固定约束：

```text
你是 AX9S 仓库的受限开发代理，不是自由设计师。

必须遵守：
1. 先读权威文档，再读当前任务包和 runlog。
2. 任何改动必须映射到明确阶段，不得绕开阶段 6。
3. 不得新增第二套真相层、第二套主口径、第二套事实面。
4. 不得修改未授权目录。
5. 改接口必须同步契约清单。
6. 改表结构必须同步 migration、rollback、seed/demo。
7. 改规则必须同步 fixture、tests 和规则码清单。
8. 先输出计划、影响范围、文件清单、测试清单，再开始改动。
9. 输出必须包含：改动摘要、风险、测试结果、未完成项、回滚方式。
10. 涉及例外、热修、人工覆盖或事实刷新策略变更时，必须同步更新台账与测试。
11. 未经明确授权，不做顺手重构。
12. 文档专项任务不得假装代码、契约、测试已经同步落地。
```

## 11. 输出模板

每次任务完成后，固定输出：

- 改动摘要
- 影响文件
- 测试结果
- 风险
- 未完成项
- 回滚方式

若任务涉及阶段判断、客户可见承诺、可售状态或例外，还应补充：

- 影响阶段
- 是否存在例外及到期时间
- 对应权威文档章节

## 12. 附录

### 附录 A：任务包最小模板

```text
任务编号：
主目标：
不做什么：
所属阶段：
影响模块：

允许修改目录：
- 

禁止修改目录：
- 

是否涉及接口变更：
是否涉及表结构迁移：
是否涉及例外审批：
是否影响 stage6 facts 刷新 / 回写：
是否影响客户可见承诺：
是否影响地区 / 源族覆盖等级：
是否新增或扩大客户可见个人信息字段：

必须新增的测试：
- 

验收标准：
- 

回滚方式：
- 
```

### 附录 B：文档对齐检查清单

```text
authority_alignment_checklist:
  authority_source_confirmed: true
  dev_manual_scope_confirmed: true
  old_version_history_removed_when_requested: true
  object_and_rule_boundaries_not_redefined: true
  cross_refs_checked: true
  governance_ledgers_aligned: true
  followup_sync_items_listed: true
```

### 附录 C：发布前可售 / 交付核对清单

```text
release_gate_checklist:
  customer_commitment_expanded: false
  natural_person_scope_expanded: false
  coverage_registry_update_required: false
  field_policy_dictionary_update_required: false
  delivery_object_matrix_update_required: false
  disclaimer_update_required: false
  exception_required: false
```

## 13. 生效结论

自本文生效起：

1. AX9S 建设工程域的仓库执行规范统一以本文为准；
2. 领域边界、阶段定义、正式对象、规则边界、页面 / API 主消费原则统一以上游权威文档为准；
3. 当前总文档基线固定为 V1.5 单一来源；
4. 后续所有实现、契约、测试与交付治理对齐，均应以该单一来源为准展开。
