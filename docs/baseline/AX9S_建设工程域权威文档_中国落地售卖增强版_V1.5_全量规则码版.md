# AX9S 建设工程域权威文档（中国落地售卖增强版）V1.5 精修终版

- 文档 ID：AX9S-CE-BASELINE-CN-V1_5
- 版本：V1.5
- 状态：EFFECTIVE
- 文档定位：建设工程域最高约束性权威基线文档
- 适用范围：AX9S 仓库中的建设工程域，中国公开证据落地版本
- 目标读者：产品、架构、研发、测试、联调、验收、AI / Codex 执行代理、经营、交付、复核、治理团队
- 生效日期：2026-04-06
- 替代关系：替代 V1.4 及此前所有中国建设工程域主口径文档
- 关联文档：
  - 《建设工程域研发 / Codex 执行手册》
  - 机器可读契约清单
  - 覆盖登记表
  - 字段策略字典
  - 对象级交付矩阵
  - 例外台账
  - 金标回归样本集说明
- 版本摘要：V1.5 在保留九阶段基线不变的前提下，统一收敛中国公开证据边界下的建设工程域定义，正式纳入招标前条款设计风险、参数定向风险、评分异常、代理行为风险、疑似拆包、中标后异常变更等能力，并将可售治理、外发治理、审计治理、验收治理纳入主文档制度层。

---

## 0. 规范语言与阅读规则

### 0.1 规范语言

本文档中的规范性语气统一按以下级别解释：

- **必须 / 不得 / 只允许**：硬约束。实现、测试、页面、接口、导出、售前、交付、治理均必须遵守。
- **应 / 不应**：强推荐。除非存在受控例外，否则应按本文执行。
- **可 / 允许**：可选能力。仅在不突破本文硬边界时允许采用。

未显式使用上述规范语气的文字，用于解释语义，不单独构成实现豁免依据。

### 0.2 文档使用规则

本文档用于回答以下问题：

1. 建设工程域在 AX9S 中如何成立；
2. 九阶段的输入、处理、输出与消费关系是什么；
3. 哪些对象、字段、结果类型、页面 / API 消费原则是正式口径；
4. 哪些事项可形成正式自动结果，哪些只能形成线索、观察或请求核验事项；
5. 在中国公开证据边界下，系统可承诺什么，不可承诺什么；
6. 如何实现可售治理、外发治理、审计治理、验收治理与动态降级；
7. 当实现、页面、接口、导出、售前材料、执行手册或局部说明发生冲突时，以什么优先级裁决。

本文档不直接规定以下内容：

- 仓库 owner 名单；
- 目录命名细节；
- CI 门禁细项；
- 分支、PR、worktree 流程；
- 脚本、命令、排障记录；
- 例外台账具体字段模板；
- 字段策略字典和对象级交付矩阵的具体机器可读格式；
- 外部源接入脚本实现细节。

上述内容统一由《建设工程域研发 / Codex 执行手册》及配套机器可读资产规定。

---

## 1. 生效规则、优先级与冲突判定总则

### 1.1 生效规则

自本文档生效起：

1. 建设工程域的阶段口径、对象边界、规则边界、覆盖边界、页面 / API 主消费面、客户交付与外发边界统一以本文为准；
2. 任何实现不得绕开阶段 6 形成第二套主判断；
3. 任何局部设计说明、任务备注、页面逻辑、接口兼容拼装、补丁说明、售前材料或临时脚本，均不得反向定义本文中的正式对象与正式边界；
4. 任何新增能力必须回答：输入是什么、处理发生在哪个阶段、输出是什么、由谁消费、是否超出公开边界、是否破坏阶段 6 统一事实中枢、是否影响可售与外发治理。

### 1.2 优先级与冲突判定总则

当多个文档、实现或口径发生冲突时，按以下优先级裁决：

1. **本文档**；
2. 经本文档明确引用的附录与机器可读契约清单；
3. 经批准生效的专题补充规范；
4. 《建设工程域研发 / Codex 执行手册》；
5. 局部设计说明、任务包、联调说明；
6. 临时备注、口头说明、页面热修逻辑、接口兼容拼装。

冲突裁决规则如下：

- 若阶段定义、正式对象、规则边界、结果边界、页面 / API 主消费原则、对外边界发生冲突，必须以本文为准；
- 若目录、CI、执行流程发生冲突，应以执行手册为准，但不得突破本文定义的领域边界；
- 若机器契约与本文对象或枚举冲突，必须先修订本文或契约之一，不得放任双口径并存；
- 未记录、未审批、无有效期的临时实现或口头例外，不得视为正式口径。

### 1.3 受控例外原则

本文档原则上为最高约束性口径，但允许存在受控例外。任何例外必须同时满足：

1. 仅用于止损、兼容过渡、阶段接线或合规处置；
2. 明确例外原因、影响范围、临时有效期与回收计划；
3. 由业务 owner 与技术 owner 共同批准；
4. 登记到机器可读例外台账；
5. 到期后回归本文正式口径；
6. 未记录、未审批、无有效期的例外一律无效。

---

## 2. 产品定位、公开证据边界与对外承诺

### 2.1 正式产品定位

本系统在中国场景下的正式定位固定为：

- 基于**公开证据**的建设工程招投标核查、线索发现、证据整理、人工复核、报告辅助与异议辅助系统；
- 面向经营、投标、法务、风控、咨询、复核、交付团队提供项目事实、证据组织能力、人工复核辅助与外发治理能力；
- 对外提供的是产品判断、证据整理、人工复核与交付支持，不是行政处罚系统、司法裁判系统、评标委员会替代系统或监管机关终局认定系统。

### 2.2 公开证据边界硬约束

建设工程域自动核查只允许使用公开、可检索、可回链证据。以下事项不得作为自动核查前置输入：

- 招投标平台后台日志；
- 上传 IP、下载 IP、登录轨迹；
- 制作机器码、预算软件加密锁、文件私有指纹；
- 原始 XML 清单比对结果；
- 非公开社保、非公开人员档案、非公开合同附件；
- 需内部账号导出的文件；
- 私下获取、无法公开回链或无法审计来源的材料。

上述事项只允许进入 `review_request`，不得直接形成 `AUTO_HIT`。

### 2.3 结果边界硬约束

- `AUTO_HIT`：仅用于公开证据充分、可回链、前置对象齐全、边界说明完整的正式命中；
- `CLUE`：用于强线索，表示公开依据较强但仍需人工复核或补证；
- `OBSERVATION`：用于弱异常、弱缺失、披露不足或链路不完整；
- `review_request`：用于需要内部材料、外部说明或人工专项核验才能闭环的事项；
- `明招暗定 / 暗箱操作`：不得作为单条自动定性规则，只允许作为阶段 6 聚合风险语义。

### 2.4 对外承诺红线

系统不得对外承诺：

1. 自动认定围标串标；
2. 自动判断中标无效；
3. 自动替代评标委员会或监管机关结论；
4. 自动保证异议成功；
5. 全国全地区、全专题、全链路同等成熟覆盖。

系统可对外承诺：

1. 公开证据核查；
2. 异常线索发现；
3. 证据整理与证据回链；
4. 人工复核辅助；
5. 报告辅助与异议辅助。

### 2.5 对外语义硬约束

- `AUTO_HIT` 的正式解释为“产品内正式命中”，不是行政、司法或评标终局结论；
- `CLUE` 的正式解释为“需要进一步人工复核或补证的强线索”，不得直接替代违法定性；
- `OBSERVATION` 的正式解释为“弱异常、弱缺失或信息不足观察”，不得单独作为对外主摘要结论；
- 所有客户交付版报告、异议辅助包、页面导出、对外 API 都必须附带“基于公开信息自动核查与人工复核辅助，不构成法律意见或行政结论”的免责声明。

---

## 3. 覆盖成熟度、地区可售与可售治理

### 3.1 中国 MVP 覆盖范围与成熟度分级

中国首发版本的正式产品核心范围固定为阶段 2 至阶段 6，即：公告抓取与公开链发现、结构化解析、规则核查与证据固化、报告与人工复核、统一项目事实与可售判断。阶段 7 至阶段 9 属于商业承接、触达、交付治理与反馈回写的配套能力，可进入正式建设范围，但不得反向要求中国首发售前承诺默认包含“全链路商业闭环”。

中国落地时，覆盖范围必须采用分级承诺，不得默认宣称全国全地区、全专题、全链路同等成熟。最低分级如下：

- **L1 核心覆盖**：全国公共资源交易平台主链可稳定获取的信息，包括招标 / 资审公告、开标记录、候选人公示、结果公示、澄清等；
- **L2 增强覆盖**：地方住建公开页、全国建筑市场监管公共服务平台、地方信用处罚页等公开增强信息；
- **L3 深度覆盖**：地方特色公告、复杂附件抽取、履约 / 变更 / 停工 / 验收的区域化深链增强能力。

中国 MVP 的默认正式承诺为：

1. 对外首发产品核心覆盖范围以 **L1 + 已验证的部分 L2** 为准；
2. L3 能力属于区域化扩展能力，不得直接作为全国统一承诺；
3. 任何地区、专题、源族若未进入覆盖登记表，不得对外承诺为稳定支持；
4. 必须区分“已实现”“已验证”“已可售”“已可交付”，不得将任一状态偷换为另一状态。

### 3.2 地区可售最低公式

地区或区域包只有同时满足以下条件，才允许在覆盖登记中标记为 `is_sellable=true`：

1. `coverage_level` 至少达到 `L1`，且对客户承诺的能力范围不超出当前登记等级；
2. `validated_topics` 至少覆盖中国 MVP 核心专题：项目负责人资格核查、真实竞争者识别、程序公开充分性核查；
3. `validated_sources` 至少包含一个主链公开源，且所有对客户可见的增强源都已登记并完成最近一次有效验证；
4. `golden_sample_count` 达到规定最低门槛，且不得存在“某核心专题样本数为 0”的情况；
5. `last_verified_at` 位于有效验证窗口内；
6. 不存在未关闭的重大覆盖风险、重大外发合规事故、重大客户投诉或核心公开源长时间失效；
7. 一旦不再满足上述条件，必须触发动态降级、停售或重新验证，不得继续维持可售状态。

### 3.3 地区可售状态机原则

地区可售状态不得只用布尔值表达，还必须符合可迁移、可审计、可恢复的状态机原则。最低状态如下：

- `NOT_READY`
- `VALIDATING`
- `SELLABLE`
- `RESTRICTED`
- `SUSPENDED`
- `RECOVERING`

最低迁移规则如下：

1. 未完成验证的地区不得从 `NOT_READY` 直接跳到 `SELLABLE`；
2. 任一重大合规、外发、投诉或核心源失效事故，至少应触发 `SELLABLE -> RESTRICTED` 或 `SELLABLE -> SUSPENDED`；
3. 从 `SUSPENDED` 恢复到 `SELLABLE` 前，必须先经过 `RECOVERING` 并完成复验；
4. 任一状态迁移都必须记录触发原因、审批人、时间、回滚与恢复说明；
5. 若状态机记录缺失、迁移越级或恢复依据不足，不得继续维持地区可售承诺。

### 3.4 动态降级、停售、恢复 SLA 与审计链原则

覆盖成熟度治理必须具备明确 SLA 与审计链。最低要求如下：

1. 重大客户投诉、重大外发事故、自然人字段越权外发、租户隔离事故被确认后，必须在 **1 个工作日内**完成降级回写；
2. 核心公开源连续失效、连续回归下降、验证窗口过期等非事故类问题，必须在规定窗口内完成限制售卖、暂停售卖或重新验证；
3. 任何恢复到 `SELLABLE` 的动作，都必须在恢复前补齐复验样本、恢复说明、审批记录与恢复时间戳；
4. 地区可售状态的降级、暂停、恢复、续签与关闭都必须形成可审计事件链，不得只保留最终状态；
5. 审计链至少应记录：`event_id`、`region_code`、`from_state`、`to_state`、`trigger_type`、`trigger_summary`、`owner`、`approved_by`、`occurred_at`、`resolved_at`、`evidence_refs`、`post_action`。

### 3.5 覆盖治理注册表原则

系统应维护统一的 `coverage_governance_registry` 或等价注册表，用于管理以下事实：

- 地区覆盖等级；
- 验证通过的专题；
- 验证通过的源族；
- 当前可售状态；
- 最近一次验证时间；
- 最近一次降级 / 恢复事件；
- 当前限制条件；
- 对外承诺边界。

`coverage_governance_registry` 属于系统治理侧正式机器可读资产，用于承接覆盖等级、验证状态、可售状态、限制条件与治理事件，不纳入阶段 3 至阶段 6 的领域真相层对象集合。其字段契约、存储形态、同步方式与审计要求，由本文原则、机器可读契约清单与《建设工程域研发 / Codex 执行手册》共同约束。

最低责任分工如下：

1. 产品管理员负责维护覆盖等级、对外承诺边界、限制条件与对象级交付矩阵的治理侧配置；
2. 复核 / 治理责任人负责批准可售状态迁移、降级、恢复与外发相关治理事件；
3. 技术实现负责将注册表同步为可被阶段 6、经营页、发布门禁与客户交付治理稳定读取的正式同步视图；
4. 页面层、接口层、售前材料、发布流程不得各自维护第二套覆盖状态缓存或自由文本说明替代正式治理状态。

凡被阶段 6、经营页、发布门禁、可售判定或客户交付治理消费的覆盖治理状态，均必须从 `coverage_governance_registry` 或其等价正式同步视图读取，不得在页面层、接口层、发布流程或售前材料中临时拼装。若治理侧状态与领域事实侧状态冲突，必须以已登记、已审批、可审计的治理状态为准，并触发复核、降级或重新验证流程。

任何能力即使已开发完成，只要未进入注册表并满足可售最低公式，均不得对外承诺为可售能力。

---

## 4. 正文—附录映射索引

为提高查阅效率，正文与附录之间的映射统一如下：

- **第 5 章 九阶段定义** ↔ 附录 A（阶段消费索引）
- **第 6 章 正式对象与字段字典** ↔ 附录 B（正式枚举、单位与表示总表）
- **第 7 章 正式规则专题** ↔ 附录 C（规则码总表）
- **第 8 章 页面与接口消费原则** ↔ 附录 D（当前标准接口清单）
- **第 9 章 客户交付与字段控制** ↔ 附录 E、附录 F（字段白名单 / 黑名单 / 字段策略字典）
- **第 10 章 角色、权限、审计留痕** ↔ 附录 G（角色矩阵与审计要求）
- **第 11 章 测试验收与发布准入** ↔ 附录 H（P0-P5 验收矩阵与边界门禁）
- **第 12 章 迁移兼容与变更治理** ↔ 附录 I（地区可售状态机与治理事件示意）、附录 J（字段策略字典最小示意）、附录 K（对象级交付矩阵最小示意）、附录 L（发布前合规 / 可售检查最小示意）

任何实现、测试或 AI / Codex 执行在引用附录时，应同时回看对应正文章节，不得只读附录而跳过正文语义。

---

## 5. 九阶段总体基线与成立标准

### 5.1 总体基线

AX9S 建设工程域必须以九阶段闭环方式成立，而不是页面、脚本、模型、报表或接口的松散堆叠。系统至少满足以下基线：

1. 系统由九个阶段构成；
2. 每个阶段同时具备明确输入、明确处理、明确输出、明确承接目标；
3. 阶段之间必须顺序承接，而不是并列堆叠；
4. 阶段 6 必须是唯一统一事实中枢；
5. 阶段 8 与阶段 9 的反馈必须回写阶段 6；
6. 阶段 9 在必要时必须触发阶段 4 的补证或重核验；
7. 系统闭环成立的最低标准是：上一阶段产物已被下一阶段真实消费。

### 5.2 阶段成立最低标准

任一阶段只有同时满足以下四项时，才能判定为成立：

1. 输入存在；
2. 处理真实发生；
3. 输出真实形成；
4. 输出已进入下一阶段并被真实消费。

只满足前三项、不满足第四项，不得判定为已打通。

### 5.3 页面存在不是成立标准

页面、按钮、卡片、导出入口、接口壳子、脚本壳子都不是成立标准。成立标准只能是：

- 业务处理真实发生；
- 正式对象真实形成；
- 下一阶段真实消费。

### 5.4 阶段职责定义

#### 阶段 1：任务编排

**职责**：定义系统何时、何地、按何条件启动主链任务。该阶段是启动控制面，不是抓取层，也不是判断层。

**输入**：启动指令、时间范围、区域范围、抓取或执行条件、任务模板、重跑策略。

**处理**：保存任务配置、启动任务、停止任务、暴露运行态、记录调度计划与执行上下文。

**输出**：可执行任务、调度状态、运行上下文、可追踪执行流。

**新增要求**：必须支持资格条件抓取任务、参数比对任务、评分披露抓取任务、代理历史扫描任务、同主体时间窗聚合任务、中标后 6-12 个月回查任务。

**承接**：阶段 1 输出必须进入阶段 2；若任务编排不能产生真实抓取动作，则后续阶段全部不成立。

#### 阶段 2：公告抓取

**职责**：将外部公开源转化为系统可消费的原始输入，并建立项目对应的公开链。

**输入**：任务编排输出、公开源入口、项目线索。

**处理**：发现公告、获取详情页、获取原始 HTML / PDF / 图片或等价原始内容、记录抓取诊断、发现同一项目的开标记录、候选人公示、中标结果、合同订立、履约变更、验收或停工公开线索，并合并形成 `public_chain` 初步节点。

**输出**：原始公告内容、附件指针、抓取诊断、`public_chain` 初步节点。

**新增要求**：
1. 对于已纳入覆盖登记表、已声明支持、已验证、已可售或已可交付的专题、地区或源族，阶段 2 必须完成相应抓取字段与原始载体接入；
2. 最低包括：资格条件、评分办法、技术参数、代理机构信息、合同 / 变更 / 验收公开页、同主体历史公告；
3. 对于尚未纳入覆盖登记表或尚未声明支持的能力，阶段 2 可按覆盖计划分批接入，但不得在页面、接口、售前、客户交付或可售登记中被表述为已支持能力；
4. 任何新增专题若缺失阶段 2 对应公开抓取输入，不得仅依赖人工补录、页面临时录入或下游推断视为正式成立。

**承接**：阶段 2 输出必须进入阶段 3。

**工程域约束**：抓取层只负责发现、固化和诊断，不得在该层决定最终业务语义；可以输出 hint，但不得产出最终行业归一、最终候选人排序或最终项目经理归一结果。

#### 阶段 3：结构化解析

**职责**：将原始公告内容转化为正式业务对象，而不是保留为不可用文本。

**输入**：原始公告内容、附件、抓取诊断、透传 hint。

**处理**：提取项目、候选人、项目经理、报价、无效标、开标记录、合同与履约、企业信用与处罚对象；统一源族差异，落成同构对象。

**输出**：`project_base`、`bidder_candidate`、`project_manager`、`invalid_bid`、`opening_record`、`contract_performance`、`credit_penalty`、`public_chain` 正式对象。

**新增要求**：
1. 对于已纳入覆盖登记表、已声明支持、已验证、已可售或已可交付的新增专题，阶段 3 必须形成与之对应的正式结构化画像对象；
2. 最低包括：`qualification_clause_profile`、`parameter_requirement_profile`、`vendor_fit_profile`、`scoring_anomaly_profile`、`tender_agent_profile`、`split_procurement_profile`、`post_award_change_profile`；
3. 任一新增专题若未形成对应正式结构化对象，不得在阶段 4 直接以自由文本、页面临时拼装结果、模型解释文本或规则侧私有中间态替代正式前置对象；
4. 阶段 3 产生的新增画像对象，必须可回链到公开来源、抓取时间、来源 URL 或等价正式载体，不得形成不可审计的第二套画像真相层。

**承接**：阶段 3 输出必须进入阶段 4。

**工程域约束**：阶段 3 是工程域唯一结构化真相层。抓取层与任务层可以透传 hint，但不得形成第二套归一结果。

#### 阶段 4：证据固化与规则核验

**职责**：把结构化对象转化为可证明、可判断、可用于后续报告和统一事实面的业务依据。

**输入**：阶段 3 正式结构化对象、`public_chain`、证据素材、规则配置。

**处理**：固化页面证据与附件证据、形成证据链、执行工程域规则专题、生成 `AUTO_HIT / CLUE / OBSERVATION`、标注证据等级、形成请求核验事项。

**输出**：`rule_hit`、`evidence`、`review_request`、规则摘要与线索摘要。

**新增要求**：新增六类能力全部在本阶段形成正式专题结果；需要内部材料闭环的事项必须同步生成 `review_request`。

**承接**：阶段 4 输出必须同时进入阶段 5 与阶段 6。

**工程域约束**：工程域只能基于公开、可回链证据形成自动命中；任何内部权限事项只能降级为请求核验事项，不得直接写成 `AUTO_HIT`。

#### 阶段 5：报告与人工复核

**职责**：将规则与证据转化为正式交付结果，并提供人工复核与导出机制。

**输入**：规则结果对象、证据对象、请求核验事项对象。

**处理**：生成项目核查简报、证据包、异议辅助草稿、人工复核任务单、正式报告对象；管理导出、补证、退回和重跑。

**输出**：项目核查简报、证据包、异议辅助草稿、请求核验事项清单、人工复核任务单、`report_record`。

**新增要求**：项目核查简报应纳入“招标前条款设计风险”“评标过程异常”“采购组织方式风险”“中标后异常变更”板块；必须支持人工确认“成立线索 / 不成立线索 / 需补证”。

**承接**：阶段 5 输出必须进入阶段 6；若只停留在文件下载而没有正式报告对象回写，则阶段 5 不成立。

#### 阶段 6：统一项目事实汇总与可售判断

**职责**：阶段 6 是系统唯一统一承接中枢。它负责将前五阶段结果整合为统一项目事实，并形成页面、接口、经营和后续商业承接的唯一消费面。

**输入**：基础项目对象、候选人与项目经理对象、规则结果对象、证据对象、正式报告对象、复核状态、覆盖治理状态。

**处理**：汇总项目综合状态；形成 `sale_gate_status`；形成 `real_competitor_count`、`serviceable_competitor_count`、`competitor_quality_grade`；聚合 `price_cluster_score`、`price_gradient_pattern`；形成事实摘要、风险摘要、经营消费字段、可售判断与外发控制依赖字段。

**输出**：`project_fact`、可售判断、经营消费字段、页面与接口消费对象。

**新增要求**：必须聚合 `tender_fairness_risk`、`evaluation_integrity_risk`、`disclosure_completeness_risk`、`award_suspicion_summary`、`post_award_change_risk`；`明招暗定 / 暗箱操作` 只允许体现在聚合解释字段中。

**承接**：阶段 6 输出必须同时进入阶段 7、阶段 8、阶段 9 与页面 / API；任何商业、触达、交付与治理链路都不得绕开阶段 6 单独成立。

**工程域约束**：接口层、页面层、经营层不得绕开 `project_fact` 重新拼装顶层主判断。

#### 阶段 7：商业承接

**职责**：将统一项目事实转化为商业对象，使系统从“值得接”进入“正式进入商业链路”。

**输入**：统一项目事实、可售判断。

**处理**：形成账户上下文、形成线索、形成商机、形成商业上下文。

**输出**：商业对象、跟进上下文、账户、线索与商机对象。

**承接**：阶段 7 输出必须进入阶段 8 与阶段 9。

**约束**：经营页和销售侧只允许消费阶段 6 聚合结果，不得直接消费原始资格条款、参数文本、评分表或未复核中间态重新生成主判断。

#### 阶段 8：销售触达

**职责**：将系统判断和商业对象推进到真实客户互动，并形成客户事实。

**输入**：统一项目事实、商机上下文、联系人上下文、客户上下文。

**处理**：选择触达对象、执行触达动作、记录反馈、确认客户身份或意向。

**输出**：触达记录、客户确认结果、反馈摘要、商机推进结果。

**承接**：阶段 8 输出必须回写阶段 6，必要时进入阶段 9。

**约束**：对外表述必须使用“公开证据风险线索”语义，不得越权表述为已认定违法或已坐实暗箱操作。

#### 阶段 9：订单支付交付与治理反馈

**职责**：将已进入商业链路的对象完成正式执行，并把执行结果重新写回系统。

**输入**：商业订单对象、支付对象、客户确认结果、执行状态。

**处理**：生成订单、确认支付、执行交付、执行治理审核、触发补救，必要时触发阶段 4 的补证或重核验。

**输出**：支付结果、交付结果、治理结果、回写触发信息。

**承接**：阶段 9 输出必须回写阶段 6，并在必要时触发阶段 4 的补证与重核验。

**约束**：对外交付中若使用新增专题，必须走外发审计；客户提供内部材料时，只允许进入复核链，不得直接改写阶段 3 原始对象。

---

## 6. 正式对象与字段字典

### 6.1 命名收敛规则

唯一正式字段名与正式对象名必须以本文为准。兼容层旧口径不得继续作为新开发主字段进入新对象与新接口。

### 6.2 基础项目对象 `project_base`

至少包含：

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
- `tender_method`
- `procurement_category`
- `tender_agent_name`
- `budget_source`

### 6.3 候选人与报价对象 `bidder_candidate`

至少包含：

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

### 6.4 项目经理对象 `project_manager`

至少包含：

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

### 6.5 公开链对象 `public_chain`

至少包含：

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
- `qualification_source_urls`
- `parameter_source_urls`
- `scoring_source_urls`

### 6.6 无效标对象 `invalid_bid`

至少包含：

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

### 6.7 开标记录对象 `opening_record`

至少包含：

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

### 6.8 合同与履约对象 `contract_performance`

至少包含：

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

### 6.9 企业信用与处罚对象 `credit_penalty`

至少包含：

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

### 6.10 证据对象 `evidence`

至少包含：

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
- `evidence_scene`

### 6.11 规则结果对象 `rule_hit`

至少包含：

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

### 6.12 请求核验事项对象 `review_request`

至少包含：

- `request_id`
- `project_id`
- `request_type`
- `reason`
- `public_basis`
- `requested_materials`
- `priority`
- `source_rule_codes`

### 6.13 正式报告对象 `report_record`

至少包含：

- `report_id`
- `project_id`
- `brief_path`
- `evidence_pack_path`
- `objection_draft_path`
- `review_request_list_path`
- `review_task_status`
- `report_status`
- `written_back_at`

### 6.14 统一项目事实对象 `project_fact`

至少包含：

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
- `tender_fairness_risk`
- `evaluation_integrity_risk`
- `disclosure_completeness_risk`
- `award_suspicion_summary`
- `post_award_change_risk`
- `coverage_sellable_state`
- `delivery_risk_state`

### 6.14.1 `project_fact` 硬约束

`project_fact` 是阶段 6 唯一正式统一事实对象，必须同时满足以下约束：

1. `project_fact` 中任一聚合字段，必须可回溯到阶段 3 正式对象、阶段 4 规则结果、阶段 5 正式报告对象、复核状态或治理侧正式资产；
2. 接口层、页面层、经营层、导出层不得绕过 `project_fact` 重新拼装顶层主判断；
3. `fact_version` 必须单调递增或满足可比较版本策略；
4. 任一人工覆盖若影响阶段 6 结果层，必须通过 `manual_override_status` 显式表达，不得静默覆盖自动结论；
5. 页面与客户可见版本必须能够区分“自动聚合结论”与“人工复核覆盖结论”；
6. `coverage_sellable_state` 必须来源于 `coverage_governance_registry` 或其等价正式同步视图，不得由页面或接口临时推断；
7. `delivery_risk_state` 只允许反映交付、外发、脱敏、审批、证据等级或审计阻断状态，不得替代项目核查结论本身；
8. 覆盖治理状态、交付阻断状态、发布门禁状态不得反向污染领域事实字段；治理侧结论不等于项目核查结论，交付阻断结论不等于业务风险结论；
9. 任一聚合字段若无法说明来源对象、计算版本、更新时间与责任归属，不得作为对外正式口径。

### 6.15 聚合字段计算规范

#### 6.15.1 `sale_gate_status`

`sale_gate_status` 为阶段 6 的正式项目售卖 / 推进裁决字段，仅允许以下取值：`OPEN / REVIEW / HOLD / BLOCK`。

- `OPEN`：公开链完整度、核心规则结果、竞争者判断与复核状态均满足最低推进条件，且不存在未决高优先级阻断事项；
- `REVIEW`：存在中高风险线索、证据冲突、披露不足、待人工复核事项或外发治理待确认事项；
- `HOLD`：存在关键证据缺失、关键前置对象缺失、客户反馈与公开证据冲突未闭环、治理状态受限或必须暂缓推进的情况；
- `BLOCK`：存在正式阻断条件，包括但不限于高置信度正式命中、重大合规限制、重大交付阻断、重大治理阻断或业务否决条件。

任一 `sale_gate_status` 结果必须能够说明其主要来源对象、主要阻断原因与最近一次计算时间。

#### 6.15.2 `competitor_quality_grade`

`competitor_quality_grade` 仅允许 `A / B / C / D`。

- `A`：真实竞争者识别充分，公开链完整，关键竞争信息稳定，可作为正式经营判断依据；
- `B`：真实竞争者识别基本成立，但仍存在少量缺失、披露不足或需人工确认点；
- `C`：竞争者识别存在较大不确定性，只适合作为弱经营参考；
- `D`：竞争者识别不稳定、样本不足或关键链路断裂，不得作为正式经营判断依据。

若样本不足、公开链缺失、无效标信息不全或关键对象缺失，最低应降级为 `C` 或 `D`，不得维持高等级。

#### 6.15.3 `price_cluster_score` 与 `price_gradient_pattern`

`price_cluster_score` 取值范围固定为 `0-100`。
`price_gradient_pattern` 必须使用受控模式字典，不得以自由文本作为正式主字段。

`price_gradient_pattern` 最低正式取值建议为：

- `NONE`
- `REGULAR_GRADIENT`
- `TWIN_VALUES`
- `NARROW_BAND`
- `MIXED_PATTERN`
- `INSUFFICIENT_SAMPLE`

任何价格类聚合若样本不足、开标记录缺失、无效标信息缺失或评标办法缺失，必须降级并在相关 `rule_hit` 或事实摘要中说明边界，不得将不稳定模式输出为正式强结论。

#### 6.15.4 `coverage_sellable_state`

`coverage_sellable_state` 用于表达当前项目所属地区、专题或源族的覆盖治理状态。
`coverage_sellable_state` 的正式取值与第 3 章地区可售状态机保持一致，仅允许：`NOT_READY / VALIDATING / SELLABLE / RESTRICTED / SUSPENDED / RECOVERING`。

`coverage_sellable_state` 只允许来源于 `coverage_governance_registry` 或其等价正式同步视图，不得由项目页、经营页、导出逻辑或接口层临时推断。

#### 6.15.5 `delivery_risk_state`

`delivery_risk_state` 用于表达客户交付、外发、脱敏、审批、证据等级或审计链相关的交付阻断风险，不直接替代项目核查结论。

`delivery_risk_state` 仅允许以下取值：`OPEN / REVIEW / HOLD / BLOCK`。

- `OPEN`：交付前置条件齐备，可按既定模板交付；
- `REVIEW`：存在需人工确认的字段、证据等级、脱敏、审批或外发语义风险；
- `HOLD`：存在关键交付前置条件缺失、关键审批未完成、关键证据不足或审计信息不完整；
- `BLOCK`：存在明确禁止外发、禁止导出或禁止进入客户可见版本的阻断条件。

#### 6.15.6 `manual_override_status`

`manual_override_status` 仅用于表达人工覆盖对阶段 6 结果层的正式状态，不得用于反向篡改阶段 3 原始真相层。

`manual_override_status` 仅允许以下取值：

- `NONE`：当前无人工覆盖；
- `PENDING`：已有人工覆盖申请或人工结论待生效；
- `CONFIRMED`：人工覆盖已确认并正式作用于阶段 6 结果层；
- `REJECTED`：人工覆盖已被驳回，不得影响正式结果。

`PENDING` 不得替代首页主结论，只能以“复核中”或等价语义显示；`CONFIRMED` 必须记录覆盖时间、原因摘要与审批 / 复核责任；`REJECTED` 不得继续留在客户可见主摘要中。

#### 6.15.7 缺失值、冲突与人工覆盖处理

1. 聚合字段缺失时，必须区分“未知”“不适用”“空结果”三种状态，不得统一以空值掩盖；
2. 多条证据、多个规则结果或多个公开载体互相冲突时，不得默认选择最新、最大、最有利或页面优先的一条，必须进入复核或降级；
3. 人工覆盖只允许覆盖阶段 5 / 阶段 6 的结果层，不得修改阶段 3 原始结构化对象；
4. 任一聚合字段若没有来源对象、时间戳、计算版本或责任归属，不得作为正式接口输出、页面主判断或客户交付字段；
5. 涉及聚合规则调整的变更，必须同步更新测试、回归样本与版本记录。

### 6.16 新增结构化画像对象

#### 6.16.1 `qualification_clause_profile`

至少包含：

- `profile_id`
- `project_id`
- `qualification_clause_list`
- `restriction_dimension_tags`
- `qualification_restriction_score`
- `source_url`

#### 6.16.2 `parameter_requirement_profile`

至少包含：

- `profile_id`
- `project_id`
- `technical_requirement_vector`
- `brand_tendency_flag`
- `parameter_specificity_score`
- `source_url`

#### 6.16.3 `vendor_fit_profile`

至少包含：

- `profile_id`
- `project_id`
- `candidate_vendor_name`
- `vendor_fit_score`
- `fit_reason_tags`
- `source_url`

#### 6.16.4 `scoring_anomaly_profile`

至少包含：

- `profile_id`
- `project_id`
- `score_deviation_index`
- `technical_score_bias`
- `commercial_score_bias`
- `score_consistency_status`
- `scoring_disclosure_status`
- `source_url`

#### 6.16.5 `tender_agent_profile`

至少包含：

- `profile_id`
- `project_id`
- `agent_name`
- `agent_project_count_12m`
- `agent_risk_pattern_score`
- `agent_history_penalty_flag`

#### 6.16.6 `split_procurement_profile`

至少包含：

- `profile_id`
- `project_group_key`
- `split_similarity_score`
- `split_time_window_days`
- `threshold_proximity_score`
- `related_project_ids`

#### 6.16.7 `post_award_change_profile`

至少包含：

- `profile_id`
- `project_id`
- `post_award_change_type`
- `change_intensity_score`
- `change_publication_status`
- `source_url`

---

## 7. 正式规则专题

### 7.1 已有正式专题

系统正式保留以下基础专题：

1. 项目负责人资格核查；
2. 项目负责人在建冲突线索核查；
3. 报价异常聚集与规律性梯度核查；
4. 真实竞争者识别；
5. 无效标与资格后审结构核查；
6. 企业关联关系核查；
7. 企业与人员信用处罚核查；
8. 程序公开充分性核查。

### 7.2 招标前条款设计风险专题

#### 7.2.1 限制性资格条件识别

- 公开输入：招标公告、资格预审公告、招标文件、资格条件文本、否决条款文本；
- 前置对象：`project_base`、`public_chain`、`qualification_clause_profile`；
- 默认结果类型：`CLUE`，证据较弱时为 `OBSERVATION`；
- 正式语义：识别是否存在异常收窄竞争范围的公开线索；
- 不得表述为“违法设置门槛已成立”。

#### 7.2.2 量身定制参数识别

- 公开输入：技术参数、评分细则、业绩口径、品牌 / 型号 / 性能描述；
- 前置对象：`project_base`、`parameter_requirement_profile`、`vendor_fit_profile`；
- 默认结果类型：`CLUE`，披露不足时为 `OBSERVATION`；
- 正式语义：识别参数或要求是否高度指向少数供应商；
- 不得表述为“定向招标已成立”。

### 7.3 评标过程异常专题

#### 7.3.1 评标打分异常识别

- 公开输入：开标记录、候选人公示、评分表、评分说明、评标办法；
- 前置对象：`bidder_candidate`、`opening_record`、`scoring_anomaly_profile`；
- 默认结果类型：`CLUE`；
- 披露不足时：`OBSERVATION`；
- 正式语义：识别评分结构异常、评分披露不足或排序与公开信息不一致；
- 不得表述为“评标不公已成立”。

### 7.4 主体行为风险专题

#### 7.4.1 招标代理 / 中介行为风险识别

- 公开输入：代理机构名称、公开处罚、历史项目、招标人—代理—中标人共现关系；
- 前置对象：`project_base`、`credit_penalty`、`tender_agent_profile`；
- 默认结果类型：`CLUE`，弱共现时为 `OBSERVATION`；
- 正式语义：识别代理机构的高风险行为模式；
- 不得表述为“代理违规已成立”。

### 7.5 采购组织方式风险专题

#### 7.5.1 规避招标 / 化整为零 / 疑似拆包识别

- 公开输入：同招标人历史公告、金额、发布时间、地点、专业类型、项目名称；
- 前置对象：`project_base`、`public_chain`、`split_procurement_profile`；
- 默认结果类型：`CLUE`，相似度不足或金额不足时为 `OBSERVATION`；
- 正式语义：识别多个公开项目是否呈现疑似拆分发布的模式；
- 不得表述为“规避招标已认定”。

### 7.6 中标后履约风险专题

#### 7.6.1 中标后异常变更 / 履约异常识别

- 公开输入：合同订立、合同变更、停工、验收、项目经理变更公开信息；
- 前置对象：`contract_performance`、`public_chain`、`project_manager`、`post_award_change_profile`；
- 默认结果类型：`CLUE`，披露不足时为 `OBSERVATION`；
- 正式语义：识别中标后异常变更与履约链异常；
- 不得直接作为自动违法定性。

### 7.7 五类线索处理原则

以下事项只允许以线索或观察形式进入系统，不得直接生成单条终局定性结论：

1. 限制性资格条件；
2. 量身定制参数；
3. 评标打分异常；
4. 规避招标 / 化整为零；
5. 明招暗定 / 暗箱操作。

其中：

- 前四类只允许作为 `CLUE / OBSERVATION` 与 `review_request` 的来源；
- `明招暗定 / 暗箱操作` 只允许作为 `project_fact.award_suspicion_summary` 的聚合风险语义，不得作为单条正式规则码。

### 7.8 结果裁决矩阵

1. 满足“公开、可回链、证据充分、前置对象齐全、边界说明完整”时，才允许输出 `AUTO_HIT`；
2. 存在较强公开依据，但仍需补证、人工核验或内部材料确认时，只允许输出 `CLUE`；
3. 公开信息弱、链路缺失、对象不完整或证据等级不足时，只允许输出 `OBSERVATION`；
4. 任一结果若缺失 `boundary_note`、`evidence_refs` 或最低证据等级，不得进入正式结果面；
5. 内部权限材料、私下获取材料、不可回链材料，只能形成 `review_request` 或对 `CLUE / OBSERVATION` 提供辅助解释，不得单独形成 `AUTO_HIT`；
6. 多条证据互相冲突时，必须进入复核，不得直接选择对业务最有利的一条。

---

## 8. 页面与接口消费原则

### 8.1 正式页面

正式页面固定为：

- 任务编排页；
- 项目页；
- 监控页；
- 深链页；
- 证据工作台；
- 异议工作台；
- 经营页；
- 规则后台。

### 8.2 页面消费约束

1. 项目页、监控页、经营页必须优先消费 `project_fact`；
2. 深链页必须消费 `public_chain`；
3. 证据工作台必须消费 `evidence` 与 `rule_hit`；
4. 异议工作台必须消费 `review_request` 与 `report_record`；
5. 页面不得通过抓取层、解析层或前端临时逻辑形成新的主判断。

### 8.3 新能力页面呈现要求

- 项目页应展示：`tender_fairness_risk`、`evaluation_integrity_risk`、`post_award_change_risk`、`award_suspicion_summary`；
- 深链页应展示：资格条件节点、参数与评分节点、合同 / 变更 / 验收节点、同主体时间窗项目聚合视图；
- 证据工作台应支持按“资格条件 / 参数 / 评分 / 代理 / 拆包 / 履约变更”分组查看证据；
- 异议工作台默认不得把线索型专题直接作为外发首页主证据结论。

### 8.4 接口消费原则

- 主判断类接口必须优先消费 `project_fact`；
- 规则解释类接口必须读取 `rule_hit`；
- 链路追溯类接口必须读取 `public_chain`；
- 证据与复核类接口必须分别读取 `evidence`、`review_request`、`report_record`；
- 新增专题接口不得在接口层重算顶层状态。

---

## 9. 客户交付、字段控制与外发治理

### 9.1 客户交付字段最小控制原则

对外页面、客户交付版报告、演示版页面、导出文件与对外 API，必须使用字段白名单机制，不得依赖“默认全量返回后前端隐藏”的方式控制字段。最低原则如下：

1. 客户交付版默认只允许输出项目摘要、统一事实摘要、经复核允许展示的规则解释、经授权的证据节选与最小必要的自然人职业信息；
2. 外发异议辅助包的字段白名单必须比客户交付版更严格；
3. 内部 ID、原始抓取路径、完整证据载体引用、内部审计字段、未复核注释、例外台账字段、owner 信息默认属于黑名单字段；
4. 证书编号、联系方式、证件号、账号标识等强识别字段，除非具备明确公开依据、最小必要性说明与外发审批，否则不得进入客户可见结果；
5. 所有对外 API、客户交付页、导出模板、演示版都应统一从“交付字段白名单层”出，不允许业务接口直接透传内部对象。

### 9.2 字段审批 / 脱敏规则字典原则

客户可见字段除白名单 / 黑名单控制外，还必须纳入字段审批与脱敏规则字典。最低原则如下：

1. 任一客户可见字段都必须声明 `field_classification`；
2. 任一条件性字段都必须声明 `approval_required`、`approval_role`、`masking_rule` 与 `external_audit_required`；
3. 证书编号、联系方式、账号标识、完整内部 ID、原始载体路径与未复核说明，默认属于高限制字段，不得仅凭前端隐藏处理；
4. 同一字段在不同交付对象中的展示级别必须一致可解释；
5. V1.5 新增的画像对象和风险字段，必须先进入字段策略字典，才允许进入页面 / API / 导出。

### 9.3 对象级交付矩阵原则

客户交付控制不得只停留在字段列表，还必须落实到“对象 × 交付形态 × 字段组”的矩阵。最低矩阵原则如下：

1. 至少对 `project_base`、`project_fact`、`rule_hit`、`evidence`、`review_request`、`report_record` 六类对象维护对象级交付矩阵；
2. 至少区分以下交付形态：内部研判版、客户交付版、外发异议辅助包、演示版页面、对外 API；
3. 每个对象在每种交付形态中都必须标记：允许字段、条件性字段、禁止字段、是否需要审批、是否需要脱敏、是否需要审计留痕；
4. 任一对象若未进入矩阵，不得默认“按字段白名单自动外发”；
5. 矩阵冲突时，以更严格的字段黑名单、审批与脱敏规则为准。

### 9.4 新能力对外交付约束

- 限制性资格条件、参数定向、评分异常、疑似拆包、代理行为风险、中标后履约异常默认属于**线索型表达**；
- 对外版本默认不得将其表述为法律定性或终局结论；
- `明招暗定 / 暗箱操作` 不得在首页以单条硬结论出现，只能作为聚合风险解释摘要，并附免责声明。

### 9.5 外发审计与交付门禁原则

发布前和交付前至少应检查：

1. 是否扩大客户可见承诺；
2. 是否扩大自然人信息处理范围；
3. 是否影响外发版报告 / 异议辅助包 / 下载权限 / 审计；
4. 是否改变地区 / 源族覆盖等级；
5. 是否可能诱导销售越界表述；
6. 是否存在未入字段策略字典或对象级交付矩阵的新字段、新对象或新导出模板。

---

## 10. 角色、权限与审计留痕

### 10.1 角色分层

中国落地版本至少应支持以下角色分层：

- **产品管理员**：维护系统配置、源登记、覆盖等级、字段策略字典、对象级交付矩阵与权限；
- **核查分析员**：查看公告链、规则结果、证据对象与项目事实；
- **人工复核员**：处理 `review_request`、复核冲突、执行人工覆盖、批准外发；
- **经营 / 销售用户**：查看 `project_fact`、经营判断、可售状态与摘要，不默认查看全部证据载体；
- **客户只读用户**：仅查看已授权的项目摘要、证据节选与正式交付物。

### 10.2 责任边界

1. 能导出外发包的角色，必须经过明确授权；
2. 能查看完整证据载体与自然人信息的角色，必须具备日志留痕；
3. 人工覆盖只允许由复核角色执行，不得由销售用户直接修改结果；
4. 客户只读用户默认不得访问原始抓取层、结构化真相层与未复核中间态结果；
5. 新增能力越多，越不得仅靠页面显隐实现权限控制，必须将 RBAC 与审计日志一并落地。

### 10.3 审计留痕原则

至少应对以下动作留痕：

- 查看完整证据载体；
- 查看或导出自然人高限制字段；
- 执行人工覆盖；
- 执行客户交付导出；
- 调整字段策略字典；
- 调整对象级交付矩阵；
- 修改地区可售状态；
- 执行降级、恢复、停售、续签。

---

## 11. 测试验收、发布准入与治理反馈

### 11.1 P0-P5 阶段验收机制

#### P0 统一底座

- 正式对象分层冻结；
- 核心字段与枚举冻结；
- 阶段口径固定；
- 不再边开发边发明主字段、主对象、主判断。

#### P1 公开链抓取

- 至少 1 个公开源族可稳定抓取；
- `public_chain` 可形成初步节点；
- 原始 HTML / PDF / 附件指针可追溯；
- 阶段 2 输出已被阶段 3 真实消费。

#### P2 解析与硬资格

- `project_base`、候选人、项目经理、无效标、开标记录、合同、处罚对象可结构化；
- 项目负责人资格专题可稳定输出；
- 阶段 3 输出已被阶段 4 真实消费。

#### P3 报价与竞争者

- 报价异常与真实竞争者识别可稳定输出；
- `project_fact` 可形成最小版 `sale_gate_status` 与竞争者字段；
- 阶段 4 结果已进入阶段 6。

#### P4 证据与异议

- 项目核查简报、证据包、异议辅助草稿、请求核验事项清单、人工复核任务单、正式报告对象全部可生成；
- A / B / C 导出规则生效；
- 正式报告对象回写阶段 6。

#### P5 统一事实与消费

- 页面与 API 只消费正式对象；
- 监控页、经营页、消息策略接入统一事实面；
- 阶段 8 / 9 反馈可回写阶段 6，并在必要时触发阶段 4 重核验。

### 11.2 新增专题专项验收

至少应建立以下最小金标样本集：

1. 限制性资格条件；
2. 量身定制参数；
3. 评分异常；
4. 疑似拆包；
5. 招标代理行为风险；
6. 中标后异常变更。

### 11.3 边界验收

必须同时满足：

1. 内部权限依赖事项全部降级为 `review_request`；
2. `OBSERVATION` 不得在页面或报告中伪装成硬结论；
3. `B` 级线索不默认进入异议导出包；
4. 任一页面均不得绕开阶段 6 拼装主判断；
5. 接口层不得临时拼第二套统一事实面；
6. 导出不得把非公开事项包装成公开自动证据；
7. 新增线索型专题不得越界表述为违法定性。

### 11.4 发布前合规 / 可售检查清单

每次正式发布前至少应检查：

1. 是否扩大客户可见承诺；
2. 是否扩大自然人字段处理范围；
3. 是否改变地区 / 专题 / 源族覆盖等级；
4. 是否引入新的外发字段或新的导出模板；
5. 是否影响对象级交付矩阵；
6. 是否影响字段策略字典；
7. 是否影响地区可售状态机；
8. 是否可能诱导销售越界表述；
9. 是否需要重新验证、重新回归或重新审批。

### 11.5 业务效果验收

除工程正确性外，还必须验证业务正确性。最低要求如下：

1. 每个规则专题必须维护最小金标样本集；
2. 每次规则变更必须输出命中率变化、误报样本数、漏报样本数与漂移说明；
3. 重点地区、重点公开源族必须保留专题回归样本；
4. 重点能力至少具备一组可复现业务回归集；
5. 若业务效果显著下降，即使单测与集成测试通过，也不得视为验收通过。

---

## 12. 迁移兼容与变更治理

### 12.1 迁移原则

1. 既有历史口径仅允许存在于兼容层；
2. 兼容层旧字段不得继续作为新开发主字段；
3. 不得在同一任务中同时完成“重命名 + 语义改变 + 删除旧字段”；
4. 优先采用先加后删、先兼容后切换、最后清理的方式；
5. 涉及阶段 6 聚合字段的变更，必须同步更新聚合逻辑与测试；
6. 涉及正式报告对象的变更，必须同步更新导出与快照测试。

### 12.2 领域变更底线

任何涉及建设工程域的实现变更，都必须遵守：

1. 不得绕开阶段 6 建第二套主判断；
2. 不得新增第二套结构化真相层；
3. 不得把阶段逻辑写进页面层；
4. 不得把内部权限事项伪装成公开自动命中；
5. 不得用仓库局部实现反向定义领域对象与领域边界。

### 12.3 版本变更记录（V1.5）

#### 本版新增

- 统一规范语言说明；
- 优先级与冲突判定总则；
- 覆盖成熟度、可售公式、可售状态机与动态降级治理；
- 客户交付字段白名单 / 黑名单主规则；
- 字段审批 / 脱敏规则字典原则；
- 对象级交付矩阵原则；
- 角色、权限与审计留痕主规则；
- 发布前合规 / 可售检查清单；
- 招标前条款设计风险专题；
- 评标过程异常专题；
- 主体行为风险专题中的代理行为风险；
- 采购组织方式风险专题中的疑似拆包；
- 中标后履约风险专题；
- 七类新增结构化画像对象；
- `project_fact` 的招标公平、评分完整、履约异常与聚合怀疑摘要字段；
- 五类线索的正式处理原则与阶段化落点；
- `project_fact` 聚合字段计算规范、缺失值 / 冲突 / 人工覆盖处理规则；
- `coverage_sellable_state`、`delivery_risk_state`、`manual_override_status` 的正式枚举与消费边界。

#### 本版语义强化

- 进一步收紧公开证据边界；
- 进一步强调阶段 4 是唯一正式出结果阶段；
- 进一步强调阶段 6 是唯一统一主判断中枢；
- 进一步明确线索、观察、请求核验与终局定性之间的边界；
- 进一步明确“已实现”“已验证”“已可售”“已可交付”的状态区分。

#### 本版对实现的影响

- 需要新增阶段 2 抓取字段；
- 需要新增阶段 3 结构化对象；
- 需要新增阶段 4 规则码与 `review_request` 模板；
- 需要新增阶段 6 聚合字段；
- 需要补齐页面、接口、测试、导出、复核链路与覆盖治理注册表。

#### 本版破坏性影响标记

- `breaking_change`：YES
- 主要原因：
  1. `project_fact` 新增治理侧消费字段与更严格的聚合约束；
  2. 覆盖治理状态与交付阻断状态被提升为正式消费字段；
  3. 客户交付、外发 API、导出模板与对象级交付矩阵必须同步收敛到统一门禁层；
  4. 新增专题要求阶段 2、阶段 3、阶段 4、阶段 6 同步补齐，原有仅靠局部页面或接口拼装的实现不再视为合格。
- 影响范围：对象契约、页面消费、外发导出、可售治理、发布门禁、测试回归。

---

# 附录 A：阶段消费索引

- 阶段 1 输出必须进入阶段 2；
- 阶段 2 输出必须进入阶段 3；
- 阶段 3 输出必须进入阶段 4；
- 阶段 4 输出必须同时进入阶段 5 与阶段 6；
- 阶段 5 输出必须进入阶段 6；
- 阶段 6 输出必须同时进入阶段 7、阶段 8、阶段 9 与页面 / API；
- 阶段 8、9 输出必须回写阶段 6，并在必要时回触阶段 4。

# 附录 B：正式枚举、单位与表示总表

- `result_type`：仅允许 `AUTO_HIT / CLUE / OBSERVATION`
- `evidence_grade`：仅允许 `A / B / C`
- `sale_gate_status`：仅允许 `OPEN / REVIEW / HOLD / BLOCK`
- `review_status`：仅允许 `PENDING / CONFIRMED / REJECTED / OVERRIDDEN`
- `report_status`：仅允许 `DRAFT / READY / ISSUED / REVOKED`
- `competitor_quality_grade`：仅允许 `A / B / C / D`
- `severity`：仅允许 `HIGH / MEDIUM / LOW`
- `coverage_sellable_state`：仅允许 `NOT_READY / VALIDATING / SELLABLE / RESTRICTED / SUSPENDED / RECOVERING`
- `delivery_risk_state`：仅允许 `OPEN / REVIEW / HOLD / BLOCK`
- `manual_override_status`：仅允许 `NONE / PENDING / CONFIRMED / REJECTED`
- `price_gradient_pattern`：必须使用受控模式字典，不得返回自由文本；最低正式取值建议包括 `NONE / REGULAR_GRADIENT / TWIN_VALUES / NARROW_BAND / MIXED_PATTERN / INSUFFICIENT_SAMPLE`
- 时间默认表示：带时区 ISO 8601；
- 金额默认单位：人民币元；
- `confidence` 范围固定为 `0-1`；
- 列表 URL 字段默认可为空数组，不建议使用 `null` 表达空集合。

# 附录 C：正式规则码总表

> 说明：本附录给出当前正式规则码、默认结果类型与最低证据等级基线。实现可新增更细子规则，但不得绕开专题边界、不得修改正式结果语义；新增正式规则码必须先更新本附录或与本附录等价的正式机器可读契约。

| 专题 | 标准规则码 | 默认结果类型 | 最低证据等级基线 | 主要回写字段 |
|---|---|---|---|---|
| 项目负责人资格核查 | `PM_CERT_PROFESSION_MISMATCH` | AUTO_HIT | A | `project_manager_public_cert_status`, `rule_hit_summary`, `sale_gate_status` |
| 项目负责人资格核查 | `PM_CERT_LEVEL_MISMATCH` | AUTO_HIT | A | `project_manager_public_cert_status`, `rule_hit_summary`, `sale_gate_status` |
| 项目负责人资格核查 | `PM_CERT_UNIT_MISMATCH` | AUTO_HIT | A | `project_manager_public_cert_status`, `rule_hit_summary`, `sale_gate_status` |
| 项目负责人资格核查 | `PM_CERT_EXPIRED` | AUTO_HIT | A | `project_manager_public_cert_status`, `rule_hit_summary`, `sale_gate_status` |
| 项目负责人资格核查 | `PM_CERT_PUBLIC_INFO_CONFLICT` | CLUE | B | `project_manager_public_cert_status`, `rule_hit_summary`, `sale_gate_status` |
| 项目负责人在建冲突线索核查 | `PM_OVERLAP_PROJECT_CLUE` | CLUE | B | `project_manager_conflict_clue_status`, `clue_summary` |
| 项目负责人在建冲突线索核查 | `PM_POSSIBLE_IN_SERVICE_CLUE` | CLUE | B | `project_manager_conflict_clue_status`, `clue_summary` |
| 项目负责人在建冲突线索核查 | `PM_CHANGE_NOT_PUBLICLY_CLEARED_CLUE` | CLUE | B | `project_manager_conflict_clue_status`, `clue_summary` |
| 项目负责人在建冲突线索核查 | `PM_CONTRACT_PERIOD_OVERLAP_CLUE` | CLUE | B | `project_manager_conflict_clue_status`, `clue_summary` |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_CLUSTERING` | CLUE | B | `price_cluster_score`, `price_gradient_pattern`, `clue_summary`, `competitor_quality_grade` |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_REGULAR_GRADIENT` | CLUE | B | `price_cluster_score`, `price_gradient_pattern`, `clue_summary`, `competitor_quality_grade` |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_TWIN_VALUES` | CLUE | B | `price_cluster_score`, `price_gradient_pattern`, `clue_summary`, `competitor_quality_grade` |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_EXTREME_NARROW_BAND` | CLUE | B | `price_cluster_score`, `price_gradient_pattern`, `clue_summary`, `competitor_quality_grade` |
| 报价异常聚集与规律性梯度核查 | `BID_PRICE_PATTERN_CLUE` | OBSERVATION | C | `price_cluster_score`, `price_gradient_pattern`, `clue_summary`, `competitor_quality_grade` |
| 真实竞争者识别 | `REAL_COMPETITOR_IDENTIFIED` | AUTO_HIT | A | `real_competitor_count`, `serviceable_competitor_count`, `competitor_quality_grade`, `sale_gate_status` |
| 真实竞争者识别 | `SERVICEABLE_COMPETITOR_IDENTIFIED` | AUTO_HIT | A | `real_competitor_count`, `serviceable_competitor_count`, `competitor_quality_grade`, `sale_gate_status` |
| 真实竞争者识别 | `STRONG_COMPETITOR_REMOVED_CLUE` | CLUE | B | `real_competitor_count`, `serviceable_competitor_count`, `competitor_quality_grade`, `sale_gate_status` |
| 真实竞争者识别 | `ABNORMAL_PRICE_CLUSTER_FILTERED` | CLUE | B | `real_competitor_count`, `serviceable_competitor_count`, `competitor_quality_grade`, `sale_gate_status` |
| 无效标与资格后审结构核查 | `INVALID_BID_FILTER_PATTERN_CLUE` | CLUE | B | `invalid_bid_count`, `clue_summary`, `rule_hit_summary` |
| 无效标与资格后审结构核查 | `QUAL_REVIEW_INCONSISTENCY_CLUE` | CLUE | B | `invalid_bid_count`, `clue_summary`, `rule_hit_summary` |
| 无效标与资格后审结构核查 | `MISSING_INVALID_REASON_PUBLICATION` | OBSERVATION | C | `invalid_bid_count`, `clue_summary`, `rule_hit_summary` |
| 企业关联关系核查 | `BIDDER_SAME_CONTROLLER_CLUE` | CLUE | B | `clue_summary`, `competitor_quality_grade` |
| 企业关联关系核查 | `BIDDER_SAME_LEGAL_REP_CLUE` | CLUE | B | `clue_summary`, `competitor_quality_grade` |
| 企业关联关系核查 | `BIDDER_ADDRESS_OVERLAP_CLUE` | OBSERVATION | C | `clue_summary`, `competitor_quality_grade` |
| 企业关联关系核查 | `BIDDER_PHONE_OVERLAP_CLUE` | OBSERVATION | C | `clue_summary`, `competitor_quality_grade` |
| 企业关联关系核查 | `BIDDER_MANAGEMENT_RELATION_CLUE` | CLUE | B | `clue_summary`, `competitor_quality_grade` |
| 企业与人员信用处罚核查 | `BIDDER_PENALTY_ACTIVE` | AUTO_HIT | A | `rule_hit_summary`, `sale_gate_status`, `competitor_quality_grade` |
| 企业与人员信用处罚核查 | `PM_PENALTY_ACTIVE` | AUTO_HIT | A | `rule_hit_summary`, `sale_gate_status`, `competitor_quality_grade` |
| 企业与人员信用处罚核查 | `BIDDER_BLACKLIST_ACTIVE` | AUTO_HIT | A | `rule_hit_summary`, `sale_gate_status`, `competitor_quality_grade` |
| 企业与人员信用处罚核查 | `PRIOR_COLLUSION_PENALTY_CLUE` | CLUE | B | `rule_hit_summary`, `sale_gate_status`, `competitor_quality_grade` |
| 程序公开充分性核查 | `MISSING_OPENING_RECORD_PUBLICATION` | OBSERVATION | C | `public_chain_status`, `clue_summary`, `rule_hit_summary` |
| 程序公开充分性核查 | `MISSING_FULL_CANDIDATE_PUBLICATION` | OBSERVATION | C | `public_chain_status`, `clue_summary`, `rule_hit_summary` |
| 程序公开充分性核查 | `MISSING_INVALID_BID_PUBLICATION` | OBSERVATION | C | `public_chain_status`, `clue_summary`, `rule_hit_summary` |
| 程序公开充分性核查 | `LATE_CRITICAL_CLARIFICATION_CLUE` | CLUE | B | `public_chain_status`, `clue_summary`, `rule_hit_summary` |
| 程序公开充分性核查 | `PUBLIC_CHAIN_INCOMPLETE` | CLUE | B | `public_chain_status`, `clue_summary`, `rule_hit_summary` |
| 招标前条款设计风险专题 | `DISCRIMINATORY_QUALIFICATION_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 招标前条款设计风险专题 | `REGIONAL_RESTRICTION_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 招标前条款设计风险专题 | `OVER_NARROW_EXPERIENCE_REQUIREMENT_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 招标前条款设计风险专题 | `NON_ESSENTIAL_HARD_GATE_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 招标前条款设计风险专题 | `TAILORED_PARAMETER_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 招标前条款设计风险专题 | `BRAND_DIRECTIONALITY_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 招标前条款设计风险专题 | `SINGLE_VENDOR_FIT_PATTERN_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 招标前条款设计风险专题 | `COMBINED_PARAMETER_EXCLUSION_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary`, `award_suspicion_summary` |
| 评标过程异常专题 | `EXPERT_SCORE_ANOMALY_CLUE` | CLUE | B | `evaluation_integrity_risk`, `clue_summary`, `award_suspicion_summary` |
| 评标过程异常专题 | `ABNORMAL_NON_PRICE_SCORE_CLUE` | CLUE | B | `evaluation_integrity_risk`, `clue_summary`, `award_suspicion_summary` |
| 评标过程异常专题 | `SCORING_METHOD_INCONSISTENCY_CLUE` | CLUE | B | `evaluation_integrity_risk`, `clue_summary`, `award_suspicion_summary` |
| 评标过程异常专题 | `MISSING_SCORING_DISCLOSURE_OBSERVATION` | OBSERVATION | C | `evaluation_integrity_risk`, `clue_summary`, `award_suspicion_summary` |
| 主体行为风险专题 | `AGENT_HIGH_RISK_CONCENTRATION_CLUE` | CLUE | B | `award_suspicion_summary`, `clue_summary` |
| 主体行为风险专题 | `AGENT_HISTORY_PENALTY_CLUE` | CLUE | B | `award_suspicion_summary`, `clue_summary` |
| 主体行为风险专题 | `AGENT_OWNER_VENDOR_REPEAT_PATTERN_CLUE` | CLUE | B | `award_suspicion_summary`, `clue_summary` |
| 主体行为风险专题 | `AGENT_ABNORMAL_REGION_CLUSTER_CLUE` | CLUE | B | `award_suspicion_summary`, `clue_summary` |
| 采购组织方式风险专题 | `TENDER_SPLIT_AVOIDANCE_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary` |
| 采购组织方式风险专题 | `ABNORMAL_PACKAGE_FRAGMENTATION_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary` |
| 采购组织方式风险专题 | `THRESHOLD_PROXIMITY_SPLIT_CLUE` | CLUE | B | `tender_fairness_risk`, `clue_summary` |
| 中标后履约风险专题 | `POST_AWARD_SCOPE_CHANGE_CLUE` | CLUE | B | `post_award_change_risk`, `disclosure_completeness_risk`, `clue_summary` |
| 中标后履约风险专题 | `PM_POST_AWARD_REPLACEMENT_CLUE` | CLUE | B | `post_award_change_risk`, `disclosure_completeness_risk`, `clue_summary` |
| 中标后履约风险专题 | `ABNORMAL_CONTRACT_PERIOD_CHANGE_CLUE` | CLUE | B | `post_award_change_risk`, `disclosure_completeness_risk`, `clue_summary` |
| 中标后履约风险专题 | `PERFORMANCE_PUBLIC_CHAIN_BREAK_CLUE` | CLUE | B | `post_award_change_risk`, `disclosure_completeness_risk`, `clue_summary` |

# 附录 D：当前标准接口清单

- `GET /projects/{id}/public-check`
- `GET /projects/{id}/public-chain`
- `GET /projects/{id}/competitors`
- `GET /projects/{id}/rules`
- `GET /projects/{id}/evidence`
- `GET /projects/{id}/review-requests`
- `POST /reports/{id}/build-objection-pack`
- `GET /projects/{id}/tender-design-risk`
- `GET /projects/{id}/post-award-changes`
- `GET /projects/{id}/bundle-risk`

# 附录 E：客户交付字段最小总表

## 默认白名单

- 项目摘要字段；
- 统一事实摘要字段；
- 规则解释节选字段；
- 版本与交付元字段。

## 条件性白名单

- 自然人职业信息；
- 企业处罚与信用信息；
- 经批准的证据节选图片、PDF 页码节选；
- 经复核批准的规则解释摘要。

## 默认黑名单

- 内部 ID 与内部 owner；
- 原始抓取路径与内部存储路径；
- 内部审计字段与未复核评注；
- 完整证书号、联系方式、证件号等高识别度字段。

# 附录 F：字段审批 / 脱敏规则字典原则

- 任一客户可见字段都必须声明分类；
- 条件性字段必须声明审批要求、审批角色、脱敏规则与外发审计要求；
- 证书编号、联系方式、账号标识、完整内部 ID、原始载体路径等默认属于高限制字段；
- 不同交付形态中的展示级别必须一致可解释。

# 附录 G：角色矩阵与审计要求

- 产品管理员：配置、权限、审计与覆盖等级维护；
- 核查分析员：查看项目、规则、证据与事实摘要；
- 人工复核员：处理复核、覆盖与外发审核；
- 经营 / 销售用户：查看经营摘要、覆盖等级、可售状态；
- 客户只读用户：查看授权后的客户交付结果与节选证据。

审计重点动作：查看完整证据、查看高限制字段、外发导出、人工覆盖、字段策略字典变更、对象级交付矩阵变更、地区可售状态变更。

# 附录 H：P0-P5 验收矩阵与边界门禁

- P0：底座冻结；
- P1：公开链抓取；
- P2：解析与硬资格；
- P3：报价与竞争者；
- P4：证据与异议；
- P5：统一事实与消费；
- 边界门禁：公开边界、线索边界、导出边界、页面 / API 主消费边界。

# 附录 I：地区可售状态机与治理事件示意

状态：

- `NOT_READY`
- `VALIDATING`
- `SELLABLE`
- `RESTRICTED`
- `SUSPENDED`
- `RECOVERING`

治理事件最小字段：

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

最小示意：

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

# 附录 J：字段策略字典最小示意

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
  award_suspicion_summary:
    classification: conditional_customer_visible_risk_summary
    approval_required: true
    approval_role: review_owner
    masking_rule: none
    external_audit_required: true
```

# 附录 K：对象级交付矩阵最小示意

```yaml
delivery_object_matrix:
  project_fact:
    customer_delivery:
      allowed_groups: [project_summary, fact_summary]
      conditional_groups: [rule_explanation_excerpt, risk_summary]
      blocked_groups: [internal_audit, raw_artifacts]
      approval_required: true
      audit_required: true
    external_objection_pack:
      allowed_groups: [project_summary, evidence_excerpt]
      conditional_groups: [rule_explanation_excerpt]
      blocked_groups: [manual_override_internal_reason, natural_person_high_risk]
      approval_required: true
      audit_required: true
  evidence:
    customer_delivery:
      allowed_groups: [approved_evidence_excerpt]
      conditional_groups: [public_pdf_page_excerpt]
      blocked_groups: [raw_storage_path, full_artifact_ref]
      approval_required: true
      audit_required: true
```

# 附录 L：发布前合规 / 可售检查最小示意

```yaml
pre_release_compliance_check:
  expands_customer_visible_commitment: false
  expands_natural_person_processing_scope: false
  changes_region_or_source_coverage_level: false
  introduces_new_export_template: true
  affects_delivery_object_matrix: true
  affects_field_policy_dictionary: true
  affects_sellable_state_machine: false
  may_induce_sales_overclaim: false
  revalidation_required: true
```

