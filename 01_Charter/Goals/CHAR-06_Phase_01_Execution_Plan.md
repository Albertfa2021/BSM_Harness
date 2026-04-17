---
Document_ID: CHAR-06
Title: Phase 01 Execution Plan
Status: Draft
Phase: Phase_02_Development
Track: Charter
Maturity: Consolidating
Related_Docs:
  - 01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md
  - 07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
  - 00_Governance/Manifest/MANI-00_Project_State.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Phase 01 Execution Plan

## Summary

本阶段目标是把研究方向固定为一个可执行的一期实现路线：

- 方法定位为单实例神经优化求解器，而不是依赖传统训练数据的泛化模型。
- 求解对象是 `BSM-MagLS` 初始化系数上的残差修正。
- 前端继续使用 BSM 物理渲染链路，不直接预测双耳波形。
- 联合目标为幅度、幅度导数、ILD 与 ITD，不做 `ILD + MSE` 可训练基线。
- Python 实现统一在 `bsm_harness_py311` conda 环境中开发，并以 `Array2Binaural` 依赖集合为基础。

## Fixed Defaults

- 阵列与 HRTF：一期固定为 `Easycom + KU100`
- 场景范围：先做静态头向，不纳入动态 yaw 轨迹
- 参考基线：复用 `07_References/Open_Source_Baselines/Array2Binaural/`
- 初始化：使用 `BSM-MagLS` 系数
- 求解器：单实例残差 MLP，优化网络参数以求解当前 `HRTF/ATF`
- ITD 代理：参考 `Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction`，采用 GCC-PHAT 互相关序列 MSE
- ILD 参考方法：补充参考 `ILD computer method` 中的 Matlab ERB 滤波评测实现
- 验收方式：先锁定客观指标闭环，不进入主观听评

## Implementation Plan

### 1. Asset And Front-End Preparation

- 下载并登记 `Device_ATFs.h5` 等缺失外部资产
- 创建并维护 `bsm_harness_py311` conda 环境
- 生成并校验 `Easycom_array_32000Hz_o25_22samps_delay.npy`
- 抽离统一前端接口，能够稳定提供 `V`、`h`、`c_init` 和方向网格响应

### 2. Baseline Reproduction

- 复现 `BSM-LS` 与 `BSM-MagLS` 作为对照和初始化
- 复现论文式 `ILD + derivative magnitude` 单实例优化流程，确认参考趋势一致
- 将 Matlab `ILD computer method` 的 ERB-band ILD 分析翻译到 Python，或以等价库包装方式复现
- 保持参考基线代码树只读，新增实现放在项目正式工作区

### 3. Joint Solver Implementation

- 构建残差 MLP：输入 `c_magls`，输出 `Δc`
- 使用 `c_joint = c_magls + alpha * Δc` 作为最终系数
- 优化目标包含：
  - 双耳幅度误差
  - 双耳幅度一阶导数误差
  - 听觉频带 ILD 误差
  - GCC-PHAT 互相关序列 ITD 误差
  - 残差幅度和频率平滑正则

### 4. Evaluation Closure

- 输出 `ILD error`、`ITD proxy error`、`normalized magnitude error`、`NMSE`
- 保存收敛曲线、损失分项和残差范数
- 与 `BSM-MagLS` 做静态方向集对比

## Task Boundaries

本阶段要做：

- 固定一期资产、求解器结构、损失定义和评估闭环
- 在单实例静态条件下完成可运行实现与客观评估
- 建立后续扩展到动态头转的代码骨架

本阶段不做：

- `ILD + MSE` 可训练基线
- 连续头转轨迹与 yaw-rate 约束
- 多阵列并行泛化
- 主观听评链路
- 实时系统或插件化部署

## Test And Review Gate

每完成一个子任务，必须执行四类检查：

1. 运行 smoke test，确认接口、形状和文件依赖成立
2. 运行数值测试，确认损失可反传且无 `nan/inf`
3. 与基线比较关键指标或中间量，确认没有偏离预期
4. 追加一段代码评价，说明正确性风险、数值稳定性和下一步是否可继续扩展

## Deliverables

- 一套正式登记的一期执行计划
- 一个可复现的静态联合优化求解流程
- 一组基线与联合方法的客观对比结果
- 对缺失资产、外部依赖和生成产物的登记记录
