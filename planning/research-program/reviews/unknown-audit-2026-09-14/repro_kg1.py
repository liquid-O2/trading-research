"""Replay the KG1/key-gamma model input for the sampled dates where every file exists."""
import sys
sys.path.insert(0,'/workspace/implementation/src')
from datetime import date, datetime
import zoneinfo
from trading_research.research.method_pack.strategy_options import gamma_at
NY=zoneinfo.ZoneInfo('America/New_York')
class Stub:
    data_root='/workspace/data'
    input_receipts=[]
    def __init__(self,d): self.day=date.fromisoformat(d)
for d in ['2020-02-27','2023-12-28','2023-06-16','2024-09-20','2020-06-19','2021-03-05']:
    m=Stub(d)
    at=int(datetime(m.day.year,m.day.month,m.day.day,9,32,tzinfo=NY).timestamp())*10**9
    try:
        g=gamma_at(m,at)
    except Exception as e:
        print(d,'EXC',type(e).__name__,e); continue
    print(d,'available=',g.get('available'),'reason=',g.get('reason'),'regime=',g.get('regime'),
          'rejected=',g.get('rejected'),'contracts=',len(g.get('contracts',[])),'spot=',g.get('spot'))
