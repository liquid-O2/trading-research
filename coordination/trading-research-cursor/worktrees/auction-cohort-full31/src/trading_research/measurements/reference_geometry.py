"""Early calendar opens, typed reference geometry and separately matured gaps."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction
from itertools import groupby, permutations
import math

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.context.range_adapter import _require_clock
from trading_research.foundations.calendar import Calendar
from trading_research.foundations.object_graph import Instrument, PublicationClock
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_rows, capture_trade_window, positive_limit, validate_trade_window
from trading_research.measurements.reference_prices import (
    ReferencePrice, session_references, official_settlement_at, range_formula, require_primitive,
)
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.object_labels import ExactPoint
from trading_research.research.labels import ObservationWindow


@dataclass(frozen=True)
class ReferenceLimits:
    max_references: int = 256
    max_edges: int = 4096
    max_period_days: int = 366
    max_inputs: int = 4096
    max_sources: int = 4096
    max_points: int = 4096
    max_batch: int = 8
    max_states: int = 4096
    max_transition_work: int = 65536
    max_identity_bytes: int = 256
    max_bytes: int = 8388608

    def __post_init__(self):
        for key in self.__dataclass_fields__:
            positive_limit(getattr(self, key))


DEFAULT_LIMITS = ReferenceLimits()


def _name(value, limits=DEFAULT_LIMITS):
    if type(value) is not str or not value or len(value.encode("utf-8")) > limits.max_identity_bytes:
        raise ContractError("reference identity exceeds its exact UTF-8 byte bound")
    return value


@dataclass(frozen=True)
class OpenObservation:
    selection_version: str
    capture_id: str
    reference: ReferencePrice
    first_observed: ReferencePrice | None
    possible_first_prices: tuple
    incomplete_open: bool
    enclosing_session_complete: bool
    status: str
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())


def observe_open(selection, view, *, coverage, cut, published_at, horizon_end,
                 semantic="session_first_eligible_trade", aggregation_unit="provider-reported-trade-record",
                 limits=DEFAULT_LIMITS):
    if type(limits) is not ReferenceLimits:
        raise ContractError("typed reference limits required")
    limits.__post_init__()
    _require_clock(selection)
    for at in (cut, published_at, horizon_end):
        timestamp(at)
    if semantic not in ("session_first_eligible_trade", "bar_open", "current_open"):
        raise ContractError("scheduled first print must retain its explicit reference type")
    if (selection.selected_at > cut or published_at < cut or horizon_end <= published_at
            or not selection.instrument.valid(published_at)):
        raise ContractError("opening reference selection, publication or expiry is invalid")
    if any(end is not None and horizon_end > end for end in (selection.instrument.valid_until, selection.instrument.expiry_at)):
        raise ContractError("opening reference horizon exceeds the exact raw lifetime")
    if coverage.instrument not in (selection.instrument.raw_symbol, selection.instrument.key):
        raise ContractError("opening source coverage differs from the selected raw instrument")
    capture = capture_trade_window(view, instrument=coverage.instrument, start=selection.window.start,
        end=selection.window.end, cut=cut, published_at=published_at, definition_version=selection.window.definition_version,
        aggregation_unit=aggregation_unit, coverage=coverage, max_inputs=limits.max_inputs, max_bytes=limits.max_bytes)
    first = tuple(t for t in capture.trades if t.event_at == capture.trades[0].event_at) if capture.trades else ()
    possibilities = tuple(sorted({Fraction(t.price.value) for t in first if t.price is not None}))
    ordered = len(first) <= 1 or all(t.order is not None for t in first) and len({t.order for t in first}) == len(first)
    price = (None if not first or first[0].price is None else Fraction(first[0].price.value)) if ordered else (
        possibilities[0] if len(possibilities)==1 and all(t.price is not None for t in first) else None)
    event_at = first[0].event_at if first else None
    prefix = bool(first) and (event_at == selection.window.start or
        any(a == selection.window.start and b >= event_at for a, b in coverage.observed_intervals))
    prefix &= all(t.history_complete for t in first)
    certified = price is not None and prefix
    status = "observed" if certified else "ambiguous" if first and price is None else "partial" if first else "empty"
    source = (capture.id, selection.version_id)
    ref = ReferencePrice("ref:"+digest((selection.clock_id, semantic)), semantic, selection.instrument,
        price if certified else None, event_at, published_at, horizon_end, source,
        "observed" if certified else status, "certified first eligible print" if certified else "opening prefix is not fully identified")
    diagnostic = None if price is None else ReferencePrice("ref:"+digest((selection.clock_id, "first_observed")),
        "first_observed_trade", selection.instrument, price, event_at, published_at, horizon_end,
        source, "observed", "first observed print without an enclosing-session completeness claim")
    result = OpenObservation(selection.version_id, capture.id, ref, diagnostic, possibilities,
        not certified, capture.window.history_complete and cut >= selection.window.end, status)
    object.__setattr__(result, "_recipe", dict(selection=selection, view=view, coverage=coverage, cut=cut,
        published_at=published_at, horizon_end=horizon_end, semantic=semantic, aggregation_unit=aggregation_unit, limits=limits))
    return result


def validate_open(value):
    if type(value) is not OpenObservation or type(value._recipe) is not dict or observe_open(**value._recipe) != value:
        raise IntegrityError("open differs from its actual historical calendar and source capture")


@dataclass(frozen=True)
class ReferenceBinding:
    reference: ReferencePrice
    producer: str
    producer_version: str
    _recipe: object = field(default=None, init=False, compare=False, repr=False)


def bind_open(observation, *, diagnostic=False):
    validate_open(observation)
    if type(diagnostic) is not bool:
        raise ContractError("opening diagnostic choice must be explicit")
    reference = observation.first_observed if diagnostic else observation.reference
    if reference is None:
        raise DependencyUnavailable("opening observation has no observed price diagnostic")
    result = ReferenceBinding(reference, "open", observation.id)
    object.__setattr__(result, "_recipe", (observation, diagnostic))
    return result


def bind_session_reference(primitive, *, field_name, clocks, horizon_end, semantic="session"):
    result = session_references(primitive, clocks=clocks, horizon_end=horizon_end, semantic=semantic)
    reference = result.field(field_name)
    binding = ReferenceBinding(reference, "session", primitive.version_id)
    object.__setattr__(binding, "_recipe", dict(primitive=primitive, field_name=field_name, clocks=clocks,
        horizon_end=horizon_end, semantic=semantic))
    return binding


def bind_official_reference(messages, *, cut, clocks, horizon_end, max_versions=256):
    reference = official_settlement_at(messages, cut=cut, clocks=clocks, horizon_end=horizon_end, max_versions=max_versions)
    if reference is None:
        raise DependencyUnavailable("no actual official settlement report at this cut")
    binding = ReferenceBinding(reference, "official", digest(messages))
    object.__setattr__(binding, "_recipe", dict(messages=messages, cut=cut, clocks=clocks,
                                              horizon_end=horizon_end, max_versions=max_versions))
    return binding


def validate_reference(binding):
    if type(binding) is not ReferenceBinding:
        raise ContractError("reference geometry requires its actual source-producing recipe")
    if binding.producer == "open" and type(binding._recipe) is tuple:
        actual = bind_open(binding._recipe[0], diagnostic=binding._recipe[1])
    elif binding.producer == "session" and type(binding._recipe) is dict:
        actual = bind_session_reference(**binding._recipe)
    elif binding.producer == "official" and type(binding._recipe) is dict:
        actual = bind_official_reference(**binding._recipe)
    else:
        raise ContractError("unsupported or detached reference producer")
    if actual != binding:
        raise IntegrityError("reference price differs from its actual retained producer")
    return binding.reference


def period_identity(current_date, period):
    if type(current_date) is not date:
        raise ContractError("period open uses an explicit civil trading date")
    if period == "day":
        return current_date.isoformat(), current_date
    if period == "iso_week":
        year, week, _ = current_date.isocalendar()
        return f"{year}-W{week:02d}", current_date-timedelta(days=current_date.weekday())
    if period == "month":
        return f"{current_date.year}-{current_date.month:02d}", current_date.replace(day=1)
    if period == "quarter":
        quarter = (current_date.month-1)//3+1
        return f"{current_date.year}-Q{quarter}", date(current_date.year, 3*quarter-2, 1)
    if period == "year":
        return str(current_date.year), date(current_date.year, 1, 1)
    raise ContractError("unknown trading-period open definition")


def period_open(*, calendar, instrument_root, current_date, period, observations, cut, limits=DEFAULT_LIMITS):
    if type(calendar) is not Calendar or type(limits) is not ReferenceLimits:
        raise ContractError("period open requires the actual explicit calendar")
    limits.__post_init__()
    bounded_rows(observations, limits.max_period_days, name="period opening observations")
    key, first = period_identity(current_date, period)
    count = (current_date-first).days+1
    if count > limits.max_period_days:
        raise ContractError("period date traversal exceeds its declared calendar capacity")
    _name(instrument_root, limits)
    timestamp(cut)
    by = {}
    for observation in observations:
        if type(observation) is not OpenObservation or type(observation._recipe) is not dict:
            raise ContractError("period members must retain their actual opening recipes")
        day = observation._recipe["selection"].window.trading_date
        if day in by:
            raise ContractError("period observations repeat a civil session date")
        by[day] = observation
    traversed, missing_observation, reads, diagnostic = [], False, 0, None
    for offset in range(count):
        day = first+timedelta(days=offset)
        try:
            session = calendar.resolve(day, instrument_root, cut=cut)
        except DependencyUnavailable:
            return _period_result({"period_key": key, "status": "calendar_unavailable", "selected_date": None,
                    "open": None, "first_observed": diagnostic, "traversed": tuple(traversed), "producer_reads": reads},limits)
        traversed.append((day.isoformat(), session.version))
        if not session.eligible:
            continue
        observation = by.get(day)
        if observation is None:
            missing_observation = True
            continue
        validate_open(observation)
        reads += 1
        selected = observation._recipe["selection"]
        if selected.session != session or observation.reference.known_at > cut:
            raise ContractError("period member differs from its actual same-date historical calendar selection")
        if observation.first_observed is not None:
            diagnostic = observation.first_observed
            return _period_result({"period_key": key, "status": "incomplete_open" if missing_observation or observation.incomplete_open else "observed",
                "selected_date": day.isoformat(), "open": None if missing_observation or observation.incomplete_open else observation.reference,
                "first_observed": diagnostic, "incomplete_open": missing_observation or observation.incomplete_open,
                "traversed": tuple(traversed), "producer_reads": reads},limits)
        if not observation.enclosing_session_complete:
            missing_observation = True
    return _period_result({"period_key": key, "status": "incomplete_open" if missing_observation else "empty", "selected_date": None,
            "open": None, "first_observed": diagnostic, "traversed": tuple(traversed), "producer_reads": reads},limits)


def _period_result(result,limits):
    if len(canonical_json(result))>limits.max_bytes:
        raise ContractError("period reference result exceeds its retained byte capacity")
    return result


@dataclass(frozen=True)
class PriorReferenceScale:
    id: str
    definition_version: str
    instrument: str
    value_ticks: Fraction
    formation_start: int
    formation_end: int
    published_at: int
    source_versions: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)


def prior_reference_scale(capture, *, view=None, definition="mean_absolute_tick_change"):
    if definition == "mean_absolute_tick_change":
        validate_trade_window(capture, view)
        w = capture.window
        if not w.history_complete or not w.order_exact or w.unpriced_volume:
            raise DependencyUnavailable("reference normalization requires actual complete ordered preceding prices")
        prices = [t.price.value for t in capture.trades]
        moves = [abs(b-a) for a, b in zip(prices, prices[1:])]
        value = Fraction(sum(moves), len(moves)) if moves else Fraction(0)
        instrument, start, end, published, sources = w.instrument, w.start, w.end, w.published_at, (capture.id,)
    elif definition == "mean_true_range":
        from trading_research.measurements.structure import SwingBarCapture, validate_swing_bars
        validate_swing_bars(capture)
        if len(capture.bars) < 2 or any(not b.final or not b.coverage_complete or any(
                getattr(b.summary, name) is None for name in ('open_ticks','high_ticks','low_ticks','close_ticks')) for b in capture.bars):
            raise DependencyUnavailable("reference true range requires actual complete bars including preceding close")
        values = [max(b.summary.high_ticks-b.summary.low_ticks, abs(b.summary.high_ticks-a.summary.close_ticks),
                      abs(b.summary.low_ticks-a.summary.close_ticks)) for a, b in zip(capture.bars, capture.bars[1:])]
        value = Fraction(sum(values), len(values))
        instrument = capture.bars[0].definition.domain.instrument
        start, end, published, sources = capture.bars[1].interval[0], capture.bars[-1].interval[1], capture.published_at, tuple(b.version_id for b in capture.bars)
    else:
        raise ContractError("reference scale needs a separately registered actual-source recipe")
    result = PriorReferenceScale(digest((capture.id, definition)), definition, instrument, value, start, end, published, sources)
    object.__setattr__(result, "_recipe", dict(capture=capture, view=view, definition=definition))
    return result


def validate_scale(scale):
    if type(scale) is not PriorReferenceScale or type(scale._recipe) is not dict or prior_reference_scale(**scale._recipe) != scale:
        raise IntegrityError("reference scale differs from its actual preceding source")


def reference_status(reference, cut, maximum_age_ns):
    if type(maximum_age_ns) is not int or maximum_age_ns < 0:
        raise ContractError("reference maximum age must be exact nonnegative nanoseconds")
    if cut >= reference.horizon_end:
        return "expired"
    if not reference.available(cut):
        return "unavailable"
    return "stale" if cut-reference.known_at > maximum_age_ns else "observed"


def normalized_gap(current, prior, *, scale, cut, published_at, maximum_age_ns):
    a, b = validate_reference(current), validate_reference(prior)
    validate_scale(scale)
    timestamp(cut)
    timestamp(published_at)
    if a.instrument != b.instrument or scale.instrument not in (a.instrument.raw_symbol, a.instrument.key):
        raise ContractError("gap normalization crosses raw reference coordinates")
    if a.observed_at is None or scale.formation_end > a.observed_at or scale.published_at > cut or published_at < cut:
        raise ContractError("reference normalization source was not prior formed and available")
    statuses = tuple(reference_status(r, cut, maximum_age_ns) for r in (a, b))
    value = a.value_ticks-b.value_ticks if statuses == ("observed", "observed") else None
    return {"current_version": a.version, "prior_version": b.version, "types": (a.kind, b.kind), "statuses": statuses,
        "gap_ticks": value, "gap_points": None if value is None else value*a.instrument.tick_size_points,
        "direction": None if value is None else (1 if value>0 else -1 if value<0 else 0),
        "normalized_gap": value/scale.value_ticks if value is not None and scale.value_ticks>0 else None,
        "scale_version": scale.id, "observation_ages": tuple(None if r.observed_at is None else cut-r.observed_at for r in (a, b)),
        "publication_ages": tuple(cut-r.known_at for r in (a, b)), "known_at": published_at}


class ReferenceGraph:
    def __init__(self, references, *, edges, cut, published_at, maximum_age_ns, limits=DEFAULT_LIMITS):
        limits.__post_init__()
        bounded_rows(references, limits.max_references, name="reference graph vertices")
        bounded_rows(edges, limits.max_edges, name="reference graph edges")
        timestamp(cut)
        timestamp(published_at)
        if published_at < cut:
            raise ContractError("reference graph publication predates its frozen input cut")
        by = {}
        for binding in references:
            ref = validate_reference(binding)
            if ref.id in by and by[ref.id].reference != ref:
                raise IntegrityError("reference graph identity reused with conflicting revision bytes")
            by[ref.id] = binding
        output = []
        for edge in edges:
            if type(edge) is not tuple or len(edge) != 2 or any(k not in by for k in edge):
                raise ContractError("reference graph edge lacks exact declared vertices")
            a, b = (by[k].reference for k in edge)
            if a.instrument != b.instrument:
                raise ContractError("reference graph edge requires explicit mapping across raw coordinates")
            status = tuple(reference_status(r, cut, maximum_age_ns) for r in (a, b))
            output.append((a.id, b.id, a.value_ticks-b.value_ticks if status == ("observed", "observed") else None, status))
        self.references, self.edges = tuple(by.values()), tuple(output)
        self.cut, self.published_at, self.maximum_age_ns, self.limits = cut, published_at, maximum_age_ns, limits
        self._sealed = self._state_bytes()
        if len(self._sealed) > limits.max_bytes:
            raise ContractError("reference graph retained byte capacity exhausted")

    def consensus(self, ids, *, weights):
        self.checkpoint()
        bounded_rows(ids, self.limits.max_references, name="reference consensus members")
        bounded_rows(weights, self.limits.max_references, name="reference consensus weights")
        if not ids or len(ids) != len(weights) or len(set(ids)) != len(ids):
            raise ContractError("reference consensus requires unique members and matching weights")
        by = {b.reference.id: b for b in self.references}
        if any(k not in by for k in ids):
            raise ContractError("reference consensus references a missing vertex")
        refs = tuple(validate_reference(by[k]) for k in ids)
        if any(type(w) not in (int, Fraction) or w < 0 for w in weights) or not sum(weights):
            raise ContractError("reference consensus weights must be exact nonnegative with positive total")
        if len({(r.kind, r.instrument, r.observed_at) for r in refs}) != 1:
            return {"mean": None, "member_count": len(refs), "status": "unlike_reference_types_or_observations"}
        if any(reference_status(r, self.cut, self.maximum_age_ns) != "observed" for r in refs):
            return {"mean": None, "member_count": len(refs), "status": "unavailable"}
        values = tuple(r.value_ticks for r in refs)
        return {"mean": sum(v*w for v, w in zip(values, weights))/sum(weights), "minimum": min(values),
                "maximum": max(values), "spread": max(values)-min(values), "member_count": len(refs), "members": tuple(ids)}

    def available(self, cut):
        timestamp(cut)
        self.checkpoint()
        return cut >= self.published_at

    def ages(self):
        self.checkpoint()
        return tuple((b.reference.id,None if b.reference.observed_at is None else self.cut-b.reference.observed_at,
                      self.cut-b.reference.known_at,self.published_at) for b in self.references)

    def _state_bytes(self):
        return canonical_json({"references": tuple((b.reference, b.producer, b.producer_version) for b in self.references),
            "edges": self.edges, "cut": self.cut, "published_at": self.published_at,
            "maximum_age_ns": self.maximum_age_ns, "limits": self.limits})

    def checkpoint(self):
        if self._state_bytes() != self._sealed:
            raise IntegrityError("reference graph changed outside its actual source reconstruction")
        for binding in self.references:
            validate_reference(binding)
        return self._sealed

    @classmethod
    def restore(cls, payload, references, *, edges, cut, published_at, maximum_age_ns, limits=DEFAULT_LIMITS):
        if type(payload) is not bytes or len(payload)>limits.max_bytes:
            raise ContractError("reference graph checkpoint exceeds its byte capacity")
        result = cls(references, edges=edges, cut=cut, published_at=published_at, maximum_age_ns=maximum_age_ns, limits=limits)
        if result.checkpoint() != payload:
            raise IntegrityError("reference graph checkpoint differs from actual retained recipes/configuration")
        return result


@dataclass(frozen=True)
class ReferenceCoordinateBinding:
    instrument: Instrument
    definition: object
    coordinate: object
    currency: str
    currency_evidence_id: str


def bind_reference_coordinate(instrument, definition, *, currency, currency_evidence_id):
    from trading_research.foundations.instruments import InstrumentDefinition
    from trading_research.foundations.rolls import RawCoordinate
    if type(instrument) is not Instrument or type(definition) is not InstrumentDefinition or definition.classification != "future":
        raise ContractError("reference raw coordinate requires actual F02 futures terms")
    instrument.__post_init__()
    definition.__post_init__()
    key, clocks = definition.key, definition.clocks
    if ((instrument.provider, instrument.venue, instrument.raw_id, instrument.raw_symbol, instrument.definition_version,
         instrument.tick_size_points, instrument.valid_from, instrument.valid_until, instrument.expiry_at) !=
        (key.provider, key.venue, key.instrument_id, key.raw_symbol, key.definition_version, Fraction(definition.tick_size),
         clocks.valid_from, clocks.valid_until, key.expiry_at)):
        raise ContractError("reference instrument differs from the exact F02 definition/lifetime")
    coordinate = RawCoordinate.from_definition(definition, currency=currency, currency_evidence_id=currency_evidence_id)
    return ReferenceCoordinateBinding(instrument, definition, coordinate, currency, currency_evidence_id)


def bridge_gap(current, prior, *, current_binding, prior_binding, bridge, cut, published_at):
    from trading_research.foundations.rolls import RollBridge
    a, b = validate_reference(current), validate_reference(prior)
    for binding, reference in ((current_binding, a), (prior_binding, b)):
        if type(binding) is not ReferenceCoordinateBinding or bind_reference_coordinate(binding.instrument, binding.definition,
            currency=binding.currency, currency_evidence_id=binding.currency_evidence_id) != binding or binding.instrument != reference.instrument:
            raise IntegrityError("reference bridge coordinate differs from actual raw terms")
    if type(bridge) is not RollBridge:
        raise ContractError("reference translation requires an actual typed F04 raw bridge")
    bridge.__post_init__()
    if (bridge.old.coordinate != prior_binding.coordinate or bridge.new.coordinate != current_binding.coordinate
            or not bridge.available(cut) or not bridge.available(published_at) or published_at < cut
            or not a.available(cut) or not b.available(cut)):
        raise DependencyUnavailable("reference bridge is mismatched, stale, future or unavailable")
    pa, pb = a.value_ticks*a.instrument.tick_size_points, b.value_ticks*b.instrument.tick_size_points
    mapped = bridge.translate(pb, coordinate=prior_binding.coordinate, at=cut)
    raw, market = pa-pb, pa-mapped
    return {"raw_gap_points": raw, "bridge_spread_points": bridge.spread, "mapped_gap_points": market,
        "mapped_gap_destination_ticks": market/a.instrument.tick_size_points,
        "uncertainty_destination_ticks": bridge.uncertainty_points/a.instrument.tick_size_points,
        "reconciliation_error": raw-market-bridge.spread, "bridge_version": bridge.version, "known_at": published_at}


def interpolate_references(forecast_open, reference_open, *, fraction, cut, extrapolation=False, maximum_ratio=Fraction(4)):
    a, b = validate_reference(forecast_open), validate_reference(reference_open)
    if type(fraction) is not Fraction or type(extrapolation) is not bool or type(maximum_ratio) is not Fraction or maximum_ratio <= 0:
        raise ContractError("interpolation requires exact fraction and declared bounded extrapolation policy")
    if (not extrapolation and not 0 <= fraction <= 1) or (extrapolation and abs(fraction) > maximum_ratio):
        raise ContractError("interpolation ratio exceeds its declared definition")
    if a.instrument != b.instrument or not a.available(cut) or not b.available(cut):
        raise ContractError("interpolation endpoints are incompatible or unavailable")
    value = (1-fraction)*a.value_ticks+fraction*b.value_ticks
    def sign(value):
        return 1 if value>0 else -1 if value<0 else 0
    return {"target_ticks": value, "formation_displacement_ticks": a.value_ticks-b.value_ticks,
        "direction_from_forecast": sign(value-a.value_ticks), "direction_from_reference": sign(value-b.value_ticks),
        "endpoints": (a.version, b.version), "fraction": fraction, "extrapolation": extrapolation}


def floor_pivots(primitive, *, clocks, horizon_end):
    require_primitive(primitive, clocks=clocks, horizon_end=horizon_end)
    if not primitive.supports("high", "low", "close"):
        raise DependencyUnavailable("floor pivots require certified completed same-period H/L/C")
    high, low, close = map(Fraction, (primitive.high_ticks, primitive.low_ticks, primitive.close_ticks))
    if high < low:
        raise ContractError("floor-pivot high is below its low")
    p, width = (high+low+close)/3, high-low
    result = {"P": p, "R1": 2*p-low, "S1": 2*p-high, "R2": p+width, "S2": p-width,
              "R3": high+2*(p-low), "S3": low-2*(high-p)}
    for i in (4, 5):
        result["R"+str(i)] = result["R"+str(i-1)]+width
        result["S"+str(i)] = result["S"+str(i-1)]-width
    return {"levels": tuple(result.items()), "primitive_version": primitive.version_id,
            "high": high, "low": low, "degenerate": width==0, "known_at": clocks.known_at}


def pivot_interval_bands(primitive, *, clocks, horizon_end, fractions=(Fraction(1, 2), Fraction(309, 500))):
    pivots = floor_pivots(primitive, clocks=clocks, horizon_end=horizon_end)
    bounded_rows(fractions, 32, name="source pivot-band fractions")
    if not fractions or any(type(p) is not Fraction or not 0 <= p <= 1 for p in fractions):
        raise ContractError("source pivot bands need exact interior fractions")
    values = dict(pivots["levels"])
    ordered = [values["S"+str(i)] for i in range(5, 0, -1)]+[values["P"]]+[values["R"+str(i)] for i in range(1, 6)]
    def band(a, b):
        return tuple(sorted(a+p*(b-a) for p in fractions))
    return {"daily_from_low": band(pivots["low"], pivots["high"]),
            "daily_from_high": band(pivots["high"], pivots["low"]),
            "P_to_R1": band(values["P"], values["R1"]), "P_to_S1": band(values["P"], values["S1"]),
            "adjacent_intervals": tuple((a, b, band(a, b)) for a, b in zip(ordered, ordered[1:])),
            "source_primitive": primitive.version_id}


@dataclass(frozen=True)
class GapTarget:
    current_version: str
    prior_version: str
    instrument: Instrument
    initial: Fraction
    reference: Fraction
    cut: int
    end: int
    observation_process: str
    contact_mode: str
    direction: int
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def version(self):
        return digest(self.record())


def gap_target(current, prior, *, cut, end, observation_process="last_observed_trade_price", contact_mode="future_contact"):
    a, b = validate_reference(current), validate_reference(prior)
    timestamp(cut)
    timestamp(end)
    _name(observation_process)
    if (end <= cut or a.instrument != b.instrument or not a.available(cut) or not b.available(cut)
            or contact_mode not in ("future_contact", "contact_at_cut")):
        raise ContractError("gap target requires available exact compatible references and a fixed future endpoint")
    if contact_mode == "contact_at_cut" and a.value_ticks != b.value_ticks:
        raise ContractError("contact-at-cut gap target requires actual equality at its own origin")
    difference = a.value_ticks-b.value_ticks
    result = GapTarget(a.version, b.version, a.instrument, a.value_ticks, b.value_ticks, cut, end,
        observation_process, contact_mode, 1 if difference>0 else -1 if difference<0 else 0)
    object.__setattr__(result, "_recipe", dict(current=current, prior=prior, cut=cut, end=end,
        observation_process=observation_process, contact_mode=contact_mode))
    return result


def validate_gap_target(target):
    if type(target) is not GapTarget or type(target._recipe) is not dict or gap_target(**target._recipe) != target:
        raise IntegrityError("gap target differs from its frozen actual source reference versions")


def gap_targets(current, prior, *, selection, cut, minutes=(5, 15, 60), include_session_remainder=True,
                 same_session=True, observation_process="last_observed_trade_price", contact_mode="future_contact"):
    _require_clock(selection)
    bounded_rows(minutes, 32, name="gap fixed horizons")
    if any(type(m) is not int or m <= 0 for m in minutes) or type(include_session_remainder) is not bool or type(same_session) is not bool:
        raise ContractError("gap horizons need positive whole minutes and explicit session policy")
    if selection.selected_at > cut or selection.instrument != validate_reference(current).instrument:
        raise ContractError("gap remainder session differs from the actual opening coordinate/cut")
    ends = tuple(timestamp(cut+m*60000000000) for m in minutes)
    if include_session_remainder:
        ends += (selection.session.close_at,)
    if any(end <= cut or same_session and end > selection.session.close_at for end in ends):
        raise ContractError("gap endpoint exceeds its declared actual session or has already elapsed")
    return tuple(gap_target(current, prior, cut=cut, end=end, observation_process=observation_process,
                            contact_mode=contact_mode) for end in ends)


@dataclass(frozen=True)
class GapOutcome:
    target_version: str
    fields: tuple
    retained_evidence_digest: str
    limits: ReferenceLimits
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def __getitem__(self, key):
        return dict(self.fields)[key]

    def record(self):
        return {"target_version": self.target_version, "fields": self.fields,
                "retained_evidence_digest": self.retained_evidence_digest, "limits": self.limits}

    @property
    def version(self):
        return digest(self.record())


def gap_outcome(target, *, points, coverage, query_at, published_at, limits=DEFAULT_LIMITS):
    validate_gap_target(target)
    if type(limits) is not ReferenceLimits:
        raise ContractError("gap outcomes require typed retained finite bounds")
    limits.__post_init__()
    bounded_rows(points, limits.max_points, name="gap future observations")
    timestamp(query_at)
    timestamp(published_at)
    if published_at < query_at or query_at < target.cut:
        raise ContractError("gap outcome publication/query predates its frozen origin")
    if any(type(p) is not ExactPoint or p.known_at < p.at for p in points):
        raise ContractError("gap path requires actual typed exact observations and availability")
    if len({(p.at, p.sequence) for p in points}) != len(points):
        raise ContractError("gap path duplicates a source order identity")
    if coverage is None:
        if points:
            raise ContractError("gap observations require their explicit observation window")
        end, maturity, complete, ordered = target.cut, target.end, False, True
    else:
        if type(coverage) is not ObservationWindow:
            raise ContractError("gap evidence requires the existing V01 observation contract")
        coverage.__post_init__()
        _name(coverage.version, limits)
        if coverage.start != target.cut or coverage.end > target.end:
            raise ContractError("gap evidence extends or changes its frozen target")
        if any(not target.cut < p.at <= coverage.end or any(a <= p.at < b for a, b in coverage.gaps) for p in points):
            raise ContractError("gap point lies outside actual observed support")
        end = coverage.end
        maturity = max(coverage.certified_through, *(p.known_at for p in points)) if points else coverage.certified_through
        complete = end == target.end and not coverage.gaps
        ordered = coverage.source_order_known
    if len(canonical_json((target.record(), points, coverage, limits))) > limits.max_bytes:
        raise ContractError("gap source recipe byte capacity exhausted")
    rows = tuple(sorted(points, key=lambda p: (p.at, p.sequence)))
    visible = tuple(p for p in rows if p.known_at <= query_at and p.at <= query_at)
    visible_contact = next((p.at for p in visible if p.price == target.reference), None)
    base = {"status": "pending" if coverage is None or query_at < maturity else "censored" if not complete else "observed",
        "maturity_at": maturity, "published_at": published_at, "observed_end": min(end,query_at), "fixed_end": target.end,
        "observed_count": len(visible), "partial_contact_at": visible_contact, "touched": None, "contact_at": None,
        "terminal_ticks": None, "closed_through": None, "held_after_contact": None, "gap_crossings": (),
        "gap_held": None, "gap_traversed": None, "compatible_terminal_ticks": (), "compatible_closed_through": (),
        "compatible_held_after_contact": (), "permutations": 0, "transition_work": 0,
        "full_outcome_count": int(complete and query_at >= maturity), "unresolved_count": int(not complete or query_at < maturity)}
    if complete and query_at >= maturity:
        contact = target.cut if target.contact_mode == "contact_at_cut" else None
        states = {(target.initial, contact, True if contact is not None else None, (),
                   True if target.direction else None, False if target.direction else None)}
        permutation_count, work = 0, 0
        for at, group in groupby(rows, key=lambda p: p.at):
            batch = tuple(group)
            if not ordered and len(batch) > limits.max_batch:
                raise ContractError("gap unknown-order batch exceeds capacity")
            orders_count = 1 if ordered else math.factorial(len(batch))
            charge = len(states)*orders_count*len(batch)
            if work+charge > limits.max_transition_work:
                raise ContractError("gap permutation transition work exceeds the declared bound")
            following = set()
            for order in ((batch,) if ordered else permutations(batch)):
                permutation_count += 1
                for previous, first_contact, held, crossings, gap_held, traversed in states:
                    crosses = list(crossings)
                    for p in order:
                        work += 1
                        if (previous-target.reference)*(p.price-target.reference)<0:
                            crosses.append(at)
                        if first_contact is None and p.price == target.reference:
                            first_contact, held = at, True
                        if first_contact is not None and target.direction:
                            held = held and target.direction*(p.price-target.reference) <= 0
                        if target.direction:
                            gap_held = gap_held and target.direction*(p.price-target.reference)>0
                            traversed = traversed or target.direction*(p.price-target.reference)<=0
                        previous = p.price
                    following.add((previous, first_contact, held, tuple(crosses), gap_held, traversed))
                    if len(following) > limits.max_states:
                        raise ContractError("gap compatible outcome states exceed capacity")
            states = following
        terminals = tuple(sorted({s[0] for s in states}))
        closes = tuple(sorted({target.direction*(s[0]-target.reference)<0 for s in states})) if target.direction else ()
        holds = tuple(sorted({s[2] for s in states}, key=lambda x: -1 if x is None else int(x))) if target.direction else ()
        contacts = {s[1] for s in states}
        crossing_sets = tuple(set(s[3]) for s in states)
        certain_crosses = tuple(sorted(set.intersection(*crossing_sets))) if crossing_sets else ()
        common_contact = next(iter(contacts)) if len(contacts)==1 else None
        base.update(status="ambiguous" if len(terminals)>1 or len(closes)>1 or len(holds)>1 else "observed",
            touched=any(s[1] is not None for s in states), contact_at=common_contact,
            terminal_ticks=terminals[0] if len(terminals)==1 else None,
            closed_through=closes[0] if len(closes)==1 else None, held_after_contact=holds[0] if len(holds)==1 else None,
            gap_crossings=certain_crosses, gap_held=all(s[4] for s in states) if target.direction else None,
            gap_traversed=all(s[5] for s in states) if target.direction else None,
            compatible_terminal_ticks=terminals, compatible_closed_through=closes,
            compatible_held_after_contact=holds, permutations=permutation_count, transition_work=work)
    result = GapOutcome(target.version, tuple(base.items()), digest((target.record(), rows, coverage)), limits)
    if len(canonical_json(result.record())) > limits.max_bytes:
        raise ContractError("gap outcome result byte capacity exhausted")
    object.__setattr__(result, "_recipe", dict(target=target, points=tuple(points), coverage=coverage,
        query_at=query_at, published_at=published_at, limits=limits))
    return result


def validate_gap_outcome(value):
    if type(value) is not GapOutcome or type(value._recipe) is not dict or gap_outcome(**value._recipe) != value:
        raise IntegrityError("gap outcome changed from its actual frozen target and retained observations")


class GapOutcomeLedger:
    def __init__(self, *, limits=DEFAULT_LIMITS):
        limits.__post_init__()
        self.limits, self.outcomes = limits, ()

    def append(self, outcome):
        validate_gap_outcome(outcome)
        if outcome.limits != self.limits:
            raise ContractError("gap outcome limits differ from the retained ledger configuration")
        if outcome.version in {v.version for v in self.outcomes}:
            return outcome
        if len(self.outcomes) >= self.limits.max_references:
            raise ContractError("gap outcome ledger capacity exhausted")
        staged = (*self.outcomes, outcome)
        if len(canonical_json({"limits": self.limits, "outcomes": tuple(v.record() for v in staged)})) > self.limits.max_bytes:
            raise ContractError("gap ledger byte capacity exhausted before publication")
        self.outcomes = staged
        return outcome

    def checkpoint(self):
        return canonical_json({"limits": self.limits, "outcomes": tuple(v.record() for v in self.outcomes)})

    @classmethod
    def restore(cls, payload, *, recipes, limits=DEFAULT_LIMITS):
        bounded_rows(recipes, limits.max_references, name="gap restoration recipes")
        if type(payload) is not bytes or len(payload)>limits.max_bytes:
            raise ContractError("gap checkpoint byte capacity exhausted")
        result = cls(limits=limits)
        for recipe in recipes:
            result.append(gap_outcome(**recipe))
        if result.checkpoint() != payload:
            raise IntegrityError("gap checkpoint differs from complete retained recipes/configuration")
        return result


def publish_open_reference(observation, *, graph, clocks, generator, generator_version, object_id, previous=None):
    """One actual F10 publication; formation origin and object birth survive value corrections."""
    from trading_research.foundations.object_graph import (
        AnchorVersion, AtomicBatch, BirthKey, Eligibility, EvidencePurpose, EvidenceState, EvidenceVersion,
        Existence, Geometry, ObjectGraph, ObjectRevision, Support,
    )
    validate_open(observation)
    if type(graph) is not ObjectGraph or type(clocks) is not PublicationClock or clocks.actual_completion_at is None:
        raise ContractError("opening object needs actual F10 graph and computation completion")
    ref = observation.reference
    if not ref.available(clocks.decision_cut) or clocks.input_known_at < ref.known_at:
        raise DependencyUnavailable("opening object requires its actual observed reference before publication")
    r=observation._recipe
    captured=capture_trade_window(r['view'],instrument=r['coverage'].instrument,
        start=r['selection'].window.start,end=r['selection'].window.end,cut=r['cut'],published_at=r['published_at'],
        definition_version=r['selection'].window.definition_version,aggregation_unit=r['aggregation_unit'],
        coverage=r['coverage'],max_inputs=r['limits'].max_inputs,max_bytes=r['limits'].max_bytes)
    validate_trade_window(captured,r['view'],publication_cut=clocks.decision_cut)
    _name(generator)
    _name(generator_version)
    _name(object_id)
    known = clocks.known_at
    ttl = graph.definition.ttl_ns
    if ttl is None:
        raise ContractError("public opening reference needs a fixed registered object TTL")
    revision, prior_evidence, birth, members = 0, None, None, []
    if previous is not None:
        if type(previous) is not ObjectRevision or graph.get_version(previous.version_id) != previous:
            raise IntegrityError("opening correction lacks its actual F10 predecessor")
        current = graph.object_asof(object_id, clocks.decision_cut)
        if current is None or current.object != previous or previous.object_id != object_id:
            raise ContractError("opening correction must extend the actual current object head")
        born, revision, birth = current.born_at, previous.revision+1, previous.birth
        prior_evidence = previous.evidence_versions[0]
        if previous.birth.instrument != ref.instrument or previous.birth.generator != generator or previous.birth.generator_definition != generator_version:
            raise ContractError("opening correction changed its canonical birth definition")
    else:
        born = known
    if ref.horizon_end != born+ttl or known >= born+ttl:
        raise ContractError("opening reference horizon must equal its original F10 birth plus fixed TTL")
    source_id = "s:"+digest((object_id, "opening_value"))
    ev_id = "e:"+digest((object_id, revision, observation.id))
    measurement = EvidenceVersion(source_id, ev_id, revision, prior_evidence, ref.observed_at, known,
        Support.OBSERVED, ref.instrument, digest(observation.record()), EvidencePurpose.MEASUREMENT)
    if birth is None:
        formation_id = "s:"+digest((object_id, "opening_origin"))
        origin_ev = EvidenceVersion(formation_id, "e:"+digest((object_id, "origin")), 0, None,
            ref.observed_at, known, Support.OBSERVED, ref.instrument,
            digest((observation.selection_version, ref.observed_at, "first_observed_origin")))
        anchor = AnchorVersion("a:"+digest(object_id), "av:"+digest((object_id, "origin")), 0, None,
            (origin_ev.version_id,), ref.observed_at, ref.observed_at, ref.observed_at, known)
        birth = BirthKey(generator, generator_version, ref.instrument, (anchor.version_id,),
                          (source_id, formation_id), object_id)
        members.extend((origin_ev, anchor))
    else:
        anchor = graph.get_version(birth.anchors[0])
        if anchor.start != ref.observed_at:
            raise ContractError("changed opening event origin requires a linked new birth")
    geometry = Geometry(ref.value_ticks, ref.value_ticks, ref.value_ticks, ref.value_ticks,
        "early_open_exact_ticks_v1", ref.instrument.raw_symbol, ref.instrument.raw_symbol)
    obj = ObjectRevision(object_id, "v:"+digest((object_id, revision, observation.id)), revision,
        None if previous is None else previous.version_id, birth, geometry, (ev_id,), (), Existence.ACTIVE,
        Eligibility.ELIGIBLE, EvidenceState.OBSERVED, ref.observed_at, known, (ref.kind,))
    members.extend((measurement, obj))
    batch = AtomicBatch("batch:"+digest((obj.version_id, graph.sequence+1)), graph.sequence+1,
        graph.definition.version, clocks, tuple(members), len(members))
    graph.commit_batch(batch, expected_head=graph.head)
    return obj
