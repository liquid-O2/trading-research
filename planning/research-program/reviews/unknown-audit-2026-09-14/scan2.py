import gzip,json,pickle,sys
from collections import defaultdict
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
P='/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz'
reason_rows=defaultdict(list)   # reason -> [(date, coverage_id, detail)]
unk_rows=[]
n=0
for line in gzip.open(P,'rt'):
    r=json.loads(line); n+=1
    d,cid=r['date'],r['coverage_id']
    for it in r['active_omissions']:
        rs=it.get('reason') or it.get('id') or 'unspecified'
        det={k:v for k,v in it.items() if k in ('date','operand','required_input','window','required_fields','record_key','instrument_id')}
        reason_rows[rs].append((d,cid,det))
    g=r['current_prefix_coverage']['unknown_intervals'] or []
    if g: unk_rows.append((d,cid,len(g),g[0][0],g[-1][1],r['required_current_prefix'],r['calendar'].get('state'),r['status']))
pickle.dump({'reason_rows':dict(reason_rows),'unk_rows':unk_rows},open(SC+'/scan2.pkl','wb'))
for k,v in sorted(reason_rows.items(),key=lambda x:-len(x[1])): print(len(v),k)
print('unk rows',len(unk_rows))
