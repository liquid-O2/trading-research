"""Explicit purpose and primary research-period admission contracts.

The historical research modules deliberately keep their legacy wire and hash
schemas.  A primary caller supplies a :class:`ResearchScopeV1` and, where a
complete retained population exists, a :class:`PrimaryAdmissionV1`.  Omitting
the scope keeps the old diagnostic behavior and can never confer primary
eligibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Iterable

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


PRIMARY_SCOPE = "primary_model"
DIAGNOSTIC_SCOPE = "diagnostic"
JUMBO_OPTIONAL_SCOPE = "jumbo_optional"
OHLC_OPTIONAL_SCOPE = "ohlc_optional"
PURPOSE_SCOPES = frozenset({PRIMARY_SCOPE, DIAGNOSTIC_SCOPE, JUMBO_OPTIONAL_SCOPE, OHLC_OPTIONAL_SCOPE})
PRIMARY_START_DATE = "2020-01-01"
PRIMARY_START_NS_UTC = 1577836800000000000
PRIMARY_END_RULE = "latest_eligible_observation_available_at_the_frozen_evaluation_cut"
OPTIONAL_DATA_USE_DECLARATIONS = (
    "Jumbo source constructions and comparisons",
    "ordinary OHLC context and comparisons",
)


def _identity(value: str, label: str) -> None:
    if type(value) is not str or not value:
        raise ContractError(f"{label} must be a nonempty immutable string")


def _sha256_text(value: str, label: str) -> None:
    if type(value) is not str or len(value) != 64:
        raise ContractError(f"{label} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ContractError(f"{label} must be hexadecimal") from exc


def _policy_body(start_date_inclusive: str, start_ns_utc: int, end_rule: str,
                 pre_period_training_or_evaluation_rows: bool,
                 older_scopes: tuple[str, ...]) -> dict:
    return {
        "kind": "ResearchPeriodPolicyV1",
        "start_date_inclusive": start_date_inclusive,
        "start_ns_utc": start_ns_utc,
        "end_rule": end_rule,
        "pre_period_training_or_evaluation_rows": pre_period_training_or_evaluation_rows,
        "older_scopes": older_scopes,
    }


@dataclass(frozen=True)
class ResearchPeriodPolicyV1:
    """Immutable lower-bound policy loaded from the recorded configuration."""

    start_date_inclusive: str = PRIMARY_START_DATE
    start_ns_utc: int = PRIMARY_START_NS_UTC
    end_rule: str = PRIMARY_END_RULE
    pre_period_training_or_evaluation_rows: bool = False
    older_scopes: tuple[str, ...] = (JUMBO_OPTIONAL_SCOPE, OHLC_OPTIONAL_SCOPE)
    config_hash: str = ""

    def __post_init__(self) -> None:
        if type(self.start_date_inclusive) is not str or self.start_date_inclusive != PRIMARY_START_DATE \
                or type(self.start_ns_utc) is not int or self.start_ns_utc != PRIMARY_START_NS_UTC:
            raise ContractError("primary period policy must begin at the frozen 2020-01-01 boundary")
        if type(self.end_rule) is not str or self.end_rule != PRIMARY_END_RULE \
                or type(self.pre_period_training_or_evaluation_rows) is not bool \
                or self.pre_period_training_or_evaluation_rows is not False:
            raise ContractError("primary period policy has an unregistered end or pre-period rule")
        if (type(self.older_scopes) is not tuple
                or self.older_scopes != (JUMBO_OPTIONAL_SCOPE, OHLC_OPTIONAL_SCOPE)):
            raise ContractError("older research scopes must remain the two registered optional purposes")
        timestamp(self.start_ns_utc)
        try:
            date.fromisoformat(self.start_date_inclusive)
        except (TypeError, ValueError) as exc:
            raise ContractError("research period start date must be ISO calendar text") from exc
        if self.config_hash:
            _sha256_text(self.config_hash, "research period config hash")
        else:
            body = _policy_body(self.start_date_inclusive, self.start_ns_utc, self.end_rule,
                                self.pre_period_training_or_evaluation_rows, self.older_scopes)
            object.__setattr__(self, "config_hash", digest(body))

    @property
    def policy_hash(self) -> str:
        return self.config_hash

    @classmethod
    def from_config(cls, path: Path | str = "configs/research-period.json") -> "ResearchPeriodPolicyV1":
        """Load and validate the exact frozen configuration and retain its byte hash."""
        if not isinstance(path, (Path, str)):
            raise ContractError("research period configuration path must be text or Path")
        path = Path(path)
        try:
            raw = path.read_bytes()
            body = json.loads(raw)
        except (OSError, ValueError, TypeError, UnicodeError) as exc:
            raise ContractError("research period configuration is unavailable or invalid") from exc
        if type(body) is not dict or body.get("kind") != "ResearchPeriodPolicyV1":
            raise ContractError("research period configuration kind is not registered")
        primary = body.get("primary_model")
        optional = body.get("older_data_optional_uses")
        if type(primary) is not dict or type(optional) is not list:
            raise ContractError("research period configuration lacks primary or optional scope declarations")
        if (primary.get("start_date_inclusive") != PRIMARY_START_DATE
                or primary.get("end") != PRIMARY_END_RULE
                or primary.get("pre_2020_training_or_evaluation_rows") is not False):
            raise ContractError("research period configuration disagrees with the frozen primary policy")
        result = cls(start_date_inclusive=primary["start_date_inclusive"],
                     start_ns_utc=PRIMARY_START_NS_UTC,
                     end_rule=primary["end"],
                     pre_period_training_or_evaluation_rows=primary["pre_2020_training_or_evaluation_rows"],
                     older_scopes=(JUMBO_OPTIONAL_SCOPE, OHLC_OPTIONAL_SCOPE),
                     config_hash=hashlib.sha256(raw).hexdigest())
        if tuple(optional) != OPTIONAL_DATA_USE_DECLARATIONS:
            raise ContractError("research period configuration optional uses differ from the frozen declarations")
        return result

    @classmethod
    def load(cls, path: Path | str = "configs/research-period.json") -> "ResearchPeriodPolicyV1":
        return cls.from_config(path)

    @classmethod
    def default(cls) -> "ResearchPeriodPolicyV1":
        return cls()

    def check_timestamp(self, value: int, *, code: str = "pre_period_observation") -> int:
        timestamp(value)
        if value < self.start_ns_utc:
            raise ContractError(code)
        return value


@dataclass(frozen=True)
class ResearchScopeV1:
    """Immutable purpose/cohort/denominator binding for one research use."""

    purpose_scope: str
    cohort_id: str
    denominator_id: str
    policy_hash: str | None = None

    def __post_init__(self) -> None:
        if type(self.purpose_scope) is not str or self.purpose_scope not in PURPOSE_SCOPES:
            raise ContractError("unregistered research purpose scope")
        _identity(self.cohort_id, "cohort_id")
        _identity(self.denominator_id, "denominator_id")
        if self.purpose_scope == PRIMARY_SCOPE:
            _sha256_text(self.policy_hash, "primary scope policy hash")
        elif self.policy_hash is not None:
            _sha256_text(self.policy_hash, "optional scope policy hash")

    @classmethod
    def primary(cls, *, cohort_id: str, denominator_id: str,
                policy: ResearchPeriodPolicyV1) -> "ResearchScopeV1":
        if type(policy) is not ResearchPeriodPolicyV1:
            raise ContractError("primary scope requires a typed ResearchPeriodPolicyV1")
        return cls(PRIMARY_SCOPE, cohort_id, denominator_id, policy.config_hash)

    @classmethod
    def diagnostic(cls, *, cohort_id: str, denominator_id: str,
                   policy: ResearchPeriodPolicyV1 | None = None) -> "ResearchScopeV1":
        if policy is not None and type(policy) is not ResearchPeriodPolicyV1:
            raise ContractError("diagnostic scope policy must be typed when supplied")
        return cls(DIAGNOSTIC_SCOPE, cohort_id, denominator_id,
                   None if policy is None else policy.config_hash)

    @classmethod
    def jumbo_optional(cls, *, cohort_id: str, denominator_id: str,
                       policy: ResearchPeriodPolicyV1 | None = None) -> "ResearchScopeV1":
        if policy is not None and type(policy) is not ResearchPeriodPolicyV1:
            raise ContractError("Jumbo optional scope policy must be typed when supplied")
        return cls(JUMBO_OPTIONAL_SCOPE, cohort_id, denominator_id,
                   None if policy is None else policy.config_hash)

    @classmethod
    def ohlc_optional(cls, *, cohort_id: str, denominator_id: str,
                      policy: ResearchPeriodPolicyV1 | None = None) -> "ResearchScopeV1":
        if policy is not None and type(policy) is not ResearchPeriodPolicyV1:
            raise ContractError("OHLC optional scope policy must be typed when supplied")
        return cls(OHLC_OPTIONAL_SCOPE, cohort_id, denominator_id,
                   None if policy is None else policy.config_hash)

    @property
    def is_primary(self) -> bool:
        return self.purpose_scope == PRIMARY_SCOPE


PurposeScopeV1 = ResearchScopeV1


def canonical_primary_population(population: Iterable) -> tuple:
    """Use the existing fold wire order for typed samples, never deduplicating.

    Non-sample envelopes (cohort evidence and protocol manifests) retain their
    original wire order. Imports are local because fold declarations use this
    module for their optional primary admission layer.
    """
    from trading_research.research.folds import Sample
    from trading_research.research.temporal_folds import TemporalSampleV1
    rows = tuple(population)
    if any(type(row) in (Sample, TemporalSampleV1) for row in rows):
        if not all(type(row) is type(rows[0]) and type(row) in (Sample, TemporalSampleV1)
                   for row in rows):
            raise ContractError("primary sample population must have one exact typed sample schema")
        if len({row.id for row in rows}) != len(rows):
            raise ContractError("duplicate sample identity")
        return tuple(sorted(rows, key=lambda row: (row.decision_at, row.id)))
    return rows


@dataclass(frozen=True)
class PrimaryAdmissionV1:
    """Immutable binding of a primary scope to one complete population and cut."""

    scope: ResearchScopeV1
    population_hash: str
    actual_cut_at: int

    def __post_init__(self) -> None:
        if type(self.scope) is not ResearchScopeV1 or not self.scope.is_primary:
            raise ContractError("primary admission requires the explicit primary scope")
        if type(self.population_hash) is not str or len(self.population_hash) != 64:
            raise ContractError("primary admission requires a complete population SHA-256")
        try:
            int(self.population_hash, 16)
        except ValueError as exc:
            raise ContractError("primary population hash must be hexadecimal") from exc
        timestamp(self.actual_cut_at)

    @classmethod
    def from_population(cls, population: Iterable, *, scope: ResearchScopeV1,
                        policy: ResearchPeriodPolicyV1, actual_cut_at: int) -> "PrimaryAdmissionV1":
        require_primary_scope(scope, policy)
        validate_primary_cut(actual_cut_at, policy)
        rows = canonical_primary_population(population)
        return cls(scope, digest(rows), timestamp(actual_cut_at))

    def validate_population(self, population: Iterable, *, policy: ResearchPeriodPolicyV1) -> tuple:
        require_primary_scope(self.scope, policy)
        rows = canonical_primary_population(population)
        if digest(rows) != self.population_hash:
            raise IntegrityError("primary retained population differs from its immutable admission hash")
        return rows


PrimaryPopulationAdmissionV1 = PrimaryAdmissionV1
PopulationAdmissionV1 = PrimaryAdmissionV1


def validate_scope(scope: ResearchScopeV1 | None, policy: ResearchPeriodPolicyV1 | None = None,
                   *, require_primary: bool = False) -> ResearchScopeV1 | None:
    """Validate an optional scope without changing legacy omitted-scope behavior."""
    if scope is None:
        if require_primary:
            raise ContractError("explicit primary research scope is required")
        return None
    if type(scope) is not ResearchScopeV1:
        raise ContractError("typed ResearchScopeV1 is required")
    if policy is not None and type(policy) is not ResearchPeriodPolicyV1:
        raise ContractError("research scope policy must be typed when supplied")
    if scope.is_primary:
        if type(policy) is not ResearchPeriodPolicyV1:
            raise ContractError("primary scope requires a typed research-period policy")
        if scope.policy_hash != policy.config_hash:
            raise IntegrityError("research scope policy hash differs from the loaded policy")
    elif require_primary:
        raise ContractError("primary research scope is required")
    return scope


def require_primary_scope(scope: ResearchScopeV1 | None,
                          policy: ResearchPeriodPolicyV1 | None) -> ResearchScopeV1:
    result = validate_scope(scope, policy, require_primary=True)
    assert result is not None
    return result


def validate_primary_cut(actual_cut_at: int, policy: ResearchPeriodPolicyV1) -> int:
    """Validate the frozen primary cut and its lower policy bound."""
    if type(policy) is not ResearchPeriodPolicyV1:
        raise ContractError("primary frozen cut requires a typed research-period policy")
    cut = timestamp(actual_cut_at)
    if cut < policy.start_ns_utc:
        raise ContractError("primary_cut_before_period")
    return cut


def validate_primary_admission(admission: PrimaryAdmissionV1 | None, population: Iterable,
                               *, scope: ResearchScopeV1,
                               policy: ResearchPeriodPolicyV1) -> tuple:
    """Require and verify the complete retained population for a primary consumer."""
    require_primary_scope(scope, policy)
    if type(admission) is not PrimaryAdmissionV1:
        raise ContractError("primary consumers require an immutable population admission envelope")
    if admission.scope != scope:
        raise IntegrityError("primary population admission scope differs from its consumer scope")
    validate_primary_cut(admission.actual_cut_at, policy)
    return admission.validate_population(population, policy=policy)


def validate_consumer_admission_shape(*, scope: ResearchScopeV1 | None,
                                      policy: ResearchPeriodPolicyV1 | None,
                                      admission: PrimaryAdmissionV1 | None) -> int | None:
    """Validate admission identity before a consumer reads its cut clock."""
    validate_scope(scope, policy)
    if admission is None:
        return None
    if type(admission) is not PrimaryAdmissionV1:
        raise ContractError("population admission envelope must be typed")
    if scope is None:
        raise ContractError("population admission envelope needs an explicit research scope")
    if not scope.is_primary:
        raise ContractError("population admission envelope is only valid for an explicit primary scope")
    return validate_primary_cut(admission.actual_cut_at, policy)  # type: ignore[arg-type]


def validate_consumer_admission(population: Iterable, *, scope: ResearchScopeV1 | None,
                                policy: ResearchPeriodPolicyV1 | None,
                                admission: PrimaryAdmissionV1 | None) -> tuple:
    """Require exactly the admission envelope allowed by an explicit consumer scope."""
    rows = tuple(population)
    validate_consumer_admission_shape(scope=scope, policy=policy, admission=admission)
    if scope is None:
        if admission is not None:
            raise ContractError("population admission envelope needs an explicit research scope")
        return rows
    if scope.is_primary:
        return validate_primary_admission(admission, rows, scope=scope, policy=policy)  # type: ignore[arg-type]
    if admission is not None:
        raise ContractError("population admission envelope is only valid for an explicit primary scope")
    return rows


def check_cohort_bounds(scope: ResearchScopeV1 | None, policy: ResearchPeriodPolicyV1 | None,
                        observation_start: int | None, observation_end: int | None,
                        *, depth: str | None = None, state: str | None = None,
                        frozen_cut_at: int | None = None) -> str:
    """Check a cohort's period extent; source and operation eligibility stay separate."""
    if scope is None:
        return "legacy_scope_unchecked"
    validate_scope(scope, policy)
    if not scope.is_primary:
        return "optional_or_diagnostic_scope"
    assert policy is not None
    if frozen_cut_at is not None:
        validate_primary_cut(frozen_cut_at, policy)
    if observation_start is None or observation_end is None:
        if state in {"missing", "ineligible", "incomplete"}:
            return "no_observed_extent"
        raise ContractError("primary_complete_range_required: primary cohort evidence requires concrete observation bounds and a complete operation-specific window")
    timestamp(observation_start)
    timestamp(observation_end)
    if observation_start < policy.start_ns_utc:
        raise ContractError("pre_period_observation: primary cohort observation_start is before 2020-01-01T00:00:00Z")
    if observation_end < observation_start:
        raise ContractError("observation extent is reversed")
    if frozen_cut_at is not None:
        timestamp(frozen_cut_at)
        if observation_end > frozen_cut_at:
            raise ContractError("future_observation_at_frozen_cut")
    if depth in {"inventory", "metadata", "row_prefix"} and state not in {"missing", "ineligible", "incomplete"}:
        raise ContractError("primary_complete_range_required: primary cohort evidence requires concrete observation bounds and a complete operation-specific window")
    return "period_admissible"


def check_sample_population(scope: ResearchScopeV1 | None, policy: ResearchPeriodPolicyV1 | None,
                            samples: Iterable, *, fit_at: int, evaluation_start: int,
                            evaluation_end: int, training_start: int | None = None,
                            actual_cut_at: int | None = None) -> tuple:
    """Validate primary sample clocks and disallowed historical raw dependencies."""
    rows = tuple(samples)
    if scope is None:
        return rows
    validate_scope(scope, policy)
    if not scope.is_primary:
        return rows
    assert policy is not None
    if actual_cut_at is not None:
        actual_cut_at = validate_primary_cut(actual_cut_at, policy)
    for label, value in (("fit_at", fit_at), ("evaluation_start", evaluation_start), ("evaluation_end", evaluation_end)):
        timestamp(value)
        if value < policy.start_ns_utc:
            raise ContractError("pre_period_training_or_dependency: primary fold population contains a pre-period decision row or a disallowed pre-period raw_past dependency")
        if actual_cut_at is not None and value > actual_cut_at:
            raise ContractError("post_cut_training_or_dependency")
    if training_start is not None:
        timestamp(training_start)
        if training_start < policy.start_ns_utc:
            raise ContractError("pre_period_training_or_dependency: primary fold population contains a pre-period decision row or a disallowed pre-period raw_past dependency")
        if actual_cut_at is not None and training_start > actual_cut_at:
            raise ContractError("post_cut_training_or_dependency")
    for sample in rows:
        decision_at = getattr(sample, "decision_at", None)
        if type(decision_at) is not int:
            raise ContractError("primary sample lacks an exact decision_at")
        timestamp(decision_at)
        if decision_at < policy.start_ns_utc:
            raise ContractError("pre_period_training_or_dependency: primary fold population contains a pre-period decision row or a disallowed pre-period raw_past dependency")
        clocks = [decision_at]
        for name in ("target_end", "label_known_at", "dependency_end"):
            if hasattr(sample, name):
                value = getattr(sample, name)
                timestamp(value)
                clocks.append(value)
        dependencies = getattr(sample, "dependencies", ())
        if type(dependencies) is not tuple:
            raise ContractError("primary sample dependencies must be immutable")
        for dependency in dependencies:
            kind = getattr(dependency, "kind", None)
            if type(kind) is not str:
                raise ContractError("primary dependency kind must be immutable text")
            for name in ("start", "end", "known_at"):
                value = getattr(dependency, name, None)
                timestamp(value)
                clocks.append(value)
                if kind == "raw_past" and value < policy.start_ns_utc:
                    raise ContractError("pre_period_training_or_dependency: primary fold population contains a pre-period decision row or a disallowed pre-period raw_past dependency")
        if actual_cut_at is not None and any(value > actual_cut_at for value in clocks):
            raise ContractError("post_cut_training_or_dependency")
    return rows


def check_protocol_dates(scope: ResearchScopeV1 | None, policy: ResearchPeriodPolicyV1 | None,
                         ordered_dates: Iterable[str], *, evaluation_start_at: int,
                         endpoint_at: int, actual_cut_at: int | None = None) -> tuple[str, ...]:
    """Check primary observation dates without constraining pre-period registration or future plans."""
    dates = tuple(ordered_dates)
    if scope is None:
        return dates
    validate_scope(scope, policy)
    if not scope.is_primary:
        return dates
    assert policy is not None
    timestamp(evaluation_start_at)
    timestamp(endpoint_at)
    if evaluation_start_at < policy.start_ns_utc:
        raise ContractError("pre_period_evaluation_date")
    if actual_cut_at is not None:
        validate_primary_cut(actual_cut_at, policy)
    for value in dates:
        if type(value) is not str or not value:
            raise ContractError("primary protocol date must be nonempty ISO text")
        try:
            day = date.fromisoformat(value)
        except ValueError as exc:
            raise ContractError("primary protocol date must be ISO calendar text") from exc
        if day < date.fromisoformat(policy.start_date_inclusive):
            raise ContractError(f"pre_period_evaluation_date: primary protocol ordered_dates contains {value} before {policy.start_date_inclusive}")
    return dates


def primary_admission(population: Iterable, *, scope: ResearchScopeV1,
                      policy: ResearchPeriodPolicyV1, actual_cut_at: int) -> PrimaryAdmissionV1:
    """Named constructor for callers that need a complete primary admission envelope."""
    return PrimaryAdmissionV1.from_population(population, scope=scope, policy=policy,
                                               actual_cut_at=actual_cut_at)
