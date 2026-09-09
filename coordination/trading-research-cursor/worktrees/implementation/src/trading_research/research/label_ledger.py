"""Finite immutable candidate/outcome ledger with explicit observation limits.

No OI report or policy outcome is inferred from a missing receipt. The ledger
retains the population and typed evidence; it does not implement a venue or a
source-specific price/profile/policy model.
"""
from dataclasses import dataclass, fields
from enum import StrEnum
from fractions import Fraction
from collections import Counter

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import ArtifactRef, canonical_json, digest
from trading_research.research.temporal_folds import (V01V02LimitsV1, DEFAULT_LIMITS,
    bounded, bounded_json, identity, names)
from trading_research.research.finite_encoding import encode_wire


class SamplingFrame(StrEnum):
    CLOCK = 'clock'
    SOURCE_EPISODE = 'source_episode'
    OBJECT_BIRTH = 'object_birth'
    CONTACT = 'contact'
    POLICY_TRAJECTORY = 'policy_trajectory'


_LABEL_KINDS = ('price_path', 'object_path', 'oi_report', 'policy_value', 'profile_mass', 'option_board')
_STATES = ('complete', 'pending', 'censored', 'ambiguous', 'invalid', 'not_applicable')


@dataclass(frozen=True)
class LabelDefinition:
    id: str
    kind: str
    cut: int
    end: int
    observation_process: str
    object_version: str = ''
    geometry_version: str = ''
    side: int = 1
    favorable_distance: Fraction = Fraction(3)
    adverse_distance: Fraction = Fraction(2)
    endpoint_group: str = 'E10'
    policy_version: str = ''
    simulator_version: str = ''
    transformation: str = 'identity'

    def __post_init__(self):
        identity(self.id,None); identity(self.observation_process,None); identity(self.endpoint_group,None)
        identity(self.transformation,None)
        timestamp(self.cut); timestamp(self.end)
        if type(self.kind) is not str or self.kind not in _LABEL_KINDS or self.end <= self.cut:
            raise ContractError('typed fixed-end label definition required')
        if type(self.side) is not int or self.side not in (-1, 1):
            raise ContractError('exact side required')
        if any(type(v) is not Fraction or v <= 0 for v in (self.favorable_distance, self.adverse_distance)):
            raise ContractError('positive exact barriers required')
        if any(type(v) is not str for v in (self.object_version,self.geometry_version,self.policy_version,self.simulator_version)):
            raise ContractError('exact optional definition identity strings required')
        if self.kind == 'object_path' and (not self.object_version or not self.geometry_version):
            raise ContractError('frozen object and geometry required')
        if self.kind == 'policy_value' and (not self.policy_version or not self.simulator_version):
            raise ContractError('policy and simulator identities required')

    @property
    def version(self):
        return digest(self)


@dataclass(frozen=True)
class CandidateRecord:
    id: str
    generator_event: str
    decision_set: str
    object_version: str
    date_group: str
    source_episode: str
    sampling_frame: SamplingFrame
    created_at: int
    known_at: int
    decision: str
    inclusion_probability: Fraction | None = None
    endpoint_group: str = 'E10'
    definition_id: str = 'price-v1'

    def __post_init__(self):
        for value in (self.id, self.generator_event, self.decision_set, self.object_version,
                      self.date_group, self.source_episode, self.endpoint_group, self.definition_id):
            identity(value,None)
        timestamp(self.created_at); timestamp(self.known_at)
        if self.created_at > self.known_at or type(self.sampling_frame) is not SamplingFrame:
            raise ContractError('candidate creation/frame evidence differs')
        if type(self.decision) is not str or self.decision not in ('selected', 'rejected', 'untraded', 'invalid'):
            raise ContractError('explicit candidate disposition required')
        p = self.inclusion_probability
        if p is not None and (type(p) is not Fraction or not 0 < p <= 1):
            raise ContractError('exact declared inclusion probability required')


@dataclass(frozen=True)
class ObservationEvidence:
    observed_end: int
    certified_at: int
    input_version: str
    gaps: tuple[tuple[int, int], ...] = ()
    source_order_known: bool = True
    partial_facts: tuple[tuple[str, int, Fraction], ...] = ()

    def __post_init__(self):
        timestamp(self.observed_end); timestamp(self.certified_at); identity(self.input_version,None)
        if self.certified_at < self.observed_end or type(self.source_order_known) is not bool:
            raise ContractError('invalid observation certification/order capability')
        if type(self.gaps) is not tuple or type(self.partial_facts) is not tuple:
            raise ContractError('immutable observation evidence required')
        previous = None
        for gap in self.gaps:
            if type(gap) is not tuple or len(gap) != 2:
                raise ContractError('typed gap interval required')
            a,b = gap; timestamp(a); timestamp(b)
            if a >= b or b > self.observed_end or (previous is not None and a < previous):
                raise ContractError('nonoverlapping chronological gaps required')
            previous = b
        for fact in self.partial_facts:
            if type(fact) is not tuple or len(fact) != 3:
                raise ContractError('typed partial fact required')
            kind, at, price = fact
            identity(kind,None); timestamp(at)
            if at > self.observed_end or type(price) is not Fraction or any(a <= at < b for a,b in self.gaps):
                raise ContractError('partial fact lacks observed point support')


@dataclass(frozen=True)
class LabelOutcome:
    id: str
    candidate_id: str
    definition_id: str
    state: str
    payload_kind: str
    payload: bytes
    observation: ObservationEvidence
    endpoint_group: str
    supersedes: str | None = None

    def __post_init__(self):
        for value in (self.id,self.candidate_id,self.definition_id,self.endpoint_group): identity(value,None)
        if type(self.state) is not str or type(self.payload_kind) is not str or self.state not in _STATES or self.payload_kind not in _LABEL_KINDS:
            raise ContractError('typed outcome state/kind required')
        if type(self.observation) is not ObservationEvidence:
            raise ContractError('actual observation evidence required')
        if type(self.payload) is not bytes:
            raise ContractError('immutable canonical outcome payload bytes required')
        if self.supersedes is not None: identity(self.supersedes,None)
        if self.supersedes == self.id:
            raise ContractError('outcome cannot revise itself')


_RECORDS = {c.__name__:c for c in (LabelDefinition,CandidateRecord,ObservationEvidence,LabelOutcome,V01V02LimitsV1)}


def _wire(value):
    if type(value) in _RECORDS.values():
        return {'type':type(value).__name__, 'fields':{f.name:_wire(getattr(value,f.name)) for f in fields(value)}}
    if type(value) is SamplingFrame: return {'frame':value.value}
    if type(value) is Fraction: return {'fraction':[value.numerator,value.denominator]}
    if type(value) is bytes: return {'bytes':value.hex()}
    if type(value) is tuple: return {'tuple':[_wire(v) for v in value]}
    if value is None or type(value) in (str,int,bool): return value
    raise ContractError('unknown ledger serialization type')


def _unwire(value):
    if type(value) is dict:
        if set(value)=={'type','fields'} and value['type'] in _RECORDS:
            cls=_RECORDS[value['type']]
            if type(value['fields']) is not dict or set(value['fields'])!={f.name for f in fields(cls)}:
                raise ContractError('unknown ledger record fields')
            return cls(**{k:_unwire(v) for k,v in value['fields'].items()})
        if set(value)=={'tuple'} and type(value['tuple']) is list: return tuple(_unwire(v) for v in value['tuple'])
        if set(value)=={'fraction'} and type(value['fraction']) is list and len(value['fraction'])==2:
            if any(type(v) is not int for v in value['fraction']): raise ContractError('exact rational wire required')
            return Fraction(*value['fraction'])
        if set(value)=={'bytes'} and type(value['bytes']) is str: return bytes.fromhex(value['bytes'])
        if set(value)=={'frame'}: return SamplingFrame(value['frame'])
        raise ContractError('unknown ledger envelope')
    if value is None or type(value) in (str,int,bool): return value
    raise ContractError('unknown ledger scalar')


class LabelLedger:
    """Append-only value log. A rejected operation does not change any bytes."""
    def __init__(self, limits=DEFAULT_LIMITS):
        if type(limits) is not V01V02LimitsV1: raise ContractError('typed ledger limits required')
        limits.__post_init__()
        self._limits=limits; self._definitions=(); self._candidates=(); self._outcomes=(); self._evidence={}
        self._sealed=self._checkpoint_values()

    @property
    def limits(self): return self._limits
    @property
    def definitions(self): return self._definitions
    @property
    def candidates(self): return self._candidates
    @property
    def outcomes(self): return self._outcomes

    def _validate_record_size(self, record):
        record.__post_init__()
        for f in fields(record):
            value=getattr(record,f.name)
            if type(value) is str and value: identity(value,self.limits)
        if type(record) is LabelOutcome:
            if len(record.payload)>self.limits.max_payload_bytes:
                raise ContractError('label payload byte capacity exceeded')
            observation=record.observation
            identity(observation.input_version,self.limits)
            if len(observation.gaps)>4096 or len(observation.partial_facts)>4096:
                raise ContractError('label observation collection capacity exceeded')
            for kind,_,_ in observation.partial_facts:
                identity(kind,self.limits)
        encode_wire(record,records=tuple(_RECORDS.values()),frame_type=SamplingFrame,
                    maximum=self.limits.max_checkpoint_bytes,max_depth=self.limits.max_nested_depth)

    def _append(self, attribute, record, cls, capacity, *, evidence=None):
        if type(record) is not cls: raise ContractError('exact ledger record required')
        self._check()
        self._validate_record_size(record)
        rows=getattr(self,attribute)
        previous=next((r for r in rows if r.id==record.id),None)
        if previous is not None:
            if previous!=record: raise ContractError('immutable ID reused for different ledger record: '+record.id)
            return record
        if len(rows)>=capacity: raise ContractError('ledger record capacity exceeded')
        proposed=(*rows,record)
        changes={attribute:proposed}
        if evidence is not None: changes['_evidence']=evidence
        snapshot=self._checkpoint_values(**changes)
        setattr(self,attribute,proposed)
        if evidence is not None: self._evidence=evidence
        self._sealed=snapshot
        return record

    def add_definition(self, definition):
        return self._append('_definitions',definition,LabelDefinition,self.limits.max_ledger_definitions)

    def add_candidate(self, candidate):
        if type(candidate) is not CandidateRecord: raise ContractError('typed candidate required')
        definition=next((d for d in self.definitions if d.id==candidate.definition_id),None)
        if definition is None or candidate.known_at>definition.cut or candidate.endpoint_group!=definition.endpoint_group:
            raise ContractError('candidate definition/cut/endpoint differs')
        if definition.kind=='object_path' and candidate.object_version!=definition.object_version:
            raise ContractError('candidate object version differs from its frozen definition')
        return self._append('_candidates',candidate,CandidateRecord,self.limits.max_ledger_candidates)

    def append_outcome(self, outcome, *, evidence_by_sha=None):
        if type(outcome) is not LabelOutcome: raise ContractError('typed outcome required')
        candidate=next((c for c in self.candidates if c.id==outcome.candidate_id),None)
        definition=next((d for d in self.definitions if d.id==outcome.definition_id),None)
        if (candidate is None or definition is None or candidate.definition_id!=outcome.definition_id
                or definition.kind!=outcome.payload_kind or definition.endpoint_group!=outcome.endpoint_group):
            raise ContractError('outcome lacks exact candidate/definition/endpoint ownership')
        observation=outcome.observation
        self._validate_record_size(outcome)
        if (not definition.cut<=observation.observed_end<=definition.end or any(a<definition.cut for a,b in observation.gaps)
                or any(at<definition.cut for _,at,_ in observation.partial_facts)):
            raise ContractError('observation outside fixed target')
        if outcome.state in ('complete','ambiguous') and (observation.observed_end!=definition.end or observation.gaps):
            raise ContractError('complete outcome requires certified full observation')
        previous=tuple(o for o in self.outcomes if o.candidate_id==outcome.candidate_id and o.definition_id==outcome.definition_id)
        same_id=next((o for o in previous if o.id==outcome.id),None)
        if same_id is None:
            if previous:
                if outcome.supersedes is None:
                    raise ContractError('duplicate outcome: '+outcome.candidate_id)
                if outcome.supersedes!=previous[-1].id or observation.certified_at<previous[-1].observation.certified_at:
                    raise ContractError('revision must append to the exact latest outcome')
            elif outcome.supersedes is not None:
                raise ContractError('revision predecessor absent')
        from trading_research.research.label_payloads import validate_payload
        incoming={} if evidence_by_sha is None else evidence_by_sha
        if type(incoming) is not dict or len(incoming)>self.limits.max_dependencies_per_sample:
            raise ContractError('bounded label evidence table required')
        for key,raw in incoming.items():
            if type(key) is not str or type(raw) is not bytes or len(raw)>self.limits.max_payload_bytes:
                raise ContractError('bounded exact label evidence bytes required')
            if key in self._evidence and self._evidence[key]!=raw:
                raise IntegrityError('retained label evidence identity changed')
        evidence={**self._evidence,**incoming}
        used=validate_payload(outcome,candidate,definition,evidence,self.limits)
        if not set(incoming)<=used:
            raise ContractError('unreferenced label evidence supplied')
        return self._append('_outcomes',outcome,LabelOutcome,self.limits.max_ledger_outcomes,evidence=evidence)

    def reconcile(self, generated_ids, required_ids=None):
        generated=bounded(generated_ids,self.limits.max_ledger_candidates,'generator population')
        names(generated,self.limits.max_ledger_candidates,self.limits)
        if set(generated)!={c.id for c in self.candidates}:
            raise ContractError('generator/candidate decision population differs')
        required=generated if required_ids is None else bounded(required_ids,self.limits.max_ledger_candidates,'required outcomes')
        names(required,self.limits.max_ledger_candidates,self.limits)
        if not set(required)<=set(generated): raise ContractError('unknown required outcome owner')
        covered={o.candidate_id for o in self.outcomes}
        if not set(required)<=covered:
            raise ContractError('missing outcomes: '+','.join(sorted(set(required)-covered)))
        latest={}
        for o in self.outcomes: latest[o.candidate_id]=o
        return tuple((i,latest[i].state) for i in sorted(required))

    def _checkpoint_values(self, **overrides):
        return encode_wire({'format':'LabelLedgerV1','limits':self.limits,
            'definitions':overrides.get('_definitions',self.definitions),
            'candidates':overrides.get('_candidates',self.candidates),
            'outcomes':overrides.get('_outcomes',self.outcomes),'evidence':overrides.get('_evidence',self._evidence)},
            records=tuple(_RECORDS.values()),frame_type=SamplingFrame,
            maximum=self.limits.max_checkpoint_bytes,max_depth=self.limits.max_nested_depth)

    def _check(self):
        if self._checkpoint_values()!=self._sealed:
            raise IntegrityError('ledger state changed outside its retained append log')

    def checkpoint(self):
        self._check()
        return self._sealed

    @classmethod
    def restore(cls, raw, *, limits=DEFAULT_LIMITS):
        value=bounded_json(raw,limits.max_checkpoint_bytes,limits)
        if type(value) is not dict or set(value)!={'format','limits','definitions','candidates','outcomes','evidence'} or value['format']!='LabelLedgerV1':
            raise ContractError('unknown ledger checkpoint format')
        try:
            retained=_unwire(value['limits'])
            if retained!=limits: raise ContractError('ledger restore limits differ')
            arrays={}
            for key,maximum in (('definitions',limits.max_ledger_definitions),('candidates',limits.max_ledger_candidates),('outcomes',limits.max_ledger_outcomes)):
                array=value[key]
                if type(array) is not dict or set(array)!={'tuple'} or type(array['tuple']) is not list or len(array['tuple'])>maximum:
                    raise ContractError('ledger restore record capacity exceeded')
                arrays[key]=array['tuple']
            if type(value['evidence']) is not dict or len(value['evidence'])>limits.max_ledger_outcomes*limits.max_dependencies_per_sample:
                raise ContractError('ledger restore evidence count exceeded')
            evidence={}
            for key,entry in value['evidence'].items():
                if (type(entry) is not dict or set(entry)!={'bytes'} or type(entry['bytes']) is not str
                        or len(entry['bytes'])>2*limits.max_payload_bytes):
                    raise ContractError('ledger restore evidence byte capacity exceeded')
                evidence[key]=_unwire(entry)
            for record in arrays['outcomes']:
                if type(record) is not dict or record.get('type')!='LabelOutcome' or type(record.get('fields')) is not dict:
                    raise ContractError('typed outcome wire required')
                payload=record['fields']['payload']
                if type(payload) is not dict or set(payload)!={'bytes'} or type(payload['bytes']) is not str or len(payload['bytes'])>2*limits.max_payload_bytes:
                    raise ContractError('restored label payload byte capacity exceeded')
                observation=record['fields']['observation']['fields']
                for key in ('gaps','partial_facts'):
                    array=observation[key]
                    if type(array) is not dict or set(array)!={'tuple'} or type(array['tuple']) is not list or len(array['tuple'])>4096:
                        raise ContractError('restored observation capacity exceeded')
            ledger=cls(limits)
            for record in arrays['definitions']: ledger.add_definition(_unwire(record))
            for record in arrays['candidates']: ledger.add_candidate(_unwire(record))
            for record in arrays['outcomes']:
                outcome=_unwire(record)
                payload=bounded_json(outcome.payload,limits.max_payload_bytes,limits)
                refs=payload['evidence']
                if type(refs) is not list or len(refs)>limits.max_dependencies_per_sample:
                    raise ContractError('restored evidence slot capacity exceeded')
                keys={item['ref']['sha256'] for item in refs}
                ledger.append_outcome(outcome,evidence_by_sha={key:evidence[key] for key in keys})
            if ledger._evidence!=evidence:
                raise ContractError('unused evidence in ledger checkpoint')
            if ledger.checkpoint()!=raw: raise ContractError('noncanonical ledger checkpoint')
            return ledger
        except (ValueError,TypeError,KeyError,ZeroDivisionError) as exc:
            raise ContractError('malformed ledger checkpoint') from exc

    def publish(self, store):
        return store.put_bytes(self.checkpoint(),kind='LabelLedgerV1')

    @classmethod
    def read(cls, store, ref, *, limits=DEFAULT_LIMITS):
        if type(ref) is not ArtifactRef or ref.kind!='LabelLedgerV1' or ref.size_bytes>limits.max_checkpoint_bytes:
            raise ContractError('bounded exact ledger checkpoint reference required')
        return cls.restore(store.read(ref),limits=limits)


def sampling_weight(candidate):
    if type(candidate) is not CandidateRecord: raise ContractError('typed candidate required')
    return None if candidate.inclusion_probability is None else 1/candidate.inclusion_probability


def grouped_weights(candidates, by='date_group', *, limits=DEFAULT_LIMITS):
    rows=bounded(candidates,limits.max_ledger_candidates,'grouped population')
    if by not in ('date_group','source_episode','endpoint_group') or any(type(c) is not CandidateRecord for c in rows):
        raise ContractError('declared dependence grouping required')
    names(tuple(c.id for c in rows),limits.max_ledger_candidates,limits)
    counts=Counter(getattr(c,by) for c in rows)
    return tuple((c.id,Fraction(1,counts[getattr(c,by)])) for c in rows)


def support_counts(candidates, *, limits=DEFAULT_LIMITS):
    rows=bounded(candidates,limits.max_ledger_candidates,'support population')
    if any(type(c) is not CandidateRecord for c in rows): raise ContractError('typed support population required')
    return {'rows':len(rows),'dates':len({c.date_group for c in rows}),
            'episodes':len({c.source_episode for c in rows}),
            'endpoints':len({c.endpoint_group for c in rows})}


def contact_partial_fact(target, points, coverage):
    """Retain only a directly observed in-band price, including an outage later."""
    points=bounded(points,4096,'partial contact observations')
    eligible=[p for p in points if target.cut<p.at<=coverage.end and target.band.contains(p.price)
              and not any(a<=p.at<b for a,b in coverage.gaps)]
    if not eligible: return ()
    at=min(p.at for p in eligible)
    prices={p.price for p in eligible if p.at==at}
    if not coverage.source_order_known and len(prices)>1: return ()
    point=min((p for p in eligible if p.at==at),key=lambda p:p.sequence)
    return (('observed_contact',point.at,point.price),)


def contact_origin(original_cut, original_end, contact_at, *, new_end=None):
    for value in (original_cut,original_end,contact_at): timestamp(value)
    if not original_cut<=contact_at<=original_end: raise ContractError('contact outside original target')
    if new_end is None:
        return {'original_cut':original_cut,'contact_cut':contact_at,'target_end':original_end,'new_target_required':False}
    timestamp(new_end)
    if new_end<=contact_at: raise ContractError('empty retargeted contact horizon')
    return {'original_cut':original_cut,'contact_cut':contact_at,'target_end':new_end,'new_target_required':True}


def admit_original_feature(original_cut, known_at):
    timestamp(original_cut); timestamp(known_at)
    if known_at>original_cut: raise ContractError('arrival feature after original cut')
    return True


@dataclass(frozen=True)
class OIReport:
    id: str
    contract: str
    position_date: str
    known_at: int
    count: int
    supersedes: str | None = None

    def __post_init__(self):
        for v in (self.id,self.contract,self.position_date): identity(v,None)
        timestamp(self.known_at)
        if type(self.count) is not int or self.count<0: raise ContractError('exact nonnegative OI count required')
        if self.supersedes is not None: identity(self.supersedes,None)


def oi_endpoint(prior, reports, *, contract, query_at, report_due, observation_boundary,
                boundary_known_at, expiry=None, receipt_coverage=True, limits=DEFAULT_LIMITS):
    """As-of receipt query, never inferred holdings or disappearance-as-zero."""
    if type(prior) is not OIReport or prior.contract!=contract: raise ContractError('continuing contract prior required')
    if type(receipt_coverage) is not bool: raise ContractError('explicit receipt coverage required')
    for t in (query_at,report_due,observation_boundary,boundary_known_at): timestamp(t)
    if observation_boundary<report_due or boundary_known_at<observation_boundary: raise ContractError('invalid missing-publication observation boundary')
    if expiry is not None:
        timestamp(expiry)
        if query_at>=expiry: return {'state':'expiry_terminal','delta':None,'report_id':None}
    rows=bounded(reports,limits.max_ledger_outcomes,'OI receipts')
    if any(type(r) is not OIReport or r.contract!=contract for r in rows): raise ContractError('OI contract identity mismatch')
    names(tuple(r.id for r in rows),limits.max_ledger_outcomes,limits)
    ordered=tuple(sorted(rows,key=lambda r:(r.known_at,r.id)))
    previous=None
    for r in ordered:
        date_key=_position_date(r.position_date); prior_key=_position_date(prior.position_date)
        if (date_key[0]!=prior_key[0] or date_key[1]<=prior_key[1] or r.known_at<report_due
                or previous is None and r.supersedes is not None
                or previous is not None and (r.supersedes!=previous.id or r.position_date!=previous.position_date
                                             or r.known_at<=previous.known_at)):
            raise ContractError('OI revision changes its next-report endpoint or predecessor')
        previous=r
    visible=[r for r in ordered if r.known_at<=query_at]
    if prior.known_at>query_at: return {'state':'pending','delta':None,'report_id':None}
    if visible:
        r=visible[-1]
        return {'state':'complete','delta':r.count-prior.count,'report_id':r.id,'known_at':r.known_at}
    return {'state':'censored_missing_publication' if receipt_coverage and query_at>=boundary_known_at else 'pending',
            'delta':None,'report_id':None}


def _position_date(value):
    from datetime import date
    import re
    if re.fullmatch(r'D(?:0|[1-9][0-9]*)',value):
        return ('synthetic_day',int(value[1:]))
    try:
        parsed=date.fromisoformat(value)
        if parsed.isoformat()!=value:
            raise ValueError('not canonical')
        return ('civil_date',parsed.toordinal())
    except (ValueError,TypeError) as exc:
        raise ContractError('explicit ISO position date or synthetic D ordinal required') from exc


def policy_outcome(*, candidate_id, policy_version, simulator_version, fill_version,
                   fee_version, account_version, target_end, observed_end, certified_at,
                   filled, value=None, provenance_ref):
    for v in (candidate_id,policy_version,simulator_version,fill_version,fee_version,account_version): identity(v)
    for t in (target_end,observed_end,certified_at): timestamp(t)
    if type(filled) is not bool or type(provenance_ref) is not ArtifactRef:
        raise ContractError('actual policy/fill provenance required')
    if value is not None and type(value) is not Fraction: raise ContractError('exact externally produced value required')
    if observed_end>target_end or certified_at<observed_end: raise ContractError('policy observation clocks differ')
    return {'identity':digest((candidate_id,policy_version,simulator_version,fill_version,fee_version,account_version,target_end,provenance_ref)),
            'state':'complete' if observed_end==target_end else 'censored','filled':filled,
            'value':value if observed_end==target_end else None,'no_fill':not filled,
            'provenance_ref':provenance_ref}


def episode_assignments(prices, lower, upper, reset_distance):
    if any(type(v) is not Fraction for v in (lower,upper,reset_distance)) or lower>upper or reset_distance<=0:
        raise ContractError('exact episode reset geometry required')
    rows=bounded(prices,DEFAULT_LIMITS.max_ledger_candidates,'episode observations')
    if any(type(p) is not Fraction for p in rows): raise ContractError('exact observed prices required')
    episode=0; armed=True; result=[]
    for price in rows:
        if price<=lower-reset_distance or price>=upper+reset_distance: armed=True
        if lower<=price<=upper and armed:
            episode+=1; armed=False
        result.append(episode if lower<=price<=upper else None)
    return tuple(result)


def censored_event_bounds(favorable, adverse, censored):
    if any(type(v) is not int or v<0 for v in (favorable,adverse,censored)) or favorable+adverse+censored==0:
        raise ContractError('finite observed support counts required')
    total=favorable+adverse+censored
    return Fraction(favorable,total),Fraction(favorable+censored,total)


def future_profile_mass(initial, additions, *, observed):
    if (type(observed) is not bool or type(initial) is not tuple or type(additions) is not tuple
            or len(initial)!=len(additions) or len(initial)>4096):
        raise ContractError('fixed grid and observation capability required')
    if any(type(x) is not int or x<0 for x in (*initial,*additions)): raise ContractError('exact nonnegative mass required')
    return {'state':'complete' if observed else 'censored','future_mass':additions if observed else None,
            'resulting_mass':tuple(a+b for a,b in zip(initial,additions)) if observed else None}


def append_price_outcome(*args,**kwargs):
    from trading_research.research.label_payloads import append_price_outcome as adapter
    return adapter(*args,**kwargs)


def append_object_outcome(*args,**kwargs):
    from trading_research.research.label_payloads import append_object_outcome as adapter
    return adapter(*args,**kwargs)


def append_oi_outcome(*args,**kwargs):
    from trading_research.research.label_payloads import append_oi_outcome as adapter
    return adapter(*args,**kwargs)


def append_policy_outcome(*args,**kwargs):
    from trading_research.research.label_payloads import append_policy_outcome as adapter
    return adapter(*args,**kwargs)


def append_profile_outcome(*args,**kwargs):
    from trading_research.research.label_payloads import append_profile_outcome as adapter
    return adapter(*args,**kwargs)
