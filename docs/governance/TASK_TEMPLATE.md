# AX9S TASK_TEMPLATE

所有研发 / Codex 任务在开始实现前，至少补齐以下模板。

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

## 使用规则

- 任务包缺失时，不得直接进入实现。
- 任务包中的允许修改目录之外，默认全部禁止修改。
- 涉及接口、字段、例外、迁移时，必须同步引用：
  - `docs/governance/INTERFACE_CATALOG.yaml`
  - `docs/governance/SCHEMA_REGISTRY.md`
  - `docs/governance/exceptions_registry.yaml`

## 当前默认边界

- 第一轮治理底座阶段，不进入业务实现。
- 第一批业务实现建议从 `stage3 -> stage4 -> stage6` 最小闭环开始。
