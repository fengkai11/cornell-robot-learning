from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .models import (
    AcceptanceCriteria,
    EpisodeLog,
    FailureCatalog,
    TaskSpecification,
    ValidationError,
)


def _load_yaml(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    try:
        raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValidationError(f"invalid YAML in {file_path}: {exc}") from exc
    if raw is None:
        raise ValidationError(f"YAML file is empty: {file_path}")
    if not isinstance(raw, dict):
        raise ValidationError(f"YAML root must be a mapping: {file_path}")
    return raw


def load_task_specification(path: str | Path) -> TaskSpecification:
    return TaskSpecification.from_mapping(_load_yaml(path))


def load_acceptance_criteria(path: str | Path) -> AcceptanceCriteria:
    return AcceptanceCriteria.from_mapping(_load_yaml(path))


def load_failure_catalog(path: str | Path) -> FailureCatalog:
    return FailureCatalog.from_mapping(_load_yaml(path))


def load_episode_logs_jsonl(path: str | Path) -> list[EpisodeLog]:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    episodes: list[EpisodeLog] = []
    for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"invalid JSON at {file_path}:{line_number}: {exc}") from exc
        try:
            episodes.append(EpisodeLog.from_mapping(raw))
        except ValidationError as exc:
            raise ValidationError(f"invalid episode at {file_path}:{line_number}: {exc}") from exc
    if not episodes:
        raise ValidationError(f"no episode logs found in {file_path}")
    ids = [episode.episode_id for episode in episodes]
    if len(ids) != len(set(ids)):
        raise ValidationError("episode_id values must be unique")
    return episodes
