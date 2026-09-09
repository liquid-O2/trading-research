"""Bounded, revalidated measurement windows over the actual F05/F09 sources.

Captures are immutable values, not credentials. Public consumers rederive them
from the retained source at their original cut before using their observations.
"""

from dataclasses import dataclass, field, fields, replace
from itertools import groupby

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import WindowCoverage
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import Ticks
from trading_research.measurements.tape import Trade, TradeLedger
from trading_research.measurements.transaction_reducers import TransactionTapeView
from trading_research.data.transactions import TransactionLedger
from trading_research.operations.artifacts import canonical_json, digest


def bounded_name(value):
    if type(value) is not str or not value or len(value) > 1024:
        raise ContractError("measurement identity must be a nonempty bounded string")
    return value


def positive_limit(value):
    if type(value) is not int or value < 1:
        raise ContractError("measurement capacity must be a positive exact integer")
    return value


def bounded_rows(value, limit, *, name="measurement inputs"):
    positive_limit(limit)
    if type(value) not in (tuple, list) or len(value) > limit:
        raise ContractError(f"{name} need a bounded materialized sequence")
    return value


@dataclass(frozen=True)
class MeasurementWindow:
    instrument: str
    start: int
    end: int
    cut: int
    published_at: int
    definition_version: str
    aggregation_unit: str
    source_kind: str
    source_domains: tuple
    source_versions: tuple
    correction_ids: tuple
    contribution_hash: str
    coverage: WindowCoverage
    coverage_id: str
    observed_duration_ns: int
    support_status: str
    history_complete: bool
    eligible_volume: int
    excluded_volume: int
    buy_volume: int
    sell_volume: int
    unknown_volume: int
    unpriced_volume: int
    print_count: int
    order_exact: bool
    covered_print_count: int
    max_inputs: int
    max_bytes: int
    source_bar_version: str | None = None

    def record(self):
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @property
    def id(self):
        return digest(self.record())

    @property
    def signed(self):
        return self.buy_volume - self.sell_volume

    @property
    def observed_signed_bounds(self):
        return self.signed - self.unknown_volume, self.signed + self.unknown_volume

    @property
    def true_signed_bounds(self):
        return self.observed_signed_bounds if self.history_complete else None


@dataclass(frozen=True)
class CapturedTradeWindow:
    window: MeasurementWindow
    trades: tuple[Trade, ...]
    _bar_recipe: object = field(default=None, init=False, repr=False, compare=False)

    def record(self):
        return {"window": self.window.record(), "trades": tuple(t.record() for t in self.trades)}

    @property
    def id(self):
        return digest(self.record())


def _preflight(view, max_inputs, max_bytes):
    positive_limit(max_inputs)
    positive_limit(max_bytes)
    if type(view) is TradeLedger:
        positive_limit(view.max_events)
        if (type(view.trades) is not dict or type(view.corrections) is not dict
                or len(view.trades) + len(view.corrections) > max_inputs):
            raise ContractError("retained legacy source exceeds capture input capacity")
    elif type(view) is TransactionTapeView and type(view.ledger) is TransactionLedger:
        for k in ("max_records", "max_bytes"):
            positive_limit(view.ledger.config[k])
        if len(view.ledger.deltas) > max_inputs:
            raise ContractError("retained F05 deltas exceed capture input capacity")
    else:
        raise ContractError("capture requires an actual supported bounded source ledger")


def _covered(at, coverage, *, cut=None):
    if any(a <= at < b for a, b in coverage.observed_intervals):
        return True
    # An actual event at the closed observation cut is point evidence. It
    # adds no duration and never changes the requested half-open interval.
    return (at == cut and coverage.start <= at < coverage.end
            and (at == coverage.start or any(b == at for _, b in coverage.observed_intervals)))


def _admit_trade(trade, instrument, aggregation_unit, cut):
    if type(trade) is not Trade:
        raise ContractError("whole typed source trade required")
    for value in (trade.id, trade.source_content_version, trade.instrument, trade.aggregation_unit):
        bounded_name(value)
    Trade.restore(trade.record())
    if (trade.instrument != instrument or trade.aggregation_unit != aggregation_unit
            or type(trade.history_complete) is not bool
            or trade.price is not None and type(trade.price) is not Ticks
            or trade.known_at < trade.event_at or trade.known_at > cut or trade.event_at > cut):
        raise ContractError("trade domain, whole-event units, history or availability mismatch")


def _finish(window, trades, recipe=None):
    result = CapturedTradeWindow(window, trades)
    if len(canonical_json(result.record())) > window.max_bytes:
        raise ContractError("measurement capture exceeds its retained byte capacity")
    object.__setattr__(result, "_bar_recipe", recipe)
    return result


def capture_trade_window(view, *, instrument, start, end, cut, published_at,
                         definition_version, aggregation_unit, coverage,
                         max_inputs=4096, max_bytes=8388608):
    _preflight(view, max_inputs, max_bytes)
    for value in (instrument, definition_version, aggregation_unit):
        bounded_name(value)
    for at in (start, end, cut, published_at):
        timestamp(at)
    if start >= end or cut < start or published_at < cut:
        raise ContractError("measurement interval/cut/publication is inconsistent")
    if type(coverage) is not WindowCoverage:
        raise ContractError("explicit immutable coverage required")
    bounded_rows(coverage.observed_intervals, max_inputs, name="coverage spans")
    WindowCoverage(**{f.name: getattr(coverage, f.name) for f in fields(coverage)})
    bounded_name(coverage.source_version)
    if ((coverage.instrument, coverage.start, coverage.end) != (instrument, start, end)
            or coverage.known_at > cut):
        raise ContractError("coverage raw domain, interval or availability mismatch")
    raw = view.asof(instrument=instrument, cut=cut, start=start, end=end)
    bounded_rows(raw, max_inputs)
    # Event-time filtering does not invent a cut+1 timestamp at the int64 edge.
    trades = tuple(sorted((t for t in raw if t.event_at <= cut),
                          key=lambda t: (t.event_at, -1 if t.order is None else t.order, t.id)))
    for trade in trades:
        _admit_trade(trade, instrument, aggregation_unit, cut)
        if not _covered(trade.event_at, coverage, cut=cut):
            raise ContractError("selected print conflicts with its declared observed coverage")
    if len({t.id for t in trades}) != len(trades):
        raise IntegrityError("capture contains duplicate whole-event identities")
    domains, excluded, source_history = (), 0, all(t.history_complete for t in trades)
    versions = tuple(sorted((t.id, t.source_content_version) for t in trades))
    source_kind = "legacy_trade"
    if type(view) is TransactionTapeView:
        resolved = view.ledger.asof(instrument=instrument, cut=cut, start=start, end=end)
        bounded_rows(resolved, max_inputs)
        selected = tuple(r for r in resolved if r.value.event_at <= cut)
        for row in selected:
            if row.value.volume_eligibility is None:
                raise DependencyUnavailable("unresolved condition eligibility in measurement window")
            if row.value.aggregation_unit != aggregation_unit or not _covered(row.value.event_at, coverage, cut=cut):
                raise ContractError("F05 source units or coverage disagree with measurement")
        source_kind = "f05_transaction"
        versions = tuple(sorted((r.root_key.id, r.version_hash) for r in selected))
        domains = tuple(sorted({(r.root_key.provider, r.root_key.dataset, r.root_key.publisher_or_venue,
                                 r.root_key.channel, r.root_key.source_session) for r in selected}, key=canonical_json))
        for domain in domains:
            for value in domain:
                if value is not None:
                    bounded_name(value)
        excluded = sum(r.value.quantity for r in selected if not r.value.volume_eligibility)
        source_history = all(r.value.history_complete for r in selected)
    changes = view.changes(instrument=instrument, cut=cut, start=start, end=end)
    bounded_rows(changes, max_inputs, name="correction impacts")
    correction_ids = tuple(sorted(bounded_name(c.id) for c in changes))
    ordered = all(len(batch := tuple(g)) <= 1 or
                  all(t.order is not None for t in batch) and len({t.order for t in batch}) == len(batch)
                  for _, g in groupby(trades, key=lambda t: t.event_at))
    history = coverage.complete and source_history
    status = "unobserved" if not coverage.observed_duration and not trades else "complete" if history else "partial"
    window = MeasurementWindow(instrument, start, end, cut, published_at, definition_version, aggregation_unit,
        source_kind, domains, versions, correction_ids, digest(tuple(t.record() for t in trades)), coverage,
        digest(coverage), coverage.observed_duration, status, history, sum(t.size for t in trades), excluded,
        sum(t.size for t in trades if t.side == 1), sum(t.size for t in trades if t.side == -1),
        sum(t.size for t in trades if t.side is None), sum(t.size for t in trades if t.price is None),
        len(trades), ordered, len(trades), max_inputs, max_bytes)
    return _finish(window, trades)


def capture_bar_window(engine, publication_version_id, *, view, aggregation_unit,
                       published_at, max_inputs=4096, max_bytes=8388608):
    from trading_research.foundations.multiresolution import SharedBarEngine, summarize
    _preflight(view, max_inputs, max_bytes)
    if type(engine) is not SharedBarEngine:
        raise ContractError("actual shared bar engine required")
    bounded_name(publication_version_id)
    timestamp(published_at)
    bar, request = engine.window_publication(publication_version_id)
    if bar.definition.kind != "time" or not bar.available(published_at, final_only=False):
        raise DependencyUnavailable("retained time bar is not available for this publication")
    if bar.definition.domain.aggregation_unit != aggregation_unit:
        raise ContractError("shared bar aggregation unit changed")
    captured = capture_trade_window(view, instrument=bar.definition.domain.instrument,
        start=request.start, end=request.end, cut=bar.observation_cut, published_at=published_at,
        definition_version=bar.definition.version, aggregation_unit=aggregation_unit, coverage=request.coverage,
        max_inputs=max_inputs, max_bytes=max_bytes)
    if (summarize(captured.trades, bar.definition.domain).record() != bar.summary.record()
            or captured.window.correction_ids != bar.correction_ids):
        raise IntegrityError("retained shared bar differs from actual source at its frozen cut")
    return _finish(replace(captured.window, source_bar_version=publication_version_id), captured.trades,
                   (engine, publication_version_id))


def validate_trade_window(captured, view, *, publication_cut=None):
    if type(captured) is not CapturedTradeWindow or type(captured.window) is not MeasurementWindow:
        raise ContractError("typed captured window required")
    w = captured.window
    bounded_rows(captured.trades, w.max_inputs)
    if w.source_bar_version is None:
        actual = capture_trade_window(view, **{name: getattr(w, name) for name in (
            "instrument", "start", "end", "cut", "published_at", "definition_version", "aggregation_unit",
            "coverage", "max_inputs", "max_bytes")})
    else:
        recipe = captured._bar_recipe
        if type(recipe) is not tuple or len(recipe) != 2 or recipe[1] != w.source_bar_version:
            raise IntegrityError("shared bar capture lost its actual retained source recipe")
        actual = capture_bar_window(recipe[0], recipe[1], view=view, aggregation_unit=w.aggregation_unit,
            published_at=w.published_at, max_inputs=w.max_inputs, max_bytes=w.max_bytes)
    if actual != captured:
        raise IntegrityError("measurement capture differs from its actual historical source")
    if publication_cut is not None:
        timestamp(publication_cut)
        if publication_cut < w.cut:
            raise ContractError("measurement publication precedes the original observation cut")
        current = view.asof(instrument=w.instrument, start=w.start, end=w.end, cut=publication_cut)
        bounded_rows(current, w.max_inputs)
        current = tuple(sorted((t for t in current if t.event_at <= w.cut),
                               key=lambda t: (t.event_at, -1 if t.order is None else t.order, t.id)))
        if current != captured.trades:
            raise IntegrityError("known source revision requires rebuilding the measurement before publication")
        if type(view) is TransactionTapeView:
            resolved = view.ledger.asof(instrument=w.instrument, start=w.start, end=w.end, cut=publication_cut)
            bounded_rows(resolved, w.max_inputs)
            versions = tuple(sorted((r.root_key.id, r.version_hash) for r in resolved if r.value.event_at <= w.cut))
            if versions != w.source_versions:
                raise IntegrityError("known eligibility revision requires rebuilding the measurement")


class MeasurementPublisher:
    """Optional stateful publication boundary; coverage IDs cannot change bytes."""
    def __init__(self, *, max_publications=4096):
        self.max_publications = positive_limit(max_publications)
        self._coverage = {}
        self._publications = {}

    def publish(self, capture, *, view):
        validate_trade_window(capture, view)
        w = capture.window
        key = (w.instrument, w.coverage.source_version)
        old = self._coverage.get(key)
        if old is not None and old != w.coverage_id:
            raise IntegrityError("coverage source identity reused with different content")
        if capture.id not in self._publications and len(self._publications) >= self.max_publications:
            raise ContractError("measurement publication capacity exhausted")
        self._coverage[key] = w.coverage_id
        self._publications[capture.id] = capture
        return capture
