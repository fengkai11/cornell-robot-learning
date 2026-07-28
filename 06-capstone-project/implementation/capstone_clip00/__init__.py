"""Clip 00 application-definition toolkit.

This package intentionally contains no ManiSkill environment or learning code.
It defines the contracts that later clips must obey.
"""

from .evaluation import evaluate_acceptance, summarize_episode_logs
from .io import (
    load_acceptance_criteria,
    load_episode_logs_jsonl,
    load_failure_catalog,
    load_task_specification,
)
from .models import (
    AcceptanceCriteria,
    EpisodeLog,
    FailureCatalog,
    FailureCode,
    TaskSpecification,
    ValidationError,
)

__all__ = [
    "AcceptanceCriteria",
    "EpisodeLog",
    "FailureCatalog",
    "FailureCode",
    "TaskSpecification",
    "ValidationError",
    "evaluate_acceptance",
    "load_acceptance_criteria",
    "load_episode_logs_jsonl",
    "load_failure_catalog",
    "load_task_specification",
    "summarize_episode_logs",
]
