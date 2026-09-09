"""Independent finite arrival list fold for registered F12 engineering fixtures.

This module does not import the candidate driver/journal or use candidate output
as its oracle. Explicit pure callbacks are the declared shared semantic kernels.
"""
import hashlib
import json


def _bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def _copy(value):
    return json.loads(_bytes(value))


def _hash(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def literal_replay(records, callbacks, *, definition='F12.ARRIVAL_TRACE.v1', policy_version='frozen-offline-v1'):
    if type(records) is not tuple or len(records) > 4096 or type(callbacks) is not tuple or len(callbacks) > 64:
        raise ValueError('finite immutable reference input required')
    specs = sorted(callbacks, key=lambda s: s.id)
    if len({s.id for s in specs}) != len(specs):
        raise ValueError('duplicate reference callback ID')
    states = {s.id: _copy(s.initial_state) for s in specs}
    declarations = [{'id': s.id, 'version_hash': s.version_hash, 'accepted_kinds': sorted(s.accepted_kinds),
                     'state_schema': s.state_schema, 'initial_sha256': _hash(s.initial_state),
                     'projection_id': s.projection_id} for s in specs]
    outputs, seen, clocks, source_generations = [], {}, {}, {}
    previous_ordinal, trace_id, active_boot, calls = -1, None, None, 0
    for supplied in records:
        r = _copy(supplied)
        if type(r['arrival_ordinal']) is not int or r['arrival_ordinal'] <= previous_ordinal:
            raise ValueError('reference arrival order regressed')
        if trace_id is not None and r['trace_id'] != trace_id:
            raise ValueError('reference trace ID changed')
        trace_id = r['trace_id']
        if r['delivery_id'] in seen:
            raise ValueError('reference trace contains a repeated transport receipt ID')
        if (type(r['receipt_monotonic_ns']) is not int or r['receipt_monotonic_ns'] < 0
                or r['boot_id'] in clocks and r['receipt_monotonic_ns'] < clocks[r['boot_id']]):
            raise ValueError('reference monotonic clock invalid')
        if active_boot is not None and active_boot != r['boot_id']:
            if r['kind'] != 'boot' or r['payload']['previous_boot_id'] != active_boot or r['boot_id'] in clocks:
                raise ValueError('reference boot epoch transition missing')
        p = r['payload']
        if r['kind'] == 'connection':
            prior = source_generations.get(p['source_id'])
            if prior and prior[1] != 'connected' and p['status'] == 'connected' and p['generation'] == prior[0]:
                raise ValueError('reference reconnect needs new generation')
            source_generations[p['source_id']] = (p['generation'], p['status'])
        elif r['kind'] == 'source':
            prior = source_generations.setdefault(p['source_id'], (p['stream_generation'], 'connected'))
            if prior != (p['stream_generation'], 'connected'):
                raise ValueError('reference source lacks active matching generation')
            raw = bytes.fromhex(p['raw_hex'])
            if hashlib.sha256(raw).hexdigest() != p['raw_sha256']:
                raise ValueError('reference raw bytes changed')
        selected = [s for s in specs if r['kind'] in s.accepted_kinds]
        named = p.get('decoder_id') if r['kind'] == 'source' else p.get('callback_id')
        if named is not None and named not in {s.id for s in selected}:
            raise ValueError('reference callback not registered')
        if not selected and r['kind'] in {'source', 'timer', 'completion', 'decision', 'order_ack'}:
            raise ValueError('reference required callback missing')
        proposed = _copy(states)
        sections = {'semantic': {}, 'timing': {}, 'transport': {}}
        for spec in selected:
            next_state, emitted = spec.transition(_copy(proposed[spec.id]), _copy(r))
            if type(next_state) is not dict or set(next_state) != set(spec.initial_state) or type(emitted) is not list:
                raise ValueError('reference callback state/output schema changed')
            proposed[spec.id] = _copy(next_state)
            for section in sections:
                part = [_copy(o[section]) for o in emitted if section in o]
                if part:
                    sections[section][spec.id] = part
            calls += 1
        semantic_states = {}
        for spec in specs:
            semantic_states[spec.id] = (_copy(proposed[spec.id]) if spec.semantic_projection is None
                                        else _copy(spec.semantic_projection(_copy(proposed[spec.id]))))
        if r['kind'] == 'source':
            core = {'kind': 'source', **{k: p[k] for k in ('source_id', 'instrument', 'definition', 'semantic_kind')}}
        elif r['kind'] == 'decision':
            core = {'kind': 'decision', **{k: p[k] for k in ('decision_id', 'action', 'served_version_ids')}}
        elif r['kind'] in {'connection', 'subscription', 'gap', 'cursor', 'boot', 'clock_adjust'}:
            core = {'kind': r['kind'], 'control': p}
        else:
            core = {'kind': r['kind']}
        semantic = {'record': core, 'states': semantic_states, 'outputs': sections['semantic']}
        timing = {k: r.get(k) for k in ('boot_id', 'receipt_utc_ns', 'receipt_monotonic_ns',
                                      'source_event_utc_ns', 'provider_published_utc_ns')}
        timing['outputs'] = sections['timing']
        observation = {'arrival_ordinal': r['arrival_ordinal'], 'delivery_id': r['delivery_id'], 'kind': r['kind'],
            'semantic': semantic,
            'semantic_sha256': _hash({'definition': definition, 'policy': policy_version,
                                      'callbacks': declarations, 'semantic': semantic}),
            'timing': timing, 'transport': {'record_sha256': _hash(r), 'provenance': r['provenance'],
                                          'outputs': sections['transport']},
            'simulated_boundary': True, 'actual_live_evidence': False}
        states = proposed
        outputs.append(observation)
        seen[r['delivery_id']] = _hash(r)
        previous_ordinal, active_boot = r['arrival_ordinal'], r['boot_id']
        clocks[r['boot_id']] = r['receipt_monotonic_ns']
    return {'states': states, 'observations': tuple(outputs),
            'metrics': {'reference_rows_examined': len(records), 'reference_callback_calls': calls},
            'simulated_boundary': True, 'actual_live_evidence': False}
