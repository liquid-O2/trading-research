"""L02 exact edge projections and typed F10 member construction.

Geometry remains unrounded. Source births are never deduplicated by price, and
contact observations cannot grant a forecast or select an execution action.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.object_graph import (
    BirthKey, ObjectRevision, Geometry, Existence, Eligibility, EvidenceState,
    RelationVersion, RelationKind, Endpoint, EndpointKind, content_hash,
)
from trading_research.foundations.time import timestamp
from trading_research.context.range_adapter import DerivedRangeMember, _derived_member, _require_derived_member, _require_links, primitive_registry_links
from trading_research.measurements.reference_prices import require_primitive, _bound, _exact

GENERATOR = 'L02-edge-extensions-v1'
DEFINITION = 'v1'
_RESULT_TOKEN = object()


@dataclass(frozen=True)
class Location:
    role: str
    ratios: tuple[Fraction, ...]
    geometry: Geometry
    required_fields: tuple[str, ...]

    def __post_init__(self):
        if (type(self.role) is not str or not self.role or type(self.ratios) is not tuple
                or any(type(r) is not Fraction for r in self.ratios)
                or type(self.geometry) is not Geometry
                or type(self.required_fields) is not tuple or not self.required_fields
                or any(f not in ('open', 'high', 'low', 'close') for f in self.required_fields)):
            raise ContractError('typed exact location formula required')


@dataclass(frozen=True)
class LocationSet:
    primitive: object
    generator: str
    generator_definition: str
    locations: tuple[Location, ...]
    clocks: object
    horizon_end: int
    status: str
    candidate_cap: int
    semantic: str
    _recipe: object = field(default=None, init=False, repr=False, compare=False)

    @property
    def version(self):
        return content_hash((self.primitive.version_id, self.generator, self.generator_definition,
                             self.locations, self.clocks, self.horizon_end, self.status,
                             self.candidate_cap, self.semantic))

    def available(self, cut):
        timestamp(cut)
        validate_locations(self)
        return (self.clocks.known_at <= cut < self.horizon_end and self.status == 'observed'
                and self.primitive.instrument.valid(cut))

    def at(self, cut):
        return self.locations if self.available(cut) else ()

    @property
    def work(self):
        return {'source_publications': 1, 'proposed_candidates': len(self.locations),
                'retained_location_records': len(self.locations), 'candidate_cap': self.candidate_cap}


def _seal_locations(result, factory, arguments):
    object.__setattr__(result, '_recipe', (_RESULT_TOKEN, factory, arguments, result.version))
    return result


def validate_locations(result):
    if type(result) is not LocationSet:
        raise ContractError('typed location formula result required')
    recipe = result._recipe
    if (type(recipe) is not tuple or len(recipe) != 4 or recipe[0] is not _RESULT_TOKEN
            or recipe[3] != result.version):
        raise ContractError('location result lost its exact formula receipt')
    rebuilt = recipe[1](**recipe[2])
    if rebuilt.version != result.version:
        raise ContractError('location result differs from its retained formula recipe')
    return result


def select_locations(result, *, roles):
    """An authenticated subset of one already bounded formula result."""
    validate_locations(result)
    if (type(roles) is not tuple or not roles or len(set(roles)) != len(roles)
            or any(type(role) is not str for role in roles)):
        raise ContractError('unique exact formula roles required')
    chosen = tuple(value for value in result.locations if value.role in roles)
    if set(roles) != {value.role for value in chosen}:
        raise ContractError('selected role is absent from formula output')
    source = result._recipe[2]['result'] if result._recipe[1] is select_locations else result
    return _seal_locations(replace(result, locations=chosen), select_locations,
                           dict(result=source, roles=roles))


def line_geometry(primitive, *, price, tolerance, definition, ratios=()):
    _exact(price); _exact(tolerance)
    if tolerance < 0:
        raise ContractError('nonnegative exact contact tolerance required')
    raw = primitive.selection.instrument.raw_symbol
    return Geometry(price, price, price - tolerance, price + tolerance,
                    definition, raw, raw, entry_tolerance=tolerance, preset_ratios=ratios)


def edge_extensions(primitive, *, ratios=(Fraction(1, 2), Fraction(1)),
                    contact_tolerance=Fraction(1), clocks, horizon_end,
                    candidate_cap=256, regions=False):
    require_primitive(primitive, clocks=clocks, horizon_end=horizon_end)
    _bound(candidate_cap); _exact(contact_tolerance)
    if (type(ratios) is not tuple or not ratios or len(ratios) > 128
            or any(type(r) is not Fraction or r <= 0 for r in ratios)
            or len(set(ratios)) != len(ratios) or type(regions) is not bool
            or contact_tolerance < 0):
        raise ContractError('bounded distinct exact positive edge ratios required')
    count = 2 if regions else 2 * len(ratios)
    if regions and (len(ratios) != 2 or ratios[0] >= ratios[1]):
        raise ContractError('a region requires exactly two ascending edge ratios')
    if count > candidate_cap:
        raise ContractError('candidate cap exceeded before source publication')
    support = {f.field: f.status for f in primitive.field_support}
    base = (primitive, GENERATOR, DEFINITION)
    tail = (clocks, horizon_end)
    recipe = dict(primitive=primitive, ratios=ratios, contact_tolerance=contact_tolerance,
                  clocks=clocks, horizon_end=horizon_end, candidate_cap=candidate_cap, regions=regions)
    def result(locations, status):
        return _seal_locations(LocationSet(*base, locations, *tail, status, candidate_cap, 'edge'),
                               edge_extensions, recipe)
    if any(support[f] != 'observed' for f in ('high', 'low')):
        return result((), 'unavailable_required_fields')
    low, high = Fraction(primitive.low_ticks), Fraction(primitive.high_ticks)
    width = high - low
    if width < 0:
        raise ContractError('inverted certified range')
    if width == 0:
        return result((), 'unavailable_zero_width')
    definition = 'def:' + content_hash((GENERATOR, DEFINITION, ratios, contact_tolerance,
                                      'edge_distance', regions))
    output = []
    for side, edge in (('upper', high), ('lower', low)):
        sign = 1 if side == 'upper' else -1
        prices = tuple(edge + sign * ratio * width for ratio in ratios)
        if regions:
            lower, upper = min(prices), max(prices)
            raw = primitive.selection.instrument.raw_symbol
            geometry = Geometry(lower, upper, lower - contact_tolerance, upper + contact_tolerance,
                                definition, raw, raw, entry_tolerance=contact_tolerance,
                                preset_ratios=ratios)
            output.append(Location(side + '_edge_region', ratios, geometry, ('high', 'low')))
        else:
            for ratio, price in zip(ratios, prices):
                output.append(Location(side + '_edge_extension', (ratio,),
                                       line_geometry(primitive, price=price,
                                                     tolerance=contact_tolerance,
                                                     definition=definition, ratios=(ratio,)),
                                       ('high', 'low')))
    return result(tuple(output), 'observed')


def object_members(result, *, links, previous=(), parent_members=()):
    """Materialize exact consumer members; shared writer performs atomic publication."""
    validate_locations(result)
    require_primitive(result.primitive, clocks=result.clocks, horizon_end=result.horizon_end)
    _require_links(links, result.primitive)
    if type(parent_members) is not tuple or len(parent_members) > 256:
        raise ContractError('bounded immutable authentic parent members required')
    for wrapped in parent_members:
        if type(wrapped) is not DerivedRangeMember or type(wrapped.member) is not ObjectRevision:
            raise ContractError('exact derived parent object required')
        _require_derived_member(wrapped)
        if (wrapped.member.birth.generator != 'C01-range-geometry-v1'
                or wrapped.requirements != ((result.primitive.version_id, ('high', 'low')),)
                or wrapped.member.known_at > result.clocks.known_at):
            raise ContractError('location parent must bind its actual available range source')
    parents = tuple(w.member.version_id for w in parent_members)
    if len(set(parents)) != len(parents):
        raise ContractError('duplicate parent member')
    if links.primitive_version != result.primitive.version_id:
        raise ContractError('registry link belongs to a different source primitive')
    if type(previous) is not tuple or any(type(o) is not ObjectRevision for o in previous):
        raise ContractError('exact immutable predecessor object versions required')
    if len(result.locations) > result.candidate_cap:
        raise ContractError('candidate bound exceeded before member construction')
    old_by_id = {o.object_id: o for o in previous}
    if len(old_by_id) != len(previous):
        raise ContractError('duplicate prior object identities')
    out = []
    used = set()
    for location in result.locations:
        birth = BirthKey(result.generator, result.generator_definition,
                         result.primitive.selection.instrument, (), (links.source_id,),
                         content_hash((result.semantic, location.role, location.ratios,
                                       result.horizon_end, location.geometry.definition_id)))
        oid = 'o:' + birth.version
        prior = old_by_id.get(oid)
        if prior is not None:
            used.add(oid)
            if prior.birth != birth or prior.known_at >= result.clocks.known_at:
                raise ContractError('source correction changes birth or backdates object')
        revision = 0 if prior is None else prior.revision + 1
        predecessor = None if prior is None else prior.version_id
        payload = (birth, location.geometry, links.evidence_version_id, revision,
                   predecessor, result.clocks.known_at, result.horizon_end)
        obj = ObjectRevision(
            oid, 'v:' + content_hash(payload), revision, predecessor, birth,
            location.geometry, (links.evidence_version_id,), parents, Existence.ACTIVE,
            Eligibility.ELIGIBLE, EvidenceState.OBSERVED,
            result.primitive.selection.window.end, result.clocks.known_at, (location.role,))
        out.append(_derived_member(obj, ((result.primitive.version_id, location.required_fields),),
                                   horizon_end=result.horizon_end))
        endpoints = (Endpoint(EndpointKind.OBJECT_VERSION, obj.version_id),
                     Endpoint(EndpointKind.ANCHOR_VERSION, links.anchor_version_id))
        relation_key = content_hash(endpoints)
        rel = RelationVersion('rel:' + relation_key, 'rv:' + relation_key, 0, None,
                              RelationKind.SHARED_EVIDENCE, *endpoints,
                              result.primitive.selection.window.end, result.clocks.known_at)
        out.append(_derived_member(rel, ()))
    if used != set(old_by_id):
        raise ContractError('unmatched predecessor cannot be silently dropped')
    return tuple(out)


def require_candidate_capacity(groups, *, candidate_cap):
    _bound(candidate_cap)
    if type(groups) is not tuple or any(type(g) is not tuple for g in groups):
        raise ContractError('immutable candidate groups required')
    if sum(len(group) for group in groups) > candidate_cap:
        raise ContractError('complete candidate request exceeds bound before commit')
    return tuple(candidate for group in groups for candidate in group)
