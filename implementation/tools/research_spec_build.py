#!/usr/bin/env python3
"""Render the research handoff; this does not implement or backtest strategies."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / 'planning/phase-1-live/research-spec'
FAMILIES = [('jumbo','J',25),('greenbird','G',11),('amt','A',18),('flow','F',18),('regime','R',4),('sires','S',9)]

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path, value): Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str)+'\n')
def cell(value):
    if not isinstance(value,str): value=json.dumps(value,ensure_ascii=False)
    return value.replace('|','\\|').replace('\n','<br>')

def inspect_data():
    import pyarrow.parquet as pq
    catalog_path=ROOT/'data/manifests/dataset-catalog.json'
    catalog=json.loads(catalog_path.read_text())
    wanted={
        'quantpad/cme__nq-continuous-futures__mbp-1',
        'quantpad/cme__nq-continuous-futures__trades',
        'quantpad/cme__nq-continuous-futures__ohlcv-1m',
        'quantpad/cme__es-continuous-futures__mbp-1',
        'quantpad/cme__es-continuous-futures__trades',
        'derived/continuous-futures__instrument-and-roll-maps',
        'free-sources/context__event-calendar__normalized',
        'free-sources/context__volatility__normalized',
        'free-sources/yahoo__cash-daily__normalized',
        'thetadata-opra/opra__ndxp-options__open-interest',
        'thetadata-opra/opra__ndxp-options__contracts',
        'thetadata-opra/opra__ndxp-options__quote-1m__dte14__strike-range70',
        'thetadata-opra/opra__qqq-options__trade-quote__dte7__strike-range42',
    }
    rows=[]
    for d in catalog['datasets']:
        if d['dataset_id'] not in wanted: continue
        directory=ROOT/'data'/d['archive_path']
        files=sorted(directory.glob('*.parquet'))
        row={k:d.get(k) for k in ['dataset_id','scope','observed_time_min','observed_time_max','status','known_gaps','timestamp_semantics']}
        row['directory_exists']=directory.is_dir()
        row['inspected_file']=str(files[-1].relative_to(ROOT)) if files else None
        if files:
            pf=pq.ParquetFile(files[-1])
            row['schema']=[{'name':f.name,'type':str(f.type)} for f in pf.schema_arrow]
            row['file_rows']=pf.metadata.num_rows
            row['file_bytes']=files[-1].stat().st_size
            row['sample_rows']=next(pf.iter_batches(batch_size=1)).to_pylist() if pf.metadata.num_rows else []
        rows.append(row)
    assert wanted=={r['dataset_id'] for r in rows}, wanted-{r['dataset_id'] for r in rows}
    dump(SPEC/'data_evidence.json', {'checked_at':datetime.now(timezone.utc).isoformat(), 'method':'Read archive manifest, Parquet metadata and one record per selected dataset; no full market-data rebuild or completeness certification.', 'catalog_sha256':sha(catalog_path),'catalog_dataset_count':len(catalog['datasets']), 'selected_datasets':rows})

def make_goldens():
    # Small specification arithmetic examples, not production strategy functions.
    cases=[
      {'id':'range_ladder','engine':'E01','operation':'range','input':{'H':120,'L':100,'k':0.5},'expected':{'W':20,'EQ':110,'upper':130,'lower':90}},
      {'id':'outer_band','engine':'E01','operation':'outer_band','input':{'H':120,'L':100,'near':1.33,'far':1.66},'expected':{'upper':[146.6,153.2],'lower':[66.8,73.4]}},
      {'id':'round_outward','engine':'E00','operation':'round','input':{'upper':101.13,'lower':98.87,'tick':0.25},'expected':{'upper':101.25,'lower':98.75}},
      {'id':'upward_golden_pocket','engine':'E08','operation':'pocket','input':{'A':100,'B':120},'expected':[107.64,110]},
      {'id':'downward_golden_pocket','engine':'E08','operation':'pocket','input':{'A':120,'B':100},'expected':[110,112.36]},
      {'id':'directional_EV','engine':'E04','operation':'EV','input':{'O':100,'u':0.02,'d':0.01,'k':0.5},'expected':{'U':102,'L':99,'W':3,'upper_extension':103.5}},
      {'id':'lower_P_zone','engine':'E04','operation':'P_zone','input':{'O':100,'q_near':0.02,'q_far':0.03},'expected':[97,98]},
      {'id':'smaller_excursion','engine':'E04','operation':'smaller_excursion','input':{'u':[2,8],'d':[8,2]},'expected':{'mean_min':2,'min_means':5}},
      {'id':'type7_quantile','engine':'E04','operation':'quantile','input':{'x':[0,10,20,30],'q':0.25},'expected':7.5},
      {'id':'trade_VWAP','engine':'E05','operation':'VWAP','input':{'prices':[100,102],'sizes':[1,1]},'expected':{'VWAP':101,'sigma':1}},
      {'id':'CVD_unknown_volume','engine':'E06','operation':'CVD','input':{'buy':100,'sell':70,'unknown':20},'expected':{'delta':30,'coverage':170/190,'quality':False}},
      {'id':'same_price_ratio','engine':'E05','operation':'ratio','input':{'own':35,'opposite':10,'threshold':3.5},'expected':True},
      {'id':'empty_ratio','engine':'E05','operation':'ratio','input':{'own':0,'opposite':0,'threshold':3.5},'expected':False},
      {'id':'steady_prints','engine':'E07','operation':'steady','input':{'sizes':[100,80,90,85],'fraction':0.8,'minimum':4},'expected':True},
      {'id':'thinning_prints','engine':'E07','operation':'steady','input':{'sizes':[100,79,90,85],'fraction':0.8,'minimum':4},'expected':False},
      {'id':'insufficient_prints','engine':'E07','operation':'steady','input':{'sizes':[100,100,100],'fraction':0.8,'minimum':4},'expected':None},
      {'id':'speed_elapsed_time','engine':'E06','operation':'speed','input':{'point_change':3.9,'tick':0.25,'elapsed_minutes':4},'expected':3.9},
      {'id':'second_transition_median','engine':'E03','operation':'median_run','input':{'volumes':[150,160,40,30,140,155]},'expected':{'median':145,'last_two_accepted':[False,True]}},
      {'id':'risk_multiple','engine':'E11','operation':'R','input':{'risk_ticks':20,'reward_ticks':30},'expected':1.5},
      {'id':'long_net_PnL','engine':'E11','operation':'PnL','input':{'entry':100,'exit':103,'direction':1,'multiplier':20,'fee':5,'R0':2},'expected':{'net_dollars':55,'net_R0':1.375}},
      {'id':'short_net_PnL','engine':'E11','operation':'PnL','input':{'entry':100,'exit':102,'direction':-1,'multiplier':20,'fee':5,'R0':2},'expected':{'net_dollars':-45,'net_R0':-1.125}},
      {'id':'parity_forward','engine':'E10','operation':'parity','input':{'K':100,'C':5,'P':4,'r':0,'T':1},'expected':101},
      {'id':'Black_forward_gamma','engine':'E10','operation':'gamma','input':{'F':100,'K':100,'sigma':0.2,'T':1,'r':0},'expected':0.01984762737385059},
      {'id':'gamma_dollars','engine':'E10','operation':'gamma_dollars','input':{'gamma':0.02,'OI':100,'multiplier':100,'X':100,'sign':-1},'expected':-20000},
      {'id':'VP_tie_expansion','engine':'E03','operation':'VP','input':{'prices':[100,101,102],'volumes':[10,20,10],'fraction':0.7},'expected':{'POC':101,'VAL':100,'VAH':102,'achieved_fraction':1.0}},
      {'id':'VP_POC_tie','engine':'E03','operation':'VP','input':{'prices':[100,101,102,103],'volumes':[2,10,10,2],'fraction':0.7},'expected':{'POC':101,'VAL':101,'VAH':102,'achieved_fraction':20/24}},
      {'id':'winter_clock','engine':'E00','operation':'clock','input':{'local':'2026-01-28T09:30:00','zone':'America/New_York'},'expected':'2026-01-28T14:30:00+00:00'},
      {'id':'summer_clock','engine':'E00','operation':'clock','input':{'local':'2026-07-10T09:30:00','zone':'America/New_York'},'expected':'2026-07-10T13:30:00+00:00'},
      {'id':'first_visit_independent','engine':'E01','operation':'visits','input':{'H':120,'L':100,'prices':[110,120,119,101]},'expected':{'high_first_index':1,'low_first_index':None}},
      {'id':'NWOG_forming_edge','engine':'E09','operation':'gap','input':{'Friday':100,'Sunday':110,'later':[110,111,110]},'expected':{'first_return_index':2,'full_fill_index':None}},
      {'id':'NWOG_immediate_penetration','engine':'E09','operation':'gap','input':{'Friday':100,'Sunday':110,'later':[110,109,100]},'expected':{'first_return_index':1,'full_fill_index':2}},
    ]
    dump(SPEC/'golden_cases.json', {'purpose':'Independent arithmetic examples for the specification; future implementation must pass its own behavioral tests. No market backtest is implied.','absolute_tolerance':1e-9,'cases':cases})

def build():
    records=[]
    for family,prefix,count in FAMILIES:
        rs=json.loads((SPEC/'models'/f'{family}.json').read_text())
        assert [r['id'] for r in rs]==[f'R-{prefix}{i:02}' for i in range(1,count+1)]
        records.extend(rs)
    master={'spec_version':'research-v1.0','status':'specified_not_implemented','scope':'85 non-Pine main models','user_decision_date':'2026-09-11','models':records,'shared_documents':['DATA_CONTRACTS.md','ENGINES.md','EXPERIMENT_PROTOCOL.md','IMPLEMENTATION_HANDOFF.md'],'grid_protocol':{'max_one_factor_configurations':32,'max_alpha_configurations_per_model':48,'interaction_axes':2,'selection_scope':'chronological training only'},'source_files':{str((SPEC/'models'/f'{f}.json').relative_to(ROOT)):sha(SPEC/'models'/f'{f}.json') for f,_,_ in FAMILIES}}
    dump(SPEC/'model_specs.json',master)
    out=['# All 85 model cards','', 'These are new research definitions, **specified but not implemented**. Read the [shared engines](ENGINES.md), [data contracts](DATA_CONTRACTS.md) and [experiment protocol](EXPERIMENT_PROTOCOL.md) first. JSON keys are literal configuration identifiers. Narrative bindings describe the exact selected objects, lifetimes and outcomes. A parameter with one allowed value is fixed; sensitivities described as diagnostic do not enter alpha selection.','',f'Total: {len(records)} models; {sum(len(r["parameters"]) for r in records)} declared parameters; {sum(r["grid_screen_config_count"] for r in records)} default/one-factor configurations before bounded interactions. No performance runs are reported.','']
    out+=['| Family | IDs | Count |','|---|---|---:|']
    for f,p,n in FAMILIES:out.append(f'| {f} | [R-{p}01](#r-{p.lower()}01)–R-{p}{n:02} | {n} |')
    out+=['','## Required family status tables','','| family | variant | n | faithful_disagreements | status | report path |','|---|---|---|---|---|---|']
    for f,p,n in FAMILIES:out.append(f'| {f} | research-v1 specification | not_run | not_applicable_research_definition | specified_not_implemented | [cards](#r-{p.lower()}01) |')
    out+=['','| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |','|---|---|---|---|---|---|---|']
    for r in records:out.append(f'| {r["family"]} | [{r["id"]}](#{r["id"].lower()}) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | {r["role"]}; {len(r["parameters"])} parameters |')
    for r in records:
        out+=['',f'<a id="{r["id"].lower()}"></a>',f'## {r["id"]} — {r["title"]}','',r['research_decision'],'',f'**Role:** {r["role"]}. **Inputs:** {", ".join(r["inputs"])}. **Engines:** {", ".join(r["engines"])}.']
        if r['dependencies']:out+=['', '**Build dependencies:** '+', '.join(f'[{x}](#{x.lower()})' for x in r['dependencies'])+'.']
        if r.get('conditional_inputs'):out+=['','**Conditional inputs:** '+cell(r['conditional_inputs'])+'.']
        if r.get('conditional_dependencies'):out+=['','**Conditional dependencies:** '+cell(r['conditional_dependencies'])+'.']
        if r['consumers']:out+=['','**Fixed consumers:** '+', '.join(f'[{x}](#{x.lower()})' for x in r['consumers'])+'.']
        out+=['','| Binding | Exact policy |','|---|---|']
        for k,v in r['bindings'].items():out.append(f'| `{k}` | {cell(v)} |')
        out+=['','| Parameter | Default | Allowed grid | Units / definition |','|---|---|---|---|']
        for k,v in r['parameters'].items():out.append(f'| `{k}` | {cell(v["default"])} | {cell(v["grid"])} | {cell(v["units"])} — {cell(v["meaning"])} |')
        out+=['','**Algorithm**','']+[f'{i}. {s}' for i,s in enumerate(r['algorithm'],1)]
        out+=['','**Model-specific outputs**','', '| Field | Type / unit |','|---|---|']
        for k,v in r['outputs'].items():out.append(f'| `{k}` | {cell(v)} |')
        out+=['','**Comparisons**','']+[f'- {s}' for s in r['controls']]
        out+=['','**Acceptance cases**','']+[f'- {s}' for s in r['acceptance_cases']]
        out+=['',f'**Missing input:** {r["unavailable_policy"]}. All shared prefix, mirror, lifetime and fill tests also apply.','',f'**Audit provenance:** [{r["id"]} source/old-code record](../../../{r["audit_record_file"]}); record SHA-256 `{r["audit_record_sha256"]}`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.']
    (SPEC/'MODEL_CARDS.md').write_text('\n'.join(out)+'\n')
    make_goldens()
    print(json.dumps({'model_count':len(records),'parameter_count':sum(len(r['parameters']) for r in records),'one_factor_configurations':sum(r['grid_screen_config_count'] for r in records),'signal_models':sum(r['role']=='signal' for r in records),'output':str(SPEC/'MODEL_CARDS.md')}))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--inspect-data',action='store_true')
    args=parser.parse_args()
    if args.inspect_data: inspect_data()
    build()
