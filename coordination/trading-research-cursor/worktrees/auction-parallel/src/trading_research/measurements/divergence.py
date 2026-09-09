"""Source-bound price/flow disagreements and bounded descriptive residuals."""

from dataclasses import dataclass, field
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.foundations.intervals import IntervalGraph
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.measurements.cvd import CVDMeasurement, CohortMeasurement, _validate_cvd, measure_cohort_cvd
from trading_research.measurements.structure import validate_swing_snapshot
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class DivergenceEndpoint:
    instrument: str
    trading_date: str
    reset_id: str
    aggregation_unit: str
    cohort_id: str | None
    comparator: str
    side: str
    price: Fraction
    flow: Fraction | None
    extreme_at: int
    known_at: int
    anchor_start: int
    source_ids: tuple
    order_exact: bool
    history_complete: bool
    unknown_flow: Fraction
    _recipe: object = field(default=None, init=False, repr=False, compare=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())


def divergence_endpoint(*, swings, swing_id, cvd_result, cvd_capture, cvd_view,
                         comparator, trading_date, cohort=None, fit_binding=None):
    validate_swing_snapshot(swings)
    validate_trade_window(cvd_capture, cvd_view)
    bounded_name(trading_date)
    if comparator not in ("at_extremum", "window_extreme", "final_close"):
        raise ContractError("price/flow endpoint comparator must be named explicitly")
    nodes = [n for n in swings.confirmed if n.id == swing_id]
    provisional = [p for p in swings.provisional if p[3] == swing_id]
    if len(nodes) + len(provisional) != 1:
        raise ContractError("endpoint must identify one actual confirmed or running extremum")
    if nodes:
        n = nodes[0]
        side, price, at, known = n.side, n.price_ticks, n.extreme_start, n.confirmed_at
        extreme_source = n.extreme_source
        if n.extreme_end > n.extreme_start:
            matches = tuple(t for t in cvd_capture.trades if n.extreme_start <= t.event_at < n.extreme_end
                            and t.price is not None and t.price.value == price)
            if not matches:
                raise DependencyUnavailable("bar extremum has no matching actual cumulative-flow price event")
            at, extreme_source = matches[0].event_at, matches[0].id
        mode = "confirmed"
    else:
        p = provisional[0]
        side, price, at, known = p[0], p[1], p[2], swings.published_at
        extreme_source = p[3]
        mode = "running"
    w = cvd_capture.window
    if (swings.instrument != w.instrument or swings.reset_id != w.definition_version
            or not w.start <= at < w.end or w.cut > swings.cut or w.published_at > swings.published_at):
        raise ContractError("swing and CVD endpoint source domain/reset/availability differ")
    cohort_id = None
    if type(cvd_result) is CVDMeasurement:
        _validate_cvd(cvd_result, cvd_view)
        if cvd_result.capture_id != cvd_capture.id or cohort is not None:
            raise ContractError("ordinary endpoint differs from its actual CVD capture")
        opening, anchor_start, unknown = cvd_result.opening, cvd_result.anchor_start, Fraction(cvd_result.unknown)
        weights = (Fraction(1),) * len(cvd_capture.trades)
    elif type(cvd_result) is CohortMeasurement:
        definition = cvd_result.definition
        actual = measure_cohort_cvd(cvd_capture, view=cvd_view, definition=definition,
            openings=tuple(p.open for p in cvd_result.paths), opening_version=cvd_result.mathematical_opening_version,
            fit_binding=fit_binding)
        if actual != cvd_result:
            raise IntegrityError("cohort endpoint differs from its actual reconstructed path")
        indexes = [i for i, p in enumerate(actual.paths) if p.channel_id == cohort]
        if len(indexes) != 1:
            raise ContractError("cohort endpoint requires one actual channel")
        index = indexes[0]
        opening, anchor_start, unknown = actual.paths[index].open, w.start, actual.paths[index].unknown
        weights = tuple(definition.weights(t.size)[index] for t in cvd_capture.trades)
        cohort_id = digest((definition.id, cohort, actual.mathematical_opening_version))
    else:
        raise ContractError("endpoint requires an actual ordinary or cohort CVD result")
    running, path, at_extremum = opening, [(w.start, opening)], None
    for trade, weight in zip(cvd_capture.trades, weights):
        running += trade.signed * weight
        path.append((trade.event_at, running))
        if trade.id == extreme_source:
            at_extremum = running
    if comparator == "at_extremum":
        flow = at_extremum if w.order_exact and swings.order_exact else None
    elif comparator == "window_extreme":
        flow = (max if side == "high" else min)(v for _, v in path) if w.order_exact else None
    else:
        flow = running
    if not w.history_complete or unknown:
        flow = None
    result = DivergenceEndpoint(w.instrument, trading_date, swings.reset_id, w.aggregation_unit, cohort_id,
        mode + ":" + comparator, side, Fraction(price), flow, at,
        max(known, swings.published_at, w.published_at), anchor_start,
        (swings.id, cvd_capture.id), w.order_exact and swings.order_exact, w.history_complete, unknown)
    object.__setattr__(result, "_recipe", dict(swings=swings, swing_id=swing_id, cvd_result=cvd_result,
        cvd_capture=cvd_capture, cvd_view=cvd_view, comparator=comparator, trading_date=trading_date,
        cohort=cohort, fit_binding=fit_binding))
    return result


paired_endpoint = divergence_endpoint


def validate_endpoint(endpoint):
    if type(endpoint) is not DivergenceEndpoint or type(endpoint._recipe) is not dict:
        raise ContractError("actual endpoint recipe required")
    if divergence_endpoint(**endpoint._recipe) != endpoint:
        raise IntegrityError("divergence endpoint source or derived values changed")


@dataclass(frozen=True)
class DivergenceScales:
    price: Fraction
    flow: Fraction
    known_at: int
    source_ids: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)


def preceding_divergence_scales(capture, *, view):
    validate_trade_window(capture, view)
    if not capture.window.history_complete or not capture.window.order_exact or capture.window.unpriced_volume:
        raise DependencyUnavailable("normalization requires preceding complete observed prices")
    prices = [t.price.value for t in capture.trades]
    moves = [abs(b-a) for a, b in zip(prices, prices[1:])]
    flow = [abs(t.signed) for t in capture.trades if t.side is not None]
    if not moves or not flow:
        raise DependencyUnavailable("missing preceding scale observations")
    result = DivergenceScales(Fraction(sum(moves), len(moves)), Fraction(sum(flow), len(flow)),
                              capture.window.published_at, (capture.id,))
    object.__setattr__(result, "_recipe", (capture, view))
    return result


def compare_divergence(a, b, *, cut, scales, tolerance_ticks=0):
    validate_endpoint(a)
    validate_endpoint(b)
    timestamp(cut)
    if type(scales) is not DivergenceScales or type(scales._recipe) is not tuple:
        raise ContractError("actual preceding normalization capture required")
    c, view = scales._recipe
    if preceding_divergence_scales(c, view=view) != scales:
        raise IntegrityError("divergence scale differs from actual preceding source")
    keys = ("instrument", "trading_date", "reset_id", "aggregation_unit", "cohort_id", "comparator", "side", "anchor_start")
    if any(getattr(a, k) != getattr(b, k) for k in keys) or a.extreme_at >= b.extreme_at:
        raise ContractError("divergence endpoints do not share one ordered reference definition")
    if scales.known_at > a.extreme_at or max(a.known_at, b.known_at) > cut:
        raise DependencyUnavailable("endpoint or preceding scales unavailable at comparison cut")
    if type(tolerance_ticks) is not int or tolerance_ticks < 0:
        raise ContractError("price tie tolerance must be exact nonnegative ticks")
    dp = b.price - a.price
    df = None if a.flow is None or b.flow is None else b.flow - a.flow
    pn = dp / scales.price if scales.price else None
    fn = df / scales.flow if df is not None and scales.flow else None
    tie = abs(dp) <= tolerance_ticks or df == 0
    regular = hidden = None
    if df is not None:
        regular = not tie and ((dp > 0 and df < 0) if a.side == "high" else (dp < 0 and df > 0))
        hidden = not tie and ((dp < 0 and df > 0) if a.side == "high" else (dp > 0 and df < 0))
    duration = b.extreme_at - a.extreme_at
    return {"endpoints": (a.id, b.id), "price_change": dp, "flow_change": df,
        "normalized_price_change": pn, "normalized_flow_change": fn,
        "discrepancy": None if fn is None or pn is None else pn-fn, "price_slope": dp/duration,
        "flow_slope": None if df is None else df/duration, "duration_ns": duration,
        "regular": regular, "hidden": hidden, "tie": tie,
        "anchor_age": b.extreme_at-b.anchor_start, "confirmation_delay": b.known_at-b.extreme_at,
        "known_at": max(a.known_at, b.known_at), "order_exact": a.order_exact and b.order_exact,
        "history_complete": a.history_complete and b.history_complete}


@dataclass(frozen=True)
class DeclaredBreachReference:
    version: str
    receiver_ticks: Fraction
    source_ticks: Fraction
    side: str
    frozen_at: int

    def __post_init__(self):
        bounded_name(self.version)
        timestamp(self.frozen_at)
        if self.side not in ("high", "low") or any(type(x) not in (int, Fraction) for x in (self.receiver_ticks, self.source_ticks)):
            raise ContractError("breach references require exact frozen coordinates and side")


def compare_reference_breaches(receiver, source, *, receiver_view, source_view, references,
                               opportunity, cut, alignment):
    for capture, view in ((receiver, receiver_view), (source, source_view)):
        validate_trade_window(capture, view)
    if type(references) is not DeclaredBreachReference:
        raise ContractError("previously declared typed references required")
    references.__post_init__()
    if type(opportunity) is not tuple or len(opportunity) != 2 or type(opportunity[0]) is not IntervalGraph:
        raise ContractError("breach opportunity requires actual F03 named interval graph")
    graph, name = opportunity
    interval = graph.intervals.get(name)
    if interval is None or max(graph.known_at, interval.known_at) > cut:
        raise DependencyUnavailable("common opportunity interval unavailable")
    if type(alignment) is not tuple or len(alignment) != 3:
        raise ContractError("alignment must name both exact raw domains and its frozen definition")
    if alignment[:2] != (receiver.window.instrument, source.window.instrument):
        raise ContractError("breach alignment raw domains differ")
    bounded_name(alignment[2])
    earliest = min(receiver.window.start, source.window.start)
    if references.frozen_at > earliest:
        raise ContractError("breach reference was selected after the opportunity began")
    observed_cut = min(cut, receiver.window.cut, source.window.cut)
    spans = tuple((s.start, min(s.end, observed_cut)) for s in interval.spans if s.start < observed_cut)
    def measure(c, level):
        w = c.window
        available = w.published_at <= cut and w.coverage.known_at <= cut
        available &= all(w.start <= a < b <= w.end and any(x <= a < b <= y for x, y in w.coverage.observed_intervals) for a, b in spans)
        relevant = tuple(t for t in c.trades if t.event_at <= observed_cut and any(s.start <= t.event_at < s.end for s in interval.spans))
        available &= all(t.history_complete and t.price is not None for t in relevant)
        if not available or not spans:
            return {"breach": None, "nonbreach": None, "event_at": None, "known_at": None}
        hits = [t for t in relevant if (t.price.value > level if references.side == "high" else t.price.value < level)]
        if not hits and (not w.history_complete or any(s.end > observed_cut for s in interval.spans)):
            return {"breach": None, "nonbreach": None, "event_at": None, "known_at": None}
        first = hits[0] if hits else None
        return {"breach": bool(hits), "nonbreach": not hits, "event_at": None if first is None else first.event_at,
                "known_at": None if first is None else first.known_at}
    r, s = measure(receiver, references.receiver_ticks), measure(source, references.source_ticks)
    times = r["event_at"] is not None and s["event_at"] is not None
    exact = receiver.window.order_exact and source.window.order_exact
    return {"receiver": r, "source": s, "available": r["breach"] is not None and s["breach"] is not None,
        "event_lag": s["event_at"]-r["event_at"] if times and exact else None,
        "knowledge_lag": s["known_at"]-r["known_at"] if times else None,
        "known_at": max(receiver.window.published_at, source.window.published_at), "opportunity_version": interval.version}


def residual_basis(x, lag, basis):
    bounded_rows(x, 16, name="residual inputs")
    bounded_rows(basis, 16, name="residual basis")
    if type(lag) not in (int, Fraction) or any(type(v) not in (int, Fraction) for v in x):
        raise ContractError("residual coordinates require exact rational values")
    values = {"intercept": Fraction(1), "lag": Fraction(lag)}
    values.update({f"x{i}": Fraction(v) for i, v in enumerate(x)})
    values.update({f"x{i}*lag": Fraction(v)*lag for i, v in enumerate(x)})
    values.update({f"x{i}*x{j}": Fraction(x[i])*x[j] for i in range(len(x)) for j in range(i+1, len(x))})
    if not basis or len(set(basis)) != len(basis) or any(k not in values for k in basis):
        raise ContractError("residual basis contains an unsupported or duplicate column")
    return tuple(values[k] for k in basis)


@dataclass(frozen=True)
class RidgeResidual:
    coefficients: tuple
    basis: tuple
    ridge: Fraction
    train_end: int
    available_at: int
    row_ids: tuple
    recipe_id: str


def fit_divergence_residual(rows, *, train_end, available_at, ridge, basis, max_training_rows=1024):
    """Unpublished exact ridge kernel; rows=(id, x, lag, y, known_at)."""
    bounded_rows(rows, max_training_rows, name="ridge training rows")
    bounded_rows(basis, 16, name="ridge basis")
    timestamp(train_end)
    timestamp(available_at)
    if not rows or available_at < train_end or type(ridge) not in (int, Fraction) or ridge < 0:
        raise ContractError("ridge fit requires finite preceding training rows and nonnegative penalty")
    n = len(basis)
    matrix = [[Fraction(ridge if i == j else 0) for j in range(n)] + [Fraction(0)] for i in range(n)]
    ids, width = [], None
    for row in rows:
        if type(row) is not tuple or len(row) != 5:
            raise ContractError("ridge row schema differs")
        identity, x, lag, y, known = row
        bounded_rows(x, 16, name="ridge row features")
        if width is not None and len(x) != width:
            raise ContractError("residual training feature dimensions differ")
        width = len(x)
        bounded_name(identity)
        timestamp(known)
        if known > train_end or type(y) not in (int, Fraction):
            raise ContractError("ridge training row was unavailable or is not exact")
        z = residual_basis(x, lag, basis)
        ids.append(identity)
        for i in range(n):
            for j in range(n):
                matrix[i][j] += z[i]*z[j]
            matrix[i][-1] += z[i]*y
    if len(set(ids)) != len(ids):
        raise ContractError("ridge fit repeats a training identity")
    for i in range(n):
        pivot = next((j for j in range(i, n) if matrix[j][i]), None)
        if pivot is None:
            raise DependencyUnavailable("singular residual basis needs a separately registered recipe")
        matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
        scale = matrix[i][i]
        matrix[i] = [v/scale for v in matrix[i]]
        for j in range(n):
            if j != i:
                scale = matrix[j][i]
                matrix[j] = [a-scale*b for a, b in zip(matrix[j], matrix[i])]
    recipe_id = digest({"rows": rows, "train_end": train_end, "available_at": available_at,
                        "ridge": ridge, "basis": tuple(basis)})
    return RidgeResidual(tuple(row[-1] for row in matrix), tuple(basis), Fraction(ridge), train_end,
                          available_at, tuple(ids), recipe_id)


def apply_divergence_residual(admission, *, query_session, window_start, residual_scale=None):
    from trading_research.measurements.measurement_fits import reconstruct_numeric_measurement_fit, read_measurement_query
    state, parameters = reconstruct_numeric_measurement_fit(admission, family="divergence_residual")
    query = read_measurement_query(admission, query_session, window_start=window_start,
                                  columns=tuple(parameters["x_columns"]) + (parameters["lag_column"], parameters["y_column"]))
    x = tuple(query[k] for k in parameters["x_columns"])
    observed = query[parameters["y_column"]]
    vector = residual_basis(x, query[parameters["lag_column"]], state.basis)
    expected = sum(b*x for b, x in zip(state.coefficients, vector))
    if residual_scale is not None:
        raise ContractError("standardized residual needs its own actual retained fitted scale")
    return {"observed": observed, "expected": expected, "residual": observed-expected,
            "standardized_residual": None, "fit_recipe_id": state.recipe_id}
