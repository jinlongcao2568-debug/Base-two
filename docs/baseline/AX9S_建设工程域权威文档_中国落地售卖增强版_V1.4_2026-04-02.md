# AX9S 建设工程域权威文档（中国落地售卖增强版）

- 版本：2026-04-02（中国落地售卖增强版，含 V1.4 状态机/矩阵/审计微修）
- 文档定位：建设工程域**最高约束性权威文档**
- 适用范围：AX9S 仓库中的建设工程域
- 目标读者：产品、架构、研发、测试、联调、验收、AI / Codex 执行代理
- 生效关系：建设工程域的领域边界、阶段口径、正式对象、规则边界、页面 / API 主消费原则，以本文为准；仓库执行纪律、目录边界、CI 门禁、任务包模板、例外台账、回滚流程等，以《建设工程域研发 / Codex 执行手册》为准。如两者冲突，以本文为准。

---

## 1. 文档定位与使用规则

本文档用于回答以下问题：

1. 建设工程域在 AX9S 中应如何成立；
2. 九阶段链路的输入、处理、输出与消费关系是什么；
3. 哪些对象、字段、结果类型、页面 / API 消费原则是正式口径；
4. 哪些事项可形成正式自动命中，哪些只能形成线索、观察或请求核验事项；
5. 做到什么程度才算阶段成立、系统成立；
6. 工程域变更时，哪些边界不得被仓库实现、页面拼装、接口兼容或临时热修反向改写。

本文档不直接规定以下内容：

- 仓库 owner 名单；
- 目录命名细节；
- CI 门禁清单；
- worktree / 分支 / PR 流程；
- Codex 任务包模板；
- 例外台账字段格式；
- 具体脚本、运行命令与排障记录。

上述内容由《建设工程域研发 / Codex 执行手册》单独规定。

### 1.1 生效规则

自本文档生效起：

1. 建设工程域的阶段口径、对象边界、规则边界、页面 / API 主消费面，统一以本文为准；
2. 任何实现不得绕开阶段 6 形成第二套主判断；
3. 任何仓库执行手册、局部设计说明、任务备注，都不得反向重定义本文中的正式对象与正式边界；
4. 任何新增能力都必须回答：输入是什么、处理在哪里发生、输出是什么、由谁消费、是否超出公开边界、是否破坏阶段 6 统一事实中枢。

### 1.2 受控例外原则

本文档原则上为最高约束性口径，但允许存在**受控例外**。任何例外必须同时满足：

1. 例外仅用于止损、兼容过渡、阶段接线或合规处置，不得用于长期替代正式口径；
2. 必须明确例外原因、影响范围、临时有效期与回收计划；
3. 必须由业务 owner 与技术 owner 共同批准；
4. 必须登记到执行手册约定的机器可读例外台账；
5. 例外解除后必须回归本文正式口径；
6. 未记录、未审批、无有效期的口头例外或临时实现，不得视为正式口径。

> 说明：本文只定义“是否允许受控例外”的领域原则；例外台账字段、审批流程、CI 阻断与过期治理，统一由执行手册规定。


### 1.3 产品定位与对外承诺边界

本系统在中国场景下的正式产品定位固定为：

- 基于**公开证据**的建设工程招投标核查、线索发现、证据整理、人工复核与异议 / 报告辅助系统；
- 面向经营、投标、法务、风控、咨询与复核团队提供产品判断与工作台支持；
- 对外提供的是**产品结果、证据组织能力与人工复核辅助能力**，不是行政处罚、司法裁判、评标裁决或监管机关终局认定。

对外承诺硬边界如下：

1. 不得将本系统宣传为“自动认定围标串标”“自动判断中标无效”“自动替代评标委员会 / 监管机关结论”的系统；
2. 不得把 `AUTO_HIT` 解释为法律定性、行政结论或司法结论；
3. 不得把异议辅助、报告辅助、复核辅助表述为正式法律意见服务；
4. 不得在售前材料、产品首页、导出模板、客户培训口径中突破上述定位。

### 1.4 中国 MVP 覆盖范围与成熟度分级

中国落地时，覆盖范围必须采用分级承诺，不得默认宣称“全国全地区、全专题、全链路同等成熟”。

最低分级如下：

- **L1 核心覆盖**：全国公共资源交易平台主链可稳定获取的信息，包括招标 / 资审公告、开标记录、候选人公示、结果公示、澄清等；
- **L2 增强覆盖**：地方住建公开页、全国建筑市场监管公共服务平台、地方信用处罚页等公开增强信息；
- **L3 深度覆盖**：地方特色公告、复杂附件抽取、履约 / 变更 / 停工 / 验收的区域化深链增强能力。

中国 MVP 的默认正式承诺为：

1. 对外首发产品核心覆盖范围以 **L1 + 已验证的部分 L2** 为准；
2. L3 能力属于区域化扩展能力，不得直接作为全国统一承诺；
3. 任何地区、专题、源族若未进入执行手册约定的覆盖登记表，不得对外承诺为“稳定支持”。

### 1.4.1 地区可售判定最低公式

地区或区域包只有同时满足以下条件，才允许在覆盖登记中标记为 `is_sellable=true`：

1. `coverage_level` 至少达到 `L1`，且对客户承诺的能力范围不超出当前登记等级；
2. `validated_topics` 至少覆盖中国 MVP 核心专题：项目负责人资格核查、真实竞争者识别、程序公开充分性核查；
3. `validated_sources` 至少包含一个主链公开源，且所有对客户可见的增强源都已登记并完成最近一次有效验证；
4. `golden_sample_count` 达到执行手册规定的最低门槛，且不得存在“某核心专题样本数为 0”的情况；
5. `last_verified_at` 位于执行手册规定的有效验证窗口内；
6. 不存在未关闭的重大覆盖风险、重大外发合规事故、重大客户投诉或核心公开源长时间失效；
7. 一旦不再满足上述条件，必须触发动态降级、停售或重新验证，不得继续维持可售状态。

地区可售判定的具体阈值、动态降级触发器、回写时限与机器可读字段，由《建设工程域研发 / Codex 执行手册》定义。


### 1.4.2 地区可售状态机原则

地区可售状态不得只用布尔值表达，还必须符合可迁移、可审计、可恢复的状态机原则。最低状态建议如下：

- `NOT_READY`：尚未进入正式验证，不得对外售卖；
- `VALIDATING`：正在进行覆盖与金标验证，不得作为稳定能力承诺；
- `SELLABLE`：满足地区可售阈值，可进入正式售卖；
- `RESTRICTED`：存在限制性条件，可在明确限制范围内售卖；
- `SUSPENDED`：因回归下降、合规事故、投诉或源失效而暂停售卖；
- `RECOVERING`：已进入恢复流程，待完成复验后才能回到 `SELLABLE`。

最低迁移规则如下：

1. 未完成验证的地区不得从 `NOT_READY` 直接跳到 `SELLABLE`；
2. 任一重大合规、外发、投诉或核心源失效事故，至少应触发 `SELLABLE -> RESTRICTED` 或 `SELLABLE -> SUSPENDED`；
3. 从 `SUSPENDED` 恢复到 `SELLABLE` 前，必须先经过 `RECOVERING` 并完成复验；
4. 任一状态迁移都必须记录触发原因、审批人、时间、回滚与恢复说明；
5. 若状态机记录缺失、迁移越级或恢复依据不足，不得继续维持地区可售承诺。

### 1.5 对外输出语义与免责声明边界

本系统对外输出时，必须使用克制且可核验的语义：

1. `AUTO_HIT` 的正式解释为“产品内正式命中”，不是行政、司法或评标终局结论；
2. `CLUE` 的正式解释为“需要进一步人工复核或补证的强线索”，不得直接替代违法定性；
3. `OBSERVATION` 的正式解释为“弱异常、弱缺失或信息不足观察”，不得单独作为对外主摘要结论；
4. 任何客户交付版报告、异议辅助包、页面导出、对外 API 文档，都必须附带“基于公开信息自动核查与人工复核辅助，不构成法律意见或行政结论”的免责声明；
5. 对外展示涉及自然人职业信息时，必须遵循最小化展示原则。

### 1.5.1 客户交付字段最小控制原则

对外页面、客户交付版报告、演示版页面、导出文件与对外 API，必须使用字段白名单机制，不得依赖“默认全量返回后前端隐藏”的方式控制字段。最低原则如下：

1. 客户交付版默认只允许输出项目摘要、统一事实摘要、经复核允许展示的规则解释、经授权的证据节选与最小必要的自然人职业信息；
2. 外发异议辅助包的字段白名单必须比客户交付版更严格，默认不得输出与异议论点无直接关系的自然人字段、内部注释与中间态对象；
3. 内部 ID、原始抓取路径、完整证据载体引用、内部审计字段、未复核注释、例外台账字段、租户内部 owner 信息，默认属于黑名单字段；
4. 证书编号、联系方式、证件号、账号标识等自然人强识别字段，除非具备明确公开依据、最小必要性说明与外发审批，否则不得进入客户可见结果；
5. 客户交付字段白名单 / 黑名单的具体列表、模板与审批条件，由执行手册维护。


### 1.5.2 字段审批 / 脱敏规则字典原则

客户可见字段除白名单 / 黑名单控制外，还必须纳入字段审批与脱敏规则字典。最低原则如下：

1. 任一客户可见字段都必须声明 `field_classification`，至少区分：公开摘要字段、客户可见解释字段、条件性自然人职业字段、禁止外发字段；
2. 任一条件性字段都必须声明 `approval_required`、`approval_role`、`masking_rule` 与 `external_audit_required`；
3. 证书编号、联系方式、账号标识、完整内部 ID、原始载体路径与未复核说明，默认属于高限制字段，不得仅凭前端隐藏处理；
4. 同一字段在不同交付对象中的展示级别必须一致可解释，不得在演示版、导出版与客户交付版中随意漂移；
5. 字段审批 / 脱敏规则的机器可读字典由执行手册维护，并必须与客户交付字段白名单 / 黑名单同步更新。

### 1.6 用户角色与责任分层

中国落地版本至少应支持以下角色分层：

- **产品管理员**：维护系统配置、源登记、覆盖等级与权限；
- **核查分析员**：查看公告链、规则结果、证据对象与项目事实；
- **人工复核员**：处理 `review_request`、复核冲突、执行人工覆盖；
- **经营 / 销售用户**：查看 `project_fact`、经营判断、可售状态与摘要，不默认查看全部证据载体；
- **客户只读用户**：仅查看已授权的项目摘要、证据节选与正式交付物。

最低责任边界如下：

1. 能导出外发包的角色，必须经过明确授权；
2. 能查看完整证据载体与自然人信息的角色，必须具备日志留痕；
3. 人工覆盖只允许由复核角色执行，不得由销售用户直接修改结果；
4. 客户只读用户默认不得访问原始抓取层、结构化真相层与未复核的中间态结果。


---

## 2. 系统总体基线与阶段成立标准

### 2.1 总体基线

AX9S 的建设工程域必须以九阶段闭环方式成立，而不是若干页面、脚本或独立服务的松散堆叠。系统至少满足以下基线：

1. 系统由九个阶段构成；
2. 每个阶段同时具备明确输入、明确处理、明确输出、明确承接目标；
3. 阶段之间必须顺序承接，而不是并列堆叠；
4. 阶段 6 必须是唯一统一事实中枢；
5. 阶段 8 与阶段 9 的反馈必须回写阶段 6；
6. 阶段 9 在必要时必须触发阶段 4 的补证或重核验；
7. 系统闭环成立的最低标准是：上一阶段产物已经被下一阶段真实消费。

### 2.2 阶段成立最低标准

任一阶段只有同时满足以下四项时，才能判定为成立：

1. 阶段输入存在；
2. 阶段处理真实发生；
3. 阶段输出真实形成；
4. 阶段输出已经进入下一阶段并被真实消费。

只满足前三项、不满足第四项，不得判定为已打通。

### 2.3 页面存在不是成立标准

页面、按钮、卡片、列表、导出入口、接口壳子都不是成立标准。成立标准只能是：

- 业务处理真实发生；
- 输出对象真实形成；
- 下一阶段真实消费。

---

## 3. 建设工程域范围与公开边界

### 3.1 领域适用范围

建设工程域只在阶段 2 至阶段 6 具有专有规则：

- 阶段 1：沿用系统基线，不增加领域特例；
- 阶段 2：增加工程域公开源、公告链、诊断与公开链对象；
- 阶段 3：增加工程域结构化对象与单一真相层约束；
- 阶段 4：增加公开核查专题、证据分级、规则结果与请求核验事项；
- 阶段 5：增加项目核查简报、证据包、异议草稿、人工复核与正式报告对象；
- 阶段 6：增加统一项目事实、经营消费字段与可售判断；
- 阶段 7 至阶段 9：只消费阶段 6 统一事实，不扩写工程域主判断。

### 3.2 公开边界硬约束

建设工程域公开核查层不得把以下内容作为自动核查前置输入：

- 招投标后台日志；
- 制作机器码、上传 IP、下载 IP、预算软件加密锁；
- 原始 XML 清单比对结果；
- 需要内部账号或内部人员导出的文件；
- 非公开社保明细、非公开人员档案、非公开合同附件；
- 任何来自封闭系统、私下获取、无法公开回链的证据。

上述事项只能进入请求核验事项，不得直接写成自动命中。

### 3.3 结果边界硬约束

- `AUTO_HIT`：仅用于公开证据已经足够支撑的正式命中；
- `CLUE`：用于需要进一步核验的强线索；
- `OBSERVATION`：用于弱异常、弱缺失或信息不充分观察；
- `OBSERVATION` 不得在页面、报告、异议导出中伪装成硬结论；
- `CLUE` 不等于法律定性，不得替代监管机关或评标委员会的终局认定。

---

## 4. 九阶段标准定义

### 阶段 1：任务编排

**职责**  
定义系统何时、何地、按何条件启动主链任务。该阶段是启动控制面，不是抓取层，也不是展示层。

**输入**  
启动指令、时间范围、区域范围、抓取或执行条件、任务模板、重跑策略。

**处理**  
保存任务配置、启动任务、停止任务、暴露运行态、记录调度计划与执行上下文。

**输出**  
可执行任务、调度状态、运行上下文、可追踪执行流。

**承接**  
阶段 1 输出必须进入阶段 2；若任务编排不能产生真实抓取动作，则后续阶段全部不成立。

### 阶段 2：公告抓取

**职责**  
将外部公开源转化为系统可消费的原始输入，并建立项目对应的公开链。

**输入**  
任务编排输出、公开源入口、项目线索。

**处理**  
发现公告、获取详情页、获取原始 HTML / PDF / 图片或等价原始内容、记录抓取诊断、发现同一项目的开标记录、候选人公示、中标结果、合同订立、履约变更、验收或停工公开线索，并合并形成 `public_chain` 初步节点。

**输出**  
原始公告内容、附件指针、抓取诊断、`public_chain` 初步节点。

**承接**  
阶段 2 输出必须进入阶段 3。

**工程域约束**  
抓取层只负责发现、固化和诊断，不得在该层决定最终业务语义；可以输出 hint，但不得产出最终行业归一、最终候选人排序或最终项目经理归一结果。

### 阶段 3：结构化解析

**职责**  
将原始公告内容转化为正式业务对象，而不是保留为不可用文本。

**输入**  
原始公告内容、附件、抓取诊断、透传 hint。

**处理**  
提取项目、候选人、项目经理、报价、无效标、开标记录、合同与履约、企业信用与处罚对象；统一源族差异，落成同构对象。

**输出**  
`project_base`、`bidder_candidate`、`project_manager`、`invalid_bid`、`opening_record`、`contract_performance`、`credit_penalty`、`public_chain` 正式对象。

**承接**  
阶段 3 输出必须进入阶段 4。

**工程域约束**  
阶段 3 是工程域唯一结构化真相层。抓取层与任务层可以透传 hint，但不得形成第二套归一结果。

### 阶段 4：证据固化与规则核验

**职责**  
把结构化对象转化为可证明、可判断、可用于后续报告和统一事实面的业务依据。

**输入**  
阶段 3 正式结构化对象、`public_chain`、证据素材、规则配置。

**处理**  
固化页面证据与附件证据、形成证据链、执行工程域规则专题、生成 `AUTO_HIT / CLUE / OBSERVATION`、标注证据等级、形成请求核验事项。

**输出**  
`rule_hit`、`evidence`、`review_request`、规则摘要与线索摘要。

**承接**  
阶段 4 输出必须同时进入阶段 5 与阶段 6。

**工程域约束**  
工程域只能基于公开、可回链证据形成自动命中；任何内部权限事项只能降级为请求核验事项，不得直接写成 `AUTO_HIT`。

### 阶段 5：报告与人工复核

**职责**  
将规则与证据转化为正式交付结果，并提供人工复核与导出机制。

**输入**  
规则结果对象、证据对象、请求核验事项对象。

**处理**  
生成项目核查简报、证据包、异议辅助草稿、人工复核任务单、正式报告对象；管理导出、补证、退回和重跑。

**输出**  
项目核查简报、证据包、异议辅助草稿、请求核验事项清单、人工复核任务单、`report_record`。

**承接**  
阶段 5 输出必须进入阶段 6；若只停留在文件下载而没有正式报告对象回写，则阶段 5 不成立。

### 阶段 6：统一项目事实汇总与可售判断

**职责**  
阶段 6 是系统唯一统一承接中枢。它负责将前五阶段结果整合为统一项目事实，并形成页面、接口、经营和后续商业承接的唯一消费面。

**输入**  
基础项目对象、候选人与项目经理对象、规则结果对象、证据对象、正式报告对象、复核状态。

**处理**  
汇总项目综合状态；形成 `sale_gate_status`；形成 `real_competitor_count`、`serviceable_competitor_count`、`competitor_quality_grade`；聚合 `price_cluster_score`、`price_gradient_pattern`；形成事实摘要、风险摘要和经营消费字段。

**输出**  
`project_fact`、可售判断、经营消费字段、页面与接口消费对象。

**承接**  
阶段 6 输出必须同时进入阶段 7、阶段 8、阶段 9 与页面 / API；任何商业、触达、交付与治理链路都不得绕开阶段 6 单独成立。

**工程域约束**  
接口层、页面层、经营层不得绕开 `project_fact` 重新拼装顶层主判断。

#### 阶段 6 补充治理协议

1. `project_fact` 每次正式刷新都必须形成新的 `fact_version`；
2. 阶段 4、阶段 5、阶段 8、阶段 9 回写阶段 6 时必须满足幂等要求；
3. 每次事实刷新都必须记录 `fact_refresh_trigger` 与 `fact_source_summary`；
4. 页面与 API 默认只能读取最近一次**已提交**的统一事实版本，不得读取中间计算态；
5. 事实重算必须保留最近至少一个可回滚版本；
6. 若客户反馈、治理反馈与公开证据结论冲突，不得直接覆盖原有自动结果，必须进入复核状态；
7. 人工复核产生的结果覆盖只允许作用于阶段 5 / 阶段 6 的结果层，不得篡改阶段 3 原始结构化对象；
8. 阶段 6 的任一聚合字段若无法回溯来源对象、来源规则与更新时间，不得视为正式字段。

### 阶段 7：商业承接

**职责**  
将统一项目事实转化为商业对象，使系统从“值得接”进入“正式进入商业链路”。

**输入**  
统一项目事实、可售判断。

**处理**  
形成账户上下文、形成线索、形成商机、形成商业上下文。

**输出**  
商业对象、跟进上下文、账户、线索与商机对象。

**承接**  
阶段 7 输出必须进入阶段 8 与阶段 9。

### 阶段 8：销售触达

**职责**  
将系统判断和商业对象推进到真实客户互动，并形成客户事实。

**输入**  
统一项目事实、商机上下文、联系人上下文、客户上下文。

**处理**  
选择触达对象、执行触达动作、记录反馈、确认客户身份或意向。

**输出**  
触达记录、客户确认结果、反馈摘要、商机推进结果。

**承接**  
阶段 8 输出必须回写阶段 6，必要时进入阶段 9。

### 阶段 9：订单支付交付与治理反馈

**职责**  
将已进入商业链路的对象完成正式执行，并把执行结果重新写回系统。

**输入**  
商业订单对象、支付对象、客户确认结果、执行状态。

**处理**  
生成订单、确认支付、执行交付、执行治理审核、触发补救，必要时触发阶段 4 的补证或重核验。

**输出**  
支付结果、交付结果、治理结果、回写触发信息。

**承接**  
阶段 9 输出必须回写阶段 6，并在必要时触发阶段 4 的补证与重核验。

---

## 5. 正式对象与字段字典

### 5.1 命名收敛规则

唯一正式字段名：

- `public_chain_status`
- `result_type`
- `evidence_grade`

兼容层旧口径不得继续作为新开发主字段，不得重新进入新对象与新接口。

补充约束：

1. 正式枚举、单位、时间表示、金额口径、空值 / 空数组约定，统一见附录 A；
2. 页面、接口、报表、任务日志中出现的正式字段名必须与本文保持一致；
3. 未登记为正式枚举、正式字段或正式对象的实现命名，不得直接上升为主口径。

### 5.2 基础项目对象 `project_base`

`project_base` 是阶段 3 结构化解析产出的基础项目实体，只承载公开源可直接结构化得到的项目事实，不承载阶段 6 聚合结果。

必须至少包含：

- `project_id`
- `source_family`
- `region_code`
- `project_name`
- `project_type_raw`
- `engineering_domain`
- `bid_control_price`
- `bid_eval_method`
- `public_chain_status`
- `opening_record_count`
- `invalid_bid_count`

### 5.3 候选人与报价对象 `bidder_candidate`

必须至少包含：

- `bidder_id`
- `project_id`
- `bidder_name`
- `candidate_rank`
- `bid_price`
- `price_score`
- `total_score`
- `is_invalid`
- `invalid_reason_raw`
- `candidate_publication_status`
- `is_real_competitor`
- `is_serviceable_competitor`

### 5.4 项目经理对象 `project_manager`

必须至少包含：

- `project_manager_id`
- `project_id`
- `project_manager_name`
- `project_manager_role_raw`
- `project_manager_role_normalized`
- `project_manager_cert_label`
- `project_manager_cert_no`
- `project_manager_cert_specialty`
- `project_manager_cert_level`
- `project_manager_cert_unit`
- `project_manager_cert_valid_until`
- `pm_public_profile_url`
- `project_manager_public_cert_status`
- `project_manager_conflict_clue_status`

### 5.5 公开链对象 `public_chain`

必须至少包含：

- `public_chain_id`
- `project_id`
- `public_chain_status`
- `announcement_url`
- `opening_record_url`
- `candidate_publication_url`
- `result_publication_url`
- `contract_publication_urls`
- `performance_change_urls`
- `credit_penalty_urls`
- `timeline_nodes`
- `missing_nodes`
- `last_refreshed_at`

### 5.6 无效标对象 `invalid_bid`

必须至少包含：

- `invalid_bid_id`
- `project_id`
- `bidder_id`
- `bidder_name`
- `raw_reason`
- `normalized_reason_code`
- `source_url`
- `source_publication_type`
- `matched_disqualification_clause`
- `reason_publication_status`

### 5.7 开标记录对象 `opening_record`

必须至少包含：

- `opening_record_id`
- `project_id`
- `publication_url`
- `publication_time`
- `opening_time`
- `bidder_id`
- `bidder_name`
- `bid_price`
- `price_score`
- `rank_in_opening_record`
- `record_completeness_status`

### 5.8 合同与履约对象 `contract_performance`

必须至少包含：

- `contract_id`
- `project_id`
- `signed_date`
- `contract_period_start`
- `contract_period_end`
- `performance_change_flag`
- `pm_change_flag`
- `acceptance_flag`
- `acceptance_date`
- `contract_change_summary`

### 5.9 企业信用与处罚对象 `credit_penalty`

必须至少包含：

- `credit_penalty_id`
- `project_id`
- `entity_type`
- `entity_name`
- `entity_id_ref`
- `penalty_type`
- `penalty_status`
- `penalty_start_date`
- `penalty_end_date`
- `penalty_source_url`
- `blacklist_flag`
- `prior_collusion_flag`

### 5.10 证据对象 `evidence`

必须至少包含：

- `evidence_id`
- `project_id`
- `source_url`
- `source_type`
- `capture_type`
- `capture_time`
- `page_title`
- `snippet`
- `evidence_artifact_refs`
- `structured_field_refs`
- `consumed_by_rule_codes`
- `evidence_grade`
- `evidence_hash`

补充约束：

1. `evidence_artifact_refs` 只表达证据载体引用，不在本文锁死底层存储路径命名；
2. 具体存储介质、目录规则、文件命名、留存周期与脱敏要求，由执行手册或专项技术设计规定；
3. 任一 `evidence` 若不可回链原始来源或不可追溯载体生成时间，不得作为 `AUTO_HIT` 的唯一依据。

### 5.11 规则结果对象 `rule_hit`

必须至少包含：

- `rule_hit_id`
- `project_id`
- `rule_code`
- `severity`
- `confidence`
- `result_type`
- `why_hit`
- `boundary_note`
- `evidence_refs`
- `target_entity_type`
- `target_entity_id`
- `review_status`

补充约束：

1. `confidence` 范围限定为 `0-1`；
2. `severity`、`result_type`、`review_status` 必须使用附录 A 中的正式取值；
3. 任一正式 `rule_hit` 若缺失 `boundary_note` 或 `evidence_refs`，不得进入正式报告与正式接口。

### 5.12 请求核验事项对象 `review_request`

必须至少包含：

- `request_id`
- `project_id`
- `request_type`
- `reason`
- `public_basis`
- `requested_materials`
- `priority`
- `source_rule_codes`

### 5.13 正式报告对象 `report_record`

必须至少包含：

- `report_id`
- `project_id`
- `brief_path`
- `evidence_pack_path`
- `objection_draft_path`
- `review_request_list_path`
- `review_task_status`
- `report_status`
- `written_back_at`



补充说明：

1. `objection_draft_path` 为历史兼容字段名，正式业务语义统一解释为“异议辅助草稿”载体路径；
2. 内部研判版、客户交付版、外发异议辅助版可以共用 `report_record` 主对象，但必须在执行手册约定的导出策略中区分权限、脱敏、免责声明与证据等级；
3. 对外版本若包含自然人职业信息、证书信息或联系方式，必须经过最小化展示与外发审计控制。

### 5.14 统一项目事实对象 `project_fact`

`project_fact` 是阶段 6 唯一正式统一事实对象，供页面、接口、经营、阶段 7 至阶段 9 与消息策略消费。

必须至少包含：

- `project_id`
- `fact_version`
- `fact_refresh_trigger`
- `fact_source_summary`
- `public_chain_status`
- `rule_hit_summary`
- `clue_summary`
- `sale_gate_status`
- `real_competitor_count`
- `serviceable_competitor_count`
- `competitor_quality_grade`
- `price_cluster_score`
- `price_gradient_pattern`
- `fact_summary`
- `risk_summary`
- `review_status`
- `manual_override_status`
- `last_fact_refreshed_at`

硬约束：

1. `project_fact` 中的任一聚合字段必须可回溯到阶段 3、阶段 4、阶段 5 的正式对象或复核状态；
2. 接口层不得绕过 `project_fact` 重新拼装主判断；
3. 页面与经营侧主判断必须优先消费 `project_fact`；
4. `fact_version` 必须单调递增或满足可比较版本策略；
5. 人工复核覆盖存在时，必须通过 `manual_override_status` 明示，而不是静默覆盖自动结论；
6. 页面必须能够区分“自动聚合结论”与“人工复核覆盖结论”。

### 5.15 聚合字段计算规范

以下聚合字段必须具备可计算定义，不得只保留字段名而缺少裁决口径：

#### 5.15.1 `sale_gate_status`

- `OPEN`：公开链完整度、规则摘要与竞争者判断均满足最低可售条件，且不存在未决高优先级复核阻断；
- `REVIEW`：存在中高风险线索、证据冲突或人工复核待确认事项；
- `HOLD`：存在重大未决问题、关键证据缺失或客户反馈与公开证据冲突未完成复核；
- `BLOCK`：存在足以阻断售卖或阻断继续推进的正式命中、合规限制或业务否决条件。

#### 5.15.2 `competitor_quality_grade`

- `A`：真实竞争者识别充分，公开链完整，关键竞争信息稳定；
- `B`：真实竞争者识别基本成立，但仍存在少量缺失或需要人工确认；
- `C`：竞争者识别存在较大不确定性，只适合作为弱经营参考；
- `D`：竞争者识别不稳定，不得作为正式经营判断依据。

#### 5.15.3 `price_cluster_score` 与 `price_gradient_pattern`

- `price_cluster_score` 取值范围限定为 `0-100`；
- `price_gradient_pattern` 必须使用受控枚举或受控模式字典，不得直接返回自由文本作为正式主字段；
- 任何价格类聚合若样本不足、开标记录缺失或无效标信息缺失，必须降级并写明 `boundary_note`。

#### 5.15.4 缺失值、冲突与人工覆盖

1. 聚合字段缺失时，必须区分“未知”“不适用”“空结果”三种状态；
2. 事实聚合遇到证据冲突时，不得默认选择最新数据覆盖旧数据，必须进入 `REVIEW` 或触发复核；
3. 人工覆盖只允许覆盖阶段 6 结果字段，不得修改阶段 3 原始真相层；
4. 任一聚合字段若没有来源对象、时间戳与计算版本，不得对外作为正式口径。

---

## 6. 公开核查规则专题

> 说明：本章定义专题边界、前置对象、结果类型与回写字段；正式 `rule_code`、最低证据等级与专题裁决基线，统一见附录 B《规则码总表》。

### 6.1 项目负责人资格核查

- 公开输入：招标文件或公告资格条件、候选人公示中的项目负责人信息、四库一平台或地方住建公开页、公开 B 证信息；
- 前置对象：`project_base`、`project_manager`、`bidder_candidate`；
- 结果类型：`AUTO_HIT`、`CLUE`；
- 回写字段：`project_manager_public_cert_status`、`rule_hit_summary`、`sale_gate_status`。

### 6.2 项目负责人在建冲突线索核查

- 公开输入：近 6-12 个月中标、公示、合同订立、工期重叠、变更、验收、停工公开线索；
- 前置对象：`project_base`、`project_manager`、`contract_performance`、`public_chain`；
- 结果类型：默认 `CLUE`，证据极弱时为 `OBSERVATION`；
- 回写字段：`project_manager_conflict_clue_status`、`clue_summary`。

### 6.3 报价异常聚集与规律性梯度核查

- 公开输入：开标记录报价、候选人公示精确报价、最高投标限价、评标办法公开文本；
- 前置对象：`bidder_candidate`、`opening_record`、`project_base`；
- 结果类型：`CLUE`，证据不足时为 `OBSERVATION`；
- 回写字段：`price_cluster_score`、`price_gradient_pattern`、`clue_summary`、`competitor_quality_grade`。

### 6.4 真实竞争者识别

- 公开输入：全体公开报价、无效标名单、无效理由、候选人排序和得分表；
- 前置对象：`bidder_candidate`、`invalid_bid`、`rule_hit`；
- 结果类型：`AUTO_HIT` 用于产品主口径，无法形成稳定识别时补 `CLUE`；
- 回写字段：`real_competitor_count`、`serviceable_competitor_count`、`competitor_quality_grade`、`sale_gate_status`。

### 6.5 无效标与资格后审结构核查

- 公开输入：无效标名单、无效理由、排名结果、资格条件文本、否决条款文本；
- 前置对象：`bidder_candidate`、`invalid_bid`、`project_base`；
- 结果类型：`CLUE`、`OBSERVATION`；
- 回写字段：`invalid_bid_count`、`clue_summary`、`rule_hit_summary`。

### 6.6 企业关联关系核查

- 公开输入：国家企业信用信息公示系统、公开企业信息页、法定代表人、股东、高管、历史变更、地址、电话等；
- 前置对象：`bidder_candidate`、`credit_penalty`；
- 结果类型：`CLUE`，证据极弱时为 `OBSERVATION`；
- 回写字段：`clue_summary`、`competitor_quality_grade`。

### 6.7 企业与人员信用处罚核查

- 公开输入：四库一平台信用记录、处罚记录、黑名单、地方住建信用栏目、行政处罚决定书、串标或骗中标处罚公示；
- 前置对象：`credit_penalty`、`project_manager`、`project_base`；
- 结果类型：`AUTO_HIT`、`CLUE`；
- 回写字段：`rule_hit_summary`、`sale_gate_status`、`competitor_quality_grade`。

### 6.8 程序公开充分性核查

- 公开输入：招标公告、澄清修改公告、开标记录、候选人公示、结果公告、合同订立与变更公开信息；
- 前置对象：`project_base`、`public_chain`、`invalid_bid`、`opening_record`；
- 结果类型：`OBSERVATION`、`CLUE`；
- 回写字段：`public_chain_status`、`clue_summary`、`rule_hit_summary`。

### 6.9 结果裁决矩阵

工程域规则执行时，必须按以下矩阵裁决，不得由页面、接口或人工口头约定替代：

1. 满足“公开、可回链、证据充分、前置对象齐全、边界说明完整”时，才允许输出 `AUTO_HIT`；
2. 存在较强公开依据，但仍需外部补证、人工核验或内部材料确认时，只允许输出 `CLUE`；
3. 公开信息弱、链路缺失、对象不完整或证据等级不足时，只允许输出 `OBSERVATION`；
4. 任一结果若缺失 `boundary_note`、`evidence_refs` 或最低证据等级，不得进入正式结果面；
5. 内部权限材料、私下获取材料、不可回链材料，只能形成 `review_request` 或对 `CLUE / OBSERVATION` 提供辅助解释，不得单独形成 `AUTO_HIT`；
6. 多条证据互相冲突时，不得直接选择对业务最有利的一条，必须进入复核或重核验流程；
7. `OBSERVATION` 不得默认进入异议导出包，`B / C` 级证据不得默认作为异议主证据。

---

## 7. 页面与接口消费原则

### 7.1 正式页面

正式页面固定为：

- 任务编排页；
- 项目页；
- 监控页；
- 深链页；
- 证据工作台；
- 异议工作台；
- 经营页；
- 规则后台。

页面消费约束：

1. 项目页、监控页、经营页必须优先消费 `project_fact`；
2. 深链页必须消费 `public_chain` 与 `public_chain_status`；
3. 证据工作台必须消费 `evidence` 与 `rule_hit`；
4. 异议工作台必须消费 `review_request` 与 `report_record`；
5. 页面不得通过抓取层、接口拼装层或前端临时逻辑形成新的主判断。

### 7.2 接口消费原则

正式约束的核心不在于 URL 数量，而在于不同类型接口必须消费正确的正式对象：

- 主判断类接口优先消费 `project_fact`；
- 规则解释类接口读取 `rule_hit`；
- 链路追溯类接口读取 `public_chain`；
- 证据与复核类接口分别读取 `evidence`、`review_request`、`report_record`。

### 7.3 接口硬约束

**主判断类接口**  
如 `GET /projects/{id}/public-check`、`GET /projects/{id}/competitors`：

- 必须优先读取 `project_fact`；
- 可以引用规则结果面解释来源；
- 不得在接口层重算顶层状态。

**规则解释类接口**  
如 `GET /projects/{id}/rules`：

- 必须读取 `rule_hit`；
- 必须返回 `rule_code`、`result_type`、`evidence_grade`、`why_hit`、`boundary_note`、`evidence_refs`。

**链路追溯类接口**  
如 `GET /projects/{id}/public-chain`：

- 必须读取 `public_chain`；
- 可展示 `public_chain_status`；
- 不得在接口层临时拼装新的链状态规则。

**证据与复核类接口**  
如 `GET /projects/{id}/evidence`、`GET /projects/{id}/review-requests`、`POST /reports/{id}/build-objection-pack`：

- 必须分别读取 `evidence`、`review_request`、`report_record`；
- `GET /projects/{id}/review-requests` 必须返回对象而不是仅返回导出文件；
- `POST /reports/{id}/build-objection-pack` 必须支持默认导出 A 级、人工追加 B 级、排除 C 级。

> 说明：当前标准接口清单见附录 C。附录 C 属于“当前标准基线”，未来 URL 变更以契约清单登记为准；真正不可被变更削弱的是本章定义的消费对象与消费边界。


### 7.4 外发报告、客户交付版与异议辅助包边界

阶段 5 与阶段 6 的正式对象可以支撑多种交付形态，但必须明确区分：

- **内部研判版**：供内部分析、经营研判与复核使用，可见完整摘要、规则结果与授权证据；
- **客户交付版**：供客户查看核查结论与证据节选，必须附带免责声明、权限控制与最小化展示；
- **外发异议辅助包**：用于支持客户或内部团队准备正式异议材料，默认导出 A 级证据，B 级需显式勾选，C 级不得默认纳入主证据。

硬约束如下：

1. 对外版本默认不得把 `OBSERVATION` 写入首页主摘要；
2. 对外版本默认不得将“产品正式命中”表述成监管或司法终局认定；
3. 对外版本若包含自然人职业信息、证书编号、联系方式或其他敏感上下文，必须执行最小化展示、脱敏与外发审计；
4. 外发异议辅助包的正式名称统一为“异议辅助包”，不得在产品宣传中表述为“自动异议文书”或“自动投诉结论包”。

### 7.4.1 客户交付字段白名单 / 黑名单原则

客户可见交付物的字段控制必须遵守以下最小原则：

**默认白名单**

- 项目级摘要：`project_name`、`region_code`、`source_family`、`public_chain_status`；
- 统一事实摘要：`sale_gate_status`、`real_competitor_count`、`serviceable_competitor_count`、`competitor_quality_grade`、`price_cluster_score`、`price_gradient_pattern`、`fact_summary`、`risk_summary`；
- 规则解释节选：`rule_code`、`result_type`、`why_hit`、`boundary_note`、`evidence_grade`、经批准的 `source_url` 或证据节选；
- 交付元信息：`report_status`、`last_fact_refreshed_at`、`manual_override_status`。

**条件性白名单**

- 自然人职业信息：项目负责人姓名、角色、专业、等级、公开任职轨迹；
- 企业处罚与信用信息：企业名称、处罚类型、处罚状态、公开处罚来源；
- 证据节选图片、 PDF 页面、公开截图。

上述字段只有在“公开可回链 + 与核查目的直接相关 + 已完成最小化展示 + 已通过外发审批”四项同时满足时，方可进入客户可见版本。

**默认黑名单**

- 内部 ID、原始 HTML / PDF 存储路径、`evidence_artifact_refs` 全量明细；
- 内部审计日志、例外台账、owner 字段、内部评注、未复核 `review_request` 细节；
- 完整证书号、联系方式、证件号、账号标识及其他高识别度字段；
- 未完成复核的中间计算态、草稿态、临时规则输出。

### 7.4.2 人工覆盖客户可见版本规则

人工覆盖进入客户可见版本时，必须遵守以下规则：

1. `manual_override_status` 必须对客户可见，至少区分 `PENDING / CONFIRMED / REJECTED` 或等价状态；
2. `PENDING` 覆盖不得替代首页主结论，只能标记为“复核中”或等价语义；
3. `CONFIRMED` 覆盖可以影响客户可见的阶段 5 / 阶段 6 结果层，但必须展示覆盖时间、状态与原因摘要；
4. `REJECTED` 覆盖不得继续出现在客户首页主摘要中，只保留在内部审计与复核记录中；
5. 客户可见版本不得展示内部复核人的个人身份信息，只可展示角色类型或组织级说明；
6. 任何人工覆盖都不得反向篡改阶段 3 原始结构化对象。


### 7.4.3 对象级交付字段矩阵原则

客户交付控制不得只停留在字段列表，还必须落实到“对象 × 交付形态 × 字段组”的矩阵。最低矩阵原则如下：

1. 至少对 `project_base`、`project_fact`、`rule_hit`、`evidence`、`review_request`、`report_record` 六类对象维护对象级交付矩阵；
2. 至少区分以下交付形态：内部研判版、客户交付版、外发异议辅助包、演示版页面、对外 API；
3. 每个对象在每种交付形态中都必须标记：允许字段、条件性字段、禁止字段、是否需要审批、是否需要脱敏、是否需要审计留痕；
4. 任一对象若未进入矩阵，不得默认“按字段白名单自动外发”；
5. 矩阵冲突时，以更严格的字段黑名单、审批与脱敏规则为准。

### 7.5 中国 MVP 产品核心范围

中国首发版本的正式产品核心范围固定为阶段 2 至阶段 6：

1. 阶段 2：公告抓取与公开链发现；
2. 阶段 3：结构化解析；
3. 阶段 4：规则核查、证据固化与请求核验事项；
4. 阶段 5：项目核查简报、证据包、异议辅助草稿、人工复核任务单与正式报告对象；
5. 阶段 6：统一项目事实、经营消费字段与可售判断。

阶段 7 至阶段 9 在中国 MVP 中属于可选商业配套能力：

- 可作为 CRM、销售触达、交付治理与反馈回写的后续版本能力；
- 不作为首发销售材料中的核心承诺；
- 不得反向要求首发产品在未验证前承诺“全链路商业闭环”。


---

## 8. 测试与验收原则

### 8.1 测试分层

- 单元测试：解析器、公开链合并逻辑、规则引擎、真实竞争者 helper、证据分级逻辑、导出筛选逻辑；
- 集成测试：从抓取到结构化、规则、报告、阶段 6 回写的完整承接；
- 页面测试：正式页面必须真实消费正式对象；
- 回归测试：字段字典、结果枚举、证据分级、报告模板、经营评分口径不得被破坏。

### 8.2 阶段验收

**P0 统一底座**

- 正式对象分层冻结；
- 核心字段与枚举冻结；
- 阶段口径固定；
- 不再边开发边发明主字段、主对象、主判断。

**P1 公开链抓取**

- 至少 1 个公开源族可稳定抓取；
- `public_chain` 可形成初步节点；
- 原始 HTML / PDF / 附件指针可追溯；
- 阶段 2 输出已被阶段 3 真实消费。

**P2 解析与硬资格**

- `project_base`、候选人、项目经理、无效标、开标记录、合同、处罚对象可结构化；
- 项目负责人资格专题可稳定输出；
- 阶段 3 输出已被阶段 4 真实消费。

**P3 报价与竞争者**

- 报价异常与真实竞争者识别可稳定输出；
- `project_fact` 可形成最小版 `sale_gate_status` 与竞争者字段；
- 阶段 4 结果已进入阶段 6。

**P4 证据与异议**

- 项目核查简报、证据包、异议辅助草稿、请求核验事项清单、人工复核任务单、正式报告对象全部可生成；
- A / B / C 导出规则生效；
- 正式报告对象回写阶段 6。

**P5 统一事实与消费**

- 页面与 API 只消费正式对象；
- 监控页、经营页、消息策略接入统一事实面；
- 阶段 8 / 9 反馈可回写阶段 6，并在必要时触发阶段 4 重核验。

### 8.3 边界验收

必须同时满足：

1. 内部权限依赖事项全部降级为请求核验事项；
2. `OBSERVATION` 不得在页面或报告中伪装成硬结论；
3. `B` 级线索不默认进入异议导出包；
4. 任一页面均不得绕开阶段 6 拼装主判断。

### 8.4 业务效果验收

除工程正确性外，还必须验证业务正确性。最低要求如下：

1. 每个规则专题必须维护最小金标样本集；
2. 每次规则变更必须输出命中率变化、误报样本数、漏报样本数与漂移说明；
3. 重点地区、重点公开源族必须保留专题回归样本；
4. 真实竞争者识别、项目负责人资格核查、程序公开充分性核查，必须至少具备一组可复现业务回归集；
5. 若业务效果显著下降，即使单测与集成测试通过，也不得视为验收通过。


### 8.5 中国 MVP 发布准入原则

中国首发版本在正式对外售卖前，至少应满足：

1. 已明确产品定位、免责声明与外发边界；
2. 已完成至少一个重点地区的 L1 主链验证；
3. 已完成至少三个 MVP 规则专题的金标回归；
4. 已形成客户交付版与外发异议辅助包的权限、脱敏与审计策略；
5. 未纳入覆盖登记表的地区、专题与源族，不得对外承诺为“稳定支持”。


---

### 8.5.1 覆盖成熟度动态降级原则

地区、源族或专题一旦出现下列情形，必须触发动态降级、停售或重新验证：

1. 重大客户投诉被确认且指向覆盖成熟度、规则稳定性或客户可见字段错误；
2. 重点地区、重点专题连续两次回归显著下降；
3. 核心公开源连续失效超过执行手册规定窗口；
4. 发生对外报告合规事故、自然人字段越权外发或租户隔离事故；
5. `last_verified_at` 超出允许窗口而未重新验证；
6. 依赖的受控例外过期、撤销或未恢复正式口径。

触发动态降级后，必须在执行手册规定时限内回写覆盖登记，并停止相应地区、专题或源族的可售承诺。


### 8.5.2 售后降级 / 恢复 SLA 与审计链原则

覆盖成熟度治理必须具备明确 SLA 与审计链，最低要求如下：

1. 重大客户投诉、重大外发事故、自然人字段越权外发、租户隔离事故被确认后，必须在 `1` 个工作日内完成降级回写；
2. 核心公开源连续失效、连续回归下降、验证窗口过期等非事故类问题，必须在执行手册规定窗口内完成限制售卖、暂停售卖或重新验证；
3. 任何恢复到 `SELLABLE` 的动作，都必须在恢复前补齐复验样本、恢复说明、审批记录与恢复时间戳；
4. 地区可售状态的降级、暂停、恢复、续签与关闭都必须形成可审计事件链，不得只保留最终状态；
5. 审计链至少应记录：`event_id`、`region_code`、`from_state`、`to_state`、`trigger_type`、`trigger_summary`、`owner`、`approved_by`、`occurred_at`、`resolved_at`、`evidence_refs`、`post_action`。

## 9. 迁移与兼容原则

### 9.1 迁移原则

1. 既有历史口径仅允许存在于兼容层；
2. 兼容层旧字段不得继续作为新开发主字段；
3. 不得在同一任务中同时完成“重命名 + 语义改变 + 删除旧字段”；
4. 优先采用先加后删、先兼容后切换、最后清理的方式；
5. 涉及阶段 6 聚合字段的变更，必须同步更新聚合逻辑与测试；
6. 涉及正式报告对象的变更，必须同步更新导出与快照测试。

### 9.2 不再保留的旧口径

以下旧口径不得继续作为主定义：

- 以 loser-first 逻辑作为顶层主判断；
- 用“报告页”替代“证据工作台 + 异议工作台”的页面定义；
- 在抓取层、接口层、页面层临时拼装主判断；
- 使用与本文冲突的历史字段命名和历史对象边界。

---

## 10. 变更治理原则

### 10.1 领域变更底线

任何涉及建设工程域的实现变更，都必须遵守：

1. 不得绕开阶段 6 建第二套主判断；
2. 不得新增第二套结构化真相层；
3. 不得把阶段逻辑写进页面层；
4. 不得把内部权限事项伪装成公开自动命中；
5. 不得用仓库局部实现反向定义领域对象与领域边界。

### 10.2 变更先后顺序

- 改对象边界，先改本文；
- 改页面 / API 主消费原则，先改本文；
- 改规则码总表、枚举总表、当前标准接口清单，先改本文或本文附录；
- 改目录、CI、任务模板、PR 流程、例外台账字段，改执行手册；
- 若执行手册与本文冲突，以本文为准。

### 10.3 证据载体与留存治理原则

1. 权威文档只规定证据必须可回链、可审计、可被规则与报告消费；
2. 证据载体的存储介质、命名规则、脱敏、访问控制、留存周期与删除策略，由执行手册或专项技术设计定义；
3. 若证据留存策略变化影响到正式证据可用性，必须同步更新执行手册、导出规则与测试；
4. 不得把底层存储路径格式上升为领域主定义。

---

## 附录 A：正式枚举、单位与表示总表

### A.1 正式枚举总表

- `result_type`：仅允许 `AUTO_HIT / CLUE / OBSERVATION`
- `evidence_grade`：仅允许 `A / B / C`
- `sale_gate_status`：仅允许 `OPEN / REVIEW / HOLD / BLOCK`
- `review_status`：仅允许 `PENDING / CONFIRMED / REJECTED / OVERRIDDEN`
- `report_status`：仅允许 `DRAFT / READY / ISSUED / REVOKED`
- `competitor_quality_grade`：仅允许 `A / B / C / D`
- `severity`：仅允许 `HIGH / MEDIUM / LOW`
- `candidate_publication_status`、`record_completeness_status`、`penalty_status` 等枚举若在实现中作为正式对象字段使用，必须同步纳入契约清单与实现枚举表。

### A.2 时间、金额、分数与空值约束

- 时间默认表示：带时区 ISO 8601；若公开源仅提供本地时间，入库时必须补充来源时区说明；
- 金额默认单位：人民币元；若来源币种不同，必须显式标记币种与换算策略；
- 分数字段默认使用十进制数；除特别说明外，常规评分范围为 `0-100`；
- `confidence` 范围固定为 `0-1`；
- 列表 URL 字段默认可为空数组，不建议使用 `null` 表达“空集合”；
- 评分字段默认保留不超过两位小数；
- 若需突破上述统一口径，必须走受控例外并登记台账。

---

## 附录 B：规则码总表

> 说明：本附录给出当前正式规则码、默认结果类型与最低证据等级基线。实现可新增更细子规则，但不得绕开专题边界、不得修改正式结果语义，新增正式规则码必须先更新本附录。

| 专题 | 标准规则码 | 默认结果类型 | 最低证据等级基线 | 主要回写字段 |
|---|---|---|---|---|
| 项目负责人资格核查 | `PM_CERT_PROFESSION_MISMATCH` | AUTO_HIT | A | `project_manager_public_cert_status`, `rule_hit_summary`, `sale_gate_status` |
| 项目负责人资格核查 | `PM_CERT_LEVEL_MISMATCH` | AUTO_HIT | A | 同上 |
| 项目负责人资格核查 | `PM_CERT_UNIT_MISMATCH` | AUTO_HIT | A | 同上 |
| 项目负责人资格核查 | `PM_CERT_EXPIRED` | AUTO_HIT | A | 同上 |
| 项目负责人资格核查 | `PM_CERT_PUBLIC_INFO_CONFLICT` | CLUE | B | 同上 |
| 项目负责人在建冲突线索核查 | `PM_OVERLAP_PROJECT_CLUE` | CLUE | B | `project_manager_conflict_clue_status`, `clue_summary` |
| 项目负责人在建冲突线索核查 | `PM_POSSIBLE_IN_SERVICE_CLUE` | CLUE | B | 同上 |
| 项目负责人在建冲突线索核查 | `PM_CHANGE_NOT_PUBLICLY_CLEARED_CLUE` | CLUE | B | 同上 |
| 项目负责人在建冲突线索核查 | `PM_CONTRACT_PERIOD_OVERLAP_CLUE` | CLUE | B | 同上 |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_CLUSTERING` | CLUE | B | `price_cluster_score`, `price_gradient_pattern`, `clue_summary`, `competitor_quality_grade` |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_REGULAR_GRADIENT` | CLUE | B | 同上 |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_TWIN_VALUES` | CLUE | B | 同上 |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_EXTREME_NARROW_BAND` | CLUE | B | 同上 |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_PATTERN_CLUE` | OBSERVATION | C | 同上 |
| 真实竞争者识别 | `REAL_COMPETITOR_IDENTIFIED` | AUTO_HIT | A | `real_competitor_count`, `serviceable_competitor_count`, `competitor_quality_grade`, `sale_gate_status` |
| 真实竞争者识别 | `SERVICEABLE_COMPETITOR_IDENTIFIED` | AUTO_HIT | A | 同上 |
| 真实竞争者识别 | `STRONG_COMPETITOR_REMOVED_CLUE` | CLUE | B | 同上 |
| 真实竞争者识别 | `ABNORMAL_PRICE_CLUSTER_FILTERED` | CLUE | B | 同上 |
| 无效标与资格后审结构核查 | `INVALID_BID_FILTER_PATTERN_CLUE` | CLUE | B | `invalid_bid_count`, `clue_summary`, `rule_hit_summary` |
| 无效标与资格后审结构核查 | `QUAL_REVIEW_INCONSISTENCY_CLUE` | CLUE | B | 同上 |
| 无效标与资格后审结构核查 | `MISSING_INVALID_REASON_PUBLICATION` | OBSERVATION | C | 同上 |
| 企业关联关系核查 | `BIDDER_SAME_CONTROLLER_CLUE` | CLUE | B | `clue_summary`, `competitor_quality_grade` |
| 企业关联关系核查 | `BIDDER_SAME_LEGAL_REP_CLUE` | CLUE | B | 同上 |
| 企业关联关系核查 | `BIDDER_ADDRESS_OVERLAP_CLUE` | OBSERVATION | C | 同上 |
| 企业关联关系核查 | `BIDDER_PHONE_OVERLAP_CLUE` | OBSERVATION | C | 同上 |
| 企业关联关系核查 | `BIDDER_MANAGEMENT_RELATION_CLUE` | CLUE | B | 同上 |
| 企业与人员信用处罚核查 | `BIDDER_PENALTY_ACTIVE` | AUTO_HIT | A | `rule_hit_summary`, `sale_gate_status`, `competitor_quality_grade` |
| 企业与人员信用处罚核查 | `PM_PENALTY_ACTIVE` | AUTO_HIT | A | 同上 |
| 企业与人员信用处罚核查 | `BIDDER_BLACKLIST_ACTIVE` | AUTO_HIT | A | 同上 |
| 企业与人员信用处罚核查 | `PRIOR_COLLUSION_PENALTY_CLUE` | CLUE | B | 同上 |
| 程序公开充分性核查 | `MISSING_OPENING_RECORD_PUBLICATION` | OBSERVATION | C | `public_chain_status`, `clue_summary`, `rule_hit_summary` |
| 程序公开充分性核查 | `MISSING_FULL_CANDIDATE_PUBLICATION` | OBSERVATION | C | 同上 |
| 程序公开充分性核查 | `MISSING_INVALID_BID_PUBLICATION` | OBSERVATION | C | 同上 |
| 程序公开充分性核查 | `LATE_CRITICAL_CLARIFICATION_CLUE` | CLUE | B | 同上 |
| 程序公开充分性核查 | `PUBLIC_CHAIN_INCOMPLETE` | CLUE | B | 同上 |


### B.1 中国 MVP 默认规则专题成熟度

中国首发版本默认优先承诺以下正式规则专题：

- `PM_CERT_PROFESSION_MISMATCH`、`PM_CERT_LEVEL_MISMATCH`、`PM_CERT_UNIT_MISMATCH`、`PM_CERT_EXPIRED`：`MVP`
- `REAL_COMPETITOR_IDENTIFIED`、`SERVICEABLE_COMPETITOR_IDENTIFIED`：`MVP`
- `MISSING_OPENING_RECORD_PUBLICATION`、`MISSING_FULL_CANDIDATE_PUBLICATION`、`PUBLIC_CHAIN_INCOMPLETE`：`MVP`
- `BIDDER_PENALTY_ACTIVE`、`PM_PENALTY_ACTIVE`、`BIDDER_BLACKLIST_ACTIVE`：`EXPANDED`
- 其他规则码默认视为 `EXPANDED` 或区域化增强能力，未通过地区回归与覆盖登记前，不得对外承诺为稳定可售能力。


---

## 附录 C：当前标准接口清单

> 说明：本附录是当前标准接口基线，服务于路由命名统一与仓库契约对齐；未来 URL 变更时，以机器可读契约清单登记为准，但不得削弱第 7 章定义的消费对象与消费边界。

### C.1 项目与链路

- `GET /projects/{id}/public-check`
- `GET /projects/{id}/public-chain`

### C.2 竞争与规则

- `GET /projects/{id}/competitors`
- `GET /projects/{id}/rules`

### C.3 证据与异议

- `GET /projects/{id}/evidence`
- `GET /projects/{id}/review-requests`
- `POST /reports/{id}/build-objection-pack`

### C.4 规则后台

- `GET /admin/public-check/rules`
- `GET /admin/public-check/audits`
- `POST /admin/public-check/replay`


## 附录 D：覆盖成熟度、对外承诺与角色边界最小总表

### D.1 覆盖成熟度分级

- `L1`：全国公共资源交易平台主链稳定支持；
- `L2`：区域化增强公开源已验证并纳入覆盖登记；
- `L3`：深链增强或复杂附件能力，仅在已验证地区提供。

### D.2 对外承诺最小边界

- 可承诺：公开证据核查、异常线索发现、人工复核辅助、异议 / 报告辅助；
- 不可承诺：自动违法认定、自动替代监管机关结论、全国全地区同等成熟覆盖。

### D.3 角色边界最小总表

- 产品管理员：配置、权限、审计与覆盖等级维护；
- 核查分析员：查看项目、规则、证据与事实摘要；
- 人工复核员：处理复核、覆盖与外发审核；
- 经营 / 销售用户：查看经营摘要与可售状态；
- 客户只读用户：查看授权后的交付结果与节选证据。


---


## 附录 E：售前承诺、客户交付与角色权限红线

### E.1 售前承诺红线

售前材料、演示、报价单、合同附件、客户培训材料与销售话术，必须同时满足以下红线：

1. 不得承诺“自动违法认定”“自动替代监管机关结论”“自动保证异议成功”；
2. 不得承诺全国所有地区、所有专题、所有公告类型同等成熟覆盖；
3. 不得把 `AUTO_HIT` 对外解释为法律终局结论；
4. 不得把未验证地区、未验证源族、未进入金标回归的专题包装为正式稳定能力；
5. 不得省略“基于公开信息核查与人工复核辅助”的产品定位说明。

### E.2 客户交付红线

客户可见交付物默认分为三类：

1. **内部研判版**：允许展示更完整的规则解释、证据摘要、人工复核状态；
2. **客户交付版**：必须附带免责声明、覆盖范围说明、来源说明与版本时间；
3. **异议辅助包**：仅用于辅助整理公开证据、形成论点和复核清单，不得表述为法律意见。

补充红线：

- 客户交付版首页必须声明：基于公开信息自动核查与人工复核辅助，不构成法律意见、行政结论或司法认定；
- 异议辅助包默认不纳入 `C` 级观察项；
- 涉及自然人字段时，必须按最小化展示原则输出；
- 未进入复核通过状态的人工覆盖结果，不得作为客户交付版首页主结论。

### E.3 角色权限红线

- 产品管理员可维护覆盖等级、租户配置与审计策略，但不得绕过复核流直接改写阶段 3 原始对象；
- 核查分析员可查看规则、证据与事实摘要，但不得直接发布客户交付版；
- 人工复核员可处理复核与覆盖，但覆盖必须留下审计记录；
- 经营 / 销售用户只能查看经营摘要、覆盖等级、可售状态与已批准对外口径；
- 客户只读用户默认只可见授权后的客户交付结果与节选证据，不得默认查看全部原始证据与全部自然人字段。

## 附录 F：首版客户交付模板最小条文

### F.1 首页免责声明最小条文

客户交付版、演示版、导出版首页至少应包含以下意思等价条文：

> 本报告基于公开信息进行自动核查与人工复核辅助，结果仅用于项目筛选、经营研判、证据整理与异议辅助，不构成法律意见、行政结论、司法认定或对中标结果的最终判断。

### F.2 覆盖范围说明最小条文

> 本次结果仅在已验证的地区、源族与专题范围内生效。未列入覆盖登记的地区、源族或专题，不视为正式稳定支持范围。

### F.3 自然人信息展示最小条文

> 报告中涉及自然人职业信息、证书信息或任职轨迹时，仅展示与公开核查目的直接相关的最小必要字段；超出最小必要范围的信息不得默认对外展示。

### F.4 异议辅助包说明最小条文

> 异议辅助包用于整理公开证据、提示待核验事项和形成人工复核建议，不保证异议结果，也不替代法定程序中的异议、答复、监督处理与裁判结论。


## 附录 G：客户交付字段控制最小总表

### G.1 客户交付版默认白名单

- 项目摘要：`project_name`、`region_code`、`source_family`、`public_chain_status`；
- 统一事实字段：`sale_gate_status`、`real_competitor_count`、`serviceable_competitor_count`、`competitor_quality_grade`、`price_cluster_score`、`price_gradient_pattern`、`fact_summary`、`risk_summary`；
- 规则解释字段：`rule_code`、`result_type`、`why_hit`、`boundary_note`、`evidence_grade`、经批准的 `source_url` 与证据节选；
- 版本与交付字段：`report_status`、`last_fact_refreshed_at`、`manual_override_status`。

### G.2 异议辅助包条件性白名单

- 与异议论点直接相关的项目负责人公开职业信息；
- 与异议论点直接相关的企业处罚、信用、程序公开性证据；
- 经复核批准的公开截图、页面节选、 PDF 页码节选；
- 经批准的规则解释摘要、请求核验事项摘要。

### G.3 默认黑名单

- 内部 ID、内部 owner、内部评论、内部复核笔记；
- 全量 `evidence_artifact_refs`、内部存储路径、原始抓取日志；
- 完整证书号、联系方式、账号标识、证件号等高识别度字段；
- 未复核中间态对象、草稿态对象、例外台账对象、审计日志对象。

### G.4 使用说明

1. 附录 G 定义的是最小总表，执行手册可在不突破最小化原则的前提下进一步细化机器可读模板；
2. 若客户交付模板需要增加新字段，必须同步更新执行手册中的白名单模板、外发门禁与审计检查；
3. 附录 G 与执行手册的客户交付字段模板冲突时，以更严格者为准。

## 11. 生效结论

自本文档生效起：

1. 建设工程域开发、联调、测试、验收、迁移中的**领域定义**统一只以本文为准；
2. 九阶段基线、领域规则、对象字段、规则专题、页面接口消费原则、测试验收原则与迁移兼容原则，均以本文为正式口径；
3. 任何新增功能都必须回答：输入是什么、处理在哪里发生、输出是什么、谁在消费、是否超出公开边界、是否破坏阶段 6 统一事实中枢；
4. 任一实现若与本文冲突，必须以本文修正实现，不得反向修改本文以迁就临时实现。

---

## 附录 H：地区可售状态机最小总表

```yaml
sellable_state_machine:
  states:
    - NOT_READY
    - VALIDATING
    - SELLABLE
    - RESTRICTED
    - SUSPENDED
    - RECOVERING
  allowed_transitions:
    - from: NOT_READY
      to: VALIDATING
    - from: VALIDATING
      to: SELLABLE
    - from: VALIDATING
      to: NOT_READY
    - from: SELLABLE
      to: RESTRICTED
    - from: SELLABLE
      to: SUSPENDED
    - from: RESTRICTED
      to: SELLABLE
    - from: RESTRICTED
      to: SUSPENDED
    - from: SUSPENDED
      to: RECOVERING
    - from: RECOVERING
      to: SELLABLE
    - from: RECOVERING
      to: SUSPENDED
```

## 附录 I：客户交付字段矩阵最小示意

```yaml
delivery_object_matrix:
  project_fact:
    customer_delivery:
      allowed_groups: [project_summary, fact_summary]
      conditional_groups: [rule_explanation_excerpt]
      blocked_groups: [internal_audit, raw_artifacts]
    external_objection_pack:
      allowed_groups: [project_summary, evidence_excerpt]
      conditional_groups: [rule_explanation_excerpt]
      blocked_groups: [manual_override_internal_reason, natural_person_high_risk]
```

## 附录 J：字段审批 / 脱敏规则字典最小示意

```yaml
field_policy_dictionary:
  project_manager_cert_no:
    classification: restricted_person_field
    approval_required: true
    approval_role: compliance_owner
    masking_rule: partial_mask_last4
    external_audit_required: true
  fact_summary:
    classification: customer_visible_summary
    approval_required: false
    masking_rule: none
    external_audit_required: false
```

## 附录 K：降级 / 恢复审计链最小示意

```yaml
sellable_state_audit_event:
  event_id: EVT-2026-001
  region_code: 320200
  from_state: SELLABLE
  to_state: SUSPENDED
  trigger_type: major_customer_visible_output_issue
  trigger_summary: customer report contained blocked field
  owner: ops_owner_x
  approved_by: business_owner_y
  occurred_at: 2026-04-02T10:00:00+08:00
  resolved_at: null
  evidence_refs:
    - AUDIT-001
  post_action:
    - suspend_region_sales
    - update_region_registry
    - notify_delivery_team
```
