"""Typed, replayable research operands into the existing method evaluator.

This boundary is separate from author/source admission: a frozen research
assumption may supply a semantic detector, but cannot certify author fidelity.
A report retains every operand and its native/record/policy derivation.
"""
from __future__ import annotations
from .catalog import PRIMARY
from .contracts import fields_for
from .expressions import evaluate
from .empirical_protocol import content_hash
from .protocol import jsonable
from .evidence import typed


class HistoricalEpisode:
    def __init__(self,market,method,branch,side,trigger,reference,*,predicate=None):
        self.market=market;self.method=method;self.branch=branch;self.side=side
        self.trigger=trigger;self.reference=reference
        self.predicate=predicate or PRIMARY[method]
        self.values={'branch':branch,'side':side}
        self.derivations={}
        self.stages=[]
        self.limitations=[]
        self.geometry={}
        self.identity={'method':method,'branch':branch,'predicate':self.predicate,'side':side,
            'session_date':str(market.day),'instrument_id':market.instrument_id,
            'reference_id':reference.get('id'),'trigger_id':trigger.get('bar_id',trigger.get('id')),
            'occurrence_at':trigger.get('start',trigger.get('at'))}
        self.id='native-v2:'+content_hash(self.identity)[:32]

    def bind(self,values,*,operation,parents=(),known_at=None,assumption=None,kind='market'):
        for field,value in values.items():
            if field in {'branch','side'} and value!=getattr(self,field):
                raise ValueError('historical binding changed selected '+field)
            if field not in fields_for(self.method) and field not in {'branch','side','decision_at'}:
                raise ValueError('unknown historical operand '+self.method+':'+field)
            if field in fields_for(self.method):value=typed(value,fields_for(self.method)[field].type,field)
            self.values[field]=value
            self.derivations[field]={'operation':operation,'parents':jsonable(list(parents)),
                'known_at':known_at,'assumption':assumption,'kind':kind,
                'recipes':list(fields_for(self.method)[field].recipes) if field in fields_for(self.method) else []}
        return self

    def missing(self,fields,reason,*,kind='input',evidence=None):
        self.bind({f:None for f in fields},operation=reason,kind=kind)
        self.limitations.append({'fields':list(fields),'kind':kind,'reason':reason,'evidence':evidence})
        return self

    def stage(self,name,at,*,observed=None,parents=(),details=None):
        self.stages.append({'stage':name,'at':at,'observed':observed,'parent_ids':list(parents),'details':details})
        return self

    def finish(self,*,decision_at,stop=None,target=None,entry=None):
        self.values['decision_at']=decision_at
        result=evaluate(self.method,self.predicate,self.values)
        source_result=result
        strategy=None
        if getattr(self.market,'reconstruct',False):
            from .strategy_policy import EXCLUDED, POLICY, observation_scope
            excluded=EXCLUDED.get(self.method,frozenset())
            result=evaluate(self.method,self.predicate,self.values,excluded_fields=excluded)
            scope=observation_scope(self.method,self.branch)
            strategy={'version':POLICY['version'],'scope':scope,'status':{True:'setup',False:'no_setup',None:'data_unavailable'}[result.value],
                'excluded_personal_fields':sorted(excluded),'failed_conditions':result.failed,'unavailable_conditions':result.unknown,
                'interpretation':'reconstructed strategy; not an author trade or recovered proprietary formula'}
            if scope!='entry_setup':strategy['status']={True:'condition_present',False:'condition_absent',None:'data_unavailable'}[result.value]

        missing=sorted(result.fields-set(self.values))
        if missing:
            raise ValueError(f'{self.method}/{self.branch} unimplemented selected operands: {missing}')
        for field,derivation in self.derivations.items():
            at=derivation['known_at']
            if field in result.fields and at is not None and at>decision_at:
                raise ValueError('future operand in historical assembly: '+field)
        self.geometry.update(entry=entry,stop=stop,target=target)
        # Actual source fidelity is deliberately not inherited from a research
        # context/confirmation policy, even when literal geometry agrees.
        verdict={True:'pass',False:'fail',None:'unknown'}[result.value]
        return jsonable({'schema':'phase1-historical-episode-v2','candidate_id':self.id,**self.identity,
            'decision_at':decision_at,'values':self.values,'operand_derivations':self.derivations,
            'selected_fields':sorted(result.fields),'stages':self.stages,'limitations':self.limitations,
            'research_verdict':verdict,'failed':result.failed,'unknown':result.unknown,
            'strategy_assessment':strategy,'source_contract_verdict':{True:'pass',False:'fail',None:'unknown'}[source_result.value],
            'author_exact_verdict':'unknown','faithful_eligible':False,'actual_trade':False,
            'reference':self.reference,'trigger':self.trigger,'geometry':self.geometry,
            'input_sha256':self.market.window.document['input_sha256'],
            'assembly_sha256':content_hash({'identity':self.identity,'values':self.values,'derivations':self.derivations})})


def absent(market,start,end,*,fields=(),seconds=60):
    if fields and any(row.get(field) is None for row in market.bars(start,end,seconds) for field in fields):
        return None
    return False if market.coverage(start,end)['observed_scope_complete'] else None


def window_result(market,method,branch,episodes,*,omissions=(),extra=False):
    counts={key:sum(r['research_verdict']==key for r in episodes) for key in ('pass','fail','unknown')}
    coverage=market.coverage(market.at('09:30'),market.end)
    limits=list(omissions)
    from .branch_coverage import external_for, EXTERNAL
    for key in external_for(method,branch,extra=extra):limits.append({'kind':'external_operand','id':key,**EXTERNAL[key]})
    reconstruction_scope=None
    if getattr(market,'reconstruct',False):
        from .strategy_policy import observation_scope
        reconstruction_scope=observation_scope(method,branch)
        for item in limits:
            if item.get('kind')=='external_operand':item['kind']='original_source_audit_requirement'
    return {'reconstruction_scope':reconstruction_scope,'method_id':method,'branch':branch,'extra_unit':extra,'session_date':str(market.day),
        'instrument_id':market.instrument_id,'population_scope':'owned_observed_events',
        'population_complete':coverage['observed_scope_complete'] and not omissions,
        'population_candidate_count':len(episodes) if coverage['observed_scope_complete'] and not omissions else None,
        'market_feed_completeness':None,'coverage':coverage,'N_observed':len(episodes),
        'n':counts['pass']+counts['fail'],'p':counts['pass'],'f':counts['fail'],'u':counts['unknown'],
        'episodes':episodes,'omissions':limits,'input_sha256':market.window.document['input_sha256']}


def close_selection_omissions(rows,selected,boundary,side):
    ambiguous=[r['bar_id'] for r in rows if (selected is None or r['start']<selected['start'])
        and r['C'] is None and (r['H']>boundary if side=='long' else r['L']<boundary)]
    return [{'kind':'input_ambiguity','reason':'earlier potential directional breakout close is unknown',
        'required_fields':['C'],'candle_ids':ambiguous,'side':side}] if ambiguous else []
