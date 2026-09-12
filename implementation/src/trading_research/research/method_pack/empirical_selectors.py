"""Causal state machines for frozen, explicitly observable comparison rules.

Inputs are complete typed native bars supplied by the empirical runner. Initial
opportunities never inspect subsequent bars. Replay is a separate operation;
prefix records and IDs remain invariant as later bars arrive.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Callable

from .empirical_protocol import Opportunity, ReplayResult, content_hash

MINUTE = 60_000_000_000


def _d(value):
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _bar_ok(bar, instrument_id):
    if str(bar.get('instrument_id')) != str(instrument_id):
        raise ValueError('selector received foreign native instrument')
    start, end, known = bar.get('start'), bar.get('end'), bar.get('known_at')
    if any(type(t) is not int for t in (start, end, known)) or not start < end <= known:
        raise ValueError('selector received contradictory native bar clocks')
    if bar.get('complete') is not True or any(bar.get(k) is None for k in ('O','H','L','C','V')):
        return False
    if _d(bar['H']) < max(_d(bar[k]) for k in ('O','L','C')) or _d(bar['L']) > min(_d(bar[k]) for k in ('O','H','C')):
        raise ValueError('selector received impossible native bar geometry')
    return True


def validate_bar_stream(bars, instrument_id):
    seen, previous = set(), None
    for bar in bars:
        _bar_ok(bar, instrument_id)
        key = bar['start'], bar['end']
        if key in seen or previous is not None and bar['start'] < previous:
            raise ValueError('duplicate, overlapping or out-of-order native bars')
        seen.add(key)
        previous = bar['end']


def compact_bar(bar):
    return {key: bar.get(key) for key in
            ('bar_id','instrument_id','start','end','known_at','complete','O','H','L','C','V')}


def make_opportunity(rule, partition, reference, bar, side, registry_sha256, expiry_at):
    identity = {'rule_id': rule['rule_id'], 'registry_sha256': registry_sha256,
                'partition_id': partition['partition_id'], 'instrument_id': partition['instrument_id'],
                'reference_id': reference['reference_id'], 'side': side,
                'occurrence_start': bar['start'], 'occurrence_end': bar['end']}
    return Opportunity(
        opportunity_id='opp-'+content_hash(identity)[:24], rule_id=rule['rule_id'],
        method_id=rule['method_id'], branch=rule['branch'], partition_id=partition['partition_id'],
        instrument_id=partition['instrument_id'], session_date=partition['session_date'],
        side=side, occurrence_start=bar['end'] if reference.get('initial_event_kind') == 'completion' else bar['start'], occurrence_end=bar['end'], available_at=bar['known_at'],
        reference_id=reference['reference_id'], reference_known_at=reference['known_at'],
        reference=reference, trigger=compact_bar(bar), expiry_at=expiry_at,
        assumption_ids=tuple(rule['assumption_ids']), registry_sha256=registry_sha256,
        observation_unit=rule.get('transport_observation_unit', 'market_opportunity'),
    ).validate()


def first_excursions(rule, partition, reference, bars, *, registry_sha256,
                     action_start, expiry_at, trigger='strict_sweep', sides=('short','long')):
    """At most one initial observation per side and identified reference.

    No confirmation, reward, stop or later return participates in this choice.
    A missing minute before an apparent first observation invalidates firstness;
    the caller records the partition's missing opportunity population.
    """
    validate_bar_stream(bars, partition['instrument_id'])
    if reference.get('complete') is not True or reference['known_at'] > action_start:
        return [], ['reference_incomplete_or_unavailable']
    selected, found, holes = [], set(), []
    cursor = action_start
    for bar in bars:
        if bar['end'] <= action_start:
            continue
        if bar['start'] >= expiry_at:
            break
        if bar['start'] != cursor or not _bar_ok(bar, partition['instrument_id']):
            holes.append('missing_initial_opportunity_interval')
            break
        cursor = bar['end']
        if bar['known_at'] > expiry_at:
            break
        for side in sides:
            if side in found:
                continue
            if trigger == 'strict_sweep':
                touched = _d(bar['H']) > _d(reference['high']) if side == 'short' else _d(bar['L']) < _d(reference['low'])
            elif trigger == 'extension_band':
                lo, hi = reference['upper_band'] if side == 'short' else reference['lower_band']
                touched = _d(bar['H']) >= _d(lo) and _d(bar['L']) <= _d(hi)
            elif trigger == 'close_above_both':
                touched = side == 'long' and _d(bar['C']) > max(_d(reference['asia_high']), _d(reference['london_high']))
            elif trigger == 'close_outside':
                touched = _d(bar['C']) > _d(reference['high']) if side == 'long' else _d(bar['C']) < _d(reference['low'])
            else:
                raise ValueError(f'unsupported frozen trigger: {trigger}')
            if touched:
                selected.append(make_opportunity(rule, partition, reference, bar, side, registry_sha256, expiry_at))
                found.add(side)
        if len(found) == len(sides):
            break
    if cursor < expiry_at and len(found) < len(sides) and not holes:
        holes.append('initial_opportunity_window_right_censored')
    return selected, holes


def next_aligned_close(opportunity, bars, *, minutes, endpoint='reclaim', extra_condition=None):
    """Score the next clock-aligned close, never search for a favorable close."""
    validate_bar_stream(bars, opportunity.instrument_id)
    duration = minutes*MINUTE
    end = ((opportunity.available_at // duration)+1)*duration
    start = end-duration
    if end > opportunity.expiry_at:
        return ReplayResult(opportunity.opportunity_id, 'unknown', opportunity.expiry_at, None,
                            'next_aligned_close_after_frozen_expiry', censored=True).validate(opportunity)
    members = [bar for bar in bars if start <= bar['start'] and bar['end'] <= end]
    cursor = start
    for bar in members:
        if bar['start'] != cursor or not _bar_ok(bar, opportunity.instrument_id) or bar['known_at'] > end:
            return ReplayResult(opportunity.opportunity_id, 'unknown', end, None,
                                'missing_or_unavailable_confirmation_members', censored=True).validate(opportunity)
        cursor = bar['end']
    if cursor != end or not members:
        return ReplayResult(opportunity.opportunity_id, 'unknown', end, None,
                            'missing_confirmation_interval', censored=True).validate(opportunity)
    close = _d(members[-1]['C'])
    ref, side = opportunity.reference, opportunity.side
    if endpoint == 'reclaim':
        passed = close < _d(ref['high']) if side == 'short' else close > _d(ref['low'])
        if ref.get('require_inside_box'):
            passed = passed and _d(ref['low']) < close < _d(ref['high'])
    elif endpoint == 'extension_rejection':
        passed = close < _d(ref['upper_band'][0]) if side == 'short' else close > _d(ref['lower_band'][1])
    else:
        raise ValueError('unknown frozen close endpoint')
    if extra_condition is not None:
        passed = passed and extra_condition(close, ref, side)
    endpoint_bar = {'bar_id':f'{opportunity.instrument_id}:{start}:{end}', 'instrument_id':opportunity.instrument_id,
                    'start':start, 'end':end, 'known_at':end, 'complete':True,
                    'O':members[0]['O'], 'H':max(_d(b['H']) for b in members),
                    'L':min(_d(b['L']) for b in members), 'C':close,
                    'V':sum((_d(b['V']) for b in members), Decimal(0)),
                    'member_bar_ids':[b['bar_id'] for b in members]}
    return ReplayResult(opportunity.opportunity_id, 'pass' if passed else 'fail', end, endpoint_bar,
                        'next_aligned_close_condition_met' if passed else 'next_aligned_close_condition_failed',
                        selected_signal_at=end if passed else None).validate(opportunity)


def later_touch(opportunity, bars, boundary_at: Callable, *, require_close_side=False):
    """Observe a later touch of a boundary frozen before each contact bar.

    boundary_at(start) returns (price, known_at), or None for missing coverage.
    It must never consume the contact bar. A missing earlier interval censors
    first-touch discovery even when a later bar looks favorable.
    """
    validate_bar_stream(bars, opportunity.instrument_id)
    cursor = opportunity.available_at
    for bar in bars:
        if bar['start'] < cursor:
            continue
        if bar['start'] >= opportunity.expiry_at:
            break
        if bar['start'] != cursor or not _bar_ok(bar, opportunity.instrument_id):
            return ReplayResult(opportunity.opportunity_id, 'unknown', cursor, None,
                                'missing_later_sequence_interval', censored=True).validate(opportunity)
        boundary = boundary_at(bar['start'])
        if boundary is None:
            return ReplayResult(opportunity.opportunity_id, 'unknown', cursor, None,
                                'boundary_snapshot_unavailable', censored=True).validate(opportunity)
        price, known = boundary
        if known > bar['start']:
            raise ValueError('contact uses a future boundary snapshot')
        cursor = bar['end']
        if cursor > opportunity.expiry_at:
            break
        touched = _d(bar['L']) <= _d(price) <= _d(bar['H'])
        if touched:
            if require_close_side:
                passed = _d(bar['C']) > _d(price) if opportunity.side == 'long' else _d(bar['C']) < _d(price)
            else:
                passed = True
            endpoint = dict(compact_bar(bar), boundary_price=price, boundary_known_at=known)
            return ReplayResult(opportunity.opportunity_id, 'pass' if passed else 'fail', cursor, endpoint,
                'first_later_touch_confirmed' if passed else 'first_later_touch_failed_close',
                selected_signal_at=cursor if passed else None).validate(opportunity)
    if cursor < opportunity.expiry_at:
        return ReplayResult(opportunity.opportunity_id, 'unknown', cursor, None,
                            'later_sequence_right_censored', censored=True).validate(opportunity)
    return ReplayResult(opportunity.opportunity_id, 'fail', opportunity.expiry_at, None,
                        'no_later_touch_before_expiry').validate(opportunity)
