# L03 课后总结：Markov Decision Processes

> 本文件不是讲义摘要的替代品，而是学习完成后的个人复盘模板。请在阅读、推导、代码实验和主动修改后填写。

## 1. 一句话概括

待填写：

> MDP 通过 ____________________，统一描述 ____________________。

参考检查：是否同时提到“状态充分性”“状态转移”和“长期决策目标”。

## 2. 我真正理解了什么

### 2.1 State 的含义

用自己的话解释：

- state 为什么不是当前传感器数组的同义词；
- “对未来预测充分”是什么意思；
- 为什么遗漏速度、接触模式或任务阶段会破坏 Markov 性。

我的理解：

> 待填写。

### 2.2 MDP 的组成

不看讲义写出：

$$
\mathcal M=(\underline{\hspace{8cm}}).
$$

并为每个元素写一个机器人例子。

### 2.3 轨迹分布

不看讲义补全：

$$
p_\pi(\tau)=\underline{\hspace{12cm}}.
$$

解释策略为什么会改变未来训练数据分布。

### 2.4 长期目标

不看讲义写出有限时域折扣回报和策略目标。

我的解释：

> 待填写。

## 3. 最容易混淆的概念

| 概念对 | 我的区分 |
|---|---|
| state vs observation | |
| policy vs trajectory | |
| reward vs value | |
| terminated vs truncated | |
| deterministic vs stochastic transition | |
| finite horizon vs infinite horizon | |
| MDP vs POMDP | |
| action vs low-level control input | |

## 4. 我的机器人任务形式化

选择当前主线任务：

- [ ] PickCube-v1
- [ ] 抵近
- [ ] 抓取
- [ ] 搬运
- [ ] 放置
- [ ] GearInsertion
- [ ] 其他：__________

### 4.1 状态与观测

- 仿真 state：
- policy observation：
- 真实传感器来源：
- 可能缺失的隐变量：
- 是否需要历史：

### 4.2 动作

- 动作接口：
- 策略频率：
- action repeat：
- 底层控制器：
- 安全限制：

### 4.3 转移

- 主要确定性因素：
- 主要随机性：
- 仿真与真实差距：
- 未建模延迟：

### 4.4 奖励与验收

- 任务 reward：
- success condition：
- failure condition：
- truncated condition：
- 真实验收指标：
- reward 与验收不一致处：

## 5. GridWorld 实验记录

### 5.1 基线

记录：

| 设置 | Mean Return | Return Std | Success Rate | Mean Length |
|---|---:|---:|---:|---:|
| 默认 | | | | |

### 5.2 主动修改

修改一：

- 改了什么：
- 预测：
- 结果：
- 是否符合预测：
- 原因：

修改二：

- 改了什么：
- 预测：
- 结果：
- 是否符合预测：
- 原因：

### 5.3 故障注入

- 故障：
- 表现：
- 原测试能否发现：
- 新增测试：
- 真实系统风险：

## 6. 工程判断

### 6.1 工业价值

本讲对工业机器人交付最直接的帮助：

1. 任务边界：
2. 数据字段：
3. 传感器选型：
4. 动作接口：
5. 失败与安全：
6. 评测协议：

### 6.2 家庭迁移价值

从当前工业任务可迁移到家庭场景的能力：

- 状态估计：
- 历史与记忆：
- 多阶段任务：
- 异常检测：
- 恢复策略：
- 安全约束：

在家庭环境中会失效的工业假设：

> 待填写。

## 7. 我能做出的工程证据

本讲不以“讲义已生成”为完成。至少保留：

- [ ] 一份完整 MDP spec；
- [ ] 一张 state/observation/action 数据流图；
- [ ] 一次 GridWorld 运行记录；
- [ ] 两组控制变量实验；
- [ ] 一个故障注入与新增测试；
- [ ] 一段 3–5 分钟口头解释或书面复盘；
- [ ] 一份 ManiSkill 到真实机器人变量映射表。

## 8. 与后续讲次的连接

### L05 Imitation Learning

我现在能够解释：专家数据来自 $p_{\pi_E}(\tau)$，学习策略部署后会改变状态分布。

仍需学习：

> 待填写。

### L06 Dynamic Programming

我现在知道 value 的定义，但尚未完整推导 Bellman 递推和求解算法。

仍需学习：

> 待填写。

### L18 State Estimation

我已经识别哪些 observation 不等于 state。

仍需学习：

> 待填写。

## 9. 未解决问题

1. 
2. 
3. 

需要转入 [`../../05-review/question-parking-lot.md`](../../05-review/question-parking-lot.md) 的问题：

> 待填写。

## 10. 掌握度自评

| 等级 | 是否达到 | 证据 |
|---|---|---|
| L1 识别 | | |
| L2 解释 | | |
| L3 形式化 | | |
| L4 实现 | | |
| L5 验证 | | |
| L6 应用 | | |

建议：本讲至少达到 L3；完成代码主动修改和故障注入后达到 L4；完成 ManiSkill 任务形式化与真实映射后开始接近 L5。
