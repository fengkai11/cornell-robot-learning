from __future__ import annotations

import math
from collections import Counter, defaultdict
from statistics import fmean
from typing import Any, Iterable

from .models import AcceptanceCriteria, EpisodeLog, FailureCode, MetricCriterion


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float] | None:
    if total == 0:
        return None
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def _split_success_rate(episodes: list[EpisodeLog], split: str) -> dict[str, Any]:
    selected = [episode for episode in episodes if episode.evaluation_split == split]
    successes = sum(episode.success for episode in selected)
    interval = _wilson_interval(successes, len(selected))
    return {
        "episodes": len(selected),
        "successes": successes,
        "value": _safe_ratio(successes, len(selected)),
        "wilson_95": list(interval) if interval else None,
    }


def summarize_episode_logs(episodes: Iterable[EpisodeLog]) -> dict[str, Any]:
    episode_list = list(episodes)
    total = len(episode_list)
    successes = sum(episode.success for episode in episode_list)
    failures = [episode for episode in episode_list if not episode.success]
    failure_counts = Counter(
        episode.failure_code.value for episode in failures if episode.failure_code is not None
    )

    per_seed: dict[int, list[EpisodeLog]] = defaultdict(list)
    for episode in episode_list:
        per_seed[episode.seed].append(episode)

    jam_truth = [episode for episode in episode_list if episode.metadata.get("ground_truth_jammed") is True]
    jam_detected = sum(episode.metadata.get("detected_jammed") is True for episode in jam_truth)
    recovery_attempts = [
        episode for episode in episode_list if episode.metadata.get("jam_recovery_attempted") is True
    ]
    recovery_successes = sum(
        episode.metadata.get("jam_recovery_succeeded") is True for episode in recovery_attempts
    )
    dangerous_codes = {
        FailureCode.CONTACT_FORCE_EXCEEDED,
        FailureCode.SAFETY_WORKSPACE_VIOLATION,
    }
    dangerous_events = sum(
        episode.metadata.get("dangerous_event") is True
        or episode.failure_code in dangerous_codes
        for episode in episode_list
    )
    diagnosed_failures = sum(episode.failure_code is not None for episode in failures)

    splits = sorted({episode.evaluation_split for episode in episode_list})
    return {
        "episodes": total,
        "successes": successes,
        "failed_episodes": len(failures),
        "success_rate": _safe_ratio(successes, total),
        "success_rate_wilson_95": list(_wilson_interval(successes, total)) if total else None,
        "mean_retries": fmean(episode.retries for episode in episode_list) if total else None,
        "mean_duration_s": fmean(episode.duration_s for episode in episode_list) if total else None,
        "dangerous_event_count": dangerous_events,
        "failure_diagnostic_coverage": _safe_ratio(diagnosed_failures, len(failures)),
        "failure_counts": dict(sorted(failure_counts.items())),
        "per_seed": {
            str(seed): {
                "episodes": len(items),
                "success_rate": _safe_ratio(sum(item.success for item in items), len(items)),
            }
            for seed, items in sorted(per_seed.items())
        },
        "split_metrics": {split: _split_success_rate(episode_list, split) for split in splits},
        "jam_detection_recall": _safe_ratio(jam_detected, len(jam_truth)),
        "jam_detection_samples": len(jam_truth),
        "jam_recovery_success_rate": _safe_ratio(recovery_successes, len(recovery_attempts)),
        "jam_recovery_samples": len(recovery_attempts),
    }


def _metric_value_and_samples(summary: dict[str, Any], name: str) -> tuple[float | int | None, int]:
    split_metrics = summary.get("split_metrics", {})
    mapping: dict[str, tuple[Any, int]] = {
        "normal_distribution_success_rate": (
            split_metrics.get("normal", {}).get("value"),
            int(split_metrics.get("normal", {}).get("episodes", 0)),
        ),
        "mild_position_perturbation_success_rate": (
            split_metrics.get("mild_position_perturbation", {}).get("value"),
            int(split_metrics.get("mild_position_perturbation", {}).get("episodes", 0)),
        ),
        "jam_detection_recall": (
            summary.get("jam_detection_recall"),
            int(summary.get("jam_detection_samples", 0)),
        ),
        "jam_recovery_success_rate": (
            summary.get("jam_recovery_success_rate"),
            int(summary.get("jam_recovery_samples", 0)),
        ),
        "dangerous_event_count": (
            summary.get("dangerous_event_count"),
            int(summary.get("episodes", 0)),
        ),
        "mean_retries": (summary.get("mean_retries"), int(summary.get("episodes", 0))),
        "failure_diagnostic_coverage": (
            summary.get("failure_diagnostic_coverage"),
            int(summary.get("failed_episodes", 0)),
        ),
    }
    return mapping.get(name, (None, 0))


def _compare(value: float | int, criterion: MetricCriterion) -> bool:
    if criterion.comparator == ">=":
        return value >= criterion.threshold
    if criterion.comparator == "<=":
        return value <= criterion.threshold
    return value == criterion.threshold


def evaluate_acceptance(summary: dict[str, Any], criteria: AcceptanceCriteria) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    all_metrics_evaluated = True
    all_evaluated_passed = True
    for criterion in criteria.criteria:
        value, actual_samples = _metric_value_and_samples(summary, criterion.name)
        if value is None:
            status = "not_evaluated"
            passed = None
            all_metrics_evaluated = False
        elif actual_samples < criterion.sample_count:
            status = "insufficient_samples"
            passed = None
            all_metrics_evaluated = False
        else:
            passed = _compare(value, criterion)
            status = "passed" if passed else "failed"
            if not passed:
                all_evaluated_passed = False
        results.append(
            {
                "name": criterion.name,
                "value": value,
                "comparator": criterion.comparator,
                "threshold": criterion.threshold,
                "unit": criterion.unit,
                "status": status,
                "sample_count_actual": actual_samples,
                "sample_count_required": criterion.sample_count,
            }
        )
    return {
        "task_id": criteria.task_id,
        "all_metrics_evaluated": all_metrics_evaluated,
        "passed": all_metrics_evaluated and all_evaluated_passed,
        "criteria": results,
    }
