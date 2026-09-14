"""Rebuild the real market with HistoricalFeatures and re-check every
absence window / comparison behind the sampled rejections on chosen dates."""
import json,os,sys,datetime
from decimal import Decimal as D
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.historical_assembly import absent
S=os.environ['SCRATCH']
A=json.load(open(S+'/sampleA.json'));B=json.load(open(S+'/sampleB.json'))
for r in A:r['sample']='A'
for r in B:r['sample']='B'
DATES=sys.argv[1:]
rows=[r for r in A+B if r['date'] in DATES]
out=[];cache={}
def mkt(d):
    if d not in cache:
        cache[d]=HistoricalFeatures(datetime.date.fromisoformat(d),data_root='/workspace/data',
                                    records={'strategy_reconstruction':True})
    return cache[d]
ABS={
 'JJ-TBR':{'source_confirmation':('trig_start','decision'),'reaction_side_confirmed':('trig_start','decision')},
 'SAINT-AMT':{'same_boundary_retest_held':('trig_end','decision'),'original_balance_reaccepted':('trig_end','decision'),
   'aggressive_poc_passage':('trig_end','decision'),'older_value_tested':('trig_start','decision'),
   'older_value_rejected':('trig_start','decision'),'prior_buying_at_upper_extreme':('ref_known','trig_start'),
   'two_distinct_prior_failures':('ref_known','trig_start'),
   'control_evidence_recorded':('csw0','csw1'),'local_control_confirms_return':('csw0','csw1'),
   'repeated_body_selling':('csw0','csw1'),'repeated_aggression_in_trade_direction':('csw0','csw1')},
 'KEANI-OPEN-ABOVE-VALUE':{k:('a_end','limit') for k in
   ('developing_value_builds_higher','source_rejection_observed','aggressive_buy_imbalance_break',
    'time_of_day_allowed','buyers_defend_same_imbalance_band','dom_supports_long')},
 'GB-VWAP':{'continuation_context':('trig_end','decision')},
}
n=0
for r in rows:
    m=mkt(r['date'])
    def pt(tag):
        if tag=='trig_start':return r['trig'].get('start') or r['occurrence_at']
        if tag=='trig_end':return r['trig'].get('end')
        if tag=='decision':return r['decision_at']
        if tag=='ref_known':return r['ref'].get('known_at')
        if tag=='csw0':return (r.get('csw') or [None,None])[0]
        if tag=='csw1':return (r.get('csw') or [None,None])[1]
        if tag=='a_end':return m.at('10:00')
        if tag=='limit':return m.at('11:00')
    for c in (r['failed'] or []):
        base=c.split()[0].replace('NOT','').strip()
        spec=ABS.get(r['method'],{}).get(base)
        if not spec:continue
        a,b=pt(spec[0]),pt(spec[1])
        if a is None or b is None:
            out.append(dict(sample=r['sample'],date=r['date'],method=r['method'],branch=r['branch'],cid=r['cid'],
                conjunct=c,window=None,note='window bound unavailable'));n+=1;continue
        cov=m.coverage(a,b)['observed_scope_complete'] if b>=a else None
        out.append(dict(sample=r['sample'],date=r['date'],method=r['method'],branch=r['branch'],cid=r['cid'],
            conjunct=c,window_ns=b-a,window_s=(b-a)/1e9,coverage_complete=cov,
            absent_value=(absent(m,a,b) if b>=a else None)));n+=1
json.dump(out,open(S+'/market_checks.json','w'),indent=0)
print('checked',n,'absence conjuncts over',len(rows),'rejections on',len(DATES),'dates')
import collections
print(collections.Counter((x.get('window_ns')==0, x.get('coverage_complete')) for x in out))
zero=[x for x in out if x.get('window_ns')==0]
print('zero-length windows:',len(zero))
for x in zero[:12]:print('   ',x['date'],x['method'],x['branch'],x['conjunct'],'absent->',x['absent_value'])
