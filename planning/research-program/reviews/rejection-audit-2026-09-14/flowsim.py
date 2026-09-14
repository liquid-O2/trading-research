"""Re-run flow_stages/_catalyst_stages on the RECORDED local_flow chunks,
as-published and with the P1 fix (baseline = immediately preceding equal-duration
window, empty windows counted as opposing=0)."""
from decimal import Decimal as D
Q=D('.25');SECOND=10**9
CFG={'effort_seconds':5,'reward_ticks':3,'no_progress_ticks':2,'near_origin_ticks':3,
     'thinning_fraction':'.5','minimum_effort_events':2,'band_halfwidth_ticks':2}
def sign(s):return 1 if s=='long' else -1
DEC={'first','last','low','high','opponent_mean','origin','entry_px'}
def load(lf):
    out=[]
    for r in lf:
        c=dict(r)
        for k in DEC:
            if c.get(k) is not None:c[k]=D(str(c[k]))
        out.append(c)
    return out
def recompute_effort(chunks,fix):
    out=[]
    for i,r in enumerate(chunks):
        c=dict(r)
        if i==0:prev=None
        else:
            p=chunks[i-1]
            prev=p if (not fix or p['end']==r['start']) else {'opposing':0,'unknown':0}
        c['effort']=(None if r['unknown'] or (prev and prev['unknown']) else
            r['opponent_count']>=CFG['minimum_effort_events'] and r['opposing']>r['own']
            and (prev is None or r['opposing']>=prev['opposing']))
        out.append(c)
    return out
def flow_stages(chunks,side,origin,start):
    sg=sign(side);sel={}
    defense=next((r for r in chunks if r['start']>=start+CFG['effort_seconds']*SECOND and r['effort'] and r['no_progress'] is True and r['held']),None)
    sel['defense']=defense
    later=[r for r in chunks if defense and r['start']>=defense['end']]
    refresh=next((r for r in later if r['added_at'] is not None and r['opposing']>0 and r['held']),None);sel['refresh']=refresh
    thinning=next((r for r in later if refresh and r['start']>=refresh['end'] and r['unknown']==0 and r['opponent_mean']<=defense['opponent_mean']*D(CFG['thinning_fraction']) and r['opposing']<defense['opposing']),None);sel['thinning']=thinning
    reward=next((r for r in later if r['last'] is not None and sg*(r['last']-origin)>=Q*CFG['reward_ticks'] and r['unknown']==0 and r['own']>r['opposing']),None);sel['reward']=reward
    rr=next((r for r in later if reward and r['start']>=reward['end'] and r['low']<=reward['last']<=r['high']),None);sel['reward_retest']=rr
    sel['renewed']=next((r for r in later if rr and r['start']>=rr['end'] and r['unknown']==0 and r['own']>r['opposing'] and r['held']),None)
    sel['liftoff']=next((r for r in later if thinning and r['start']>=thinning['end'] and r['last'] is not None and D(2)*Q<=sg*(r['last']-origin)<=D(4)*Q and r['unknown']==0 and r['own']>r['opposing']),None)
    return sel
def catalyst(chunks,side,origin,st):
    sg=sign(side);cat=st['defense']
    release=next((r for r in chunks if cat and r['start']>=cat['end'] and r['last'] is not None and sg*(r['last']-origin)>=Q*3 and r['unknown']==0 and r['own']>r['opposing']),None)
    failure=next((r for r in chunks if release and r['start']>=release['end'] and r['last'] is not None and sg*(r['last']-origin)<=Q),None)
    refill=next((r for r in chunks if failure and r['start']>=failure['end'] and r['held'] and r['added_at'] is not None),None)
    drive=next((r for r in chunks if refill and r['start']>=refill['end'] and r['last'] is not None and sg*(r['last']-release['last'])>0 and r['unknown']==0 and r['own']>r['opposing']),None)
    retest=next((r for r in chunks if drive and r['start']>=drive['end'] and r['low']<=drive['last']<=r['high'] and r['unknown']==0 and r['own']>r['opposing']),None)
    pullback=next((r for r in chunks if release and r['start']>=release['end'] and r['last'] is not None and sg*(r['last']-release['last'])<0),None)
    cont=next((r for r in chunks if pullback and r['start']>=pullback['end'] and r['last'] is not None and sg*(r['last']-release['last'])>0 and r['unknown']==0 and r['own']>r['opposing']),None)
    return dict(catalyst=cat,release=release,failure=failure,refill=refill,drive=drive,retest=retest,pullback=pullback,continuation=cont)
def run(lf,side,fix):
    chunks=recompute_effort(load(lf),fix)
    origin=chunks[0]['origin'];start=chunks[0]['start']
    st=flow_stages(chunks,side,origin,start)
    return chunks,st,catalyst(chunks,side,origin,st)
