# GitHub Markdown 写作约束

本仓库的主要阅读环境是 **GitHub 网页端**。所有 Markdown 文档必须优先保证 GitHub Web 的渲染兼容性，而不是只在本地编辑器中显示正常。

参考：GitHub 官方文档《Writing mathematical expressions》：
<https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions>

## 1. 数学公式

### 1.1 行内公式

统一使用单美元符号：

```markdown
状态记为 $s_t$，动作为 $a_t$。
```

不要使用 `\(...\)` 作为默认行内格式。

### 1.2 独立公式块

统一使用双美元符号，并让起止符各自独占一行：

```markdown
$$
\hat y=f_\theta(x), \qquad
\min_\theta \mathbb E_{(x,y)\sim D}\left[\ell(f_\theta(x),y)\right].
$$
```

公式块前后各保留一个空行。

### 1.2.1 短公式正文必须单行

对于不需要 `aligned`、`cases`、`array`、矩阵等结构化环境的普通独立公式，`$$` 起止符仍各自独占一行，但公式正文必须写在同一个源码行中。

正确写法：

```markdown
$$
e_\theta = \operatorname{wrapToPi}(\theta_d-\theta).
$$
```

禁止为了视觉对齐，把左侧变量、等号和右侧表达式拆成多个普通源码行：

```markdown
$$
e_\theta
=
\operatorname{wrapToPi}(\theta_d-\theta).
$$
```

Markdown 源码中的普通换行不等于数学换行。确实需要多行推导时，必须显式使用 `aligned` 等结构化环境，并用 `\\` 标记数学换行；不要依赖公式块中的普通换行控制布局。

### 1.3 多行公式

优先在 `$$...$$` 中使用 `aligned`：

```markdown
$$
\begin{aligned}
a_t &\sim \pi_\theta(\cdot\mid o_t), \\
s_{t+1} &\sim P(\cdot\mid s_t,a_t).
\end{aligned}
$$
```

也可以使用 GitHub 官方支持的 `math` 代码块，但同一篇文档中应尽量保持一致。

### 1.4 禁止写法

本仓库默认禁止以下写法：

```markdown
\[
公式
\]
```

也禁止将公式仅放在普通方括号中：

```markdown
[ 公式 ]
```

原因是它们不能作为本仓库在 GitHub 网页端的可靠公式分隔符。

### 1.5 表格中的公式

表格中只放简短行内公式，例如 `$s_t$`、`$\pi(a\mid s)$`。

复杂公式必须移出表格，使用独立公式块。避免在表格中使用多行 LaTeX、`aligned` 或大量竖线符号。

### 1.6 公式书写要求

- 期望、概率、实数域等使用 `\mathbb{E}`、`\mathbb{P}`、`\mathbb{R}`；
- 条件概率或策略条件优先使用 `\mid`；
- 长括号使用 `\left[...\right]`、`\left(...\right)`；
- 向量和矩阵的粗体约定应在具体章节中统一；
- 每个关键公式后必须解释变量、假设和机器人含义，不能只堆公式；
- 不使用图片替代可由 MathJax 渲染的公式。

## 2. Mermaid 图

- 节点文本避免直接以 `@`、复杂括号或大段公式开头；
- 节点文字较复杂时使用引号；
- GitHub 网页端提交后必须检查是否能正常渲染；
- 公式较多的关系图优先使用普通文本图或分开解释，不强行塞入 Mermaid。

## 3. 代码块

- Python 使用 `python`；
- shell 命令使用 `bash`；
- 伪代码或目录结构使用 `text`；
- 数学公式不得放进普通代码块，除非目的是展示 Markdown 源码写法。

## 4. 提交前检查

新增或修改课程文档后至少检查：

1. 是否残留独立的 `\[` 或 `\]`；
2. 所有 `$$` 是否成对出现；
3. 公式块前后是否留有空行；
4. 非结构化独立公式的正文是否保持单行；
5. 表格中的公式是否过于复杂；
6. Mermaid 是否能在 GitHub 网页端渲染；
7. 文档内部链接是否有效。

## 5. 适用范围

该约束适用于：

- 课程讲义；
- 作业推导；
- ManiSkill 实验记录；
- 论文笔记；
- 阶段复盘；
- README 与项目规范。

若未来主要发布平台改变，应先更新本文件，再批量调整文档格式。
