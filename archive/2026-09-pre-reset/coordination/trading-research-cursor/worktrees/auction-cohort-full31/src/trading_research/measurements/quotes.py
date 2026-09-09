"""Best-quote pressure and net displayed recovery under explicit observability."""

from dataclasses import dataclass, field
from fractions import Fraction

from trading_research.data.book import Transition
from trading_research.data.events import CanonicalEvent, Flags, Quote
from trading_research.errors import ContractError, DependencyUnavailable


@dataclass(frozen=True)
class QuoteMetrics:
    ofi_contracts: int
    queue_imbalance: Fraction
    microprice_points: Fraction
    spread_points: Fraction


def quote_metrics(previous: Quote, current: Quote) -> QuoteMetrics:
    if not previous.valid or not current.valid:
        raise DependencyUnavailable("quote-state metrics require validated noncrossed positive-size BBOs")
    b, a, bp, ap = current.bid, current.ask, previous.bid, previous.ask
    qb, qa, qbp, qap = current.bid_size, current.ask_size, previous.bid_size, previous.ask_size
    ofi = int(b >= bp) * qb - int(b <= bp) * qbp - int(a <= ap) * qa + int(a >= ap) * qap
    return QuoteMetrics(ofi, Fraction(qb - qa, qb + qa),
                        (Fraction(a) * qb + Fraction(b) * qa) / (qb + qa), Fraction(a) - Fraction(b))


def transition_metrics(event: CanonicalEvent, transition: Transition) -> QuoteMetrics | None:
    if transition.event_id != event.id:
        raise ContractError("quote metric transition and source event disagree")
    if (transition.duplicate or event.action not in {"A", "M", "C"}
            or event.flags & (Flags.SNAPSHOT | Flags.MAYBE_BAD_BOOK)
            or not transition.before.trusted or not transition.after.trusted):
        return None
    return quote_metrics(transition.before.quote, transition.after.quote)


@dataclass(frozen=True)
class RecoveryInterval:
    previous: Quote
    current: Quote
    executed_at_bid: int
    executed_at_ask: int
    source_event_ids: tuple[str, ...]
    ordering_certificate_id: str | None
    bid_price_constant: bool
    ask_price_constant: bool
    hidden_or_unknown_execution: bool

    def __post_init__(self):
        if (any(type(v) is not int or v < 0 for v in (self.executed_at_bid, self.executed_at_ask))
                or not self.source_event_ids or len(set(self.source_event_ids)) != len(self.source_event_ids)):
            raise ContractError("recovery bundle needs unique observed events and exact eligible execution totals")


@dataclass(frozen=True)
class NetRecovery:
    bid_net_additions: int | None
    ask_net_additions: int | None
    interpretation: str
    ambiguous_reason: str | None


def net_displayed_recovery(interval: RecoveryInterval) -> NetRecovery:
    if (not interval.previous.valid or not interval.current.valid or not interval.ordering_certificate_id
            or interval.hidden_or_unknown_execution):
        return NetRecovery(None, None, "net displayed nontrade change only", "unreconciled ordering, hidden/unknown execution or invalid quote")
    bid = (interval.current.bid_size - interval.previous.bid_size + interval.executed_at_bid
           if interval.bid_price_constant and interval.current.bid == interval.previous.bid else None)
    ask = (interval.current.ask_size - interval.previous.ask_size + interval.executed_at_ask
           if interval.ask_price_constant and interval.current.ask == interval.previous.ask else None)
    return NetRecovery(bid, ask, "net displayed additions minus cancellations; gross refill/cancel and identity are not identified",
                       "best price changed inside the interval" if bid is None or ask is None else None)


# The small functions above remain the literal comparators. The production
# boundary below retains and redecodes the actual F01 input before each read.
from itertools import groupby
from trading_research.data.book import BookReducer
from trading_research.data.events import SourceAddress, LatencyScenario, decode_fields, encode_fields, normalize_mbp
from trading_research.errors import IntegrityError
from trading_research.foundations.bars import WindowCoverage
from trading_research.foundations.instruments import InstrumentRegistry
from trading_research.foundations.object_graph import Instrument
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import FuturesTerms
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class MBPEventRecipe:
    fields: bytes
    address: SourceAddress
    native: bool
    scenario: LatencyScenario | None
    strategy_received_at: int | None = None
    raw_record: bytes | None = None

    def __post_init__(self):
        if type(self.fields) is dict:
            object.__setattr__(self, "fields", encode_fields(self.fields))
        if (type(self.fields) is not bytes or len(self.fields) > 8388608
                or type(self.address) is not SourceAddress or type(self.native) is not bool
                or self.scenario is not None and type(self.scenario) is not LatencyScenario
                or self.raw_record is not None and (type(self.raw_record) is not bytes or len(self.raw_record) > 8388608)):
            raise ContractError("MBP recipe needs bounded lossless raw fields and normalization inputs")

    def decode(self):
        self.__post_init__()
        return normalize_mbp(decode_fields(self.fields), self.address, native=self.native, scenario=self.scenario,
                             strategy_received_at=self.strategy_received_at, raw_record=self.raw_record)


@dataclass(frozen=True)
class QuoteCapture:
    recipes: tuple
    initial_recipes: tuple
    instrument: Instrument
    terms: FuturesTerms
    start: int
    end: int
    cut: int
    published_at: int
    coverage: WindowCoverage
    definition: str
    events: tuple
    transitions: tuple
    initial_state: object
    terminal_state: object
    order_exact: bool
    max_inputs: int
    max_bytes: int
    _mapping: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        # Retain lossless normalization inputs once. Events and reducer states
        # are reproducible projections, bound by an exact digest of that replay.
        result = {k: getattr(self, k) for k in self.__dataclass_fields__
                  if k not in ("_mapping", "events", "transitions")}
        result['projection_digest'] = digest((self.events, self.transitions))
        return result

    @property
    def id(self):
        return digest(self.record())


def capture_quote_window(recipes, *, mapping, terms, instrument, start, end, cut, published_at,
                         coverage, definition, initial_recipes=(), max_inputs=4096, max_bytes=8388608):
    bounded_rows(recipes, max_inputs, name="quote normalization recipes")
    bounded_rows(initial_recipes, max_inputs, name="initial quote recipes")
    positive_limit(max_bytes)
    if len(recipes) + len(initial_recipes) > max_inputs:
        raise ContractError("combined quote recipe capacity exhausted")
    if (type(mapping) is not InstrumentRegistry or type(instrument) is not Instrument
            or type(terms) is not FuturesTerms or type(coverage) is not WindowCoverage):
        raise ContractError("quote capture requires actual F02 registry, terms, instrument and coverage")
    instrument.__post_init__()
    coverage.__post_init__()
    bounded_name(definition)
    for at in (start, end, cut, published_at):
        timestamp(at)
    if start >= end or cut < start or published_at < cut or not instrument.valid(cut):
        raise ContractError("quote interval, instrument lifetime or publication is invalid")
    if ((coverage.instrument, coverage.start, coverage.end) != (instrument.raw_symbol, start, end)
            or coverage.known_at > cut):
        raise ContractError("quote coverage identity or availability differs")
    if len(canonical_json((recipes, initial_recipes))) > max_bytes:
        raise ContractError("quote input bytes exceed capacity before decoding")
    selected = [[], []]
    for index, source in enumerate((initial_recipes, recipes)):
        for recipe in source:
            if type(recipe) is not MBPEventRecipe:
                raise ContractError("detached normalized events cannot authenticate quote history")
            event = recipe.decode()
            if event.clocks.known_at > cut or event.clocks.event_at > cut:
                continue
            at = event.clocks.event_at
            if (index == 0 and at >= start) or (index == 1 and not start <= at < end):
                raise ContractError("quote recipe is outside its declared initial/window interval")
            resolved = mapping.resolve(provider=instrument.provider, venue=instrument.venue,
                instrument_id=str(event.instrument_id), valid_at=at, known_at=cut)
            if (resolved is None or str(event.instrument_id) != instrument.raw_id
                    or resolved.key.raw_symbol != instrument.raw_symbol
                    or resolved.key.definition_version != instrument.definition_version
                    or (resolved.key.provider, resolved.key.venue, resolved.key.expiry_at,
                        resolved.clocks.valid_from, resolved.clocks.valid_until) !=
                       (instrument.provider, instrument.venue, instrument.expiry_at,
                        instrument.valid_from, instrument.valid_until)
                    or resolved.futures_terms() != terms
                    or Fraction(terms.tick_size) != instrument.tick_size_points):
                raise ContractError("decoded quote differs from the actual raw-instrument mapping/terms")
            from trading_research.measurements.common import _covered
            if index == 1 and not _covered(at, coverage, cut=cut):
                raise ContractError("quote event conflicts with observed coverage")
            selected[index].append((recipe, event))
    # Arrival order is retained. A provider sequence only certifies ordering
    # within the same stream; it never orders unrelated sources.
    for rows in selected:
        rows.sort(key=lambda pair: (pair[1].clocks.known_at, pair[1].address.row, pair[1].id))
    reducer = BookReducer()
    for _, event in selected[0]:
        reducer.apply(event)
    from trading_research.data.book import BookState
    initial = reducer.states.get(int(instrument.raw_id), BookState(int(instrument.raw_id)))
    transitions = tuple(reducer.apply(event) for _, event in selected[1])
    terminal = reducer.states.get(int(instrument.raw_id), initial)
    unique = tuple(e for (_, e), tr in zip(selected[1], transitions) if not tr.duplicate)
    exact = True
    for _, group in groupby(sorted(unique, key=lambda e: e.clocks.event_at), key=lambda e: e.clocks.event_at):
        batch = tuple(group)
        if len(batch) > 1:
            streams = {(e.address.dataset_id, e.address.partition, e.publisher_id) for e in batch}
            seqs = [e.provider_sequence for e in batch]
            exact &= len(streams) == 1 and None not in seqs and len(set(seqs)) == len(seqs)
    exact &= all(a.clocks.event_at <= b.clocks.event_at for a, b in zip(unique, unique[1:]))
    result = QuoteCapture(tuple(r for r, _ in selected[1]), tuple(r for r, _ in selected[0]), instrument, terms,
        start, end, cut, published_at, coverage, definition, tuple(e for _, e in selected[1]), transitions,
        initial, terminal, bool(exact), max_inputs, max_bytes)
    object.__setattr__(result, "_mapping", mapping)
    if len(canonical_json(result.record())) > max_bytes:
        raise ContractError("quote capture byte capacity exhausted")
    return result


def validate_quote_capture(capture):
    if type(capture) is not QuoteCapture or type(capture._mapping) is not InstrumentRegistry:
        raise ContractError("actual retained quote recipe required")
    fresh = capture_quote_window(capture.recipes, mapping=capture._mapping,
        **{k: getattr(capture, k) for k in ("terms", "instrument", "start", "end", "cut", "published_at",
            "coverage", "definition", "initial_recipes", "max_inputs", "max_bytes")})
    if fresh != capture:
        raise IntegrityError("quote capture differs from its original decoding and replay")


@dataclass(frozen=True)
class QuoteSummary:
    capture_id: str
    instrument: str
    start: int
    end: int
    cut: int
    published_at: int
    initial_midpoint: Fraction | None
    terminal_midpoint: Fraction | None
    spread_change: Fraction | None
    depth_change: int | None
    initial_quote_at: int | None
    terminal_quote_at: int | None
    strictly_prewindow: bool
    history_complete: bool
    order_exact: bool
    source_ids: tuple

    @property
    def id(self):
        return digest(self)


def quote_summary(capture):
    validate_quote_capture(capture)
    initial, terminal = capture.initial_state, capture.terminal_state
    if not initial.trusted:
        initial = next((t.after for e, t in zip(capture.events, capture.transitions)
                        if not t.duplicate and t.after.trusted and not e.flags & Flags.SNAPSHOT), initial)
    def values(state):
        if not state.trusted or not state.quote or not state.quote.valid:
            return None, None, None
        q, tick = state.quote, Fraction(capture.terms.tick_size)
        return (Fraction(q.bid) + Fraction(q.ask)) / (2 * tick), (Fraction(q.ask) - Fraction(q.bid)) / tick, q.bid_size + q.ask_size
    im, isp, idepth = values(initial)
    tm, tsp, tdepth = values(terminal)
    return QuoteSummary(capture.id, capture.instrument.raw_symbol, capture.start, capture.end, capture.cut,
        capture.published_at, im, tm, None if isp is None or tsp is None else tsp - isp,
        None if idepth is None or tdepth is None else tdepth - idepth,
        initial.economic_quote_at, terminal.economic_quote_at,
        initial.economic_quote_at is not None and initial.economic_quote_at < capture.start,
        capture.coverage.complete and terminal.flow_complete, capture.order_exact,
        tuple(e.id for e, t in zip(capture.events, capture.transitions) if not t.duplicate))


def validate_quote_summary(summary, capture):
    if type(summary) is not QuoteSummary or quote_summary(capture) != summary:
        raise IntegrityError("quote summary differs from its actual source capture")


def measure_quote_pressure(capture, *, kernels=()):
    validate_quote_capture(capture)
    bounded_rows(kernels, 32, name="quote lag kernels")
    output, normalized, imbalance_updates = [], Fraction(0), []
    exposures = []
    standing = capture.initial_state
    at = capture.start
    for event, tr in zip(capture.events, capture.transitions):
        if tr.duplicate:
            continue
        endpoint = min(event.clocks.event_at, capture.end, capture.cut)
        if capture.order_exact and standing.trusted and standing.economic_quote_at is not None and standing.quote.valid:
            q = standing.quote
            weight = sum(max(0, min(endpoint, b) - max(at, a)) for a, b in capture.coverage.observed_intervals)
            if weight:
                exposures.append((weight, Fraction(q.bid_size - q.ask_size, q.bid_size + q.ask_size)))
        value = transition_metrics(event, tr)
        same = price = None
        if value is not None:
            p, q = tr.before.quote, tr.after.quote
            same = (q.bid_size - p.bid_size if q.bid == p.bid else 0) - (q.ask_size - p.ask_size if q.ask == p.ask else 0)
            price = value.ofi_contracts - same
            normalized += Fraction(value.ofi_contracts, p.bid_size + p.ask_size)
            imbalance_updates.append(value.queue_imbalance)
        output.append((event.id, event.clocks.event_at, value, same, price))
        standing, at = tr.after, endpoint
    endpoint = min(capture.end, capture.cut)
    if capture.order_exact and standing.trusted and standing.economic_quote_at is not None and standing.quote.valid:
        q = standing.quote
        weight = sum(max(0, min(endpoint, b) - max(at, a)) for a, b in capture.coverage.observed_intervals)
        if weight:
            exposures.append((weight, Fraction(q.bid_size - q.ask_size, q.bid_size + q.ask_size)))
    observed = [row[2] for row in output if row[2] is not None]
    total = sum(m.ofi_contracts for m in observed)
    duration = sum(w for w, _ in exposures)
    covered = capture.coverage.observed_duration
    result = {"capture_id": capture.id, "transitions": tuple(output), "raw_ofi": total,
        "fresh_pressure_update_count": len(observed), "per_update": Fraction(total, len(observed)) if observed else None,
        "per_second": Fraction(total * 1000000000, covered) if covered else None,
        "sum_depth_normalized": normalized, "exposure_ns": duration,
        "mean_imbalance": sum(w * q for w, q in exposures) / duration if duration else None,
        "positive_duration_fraction": Fraction(sum(w for w, q in exposures if q > 0), duration) if duration else None,
        "update_positive_fraction": Fraction(sum(q > 0 for q in imbalance_updates), len(imbalance_updates)) if imbalance_updates else None,
        "history_complete": capture.coverage.complete and capture.terminal_state.flow_complete,
        "order_exact": capture.order_exact}
    result["lag_channels"] = tuple(_quote_lag(capture, output, k) for k in kernels)
    return result


def _quote_lag(capture, pressure_rows, kernel):
    if type(kernel) is not tuple or len(kernel) != 2 or kernel[0] not in ("half_life", "box") or kernel[1] <= 0:
        raise ContractError("lag kernel needs a frozen kind and positive time scale")
    if not capture.order_exact:
        return {"kernel": kernel, "ofi": None, "trade": None, "product": None}
    def weight(at):
        age = capture.cut - at
        return (1 if age <= kernel[1] else 0) if kernel[0] == "box" else 2 ** (-age / kernel[1])
    ofi = sum(weight(at) * m.ofi_contracts for _, at, m, _, _ in pressure_rows if m is not None)
    trade = sum(weight(e.clocks.event_at) * e.size * e.aggressor for e, t in zip(capture.events, capture.transitions)
                if not t.duplicate and e.trade_eligible and e.aggressor is not None)
    return {"kernel": kernel, "ofi": ofi, "trade": trade, "product": ofi * trade}


def recovery_episodes(capture, *, definition=("constant_touch_v1", Fraction(1, 2))):
    validate_quote_capture(capture)
    if type(definition) is not tuple or len(definition) != 2 or not 0 < definition[1] <= 1:
        raise ContractError("recovery needs a frozen positive fractional crossing definition")
    bounded_name(definition[0])
    episodes, live = [], {}
    def start(side, state, at):
        if not state.trusted or not state.quote or not state.quote.valid:
            return None
        q = state.quote
        depth = q.bid_size if side == "bid" else q.ask_size
        return {"side": side, "price": q.bid if side == "bid" else q.ask, "start": at, "end": at,
            "initial_depth": depth, "terminal_depth": depth, "minimum_depth": depth, "executed": 0,
            "unknown_execution": 0, "depletion_at": None, "initial_depletion": None,
            "recovery_at": None, "full_recovery_at": None, "source_ids": []}
    def finish(ep):
        if ep is None:
            return
        net = ep["terminal_depth"] - ep["initial_depth"] + ep["executed"]
        exact = capture.coverage.complete and capture.order_exact and capture.terminal_state.flow_complete and not ep["unknown_execution"]
        episodes.append({**ep, "source_ids": tuple(ep["source_ids"]), "observed_known_execution_net": net,
            "exact_net": net if exact else None,
            "recovery_at": ep["recovery_at"] if exact else None,
            "full_recovery_at": ep["full_recovery_at"] if exact else None,
            "gross_additions": None, "gross_cancellations": None})
    for side in ("bid", "ask"):
        live[side] = start(side, capture.initial_state, capture.start)
    for e, tr in zip(capture.events, capture.transitions):
        if tr.duplicate:
            continue
        for side in ("bid", "ask"):
            ep = live[side]
            if e.trade_eligible and ep is not None:
                correct_side = e.aggressor == (-1 if side == "bid" else 1)
                if correct_side and e.price == ep["price"]:
                    ep["executed"] += e.size
                elif e.aggressor is None or correct_side:
                    ep["unknown_execution"] += e.size
                ep["source_ids"].append(e.id)
            if e.action not in {"A", "M", "C", "R"} or e.flags & Flags.SNAPSHOT:
                continue
            q = tr.after.quote
            price = None if not tr.after.trusted or not q or not q.valid else (q.bid if side == "bid" else q.ask)
            if ep is None or ep["price"] != price:
                finish(ep)
                live[side] = start(side, tr.after, e.clocks.event_at)
                continue
            depth = q.bid_size if side == "bid" else q.ask_size
            ep["end"], ep["terminal_depth"] = e.clocks.event_at, depth
            ep["source_ids"].append(e.id)
            ep["minimum_depth"] = min(ep["minimum_depth"], depth)
            if ep["depletion_at"] is None and depth < ep["initial_depth"]:
                ep["depletion_at"] = e.clocks.event_at
                ep["initial_depletion"] = ep["initial_depth"] - depth
            elif ep["depletion_at"] is not None:
                recovered = Fraction(depth - ep["minimum_depth"], ep["initial_depletion"])
                if recovered >= definition[1] and ep["recovery_at"] is None:
                    ep["recovery_at"] = e.clocks.event_at
                if depth >= ep["initial_depth"] and ep["full_recovery_at"] is None:
                    ep["full_recovery_at"] = e.clocks.event_at
    for ep in live.values():
        finish(ep)
    return tuple(episodes)


def apply_quote_lag(admission, *, query_session, window_start, capture):
    """Learned lag residual with actual quote and F11 source-read admission."""
    from trading_research.measurements.measurement_fits import reconstruct_numeric_measurement_fit, read_measurement_query
    from trading_research.measurements.divergence import residual_basis
    validate_quote_capture(capture)
    if window_start != capture.start or admission.request.decision_cut != capture.cut:
        raise ContractError("quote lag query differs from the actual quote observation window")
    state, parameters = reconstruct_numeric_measurement_fit(admission, family="quote_lag")
    columns = tuple(parameters["x_columns"]) + (parameters["lag_column"], parameters["y_column"], "quote_capture")
    query = read_measurement_query(admission, query_session, window_start=window_start, columns=columns)
    if canonical_json(query["quote_capture"]) != canonical_json(capture.record()):
        raise IntegrityError("quote lag query capture differs from its actual retained read")
    vector = residual_basis(tuple(query[k] for k in parameters["x_columns"]), query[parameters["lag_column"]], state.basis)
    expected = sum(b*x for b, x in zip(state.coefficients, vector))
    observed = query[parameters["y_column"]]
    return {"observed": observed, "expected": expected, "residual": observed-expected,
            "fit_recipe_id": state.recipe_id, "capture_id": capture.id}
