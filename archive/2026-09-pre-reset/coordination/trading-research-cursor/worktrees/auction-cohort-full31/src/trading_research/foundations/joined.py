"""Bounded F07 materialized field eligibility and explicit joint support.

Build work is deliberately visible. Queries bisect immutable intervals and do
not scan original observations; the separate literal reference does full scans.
"""
from __future__ import annotations

from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass, replace
from fractions import Fraction
import json
from types import MappingProxyType

from trading_research.errors import ContractError
from trading_research.foundations.quality import (
    OPERATIONS, FieldFact, FieldKey, FieldRef, FieldSupport, OperationPolicy, QualityIncident,
    QualityRecovery, SourceLiveness, _nonnegative, _text, incident_interval,
    missing_support, validate_recovery,
)
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class EligibilityInterval:
    start: int
    end: int | None
    support: FieldSupport

    def __post_init__(self):
        timestamp(self.start)
        if self.end is not None:
            timestamp(self.end)
            if self.end <= self.start:
                raise ContractError('eligibility interval must be forward and nonempty')
        if not isinstance(self.support, FieldSupport) or self.support.cut != self.start:
            raise ContractError('interval support must describe its original start')


@dataclass(frozen=True)
class EligibilityCheckpoint:
    configuration_version: str
    events: tuple
    state_digest: str
    max_events: int
    max_intervals: int

    def __post_init__(self):
        if not isinstance(self.events, tuple) or self.state_digest != digest((self.configuration_version, self.events)):
            raise ContractError('checkpoint content does not match its immutable identity')


@dataclass(frozen=True)
class _EligibilityConfiguration:
    bindings: tuple[tuple[FieldKey, OperationPolicy], ...]
    max_events: int
    max_intervals: int
    version: str


class EligibilityIndex:
    def __init__(self, bindings: tuple[tuple[FieldKey, OperationPolicy], ...], *,
                 max_events: int = 4096, max_intervals: int = 16384):
        if (not isinstance(bindings, tuple) or not bindings
                or any(not isinstance(row, tuple) or len(row) != 2
                       or not isinstance(row[0], FieldKey) or not isinstance(row[1], OperationPolicy) for row in bindings)
                or any(type(v) is not int or v <= 0 for v in (max_events, max_intervals))):
            raise ContractError('bounded typed field/policy bindings required')
        by_key = {(key, policy.id): policy for key, policy in bindings}
        if len(by_key) != len(bindings):
            raise ContractError('duplicate field/policy binding')
        ordered = tuple(sorted(bindings, key=lambda row: (row[0].version, row[1].id)))
        self._configuration = _EligibilityConfiguration(ordered, max_events, max_intervals,
                                                       digest((ordered, max_events, max_intervals)))
        self._policies = MappingProxyType(by_key)
        self._keys = frozenset(key for key, _ in bindings)
        self._events = {}
        self._timelines = {key: () for key in by_key}
        self._starts = {key: () for key in by_key}
        self.stats = Counter(build_candidate_checks=0, build_intervals=0, rebuilt_fields=0,
                             query_interval_lookups=0, query_source_candidate_scans=0)

    def __setattr__(self, name, value):
        if name == '_configuration' and name in self.__dict__:
            raise AttributeError('eligibility configuration is immutable after construction')
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name == '_configuration':
            raise AttributeError('eligibility configuration cannot be removed')
        object.__delattr__(self, name)

    @property
    def bindings(self):
        return self._configuration.bindings

    @property
    def max_events(self):
        return self._configuration.max_events

    @property
    def max_intervals(self):
        return self._configuration.max_intervals

    @property
    def configuration_version(self):
        return self._configuration.version

    @property
    def events(self):
        return tuple(self._events.values())

    def append(self, event):
        return bool(self.extend((event,)))

    def extend(self, events: tuple):
        """Validate and build a proposed state before making any part visible."""
        if not isinstance(events, tuple):
            raise ContractError('batch admission must be immutable')
        proposed = dict(self._events)
        dirty = set()
        added = 0
        for event in events:
            if not isinstance(event, (FieldFact, SourceLiveness, QualityIncident, QualityRecovery)):
                raise ContractError('typed quality event required')
            old = proposed.get(event.id)
            if old is not None:
                if old != event:
                    raise ContractError('quality event ID reused with changed content')
                continue
            if len(proposed) >= self.max_events:
                raise ContractError('bounded quality event capacity exceeded; no history was evicted')
            if isinstance(event, FieldFact):
                if event.key not in self._keys:
                    raise ContractError('fact has no registered field/definition policy')
                if event.content_origin_id is not None:
                    origin = proposed.get(event.content_origin_id)
                    if (not isinstance(origin, FieldFact) or origin.content_origin_id is not None
                            or origin.known_at > event.known_at or origin.source != event.source
                            or origin.economic_signature != event.economic_signature
                            or origin.clocks.source_version != event.clocks.source_version
                            or origin.clocks.event_at != event.clocks.event_at
                            or origin.clocks.provider_received_at != event.clocks.provider_received_at
                            or origin.clocks.published_at != event.clocks.published_at):
                        raise ContractError('copied state does not match an already admitted economic origin')
                for other in proposed.values():
                    if (isinstance(other, FieldFact) and other.key == event.key
                            and (other.observed_at, other.revision)
                            == (event.observed_at, event.revision)
                            and other.economic_signature != event.economic_signature):
                        raise ContractError('conflicting overlapping field acquisitions')
                dirty.add(event.key)
            elif isinstance(event, QualityIncident):
                if not event.fields.issubset(self._keys):
                    raise ContractError('incident has unregistered field/definition scope')
                dirty.update(event.fields)
            elif isinstance(event, QualityRecovery):
                incident = proposed.get(event.incident_id)
                if not isinstance(incident, QualityIncident):
                    raise ContractError('recovery has no admitted incident')
                validate_recovery(event, incident)
                for old_recovery in proposed.values():
                    if (isinstance(old_recovery, QualityRecovery) and old_recovery.incident_id == event.incident_id
                            and old_recovery.fields.intersection(event.fields)):
                        raise ContractError('incident field already has immutable recovery evidence')
                dirty.update(event.fields)
            else:
                if event.instrument not in {key.instrument for key in self._keys}:
                    raise ContractError('liveness evidence is outside the registered instrument scope')
                for other in proposed.values():
                    if (isinstance(other, SourceLiveness)
                            and (other.source, other.instrument, other.observed_at, other.known_at)
                            == (event.source, event.instrument, event.observed_at, event.known_at)
                            and (other.healthy, other.stream_kind) != (event.healthy, event.stream_kind)):
                        raise ContractError('conflicting source-liveness evidence')
                dirty.update(f.key for f in proposed.values() if isinstance(f, FieldFact)
                             and f.source == event.source and f.key.instrument == event.instrument)
            proposed[event.id] = event
            added += 1
        if not added:
            return 0
        timelines = dict(self._timelines)
        # Newly appended facts may establish the scope of a heartbeat admitted
        # earlier in this same batch. Their own dirty field includes that evidence.
        for key, policy in self.bindings:
            if key in dirty:
                timelines[(key, policy.id)] = self._build(key, policy, tuple(proposed.values()))
        if sum(len(rows) for rows in timelines.values()) > self.max_intervals:
            raise ContractError('bounded eligibility interval capacity exceeded; no partial state published')
        starts = {key: tuple(row.start for row in rows) for key, rows in timelines.items()}
        self._events, self._timelines, self._starts = proposed, timelines, starts
        self.stats['rebuilt_fields'] += len(dirty)
        return added

    def _build(self, key, policy, events):
        facts = tuple(e for e in events if isinstance(e, FieldFact) and e.key == key)
        sources = {f.source for f in facts}
        pulses = tuple(e for e in events if isinstance(e, SourceLiveness)
                       and e.instrument == key.instrument and e.source in sources)
        incidents = tuple(e for e in events if isinstance(e, QualityIncident)
                          and key in e.fields and policy.operation in e.operations)
        incident_ids = {e.id for e in incidents}
        recoveries = tuple(e for e in events if isinstance(e, QualityRecovery)
                           and key in e.fields and e.incident_id in incident_ids)
        boundaries = set()
        for fact in facts:
            boundaries.update((fact.known_at, max(fact.known_at, fact.observed_at)))
            # Upper age = cut-observation+uncertainty. Integer TTL is inclusive.
            boundaries.add(timestamp(fact.observed_at - fact.clocks.clock_uncertainty_ns + policy.max_age_ns + 1))
            if fact.clocks.valid_from is not None:
                boundaries.add(fact.clocks.valid_from)
            if fact.clocks.valid_until is not None:
                boundaries.add(fact.clocks.valid_until)
        for pulse in pulses:
            boundaries.add(pulse.known_at)
            if policy.max_source_silence_ns is not None:
                boundaries.add(timestamp(pulse.observed_at + policy.max_source_silence_ns + 1))
        for incident in incidents:
            boundaries.update((incident.known_at, max(incident.known_at, incident.affected_from)))
            if incident.affected_until is not None:
                boundaries.add(incident.affected_until)
        boundaries.update(r.known_at for r in recoveries)
        points = sorted(boundaries)
        rows = []
        for n, at in enumerate(points):
            support = self._resolve_build(key, policy, at, facts, pulses, incidents, recoveries)
            rows.append(EligibilityInterval(at, points[n + 1] if n + 1 < len(points) else None, support))
            self.stats['build_intervals'] += 1
            if len(rows) > self.max_intervals:
                raise ContractError('one field exceeds bounded eligibility intervals')
        return tuple(rows)

    def _resolve_build(self, key, policy, cut, facts, pulses, incidents, recoveries):
        available = []
        for fact in facts:
            self.stats['build_candidate_checks'] += 1
            if fact.known_at <= cut and fact.observed_at <= cut:
                available.append(fact)
        active_incidents = []
        for incident in incidents:
            matching = tuple(r for r in recoveries if r.incident_id == incident.id)
            span = incident_interval(incident, matching, field=key, cut=cut)
            if span is not None and span[0] <= cut and (span[1] is None or cut < span[1]):
                active_incidents.append(incident)
        ids = tuple(sorted(i.id for i in active_incidents))
        if not available:
            return missing_support(key, policy, cut, incident_ids=ids)
        # Receipt governs visibility only. It cannot promote an older revision
        # or a copied original above an already visible invalidating revision.
        newest_order = max((f.observed_at, f.revision) for f in available)
        aliases = tuple(sorted((f for f in available if (f.observed_at, f.revision) == newest_order), key=lambda f: f.id))
        fact = min(aliases, key=lambda f: (f.content_origin_id is not None, f.id))
        actual = sorted((f for f in available if f.content_origin_id is None),
                        key=lambda f: (f.observed_at, f.revision, f.id))
        changed_at, previous = None, None
        for row in actual:
            if row.eligible and not row.estimated:
                if previous != row.payload_json:
                    changed_at = row.observed_at
                previous = row.payload_json
        source_at = max((f.observed_at for f in actual), default=None)
        receipts = [f.clocks.received_at for f in available if f.clocks.received_at is not None]
        receipt = max(receipts) if receipts else None
        live = [p for p in pulses if p.source == fact.source and p.known_at <= cut and p.observed_at <= cut]
        pulse = max(live, key=lambda p: (p.observed_at, p.known_at, p.id)) if live else None
        state, reasons = ('estimated' if fact.estimated else 'observed'), []
        if policy.operation not in fact.available_operations:
            state, reasons = 'ineligible', ['source_capability_missing']
        elif not fact.eligible:
            state, reasons = 'invalid', ['source_invalid']
        elif not fact.clocks.available(cut):
            state, reasons = 'ineligible', ['definition_or_source_validity']
        elif fact.estimated and not policy.allow_estimated:
            state, reasons = 'ineligible', ['estimated_value_not_admitted']
        elif any(i.blocks(policy.operation) for i in active_incidents):
            state, reasons = 'invalid', sorted({i.kind for i in active_incidents if i.blocks(policy.operation)})
        elif fact.clocks.clock_uncertainty_ns > policy.max_clock_uncertainty_ns:
            state, reasons = 'ineligible', ['clock_uncertainty_exceeded']
        elif cut - fact.observed_at + fact.clocks.clock_uncertainty_ns > policy.max_age_ns:
            state, reasons = 'stale', ['conservative_age_exceeded']
        elif policy.max_source_silence_ns is not None:
            if pulse is None:
                state, reasons = 'missing', ['liveness_missing']
            elif not pulse.healthy:
                state, reasons = 'invalid', ['source_gap']
            elif cut - pulse.observed_at > policy.max_source_silence_ns:
                state, reasons = 'stale', ['source_silent']
        return FieldSupport(key, policy.operation, policy.version, cut, state, tuple(reasons), fact.id,
                            fact.content_origin_id or fact.id,
                            tuple((f.id, f.clocks.source_version) for f in aliases),
                            fact.payload_json if state in {'observed', 'estimated'} else None,
                            fact.observed_at, source_at, changed_at, receipt,
                            pulse.observed_at if pulse else None, pulse.id if pulse else None,
                            fact.clocks.clock_uncertainty_ns, ids)

    def field(self, key: FieldKey, policy_id: str, *, cut: int):
        timestamp(cut)
        binding = (key, policy_id)
        if binding not in self._policies:
            raise ContractError('unregistered field or operation policy')
        self.stats['query_interval_lookups'] += 1
        index = bisect_right(self._starts[binding], cut) - 1
        if index < 0:
            return missing_support(key, self._policies[binding], cut)
        interval = self._timelines[binding][index]
        # All status-changing time boundaries were materialized during build.
        # Replacing the cut derives ages from retained clocks, not from sources.
        return replace(interval.support, cut=cut)

    def intervals(self, key, policy_id):
        if (key, policy_id) not in self._policies:
            raise ContractError('unregistered field or policy')
        return self._timelines[(key, policy_id)]

    def snapshot(self, requests, *, cut, joint_policy, optional=frozenset(), movement=None):
        if (not isinstance(requests, tuple) or not requests
                or any(not isinstance(r, tuple) or len(r) != 2 for r in requests)):
            raise ContractError('joined requests must be immutable field/policy pairs')
        supports = tuple(self.field(key, policy_id, cut=cut) for key, policy_id in requests)
        return joint_snapshot(supports, joint_policy=joint_policy, optional=optional, movement=movement)

    def checkpoint(self):
        def order(event):
            rank = (2 if event.content_origin_id else 0) if isinstance(event, FieldFact) else (3 if isinstance(event, QualityRecovery) else 1)
            return event.known_at, rank, event.id
        events = tuple(sorted(self._events.values(), key=order))
        return EligibilityCheckpoint(self.configuration_version, events,
                                     digest((self.configuration_version, events)), self.max_events, self.max_intervals)

    @classmethod
    def restore(cls, checkpoint, *, bindings):
        if not isinstance(checkpoint, EligibilityCheckpoint):
            raise ContractError('typed immutable eligibility checkpoint required')
        result = cls(bindings, max_events=checkpoint.max_events, max_intervals=checkpoint.max_intervals)
        if result.configuration_version != checkpoint.configuration_version:
            raise ContractError('checkpoint policy/definition configuration changed')
        if checkpoint.state_digest != digest((checkpoint.configuration_version, checkpoint.events)):
            raise ContractError('checkpoint input identity changed')
        result.extend(checkpoint.events)
        return result


@dataclass(frozen=True)
class JointPolicy:
    id: str
    max_observation_span_ns: int
    max_movement_ticks: int | None = None
    reference_instrument: str | None = None

    def __post_init__(self):
        _text(self.id, 'joint policy'); _nonnegative(self.max_observation_span_ns, 'joint observation span')
        if self.max_movement_ticks is not None:
            _nonnegative(self.max_movement_ticks, 'movement limit'); _text(self.reference_instrument, 'movement reference')
        elif self.reference_instrument is not None:
            raise ContractError('reference movement identity needs an explicit movement limit')

    @property
    def version(self):
        return digest(self)


@dataclass(frozen=True)
class JointMovementEvidence:
    id: str
    instrument: str
    start: int
    end: int
    known_at: int
    complete: bool
    min_ticks: int
    max_ticks: int
    source_version: str

    def __post_init__(self):
        for name in ('id', 'instrument', 'source_version'):
            _text(getattr(self, name), name)
        for at in (self.start, self.end, self.known_at):
            timestamp(at)
        if (self.start >= self.end or self.end > self.known_at or type(self.complete) is not bool
                or type(self.min_ticks) is not int or type(self.max_ticks) is not int or self.min_ticks > self.max_ticks):
            raise ContractError('joint movement needs exact prior interval, bounds and completeness evidence')


@dataclass(frozen=True)
class JoinedSnapshot:
    cut: int
    operation: str
    joint_policy_version: str
    fields: tuple[FieldSupport, ...]
    optional_omissions: tuple[FieldKey, ...]
    supported: bool
    reasons: tuple[str, ...]
    observation_span_ns: int | None
    movement_id: str | None

    def __post_init__(self):
        timestamp(self.cut); _text(self.joint_policy_version, 'joint policy version')
        if (type(self.operation) is not str or self.operation not in OPERATIONS
                or not isinstance(self.fields, tuple) or not self.fields
                or any(not isinstance(f, FieldSupport) for f in self.fields)
                or len({f.key for f in self.fields}) != len(self.fields)
                or any((f.cut, f.operation) != (self.cut, self.operation) for f in self.fields)
                or type(self.supported) is not bool
                or not isinstance(self.optional_omissions, tuple)
                or any(not isinstance(k, FieldKey) for k in self.optional_omissions)
                or len(set(self.optional_omissions)) != len(self.optional_omissions)
                or not set(self.optional_omissions).issubset(f.key for f in self.fields if not f.admitted)
                or not isinstance(self.reasons, tuple)
                or any(type(reason) is not str or not reason for reason in self.reasons)
                or len(set(self.reasons)) != len(self.reasons)):
            raise ContractError('joined snapshot requires immutable coherent same-cut field support')
        if self.movement_id is not None:
            _text(self.movement_id, 'movement evidence')
        admitted = tuple(f for f in self.fields if f.admitted)
        expected_span = (max(f.observed_at + f.clock_uncertainty_ns for f in admitted)
                         - min(f.observed_at - f.clock_uncertainty_ns for f in admitted)) if admitted else None
        if self.observation_span_ns is not None:
            _nonnegative(self.observation_span_ns, 'observation span')
        if self.observation_span_ns != expected_span:
            raise ContractError('joined observation span disagrees with its field clocks')
        if (self.supported != (not self.reasons)
                or (self.supported and (not admitted or any(not f.admitted and f.key not in self.optional_omissions
                                                           for f in self.fields)))):
            raise ContractError('joined admission disagrees with its evidence and rejection reasons')

    @property
    def version_vector(self):
        return tuple(sorted((f.version_vector_entry for f in self.fields), key=lambda row: row[0]))

    @property
    def values(self):
        return tuple((f.key, f.payload_json) for f in self.fields if f.admitted)


def joint_snapshot(supports, *, joint_policy, optional=frozenset(), movement=None):
    if (not isinstance(supports, tuple) or not supports or any(not isinstance(f, FieldSupport) for f in supports)
            or not isinstance(joint_policy, JointPolicy) or not isinstance(optional, frozenset)
            or not optional.issubset(f.key for f in supports)
            or len({f.key for f in supports}) != len(supports)
            or len({(f.cut, f.operation) for f in supports}) != 1
            or (movement is not None and not isinstance(movement, JointMovementEvidence))):
        raise ContractError('joint snapshot requires unique same-cut/operation fields and explicit optionality')
    cut, operation = supports[0].cut, supports[0].operation
    available = tuple(f for f in supports if f.admitted)
    omissions = tuple(f.key for f in supports if f.key in optional and not f.admitted)
    reasons = []
    if any(not f.admitted and f.key not in optional for f in supports):
        reasons.append('required_field_unavailable')
    if not available:
        reasons.append('no_admitted_fields')
    span = None
    if available:
        first = min(f.observed_at - f.clock_uncertainty_ns for f in available)
        last = max(f.observed_at + f.clock_uncertainty_ns for f in available)
        span = last - first
        if span > joint_policy.max_observation_span_ns:
            reasons.append('asynchronous_support')
        if joint_policy.max_movement_ticks is not None:
            if (movement is None or not movement.complete or movement.known_at > cut
                    or movement.instrument != joint_policy.reference_instrument
                    or movement.start > first or movement.end < cut):
                reasons.append('movement_support_missing')
            elif movement.max_ticks - movement.min_ticks > joint_policy.max_movement_ticks:
                reasons.append('movement_limit_exceeded')
    return JoinedSnapshot(cut, operation, joint_policy.version, supports, omissions, not reasons,
                          tuple(reasons), span, movement.id if movement is not None and movement.known_at <= cut else None)


@dataclass(frozen=True)
class UniverseMember:
    instrument: str
    definition_version: str
    asset: str
    chain: str
    expiry: str
    known_at: int
    active_from: int
    active_until: int | None
    dte: int
    evidence_id: str

    def __post_init__(self):
        for name in ('instrument', 'definition_version', 'asset', 'chain', 'expiry', 'evidence_id'):
            _text(getattr(self, name), name)
        timestamp(self.known_at); timestamp(self.active_from); _nonnegative(self.dte, 'DTE')
        if self.active_until is not None:
            timestamp(self.active_until)
            if self.active_until <= self.active_from:
                raise ContractError('universe membership has invalid effective lifetime')


@dataclass(frozen=True)
class CoverageFieldRole:
    """Explicit measured field and operation used by an OI coverage contract."""
    field: FieldRef
    unit: str
    operation: str

    def __post_init__(self):
        _text(self.unit, 'coverage field unit')
        if (not isinstance(self.field, FieldRef) or type(self.operation) is not str
                or self.operation not in OPERATIONS):
            raise ContractError('coverage role requires an explicit field and operation')

    def matches(self, support):
        return (support.key.ref == self.field and support.key.unit == self.unit
                and support.operation == self.operation)


@dataclass(frozen=True)
class OICoverageContract:
    id: str
    oi_role: CoverageFieldRole
    required_quote_components: tuple[CoverageFieldRole, ...]

    def __post_init__(self):
        _text(self.id, 'OI coverage contract')
        if (not isinstance(self.oi_role, CoverageFieldRole) or self.oi_role.unit != 'contracts'
                or not isinstance(self.required_quote_components, tuple) or not self.required_quote_components
                or any(not isinstance(role, CoverageFieldRole) for role in self.required_quote_components)):
            raise ContractError('coverage needs an explicit contract-unit OI role and immutable required quote components')
        refs = tuple(role.field for role in self.required_quote_components)
        if len(set(refs)) != len(refs) or self.oi_role.field in refs:
            raise ContractError('OI and quote component roles must be distinct and unique')

    @property
    def version(self):
        return digest(self)


@dataclass(frozen=True)
class OICoverage:
    universe_version: str
    coverage_contract_version: str
    cut: int
    eligible_contract_ids: tuple[str, ...]
    quoted_contract_ids: tuple[str, ...]
    missing_quote_ids: tuple[str, ...]
    known_oi_contract_count: int
    missing_oi_contract_count: int
    quoted_known_oi: int
    total_reported_known_oi: int
    observed_oi_quote_fraction: Fraction | None
    state: str
    reason: str
    outside_universe_ids: tuple[str, ...]
    missing_quote_fields: tuple[tuple[str, FieldRef], ...]

    @property
    def true_total_exposure_fraction(self):
        return None


def observed_oi_coverage(universe, *, contract, oi_fields, quote_fields, cut, universe_version, max_dte=None):
    """A supplied PIT universe is mandatory; observed fields cannot invent it."""
    timestamp(cut); _text(universe_version, 'universe version')
    if (not isinstance(contract, OICoverageContract)
            or not isinstance(universe, tuple) or any(not isinstance(m, UniverseMember) for m in universe)
            or not isinstance(oi_fields, tuple) or not isinstance(quote_fields, tuple)):
        raise ContractError('coverage needs immutable supplied universe and joined field evidence')
    if max_dte is not None:
        _nonnegative(max_dte, 'scope maximum DTE')
    members = {}
    for member in universe:
        if member.known_at > cut or member.active_from > cut or (member.active_until is not None and cut >= member.active_until):
            continue
        if max_dte is not None and member.dte > max_dte:
            continue
        prior = members.get(member.instrument)
        if prior is not None and prior != member:
            raise ContractError('conflicting PIT membership/definition for one instrument')
        members[member.instrument] = member
    oi, components, outside, seen = {}, {}, set(), {}
    for kind, fields in (('oi', oi_fields), ('quote', quote_fields)):
        for field in fields:
            if not isinstance(field, FieldSupport) or field.cut != cut:
                raise ContractError('coverage must use exact same-cut joined fields')
            roles = (contract.oi_role,) if kind == 'oi' else contract.required_quote_components
            if not any(role.matches(field) for role in roles):
                raise ContractError('field does not satisfy the explicit OI or quote component/operation role')
            prior = seen.get((kind, field.key))
            if prior is not None and prior != field:
                raise ContractError('conflicting joined evidence for one coverage field')
            seen[(kind, field.key)] = field
            member = members.get(field.key.instrument)
            if member is None:
                outside.add(field.key.instrument)
                continue
            if (field.key.definition_version != member.definition_version or field.key.asset != member.asset
                    or field.key.chain != member.chain or field.key.expiry != member.expiry):
                raise ContractError('quote/OI identity disagrees with PIT payoff/definition membership')
            if not field.admitted or field.state != 'observed':
                continue
            if kind == 'quote':
                components.setdefault(member.instrument, set()).add(field.key.ref)
            else:
                value = json.loads(field.payload_json)
                if type(value) is not int or value < 0:
                    raise ContractError('reported OI must be an exact nonnegative count')
                previous = oi.get(member.instrument)
                if previous is not None and previous != value:
                    raise ContractError('conflicting joined OI cannot be added or arbitrarily selected')
                oi[member.instrument] = value
    required_refs = frozenset(role.field for role in contract.required_quote_components)
    quoted = {instrument for instrument, available in components.items() if required_refs.issubset(available)}
    ids = tuple(sorted(members))
    missing = tuple(sorted(set(members) - quoted))
    missing_fields = tuple((instrument, ref) for instrument in ids
                           for ref in sorted(required_refs - components.get(instrument, set())))
    total = sum(oi.values()); numerator = sum(value for key, value in oi.items() if key in quoted)
    return OICoverage(universe_version, contract.version, cut, ids, tuple(sorted(quoted)), missing,
                      len(oi), len(members) - len(oi), numerator, total,
                      Fraction(numerator, total) if total else None,
                      'ineligible' if not ids else 'missing' if missing else 'observed',
                      'no_contract_in_declared_scope' if not ids else 'partial_quote_coverage' if missing else 'reported_known_oi_support',
                      tuple(sorted(outside)), missing_fields)
