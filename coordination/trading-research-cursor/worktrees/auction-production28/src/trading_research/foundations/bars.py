"""Literal causal time bars and whole-event activity bars with durable versions."""

from collections import defaultdict
from dataclasses import asdict, dataclass, replace
import json
from types import MappingProxyType

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.tape import Trade, TradeLedger, TradeView
from trading_research.operations.artifacts import canonical_json, digest


def _text(value):
    if type(value) is not str or not value:
        raise ContractError("bar evidence needs an explicit string identity")
    return value


@dataclass(frozen=True)
class WindowCoverage:
    instrument: str
    start: int
    end: int
    observed_intervals: tuple[tuple[int, int], ...]
    known_at: int
    source_version: str

    def __post_init__(self):
        for at in (self.start, self.end, self.known_at):
            timestamp(at)
        _text(self.instrument)
        _text(self.source_version)
        if self.end <= self.start or type(self.observed_intervals) is not tuple:
            raise ContractError("coverage needs a versioned instrument, interval and observed spans")
        previous = self.start
        for pair in self.observed_intervals:
            if type(pair) is not tuple or len(pair) != 2:
                raise ContractError("coverage spans must be immutable exact endpoint pairs")
            left, right = pair
            timestamp(left)
            timestamp(right)
            if not self.start <= left < right <= self.end or left < previous or right > self.known_at:
                raise ContractError("coverage spans overlap, regress or exceed the requested interval")
            previous = right

    @property
    def observed_duration(self):
        return sum(right - left for left, right in self.observed_intervals)

    @property
    def complete(self):
        return self.observed_duration == self.end - self.start


@dataclass(frozen=True)
class Watermark:
    through_event_at: int
    known_at: int
    source_version: str

    def __post_init__(self):
        timestamp(self.through_event_at)
        timestamp(self.known_at)
        _text(self.source_version)
        if self.known_at < self.through_event_at:
            raise ContractError("a historical watermark requires an explicit available source/replay certificate")


@dataclass(frozen=True)
class CausalBar:
    instrument: str
    start: int
    end: int
    definition_version: str
    revision: int
    observation_cut: int
    minimum_known_at: int
    final: bool
    open_ticks: int | None
    high_ticks: int | None
    low_ticks: int | None
    close_ticks: int | None
    volume: int
    prints: int
    unpriced_volume: int
    order_exact: bool
    coverage_complete: bool
    observed_duration_ns: int
    source_event_ids: tuple[str, ...]
    coverage_version: str
    correction_ids: tuple[str, ...]
    published_at: int | None = None

    def __post_init__(self):
        for at in (self.start,self.end,self.observation_cut,self.minimum_known_at):
            timestamp(at)
        if (not self.instrument or not self.definition_version or not self.coverage_version
                or self.end<=self.start or not self.start<=self.minimum_known_at<=self.observation_cut
                or type(self.revision) is not int or self.revision<0):
            raise ContractError("bar identity, observation interval and availability disagree")
        if (any(type(v) is not int or v<0 for v in (self.volume,self.prints,self.unpriced_volume,self.observed_duration_ns))
                or self.unpriced_volume>self.volume or self.prints>self.volume or self.observed_duration_ns>self.end-self.start):
            raise ContractError("bar mass and observed duration are inconsistent")
        if any(type(v) is not bool for v in (self.final,self.order_exact,self.coverage_complete)):
            raise ContractError("bar status flags must be explicit booleans")
        if self.coverage_complete and (self.unpriced_volume or self.observed_duration_ns!=self.end-self.start):
            raise ContractError("complete price coverage cannot include unpriced mass or missing duration")
        if self.final and self.minimum_known_at<self.end:
            raise ContractError("final bar precedes its endpoint")
        for values in (self.source_event_ids,self.correction_ids):
            if not isinstance(values,tuple) or len(set(values))!=len(values):
                raise ContractError("bar evidence identities must be immutable and unique")
        if self.published_at is not None:
            timestamp(self.published_at)
            if self.published_at<self.observation_cut:
                raise ContractError("bar publication precedes its captured cut")
        prices=(self.open_ticks,self.high_ticks,self.low_ticks,self.close_ticks)
        if any(p is not None and type(p) is not int for p in prices):
            raise ContractError("bar prices require exact ticks or explicit missingness")
        if (self.high_ticks is None)!=(self.low_ticks is None):
            raise ContractError("bar high/low must share observed price support")
        if self.high_ticks is None:
            if self.open_ticks is not None or self.close_ticks is not None:
                raise ContractError("bar edge price has no observed extrema support")
        elif self.high_ticks<self.low_ticks or any(p is not None and not self.low_ticks<=p<=self.high_ticks for p in (self.open_ticks,self.close_ticks)):
            raise ContractError("bar prices violate observed extrema")

    @property
    def bar_id(self):
        return digest([self.instrument, self.start, self.end, self.definition_version])

    @property
    def version_id(self):
        return digest(self)


def _price_order(values: tuple[Trade, ...]):
    if not values:
        return None, None, None, None, True
    ordered = sorted(values, key=lambda t: (t.event_at, t.order or 0, t.id))
    exact = True
    groups = defaultdict(list)
    for t in ordered:
        groups[t.event_at].append(t)
    for tied in groups.values():
        if len(tied) > 1 and (any(t.order is None for t in tied) or len({t.order for t in tied}) < len(tied)):
            exact = False
    first = groups[ordered[0].event_at]
    last = groups[ordered[-1].event_at]

    def edge(batch, terminal=False):
        prices = {None if t.price is None else t.price.value for t in batch}
        ordered_tie = len(batch) == 1 or (all(t.order is not None for t in batch) and len({t.order for t in batch}) == len(batch))
        if ordered_tie:
            price=sorted(batch,key=lambda t:t.order or 0)[-1 if terminal else 0].price
            return None if price is None else price.value
        return next(iter(prices)) if len(prices)==1 else None
    priced=[t.price.value for t in ordered if t.price is not None]
    return edge(first), max(priced,default=None), min(priced,default=None), edge(last, True), exact


def bar_reference(ledger: TradeView, *, instrument: str, start: int, end: int, cut: int,
                  definition_version: str, coverage: WindowCoverage, watermark: Watermark | None = None,
                  revision: int = 0) -> CausalBar:
    for at in (start, end, cut):
        timestamp(at)
    _text(instrument)
    _text(definition_version)
    if (end <= start or cut < start or type(revision) is not int or revision < 0
            or type(coverage) is not WindowCoverage or watermark is not None and type(watermark) is not Watermark):
        raise ContractError("invalid causal half-open bar definition")
    if coverage.instrument != instrument or coverage.start != start or coverage.end != end or coverage.known_at > cut:
        raise DependencyUnavailable("bar coverage does not match the available instrument/interval")
    final = watermark is not None and watermark.known_at <= cut and watermark.through_event_at >= end
    values = ledger.asof(instrument=instrument, cut=cut, start=start, end=min(end, cut + 1))
    impacts = ledger.changes(instrument=instrument, cut=cut, start=start, end=end)
    corrections = tuple(c.id for c in impacts)
    opening, high, low, close, exact = _price_order(values)
    known = max([coverage.known_at, *(t.known_at for t in values),
                 *(c.known_at for c in impacts),
                 *([end, watermark.known_at] if final else [start])])
    return CausalBar(instrument, start, end, definition_version, revision, cut, known, final, opening, high, low, close,
                     sum(t.size for t in values), len(values), sum(t.size for t in values if t.price is None), exact,
                     coverage.complete and all(t.history_complete and t.price is not None for t in values), coverage.observed_duration,
                     tuple(t.id for t in values), coverage.source_version, corrections)


class BarEngine:
    __slots__ = ("_instrument", "_definition_version", "_max_events", "_max_publications", "_ledger", "_versions", "_requests", "_prefixes")

    def __setattr__(self, name, value):
        if name in {"_instrument", "_definition_version", "_max_events", "_max_publications", "_ledger"} and hasattr(self, name):
            raise AttributeError("admitted legacy bar configuration is immutable")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError("bar engine slots cannot be deleted")

    def __init__(self, *, instrument: str, definition_version: str, max_events: int = 100_000, max_publications: int = 4096):
        _text(instrument)
        _text(definition_version)
        if any(type(v) is not int or v <= 0 for v in (max_events, max_publications)):
            raise ContractError("bar source and publication retention need finite positive bounds")
        self._instrument, self._definition_version = instrument, definition_version
        self._max_events, self._max_publications = max_events, max_publications
        self._ledger = TradeLedger(max_events=max_events)
        self._versions, self._requests, self._prefixes = {}, [], {}

    instrument = property(lambda self: self._instrument)
    definition_version = property(lambda self: self._definition_version)
    max_events = property(lambda self: self._max_events)
    max_publications = property(lambda self: self._max_publications)
    ledger = property(lambda self: self._ledger)
    versions = property(lambda self: MappingProxyType({key: tuple(value) for key, value in self._versions.items()}))

    def add(self, trade: Trade):
        if type(trade) is not Trade or trade.instrument != self.instrument or self.ledger.max_events != self.max_events:
            raise ContractError("raw contract or retained source configuration changed")
        return self.ledger.add(trade)

    def publish(self, *, start: int, end: int, cut: int, published_at: int,
                coverage: WindowCoverage, watermark: Watermark | None = None):
        timestamp(published_at)
        timestamp(cut)
        if (published_at < cut or self.ledger.max_events != self.max_events
                or len(self._requests) >= self.max_publications):
            raise ContractError("publication clock, source configuration or retained publication bound is invalid")
        id = digest([self.instrument, start, end, self.definition_version])
        prior = self._versions.get(id, [])
        if prior and (published_at < prior[-1].published_at or cut < prior[-1].observation_cut):
            raise ContractError("cannot regress a bar publication or observation cut")
        value = bar_reference(self.ledger, instrument=self.instrument, start=start, end=end, cut=cut,
                              definition_version=self.definition_version, coverage=coverage, watermark=watermark, revision=len(prior))
        if prior and prior[-1].final and not value.final:
            raise ContractError("a published final bar cannot revert to an incomplete watermark")
        value = replace(value, published_at=published_at)
        prefix = self.ledger.checkpoint()
        prefix_id = digest(prefix)
        request = {"start": start, "end": end, "cut": cut, "published_at": published_at,
                   "coverage": asdict(coverage), "watermark": None if watermark is None else asdict(watermark), "prefix_id": prefix_id}
        self._prefixes[prefix_id] = prefix.hex()
        self._requests.append(request)
        self._versions.setdefault(id, []).append(value)
        return value

    def asof(self, *, start: int, end: int, cut: int) -> CausalBar | None:
        timestamp(start); timestamp(end); timestamp(cut)
        values = self._versions.get(digest([self.instrument, start, end, self.definition_version]), [])
        return max((v for v in values if v.published_at <= cut), key=lambda v: (v.published_at, v.revision), default=None)

    def checkpoint(self):
        return canonical_json({"schema": "causal-bar-engine-v3", "instrument": self.instrument,
            "definition_version": self.definition_version, "max_events": self.max_events, "max_publications": self.max_publications,
            "ledger_hex": self.ledger.checkpoint().hex(), "prefixes": self._prefixes, "requests": self._requests,
            "versions": {id: [asdict(v) for v in versions] for id, versions in self._versions.items()}})

    @classmethod
    def restore(cls, payload: bytes):
        if type(payload) is not bytes:
            raise ContractError("bar checkpoint requires immutable bytes")
        try:
            p = json.loads(payload)
            if p["schema"] != "causal-bar-engine-v3":
                raise ContractError("incompatible bar checkpoint")
            result = cls(instrument=p["instrument"], definition_version=p["definition_version"],
                         max_events=p["max_events"], max_publications=p["max_publications"])
            ledger = TradeLedger.restore(bytes.fromhex(p["ledger_hex"]))
            if ledger.max_events != result.max_events or type(p["requests"]) is not list or len(p["requests"]) > result.max_publications:
                raise IntegrityError("bar checkpoint source/publication retention changed")
            final_rows = list(ledger.trades.values())
            prefixes = {}
            for id, raw_hex in p["prefixes"].items():
                raw = bytes.fromhex(raw_hex)
                prefix = TradeLedger.restore(raw)
                if (digest(raw) != id or prefix.max_events != result.max_events
                        or list(prefix.trades.values()) != final_rows[:len(prefix.trades)]
                        or any(ledger.corrections.get(key) != value for key, value in prefix.corrections.items())):
                    raise IntegrityError("publication prefix is not retained in the final original ledger")
                prefixes[id] = prefix
            prior_rows, prior_corrections = 0, set()
            for request in p["requests"]:
                prefix = prefixes[request["prefix_id"]]
                if len(prefix.trades) < prior_rows or not prior_corrections <= set(prefix.corrections):
                    raise IntegrityError("publication admission prefixes regressed")
                prior_rows, prior_corrections = len(prefix.trades), set(prefix.corrections)
                object.__setattr__(result, "_ledger", prefix)
                cov = request["coverage"]
                coverage = WindowCoverage(**{**cov, "observed_intervals": tuple(tuple(pair) for pair in cov["observed_intervals"])})
                watermark = None if request["watermark"] is None else Watermark(**request["watermark"])
                result.publish(start=request["start"], end=request["end"], cut=request["cut"],
                               published_at=request["published_at"], coverage=coverage, watermark=watermark)
            object.__setattr__(result, "_ledger", ledger)
            if result.checkpoint() != payload:
                raise IntegrityError("bar output, coverage, watermark or admission-prefix reconstruction differs")
            return result
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise IntegrityError("malformed bar checkpoint") from exc


@dataclass(frozen=True)
class ActivityBar:
    index: int
    kind: str
    threshold: int
    event_ids: tuple[str, ...]
    volume: int
    minimum_known_at: int
    threshold_reached: bool
    close_reason: str


class ActivityBars:
    __slots__ = ("_kind", "_threshold", "_max_events", "_pending", "_completed", "_seen", "_latest_known_at", "_boundaries", "_journal", "_pending_volume")

    def __setattr__(self, name, value):
        if name in {"_kind", "_threshold", "_max_events"} and hasattr(self, name):
            raise AttributeError("admitted activity configuration is immutable")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError("activity state slots cannot be deleted")

    def __init__(self, *, kind: str, threshold: int, max_events: int = 100_000):
        if type(kind) is not str or kind not in {"volume", "events"} or any(type(v) is not int or v <= 0 for v in (threshold, max_events)):
            raise ContractError("activity bars need an explicit whole-event threshold")
        self._kind, self._threshold, self._max_events = kind, threshold, max_events
        self._pending, self._completed, self._boundaries, self._journal = [], [], [], []
        self._seen, self._latest_known_at, self._pending_volume = {}, None, 0

    kind = property(lambda self: self._kind)
    threshold = property(lambda self: self._threshold)
    max_events = property(lambda self: self._max_events)
    pending = property(lambda self: tuple(self._pending))
    completed = property(lambda self: tuple(self._completed))
    seen = property(lambda self: MappingProxyType(dict(self._seen)))
    latest_known_at = property(lambda self: self._latest_known_at)
    boundaries = property(lambda self: tuple(self._boundaries))
    pending_volume = property(lambda self: self._pending_volume)

    def add(self, trade: Trade) -> ActivityBar | None:
        if type(trade) is not Trade:
            raise ContractError("activity input must be a whole source trade")
        Trade.restore(trade.record())
        if trade.id in self._seen:
            if self._seen[trade.id] != trade:
                raise IntegrityError("activity bar duplicate content mismatch")
            return None
        if len(self._seen) >= self.max_events:
            raise ContractError("activity-bar reference retained source bound exceeded")
        if ((self._seen and trade.instrument != next(iter(self._seen.values())).instrument)
                or self.latest_known_at is not None and trade.known_at < self.latest_known_at):
            raise ContractError("activity bar stream changed instrument or regressed availability")
        self._pending.append(trade)
        self._pending_volume += trade.size
        self._seen[trade.id] = trade
        self._latest_known_at = trade.known_at
        self._journal.append({"op": "add", "trade": trade.record()})
        mass = self._pending_volume if self.kind == "volume" else len(self._pending)
        return self._close(trade.known_at, True, "whole-event threshold including overshoot") if mass >= self.threshold else None

    def _close(self, at: int, reached: bool, reason: str):
        value = ActivityBar(len(self._completed), self.kind, self.threshold, tuple(t.id for t in self._pending),
                            self._pending_volume, at, reached, reason)
        self._completed.append(value)
        self._pending, self._pending_volume = [], 0
        return value

    def boundary(self, *, known_at: int, reason: str) -> ActivityBar | None:
        timestamp(known_at)
        _text(reason)
        if self.latest_known_at is not None and known_at < self.latest_known_at:
            raise ContractError("partial activity bar requires a current explicit boundary")
        if len(self._boundaries) >= self.max_events:
            raise ContractError("activity-bar retained boundary bound exceeded")
        self._boundaries.append((known_at, reason))
        self._journal.append({"op": "boundary", "known_at": known_at, "reason": reason})
        self._latest_known_at = known_at
        return self._close(known_at, False, reason) if self._pending else None

    def checkpoint(self):
        return canonical_json({"schema": "whole-event-activity-bars-v3", "kind": self.kind, "threshold": self.threshold,
            "max_events": self.max_events, "seen": [t.record() for t in self._seen.values()],
            "pending": [t.id for t in self._pending], "pending_volume": self._pending_volume, "completed": self._completed,
            "latest_known_at": self.latest_known_at, "boundaries": self._boundaries, "journal": self._journal})

    @classmethod
    def restore(cls, payload: bytes):
        if type(payload) is not bytes:
            raise ContractError("activity checkpoint requires immutable bytes")
        try:
            p = json.loads(payload)
            if p["schema"] != "whole-event-activity-bars-v3":
                raise ContractError("incompatible activity-bar checkpoint")
            result = cls(kind=p["kind"], threshold=p["threshold"], max_events=p["max_events"])
            if type(p["journal"]) is not list or len(p["journal"]) > result.max_events * 2:
                raise IntegrityError("activity operation history exceeds its retained bound")
            for record in p["journal"]:
                if record["op"] == "add":
                    result.add(Trade.restore(record["trade"]))
                elif record["op"] == "boundary":
                    result.boundary(known_at=record["known_at"], reason=record["reason"])
                else:
                    raise IntegrityError("unknown activity operation")
            if result.checkpoint() != payload:
                raise IntegrityError("activity first-crossing/reset/output reconstruction differs")
            return result
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise IntegrityError("malformed activity checkpoint") from exc
