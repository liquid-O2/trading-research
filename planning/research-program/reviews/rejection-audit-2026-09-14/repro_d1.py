"""D1: GB-VWAP continuation_context is rebound with the retest-absence answer."""
import datetime,sys
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.historical_assembly import absent
from trading_research.research.method_pack.branch_coverage import setting
MINUTE=60*10**9
day=datetime.date(2023,12,8)
m=HistoricalFeatures(day,data_root='/workspace/data',records={'strategy_reconstruction':True})
refs={n:m.range(m.at(lo,-1 if lo>='18:00' else 0),m.at(hi),n) for n,(lo,hi) in
      ((n,setting('gb_sessions')[n]) for n in ('asia','london'))}
asia,london=refs['asia'],refs['london']
begin=max(m.at('09:30'),asia['known_at'],london['known_at'])
boundary=max(asia['high'],london['high'])
rows=m.bars(begin,m.end,300)
breakout=next((r for r in rows if r['observed_complete'] and r['C'] is not None and r['C']>boundary),None)
print('asia high',asia['high'],'london high',london['high'],'boundary',boundary)
print('breakout close',breakout['C'],'-> line 308 continuation_context =',breakout['C']>boundary)
retest=None
for row in m.bars(breakout['end'],m.end):
    s=m.vwap(row['start'])
    if s['price'] is not None and row['L']<=s['price']<=row['H']:retest=row;break
deadline=min(m.end,breakout['end']+60*MINUTE)
if retest is not None and retest['known_at']>deadline:retest=None
print('retest in the declared 60m horizon:',retest is not None)
print('line 314 rebinds continuation_context = absent(breakout.end,deadline) =',absent(m,breakout['end'],deadline))
print('published operand in the accepted run: continuation_context=False, breakout_close=16044.5')
print('=> the True context evidence is discarded; a missing retest is reported as a failed context')
