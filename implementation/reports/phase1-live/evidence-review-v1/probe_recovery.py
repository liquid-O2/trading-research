from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import hashlib
import json
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[4]
EMP=ROOT/'implementation/reports/phase1-live/empirical'
OUT=ROOT/'implementation/reports/phase1-live/evidence-review-v1'
OUT.mkdir(exist_ok=True)
inventory=json.loads((EMP/'coverage/native-inventory-all.json').read_text())
all_files=inventory['files']
specs=[]
for date,branch in [('2010-09-07','judas_reversal'),('2011-04-04','nyam_box'),('2014-05-01','nyam_box'),('2023-01-03','prior_day_level')]:
    cp=next(p for p in (EMP/'checkpoints').glob('bar-*.json') if date in p.name)
    checkpoint=json.loads(cp.read_text())
    rule=next(r for r in checkpoint['rules'] if r['branch']==branch)
    ref=rule['references'][0]
    specs.append({'label':f'{date} {branch} first reference', 'date':date,'instrument_id':int(checkpoint['instrument_id']),
                  'start_ns':ref['formation_start'],'end_ns':ref['formation_end'],'checkpoint':str(cp),'reference_id':ref['reference_id']})
for cp in sorted((EMP/'checkpoints').glob('bar-*.json')):
    checkpoint=json.loads(cp.read_text()); artifact=json.loads(Path(checkpoint['artifact_path']).read_text())
    hits=[r for r in artifact['records'] if r['opportunity']['method_id']=='GB-VWAP' and r['replay']['reason']=='boundary_snapshot_unavailable']
    if hits:
        row=hits[0];date=checkpoint['session_date']; day=datetime.fromisoformat(date).replace(tzinfo=ZoneInfo('America/New_York'))
        start=(day-timedelta(days=1)).replace(hour=18)
        specs.append({'label':f'{date} first GB-VWAP missing boundary prefix','date':date,'instrument_id':int(checkpoint['instrument_id']),
                      'start_ns':int(start.timestamp())*10**9,'end_ns':row['replay']['completed_at'],'checkpoint':str(cp),
                      'opportunity_id':row['opportunity']['opportunity_id']})
        break

digest_cache={}
def digest(path):
    if path not in digest_cache:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
        digest_cache[path]=h.hexdigest()
    return digest_cache[path]

rows=[]
for spec in specs:
    expected=set(range(spec['start_ns']//60_000_000_000,spec['end_ns']//60_000_000_000))
    occupied={};used=[]
    for kind in ['ohlcv_1m','ohlcv_1s']:
        minutes=set();physical_rows=0
        for f in all_files:
            if f['root']!='NQ' or f['dataset_key']!=kind or f['canonical_owner']!='owned':continue
            if f['observed_min_ns']>=spec['end_ns'] or f['observed_max_ns']<spec['start_ns']:continue
            path=ROOT/'data'/f['path'];scale={'ms':10**6,'ns':1}[f['timestamp_unit']]
            table=pq.read_table(path,columns=['t','instrument_id'],filters=[('t','>=',spec['start_ns']//scale),('t','<',spec['end_ns']//scale),('instrument_id','=',spec['instrument_id'])])
            times=table.column('t').to_pylist();physical_rows+=len(times)
            minutes.update(int(t)*scale//60_000_000_000 for t in times)
            used.append({'path':str(path),'sha256':digest(path),'dataset':kind,'rows_in_window':len(times)})
        occupied[kind]=minutes
        spec[f'{kind}_physical_rows']=physical_rows
        spec[f'{kind}_occupied_minutes']=len(minutes & expected)
    missing=expected-occupied['ohlcv_1m'];candidate=missing & occupied['ohlcv_1s']
    rows.append({**spec,'expected_clock_minutes':len(expected),'missing_minute_bars':len(missing),
                 'missing_minute_slots_with_one_second_rows':len(candidate),
                 'missing_minute_slots_without_one_second_rows':len(missing-candidate),
                 'first_missing_minutes_utc':[datetime.fromtimestamp(x*60,ZoneInfo('UTC')).isoformat() for x in sorted(missing)[:8]],
                 'candidate_recovery_minutes_utc':[datetime.fromtimestamp(x*60,ZoneInfo('UTC')).isoformat() for x in sorted(candidate)[:8]],
                 'input_files':used,
                 'admission':'presence probe only; no fabricated zero-volume bars, coverage certificate or replay change'})

# Optional feeds were metadata-available but deliberately not bound into the
# standalone-trade experiment. Inventory overlap is a follow-on investigation,
# not permission to substitute them into the accepted run.
alternatives=[]
for path in sorted((EMP/'checkpoints').glob('tape-*.json')):
    c=json.loads(path.read_text()); a=json.loads(Path(c['artifact_path']).read_text())
    for role in ['tape','prior_profile']:
        view=a[role];start,end=view['formation_start'],view['formation_end']
        matches=[{'path':f['absolute_path'],'canonical_owner':f['canonical_owner'],
                  'min_ns':f['observed_min_ns'],'max_ns':f['observed_max_ns']}
                 for f in all_files if f['root']=='NQ' and f['dataset_key']=='mbp1'
                 and f['observed_min_ns']<end and f['observed_max_ns']>=start]
        coverage=view['coverage']
        alternatives.append({'date':c['session_date'],'role':role,'instrument_id':c['instrument_id'],
                             'coverage_reason':coverage.get('coverage_reason'),'physical_rows':view['row_count'],
                             'mismatched_minutes':len({m['minute_start'] for m in coverage.get('mismatches',[])}),
                             'overlapping_mbp1_files':matches,
                             'limit':'file time overlap does not certify same-instrument event coverage or agreement'})
record={'source_inventory':{'path':str(EMP/'coverage/native-inventory-all.json'),'sha256':digest(EMP/'coverage/native-inventory-all.json')},
        'probe_script_sha256':digest(Path(__file__).resolve()),
        'schema':'phase1-evidence-recovery-presence-probes-v1','scope':'read-only bounded timestamp/instrument probes; no discovery or replay',
        'selection':'first missing Jumbo reference, both missing NYAM dates, January 2023 prior-day reference, first unknown GB-VWAP prefix; selected by coverage rather than outcome returns',
        'bar_probes':rows,'tape_alternatives':alternatives}
(OUT/'RECOVERY_PROBES.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'bar_probes':[{k:r[k] for k in ['label','expected_clock_minutes','missing_minute_bars','missing_minute_slots_with_one_second_rows','missing_minute_slots_without_one_second_rows']} for r in rows],
                  'tape_alternatives':[{k:r[k] for k in ['date','role','coverage_reason','mismatched_minutes']}|{'owned_mbp_files':sum(x['canonical_owner']=='owned' for x in r['overlapping_mbp1_files'])} for r in alternatives]},indent=2))
