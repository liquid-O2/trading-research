import ast, collections, hashlib, heapq, json, math
from pathlib import Path
from datetime import datetime, timezone
R=Path('/workspace/trading-research'); D=Path('/workspace/coordination/trading-research-cursor/auction-production-failure31-draft')
A=R/'reports/auction-flow-runs/eea751045b15bf143265901beda8afb8efade7074129706ebeb86417f79b73b7'
def read(p): return json.loads(Path(p).read_bytes())
def ref(p,kind):
 p=Path(p); b=p.read_bytes(); return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),size_bytes=len(b),kind=kind)
def save(p,v):
 p=Path(p)
 with p.open('x') as f: json.dump(v,f,sort_keys=True,separators=(',',':'),allow_nan=False); f.write('\n')
 return ref(p,v.get('kind','retained_performance_evidence'))
def key(w): return tuple(w[k] for k in ('root','source_path','source_metadata_sha256','event_start_ns','event_end_ns'))
def fk(w): return key(w)[:3]
e=read(R/'validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V19.json'); plan=read(e['production_plan']['path']); schedule=read(plan['schedule']['path']); windows={key(w):w for w in schedule['windows']}
refs=list(e['prior_production_window_receipts'])+[ref(p,'auction_flow_source_window_receipt_v1') for p in sorted((A/'outputs').glob('source-file-*/artifacts/*-window-receipt.json'))]
assert len(refs)==2939
receipts={}; identity=None; runtime=None
for reference in refs:
 assert ref(reference['path'],reference['kind'])==reference
 receipt=read(reference['path']); k=key(receipt['unit']); assert k in windows and receipt['unit']==windows[k] and k not in receipts
 assert receipt['success'] is True
 if identity is None: identity=receipt['producer_identity']; runtime=receipt['runtime_versions']
 assert receipt['producer_identity']==identity and receipt['runtime_versions']==runtime
 receipts[k]=receipt
for name,row in identity['files'].items():
 b=(R/name).read_bytes(); assert len(b)==row['size_bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],name
chains=collections.defaultdict(list)
for w in schedule['windows']: chains[fk(w)].append(w)
for group in chains.values():
 group.sort(key=lambda w:w['event_start_ns']); carry=None; missing=False
 for w in group:
  r=receipts.get(key(w))
  if r is None: missing=True; continue
  assert not missing and r['initial_continuation_identity']==carry
  carry=r['final_continuation_identity']
cat=save(R/'validation/AUCTION_FLOW_RETAINED_PRODUCTION_RECEIPTS_30.json',dict(kind='auction_flow_retained_production_receipt_catalog_v1',receipts=refs,receipt_count=len(refs),source_attempts=[r['attempt_id'] for r in [next(iter(receipts.values()))]] ,scope='Hash-bound complete window receipts; runtime, producer closure and contiguous prefix checked before registration. Original retained payload and carry authentication remains mandatory in registered verification.'))
statepath=Path('/workspace/planning/trading-research/state/CURRENT.json'); state=read(statepath)
weights=state['performance_diagnosis']['dispatch_order_hypothesis']['file_weights']; byfile={(x['root'],x['source_path'],x['source_metadata_sha256']):x for x in weights}
b=plan['reservation_basis']; years=collections.Counter((w['root'],w['year']) for w in schedule['windows']); remaining_cpu=0
for row in plan['files']:
 k=(row['root'],row['source_path'],row['source_metadata_sha256']); allw=chains[k]; left=[w for w in allw if key(w) not in receipts]
 reserve=sum(b['failure_bytes_per_source_year']/years[w['root'],w['year']] for w in allw)
 output=sum(w['native_instrument_cells_upper']*b['native_bytes_per_cell']+w['atomic_cells_per_instrument']*w['raw_instruments_per_window_upper']*b['compressed_measurement_bytes_per_atomic_cell']+w['physical_scan_rows']*b['trade_density']*b['bytes_per_trade']+b['metadata_bytes_per_window']+w['reader_batches_upper']*b['metadata_bytes_per_reader_batch'] for w in left)
 row['maximum_output_bytes']=math.ceil(output*b['empirical_margin']+reserve+16*1024**2)
 ratio=max(sum(w[field] for w in left)/sum(w[field] for w in allw) for field in ('native_instrument_cells_upper','physical_scan_rows')) if left else 0
 row.update(dispatch_work_weight=byfile[k]['cpu_weight']*ratio,remaining_windows=len(left),reused_prefix_windows=len(allw)-len(left))
 remaining_cpu+=row['dispatch_work_weight']
plan['dispatch_strategy']='largest_declared_file_first_v1'; plan['prior_receipt_catalog']=cat
plan['reservation_basis'].update(reuse_scope='Original 3589-window/167-file schedule unchanged. Empirical new output cost only for remaining 650 windows; all original root/year failure reserves preserved, plus 16MiB per file for packets/receipt publication. Retained output remains charged to its original attempts.',dispatch_weight_basis='Frozen attempt23 original file cost times max remaining/full native-cell and physical-scan-row fraction; original ordinal breaks ties.')
planref=save(R/'validation/AUCTION_FLOW_PRODUCTION_PLAN_V2.json',plan)
execution=read(A/'execution.json'); worker=read(A/'worker.json'); pool=execution['source_unit_parallel_execution']; durations={c['ordinal']:c['wall_seconds'] for c in pool['children']}
def makespan(order):
 slots=[0.0]*17
 for i in order:
  t=heapq.heappop(slots); heapq.heappush(slots,t+durations[i])
 return max(slots)
fifo=makespan(range(167)); reordered=makespan(sorted(range(167),key=lambda i:(-weights[i]['cpu_weight'],i)))
e['kind']='auction_flow_source_check_extension_v20'; e['version']=20; e['prior_production_window_receipts']=[]; e['prior_production_receipt_catalog']=cat; e['production_plan']=planref
e['production_continuation_check_modules']=['tests.test_auction_flow_parallel']; e['diagnose_first_unresolved_clock_after_file_failure']=True
cpu=math.ceil(1.5*remaining_cpu+10000); output=sum(f['maximum_output_bytes'] for f in plan['files'])+plan['coordinator_reserve_bytes']+16*1024**2
assert cpu+10 < 192000-57500.146783 and output<274877906944-47345260497
limits={**e['production_limits'],'cpu_seconds':cpu,'hard_cpu_seconds':cpu+10,'maximum_output_bytes':output,'wall_seconds':7200}
e['production_limits']=limits
e['performance_verification_scope']='One consolidated tools-only scheduling/failure-reporting fix verification. Reuse all authenticated 2939 complete prefixes, retain first actual remaining failures and raw neighbors. No scientific policy change, no downstream expansion, no automatic repair cycle or complete-population claim.'
e['performance_verification_cpu_basis']={'remaining_frozen_file_weights_seconds':remaining_cpu,'margin':1.5,'authentication_tests_failure_capture_controller_reserve_cpu_seconds':10000}
e['retained_validation_inputs'] += [cat,planref,ref(A/'execution.json','retained_performance_source_execution'),ref(A/'worker.json','retained_performance_source_worker')]
eref=save(R/'validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V20.json',e)
baseline=read(D/'baseline.json')
for name,field in [('tools/run_auction_flow_study.py','canonical_runner_sha256'),('tests/test_auction_flow_parallel.py','canonical_parallel_tests_sha256')]:
 original=(R/name).read_bytes(); assert hashlib.sha256(original).hexdigest()==baseline[field]
 draft=D/Path(name).name; ast.parse(draft.read_bytes()); (D/('before-'+Path(name).name)).write_bytes(original)
# Integration follows complete static review and metadata resource/reuse joins.
for name in ('tools/run_auction_flow_study.py','tests/test_auction_flow_parallel.py'): (R/name).write_bytes((D/Path(name).name).read_bytes())
measurement={'execution':ref(A/'execution.json','auction_flow_execution'),'worker':ref(A/'worker.json','auction_flow_worker_report'),'wall_seconds':execution['wall_seconds'],'cpu_seconds':execution['cpu_seconds'],'output_bytes':execution['attempt_output_bytes'],'failed_files':sum(c['exit_code']!=0 for c in pool['children']),'new_window_receipts':2931,'retained_prefix_windows':2939,'remaining_windows':650,'cpu_accounting_complete':execution['cpu_accounting_complete'],'within_declared_limits':execution['within_declared_limits'],'observed_pool_wall_seconds':pool['wall_seconds'],'fixed_observed_duration_fifo_counterfactual_seconds':fifo,'declared_weight_dispatch_counterfactual_seconds':reordered,'estimated_pool_reduction_seconds':fifo-reordered,'scope':'Counterfactual holds observed job durations fixed; failures and shared I/O contention remain. Not an observed rerun or full pipeline speedup.'}
state['performance_diagnosis']['completed_source_run30']=measurement
state['active_research_processes']=[]; state['auction_budget'].update(attempts_used=30,cpu_used_seconds=57500.146783,recorded_output_bytes=47345260497,check_extension=eref)
state['current_deliverable'].update(current_phase='single_consolidated_fix_integrated_ready_for_verification',current_blockers=['Original errors from 51 source files need capture; complete all-family/Context/Location runtime remains unmeasured.'],implementation_gate='Single consolidated pass integrated; one decisive registered verification, preserve failures and reassess without automatic repairs.')
state['performance_verification31']={'extension':eref,'plan':planref,'receipt_catalog':cat,'limits':limits,'status':'prepared_not_executed','producer_files_unchanged':len(identity['files'])}
state['updated_at']=datetime.now(timezone.utc).isoformat()
statepath.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
cpath=Path('/workspace/coordination/trading-research-cursor/state.json'); c=read(cpath)
for k in ('performance_diagnosis','current_deliverable','active_research_processes','auction_budget','performance_verification31','updated_at'): c[k]=state[k]
cpath.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
print(json.dumps({'receipt_count':len(refs),'producer_files_unchanged':len(identity['files']),'limits':limits,'remaining_cpu_weights':remaining_cpu,'output_GB':output/1e9,'estimated_ordering_saving_seconds':fifo-reordered,'integrated':True}))
