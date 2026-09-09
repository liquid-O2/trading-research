"""Actual measurement publications and frozen location-label boundaries."""

from dataclasses import dataclass, field
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.context.range_adapter import _require_clock
from trading_research.foundations.contracts import Band
from trading_research.foundations.graph import Graph, InputPort, Port
from trading_research.foundations.object_graph import (
    Instrument, ObjectGraph, ObjectRevision, EvidenceVersion, AtomicBatch, PublicationClock,
    BirthKey, Geometry, Support, EvidencePurpose, Existence, Eligibility, EvidenceState,
)
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_name, bounded_rows, validate_trade_window
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.labels import ObservationWindow
from trading_research.research.object_labels import ObjectTarget, ExactPoint, reference_object_label


def _completed_measurement_receipt(record, clocks):
    """Freeze computation inputs separately from F10 receiving its result.

    The producer validates all inputs against the original computation cut.
    Its completed result then becomes an external F10 input at publication;
    treating the result as an input to its own earlier computation is invalid.
    """
    clocks.__post_init__()
    if clocks.actual_completion_at is None:
        raise ContractError('measurement receipt requires actual completion')
    receipt = {'kind': 'CausalMeasurementPublicationV1',
               'measurement': record, 'computation_clock': clocks}
    received = PublicationClock(clocks.known_at, clocks.known_at, clocks.known_at,
                                actual_completion_at=clocks.known_at)
    return digest(receipt), received


def measurement_dependency_graph():
    """F04 invalidation edges; labels never feed their own formation measurements."""
    roots = ('trades', 'quotes', 'calendar', 'bars', 'anchors', 'fit')
    dependencies = {
        'cvd': ('trades',), 'cohort_cvd': ('trades','fit'),
        'swings': ('bars',), 'divergence': ('cvd','swings','calendar'),
        'quote_pressure': ('quotes',), 'intensity': ('trades','quote_pressure','fit'),
        'profile': ('trades','bars','anchors'), 'side_profile': ('profile','cohort_cvd'),
        'tpo': ('profile','calendar'), 'vwap': ('trades','bars','anchors'),
        'footprint': ('side_profile','bars'), 'memory': ('trades','swings'),
        'references': ('trades','calendar','bars'),
        'location': ('profile','side_profile','vwap','tpo','memory','references'),
        'labels': ('location','trades'),
    }
    ports = [Port(k,'F04',0,'MeasurementPort.v1',frozenset({'value','lineage'}),
                  lane='market' if k in ('trades','quotes') else 'optional') for k in roots]
    stage = {k:0 for k in roots}
    for key, sources in dependencies.items():
        stage[key] = max(stage[s] for s in sources)+1
        ports.append(Port(key,'measurements',stage[key],'MeasurementPort.v1',frozenset({'value','lineage'}),
            tuple(InputPort(s,'MeasurementPort.v1',frozenset({'value','lineage'})) for s in sources)))
    return Graph(ports)


def publish_measurement_evidence(value, *, graph, instrument, clocks, source_id, view=None):
    """Revalidate an actual producer before exposing its completed F10 evidence."""
    from trading_research.measurements.cvd import CVDMeasurement, _validate_cvd
    from trading_research.measurements.structure import SwingSnapshot, validate_swing_snapshot
    from trading_research.measurements.divergence import DivergenceEndpoint, validate_endpoint
    from trading_research.measurements.memory import MemorySnapshot, validate_memory
    from trading_research.measurements.quotes import QuoteCapture, validate_quote_capture, measure_quote_pressure
    if type(graph) is not ObjectGraph or type(instrument) is not Instrument or type(clocks) is not PublicationClock:
        raise ContractError('actual graph, raw instrument and publication clocks required')
    if clocks.actual_completion_at is None:
        raise ContractError('measurement publication requires observed computation completion')
    instrument.__post_init__()
    bounded_name(source_id)
    current_windows, current_swing = (), None
    if type(value) is CVDMeasurement:
        _validate_cvd(value,view)
        capture=value._recipe[0]
        current_windows=tuple((c,view) for c in (capture,*value._recipe[2]))
        raw, at, known = capture.window.instrument,capture.window.cut,capture.window.published_at
        record = {k:getattr(value,k) for k in value.__dataclass_fields__ if k != '_recipe'}
    elif type(value) is SwingSnapshot:
        validate_swing_snapshot(value)
        current_swing=value
        raw, at, known, record = value.instrument,value.cut,value.published_at,value.record()
    elif type(value) is DivergenceEndpoint:
        validate_endpoint(value)
        current_windows=((value._recipe['cvd_capture'],value._recipe['cvd_view']),)
        current_swing=value._recipe['swings']
        raw, at, known, record = value.instrument,value.extreme_at,value.known_at,value.record()
    elif type(value) is MemorySnapshot:
        validate_memory(value)
        current_windows=tuple(zip(value._recipe['captures'],value._recipe['views']))
        raw, at, known, record = value.instrument,value.cut,value.published_at,value.record()
    elif type(value) is QuoteCapture:
        validate_quote_capture(value)
        if value.instrument != instrument:
            raise ContractError('quote publication changes its full raw instrument definition')
        raw, at, known, record = value.instrument.raw_symbol,value.cut,value.published_at,measure_quote_pressure(value)
    else:
        raise ContractError('measurement producer has no registered public evidence adapter')
    if raw not in (instrument.key,instrument.raw_symbol) or known > clocks.decision_cut or known > clocks.input_known_at:
        raise DependencyUnavailable('measurement source is unavailable at its public decision cut')
    for capture,source_view in current_windows:
        validate_trade_window(capture,source_view,publication_cut=clocks.decision_cut)
    if current_swing is not None:
        _current_swing(current_swing,clocks.decision_cut)
    receipt_hash, received = _completed_measurement_receipt(record, clocks)
    evidence=EvidenceVersion(source_id,'e:'+digest((source_id,receipt_hash)),0,None,at,clocks.known_at,
        Support.OBSERVED,instrument,receipt_hash,EvidencePurpose.MEASUREMENT)
    batch=AtomicBatch('batch:'+digest(evidence),graph.sequence+1,graph.definition.version,received,(evidence,),1)
    graph.commit_batch(batch,expected_head=graph.head)
    return evidence


def _current_swing(value, cut):
    from trading_research.measurements.structure import SwingBarCapture
    capture, _, view = value._recipe
    if type(capture) is SwingBarCapture:
        for b in capture.bars:
            current = capture._engine.asof(bar_id=b.bar_id,cut=cut)
            if current is None or current.version_id != b.version_id:
                raise IntegrityError('known shared-bar revision requires rebuilding the swing')
    else:
        validate_trade_window(capture,view,publication_cut=cut)


@dataclass(frozen=True)
class MeasurementLocation:
    measurement_id: str
    producer: str
    role: str
    instrument: Instrument
    geometry: Geometry
    anchor_versions: tuple
    source_ids: tuple
    formed_at: int
    confirmed_at: int
    known_at: int
    _recipe: object = field(default=None,init=False,compare=False,repr=False)

    def record(self):
        return {k:getattr(self,k) for k in self.__dataclass_fields__ if k != '_recipe'}

    @property
    def id(self):
        return digest(self.record())


def measurement_location(value, *, role, index=0, multiplier=Fraction(1)):
    from trading_research.measurements.profiles import ProfileSnapshot, validate_profile, profile_geometry, side_geometry, profile_base
    from trading_research.measurements.vwap import VWAPSnapshot, validate_vwap, vwap_bands
    if type(index) is not int or not 0 <= index < 4096:
        raise ContractError('bounded location index required')
    bounded_name(role)
    if type(value) is ProfileSnapshot:
        validate_profile(value)
        base=profile_base(value)
        recipe=base._recipe[1]
        anchors=recipe['anchors'];producer='profile'
        geometry=profile_geometry(value)
        side=side_geometry(value)
        points={
            'poc':geometry['poc_set'], 'value_low':geometry['value_rows'][:1],
            'value_high':geometry['value_rows'][-1:], 'buy_delta_peak':side['maximum_rows'],
            'sell_delta_peak':side['minimum_rows'], 'absolute_delta_peak':side['absolute_peak_rows'],
        }
        regions={'hvn':tuple(p['rows'] for p in geometry['local_peaks']),
                 'lvn':geometry['interior_valleys'], 'poc_plateau':geometry['maximum_plateaus']}
        if (not value.history_complete or value.representation.startswith('bar_proxy')
                or any(sum(x) for x in (value.unpriced,value.low_overflow,value.high_overflow))):
            raise DependencyUnavailable('public exact location requires complete observed trade geography')
        if role in ('buy_delta_peak','sell_delta_peak','absolute_delta_peak') and any(r.unknown for r in value.rows):
            raise DependencyUnavailable('public signed location requires complete directional geography')
        if role in points:
            rows=points[role]
            if index >= len(rows):raise DependencyUnavailable('requested profile location is absent')
            low=high=Fraction(value.grid.origin_ticks+rows[index]*value.grid.width_ticks)
        elif role in regions:
            rows=regions[role]
            if index >= len(rows):raise DependencyUnavailable('requested profile region is absent')
            low=Fraction(value.grid.origin_ticks+rows[index][0]*value.grid.width_ticks)
            high=Fraction(value.grid.origin_ticks+(rows[index][1]+1)*value.grid.width_ticks)
        else:
            raise ContractError('undeclared profile location role')
    elif type(value) is VWAPSnapshot:
        validate_vwap(value)
        recipe=value._recipe;anchors=recipe['anchors'];producer='vwap'
        if value.mean is None or not value.history_complete or value.unpriced_mass:
            raise DependencyUnavailable('public VWAP location requires complete supported priced mass')
        bands=vwap_bands(value,multipliers=(multiplier,))
        points={'mean':value.mean,'median':bands['median'],'quantile_low':bands['quantiles'][0][1],
                'quantile_high':bands['quantiles'][2][1],
                'sigma_low':Fraction(bands['sigma_bands'][0][1]),'sigma_high':Fraction(bands['sigma_bands'][0][2])}
        if role not in points or index != 0:
            raise ContractError('undeclared VWAP location role/index')
        low=high=Fraction(points[role])
    else:
        raise ContractError('location requires an actual registered profile or VWAP producer')
    instrument=anchors[0].instrument
    if any(a.instrument != instrument for a in anchors):
        raise ContractError('location anchors cross exact raw contracts')
    geometry=Geometry(low,high,low,high,'measurement_ticks_v1:'+producer+':'+role,
                      instrument.raw_symbol,instrument.raw_symbol)
    result=MeasurementLocation(value.id,producer,role,instrument,geometry,
        tuple(a.anchor.version_id for a in anchors),tuple(sorted({e.source_id for a in anchors for e in a.evidence})),
        min(a.anchor.start for a in anchors),max(a.anchor.confirmed_at for a in anchors),value.published_at)
    object.__setattr__(result,'_recipe',dict(value=value,role=role,index=index,multiplier=multiplier))
    return result


def validate_measurement_location(location):
    if (type(location) is not MeasurementLocation or type(location._recipe) is not dict
            or measurement_location(**location._recipe) != location):
        raise IntegrityError('location geometry differs from its actual measurement recipe')


def publish_measurement_location(location, *, graph, clocks, object_id, generator='measurement-location-v1', previous=None):
    validate_measurement_location(location)
    if type(graph) is not ObjectGraph or type(clocks) is not PublicationClock or clocks.actual_completion_at is None:
        raise ContractError('location publication requires actual F10 and computation completion')
    if location.known_at > min(clocks.input_known_at,clocks.decision_cut):
        raise DependencyUnavailable('measurement location was unavailable at publication input cut')
    from trading_research.measurements.profiles import ProfileSnapshot, profile_base
    value=location._recipe['value']
    recipe=profile_base(value)._recipe[1] if type(value) is ProfileSnapshot else value._recipe
    for c,v in zip(recipe['captures'],recipe['views']):
        validate_trade_window(c,v,publication_cut=clocks.decision_cut)
    if graph.definition.ttl_ns is None:
        raise ContractError('location requires a fixed registered outcome-independent TTL')
    accumulation_evidence={}
    for captured_anchor in recipe['anchors']:
        anchor_id=captured_anchor.anchor.version_id
        anchor=graph.get_version(anchor_id)
        if anchor != captured_anchor.anchor or anchor.known_at > min(clocks.decision_cut,clocks.input_known_at):
            raise IntegrityError('measurement anchor is absent from the actual publication graph')
        graph.lineage_closure((anchor_id,),clocks.decision_cut)
        for evidence in captured_anchor.evidence:
            if graph.get_version(evidence.version_id) != evidence or evidence.known_at > min(clocks.decision_cut,clocks.input_known_at):
                raise IntegrityError('measurement source evidence differs from its actual publication graph')
            if evidence.version_id not in anchor.evidence_versions:
                accumulation_evidence[evidence.version_id]=evidence
    revision,predecessor,born,birth=0,None,clocks.known_at,None
    source_id='s:'+digest((object_id,location.producer,location.role))
    if previous is not None:
        if type(previous) is not ObjectRevision or graph.get_version(previous.version_id) != previous:
            raise IntegrityError('location correction lacks its actual predecessor')
        current=graph.object_asof(object_id,clocks.decision_cut)
        if current is None or current.object != previous or previous.roles != (location.role,):
            raise ContractError('location correction must extend the current same-role object')
        if previous.birth.instrument != location.instrument or previous.birth.generator != generator:
            raise ContractError('location correction changed canonical birth')
        original_anchors={graph.get_version(v).anchor_id:(graph.get_version(v).start,graph.get_version(v).end)
                          for v in previous.birth.anchors}
        corrected_anchors={graph.get_version(v).anchor_id:(graph.get_version(v).start,graph.get_version(v).end)
                           for v in location.anchor_versions}
        if original_anchors!=corrected_anchors:
            raise ContractError('location correction changed its original anchor formation')
        receipt_predecessors=[eid for eid in previous.evidence_versions if graph.get_version(eid).source_id==source_id]
        if len(receipt_predecessors)!=1:
            raise IntegrityError('location correction requires one actual measurement receipt predecessor')
        revision,predecessor,born,birth=previous.revision+1,receipt_predecessors[0],current.born_at,previous.birth
    if clocks.known_at >= born+graph.definition.ttl_ns or not location.instrument.valid(clocks.known_at):
        raise ContractError('location publication is outside its original TTL/raw lifetime')
    receipt_hash, received = _completed_measurement_receipt(location.record(), clocks)
    ev=EvidenceVersion(source_id,'e:'+digest((object_id,revision,receipt_hash)),revision,predecessor,
        location.formed_at,clocks.known_at,Support.OBSERVED,location.instrument,receipt_hash,EvidencePurpose.MEASUREMENT)
    birth=birth or BirthKey(generator,'v1',location.instrument,location.anchor_versions,
                           tuple(sorted({source_id,*location.source_ids})),object_id)
    obj=ObjectRevision(object_id,'v:'+digest((object_id,revision,location.id)),revision,
        None if previous is None else previous.version_id,birth,location.geometry,(ev.version_id,*sorted(accumulation_evidence)),(),
        Existence.ACTIVE,Eligibility.ELIGIBLE,EvidenceState.OBSERVED,location.confirmed_at,clocks.known_at,(location.role,))
    batch=AtomicBatch('batch:'+digest(obj),graph.sequence+1,graph.definition.version,received,(ev,obj),2)
    graph.commit_batch(batch,expected_head=graph.head)
    return obj


@dataclass(frozen=True)
class LocationTarget:
    target: ObjectTarget
    horizon_kind: str
    selection_version: str
    _recipe: object = field(default=None,init=False,compare=False,repr=False)


def location_targets(graph, object_version, *, selection, cut, side, favorable_distance, adverse_distance,
                     observation_process='observed_trade_prices'):
    _require_clock(selection)
    timestamp(cut)
    if type(graph) is not ObjectGraph or selection.selected_at > cut:
        raise ContractError('target requires actual available object and session clock')
    obj=graph.get_version(object_version)
    if type(obj) is not ObjectRevision or obj.birth.instrument != selection.instrument:
        raise ContractError('target object and calendar raw instrument differ')
    current=graph.object_asof(obj.object_id,cut)
    if current is None or current.object != obj or not current.available(cut,graph.definition.ttl_ns):
        raise DependencyUnavailable('target requires the actual eligible object at its original cut')
    session_end=selection.session.close_at
    ends=(('5m',cut+300000000000),('15m',cut+900000000000),('60m',cut+3600000000000),('session_remainder',session_end))
    result=[]
    for kind,end in ends:
        if end <= cut or any(end > t for t in (current.born_at+graph.definition.ttl_ns,
                *(t for t in (obj.birth.instrument.valid_until,obj.birth.instrument.expiry_at) if t is not None))):
            raise ContractError('mandatory location horizon exceeds fixed object/raw lifetime')
        target=ObjectTarget('target:'+digest((object_version,cut,kind,side,favorable_distance,adverse_distance,observation_process)),
            object_version,cut,end,Band(obj.geometry.lower,obj.geometry.upper),side,
            favorable_distance,adverse_distance,observation_process)
        wrapped=LocationTarget(target,kind,selection.version_id)
        object.__setattr__(wrapped,'_recipe',dict(graph=graph,object_version=object_version,selection=selection,
            cut=cut,side=side,favorable_distance=favorable_distance,adverse_distance=adverse_distance,
            observation_process=observation_process))
        result.append(wrapped)
    return tuple(result)


def location_outcome(target, *, initial, points, coverage, query_at):
    timestamp(query_at)
    bounded_rows(points,4096,name='location future observations')
    if type(target) is not LocationTarget or type(target._recipe) is not dict:
        raise ContractError('actual frozen location target required')
    fresh=next(t for t in location_targets(**target._recipe) if t.horizon_kind == target.horizon_kind)
    if fresh != target:
        raise IntegrityError('location target changed after its original formation')
    if type(coverage) is not ObservationWindow or any(type(p) is not ExactPoint for p in points):
        raise ContractError('actual typed V01 observations required')
    coverage.__post_init__()
    maturity=max(target.target.end,coverage.certified_through,*(p.known_at for p in points))
    if query_at < maturity:
        return {'state':'pending','target_version':target.target.version,'maturity_at':maturity,'contact_at':None}
    result=reference_object_label(target.target,initial=initial,points=points,coverage=coverage)
    return {'state':'complete' if coverage.end == target.target.end and not coverage.gaps else 'censored',**result}
