"""Recover two absent RTH days from owned same-instrument one-second bars.

Produces a separately identified derived input under ignored data/. Does not
modify the frozen native archive or score/replay an exposed experiment.
"""
from datetime import date, timedelta
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from audit_tape import ROOT, OUT, identify, identities, native_rows, aggregates, physical_ranges
from zoneinfo import ZoneInfo
from datetime import datetime

ID=42004177
MIN=60_000_000_000
NY=ZoneInfo('America/New_York')
def clock(day,hm):return int(datetime.fromisoformat(str(day)+'T'+hm).replace(tzinfo=NY).timestamp())*10**9

def main():
    census=json.loads((OUT/'BAR_CENSUS.json').read_text())
    candidates=[w for w in census['windows'] if w['one_second_recovery_slots']]
    assert len(candidates)==2 and all(w['instrument_id']==ID and w['one_second_recovery_slots']==390 for w in candidates)
    start=clock(date(2026,8,1),'00:00');end=clock(date(2026,9,1),'00:00')
    paths=[ROOT/f'data/quantpad/cme__nq-continuous-futures__ohlcv-{k}/2026.parquet' for k in ['1m','1s']]
    rows=[native_rows(p,start,end,ID,bars=True) for p in paths]
    for frame in rows:
        assert len({r['t'] for r in frame})==len(frame), 'duplicate source timestamp/instrument'
        assert all(r['t']%1_000_000_000==0 and r['v']>0 and r['l']<=min(r['o'],r['c'])<=max(r['o'],r['c'])<=r['h'] for r in frame)
        assert all(float(r[k])*4==int(float(r[k])*4) for r in frame for k in ['o','h','l','c'])
    one,seconds=[aggregates(f,bars=True) for f in rows]
    days=[date(2026,8,1)+timedelta(days=i) for i in range(31) if (date(2026,8,1)+timedelta(days=i)).weekday()<5]
    expected={t for day in days for t in range(clock(day,'09:30'),clock(day,'16:00'),MIN)}
    overlap=expected&one.keys()&seconds.keys()
    mismatch=[t for t in overlap if any(one[t][k]!=seconds[t][k] for k in ['O','H','L','C','V'])]
    assert not mismatch
    missing=expected-one.keys();assert missing=={m*MIN for w in candidates for a,b in w['one_second_candidate_ranges'] for m in range(a,b)}
    assert not expected-seconds.keys()
    patch=[]
    source_members={}
    for row in rows[1]:
        minute=row['t']//MIN*MIN
        if minute in missing:source_members.setdefault(minute,[]).append(row)
    for t in sorted(missing):
        a=seconds[t];members=source_members[t]
        patch.append({'t':t//1_000_000,'o':a['O'],'h':a['H'],'l':a['L'],'c':a['C'],'v':a['V'],'instrument_id':ID,'known_at_ns':t+MIN,'source_second_rows':len(members),'source_physical_rows_sha256':physical_ranges(members)['row_ids_sha256']})
    outdir=ROOT/'data/derived/phase1-data-recovery-v1';outdir.mkdir(exist_ok=True)
    path=outdir/'NQU6-2026-08-03_04-RTH-1m-from-1s.parquet'
    pq.write_table(pa.Table.from_pylist(patch),path,compression='zstd')
    reread=pq.read_table(path).to_pylist();assert reread==patch
    combined=dict(one);combined.update({t:seconds[t] for t in missing})
    reference={'instrument_id':ID,'raw_symbol':'NQU6','kind':'prior_month_RTH','expected_weekdays':[str(d) for d in days],'formation_start':min(expected),'formation_end':max(expected)+MIN,'known_at':max(expected)+MIN,'expected_minutes':len(expected),'original_1m_minutes':len(expected&one.keys()),'recovered_minutes':len(missing),'complete_minute_grid':not expected-combined.keys(),'high':max(combined[t]['H'] for t in expected),'low':min(combined[t]['L'] for t in expected),'volume':sum(combined[t]['V'] for t in expected),'definition_change':False,'input_resolution_change':'two missing dates subsampled from owned native 1s; existing 1m rows retained','source_faithful':False}
    identify(path);identify(Path(__file__).resolve());identify(OUT/'audit_tape.py');identify(OUT/'BAR_CENSUS.json')
    result={'schema':'phase1-recovered-prior-reference-v1','accepted_run_changed':False,'replay_run':False,'selection':'All recoverable slots from exhaustive census; selected before examining a follow-on outcome','recovered_input_path':str(path.relative_to(ROOT)),'reference':reference,'validation':{'overlapping_RTH_minutes_compared':len(overlap),'OHLCV_mismatches':len(mismatch),'missing_minutes_without_1s':len(expected-seconds.keys()),'patch_rows':len(patch),'patch_roundtrip_exact':True,'duplicate_timestamp_instrument_keys':0,'source_prices_on_quarter_point_tick':True},'source_membership':{'all_August_1m':physical_ranges(rows[0]),'all_August_1s':physical_ranges(rows[1]),'patch_1s':[{'start_ns':w['start_ns'],'end_ns':w['end_ns'],'membership':physical_ranges([r for r in rows[1] if w['start_ns']<=r['t']<w['end_ns']])} for w in candidates]},'source_files':identities,'limit':'Complete bar-grid recovery from owned native aggregates, not an independently certified execution feed or a trade-volume profile. Accepted empirical denominators stay frozen; any outcome replay must bind this new input identity explicitly.'}
    (OUT/'RECOVERED_AUGUST_REFERENCE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'reference':reference,'validation':result['validation'],'file':str(path)},indent=2))

if __name__=='__main__':main()
