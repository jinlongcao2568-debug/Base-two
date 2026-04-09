去任务池接单并执行，完成后回任务池继续接单并重复此流程。
当前任务如下：
阶段1 源族中国切片
Stage1 source-family China slice · stage1-source-family-cn




上 13 条消息
我先从任务池核对这个候选的依赖、授权目录和现有续接点，再落任务包；确认无旧续接点冲突后再开始实现。

当前控制面还挂着上一个 Stage1 任务的 review 态。我先把这条已完成任务正式关账，然后再接 stage1-source-family-cn，避免跨任务脏状态串台。

上一个任务已关账。现在我查这个新候选在路线图里的真实标识和授权范围；如果任务池里没有 stage1-source-family-cn 这个候选，我会先按现有路线图映射到对应的正式候选再接单。

路线图里没有单独的 stage1-source-family-cn 候选，当前正式候选是 stage1-source-family-lanes。
我先刷新任务池状态，再把你指定的“中国切片”落成这个候选下的受限执行任务，避免凭空发明任务编号。

我先让候选池基于刚刚关账后的状态重新计算；如果 stage1-source-family-lanes 变成 ready，就在它下面落中国切片执行任务。

任务池状态还是卡在旧候选传播上，我不等它自动修正了。
我先按路线图的正式父候选 stage1-source-family-lanes，把你指定的“中国切片”落成一个受限执行任务包，然后直接在授权目录内实现。

我已经确认：任务池没有单独的 stage1-source-family-cn 正式候选，所以我会先起草并落库这个中国切片执行任务包，挂在 Stage1 源族 lane 主题下执行。
当前理解如下：

任务理解：为 Stage1 增加“中国源族切片”的编排能力，但不改 Stage2、Stage6，也不回头改上一轮核心契约。
所属阶段：stage1
影响范围：src/stage1_orchestration/、tests/stage1/
文件清单：先落任务包；实现预计只动 src/stage1_orchestration/runtime.py 和 tests/stage1/test_stage1_ingestion_job_runtime.py
测试清单：至少 pytest tests/stage1 -q
风险点：正式候选池还没细化到中国切片，所以这次是“先起草任务包后执行”；实现必须保持为 Stage1 内部编排增强，不能变成 Stage2/Stage6 契约漂移。
任务包已经落地，我现在只看 Stage1 当前真实消费链，找出“中国源族切片”应该落在哪个最小编排点上，再做最小实现。

我已经收敛到最小实现面了：不改 Stage1 既有 ingestion_job 输出契约，只新增“中国源族切片”的 Stage1 内部 lane 构建函数，并补 Stage1 测试锁定边界。

实现已经落下去了。我先只跑授权范围内的 Stage1 测试；如果通过，再决定是否需要补一轮下游冒烟确认这次内部 lane 没外溢。

Stage1 测试已经全绿。我再补一轮下游冒烟，只确认这次中国切片 helper 没碰坏既有最小链路，然后就正式关账。

实现已经完成，测试也收口了。我现在顺序执行 worker-finish 和 close，避免再出现并发关账竞争。

当前任务已正式关账。我现在回任务池看下一个可接项；如果任务池还停在旧候选状态，我会给出明确阻塞点，而不是重复接同一类任务。

已接单并完成 TASK-RM-STAGE1-SOURCE-FAMILY-CN，也已正式关账。

本次改动只在授权范围内完成了 Stage1 的中国源族切片编排，不改 Stage2/Stage6。新增了 Stage1 内部 helper build_source_family_china_lane，用于从 ggzy_national 的中国原始夹具生成中国切片 lane 元数据，并对非 CN-* 区域、非 ggzy_national 源族做确定性拒绝。代码在 [runtime.py](D:/Base One/Base-two/AX9.clones/worker-01/src/stage1_orchestration/runtime.py)，测试在 [test_stage1_ingestion_job_runtime.py](D:/Base One/Base-two/AX9.clones/worker-01/tests/stage1/test_stage1_ingestion_job_runtime.py)。任务包和 runlog 在 [TASK-RM-STAGE1-SOURCE-FAMILY-CN.md](D:/Base One/Base-two/AX9.clones/worker-01/docs/governance/tasks/TASK-RM-STAGE1-SOURCE-FAMILY-CN.md) 和 [TASK-RM-STAGE1-SOURCE-FAMILY-CN-RUNLOG.md](D:/Base One/Base-two/AX9.clones/worker-01/docs/governance/runlogs/TASK-RM-STAGE1-SOURCE-FAMILY-CN-RUNLOG.md)。

测试结果：

pytest tests/stage1 -q -> 9 passed
pytest tests/stage2/test_stage2_raw_ingestion_runtime.py tests/integration/test_stage3_stage4_stage6_minimal_flow.py -q -> 2 passed
我已经回到任务池检查后继任务，但任务池状态仍然是脏的：它还把 stage1-core-contract 视为 ready，同时把 stage1-source-family-lanes 继续卡在 waiting。也就是说，这次“当前任务”已经完成，但“自动回池继续接单”被任务池状态传播问题挡住了，不是业务实现没做完。

未完成项只有这一条：任务池同步/候选状态推进仍未恢复。若继续自动循环，下一步应先修复任务池状态传播，或由你明确指定下一个任务。