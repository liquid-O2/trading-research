"""Immutable common messages with explicit identity, geometry and capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from fractions import Fraction
import json
import math

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.time import Clocks, timestamp
from trading_research.foundations.units import Quantity, Ticks, Unit
from trading_research.operations.artifacts import digest


def _json_payload(payload: bytes) -> None:
    if not isinstance(payload, bytes):
        raise ContractError("immutable JSON bytes required")
    def finite_number(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError("nonfinite JSON number")
        return value

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON member")
            result[key] = value
        return result

    try:
        json.loads(payload, parse_float=finite_number, object_pairs_hook=unique_object,
                   parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ContractError("invalid finite JSON payload") from exc


def _unique(values: tuple, name: str) -> None:
    if (not isinstance(values, tuple) or any(not isinstance(v, str) or not v for v in values)
            or len(set(values)) != len(values)):
        raise ContractError(f"{name} must be an immutable sequence without duplicates")


class CoverageState(StrEnum):
    OBSERVED = "observed"
    STALE = "stale"
    MISSING = "missing"
    INELIGIBLE = "ineligible"
    ESTIMATED = "estimated"
    INVALID = "invalid"


@dataclass(frozen=True)
class CoverageMask:
    asset: str
    chain: str | None
    expiry: str | None
    moneyness: str | None
    field: str
    at: int
    state: CoverageState
    reason: str
    observed_at: int | None = None
    source_version: str | None = None

    def __post_init__(self) -> None:
        timestamp(self.at)
        if self.observed_at is not None:
            timestamp(self.observed_at)
        if not isinstance(self.state, CoverageState) or not self.field or not self.reason:
            raise ContractError("explicit field-level coverage and reason required")
        if self.observed_at is not None and self.observed_at > self.at:
            raise ContractError("future source observation in coverage mask")


@dataclass(frozen=True)
class InstrumentKey:
    provider: str
    venue: str
    instrument_id: str
    raw_symbol: str | None
    underlying: str | None
    definition_version: str | None
    expiry_at: int | None = None
    right: str | None = None
    strike: Decimal | None = None
    exercise: str | None = None
    settlement: str | None = None
    corporate_action_version: str | None = None

    def __post_init__(self) -> None:
        if not self.provider or not self.venue or not self.instrument_id:
            raise ContractError("provider, venue and instrument ID required")
        if self.strike is not None and (not isinstance(self.strike, Decimal) or not self.strike.is_finite()):
            raise ContractError("strike requires an exact finite decimal")


@dataclass(frozen=True)
class Band:
    lower: Fraction
    upper: Fraction
    unit: Unit = Unit.TICKS

    def __post_init__(self) -> None:
        if (not isinstance(self.lower, Fraction) or not isinstance(self.upper, Fraction)
                or self.lower > self.upper or not isinstance(self.unit, Unit)):
            raise ContractError("invalid exact band")

    def contains(self, price: Fraction) -> bool:
        return self.lower <= price <= self.upper


@dataclass(frozen=True)
class Geometry:
    physical_support: Band
    contact_region: Band
    estimation_uncertainty: Fraction
    mapping_uncertainty: Fraction
    entry_tolerance: Fraction
    definition_id: str
    source_coordinate: str
    execution_coordinate: str

    def __post_init__(self) -> None:
        if self.physical_support.unit != self.contact_region.unit or not self.definition_id:
            raise ContractError("geometry units or definition mismatch")
        for value in (self.estimation_uncertainty, self.mapping_uncertainty, self.entry_tolerance):
            if not isinstance(value, Fraction) or value < 0:
                raise ContractError("uncertainty and tolerance must be distinct nonnegative quantities")

    @property
    def target_geometry_id(self) -> str:
        return digest({"contact": self.contact_region, "definition": self.definition_id,
                       "coordinate": self.execution_coordinate})


@dataclass(frozen=True)
class Measurement:
    component_id: str
    definition_version: str
    instrument: InstrumentKey
    anchor_id: str
    window_start: int
    window_end: int
    clocks: Clocks
    values: tuple[Quantity, ...]
    sample_count: int
    covered_duration_ns: int
    coverage: tuple[CoverageMask, ...]
    reset_reason: str | None = None

    def __post_init__(self) -> None:
        timestamp(self.window_start)
        timestamp(self.window_end)
        if not isinstance(self.values, tuple) or not isinstance(self.coverage, tuple):
            raise ContractError("measurement values and coverage must be immutable")
        if not self.component_id or not self.definition_version or not self.anchor_id:
            raise ContractError("measurement identity and definition required")
        if self.window_end < self.window_start or self.clocks.known_at < self.window_end:
            raise ContractError("measurement window is invalid or not yet observed")
        if (type(self.sample_count) is not int or self.sample_count < 0
                or type(self.covered_duration_ns) is not int
                or not 0 <= self.covered_duration_ns <= self.window_end - self.window_start):
            raise ContractError("invalid sample count/covered duration")


@dataclass(frozen=True)
class MarketObject:
    id: str
    revision: int
    generator: str
    parameter_version: str
    instrument: InstrumentKey
    geometry: Geometry
    clocks: Clocks
    parent_ids: tuple[str, ...]
    source_event_ids: tuple[str, ...]
    anchor_start: int
    anchor_end: int
    confirmed_at: int
    eligibility: str
    visit_state: str
    evidence_state: str
    role_candidates: tuple[str, ...]
    supersedes: str | None = None

    def __post_init__(self) -> None:
        for at in (self.anchor_start, self.anchor_end, self.confirmed_at):
            timestamp(at)
        if (not self.id or not self.generator or not self.parameter_version
                or type(self.revision) is not int or self.revision < 0):
            raise ContractError("invalid object identity/version")
        if self.anchor_end < self.anchor_start or self.confirmed_at < self.anchor_end:
            raise ContractError("object confirmation precedes its formation")
        if self.clocks.known_at < self.confirmed_at:
            raise ContractError("object was backdated before confirmation")
        _unique(self.source_event_ids, "source events")
        _unique(self.parent_ids, "parents")
        _unique(self.role_candidates, "object roles")

    @property
    def version_id(self) -> str:
        return digest(self)


class Capability(StrEnum):
    REALIZED_VARIATION = "realized_variation"
    TERMINAL_VARIANCE = "terminal_return_variance"
    TERMINAL_RETURN = "terminal_return"
    EXCURSIONS = "excursions"
    FIRST_PASSAGE = "ordered_first_passage"
    TRAJECTORY = "coherent_trajectory"
    COUNT = "count"
    ACTION_VALUE = "action_value"


@dataclass(frozen=True)
class Target:
    id: str
    definition_version: str
    asset: str
    decision_at: int
    horizon_end: int
    observation_process: str
    population: str
    unit: Unit
    capabilities: frozenset[Capability]
    object_version: str | None = None
    geometry_id: str | None = None
    policy_version: str | None = None

    def __post_init__(self) -> None:
        timestamp(self.decision_at)
        timestamp(self.horizon_end)
        if self.horizon_end <= self.decision_at or not self.id or not self.definition_version:
            raise ContractError("target must have a fixed future endpoint and version")
        if not self.observation_process or not self.population or not isinstance(self.unit, Unit):
            raise ContractError("target needs observation process, population and units")
        if not isinstance(self.capabilities, frozenset) or not self.capabilities or any(not isinstance(c, Capability) for c in self.capabilities):
            raise ContractError("explicit forecast capabilities required")

    @property
    def signature(self) -> str:
        return digest(self)


@dataclass(frozen=True)
class Forecast:
    id: str
    target: Target
    clocks: Clocks
    distribution_json: bytes
    uncertainty_type: str
    model_version: str
    fold_id: str
    calibrator_version: str | None
    upstream_prediction_ids: tuple[str, ...]
    coverage: tuple[CoverageMask, ...]
    abstention_reason: str | None = None

    def __post_init__(self) -> None:
        _json_payload(self.distribution_json)
        _unique(self.upstream_prediction_ids, "upstream predictions")
        if not isinstance(self.coverage, tuple):
            raise ContractError("forecast coverage must be immutable")
        if not all((self.id, self.uncertainty_type, self.model_version, self.fold_id)):
            raise ContractError("forecast identity, uncertainty and fitted lineage required")
        if self.clocks.known_at < self.target.decision_at:
            raise ContractError("forecast precedes its original decision cut")

    def require(self, target: Target, capabilities: frozenset[Capability], *, cut: int) -> None:
        if self.target.signature != target.signature:
            raise ContractError("forecast target/horizon/geometry/population mismatch")
        if not capabilities.issubset(self.target.capabilities):
            raise DependencyUnavailable("forecast does not identify required path capability")
        if not self.clocks.available(cut) or cut >= self.target.horizon_end or self.abstention_reason:
            raise DependencyUnavailable("forecast is unavailable, expired or abstaining")


@dataclass(frozen=True)
class Opportunity:
    id: str
    decision_set_id: str
    object_version: str
    source_event_ids: tuple[str, ...]
    side: int
    plan_ids: tuple[str, ...]
    forecast_ids: tuple[str, ...]
    wait_action_ids: tuple[str, ...]
    clocks: Clocks
    coverage: tuple[CoverageMask, ...]
    unavailable_reason: str | None

    def __post_init__(self) -> None:
        if type(self.side) is not int or self.side not in {-1, 1}:
            raise ContractError("opportunity side must be signed")
        if not self.id or not self.decision_set_id or not self.object_version:
            raise ContractError("opportunity requires decision set and object version")
        for values in (self.source_event_ids, self.plan_ids, self.forecast_ids, self.wait_action_ids):
            _unique(values, "opportunity inputs")
        if not isinstance(self.coverage, tuple):
            raise ContractError("opportunity coverage must be immutable")


@dataclass(frozen=True)
class Decision:
    id: str
    at: int
    candidate_ids: tuple[str, ...]
    selected_action: str
    rejected_reasons: tuple[tuple[str, str], ...]
    pre_action_state_version: str
    model_versions: tuple[str, ...]
    intent_id: str | None
    expires_at: int | None
    risk_verdict: str
    completed_at: int
    dispatched_at: int | None

    def __post_init__(self) -> None:
        timestamp(self.at)
        timestamp(self.completed_at)
        _unique(self.candidate_ids, "decision candidates")
        _unique(self.model_versions, "decision model versions")
        if (not isinstance(self.rejected_reasons, tuple)
                or any(not isinstance(row, tuple) or len(row) != 2
                       or any(not isinstance(v, str) or not v for v in row) for row in self.rejected_reasons)):
            raise ContractError("rejected reasons must be immutable candidate/reason pairs")
        if self.completed_at < self.at:
            raise ContractError("decision completion precedes information cut")
        if self.expires_at is not None:
            timestamp(self.expires_at)
            if self.expires_at <= self.at:
                raise ContractError("intent is already expired at its original cut")
        if self.dispatched_at is not None:
            timestamp(self.dispatched_at)
            if (self.dispatched_at < self.completed_at or not self.intent_id
                    or (self.expires_at is not None and self.dispatched_at >= self.expires_at)):
                raise ContractError("dispatch requires a completed, unexpired intent")


@dataclass(frozen=True)
class OrderEvent:
    id: str
    client_id: str
    broker_id: str | None
    kind: str
    quantity: int
    side: int
    price: Ticks | None
    fees: Quantity
    clocks: Clocks
    previous_state: str
    idempotency_key: str

    def __post_init__(self) -> None:
        if not all((self.id, self.client_id, self.kind, self.previous_state, self.idempotency_key)):
            raise ContractError("order identity/state/idempotency required")
        if type(self.quantity) is not int or self.quantity != 1 or type(self.side) is not int or self.side not in {-1, 1}:
            raise ContractError("primary order must be exactly one signed outright mini")
        if self.fees.unit != Unit.USD or self.fees.value < 0:
            raise ContractError("explicit nonnegative USD fees required")


@dataclass(frozen=True)
class Outcome:
    id: str
    candidate_id: str
    target: Target
    maturity_at: int
    actual_observation_end: int
    status: str
    observed_json: bytes
    revision: int = 0
    ambiguous: bool = False
    fill_status: str | None = None
    sequential_account_id: str | None = None

    def __post_init__(self) -> None:
        _json_payload(self.observed_json)
        timestamp(self.maturity_at)
        timestamp(self.actual_observation_end)
        if self.status not in {"observed", "censored", "ambiguous", "ineligible"}:
            raise ContractError("invalid outcome observation status")
        if self.actual_observation_end < self.target.decision_at or self.maturity_at < self.actual_observation_end:
            raise ContractError("label maturity/observation precedes required data")
        if type(self.revision) is not int or self.revision < 0 or not self.id or not self.candidate_id:
            raise ContractError("invalid immutable outcome identity")
