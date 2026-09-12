"""Hand-authored C01/C03/C04 fixtures with actual timed local observations.

These remain synthetic research helpers. Native provenance is tested separately
with immutable files in test_phase1_native_contracts and native_windows.
"""
from copy import deepcopy
from decimal import Decimal

MINUTE = 60_000_000_000


def install(fixtures):
    for spec in fixtures:
        if spec.get('_completion_native_v2'):
            continue
        fid, inp = spec['id'], spec['inputs']
        if fid in {'O001-F1','O001-F1a','O001-F1b','O001-F1c'}:
            start = inp['bars'][0]['start']
            end = start + 5*MINUTE
            count = 4 if fid == 'O001-F1c' else 5
            bars = [{'bar_id':f'{fid}:m{i}','instrument_id':'NQ','start':start+i*MINUTE,
                     'end':start+(i+1)*MINUTE,'known_at':start+(i+1)*MINUTE,
                     'O':Decimal(100),'H':Decimal(101),'L':Decimal(99),'C':Decimal(100),
                     'V':Decimal(2),'complete':True} for i in range(count)]
            trades = [{'event_id':f'{fid}:t{i}','instrument_id':'NQ','t':start+i*MINUTE+1,
                       'price':Decimal(100),'size':2,'side':None if fid=='O001-F1a' else 'B'} for i in range(count)]
            spec['inputs'] = {'bars':bars,'trades':trades,'instrument_id':'NQ','start_ns':start,'end_ns':end,
                'required_fields':['ohlcv','aggressor','trades'],'known_at':end,'use_at':end+MINUTE,
                'trade_coverage':{'start_ns':start,'end_ns':end,'coverage_ok':True,
                                  'missing_intervals':[],'evidence_id':f'{fid}:synthetic-tape-membership'}}
            if fid == 'O001-F1a':
                spec['expected']={'price_coverage':True,'side_coverage':None,'coverage_ok':None,'state':'hole'}
            elif fid == 'O001-F1c':
                # A missing minute is unknown coverage, not an observed complete
                # negative. The gap is exactly the unsupplied final minute.
                spec['inputs']['trade_coverage']['coverage_ok']=None
                spec['inputs']['trade_coverage']['missing_intervals']=[[start+4*MINUTE,end]]
                spec['expected']={'price_coverage':None,'side_coverage':None,'coverage_ok':None,
                                  'missing_intervals':[[start+4*MINUTE,end]],'state':'hole'}
            else:
                spec['expected']={'price_coverage':True,'side_coverage':True,'coverage_ok':True,'state':'computed'}
        elif fid == 'O003-F1b':
            spec['inputs']={**deepcopy(inp),'clock_verified':True}
            spec['expected']={'clock_check':True,'clock_verified':True,'available':True,'bar_close_at':inp['end_ns']}
        elif fid == 'O004-F1':
            end=inp['end_ns'];start=end-2*MINUTE
            members=[]
            for i,row in enumerate(inp['members']):
                members.append({**row,'bar_id':f'{fid}:m{i}','instrument_id':'NQ',
                                'start':start+i*MINUTE,'end':start+(i+1)*MINUTE,
                                'known_at':start+(i+1)*MINUTE,'complete':True})
            spec['inputs']={**deepcopy(inp),'members':members,'instrument_id':'NQ','start_ns':start,
                            'kind':'time','size_minutes':2,'bar_id':'fixture-two-minute'}
            spec['expected']={'O':Decimal(100),'H':Decimal(103),'L':Decimal(99),'C':Decimal(102),
                              'V':Decimal(30),'complete':True,'start':start,'end':end,'known_at':end}
        else:
            continue
        spec['_completion_native_v2']=True


__all__=['install']
