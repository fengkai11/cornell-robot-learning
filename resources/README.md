# 资源索引

本页集中记录课程官方资源和必要前置材料。课程主页始终作为信息主源。

## 官方入口

- Cornell CS 4756/5756 Robot Learning Spring 2026：<https://www.cs.cornell.edu/courses/cs4756/2026sp/>
- 官方课程主页中的 Schedule：课件与推荐阅读入口
- 官方 Assignments：A0–A5 作业仓库入口

## 主要教材

课程主页列出的核心教材包括：

1. **Modern Adaptive Control and Reinforcement Learning (MACRL)**  
   用于 MDP、模仿学习、强化学习、控制和在线学习主线。

2. **Modern Robotics: Mechanics, Planning, and Control**  
   用于机器人运动学、动力学、控制和规划基础。

3. **Reinforcement Learning: An Introduction**  
   用于价值函数、动态规划、TD、Policy Gradient 和 Actor-Critic 基础。

4. **Multiple View Geometry in Computer Vision**  
   用于相机模型和多视几何。

5. **Probabilistic Robotics**  
   用于状态估计、概率推断和机器人感知补充。

## 工具与框架

- Python 3.10+；
- NumPy；
- PyTorch；
- Gymnasium；
- ManiSkill；
- TensorBoard 或 Weights & Biases（实验记录二选一即可）；
- Git / GitHub；
- Jupyter（只用于探索，正式实验应沉淀为脚本和配置）。

## 环境记录原则

首次建立环境后，应新增 `environment.md`，记录：

- 操作系统；
- Python 版本；
- CUDA、驱动和 GPU；
- PyTorch、ManiSkill、SAPIEN、Gymnasium 版本；
- 安装命令；
- 最小运行验证；
- 已知兼容性问题。

不要只保存 `pip freeze`。需要同时说明哪些依赖是直接依赖、哪些是间接依赖。

## 资料使用顺序

遇到课程概念时，按以下顺序查阅：

1. 官方课件；
2. 官方推荐阅读；
3. 作业题目与代码框架；
4. 对应经典教材章节；
5. 原始论文；
6. 其他课程或博客作为辅助解释。

二手资料不能覆盖官方符号定义和课程边界。

## 版本与来源记录

由于课程主页和在线教材可能更新，笔记中引用重要材料时记录：

- 标题；
- 链接；
- 访问日期；
- 版本或提交号（如有）；
- 使用的具体章节或页码。
