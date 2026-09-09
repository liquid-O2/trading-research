"""E0 frozen range objects and sampled first-inward-contact visit policy."""

from dataclasses import dataclass
from fractions import Fraction
import math

from trading_research.errors import ContractError,DependencyUnavailable
from trading_research.foundations.contracts import Band
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class FrozenRange:
    id:str
    instrument:str
    start:int
    end:int
    known_at:int
    low:Fraction
    high:Fraction
    open:Fraction
    close:Fraction
    observation_process:str
    source_version:str
    complete:bool
    # Optional source lineage added by the integration adapter.  These fields
    # deliberately come after the original positional contract so existing
    # E0 callers remain source compatible.
    instrument_lifetime:str|None=None
    clock_id:str|None=None
    selection_version:str|None=None
    publication_version:str|None=None
    supersedes:str|None=None
    source_identity:str|None=None

    def __post_init__(self):
        if not all((self.id,self.instrument,self.observation_process,self.source_version)) or not self.start<self.end<=self.known_at or any(not isinstance(v,Fraction) for v in (self.low,self.high,self.open,self.close)) or not self.low<=min(self.open,self.close)<=max(self.open,self.close)<=self.high:raise ContractError("range requires exact completed-window extrema and original process/contract identity")
        for value in (self.instrument_lifetime,self.clock_id,self.selection_version,
                      self.publication_version,self.supersedes,self.source_identity):
            if value is not None and (type(value) is not str or not value):
                raise ContractError("range lineage identities must be nonempty strings")
        if self.supersedes == self.id:
            raise ContractError("range revision cannot supersede itself")

    @property
    def width(self):return self.high-self.low
    @property
    def version(self):return digest(self)


@dataclass(frozen=True)
class E0Object:
    id:str
    type:str
    instrument:str
    price:Fraction
    band:Band
    born_at:int
    source_version:str
    range_width:Fraction|None
    source_role:str|None=None
    born_revision:int|None=None
    supersedes:str|None=None
    known_at:int|None=None

    def __post_init__(self):
        if (any(type(v) is not str or not v for v in (self.id,self.type,self.instrument,self.source_version))
                or type(self.price) is not Fraction or type(self.band) is not Band
                or not self.band.contains(self.price)
                or self.range_width is not None and (type(self.range_width) is not Fraction or self.range_width<0)):
            raise ContractError("E0 object requires frozen exact geometry and source identity")
        timestamp(self.born_at)
        if self.known_at is not None:
            timestamp(self.known_at)
            if self.known_at<self.born_at:
                raise ContractError("E0 object cannot be known before its birth")

    @property
    def available_at(self):return self.born_at if self.known_at is None else self.known_at

    @property
    def version(self):return digest(self)

    @property
    def observation_process(self):
        """Stable process label consumed by the population/label bridge.

        Older frozen objects carry this lineage as ``source_role``.  Expose
        the typed process name without changing their positional constructor
        or rehashing existing object identities.
        """
        return self.source_role or "frozen_e0_object"


def objects(range_06_09:FrozenRange|None,prior_rth:FrozenRange|None,*,cut:int):
    admitted=[]
    for row,role in ((range_06_09,'06_09'),(prior_rth,'prior_rth')):
        if row is None or row.known_at>cut or not row.complete:continue
        if role=='06_09':
            if row.width<=0:continue
            grid=(('low',Fraction(0)),('quarter_1',Fraction(1,4)),('eq',Fraction(1,2)),('quarter_3',Fraction(3,4)),('high',Fraction(1)),
                  ('lower_half_extension',Fraction(-1,2)),('lower_full_extension',Fraction(-1)),('upper_half_extension',Fraction(3,2)),('upper_full_extension',Fraction(2)))
            levels=[(name,row.low+k*row.width) for name,k in grid]
        else:levels=[('low',row.low),('high',row.high),('open',row.open),('close',row.close)]
        for name,price in levels:
            id=digest({'generator':'E0-frozen-grid-v1','parent':row.version,'role':role,'name':name})
            admitted.append(E0Object(id,role+':'+name,row.instrument,price,Band(price-1,price+1),row.known_at,row.version,
                                     range_06_09.width if range_06_09 and range_06_09.complete and range_06_09.known_at<=cut and range_06_09.width>0 else None))
    if len({o.instrument for o in admitted})>1:raise DependencyUnavailable("prior contract levels need an explicit known-time roll mapping before E0 contact comparison")
    return tuple(admitted)


@dataclass(frozen=True)
class Contact:
    object_id:str
    object_version:str
    visit:int
    at:int
    price:Fraction
    approach:int|None
    fade_side:int|None


class VisitTracker:
    def __init__(self,*,maximum_gap_ns:int):
        if type(maximum_gap_ns) is not int or maximum_gap_ns<=0:raise ContractError("sampled observation gap tolerance required")
        self.maximum_gap_ns=maximum_gap_ns;self.states={};self.last_cut=None

    def observe(self,*,cut:int,price:Fraction|None,candidates:tuple[E0Object,...]):
        if self.last_cut is not None and cut<=self.last_cut:raise ContractError("visit replay must advance decision cuts")
        if price is not None and not isinstance(price,Fraction):raise ContractError("exact midpoint observation required")
        gap=self.last_cut is not None and cut-self.last_cut>self.maximum_gap_ns;self.last_cut=cut
        contacts=[]
        for obj in candidates:
            if obj.available_at>cut:raise ContractError("object known_at exceeds decision cut")
            state=self.states.setdefault(obj.version,{'consumed':False,'outside':None,'visit':0})
            if gap or price is None:state['outside']=None
            if price is None:continue
            distance=price-obj.price
            inside=obj.band.contains(price)
            reset=max(Fraction(4),(obj.range_width or Fraction(0))/20)
            if not inside:
                if max(obj.band.lower-price,price-obj.band.upper)>=reset:state['consumed']=False
                state['outside']=-1 if price<obj.band.lower else 1
            elif not state['consumed']:
                approach=None if state['outside'] is None else -state['outside']
                state['visit']+=1;state['consumed']=True
                contacts.append(Contact(obj.id,obj.version,state['visit'],cut,price,approach,None if approach is None else -approach))
        by={o.id:o for o in candidates}
        return tuple(sorted(contacts,key=lambda c:(abs(price-by[c.object_id].price),by[c.object_id].born_at,c.object_id)))

    def checkpoint(self):return {'maximum_gap_ns':self.maximum_gap_ns,'last_cut':self.last_cut,'states':{k:dict(v) for k,v in self.states.items()}}
    @classmethod
    def restore(cls,checkpoint):
        result=cls(maximum_gap_ns=checkpoint['maximum_gap_ns']);result.last_cut=checkpoint['last_cut'];result.states={k:dict(v) for k,v in checkpoint['states'].items()};return result


def stop_distance(width:Fraction|None):
    if width is None or width<=0:raise DependencyUnavailable("E0 bracket requires an available positive 06-09 range width")
    return math.ceil(max(Fraction(8),width/10))


def numeric_features(*,obj:E0Object,side:int,cut:int,price:Fraction,range_06_09:FrozenRange,prior_rth:FrozenRange,
                     five_minute_return:Fraction,thirty_minute_realized_variation:Fraction,history_known_at:int,
                     minute_of_session:int,remaining_minutes:Fraction,object_type_code:int):
    if side not in (-1,1) or max(range_06_09.known_at,prior_rth.known_at,history_known_at,obj.available_at)>cut or not range_06_09.complete or not prior_rth.complete or range_06_09.width<=0 or prior_rth.width<=0:raise DependencyUnavailable("complete causally available E0 feature windows required")
    if len({obj.instrument,range_06_09.instrument,prior_rth.instrument})!=1 or thirty_minute_realized_variation<0:raise ContractError("E0 features mix raw contracts or invalid variation")
    return {'side':float(side),'object_type':float(object_type_code),'distance_over_width':float(abs(price-obj.price)/range_06_09.width),
            'range_position':float((price-range_06_09.low)/range_06_09.width),'prior_rth_distance':float((price-prior_rth.close)/prior_rth.width),
            'five_minute_return_ticks':float(five_minute_return),'thirty_minute_realized_variation_ticks2':float(thirty_minute_realized_variation),
            'minute_sine':math.sin(2*math.pi*minute_of_session/390),'minute_cosine':math.cos(2*math.pi*minute_of_session/390),
            'remaining_minutes':float(remaining_minutes)}
