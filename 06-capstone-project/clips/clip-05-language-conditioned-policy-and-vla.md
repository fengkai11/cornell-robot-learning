# Clip 05：语言条件策略与轻量 VLA

## 1. 本阶段目标

将单任务装配扩展为语言条件下的多对象、多目标或多技能任务，并验证语言是否真正改变策略行为。

本阶段不把 VLA 当作“替代全部模块的万能模型”。推荐顺序是：

```text
固定任务视觉/状态策略
→ Language-conditioned ACT
→ 多对象、多目标组合泛化
→ SmolVLA 参数高效适配
→ 与分层混合系统对照
```

## 2. 为什么先做 Language-conditioned ACT

在接入预训练 VLA 前，先用较小的语言条件策略验证：

- 数据中是否真的存在语言变化；
- 指令是否和对象、目标、技能正确对齐；
- 模型是否能够根据语言改变动作；
- 多任务组合是否定义合理；
- 失败来自任务设计、数据还是预训练模型适配。

如果简单模型无法学会任务，直接换更大 VLA 通常只会增加诊断难度。

## 3. 多任务环境扩展

场景至少加入两类变化：

### 3.1 对象或目标变化

```text
Insert the red peg into the left hole.
Insert the blue peg into the right hole.
Mount the small gear on the front shaft.
Place the large gear in the tray.
```

### 3.2 技能变化

```text
Insert the peg.
Remove the peg.
Lift and retry.
Place the gear in the tray.
```

第一版只使用模板化英文，避免同时引入中文 tokenizer、翻译和复杂语义问题。

## 4. 必须避免的伪 VLA 设置

以下设置不能证明语言能力：

- 所有数据只有一句固定指令；
- 每个对象永远只对应一个固定目标；
- 语言变化与相机背景或初始位置完全绑定；
- 更换语言后动作不变但仍声称模型理解指令；
- 测试组合在训练数据中已经完整出现；
- 只比较最终成功率，不做错误语言和空语言对照。

## 5. Language-conditioned ACT 基线

输入：

```text
image or state history
robot_state
language_embedding
```

输出：

```text
action chunk [H, action_dim]
```

建议先冻结一个轻量文本编码器，或使用固定语言 embedding，重点验证任务条件是否生效，而不是一开始训练语言模型。

## 6. SmolVLA 适配路线

SmolVLA 是 LeRobot 提供的轻量 VLA 基础模型，官方模型规模为 450M，输入多相机、机器人状态和自然语言，输出 action chunk。对 RTX 4060 Laptop GPU，课程主线采用：

1. 完成数据格式适配和推理；
2. 冻结视觉语言骨干，只训练动作相关模块；
3. 使用 PEFT/LoRA；
4. 显存允许时再逐步解冻少量后层；
5. 不把全参数训练作为必做项。

保守配置从以下方向开始：

```yaml
num_cameras: 1
image_size: 224
batch_size: 1
gradient_accumulation_steps: 8
mixed_precision: fp16_or_bf16
gradient_checkpointing: true
freeze_vision_encoder: true
freeze_language_backbone: true
train_action_expert: true
action_chunk_size: 10
history_length: 1
```

实际参数必须以当前 LeRobot 版本的官方配置字段为准，Codex 实现前先查阅官方文档和源码。

## 7. 数据格式

每个 episode 至少包含：

```text
camera image(s)
robot state
action
language instruction
task id
object id
target id
skill id
environment randomization
success/failure
```

语言标注需要控制变量：

- 同一任务有多种表述；
- 同一句式覆盖不同对象和目标；
- 对象、目标和动作组合不能完全绑定；
- 训练和测试按组合划分，而不仅是随机 episode 划分。

## 8. Codex 实现任务

### Task 05A：多任务环境

- 支持对象、目标和技能配置；
- 指令由任务配置确定；
- 记录每个语义变量；
- 增加组合划分测试。

### Task 05B：Language-conditioned ACT

- 文本编码器与机器人策略解耦；
- 支持空语言、错误语言和打乱语言；
- 输出 action chunk；
- 保存注意力或语言 embedding 仅用于辅助诊断。

### Task 05C：LeRobot 数据转换

- 将 ManiSkill 数据转换为当前 LeRobotDataset 格式；
- 校验图像、状态、动作、时间戳和语言对齐；
- 用少量数据完成读取和前向测试；
- 记录 LeRobot commit 或版本。

### Task 05D：SmolVLA 参数高效适配

- 先完成预训练 checkpoint 加载；
- 输出可训练参数列表和比例；
- 支持冻结动作头、只训练动作头和 PEFT 三种配置；
- 记录显存峰值、单步耗时和推理延迟；
- 出现 OOM 时自动降低配置，但不得静默改变实验。

## 9. 必做实验

### 实验 A：语言敏感性

同一场景分别输入：

- 正确指令；
- 错误指令；
- 空指令；
- 随机打乱指令。

如果行为几乎不变，应判断模型忽略语言。

### 实验 B：组合泛化

训练：

```text
red peg → left hole
blue peg → right hole
```

测试：

```text
red peg → right hole
blue peg → left hole
```

需要谨慎解释：成功可能来自颜色、位置或任务先验，必须配合消融。

### 实验 C：预训练价值

比较：

- Language-ACT from scratch；
- SmolVLA 只训练动作模块；
- SmolVLA + PEFT；
- 相同结构随机初始化（可行时）。

重点比较数据效率、组合泛化、显存和推理延迟。

### 实验 D：VLA 与 Residual RL

比较：

- VLA 单独执行；
- VLA 负责目标和正常动作，Residual RL 处理接触；
- Language-ACT + Residual RL；
- 分层状态机 + 技能策略。

## 10. 主动修改任务

至少完成：

- 增加指令改写；
- 打破对象与目标固定绑定；
- 改变 action chunk 长度；
- 加入腕部相机或移除主相机；
- 修改可训练模块；
- 比较冻结骨干和 PEFT；
- 将 VLA 从底层连续控制改为高层技能选择。

## 11. 故障注入

主动制造：

- 语言与 episode 错位；
- 所有任务被错误写成相同语言；
- train/test 组合泄漏；
- 图像通道或归一化错误；
- 动作维度映射错误；
- checkpoint 与配置版本不匹配；
- 模型看似成功但移除语言后结果不变；
- ManiSkill 渲染与训练同时占用显存导致 OOM。

## 12. 应用映射

VLA 在真实系统中优先负责：

- 识别用户指定的对象和目标；
- 在已有技能中进行选择；
- 处理任务改写和多任务条件；
- 为低层策略提供语义条件。

高速接触控制、安全停止和力限制不应只依赖语言模型。

## 13. 工业与家庭迁移价值

### 工业

- 多型号工件共线；
- 柔性换产；
- 自然语言或结构化工单驱动；
- 共享操作策略与局部专用技能。

### 家庭

- 用户语言指令变化更大；
- 对象和目标组合更多；
- 场景变化与遮挡更强；
- VLA 的高层泛化价值高于固定工位，但低层安全和恢复仍需专门设计。

## 14. 阶段产物

- 多任务环境；
- 语言条件数据集；
- Language-ACT；
- LeRobot 数据适配器；
- SmolVLA 参数高效适配配置；
- 语言敏感性和组合泛化实验；
- 显存、速度和模型规模对比；
- VLA 在系统中应承担与不应承担的职责说明。

## 15. 通过门槛

- 更换指令能在同一场景中稳定改变目标或技能；
- 空语言和错误语言对照完整；
- 训练/测试组合无泄漏；
- 能列出实际参与训练的参数；
- 能解释预训练带来的收益是否超过工程复杂度；
- 4060 上训练和推理流程可复现；
- 不把 VLA 的语言理解能力与接触控制能力混为一谈。
