# AX9S 建设工程域研发 / Codex 执行手册（中国落地售卖增强版）

- 版本：2026-04-02（中国落地售卖增强版，含 V1.4 状态机/矩阵/审计微修）
- 文档定位：建设工程域仓库执行规范与 AI / Codex 操作手册
- 适用范围：AX9S 仓库中的建设工程域研发、测试、联调、迁移、回滚、审查与 AI / Codex 执行任务
- 配套关系：本文档只规定“怎么在仓库里动手”，不重定义建设工程域的阶段边界、正式对象、规则边界、页面 / API 主消费原则；上述内容统一以《建设工程域权威文档》为准。
- 冲突规则：如本文与《建设工程域权威文档》冲突，以《建设工程域权威文档》为准。

---

## 1. 文档目标与边界

本文档用于回答以下问题：

1. 研发与 AI / Codex 在开始任务前必须做什么准备；
2. 一个任务包至少应包含哪些内容；
3. 哪些目录、模块、接口、迁移、测试属于允许修改范围；
4. 如何通过 CI 门禁、防止越界改动、防止文档与实现漂移；
5. 发生紧急故障、热修、回滚时如何在不破坏领域权威口径的前提下处理；
6. 受控例外如何登记、审批、过期与回收。

本文档不负责回答以下问题：

- 建设工程域九阶段如何定义；
- `project_base`、`project_fact`、`rule_hit` 等正式对象边界如何定义；
- `AUTO_HIT / CLUE / OBSERVATION` 如何定义；
- 页面 / API 主判断应该消费哪一层对象；
- 哪些规则码、枚举与字段属于正式领域口径。

这些问题只由《建设工程域权威文档》回答。


### 1.1 中国落地售卖场景下的执行目标

除通用研发与仓库治理外，本文还约束以下中国落地售卖相关执行动作：

1. 防止销售、交付、导出与客户培训突破权威文档中的对外承诺边界；
2. 防止未验证地区、未验证专题、未登记公开源被提前包装为稳定可售能力；
3. 防止客户交付版、外发异议辅助包、下载导出在权限、脱敏、免责声明与审计上失控；
4. 防止“公开证据核查产品”被执行动作误导成“自动法律结论系统”。

### 1.2 本文新增约束的直接对象

中国落地售卖增强版额外约束以下对象：

- 客户可见报告；
- 外发异议辅助包；
- 地区覆盖等级与源族成熟度登记；
- 客户可见承诺、销售话术与交付用语；
- 多租户隔离、下载审计与人工覆盖日志；
- 发布前合规检查与可售检查。


---

## 2. 执行总原则

### 2.1 基本原则

任何建设工程域开发任务必须遵守以下原则：

1. 先读《建设工程域权威文档》；
2. 任何改动必须映射到明确阶段；
3. 不得绕开阶段 6 建第二套主判断；
4. 不得新增第二套真相层、第二套主口径、第二套事实面；
5. 未经明确授权，不做顺手重构；
6. 输出必须可测试、可审计、可回滚、可追溯；
7. 任何例外、热修、临时兼容都必须登记入机器可读台账并声明失效时间；
8. 执行手册只约束“仓库动作”，不得反向定义领域对象、规则口径与页面 / API 主消费原则。

### 2.2 标准执行顺序

每次任务的标准顺序应为：

1. 阅读权威文档；
2. 阅读任务包；
3. 确认影响阶段；
4. 确认允许修改目录；
5. 确认是否涉及接口变更；
6. 确认是否涉及表结构迁移；
7. 确认是否涉及例外审批；
8. 列出文件清单与测试清单；
9. 实施改动；
10. 跑门禁与测试；
11. 输出改动摘要、风险、测试结果、未完成项与回滚方式。


### 2.3 发布前合规与可售检查原则

任何面向中国客户的版本发布前，必须额外确认：

1. 本次改动是否扩大了客户可见承诺；
2. 本次改动是否新增或扩大了公开自然人职业信息处理范围；
3. 本次改动是否影响外发版报告、异议辅助包、下载权限或审计策略；
4. 本次改动是否改变地区 / 源族覆盖等级；
5. 本次改动是否可能使销售或交付误用“自动认定违法”“自动替代监管机关结论”等表述。

未完成上述检查时，不得进入正式发布或对外演示。


---

## 3. 任务准入规则

### 3.1 开始任务前必须确认

每个任务开始前，必须明确：

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

### 3.2 一次任务的边界

默认要求：

1. 一次任务只允许一个主目标；
2. 一次任务默认最多影响两个相邻阶段；
3. 若任务的唯一目的是将相邻阶段结果接入阶段 6 统一事实面，可允许覆盖“相邻阶段 + 阶段 6”，但必须在任务包中写明原因、边界、影响字段与回滚方式；
4. 若必须跨越两个以上阶段且不属于上述情形，必须在任务包中说明原因与边界；
5. 若必须临时越过默认边界，必须走例外审批并登记台账。

### 3.3 禁止启动的任务类型

以下任务在缺少明确授权前不得启动：

- 以“顺手整理”为名的大范围重构；
- 同时重命名对象、改变语义、删除兼容字段；
- 在页面层补阶段逻辑；
- 在接口层重算顶层主判断；
- 为图方便新增平行字段、平行口径、平行事实面；
- 修改未列入任务包的关键目录；
- 以本手册为依据重定义权威文档中的正式对象与正式边界。

---

## 4. 受控例外治理

> 说明：权威文档只定义“允许受控例外”的领域原则；本章负责例外台账、审批字段、时效治理与 CI 阻断。

### 4.1 需要走例外的情形

以下情形必须登记例外：

- 越过默认阶段边界；
- 引入临时兼容字段或临时适配层；
- 紧急热修；
- 临时调整统一事实刷新策略；
- 业务效果下降但因止损需要暂时合并；
- 因外部系统或上游公开源突变导致的临时绕行方案。

### 4.2 例外台账要求

任何例外都必须：

1. 在 `docs/governance/exceptions/` 下登记例外记录；
2. 同步更新 `exceptions_registry.yaml`；
3. 具有唯一 `exception_id`；
4. 明确 `reason`、`scope`、`owner`、`approved_by_business`、`approved_by_tech`；
5. 明确 `start_at`、`expire_at`、`rollback_plan`、`recovery_plan`、`status`；
6. 写明是否影响阶段 6 事实刷新、主判断消费或业务效果基线。

### 4.3 合并与过期阻断

- 例外未登记、审批字段缺失或有效期缺失时，不得合并；
- 例外到期未回收时，CI 必须失败；
- 例外若影响正式对象或主判断消费边界，必须在 PR 中显式标注；
- 例外结束后必须补齐正式实现、测试、文档与回收记录。


### 4.4 发布前合规检查清单

每次进入客户演示、灰度发布、正式发布或交付前，至少核对以下清单：

- 是否新增客户可见结论字段；
- 是否新增自然人姓名、证书编号、联系方式或其他客户可见职业信息；
- 是否新增外发版报告字段、异议辅助包字段或导出能力；
- 是否新增、变更或下线地区覆盖等级；
- 是否新增、变更或下线公开源登记；
- 是否影响免责声明、脱敏、下载权限、租户隔离或审计日志；
- 是否需要同步更新销售禁用话术清单、可售包定义或覆盖登记表。

未勾选完成的发布，不得进入正式交付流程。


---

## 5. 模块 owner 与评审要求

### 5.1 owner 机制

每个关键目录必须定义：

- `business_owner`
- `tech_owner`
- `backup_owner`

推荐最小 owner 颗粒度：

- `src/stage3_parsing/`
- `src/stage4_validation/`
- `src/stage5_reporting/`
- `src/stage6_facts/`
- `src/domain/engineering/`
- `db/migrations/`
- `docs/baseline/`
- `docs/governance/`

### 5.2 合并要求

1. 未经对应 owner 审阅不得合并；
2. 涉及阶段 6 主判断的改动，必须同时经过业务 owner 与技术 owner 审阅；
3. 涉及迁移、回滚、正式对象兼容或业务效果下降的改动，必须补充兼容说明或例外说明；
4. owner 列表应机器可读，建议维护在 `docs/governance/owners.yaml`。

---

## 6. 目录边界与代码放置规则

### 6.1 推荐主目录结构

```text
src/
  stage1_orchestration/
  stage2_ingestion/
  stage3_parsing/
  stage4_validation/
  stage5_reporting/
  stage6_facts/
  stage7_sales/
  stage8_contact/
  stage9_delivery/
  domain/
    engineering/
      public_chain/
      project_manager/
      competitor_analysis/
      evidence/
      review_requests/
  shared/
    contracts/
    infra/
    utils/

tests/
  stage3/
  stage4/
  stage5/
  stage6/
  integration/
  fixtures/

docs/
  baseline/
  governance/
    exceptions/
  contracts/

db/
  migrations/
```

### 6.2 目录硬约束

- 不得新增无审批的顶级目录；
- 不得把阶段逻辑写进页面层；
- 不得把解析层逻辑写进规则层或接口层；
- 不得把阶段 6 主判断下沉到页面拼装；
- 不得把仅供兼容的旧逻辑重新上升为主实现；
- 证据载体路径、留存策略、脱敏与访问控制必须放在执行规范或专项设计中，不得反向上升为领域主定义。

### 6.3 允许修改与禁止修改

每个任务必须明确：

- 允许修改目录；
- 禁止修改目录；
- 允许新增文件类型；
- 禁止触碰的共享模块。

未被任务包授权的目录，视为禁止修改目录。


### 6.4 公开源与地区覆盖登记

中国落地售卖版必须维护以下机器可读登记表：

- `docs/contracts/sources_registry.yaml`
- `docs/contracts/region_coverage_registry.yaml`

最低要求如下：

1. `sources_registry.yaml` 至少记录 `source_id`、`source_name`、`is_public`、`collection_mode`、`coverage_regions`、`contains_person_fields`、`maturity_level`、`last_verified_at`、`owner`、`risk_note`；
2. `region_coverage_registry.yaml` 至少记录 `region_code`、`coverage_level`、`validated_topics`、`validated_sources`、`golden_sample_count`、`is_sellable`、`last_verified_at`、`owner`；
3. 未登记的公开源不得进入正式可售能力；
4. 未登记或 `is_sellable=false` 的地区，不得对外承诺为稳定支持地区。


---

### 6.4.1 地区可售判定阈值

`region_coverage_registry.yaml` 中的 `is_sellable=true` 默认必须同时满足以下阈值：

1. `coverage_level` 至少为 `L1`；
2. `validated_topics` 至少包含中国 MVP 三个核心专题：项目负责人资格核查、真实竞争者识别、程序公开充分性核查；
3. `validated_sources` 至少包含一个主链公开源，且所有客户可见增强源均已登记；
4. `golden_sample_count >= 20`，且每个中国 MVP 核心专题在该地区的有效样本数不得低于 `5`；
5. `last_verified_at` 距当前时间不得超过 `45` 天；
6. 所有客户可见公开源的 `last_verified_at` 距当前时间不得超过 `30` 天；
7. 不存在未关闭的重大客户投诉、重大合规事故、重大数据隔离事故或高严重度例外。

若需突破上述阈值，只能走受控例外并在发布说明中明示。


### 6.4.1A 地区可售状态机与迁移规则

`region_coverage_registry.yaml` 不得只维护 `is_sellable`，还必须维护 `sellable_state`。最低状态机如下：

- `NOT_READY`
- `VALIDATING`
- `SELLABLE`
- `RESTRICTED`
- `SUSPENDED`
- `RECOVERING`

最低执行要求如下：

1. 新地区默认以 `NOT_READY` 进入台账；
2. 完成样本准备与首轮验证后，方可迁移到 `VALIDATING`；
3. 只有满足 6.4.1 阈值且审批通过，才可迁移到 `SELLABLE`；
4. 存在限制条件但仍允许局部售卖时，使用 `RESTRICTED`；
5. 发生重大问题时，必须迁移到 `SUSPENDED`；
6. 进入恢复流程后使用 `RECOVERING`，恢复完成前不得直接改回 `SELLABLE`。

任何越级迁移、未留痕迁移或缺少审批的迁移，发布检查必须失败。

### 6.4.2 动态降级与停售触发器

以下任一条件成立时，必须在 `1` 个工作日内更新 `region_coverage_registry.yaml`，并将相应地区、专题或源族降级为不可售或限制售卖：

1. 核心公开源连续失效超过 `7` 个自然日；
2. 重点地区、重点专题连续两次金标回归显著下降；
3. 重大客户投诉经确认属实，且指向客户可见结论、覆盖承诺或字段外发问题；
4. 发生自然人字段越权外发、租户隔离失败或外发报告合规事故；
5. `last_verified_at` 超窗仍未完成复验；
6. 依赖的正式规则码、模板、免责声明或覆盖登记存在缺失或失配。

降级后必须同步更新售前材料、演示环境、客户交付模板与回归计划，不得继续沿用旧承诺。


### 6.4.3 降级 / 恢复 SLA 与审计链

最低 SLA 要求如下：

1. 重大客户投诉、重大外发事故、自然人字段越权外发、租户隔离事故：`1` 个工作日内完成降级回写；
2. 核心公开源连续失效：`1` 个工作日内进入 `RESTRICTED` 或 `SUSPENDED`；
3. 验证窗口过期：`2` 个工作日内进入 `RESTRICTED` 或重新验证；
4. 恢复为 `SELLABLE`：必须在恢复前完成复验、审批和审计链补齐，不允许先恢复后补录。

最低审计链字段如下：

- `event_id`
- `region_code`
- `from_state`
- `to_state`
- `trigger_type`
- `trigger_summary`
- `owner`
- `approved_by`
- `occurred_at`
- `resolved_at`
- `evidence_refs`
- `post_action`

`region_coverage_registry.yaml` 与发布审计必须能追溯最近一次降级、最近一次恢复与当前限制原因。

## 7. 接口契约治理

### 7.1 接口清单要求

接口清单必须机器可读。每条接口必须包含：

- `name`
- `owner`
- `source_stage`
- `target_stage`
- `input_contract`
- `output_contract`
- `version`
- `breaking_change`
- `last_changed_by_task`

若接口涉及正式枚举、单位或时间口径，还必须同步维护：

- 枚举总表引用；
- 单位说明；
- 时间时区说明；
- 空值 / 空数组约定。

### 7.2 接口变更规则

1. 改接口必须同步接口清单；
2. 改输入输出契约必须同步更新调用方影响说明；
3. 任何 breaking change 必须显式标记；
4. 接口变更若未同步清单，CI 必须失败；
5. 若接口变更影响枚举、单位、空值语义或时间口径，必须同步更新契约与文档；
6. 接口不得反向定义领域对象边界。

### 7.3 禁止事项

- 不得在接口层重算顶层主判断；
- 不得使用接口返回体偷偷扩写第二套主字段；
- 不得以“前端方便”为名绕开权威文档中的正式对象。


### 7.4 客户可见契约与承诺变更

以下变更除更新接口清单外，还必须同步更新覆盖登记或销售材料：

1. 客户可见结论字段新增、下线或语义变化；
2. 对外报告字段新增、下线或语义变化；
3. 地区覆盖等级变化；
4. 源族成熟度变化；
5. 免责声明、脱敏、外发权限或下载审计策略变化。

若改动会影响客户可见承诺，任务包中必须显式标记，并在 PR 与发布说明中单独列出。


---

## 8. 表结构迁移与兼容执行规则

### 8.1 迁移基本规则

- 迁移文件必须带编号和说明；
- 必须先加后删，优先向后兼容；
- 禁止在同一任务里同时做“重命名 + 语义改变 + 删除旧字段”；
- 每个迁移必须带 rollback 说明；
- 每个迁移必须带 seed / demo fixture。

### 8.2 与阶段相关的附加要求

- 改阶段 6 事实字段，必须同步更新聚合逻辑、`fact_version` 策略和测试；
- 改阶段 5 报告对象，必须同步更新导出与快照测试；
- 改阶段 3 结构化对象，必须同步更新解析 fixture 与兼容说明；
- 改人工覆盖、复核状态或事实刷新触发逻辑，必须同步更新回写幂等测试与回滚说明。

### 8.3 回滚要求

每个涉及迁移的任务都必须给出：

1. 回滚步骤；
2. 受影响对象；
3. 是否需要数据修复；
4. 是否需要补跑回填；
5. 回滚后需要恢复的接口或任务配置。

---

## 9. 测试与 CI 门禁

### 9.1 最少门禁

最少门禁包含：

- formatter
- lint
- type check
- unit tests
- integration tests
- contract tests
- migration dry-run
- forbidden import check
- docs sync check
- exception registry check

### 9.2 追加硬门禁

- 改阶段 3，必须带解析 fixture；
- 改阶段 4，必须带规则命中测试；
- 新增、下线或重命名正式 `rule_code`，必须同步更新《建设工程域权威文档》附录 B《规则码总表》、fixture、契约清单与回归样本；
- 改阶段 5 / 6，必须带报告或事实面快照测试；
- 所有规则结果必须支持证据回链测试；
- 改导出逻辑，必须验证 A / B / C 证据导出规则；
- 改规则专题，必须带最小金标样本回归；
- 改阶段 6 刷新或人工覆盖逻辑，必须带幂等与版本回退测试。

### 9.3 失败即阻断

以下情况 CI 必须失败：

- 接口变更但接口清单未更新；
- 改规则但缺少 fixture 或命中测试；
- 新增、下线或重命名正式 `rule_code` 但未同步更新《建设工程域权威文档》附录 B《规则码总表》、契约清单或回归样本；
- 改迁移但缺少 rollback 或 seed / demo；
- 文档口径与实现明显失配但 docs sync 未更新；
- forbidden import 规则被破坏；
- 例外台账缺失、审批字段缺失或已过期；
- 业务金标回归显著下降且未附带批准的例外说明。

### 9.4 业务效果验收

除工程门禁外，还必须维护业务效果验收：

1. 每个规则专题至少维护一组最小金标样本；
2. 规则改动必须输出命中率变化、误报样本、漏报样本与漂移说明；
3. 重点地区与重点公开源族必须保留回归集；
4. 业务效果明显下降时，即使技术门禁通过，也不得直接合并；
5. 若因紧急止损临时接受业务效果下降，必须登记例外并给出恢复截止时间。


### 9.5 外发版报告、租户隔离与合规门禁

中国落地售卖版额外门禁如下：

1. 外发版报告必须自动附带免责声明；
2. 外发版报告默认不得包含 C 级观察项；
3. 外发异议辅助包默认不得导出未经授权的自然人字段；
4. 涉及自然人职业信息的客户可见导出，必须经过脱敏或最小化展示检查；
5. 多租户数据读取、下载与导出必须具备租户隔离校验；
6. 原始证据查看、客户交付版下载、人工覆盖操作必须具备审计日志；
7. 地区 / 源族覆盖等级变更若未同步登记表，不得发布。

### 9.5.1 客户交付字段白名单 / 黑名单门禁

客户交付版、演示版、导出版与对外 API 必须至少维护以下机器可读模板：

- `docs/contracts/customer_delivery_field_whitelist.yaml`
- `docs/contracts/customer_delivery_field_blacklist.yaml`

最低门禁如下：

1. 未进入白名单的字段，不得默认进入客户交付版；
2. 进入黑名单的字段，不得通过“前端隐藏”“文案省略”替代正式拦截；
3. 条件性白名单字段必须同时绑定审批条件、脱敏规则与审计要求；
4. 任何新增客户可见字段都必须同步更新白名单 / 黑名单模板、外发检查模板与回归样本；
5. 白名单 / 黑名单模板缺失、未同步或与权威文档附录 G 冲突时，发布检查必须失败。


### 9.5.2 对象级交付字段矩阵门禁

除字段级白名单 / 黑名单外，还必须维护对象级交付矩阵。最低门禁如下：

1. 至少对 `project_base`、`project_fact`、`rule_hit`、`evidence`、`review_request`、`report_record` 维护矩阵配置；
2. 至少覆盖：内部研判版、客户交付版、外发异议辅助包、演示版页面、对外 API 五种交付形态；
3. 若对象未进入矩阵，默认不得对客户可见；
4. 若矩阵与字段白名单 / 黑名单冲突，以更严格规则为准；
5. 对象级矩阵缺失、审批策略缺失或审计要求缺失时，发布检查必须失败。

### 9.5.3 字段审批 / 脱敏规则字典门禁

客户可见字段必须同步纳入机器可读的审批 / 脱敏规则字典。最低门禁如下：

1. 每个条件性字段必须声明 `classification`、`approval_required`、`approval_role`、`masking_rule`、`external_audit_required`；
2. 高限制字段若缺失脱敏规则或审批角色，不得进入客户交付版；
3. 新增自然人字段、证书字段、联系方式字段或内部审计字段时，必须同步更新规则字典与回归样本；
4. 审批 / 脱敏字典缺失、未同步或与外发模板冲突时，发布检查必须失败。

### 9.6 业务效果验收的地区化要求### 9.6 业务效果验收的地区化要求

业务效果验收除专题维度外，还必须按地区与覆盖等级执行：

1. 中国 MVP 只要求对已登记的重点地区执行正式业务回归；
2. 每个可售地区至少应绑定一个最小金标样本集；
3. 未完成地区化回归的地区，不得标记为 `is_sellable=true`；
4. 未纳入 MVP 的专题即使代码存在，也不得进入首版可售包承诺。


---

### 9.7 售后反馈与可售状态回写规则

售卖后的真实反馈必须反向影响可售状态，不得把 `is_sellable` 视为一次性发布标签。最低规则如下：

1. 重大客户投诉、重大误报 / 漏报、重大外发事故一经确认，必须在 `1` 个工作日内回写 `region_coverage_registry.yaml`；
2. 若反馈问题影响某地区核心专题可信度，该地区 `is_sellable` 默认应先降为 `false` 或受限可售，再进行补救；
3. 若问题只影响单一专题或单一源族，应至少下调对应 `validated_topics` 或源成熟度，不得继续按原成熟度售卖；
4. 重新恢复可售前，必须补充回归样本、复验记录与恢复说明；
5. 任何客户投诉关闭后，仍应保留审计记录与降级 / 恢复轨迹。


### 9.7.1 售后降级 / 恢复闭环与运营回写

售后反馈除更新地区台账外，还必须更新以下对象：

- `customer_visible_incident_registry`
- `sellable_state_audit_log`
- `delivery_release_notes`
- `sales_claim_registry`

最低要求如下：

1. 任何导致降级的事件都必须同步标记受影响地区、受影响专题、受影响源族与受影响客户交付模板；
2. 恢复完成后必须回写恢复证据、恢复样本、恢复审批人与恢复时间；
3. 已关闭事件不得删除，只能转为归档状态；
4. 若问题由销售承诺失真引起，必须同步修订允许话术模板与相关销售材料。

## 10. Worktree / 分支 / PR 纪律

### 10.1 基本纪律

- 一任务一 worktree；
- 一任务一分支；
- 一 PR 只允许一个主目标；
- 一 PR 默认最多改两个相邻阶段；
- 未合并前不得让多个大任务共用一个 worktree。

### 10.2 命名建议

- 分支：`feat/TASK-024-public-check-review-requests`
- worktree：`../wt-TASK-024`

### 10.3 PR 最低内容

每个 PR 至少包含：

- 任务编号；
- 主目标；
- 所属阶段；
- 影响模块；
- 是否涉及接口变更；
- 是否涉及表结构迁移；
- 是否涉及例外审批；
- 新增测试清单；
- 风险点；
- 回滚方式；
- 与权威文档的对应关系。

---

## 11. Codex 任务包模板

所有 AI 开发任务必须至少包含：

- 任务编号；
- 目标；
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

### 11.1 任务包示例

```text
任务：TASK-024
目标：新增项目负责人在建冲突公开线索聚合器
所属阶段：3/4/6
允许修改：
- src/stage3_parsing/
- src/stage4_validation/
- src/stage6_facts/
- tests/stage3/
- tests/stage4/
- tests/stage6/
禁止修改：
- src/stage7_sales/
- src/stage8_contact/
- src/stage9_delivery/
接口变更：否
表结构迁移：是，新增 project_manager_public_conflict_signals
例外审批：否（属于“相邻阶段 + 阶段 6 统一事实接入”允许情形）
影响阶段 6 事实刷新 / 回写：是
影响客户可见承诺：否
影响地区 / 源族覆盖等级：否
新增或扩大客户可见个人信息字段：否
必须测试：
- 解析 fixture 2 组
- 规则命中单测 4 个
- facts 汇总测试 2 个
- 事实刷新幂等测试 1 个
验收：
- 不新增第二套 PM 归一字段
- 阶段 4 结果进入阶段 6
- 不绕开 `project_fact`
- 全部测试通过
回滚：
- 回滚 migration 024
- 删除对应 facts 聚合字段
```

---

## 12. 给 Codex 的固定执行约束

```text
你是 AX9S 仓库的受限开发代理，不是自由设计师。

必须遵守：
1. 先读《建设工程域权威文档》。
2. 任何改动必须映射到明确阶段，不得绕开阶段 6。
3. 不得新增第二套真相层、第二套主口径、第二套事实面。
4. 不得修改未授权目录。
5. 改接口必须同步接口清单。
6. 改表结构必须新增 migration、rollback、seed/demo。
7. 改规则必须新增 fixture 和测试。
8. 先给出计划、影响范围、文件清单，再开始改。
9. 输出必须包含：改动摘要、风险、测试结果、未完成项。
10. 涉及例外、热修、人工覆盖或事实刷新策略变更时，必须同步更新台账与测试。
11. 未经明确授权，不做顺手重构。
```

---

## 13. 紧急变更与热修处理

### 13.1 可触发条件

以下情形可走紧急变更：

- 线上故障直接影响主流程；
- 严重数据污染需要立即止损；
- 合规或安全问题要求立刻处置；
- 上游公开源发生突变导致抓取全面失效。

### 13.2 紧急变更的最低要求

即使是紧急变更，也必须至少满足：

1. 明确问题编号；
2. 明确止损目标；
3. 明确临时影响范围；
4. 明确回滚方案；
5. 明确事后补测试与补文档责任人；
6. 明确恢复为正式口径的截止时间；
7. 在例外台账中登记临时措施与失效时间。

### 13.3 紧急变更禁止事项

- 不得借紧急变更永久引入第二套主判断；
- 不得以紧急变更为由跳过回滚说明；
- 不得以紧急修复替代正式迁移与兼容策略；
- 不得把临时字段长期滞留为主字段。

---

## 14. 交付与输出模板

### 14.1 每次任务输出必须包含

- 改动摘要；
- 影响阶段；
- 影响文件清单；
- 风险点；
- 测试结果；
- 业务效果变化；
- 未完成项；
- 回滚方式；
- 与权威文档对应关系；
- 是否存在例外及其到期时间。

### 14.2 推荐输出模板

```text
任务：TASK-024
主目标：新增项目负责人在建冲突公开线索聚合器
影响阶段：3 / 4 / 6
改动摘要：
- 新增 PM 公开冲突线索解析
- 新增规则命中与 facts 聚合
影响文件：
- src/stage3_parsing/...
- src/stage4_validation/...
- src/stage6_facts/...
风险：
- 同名归一误判风险
- 历史数据回填耗时增加
测试结果：
- unit: pass
- integration: pass
- facts snapshot: pass
业务效果变化：
- 金标命中率：无下降
- 误报样本：无新增
未完成项：
- 待补 1 组地方住建源 fixture
回滚：
- rollback migration 024
- 下线 stage6 对应聚合字段
对应权威文档：
- 规则专题 6.2
- project_manager 对象
- project_fact 聚合字段
例外：
- 无
```


## 附录 A：机器可读台账与清单最小 Schema

### A.1 例外台账最小样例

```yaml
- exception_id: EX-2026-004
  reason: stage6 refresh hotfix
  scope:
    - src/stage6_facts/
    - tests/stage6/
  owner: tech_owner_x
  approved_by_business: business_owner_y
  approved_by_tech: tech_owner_x
  start_at: 2026-04-02T10:00:00+08:00
  expire_at: 2026-04-09T23:59:59+08:00
  rollback_plan: revert hotfix branch and restore previous fact version
  recovery_plan: replace with formal migration and tests
  affects_fact_refresh: true
  affects_business_baseline: false
  status: active
```

### A.2 接口清单最小样例

```yaml
- name: GET /projects/{id}/public-check
  owner: tech_owner_public_check
  source_stage: stage6
  target_stage: page_api
  input_contract: ProjectPublicCheckRequestV1
  output_contract: ProjectPublicCheckResponseV1
  version: v1
  breaking_change: false
  last_changed_by_task: TASK-031
  enum_refs:
    - result_type
    - sale_gate_status
  unit_notes:
    - amount:CNY_yuan
  time_notes:
    - timezone:ISO8601_with_offset
  empty_value_policy:
    - arrays_use_empty_array
```

### A.3 owner 清单最小样例

```yaml
- path: src/stage6_facts/
  business_owner: business_owner_a
  tech_owner: tech_owner_b
  backup_owner: tech_owner_c
```


### A.4 `sources_registry.yaml` 最小 Schema

```yaml
- source_id: SRC-GGZY-001
  source_name: national_public_resource_platform
  is_public: true
  collection_mode: crawler_or_api
  coverage_regions:
    - 110000
  contains_person_fields: true
  maturity_level: L1
  last_verified_at: 2026-04-02T10:00:00+08:00
  owner: tech_owner_x
  risk_note: attachments quality varies by region
```

### A.5 `region_coverage_registry.yaml` 最小 Schema

```yaml
- region_code: 110000
  coverage_level: L1
  validated_topics:
    - ENG-PM-QUAL-001
    - ENG-COMPETITOR-REAL-001
    - ENG-PUBLIC-COVERAGE-001
  validated_sources:
    - SRC-GGZY-001
  golden_sample_count: 30
  is_sellable: true
  last_verified_at: 2026-04-02T10:00:00+08:00
  owner: business_owner_y
```



## 附录 B：销售与交付禁用话术最小清单

以下表述不得出现在销售材料、客户培训、外发报告首页、演示口径或交付说明中：

- 自动认定围标串标
- 自动判断中标无效
- 自动替代评标委员会结论
- 自动替代监管机关结论
- 自动形成法律意见
- 全国所有地区稳定全覆盖
- 任意地区、任意专题均可直接异议成功

允许使用的正式表述包括：

- 公开证据核查
- 异常线索发现
- 人工复核辅助
- 异议 / 报告辅助
- 项目筛选与经营研判辅助
- 已验证地区 / 已验证专题支持



> 说明：附录 B 只列禁用话术，允许使用的标准口径请直接引用附录 F《销售允许话术最小模板》，不得由销售或交付团队自由改写为更强承诺。

## 附录 C：首版可售包定义（中国 MVP）

中国首版可售包默认只包含以下能力：

1. 项目检索与公告链整合；
2. 项目负责人资格核查；
3. 真实竞争者识别；
4. 程序公开充分性核查；
5. 证据工作台；
6. 人工复核；
7. 项目核查简报、证据包与异议辅助包导出。

中国首版可售包默认不包含以下承诺：

- 全国全地区同等成熟覆盖；
- 自动法律定性；
- 自动监管结论；
- 未验证地区的深链履约 / 变更 / 停工全国化覆盖；
- 阶段 7 至阶段 9 的全量商业闭环作为首发卖点。



---


## 附录 D：售前、交付与地区覆盖执行模板

### D.1 售前口径检查最小模板

```yaml
pre_sale_claim_check:
  task_or_release_id: REL-2026-001
  sellable_scope_confirmed: true
  mvp_package_only: true
  forbidden_claims_checked: true
  region_coverage_registry_checked: true
  sources_registry_checked: true
  customer_visible_disclaimer_checked: true
  approved_by_business: business_owner_y
  approved_by_legal_or_compliance: compliance_owner_z
  approved_at: 2026-04-02T10:00:00+08:00
```

### D.2 客户交付检查最小模板

```yaml
customer_delivery_check:
  delivery_id: DEL-2026-018
  tenant_id: TENANT-001
  report_type: customer_delivery
  disclaimer_included: true
  coverage_scope_included: true
  natural_person_fields_minimized: true
  c_grade_observation_excluded: true
  manual_override_status_visible: true
  reviewed_by: review_owner_x
  approved_for_external_delivery: true
  approved_at: 2026-04-02T10:30:00+08:00
```

### D.3 地区覆盖表述红线

- 销售、交付、客户成功、培训与演示只允许引用 `region_coverage_registry.yaml` 中 `is_sellable: true` 的地区；
- 未验证地区只能表述为“规划中 / 验证中 / 不构成正式承诺”；
- 不得把 `L2 / L3` 地区口径表述为全国统一成熟能力；
- 若某地区金标样本不足、规则漂移未处理或源稳定性下降，必须先下调可售状态，再决定是否继续售卖。

## 附录 E：客户可见承诺与外发合规附加门禁

### E.1 追加硬门禁

- 改动客户首页摘要、免责声明、覆盖范围说明、自然人字段展示规则，必须同步更新客户交付模板与外发检查项；
- 改动可售地区、可售专题或源成熟度定义，必须同步更新 `region_coverage_registry.yaml`、售前材料与回归样本说明；
- 新增客户可见自然人字段，必须同步更新最小化展示规则、租户权限矩阵与下载审计检查；
- 若产品营销、销售或交付模板引用了未验证规则码、未验证地区或未验证源族，CI 或发布检查必须失败。

### E.2 失败即阻断的外发场景

以下情况不得发布对外版本、不得出具客户交付包、不得向销售开放演示：

1. 客户交付版缺少免责声明；
2. 地区覆盖与售前承诺不一致；
3. 未脱敏或越权展示自然人字段；
4. 人工覆盖结论未标明状态；
5. 未验证地区或未验证专题被标记为正式稳定支持；
6. 异议辅助包默认纳入 `C` 级观察项或未排除明显不足证据。


## 附录 F：销售允许话术最小模板

### F.1 标准电梯话术

> AX9S 是面向建设工程招投标场景的公开证据核查、异常线索发现、人工复核与异议 / 报告辅助系统，帮助客户在已验证地区和已验证专题内更快完成项目筛选、风险识别与证据整理。

### F.2 标准报价页描述

> 本产品按已验证地区、已验证源族与已验证专题提供公开信息核查服务。产品输出为基于公开信息的自动核查结果与人工复核辅助结果，不构成法律意见、行政结论、司法认定或对中标结果的最终判断。

### F.3 标准演示口径

> 当前演示仅覆盖登记表中 `is_sellable=true` 的地区与首版可售包中的专题；未展示的地区、源族或专题不视为正式稳定支持范围。

### F.4 标准覆盖范围说明

> 覆盖范围以 `region_coverage_registry.yaml` 与 `sources_registry.yaml` 当前登记结果为准；规划中、验证中或已降级地区不得按正式可售范围对外表述。

### F.5 标准免责声明模板

> 本系统结果基于公开信息进行自动核查与人工复核辅助，仅用于项目筛选、经营研判、证据整理与异议辅助，不构成法律意见、行政结论、司法认定或对中标结果的最终判断。

## 附录 G：客户交付字段白名单 / 黑名单最小模板

### G.1 客户交付版默认白名单

```yaml
customer_delivery_field_whitelist:
  project_summary:
    - project_name
    - region_code
    - source_family
    - public_chain_status
  fact_summary:
    - sale_gate_status
    - real_competitor_count
    - serviceable_competitor_count
    - competitor_quality_grade
    - price_cluster_score
    - price_gradient_pattern
    - fact_summary
    - risk_summary
    - manual_override_status
  rule_explanation:
    - rule_code
    - result_type
    - why_hit
    - boundary_note
    - evidence_grade
  delivery_meta:
    - report_status
    - last_fact_refreshed_at
```

### G.2 条件性白名单模板

```yaml
customer_delivery_conditional_whitelist:
  natural_person_fields:
    - project_manager_name_masked
    - project_manager_role_normalized
    - project_manager_cert_specialty
    - project_manager_public_cert_status
  penalty_fields:
    - entity_name
    - penalty_type
    - penalty_status
    - penalty_source_url
  evidence_fields:
    - approved_evidence_snippet
    - approved_source_url
  conditions:
    - public_traceable
    - minimum_necessary
    - external_delivery_approved
    - audit_enabled
```

### G.3 默认黑名单模板

```yaml
customer_delivery_field_blacklist:
  - internal_id
  - raw_html_path
  - raw_pdf_path
  - evidence_artifact_refs_full
  - full_certificate_number
  - phone_number
  - id_number
  - internal_review_note
  - exception_id
  - audit_log_detail
  - owner_name
  - draft_review_request_detail
  - unreviewed_intermediate_result
```

### G.4 使用说明

1. 模板文件应与权威文档附录 G 保持一致或更严格；
2. 任何新增客户可见字段都必须同时更新白名单 / 黑名单模板、客户交付检查模板与外发门禁；
3. 若模板未更新，不得通过发布检查。

## 15. 生效结论

自本文档生效起：

1. 建设工程域研发、测试、联调、迁移、PR 审查、AI / Codex 执行中的**仓库动作规范**统一以本文为准；
2. 本文只定义执行纪律，不重定义领域对象、阶段边界和主判断；
3. 若本文与《建设工程域权威文档》冲突，以《建设工程域权威文档》为准；
4. 任何执行动作都必须保证：不新增第二套主判断、不新增第二套真相层、不破坏阶段 6 统一事实中枢。


---

## 附录 H：字段审批 / 脱敏规则字典最小模板

```yaml
field_policy_dictionary:
  fact_summary:
    classification: customer_visible_summary
    approval_required: false
    approval_role: null
    masking_rule: none
    external_audit_required: false
  project_manager_cert_no:
    classification: restricted_person_field
    approval_required: true
    approval_role: compliance_owner
    masking_rule: partial_mask_last4
    external_audit_required: true
```

## 附录 I：对象级交付字段矩阵最小模板

```yaml
delivery_object_matrix:
  project_fact:
    customer_delivery:
      allowed_groups: [project_summary, fact_summary]
      conditional_groups: [rule_explanation_excerpt]
      blocked_groups: [internal_audit]
      approval_required: false
      audit_required: true
  evidence:
    external_objection_pack:
      allowed_groups: [evidence_excerpt]
      conditional_groups: [person_professional_excerpt]
      blocked_groups: [raw_artifacts]
      approval_required: true
      audit_required: true
```

## 附录 J：售前允许话术补充模板

```yaml
allowed_sales_claims:
  - "基于公开信息进行自动核查与人工复核辅助"
  - "当前版本在已登记可售地区提供稳定支持"
  - "客户交付版遵循最小化字段展示与审计留痕"
  - "异议辅助包用于证据整理和草稿辅助，不替代法定结论"
```
