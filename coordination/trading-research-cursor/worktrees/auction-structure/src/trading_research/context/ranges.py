"""C01 exact range geometry and explicitly bounded source comparisons.

The arithmetic layer is not an evidence factory. Published range versions take
certified neutral primitives and retain their source/clock identity. Unsupported
source models remain named unavailable comparisons.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction
from types import MappingProxyType
from threading import RLock

from trading_research.context.range_adapter import (
    DerivedRangeMember, RangeRegistryLinks, primitive_registry_links, _derived_member, _require_links,
)
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.object_graph import (
    BirthKey, Eligibility, Endpoint, EndpointKind, EvidenceState, Existence,
    Geometry, ObjectRevision, RelationKind, RelationVersion,
)
from trading_research.foundations.range_primitives import ClockSelection, RangePrimitive
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


GENERATOR = "C01-range-geometry-v1"
GENERATOR_DEFINITION = "registered-linear-wick-v1"
_RANGE_TOKEN = object()


def exact(value):
    if type(value) is int:
        return Fraction(value)
    if type(value) is Fraction:
        return value
    raise ContractError("range coordinates require exact integer or rational ticks")


def ratio(pair):
    if (type(pair) not in (tuple, list) or len(pair) != 2
            or any(type(v) is not int for v in pair) or pair[1] <= 0):
        raise ContractError("exact numerator and positive denominator required")
    return Fraction(*pair)


def _name(value):
    if type(value) is not str or not value or len(value.encode()) > 256:
        raise ContractError("bounded explicit range definition identity required")
    return value


def _names(values):
    if type(values) is not tuple or not values:
        raise ContractError("nonempty immutable source identity tuple required")
    for value in values:
        _name(value)
    if len(set(values)) != len(values):
        raise ContractError("duplicate source identity")


@dataclass(frozen=True)
class RangeArithmetic:
    low: Fraction
    high: Fraction
    open: Fraction | None = None
    close: Fraction | None = None

    def __post_init__(self):
        for name in ("low", "high", "open", "close"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, exact(value))
        if self.low is None or self.high is None or self.high < self.low:
            raise ContractError("ordered exact range endpoints required")
        if any(v is not None and not self.low <= v <= self.high for v in (self.open, self.close)):
            raise ContractError("observed open/close lie outside their range")

    @property
    def width(self):
        return self.high - self.low

    @property
    def usable(self):
        return self.width > 0

    def coordinate(self, x):
        x = exact(x)
        return self.low + x * self.width if self.usable else None

    def normalized_position(self, price):
        price = exact(price)
        return (price - self.low) / self.width if self.usable else None

    def extension(self, side, k):
        k = exact(k)
        if side not in ("upper", "lower") or k < 0:
            raise ContractError("edge extension needs a named side and nonnegative ratio")
        if not self.usable:
            return None
        return self.high + k * self.width if side == "upper" else self.low - k * self.width

    @property
    def price_percent(self):
        return self.width / self.open if self.open not in (None, 0) else None

    def body25(self):
        if self.open is None or self.close is None:
            return None
        return Fraction(3, 4) * self.close + Fraction(1, 4) * self.open

    def session_body_lower25(self):
        if self.open is None or self.close is None:
            return None
        low, high = min(self.open, self.close), max(self.open, self.close)
        return low + Fraction(1, 4) * (high - low)


@dataclass(frozen=True)
class RangeDefinition:
    id: str
    version: str
    source_ids: tuple[str, ...]
    clock_variant_id: str
    calendar_version: str
    raw_instrument_definition: str
    formation_start: int
    formation_end: int
    trading_date: date
    geometry_kind: str = "wick"
    exact_ratio_tuple: tuple[Fraction, ...] = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
    price_normalization_denominator_policy: str = "range_open"
    partial_range_policy: str = "diagnostic_only"

    def __post_init__(self):
        for value in (self.id, self.version, self.clock_variant_id, self.calendar_version,
                      self.raw_instrument_definition):
            _name(value)
        _names(self.source_ids)
        timestamp(self.formation_start)
        timestamp(self.formation_end)
        if (self.formation_start >= self.formation_end or type(self.trading_date) is not date
                or self.geometry_kind not in ("wick", "session_oc", "body_envelope", "statistical_population")
                or self.price_normalization_denominator_policy != "range_open"
                or self.partial_range_policy != "diagnostic_only"
                or type(self.exact_ratio_tuple) is not tuple
                or len(self.exact_ratio_tuple) > 256
                or any(type(v) is not Fraction for v in self.exact_ratio_tuple)):
            raise ContractError("range definition requires resolved exact immutable geometry policy")

    @property
    def identity(self):
        return digest(self)


@dataclass(frozen=True)
class PriorScale:
    id: str
    value_ticks: Fraction
    formation_end: int
    published_at: int
    complete: bool

    def __post_init__(self):
        _name(self.id)
        object.__setattr__(self, "value_ticks", exact(self.value_ticks))
        timestamp(self.formation_end)
        timestamp(self.published_at)
        if type(self.complete) is not bool or self.formation_end > self.published_at:
            raise ContractError("prior scale needs explicit completion and causal availability")


def range_definition(selection: ClockSelection, *, id="source-wick", version="v1", source_ids=("C01",)):
    if type(selection) is not ClockSelection:
        raise ContractError("range definition needs its selected clock")
    return RangeDefinition(id, version, source_ids, selection.window.clock_variant,
        selection.session.version, selection.instrument.definition_version,
        selection.formation_start, selection.formation_end, selection.window.trading_date)


@dataclass(frozen=True)
class RangeVersion:
    id: str
    version_id: str
    definition: RangeDefinition
    primitive: RangePrimitive
    geometry: RangeArithmetic | None
    diagnostic_geometry: RangeArithmetic | None
    prior_scale_id: str | None
    width_prior_volatility: Fraction | None
    derivation_at: int
    _receipt: object = field(default=None, init=False, repr=False, compare=False)

    @property
    def status(self):
        return self.primitive.status

    @property
    def revision(self):
        return self.primitive.revision

    @property
    def known_at(self):
        return self.derivation_at

    @property
    def width_ticks(self):
        return None if self.geometry is None else self.geometry.width

    @property
    def observed_width_ticks(self):
        return None if self.diagnostic_geometry is None else self.diagnostic_geometry.width

    @property
    def usable_e0(self):
        return self.status == "final" and self.geometry is not None and self.geometry.usable

    @property
    def price_percent(self):
        return None if self.geometry is None else self.geometry.price_percent

    @property
    def internal(self):
        if self.geometry is None or not self.geometry.usable:
            return ()
        return tuple((q, self.geometry.coordinate(q)) for q in self.definition.exact_ratio_tuple)


def range_version(primitive: RangePrimitive, definition: RangeDefinition, *, prior_scale: PriorScale | None = None,
                  cut: int | None = None) -> RangeVersion:
    primitive_registry_links(primitive)  # Reject a detached/altered primitive.
    if type(definition) is not RangeDefinition:
        raise ContractError("registered immutable range definition required")
    selection = primitive.selection
    if (definition.calendar_version != selection.session.version
            or definition.clock_variant_id != selection.window.clock_variant
            or definition.raw_instrument_definition != primitive.instrument.definition_version
            or definition.trading_date != selection.window.trading_date
            or (definition.formation_start, definition.formation_end) != (primitive.formation_start, primitive.formation_end)):
        raise ContractError("range definition substituted another clock or raw instrument")
    if definition.geometry_kind != "wick":
        raise DependencyUnavailable("non-wick source formula requires its own registered adapter")
    available_at = max(primitive.published_at, selection.selected_at, selection.session.known_at,
                       selection.interval_graph.known_at)
    at = available_at if cut is None else timestamp(cut)
    if at < available_at:
        raise DependencyUnavailable("range source unavailable at requested cut")
    geometry = (RangeArithmetic(primitive.low_ticks, primitive.high_ticks, primitive.open_ticks, primitive.close_ticks)
                if primitive.supports("high", "low") else None)
    o, h, l, c = primitive.observed_ohlc
    diagnostic = RangeArithmetic(l, h, o, c) if h is not None and l is not None else None
    scale_id, normalized = None, None
    if prior_scale is not None:
        if type(prior_scale) is not PriorScale:
            raise ContractError("prior normalization scale needs typed lineage")
        scale_id = prior_scale.id
        if (geometry is not None and prior_scale.complete and prior_scale.value_ticks > 0
                and prior_scale.formation_end <= primitive.formation_start and prior_scale.published_at <= at):
            normalized = geometry.width / prior_scale.value_ticks
    identity = "c01-range:" + digest((primitive.id, definition.identity))
    version_id = "c01-version:" + digest((identity, primitive.version_id, prior_scale, normalized, at))
    value = RangeVersion(identity, version_id, definition, primitive, geometry, diagnostic, scale_id, normalized, at)
    object.__setattr__(value, '_receipt', (_RANGE_TOKEN, prior_scale, at, _range_record(value)))
    return value


def _range_record(value):
    return digest((value.id, value.version_id, value.definition, value.primitive.record(),
                   value.geometry, value.diagnostic_geometry, value.prior_scale_id,
                   value.width_prior_volatility, value.derivation_at))


def validate_range_version(value):
    if type(value) is not RangeVersion:
        raise ContractError('actual range formula result required')
    receipt = value._receipt
    if (type(receipt) is not tuple or len(receipt) != 4 or receipt[0] is not _RANGE_TOKEN
            or receipt[3] != _range_record(value)):
        raise ContractError('range formula result lacks its unaltered factory receipt')
    rebuilt = range_version(value.primitive, value.definition, prior_scale=receipt[1], cut=receipt[2])
    if _range_record(rebuilt) != receipt[3]:
        raise IntegrityError('range result differs from its retained formula')
    return value


def range_object_member(value: RangeVersion, links: RangeRegistryLinks, *, known_at: int,
                        previous: ObjectRevision | None = None) -> DerivedRangeMember:
    validate_range_version(value)
    _require_links(links, value.primitive)
    if links.primitive_version != value.primitive.version_id:
        raise ContractError("range object needs exact measured version and registry links")
    # Diagnostic provisional/incomplete geometry can be retained, never eligible.
    geometry = value.geometry if value.geometry is not None else value.diagnostic_geometry
    if geometry is None:
        raise DependencyUnavailable("empty range has no fabricated geometric extent")
    timestamp(known_at)
    if known_at < value.known_at:
        raise DependencyUnavailable("range object precedes its source publication")
    birth = BirthKey(GENERATOR, GENERATOR_DEFINITION, value.primitive.instrument, (),
                     (links.source_id,), value.definition.identity)
    oid = "o:" + birth.version
    revision = 0 if previous is None else previous.revision + 1
    supersedes = None if previous is None else previous.version_id
    if previous is not None and (type(previous) is not ObjectRevision or previous.object_id != oid):
        raise ContractError("range revision substituted a different birth")
    exact_geometry = Geometry(geometry.low, geometry.high, geometry.low, geometry.high,
        value.definition.identity, value.primitive.instrument.raw_symbol, value.primitive.instrument.raw_symbol)
    eligible = value.usable_e0
    existence = Existence.ACTIVE if value.status != "provisional" else Existence.PROVISIONAL
    member = ObjectRevision(oid, "v:" + digest((oid, revision, value.version_id, known_at)), revision,
        supersedes, birth, exact_geometry, (links.evidence_version_id,), (), existence,
        Eligibility.ELIGIBLE if eligible else Eligibility.INELIGIBLE, EvidenceState.OBSERVED,
        min(value.primitive.formation_end, value.primitive.observation_cut), known_at, ("range_geometry",))
    return _derived_member(member, ((value.primitive.version_id, ("high", "low")),), range_value=value)


def anchor_relation(member: ObjectRevision, links: RangeRegistryLinks, *, known_at: int) -> DerivedRangeMember:
    identity = (member.version_id, links.anchor_version_id)
    relation = RelationVersion("rel:" + digest(identity), "rv:" + digest((identity, known_at)), 0, None,
        RelationKind.SHARED_EVIDENCE, Endpoint(EndpointKind.OBJECT_VERSION, member.version_id),
        Endpoint(EndpointKind.ANCHOR_VERSION, links.anchor_version_id), known_at, known_at)
    return _derived_member(relation, ())


def _difference(interval, shared):
    if shared is None:
        return (interval,)
    start, end = interval
    a, b = shared
    return tuple(p for p in ((start, a), (b, end)) if p[0] < p[1])


@dataclass(frozen=True)
class RangeRelation:
    left_version: str
    right_version: str
    shared_intervals: tuple[tuple[int, int], ...]
    left_unique_intervals: tuple[tuple[int, int], ...]
    right_unique_intervals: tuple[tuple[int, int], ...]
    time_relation: str
    price_relation: str
    price_intersection: tuple[Fraction, Fraction] | None
    overlap_width: Fraction
    relative_width: Fraction | None
    right_open_position_in_left: Fraction | None
    anchor_displacement: Fraction | None
    known_at: int
    independent_confirmation: bool = False


def relate_ranges(left: RangeVersion, right: RangeVersion, *, retention) -> RangeRelation:
    if type(retention) is not RangeRetention:
        raise ContractError('range relation requires its explicit bounded retention state')
    with retention._lock:
        staged = retention._stage((left, right), pairs=((left.version_id, right.version_id),))
        value = _range_relation(left, right)
        retention._adopt(staged)
        return value


def _range_relation(left: RangeVersion, right: RangeVersion) -> RangeRelation:
    validate_range_version(left)
    validate_range_version(right)
    for value in (left, right):
        if type(value) is not RangeVersion:
            raise ContractError("range relation requires exact parent versions")
        primitive_registry_links(value.primitive)
    if left.primitive.instrument != right.primitive.instrument:
        raise ContractError("range relation cannot silently cross raw contracts")
    if left.geometry is None or right.geometry is None:
        raise DependencyUnavailable("range relation lacks complete parent H/L")
    a, b = (left.primitive.formation_start, left.primitive.formation_end), (right.primitive.formation_start, right.primitive.formation_end)
    s, e = max(a[0], b[0]), min(a[1], b[1])
    shared = (s, e) if s < e else None
    time_relation = ("equal" if a == b else "B_inside_A" if a[0] <= b[0] and b[1] <= a[1] else
                     "A_inside_B" if b[0] <= a[0] and a[1] <= b[1] else "overlap" if shared else "disjoint")
    ag, bg = left.geometry, right.geometry
    lo, hi = max(ag.low, bg.low), min(ag.high, bg.high)
    intersection = (lo, hi) if lo <= hi else None
    price_relation = ("equal" if (ag.low, ag.high) == (bg.low, bg.high) else
                      "B_inside_A" if ag.low <= bg.low and bg.high <= ag.high else
                      "A_inside_B" if bg.low <= ag.low and ag.high <= bg.high else
                      "overlap" if lo < hi else "touching" if lo == hi else "disjoint")
    return RangeRelation(left.version_id, right.version_id, () if shared is None else (shared,),
        _difference(a, shared), _difference(b, shared), time_relation, price_relation, intersection,
        max(Fraction(0), hi - lo), bg.width / ag.width if ag.width else None,
        ag.normalized_position(bg.open) if bg.open is not None else None,
        bg.open - ag.open if bg.open is not None and ag.open is not None else None,
        max(left.known_at, right.known_at))


@dataclass(frozen=True)
class RangeLimits:
    max_definitions: int = 32
    max_retained_range_versions: int = 4096
    max_active_relation_pairs: int = 8192

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in (self.max_definitions,
                self.max_retained_range_versions, self.max_active_relation_pairs)):
            raise ContractError("positive finite range retention bounds required")


class RangeRetention:
    """Bounded C01 publication/relation admission; F10 owns object history."""
    def __init__(self, limits=RangeLimits()):
        if type(limits) is not RangeLimits:
            raise ContractError("immutable range resource policy required")
        self.limits = limits
        self._definitions, self._versions, self._pairs = {}, {}, {}
        self._work = {"definitions_admitted": 0, "versions_retained": 0, "relation_pairs_evaluated": 0,
                      "silent_evictions": 0, "object_identity_merges": 0}
        self._lock = RLock()
        self._sealed = self.state_hash

    def _check(self):
        if self._sealed != self.state_hash:
            raise IntegrityError('range admission state changed outside admitted transitions')

    def _stage(self, values, *, pairs=()):
        self._check()
        if type(values) is not tuple or len(values) > 256 or type(pairs) is not tuple or len(pairs) > 256:
            raise ContractError('bounded immutable range admission request required')
        staged = RangeRetention(self.limits)
        for attr in ('_definitions', '_versions', '_pairs', '_work'):
            setattr(staged, attr, dict(getattr(self, attr)))
        staged._sealed = staged.state_hash
        for value in values:
            validate_range_version(value)
            staged.admit_definition(value.definition.identity, value.definition)
            staged.retain_version(value)
        for left, right in pairs:
            if left not in staged._versions or right not in staged._versions:
                raise ContractError('range relation lacks retained endpoint versions')
            staged.admit_relation(left, right)
        return staged

    def _adopt(self, staged):
        self._check()
        staged._check()
        for attr in ('_definitions', '_versions', '_pairs', '_work'):
            setattr(self, attr, dict(getattr(staged, attr)))
        self._sealed = self.state_hash

    def _put(self, store, key, value, bound, counter):
        with self._lock:
            self._check()
            _name(key)
            identity = digest(value)
            if key in store:
                if store[key] != identity:
                    raise IntegrityError("retained range identity reused with changed content")
                return False
            if len(store) >= bound:
                raise ContractError("declared range retention capacity exceeded; no silent eviction")
            store[key] = identity
            self._work[counter] += 1
            self._sealed = self.state_hash
            return True

    def admit_definition(self, definition_id, immutable_recipe):
        return self._put(self._definitions, definition_id, immutable_recipe,
                         self.limits.max_definitions, "definitions_admitted")

    def retain_version(self, value: RangeVersion):
        if type(value) is not RangeVersion:
            raise ContractError("retention requires a measured immutable C01 version")
        validate_range_version(value)
        return self._put(self._versions, value.version_id,
            (value.version_id, value.primitive.version_id, value.definition.identity),
            self.limits.max_retained_range_versions, "versions_retained")

    def admit_relation(self, left_version, right_version):
        if left_version == right_version:
            raise ContractError("relation needs distinct range versions")
        _name(left_version)
        _name(right_version)
        pair = tuple(sorted((left_version, right_version)))
        return self._put(self._pairs, digest(pair), pair,
                         self.limits.max_active_relation_pairs, "relation_pairs_evaluated")

    @property
    def definition_ids(self):
        return tuple(self._definitions)

    @property
    def version_ids(self):
        return tuple(self._versions)

    @property
    def relation_count(self):
        return len(self._pairs)

    @property
    def state_hash(self):
        return digest((self.limits, self._definitions, self._versions, self._pairs, self._work))

    @property
    def work(self):
        return MappingProxyType(dict(self._work))


def _immutable(value):
    if type(value) is dict:
        return tuple(sorted((str(k), _immutable(v)) for k, v in value.items()))
    if type(value) in (list, tuple):
        return tuple(_immutable(v) for v in value)
    if value is None or type(value) in (str, int, bool, Fraction):
        return value
    raise ContractError("source definition requires exact immutable values")


@dataclass(frozen=True)
class SourceVariant:
    id: str
    parameters: tuple
    status: str

    @classmethod
    def from_record(cls, record):
        if type(record) is not dict or "id" not in record or "status" not in record:
            raise ContractError("source variant needs identity and explicit definition status")
        _name(record["id"])
        return cls(record["id"], _immutable(record), record["status"])

    @property
    def version(self):
        return digest((self.id, self.parameters, self.status))

    @property
    def resolved(self):
        p = dict(self.parameters)
        return self.status == "defined" and bool(p.get("start_local")) and bool(p.get("end_local"))

    def formation(self):
        if not self.resolved:
            raise DependencyUnavailable("source clock unresolved or challenger unfitted")
        p = dict(self.parameters)
        return p["start_local"], p["end_local"]


@dataclass(frozen=True)
class PresetSnapshot:
    name: str
    applied_version: str
    upper_edge_ratio: Fraction
    reverse: bool
    log: bool
    color: str | None = None
    visible: bool = True

    def __post_init__(self):
        _name(self.name)
        _name(self.applied_version)
        object.__setattr__(self, "upper_edge_ratio", exact(self.upper_edge_ratio))
        if self.upper_edge_ratio < 0 or any(type(v) is not bool for v in (self.reverse, self.log, self.visible)):
            raise ContractError("preset geometry and presentation settings must be typed")

    @property
    def geometric_parameters(self):
        return self.upper_edge_ratio, self.reverse, self.log

    @property
    def geometry_definition(self):
        return digest(self.geometric_parameters)

    def upper(self, geometry: RangeArithmetic):
        if self.reverse or self.log:
            raise DependencyUnavailable("preserved_definition_requires_own_adapter")
        return geometry.extension("upper", self.upper_edge_ratio)


def historical_comparators(sessions, current_open, *, weights):
    if type(sessions) is not tuple or not sessions or len(weights) != len(sessions):
        raise ContractError("explicit historical population and aligned weights required")
    opening = exact(current_open)
    highs = tuple(exact(row[1]) for row in sessions)
    excursions = tuple(exact(h) - exact(o) for o, h in sessions)
    weights = tuple(exact(w) for w in weights)
    if any(w < 0 for w in weights) or sum(weights) <= 0:
        raise ContractError("illustrative weights must have positive mass")
    return {"absolute_high_mean": sum(highs) / len(highs),
            "anchored_high_excursion_mean": opening + sum(excursions) / len(excursions),
            "illustrative_weighted_absolute_high_mean": sum(h*w for h, w in zip(highs, weights)) / sum(weights),
            "illustrative_weighted_anchored_excursion_mean": opening + sum(h*w for h, w in zip(excursions, weights)) / sum(weights),
            "weighted_formula_is_claimed_vendor_definition": False}


def dispersion(values, *, population):
    if type(values) is not tuple or not values or type(population) is not bool:
        raise ContractError("explicit finite dispersion population required")
    values = tuple(exact(v) for v in values)
    denominator = len(values) if population else len(values) - 1
    if denominator <= 0:
        raise DependencyUnavailable("sample dispersion needs two observations")
    mean = sum(values) / len(values)
    return sum((v-mean)**2 for v in values) / denominator


def unresolved_formula(name):
    _name(name)
    raise DependencyUnavailable("unresolved source formula: " + name)


def pool_source_probabilities(populations):
    if type(populations) is not tuple or not populations:
        raise ContractError("named source populations required")
    # The engineering adapter has no registered common denominator or model.
    raise DependencyUnavailable("incompatible_undefined_denominators")


def classify_position(price, low, high):
    price, low, high = exact(price), exact(low), exact(high)
    if low > high:
        raise ContractError("ordered comparison interval required")
    return "below" if price < low else "above" if price > high else "inside"


def profile_comparators(histogram, *, low, high, open_price, val=None, vah=None):
    if type(histogram) is not tuple or not histogram:
        raise DependencyUnavailable("missing profile cannot imply inside value")
    rows = tuple((exact(price), count) for price, count in histogram)
    if any(type(count) is not int or count <= 0 for _, count in rows) or len({p for p, _ in rows}) != len(rows):
        raise ContractError("exact unique profile bins with positive counts required")
    rows = tuple(sorted(rows))
    total = sum(count for _, count in rows)
    maximum = max(count for _, count in rows)
    modes = tuple(price for price, count in rows if count == maximum)
    targets = ((total-1)//2, total//2)
    middle, cumulative = [], 0
    for price, count in rows:
        middle.extend(price for index in targets if cumulative <= index < cumulative+count)
        cumulative += count
    return {"range_open_class": classify_position(open_price, low, high),
            "value_open_class": "unavailable" if val is None or vah is None else classify_position(open_price, val, vah),
            "range_eq": (exact(low)+exact(high))/2,
            "volume_POC": modes[0] if len(modes) == 1 else None,
            "expanded_trade_median": sum(middle)/2,
            "VWAP": sum(price*count for price, count in rows)/total,
            "MPOC": None, "MPOC_formula_status": "unresolved", "calibrated_touch_probability": None}


def validate_source_obligations(required_rows, proposed_rows):
    """Validate exact individual obligations; generic family coverage is no proof."""
    if type(required_rows) is not tuple or type(proposed_rows) is not tuple:
        raise ContractError("complete immutable source obligation populations required")
    required = {row["source_id"]: row for row in required_rows}
    if len(required) != len(required_rows):
        raise ContractError("required source population repeats an identity")
    ids = [row.get("source_id") for row in proposed_rows]
    if len(set(ids)) != len(ids) or set(ids) != set(required):
        raise ContractError("source obligation denominator changed")
    for row in proposed_rows:
        origin = required[row["source_id"]]
        for key in ("source_specific_semantics", "required_disposition", "exact_open_obligation",
                    "exact_reviewed_clause", "original_proof", "upstream_or_consumer_owners"):
            if key not in origin or row.get(key) != origin[key]:
                raise IntegrityError("source-specific obligation rewritten without a new definition")
        if row.get("closure_granted") is not False or row.get("whole_source_closed") is not False:
            raise ContractError("this engineering map grants no whole-source-row closure")
        if row.get("full_clause_implementation_status") == "implemented" and not row.get("exact_clause_assertions"):
            raise ContractError("unresolved or mixed source row cannot claim implementation without assertions")
    return True
