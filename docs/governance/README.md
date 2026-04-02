# AX9S Governance Index

本目录存放 AX9S 仓库治理文件。

## 当前治理文件

- `DIRECTORY_MAP.md`
  - 目录职责边界
- `ERROR_POLICY.md`
  - 错误分级、降级与阻断规则
- `FIXTURE_POLICY.md`
  - fixtures 来源、命名、脱敏与回归要求
- `PR_CHECKLIST.md`
  - PR 合并前检查表
- `REVIEW_POLICY.md`
  - 人工 review 触发条件
- `owners.yaml`
  - 关键路径 owner 清单
- `exceptions_registry.yaml`
  - 受控例外总台账
- `INTERFACE_CATALOG.yaml`
  - 机器可读接口清单 seed
- `SCHEMA_REGISTRY.md`
  - 正式字段登记册 seed
- `WORKTREE_POLICY.md`
  - 本地 git / worktree / 分支纪律
- `TASK_TEMPLATE.md`
  - 任务准入模板

## 与 baseline 的关系

- `docs/baseline/` 负责领域定义与执行准则。
- `docs/governance/` 负责仓库层治理、登记、检查和审阅要求。
- 若治理文件与权威文档冲突，以权威文档为准。

## 当前状态

- owner、例外、接口和字段登记文件已建立最小 seed。
- 本地分支纪律和任务模板已建立。
- 具体实现落地后，相关目录 owner、接口项和正式字段必须同步补齐。
