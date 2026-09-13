"""Read-only exhaustive presence census for the three authorized recovery priorities."""
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import Counter
import hashlib
import json
import numpy as np
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
EMP=ROOT/'implementation/reports/phase1-live/empirical'
NY=ZoneInfo('America/New_York')
MIN=60_000_000_000
sources={}
def identity(p):
    key=str(p.relative_to(ROOT))
    if key not in sources:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''): h.update(chunk)
        sources[key]={'sha256':h.hexdigest(),'bytes':p.stat().st_size}
    return key

def read(p):
    identity(p); return json.loads(p.read_text())
def clock(date,hm):
    return int(datetime.fromisoformat(date+'T'+hm).replace(tzinfo=NY).timestamp())*10**9

def ranges(a):
    a=sorted(set(map(int,a)))
    if not a:return []
    out=[];start=prev=a[0]
    for x in a[1:]:
        if x!=prev+1:out.append([start,prev+1]);start=x
        prev=x
    out.append([start,prev+1]);return out

D=read(EMP.parent/'evidence-review-v1/DENOMINATOR_AUDIT.json')
inv=read(EMP/'coverage/native-inventory-all.json')['files']
windows={};jobs=[];unknowns=[]
def add(kind,i,start,end,consumer):
    assert start%MIN==end%MIN==0 and start<end
    key=f'{i}:{start//MIN}:{end//MIN}'
    if key not in windows:windows[key]={'window_id':key,'instrument_id':int(i),'start_ns':start,'end_ns':end,'kinds':[],'consumers':[]}
    w=windows[key]
    if kind not in w['kinds']:w['kinds'].append(kind)
    if consumer not in w['consumers']:w['consumers'].append(consumer)
    return key
prior={'prior_day_level','prior_week_level','prior_month_level','continuation_retest'}
overnight={'judas_reversal','internal_rotation','extension_reaction','asia_tdo_case','vwap_deviation_fade'}
for b in D['branches']:
    if not b['supported']:continue
    for j in b['jobs']:
        if j['cohort']!='bar-monthly' or j['status']=='completed':continue
        branch=b['branch']; group='prior' if branch in prior else 'overnight' if branch in overnight or b['method_id']=='GB-VWAP' else 'adjacent_small_reference'
        consumer=f"{b['rule_id']}|{j['date']}"
        r={k:j[k] for k in ['date','instrument_id','status','population_holes','checkpoint']};r.update(rule_id=b['rule_id'],branch=branch,group=group,consumer=consumer,window_ids=[])
        for ref in j['incomplete_references']:
            if 'missing_reference_dates' in ref:
                for day in ref['missing_reference_dates']:
                    r['window_ids'].append(add('prior_RTH',j['instrument_id'],clock(day,'09:30'),clock(day,'16:00'),consumer))
            elif 'formation_start' in ref:
                r['window_ids'].append(add('range_reference',j['instrument_id'],ref['formation_start'],ref['formation_end'],consumer))
        day=j['date'];prev=(datetime.fromisoformat(day)-timedelta(days=1)).date().isoformat()
        if branch=='asia_tdo_case':r['window_ids'].append(add('TDO_minute',j['instrument_id'],clock(day,'00:00'),clock(day,'00:01'),consumer))
        if branch=='vwap_deviation_fade':r['window_ids'].append(add('initial_VWAP_prefix',j['instrument_id'],clock(prev,'18:00'),clock(day,'09:30'),consumer))
        if 'missing_initial_opportunity_interval' in j['population_holes']:
            start=clock(day,'00:01' if branch=='asia_tdo_case' else '05:00')
            # Diagnostic full action span. Only its first absent minute is the selector stop.
            r['window_ids'].append(add('action_span_diagnostic',j['instrument_id'],start,clock(day,'16:00'),consumer))
        r['window_ids']=sorted(set(r['window_ids']));jobs.append(r)
for p in sorted((EMP/'checkpoints').glob('bar-*.json')):
    c=read(p);a=read(Path(c['artifact_path']))
    for r in a['records']:
        if r['opportunity']['method_id']=='GB-VWAP' and r['replay']['reason']=='boundary_snapshot_unavailable':
            day=c['session_date'];prev=(datetime.fromisoformat(day)-timedelta(days=1)).date().isoformat();oid=r['opportunity']['opportunity_id']
            end=r['replay']['completed_at']
            unknowns.append({'opportunity_id':oid,'date':day,'window_id':add('observed_unknown_VWAP_prefix',c['instrument_id'],clock(prev,'18:00'),end,oid)})
# Explicit calendar question shared by the January 2023 tape jobs.
add('tape_prior_RTH_calendar',next(c['instrument_id'] for p in (EMP/'checkpoints').glob('tape-*2023-01-03*') for c in [read(p)]),clock('2023-01-02','09:30'),clock('2023-01-02','16:00'),'2023-01-03 tape prior profile')

rollpath=ROOT/'data/derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet';identity(rollpath)
rolls=pq.read_table(rollpath,columns=['instrument_id','raw_symbol','segment_start_ms','segment_end_exclusive_ms']).to_pylist()
map_path=rollpath.with_name('nq-instruments.parquet');identity(map_path)
contracts=pq.read_table(map_path,columns=['instrument_id','raw_symbol','first_bar_ms','last_bar_ms','activation','expiration']).to_pylist()
contract={int(c['instrument_id']):c for c in contracts}
bar_files={kind:[f for f in inv if f['root']=='NQ' and f['dataset_key']==kind and f['canonical_owner']=='owned'] for kind in ['ohlcv_1m','ohlcv_1s']}
archive_start=min(f['observed_min_ns'] for f in bar_files['ohlcv_1m'])
for w in windows.values():
    w['_occupied']={kind:set() for kind in bar_files};w['_other']={};w['files']=[]
for kind,files in bar_files.items():
    for f in files:
        selected=[w for w in windows.values() if w['start_ns']<=f['observed_max_ns'] and w['end_ns']>f['observed_min_ns']]
        if not selected:continue
        p=ROOT/'data'/f['path'];key=identity(p)
        print(kind,p.name,'windows',len(selected),flush=True)
        t=pq.read_table(p,columns=['t','instrument_id']);ts=t['t'].to_numpy();ids=t['instrument_id'].to_numpy();assert np.all(ts[1:]>=ts[:-1])
        scale={'ms':10**6,'ns':1}[f['timestamp_unit']]
        for w in selected:
            lo,hi=np.searchsorted(ts,[w['start_ns']//scale,w['end_ns']//scale])
            wt=ts[lo:hi];wi=ids[lo:hi];same=wi==w['instrument_id']
            w['_occupied'][kind].update(map(int,np.unique(wt[same]//(MIN//scale))))
            if kind=='ohlcv_1m':
                for i in np.unique(wi[~same]):w['_other'].setdefault(int(i),set()).update(map(int,np.unique(wt[wi==i]//(MIN//scale))))
            w['files'].append({'path':key,'dataset':kind,'same_instrument_rows':int(same.sum())})
        del t,ts,ids
for w in windows.values():
    expected=set(range(w['start_ns']//MIN,w['end_ns']//MIN));m=w.pop('_occupied');other=w.pop('_other');missing=expected-m['ohlcv_1m'];recover=missing&m['ohlcv_1s']
    w.update(expected_minutes=len(expected),same_contract_1m_minutes=len(expected&m['ohlcv_1m']),same_contract_1s_occupied_minutes=len(expected&m['ohlcv_1s']),missing_minutes=len(missing),one_second_recovery_slots=len(recover),missing_minute_ranges=ranges(missing),one_second_candidate_ranges=ranges(recover),other_contracts=[{'instrument_id':i,'raw_symbol':contract.get(i,{}).get('raw_symbol'),'occupied_minutes':len(s&expected)} for i,s in sorted(other.items())])
    w['contract']=contract[w['instrument_id']]
    w['overlapping_roll_segments']=[r for r in rolls if r['segment_start_ms']*10**6<w['end_ns'] and (r['segment_end_exclusive_ms'] is None or r['segment_end_exclusive_ms']*10**6>w['start_ns'])]
    own_segments=[r for r in w['overlapping_roll_segments'] if int(r['instrument_id'])==w['instrument_id']]
    if not missing:classification='complete_native_minutes'
    elif w['end_ns']<=archive_start:classification='before_local_archive'
    elif w['start_ns']<archive_start:classification='straddles_archive_start'
    elif not own_segments and other:classification='different_front_contract_present'
    elif not own_segments:classification='outside_target_front_segment_no_bars'
    elif not m['ohlcv_1m']:classification='no_bars_calendar_or_feed_unresolved'
    else:classification='partial_minutes_calendar_or_sparse_or_feed_unresolved'
    w['classification']=classification
    w['first_absent_minute_ns']=min(missing)*MIN if missing else None
    w['calendar_status']='not_certified_by_presence_census'
summary={'jobs_by_group_status':dict(Counter(f"{j['group']}:{j['status']}" for j in jobs)),'unique_windows':len(windows),'prior_RTH_unique_windows':sum('prior_RTH' in w['kinds'] for w in windows.values()),'prior_classifications':dict(Counter(w['classification'] for w in windows.values() if 'prior_RTH' in w['kinds'])),'unique_missing_same_instrument_slots':len({(w['instrument_id'],m) for w in windows.values() for a,b in w['missing_minute_ranges'] for m in range(a,b)}),'unique_recoverable_slots':len({(w['instrument_id'],m) for w in windows.values() for a,b in w['one_second_candidate_ranges'] for m in range(a,b)}),'observed_unknown_prefixes':len(unknowns)}
identity(Path(__file__).resolve())
out={'schema':'phase1-data-recovery-bar-census-v1','admission':'Presence audit only. No zero-volume imputation, roll stitching, calendar policy replacement or replay. Action-span gaps after first absent minute are diagnostic, not additional selector failures.','summary':summary,'jobs':jobs,'observed_unknowns':unknowns,'windows':list(windows.values()),'source_files':sources}
(OUT/'BAR_CENSUS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2))
