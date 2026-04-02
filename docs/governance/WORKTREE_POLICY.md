# AX9S WORKTREE_POLICY

本文件定义 AX9S 在本地 git 场景下的最小分支与 worktree 纪律。

## 1. 基本规则

- 一任务一分支。
- 一任务一主目标。
- 默认不在同一分支混做多个阶段目标。
- 未登记例外，不允许越过默认阶段边界。
- 未合并或未归档前，不允许多个大任务共用同一 worktree。

## 2. 分支命名建议

- `feat/TASK-xxx-short-topic`
- `fix/TASK-xxx-short-topic`
- `chore/TASK-xxx-short-topic`

## 3. worktree 命名建议

- `../wt-TASK-xxx`

## 4. 开工前检查

开始任何实现前，至少确认：

- 当前任务编号已经分配。
- 当前分支只服务一个主目标。
- 当前修改目录在任务包授权范围内。
- 如需跨两个以上阶段，已登记例外或有明确授权。

## 5. 当前阶段说明

当前仓库先采用本地 git 纪律，不包含 GitHub Actions 或远程 PR 流程。
远程协作规则后续可在本文件基础上扩展。
