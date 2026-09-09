"""Anchored exact mass profiles, side geography and explicit proxy variants."""

from dataclasses import dataclass, field, replace
from fractions import Fraction
import math

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.anchored import bind_anchor_members
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class FrozenGrid:
    origin_ticks: int
    width_ticks: int
    lower_row: int
    upper_row: int
    version: str
    known_at: int
    max_rows: int = 4096

    def __post_init__(self):
        if any(type(v) is not int for v in (self.origin_ticks, self.width_ticks, self.lower_row, self.upper_row)):
            raise ContractError("profile grid requires exact raw tick coordinates")
        positive_limit(self.width_ticks)
        positive_limit(self.max_rows)
        if not 0 < self.upper_row-self.lower_row+1 <= self.max_rows:
            raise ContractError("profile requested row span exceeds its frozen capacity")
        bounded_name(self.version)
        timestamp(self.known_at)

    def row(self, ticks):
        if type(ticks) not in (int, Fraction):
            raise ContractError("profile input price must have exact raw tick units")
        return (ticks-self.origin_ticks)//self.width_ticks

    @property
    def id(self):
        return digest(self)


@dataclass(frozen=True)
class ProfileDefinition:
    version: str
    anchor_kind: str = "event"
    value_fraction: Fraction = Fraction(7, 10)
    poc_tie: str = "lower"
    value_tie: str = "upper"
    gap_policy: str = "cross"
    viewport_known_at: int | None = None

    def __post_init__(self):
        bounded_name(self.version)
        if self.anchor_kind not in ("rth", "prior_rth", "overnight", "jumbo_named_range", "day", "week", "month",
                                     "quarter", "year", "rolling", "event", "swing", "composite"):
            raise ContractError("profile anchor kind must be explicitly registered")
        if (type(self.value_fraction) is not Fraction or not 0 < self.value_fraction <= 1
                or self.poc_tie not in ("lower", "upper") or self.value_tie not in ("lower", "upper", "both")
                or self.gap_policy not in ("cross", "stop_empty")):
            raise ContractError("profile requires exact value fraction and explicit POC/expansion conventions")
        if self.viewport_known_at is not None:
            timestamp(self.viewport_known_at)


@dataclass(frozen=True)
class ProfileCell:
    row: int
    buy: Fraction
    sell: Fraction
    unknown: Fraction

    @property
    def mass(self):
        return self.buy+self.sell+self.unknown

    @property
    def delta(self):
        return self.buy-self.sell


@dataclass(frozen=True)
class ProfileSnapshot:
    instrument: str
    aggregation_unit: str
    grid: FrozenGrid
    definition: ProfileDefinition
    representation: str
    cut: int
    published_at: int
    anchor_ids: tuple
    capture_ids: tuple
    members: tuple
    rows: tuple
    low_overflow: tuple
    high_overflow: tuple
    unpriced: tuple
    coverage_intervals: tuple
    history_complete: bool
    source_bar_versions: tuple
    work: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())

    @property
    def total_mass(self):
        return sum(r.mass for r in self.rows)+sum(self.low_overflow)+sum(self.high_overflow)+sum(self.unpriced)

    @property
    def observed_duration_ns(self):
        return sum(b-a for a, b in self.coverage_intervals)


def union_intervals(intervals):
    result = []
    for a, b in sorted(intervals):
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0], max(b, result[-1][1]))
        else:
            result.append((a, b))
    return tuple(result)


def auction_sources(captures, *, views, anchors, graphs, grid=None, max_inputs=4096, max_bytes=8388608):
    for values in (captures, views, anchors, graphs):
        bounded_rows(values, 256, name="auction constituent recipes")
    positive_limit(max_bytes)
    positive_limit(max_inputs)
    if not captures or not len(captures) == len(views) == len(anchors) == len(graphs):
        raise ContractError("each auction constituent needs its actual capture, view, anchor and graph")
    if len({a.anchor.version_id for a in anchors}) != len(anchors):
        raise ContractError("composite repeats an anchor version")
    if grid is not None:
        if type(grid) is not FrozenGrid:
            raise ContractError("typed fixed profile grid required")
        grid.__post_init__()
    by, visits = {}, 0
    first = captures[0].window
    for capture, view, anchor, graph in zip(captures, views, anchors, graphs):
        bind_anchor_members(anchor, graph, capture, view)
        w = capture.window
        if (w.instrument, w.aggregation_unit) != (first.instrument, first.aggregation_unit):
            raise ContractError("auction composite crosses an exact raw instrument or aggregation unit")
        if grid is not None and grid.known_at > w.start:
            raise ContractError("future range information cannot choose a historical profile grid")
        for t in capture.trades:
            visits += 1
            if t.id in by and by[t.id] != t:
                raise IntegrityError("composite repeats a source identity with conflicting revision bytes")
            by[t.id] = t
            if len(by) > max_inputs:
                raise ContractError("auction source union exceeds its finite input capacity")
    members = tuple(sorted(by.values(), key=lambda t: (t.event_at, -1 if t.order is None else t.order, t.id)))
    if len(canonical_json(tuple(t.record() for t in members))) > max_bytes:
        raise ContractError("auction union exceeds its bounded source bytes")
    return members, visits


def build_profile(captures, *, views, anchors, graphs, grid, definition,
                   cut=None, published_at=None, cohort=None, cohort_index=None, fit_binding=None,
                   max_inputs=4096, max_bytes=8388608):
    if type(definition) is not ProfileDefinition:
        raise ContractError("profile requires a typed explicit formation definition")
    definition.__post_init__()
    members, visits = auction_sources(captures, views=views, anchors=anchors, graphs=graphs,
                                      grid=grid, max_inputs=max_inputs, max_bytes=max_bytes)
    cut = max(c.window.cut for c in captures) if cut is None else timestamp(cut)
    published_at = max(cut, *(c.window.published_at for c in captures), *(a.published_at for a in anchors)) if published_at is None else timestamp(published_at)
    if (any(c.window.cut > cut or c.window.published_at > published_at for c in captures)
            or any(a.published_at > published_at for a in anchors) or published_at < cut):
        raise ContractError("profile is unavailable at the requested cut/publication")
    if definition.viewport_known_at is not None and definition.viewport_known_at > min(c.window.start for c in captures):
        raise ContractError("algorithmic viewport was chosen after its measurement began")
    if cohort is not None:
        from trading_research.measurements.cvd import CohortDefinition, measure_cohort_cvd
        if type(cohort) is not CohortDefinition or type(cohort_index) is not int:
            raise ContractError("profile cohort needs an actual declared M02 channel")
        for c, view in zip(captures, views):
            paths = measure_cohort_cvd(c, view=view, definition=cohort, fit_binding=fit_binding).paths
            if not 0 <= cohort_index < len(paths):
                raise ContractError("profile cohort channel index is outside the frozen definition")
    elif cohort_index is not None:
        raise ContractError("profile cohort index lacks its source definition")
    cells = {i: [Fraction(0)]*3 for i in range(grid.lower_row, grid.upper_row+1)}
    lower, upper, unpriced = [Fraction(0)]*3, [Fraction(0)]*3, [Fraction(0)]*3
    for t in members:
        side = 0 if t.side == 1 else 1 if t.side == -1 else 2
        weight = Fraction(1) if cohort is None else cohort.weights(t.size)[cohort_index]
        if t.price is None:
            target = unpriced
        else:
            row = grid.row(t.price.value)
            target = lower if row < grid.lower_row else upper if row > grid.upper_row else cells[row]
        target[side] += t.size*weight
    result = ProfileSnapshot(captures[0].window.instrument, captures[0].window.aggregation_unit, grid, definition,
        "whole_trade" if cohort is None else "whole_trade_cohort:"+cohort.id+":"+str(cohort_index), cut, published_at,
        tuple(a.id for a in anchors), tuple(c.id for c in captures), members,
        tuple(ProfileCell(i, *v) for i, v in cells.items()), tuple(lower), tuple(upper), tuple(unpriced),
        union_intervals(tuple(span for c in captures for span in c.window.coverage.observed_intervals)),
        all(c.window.history_complete for c in captures), tuple(c.window.source_bar_version for c in captures),
        (("source_visits", visits), ("source_records_hashed", visits), ("rows_initialized", len(cells))))
    if len(canonical_json(result.record())) > max_bytes:
        raise ContractError("profile result byte capacity exhausted")
    object.__setattr__(result, "_recipe", ("build", dict(captures=tuple(captures), views=tuple(views), anchors=tuple(anchors),
        graphs=tuple(graphs), grid=grid, definition=definition, cut=cut, published_at=published_at, cohort=cohort,
        cohort_index=cohort_index, fit_binding=fit_binding, max_inputs=max_inputs, max_bytes=max_bytes)))
    return result


def profile_base(profile):
    return _profile_lineage(profile)[-1]


def _profile_lineage(profile,maximum=32):
    seen = set()
    lineage=[]
    while True:
        if (type(profile) is not ProfileSnapshot or type(profile._recipe) is not tuple
                or len(profile._recipe) != 2 or type(profile._recipe[1]) is not dict):
            raise ContractError("actual profile producer recipe required")
        if id(profile) in seen or len(seen) >= maximum:
            raise ContractError("profile transformation history exceeds its acyclic capacity")
        seen.add(id(profile));lineage.append(profile)
        kind, recipe = profile._recipe
        if kind == 'build':
            return tuple(lineage)
        if kind not in ('transform', 'proxy') or 'profile' not in recipe:
            raise IntegrityError("profile transformation recipe is unavailable")
        profile = recipe['profile']


def validate_profile(profile):
    base = profile_base(profile)
    if len(canonical_json(profile.record())) > base._recipe[1]['max_bytes']:
        raise ContractError("profile result exceeds its original retained byte capacity")
    kind, recipe = profile._recipe
    producer = {"build": build_profile, "transform": transform_profile, "proxy": bar_proxy_profile}.get(kind)
    if producer is None or producer(**recipe) != profile:
        raise IntegrityError("profile differs from its actual retained source/representation")


def _plateaus(values, start):
    groups = []
    for index, value in enumerate(values):
        if groups and groups[-1][2] == value:
            groups[-1] = (groups[-1][0], start+index, value)
        else:
            groups.append((start+index, start+index, value))
    return groups


def _validate_mass_rows(rows, *, grid):
    if type(grid) is not FrozenGrid:
        raise ContractError("exact mass rows require a frozen finite grid")
    grid.__post_init__()
    bounded_rows(rows, grid.max_rows, name="profile mass rows")
    if len(rows) != grid.upper_row - grid.lower_row + 1:
        raise ContractError("mass rows must retain the complete grid, including empty cells")
    normalized = []
    for expected, row in enumerate(rows, grid.lower_row):
        if (type(row) is not ProfileCell or type(row.row) is not int or row.row != expected
                or any(type(v) not in (int, Fraction) or v < 0 for v in (row.buy, row.sell, row.unknown))):
            raise ContractError("profile cells must be ordered nonnegative exact side mass")
        normalized.append(row if all(type(v) is Fraction for v in (row.buy, row.sell, row.unknown))
                          else ProfileCell(row.row, Fraction(row.buy), Fraction(row.sell), Fraction(row.unknown)))
    return tuple(normalized)


def profile_geometry(profile):
    validate_profile(profile)
    return profile_geometry_rows(profile.rows, grid=profile.grid, definition=profile.definition)


def profile_geometry_rows(rows, *, grid, definition):
    """Pure exact mass geometry; source eligibility remains the caller's gate.

    The retained capture API above validates its complete source recipe first.
    The research event stream can reuse these same equations on its separately
    admitted cells without fabricating a legacy capture or copying a kernel.
    """
    rows = _validate_mass_rows(rows, grid=grid)
    if type(definition) is not ProfileDefinition:
        raise ContractError("profile geometry needs its explicit value/POC definition")
    definition.__post_init__()
    values = [r.mass for r in rows]
    start, end = grid.lower_row, grid.upper_row
    mass, maximum = sum(values), max(values, default=Fraction(0))
    modes = tuple(start+i for i, v in enumerate(values) if v == maximum) if maximum else ()
    scalar = (min(modes) if definition.poc_tie == "lower" else max(modes)) if modes else None
    plateaus = tuple((a, b) for a, b, h in _plateaus(values, start) if h == maximum) if maximum else ()
    selected, achieved = [], Fraction(0)
    target = mass*definition.value_fraction
    if scalar is not None:
        low = high = scalar
        selected, achieved = [scalar], values[scalar-start]
        while achieved < target and (low > start or high < end):
            left = values[low-start-1] if low > start else None
            right = values[high-start+1] if high < end else None
            if definition.gap_policy == "stop_empty" and (left or 0) == (right or 0) == 0:
                break
            choices = ["right"] if left is None else ["left"] if right is None else (
                ["left"] if left > right else ["right"] if right > left else
                ["left", "right"] if definition.value_tie == "both" else
                ["left"] if definition.value_tie == "lower" else ["right"])
            for choice in choices:
                if choice == "left":
                    low -= 1
                    selected.append(low)
                    achieved += values[low-start]
                else:
                    high += 1
                    selected.append(high)
                    achieved += values[high-start]
    peaks, valleys = [], []
    for a, b, h in _plateaus(values, start):
        left, right = (0 if a == start else values[a-start-1]), (0 if b == end else values[b-start+1])
        if h > 0 and h > left and h > right:
            basins = []
            for step, edge in ((-1, a), (1, b)):
                minimum, found = h, False
                for i in range(edge-start+step, len(values) if step == 1 else -1, step):
                    minimum = min(minimum, values[i])
                    if values[i] > h:
                        found = True
                        break
                basins.append(minimum if found else 0)
            peaks.append({"rows": (a, b), "height": h, "center": Fraction(a+b, 2), "prominence": h-max(basins)})
        if a > start and b < end and h < left and h < right:
            valleys.append((a, b))
    probability = [v/mass for v in values] if mass else []
    ordered_heights = sorted(set(values), reverse=True)
    return {"poc_set": modes, "scalar_poc": scalar, "maximum_plateaus": plateaus,
        "value_rows": tuple(sorted(selected)), "requested_mass": target, "achieved_mass": achieved,
        "overshoot": max(Fraction(0), achieved-target), "local_peaks": tuple(peaks), "interior_valleys": tuple(valleys),
        "mean_row": sum(Fraction(start+i)*v for i, v in enumerate(values))/mass if mass else None,
        "dominance_margin": maximum-(ordered_heights[1] if len(ordered_heights)>1 else 0),
        "concentration": sum(p*p for p in probability) if mass else None,
        "normalized_entropy": -sum(float(p)*math.log(float(p)) for p in probability if p)/math.log(len(values)) if mass and len(values)>1 else 0 if mass else None,
        "gradient_edges": tuple((start+i, values[i+1]-values[i]) for i in range(len(values)-1))}


def transform_profile(profile, *, kind, scale):
    base=_profile_lineage(profile,31)[-1]
    validate_profile(profile)
    grid, cells, lower, upper, operations = transform_profile_rows(profile.rows,
        grid=profile.grid, low_overflow=profile.low_overflow, high_overflow=profile.high_overflow,
        kind=kind, scale=scale)
    result = replace(profile, grid=grid, rows=cells,
        low_overflow=lower, high_overflow=upper, representation=profile.representation+":"+kind+":"+str(scale),
        work=profile.work+(("transform_operations", operations),))
    object.__setattr__(result, "_recipe", ("transform", dict(profile=profile, kind=kind, scale=scale)))
    if len(canonical_json(result.record()))>base._recipe[1]['max_bytes']:
        raise ContractError('transformed profile exceeds its retained byte capacity')
    return result


def transform_profile_rows(cells, *, grid, low_overflow, high_overflow, kind, scale):
    """Shared exact redistribution; source/capture and byte gates stay outside."""
    cells = _validate_mass_rows(cells, grid=grid)
    for mass in (low_overflow, high_overflow):
        if (type(mass) is not tuple or len(mass) != 3
                or any(type(v) not in (int, Fraction) or v < 0 for v in mass)):
            raise ContractError("profile transformation needs exact side overflow")
    if kind not in ("coarsen", "triangular") or type(scale) is not int or not 1 <= scale <= 32:
        raise ContractError("profile transformation requires a registered bounded integer scale")
    if kind == "coarsen":
        grid = FrozenGrid(grid.origin_ticks, grid.width_ticks*scale, grid.lower_row//scale, grid.upper_row//scale,
                          grid.version+":coarse:"+str(scale), grid.known_at, grid.max_rows)
    rows = {i: [Fraction(0)]*3 for i in range(grid.lower_row, grid.upper_row+1)}
    lower, upper = list(map(Fraction, low_overflow)), list(map(Fraction, high_overflow))
    operations = 0
    for row in cells:
        destinations = ((row.row//scale, Fraction(1)),) if kind == "coarsen" else tuple(
            (row.row+d, Fraction(scale+1-abs(d), (scale+1)**2)) for d in range(-scale, scale+1))
        for index, weight in destinations:
            operations += 1
            target = lower if index < grid.lower_row else upper if index > grid.upper_row else rows[index]
            for j, value in enumerate((row.buy, row.sell, row.unknown)):
                target[j] += value*weight
    return grid, tuple(ProfileCell(i, *v) for i, v in rows.items()), tuple(lower), tuple(upper), operations


def multiscale_profile_topology(profile, *, scales):
    bounded_rows(scales, 32, name="profile topology scales")
    variants = tuple(profile if s == 0 else transform_profile(profile, kind="triangular", scale=s) for s in scales)
    peaks = tuple((p.id, profile_geometry(p)["local_peaks"]) for p in variants)
    relations = []
    for i, (pid, rows) in enumerate(peaks):
        for peak in rows:
            a, b = peak["rows"]
            for qid, others in peaks[i+1:]:
                for other in others:
                    c, d = other["rows"]
                    if max(a, c) <= min(b, d):
                        relations.append((pid, (a, b), qid, (c, d)))
    return {"representations": tuple(p.id for p in variants), "peaks": peaks, "matches": tuple(relations)}


def _probabilities(values):
    mass = sum(values)
    return tuple(v/mass for v in values) if mass else None


def _transport(a, b, width):
    pa, pb = _probabilities(a), _probabilities(b)
    if pa is None or pb is None:
        return None
    cumulative, total = Fraction(0), Fraction(0)
    for x, y in zip(pa, pb):
        cumulative += x-y
        total += abs(cumulative)*width
    return total


def profile_transport(a, b):
    validate_profile(a)
    validate_profile(b)
    if a.grid != b.grid or a.instrument != b.instrument or a.aggregation_unit != b.aggregation_unit:
        raise ContractError("profile transport needs identical raw coordinates and fixed grid")
    if any(sum(v) for p in (a, b) for v in (p.low_overflow, p.high_overflow, p.unpriced)) or not a.history_complete or not b.history_complete:
        return None
    return _transport(tuple(r.mass for r in a.rows), tuple(r.mass for r in b.rows), a.grid.width_ticks)


def profile_change(a, b):
    validate_profile(a)
    validate_profile(b)
    if (a.instrument, a.grid, a.representation) != (b.instrument, b.grid, b.representation):
        raise ContractError("profile change needs compatible representations")
    old, new = tuple(r.mass for r in a.rows), tuple(r.mass for r in b.rows)
    m, n = sum(old), sum(new)
    if not m or not n:
        raise DependencyUnavailable("normalized change requires positive old and new mass")
    changes = tuple(y-x for x, y in zip(old, new))
    normalization = tuple(x*(1/n-1/m) for x in old)
    additions = tuple(z/n for z in changes)
    old_by, new_by = {t.id: t for t in a.members}, {t.id: t for t in b.members}
    return {"row_mass_change": changes, "normalization_component": normalization, "new_mass_component": additions,
        "probability_change": tuple(x+y for x, y in zip(normalization, additions)),
        "added_ids": tuple(sorted(new_by.keys()-old_by.keys())), "removed_ids": tuple(sorted(old_by.keys()-new_by.keys())),
        "corrected_ids": tuple(sorted(i for i in old_by.keys() & new_by.keys() if old_by[i] != new_by[i]))}


def side_geometry(profile, *, pseudo_mass=Fraction(0)):
    validate_profile(profile)
    return side_geometry_rows(profile.rows, grid=profile.grid,
                              history_complete=profile.history_complete, pseudo_mass=pseudo_mass)


def side_geometry_rows(cells, *, grid, history_complete, pseudo_mass=Fraction(0)):
    """Pure side-mass equations, with an explicit source-coverage disposition."""
    cells = _validate_mass_rows(cells, grid=grid)
    if type(history_complete) is not bool:
        raise ContractError("side geometry needs an explicit source-history disposition")
    if type(pseudo_mass) not in (int, Fraction) or pseudo_mass < 0:
        raise ContractError("side shrinkage requires nonnegative exact fixed pseudo-mass")
    buys, sells = tuple(r.buy for r in cells), tuple(r.sell for r in cells)
    pb, ps = _probabilities(buys), _probabilities(sells)
    rows, running = [], Fraction(0)
    for r in cells:
        running += r.delta
        denom = r.mass+2*pseudo_mass
        bounds = (r.delta-r.unknown, r.delta+r.unknown)
        rows.append({"row": r.row, "delta": r.delta, "gross": r.mass, "observed_bounds": bounds,
            "true_bounds": bounds if history_complete else None,
            "certain_sign": (1 if bounds[0]>0 else -1 if bounds[1]<0 else None) if history_complete else None,
            "ratio": r.buy/r.sell if r.sell else None, "zero_denominator": not bool(r.sell),
            "contrast": r.delta/denom if denom else None, "cumulative_signed": running})
    def cdf(prob):
        total, result = Fraction(0), []
        for p in prob or ():
            total += p
            result.append(total)
        return tuple(result) if prob is not None else None
    deltas = tuple(r.delta for r in cells)
    maximum = max(deltas, default=None)
    minimum = min(deltas, default=None)
    absolute_peak = max(map(abs, deltas), default=None)
    return {"rows": tuple(rows), "cdf_buy": cdf(pb), "cdf_sell": cdf(ps),
        "overlap": sum(min(x, y) for x, y in zip(pb, ps)) if pb is not None and ps is not None else None,
        "total_variation": sum(abs(x-y) for x, y in zip(pb, ps))/2 if pb is not None and ps is not None else None,
        "wasserstein_ticks": _transport(buys, sells, grid.width_ticks),
        "maximum_rows": tuple(r.row for r in cells if r.delta == maximum),
        "minimum_rows": tuple(r.row for r in cells if r.delta == minimum),
        "absolute_peak_rows": tuple(r.row for r in cells if abs(r.delta) == absolute_peak),
        "absolute_delta_mass": sum(map(abs, deltas))}


def bar_allocation_rows(bars, *, grid, variant):
    """Pure source bar-allocation formulas, separately bound to admitted inputs.

    Bars contain (open, high, low, close, priced volume, unpriced volume).
    The source flat-bar loss is retained explicitly; the corrected comparison
    restores that mass at the close. No synthetic side is called a trade side.
    """
    variants = ("equal_inclusive_rows", "continuous_overlap", "pin066_source", "pin066_corrected", "close", "hlc3")
    if (type(bars) is not tuple or len(bars) > 1_000_000 or type(grid) is not FrozenGrid or variant not in variants):
        raise ContractError('bounded exact bar allocation inputs and registered representation required')
    grid.__post_init__()
    rows = {r: [Fraction(0)]*3 for r in range(grid.lower_row, grid.upper_row + 1)}
    lower, upper, unpriced, lost = [Fraction(0)]*3, [Fraction(0)]*3, [Fraction(0)]*3, Fraction(0)
    def put(index, value, side=2):
        target = lower if index < grid.lower_row else upper if index > grid.upper_row else rows[index]
        target[side] += value
    def spread(lo, hi, mass, side=2):
        if hi == lo:
            put(grid.row(lo), mass, side)
            return
        first, last = grid.row(lo), grid.row(hi)
        if last-first+1 > grid.max_rows:
            raise ContractError("proxy distribution span exceeds its finite grid-work capacity")
        for index in range(first, last+1):
            a = grid.origin_ticks+index*grid.width_ticks
            overlap = max(Fraction(0), min(hi, a+grid.width_ticks)-max(lo, a))
            if overlap:
                put(index, mass*overlap/(hi-lo), side)
    for bar in bars:
        if (type(bar) is not tuple or len(bar) != 6
                or any(type(v) not in (int, Fraction) for v in bar)
                or not bar[2] <= min(bar[0], bar[3]) <= max(bar[0], bar[3]) <= bar[1]
                or bar[4] < 0 or bar[5] < 0):
            raise ContractError('bar allocation requires exact observed OHLC and nonnegative priced/unpriced mass')
        o, h, l, close, volume, unpriced_volume = map(Fraction, bar)
        unpriced[2] += unpriced_volume
        if variant == "equal_inclusive_rows":
            first, last = grid.row(l), grid.row(h)
            if last-first+1 > grid.max_rows:
                raise ContractError("inclusive proxy span exceeds finite row-work capacity")
            for index in range(first, last+1):
                put(index, volume/(last-first+1))
        elif variant == "continuous_overlap":
            spread(l, h, volume)
        elif variant in ("close", "hlc3"):
            put(grid.row(close if variant == "close" else (h+l+close)/3), volume)
        else:
            body, low_wick, high_wick = abs(close-o), min(o, close)-l, h-max(o, close)
            denominator = body+2*low_wick+2*high_wick
            if not denominator:
                if variant == "pin066_source":
                    lost += volume
                else:
                    put(grid.row(close), volume)
                continue
            if body:
                spread(min(o, close), max(o, close), volume*body/denominator, 0 if close >= o else 1)
            for a, b, wick in ((l, min(o, close), low_wick), (max(o, close), h, high_wick)):
                if wick:
                    for side in (0, 1):
                        spread(a, b, volume*wick/denominator, side)
    total = sum(sum(v) for v in rows.values()) + sum(lower + upper + unpriced) + lost
    if total != sum(bar[4] + bar[5] for bar in bars):
        raise IntegrityError('bar allocation lost mass outside its explicit source defect channel')
    return {'rows': tuple(ProfileCell(i, *v) for i, v in rows.items()),
            'low_overflow': tuple(lower), 'high_overflow': tuple(upper),
            'unpriced': tuple(unpriced), 'source_flat_bar_lost_mass': lost}


def bar_proxy_profile(profile, *, variant):
    """Explicit bar approximations over authenticated F09 source publications."""
    validate_profile(profile)
    if profile._recipe[0] != "build" or any(v is None for v in profile.source_bar_versions):
        raise ContractError("bar proxies require actual retained common/F09 captures")
    recipe = profile._recipe[1]
    bars = []
    for c in recipe["captures"]:
        engine, pub = c._bar_recipe
        bar, _ = engine.window_publication(pub)
        s = bar.summary
        if s.open_ticks is None or s.close_ticks is None or s.high_ticks is None or s.low_ticks is None:
            raise DependencyUnavailable("proxy candle geometry is unsupported")
        bars.append((s.open_ticks, s.high_ticks, s.low_ticks, s.close_ticks,
                     sum(t.size for t in c.trades if t.price is not None),
                     sum(t.size for t in c.trades if t.price is None)))
    allocation = bar_allocation_rows(tuple(bars), grid=profile.grid, variant=variant)
    result = replace(profile, representation="bar_proxy:"+variant, rows=allocation['rows'],
        low_overflow=allocation['low_overflow'], high_overflow=allocation['high_overflow'], unpriced=allocation['unpriced'],
        work=profile.work+(("source_flat_bar_lost_mass", allocation['source_flat_bar_lost_mass']),))
    object.__setattr__(result, "_recipe", ("proxy", dict(profile=profile, variant=variant)))
    if len(canonical_json(result.record()))>profile._recipe[1]['max_bytes']:
        raise ContractError('bar proxy exceeds its retained byte capacity')
    return result


def source_pin066_poc(profile):
    validate_profile(profile)
    if profile.representation != "bar_proxy:pin066_source":
        raise ContractError("source bottom-bin defect is only a named source proxy diagnostic")
    poc = profile_geometry(profile)["scalar_poc"]
    return None if poc == profile.grid.lower_row else poc


@dataclass(frozen=True)
class DevelopingProfileFit:
    grid_id: str
    instrument: str
    row_ids: tuple
    cells: tuple
    pooled_rates: tuple
    training_profiles: tuple
    train_end: int
    available_at: int
    minimum_context_rows: int
    recipe_id: str


def fit_developing_profile(rows, *, train_end, available_at, minimum_context_rows=1,
                           max_training_rows=1024):
    """Unpublished rate arithmetic; actual F11 admission is required for inference."""
    bounded_rows(rows, max_training_rows, name="developing-profile training rows")
    positive_limit(minimum_context_rows)
    timestamp(train_end)
    timestamp(available_at)
    if not rows or available_at < train_end:
        raise ContractError("developing profile fit needs preceding actual rows and causal completion")
    first = rows[0][0]
    sums, exposure, count = {}, {}, {}
    origins=set()
    for profile, context in rows:
        validate_profile(profile)
        if (profile.grid != first.grid or profile.instrument != first.instrument
                or profile.definition!=first.definition or profile.aggregation_unit!=first.aggregation_unit
                or profile.representation != first.representation or profile.published_at > train_end
                or not profile.history_complete or profile.observed_duration_ns <= 0):
            raise ContractError("developing profile fit requires complete compatible preceding exposure")
        if type(context) is not tuple or len(context) != 2:
            raise ContractError("profile context requires actual prewindow known time and fixed key")
        known, key = context
        timestamp(known)
        bounded_name(key)
        if profile._recipe[0] != "build" or known > min(c.window.start for c in profile._recipe[1]["captures"]):
            raise ContractError("profile fit context was selected after formation began")
        row_origins={(c.window.instrument,c.window.aggregation_unit,c.window.start,c.window.end)
                     for c in profile._recipe[1]['captures']}
        if origins&row_origins:
            raise ContractError('developing-profile fit repeats an underlying exposure origin')
        origins.update(row_origins)
        if key not in sums:
            if len(sums) >= 256:
                raise ContractError("profile fitted context capacity exhausted")
            sums[key], exposure[key], count[key] = [Fraction(0)]*len(first.rows), 0, 0
        sums[key] = [x+r.mass for x, r in zip(sums[key], profile.rows)]
        exposure[key] += profile.observed_duration_ns
        count[key] += 1
    if len({p.id for p, _ in rows}) != len(rows):
        raise ContractError("developing-profile fit repeats a source profile")
    total_exposure = sum(exposure.values())
    pooled = tuple(sum(values[i] for values in sums.values())/total_exposure for i in range(len(first.rows)))
    cells = tuple((key, tuple(v/exposure[key] for v in sums[key]), count[key]) for key in sorted(sums))
    recipe = digest({"profiles": tuple((p.id, c) for p, c in rows), "train_end": train_end,
        "available_at": available_at, "minimum_context_rows": minimum_context_rows})
    return DevelopingProfileFit(first.grid.id, first.instrument, tuple(r.row for r in first.rows), cells,
        pooled, tuple(p.id for p, _ in rows), train_end, available_at, minimum_context_rows, recipe)


def apply_developing_profile(profile, *, admission, training_profiles, query_session, context):
    from trading_research.measurements.measurement_fits import _reopen, _json_exact, read_measurement_query, validate_measurement_fit_payload
    validate_profile(profile)
    admission = _reopen(admission)
    bounded_rows(training_profiles, admission.max_training_rows, name="actual retained fitted profile recipes")
    if profile._recipe[0] != "build":
        raise ContractError("developing fitted profile needs the registered original representation")
    recipe = _json_exact(admission.configuration)["measurement_fit"]
    params = recipe.get("parameters")
    if recipe.get("family") != "developing_profile" or type(params) is not dict or set(params) != {
            "train_end", "available_at", "minimum_context_rows"}:
        raise ContractError("developing-profile retained fit configuration differs")
    by = {}
    for row in training_profiles:
        if type(row) is not tuple or len(row) != 3 or row[0] in by:
            raise ContractError("fitted profile recipes must pair unique temporal row and actual profile/context")
        by[row[0]] = row[1:]
    if set(by) != set(admission.fold.training_ids):
        raise IntegrityError("fitted profile recipes differ from the complete actual training population")
    manifests = {m.bindings[0].request.row_id: m for m in admission.training_manifests}
    for row_id, (p, c) in by.items():
        validate_profile(p)
        reads = {r.binding.column: r.row for r in manifests[row_id].reads}
        if ("profile" not in reads or "profile_context" not in reads
                or reads["profile"].value_json != canonical_json(p.record())
                or reads["profile_context"].value_json != canonical_json(c)):
            raise IntegrityError("profile fit input differs from its actual retained original reads")
    state = fit_developing_profile(tuple(by[i] for i in admission.fold.training_ids),
        max_training_rows=admission.max_training_rows, **params)
    if state.recipe_id != admission.recipe_id:
        raise IntegrityError("developing-profile recipe identity differs after source reconstruction")
    validate_measurement_fit_payload(admission, canonical_json(state))
    window_start = min(c.window.start for c in profile._recipe[1]["captures"])
    values = read_measurement_query(admission, query_session, window_start=window_start,
                                    columns=("profile", "profile_context"))
    if canonical_json(values["profile"]) != canonical_json(profile.record()) or canonical_json(values["profile_context"]) != canonical_json(context):
        raise IntegrityError("developing profile query differs from actual source reads")
    if type(context) is not tuple or len(context) != 2 or context[0] > window_start:
        raise ContractError("developing profile inference context was unavailable before formation")
    first_training=next(iter(by.values()))[0]
    if ((profile.grid.id, profile.instrument) != (state.grid_id, state.instrument)
            or profile.definition!=first_training.definition or profile.aggregation_unit!=first_training.aggregation_unit
            or profile.representation!=first_training.representation):
        raise ContractError("fitted profile query changes the raw spatial representation")
    cell = next((c for c in state.cells if c[0] == context[1]), None)
    rates = cell[1] if cell is not None and cell[2] >= state.minimum_context_rows else state.pooled_rates
    expected = tuple(rate*profile.observed_duration_ns for rate in rates)
    observed = tuple(r.mass for r in profile.rows)
    shape, actual_shape = _probabilities(expected), _probabilities(observed)
    return {"expected_mass": expected, "expected_shape": shape,
        "raw_residual": tuple(x-y for x, y in zip(observed, expected)),
        "shape_residual": tuple(x-y for x, y in zip(actual_shape, shape)) if actual_shape is not None and shape is not None else None,
        "support_rows": cell[2] if cell is not None and cell[2] >= state.minimum_context_rows else len(training_profiles),
        "pooled_fallback": cell is None or cell[2] < state.minimum_context_rows, "fit_recipe_id": state.recipe_id}
