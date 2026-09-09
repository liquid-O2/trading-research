"""Calendar-bracket occupancy and explicitly estimated trade-price dwell."""

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import groupby

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.intervals import IntervalGraph
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.measurements.profiles import FrozenGrid, auction_sources
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class BracketSelection:
    interval_name: str
    interval_version: str
    graph_version: str
    bracket_ns: int
    cut: int
    brackets: tuple
    max_brackets: int
    _graph: object = field(default=None, init=False, compare=False, repr=False)


def select_brackets(interval_graph, interval_name, *, bracket_ns, cut, max_brackets=1024):
    positive_limit(bracket_ns)
    positive_limit(max_brackets)
    timestamp(cut)
    if type(interval_graph) is not IntervalGraph:
        raise ContractError("TPO brackets require the actual F03 interval graph")
    bounded_name(interval_name)
    interval = interval_graph.intervals.get(interval_name)
    if interval is None or max(interval.known_at, interval_graph.known_at) > cut:
        raise DependencyUnavailable("TPO named interval is unavailable")
    count = sum(max(0, (min(s.end, cut)-s.start+bracket_ns-1)//bracket_ns) for s in interval.spans)
    if count > max_brackets:
        raise ContractError("TPO bracket capacity exhausted before materialization")
    brackets = []
    for span in interval.spans:
        at = span.start
        while at < min(span.end, cut):
            end = min(at+bracket_ns, span.end)
            brackets.append((digest((interval.version, at, end)), at, end))
            at = end
    result = BracketSelection(interval_name, interval.version, interval_graph.version, bracket_ns, cut,
                              tuple(brackets), max_brackets)
    object.__setattr__(result, "_graph", interval_graph)
    return result


def validate_brackets(selection):
    if type(selection) is not BracketSelection:
        raise ContractError("typed actual calendar bracket selection required")
    fresh = select_brackets(selection._graph, selection.interval_name, bracket_ns=selection.bracket_ns,
                             cut=selection.cut, max_brackets=selection.max_brackets)
    if fresh != selection:
        raise IntegrityError("TPO brackets differ from the selected actual F03 interval")


@dataclass(frozen=True)
class TPOMeasurement:
    instrument: str
    grid: FrozenGrid
    selection_id: str
    source_capture_ids: tuple
    definition: str
    representation: str
    cut: int
    published_at: int
    rows: tuple
    brackets: tuple
    completed_brackets: int
    occupied_brackets: int
    history_complete: bool
    final: bool
    source_display_ready: bool
    provisional_single_rows: tuple
    confirmed_single_rows: tuple | None
    chronological_visits: tuple | None
    overflow_visits: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())


def measure_tpo(captures, *, views, anchors, graphs, grid, brackets, definition,
                minimum_brackets=5, representation="whole_trade_visits", published_at=None,max_bytes=8388608):
    positive_limit(minimum_brackets)
    bounded_name(definition)
    validate_brackets(brackets)
    members, _ = auction_sources(captures, views=views, anchors=anchors, graphs=graphs, grid=grid,max_bytes=max_bytes)
    if representation not in ("whole_trade_visits", "ohlc_range_proxy"):
        raise ContractError("TPO exact visits and OHLC range fill require distinct representations")
    cut = brackets.cut
    published_at = max(cut, *(c.window.published_at for c in captures), *(a.published_at for a in anchors)) if published_at is None else timestamp(published_at)
    if (any(c.window.cut > cut or c.window.published_at > published_at for c in captures)
            or any(a.published_at > published_at for a in anchors) or published_at < cut):
        raise ContractError("TPO source or computation is unavailable at publication")
    incidence, overflow, status, chronology = {}, set(), [], []
    selected = [(bid, a, b) for bid, a, b in brackets.brackets]
    for bid, a, b in selected:
        covered = (any(x <= a < b <= y for x, y in _coverage(captures))
                   and all(t.history_complete and t.price is not None for t in members if a <= t.event_at < b))
        complete = b <= cut and covered
        status.append((bid, a, b, "complete" if complete else "provisional" if a <= cut < b else "missing"))
        trades = [t for t in members if a <= t.event_at < b and t.event_at <= cut and t.price is not None]
        rows = {grid.row(t.price.value) for t in trades}
        if representation == "ohlc_range_proxy" and rows:
            if max(rows)-min(rows)+1 > grid.max_rows:
                raise ContractError("TPO range-fill proxy exceeds its finite row span")
            rows = set(range(min(rows), max(rows)+1))
        for row in rows:
            if grid.lower_row <= row <= grid.upper_row:
                incidence.setdefault(row, set()).add(bid)
            else:
                overflow.add((row, bid))
        previous = None
        for t in trades:
            row = grid.row(t.price.value)
            if row != previous:
                chronology.append((bid, row, t.event_at, t.id))
            previous = row
    complete_count = sum(s[-1] == "complete" for s in status)
    original = brackets._graph.intervals[brackets.interval_name]
    final = bool(original.spans) and cut >= original.spans[-1].end
    complete = all(s[-1] == "complete" for s in status) and all(c.window.history_complete and not c.window.unpriced_volume for c in captures)
    single = tuple(sorted(row for row, ids in incidence.items() if len(ids) == 1))
    ready = complete_count >= minimum_brackets
    ordered = all(c.window.order_exact for c in captures)
    result = TPOMeasurement(captures[0].window.instrument, grid, digest((brackets.interval_version, brackets.brackets)),
        tuple(c.id for c in captures), definition, representation, cut, published_at,
        tuple((row, tuple(sorted(ids))) for row, ids in sorted(incidence.items())), tuple(status), complete_count,
        len({bid for ids in incidence.values() for bid in ids}), complete, final, ready, single,
        single if final and complete and ready else None, tuple(chronology) if ordered else None, tuple(sorted(overflow)))
    if len(canonical_json(result.record()))>max_bytes:
        raise ContractError('TPO result exceeds its retained byte capacity')
    object.__setattr__(result, "_recipe", dict(captures=tuple(captures), views=tuple(views), anchors=tuple(anchors), graphs=tuple(graphs),
        grid=grid, brackets=brackets, definition=definition, minimum_brackets=minimum_brackets,
        representation=representation, published_at=published_at,max_bytes=max_bytes))
    return result


def _coverage(captures):
    from trading_research.measurements.profiles import union_intervals
    return union_intervals(tuple(span for c in captures for span in c.window.coverage.observed_intervals))


def validate_tpo(value):
    if type(value) is not TPOMeasurement or type(value._recipe) is not dict or measure_tpo(**value._recipe) != value:
        raise IntegrityError("TPO differs from its actual source/calendar recipe")


def tpo_tails(value):
    validate_tpo(value)
    rows = dict(value.rows)
    if not rows:
        return {"low": (), "high": (), "low_same_letter": None, "high_same_letter": None}
    tails = []
    for at, step in ((min(rows), 1), (max(rows), -1)):
        tail = []
        while at in rows and len(rows[at]) == 1:
            tail.append(at)
            at += step
        tails.append(tuple(sorted(tail)))
    return {"low": tails[0], "high": tails[1],
        "low_same_letter": len({rows[r][0] for r in tails[0]}) == 1 if tails[0] else None,
        "high_same_letter": len({rows[r][0] for r in tails[1]}) == 1 if tails[1] else None}


def estimate_dwell(capture, *, view, grid, stale_cap_ns):
    validate_trade_window(capture, view)
    if type(grid) is not FrozenGrid:
        raise ContractError("dwell needs a fixed exact grid")
    grid.__post_init__()
    positive_limit(stale_cap_ns)
    if grid.known_at > capture.window.start:
        raise ContractError("dwell grid was unavailable at window start")
    w = capture.window
    groups = tuple((at, tuple(g)) for at, g in groupby(capture.trades, key=lambda t: t.event_at))
    durations, ambiguous, overflow = {}, 0, 0
    for i, (at, batch) in enumerate(groups):
        until = min(w.end, w.cut, groups[i+1][0] if i+1 < len(groups) else w.end, at+stale_cap_ns)
        containing = next(((a, b) for a, b in w.coverage.observed_intervals if a <= at < b), None)
        if containing is None:
            continue
        until = min(until, containing[1])
        duration = max(0, until-at)
        ordered = len(batch) == 1 or all(t.order is not None for t in batch) and len({t.order for t in batch}) == len(batch)
        if not ordered and len({t.price for t in batch}) != 1:
            ambiguous += duration
            continue
        trade = max(batch, key=lambda t: -1 if t.order is None else t.order)
        if trade.price is None or not all(t.history_complete for t in batch):
            continue
        row = grid.row(trade.price.value)
        if grid.lower_row <= row <= grid.upper_row:
            durations[row] = durations.get(row, 0)+duration
        else:
            overflow += duration
    exposure = sum(max(0, min(b, w.cut)-a) for a, b in w.coverage.observed_intervals)
    assigned = sum(durations.values())+overflow
    return {"duration_by_row": tuple(sorted(durations.items())), "overflow_duration": overflow,
        "covered_duration_ns": exposure, "unassigned_duration": exposure-assigned,
        "missing_duration_ns": min(w.end, w.cut)-w.start-exposure, "uncertain_order_duration_ns": ambiguous,
        "true_per_row_lower": 0, "true_per_row_upper": exposure,
        "method": "last_observed_trade_price_with_stale_cap", "capture_id": capture.id}


def displayed_quote_occupancy(capture, *, grid):
    from trading_research.measurements.quotes import validate_quote_capture
    validate_quote_capture(capture)
    if type(grid) is not FrozenGrid or grid.known_at > capture.start:
        raise ContractError("displayed quote occupancy requires an available fixed grid")
    if not capture.order_exact:
        return {"durations": None, "reason": "unknown_quote_path_order"}
    state, at, durations = capture.initial_state, capture.start, {}
    for event, transition in (*tuple(zip(capture.events, capture.transitions)), (None, None)):
        end = min(capture.end, capture.cut) if event is None else min(event.clocks.event_at, capture.end, capture.cut)
        if state.trusted and state.economic_quote_at is not None and state.quote and state.quote.valid:
            midpoint = (Fraction(state.quote.bid)+Fraction(state.quote.ask))/(2*Fraction(capture.terms.tick_size))
            row = grid.row(midpoint)
            duration = sum(max(0, min(end, b)-max(at, a)) for a, b in capture.coverage.observed_intervals)
            durations[row] = durations.get(row, 0)+duration
        if event is not None and not transition.duplicate:
            state, at = transition.after, end
    return {"durations": tuple(sorted(durations.items())), "capture_id": capture.id,
            "method": "observed_displayed_quote_midpoint", "trade_residence_claim": False}


def naked_reference(anchor, *, graph, level_ticks, price_capture, view, cut):
    from trading_research.measurements.anchored import validate_anchor
    validate_anchor(anchor, graph)
    validate_trade_window(price_capture, view)
    timestamp(cut)
    if type(level_ticks) not in (int, Fraction):
        raise ContractError("naked-reference level requires exact raw ticks")
    w = price_capture.window
    birth = anchor.anchor.known_at
    if w.instrument != anchor.instrument.raw_symbol or birth > cut or w.cut > cut or w.published_at > cut:
        raise ContractError("naked-reference source or anchor is unavailable at its historical query")
    contact = next((t for t in price_capture.trades if birth < t.event_at <= cut
                    and t.price is not None and t.price.value == level_ticks), None)
    complete = (cut == birth or any(a <= birth and b >= cut for a, b in w.coverage.observed_intervals))
    complete &= all(t.history_complete and t.price is not None for t in price_capture.trades)
    return {"naked": False if contact else True if complete else None,
            "first_touch_at": contact.event_at if contact else None, "birth": birth, "anchor_version": anchor.anchor.version_id}
