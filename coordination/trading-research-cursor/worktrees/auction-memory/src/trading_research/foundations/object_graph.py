"""Versioned factual object graph; publication batches are durable atomic cuts.

This service is the registered F10 engineering extension. It neither evaluates
source indicators nor enables the declarative runtime port or any trading rule.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, fields, is_dataclass
from enum import StrEnum
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
from types import MappingProxyType
from typing import Iterator

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError


def _time(value: int) -> int:
    if type(value) is not int or not -(2**63) <= value < 2**63:
        raise ContractError("signed int64 UTC nanoseconds required")
    return value


def _name(value: str, prefix: str | None = None) -> str:
    if (type(value) is not str or not value or len(value.encode('utf8')) > 256
            or (prefix is not None and (not value.startswith(prefix + ':') or value == prefix + ':'))):
        raise ContractError("nonempty bounded namespace-qualified identity required")
    return value


def _tuple(value: tuple, cls, *, unique: bool = False) -> None:
    if not isinstance(value, tuple) or any(not isinstance(v, cls) for v in value):
        raise ContractError("typed immutable tuple required")
    if unique and len(set(value)) != len(value):
        raise ContractError("duplicate tuple identities")


def _fraction(value: Fraction, *, nonnegative: bool = False) -> None:
    if not isinstance(value, Fraction) or (nonnegative and value < 0):
        raise ContractError("exact rational tick quantity required")


def _pack(value):
    if isinstance(value, Fraction):
        return {'numerator': value.numerator, 'denominator': value.denominator}
    if isinstance(value, StrEnum):
        return value.value
    if is_dataclass(value):
        return {f.name: _pack(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, (tuple, list)):
        return [_pack(v) for v in value]
    if isinstance(value, (dict, MappingProxyType)):
        return {k: _pack(v) for k, v in value.items()}
    if value is None or type(value) in (str, int, bool):
        return value
    raise ContractError("noncanonical or mutable payload value")


def canonical(value) -> bytes:
    return json.dumps(_pack(value), sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf8')


def content_hash(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


def _q(value: dict) -> Fraction:
    if (set(value) != {'numerator', 'denominator'} or type(value['numerator']) is not int
            or type(value['denominator']) is not int or value['denominator'] <= 0):
        raise IntegrityError("noncanonical rational encoding")
    result = Fraction(value['numerator'], value['denominator'])
    if result.numerator != value['numerator'] or result.denominator != value['denominator']:
        raise IntegrityError("rational encoding is not reduced")
    return result


class Support(StrEnum):
    OBSERVED = 'observed'
    MISSING = 'missing'
    INVALID = 'invalid'
    TOMBSTONED = 'tombstoned'


class EvidencePurpose(StrEnum):
    MEASUREMENT = 'measurement'
    MAPPING = 'mapping'
    PRESET = 'preset'
    UNIVERSE = 'universe'


class Existence(StrEnum):
    PROVISIONAL = 'provisional'
    ACTIVE = 'active'
    INVALIDATED = 'invalidated'
    EXPIRED = 'expired'
    SUPERSEDED = 'superseded'


class Eligibility(StrEnum):
    ELIGIBLE = 'eligible'
    INELIGIBLE = 'ineligible'
    UNKNOWN = 'unknown'


class EvidenceState(StrEnum):
    OBSERVED = 'observed'
    MISSING = 'missing'
    INVALID = 'invalid'
    ESTIMATED = 'estimated'


class ObservationKind(StrEnum):
    ENTER = 'enter'
    CONTACT = 'contact'
    SWEEP = 'sweep'
    RECLAIM = 'reclaim'
    EXIT = 'exit'
    RESET = 'reset'


class EndpointKind(StrEnum):
    OBJECT_VERSION = 'object_version'
    ANCHOR_VERSION = 'anchor_version'
    EVIDENCE_VERSION = 'evidence_version'
    VISIT = 'visit'
    ACTION_ALIAS = 'action_alias'


class RelationKind(StrEnum):
    PARENT = 'parent'
    SPLIT_PARENT = 'split_parent'
    MERGE_PARENT = 'merge_parent'
    MAPPED_FROM = 'mapped_from'
    SHARED_EVIDENCE = 'shared_evidence'
    EQUIVALENT = 'equivalent'
    SHARED_IDEA = 'shared_idea'
    DISPLAY_GROUP = 'display_group'
    ALIAS = 'alias'


ANCESTRY = frozenset({RelationKind.PARENT, RelationKind.SPLIT_PARENT,
                     RelationKind.MERGE_PARENT, RelationKind.MAPPED_FROM})
TERMINAL = frozenset({Existence.INVALIDATED, Existence.EXPIRED, Existence.SUPERSEDED})
TRANSITIONS = ((Existence.PROVISIONAL, Existence.PROVISIONAL),
               (Existence.PROVISIONAL, Existence.ACTIVE),
               (Existence.PROVISIONAL, Existence.INVALIDATED),
               (Existence.ACTIVE, Existence.ACTIVE),
               (Existence.ACTIVE, Existence.INVALIDATED),
               (Existence.INVALIDATED, Existence.ACTIVE),
               (Existence.ACTIVE, Existence.EXPIRED),
               (Existence.ACTIVE, Existence.SUPERSEDED))


@dataclass(frozen=True)
class Instrument:
    provider: str
    venue: str
    raw_id: str
    raw_symbol: str
    definition_version: str
    tick_size_points: Fraction
    valid_from: int = -(2**63)
    valid_until: int | None = None
    expiry_at: int | None = None
    option_terms: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        for s in (self.provider, self.venue, self.raw_id, self.raw_symbol, self.definition_version):
            _name(s)
        _fraction(self.tick_size_points)
        if self.tick_size_points <= 0:
            raise ContractError("positive exact instrument tick size required")
        _time(self.valid_from)
        for at in (self.valid_until, self.expiry_at):
            if at is not None:
                _time(at)
                if at <= self.valid_from:
                    raise ContractError("instrument lifetime is empty")
        _tuple(self.option_terms, tuple)
        if any(len(pair) != 2 or any(type(s) is not str or not s for s in pair) for pair in self.option_terms):
            raise ContractError("exact immutable option terms required")
        if len({k for k, _ in self.option_terms}) != len(self.option_terms):
            raise ContractError("duplicate option term")

    @property
    def key(self):
        return content_hash(self)

    def valid(self, at):
        return self.valid_from <= at and all(end is None or at < end for end in (self.valid_until, self.expiry_at))


@dataclass(frozen=True)
class Geometry:
    lower: Fraction
    upper: Fraction
    contact_lower: Fraction
    contact_upper: Fraction
    definition_id: str
    source_coordinate: str
    execution_coordinate: str
    estimation_uncertainty: Fraction = Fraction(0)
    mapping_uncertainty: Fraction = Fraction(0)
    entry_tolerance: Fraction = Fraction(0)
    unit: str = 'ticks'
    preset_ratios: tuple[Fraction, ...] = ()

    def __post_init__(self):
        for q in (self.lower, self.upper, self.contact_lower, self.contact_upper):
            _fraction(q)
        if self.lower > self.upper or self.contact_lower > self.contact_upper or self.unit != 'ticks':
            raise ContractError("ordered exact tick geometry required")
        for q in (self.estimation_uncertainty, self.mapping_uncertainty, self.entry_tolerance):
            _fraction(q, nonnegative=True)
        for s in (self.definition_id, self.source_coordinate, self.execution_coordinate):
            _name(s)
        _tuple(self.preset_ratios, Fraction)

    def require_preset(self):
        if not self.preset_ratios:
            raise DependencyUnavailable("preset parameters absent: name alone is not a definition")
        return content_hash((self.definition_id, self.preset_ratios))

    @property
    def version(self):
        return content_hash(self)


@dataclass(frozen=True)
class RegistryDefinition:
    id: str = 'def:f10-v1'
    generator_versions: tuple[tuple[str, str], ...] = (('fixture', 'v1'),)
    transitions: tuple[tuple[Existence, Existence], ...] = TRANSITIONS
    initial_states: tuple[Existence, ...] = (Existence.PROVISIONAL, Existence.ACTIVE)
    visit_reset_policy: str = 'preserve'
    ttl_ns: int | None = None
    batch_members_max: int = 128
    parent_edges_max: int = 32
    hot_active_max: int = 2048
    hot_relations_max: int = 8192
    payload_bytes_max: int = 1048576
    archive_page_size: int = 256

    def __post_init__(self):
        _name(self.id, 'def')
        _tuple(self.generator_versions, tuple, unique=True)
        if not self.generator_versions or any(len(p) != 2 or any(type(s) is not str or not s for s in p) for p in self.generator_versions):
            raise ContractError("registered generator definitions required")
        if len({p[0] for p in self.generator_versions}) != len(self.generator_versions):
            raise ContractError('generator name has conflicting definitions')
        object.__setattr__(self, 'generator_versions', tuple(sorted(self.generator_versions)))
        _tuple(self.transitions, tuple, unique=True)
        if any(len(p) != 2 or any(not isinstance(s, Existence) for s in p) or p[0] in (Existence.EXPIRED, Existence.SUPERSEDED) for p in self.transitions):
            raise ContractError("invalid lifecycle transition declaration")
        _tuple(self.initial_states, Existence, unique=True)
        if any(v not in {Existence.PROVISIONAL, Existence.ACTIVE} for v in self.initial_states):
            raise ContractError('terminal state cannot be an initial birth')
        if not self.initial_states or self.visit_reset_policy not in {'preserve', 'reset_on_geometry_change'}:
            raise ContractError("initial states and visit policy required")
        for n in (self.batch_members_max, self.parent_edges_max, self.hot_active_max,
                  self.hot_relations_max, self.payload_bytes_max, self.archive_page_size):
            if type(n) is not int or n <= 0:
                raise ContractError("positive resource bounds required")
        if self.ttl_ns is not None and (type(self.ttl_ns) is not int or self.ttl_ns <= 0):
            raise ContractError("positive outcome-independent TTL required")

    @property
    def version(self):
        return content_hash(self)


@dataclass(frozen=True)
class PublicationClock:
    decision_cut: int
    input_known_at: int
    known_at: int
    actual_completion_at: int | None = None
    simulated_start_at: int | None = None
    simulated_duration_ns: int | None = None
    assumption_id: str | None = None

    def __post_init__(self):
        for at in (self.decision_cut, self.input_known_at, self.known_at):
            _time(at)
        if self.actual_completion_at is not None:
            _time(self.actual_completion_at)
            if any(v is not None for v in (self.simulated_start_at, self.simulated_duration_ns, self.assumption_id)):
                raise ContractError("actual completion cannot be charged modeled delay")
        else:
            _time(self.simulated_start_at)
            if type(self.simulated_duration_ns) is not int or self.simulated_duration_ns < 0 or not self.assumption_id:
                raise ContractError("unobserved completion requires named start/duration policy")
            _name(self.assumption_id)
        if self.input_known_at > self.decision_cut or self.completion_at < self.decision_cut or self.known_at < max(self.completion_at, self.input_known_at):
            raise ContractError("publication clock violates input/completion cut")

    @property
    def completion_at(self):
        if self.actual_completion_at is not None:
            return self.actual_completion_at
        return _time(max(self.input_known_at, self.simulated_start_at) + self.simulated_duration_ns)


@dataclass(frozen=True)
class EvidenceVersion:
    source_id: str
    version_id: str
    revision: int
    predecessor: str | None
    event_at: int
    known_at: int
    support: Support
    instrument: Instrument
    content_digest: str
    purpose: EvidencePurpose = EvidencePurpose.MEASUREMENT
    mapped_instrument: Instrument | None = None

    def __post_init__(self):
        _name(self.source_id, 's'); _name(self.version_id, 'e'); _name(self.content_digest)
        _time(self.event_at); _time(self.known_at)
        if self.event_at > self.known_at:
            raise ContractError('future event cannot be a known fact')
        if type(self.revision) is not int or self.revision < 0 or not isinstance(self.support, Support) or not isinstance(self.purpose, EvidencePurpose) or not isinstance(self.instrument, Instrument):
            raise ContractError("typed evidence revision/support/instrument required")
        if self.predecessor is not None:
            _name(self.predecessor, 'e')
        if (self.purpose == EvidencePurpose.MAPPING) != (self.mapped_instrument is not None):
            raise ContractError("mapping evidence requires explicit destination instrument")
        if self.mapped_instrument is not None and not isinstance(self.mapped_instrument, Instrument):
            raise ContractError("typed mapped instrument required")


@dataclass(frozen=True)
class AnchorVersion:
    anchor_id: str
    version_id: str
    revision: int
    predecessor: str | None
    evidence_versions: tuple[str, ...]
    start: int
    end: int
    confirmed_at: int
    known_at: int

    def __post_init__(self):
        _name(self.anchor_id, 'a'); _name(self.version_id, 'av')
        for at in (self.start, self.end, self.confirmed_at, self.known_at):
            _time(at)
        if not self.start <= self.end <= self.confirmed_at <= self.known_at or type(self.revision) is not int or self.revision < 0:
            raise ContractError("anchor formation/confirmation/version invalid")
        _tuple(self.evidence_versions, str, unique=True)
        if not self.evidence_versions:
            raise ContractError("anchor needs exact evidence")
        for v in self.evidence_versions:
            _name(v, 'e')
        if self.predecessor is not None:
            _name(self.predecessor, 'av')


@dataclass(frozen=True)
class BirthKey:
    generator: str
    generator_definition: str
    instrument: Instrument
    anchors: tuple[str, ...]
    source_origins: tuple[str, ...]
    discriminator: str

    def __post_init__(self):
        for s in (self.generator, self.generator_definition, self.discriminator):
            _name(s)
        if not isinstance(self.instrument, Instrument):
            raise ContractError("typed birth instrument required")
        _tuple(self.anchors, str, unique=True); _tuple(self.source_origins, str, unique=True)
        if not self.anchors and not self.source_origins:
            raise ContractError("birth requires anchored source origin")
        for s in self.anchors:
            _name(s, 'av')
        for s in self.source_origins:
            _name(s, 's')
        object.__setattr__(self, 'source_origins', tuple(sorted(self.source_origins)))

    @property
    def version(self):
        return content_hash(self)


@dataclass(frozen=True)
class ObjectRevision:
    object_id: str
    version_id: str
    revision: int
    supersedes: str | None
    birth: BirthKey
    geometry: Geometry
    evidence_versions: tuple[str, ...]
    parent_versions: tuple[str, ...]
    existence: Existence
    eligibility: Eligibility
    evidence_state: EvidenceState
    confirmed_at: int | None
    known_at: int
    roles: tuple[str, ...] = ()
    mapping_version: str | None = None

    def __post_init__(self):
        _name(self.object_id, 'o'); _name(self.version_id, 'v'); _time(self.known_at)
        if type(self.revision) is not int or self.revision < 0 or not isinstance(self.birth, BirthKey) or not isinstance(self.geometry, Geometry):
            raise ContractError("typed immutable object revision required")
        if not isinstance(self.existence, Existence) or not isinstance(self.eligibility, Eligibility) or not isinstance(self.evidence_state, EvidenceState):
            raise ContractError("independent typed state dimensions required")
        if self.confirmed_at is not None:
            _time(self.confirmed_at)
            if self.confirmed_at > self.known_at:
                raise ContractError("geometry cannot be known before confirmation")
        if self.existence == Existence.ACTIVE and self.confirmed_at is None:
            raise ContractError("unknown formation cannot activate")
        if self.supersedes is not None:
            _name(self.supersedes, 'v')
        _tuple(self.evidence_versions, str, unique=True); _tuple(self.parent_versions, str, unique=True); _tuple(self.roles, str, unique=True)
        for s in self.evidence_versions:
            _name(s, 'e')
        for s in self.parent_versions:
            _name(s, 'v')
        for s in self.roles:
            _name(s)
        if not self.evidence_versions and not self.parent_versions:
            raise ContractError("object formation requires exact evidence or parent revisions")
        if self.geometry.execution_coordinate != self.birth.instrument.raw_symbol:
            raise ContractError("execution coordinate does not match exact raw instrument")
        if self.mapping_version is not None:
            _name(self.mapping_version, 'e')


@dataclass(frozen=True)
class ObservationEvent:
    event_id: str
    object_version: str
    visit_id: str
    kind: ObservationKind
    event_at: int
    known_at: int
    evidence_versions: tuple[str, ...]
    reason: str
    predecessor_event: str | None = None
    source_order_known: bool = True

    def __post_init__(self):
        _name(self.event_id, 'obs'); _name(self.object_version, 'v'); _name(self.visit_id, 'visit'); _name(self.reason)
        _time(self.event_at); _time(self.known_at)
        if self.event_at > self.known_at:
            raise ContractError('future event cannot be a known fact')
        if not isinstance(self.kind, ObservationKind) or type(self.source_order_known) is not bool:
            raise ContractError("typed visit event and order support required")
        _tuple(self.evidence_versions, str, unique=True)
        if not self.evidence_versions:
            raise ContractError("visit event requires actual source evidence")
        for s in self.evidence_versions:
            _name(s, 'e')
        if self.predecessor_event is not None:
            _name(self.predecessor_event, 'obs')


@dataclass(frozen=True)
class Endpoint:
    kind: EndpointKind
    id: str

    def __post_init__(self):
        if not isinstance(self.kind, EndpointKind):
            raise ContractError("typed relation endpoint required")
        _name(self.id, {EndpointKind.OBJECT_VERSION: 'v', EndpointKind.ANCHOR_VERSION: 'av',
                       EndpointKind.EVIDENCE_VERSION: 'e', EndpointKind.VISIT: 'visit',
                       EndpointKind.ACTION_ALIAS: 'alias'}[self.kind])


@dataclass(frozen=True)
class RelationVersion:
    relation_id: str
    version_id: str
    revision: int
    predecessor: str | None
    kind: RelationKind
    left: Endpoint
    right: Endpoint
    event_at: int
    known_at: int
    tombstone: bool = False
    independent_confirmation: bool = False

    def __post_init__(self):
        _name(self.relation_id, 'rel'); _name(self.version_id, 'rv')
        _time(self.event_at); _time(self.known_at)
        if self.event_at > self.known_at:
            raise ContractError('future event cannot be a known fact')
        if (type(self.revision) is not int or self.revision < 0 or not isinstance(self.kind, RelationKind)
                or not isinstance(self.left, Endpoint) or not isinstance(self.right, Endpoint)
                or self.left == self.right or type(self.tombstone) is not bool or self.independent_confirmation is not False):
            raise ContractError("explicit non-independent typed relation required")
        if self.predecessor is not None:
            _name(self.predecessor, 'rv')
        if self.kind in ANCESTRY and any(e.kind != EndpointKind.OBJECT_VERSION for e in (self.left, self.right)):
            raise ContractError("ancestry edges require exact object versions")


@dataclass(frozen=True)
class Alias:
    alias_id: str
    object_id: str
    known_at: int
    display_name: str

    def __post_init__(self):
        _name(self.alias_id, 'alias'); _name(self.object_id, 'o'); _time(self.known_at); _name(self.display_name)


@dataclass(frozen=True)
class Presentation:
    view_id: str
    object_id: str
    known_at: int
    preset_version: str
    universe_version: str
    color: str = 'default'
    clamp: Fraction = Fraction(4)
    opacity: Fraction = Fraction(35)

    def __post_init__(self):
        _name(self.view_id, 'view'); _name(self.object_id, 'o'); _time(self.known_at)
        for s in (self.preset_version, self.universe_version, self.color):
            _name(s)
        _fraction(self.clamp, nonnegative=True); _fraction(self.opacity, nonnegative=True)
        if self.opacity > 100:
            raise ContractError("opacity outside presentation scale")


MEMBER_TYPES = (EvidenceVersion, AnchorVersion, ObjectRevision, ObservationEvent,
                RelationVersion, Alias, Presentation)
MEMBER_NAMES = {cls.__name__: cls for cls in MEMBER_TYPES}


def member_record(member):
    if not isinstance(member, MEMBER_TYPES):
        raise ContractError("only registered immutable factual or presentation members allowed")
    return {'type': type(member).__name__, 'value': _pack(member)}


def _instrument(p):
    return Instrument(**{**p, 'tick_size_points': _q(p['tick_size_points']),
                         'option_terms': tuple(tuple(v) for v in p['option_terms'])})


def _geometry(p):
    return Geometry(**{**p, 'preset_ratios': tuple(_q(v) for v in p.get('preset_ratios', ())), **{k: _q(p[k]) for k in ('lower', 'upper', 'contact_lower', 'contact_upper',
                                                  'estimation_uncertainty', 'mapping_uncertainty', 'entry_tolerance')}})


def restore_member(record):
    kind, p = record['type'], dict(record['value'])
    if kind == 'EvidenceVersion':
        p.update(instrument=_instrument(p['instrument']), support=Support(p['support']), purpose=EvidencePurpose(p['purpose']),
                 mapped_instrument=None if p['mapped_instrument'] is None else _instrument(p['mapped_instrument']))
    elif kind == 'AnchorVersion':
        p['evidence_versions'] = tuple(p['evidence_versions'])
    elif kind == 'ObjectRevision':
        b = p['birth']; p.update(birth=BirthKey(**{**b, 'instrument': _instrument(b['instrument']),
                                                'anchors': tuple(b['anchors']), 'source_origins': tuple(b['source_origins'])}),
                                geometry=_geometry(p['geometry']), evidence_versions=tuple(p['evidence_versions']),
                                parent_versions=tuple(p['parent_versions']), roles=tuple(p['roles']),
                                existence=Existence(p['existence']), eligibility=Eligibility(p['eligibility']),
                                evidence_state=EvidenceState(p['evidence_state']))
    elif kind == 'ObservationEvent':
        p.update(kind=ObservationKind(p['kind']), evidence_versions=tuple(p['evidence_versions']))
    elif kind == 'RelationVersion':
        p.update(kind=RelationKind(p['kind']), left=Endpoint(EndpointKind(p['left']['kind']), p['left']['id']),
                 right=Endpoint(EndpointKind(p['right']['kind']), p['right']['id']))
    elif kind == 'Presentation':
        p.update(clamp=_q(p['clamp']), opacity=_q(p['opacity']))
    if kind not in MEMBER_NAMES:
        raise IntegrityError("unknown immutable record kind")
    return MEMBER_NAMES[kind](**p)


@dataclass(frozen=True)
class AtomicBatch:
    batch_id: str
    sequence: int
    definition_version: str
    clocks: PublicationClock
    members: tuple
    member_count: int

    def __post_init__(self):
        _name(self.batch_id, 'batch'); _name(self.definition_version)
        if type(self.sequence) is not int or self.sequence <= 0 or not isinstance(self.clocks, PublicationClock):
            raise ContractError("positive publication cursor and clocks required")
        _tuple(self.members, MEMBER_TYPES)
        if type(self.member_count) is not int or self.member_count != len(self.members) or not self.members:
            raise ContractError("complete nonempty atomic member set required")

    @property
    def record(self):
        return {'batch_id': self.batch_id, 'sequence': self.sequence,
                'definition_version': self.definition_version, 'clocks': _pack(self.clocks),
                'members': [member_record(m) for m in self.members], 'member_count': self.member_count}

    @property
    def version(self):
        return content_hash(self.record)


@dataclass(frozen=True)
class ObjectView:
    object: ObjectRevision
    dirty: bool
    reason: str
    born_at: int

    def available(self, cut, ttl_ns=None):
        return (self.object.existence == Existence.ACTIVE and self.object.eligibility == Eligibility.ELIGIBLE
                and self.object.evidence_state == EvidenceState.OBSERVED and not self.dirty
                and self.object.birth.instrument.valid(cut)
                and (ttl_ns is None or cut < self.born_at + ttl_ns))


@dataclass(frozen=True)
class ActionProposal:
    id: str
    object_version: str
    canonical_idea_id: str
    visit_id: str
    side: int
    plan_definition: str
    horizon_end: int
    instrument: Instrument

    def __post_init__(self):
        _name(self.id, 'action'); _name(self.object_version, 'v'); _name(self.canonical_idea_id, 'idea'); _name(self.visit_id, 'visit')
        _name(self.plan_definition); _time(self.horizon_end)
        if type(self.side) is not int or self.side not in (-1, 1) or not isinstance(self.instrument, Instrument):
            raise ContractError("typed full action alias identity required")


@dataclass(frozen=True)
class ScoreView:
    rank: int | None
    rank_scale: int | None
    claimed_probability: Fraction | None
    admitted_probability: None = None
    calibrated: bool = False


def score_view(*, rank=None, rank_scale=None, claimed_probability=None):
    """Presentation of an unvalidated claim; this API cannot certify a learned head."""
    if (rank is None) != (rank_scale is None) or (rank is not None and
            (type(rank) is not int or type(rank_scale) is not int or rank_scale <= 0 or not 0 <= rank <= rank_scale)):
        raise ContractError("rank scale must be explicit")
    if claimed_probability is not None:
        _fraction(claimed_probability)
        if not 0 <= claimed_probability <= 1:
            raise ContractError("probability claim outside unit interval")
    return ScoreView(rank, rank_scale, claimed_probability)


def weighted_midpoint(prices: tuple[Fraction, ...], weights: tuple[Fraction, ...]) -> Fraction:
    _tuple(prices, Fraction); _tuple(weights, Fraction)
    if not prices or len(prices) != len(weights) or any(w < 0 for w in weights) or sum(weights) <= 0:
        raise ContractError("ordinary weighted location requires positive mass, not cancelling signed density")
    return sum(p*w for p, w in zip(prices, weights)) / sum(weights)


_SCHEMA = '''
CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY CHECK(id=1), payload BLOB NOT NULL, hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS batches (sequence INTEGER PRIMARY KEY, event_key TEXT UNIQUE NOT NULL, known_at INTEGER NOT NULL, payload BLOB NOT NULL, previous TEXT, hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS records (version_id TEXT PRIMARY KEY, kind TEXT NOT NULL, identity TEXT NOT NULL, revision INTEGER NOT NULL, known_at INTEGER NOT NULL, sequence INTEGER NOT NULL, ordinal INTEGER NOT NULL, object_id TEXT, payload BLOB NOT NULL);
CREATE INDEX IF NOT EXISTS record_identity ON records(kind,identity,sequence DESC,ordinal DESC);
CREATE INDEX IF NOT EXISTS record_object ON records(kind,object_id,sequence,ordinal);
CREATE INDEX IF NOT EXISTS record_revision ON records(kind,identity,revision);
CREATE INDEX IF NOT EXISTS record_known ON records(kind,known_at,sequence,ordinal);
CREATE TABLE IF NOT EXISTS births (birth_key TEXT PRIMARY KEY, object_id TEXT UNIQUE NOT NULL, born_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS dependencies (kind TEXT NOT NULL, dependency TEXT NOT NULL, object_id TEXT NOT NULL, PRIMARY KEY(kind,dependency,object_id));
CREATE INDEX IF NOT EXISTS dependency_child ON dependencies(object_id);
CREATE TABLE IF NOT EXISTS ancestry (parent TEXT NOT NULL, child TEXT NOT NULL, edge_id TEXT NOT NULL, PRIMARY KEY(parent,child,edge_id));
CREATE INDEX IF NOT EXISTS ancestry_child ON ancestry(child);
CREATE TABLE IF NOT EXISTS object_states (object_id TEXT NOT NULL, sequence INTEGER NOT NULL, known_at INTEGER NOT NULL, version_id TEXT NOT NULL, dirty INTEGER NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(object_id,sequence));
CREATE INDEX IF NOT EXISTS object_state_cut ON object_states(object_id,sequence DESC);
CREATE TABLE IF NOT EXISTS visit_states (visit_id TEXT NOT NULL, sequence INTEGER NOT NULL, ordinal INTEGER NOT NULL, object_id TEXT NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(visit_id,sequence,ordinal));
CREATE INDEX IF NOT EXISTS visit_object ON visit_states(object_id,sequence DESC,ordinal DESC);
CREATE TABLE IF NOT EXISTS controls (id TEXT PRIMARY KEY, kind TEXT NOT NULL, sequence INTEGER NOT NULL, payload BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS current_objects (object_id TEXT PRIMARY KEY, version_id TEXT NOT NULL, instrument_key TEXT NOT NULL, hot_until INTEGER, valid_from INTEGER NOT NULL, eligible INTEGER NOT NULL, dirty INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS current_hot ON current_objects(hot_until,eligible,dirty,instrument_key);
CREATE TABLE IF NOT EXISTS current_relations (relation_id TEXT PRIMARY KEY, version_id TEXT NOT NULL, left_id TEXT NOT NULL, right_id TEXT NOT NULL, kind TEXT NOT NULL, tombstone INTEGER NOT NULL, hot_until INTEGER);
CREATE INDEX IF NOT EXISTS relation_hot ON current_relations(hot_until);
CREATE TABLE IF NOT EXISTS relation_endpoints (relation_version TEXT NOT NULL, endpoint_id TEXT NOT NULL, object_id TEXT NOT NULL, sequence INTEGER NOT NULL, PRIMARY KEY(relation_version,endpoint_id));
CREATE INDEX IF NOT EXISTS relation_owner ON relation_endpoints(object_id,sequence,relation_version);
CREATE INDEX IF NOT EXISTS relation_left ON current_relations(left_id,tombstone);
CREATE INDEX IF NOT EXISTS relation_right ON current_relations(right_id,tombstone);
CREATE TABLE IF NOT EXISTS open_visits (object_id TEXT PRIMARY KEY, visit_id TEXT NOT NULL, payload BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS visit_counters (object_id TEXT PRIMARY KEY, ordinal INTEGER NOT NULL);
CREATE TRIGGER IF NOT EXISTS batch_no_update BEFORE UPDATE ON batches BEGIN SELECT RAISE(ABORT,'immutable batch'); END;
CREATE TRIGGER IF NOT EXISTS batch_no_delete BEFORE DELETE ON batches BEGIN SELECT RAISE(ABORT,'immutable batch'); END;
CREATE TRIGGER IF NOT EXISTS record_no_update BEFORE UPDATE ON records BEGIN SELECT RAISE(ABORT,'immutable version'); END;
CREATE TRIGGER IF NOT EXISTS record_no_delete BEFORE DELETE ON records BEGIN SELECT RAISE(ABORT,'immutable version'); END;
CREATE TRIGGER IF NOT EXISTS control_no_update BEFORE UPDATE ON controls BEGIN SELECT RAISE(ABORT,'immutable cut/target'); END;
CREATE TRIGGER IF NOT EXISTS control_no_delete BEFORE DELETE ON controls BEGIN SELECT RAISE(ABORT,'immutable cut/target'); END;
'''


_INDEX_KEYS = {
    'births': ('birth_key',), 'dependencies': ('kind', 'dependency', 'object_id'),
    'ancestry': ('parent', 'child', 'edge_id'), 'current_objects': ('object_id',),
    'current_relations': ('relation_id',), 'open_visits': ('object_id',),
    'visit_counters': ('object_id',), 'relation_endpoints': ('relation_version','endpoint_id'),
}
_AUDIT_TABLES = ('records', 'births', 'dependencies', 'ancestry', 'object_states',
                 'visit_states', 'controls', 'current_objects', 'current_relations',
                 'open_visits','visit_counters','relation_endpoints')


class _MeasuredCursor:
    def __init__(self, cursor, stats):
        self.cursor, self.stats = cursor, stats

    def _read(self, row):
        if row is not None:
            self.stats['index_rows_read'] += 1
            self.stats['logical_index_bytes_read'] += sum(len(v) if isinstance(v, bytes) else len(str(v).encode('utf8')) for v in row if v is not None)
        return row

    def fetchone(self):
        return self._read(self.cursor.fetchone())

    def fetchall(self):
        return [self._read(r) for r in self.cursor.fetchall()]

    def __iter__(self):
        for row in self.cursor:
            yield self._read(row)


class _MeasuredConnection:
    def __init__(self, con, stats):
        self.con, self.stats = con, stats

    def execute(self, sql, args=()):
        self.stats['sql_statements'] += 1
        return _MeasuredCursor(self.con.execute(sql, args), self.stats)

    def executescript(self, sql):
        self.stats['sql_statements'] += 1
        return self.con.executescript(sql)


class ObjectGraph:
    """SQLite-backed immutable journal with object-local historical projections.

    SQL indexes live on disk. A commit touches only declared members and their
    dependency descendants. Integrity scans on restore are measured separately
    from object derivation, and never presented as free checkpoint validation.
    """
    __slots__ = ('__definition', '__path', '_stats', '_hot', '_verified_prefix_digest')

    def __init__(self, path: Path, *, definition: RegistryDefinition, _checkpoint_cursor=None):
        if not isinstance(definition, RegistryDefinition):
            raise ContractError("frozen registry definition required")
        self.__definition = definition
        self.__path = Path(path)
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        self._stats = {'journal_bytes_read':0,'journal_records_decoded':0,'journal_bytes_written':0,'journal_records_written':0,'retained_members_validated':0,
                       'object_evaluations': 0, 'adjacency_edges_visited': 0,
                       'query_rows_returned': 0, 'suffix_batches_replayed': 0,
                       'suffix_members_replayed': 0, 'support_checks': 0,
                       'admission_members_validated': 0, 'sql_statements': 0,
                       'index_rows_read': 0, 'logical_index_bytes_read': 0,
                       'sqlite_vm_steps_lower_bound_1000': 0, 'record_decodes': 0,
                       'hot_entries_examined': 0, 'integrity_rows_compared': 0,
                       'integrity_index_changes_folded': 0, 'capacity_rows_checked': 0}
        self._hot = {}
        self._verified_prefix_digest = None
        with self._connection(write=True) as con:
            marker=con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='config'").fetchone()
            fresh=marker is None
            if fresh:
                if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' LIMIT 1").fetchone() is not None:
                    raise IntegrityError('existing registry lost its configuration table')
                con.executescript(_SCHEMA)
            row=con.execute('SELECT payload,hash FROM config WHERE id=1').fetchone()
            if row is None and fresh:
                con.execute('INSERT INTO config VALUES (1,?,?)',(canonical(definition),definition.version))
            elif row is None:
                raise IntegrityError('existing registry lost its configuration marker')
            elif bytes(row['payload']) != canonical(definition) or row['hash'] != definition.version:
                raise IntegrityError("registry definition changed")
        self._audit_journal(checkpoint_cursor=_checkpoint_cursor)
        self._refresh_hot()

    @property
    def definition(self):
        return self.__definition

    @property
    def path(self):
        return self.__path

    @property
    def stats(self):
        return MappingProxyType(dict(self._stats))

    @property
    def hot_ids(self):
        return frozenset(self._hot)

    @contextmanager
    def _connection(self, *, write=False) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.path, timeout=30)
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA synchronous=FULL')
        def progress():
            self._stats['sqlite_vm_steps_lower_bound_1000'] += 1000
            return 0
        con.set_progress_handler(progress, 1000)
        try:
            con.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield _MeasuredConnection(con, self._stats)
            if write:
                con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    @staticmethod
    def _head(con):
        return con.execute('SELECT sequence,known_at,hash FROM batches ORDER BY sequence DESC LIMIT 1').fetchone()

    @property
    def sequence(self):
        with self._connection() as con:
            h = self._head(con)
            return 0 if h is None else h['sequence']

    @property
    def head(self):
        with self._connection() as con:
            h = self._head(con)
            return None if h is None else h['hash']

    @property
    def known_at(self):
        with self._connection() as con:
            h = self._head(con)
            return None if h is None else h['known_at']

    @staticmethod
    def _journal_hash(seq, key, known, payload, previous):
        return content_hash({'sequence': seq, 'key': key, 'known_at': known,
                             'payload': json.loads(payload), 'previous': previous})

    @staticmethod
    def _index_apply(con, change):
        table = change['table']
        if table not in _INDEX_KEYS or set(change) != {'table', 'key', 'row'}:
            raise IntegrityError('unknown retained index change')
        keys = _INDEX_KEYS[table]
        if set(change['key']) != set(keys):
            raise IntegrityError('index key schema mismatch')
        where = ' AND '.join(k+'=?' for k in keys)
        con.execute('DELETE FROM '+table+' WHERE '+where, tuple(change['key'][k] for k in keys))
        if change['row'] is not None:
            row = dict(change['row'])
            if any(row[k] != change['key'][k] for k in keys):
                raise IntegrityError('index key differs from retained row')
            if table == 'open_visits':
                row['payload'] = canonical(row['payload'])
            columns = tuple(row)
            con.execute('INSERT INTO '+table+' ('+','.join(columns)+') VALUES ('+','.join('?' for _ in columns)+')', tuple(row[k] for k in columns))

    def _index(self, con, table, row, derived, *, delete=False):
        keys = _INDEX_KEYS[table]
        change = {'table': table, 'key': {k: row[k] for k in keys},
                  'row': None if delete else dict(row)}
        self._index_apply(con, change)
        derived['index_changes'].append(change)

    @staticmethod
    def _table_digest(con, table):
        cols = [r[1] for r in con.execute('PRAGMA table_info('+table+')')]
        h = hashlib.sha256()
        for row in con.execute('SELECT * FROM '+table+' ORDER BY '+','.join(cols)):
            h.update(canonical([{'bytes': v.hex()} if isinstance(v, bytes) else v for v in row]))
        return h.hexdigest()

    def _indexes_digest(self, con):
        return content_hash({t: self._table_digest(con, t) for t in _AUDIT_TABLES})

    def _audit_journal(self, *, checkpoint_cursor=None):
        # Fold retained index deltas into a separate disk database. This is an
        # integrity pass, not source/support derivation or hidden prefix replay.
        with tempfile.TemporaryDirectory(prefix='f10-index-audit-') as root:
            raw_expected = sqlite3.connect(Path(root)/'expected.sqlite')
            raw_expected.row_factory = sqlite3.Row
            def progress():
                self._stats['sqlite_vm_steps_lower_bound_1000'] += 1000
                return 0
            raw_expected.set_progress_handler(progress,1000)
            expected = _MeasuredConnection(raw_expected,self._stats)
            try:
                expected.executescript(_SCHEMA)
                previous, n, last_known = None, 0, -(2**63)
                if checkpoint_cursor == 0:
                    self._verified_prefix_digest = self._indexes_digest(expected)
                with self._connection() as con:
                    for row in con.execute('SELECT * FROM batches ORDER BY sequence'):
                        n += 1; raw = bytes(row['payload'])
                        self._stats['journal_bytes_read'] += len(raw)
                        self._stats['journal_records_decoded'] += 1
                        if (row['sequence'] != n or row['previous'] != previous or row['known_at'] < last_known
                                or row['hash'] != self._journal_hash(n, row['event_key'], row['known_at'], raw, previous)
                                or canonical(json.loads(raw)) != raw):
                            raise IntegrityError('journal prefix/hash/publication order mismatch')
                        envelope = json.loads(raw)
                        if envelope['kind'] == 'batch':
                            batch = envelope['input']
                            if (batch['batch_id'] != row['event_key'] or batch['sequence'] != n
                                    or batch['clocks']['known_at'] != row['known_at']
                                    or batch['definition_version'] != self.definition.version
                                    or batch['member_count'] != len(batch['members'])):
                                raise IntegrityError('retained atomic envelope metadata mismatch')
                            for ordinal, member in enumerate(batch['members']):
                                obj=restore_member(member)
                                self._stats['record_decodes']+=1
                                self._stats['retained_members_validated']+=1
                                vid, kind, identity, revision, owner = self._meta(obj)
                                if isinstance(obj, ObservationEvent):
                                    owner_row = expected.execute('SELECT object_id FROM records WHERE version_id=?', (obj.object_version,)).fetchone()
                                    if owner_row is None:
                                        raise IntegrityError('orphan retained observation')
                                    owner = owner_row[0]
                                old = expected.execute('SELECT payload FROM records WHERE version_id=?', (vid,)).fetchone()
                                packed = canonical(member)
                                if old is not None:
                                    if bytes(old[0]) != packed:
                                        raise IntegrityError('retained identity conflict')
                                else:
                                    expected.execute('INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?)', (vid,kind,identity,revision,row['known_at'],n,ordinal,owner,packed))
                            for state in envelope['derived']['states']:
                                expected.execute('INSERT INTO object_states VALUES (?,?,?,?,?,?)', (state['object_id'],n,row['known_at'],state['version_id'],int(state['dirty']),state['reason']))
                            for visit in envelope['derived']['visits']:
                                expected.execute('INSERT INTO visit_states VALUES (?,?,?,?,?)', (visit['visit_id'],n,visit['member_ordinal'],visit['object_id'],canonical(visit)))
                            for change in envelope['derived']['index_changes']:
                                self._index_apply(expected, change)
                                self._stats['integrity_index_changes_folded'] += 1
                        else:
                            if envelope['id'] != row['event_key']:
                                raise IntegrityError('control identity mismatch')
                            expected.execute('INSERT INTO controls VALUES (?,?,?,?)', (envelope['id'],envelope['kind'],n,canonical(envelope['value'])))
                        previous, last_known = row['hash'], row['known_at']
                        if n == checkpoint_cursor:
                            self._verified_prefix_digest = self._indexes_digest(expected)
                    for table in _AUDIT_TABLES:
                        count = con.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
                        self._stats['integrity_rows_compared'] += count
                        if self._table_digest(con, table) != self._table_digest(expected, table):
                            raise IntegrityError('public index differs from authoritative journal: '+table)
                    schema = "SELECT type,name,tbl_name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
                    if [tuple(r) for r in con.execute(schema)] != [tuple(r) for r in expected.execute(schema)]:
                        raise IntegrityError('public index/schema protection differs')
            except (sqlite3.DatabaseError, KeyError, TypeError, ValueError) as exc:
                if isinstance(exc, IntegrityError):
                    raise
                raise IntegrityError('invalid retained journal/index envelope') from exc
            finally:
                raw_expected.close()

    def journal_page(self, *, after=0, limit=256):
        if type(after) is not int or after < 0 or type(limit) is not int or not 0 < limit <= self.definition.archive_page_size:
            raise ContractError("bounded journal pagination required")
        with self._connection() as con:
            rows = con.execute('SELECT sequence,event_key,known_at,payload,previous,hash FROM batches WHERE sequence>? ORDER BY sequence LIMIT ?', (after, limit)).fetchall()
        return tuple({'sequence': r['sequence'], 'key': r['event_key'], 'known_at': r['known_at'],
                      'payload': json.loads(r['payload']), 'previous': r['previous'], 'hash': r['hash']} for r in rows)

    @staticmethod
    def _meta(obj):
        if isinstance(obj, EvidenceVersion):
            return obj.version_id, 'evidence', obj.source_id, obj.revision, None
        if isinstance(obj, AnchorVersion):
            return obj.version_id, 'anchor', obj.anchor_id, obj.revision, None
        if isinstance(obj, ObjectRevision):
            return obj.version_id, 'object', obj.object_id, obj.revision, obj.object_id
        if isinstance(obj, ObservationEvent):
            return obj.event_id, 'observation', obj.event_id, 0, None
        if isinstance(obj, RelationVersion):
            return obj.version_id, 'relation', obj.relation_id, obj.revision, None
        if isinstance(obj, Alias):
            return obj.alias_id, 'alias', obj.alias_id, 0, obj.object_id
        return obj.view_id, 'presentation', obj.view_id, 0, obj.object_id

    def _decode_record(self, payload):
        self._stats['record_decodes'] += 1
        return restore_member(json.loads(payload))

    def _get(self, con, version_id, expected=None):
        row = con.execute('SELECT * FROM records WHERE version_id=?', (version_id,)).fetchone()
        if row is None or (expected is not None and row['kind'] != expected):
            raise ContractError("orphan or wrongly typed endpoint")
        return self._decode_record(row['payload']), row

    @staticmethod
    def _latest(con, kind, identity, cursor=None):
        cursor = 2**63-1 if cursor is None else cursor
        return con.execute('SELECT * FROM records WHERE kind=? AND identity=? AND sequence<=? ORDER BY sequence DESC,ordinal DESC LIMIT 1', (kind, identity, cursor)).fetchone()

    @staticmethod
    def _require_prior(obj, old):
        revision = obj.revision
        predecessor = obj.supersedes if isinstance(obj, ObjectRevision) else obj.predecessor
        if old is None:
            if revision != 0 or predecessor is not None:
                raise ContractError("new identity requires revision zero without predecessor")
        elif revision != old['revision']+1 or predecessor != old['version_id']:
            raise ContractError("revision must extend exact preceding version")

    def _edge(self, con, parent, child, edge_id, derived):
        if parent == child:
            raise ContractError('self ancestry')
        cycle = con.execute('WITH RECURSIVE reach(id) AS (SELECT child FROM ancestry WHERE parent=? UNION SELECT a.child FROM ancestry a JOIN reach r ON a.parent=r.id) SELECT 1 FROM reach WHERE id=? LIMIT 1', (child, parent)).fetchone()
        if cycle:
            raise ContractError('parent ancestry cycle')
        self._index(con, 'ancestry', {'parent': parent, 'child': child, 'edge_id': edge_id}, derived)

    def _relation_parents(self, con, version_id, cursor=None):
        if cursor is None:
            rows = con.execute("SELECT r.payload FROM current_relations c JOIN records r ON r.version_id=c.version_id WHERE c.right_id=? AND c.tombstone=0 AND c.kind IN ('parent','split_parent','merge_parent','mapped_from') ORDER BY c.relation_id", (version_id,))
        else:
            rows = con.execute("SELECT r.payload FROM records r WHERE r.kind='relation' AND r.sequence<=? AND json_extract(r.payload,'$.value.right.id')=? AND json_extract(r.payload,'$.value.tombstone')=0 AND json_extract(r.payload,'$.value.kind') IN ('parent','split_parent','merge_parent','mapped_from') AND NOT EXISTS (SELECT 1 FROM records n WHERE n.kind='relation' AND n.identity=r.identity AND n.sequence<=? AND (n.sequence>r.sequence OR (n.sequence=r.sequence AND n.ordinal>r.ordinal))) ORDER BY r.identity", (cursor,version_id,cursor))
        return tuple(self._decode_record(r['payload']).left.id for r in rows)

    def _support(self,con,obj,*,cursor=None):
        # Iterative memoized DAG walk avoids recursion failure and repeated
        # exponential paths through shared ancestry. Work remains observable.
        results={};active=set();stack=[(obj,None)]
        while stack:
            current,parents=stack.pop()
            if current.version_id in results:continue
            if parents is not None:
                result=(True,'supported')
                for parent in parents:
                    if not results[parent.version_id][0]:
                        result=results[parent.version_id];break
                results[current.version_id]=result;active.remove(current.version_id)
                continue
            if current.version_id in active:raise ContractError('cyclic source dependency')
            if len(results)+len(active)>self.definition.hot_active_max*self.definition.parent_edges_max:
                raise DependencyUnavailable('capacity_unavailable: complete support ancestry')
            self._stats['support_checks']+=1
            good,reason,parents=self._support_step(con,current,cursor)
            if not good or not parents:
                results[current.version_id]=(good,reason);continue
            active.add(current.version_id);stack.append((current,parents))
            stack.extend((parent,None) for parent in reversed(parents))
        return results[obj.version_id]

    def _support_step(self,con,obj,cursor):
        evidence_ids = set(obj.evidence_versions)
        if obj.mapping_version is not None:
            evidence_ids.add(obj.mapping_version)
        for eid in sorted(evidence_ids):
            evidence, row = self._get(con, eid, 'evidence')
            head = self._latest(con, 'evidence', evidence.source_id, cursor)
            if head is None or (cursor is not None and row['sequence'] > cursor):
                return (False, 'source_not_known', ())
            if evidence.support != Support.OBSERVED:
                return (False, 'source_' + evidence.support.value, ())
            if head['version_id'] != eid:
                now = self._decode_record(head['payload'])
                return (False, 'source_' + now.support.value if now.support != Support.OBSERVED else 'source_revision_pending', ())
        for avid in obj.birth.anchors:
            anchor, row = self._get(con, avid, 'anchor')
            ahead = self._latest(con, 'anchor', anchor.anchor_id, cursor)
            if ahead is None or ahead['version_id'] != avid or (cursor is not None and row['sequence'] > cursor):
                return (False, 'anchor_revision_pending', ())
            for eid in anchor.evidence_versions:
                evidence, _ = self._get(con, eid, 'evidence')
                eh = self._latest(con, 'evidence', evidence.source_id, cursor)
                if evidence.support != Support.OBSERVED or eh is None or eh['version_id'] != eid:
                    return (False, 'anchor_source_pending', ())
        parent_objects=[]
        parents = set(obj.parent_versions) | set(self._relation_parents(con, obj.version_id, cursor))
        for pid in sorted(parents):
            parent, row = self._get(con, pid, 'object')
            head = self._latest(con, 'object', parent.object_id, cursor)
            if head is None or (cursor is not None and row['sequence'] > cursor):
                return (False, 'parent_not_known', ())
            current = self._decode_record(head['payload'])
            if parent.existence != Existence.ACTIVE or parent.evidence_state != EvidenceState.OBSERVED:
                return (False, 'parent_formation_unavailable', ())
            if current.existence == Existence.INVALIDATED:
                return (False, 'parent_invalidated', ())
            if head['version_id'] != pid and current.existence not in {Existence.SUPERSEDED, Existence.EXPIRED}:
                return (False, 'parent_revision_pending', ())
            parent_objects.append(parent)
        return True,'supported',tuple(parent_objects)


    def _prior_input(self, obj, row, seq, batch):
        # Earlier staged members can complete together. Existing required inputs
        # must already belong to the frozen input cut by effective publication.
        if row['sequence'] < seq and row['known_at'] > batch.clocks.input_known_at:
            raise ContractError('required prior input arrived after frozen input cut')
        if row['sequence'] > seq or obj.known_at > batch.clocks.known_at:
            raise ContractError('future required input')

    def _hot_until(self, obj, born_at):
        if obj.existence not in {Existence.ACTIVE, Existence.PROVISIONAL}:
            return -(2**63)
        ends = []
        ends.extend(v for v in (obj.birth.instrument.valid_until, obj.birth.instrument.expiry_at) if v is not None)
        if self.definition.ttl_ns is not None:
            ends.append(born_at+self.definition.ttl_ns)
        # NULL means no expiry inside the entire accepted int64 time domain.
        # A real expiry at MAX_I64 remains exclusive and is not infinity.
        end = min(ends) if ends else None
        return None if end is None or end > 2**63-1 else end

    def _relation_hot_until(self, con, relation):
        if relation.tombstone:
            return -(2**63)
        ends = []
        for endpoint in (relation.left,relation.right):
            if endpoint.kind == EndpointKind.OBJECT_VERSION:
                original,_ = self._get(con,endpoint.id,'object')
                latest = self._latest(con,'object',original.object_id)
                obj = self._decode_record(latest['payload'])
                born = con.execute('SELECT born_at FROM births WHERE object_id=?',(obj.object_id,)).fetchone()['born_at']
                ends.append(self._hot_until(obj,born))
            else:
                ends.append(None)
        return None if any(end is None for end in ends) else max(ends)

    def _sync_dependencies(self, con, obj, derived):
        for row in con.execute('SELECT * FROM dependencies WHERE object_id=?', (obj.object_id,)).fetchall():
            self._index(con, 'dependencies', dict(row), derived, delete=True)
        keys = set()
        for eid in set(obj.evidence_versions) | ({obj.mapping_version} if obj.mapping_version else set()):
            ev, _ = self._get(con, eid, 'evidence'); keys.add(('source',ev.source_id))
        for avid in obj.birth.anchors:
            anchor, _ = self._get(con, avid, 'anchor'); keys.add(('anchor',anchor.anchor_id))
            for eid in anchor.evidence_versions:
                ev, _ = self._get(con, eid, 'evidence'); keys.add(('source',ev.source_id))
        for pid in set(obj.parent_versions) | set(self._relation_parents(con, obj.version_id)):
            parent, _ = self._get(con, pid, 'object'); keys.add(('object',parent.object_id))
        for kind, dependency in sorted(keys):
            self._index(con,'dependencies',{'kind':kind,'dependency':dependency,'object_id':obj.object_id},derived)

    def _visit_heads(self, con, *, object_id=None, cursor=None, after=('', ''), limit=256):
        cursor = 2**63-1 if cursor is None else cursor
        where, args = (' AND v.object_id=?', [cursor,object_id]) if object_id is not None else ('',[cursor])
        sql = ('SELECT v.payload FROM visit_states v WHERE v.sequence<=?'+where+
               ' AND (v.object_id,v.visit_id)>(?,?) AND NOT EXISTS (SELECT 1 FROM visit_states n WHERE n.visit_id=v.visit_id AND n.sequence<=? AND (n.sequence>v.sequence OR (n.sequence=v.sequence AND n.ordinal>v.ordinal))) ORDER BY v.object_id,v.visit_id LIMIT ?')
        return tuple(json.loads(r['payload']) for r in con.execute(sql,(*args,*after,cursor,limit)))

    def _open_visit(self, con, object_id):
        row = con.execute('SELECT payload FROM open_visits WHERE object_id=?',(object_id,)).fetchone()
        return None if row is None else json.loads(row['payload'])

    def _save_visit(self, con, visit, seq, ordinal, derived):
        value = {**visit, 'member_ordinal': ordinal}
        con.execute('INSERT INTO visit_states VALUES (?,?,?,?,?)',(value['visit_id'],seq,ordinal,value['object_id'],canonical(value)))
        derived['visits'].append(value)
        if value['state'] in {'closed','reset'}:
            self._index(con,'open_visits',{'object_id':value['object_id']},derived,delete=True)
        else:
            self._index(con,'open_visits',{'object_id':value['object_id'],'visit_id':value['visit_id'],'payload':value},derived)
        self._index(con,'visit_counters',{'object_id':value['object_id'],'ordinal':value['ordinal']},derived)

    def _reset_visit(self, con, obj, seq, ordinal, derived, reason):
        visit = self._open_visit(con,obj.object_id)
        if visit is not None:
            self._save_visit(con,{**visit,'state':'reset','reset_at':obj.known_at,'known_at':obj.known_at,'reset_reason':reason},seq,ordinal,derived)

    def _admit(self, con, obj, seq, ordinal, batch, derived):
        vid, kind, identity, revision, owner = self._meta(obj)
        self._stats['admission_members_validated'] += 1
        raw = canonical(member_record(obj))
        old_id = con.execute('SELECT payload FROM records WHERE version_id=?', (vid,)).fetchone()
        if old_id is not None:
            if bytes(old_id['payload']) != raw:
                raise IntegrityError("identity reused with changed payload")
            return set(), set(), False
        effective = batch.clocks.known_at
        if obj.known_at > effective:
            raise ContractError("future member in atomic publication")
        if isinstance(obj, (ObjectRevision, ObservationEvent, RelationVersion, Alias, Presentation)) and obj.known_at != effective:
            raise ContractError("derived member publication must equal actual batch completion cut")
        old = self._latest(con, kind, identity)
        roots, touched = set(), set()
        if isinstance(obj, (EvidenceVersion, AnchorVersion, ObjectRevision, RelationVersion)):
            self._require_prior(obj, old)
        if isinstance(obj, EvidenceVersion):
            if obj.known_at > batch.clocks.input_known_at:
                raise ContractError("external evidence arrived after frozen input cut")
            if old is not None:
                prior = self._decode_record(old['payload'])
                if (obj.instrument, obj.purpose, obj.mapped_instrument) != (prior.instrument, prior.purpose, prior.mapped_instrument):
                    raise ContractError("source identity changed instrument or purpose")
            roots.add(('source', obj.source_id))
        elif isinstance(obj, AnchorVersion):
            for eid in obj.evidence_versions:
                evidence, row = self._get(con, eid, 'evidence')
                self._prior_input(evidence,row,seq,batch)
                if evidence.known_at > obj.known_at or obj.confirmed_at > batch.clocks.decision_cut:
                    raise ContractError('anchor precedes required evidence or frozen confirmation')
            roots.add(('anchor', obj.anchor_id))
        elif isinstance(obj,ObjectRevision):
            if obj.confirmed_at is not None and obj.confirmed_at>batch.clocks.decision_cut:
                raise ContractError('formation confirmation after frozen decision cut')
            if (obj.birth.generator, obj.birth.generator_definition) not in self.definition.generator_versions:
                raise ContractError("unregistered generator definition")
            if len(obj.parent_versions)+len(obj.birth.anchors)+len(set(obj.evidence_versions)|({obj.mapping_version} if obj.mapping_version else set())) > self.definition.parent_edges_max:
                raise DependencyUnavailable("capacity_unavailable: too many parent edges")
            if obj.geometry.source_coordinate != obj.geometry.execution_coordinate and obj.mapping_version is None:
                raise ContractError("cross-coordinate geometry needs exact mapping evidence")
            if obj.mapping_version is not None:
                mapping, mapping_row = self._get(con,obj.mapping_version,'evidence')
                self._prior_input(mapping,mapping_row,seq,batch)
                latest_mapping = self._latest(con,'evidence',mapping.source_id)
                if latest_mapping['version_id'] != obj.mapping_version:
                    raise DependencyUnavailable('mapping revision is no longer current')
                if (mapping.purpose != EvidencePurpose.MAPPING or mapping.support != Support.OBSERVED
                        or mapping.mapped_instrument != obj.birth.instrument
                        or mapping.instrument.raw_symbol != obj.geometry.source_coordinate):
                    raise ContractError("mapping does not certify this source/execution coordinate pair")
            if old is None:
                if obj.existence not in self.definition.initial_states:
                    raise ContractError("birth state absent from frozen lifecycle")
                birth = con.execute('SELECT object_id FROM births WHERE birth_key=?', (obj.birth.version,)).fetchone()
                if birth is not None:
                    raise IntegrityError("same canonical birth renamed as a new object")
                self._index(con,'births',{'birth_key':obj.birth.version,'object_id':obj.object_id,'born_at':effective},derived)
            else:
                prior = self._decode_record(old['payload'])
                if prior.birth != obj.birth:
                    raise ContractError("birth identity, instrument or anchor changed: use linked new birth")
                if (prior.existence, obj.existence) not in self.definition.transitions:
                    raise ContractError("undeclared generator transition")
                if obj.existence in TERMINAL or (self.definition.visit_reset_policy == 'reset_on_geometry_change' and prior.geometry != obj.geometry):
                    self._reset_visit(con, obj, seq, ordinal, derived, 'lifecycle_' + obj.existence.value if obj.existence in TERMINAL else 'geometry_revision')
            origins = set()
            for eid in set(obj.evidence_versions) | ({obj.mapping_version} if obj.mapping_version else set()):
                evidence,row = self._get(con,eid,'evidence')
                self._prior_input(evidence,row,seq,batch)
                if evidence.instrument != obj.birth.instrument and (obj.mapping_version is None or evidence.instrument != mapping.instrument):
                    raise ContractError("object evidence crosses instrument without mapping")
                origins.add(evidence.source_id)
            for avid in obj.birth.anchors:
                anchor,anchor_row = self._get(con,avid,'anchor')
                self._prior_input(anchor,anchor_row,seq,batch)
                if anchor.known_at > effective or (obj.confirmed_at is not None and anchor.confirmed_at > obj.confirmed_at):
                    raise ContractError("unknown anchor formation")
                for eid in anchor.evidence_versions:
                    ev,ev_row = self._get(con,eid,'evidence'); self._prior_input(ev,ev_row,seq,batch)
                    if ev.instrument != obj.birth.instrument and (obj.mapping_version is None or ev.instrument != mapping.instrument):
                        raise ContractError('anchor evidence crosses unproved instrument mapping')
                    origins.add(ev.source_id)
            for pid in obj.parent_versions:
                parent,parent_row = self._get(con,pid,'object')
                self._prior_input(parent,parent_row,seq,batch)
                if parent.known_at > effective or parent.object_id == obj.object_id:
                    raise ContractError("future or self parent")
                if parent.birth.instrument != obj.birth.instrument and (obj.mapping_version is None or parent.birth.instrument != mapping.instrument):
                    raise ContractError("cross-instrument parent needs mapping evidence")
                origins.update(parent.birth.source_origins)
                self._edge(con,pid,obj.version_id,obj.version_id,derived)
            if set(obj.birth.source_origins) != origins:
                raise ContractError("canonical source origins lack evidence closure")
            supported, reason = self._support(con, obj)
            if obj.existence == Existence.ACTIVE and obj.eligibility == Eligibility.ELIGIBLE and (not supported or obj.evidence_state != EvidenceState.OBSERVED or not obj.birth.instrument.valid(effective)):
                raise DependencyUnavailable("unknown/ineligible formation cannot activate: " + reason)
            if obj.existence == Existence.PROVISIONAL and obj.eligibility == Eligibility.ELIGIBLE:
                raise ContractError("provisional formation cannot be eligible")
            self._sync_dependencies(con,obj,derived)
            touched.add(obj.object_id); roots.add(('object', obj.object_id))
        elif isinstance(obj, ObservationEvent):
            parent,parent_row = self._get(con,obj.object_version,'object')
            self._prior_input(parent,parent_row,seq,batch)
            owner = parent.object_id
            latest = self._latest(con,'object',owner)
            born = con.execute('SELECT born_at FROM births WHERE object_id=?',(owner,)).fetchone()['born_at']
            if latest['version_id'] != parent.version_id or parent.known_at > obj.known_at or obj.event_at < parent.known_at:
                raise ContractError('observation requires actual current known geometry')
            if not obj.source_order_known:
                raise DependencyUnavailable('unknown source chronology cannot assert an ordered visit transition')
            supported,_ = self._support(con,parent)
            if not ObjectView(parent,not supported,'observation',born).available(obj.known_at,self.definition.ttl_ns):
                raise DependencyUnavailable('unsupported or expired object cannot claim a visit')
            for eid in obj.evidence_versions:
                ev,row = self._get(con,eid,'evidence'); self._prior_input(ev,row,seq,batch)
                head = self._latest(con,'evidence',ev.source_id)
                if ev.support != Support.OBSERVED or head['version_id'] != eid or ev.instrument != parent.birth.instrument:
                    raise ContractError('visit source unavailable, stale or instrument mismatch')
            opened = self._open_visit(con,owner)
            collision = con.execute('SELECT object_id FROM visit_states WHERE visit_id=? LIMIT 1',(obj.visit_id,)).fetchone()
            if collision is not None and collision['object_id'] != owner:
                raise IntegrityError('visit identity reused by another birth')
            if obj.kind in {ObservationKind.ENTER,ObservationKind.CONTACT} and opened is None:
                if collision is not None or obj.predecessor_event is not None:
                    raise ContractError('closed visit cannot reopen or invent predecessor')
                count = con.execute('SELECT ordinal FROM visit_counters WHERE object_id=?',(owner,)).fetchone()
                visit = {'visit_id':obj.visit_id,'object_id':owner,'ordinal':1 if count is None else count['ordinal']+1,
                         'start_geometry':parent.version_id,'entered_at':obj.event_at,
                         'state':'entered' if obj.kind == ObservationKind.ENTER else 'contacted',
                         'known_at':obj.known_at,'last_event':obj.event_id,'last_event_at':obj.event_at,
                         'reset_at':None,'reset_reason':None}
            else:
                if opened is None or opened['visit_id'] != obj.visit_id or obj.kind in {ObservationKind.ENTER,ObservationKind.CONTACT}:
                    raise ContractError('event needs matching open visit')
                if obj.predecessor_event != opened['last_event'] or obj.event_at < opened['last_event_at']:
                    raise ContractError('visit predecessor or temporal order changed')
                states = {ObservationKind.EXIT:'closed',ObservationKind.RESET:'reset',ObservationKind.SWEEP:'swept',ObservationKind.RECLAIM:'reclaimed'}
                visit = {**opened,'state':states[obj.kind],'known_at':obj.known_at,'last_event':obj.event_id,
                         'last_event_at':obj.event_at,'reset_at':obj.event_at if obj.kind == ObservationKind.RESET else None,
                         'reset_reason':obj.reason if obj.kind == ObservationKind.RESET else None}
            self._save_visit(con,visit,seq,ordinal,derived)
        elif isinstance(obj, RelationVersion):
            for endpoint in (obj.left, obj.right):
                if endpoint.kind == EndpointKind.VISIT:
                    known = con.execute('SELECT MIN(sequence) AS sequence FROM visit_states WHERE visit_id=?', (endpoint.id,)).fetchone()['sequence']
                    if known is None or known>seq:
                        raise ContractError('orphan visit relation')
                    if known<seq:
                        prior_known=con.execute('SELECT known_at FROM batches WHERE sequence=?',(known,)).fetchone()['known_at']
                        if prior_known>batch.clocks.input_known_at:
                            raise ContractError('visit endpoint arrived after frozen input cut')
                else:
                    expected = {EndpointKind.OBJECT_VERSION: 'object', EndpointKind.ANCHOR_VERSION: 'anchor', EndpointKind.EVIDENCE_VERSION: 'evidence', EndpointKind.ACTION_ALIAS: 'alias'}[endpoint.kind]
                    endpoint_obj,row = self._get(con,endpoint.id,expected)
                    self._prior_input(endpoint_obj,row,seq,batch)
                    if endpoint_obj.known_at > obj.known_at:
                        raise ContractError("future relation endpoint")
            if old is not None:
                prior = self._decode_record(old['payload'])
                if (prior.kind, prior.left, prior.right) != (obj.kind, obj.left, obj.right):
                    raise ContractError("relation revision cannot secretly change endpoint identity")
            self._index(con,'current_relations',{'relation_id':obj.relation_id,'version_id':obj.version_id,
                        'left_id':obj.left.id,'right_id':obj.right.id,'kind':obj.kind.value,'tombstone':int(obj.tombstone),'hot_until':self._relation_hot_until(con,obj)},derived)
            for endpoint in (obj.left,obj.right):
                if endpoint.kind == EndpointKind.OBJECT_VERSION:
                    endpoint_obj,_ = self._get(con,endpoint.id,'object')
                    self._index(con,'relation_endpoints',{'relation_version':obj.version_id,'endpoint_id':endpoint.id,'object_id':endpoint_obj.object_id,'sequence':seq},derived)
            if obj.kind in ANCESTRY:
                parent,_ = self._get(con,obj.left.id,'object'); child,_ = self._get(con,obj.right.id,'object')
                if parent.birth.instrument != child.birth.instrument:
                    if obj.kind != RelationKind.MAPPED_FROM or child.mapping_version is None:
                        raise ContractError('cross-instrument ancestry requires exact mapped-from support')
                    mapping,_ = self._get(con,child.mapping_version,'evidence')
                    if mapping.instrument != parent.birth.instrument or mapping.mapped_instrument != child.birth.instrument:
                        raise ContractError('relation mapping endpoints differ')
                if obj.tombstone:
                    for row in con.execute('SELECT * FROM ancestry WHERE edge_id=?',(obj.relation_id,)).fetchall():
                        self._index(con,'ancestry',dict(row),derived,delete=True)
                else:
                    self._edge(con,obj.left.id,obj.right.id,obj.relation_id,derived)
                touched.add(child.object_id); roots.add(('object',child.object_id))
        else:
            owner_row=self._latest(con,'object',obj.object_id)
            if owner_row is None:
                raise ContractError('alias/presentation references missing birth')
            self._prior_input(self._decode_record(owner_row['payload']),owner_row,seq,batch)
        con.execute('INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?)',(vid,kind,identity,revision,effective,seq,ordinal,owner,raw))
        if isinstance(obj,RelationVersion) and obj.kind in ANCESTRY:
            latest_child = self._latest(con,'object',child.object_id)
            self._sync_dependencies(con,self._decode_record(latest_child['payload']),derived)
        return roots, touched, True

    def _descendants(self, con, roots):
        queue, seen, objects, edges = list(sorted(roots)), set(), set(), 0
        while queue:
            key = queue.pop()
            if key in seen:
                continue
            seen.add(key)
            for row in con.execute('SELECT object_id FROM dependencies WHERE kind=? AND dependency=? ORDER BY object_id', key):
                edges+=1;oid=row['object_id'];objects.add(oid)
                if len(objects)>self.definition.hot_active_max:
                    raise DependencyUnavailable('capacity_unavailable: complete dirty closure population')
                queue.append(('object', oid))
        return objects, edges

    def commit_batch(self, batch: AtomicBatch, *, expected_head: str | None):
        if not isinstance(batch, AtomicBatch) or batch.definition_version != self.definition.version:
            raise ContractError("atomic batch has wrong frozen definition")
        if batch.member_count > self.definition.batch_members_max or len(canonical(batch.record)) > self.definition.payload_bytes_max:
            raise DependencyUnavailable("capacity_unavailable: atomic payload bounds")
        evaluated, edges = 0, 0
        with self._connection(write=True) as con:
            duplicate = con.execute('SELECT payload,hash FROM batches WHERE event_key=?', (batch.batch_id,)).fetchone()
            if duplicate is not None:
                old = json.loads(duplicate['payload'])
                if old.get('kind') != 'batch' or canonical(old['input']) != canonical(batch.record):
                    raise IntegrityError("batch identity reused with changed content")
                return duplicate['hash'], False
            h = self._head(con); seq = 1 if h is None else h['sequence']+1
            if batch.sequence != seq or expected_head != (None if h is None else h['hash']):
                raise ContractError("critical state changed before atomic commit")
            if h is not None and batch.clocks.known_at < h['known_at']:
                raise ContractError("publication clock cannot regress")
            frontier = con.execute("SELECT MAX(json_extract(payload,'$.at')) AS cut FROM controls WHERE kind='candidate_cut'").fetchone()['cut']
            identities = [self._meta(m)[0] for m in batch.members]
            if len(set(identities)) != len(identities):
                raise IntegrityError("duplicate member identity inside batch")
            new_facts = any(con.execute('SELECT 1 FROM records WHERE version_id=?', (v,)).fetchone() is None for v in identities)
            if frontier is not None and new_facts and batch.clocks.known_at <= frontier:
                raise ContractError("new publication would alter frozen time prefix")
            confirmations = [m.confirmed_at for m in batch.members if isinstance(m, (AnchorVersion, ObjectRevision)) and m.confirmed_at is not None]
            if batch.clocks.known_at != max(batch.clocks.input_known_at, batch.clocks.completion_at, *confirmations):
                raise ContractError("known time must be actual causal maximum, not backdraw time")
            roots,touched = set(),set(); derived = {'states':[],'visits':[],'index_changes':[]}
            for ordinal, member in enumerate(batch.members):
                r, t, _ = self._admit(con, member, seq, ordinal, batch, derived)
                roots.update(r); touched.update(t)
            descendants, edges = self._descendants(con, roots)
            affected = touched | descendants
            for oid in sorted(affected):
                row = self._latest(con, 'object', oid)
                obj = self._decode_record(row['payload'])
                supported, reason = self._support(con, obj)
                evaluated += 1
                state = {'object_id': oid, 'version_id': obj.version_id, 'dirty': not supported, 'reason': reason}
                con.execute('INSERT INTO object_states VALUES (?,?,?,?,?,?)', (oid, seq, batch.clocks.known_at, obj.version_id, int(not supported), reason))
                derived['states'].append(state)
                born = con.execute('SELECT born_at FROM births WHERE object_id=?',(oid,)).fetchone()['born_at']
                self._index(con,'current_objects',{'object_id':oid,'version_id':obj.version_id,
                            'instrument_key':obj.birth.instrument.key,'hot_until':self._hot_until(obj,born),
                            'valid_from':obj.birth.instrument.valid_from,
                            'eligible':int(obj.existence == Existence.ACTIVE and obj.eligibility == Eligibility.ELIGIBLE and obj.evidence_state == EvidenceState.OBSERVED),
                            'dirty':int(not supported)},derived)
            # Retire relation hot capacity by the same fixed endpoint lifetimes.
            incident = set()
            for oid in sorted(affected):
                incident.update(r['relation_id'] for r in con.execute('SELECT DISTINCT c.relation_id FROM relation_endpoints e JOIN current_relations c ON c.version_id=e.relation_version WHERE e.object_id=?',(oid,)))
            for rid in sorted(incident):
                rr = con.execute('SELECT * FROM current_relations WHERE relation_id=?',(rid,)).fetchone()
                relation,_ = self._get(con,rr['version_id'],'relation')
                self._index(con,'current_relations',{**dict(rr),'hot_until':self._relation_hot_until(con,relation)},derived)
            active_count = con.execute('SELECT COUNT(*) FROM current_objects WHERE (hot_until IS NULL OR hot_until>?) AND valid_from<=?',(batch.clocks.known_at,batch.clocks.known_at)).fetchone()[0]
            relation_count = con.execute('SELECT COUNT(*) FROM current_relations WHERE (hot_until IS NULL OR hot_until>?)',(batch.clocks.known_at,)).fetchone()[0]
            self._stats['capacity_rows_checked'] += active_count+relation_count
            if active_count > self.definition.hot_active_max or relation_count > self.definition.hot_relations_max:
                raise DependencyUnavailable('capacity_unavailable: active graph bound')
            envelope = {'kind': 'batch', 'input': batch.record, 'derived': derived}
            raw = canonical(envelope)
            if len(raw) > self.definition.payload_bytes_max:
                raise DependencyUnavailable("capacity_unavailable: retained atomic envelope")
            previous = None if h is None else h['hash']
            value = self._journal_hash(seq, batch.batch_id, batch.clocks.known_at, raw, previous)
            con.execute('INSERT INTO batches VALUES (?,?,?,?,?,?)', (seq, batch.batch_id, batch.clocks.known_at, raw, previous, value))
        self._stats['journal_records_written']+=1
        self._stats['journal_bytes_written']+=len(raw)
        self._stats['object_evaluations'] += evaluated
        self._stats['adjacency_edges_visited'] += edges
        self._update_hot(affected,batch.clocks.known_at)
        return value, True

    def _cursor(self, con, cut, cursor=None):
        _time(cut)
        head = self._head(con); end = 0 if head is None else head['sequence']
        if cursor is not None and (type(cursor) is not int or not 0 <= cursor <= end):
            raise ContractError("cut must reference a completed publication cursor")
        upper = end if cursor is None else cursor
        row = con.execute('SELECT MAX(sequence) AS n FROM batches WHERE known_at<=? AND sequence<=?', (cut, upper)).fetchone()
        return 0 if row['n'] is None else row['n']

    def _object_view(self, con, oid, cursor):
        row = self._latest(con, 'object', oid, cursor)
        if row is None:
            return None
        obj = self._decode_record(row['payload'])
        state = con.execute('SELECT dirty,reason FROM object_states WHERE object_id=? AND sequence<=? ORDER BY sequence DESC LIMIT 1', (oid, cursor)).fetchone()
        if state is None:
            raise IntegrityError("object lacks atomic support projection")
        born = con.execute('SELECT born_at FROM births WHERE object_id=?', (oid,)).fetchone()['born_at']
        return ObjectView(obj, bool(state['dirty']), state['reason'], born)

    def object_asof(self, object_id, cut, *, cursor=None):
        _name(object_id, 'o')
        with self._connection() as con:
            n = self._cursor(con, cut, cursor)
            value = self._object_view(con, object_id, n)
        self._stats['query_rows_returned'] += int(value is not None)
        return value

    def get_version(self, version_id):
        _name(version_id)
        with self._connection() as con:
            row = con.execute('SELECT payload FROM records WHERE version_id=?', (version_id,)).fetchone()
        if row is None:
            raise DependencyUnavailable('not_found: exact immutable version')
        self._stats['query_rows_returned'] += 1
        return self._decode_record(row['payload'])

    def revisions(self, object_id, *, after_revision=-1, limit=256):
        _name(object_id, 'o')
        if type(after_revision) is not int or after_revision < -1 or type(limit) is not int or not 0 < limit <= self.definition.archive_page_size:
            raise ContractError("bounded version pagination required")
        with self._connection() as con:
            rows = con.execute("SELECT payload FROM records WHERE kind='object' AND identity=? AND revision>? ORDER BY revision LIMIT ?", (object_id, after_revision, limit)).fetchall()
        self._stats['query_rows_returned'] += len(rows)
        return tuple(self._decode_record(r['payload']) for r in rows)

    def _views(self, con, cursor, instrument=None):
        # Complete denominator requests are explicitly bounded. No truncation:
        # excessive retained populations fail before publication.
        sql = "SELECT r.identity FROM records r WHERE r.kind='object' AND r.sequence<=? AND NOT EXISTS(SELECT 1 FROM records n WHERE n.kind='object' AND n.identity=r.identity AND n.sequence<=? AND (n.sequence>r.sequence OR(n.sequence=r.sequence AND n.ordinal>r.ordinal)))"
        args = [cursor,cursor]
        if instrument is not None:
            sql += " AND json_extract(r.payload,'$.value.birth.instrument')=json(?)"
            args.append(canonical(instrument).decode())
        rows = con.execute(sql+' ORDER BY r.identity LIMIT ?',(*args,self.definition.hot_active_max+1)).fetchall()
        if len(rows) > self.definition.hot_active_max:
            raise DependencyUnavailable('capacity_unavailable: complete denominator population')
        return tuple(self._object_view(con,r['identity'],cursor) for r in rows)

    def _active(self, con, cursor, cut, instrument=None):
        head = self._head(con)
        if cursor == (0 if head is None else head['sequence']):
            sql = 'SELECT r.payload FROM current_objects c JOIN records r ON r.version_id=c.version_id WHERE (c.hot_until IS NULL OR c.hot_until>?) AND c.valid_from<=? AND c.eligible=1 AND c.dirty=0'
            args = [cut,cut]
            if instrument is not None:
                sql += ' AND c.instrument_key=?'; args.append(instrument.key)
            sql += ' ORDER BY c.object_id'
        else:
            sql = "SELECT r.payload FROM object_states s JOIN records r ON r.version_id=s.version_id JOIN births b ON b.object_id=s.object_id WHERE s.sequence<=? AND s.dirty=0 AND NOT EXISTS(SELECT 1 FROM object_states n WHERE n.object_id=s.object_id AND n.sequence<=? AND n.sequence>s.sequence) AND json_extract(r.payload,'$.value.existence')='active' AND json_extract(r.payload,'$.value.eligibility')='eligible' AND json_extract(r.payload,'$.value.evidence_state')='observed' AND json_extract(r.payload,'$.value.birth.instrument.valid_from')<=? AND (json_extract(r.payload,'$.value.birth.instrument.valid_until') IS NULL OR json_extract(r.payload,'$.value.birth.instrument.valid_until')>?) AND (json_extract(r.payload,'$.value.birth.instrument.expiry_at') IS NULL OR json_extract(r.payload,'$.value.birth.instrument.expiry_at')>?)"
            args = [cursor,cursor,cut,cut,cut]
            if self.definition.ttl_ns is not None:
                threshold = cut-self.definition.ttl_ns
                # Every representable birth passes when the exact threshold
                # lies below MIN_I64; do not bind an overflowing SQLite int.
                if threshold >= -(2**63):
                    sql += ' AND b.born_at>?'; args.append(threshold)
            if instrument is not None:
                sql += " AND json_extract(r.payload,'$.value.birth.instrument')=json(?)"; args.append(canonical(instrument).decode())
            sql += ' ORDER BY s.object_id'
        rows = con.execute(sql+' LIMIT ?',(*args,self.definition.hot_active_max+1)).fetchall()
        if len(rows) > self.definition.hot_active_max:
            raise IntegrityError('retained active population exceeds frozen bound')
        return tuple(self._decode_record(r['payload']) for r in rows)

    def active_set(self, cut, *, instrument=None, cursor=None):
        if instrument is not None and not isinstance(instrument,Instrument):
            raise ContractError('exact instrument namespace required')
        with self._connection() as con:
            n = self._cursor(con,cut,cursor)
            values = self._active(con,n,cut,instrument)
        self._stats['query_rows_returned'] += len(values)
        return values

    def _refresh_hot(self, cut=None):
        at = self.known_at if cut is None else cut
        self._hot = {}
        if at is None:
            return
        with self._connection() as con:
            rows = con.execute('SELECT object_id,hot_until FROM current_objects WHERE (hot_until IS NULL OR hot_until>?) AND valid_from<=? AND eligible=1 AND dirty=0 LIMIT ?',(at,at,self.definition.hot_active_max+1)).fetchall()
            if len(rows) > self.definition.hot_active_max:
                raise IntegrityError('hot active bound exceeded')
            self._hot = {r['object_id']:r['hot_until'] for r in rows}

    def _update_hot(self, affected, cut):
        # Only bounded hot metadata is inspected for wall-clock expiry; no
        # unrelated archived object is decoded or support-recomputed here.
        self._stats['hot_entries_examined'] += len(self._hot)
        self._hot = {oid:end for oid,end in self._hot.items() if end is None or end>cut}
        with self._connection() as con:
            for oid in sorted(affected):
                row = con.execute('SELECT * FROM current_objects WHERE object_id=?',(oid,)).fetchone()
                if row is not None and (row['hot_until'] is None or row['hot_until']>cut) and row['valid_from']<=cut and row['eligible'] and not row['dirty']:
                    self._hot[oid] = row['hot_until']
                else:
                    self._hot.pop(oid,None)

    def _page_limit(self, limit):
        if type(limit) is not int or not 0<limit<=self.definition.archive_page_size:
            raise ContractError('bounded archive page required')
        return limit

    def _events(self,con,cursor,*,object_id=None,after_event=None,limit=256,instrument=None):
        seq, ordinal = 0,-1
        if after_event is not None:
            _name(after_event,'obs')
            row = con.execute("SELECT sequence,ordinal FROM records WHERE kind='observation' AND version_id=? AND sequence<=?",(after_event,cursor)).fetchone()
            if row is None:
                raise ContractError('event page cursor absent from cut')
            seq,ordinal = row['sequence'],row['ordinal']
        sql = "SELECT payload FROM records WHERE kind='observation' AND sequence<=? AND (sequence,ordinal)>(?,?)"
        args = [cursor,seq,ordinal]
        if object_id is not None:
            sql += ' AND object_id=?';args.append(object_id)
        if instrument is not None:
            sql += ' AND object_id IN (SELECT object_id FROM current_objects WHERE instrument_key=?)';args.append(instrument.key)
        return tuple(self._decode_record(r['payload']) for r in con.execute(sql+' ORDER BY sequence,ordinal LIMIT ?',(*args,limit)))

    def events_asof(self, cut, *, object_id=None, cursor=None, after_event=None, limit=256):
        if object_id is not None:
            _name(object_id,'o')
        self._page_limit(limit)
        with self._connection() as con:
            values = self._events(con,self._cursor(con,cut,cursor),object_id=object_id,after_event=after_event,limit=limit)
        self._stats['query_rows_returned'] += len(values)
        return values

    def visits_asof(self, cut, *, object_id=None, cursor=None, after=('', ''), limit=256):
        if object_id is not None:
            _name(object_id,'o')
        if type(after) is not tuple or len(after)!=2 or any(type(v) is not str for v in after):
            raise ContractError('exact visit pagination key required')
        self._page_limit(limit)
        with self._connection() as con:
            values = self._visit_heads(con,object_id=object_id,cursor=self._cursor(con,cut,cursor),after=after,limit=limit)
        self._stats['query_rows_returned'] += len(values)
        return tuple(_freeze(v) for v in values)

    def _relations(self, con, cursor, *, object_id=None, after_relation='', limit=256):
        sql = "SELECT r.payload FROM records r WHERE r.kind='relation' AND r.sequence<=? AND r.identity>? AND json_extract(r.payload,'$.value.tombstone')=0 AND NOT EXISTS(SELECT 1 FROM records n WHERE n.kind='relation' AND n.identity=r.identity AND n.sequence<=? AND (n.sequence>r.sequence OR(n.sequence=r.sequence AND n.ordinal>r.ordinal)))"
        args = [cursor,after_relation,cursor]
        if object_id is not None:
            sql += ' AND r.version_id IN (SELECT e.relation_version FROM relation_endpoints e WHERE e.object_id=? AND e.sequence<=?)'
            args.extend((object_id,cursor))
        return tuple(self._decode_record(r['payload']) for r in con.execute(sql+' ORDER BY r.identity LIMIT ?',(*args,limit)))

    def relations_asof(self, cut, *, object_id=None, cursor=None, after_relation='', limit=256):
        if object_id is not None:
            _name(object_id,'o')
        if type(after_relation) is not str:
            raise ContractError('relation pagination key required')
        self._page_limit(limit)
        with self._connection() as con:
            values = self._relations(con,self._cursor(con,cut,cursor),object_id=object_id,after_relation=after_relation,limit=limit)
        self._stats['query_rows_returned'] += len(values)
        return values

    def _lineage_closure(self, con, seeds, cursor):
        versions,parent_edges,relations,visits = {},set(),{},{}
        pending=list(seeds);visited_owners=set();retained_bytes=0
        def incident(endpoint_id):
            sql="SELECT r.version_id FROM records r WHERE r.kind='relation' AND r.sequence<=? AND json_extract(r.payload,'$.value.tombstone')=0 AND(json_extract(r.payload,'$.value.left.id')=? OR json_extract(r.payload,'$.value.right.id')=?) AND NOT EXISTS(SELECT 1 FROM records n WHERE n.kind='relation' AND n.identity=r.identity AND n.sequence<=? AND(n.sequence>r.sequence OR(n.sequence=r.sequence AND n.ordinal>r.ordinal)))"
            pending.extend(rr['version_id'] for rr in con.execute(sql,(cursor,endpoint_id,endpoint_id,cursor)))
        def visit(visit_id):
            nonlocal retained_bytes
            if visit_id in visits:return
            row=con.execute('SELECT payload FROM visit_states WHERE visit_id=? AND sequence<=? ORDER BY sequence DESC,ordinal DESC LIMIT 1',(visit_id,cursor)).fetchone()
            if row is None:raise ContractError('orphan visit in complete lineage')
            value=json.loads(row['payload']);visits[visit_id]=value;retained_bytes+=len(row['payload'])
            pending.append(value['start_geometry']);incident(visit_id)
            for event in con.execute("SELECT version_id FROM records WHERE kind='observation' AND sequence<=? AND json_extract(payload,'$.value.visit_id')=? ORDER BY sequence,ordinal",(cursor,visit_id)):
                pending.append(event['version_id'])
                if len(pending)>self.definition.payload_bytes_max//8:
                    raise DependencyUnavailable('capacity_unavailable: complete visit membership')
        while pending:
            if retained_bytes>self.definition.payload_bytes_max:
                raise DependencyUnavailable('capacity_unavailable: complete lineage bytes')
            vid=pending.pop()
            if vid in versions:continue
            obj,row=self._get(con,vid)
            if row['sequence']>cursor:raise ContractError('future member in requested lineage closure')
            versions[vid]=member_record(obj);retained_bytes+=len(row['payload'])
            if len(versions)>self.definition.hot_active_max*self.definition.parent_edges_max:
                raise DependencyUnavailable('capacity_unavailable: complete lineage closure')
            if isinstance(obj,ObjectRevision):
                pending.extend(obj.evidence_versions);pending.extend(obj.birth.anchors)
                if obj.mapping_version:pending.append(obj.mapping_version)
                for parent in obj.parent_versions:
                    parent_edges.add((parent,obj.version_id));pending.append(parent)
                if obj.object_id not in visited_owners:
                    visited_owners.add(obj.object_id)
                    for vr in con.execute('SELECT DISTINCT visit_id FROM visit_states WHERE object_id=? AND sequence<=? ORDER BY visit_id',(obj.object_id,cursor)):
                        visit(vr['visit_id'])
                    for metadata in con.execute("SELECT version_id FROM records WHERE kind IN ('alias','presentation') AND object_id=? AND sequence<=? ORDER BY sequence,ordinal",(obj.object_id,cursor)):
                        pending.append(metadata['version_id'])
            elif isinstance(obj,AnchorVersion):pending.extend(obj.evidence_versions)
            elif isinstance(obj,ObservationEvent):
                pending.append(obj.object_version);pending.extend(obj.evidence_versions);visit(obj.visit_id)
            elif isinstance(obj,(Alias,Presentation)):
                owner=self._latest(con,'object',obj.object_id,cursor)
                if owner is None:raise ContractError('orphan metadata owner')
                pending.append(owner['version_id'])
            elif isinstance(obj,RelationVersion):
                relations[obj.relation_id]=member_record(obj)
                if len(relations)>self.definition.hot_relations_max:
                    raise DependencyUnavailable('capacity_unavailable: complete relation closure')
                for endpoint in(obj.left,obj.right):
                    if endpoint.kind==EndpointKind.VISIT:visit(endpoint.id)
                    else:pending.append(endpoint.id)
                if obj.kind in ANCESTRY:parent_edges.add((obj.left.id,obj.right.id))
            incident(vid)
        value={'lineage_versions':[versions[k] for k in sorted(versions)],'lineage_visits':[visits[k] for k in sorted(visits)],
               'parent_edges':[list(edge) for edge in sorted(parent_edges)],'relations':[relations[k] for k in sorted(relations)]}
        if len(canonical(value))>self.definition.payload_bytes_max:raise DependencyUnavailable('capacity_unavailable: complete lineage bytes')
        return value

    def lineage_closure(self, version_ids, cut, *, cursor=None):
        _tuple(version_ids,str,unique=True)
        with self._connection() as con:
            value = self._lineage_closure(con,version_ids,self._cursor(con,cut,cursor))
        return _freeze(value)

    @staticmethod
    def _control_old(con, id, kind):
        row = con.execute('SELECT kind,payload FROM controls WHERE id=?', (id,)).fetchone()
        if row is None:
            return None
        if row['kind'] != kind:
            raise IntegrityError("control identity reused across types")
        return _freeze(json.loads(row['payload']))

    def _write_control(self, con, *, id, kind, value, at, expected_head):
        old = self._control_old(con, id, kind)
        if old is not None:
            if canonical(old) != canonical(value):
                raise IntegrityError("immutable cut/control changed")
            return old
        h = self._head(con)
        if expected_head != (None if h is None else h['hash']):
            raise ContractError("state changed before control publication")
        seq = 1 if h is None else h['sequence']+1
        known = max(at, at if h is None else h['known_at'])
        raw = canonical({'kind': kind, 'id': id, 'value': value})
        if len(raw) > self.definition.payload_bytes_max:
            raise DependencyUnavailable("capacity_unavailable: control payload")
        previous = None if h is None else h['hash']
        value_hash = self._journal_hash(seq, id, known, raw, previous)
        con.execute('INSERT INTO controls VALUES (?,?,?,?)', (id, kind, seq, canonical(value)))
        con.execute('INSERT INTO batches VALUES (?,?,?,?,?,?)',(seq,id,known,raw,previous,value_hash))
        self._stats['journal_records_written']+=1
        self._stats['journal_bytes_written']+=len(raw)
        return _freeze(value)

    def freeze_candidates(self, *, cut_id, at, instrument, expected_head):
        _name(cut_id, 'cut'); _time(at)
        if not isinstance(instrument, Instrument):
            raise ContractError("candidate denominator needs exact instrument")
        with self._connection(write=True) as con:
            old = self._control_old(con, cut_id, 'candidate_cut')
            if old is not None:
                if old['at'] != at or canonical(old['instrument']) != canonical(instrument):
                    raise IntegrityError("candidate ID reused at another cut/instrument")
                return old
            n = self._cursor(con, at)
            views = self._views(con, n, instrument)
            candidates, excluded = [], []
            for v in views:
                if v.available(at, self.definition.ttl_ns):
                    candidates.append(v.object.version_id)
                else:
                    reason = v.reason if v.dirty else ('ttl_expired' if self.definition.ttl_ns is not None and at >= v.born_at+self.definition.ttl_ns else v.object.existence.value + ':' + v.object.eligibility.value)
                    excluded.append({'object_version': v.object.version_id, 'reason': reason})
            closure = self._lineage_closure(con,tuple(v.object.version_id for v in views),n)
            value = {'id':cut_id,'at':at,'instrument':_pack(instrument),'definition':self.definition.version,
                     'history_cursor':n,'candidate_versions':candidates,'candidate_count':len(candidates),
                     'considered_count':len(views),'excluded':excluded,**closure,
                     'empty_population':not views,'unknown_support':any(v.dirty for v in views)}
            return self._write_control(con, id=cut_id, kind='candidate_cut', value=value, at=at, expected_head=expected_head)

    def candidate_cut(self, cut_id):
        _name(cut_id, 'cut')
        with self._connection() as con:
            result = self._control_old(con, cut_id, 'candidate_cut')
        if result is None:
            raise DependencyUnavailable('not_found: frozen candidate cut')
        return result

    def annotate_selection(self, *, annotation_id, cut_id, selected, rejected, expected_head):
        _name(annotation_id, 'selection'); _tuple(selected, str, unique=True); _tuple(rejected, str, unique=True)
        cut = self.candidate_cut(cut_id)
        if set(selected) & set(rejected) or set(selected) | set(rejected) != set(cut['candidate_versions']):
            raise ContractError("selection must retain complete selected/rejected denominator")
        value = {'id': annotation_id, 'cut_id': cut_id, 'selected': list(selected), 'rejected': list(rejected)}
        with self._connection(write=True) as con:
            return self._write_control(con, id=annotation_id, kind='selection', value=value, at=cut['at'], expected_head=expected_head)

    def bind_target(self, *, target_id, cut_id, object_version, geometry, horizon_end,
                    observation_process, expected_head):
        _name(target_id, 'target'); _name(object_version, 'v'); _name(observation_process); _time(horizon_end)
        if not isinstance(geometry, Geometry):
            raise ContractError("frozen target needs typed geometry")
        cut = self.candidate_cut(cut_id)
        if horizon_end <= cut['at'] or object_version not in cut['candidate_versions']:
            raise ContractError("target outside its original candidate denominator/horizon")
        obj = self.get_version(object_version)
        if not isinstance(obj, ObjectRevision) or obj.geometry != geometry:
            raise ContractError("target substituted another geometry version")
        value = {'id': target_id, 'cut_id': cut_id, 'cut': cut['at'], 'object_version': object_version,
                 'geometry': _pack(geometry), 'geometry_hash': geometry.version,
                 'horizon_end': horizon_end, 'observation_process': observation_process, 'unit': 'ticks'}
        with self._connection(write=True) as con:
            return self._write_control(con, id=target_id, kind='target', value=value, at=cut['at'], expected_head=expected_head)

    def target(self, target_id):
        _name(target_id, 'target')
        with self._connection() as con:
            value = self._control_old(con, target_id, 'target')
        if value is None:
            raise DependencyUnavailable('not_found: target binding')
        return value

    def project_action_aliases(self, *, projection_id, cut_id, policy_version, proposals, expected_head):
        _name(projection_id, 'actions'); _name(policy_version); _tuple(proposals, ActionProposal)
        if len({p.id for p in proposals}) != len(proposals):
            raise IntegrityError("duplicate action proposal identity")
        cut = self.candidate_cut(cut_id); groups = {}
        for p in proposals:
            if (p.object_version not in cut['candidate_versions'] or p.horizon_end <= cut['at']
                    or canonical(p.instrument) != canonical(cut['instrument'])):
                raise ContractError("action alias outside original cut/instrument/horizon")
            obj = self.get_version(p.object_version)
            with self._connection() as con:
                visit = con.execute('SELECT 1 FROM visit_states WHERE visit_id=? AND object_id=? AND sequence<=? LIMIT 1',(p.visit_id,obj.object_id,cut['history_cursor'])).fetchone()
            if visit is None:
                raise ContractError("action alias needs original known visit")
            key = content_hash((policy_version, p.canonical_idea_id, p.visit_id, p.side,
                                p.plan_definition, p.horizon_end, p.instrument))
            groups.setdefault(key, []).append(p.id)
        values = [{'key': key, 'members': sorted(members), 'representative': min(members),
                   'duplicate_members': sorted(members)[1:]} for key, members in sorted(groups.items())]
        result = {'id': projection_id, 'cut_id': cut_id, 'policy': policy_version,
                  'proposals': [_pack(p) for p in proposals], 'groups': values, 'unique_action_count': len(groups)}
        with self._connection(write=True) as con:
            return self._write_control(con, id=projection_id, kind='actions', value=result, at=cut['at'], expected_head=expected_head)

    def fallback(self, object_id, cut, *, policy='block'):
        _name(object_id,'o')
        if policy not in {'block','previous_valid'}:
            raise ContractError('explicit fallback policy required')
        with self._connection() as con:
            n = self._cursor(con,cut)
            current = self._object_view(con,object_id,n)
            if current is None:
                raise ContractError('known object required')
            if current.available(cut,self.definition.ttl_ns):
                return _freeze({'object_version':current.object.version_id,'fallback':False,'reason':'current_valid'})
            expired = (not current.object.birth.instrument.valid(cut) or
                       (self.definition.ttl_ns is not None and cut>=current.born_at+self.definition.ttl_ns))
            if policy=='block' or current.dirty or expired or current.object.existence in {Existence.EXPIRED,Existence.SUPERSEDED}:
                return _freeze({'object_version':None,'fallback':False,'reason':'blocked:'+current.reason})
            rows = con.execute("SELECT payload FROM records WHERE kind='object' AND identity=? AND sequence<=? AND revision<? ORDER BY revision DESC",(object_id,n,current.object.revision))
            for row in rows:
                obj = self._decode_record(row['payload'])
                ok,_ = self._support(con,obj,cursor=n)
                if ObjectView(obj,not ok,'prior',current.born_at).available(cut,self.definition.ttl_ns):
                    return _freeze({'object_version':obj.version_id,'fallback':True,'reason':'explicit_previous_valid',
                                    'invalid_latest':current.object.version_id,'policy':policy,'history_cursor':n,'cut':cut})
        return _freeze({'object_version':None,'fallback':False,'reason':'no_supported_prior_version'})

    def archive_expired(self, cut, *, expected_head):
        _time(cut)
        with self._connection(write=True) as con:
            n = self._cursor(con, cut)
            ids = [v.object.object_id for v in self._views(con, n)
                   if v.object.existence in TERMINAL or (self.definition.ttl_ns is not None and cut >= v.born_at+self.definition.ttl_ns)]
            key = 'archive:' + content_hash((self.definition.version, cut))
            value = {'id': key, 'at': cut, 'archived_ids': ids, 'history_deleted': False}
            result = self._write_control(con, id=key, kind='archive', value=value, at=cut, expected_head=expected_head)
        self._update_hot((),cut)
        return result

    def _projection_digest(self, con, cursor):
        h = hashlib.sha256()
        for table, query in (
                ('records', 'SELECT * FROM records WHERE sequence<=? ORDER BY sequence,ordinal,version_id'),
                ('support', 'SELECT * FROM object_states WHERE sequence<=? ORDER BY sequence,object_id'),
                ('visits', 'SELECT * FROM visit_states WHERE sequence<=? ORDER BY sequence,ordinal,visit_id'),
                ('controls', 'SELECT * FROM controls WHERE sequence<=? ORDER BY sequence')):
            h.update(table.encode())
            for row in con.execute(query, (cursor,)):
                values = [v.decode('utf8') if isinstance(v, bytes) else v for v in row]
                h.update(canonical(values))
        return h.hexdigest()

    def checkpoint(self):
        with self._connection() as con:
            head = self._head(con); n = 0 if head is None else head['sequence']
            value = {'definition': self.definition.version, 'cursor': n,
                     'head': None if head is None else head['hash'], 'pending_free': True,
                     'projection_digest':self._projection_digest(con,n),'indexes_digest':self._indexes_digest(con)}
        return {**value, 'content_hash': content_hash(value)}

    @classmethod
    def restore(cls, path, *, definition, checkpoint):
        if not isinstance(checkpoint, dict) or set(checkpoint) != {'definition','cursor','head','pending_free','projection_digest','indexes_digest','content_hash'}:
            raise IntegrityError("checkpoint schema changed")
        body = {k: v for k, v in checkpoint.items() if k != 'content_hash'}
        if (checkpoint['content_hash'] != content_hash(body) or checkpoint['pending_free'] is not True
                or checkpoint['definition'] != definition.version or type(checkpoint['cursor']) is not int or checkpoint['cursor'] < 0):
            raise IntegrityError("checkpoint integrity/configuration/atomicity mismatch")
        result = cls(path,definition=definition,_checkpoint_cursor=checkpoint['cursor'])
        with result._connection() as con:
            n = checkpoint['cursor']; head = result._head(con)
            if n > (0 if head is None else head['sequence']):
                raise IntegrityError("checkpoint cursor beyond retained journal")
            prefix = con.execute('SELECT hash FROM batches WHERE sequence=?', (n,)).fetchone() if n else None
            if (None if prefix is None else prefix['hash']) != checkpoint['head'] or result._projection_digest(con, n) != checkpoint['projection_digest']:
                raise IntegrityError("checkpoint does not match exact durable prefix")
            if result._verified_prefix_digest != checkpoint['indexes_digest']:
                raise IntegrityError('checkpoint index state differs from exact durable prefix')
            # The integrity fold verified every retained index delta once. No
            # prefix support derivation occurs. Suffix records are visited once
            # for replay accounting; current hot state was hydrated once above.
            for row in con.execute('SELECT payload FROM batches WHERE sequence>? ORDER BY sequence',(n,)):
                payload = json.loads(row['payload'])
                result._stats['suffix_batches_replayed'] += 1
                result._stats['suffix_members_replayed'] += payload.get('input',{}).get('member_count',0)
        return result

    def lineage_payload(self, cut, *, instrument, cut_id=None):
        """One immutable instrument-specific snapshot at one completed cursor.

        Every complete output is byte-bounded; paged history APIs remain the
        archive interface when a single published payload cannot fit.
        """
        if not isinstance(instrument,Instrument):
            raise ContractError('exact instrument required')
        with self._connection() as con:
            cursor = self._cursor(con,cut)
            objects = self._active(con,cursor,cut,instrument)
            candidate = None
            if cut_id is not None:
                _name(cut_id,'cut')
                row = con.execute("SELECT sequence FROM controls WHERE id=? AND kind='candidate_cut'",(cut_id,)).fetchone()
                candidate = self._control_old(con,cut_id,'candidate_cut')
                if (candidate is None or row['sequence']>cursor or candidate['at']!=cut
                        or canonical(candidate['instrument'])!=canonical(instrument)
                        or candidate['history_cursor']>cursor):
                    raise ContractError('candidate cut is future or incompatible with snapshot')
            object_ids = {r['identity'] for r in con.execute("SELECT DISTINCT identity FROM records WHERE kind='object' AND sequence<=? AND json_extract(payload,'$.value.birth.instrument')=json(?) LIMIT ?",(cursor,canonical(instrument).decode(),self.definition.hot_active_max+1))}
            if len(object_ids)>self.definition.hot_active_max:
                raise DependencyUnavailable('capacity_unavailable: complete instrument history')
            observations,visits = [],[]
            after_event=None
            while True:
                page=self._events(con,cursor,after_event=after_event,limit=self.definition.archive_page_size,instrument=instrument)
                if not page:break
                observations.extend(page);after_event=page[-1].event_id
                if len(canonical(observations))>self.definition.payload_bytes_max:
                    raise DependencyUnavailable('capacity_unavailable: complete observation payload')
            for oid in sorted(object_ids):
                after = ('','')
                while True:
                    page = self._visit_heads(con,object_id=oid,cursor=cursor,after=after,limit=self.definition.archive_page_size)
                    if not page: break
                    visits.extend(page); after = (page[-1]['object_id'],page[-1]['visit_id'])
                    if len(canonical(visits))>self.definition.payload_bytes_max:
                        raise DependencyUnavailable('capacity_unavailable: complete visit payload')
            closure = self._lineage_closure(con,tuple(o.version_id for o in objects),cursor)
            targets,actions = [],[]
            for row in con.execute("SELECT kind,payload FROM controls WHERE kind IN ('target','actions') AND sequence<=? ORDER BY id",(cursor,)):
                value = json.loads(row['payload'])
                owner_cut = self._control_old(con,value['cut_id'],'candidate_cut')
                if canonical(owner_cut['instrument'])==canonical(instrument):
                    (targets if row['kind']=='target' else actions).append(value)
            known = con.execute('SELECT known_at FROM batches WHERE sequence=?',(cursor,)).fetchone()
            value = {'objects':[_pack(o) for o in objects],'versions':closure['lineage_versions'],
                     'geometry':[_pack(o.geometry) for o in objects],'observations':[_pack(o) for o in observations],
                     'visits':visits,'relations':closure['relations'],'candidate_cut':candidate,
                     'targets':targets,'action_aliases':actions,'known_time':None if known is None else known['known_at'],
                     'history_cursor':cursor}
            raw = canonical(value)
            if len(raw)>self.definition.payload_bytes_max:
                raise DependencyUnavailable('capacity_unavailable: complete lineage payload')
            return raw

    @staticmethod
    def engineering_scope():
        return _freeze({'native_mapping_certified':False,'mapping_formula_certified':False,
                        'visual_replay_button_certifies_asof':False,'calibrated_confidence':False,
                        'phase_P5_complete':False,'market_or_economic_evidence':False})
