"""Read-only acquisition/representative-schema audit; not a production loader."""
from pathlib import Path
import os,json,time,collections
import pyarrow.parquet as pq
root=Path('/workspace/data');out=Path('/workspace/planning/trading-model/review/data-audit');out.mkdir(exist_ok=True)
t0=time.time(); inv=pq.read_table(root/'manifests/files.parquet').to_pylist(); by=collections.defaultdict(list)
for r in inv:by[r['dataset_id']].append(r)
actual={}
for provider in ['databento','derived','free-sources','quantpad','thetadata-opra']:
 for ds in os.scandir(root/provider):
  if ds.is_dir():
   for e in os.scandir(ds.path):
    if e.is_file():actual[str(Path(e.path).relative_to(root))]=e.stat().st_size
expected={r['archive_path']:r['bytes'] for r in inv}
recon={'inventoried_files':len(inv),'actual_dataset_files':len(actual),'expected_bytes':sum(expected.values()),'actual_bytes':sum(actual.values()),'missing':[p for p in expected if p not in actual],'extra':[p for p in actual if p not in expected],'size_mismatch':[{'path':p,'expected':n,'actual':actual[p]} for p,n in expected.items() if p in actual and actual[p]!=n],'datasets':len(by),'elapsed_seconds':time.time()-t0}
(out/'reconciliation.json').write_text(json.dumps(recon,indent=2));print('RECON',json.dumps(recon),flush=True)
results=[]
for ds,rows in sorted(by.items()):
 files=sorted([r for r in rows if r['format']=='parquet'],key=lambda r:r['archive_path'])
 if not files:continue
 indices=sorted(set([0,len(files)//2,len(files)-1]))
 for idx in indices:
  r=files[idx];p=root/r['archive_path']
  try:
   f=pq.ParquetFile(p);batch=next(f.iter_batches(batch_size=128,use_threads=False),None)
   d={'dataset':ds,'file':r['archive_path'],'manifest_rows':r['rows'],'footer_rows':f.metadata.num_rows,'row_groups':f.metadata.num_row_groups,'schema':str(f.schema_arrow),'manifest_min':r['observed_time_min'],'manifest_max':r['observed_time_max'],'sample_rows':batch.num_rows if batch else 0,'head':batch.slice(0,3).to_pylist() if batch else []}
   if batch:
    d['nulls_in_sample']={c:batch.column(j).null_count for j,c in enumerate(batch.schema.names) if batch.column(j).null_count}
    d['sample_extrema']={}
    for c in ['t','ts_event','ts_quote','ts_recv','price','bid','ask','bid_px','ask_px','size','open_interest','strike','instrument_id','action','side','valid_for_volume']:
     if c in batch.schema.names:
      vals=[v for v in batch.column(batch.schema.get_field_index(c)).to_pylist() if v is not None]
      if vals:d['sample_extrema'][c]={'min':str(min(vals)),'max':str(max(vals)),'distinct_count':len(set(vals))}
   results.append(d)
  except Exception as e:results.append({'dataset':ds,'file':r['archive_path'],'error':str(e)})
 (out/'parquet-samples.json').write_text(json.dumps(results,indent=2,default=str))
 print('SAMPLED',ds,len(indices),flush=True)
print('DONE',len(results),'files',len({r['dataset'] for r in results}),'datasets',round(time.time()-t0,2),'seconds',flush=True)
