"""Finite independent worked examples for design corrections; no strategy tests."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal as D
import ast
import json
import math

OUT=Path(__file__).resolve().parent
results=[]
def check(id,actual,expected,meaning,tol=None):
    ok=abs(float(actual)-float(expected))<=tol if tol is not None else actual==expected
    results.append({'id':id,'passed':bool(ok),'actual':str(actual),'expected':str(expected),'meaning':meaning})
    assert ok,(id,actual,expected)

# Literal account marks already include each charged fee exactly once.
net_marks=[D('0'),D('-5'),D('20'),D('100'),D('95')]
increments=[b-a for a,b in zip(net_marks,net_marks[1:])]
check('EXAMPLE-REWARD-01',sum(increments),D('95'),'Incremental marked-net reward telescopes to terminal net.')
check('EXAMPLE-REWARD-02',D('30')+D('80')>D('100'),True,'A shorter trade can leave valuable occupied-time capacity; all alternatives use the same boundary.')
check('EXAMPLE-REWARD-03',D('95')+D('75')==D('95'),False,'Adding complete-trade reward and overlapping continuation double counts value.')

def excursions(path):return max(path)-path[0],path[0]-min(path),path[-1]-path[0]
def first(path,up=2,down=-1):
    for x in path[1:]:
        if x>=up:return 'upper'
        if x<=down:return 'lower'
    return 'none'
a=[0,2,-1,1];b=[0,-1,2,1]
check('EXAMPLE-ORDER-01',excursions(a),excursions(b),'Identical excursions and endpoint do not identify order.')
check('EXAMPLE-ORDER-02',(first(a),first(b)),('upper','lower'),'The ordered labels must differ despite matching excursion summaries.')
check('EXAMPLE-HORIZON-01',11<=0+10,False,'Contact at minute nine and favorable passage at eleven is unresolved at the original minute-ten end.')
check('EXAMPLE-HORIZON-02',11<=9+10,True,'A new ten-minute contact-origin forecast has a different end and label.')

quotes=[{'event':0,'receipt':0,'ask':100},{'event':4,'receipt':6,'ask':102},{'event':10,'receipt':10,'ask':103}]
decision_time=3;arrival=5
decision_ask=max((q for q in quotes if q['receipt']<=decision_time),key=lambda q:q['event'])['ask']
venue_ask=max((q for q in quotes if q['event']<=arrival),key=lambda q:q['event'])['ask']
check('EXAMPLE-QUOTE-01',decision_ask,100,'The strategy cannot use the later venue quote before receipt.')
check('EXAMPLE-QUOTE-02',venue_ask,102,'At arrival the venue can have a changed standing quote not yet received locally.')
check('EXAMPLE-QUOTE-03',venue_ask==103,False,'A marketable fill is not delayed to the next quote update.')

# One N(0,1) prior and one unit-noise observation y=1: mean .5, variance .5.
observations=[('flow1',D('1')),('flow1',D('1'))]
unique=dict(observations);precision=D('1')+len(unique)
check('EXAMPLE-ASSIMILATION-01',sum(unique.values())/precision,D('.5'),'Identical evidence ID is assimilated once in this illustrative Gaussian model.')
check('EXAMPLE-ASSIMILATION-02',D('1')/precision,D('.5'),'Duplicate input must not create a second independent observation.')
check('EXAMPLE-GEOMETRY-01',D('99')<=D('103')<=D('101'),False,'The original physical band does not include a point admitted only by a wider uncertainty region.')
check('EXAMPLE-GEOMETRY-02',D('97')<=D('103')<=D('103'),True,'A declared scenario region is a distinct event definition, not a retroactive physical touch.')

vega=D('2')*D('100')*D('5')
check('EXAMPLE-VEGA-01',vega,D('1000'),'USD per unit annualized IV fraction.')
check('EXAMPLE-VEGA-02',vega*D('.01'),D('10'),'USD per one volatility percentage point.')
check('EXAMPLE-VEGA-03',-vega*D('.01'),D('-10'),'A sold trade reverses the signed vega-flow contribution.')
check('EXAMPLE-SKEW-01',D('.30')-D('.24'),D('.06'),'Put-minus-call skew uses a declared positive downside-richness convention.')
check('EXAMPLE-SKEW-02',(D('.30')+D('.24'))/2-D('.25'),D('.02'),'Butterfly curvature is distinct from the skew slope.')
w1=D('.2')**2*D('.1');w2=D('.3')**2*D('.2')
check('EXAMPLE-TERM-01',(w2-w1)/(D('.2')-D('.1')),D('.14'),'Interval total-variance difference is a variance proxy, not a difference of volatilities.')
check('EXAMPLE-RISK-01',D('1000')-D('300')-D('250')-D('20'),D('430'),'Headroom subtracts current net loss and incremental stop/cost exposure once.')
check('EXAMPLE-OI-01',(max(0,100-20),100+20),(80,120),'Synthetic no-exercise OI bounds do not identify a path or trade-level opening status.')
check('EXAMPLE-NONFILL-01',D('0'),D('0'),'No fill creates zero trade P&L absent an explicit order cost; a missed winner is an alternative-policy diagnostic.')

# Reuse only the isolated review pricing functions, without rerunning data reads.
module=ast.parse((OUT/'audit_vix_surface_feasibility.py').read_text())
selected=ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in {'normal_cdf','black','iv'}],type_ignores=[])
ns={'math':math};exec(compile(selected,'<review-pricing-functions>','exec'),ns)
# Independent ATM identity C=F*(2*Phi(sigma*sqrt(T)/2)-1), D=1.
price=20*math.erf(.1/math.sqrt(2))
check('EXAMPLE-IV-01',ns['iv'](price,20,20,.25,1,'CALL'),.4,'Bisection inversion agrees with an independent ATM closed-form identity.',1e-10)
check('EXAMPLE-IV-02',ns['iv'](price,20,20,.25,1,'PUT'),.4,'ATM put/call symmetry under the same forward convention.',1e-10)
check('EXAMPLE-IV-03',ns['iv'](-.1,20,20,.25,1,'CALL'),None,'Below-bound quotes have no admissible IV.')
check('EXAMPLE-IV-04',ns['iv'](20,20,20,.25,1,'CALL'),None,'A price at the strict upper bound has no finite IV in this convention.')

report={'status':'PASS','created_at':datetime.now(timezone.utc).isoformat(),'count':len(results),
        'scope':'Finite arithmetic, ordering and clock examples only. This does not test an implemented trading system, data feed, forecast model, policy or profit.',
        'results':results}
(OUT/'design_examples.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Verified finite design examples','',report['scope'],'',
       f"**{len(results)} explicit assertions passed.** These examples check the internal logic of the corrected specification and the small review-only IV inversion routine. They are not the thousands of proposed trading-system phase checks.",'',
       '| Example | Actual | Expected | Meaning |','|---|---|---|---|']
for r in results:lines.append(f"| {r['id']} | {r['actual']} | {r['expected']} | {r['meaning']} |")
lines += ['', '[Machine-readable results](design_examples.json). [Reproduction script](verify_design_examples.py).']
(OUT/'DESIGN_EXAMPLES.md').write_text('\n'.join(lines)+'\n')
print(f'PASS: {len(results)} finite design-example assertions; no strategy tests.')
