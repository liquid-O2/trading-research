"""P2 family: _control_absence certifies 'no control' from a zero-length window."""
import datetime,sys
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.historical_auction_scanners import _control_absence
from trading_research.research.method_pack.historical_assembly import absent
m=HistoricalFeatures(datetime.date(2021,1,4),data_root='/workspace/data',records={'strategy_reconstruction':True})
t=1609774260000000000   # control_search_window = [t,t] for 4 SAINT branches this session
print('window',[t,t],'length',0)
print('m.coverage(t,t).observed_scope_complete =',m.coverage(t,t)['observed_scope_complete'],'(no minute is inspected)')
print('absent(m,t,t) =',absent(m,t,t),'   <- historical_assembly.py:93 via event_time.py:298')
print('_control_absence(m,t,t,"short") =',_control_absence(m,t,t,'short'),'  <- historical_auction_scanners.py:28 `if end<=after:return False`')
print('published operands: control_evidence_recorded=False, repeated_aggression_in_trade_direction=False')
print('A2-BALANCE/C04 require unknown here: nothing was observed, so absence cannot be certified')
