# L03 独立代码实验：GridWorld MDP

本目录提供一个与官方作业无关的最小实验，用于把 MDP 的定义变成可运行对象。

## 学习边界

这个实验只覆盖：

- 状态、动作、转移分布、奖励、终止状态和时域；
- 随机策略执行与轨迹采样；
- 折扣回报；
- 使用 Monte Carlo 统计评估固定策略；
- 通过代码检查 Markov 假设和吸收终止状态。

暂不实现：

- Value Iteration；
- Policy Iteration；
- Q-Learning；
- Policy Gradient；
- 官方 Assignment 1 的任何题目或答案。

这些内容分别留给 L06、L07 和后续讲次。

## 运行

进入本目录：

```bash
python gridworld_mdp.py
```

运行测试：

```bash
python -m unittest test_gridworld_mdp.py
```

依赖只有 NumPy。

## 代码阅读顺序

1. 阅读 `Action`、`Transition`、`StepRecord` 和 `Episode`；
2. 阅读 `GridWorldMDP.transition_distribution()`；
3. 检查终止状态为何是 absorbing state；
4. 阅读 `sample_transition()`，区分模型与采样结果；
5. 阅读 `rollout()`，画出轨迹分布的数据流；
6. 阅读 `evaluate_policy()`，理解一次轨迹与多次统计的区别；
7. 最后阅读两个简单策略，观察策略本身并没有“优化器”。

## 必做主动修改

至少完成以下四项中的两项：

1. 将 `slip_probability` 从 `0.2` 改为 `0.0`、`0.4`，比较成功率与回报；
2. 将动作频率抽象成每一步 `0.1 s` 与 `0.5 s`，解释时域变化是否仍是同一个 MDP；
3. 增加一个“危险区域”，进入后得到较大负奖励，比较最短路径与低风险路径；
4. 在状态中增加朝向 `heading`，将动作改为前进、左转、右转，观察状态空间和转移模型如何变化。

## 故障注入

主动制造并解释：

- 转移概率和不为 1；
- 目标状态不是 absorbing；
- 忘记把速度加入需要惯性的机器人状态；
- 奖励只鼓励靠近目标，却允许机器人无限振荡；
- 只报告一次 rollout 的结果。

## 真实机器人映射

GridWorld 中的变量与机械臂抵近任务可做如下类比：

| GridWorld | 机械臂任务 |
|---|---|
| 网格位置 | 关节状态、末端位姿或任务相关状态 |
| 离散移动动作 | 关节命令、末端增量或高层子目标 |
| slip | 执行误差、模型误差、接触扰动 |
| 障碍格 | 碰撞约束、关节限位、不可达区域 |
| 目标格 | 成功集合，而不应只是单点 |
| step reward | 时间、能耗、路径长度或风险代价 |

真实系统中最重要的新增问题是：传感器通常只给出 observation，而不是完整 state；动作也通常还要经过 IK、轨迹生成和低层控制器。
