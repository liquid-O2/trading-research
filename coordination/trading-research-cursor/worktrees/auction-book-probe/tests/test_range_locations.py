"""All 41 registered C01/L01 vectors; execution is owned by shared verifier."""
from dataclasses import replace
from datetime import date, datetime, time as civil_time, timedelta, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from references.range_locations_literal import (
    literal_comparators, literal_diagnostic, literal_e0, literal_horizon_status,
    literal_ohlc, literal_profile, literal_range, literal_relation, literal_sampled,
)
from trading_research.context.range_adapter import (
    DerivedRangeMember, primitive_from_shared_bar, primitive_registry_links,
    publish_range_batch, select_clock,
)
from trading_research.context.ranges import (
    GENERATOR as RANGE_GENERATOR, GENERATOR_DEFINITION as RANGE_GENERATOR_DEFINITION,
    PresetSnapshot, PriorScale, RangeArithmetic, RangeLimits, RangeRetention, SourceVariant,
    anchor_relation, dispersion, exact, historical_comparators, pool_source_probabilities,
    profile_comparators, range_definition, range_object_member, range_version, ratio,
    relate_ranges, unresolved_formula, validate_source_obligations,
)
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import Watermark, WindowCoverage
from trading_research.foundations.calendar import Calendar, Session
from trading_research.foundations.cash_calendar import zone_version
from trading_research.foundations.intervals import IntervalGraph, NamedInterval, Span, WallRule
from trading_research.foundations.multiresolution import BarDefinition, BarDomain, BarLimits, SharedBarEngine, WindowRequest, ResetMarker
from trading_research.foundations.object_graph import (
    ActionProposal, AtomicBatch, Eligibility, EvidenceVersion, Instrument, ObjectGraph,
    ObjectRevision, ObservationEvent, ObservationKind, Presentation, PublicationClock, RegistryDefinition, Support,
)
from trading_research.foundations.time import datetime_ns
from trading_research.foundations.units import Ticks
from trading_research.location.edge_extensions import edge_extensions, object_members, select_locations
from trading_research.measurements.reference_prices import select_prior_session
from trading_research.location.internal_ranges import (
    DiagnosticBinding, LocationProposal, ObservationWindow, bounded_offset,
    internal_locations, internal_room, observed_diagnostic, role_asof, role_probability,
    sampled_contacts, simultaneous_action_representatives, visit_reset_ticks,
)
from trading_research.location.prior_session import prior_locations
from trading_research.measurements.tape import Trade


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = ROOT / "tests/golden/c01_l01_engineering_v1.json"
GOLD = json.loads(GOLDEN_PATH.read_text())
CASES = {v["id"]: v for v in (*GOLD["fixtures"], *GOLD["extra_vectors"])}
NS = 1_000_000_000
ENGINEERING_METRICS = {}


def pair(value):
    return None if value is None else [Fraction(value).numerator, Fraction(value).denominator]


def ns(value):
    if type(value) is not int:
        raise ContractError("fixture requires exact integer seconds")
    return value * NS


def utc(text):
    return datetime_ns(datetime.fromisoformat(text.replace("Z", "+00:00")))


def clock(at, *, input_at=None, completion_at=None):
    inp = at if input_at is None else input_at
    completion = at if completion_at is None else completion_at
    return PublicationClock(at, inp, completion, actual_completion_at=completion)


_TEMPORARIES = []


def registry(path=None, *, ttl_ns=ns(1000)):
    if path is None:
        temporary = tempfile.TemporaryDirectory()
        _TEMPORARIES.append(temporary)
        path = Path(temporary.name) / 'registry.sqlite'
    definition = RegistryDefinition(id="def:c01-l01-test", generator_versions=(
        (RANGE_GENERATOR, RANGE_GENERATOR_DEFINITION), ("L01-internal-ranges-v1", "v1"),
        ("L02-edge-extensions-v1", "v1"), ("L03-prior-session-v1", "v1")),
        batch_members_max=128, parent_edges_max=32, hot_active_max=512, hot_relations_max=1024,
        ttl_ns=ttl_ns)
    return ObjectGraph(path, definition=definition)


def tearDownModule():
    for temporary in _TEMPORARIES:
        temporary.cleanup()
    _TEMPORARIES.clear()


class Formation:
    """Construct actual F03 named clocks, F09 publications and exact raw identity."""
    def __init__(self, start=0, end=10, *, origin=0, name="formation", instrument=None,
                 interval_graph=None, calendar=None, selection=None, limits=None, trading_date=None):
        self.origin, self.start, self.end = origin, start, end
        self.instrument = instrument or Instrument("fixture", "fixture-venue", "NQ-id", "NQ-fixture", "raw-v1", Fraction(1, 4))
        if selection is None:
            day = trading_date or datetime.fromtimestamp(origin // NS, timezone.utc).date()
            known = min(origin, origin+ns(start))
            node = NamedInterval(name, "C01-fixture", (Span(origin+ns(start), origin+ns(end)),),
                known, "explicit-fixture-v1", "UTC-fixture", "fixture-not-native-calendar", (day,))
            interval_graph = interval_graph or IntervalGraph("fixture-range-graph", (node,))
            session = Session("session-"+day.isoformat(), day, "NQ", origin+ns(start), origin+ns(end), (),
                0, known, "fixture-session-v1", "fixture-not-native-calendar", True, "synthetic-engineering-only")
            calendar = calendar or Calendar()
            calendar.append(session)
            selection = select_clock(calendar=calendar, interval_graph=interval_graph, interval_name=name,
                trading_date=day, instrument_root="NQ", instrument=self.instrument, cut=known)
        self.selection = selection
        self.domain = BarDomain(self.instrument.raw_symbol, "registered-whole-print", "registered-whole-print")
        self.definition = BarDefinition(self.domain, "registered-range-time-v1", selection.interval_graph.version, selection.clock_id)
        self.engine = SharedBarEngine(self.domain, (self.definition,), limits=limits or BarLimits(block_events=2))

    def trade(self, row):
        return Trade(row["id"], row.get("content", "content-"+row["id"]), self.domain.instrument,
            self.origin+ns(row["event_s"]), self.origin+ns(row["known_s"]),
            None if row.get("ticks") is None else Ticks(row["ticks"]), row.get("size", 1),
            row.get("side", 1), row.get("order", 1), self.domain.aggregation_unit, row.get("history_complete", True))

    def add(self, rows):
        self.engine.add_many(tuple(self.trade(row) for row in rows))

    def publish(self, *, cut, published=None, spans=None, coverage_known=None, watermark=True,
                watermark_known=None, coverage_version="coverage-v1", watermark_version="watermark-v1"):
        published = cut if published is None else published
        spans = ((self.start, self.end),) if spans is None else tuple(tuple(p) for p in spans)
        cov = WindowCoverage(self.domain.instrument, self.origin+ns(self.start), self.origin+ns(self.end),
            tuple((self.origin+ns(a), self.origin+ns(b)) for a, b in spans),
            self.origin+ns(cut if coverage_known is None else coverage_known), coverage_version)
        wm = None if watermark is False or watermark is None else Watermark(
            self.origin+ns(self.end if watermark is True else watermark),
            self.origin+ns(cut if watermark_known is None else watermark_known), watermark_version)
        request = WindowRequest(self.definition.id, self.origin+ns(self.start), self.origin+ns(self.end), cov, wm)
        return self.engine.publish_window(self.engine.capture(self.origin+ns(cut)), request,
                                         published_at=self.origin+ns(published))

    def primitive(self, bar, *, cut=None):
        return primitive_from_shared_bar(selection=self.selection, engine=self.engine,
            publication_version_id=bar.version_id, cut=bar.published_at if cut is None else self.origin+ns(cut))

    def version(self, bar, **kwargs):
        p = self.primitive(bar)
        return range_version(p, range_definition(self.selection), **kwargs)


def from_ohlc(values, *, start=0, end=10, name="formation", origin=0, instrument=None, calendar=None, trading_date=None):
    o, h, l, c = values
    f = Formation(start, end, name=name, origin=origin, instrument=instrument,
                  calendar=calendar, trading_date=trading_date)
    slots = (start, start+(end-start)//3, start+2*(end-start)//3, end-1)
    # Caller fixtures have >=4ns at integer-second scale; unique sequence is explicit.
    rows = [{"id": name+str(i), "event_s": at, "known_s": at, "ticks": price, "order": i}
            for i, (at, price) in enumerate(zip(slots, (o, h, l, c)))]
    f.add(rows)
    return f, f.publish(cut=end, published=end+1), rows


def eq_members(primitive, links, *, at=None, previous=(), horizon=None, parent_members=()):
    at = primitive.published_at if at is None else at
    horizon = at+ns(1000) if horizon is None else horizon
    result = internal_locations(primitive, clocks=clock(at), horizon_end=horizon)
    return object_members(select_locations(result, roles=('range_eq',)), links=links,
                          previous=previous, parent_members=parent_members)


def publish_eq(graph, primitive, *, links=None, previous_links=None, previous=(), at=None,
               batch_id=None, horizon=None):
    links = links or primitive_registry_links(primitive, previous=previous_links)
    at = primitive.published_at if at is None else at
    if horizon is None:
        born = at if not previous else graph.object_asof(previous[0].object_id, at).born_at
        horizon = born + graph.definition.ttl_ns
    members = eq_members(primitive, links, at=at, previous=previous, horizon=horizon)
    receipt = publish_range_batch(graph=graph, primitives=(primitive,), registry_links=(links,),
        derived_members=members, batch_id=batch_id or "batch:eq-"+str(graph.sequence+1),
        batch_sequence=graph.sequence+1, clocks=clock(at), expected_head=graph.head)
    obj = next(v.member for v in members if isinstance(v.member, ObjectRevision))
    return receipt, obj, members


class RangeLocationTests(unittest.TestCase):
    def assertPrimitiveLiteral(self, primitive, rows, start, end, cut):
        ref = literal_ohlc(rows, start=start, end=end, cut=cut)
        self.assertEqual(primitive.observed_ohlc, ref["ohlc"])
        self.assertEqual(primitive.source_event_ids, ref["ids"])
        return ref

    def test_cl_g01(self):
        g = CASES["CL-G01"]
        f, bar, rows = from_ohlc(g["input_vector"]["ohlc_ticks"])
        p = f.primitive(bar)
        r = f.version(bar).geometry
        ref = literal_range(p.ohlc)
        self.assertPrimitiveLiteral(p, rows, 0, 10, 10)
        expected = g["expected_literal"]
        actual = {"width": r.width, "quarter25": pair(r.coordinate(Fraction(1, 4))),
            "eq": pair(r.coordinate(Fraction(1, 2))), "quarter75": pair(r.coordinate(Fraction(3, 4))),
            "range_open": pair(r.open), "upper_edge_133": pair(r.extension("upper", Fraction(133, 100))),
            "lower_edge_133": pair(r.extension("lower", Fraction(133, 100))), "normalized_133": pair(r.coordinate(Fraction(133, 100)))}
        self.assertEqual(actual, {k: v for k, v in expected.items() if k != "input_ticks"})
        for k in actual:
            self.assertEqual(actual[k], ref[k] if k == "width" else pair(ref[k]))
        self.assertEqual(r.price_percent, Fraction(5, 6))
        scale = PriorScale("scale-prior", Fraction(25), -NS, 0, True)
        self.assertEqual(f.version(bar, prior_scale=scale).width_prior_volatility, Fraction(4))
        self.assertIsNone(f.version(bar, prior_scale=replace(scale, value_ticks=Fraction(0))).width_prior_volatility)
        self.assertIsNone(f.version(bar, prior_scale=replace(scale, published_at=bar.published_at+1)).width_prior_volatility)

    def test_cl_g02(self):
        g = CASES["CL-G02"]
        bull = g["input_vector"]["bull_ohlc_ticks"]
        bear = g["input_vector"]["bear_ohlc_ticks"]
        a, b = RangeArithmetic(bull[2], bull[1], bull[0], bull[3]), RangeArithmetic(bear[2], bear[1], bear[0], bear[3])
        actual = {"wick_quarter25": pair(a.coordinate(Fraction(1, 4))),
            "bull_body_source25": pair(a.body25()), "bull_session_body_lower25": pair(a.session_body_lower25()),
            "bear_body_source25": pair(b.body25())}
        self.assertEqual(actual, g["expected_literal"])
        self.assertEqual(a.body25(), literal_range(bull)["source_body25"])
        self.assertEqual(b.body25(), literal_range(bear)["source_body25"])
        self.assertNotEqual(a.body25(), a.session_body_lower25())

    def test_cl_g03(self):
        f, bar, _ = from_ohlc(CASES["CL-G03"]["input_vector"]["ohlc_ticks"])
        p, v = f.primitive(bar), f.version(bar)
        self.assertEqual(v.width_ticks, CASES["CL-G03"]["expected_literal"]["width"])
        self.assertFalse(v.usable_e0)
        self.assertEqual(v.internal, ())
        self.assertIsNone(v.geometry.normalized_position(100))
        self.assertEqual(v.geometry.coordinate(Fraction(1, 4)), literal_range(p.ohlc)["quarter25"])
        self.assertEqual(internal_locations(p, clocks=clock(p.published_at), horizon_end=p.published_at+NS).locations, ())
        self.assertEqual(edge_extensions(p, clocks=clock(p.published_at), horizon_end=p.published_at+NS).locations, ())

    def test_cl_t01(self):
        g = CASES["CL-T01"]
        inp, expected = g["input_vector"], g["expected_literal"]
        f = Formation(0, 10800, origin=utc(inp["clock"]["origin"]))
        f.add(inp["trades"])
        bar = f.publish(cut=inp["observation_cut_s"], published=inp["publication_s"],
            spans=inp["coverage"]["spans_s"], coverage_known=inp["coverage"]["known_s"],
            watermark_known=inp["watermark"]["known_s"])
        p = f.primitive(bar)
        self.assertPrimitiveLiteral(p, inp["trades"], 0, 10800, inp["observation_cut_s"])
        self.assertEqual(list(p.source_event_ids), expected["included_trade_ids"])
        self.assertEqual([row["id"] for row in inp["trades"] if row["id"] not in p.source_event_ids], expected["excluded_trade_ids"])
        self.assertEqual(list(p.ohlc), expected["ohlc_ticks"])
        self.assertEqual([bar.available(f.origin+ns(t)) for t in inp["query_cuts_s"]], expected["final_available_at_cuts"])
        self.assertEqual((p.minimum_known_at-f.origin)//NS, expected["minimum_known_s"])
        self.assertEqual((p.published_at-f.origin)//NS, expected["published_s"])
        self.assertEqual(p.width_ticks, expected["width_ticks"])
        self.assertEqual(pair(f.version(bar).geometry.coordinate(Fraction(1, 2))), expected["eq"])
        for t in inp["query_cuts_s"][:-1]:
            with self.assertRaises(DependencyUnavailable):
                f.primitive(bar, cut=t)

    def test_cl_t02(self):
        g = CASES["CL-T02"]
        inp = g["input_vector"]
        f = Formation(0, 900, origin=utc(inp["clock"]["origin"]))
        f.add(inp["trades"][:2])
        request = inp["requests"][0]
        b0 = f.publish(cut=request["cut_s"], published=request["published_s"], spans=request["coverage_spans_s"], watermark=False)
        p0, r0 = f.primitive(b0), f.version(b0)
        self.assertPrimitiveLiteral(p0, inp["trades"][:2], 0, 900, request["cut_s"])
        expected0 = g["expected_literal"]["versions"][0]
        self.assertEqual(list(p0.observed_ohlc), expected0["ohlc_ticks"])
        self.assertEqual(r0.observed_width_ticks, expected0["width_ticks"])
        self.assertEqual(pair(r0.diagnostic_geometry.coordinate(Fraction(1, 2))), expected0["eq"])
        self.assertEqual(p0.status, expected0["status"])
        self.assertEqual((p0.published_at-f.origin)//NS, expected0["known_s"])
        graph = registry()
        links0 = primitive_registry_links(p0)
        member0 = range_object_member(r0, links0, known_at=p0.published_at)
        publish_range_batch(graph=graph, primitives=(p0,), registry_links=(links0,), derived_members=(member0,),
            batch_id="batch:forming", batch_sequence=1, clocks=clock(p0.published_at), expected_head=None, range_retention=RangeRetention())
        self.assertEqual(graph.active_set(p0.published_at), ())
        binding = DiagnosticBinding("forming-label", r0.version_id, r0.diagnostic_geometry.coordinate(Fraction(1, 2)),
            f.origin+ns(inp["label_binding"]["bound_s"]), f.origin+ns(1000))
        f.add(inp["trades"][2:])
        request = inp["requests"][1]
        b1 = f.publish(cut=request["cut_s"], published=request["published_s"], spans=request["coverage_spans_s"],
                       watermark_known=request["watermark_known_s"])
        p1, r1 = f.primitive(b1), f.version(b1)
        expected1 = g["expected_literal"]["versions"][1]
        self.assertEqual(list(p1.ohlc), expected1["ohlc_ticks"])
        self.assertEqual(r1.width_ticks, expected1["width_ticks"])
        self.assertEqual(pair(r1.geometry.coordinate(Fraction(1, 2))), expected1["eq"])
        self.assertEqual((p1.published_at-f.origin)//NS, expected1["known_s"])
        self.assertTrue(r1.usable_e0)
        self.assertFalse(r0.usable_e0)
        self.assertEqual(pair(binding.coordinate), g["expected_literal"]["old_label_geometry"])
        self.assertEqual(graph.get_version(member0.member.version_id), member0.member)
        self.assertEqual(p1.supersedes, b0.version_id)
        self.assertFalse(b1.available(f.origin))

    def test_cl_t03(self):
        g = CASES["CL-T03"]
        inp, exp = g["input_vector"], g["expected_literal"]
        f = Formation(*inp["clock_interval_s"])
        f.add(inp["trades"])
        bar = f.publish(cut=inp["watermark"]["known_s"], published=inp["publication_s"],
            spans=inp["coverage"]["spans_s"], coverage_known=inp["coverage"]["known_s"])
        p, r = f.primitive(bar), f.version(bar)
        self.assertPrimitiveLiteral(p, inp["trades"], 0, 10800, 10801)
        self.assertEqual(list(p.observed_ohlc), exp["observed_ohlc_ticks"])
        self.assertEqual(r.observed_width_ticks, exp["observed_width_ticks"])
        self.assertEqual(p.observed_duration//NS, exp["coverage_duration_s"])
        self.assertEqual(exp["field_support"], dict.fromkeys(('open', 'high', 'low', 'close'), 'partial'))
        # Retained clarification separates whole-window fidelity from endpoint support.
        self.assertEqual({s.field: s.status for s in p.field_support},
                         {'open': 'partial', 'high': 'partial', 'low': 'partial', 'close': 'observed'})
        self.assertEqual(p.close_ticks, 180)
        self.assertFalse(p.coverage_complete)
        self.assertFalse(p.supports("high", "low"))
        self.assertEqual(len(internal_locations(p, clocks=clock(p.published_at), horizon_end=p.published_at+NS).locations), exp["eligible_e0_range_candidates"])
        self.assertNotIn(220, p.observed_ohlc)
        self.assertIsNone(p.open_ticks)
        self.assertEqual(p.support("open").reason, "incomplete_open")

    def test_cl_t04(self):
        g = CASES["CL-T04"]
        inp, exp = g["input_vector"], g["expected_literal"]
        f = Formation(*inp["clock_interval_s"])
        f.add(inp["trades"])
        b = f.publish(cut=inp["watermark"]["known_s"], published=inp["publication_s"], spans=inp["coverage"]["spans_s"], coverage_known=inp["coverage"]["known_s"])
        p = f.primitive(b)
        self.assertPrimitiveLiteral(p, inp["trades"], 0, 10800, 10801)
        self.assertEqual(list(p.observed_ohlc), exp["observed_ohlc_ticks"])
        self.assertEqual(p.observed_duration//NS, exp["coverage_duration_s"])
        self.assertEqual(10800-p.observed_duration//NS, exp["missing_duration_s"])
        self.assertTrue(b.final)
        self.assertFalse(p.coverage_complete)
        self.assertIsNone(p.close_ticks)
        self.assertEqual(p.observed_ohlc[3], exp["observed_last_ticks"])
        self.assertFalse(p.supports("high", "low"))
        self.assertEqual(len(internal_locations(p, clocks=clock(p.published_at), horizon_end=p.published_at+NS).locations), exp["eligible_e0_range_candidates"])

    def test_cl_t05(self):
        g = CASES["CL-T05"]
        inp, exp = g["input_vector"], g["expected_literal"]
        f = Formation(*inp["clock_interval_s"])
        f.add(inp["initial_trades"])
        request = inp["initial_final"]
        b0 = f.publish(cut=request["cut_s"], published=request["published_s"],
            spans=request["coverage_spans_s"], coverage_version=request["coverage_version"],
            watermark_known=request["watermark_known_s"])
        p0 = f.primitive(b0)
        horizon = ns(12000)
        graph = registry(ttl_ns=horizon-p0.published_at)
        receipt0, object0, _ = publish_eq(graph, p0, horizon=horizon)
        cut = graph.freeze_candidates(cut_id="cut:before-late", at=ns(inp["target_binding"]["bound_s"]),
            instrument=f.instrument, expected_head=graph.head)
        target = graph.bind_target(target_id="target:before-late", cut_id=cut["id"], object_version=object0.version_id,
            geometry=object0.geometry, horizon_end=horizon, observation_process="synthetic-observations", expected_head=graph.head)
        before = graph.get_version(object0.version_id)
        source_checkpoint = f.engine.checkpoint()
        f.add((inp["late_admission"],))
        request = inp["corrected_final"]
        b1 = f.publish(cut=request["cut_s"], published=request["published_s"],
            spans=request["coverage_spans_s"], coverage_version=request["coverage_version"],
            watermark_known=request["watermark_known_s"], watermark_version="wm-late")
        p1 = f.primitive(b1)
        receipt1, object1, _ = publish_eq(graph, p1, previous_links=receipt0.registry_links[0],
            previous=(object0,), horizon=horizon)
        for row in exp["asof"]:
            bar = f.engine.asof(bar_id=b0.bar_id, cut=ns(row["cut_s"]))
            self.assertEqual(bar.revision, row["revision"])
            self.assertEqual(list(bar.summary.open_ticks for _ in (0,)) + [bar.summary.high_ticks, bar.summary.low_ticks, bar.summary.close_ticks], row["ohlc_ticks"])
            view = graph.object_asof(object0.object_id, ns(row["cut_s"]))
            self.assertEqual(pair(view.object.geometry.lower), row["eq"])
        self.assertEqual(pair(before.geometry.lower), exp["target_birth_eq"])
        self.assertEqual(graph.target(target["id"])["geometry_hash"], object0.geometry.version)
        self.assertEqual(graph.get_version(object0.version_id), before)
        self.assertEqual(object1.supersedes, object0.version_id)
        self.assertIn(inp["late_admission"]["id"], p1.source_event_ids)
        self.assertEqual(p1.supersedes, b0.version_id)
        prefix = SharedBarEngine.restore(source_checkpoint)
        self.assertEqual(prefix.asof(bar_id=b0.bar_id, cut=ns(10860)).version_id, b0.version_id)
        self.assertEqual(tuple(cut["candidate_versions"]), (object0.version_id,))
        self.assertEqual(receipt1.registry_links[0].registry_revision, 1)

    def test_cl_t06(self):
        g = CASES["CL-T06"]
        actual, durations, selections = [], [], []
        for row in g["input_vector"]["windows"]:
            start = datetime.fromisoformat(row["local_start"])
            end = datetime.fromisoformat(row["local_end"])
            zone = "Etc/GMT+5" if row["zone"] == "fixed-05:00" else row["zone"]
            day = date.fromisoformat(row.get("declared_trading_date", start.date().isoformat()))
            rule = WallRule(row["id"], "source-clock-fixture", day, start.date(), end.date(),
                start.time().replace(tzinfo=None).isoformat(), end.time().replace(tzinfo=None).isoformat(), zone,
                row["zone"], zone_version(zone), utc("2024-01-01T00:00:00Z")-ns(86400*400), "clock-source-v1")
            node = rule.compile()
            graph = IntervalGraph("clock-fixture", (node,))
            session = Session("session-"+day.isoformat(), day, "NQ", node.spans[0].start+ns(36000),
                node.spans[0].start+ns(59400), (), 0, rule.known_at, "declared-calendar-v1", rule.timezone_version,
                True, "fixture-not-native-CME")
            calendar = Calendar()
            calendar.append(session)
            instrument = Instrument("fixture", "fixture", "NQ", "NQ-fixture", "v1", Fraction(1, 4))
            selection = select_clock(calendar=calendar, interval_graph=graph, interval_name=node.name,
                trading_date=day, instrument_root="NQ", instrument=instrument, cut=rule.known_at)
            selections.append(selection)
            actual.append([datetime.fromtimestamp(t//NS, timezone.utc).isoformat().replace("+00:00", "Z")
                           for t in (selection.formation_start, selection.formation_end)])
            durations.append((selection.formation_end-selection.formation_start)//NS)
            self.assertEqual(selection.named_interval.version, node.version)
            self.assertEqual(selection.interval_graph.version, graph.version)
            self.assertLess(selection.formation_end, selection.session.open_at)  # No RTH containment requirement.
        exp = g["expected_literal"]
        self.assertEqual(actual, exp["utc_windows"])
        self.assertEqual(durations, exp["durations_s"])
        self.assertFalse(selections[3].window.contains(utc(g["input_vector"]["endpoint_tick_utc"])))
        self.assertEqual(selections[3].window.trading_date.isoformat(), exp["overnight_trading_date"])
        self.assertNotEqual(selections[1].clock_id, selections[2].clock_id)

    def test_cl_t07(self):
        g = CASES["CL-T07"]
        records = g["input_vector"]["source_definition_records"]
        variants = tuple(SourceVariant.from_record(r) for r in records)
        exp = g["expected_literal"]
        self.assertEqual(len({v.version for v in variants}), exp["distinct_definition_count"])
        self.assertEqual(sum(v.resolved for v in variants), exp["resolved_source_window_count"])
        self.assertEqual(sum(v.status == "unresolved_start" for v in variants), exp["unresolved_london_count"])
        for variant in variants[2:]:
            with self.assertRaises(DependencyUnavailable):
                variant.formation()
        self.assertEqual([v.formation() for v in variants[:2]], [("06:00", "09:00"), ("09:30", "10:00")])
        opens = g["input_vector"]["named_open_prints"]
        self.assertEqual(opens[0]["ticks"], exp["nine_open_ticks"])
        self.assertEqual(opens[1]["ticks"], exp["nine_thirty_open_ticks"])
        self.assertNotEqual(opens[0]["clock_open"], opens[1]["clock_open"])
        self.assertTrue(all(dict(v.parameters).get("start_local") is None for v in variants[2:4]))

    def test_cl_t08(self):
        g = CASES["CL-T08"]
        inp, exp = g["input_vector"], g["expected_literal"]
        cal = inp["calendar_fixture"]
        day = date.fromisoformat(cal["date"])
        rule = WallRule(cal["id"], "declared-early-close", day, day, day, cal["start_local"], cal["end_local"],
            cal["zone"], cal["zone"], zone_version(cal["zone"]), utc(cal["known_at"]), "fixture-only-v1")
        node = rule.compile()
        start, end = node.spans[0].start, node.spans[0].end
        self.assertEqual([datetime.fromtimestamp(t//NS, timezone.utc).isoformat().replace("+00:00", "Z") for t in (start, end)], exp["declared_early_utc_interval"])
        calendar = Calendar()
        calendar.append(Session("early-session", day, "NQ", start, end, (), 0, rule.known_at,
            "explicit-early-fixture", rule.timezone_version, True, "fixture-not-native-CME"))
        instrument = Instrument("fixture", "fixture", "NQ", "NQ-fixture", "v1", Fraction(1, 4))
        selected = select_clock(calendar=calendar, interval_graph=IntervalGraph("early", (node,)), interval_name=node.name,
            trading_date=day, instrument_root="NQ", instrument=instrument, cut=rule.known_at)
        f = Formation(0, 12600, origin=start, instrument=instrument, selection=selected)
        rows = [{"id": "early"+str(i), "event_s": r["seconds_after0930"], "known_s": r["seconds_after0930"], "ticks": r["ticks"]}
                for i, r in enumerate(inp["eligible_trades"])]
        f.add(rows)
        bar = f.publish(cut=12600, published=12601)
        p, r = f.primitive(bar), f.version(bar)
        self.assertPrimitiveLiteral(p, rows, 0, 12600, 12600)
        self.assertEqual(list(p.ohlc), exp["early_ohlc_ticks"])
        self.assertEqual(r.width_ticks, exp["early_width_ticks"])
        self.assertEqual(pair(r.geometry.coordinate(Fraction(1, 2))), exp["early_eq"])
        self.assertEqual(pair(r.geometry.coordinate(Fraction(1, 4))), exp["early_quarter25"])
        self.assertEqual(pair(r.geometry.coordinate(Fraction(3, 4))), exp["early_quarter75"])
        regular = Formation(0, 23400, origin=start, name="requested-regular", instrument=instrument)
        regular.add(rows)
        rb = regular.publish(cut=23400, published=23401, spans=((0, 12600),))
        rp = regular.primitive(rb)
        self.assertTrue(p.coverage_complete)
        self.assertFalse(rp.coverage_complete)
        self.assertFalse(regular.version(rb).usable_e0)
        self.assertEqual((rp.formation_end-rp.formation_start-rp.observed_duration)//NS, exp["regular_missing_duration_s"])
        self.assertEqual(rp.source_event_ids, p.source_event_ids)
        self.assertFalse(cal["historical_CME_certificate"])

    def test_cl_r01(self):
        g = CASES["CL-R01"]
        inp, exp = g["input_vector"], g["expected_literal"]
        versions = []
        for name in ("A", "B"):
            row = inp[name]
            f, b, _ = from_ohlc((row["low"], row["high"], row["low"], row["high"]),
                                start=row["formation_s"][0], end=row["formation_s"][1], name=name)
            versions.append(f.version(b))
        relation = relate_ranges(*versions, retention=RangeRetention())
        ref = literal_relation(inp["A"], inp["B"])
        self.assertEqual(relation.price_relation, exp["price_relation"])
        self.assertEqual(relation.time_relation, exp["time_relation"])
        self.assertEqual(pair(relation.relative_width), exp["relative_width"])
        self.assertEqual(tuple((a//NS, b//NS) for a, b in relation.shared_intervals), ref["shared"])
        self.assertEqual(tuple((a//NS, b//NS) for a, b in relation.left_unique_intervals), ref["a_unique"])
        self.assertEqual(versions[0].width_ticks, exp["a_width"])
        self.assertEqual(versions[1].width_ticks, exp["b_width"])
        self.assertFalse(relation.independent_confirmation)
        self.assertNotEqual(relation.left_version, relation.right_version)

    def test_cl_r02(self):
        inp = CASES["CL-R02"]["input_vector"]
        result = []
        for name in ("A", "B"):
            row = inp[name]
            f, b, _ = from_ohlc((row["low"], row["high"], row["low"], row["high"]),
                                start=row["formation_s"][0], end=row["formation_s"][1], name=name)
            result.append(f.version(b))
        relation = relate_ranges(*result, retention=RangeRetention())
        ref = literal_relation(inp["A"], inp["B"])
        self.assertEqual(relation.price_relation, CASES["CL-R02"]["expected_literal"]["price_relation"])
        self.assertEqual(relation.overlap_width, ref["overlap_width"])
        self.assertEqual(relation.shared_intervals, ())
        self.assertFalse(result[0].primitive.selection.window.contains(ns(100)))
        self.assertTrue(result[1].primitive.selection.window.contains(ns(100)))

    def test_cl_r03(self):
        g = CASES["CL-R03"]
        out = []
        for name, row in g["input_vector"].items():
            f, b, _ = from_ohlc(row["ohlc_ticks"], start=row["formation_s"][0], end=row["formation_s"][1], name=name)
            out.append(f.version(b))
        prior, current = out
        exp = g["expected_literal"]
        self.assertEqual(prior.width_ticks, exp["prior_width"])
        self.assertEqual(current.width_ticks, exp["formation_width"])
        self.assertEqual(pair(prior.geometry.coordinate(Fraction(1, 2))), exp["prior_eq"])
        self.assertEqual(pair(current.geometry.coordinate(Fraction(1, 2))), exp["formation_eq"])
        self.assertNotEqual(prior.id, current.id)
        self.assertNotEqual(prior.primitive.id, current.primitive.id)
        self.assertEqual(prior.geometry.extension("upper", Fraction(1, 2)), 270)
        self.assertEqual(current.geometry.extension("upper", Fraction(1, 2)), 250)

    def test_cl_l01(self):
        g = CASES["CL-L01"]
        fa, ba, _ = from_ohlc((150, 200, 100, 180), name="A")
        fb, bb, _ = from_ohlc((120, 190, 110, 170), name="B")
        pa, pb = fa.primitive(ba), fb.primitive(bb)
        la, lb = primitive_registry_links(pa), primitive_registry_links(pb)
        horizon = ns(100)
        a = internal_locations(pa, clocks=clock(pa.published_at), horizon_end=horizon, include_open=True)
        b = internal_locations(pb, clocks=clock(pb.published_at), horizon_end=horizon)
        a = select_locations(a, roles=('range_open', 'range_eq'))
        b = select_locations(b, roles=('range_eq',))
        members = object_members(a, links=la)+object_members(b, links=lb)
        graph = registry(ttl_ns=horizon-pa.published_at)
        publish_range_batch(graph=graph, primitives=(pa, pb), registry_links=(la, lb), derived_members=members,
            batch_id="batch:coincident", batch_sequence=1, clocks=clock(pa.published_at), expected_head=None)
        candidates = graph.active_set(pa.published_at)
        exp = g["expected_literal"]
        self.assertEqual(len(candidates), exp["source_identity_count"])
        self.assertEqual(len({o.geometry.lower for o in candidates}), exp["distinct_price_count"])
        self.assertEqual(len({o.object_id for o in candidates}), 3)
        self.assertEqual(len(graph.relations_asof(pa.published_at)), 3)
        selected = simultaneous_action_representatives(tuple((o.object_id, o.known_at, Fraction(0), o.geometry.lower) for o in candidates), policy=g["input_vector"]["policy"])
        self.assertEqual(len(selected), exp["maximum_simultaneous_economic_actions"])
        self.assertEqual(selected, simultaneous_action_representatives(tuple(reversed(tuple((o.object_id, o.known_at, Fraction(0), o.geometry.lower) for o in candidates))), policy=g["input_vector"]["policy"]))

    def test_cl_l02(self):
        g = CASES["CL-L02"]
        inp, exp = g["input_vector"], g["expected_literal"]
        proposal = LocationProposal("proposal", "range-v0", Fraction(150), inp["source_branch"], "long",
            ns(2), ns(2), "explicit-source-branch", ("DRF-U11",))
        self.assertEqual(proposal.role, exp["proposal_role"])
        self.assertEqual(proposal.edge_first_required, exp["edge_first_required"])
        self.assertEqual(proposal.gamma_required, exp["gamma_required"])
        self.assertEqual(proposal.response_required, exp["response_required"])
        self.assertTrue(proposal.available(ns(2)))
        self.assertIsNone(inp["gamma_feature"])
        self.assertIsNone(inp["Response_feature"])
        self.assertTrue(all(inp["range_ticks"][0] < v < inp["range_ticks"][1] for v in inp["observations"]))
        with self.assertRaises(DependencyUnavailable):
            role_probability(proposal)

    def test_cl_l03(self):
        g = CASES["CL-L03"]
        actual = []
        for row in g["input_vector"]["ranges"]:
            o, h, l, c = row["ohlc_ticks"]
            result = internal_room(RangeArithmetic(l, h, o, c), row["observed_price_ticks"], remaining_ns=ns(row["remaining_s"]))
            actual.append({"id": row["id"], "width_ticks": result["width_ticks"],
                **{k: pair(result[k]) for k in ("eq", "upper_edge_distance", "upper_half_extension", "upper_half_extension_distance")},
                "remaining_s": result["remaining_ns"]//NS})
            ref = literal_range(row["ohlc_ticks"])
            self.assertEqual(result["eq"], ref["eq"])
            self.assertEqual(result["upper_half_extension"], ref["upper_half"])
            self.assertIsNone(result["guaranteed_destination"])
            self.assertEqual(list(result["branches"]), g["expected_literal"]["retained_branch_catalog"])
        self.assertEqual(actual, g["expected_literal"]["rows"])
        with self.assertRaises(DependencyUnavailable):
            role_probability(g["input_vector"]["role_model_artifact"])

    def test_cl_l04(self):
        g = CASES["CL-L04"]
        inp, exp = g["input_vector"], g["expected_literal"]
        f = Formation(-10, 0)
        f.add(({"id": "first", "event_s": -10, "known_s": -10, "ticks": 100},
               {"id": "last", "event_s": -1, "known_s": -1, "ticks": 200}))
        p = f.primitive(f.publish(cut=0))
        graph = registry(ttl_ns=ns(5)-p.published_at)
        _, obj, _ = publish_eq(graph, p, horizon=ns(5))
        frozen = graph.freeze_candidates(cut_id="cut:diagnostic", at=ns(1), instrument=f.instrument, expected_head=graph.head)
        target = graph.bind_target(target_id="target:diagnostic", cut_id=frozen["id"], object_version=obj.version_id,
            geometry=obj.geometry, horizon_end=ns(5), observation_process="ordered-synthetic", expected_head=graph.head)
        bind = DiagnosticBinding("observed", obj.version_id, obj.geometry.lower, ns(1), ns(5))
        rows = tuple((ns(r["s"]), r["ticks"]) for r in inp["ordered_observations"])
        result = observed_diagnostic(bind, rows, upper_extension=250)
        ref = literal_diagnostic(rows, point=150, decision=ns(1), end=ns(5), extension=250)
        self.assertEqual(result["first_contact_at"]//NS, exp["first_eq_contact_s"])
        self.assertIsNone(result["upper_extension_contact_at"])
        self.assertEqual(result["maximum_after_contact"], exp["maximum_after_contact_ticks"])
        self.assertEqual(result["minimum_after_contact"], exp["minimum_after_contact_ticks"])
        self.assertEqual(result["first_contact_at"], ref["first"])
        self.assertEqual(result["maximum_after_contact"], ref["maximum"])
        self.assertEqual(result["minimum_after_contact"], ref["minimum"])
        self.assertEqual(graph.get_version(obj.version_id).geometry.lower, exp["source_object_geometry_ticks"])
        self.assertEqual(graph.target(target["id"])["geometry_hash"], obj.geometry.version)
        self.assertEqual(graph.active_set(ns(5)), ())

    def test_cl_l05(self):
        g = CASES["CL-L05"]
        inp, exp = g["input_vector"], g["expected_literal"]
        proposals = tuple(LocationProposal(r["id"], inp["range_version"], Fraction(inp["point_ticks"]), r["role"], r["side"],
            ns(r["known_s"]), ns(r["evidence_prefix_end_s"]), inp["role_proposal_policy"], ("UP-L01",))
            for r in inp["external_role_proposals"])
        for at, expected in ((2, exp["role_asof_s2"]), (5, exp["role_asof_s5"])):
            selected = role_asof(proposals, cut=ns(at), range_version=inp["range_version"], point_ticks=inp["point_ticks"])
            self.assertEqual({"id": selected.id, "side": selected.side, "role": selected.role}, expected)
        self.assertEqual([p.point_ticks for p in proposals], exp["point_ticks_before_after"])
        self.assertEqual([p.range_version for p in proposals], exp["range_version_before_after"])
        self.assertFalse(proposals[1].available(ns(2)))
        offset = inp["offset_proposal"]
        with self.assertRaises(DependencyUnavailable):
            bounded_offset(inp["point_ticks"], ratio(offset["offset_ticks"]), bound=ratio(offset["bound_ticks"]), training_artifact=offset["training_artifact"])
        self.assertEqual(proposals[0].point_ticks, 150)

    def test_cl_p01(self):
        g = CASES["CL-P01"]
        inp, exp = g["input_vector"], g["expected_literal"]
        geometry = RangeArithmetic(inp["range"]["low_ticks"], inp["range"]["high_ticks"])
        presets = tuple(PresetSnapshot(r["name"], r["applied_version"], ratio(r["upper_edge_ratio"]), r["reverse"], r["log"], r.get("color"), r.get("visible", True)) for r in inp["preset_records"])
        self.assertEqual(pair(presets[0].upper(geometry)), exp["p0_upper"])
        self.assertEqual(pair(presets[1].upper(geometry)), exp["p1_upper"])
        self.assertEqual(pair(presets[0].upper(geometry)), exp["p0_historical_upper_after_name_reuse"])
        self.assertEqual(pair(presets[2].upper(geometry)), exp["style_variant_upper"])
        self.assertEqual(presets[0].geometric_parameters, presets[2].geometric_parameters)
        self.assertEqual(presets[0].geometry_definition, presets[2].geometry_definition)
        self.assertNotEqual(presets[0].geometry_definition, presets[3].geometry_definition)
        self.assertNotEqual(presets[0].geometry_definition, presets[4].geometry_definition)
        for preset in presets[3:]:
            with self.assertRaises(DependencyUnavailable):
                preset.upper(geometry)
        self.assertEqual(presets[0].upper(geometry), literal_range((None, 200, 100, None))["upper_half"])

    def test_cl_s01(self):
        g = CASES["CL-S01"]
        inp, exp = g["input_vector"], g["expected_literal"]
        sessions = tuple((r["open"], r["high"]) for r in inp["historical_sessions"])
        result = historical_comparators(sessions, inp["current_open"], weights=tuple(inp["illustrative_weights"]))
        ref = literal_comparators(inp["historical_sessions"], inp["current_open"], inp["illustrative_weights"], inp["dispersion_observations"])
        for key in ref:
            actual = result[key] if key in result else dispersion(tuple(inp["dispersion_observations"]), population=key == "population_variance")
            self.assertEqual(actual, ref[key])
            self.assertEqual(pair(actual), exp[key])
        self.assertFalse(result["weighted_formula_is_claimed_vendor_definition"])
        for row in inp["source_formula_records"]:
            self.assertIsNone(row["formula"])
            with self.assertRaises(DependencyUnavailable):
                unresolved_formula(row["id"])
        trade = inp["large_trade_comparator"]
        flags = [row["size"] >= trade[row["session"]+"_threshold"] for row in trade["observations"]]
        self.assertEqual(flags, exp["large_trade_flags"])
        with self.assertRaises(DependencyUnavailable):
            unresolved_formula("absorption_from_size_alone")
        with self.assertRaises(DependencyUnavailable):
            pool_source_probabilities((inp["published_probability"],))

    def test_cl_s02(self):
        g = CASES["CL-S02"]
        populations = g["input_vector"]["source_populations"]
        exp = g["expected_literal"]
        displayed = Fraction(populations[0]["displayed_high_only_percent"])+Fraction(populations[0]["displayed_low_only_percent"])
        self.assertEqual(pair(displayed), exp["JXA24_displayed_single_break_sum_percent"])
        self.assertFalse(displayed > 74)
        self.assertEqual(len({p["id"] for p in populations}), exp["source_population_identity_count"])
        self.assertIn("tentative", populations[1]["digit_status"])
        self.assertTrue(any(len(values) > 1 for values in populations[1]["EQ_percent_candidate_readings"]))
        self.assertNotEqual(populations[2]["text_years"], populations[2]["other_JTR_text_years"])
        with self.assertRaises(DependencyUnavailable):
            pool_source_probabilities(tuple(populations))
        self.assertEqual(populations[0]["n"], 3249)
        self.assertEqual(populations[2]["n"], 4537)

    def test_cl_s03(self):
        g = CASES["CL-S03"]
        inp, exp = g["input_vector"], g["expected_literal"]
        p = inp["prior_profile"]
        result = profile_comparators(tuple(tuple(r) for r in p["histogram"]), low=p["low_ticks"], high=p["high_ticks"],
            open_price=inp["RTH_open_ticks"], val=p["VAL_ticks"], vah=p["VAH_ticks"])
        for key in ("range_open_class", "value_open_class", "MPOC", "MPOC_formula_status", "calibrated_touch_probability"):
            self.assertEqual(result[key], exp[key])
        for key in ("range_eq", "volume_POC", "expanded_trade_median", "VWAP"):
            self.assertEqual(pair(result[key]), exp[key])
        ref = literal_profile(p["histogram"])
        self.assertEqual(result["volume_POC"], ref["POC"])
        self.assertEqual(result["expanded_trade_median"], ref["median"])
        self.assertEqual(result["VWAP"], ref["VWAP"])
        missing_value = profile_comparators(tuple(tuple(r) for r in p["histogram"]), low=p["low_ticks"], high=p["high_ticks"], open_price=inp["RTH_open_ticks"])
        self.assertEqual(missing_value["value_open_class"], exp["missing_profile_value_class"])
        with self.assertRaises(DependencyUnavailable):
            profile_comparators((), low=100, high=200, open_price=120)

    def test_cl_e01(self):
        g = CASES["CL-E01"]
        inp, exp = g["input_vector"], g["expected_literal"]
        calendar = Calendar()
        fp, bp, _ = from_ohlc(inp["prior_rth_ohlc_ticks"], start=0, end=10, name="prior-RTH",
                            calendar=calendar, trading_date=date(1970, 1, 1))
        fc, bc, _ = from_ohlc(inp["six_nine_ohlc_ticks"], start=100, end=110, name="six-nine",
                            calendar=calendar, trading_date=date(1970, 1, 2))
        current, prior = fc.primitive(bc), fp.primitive(bp)
        clocks, horizon = clock(ns(111)), ns(300)
        internal = internal_locations(current, clocks=clocks, horizon_end=horizon)
        external = edge_extensions(current, clocks=clocks, horizon_end=horizon)
        selection = select_prior_session(calendar=calendar, current_date=date(1970, 1, 2),
                                         instrument_root='NQ', cut=clocks.decision_cut)
        previous = prior_locations(prior, clocks=clocks, horizon_end=horizon,
                                   prior_selection=selection, current_instrument=current.instrument)
        self.assertEqual(len(internal.locations), 5)
        self.assertEqual(len(external.locations), 4)
        self.assertEqual(len(previous.locations), 4)
        locations = internal.locations+external.locations+previous.locations
        self.assertEqual(len(locations), exp["source_object_count"])
        now_expected = [exp["six_nine"][k] for k in ("H", "L", "EQ", "Q25", "Q75")]
        self.assertEqual([pair(v.geometry.lower) for v in internal.locations], now_expected)
        self.assertCountEqual([pair(v.geometry.lower) for v in external.locations], [exp["six_nine"][k] for k in ("upper_half", "lower_half", "upper_one", "lower_one")])
        self.assertEqual({v.role: pair(v.geometry.lower) for v in previous.locations}, {"prior_high": exp["prior_rth"]["H"], "prior_low": exp["prior_rth"]["L"], "prior_open": exp["prior_rth"]["O"], "prior_close": exp["prior_rth"]["C"]})
        ref_current, ref_prior = literal_e0(inp["six_nine_ohlc_ticks"], inp["prior_rth_ohlc_ticks"])
        self.assertCountEqual([v.geometry.lower for v in internal.locations+external.locations], ref_current)
        self.assertCountEqual([v.geometry.lower for v in previous.locations], ref_prior)
        lc, lp = primitive_registry_links(current), primitive_registry_links(prior)
        members = object_members(internal, links=lc)+object_members(external, links=lc)+object_members(previous, links=lp)
        graph = registry(ttl_ns=horizon-clocks.known_at)
        receipt = publish_range_batch(graph=graph, primitives=(current, prior), registry_links=(lc, lp),
            derived_members=members, batch_id="batch:e0-thirteen", batch_sequence=1, clocks=clocks, expected_head=None)
        candidates = graph.freeze_candidates(cut_id="cut:e0-thirteen", at=clocks.known_at, instrument=fc.instrument, expected_head=graph.head)
        self.assertEqual(candidates["candidate_count"], exp["source_object_count"])
        self.assertEqual(len(set(receipt.object_versions)), 13)
        self.assertFalse(any(v.role == "range_open" for v in internal.locations))
        broader = internal_locations(current, clocks=clocks, horizon_end=horizon, include_open=True)
        self.assertEqual(len(broader.locations), 6)
        self.assertEqual(next(v.geometry.lower for v in broader.locations if v.role == "range_open"), 120)

    def test_cl_e02(self):
        g = CASES["CL-E02"]
        inp, exp = g["input_vector"], g["expected_literal"]
        window = ObservationWindow(ns(inp["decision_s"]), ns(inp["fixed_end_s"]))
        full = tuple((ns(a), ns(b)) for a, b in inp["complete_coverage_s"])
        partial = tuple((ns(a), ns(b)) for a, b in inp["incomplete_alternative_s"])
        self.assertEqual(window.end, ns(900))
        self.assertNotEqual(window.end, ns(inp["contact_s"]+inp["fixed_end_s"]))
        self.assertEqual(window.classify(contact_at=None, observed_intervals=full), exp["full_interval_no_contact"])
        self.assertEqual(window.classify(contact_at=None, observed_intervals=partial), exp["incomplete_until_1012"])
        self.assertEqual(window.classify(contact_at=ns(840), observed_intervals=full), literal_horizon_status(0, ns(900), full, ns(840)))
        self.assertEqual(window.classify(contact_at=None, observed_intervals=partial), literal_horizon_status(0, ns(900), partial, None))
        partition = ((ns(400), ns(900)), (0, ns(200)), (ns(200), ns(400)))
        self.assertEqual(window.classify(contact_at=None, observed_intervals=partition), exp['full_interval_no_contact'])
        self.assertEqual(window.classify(contact_at=None, observed_intervals=tuple(reversed(partition))), exp['full_interval_no_contact'])
        with self.assertRaises(ContractError):
            window.classify(contact_at=window.end, observed_intervals=full)

    def test_cl_e03(self):
        g = CASES["CL-E03"]
        inp, exp = g["input_vector"], g["expected_literal"]
        observations = tuple((ns(a), b) for a, b in inp["BBO_midpoint_observations"])
        grid = tuple(ns(t) for t in inp["decision_grid_s"])
        actual = sampled_contacts(grid, observations, point_ticks=inp["object_ticks"], tolerance_ticks=inp["contact_tolerance_ticks"])
        self.assertEqual(actual, ())
        self.assertEqual(actual, literal_sampled(grid, observations, 150, 1))
        self.assertEqual(sampled_contacts((ns(30),), observations, point_ticks=150, tolerance_ticks=1), (ns(30),))
        self.assertEqual(pair(visit_reset_ticks(inp["width_ticks"])), exp["visit_reset_ticks"])
        self.assertEqual(visit_reset_ticks(1), 4)

    def test_cl_e04(self):
        g = CASES["CL-E04"]
        inp, exp = g["input_vector"], g["expected_literal"]
        instruments = {r["id"]: Instrument("fixture", "fixture", r["id"], r["id"], "def-"+r["id"], Fraction(1, 4), ns(r["valid_s"][0]), ns(r["valid_s"][1])) for r in inp["instruments"]}
        sources = []
        for row in inp["prior_records"]:
            f, b, _ = from_ohlc(row["ohlc_ticks"], start=row["formation_s"][0], end=row["formation_s"][1], name="prior-"+row["instrument"], instrument=instruments[row["instrument"]])
            sources.append((f.primitive(b), f.version(b)))
        current_instrument = instruments[inp["current"]["instrument"]]
        accepted = [p for p, _ in sources if p.instrument == current_instrument and p.published_at <= ns(inp["current"]["cut_s"])]
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0].instrument.raw_symbol, exp["accepted_same_raw_prior_record_instrument"])
        self.assertEqual(list(accepted[0].ohlc), exp["accepted_prior_ohlc_ticks"])
        self.assertFalse(instruments["A"].valid(ns(1100)))
        with self.assertRaises(ContractError):
            relate_ranges(sources[0][1], sources[1][1], retention=RangeRetention())
        with self.assertRaises(DependencyUnavailable):
            prior_locations(sources[0][0], clocks=clock(ns(1100)), horizon_end=ns(1200))
        prior = accepted[0]
        calendar = prior.selection._calendar_receipt[1]
        current_day = prior.selection.session.trading_date + timedelta(days=1)
        calendar.append(Session('session-current-B', current_day, 'NQ', ns(1000), ns(1100), (), 0, 0,
                                'current-B-v1', 'fixture-not-native-calendar', True, 'explicit current session'))
        selection = select_prior_session(calendar=calendar, current_date=current_day, instrument_root='NQ', cut=ns(1100))
        self.assertEqual(len(prior_locations(prior, clocks=clock(ns(1100)), horizon_end=ns(1200),
            prior_selection=selection, current_instrument=current_instrument).locations), 4)
        self.assertGreater(ns(inp["mapping_request"]["known_s"]), ns(inp["current"]["cut_s"]))
        self.assertFalse(inp["mapping_request"]["supported_mapping_adapter"])

    def test_cl_x01_capabilities(self):
        exp = CASES["CL-X01-capabilities"]["expected"]
        rows = ({"id": "o1", "event_s": 0, "known_s": 0, "ticks": 120, "order": None},
                {"id": "o2", "event_s": 0, "known_s": 0, "ticks": 121, "order": None},
                {"id": "lo", "event_s": 1, "known_s": 1, "ticks": 100},
                {"id": "hi", "event_s": 2, "known_s": 2, "ticks": 200},
                {"id": "close", "event_s": 3, "known_s": 3, "ticks": 180})
        f = Formation(0, 4)
        f.add(rows)
        b = f.publish(cut=4, published=5)
        p = f.primitive(b)
        self.assertPrimitiveLiteral(p, rows, 0, 4, 4)
        self.assertEqual(p.supports("high", "low"), exp["HL_supported"])
        self.assertEqual(p.supports("open"), exp["O_supported"])
        self.assertEqual(p.supports("close"), exp["C_supported"])
        self.assertEqual(p.width_ticks, exp["width_ticks"])
        self.assertIsNone(p.price_percent)
        clocks, horizon = clock(p.published_at), ns(100)
        internal = internal_locations(p, clocks=clocks, horizon_end=horizon, include_open=True)
        external = edge_extensions(p, clocks=clocks, horizon_end=horizon)
        previous = prior_locations(p, clocks=clocks, horizon_end=horizon, semantic='current_range')
        self.assertEqual(len(internal.locations)+len(external.locations), exp["six_nine_E0_geometry_count"])
        self.assertFalse(any(l.role == "range_open" for l in internal.locations))
        self.assertEqual([l.role.split("_")[-1][0].upper() for l in previous.locations], exp["supported_prior_reference_kinds"])
        self.assertNotEqual(previous.status, "observed")
        graph = registry()
        links = primitive_registry_links(p)
        base = internal.locations[0]
        bad_location = replace(base, role="range_open", required_fields=("open",))
        bad_result = replace(internal, locations=(bad_location,))
        with self.assertRaises(ContractError):
            object_members(bad_result, links=links)
        self.assertEqual(graph.sequence, 0)
        missing = CASES["CL-X01-capabilities"]["additional_missing_open_vector"]
        fm = Formation(*missing["formation_s"])
        mr = tuple({"id": "missing"+str(i), **row} for i, row in enumerate((missing["first_observed_trade"], missing["last_observed_trade"])))
        fm.add(mr)
        pm = fm.primitive(fm.publish(cut=missing["watermark_known_s"], published=missing["publication_s"], spans=missing["observed_coverage_spans_s"]))
        self.assertIsNone(pm.open_ticks)
        self.assertEqual(pm.observed_ohlc[0], missing["expected"]["observed_first_ticks"])
        self.assertEqual(pm.support("open").reason, missing["expected"]["support_reason"])
        zero, zb, _ = from_ohlc((0, 2, -2, 1), name="zero-open")
        zp = zero.primitive(zb)
        self.assertTrue(zp.supports("high", "low"))
        self.assertIsNone(zp.price_percent)

    def test_cl_x02_interior_order(self):
        rows = ({"id": "open", "event_s": 0, "known_s": 0, "ticks": 120},
                {"id": "lo", "event_s": 1, "known_s": 1, "ticks": 100, "order": None},
                {"id": "hi", "event_s": 1, "known_s": 1, "ticks": 200, "order": None},
                {"id": "close", "event_s": 2, "known_s": 2, "ticks": 180})
        f = Formation(0, 3)
        f.add(rows)
        b = f.publish(cut=3, published=4)
        p = f.primitive(b)
        self.assertPrimitiveLiteral(p, rows, 0, 3, 3)
        exp = CASES["CL-X02-interior-order"]["expected"]
        self.assertEqual(list(p.ohlc), exp["OHLC_ticks"])
        self.assertTrue(p.supports("open", "high", "low", "close"))
        self.assertFalse(b.summary.order_exact)
        clocks, horizon = clock(p.published_at), ns(100)
        self.assertEqual(len(internal_locations(p, clocks=clocks, horizon_end=horizon).locations)+len(edge_extensions(p, clocks=clocks, horizon_end=horizon).locations), exp["six_nine_E0_geometry_count"])
        self.assertEqual(len(prior_locations(p, clocks=clocks, horizon_end=horizon, semantic='current_range').locations), exp["prior_reference_count"])
        before = dict(f.engine.work)
        retained, request = f.engine.window_publication(b.version_id)
        self.assertIs(retained, b)
        self.assertEqual(request.coverage.observed_intervals, ((0, ns(3)),))
        with self.assertRaises(AttributeError):
            request.start = ns(1)
        self.assertEqual(f.engine.work["window_publication_entries_examined"]-before.get("window_publication_entries_examined", 0), 1)
        self.assertEqual(f.engine.work["window_publication_index_lookups"]-before.get("window_publication_index_lookups", 0), 1)
        restored = SharedBarEngine.restore(f.engine.checkpoint())
        self.assertEqual(restored.window_publication(b.version_id)[1], request)
        self.assertIsNone(restored.window_publication_predecessor(b.version_id))
        # Lookup visits one entry even after multiple unrelated retained revisions.
        for index in range(5):
            f.publish(cut=4+index, published=5+index, coverage_version="coverage-repeat"+str(index))
        before = dict(f.engine.work)
        f.engine.window_publication(b.version_id)
        self.assertEqual(f.engine.work["window_publication_entries_examined"]-before["window_publication_entries_examined"], 1)
        ENGINEERING_METRICS["CL-X02"] = {"retained_publications": len(f.engine.publications),
            "single_lookup_entries": 1, "single_lookup_source_identities": len(b.summary.event_ids),
            "single_lookup_coverage_spans": len(request.coverage.observed_intervals),
            "checkpoint_bytes": len(f.engine.checkpoint()), "actual_F09_work": dict(f.engine.work)}

    def test_cl_x03_window_bound(self):
        inp, exp = CASES["CL-X03-window-bound"]["input"], CASES["CL-X03-window-bound"]["expected"]
        book = RangeRetention(RangeLimits(max_definitions=inp["max_definitions"]))
        for identity in inp["admitted_ids"]:
            book.admit_definition(identity, (identity, "exact-clock-v1"))
        before = book.state_hash
        with self.assertRaises(ContractError):
            book.admit_definition(inp["attempt"], (inp["attempt"], "exact-clock-v1"))
        self.assertEqual(list(book.definition_ids), exp["admitted_ids_after"])
        self.assertEqual(before, book.state_hash)
        self.assertEqual(book.work["versions_retained"], exp["publication_count_delta"])
        self.assertFalse(book.admit_definition(inp["admitted_ids"][0], (inp["admitted_ids"][0], "exact-clock-v1")))
        production = RangeRetention(RangeLimits(max_definitions=inp['max_definitions']))
        graph = registry()
        for index, identity in enumerate((*inp['admitted_ids'], inp['attempt'])):
            f,b,_ = from_ohlc((120,200,100,180), name=identity)
            primitive = f.primitive(b)
            value = range_version(primitive, range_definition(f.selection, id=identity))
            links = primitive_registry_links(primitive)
            member = range_object_member(value,links,known_at=value.known_at)
            args = dict(graph=graph,primitives=(primitive,),registry_links=(links,),derived_members=(member,),
                batch_id='batch:definition-'+str(index),batch_sequence=graph.sequence+1,
                clocks=clock(value.known_at),expected_head=graph.head,range_retention=production)
            if identity == inp['attempt']:
                state, checkpoint = production.state_hash, graph.checkpoint()
                with self.assertRaises(ContractError):
                    publish_range_batch(**args)
                self.assertEqual((production.state_hash,graph.checkpoint()),(state,checkpoint))
            else:
                publish_range_batch(**args)
        self.assertEqual(len(production.definition_ids),len(inp['admitted_ids']))

    def test_cl_x04_retention_bound(self):
        inp, exp = CASES["CL-X04-retention-bound"]["input"], CASES["CL-X04-retention-bound"]["expected"]
        f, b0, _ = from_ohlc((120, 200, 100, 180))
        versions = [f.version(b0)]
        for i, price in enumerate((220, 240)):
            f.add(({"id": "later"+str(i), "event_s": 9, "known_s": 20+i*10, "ticks": price, "order": 10+i},))
            versions.append(f.version(f.publish(cut=20+i*10, published=21+i*10, coverage_version="new"+str(i))))
        book = RangeRetention(RangeLimits(max_retained_range_versions=inp["max_retained_range_versions"]))
        for v in versions[:2]:
            book.retain_version(v)
        before = book.state_hash
        with self.assertRaises(ContractError):
            book.retain_version(versions[2])
        self.assertEqual(book.version_ids, tuple(v.version_id for v in versions[:2]))
        self.assertEqual(book.state_hash, before)
        self.assertEqual(book.work["silent_evictions"], exp["silent_eviction_count"])
        self.assertEqual(book.work["versions_retained"], len(exp["retained_versions_after"]))
        production = RangeRetention(RangeLimits(max_retained_range_versions=inp['max_retained_range_versions']))
        graph = registry(); links = None; previous = None
        for index,value in enumerate(versions):
            next_links = primitive_registry_links(value.primitive,previous=links)
            member = range_object_member(value,next_links,known_at=value.known_at,previous=previous)
            args = dict(graph=graph,primitives=(value.primitive,),registry_links=(next_links,),derived_members=(member,),
                batch_id='batch:range-version-'+str(index),batch_sequence=graph.sequence+1,
                clocks=clock(value.known_at),expected_head=graph.head,range_retention=production)
            if index == 2:
                state, checkpoint = production.state_hash, graph.checkpoint()
                with self.assertRaises(ContractError):
                    publish_range_batch(**args)
                self.assertEqual((production.state_hash,graph.checkpoint()),(state,checkpoint))
            else:
                publish_range_batch(**args)
                links, previous = next_links, member.member
        self.assertEqual(production.version_ids,tuple(v.version_id for v in versions[:2]))

    def test_cl_x05_atomic_batch(self):
        f, b0, _ = from_ohlc((120, 200, 100, 180))
        p0 = f.primitive(b0)
        links0 = primitive_registry_links(p0)
        range0 = range_object_member(f.version(b0), links0, known_at=p0.published_at)
        eq0 = next(v for v in eq_members(p0, links0, parent_members=(range0,)) if isinstance(v.member, ObjectRevision))
        graph = registry()
        retention = RangeRetention()
        publish_range_batch(graph=graph, primitives=(p0,), registry_links=(links0,), derived_members=(range0, eq0),
            batch_id="batch:atomic-base", batch_sequence=1, clocks=clock(p0.published_at), expected_head=None, range_retention=retention)
        frozen = graph.freeze_candidates(cut_id="cut:atomic-base", at=p0.published_at, instrument=f.instrument, expected_head=graph.head)
        head, seq, before = graph.head, graph.sequence, graph.checkpoint()
        before_retention = retention.state_hash
        f.add(({"id": "late", "event_s": 9, "known_s": 20, "ticks": 220, "order": 10},))
        b1 = f.publish(cut=20, published=21, coverage_version="cov-correction")
        p1 = f.primitive(b1)
        links1 = primitive_registry_links(p1, previous=links0)
        range1 = range_object_member(f.version(b1), links1, known_at=p1.published_at, previous=range0.member)
        eq1 = next(v for v in eq_members(p1, links1, previous=(eq0.member,), horizon=p0.published_at+ns(1000)) if isinstance(v.member, ObjectRevision))
        bad = DerivedRangeMember(replace(eq1.member, parent_versions=("v:missing-range",)), eq1.requirements)
        with self.assertRaises(ContractError):
            publish_range_batch(graph=graph, primitives=(p1,), registry_links=(links1,), derived_members=(range1, bad),
                batch_id="batch:atomic-rejected", batch_sequence=seq+1, clocks=clock(p1.published_at), expected_head=head, range_retention=retention)
        self.assertEqual(graph.head, head)
        self.assertEqual(graph.sequence, seq)
        self.assertEqual(graph.checkpoint(), before)
        self.assertEqual(retention.state_hash,before_retention)
        self.assertEqual(graph.candidate_cut(frozen["id"]), frozen)
        for vid in (links1.evidence_version_id, links1.anchor_version_id, range1.member.version_id, bad.member.version_id):
            with self.assertRaises(DependencyUnavailable):
                graph.get_version(vid)
        for vid in (links0.evidence_version_id, links0.anchor_version_id, range0.member.version_id, eq0.member.version_id):
            self.assertIsNotNone(graph.get_version(vid))

    def test_cl_x06_restart(self):
        g = CASES["CL-X06-restart"]
        inp, exp = g["input"], g["expected"]
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            f = Formation(*inp["formation_s"])
            f.add(inp["trades"])
            b0 = f.publish(cut=3, published=3)
            p0 = f.primitive(b0)
            horizon = ns(100)
            graph = registry(directory / "uninterrupted.sqlite", ttl_ns=horizon-p0.published_at)
            receipt0, obj0, _ = publish_eq(graph, p0, horizon=horizon)
            frozen = graph.freeze_candidates(cut_id="cut:restart-old", at=ns(3), instrument=f.instrument, expected_head=graph.head)
            target = graph.bind_target(target_id="target:restart-old", cut_id=frozen["id"], object_version=obj0.version_id,
                geometry=obj0.geometry, horizon_end=horizon, observation_process="synthetic", expected_head=graph.head)
            source_checkpoint, checkpoint = f.engine.checkpoint(), graph.checkpoint()
            shutil.copyfile(directory / "uninterrupted.sqlite", directory / "restored.sqlite")
            restored_graph = ObjectGraph.restore(directory / "restored.sqlite", definition=graph.definition, checkpoint=checkpoint)
            restored_engine = SharedBarEngine.restore(source_checkpoint)
            correction = inp["correction"]
            replacement = f.trade({"id": correction["replacement_id"], "event_s": correction["replacement_event_s"],
                "known_s": correction["replacement_known_s"], "ticks": correction["replacement_ticks"]})
            final = []
            for engine, current_graph in ((f.engine, graph), (restored_engine, restored_graph)):
                engine.correct(id=correction["id"], original_id=correction["target_id"], known_at=ns(correction["known_s"]), reason="fixture-price-correction", replacement=replacement)
                request = WindowRequest(f.definition.id, 0, ns(3), WindowCoverage(f.domain.instrument, 0, ns(3), ((0, ns(3)),), ns(4), "coverage-corrected"), Watermark(ns(3), ns(4), "wm-corrected"))
                bar = engine.publish_window(engine.capture(ns(4)), request, published_at=ns(inp["next_publication_s"]))
                primitive = primitive_from_shared_bar(selection=f.selection, engine=engine, publication_version_id=bar.version_id, cut=ns(5))
                receipt, obj, _ = publish_eq(current_graph, primitive, previous_links=receipt0.registry_links[0], previous=(obj0,), horizon=horizon)
                final.append((primitive, receipt, obj))
                self.assertEqual(primitive.supersedes, b0.version_id)
                self.assertEqual(engine.window_publication_predecessor(bar.version_id), b0.version_id)
                self.assertEqual(engine.window_publication(bar.version_id)[1], request)
                self.assertEqual(current_graph.object_asof(obj0.object_id, ns(3)).object.geometry.lower, Fraction(150))
                self.assertEqual(current_graph.target(target["id"])["geometry_hash"], obj0.geometry.version)
                self.assertEqual(list(primitive.correction_ids), exp["source_correction_ids"])
                self.assertEqual(current_graph.object_asof(obj0.object_id, ns(5)).object.geometry.lower, Fraction(160))
            self.assertEqual(final[0][0], final[1][0])
            self.assertEqual(final[0][2], final[1][2])
            self.assertEqual(graph.active_set(ns(5)), restored_graph.active_set(ns(5)))
            self.assertEqual(list(p0.ohlc), exp["asof_s3"]["ohlc_ticks"])
            self.assertEqual(list(final[0][0].ohlc), exp["asof_s5"]["ohlc_ticks"])
            self.assertEqual(final[0][0].revision, 1)
            # Distinct admissible admission chunks pass through the real common
            # writer both before and after the same source correction.
            n=len(inp['trades'])
            for number,boundaries in enumerate(((n,),tuple(range(1,n+1)))):
                chunked=Formation(*inp['formation_s'],selection=f.selection,instrument=f.instrument)
                start=0
                for stop in boundaries:
                    chunked.add(inp['trades'][start:stop]);start=stop
                initial_bar=chunked.publish(cut=3,published=3)
                initial_primitive=chunked.primitive(initial_bar)
                chunk_graph=registry(directory/('chunks-'+str(number)+'.sqlite'),ttl_ns=horizon-initial_primitive.published_at)
                initial_receipt,initial_object,_=publish_eq(chunk_graph,initial_primitive,horizon=horizon)
                self.assertEqual((initial_primitive.ohlc,initial_object.version_id),(p0.ohlc,obj0.version_id))
                chunked.engine=SharedBarEngine.restore(chunked.engine.checkpoint())
                chunked.engine.correct(id=correction['id'],original_id=correction['target_id'],known_at=ns(correction['known_s']),
                    reason='fixture-price-correction',replacement=replacement)
                revised_bar=chunked.engine.publish_window(chunked.engine.capture(ns(4)),request,published_at=ns(inp['next_publication_s']))
                revised_primitive=chunked.primitive(revised_bar)
                _,revised_object,_=publish_eq(chunk_graph,revised_primitive,previous_links=initial_receipt.registry_links[0],
                    previous=(initial_object,),horizon=horizon)
                self.assertEqual((revised_primitive.ohlc,revised_object.version_id),(final[0][0].ohlc,final[0][2].version_id))
                self.assertEqual([chunk_graph.object_asof(initial_object.object_id,ns(t)).object.geometry.lower for t in (3,5)],
                                 [Fraction(150),Fraction(160)])
            # Initial registry ordinal is independent of an already revised F09 stream.
            fresh_graph = registry(directory / "late-join.sqlite", ttl_ns=horizon-final[0][0].published_at)
            first_links = primitive_registry_links(final[0][0])
            self.assertEqual(first_links.registry_revision, 0)
            fresh, _, _ = publish_eq(fresh_graph, final[0][0], links=first_links, horizon=horizon)
            ev = fresh_graph.get_version(first_links.evidence_version_id)
            self.assertEqual(ev.revision, 0)
            self.assertEqual(final[0][0].revision, 1)
            self.assertTrue(fresh.changed)
            ENGINEERING_METRICS["CL-X06"] = {"events": f.engine.event_count,
                "source_publications": len(f.engine.publications), "source_checkpoint_bytes": len(source_checkpoint),
                "registry_checkpoint_bytes": len(json.dumps(checkpoint)),
                "registry_file_bytes": (directory / "uninterrupted.sqlite").stat().st_size,
                "source_work_including_adapter_reconstruction": dict(f.engine.work),
                "registry_work": dict(graph.stats),
                "fresh_paths_restored": 2, "market_tape_reads": 0}

    def test_cl_x07_malformed_scalar(self):
        variants = CASES["CL-X07-malformed-scalar"]["input_variants"]
        calls = (lambda: exact(variants[0]["value"]), lambda: Span(variants[1]["value"], ns(2)),
                 lambda: ratio(variants[2]["value"]), lambda: Span(*variants[3]["value"]))
        book = RangeRetention()
        original = book.state_hash
        for call in calls:
            with self.assertRaises(ContractError):
                call()
            self.assertEqual(book.state_hash, original)
        for bad in (1.0, float("nan"), float("inf")):
            with self.assertRaises(ContractError):
                exact(bad)

    def test_cl_x08_forged_or_wrong_bar(self):
        f, b, rows = from_ohlc((120, 200, 100, 180), end=60)
        p = f.primitive(b)
        forged_bar = replace(b)
        with self.assertRaises(ContractError):
            forged_bar.available(b.published_at)
        with self.assertRaises(ContractError):
            primitive_registry_links(replace(p))
        with self.assertRaises(DependencyUnavailable):
            primitive_from_shared_bar(selection=f.selection, engine=f.engine, publication_version_id="unretained-forged", cut=b.published_at)
        activity_definition = BarDefinition(f.domain, "events-v1", f.selection.interval_graph.version, f.selection.clock_id, "events", 5)
        activity = SharedBarEngine(f.domain, (activity_definition,))
        activity.add_many((f.trade({"id": "a", "event_s": 0, "known_s": 0, "ticks": 100}),
                           f.trade({"id": "b", "event_s": 2, "known_s": 2, "ticks": 200})))
        output = activity.publish_activity(activity.capture(ns(3)), activity_definition.id, published_at=ns(3),
            resets=(ResetMarker("reset", ns(3), ns(3), "next-epoch"),))
        partial = output.completed[0]
        self.assertEqual(partial.state, "reset_partial")
        with self.assertRaises(DependencyUnavailable):
            primitive_from_shared_bar(selection=f.selection, engine=activity, publication_version_id=partial.version_id, cut=ns(3))
        coarse, cb, _ = from_ohlc((120, 200, 100, 180), end=120)
        with self.assertRaises(ContractError):
            primitive_from_shared_bar(selection=f.selection, engine=coarse.engine, publication_version_id=cb.version_id, cut=cb.published_at)
        es = Instrument("fixture", "fixture", "ES", "ES", "ES-v1", Fraction(1, 4))
        wrong, wb, _ = from_ohlc((120, 200, 100, 180), end=60, instrument=es)
        with self.assertRaises(ContractError):
            primitive_from_shared_bar(selection=f.selection, engine=wrong.engine, publication_version_id=wb.version_id, cut=wb.published_at)
        self.assertEqual(p.source_event_ids, tuple(row["id"] for row in sorted(rows, key=lambda row: (row["event_s"], row["order"], row["id"]))))
        self.assertEqual(len(f.engine.publications), 1)
        self.assertIsNone(f.engine.window_publication_predecessor(b.version_id))
        separate_domain=replace(f.domain,measurement='reported_trade')
        separate_definition=replace(f.definition,domain=separate_domain)
        separate_engine=SharedBarEngine(separate_domain,(separate_definition,))
        separate_engine.add_many(tuple(f.trade(row) for row in rows))
        _,retained_request=f.engine.window_publication(b.version_id)
        separate_bar=separate_engine.publish_window(separate_engine.capture(ns(60)),replace(retained_request,definition_id=separate_definition.id),published_at=b.published_at)
        separate_primitive=primitive_from_shared_bar(selection=f.selection,engine=separate_engine,
            publication_version_id=separate_bar.version_id,cut=separate_bar.published_at)
        self.assertNotEqual(separate_domain.measurement,separate_domain.aggregation_unit)
        self.assertEqual(separate_primitive.ohlc,p.ohlc)
        links = primitive_registry_links(p)
        measured = f.version(b)
        with self.assertRaises(ContractError):
            range_object_member(replace(measured, geometry=RangeArithmetic(0, 999)), links, known_at=p.published_at)
        good = range_object_member(measured, links, known_at=p.published_at)
        graph = registry()
        with self.assertRaises(ContractError):
            publish_range_batch(graph=graph, primitives=(p,), registry_links=(links,),
                derived_members=(DerivedRangeMember(good.member, good.requirements),),
                batch_id='batch:detached-formula', batch_sequence=1, clocks=clock(p.published_at), expected_head=None)
        self.assertEqual(graph.sequence, 0)
        calendar = f.selection._calendar_receipt[1]
        late_selection = select_clock(calendar=calendar, interval_graph=f.selection.interval_graph,
            interval_name=f.selection.window.id, trading_date=f.selection.window.trading_date,
            instrument_root='NQ', instrument=f.instrument, cut=ns(65))
        late_primitive = primitive_from_shared_bar(selection=late_selection, engine=f.engine,
            publication_version_id=b.version_id, cut=ns(65))
        with self.assertRaises(DependencyUnavailable):
            range_version(late_primitive, range_definition(late_selection), cut=ns(64))
        self.assertEqual(range_version(late_primitive, range_definition(late_selection)).known_at, ns(65))
        # Same prints, newly known missing coverage: an initial old publication
        # may not activate at a later decision cut.
        rolled = f.publish(cut=66, published=67, spans=((1, 60),), coverage_version='cov-rollback')
        self.assertEqual(rolled.summary, b.summary)
        before = graph.checkpoint()
        with self.assertRaises(DependencyUnavailable):
            publish_eq(graph, p, at=ns(67))
        self.assertEqual(graph.checkpoint(), before)
        p1 = f.primitive(rolled)
        b2 = f.publish(cut=68, published=69, coverage_version='cov-restored')
        p2 = f.primitive(b2)
        with self.assertRaises(ContractError):
            primitive_registry_links(p2, previous=links)
        self.assertEqual(primitive_registry_links(p2, previous=primitive_registry_links(p1, previous=links)).registry_revision, 2)
        f.engine.correct(id='known-unpublished', original_id=rows[0]['id'], known_at=ns(70), reason='cancel')
        with self.assertRaises(DependencyUnavailable):
            publish_eq(graph, p2, at=ns(70))
        self.assertEqual(graph.checkpoint(), before)

    def test_cl_x09_duplicate_and_conflict(self):
        g = CASES["CL-X09-duplicate-and-conflict"]
        f, b, _ = from_ohlc(g["input"]["initial_OHLC"])
        p = f.primitive(b)
        links = primitive_registry_links(p)
        graph = registry()
        members = eq_members(p, links)
        args = dict(graph=graph, primitives=(p,), registry_links=(links,), derived_members=members,
            batch_id="batch:duplicate", batch_sequence=1, clocks=clock(p.published_at), expected_head=None)
        first = publish_range_batch(**args)
        head, sequence = graph.head, graph.sequence
        duplicate = publish_range_batch(**args)
        self.assertFalse(duplicate.changed)
        self.assertEqual(duplicate.committed_head, first.committed_head)
        self.assertEqual(graph.head, head)
        self.assertEqual(graph.sequence, sequence)
        obj = next(w for w in members if isinstance(w.member, ObjectRevision))
        original = obj.member
        changed_geometry = replace(original.geometry, lower=Fraction(160), upper=Fraction(160), contact_lower=Fraction(159), contact_upper=Fraction(161))
        bad = DerivedRangeMember(replace(original, geometry=changed_geometry), obj.requirements)
        changed_members = tuple(bad if w is obj else w for w in members)
        with self.assertRaises((ContractError, IntegrityError)):
            publish_range_batch(**{**args, "derived_members": changed_members})
        self.assertEqual(list(p.ohlc), g["expected"]["old_version_OHLC"])
        self.assertEqual(pair(graph.get_version(original.version_id).geometry.lower), g["expected"]["old_EQ"])
        self.assertEqual(graph.sequence-sequence, g["expected"]["identical_duplicate_new_versions"])
        self.assertEqual(primitive_registry_links(p, previous=links), links)

    def test_cl_x10_frozen_cut(self):
        g = CASES["CL-X10-frozen-cut"]
        at = g["input"]["range_r0_publication_s"]
        f, b, _ = from_ohlc((120, 200, 100, 180), end=at-1)
        p = f.primitive(b)
        graph = registry()
        receipt, original, _ = publish_eq(graph, p)
        frozen = graph.freeze_candidates(cut_id="cut:frozen", at=ns(g["input"]["frozen_candidate_cut_s"]), instrument=f.instrument, expected_head=graph.head)
        head = graph.head
        result = internal_locations(p, clocks=clock(ns(at)), horizon_end=p.published_at+graph.definition.ttl_ns)
        q25 = next(l for l in result.locations if l.role == "range_quarter25")
        members = object_members(select_locations(result, roles=('range_quarter25',)), links=receipt.registry_links[0])
        with self.assertRaises(ContractError):
            publish_range_batch(graph=graph, primitives=(p,), registry_links=receipt.registry_links, derived_members=members,
                batch_id="batch:retroactive", batch_sequence=graph.sequence+1, clocks=clock(ns(at)), expected_head=head)
        self.assertEqual(graph.head, head)
        self.assertEqual(graph.candidate_cut(frozen["id"]), frozen)
        self.assertEqual(tuple(frozen["candidate_versions"]), (original.version_id,))
        for member in members:
            if isinstance(member.member, ObjectRevision):
                with self.assertRaises(DependencyUnavailable):
                    graph.get_version(member.member.version_id)

    def test_cl_x11_fractional_point(self):
        g = CASES["CL-X11-fractional-point"]
        inp, exp = g["input"], g["expected"]
        f, b, _ = from_ohlc((100, inp["high_ticks"], inp["low_ticks"], 101))
        p = f.primitive(b)
        result = internal_locations(p, clocks=clock(p.published_at), horizon_end=ns(100))
        q25 = next(l for l in result.locations if l.role == "range_quarter25")
        self.assertEqual(pair(q25.geometry.lower), exp["raw_internal_point"])
        self.assertEqual(p.width_ticks, exp["raw_width_ticks"])
        self.assertEqual(q25.geometry.lower, literal_range(p.ohlc)["quarter25"])
        self.assertNotEqual(q25.geometry.lower, Fraction(round(q25.geometry.lower)))
        links = primitive_registry_links(p)
        members = object_members(select_locations(result, roles=('range_quarter25',)), links=links)
        graph = registry(ttl_ns=ns(100)-p.published_at)
        publish_range_batch(graph=graph, primitives=(p,), registry_links=(links,), derived_members=members,
            batch_id="batch:fractional", batch_sequence=1, clocks=clock(p.published_at), expected_head=None)
        obj = next(w.member for w in members if isinstance(w.member, ObjectRevision))
        before = graph.active_set(p.published_at)
        presentation = Presentation("view:rounding-display", obj.object_id, p.published_at+NS,
            "preset:display-only", "universe:synthetic", color="red")
        batch = AtomicBatch("batch:presentation", graph.sequence+1, graph.definition.version,
            clock(p.published_at+NS), (presentation,), 1)
        graph.commit_batch(batch, expected_head=graph.head)
        self.assertEqual(graph.active_set(p.published_at+NS), before)
        self.assertEqual(graph.get_version(obj.version_id).geometry, q25.geometry)

    def test_cl_x12_malformed_restore(self):
        f = Formation(0, 3)
        f.add(CASES["CL-X06-restart"]["input"]["trades"])
        b = f.publish(cut=3)
        payload = json.loads(f.engine.checkpoint())
        altered = json.loads(json.dumps(payload))
        altered["history"][-1]["published_at"] = ns(1)
        with self.assertRaises((ContractError, IntegrityError)):
            SharedBarEngine.restore(json.dumps(altered, sort_keys=True, separators=(",", ":")).encode())
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            graph = registry(directory / "good.sqlite", ttl_ns=ns(100)-b.published_at)
            _, obj, _ = publish_eq(graph, f.primitive(b), horizon=ns(100))
            checkpoint = graph.checkpoint()
            for kind in ("derived_EQ", "source_parent_version"):
                path = directory / (kind+".sqlite")
                shutil.copyfile(directory / "good.sqlite", path)
                with sqlite3.connect(path) as con:
                    con.execute("DROP TRIGGER record_no_update")
                    raw = con.execute("SELECT payload FROM records WHERE version_id=?", (obj.version_id,)).fetchone()[0]
                    changed = json.loads(raw)
                    if kind == "derived_EQ":
                        changed["value"]["geometry"]["lower"]["numerator"] = 151
                    else:
                        changed["value"]["parent_versions"] = ["v:unretained-parent"]
                    con.execute("UPDATE records SET payload=? WHERE version_id=?", (json.dumps(changed, sort_keys=True, separators=(",", ":")).encode(), obj.version_id))
                with self.assertRaises((ContractError, IntegrityError)):
                    ObjectGraph.restore(path, definition=graph.definition, checkpoint=checkpoint)
            self.assertEqual(graph.get_version(obj.version_id).geometry.lower, 150)
            self.assertEqual(graph.checkpoint(), checkpoint)
        # Request coverage corruption is detected against its actual expected source.
        corrupt = json.loads(json.dumps(payload))
        corrupt["history"][-1]["request"]["coverage"]["observed_intervals"] = [[ns(1), ns(3)]]
        with self.assertRaises((ContractError, IntegrityError)):
            SharedBarEngine.restore(json.dumps(corrupt, sort_keys=True, separators=(",", ":")).encode())
        # The read-only accessor also refuses altered retained request metadata.
        f.engine._history[-1]["request"]["coverage"]["source_version"] = "altered-retained-request"
        with self.assertRaises(IntegrityError):
            f.engine.window_publication(b.version_id)

    def test_cl_x13_source_list_completeness(self):
        prepared = json.loads((ROOT / "reports/c01-l01-source-preparation.json").read_text())
        required = tuple({"source_id": row["id"], "source_specific_semantics": row["idea"],
            "required_disposition": row["rationale"], "exact_open_obligation": row["rationale"],
            "exact_reviewed_clause": row['exact_reviewed_finding_row'],
            "original_proof": row['reading_proof'], "upstream_or_consumer_owners": row['components']}
            for row in prepared["source_findings"])
        mapping = json.loads((ROOT / "reports/c01-l01-case-test-map.json").read_text())
        proposed = tuple(mapping["source_dispositions"])
        self.assertEqual(len(required), 237)
        self.assertTrue(validate_source_obligations(required, proposed))
        variants = []
        variants.append(proposed[:-1])
        variants.append(proposed+(proposed[0],))
        altered = json.loads(json.dumps(proposed))
        altered[0]["required_disposition"] = "rewritten_without_new_definition"
        variants.append(tuple(altered))
        altered = json.loads(json.dumps(proposed))
        altered[0]["full_clause_implementation_status"] = "implemented"
        altered[0]["exact_clause_assertions"] = []
        variants.append(tuple(altered))
        for key, value in (('whole_source_closed', True), ('closure_granted', True),
                           ('original_proof', {}), ('exact_reviewed_clause', 'other-source'),
                           ('upstream_or_consumer_owners', ['substituted'])):
            altered = json.loads(json.dumps(proposed))
            altered[0][key] = value
            variants.append(tuple(altered))
        for rows in variants:
            with self.assertRaises((ContractError, IntegrityError)):
                validate_source_obligations(required, rows)
        self.assertTrue(all(row["whole_source_closed"] is False for row in proposed))
        self.assertEqual({row["case_id"] for row in mapping["cases"]}, set(CASES))
        self.assertTrue(all(row["remaining"] for row in proposed))
        self.assertEqual(len(mapping["cases"]), 41)
        self.assertEqual(hashlib.sha256(GOLDEN_PATH.read_bytes()).hexdigest(), "696b39ea7656c16cea7894f3235d96ba4410fead505781d65feb83b6f04b0a29")

    def test_cl_x14_relation_bound(self):
        g = CASES["CL-X14-relation-bound"]
        inp, exp = g["input"], g["expected"]
        book = RangeRetention(RangeLimits(max_active_relation_pairs=inp["max_active_relation_pairs"]))
        self.assertTrue(book.admit_relation(*inp["admitted_pair"]))
        before = book.state_hash
        with self.assertRaises(ContractError):
            book.admit_relation(*inp["attempt_pair"])
        self.assertEqual(book.state_hash, before)
        self.assertEqual(book.relation_count, len(exp["admitted_pairs_after"]))
        self.assertEqual(book.work["object_identity_merges"], exp["object_identity_merge_count"])
        self.assertFalse(book.admit_relation(*reversed(inp["admitted_pair"])))
        production = RangeRetention(RangeLimits(max_active_relation_pairs=inp['max_active_relation_pairs']))
        values=[]
        for index in range(3):
            f,b,_=from_ohlc((120,200+index,100,180),name='relation-'+str(index))
            values.append(f.version(b))
        relation=relate_ranges(values[0],values[1],retention=production)
        before=production.state_hash
        with self.assertRaises(ContractError):
            relate_ranges(values[0],values[2],retention=production)
        self.assertEqual(production.state_hash,before)
        self.assertEqual(production.relation_count,1)
        self.assertEqual(relate_ranges(values[0],values[1],retention=production),relation)
