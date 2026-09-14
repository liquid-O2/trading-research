import gzip,json,collections,pickle
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
P='/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz'
n=0; st=collections.Counter(); horiz=collections.Counter(); inc=[]
mref=[]
elig=collections.Counter()
for line in gzip.open(P,'rt'):
    r=json.loads(line); n+=1
    pm=r['price_measurement']
    st[pm.get('status')]+=1
    elig[bool(r.get('eligible_complete_session'))]+=1
    if pm.get('status')=='measurement_reference_unavailable':
        mref.append((r['session_date'],r['coverage_id'],pm.get('origin',{}).get('kind'),pm.get('origin',{}).get('at')))
    for h in pm.get('horizons',[]):
        horiz[(h['minutes'],h['status'],bool(h['horizon_truncated']))]+=1
        if h['status']!='complete_observed_horizon' and not h['horizon_truncated']:
            inc.append((r['session_date'],r['coverage_id'],h['minutes'],h['requested_end_ns'],h['observed_end_ns'],
                        len(h['coverage'].get('unknown_intervals') or []),h['coverage'].get('unknown_intervals') or []))
    b=pm.get('boundary') or {}
    if b: st['boundary:'+str(b.get('result'))]+=1
pickle.dump({'incomplete_not_truncated':inc,'measurement_reference_unavailable':mref},open(SC+'/setups.pkl','wb'))
print('setup records',n)
print('eligible_complete_session',dict(elig))
for k,v in sorted(st.items()): print(' ',k,v)
print('horizon counts:')
for k,v in sorted(horiz.items()): print('  ',k,v)
print('incomplete but NOT truncated:',len(inc))
for x in inc[:15]: print('   ',x[:6])
print('measurement_reference_unavailable:',len(mref))
