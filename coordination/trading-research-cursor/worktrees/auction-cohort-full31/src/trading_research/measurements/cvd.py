"""Reported-side flow, whole-print cohorts and ordered cumulative excursions."""

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import groupby
import math

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import (
    CapturedTradeWindow, bounded_name, bounded_rows, positive_limit, validate_trade_window,
)
from trading_research.operations.artifacts import digest


def exact_number(value):
    if type(value) not in (int, Fraction):
        raise ContractError("flow arithmetic requires an exact integer or rational")
    return Fraction(value)


@dataclass(frozen=True)
class CVDMeasurement:
    capture_id: str
    anchor_id: str
    anchor_start: int
    opening: Fraction
    close: Fraction
    buy: int
    sell: int
    unknown: int
    prints: int
    complete_history: bool
    known_side_fraction: Fraction | None
    observed_signed_bounds: tuple
    true_signed_bounds: tuple | None
    offset_version: str | None
    preceding_capture_ids: tuple
    age_ns: int
    _recipe: object = field(default=None, init=False, repr=False, compare=False)

    @property
    def signed(self):
        return self.buy - self.sell

    @property
    def total(self):
        return self.buy + self.sell + self.unknown


def measure_cvd(capture, *, view, anchor_id, opening=0, preceding=(), offset_version=None):
    validate_trade_window(capture, view)
    bounded_name(anchor_id)
    opening = exact_number(opening)
    w = capture.window
    bounded_rows(preceding, w.max_inputs, name="preceding anchor captures")
    if offset_version is not None:
        bounded_name(offset_version)
    if opening and offset_version is None:
        raise ContractError("nonzero opening needs an explicit mathematical offset or actual preceding captures")
    if preceding and (opening or offset_version is not None):
        raise ContractError("observed preceding flow and mathematical offsets are distinct definitions")
    history, unknown, anchor_start = w.history_complete, w.unknown_volume, w.start
    last = None
    for previous in preceding:
        validate_trade_window(previous, view)
        p = previous.window
        if ((p.instrument, p.aggregation_unit, p.definition_version) !=
                (w.instrument, w.aggregation_unit, w.definition_version)
                or p.end > w.start or p.published_at > w.start or p.cut > w.start
                or last is not None and p.start != last):
            raise ContractError("cumulative opening requires contiguous compatible available anchor history")
        if last is None:
            anchor_start = p.start
        opening += p.signed
        unknown += p.unknown_volume
        history = history and p.history_complete
        last = p.end
    if last is not None and last != w.start:
        raise ContractError("gap between preceding anchor history and current measurement")
    close = opening + w.signed
    bounds = (close - unknown, close + unknown)
    result = CVDMeasurement(capture.id, anchor_id, anchor_start, opening, close, w.buy_volume, w.sell_volume,
        w.unknown_volume, w.print_count, history,
        Fraction(w.buy_volume + w.sell_volume, w.eligible_volume) if w.eligible_volume else None,
        w.observed_signed_bounds, bounds if history else None, offset_version,
        tuple(p.id for p in preceding), min(w.cut, w.end) - anchor_start)
    object.__setattr__(result, "_recipe", (capture, anchor_id, tuple(preceding), offset_version,
                                          opening if not preceding else Fraction(0)))
    return result


def _validate_cvd(value, view):
    if type(value) is not CVDMeasurement or type(value._recipe) is not tuple:
        raise ContractError("actual CVD measurement recipe required")
    capture, anchor_id, preceding, offset, opening = value._recipe
    actual = measure_cvd(capture, view=view, anchor_id=anchor_id, preceding=preceding,
                         offset_version=offset, opening=opening)
    if value != actual:
        raise IntegrityError("CVD measurement changed from its authenticated source")
    return capture.window


def cvd_interval_increment(left, right, *, view):
    a, b = _validate_cvd(left, view), _validate_cvd(right, view)
    if ((left.anchor_id, a.instrument, a.definition_version, a.aggregation_unit, left.offset_version) !=
            (right.anchor_id, b.instrument, b.definition_version, b.aggregation_unit, right.offset_version)
            or a.end != b.start or right.opening != left.close):
        raise ContractError("reset jumps and unrelated cumulative anchors are not interval flow")
    return right.close - left.close


@dataclass(frozen=True)
class CohortChannel:
    id: str
    lower_inclusive: int
    upper_exclusive: int | None
    role: str = "included"

    def __post_init__(self):
        bounded_name(self.id)
        bounded_name(self.role)
        positive_limit(self.lower_inclusive)
        if self.upper_exclusive is not None:
            positive_limit(self.upper_exclusive)
            if self.upper_exclusive <= self.lower_inclusive:
                raise ContractError("cohort interval is empty or reversed")


@dataclass(frozen=True)
class CohortDefinition:
    version: str
    aggregation_unit: str
    channels: tuple[CohortChannel, ...]
    knots: tuple[int, ...] = ()
    partition: bool = True
    origin: str = "fixed"
    available_at: int | None = None
    fit_recipe_id: str | None = None

    def __post_init__(self):
        bounded_name(self.version)
        bounded_name(self.aggregation_unit)
        bounded_rows(self.channels, 32, name="cohort channels")
        bounded_rows(self.knots, 32, name="size basis knots")
        if type(self.channels) is not tuple or type(self.knots) is not tuple or type(self.partition) is not bool:
            raise ContractError("cohort definition must be immutable and explicit")
        if any(type(c) is not CohortChannel for c in self.channels) or len({c.id for c in self.channels}) != len(self.channels):
            raise ContractError("cohort channels require distinct typed identities")
        if bool(self.channels) == bool(self.knots):
            raise ContractError("choose hard channels or a continuous size basis")
        for knot in self.knots:
            positive_limit(knot)
        if self.knots and (tuple(sorted(set(self.knots))) != self.knots or not self.partition):
            raise ContractError("continuous size knots must increase and conserve print weight")
        if self.channels and self.partition:
            if self.channels[0].lower_inclusive != 1 or self.channels[-1].upper_exclusive is not None:
                raise ContractError("hard partitions must retain all below/above mass")
            if any(a.upper_exclusive != b.lower_inclusive for a, b in zip(self.channels, self.channels[1:])):
                raise ContractError("hard partition intervals must be contiguous and disjoint")
        if self.origin == "fixed":
            if self.available_at is not None or self.fit_recipe_id is not None:
                raise ContractError("fixed source cohort cannot claim fitted provenance")
        elif self.origin == "fitted":
            timestamp(self.available_at)
            bounded_name(self.fit_recipe_id)
        else:
            raise ContractError("unknown cohort origin")

    @property
    def id(self):
        return digest(self)

    def weights(self, size):
        positive_limit(size)
        if self.channels:
            return tuple(Fraction(int(size >= c.lower_inclusive and
                         (c.upper_exclusive is None or size < c.upper_exclusive))) for c in self.channels)
        values = [Fraction(0)] * len(self.knots)
        if size <= self.knots[0]:
            values[0] = Fraction(1)
        elif size >= self.knots[-1]:
            values[-1] = Fraction(1)
        else:
            for i, (a, b) in enumerate(zip(self.knots, self.knots[1:])):
                if a <= size < b:
                    values[i], values[i + 1] = Fraction(b - size, b - a), Fraction(size - a, b - a)
                    break
        return tuple(values)


def fixed_source_cohort(name, *, aggregation_unit="provider-reported-trade-record"):
    cuts = {"ny_ge100": (100, None), "london_ge75": (75, None), "inclusive30_through60": (30, 61)}
    if name not in cuts:
        raise ContractError("unknown fixed source interpretation")
    lower, upper = cuts[name]
    channels = [CohortChannel("excluded_below", 1, lower, "excluded_below"),
                CohortChannel("included", lower, upper)]
    if upper is not None:
        channels.append(CohortChannel("excluded_above", upper, None, "excluded_above"))
    return CohortDefinition(name, aggregation_unit, tuple(channels))


@dataclass(frozen=True)
class CohortPath:
    channel_id: str
    open: Fraction
    close: Fraction
    high_bounds: tuple
    low_bounds: tuple
    high_at: int | None
    low_at: int | None
    high_origin: str
    low_origin: str
    buy: Fraction
    sell: Fraction
    unknown: Fraction
    weighted_prints: Fraction
    contributing_prints: int
    order_exact: bool
    history_complete: bool

    @property
    def volume(self):
        return self.buy + self.sell + self.unknown

    @property
    def signed(self):
        return self.buy - self.sell

    @property
    def observed_signed_bounds(self):
        return self.signed - self.unknown, self.signed + self.unknown

    @property
    def true_signed_bounds(self):
        return self.observed_signed_bounds if self.history_complete else None

    @property
    def relative(self):
        return (Fraction(0), tuple(x - self.open for x in self.high_bounds),
                tuple(x - self.open for x in self.low_bounds), self.close - self.open)

    @property
    def actual_side_extrema_bounds(self):
        if not self.history_complete:
            return None
        # Conservative full-side bounds; reported-side path stays separately identified.
        return ((max(self.open, self.high_bounds[0] - self.unknown), self.high_bounds[1] + self.unknown),
                (self.low_bounds[0] - self.unknown, min(self.open, self.low_bounds[1] + self.unknown)))


def _cohort_path(trades, weights, opening, channel_id, complete):
    value = high_lo = high_hi = low_lo = low_hi = exact_number(opening)
    high_at = low_at = None
    buy = sell = unknown = weighted_prints = Fraction(0)
    contributing, exact = 0, True
    for at, group in groupby(zip(trades, weights), key=lambda tw: tw[0].event_at):
        batch = [(t, w) for t, w in group if w]
        for t, w in batch:
            buy += t.size * w if t.side == 1 else 0
            sell += t.size * w if t.side == -1 else 0
            unknown += t.size * w if t.side is None else 0
            weighted_prints += w
            contributing += 1
        ordered = len(batch) <= 1 or (all(t.order is not None for t, _ in batch)
                                      and len({t.order for t, _ in batch}) == len(batch))
        if ordered:
            for t, w in sorted(batch, key=lambda tw: tw[0].order or 0):
                value += t.signed * w
                if value > high_hi:
                    high_at = at
                if value < low_lo:
                    low_at = at
                high_lo, high_hi = max(high_lo, value), max(high_hi, value)
                low_lo, low_hi = min(low_lo, value), min(low_hi, value)
        else:
            exact = False
            final = value + sum(t.signed * w for t, w in batch)
            high_lo, high_hi = max(high_lo, value, final), max(high_hi, value + sum(max(0, t.signed * w) for t, w in batch))
            low_lo, low_hi = min(low_lo, value + sum(min(0, t.signed * w) for t, w in batch)), min(low_hi, value, final)
            value = final
    return CohortPath(channel_id, exact_number(opening), value, (high_lo, high_hi), (low_lo, low_hi),
        high_at if exact else None, low_at if exact else None,
        "ambiguous" if not exact else "opening_baseline" if high_at is None else "print",
        "ambiguous" if not exact else "opening_baseline" if low_at is None else "print",
        buy, sell, unknown, weighted_prints, contributing, exact, complete)


@dataclass(frozen=True)
class CohortMeasurement:
    capture_id: str
    definition: CohortDefinition
    paths: tuple[CohortPath, ...]
    partition: bool
    mathematical_opening_version: str | None


def measure_cohort_cvd(capture, *, view, definition, openings=None, opening_version=None, fit_binding=None):
    validate_trade_window(capture, view)
    if type(definition) is not CohortDefinition:
        raise ContractError("typed frozen cohort definition required")
    CohortDefinition(**{f: getattr(definition, f) for f in definition.__dataclass_fields__})
    if definition.aggregation_unit != capture.window.aggregation_unit:
        raise ContractError("cohort aggregation differs from actual source prints")
    if definition.origin == "fitted":
        if definition.available_at > capture.window.start:
            raise DependencyUnavailable("cohort fit was unavailable at window start")
        from trading_research.measurements.measurement_fits import validate_measurement_fit
        validate_measurement_fit(fit_binding, capture=capture, view=view, family="cohort", state=definition)
    n = len(definition.channels) or len(definition.knots)
    if openings is None:
        openings = (0,) * n
    bounded_rows(openings, 32, name="cohort openings")
    if len(openings) != n:
        raise ContractError("one opening per cohort channel required")
    openings = tuple(exact_number(x) for x in openings)
    if any(openings):
        bounded_name(opening_version)
    elif opening_version is not None:
        bounded_name(opening_version)
    # Only compact channel weights are allocated; no separate cohort tape is built.
    weights = tuple(definition.weights(t.size) for t in capture.trades)
    paths = tuple(_cohort_path(capture.trades, (w[i] for w in weights), openings[i],
                 definition.channels[i].id if definition.channels else f"knot:{definition.knots[i]}",
                 capture.window.history_complete) for i in range(n))
    if definition.partition and sum(p.volume for p in paths) != capture.window.eligible_volume:
        raise IntegrityError("cohort partition lost or duplicated whole-print mass")
    return CohortMeasurement(capture.id, definition, paths, definition.partition, opening_version)


def fit_cohort_definition(training_captures, *, view, train_end, available_at, probabilities,
                          weighting="count", max_training_rows=4096, version="empirical-cohort-v1"):
    """Pure unpublished kernel. F11 admission is required before fitted serving."""
    bounded_rows(training_captures, max_training_rows, name="cohort training captures")
    bounded_rows(probabilities, 31, name="cohort probabilities")
    timestamp(train_end)
    timestamp(available_at)
    if not training_captures or available_at < train_end or weighting not in ("count", "volume"):
        raise ContractError("cohort fit requires historical rows, availability and weighting")
    probabilities = tuple(exact_number(p) for p in probabilities)
    if tuple(sorted(set(probabilities))) != probabilities or any(not 0 < p < 1 for p in probabilities):
        raise ContractError("quantile probabilities must be distinct increasing interior fractions")
    sizes = []
    first = training_captures[0].window
    for c in training_captures:
        validate_trade_window(c, view)
        w = c.window
        if ((w.instrument, w.aggregation_unit) != (first.instrument, first.aggregation_unit)
                or w.end > train_end or w.published_at > train_end or not w.history_complete):
            raise ContractError("cohort training must use compatible, complete, available observations")
        if len(sizes) + len(c.trades) > max_training_rows:
            raise ContractError("cohort fit exceeds bounded whole-print training capacity")
        sizes.extend(t.size for t in c.trades)
    if not sizes or len({c.id for c in training_captures}) != len(training_captures):
        raise ContractError("cohort training is empty or duplicates source windows")
    sizes.sort()
    total = len(sizes) if weighting == "count" else sum(sizes)
    thresholds = []
    for p in probabilities:
        mass = 0
        for size in sizes:
            mass += 1 if weighting == "count" else size
            if mass >= p * total:
                thresholds.append(size + 1)
                break
    # Registered equal-boundary policy: retain requested quantiles in the recipe,
    # merge identical empty intervals deterministically, and report realized mass.
    cuts = (1, *sorted(set(thresholds)), None)
    recipe = {"family": "cohort", "version": version, "window_ids": tuple(c.id for c in training_captures),
              "train_end": train_end, "available_at": available_at, "probabilities": probabilities,
              "weighting": weighting, "requested_thresholds": tuple(thresholds), "tie_policy": "lower_bin_then_merge_empty"}
    definition = CohortDefinition(version, first.aggregation_unit,
        tuple(CohortChannel(f"bin:{i}", a, b) for i, (a, b) in enumerate(zip(cuts, cuts[1:]))),
        origin="fitted", available_at=available_at, fit_recipe_id=digest(recipe))
    return {"definition": definition, "recipe": recipe, "publication_status": "unpublished",
            "realized_count": tuple(sum(c.lower_inclusive <= s and (c.upper_exclusive is None or s < c.upper_exclusive)
                                         for s in sizes) for c in definition.channels),
            "realized_volume": tuple(sum(s for s in sizes if c.lower_inclusive <= s and
                                          (c.upper_exclusive is None or s < c.upper_exclusive)) for c in definition.channels)}


@dataclass(frozen=True)
class FlowDecayDefinition:
    clock: str
    kernel: str
    scale: int
    version: str

    def __post_init__(self):
        if self.clock not in ("elapsed_ns", "executed_contracts", "event_count") or self.kernel not in ("box", "exponential"):
            raise ContractError("unsupported causal flow clock/kernel")
        positive_limit(self.scale)
        bounded_name(self.version)


def measure_decayed_flow(capture, *, view, definition):
    validate_trade_window(capture, view)
    if type(definition) is not FlowDecayDefinition:
        raise ContractError("typed frozen decay definition required")
    if definition.clock != "elapsed_ns" and not capture.window.order_exact:
        raise DependencyUnavailable("activity decay cannot invent order within an ambiguous time tie")
    age, buy, sell, unknown = 0, 0.0, 0.0, 0.0
    for t in reversed(capture.trades):
        current_age = capture.window.cut - t.event_at if definition.clock == "elapsed_ns" else age
        weight = float(current_age < definition.scale) if definition.kernel == "box" else math.exp2(-current_age / definition.scale)
        buy += weight * t.size if t.side == 1 else 0
        sell += weight * t.size if t.side == -1 else 0
        unknown += weight * t.size if t.side is None else 0
        age += t.size if definition.clock == "executed_contracts" else 1
    return {"capture_id": capture.id, "definition": definition, "buy": buy, "sell": sell, "unknown": unknown,
            "signed": buy - sell, "gross": buy + sell + unknown, "support": capture.window.support_status,
            "true_signed_bounds": (buy - sell - unknown, buy - sell + unknown) if capture.window.history_complete else None}
