# 麦克风阵列双耳渲染学习指引

## 1. 文档目的

这份文档用于给其他项目快速介绍当前仓库里最有复用价值的两部分：

1. `BSM_reproduction.m` 中的 BSM 滤波器计算方法。
2. `plot_ITD_fig8.m` 与 `plot_ILD_fig9.m` 中的双耳线索仿真评测方法。

这里不追求把论文全文重述，而是强调“当前项目到底是怎么实现的、后续项目要复用时应该抓什么”。

---

## 1.1 当前项目根目录与绝对路径

当前项目的根目录绝对路径是：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching`

后文中提到的所有源码、数据和依赖，默认都位于这个根目录下面。

为了避免在另一个项目中迁移时找不到文件，建议直接记录下面这些绝对路径。

### 核心源码绝对路径

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\BSM_reproduction.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SteeringVector.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\get_sampled_hrir.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ITD_fig8.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ILD_fig9.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\Test_BSM.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\compare_directional_BSM_optimization.m`

### 结果文件绝对路径

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\BSM_results.mat`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\ITD_fig8_results.mat`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\ILD_fig9_results.mat`

### KU100 数据与相关资源绝对路径

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\KU100 dataset`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\KU100 dataset\HRIR_L2702.mat`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\KU100 dataset\Beyerdynamic-DT990PRO.mat`

### 球谐/阵列处理工具库绝对路径

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SphArrayProc`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SphArrayProc\matlab\math`

当前项目实际调用到的函数主要来自这个目录，例如：

- `BnMat.m`
- `sh2.m`
- `equiangle_sampling.m`

### 听觉滤波器组工具库绝对路径

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\AuditoryToolbox`

`plot_ILD_fig9.m` 依赖这个目录中的 ERB 相关函数，例如：

- `ERBSpace`
- `MakeERBFilters`
- `ERBFilterBank`

---

## 2. 项目里最重要的脚本

- `BSM_reproduction.m`
  负责计算左右耳 BSM 频域滤波器 `c_BSM_left` 和 `c_BSM_right`。
- `SteeringVector.m`
  负责计算阵列对某一入射方向、某一频率下的 steering vector。
- `get_sampled_hrir.m`
  负责从 KU100 HRTF/HRIR 数据中抽取训练方向上的 HRIR。
- `plot_ITD_fig8.m`
  负责用参考 HRIR 和 BSM 重建结果计算 ITD。
- `plot_ILD_fig9.m`
  负责用 ERB 滤波器组计算 ILD 和 ILD 误差。
- `Test_BSM.m`
  是运行 BSM 计算并保存 `BSM_results.mat` 的最直接入口。

对应的绝对路径如下：

- `BSM_reproduction.m`
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\BSM_reproduction.m`
- `SteeringVector.m`
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SteeringVector.m`
- `get_sampled_hrir.m`
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\get_sampled_hrir.m`
- `plot_ITD_fig8.m`
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ITD_fig8.m`
- `plot_ILD_fig9.m`
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ILD_fig9.m`
- `Test_BSM.m`
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\Test_BSM.m`

---

## 3. 整体方法框架

当前项目的核心思想可以概括为：

1. 先选定一组训练方向 `Q`。
2. 对每个训练方向，从 KU100 数据集中取出左右耳 HRIR，并转到频域得到 HRTF。
3. 对每个频点，建立麦克风阵列对这些训练方向的 steering matrix `V`。
4. 对左右耳分别求解一个正则化最小二乘问题，得到每个频点上的 BSM 滤波器。
5. 在评测时，对任意测试方向重新计算 steering vector，把阵列响应代入已求得的滤波器，得到双耳重建结果。
6. 再对重建结果与参考 HRIR 比较，计算 ITD / ILD 误差。

也就是说：

- 滤波器设计阶段：用很多训练方向拟合“阵列响应 -> 左右耳目标 HRTF”的映射。
- 仿真评测阶段：检查这个映射在测试方向上能否保留关键双耳线索。

---

## 4. 滤波器计算部分

### 4.1 输入是什么

`BSM_reproduction.m` 的主要输入有：

- `hrir_filename`
  训练所用的 KU100 HRIR 数据文件。
- `array_config`
  阵列几何配置，包括麦克风的球坐标位置和阵列半径。
- `Q`
  假设声源方向数，即训练方向数。
- `filter_length`
  滤波器长度，同时也是 FFT 长度。
- `SNR_dB`
  正则化强度的来源。
- `N_order`
  steering vector 计算时采用的球谐阶数。

当前工程常用配置是：

- `Q = 240`
- `filter_length = 512`
- `SNR_dB = 20`
- `N_order = 30`
- 阵列为半圆 6 麦、半径 `0.10 m`

当前这些参数最直接的查看入口在：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\Test_BSM.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ITD_fig8.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ILD_fig9.m`

### 4.2 训练方向怎么来

训练方向由 `get_sampled_hrir.m` 生成。这里项目主要使用：

- `sampling_method = 'spiral'`

也就是球面 spiral points 采样。它的作用是让训练方向在球面上尽量均匀铺开，避免方向覆盖不均。

这一步的输出包括：

- `azimuth` / `elevation`
- `ir_data`
- `sampling_weights`

但在当前 BSM 主流程里，真正被核心使用的是：

- 每个训练方向的 HRIR
- 每个训练方向的球坐标

源码位置：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\get_sampled_hrir.m`

该函数内部实际会访问：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\KU100 dataset\HRIR_L2702.mat`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SphArrayProc\matlab\math`

### 4.3 HRIR 如何变成目标量

在 `BSM_reproduction.m` 中，流程是：

1. 读取训练方向上的双耳 HRIR。
2. 将 HRIR 截断或补零到 `filter_length`。
3. 对左右耳分别做 FFT。
4. 保留单边频谱，得到：
   - `HRTF_left(f, q)`
   - `HRTF_right(f, q)`

因此，对每个频率点 `f`，左右耳目标向量分别是：

- `h_left = HRTF_left(f, :)'`
- `h_right = HRTF_right(f, :)'`

它们描述的是：在该频点上，所有训练方向对应的目标双耳响应。

源码位置：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\BSM_reproduction.m`

### 4.4 阵列模型如何建立

对每个频点，项目会为所有训练方向建立 steering matrix：

- `V ∈ C^(M x Q)`

其中：

- `M` 是麦克风数。
- `Q` 是训练方向数。
- `V(:, q)` 是第 `q` 个方向下的阵列 steering vector。

这个 steering vector 由 `SteeringVector.m` 计算，方法依赖：

- 球谐展开
- 刚性球阵列径向项 `B_rigid`
- 源方向与麦克风方向的球谐函数

本质上，它给出的是：

- 在某个频率、某个入射方向下，阵列各麦克风的复数响应。

源码与依赖位置：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SteeringVector.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SphArrayProc\matlab\math\BnMat.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SphArrayProc\matlab\math\sh2.m`

### 4.5 滤波器的求解公式

当前实现对应论文中的 BSM 正则化解：

`c_BSM = (V V^H + λ I)^(-1) V conj(h)`

左右耳分别求一次：

- `c_BSM_left(:, f) = (V V^H + λI)^(-1) V conj(h_left)`
- `c_BSM_right(:, f) = (V V^H + λI)^(-1) V conj(h_right)`

其中：

- `λ = sigma2_n / sigma2_s`
- 当前代码中 `sigma2_s = 1`
- `sigma2_n = 10^(-SNR_dB/10)`

因此 `SNR_dB` 越低，正则化越强。

### 4.6 这一步到底在优化什么

可以把它理解成：

- 让阵列经过滤波后的输出，尽量逼近左右耳目标 HRTF。
- 由于训练方向很多、麦克风数有限，所以本质是一个带正则化的多方向拟合问题。

更直白地说：

- 每个频点都在学一组“从 `M` 个麦克风到左耳/右耳”的复权重。
- 这些权重不是只服务于某一个方向，而是同时折中满足 `Q` 个训练方向。

这也是后面 directional optimization 脚本会进一步研究的原因：如果所有方向一起优化，重点方向可能会被平均掉。

---

## 5. 如何用这些滤波器做重建

训练完成后，如果要评估某个测试方向 `(theta_test, phi_test)`，项目的做法是：

1. 对每个频点重新计算该测试方向的 steering vector `V_test(:, f)`。
2. 用左右耳滤波器分别投影：
   - `P_left(f) = c_BSM_left(:, f)^H V_test(:, f)`
   - `P_right(f) = c_BSM_right(:, f)^H V_test(:, f)`
3. 补成共轭对称全频谱。
4. 通过 IFFT 回到时域，得到：
   - `p_BSM_left`
   - `p_BSM_right`

在 `plot_ITD_fig8.m` 和 `plot_ILD_fig9.m` 中，默认测试信号取的是单位脉冲，因此频域里相当于：

- `S(f) = 1`

这样得到的时域结果可以直接理解成“该方向下 BSM 重建得到的双耳脉冲响应”。

这一步很关键，因为：

- 训练阶段比的是方向集合上的拟合能力。
- 评测阶段真正比较的是某个测试方向上的双耳线索是否正确。

可直接参考的源码位置：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ITD_fig8.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ILD_fig9.m`

---

## 6. ITD 仿真评测方法

对应脚本：`plot_ITD_fig8.m`

绝对路径：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ITD_fig8.m`

### 6.1 测试设置

当前脚本用的是：

- 水平面测试
- `theta = 90°`
- `phi = 0:359°`

也就是对水平面一整圈逐度扫描，比较每个方位角的 ITD 表现。

### 6.2 参考信号是什么

对每个测试方向：

1. 从 KU100 HRIR 数据中取最近邻 HRIR。
2. 做截断/补零到 `filter_length`。
3. 左右耳参考信号就是该方向的参考 HRIR。

也就是说，ITD 的 reference 不是理论头模，而是 KU100 数据集中的实际双耳脉冲响应。

### 6.3 为什么要先低通

脚本中先设计了一个 1.5 kHz 的 FIR 低通：

- `fc_lpf = 1500 Hz`

然后对参考 HRIR 和 BSM 重建结果都做 `filtfilt`。

这样做的原因是：

- ITD 主要由低频相位/时延线索承载。
- 高频部分更容易受头部遮挡和谱细节影响，直接拿来做互相关会让 ITD 估计更不稳定。

所以这个脚本的 ITD 不是“全频 ITD”，而是“低频主导的 ITD 估计”。

相关依赖的实际位置：

- KU100 HRIR 数据：
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\KU100 dataset\HRIR_L2702.mat`
- 耳机补偿文件：
  `D:\Files Library\Phd Files\Research Folder\binaural signal matching\KU100 dataset\Beyerdynamic-DT990PRO.mat`

### 6.4 ITD 是怎么计算的

脚本采用 inter-aural cross-correlation 的最大值位置：

1. 对左右耳低通信号做互相关 `xcorr`。
2. 限制搜索范围在 `±2 ms`。
3. 取最大相关系数对应的 lag。

得到的是：

- `ITD_reference`
- `ITD_BSM`

最后再从 samples 转成 microseconds。

### 6.5 ITD 误差是什么

误差定义很直接：

- `ITD_error_us = abs(ITD_BSM_us - ITD_reference_us)`

因此它回答的问题是：

- 对每个方位角，BSM 重建出的双耳时间差偏离参考值多少微秒。

### 6.6 这一评测最有价值的地方

ITD 脚本的价值不只是“出一张图”，而是提供了一个稳定的低频时延一致性检查：

- 能快速判断 BSM 是否保留了左右耳到达时差。
- 对水平面定位表现尤其敏感。
- 对阵列半径、训练方向数、正则化参数变化也比较敏感。

如果后续项目要比较不同阵列结构，这个脚本非常适合作为第一批基准评测。

---

## 7. ILD 仿真评测方法

对应脚本：`plot_ILD_fig9.m`

绝对路径：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ILD_fig9.m`

### 7.1 测试设置

ILD 脚本和 ITD 脚本保持一致，也是在：

- `theta = 90°`
- `phi = 0:359°`

的水平面上评测。

这样做的好处是：

- ITD 和 ILD 的结果可以直接对比同一批方位角。
- 更方便评估双耳定位线索在整圈方位上的一致性。

### 7.2 为什么要用 ERB 滤波器组

ILD 不是简单地直接在全带宽上做左右耳能量比，而是先经过 auditory filter bank。

脚本使用 AuditoryToolbox：

- `ERBSpace`
- `MakeERBFilters`
- `ERBFilterBank`

配置是：

- 29 个 ERB band
- 频率范围 `[50, 6000] Hz`

这意味着当前项目的 ILD 评测更接近听觉相关分析，而不是纯物理能量比分析。

工具库实际位置：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\AuditoryToolbox`

### 7.3 ILD 怎么计算

对每个测试方向，先得到：

- 参考左右耳 HRIR
- BSM 重建左右耳时域响应

然后分别进入 ERB 滤波器组。对每个 band：

1. 计算左耳 band 输出能量。
2. 计算右耳 band 输出能量。
3. 做能量比的 dB 表达。

即：

- `ILD_band = 10 * log10(P_left / P_right)`

最后得到：

- `ILD_reference_bands(band, angle)`
- `ILD_BSM_bands(band, angle)`

### 7.4 平均 ILD 与 ILD 误差

脚本里定义了两个汇总量：

1. 平均 ILD
   - 在 29 个 ERB band 上取均值。
2. 平均 ILD 误差
   - 先取每个 band 的绝对误差，再跨 band 取平均。

也就是：

- `ILD_reference_avg(angle) = mean(ILD_reference_bands(:, angle))`
- `ILD_BSM_avg(angle) = mean(ILD_BSM_bands(:, angle))`
- `ILD_error_avg(angle) = mean(abs(ILD_BSM_bands(:, angle) - ILD_reference_bands(:, angle)))`

### 7.5 这一评测最有价值的地方

ILD 脚本特别适合检查：

- 高频和中频段的双耳电平差是否被保留。
- 某些方位上是否存在明显的左右耳能量失衡。
- 重建误差是宽带一致偏差，还是集中在少数听觉频带上。

尤其是它最后给出的 ERB-band 热力图，非常适合定位误差来源：

- 如果误差只出现在高频末端，通常是阵列建模或 HRTF 高频细节拟合不足。
- 如果误差在多数频带都大，往往说明滤波器设计本身有系统性问题。

---

## 8. 这两类评测与滤波器设计的关系

这部分是后续项目最应该理解的连接点。

### 8.1 滤波器设计解决的是“多方向逼近”

`BSM_reproduction.m` 本质是在每个频率上，寻找一组麦克风权重，使得：

- 对 `Q` 个训练方向，阵列输出尽量逼近目标双耳 HRTF。

所以它更像一个“训练过程”。

### 8.2 ITD / ILD 评测解决的是“感知线索是否保真”

`plot_ITD_fig8.m` 和 `plot_ILD_fig9.m` 并不关心滤波器矩阵本身长什么样，而是关心：

- 这个滤波器真正用于新方向时，能否保住双耳线索。

所以它更像一个“感知层面的验证过程”。

### 8.3 为什么这两部分最有复用价值

因为在另一个项目中，只要还满足下面三个条件，这两块逻辑几乎都能迁移：

1. 仍然是“阵列输入 -> 双耳输出”的问题。
2. 仍然使用 HRIR/HRTF 作为目标。
3. 仍然关心定位相关双耳线索而不只是频谱误差。

换句话说：

- 滤波器计算部分是“方法核心”。
- ITD/ILD 评测部分是“结果是否真的有听觉意义”的检查核心。

---

## 9. 迁移到其他项目时建议优先复用什么

### 9.1 可以直接复用的模块

- `BSM_reproduction.m`
  作为基础滤波器设计器。
- `SteeringVector.m`
  如果新项目仍是刚性球阵列或兼容的球谐建模。
- `get_sampled_hrir.m`
  如果仍然使用 KU100 数据和类似的方向抽样逻辑。
- `plot_ITD_fig8.m` 的 ITD 计算框架
  尤其是“低通 + 互相关峰值”的流程。
- `plot_ILD_fig9.m` 的 ILD 计算框架
  尤其是“ERB 滤波组 + 分 band 能量比”的流程。

它们在当前仓库中的绝对路径分别是：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\BSM_reproduction.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SteeringVector.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\get_sampled_hrir.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ITD_fig8.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ILD_fig9.m`

### 9.2 迁移时通常要替换的部分

- HRIR 数据集路径和对象加载方式。
- 阵列几何配置 `array_config`。
- steering vector 模型。
  如果不是刚性球阵列，这一部分必须重写。
- 训练方向数 `Q` 与球谐阶数 `N_order`。
- 评测方向集合。
  不一定非要是水平面 0 到 359 度。

---

## 10. 实现层面的关键细节和踩坑点

### 10.1 当前实现是按频点独立求解

每个频率点单独求一组复权重，没有显式跨频约束。

优点：

- 简单、清晰、容易分析。

代价：

- 频点之间不自动保证平滑。
- 某些频段可能会出现较强的局部波动。

### 10.2 训练和评测都强依赖坐标系定义

项目默认使用：

- `theta` 从正 `z` 轴向下量
- `phi` 从正 `x` 轴朝正 `y` 轴

如果另一个项目坐标定义不同，最容易出错的不是公式，而是：

- 麦克风方向错位
- 测试方向错位
- 左右或前后方位解释错位

这会直接把 ITD/ILD 图弄反或平移。

### 10.3 当前测试信号是单位脉冲

这意味着评测更接近：

- “系统本身的双耳冲激响应是否合理”

而不是：

- “某个真实宽带节目素材听起来是否合理”

如果后续项目更关心节目素材渲染效果，需要在这个框架上继续加实际输入信号验证。

### 10.4 ILD 评测依赖 AuditoryToolbox

如果目标项目里没有：

- `ERBSpace`
- `MakeERBFilters`
- `ERBFilterBank`

那就需要先补齐听觉滤波器组实现，否则 ILD 脚本不能直接跑通。

当前项目中的工具库路径是：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\AuditoryToolbox`

### 10.5 当前实现里有一个值得注意的工程细节

`BSM_reproduction.m` 在对 HRIR 做截断/补零后，又固定按 `hrir_length` 继续构造零填充 FFT 输入。实际复用时建议检查这一段，确保：

- 截断后使用的有效长度与后续 padding 逻辑一致。
- 不会因为原始 HRIR 长度和 `filter_length` 的关系变化而出现重复补零或维度问题。

也就是说，后续项目在直接复用时，最好把 HRIR 长度处理再整理一遍。

---

## 11. 建议的学习顺序

如果另一个项目要快速掌握这套方法，建议按下面顺序阅读：

1. 先看 `Test_BSM.m`
   先理解输入参数、阵列配置、输出结果长什么样。
2. 再看 `BSM_reproduction.m`
   重点看训练方向、HRTF 构造、`V` 的建立、正则化求解。
3. 然后看 `SteeringVector.m`
   理解阵列模型如何进入 BSM。
4. 接着看 `plot_ITD_fig8.m`
   理解低频时延线索怎么验证。
5. 最后看 `plot_ILD_fig9.m`
   理解听觉频带上的左右耳能量差怎么验证。

如果只想抓主线，可以压缩成：

1. `BSM_reproduction.m`
2. `plot_ITD_fig8.m`
3. `plot_ILD_fig9.m`

---

## 12. 给后续项目的最短总结

如果要把这套方法迁移到新项目，只需要先记住下面几句话：

- BSM 滤波器是在频域里、对每个频点独立求解的正则化多方向拟合器。
- 它把“阵列 steering response”拟合到“左右耳目标 HRTF”。
- ITD 评测看的是低频互相关峰值位置是否正确。
- ILD 评测看的是 ERB 听觉频带上的左右耳能量比是否正确。
- 真正决定结果质量的，不只是滤波器公式本身，还包括方向采样、阵列模型、HRIR 数据和坐标系一致性。

---

## 13. 推荐在新项目中保留的最小接口

如果新项目要做成可维护模块，建议至少保留下面几个接口：

- `design_bsm_filters(array_config, hrir_dataset, Q, filter_length, SNR_dB, model_config)`
- `render_binaural_response(filters, test_direction, array_config)`
- `evaluate_itd(reference_brir, rendered_brir, fs)`
- `evaluate_ild(reference_brir, rendered_brir, fs, erb_config)`

这样做的好处是：

- 设计、渲染、评测三部分职责清楚。
- 后面替换阵列模型或 HRTF 数据集时，不需要整体重写。

---

## 14. 本文档对应的源码锚点

建议在阅读本文档时，对照下面几个源码文件：

- `BSM_reproduction.m`
- `SteeringVector.m`
- `get_sampled_hrir.m`
- `plot_ITD_fig8.m`
- `plot_ILD_fig9.m`
- `Test_BSM.m`

这几个文件已经覆盖了当前项目最核心的方法链路。

对应绝对路径汇总如下：

- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\BSM_reproduction.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\SteeringVector.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\get_sampled_hrir.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ITD_fig8.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\plot_ILD_fig9.m`
- `D:\Files Library\Phd Files\Research Folder\binaural signal matching\Test_BSM.m`
