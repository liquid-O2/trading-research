"""L01 internal source locations and causal, nonpredictive proposal records."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from trading_research.context.range_adapter import primitive_registry_links
from trading_research.context.ranges import RangeArithmetic, exact
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.object_graph import PublicationClock
from trading_research.foundations.range_primitives import RangePrimitive
from trading_research.foundations.time import timestamp
from trading_research.location.edge_extensions import Location, LocationSet, line_geometry, _seal_locations
from trading_research.measurements.reference_prices import require_primitive
from trading_research.operations.artifacts import digest


GENERATOR = "L01-internal-ranges-v1"
DEFINITION = "v1"
BRANCHES = ("internal_reversal_entry_into_continuation", "internal_to_edge", "internal_to_extension")


def internal_locations(primitive: RangePrimitive, *, clocks: PublicationClock, horizon_end: int,
                       include_open=False, contact_tolerance=Fraction(1), candidate_cap=256):
    """Five exact E0 internal/edge facts; optional general range open is separate.

    The four external edge extensions and four prior references are composed
    through the registered L02/L03 consumers, not duplicated here.
    """
    require_primitive(primitive, clocks=clocks, horizon_end=horizon_end)
    timestamp(horizon_end)
    tolerance = exact(contact_tolerance)
    if (type(clocks) is not PublicationClock or primitive.published_at > clocks.input_known_at
            or horizon_end <= clocks.known_at or type(include_open) is not bool
            or type(candidate_cap) is not int or candidate_cap <= 0 or tolerance < 0):
        raise ContractError("internal locations need available source, explicit clock/horizon and bounds")
    if primitive.selection.selected_at > clocks.decision_cut:
        raise DependencyUnavailable("clock selection unavailable at location decision")
    if 5 + int(include_open) > candidate_cap:
        raise ContractError("complete internal location family exceeds candidate cap")
    locations = []
    if primitive.supports("high", "low") and primitive.high_ticks > primitive.low_ticks:
        geometry = RangeArithmetic(primitive.low_ticks, primitive.high_ticks,
                                   primitive.open_ticks, primitive.close_ticks)
        rows = (("range_high", geometry.high, ("high",), ()),
                ("range_low", geometry.low, ("low",), ()),
                ("range_eq", geometry.coordinate(Fraction(1, 2)), ("high", "low"), (Fraction(1, 2),)),
                ("range_quarter25", geometry.coordinate(Fraction(1, 4)), ("high", "low"), (Fraction(1, 4),)),
                ("range_quarter75", geometry.coordinate(Fraction(3, 4)), ("high", "low"), (Fraction(3, 4),)))
        for role, price, required, ratios in rows:
            definition = "def:" + digest((GENERATOR, DEFINITION, role, ratios, tolerance))
            locations.append(Location(role, ratios, line_geometry(primitive, price=price,
                tolerance=tolerance, definition=definition, ratios=ratios), required))
    if include_open and primitive.supports("open"):
        definition = "def:" + digest((GENERATOR, DEFINITION, "range_open", tolerance))
        locations.append(Location("range_open", (), line_geometry(primitive,
            price=Fraction(primitive.open_ticks), tolerance=tolerance, definition=definition), ("open",)))
    complete = len(locations) == 5 + int(include_open)
    return _seal_locations(LocationSet(primitive, GENERATOR, DEFINITION, tuple(locations), clocks, horizon_end,
        "observed" if complete else "unavailable_required_fields_or_zero_width", candidate_cap, "range_internal"),
        internal_locations, dict(primitive=primitive, clocks=clocks, horizon_end=horizon_end,
            include_open=include_open, contact_tolerance=contact_tolerance, candidate_cap=candidate_cap))


@dataclass(frozen=True)
class LocationProposal:
    id: str
    range_version: str
    point_ticks: Fraction
    role: str
    side: str
    known_at: int
    evidence_prefix_end: int
    definition: str
    source_ids: tuple[str, ...]
    gamma_required: bool = False
    response_required: bool = False
    edge_first_required: bool = False

    def __post_init__(self):
        for value in (self.id, self.range_version, self.role, self.definition, *self.source_ids):
            if type(value) is not str or not value:
                raise ContractError("proposal requires explicit immutable source identities")
        object.__setattr__(self, "point_ticks", exact(self.point_ticks))
        timestamp(self.known_at)
        timestamp(self.evidence_prefix_end)
        if (self.evidence_prefix_end > self.known_at or self.side not in ("long", "short", "unspecified")
                or type(self.source_ids) is not tuple or not self.source_ids
                or any(value is not False for value in (self.gamma_required, self.response_required, self.edge_first_required))):
            raise ContractError("source proposal is causal and has no invented mandatory context gate")

    @property
    def version_id(self):
        return digest(self)

    def available(self, cut):
        return self.known_at <= timestamp(cut)


def role_asof(proposals, *, cut, range_version, point_ticks):
    timestamp(cut)
    point_ticks = exact(point_ticks)
    if type(proposals) is not tuple or any(type(p) is not LocationProposal for p in proposals):
        raise ContractError("immutable named role proposal versions required")
    if len({p.id for p in proposals}) != len(proposals):
        raise IntegrityError("role proposal identity reused")
    if any(p.range_version != range_version or p.point_ticks != point_ticks for p in proposals):
        raise ContractError("role proposal cannot move its source geometry")
    visible = [p for p in proposals if p.available(cut)]
    if not visible:
        return None
    newest = max(p.known_at for p in visible)
    choices = [p for p in visible if p.known_at == newest]
    if len(choices) != 1:
        raise ContractError("simultaneous role proposals need an explicit resolution policy")
    return choices[0]


def role_probability(*args, **kwargs):
    raise DependencyUnavailable("registered training artifact and causal feature model unavailable")


def bounded_offset(point, offset, *, bound, training_artifact):
    point, offset, bound = exact(point), exact(offset), exact(bound)
    if bound < 0 or abs(offset) > bound:
        raise ContractError("offset exceeds its declared geometric bound")
    if training_artifact is None:
        raise DependencyUnavailable("training_artifact_unavailable")
    raise DependencyUnavailable("bounded-offset adapter requires separately registered training definition")


def internal_room(geometry: RangeArithmetic, observed_price, *, remaining_ns):
    if type(geometry) is not RangeArithmetic:
        raise ContractError("exact range geometry required")
    price = exact(observed_price)
    timestamp(remaining_ns)
    if remaining_ns < 0:
        raise ContractError("remaining horizon cannot be negative")
    return {"width_ticks": geometry.width, "eq": geometry.coordinate(Fraction(1, 2)),
            "upper_edge_distance": geometry.high-price,
            "upper_half_extension": geometry.extension("upper", Fraction(1, 2)),
            "upper_half_extension_distance": (None if not geometry.usable else geometry.extension("upper", Fraction(1, 2))-price),
            "remaining_ns": remaining_ns, "branches": ("internal_to_edge", "internal_to_extension"),
            "guaranteed_destination": None}


@dataclass(frozen=True)
class DiagnosticBinding:
    """An immutable observation coordinate, including ineligible forming ranges.

    This is not an F10 eligible candidate target or an execution authorization.
    Actual eligible targets use ObjectGraph.bind_target.
    """
    id: str
    source_version: str
    coordinate: Fraction
    bound_at: int
    horizon_end: int

    def __post_init__(self):
        object.__setattr__(self, "coordinate", exact(self.coordinate))
        timestamp(self.bound_at)
        timestamp(self.horizon_end)
        if not self.id or not self.source_version or self.horizon_end <= self.bound_at:
            raise ContractError("diagnostic binding needs source identity and fixed future endpoint")


def observed_diagnostic(binding: DiagnosticBinding, observations, *, upper_extension=None):
    if type(binding) is not DiagnosticBinding or type(observations) is not tuple:
        raise ContractError("frozen diagnostic coordinate and immutable ordered observations required")
    visible = []
    previous = None
    for at, price in observations:
        timestamp(at)
        price = exact(price)
        if previous is not None and at <= previous:
            raise ContractError("diagnostic observation order must be exact and increasing")
        previous = at
        if binding.bound_at <= at < binding.horizon_end:
            visible.append((at, price))
    contact = next((at for at, p in visible if p == binding.coordinate), None)
    after = [p for at, p in visible if contact is not None and at >= contact]
    extension = None if upper_extension is None else exact(upper_extension)
    return {"first_contact_at": contact,
            "upper_extension_contact_at": next((at for at, p in visible if extension is not None and p >= extension), None),
            "maximum_after_contact": max(after) if after else None,
            "minimum_after_contact": min(after) if after else None,
            "bound_coordinate": binding.coordinate, "source_version": binding.source_version,
            "observation_end": binding.horizon_end, "object_retained": True}


@dataclass(frozen=True)
class ObservationWindow:
    decision_at: int
    end: int

    def __post_init__(self):
        timestamp(self.decision_at)
        timestamp(self.end)
        if self.end <= self.decision_at:
            raise ContractError("observation horizon is fixed at decision")

    def classify(self, *, contact_at, observed_intervals):
        if type(observed_intervals) is not tuple:
            raise ContractError("immutable observed coverage intervals required")
        frontier = self.decision_at
        for left, right in sorted(observed_intervals):
            timestamp(left)
            timestamp(right)
            if right <= left:
                raise ContractError("positive coverage interval required")
            if left <= frontier:
                frontier = max(frontier, right)
        if contact_at is not None:
            timestamp(contact_at)
            if not self.decision_at <= contact_at < self.end:
                raise ContractError("contact outside fixed observation horizon")
        if frontier < self.end:
            return "censored"
        return "observed_no_contact" if contact_at is None else "observed_contact"


def visit_reset_ticks(width_ticks):
    width = exact(width_ticks)
    if width < 0:
        raise ContractError("visit reset requires nonnegative source width")
    return max(Fraction(4), width/Fraction(20))


def sampled_contacts(grid, observations, *, point_ticks, tolerance_ticks):
    point, tolerance = exact(point_ticks), exact(tolerance_ticks)
    if (type(grid) is not tuple or tuple(sorted(set(grid))) != grid
            or type(observations) is not tuple or tolerance < 0):
        raise ContractError("fixed ordered decision grid and contact band required")
    for at in grid:
        timestamp(at)
    by_time = {}
    for at, value in observations:
        timestamp(at)
        if at in by_time:
            raise ContractError("ambiguous midpoint at sampled decision")
        by_time[at] = exact(value)
    return tuple(at for at in grid if at in by_time and abs(by_time[at]-point) <= tolerance)


def simultaneous_action_representatives(candidates, *, policy):
    """A declared one-action policy over retained source identities, not geometry dedup."""
    if policy != "one_action_at_simultaneous_price" or type(candidates) is not tuple:
        raise ContractError("explicit simultaneous action policy required")
    groups = {}
    ids = set()
    for identity, birth_at, distance, price in candidates:
        timestamp(birth_at)
        distance, price = exact(distance), exact(price)
        if not identity or identity in ids or distance < 0:
            raise ContractError("unique candidate source identity and exact ordering fields required")
        ids.add(identity)
        groups.setdefault(price, []).append((distance, birth_at, identity))
    return tuple(min(group)[2] for _, group in sorted(groups.items()))
