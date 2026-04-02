# AX9S Governance Skeleton

AX9S 当前处于“治理底座 + 目录骨架 + contracts 校验链”阶段。

## 当前仓库包含

- `docs/baseline/`
  - 建设工程域权威文档
  - 建设工程域研发 / Codex 执行手册
- `docs/governance/`
  - 目录边界、错误策略、fixture 策略、评审与 PR 检查
  - owner 清单、例外台账、接口清单、字段登记册
  - 分支纪律和任务模板
- `docs/contracts/`
  - 4 份机器可读台账
  - 对应 JSON Schema
- `scripts/validate_contracts.py`
  - contracts 校验入口
- `tests/contracts/test_contract_templates.py`
  - contracts smoke test
- `src/`、`tests/`、`db/`
  - 九阶段与治理目录骨架

## 当前正式真源

- 领域定义真源：
  - `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`
- 仓库执行真源：
  - `docs/baseline/AX9S_建设工程域研发_Codex_执行手册_中国落地售卖增强版_V1.4_2026-04-02.md`
- contracts 台账真源：
  - `docs/contracts/sources_registry.yaml`
  - `docs/contracts/region_coverage_registry.yaml`
  - `docs/contracts/customer_delivery_field_whitelist.yaml`
  - `docs/contracts/customer_delivery_field_blacklist.yaml`

根目录不再保留平行的 contracts YAML 副本。

## 本地校验

1. 安装依赖

```powershell
python -m pip install -r requirements-dev.txt
```

2. 校验 contracts

```powershell
python scripts/validate_contracts.py
pytest tests/contracts/test_contract_templates.py
```

3. 本地 git 初始化后的建议流程

```powershell
git checkout -b feat/TASK-xxx-short-topic
```

开工前先填写：

- `docs/governance/TASK_TEMPLATE.md`
- 相关接口或字段登记文件
- 如需越边界，先登记 `docs/governance/exceptions_registry.yaml`

## 当前状态说明

- `src/` 和阶段测试目录已建立，但仍是最小骨架。
- 合同台账、Schema 和 smoke test 已接入。
- 后续进入具体研发前，应先在任务包中明确阶段、授权目录、测试和回滚路径。
