import gzip, json, pickle, sys
from collections import Counter, defaultdict
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
P='/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz'
reason_branch=defaultdict(Counter)      # reason -> branch -> branch-session count
reason_year=defaultdict(Counter)
status_branch=defaultdict(Counter)
unk_minutes_branch=Counter()            # branch -> sum of unknown minutes (branch-session dup)
unk_minutes_year=Counter()
distinct_unknown=set()                  # (date, minute_start_ns) distinct across census
distinct_required=set()                 # (date, minute) required by any branch  -- approximated by required_current_prefix
unavail_rows=[]                         # rows with unavailable_candidates>0
state_totals=Counter()
per_bs_unk=[]                           # (date, coverage_id, n_unknown_minutes, status)
calendar_state=Counter()
calendar_unknown=Counter()
n=0
with gzip.open(P,'rt') as f:
    for line in f:
        r=json.loads(line)
        n+=1
        d=r['date']; cid=r['coverage_id']; yr=d[:4]
        st=r['status']
        status_branch[cid][st]+=1
        cov=r['current_prefix_coverage']
        for k,v in (cov.get('states') or {}).items(): state_totals[k]+=v
        gaps=cov.get('unknown_intervals') or []
        reasons={it.get('reason') or it.get('id') or 'unspecified' for it in r['active_omissions']}
        if gaps:
            reasons.add('current input prefix has unknown intervals')
            unk_minutes_branch[cid]+=len(gaps); unk_minutes_year[yr]+=len(gaps)
            for a,b in gaps: distinct_unknown.add((d,a))
        per_bs_unk.append((d,cid,len(gaps),st))
        for rs in reasons:
            reason_branch[rs][cid]+=1; reason_year[rs][yr]+=1
        if r.get('unavailable_candidates'):
            unavail_rows.append((d,cid,r['unavailable_candidates'],r['job']['path']))
        cal=r.get('calendar') or {}
        calendar_state[(cal.get('state'),bool(cal.get('known')))]+=1
        if n%10000==0: print(n,file=sys.stderr,flush=True)
out=dict(n=n,reason_branch={k:dict(v) for k,v in reason_branch.items()},
         reason_year={k:dict(v) for k,v in reason_year.items()},
         status_branch={k:dict(v) for k,v in status_branch.items()},
         unk_minutes_branch=dict(unk_minutes_branch), unk_minutes_year=dict(unk_minutes_year),
         state_totals=dict(state_totals), unavail_rows=unavail_rows,
         calendar_state={str(k):v for k,v in calendar_state.items()},
         n_distinct_unknown=len(distinct_unknown))
json.dump(out,open(SC+'/coverage_summary.json','w'),indent=1)
pickle.dump({'distinct_unknown':distinct_unknown,'per_bs_unk':per_bs_unk},open(SC+'/coverage_detail.pkl','wb'))
print('rows',n,'distinct unknown minutes',len(distinct_unknown))
