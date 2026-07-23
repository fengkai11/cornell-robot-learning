# 课程讲义与学习笔记

本目录按官方讲次保存每一讲的完整学习记录。

## 当前讲次

### L01：Introduction to Robot Learning（学习中）

- [课前导读](L01-introduction-to-robot-learning/00-preview.md)
- [正式讲义](L01-introduction-to-robot-learning/01-notes.md)
- [课堂练习与自测](L01-introduction-to-robot-learning/02-exercises.md)
- [课后总结](L01-introduction-to-robot-learning/03-summary.md)
- 指定阅读笔记：[*The Bitter Lesson*](L01-introduction-to-robot-learning/reading-notes/01-the-bitter-lesson.md)

### L02：Fundamentals of Robotic Control（学习中）

- [课前导读](L02-fundamentals-of-robotic-control/00-preview.md)
- [正式讲义](L02-fundamentals-of-robotic-control/01-notes.md)
- [课堂练习与自测](L02-fundamentals-of-robotic-control/02-exercises.md)
- [课后总结](L02-fundamentals-of-robotic-control/03-summary.md)

L02 以 configuration、degrees of freedom、configuration space、task space、运动学和反馈控制为主线，建立后续 MDP、IL、MPC 与 visuomotor policy 所需的传统控制基线。

完成练习并通过概念检查后，才能将讲次从“学习中”更新为“已完成”。

## 目录约定

```text
01-lectures/
├── lecture-template.md
├── L01-introduction-to-robot-learning/
│   ├── 00-preview.md
│   ├── 01-notes.md
│   ├── 02-exercises.md
│   ├── 03-summary.md
│   └── reading-notes/
│       └── 01-the-bitter-lesson.md
└── L02-fundamentals-of-robotic-control/
    ├── 00-preview.md
    ├── 01-notes.md
    ├── 02-exercises.md
    └── 03-summary.md
```

## 文件职责

- `00-preview.md`：课前导读、前置知识、带着问题阅读；
- `01-notes.md`：正式讲授内容、定义、推导、例子；
- `02-exercises.md`：概念题、推导题、机器人任务形式化练习；
- `03-summary.md`：课后总结、掌握度和未解决问题；
- `reading-notes/`：保存指定阅读的原始理解、导师解析、认知修订和待读问题。

## 学习要求

每讲至少完成以下检查：

1. 能否用一句话说清本讲解决的问题；
2. 能否写出关键变量和目标函数；
3. 能否说明隐含假设；
4. 能否给出一个传统方法或简单方法对照；
5. 能否解释至少一种失败模式；
6. 能否把概念映射到抵近、抓取、搬运、放置或装配任务；
7. 能否提出一个可以被实验否证的假设。

## 笔记边界

课程笔记优先服务于 Cornell 主线。以下内容可以引用，但不能反客为主：

- Diffusion Policy、ACT、VLA 等后续策略模型；
- 具身智能产业分析；
- 创业和产品判断；
- “空间智能”项目中的长期研究假设。

明显偏离当前讲次的问题记录到 [`../05-review/question-parking-lot.md`](../05-review/question-parking-lot.md)。