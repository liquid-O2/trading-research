"""Upstream synthetic reaction/HVN provenance regression; not market performance."""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import importlib.util,json,sys
from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.event_time import aggregate_events,EventWindow,VERSION,CONTRACT
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.historical_auction_scanners import scan_member
from trading_research.research.method_pack.historical_runner import load_registry,immutable_json,serializable
from trading_research.research.method_pack.native_resolution import file_digest
root=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('upstream_controls','/workspace/implementation/tests/test_phase1_historical_replay.py')
f=importlib.util.module_from_spec(spec);sys.modules[spec.name]=f;spec.loader.exec_module(f)
prior_day=f.DAY-timedelta(days=1);start=clock(prior_day,'09:30');split=clock(prior_day,'12:45');end=clock(prior_day,'16:00')
prices=[104,105,110,106,104,100,103,106,109,106,103,101,103,105]
events=[f.raw(start+i*5*f.MINUTE+f.SECOND,p,index=i) for i,p in enumerate(prices)]
events += [f.raw(split+f.MINUTE,110,100,index=100),f.raw(split+2*f.MINUTE,109.75,1,index=101),f.raw(split+3*f.MINUTE,110.25,1,index=102)]
def window(rows):
    doc=aggregate_events(rows,start,end,17)
    doc.update(schema=VERSION,contract_sha256=content_hash(CONTRACT),instrument_id=17,start_ns=start,end_ns=end,
        input_sha256=content_hash(doc),plan={'unowned_intervals':[]})
    return EventWindow(doc)
def current(prior):
    rows=[dict(r,price=210-r['price'],side={'B':'A','A':'B'}.get(r['side'],r['side'])) for r in f.flow_events() if r['event_ns']>=f.TOUCH]
    m=f.Market(rows)
    m.prior=lambda kind:{'sessions':[{'day':str(prior_day),'window':prior}],'omissions':[]}
    return m
control=scan_member(current(window(events)),'resistance_short')
assert len(control['episodes'])==1,control
observation=control['episodes'][0]
assert observation['values']['independent_minor_hvn_known'] is True
assert observation['research_verdict']=='pass',observation['values']
# Move every HVN print into the reaction interval. The same price and quantity
# may no longer instantiate an independently formed later-profile reason.
mutated=[dict(r,event_ns=start+75*f.MINUTE+(r['event_ns']-split),known_at=start+75*f.MINUTE+(r['event_ns']-split)) if r['event_ns']>=split else r for r in events]
rejected=scan_member(current(window(mutated)),'resistance_short')
assert not rejected['episodes']
reg,_=load_registry(root)
result={'kind':'upstream_synthetic_independent_reaction_hvn_regression','status':'pass',
    'registry_sha256':reg['registry_sha256'],'software_sha256':reg['software']['sha256'],
    'probe_path':str(Path(__file__).resolve()),'probe_sha256':file_digest(Path(__file__)),
    'input_sha256':content_hash(serializable(events)),'positive':observation,
    'same_period_mutation_observations':0,'native_market_performance_claim':False}
immutable_json(root/'validation/member-independence.json',result)
print('Independent disjoint-period HVN passes; same-period reuse rejected.')
