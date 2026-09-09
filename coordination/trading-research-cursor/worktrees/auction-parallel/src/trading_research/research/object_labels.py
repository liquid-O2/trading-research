"""Literal discrete-observation reach and fixed-end ordered departure labels."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import groupby

from trading_research.errors import ContractError
from trading_research.foundations.contracts import Band
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest
from trading_research.research.labels import ObservationWindow


@dataclass(frozen=True)
class ExactPoint:
    at:int
    sequence:int
    price:Fraction
    known_at:int

    def __post_init__(self):
        timestamp(self.at);timestamp(self.known_at)
        if type(self.sequence) is not int or self.sequence<0 or not isinstance(self.price,Fraction):raise ContractError("ordered exact fractional-tick observation required")


@dataclass(frozen=True)
class ObjectTarget:
    id:str
    object_version:str
    cut:int
    end:int
    band:Band
    side:int
    favorable_distance:Fraction
    adverse_distance:Fraction
    observation_process:str
    contact_mode:str='future_contact'

    def __post_init__(self):
        if (any(type(v) is not str or not v for v in (self.id,self.object_version,self.observation_process))
                or self.end<=self.cut or type(self.side) is not int or self.side not in (-1,1)
                or type(self.band) is not Band or self.contact_mode not in ('future_contact','contact_at_cut')):
            raise ContractError("object label requires frozen identity, horizon, process and contact condition")
        if any(not isinstance(v,Fraction) or v<=0 for v in (self.favorable_distance,self.adverse_distance)):raise ContractError("positive frozen departure distances in exact ticks required")
        timestamp(self.cut);timestamp(self.end)

    @property
    def version(self):return digest(self)


def reference_object_label(target:ObjectTarget,*,initial:Fraction,points:tuple[ExactPoint,...],coverage:ObservationWindow):
    if not isinstance(initial,Fraction) or coverage.start!=target.cut or coverage.end>target.end:raise ContractError("initial observation and coverage must belong to the frozen target")
    rows=tuple(sorted(points,key=lambda p:(p.at,p.sequence)))
    if len({(p.at,p.sequence) for p in rows})!=len(rows) or any(not target.cut<p.at<=coverage.end for p in rows):raise ContractError("future object path has duplicate order or out-of-window points")
    if any(a<=p.at<b for p in rows for a,b in coverage.gaps):raise ContractError("observation inside a declared absent interval")
    maturity=max(coverage.certified_through,*(p.known_at for p in rows)) if rows else coverage.certified_through
    complete=coverage.end==target.end and not coverage.gaps
    result={'target_version':target.version,'object_version':target.object_version,'observation_version':coverage.version,
            'observed_end':coverage.end,'maturity_at':maturity,'reach_status':'censored' if not complete else 'no_contact',
            'contact_at':None,'contact_price':None,'gap_crossings':(), 'departure':'censored' if not complete else 'no_contact',
            'first_barrier_at':None,'maximum_favorable_ticks':None,'maximum_adverse_ticks':None,'fixed_end':target.end}
    if target.contact_mode=='contact_at_cut' and not target.band.contains(initial):raise ContractError("contact-conditioned prediction requires observable contact at its own cut")
    if not complete:return _gap_result(result,target,initial,rows,coverage)
    contact=(target.cut,initial) if target.contact_mode=='contact_at_cut' else None
    previous=initial;crosses=[];post=[]
    for at,batch in groupby(rows,key=lambda p:p.at):
        group=tuple(batch)
        if not coverage.source_order_known and len({p.price for p in group})>1:
            relevant=contact is None and any(target.band.contains(p.price) for p in group)
            crosses.extend(p.at for p in group if (previous<target.band.lower and p.price>target.band.upper) or (previous>target.band.upper and p.price<target.band.lower))
            if relevant:
                result.update(reach_status='contact',departure='ambiguous',gap_crossings=tuple(crosses),contact_at=at)
                return _gap_result(result,target,initial,rows,coverage)
            if contact is not None:post.extend(group)
            # Multiple orderings without any contact still cannot invent a touch.
            previous=group[-1].price
            continue
        for p in group:
            if (previous<target.band.lower and p.price>target.band.upper) or (previous>target.band.upper and p.price<target.band.lower):crosses.append(p.at)
            previous=p.price
            if contact is None:
                if target.band.contains(p.price):contact=(p.at,p.price)
            else:post.append(p)
    result['gap_crossings']=tuple(crosses)
    if contact is None:return _gap_result(result,target,initial,rows,coverage)
    result.update(reach_status='contact',contact_at=contact[0],contact_price=contact[1],departure='unresolved')
    deltas=[Fraction(0),*(target.side*(p.price-contact[1]) for p in post)]
    result['maximum_favorable_ticks']=max(deltas);result['maximum_adverse_ticks']=-min(deltas)
    for at,batch in groupby(post,key=lambda p:p.at):
        hits=[]
        for p in batch:
            d=target.side*(p.price-contact[1])
            if d>=target.favorable_distance or d<=-target.adverse_distance:hits.append('favorable_first' if d>=target.favorable_distance else 'adverse_first')
        if hits:
            result.update(departure='ambiguous' if not coverage.source_order_known and len(set(hits))>1 else hits[0],first_barrier_at=at);break
    return _gap_result(result,target,initial,rows,coverage)



def compatible_gap_evidence(target, initial, points, *, source_order_known=True,
                            maximum_states=4096, maximum_batch=8, maximum_transition_work=65536):
    """Enumerate bounded compatible source orders without selecting a last tick."""
    from itertools import permutations
    from math import factorial
    from trading_research.research.temporal_folds import bounded
    if (type(source_order_known) is not bool or type(target) is not ObjectTarget or type(initial) is not Fraction
            or any(type(value) is not int or not 1<=value<=cap for value,cap in
                   ((maximum_states,4096),(maximum_batch,8),(maximum_transition_work,65536)))):
        raise ContractError("explicit finite order evidence required")
    selected=bounded(points,4096,'gap observation')
    if any(type(p) is not ExactPoint for p in selected):
        raise ContractError('exact gap observation points required')
    rows=tuple(sorted(selected,key=lambda p:(p.at,p.sequence)))
    states={(initial,())}
    work=0
    for at,batch in groupby(rows,key=lambda p:p.at):
        group=tuple(batch)
        if len(group)>maximum_batch and not source_order_known:
            raise ContractError("unknown-order batch capacity exceeded")
        charge=len(states)*(1 if source_order_known else factorial(len(group)))*len(group)
        if work+charge>maximum_transition_work:
            raise ContractError('compatible-order transition work capacity exceeded')
        work+=charge
        orders=(group,) if source_order_known else permutations(group)
        following=set()
        for order in orders:
            for previous,crossings in states:
                times=list(crossings)
                for point in order:
                    if ((previous<target.band.lower and point.price>target.band.upper)
                            or (previous>target.band.upper and point.price<target.band.lower)):
                        times.append(at)
                    previous=point.price
                following.add((previous,tuple(times)))
                if len(following)>maximum_states:
                    raise ContractError("compatible-order capacity exceeded")
        states=following
    compatible=tuple(sorted({times for _,times in states}))
    sets=tuple(set(times) for times in compatible)
    return {'compatible_gap_crossing_times':compatible,
            'certain_crossing_time_set':tuple(sorted(set.intersection(*sets))) if sets else (),
            'possible_crossing_time_set':tuple(sorted(set.union(*sets))) if sets else ()}


def _gap_result(result,target,initial,rows,coverage):
    if not coverage.source_order_known and result['reach_status']!='censored':
        evidence=compatible_gap_evidence(target,initial,rows,source_order_known=False)
        result['gap_crossings']=evidence['certain_crossing_time_set']
    return result
