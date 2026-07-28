# Clip 02：专家数据、Behavior Cloning 与闭环评测

## 1. 本阶段目标

建立从专家控制器到训练数据、从监督学习到闭环执行的完整链路，并理解：

> 训练集上的动作预测误差很低，不代表机器人闭环任务成功率高。

本阶段只解决专家能够稳定演示的正常执行，不承担复杂卡滞恢复。

## 2. 数据生成

使用 Clip 01 的状态机专家采集：

- 成功轨迹；
- 接近失败但被专家纠正的轨迹；
- 不同初始位置和姿态；
- 不同动作速度；
- 适量专家动作噪声；
- 完整环境随机化参数。

每条 transition 至少保存：

```text
episode_id
timestep
observation
raw_state
action
executed_action
phase_id
reward
success
failure_code
env_randomization
seed
timestamp
```

图像版本后续再加入，第一版先用状态观测验证闭环。

## 3. 数据质量检查

训练前必须完成：

- observation/action shape 检查；
- NaN、Inf 和越界值检查；
- episode 长度分布；
- 成功与失败比例；
- 每个 phase 的样本比例；
- 动作直方图；
- 时间对齐检查；
- 环境随机化覆盖范围；
- train/validation/test 按 episode 切分。

禁止按 transition 随机切分同一 episode，否则会造成信息泄漏。

## 4. BC 基线

第一版使用简单 MLP：

```text
normalized observation
→ MLP
→ predicted action
→ action denormalization / clipping
```

损失可从均方误差开始：

$$
\mathcal{L}_{BC}(\theta)=\mathbb{E}_{(o,a)\sim D}\left[\|\pi_\theta(o)-a\|_2^2\right].
$$

如果动作中平移、旋转和夹爪量纲不同，应分别归一化或设置权重，不能直接假设各维同等重要。

## 5. 两类评测必须分开

### 5.1 离线评测

- validation loss；
- 每个动作维度误差；
- phase 分组误差；
- 极端状态误差。

### 5.2 闭环评测

- 成功率；
- 轨迹长度；
- 横向和姿态误差；
- 卡滞率；
- 失败类型；
- 与专家状态分布的偏离；
- 分布内和分布外表现。

结论优先依据闭环任务指标，而不是训练 loss。

## 6. Codex 实现任务

### Task 02A：数据采集器

- 将专家轨迹保存为明确版本的数据格式；
- 保存任务配置和代码 commit 信息；
- 支持断点续采和数据校验；
- 编写小数据集测试。

### Task 02B：Dataset 与归一化

- 按 episode 切分；
- 统计训练集 normalization；
- 验证集和测试集禁止重新拟合统计量；
- 输出每个 batch 的 shape 文档。

### Task 02C：BC 模型与训练

- 简单 MLP；
- 配置化网络宽度、历史长度和损失权重；
- 保存 checkpoint、optimizer、随机种子和日志；
- 提供最小过拟合测试：先在极小数据上确认 loss 能下降。

### Task 02D：闭环评测

- 加载 checkpoint；
- 在统一随机种子上运行；
- 与专家基线并排输出；
- 自动保存典型失败轨迹。

## 7. 代码阅读清单

你必须能指出：

1. 数据在哪一步从 episode 变成 transition；
2. observation 的拼接顺序；
3. normalization 统计量来自哪一部分数据；
4. 模型输出怎样变成环境动作；
5. 训练和评测模式如何切换；
6. checkpoint 是否包含完整复现信息；
7. 闭环评测是否意外使用专家状态或未来信息。

## 8. 必做实验

### 实验 A：数据量

比较至少三种数据量，观察离线 loss 与闭环成功率是否同步变化。

### 实验 B：观测消融

删除 `object_to_target_pose` 或其他关键相对状态，分析性能变化。

### 实验 C：动作表示

比较绝对目标动作与增量动作，或比较不同动作缩放。

### 实验 D：专家噪声

加入小幅专家动作扰动，观察是否提高状态覆盖，还是降低动作一致性。

## 9. 主动修改任务

至少完成：

- 增加 2–4 步历史观测；
- 分别调整平移和旋转 loss 权重；
- 修改 normalization；
- 将单步动作扩展为短 action chunk；
- 添加上一时刻动作作为输入。

每次只改变一个主要变量。

## 10. 故障注入

主动制造：

- observation 字段顺序在训练和评测不一致；
- action normalization 忘记反归一化；
- train/test transition 混在同一 episode；
- 使用下一时刻状态预测当前动作；
- 模型评测时未切换 `eval()`；
- 环境动作裁剪隐藏了过大的模型输出。

记录症状、定位过程和测试修复。

## 11. 应用映射

回答：

- 专家在真实系统中由谁提供；
- 专家是否需要遥操作、手把手示教或传统控制器；
- 数据采集每小时能获得多少有效 episode；
- 哪些危险或失败状态无法安全示范；
- 模型输出异常时系统如何限幅和回退。

## 12. 阶段产物

- 版本化专家数据集；
- 数据质量报告；
- BC 模型和训练脚本；
- 离线与闭环评测；
- 至少四个对照实验；
- 失败轨迹库；
- `analysis.md`：解释 loss 与闭环结果的差异。

## 13. 通过门槛

- 能从一个 batch 逐维解释数据；
- 小数据过拟合测试通过；
- 训练、验证和测试无 episode 泄漏；
- BC 在固定条件下明显优于随机策略；
- 能展示至少一种误差累积导致的分布偏移；
- 能说明真实采集数据与仿真专家数据的主要差异。
