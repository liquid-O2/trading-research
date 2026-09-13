"""Source controls, selected-branch logic controls and native perturbations.

Truth-table controls test the evaluator boundary only. They cannot establish
native discovery; the pilot and independent input regressions do that.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import os
import importlib.util
import sys
import subprocess
import sys

from .catalog import METHOD_BY_ID,PRIMARY
from .contracts import fields_for
from .evidence import typed
from .expressions import evaluate,expression_for
from .historical_runner import ROOT,BASE,load_registry,software_identity,immutable_json,write_job,read
from .empirical_protocol import content_hash
from .native_resolution import file_digest,NativeEvidenceError
from .protocol import jsonable


def predicate_controls(manifest,method_rows):
    controls=[]
    for row in manifest['branches']:
        method,branch=row['method_id'],row['branch']
        if row['extra_unit']:continue
        fixture_rows=method_rows[method]
        predicate=('selected_order_configuration' if method=='REFILL-STUDY' and branch=='supplied_selected_order' else
                   'macro_application' if method=='STOIC-DATA' and branch=='macro_application' else PRIMARY[method])
        selected=[f for f in fixture_rows if f.get('actual_value',{}).get('verdict')=='pass' and f.get('predicate')==predicate]
        original=next((f for f in selected if f['actual_value']['branch']==branch),selected[0] if selected else None)
        if original is None:raise NativeEvidenceError('no logical seed for '+row['coverage_id'])
        values={k:v['value'] for k,v in original['actual_value']['operands'].items()}
        values.update(branch=branch)
        contracts=fields_for(method)
        values={k:typed(v,contracts[k].type,k) if k in contracts else v for k,v in values.items()}
        # Branches sharing a common family predicate get their own selected
        # operand inventory. New flags are declared logical controls, never
        # presented as native observations or an author setting.
        for _ in range(2):
            selected_fields=evaluate(method,predicate,values).fields
            for name in selected_fields:
                if name in values and values[name] is not None:continue
                contract=fields_for(method).get(name)
                if contract is None:raise NativeEvidenceError('unknown logical control operand '+name)
                values[name]=True if contract.type.startswith('boolean') else values.get('range_known_at',values.get('decision_at',1))-1 if contract.type.startswith('event_key') else 1
        contracts=fields_for(method)
        values={k:typed(v,contracts[k].type,k) if k in contracts else v for k,v in values.items()}
        actual=evaluate(method,predicate,values)
        if actual.value is not True:raise NativeEvidenceError('logical positive control does not pass '+row['coverage_id']+' '+str(actual))
        gates=[k for k in actual.fields if values.get(k) is True and k in contracts and contracts[k].type.startswith('boolean')]
        found=None
        for gate in sorted(gates):
            failing=dict(values,**{gate:False});missing=dict(values,**{gate:None})
            if evaluate(method,predicate,failing).value is False and evaluate(method,predicate,missing).value is None:
                found=gate;break
        if found is None:raise NativeEvidenceError('no essential logical control gate '+row['coverage_id'])
        controls.append({'coverage_id':row['coverage_id'],'kind':'selected_predicate_logic_only','seed_fixture':original['id'],
            'predicate':predicate,'positive_values':jsonable(values),'positive_verdict':'pass',
            'failing_mutation':{found:False},'failing_verdict':'fail','missing_mutation':{found:None},'missing_verdict':'unknown',
            'native_discovery_proof':False,'ambiguity_proof':'separate upstream timestamp-batch/native boundary controls and source C08 cases'})
    return controls


def native_perturbations():
    from .historical_features import HistoricalFeatures,MINUTE
    from .historical_price_scanners import scan_jumbo,scan_green_failure
    from .historical_flow import scan_sires
    from decimal import Decimal
    base=HistoricalFeatures('2026-09-01')
    cutoff=base.at('11:00')
    document=deepcopy(base.window.document)
    for rows in document['bars'].values():
        for bar in rows:
            if bar['start']>=cutoff:
                for key in 'OHLC':
                    if bar[key] is not None:bar[key]+=Decimal(100000)
                bar['V']*=1000
    for row in document['footprints']:
        if row['start']>=cutoff:
            row['rows']=[[px+Decimal(100000),b*1000,a*1000,u*1000] for px,b,a,u in row['rows']]
            row['pv']+=Decimal(100000)*row['volume'];row['p2v']*=1000000
    changed=HistoricalFeatures('2026-09-01',document=document)
    raw_local=changed.local
    def local(a,b,*,book=False):
        return [dict(r,price=r['price']+Decimal(100000) if r['price'] is not None else None,
                    executed_size=r['executed_size']*1000 if r.get('executed_size') is not None else None)
                if r['event_ns']>=cutoff else r for r in raw_local(a,b,book=book)]
    changed.local=local
    results=[]
    for scanner,branch in ((scan_jumbo,'judas_reversal'),(scan_green_failure,'nyam_box'),(scan_sires,'vwap_deviation_fade')):
        a=scanner(base,branch);b=scanner(changed,branch)
        def prefix(result):
            return [{k:e[k] for k in ('candidate_id','decision_at','values','research_verdict')}
                for e in result['episodes'] if e['decision_at']<=cutoff]
        before,after=prefix(a),prefix(b)
        if before!=after:raise NativeEvidenceError('native future perturbation changed earlier '+branch)
        results.append({'method_id':a['method_id'],'branch':branch,'cutoff':cutoff,'native_input_sha256':base.window.document['input_sha256'],
            'native_executions':base.window.document['row_count'],'earlier_episodes':len(before),'prefix_sha256':content_hash(before),
            'future_price_change':100000,'future_volume_multiplier':1000,'result':'pass'})
    if sum(r['earlier_episodes'] for r in results)==0:raise NativeEvidenceError('native perturbation exercised no earlier episode')
    return results


def run_controls(root):
    from .core_fixtures import run_core_fixtures
    from .objects import run_object_fixtures
    from .methods import method_fixtures
    registry,manifest=load_registry(root)
    core=run_core_fixtures();objects=run_object_fixtures([r['object_id'] for r in manifest['objects']])
    methods={m:method_fixtures(m) for m in METHOD_BY_ID}
    rows=[*core,*objects,*[r for group in methods.values() for r in group]]
    failures=[r['id'] for r in rows if r['status']!='pass']
    regressions=[]
    for filename,output_name,attribute in (
        ('validate_phase1_audit_regressions.py','audit-regressions.json','OUTPUT'),
        ('validate_phase1_post_implementation_regressions.py','repair-regressions.json','REPORT')):
        path=ROOT/'implementation/tools'/filename
        spec=importlib.util.spec_from_file_location('phase1_v2_'+path.stem,path)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        destination=Path(root)/'validation'/output_name;destination.parent.mkdir(parents=True,exist_ok=True)
        setattr(module,attribute,destination)
        code=module.main()
        if code:failures.append(filename)
        regressions.append({'path':str(destination),'sha256':file_digest(destination),'exit_code':code})
    logic=predicate_controls(manifest,methods)
    native=native_perturbations()
    artifact=write_job(Path(root)/'validation/control-details.json.gz',{'core':core,'objects':objects,'methods':methods,'logic':logic,'native':native})
    report={'schema':'phase1-control-validation-v2','software_sha256':registry['software']['sha256'],
        'registry_sha256':registry['registry_sha256'],'failures':failures,'details':artifact,
        'counts':{'core':len(core),'object':len(objects),'method':sum(map(len,methods.values())),
            'selected_branch_logic':len(logic),'native_future_perturbations':len(native)},
        'coverage_ids':[r['coverage_id'] for r in manifest['branches']],
        'coverage_basis':'all 50 selected branch predicates plus existing source/quantity/lifecycle/state controls for eight secondary units; actual native dispatch is required independently for every unit',
        'native_perturbations':native,'regressions':regressions,'truth_tables_are_native_discovery_proof':False}
    immutable_json(Path(root)/'validation/controls.json',report)
    if failures:raise NativeEvidenceError('source controls failed '+str(failures))
    return report


def full_suite(root):
    registry,_=load_registry(root)
    directory=Path(root)/'validation';directory.mkdir(parents=True,exist_ok=True)
    path=directory/'full-suite.log'
    command=[sys.executable,'-m','pytest','-q','implementation/tests']
    env=dict(os.environ,PYTHONPATH=str(ROOT/'implementation/src'))
    with path.open('w') as log:
        process=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    if software_identity()['sha256']!=registry['software']['sha256']:
        raise NativeEvidenceError('code/tests changed during full suite')
    lines=path.read_text().splitlines()
    summary=next((line for line in reversed(lines) if 'passed' in line or 'failed' in line),lines[-1] if lines else 'empty test output')
    out={'schema':'phase1-full-suite-v2','software_sha256':registry['software']['sha256'],
        'command':command,'exit_code':process.returncode,'summary':summary,'log_path':str(path),'log_sha256':file_digest(path)}
    immutable_json(directory/'full-suite.json',out)
    if process.returncode:raise NativeEvidenceError('full suite failed: '+summary)
    return out
