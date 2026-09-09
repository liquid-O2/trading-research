"""Independent finite F06/F07 full-scan oracle over immutable supplied facts.

No challenger index, timeline builder, field selector or joint helper is used.
The numeric units/thresholds belong to the caller's frozen engineering contract.
"""
from collections import Counter

from trading_research.errors import ContractError
from trading_research.foundations.joined import JoinedSnapshot, JointMovementEvidence, JointPolicy
from trading_research.foundations.quality import (
    OPERATIONS, AggregateSupport, FieldFact, FieldKey, FieldSupport, ObservedSpan, OperationPolicy,
    QualityIncident, QualityRecovery, SourceLiveness,
)
from trading_research.foundations.time import timestamp


def _quality_relation(events, counts=None):
    """Independent recovery admission checks; no production resolver is used."""
    if not isinstance(events, tuple):
        raise ContractError('literal evidence must be an immutable event sequence')
    identities, incidents, recoveries = {}, {}, {}
    for event in events:
        if counts is not None:
            counts['reference_quality_validation_checks'] += 1
        if not isinstance(event, (FieldFact, SourceLiveness, QualityIncident, QualityRecovery)):
            raise ContractError('unrecognized reference source event')
        if event.id in identities and identities[event.id] != event:
            raise ContractError('literal event identity conflicts')
        identities[event.id] = event
        if isinstance(event, QualityIncident):
            incidents[event.id] = event
        elif isinstance(event, QualityRecovery):
            recoveries[event.id] = event
    recovered = set()
    for recovery in recoveries.values():
        incident = incidents.get(recovery.incident_id)
        if (incident is None or not incident.requires_recovery
                or not recovery.fields.issubset(incident.fields)
                or recovery.known_at < incident.known_at or recovery.effective_at <= incident.affected_from):
            raise ContractError('literal recovery does not match available incident scope and timing')
        book = recovery.method in ('documented_book_snapshot', 'source_certified_rebuild')
        if ((book and (incident.kind != 'book_gap' or incident.scope != 'state'))
                or (not book and (incident.kind != 'flow_gap' or incident.scope != 'history'))):
            raise ContractError('literal recovery cannot substitute book state for flow history')
        for field in recovery.fields:
            pair = incident.id, field
            if pair in recovered:
                raise ContractError('literal incident field has duplicate recovery evidence')
            recovered.add(pair)
    return tuple(incidents.values()), tuple(recoveries.values())


def field_reference(events, key, policy, *, cut, counts=None):
    timestamp(cut)
    if not isinstance(key, FieldKey) or not isinstance(policy, OperationPolicy):
        raise ContractError('reference query needs typed field and policy')
    counts = Counter() if counts is None else counts
    if not isinstance(events, tuple):
        raise ContractError('literal evidence must be an immutable event sequence')
    history, pulses, incidents, recoveries = [], [], [], []
    all_quality = []
    winner_order, winners = None, []
    seen, signatures = {}, {}
    # Visit every fact for every requested field. Future rows count as inspected,
    # but cannot enter the admitted state or change an earlier-cut answer.
    for event in events:
        counts['reference_event_checks'] += 1
        if not isinstance(event, (FieldFact, SourceLiveness, QualityIncident, QualityRecovery)):
            raise ContractError('unrecognized reference source event')
        if isinstance(event, FieldFact):
            counts['candidate_row_checks'] += 1
        if event.id in seen:
            if seen[event.id] != event:
                raise ContractError('literal event identity conflicts')
            continue
        if isinstance(event, FieldFact):
            signature_key = event.key, event.observed_at, event.revision
            previous = signatures.get(signature_key)
            if previous is not None and previous != event.economic_signature:
                raise ContractError('literal acquisitions conflict regardless of their receipt times')
            signatures[signature_key] = event.economic_signature
            if event.content_origin_id is not None:
                origin = seen.get(event.content_origin_id)
                if (not isinstance(origin, FieldFact) or origin.content_origin_id is not None
                        or origin.known_at > event.known_at or origin.source != event.source
                        or origin.economic_signature != event.economic_signature
                        or origin.clocks.source_version != event.clocks.source_version
                        or origin.clocks.event_at != event.clocks.event_at
                        or origin.clocks.provider_received_at != event.clocks.provider_received_at
                        or origin.clocks.published_at != event.clocks.published_at):
                    raise ContractError('literal copied content lacks its preceding matching origin')
        seen[event.id] = event
        if isinstance(event, (QualityIncident, QualityRecovery)):
            all_quality.append(event)
        if isinstance(event, FieldFact):
            if event.key != key or event.known_at > cut or event.observed_at > cut:
                continue
            history.append(event)
            priority = event.observed_at, event.revision
            if winner_order is None or priority > winner_order:
                winner_order, winners = priority, [event]
            elif priority == winner_order:
                winners.append(event)
        elif isinstance(event, SourceLiveness):
            if event.instrument == key.instrument and event.known_at <= cut and event.observed_at <= cut:
                pulses.append(event)
        elif isinstance(event, QualityIncident):
            if key in event.fields and event.known_at <= cut and policy.operation in event.operations:
                incidents.append(event)
        elif isinstance(event, QualityRecovery):
            if key in event.fields and event.known_at <= cut:
                recoveries.append(event)
        else:
            raise ContractError('unrecognized reference source event')
    # This validation visits only quality rows. The source-fact selection above
    # remains one counted visit per supplied fact, field and cut.
    _quality_relation(tuple(all_quality), counts)
    active = []
    for incident in incidents:
        end = incident.affected_until
        for recovery in recoveries:
            if recovery.incident_id == incident.id:
                if end is None or recovery.effective_at < end:
                    end = recovery.effective_at
        if incident.affected_from <= cut and (end is None or cut < end):
            active.append(incident)
    active_ids = tuple(sorted(i.id for i in active))
    if not winners:
        return FieldSupport(key, policy.operation, policy.version, cut, 'missing', ('field_missing',),
                            None, None, (), None, None, None, None, None, None, None, 0, active_ids)
    winners.sort(key=lambda f: f.id)
    selected = min(winners, key=lambda f: (f.content_origin_id is not None, f.id))
    for other in winners:
        if other.economic_signature != selected.economic_signature:
            raise ContractError('conflicting overlapping field acquisitions in literal reference')
    real_history = [row for row in history if row.content_origin_id is None]
    real_history.sort(key=lambda row: (row.observed_at, row.revision, row.id))
    prior_value, changed_at = None, None
    for row in real_history:
        if not row.eligible or row.estimated:
            continue
        if prior_value != row.payload_json:
            changed_at = row.observed_at
        prior_value = row.payload_json
    source_observation = max((row.observed_at for row in real_history), default=None)
    local_receipt = max((row.clocks.received_at for row in history if row.clocks.received_at is not None), default=None)
    relevant_pulses = [pulse for pulse in pulses if pulse.source == selected.source]
    relevant_pulses.sort(key=lambda pulse: (pulse.observed_at, pulse.known_at, pulse.id))
    latest_pulse = relevant_pulses[-1] if relevant_pulses else None
    blocking_kinds = set()
    for incident in active:
        if incident.severity == 'informational':
            continue
        if incident.severity == 'execution-block' and policy.operation != 'execution':
            continue
        blocking_kinds.add(incident.kind)
    state, reasons = ('estimated' if selected.estimated else 'observed'), ()
    if policy.operation not in selected.available_operations:
        state, reasons = 'ineligible', ('source_capability_missing',)
    elif not selected.eligible:
        state, reasons = 'invalid', ('source_invalid',)
    elif ((selected.clocks.valid_from is not None and cut < selected.clocks.valid_from)
          or (selected.clocks.valid_until is not None and cut >= selected.clocks.valid_until)):
        state, reasons = 'ineligible', ('definition_or_source_validity',)
    elif selected.estimated and not policy.allow_estimated:
        state, reasons = 'ineligible', ('estimated_value_not_admitted',)
    elif blocking_kinds:
        state, reasons = 'invalid', tuple(sorted(blocking_kinds))
    elif selected.clocks.clock_uncertainty_ns > policy.max_clock_uncertainty_ns:
        state, reasons = 'ineligible', ('clock_uncertainty_exceeded',)
    elif cut > selected.observed_at + policy.max_age_ns - selected.clocks.clock_uncertainty_ns:
        state, reasons = 'stale', ('conservative_age_exceeded',)
    elif policy.max_source_silence_ns is not None:
        if latest_pulse is None:
            state, reasons = 'missing', ('liveness_missing',)
        elif not latest_pulse.healthy:
            state, reasons = 'invalid', ('source_gap',)
        elif cut > latest_pulse.observed_at + policy.max_source_silence_ns:
            state, reasons = 'stale', ('source_silent',)
    return FieldSupport(key, policy.operation, policy.version, cut, state, reasons, selected.id,
                        selected.content_origin_id or selected.id,
                        tuple((row.id, row.clocks.source_version) for row in winners),
                        selected.payload_json if state in ('observed', 'estimated') else None,
                        selected.observed_at, source_observation, changed_at, local_receipt,
                        latest_pulse.observed_at if latest_pulse else None,
                        latest_pulse.id if latest_pulse else None,
                        selected.clocks.clock_uncertainty_ns, active_ids)


def snapshot_reference(events, requests, *, cut, joint_policy, optional=frozenset(), movement=None, counts=None):
    if (not isinstance(requests, tuple) or not requests or not isinstance(joint_policy, JointPolicy)
            or not isinstance(optional, frozenset)
            or not optional.issubset(key for key, _ in requests)
            or len({key for key, _ in requests}) != len(requests)
            or (movement is not None and not isinstance(movement, JointMovementEvidence))):
        raise ContractError('literal joined request violates its explicit contract')
    fields = tuple(field_reference(events, key, policy, cut=cut, counts=counts) for key, policy in requests)
    if len({f.operation for f in fields}) != 1:
        raise ContractError('literal joint request mixes operations')
    omitted, admitted, failures = [], [], []
    for field in fields:
        if field.admitted:
            admitted.append(field)
        elif field.key in optional:
            omitted.append(field.key)
    if any(not f.admitted and f.key not in optional for f in fields):
        failures.append('required_field_unavailable')
    if not admitted:
        failures.append('no_admitted_fields')
        span = None
    else:
        earliest = min(f.observed_at - f.clock_uncertainty_ns for f in admitted)
        latest = max(f.observed_at + f.clock_uncertainty_ns for f in admitted)
        span = latest - earliest
        if span > joint_policy.max_observation_span_ns:
            failures.append('asynchronous_support')
        if joint_policy.max_movement_ticks is not None:
            valid_witness = (movement is not None and movement.complete and movement.known_at <= cut
                             and movement.instrument == joint_policy.reference_instrument
                             and movement.start <= earliest and movement.end >= cut)
            if not valid_witness:
                failures.append('movement_support_missing')
            elif movement.max_ticks - movement.min_ticks > joint_policy.max_movement_ticks:
                failures.append('movement_limit_exceeded')
    return JoinedSnapshot(cut, fields[0].operation, joint_policy.version, fields, tuple(omitted), not failures,
                          tuple(failures), span, movement.id if movement is not None and movement.known_at <= cut else None)


def aggregate_reference(events, *, field, operation, start, end, cut, observed_spans=()):
    """Independent sweep of positive, invalid and unknown interval categories."""
    for at in (start, end, cut):
        timestamp(at)
    if (start >= end or end > cut or not isinstance(field, FieldKey)
            or type(operation) is not str or operation not in OPERATIONS
            or not isinstance(observed_spans, tuple)):
        raise ContractError('reference support window is invalid')
    incidents, all_recoveries = _quality_relation(events)
    changes, ids, witness_ids = {start: [0, 0], end: [0, 0]}, [], []
    recoveries = [r for r in all_recoveries if r.known_at <= cut and field in r.fields]
    for incident in incidents:
        if (incident.known_at > cut or field not in incident.fields
                or operation not in incident.operations or incident.severity == 'informational'
                or (incident.severity == 'execution-block' and operation != 'execution')):
            continue
        stop = end if incident.affected_until is None else incident.affected_until
        for recovery in recoveries:
            if recovery.incident_id == incident.id:
                stop = min(stop, recovery.effective_at)
        left, right = max(start, incident.affected_from), min(end, stop)
        if left < right:
            ids.append(incident.id)
            changes.setdefault(left, [0, 0])[0] += 1
            changes.setdefault(right, [0, 0])[0] -= 1
    seen = {}
    for witness in observed_spans:
        if not isinstance(witness, ObservedSpan):
            raise ContractError('literal positive support requires an observed-span witness')
        if witness.id in seen:
            if seen[witness.id] != witness:
                raise ContractError('literal observed-span identity conflicts')
            continue
        seen[witness.id] = witness
        if witness.field != field or witness.operation != operation or witness.known_at > cut:
            continue
        left, right = max(start, witness.start), min(end, witness.end)
        if left < right:
            witness_ids.append(witness.evidence_id)
            changes.setdefault(left, [0, 0])[1] += 1
            changes.setdefault(right, [0, 0])[1] -= 1
    invalid, observed, categories = 0, 0, {'invalid': [], 'supported': [], 'unknown': []}
    points = sorted(changes)
    for position, left in enumerate(points[:-1]):
        invalid += changes[left][0]
        observed += changes[left][1]
        right = points[position + 1]
        category = 'invalid' if invalid > 0 else 'supported' if observed > 0 else 'unknown'
        spans = categories[category]
        if spans and spans[-1][1] == left:
            spans[-1] = spans[-1][0], right
        else:
            spans.append((left, right))
    return AggregateSupport((start, end), tuple(categories['invalid']), tuple(sorted(set(ids))),
                            tuple(categories['supported']), tuple(categories['unknown']), tuple(sorted(set(witness_ids))))
