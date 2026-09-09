"""Bounded shared bars from frozen raw-event prefixes.

Ordered summaries compose only in event order. Quotes, coarse observations and
allocated pieces retain their distinct measurement contracts. Portable restore
replays retained inputs and requests; a serialized output is never its own proof.
"""

from bisect import bisect_left
from dataclasses import asdict, dataclass, field, fields
from fractions import Fraction
import json
from types import MappingProxyType

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import Watermark, WindowCoverage
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import Ticks
from trading_research.measurements.tape import CorrectionImpact, Trade, TradeView
from trading_research.operations.artifacts import canonical_json, digest


def _name(value):
    try:
        valid = type(value) is str and bool(value) and len(value.encode()) <= 256
    except UnicodeError:
        valid = False
    if not valid:
        raise ContractError("a bounded nonempty semantic identity is required")
    return value


def _integer(value, *, minimum=None):
    if type(value) is not int or minimum is not None and value < minimum:
        raise ContractError("an exact integer inside the declared bounds is required")
    return value


def _identities(values):
    if type(values) is not tuple:
        raise ContractError("evidence identities must be an immutable tuple")
    for value in values:
        _name(value)
    if len(set(values)) != len(values):
        raise ContractError("evidence identities must be unique")


AUXILIARY_LIMIT = 4096


@dataclass(frozen=True)
class BarDomain:
    instrument: str
    measurement: str
    aggregation_unit: str
    price_unit: str = "raw_ticks"
    quantity_unit: str = "contracts"

    def __post_init__(self):
        for value in (self.instrument, self.measurement, self.aggregation_unit):
            _name(value)
        if self.price_unit != "raw_ticks" or self.quantity_unit != "contracts":
            raise ContractError("shared trade bars require exact raw ticks and contracts")

    @property
    def id(self):
        return digest(self)


@dataclass(frozen=True)
class BarLimits:
    max_events: int = 4096
    max_clocks: int = 32
    block_events: int = 32
    max_publications: int = 4096

    def __post_init__(self):
        for f in fields(self):
            _integer(getattr(self, f.name), minimum=1)
        if self.block_events > self.max_events:
            raise ContractError("a shared block cannot exceed retained event capacity")


@dataclass(frozen=True)
class BarDefinition:
    domain: BarDomain
    version: str
    calendar_id: str
    reset_id: str
    kind: str = "time"
    threshold: int | None = None

    def __post_init__(self):
        if type(self.domain) is not BarDomain:
            raise ContractError("bar definition requires an immutable raw domain")
        for value in (self.version, self.calendar_id, self.reset_id):
            _name(value)
        if type(self.kind) is not str or self.kind not in {"time", "events", "volume", "range"}:
            raise ContractError("unknown bar construction")
        if self.kind == "time":
            if self.threshold is not None:
                raise ContractError("time bars use explicit calendar intervals")
        else:
            _integer(self.threshold, minimum=1)

    @property
    def id(self):
        return digest(self)


def _trade(value, domain):
    if type(value) is not Trade:
        raise ContractError("only whole Trade observations enter the trade bar layer")
    for s in (value.id, value.source_content_version, value.instrument, value.aggregation_unit):
        _name(s)
    if (value.instrument != domain.instrument or value.aggregation_unit != domain.aggregation_unit
            or type(value.history_complete) is not bool
            or value.price is not None and type(value.price) is not Ticks
            or value.known_at < value.event_at):
        raise ContractError("trade instrument, measurement, history or availability mismatch")
    # Reconstruct to apply the original immutable record's scalar validation too.
    Trade.restore(value.record())
    return value


def _key(t):
    # ID ordering makes storage deterministic only. It never proves market order.
    return t.event_at, -1 if t.order is None else t.order, t.id


def _tie_exact(edge):
    return len(edge) <= 1 or (all(v[1] is not None for v in edge)
                            and len({v[1] for v in edge}) == len(edge))


def _edge_price(edge, *, terminal=False):
    if not edge:
        return None
    if _tie_exact(edge):
        return sorted(edge, key=lambda v: -1 if v[1] is None else v[1])[-1 if terminal else 0][2]
    prices = {v[2] for v in edge}
    return next(iter(prices)) if len(prices) == 1 else None


@dataclass(frozen=True)
class TradeSummary:
    domain: BarDomain
    event_ids: tuple[str, ...]
    content_versions: tuple[str, ...]
    first_at: int | None
    last_at: int | None
    first_edge: tuple[tuple[str, int | None, int | None], ...]
    last_edge: tuple[tuple[str, int | None, int | None], ...]
    high_ticks: int | None
    low_ticks: int | None
    volume: int
    priced_volume: int
    unpriced_volume: int
    sum_pv: int
    sum_p2v: int
    buy: int
    sell: int
    unknown: int
    history_complete: bool
    order_exact: bool
    cvd_high: int | None
    cvd_low: int | None
    minimum_known_at: int | None
    _certified: bool = field(default=False, init=False, repr=False, compare=False)

    def record(self):
        return {f.name: getattr(self, f.name) for f in fields(self) if not f.name.startswith("_")}

    @property
    def id(self):
        return digest(self.record())

    @property
    def prints(self):
        return len(self.event_ids)

    @property
    def open_ticks(self):
        return _edge_price(self.first_edge)

    @property
    def close_ticks(self):
        return _edge_price(self.last_edge, terminal=True)

    @property
    def signed(self):
        return self.buy - self.sell

    @property
    def signed_bounds(self):
        return (self.signed - self.unknown, self.signed + self.unknown) if self.history_complete else None

    @property
    def mean(self):
        return Fraction(self.sum_pv, self.priced_volume) if self.priced_volume else None

    @property
    def variance(self):
        return Fraction(self.sum_p2v, self.priced_volume) - self.mean ** 2 if self.priced_volume else None

    def cvd_ohlc(self, opening=0):
        if opening is None:
            return None
        _integer(opening)
        if self.cvd_high is None:
            return None
        return opening, opening + self.cvd_high, opening + self.cvd_low, opening + self.signed

    def statistic(self, name):
        if name not in {"mean", "variance", "sum_pv", "sum_p2v", "volume", "signed_bounds"}:
            raise DependencyUnavailable("ordered moments do not identify that statistic or forecast")
        return getattr(self, name)


def _summary(**values):
    result = TradeSummary(**values)
    object.__setattr__(result, "_certified", True)
    return result


def empty_summary(domain):
    if type(domain) is not BarDomain:
        raise ContractError("summary requires a typed raw domain")
    return _summary(domain=domain, event_ids=(), content_versions=(), first_at=None, last_at=None,
                    first_edge=(), last_edge=(), high_ticks=None, low_ticks=None, volume=0,
                    priced_volume=0, unpriced_volume=0, sum_pv=0, sum_p2v=0,
                    buy=0, sell=0, unknown=0, history_complete=True, order_exact=True,
                    cvd_high=0, cvd_low=0, minimum_known_at=None)


def summarize_trade(trade, domain):
    t = _trade(trade, domain)
    p = None if t.price is None else t.price.value
    edge = ((t.id, t.order, p),)
    exact_flow = t.history_complete and t.side is not None
    return _summary(domain=domain, event_ids=(t.id,), content_versions=(t.source_content_version,),
                    first_at=t.event_at, last_at=t.event_at, first_edge=edge, last_edge=edge,
                    high_ticks=p, low_ticks=p, volume=t.size,
                    priced_volume=t.size if p is not None else 0,
                    unpriced_volume=t.size if p is None else 0,
                    sum_pv=0 if p is None else p * t.size,
                    sum_p2v=0 if p is None else p * p * t.size,
                    buy=t.size if t.side == 1 else 0, sell=t.size if t.side == -1 else 0,
                    unknown=t.size if t.side is None else 0, history_complete=t.history_complete,
                    order_exact=True, cvd_high=max(0, t.signed) if exact_flow else None,
                    cvd_low=min(0, t.signed) if exact_flow else None, minimum_known_at=t.known_at)


def merge_summaries(left, right):
    """Concatenate two factory-created blocks, retaining ambiguous edge ties."""
    if any(type(v) is not TradeSummary or not v._certified for v in (left, right)):
        raise ContractError("restore retained source records before composing a portable summary")
    if left.domain != right.domain or set(left.event_ids).intersection(right.event_ids):
        raise ContractError("summary domain mismatch or repeated source evidence")
    if not left.prints:
        return right
    if not right.prints:
        return left
    if left.last_at > right.first_at:
        raise ContractError("summary concatenation regressed market event time")
    tie = left.last_at == right.first_at
    edge = left.last_edge + right.first_edge if tie else ()
    ordered_boundary = not tie or _tie_exact(edge)
    if tie and ordered_boundary:
        if max(v[1] for v in left.last_edge) >= min(v[1] for v in right.first_edge):
            raise ContractError("explicit sequence proves the supplied block order is wrong")
    order_exact = left.order_exact and right.order_exact and ordered_boundary
    history = left.history_complete and right.history_complete
    exact_flow = order_exact and history and left.unknown + right.unknown == 0
    first = left.first_edge + right.first_edge if tie and left.first_at == left.last_at else left.first_edge
    last = left.last_edge + right.last_edge if tie and right.first_at == right.last_at else right.last_edge
    highs = [v for v in (left.high_ticks, right.high_ticks) if v is not None]
    lows = [v for v in (left.low_ticks, right.low_ticks) if v is not None]
    additive = {n: getattr(left, n) + getattr(right, n) for n in
                ("volume", "priced_volume", "unpriced_volume", "sum_pv", "sum_p2v", "buy", "sell", "unknown")}
    return _summary(domain=left.domain, event_ids=left.event_ids + right.event_ids,
                    content_versions=left.content_versions + right.content_versions,
                    first_at=left.first_at, last_at=right.last_at, first_edge=first, last_edge=last,
                    high_ticks=max(highs, default=None), low_ticks=min(lows, default=None),
                    **additive, history_complete=history, order_exact=order_exact,
                    cvd_high=max(left.cvd_high, left.signed + right.cvd_high) if exact_flow else None,
                    cvd_low=min(left.cvd_low, left.signed + right.cvd_low) if exact_flow else None,
                    minimum_known_at=max(left.minimum_known_at, right.minimum_known_at))


def summarize(trades, domain):
    if type(trades) is not tuple:
        raise ContractError("summary inputs must be an immutable whole-event tuple")
    result = empty_summary(domain)
    for trade in sorted(trades, key=_key):
        result = merge_summaries(result, summarize_trade(trade, domain))
    return result


@dataclass(frozen=True)
class ResetMarker:
    id: str
    event_at: int
    known_at: int
    new_epoch_id: str

    def __post_init__(self):
        _name(self.id)
        _name(self.new_epoch_id)
        timestamp(self.event_at)
        timestamp(self.known_at)


@dataclass(frozen=True)
class WindowRequest:
    definition_id: str
    start: int
    end: int
    coverage: WindowCoverage
    watermark: Watermark | None = None

    def __post_init__(self):
        _name(self.definition_id)
        timestamp(self.start)
        timestamp(self.end)
        if (self.end <= self.start or type(self.coverage) is not WindowCoverage
                or self.coverage.start != self.start or self.coverage.end != self.end
                or self.watermark is not None and type(self.watermark) is not Watermark):
            raise ContractError("time request requires an exact calendar/coverage interval")


@dataclass(frozen=True)
class SharedCapture:
    domain: BarDomain
    cut: int
    admission_cursor: int
    prefix_id: str
    events: tuple[Trade, ...]
    leaves: tuple[TradeSummary, ...]
    blocks: tuple[TradeSummary, ...]
    block_offsets: tuple[tuple[int, int], ...]
    corrections: tuple[CorrectionImpact, ...]
    source_visits: int
    event_times: tuple[int, ...]
    block_ids: tuple[str, ...]
    admission_proof: str
    build_work: tuple[tuple[str, int], ...]
    _owner: object = field(default=None, init=False, repr=False, compare=False)


@dataclass(frozen=True)
class SharedBar:
    definition: BarDefinition
    interval: tuple[int, int]
    index: int | None
    reset_epoch: str
    state: str
    summary: TradeSummary
    observation_cut: int
    minimum_known_at: int
    published_at: int
    revision: int
    prefix_id: str
    admission_cursor: int
    coverage_complete: bool
    observed_duration: int | None
    coverage_version: str | None
    watermark_version: str | None
    correction_ids: tuple[str, ...]
    block_ids: tuple[str, ...]
    threshold_reached: bool
    overshoot: int | None
    opening_cvd: int | None
    _certified: bool = field(default=False, init=False, repr=False, compare=False)

    def __post_init__(self):
        if (type(self.definition) is not BarDefinition or type(self.summary) is not TradeSummary
                or not self.summary._certified or self.summary.domain != self.definition.domain
                or type(self.interval) is not tuple or len(self.interval) != 2):
            raise ContractError("publication needs typed compatible immutable bar evidence")
        for at in (*self.interval, self.observation_cut, self.minimum_known_at, self.published_at):
            timestamp(at)
        if (self.interval[0] >= self.interval[1] or self.minimum_known_at > self.observation_cut
                or self.observation_cut > self.published_at
                or self.summary.minimum_known_at is not None and self.summary.minimum_known_at > self.minimum_known_at
                or self.summary.prints and not self.interval[0] <= self.summary.first_at <= self.summary.last_at < self.interval[1]):
            raise ContractError("publication interval, source support or availability disagrees")
        _name(self.reset_epoch)
        _name(self.prefix_id)
        _integer(self.revision, minimum=0)
        _integer(self.admission_cursor, minimum=0)
        if self.index is not None:
            _integer(self.index, minimum=0)
        if self.opening_cvd is not None:
            _integer(self.opening_cvd)
        if self.observed_duration is not None:
            _integer(self.observed_duration, minimum=0)
            if self.observed_duration > self.interval[1] - self.interval[0]:
                raise ContractError("observed duration exceeds the bar interval")
        if any(type(v) is not bool for v in (self.coverage_complete, self.threshold_reached)):
            raise ContractError("bar support and threshold flags require explicit booleans")
        if type(self.state) is not str or self.state not in {"final", "provisional", "threshold", "reset_partial", "forming"}:
            raise ContractError("unknown publication state")
        if self.definition.kind == "time":
            if (self.index is not None or self.state not in {"final", "provisional"}
                    or self.threshold_reached or self.overshoot is not None or self.observed_duration is None
                    or self.coverage_version is None or self.opening_cvd is None
                    or self.state == "final" and (self.watermark_version is None or self.minimum_known_at < self.interval[1])):
                raise ContractError("time bar finality or support is inconsistent")
        elif (self.index is None or self.state not in {"threshold", "reset_partial", "forming"}
                or self.observed_duration is not None or self.coverage_version is not None or self.watermark_version is not None
                or self.threshold_reached != (self.state == "threshold")):
            raise ContractError("activity completion metadata is inconsistent")
        if self.threshold_reached:
            _integer(self.overshoot, minimum=0)
        elif self.overshoot is not None:
            raise ContractError("an unfinished threshold cannot report overshoot")
        if self.coverage_complete and (not self.summary.history_complete or self.summary.unpriced_volume
                or self.definition.kind == "time" and self.observed_duration != self.interval[1] - self.interval[0]):
            raise ContractError("complete coverage lacks supporting source evidence")
        for value in (self.coverage_version, self.watermark_version):
            if value is not None:
                _name(value)
        _identities(self.correction_ids)
        _identities(self.block_ids)

    @property
    def final(self):
        return self.state in {"final", "threshold", "reset_partial"}

    @property
    def bar_id(self):
        return digest([self.definition.id, self.interval, self.index, self.reset_epoch])

    def record(self):
        return {**{f.name: getattr(self, f.name) for f in fields(self) if f.name != "summary" and not f.name.startswith("_")},
                "summary": self.summary.record()}

    @property
    def version_id(self):
        # Arrival cursor is retained for audit/reconstruction. Unavailable future
        # arrivals do not change the semantic identity of the same eligible cut.
        return digest({k: v for k, v in self.record().items() if k != "admission_cursor"})

    def available(self, at, *, final_only=True):
        timestamp(at)
        if not self._certified or type(final_only) is not bool:
            raise ContractError("availability requires a retained factory publication")
        return self.published_at <= at and (self.final or not final_only)


def _shared_bar(*args, **kwargs):
    result = SharedBar(*args, **kwargs)
    object.__setattr__(result, "_certified", True)
    return result


@dataclass(frozen=True)
class ActivityResult:
    definition_id: str
    completed: tuple[SharedBar, ...]
    forming: SharedBar | None
    available: bool
    reason: str | None
    prefix_id: str
    published_at: int

    def __post_init__(self):
        _name(self.definition_id)
        _name(self.prefix_id)
        timestamp(self.published_at)
        if (type(self.completed) is not tuple or type(self.available) is not bool
                or any(type(v) is not SharedBar or not v._certified or not v.final for v in self.completed)
                or self.forming is not None and (type(self.forming) is not SharedBar or not self.forming._certified or self.forming.state != "forming")
                or self.available != (self.reason is None)
                or not self.available and (self.completed or self.forming is not None)):
            raise ContractError("activity result requires consistent immutable publications")
        if self.reason is not None:
            _name(self.reason)
        values = self.completed + (() if self.forming is None else (self.forming,))
        if any(v.definition.id != self.definition_id or v.prefix_id != self.prefix_id or v.published_at != self.published_at for v in values):
            raise ContractError("activity outputs do not share their captured definition/publication")

    def record(self):
        return {"definition_id": self.definition_id, "completed": [v.record() for v in self.completed],
                "forming": None if self.forming is None else self.forming.record(),
                "available": self.available, "reason": self.reason, "prefix_id": self.prefix_id,
                "published_at": self.published_at}


def _coverage_record(value):
    return asdict(value)


def _request_record(value):
    return {"definition_id": value.definition_id, "start": value.start, "end": value.end,
            "coverage": _coverage_record(value.coverage),
            "watermark": None if value.watermark is None else asdict(value.watermark)}


def _request_restore(value):
    c = value["coverage"]
    return WindowRequest(value["definition_id"], value["start"], value["end"],
                         WindowCoverage(**{**c, "observed_intervals": tuple(tuple(p) for p in c["observed_intervals"])}),
                         None if value["watermark"] is None else Watermark(**value["watermark"]))


class SharedBarEngine:
    """A finite immutable-prefix store with reusable shared event blocks."""

    __slots__ = ("_domain", "_definitions", "_limits", "_events", "_admissions", "_known",
                 "_removed", "_correction_records", "_history", "_publications", "_last_published",
                 "_block_cache", "_view_evidence", "_seeding_view", "_admission_proofs", "_activity_versions", "_stats",
                 "_window_publication_index", "_window_stream_heads")

    def __setattr__(self, name, value):
        if name in {"_domain", "_definitions", "_limits"} and hasattr(self, name):
            raise AttributeError("admitted shared-bar configuration is immutable")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError("shared-bar state slots cannot be deleted")

    def __init__(self, domain, definitions, *, limits=BarLimits()):
        if type(domain) is not BarDomain or type(limits) is not BarLimits or type(definitions) is not tuple:
            raise ContractError("shared engine needs immutable domain, clock tuple and bounds")
        if (not definitions or len(definitions) > limits.max_clocks
                or any(type(d) is not BarDefinition or d.domain != domain for d in definitions)
                or len({d.id for d in definitions}) != len(definitions)):
            raise ContractError("shared clocks are unique and must use one exact measurement domain")
        self._domain, self._definitions, self._limits = domain, definitions, limits
        self._events, self._admissions, self._removed, self._correction_records = {}, [], set(), {}
        self._known, self._last_published = None, None
        self._history, self._publications, self._block_cache = [], [], {}
        self._view_evidence, self._seeding_view = None, False
        self._admission_proofs = [digest([domain, "empty-admissions"])]
        self._activity_versions, self._stats = {}, {}
        self._window_publication_index, self._window_stream_heads = {}, {}

    @property
    def domain(self):
        return self._domain

    @property
    def definitions(self):
        return self._definitions

    @property
    def limits(self):
        return self._limits

    @property
    def event_count(self):
        return len(self._events)

    @property
    def publications(self):
        return tuple(self._publications)

    def window_publication(self, publication_version_id):
        """Return one retained time publication and its exact immutable request.

        The lookup visits one indexed publication, never a checkpoint or the
        complete history. Integrity work hashes this publication's own source
        identities and coverage spans; those costs are exposed in ``work``.
        The index is reconstructed by normal checked restore replay.
        """
        _name(publication_version_id)
        self._work("window_publication_index_lookups")
        entry = self._window_publication_index.get(publication_version_id)
        if entry is None:
            raise DependencyUnavailable("retained time publication is unavailable")
        bar, request, history_index, publication_index, proof, _ = entry
        self._work("window_publication_entries_examined")
        # The bar digest and retained-history digest each encode these IDs.
        self._work("window_publication_source_identities_hashed", 2 * len(bar.summary.event_ids))
        self._work("window_publication_source_identities_serialized_for_comparison", len(bar.summary.event_ids))
        self._work("window_publication_coverage_spans_hashed", len(request.coverage.observed_intervals))
        if (not bar._certified or self._publications[publication_index] is not bar
                or bar.version_id != publication_version_id
                or digest(self._history[history_index]) != proof
                or self._history[history_index]["request"] != _request_record(request)
                or self._history[history_index]["expected"] != json.loads(canonical_json(bar.record()))
                or request.definition_id != bar.definition.id
                or (request.start, request.end) != bar.interval
                or request.coverage.instrument != bar.definition.domain.instrument
                or request.coverage.source_version != bar.coverage_version
                or request.coverage.known_at > bar.observation_cut
                or (None if request.watermark is None else request.watermark.source_version) != bar.watermark_version):
            raise IntegrityError("retained publication/request source integrity changed")
        return bar, request

    def window_publication_predecessor(self, publication_version_id):
        """Exact previous SharedBar version ID in this retained time stream."""
        self.window_publication(publication_version_id)
        return self._window_publication_index[publication_version_id][5]

    @property
    def work(self):
        return MappingProxyType(dict(self._stats))

    def _work(self, name, amount=1):
        self._stats[name] = self._stats.get(name, 0) + amount

    def _retain_admission(self, record):
        proof = digest([self._admission_proofs[-1], record])
        self._work("admission_proof_operations_hashed")
        self._work("admission_proof_source_records_hashed", len(record["trades"]) if record["op"] == "add" else int(record["replacement"] is not None))
        self._admissions.append(record)
        self._admission_proofs.append(proof)
        self._history.append(record)

    def _definition(self, id, kind=None):
        value = next((d for d in self.definitions if d.id == id), None)
        if value is None or kind is not None and value.kind != kind:
            raise ContractError("unregistered clock/threshold; install a new definition and explicit reset")
        return value

    def add_many(self, trades):
        if (type(trades) is not tuple or len(trades) > self.limits.max_events
                or self._view_evidence is not None and not self._seeding_view):
            raise ContractError("admission needs a whole immutable batch; imported views stay frozen")
        staged, known = {}, self._known
        for value in trades:
            t = _trade(value, self.domain)
            old = staged.get(t.id, self._events.get(t.id))
            if old is not None:
                if old != t:
                    raise IntegrityError("conflicting source ID requires an explicit correction")
                continue
            if known is not None and t.known_at < known:
                raise ContractError("new event availability regressed")
            staged[t.id], known = t, t.known_at
        if len(self._events) + len(staged) > self.limits.max_events:
            raise ContractError("shared source retention exceeded")
        if not staged:
            return 0
        record = {"op": "add", "trades": [t.record() for t in staged.values()]}
        self._events.update(staged)
        self._known = known
        self._retain_admission(record)
        return len(staged)

    def add(self, trade):
        return bool(self.add_many((trade,)))

    def correct(self, *, id, original_id, known_at, reason, replacement=None):
        for s in (id, original_id, reason):
            _name(s)
        timestamp(known_at)
        if self._view_evidence is not None:
            raise ContractError("obtain a new frozen TradeView for a corrected imported state")
        if replacement is not None:
            _trade(replacement, self.domain)
        record = {"op": "correct", "id": id, "original_id": original_id, "known_at": known_at,
                  "reason": reason, "replacement": None if replacement is None else replacement.record()}
        if id in self._correction_records:
            if self._correction_records[id] != record:
                raise IntegrityError("correction ID content changed")
            return False
        if (original_id not in self._events or original_id in self._removed
                or self._known is not None and known_at < self._known
                or len(self._correction_records) >= self.limits.max_events
                or replacement is not None and (replacement.id in self._events
                    or replacement.known_at != known_at or len(self._events) >= self.limits.max_events)):
            raise ContractError("correction requires a current existing origin and a new bounded replacement")
        self._removed.add(original_id)
        if replacement is not None:
            self._events[replacement.id] = replacement
        self._known = known_at
        self._correction_records[id] = record
        self._retain_admission(record)
        return True

    def capture(self, cut):
        return self._capture(cut, len(self._admissions))

    def _capture(self, cut, cursor):
        timestamp(cut)
        _integer(cursor, minimum=0)
        if cursor > len(self._admissions):
            raise IntegrityError("capture cursor exceeds retained admissions")
        if self._view_evidence is not None and cut != self._view_evidence["cut"]:
            raise ContractError("a frozen external view cannot answer a different knowledge cut")
        current, all_rows, corrections, eligible_corrections = {}, {}, [], []
        scanned_rows = 0
        for r in self._admissions[:cursor]:
            if r["op"] == "add":
                for raw in r["trades"]:
                    scanned_rows += 1
                    t = self._events[raw["id"]]
                    all_rows[t.id] = t
                    if t.known_at <= cut:
                        current[t.id] = t
            else:
                before = all_rows[r["original_id"]]
                after = None if r["replacement"] is None else self._events[r["replacement"]["id"]]
                if after is not None:
                    scanned_rows += 1
                    all_rows[after.id] = after
                if r["known_at"] <= cut:
                    eligible_corrections.append(r)
                    current.pop(before.id, None)
                    if after is not None:
                        current[after.id] = after
                    corrections.append(CorrectionImpact(r["id"], r["known_at"], before.instrument,
                        before.event_at, None if after is None else after.instrument, None if after is None else after.event_at))
        if self._view_evidence is not None:
            corrections.extend(CorrectionImpact(**r) for r in self._view_evidence["corrections"])
        events = tuple(sorted(current.values(), key=_key))
        leaves = tuple(summarize_trade(t, self.domain) for t in events)
        blocks, offsets, new_cache, block_ids = [], [], {}, []
        built = compositions = copied = block_id_hash_items = 0
        for a in range(0, len(events), self.limits.block_events):
            b = min(a + self.limits.block_events, len(events))
            key = digest([self.domain.id, [digest(t.record()) for t in events[a:b]]])
            cached = self._block_cache.get(key)
            if cached is None:
                built += 1
                value = empty_summary(self.domain)
                for leaf in leaves[a:b]:
                    copied += 2 * (value.prints + leaf.prints)
                    value = merge_summaries(value, leaf)
                    compositions += 1
                value_id = value.id
                block_id_hash_items += value.prints * 2
            else:
                value, value_id = cached
            blocks.append(value)
            block_ids.append(value_id)
            offsets.append((a, b))
            new_cache[key] = (value, value_id)
        # Cache retains only this capture's bounded blocks. Immutable prior captures
        # and publications keep their own values; no historic output is changed.
        self._block_cache = new_cache
        eligible_rows = tuple(sorted((t for t in all_rows.values() if t.known_at <= cut), key=lambda t: (t.known_at, t.id)))
        prefix_id = digest([self.domain, eligible_rows,
                            sorted(eligible_corrections, key=lambda r: (r["known_at"], r["id"])), self._view_evidence])
        build_work = {"admission_operations_visited": cursor, "admitted_trade_records_visited": scanned_rows,
            "eligible_source_records_hashed": len(eligible_rows), "block_source_records_hashed": len(events),
            "leaf_summaries_created": len(leaves), "block_summaries_built": built,
            "block_compositions": compositions, "lineage_identity_items_copied": copied,
            "block_id_identity_items_hashed": block_id_hash_items, "event_timestamp_index_entries": len(events)}
        for name, amount in build_work.items():
            self._work("capture_" + name, amount)
        result = SharedCapture(self.domain, cut, cursor, prefix_id, events, leaves, tuple(blocks),
                               tuple(offsets), tuple(corrections), len(events), tuple(t.event_at for t in events),
                               tuple(block_ids), self._admission_proofs[cursor], tuple(sorted(build_work.items())))
        object.__setattr__(result, "_owner", self)
        return result

    def _check_capture(self, capture):
        if type(capture) is not SharedCapture or capture._owner is not self:
            raise ContractError("capture belongs to another engine or lacks retained-prefix proof")
        if (capture.domain != self.domain or type(capture.admission_cursor) is not int
                or not 0 <= capture.admission_cursor < len(self._admission_proofs)
                or capture.admission_proof != self._admission_proofs[capture.admission_cursor]):
            raise IntegrityError("captured raw prefix changed")

    def query(self, capture, *, start, end):
        """Return a summary, used block IDs and measured composition work."""
        self._check_capture(capture)
        timestamp(start)
        timestamp(end)
        if end <= start or start > capture.cut:
            raise ContractError("query requires a nonempty observable half-open window")
        if self._view_evidence is not None and not self._view_evidence["start"] <= start < end <= self._view_evidence["end"]:
            raise DependencyUnavailable("query exceeds the imported source-view interval")
        # Binary searches are on the captured event index; full blocks need no
        # further source reads. Leaf arithmetic was shared at capture time.
        left = bisect_left(capture.event_times, start)
        right = bisect_left(capture.event_times, min(end, capture.cut + 1))
        result, ids, work = empty_summary(self.domain), [], 0
        self._work("query_binary_searches", 2)
        copied = 0
        for index in range(left // self.limits.block_events, (right - 1) // self.limits.block_events + 1 if right > left else left // self.limits.block_events):
            block, (a, b) = capture.blocks[index], capture.block_offsets[index]
            self._work("query_blocks_visited")
            if left <= a and b <= right:
                copied += 2 * (result.prints + block.prints)
                result = merge_summaries(result, block)
                work += 1
            else:
                for leaf in capture.leaves[max(a, left):min(b, right)]:
                    copied += 2 * (result.prints + leaf.prints)
                    result = merge_summaries(result, leaf)
                    work += 1
            ids.append(capture.block_ids[index])
        self._work("query_compositions", work)
        self._work("query_lineage_identity_items_copied", copied)
        return result, tuple(ids), work

    def _prepare_publication(self, capture, published_at):
        self._check_capture(capture)
        timestamp(published_at)
        if (published_at < capture.cut or self._last_published is not None
                and published_at < self._last_published):
            raise ContractError("publication precedes its captured cut or prior actual completion")

    def publish_window(self, capture, request, *, published_at, opening_cvd=0):
        self._prepare_publication(capture, published_at)
        if type(request) is not WindowRequest:
            raise ContractError("time publication requires an immutable request")
        definition = self._definition(request.definition_id, "time")
        _integer(opening_cvd)
        coverage, watermark = request.coverage, request.watermark
        if coverage.instrument != self.domain.instrument or coverage.known_at > capture.cut:
            raise DependencyUnavailable("required price coverage is not available at the captured cut")
        summary, block_ids, _ = self.query(capture, start=request.start, end=request.end)
        final = watermark is not None and watermark.known_at <= capture.cut and watermark.through_event_at >= request.end
        impacts = tuple(c for c in capture.corrections if any(i == self.domain.instrument and at is not None
            and request.start <= at < request.end for i, at in
            ((c.before_instrument, c.before_event_at), (c.after_instrument, c.after_event_at))))
        minimum = max([coverage.known_at, request.start, *([summary.minimum_known_at] if summary.prints else []),
                       *(c.known_at for c in impacts), *([request.end, watermark.known_at] if final else [])])
        prior = [v for v in self._publications if isinstance(v, SharedBar)
                 and v.definition.id == definition.id and v.interval == (request.start, request.end)]
        if prior and (capture.cut < prior[-1].observation_cut
                      or capture.admission_cursor < prior[-1].admission_cursor or prior[-1].final and not final):
            raise ContractError("a new time-bar version regressed its observation cut or finality")
        value = _shared_bar(definition, (request.start, request.end), None, definition.reset_id,
            "final" if final else "provisional", summary, capture.cut, minimum, published_at, len(prior),
            capture.prefix_id, capture.admission_cursor,
            coverage.complete and summary.history_complete and summary.unpriced_volume == 0,
            coverage.observed_duration, coverage.source_version, None if watermark is None else watermark.source_version,
            tuple(c.id for c in impacts), block_ids, False, None, opening_cvd)
        if len(self._publications) >= self.limits.max_publications:
            raise ContractError("published bar retention exceeded")
        record = {"op": "window", "cursor": capture.admission_cursor, "cut": capture.cut,
                  "request": _request_record(request), "published_at": published_at,
                  "opening_cvd": opening_cvd, "expected": json.loads(canonical_json(value.record()))}
        version_id = value.version_id
        predecessor = self._window_stream_heads.get(value.bar_id)
        entry = (value, request, len(self._history), len(self._publications), digest(record), predecessor)
        self._publications.append(value)
        self._last_published = published_at
        self._history.append(record)
        self._window_publication_index[version_id] = entry
        self._window_stream_heads[value.bar_id] = version_id
        self._work("window_publication_index_entries_retained")
        return value

    def publish_activity(self, capture, definition_id, *, published_at, resets=(), opening_cvd=0):
        return self.publish_activities(capture, (definition_id,), published_at=published_at,
                                       resets=resets, opening_cvd=opening_cvd)[0]

    def publish_activities(self, capture, definition_ids, *, published_at, resets=(), opening_cvd=0):
        """Dispatch each captured whole event once to the bounded active clocks.

        Arithmetic and source-identity composition per clock are both counted.
        No result is published unless all requested clocks fit the retained bound.
        """
        self._prepare_publication(capture, published_at)
        _integer(opening_cvd)
        if (type(definition_ids) is not tuple or not definition_ids or len(definition_ids) > self.limits.max_clocks
                or any(type(id) is not str for id in definition_ids) or len(set(definition_ids)) != len(definition_ids)):
            raise ContractError("activity dispatch requires unique bounded clock identities")
        definitions = tuple(self._definition(id) for id in definition_ids)
        if any(d.kind == "time" for d in definitions) or type(resets) is not tuple or any(type(r) is not ResetMarker for r in resets):
            raise ContractError("activity publication requires whole-event clocks and immutable resets")
        if (len(resets) > self.limits.max_events or len({r.id for r in resets}) != len(resets)
                or len({r.new_epoch_id for r in resets}) != len(resets)
                or any(r.new_epoch_id in {d.reset_id for d in definitions} or r.known_at > capture.cut or r.event_at > capture.cut for r in resets)
                or any(a.event_at >= b.event_at for a, b in zip(resets, resets[1:]))):
            raise ContractError("reset identities, order, epoch or availability are invalid")
        total = empty_summary(self.domain)
        for block in capture.blocks:
            self._work("activity_support_lineage_items_copied", 2 * (total.prints + block.prints))
            total = merge_summaries(total, block)
            self._work("activity_support_block_compositions")
        states = []
        staged_bars = 0
        for definition in definitions:
            prior = self._activity_versions.get(definition.id)
            if prior and (capture.cut < prior[0] or capture.admission_cursor < prior[1]):
                raise ContractError("activity publication regressed its retained input cut or prefix cursor")
            reason = ("unordered_or_missing_history" if not total.order_exact or not total.history_complete else
                      "unpriced_range_threshold" if definition.kind == "range" and total.unpriced_volume else None)
            states.append({"definition": definition, "completed": [], "pending": empty_summary(self.domain),
                           "epoch": definition.reset_id, "carry": opening_cvd, "reset_known": None,
                           "index": 0, "reason": reason, "revision": 0 if prior is None else prior[2] + 1})

        def mass(summary, definition):
            if definition.kind == "events":
                return summary.prints
            if definition.kind == "volume":
                return summary.volume
            return summary.high_ticks - summary.low_ticks

        def make(state, status, reached, end=None):
            nonlocal staged_bars
            summary, definition = state["pending"], state["definition"]
            if not summary.prints:
                return None
            if len(self._publications) + staged_bars >= self.limits.max_publications:
                raise ContractError("published activity-bar retention exceeded")
            endpoint = timestamp(summary.last_at + 1 if end is None else end)
            minimum = max(summary.minimum_known_at, state["reset_known"] if state["reset_known"] is not None else summary.minimum_known_at)
            value = _shared_bar(definition, (summary.first_at, endpoint), state["index"], state["epoch"], status,
                summary, capture.cut, minimum, published_at, state["revision"], capture.prefix_id,
                capture.admission_cursor, summary.history_complete and summary.unpriced_volume == 0,
                None, None, None, tuple(c.id for c in capture.corrections), capture.block_ids,
                reached, mass(summary, definition) - definition.threshold if reached else None, state["carry"])
            self._work("activity_publication_block_references", len(capture.block_ids))
            self._work("activity_publication_source_identity_references", summary.prints)
            staged_bars += 1
            return value

        def reset(marker):
            for state in states:
                if state["reason"] is not None:
                    continue
                state["reset_known"] = max(marker.event_at, marker.known_at)
                value = make(state, "reset_partial", False, marker.event_at)
                if value is not None:
                    state["completed"].append(value)
                    state["index"] += 1
                state["pending"], state["carry"], state["epoch"] = empty_summary(self.domain), 0, marker.new_epoch_id
                self._work("activity_reset_clock_updates")

        reset_index = 0
        for event, leaf in zip(capture.events, capture.leaves):
            self._work("activity_source_dispatches")
            while reset_index < len(resets) and resets[reset_index].event_at <= event.event_at:
                reset(resets[reset_index])
                reset_index += 1
            for state in states:
                if state["reason"] is not None:
                    continue
                pending = state["pending"]
                self._work("activity_lineage_identity_items_copied", 2 * (pending.prints + leaf.prints))
                pending = merge_summaries(pending, leaf)
                state["pending"] = pending
                self._work("activity_clock_compositions")
                if mass(pending, state["definition"]) >= state["definition"].threshold:
                    state["completed"].append(make(state, "threshold", True))
                    state["index"] += 1
                    state["carry"] = (None if state["carry"] is None or pending.unknown or not pending.history_complete
                                      else state["carry"] + pending.signed)
                    state["pending"] = empty_summary(self.domain)
        while reset_index < len(resets):
            reset(resets[reset_index])
            reset_index += 1
        results, publications = [], []
        for state in states:
            forming = make(state, "forming", False) if state["reason"] is None else None
            result = ActivityResult(state["definition"].id, tuple(state["completed"]), forming,
                                    state["reason"] is None, state["reason"], capture.prefix_id, published_at)
            results.append(result)
            values = result.completed + (() if forming is None else (forming,))
            publications.extend(values if values else (result,))
        if len(self._publications) + len(publications) > self.limits.max_publications:
            raise ContractError("published activity-bar retention exceeded")
        record = {"op": "activities", "cursor": capture.admission_cursor, "cut": capture.cut,
            "definition_ids": list(definition_ids), "published_at": published_at, "resets": [asdict(r) for r in resets],
            "opening_cvd": opening_cvd, "expected": json.loads(canonical_json([r.record() for r in results]))}
        self._publications.extend(publications)
        self._last_published = published_at
        for state in states:
            self._activity_versions[state["definition"].id] = (capture.cut, capture.admission_cursor, state["revision"])
        self._history.append(record)
        return tuple(results)

    def asof(self, *, bar_id, cut, final_only=False):
        _name(bar_id)
        timestamp(cut)
        self._work("publication_asof_entries_examined", len(self._publications))
        values = [v for v in self._publications if isinstance(v, SharedBar) and v.bar_id == bar_id
                  and v.available(cut, final_only=final_only)]
        return values[-1] if values else None

    @staticmethod
    def _view_metadata(value, domain, limits):
        if (type(value) is not dict or set(value) != {"start", "end", "cut", "corrections", "rows_hash"}
                or type(value["corrections"]) is not list or len(value["corrections"]) > limits.max_events):
            raise ContractError("imported view evidence has an invalid bounded schema")
        start, end, cut = (timestamp(value[k]) for k in ("start", "end", "cut"))
        sha = value["rows_hash"]
        if (start >= end or cut < start or type(sha) is not str or len(sha) != 64
                or any(c not in "0123456789abcdef" for c in sha)):
            raise ContractError("imported view interval or source hash is invalid")
        impacts = []
        for raw in value["corrections"]:
            if type(raw) is not dict:
                raise ContractError("imported correction evidence requires an exact record")
            impact = CorrectionImpact(**raw)
            _name(impact.id)
            for instrument in (impact.before_instrument, impact.after_instrument):
                if instrument is not None:
                    _name(instrument)
            if (impact.known_at > cut or not any(instrument == domain.instrument and at is not None and start <= at < end
                    for instrument, at in ((impact.before_instrument, impact.before_event_at),
                                           (impact.after_instrument, impact.after_event_at)))):
                raise ContractError("imported correction falls outside the available requested source view")
            impacts.append(impact)
        if len({c.id for c in impacts}) != len(impacts):
            raise IntegrityError("imported correction identities repeat")
        return {"start": start, "end": end, "cut": cut, "rows_hash": sha,
                "corrections": [asdict(c) for c in sorted(impacts, key=lambda c: (c.known_at, c.id))]}

    def _validate_imported_rows(self):
        if self._view_evidence is None:
            return
        evidence = self._view_evidence
        rows = tuple(sorted(self._events.values(), key=_key))
        if (len(self._admissions) > 1 or self._correction_records
                or any(not evidence["start"] <= t.event_at < evidence["end"] or t.known_at > evidence["cut"] for t in rows)
                or digest(rows) != evidence["rows_hash"]):
            raise IntegrityError("imported raw rows differ from retained interval, availability or canonical hash")

    @classmethod
    def from_trade_view(cls, view: TradeView, domain, definitions, *, start, end, cut, limits=BarLimits()):
        result = cls(domain, definitions, limits=limits)
        timestamp(start)
        timestamp(end)
        timestamp(cut)
        if start >= end or cut < start:
            raise ContractError("imported view requires a captured interval")
        rows = view.asof(instrument=domain.instrument, cut=cut, start=start, end=end)
        changes = view.changes(instrument=domain.instrument, cut=cut, start=start, end=end)
        if (type(rows) is not tuple or type(changes) is not tuple or len(rows) > limits.max_events or len(changes) > limits.max_events
                or any(type(c) is not CorrectionImpact or c.known_at > cut for c in changes)
                or any(type(t) is not Trade or not start <= t.event_at < end or t.known_at > cut for t in rows)):
            raise ContractError("external view returned facts beyond the frozen input contract")
        for row in rows:
            _trade(row, domain)
        if len({t.id for t in rows}) != len(rows):
            raise IntegrityError("external view repeats a source identity")
        result.add_many(tuple(sorted(rows, key=lambda t: (t.known_at, t.id))))
        result._view_evidence = cls._view_metadata({"start": start, "end": end, "cut": cut,
            "corrections": [asdict(c) for c in changes], "rows_hash": digest(tuple(sorted(rows, key=_key)))}, domain, limits)
        result._validate_imported_rows()
        return result

    def checkpoint(self):
        return canonical_json({"schema": "shared-bars-v1", "domain": self.domain,
            "definitions": self.definitions, "limits": self.limits, "view_evidence": self._view_evidence,
            "history": self._history})

    @classmethod
    def restore(cls, payload, *, expected_domain=None, expected_definitions=None, expected_limits=None):
        if type(payload) is not bytes:
            raise ContractError("checkpoint requires immutable canonical bytes")
        try:
            p = json.loads(payload)
            if p["schema"] != "shared-bars-v1":
                raise ContractError("incompatible shared-bar checkpoint")
            domain, limits = BarDomain(**p["domain"]), BarLimits(**p["limits"])
            definitions = tuple(BarDefinition(**{**d, "domain": BarDomain(**d["domain"])}) for d in p["definitions"])
            if ((expected_domain is not None and expected_domain != domain)
                    or expected_definitions is not None and expected_definitions != definitions
                    or expected_limits is not None and expected_limits != limits):
                raise IntegrityError("restored immutable semantic configuration changed")
            result = cls(domain, definitions, limits=limits)
            result._view_evidence = (None if p["view_evidence"] is None else cls._view_metadata(p["view_evidence"], domain, limits))
            result._seeding_view = True
            if type(p["history"]) is not list or len(p["history"]) > limits.max_events * 2 + limits.max_publications:
                raise IntegrityError("shared-bar journal exceeds its admitted operation bound")
            for r in p["history"]:
                if r["op"] == "add":
                    result.add_many(tuple(Trade.restore(t) for t in r["trades"]))
                elif r["op"] == "correct":
                    result.correct(**{k: (None if v is None else Trade.restore(v)) if k == "replacement" else v
                                      for k, v in r.items() if k != "op"})
                elif r["op"] in {"window", "activities"}:
                    result._validate_imported_rows()
                    capture = result._capture(r["cut"], r["cursor"])
                    if r["op"] == "window":
                        value = result.publish_window(capture, _request_restore(r["request"]),
                            published_at=r["published_at"], opening_cvd=r["opening_cvd"])
                    else:
                        values = result.publish_activities(capture, tuple(r["definition_ids"]), published_at=r["published_at"],
                            resets=tuple(ResetMarker(**v) for v in r["resets"]), opening_cvd=r["opening_cvd"])
                    restored_record = value.record() if r["op"] == "window" else [v.record() for v in values]
                    if json.loads(canonical_json(restored_record)) != r["expected"]:
                        raise IntegrityError("restored arithmetic, publication or lineage failed reconstruction")
                else:
                    raise IntegrityError("unknown shared-bar journal operation")
            result._seeding_view = False
            result._validate_imported_rows()
            if result.checkpoint() != payload:
                raise IntegrityError("noncanonical or incomplete shared-bar checkpoint")
            return result
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise IntegrityError("malformed shared-bar checkpoint") from exc


@dataclass(frozen=True)
class QuotePoint:
    id: str
    source_version: str
    instrument: str
    event_at: int
    known_at: int
    bid_ticks: int | None
    ask_ticks: int | None
    order: int | None = None

    def __post_init__(self):
        for s in (self.id, self.source_version, self.instrument):
            _name(s)
        timestamp(self.event_at)
        timestamp(self.known_at)
        if self.known_at < self.event_at:
            raise ContractError("quote was not yet observable")
        for v in (self.bid_ticks, self.ask_ticks):
            if v is not None:
                _integer(v)
        if self.order is not None:
            _integer(self.order, minimum=0)


def _quote_prices(points, attribute):
    if not points:
        return None, None, None, None
    first_at, last_at = points[0].event_at, points[-1].event_at
    first = tuple((p.id, p.order, getattr(p, attribute)) for p in points if p.event_at == first_at)
    last = tuple((p.id, p.order, getattr(p, attribute)) for p in points if p.event_at == last_at)
    priced = [getattr(p, attribute) for p in points if getattr(p, attribute) is not None]
    return _edge_price(first), max(priced, default=None), min(priced, default=None), _edge_price(last, terminal=True)


@dataclass(frozen=True)
class QuoteBar:
    instrument: str
    definition_id: str
    start: int
    end: int
    cut: int
    published_at: int
    points: tuple[QuotePoint, ...]

    def __post_init__(self):
        _name(self.instrument)
        _name(self.definition_id)
        for at in (self.start, self.end, self.cut, self.published_at):
            timestamp(at)
        if (self.start >= self.end or self.cut < self.start or self.published_at < self.cut
                or type(self.points) is not tuple or len(self.points) > AUXILIARY_LIMIT
                or any(type(p) is not QuotePoint or p.instrument != self.instrument
                       or not self.start <= p.event_at < self.end or p.known_at > self.cut for p in self.points)
                or len({p.id for p in self.points}) != len(self.points)
                or self.points != tuple(sorted(self.points, key=lambda p: (p.event_at, -1 if p.order is None else p.order, p.id)))):
            raise ContractError("quote publication lacks bounded ordered source support")

    @property
    def bid_ohlc(self):
        return _quote_prices(self.points, "bid_ticks")

    @property
    def ask_ohlc(self):
        return _quote_prices(self.points, "ask_ticks")

    @property
    def traded_volume(self):
        return None

    @property
    def cvd(self):
        return None

    @property
    def id(self):
        return digest(self)


def quote_bar(points, *, instrument, definition_id, start, end, cut, published_at):
    _name(instrument)
    _name(definition_id)
    for at in (start, end, cut, published_at):
        timestamp(at)
    if (type(points) is not tuple or len(points) > AUXILIARY_LIMIT or end <= start or cut < start or published_at < cut
            or any(type(p) is not QuotePoint or p.instrument != instrument for p in points)
            or len({p.id for p in points}) != len(points)):
        raise ContractError("quote bars require unique quote observations and a frozen interval")
    values = tuple(sorted((p for p in points if start <= p.event_at < end and p.known_at <= cut),
                          key=lambda p: (p.event_at, -1 if p.order is None else p.order, p.id)))
    return QuoteBar(instrument, definition_id, start, end, cut, published_at, values)


@dataclass(frozen=True)
class CoarseBar:
    id: str
    source_version: str
    instrument: str
    measurement: str
    start: int
    end: int
    known_at: int
    final: bool
    ohlc: tuple[int | None, int | None, int | None, int | None]
    volume: int | None
    buy: int | None = None
    sell: int | None = None
    unknown: int | None = None
    body_envelope: tuple[int, int] | None = None
    quantity_kind: str = "disjoint_trade_volume"

    def __post_init__(self):
        for s in (self.id, self.source_version, self.instrument, self.measurement):
            _name(s)
        for at in (self.start, self.end, self.known_at):
            timestamp(at)
        if (self.start >= self.end or self.known_at < self.start or type(self.final) is not bool
                or self.final and self.known_at < self.end
                or type(self.ohlc) is not tuple or len(self.ohlc) != 4):
            raise ContractError("coarse bar identity, interval or finality is invalid")
        for price in self.ohlc:
            if price is not None:
                _integer(price)
        o, h, l, c = self.ohlc
        if ((h is None) != (l is None) or h is None and (o is not None or c is not None)
                or h is not None and (h < l or any(p is not None and not l <= p <= h for p in (o, c)))):
            raise ContractError("coarse observed price support is inconsistent")
        for v in (self.volume, self.buy, self.sell, self.unknown):
            if v is not None:
                _integer(v, minimum=0)
        if len({v is None for v in (self.buy, self.sell, self.unknown)}) > 1:
            raise ContractError("coarse signed totals require all three support categories")
        if self.buy is not None and self.volume != self.buy + self.sell + self.unknown:
            raise ContractError("coarse side totals do not conserve reported traded volume")
        if self.body_envelope is not None:
            if type(self.body_envelope) is not tuple or len(self.body_envelope) != 2:
                raise ContractError("constituent body envelope must be an explicit exact pair")
            for p in self.body_envelope:
                _integer(p)
            if (h is None or not l <= self.body_envelope[0] <= self.body_envelope[1] <= h
                    or any(p is not None and not self.body_envelope[0] <= p <= self.body_envelope[1] for p in (o, c))):
                raise ContractError("body envelope exceeds observed extrema")
        if type(self.quantity_kind) is not str or self.quantity_kind not in {"disjoint_trade_volume", "daily_oi_delta", "daily_cumulative_volume"}:
            raise ContractError("unknown coarse source quantity semantics")

    @property
    def version_id(self):
        return digest(self)


@dataclass(frozen=True)
class CoarseAggregate:
    instrument: str
    measurement: str
    start: int
    end: int
    cut: int
    source_versions: tuple[str, ...]
    ohlc: tuple[int | None, int | None, int | None, int | None]
    volume: int | None
    signed_endpoint: int | None
    body_envelope: tuple[int, int] | None
    coverage_complete: bool
    known_signed_mass: int | None
    unknown_mass: int | None

    def __post_init__(self):
        _name(self.instrument)
        _name(self.measurement)
        for at in (self.start, self.end, self.cut):
            timestamp(at)
        _identities(self.source_versions)
        if (self.start >= self.end or type(self.coverage_complete) is not bool
                or type(self.ohlc) is not tuple or len(self.ohlc) != 4):
            raise ContractError("coarse aggregate identity or support is malformed")
        for value in (*self.ohlc, self.signed_endpoint, self.known_signed_mass):
            if value is not None:
                _integer(value)
        for value in (self.volume, self.unknown_mass):
            if value is not None:
                _integer(value, minimum=0)
        if ((self.known_signed_mass is None) != (self.unknown_mass is None)
                or self.signed_endpoint != (self.known_signed_mass if self.unknown_mass == 0 else None)):
            raise ContractError("coarse signed endpoint cannot invent unknown source direction")
        if self.body_envelope is not None:
            if type(self.body_envelope) is not tuple or len(self.body_envelope) != 2:
                raise ContractError("coarse body support needs an immutable endpoint pair")
            for value in self.body_envelope:
                _integer(value)
        o, h, l, c = self.ohlc
        if ((h is None) != (l is None) or h is None and (o is not None or c is not None)
                or h is not None and (h < l or any(p is not None and not l <= p <= h for p in (o, c)))
                or self.body_envelope is not None and (h is None or not l <= self.body_envelope[0] <= self.body_envelope[1] <= h
                    or any(p is not None and not self.body_envelope[0] <= p <= self.body_envelope[1] for p in (o, c)))):
            raise ContractError("coarse aggregate price or body support is inconsistent")
        if self.known_signed_mass is not None and (self.volume is None or abs(self.known_signed_mass) + self.unknown_mass > self.volume):
            raise ContractError("coarse aggregate signed support exceeds reported mass")

    @property
    def signed_bounds(self):
        if self.unknown_mass is None or not self.coverage_complete:
            return None
        return self.known_signed_mass - self.unknown_mass, self.known_signed_mass + self.unknown_mass

    @property
    def cvd_high(self):
        return None

    @property
    def cvd_low(self):
        return None

    @property
    def id(self):
        return digest(self)

    def require_body_envelope(self):
        if self.body_envelope is None:
            raise DependencyUnavailable("an opaque aggregate does not retain constituent candle bodies")
        return self.body_envelope


def merge_coarse_bars(bars, *, instrument, measurement, start, end, cut):
    """Merge wholly contained final source bars; never prorate a straddler."""
    for s in (instrument, measurement):
        _name(s)
    for at in (start, end, cut):
        timestamp(at)
    if start >= end or type(bars) is not tuple or len(bars) > AUXILIARY_LIMIT or any(type(b) is not CoarseBar for b in bars):
        raise ContractError("coarse merge requires explicit nonempty target bounds and typed bars")
    unique = {}
    for b in bars:
        if b.instrument != instrument or b.measurement != measurement or b.quantity_kind != "disjoint_trade_volume":
            raise ContractError("native reconciliation needs the same raw instrument, measure and disjoint filter")
        if b.id in unique and unique[b.id] != b:
            raise IntegrityError("coarse source identity changed without a revision")
        unique[b.id] = b
    values = sorted((b for b in unique.values() if b.start < end and b.end > start), key=lambda b: b.start)
    if any(not start <= b.start < b.end <= end for b in values):
        raise DependencyUnavailable("opaque source bar straddles the requested boundary")
    if any(not b.final or b.known_at > cut for b in values):
        raise DependencyUnavailable("coarse bar is not final and available at the captured cut")
    if any(a.end > b.start for a, b in zip(values, values[1:])):
        raise ContractError("coarse source intervals overlap and would double count")
    highs = [b.ohlc[1] for b in values if b.ohlc[1] is not None]
    lows = [b.ohlc[2] for b in values if b.ohlc[2] is not None]
    bodies = [b.body_envelope for b in values]
    body = (min(p[0] for p in bodies), max(p[1] for p in bodies)) if bodies and all(p is not None for p in bodies) else None
    complete = bool(values) and values[0].start == start and values[-1].end == end and all(a.end == b.start for a, b in zip(values, values[1:]))
    signed = sum(b.buy - b.sell for b in values) if values and all(b.buy is not None for b in values) else None
    unknown = sum(b.unknown for b in values) if signed is not None else None
    return CoarseAggregate(instrument, measurement, start, end, cut, tuple(b.version_id for b in values),
        (values[0].ohlc[0] if values else None, max(highs, default=None), min(lows, default=None),
         values[-1].ohlc[3] if values else None),
        sum(b.volume for b in values) if all(b.volume is not None for b in values) else None,
        signed if unknown == 0 else None, body, complete, signed, unknown)


@dataclass(frozen=True)
class QuantityObservation:
    id: str
    source_version: str
    instrument: str
    quantity_kind: str
    value: int
    known_at: int

    def __post_init__(self):
        for s in (self.id, self.source_version, self.instrument):
            _name(s)
        _integer(self.value)
        timestamp(self.known_at)
        if type(self.quantity_kind) is not str or self.quantity_kind not in {"daily_oi_delta", "daily_cumulative_volume", "disjoint_trade_volume"}:
            raise ContractError("source quantity must retain its aggregation semantics")


def unique_quantity_observations(values):
    if type(values) is not tuple or len(values) > AUXILIARY_LIMIT or any(type(v) is not QuantityObservation for v in values):
        raise ContractError("quantity lineage requires immutable typed observations")
    result = {}
    for v in values:
        if v.id in result and result[v.id] != v:
            raise IntegrityError("observation identity reused with different content")
        result[v.id] = v
    return tuple(result.values())


def disjoint_trade_volume(values, *, instrument):
    _name(instrument)
    rows = unique_quantity_observations(values)
    if any(v.instrument != instrument or v.quantity_kind != "disjoint_trade_volume" or v.value < 0 for v in rows):
        raise DependencyUnavailable("OI or cumulative source fields are not disjoint underlying trades")
    return sum(v.value for v in rows)


@dataclass(frozen=True)
class TradeAllocation:
    original_id: str
    original_version: str
    part_index: int
    size: int
    known_at: int

    def __post_init__(self):
        _name(self.original_id)
        _name(self.original_version)
        _integer(self.part_index, minimum=0)
        _integer(self.size, minimum=1)
        timestamp(self.known_at)


@dataclass(frozen=True)
class AllocationPlan:
    original: Trade
    parts: tuple[TradeAllocation, ...]

    def __post_init__(self):
        if type(self.original) is not Trade or type(self.parts) is not tuple or not self.parts:
            raise ContractError("allocation retains one original whole trade")
        _trade(self.original, BarDomain(self.original.instrument, self.original.aggregation_unit, self.original.aggregation_unit))
        if (len(self.parts) > min(self.original.size, AUXILIARY_LIMIT) or any(type(p) is not TradeAllocation or p.part_index != i
                or p.original_id != self.original.id or p.original_version != self.original.source_content_version
                or p.known_at != self.original.known_at or type(p.size) is not int or p.size <= 0
                for i, p in enumerate(self.parts)) or sum(p.size for p in self.parts) != self.original.size):
            raise ContractError("complete exact allocation must conserve original size and availability")

    @property
    def independent_source_events(self):
        return 1

    @property
    def id(self):
        return digest(self)


def allocate_trade(original, sizes):
    if type(original) is not Trade or type(sizes) is not tuple or not sizes or len(sizes) > AUXILIARY_LIMIT:
        raise ContractError("allocation requires a whole original and immutable exact sizes")
    return AllocationPlan(original, tuple(TradeAllocation(original.id, original.source_content_version,
                          i, size, original.known_at) for i, size in enumerate(sizes)))


@dataclass(frozen=True)
class BarConfirmation:
    id: str
    source_versions: tuple[str, ...]
    anchor_at: int
    known_at: int
    definition_id: str
    required_bars: int

    def __post_init__(self):
        _name(self.id)
        _name(self.definition_id)
        _identities(self.source_versions)
        timestamp(self.anchor_at)
        timestamp(self.known_at)
        _integer(self.required_bars, minimum=1)
        if self.anchor_at > self.known_at or self.required_bars != len(self.source_versions):
            raise ContractError("confirmation source count or availability is invalid")

    def available(self, cut):
        timestamp(cut)
        return cut >= self.known_at


def confirm_final_bars(bars, *, anchor_at, cut, published_at, definition_id, required_bars=None):
    _name(definition_id)
    for at in (anchor_at, cut, published_at):
        timestamp(at)
    if (type(bars) is not tuple or not bars or len(bars) > AUXILIARY_LIMIT or published_at < cut or anchor_at > cut
            or any(type(b) is not SharedBar or not b.available(cut) or not b.coverage_complete for b in bars)):
        raise DependencyUnavailable("confirmation needs completed available bar evidence")
    required_bars = len(bars) if required_bars is None else _integer(required_bars, minimum=1)
    if (len(bars) != required_bars or len({b.bar_id for b in bars}) != len(bars)
            or any(b.definition != bars[0].definition or b.interval[0] <= anchor_at for b in bars)
            or any(a.interval[1] > b.interval[0] for a, b in zip(bars, bars[1:]))):
        raise ContractError("confirmation needs distinct compatible ordered bars to the right of its anchor")
    versions = tuple(b.version_id for b in bars)
    return BarConfirmation(digest([definition_id, versions, anchor_at, published_at]), versions,
                           anchor_at, published_at, definition_id, required_bars)


@dataclass(frozen=True)
class OpportunityWitness:
    id: str
    bar_id: str
    version_id: str
    final: bool
    complete: bool
    source_events: int
    observation_process: str
    bar_published_at: int
    target_end: int
    label_known_at: int
    touched: bool

    def __post_init__(self):
        for s in (self.id, self.bar_id, self.version_id):
            _name(s)
        for at in (self.bar_published_at, self.target_end, self.label_known_at):
            timestamp(at)
        _integer(self.source_events, minimum=0)
        if (type(self.observation_process) is not str or self.observation_process not in {"nonempty_completed_bar", "completed_calendar_interval"}
                or any(type(v) is not bool for v in (self.final, self.complete, self.touched))
                or self.target_end < self.bar_published_at or self.label_known_at < self.target_end):
            raise ContractError("bar opportunity observation and maturity contract is invalid")


def opportunity_witness(bar, *, target_definition, target_end, label_known_at, touched, observation_process):
    if type(bar) is not SharedBar or not bar._certified:
        raise ContractError("opportunity needs a published immutable bar")
    _name(target_definition)
    return OpportunityWitness(digest([bar.bar_id, target_definition, target_end]), bar.bar_id,
        bar.version_id, bar.final, bar.coverage_complete, bar.summary.prints, observation_process,
        bar.published_at, target_end, label_known_at, touched)


def count_mature_opportunities(witnesses, *, cut):
    timestamp(cut)
    if type(witnesses) is not tuple or len(witnesses) > AUXILIARY_LIMIT or any(type(w) is not OpportunityWitness for w in witnesses):
        raise ContractError("opportunity counting retains immutable version witnesses")
    unique = {}
    for w in witnesses:
        if w.id in unique and unique[w.id] != w:
            raise IntegrityError("an opportunity cannot substitute another geometry/version or outcome")
        unique[w.id] = w
    eligible, rejected = [], []
    for w in unique.values():
        if (w.final and w.complete and w.label_known_at <= cut
                and (w.source_events > 0 or w.observation_process == "completed_calendar_interval")):
            eligible.append(w)
        else:
            rejected.append(w.id)
    return {"eligible": len(eligible), "successes": sum(w.touched for w in eligible),
            "eligible_ids": tuple(w.id for w in eligible), "rejected_ids": tuple(rejected)}


def coarse_contact_facts(bar, *, level, return_anchor):
    if type(bar) is not CoarseBar:
        raise ContractError("contact facts require typed observed coarse prices")
    _integer(level)
    _integer(return_anchor)
    o, h, l, c = bar.ohlc
    return {"inclusive_contact": None if h is None else l <= level <= h,
            "strict_upper_break": None if h is None else h > level,
            "strict_lower_break": None if l is None else l < level,
            "exact_close_return": None if c is None else c == return_anchor,
            "high_first": None, "intrabar_first_passage_at": None}
