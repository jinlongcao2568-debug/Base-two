# AX9S SCHEMA_REGISTRY

本文件用于登记正式字段、正式对象与变更规则。

## 1. 使用原则

- 任何新增正式字段，必须先登记再实现。
- 任何重命名、删除、语义变化，必须在本文件中留下变更记录。
- 兼容层旧字段不得重新回升为新开发主字段。

## 2. 当前正式对象范围

以下对象已由权威文档定义为正式对象：

- `project_base`
- `bidder_candidate`
- `project_manager`
- `public_chain`
- `invalid_bid`
- `opening_record`
- `contract_performance`
- `credit_penalty`
- `evidence`
- `rule_hit`
- `review_request`
- `report_record`
- `project_fact`

## 3. 当前全局正式枚举

- `result_type`
  - `AUTO_HIT`
  - `CLUE`
  - `OBSERVATION`
- `evidence_grade`
  - `A`
  - `B`
  - `C`
- `sale_gate_status`
  - `OPEN`
  - `REVIEW`
  - `HOLD`
  - `BLOCK`
- `review_status`
  - `PENDING`
  - `CONFIRMED`
  - `REJECTED`
  - `OVERRIDDEN`
- `report_status`
  - `DRAFT`
  - `READY`
  - `ISSUED`
  - `REVOKED`

## 4. 当前登记状态

当前仓库仍处于目录骨架阶段，字段级实现尚未落库或落模型。

因此本文件当前只完成：

- 正式对象登记
- 全局枚举登记
- 变更前置规则登记

后续进入模型、迁移、接口或 facts 实现时，必须补充字段级登记表。

## 5. 变更要求

- 改正式对象：先改权威文档，再改本文件。
- 改字段：先在本文件登记，再改实现。
- 改接口字段：同步更新 `INTERFACE_CATALOG.yaml`。
- 改阶段 6 聚合字段：同步更新 tests 和事实快照。
