# AX9S DIRECTORY_MAP

本文件定义每个目录的职责边界。任何代码、测试、脚本或文档都必须放在正确位置；放错目录视为结构违规。

## 1. `src/stage1_orchestration/`
职责：任务编排、调度状态、任务模板、重跑控制。
允许：scheduler、job config、task state、dispatch。
禁止：抓取实现、规则判定、页面拼装。

## 2. `src/stage2_ingestion/`
职责：公开源发现、公告抓取、附件抓取、公开链发现、抓取诊断。
允许：crawler、fetcher、html/pdf/image snapshot、source adapters。
禁止：业务规则判定、页面输出、经营字段计算。

## 3. `src/stage3_parsing/`
职责：原始内容转结构化对象。
允许：parser、extractor、normalizer、field mapping。
禁止：串标判定、资格判定、页面拼装、数据库迁移。

## 4. `src/stage4_validation/`
职责：规则引擎、证据映射、请求核验事项、结果边界处理。
允许：validators、rule engine、evidence binding、review-request builders。
禁止：抓取器、UI 逻辑、事实面主聚合。

## 5. `src/stage5_reporting/`
职责：项目核查简报、证据包、异议草稿、人工复核任务单、正式报告对象。
允许：report templates、export builders、review workflow。
禁止：重新解析原始页面、直接读取抓取层状态来拼主判断。

## 6. `src/stage6_facts/`
职责：统一事实面、经营消费字段、阶段 6 唯一主判断聚合。
允许：fact aggregators、fact writers、consumer projections。
禁止：页面层直拼、第二套主判断、抓取逻辑。

## 7. `src/stage7_sales/`
职责：商业承接对象和跟进上下文。
允许：lead/opportunity objects。
禁止：工程域规则判定。

## 8. `src/stage8_contact/`
职责：触达、反馈、客户确认。
允许：contact events、feedback mapping。
禁止：阶段 6 事实面重定义。

## 9. `src/stage9_delivery/`
职责：支付、交付、治理反馈、回写触发。
允许：delivery workflow、governance feedback。
禁止：主规则引擎。

## 10. `src/domain/engineering/`
职责：工程域专题模块。
建议子目录：
- `public_chain/`
- `project_manager/`
- `competitor_analysis/`
- `evidence/`
- `review_requests/`
禁止：与工程域无关的通用业务逻辑。

## 11. `tests/`
- `tests/stage3/`：解析与归一
- `tests/stage4/`：规则、证据、请求核验事项
- `tests/stage5/`：报告、导出、复核
- `tests/stage6/`：事实面与经营消费字段
- `tests/integration/`：从抓取到阶段 6 的完整承接
- `tests/fixtures/`：原始公开样本、预期输出、脱敏材料

## 12. `docs/`
- `docs/baseline/`：单文件权威文档
- `docs/product/`：从 baseline 派生的执行级产品文档
- `docs/contracts/`：正式 contracts 真源，包含 registry、schema、example、field semantics
- `docs/governance/`：治理文件、检查表、政策文档
禁止把临时排障记录、实验说明放入 baseline。

## 13. `db/migrations/`
职责：数据库迁移、回滚说明、seed/demo。
禁止：夹带无关业务逻辑。

## 14. 顶级目录硬规则
- 不得新增未审批的顶级目录。
- 不得把脚本散落在仓库根目录。
- 不得把实验代码、临时数据、调试文件提交进正式目录。
