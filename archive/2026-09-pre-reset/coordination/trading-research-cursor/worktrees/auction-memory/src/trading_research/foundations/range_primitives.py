"""Immutable neutral range measurements shared by C01/M12/L01/L02/L03.

Only ``context.range_adapter`` certifies a primitive against an actual retained
F09 publication. These records contain geometry support, never a trading rule
or a fitted estimate of reversal probability.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import date
from fractions import Fraction

from trading_research.errors import ContractError
from trading_research.foundations.calendar import FormationWindow, Session
from trading_research.foundations.intervals import IntervalGraph, NamedInterval
from trading_research.foundations.object_graph import Instrument
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


FIELDS = ("open", "high", "low", "close")
SUPPORT_STATUSES = ("observed", "partial", "ambiguous", "empty", "unavailable")


def _name(value):
    if type(value) is not str or not value or len(value.encode("utf8")) > 256:
        raise ContractError("bounded explicit range identity required")
    return value


def _integer(value, *, minimum=None):
    if type(value) is not int or minimum is not None and value < minimum:
        raise ContractError("exact range integer required")
    return value


def _identities(values):
    if type(values) is not tuple:
        raise ContractError("range provenance must be an immutable tuple")
    for value in values:
        _name(value)
    if len(set(values)) != len(values):
        raise ContractError("duplicate range provenance identity")


@dataclass(frozen=True, eq=False)
class ClockSelection:
    instrument: Instrument
    window: FormationWindow
    session: Session
    selected_at: int
    predecessor_of_session_version: str | None
    interval_graph: IntervalGraph
    named_interval: NamedInterval
    _calendar_receipt: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        if (type(self.instrument) is not Instrument or type(self.window) is not FormationWindow
                or type(self.session) is not Session or type(self.interval_graph) is not IntervalGraph
                or type(self.named_interval) is not NamedInterval):
            raise ContractError("range clock needs actual typed calendar and interval graph")
        timestamp(self.selected_at)
        node = self.named_interval
        if (self.interval_graph.known_at > self.selected_at or node.known_at > self.selected_at
                or self.session.known_at > self.selected_at
                or self.interval_graph.intervals.get(node.name) != node
                or len(node.spans) != 1
                or node.trading_dates != (self.session.trading_date,)
                or self.window.trading_date != self.session.trading_date
                or (self.window.start, self.window.end) != (node.spans[0].start, node.spans[0].end)
                or self.window.id != node.name or self.window.definition_version != node.version
                or self.window.clock_variant != node.clock_variant):
            raise ContractError("selected clock differs from its available named interval")
        if (not self.instrument.valid(self.window.start)
                or not self.instrument.valid(self.window.end - 1)):
            raise ContractError("formation crosses the exact raw instrument lifetime")
        if self.predecessor_of_session_version is not None:
            _name(self.predecessor_of_session_version)

    @property
    def formation_start(self):
        return self.window.start

    @property
    def formation_end(self):
        return self.window.end

    @property
    def calendar_version(self):
        return self.session.version

    @property
    def source_version(self):
        return self.named_interval.source_version

    @property
    def timezone_version(self):
        return self.named_interval.timezone_version

    @property
    def clock_id(self):
        """Stable measurement stream identity, excluding selection time."""
        return digest({"instrument": self.instrument.key, "window": self.window,
                       "session": self.session.version, "node": self.named_interval.version,
                       "graph": self.interval_graph.version})

    def record(self):
        return {"instrument": self.instrument, "window": self.window,
                "session": self.session, "selected_at": self.selected_at,
                "predecessor_of_session_version": self.predecessor_of_session_version,
                "interval_graph_version": self.interval_graph.version,
                "named_interval_version": self.named_interval.version}

    @property
    def version_id(self):
        return digest(self.record())

    def __eq__(self, other):
        return type(other) is ClockSelection and self.version_id == other.version_id

    def __hash__(self):
        return hash(self.version_id)


@dataclass(frozen=True)
class FieldSupport:
    field: str
    status: str
    reason: str
    source_versions: tuple[str, ...]

    def __post_init__(self):
        if self.field not in FIELDS or self.status not in SUPPORT_STATUSES:
            raise ContractError("unknown range field support")
        _name(self.reason)
        _identities(self.source_versions)
        if self.status == "observed" and not self.source_versions:
            raise ContractError("observed range field needs retained provenance")


@dataclass(frozen=True, eq=False)
class RangePrimitive:
    id: str
    version_id: str
    selection: ClockSelection
    publication_version_id: str
    source_definition_id: str
    reset_epoch: str
    revision: int
    supersedes: str | None
    observation_cut: int
    minimum_known_at: int
    published_at: int
    complete_observation_at: int | None
    open_ticks: int | None
    high_ticks: int | None
    low_ticks: int | None
    close_ticks: int | None
    observed_ohlc: tuple[int | None, int | None, int | None, int | None]
    first_event_at: int | None
    last_event_at: int | None
    coverage_complete: bool
    observed_duration: int
    coverage_version: str
    watermark_version: str | None
    source_event_ids: tuple[str, ...]
    source_content_versions: tuple[str, ...]
    correction_ids: tuple[str, ...]
    field_support: tuple[FieldSupport, ...]
    status: str
    _factory_receipt: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        if type(self.selection) is not ClockSelection:
            raise ContractError("range primitive requires a resolved clock selection")
        for value in (self.id, self.version_id, self.publication_version_id,
                      self.source_definition_id, self.reset_epoch, self.coverage_version):
            _name(value)
        for value in (self.supersedes, self.watermark_version):
            if value is not None:
                _name(value)
        _integer(self.revision, minimum=0)
        if (self.revision == 0) != (self.supersedes is None):
            raise ContractError("source ordinal and exact F09 predecessor disagree")
        for at in (self.observation_cut, self.minimum_known_at, self.published_at):
            timestamp(at)
        if self.minimum_known_at > self.observation_cut or self.observation_cut > self.published_at:
            raise ContractError("range causal clocks regress")
        for at in (self.complete_observation_at, self.first_event_at, self.last_event_at):
            if at is not None:
                timestamp(at)
        if self.complete_observation_at is not None and not self.selection.formation_end <= self.complete_observation_at <= self.published_at:
            raise ContractError("range completion lacks an available endpoint")
        if (type(self.observed_ohlc) is not tuple or len(self.observed_ohlc) != 4
                or any(v is not None and type(v) is not int for v in (*self.ohlc, *self.observed_ohlc))):
            raise ContractError("OHLC uses exact raw integer ticks or missingness")
        if (self.first_event_at is None) != (self.last_event_at is None):
            raise ContractError("observed range endpoints must be jointly present")
        if self.first_event_at is not None and not self.selection.formation_start <= self.first_event_at <= self.last_event_at < self.selection.formation_end:
            raise ContractError("observed events fall outside selected formation")
        if type(self.coverage_complete) is not bool:
            raise ContractError("explicit coverage state required")
        _integer(self.observed_duration, minimum=0)
        if self.observed_duration > self.selection.formation_end - self.selection.formation_start:
            raise ContractError("observed coverage exceeds formation")
        for ids in (self.source_event_ids, self.correction_ids):
            _identities(ids)
        if type(self.source_content_versions) is not tuple:
            raise ContractError("immutable source content tuple required")
        for content in self.source_content_versions:
            _name(content)
        if len(self.source_event_ids) != len(self.source_content_versions):
            raise ContractError("source rows and content identities must align")
        if (type(self.field_support) is not tuple or any(type(v) is not FieldSupport for v in self.field_support)
                or tuple(v.field for v in self.field_support) != FIELDS
                or self.status not in ("provisional", "final", "incomplete", "empty")):
            raise ContractError("complete canonical field support tuple required")
        for value, support in zip(self.ohlc, self.field_support):
            if (value is not None) != (support.status == "observed"):
                raise ContractError("primary price field must have exact observed support")
        if self.high_ticks is not None and self.low_ticks is not None and self.high_ticks < self.low_ticks:
            raise ContractError("range high below low")

    @property
    def ohlc(self):
        return self.open_ticks, self.high_ticks, self.low_ticks, self.close_ticks

    @property
    def instrument(self):
        return self.selection.instrument

    @property
    def formation_start(self):
        return self.selection.formation_start

    @property
    def formation_end(self):
        return self.selection.formation_end

    def support(self, name):
        if name not in FIELDS:
            raise ContractError("unknown range capability")
        return self.field_support[FIELDS.index(name)]

    def supports(self, *names):
        return all(self.support(name).status == "observed" for name in names)

    @property
    def width_ticks(self):
        return self.high_ticks - self.low_ticks if self.supports("high", "low") else None

    @property
    def price_percent(self):
        width = self.width_ticks
        return Fraction(width, self.open_ticks) if width is not None and self.open_ticks not in (None, 0) else None

    def record(self):
        return {f.name: (self.selection.record() if f.name == "selection" else getattr(self, f.name))
                for f in fields(self) if not f.name.startswith("_")}

    def __eq__(self, other):
        return type(other) is RangePrimitive and self.record() == other.record()

    def __hash__(self):
        return hash(self.version_id)
