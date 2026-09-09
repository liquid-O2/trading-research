"""Finite F06 field quality contracts, independent clocks and recovery support.

These contracts consume explicit source/definition evidence. They do not certify
an acquired cohort, infer a missing market stream, or fit liveness thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from trading_research.errors import ContractError
from trading_research.foundations.contracts import _json_payload
from trading_research.foundations.graph import Graph
from trading_research.foundations.time import Clocks, timestamp
from trading_research.operations.artifacts import digest

OPERATIONS = frozenset({'valuation', 'signing', 'forecasting', 'execution'})
SEVERITIES = frozenset({'informational', 'dependent-feature-block', 'execution-block'})


def _text(value, name):
    if type(value) is not str or not value:
        raise ContractError(f'{name} needs a nonempty immutable identity')


def _nonnegative(value, name):
    if type(value) is not int or value < 0:
        raise ContractError(f'{name} needs an exact nonnegative integer')


def _operations(value):
    if not isinstance(value, frozenset) or not value.issubset(OPERATIONS):
        raise ContractError('operations must be an immutable registered set')


@dataclass(frozen=True, order=True)
class FieldRef:
    producer: str
    field: str

    def __post_init__(self):
        _text(self.producer, 'producer'); _text(self.field, 'field')


@dataclass(frozen=True, order=True)
class FieldKey:
    producer: str
    field: str
    instrument: str
    definition_version: str
    unit: str
    asset: str
    chain: str | None = None
    expiry: str | None = None
    moneyness: str | None = None

    def __post_init__(self):
        for name in ('producer', 'field', 'instrument', 'definition_version', 'unit', 'asset'):
            _text(getattr(self, name), name)
        for name in ('chain', 'expiry', 'moneyness'):
            if getattr(self, name) is not None:
                _text(getattr(self, name), name)

    @property
    def ref(self):
        return FieldRef(self.producer, self.field)

    @property
    def version(self):
        return digest(self)


@dataclass(frozen=True)
class FieldFact:
    id: str
    key: FieldKey
    source: str
    observed_at: int
    clocks: Clocks
    payload_json: bytes
    revision: int = 0
    available_operations: frozenset[str] = frozenset()
    content_origin_id: str | None = None
    eligible: bool = True
    estimated: bool = False

    def __post_init__(self):
        _text(self.id, 'fact ID'); _text(self.source, 'source')
        if not isinstance(self.key, FieldKey) or not isinstance(self.clocks, Clocks):
            raise ContractError('typed field and clock contracts required')
        timestamp(self.observed_at); _nonnegative(self.revision, 'revision')
        _json_payload(self.payload_json); _operations(self.available_operations)
        if type(self.eligible) is not bool or type(self.estimated) is not bool:
            raise ContractError('eligibility and estimation status must be explicit booleans')
        if self.content_origin_id is not None:
            _text(self.content_origin_id, 'content origin')
            if self.content_origin_id == self.id:
                raise ContractError('a copied fact cannot be its own origin')

    @property
    def known_at(self):
        return self.clocks.known_at

    @property
    def economic_signature(self):
        # Acquisition IDs/source versions stay in lineage; they are not amounts
        # to add when the same field/time is acquired more than once.
        return (self.key, self.observed_at, self.payload_json, self.revision,
                self.available_operations, self.eligible, self.estimated,
                self.clocks.clock_uncertainty_ns, self.clocks.valid_from,
                self.clocks.valid_until)


@dataclass(frozen=True)
class SourceLiveness:
    id: str
    source: str
    instrument: str
    observed_at: int
    known_at: int
    healthy: bool
    stream_kind: str
    evidence_id: str

    def __post_init__(self):
        for name in ('id', 'source', 'instrument', 'stream_kind', 'evidence_id'):
            _text(getattr(self, name), name)
        timestamp(self.observed_at); timestamp(self.known_at)
        if self.observed_at > self.known_at or type(self.healthy) is not bool:
            raise ContractError('liveness needs an available source observation and explicit health')
        if self.stream_kind not in {'heartbeat', 'source_observation', 'scheduled_publication'}:
            raise ContractError('copied state and zero trades are not source-liveness evidence')


@dataclass(frozen=True)
class QualityIncident:
    id: str
    stage: str
    fields: frozenset[FieldKey]
    known_at: int
    affected_from: int
    affected_until: int | None
    kind: str
    severity: str
    operations: frozenset[str]
    evidence_id: str
    scope: str = 'state'
    requires_recovery: bool = False

    def __post_init__(self):
        for name in ('id', 'kind', 'evidence_id'):
            _text(getattr(self, name), name)
        timestamp(self.known_at); timestamp(self.affected_from)
        if self.affected_until is not None:
            timestamp(self.affected_until)
            if self.affected_until <= self.affected_from:
                raise ContractError('quality interval must be nonempty and forward')
        if (not isinstance(self.fields, frozenset) or not self.fields
                or any(not isinstance(f, FieldKey) for f in self.fields)
                or self.stage not in {'raw', 'semantic'} or self.severity not in SEVERITIES
                or self.scope not in {'state', 'history'} or type(self.requires_recovery) is not bool):
            raise ContractError('quality needs typed immutable fields, stage, scope and severity')
        _operations(self.operations)
        if not self.operations:
            raise ContractError('quality incident must name its affected operations')
        if self.requires_recovery and self.affected_until is not None:
            raise ContractError('a recovery-required incident needs an explicit recovery, not a guessed end')

    def blocks(self, operation):
        return (operation in self.operations and self.severity != 'informational'
                and (self.severity != 'execution-block' or operation == 'execution'))


@dataclass(frozen=True)
class QualityRecovery:
    id: str
    incident_id: str
    fields: frozenset[FieldKey]
    known_at: int
    effective_at: int
    method: str
    evidence_id: str

    def __post_init__(self):
        for name in ('id', 'incident_id', 'evidence_id'):
            _text(getattr(self, name), name)
        timestamp(self.known_at); timestamp(self.effective_at)
        if (self.effective_at > self.known_at or not isinstance(self.fields, frozenset)
                or not self.fields or any(not isinstance(f, FieldKey) for f in self.fields)
                or self.method not in {'documented_book_snapshot', 'source_certified_rebuild',
                                       'certified_flow_replay', 'new_measurement_epoch'}):
            raise ContractError('recovery needs explicit available evidence and immutable scope')


def validate_recovery(recovery: QualityRecovery, incident: QualityIncident):
    if not isinstance(recovery, QualityRecovery) or not isinstance(incident, QualityIncident):
        raise ContractError('typed incident and recovery evidence required')
    if (recovery.incident_id != incident.id or not recovery.fields.issubset(incident.fields)
            or recovery.known_at < incident.known_at or recovery.effective_at <= incident.affected_from
            or not incident.requires_recovery):
        raise ContractError('recovery does not match the incident, interval or field scope')
    book_method = recovery.method in {'documented_book_snapshot', 'source_certified_rebuild'}
    if book_method and (incident.kind != 'book_gap' or incident.scope != 'state'):
        raise ContractError('book recovery cannot repair missing trade history')
    if not book_method and (incident.kind != 'flow_gap' or incident.scope != 'history'):
        raise ContractError('flow recovery/epoch must name a flow-history incident')


def validate_quality_evidence(incidents, recoveries):
    """Validate the complete supplied recovery relation, including future rows."""
    if not isinstance(incidents, tuple) or not isinstance(recoveries, tuple):
        raise ContractError('quality evidence collections must be immutable')
    by_id, admitted_incidents, admitted_recoveries = {}, {}, {}
    for collection, expected in ((incidents, QualityIncident), (recoveries, QualityRecovery)):
        for event in collection:
            if not isinstance(event, expected):
                raise ContractError('quality evidence has an invalid event kind')
            previous = by_id.get(event.id)
            if previous is not None and previous != event:
                raise ContractError('quality evidence ID has conflicting content')
            by_id[event.id] = event
    for incident in incidents:
        if not isinstance(incident, QualityIncident):
            raise ContractError('typed incident evidence required')
        admitted_incidents[incident.id] = incident
    for recovery in recoveries:
        if not isinstance(recovery, QualityRecovery):
            raise ContractError('typed recovery evidence required')
        incident = admitted_incidents.get(recovery.incident_id)
        validate_recovery(recovery, incident)
        if recovery.id in admitted_recoveries:
            continue
        if any(old.incident_id == recovery.incident_id and old.fields.intersection(recovery.fields)
               for old in admitted_recoveries.values()):
            raise ContractError('incident field already has immutable recovery evidence')
        admitted_recoveries[recovery.id] = recovery
    return tuple(admitted_incidents.values()), tuple(admitted_recoveries.values())


@dataclass(frozen=True)
class OperationPolicy:
    id: str
    operation: str
    max_age_ns: int
    max_source_silence_ns: int | None = None
    max_clock_uncertainty_ns: int = 0
    allow_estimated: bool = False

    def __post_init__(self):
        _text(self.id, 'policy')
        if self.operation not in OPERATIONS or type(self.allow_estimated) is not bool:
            raise ContractError('unknown operation or invalid estimate policy')
        _nonnegative(self.max_age_ns, 'maximum age')
        _nonnegative(self.max_clock_uncertainty_ns, 'clock uncertainty')
        if self.max_source_silence_ns is not None:
            _nonnegative(self.max_source_silence_ns, 'source silence')

    @property
    def version(self):
        return digest(self)


@dataclass(frozen=True)
class FieldSupport:
    key: FieldKey
    operation: str
    policy_version: str
    cut: int
    state: str
    reasons: tuple[str, ...]
    candidate_id: str | None
    origin_id: str | None
    acquisition_versions: tuple[tuple[str, str], ...]
    payload_json: bytes | None
    observed_at: int | None
    last_source_observation_at: int | None
    last_value_change_at: int | None
    last_local_receipt_at: int | None
    liveness_at: int | None
    liveness_id: str | None
    clock_uncertainty_ns: int
    incident_ids: tuple[str, ...]

    def __post_init__(self):
        timestamp(self.cut)
        if (not isinstance(self.key, FieldKey) or type(self.operation) is not str or self.operation not in OPERATIONS
                or type(self.state) is not str
                or self.state not in {'observed', 'estimated', 'missing', 'stale', 'ineligible', 'invalid'}
                or not isinstance(self.reasons, tuple) or not isinstance(self.acquisition_versions, tuple)
                or not isinstance(self.incident_ids, tuple)):
            raise ContractError('immutable typed field support required')
        _text(self.policy_version, 'policy version'); _nonnegative(self.clock_uncertainty_ns, 'uncertainty')
        for values in (self.reasons, self.incident_ids):
            if any(type(value) is not str or not value for value in values) or len(set(values)) != len(values):
                raise ContractError('support reasons and incidents need unique immutable identities')
        for pair in self.acquisition_versions:
            if (not isinstance(pair, tuple) or len(pair) != 2
                    or any(type(value) is not str or not value for value in pair)):
                raise ContractError('acquisition lineage needs immutable ID/version pairs')
        acquisition_ids = tuple(pair[0] for pair in self.acquisition_versions)
        if len(set(acquisition_ids)) != len(acquisition_ids):
            raise ContractError('acquisition identities cannot repeat with the same or changed version')
        for identity in (self.candidate_id, self.origin_id, self.liveness_id):
            if identity is not None:
                _text(identity, 'support evidence identity')
        for at in (self.observed_at, self.last_source_observation_at, self.last_value_change_at,
                   self.last_local_receipt_at, self.liveness_at):
            if at is not None:
                timestamp(at)
                if at > self.cut:
                    raise ContractError('field support cannot contain future clocks')
        if (self.liveness_at is None) != (self.liveness_id is None):
            raise ContractError('liveness time and evidence identity must appear together')
        if self.candidate_id is None:
            if (self.origin_id is not None or self.acquisition_versions
                    or any(at is not None for at in (self.observed_at, self.last_source_observation_at,
                                                     self.last_value_change_at, self.last_local_receipt_at))):
                raise ContractError('content clocks and lineage require a candidate')
        elif (self.origin_id not in acquisition_ids or self.candidate_id not in acquisition_ids
              or self.observed_at is None or self.last_source_observation_at is None):
            raise ContractError('candidate support lacks its observation and available origin lineage')
        if (self.observed_at is not None and self.last_source_observation_at is not None
                and self.last_source_observation_at < self.observed_at):
            raise ContractError('economic observation cannot follow the last source observation')
        if (self.last_value_change_at is not None
                and (self.last_source_observation_at is None
                     or self.last_value_change_at > self.last_source_observation_at)):
            raise ContractError('value change needs a matching source observation clock')
        if self.state in {'observed', 'estimated'}:
            if (self.payload_json is None or self.candidate_id is None
                    or (self.state == 'observed' and self.last_value_change_at is None)):
                raise ContractError('admitted support requires payload, clocks and evidence lineage')
            _json_payload(self.payload_json)
        elif self.payload_json is not None:
            raise ContractError('unavailable field cannot carry an admitted payload')

    @property
    def admitted(self):
        return self.state in {'observed', 'estimated'} and self.payload_json is not None

    @property
    def age_ns(self):
        return None if self.observed_at is None else self.cut - self.observed_at

    @property
    def age_lower_ns(self):
        return None if self.age_ns is None else max(0, self.age_ns - self.clock_uncertainty_ns)

    @property
    def age_upper_ns(self):
        return None if self.age_ns is None else self.age_ns + self.clock_uncertainty_ns

    @property
    def liveness_age_ns(self):
        return None if self.liveness_at is None else self.cut - self.liveness_at

    @property
    def version_vector_entry(self):
        # Ages and cut are reported separately: merely waiting is not new content.
        return (self.key.version, self.policy_version, self.candidate_id, self.origin_id,
                self.acquisition_versions, self.liveness_id, self.incident_ids, self.state)


def missing_support(key, policy, cut, *, incident_ids=()):
    return FieldSupport(key, policy.operation, policy.version, cut, 'missing', ('field_missing',),
                        None, None, (), None, None, None, None, None, None, None, 0, incident_ids)


def incident_interval(incident, recoveries, *, field, cut):
    """Known recovery ends future blocking but retains the bad historical span."""
    timestamp(cut)
    if not isinstance(field, FieldKey):
        raise ContractError('incident interval requires a typed field')
    _, recoveries = validate_quality_evidence((incident,), recoveries)
    if field not in incident.fields or incident.known_at > cut:
        return None
    end = incident.affected_until
    for recovery in recoveries:
        if (recovery.incident_id == incident.id and field in recovery.fields
                and recovery.known_at <= cut):
            end = recovery.effective_at if end is None else min(end, recovery.effective_at)
    return incident.affected_from, end


def interval_union(intervals):
    """Union finite half-open intervals; open ends must first be clipped to a cut."""
    result = []
    for left, right in sorted(intervals):
        timestamp(left); timestamp(right)
        if left >= right:
            raise ContractError('quality support interval is reversed or empty')
        if result and left <= result[-1][1]:
            result[-1] = (result[-1][0], max(right, result[-1][1]))
        else:
            result.append((left, right))
    return tuple(result)


@dataclass(frozen=True)
class ObservedSpan:
    """Positive source coverage, never inferred from an absence of incidents."""
    id: str
    field: FieldKey
    operation: str
    start: int
    end: int
    known_at: int
    evidence_id: str

    def __post_init__(self):
        _text(self.id, 'observed span'); _text(self.evidence_id, 'observation evidence')
        for at in (self.start, self.end, self.known_at):
            timestamp(at)
        if (not isinstance(self.field, FieldKey) or type(self.operation) is not str
                or self.operation not in OPERATIONS or self.start >= self.end or self.end > self.known_at):
            raise ContractError('positive coverage needs a typed field, operation and available completed span')


def _subtract_intervals(spans, removed):
    result = []
    for left, right in spans:
        cursor = left
        for bad_left, bad_right in removed:
            if bad_right <= cursor or bad_left >= right:
                continue
            if bad_left > cursor:
                result.append((cursor, bad_left))
            cursor = max(cursor, min(right, bad_right))
        if cursor < right:
            result.append((cursor, right))
    return tuple(result)


@dataclass(frozen=True)
class AggregateSupport:
    window: tuple[int, int]
    invalid_intervals: tuple[tuple[int, int], ...]
    incident_ids: tuple[str, ...]
    supported_intervals: tuple[tuple[int, int], ...]
    unknown_intervals: tuple[tuple[int, int], ...]
    observation_evidence_ids: tuple[str, ...]

    def __post_init__(self):
        if not isinstance(self.window, tuple) or len(self.window) != 2:
            raise ContractError('aggregate window must be an immutable interval')
        start, end = self.window
        timestamp(start); timestamp(end)
        if start >= end:
            raise ContractError('aggregate window must be forward')
        pieces = []
        for intervals in (self.invalid_intervals, self.supported_intervals, self.unknown_intervals):
            if (not isinstance(intervals, tuple)
                    or any(not isinstance(pair, tuple) or len(pair) != 2 for pair in intervals)):
                raise ContractError('aggregate partitions must be immutable interval pairs')
            if intervals != interval_union(intervals):
                raise ContractError('aggregate partitions must be ordered disjoint unions')
            if any(left < start or right > end for left, right in intervals):
                raise ContractError('aggregate evidence lies outside the requested window')
            pieces.extend(intervals)
        ordered = sorted(pieces)
        if (not ordered or ordered[0][0] != start or ordered[-1][1] != end
                or any(left[1] != right[0] for left, right in zip(ordered, ordered[1:]))):
            raise ContractError('observed, invalid and unknown spans must partition the window exactly')
        for identities in (self.incident_ids, self.observation_evidence_ids):
            if (not isinstance(identities, tuple) or any(type(v) is not str or not v for v in identities)
                    or len(set(identities)) != len(identities)):
                raise ContractError('aggregate provenance requires unique immutable evidence IDs')
        if self.supported_intervals and not self.observation_evidence_ids:
            raise ContractError('positive aggregate support requires observation evidence')

    @property
    def invalid_duration_ns(self):
        return sum(right - left for left, right in self.invalid_intervals)

    @property
    def supported_duration_ns(self):
        return sum(right - left for left, right in self.supported_intervals)

    @property
    def unknown_duration_ns(self):
        return sum(right - left for left, right in self.unknown_intervals)

    @property
    def missing_contribution_upper_bound(self):
        return None


def aggregate_support(incidents, recoveries, *, field, operation, start, end, cut, observed_spans=()):
    for at in (start, end, cut):
        timestamp(at)
    if (start >= end or end > cut or not isinstance(field, FieldKey)
            or type(operation) is not str or operation not in OPERATIONS
            or not isinstance(observed_spans, tuple)):
        raise ContractError('aggregate support requires a bounded interval, field, operation and immutable evidence')
    incidents, recoveries = validate_quality_evidence(incidents, recoveries)
    witnesses = {}
    for witness in observed_spans:
        if not isinstance(witness, ObservedSpan):
            raise ContractError('positive aggregate support needs typed observed spans')
        if witness.id in witnesses and witnesses[witness.id] != witness:
            raise ContractError('observed span ID has conflicting evidence')
        witnesses[witness.id] = witness
    spans, ids = [], []
    for incident in incidents:
        matching = tuple(r for r in recoveries if r.incident_id == incident.id)
        span = incident_interval(incident, matching, field=field, cut=cut)
        if span is None or not incident.blocks(operation):
            continue
        left, right = max(start, span[0]), min(end, span[1] if span[1] is not None else end)
        if left < right:
            spans.append((left, right)); ids.append(incident.id)
    observed, evidence_ids = [], []
    for witness in witnesses.values():
        if witness.field != field or witness.operation != operation or witness.known_at > cut:
            continue
        left, right = max(start, witness.start), min(end, witness.end)
        if left < right:
            observed.append((left, right)); evidence_ids.append(witness.evidence_id)
    invalid = interval_union(spans)
    supported = _subtract_intervals(interval_union(observed), invalid)
    unknown = _subtract_intervals(((start, end),), interval_union(invalid + supported))
    return AggregateSupport((start, end), invalid, tuple(sorted(set(ids))), supported,
                            unknown, tuple(sorted(set(evidence_ids))))


@dataclass(frozen=True)
class PropagatedQuality:
    graph_version: str
    blocked: frozenset[FieldRef]
    dirty_consumers: tuple[str, ...]
    optional_omissions: tuple[tuple[str, FieldRef], ...]
    unconditional: tuple[str, ...]
    affected_interval: tuple[int, int | None]
    incident_id: str
    unavailable_producers: frozenset[str]
    optional_provenance_omissions: tuple[tuple[str, str], ...]


class QualityDependencies:
    """Use the existing graph's field/optional/stage contract, never a hidden DAG."""
    def __init__(self, graph: Graph):
        if not isinstance(graph, Graph):
            raise ContractError('compiled graph required')
        self.graph = graph

    def propagate(self, incident: QualityIncident, *, cut, operation):
        timestamp(cut)
        if not isinstance(incident, QualityIncident) or operation not in OPERATIONS:
            raise ContractError('typed incident and registered operation required')
        refs = frozenset(field.ref for field in incident.fields)
        for ref in refs:
            if ref.producer not in self.graph.ports or ref.field not in self.graph.ports[ref.producer].fields:
                raise ContractError('quality incident references an undeclared raw field')
        active = (incident.known_at <= cut and incident.affected_from <= cut
                  and (incident.affected_until is None or cut < incident.affected_until)
                  and incident.blocks(operation))
        blocked = set(refs) if active else set()
        unavailable = {ref.producer for ref in blocked}
        dirty, omissions, provenance_omissions = set(), set(), set()
        if active:
            changed_fields, changed_producers = set(refs), set(unavailable)
            # Topological same-cut edges; a preceding-state edge cannot be made
            # unavailable by the current cut's incident without its own evidence.
            for key in self.graph.order:
                port = self.graph.ports[key]
                mandatory = False
                for edge in port.inputs:
                    if edge.lag_ns:
                        continue
                    if edge.fields:
                        consumed = {FieldRef(edge.source, f) for f in edge.fields}
                        if consumed.intersection(changed_fields):
                            dirty.add(key)
                        hits = consumed.intersection(blocked)
                        if hits and edge.optional:
                            omissions.update((key, ref) for ref in hits)
                        elif hits:
                            mandatory = True
                    else:
                        # An empty field set still requires the producer's
                        # same-cut provenance, including a fieldless producer.
                        if edge.source in changed_producers:
                            dirty.add(key)
                        if edge.source in unavailable:
                            if edge.optional:
                                provenance_omissions.add((key, edge.source))
                            else:
                                mandatory = True
                if mandatory:
                    unavailable.add(key)
                    blocked.update(FieldRef(key, f) for f in port.fields)
                if key in dirty:
                    changed_producers.add(key)
                    changed_fields.update(FieldRef(key, f) for f in port.fields)
        unconditional = tuple(k for k in self.graph.order if self.graph.ports[k].lane in {'market', 'account', 'timer'})
        return PropagatedQuality(self.graph.version, frozenset(blocked),
                                 tuple(k for k in self.graph.order if k in dirty),
                                 tuple(sorted(omissions)), unconditional,
                                 (incident.affected_from, incident.affected_until), incident.id,
                                 frozenset(unavailable), tuple(sorted(provenance_omissions)))


def classify_stream(*, expected_stream, recent_liveness, trade_count, halted=False,
                    stale_copy=False, computation_timeout=False):
    if any(type(v) is not bool for v in (expected_stream, recent_liveness, halted, stale_copy, computation_timeout)):
        raise ContractError('stream classification needs explicit evidence flags')
    _nonnegative(trade_count, 'observed trade count')
    if computation_timeout:
        return 'computation_timeout'
    if halted:
        return 'halted'
    if stale_copy:
        return 'stale_content'
    if expected_stream and not recent_liveness:
        return 'source_gap'
    if not expected_stream and not recent_liveness and trade_count == 0:
        return 'not_expected_unobserved'
    return 'observed_no_event' if trade_count == 0 else 'observed_events'


@dataclass(frozen=True)
class RepairPlan:
    state: str
    affected_fields: frozenset[FieldKey]
    missing_intervals: tuple[tuple[int, int], ...]
    checkpoint_cut: int
    correction_known_at: int


def plan_repair(*, affected_from, checkpoint_cut, correction_known_at, cut,
                affected_fields, retained_intervals):
    for at in (affected_from, checkpoint_cut, correction_known_at, cut):
        timestamp(at)
    if (checkpoint_cut >= affected_from or correction_known_at < affected_from
            or not isinstance(affected_fields, frozenset) or not affected_fields
            or any(not isinstance(k, FieldKey) for k in affected_fields)
            or not isinstance(retained_intervals, tuple)):
        raise ContractError('repair requires a preceding checkpoint, exact affected fields and retained originals')
    if cut < correction_known_at:
        return RepairPlan('not_yet_known', frozenset(), (), checkpoint_cut, correction_known_at)
    spans = interval_union(retained_intervals)
    cursor, missing = checkpoint_cut, []
    for left, right in spans:
        if right <= cursor or left >= cut:
            continue
        if left > cursor:
            missing.append((cursor, min(left, cut)))
        cursor = max(cursor, min(right, cut))
    if cursor < cut:
        missing.append((cursor, cut))
    return RepairPlan('unavailable' if missing else 'ready', affected_fields,
                      tuple(missing), checkpoint_cut, correction_known_at)
