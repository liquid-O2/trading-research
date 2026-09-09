from fractions import Fraction
import math
import unittest

from references import measurement_flow_literal as literal
from trading_research.errors import ContractError
from trading_research.foundations.contracts import Target, Capability
from trading_research.foundations.units import Unit, Ticks
from trading_research.measurements.common import capture_trade_window
from trading_research.measurements.tape_intensity import (
    measure_tape_intensity, PrewindowContext, fit_conditional_flow, fit_count_likelihood,
    fit_effort_progress_surface, BurstTracker, matured_effort_markout,
)
from trading_research.research.labels import PathPoint, ObservationWindow
from tests.measurement_fixtures import CASES, row, ledger, request, capture, gold_capture


class MeasurementIntensityTests(unittest.TestCase):
    def test_M10_ZERO_001_and_SCALE_actual_quote_origin(self):
        from tests.measurement_sources import Sources
        from trading_research.measurements.quotes import quote_summary
        s=Sources(self)
        outputs=[]
        for effort,move,epsilon in ((0,4,1),(1,1,1),(10,10,10)):
            initial=s.quote_recipe(0,at=0,quote=(100,102,10,20),snapshot=False)
            # The actual F02 tick is 1/4 point; four midpoint ticks per point.
            terminal=s.quote_recipe(1,at=2,quote=(100+move/4,102+move/4,10,20))
            qc=s.quotes((terminal,),initial=(initial,),start=1,end=3,cut=3)
            view,c,_=s.capture([] if not effort else [row('effort',at=2,size=effort)],start=1,end=3,cut=3)
            value=measure_tape_intensity(c,view=view,epsilon=epsilon,price_origin='quote_mid',quote_summary=(quote_summary(qc),qc))
            outputs.append(value)
        self.assertEqual((outputs[0].gross_effort,outputs[0].progress_ticks,outputs[0].zero_effort),(0,4,True))
        self.assertEqual([v.effort_progress_ratio for v in outputs[1:]],[Fraction(1,2)]*2)
        self.assertEqual([v.gross_effort for v in outputs[1:]],[1,10])

    def test_M10_EFFORT_001(self):
        view, c = gold_capture("M10-EFFORT-001")
        m = measure_tape_intensity(c, view=view, epsilon=1)
        self.assertEqual((m.gross_effort, m.signed_effort, m.progress_ticks, m.effort_progress_ratio,
                          m.count_per_sec, m.contracts_per_sec, m.zero_effort), (100, 100, 0, 0, 2, 100, False))

    def test_M10_SCALE_001(self):
        for epsilon in (0, -1, True):
            view, c = capture([row("a")])
            with self.assertRaises(ContractError):
                measure_tape_intensity(c, view=view, epsilon=epsilon)

    def test_M10_PACE_001(self):
        rows = [row("a", at=100000000, size=5), row("b", at=900000000, size=5)]
        outputs = []
        for duration in (10**9, 2 * 10**9):
            view, c = capture(rows, end=duration)
            m = measure_tape_intensity(c, view=view, epsilon=1)
            outputs.append((m.contracts_per_sec, m.count_per_sec))
        self.assertEqual(outputs, [(10, 2), (5, 1)])

    def test_M10_OUTAGE_001(self):
        inputs = CASES["M10-OUTAGE-001"]["inputs"]
        view, c = capture(inputs["trades"], end=10**9, spans=tuple(map(tuple, inputs["observed_intervals"])))
        m = measure_tape_intensity(c, view=view, epsilon=1)
        self.assertEqual((m.covered_ns, m.missing_ns, m.contracts_per_sec, m.count_per_sec), (500000000, 500000000, 20, 4))
        self.assertEqual(m.interarrival_ns, ())
        self.assertFalse(m.history_complete)

    def test_M10_RUN_001(self):
        view, c = gold_capture("M10-RUN-001")
        m = measure_tape_intensity(c, view=view, epsilon=1)
        self.assertEqual((m.max_known_same_side_run, m.final_known_run, c.window.print_count), (2, 1, 5))

    def test_M10_MOTION_001(self):
        view, c = gold_capture("M10-MOTION-001")
        m = measure_tape_intensity(c, view=view, epsilon=1)
        self.assertEqual((m.progress_ticks, m.absolute_tick_movement, m.high_ticks, m.low_ticks), (1, 5, 103, 100))

    def test_M10_SEASONAL_001(self):
        rows = [row("a", at=100000000, size=6), row("b", at=900000000, size=4, side=-1),
                row("c", at=1100000000, size=7), row("d", at=1200000000, size=6),
                row("e", at=1300000000, size=4, side=-1), row("f", at=1900000000, size=3, side=-1)]
        view = ledger(rows)
        captures = tuple(capture_trade_window(view, **request(start=i * 10**9, end=(i + 1) * 10**9)) for i in range(2))
        contexts = (PrewindowContext("session-v1", 0, (("session", "rth"),)),
                    PrewindowContext("session-v1", 10**9, (("session", "rth"),)))
        baseline = fit_conditional_flow(tuple(zip(captures, contexts)), view=view, train_end=3*10**9, available_at=3*10**9 + 1)
        expected = literal.flow_baseline(((1, 2, 10, 2), (1, 4, 20, 6)), 2)
        self.assertEqual(tuple(rate * 2 for rate in (baseline.pooled.count_rate, baseline.pooled.gross_rate, baseline.pooled.signed_rate)), expected)
        self.assertEqual(expected, (6, 30, 8))
        self.assertEqual(tuple(a - b for a, b in zip((8, 40, 10), expected)), (2, 10, 2))

    def test_M10_PREWINDOW_001(self):
        view, c = capture([row("a", at=12)], start=10, end=20)
        context = PrewindowContext("bad-context", 11, (("burst", "completed_size"),))
        with self.assertRaises(ContractError):
            fit_conditional_flow(((c, context),), view=view, train_end=30, available_at=31)

    def test_M10_BURST_001(self):
        inputs = CASES["M10-BURST-001"]["inputs"]
        rows = [row(f"w{i}p{j}", at=i*10**9 + (j+1)*1000000)
                for i, count in enumerate(inputs["whole_print_counts"]) for j in range(count)]
        view = ledger(rows)
        captures = tuple(capture_trade_window(view, **request(start=a, end=b)) for a, b in inputs["captured_windows"])
        tracker = BurstTracker(threshold_count_per_sec=3, threshold_known_at=0, version="burst3")
        for c in captures[:4]:
            tracker.observe(c, view=view)
        first = tracker.episodes[0]
        self.assertEqual((first.born_at, first.completed_at), (2000000001, 4000000001))
        before = tracker.checkpoint()
        tracker.observe(captures[4], view=view)
        self.assertEqual(tracker.episodes[0], first)
        self.assertEqual(tracker.episodes[1].born_at, 5000000001)
        restored = BurstTracker.restore(before, captures=captures[:4], view=view)
        self.assertEqual(restored.episodes, (first,))

    def test_M10_MARKOUT_001(self):
        view, c = capture([row("origin", at=1, price=100)], end=10, published=10)
        target = Target("markout", "markout-v1", "NQ.test", 10, 15, "observed-price", "effort-windows",
                        Unit.TICKS, frozenset({Capability.TERMINAL_RETURN}))
        kwargs = dict(view=view, target=target, points=(PathPoint(15, 0, Ticks(103), 15),),
                      coverage=ObservationWindow(10, 15, 15, version="observed-v1"), side=1, published_at=15)
        self.assertIsNone(matured_effort_markout(c, cut=14, **kwargs))
        self.assertEqual(matured_effort_markout(c, cut=15, **kwargs).signed_terminal_ticks, 3)
        self.assertNotIn("signed_terminal_ticks", measure_tape_intensity(c, view=view, epsilon=1).__dataclass_fields__)

    def test_M10_COUNT_LIKELIHOOD_001(self):
        fit = fit_count_likelihood((1, 9))
        self.assertEqual((fit.mean_per_second, fit.variance_per_second, fit.negative_binomial_shape), (5, 16, Fraction(25, 11)))
        self.assertAlmostEqual(math.exp(fit.log_probability(0, exposure_ns=10**9, kind="negative_binomial")), (5/16)**(25/11), places=12)
        self.assertAlmostEqual(math.exp(fit.log_probability(0, exposure_ns=10**9)), math.exp(-5), places=12)
        self.assertEqual(fit.log_probability(0, exposure_ns=0), 0)
        self.assertEqual(fit.log_probability(1, exposure_ns=0), -math.inf)

    def test_M10_SURFACE_001(self):
        state = fit_effort_progress_surface(((2, 1, 0), (2, 1, 2), (20, 1, 0), (20, 1, 8)),
                                            effort_cuts=(10,), available_at=10)
        self.assertEqual(tuple(c[1] for c in state.cells), (1, 4))
        self.assertEqual(state.pooled, Fraction(5, 2))
