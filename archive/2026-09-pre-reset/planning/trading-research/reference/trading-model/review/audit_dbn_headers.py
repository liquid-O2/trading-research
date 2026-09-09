from pathlib import Path
import databento as db,itertools,json,time
base=Path('/workspace/data/databento');out=[];start=time.time()
for folder in sorted(base.glob('*options*')):
 files=sorted(folder.glob('*.dbn.zst'))
 for i in sorted({0,len(files)//2,len(files)-1}):
  p=files[i];s=db.DBNStore.from_file(p);m=s.metadata
  rec={'file':str(p),'bytes':p.stat().st_size,'schema':str(m.schema),'start_ns':m.start,'end_ns':m.end,'symbols':m.symbols,'partial':m.partial,'not_found':m.not_found,'mapping_count':len(m.mappings),'rows':[]}
  for r in itertools.islice(s,3):
   v={}
   for k in ['rtype','ts_event','ts_recv','ts_ref','instrument_id','publisher_id','sequence','side','action','price','size','quantity','stat_type','update_action','channel_id','flags','raw_symbol','underlying_id','expiration','strike_price','contract_multiplier','unit_of_measure_qty','instrument_class','security_type','min_price_increment','currency','settlement_currency','asset','open','high','low','close','volume']:
    if hasattr(r,k):
     x=getattr(r,k);v[k]=x if isinstance(x,(int,float,str,bool)) or x is None else str(x)
   rec['rows'].append(v)
  out.append(rec)
(Path('/workspace/planning/trading-model/review/data-audit/dbn-header-samples.json')).write_text(json.dumps(out,indent=2))
print('files',len(out),'sample rows',sum(len(x['rows']) for x in out),'seconds',round(time.time()-start,2))
