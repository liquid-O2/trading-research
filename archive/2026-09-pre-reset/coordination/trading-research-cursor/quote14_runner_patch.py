from pathlib import Path
import json,hashlib
p=Path('/workspace/trading-research/tools/run_options_quote_study.py');s=p.read_text()
s=s.replace('OPTIONS_QUOTE_OPERATIONAL_LIMITS_V1.json','OPTIONS_QUOTE_OPERATIONAL_LIMITS_V2.json',1)
a=s.index('def effective_resources(');b=s.index('\ndef ',a+5)
s=s[:a]+'''def effective_resources(protocol, reference):
    document = json.loads(checked(reference['path'], reference['sha256']))
    allowed = {'per_attempt_output_bytes','mode_cpu_seconds','memory_bytes','wall_seconds','concurrency'}
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

''' +s[b:]
s=s.replace("cap=resources or protocol['resources'];reserve=1024**3;floor=32*1024**2", "cap=resources or protocol['resources'];reserve=6*1024**3;floor=256*1024**2")
# A partition is a measurement producer; final groups already include all years/stages.
s=s.replace("selected_dates=part['selected_dates'],selected_chains=[part['chain']])", "selected_dates=part['selected_dates'],selected_chains=[part['chain']],\n        calculate_statistics=False,execution_resources=cap)")
s=s.replace("selected_dates=selected,selected_chains=protocol['population']['chains'])", "selected_dates=selected,selected_chains=protocol['population']['chains'],execution_resources=cap)")
s=s.replace("resource.setrlimit(resource.RLIMIT_CPU,(60010,60010));resource.setrlimit(resource.RLIMIT_AS,(8589934592,8589934592))", "resource.setrlimit(resource.RLIMIT_CPU,(90010,90010));resource.setrlimit(resource.RLIMIT_AS,(17179869184,17179869184))")
s=s.replace("resource.setrlimit(resource.RLIMIT_FSIZE,(17179869184,17179869184))", "resource.setrlimit(resource.RLIMIT_FSIZE,(51539607552,51539607552))")
s=s.replace("cap=effective_resources(protocol,cfg['operational_limits'])\n    jobs=", "cap=effective_resources(protocol,cfg['operational_limits'])\n    resource.setrlimit(resource.RLIMIT_AS,(cap['memory_bytes'],cap['memory_bytes']))\n    jobs=")
s=s.replace("resource.setrlimit(resource.RLIMIT_CPU,(soft,hard))\n    sys.path", "resource.setrlimit(resource.RLIMIT_CPU,(soft,hard))\n    resource.setrlimit(resource.RLIMIT_AS,(cap['memory_bytes'],cap['memory_bytes']))\n    sys.path")
s=s.replace("cap=effective_resources(protocol,packet['configuration']['operational_limits']);concurrency=6", "cap=effective_resources(protocol,packet['configuration']['operational_limits']);concurrency=cap.get('concurrency',6)")
# Scale observation artifacts by admitted work; reports by their actual target graph.
s=s.replace("    projected_output=1.5*resources['output_bytes']*scale+512*1024**2\n    concurrency=6", """    group_count = int(pilot['group_count']) if 'group_count' in pilot else sum(
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
    concurrency=cap.get('concurrency',6)""")
s=s.replace("+load_cpu*max(1,oi_scale)+stats_cpu*len(p['selected_dates'])/8)", "+load_cpu*max(1,oi_scale))")
s=s.replace("    wall=max(loads)+600", "    wall=max(loads)+1.5*stats_cpu*date_scale+600")
s=s.replace("'projected_parallel_wall_seconds':wall,'concurrency':concurrency,'partitions':len(parts),", "'projected_parallel_wall_seconds':wall,'concurrency':concurrency,'partitions':len(parts),\n        'projected_measurement_output_bytes':production_output,'projected_statistics_output_bytes':statistics_output,\n        'maximum_statistical_groups':maximum_groups,'pilot_statistical_groups':group_count,\n        'memory_bytes_per_process':cap['memory_bytes'],'allocated_address_space_bytes':(concurrency+1)*cap['memory_bytes'],")
s=s.replace("'method':'separate measured parsing/boards, OI/support loading and statistics; full admitted source size and date population; repeated OI loading charged per partition'", "'method':'measured production scaled by admitted rows/bytes/dates; OI authentication charged per partition; statistics once after all partitions with date-scaled CPU and full declared target-count output plus uncompressed date-label allowance'")
s=s.replace("or wall>cap['wall_seconds']):raise ValueError", "or production_output>sum(p['output_bytes'] for p in parts)\n            or statistics_output>6*1024**3-512*1024**2 or wall>cap['wall_seconds']):raise ValueError")
# Pin the accepted result as an independent expected population in the pilot.
needle="    if packet['mode']=='pilot' and oi_execution['mode']=='full':\n"
s=s.replace(needle,"""    if packet['mode']=='pilot':
        operation=json.loads(checked(cfg['operational_limits']['path'],cfg['operational_limits']['sha256']))
        if operation.get('accepted_parity_execution'):
            prior_exec,expected=predecessor_actual(operation['accepted_parity_execution'],store,protocol,'pilot')
            actual['accepted_population_parity']=compare_quote_population(expected,actual,outputs)
"""+needle)
a=s.index('def run_measurement(')
helper='''def compare_quote_population(expected, actual, outputs):
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


'''
s=s[:a]+helper+s[a:]
p.write_text(s)
# Operational envelope remains inside the existing family CPU and output totals.
v=Path('/workspace/trading-research/validation');op=json.loads((v/'OPTIONS_QUOTE_OPERATIONAL_LIMITS_V1.json').read_text())
def ref(path,kind):
 raw=path.read_bytes();return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),'kind':kind}
prior=Path('/workspace/trading-research/reports/options-quote-runs/a930254c41bdac723592f14b04831f7caa96efe8624fefcef61cdccb99273830/execution.json')
op['overrides']={'per_attempt_output_bytes':46*1024**3,'memory_bytes':12*1024**3,'mode_cpu_seconds':{'admit':1800,'pilot':1200,'full':80000},'wall_seconds':36000,'concurrency':5}
op['accepted_parity_execution']=ref(prior,'options_quote_execution_v1');op['evidence']=ref(prior,'options_quote_execution_v1')
op['authority']='Existing explicit allDeliverable1 authorization. Original total90000CPU/48GiB retained, all13attempts charged. Operational source-date memory bound12GiB for admitted maximum11342128rows/day, five workers plus parent72GiB below83GBcgroup; full80kCPU within retained total. Final statistics once after partitions; full requires measured actualpilot14 and full-table/statistical parity to12.'
op['gate']='All48checks plus actual pilot and accepted12 population parity; separate observation output and complete final target graph; no full unless conservative measuredCPU/output/wall gate passes.'
(v/'OPTIONS_QUOTE_OPERATIONAL_LIMITS_V2.json').write_text(json.dumps(op,indent=2,sort_keys=True)+'\n')
import ast
ast.parse(s)
print('runner and operational envelope ready')
