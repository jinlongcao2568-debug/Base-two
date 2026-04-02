任务：TASK-002
目标：把 docs/contracts 机器可读台账接入 JSON Schema 校验与 pytest
所属阶段：0（底座治理）
允许修改：
- docs/contracts/
- docs/contracts/schemas/
- scripts/validate_contracts.py
- tests/contracts/
- pyproject.toml
禁止修改：
- src/ax9s/ingestion/
- src/ax9s/rules/
- src/ax9s/facts/
- alembic/versions/
接口变更：否
表结构迁移：否
例外审批：否
影响阶段6事实刷新/回写：否
必须测试：
- python scripts/validate_contracts.py
- pytest tests/contracts/test_contract_templates.py
验收：
- 4 个 YAML 均可通过 JSON Schema 校验
- pytest 可阻断 contracts 台账失配
- 不引入第二套 contracts 命名
回滚：
- 删除新增 schema/validate/test 文件
- 回滚 pyproject.toml 的依赖变更
