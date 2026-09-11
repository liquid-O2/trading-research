#!/usr/bin/env python3
"""Validate the handoff and arithmetic; never imply models were backtested."""
from __future__ import annotations
import hashlib,json,math,re,statistics,sys
import jsonschema
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import unquote
from zoneinfo import ZoneInfo
from research_spec_build import ROOT,SPEC,FAMILIES,sha,dump

def quantile(x,q):
    x=sorted(x); h=(len(x)-1)*q; lo=math.floor(h); hi=math.ceil(h)
    return x[lo]+(h-lo)*(x[hi]-x[lo])

def calculate(op,x):
    if op=='range':
        w=x['H']-x['L'];return dict(W=w,EQ=(x['H']+x['L'])/2,upper=x['H']+x['k']*w,lower=x['L']-x['k']*w)
    if op=='outer_band':
        w=x['H']-x['L'];return dict(upper=[x['H']+x['near']*w,x['H']+x['far']*w],lower=[x['L']-x['far']*w,x['L']-x['near']*w])
    if op=='round':return dict(upper=math.ceil(x['upper']/x['tick'])*x['tick'],lower=math.floor(x['lower']/x['tick'])*x['tick'])
    if op=='pocket':return sorted([x['B']-k*(x['B']-x['A']) for k in [0.5,0.618]])
    if op=='EV':
        u=x['O']*(1+x['u']);l=x['O']*(1-x['d']);return dict(U=u,L=l,W=u-l,upper_extension=u+x['k']*(u-l))
    if op=='P_zone':return sorted([x['O']*(1-x[k]) for k in ['q_near','q_far']])
    if op=='smaller_excursion':return dict(mean_min=statistics.mean(min(u,d) for u,d in zip(x['u'],x['d'])),min_means=min(statistics.mean(x['u']),statistics.mean(x['d'])))
    if op=='quantile':return quantile(x['x'],x['q'])
    if op=='VWAP':
        v=sum(x['sizes']);mu=sum(p*n for p,n in zip(x['prices'],x['sizes']))/v
        return dict(VWAP=mu,sigma=math.sqrt(sum(n*(p-mu)**2 for p,n in zip(x['prices'],x['sizes']))/v))
    if op=='CVD':
        coverage=(x['buy']+x['sell'])/(x['buy']+x['sell']+x['unknown']);return dict(delta=x['buy']-x['sell'],coverage=coverage,quality=coverage>=0.95)
    if op=='ratio':return x['own']>0 and x['opposite']>0 and x['own']/x['opposite']>=x['threshold']
    if op=='steady':return None if len(x['sizes'])<x['minimum'] else all(v>=x['fraction']*x['sizes'][0] for v in x['sizes'][-3:])
    if op=='speed':return x['point_change']/x['tick']/x['elapsed_minutes']
    if op=='median_run':
        med=statistics.median([v for v in x['volumes'] if v>0]);return dict(median=med,last_two_accepted=[v>=med for v in x['volumes'][-2:]])
    if op=='R':return x['reward_ticks']/x['risk_ticks']
    if op=='PnL':
        net=x['direction']*(x['exit']-x['entry'])*x['multiplier']-x['fee'];return dict(net_dollars=net,net_R0=net/(x['R0']*x['multiplier']))
    if op=='parity':return x['K']+math.exp(x['r']*x['T'])*(x['C']-x['P'])
    if op=='gamma':
        d1=(math.log(x['F']/x['K'])+0.5*x['sigma']**2*x['T'])/(x['sigma']*math.sqrt(x['T']))
        return math.exp(-x['r']*x['T'])*math.exp(-d1*d1/2)/math.sqrt(2*math.pi)/(x['F']*x['sigma']*math.sqrt(x['T']))
    if op=='gamma_dollars':return x['sign']*x['gamma']*x['OI']*x['multiplier']*x['X']**2*0.01
    if op=='VP':
        prices=x['prices'];vs=x['volumes'];total=sum(vs);mu=sum(p*v for p,v in zip(prices,vs))/total
        poc=min(range(len(vs)),key=lambda i:(-vs[i],abs(prices[i]-mu),prices[i]));lo=hi=poc;cum=vs[poc]
        while cum<x['fraction']*total:
            left=vs[lo-1] if lo>0 else -1;right=vs[hi+1] if hi+1<len(vs) else -1
            if left>=right and lo>0:lo-=1;cum+=vs[lo]
            if right>=left and hi+1<len(vs):hi+=1;cum+=vs[hi]
        return dict(POC=prices[poc],VAL=prices[lo],VAH=prices[hi],achieved_fraction=cum/total)
    if op=='clock':return datetime.fromisoformat(x['local']).replace(tzinfo=ZoneInfo(x['zone'])).astimezone(timezone.utc).isoformat()
    if op=='visits':return dict(high_first_index=next((i for i,p in enumerate(x['prices']) if p>=x['H']),None),low_first_index=next((i for i,p in enumerate(x['prices']) if p<=x['L']),None))
    if op=='gap':
        g=1 if x['Sunday']>x['Friday'] else -1;away=False;contact=None;full=None
        for i,p in enumerate(x['later']):
            relative=g*(p-x['Sunday'])
            if contact is None and (relative<0 or (away and relative<=0)):contact=i
            if relative>=1:away=True
            if full is None and g*(p-x['Friday'])<=0:full=i
        return dict(first_return_index=contact,full_fill_index=full)
    raise ValueError(op)

def equal(a,b,tol):
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(equal(a[k],b[k],tol) for k in a)
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(equal(x,y,tol) for x,y in zip(a,b))
    if isinstance(a,(int,float)) and not isinstance(a,bool):return isinstance(b,(int,float)) and not isinstance(b,bool) and math.isclose(a,b,rel_tol=tol,abs_tol=tol)
    return type(a)==type(b) and a==b

def validate():
    errors=[];checks={}
    def check(ok,msg):
        if not ok:errors.append(msg)
    master=json.loads((SPEC/'model_specs.json').read_text());rs=master['models'];by={r['id']:r for r in rs}
    schema=json.loads((SPEC/'model_specs.schema.json').read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    schema_errors=sorted(jsonschema.Draft202012Validator(schema).iter_errors(master),key=lambda e:e.json_path)
    for error in schema_errors:check(False,f'Schema {error.json_path}: {error.message}')
    checks['json_schema']='passed' if not schema_errors else 'failed'
    expected={f'R-{p}{i:02}' for _,p,n in FAMILIES for i in range(1,n+1)}
    check(set(by)==expected and len(rs)==85,'85 unique non-Pine IDs required')
    checks['models']=len(rs); checks['signal_models']=sum(r['role']=='signal' for r in rs)
    allowed_inputs={f'D{i:02}' for i in range(1,11)};allowed_engines={f'E{i:02}' for i in range(13)}
    required={'id','role','title','research_decision','inputs','engines','dependencies','consumers','bindings','parameters','algorithm','outputs','controls','acceptance_cases','unavailable_policy','audit_record_sha256','shared_acceptance'}
    for r in rs:
        id=r['id'];check(required<=set(r),f'{id}: missing contract fields')
        check(r['status']=='specified_not_implemented',f'{id}: misleading implementation status')
        check(len(r['algorithm'])>=4 and len(r['acceptance_cases'])>=3 and len(r['controls'])>=2,f'{id}: incomplete model/acceptance/control definition')
        check(set(r['inputs'])<=allowed_inputs,f'{id}: unknown input')
        check(set(r['engines'])<=allowed_engines,f'{id}: unknown engine')
        check(set(r['dependencies']+r['consumers'])<=expected,f'{id}: unknown dependency/consumer')
        for cond,inputs in r.get('conditional_inputs',{}).items():check('=' in cond and set(inputs)<=allowed_inputs,f'{id}: malformed conditional inputs')
        for cond,deps in r.get('conditional_dependencies',{}).items():check('=' in cond and set(deps)<=expected,f'{id}: malformed conditional dependencies')
        for name,p in r['parameters'].items():
            check(set(p)=={'default','grid','units','meaning'},f'{id}.{name}: incomplete parameter')
            grid=[json.dumps(v,sort_keys=True) for v in p['grid']]
            check(grid and len(grid)==len(set(grid)) and json.dumps(p['default'],sort_keys=True) in grid,f'{id}.{name}: invalid grid/default')
            check(bool(p['units']) and bool(p['meaning']),f'{id}.{name}: unspecified units/meaning')
        screen=1+sum(len(p['grid'])-1 for p in r['parameters'].values())
        check(screen==r['grid_screen_config_count'] and screen<=32,f'{id}: grid count/budget')
        if r['role']=='signal':
            check('stop' in r['bindings'],f'{id}: no explicit structural stop')
            check('target' in r['bindings'] or 'targets' in r['bindings'],f'{id}: no explicit target')
            check(any(k in r['bindings'] for k in ['exit_horizon','exit','exit_horizons']),f'{id}: no explicit expiry')
            check(r['execution_contract']=='E11',f'{id}: no order contract')
        old=json.loads((ROOT/r['audit_record_file']).read_text());a=next(x for x in old if x['id']==id)
        digest=hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        check(digest==r['audit_record_sha256'],f'{id}: audit provenance changed')
    # Evidence producers form a DAG. Consumer links are intentionally not edges.
    seen=set();active=set()
    def visit(id):
        if id in active:errors.append('Dependency cycle: '+id);return
        if id in seen:return
        active.add(id)
        deps=by[id]['dependencies']+[d for ds in by[id].get('conditional_dependencies',{}).values() for d in ds]
        for dep in deps:
            if dep in by:visit(dep)
        active.remove(id);seen.add(id)
    for id in sorted(by):visit(id)
    checks['parameters']=sum(len(r['parameters']) for r in rs)
    checks['one_factor_configurations']=sum(r['grid_screen_config_count'] for r in rs)
    checks['per_model_acceptance_cases']=sum(len(r['acceptance_cases']) for r in rs)
    for path,digest in master['source_files'].items():check(sha(ROOT/path)==digest,f'Master out of date: {path}')
    family_records=[r for f,_,_ in FAMILIES for r in json.loads((SPEC/'models'/f'{f}.json').read_text())]
    check(family_records==rs,'Master differs from family sources')
    gold=json.loads((SPEC/'golden_cases.json').read_text());gold_results=[]
    for c in gold['cases']:
        actual=calculate(c['operation'],c['input']);ok=equal(c['expected'],actual,gold['absolute_tolerance'])
        check(ok,f'Golden arithmetic failed: {c["id"]}; actual={actual}')
        gold_results.append({'id':c['id'],'passed':ok})
    checks['golden_arithmetic_cases']=len(gold_results)
    # All local Markdown targets must exist; model anchors must resolve exactly.
    md_files=[ROOT/'planning/phase-1-live/RESEARCH_BUILD_SPEC.md']+list(SPEC.glob('*.md'))
    link_count=0
    for f in md_files:
        text=f.read_text()
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^\n]+?)\)',text):
            if target.startswith(('https://','http://','mailto:')):continue
            target=unquote(target.strip('<>'))
            path,_,anchor=target.partition('#');dest=(f.parent/path).resolve() if path else f
            link_count+=1;check(dest.exists(),f'Broken local link {f.name}: {target}')
            if anchor and anchor.startswith('r-') and dest.exists():check(f'id="{anchor}"' in dest.read_text(),f'Broken model anchor {target}')
    checks['local_links']=link_count
    evidence=json.loads((SPEC/'data_evidence.json').read_text())
    check(evidence['catalog_sha256']==sha(ROOT/'data/manifests/dataset-catalog.json'),'Data catalog changed since inspection')
    check(len(evidence['selected_datasets'])==13,'Missing bounded input schema inspection')
    checks['inspected_datasets']=len(evidence['selected_datasets'])
    # Preserve all 224 prior audit/protected/retained input checks.
    audit=ROOT/'implementation/reports/phase1-live/chart-audit'
    manifest=json.loads((audit/'audit_input_manifest.json').read_text())
    protected=json.loads((audit/'source-recheck-2026-09-11/protected_inputs.json').read_text())
    originals=manifest['audited_inputs']+manifest['retained_tables']+protected
    for row in originals:check(sha(ROOT/row['path'])==row['sha256'],f'Protected original changed: {row["path"]}')
    checks['original_input_hash_checks']=len(originals)
    old_delivery=json.loads((audit/'delivery_manifest.json').read_text())
    audit_report='planning/phase-1-live/CHART_AUDIT.md'
    if audit_report in old_delivery:check(sha(ROOT/audit_report)==old_delivery[audit_report],'Preserved audit report changed')
    checks['dependency_graph']='acyclic' if not any('Dependency cycle' in s for s in errors) else 'failed'
    result={'passed':not errors,'status':'specification_validated_models_not_implemented','checks':checks,'errors':errors,'golden_arithmetic':gold_results,'limitations':['No replacement model was implemented or backtested by this specification task.','Per-card behavioral/prefix/sequence cases are build requirements, not claimed engine test passes.','Empirical improvement remains to be established by the registered comparison protocol.']}
    dump(SPEC/'validation.json',result)
    paths=md_files+list(SPEC.glob('*.json'))+list((SPEC/'models').glob('*.json'))+[ROOT/'implementation/tools/research_spec_build.py',ROOT/'implementation/tools/research_spec_validate.py']
    paths=[p for p in paths if p.name!='delivery_manifest.json']
    dump(SPEC/'delivery_manifest.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))})
    print(json.dumps({k:result[k] for k in ['passed','status','checks','errors']}))
    return not errors

if __name__=='__main__':sys.exit(0 if validate() else 1)
