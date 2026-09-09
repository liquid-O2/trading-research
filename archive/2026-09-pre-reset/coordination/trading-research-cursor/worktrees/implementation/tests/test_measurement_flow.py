from dataclasses import replace
from fractions import Fraction
import unittest

from references import measurement_flow_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.multiresolution import BarDomain, BarDefinition, SharedBarEngine
from trading_research.measurements.common import capture_trade_window
from trading_research.measurements.cvd import (
    measure_cvd, cvd_interval_increment, CohortChannel, CohortDefinition, measure_cohort_cvd,
    fixed_source_cohort, fit_cohort_definition, FlowDecayDefinition, measure_decayed_flow,
)
from tests.measurement_fixtures import CASES, UNIT, row, ledger, request, capture, gold_capture


ALL = CohortDefinition("all", UNIT, (CohortChannel("all", 1, None),))


class MeasurementFlowTests(unittest.TestCase):
    def test_M01_RESET_001(self):
        rows = CASES["M01-RESET-001"]["inputs"]["trades"]
        view = ledger(rows)
        a = measure_cvd(capture_trade_window(view, **request(end=10)), view=view, anchor_id="A")
        b = measure_cvd(capture_trade_window(view, **request(start=10, end=20)), view=view, anchor_id="B")
        whole = measure_cvd(capture_trade_window(view, **request(end=20)), view=view, anchor_id="whole")
        self.assertEqual((a.signed, b.signed, whole.signed), (100, 1, 101))
        with self.assertRaises(ContractError):
            cvd_interval_increment(a, b, view=view)
        with self.assertRaises(ContractError):
            measure_cvd(capture_trade_window(view, **request(end=20)), view=view, anchor_id="whole", opening=100)

    def test_M01_UNKNOWN_001(self):
        view, c = gold_capture("M01-UNKNOWN-001")
        result = measure_cvd(c, view=view, anchor_id="session")
        self.assertEqual((result.buy, result.sell, result.unknown, result.signed, result.known_side_fraction,
                          result.true_signed_bounds), (0, 0, 7, 0, 0, (-7, 7)))

    def test_M01_PATH_001(self):
        inputs = CASES["M01-PATH-001"]["inputs"]
        outputs = []
        for key in ("a", "b"):
            view, c = capture(inputs[key])
            actual = measure_cohort_cvd(c, view=view, definition=ALL).paths[0]
            expected = literal.paths(inputs[key])
            self.assertEqual((actual.close, actual.high_bounds, actual.low_bounds),
                             (expected["close"], expected["high_bounds"], expected["low_bounds"]))
            outputs.append((actual.high_bounds[0], actual.low_bounds[0]))
        self.assertEqual(outputs, [(10, 0), (0, -10)])

    def test_M01_DECAY_001(self):
        view, c = gold_capture("M01-DECAY-001")
        result = measure_decayed_flow(c, view=view, definition=FlowDecayDefinition("event_count", "exponential", 1, "half-life-1"))
        self.assertEqual((result["buy"], result["sell"], result["signed"], result["gross"]), (2, 2, 0, 4))

    def test_M02_OHLC_001(self):
        view, c = gold_capture("M02-OHLC-001")
        actual = measure_cohort_cvd(c, view=view, definition=ALL, openings=(100,), opening_version="literal-offset-100").paths[0]
        expected = literal.paths(CASES["M02-OHLC-001"]["inputs"]["trades"], 100)
        self.assertEqual((actual.open, actual.high_bounds, actual.low_bounds, actual.close),
                         (100, expected["high_bounds"], expected["low_bounds"], 100))
        self.assertEqual((actual.high_at, actual.low_at), (1, 2))
        self.assertEqual(actual.relative, (0, (10, 10), (-10, -10), 0))

    def test_M02_OPEN_001(self):
        view, c = gold_capture("M02-OPEN-001")
        p = measure_cohort_cvd(c, view=view, definition=ALL, openings=(10,), opening_version="offset10").paths[0]
        self.assertEqual((p.open, p.high_bounds, p.low_bounds, p.close, p.high_at, p.low_at, p.high_origin),
                         (10, (10, 10), (6, 6), 6, None, 1, "opening_baseline"))

    def test_M02_PARTITION_001(self):
        view, c = gold_capture("M02-PARTITION-001")
        definition = CohortDefinition("partition6", UNIT, (CohortChannel("low", 1, 6), CohortChannel("high", 6, None)))
        low, high = measure_cohort_cvd(c, view=view, definition=definition).paths
        self.assertEqual((low.buy, low.sell, low.unknown, high.buy, high.sell, high.unknown), (5, 5, 0, 0, 0, 10))
        self.assertEqual(low.volume + high.volume, 20)
        self.assertEqual(high.true_signed_bounds, (-10, 10))

    def test_M02_FIXED_001(self):
        view, c = gold_capture("M02-FIXED-001")
        ny = measure_cohort_cvd(c, view=view, definition=fixed_source_cohort("ny_ge100"))
        london = measure_cohort_cvd(c, view=view, definition=fixed_source_cohort("london_ge75"))
        self.assertEqual((ny.paths[1].volume, ny.paths[1].contributing_prints), (201, 2))
        self.assertEqual((london.paths[1].volume, london.paths[1].contributing_prints), (375, 4))
        self.assertEqual(sum(p.volume for p in ny.paths), 449)
        self.assertEqual(sum(p.volume for p in london.paths), 449)

    def test_M02_BAND_001(self):
        view, c = gold_capture("M02-BAND-001")
        outputs = measure_cohort_cvd(c, view=view, definition=fixed_source_cohort("inclusive30_through60"))
        self.assertEqual((outputs.paths[1].volume, outputs.paths[2].volume, outputs.paths[1].contributing_prints), (90, 61, 2))
        self.assertEqual(outputs.definition.channels[2].role, "excluded_above")

    def test_M02_QUANTILE_001(self):
        view, c = capture([row(str(s), at=s, size=s) for s in (1, 2, 3, 4)], end=8, published=9)
        for weighting, cutoff, lower in (("count", 3, 3), ("volume", 4, 6)):
            fit = fit_cohort_definition((c,), view=view, train_end=10, available_at=11,
                                        probabilities=(Fraction(1, 2),), weighting=weighting)
            self.assertEqual(fit["definition"].channels[1].lower_inclusive, cutoff)
            self.assertEqual(literal.weighted_quantile([1, 2, 3, 4], Fraction(1, 2), volume=weighting == "volume") + 1, cutoff)
            self.assertEqual(fit["realized_volume"][0], lower)
            self.assertEqual(fit["publication_status"], "unpublished")

    def test_M02_FUTURE_001(self):
        view, c = capture([row("early", at=1)], end=10, published=11)
        fit = fit_cohort_definition((c,), view=view, train_end=20, available_at=21, probabilities=(Fraction(1, 2),))
        view2, future_window = capture([row("later", at=20)], start=19, end=22)
        with self.assertRaises(DependencyUnavailable):
            measure_cohort_cvd(future_window, view=view2, definition=fit["definition"])
        _, allowed_time = capture([row("later", at=20)], start=19, end=22)
        with self.assertRaises(ContractError):
            measure_cohort_cvd(allowed_time, view=view2, definition=replace(fit["definition"], available_at=18))

    def test_M02_SOFT_001(self):
        view, c = gold_capture("M02-SOFT-001")
        definition = CohortDefinition("soft", UNIT, (), (10, 20))
        self.assertEqual(definition.weights(15), (Fraction(1, 2),) * 2)
        output = measure_cohort_cvd(c, view=view, definition=definition)
        for p in output.paths:
            self.assertEqual((p.volume, p.close, p.high_bounds, p.low_bounds),
                             (Fraction(15, 2), Fraction(15, 2), (Fraction(15, 2),) * 2, (0, 0)))
        self.assertEqual(sum(p.volume for p in output.paths), 15)

    def test_M02_EMPTY_001(self):
        view, c = capture([])
        p = measure_cohort_cvd(c, view=view, definition=ALL, openings=(7,), opening_version="offset7").paths[0]
        self.assertEqual((p.open, p.high_bounds, p.low_bounds, p.close, p.contributing_prints, p.volume), (7, (7, 7), (7, 7), 7, 0, 0))
        self.assertTrue(p.history_complete)

    def test_M02_AGGREGATION_001(self):
        inputs = CASES["M02-AGGREGATION-001"]["inputs"]
        view, c = capture(inputs["individual_prints"])
        self.assertEqual(measure_cohort_cvd(c, view=view, definition=fixed_source_cohort("london_ge75")).paths[1].volume, 0)
        with self.assertRaises(ContractError):
            capture(inputs["aggregate"])
        aggregate_view = ledger(inputs["aggregate"])
        aggregate = capture_trade_window(aggregate_view, **{**request(), "aggregation_unit": "aggregated-parent-summary"})
        d = fixed_source_cohort("london_ge75", aggregation_unit="aggregated-parent-summary")
        self.assertEqual(measure_cohort_cvd(aggregate, view=aggregate_view, definition=d).paths[1].volume, 80)

    def test_M02_WHOLE_001(self):
        rows = CASES["M02-WHOLE-001"]["inputs"]["trades"]
        view = ledger(rows)
        domain = BarDomain("NQ.test", "trades", UNIT)
        definition = BarDefinition(domain, "whole10", "calendar", "reset", "volume", 10)
        engine = SharedBarEngine(domain, (definition,))
        engine.add_many(tuple(view.trades.values()))
        result = engine.publish_activity(engine.capture(10), definition.id, published_at=11)
        bar = result.completed[0]
        self.assertEqual((bar.summary.volume, bar.overshoot, set(bar.summary.event_ids)), (15, 5, {"a", "b"}))
