#!/usr/bin/env python3
"""Verify source identities and every retained daily completion, once per unique file."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
import time
from pathlib import Path
import sys
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack import historical_runner as hr


def verify_pair(item):
    path,digest=item
    for attempt in range(6):
        try:
            actual=hr.file_digest(path)
            break
        except hr.NativeEvidenceError as error:
            if 'file changed while hashing' not in str(error) or attempt==5:raise
            time.sleep(2)
    if actual!=digest:raise ValueError('verified file changed: '+str(path))


def verify_pairs(items,workers,label):
    # Bound queued work while overlapping independent filesystem reads. Each
    # file still receives the original full SHA and before/after identity check.
    items=list(items);iterator=iter(items);done=0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while batch:=list(islice(iterator,4096)):
            list(pool.map(verify_pair,batch));done+=len(batch)
            print(label,done,'/',len(items),flush=True)


def main(root,workers=32):
    root=Path(root).resolve();registry,manifest=hr.load_registry(root)
    composition=hr.read(root/'protocol/CALENDAR_RECOVERY_COMPOSITION.json')
    inputs=hr.read(root/'validation/INPUT_RECEIPTS.json')
    collection=hr.read(root/'validation/COLLECTION_REVIEW.json')
    collection_rows={r['coverage_id']:r for r in manifest['branches'] if r['method_id']=='STOIC-DATA'}
    assert {j['coverage_id'] for j in collection['jobs']}==set(collection_rows)
    for receipt in collection['jobs']:
        assert hr.file_digest(receipt['path'])==receipt['sha256']
        doc=hr.verify_job(hr.read_job(receipt['path']),registry,collection_rows[receipt['coverage_id']])
        inputs.extend(doc.get('input_receipts',[]))
        inputs.extend(doc.get('domain_observations',{}).values())
    unique={}
    for item in inputs:
        if item.get('cache_identity') is not None:
            unique[item['path']]=item['artifact_sha256']
            for s in item['cache_identity']['sources']:
                path=str(hr.ROOT/'data'/s['path'])
                if path in unique and unique[path]!=s['sha256']:raise ValueError('conflicting source hashes')
                unique[path]=s['sha256']
        elif item.get('path') and item.get('sha256'):
            path=item['path']
            if path in unique and unique[path]!=item['sha256']:raise ValueError('conflicting input hashes')
            unique[path]=item['sha256']
    verify_pairs(sorted(unique.items()),workers,'verified inputs')
    population=hr.read(root/'protocol/ACQUIRED_INPUT_POPULATION.json')
    for path,expected in population['files_at_freeze'].items():
        st=Path(path).stat()
        actual={'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'ctime_ns':st.st_ctime_ns,'inode':st.st_ino}
        if actual!=expected:raise ValueError('owned source stat changed: '+path)
    for rows in population['context_files_at_freeze'].values():
        for row in rows:
            st=Path(row['path']).stat()
            if st.st_size!=row['bytes'] or st.st_mtime_ns!=row['mtime_ns']:
                raise ValueError('context input changed: '+row['path'])
    baseline=hr.read(root/'protocol/BASELINE_SOFTWARE.json')
    for path,digest in baseline['files'].items():
        if hr.file_digest(hr.ROOT/path)!=digest:raise ValueError('accepted implementation changed: '+path)
    preserved=hr.read(root/'protocol/PRESERVED_WORKTREE.json')
    for path,item in preserved['files'].items():
        if item['body'] not in (hr.ROOT/path).read_text():
            raise ValueError('preserved user document body missing: '+path)
    counts={};failure_receipts=[]
    for run in (root,Path(composition['recovery_run']['path'])):
        reg,rows=hr.load_registry(run);completed=0;jobs=0;checkpoint_pairs=[]
        expected={r['coverage_id'] for r in rows['branches']
            if not (r['method_id']=='STOIC-DATA' and r['branch']=='process_review')}
        for day in reg['scope']['evaluation_dates']:
            done=hr.read(run/'jobs/evaluation'/day/'completion.json')
            assert done['registry_sha256']==reg['registry_sha256']
            assert {j['coverage_id'] for j in done['jobs']}==expected
            for j in done['jobs']:
                checkpoint_pairs.append((j['path'],j['sha256']));jobs+=1
            completed+=1
        verify_pairs(checkpoint_pairs,workers,'verified checkpoint jobs')
        counts[str(run)]={'sessions':completed,'daily_jobs':jobs,'registry_sha256':reg['registry_sha256']}
        for path in (run/'failures').rglob('*.json'):
            receipt=hr.read(path)
            failure_receipts.append({'path':str(path),'sha256':hr.file_digest(path),
                'resolution':'date has a verified completed checkpoint under its original registry',
                'original_failure':receipt})
    result={'status':'pass','verification_workers':workers,'unique_verified_input_files':len(unique),'input_files':unique,
        'collection_jobs_verified':collection['jobs'],
        'all_primary_and_recovery_completions':counts,'baseline_software_files_unchanged':len(baseline['files']),
        'preserved_user_document_bodies':list(preserved['files']),
        'owned_source_stats_unchanged':len(population['files_at_freeze']),
        'failure_history_with_resolution':failure_receipts}
    hr.immutable_json(root/'validation/FULL_INPUT_VERIFICATION.json',result)
    print('pass',len(unique),'inputs',counts)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);p.add_argument('--workers',type=int,default=32)
    a=p.parse_args();main(a.run_root,a.workers)
