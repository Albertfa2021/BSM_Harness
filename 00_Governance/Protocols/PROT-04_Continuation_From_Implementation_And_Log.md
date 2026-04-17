---
Document_ID: PROT-04
Title: 按实施文档和开发日志继续的续接协议
Status: Stable
Phase: Phase_02_Development
Track: Governance
Maturity: Stable
Related_Docs:
  - Agent.md
  - 00_Governance/Framework_Quick_Guide.md
  - 00_Governance/Protocols/PROT-00_Core_Protocols.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/Index.md
  - 03_Sessions/Phase_02_Development/Index.md
Last_Updated: 2026-04-17
Review_Required: No
---

# 按实施文档和开发日志继续的续接协议

## 1. 触发语句

当用户使用下列表达时，默认进入本协议：

- “按照实施文档和开发日志继续”
- “继续当前任务”
- “按文档继续上一轮工作”

除非用户另行指定，agent 不应要求用户重复提供已在仓库文档中存在的上下文。

## 2. 术语映射

- 实施文档：当前任务对应的 `04_Tasks/Active/` 文档，以及该任务直接引用的正式模块。
- 开发日志：当前任务最近一次相关的 `03_Sessions/Phase_02_Development/` Session。

如果任务不在开发阶段，开发日志可替换为对应阶段的 Session 文档。

## 3. 续接顺序

收到续接指令后，agent 按以下顺序读取：

1. `Agent.md`
2. `00_Governance/Protocols/PROT-00_Core_Protocols.md`
3. 本协议
4. `00_Governance/Manifest/MANI-00_Project_State.md`
5. `00_Governance/Manifest/MANI-02_Active_Focus.md`
6. `04_Tasks/Active/Index.md`
7. 当前任务的实施文档
8. 对应阶段最近一次相关开发日志

如果实施文档已经显式列出“开始前先读”或 `Related_Docs`，继续补读这些直接依赖，不做无界扩散。

## 4. 当前任务判定

agent 按以下优先级判定“当前任务”：

1. 用户本轮明确点名的 `TASK-*`
2. `MANI-02_Active_Focus.md` 指向的当前主线任务
3. `04_Tasks/Active/Index.md` 中最近更新且未完成的任务

如果多个任务同时满足，优先选择与最近开发日志相互引用的那一个。

## 5. 行为要求

进入本协议后，agent 应：

- 先基于实施文档和开发日志复述当前目标、当前 blocker、下一步最小动作。
- 默认在当前任务范围内继续，不自动跳到下一个任务。
- 把正式结论写回正式模块，把过程记录写回对应 Session。
- 若采用 subagents，主 agent 负责控制、分派、审核和整合；具体实现尽量交给 subagents。

agent 不应：

- 要求用户再次手工整理同一批背景
- 把旧 Session 的临时结论直接当成正式结论
- 在未确认当前任务前扩大工作范围

## 6. 最小响应模板

当用户说“按照实施文档和开发日志继续”时，agent 的首轮响应至少应覆盖：

- 当前识别到的任务
- 已读取的实施文档和开发日志
- 当前 blocker 或待验证项
- 本轮准备执行的最小步骤

## 7. 文档维护要求

为了让本协议持续有效：

- 每个活跃任务都应有可识别的实施文档
- 每次开发推进后应补一条对应阶段 Session
- `04_Tasks/Active/Index.md` 和相关 Session `Index.md` 应保持可导航
