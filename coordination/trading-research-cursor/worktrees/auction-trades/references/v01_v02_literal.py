"""Independent literal engineering arithmetic; no candidate imports.

Inputs are plain primitive records with Fraction prices. This module neither
reads golden expected fields nor imports trading_research modules.
"""
from fractions import Fraction
from itertools import permutations, product
import hashlib
import json


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


def path(initial, events, end, *, up=3, down=3, complete=True, ordered=True):
    if not complete:
        return {'state':'censored','terminal':None,'up':None,'down':None,'barrier':None,'at':None}
    points=sorted(events,key=lambda p:(p[0],p[1]))
    changes=[0]+[p[2]-initial for p in points]
    first='neither'; at=None
    for time in sorted({p[0] for p in points}):
        hits=set()
        for t,seq,price in points:
            if t!=time: continue
            side='upper' if price-initial>=up else 'lower' if price-initial<=-down else None
            if side:
                hits.add(side)
                if ordered:
                    first=side;at=time;break
        if hits:
            if not ordered: first='ambiguous' if len(hits)>1 else next(iter(hits));at=time
            break
    terminal=changes[-1]
    if not ordered and points and len({p[2] for p in points if p[0]==points[-1][0]})>1: terminal=None
    return {'state':'ambiguous' if first=='ambiguous' or terminal is None else 'observed',
            'terminal':terminal,'up':max(changes),'down':-min(changes),'barrier':first,'at':at}


def object_path(initial,events,lower,upper,*,cut=0,end=10,side=1,favorable=3,adverse=2,contact_at_cut=False):
    point=(cut,initial) if contact_at_cut else None
    gaps=[]; previous=initial; after=[]
    for time,sequence,price in sorted(events):
        if previous<lower and price>upper or previous>upper and price<lower: gaps.append(time)
        previous=price
        if point is None and lower<=price<=upper: point=(time,price)
        elif point is not None: after.append((time,sequence,price))
    if point is None: return {'contact':None,'departure':'no_contact','gaps':tuple(gaps)}
    first='unresolved';at=None;changes=[Fraction(0)]
    for time,sequence,price in after:
        delta=side*(price-point[1]);changes.append(delta)
        if first=='unresolved' and (delta>=favorable or delta<=-adverse):
            first='favorable_first' if delta>=favorable else 'adverse_first';at=time
    return {'contact':point,'departure':first,'at':at,'favorable':max(changes),
            'adverse':-min(changes),'gaps':tuple(gaps),'end':end}


def gap_orders(initial,batches,lower,upper):
    results=set()
    # Literal full cartesian product, independent of candidate state propagation.
    choices=[tuple(permutations(batch)) for _,batch in batches]
    for sequence in product(*choices):
        previous=initial;crossings=[]
        for (time,_),order in zip(batches,sequence):
            for price in order:
                if previous<lower and price>upper or previous>upper and price<lower: crossings.append(time)
                previous=price
        results.add(tuple(crossings))
    return tuple(sorted(results))


def temporal(rows,*,fit,start,end,embargo=0,training_start=None,roles=('train',)):
    ordered=sorted(rows,key=lambda s:(s['decision'],s['id']))
    train=[];evaluation=[];excluded=[]
    for row in ordered:
        if start<=row['decision']<end: evaluation.append(row['id'])
        if row['decision']>=start: continue
        failure=None;deps=()
        if training_start is not None and row['decision']<training_start: failure='outside_registered_training_window'
        elif row['role'] not in roles: failure='forbidden_phase_role'
        elif row['known']>fit: failure='label_not_mature_at_fit'
        elif any(d['known']>fit for d in row['dependencies']):
            failure='dependency_not_available_at_fit';deps=tuple(sorted(d['id'] for d in row['dependencies'] if d['known']>fit))
        else:
            deps=tuple(sorted(d['id'] for d in row['dependencies'] if d['kind']!='raw_past' and d['end']>=start-embargo))
            if row['target_end']>=start-embargo or deps: failure='forbidden_dependency_overlap'
        if failure is None: train.append(row['id'])
        else: excluded.append((row['id'],failure,deps))
    return tuple(train),tuple(evaluation),tuple(excluded)


def temporal_identity(records,*,id,fit,start,end,embargo=0,training_start=None,roles=('train',)):
    records=sorted(records,key=lambda row:(row['decision_at'],row['id']))
    primitive=[{'id':s['id'],'decision':s['decision_at'],'target_end':s['target_end'],
        'known':s['label_known_at'],'role':s['phase_role'],
        'dependencies':[{'id':d['id'],'kind':d['kind'],'end':d['end'],'known':d['known_at']} for d in s['dependencies']]}
        for s in records]
    train,evaluation,excluded=temporal(primitive,fit=fit,start=start,end=end,embargo=embargo,training_start=training_start,roles=roles)
    value={'type':'TemporalFoldV1','fields':{'id':id,'fit_at':fit,'evaluation_start':start,'evaluation_end':end,
        'embargo_ns':embargo,'training_start':training_start,'training_roles':roles,
        'training_ids':train,'evaluation_ids':evaluation,
        'exclusions':[dict(sample_id=i,reason=reason,dependency_ids=deps) for i,reason,deps in excluded],
        'sample_manifest_hash':hashlib.sha256(canonical(records)).hexdigest()}}
    return hashlib.sha256(canonical(value)).hexdigest()


def equal_group_weights(pairs):
    return tuple((identity,Fraction(1,sum(other==group for _,other in pairs))) for identity,group in pairs)


def beta_frequency(successes,count):
    return Fraction(successes+1,count+2)


def oi_query(prior_count,receipts,query,boundary,expiry=None):
    if expiry is not None and query>=expiry: return 'expiry_terminal',None
    visible=[r for r in receipts if r['known']<=query]
    if visible: return 'complete',max(visible,key=lambda r:r['known'])['count']-prior_count
    return ('pending' if query<boundary else 'censored_missing_publication'),None


def reset_episodes(prices,lower,upper,distance):
    # Literal contact indices; a new episode needs a qualifying intervening event.
    contacts=[i for i,p in enumerate(prices) if lower<=p<=upper]
    result=[None]*len(prices);episode=0;last=None
    for i in contacts:
        if last is None or any(p<=lower-distance or p>=upper+distance for p in prices[last+1:i]): episode+=1
        result[i]=episode;last=i
    return tuple(result)


def bounds(favorable,adverse,censored):
    n=favorable+adverse+censored
    return Fraction(favorable,n),Fraction(favorable+censored,n)


def interval_points(events,cut,end,gaps=()):
    return tuple((at,seq) for at,seq,*_ in events
                 if not cut<at<=end or any(a<=at<b for a,b in gaps))


def partial_contact(events,lower,upper,gaps):
    observed=sorted(p for p in events if lower<=p[2]<=upper and not any(a<=p[0]<b for a,b in gaps))
    return () if not observed else (('observed_contact',observed[0][0],Fraction(observed[0][2])),)


def observation_state(cut,end,observed,known,gaps=()):
    if not cut<=observed<=end: return 'invalid'
    return 'complete' if observed==end and not gaps else 'pending' if known<end else 'censored'


def primitive_violations(*,sequence=0,price_type='Ticks',order=True,gaps=(),version='v',at=1,cut=0):
    failures=[]
    if type(sequence) is not int or sequence<0: failures.append('sequence')
    if price_type!='Ticks': failures.append('price')
    if type(order) is not bool: failures.append('order')
    if any(a>=b or i and a<gaps[i-1][1] for i,(a,b) in enumerate(gaps)): failures.append('gaps')
    if type(version) is not str or not version: failures.append('version')
    if at<=cut: failures.append('cut')
    return tuple(failures)


def ledger_relation(generated,candidates,outcomes):
    from collections import Counter
    supplied=Counter(generated); owners=Counter(outcomes)
    return {'missing_candidates':tuple(sorted(set(generated)-set(candidates))),
        'missing_outcomes':tuple(sorted(set(generated)-set(outcomes))),
        'duplicate_generator':tuple(sorted(i for i,n in supplied.items() if n>1)),
        'duplicate_outcomes':tuple(sorted(i for i,n in owners.items() if n>1))}


def group_support(rows):
    return {'rows':len(rows),'dates':len({r['date'] for r in rows}),
            'episodes':len({r['episode'] for r in rows}),'endpoints':len({r['endpoint'] for r in rows})}


def frame_partition(rows):
    return {frame:tuple(i for i,f in rows if f==frame) for frame in sorted({f for _,f in rows})}


def group_splits(rows,start,end,training_start=None):
    evaluation={g for _,g,at in rows if start<=at<end}
    bad={g for _,g,at in rows if g in evaluation and not start<=at<end}
    if training_start is not None:
        training={g for _,g,at in rows if training_start<=at<start}
        bad.update(g for _,g,at in rows if g in training and at<training_start)
    return tuple(sorted(bad))


def legacy_population(rows,fit,start,end,embargo=0):
    ordered=sorted(rows,key=lambda r:(r[2],r[0]))
    train=tuple(i for i,g,at,known,last in ordered if at<start and known<=fit and last<start-embargo)
    evaluation=tuple(i for i,g,at,known,last in ordered if start<=at<end)
    purged=tuple((i,'label_not_mature_at_fit' if known>fit else 'dependency_interval_overlaps_evaluation_or_embargo')
        for i,g,at,known,last in ordered if at<start and (known>fit or last>=start-embargo))
    return train,evaluation,purged


def fit_edges(nodes,root,*,row,date,cut,fold,routes=None):
    """Finite adjacency-matrix closure and independent row/date/clock joins."""
    ids=sorted(nodes); index={i:n for n,i in enumerate(ids)}
    reach=[[False]*len(ids) for _ in ids]; failures=set()
    for i,node in nodes.items():
        for parent in node.get('parents',()):
            if parent not in nodes: failures.add(('missing',parent)); continue
            reach[index[i]][index[parent]]=True
            if nodes[parent]['at']>node['at']: failures.add(('edge_completion',parent))
    for k in range(len(ids)):
        for i in range(len(ids)):
            for j in range(len(ids)):
                reach[i][j]=reach[i][j] or reach[i][k] and reach[k][j]
    ancestors={root}|{i for i in ids if reach[index[root]][index[i]]}
    for i in ancestors:
        n=nodes[i]
        if reach[index[i]][index[i]]: failures.add(('cycle',i))
        if row in n.get('rows',()) or date in n.get('groups',()): failures.add(('heldout',i))
        if n['at']>cut: failures.add(('prediction_completion',i))
        expected=fold if i==root else (routes or {}).get(i,fold)
        if n['fold']!=expected: failures.add(('route',i))
    return tuple(sorted(failures)),tuple(sorted(ancestors))


def actual_fit_relation(allowed,labels,reads):
    return {'extra_labels':tuple(sorted(set(labels)-set(allowed))),
            'extra_reads':tuple(sorted(set(reads)-set(allowed))),
            'missing_reads':tuple(sorted(set(allowed)-set(reads)))}


def required_oof_rows(required,supplied):
    return tuple(sorted(set(required)-set(supplied)))


def phase_records(units):
    return tuple('EX-'+unit+'-P'+str(phase) for unit in units for phase in range(8))


def fixed_grid(initial,additions,complete):
    return (tuple(a+b for a,b in zip(initial,additions)),tuple(additions),not any(additions)) if complete else (None,None,None)


def immutable_revision_ids(original,appended):
    rows=list(original)
    for identity,previous,payload in appended:
        exact=[r for r in rows if r[0]==identity]
        if exact:
            if exact[0]!=(identity,previous,payload): return 'conflict',tuple(rows)
        elif previous!=(rows[-1][0] if rows else None): return 'predecessor',tuple(rows)
        else: rows.append((identity,previous,payload))
    return 'accepted',tuple(rows)


def legacy_wire(value,field_schema):
    """Independent old-field encoder; schema is frozen before candidate edits."""
    if hasattr(value,'__dataclass_fields__'):
        cls=type(value).__name__
        names=field_schema[cls]
        return {'type':cls,'fields':{name:legacy_wire(getattr(value,name),field_schema) for name in names}}
    if type(value) is tuple: return {'tuple':[legacy_wire(v,field_schema) for v in value]}
    if type(value) is bytes: return {'bytes':value.hex()}
    if value is None or type(value) in (str,int,bool): return value
    raise ValueError('unknown old wire scalar')


def legacy_encode(value,field_schema):
    return canonical({'format':1,'value':legacy_wire(value,field_schema)})
