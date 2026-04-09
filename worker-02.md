去任务池接单并执行，完成后回任务池继续接单并重复此流程。
当前任务如下：
阶段1 源族全球切片
Stage1 source-family global slice · stage1-source-family-global




上 4 条消息
我先核对这个任务在任务池里的正式定义和任务包，确认任务编号、阶段、允许目录、测试与回滚信息；只有任务包完整后才进入实现。

仓库里还没有这个任务的正式任务包；当前只存在 TASK-RM-STAGE1-CORE-CONTRACT。我继续查路由规则，看 stage1-source-family-global 应该作为哪个父任务下的正式子任务来登记。

我先核对执行命令层：如果这个任务还没正式登记，就需要先按治理流程生成任务包和执行记录；同时要确认它能否在 stage1-core-contract 未完成时合法启动。

我先补足实现侧上下文：读取 stage1 现有代码和测试，判断这个切片要补的实际能力边界。同时我会确认执行任务是否必须挂在父任务下，避免先写了再发现治理流不允许。

Preflight
任务理解是 stage1-source-family-global，应属于 stage1_orchestration 的 source-family 内部分片；预期影响范围是 runtime.py 和 test_stage1_ingestion_job_runtime.py，默认测试是 pytest tests/stage1 -q。按当前路线图，它必须在 stage1-core-contract 完成后才能合法启动，且不能越过 stage6 或扩散到 stage2+。

Status
这个单我现在不能安全接，也不能进入实现。原因有四个：

任务池里目前没有这个任务的正式任务包；仓库内只有 TASK-RM-STAGE1-CORE-CONTRACT.md。
路线图里 stage1-source-family-lanes 明确依赖 stage1-core-contract，来源是 ROADMAP_BACKLOG.yaml。
TASK-RM-STAGE1-CORE-CONTRACT 仍是 doing，并且由其他 AI 占用；你刚才也确认“这个其他AI在做”。
它占用的写入范围就是 src/stage1_orchestration/ 和 tests/stage1/，与当前任务完全重叠。按现有 split/worktree guard，新建并行执行任务会被阻塞。
这轮没有做代码改动，没有跑测试，也没有新增例外。当前阻塞解除条件只有两个：stage1-core-contract 完成并释放相同写入范围，或者你明确改派我接管那个现有任务。


