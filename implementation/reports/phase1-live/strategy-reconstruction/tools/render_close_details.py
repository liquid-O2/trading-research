"""Correct the diagnostic close-up for decisions exactly at the study endpoint.

Reads frozen jobs unchanged. The generic renderer's strict end check falls
back to the open at 16:00; this artifact-only renderer includes that endpoint.
Original plots remain preserved, and the chart index links the reviewed view.
"""
from pathlib import Path
import argparse,inspect
from trading_research.research.method_pack import historical_charts as base
from trading_research.research.method_pack.historical_runner import load_registry,read,read_job,file_digest,immutable_json
from trading_research.research.method_pack.empirical_market import clock
from datetime import date
p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);args=p.parse_args();root=Path(args.run_root)
registry,coverage=load_registry(root);original=read(root/'charts/manifest.json');rows={r['coverage_id']:r for r in coverage['branches']}
source=inspect.getsource(base.render_example)
assert source.count('market.start<=at<market.end')==1
source=source.replace('market.start<=at<market.end','market.start<=at<=market.end')
namespace=dict(vars(base));exec(compile(source,'reviewed_endpoint_renderer','exec'),namespace)
outputs=[]
for example in original['examples']:
 row=rows[example['coverage_id']]
 if row['extra_unit'] or row['method_id'] in {'STOIC-DATA','STOIC-RISK'} or not example['candidate_id']:continue
 doc=read_job(example['job']['path']);e=next(e for e in doc['episodes'] if e['candidate_id']==example['candidate_id'])
 if e['decision_at']!=clock(date.fromisoformat(doc['session_date']),'16:00'):continue
 corrected=namespace['render_example'](root/'diagnostics/close-time',row,doc,example['job'],e)
 outputs.append({'original':example,'reviewed':corrected,'change':'local price view includes the 16:00 study endpoint; unchanged job/episode/values'})
out={'registry_sha256':registry['registry_sha256'],'original_renderer_sha256':file_digest(Path(base.__file__)),
 'review_renderer_sha256':file_digest(Path(__file__)),'examples':outputs}
immutable_json(root/'diagnostics/close-time/manifest.json',out)
print('Reviewed endpoint charts:',len(outputs))
