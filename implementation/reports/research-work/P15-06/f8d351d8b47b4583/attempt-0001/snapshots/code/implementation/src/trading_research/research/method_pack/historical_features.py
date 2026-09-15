"""Causal market features shared by historical method scanners.

All market members come from the owned event-time adapter. Research selection
assumptions are explicit; domain recipe results retain their original evidence
class and never become claims about an author's actual selection or orders.
"""
from __future__ import annotations
from collections import defaultdict, OrderedDict
from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache

from .branch_coverage import setting
from .empirical_market import clock
from .empirical_protocol import content_hash
from .event_cache import cached_window, contract_at, ownership
from .event_time import EventWindow, BookObservations, MINUTE, SECOND
from .mbp1_views import iter_mbp1_window, plan_window
from .native_resolution import NativeEvidenceError
from .protocol import RECIPES, jsonable
from .session_policy import NQSessionPolicy
from . import objects  # register existing domain recipes

Q = Decimal('.25')
D = Decimal


def sign(side):
    return 1 if side == 'long' else -1


def recipe(rid, inputs):
    result = RECIPES[rid](inputs)
    return {'recipe_id': rid, 'inputs': inputs, 'result': jsonable(asdict(result)),
            'derivation_sha256': content_hash({'recipe': rid, 'inputs': inputs})}


def span(rows, start, end, identity, *, coverage=None):
    if not rows:
        return None
    return {'id': identity, 'start': start, 'end': end, 'known_at': max(end, max(r['known_at'] for r in rows)),
            'low': min(r['L'] for r in rows), 'high': max(r['H'] for r in rows),
            'open': rows[0]['O'], 'close': rows[-1]['C'], 'volume': sum(r['V'] for r in rows),
            'members': [r['bar_id'] for r in rows], 'coverage': coverage,
            'complete': all(r['observed_complete'] for r in rows)}


def pivots(bars, n=None):
    """Strict extrema, confirmed only after n subsequent completed bars."""
    n = setting('balance')['pivot_bars'] if n is None else n
    result = []
    for i in range(n, len(bars)-n):
        group = bars[i-n:i+n+1]
        if any(not r['observed_complete'] for r in group) or any(a['end'] != b['start'] for a,b in zip(group,group[1:])):
            continue
        row = bars[i]
        for side, key, op in [('high','H',max), ('low','L',min)]:
            values = [r[key] for r in group]
            if row[key] == op(values) and values.count(row[key]) == 1:
                result.append({'id': row['bar_id'] + ':' + side, 'side': side, 'price': row[key],
                    'at': row['end'], 'known_at': group[-1]['known_at'], 'members': [r['bar_id'] for r in group]})
    return sorted(result, key=lambda r: (r['known_at'],r['side']))


def balances(bars, prior_width=None):
    """Four alternating confirmed swings, with repeated tests of both edges."""
    ps = pivots(bars)
    alternating = []
    output = []
    config = setting('balance')
    for p in ps:
        if alternating and p['side'] == alternating[-1]['side']:
            old = alternating[-1]
            if p['price'] > old['price'] if p['side'] == 'high' else p['price'] < old['price']:
                alternating[-1] = p
            continue
        alternating.append(p)
        selected = alternating[-config['alternating_pivots']:]
        if len(selected) < config['alternating_pivots']:
            continue
        lo = min(r['price'] for r in selected); hi = max(r['price'] for r in selected); width = hi-lo
        if width <= 0 or prior_width is not None and width > prior_width * D(config['max_width_prior_fraction']):
            continue
        tolerance = width * D(config['edge_tolerance_fraction'])
        if any((hi-r['price'] if r['side']=='high' else r['price']-lo) > tolerance for r in selected):
            continue
        output.append({'id': 'balance:' + content_hash(selected), 'low': lo, 'high': hi, 'width': width,
            'start': min(r['at'] for r in selected), 'end': p['known_at'], 'known_at': p['known_at'],
            'pivots': selected, 'selection': 'A2-BALANCE'})
    return output


class HistoricalFeatures:
    def __init__(self, day, *, data_root='/workspace/data', document=None, records=None):
        self.day = date.fromisoformat(day) if isinstance(day,str) else day
        self.data_root = data_root
        self.policy = NQSessionPolicy()
        self.records = records or {}
        self.reconstruct = bool(self.records.get("strategy_reconstruction"))
        if self.reconstruct:
            from .session_policy import ReconstructionSessionPolicy
            self.policy = ReconstructionSessionPolicy()
        self.input_receipts = []
        if document is None:
            instrument = contract_at(data_root,clock(self.day,'09:30'))
            document,receipt = cached_window(data_root,clock(self.day-timedelta(days=1),'18:00'),
                clock(self.day,'16:00'),instrument['instrument_id'])
            self.input_receipts.append(receipt)
        if self.reconstruct:
            from .strategy_measurements import StrategyWindow
            self.window = StrategyWindow(document,schedule=self.policy,owner=self)
        else:
            self.window = EventWindow(document,schedule=self.policy)
        self.instrument_id = self.window.instrument_id
        self.start,self.end = self.window.start,self.window.end
        self._earlier = {}
        self._local = OrderedDict()
        self._profiles = {}
        self._vwap = {}
        self._ranges = {}
        self.domain_observations = {}

    def at(self,text,offset=0):
        return clock(self.day+timedelta(days=offset),text)

    def bars(self,start,end,seconds=60):
        if start < self.start or end > self.end or end <= start:
            return []
        return self.window.bars(start,end,seconds)

    def coverage(self,start,end):
        return self.window.coverage(start,end)

    def range(self,start,end,label):
        key=start,end,label
        if key not in self._ranges:
            self._ranges[key] = span(self.bars(start,end),start,end,
                f'{label}:{self.instrument_id}:{start}:{end}',coverage=self.coverage(start,end))
        return self._ranges[key]

    def profile(self,start,end,fraction='.70'):
        from .empirical_tape import _profile_payload
        key=start,end,fraction
        if key not in self._profiles:
            accum=defaultdict(lambda:[D(0),D(0),D(0)])
            members=[]
            for at,r in self.window.footprints.items():
                if at>=start and r['end']<=end and r['known_at']<=end:
                    members.append(at)
                    for px,b,a,u in r['rows']:
                        for i,v in enumerate((b,a,u)):accum[px][i]+=v
            p=_profile_payload(accum,tick=Q,tie_policy='lowest',value_area={'fraction':D(fraction),
                'algorithm':'contiguous_larger_adjacent_volume_tie_both','tie_policy':'both'},
                complete=self.coverage(start,end)['observed_scope_complete'])
            p.update(id=f'profile:{self.instrument_id}:{start}:{end}:{fraction}',known_at=end,start=start,end=end,
                minute_members=members,fraction=fraction,coverage=self.coverage(start,end))
            p['value_area_config_id']=f'event-v2-va-{fraction}-tie-both'
            self._profiles[key]=p
        return self._profiles[key]

    def vwap(self,at):
        if at not in self._vwap:self._vwap[at]=self.window.vwap(self.start,at)
        return self._vwap[at]

    def prior(self,kind='day'):
        """Exact calendar membership, bounded lookback, same contract only."""
        if kind in self._earlier:return self._earlier[kind]
        if kind == 'day':
            policy=self.policy.previous_session(self.day)
            days=[date.fromisoformat(policy['date'])]
        else:
            end = self.day-timedelta(days=self.day.weekday()) if kind=='week' else self.day.replace(day=1)
            start = end-timedelta(days=7) if kind=='week' else (end-timedelta(days=1)).replace(day=1)
            days=[start+timedelta(days=i) for i in range((end-start).days)]
        docs=[]; omissions=[]; range_windows=[]
        for day in days:
            calendar=self.policy.rth(day)
            if not calendar['known']:
                omissions.append({'date':str(day),'reason':'calendar_unverified','required_input':calendar.get('required_input')})
            if not calendar['windows']:continue
            if (self.day-day).days>62:
                omissions.append({'date':str(day),'reason':'outside_frozen_lookback'});continue
            for start,end in calendar['windows']:
                range_windows.append((start,end))
                # The acquired front map selects scope. It does not authorize a
                # different instrument's prices to stand in for prior history.
                doc,receipt=cached_window(self.data_root,start,end,self.instrument_id,seconds=(60,300,1800))
                self.input_receipts.append(receipt)
                if self.reconstruct:
                    from .strategy_measurements import StrategyWindow
                    win=StrategyWindow(doc,schedule=self.policy,owner=self)
                else:
                    win=EventWindow(doc,schedule=self.policy)
                rows=win.bars(start,end)
                cov=win.coverage(start,end)
                if not cov['observed_scope_complete']:
                    omissions.append({'date':str(day),'reason':'same_contract_prior_scope_unknown',
                        'instrument_id':self.instrument_id,'observed_rows':len(rows),'coverage':cov})
                docs.append({'day':str(day),'window':win,'rows':rows,'coverage':cov})
        rows=[r for d in docs for r in d['rows']]
        result={'kind':kind,'sessions':docs,'omissions':omissions,'scope_complete':not omissions,
            'range':span(rows,min((r['start'] for r in rows),default=0),max((r['end'] for r in rows),default=0),
                f'prior_{kind}:{self.instrument_id}:{self.day}',coverage={'observed_scope_complete':not omissions})}
        if self.reconstruct and (omissions or result['range'] is None) and range_windows:
            from .strategy_measurements import published_prior_range
            fallback=published_prior_range(self,range_windows,kind,native_sessions=docs)
            if fallback is not None:
                result['native_range']=result['range']
                result['range']=fallback
                result['range_scope_complete']=True
        self._earlier[kind]=result
        return result

    def local(self,start,end,*,book=False):
        """Exact raw local membership; never reuse a future-containing summary."""
        key=start,end,book
        if key not in self._local:
            if start<self.start or end>self.end:raise NativeEvidenceError('local observation outside admitted day')
            plan=plan_window(self.data_root,start,end,ownership=ownership(str(self.data_root)))
            rows=list(iter_mbp1_window(plan,trades_only=not book,instrument_id=self.instrument_id))
            for r in rows:r['event_id']=f"{r['source_file']}:{r['source_row']}"
            if len(rows) > 50000:
                return rows
            self._local[key]=rows
            while sum(len(v) for v in self._local.values()) > 100000:
                self._local.popitem(last=False)
        return self._local[key]

    def domain(self,rid,inputs):
        record=recipe(rid,inputs)
        self.domain_observations[record['derivation_sha256']]=record
        return record['result']['value']

    def supplied(self,kind,at):
        rows=[r for r in self.records.get(kind,[]) if r.get('known_at',at+1)<=at
              and str(r.get('instrument_id',self.instrument_id))==str(self.instrument_id)]
        for r in rows:
            if not r.get('evidence_path') or not r.get('evidence_sha256'):
                raise NativeEvidenceError('supplied record requires actual evidence identity')
            from pathlib import Path
            from .native_resolution import file_digest
            if file_digest(Path(r['evidence_path']))!=r['evidence_sha256']:
                raise NativeEvidenceError('supplied record evidence changed')
            import json
            path=Path(r['evidence_path'])
            doc=json.loads(path.read_text())
            members=doc if isinstance(doc,list) else doc.get('records',[doc])
            actual={k:v for k,v in r.items() if k not in {'evidence_path','evidence_sha256'}}
            if actual not in members:
                raise NativeEvidenceError('supplied record absent from identified evidence contents')
        return rows


def first_contact(rows,lo,hi,*,after=None):
    return next((r for r in rows if (after is None or r['start']>=after) and r['L']<=hi and r['H']>=lo),None)


def distinct_contacts(rows,lo,hi,departure=Q*4):
    ready=True
    for row in rows:
        if row['L']<=hi and row['H']>=lo:
            if ready:yield row;ready=False
        elif row['L']>hi+departure or row['H']<lo-departure:
            ready=True


def delta(market,start,end):
    rows=[r for at,r in market.window.footprints.items() if at>=start and r['end']<=end and r['known_at']<=end]
    return sum(b-a for r in rows for px,b,a,u in r['rows']) if rows else None
