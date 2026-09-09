"""Typed finite label adapters, replayed from retained canonical source bytes."""
from dataclasses import fields
from fractions import Fraction
import hashlib
import re

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.contracts import Target, Capability, Band
from trading_research.foundations.units import Ticks, Unit
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import ArtifactRef, digest
from trading_research.research.finite_encoding import encode_wire
from trading_research.research.temporal_folds import bounded, bounded_json, identity, names
from trading_research.research.labels import PathPoint, ObservationWindow, reference_path_label
from trading_research.research.object_labels import ObjectTarget, ExactPoint, reference_object_label, compatible_gap_evidence
from trading_research.research.label_ledger import ObservationEvidence, LabelOutcome, OIReport, oi_endpoint, contact_partial_fact


_ENVELOPE={'schema','kind','candidate_version','definition_version','observation_version','evidence','data'}
_MAX_POINTS=4096


def _object(value, keys):
    if type(value) is not dict or set(value)!=set(keys):
        raise ContractError('exact typed label source fields required')
    return value


def _fraction(value):
    if (type(value) is not list or len(value)!=2 or any(type(n) is not int for n in value)
            or value[1]<=0):
        raise ContractError('exact reduced rational label value required')
    result=Fraction(*value)
    if [result.numerator,result.denominator]!=value:
        raise ContractError('label rational must be reduced')
    return result


def _pair(value):
    return None if value is None else [value.numerator,value.denominator]


def _raw(value, limits):
    return encode_wire(value,records=(),maximum=limits.max_payload_bytes,max_depth=limits.max_nested_depth)


def _reference(raw, kind):
    return {'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),'kind':kind}


def _rows(value, maximum, name):
    if type(value) is not list or len(value)>maximum:
        raise ContractError(name+' source cardinality exceeded')
    return value


def _coverage_record(coverage, cut):
    if type(coverage) is ObservationWindow:
        coverage.__post_init__()
        return {'start':coverage.start,'end':coverage.end,'certified_through':coverage.certified_through,
            'gaps':[list(g) for g in coverage.gaps],'source_order_known':coverage.source_order_known,'version':coverage.version}
    if type(coverage) is ObservationEvidence:
        coverage.__post_init__()
        if coverage.partial_facts:
            raise ContractError('partial facts are derived from actual retained points')
        return {'start':cut,'end':coverage.observed_end,'certified_through':coverage.certified_at,
            'gaps':[list(g) for g in coverage.gaps],'source_order_known':coverage.source_order_known,'version':coverage.input_version}
    raise ContractError('typed actual observation coverage required')


def _coverage(value, definition, limits):
    _object(value,('start','end','certified_through','gaps','source_order_known','version'))
    for key in ('start','end','certified_through'):
        timestamp(value[key])
    identity(value['version'],limits)
    _rows(value['gaps'],_MAX_POINTS,'coverage gaps')
    if (value['start']!=definition.cut or not definition.cut<=value['end']<=definition.end
            or value['certified_through']<value['end'] or type(value['source_order_known']) is not bool):
        raise ContractError('coverage differs from the fixed label target')
    gaps=tuple(tuple(g) for g in value['gaps'])
    evidence=ObservationEvidence(value['end'],value['certified_through'],value['version'],gaps,value['source_order_known'])
    if any(a<definition.cut for a,b in gaps):
        raise ContractError('coverage gap precedes label origin')
    if value['end']==definition.cut:
        if gaps:
            raise ContractError('empty observed prefix cannot contain a coverage gap')
        return None,evidence
    return ObservationWindow(value['start'],value['end'],value['certified_through'],gaps,
                             value['source_order_known'],value['version']),evidence


def _path_target_record(target):
    if type(target) is not Target:
        raise ContractError('actual fixed price target required')
    value={f.name:getattr(target,f.name) for f in fields(Target)}
    value['unit']=target.unit.value
    value['capabilities']=sorted(cap.value for cap in target.capabilities)
    return value


def _path_target(value, definition, limits):
    _object(value,(f.name for f in fields(Target)))
    _rows(value['capabilities'],16,'target capabilities')
    for key in ('id','definition_version','asset','observation_process','population'):
        identity(value[key],limits)
    if type(value['unit']) is not str or any(type(v) is not str for v in value['capabilities']):
        raise ContractError('exact target unit and capabilities required')
    try:
        target=Target(**{**value,'unit':Unit(value['unit']),
                        'capabilities':frozenset(Capability(v) for v in value['capabilities'])})
    except (ValueError,TypeError) as exc:
        raise ContractError('invalid retained price target') from exc
    if (target.unit!=Unit.TICKS or target.definition_version!=definition.id
            or target.decision_at!=definition.cut or target.horizon_end!=definition.end
            or target.observation_process!=definition.observation_process):
        raise ContractError('price target differs from its definition')
    return target


def _object_target_record(target):
    if type(target) is not ObjectTarget:
        raise ContractError('actual frozen object target required')
    return {'id':target.id,'object_version':target.object_version,'cut':target.cut,'end':target.end,
        'band':[_pair(target.band.lower),_pair(target.band.upper)],'side':target.side,
        'favorable_distance':_pair(target.favorable_distance),'adverse_distance':_pair(target.adverse_distance),
        'observation_process':target.observation_process,'contact_mode':target.contact_mode}


def geometry_source(target, definition):
    """Explicit geometry receipt format; callers can retain its bytes upstream."""
    return {'geometry_version':definition.geometry_version,'object_version':target.object_version,
        'band':[_pair(target.band.lower),_pair(target.band.upper)],'side':target.side,
        'favorable_distance':_pair(target.favorable_distance),'adverse_distance':_pair(target.adverse_distance),
        'observation_process':target.observation_process,'contact_mode':target.contact_mode}


def _object_target(value, definition, candidate, geometry, limits):
    _object(value,('id','object_version','cut','end','band','side','favorable_distance','adverse_distance','observation_process','contact_mode'))
    if type(value['band']) is not list or len(value['band'])!=2:
        raise ContractError('exact frozen object band required')
    target=ObjectTarget(value['id'],value['object_version'],value['cut'],value['end'],
        Band(*(_fraction(v) for v in value['band'])),value['side'],_fraction(value['favorable_distance']),
        _fraction(value['adverse_distance']),value['observation_process'],value['contact_mode'])
    for key in ('id','object_version','observation_process'):
        identity(value[key],limits)
    if (target.object_version!=candidate.object_version or target.object_version!=definition.object_version
            or target.cut!=definition.cut or target.end!=definition.end or target.side!=definition.side
            or target.favorable_distance!=definition.favorable_distance or target.adverse_distance!=definition.adverse_distance
            or target.observation_process!=definition.observation_process or geometry!=geometry_source(target,definition)):
        raise ContractError('actual object target/geometry differs from its frozen definition')
    return target


def _points(rows, *, exact, coverage, limits):
    _rows(rows,_MAX_POINTS,'label points')
    result=[]
    for row in rows:
        if type(row) is not list or len(row)!=4:
            raise ContractError('exact retained point identity, price and availability required')
        at,sequence,price,known=row
        if exact:
            p=ExactPoint(at,sequence,_fraction(price),known)
        else:
            if type(price) is not int:
                raise ContractError('integral source ticks required')
            p=PathPoint(at,sequence,Ticks(price),known)
        if p.known_at<p.at:
            raise ContractError('observation receipt precedes source event')
        if coverage is None:
            raise ContractError('empty observed prefix contains future points')
        result.append(p)
    return tuple(result)


def _path(kind,source,candidate,definition,slots,limits):
    keys=('schema','target','initial','points','coverage')
    _object(source,(*keys,'up_ticks','down_ticks') if kind=='price_path' else keys)
    if source['schema']!=('PriceLabelSourceV1' if kind=='price_path' else 'ObjectLabelSourceV1'):
        raise ContractError('wrong retained label source schema')
    coverage,observation=_coverage(source['coverage'],definition,limits)
    points=_points(source['points'],exact=kind=='object_path',coverage=coverage,limits=limits)
    known=max(observation.certified_at,*(p.known_at for p in points)) if points else observation.certified_at
    complete=observation.observed_end==definition.end and not observation.gaps
    state='complete' if complete else 'pending' if known<definition.end else 'censored'
    if kind=='price_path':
        target=_path_target(source['target'],definition,limits)
        if (type(source['initial']) is not int or type(source['up_ticks']) is not int or type(source['down_ticks']) is not int
                or Fraction(source['up_ticks'])!=definition.favorable_distance
                or Fraction(source['down_ticks'])!=definition.adverse_distance):
            raise ContractError('price source initial/barriers differ from exact definition')
        result=None if coverage is None else reference_path_label(target,initial=Ticks(source['initial']),points=points,
            coverage=coverage,up_ticks=source['up_ticks'],down_ticks=source['down_ticks'])
        if complete and result.status=='ambiguous':
            state='ambiguous'
        elif complete and result.status=='censored':
            state='censored'
        data={'target_signature':target.signature,'terminal_ticks':None,'maximum_up_ticks':None,
            'maximum_down_ticks':None,'first_barrier':None,'first_barrier_at':None,'observed_count':len(points)}
        if state in ('complete','ambiguous'):
            for key in ('terminal_ticks','maximum_up_ticks','maximum_down_ticks','first_barrier','first_barrier_at'):
                data[key]=getattr(result,key)
        facts=()
    else:
        if set(slots)!={'source','geometry'}:
            raise ContractError('object outcome needs exact target and geometry receipts')
        target=_object_target(source['target'],definition,candidate,slots['geometry'],limits)
        initial=_fraction(source['initial'])
        if target.contact_mode=='contact_at_cut' and not target.band.contains(initial):
            raise ContractError('contact-origin target lacks observed contact at its origin')
        result=None if coverage is None else reference_object_label(target,initial=initial,points=points,coverage=coverage)
        if complete and result['departure']=='ambiguous':
            state='ambiguous'
        data={'target_version':target.version,'object_version':target.object_version,
            'geometry_version':definition.geometry_version,'reach_status':'censored',
            'contact_at':None,'contact_price':None,'departure':None,'first_barrier_at':None,
            'maximum_favorable_ticks':None,'maximum_adverse_ticks':None,
            'gap_evidence':{'compatible_gap_crossing_times':[],'certain_crossing_time_set':[],'possible_crossing_time_set':[]}}
        if state in ('complete','ambiguous'):
            for key in ('reach_status','contact_at','departure','first_barrier_at'):
                data[key]=result[key]
            for key in ('contact_price','maximum_favorable_ticks','maximum_adverse_ticks'):
                data[key]=_pair(result[key])
            if coverage.source_order_known:
                times=list(result['gap_crossings']); unique=sorted(set(times))
                gap={'compatible_gap_crossing_times':[times],'certain_crossing_time_set':unique,'possible_crossing_time_set':unique}
            else:
                evidence=compatible_gap_evidence(target,initial,points,source_order_known=False)
                gap={key:[list(t) for t in value] if key=='compatible_gap_crossing_times' else list(value)
                     for key,value in evidence.items()}
            data['gap_evidence']=gap
        facts=() if coverage is None or complete else contact_partial_fact(target,points,coverage)
    observation=ObservationEvidence(observation.observed_end,known,observation.input_version,
                                    observation.gaps,observation.source_order_known,facts)
    return state,data,observation


def _oi(source,candidate,definition,slots,limits):
    _object(source,('schema','prior','reports','contract','position_date','query_at','report_due',
        'observation_boundary','boundary_known_at','receipt_coverage','expiry'))
    if source['schema']!='OIEndpointSourceV1' or type(source['receipt_coverage']) is not bool:
        raise ContractError('actual continuing-contract receipt observation required')
    _rows(source['reports'],limits.max_ledger_outcomes,'OI reports')
    def report(value):
        _object(value,(f.name for f in fields(OIReport)))
        return OIReport(**value)
    prior=report(source['prior']); reports=tuple(report(v) for v in source['reports'])
    identity(source['position_date'],limits)
    from trading_research.research.label_ledger import _position_date
    prior_date=_position_date(prior.position_date); next_date=_position_date(source['position_date'])
    if (source['report_due']!=definition.end or source['query_at']<definition.cut
            or prior.known_at>definition.cut or next_date[0]!=prior_date[0] or next_date[1]<=prior_date[1]):
        raise ContractError('OI endpoint differs from its fixed target')
    if any(r.position_date!=source['position_date'] for r in reports):
        raise ContractError('OI receipt revision belongs to another endpoint')
    result=oi_endpoint(prior,reports,contract=source['contract'],query_at=source['query_at'],
        report_due=source['report_due'],observation_boundary=source['observation_boundary'],
        boundary_known_at=source['boundary_known_at'],expiry=source['expiry'],
        receipt_coverage=source['receipt_coverage'],limits=limits)
    published=next((r for r in reports if r.id==result['report_id']),None)
    state={'complete':'complete','pending':'pending','censored_missing_publication':'censored',
           'expiry_terminal':'not_applicable'}[result['state']]
    known=published.known_at if published else source['query_at']
    observed_end=definition.end if published else min(definition.end,source['query_at'])
    observation=ObservationEvidence(observed_end,known,'oi:'+digest(source))
    data={'contract':source['contract'],'position_date':source['position_date'],'prior_report_id':prior.id,
        'report_id':None if published is None else published.id,
        'supersedes_report_id':None if published is None else published.supersedes,
        'next_oi':None if published is None else published.count,'delta_oi':result['delta'],
        'endpoint_status':{'complete':'published','pending':'pending','censored':'missing_publication',
            'not_applicable':'expiry_terminal'}[state], 'report_due':source['report_due'],
        'observation_boundary':source['observation_boundary'],'expiry':source['expiry']}
    return state,data,observation


def _policy(source,candidate,definition,slots,limits):
    _object(source,('schema','candidate_id','cut','end','policy_version','simulator_version','fill_version',
        'fee_version','account_version','reward_target_signature','fill_status','filled','net_value_usd','cancel_at','observation'))
    if source['schema']!='ExternalPolicyOutcomeV1' or source['candidate_id']!=candidate.id:
        raise ContractError('exact external policy candidate evidence required')
    if (source['cut']!=definition.cut or source['end']!=definition.end
            or source['policy_version']!=definition.policy_version or source['simulator_version']!=definition.simulator_version):
        raise ContractError('external policy definition differs')
    for key in ('policy_version','simulator_version','fill_version','fee_version','account_version','reward_target_signature'):
        identity(source[key],limits)
    if type(source['filled']) is not bool or source['fill_status'] not in ('filled','nonfill','pending','censored'):
        raise ContractError('explicit external fill disposition required')
    if source['cancel_at'] is not None:
        timestamp(source['cancel_at'])
        if not definition.cut<=source['cancel_at']<=definition.end:
            raise ContractError('cancel lies outside policy target')
    _,observation=_coverage(source['observation'],definition,limits)
    complete=observation.observed_end==definition.end and not observation.gaps
    state='complete' if complete else 'pending' if observation.certified_at<definition.end else 'censored'
    if complete and source['fill_status']!=('filled' if source['filled'] else 'nonfill'):
        raise ContractError('complete external policy disposition differs from observed fill')
    value=None if source['net_value_usd'] is None else _fraction(source['net_value_usd'])
    if complete and value is None:
        raise ContractError('complete reward requires actual external reward evidence')
    data={key:source[key] for key in ('policy_version','simulator_version','fill_version','fee_version',
          'account_version','reward_target_signature','cancel_at')}
    data.update(fill_status=source['fill_status'] if complete else state,filled=source['filled'] if complete else None,
                net_value_usd=_pair(value) if complete else None)
    return state,data,observation


def _profile(source,candidate,definition,slots,limits):
    _object(source,('schema','grid_version','initial','additions','observation'))
    if source['schema']!='ProfileMassSourceV1':
        raise ContractError('exact profile mass source required')
    identity(source['grid_version'],limits)
    for key in ('initial','additions'):
        _rows(source[key],_MAX_POINTS,'profile grid')
        if any(type(n) is not int or n<0 for n in source[key]):
            raise ContractError('exact nonnegative profile counts required')
    if len(source['initial'])!=len(source['additions']):
        raise ContractError('future profile mass changed its fixed grid')
    _,observation=_coverage(source['observation'],definition,limits)
    complete=observation.observed_end==definition.end and not observation.gaps
    state='complete' if complete else 'pending' if observation.certified_at<definition.end else 'censored'
    return state,{'grid_version':source['grid_version'],'future_mass':source['additions'] if complete else None,
        'resulting_mass':[a+b for a,b in zip(source['initial'],source['additions'])] if complete else None,
        'no_new_volume':not any(source['additions']) if complete else None},observation


def _derive(kind,slots,candidate,definition,limits):
    expected_slots={'source','geometry'} if kind=='object_path' else {'source'}
    if set(slots)!=expected_slots:
        raise ContractError('typed label source receipt slots differ')
    source=slots['source']
    if kind in ('price_path','object_path'):
        return _path(kind,source,candidate,definition,slots,limits)
    if kind=='oi_report':
        return _oi(source,candidate,definition,slots,limits)
    if kind=='policy_value':
        return _policy(source,candidate,definition,slots,limits)
    if kind=='profile_mass':
        return _profile(source,candidate,definition,slots,limits)
    _object(source,('schema','state','reason','unavailable_fields','observation'))
    if source['schema']!='UnavailableOptionBoardV1' or source['state'] not in ('pending','censored','invalid','not_applicable'):
        raise ContractError('finite option-board adapter admits unavailable diagnostics only')
    identity(source['reason'],limits)
    _rows(source['unavailable_fields'],limits.max_dependencies_per_sample,'option fields')
    names(tuple(source['unavailable_fields']),limits.max_dependencies_per_sample,limits)
    if source['unavailable_fields']!=sorted(source['unavailable_fields']):
        raise ContractError('canonical unavailable field order required')
    _,observation=_coverage(source['observation'],definition,limits)
    return source['state'],{'reason':source['reason'],'unavailable_fields':source['unavailable_fields']},observation


def validate_payload(outcome,candidate,definition,payloads,limits):
    envelope=bounded_json(outcome.payload,limits.max_payload_bytes,limits)
    _object(envelope,_ENVELOPE)
    if (envelope['schema']!='LabelPayloadV1' or envelope['kind']!=definition.kind
            or envelope['kind']!=outcome.payload_kind or envelope['candidate_version']!=digest(candidate)
            or envelope['definition_version']!=definition.version or envelope['observation_version']!=digest(outcome.observation)):
        raise ContractError('label payload ownership or schema differs from retained records')
    _rows(envelope['evidence'],limits.max_dependencies_per_sample,'label receipt slots')
    slots={}; used=set(); prior_slot=None
    for item in envelope['evidence']:
        _object(item,('slot','ref')); identity(item['slot'],limits)
        if prior_slot is not None and item['slot']<=prior_slot:
            raise ContractError('label evidence slots must be unique and canonical')
        prior_slot=item['slot']; ref=item['ref']
        _object(ref,('sha256','size_bytes','kind')); identity(ref['kind'],limits)
        if type(ref['sha256']) is not str or re.fullmatch('[0-9a-f]{64}',ref['sha256']) is None:
            raise ContractError('exact retained label evidence hash required')
        if type(ref['size_bytes']) is not int or not 0<=ref['size_bytes']<=limits.max_payload_bytes:
            raise ContractError('label evidence byte capacity exceeded')
        raw=payloads.get(ref['sha256'])
        if type(raw) is not bytes or len(raw)!=ref['size_bytes'] or hashlib.sha256(raw).hexdigest()!=ref['sha256']:
            raise IntegrityError('label source bytes differ from their retained receipt')
        slots[item['slot']]=bounded_json(raw,limits.max_payload_bytes,limits);used.add(ref['sha256'])
    state,data,observation=_derive(definition.kind,slots,candidate,definition,limits)
    if (outcome.state!=state or outcome.observation!=observation
            or _raw(envelope['data'],limits)!=_raw(data,limits)):
        raise ContractError('typed label differs from replay of its actual retained source evidence')
    return used


def _owner(ledger,candidate_id,definition_id):
    candidate=next((c for c in ledger.candidates if c.id==candidate_id),None)
    definition=next((d for d in ledger.definitions if d.id==definition_id),None)
    if candidate is None or definition is None or candidate.definition_id!=definition.id:
        raise ContractError('actual retained label candidate and definition required')
    return candidate,definition


def append_source(ledger,candidate_id,definition_id,*,source,outcome_id,kind,supersedes=None,extra_sources=(),source_ref=None):
    """Internal finite source replay; no precomputed outcome dictionary is admitted."""
    candidate,definition=_owner(ledger,candidate_id,definition_id)
    if kind!=definition.kind:
        raise ContractError('label adapter kind differs from definition')
    raw=_raw(source,ledger.limits)
    if source_ref is not None and (type(source_ref) is not ArtifactRef or
            _reference(raw,source_ref.kind)!={'sha256':source_ref.sha256,'size_bytes':source_ref.size_bytes,'kind':source_ref.kind}):
        raise IntegrityError('actual source reference differs from retained label source')
    if type(extra_sources) is not tuple or len(extra_sources)>1:
        raise ContractError('bounded exact label source slots required')
    sources={'source':(raw,'label_source_v1' if source_ref is None else source_ref.kind)}
    for slot,ref,blob in extra_sources:
        if slot in sources or type(ref) is not ArtifactRef or type(blob) is not bytes or len(blob)>ledger.limits.max_payload_bytes:
            raise ContractError('bounded exact additional source receipt required')
        if _reference(blob,ref.kind)!={'sha256':ref.sha256,'size_bytes':ref.size_bytes,'kind':ref.kind}:
            raise IntegrityError('extra label source receipt changed')
        sources[slot]=(blob,ref.kind)
    decoded={slot:bounded_json(blob,ledger.limits.max_payload_bytes,ledger.limits) for slot,(blob,_) in sources.items()}
    state,data,observation=_derive(kind,decoded,candidate,definition,ledger.limits)
    envelope={'schema':'LabelPayloadV1','kind':kind,'candidate_version':digest(candidate),
        'definition_version':definition.version,'observation_version':digest(observation),
        'evidence':[{'slot':slot,'ref':_reference(blob,tag)} for slot,(blob,tag) in sorted(sources.items())],'data':data}
    value=LabelOutcome(outcome_id,candidate_id,definition_id,state,kind,_raw(envelope,ledger.limits),
        observation,definition.endpoint_group,supersedes)
    return ledger.append_outcome(value,evidence_by_sha={hashlib.sha256(blob).hexdigest():blob for blob,_ in sources.values()})


def append_price_outcome(ledger,candidate_id,definition_id,*,target,initial,points,coverage,
                         up_ticks,down_ticks,outcome_id,supersedes=None):
    selected=bounded(points,_MAX_POINTS,'price label source')
    if type(initial) is not Ticks or any(type(p) is not PathPoint for p in selected):
        raise ContractError('actual typed price label observations required')
    source={'schema':'PriceLabelSourceV1','target':_path_target_record(target),'initial':initial.value,
        'points':[[p.at,p.sequence,p.price.value,p.known_at] for p in selected],
        'coverage':_coverage_record(coverage,target.decision_at),'up_ticks':up_ticks,'down_ticks':down_ticks}
    return append_source(ledger,candidate_id,definition_id,source=source,outcome_id=outcome_id,
                         kind='price_path',supersedes=supersedes)


def append_object_outcome(ledger,candidate_id,definition_id,*,target,initial,points,coverage,
                          geometry_ref,geometry_bytes,outcome_id,supersedes=None):
    selected=bounded(points,_MAX_POINTS,'object label source')
    if type(initial) is not Fraction or any(type(p) is not ExactPoint for p in selected):
        raise ContractError('actual typed object label observations required')
    source={'schema':'ObjectLabelSourceV1','target':_object_target_record(target),'initial':_pair(initial),
        'points':[[p.at,p.sequence,_pair(p.price),p.known_at] for p in selected],
        'coverage':_coverage_record(coverage,target.cut)}
    return append_source(ledger,candidate_id,definition_id,source=source,outcome_id=outcome_id,
        kind='object_path',supersedes=supersedes,extra_sources=(('geometry',geometry_ref,geometry_bytes),))


def append_oi_outcome(ledger,candidate_id,definition_id,*,prior_report,reports,position_date,query_at,
                      report_due,observation_boundary,boundary_known_at,receipt_coverage,expiry=None,
                      outcome_id,supersedes=None):
    selected=bounded(reports,ledger.limits.max_ledger_outcomes,'OI receipts')
    if type(prior_report) is not OIReport or any(type(r) is not OIReport for r in selected):
        raise ContractError('actual continuing-contract OI reports required')
    timestamp(query_at)
    selected=tuple(r for r in selected if r.known_at<=query_at)
    record=lambda r:{f.name:getattr(r,f.name) for f in fields(OIReport)}
    source={'schema':'OIEndpointSourceV1','prior':record(prior_report),'reports':[record(r) for r in selected],
        'contract':prior_report.contract,'position_date':position_date,'query_at':query_at,'report_due':report_due,
        'observation_boundary':observation_boundary,'boundary_known_at':boundary_known_at,
        'receipt_coverage':receipt_coverage,'expiry':expiry}
    return append_source(ledger,candidate_id,definition_id,source=source,outcome_id=outcome_id,
                         kind='oi_report',supersedes=supersedes)


def append_policy_outcome(ledger,candidate_id,definition_id,*,external_record,provenance_ref,
                          provenance_bytes,outcome_id,supersedes=None):
    raw=_raw(external_record,ledger.limits)
    if (type(provenance_ref) is not ArtifactRef or type(provenance_bytes) is not bytes or raw!=provenance_bytes
            or _reference(raw,provenance_ref.kind)!={'sha256':provenance_ref.sha256,
                'size_bytes':provenance_ref.size_bytes,'kind':provenance_ref.kind}):
        raise IntegrityError('external policy result differs from retained provenance bytes')
    return append_source(ledger,candidate_id,definition_id,source=external_record,outcome_id=outcome_id,
                         kind='policy_value',supersedes=supersedes,source_ref=provenance_ref)


def append_profile_outcome(ledger,candidate_id,definition_id,*,grid_version,initial,additions,
                           coverage,outcome_id,supersedes=None):
    _,definition=_owner(ledger,candidate_id,definition_id)
    initial=bounded(initial,_MAX_POINTS,'initial profile grid');additions=bounded(additions,_MAX_POINTS,'future profile grid')
    return append_source(ledger,candidate_id,definition_id,source={'schema':'ProfileMassSourceV1',
        'grid_version':grid_version,'initial':list(initial),'additions':list(additions),
        'observation':_coverage_record(coverage,definition.cut)},outcome_id=outcome_id,kind='profile_mass',supersedes=supersedes)
