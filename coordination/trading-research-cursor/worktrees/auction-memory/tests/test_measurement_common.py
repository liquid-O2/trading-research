from dataclasses import replace
import unittest

from references import measurement_flow_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import WindowCoverage, Watermark
from trading_research.foundations.multiresolution import BarDomain, BarDefinition, SharedBarEngine, WindowRequest
from trading_research.measurements.common import (
    capture_trade_window, capture_bar_window, validate_trade_window, MeasurementPublisher,
)
from trading_research.measurements.cvd import CohortChannel, CohortDefinition, measure_cohort_cvd
from trading_research.measurements.tape import Trade, TradeLedger
from trading_research.measurements.tape_intensity import measure_tape_intensity
from trading_research.measurements.transaction_reducers import TransactionTapeView
from trading_research.data.transactions import TransactionLedger
from tests.measurement_fixtures import CASES, UNIT, row, ledger, request, capture, gold_capture
from tests.test_transactions import key, value, receipt


class MeasurementCommonTests(unittest.TestCase):
    def test_M_COMMON_001(self):
        view, c = gold_capture("M-COMMON-001")
        expected = literal.flow(CASES["M-COMMON-001"]["inputs"]["trades"])
        w = c.window
        self.assertEqual((w.buy_volume, w.sell_volume, w.unknown_volume, w.signed, w.eligible_volume, w.print_count),
                         tuple(expected[k] for k in ("buy", "sell", "unknown", "signed", "total", "prints")))
        actual = measure_tape_intensity(c, view=view, epsilon=1)
        self.assertEqual((actual.count_per_sec, actual.contracts_per_sec, actual.signed_per_sec), (3, 11, 7))
        self.assertTrue(w.history_complete and w.order_exact)
        validate_trade_window(c, view)
        self.assertEqual(literal.wire(literal.legacy_envelope(CASES["M-COMMON-001"]["inputs"]["trades"],
                         CASES["M-COMMON-001"]["inputs"]["window"])),
                         __import__('trading_research.operations.artifacts', fromlist=['canonical_json']).canonical_json(c.record()))

    def test_M_COMMON_002(self):
        inputs = CASES["M-COMMON-002"]["inputs"]
        view, c = gold_capture("M-COMMON-002")
        with self.assertRaises(ContractError):
            capture_trade_window(view, **{**request(end=10**9), "instrument": "ES.test"})
        changed = [{**r, "aggregation_unit": "aggregated-parent-summary"} if i == 0 else r for i, r in enumerate(inputs["trades"])]
        with self.assertRaises(ContractError):
            capture(changed, end=10**9)
        changed = [{**r, "source_content_version": "a.v2"} if i == 0 else r for i, r in enumerate(inputs["trades"])]
        _, other = capture(changed, end=10**9, max_inputs=64)
        self.assertNotEqual(c.id, other.id)
        later = capture_trade_window(view, **request(end=10**9, published=10**9 + 2, max_inputs=64))
        self.assertNotEqual(c.id, later.id)
        with self.assertRaises(IntegrityError):
            validate_trade_window(replace(c, window=replace(c.window, eligible_volume=1)), view)

    def test_M_COMMON_003(self):
        rows = CASES["M-COMMON-003"]["inputs"]["trades"]
        view, full = capture(rows, end=10**9)
        self.assertEqual(full.window.true_signed_bounds, (-1, 7))
        _, partial = capture(rows, end=10**9, spans=((0, 500000000),))
        self.assertEqual(partial.window.observed_signed_bounds, (-1, 7))
        self.assertIsNone(partial.window.true_signed_bounds)
        for spans, expected, complete in [(((0, 10**9),), 0, True), ((), None, False)]:
            quiet_view, quiet = capture([], end=10**9, spans=spans)
            self.assertEqual(measure_tape_intensity(quiet, view=quiet_view, epsilon=1).count_per_sec, expected)
            self.assertEqual(quiet.window.history_complete, complete)

    def test_M_COMMON_004(self):
        inputs = CASES["M-COMMON-004"]["inputs"]
        view = ledger(inputs["trades"])
        old = capture_trade_window(view, **request(end=10, cut=10))
        before_b = capture_trade_window(view, **request(start=10, end=20, cut=10, spans=()))
        correction = {**inputs["correction"], "replacement": Trade.restore(inputs["correction"]["replacement"])}
        view.correct(**correction)
        a = capture_trade_window(view, **request(end=10, cut=20))
        b = capture_trade_window(view, **request(start=10, end=20, cut=20))
        self.assertEqual((old.window.signed, before_b.window.signed, a.window.signed, b.window.signed), (5, 0, 0, 5))
        self.assertEqual(a.window.correction_ids, ("move",))
        self.assertEqual(b.window.correction_ids, ("move",))
        restored = TradeLedger.restore(view.checkpoint())
        for c in (old, before_b, a, b):
            validate_trade_window(c, restored)

    def test_M_COMMON_005(self):
        rows = CASES["M-COMMON-005"]["inputs"]["trades"]
        definition = CohortDefinition("all", UNIT, (CohortChannel("all", 1, None),))
        for orders, bounds in [((None,) * 3, ((0, 20), (-20, 0))), ((0, 1, 2), ((10, 10), (-10, -10)))]:
            data = [{**r, "order": o} for r, o in zip(rows, orders)]
            view, c = capture(data)
            path = measure_cohort_cvd(c, view=view, definition=definition).paths[0]
            independent = literal.paths(data)
            self.assertEqual((path.high_bounds, path.low_bounds), bounds)
            self.assertEqual((path.high_bounds, path.low_bounds), (independent["high_bounds"], independent["low_bounds"]))
        source = TransactionLedger()
        for i, r in enumerate(rows):
            k = key(r["id"], instrument_key="NQ.test", provider="A" if i != 1 else "B")
            source.admit(receipt(r["id"], r["id"]+"v1", identity=k, known=10,
                data=value(event_at=10, quantity=r["size"], side=r["side"], source_order=i)), actual_completion_at=10)
        view = TransactionTapeView(source)
        c = capture_trade_window(view, **request())
        self.assertFalse(c.window.order_exact)
        self.assertEqual(len(c.window.source_domains), 2)

    def test_M_COMMON_006(self):
        inputs = CASES["M-COMMON-006"]["inputs"]
        rows, spec = inputs["trades"], inputs["window"]
        byte_limit = literal.exact_byte_capacity(rows, spec)
        view, c = capture(rows, end=10**9, max_inputs=3, max_bytes=byte_limit)
        self.assertEqual(len(literal.wire(literal.legacy_envelope(rows, {**spec, "max_bytes": byte_limit}))), byte_limit)
        before = view.checkpoint()
        with self.assertRaises(ContractError):
            capture_trade_window(view, **request(end=10**9, max_inputs=3, max_bytes=byte_limit - 1))
        self.assertEqual(view.checkpoint(), before)
        view.add(Trade.restore(inputs["one_over_trade"]))
        with self.assertRaises(ContractError):
            capture_trade_window(view, **request(end=10**9, max_inputs=3))
        consumed = []
        def endless():
            consumed.append(True)
            yield Trade.restore(rows[0])
        with self.assertRaises(ContractError):
            capture_trade_window(endless(), **request())
        self.assertEqual(consumed, [])

    def test_M_COMMON_007(self):
        rows = [row("p1", at=1, size=2, order=0), row("p2", at=2, price=102, size=3, side=-1, order=0)]
        view = ledger(rows)
        domain = BarDomain("NQ.test", "trades", UNIT)
        definition = BarDefinition(domain, "bar-v1", "calendar-v1", "session-v1")
        engine = SharedBarEngine(domain, (definition,))
        engine.add_many(tuple(view.trades.values()))
        coverage = request(end=10)["coverage"]
        bar = engine.publish_window(engine.capture(10), WindowRequest(definition.id, 0, 10, coverage, Watermark(10, 10, "wm")), published_at=11)
        c = capture_bar_window(engine, bar.version_id, view=view, aggregation_unit=UNIT, published_at=12)
        self.assertEqual((c.window.eligible_volume, c.window.buy_volume, c.window.sell_volume), (5, 2, 3))
        self.assertEqual((bar.summary.sum_pv, bar.summary.sum_p2v), (506, 51212))
        self.assertEqual((bar.summary.open_ticks, bar.summary.high_ticks, bar.summary.low_ticks, bar.summary.close_ticks), (100, 102, 100, 102))
        restored = SharedBarEngine.restore(engine.checkpoint())
        self.assertEqual(c, capture_bar_window(restored, bar.version_id, view=TradeLedger.restore(view.checkpoint()), aggregation_unit=UNIT, published_at=12))
        with self.assertRaises(DependencyUnavailable):
            capture_bar_window(engine, "unknown", view=view, aggregation_unit=UNIT, published_at=12)
        with self.assertRaises(DependencyUnavailable):
            capture_bar_window(engine, bar.version_id, view=view, aggregation_unit=UNIT, published_at=10)
        wrong = ledger([{**rows[0], "price": 99}, rows[1]])
        with self.assertRaises(IntegrityError):
            capture_bar_window(engine, bar.version_id, view=wrong, aggregation_unit=UNIT, published_at=12)
        service = MeasurementPublisher()
        direct = capture_trade_window(view, **request(end=10))
        service.publish(direct, view=view)
        changed = capture_trade_window(view, **request(end=10, spans=((0, 5),)))
        with self.assertRaises(IntegrityError):
            service.publish(changed, view=view)
        activity_def = BarDefinition(domain, "activity", "calendar-v1", "session-v1", "volume", 4)
        active = SharedBarEngine(domain, (activity_def,))
        active.add_many(tuple(view.trades.values()))
        result = active.publish_activity(active.capture(10), activity_def.id, published_at=11)
        with self.assertRaises(DependencyUnavailable):
            capture_bar_window(active, result.completed[0].version_id, view=view, aggregation_unit=UNIT, published_at=12)

    def test_M_CAUSAL_PREFIX_001(self):
        view, old = capture([row("a", at=1, size=5)], end=10)
        view.add(Trade.restore(row("future", at=2, known=20, size=100, side=-1, price=90)))
        validate_trade_window(old, view)
        current = capture_trade_window(view, **request(end=10, cut=20))
        self.assertEqual((old.window.signed, old.window.print_count), (5, 1))
        self.assertEqual(current.window.signed, -95)
        restored = TradeLedger.restore(view.checkpoint())
        validate_trade_window(old, restored)

    def test_f05_ineligible_mass_and_unresolved_condition(self):
        source = TransactionLedger()
        for i, (quantity, eligible) in enumerate(((3, True), (7, False))):
            source.admit(receipt(str(i), f"v{i}", identity=key(str(i), instrument_key="NQ.test"), known=10,
                data=value(quantity=quantity, volume_eligibility=eligible, directional_eligibility=eligible)), actual_completion_at=10)
        c = capture_trade_window(TransactionTapeView(source), **request())
        self.assertEqual((c.window.eligible_volume, c.window.excluded_volume, len(c.window.source_versions)), (3, 7, 2))
        unresolved = TransactionLedger()
        unresolved.admit(receipt(identity=key(instrument_key="NQ.test"), data=value(volume_eligibility=None, directional_eligibility=False)), actual_completion_at=10)
        with self.assertRaises(DependencyUnavailable):
            capture_trade_window(TransactionTapeView(unresolved), **request())
