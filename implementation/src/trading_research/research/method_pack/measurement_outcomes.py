"""Descriptive post-setup prices under the frozen full-history protocol.

No output from this module is passed to a scanner. A measurement reference is
not a modeled fill, and a missing price interval cannot certify an outcome.
"""
from decimal import Decimal as D

from .historical_features import MINUTE, SECOND
from .historical_flow import batches
from .branch_coverage import setting


HORIZONS = (5, 15, 30, 60)


def signed_excursions(low, high, reference, side):
    low, high, reference = map(lambda x: D(str(x)), (low, high, reference))
    favorable, adverse = ((high-reference, reference-low) if side == 'long'
                           else (reference-low, high-reference))
    return {'favorable_points': max(D(0), favorable),
            'adverse_points': max(D(0), adverse),
            'favorable_ticks': max(D(0), favorable)/D('.25'),
            'adverse_ticks': max(D(0), adverse)/D('.25')}


def price_origin(market, episode):
    start = episode['decision_at']
    entry = episode.get('geometry', {}).get('entry')
    if entry is not None:
        return {'price': D(str(entry)), 'at': start,
                'kind': 'existing_setup_entry_reference', 'actual_fill': False}
    trigger = episode.get('trigger', {})
    if trigger.get('C') is not None and trigger.get('known_at', start+1) <= start:
        return {'price': D(str(trigger['C'])), 'at': start,
                'kind': 'measurement_only_completed_trigger_close',
                'evidence': trigger.get('bar_id'), 'actual_fill': False}
    # Read at most one minute at a time; preserve the entire first timestamp
    # batch rather than selecting a favorable print from an ambiguous batch.
    for a in range(start, market.end, MINUTE):
        for at, rows in batches(market.local(a, min(a+MINUTE, market.end))):
            if at <= start:
                continue
            quantity = sum(r['executed_size'] for r in rows)
            if quantity:
                return {'price': sum(r['price']*r['executed_size'] for r in rows)/quantity,
                        'at': at, 'kind': 'measurement_only_first_subsequent_batch_vwap',
                        'event_ids': [r['event_id'] for r in rows], 'actual_fill': False}
    return {'price': None, 'at': start, 'kind': 'unavailable_post_confirmation_price',
            'actual_fill': False}


def rounded_coverage(market, start, end):
    if end <= start:
        return {'observed_scope_complete': False, 'unknown_intervals': [],
                'reason': 'no positive subsequent interval'}
    # A whole-minute evidence check is deliberately conservative. Partial
    # interval endpoint arithmetic must not turn ordinary sub-minute decisions
    # into gaps, while a genuinely missing enclosing minute stays unknown.
    return market.coverage(max(market.start, start//MINUTE*MINUTE),
                           min(market.end, ((end+MINUTE-1)//MINUTE)*MINUTE))


def interval_extrema(market, start, end):
    """Exact open-left/closed-right native population using cached full seconds.

    Full-second H/L do not need an invented ordering of opening/closing prints.
    Boundary seconds are read natively and filtered to (start, end].
    """
    if end <= start:
        return None
    a = (start//SECOND+1)*SECOND
    b = end//SECOND*SECOND
    bars = market.bars(a, b, 1) if b > a else []
    pieces = [{'low': r['L'], 'high': r['H'], 'id': r['bar_id'],
               'kind': 'owned_native_second_extrema'} for r in bars]
    spans = [(start, min(a, end+1))]
    if b >= a:
        spans.append((b, min(end+1, market.end)))
    for lo, hi in spans:
        if hi <= lo:
            continue
        rows = [r for r in market.local(lo, hi) if start < r['event_ns'] <= end]
        if rows:
            low, high = min(r['price'] for r in rows), max(r['price'] for r in rows)
            pieces.append({'low': low, 'high': high, 'kind': 'owned_native_boundary_events',
                           'id': [r['event_id'] for r in rows if r['price'] in (low, high)]})
    if not pieces:
        return None
    low, high = min(r['low'] for r in pieces), max(r['high'] for r in pieces)
    return {'low': low, 'high': high,
            'extremum_evidence': [r for r in pieces if r['low'] == low or r['high'] == high]}


def boundary_order(market, episode, origin):
    """Observe defined structural boundaries independently of missing partners."""
    geometry = episode.get('geometry', {})
    stop, target = (None if geometry.get(k) is None else D(str(geometry[k]))
                    for k in ('stop', 'target'))
    start = origin['at']
    end = min(market.end, episode['decision_at'] + setting('outcomes')['horizon_minutes']*MINUTE)
    outbound = episode['method'] == 'JJ-TBR' and episode['branch'] == 'judas_outbound'
    if outbound:
        end = min(end, market.at(setting('tbr_sessions')['outbound_end']))
    result = {'start_ns': start, 'end_ns': end, 'stop': stop, 'target': target,
              'expiry_kind': 'published_outbound_deadline' if outbound else 'fixed_measurement_expiry',
              'result': 'boundaries_not_defined', 'resolved_at_ns': None,
              'seconds_to_resolution': None, 'actual_trade': False}
    if stop is None and target is None:
        return result
    if end <= start:
        return dict(result, result='missing_future_coverage')
    sg = 1 if episode['side'] == 'long' else -1
    # Each possible first crossing second is resolved on whole native batches.
    spans = [(start, min((start//SECOND+1)*SECOND, end))]
    a = (start//SECOND+1)*SECOND
    for r in market.bars(a, end, 1) if end > a else []:
        crosses = ((target is not None and (r['H'] >= target if sg == 1 else r['L'] <= target)) or
                   (stop is not None and (r['L'] <= stop if sg == 1 else r['H'] >= stop)))
        if crosses:
            spans.append((r['start'], r['end']))
    tail = end//SECOND*SECOND
    if tail >= a and end > tail:
        spans.append((tail, end))
    for lo, hi in spans:
        if hi <= lo:
            continue
        for at, rows in batches(market.local(lo, hi)):
            if at <= start:
                continue
            objectives = [r for r in rows if target is not None and sg*(r['price']-target) >= 0]
            invalidations = [r for r in rows if stop is not None and sg*(r['price']-stop) <= 0]
            if not objectives and not invalidations:
                continue
            coverage = rounded_coverage(market, start, at+1)
            observed = ('unresolved_timestamp_order' if objectives and invalidations else
                        'objective_observed' if objectives else 'invalidation_observed')
            result.update(observed_result=observed, result=observed if coverage['observed_scope_complete']
                          else 'unresolved_prior_coverage', resolved_at_ns=at,
                          resolution_known_at_ns=max(r['known_at'] for r in rows),
                          seconds_to_resolution=(at-episode['decision_at'])/SECOND,
                          event_ids=[r['event_id'] for r in objectives+invalidations], coverage=coverage,
                          both_boundaries_defined=stop is not None and target is not None)
            return result
    coverage = rounded_coverage(market, start, end)
    result.update(result='expired_without_observed_boundary' if coverage['observed_scope_complete']
                  else 'missing_future_coverage', coverage=coverage,
                  both_boundaries_defined=stop is not None and target is not None)
    return result


def measure_setup(market, episode):
    origin = price_origin(market, episode)
    result = {'schema': 'phase1-setup-price-measurement-v1',
              'candidate_id': episode['candidate_id'], 'origin': origin,
              'actual_fill': False, 'simulated_return': None, 'horizons': []}
    if origin['price'] is None or episode['side'] not in ('long', 'short'):
        return dict(result, status='measurement_reference_unavailable')
    for minutes in HORIZONS:
        requested = episode['decision_at'] + minutes*MINUTE
        end = min(market.end, requested)
        extrema = interval_extrema(market, origin['at'], end)
        coverage = rounded_coverage(market, origin['at'], end)
        complete = requested <= market.end and coverage['observed_scope_complete'] and extrema is not None
        row = {'minutes': minutes, 'requested_end_ns': requested, 'observed_end_ns': end,
               'horizon_truncated': requested > market.end, 'coverage': coverage,
               'status': 'complete_observed_horizon' if complete else 'incomplete_future_coverage',
               'extrema_are_lower_bounds': not complete,
               'measurement_start_delay_seconds': (origin['at']-episode['decision_at'])/SECOND}
        if extrema is not None:
            row.update(extrema, **signed_excursions(extrema['low'], extrema['high'], origin['price'], episode['side']))
        result['horizons'].append(row)
    result.update(status='measured', boundary=boundary_order(market, episode, origin))
    return result
