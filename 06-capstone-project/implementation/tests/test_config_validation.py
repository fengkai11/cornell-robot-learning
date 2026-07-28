from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from capstone_clip00.evaluation import evaluate_acceptance, summarize_episode_logs
from capstone_clip00.io import (
    load_acceptance_criteria,
    load_episode_logs_jsonl,
    load_failure_catalog,
    load_task_specification,
)
from capstone_clip00.models import (
    AcceptanceCriteria,
    EpisodeLog,
    FailureCatalog,
    TaskSpecification,
    ValidationError,
)


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"


def test_reference_configs_validate() -> None:
    task = load_task_specification(CONFIG_DIR / "task-specification.yaml")
    criteria = load_acceptance_criteria(CONFIG_DIR / "acceptance-criteria.yaml")
    catalog = load_failure_catalog(CONFIG_DIR / "failure-codes.yaml")
    assert task.task_id == criteria.task_id
    assert len(catalog.failures) == 13


def test_missing_required_metric_field_is_rejected() -> None:
    raw = yaml.safe_load((CONFIG_DIR / "acceptance-criteria.yaml").read_text(encoding="utf-8"))
    del raw["criteria"][0]["measurement"]
    with pytest.raises(ValidationError, match="missing fields"):
        AcceptanceCriteria.from_mapping(raw)


def test_negative_ratio_threshold_is_rejected() -> None:
    raw = yaml.safe_load((CONFIG_DIR / "acceptance-criteria.yaml").read_text(encoding="utf-8"))
    raw["criteria"][0]["threshold"] = -0.1
    with pytest.raises(ValidationError, match=r"\[0, 1\]"):
        AcceptanceCriteria.from_mapping(raw)


def test_unknown_failure_code_is_rejected() -> None:
    raw = yaml.safe_load((CONFIG_DIR / "failure-codes.yaml").read_text(encoding="utf-8"))
    raw["failures"][0]["code"] = "UNKNOWN_FAILURE"
    with pytest.raises(ValidationError, match="not a registered FailureCode"):
        FailureCatalog.from_mapping(raw)


def test_episode_without_seed_is_rejected() -> None:
    line = json.loads((CONFIG_DIR / "sample-episodes.jsonl").read_text(encoding="utf-8").splitlines()[0])
    del line["seed"]
    with pytest.raises(ValidationError, match="missing fields: seed"):
        EpisodeLog.from_mapping(line)


def test_invalid_task_timeout_is_rejected() -> None:
    raw = yaml.safe_load((CONFIG_DIR / "task-specification.yaml").read_text(encoding="utf-8"))
    raw["timeout_s"] = 1.0
    with pytest.raises(ValidationError, match="max_episode_steps / control_frequency_hz"):
        TaskSpecification.from_mapping(raw)


def test_summary_and_acceptance_report() -> None:
    episodes = load_episode_logs_jsonl(CONFIG_DIR / "sample-episodes.jsonl")
    criteria = load_acceptance_criteria(CONFIG_DIR / "acceptance-criteria.yaml")
    summary = summarize_episode_logs(episodes)
    report = evaluate_acceptance(summary, criteria)
    assert summary["episodes"] == 3
    assert summary["failure_counts"] == {"INSERTION_JAMMED": 1}
    assert report["task_id"] == criteria.task_id
    assert report["passed"] is False
    assert {item["status"] for item in report["criteria"]} == {"insufficient_samples"}
