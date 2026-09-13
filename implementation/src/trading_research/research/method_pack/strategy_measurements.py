"""Resolve strategy measurements from complementary owned market records.

The strict tick adapter remains unchanged. Published OHLCV may resolve an
endpoint only after its complete clock interval and after H/L/V reconciliation.
Local flow uses an order-independent price for a simultaneous execution batch.
"""
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal as D
from functools import lru_cache
from pathlib import Path

import pyarrow.parquet as pq

from .event_time import EventWindow, MINUTE, SECOND
from .empirical_protocol import content_hash


@lru_cache(maxsize=24)
def vendor_rows(root, start, end, base_seconds=60, instrument_id=None):
    """Bounded, instrument-preserving reads; the source bar clock is explicit."""
    folder = Path(root) / 'quantpad' / ('cme__nq-continuous-futures__ohlcv-1s'
        if base_seconds == 1 else 'cme__nq-continuous-futures__ohlcv-1m')
    first = datetime.fromtimestamp(start / SECOND, timezone.utc).year
    last = datetime.fromtimestamp((end - 1) / SECOND, timezone.utc).year
    rows, receipts = [], []
    from .historical_runner import file_digest
    for year in range(first, last + 1):
        path = folder / f'{year}.parquet'
        if not path.exists():
            continue
        filters = [('t', '>=', start // 1_000_000), ('t', '<', end // 1_000_000)]
        if instrument_id is not None:
            filters.append(('instrument_id', '=', int(instrument_id)))
        for row in pq.read_table(path, filters=filters).to_pylist():
            at = int(row['t']) * 1_000_000
            if at < start or at + base_seconds * SECOND > end:
                continue
            rows.append({**row, 'source_path': str(path), 'start': at,
                'end': at + base_seconds * SECOND,
                'known_at': at + base_seconds * SECOND})
        receipts.append({'path': str(path), 'sha256': file_digest(path)})
    return sorted(rows, key=lambda r: (r['start'], r['instrument_id'])), receipts


def aggregate_vendor(rows, seconds):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row['start'] // (seconds * SECOND) * seconds * SECOND,
                 row['instrument_id'])].append(row)
    result = {}
    for (start, instrument), members in grouped.items():
        members = sorted(members, key=lambda r: r['start'])
        if len({r['start'] for r in members}) != len(members):
            continue
        if any(r[k] is None for r in members for k in ('o', 'h', 'l', 'c', 'v')):
            continue
        end = start + seconds * SECOND
        result[(start, str(instrument))] = {
            'start': start, 'end': end, 'instrument_id': instrument,
            'O': D(str(members[0]['o'])), 'C': D(str(members[-1]['c'])),
            'H': max(D(str(r['h'])) for r in members),
            'L': min(D(str(r['l'])) for r in members),
            'V': sum(D(str(r['v'])) for r in members), 'known_at': end,
            'source_paths': sorted({r['source_path'] for r in members}),
            'source_bar_starts': [r['start'] for r in members],
            'source_clock': 'QuantPad published interval-start OHLCV; available at interval end',
        }
    return result


def reconcile_bar(native, published):
    """A different instrument, population, clock or known endpoint cannot fill a gap."""
    if published is None or not native.get('observed_complete'):
        return native
    if any(native.get(k) != published.get(k) for k in ('start', 'end')):
        return native
    if str(native['instrument_id']) != str(published['instrument_id']):
        return native
    if published['known_at'] > native['end']:
        return native
    if any(native.get(k) is None or D(str(native[k])) != published[k] for k in ('H', 'L', 'V')):
        return native
    if any(native.get(k) is not None and D(str(native[k])) != published[k] for k in ('O', 'C')):
        return native
    missing = [k for k in ('O', 'C') if native.get(k) is None]
    if not missing:
        return native
    result = dict(native)
    result.update({k: published[k] for k in missing})
    result.update(open_order_known=True, close_order_known=True, complete=True)
    result['endpoint_evidence'] = {
        'method': 'same-contract published OHLCV reconciled to native H/L/V and known endpoints',
        'resolved_fields': missing, 'native_endpoints': {k: native.get(k) for k in ('O', 'C')},
        'published': published, 'raw_tick_order_recovered': False,
    }
    return result


def batch_price(rows):
    """Execution VWAP of one timestamp batch; never invent within-batch order."""
    prices = {r['price'] for r in rows}
    if len(prices) == 1:
        return next(iter(prices))
    volume = sum(r['executed_size'] for r in rows)
    return sum(r['price'] * r['executed_size'] for r in rows) / volume if volume else None


class StrategyWindow(EventWindow):
    def __init__(self, document, *, schedule, owner):
        super().__init__(document, schedule=schedule)
        self.owner = owner
        self._vendor = {}
        self._resolved = {}
        self._authenticated = bool(document.get('plan', {}).get('owned_spans'))

    def bars(self, start, end, seconds=60):
        native = super().bars(start, end, seconds)
        if not self._authenticated or not any(r['O'] is None or r['C'] is None for r in native):
            return native
        if seconds not in self._vendor:
            rows, receipts = vendor_rows(str(self.owner.data_root), self.start, self.end,
                1 if seconds == 1 else 60, self.instrument_id)
            self._vendor[seconds] = aggregate_vendor(rows, seconds)
            self.owner.input_receipts.extend(r for r in receipts if r not in self.owner.input_receipts)
        result = []
        for row in native:
            key = (seconds, row['start'])
            if key not in self._resolved:
                self._resolved[key] = reconcile_bar(row,
                    self._vendor[seconds].get((row['start'], str(self.instrument_id))))
            result.append(self._resolved[key])
        return result

    def coverage(self, start, end):
        original = super().coverage(start, end)
        if original['observed_scope_complete'] or not self._authenticated:
            return original
        if start < self.start or end > self.end:
            return original
        if not self.series.get(60):
            return original
        from .event_cache import contract_at
        if any(str(contract_at(str(self.owner.data_root), at)['instrument_id']) != str(self.instrument_id)
               for at in (start, end - 1)):
            return original
        plan = self.document['plan']
        unowned = plan.get('unowned_intervals', [])
        def intersects(span):
            lo, hi = (span['start_ns'], span['end_ns']) if isinstance(span, dict) else span
            return lo < end and hi > start
        if any(intersects(span) for span in unowned):
            return original
        # Source ownership certifies the enumerated archive population, not an
        # exchange feed. Zero executions and partial minutes need no invented bar.
        invalid = [r for r in self.series.get(60, {}).values()
            if r['start'] < end and r['end'] > start and not r['observed_complete']]
        if invalid:
            return original
        return {**original, 'observed_scope_complete': True, 'unknown_intervals': [],
            'coverage_basis': 'fully enumerated canonical owned interval; no market-feed completeness claim',
            'strict_tick_coverage': original, 'market_coverage_complete': None}


def expired_chart_window(market, start, end):
    """Identify an empty c.0 chart interval after its mapped contract expired."""
    from .event_cache import contract_at
    path=Path(market.data_root)/'derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet'
    if not path.exists():
        return None
    contract=contract_at(market.data_root,start)
    expiry=contract.get('expiration_ts_utc')
    segment_end=contract.get('segment_end_exclusive_ms')
    if expiry is None or int(expiry.timestamp()*SECOND)>start or (segment_end is not None and segment_end*1_000_000<end):
        return None
    return {'start':start,'end':end,'instrument_id':contract['instrument_id'],
        'expiration_ns':int(expiry.timestamp()*SECOND),
        'reason':'mapped continuous contract expired before this empty chart window',
        'path':contract['roll_source_path'],'sha256':contract['roll_source_sha256']}


def published_prior_range(market, windows, kind, native_sessions=()):
    """Prior chart extrema from the owned continuous series, with rolls disclosed.

    This supplies price-range context only; it never fabricates a volume profile,
    depth, delta or a same-contract history that the archive did not retain.
    """
    selected, receipts, native_inputs, expired = [], [], [], []
    native_by_window={(s['window'].start,s['window'].end):s for s in native_sessions}
    for start, end in windows:
        rows, current = vendor_rows(str(market.data_root), start, end)
        if not rows:
            native=native_by_window.get((start,end))
            if not native or not native['coverage']['observed_scope_complete'] or not native['rows']:
                exclusion=expired_chart_window(market,start,end)
                if exclusion is None or native and native['rows']:
                    return None
                expired.append(exclusion)
                receipts.extend(r for r in current if r not in receipts)
                receipt={k:exclusion[k] for k in ('path','sha256')}
                if receipt not in receipts:receipts.append(receipt)
                continue
            win=native['window']
            rows=[{'start':r['start'],'end':r['end'],'known_at':r['known_at'],
                'instrument_id':win.instrument_id,'o':r['O'],'h':r['H'],'l':r['L'],'c':r['C'],'v':r['V'],
                'native_bar_id':r['bar_id'],'native_input_sha256':win.document['input_sha256']}
                for r in native['rows']]
            native_inputs.append(win.document['input_sha256'])
        selected.extend(rows)
        receipts.extend(r for r in current if r not in receipts)
    if not selected:
        return None
    selected.sort(key=lambda r: (r['start'], r['instrument_id']))
    if any(r[k] is None for r in selected for k in ('h', 'l', 'v')):
        return None
    if len({r['start'] for r in selected}) != len(selected):
        return None
    market.input_receipts.extend(r for r in receipts if r not in market.input_receipts)
    contracts = sorted({r['instrument_id'] for r in selected})
    identity = content_hash({'kind': kind, 'windows': windows, 'rows': selected})
    return {'id': 'published-prior-range:' + identity, 'start': windows[0][0],
        'end': windows[-1][1], 'known_at': windows[-1][1],
        'low': min(D(str(r['l'])) for r in selected), 'high': max(D(str(r['h'])) for r in selected),
        'open': None if selected[0]['o'] is None else D(str(selected[0]['o'])),
        'close': None if selected[-1]['c'] is None else D(str(selected[-1]['c'])),
        'volume': sum(D(str(r['v'])) for r in selected), 'complete': True,
        'coverage': {'observed_scope_complete': True, 'market_coverage_complete': None,
            'basis': 'all published prior RTH chart records; covered native execution bars supply missing published sessions'},
        'input_receipts': receipts, 'contract_ids': contracts,
        'native_supplement_input_sha256s':sorted(set(native_inputs)),
        'expired_continuous_chart_windows':expired,
        'price_basis': 'acquired unadjusted continuous chart; contract changes retained',
        'same_current_contract': contracts == [int(market.instrument_id)],
        'price_adjustment': None, 'members': [r['start'] for r in selected],
        'source_kind': 'published_ohlcv_range', 'not_a_volume_profile': True}
