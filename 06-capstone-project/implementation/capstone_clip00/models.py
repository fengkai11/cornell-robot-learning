from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class ValidationError(ValueError):
    """Raised when a Clip 00 configuration or log violates its schema."""


class FailureCode(str, Enum):
    PERCEPTION_TARGET_MISSING = "PERCEPTION_TARGET_MISSING"
    PERCEPTION_POSE_ERROR = "PERCEPTION_POSE_ERROR"
    PLANNING_UNREACHABLE = "PLANNING_UNREACHABLE"
    APPROACH_COLLISION = "APPROACH_COLLISION"
    ALIGNMENT_OUT_OF_TOLERANCE = "ALIGNMENT_OUT_OF_TOLERANCE"
    CONTACT_FORCE_EXCEEDED = "CONTACT_FORCE_EXCEEDED"
    INSERTION_NO_PROGRESS = "INSERTION_NO_PROGRESS"
    INSERTION_JAMMED = "INSERTION_JAMMED"
    OBJECT_DROPPED = "OBJECT_DROPPED"
    POLICY_OSCILLATION = "POLICY_OSCILLATION"
    TIMEOUT = "TIMEOUT"
    RECOVERY_FAILED = "RECOVERY_FAILED"
    SAFETY_WORKSPACE_VIOLATION = "SAFETY_WORKSPACE_VIOLATION"


class ObservationSource(str, Enum):
    DIRECTLY_MEASURED = "directly_measured"
    ESTIMATED = "estimated"
    PRIVILEGED_SIMULATION = "privileged_simulation"
    CURRENTLY_UNAVAILABLE = "currently_unavailable"


class Severity(str, Enum):
    INFO = "info"
    RECOVERABLE = "recoverable"
    STOP_REQUIRED = "stop_required"
    DANGEROUS = "dangerous"


_ALLOWED_COMPARATORS = {">=", "<=", "=="}
_ALLOWED_ACTIONS = {"retry", "retreat", "stop", "human_intervention", "none"}


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{name} must be a mapping, got {type(value).__name__}")
    return value


def _require_sequence(value: Any, name: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValidationError(f"{name} must be a sequence")
    return value


def _require_non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")
    return value.strip()


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValidationError(f"{name} must be finite")
    return number


def _positive(value: Any, name: str, *, allow_zero: bool = False) -> float:
    number = _finite_number(value, name)
    if allow_zero:
        if number < 0:
            raise ValidationError(f"{name} must be >= 0")
    elif number <= 0:
        raise ValidationError(f"{name} must be > 0")
    return number


def _integer(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{name} must be >= {minimum}")
    return value


def _reject_unknown_fields(data: Mapping[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValidationError(f"{name} has unknown fields: {', '.join(unknown)}")


@dataclass(frozen=True)
class NumericRange:
    minimum: float
    maximum: float

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any], name: str) -> "NumericRange":
        data = _require_mapping(data, name)
        _reject_unknown_fields(data, {"min", "max"}, name)
        minimum = _finite_number(data.get("min"), f"{name}.min")
        maximum = _finite_number(data.get("max"), f"{name}.max")
        if minimum > maximum:
            raise ValidationError(f"{name}.min must be <= {name}.max")
        return cls(minimum=minimum, maximum=maximum)


@dataclass(frozen=True)
class ObservationDefinition:
    name: str
    source: ObservationSource
    unit: str
    description: str
    required_for_clip01: bool

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any], index: int) -> "ObservationDefinition":
        name = f"observations[{index}]"
        data = _require_mapping(data, name)
        _reject_unknown_fields(
            data,
            {"name", "source", "unit", "description", "required_for_clip01"},
            name,
        )
        try:
            source = ObservationSource(_require_non_empty_string(data.get("source"), f"{name}.source"))
        except ValueError as exc:
            allowed = ", ".join(item.value for item in ObservationSource)
            raise ValidationError(f"{name}.source must be one of: {allowed}") from exc
        required = data.get("required_for_clip01")
        if not isinstance(required, bool):
            raise ValidationError(f"{name}.required_for_clip01 must be boolean")
        return cls(
            name=_require_non_empty_string(data.get("name"), f"{name}.name"),
            source=source,
            unit=_require_non_empty_string(data.get("unit"), f"{name}.unit"),
            description=_require_non_empty_string(data.get("description"), f"{name}.description"),
            required_for_clip01=required,
        )


@dataclass(frozen=True)
class TaskSpecification:
    schema_version: str
    task_id: str
    description: str
    object_type: str
    target_type: str
    action_mode: str
    observation_mode: str
    control_frequency_hz: float
    max_episode_steps: int
    timeout_s: float
    max_retries: int
    success_position_tolerance_mm: float
    success_orientation_tolerance_deg: float
    max_contact_force_n: float
    workspace_bounds_m: dict[str, NumericRange]
    position_perturbation_mm: float
    orientation_perturbation_deg: float
    observations: tuple[ObservationDefinition, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "TaskSpecification":
        data = _require_mapping(raw, "task specification")
        allowed = {
            "schema_version",
            "task_id",
            "description",
            "object_type",
            "target_type",
            "action_mode",
            "observation_mode",
            "control_frequency_hz",
            "max_episode_steps",
            "timeout_s",
            "max_retries",
            "success_position_tolerance_mm",
            "success_orientation_tolerance_deg",
            "max_contact_force_n",
            "workspace_bounds_m",
            "position_perturbation_mm",
            "orientation_perturbation_deg",
            "observations",
        }
        _reject_unknown_fields(data, allowed, "task specification")
        missing = sorted(field for field in allowed if field not in data)
        if missing:
            raise ValidationError(f"task specification missing fields: {', '.join(missing)}")

        bounds_raw = _require_mapping(data["workspace_bounds_m"], "workspace_bounds_m")
        if set(bounds_raw) != {"x", "y", "z"}:
            raise ValidationError("workspace_bounds_m must contain exactly x, y, z")
        bounds = {
            axis: NumericRange.from_mapping(bounds_raw[axis], f"workspace_bounds_m.{axis}")
            for axis in ("x", "y", "z")
        }

        observations_raw = _require_sequence(data["observations"], "observations")
        observations = tuple(
            ObservationDefinition.from_mapping(item, index)
            for index, item in enumerate(observations_raw)
        )
        if not observations:
            raise ValidationError("observations must not be empty")
        names = [item.name for item in observations]
        if len(names) != len(set(names)):
            raise ValidationError("observation names must be unique")

        timeout_s = _positive(data["timeout_s"], "timeout_s")
        control_frequency_hz = _positive(data["control_frequency_hz"], "control_frequency_hz")
        max_episode_steps = _integer(data["max_episode_steps"], "max_episode_steps", minimum=1)
        implied_timeout = max_episode_steps / control_frequency_hz
        if timeout_s + 1e-9 < implied_timeout:
            raise ValidationError(
                "timeout_s must be at least max_episode_steps / control_frequency_hz "
                f"({implied_timeout:.3f}s)"
            )

        return cls(
            schema_version=_require_non_empty_string(data["schema_version"], "schema_version"),
            task_id=_require_non_empty_string(data["task_id"], "task_id"),
            description=_require_non_empty_string(data["description"], "description"),
            object_type=_require_non_empty_string(data["object_type"], "object_type"),
            target_type=_require_non_empty_string(data["target_type"], "target_type"),
            action_mode=_require_non_empty_string(data["action_mode"], "action_mode"),
            observation_mode=_require_non_empty_string(data["observation_mode"], "observation_mode"),
            control_frequency_hz=control_frequency_hz,
            max_episode_steps=max_episode_steps,
            timeout_s=timeout_s,
            max_retries=_integer(data["max_retries"], "max_retries", minimum=0),
            success_position_tolerance_mm=_positive(
                data["success_position_tolerance_mm"], "success_position_tolerance_mm"
            ),
            success_orientation_tolerance_deg=_positive(
                data["success_orientation_tolerance_deg"], "success_orientation_tolerance_deg"
            ),
            max_contact_force_n=_positive(data["max_contact_force_n"], "max_contact_force_n"),
            workspace_bounds_m=bounds,
            position_perturbation_mm=_positive(
                data["position_perturbation_mm"], "position_perturbation_mm", allow_zero=True
            ),
            orientation_perturbation_deg=_positive(
                data["orientation_perturbation_deg"], "orientation_perturbation_deg", allow_zero=True
            ),
            observations=observations,
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["observations"] = [
            {**asdict(item), "source": item.source.value} for item in self.observations
        ]
        result["workspace_bounds_m"] = {
            axis: {"min": value.minimum, "max": value.maximum}
            for axis, value in self.workspace_bounds_m.items()
        }
        return result


@dataclass(frozen=True)
class MetricCriterion:
    name: str
    comparator: str
    threshold: float
    unit: str
    measurement: str
    sample_count: int
    seeds: tuple[int, ...]
    uses_privileged_truth: bool
    disturbance_scope: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any], index: int) -> "MetricCriterion":
        name = f"criteria[{index}]"
        data = _require_mapping(data, name)
        allowed = {
            "name",
            "comparator",
            "threshold",
            "unit",
            "measurement",
            "sample_count",
            "seeds",
            "uses_privileged_truth",
            "disturbance_scope",
        }
        _reject_unknown_fields(data, allowed, name)
        missing = sorted(field for field in allowed if field not in data)
        if missing:
            raise ValidationError(f"{name} missing fields: {', '.join(missing)}")

        comparator = _require_non_empty_string(data["comparator"], f"{name}.comparator")
        if comparator not in _ALLOWED_COMPARATORS:
            raise ValidationError(f"{name}.comparator must be one of {_ALLOWED_COMPARATORS}")
        unit = _require_non_empty_string(data["unit"], f"{name}.unit")
        threshold = _finite_number(data["threshold"], f"{name}.threshold")
        if unit == "ratio" and not 0.0 <= threshold <= 1.0:
            raise ValidationError(f"{name}.threshold must be in [0, 1] for ratio metrics")
        if unit in {"count", "seconds", "retries"} and threshold < 0:
            raise ValidationError(f"{name}.threshold must be >= 0 for unit {unit}")

        seeds_raw = _require_sequence(data["seeds"], f"{name}.seeds")
        seeds = tuple(_integer(seed, f"{name}.seeds", minimum=0) for seed in seeds_raw)
        if not seeds:
            raise ValidationError(f"{name}.seeds must not be empty")
        if len(seeds) != len(set(seeds)):
            raise ValidationError(f"{name}.seeds must be unique")
        privileged = data["uses_privileged_truth"]
        if not isinstance(privileged, bool):
            raise ValidationError(f"{name}.uses_privileged_truth must be boolean")

        return cls(
            name=_require_non_empty_string(data["name"], f"{name}.name"),
            comparator=comparator,
            threshold=threshold,
            unit=unit,
            measurement=_require_non_empty_string(data["measurement"], f"{name}.measurement"),
            sample_count=_integer(data["sample_count"], f"{name}.sample_count", minimum=1),
            seeds=seeds,
            uses_privileged_truth=privileged,
            disturbance_scope=_require_non_empty_string(
                data["disturbance_scope"], f"{name}.disturbance_scope"
            ),
        )


@dataclass(frozen=True)
class AcceptanceCriteria:
    schema_version: str
    task_id: str
    criteria: tuple[MetricCriterion, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "AcceptanceCriteria":
        data = _require_mapping(raw, "acceptance criteria")
        _reject_unknown_fields(data, {"schema_version", "task_id", "criteria"}, "acceptance criteria")
        for required in ("schema_version", "task_id", "criteria"):
            if required not in data:
                raise ValidationError(f"acceptance criteria missing field: {required}")
        criteria_raw = _require_sequence(data["criteria"], "criteria")
        criteria = tuple(
            MetricCriterion.from_mapping(item, index) for index, item in enumerate(criteria_raw)
        )
        if not criteria:
            raise ValidationError("criteria must not be empty")
        names = [item.name for item in criteria]
        if len(names) != len(set(names)):
            raise ValidationError("criterion names must be unique")
        return cls(
            schema_version=_require_non_empty_string(data["schema_version"], "schema_version"),
            task_id=_require_non_empty_string(data["task_id"], "task_id"),
            criteria=criteria,
        )


@dataclass(frozen=True)
class FailureDefinition:
    code: FailureCode
    category: str
    severity: Severity
    retryable: bool
    default_action: str
    description: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], index: int) -> "FailureDefinition":
        name = f"failures[{index}]"
        data = _require_mapping(raw, name)
        allowed = {"code", "category", "severity", "retryable", "default_action", "description"}
        _reject_unknown_fields(data, allowed, name)
        missing = sorted(field for field in allowed if field not in data)
        if missing:
            raise ValidationError(f"{name} missing fields: {', '.join(missing)}")
        try:
            code = FailureCode(_require_non_empty_string(data["code"], f"{name}.code"))
        except ValueError as exc:
            raise ValidationError(f"{name}.code is not a registered FailureCode") from exc
        try:
            severity = Severity(_require_non_empty_string(data["severity"], f"{name}.severity"))
        except ValueError as exc:
            allowed_severity = ", ".join(item.value for item in Severity)
            raise ValidationError(f"{name}.severity must be one of: {allowed_severity}") from exc
        retryable = data["retryable"]
        if not isinstance(retryable, bool):
            raise ValidationError(f"{name}.retryable must be boolean")
        default_action = _require_non_empty_string(data["default_action"], f"{name}.default_action")
        if default_action not in _ALLOWED_ACTIONS:
            raise ValidationError(f"{name}.default_action must be one of {_ALLOWED_ACTIONS}")
        if severity in {Severity.STOP_REQUIRED, Severity.DANGEROUS} and default_action == "retry":
            raise ValidationError(f"{name}: stop_required/dangerous failures cannot default to retry")
        return cls(
            code=code,
            category=_require_non_empty_string(data["category"], f"{name}.category"),
            severity=severity,
            retryable=retryable,
            default_action=default_action,
            description=_require_non_empty_string(data["description"], f"{name}.description"),
        )


@dataclass(frozen=True)
class FailureCatalog:
    schema_version: str
    failures: tuple[FailureDefinition, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "FailureCatalog":
        data = _require_mapping(raw, "failure catalog")
        _reject_unknown_fields(data, {"schema_version", "failures"}, "failure catalog")
        if "schema_version" not in data or "failures" not in data:
            raise ValidationError("failure catalog requires schema_version and failures")
        failures_raw = _require_sequence(data["failures"], "failures")
        failures = tuple(
            FailureDefinition.from_mapping(item, index) for index, item in enumerate(failures_raw)
        )
        codes = [item.code for item in failures]
        if len(codes) != len(set(codes)):
            raise ValidationError("failure catalog contains duplicate codes")
        missing = sorted(code.value for code in set(FailureCode) - set(codes))
        extra = sorted(code.value for code in set(codes) - set(FailureCode))
        if missing or extra:
            details = []
            if missing:
                details.append(f"missing: {', '.join(missing)}")
            if extra:
                details.append(f"extra: {', '.join(extra)}")
            raise ValidationError("failure catalog must match FailureCode enum (" + "; ".join(details) + ")")
        return cls(
            schema_version=_require_non_empty_string(data["schema_version"], "schema_version"),
            failures=failures,
        )


@dataclass(frozen=True)
class StepRecord:
    step: int
    timestamp_s: float
    observation: dict[str, Any]
    action: list[float]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], index: int) -> "StepRecord":
        name = f"recent_steps[{index}]"
        data = _require_mapping(raw, name)
        _reject_unknown_fields(data, {"step", "timestamp_s", "observation", "action"}, name)
        action_raw = _require_sequence(data.get("action"), f"{name}.action")
        action = [_finite_number(value, f"{name}.action") for value in action_raw]
        observation = dict(_require_mapping(data.get("observation"), f"{name}.observation"))
        return cls(
            step=_integer(data.get("step"), f"{name}.step", minimum=0),
            timestamp_s=_positive(data.get("timestamp_s"), f"{name}.timestamp_s", allow_zero=True),
            observation=observation,
            action=action,
        )


@dataclass(frozen=True)
class EpisodeLog:
    episode_id: str
    seed: int
    success: bool
    failure_code: FailureCode | None
    evaluation_split: str
    environment_parameters: dict[str, Any]
    recent_steps: tuple[StepRecord, ...]
    tcp_trajectory: tuple[tuple[float, ...], ...]
    contact_force_n: tuple[float, ...]
    retries: int
    duration_s: float
    screenshot_or_video_index: str | None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "EpisodeLog":
        data = _require_mapping(raw, "episode log")
        allowed = {
            "episode_id",
            "seed",
            "success",
            "failure_code",
            "evaluation_split",
            "environment_parameters",
            "recent_steps",
            "tcp_trajectory",
            "contact_force_n",
            "retries",
            "duration_s",
            "screenshot_or_video_index",
            "metadata",
        }
        _reject_unknown_fields(data, allowed, "episode log")
        required = allowed - {"failure_code", "screenshot_or_video_index", "metadata"}
        missing = sorted(field for field in required if field not in data)
        if missing:
            raise ValidationError(f"episode log missing fields: {', '.join(missing)}")

        success = data["success"]
        if not isinstance(success, bool):
            raise ValidationError("episode log success must be boolean")
        raw_failure = data.get("failure_code")
        failure: FailureCode | None
        if raw_failure is None:
            failure = None
        else:
            try:
                failure = FailureCode(_require_non_empty_string(raw_failure, "failure_code"))
            except ValueError as exc:
                raise ValidationError("episode log contains an unregistered failure_code") from exc
        if success and failure is not None:
            raise ValidationError("successful episode must not contain failure_code")
        if not success and failure is None:
            raise ValidationError("failed episode must contain failure_code")

        steps_raw = _require_sequence(data["recent_steps"], "recent_steps")
        steps = tuple(StepRecord.from_mapping(item, index) for index, item in enumerate(steps_raw))
        trajectory_raw = _require_sequence(data["tcp_trajectory"], "tcp_trajectory")
        trajectory: list[tuple[float, ...]] = []
        for index, pose in enumerate(trajectory_raw):
            pose_values = tuple(
                _finite_number(value, f"tcp_trajectory[{index}]")
                for value in _require_sequence(pose, f"tcp_trajectory[{index}]")
            )
            if len(pose_values) not in {3, 7}:
                raise ValidationError("each tcp_trajectory pose must have 3 or 7 values")
            trajectory.append(pose_values)
        forces = tuple(
            _positive(value, "contact_force_n", allow_zero=True)
            for value in _require_sequence(data["contact_force_n"], "contact_force_n")
        )
        screenshot = data.get("screenshot_or_video_index")
        if screenshot is not None:
            screenshot = _require_non_empty_string(screenshot, "screenshot_or_video_index")
        metadata = dict(_require_mapping(data.get("metadata", {}), "metadata"))

        return cls(
            episode_id=_require_non_empty_string(data["episode_id"], "episode_id"),
            seed=_integer(data["seed"], "seed", minimum=0),
            success=success,
            failure_code=failure,
            evaluation_split=_require_non_empty_string(data["evaluation_split"], "evaluation_split"),
            environment_parameters=dict(
                _require_mapping(data["environment_parameters"], "environment_parameters")
            ),
            recent_steps=steps,
            tcp_trajectory=tuple(trajectory),
            contact_force_n=forces,
            retries=_integer(data["retries"], "retries", minimum=0),
            duration_s=_positive(data["duration_s"], "duration_s", allow_zero=True),
            screenshot_or_video_index=screenshot,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "seed": self.seed,
            "success": self.success,
            "failure_code": self.failure_code.value if self.failure_code else None,
            "evaluation_split": self.evaluation_split,
            "environment_parameters": self.environment_parameters,
            "recent_steps": [asdict(item) for item in self.recent_steps],
            "tcp_trajectory": [list(item) for item in self.tcp_trajectory],
            "contact_force_n": list(self.contact_force_n),
            "retries": self.retries,
            "duration_s": self.duration_s,
            "screenshot_or_video_index": self.screenshot_or_video_index,
            "metadata": self.metadata,
        }
