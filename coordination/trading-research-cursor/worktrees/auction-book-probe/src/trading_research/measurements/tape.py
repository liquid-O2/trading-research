"""Whole observed trades, reported-side CVD, exact profiles and VWAP moments."""

from collections import defaultdict
from dataclasses import asdict, dataclass
from fractions import Fraction
import json
import re
from typing import Iterable, Protocol

from trading_research.data.events import CanonicalEvent, Flags
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import FuturesTerms, Ticks
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class Trade:
    id: str
    source_content_version: str
    instrument: str
    event_at: int
    known_at: int
    price: Ticks | None
    size: int
    side: int | None
    order: int | None
    aggregation_unit: str
    history_complete: bool

    def __post_init__(self):
        timestamp(self.event_at)
        timestamp(self.known_at)
        if (not all((self.id, self.source_content_version, self.instrument, self.aggregation_unit))
                or type(self.size) is not int or self.size <= 0
                or (self.side is not None and (type(self.side) is not int or self.side not in {-1, 1}))
                or (self.order is not None and (type(self.order) is not int or self.order < 0))):
            raise ContractError("trade needs exact whole-event size, reported sign, source identity and ordering semantics")

    @property
    def signed(self):
        return (self.side or 0) * self.size

    def record(self):
        return {**asdict(self), "price": None if self.price is None else self.price.value}

    @classmethod
    def restore(cls, record):
        return cls(**{**record, "price": None if record["price"] is None else Ticks(record["price"])})


def trade_from_event(event: CanonicalEvent, *, terms: FuturesTerms, instrument: str,
                     order: int | None, history_complete: bool) -> Trade | None:
    if not event.trade_eligible:
        return None
    # Price-dependent operations reject an off-tick quote; observed signed/unknown
    # volume remains available when price is missing, with separate coverage.
    try:
        price = None if event.price is None else terms.ticks(event.price)
    except ContractError:
        price = None  # Preserve flow; price-dependent outputs report unpriced mass.
    return Trade(event.address.id, event.id, instrument, event.clocks.event_at, event.clocks.known_at,
                 price, event.size, event.aggressor, order, "provider-reported-trade-record",
                 history_complete and not bool(event.flags & Flags.MAYBE_BAD_BOOK))


@dataclass(frozen=True)
class CorrectionImpact:
    id: str
    known_at: int
    before_instrument: str | None
    before_event_at: int | None
    after_instrument: str | None
    after_event_at: int | None

    def __post_init__(self):
        timestamp(self.known_at)
        if not isinstance(self.id, str) or not self.id:
            raise ContractError("correction impact requires immutable identity")
        for instrument, at in ((self.before_instrument, self.before_event_at),
                               (self.after_instrument, self.after_event_at)):
            if (instrument is None) != (at is None):
                raise ContractError("correction impact needs paired instrument/event time")
            if at is not None:
                timestamp(at)
                if not isinstance(instrument, str) or not instrument:
                    raise ContractError("correction impact instrument is invalid")


class TradeView(Protocol):
    def asof(self, *, instrument: str, cut: int, start: int | None = None,
             end: int | None = None) -> tuple[Trade, ...]: ...

    def changes(self, *, instrument: str, cut: int, start: int,
                end: int) -> tuple[CorrectionImpact, ...]: ...


class TradeLedger:
    """Bounded literal reference: retain original trades and current corrections.

    Bounds stop a run explicitly. Production archival/index optimization must
    match this reference before replacing it; no older rows silently disappear.
    """

    def __init__(self, *, max_events: int = 100_000):
        if type(max_events) is not int or max_events <= 0:
            raise ContractError("reference event retention requires an explicit positive bound")
        self.max_events = max_events
        self.trades: dict[str, Trade] = {}
        self.corrections: dict[str, dict] = {}
        self.latest_known_at: int | None = None

    def add(self, trade: Trade) -> bool:
        old = self.trades.get(trade.id)
        if old is not None:
            if old != trade:
                raise IntegrityError("source trade ID reused with changed content; append a correction")
            return False
        if len(self.trades) >= self.max_events:
            raise ContractError("bounded literal tape retention exceeded; register archive/index expansion")
        if self.latest_known_at is not None and trade.known_at < self.latest_known_at:
            raise ContractError("admitted availability stream regressed; do not backdate a late event")
        self.trades[trade.id] = trade
        self.latest_known_at = trade.known_at
        return True

    def correct(self, *, id: str, original_id: str, known_at: int, reason: str, replacement: Trade | None = None):
        timestamp(known_at)
        record = {"id": id, "original_id": original_id, "known_at": known_at, "reason": reason,
                  "replacement_id": replacement.id if replacement else None}
        if id in self.corrections:
            if self.corrections[id] != record or (replacement is not None and self.trades.get(replacement.id) != replacement):
                raise IntegrityError("correction ID reused")
            return
        if (not id or not reason or original_id not in self.trades
                or (self.latest_known_at is not None and known_at < self.latest_known_at)
                or any(c["original_id"] == original_id for c in self.corrections.values())):
            raise ContractError("correction needs one existing live source record and a current availability time")
        if replacement is not None:
            if (replacement.id in self.trades or replacement.known_at != known_at
                    or replacement.instrument != self.trades[original_id].instrument):
                raise ContractError("replacement requires a new ID and the correction's current known time")
            self.add(replacement)
        self.corrections[id] = record
        self.latest_known_at = known_at

    def asof(self, *, instrument: str, cut: int, start: int | None = None, end: int | None = None) -> tuple[Trade, ...]:
        timestamp(cut)
        removed = {c["original_id"] for c in self.corrections.values() if c["known_at"] <= cut}
        return tuple(t for t in self.trades.values() if t.instrument == instrument and t.known_at <= cut
                     and t.id not in removed and (start is None or t.event_at >= start) and (end is None or t.event_at < end))

    def changes(self, *, instrument: str, cut: int, start: int, end: int) -> tuple[CorrectionImpact, ...]:
        timestamp(cut); timestamp(start); timestamp(end)
        if start >= end:
            raise ContractError("correction impact interval must be nonempty")
        result = []
        for correction in self.corrections.values():
            before = self.trades[correction["original_id"]]
            after = self.trades.get(correction["replacement_id"])
            if correction["known_at"] <= cut and any(t is not None and t.instrument == instrument
                                                     and start <= t.event_at < end for t in (before, after)):
                result.append(CorrectionImpact(correction["id"], correction["known_at"], before.instrument,
                                               before.event_at, after.instrument if after else None,
                                               after.event_at if after else None))
        return tuple(result)

    def checkpoint(self) -> bytes:
        return canonical_json({"schema": "literal-trade-ledger-v1", "max_events": self.max_events,
                               "trades": [t.record() for t in self.trades.values()], "corrections": self.corrections,
                               "latest_known_at": self.latest_known_at})

    @classmethod
    def restore(cls, payload: bytes):
        p = json.loads(payload)
        if p["schema"] != "literal-trade-ledger-v1":
            raise ContractError("incompatible tape checkpoint")
        result = cls(max_events=p["max_events"])
        for t in p["trades"]:
            result.add(Trade.restore(t))
        result.corrections = p["corrections"]
        result.latest_known_at = p["latest_known_at"]
        origins = set()
        for id, c in result.corrections.items():
            original, replacement = result.trades.get(c["original_id"]), result.trades.get(c["replacement_id"])
            if (id != c["id"] or not c["reason"] or original is None or c["original_id"] in origins
                    or c["known_at"] < original.known_at
                    or (c["replacement_id"] is not None and (replacement is None or replacement.id == original.id
                        or replacement.instrument != original.instrument or replacement.known_at != c["known_at"]))):
                raise IntegrityError("invalid correction lineage in tape checkpoint")
            origins.add(c["original_id"])
        expected_known = max([*(t.known_at for t in result.trades.values()), *(c["known_at"] for c in result.corrections.values())], default=None)
        if result.latest_known_at != expected_known:
            raise IntegrityError("tape checkpoint availability clock disagrees with its events")
        if result.checkpoint() != payload:
            raise IntegrityError("noncanonical or inconsistent tape checkpoint")
        return result


@dataclass(frozen=True)
class CVD:
    buy: int
    sell: int
    unknown: int
    prints: int
    complete_history: bool

    @property
    def signed(self):
        return self.buy - self.sell

    @property
    def total(self):
        return self.buy + self.sell + self.unknown

    @property
    def true_signed_bounds(self) -> tuple[int, int] | None:
        return (self.signed - self.unknown, self.signed + self.unknown) if self.complete_history else None

    @property
    def known_side_fraction(self) -> Fraction | None:
        return Fraction(self.buy + self.sell, self.total) if self.total else None


def _one_tape(trades: Iterable[Trade]) -> tuple[Trade, ...]:
    values = tuple(trades)
    if len({t.id for t in values}) != len(values):
        raise ContractError("duplicate source evidence in tape input")
    if len({t.instrument for t in values}) > 1:
        raise ContractError("raw instruments/contracts cannot share one measurement anchor")
    return values


def cvd_reference(trades: Iterable[Trade], *, coverage_complete: bool) -> CVD:
    values = _one_tape(trades)
    return CVD(sum(t.size for t in values if t.side == 1), sum(t.size for t in values if t.side == -1),
               sum(t.size for t in values if t.side is None), len(values), coverage_complete and all(t.history_complete for t in values))


@dataclass(frozen=True)
class Cohort:
    id: str
    lower_inclusive: int
    upper_exclusive: int | None
    definition_version: str
    aggregation_unit: str

    def __post_init__(self):
        if (not all((self.id, self.definition_version, self.aggregation_unit)) or self.lower_inclusive < 1
                or (self.upper_exclusive is not None and self.upper_exclusive <= self.lower_inclusive)):
            raise ContractError("cohort definition requires a frozen positive count interval and observable aggregation unit")

    def contains(self, trade):
        if trade.aggregation_unit != self.aggregation_unit:
            raise DependencyUnavailable("vendor aggregation changed; size cohorts require a separate registered definition")
        return self.lower_inclusive <= trade.size and (self.upper_exclusive is None or trade.size < self.upper_exclusive)


@dataclass(frozen=True)
class CVDBar:
    open: int
    close: int
    high_bounds: tuple[int, int]
    low_bounds: tuple[int, int]
    high_at: int | None
    low_at: int | None
    flow: CVD
    cohort_version: str
    order_exact: bool

    @property
    def relative(self):
        return (0, self.close - self.open, tuple(v - self.open for v in self.high_bounds), tuple(v - self.open for v in self.low_bounds))


def cvd_bar(trades: Iterable[Trade], *, opening_cvd: int, cohort: Cohort, coverage_complete: bool) -> CVDBar:
    selected = [t for t in _one_tape(trades) if cohort.contains(t)]
    groups = defaultdict(list)
    for t in selected:
        groups[t.event_at].append(t)
    value, high_lo, high_hi, low_lo, low_hi = (opening_cvd,) * 5
    high_at = low_at = None
    exact = True
    for at, batch in sorted(groups.items()):
        ordered = len(batch) == 1 or (all(t.order is not None for t in batch) and len({t.order for t in batch}) == len(batch))
        if ordered:
            for t in sorted(batch, key=lambda t: t.order or 0):
                value += t.signed
                if value > high_hi:
                    high_at = at
                if value < low_lo:
                    low_at = at
                high_lo, high_hi = max(high_lo, value), max(high_hi, value)
                low_lo, low_hi = min(low_lo, value), min(low_hi, value)
        else:
            exact = False
            final = value + sum(t.signed for t in batch)
            high_lo = max(high_lo, value, final)
            high_hi = max(high_hi, value + sum(max(0, t.signed) for t in batch))
            low_lo = min(low_lo, value + sum(min(0, t.signed) for t in batch))
            low_hi = min(low_hi, value, final)
            value = final
    return CVDBar(opening_cvd, value, (high_lo, high_hi), (low_lo, low_hi), high_at if exact else None,
                  low_at if exact else None, cvd_reference(selected, coverage_complete=coverage_complete), cohort.definition_version, exact)


@dataclass(frozen=True)
class RowGrid:
    width_ticks: int
    origin_ticks: int
    definition_version: str

    def __post_init__(self):
        if type(self.width_ticks) is not int or self.width_ticks <= 0 or type(self.origin_ticks) is not int or not self.definition_version:
            raise ContractError("profile grid must be frozen in exact ticks")

    def row(self, price: Ticks):
        return (price.value - self.origin_ticks) // self.width_ticks

    def lower_tick(self, row: int):
        return self.origin_ticks + row * self.width_ticks


@dataclass(frozen=True)
class Profile:
    grid: RowGrid
    anchor_id: str
    rows: tuple[tuple[int, int, int, int], ...]  # row, buy, sell, unknown
    unpriced_volume: int
    complete_history: bool

    @property
    def histogram(self):
        return {row: b + s + u for row, b, s, u in self.rows}

    @property
    def delta(self):
        return {row: b - s for row, b, s, u in self.rows}

    @property
    def delta_bounds(self):
        return {row: (b - s - u, b - s + u) for row, b, s, u in self.rows}

    @property
    def total_volume(self):
        return sum(self.histogram.values()) + self.unpriced_volume


def profile_reference(trades: Iterable[Trade], *, grid: RowGrid, anchor_id: str, coverage_complete: bool) -> Profile:
    values = _one_tape(trades)
    if not anchor_id:
        raise ContractError("profile requires a frozen anchor and unique raw observations")
    rows = defaultdict(lambda: [0, 0, 0])
    missing = 0
    for t in values:
        if t.price is None:
            missing += t.size
        else:
            rows[grid.row(t.price)][{1:0, -1:1, None:2}[t.side]] += t.size
    return Profile(grid, anchor_id, tuple((r, *v) for r, v in sorted(rows.items())), missing,
                   coverage_complete and all(t.history_complete for t in values))


@dataclass(frozen=True)
class ValueArea:
    poc: int
    poc_maximizers: tuple[int, ...]
    lower_row: int
    upper_row: int
    requested_fraction: Fraction
    achieved_fraction: Fraction
    tie_rule: str


def value_area(histogram: dict[int, int], *, fraction: Fraction, tie_rule: str = "lower") -> ValueArea | None:
    if (not isinstance(fraction, Fraction) or not 0 < fraction <= 1 or tie_rule not in {"lower", "upper"}
            or any(type(k) is not int or type(v) is not int or v < 0 for k, v in histogram.items())):
        raise ContractError("value area uses nonnegative mass, a declared fraction and deterministic row ties")
    total = sum(histogram.values())
    if not total:
        return None
    maximum = max(histogram.values())
    maximizers = tuple(sorted(k for k, v in histogram.items() if v == maximum))
    poc = maximizers[0] if tie_rule == "lower" else maximizers[-1]
    low = high = poc
    retained = histogram[poc]
    left, right = min(histogram), max(histogram)
    # Missing price rows have zero observed mass. Crossing them expands geometric
    # support; it never manufactures traded volume at those prices.
    while Fraction(retained, total) < fraction:
        l = histogram.get(low - 1, 0) if low > left else -1
        r = histogram.get(high + 1, 0) if high < right else -1
        if l < 0 and r < 0:
            raise IntegrityError("profile expansion exhausted before its mass target")
        if l > r or (l == r and tie_rule == "lower"):
            low -= 1
            retained += l
        else:
            high += 1
            retained += r
    return ValueArea(poc, maximizers, low, high, fraction, Fraction(retained, total), tie_rule)


class WeightedMoments:
    """Integer tick sums make online updates/downdates exact and cancellation free."""

    def __init__(self, *, max_events: int = 100_000):
        if type(max_events) is not int or max_events <= 0:
            raise ContractError("weighted-moment retained IDs require an explicit bound")
        self.max_events = max_events
        self.mass = self.first = self.second = 0
        self._events: dict[str, tuple[int, int, str]] = {}
        self.instrument: str | None = None

    def add(self, trade: Trade):
        if trade.price is None:
            raise DependencyUnavailable("VWAP requires observed trade prices")
        if self.instrument is not None and trade.instrument!=self.instrument:
            raise ContractError("VWAP anchor cannot mix raw instruments or contract transitions")
        entry = (trade.price.value, trade.size, digest(trade))
        if trade.id in self._events:
            if self._events[trade.id] != entry:
                raise IntegrityError("VWAP source ID content changed")
            return
        if len(self._events) >= self.max_events:
            raise ContractError("weighted-moment retained source-ID bound exceeded")
        p, q, _ = entry
        self.mass += q
        self.first += p * q
        self.second += p * p * q
        self._events[trade.id] = entry
        self.instrument = trade.instrument

    def remove(self, event_id: str):
        if event_id not in self._events:
            raise ContractError("rolling downdate references an absent event")
        p, q, _ = self._events.pop(event_id)
        self.mass -= q
        self.first -= p * q
        self.second -= p * p * q

    @property
    def mean(self) -> Fraction | None:
        return Fraction(self.first, self.mass) if self.mass else None

    @property
    def variance(self) -> Fraction | None:
        return Fraction(self.second, self.mass) - self.mean ** 2 if self.mass else None

    def checkpoint(self) -> bytes:
        return canonical_json({"schema": "exact-weighted-moments-v2", "events": self._events, "max_events": self.max_events,
                               "instrument":self.instrument,
                               "mass": self.mass, "first": self.first, "second": self.second})

    @classmethod
    def restore(cls, payload: bytes):
        p = json.loads(payload)
        if p["schema"] != "exact-weighted-moments-v2":
            raise ContractError("incompatible weighted-moment checkpoint")
        result = cls(max_events=p["max_events"])
        result._events = {id: tuple(entry) for id, entry in p["events"].items()}
        result.instrument=p['instrument']
        if ((result._events and not result.instrument) or result.instrument is not None and not isinstance(result.instrument,str)
                or len(result._events) > result.max_events
                or any(not id or type(price) is not int or type(q) is not int or q <= 0 or not isinstance(content,str)
                       or re.fullmatch(r'[0-9a-f]{64}',content) is None for id, (price, q, content) in result._events.items())):
            raise IntegrityError("invalid weighted-moment source events")
        result.mass = sum(q for price, q, _ in result._events.values())
        result.first = sum(price * q for price, q, _ in result._events.values())
        result.second = sum(price * price * q for price, q, _ in result._events.values())
        if result.checkpoint() != payload:
            raise IntegrityError("weighted-moment checkpoint arithmetic mismatch")
        return result


def vwap_two_pass(trades: Iterable[Trade]) -> tuple[Fraction | None, Fraction | None]:
    values = _one_tape(trades)
    if any(t.price is None for t in values):
        raise DependencyUnavailable("two-pass reference needs observed trade prices")
    mass = sum(t.size for t in values)
    if not mass:
        return None, None
    mean = sum((Fraction(t.price.value) * t.size for t in values), Fraction()) / mass
    variance = sum((t.size * (Fraction(t.price.value) - mean) ** 2 for t in values), Fraction()) / mass
    return mean, variance
