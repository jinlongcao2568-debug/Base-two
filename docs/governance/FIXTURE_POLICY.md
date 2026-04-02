# AX9S FIXTURE_POLICY

## 1. 目的
Fixtures 是 AX9S 解析、规则和报告稳定性的核心资产。任何涉及公开页面、附件、开标记录、候选人公示、合同链的开发，都必须依赖 fixtures 做回归。

## 2. 来源范围
允许来源：
- 公开公告页
- 公开候选人公示页
- 公开中标结果页
- 公开开标记录页
- 公开合同订立/履约/变更页
- 公开信用处罚页

禁止来源：
- 需要内部账号访问的页面
- 私下获取的截图或导出
- 无法公开回链的材料

## 3. 存放规范
推荐目录：
- `tests/fixtures/raw/`
- `tests/fixtures/normalized/`
- `tests/fixtures/expected/`

命名规范：
`<region>__<source_family>__<project_slug>__<publication_type>__<yyyymmdd>.<ext>`

## 4. 脱敏规则
- 身份证号、手机号、邮箱等个人信息必须脱敏。
- 不得保留内部账号、cookie、token。
- 保留业务判断所需的字段，不做过度脱敏导致测试失真。

## 5. 最低覆盖要求
- 每个解析器至少 2 组 fixture。
- 每个规则专题至少 2 组命中 fixture + 1 组不命中 fixture。
- 每个导出/报告模板至少 1 组快照 fixture。

## 6. 变更要求
以下情况必须更新 fixtures：
- 解析字段变更
- 规则码变更
- 证据映射变更
- 报告模板变更
- 统一事实面字段变更

## 7. 回归要求
- fixtures 更新后必须跑对应阶段测试。
- 高价值专题（项目负责人资格、报价异常、真实竞争者）更新后必须跑集成测试。
