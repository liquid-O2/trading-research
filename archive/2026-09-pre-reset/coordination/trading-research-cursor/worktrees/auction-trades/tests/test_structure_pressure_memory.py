"""Registered M03/M08/M09/M11 vectors through actual measurement producers."""

from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from references import structure_pressure_memory_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import WindowCoverage, Watermark
from trading_research.foundations.multiresolution import BarDomain, BarDefinition, SharedBarEngine, WindowRequest
from trading_research.measurements.common import capture_trade_window, capture_bar_window, validate_trade_window
from trading_research.measurements.cvd import measure_cvd, CohortDefinition, CohortChannel, measure_cohort_cvd
from trading_research.measurements.divergence import (
    divergence_endpoint, compare_divergence, preceding_divergence_scales, validate_endpoint,
    DeclaredBreachReference, compare_reference_breaches, fit_divergence_residual, residual_basis,
    apply_divergence_residual,
)
from trading_research.measurements.structure import (
    capture_swing_bars, SwingDefinition, swing_snapshot, multiscale_swing_tree, SwingBook,
    validate_swing_snapshot, swing_scale, retracement,
)
from trading_research.measurements.quotes import (
    measure_quote_pressure, quote_summary, validate_quote_capture, validate_quote_summary,
    recovery_episodes, apply_quote_lag, capture_quote_window,
)
from trading_research.measurements.memory import (
    MemoryDefinition, build_memory, validate_memory, MemoryBook, observe_memory_visits,
    markout, protect_memory, memory_context, MemoryEpisode, retrieve_matured,
)
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.artifact_graph import SemanticArtifactStore, ReadRequest, ReadBinding, ReadSession
from trading_research.measurements.measurement_fits import admit_measurement_fit
from tests.measurement_sources import Sources
from tests.measurement_fixtures import row, ledger, UNIT, request
from tests.measurement_fit_sources import fitted_sources, SCHEMA, UNIT as FIT_UNIT


GOLD = json.loads((Path(__file__).parent/"golden/m03_m08_m09_m11_engineering_v1.json").read_text())
CASES = {c["id"]: c for c in GOLD["cases"]}


class StructurePressureMemoryTests(unittest.TestCase):
    def setUp(self):
        self.s = Sources(self)

    def test_MX07_actual_measurement_F10_F04_publication(self):
        from trading_research.foundations.object_graph import ObjectGraph,RegistryDefinition,PublicationClock
        from trading_research.foundations.graph import Graph,Port,InputPort
        from trading_research.runtime.scheduling import DirtyPlanner,FieldChange
        from trading_research.measurements.measurement_ports import publish_measurement_evidence,measurement_dependency_graph
        from trading_research.operations.artifacts import digest
        v,c,_=self.s.capture([row('a',at=1,price=100),row('b',at=2,price=103),row('c',at=3,price=100)],cut=10)
        swings=swing_snapshot(c,view=v,definition=SwingDefinition('public',reversal_ticks=Fraction(2)))
        graph=ObjectGraph(self.s.root/'measurements.sqlite',definition=RegistryDefinition())
        head=graph.head
        with self.assertRaises(DependencyUnavailable):
            publish_measurement_evidence(swings,graph=graph,instrument=self.s.instrument,
                clocks=PublicationClock(9,9,12,actual_completion_at=12),source_id='s:unavailable-swing')
        self.assertEqual(graph.head,head)
        computation_clock=PublicationClock(10,10,12,actual_completion_at=12)
        evidence=publish_measurement_evidence(swings,graph=graph,instrument=self.s.instrument,
            clocks=computation_clock,source_id='s:swing-measurement')
        self.assertEqual(evidence.known_at,12)
        self.assertEqual(evidence.content_digest,digest({'kind':'CausalMeasurementPublicationV1',
            'measurement':swings.record(),'computation_clock':computation_clock}))
        self.assertEqual([graph.get_version(evidence.version_id).known_at<=cut for cut in (10,12)],[False,True])
        cvd=measure_cvd(c,view=v,anchor_id='public-reset')
        high=next(n for n in swings.confirmed if n.side=='high')
        endpoint=divergence_endpoint(swings=swings,swing_id=high.id,cvd_result=cvd,cvd_capture=c,cvd_view=v,
            comparator='at_extremum',trading_date='2026-01-05')
        memory=build_memory((c,),views=(v,),definition=MemoryDefinition('public-memory'),cut=10,published_at=10)
        quotes=self.s.quotes((self.s.quote_recipe(1,at=2),),initial=(self.s.quote_recipe(0,at=0),),start=1,end=10)
        for name,value in (('cvd',cvd),('endpoint',endpoint),('memory',memory),('quotes',quotes)):
            published=publish_measurement_evidence(value,graph=graph,instrument=self.s.instrument,view=v,
                clocks=PublicationClock(10,10,12,actual_completion_at=12),source_id='s:public-'+name)
            self.assertEqual(graph.get_version(published.version_id),published)
            self.assertEqual(published.known_at,12)
        planner=DirtyPlanner(measurement_dependency_graph())
        changed=planner.plan({'bars':FieldChange(frozenset(),lineage_changed=True)})
        self.assertTrue({'swings','divergence','memory'}.issubset(changed.optional))
        with self.assertRaises(ContractError):
            Graph((Port('a','M08',1,'v1',frozenset({'x'}),(InputPort('b','v1',frozenset({'x'})),)),
                Port('b','M03',1,'v1',frozenset({'x'}),(InputPort('a','v1',frozenset({'x'})),))))

    def test_MX03_exact_4096_quote_inputs_and_atomic_one_over(self):
        initial=self.s.quote_recipe(0,at=0,snapshot=True,native=True)
        recipes=tuple(self.s.quote_recipe(i,at=i,native=True,sequence=i) for i in range(1,4096))
        captured=self.s.quotes(recipes,initial=(initial,),start=1,end=4097)
        self.assertEqual(len(captured.events)+len(captured.initial_recipes),4096)
        before=captured.record()
        with self.assertRaises(ContractError):self.s.quotes(recipes+(self.s.quote_recipe(4096,at=4096,native=True),),initial=(initial,),start=1,end=4098)
        self.assertEqual(captured.record(),before)

    def test_MQ13_actual_lagged_quote_and_trade_channels(self):
        initial=self.s.quote_recipe(0,at=0,quote=(100,102,10,20),snapshot=True,native=True)
        specs=((1,1,8,'M',1,'B'),(2,2,10,'M',1,'B'),(3,2,10,'T',1,'A'),(4,3,14,'M',1,'B'),(5,3,14,'T',3,'B'))
        recipes=tuple(self.s.quote_recipe(i,at=t,quote=(100,102,bid,20),action=action,size=size,side=side,native=True,sequence=i)
                      for i,t,bid,action,size,side in specs)
        capture=self.s.quotes(recipes,initial=(initial,),start=1,end=4,cut=3,spans=((1,3),))
        lag=measure_quote_pressure(capture,kernels=(('half_life',1),))['lag_channels'][0]
        self.assertEqual((lag['ofi'],lag['trade'],lag['product']),(Fraction(9,2),Fraction(5,2),Fraction(45,4)))

    def test_MM08_MM14_actual_visit_decay_and_attempt_producer(self):
        from trading_research.measurements.memory import MemoryAttempt,memory_attempt_summary
        view,c,_=self.s.capture([row('effort',at=0,price=100,size=16)],end=1)
        definition=MemoryDefinition('visits',minimum_size=16,decay_clock='visits',decay_scale=Fraction(1))
        original=build_memory((c,),views=(view,),definition=definition,cut=1,published_at=1)
        rows=[row(str(i),at=t,price=p) for i,(t,p) in enumerate([(1,100),(2,102),(3,100),(4,102),(5,100)])]
        pv,pc,_=self.s.capture(rows,start=1,end=6)
        visits=observe_memory_visits(original,cluster_id=original.clusters[0].id,price_capture=pc,view=pv,definition=('retest',0,0))
        self.assertEqual(visits.retests,2)
        updated=build_memory((c,),views=(view,),definition=definition,cut=6,published_at=6,previous=original,visits=visits)
        self.assertEqual((updated.raw_mass[0],updated.decayed_mass[0]),(16,4))
        attempts=[]
        for i,(horizon,price) in enumerate(((8,98),(10,97))):
            fv,fc,_=self.s.capture([row('mark'+str(i),at=horizon-1,price=price)],start=1,end=horizon)
            label=markout(original,cluster_id=original.clusters[0].id,future_capture=fc,future_view=fv,horizon_end=horizon,
                observation_definition='attempt-mark',cut=horizon,published_at=horizon)
            attempts.append(MemoryAttempt('A'+str(i+1),'E1',original.id,original.clusters[0].id,label,visits))
        summary=memory_attempt_summary(tuple(attempts))
        self.assertEqual((summary['attempt_count'],summary['independent_episode_count'],summary['sum_attempt_markouts']),(2,1,-5))
        self.assertFalse(dict(summary['fresh_effort'])['A2'])

    def test_MD16_zero_preceding_scale_preserves_raw_comparison(self):
        a,b,_=self.endpoints(100,104,b_flow=10)
        view,c,_=self.s.capture((row('flat0',at=-3,price=100,size=5),row('flat1',at=-2,price=100,size=5)),start=-4,end=-1)
        scales=preceding_divergence_scales(c,view=view)
        out=compare_divergence(a,b,cut=4,scales=scales)
        self.assertEqual((out['price_change'],out['flow_change']),(4,-10))
        self.assertIsNone(out['normalized_price_change']);self.assertIsNone(out['discrepancy'])


    def path(self, prices, *, times=None, sizes=None, sides=None, complete=None, end=None, published=None, orders=None, start=0):
        times = list(range(start, start+len(prices))) if times is None else times
        sizes = [1]*len(prices) if sizes is None else sizes
        sides = [1]*len(prices) if sides is None else sides
        complete = [True]*len(prices) if complete is None else complete
        orders = [0]*len(prices) if orders is None else orders
        rows = [row("p"+str(i), at=t, price=p, size=q, side=side, order=o, history_complete=h)
                for i,(p,t,q,side,o,h) in enumerate(zip(prices,times,sizes,sides,orders,complete))]
        # row() fixes ordinary history; explicitly replace to model the registered gap vector.
        rows = [{**r, "history_complete": h} for r,h in zip(rows,complete)]
        return self.s.capture(rows, start=start, end=max(times)+1 if end is None else end, published=published)[:2]

    def endpoints(self, a, b, *, side="high", a_flow=20, b_flow=10):
        initial = a-1 if side=="high" else a+1
        middle = min(a,b)-1 if side=="high" else max(a,b)+1
        delta = b_flow-(a_flow+1)
        rows = [row("p0", at=0, price=initial, size=1), row("a", at=1, price=a, size=a_flow-1),
                row("middle", at=2, price=middle, size=1), row("b", at=3, price=b, size=abs(delta), side=1 if delta>0 else -1)]
        view = ledger(rows)
        definition = SwingDefinition("endpoint-swings", reversal_ticks=1, frozen_at=0)
        output = []
        for end, identity in ((2,"a"),(4,"b")):
            capture = capture_trade_window(view, **request(end=end, published=end))
            swings = swing_snapshot(capture, definition=definition, view=view)
            flow = measure_cvd(capture, view=view, anchor_id="reset1")
            output.append(divergence_endpoint(swings=swings, swing_id=identity, cvd_result=flow,
                cvd_capture=capture, cvd_view=view, comparator="at_extremum", trading_date="2027-01-04"))
        scale_view, scale_capture = self.s.capture((row("s0", at=-3, price=98, size=5), row("s1", at=-2, price=100, size=5)),
                                                  start=-4,end=-1)[:2]
        return *output, preceding_divergence_scales(scale_capture, view=scale_view)

    def bars(self, specs, *, cut=None, published=None):
        domain = BarDomain("NQ.test", "reported_trade", UNIT)
        definition = BarDefinition(domain, "m-test-v1", "calendar", "m-test-v1")
        engine = SharedBarEngine(domain, (definition,))
        rows = []
        for i,(start,end,high,low,pub,*quality) in enumerate(specs):
            rows.extend((row(f"b{i}l",at=start,known=end,price=low,order=0), row(f"b{i}h",at=end-1,known=end,price=high,order=1)))
        view = ledger(rows)
        engine.add_many(tuple(sorted(view.trades.values(),key=lambda t:t.known_at)))
        publications = []
        for start,end,high,low,pub,*quality in specs:
            spans = ((start,end),) if not quality or quality[0] else ((start,end-1),) if end-start>1 else ()
            cov = WindowCoverage("NQ.test",start,end,spans,end,"coverage:"+str(start))
            req = WindowRequest(definition.id,start,end,cov,Watermark(end,end,"watermark:"+str(end)))
            publications.append(engine.publish_window(engine.capture(end),req,published_at=pub))
        cut = max(p.published_at for p in publications) if cut is None else cut
        capture = capture_swing_bars(engine=engine, publication_ids=tuple(p.version_id for p in publications if p.published_at<=cut),
            cut=cut,published_at=cut if published is None else published,definition_version="swings-bars-v1")
        return engine, view, tuple(publications), capture

    def test_MD01_MD02_MD03(self):
        cases = [(104,10,"high"),(96,30,"high"),(96,30,"low"),(104,10,"low"),(101,19,"high"),(110,10,"high"),(100,10,"high"),(104,20,"high")]
        for p,f,side in cases:
            with self.subTest(price=p,flow=f,side=side):
                a,b,scales = self.endpoints(100,p,side=side,b_flow=f)
                tolerance = 1 if (p,f) in ((101,19),(110,10)) else 0
                out = compare_divergence(a,b,cut=4,scales=scales,tolerance_ticks=tolerance)
                expected = literal.disagreement((100,20),(p,f),side,2,5,tolerance)
                self.assertEqual((out["normalized_price_change"],out["normalized_flow_change"],out["discrepancy"]),
                                 (expected["price"],expected["flow"],expected["discrepancy"]))
                self.assertEqual((out["regular"],out["hidden"],out["tie"]),(expected["regular"],expected["hidden"],expected["tie"]))
                self.assertEqual(out["confirmation_delay"],1)

    def test_MD04_MD05_MD06_MD07(self):
        _, opportunity, _ = self.s.clock(0,4)
        ref = DeclaredBreachReference("reference100",100,100,"high",-1)
        for receiver, source, lag in (([99,101,102],[99,99,102],1),([99,99,102],[99,101,102],-1)):
            rv,rc = self.path(receiver,end=4)
            sv,sc = self.path(source,end=4)
            out = compare_reference_breaches(rc,sc,receiver_view=rv,source_view=sv,references=ref,
                opportunity=(opportunity,"session"),cut=4,alignment=("NQ.test","NQ.test","same-clock"))
            self.assertEqual(out["event_lag"],lag)
        rv,rc = self.path([99,101],end=4)
        sv,sc = self.path([99,100],end=4)
        result = compare_reference_breaches(rc,sc,receiver_view=rv,source_view=sv,references=ref,
            opportunity=(opportunity,"session"),cut=4,alignment=("NQ.test","NQ.test","same-clock"))
        self.assertTrue(result["receiver"]["breach"] and result["source"]["nonbreach"])
        self.assertIsNone(result["source"]["event_at"])
        for state in ("closed","missing","stale"):
            ev,empty,_ = self.s.capture((),end=4,spans=())
            unavailable = compare_reference_breaches(rc,empty,receiver_view=rv,source_view=ev,references=ref,
                opportunity=(opportunity,"session"),cut=4,alignment=("NQ.test","NQ.test",state))
            self.assertFalse(unavailable["available"])
            self.assertIsNone(unavailable["source"]["nonbreach"])
        delayed = ledger([row("r",at=3,known=3,price=101)])
        early_source = ledger([row("s",at=2,known=5,price=101)])
        for cut, available in ((3,False),(5,True)):
            rc = capture_trade_window(delayed,**request(end=4,cut=cut,published=cut,spans=((0,min(cut,4)),)))
            sc = capture_trade_window(early_source,**request(end=4,cut=cut,published=cut,spans=((0,min(cut,4)),)))
            out = compare_reference_breaches(rc,sc,receiver_view=delayed,source_view=early_source,references=ref,
                opportunity=(opportunity,"session"),cut=cut,alignment=("NQ.test","NQ.test","delayed"))
            self.assertEqual(out["available"],available)
            if available:self.assertEqual((out["event_lag"],out["knowledge_lag"]),(-1,2))

    def test_MD08_MX06_endpoint_forgery(self):
        a,b,scale = self.endpoints(100,104)
        for change in ({"instrument":"NQM7"},{"trading_date":"2027-01-05"},{"reset_id":"R2"},
                       {"aggregation_unit":"minute_net"},{"cohort_id":"C2"},{"price":Fraction(999)}):
            with self.subTest(change=change),self.assertRaises((ContractError,IntegrityError)):
                compare_divergence(a,replace(b,**change),cut=4,scales=scale)
        with self.assertRaises(DependencyUnavailable):compare_divergence(a,b,cut=3,scales=scale)

    def test_MD09_MD10_MD11_MD12(self):
        definition = CohortDefinition("size10",UNIT,(CohortChannel("small",1,10),CohortChannel("large",10,None)))
        view,capture = self.path([100,100,100,104,104,104],times=[0,1,1,2,3,3],
            sizes=[20,5,5,10,5,5],sides=[1,-1,-1,-1,1,1],orders=[0,0,1,0,0,1],end=5)
        first = capture_trade_window(view,**request(end=2,published=2))
        one,two = measure_cohort_cvd(first,view=view,definition=definition),measure_cohort_cvd(capture,view=view,definition=definition)
        self.assertEqual((measure_cvd(first,view=view,anchor_id="R").close,measure_cvd(capture,view=view,anchor_id="R").close),(10,10))
        self.assertEqual((one.paths[1].close,two.paths[1].close),(20,10))
        soft = CohortDefinition("soft",UNIT,(),(10,20))
        v,c = self.path([100],sizes=[15],end=1)
        paths = measure_cohort_cvd(c,view=v,definition=soft).paths
        self.assertEqual(tuple(p.buy for p in paths),(Fraction(15,2),)*2)
        self.assertEqual(c.window.print_count,1)
        for spans, expected in ((((0,2),), (0,0)),((),None)):
            v = ledger(())
            c = capture_trade_window(v,**request(end=2,published=2,spans=spans))
            p = measure_cohort_cvd(c,view=v,definition=definition).paths[1]
            self.assertEqual(p.true_signed_bounds,expected)
        all_rows = CohortDefinition("all",UNIT,(CohortChannel("all",1,None),))
        result=[]
        for values in ([10,-8,3],[-8,10,3]):
            v,c = self.path([100]*3,sizes=list(map(abs,values)),sides=[1 if x>0 else -1 for x in values],end=3)
            p=measure_cohort_cvd(c,view=v,definition=all_rows).paths[0]
            result.append((p.close,p.high_bounds[0],p.low_bounds[0],p.high_at))
        self.assertEqual(result,[(5,10,0,0),(5,5,-8,2)])

    def test_MD13_running_prefix_is_immutable(self):
        a,b,_ = self.endpoints(100,104)
        self.assertEqual(b.flow,10)
        source = b._recipe["cvd_view"]
        source.add(__import__("trading_research.measurements.tape",fromlist=["Trade"]).Trade.restore(row("later",at=4,price=103,size=20)))
        validate_endpoint(b)
        later = capture_trade_window(source,**request(end=5,published=5))
        self.assertEqual(measure_cvd(later,view=source,anchor_id="reset1").close,30)
        self.assertEqual((a.flow,b.flow),(20,10))
        self.assertTrue(literal.disagreement((100,20),(104,10),"high",1,1)["regular"])
        self.assertFalse(literal.disagreement((100,20),(104,30),"high",1,1)["regular"])

    def test_MD14_MD15_MX01(self):
        rows=(("a",(-1,),0,-2,1),("b",(1,),0,2,2))
        state=fit_divergence_residual(rows,train_end=3,available_at=4,ridge=2,basis=("x0",))
        self.assertEqual(state.coefficients,(literal.ridge_one_dim([-1,1],[-2,2],2),))
        vector=residual_basis((2,3),-1,("intercept","x0","x1","lag","x0*lag","x1*lag"))
        self.assertEqual(vector,(1,2,3,-1,-2,-3))
        self.assertEqual(sum(x*b for x,b in zip(vector,(1,2,0,1,1,0))),2)
        many=tuple((str(i),(1,),0,1,0) for i in range(1024))
        self.assertEqual(len(fit_divergence_residual(many,train_end=1,available_at=2,ridge=1,basis=("x0",)).row_ids),1024)
        with self.assertRaises(ContractError):fit_divergence_residual(many+(("over",(1,),0,1,0),),train_end=1,available_at=2,ridge=1,basis=("x0",))

    def test_MS01_MS02_MS03_MS12(self):
        specs=((0,1,100,90,1),(1,2,110,95,2),(2,3,105,92,4))
        for cut in (3,4):
            engine,view,bars,capture=self.bars(specs,cut=cut)
            snapshot=swing_snapshot(capture,definition=SwingDefinition("pivot",kind="pivot",frozen_at=0))
            expected=literal.pivots([(*s,True) for s in specs],cut=cut)
            self.assertEqual(tuple((n.side,n.price_ticks,n.extreme_start,n.confirmed_at) for n in snapshot.confirmed),expected)
            if cut==3:
                with self.assertRaises(ContractError):capture_swing_bars(engine=engine,publication_ids=tuple(b.version_id for b in bars),cut=3,published_at=3,definition_version="bad")
        equal=((0,1,100,90,1),(1,2,110,95,2),(2,3,110,96,3),(3,4,105,92,4))
        _,_,_,c=self.bars(equal)
        for ties,starts in (("strict",()),("earliest",(1,)),("latest",(2,)),("ambiguous",(1,2))):
            s=swing_snapshot(c,definition=SwingDefinition("pivot:"+ties,kind="pivot",ties=ties))
            self.assertEqual(tuple(n.extreme_start for n in s.confirmed if n.side=="high"),starts)
        _,_,_,gapped=self.bars(((0,1,100,90,1),(1,2,110,95,2),(3,4,105,92,4)))
        self.assertEqual(swing_snapshot(gapped,definition=SwingDefinition("pivot",kind="pivot")).confirmed,())
        with self.assertRaises(ContractError):swing_snapshot(object(),definition=SwingDefinition("bad"))

    def test_MS04_MS05_MS07_MX02(self):
        v,c=self.path([100,106,103,100],end=4)
        definitions=tuple(SwingDefinition("threshold"+str(t),reversal_ticks=t) for t in (2,4))
        tree=multiscale_swing_tree(c,definitions=definitions,view=v)
        highs=[r for r in tree["nodes"] if r["swing"].side=="high"]
        self.assertEqual(tuple((r["swing"].threshold,r["swing"].confirmed_at,r["confirmation_delay"],r["prominence"]) for r in highs),
                         ((2,2,1,3),(4,3,2,Fraction(3,2))))
        self.assertEqual(tuple(r["persistence"] for r in highs),(2,2))
        for d in definitions:
            snapshot=swing_snapshot(c,definition=d,view=v)
            self.assertEqual(tuple((n.side,n.price_ticks,n.extreme_start,n.confirmed_at) for n in snapshot.confirmed),literal.directional([100,106,103,100],[0,1,2,3],d.reversal_ticks))
        thirtytwo=tuple(SwingDefinition("scale"+str(t),reversal_ticks=t+1) for t in range(32))
        self.assertEqual(len(multiscale_swing_tree(c,definitions=thirtytwo,view=v)["snapshots"]),32)
        with self.assertRaises(ContractError):multiscale_swing_tree(c,definitions=thirtytwo+(SwingDefinition("over",reversal_ticks=33),),view=v)
        v,c=self.path([100,106,100],end=3)
        highs=[r for r in multiscale_swing_tree(c,definitions=definitions,view=v)["nodes"] if r["swing"].side=="high"]
        self.assertEqual((len(highs),len({r["swing"].extreme_source for r in highs})),(2,1))

    def test_MS06_MS08_MS09_MS10(self):
        _,_,_,preceding=self.bars(((-2,0,5,0,1),))
        scale=swing_scale(preceding)
        v,c=self.path([100,106,103],end=3)
        s=swing_snapshot(c,definition=SwingDefinition("frozen",reversal_ticks=2,subsequent_scales=(scale,)),view=v)
        high=[n for n in s.confirmed if n.side=="high"][0]
        self.assertEqual((high.threshold,high.confirmed_at,s.provisional[0][-1]),(2,2,10))
        v,c=self.path([100,106,103],complete=[True,False,True],end=3)
        self.assertEqual(swing_snapshot(c,definition=SwingDefinition("gap"),view=v).confirmed,())
        v,c=self.path([100,106,100],times=[0,1,1],orders=[0,None,None],end=2)
        snapshot=swing_snapshot(c,definition=SwingDefinition("unordered"),view=v)
        self.assertFalse(snapshot.order_exact)
        self.assertFalse(any(n.side=="high" for n in snapshot.confirmed))
        ratios=tuple(Fraction(s) for s in CASES["MS10"]["input_vector"]["fractions"])
        self.assertEqual(tuple(retracement(100,120,f) for f in ratios),(100,105,110,115,120,Fraction(633,5),90))

    def test_MS11_MX05_MX06_swing_restart(self):
        v,c=self.path([100,106,103,100],end=4)
        ds=(SwingDefinition("two"),SwingDefinition("four",reversal_ticks=4))
        book=SwingBook(instrument="NQ.test",definition_ids=tuple(d.id for d in ds))
        original=book.advance(c,ds,view=v)
        payload=book.checkpoint()
        restored=SwingBook.restore(payload,recipes=((c,ds,v),),instrument="NQ.test",definition_ids=book.definition_ids)
        self.assertEqual(restored.checkpoint(),payload)
        with self.assertRaises(IntegrityError):SwingBook.restore(payload,recipes=(),instrument="NQ.test",definition_ids=book.definition_ids)
        snapshot=swing_snapshot(c,definition=ds[0],view=v)
        detached=replace(snapshot,confirmed=())
        with self.assertRaises(ContractError):validate_swing_snapshot(detached)
        forged=replace(snapshot,confirmed=())
        object.__setattr__(forged,'_recipe',snapshot._recipe)
        with self.assertRaises(IntegrityError):validate_swing_snapshot(forged)
        self.assertEqual(book.checkpoint(),payload)
        self.assertEqual(original["version_id"],restored._versions[0]["version_id"])
        from trading_research.measurements.tape import Trade
        from trading_research.measurements.structure import validate_swing_tree
        engine,view,bars,source=self.bars(((0,1,100,90,1),(1,2,110,95,2),(2,3,105,92,4)))
        definition=SwingDefinition('corrected-pivot',kind='pivot')
        book=SwingBook(instrument='NQ.test',definition_ids=(definition.id,))
        old=book.advance(source,(definition,))
        before=canonical_json(old)
        self.assertEqual(tuple(n['swing'].price_ticks for n in old['nodes'] if n['swing'].side=='high'),(110,))
        replacement=Trade.restore(row('b1h-corrected',at=1,known=5,price=102,order=1))
        engine.correct(id='middle-high',original_id='b1h',known_at=5,reason='source revision',replacement=replacement)
        view.correct(id='middle-high',original_id='b1h',known_at=5,reason='source revision',replacement=replacement)
        _,request=engine.window_publication(bars[1].version_id)
        revised=engine.publish_window(engine.capture(5),request,published_at=6)
        updated=capture_swing_bars(engine=engine,publication_ids=tuple(b.version_id for b in bars)+(revised.version_id,),
            cut=6,published_at=6,definition_version='swings-bars-v1')
        new=book.advance(updated,(definition,))
        self.assertFalse(any(n['swing'].side=='high' for n in new['nodes']))
        self.assertNotEqual(source.id,updated.id);self.assertEqual(canonical_json(old),before)
        reopened=SharedBarEngine.restore(engine.checkpoint())
        restored_sources=tuple(capture_swing_bars(engine=reopened,**{k:getattr(c,k) for k in
            ('publication_ids','cut','published_at','definition_version','max_inputs','max_bytes')}) for c in (source,updated))
        replay=SwingBook.restore(book.checkpoint(),recipes=tuple((c,(definition,),None) for c in restored_sources),
            instrument='NQ.test',definition_ids=(definition.id,))
        self.assertEqual(replay.checkpoint(),book.checkpoint())
        with self.assertRaises(ContractError):multiscale_swing_tree(updated,definitions=(definition,),previous=dict(old))
        from copy import copy
        forged=copy(new);forged['previous_version']=None
        with self.assertRaises(IntegrityError):validate_swing_tree(forged)

    def test_MQ01_MQ02_MQ03(self):
        initial=self.s.quote_recipe(0,at=0,quote=(100,102,10,20))
        for current in ((100,102,12,17),(101,103,12,17)):
            c=self.s.quotes((self.s.quote_recipe(1,at=1,quote=current),),initial=(initial,))
            result=measure_quote_pressure(c)["transitions"][0]
            expected=literal.quote((100,102,10,20),current)
            self.assertEqual((result[2].ofi_contracts,result[3],result[4]),(expected["ofi"],expected["same"],expected["price"]))
            self.assertEqual((result[2].queue_imbalance,result[2].microprice_points,result[2].spread_points),
                             (expected["imbalance"],expected["microprice"],expected["spread"]))
        for quote in ((103,102,10,20),(100,102,0,20),(100,102,0,0)):
            c=self.s.quotes((self.s.quote_recipe(1,at=1,quote=quote),),initial=(initial,))
            self.assertIsNone(quote_summary(c).terminal_midpoint)
            self.assertIsNone(measure_quote_pressure(c)["transitions"][0][2])

    def test_MQ04_MQ05_MQ06_MQ07(self):
        initial=self.s.quote_recipe(0,at=0,quote=(100,102,10,20),snapshot=True,action="A")
        c=self.s.quotes((),initial=(initial,))
        self.assertEqual(measure_quote_pressure(c)["fresh_pressure_update_count"],0)
        self.assertIsNone(c.initial_state.economic_quote_at)
        unchanged=self.s.quote_recipe(1,at=1,quote=(100,102,10,20))
        copied=self.s.quote_recipe(2,at=2,quote=(100,102,10,20),snapshot=True,action="A")
        c=self.s.quotes((unchanged,copied),initial=(initial,))
        pressure=measure_quote_pressure(c)
        self.assertEqual((pressure["fresh_pressure_update_count"],c.terminal_state.economic_quote_at),(1,1))
        self.assertEqual(tuple(None if r[2] is None else r[2].ofi_contracts for r in pressure["transitions"]),(0,None))
        trade=self.s.quote_recipe(1,at=1,action="T",quote=(100,102,10,20),size=5,price=102,side="B")
        following=self.s.quote_recipe(2,at=2,quote=(100,102,10,17))
        c=self.s.quotes((trade,following),initial=(initial,))
        self.assertEqual((c.transitions[0].after.quote.ask_size,c.terminal_state.quote.ask_size,c.terminal_state.trade_count),(20,17,1))
        ask=next(ep for ep in recovery_episodes(c) if ep["side"]=="ask")
        self.assertEqual(ask["exact_net"],2)
        c=self.s.quotes((self.s.quote_recipe(1,at=1,action="T",size=5,price=100,side="A"),
                        self.s.quote_recipe(2,at=2,quote=(100,102,8,20))),initial=(initial,))
        bid=next(ep for ep in recovery_episodes(c) if ep["side"]=="bid")
        self.assertEqual(bid["exact_net"],3)
        self.assertIsNone(bid["gross_additions"])
        self.assertEqual(3-0,8-5)

    def test_MQ08_MQ09_MQ12_MQ14(self):
        initial=self.s.quote_recipe(0,at=0,quote=(100,102,10,20))
        c=self.s.quotes(tuple(self.s.quote_recipe(i,at=i,quote=(p,102,q,20)) for i,(p,q) in enumerate(((99,8),(100,10)),1)),initial=(initial,))
        self.assertEqual(len([e for e in recovery_episodes(c) if e["side"]=="bid"]),3)
        trade=self.s.quote_recipe(1,at=1,action="T",size=5,price=102,side="B")
        unknown=self.s.quote_recipe(2,at=2,action="T",size=3,price=102,side="N")
        c=self.s.quotes((trade,trade,unknown,self.s.quote_recipe(3,at=3,quote=(100,102,10,17))),initial=(initial,))
        self.assertEqual((c.terminal_state.total_volume,c.terminal_state.buy_volume,c.terminal_state.unknown_volume),(8,5,3))
        ask=next(ep for ep in recovery_episodes(c) if ep["side"]=="ask")
        self.assertEqual((ask["exact_net"],ask["observed_known_execution_net"]),(None,2))
        c=self.s.quotes(tuple(self.s.quote_recipe(i,at=i,quote=(100,102,q,20)) for i,q in enumerate((4,7,10),1)),initial=(initial,))
        bid=next(ep for ep in recovery_episodes(c) if ep["side"]=="bid")
        self.assertEqual((bid["minimum_depth"],bid["initial_depletion"],bid["recovery_at"],bid["full_recovery_at"]),(4,6,2,3))
        c=self.s.quotes((self.s.quote_recipe(1,at=1,quote=(100,102,5,20)),self.s.quote_recipe(2,at=1,quote=(100,102,10,20))),initial=(initial,))
        self.assertFalse(c.order_exact)
        self.assertEqual(quote_summary(c).depth_change,0)
        self.assertIsNone(next(ep for ep in recovery_episodes(c) if ep["side"]=="bid")["recovery_at"])

    def test_MQ10_MQ11_MQ13(self):
        initial=self.s.quote_recipe(0,at=0,quote=(100,102,10,10))
        c=self.s.quotes((self.s.quote_recipe(1,at=1,quote=(100,102,5,0)),),initial=(initial,))
        self.assertFalse(c.terminal_state.trusted)
        # Actual update transitions separately supply the two registered denominators.
        c1=self.s.quotes((self.s.quote_recipe(1,at=1,quote=(100,102,15,10)),),initial=(initial,),end=1000000001)
        i2=self.s.quote_recipe(0,at=0,quote=(100,102,5,5))
        c2=self.s.quotes((self.s.quote_recipe(1,at=1,quote=(100,102,4,5)),),initial=(i2,),end=1000000001)
        p1,p2=measure_quote_pressure(c1),measure_quote_pressure(c2)
        self.assertEqual(p1["raw_ofi"]+p2["raw_ofi"],4)
        self.assertEqual(p1["sum_depth_normalized"]+p2["sum_depth_normalized"],Fraction(3,20))
        initial=self.s.quote_recipe(0,at=-1,quote=(100,102,3,1))
        c=self.s.quotes((self.s.quote_recipe(1,at=0,quote=(100,102,3,1)),self.s.quote_recipe(2,at=2,quote=(100,102,1,3))),
                        initial=(initial,),start=0,end=3)
        p=measure_quote_pressure(c)
        self.assertEqual((p["mean_imbalance"],p["positive_duration_fraction"],p["update_positive_fraction"]),
                         (Fraction(1,6),Fraction(2,3),Fraction(1,2)))
        # Exact source weights are checked independently; actual lag channels must preserve the same causal convolution.
        self.assertEqual(sum(Fraction(o,2**age) for age,o in zip((0,1,2),(4,2,-2))),Fraction(9,2))
        self.assertEqual(sum(Fraction(t,2**age) for age,t in zip((0,1,2),(3,-1,0))),Fraction(5,2))

    def test_MQ15_MQ16_MQ17_MX03_MX06(self):
        initial=self.s.quote_recipe(0,at=0)
        c=self.s.quotes((self.s.quote_recipe(1,at=2,quote=(101,103,12,17)),),initial=(initial,),start=1,end=3)
        q=quote_summary(c)
        self.assertEqual((q.initial_midpoint,q.terminal_midpoint,q.spread_change,q.depth_change,q.strictly_prewindow),(404,408,0,-1,True))
        first=self.s.quotes((self.s.quote_recipe(1,at=2),),start=1,end=3)
        self.assertFalse(quote_summary(first).strictly_prewindow)
        with self.assertRaises(IntegrityError):validate_quote_summary(replace(q,terminal_midpoint=999),c)
        bad=replace(c.events[0],size=50)
        self.assertEqual(bad.id,c.events[0].id)
        detached=replace(c,events=(bad,))
        with self.assertRaises(ContractError):validate_quote_capture(detached)
        forged=replace(c,events=(bad,))
        object.__setattr__(forged,'_mapping',c._mapping)
        with self.assertRaises(IntegrityError):validate_quote_capture(forged)
        before=canonical_json(c.record())
        with self.assertRaises(ContractError):self.s.quotes((initial,)*4097,start=0,end=1)
        self.assertEqual(canonical_json(c.record()),before)

    def memory(self, rows, *, definition=None, start=0, end=3, published=None, cut=None, previous=None):
        view,capture,_=self.s.capture(rows,start=start,end=end,cut=cut,published=published)
        definition=definition or MemoryDefinition("memory",time_radius_ns=10,price_radius_ticks=0,decay_kernel="box",decay_scale=1000)
        result=build_memory((capture,),views=(view,),definition=definition,cut=capture.window.cut,
                            published_at=capture.window.published_at,previous=previous)
        return result,view,capture

    def test_MM01_MM02_MM03_MM04(self):
        rows=[row("a",at=0,price=100,size=10),row("b",at=1,price=100,size=8,side=-1),row("c",at=2,price=100,size=2,side=None)]
        memory,view,capture=self.memory(rows)
        self.assertEqual((len(memory.clusters),memory.raw_mass),(3,(10,8,2)))
        expected=literal.clusters([(r["id"],r["event_at"],r["price"],r["size"],r["side"]) for r in rows],0,10)
        self.assertEqual(tuple(sorted((c.member_ids,c.gross,c.center_ticks) for c in memory.clusters)),expected)
        rows=[row("a",at=0,price=100,size=10),row("b",at=1,price=101,size=20),row("c",at=2,price=102,size=30)]
        v=ledger(rows)
        a=capture_trade_window(v,**request(end=2,published=2))
        b=capture_trade_window(v,**request(start=1,end=3,published=3))
        d=MemoryDefinition("union",price_radius_ticks=1,time_radius_ns=10,decay_scale=100)
        union=build_memory((a,b),views=(v,v),definition=d,cut=3,published_at=3)
        self.assertEqual((union.clusters[0].member_ids,union.clusters[0].gross,union.clusters[0].center_ticks),(('a','b','c'),60,Fraction(304,3)))
        d=MemoryDefinition("bridge",price_radius_ticks=2,time_radius_ns=2,decay_scale=100)
        base=[row("a",at=0,price=100,size=10,order=0),row("b",at=0,price=104,size=10,order=1)]
        old,v,_=self.memory(base,definition=d,end=1)
        v.add(__import__("trading_research.measurements.tape",fromlist=["Trade"]).Trade.restore(row("c",at=1,price=102,size=10)))
        new_capture=capture_trade_window(v,**request(end=2,published=2))
        merged=build_memory((new_capture,),views=(v,),definition=d,cut=2,published_at=2,previous=old)
        self.assertEqual((len(old.clusters),len(merged.clusters),merged.clusters[0].center_ticks),(2,1,102))
        self.assertEqual(merged.clusters[0].member_ids,('a','b','c'))
        self.assertEqual(len(merged.clusters[0].predecessors),2)
        v.correct(id="remove-c",original_id="c",known_at=3,reason="source revision",replacement=None)
        corrected=capture_trade_window(v,**request(end=2,cut=3,published=3))
        split=build_memory((corrected,),views=(v,),definition=d,cut=3,published_at=3,previous=merged)
        self.assertEqual((len(split.clusters),merged.clusters[0].raw_count),(2,3))
        validate_memory(old)

    def test_MM05_MM06_MM08_MX04(self):
        d=MemoryDefinition("triangular",spatial_grid=(99,100,101),spatial_kernel="triangular",decay_kernel="box",decay_scale=100)
        m,_,_=self.memory([row("a",at=0,price=100,size=10)],definition=d,end=1)
        self.assertEqual(tuple(c[1][0] for c in m.field_cells),literal.triangular(100,10,[99,100,101]))
        self.assertEqual(m.raw_mass,(10,0,0))
        rows=[row("a",at=0,price=100,size=16),row("later",at=1,price=100,size=8)]
        for clock,scale,expected in (("time",2,8),("volume",4,4)):
            d=MemoryDefinition("decay:"+clock,minimum_size=10,decay_clock=clock,decay_scale=scale)
            m,_,_=self.memory(rows,definition=d,end=2)
            self.assertAlmostEqual(m.decayed_mass[0],expected)
            self.assertEqual(m.raw_mass[0],16)
        grid=tuple(range(4096))
        d=MemoryDefinition("large-grid",spatial_grid=grid)
        m,_,_=self.memory([row("a",at=0,price=100)],definition=d,end=1)
        self.assertEqual(len(m.field_cells),4096)
        with self.assertRaises(ContractError):MemoryDefinition("over",spatial_grid=tuple(range(4097)))

    def test_MM07_MM08_MM14(self):
        m,_,_=self.memory([row("a",at=0,price=100,size=10)],end=1)
        rows=[row("a",at=0,price=100,size=10),row("tick1",at=1,price=101),row("tick2",at=2,price=100),
              row("exit",at=3,price=103),row("b",at=4,price=100,size=3),row("tick5",at=5,price=100)]
        view,capture,_=self.s.capture(rows,end=6)
        visits=observe_memory_visits(m,cluster_id=m.clusters[0].id,price_capture=capture,view=view,definition=("visit-band",1,0))
        self.assertEqual((visits.visits,visits.retests),(2,1))
        self.assertIn("b",visits.new_source_ids)
        self.assertNotIn("a",visits.new_source_ids)
        self.assertEqual(16*2**(-2),4)
        attempts=(('E1','A1',-2,True),('E1','A2',-3,False))
        self.assertEqual((len(attempts),len({a[0] for a in attempts}),sum(a[2] for a in attempts)),(2,1,-5))

    def test_MM09_MM10_MM11_MM12(self):
        for side in (1,-1):
            m,_,_=self.memory([row("origin",at=0,price=100,size=100,side=side)],end=1)
            rows=[row(str(i),at=t,price=p) for i,(t,p) in enumerate(((2,103),(3,98),(4,101)))]
            v,c,_=self.s.capture(rows,start=1,end=5,published=5)
            for cut,status in ((3,"pending"),(4,"pending"),(5,"mature")):
                out=markout(m,cluster_id=m.clusters[0].id,future_capture=c,future_view=v,horizon_end=4,
                    observation_definition="observed-trade-price",cut=cut,published_at=cut)
                self.assertEqual(out.status,status)
                if status=="mature":self.assertEqual((out.terminal_markout,out.mfe,out.mae),literal.markout(100,side,[103,98,101]))
            v,c,_=self.s.capture([row(str(i),at=i+2,price=p) for i,p in enumerate((99,98,97))],start=1,end=5)
            loss=markout(m,cluster_id=m.clusters[0].id,future_capture=c,future_view=v,horizon_end=4,
                         observation_definition="trade-price",cut=5,published_at=5)
            self.assertEqual(loss.terminal_markout,-3*side)
        m,_,_=self.memory([row("origin",at=0,price=100)],end=1)
        v,c,_=self.s.capture([row("seen",at=2,price=101),row("unpriced",at=3,price=None)],start=1,end=5,spans=((1,4),))
        out=markout(m,cluster_id=m.clusters[0].id,future_capture=c,future_view=v,horizon_end=4,
                    observation_definition="trade-price",cut=5,published_at=5)
        self.assertEqual((out.status,out.terminal_markout,out.mfe,out.observed_mfe),("unavailable",None,None,1))

    def test_MM13(self):
        m,_,_=self.memory([row("origin",at=0,price=100)],end=1)
        v,c=self.path([100,106,100],times=[1,2,5],end=6,published=6)
        s=swing_snapshot(c,definition=SwingDefinition("protect"),view=v)
        high=next(n for n in s.confirmed if n.side=="high")
        for cut,expected in ((3,False),(6,True)):
            out=protect_memory(m,cluster_id=m.clusters[0].id,swings=s,swing_id=high.id,published_at=6,cut=cut)
            self.assertEqual((out["protected"],out["birth"]),(expected,1))

    def test_MM17_MX05_MX06_memory_restore(self):
        rows=[row(str(i),at=i,price=100,size=q) for i,q in enumerate((59,60,61))]
        for strict,expected in ((False,121),(True,61)):
            d=MemoryDefinition("threshold",minimum_size=60,strict_size=strict)
            m,v,c=self.memory(rows,definition=d)
            self.assertEqual(sum(m.raw_mass),expected)
            book=MemoryBook(definition=d)
            book.advance((c,),views=(v,),cut=3,published_at=3)
            payload=book.checkpoint()
            restored=MemoryBook.restore(payload,recipes=book.recipes,definition=d)
            self.assertEqual(restored.checkpoint(),payload)
            detached=replace(m,raw_mass=(0,0,0))
            with self.assertRaises(ContractError):validate_memory(detached)
            forged=replace(m,raw_mass=(0,0,0))
            object.__setattr__(forged,'_recipe',m._recipe)
            with self.assertRaises(IntegrityError):validate_memory(forged)
            with self.assertRaises(IntegrityError):MemoryBook.restore(payload,recipes=(),definition=d)
        with self.assertRaises(ContractError):MemoryDefinition("proxy",cohort_definition="ohlc_signed_proxy")

    def ridge_state(self):
        rows=(("train1",(-1,),0,-2,12),("train2",(1,),0,2,22))
        recipe=digest({"rows":rows,"train_end":30,"available_at":31,"ridge":2,"basis":("x0",)})
        state={"coefficients":(Fraction(1),),"basis":("x0",),"ridge":Fraction(2),"train_end":30,
               "available_at":31,"row_ids":("train1","train2"),"recipe_id":recipe}
        parameters={"x_columns":("x",),"lag_column":"lag","y_column":"observed","basis":("x0",),
                    "ridge":2,"train_end":30,"available_at":31}
        return recipe,state,parameters

    def test_MX08_real_retained_ridge_consumers(self):
        recipe,state,parameters=self.ridge_state()
        for family in ("divergence_residual","quote_lag"):
            with TemporaryDirectory() as root:
                query={"x":2,"lag":0,"observed":3}
                capture=None
                if family=="quote_lag":
                    capture=self.s.quotes((self.s.quote_recipe(1,at=39,quote=(100,102,12,9)),),
                        initial=(self.s.quote_recipe(0,at=38,quote=(100,102,10,10)),),start=39,end=40)
                    query["quote_capture"]=capture.record()
                f=fitted_sources(root,family=family,parameters=parameters,recipe_id=recipe,state=state,
                    training_features=({"x":-1,"lag":0},{"x":1,"lag":0}),query_features=query)
                if family=="quote_lag":out=apply_quote_lag(f["admission"],query_session=f["query_session"],window_start=39,capture=capture)
                else:out=apply_divergence_residual(f["admission"],query_session=f["query_session"],window_start=39)
                self.assertEqual((out["expected"],out["residual"]),(2,1))
                reopened=SemanticArtifactStore(Path(root),f["store"].namespace)
                admission=admit_measurement_fit(reopened,f["commit"],f["transform"].id,f["request"],schema_id=SCHEMA,unit=FIT_UNIT,recipe_id=recipe)
                self.assertEqual(admission.payload,canonical_json(state))
                with self.assertRaises(ContractError):apply_divergence_residual(admission,query_session=f["query_session"],window_start=30)

    def test_MM15_MM16_MX08_real_retained_memory_distance(self):
        episodes=[]
        for identity,x,y,maturity,episode in (("a",1,3,8,"A"),("b",3,-1,9,"B"),("c",2,100,11,"C"),("q",2,100,8,"Q")):
            m,_,_=self.memory([row("origin:"+identity,at=0,price=100,size=x)],end=1)
            context=memory_context(m,cluster_id=m.clusters[0].id,feature_names=("size",),episode=episode,date_group=identity)
            v,c,_=self.s.capture([row("future:"+identity,at=4,price=100+y)],start=1,end=5,published=maturity)
            label=markout(m,cluster_id=m.clusters[0].id,future_capture=c,future_view=v,horizon_end=4,
                observation_definition="fixed-trade-markout",cut=maturity,published_at=maturity)
            episodes.append(MemoryEpisode(identity,context,label))
        m,_,_=self.memory([row("query",at=8,price=100,size=2)],end=9,published=10)
        query=memory_context(m,cluster_id=m.clusters[0].id,feature_names=("size",),episode="Q",date_group="query")
        recipe=digest(("memory-distance",("x",)))
        state={"columns":("x",),"means":(2.0,),"scales":(1.0,)}
        with TemporaryDirectory() as root:
            f=fitted_sources(root,family="memory_distance",parameters={"columns":("x",)},recipe_id=recipe,state=state,
                training_features=({"x":1},{"x":3}),query_features={"x":2},clock_offset=-30)
            out=retrieve_matured(query,tuple(episodes),definition=("nearest",2,False),cut=10,
                fit_admission=f["admission"],query_session=f["query_session"])
            self.assertEqual((out["selected"],out["distances"],out["mean_markout"]),(("a","b"),(1,1),1))
            empty=retrieve_matured(query,(episodes[2],),definition=("nearest",2,False),cut=10,
                fit_admission=f["admission"],query_session=f["query_session"])
            self.assertEqual((empty["selected"],empty["support"],empty["mean_markout"]),((),0,None))
