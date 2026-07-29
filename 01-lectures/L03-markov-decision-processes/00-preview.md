# L03 课前导读：Markov Decision Processes

## 1. 本讲在课程中的位置

Lecture 02 建立了机器人控制闭环：状态经过动力学和控制输入演化，传感器提供反馈，控制器持续减小误差。

Lecture 03 进一步追问：

> **当机器人需要连续做出一系列会改变未来状态的决策时，如何用统一数学对象描述任务、环境、策略和长期目标？**

MDP 是后续模仿学习、动态规划、Q-Learning、Policy Gradient、Actor-Critic、MPC 和部分 VLA 讨论的共同语言。

```text
L02：状态、动力学、控制接口与反馈
        ↓
L03：状态、动作、转移、奖励、时域与策略
        ↓
L05–L10：如何从示范或交互数据学习策略
        ↓
L11–L14：如何利用或学习模型进行决策
```

本讲不是在回答“用什么算法求解 MDP”，而是先保证问题被正确形式化。状态遗漏、动作接口错误、奖励不完整或终止条件不合理，都会让后续算法优化错误的问题。

## 2. 官方材料

- 课程主页：<https://www.cs.cornell.edu/courses/cs4756/2026sp/>
- 2026 Lecture 03 课件：<https://drive.google.com/file/d/1qZiHppwM0UE55soqtnwO_6yABc2hxPrB/view?usp=sharing>
- 指定阅读：*Modern Adaptive Control and Reinforcement Learning*，Chapter 1：<https://macrl-book.github.io/assets/pdf/1_macrl.pdf>

官方课程将本讲安排在 2026-01-27，并把 MDP 与后续 Assignment 1：MDP & Imitation Learning 连接。

> **材料边界**：本讲以 MDP 形式化为核心。Bellman 最优方程、Value Iteration 和 Policy Iteration 只建立直觉，不在此处展开完整算法；它们属于 L06。Q-Learning 与策略梯度分别留给 L07、L08。

## 3. 学习目标

完成本讲后，应能：

- 用状态的“未来预测充分性”解释 Markov 性，而不是把当前观测直接称为状态；
- 写出一个 MDP 的基本组成：状态空间、动作空间、初始状态分布、转移模型、奖励或成本、时域、折扣因子和终止条件；
- 区分 deterministic transition 与 stochastic transition；
- 区分 state、observation、history、belief state；
- 写出策略诱导的轨迹分布；
- 写出有限时域和无限折扣时域的期望累计回报；
- 解释为什么有限时域最优策略可能依赖时间；
- 区分 policy、trajectory、plan、controller 与 low-level action；
- 为抵近、抓取、搬运、放置和接触装配分别提出合理状态与动作接口；
- 识别状态遗漏、奖励投机、终止错误和仿真特权信息等常见形式化失败；
- 运行独立 GridWorld 实验，并通过主动修改验证 horizon、discount、stochasticity 和 reward 对结果的影响。

## 4. 必要前置知识

### 4.1 概率

需要理解：

- 条件概率 $p(x\mid y)$；
- 随机变量与概率分布；
- 期望 $\mathbb{E}[X]$；
- 联合分布的链式分解；
- 条件独立的基本含义。

### 4.2 控制与机器人变量

需要能区分：

- 构型 $q_t$；
- 动态状态 $x_t$，例如 $[q_t^\top,\dot q_t^\top]^\top$；
- 观测 $o_t$；
- 控制输入 $u_t$；
- 任务空间目标和成功集合；
- 低层控制频率与高层策略频率。

### 4.3 本讲统一符号

- 状态：$s_t\in\mathcal S$；
- 动作：$a_t\in\mathcal A$；
- 初始状态：$s_0\sim\rho_0$；
- 转移：$s_{t+1}\sim P(\cdot\mid s_t,a_t)$；
- 奖励：$r_t=r(s_t,a_t,s_{t+1})$；
- 策略：$a_t\sim\pi(\cdot\mid s_t,t)$；
- 时域：$H$；
- 折扣因子：$\gamma\in[0,1]$；
- 轨迹：$\tau=(s_0,a_0,s_1,a_1,\ldots,s_H)$；
- 回报：$G(\tau)$；
- 价值函数：$V^\pi(s,t)$，本讲只建立定义和直觉。

## 5. 带着问题阅读

1. 什么变量必须包含在状态中，才能让过去历史对未来预测不再提供额外信息？
2. 机械臂只有关节角、没有关节速度时，系统一定满足 Markov 性吗？
3. 一张 RGB 图像通常是 state 还是 observation？
4. 策略输出关节力矩、关节位置、末端增量或高层子目标时，MDP 是否相同？
5. 为什么“最短时间到达目标”的奖励可能导致碰撞或猛烈动作？
6. 为什么有限时域策略可能写成 $\pi(a\mid s,t)$？
7. 折扣因子只是为了偏好更快奖励吗？它还改变了什么数学性质？
8. 接触装配中的摩擦、卡滞模式和接触历史没有进入状态时，会发生什么？
9. 仿真中可以直接读取物体真值位姿，真实部署中却只能看到图像，这个训练问题仍是同一个 MDP 吗？
10. 如何判断一个失败来自求解算法，还是来自 MDP 定义本身？

## 6. 推荐阅读顺序

### 第一步：先写出交互循环

```text
s_t
 ↓
策略 π(a_t | s_t, t)
 ↓
a_t
 ↓
环境 P(s_{t+1} | s_t, a_t)
 ↓
r_t, s_{t+1}
 ↓
进入下一次决策
```

先不要考虑神经网络。策略可以是表格、规则、控制器、搜索器或参数化模型。

### 第二步：理解 state 是充分统计量

重点不是“状态包含多少变量”，而是：

> 给定当前状态和动作后，完整历史是否还会改变下一个状态的条件分布？

若会，则当前状态定义不充分，或真实任务更接近 POMDP。

### 第三步：列出 MDP 元素

对一个具体机器人任务，依次回答：

1. 机器人和环境中哪些变量决定未来？
2. 策略能够选择什么？
3. 下一状态如何产生？
4. 什么行为应该被鼓励或惩罚？
5. 任务何时结束？
6. 评价是有限时域还是无限时域？
7. 哪些变量在仿真可得、真实系统不可得？

### 第四步：从单步奖励转向轨迹目标

单步动作不能独立评价，因为当前动作会改变未来可达状态和未来数据分布。

需要从：

$$
\max_a r(s_t,a)
$$

转向：

$$
\max_\pi \mathbb{E}_{\tau\sim p_\pi(\tau)}\left[\sum_{t=0}^{H-1}\gamma^t r(s_t,a_t,s_{t+1})\right].
$$

### 第五步：映射到机械臂四阶段

分别为以下阶段写出状态、动作、转移、奖励和终止：

- 抵近；
- 接触与抓取；
- 搬运；
- 放置或插装。

注意：四个阶段不一定应该共享同一个动作频率、状态表示、奖励和控制接口。

## 7. 可以暂时略读的内容

本讲可以暂时略读：

- Bellman 算子的收缩映射证明；
- Value Iteration 与 Policy Iteration 的完整推导；
- 连续状态动态规划的数值方法；
- Q-Learning 收敛证明；
- Policy Gradient theorem；
- POMDP belief update 的完整推导；
- average-reward MDP 的严格理论。

但不能略过：

- Markov 性；
- state 与 observation 的区别；
- 转移分布；
- 策略诱导轨迹分布；
- 累计回报；
- horizon、discount 和 terminal state；
- 机器人任务中状态、动作与奖励的工程选择。

## 8. 课前输出

正式学习前，完成以下输出：

1. 用一句话解释 MDP 试图解决什么问题；
2. 为 PickCube-v1 写出一个仿真特权状态版本的 MDP；
3. 再写出一个真实相机观测版本，指出它为何可能是 POMDP；
4. 比较关节位置动作与末端位姿增量动作对任务难度的影响；
5. 写出一个可能被 reward hacking 利用的奖励；
6. 指出至少两个应当作为 terminal condition 的失败；
7. 预测 `slip_probability` 增大后，独立 GridWorld 实验的成功率和回报会如何变化。
