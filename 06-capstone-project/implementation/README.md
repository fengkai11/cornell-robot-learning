# Clip 00 Implementation

本目录实现 `clip-00-application-definition.md` 要求的纯数据结构、配置校验、失败日志合同与离线汇总。它**不包含** ManiSkill 环境、机器人控制器或学习算法。

## 依赖

代码只依赖 `PyYAML`；测试额外依赖 `pytest`。ManiSkill 环境通常已经包含这两个包，可以先直接运行。缺少时执行：

```bash
python -m pip install PyYAML pytest
```

可选地安装为 editable package：

```bash
python -m pip install --no-build-isolation -e "06-capstone-project/implementation[test]"
```

## 运行配置校验

```bash
python 06-capstone-project/implementation/scripts/validate_configs.py
```

期望输出包含：

```json
{
  "status": "ok",
  "task_id": "gear-insertion-state-v0",
  "criteria": 7,
  "failure_codes": 13
}
```

## 运行测试

```bash
python -m pytest 06-capstone-project/implementation/tests
```

测试覆盖 Clip 00 要求的故障注入：

- 缺失必填指标；
- 成功率阈值为负数；
- 未注册失败码；
- episode 日志缺少随机种子；
- episode 超时配置与控制频率矛盾。

## 汇总 episode 日志

先用示例日志验证接口：

```bash
python 06-capstone-project/implementation/scripts/summarize_episodes.py \
  06-capstone-project/implementation/configs/sample-episodes.jsonl
```

后续 ManiSkill 环境每个 episode 输出一行 JSON，字段必须满足 `EpisodeLog`。汇总脚本会计算：

- 总体与各 split 成功率；
- Wilson 95% 区间；
- 各随机种子成功率；
- 失败类型分布；
- 卡滞检测召回率；
- 卡滞恢复成功率；
- 危险事件数；
- 平均重试次数；
- 失败诊断覆盖率；
- 验收指标通过情况。

当有效样本数低于 `acceptance-criteria.yaml` 中的要求时，指标状态为 `insufficient_samples`，不会被误判为通过。

## 推荐阅读顺序

1. `configs/task-specification.yaml`；
2. `capstone_clip00/models.py` 中的 `TaskSpecification`；
3. `FailureCode`、`FailureCatalog`；
4. `EpisodeLog`；
5. `capstone_clip00/evaluation.py`；
6. `tests/test_config_validation.py`。

## 你需要主动完成的修改

从下面选择一项，并重新运行测试和配置校验：

- 将位置扰动从 `10 mm` 改为 `15 mm`；
- 将成功位置阈值从 `2 mm` 改为 `1 mm`；
- 将最大接触力从 `20 N` 改为更保守值；
- 修改最大重试次数；
- 修改控制频率、最大步数和超时时间，并保持三者一致。

修改后在 clip 复盘中说明：任务难度、系统风险和验收指标应如何变化。
