---
Document_ID: GOV-GUIDE-01
Title: 框架快速说明
Status: Stable
Phase: Phase_01_Discovery
Track: Governance
Maturity: Stable
Related_Docs:
  - 00_Governance/Index.md
  - 00_Governance/Protocols/PROT-00_Core_Protocols.md
  - 00_Governance/Protocols/PROT-04_Continuation_From_Implementation_And_Log.md
  - 00_Governance/Manifest/MANI-00_Project_State.md
  - 03_Sessions/Index.md
Last_Updated: 2026-04-17
Review_Required: No
---

# 框架快速说明

## 1. 这个框架是干什么的

这个框架用来管理一个长期、非线性推进的科研项目。

核心思想很简单：

- 文档就是项目状态。
- 模块是状态的容器。
- Session 用来记录发散思考。
- Distillation 用来提炼共识。
- 正式模块只保存当前认可的结论。

这意味着两件事：

- 你不应该把所有内容都塞进一个长文档里。
- 你不应该让临时讨论直接变成正式项目知识。

## 2. 整个项目怎么分层

### `00_Governance/`

这是治理层。

它回答这些问题：

- 项目按什么规则运行？
- 当前处于哪个阶段？
- 已经做过哪些重要决策？

主要内容：

- `Protocols/`：运行协议
- `Manifest/`：当前项目状态
- `Decisions/`：重大决策和推翻记录

### `01_Charter/`

这是战略边界层。

它回答这些问题：

- 这个项目为什么存在？
- 当前想解决什么？
- 哪些内容不在范围内？

### `02_Architecture/`

这是稳定逻辑层。

它回答这些问题：

- 当前认可的方法逻辑是什么？
- 数据如何流动？
- 模块边界和风险是什么？

### `03_Sessions/`

这是发散讨论层。

它用来保存：

- 碎片化想法
- 临时讨论记录
- 还没确定的理解
- 阅读源码时的草稿笔记

要点：`Session` 不是正式结论。

### `04_Tasks/`

这是任务管理层。

它用来跟踪：

- 正在做的任务
- 待办任务
- 被阻塞的任务
- 已完成任务

### `05_Experiments/`

这是证据层。

它用来保存：

- 实验假设
- 实验协议
- 运行记录
- 结果
- 分析

### `06_Assets/`

这是资产登记层。

它用来记录：

- 数据集
- 外部依赖
- 生成产物

### `07_References/`

这是参考与学习层。

你导入的开源代码就在这里。

当前基线位置：

- `07_References/Open_Source_Baselines/Array2Binaural/`

也就是说，原来的 `src` 现在被视为“需要学习的参考基线”，而不是项目治理文档的存放位置。

### `08_Reviews/`

这是回顾层。

它用来记录阶段总结和复盘。

## 3. 每次开始工作时先看什么

每次新一轮工作，先看这两个文件：

1. `00_Governance/Protocols/PROT-00_Core_Protocols.md`
2. `00_Governance/Protocols/PROT-04_Continuation_From_Implementation_And_Log.md`
3. `00_Governance/Manifest/MANI-00_Project_State.md`

这样你就能快速知道：

- 当前规则是什么
- 用户说“按照实施文档和开发日志继续”时该怎么续接
- 当前阶段是什么
- 当前重点是什么
- 当前基线代码在哪里

如果用户只给出一句“按照实施文档和开发日志继续”，按 `PROT-04` 执行，不要求用户补写长提示词。

## 4. 最简单的日常使用流程

平时就记住三步循环。

### 第一步：Capture

如果讨论还在发散、还没稳定，就先记到：

- `03_Sessions/Phase_01_Discovery/`
- `03_Sessions/Phase_02_Development/`
- `03_Sessions/Phase_03_Evaluation/`

适合写 `Session` 的情况：

- 你还在理解问题
- 你正在读基线源码
- 你不确定一个想法是否成立
- 你在比较多个方案

这一步不要直接改 `Charter` 或 `Architecture`。

### 第二步：Distill

当几次讨论开始收敛，就在这里写蒸馏文档：

- `03_Sessions/Distillations/`

一个 `Distillation` 至少要说明：

- 它来自哪些 `Session`
- 提炼出了什么共识
- 会影响哪些正式模块
- 是否需要记录重大决策

### 第三步：Commit

只有在蒸馏之后，才去更新正式模块，例如：

- `01_Charter/`
- `02_Architecture/`
- `05_Experiments/`
- `00_Governance/Manifest/`

如果变化很大，还要在这里补一条：

- `00_Governance/Decisions/`

## 5. 一个最简单的例子

假设你正在阅读导入的 `Array2Binaural` 源码。

使用流程应该是：

1. 先读几个脚本，发现一个大致的数据处理流程。
2. 把粗糙理解记到 `03_Sessions/Phase_01_Discovery/SESSION-2026-03-23-01.md`。
3. 继续读更多脚本，确认这个流程基本稳定。
4. 创建 `03_Sessions/Distillations/DIST-0001.md`，总结当前共识。
5. 再更新 `02_Architecture/Logic/ARCH-01_Logical_Flow.md`。
6. 如果这个理解会改变项目方向，再补一条 `00_Governance/Decisions/DEC-0001.md`。

这就是整个框架最核心的工作方式。

## 6. 不知道该放哪时，怎么判断

可以用这个简单映射：

- 临时想法 -> `03_Sessions/`
- 提炼后的共识 -> `03_Sessions/Distillations/`
- 稳定的目标和边界 -> `01_Charter/`
- 稳定的方法和数据理解 -> `02_Architecture/`
- 具体任务 -> `04_Tasks/`
- 实验证据 -> `05_Experiments/`
- 数据集或生成文件登记 -> `06_Assets/`
- 外部代码和论文笔记 -> `07_References/`
- 重大变化记录 -> `00_Governance/Decisions/`

## 7. 实际使用时最重要的几条规则

如果你只记几条，就记这几条：

- 不要把整个项目历史都写进一个文档。
- 不要让 `Session` 直接覆盖正式文档。
- 不要把外部基线代码和项目治理内容混在一起。
- 每个文件夹都应通过 `Index.md` 导航。
- 重要结论都应该能追溯到 `Session`、`Distillation`、实验或决策。

## 8. 现在这个项目里，基线代码该怎么用

导入的开源代码现在在：

- `07_References/Open_Source_Baselines/Array2Binaural/`

你应该把它看成：

- 学习对象
- 总结对象
- 提炼对象
- 未来比较对象

在没有把逻辑蒸馏进 `02_Architecture/` 之前，不要把它直接当成你自己项目的正式架构说明。

## 9. 当前项目下一步该做什么

当前最合理的下一步是：

1. 阅读并总结这份基线源码。
2. 建立第一份 discovery session。
3. 识别关键脚本、关键数据源和关键产物。
4. 把稳定下来的流程蒸馏进 `02_Architecture/`。
5. 把重要数据和产物登记进 `06_Assets/`。
