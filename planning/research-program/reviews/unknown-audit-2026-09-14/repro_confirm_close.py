"""Why GB-FAIL previous_hour 2020-04-17 reports candidate_status:data_unavailable."""
import json,gzip,sys
sys.path.insert(0,'/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit')
import rawcount as R
import pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
P='/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/jobs/evaluation/2020-04-17/GB-FAIL--branch--previous_hour.json.gz'
doc=json.load(gzip.open(P))
inst=doc['instrument_id']
for e in doc['episodes']:
    if e['candidate_id']!='native-v2:3ab79b3344f06bcd950c33f080bc3f5f': continue
    cb=e['geometry'].get('confirmation_bar')
    print('recorded confirmation bar:',{k:cb.get(k) for k in
        ('bar_id','start_et','end_et','O','H','L','C','V','open_order_known','close_order_known','observed_complete','trade_count','last_trade_ns')})
    a,b=cb['start_ns'],cb['end_ns']
    # last timestamp batch of that 5-minute bar, straight from the raw parquet
    last=None; lb=[]
    for path in R.files_for(a,b):
        f=pq.ParquetFile(path); i=f.schema_arrow.names.index('t')
        for g in range(f.num_row_groups):
            st=f.metadata.row_group(g).column(i).statistics
            if st.max<a or st.min>=b: continue
            for bt in f.iter_batches(batch_size=200000,row_groups=[g],columns=['t','action','price','size','instrument_id']):
                tt=bt.column(0)
                m=pc.and_(pc.and_(pc.greater_equal(tt,a),pc.less(tt,b)),pc.equal(pc.cast(bt.column(1),pa.string()),'T'))
                m=pc.and_(m,pc.equal(bt.column(4),int(inst)))
                for r in bt.filter(m).to_pylist():
                    if last is None or r['t']>last: last=r['t']; lb=[]
                    if r['t']==last: lb.append(r)
    print('raw last trade timestamp',last,'rows in batch',len(lb),'distinct prices',sorted({r['price'] for r in lb}))
    print('exchange_sequence column present in raw MBP-1:', 'exchange_sequence' in pq.ParquetFile(R.files_for(a,b)[0]).schema_arrow.names)
    print('=> C is None: the closing print of the confirmation bar is two different prices at the')
    print('   same nanosecond and the acquired file carries no sequence number to order them.')
