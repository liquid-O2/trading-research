"""Native bar context, fixed references and comparison-to-method assembly."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal

from .clocks import et_ns, ns_to_et
from .empirical_native import WindowPrefixResolver, native_object
from .empirical_protocol import content_hash
from .empirical_selectors import MINUTE, compact_bar
from .native_windows import collect_window
from .protocol import jsonable


def clock(day, text):
    hour, minute = map(int, text.split(':'))
    return et_ns(day, hour, minute)


def previous_weekday(day):
    day -= timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


def prior_period_days(day, kind):
    if kind == 'day':
        return [previous_weekday(day)]
    if kind == 'week':
        first = day-timedelta(days=day.weekday()+7)
        last = first+timedelta(days=7)
    elif kind == 'month':
        last = day.replace(day=1)
        first = (last-timedelta(days=1)).replace(day=1)
    else:
        raise ValueError('unknown prior period')
    return [first+timedelta(days=i) for i in range((last-first).days)
            if (first+timedelta(days=i)).weekday() < 5]


class BarMarket:
    """One instrument/date partition with bounded lookback and typed producers."""
    def __init__(self, partition, data_root='/workspace/data'):
        self.partition = dict(partition)
        self.day = date.fromisoformat(partition['session_date'])
        self.instrument_id = partition['instrument_id']
        self.dataset_id = partition.get('dataset_id','quantpad/cme__nq-continuous-futures__ohlcv-1m')
        # The frozen coverage manifest covers the maximum full prior-month dependency.
        # A preceding month that extends beyond this cap remains incomplete;
        # it cannot silently borrow earlier unmanifested observations.
        self.start = clock(self.day-timedelta(days=62),'00:00')
        self.end = clock(self.day,'16:00')
        self.window = collect_window(data_root,self.dataset_id,self.start,self.end,self.instrument_id,required='ohlcv')
        self.resolver = WindowPrefixResolver([self.window])
        self.rows = tuple(self.window.rows)
        self.index = {r['start']:r for r in self.rows}
        if len(self.index) != len(self.rows):
            raise ValueError('duplicate native minute keys in partition')
        self.objects = {}
        self.object_results = {}
        self._bars = {}
        self._ranges = {}
        self._vwap = {}

    def members(self,start,end):
        return [self.index[t] for t in range(start,end,MINUTE) if t in self.index]

    def object(self, method, branch, recipe, start, end, inputs=None, label=None):
        key = method,branch,recipe,start,end,content_hash(inputs or {}),label
        oid = f'{method}:{branch}:{recipe}:{label or "native"}:{self.instrument_id}:{start}:{end}'
        if key not in self.object_results:
            rows = self.members(start,end)
            if not rows:
                return None, None
            obj,result = native_object(self.resolver,rows,object_id=oid,recipe_id=recipe,
                method_id=method,branch=branch,instrument_id=self.instrument_id,start=start,end=end,inputs=inputs)
            if result.base_ok is False:
                raise ValueError(f'invalid native empirical object {oid}: {result.reason}')
            self.objects[oid]=obj
            self.object_results[key]=obj,result
        return self.object_results[key]

    def bars(self,start,end,minutes=1):
        key=start,end,minutes
        if key in self._bars:return self._bars[key]
        duration=minutes*MINUTE
        if start % duration or end % duration:
            raise ValueError('bar scan bounds must align to requested native clock')
        result=[]
        for at in range(start,end,duration):
            # Producer identity here is a storage owner. A method-specific
            # envelope is rematerialized and replayed when assembling a candidate.
            obj,value=self.object('GB-FAIL','previous_hour','O004',at,at+duration,
                {'kind':'time','size_minutes':minutes},label='cache')
            if value is None:
                bar={'bar_id':f'{self.instrument_id}:{at}:{at+duration}','instrument_id':self.instrument_id,
                     'start':at,'end':at+duration,'known_at':at+duration,'complete':False,
                     'O':None,'H':None,'L':None,'C':None,'V':None}
            else:bar=deepcopy(value.value)
            result.append(bar)
        self._bars[key]=result
        return result

    def range_reference(self,rule,start,end,*,recipe='O046',label='range',require_inside=False):
        method,branch=rule['method_id'],rule['branch']
        refid=f'{method}:{branch}:{label}:{self.instrument_id}:{start}:{end}'
        inputs={'range_id':refid}
        if recipe=='O048':inputs.update(period_id=refid,period_kind=label,period_scope='frozen_research_RTH',period_end=end)
        obj,result=self.object(method,branch,recipe,start,end,inputs,label=label)
        if result is None:
            return {'reference_id':refid,'instrument_id':self.instrument_id,'known_at':end,
                    'formation_start':start,'formation_end':end,'complete':False,
                    'high':None,'low':None,'object_ids':[], 'missing':['no_native_reference_members']}
        value=result.value
        high=value.get('H',value.get('box_high',value.get('prior_high')))
        low=value.get('L',value.get('box_low',value.get('prior_low')))
        return {'reference_id':refid,'instrument_id':self.instrument_id,'known_at':result.known_at,
                'formation_start':start,'formation_end':end,'complete':result.coverage_ok is True and high is not None and low is not None,
                'high':high,'low':low,'object_ids':[obj['object_id']],
                'require_inside_box':require_inside,'source_holes':result.hole_ids}

    def prior_reference(self,rule,kind='day'):
        days=prior_period_days(self.day,kind)
        references=[self.range_reference(rule,clock(day,'09:30'),clock(day,'16:00'),
                    recipe='O048' if rule['method_id']=='GB-FAIL' else 'O046',label='prior_'+kind) for day in days]
        refid=f'{rule["rule_id"]}:{self.instrument_id}:prior-{kind}:{days[0]}:{days[-1]}'
        complete=all(r['complete'] for r in references)
        return {'reference_id':refid,'instrument_id':self.instrument_id,
                'known_at':max(r['known_at'] for r in references),
                'formation_start':references[0]['formation_start'],'formation_end':references[-1]['formation_end'],
                'complete':complete,'high':max(r['high'] for r in references) if complete else None,
                'low':min(r['low'] for r in references) if complete else None,
                'constituent_reference_ids':[r['reference_id'] for r in references],
                'object_ids':[oid for r in references for oid in r['object_ids']],
                'expected_weekdays':[str(d) for d in days],
                'missing_reference_dates':[str(d) for d,r in zip(days,references) if not r['complete']],
                'calendar_policy':'All prior calendar weekdays required; no unsupported holiday-closure or roll stitching.'}

    def minute_open_reference(self,rule,at,label):
        obj,result=self.object(rule['method_id'],rule['branch'],'O004',at,at+MINUTE,
                               {'kind':'time','size_minutes':1},label=label)
        value=None if result is None else result.value
        price=None if value is None else value['O']
        return {'reference_id':f'{rule["rule_id"]}:{label}:{self.instrument_id}:{at}',
                'instrument_id':self.instrument_id,'known_at':at+MINUTE,
                'formation_start':at,'formation_end':at+MINUTE,
                'high':price,'low':price,'complete':value is not None and value['complete'],
                'object_ids':[] if obj is None else [obj['object_id']],
                'reference_definition':'native one-minute open, available at minute end; no exact source opening execution inferred'}

    def vwap(self,rule,at):
        key=rule['rule_id'],at
        if key in self._vwap:return self._vwap[key]
        reset=clock(self.day-timedelta(days=1),'18:00')
        obj,result=self.object(rule['method_id'],rule['branch'],'O030',reset,at,
            {'variant':'comparison','basis':'HLC3','reset_at':reset,
             'reset_id':f'comparison-18:{self.instrument_id}:{self.day}',
             'reset_verified':False,'source_basis_verified':False},label='vwap')
        if result is None or result.coverage_ok is not True or result.known_at != at:
            value=None
        else:
            value={'price':result.value['comparison_vwap'],
                   'variance':result.value['weighted_variance_population'],
                   'known_at':at,'object_id':obj['object_id'],'source_faithful':False}
        self._vwap[key]=value
        return value

    def source_assembly(self,rule,opportunity,registry):
        """Run the accepted C01/native assembler; retain absent source gates.

        The opportunity clock is a research observation, never an O150 actual
        decision. The full method evaluator therefore cannot acquire private
        admission, thesis, risk, order or fill evidence from this comparison.
        """
        from .assembly import assemble_episode
        from .catalog import objects_for
        candidate={'candidate_id':opportunity.opportunity_id,'rule_id':rule['rule_id'],
            'registry_version':registry['version'],'registry_sha256':registry['registry_sha256'],
            'assumption_ids':rule['assumption_ids'],'method_id':rule['method_id'],'branch':rule['branch'],
            'side':opportunity.side,'instrument_id':self.instrument_id,'session_date_et':str(self.day),
            'decision_at':opportunity.available_at,'band_ids':[opportunity.reference_id],
            'cohort_id':self.partition['partition_id'],'evidence_mode':'research_comparison',
            'variant':'comparison','faithful_eligible':False,'object_ids':[],'assertion_ids':[], 'operands':{}}
        size=(opportunity.trigger['end']-opportunity.trigger['start'])//MINUTE
        trigger,_=self.object(rule['method_id'],rule['branch'],'O004',opportunity.trigger['start'],
                opportunity.trigger['end'],{'kind':'time','size_minutes':size},label='opportunity')
        oids=list(dict.fromkeys([*(opportunity.reference.get('object_ids') or []),
                                *([] if trigger is None else [trigger['object_id']])]))
        allowed=objects_for(rule['method_id'])
        objects=[self.objects[oid] for oid in oids if self.objects[oid]['recipe_id'] in allowed
                 and self.objects[oid]['formation_end'] <= opportunity.available_at]
        candidate['object_ids']=[o['object_id'] for o in objects]
        from .empirical_binding import selected_bindings
        bindings,roles=selected_bindings(rule,objects,candidate)
        assembled=assemble_episode(candidate,objects,bindings=bindings,roles=roles,resolver=self.resolver)
        if assembled.result.get('faithful_eligible') is not False or assembled.result['detected_causal_violations']:
            raise ValueError('comparison source assembly violated causal/faithfulness boundary')
        return assembled
