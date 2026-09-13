"""Finalize verified report chunks with bounded-memory JSON and receipt metadata.

The numerical collector is unchanged. Full domain results remain in their
original hashed files; the verification index needs their identities only.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
import io
import json
from pathlib import Path
import pickle
import time
import report_census as r


class ChunkUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        if module in ('__main__','report_census') and name=='blank':return r.blank
        return super().find_class(module,name)


def load_state(path):
    with Path(path).open('rb') as f:
        state=ChunkUnpickler(f).load()
        if f.read():raise ValueError('extra bytes after aggregation state')
    return state


def stable_digest(path):
    for attempt in range(6):
        try:return r.hr.file_digest(path)
        except r.hr.NativeEvidenceError as error:
            if 'file changed while hashing' not in str(error) or attempt==5:raise
            time.sleep(2)


def stream_json(path,body):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:
        json.dump(body,f,default=r.hr.serializable,indent=2,sort_keys=True,allow_nan=False)
        f.write('\n')


def compact_state(state):
    state=dict(state)
    state['input_receipts']={key:({k:v for k,v in item.items() if k!='result'}
        if item.get('recipe_id') and item.get('path') and item.get('sha256') else item)
        for key,item in state['input_receipts'].items()}
    return state


def seal_chunk(args):
    root,days,registry,rows,recovery_root,recovery_registry,recovery_dates,wait,chunk=args
    identity={'helper_sha256':stable_digest(Path(r.__file__)),'registry_sha256':registry['registry_sha256'],'dates':days}
    marker=chunk/'COMPLETE.json'
    if marker.exists():
        receipt=r.hr.read(marker)
        if receipt['identity']!=identity:raise ValueError('chunk identity differs')
        for path,digest in receipt['files'].items():
            if stable_digest(path)!=digest:raise ValueError('chunk file changed')
        return {'path':str(marker),'sha256':stable_digest(marker),'recovered':False}
    state=load_state(chunk/'state.pickle')
    assert set(state['native'])==set(days)
    daily=[row for row in rows if not (row['method_id']=='STOIC-DATA' and row['branch']=='process_review')]
    expected_units=[day+':'+row['coverage_id'] for day in days for row in daily]
    assert state['eligible_ids']==state['included_ids']==expected_units
    assert state['total']['daily_jobs']==len(expected_units)
    assert set(state['bybranch'])=={row['coverage_id'] for row in daily}
    assert all(s['counts']['searched_sessions']==len(days) for s in state['bybranch'].values())
    assert sum(s['counts']['setups'] for s in state['bybranch'].values())==state['total']['setups']==len(state['setup_ids'])
    assert sum(s['counts']['observed_candidates'] for s in state['bybranch'].values())==len(state['features'])
    expected_hashes={}
    for day in days:
        source=recovery_root if day in recovery_dates else root
        done=r.hr.read(source/'jobs/evaluation'/day/'completion.json')
        assert state['native'][day]=={'executions':done['native_executions'],'input_sha256':done['native_input_sha256']}
        expected_hashes.update({item['path']:item['sha256'] for item in done['jobs']})
    assert state['job_hashes']==expected_hashes
    for path,digest in expected_hashes.items():
        if stable_digest(path)!=digest:raise ValueError('chunk source job changed')
    expected_lines={'coverage-exclusions.jsonl.gz':len(expected_units),
        'setup-records.jsonl.gz':len(state['setup_ids']),
        'non-setup-observations.jsonl.gz':len(days)*sum(r.measurement_scope(row['method_id'],row['branch'])!='entry_setup' for row in daily)}
    for name,count in expected_lines.items():
        with gzip.open(chunk/'records'/name,'rb') as f:
            observed=sum(1 for _ in f)  # EOF verifies every member's CRC/trailer.
        assert observed==count,(name,observed,count)
    paths=[chunk/'state.pickle',*sorted((chunk/'records').glob('*.gz'))]
    receipt={'identity':identity,'files':{str(path):stable_digest(path) for path in paths},
        'recovery':'Complete pickle, closed gzip CRCs, record counts and all source hashes verified after the final chunk receipt was not saved.'}
    r.hr.immutable_json(marker,receipt)
    return {'path':str(marker),'sha256':stable_digest(marker),'recovered':True}


def load_compact_chunk(args):
    chunk=args[-1];receipt=r.hr.read(chunk/'COMPLETE.json')
    identity={'helper_sha256':stable_digest(Path(r.__file__)),'registry_sha256':args[2]['registry_sha256'],'dates':args[1]}
    if receipt['identity']!=identity:raise ValueError('chunk identity differs')
    for path,digest in receipt['files'].items():
        if stable_digest(path)!=digest:raise ValueError('chunk file changed')
    state=load_state(chunk/'state.pickle')
    for path,digest in state['job_hashes'].items():
        if stable_digest(path)!=digest:raise ValueError('chunk source job changed')
    return compact_state(state)


def collect_missing_chunk(args):
    chunk=args[-1]
    if (chunk/'state.pickle').exists():return str(chunk)
    chunk.mkdir(parents=True,exist_ok=True)
    identity={'helper_sha256':stable_digest(Path(r.__file__)),
              'registry_sha256':args[2]['registry_sha256'],'dates':args[1]}
    r.hr.immutable_json(chunk/'COLLECTOR_IDENTITY.json',identity)
    state=r.collect_dates(args)
    with (chunk/'state.pickle').open('wb') as f:pickle.dump(state,f,protocol=5)
    return str(chunk)


def check(root):
    state=load_state(root/'aggregation-chunks/0002/state.pickle')
    compact=compact_state(state)
    old=r.merge_states([state]);new=r.merge_states([compact])
    assert all(old[key]==new[key] for key in old if key!='input_receipts')
    removed=0
    for key,item in old['input_receipts'].items():
        projected=new['input_receipts'][key]
        assert {k:v for k,v in item.items() if k!='result'}=={k:v for k,v in projected.items() if k!='result'}
        if 'result' in item and 'result' not in projected:
            assert item.get('recipe_id') and item.get('path') and item.get('sha256');removed+=1
    samples=[r.summarize(next(iter(old['bybranch'].values()))),*list(new['input_receipts'].values())[:30],
             {'path':Path('/workspace'),'tuple':(1,'a',None),'counts':r.Counter({'a':2})}]
    for item in samples:
        expected=json.dumps(r.hr.serializable(item),indent=2,sort_keys=True)+'\n'
        output=io.StringIO();json.dump(item,output,default=r.hr.serializable,indent=2,sort_keys=True,allow_nan=False);output.write('\n')
        assert output.getvalue()==expected
    result={'status':'pass','helper_sha256':stable_digest(Path(__file__)),
        'collector_sha256':stable_digest(Path(r.__file__)),'chunk_daily_jobs':old['total']['daily_jobs'],
        'all_measurement_and_selection_fields_equal':True,'verification_receipt_identities_preserved':True,
        'embedded_domain_results_replaced_by_existing_path_and_hash':removed,
        'JSON_serialization_equivalent_samples':len(samples)}
    stream_json(root/'validation/AGGREGATION_FINALIZATION_EQUIVALENCE.json',result)
    print(result,flush=True)


def main(root,workers,collect=False,wait=False):
    registry,manifest=r.hr.load_registry(root);days=registry['scope']['evaluation_dates']
    composition=r.hr.read(root/'protocol/CALENDAR_RECOVERY_COMPOSITION.json')
    recovery=Path(composition['recovery_run']['path']);rr,_=r.hr.load_registry(recovery)
    if not wait:
        for run,reg in ((root,registry),(recovery,rr)):
            assert all((run/'jobs/evaluation'/day/'completion.json').exists() for day in reg['scope']['evaluation_dates'])
    proof=r.hr.read(root/'validation/AGGREGATION_FINALIZATION_EQUIVALENCE.json')
    assert proof['helper_sha256']==stable_digest(Path(__file__))
    assert proof['collector_sha256']==stable_digest(Path(r.__file__))
    chunks=[days[i:i+25] for i in range(0,len(days),25)]
    work=[(root,chunk,registry,manifest['branches'],recovery,rr,set(composition['replace_all_daily_units_on_dates']),wait,
           root/'aggregation-chunks'/f'{i:04}') for i,chunk in enumerate(chunks)]
    if collect:
        with ProcessPoolExecutor(max_workers=workers) as pool:list(pool.map(collect_missing_chunk,work))
    for run,reg in ((root,registry),(recovery,rr)):
        while not all((run/'jobs/evaluation'/day/'completion.json').exists() for day in reg['scope']['evaluation_dates']):
            if not wait:raise ValueError('census incomplete before finalization')
            time.sleep(10)
    with ProcessPoolExecutor(max_workers=workers) as pool:receipts=list(pool.map(seal_chunk,work))
    stream_json(root/'validation/AGGREGATION_FINALIZATION.json',{
        'driver_sha256':stable_digest(Path(__file__)),'collector_sha256':stable_digest(Path(r.__file__)),
        'chunks':receipts,'domain_results':'Full values retained in original hashed domain files; verification index uses identity metadata.',
        'numerical_and_selection_changes':False})
    r.collect_chunk=load_compact_chunk;r.write_json=stream_json
    # Paths were local to the original serial collector; report rendering resolves
    # these names from its module after parallel collection.
    r.setup_path=root/'records/setup-records.jsonl.gz'
    r.coverage_path=root/'records/coverage-exclusions.jsonl.gz'
    r.other_path=root/'records/non-setup-observations.jsonl.gz'
    r.main(root,False,workers)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);p.add_argument('--workers',type=int,default=8)
    p.add_argument('--check',action='store_true');p.add_argument('--collect',action='store_true')
    p.add_argument('--wait-for-completion',action='store_true')
    a=p.parse_args();root=Path(a.run_root).resolve()
    check(root) if a.check else main(root,a.workers,a.collect,a.wait_for_completion)
