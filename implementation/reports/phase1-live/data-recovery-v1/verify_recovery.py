"""Verify source identity, census scope, recovered input and preserved baseline."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;EMP=OUT.parent/'empirical'
def digest(p):
    h=sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    c=read(OUT/'BAR_CENSUS.json');t=read(OUT/'TAPE_RECONCILIATION.json');r=read(OUT/'RECOVERED_AUGUST_REFERENCE.json');s=read(OUT/'SUMMARY.json')
    sources={}
    for doc in [c,t,r]:
        for key,value in doc['source_files'].items():
            if key in sources:assert value['sha256']==sources[key]['sha256']
            sources[key]=value
    for key,value in sorted(sources.items()):
        p=ROOT/key;assert p.stat().st_size==value['bytes'];assert digest(p)==value['sha256'],key
    manifest_path=ROOT/'data/manifests/files.parquet';manifest=pq.read_table(manifest_path).to_pylist()
    raw=[key for key in sources if key.startswith('data/quantpad/')]
    for key in raw:
        owner=[x for x in manifest if x['archive_path']==key.removeprefix('data/')]
        assert len(owner)==1 and owner[0]['bytes']==sources[key]['bytes'],key
        md=pq.ParquetFile(ROOT/key).metadata
        assert md.num_rows==owner[0]['rows'] and md.num_row_groups==owner[0]['row_groups'],key
    # Derive required prior-date set independently from accepted checkpoints.
    expected=set();rule_jobs=Counter();NY=ZoneInfo('America/New_York');windows={w['window_id']:w for w in c['windows']}
    for p in (EMP/'checkpoints').glob('bar-*.json'):
        cp=read(p)
        assert digest(Path(cp['artifact_path']))==cp['artifact_sha256']
        for rule in cp['rules']:
            if rule['branch'] not in ['prior_day_level','prior_week_level','prior_month_level','continuation_retest']:continue
            if rule['status']=='missing_data':rule_jobs[rule['branch']]+=1
            for ref in rule['references']:
                for day in ref.get('missing_reference_dates',[]):expected.add((int(cp['instrument_id']),day))
    actual={(w['instrument_id'],datetime.fromtimestamp(w['start_ns']/1e9,NY).date().isoformat()) for w in c['windows'] if 'prior_RTH' in w['kinds']}
    assert actual==expected and len(actual)==1294
    assert sum(rule_jobs.values())==315
    for w in c['windows']:
        assert w['expected_minutes']==(w['end_ns']-w['start_ns'])//60_000_000_000
        assert w['missing_minutes']==sum(b-a for a,b in w['missing_minute_ranges'])
        assert w['expected_minutes']==w['same_contract_1m_minutes']+w['missing_minutes']
        assert w['one_second_recovery_slots']==sum(b-a for a,b in w['one_second_candidate_ranges'])
    assert len(c['observed_unknowns'])==8 and all(windows[u['window_id']]['missing_minutes']>0 and windows[u['window_id']]['one_second_recovery_slots']==0 for u in c['observed_unknowns'])
    sires=[j for j in c['jobs'] if j['branch']=='vwap_deviation_fade']
    assert len(sires)==102 and all(any('initial_VWAP_prefix' in windows[k]['kinds'] and windows[k]['missing_minutes']>0 for k in j['window_ids']) for j in sires)
    assert s['bar_groups']['overnight']['unique_recovery_slots']==0
    assert len(t['windows'])==4 and sum(w['standalone_rows'] for w in t['windows'])==946027
    assert all(w['same_execution_multiset'] and not w['aggregated_1s_vs_1m_mismatches'] and w['standalone_vs_1m_mismatches']==w['mbp_vs_1m_mismatches'] for w in t['windows'])
    patch_path=ROOT/r['recovered_input_path'];patch=pq.read_table(patch_path).to_pylist()
    assert len(patch)==len({(x['instrument_id'],x['t']) for x in patch})==780
    assert all(x['v']>0 and x['known_at_ns']==x['t']*1_000_000+60_000_000_000 for x in patch)
    assert r['reference']['complete_minute_grid'] and r['validation']['overlapping_RTH_minutes_compared']==7410 and r['validation']['OHLCV_mismatches']==0
    accepted=read(EMP/'RUN_MANIFEST.json');assert accepted['manifest_sha256']==s['accepted_manifest_sha256']
    for key,value in accepted['implementation']['files'].items():assert digest(ROOT/key)==value,key
    for split in accepted['splits'].values():assert digest(Path(split['path']))==split['sha256']
    assert not s['accepted_results_changed'] and not s['new_replay']
    artifact_hashes={p.name:digest(p) for p in OUT.iterdir() if p.is_file() and p.name!='VERIFICATION.json'}
    receipt={'schema':'phase1-data-recovery-verification-v1','passed':True,'source_files_rehashed':len(sources),'canonical_native_files_checked':len(raw),'canonical_manifest_sha256':digest(manifest_path),'prior_windows_reconciled_to_accepted_checkpoints':len(actual),'prior_missing_rule_jobs':dict(rule_jobs),'observed_unknown_prefixes_checked':8,'SIRES_initial_prefix_failures_checked':102,'tape_multiset_and_bar_resampling_checks':4,'recovered_patch_rows_verified':780,'accepted_implementation_and_splits_unchanged':True,'accepted_manifest_file_sha256':digest(EMP/'RUN_MANIFEST.json'),'new_test_suite_run':False,'artifact_sha256':artifact_hashes}
    (OUT/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='artifact_sha256'},indent=2))

if __name__=='__main__':main()
