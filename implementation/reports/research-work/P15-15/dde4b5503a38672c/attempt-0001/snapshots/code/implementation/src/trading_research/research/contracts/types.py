"""Frozen research records for Phase 1.5. Boundary validation lives here."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Any, Iterable, Literal, Mapping, Protocol, TypeAlias

from trading_research.errors import ContractError

Ns: TypeAlias = int
AssetId: TypeAlias = str
Side: TypeAlias = Literal[-1, 1]
JSONValue: TypeAlias = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]

SHA256_LEN = 64
ACCOUNT_DAY_LEN = 10
PROVENANCE = frozenset({"source_literal", "source_inspired", "custom"})
CONTACT_KINDS = frozenset({"touch", "strict_sweep", "ambiguous"})
FORECAST_SUPPORT = frozenset({"supported", "low_support", "input_limited", "unavailable"})


class Coverage(Enum):
    COMPLETE = "complete_observed_scope"
    PARTIAL = "partial"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"


def freeze_json_value(value: object) -> object:
    """Copy mappings and sequences so a frozen record cannot alias callers."""
    if isinstance(value, MappingProxyType):
        return MappingProxyType({str(k): freeze_json_value(v) for k, v in value.items()})
    if isinstance(value, dict):
        if any(not isinstance(k, str) for k in value):
            raise ContractError("JSON keys must be strings")
        return MappingProxyType({k: freeze_json_value(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze_json_value(v) for v in value)
    return value


def require_ns(name: str, value: object) -> int:
    if type(value) is not int:
        raise ContractError(f"{name} must be an int UTC nanosecond clock")
    if value < 0:
        raise ContractError(f"{name} must be nonnegative")
    return value


def require_sha256(name: str, value: object) -> str:
    if not isinstance(value, str) or len(value) != SHA256_LEN or any(c not in "0123456789abcdef" for c in value):
        raise ContractError(f"{name} must be a lowercase 64-character SHA-256 hex digest")
    return value


def require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{name} must be a nonempty string")
    return value


def require_account_day(name: str, value: object) -> str:
    text = require_text(name, value)
    if len(text) != ACCOUNT_DAY_LEN or text[4] != "-" or text[7] != "-":
        raise ContractError(f"{name} must be YYYY-MM-DD")
    year, month, day = int(text[0:4]), int(text[5:7]), int(text[8:10])
    if not (1 <= month <= 12 and 1 <= day <= 31):
        raise ContractError(f"{name} must be a calendar date")
    return text


def require_decimal(name: str, value: object) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ContractError(f"{name} must be a finite Decimal")
    return value


def require_optional_decimal(name: str, value: object) -> Decimal | None:
    if value is None:
        return None
    return require_decimal(name, value)


def require_side(name: str, value: object) -> int:
    if type(value) is not int or value not in (-1, 1):
        raise ContractError(f"{name} must be +1 or -1")
    return value


def require_nonneg_int(name: str, value: object) -> int:
    if type(value) is not int or value < 0:
        raise ContractError(f"{name} must be a nonnegative int")
    return value


def require_coverage(name: str, value: object) -> Coverage:
    if isinstance(value, Coverage):
        return value
    raise ContractError(f"{name} must be a Coverage enum")


def require_interval(name: str, start: int, end: int) -> None:
    if end < start:
        raise ContractError(f"{name} end must be at or after start")


def require_not_future(event_start_ns: int, event_end_ns: int, available_at_ns: int) -> None:
    require_interval("evidence event", event_start_ns, event_end_ns)
    if event_end_ns > available_at_ns:
        raise ContractError("future evidence: event_end_ns exceeds available_at_ns")


def require_finite_float(name: str, value: object) -> float:
    if type(value) is not float or not isfinite(value):
        raise ContractError(f"{name} must be a finite float")
    return value


def _replace(instance: object, field: str, value: object) -> None:
    object.__setattr__(instance, field, value)


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    path: str
    sha256: str
    schema_version: str
    byte_count: int
    row_count: int | None

    def __post_init__(self) -> None:
        require_text("path", self.path)
        require_sha256("sha256", self.sha256)
        require_text("schema_version", self.schema_version)
        require_nonneg_int("byte_count", self.byte_count)
        if self.row_count is not None:
            require_nonneg_int("row_count", self.row_count)


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    artifact_sha256: str
    row_ids: tuple[str, ...]
    event_start_ns: Ns
    event_end_ns: Ns
    available_at_ns: Ns
    coverage: Coverage
    limitation_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        require_sha256("artifact_sha256", self.artifact_sha256)
        if not isinstance(self.row_ids, tuple) or any(not isinstance(i, str) or not i for i in self.row_ids):
            raise ContractError("row_ids must be a tuple of nonempty strings")
        require_ns("event_start_ns", self.event_start_ns)
        require_ns("event_end_ns", self.event_end_ns)
        require_ns("available_at_ns", self.available_at_ns)
        require_coverage("coverage", self.coverage)
        require_not_future(self.event_start_ns, self.event_end_ns, self.available_at_ns)
        if not isinstance(self.limitation_ids, tuple) or any(not isinstance(i, str) or not i for i in self.limitation_ids):
            raise ContractError("limitation_ids must be a tuple of nonempty strings")


@dataclass(frozen=True, slots=True)
class CoverageReceipt:
    start_ns: Ns
    end_ns: Ns
    status: Coverage
    expected_matching_intervals: tuple[tuple[Ns, Ns], ...]
    observed_intervals: tuple[tuple[Ns, Ns], ...]
    missing_intervals: tuple[tuple[Ns, Ns], ...]
    calendar_sha256: str
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        require_ns("start_ns", self.start_ns)
        require_ns("end_ns", self.end_ns)
        require_interval("coverage window", self.start_ns, self.end_ns)
        require_coverage("status", self.status)
        require_sha256("calendar_sha256", self.calendar_sha256)
        for label in ("expected_matching_intervals", "observed_intervals", "missing_intervals"):
            rows = getattr(self, label)
            if not isinstance(rows, tuple):
                raise ContractError(f"{label} must be a tuple")
            for start, end in rows:
                require_ns(label, start)
                require_ns(label, end)
                require_interval(label, start, end)
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, EvidenceRef) for item in self.evidence):
            raise ContractError("evidence must be a tuple of EvidenceRef")
        for item in self.evidence:
            if item.available_at_ns > self.end_ns:
                raise ContractError("future evidence: coverage evidence exceeds coverage window")


@dataclass(frozen=True, slots=True)
class NativeTrade:
    event_id: str
    asset_id: AssetId
    event_ns: Ns
    available_at_ns: Ns
    price: Decimal
    quantity: int
    aggressor: Side | None
    evidence: EvidenceRef

    def __post_init__(self) -> None:
        require_text("event_id", self.event_id)
        require_text("asset_id", self.asset_id)
        require_ns("event_ns", self.event_ns)
        require_ns("available_at_ns", self.available_at_ns)
        if self.event_ns > self.available_at_ns:
            raise ContractError("future evidence: trade event_ns exceeds available_at_ns")
        require_decimal("price", self.price)
        require_nonneg_int("quantity", self.quantity)
        if self.aggressor is not None:
            require_side("aggressor", self.aggressor)
        if not isinstance(self.evidence, EvidenceRef):
            raise ContractError("trade evidence must be EvidenceRef")
        if self.available_at_ns < self.evidence.available_at_ns:
            raise ContractError("future evidence: trade available_at_ns is earlier than its evidence")


@dataclass(frozen=True, slots=True)
class NativeBatch:
    batch_id: str
    event_ns: Ns
    available_at_ns: Ns
    trades: tuple[NativeTrade, ...]
    internal_order_known: bool

    def __post_init__(self) -> None:
        require_text("batch_id", self.batch_id)
        require_ns("event_ns", self.event_ns)
        require_ns("available_at_ns", self.available_at_ns)
        if self.event_ns > self.available_at_ns:
            raise ContractError("future evidence: batch event_ns exceeds available_at_ns")
        if type(self.internal_order_known) is not bool:
            raise ContractError("internal_order_known must be bool")
        if not isinstance(self.trades, tuple) or any(not isinstance(t, NativeTrade) for t in self.trades):
            raise ContractError("trades must be a tuple of NativeTrade")
        for trade in self.trades:
            if trade.event_ns != self.event_ns:
                raise ContractError("batch trades must share the batch event clock")
            if trade.available_at_ns > self.available_at_ns:
                raise ContractError("trade availability cannot follow the batch")


@dataclass(frozen=True, slots=True)
class QuoteBatch:
    batch_id: str
    asset_id: AssetId
    event_ns: Ns
    available_at_ns: Ns
    bid: Decimal | None
    ask: Decimal | None
    bid_size: int | None
    ask_size: int | None
    ambiguous: bool
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        require_text("batch_id", self.batch_id)
        require_text("asset_id", self.asset_id)
        require_ns("event_ns", self.event_ns)
        require_ns("available_at_ns", self.available_at_ns)
        if self.event_ns > self.available_at_ns:
            raise ContractError("future evidence: quote event_ns exceeds available_at_ns")
        bid = require_optional_decimal("bid", self.bid)
        ask = require_optional_decimal("ask", self.ask)
        if bid is not None and bid < 0:
            raise ContractError("bid must be nonnegative")
        if ask is not None and ask < 0:
            raise ContractError("ask must be nonnegative")
        if bid is not None and ask is not None and ask < bid:
            raise ContractError("ask must be at least bid")
        if self.bid_size is not None:
            require_nonneg_int("bid_size", self.bid_size)
        if self.ask_size is not None:
            require_nonneg_int("ask_size", self.ask_size)
        if type(self.ambiguous) is not bool:
            raise ContractError("ambiguous must be bool")
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, EvidenceRef) for item in self.evidence):
            raise ContractError("quote evidence must be a tuple of EvidenceRef")
        for item in self.evidence:
            if item.available_at_ns > self.available_at_ns:
                raise ContractError("future evidence: quote parent availability exceeds available_at_ns")


@dataclass(frozen=True, slots=True)
class Bar:
    bar_id: str
    asset_id: AssetId
    start_ns: Ns
    end_ns: Ns
    available_at_ns: Ns
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    volume: int
    known_signed_volume: int
    unknown_aggressor_volume: int
    coverage: Coverage
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        require_text("bar_id", self.bar_id)
        require_text("asset_id", self.asset_id)
        require_ns("start_ns", self.start_ns)
        require_ns("end_ns", self.end_ns)
        require_ns("available_at_ns", self.available_at_ns)
        if self.end_ns <= self.start_ns:
            raise ContractError("bar end must be after start")
        if self.end_ns > self.available_at_ns:
            raise ContractError("future evidence: bar end exceeds available_at_ns")
        for name in ("open", "high", "low", "close"):
            require_optional_decimal(name, getattr(self, name))
        if self.high is not None and self.low is not None and self.high < self.low:
            raise ContractError("bar high must be at least low")
        require_nonneg_int("volume", self.volume)
        if type(self.known_signed_volume) is not int:
            raise ContractError("known_signed_volume must be int")
        require_nonneg_int("unknown_aggressor_volume", self.unknown_aggressor_volume)
        if self.unknown_aggressor_volume > self.volume:
            raise ContractError("unknown aggressor volume cannot exceed total volume")
        require_coverage("coverage", self.coverage)
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, EvidenceRef) for item in self.evidence):
            raise ContractError("bar evidence must be a tuple of EvidenceRef")
        for item in self.evidence:
            if item.available_at_ns > self.available_at_ns:
                raise ContractError("future evidence: bar parent availability exceeds available_at_ns")


@dataclass(frozen=True, slots=True)
class FeatureValue:
    name: str
    value: float | None
    unit: str
    available_at_ns: Ns
    evidence: tuple[EvidenceRef, ...]
    missing_reason: str | None

    def __post_init__(self) -> None:
        require_text("name", self.name)
        require_text("unit", self.unit)
        require_ns("available_at_ns", self.available_at_ns)
        if self.value is None:
            if not isinstance(self.missing_reason, str) or not self.missing_reason:
                raise ContractError("missing feature needs missing_reason")
        else:
            require_finite_float("value", self.value)
            if self.missing_reason is not None:
                raise ContractError("present feature cannot carry missing_reason")
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, EvidenceRef) for item in self.evidence):
            raise ContractError("feature evidence must be a tuple of EvidenceRef")
        for item in self.evidence:
            if item.available_at_ns > self.available_at_ns:
                raise ContractError("future evidence: feature parent availability exceeds feature clock")


@dataclass(frozen=True, slots=True)
class Snapshot:
    snapshot_id: str
    account_day: str
    asset_id: AssetId
    issue_at_ns: Ns
    feature_schema: str
    values: tuple[FeatureValue, ...]
    policy_sha256: str

    def __post_init__(self) -> None:
        require_text("snapshot_id", self.snapshot_id)
        require_account_day("account_day", self.account_day)
        require_text("asset_id", self.asset_id)
        require_ns("issue_at_ns", self.issue_at_ns)
        require_text("feature_schema", self.feature_schema)
        require_sha256("policy_sha256", self.policy_sha256)
        if not isinstance(self.values, tuple) or any(not isinstance(item, FeatureValue) for item in self.values):
            raise ContractError("values must be a tuple of FeatureValue")
        for item in self.values:
            if item.available_at_ns > self.issue_at_ns:
                raise ContractError("future evidence: feature availability exceeds snapshot issue time")


@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    family: str
    source_branch: str | None
    version: str
    provenance: Literal["source_literal", "source_inspired", "custom"]
    baseline_rule_id: str | None
    changed_axis: str
    parameters: dict[str, str | int | bool]
    required_inputs: tuple[str, ...]
    required_stages: tuple[str, ...]
    formation_policy: str
    expiry_policy: str

    def __post_init__(self) -> None:
        require_text("rule_id", self.rule_id)
        require_text("family", self.family)
        if self.source_branch is not None:
            require_text("source_branch", self.source_branch)
        require_text("version", self.version)
        if self.provenance not in PROVENANCE:
            raise ContractError("provenance must be source_literal, source_inspired or custom")
        if self.baseline_rule_id is not None:
            require_text("baseline_rule_id", self.baseline_rule_id)
        require_text("changed_axis", self.changed_axis)
        require_text("formation_policy", self.formation_policy)
        require_text("expiry_policy", self.expiry_policy)
        params = freeze_json_value(self.parameters)
        if not isinstance(params, MappingProxyType):
            raise ContractError("parameters must be a mapping")
        for key, item in params.items():
            if not isinstance(key, str) or not key:
                raise ContractError("parameter keys must be nonempty strings")
            if type(item) not in (str, int, bool):
                raise ContractError("parameter values must be str, int or bool")
        _replace(self, "parameters", params)
        for label in ("required_inputs", "required_stages"):
            rows = getattr(self, label)
            if not isinstance(rows, tuple) or any(not isinstance(i, str) or not i for i in rows):
                raise ContractError(f"{label} must be a tuple of nonempty strings")


@dataclass(frozen=True, slots=True)
class Formation:
    formation_id: str
    asset_id: AssetId
    start_ns: Ns
    end_ns: Ns
    available_at_ns: Ns
    high: Decimal
    low: Decimal
    volume: int
    profile_id: str | None
    construction_kind: str
    parent_ids: tuple[str, ...]
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        require_text("formation_id", self.formation_id)
        require_text("asset_id", self.asset_id)
        require_ns("start_ns", self.start_ns)
        require_ns("end_ns", self.end_ns)
        require_ns("available_at_ns", self.available_at_ns)
        require_interval("formation", self.start_ns, self.end_ns)
        if self.end_ns > self.available_at_ns:
            raise ContractError("future evidence: formation end exceeds available_at_ns")
        require_decimal("high", self.high)
        require_decimal("low", self.low)
        if self.high < self.low:
            raise ContractError("invalid geometry: formation high is below low")
        require_nonneg_int("volume", self.volume)
        if self.profile_id is not None:
            require_text("profile_id", self.profile_id)
        require_text("construction_kind", self.construction_kind)
        if not isinstance(self.parent_ids, tuple) or any(not isinstance(i, str) or not i for i in self.parent_ids):
            raise ContractError("parent_ids must be a tuple of nonempty strings")
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, EvidenceRef) for item in self.evidence):
            raise ContractError("formation evidence must be a tuple of EvidenceRef")
        for item in self.evidence:
            if item.available_at_ns > self.available_at_ns:
                raise ContractError("future evidence: formation parent availability exceeds available_at_ns")


@dataclass(frozen=True, slots=True)
class Reference:
    reference_id: str
    reference_lifecycle_id: str
    formation_id: str
    asset_id: AssetId
    lower: Decimal
    upper: Decimal
    issue_at_ns: Ns
    expiry_at_ns: Ns
    permitted_sides: tuple[Side, ...]
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        require_text("reference_id", self.reference_id)
        require_text("reference_lifecycle_id", self.reference_lifecycle_id)
        require_text("formation_id", self.formation_id)
        require_text("asset_id", self.asset_id)
        require_decimal("lower", self.lower)
        require_decimal("upper", self.upper)
        if self.upper < self.lower:
            raise ContractError("invalid geometry: reference upper is below lower")
        require_ns("issue_at_ns", self.issue_at_ns)
        require_ns("expiry_at_ns", self.expiry_at_ns)
        if self.expiry_at_ns < self.issue_at_ns:
            raise ContractError("reference expiry cannot precede issue")
        if not isinstance(self.permitted_sides, tuple) or not self.permitted_sides:
            raise ContractError("permitted_sides must be a nonempty tuple")
        for side in self.permitted_sides:
            require_side("permitted_sides", side)
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, EvidenceRef) for item in self.evidence):
            raise ContractError("reference evidence must be a tuple of EvidenceRef")
        for item in self.evidence:
            if item.available_at_ns > self.issue_at_ns:
                raise ContractError("future evidence: reference parent availability exceeds issue time")


@dataclass(frozen=True, slots=True)
class Contact:
    contact_id: str
    reference_id: str
    batch_id: str
    at_ns: Ns
    available_at_ns: Ns
    side: Side
    kind: Literal["touch", "strict_sweep", "ambiguous"]
    possible_prices: tuple[Decimal, ...]
    departure_evidence: tuple[EvidenceRef, ...]
    evidence: tuple[EvidenceRef, ...]

    def __post_init__(self) -> None:
        require_text("contact_id", self.contact_id)
        require_text("reference_id", self.reference_id)
        require_text("batch_id", self.batch_id)
        require_ns("at_ns", self.at_ns)
        require_ns("available_at_ns", self.available_at_ns)
        if self.at_ns > self.available_at_ns:
            raise ContractError("future evidence: contact time exceeds available_at_ns")
        require_side("side", self.side)
        if self.kind not in CONTACT_KINDS:
            raise ContractError("contact kind must be touch, strict_sweep or ambiguous")
        if not isinstance(self.possible_prices, tuple) or not self.possible_prices:
            raise ContractError("possible_prices must be a nonempty tuple of Decimal")
        for price in self.possible_prices:
            require_decimal("possible_prices", price)
        if self.kind == "ambiguous" and len(self.possible_prices) < 2:
            raise ContractError("ambiguous contact needs at least two possible prices")
        for label in ("departure_evidence", "evidence"):
            rows = getattr(self, label)
            if not isinstance(rows, tuple) or any(not isinstance(item, EvidenceRef) for item in rows):
                raise ContractError(f"{label} must be a tuple of EvidenceRef")
            for item in rows:
                if item.available_at_ns > self.available_at_ns:
                    raise ContractError(f"future evidence: {label} exceeds contact available_at_ns")


@dataclass(frozen=True, slots=True)
class PredicateEvidence:
    name: str
    value: bool | None
    available_at_ns: Ns | None
    evidence: tuple[EvidenceRef, ...]
    missing_reason: str | None

    def __post_init__(self) -> None:
        require_text("name", self.name)
        if self.value is None:
            if not isinstance(self.missing_reason, str) or not self.missing_reason:
                raise ContractError("unknown predicate needs missing_reason")
        else:
            if type(self.value) is not bool:
                raise ContractError("predicate value must be bool or None")
            if self.missing_reason is not None:
                raise ContractError("known predicate cannot carry missing_reason")
        if self.available_at_ns is not None:
            require_ns("available_at_ns", self.available_at_ns)
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, EvidenceRef) for item in self.evidence):
            raise ContractError("predicate evidence must be a tuple of EvidenceRef")
        if self.available_at_ns is not None:
            for item in self.evidence:
                if item.available_at_ns > self.available_at_ns:
                    raise ContractError("future evidence: predicate parent availability exceeds predicate clock")


@dataclass(frozen=True, slots=True)
class ContextEvidence:
    family: str
    branch: str
    reference_id: str
    at_ns: Ns
    predicates: tuple[PredicateEvidence, ...]

    def __post_init__(self) -> None:
        require_text("family", self.family)
        require_text("branch", self.branch)
        require_text("reference_id", self.reference_id)
        require_ns("at_ns", self.at_ns)
        if not isinstance(self.predicates, tuple) or any(not isinstance(item, PredicateEvidence) for item in self.predicates):
            raise ContractError("predicates must be a tuple of PredicateEvidence")
        for item in self.predicates:
            if item.available_at_ns is not None and item.available_at_ns > self.at_ns:
                raise ContractError("future evidence: predicate availability exceeds context time")


@dataclass(frozen=True, slots=True)
class SequenceSpec:
    recipe_id: str
    ordered_stages: tuple[str, ...]
    deadline_seconds: int
    parameters: dict[str, str | int | bool]

    def __post_init__(self) -> None:
        require_text("recipe_id", self.recipe_id)
        if not isinstance(self.ordered_stages, tuple) or not self.ordered_stages:
            raise ContractError("ordered_stages must be a nonempty tuple")
        if any(not isinstance(i, str) or not i for i in self.ordered_stages):
            raise ContractError("ordered_stages must be nonempty strings")
        require_nonneg_int("deadline_seconds", self.deadline_seconds)
        params = freeze_json_value(self.parameters)
        _replace(self, "parameters", params)


@dataclass(frozen=True, slots=True)
class SequenceState:
    sequence_id: str
    recipe_id: str
    contact_id: str
    state: str
    state_at_ns: Ns
    available_at_ns: Ns
    deadline_ns: Ns
    stage_evidence: tuple[PredicateEvidence, ...]
    terminal_reason: str | None
    working_memory: dict[str, JSONValue]

    def __post_init__(self) -> None:
        require_text("sequence_id", self.sequence_id)
        require_text("recipe_id", self.recipe_id)
        require_text("contact_id", self.contact_id)
        require_text("state", self.state)
        require_ns("state_at_ns", self.state_at_ns)
        require_ns("available_at_ns", self.available_at_ns)
        require_ns("deadline_ns", self.deadline_ns)
        if self.state_at_ns > self.available_at_ns:
            raise ContractError("future evidence: sequence state exceeds available_at_ns")
        if self.terminal_reason is not None:
            require_text("terminal_reason", self.terminal_reason)
        if not isinstance(self.stage_evidence, tuple) or any(not isinstance(item, PredicateEvidence) for item in self.stage_evidence):
            raise ContractError("stage_evidence must be a tuple of PredicateEvidence")
        for item in self.stage_evidence:
            if item.available_at_ns is not None and item.available_at_ns > self.available_at_ns:
                raise ContractError("future evidence: stage evidence exceeds sequence available_at_ns")
        _replace(self, "working_memory", freeze_json_value(self.working_memory))


@dataclass(frozen=True, slots=True)
class SequenceInputs:
    reference: Reference
    context: ContextEvidence
    completed_bars: tuple[Bar, ...]
    flow_features: tuple[FeatureValue, ...]
    available_at_ns: Ns

    def __post_init__(self) -> None:
        if not isinstance(self.reference, Reference):
            raise ContractError("reference must be Reference")
        if not isinstance(self.context, ContextEvidence):
            raise ContractError("context must be ContextEvidence")
        require_ns("available_at_ns", self.available_at_ns)
        if self.reference.issue_at_ns > self.available_at_ns:
            raise ContractError("future evidence: reference issue exceeds sequence input clock")
        if self.context.at_ns > self.available_at_ns:
            raise ContractError("future evidence: context time exceeds sequence input clock")
        if not isinstance(self.completed_bars, tuple) or any(not isinstance(item, Bar) for item in self.completed_bars):
            raise ContractError("completed_bars must be a tuple of Bar")
        if not isinstance(self.flow_features, tuple) or any(not isinstance(item, FeatureValue) for item in self.flow_features):
            raise ContractError("flow_features must be a tuple of FeatureValue")
        for bar in self.completed_bars:
            if bar.available_at_ns > self.available_at_ns:
                raise ContractError("future evidence: bar availability exceeds sequence input clock")
        for feature in self.flow_features:
            if feature.available_at_ns > self.available_at_ns:
                raise ContractError("future evidence: flow feature exceeds sequence input clock")


@dataclass(frozen=True, slots=True)
class Opportunity:
    opportunity_id: str
    parent_opportunity_id: str | None
    overlap_group_id: str
    rule_id: str
    family: str
    branch: str
    account_day: str
    side: Side
    issue_at_ns: Ns
    decision_at_ns: Ns
    reference_asset: AssetId
    response_asset: AssetId
    execution_asset: AssetId
    reference_id: str
    lower: Decimal
    upper: Decimal
    entry_reference: Decimal | None
    invalidation: Decimal | None
    objective: Decimal | None
    expiry_at_ns: Ns
    stages: tuple[EvidenceRef, ...]
    coverage: Coverage
    source_exact: bool
    hypothesis_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        require_text("opportunity_id", self.opportunity_id)
        if self.parent_opportunity_id is not None:
            require_text("parent_opportunity_id", self.parent_opportunity_id)
        require_text("overlap_group_id", self.overlap_group_id)
        require_text("rule_id", self.rule_id)
        require_text("family", self.family)
        require_text("branch", self.branch)
        require_account_day("account_day", self.account_day)
        require_side("side", self.side)
        require_ns("issue_at_ns", self.issue_at_ns)
        require_ns("decision_at_ns", self.decision_at_ns)
        require_ns("expiry_at_ns", self.expiry_at_ns)
        if self.issue_at_ns > self.decision_at_ns:
            raise ContractError("decision cannot precede issue")
        if self.decision_at_ns > self.expiry_at_ns:
            raise ContractError("decision cannot follow expiry")
        require_text("reference_asset", self.reference_asset)
        require_text("response_asset", self.response_asset)
        require_text("execution_asset", self.execution_asset)
        require_text("reference_id", self.reference_id)
        require_decimal("lower", self.lower)
        require_decimal("upper", self.upper)
        if self.upper < self.lower:
            raise ContractError("invalid geometry: opportunity upper is below lower")
        require_optional_decimal("entry_reference", self.entry_reference)
        require_optional_decimal("invalidation", self.invalidation)
        require_optional_decimal("objective", self.objective)
        if not isinstance(self.stages, tuple) or any(not isinstance(item, EvidenceRef) for item in self.stages):
            raise ContractError("stages must be a tuple of EvidenceRef")
        for item in self.stages:
            if item.available_at_ns > self.decision_at_ns:
                raise ContractError("future evidence: stage availability exceeds decision time")
        require_coverage("coverage", self.coverage)
        if type(self.source_exact) is not bool:
            raise ContractError("source_exact must be bool")
        if not isinstance(self.hypothesis_ids, tuple) or any(not isinstance(i, str) or not i for i in self.hypothesis_ids):
            raise ContractError("hypothesis_ids must be a tuple of nonempty strings")


@dataclass(frozen=True, slots=True)
class ScanResult:
    opportunities: tuple[Opportunity, ...]
    rejected_contacts: tuple[Contact, ...]
    unknown_contacts: tuple[Contact, ...]
    formations: tuple[Formation, ...]
    sequences: tuple[SequenceState, ...]
    coverage: CoverageReceipt
    baseline_payloads: tuple[dict[str, JSONValue], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.opportunities, tuple) or any(not isinstance(i, Opportunity) for i in self.opportunities):
            raise ContractError("opportunities must be a tuple of Opportunity")
        if not isinstance(self.rejected_contacts, tuple) or any(not isinstance(i, Contact) for i in self.rejected_contacts):
            raise ContractError("rejected_contacts must be a tuple of Contact")
        if not isinstance(self.unknown_contacts, tuple) or any(not isinstance(i, Contact) for i in self.unknown_contacts):
            raise ContractError("unknown_contacts must be a tuple of Contact")
        if not isinstance(self.formations, tuple) or any(not isinstance(i, Formation) for i in self.formations):
            raise ContractError("formations must be a tuple of Formation")
        if not isinstance(self.sequences, tuple) or any(not isinstance(i, SequenceState) for i in self.sequences):
            raise ContractError("sequences must be a tuple of SequenceState")
        if not isinstance(self.coverage, CoverageReceipt):
            raise ContractError("coverage must be CoverageReceipt")
        frozen = tuple(freeze_json_value(item) for item in self.baseline_payloads)
        _replace(self, "baseline_payloads", frozen)


BaselineResult: TypeAlias = ScanResult


@dataclass(frozen=True, slots=True)
class Forecast:
    forecast_id: str
    expert_id: str
    artifact_sha256: str
    snapshot_id: str
    issue_at_ns: Ns
    horizon_id: str
    target_end_ns: Ns | None
    output: dict[str, float | str | None]
    support: str
    train_end_ns: Ns
    fit_available_at_ns: Ns
    input_feature_ids: tuple[str, ...]
    parent_forecast_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        require_text("forecast_id", self.forecast_id)
        require_text("expert_id", self.expert_id)
        require_sha256("artifact_sha256", self.artifact_sha256)
        require_text("snapshot_id", self.snapshot_id)
        require_ns("issue_at_ns", self.issue_at_ns)
        require_text("horizon_id", self.horizon_id)
        require_ns("train_end_ns", self.train_end_ns)
        require_ns("fit_available_at_ns", self.fit_available_at_ns)
        if not (self.train_end_ns <= self.fit_available_at_ns <= self.issue_at_ns):
            raise ContractError("future evidence: train_end_ns must be <= fit_available_at_ns <= issue_at_ns")
        if self.support not in FORECAST_SUPPORT:
            raise ContractError("unsupported forecast support label")
        if self.support == "supported":
            if self.target_end_ns is None or type(self.target_end_ns) is not int:
                raise ContractError("supported forecast needs a known target_end_ns")
            if self.target_end_ns <= self.issue_at_ns:
                raise ContractError("supported forecast target must end after issue")
        elif self.target_end_ns is not None:
            require_ns("target_end_ns", self.target_end_ns)
        frozen = freeze_json_value(self.output)
        if not isinstance(frozen, MappingProxyType):
            raise ContractError("forecast output must be a mapping")
        for key, item in frozen.items():
            if isinstance(item, float) and not isfinite(item):
                raise ContractError("supported forecast output must be finite")
        _replace(self, "output", frozen)
        for label in ("input_feature_ids", "parent_forecast_ids"):
            rows = getattr(self, label)
            if not isinstance(rows, tuple) or any(not isinstance(i, str) or not i for i in rows):
                raise ContractError(f"{label} must be a tuple of nonempty strings")


class MarketView(Protocol):
    def executions(self, start_ns: Ns, end_ns: Ns) -> Iterable[NativeBatch]: ...
    def quotes(self, start_ns: Ns, end_ns: Ns) -> Iterable[QuoteBatch]: ...
    def coverage(self, start_ns: Ns, end_ns: Ns) -> CoverageReceipt: ...
    def completed_bars(self, start_ns: Ns, end_ns: Ns, seconds: int) -> tuple[Bar, ...]: ...


def source_exact_from_baseline(payload: dict[str, JSONValue] | MappingProxyType) -> bool:
    """Author-exact unknown stays false. Geometry agreement does not promote it."""
    verdict = payload.get("author_exact_verdict")
    return verdict == "pass"


def _as_mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{name} must be a mapping")
    return dict(value)


def _as_seq(value: object, name: str) -> tuple[Any, ...]:
    if not isinstance(value, (list, tuple)):
        raise ContractError(f"{name} must be a sequence")
    return tuple(value)


def parse_coverage(name: str, value: object) -> Coverage:
    if isinstance(value, Coverage):
        return value
    if isinstance(value, str):
        for item in Coverage:
            if item.value == value or item.name == value:
                return item
    raise ContractError(f"{name} must be a Coverage enum")


def parse_decimal(name: str, value: object) -> Decimal:
    if isinstance(value, Decimal):
        return require_decimal(name, value)
    if isinstance(value, str):
        try:
            parsed = Decimal(value)
        except Exception as exc:
            raise ContractError(f"{name} must be a finite Decimal") from exc
        return require_decimal(name, parsed)
    raise ContractError(f"{name} must be a finite Decimal")


def parse_optional_decimal(name: str, value: object) -> Decimal | None:
    if value is None:
        return None
    return parse_decimal(name, value)


def parse_evidence_ref(data: object) -> EvidenceRef:
    if isinstance(data, EvidenceRef):
        return data
    payload = _as_mapping(data, "EvidenceRef")
    return EvidenceRef(
        artifact_sha256=payload.get("artifact_sha256"),
        row_ids=_as_seq(payload.get("row_ids"), "row_ids"),
        event_start_ns=payload.get("event_start_ns"),
        event_end_ns=payload.get("event_end_ns"),
        available_at_ns=payload.get("available_at_ns"),
        coverage=parse_coverage("coverage", payload.get("coverage")),
        limitation_ids=_as_seq(payload.get("limitation_ids") or (), "limitation_ids"),
    )


def parse_native_trade(data: object) -> NativeTrade:
    if isinstance(data, NativeTrade):
        return data
    payload = _as_mapping(data, "NativeTrade")
    return NativeTrade(
        event_id=payload.get("event_id"),
        asset_id=payload.get("asset_id"),
        event_ns=payload.get("event_ns"),
        available_at_ns=payload.get("available_at_ns"),
        price=parse_decimal("price", payload.get("price")),
        quantity=payload.get("quantity"),
        aggressor=payload.get("aggressor"),
        evidence=parse_evidence_ref(payload.get("evidence")),
    )


def parse_reference(data: object) -> Reference:
    if isinstance(data, Reference):
        return data
    payload = _as_mapping(data, "Reference")
    return Reference(
        reference_id=payload.get("reference_id"),
        reference_lifecycle_id=payload.get("reference_lifecycle_id"),
        formation_id=payload.get("formation_id"),
        asset_id=payload.get("asset_id"),
        lower=parse_decimal("lower", payload.get("lower")),
        upper=parse_decimal("upper", payload.get("upper")),
        issue_at_ns=payload.get("issue_at_ns"),
        expiry_at_ns=payload.get("expiry_at_ns"),
        permitted_sides=_as_seq(payload.get("permitted_sides"), "permitted_sides"),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence"), "evidence")),
    )


def parse_forecast(data: object) -> Forecast:
    if isinstance(data, Forecast):
        return data
    payload = _as_mapping(data, "Forecast")
    output = payload.get("output")
    if not isinstance(output, dict):
        raise ContractError("forecast output must be a mapping")
    return Forecast(
        forecast_id=payload.get("forecast_id"),
        expert_id=payload.get("expert_id"),
        artifact_sha256=payload.get("artifact_sha256"),
        snapshot_id=payload.get("snapshot_id"),
        issue_at_ns=payload.get("issue_at_ns"),
        horizon_id=payload.get("horizon_id"),
        target_end_ns=payload.get("target_end_ns"),
        output=output,
        support=payload.get("support"),
        train_end_ns=payload.get("train_end_ns"),
        fit_available_at_ns=payload.get("fit_available_at_ns"),
        input_feature_ids=_as_seq(payload.get("input_feature_ids") or (), "input_feature_ids"),
        parent_forecast_ids=_as_seq(payload.get("parent_forecast_ids") or (), "parent_forecast_ids"),
    )


def parse_feature_value(data: object) -> FeatureValue:
    if isinstance(data, FeatureValue):
        return data
    payload = _as_mapping(data, "FeatureValue")
    return FeatureValue(
        name=payload.get("name"),
        value=payload.get("value"),
        unit=payload.get("unit"),
        available_at_ns=payload.get("available_at_ns"),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence") or (), "evidence")),
        missing_reason=payload.get("missing_reason"),
    )


def parse_formation(data: object) -> Formation:
    if isinstance(data, Formation):
        return data
    payload = _as_mapping(data, "Formation")
    profile_id = payload.get("profile_id")
    return Formation(
        formation_id=payload.get("formation_id"),
        asset_id=payload.get("asset_id"),
        start_ns=payload.get("start_ns"),
        end_ns=payload.get("end_ns"),
        available_at_ns=payload.get("available_at_ns"),
        high=parse_decimal("high", payload.get("high")),
        low=parse_decimal("low", payload.get("low")),
        volume=payload.get("volume"),
        profile_id=profile_id,
        construction_kind=payload.get("construction_kind"),
        parent_ids=_as_seq(payload.get("parent_ids") or (), "parent_ids"),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence"), "evidence")),
    )


def parse_contact(data: object) -> Contact:
    if isinstance(data, Contact):
        return data
    payload = _as_mapping(data, "Contact")
    prices = tuple(parse_decimal("possible_prices", item) for item in _as_seq(payload.get("possible_prices"), "possible_prices"))
    return Contact(
        contact_id=payload.get("contact_id"),
        reference_id=payload.get("reference_id"),
        batch_id=payload.get("batch_id"),
        at_ns=payload.get("at_ns"),
        available_at_ns=payload.get("available_at_ns"),
        side=payload.get("side"),
        kind=payload.get("kind"),
        possible_prices=prices,
        departure_evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("departure_evidence") or (), "departure_evidence")),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence"), "evidence")),
    )


def parse_predicate_evidence(data: object) -> PredicateEvidence:
    if isinstance(data, PredicateEvidence):
        return data
    payload = _as_mapping(data, "PredicateEvidence")
    return PredicateEvidence(
        name=payload.get("name"),
        value=payload.get("value"),
        available_at_ns=payload.get("available_at_ns"),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence") or (), "evidence")),
        missing_reason=payload.get("missing_reason"),
    )


def parse_sequence_state(data: object) -> SequenceState:
    if isinstance(data, SequenceState):
        return data
    payload = _as_mapping(data, "SequenceState")
    memory = payload.get("working_memory")
    if not isinstance(memory, dict):
        raise ContractError("working_memory must be a mapping")
    return SequenceState(
        sequence_id=payload.get("sequence_id"),
        recipe_id=payload.get("recipe_id"),
        contact_id=payload.get("contact_id"),
        state=payload.get("state"),
        state_at_ns=payload.get("state_at_ns"),
        available_at_ns=payload.get("available_at_ns"),
        deadline_ns=payload.get("deadline_ns"),
        stage_evidence=tuple(parse_predicate_evidence(item) for item in _as_seq(payload.get("stage_evidence") or (), "stage_evidence")),
        terminal_reason=payload.get("terminal_reason"),
        working_memory=memory,
    )


def parse_snapshot(data: object) -> Snapshot:
    if isinstance(data, Snapshot):
        return data
    payload = _as_mapping(data, "Snapshot")
    return Snapshot(
        snapshot_id=payload.get("snapshot_id"),
        account_day=payload.get("account_day"),
        asset_id=payload.get("asset_id"),
        issue_at_ns=payload.get("issue_at_ns"),
        feature_schema=payload.get("feature_schema"),
        values=tuple(parse_feature_value(item) for item in _as_seq(payload.get("values"), "values")),
        policy_sha256=payload.get("policy_sha256"),
    )


def parse_quote_batch(data: object) -> QuoteBatch:
    if isinstance(data, QuoteBatch):
        return data
    payload = _as_mapping(data, "QuoteBatch")
    return QuoteBatch(
        batch_id=payload.get("batch_id"),
        asset_id=payload.get("asset_id"),
        event_ns=payload.get("event_ns"),
        available_at_ns=payload.get("available_at_ns"),
        bid=parse_optional_decimal("bid", payload.get("bid")),
        ask=parse_optional_decimal("ask", payload.get("ask")),
        bid_size=payload.get("bid_size"),
        ask_size=payload.get("ask_size"),
        ambiguous=payload.get("ambiguous"),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence") or (), "evidence")),
    )


def parse_bar(data: object) -> Bar:
    if isinstance(data, Bar):
        return data
    payload = _as_mapping(data, "Bar")
    return Bar(
        bar_id=payload.get("bar_id"),
        asset_id=payload.get("asset_id"),
        start_ns=payload.get("start_ns"),
        end_ns=payload.get("end_ns"),
        available_at_ns=payload.get("available_at_ns"),
        open=parse_optional_decimal("open", payload.get("open")),
        high=parse_optional_decimal("high", payload.get("high")),
        low=parse_optional_decimal("low", payload.get("low")),
        close=parse_optional_decimal("close", payload.get("close")),
        volume=payload.get("volume"),
        known_signed_volume=payload.get("known_signed_volume"),
        unknown_aggressor_volume=payload.get("unknown_aggressor_volume"),
        coverage=parse_coverage("coverage", payload.get("coverage")),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence") or (), "evidence")),
    )


def parse_coverage_receipt(data: object) -> CoverageReceipt:
    if isinstance(data, CoverageReceipt):
        return data
    payload = _as_mapping(data, "CoverageReceipt")

    def intervals(name: str) -> tuple[tuple[int, int], ...]:
        rows = []
        for item in _as_seq(payload.get(name), name):
            pair = _as_seq(item, name)
            if len(pair) != 2:
                raise ContractError(f"{name} entries must be start/end pairs")
            rows.append((pair[0], pair[1]))
        return tuple(rows)

    return CoverageReceipt(
        start_ns=payload.get("start_ns"),
        end_ns=payload.get("end_ns"),
        status=parse_coverage("status", payload.get("status")),
        expected_matching_intervals=intervals("expected_matching_intervals"),
        observed_intervals=intervals("observed_intervals"),
        missing_intervals=intervals("missing_intervals"),
        calendar_sha256=payload.get("calendar_sha256"),
        evidence=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("evidence") or (), "evidence")),
    )


def parse_opportunity(data: object) -> Opportunity:
    if isinstance(data, Opportunity):
        return data
    payload = _as_mapping(data, "Opportunity")
    return Opportunity(
        opportunity_id=payload.get("opportunity_id"),
        parent_opportunity_id=payload.get("parent_opportunity_id"),
        overlap_group_id=payload.get("overlap_group_id"),
        rule_id=payload.get("rule_id"),
        family=payload.get("family"),
        branch=payload.get("branch"),
        account_day=payload.get("account_day"),
        side=payload.get("side"),
        issue_at_ns=payload.get("issue_at_ns"),
        decision_at_ns=payload.get("decision_at_ns"),
        reference_asset=payload.get("reference_asset"),
        response_asset=payload.get("response_asset"),
        execution_asset=payload.get("execution_asset"),
        reference_id=payload.get("reference_id"),
        lower=parse_decimal("lower", payload.get("lower")),
        upper=parse_decimal("upper", payload.get("upper")),
        entry_reference=parse_optional_decimal("entry_reference", payload.get("entry_reference")),
        invalidation=parse_optional_decimal("invalidation", payload.get("invalidation")),
        objective=parse_optional_decimal("objective", payload.get("objective")),
        expiry_at_ns=payload.get("expiry_at_ns"),
        stages=tuple(parse_evidence_ref(item) for item in _as_seq(payload.get("stages"), "stages")),
        coverage=parse_coverage("coverage", payload.get("coverage")),
        source_exact=payload.get("source_exact"),
        hypothesis_ids=_as_seq(payload.get("hypothesis_ids") or (), "hypothesis_ids"),
    )


_FROM_MAPPING = {
    EvidenceRef: parse_evidence_ref,
    NativeTrade: parse_native_trade,
    Reference: parse_reference,
    Forecast: parse_forecast,
    FeatureValue: parse_feature_value,
    Formation: parse_formation,
    Contact: parse_contact,
    PredicateEvidence: parse_predicate_evidence,
    SequenceState: parse_sequence_state,
    Snapshot: parse_snapshot,
    QuoteBatch: parse_quote_batch,
    Bar: parse_bar,
    CoverageReceipt: parse_coverage_receipt,
    Opportunity: parse_opportunity,
}

for _cls, _parser in _FROM_MAPPING.items():
    _cls.from_mapping = classmethod(lambda cls, data, parser=_parser: parser(data))


def record_from_json(cls: type, text: str) -> object:
    import json
    try:
        payload = json.loads(text)
    except ValueError as exc:
        raise ContractError(f"invalid JSON: {exc}") from exc
    parser = _FROM_MAPPING.get(cls)
    if parser is None:
        raise ContractError(f"no deserializer for {cls.__name__}")
    return parser(payload)
