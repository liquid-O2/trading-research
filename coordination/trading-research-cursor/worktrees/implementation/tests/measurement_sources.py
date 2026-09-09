"""Actual synthetic F01/F02/F03/F09/F10 sources for the combined measurement suite."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

from trading_research.context.range_adapter import select_clock, primitive_from_shared_bar
from trading_research.data.events import SourceAddress
from trading_research.foundations.bars import WindowCoverage, Watermark
from trading_research.foundations.calendar import Calendar, Session
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition, InstrumentRegistry
from trading_research.foundations.intervals import Span, NamedInterval, IntervalGraph
from trading_research.foundations.multiresolution import BarDomain, BarDefinition, SharedBarEngine, WindowRequest, BarLimits
from trading_research.foundations.object_graph import (
    Instrument, ObjectGraph, RegistryDefinition, EvidenceVersion, AnchorVersion, AtomicBatch,
    PublicationClock, Support, EvidencePurpose,
)
from trading_research.foundations.time import Clocks, AvailabilityBasis
from trading_research.measurements.anchored import capture_anchor
from trading_research.measurements.common import capture_trade_window, capture_bar_window
from trading_research.measurements.quotes import MBPEventRecipe, capture_quote_window
from trading_research.operations.artifacts import digest
from tests.measurement_fixtures import row, ledger, request, UNIT


INSTRUMENT = Instrument("synthetic", "CME", "1", "NQ.test", "terms.v1", Fraction(1, 4), -10**15, 10**15)


class Sources:
    def __init__(self, testcase, *, instrument=INSTRUMENT):
        self.temp = TemporaryDirectory()
        testcase.addCleanup(self.temp.cleanup)
        self.root, self.instrument, self.counter = Path(self.temp.name), instrument, 0

    def clock(self, start, end, *, day=date(2026, 1, 5), cut=None, name="session", calendar=None):
        cut = end if cut is None else cut
        known = min(start, cut)-1
        cal = Calendar() if calendar is None else calendar
        session = Session("session:"+day.isoformat(), day, "NQ", start, end, (), 0, known,
                          "calendar:"+day.isoformat(), "synthetic-exact-clock", True, "engineering fixture")
        cal.append(session)
        node = NamedInterval(name, "measurement-fixture", (Span(start, end),), known,
                             "interval:"+day.isoformat()+":"+name, "synthetic-clock", "synthetic-tz", (day,))
        graph = IntervalGraph("measurement-fixture", (node,))
        selection = select_clock(calendar=cal, interval_graph=graph, interval_name=name, trading_date=day,
                                  instrument_root="NQ", instrument=self.instrument, cut=cut)
        return cal, graph, selection

    def capture(self, rows, *, start=0, end=10, cut=None, published=None, spans=None, bar=False,
                definition="m-test-v1", view=None, engine=None, max_inputs=4096):
        cut = end if cut is None else cut
        published = cut if published is None else published
        view = ledger(rows, max_events=max_inputs) if view is None else view
        spec = request(start=start, end=end, cut=cut, published=published, spans=spans,
                       instrument=self.instrument.raw_symbol, definition=definition, max_inputs=max_inputs)
        if not bar:
            return view, capture_trade_window(view, **spec), None
        domain = BarDomain(self.instrument.raw_symbol, "reported_trade", UNIT)
        clock = BarDefinition(domain, definition, "calendar.synthetic", definition)
        if engine is None:
            engine = SharedBarEngine(domain, (clock,), limits=BarLimits(max_inputs, 32, min(32, max_inputs), 4096))
            engine.add_many(tuple(sorted(view.trades.values(), key=lambda t: t.known_at)))
        cov = spec["coverage"]
        wm = Watermark(end, cut, "watermark:"+str(end)) if end <= cut else None
        req = WindowRequest(clock.id, start, end, cov, wm)
        result = engine.publish_window(engine.capture(cut), req, published_at=published)
        capture = capture_bar_window(engine, result.version_id, view=view, aggregation_unit=UNIT,
                                      published_at=published, max_inputs=max_inputs)
        return view, capture, engine

    def anchor(self, capture, *, kind="event", name=None, graph=None):
        self.counter += 1
        name = name or str(self.counter)
        graph = graph or ObjectGraph(self.root/("anchor-"+name+".sqlite"), definition=RegistryDefinition())
        w = capture.window
        at = max(w.published_at, w.end)
        evidence = EvidenceVersion("s:"+name, "e:"+name, 0, None, min(w.end, w.cut), at,
            Support.OBSERVED, self.instrument, digest(capture.record()), EvidencePurpose.MEASUREMENT)
        anchor = AnchorVersion("a:"+name, "av:"+name, 0, None, (evidence.version_id,), w.start, min(w.end, w.cut),
                               min(w.end, w.cut), at)
        clocks = PublicationClock(at, at, at, actual_completion_at=at)
        batch = AtomicBatch("batch:"+name, graph.sequence+1, graph.definition.version, clocks, (evidence, anchor), 2)
        graph.commit_batch(batch, expected_head=graph.head)
        captured = capture_anchor(graph, anchor_version_id=anchor.version_id, instrument=self.instrument,
                                   cut=at, published_at=at, definition_version=kind)
        return captured, graph

    def primitive(self, rows, *, start=0, end=10, cut=None, published=None, selection=None,
                  spans=None, view=None):
        """Actual F03-aligned F09 publication for the existing C01/M12 adapter."""
        cut = end if cut is None else cut
        published = cut if published is None else published
        if selection is None:
            _, _, selection = self.clock(start,end,cut=cut)
        view = ledger(rows) if view is None else view
        domain = BarDomain(self.instrument.raw_symbol,UNIT,UNIT)
        definition = BarDefinition(domain,'measurement-reference-fixture',selection.interval_graph.version,selection.clock_id)
        engine = SharedBarEngine(domain,(definition,),limits=BarLimits(4096,32,32,4096))
        engine.add_many(tuple(sorted(view.trades.values(),key=lambda t:t.known_at)))
        coverage = WindowCoverage(self.instrument.raw_symbol,start,end,((start,end),) if spans is None else spans,cut,'primitive-coverage')
        req = WindowRequest(definition.id,start,end,coverage,Watermark(end,cut,'primitive-watermark') if end <= cut else None)
        bar = engine.publish_window(engine.capture(cut),req,published_at=published)
        primitive = primitive_from_shared_bar(selection=selection,engine=engine,publication_version_id=bar.version_id,cut=published)
        return primitive,engine,bar,view

    def profile(self, trades, *, grid=None, definition=None, start=0, end=10, cut=None, published=None,
                bar=False, spans=None, name=None, view=None, cohort=None, cohort_index=None,
                source_identity=None):
        from trading_research.measurements.profiles import FrozenGrid, ProfileDefinition, build_profile
        prefix = "" if source_identity is None else str(source_identity) + ":"
        rows = [row(prefix + str(i), at=start+i, price=p, size=q, side=side, instrument=self.instrument.raw_symbol)
                for i, (p, q, side) in enumerate(trades)]
        v, c, engine = self.capture(rows, start=start, end=end, cut=cut, published=published, bar=bar, spans=spans, view=view)
        anchor, graph = self.anchor(c, name=name)
        grid = grid or FrozenGrid(100, 1, 0, 10, "grid.v1", start-1)
        definition = definition or ProfileDefinition("profile.v1")
        p = build_profile((c,), views=(v,), anchors=(anchor,), graphs=(graph,), grid=grid, definition=definition,
                           cohort=cohort, cohort_index=cohort_index)
        return p, v, c, anchor, graph, engine

    def mapping(self):
        inst = self.instrument
        key = InstrumentKey(inst.provider, inst.venue, inst.raw_id, inst.raw_symbol, "NQ", inst.definition_version,
                            expiry_at=inst.expiry_at)
        clocks = Clocks(inst.valid_from, inst.valid_from, "instrument-terms", AvailabilityBasis.RECEIVED,
            valid_from=inst.valid_from, valid_until=inst.valid_until, received_at=inst.valid_from)
        definition = InstrumentDefinition(key, clocks, "future", Decimal(20), Decimal(inst.tick_size_points.numerator)/Decimal(inst.tick_size_points.denominator))
        mapping = InstrumentRegistry()
        mapping.append(definition)
        return mapping, definition

    def quote_recipe(self, i, *, at, quote=(100,102,10,20), action="M", size=1, side="B", price=100,
                     snapshot=False, received=None, native=False, sequence=None):
        fields = {"t": at, "action": action, "side": side, "price": price, "size": size,
                  "bid_px": quote[0], "ask_px": quote[1], "bid_sz": quote[2], "ask_sz": quote[3],
                  "instrument_id": int(self.instrument.raw_id), "flags": 32 if snapshot else 0}
        if native:
            fields = {("ts_event" if k=="t" else k+"_00" if k in ("bid_px","ask_px","bid_sz","ask_sz") else k): v
                      for k,v in fields.items()}
            for k in ("price", "bid_px_00", "ask_px_00"):
                fields[k] *= 1000000000
            fields.update(ts_recv=at, publisher_id=1, sequence=i if sequence is None else sequence, depth=0)
        address = SourceAddress("synthetic/mbp1", "measurement-fixture", "mbp.fixture", "quote-content", "stream:1", i,
                                "native-v1" if native else "quantpad11-v1")
        return MBPEventRecipe(fields, address, native, None, at if received is None else received)

    def quotes(self, recipes, *, initial=(), start=1, end=10, cut=None, published=None, spans=None, max_inputs=4096):
        cut = end if cut is None else cut
        published = cut if published is None else published
        mapping, definition = self.mapping()
        coverage = WindowCoverage(self.instrument.raw_symbol, start, end,
            ((start, end),) if spans is None else spans, cut, "quote-coverage")
        return capture_quote_window(tuple(recipes), mapping=mapping, terms=definition.futures_terms(), instrument=self.instrument,
            start=start, end=end, cut=cut, published_at=published, coverage=coverage, definition="quote-window-v1",
            initial_recipes=tuple(initial), max_inputs=max_inputs)
