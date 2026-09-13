"""Join audit receipts, calendar evidence and exact remaining input requests."""
from pathlib import Path
from collections import Counter
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.easter import easter
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
MIN=60_000_000_000;NY=ZoneInfo('America/New_York')
def read(name):return json.loads((OUT/name).read_text())
def write(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def day(w):return datetime.fromtimestamp(w['start_ns']/1e9,NY).date()
def nth(y,m,weekday,n):
    d=date(y,m,1);return d+timedelta(days=(weekday-d.weekday())%7+7*(n-1))
def flags(d):
    y=d.year;flags=[]
    candidates={nth(y,1,0,3):'MLK',nth(y,2,0,3):'Presidents Day',nth(y,9,0,1):'Labor Day',nth(y,11,3,4):'Thanksgiving',nth(y,11,3,4)+timedelta(days=1):'post-Thanksgiving',easter(y)-timedelta(days=2):'Good Friday'}
    last=date(y,5,31);candidates[last-timedelta(days=last.weekday())]='Memorial Day'
    for yy in [y-1,y,y+1]:
        for m,dd,name in [(1,1,'New Year'),(7,4,'Independence Day'),(12,25,'Christmas')]+([(6,19,'Juneteenth')] if yy>=2022 else []):
            fixed=date(yy,m,dd);candidates[fixed]=name
            if fixed.weekday()==5:candidates[fixed-timedelta(days=1)]=name+' possible observance'
            if fixed.weekday()==6:candidates[fixed+timedelta(days=1)]=name+' possible observance'
    if d.month==12 and d.day==24 and d.weekday()<5:flags.append('Christmas Eve')
    if d.month==7 and d.day==3 and d.weekday()<5:flags.append('pre-Independence Day')
    if d in candidates:flags.append(candidates[d])
    if str(d) in ['2012-10-29','2012-10-30']:flags.append('Hurricane Sandy')
    if str(d)=='2018-12-05':flags.append('national mourning candidate')
    return flags

def main():
    c=read('BAR_CENSUS.json');t=read('TAPE_RECONCILIATION.json');r=read('RECOVERED_AUGUST_REFERENCE.json');cal=read('calendar_evidence.json')
    ws={w['window_id']:w for w in c['windows']};closed={x['date']:x for x in cal['verified_RTH_closures']}
    prior=[w for w in c['windows'] if 'prior_RTH' in w['kinds']]
    classified=[]
    for w in prior:
        d=str(day(w));status='verified_RTH_closed' if d in closed else 'holiday_candidate_hours_unverified' if flags(day(w)) else 'no_calendar_flag_hours_unverified'
        classification='recovered_from_owned_1s' if w['one_second_recovery_slots']==w['missing_minutes'] else 'verified_RTH_closed' if d in closed else w['classification']
        classified.append({'window_id':w['window_id'],'date':d,'instrument_id':w['instrument_id'],'raw_symbol':w['contract']['raw_symbol'],'input_classification':classification,'calendar_status':status,'calendar_flags':flags(day(w)),'source_url':closed.get(d,{}).get('source_url'),'contract_active_at_window_start':w['contract']['activation']<=w['start_ns']<w['contract']['expiration'],'consumers':w['consumers']})
    assert all(x['contract_active_at_window_start'] for x in classified)
    write('PRIOR_REFERENCE_CLASSIFICATION.json',{'schema':'phase1-prior-reference-classification-v1','calendar_flags_are_diagnostic_only':True,'calendar_definition_changed':False,'native_contract_active_checks':len(classified),'counts':dict(Counter(x['input_classification'] for x in classified)),'calendar_counts':dict(Counter(x['calendar_status'] for x in classified)),'windows':classified})
    group_summary={}
    for group in ['prior','overnight','adjacent_small_reference']:
        jobs=[j for j in c['jobs'] if j['group']==group];keys={i for j in jobs for i in j['window_ids']}
        missing={(ws[i]['instrument_id'],m) for i in keys for a,b in ws[i]['missing_minute_ranges'] for m in range(a,b)}
        recovery={(ws[i]['instrument_id'],m) for i in keys for a,b in ws[i]['one_second_candidate_ranges'] for m in range(a,b)}
        group_summary[group]={'job_status_counts':dict(Counter(j['status'] for j in jobs)),'unique_windows':len(keys),'unique_missing_slots':len(missing),'unique_recovery_slots':len(recovery)}
    # Every requested window has complete schema and identity requirements;
    # dates with unresolved calendars require calendar verification before purchase.
    requests=[]
    for w in t['windows']:
        requests.append({'priority':1,'kind':'receive_clock_native_executions','instrument_id':w['instrument_id'],'start_ns':w['start_ns']-1_000_000_000,'end_ns':w['end_ns']+1_000_000_000,'purpose':f"{w['date']} {w['role']}",'dataset':'GLBX.MDP3','schema':'trades or MBO/MBP with execution records','required_fields':['instrument_id','ts_event','ts_recv','sequence','action','price','size','side','flags'],'acceptance':'Native same-instrument rows with source identity, deterministic duplicate/sequence handling, declared trade conditions and clock; independently reconcile every minute OHLCV and preserve aggressor. No fitted shifts.'})
    for x in classified:
        if x['input_classification'] in ['verified_RTH_closed','recovered_from_owned_1s']:continue
        w=ws[x['window_id']]
        requests.append({'priority':2,'kind':'same_contract_prior_RTH','window_id':w['window_id'],'raw_symbol':x['raw_symbol'],'instrument_id':x['instrument_id'],'start_ns':w['start_ns'],'end_ns':w['end_ns'],'calendar_status':x['calendar_status'],'current_input_classification':x['input_classification'],'dataset':'GLBX.MDP3','schema':'native 1m/1s or complete executions','acceptance':'Verify historical NQ matching calendar first; retrieve this outright contract for this date, with identity and source completeness. Front-continuous substitution does not supply a different contract history.'})
    keys={i for j in c['jobs'] if j['group']=='overnight' for i in j['window_ids']}|{x['window_id'] for x in c['observed_unknowns']}
    for key in sorted(keys):
        w=ws[key]
        if not w['missing_minutes']:continue
        requests.append({'priority':3,'kind':'overnight_reference_or_VWAP_prefix','window_id':key,'instrument_id':w['instrument_id'],'raw_symbol':w['contract']['raw_symbol'],'start_ns':w['start_ns'],'end_ns':w['end_ns'],'missing_minute_ranges':w['missing_minute_ranges'],'range_units':'epoch minutes, half-open','first_absent_minute_ns':w['first_absent_minute_ns'],'roles':w['kinds'],'consumers':w['consumers'],'dataset':'GLBX.MDP3','schema':'native executions plus sequence/gap and session-status evidence; compare existing 1m/1s','acceptance':'Certify full requested prefix/reference and classify every absent minute as confirmed no-execution, scheduled pause or feed gap. No forward-fill; TDO requires a declared opening observation. For action diagnostic spans, first absent minute is the selector stop.'})
    write('REMAINING_INPUT_REQUESTS.json',{'schema':'phase1-exact-recovery-input-requests-v1','submitted':False,'purchase_authorized':False,'calendar_filter_required_before_acquisition':True,'selection':'Dependency/coverage only; no candidate score or return selection','counts':dict(Counter(str(q['priority']) for q in requests)),'requests':requests})
    summary={'schema':'phase1-three-priority-recovery-summary-v1','accepted_phase1_complete':True,'accepted_manifest_sha256':'d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247','accepted_results_changed':False,'new_replay':False,'tape_windows':len(t['windows']),'tape_executions_compared':sum(w['standalone_rows'] for w in t['windows']),'tape_mismatched_minutes':sum(len(w['standalone_vs_1m_mismatches']) for w in t['windows']),'mbp_repairs':0,'tape_clock_conclusion':'Documented event/receive-clock incompatibility is consistent with boundary discrepancies; actual receive timestamps unavailable, so per-execution cause is not proven.','bar_groups':group_summary,'prior_classifications':dict(Counter(x['input_classification'] for x in classified)),'calendar_status_counts':dict(Counter(x['calendar_status'] for x in classified)),'observed_GB_VWAP_unknown_prefixes_audited':len(c['observed_unknowns']),'recovered_input_rows':r['validation']['patch_rows'],'recovered_reference_complete':r['reference']['complete_minute_grid'],'recovered_reference_job':'GB-FAIL:prior_month_level:comparison-v1|2026-09-01','remaining_input_request_counts':dict(Counter(str(q['priority']) for q in requests))}
    write('SUMMARY.json',summary)
    original=(OUT.parent/'evidence-review-v1/PHASE_AND_AUDIT_TABLES.md').read_text()
    original=original.replace('Accepted Phase 1 tables reproduced for this follow-on review. No new replay or test-suite run is represented here.','Accepted Phase 1 tables reproduced for the three-priority data recovery. The separate 780-row recovered input is not counted as a new empirical replay. No new family opportunity counts or test-suite run are represented here.')
    (OUT/'PHASE_AND_AUDIT_TABLES.md').write_text(original)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
