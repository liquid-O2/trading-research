"""Immutable object lifecycles, known-time active sets and complete candidate cuts."""

from dataclasses import asdict, dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.contracts import Band, Geometry, InstrumentKey, MarketObject
from trading_research.foundations.time import AvailabilityBasis, Clocks, timestamp
from trading_research.foundations.units import Unit
from trading_research.operations.artifacts import digest
from trading_research.operations.journal import Journal


STATES=frozenset({'born','provisional','active','contacted','swept','reclaimed','invalidated','expired','superseded'})


@dataclass(frozen=True)
class Lifecycle:
    generator:str
    parameter_version:str
    transitions:tuple[tuple[str,str],...]
    initial_states:frozenset[str]
    tradable_states:frozenset[str]
    geometry_may_change:bool
    anchor_may_extend:bool

    def __post_init__(self):
        if (not isinstance(self.transitions,tuple) or any(not isinstance(t,tuple) or len(t)!=2 for t in self.transitions)
                or not isinstance(self.initial_states,frozenset) or not isinstance(self.tradable_states,frozenset)
                or type(self.geometry_may_change) is not bool or type(self.anchor_may_extend) is not bool):
            raise ContractError("lifecycle transitions, states and flags must be immutable typed declarations")
        if not self.generator or not self.parameter_version or not self.initial_states or not self.tradable_states:
            raise ContractError("generator-specific lifecycle and initial/tradable states required")
        if not self.initial_states<=STATES or not self.tradable_states<=STATES or any(a not in STATES or b not in STATES for a,b in self.transitions):
            raise ContractError("unregistered lifecycle state")
        if any(a in {'expired','superseded'} for a,b in self.transitions):
            raise ContractError("expired/superseded identities require a linked new object; invalidation reactivation needs an explicit generator transition")

    @property
    def version(self):return digest(self)


def object_record(obj:MarketObject):
    p=asdict(obj)
    p['instrument']['strike']=None if obj.instrument.strike is None else str(obj.instrument.strike)
    for name in ('physical_support','contact_region'):
        band=getattr(obj.geometry,name);p['geometry'][name]={'lower':str(band.lower),'upper':str(band.upper),'unit':band.unit.value}
    for name in ('estimation_uncertainty','mapping_uncertainty','entry_tolerance'):
        p['geometry'][name]=str(getattr(obj.geometry,name))
    return p


def object_restore(p):
    geom={**p['geometry']}
    for name in ('physical_support','contact_region'):
        b=geom[name];geom[name]=Band(Fraction(b['lower']),Fraction(b['upper']),Unit(b['unit']))
    for name in ('estimation_uncertainty','mapping_uncertainty','entry_tolerance'):geom[name]=Fraction(geom[name])
    inst={**p['instrument'],'strike':None if p['instrument']['strike'] is None else Decimal(p['instrument']['strike'])}
    return MarketObject(**{**p,'geometry':Geometry(**geom),'instrument':InstrumentKey(**inst),
                           'clocks':Clocks(**{**p['clocks'],'basis':AvailabilityBasis(p['clocks']['basis'])}),
                           **{name:tuple(p[name]) for name in ('parent_ids','source_event_ids','role_candidates')}})


class ObjectRegistry:
    def __init__(self,path:Path,*,lifecycles:tuple[Lifecycle,...]):
        self.journal=Journal(path);self.lifecycles=MappingProxyType({(l.generator,l.parameter_version):l for l in lifecycles})
        if len(self.lifecycles)!=len(lifecycles):raise ContractError("duplicate generator lifecycle")
        self.journal.append(key='object-registry-contract',kind='object_contract',payload={'lifecycles':tuple(sorted((k,l.version) for k,l in self.lifecycles.items()))})

    def anchor(self,*,id:str,known_at:int,evidence_version:str):
        timestamp(known_at)
        if not id or not evidence_version:raise ContractError("external bar/swing anchor requires an evidence version")
        self.journal.append(key='anchor:'+id,kind='anchor',payload={'id':id,'known_at':known_at,'evidence_version':evidence_version})

    def _state(self):
        events=self.journal.read();versions={};anchors={};latest={}
        for e in events:
            if e['kind']=='anchor':anchors[e['payload']['id']]=e['payload']['known_at']
            elif e['kind']=='object_version':
                p=e['payload'];obj=object_restore(p['object'])
                if obj.version_id!=p['version_id']:raise IntegrityError("object serialization/version changed")
                versions[obj.version_id]=(obj,p['state']);latest[obj.id]=(obj,p['state'])
        return events,versions,anchors,latest

    def append(self,obj:MarketObject,*,state:str,event_id:str,reason:str):
        if state not in STATES or not event_id or not reason:raise ContractError("object transition needs identity, state and reason")
        contract=self.lifecycles.get((obj.generator,obj.parameter_version))
        if contract is None:raise ContractError("unregistered generator lifecycle")
        events,versions,anchors,latest=self._state();old=latest.get(obj.id)
        payload={'event_id':event_id,'object':object_record(obj),'version_id':obj.version_id,'state':state,'reason':reason,'lifecycle':contract.version}
        duplicate=next((e for e in events if e['key']=='transition:'+event_id),None)
        if duplicate:
            if digest(duplicate['payload'])!=digest(payload):raise IntegrityError("object event ID reused with changed history")
            return obj.version_id
        if obj.clocks.known_at<max((v[0].clocks.known_at for v in latest.values()),default=obj.clocks.known_at):
            raise ContractError("new object admission cannot regress the registry publication clock")
        if any(e['kind']=='candidate_cut' and obj.clocks.known_at<=e['payload']['at'] for e in events):
            raise ContractError("new object admission would change an already frozen candidate prefix")
        if old:
            prior,old_state=old
            if obj.revision!=prior.revision+1 or obj.supersedes!=prior.version_id or obj.clocks.known_at<prior.clocks.known_at:
                raise ContractError("object revision must extend its exact previous version at a current known time")
            if (old_state,state) not in contract.transitions:raise ContractError("transition absent from this generator's frozen lifecycle")
            if (obj.generator,obj.parameter_version,obj.instrument,obj.anchor_start)!=(prior.generator,prior.parameter_version,prior.instrument,prior.anchor_start):
                raise ContractError("identity/contract/birth anchor changed; create a new linked object")
            if (not contract.geometry_may_change and obj.geometry!=prior.geometry) or (not contract.anchor_may_extend and obj.anchor_end!=prior.anchor_end) or obj.anchor_end<prior.anchor_end:
                raise ContractError("forbidden geometry change or backward/undeclared anchor revision")
        elif obj.revision!=0 or obj.supersedes is not None or state not in contract.initial_states:
            raise ContractError("new identity requires initial version and declared birth state")
        if not obj.source_event_ids and not obj.parent_ids:raise ContractError("object formation has no source evidence")
        for parent in obj.parent_ids:
            known=versions[parent][0].clocks.known_at if parent in versions else anchors.get(parent)
            if known is None or known>obj.clocks.known_at:raise ContractError("orphan or future parent anchor")
        if state in contract.tradable_states and obj.eligibility!='eligible':raise ContractError("unknown/ineligible formation cannot activate an object")
        self.journal.append(key='transition:'+event_id,kind='object_version',payload=payload,
                            expected_head=events[-1]['hash'] if events else None,check_head=True)
        return obj.version_id

    def asof(self,cut:int,*,active_only:bool=False):
        timestamp(cut);_,versions,_,_=self._state()
        return self._asof(versions,cut,active_only=active_only)

    def _asof(self,versions,cut,*,active_only):
        latest={}
        for obj,state in versions.values():
            if obj.clocks.known_at<=cut:latest[obj.id]=(obj,state)
        if not active_only:return tuple(latest[id] for id in sorted(latest))
        return tuple((obj,state) for id,(obj,state) in sorted(latest.items()) if state in self.lifecycles[(obj.generator,obj.parameter_version)].tradable_states and obj.eligibility=='eligible' and obj.clocks.available(cut))

    def freeze_candidates(self,*,id:str,at:int,instrument:InstrumentKey):
        timestamp(at)
        if not id or not isinstance(instrument,InstrumentKey):
            raise ContractError("candidate cut requires its exact provider/venue/instrument definition key")
        events,versions,_,_=self._state()
        candidates=tuple(obj.version_id for obj,state in self._asof(versions,at,active_only=True) if obj.instrument==instrument)
        payload={'id':id,'at':at,'instrument':asdict(instrument),'candidate_versions':candidates,'candidate_count':len(candidates)}
        self.journal.append(key='candidate-cut:'+id,kind='candidate_cut',payload=payload,
                            expected_head=events[-1]['hash'] if events else None,check_head=True)
        return payload

    def relationship(self,*,id:str,at:int,left_version:str,right_version:str,kind:str):
        _,versions,_,_=self._state()
        if not id or left_version==right_version or kind not in {'geometric_overlap','same_source_evidence','mapped_from','merge_parent','split_parent'}:
            raise ContractError("explicit distinct object relationship required")
        if any(v not in versions or versions[v][0].clocks.known_at>at for v in (left_version,right_version)):
            raise ContractError("object relationship references future or missing version")
        self.journal.append(key='relationship:'+id,kind='object_relationship',payload={'at':at,'left':left_version,'right':right_version,'kind':kind,'independent_confirmation':False})
