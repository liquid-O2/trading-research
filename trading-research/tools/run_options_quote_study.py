"""Register bounded admission and measurement of the acquired options-quote sources."""
from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'validation/OPTIONS_QUOTE_QUALITY_SUPPORT_V1.json'
RUNS=ROOT/'reports/options-quote-runs'
OPERATIONAL_LIMITS=ROOT/'validation/OPTIONS_QUOTE_OPERATIONAL_LIMITS_V4.json'


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def checked(path, sha=None, maximum=16*1024**2):
    path=Path(path)
    if 'archive' in path.parts or not path.is_file() or path.stat().st_size>maximum:
        raise ValueError('bounded retained input required')
    raw=path.read_bytes()
    if sha and hashlib.sha256(raw).hexdigest()!=sha:raise ValueError(f'input changed: {path}')
    return raw



def effective_resources(protocol, reference):
    document = json.loads(checked(reference['path'], reference['sha256']))
    allowed = {'per_attempt_output_bytes','mode_cpu_seconds','memory_bytes','wall_seconds','concurrency','cpu_budget_seconds'}
    override = document.get('overrides',{})
    if (document.get('kind') != 'options_quote_operational_limits_v1'
            or document.get('family') != protocol['family']
            or document.get('protocol_sha256') != hashlib.sha256(checked(PROTOCOL)).hexdigest()
            or not set(override) <= allowed):
        raise ValueError('quote operational allocation must bind the unchanged scientific family')
    cap = {**protocol['resources'], **override}
    if not protocol['resources']['per_attempt_output_bytes'] <= cap['per_attempt_output_bytes'] <= cap['maximum_study_output_bytes']:
        raise ValueError('quote attempt allocation exceeds retained study output')
    if (set(cap['mode_cpu_seconds']) != set(protocol['resources']['mode_cpu_seconds'])
            or any(type(v) is not int or v <= 0 or v > cap['cpu_budget_seconds'] for v in cap['mode_cpu_seconds'].values())
            or type(cap['memory_bytes']) is not int or cap['memory_bytes'] > 2*protocol['resources']['memory_bytes']
            or type(cap['wall_seconds']) is not int or not 0 < cap['wall_seconds'] <= 36000
            or type(cap.get('concurrency',6)) is not int or not 1 <= cap.get('concurrency',6) <= 6):
        raise ValueError('operational quote allocation is not bounded')
    return cap


def safe(value):
    if isinstance(value,(date,datetime)):return value.isoformat()
    if isinstance(value,dict):return {str(k):safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [safe(v) for v in value]
    if isinstance(value,float) and not __import__('math').isfinite(value):return {'nonfinite':str(value)}
    return value


def admit_sources(protocol,store,progress_path):
    import pyarrow.parquet as pq
    from pyarrow import BufferReader
    reference=protocol['source_file_manifest']
    manifest=json.loads(checked(reference['path'],reference['sha256']))
    if manifest['file_count']!=len(manifest['files']):raise ValueError('source file membership differs')
    records=[];schemas={};rows_by_role={};source_bytes=0;samples={}
    for file_id,source in enumerate(manifest['files']):
        path=Path('/workspace/data')/source['path']
        if not path.resolve().is_relative_to(Path('/workspace/data')):raise ValueError('source outside original acquired data')
        raw=checked(path,maximum=protocol['resources']['maximum_source_file_bytes'])
        if len(raw)!=source['size_bytes']:raise ValueError('source changed since metadata freeze')
        sha=hashlib.sha256(raw).hexdigest();record={'file_id':file_id,'source':source,'sha256':sha,'format':path.suffix}
        if path.suffix=='.parquet':
            pf=pq.ParquetFile(BufferReader(raw));schema=str(pf.schema_arrow);schema_id=hashlib.sha256(schema.encode()).hexdigest()
            schemas[schema_id]=schema;record.update(rows=pf.metadata.num_rows,schema_id=schema_id)
            rows_by_role[source['role']]=rows_by_role.get(source['role'],0)+pf.metadata.num_rows
            if source['dataset_id'] not in samples:
                batches=pf.iter_batches(batch_size=2);batch=next(batches,None)
                samples[source['dataset_id']]={'file_id':file_id,'rows':[] if batch is None else safe(batch.to_pylist())}
        else:
            marker=json.loads(raw);record.update(rows=0,schema_id='empty_marker',marker=marker)
        records.append(record);source_bytes+=len(raw)
        with Path(progress_path).open('ab') as progress:progress.write(json.dumps({'file_id':file_id,'sha256':sha,'rows':record['rows']}).encode()+b'\n')
    return {'kind':'options_quote_admitted_sources_v1','sources':records,'source_files':len(records),'source_bytes':source_bytes,
            'schemas':schemas,'rows_by_role':rows_by_role,'samples':samples,'all_declared_sources_admitted':True,'full_population_statistics_complete':False}

def predecessor_actual(reference,store,protocol,mode):
    from trading_research.operations.artifacts import artifact_ref
    execution=json.loads(checked(reference['path'],reference['sha256']))
    if execution.get('success') is not True or execution.get('mode')!=mode or execution.get('family')!=protocol['family']:
        raise ValueError('successful own-family predecessor required')
    worker=store.read_json(artifact_ref(execution['worker']))
    if worker.get('success') is not True or worker.get('attempt_id')!=execution['attempt_id']:
        raise ValueError('predecessor worker identity differs')
    actual=store.read_json(artifact_ref(worker['actual']))
    return execution,actual


def implementation_paths():
    import ast
    pending=['src/trading_research/research/options_quote_measurements.py','tests/test_options_quote_measurements.py']
    seen=set()
    while pending:
        name=pending.pop()
        if name in seen:continue
        seen.add(name)
        tree=ast.parse((ROOT/name).read_text())
        for node in ast.walk(tree):
            mods=[]
            if isinstance(node,ast.ImportFrom) and node.module:mods=[node.module]
            elif isinstance(node,ast.Import):mods=[a.name for a in node.names]
            for mod in mods:
                if not mod.startswith('trading_research'):continue
                rel='src/'+mod.replace('.','/')+'.py'
                if (ROOT/rel).is_file() and rel not in seen:pending.append(rel)
    return sorted(seen)


def compare_quote_population(expected, actual, outputs):
    import math
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
    from trading_research.research.options_quote_measurements import _auth_output_ref
    from trading_research.research.auction_flow_storage import read_json_artifact
    if expected['selected_dates']!=actual['selected_dates'] or expected['selected_chains']!=actual['selected_chains']:
        raise ValueError('accepted quote parity population differs')
    if expected['counts']!=actual['counts']:
        raise ValueError('accepted quote parity counts differ')
    def parts(refs):
        if isinstance(refs,list):
            for ref in refs:yield from parts(ref)
        else:yield refs
    def batches(refs):
        for ref in parts(refs):
            _auth_output_ref(ref)
            yield from pq.ParquetFile(ref['path']).iter_batches(batch_size=32768)
    tables={}
    for name in ('admission','exceptions','alias_conflict','cut_board','source_quality',
                 'underlier_support','fred_support','action_support','identity_match','coverage'):
        left,right=iter(batches(expected['refs'][name])),iter(batches(actual['refs'][name]))
        a=b=None;ai=bi=total=0
        while True:
            if a is None or ai==len(a):a=next(left,None);ai=0
            if b is None or bi==len(b):b=next(right,None);bi=0
            if a is None or b is None:
                if a is not None or b is not None:raise ValueError('accepted table length differs: '+name)
                break
            if a.schema!=b.schema:raise ValueError('accepted schema differs: '+name)
            n=min(len(a)-ai,len(b)-bi)
            for index,field in enumerate(a.schema):
                x,y=a.column(index).slice(ai,n),b.column(index).slice(bi,n)
                if name=='coverage' and pa.types.is_floating(field.type):
                    if not x.is_null().equals(y.is_null()) or not np.allclose(x.to_numpy(zero_copy_only=False),y.to_numpy(zero_copy_only=False),rtol=1e-12,atol=1e-10,equal_nan=True):
                        raise ValueError('accepted aggregate differs: '+field.name)
                elif not x.equals(y):raise ValueError('accepted table field differs: '+name+'.'+field.name)
            ai+=n;bi+=n;total+=n
        tables[name]={'rows':total,'all_fields_equal':True,'coverage_float_tolerance':{'relative':1e-12,'absolute':1e-10} if name=='coverage' else None}
    def equal(a,b,path):
        if type(a) is float or type(b) is float:
            if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10):
                raise ValueError('accepted statistic differs: '+path)
        elif isinstance(a,dict):
            if not isinstance(b,dict) or a.keys()!=b.keys():raise ValueError('accepted statistic keys differ: '+path)
            for key in a:equal(a[key],b[key],path+'.'+str(key))
        elif isinstance(a,list):
            if not isinstance(b,list) or len(a)!=len(b):raise ValueError('accepted statistic list differs: '+path)
            for i,(x,y) in enumerate(zip(a,b)):equal(x,y,path+'.'+str(i))
        elif a!=b:raise ValueError('accepted statistic differs: '+path)
    groups=0
    for chain,ref in expected['refs']['chain_groups'].items():
        before=read_json_artifact(ref);after=read_json_artifact(actual['refs']['chain_groups'][chain])
        equal(before,after,chain);groups+=len(before)
        del before,after
    return outputs.json('accepted-pilot12-population-parity.json',
        {'kind':'options_quote_accepted_population_parity_v1','passed':True,'tables':tables,
         'statistical_groups':groups,'statistics_float_tolerance':{'relative':1e-12,'absolute':1e-10},
         'expected_counts':expected['counts'],'actual_counts':actual['counts'],
         'source':'accepted pilot12 exact same102quote files,fullOI and56chain/dateunits; all10logicaltables and every statisticalgroup'},
         kind='options_quote_accepted_population_parity_v1')


def run_measurement(packet,protocol,store,outputs):
    import importlib.util,io,unittest
    from trading_research.research.options_quote_measurements import run,combine_partition_results
    from trading_research.operations.artifacts import artifact_ref
    cfg=packet['configuration']
    cap=effective_resources(protocol,cfg['operational_limits'])
    admission,admitted=predecessor_actual(cfg['predecessor'],store,protocol,'admit')
    if admitted.get('kind')!='options_quote_admitted_sources_v1' or admitted.get('all_declared_sources_admitted') is not True:
        raise ValueError('complete authenticated quote admission required')
    oi_execution,oi_population=accepted_oi(cfg['oi_execution'],store,full=packet['mode']=='full')
    dates=quote_dates(protocol)
    selected=dates[:8] if packet['mode']=='pilot' else dates
    oi_dates=oi_population.get('selected_dates')
    if oi_dates is not None and not set(selected)<=set(oi_dates):
        raise ValueError('OI accepted population does not cover the quote date selection')
    gate=None
    if packet['mode']=='full':
        pilot,prior=predecessor_actual(cfg['pilot'],store,protocol,'pilot')
        previous=store.read_json(artifact_ref(pilot['snapshot']))['manifest']
        current=store.read_json(artifact_ref(packet['snapshot']))['manifest']
        paths=cfg['implementation_paths']
        operation=json.loads(checked(cfg['operational_limits']['path'],cfg['operational_limits']['sha256']))
        compatibility=operation.get('operational_runner_compatibility',{})
        runner_ok=pilot['runner_sha256']==packet['runner_sha256']
        if not runner_ok and compatibility:
            prior_source=checked(compatibility['prior_source']['path'],compatibility['prior_source']['sha256'])
            review=json.loads(checked(compatibility['review']['path'],compatibility['review']['sha256']))
            runner_ok=(hashlib.sha256(prior_source).hexdigest()==pilot['runner_sha256']
                and compatibility.get('from_sha256')==pilot['runner_sha256']
                and compatibility.get('to_sha256')==packet['runner_sha256']
                and review.get('prior_runner_sha256')==pilot['runner_sha256']
                and review.get('current_runner_sha256')==packet['runner_sha256']
                and review.get('measurement_implementation_unchanged') is True
                and review.get('only_operational_allocation_and_compatibility') is True)
        if (not runner_ok or pilot['configuration_implementation_paths']!=paths
                or any(previous.get(name)!=current.get(name) for name in paths)):
            raise ValueError('quote full needs unchanged tested measurement implementation and authenticated operational runner compatibility')
        if prior.get('selected_dates')!=dates[:8] or prior.get('selected_chains')!=protocol['population']['chains']:
            raise ValueError('quote pilot did not cover all seven chains and eight prescribed dates')
        gate=quote_full_gate(protocol,admitted,prior,oi_population,resources=cap)
        outputs.json('full-resource-gate.json',gate,kind='options_quote_full_resource_gate_v1')
    spec=importlib.util.spec_from_file_location('test_options_quote_measurements',ROOT/'tests/test_options_quote_measurements.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    stream=io.StringIO();began=time.process_time()
    result=unittest.TextTestRunner(stream=stream,verbosity=2,failfast=True).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    tests={'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'cpu_seconds':time.process_time()-began,'output':stream.getvalue()}
    outputs.json('unit-tests.json',tests,kind='options_quote_unit_tests_v1')
    if not tests['passed']:raise ValueError('quote quality regressions failed before actual source execution:\n'+stream.getvalue())
    binding={'admission_execution':cfg['predecessor'],'oi_execution':cfg['oi_execution'],
        'admitted_sources_sha256':__import__('trading_research.operations.artifacts',fromlist=['digest']).digest(admitted),
        'actual_oi_mode':oi_execution['mode']}
    outputs.json('accepted-input-binding.json',binding,kind='options_quote_accepted_inputs_v1')
    if packet['mode']=='pilot':
        actual=run(protocol=protocol,admitted=admitted,oi_population=oi_population,store=store,outputs=outputs,
            selected_dates=selected,selected_chains=protocol['population']['chains'],execution_resources=cap)
        parallel=None
    else:
        parts,parallel=run_quote_shards(packet,protocol,admitted,store,outputs)
        actual=combine_partition_results(protocol=protocol,results=parts,outputs=outputs,load_reference=load_output_reference)
    if actual.get('passed') is not True:raise ValueError('quote measurement/reduction did not pass')
    actual.update(tests=tests,output_bytes=outputs.written,pilot_gate=gate,accepted_input_binding=binding,
        parallel_execution=parallel,selected_dates=selected,selected_chains=protocol['population']['chains'],execution_resources=cap)
    if packet['mode']=='pilot':
        operation=json.loads(checked(cfg['operational_limits']['path'],cfg['operational_limits']['sha256']))
        if operation.get('accepted_parity_execution'):
            prior_exec,expected=predecessor_actual(operation['accepted_parity_execution'],store,protocol,'pilot')
            actual['accepted_population_parity']=compare_quote_population(expected,actual,outputs)
    if packet['mode']=='pilot' and oi_execution['mode']=='full':
        try:
            actual['full_resource_projection']=quote_full_gate(protocol,admitted,actual,oi_population,resources=cap)
            actual['full_resource_projection']['passed']=True
        except ValueError as error:
            actual['full_resource_projection']={'passed':False,'reason':str(error)}
        outputs.json('full-resource-projection.json',actual['full_resource_projection'],kind='options_quote_full_resource_projection_v1')
    return actual


def load_output_reference(ref,maximum=512*1024**2):
    raw=checked(ref['path'],ref['sha256'],maximum=maximum)
    if len(raw)!=ref['size_bytes']:raise ValueError('retained output size mismatch')
    if ref.get('encoding')=='canonical-json-zstd-v1':
        from trading_research.research.auction_flow_storage import read_json_artifact
        return read_json_artifact(ref)
    return json.loads(raw)


def accepted_oi(reference,store,*,full):
    from trading_research.operations.artifacts import artifact_ref,digest
    from trading_research.operations.trials import TrialRegistry
    execution=json.loads(checked(reference['path'],reference['sha256']))
    state=TrialRegistry(ROOT/'evidence/trials').state();attempt=state['attempts'].get(execution.get('attempt_id'))
    if (execution.get('family')!='Research-Options-OI-report-lifecycle-v1' or execution.get('success') is not True
            or execution.get('mode') not in (('full',) if full else ('pilot','full'))
            or attempt is None or attempt['status']!='succeeded'
            or not any(r['sha256']==digest(execution) for r in attempt['result_artifacts'])):
        raise ValueError('accepted registered OI execution required for quote measurement')
    worker=store.read_json(artifact_ref(execution['worker']))
    actual=store.read_json(artifact_ref(worker['actual']))
    if (worker.get('success') is not True or worker.get('attempt_id')!=execution['attempt_id']
            or actual.get('passed') is not True or (full and actual.get('selected_dates') is not None)):
        raise ValueError('OI worker/result does not identify the accepted population')
    for name in ('identity_map','reports','asof_intervals','coverage','membership','source_manifest'):
        if not actual.get('refs',{}).get(name):raise ValueError('accepted OI result lacks '+name)
    return execution,dict(actual,accepted_execution=reference,accepted_execution_mode=execution['mode'])


def quote_dates(protocol):
    from trading_research.research.options_quote_measurements import load_calendar
    from trading_research.research.options_oi_measurements import intended_cash_dates
    pop=protocol['population']
    return [d.isoformat() for d in intended_cash_dates(load_calendar(protocol)[0],pop['first_date'],pop['last_date'])]


def quote_partition_plan(protocol,admitted,*,resources=None):
    dates=quote_dates(protocol);jobs=[]
    for chain in protocol['population']['chains']:
        for year in sorted({d[:4] for d in dates}):
            selected=[d for d in dates if d.startswith(year)]
            records=[s for s in admitted['sources'] if s['source'].get('role')=='quote'
                and s['source'].get('chain')==chain and str(s['source'].get('request_date','')).startswith(year)]
            jobs.append({'chain':chain,'year':int(year),'selected_dates':selected,
                'quote_rows':sum(s['rows'] for s in records),'quote_bytes':sum(s['source']['size_bytes'] for s in records),
                'quote_file_ids':sorted(s['file_id'] for s in records)})
    jobs.sort(key=lambda p:(-p['quote_rows'],p['chain'],p['year']))
    cap=resources or protocol['resources'];reserve=7*1024**3;floor=256*1024**2
    variable=cap['per_attempt_output_bytes']-reserve-floor*len(jobs)
    weights=[max(1,p['quote_rows']) for p in jobs];total=sum(weights)
    if variable<=0:raise ValueError('quote shard output reservation is empty')
    for i,p in enumerate(jobs):
        p.update(ordinal=i,output_bytes=floor+variable*weights[i]//total,
            cpu_seconds=cap['mode_cpu_seconds']['full']-300,memory_bytes=cap['memory_bytes'])
    return jobs


def oi_reference_bytes(population):
    refs=population.get('refs',{})
    total=0
    for name in ('identity_map','reports','asof_intervals','coverage'):
        value=refs.get(name,[])
        if isinstance(value,dict):value=[value]
        total+=sum(r['size_bytes'] for r in value)
    return total


def quote_full_gate(protocol,admitted,pilot,oi_population,*,resources=None):
    all_dates=quote_dates(protocol);selected=set(all_dates[:8]);parts=quote_partition_plan(protocol,admitted,resources=resources)
    raw=[r for r in admitted['sources'] if r['source'].get('role')=='quote']
    chosen=[r for r in raw if r['source']['request_date'] in selected]
    total_rows=sum(r['rows'] for r in raw);pilot_rows=sum(r['rows'] for r in chosen)
    if pilot_rows<=0 or pilot['counts']['source_rows_read']!=pilot_rows:raise ValueError('pilot original quote row count differs')
    row_scale=total_rows/pilot_rows
    byte_scale=sum(r['source']['size_bytes'] for r in raw)/max(1,sum(r['source']['size_bytes'] for r in chosen))
    date_scale=len(all_dates)/len(selected);scale=max(row_scale,byte_scale,date_scale)
    cap=resources or protocol['resources']
    resources=pilot['resources'];source_cpu=resources['source_parse_dedup_board_cpu_seconds']
    stats_cpu=resources['statistics_cpu_seconds'];load_cpu=resources['oi_support_load_cpu_seconds']
    pilot_oi=pilot['oi_population_identity'];pilot_refs=pilot_oi.get('refs',pilot_oi)
    oi_scale=oi_reference_bytes(oi_population)/max(1,oi_reference_bytes({'refs':pilot_refs}))
    # Each child can read the accepted OI reference set. Charge this repeated
    # authentication conservatively until measured partition loading is known.
    projected_cpu=1.5*(source_cpu*scale+stats_cpu*max(date_scale,len(parts))+load_cpu*max(1,oi_scale)*len(parts)
        +pilot['tests']['cpu_seconds'])+300
    group_count = int(pilot['group_count']) if 'group_count' in pilot else sum(
        len(load_output_reference(ref)) for ref in pilot['refs']['chain_groups'].values())
    universes = 1+len({d[:4] for d in all_dates})+len(protocol['population']['stages'])
    cuts,rights,dtes = 5,3,9
    def targets(families):
        return 1+cuts+families+rights+dtes+families*rights+families*dtes+cuts*families+cuts*families*rights*dtes
    target_count = sum(targets(2 if chain=='VIX' else 3) for chain in protocol['population']['chains'])
    maximum_groups = universes*target_count
    production_output=1.5*resources['production_output_bytes']*scale
    # Date labels are the only length-N output vector in a statistical group.
    # Two times measured bytes/group covers longer nonnull estimates/count text;
    # complete date vectors get an additional uncompressed size allowance.
    statistics_output=1.5*(2*resources['statistics_output_bytes']*maximum_groups/max(1,group_count)
        +13*len(all_dates)*maximum_groups)
    projected_output=production_output+statistics_output+512*1024**2
    concurrency=cap.get('concurrency',6)
    loads=[0.0]*concurrency
    for p in parts:
        cost=1.5*(source_cpu*p['quote_rows']/pilot_rows+load_cpu*max(1,oi_scale))
        j=min(range(concurrency),key=lambda i:loads[i]);loads[j]+=cost
    wall=max(loads)+1.5*stats_cpu*date_scale+600
    gate={'margin':1.5,'rows_scale':row_scale,'bytes_scale':byte_scale,'dates_scale':date_scale,'oi_bytes_scale':oi_scale,
        'projected_cpu_seconds':projected_cpu,'projected_output_bytes':projected_output,
        'projected_parallel_wall_seconds':wall,'concurrency':concurrency,'partitions':len(parts),
        'projected_measurement_output_bytes':production_output,'projected_statistics_output_bytes':statistics_output,
        'maximum_statistical_groups':maximum_groups,'pilot_statistical_groups':group_count,
        'memory_bytes_per_process':cap['memory_bytes'],'allocated_address_space_bytes':(concurrency+1)*cap['memory_bytes'],
        'method':'measured production scaled by admitted rows/bytes/dates; OI authentication charged per partition; statistics once after all partitions with date-scaled CPU and full declared target-count output plus uncompressed date-label allowance'}
    if (projected_cpu>cap['mode_cpu_seconds']['full'] or projected_output>cap['per_attempt_output_bytes']-32*1024**2
            or production_output>sum(p['output_bytes'] for p in parts)
            or statistics_output>7*1024**3-512*1024**2 or wall>cap['wall_seconds']):raise ValueError('measured quote full projection exceeds registered bounds: '+str(gate))
    return gate


def quote_parallel_tools(packet):
    checked(ROOT/'tools/auction_flow_parallel.py',packet['configuration']['parallel_helper_sha256'])
    sys.path.insert(0,str(ROOT/'tools'))
    import auction_flow_parallel
    return auction_flow_parallel


def quote_shard(registered_path,child_path):
    # Children inherit the coordinator's finite limits. Bootstrap may only lower
    # these bounds; authenticated partition limits narrow them again below.
    for limit,bound in ((resource.RLIMIT_CPU,120010),(resource.RLIMIT_AS,17179869184),
                        (resource.RLIMIT_FSIZE,51539607552)):
        soft,hard=resource.getrlimit(limit)
        hard=bound if hard==resource.RLIM_INFINITY else min(bound,hard)
        soft=hard if soft==resource.RLIM_INFINITY else min(soft,hard)
        resource.setrlimit(limit,(soft,hard))
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref
    from trading_research.operations.trials import TrialRegistry
    from trading_research.research.auction_flow_storage import BoundedOutputs
    packet=json.loads(checked(registered_path));child=json.loads(checked(child_path));cfg=packet['configuration']
    protocol=json.loads(checked(PROTOCOL,packet['protocol_sha256']));registry=TrialRegistry(ROOT/'evidence/trials');store=registry.artifacts
    state=registry.state();a=state['attempts'][packet['attempt_id']];t=state['trials'][packet['trial_id']]
    helper=quote_parallel_tools(packet)
    helper.require_parent_identity(coordinator_pid=child['coordinator_pid'],supervisor_pid=packet['supervisor_pid'])
    if (a['status']!='running' or a['trial_id']!=packet['trial_id'] or a['family']!=protocol['family']
            or t['configuration']!=cfg or t['code_hash']!=packet['snapshot']['sha256'] or packet['mode']!='full'
            or child['coordinator_pid']!=os.getppid() or child['attempt_id']!=packet['attempt_id']
            or child['trial_id']!=packet['trial_id'] or child['configuration']!=cfg
            or Path(registered_path).resolve()!=RUNS/packet['attempt_id']/'packet.json'):
        raise ValueError('quote shard does not identify its registered coordinator')
    checked(__file__,packet['runner_sha256']);manifest=store.read_json(artifact_ref(packet['snapshot']))['manifest']
    for name in cfg['implementation_paths']:checked(ROOT/name,manifest[name])
    if any(os.environ.get(k)!=v for k,v in cfg['thread_limits'].items()):raise ValueError('quote shard threadlimits changed')
    _,admitted=predecessor_actual(cfg['predecessor'],store,protocol,'admit')
    cap=effective_resources(protocol,cfg['operational_limits'])
    resource.setrlimit(resource.RLIMIT_AS,(cap['memory_bytes'],cap['memory_bytes']))
    jobs=quote_partition_plan(protocol,admitted,resources=cap);ordinal=child['ordinal']
    if type(ordinal) is not int or not 0<=ordinal<len(jobs) or child['partition']!=jobs[ordinal]:raise ValueError('quote shard ownership differs')
    directory=Path(registered_path).parent/'outputs'/f'quote-shard-{ordinal:02d}'
    if Path(child_path).resolve()!=directory.parent/f'quote-shard-{ordinal:02d}-packet.json':raise ValueError('quote shard packet namespace differs')
    part=jobs[ordinal];resource.setrlimit(resource.RLIMIT_CPU,(part['cpu_seconds'],part['cpu_seconds']+10))
    _,oi=accepted_oi(cfg['oi_execution'],store,full=True)
    from trading_research.research.options_quote_measurements import run
    out=BoundedOutputs(directory,maximum_total_bytes=part['output_bytes'],maximum_file_bytes=part['output_bytes'])
    actual=run(protocol=protocol,admitted=admitted,oi_population=oi,store=store,outputs=out,
        selected_dates=part['selected_dates'],selected_chains=[part['chain']],
        calculate_statistics=False,execution_resources=cap)
    out.json('result.json',{'passed':actual['passed'],'attempt_id':packet['attempt_id'],'ordinal':ordinal,
        'partition':part,'actual':actual},kind='options_quote_shard_result_v1')
    return 0


def run_quote_shards(packet,protocol,admitted,store,outputs):
    helper=quote_parallel_tools(packet);live=helper.live_hardware_limits();cap=effective_resources(protocol,packet['configuration']['operational_limits']);concurrency=cap.get('concurrency',6)
    allocated=(concurrency+1)*cap['memory_bytes']
    if live['memory_limit_bytes'] is not None and allocated>live['memory_limit_bytes']:raise ValueError('quote shard allocation exceeds live memory')
    parts=quote_partition_plan(protocol,admitted,resources=cap);jobs=[];directories=[]
    registered=RUNS/packet['attempt_id']/'packet.json'
    for part in parts:
        ordinal=part['ordinal'];directory=outputs.directory/f'quote-shard-{ordinal:02d}'
        child={'ordinal':ordinal,'coordinator_pid':os.getpid(),'attempt_id':packet['attempt_id'],
            'trial_id':packet['trial_id'],'configuration':packet['configuration'],'partition':part}
        ref=outputs.json(f'quote-shard-{ordinal:02d}-packet.json',child,kind='options_quote_shard_packet_v1')
        jobs.append({'ordinal':ordinal,'argv':[sys.executable,str(Path(__file__).resolve()),'--shard',str(registered),ref['path']],
            'cwd':str(ROOT),'env':dict(os.environ)})
        directories.append(directory)
    evidence={}
    try:
        helper.supervise_source_children(jobs,concurrency=concurrency,cpu_soft_seconds=cap['mode_cpu_seconds']['full'],
            cpu_hard_seconds=cap['mode_cpu_seconds']['full']+cap['hard_cpu_margin'],
            wall_deadline_monotonic=time.monotonic()+cap['wall_seconds']-120,allocated_address_space_bytes=allocated,evidence=evidence)
    finally:
        outputs.written+=sum(p.stat().st_size for d in directories for p in d.rglob('*') if p.is_file())
        helper.apply_remaining_coordinator_cpu_limit(cap['mode_cpu_seconds']['full'],cap['mode_cpu_seconds']['full']+cap['hard_cpu_margin'])
        outputs.json('parallel-execution.json',evidence,kind='options_quote_parallel_execution_v1')
        if outputs.written>outputs.maximum_total:raise ValueError('quote shards exceeded physical output bound')
    results=[]
    for part,directory in zip(parts,directories):
        result=json.loads(checked(directory/'result.json',maximum=512*1024**2))
        if (result.get('passed') is not True or result['attempt_id']!=packet['attempt_id'] or result['partition']!=part
                or result['ordinal']!=part['ordinal'] or result['actual']['selected_dates']!=part['selected_dates']
                or result['actual']['selected_chains']!=[part['chain']]):raise ValueError('quote shard result ownership differs')
        results.append(result['actual'])
    return results,evidence


def worker(packet_path):
    resource.setrlimit(resource.RLIMIT_CPU,(120010,120010));resource.setrlimit(resource.RLIMIT_AS,(17179869184,17179869184))
    resource.setrlimit(resource.RLIMIT_FSIZE,(51539607552,51539607552))
    def interrupted(signum,frame):
        raise RuntimeError('registered quote coordinator interrupted: '+str(signum))
    for signum in (signal.SIGTERM,signal.SIGINT,signal.SIGXCPU):signal.signal(signum,interrupted)
    packet=json.loads(checked(packet_path));protocol=json.loads(checked(PROTOCOL,packet['protocol_sha256']))
    cap=effective_resources(protocol,packet['configuration']['operational_limits']);soft=cap['mode_cpu_seconds'][packet['mode']];hard=soft+cap['hard_cpu_margin']
    resource.setrlimit(resource.RLIMIT_CPU,(soft,hard))
    resource.setrlimit(resource.RLIMIT_AS,(cap['memory_bytes'],cap['memory_bytes']))
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref,publish_new
    from trading_research.operations.trials import TrialRegistry
    registry=TrialRegistry(ROOT/'evidence/trials');store=registry.artifacts;state=registry.state()
    attempt=state['attempts'][packet['attempt_id']];trial=state['trials'][packet['trial_id']]
    if (attempt['status']!='running' or attempt['trial_id']!=packet['trial_id'] or attempt['family']!=protocol['family']
            or trial['configuration']!=packet['configuration'] or trial['code_hash']!=packet['snapshot']['sha256']
            or os.getppid()!=packet['supervisor_pid'] or Path(packet_path).resolve()!=RUNS/packet['attempt_id']/'packet.json'):
        raise ValueError('options-quote worker does not identify its registered supervisor and attempt')
    manifest=store.read_json(artifact_ref(packet['snapshot']))['manifest']
    for name,sha in manifest.items():checked(ROOT/name,sha)
    checked(__file__,packet['runner_sha256'])
    if any(os.environ.get(k)!=v for k,v in packet['configuration']['thread_limits'].items()):raise ValueError('threadlimitschanged')
    if packet['mode']=='admit':
        actual=admit_sources(protocol,store,Path(packet_path).parent/"raw-admissions.jsonl")
        actual_ref=asdict(store.put_json(actual,kind=actual['kind']))
        output_bytes=actual_ref['size_bytes']
    else:
        from trading_research.research.auction_flow_storage import BoundedOutputs
        outputs=BoundedOutputs(Path(packet_path).parent/'outputs',maximum_total_bytes=cap['per_attempt_output_bytes']-32*1024**2,maximum_file_bytes=cap['per_attempt_output_bytes']-32*1024**2)
        actual=run_measurement(packet,protocol,store,outputs)
        actual_ref=asdict(store.put_json(actual,kind='options_quote_measurement_results_v1'))
        output_bytes=outputs.written+actual_ref['size_bytes']
    report={'success':True,'attempt_id':packet['attempt_id'],'trial_id':packet['trial_id'],'mode':packet['mode'],
        'protocol_sha256':packet['protocol_sha256'],'snapshot':packet['snapshot'],'actual':actual_ref,
        'source_files':actual.get('source_files'),'output_bytes':output_bytes,
        'cas_output_bytes':actual_ref['size_bytes'],
        'parallel_execution':actual.get('parallel_execution'),
        'full_family_complete':False,'context_models_complete':False,'model_fits':0}
    if output_bytes+len(encoded(report))*2>cap['per_attempt_output_bytes']:raise ValueError('event attemptoutput exceeded')
    publish_new(Path(packet_path).parent/'worker.json',encoded(report))
    return 0


def parent(mode,predecessor=None,pilot=None,oi=None):
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref,code_snapshot,digest,publish_new
    from trading_research.operations.trials import TrialRegistry
    raw=checked(PROTOCOL);protocol=json.loads(raw);sha=hashlib.sha256(raw).hexdigest()
    limits_raw=checked(OPERATIONAL_LIMITS)
    limits_ref={'path':str(OPERATIONAL_LIMITS),'sha256':hashlib.sha256(limits_raw).hexdigest(),'size_bytes':len(limits_raw)}
    cap=effective_resources(protocol,limits_ref)
    registry=TrialRegistry(ROOT/'evidence/trials');store=registry.artifacts
    protocol_ref=asdict(store.put_bytes(raw,kind=protocol['kind']))
    registry.register_family(protocol['family'],scope_ids=tuple(protocol['scope_ids']),protocol=protocol_ref,
        max_attempts=protocol['resources']['max_attempts'],cpu_budget_seconds=protocol['resources']['cpu_budget_seconds'])
    state=registry.state();used=0
    if cap['cpu_budget_seconds'] > state['effective_budgets'][protocol['family']]['cpu_budget_seconds']:
        raise ValueError('operational allocation exceeds the retained family budget')
    for attempt in state['attempts'].values():
        if attempt['family']!=protocol['family']:continue
        for ref in attempt.get('result_artifacts',[]):
            if ref['kind']=='options_quote_execution_v1':used+=store.read_json(artifact_ref(ref))['output_bytes']
    if used+cap['per_attempt_output_bytes']>cap['maximum_study_output_bytes']:raise ValueError('event totaloutput allowance exhausted')
    prior=None
    if predecessor:
        path=Path(predecessor).resolve()
        if not path.is_relative_to(RUNS):raise ValueError('event predecessor must be ownretainedexecution')
        prior_raw=checked(path);d=json.loads(prior_raw);attempt=state['attempts'].get(d.get('attempt_id'))
        if (d.get('success') is not True or d.get('mode')!='admit' or attempt is None or attempt['status']!='succeeded'
                or not any(r['sha256']==digest(d) for r in attempt['result_artifacts'])):raise ValueError('options-quote measurement needs exactaccepted admission')
        prior={'path':str(path),'sha256':hashlib.sha256(prior_raw).hexdigest(),'size_bytes':len(prior_raw)}
    if mode in ('pilot','full') and prior is None:raise ValueError('options-quote measurement needsadmission')
    oi_reference=None
    if mode in ('pilot','full'):
        if oi is None:raise ValueError('quote pilot/full requires --oi-execution')
        path=Path(oi).resolve()
        if not path.is_relative_to(ROOT/'reports/options-oi-runs'):raise ValueError('retained OI execution namespace required')
        raw=checked(path);oi_reference={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
        accepted_oi(oi_reference,store,full=mode=='full')
    pilot_reference=None
    if mode=='full':
        if not pilot:raise ValueError('full requires accepted pilot execution')
        path=Path(pilot).resolve();raw=checked(path);d=json.loads(raw);a=state['attempts'].get(d.get('attempt_id'))
        if (not path.is_relative_to(RUNS) or d.get('success') is not True or d.get('mode')!='pilot' or a is None or a['status']!='succeeded'
                or not any(ref['sha256']==digest(d) for ref in a['result_artifacts'])):raise ValueError('registered accepted pilot required')
        pilot_reference={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
    snapshot=code_snapshot(ROOT,store);runner_sha=hashlib.sha256(checked(__file__)).hexdigest()
    helper_raw=checked(ROOT/'tools/auction_flow_parallel.py');helper_sha=hashlib.sha256(helper_raw).hexdigest()
    config={'operational_limits':limits_ref,'implementation_paths':[] if mode=='admit' else implementation_paths(),'mode':mode,'protocol_sha256':sha,'predecessor':prior,'pilot':pilot_reference,'runner_sha256':runner_sha,
        'oi_execution':oi_reference,'parallel_helper_sha256':helper_sha,
        'parallel_helper_source':asdict(store.put_bytes(helper_raw,kind='options_quote_parallel_helper_source_v1')),
        'runner_source':asdict(store.put_bytes(checked(__file__),kind='options_quote_runner_source_v1')),
        'thread_limits':{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','ARROW_NUM_THREADS':'1'}}
    trial=registry.register(name='options-quote:'+mode,family=protocol['family'],stage='original' if mode=='admit' else 'representation',
        configuration=config,code_hash=snapshot.sha256,data_hashes={'protocol':sha},fold_version='2020plus-options-quote-v1',target_version='options-quote-curve-observation-v1')
    soft=cap['mode_cpu_seconds'][mode];hard=soft+cap['hard_cpu_margin'];attempt=registry.start(trial,cpu_reservation_seconds=hard)
    out=RUNS/attempt;out.mkdir(parents=True,exist_ok=False)
    packet={'mode':mode,'attempt_id':attempt,'trial_id':trial,'snapshot':asdict(snapshot),'runner_sha256':runner_sha,
            'protocol_sha256':sha,'configuration':config,'supervisor_pid':os.getpid()}
    publish_new(out/'packet.json',encoded(packet));started=time.monotonic();process=None;usage=None;finished=False
    helper=quote_parallel_tools(packet);cleanup={'cpu_accounting_complete':True,'surviving_group_pids':[]}
    try:
        with (out/'worker.log').open('xb') as log:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(out/'packet.json')],cwd=ROOT,
                env={**os.environ,**config['thread_limits'],'PYTHONHASHSEED':'0'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            while True:
                pid,status,usage_now=os.wait4(process.pid,os.WNOHANG)
                if pid:
                    usage=usage_now;process.returncode=os.waitstatus_to_exitcode(status)
                    cleanup=helper.cleanup_reaped_coordinator_group(process.pid);break
                if time.monotonic()-started>cap['wall_seconds']:
                    cleanup=helper.terminate_then_kill_group(process.pid);usage=cleanup['usage'];process.returncode=cleanup['exit_code'];break
                time.sleep(.2)
        worker_value=json.loads(checked(out/'worker.json')) if (out/'worker.json').exists() else None
        observed_cpu=None if usage is None else usage.ru_utime+usage.ru_stime
        cpu=observed_cpu if cleanup['cpu_accounting_complete'] and observed_cpu is not None else max(hard,observed_cpu or 0)
        peak=0 if usage is None else usage.ru_maxrss*1024;wall=time.monotonic()-started
        success=bool(process.returncode==0 and worker_value and worker_value['success'] and worker_value['attempt_id']==attempt
                     and worker_value['trial_id']==trial and worker_value['snapshot']==asdict(snapshot)
                     and cleanup['cpu_accounting_complete'] and cpu<=soft and peak<=cap['memory_bytes'] and wall<=cap['wall_seconds'])
        worker_ref=None if worker_value is None else asdict(store.put_json(worker_value,kind='options_quote_worker_v1'))
        raw_progress = 0
        output_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+(raw_progress if worker_value is None else worker_value['cas_output_bytes']+worker_ref['size_bytes'])
        success=success and output_bytes<=cap['per_attempt_output_bytes']
        report={'kind':'options_quote_execution_v1','family':protocol['family'],'mode':mode,'attempt_id':attempt,'trial_id':trial,
            'configuration_implementation_paths':config['implementation_paths'],'protocol':protocol_ref,'snapshot':asdict(snapshot),'runner_sha256':runner_sha,'success':success,'worker':worker_ref,
            'cpu_seconds':cpu,'observed_cpu_seconds':observed_cpu,'cpu_accounting_complete':cleanup['cpu_accounting_complete'],
            'cleanup':{k:v for k,v in cleanup.items() if k!='usage'},'wall_seconds':wall,'peak_rss_bytes':peak,'output_bytes':output_bytes,
            'exit_code':process.returncode,'finished_at':datetime.now(timezone.utc).isoformat()}
        ref=store.put_json(report,kind=report['kind']);registry.finish(attempt,status='succeeded' if success else 'failed',cpu_seconds=cpu,
            wall_seconds=wall,peak_rss_bytes=peak,reason='bounded options-quote study result; all failures retained',result_artifacts=(asdict(ref),))
        finished=True;publish_new(out/'execution.json',encoded(report));print(json.dumps({'report':str(out/'execution.json'),'success':success,'cpu_seconds':cpu}),flush=True)
        return 0 if success else 1
    finally:
        if not finished:
            if process is not None and process.returncode is None:
                cleanup=helper.terminate_then_kill_group(process.pid);usage=cleanup['usage'];process.returncode=cleanup['exit_code']
            registry.finish(attempt,status='interrupted',cpu_seconds=0 if process is None else None if usage is None or not cleanup['cpu_accounting_complete'] else usage.ru_utime+usage.ru_stime,
                wall_seconds=time.monotonic()-started,peak_rss_bytes=0 if usage is None else usage.ru_maxrss*1024,reason='options-quote supervisor failure; reservation retained if usageunknown')


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':raise SystemExit(worker(sys.argv[2]))
    if len(sys.argv)==4 and sys.argv[1]=='--shard':raise SystemExit(quote_shard(sys.argv[2],sys.argv[3]))
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('admit','pilot','full'))
    parser.add_argument('admission',nargs='?');parser.add_argument('pilot',nargs='?')
    parser.add_argument('--oi-execution')
    args=parser.parse_args()
    raise SystemExit(parent(args.mode,args.admission,args.pilot,args.oi_execution))
