# 课程地图

本页依据 Cornell CS 4756/5756 Robot Learning Spring 2026 官方主页整理，作为项目的正式学习顺序。

课程主页：<https://www.cs.cornell.edu/courses/cs4756/2026sp/>

## 总体知识链

```text
机器人任务
   ↓
控制与动力学基础
   ↓
MDP / POMDP 形式化
   ↓
无模型决策：IL → DP/Q-Learning → PG → Actor-Critic → Deep RL
   ↓
基于模型决策：MPC → 动力学学习 → 奖励设计 → 仿真
   ↓
感知：相机 → 2D/3D 表示 → 状态估计 → 视觉运动策略
   ↓
前沿：迁移、多任务、生成模型、Transformer、层级决策、开放世界
```

## 官方讲次

> 状态说明：未开始 / 学习中 / 已完成 / 待复习。

### Part I：Fundamentals

| 编号 | 主题 | 主要问题 | 状态 |
|---|---|---|---|
| L01 | Introduction to Robot Learning | 什么问题需要机器人学习，学习系统为何难以进入真实世界 | 学习中 |
| L02 | Fundamentals of Robotic Control | 已知模型和目标时，如何用传统控制驱动机器人 | 学习中 |
| L03 | Markov Decision Processes | 如何统一描述序贯决策任务 | 未开始 |
| L04 | Deep Learning Tutorial | 策略、价值函数和感知模型所需的神经网络基础 | 未开始 |

### Part II：Model-Free Decision Making

| 编号 | 主题 | 主要问题 | 状态 |
|---|---|---|---|
| L05 | Imitation Learning | 如何从专家示范学习策略，以及为什么会发生分布偏移 | 未开始 |
| L06 | Value Function and Dynamic Programming | 如何用价值递推解决已知 MDP | 未开始 |
| L07 | Q-Learning | 不知道模型时如何学习动作价值 | 未开始 |
| L08 | Policy Gradients | 如何直接优化参数化策略 | 未开始 |
| L09 | Actor-Critic Methods | 如何结合策略优化与价值估计 | 未开始 |
| L10 | Deep Reinforcement Learning Algorithms | 如何把无模型 RL 扩展到高维连续任务 | 未开始 |

### Part III：Model-Based Decision Making

| 编号 | 主题 | 主要问题 | 状态 |
|---|---|---|---|
| L11 | Model Predictive Control | 如何利用模型滚动预测并实时重规划 | 未开始 |
| L12 | Dynamics Learning | 如何从数据学习可用于控制的动力学模型 | 未开始 |
| L13 | Reward Shaping and Learning | 如何定义、塑形或学习任务目标 | 未开始 |
| L14 | Simulation | 如何利用仿真训练与评估机器人策略 | 未开始 |

### Part IV：Perception

| 编号 | 主题 | 主要问题 | 状态 |
|---|---|---|---|
| L15 | Camera Models | 图像如何由三维世界形成 | 未开始 |
| L16 | 2D Visual Representations | 如何从图像中学习可用于机器人任务的表示 | 未开始 |
| L17 | 3D Visual Representations | 如何表示点云、深度和三维结构 | 未开始 |
| L18 | State Estimation | 如何从噪声观测估计不可直接获取的状态 | 未开始 |
| L19 | End-to-End Visuomotor Policy Learning | 如何从视觉观测直接产生机器人动作 | 未开始 |

### Part V：Frontiers

| 编号 | 主题 | 主要问题 | 状态 |
|---|---|---|---|
| L20 | Transfer Learning | 如何把能力迁移到新机器人、新任务或新场景 | 未开始 |
| L21 | Multi-Task Learning | 如何在多个任务间共享表示与策略能力 | 未开始 |
| L22 | Generative Models | 生成建模如何表示多峰动作和复杂数据分布 | 未开始 |
| L23 | Sequence Models: RNN, Transformer, Transformer Policy | 如何利用历史、上下文和动作序列 | 未开始 |
| L24 | Hierarchical Decision Making | 如何把长时序任务分解为高层和低层决策 | 未开始 |
| L25 | Open-World Robotics | 如何面对开放类别、未知场景和持续变化 | 未开始 |

## 官方作业映射

| 作业 | 主题 | 对应讲次 | 本项目目标 |
|---|---|---|---|
| A0 | NumPy and PyTorch | L04 前置 | 检查张量、自动微分和训练循环能力 |
| A1 | MDP & Imitation Learning | L03、L05 | 掌握任务形式化、BC 与分布偏移 |
| A2 | Policy Gradients | L08 | 掌握轨迹目标与策略梯度估计 |
| A3 | Actor-Critic Methods | L09–L10 | 掌握 advantage、critic 和稳定训练 |
| A4 | Model-Based RL | L11–L14 | 掌握动力学模型、预测和控制 |
| A5 | Perception | L15–L19 | 掌握视觉表示和机器人感知任务 |

## 与 ManiSkill 的实验映射

| 课程主题 | 建议实验 | 核心对照 |
|---|---|---|
| 控制基础 | 已知目标位姿下的抵近 | IK/轨迹规划/闭环控制 |
| MDP | 抵近或搬运任务形式化 | 不同状态、动作和奖励定义 |
| Imitation Learning | 专家轨迹训练抵近策略 | BC vs 传统控制；BC vs DAgger |
| Policy Gradient | 连续末端增量控制 | REINFORCE vs 简单控制器 |
| Actor-Critic | 提高样本效率 | PG vs A2C/PPO 类方法 |
| MPC | 搬运或推物任务滚动规划 | 开环轨迹 vs MPC |
| Dynamics Learning | 推块/接触局部动力学 | 真实模型 vs 学习模型 |
| Simulation | Domain Randomization | 固定仿真 vs 随机化训练 |
| State Estimation | 噪声目标位姿估计 | 真值状态 vs 滤波估计 |
| Visuomotor Policy | 图像 + 本体状态控制 | state policy vs visual policy |
| Transformer Policy | 历史观测与动作块 | MLP/单帧策略 vs 序列策略 |

## 阶段门槛

### 完成 Part I 前

应能独立回答：

1. 状态、观测、动作和控制输入有什么区别？
2. 已知目标位姿时，为什么通常先考虑控制或规划？
3. 一个机械臂任务何时是 MDP，何时更接近 POMDP？
4. 控制频率和策略频率为何不能随意混淆？

### 完成 Part II 前

应能：

- 推导 BC 的监督学习目标；
- 解释闭环分布偏移；
- 推导 Bellman 方程和基本策略梯度；
- 解释 critic、baseline、advantage 和 bootstrapping；
- 对比 BC、Q-Learning、Policy Gradient 和 Actor-Critic 的数据来源。

### 完成 Part III 前

应能：

- 写出有限时域控制目标；
- 解释 MPC 为什么能利用反馈修正模型误差；
- 区分模型偏差、规划误差和控制误差；
- 设计学习动力学模型的多步预测评测；
- 说明 Domain Randomization 何时有效、何时只是扩大训练分布。

### 完成 Part IV–V 前

应能：

- 区分几何状态估计与端到端视觉策略；
- 设计图像、本体状态和历史观测的消融实验；
- 解释生成策略、序列策略和层级策略各自解决的困难；
- 判断前沿策略模型相对于传统系统增加了什么能力和成本。

## 第一阶段计划

1. L01：建立 Robot Learning 系统框架；
2. L02：补齐控制、坐标系、运动学和反馈基础；
3. L03：把抵近、抓取、搬运、放置形式化为 MDP/POMDP；
4. A0：完成 PyTorch 与数值计算能力检查；
5. 建立第一个 ManiSkill 实验：同一抵近任务下比较传统控制与简单状态策略。