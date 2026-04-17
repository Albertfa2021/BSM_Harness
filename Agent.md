# Agent Guide

本文件是根目录入口页，给新加入的 agent 或协作者一个最短上手路径。

## 0. 开始前先确认环境

- 本项目后续所有项目侧 Python 开发默认使用 conda 环境 `bsm_harness_py311`
- 每次开始工作先执行：`conda activate bsm_harness_py311`
- 不要把系统 Python 的包状态当成项目环境状态
- 环境详情见：`06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md`

## 1. 先看什么

每次开始工作前，按这个顺序看：

1. `00_Governance/Protocols/PROT-00_Core_Protocols.md`
2. `00_Governance/Protocols/PROT-04_Continuation_From_Implementation_And_Log.md`
3. `00_Governance/Manifest/MANI-00_Project_State.md`
4. `00_Governance/Manifest/MANI-02_Active_Focus.md`
5. `01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md`

如果只是快速熟悉框架，再看：

- `00_Governance/Framework_Quick_Guide.md`

如果用户只说“按照实施文档和开发日志继续”，默认按

- `00_Governance/Protocols/PROT-04_Continuation_From_Implementation_And_Log.md`

执行 continuation workflow，不再要求用户重复粘贴当前任务背景。

仓库 GitHub remote 当前绑定为：

- `https://github.com/Albertfa2021/BSM_Harness.git`

## 2. 这个框架怎么用

框架遵循三层分离：

- 正式结论放正式模块。
- 临时理解放 Session。
- 外部源码和论文放 References。

工作流程固定为：

1. `Capture`：先把未定结论写进 `03_Sessions/`
2. `Distill`：把多次讨论收敛成 `03_Sessions/Distillations/`
3. `Commit`：再更新 `01_Charter/`、`02_Architecture/`、`05_Experiments/` 等正式文档

不要把临时讨论直接写成正式架构。
不要把项目治理内容写进外部参考代码树。

## 3. 根目录 map

### `00_Governance/`

治理层，说明项目怎么运行。

- `Protocols/`：规则、文档标准、工作流协议
- `Manifest/`：当前阶段、当前重点、模块登记
- `Decisions/`：重大决策

### `01_Charter/`

目标和边界层，回答“为什么做、做什么、不做什么”。

- `Goals/`：正式目标、研究问题、阶段计划
- `Boundaries/`：范围边界和非目标
- `Assumptions/`：当前默认前提

### `02_Architecture/`

稳定方法层，回答“怎么做”。

- `Logic/`：方法流程、主逻辑
- `Data/`：数据结构、输入输出契约
- `Interfaces/`：模块边界
- `Risks/`：风险登记

### `03_Sessions/`

临时讨论层，不是正式结论。

- `Phase_01_Discovery/`：阅读、理解、探索
- `Phase_02_Development/`：实现期工作记录
- `Phase_03_Evaluation/`：评测和分析记录
- `Distillations/`：从 Session 提炼出的稳定共识

### `04_Tasks/`

任务跟踪层。

- `Active/`：正在做
- `Backlog/`：待做
- `Blocked/`：阻塞
- `Completed/`：已完成

### `05_Experiments/`

实验与证据层。

- `Registry/`：实验登记、结果跟踪

### `06_Assets/`

资产登记层。

- `Datasets/`：数据集
- `External_Dependencies/`：外部依赖、下载源、版本
- `Generated_Artifacts/`：生成产物

### `07_References/`

参考资料层。

- `Papers/`：论文
- `Notes/`：阅读笔记
- `Open_Source_Baselines/`：外部基线代码

当前参考基线在：

- `07_References/Open_Source_Baselines/Array2Binaural/`

这棵树默认只读学习、包装复用，不作为正式项目文档位置。

### `08_Reviews/`

阶段回顾和复盘。

## 4. 内容放哪

遇到新内容，按这个 map 放置：

- 临时想法、源码阅读草稿 -> `03_Sessions/`
- 多轮讨论后的稳定共识 -> `03_Sessions/Distillations/`
- 正式研究目标、阶段计划 -> `01_Charter/Goals/`
- 方法流程、模块和数据契约 -> `02_Architecture/`
- 任务状态 -> `04_Tasks/`
- 实验设计、运行和结果 -> `05_Experiments/`
- 下载的数据、依赖、生成文件登记 -> `06_Assets/`
- 外部论文、源码、对照资料 -> `07_References/`
- 重大方向调整 -> `00_Governance/Decisions/`

## 5. 当前项目的具体约束

- 当前主线不是做“有训练数据的端到端模型”。
- 一期目标是单实例神经优化求解器。
- 参考前端优先复用 `Array2Binaural` 的 Easycom + KU100 资产链路。
- Python 开发默认在 conda 环境 `bsm_harness_py311` 中进行。
- 该环境以 `07_References/Open_Source_Baselines/Array2Binaural/requirements.txt` 为基础安装依赖。
- 与 Matlab `ILD computer method` 对应的项目侧 Python 复刻当前放在 `05_Experiments/EXP-0001_Auditory_ILD_Python/`。
- 该 ILD 路径的精确实现优先使用项目内的 `numpy + scipy` 版本，`gammatone` 仅作为数值对照，`pyfilterbank` 主要用于理解 `Array2Binaural` 原始脚本。
- 新增的 `07_References/Open_Source_Baselines/ILD computer method/` 是 ILD 评测的重要参考，不应与正式实现混写。
- 不要先做实时系统、主观实验平台或大范围泛化。
- 不要在理解不充分前直接重写参考基线。

## 6. 日常执行检查表

开始前：

- 读 `MANI-00` 和 `MANI-02`
- 确认当前要改的是正式文档、Session，还是实验记录
- 确认外部参考代码是否需要只读包装

完成一个子任务后：

- 补测试或运行校验
- 记录结果和失败点
- 评价代码质量和数值稳定性
- 再决定是否更新正式模块

环境使用时：

- 激活命令：`conda activate bsm_harness_py311`
- 依赖来源：`Array2Binaural/requirements.txt`
- ILD smoke test：`python 05_Experiments/EXP-0001_Auditory_ILD_Python/code/smoke_test.py`
- 如果新增实验依赖，先登记到 `06_Assets/External_Dependencies/`

## 7. 文档规则

- 正式文档使用标准 frontmatter
- 每个目录靠 `Index.md` 导航
- 新增正式文档后同步更新本目录 `Index.md`
- `Related_Docs` 使用 repo 相对路径

## 8. 一句话理解这个仓库

这是一个“研究治理框架 + 外部参考基线”的混合仓库：

- 框架负责沉淀目标、架构、实验和决策
- `Array2Binaural` 负责提供可学习和可复用的参考实现
- `ILD computer method` 负责提供 Matlab 版 ILD 听觉滤波分析参考
