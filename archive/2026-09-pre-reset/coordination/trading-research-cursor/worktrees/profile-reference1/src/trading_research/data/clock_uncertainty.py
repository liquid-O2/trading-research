"""Explicit source-clock uncertainty; original event timestamps remain intact."""
from __future__ import annotations

import copy
import math
import struct

from trading_research.errors import IntegrityError

_plans = ()
_fields = ('t', 'action', 'side', 'price', 'size', 'bid_px', 'ask_px',
           'bid_sz', 'ask_sz', 'instrument_id', 'flags', 'source_row')


def original_record(record):
    return {name: ({'$float64_bits_le': struct.pack('<d', value).hex()}
                   if type(value) is float and not math.isfinite(value) else value)
            for name in _fields for value in (record.get(name),)}


def configure(plans):
    global _plans
    if not isinstance(plans, (tuple, list)):
        raise IntegrityError('explicit authenticated clock uncertainty plans required')
    for plan in plans:
        lo, hi = plan['interval']
        if (type(lo) is not int or type(hi) is not int or not lo < hi
                or not plan['event_start_ns'] <= lo < hi < plan['event_end_ns']
                or lo // 60_000_000_000 != hi // 60_000_000_000
                or plan['event']['source_row'] != plan['predecessor']['source_row'] + 1
                or plan['event']['t'] != lo or plan['predecessor']['t'] != hi
                or plan['event']['instrument_id'] != plan['predecessor']['instrument_id']
                or 'R' not in (plan['event']['action'], plan['predecessor']['action'])):
            raise IntegrityError('bounded original reset pair required')
    _plans = tuple(copy.deepcopy(plans))


def plans_for(records, start, end):
    from trading_research.operations.artifacts import digest
    identities = {(r['path'], digest(r)) for r in records}
    return tuple(copy.deepcopy(p) for p in _plans
                 if (p['source_path'], p['source_metadata_sha256']) in identities
                 and (p['event_start_ns'], p['event_end_ns']) == (start, end))


def clock_order_valid(times, previous, intervals):
    import numpy as np
    if not len(times):
        return True
    if not intervals:
        return not (np.any(times[1:] < times[:-1]) or previous is not None and times[0] < previous)
    high = np.maximum.accumulate(np.r_[int(times[0]) if previous is None else previous, times])[:-1]
    bad = times < high
    admitted = np.zeros(len(times), dtype=bool)
    for lo, hi in intervals:
        admitted |= (times >= lo) & (high <= hi)
    return not np.any(bad & ~admitted)


def certain_segments(starts, ends, intervals):
    """Subtract unknown durations, retaining the original interval owner index."""
    import numpy as np
    a, b = np.asarray(starts), np.asarray(ends)
    index = np.arange(len(a), dtype=np.int64)
    for lo, hi in intervals:
        outside = (b <= lo) | (a >= hi)
        left = ~outside & (a < lo)
        right = ~outside & (b > hi)
        a, b, index = (np.r_[a[outside], a[left], np.full(np.count_nonzero(right), hi)],
                       np.r_[b[outside], np.full(np.count_nonzero(left), lo), b[right]],
                       np.r_[index[outside], index[left], index[right]])
    keep = b > a
    a, b, index = a[keep], b[keep], index[keep]
    order = np.argsort(a, kind='stable')
    return a[order], b[order], index[order]
