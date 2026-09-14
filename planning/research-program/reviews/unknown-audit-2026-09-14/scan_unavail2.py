import json,gzip,collections,sys
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
s=json.load(open(SC+'/coverage_summary.json'))
rows=s['unavail_rows']
out=[];ops=collections.Counter()
for i,(d,cid,n,path) in enumerate(rows):
    doc=json.load(gzip.open('/workspace/'+path if not path.startswith('/') else path))
    for e in doc['episodes']:
        sa=e.get('strategy_assessment') or {}
        if sa.get('status')!='data_unavailable': continue
        vals=e.get('values') or {}; der=e.get('operand_derivations') or {}
        sel=set(e.get('selected_fields') or [])
        nones={k for k,v in vals.items() if v is None and k in sel}
        reasons={}
        for k in nones:
            reasons[k]={'operation':(der.get(k) or {}).get('operation'),'kind':(der.get(k) or {}).get('kind')}
            ops[((der.get(k) or {}).get('operation'),(der.get(k) or {}).get('kind'))]+=1
        out.append({'date':d,'coverage_id':cid,'candidate_id':e['candidate_id'],'decision_at':e['decision_at'],
                    'unavailable_conditions':sa.get('unavailable_conditions'),'none_fields':reasons,
                    'active_omissions':[o.get('reason') for o in doc['session_accounting']['active_omissions']],
                    'unknown_minutes':len(doc['session_accounting']['current_prefix_coverage']['unknown_intervals'])})
json.dump(out,open(SC+'/unavailable_detail.json','w'),indent=1)
for k,v in ops.most_common(60): print(v,k)
