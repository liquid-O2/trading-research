"""Covered-exposure flow intensity and descriptive effort/progress transforms."""

from dataclasses import dataclass, replace
from fractions import Fraction
import math

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import NS, timestamp
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.measurements.cvd import exact_number
from trading_research.operations.artifacts import canonical_json, digest


def _rate(value, exposure):
    return Fraction(value * NS, exposure) if exposure else None


def _quantile(values, probability):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, (len(ordered) * probability.numerator + probability.denominator - 1) // probability.denominator - 1)
    return ordered[index]


@dataclass(frozen=True)
class TapeIntensity:
    capture_id: str
    covered_ns: int
    missing_ns: int
    count_per_sec: Fraction | None
    contracts_per_sec: Fraction | None
    signed_per_sec: Fraction | None
    unknown_per_sec: Fraction | None
    size_quantiles: tuple
    max_known_same_side_run: int | None
    final_known_run: int | None
    interarrival_ns: tuple
    first_ticks: Fraction | None
    last_ticks: Fraction | None
    high_ticks: int | None
    low_ticks: int | None
    progress_ticks: Fraction | None
    absolute_tick_movement: int | None
    tick_speed_per_sec: Fraction | None
    gross_effort: int
    signed_effort: int
    epsilon_contracts: Fraction
    effort_progress_ratio: Fraction | None
    zero_effort: bool
    history_complete: bool
    order_exact: bool
    quote_summary_id: str | None
    quote_spread_change: Fraction | None
    quote_depth_change: int | None


def measure_tape_intensity(capture, *, view, epsilon, price_origin=None, quote_summary=None):
    validate_trade_window(capture, view)
    epsilon = exact_number(epsilon)
    if epsilon <= 0:
        raise ContractError("effort epsilon must be a frozen positive contract quantity")
    if price_origin not in (None, "quote_mid"):
        raise ContractError("price origin must derive from observed trades or an authenticated quote capture")
    w, trades = capture.window, capture.trades
    values = tuple(t.price.value for t in trades if t.price is not None)
    path_supported = w.order_exact and len(values) == len(trades)
    first = Fraction(values[0]) if values and path_supported else None
    last = Fraction(values[-1]) if values and path_supported else None
    quote_id = spread = depth = None
    if quote_summary is not None:
        if type(quote_summary) is not tuple or len(quote_summary) != 2:
            raise ContractError("quote origin needs the actual quote capture and its summary")
        from trading_research.measurements.quotes import validate_quote_summary
        summary, quote_capture = quote_summary
        validate_quote_summary(summary, quote_capture)
        if ((summary.instrument, summary.start, summary.end, summary.cut) != (w.instrument, w.start, w.end, w.cut)
                or summary.published_at > w.published_at):
            raise ContractError("quote and flow observation windows/publications differ")
        quote_id, spread, depth = summary.id, summary.spread_change, summary.depth_change
        if price_origin == "quote_mid" or not trades:
            if (summary.initial_quote_at is None or summary.terminal_quote_at is None
                    or not summary.order_exact):
                first = last = None
            else:
                first, last = summary.initial_midpoint, summary.terminal_midpoint
    elif price_origin == "quote_mid":
        raise DependencyUnavailable("quote-origin progress requires retained quote evidence")
    progress = last - first if first is not None and last is not None else None
    movement = (sum(abs(b - a) for a, b in zip(values, values[1:]))
                if path_supported and values and w.history_complete else None)
    maximum_run = current_run = 0
    previous_side = previous_span = previous_at = None
    interarrival = []
    for trade in trades:
        span = next((i for i, (a, b) in enumerate(w.coverage.observed_intervals)
                     if a <= trade.event_at < b or trade.event_at == w.cut == b), -1)
        if span == previous_span and previous_at is not None:
            interarrival.append(trade.event_at - previous_at)
        if trade.side is None:
            current_run, previous_side = 0, None
        else:
            current_run = current_run + 1 if trade.side == previous_side and span == previous_span else 1
            previous_side = trade.side
            maximum_run = max(maximum_run, current_run)
        previous_span, previous_at = span, trade.event_at
    return TapeIntensity(capture.id, w.observed_duration_ns, w.end - w.start - w.observed_duration_ns,
        _rate(w.print_count, w.observed_duration_ns), _rate(w.eligible_volume, w.observed_duration_ns),
        _rate(w.signed, w.observed_duration_ns), _rate(w.unknown_volume, w.observed_duration_ns),
        tuple((p, _quantile(tuple(t.size for t in trades), p)) for p in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))),
        maximum_run if w.order_exact else None, current_run if w.order_exact else None,
        tuple(interarrival) if w.order_exact else (), first, last, max(values) if values else None,
        min(values) if values else None, progress, movement,
        _rate(movement, w.observed_duration_ns) if movement is not None else None,
        w.eligible_volume, w.signed, epsilon, progress / (w.eligible_volume + epsilon) if progress is not None else None,
        w.eligible_volume == 0, w.history_complete, w.order_exact, quote_id, spread, depth)


@dataclass(frozen=True)
class PrewindowContext:
    version: str
    known_at: int
    bins: tuple[tuple[str, str], ...]

    def __post_init__(self):
        bounded_name(self.version)
        timestamp(self.known_at)
        bounded_rows(self.bins, 16, name="prewindow context bins")
        if type(self.bins) is not tuple or any(type(p) is not tuple or len(p) != 2 for p in self.bins):
            raise ContractError("context schema must be immutable")
        for name, value in self.bins:
            bounded_name(name)
            bounded_name(value)
        if tuple(sorted(set(self.bins))) != self.bins or len({k for k, _ in self.bins}) != len(self.bins):
            raise ContractError("prewindow context must have canonical distinct named bins")


def _context(context, start):
    if type(context) is not PrewindowContext or context.known_at > start:
        raise ContractError("conditional intensity context must be available before the measured window")
    return context.version, context.bins


@dataclass(frozen=True)
class FlowBaselineCell:
    key: tuple
    count_rate: Fraction
    gross_rate: Fraction
    signed_rate: Fraction
    rate_variances: tuple
    rows: int
    exposure_ns: int


@dataclass(frozen=True)
class ConditionalFlowBaseline:
    version: str
    instrument: str
    aggregation_unit: str
    train_end: int
    available_at: int
    minimum_cell_rows: int
    cells: tuple[FlowBaselineCell, ...]
    pooled: FlowBaselineCell
    capture_ids: tuple
    recipe_id: str


def _flow_cell(key, captures):
    exposure = sum(c.window.observed_duration_ns for c in captures)
    totals = tuple(sum(getattr(c.window, name) for c in captures) for name in ("print_count", "eligible_volume", "signed"))
    rates = tuple(Fraction(v * NS, exposure) for v in totals)
    variances = tuple(sum((Fraction(getattr(c.window, name) * NS, c.window.observed_duration_ns) - mean) ** 2
                          * c.window.observed_duration_ns for c in captures) / exposure
                      for name, mean in zip(("print_count", "eligible_volume", "signed"), rates))
    return FlowBaselineCell(key, *rates, variances, len(captures), exposure)


def fit_conditional_flow(rows, *, view, train_end, available_at, version="conditional-flow-v1",
                         minimum_cell_rows=2, max_training_rows=1024):
    """Unpublished descriptive rate fit; public application requires actual F11."""
    bounded_rows(rows, max_training_rows, name="conditional-flow training rows")
    positive_limit(minimum_cell_rows)
    bounded_name(version)
    timestamp(train_end)
    timestamp(available_at)
    if not rows or available_at < train_end:
        raise ContractError("conditional flow fit needs observed historical rows")
    groups, captures, keys = {}, [], []
    first = rows[0][0].window
    for row in rows:
        if type(row) is not tuple or len(row) != 2:
            raise ContractError("flow training row needs an actual capture and prewindow context")
        capture, context = row
        validate_trade_window(capture, view)
        w = capture.window
        key = _context(context, w.start)
        if ((w.instrument, w.aggregation_unit) != (first.instrument, first.aggregation_unit)
                or w.end > train_end or w.published_at > train_end
                or not w.history_complete or not w.observed_duration_ns):
            raise ContractError("flow training requires complete available compatible source windows")
        groups.setdefault(key, []).append(capture)
        captures.append(capture)
        keys.append(key)
    if len({c.id for c in captures}) != len(captures):
        raise ContractError("duplicate source capture in flow baseline")
    recipe = (version, tuple(c.id for c in captures), tuple(keys), train_end, available_at, minimum_cell_rows)
    return ConditionalFlowBaseline(version, first.instrument, first.aggregation_unit, train_end, available_at,
        minimum_cell_rows, tuple(_flow_cell(k, cs) for k, cs in sorted(groups.items())),
        _flow_cell((), captures), tuple(c.id for c in captures), digest(recipe))


def apply_conditional_flow(capture, *, view, context, baseline, fit_binding):
    validate_trade_window(capture, view)
    if type(baseline) is not ConditionalFlowBaseline:
        raise ContractError("typed conditional baseline required")
    w = capture.window
    key = _context(context, w.start)
    if baseline.available_at > w.start:
        raise DependencyUnavailable("flow baseline was not available before the measurement window")
    if (baseline.instrument, baseline.aggregation_unit) != (w.instrument, w.aggregation_unit):
        raise ContractError("flow baseline source domain differs")
    from trading_research.measurements.measurement_fits import validate_measurement_fit
    validate_measurement_fit(fit_binding, capture=capture, view=view, family="conditional_flow", state=baseline, context=context)
    cell = next((c for c in baseline.cells if c.key == key and c.rows >= baseline.minimum_cell_rows), baseline.pooled)
    exposure = Fraction(w.observed_duration_ns, NS)
    means = tuple(rate * exposure for rate in (cell.count_rate, cell.gross_rate, cell.signed_rate)) if exposure else (None,) * 3
    raw = (w.print_count, w.eligible_volume, w.signed)
    residuals = tuple(a - b if b is not None else None for a, b in zip(raw, means))
    standardized = tuple(float(r) / (math.sqrt(float(v)) * float(exposure)) if r is not None and v > 0 and exposure else None
                         for r, v in zip(residuals, cell.rate_variances))
    return {"capture_id": capture.id, "baseline_id": digest(baseline), "raw": raw, "expected": means,
            "residuals": residuals, "standardized_residuals": standardized, "support_rows": cell.rows,
            "pooled_fallback": cell is baseline.pooled, "coverage": w.support_status}


@dataclass(frozen=True)
class CountLikelihood:
    mean_per_second: Fraction
    variance_per_second: Fraction
    negative_binomial_shape: Fraction | None

    def log_probability(self, count, *, exposure_ns, kind="poisson"):
        if type(count) is not int or count < 0 or type(exposure_ns) is not int or exposure_ns < 0:
            raise ContractError("count likelihood needs nonnegative exact observations and exposure")
        if kind not in ("poisson", "negative_binomial"):
            raise ContractError("unknown normalized count likelihood")
        mean = float(self.mean_per_second * Fraction(exposure_ns, NS))
        if mean == 0:
            return 0.0 if count == 0 else -math.inf
        if kind == "poisson" or self.negative_binomial_shape is None:
            return count * math.log(mean) - mean - math.lgamma(count + 1)
        shape = float(self.negative_binomial_shape * Fraction(exposure_ns, NS))
        probability = shape / (shape + mean)
        return (math.lgamma(count + shape) - math.lgamma(shape) - math.lgamma(count + 1)
                + shape * math.log(probability) + count * math.log1p(-probability))


def fit_count_likelihood(counts, *, exposure_ns=NS, max_training_rows=1024):
    """Pure equal-exposure moment comparator, without any fitted-publication claim."""
    bounded_rows(counts, max_training_rows, name="count likelihood rows")
    positive_limit(exposure_ns)
    if not counts or any(type(n) is not int or n < 0 for n in counts):
        raise ContractError("observed nonnegative counts required")
    mean = Fraction(sum(counts), len(counts))
    variance = sum((n - mean) ** 2 for n in counts) / len(counts)
    seconds = Fraction(exposure_ns, NS)
    shape = mean * mean / (variance - mean) / seconds if variance > mean and mean > 0 else None
    return CountLikelihood(mean / seconds, variance / seconds, shape)


@dataclass(frozen=True)
class EffortProgressSurface:
    version: str
    effort_cuts: tuple
    volatility_cuts: tuple
    shrinkage: Fraction
    pooled: Fraction
    cells: tuple
    available_at: int
    recipe_id: str


def fit_effort_progress_surface(rows, *, effort_cuts, volatility_cuts=(), shrinkage=0,
                                available_at, version="effort-progress-v1", max_training_rows=1024):
    """Unpublished numerical kernel; retained rows bind observations at F11 admission."""
    bounded_rows(rows, max_training_rows, name="effort/progress rows")
    for cuts in (effort_cuts, volatility_cuts):
        bounded_rows(cuts, 31, name="surface cuts")
        if tuple(sorted(set(cuts))) != tuple(cuts) or any(exact_number(v) < 0 for v in cuts):
            raise ContractError("surface axes require frozen nonnegative increasing cuts")
    timestamp(available_at)
    bounded_name(version)
    shrinkage = exact_number(shrinkage)
    if not rows or shrinkage < 0:
        raise ContractError("surface fit needs bounded rows and nonnegative pooled shrinkage")
    groups, progress_values, normalized_rows = {}, [], []
    for row in rows:
        if type(row) is not tuple or len(row) != 3:
            raise ContractError("surface row must be effort, prewindow volatility and observed progress")
        effort, volatility, progress = map(exact_number, row)
        normalized_rows.append((effort,volatility,progress))
        if effort < 0 or volatility < 0:
            raise ContractError("effort/volatility are nonnegative dimensional inputs")
        key = (sum(effort >= c for c in effort_cuts), sum(volatility >= c for c in volatility_cuts))
        groups.setdefault(key, []).append(progress)
        progress_values.append(progress)
    pooled = sum(progress_values) / len(progress_values)
    cells = tuple((key, (sum(values) + shrinkage * pooled) / (len(values) + shrinkage), len(values))
                  for key, values in sorted(groups.items()))
    return EffortProgressSurface(version, tuple(effort_cuts), tuple(volatility_cuts), shrinkage, pooled,
        cells, available_at, digest((version, tuple(normalized_rows), effort_cuts, volatility_cuts, shrinkage, available_at)))


def apply_effort_progress_surface(capture, *, view, surface, prewindow_volatility,
                                  context_known_at, fit_binding, epsilon=1):
    validate_trade_window(capture, view)
    timestamp(context_known_at)
    if type(surface) is not EffortProgressSurface or context_known_at > capture.window.start:
        raise ContractError("surface needs typed retained state and prewindow volatility")
    if surface.available_at > capture.window.start:
        raise DependencyUnavailable("effort-progress surface is future trained")
    volatility = exact_number(prewindow_volatility)
    if volatility < 0:
        raise ContractError("prewindow volatility must be nonnegative")
    from trading_research.measurements.measurement_fits import validate_measurement_fit
    validate_measurement_fit(fit_binding, capture=capture, view=view, family="effort_surface", state=surface,
                             context=(context_known_at, prewindow_volatility), epsilon=epsilon)
    raw = measure_tape_intensity(capture, view=view, epsilon=epsilon)
    key = (sum(raw.gross_effort >= c for c in surface.effort_cuts), sum(volatility >= c for c in surface.volatility_cuts))
    cell = next((c for c in surface.cells if c[0] == key), None)
    expected, support = (cell[1], cell[2]) if cell is not None else (surface.pooled, 0)
    return {"capture_id": capture.id, "surface_id": digest(surface), "raw": raw,
            "expected_progress": expected, "residual": None if raw.progress_ticks is None else raw.progress_ticks - expected,
            "support_rows": support, "pooled_fallback": cell is None}


@dataclass(frozen=True)
class BurstEpisode:
    id: str
    born_at: int
    last_observed_at: int
    completed_at: int | None
    capture_ids: tuple
    maximum_observed_rate: Fraction


class BurstTracker:
    def __init__(self, *, threshold_count_per_sec, threshold_known_at, version, max_windows=4096):
        self.threshold = exact_number(threshold_count_per_sec)
        if self.threshold < 0:
            raise ContractError("burst threshold must be nonnegative")
        timestamp(threshold_known_at)
        self.threshold_known_at = threshold_known_at
        self.version = bounded_name(version)
        self.max_windows = positive_limit(max_windows)
        self._captures, self._episodes = (), ()

    @property
    def episodes(self):
        return self._episodes

    def observe(self, capture, *, view):
        validate_trade_window(capture, view)
        w = capture.window
        if self.threshold_known_at > w.start:
            raise ContractError("burst threshold was unavailable at window start")
        if self._captures and capture.id == self._captures[-1].id:
            return self._episodes
        if len(self._captures) >= self.max_windows:
            raise ContractError("burst observation capacity exhausted")
        if self._captures:
            old = self._captures[-1].window
            if ((old.instrument, old.definition_version, old.aggregation_unit) !=
                    (w.instrument, w.definition_version, w.aggregation_unit)
                    or old.end != w.start or old.published_at >= w.published_at):
                raise ContractError("burst observations must be chronological contiguous compatible windows")
        if not w.history_complete:
            raise DependencyUnavailable("missing burst exposure cannot become an observed noncrossing")
        rate = _rate(w.print_count, w.observed_duration_ns)
        episodes = self._episodes
        active = episodes[-1] if episodes and episodes[-1].completed_at is None else None
        if rate is not None and rate > self.threshold:
            if active is None:
                episodes += (BurstEpisode(digest((self.version, capture.id)), w.published_at, w.published_at,
                                          None, (capture.id,), rate),)
            else:
                episodes = (*episodes[:-1], replace(active, last_observed_at=w.published_at,
                    capture_ids=(*active.capture_ids, capture.id), maximum_observed_rate=max(active.maximum_observed_rate, rate)))
        elif active is not None and rate is not None:
            episodes = (*episodes[:-1], replace(active, last_observed_at=w.published_at, completed_at=w.published_at,
                                                capture_ids=(*active.capture_ids, capture.id)))
        self._captures, self._episodes = (*self._captures, capture), episodes
        return episodes

    def checkpoint(self):
        return canonical_json({"schema": "measurement-bursts-v1", "threshold": self.threshold,
            "threshold_known_at": self.threshold_known_at, "version": self.version, "max_windows": self.max_windows,
            "capture_ids": tuple(c.id for c in self._captures), "episodes": self._episodes})

    @classmethod
    def restore(cls, payload, *, captures, view, max_bytes=8388608):
        import json
        positive_limit(max_bytes)
        if type(payload) is not bytes or len(payload) > max_bytes:
            raise ContractError("bounded burst checkpoint bytes required")
        data = json.loads(payload)
        bounded_rows(captures, data["max_windows"], name="burst restore captures")
        result = cls(threshold_count_per_sec=Fraction(*data["threshold"]["$fraction"]),
            threshold_known_at=data["threshold_known_at"], version=data["version"], max_windows=data["max_windows"])
        if tuple(c.id for c in captures) != tuple(data["capture_ids"]):
            raise IntegrityError("burst restore omitted or substituted its source observations")
        for c in captures:
            result.observe(c, view=view)
        if result.checkpoint() != payload:
            raise IntegrityError("burst restore changed registered threshold or historical state")
        return result


@dataclass(frozen=True)
class EffortMarkout:
    effort_capture_id: str
    target_signature: str
    path_label_version: str
    maturity_at: int
    published_at: int
    side: int
    signed_terminal_ticks: int | None
    status: str


def matured_effort_markout(capture, *, view, target, points, coverage, side,
                           published_at, cut, max_points=4096):
    """Separate future label; never a contemporaneous intensity feature."""
    from trading_research.foundations.contracts import Target
    from trading_research.foundations.units import Ticks, Unit
    from trading_research.research.labels import ObservationWindow, PathPoint, reference_path_label
    validate_trade_window(capture, view)
    bounded_rows(points, max_points, name="effort markout observations")
    timestamp(published_at)
    timestamp(cut)
    if (type(target) is not Target or type(coverage) is not ObservationWindow
            or type(points) is not tuple or any(type(p) is not PathPoint for p in points)
            or type(side) is not int or side not in (-1, 1)
            or target.asset != capture.window.instrument or target.unit != Unit.TICKS
            or target.decision_at != capture.window.cut):
        raise ContractError("markout needs original effort cut, raw instrument and typed future path")
    raw = measure_tape_intensity(capture, view=view, epsilon=1)
    if raw.last_ticks is None or raw.last_ticks.denominator != 1:
        raise DependencyUnavailable("effort markout origin is not an observed traded tick")
    label = reference_path_label(target, initial=Ticks(int(raw.last_ticks)), points=points, coverage=coverage,
                                 up_ticks=1, down_ticks=1)
    if published_at < max(label.maturity_at, capture.window.published_at):
        raise ContractError("markout publication precedes actual source/label availability")
    if cut < published_at:
        return None
    return EffortMarkout(capture.id, target.signature, label.version, label.maturity_at, published_at, side,
                         None if label.terminal_ticks is None else side * label.terminal_ticks, label.status)
