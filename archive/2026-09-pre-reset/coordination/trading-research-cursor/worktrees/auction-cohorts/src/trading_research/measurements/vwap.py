"""Exact anchored moments and separately named robust/source band variants."""

from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.measurements.profiles import auction_sources
from trading_research.operations.artifacts import canonical_json, digest


def exact_sqrt(value):
    if value is None:
        return None
    if value < 0:
        raise IntegrityError("negative exact moment variance")
    with localcontext() as context:
        context.prec = 50
        return (Decimal(value.numerator)/Decimal(value.denominator)).sqrt()


def weighted_quantile(weighted, probability):
    if type(probability) is not Fraction or not 0 <= probability <= 1:
        raise ContractError("weighted quantile requires an exact probability in [0,1]")
    if not weighted:
        return None
    rows = sorted(weighted)
    total = sum(q for _, q in rows)
    if not total:
        return None
    cumulative = Fraction(0)
    for price, quantity in rows:
        cumulative += quantity
        if cumulative >= probability*total:
            return price
    return rows[-1][0]


@dataclass(frozen=True)
class VWAPSnapshot:
    instrument: str
    aggregation_unit: str
    definition: str
    anchor_keys: tuple
    anchor_versions: tuple
    capture_ids: tuple
    members: tuple
    cut: int
    published_at: int
    mass: int
    unpriced_mass: int
    sum_pv: int
    sum_p2v: int
    mean: Fraction | None
    variance: Fraction | None
    history_complete: bool
    work: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())


def measure_vwap(captures, *, views, anchors, graphs, definition, cut=None, published_at=None,
                  max_inputs=4096, max_bytes=8388608):
    bounded_name(definition)
    members, visits = auction_sources(captures, views=views, anchors=anchors, graphs=graphs,
                                      max_inputs=max_inputs, max_bytes=max_bytes)
    cut = max(c.window.cut for c in captures) if cut is None else timestamp(cut)
    published_at = max(cut, *(c.window.published_at for c in captures), *(a.published_at for a in anchors)) if published_at is None else timestamp(published_at)
    if (published_at < cut or any(c.window.cut > cut or c.window.published_at > published_at for c in captures)
            or any(a.published_at > published_at for a in anchors)):
        raise ContractError("VWAP source unavailable at requested publication")
    mass = sum(t.size for t in members if t.price is not None)
    unpriced = sum(t.size for t in members if t.price is None)
    pv = sum(t.price.value*t.size for t in members if t.price is not None)
    p2v = sum(t.price.value*t.price.value*t.size for t in members if t.price is not None)
    mean = Fraction(pv, mass) if mass else None
    variance = Fraction(mass*p2v-pv*pv, mass*mass) if mass else None
    result = VWAPSnapshot(captures[0].window.instrument, captures[0].window.aggregation_unit, definition,
        tuple(a.anchor.anchor_id for a in anchors), tuple(a.anchor.version_id for a in anchors), tuple(c.id for c in captures),
        members, cut, published_at, mass, unpriced, pv, p2v, mean, variance,
        all(c.window.history_complete for c in captures), (("source_visits", visits), ("source_records_hashed", visits)))
    if len(canonical_json(result.record())) > max_bytes:
        raise ContractError("VWAP result byte capacity exhausted")
    object.__setattr__(result, "_recipe", dict(captures=tuple(captures), views=tuple(views), anchors=tuple(anchors),
        graphs=tuple(graphs), definition=definition, cut=cut, published_at=published_at, max_inputs=max_inputs, max_bytes=max_bytes))
    return result


def validate_vwap(result):
    if type(result) is not VWAPSnapshot or type(result._recipe) is not dict or measure_vwap(**result._recipe) != result:
        raise IntegrityError("VWAP differs from its actual anchored whole-trade recipe")


def vwap_bands(result, *, multipliers=(Fraction(1), Fraction(2), Fraction(5, 2), Fraction(3)),
               probabilities=(Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)), percentage=None,
               winsor_limits=(Fraction(1, 10), Fraction(9, 10))):
    validate_vwap(result)
    bounded_rows(multipliers, 32, name="VWAP band multipliers")
    bounded_rows(probabilities, 32, name="VWAP quantile probabilities")
    if any(type(m) not in (int, Fraction) or m < 0 for m in multipliers):
        raise ContractError("VWAP band multiplier must be exact nonnegative")
    if result.mean is None:
        return {"sd": None, "sigma_bands": None, "quantiles": None, "median": None, "mad": None, "winsorized_mean": None, "percentage_bands": None}
    weighted = tuple((Fraction(t.price.value), Fraction(t.size)) for t in result.members if t.price is not None)
    median = weighted_quantile(weighted, Fraction(1, 2))
    mad = weighted_quantile(tuple((abs(p-median), q) for p, q in weighted), Fraction(1, 2))
    if type(winsor_limits) is not tuple or len(winsor_limits) != 2 or not 0 <= winsor_limits[0] <= winsor_limits[1] <= 1:
        raise ContractError("winsorization requires ordered declared quantile limits")
    lo, hi = (weighted_quantile(weighted, p) for p in winsor_limits)
    winsorized = sum(min(hi, max(lo, p))*q for p, q in weighted)/result.mass
    sd = exact_sqrt(result.variance)
    with localcontext() as context:
        context.prec = 50
        mean = Decimal(result.mean.numerator)/Decimal(result.mean.denominator)
        sigma = tuple((m, mean-Decimal(Fraction(m).numerator)/Decimal(Fraction(m).denominator)*sd,
                        mean+Decimal(Fraction(m).numerator)/Decimal(Fraction(m).denominator)*sd) for m in multipliers)
    percent = None
    if percentage is not None:
        if type(percentage) is not Fraction or percentage < 0:
            raise ContractError("percentage band requires an exact nonnegative fraction")
        distance = abs(result.mean)*percentage
        percent = result.mean-distance, result.mean+distance
    return {"sd": sd, "sigma_bands": sigma, "quantiles": tuple((p, weighted_quantile(weighted, p)) for p in probabilities),
            "median": median, "mad": mad, "winsorized_mean": winsorized, "percentage_bands": percent}


def vwap_difference(a, b, *, kind="cross_anchor"):
    validate_vwap(a)
    validate_vwap(b)
    if (a.instrument, a.aggregation_unit) != (b.instrument, b.aggregation_unit):
        raise ContractError("VWAP relation requires one exact raw coordinate system")
    if kind not in ("cross_anchor", "same_anchor_change", "same_anchor_slope"):
        raise ContractError("VWAP change must distinguish anchor relation from a same-anchor slope")
    if kind != "cross_anchor" and (a.anchor_keys != b.anchor_keys or a.definition != b.definition or b.cut <= a.cut):
        raise ContractError("VWAP reset jump cannot become a same-anchor change or slope")
    if not a.mass or not b.mass:
        raise DependencyUnavailable("VWAP difference needs observed positive mass at both anchors")
    left, right = {t.id: t for t in a.members if t.price is not None}, {t.id: t for t in b.members if t.price is not None}
    contributions = []
    for identity in sorted(left.keys() | right.keys()):
        x, y = left.get(identity), right.get(identity)
        if x is not None and y is not None and x != y:
            raise ContractError("changed print revisions require an explicit correction decomposition")
        value = (Fraction(y.price.value*y.size, b.mass) if y else 0)-(Fraction(x.price.value*x.size, a.mass) if x else 0)
        contributions.append((identity, value, "shared" if x and y else "B_only" if y else "A_only"))
    difference = b.mean-a.mean
    return {"difference": difference, "slope": difference/(b.cut-a.cut) if kind == "same_anchor_slope" else None,
            "contributions": tuple(contributions), "reconciliation_error": difference-sum(v for _, v, _ in contributions)}


@dataclass(frozen=True)
class MovingAnchorResidual:
    source_capture_id: str
    anchor_ids: tuple
    known_at: int
    source_price: Fraction
    historical_anchor: Fraction
    deviation: Fraction
    weight: int
    _recipe: object = field(default=None, init=False, compare=False, repr=False)


def moving_anchor_residual(source_capture, *, view, session_vwap, high_anchor_vwap):
    validate_trade_window(source_capture, view)
    for result in (session_vwap, high_anchor_vwap):
        validate_vwap(result)
        if result.instrument != source_capture.window.instrument or result.mean is None:
            raise ContractError("moving-anchor residual requires supported same-instrument anchors")
        if result.published_at > source_capture.window.published_at:
            raise ContractError("moving-anchor residual cannot use an anchor published later")
    if not source_capture.window.order_exact or source_capture.window.unpriced_volume or not source_capture.trades:
        raise DependencyUnavailable("moving residual needs its actual ordered source close")
    price = Fraction(source_capture.trades[-1].price.value)
    anchor = (session_vwap.mean+high_anchor_vwap.mean)/2
    result = MovingAnchorResidual(source_capture.id, (session_vwap.id, high_anchor_vwap.id), source_capture.window.published_at,
        price, anchor, price-anchor, source_capture.window.eligible_volume)
    object.__setattr__(result, "_recipe", dict(source_capture=source_capture, view=view,
        session_vwap=session_vwap, high_anchor_vwap=high_anchor_vwap))
    return result


def residual_band_statistics(observations, *, current_anchor):
    bounded_rows(observations, 4096, name="moving-anchor historical residuals")
    validate_vwap(current_anchor)
    if not observations or current_anchor.mean is None:
        raise DependencyUnavailable("residual bands require actual residual observations and current anchor")
    for obs in observations:
        if (type(obs) is not MovingAnchorResidual or type(obs._recipe) is not dict
                or moving_anchor_residual(**obs._recipe) != obs or obs.known_at > current_anchor.published_at):
            raise IntegrityError("historical deviation changed or was unavailable at current anchor")
    weighted = tuple((o.deviation, Fraction(o.weight)) for o in observations)
    total = sum(w for _, w in weighted)
    if not total:
        raise DependencyUnavailable("zero residual observation mass")
    mean = sum(d*w for d, w in weighted)/total
    rms2 = sum(d*d*w for d, w in weighted)/total
    def side_square(sign):
        part = [(d, w) for d, w in weighted if sign*d>0]
        return sum(d*d*w for d, w in part)/sum(w for _, w in part) if part else None
    values = sorted(d for d, _ in weighted)
    def linear_quantile(p):
        if len(values)<2:
            return None
        at = p*(len(values)-1)
        i = at.numerator//at.denominator
        return values[i] if i==len(values)-1 else values[i]+(at-i)*(values[i+1]-values[i])
    absolute = sorted(abs(d) for d in values)
    mid = len(absolute)//2
    zero_median = absolute[mid] if len(absolute)%2 else (absolute[mid-1]+absolute[mid])/2
    median = values[mid] if len(values)%2 else (values[mid-1]+values[mid])/2
    centered_absolute = sorted(abs(d-median) for d in values)
    centered_mad = centered_absolute[mid] if len(values)%2 else (centered_absolute[mid-1]+centered_absolute[mid])/2
    return {"weighted_mean": mean, "rms_squared": rms2, "rms": exact_sqrt(rms2),
        "positive_rms_squared": side_square(1), "negative_rms_squared": side_square(-1),
        "negative_rms": exact_sqrt(side_square(-1)), "centered_variance": rms2-mean*mean,
        "zero_centered_median_abs": zero_median, "centered_mad": centered_mad,
        "source_quantiles": tuple(linear_quantile(p) for p in (Fraction(1, 10), Fraction(1, 4), Fraction(3, 4), Fraction(9, 10))),
        "weighted_offset_band": current_anchor.mean+mean}


def source_volume_ema(captures, *, views, length=5):
    bounded_rows(captures, 4096, name="source EMA bar sequence")
    bounded_rows(views, 4096, name="source EMA views")
    positive_limit(length)
    if len(captures) != len(views):
        raise ContractError("EMA needs one actual view per captured source bar")
    alpha, result, value = Fraction(2, length+1), [], None
    for c, view in zip(captures, views):
        validate_trade_window(c, view)
        if c.window.source_bar_version is None:
            raise ContractError("source EMA5 proxy requires actual shared-bar observations")
        volume = Fraction(c.window.eligible_volume)
        value = volume if value is None else alpha*volume+(1-alpha)*value
        result.append(value)
    return {"alpha": alpha, "values": tuple(result), "proxy_volume_total": sum(result),
            "actual_volume_total": sum(c.window.eligible_volume for c in captures), "representation": "source_bar_volume_ema"}


def source_new_high_anchors(captures, *, views, anchors, graphs, interval_graph, interval_name):
    from trading_research.foundations.intervals import IntervalGraph
    if type(interval_graph) is not IntervalGraph or interval_name not in interval_graph.intervals:
        raise ContractError("source reanchor needs an actual disclosed F03 clock")
    interval = interval_graph.intervals[interval_name]
    auction_sources(captures, views=views, anchors=anchors, graphs=graphs)
    high, total, pv, origin, result = None, Fraction(0), Fraction(0), None, []
    for capture, anchor in zip(captures, anchors):
        if capture.window.source_bar_version is None:
            raise ContractError("source high-anchor variant requires actual F09 bars")
        engine, pub = capture._bar_recipe
        bar, _ = engine.window_publication(pub)
        s = bar.summary
        if s.high_ticks is None or s.close_ticks is None:
            raise DependencyUnavailable("source high-anchor bar geometry unavailable")
        within = interval.contains(bar.interval[0], cut=capture.window.cut)
        if high is None or within and s.high_ticks > high:
            if anchor.anchor.start != bar.interval[0]:
                raise ContractError("new-high source anchor does not bind its actual causal origin")
            high, total, pv, origin = s.high_ticks, Fraction(0), Fraction(0), bar.interval[0]
        total += s.volume
        pv += s.close_ticks*s.volume
        result.append((origin, pv/total if total else None, anchor.id, capture.window.published_at))
    return tuple(result)


class VWAPBook:
    def __init__(self, *, max_versions=1024, max_bytes=8388608):
        self.max_versions, self.max_bytes = positive_limit(max_versions), positive_limit(max_bytes)
        self.versions, self.recipes = (), ()
        self._sealed = self._state_bytes()

    def advance(self, captures, **kwargs):
        self.checkpoint()
        if len(self.versions) >= self.max_versions:
            raise ContractError("VWAP retained versions require explicit archival")
        result = measure_vwap(captures, **kwargs)
        if self.versions and result.published_at <= self.versions[-1].published_at:
            raise ContractError("VWAP update publication must advance")
        staged = canonical_json({"max_versions": self.max_versions, "max_bytes": self.max_bytes,
                                 "versions": tuple(v.record() for v in (*self.versions, result))})
        if len(staged) > self.max_bytes:
            raise ContractError("VWAP retained byte capacity exhausted")
        self.versions, self.recipes = (*self.versions, result), (*self.recipes, result._recipe)
        self._sealed = staged
        return result

    def _state_bytes(self):
        return canonical_json({"max_versions": self.max_versions, "max_bytes": self.max_bytes,
                               "versions": tuple(v.record() for v in self.versions)})

    def checkpoint(self):
        if self._state_bytes() != self._sealed or len(self.versions) != len(self.recipes):
            raise IntegrityError("VWAP book changed outside its actual source replay")
        if len(self._sealed) > self.max_bytes:
            raise ContractError("VWAP checkpoint byte capacity exhausted")
        return self._sealed

    @classmethod
    def restore(cls, payload, *, recipes, max_versions=1024, max_bytes=8388608):
        bounded_rows(recipes, max_versions, name="VWAP restoration recipes")
        if type(payload) is not bytes or len(payload)>positive_limit(max_bytes):
            raise ContractError("VWAP restoration byte capacity exhausted")
        result = cls(max_versions=max_versions, max_bytes=max_bytes)
        for recipe in recipes:
            result.advance(**recipe)
        if result.checkpoint() != payload:
            raise IntegrityError("VWAP checkpoint differs from actual bounded source replay")
        return result
