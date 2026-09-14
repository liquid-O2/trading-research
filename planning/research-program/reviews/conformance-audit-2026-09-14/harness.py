"""Frozen HistoricalFeatures harness (pattern of tests/test_phase1_historical_replay.py)."""
import sys
sys.path.insert(0,'/workspace/implementation/src')
from datetime import date,timedelta
from decimal import Decimal as D
from trading_research.research.method_pack.adapters import normalize_mbp1_row
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.event_time import aggregate_events,VERSION,CONTRACT,MINUTE,SECOND
from trading_research.research.method_pack.historical_features import HistoricalFeatures

DAY=date(2026,1,15)
START=clock(DAY-timedelta(days=1),'18:00')
END=clock(DAY,'16:00')

def at(text,offset=0):return clock(DAY+timedelta(days=offset),text)

def raw(ns,px,size=1,side='B',action='T',index=0,bid_size=10,**kw):
    row=normalize_mbp1_row({'t':ns,'price':str(px),'size':size,'side':side,'action':action,
        'instrument_id':17,'flags':128,'bid_px':str(D(str(px))-D('.25')),'ask_px':str(D(str(px))+D('.25')),
        'bid_sz':bid_size,'ask_sz':10,**kw},source_file='conformance-fixture.parquet',source_row=index)
    row['event_id']=f"{row['source_file']}:{row['source_row']}"
    return row

class Market(HistoricalFeatures):
    """Same shape as the replay control; prior sessions and supplied records are empty."""
    def __init__(self,events,records=None):
        events=sorted(events,key=lambda r:r['event_ns'])
        for i,row in enumerate(events):
            row['source_row']=i;row['event_id']=f'conformance-fixture.parquet:{i}'
        self.events=events
        doc=aggregate_events(events,START,END,17)
        doc.update(schema=VERSION,contract_sha256=content_hash(CONTRACT),instrument_id=17,
            start_ns=START,end_ns=END,input_sha256=content_hash(doc),plan={'unowned_intervals':[]})
        super().__init__(DAY,document=doc,records=records)
    def local(self,start,end,*,book=False):
        return [r for r in self.events if start<=r['event_ns']<end and (book or r['action']=='T')]
    def prior(self,kind='day'):
        return {'kind':kind,'sessions':[],'omissions':[{'reason':'fixture: no prior session supplied'}],
                'scope_complete':False,'range':None}
    def supplied(self,kind,when):return []

def minute_series(lo,hi,px=100.0,step=60,size=1):
    """One print per `step` seconds across [lo,hi) at a flat price."""
    return [raw(t,px,size) for t in range(lo,hi,step*SECOND)]
