from dataclasses import replace
from decimal import Decimal
from fractions import Fraction
import json
import unittest

from trading_research.data.book import BookReducer
from trading_research.data.events import Quote
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import ActivityBars, BarEngine, Watermark, WindowCoverage, bar_reference
from trading_research.foundations.units import NQ_REFERENCE, Ticks
from trading_research.measurements.auction import bounded_dwell, tpo_reference
from trading_research.measurements.quotes import RecoveryInterval, net_displayed_recovery, quote_metrics, transition_metrics
from trading_research.measurements.tape import Cohort, RowGrid, Trade, TradeLedger, WeightedMoments, cvd_bar, cvd_reference, profile_reference, trade_from_event, value_area, vwap_two_pass
from trading_research.operations.artifacts import canonical_json
from tests.test_market_data import event


def trade(i, price=100, size=1, side=1, *, at=None, known=None, order="known", complete=True):
    at = i + 1 if at is None else at
    return Trade(f"trade:{i}", f"raw-content:{i}", "NQH5", at, at if known is None else known,
                 None if price is None else Ticks(price), size, side, i if order == "known" else None,
                 "provider-reported-trade-record", complete)


def ledger(trades):
    result = TradeLedger()
    for t in trades:
        result.add(t)
    return result


def coverage(start, end, *, cut=None, intervals=None):
    return WindowCoverage("NQH5", start, end, ((start, end),) if intervals is None else intervals,
                          end if cut is None else cut, f"synthetic-coverage:{start}:{end}:{cut}")


ALL = Cohort("all", 1, None, "all-whole-provider-prints-v1", "provider-reported-trade-record")


class FlowAndCohortTests(unittest.TestCase):
    def test_known_cvd_unknown_bounds_and_missing_history_are_different(self):
        values = [trade(0, size=5), trade(1, size=2, side=-1), trade(2, size=4)]
        exact = cvd_reference(values, coverage_complete=True)
        self.assertEqual((exact.signed, exact.total, exact.known_side_fraction), (7, 11, Fraction(1)))
        values += [trade(3, size=9, side=None)]
        observed = cvd_reference(values, coverage_complete=True)
        self.assertEqual((observed.buy, observed.sell, observed.unknown, observed.true_signed_bounds), (9, 2, 9, (-2, 16)))
        self.assertIsNone(cvd_reference(values, coverage_complete=False).true_signed_bounds)
        self.assertIsNone(cvd_reference([replace(values[0], history_complete=False)], coverage_complete=True).true_signed_bounds)
        with self.assertRaises(ContractError):
            cvd_reference([values[0], values[0]], coverage_complete=True)

    def test_cohort_intrabar_path_retains_extrema_despite_zero_close(self):
        values = [trade(0, size=10), trade(1, size=20, side=-1), trade(2, size=10)]
        bar = cvd_bar(values, opening_cvd=30, cohort=ALL, coverage_complete=True)
        self.assertEqual((bar.open, bar.close, bar.high_bounds, bar.low_bounds, bar.high_at, bar.low_at),
                         (30, 30, (40, 40), (20, 20), 1, 2))
        self.assertEqual(bar.relative, (0, 0, (10, 10), (-10, -10)))
        small = replace(ALL, id="small", upper_exclusive=20, definition_version="under20")
        large = replace(ALL, id="large", lower_inclusive=20, definition_version="20plus")
        a, b = [cvd_bar(values, opening_cvd=0, cohort=c, coverage_complete=True) for c in (small, large)]
        self.assertEqual((a.close, b.close, a.close + b.close), (20, -20, bar.close - bar.open))
        empty = cvd_bar(values, opening_cvd=7, cohort=replace(ALL, lower_inclusive=100), coverage_complete=True)
        self.assertEqual((empty.open, empty.close, empty.high_bounds, empty.flow.total), (7, 7, (7, 7), 0))

    def test_unordered_ties_emit_tight_extrema_bounds_not_an_invented_path(self):
        values = [trade(0, size=10, at=10, order=None), trade(1, size=20, side=-1, at=10, order=None), trade(2, size=10, at=10, order=None)]
        bar = cvd_bar(values, opening_cvd=0, cohort=ALL, coverage_complete=True)
        self.assertEqual((bar.close, bar.high_bounds, bar.low_bounds, bar.order_exact), (0, (0, 20), (-20, 0), False))
        self.assertIsNone(bar.high_at)
        with self.assertRaises(DependencyUnavailable):
            cvd_bar([replace(values[0], aggregation_unit="changed-provider-summary")], opening_cvd=0, cohort=ALL, coverage_complete=True)

    def test_corrections_preserve_prior_cuts_and_raw_multiplicity_across_restart(self):
        tape = ledger([trade(0, size=5, at=5), trade(1, size=5, at=5)])
        before = tape.asof(instrument="NQH5", cut=10)
        tape.correct(id="correction", original_id="trade:0", known_at=20, reason="provider correction observed now",
                     replacement=trade(2, size=2, side=-1, at=15, known=20))
        for actual in (tape, TradeLedger.restore(tape.checkpoint())):
            self.assertEqual(actual.asof(instrument="NQH5", cut=10), before)
            self.assertEqual(cvd_reference(actual.asof(instrument="NQH5", cut=20), coverage_complete=True).signed, 3)
            self.assertEqual(cvd_reference(actual.asof(instrument="NQH5", cut=20, start=10), coverage_complete=True).signed, -2)
        broken = json.loads(tape.checkpoint())
        broken["corrections"]["correction"]["original_id"] = "nonexistent"
        with self.assertRaises(IntegrityError):
            TradeLedger.restore(canonical_json(broken))

    def test_off_tick_missing_price_and_gap_preserve_observed_flow(self):
        raw = event(0, action="T", side="B", flags=132, price=100.1, size=7)
        normalized = trade_from_event(raw, terms=NQ_REFERENCE, instrument="NQH5", order=0, history_complete=True)
        self.assertIsNone(normalized.price)
        self.assertEqual(cvd_reference([normalized], coverage_complete=True).signed, 7)
        self.assertIsNone(cvd_reference([normalized], coverage_complete=True).true_signed_bounds)
        p = profile_reference([normalized], grid=RowGrid(1, 0, "g"), anchor_id="a", coverage_complete=False)
        self.assertEqual((p.histogram, p.unpriced_volume, p.total_volume), ({}, 7, 7))


class ProfileAndMomentTests(unittest.TestCase):
    def test_profile_mass_side_bounds_ties_and_untraded_gap(self):
        values = [trade(0, 100, 5), trade(1, 100, 5, -1), trade(2, 104, 3), trade(3, 104, 7, None)]
        p = profile_reference(values, grid=RowGrid(1, 0, "tick-grid"), anchor_id="prior-RTH", coverage_complete=True)
        self.assertEqual(p.histogram, {100:10, 104:10})
        self.assertEqual(p.delta, {100:0, 104:3})
        self.assertEqual(p.delta_bounds[104], (-4, 10))
        v = value_area(p.histogram, fraction=Fraction(7, 10))
        self.assertEqual((v.poc, v.poc_maximizers, v.lower_row, v.upper_row, v.achieved_fraction), (100, (100, 104), 100, 104, Fraction(1)))
        self.assertNotIn(102, p.histogram)
        shifted = profile_reference(values, grid=RowGrid(4, 1, "shifted"), anchor_id="prior-RTH", coverage_complete=True)
        self.assertEqual(shifted.total_volume, p.total_volume)
        self.assertNotEqual(shifted.histogram, p.histogram)

    def test_value_area_fraction_and_expansion_tie_change_geometry_without_changing_mass(self):
        histogram = {99:1, 100:68, 101:1, 102:30}
        a = value_area(histogram, fraction=Fraction(68, 100))
        b = value_area(histogram, fraction=Fraction(70, 100))
        self.assertEqual((a.lower_row, a.upper_row, a.achieved_fraction), (100, 100, Fraction(68, 100)))
        self.assertEqual((b.lower_row, b.upper_row, b.achieved_fraction), (99, 101, Fraction(70, 100)))
        plateau = value_area({1:5, 2:5, 3:5}, fraction=Fraction(7, 10), tie_rule="upper")
        self.assertEqual((plateau.poc, plateau.poc_maximizers, plateau.achieved_fraction), (3, (1, 2, 3), Fraction(1)))
        with self.assertRaises(ContractError):
            value_area({1:-2, 2:5}, fraction=Fraction(7, 10))

    def test_exact_online_and_two_pass_vwap_survive_large_price_small_variance_and_downdates(self):
        big = 10**30
        values = [trade(0, big, 1), trade(1, big + 1, 3), trade(2, big + 2, 2)]
        moments = WeightedMoments()
        for i, t in enumerate(values):
            moments.add(t)
            self.assertEqual((moments.mean, moments.variance), vwap_two_pass(values[:i+1]))
        self.assertEqual(moments.mean, Fraction(6 * big + 7, 6))
        self.assertEqual(moments.variance, Fraction(17, 36))
        restored = WeightedMoments.restore(moments.checkpoint())
        for value in (moments, restored):
            value.remove(values[0].id)
            self.assertEqual((value.mean, value.variance), vwap_two_pass(values[1:]))
            value.remove(values[1].id)
            value.remove(values[2].id)
            self.assertEqual((value.mass, value.mean, value.variance), (0, None, None))
            with self.assertRaises(ContractError):
                value.remove(values[2].id)


class CausalBarTests(unittest.TestCase):
    def test_boundary_tick_empty_valid_interval_and_missing_coverage(self):
        tape = ledger([trade(0, 100, 5, at=1), trade(1, 101, 2, at=10)])
        a = bar_reference(tape, instrument="NQH5", start=0, end=10, cut=11, definition_version="time10", coverage=coverage(0,10), watermark=Watermark(10,11,"w"))
        b = bar_reference(tape, instrument="NQH5", start=10, end=20, cut=21, definition_version="time10", coverage=coverage(10,20), watermark=Watermark(20,21,"w"))
        self.assertEqual((a.volume, b.volume, a.high_ticks, b.open_ticks), (5, 2, 100, 101))
        empty = bar_reference(tape, instrument="NQH5", start=20, end=30, cut=31, definition_version="time10", coverage=coverage(20,30), watermark=Watermark(30,31,"w"))
        missing = bar_reference(tape, instrument="NQH5", start=20, end=30, cut=31, definition_version="time10", coverage=coverage(20,30, intervals=()), watermark=Watermark(30,31,"w"))
        self.assertEqual((empty.volume, empty.open_ticks, empty.high_ticks, empty.final, empty.coverage_complete), (0, None, None, True, True))
        self.assertFalse(missing.coverage_complete)

    def test_unfinished_bar_restart_delayed_publication_and_late_correction_keep_old_versions(self):
        engine = BarEngine(instrument="NQH5", definition_version="time10")
        engine.add(trade(0, 100, 5, at=2))
        provisional = engine.publish(start=0, end=10, cut=5, published_at=6, coverage=coverage(0,10,cut=5,intervals=((0,5),)))
        self.assertFalse(provisional.final)
        restored = BarEngine.restore(engine.checkpoint())
        for actual in (engine, restored):
            actual.add(trade(1, 105, 2, at=8))
            final = actual.publish(start=0,end=10,cut=11,published_at=13,coverage=coverage(0,10),watermark=Watermark(10,11,"w"))
            self.assertEqual((final.volume, final.high_ticks, final.final), (7,105,True))
            self.assertEqual(actual.asof(start=0,end=10,cut=12), provisional)
            actual.ledger.correct(id="late-fix",original_id="trade:1",known_at=20,reason="busted trade")
            current = actual.publish(start=0,end=10,cut=20,published_at=21,coverage=coverage(0,10),watermark=Watermark(10,11,"w"))
            self.assertEqual(actual.asof(start=0,end=10,cut=15), final)
            self.assertEqual((current.volume,current.high_ticks,current.correction_ids), (5,100,("late-fix",)))
        self.assertEqual(engine.checkpoint(), restored.checkpoint())

    def test_identical_higher_timeframe_prices_have_distinct_ids_and_no_early_final(self):
        engine = BarEngine(instrument="NQH5", definition_version="time10")
        engine.add(trade(0, 100, at=1))
        engine.add(trade(1, 100, at=11))
        a = engine.publish(start=0,end=10,cut=10,published_at=10,coverage=coverage(0,10),watermark=Watermark(10,10,"w"))
        b = engine.publish(start=10,end=20,cut=20,published_at=20,coverage=coverage(10,20),watermark=Watermark(20,20,"w"))
        self.assertEqual(a.open_ticks,b.open_ticks)
        self.assertNotEqual(a.bar_id,b.bar_id)
        with self.assertRaises(ContractError):
            Watermark(20,19,"future")
        with self.assertRaises(ContractError):
            coverage(10,20,cut=15)

    def test_unknown_same_timestamp_order_does_not_invent_open_or_close(self):
        tape = ledger([trade(0,100,at=1,order=None),trade(1,105,at=1,order=None)])
        b = bar_reference(tape,instrument="NQH5",start=0,end=10,cut=10,definition_version="d",coverage=coverage(0,10),watermark=Watermark(10,10,"w"))
        self.assertEqual((b.open_ticks,b.close_ticks,b.low_ticks,b.high_ticks,b.order_exact), (None,None,100,105,False))

    def test_giant_trade_activity_threshold_keeps_one_event_and_overshoot(self):
        engine = ActivityBars(kind="volume", threshold=10)
        big = trade(0, size=35)
        bar = engine.add(big)
        self.assertEqual((bar.volume,bar.event_ids,len(engine.completed)), (35,(big.id,),1))
        self.assertIsNone(engine.add(big))
        engine.add(trade(1, size=3))
        restored = ActivityBars.restore(engine.checkpoint())
        for actual in (engine, restored):
            last = actual.boundary(known_at=10,reason="required session boundary")
            self.assertEqual((last.volume,last.threshold_reached),(3,False))
        self.assertEqual(engine.checkpoint(),restored.checkpoint())


class TPOAndQuoteTests(unittest.TestCase):
    def test_tpo_distinct_brackets_and_final_single_print_confirmation(self):
        tape = ledger([trade(0,100,at=1),trade(1,104,at=2),trade(2,100,at=12),trade(3,100,at=15),trade(4,104,at=25)])
        args = dict(instrument="NQH5",start=0,end=30,bracket_ns=10,grid=RowGrid(1,0,"g"),definition_version="tpo-exact",minimum_brackets=3)
        early = tpo_reference(tape,cut=10,coverage=coverage(0,30,cut=10,intervals=((0,10),)),**args)
        final = tpo_reference(tape,cut=30,coverage=coverage(0,30),watermark=Watermark(30,30,"w"),**args)
        self.assertEqual(early.provisional_single_rows,(100,104))
        self.assertEqual(early.confirmed_single_rows,())
        self.assertEqual(final.histogram,{100:2,104:2})
        self.assertEqual(final.confirmed_single_rows,())
        self.assertNotIn(102,final.histogram)

    def test_interpolated_dwell_is_capped_and_unknown_order_is_not_allocated(self):
        tape = ledger([trade(0,100,at=1),trade(1,104,at=20)])
        d = bounded_dwell(tape,instrument="NQH5",start=0,end=30,cut=30,stale_cap_ns=5,grid=RowGrid(1,0,"g"))
        self.assertEqual((d.duration_by_row,d.covered_duration_ns,d.missing_or_stale_duration_ns),(((100,5),(104,5)),10,20))
        ties = ledger([trade(0,100,at=5,order=None),trade(1,104,at=5,order=None)])
        d = bounded_dwell(ties,instrument="NQH5",start=0,end=10,cut=10,stale_cap_ns=5,grid=RowGrid(1,0,"g"))
        self.assertEqual((d.covered_duration_ns,d.uncertain_order_duration_ns),(0,5))

    def test_best_quote_ofi_price_cases_microprice_and_no_trade_double_subtraction(self):
        q = Quote(Decimal(100),Decimal(101),10,20)
        unchanged = quote_metrics(q,replace(q,bid_size=12,ask_size=18))
        self.assertEqual((unchanged.ofi_contracts,unchanged.queue_imbalance,unchanged.microprice_points), (4,Fraction(-1,5),Fraction(502,5)))
        self.assertEqual(quote_metrics(q,replace(q,bid=Decimal("100.5"),bid_size=7)).ofi_contracts,7)
        self.assertEqual(quote_metrics(q,replace(q,bid=Decimal("99.5"),bid_size=7)).ofi_contracts,-10)
        self.assertEqual(quote_metrics(q,replace(q,ask=Decimal("100.5"),ask_size=7)).ofi_contracts,-7)
        self.assertEqual(quote_metrics(q,replace(q,ask=Decimal("101.5"),ask_size=7)).ofi_contracts,20)
        reducer = BookReducer()
        reducer.apply(event(0,ask_size=10))
        t = event(1,action="T",side="B",size=3,ask_size=10,flags=0)
        self.assertIsNone(transition_metrics(t,reducer.apply(t)))
        update = event(2,ask_size=7)
        self.assertEqual(transition_metrics(update,reducer.apply(update)).ofi_contracts,3)
        snapshot_event = event(3,flags=160,ask_size=100)
        self.assertIsNone(transition_metrics(snapshot_event,reducer.apply(snapshot_event)))

    def test_net_displayed_recovery_requires_reconciled_constant_price_and_is_not_gross_refill(self):
        q = Quote(Decimal(100),Decimal(101),10,10)
        interval = RecoveryInterval(q,replace(q,ask_size=7),0,3,("trade","quote"),"reconciled-fixture",True,True,False)
        self.assertEqual(net_displayed_recovery(interval).ask_net_additions,0)
        self.assertEqual(net_displayed_recovery(replace(interval,current=q)).ask_net_additions,3)
        self.assertIsNone(net_displayed_recovery(replace(interval,ordering_certificate_id=None)).ask_net_additions)
        self.assertIsNone(net_displayed_recovery(replace(interval,ask_price_constant=False)).ask_net_additions)
        self.assertIsNone(net_displayed_recovery(replace(interval,hidden_or_unknown_execution=True)).ask_net_additions)


if __name__ == "__main__":
    unittest.main()
