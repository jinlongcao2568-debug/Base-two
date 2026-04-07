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

### 2.4 旧版文档隔离规则

为避免旧版材料误入当前执行链，默认执行以下规则：

1. 当前执行链只允许引用现行 V1.5 基线文件；
2. 新任务、手册、专项说明、PR 描述、测试说明不得把旧版文档作为当前执行依据引用；
3. 若旧版文件重新进入 `docs/baseline/`，必须先显式标记为 archive 或移出当前基线路径，才能继续作为仓库材料保留；
4. 未完成归档隔离的旧版文件，不得在任何自动检查、人工审阅或任务说明中作为当前依据使用。

### 2.5 当前基线文件清单

当前建设工程域现行基线文件固定为：

1. `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.5_全量规则码版.md`
2. `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.5_2026-04-07.md`

除上述两份文件外，`docs/baseline/` 中不应再存在其他现行基线文件。

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

### 6.4 当前 V1.5 基线的推荐同步顺序

当权威文档先于代码与契约落地时，必须按以下顺序推进，不得无序穿插：

1. 先固定权威文档与开发手册；
2. 再同步治理台账与任务边界；
3. 再同步 `INTERFACE_CATALOG`、`SCHEMA_REGISTRY` 等总索引；
4. 再同步 field semantics、schema、example；
5. 再同步客户交付白名单 / 黑名单、字段策略字典、对象级交付矩阵、覆盖登记；
6. 最后同步实现、fixture、tests 与发布门禁。

若前一层尚未收敛，禁止直接跳到后一层。

### 6.5 当前 V1.5 基线的直接待同步项

以当前 V1.5 基线为准，后续任务至少应补齐以下机器可读资产：

1. `docs/governance/INTERFACE_CATALOG.yaml`
   - 新增或确认：
   - `GET /projects/{id}/tender-design-risk`
   - `GET /projects/{id}/post-award-changes`
   - `GET /projects/{id}/bundle-risk`
2. `docs/governance/SCHEMA_REGISTRY.md`
   - 新增或确认：
   - `coverage_sellable_state`
   - `delivery_risk_state`
   - `manual_override_status`
   - 七类 profile 对象
3. `docs/contracts/field_semantics/`
   - 新增或确认七类 profile 对象的字段语义文件
   - 补齐 `project_fact` 中治理侧消费字段的字段语义
4. `docs/contracts/schemas/`
   - 更新 `stage4_rule_hit.schema.json`
   - 更新 `stage4_review_request.schema.json`
   - 更新 `stage6_project_fact.schema.json`
   - 必要时新增七类 profile 对象 schema
5. `docs/contracts/examples/`
   - 更新 `rule_hit.example.json`
   - 更新 `review_request.example.json`
   - 更新 `project_fact.example.json`
   - 必要时新增七类 profile 对象 example
6. 交付与覆盖治理资产
   - `customer_delivery_field_whitelist.yaml`
   - `customer_delivery_field_blacklist.yaml`
   - `field_policy_dictionary.yaml`
   - `delivery_object_matrix.yaml`
   - `coverage_governance_registry.yaml`
   - `region_coverage_registry.yaml`
   - `sources_registry.yaml`

若上述资产未完成同步，必须在任务输出中明确标注“未完成项”，不得表述为“仓库已全面对齐 V1.5”。

### 6.6 权威章节到仓库资产硬映射

为避免“知道制度但不知道要改什么文件”，当前基线按下列映射强制执行：

1. 权威文档第 3 章“覆盖成熟度、地区可售与可售治理”
   - 主同步目标：
   - `docs/contracts/region_coverage_registry.yaml`
   - `docs/contracts/sources_registry.yaml`
   - `docs/contracts/coverage_governance_registry.yaml`
2. 权威文档第 5 章“九阶段总体基线与成立标准”
   - 主同步目标：
   - 任务包中的所属阶段
   - 任务包中的允许修改目录
   - 对应 stage 测试目录
3. 权威文档第 6 章“正式对象与字段字典”
   - 主同步目标：
   - `docs/governance/SCHEMA_REGISTRY.md`
   - `docs/contracts/field_semantics/`
   - `docs/contracts/schemas/`
   - `docs/contracts/examples/`
4. 权威文档第 7 章“正式规则专题”
   - 主同步目标：
   - 权威文档规则码总表
   - `stage4_rule_hit` 契约
   - `stage4_review_request` 契约
   - fixture / tests / 回归样本说明
5. 权威文档第 8 章“页面与接口消费原则”
   - 主同步目标：
   - `docs/governance/INTERFACE_CATALOG.yaml`
   - 页面消费说明
   - 调用方影响说明
6. 权威文档第 9 章“客户交付、字段控制与外发治理”
   - 主同步目标：
   - 客户交付白名单 / 黑名单
   - `docs/contracts/field_policy_dictionary.yaml`
   - `docs/contracts/delivery_object_matrix.yaml`
   - 外发审计与导出门禁
7. 权威文档第 10 章“角色、权限与审计留痕”
   - 主同步目标：
   - 权限矩阵
   - 审计事件清单
   - 高限制字段访问日志要求
8. 权威文档第 11 章“测试验收、发布准入与治理反馈”
   - 主同步目标：
   - `docs/governance/TEST_MATRIX.yaml`
   - 任务包 required tests
   - 发布前附加检查
9. 权威文档第 12 章“迁移兼容与变更治理”
   - 主同步目标：
   - 迁移任务包
   - rollback 说明
   - 例外台账
   - 兼容窗口说明

### 6.7 当前关键治理资产的规范路径与审批责任

以下资产在当前基线下视为规范位置；如仓库尚未创建，后续任务必须优先补齐，禁止再使用其他“等价位置”自由发挥：

1. `docs/contracts/coverage_governance_registry.yaml`
   - 业务审批：产品 / 治理 owner
   - 技术审批：tech owner
2. `docs/contracts/field_policy_dictionary.yaml`
   - 业务审批：交付 / 合规 owner
   - 技术审批：tech owner
3. `docs/contracts/delivery_object_matrix.yaml`
   - 业务审批：产品 / 交付 owner
   - 技术审批：tech owner
4. `docs/governance/INTERFACE_CATALOG.yaml`
   - 业务审批：产品 owner
   - 技术审批：接口 owner
5. `docs/governance/SCHEMA_REGISTRY.md`
   - 业务审批：领域 owner
   - 技术审批：schema owner

若任务影响上述资产但未明确 owner、审批人与同步位置，不得进入实现。

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

### 8.4 V1.5 对齐任务的最低测试要求

凡是“对齐 V1.5 基线”的任务，除本任务自身范围内测试外，至少应按层次声明以下校验：

1. 文档层
   - 文档结构完整性检查
   - 交叉引用一致性检查
   - 权威文档与开发手册职责边界检查
2. 契约层
   - `INTERFACE_CATALOG` 与权威接口清单一致
   - `SCHEMA_REGISTRY` 与正式字段 / 对象一致
   - field semantics、schema、example 三者一致
3. 治理层
   - 客户交付白名单 / 黑名单与权威文档边界一致
   - 字段策略字典与对象级交付矩阵具备正式承接位置
   - 覆盖登记与可售状态口径具备正式承接位置
4. 实现层
   - 新规则码具备 fixture、tests、回归样本说明
   - 新治理字段具备 stage6 汇总、消费与阻断验证
   - 新接口具备契约与调用方影响说明

未声明测试层次的 V1.5 对齐任务，不应视为专业化任务包。

### 8.5 V1.5 对齐任务的关账门槛

凡是“V1.5 对齐”任务，默认只有在以下条件满足时才建议关账：

1. 当前任务范围内的文档、契约、代码或治理资产已经全部写完；
2. required tests 已在 runlog 中登记结果；
3. 任务输出已经明确：
   - 已完成项
   - 未完成项
   - 后续待同步资产
4. 若仍有未同步资产，已明确这些资产属于后续任务，而不是本任务遗漏；
5. 若仍有后续待同步资产，已为这些资产建立或显式预留后续任务编号；
6. 若未建立后续任务编号，不得以“后续再做”作为关账理由；
7. `CURRENT_TASK`、`TASK_REGISTRY`、`WORKTREE_REGISTRY`、task 文件、runlog、handoff 没有漂移；
8. 若任务仅完成文档层，不得把状态写成“全仓完成对齐”；
9. 若任务影响客户可见口径、规则边界、正式字段或正式接口，必须明确是否已触发下游同步任务。

不满足上述条件时，必须保持 `doing` 或 `review`，不得为了形式化关账而提前结束。

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

### 附录 D：V1.5 对齐分层任务模板

```text
alignment_task_layers:
  L0_authority_docs:
    scope:
      - docs/baseline/
    goal:
      - 固定权威文档
      - 固定开发手册
  L1_governance_indexes:
    scope:
      - docs/governance/INTERFACE_CATALOG.yaml
      - docs/governance/SCHEMA_REGISTRY.md
    goal:
      - 固定总索引
  L2_contract_assets:
    scope:
      - docs/contracts/field_semantics/
      - docs/contracts/schemas/
      - docs/contracts/examples/
    goal:
      - 固定对象、字段、schema、example
  L3_delivery_and_coverage:
    scope:
      - docs/contracts/customer_delivery_field_whitelist.yaml
      - docs/contracts/customer_delivery_field_blacklist.yaml
      - docs/contracts/field_policy_dictionary.yaml
      - docs/contracts/delivery_object_matrix.yaml
      - docs/contracts/coverage_governance_registry.yaml
      - docs/contracts/region_coverage_registry.yaml
      - docs/contracts/sources_registry.yaml
    goal:
      - 固定交付与可售治理
  L4_code_and_tests:
    scope:
      - src/
      - tests/
    goal:
      - 固定实现、fixture、tests、门禁
```

### 附录 E：V1.5 权威一致性审校尺子

```text
authority_review_rubric:
  single_source:
    question: 是否存在旧版口径回流为现行依据
  boundary_clarity:
    question: 权威文档与开发手册是否各守其责
  sync_order:
    question: 是否明确了从文档到契约再到实现的顺序
  machine_readable_readiness:
    question: 是否明确了需要同步的机器可读资产
  customer_visible_governance:
    question: 是否明确了客户交付、字段控制、覆盖治理、审计的落点
  execution_usability:
    question: 工程师或 Codex 是否能据此直接拆下一批任务
```

### 附录 F：权威章节到仓库资产速查表

```text
authority_to_repo_quickmap:
  chapter_3_coverage_governance:
    - docs/contracts/region_coverage_registry.yaml
    - docs/contracts/sources_registry.yaml
    - docs/contracts/coverage_governance_registry.yaml
  chapter_5_stage_baseline:
    - task_package_stage
    - allowed_dirs
    - stage_tests
  chapter_6_objects_and_fields:
    - SCHEMA_REGISTRY
    - field_semantics
    - schemas
    - examples
  chapter_7_rule_topics:
    - 权威文档附录规则码总表
    - docs/contracts/schemas/stage4_rule_hit.schema.json
    - docs/contracts/schemas/stage4_review_request.schema.json
    - fixtures_and_regressions
  chapter_8_page_api_consumption:
    - docs/governance/INTERFACE_CATALOG.yaml
    - page_consumer_notes
  chapter_9_delivery_governance:
    - docs/contracts/customer_delivery_field_whitelist.yaml
    - docs/contracts/customer_delivery_field_blacklist.yaml
    - docs/contracts/field_policy_dictionary.yaml
    - docs/contracts/delivery_object_matrix.yaml
  chapter_10_roles_audit:
    - permission_matrix
    - audit_event_catalog
  chapter_11_testing_release:
    - docs/governance/TEST_MATRIX.yaml
    - required_tests
    - release_gate_checklist
  chapter_12_migration_change:
    - migration_task_package
    - rollback_notes
    - exceptions_registry
```

## 13. 生效结论

自本文生效起：

1. AX9S 建设工程域的仓库执行规范统一以本文为准；
2. 领域边界、阶段定义、正式对象、规则边界、页面 / API 主消费原则统一以上游权威文档为准；
3. 当前总文档基线固定为 V1.5 单一来源；
4. 后续所有实现、契约、测试与交付治理对齐，均应以该单一来源为准展开。
