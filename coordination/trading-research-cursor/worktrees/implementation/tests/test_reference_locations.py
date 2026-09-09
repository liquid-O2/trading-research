"""Registered 32-case M12/L02/L03 suite; no market source or fitted model."""
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import shutil
import sqlite3
import unittest

from references import reference_locations_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import Watermark, WindowCoverage
from trading_research.foundations.calendar import Calendar, Session
from trading_research.foundations.cash_calendar import zone_version
from trading_research.foundations.intervals import Span, NamedInterval, IntervalGraph, WallRule
from trading_research.foundations.multiresolution import (
    BarDomain, BarDefinition, BarLimits, SharedBarEngine, WindowRequest,
)
from trading_research.foundations.object_graph import (
    Instrument, PublicationClock, RegistryDefinition, ObjectGraph, ObjectRevision, AtomicBatch,
    Presentation, EvidenceVersion, Support, BirthKey, Geometry, Existence, Eligibility,
    EvidenceState, ObservationEvent, ObservationKind, content_hash,
)
from trading_research.foundations.units import Ticks
from trading_research.foundations.contracts import Band
from trading_research.context.range_adapter import (
    select_clock, primitive_from_shared_bar, primitive_registry_links, publish_range_batch,
)
from trading_research.measurements.tape import Trade
from trading_research.measurements.reference_prices import (
    ReferencePrice, OfficialSettlement, session_references, range_formula,
    select_prior_session, require_prior_primitive, official_settlement_at,
    reference_gap, ticks_to_points, points_to_ticks,
)
from trading_research.location.edge_extensions import (
    Location, edge_extensions, object_members, require_candidate_capacity, line_geometry,
)
from trading_research.location.prior_session import (
    prior_locations, ReferenceObservation, reference_freshness,
)
from trading_research.research.object_labels import ObjectTarget, ExactPoint, reference_object_label
from trading_research.research.labels import ObservationWindow

GOLD = json.loads((Path(__file__).parent / 'golden/m12_l02_l03_engineering_v1.json').read_text())
CASES = {c['case_id']: c for c in GOLD['cases']}
METRICS = {}


def merged(base, override):
    result = deepcopy(base)
    for key, value in override.items():
        result[key] = merged(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else deepcopy(value)
    return result


def make_trade(row, domain):
    return Trade(row['id'], 'content:' + row['id'], domain.instrument,
                 row['event_at'], row['known_at'], Ticks(row['price_ticks']),
                 row.get('size', 1), None, row.get('sequence'), domain.aggregation_unit,
                 row.get('history_complete', True))


def publication_clocks(cut=203, known=205, source=203):
    return PublicationClock(cut, source, known, actual_completion_at=known)


def sealed(override=None, *, calendar=None):
    """Only actual F03 calendar/graph -> F09 factory -> certified common adapter."""
    cfg = merged(GOLD['fixtures']['sealed_range_base'], override or {})
    raw = cfg['raw_instrument']
    instrument = Instrument(**{**raw, 'tick_size_points': Fraction(raw['tick_size_points'])})
    c = cfg['calendar']; day = date.fromisoformat(c['trading_date'])
    session = Session(c['session_id'], day, c['instrument_root'], c['open_at'], c['close_at'],
                      (), 0, c['known_at'], c['calendar_version'], c['timezone_version'],
                      c['eligible'], 'synthetic explicit calendar fact')
    cal = Calendar() if calendar is None else calendar
    cal.append(session)
    node = NamedInterval('fixture-range', 'M12-fixture', (Span(*cfg['formation']),),
                         c['known_at'], 'fixture-named-v1', c['clock_variant_id'],
                         c['timezone_version'], (day,))
    graph = IntervalGraph('M12-fixture', (node,))
    selection = select_clock(calendar=cal, interval_graph=graph, interval_name=node.name,
                             trading_date=day, instrument_root=c['instrument_root'],
                             instrument=instrument, cut=cfg['bar_publication']['observation_cut'])
    domain = BarDomain(instrument.raw_symbol, 'registered-whole-print', 'registered-whole-print')
    definition = BarDefinition(domain, 'm12-fixture-v1', selection.interval_graph.version, selection.clock_id)
    engine = SharedBarEngine(domain, (definition,), limits=BarLimits(128, 8, 4, 32))
    rows = tuple(make_trade(r, domain) for r in cfg['events'])
    engine.add_many(tuple(sorted(rows, key=lambda r: r.known_at)))
    coverage = cfg['coverage']; wm = cfg['watermark']
    request = WindowRequest(definition.id, *cfg['formation'],
                            WindowCoverage(domain.instrument, *coverage['interval'],
                                           tuple(tuple(p) for p in coverage['observed']),
                                           coverage['known_at'], coverage['version']),
                            Watermark(wm['event_through'], wm['known_at'], wm['version']))
    pub = cfg['bar_publication']
    bar = engine.publish_window(engine.capture(pub['observation_cut']), request,
                                published_at=pub['published_at'])
    primitive = primitive_from_shared_bar(selection=selection, engine=engine,
                                          publication_version_id=bar.version_id,
                                          cut=cfg['derivation']['cut'])
    dc = cfg['derivation']
    clocks = publication_clocks(dc['cut'], dc['known_at'], bar.published_at)
    return cfg, engine, request, bar, primitive, clocks


def refs_for(case_id):
    vector = CASES[case_id]['fixture_vector']
    bundle = sealed(vector.get('override'))
    cfg, _, _, _, primitive, clocks = bundle
    return bundle, session_references(primitive, clocks=clocks,
                                      horizon_end=cfg['derivation']['horizon_end'])


def edge_for(case_id, **kwargs):
    vector = CASES[case_id]['fixture_vector']
    bundle = sealed(vector.get('override'))
    cfg, _, _, _, primitive, clocks = bundle
    ratios = tuple(Fraction(v) for v in vector.get('ratios', [vector.get('ratio', '1/2')]))
    return bundle, edge_extensions(primitive, ratios=ratios, clocks=clocks,
                                   horizon_end=cfg['derivation']['horizon_end'], **kwargs)


def native_ref(value, *, instrument, kind='session_high', known=205, source='s:fixture', horizon=300):
    return ReferencePrice('ref:' + source + ':' + kind, kind, instrument, Fraction(value),
                          min(known, 200), known, horizon, (source,), 'observed',
                          'explicit typed synthetic message')


def graph_for(path, *, horizon=300, known=205):
    definition = RegistryDefinition(
        id='def:m12-fixture', generator_versions=(('L02-edge-extensions-v1', 'v1'),
                                                  ('L03-prior-session-v1', 'v1')),
        ttl_ns=horizon-known, batch_members_max=128, hot_active_max=64, hot_relations_max=128)
    return ObjectGraph(path, definition=definition)


def publish_result(graph, result, *, batch='batch:fixture', sequence=1, links=None, previous=()):
    links = links or primitive_registry_links(result.primitive)
    members = object_members(result, links=links, previous=previous)
    receipt = publish_range_batch(graph=graph, primitives=(result.primitive,), registry_links=(links,),
                                  derived_members=members, batch_id=batch, batch_sequence=sequence,
                                  clocks=result.clocks, expected_head=graph.head)
    return receipt, links, tuple(m.member for m in members if isinstance(m.member, ObjectRevision))


def prior_choice(primitive, *, cut, current_start=201, current_end=300):
    calendar = primitive.selection._calendar_receipt[1]
    current_day = primitive.selection.session.trading_date + timedelta(days=1)
    calendar.append(Session('fixture-current-' + current_day.isoformat(), current_day,
        primitive.selection.session.instrument_root, current_start, current_end, (), 0,
        primitive.selection.session.known_at, 'fixture-current-v1',
        primitive.selection.session.timezone_version, True, 'explicit synthetic current session'))
    return select_prior_session(calendar=calendar, current_date=current_day,
        instrument_root=primitive.selection.session.instrument_root, cut=cut)


def retain_reference(reference, path):
    """Actual F10 retention of a separately derived typed reference receipt."""
    generator='M12-reference-type-v1'
    graph=ObjectGraph(path,definition=RegistryDefinition(id='def:typed-reference',
        generator_versions=((generator,'v1'),),ttl_ns=reference.horizon_end-reference.known_at))
    eid='e:'+reference.version; sid='s:'+reference.version
    evidence=EvidenceVersion(sid,eid,0,None,reference.observed_at,reference.known_at,
        Support.OBSERVED,reference.instrument,reference.version)
    birth=BirthKey(generator,'v1',reference.instrument,(),(sid,),reference.kind)
    p=reference.value_ticks; raw=reference.instrument.raw_symbol
    geometry=Geometry(p,p,p,p,'def:'+reference.kind,raw,raw)
    obj=ObjectRevision('o:'+birth.version,'v:'+content_hash((birth,geometry,eid)),0,None,birth,
        geometry,(eid,),(),Existence.ACTIVE,Eligibility.ELIGIBLE,EvidenceState.OBSERVED,
        reference.observed_at,reference.known_at,(reference.kind,))
    graph.commit_batch(AtomicBatch('batch:typed-reference',1,graph.definition.version,
        publication_clocks(reference.known_at,reference.known_at,reference.known_at),(evidence,obj),2),expected_head=None)
    return graph,obj


class ReferenceLocationsTests(unittest.TestCase):
    def assertLiteralFields(self, cfg, primitive):
        rows = tuple((r['id'], r['event_at'], r['price_ticks'], r.get('sequence')) for r in cfg['events'])
        expected, ids, first, last = literal.sealed_fields(rows, *cfg['formation'], cfg['coverage']['observed'])
        self.assertEqual(primitive.ohlc, expected)
        self.assertEqual(set(primitive.source_event_ids), set(ids))
        self.assertEqual((primitive.first_event_at, primitive.last_event_at), (first, last))

    def test_m12_01_delayed_certified_first_print(self):
        bundle, refs = refs_for('M12-01'); cfg, _, _, _, p, _ = bundle
        self.assertLiteralFields(cfg, p)
        r = refs.field('open')
        self.assertEqual((r.kind, r.observed_at, r.known_at), ('session_first_eligible_trade', 104, 205))
        self.assertEqual([r.value_at(t) for t in (204, 205)], [None, Fraction(400)])

    def test_m12_02_partial_endpoints_and_restore(self):
        bundle, refs = refs_for('M12-02'); cfg, e, _, _, p, clocks = bundle
        self.assertLiteralFields(cfg, p)
        self.assertEqual(tuple(r.value_ticks for r in refs.references), (None, None, None, Fraction(400)))
        self.assertEqual(refs.first_observed.value_ticks, 400); self.assertFalse(refs.complete_e0)
        for v in CASES['M12-02']['fixture_vector']['endpoint_coverage_variants']:
            override = {'formation': v['formation'], 'events': v['events'],
                        'raw_instrument': v['raw_instrument_lifetime'], 'calendar': v['calendar'],
                        'coverage': {'interval': v['formation'], 'observed': v['coverage'],
                                     'known_at': v['coverage_known_at'], 'version': 'cov:endpoint'},
                        'watermark': {'event_through': v['watermark_event_through'],
                                      'known_at': v['watermark_known_at'], 'version': 'wm:endpoint'},
                        'bar_publication': {'observation_cut': v['watermark_known_at'],
                                            'published_at': v['bar_published_at']},
                        'derivation': {'cut': v['decision_cut'], 'known_at': v['actual_completion_at'],
                                       'actual_completion_at': v['actual_completion_at'],
                                       'horizon_end': v['horizon_end']}}
            cfg, engine, _, bar, primitive, clocks = sealed(override)
            self.assertLiteralFields(cfg, primitive)
            self.assertEqual(primitive.ohlc, tuple(v['expected_OHLC']))
            self.assertEqual([s.status for s in primitive.field_support], v['expected_per_field_support'])
            rset = session_references(primitive, clocks=clocks, horizon_end=v['horizon_end'])
            supported = next(r for r in rset.references if r.value_ticks is not None)
            self.assertEqual([supported.available(t) for t in v['query_cuts']], v['expected_available'])
            restored = SharedBarEngine.restore(engine.checkpoint())
            again = primitive_from_shared_bar(selection=primitive.selection, engine=restored,
                                               publication_version_id=bar.version_id, cut=v['decision_cut'])
            self.assertEqual(again.record(), primitive.record())
            self.assertEqual(session_references(again, clocks=clocks, horizon_end=v['horizon_end']), rset)

    def test_m12_03_ambiguous_open_keeps_extrema(self):
        bundle, refs = refs_for('M12-03'); cfg, _, _, _, p, clocks = bundle
        self.assertLiteralFields(cfg, p)
        self.assertEqual(p.ohlc, (None, 410, 398, 410)); self.assertFalse(refs.complete_e0)
        self.assertTrue(p.supports('high', 'low')); self.assertFalse(p.supports('open', 'high', 'low', 'close'))
        self.assertEqual(len(edge_extensions(p, clocks=clocks, horizon_end=300).locations), 4)

    def test_m12_04_empty_complete_has_no_prices(self):
        bundle, refs = refs_for('M12-04')
        self.assertEqual(bundle[4].ohlc, (None,)*4)
        self.assertEqual(refs.status, 'complete_no_execution'); self.assertFalse(refs.complete_e0)
        self.assertEqual(bundle[4].source_event_ids, ())

    def test_m12_05_half_open_close(self):
        bundle, refs = refs_for('M12-05'); cfg, _, _, _, p, _ = bundle
        self.assertLiteralFields(cfg, p); self.assertEqual(p.ohlc, (400, 404, 400, 404))
        self.assertNotIn('outside', p.source_event_ids); self.assertEqual(refs.field('close').observed_at, 199)

    def test_m12_06_calendar_predecessor_complete_sequence(self):
        cfg = GOLD['fixtures']['real_ny_E0_calendar']; cal, instrument, current, prior = real_calendar()
        cut = CASES['M12-06']['fixture_vector']['calendar_selection_cut']
        selection = select_prior_session(calendar=cal, current_date=current.trading_date, instrument_root='NQ', cut=cut)
        self.assertEqual(selection.prior.id, cfg['prior_RTH']['id']); self.assertEqual(len(selection.traversed_versions), 4)
        rows = [(date(2025, 1, 3), True, cfg['prior_RTH']['id'], (400,420,392,412)),
                *( (date(2025,1,d),False,'nonRTH',None) for d in (4,5,6))]
        self.assertEqual(literal.prior_row(rows, current.trading_date)[0], selection.prior.id)
        bundle = real_primitive(cal, instrument, prior, CASES['M12-06']['fixture_vector']['prior_events'],
                                current=False, cut=cut)
        p, _, _, _ = bundle
        require_prior_primitive(p, selection, current_instrument=instrument)
        self.assertEqual(p.ohlc, (400,420,392,412))
        missing = Calendar(); missing.append(current); missing.append(prior)
        with self.assertRaises(DependencyUnavailable):
            select_prior_session(calendar=missing, current_date=current.trading_date, instrument_root='NQ', cut=cut)

    def test_m12_07_shortened_exact_session(self):
        bundle, refs = refs_for('M12-07')
        self.assertEqual(bundle[4].formation_end, 150)
        self.assertEqual(refs.field('close').observed_at, 149)
        self.assertEqual([refs.field('close').value_at(t) for t in (154,155)], [None,Fraction(406)])

    def test_m12_08_equal_numbers_have_distinct_reference_types(self):
        cfg,_,_,_,p,clocks=sealed()
        instrument=p.instrument
        rows = CASES['M12-08']['fixture_vector']['typed_reference_rows']
        first=session_references(p,clocks=clocks,horizon_end=300).field('open')
        bar_events=[{'id':'bar'+str(i),'event_at':at,'known_at':at+1,'price_ticks':price,'sequence':i}
                    for i,(at,price) in enumerate(((110,400),(120,410),(150,390),(199,400)))]
        _,_,_,_,bp,bc=sealed({'formation':[110,200],'events':bar_events,
            'coverage':{'interval':[110,200],'observed':[[110,200]]},
            'bar_publication':{'observation_cut':212,'published_at':213},
            'derivation':{'cut':213,'known_at':215}})
        bar_open=session_references(bp,clocks=bc,horizon_end=300,semantic='bar').field('open')
        official=official_settlement_at((OfficialSettlement('equal-settlement','settlement-v0',0,None,
            instrument,190,220,220,Fraction(400),'explicit-official-v1'),),cut=220,
            clocks=publication_clocks(220,220,220),horizon_end=300)
        midpoint=range_formula(bp,formula='arithmetic_midpoint',clocks=publication_clocks(223,225,223),horizon_end=300)
        refs=(first,bar_open,official,midpoint)
        self.assertEqual(len({r.id for r in refs}),4); self.assertEqual(len({r.kind for r in refs}),4)
        self.assertEqual([sum(r.available(t) for r in refs) for t in (205,215,220,225)],[1,2,3,4])
        self.assertEqual(len({r.value_ticks for r in refs}),1)
        self.assertEqual([(r.value_ticks,r.observed_at,r.known_at) for r in refs],
                         [(Fraction(r['value_ticks']),r['event_at'],r['known_at']) for r in rows])
        with tempfile.TemporaryDirectory() as d:
            histories=[retain_reference(r,Path(d)/('reference'+str(i)+'.sqlite')) for i,r in enumerate(refs)]
            self.assertEqual(len({obj.object_id for graph,obj in histories}),4)
            self.assertEqual([sum(len(graph.active_set(t)) for graph,obj in histories)
                              for t in (205,215,220,225)],[1,2,3,4])
            for graph,obj in histories:
                self.assertEqual(graph.get_version(obj.version_id),obj)

    def test_m12_09_official_revisions_are_causal(self):
        instrument = sealed()[4].instrument
        rows = CASES['M12-09']['fixture_vector']['official_messages']
        messages = tuple(OfficialSettlement(r['report_id'],r['version_id'],r['revision'],r['predecessor'],
                                            instrument,r['observation_at'],r['published_at'],r['received_at'],
                                            Fraction(r['price_ticks']),'official-synthetic-message-v1') for r in rows)
        answers = []
        for cut in (219,230,240):
            result = official_settlement_at(messages,cut=cut,clocks=publication_clocks(cut,cut, min(cut,240)),horizon_end=300)
            answers.append(None if result is None else result.value_ticks)
        self.assertEqual(answers,[None,400,402])
        self.assertEqual(answers,[literal.official_at([(r['version_id'],r['received_at'],r['price_ticks']) for r in rows],t) for t in (219,230,240)])
        old = official_settlement_at(messages[:1],cut=230,clocks=publication_clocks(230,230,220),horizon_end=300)
        self.assertEqual(old.value_ticks,400); self.assertEqual(old.source_versions[0],'settle:D:v0')
        self.assertIsNone(official_settlement_at((),cut=240,clocks=publication_clocks(240,240,240),horizon_end=300))

    def test_m12_10_body_range_and_named_gaps(self):
        _,_,_,_,p,_ = sealed(); clocks=publication_clocks(220,222,220)
        values = tuple(range_formula(p,formula=f,clocks=clocks,horizon_end=300).value_ticks for f in ('body25','range25'))
        self.assertEqual(values,(406,399)); self.assertEqual(values,literal.body_and_range(400,420,392,408))
        current=native_ref(416,instrument=p.instrument,kind='current_open',known=211)
        refs=(native_ref(408,instrument=p.instrument,kind='session_last_eligible_trade'),
              native_ref(410,instrument=p.instrument,kind='official_settlement',known=220),
              native_ref(420,instrument=p.instrument))
        self.assertEqual(tuple(reference_gap(current,r,cut=222).value_ticks for r in refs),(8,6,-4))
        self.assertEqual(literal.gaps(416,408,410,420),(8,6,-4))

    def test_m12_11_raw_contract_mismatch_is_not_a_gap(self):
        _,_,_,_,p,clocks=sealed({'raw_instrument':{'raw_symbol':'NQ-OLD','definition_version':'def:old'},
            'events':[{'id':'old-close','event_at':199,'known_at':200,'price_ticks':400,'sequence':1}]})
        old=session_references(p,clocks=clocks,horizon_end=300).field('close')
        new=native_ref(440,instrument=replace(p.instrument,raw_id='102',raw_symbol='NQ-NEW',definition_version='def:new'),kind='current_open',known=211)
        result=reference_gap(new,old,cut=211)
        self.assertIsNone(result.value_ticks); self.assertEqual(result.status,'explicit_valid_mapping_required')
        with tempfile.TemporaryDirectory() as d:
            graph=graph_for(Path(d)/'raw.sqlite')
            location=prior_locations(p,clocks=clocks,horizon_end=300,fields=('close',),semantic='current_range')
            _,_,objects=publish_result(graph,location)
            current=graph.freeze_candidates(cut_id='cut:new-raw',at=211,instrument=new.instrument,expected_head=graph.head)
            self.assertEqual(current['candidate_count'],0)
            self.assertEqual(graph.get_version(objects[0].version_id).geometry.lower,400)

    def test_m12_12_exact_units(self):
        instrument=sealed()[4].instrument; v=CASES['M12-12']['fixture_vector']
        values=tuple(Fraction(x) for x in v['tick_values']); points=tuple(ticks_to_points(x,instrument) for x in values)
        self.assertEqual(points,tuple(Fraction(x) for x in v['expected_points']))
        self.assertEqual(points,literal.points(values,Fraction(1,4)))
        self.assertEqual(tuple(points_to_ticks(x,instrument) for x in points),values)
        with self.assertRaises(ContractError): ticks_to_points(400.0,instrument)

    def test_l02_01_e0_edge_ladder(self):
        _, result = edge_for('L02-01')
        values = tuple(l.geometry.lower for l in result.locations)
        self.assertEqual(values, (1150,1200,950,900))
        self.assertEqual(values, tuple(r[2] for r in literal.ladder(1000,1100,('1/2','1'))))
        self.assertEqual([len(result.at(t)) for t in (204,205)],[0,4])

    def test_l02_02_edge133_has_distinct_coordinate(self):
        _, result=edge_for('L02-02')
        self.assertEqual(tuple(l.geometry.lower for l in result.locations),(1233,867))
        self.assertEqual(Fraction(1233-1000,100),Fraction(233,100))
        self.assertNotEqual(result.locations[0].geometry.lower,1133)
        self.assertEqual(literal.ladder(1000,1100,('133/100',))[0][2],1233)

    def test_l02_03_reflected_region_bounds(self):
        _, result=edge_for('L02-03',regions=True)
        bounds=tuple((l.geometry.lower,l.geometry.upper) for l in result.locations)
        self.assertEqual(bounds,((1233,1266),(834,867)))
        self.assertEqual(bounds,literal.regions(1000,1100,('133/100','83/50')))

    def test_l02_04_flat_rejects_only_dependent_extensions(self):
        v=CASES['L02-04']['fixture_vector']; cfg,e,req,bar,p,clocks=sealed({'events':v['variants'][0]['events']})
        result=edge_extensions(p,clocks=clocks,horizon_end=300)
        self.assertEqual((result.status,len(result.locations)),('unavailable_zero_width',0))
        independent=native_ref(120,instrument=p.instrument,known=203)
        self.assertEqual(independent.value_at(205),120)
        with self.assertRaises(ContractError):
            edge_extensions(replace(p,high_ticks=100,low_ticks=101),clocks=clocks,horizon_end=300)
        self.assertEqual(literal.ladder(100,100,('1/2',)),())
        with self.assertRaises(ValueError): literal.ladder(101,100,('1/2',))

    def test_l02_05_fractional_contact_geometry(self):
        _, result=edge_for('L02-05'); upper,lower=result.locations
        self.assertEqual((upper.geometry.lower,lower.geometry.lower),(Fraction(809,2),Fraction(797,2)))
        self.assertEqual((upper.geometry.contact_lower,upper.geometry.contact_upper),(Fraction(807,2),Fraction(811,2)))
        self.assertEqual((lower.geometry.contact_lower,lower.geometry.contact_upper),(Fraction(795,2),Fraction(799,2)))
        self.assertEqual(tuple(l.geometry.lower for l in result.locations),tuple(r[2] for r in literal.ladder(400,403,('1/2',))))

    def test_l02_06_rounding_does_not_merge_source_births(self):
        _,result=edge_for('L02-06'); upper=result.locations[:2]
        self.assertEqual(tuple(l.geometry.lower for l in upper),(Fraction(1204,3),Fraction(2007,5)))
        self.assertEqual([round(l.geometry.lower) for l in upper],[401,401])
        members=object_members(result,links=primitive_registry_links(result.primitive))
        objects=[m.member for m in members if isinstance(m.member,ObjectRevision)]
        self.assertEqual(len({o.object_id for o in objects}),4)
        self.assertEqual(len({o.object_id for o in objects if o.roles==('upper_edge_extension',)}),2)

    def test_l02_07_explicit_publication_and_expiry(self):
        _,result=edge_for('L02-07'); vector=CASES['L02-07']['fixture_vector']
        self.assertEqual([None if not result.at(t) else result.at(t)[0].geometry.lower for t in vector['query_cuts']],vector['expected_upper_values'])

    def test_l02_08_late_correction_preserves_candidate_cut(self):
        bundle,result=edge_for('L02-08'); cfg,e,request,bar,p,clocks=bundle
        with tempfile.TemporaryDirectory() as d:
            graph=graph_for(Path(d)/'graph.sqlite'); receipt,links,objects=publish_result(graph,result)
            frozen=graph.freeze_candidates(cut_id='cut:230',at=230,instrument=p.instrument,expected_head=graph.head)
            correction=CASES['L02-08']['fixture_vector']['corrections'][0]
            e.correct(id=correction['id'],original_id=correction['original_id'],known_at=correction['known_at'],
                      reason='explicit fixture correction',replacement=make_trade(correction['replacement'],e.domain))
            new_bar=e.publish_window(e.capture(237),request,published_at=238)
            new=primitive_from_shared_bar(selection=p.selection,engine=e,publication_version_id=new_bar.version_id,cut=238)
            revised=edge_extensions(new,ratios=(Fraction(1,2),),clocks=publication_clocks(238,240,238),horizon_end=300)
            new_links=primitive_registry_links(new,previous=links)
            _,_,revisions=publish_result(graph,revised,batch='batch:revision',sequence=graph.sequence+1,links=new_links,previous=objects)
            self.assertEqual(revised.locations[0].geometry.lower,1153)
            self.assertEqual(graph.candidate_cut('cut:230'),frozen)
            self.assertEqual(graph.get_version(objects[0].version_id).geometry.lower,1150)
            self.assertEqual(revisions[0].supersedes,objects[0].version_id)
            self.assertEqual(new.supersedes,bar.version_id)
            self.assertEqual([graph.object_asof(objects[0].object_id,t).object.geometry.lower for t in (230,239,240)], [1150,1150,1153])
            self.assertEqual(graph.object_asof(objects[0].object_id,240).born_at,205)
            self.assertEqual(graph.active_set(300),())
            source2 = SharedBarEngine.restore(e.checkpoint())
            shutil.copyfile(Path(d)/'graph.sqlite',Path(d)/'restored.sqlite')
            graph2 = ObjectGraph.restore(Path(d)/'restored.sqlite',definition=graph.definition,checkpoint=graph.checkpoint())
            p2 = primitive_from_shared_bar(selection=p.selection,engine=source2,publication_version_id=new_bar.version_id,cut=238)
            reopened = edge_extensions(p2,ratios=(Fraction(1,2),),clocks=revised.clocks,horizon_end=300)
            self.assertEqual(reopened.version,revised.version)
            for at in (230,239,240,300):
                self.assertEqual(graph2.object_asof(objects[0].object_id,at),graph.object_asof(objects[0].object_id,at))

    def test_l02_09_gap_cross_is_not_contact(self):
        vector=CASES['L02-09']['fixture_vector']; events=vector['events']
        target=ObjectTarget('l02-gap','object:zone',210,230,Band(Fraction(109),Fraction(111)),1,Fraction(3),Fraction(3),'native_trade_ticks')
        result=reference_object_label(target,initial=Fraction(108),
            points=tuple(ExactPoint(r['event_at'],r['sequence'],Fraction(r['price_ticks']),r['known_at']) for r in events[1:]),
            coverage=ObservationWindow(210,230,231,(),True,'coverage:complete'))
        self.assertEqual(result['gap_crossings'],(212,)); self.assertEqual(result['reach_status'],'no_contact')
        self.assertEqual(literal.contacts([(r['id'],r['price_ticks']) for r in events],109,111),((),('after',)))

    def test_l02_10_contact_is_not_a_reversal_probability(self):
        events=CASES['L02-10']['fixture_vector']['events']
        target=ObjectTarget('l02-touch','object:zone',210,230,Band(Fraction(109),Fraction(111)),1,Fraction(3),Fraction(3),'native_trade_ticks')
        result=reference_object_label(target,initial=Fraction(108),
            points=tuple(ExactPoint(r['event_at'],r['sequence'],Fraction(r['price_ticks']),r['known_at']) for r in events[1:]),
            coverage=ObservationWindow(210,230,231,(),True,'coverage:complete'))
        self.assertEqual((result['contact_at'],result['departure']),(212,'favorable_first'))
        self.assertEqual(literal.contacts([(r['id'],r['price_ticks']) for r in events],109,111)[0],('touch',))
        self.assertNotIn('reversal_probability',result)

    def test_l02_11_no_reach_and_censor_keep_both_targets(self):
        target=ObjectTarget('l02-noreach','object:120',210,230,Band(Fraction(119),Fraction(121)),1,Fraction(3),Fraction(3),'native_trade_ticks')
        answers=[]
        for v in CASES['L02-11']['fixture_vector']['variants']:
            first,*rest=v['events']
            result=reference_object_label(target,initial=Fraction(first['price_ticks']),
                points=tuple(ExactPoint(r['event_at'],r['sequence'],Fraction(r['price_ticks']),r['known_at']) for r in rest),
                coverage=ObservationWindow(210,v['coverage_end'],232,(),True,'coverage:'+v['name']))
            answers.append(result)
        self.assertEqual([r['reach_status'] for r in answers],['no_contact','censored'])
        self.assertEqual(len(answers),2); self.assertEqual(answers[0]['target_version'],answers[1]['target_version'])

    def test_l03_01_prior_outer_and_current_inner(self):
        values=[]; identities=[]; v=CASES['L03-01']['fixture_vector']
        calendar=Calendar()
        prior=sealed({'events':v['prior']['events'],'calendar':{'close_at':200}},calendar=calendar)[4]
        next_day=prior.selection.session.trading_date+timedelta(days=1)
        current=sealed({'formation':v['current']['interval'], 'events':v['current']['events'],
            'calendar':{'trading_date':next_day.isoformat(),'session_id':'fixture-current-inner','open_at':210,'close_at':240},
            'coverage':{'interval':[210,240],'observed':[[210,240]],'known_at':241},
            'watermark':{'event_through':240,'known_at':241},
            'bar_publication':{'observation_cut':242,'published_at':243},
            'derivation':{'cut':243,'known_at':245}},calendar=calendar)[4]
        selection=select_prior_session(calendar=calendar,current_date=next_day,
            instrument_root=prior.selection.session.instrument_root,cut=243)
        for semantic,p in (('prior_RTH',prior),('current_range',current)):
            binding=dict(prior_selection=selection,current_instrument=current.instrument) if semantic=='prior_RTH' else {}
            result=prior_locations(p,clocks=publication_clocks(243,245,243),horizon_end=300,
                                   fields=('high','low'),semantic=semantic,**binding)
            values.extend(l.geometry.lower for l in result.locations)
            identities.extend(m.member.object_id for m in object_members(result,links=primitive_registry_links(p)) if isinstance(m.member,ObjectRevision))
        self.assertEqual(values,[450,380,420,400]); self.assertEqual(len(set(identities)),4)

    def test_l03_02_separate_rth_and_eth_freshness(self):
        _,_,_,_,p,clocks=sealed({'calendar':{'close_at':200},
            'events':[{'id':'rth-low','event_at':100,'known_at':101,'price_ticks':380,'sequence':1},
                      {'id':'rth-high','event_at':199,'known_at':200,'price_ticks':450,'sequence':2}]})
        ref=session_references(p,clocks=clocks,horizon_end=300).field('high')
        vector=CASES['L03-02']['fixture_vector']
        for events,cuts in ((vector['events'],vector['query_cuts']),
                            (vector['ordered_return_variant']['events'],vector['ordered_return_variant']['query_cuts'])):
            rows=tuple(ReferenceObservation(r['id'],p.instrument,r['event_at'],r['known_at'],r['sequence'],Fraction(r['price_ticks']),
                                            'ETH' if r['event_at']<240 else 'RTH','native-fixture-v1') for r in events)
            for cut in cuts:
                faithful=reference_freshness(ref,rows,cut=cut,side=1,interpretation='RTH_only')
                full=reference_freshness(ref,rows,cut=cut,side=1,interpretation='full_session')
                raw=[(r.id,r.at,r.known_at,r.price_ticks,r.session) for r in rows]
                self.assertEqual((faithful.contact_event_ids,faithful.breach_event_ids,faithful.return_event_ids),literal.freshness(raw,450,cut,rth_only=True))
                self.assertEqual((full.contact_event_ids,full.breach_event_ids,full.return_event_ids),literal.freshness(raw,450,cut))
                self.assertEqual(faithful.touched,cut>=251); self.assertFalse(faithful.breached)
                self.assertTrue(full.breached); self.assertIsNone(full.role_probability)
                self.assertEqual(full.returned,any(r.id=='ETH_return' and r.known_at<=cut for r in rows))
                self.assertEqual(full.reference_version,faithful.reference_version)
        self.assertEqual(ref.value_at(251),450)
        with tempfile.TemporaryDirectory() as d:
            graph=graph_for(Path(d)/'freshness.sqlite')
            choice=prior_choice(p,cut=clocks.decision_cut,current_start=240,current_end=300)
            location=prior_locations(p,clocks=clocks,horizon_end=300,fields=('high',),
                prior_selection=choice,current_instrument=p.instrument)
            _,_,objects=publish_result(graph,location)
            source=EvidenceVersion('s:rth-retest','e:rth-retest',0,None,250,251,Support.OBSERVED,p.instrument,
                content_hash(vector['events'][1]))
            visit=ObservationEvent('obs:rth-retest',objects[0].version_id,'visit:rth-retest',ObservationKind.ENTER,
                250,251,(source.version_id,),'actual observed RTH contact')
            graph.commit_batch(AtomicBatch('batch:rth-retest',graph.sequence+1,graph.definition.version,
                publication_clocks(251,251,251),(source,visit),2),expected_head=graph.head)
            self.assertEqual([len(graph.active_set(t)) for t in vector['query_cuts']],vector['expected_object_count'])
            self.assertEqual(graph.get_version(visit.event_id),visit)
            self.assertEqual(graph.get_version(objects[0].version_id).geometry.lower,450)

    def test_l03_03_range_values_do_not_require_profile(self):
        pairs=[]; count=0
        for row in CASES['L03-03']['fixture_vector']['range_rows']:
            start,end=row['interval']
            override={'formation':[start,end],'events':row['events'],
                      'calendar':{'known_at':0,'open_at':start,'close_at':end},
                      'coverage':{'interval':[start,end],'observed':[[start,end]]}}
            _,_,_,_,p,clocks=sealed(override)
            binding={} if row['source']=='full_session' else dict(prior_selection=prior_choice(p,cut=clocks.decision_cut),current_instrument=p.instrument)
            result=prior_locations(p,clocks=clocks,horizon_end=300,fields=('high','low'),
                semantic='full_session' if row['source']=='full_session' else 'prior_RTH',**binding)
            pairs.append(tuple(l.geometry.lower for l in result.locations)); count+=len(result.locations)
        self.assertEqual(pairs,[(450,380),(460,370)]); self.assertEqual(count,4)
        self.assertEqual(CASES['L03-03']['fixture_vector']['profiles'],[])

    def test_l03_04_prior_revision_keeps_old_geometry_binding(self):
        v=CASES['L03-04']['fixture_vector']; cfg,e,request,bar,p,clocks=sealed(merged(v['override'],{'calendar':{'close_at':200}}))
        choice=prior_choice(p,cut=clocks.decision_cut)
        result=prior_locations(p,clocks=clocks,horizon_end=300,fields=('high',),prior_selection=choice,current_instrument=p.instrument)
        with tempfile.TemporaryDirectory() as d:
            graph=graph_for(Path(d)/'prior.sqlite'); _,links,objects=publish_result(graph,result)
            frozen=graph.freeze_candidates(cut_id='cut:prior230',at=230,instrument=p.instrument,expected_head=graph.head)
            target=graph.bind_target(target_id='target:prior450',cut_id=frozen['id'],object_version=objects[0].version_id,
                geometry=objects[0].geometry,horizon_end=300,observation_process='native_trade_ticks',expected_head=graph.head)
            c=v['correction']; e.correct(id=c['id'],original_id=c['original_id'],known_at=c['known_at'],reason='prior correction',replacement=make_trade(c['replacement'],e.domain))
            bar2=e.publish_window(e.capture(242),request,published_at=243)
            p2=primitive_from_shared_bar(selection=p.selection,engine=e,publication_version_id=bar2.version_id,cut=243)
            result2=prior_locations(p2,clocks=publication_clocks(243,245,243),horizon_end=300,fields=('high',),
                prior_selection=choice,current_instrument=p.instrument)
            _,_,objects2=publish_result(graph,result2,batch='batch:prior-revision',sequence=graph.sequence+1,
                                        links=primitive_registry_links(p2,previous=links),previous=objects)
            self.assertEqual((objects[0].geometry.lower,objects2[0].geometry.lower),(450,452))
            self.assertEqual(graph.candidate_cut('cut:prior230'),frozen)
            self.assertEqual(graph.get_version(objects[0].version_id).geometry.lower,450)
            self.assertEqual([graph.object_asof(objects[0].object_id,t).object.geometry.lower for t in v['query_cuts']],v['expected_highs'])
            self.assertEqual(graph.target(target['id']),target)
            self.assertEqual(graph.target(target['id'])['geometry_hash'],objects[0].geometry.version)
            source2=SharedBarEngine.restore(e.checkpoint())
            shutil.copyfile(Path(d)/'prior.sqlite',Path(d)/'prior-restored.sqlite')
            restored=ObjectGraph.restore(Path(d)/'prior-restored.sqlite',definition=graph.definition,checkpoint=graph.checkpoint())
            actual=primitive_from_shared_bar(selection=p.selection,engine=source2,publication_version_id=bar2.version_id,cut=243)
            self.assertEqual(actual,p2)
            self.assertEqual(restored.target(target['id']),target)
            for t in v['query_cuts']:
                self.assertEqual(restored.object_asof(objects[0].object_id,t),graph.object_asof(objects[0].object_id,t))

    def test_cl_01_actual_thirteen_source_union(self):
        with tempfile.TemporaryDirectory() as d:
            bundle=e0_bundle(Path(d)/'e0.sqlite')
            graph,results,primitives,links,clocks,instrument,engines=bundle
            objects,members=e0_members(results,links)
            expected=CASES['CL-01']['fixture_vector']['expected_counts_by_price']
            self.assertEqual(len(objects),13); self.assertEqual(len({o.object_id for o in objects}),13)
            self.assertEqual(Counter(str(o.geometry.lower) for o in objects),Counter(expected))
            actual_rows=source_rows(results)
            expected_rows=CASES['CL-01']['fixture_vector']['expected_source_identity_price_rows']
            frozen=Counter((source,role,None if ratio is None else Fraction(ratio),Fraction(price)) for source,role,ratio,price in expected_rows)
            self.assertEqual(Counter(actual_rows),frozen)
            self.assertEqual(Counter(actual_rows),Counter(literal.e0_sources((410,420,400,412),(420,440,390,410))))
            receipt=publish_range_batch(graph=graph,primitives=primitives,registry_links=links,derived_members=members,
                batch_id='batch:E0-fixture',batch_sequence=1,clocks=clocks,expected_head=graph.head)
            self.assertTrue(receipt.changed)
            cut=graph.freeze_candidates(cut_id='cut:E0-fixture',at=clocks.known_at,instrument=instrument,expected_head=graph.head)
            self.assertEqual(cut['candidate_count'],13)
            METRICS['CL-01']={'source_objects':13,'graph_stats':dict(graph.stats),'consumer_work':[r.work for r in results]}

    def test_cl_02_fourteenth_candidate_rejects_before_commit(self):
        with tempfile.TemporaryDirectory() as d:
            graph,results,primitives,links,clocks,instrument,engines=e0_bundle(Path(d)/'cap.sqlite')
            before=graph.head
            groups=tuple(r.locations for r in results)
            extra=Location('extra_grid',(),line_geometry(primitives[0],price=Fraction(450),
                tolerance=Fraction(1),definition='def:extra-grid-450'),('high','low'))
            self.assertNotIn(extra,tuple(value for group in groups for value in group))
            with self.assertRaises(ContractError):
                require_candidate_capacity(groups+((extra,),),candidate_cap=13)
            self.assertEqual(graph.head,before); self.assertEqual(graph.sequence,0)
            self.assertEqual(len(require_candidate_capacity(groups,candidate_cap=13)),13)

    def test_cl_03_display_and_future_suffix_preserve_identity(self):
        from trading_research.location.internal_ranges import internal_locations
        vector=CASES['CL-03']['fixture_vector']; identities=[]; counts=[]
        with tempfile.TemporaryDirectory() as d:
            for index,variant in enumerate(vector['variants']):
                graph,results,primitives,links,clocks,instrument,engines=e0_bundle(Path(d)/('variant'+str(index)+'.sqlite'))
                original,_=e0_members(results,links)
                for row in variant['extra_events']:
                    engines[0].add(make_trade(row,engines[0].domain))
                recertified=tuple(primitive_from_shared_bar(selection=p.selection,engine=e,
                    publication_version_id=p.publication_version_id,cut=clocks.decision_cut)
                    for p,e in zip(primitives,engines))
                self.assertEqual([p.record() for p in recertified],[p.record() for p in primitives])
                horizon=results[0].horizon_end
                regenerated=(internal_locations(recertified[0],clocks=clocks,horizon_end=horizon),
                    edge_extensions(recertified[0],clocks=clocks,horizon_end=horizon),
                    prior_locations(recertified[1],clocks=clocks,horizon_end=horizon,
                        prior_selection=results[2]._recipe[2]['prior_selection'],current_instrument=instrument))
                objects,members=e0_members(regenerated,links)
                self.assertEqual(objects,original)
                publish_range_batch(graph=graph,primitives=recertified,registry_links=links,derived_members=members,
                    batch_id='batch:display-source',batch_sequence=1,clocks=clocks,expected_head=None)
                if variant['display_enabled']:
                    presentation=Presentation('view:fixture',objects[0].object_id,clocks.known_at,
                        'preset:v1','universe:v1',color=variant['color'])
                    display_clocks=PublicationClock(clocks.known_at,clocks.known_at,clocks.known_at,
                        actual_completion_at=clocks.known_at)
                    graph.commit_batch(AtomicBatch('batch:presentation',graph.sequence+1,graph.definition.version,
                        display_clocks,(presentation,),1),expected_head=graph.head)
                active=graph.active_set(clocks.known_at)
                counts.append(len(active))
                identities.append(tuple((o.object_id,o.version_id,o.geometry) for o in objects))
                self.assertEqual(sorted(o.geometry.lower for o in active),vector['expected_sorted_prices'])
            self.assertEqual(counts,vector['expected_source_counts'])
            self.assertEqual([value==identities[0] for value in identities],vector['expected_same_source_identity_vectors'])

    def test_cl_04_actual_checkpoint_and_exact_retry(self):
        with tempfile.TemporaryDirectory() as d:
            graph,results,primitives,links,clocks,instrument,engines=e0_bundle(Path(d)/'original.sqlite')
            objects,members=e0_members(results,links)
            args=dict(primitives=primitives,registry_links=links,derived_members=members,
                      batch_id='batch:E0-fixture',batch_sequence=1,clocks=clocks)
            first=publish_range_batch(graph=graph,expected_head=graph.head,**args)
            retry=publish_range_batch(graph=graph,expected_head=graph.head,**args)
            self.assertTrue(first.changed); self.assertFalse(retry.changed)
            checkpoint=graph.checkpoint()
            with sqlite3.connect(Path(d)/'original.sqlite') as source, sqlite3.connect(Path(d)/'restored.sqlite') as destination:
                source.backup(destination)
            restored=ObjectGraph.restore(Path(d)/'restored.sqlite',definition=graph.definition,checkpoint=checkpoint)
            engines2=tuple(SharedBarEngine.restore(e.checkpoint()) for e in engines)
            primitives2=tuple(primitive_from_shared_bar(selection=p.selection,engine=e,publication_version_id=p.publication_version_id,
                                                        cut=clocks.decision_cut) for p,e in zip(primitives,engines2))
            links2=tuple(primitive_registry_links(p) for p in primitives2)
            self.assertEqual([l.record() for l in links2],[l.record() for l in links])
            retried=publish_range_batch(graph=restored,expected_head=restored.head,**{**args,'primitives':primitives2,'registry_links':links2})
            self.assertFalse(retried.changed)
            for g in (graph,restored):
                past=g.freeze_candidates(cut_id='cut:before',at=clocks.known_at-1,instrument=instrument,expected_head=g.head)
                now=g.freeze_candidates(cut_id='cut:now',at=clocks.known_at,instrument=instrument,expected_head=g.head)
                self.assertEqual(past['candidate_count'],0); self.assertEqual(now['candidate_count'],13)
            self.assertEqual(graph.candidate_cut('cut:now'),restored.candidate_cut('cut:now'))

    def test_cl_05_bad_clock_domain_and_forged_source_reject(self):
        from trading_research.context.range_adapter import DerivedRangeMember
        cfg,e,request,bar,p,clocks=sealed()
        with tempfile.TemporaryDirectory() as d:
            graph=graph_for(Path(d)/'invalid.sqlite'); before=graph.head
            with self.assertRaises((ContractError,DependencyUnavailable)):
                edge_extensions(p,clocks=publication_clocks(202,205,202),horizon_end=300)
            with self.assertRaises(ContractError):
                edge_extensions(p,clocks=publication_clocks(203,202,203),horizon_end=300)
            with self.assertRaises((ContractError,DependencyUnavailable)):
                wrong=replace(p.selection,instrument=replace(p.instrument,raw_id='102'))
                primitive_from_shared_bar(selection=wrong,engine=e,publication_version_id=bar.version_id,cut=203)
            with self.assertRaises(ContractError):
                edge_extensions(replace(p),clocks=clocks,horizon_end=300)
            with self.assertRaises(ContractError):
                edge_extensions(p,clocks=clocks,horizon_end=205)
            result=edge_extensions(p,clocks=clocks,horizon_end=300)
            links=primitive_registry_links(p)
            first=result.locations[0]
            numeric=replace(result,locations=(replace(first,geometry=replace(first.geometry,lower=Fraction(999),upper=Fraction(999),
                contact_lower=Fraction(999),contact_upper=Fraction(999))),*result.locations[1:]))
            object.__setattr__(numeric,'_recipe',result._recipe)
            with self.assertRaises(ContractError):object_members(numeric,links=links)
            detached=replace(result)
            with self.assertRaises(ContractError):object_members(detached,links=links)
            rewritten=replace(result)
            object.__setattr__(rewritten,'_recipe',(result._recipe[0],result._recipe[1],
                {**result._recipe[2],'ratios':(Fraction(4),)},result._recipe[3]))
            with self.assertRaises(ContractError):object_members(rewritten,links=links)
            members=object_members(result,links=links)
            detached_member=replace(members[0])
            with self.assertRaises(ContractError):publish_range_batch(graph=graph,primitives=(p,),registry_links=(links,),
                derived_members=(detached_member,*members[1:]),batch_id='batch:detached',batch_sequence=1,clocks=clocks,expected_head=graph.head)
            later_horizon=edge_extensions(p,clocks=clocks,horizon_end=301)
            with self.assertRaises(ContractError):publish_result(graph,later_horizon)
            self.assertEqual(graph.head,before); self.assertEqual(graph.sequence,0)


def real_calendar():
    cfg=GOLD['fixtures']['real_ny_E0_calendar']; cal=Calendar(); tz=zone_version('America/New_York')
    instrument=Instrument('fixture','fixture_exchange','101','NQ-FIX','def:raw-v1',Fraction(1,4),
                          cfg['raw_lifetime'][0],cfg['raw_lifetime'][1],cfg['raw_lifetime'][1])
    sessions=[]
    for key in ('prior_RTH','current_RTH'):
        row=cfg[key]
        s=Session(row['id'],date.fromisoformat(row['date']),'NQ',*row['interval'],(),0,
                  cfg['calendar_known_at'],cfg['calendar_version'],tz,True,'explicit synthetic RTH')
        cal.append(s); sessions.append(s)
    for text in cfg['declared_non_RTH_dates']:
        day=date.fromisoformat(text); n=(day-sessions[0].trading_date).days
        opening=sessions[0].open_at+n*86400000000000
        cal.append(Session('noRTH:'+text,day,'NQ',opening,opening+1,(),0,cfg['calendar_known_at'],
                           cfg['calendar_version'],tz,False,'explicit synthetic no-RTH date'))
    return cal,instrument,sessions[1],sessions[0]


def real_primitive(calendar,instrument,session,events,*,current,cut):
    day=session.trading_date
    node=WallRule('current_06_09' if current else 'prior_RTH','M12-fixture',day,day,day,
                  '06:00' if current else '09:30','09:00' if current else '16:00',
                  'America/New_York','NY_06_09' if current else 'NY_RTH',session.timezone_version,
                  session.known_at,'wall-fixture-v1').compile()
    graph=IntervalGraph('M12-real-NY',(node,)); start,end=node.spans[0].start,node.spans[0].end
    selection=select_clock(calendar=calendar,interval_graph=graph,interval_name=node.name,trading_date=day,
                             instrument_root='NQ',instrument=instrument,cut=end+3)
    domain=BarDomain(instrument.raw_symbol,'registered-whole-print','registered-whole-print')
    definition=BarDefinition(domain,'real-NY-fixture-v1',graph.version,selection.clock_id)
    engine=SharedBarEngine(domain,(definition,),limits=BarLimits(128,8,4,32))
    engine.add_many(tuple(make_trade(r,domain) for r in events))
    request=WindowRequest(definition.id,start,end,WindowCoverage(domain.instrument,start,end,((start,end),),end+1,'cov:'+node.name),
                          Watermark(end,end+2,'wm:'+node.name))
    bar=engine.publish_window(engine.capture(end+2),request,published_at=end+3)
    p=primitive_from_shared_bar(selection=selection,engine=engine,publication_version_id=bar.version_id,cut=cut)
    return p,engine,request,bar


def e0_bundle(path):
    from trading_research.location.internal_ranges import internal_locations
    cal,instrument,current,prior=real_calendar(); vector=CASES['CL-01']['fixture_vector']; derivation=vector['derivation']
    p,e,_,_=real_primitive(cal,instrument,current,vector['current_events'],current=True,cut=derivation['cut'])
    pp,pe,_,_=real_primitive(cal,instrument,prior,vector['prior_events'],current=False,cut=derivation['cut'])
    clocks=publication_clocks(derivation['cut'],derivation['known_at'],derivation['cut'])
    selection=select_prior_session(calendar=cal,current_date=current.trading_date,instrument_root='NQ',cut=derivation['cut'])
    results=(internal_locations(p,clocks=clocks,horizon_end=derivation['horizon_end']),
             edge_extensions(p,clocks=clocks,horizon_end=derivation['horizon_end']),
             prior_locations(pp,clocks=clocks,horizon_end=derivation['horizon_end'],prior_selection=selection,current_instrument=instrument))
    definition=RegistryDefinition(id='def:E0-fixture',generator_versions=(('L01-internal-ranges-v1','v1'),
        ('L02-edge-extensions-v1','v1'),('L03-prior-session-v1','v1')),ttl_ns=derivation['horizon_end']-clocks.known_at,
        batch_members_max=128,hot_active_max=64,hot_relations_max=128)
    graph=ObjectGraph(path,definition=definition)
    return graph,results,(p,pp),(primitive_registry_links(p),primitive_registry_links(pp)),clocks,instrument,(e,pe)


def e0_members(results,links):
    require_candidate_capacity(tuple(r.locations for r in results),candidate_cap=13)
    members=tuple(m for r,l in zip(results,(links[0],links[0],links[1])) for m in object_members(r,links=l))
    return tuple(m.member for m in members if isinstance(m.member,ObjectRevision)),members


def source_rows(results):
    aliases={'range_high':('high',None),'range_low':('low',None),'range_eq':('EQ',Fraction(1,2)),
             'range_quarter25':('quarter',Fraction(1,4)),'range_quarter75':('quarter',Fraction(3,4))}
    rows=[]
    for result in results:
        for location in result.locations:
            if location.role in aliases:
                role,ratio=aliases[location.role]; source='current_06_09'
            elif location.role.startswith('prior_'):
                source,role,ratio='prior_RTH',location.role[6:],None
            else:
                source,role,ratio='current_06_09',location.role,location.ratios[0]
            rows.append((source,role,ratio,location.geometry.lower))
    return tuple(rows)
