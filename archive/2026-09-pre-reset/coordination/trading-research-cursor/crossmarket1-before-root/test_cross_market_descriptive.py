"""Independent cross-market alignment and descriptive fixtures. No raw population."""
from datetime import date, time, timedelta
from pathlib import Path
import math
import tempfile
import unittest

from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.time import MINUTE, NS
from trading_research.operations.artifacts import ArtifactStore
from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact, read_series_tables
from trading_research.research.cross_market_alignment import (
    FAMILY, PROTOCOL_KIND, PriorCarry, backward_join_indices, bar_clocks,
    close_to_close_logreturn, confirmed_pivots, contemporaneous_ratio,
    daily_observation_clock, futures_session_bounds, grid_cuts,
    join_status_name, lagged_mapping_residual, last_available,
    parse_raw_minute_arrays, pivot_scenario_known, priced_ok,
    running_breaches, running_references, scenario_known_at, session_label,
    utc_datetime, volume_unit_for,
)
from trading_research.research.cross_market_descriptive import (
    concordance, date_cells_for_ci, excursion_bundle, future_window,
    independent_date_support, pair_timing_rows,
    reconstruct_joint_event_rows, restore_event_counts, run,
    stages_aligned_for_ci,
)
from trading_research.research.date_statistics import observed_date_statistics


CALENDAR = Path("/workspace/trading-research/configs/cash-rth-calendar-research-v1.json")
NY = "America/New_York"
PROTOCOL = {
    "kind": PROTOCOL_KIND,
    "version": 1,
    "family": FAMILY,
    "cash_calendar": {
        "path": str(CALENDAR),
        "sha256": "f069df0ccbb8318f1c675a05d9deed64ad681ebe1e47dd8573a6b18266665818",
        "size_bytes": 6922,
    },
}


def _t_ms(start_ns, offset):
    return (int(start_ns) + offset * MINUTE) // 1_000_000


def _bars(symbol, start_ns, closes, *, highs=None, lows=None, volume=1.0, instrument=1, year=2020, variant="primary_corrected"):
    n = len(closes)
    t_ms = [_t_ms(start_ns, i) for i in range(n)]
    high = list(highs) if highs is not None else [c + 0.01 if c > 0 else 0.01 for c in closes]
    low = list(lows) if lows is not None else [c - 0.01 if c > 0.01 else c for c in closes]
    return parse_raw_minute_arrays(
        t_ms=t_ms,
        open_=list(closes),
        high=high,
        low=low,
        close=list(closes),
        volume=[volume] * n,
        instrument_id=[instrument] * n,
        symbol=symbol,
        year=year,
        variant=variant,
        file_id=1 if symbol != "NQ" else 2,
        source_sha256="a" * 64,
    )


class ClockAndJoinFixtures(unittest.TestCase):
    def test_bar_start_end_known_at_60_0_120_exact(self):
        start_ms = 1_577_880_000_000
        baseline = bar_clocks(start_ms, latency_after_end_s=60)
        zero = bar_clocks(start_ms, latency_after_end_s=0)
        late = bar_clocks(start_ms, latency_after_end_s=120)
        self.assertEqual(baseline["start_ns"], start_ms * 1_000_000)
        self.assertEqual(baseline["end_ns"], baseline["start_ns"] + MINUTE)
        self.assertEqual(baseline["known_at_ns"], baseline["end_ns"] + 60 * NS)
        self.assertEqual(zero["known_at_ns"], baseline["end_ns"])
        self.assertEqual(late["known_at_ns"], baseline["end_ns"] + 120 * NS)
        self.assertIsNone(baseline["actual_received_at_ns"])
        self.assertEqual(scenario_known_at(baseline["end_ns"], 0), zero["known_at_ns"])
        self.assertEqual(scenario_known_at(baseline["end_ns"], 120), late["known_at_ns"])
        self.assertNotEqual(scenario_known_at(baseline["known_at_ns"], 60), late["known_at_ns"])

    def test_timestamp_above_2_pow_53_roundtrip(self):
        ns = 2 ** 53 + 123
        self.assertGreater(ns, 2 ** 53)
        start_ms = 1_600_000_000_000
        unit = parse_raw_minute_arrays(
            t_ms=[start_ms, start_ms + 60_000],
            open_=[100.0, 100.0], high=[100.0, 100.0], low=[100.0, 100.0], close=[100.0, 100.0],
            volume=[1.0, 1.0], instrument_id=[1, 1], symbol="YM",
        )
        unit.start_ns[0] = ns
        unit.end_ns[0] = ns + MINUTE
        unit.known_at_ns[0] = ns + 2 * MINUTE
        self.assertEqual(int(unit.start_ns[0]), ns)
        self.assertEqual(int(unit.end_ns[0]) - int(unit.start_ns[0]), MINUTE)
        self.assertNotEqual(int(float(ns)), ns)

    def test_delayed_es_cannot_future_join(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        es = _bars("ES", start, [100.0, 101.0])
        cut = int(es.end_ns[0])
        index, status = last_available(es, cut, latency_after_end_s=60)
        self.assertIsNone(index)
        self.assertEqual(status, "missing")
        later = last_available(es, int(es.known_at_ns[0]), latency_after_end_s=60)
        self.assertIsNotNone(later[0])

    def test_equal_nearest_future_excluded(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        unit = _bars("NQ", start, [100.0, 101.0, 102.0])
        known = unit.known_at_ns
        ends = unit.end_ns
        cut = int((known[0] + known[1]) // 2)
        if int(known[1]) - cut == cut - int(known[0]):
            index, status = backward_join_indices(known, cut, ends)
            self.assertEqual(index, 0)
            self.assertNotEqual(index, 1)
            self.assertIn(join_status_name(status), ("fresh", "stale"))
        future_cut = int(known[0] - MINUTE)
        index, status = backward_join_indices(known, future_cut, ends)
        self.assertEqual(index, -1)
        self.assertEqual(join_status_name(status), "missing")

    def test_missing_etf_m1_remains_missing(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        qqq = _bars("QQQ", start + 2 * MINUTE, [100.0, 101.0])
        index, status = last_available(qqq, int(start + MINUTE), latency_after_end_s=0)
        self.assertIsNone(index)
        self.assertEqual(status, "missing")

    def test_daily_close_unknown_clock(self):
        clock = daily_observation_clock(date(2020, 1, 6))
        self.assertIsNone(clock["known_at_ns"])
        self.assertIsNone(clock["verified_known_at_ns"])
        self.assertFalse(clock["causal_feature_eligible"])
        self.assertEqual(clock["clock"], "date_only")
        self.assertFalse(clock["next_open_invented"])


class ReturnVolumeAndPriceFixtures(unittest.TestCase):
    def test_one_and_five_minute_return_100_to_110_is_log_1_1(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        closes = [100.0] + [100.0] * 4 + [110.0]
        unit = _bars("NQ", start, closes)
        one, one_ok = close_to_close_logreturn(unit.close, unit.start_ns, unit.instrument_id, unit.valid, 1)
        five, five_ok = close_to_close_logreturn(unit.close, unit.start_ns, unit.instrument_id, unit.valid, 5)
        self.assertTrue(one_ok[-1])
        self.assertTrue(five_ok[-1])
        self.assertAlmostEqual(float(five[-1]), math.log(1.1), places=15)
        self.assertAlmostEqual(float(one[-1]), math.log(1.1), places=15)
        self.assertFalse(five_ok[3])

    def test_log_excursion_all_above_clamps_down_zero(self):
        bundle = excursion_bundle(100.0, 120.0, 110.0, 115.0)
        self.assertAlmostEqual(bundle["up_log"], math.log(120.0 / 100.0), places=15)
        self.assertEqual(bundle["down_log"], 0.0)
        self.assertAlmostEqual(bundle["path_range_log"], math.log(120.0 / 110.0), places=15)
        self.assertNotAlmostEqual(bundle["path_range_log"], bundle["up_log"] + bundle["down_log"], places=6)
        self.assertGreaterEqual(bundle["up_log"], 0.0)
        self.assertGreaterEqual(bundle["down_log"], 0.0)

    def test_wrong_instrument_roll_missing(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        closes = [100.0] * 6
        unit = parse_raw_minute_arrays(
            t_ms=[_t_ms(start, i) for i in range(6)],
            open_=closes, high=closes, low=closes, close=closes,
            volume=[1.0] * 6, instrument_id=[1, 1, 1, 2, 2, 2],
            symbol="YM",
        )
        ret, ok = close_to_close_logreturn(unit.close, unit.start_ns, unit.instrument_id, unit.valid, 5)
        self.assertFalse(bool(ok[-1]))
        window = future_window(unit, int(unit.start_ns[1]), 5)
        self.assertEqual(window["status"], "roll")
        self.assertIn("raw_contract_transition", window["reasons"])
        self.assertIsNone(window["close"])

    def test_etf_volume_two_shares_not_two_contracts(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        unit = _bars("QQQ", start, [100.0], volume=2.0)
        self.assertEqual(unit.volume_unit, "shares")
        self.assertEqual(float(unit.volume[0]), 2.0)
        self.assertEqual(volume_unit_for("QQQ"), "shares")
        self.assertEqual(volume_unit_for("YM"), "contracts")
        self.assertNotEqual(unit.volume_unit, "contracts")

    def test_native_ym_tick_one_and_etf_cent_not_quarter_rounded(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        ym = _bars("YM", start, [28001.0], highs=[28001.0], lows=[28001.0])
        etf = _bars("SPY", start, [100.01], highs=[100.01], lows=[100.01])
        self.assertEqual(float(ym.close[0]), 28001.0)
        self.assertEqual(float(etf.close[0]), 100.01)
        self.assertNotEqual(100.01, 100.00)
        self.assertNotEqual(100.01, 100.25)

    def test_twenty_day_relative_volume_not_current_day(self):
        carry = PriorCarry()
        for offset in range(20):
            carry.push_day(date(2020, 1, 6) , {630: 1.0}, None, False)
            carry.dates[-1] = date(2019, 12, 2 + offset)
        relative, reason = carry.relative_volume(630, 100.0)
        self.assertIsNone(reason)
        self.assertAlmostEqual(relative, 100.0, places=12)
        self.assertNotAlmostEqual(relative, 100.0 / ((20 * 1.0 + 100.0) / 21.0), places=6)
        short = PriorCarry()
        short.push_day(date(2020, 1, 2), {630: 1.0}, None, False)
        missing, why = short.relative_volume(630, 2.0)
        self.assertIsNone(missing)
        self.assertEqual(why, "insufficient_prior_dates")


class CalendarMappingSmtFixtures(unittest.TestCase):
    def test_dst_and_early_close_calendar(self):
        calendar = CashCalendar(CALENDAR)
        early = calendar.resolve(date(2020, 11, 27), cut=local_timestamp(date(2020, 11, 27), time(0), NY))
        self.assertEqual(early.state, "early_close")
        self.assertEqual(early.close_at, local_timestamp(date(2020, 11, 27), time(13, 0), NY))
        self.assertEqual(session_label(early.close_at - 1, early, NY), "cash_rth")
        self.assertEqual(session_label(early.close_at, early, NY), "other_futures")
        winter = calendar.resolve(date(2020, 1, 6), cut=local_timestamp(date(2020, 1, 6), time(0), NY))
        summer = calendar.resolve(date(2020, 7, 6), cut=local_timestamp(date(2020, 7, 6), time(0), NY))
        winter_open = local_timestamp(date(2020, 1, 6), time(9, 30), NY)
        summer_open = local_timestamp(date(2020, 7, 6), time(9, 30), NY)
        self.assertEqual(winter.open_at, winter_open)
        self.assertEqual(summer.open_at, summer_open)
        winter_utc = utc_datetime(winter_open)
        summer_utc = utc_datetime(summer_open)
        self.assertEqual(winter_utc.hour, 14)
        self.assertEqual(summer_utc.hour, 13)
        self.assertEqual((winter_utc.hour - summer_utc.hour) % 24, 1)
        start, end, _ = futures_session_bounds(winter, NY)
        cuts = grid_cuts(int(start), int(end), 5)
        self.assertEqual(int(cuts[0]), int(start))
        self.assertLess(int(cuts[-1]), int(end))
        self.assertEqual((int(end) - int(start)) % (5 * MINUTE), 0)

    def test_prior_closing_ratio_100_over_10_maps_etf_11_error_two_points(self):
        mapped = lagged_mapping_residual(
            prior_receiver_close=100.0, prior_source_close=10.0,
            current_source=11.0, current_receiver=112.0,
        )
        self.assertEqual(mapped["ratio"], 10.0)
        self.assertEqual(mapped["predicted_receiver"], 110.0)
        self.assertEqual(mapped["residual_receiver_points"], 2.0)
        later = lagged_mapping_residual(
            prior_receiver_close=100.0, prior_source_close=10.0,
            current_source=11.0, current_receiver=200.0,
        )
        self.assertEqual(later["ratio"], 10.0)
        self.assertEqual(later["predicted_receiver"], 110.0)
        self.assertTrue(later["prior_ratio_frozen"])
        missing = lagged_mapping_residual(
            prior_receiver_close=None, prior_source_close=10.0,
            current_source=11.0, current_receiver=112.0,
        )
        self.assertEqual(missing["status"], "undefined")
        ratio = contemporaneous_ratio(112.0, 11.0)
        self.assertTrue(ratio["zero_residual_is_not_validation"])

    def test_running_high_excludes_current(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        highs = [10.0] * 15 + [25.0]
        lows = [9.0] * 16
        closes = [10.0] * 15 + [12.0]
        unit = _bars("ES", start, closes, highs=highs, lows=lows)
        prior_high, prior_low, defined = running_references(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, 15)
        self.assertTrue(bool(defined[-1]))
        self.assertEqual(float(prior_high[-1]), 10.0)
        self.assertNotEqual(float(prior_high[-1]), 25.0)
        high_b, _ = running_breaches(unit.high, unit.low, prior_high, prior_low, defined)
        self.assertTrue(bool(high_b[-1]))

    def test_strict_two_plus_two_pivot_not_known_until_right_two(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        highs = [1.0, 2.0, 10.0, 3.0, 4.0, 9.0]
        lows = [0.5, 1.0, 2.0, 1.5, 1.8, 2.0]
        unit = _bars("NQ", start, [1, 2, 9, 3, 4, 8], highs=highs, lows=lows)
        pivots = confirmed_pivots(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, unit.known_at_ns)
        self.assertTrue(math.isnan(float(pivots["high_level"][2])))
        self.assertTrue(math.isnan(float(pivots["high_level"][3])))
        self.assertFalse(math.isnan(float(pivots["high_level"][4])))
        self.assertEqual(int(pivots["high_known_ns"][4]), int(unit.known_at_ns[4]))
        self.assertFalse(bool(pivots["high_breach"][4]))
        self.assertFalse(bool(pivots["high_breach"][5]))

    def test_source_new_high_receiver_no_own_breach_retained(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        src = _bars("YM", start, [10.0] * 15 + [20.0], highs=[10.0] * 15 + [20.0], lows=[9.0] * 16)
        rcv = _bars("NQ", start, [100.0] * 16, highs=[100.0] * 16, lows=[99.0] * 16)
        sph, spl, sd = running_references(src.high, src.low, src.start_ns, src.instrument_id, src.valid, 15)
        rph, rpl, rd = running_references(rcv.high, rcv.low, rcv.start_ns, rcv.instrument_id, rcv.valid, 15)
        sh, sl = running_breaches(src.high, src.low, sph, spl, sd)
        rh, rl = running_breaches(rcv.high, rcv.low, rph, rpl, rd)
        self.assertTrue(bool(sh[-1]))
        self.assertFalse(bool(rh[-1]))
        self.assertFalse(bool(rl[-1]))
        self.assertTrue(bool(sd[-1]) and bool(rd[-1]))

    def test_no_receiver_and_expiry_future_censor(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        unit = _bars("NQ", start, [100.0] * 3)
        missing = future_window(unit, int(unit.start_ns[0] + 10 * MINUTE), 5)
        self.assertEqual(missing["status"], "no_receiver")
        short = future_window(unit, int(unit.start_ns[0]), 5)
        self.assertEqual(short["status"], "censored")
        self.assertIsNone(short["close"])

    def test_future_one_vs_five_minute_separate(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        closes = [100.0, 101.0, 102.0, 103.0, 110.0, 104.0]
        highs = [100.0, 101.0, 102.0, 103.0, 110.0, 104.0]
        unit = _bars("ES", start, closes, highs=highs, lows=closes)
        one = future_window(unit, int(unit.start_ns[0]), 1)
        five = future_window(unit, int(unit.start_ns[0]), 5)
        self.assertEqual(one["status"], "complete")
        self.assertEqual(five["status"], "complete")
        self.assertEqual(one["close"], 100.0)
        self.assertEqual(five["close"], 110.0)
        self.assertNotEqual(one["close"], five["close"])
        self.assertEqual(one["count"], 1)
        self.assertEqual(five["count"], 5)


class PairingAndStatisticsFixtures(unittest.TestCase):
    def test_different_lag_receiver_ref_not_paired(self):
        left = {
            "event_id": "e1", "horizon_minutes": 5, "receiver_variant": "primary_corrected",
            "anchor_ns": 10, "source_start_ns": 10, "receiver_ref_start_ns": 100,
            "terminal_log": 0.1,
        }
        right = dict(left)
        right["receiver_ref_start_ns"] = 200
        right["terminal_log"] = 0.2
        paired = pair_timing_rows(left, right)
        self.assertEqual(paired["pairing"], "reference_change")
        self.assertTrue(paired["reference_change"])
        self.assertFalse(paired.get("common_reference"))
        same = dict(right)
        same["receiver_ref_start_ns"] = 100
        common = pair_timing_rows(left, same)
        self.assertEqual(common["pairing"], "common_reference")
        self.assertAlmostEqual(common["terminal_contrast"], 0.1, places=15)

    def test_shared_one_vs_one_hundred_same_date_events_balanced(self):
        cells = date_cells_for_ci(
            {"2020-01-06": 1.0, "2020-01-07": 0.0},
            {"2020-01-06": 1, "2020-01-07": 100},
        )
        self.assertEqual(cells["2020-01-06"], 1.0)
        self.assertEqual(cells["2020-01-07"], 0.0)
        stats = observed_date_statistics(
            {"value": cells}, ["2020-01-06", "2020-01-07"],
            estimator="date_mean", seed=20260908, block_length=1,
            replicates=200, confidence=0.95,
            minimum_independent_dates=1, minimum_events=1,
            _retain_replicate_estimates=False,
        )
        metric = stats["metrics"]["value"]
        self.assertAlmostEqual(metric["estimate"], 0.5, places=12)
        restore_event_counts(metric, {"2020-01-06": 1, "2020-01-07": 100})
        self.assertEqual(metric["actual_valid_event_count"], 101)
        self.assertEqual(metric["actual_valid_date_count"], 2)
        self.assertNotAlmostEqual(metric["estimate"], 1.0 / 101.0, places=6)

    def test_original_nq2024_not_doubled(self):
        support = independent_date_support({
            "primary_corrected": {"2024-01-02", "2024-01-03"},
            "original_nq2024_sensitivity": {"2024-01-02", "2024-01-03"},
        })
        self.assertEqual(support["primary_dates"], 2)
        self.assertEqual(support["original_nq2024_dates"], 2)
        self.assertEqual(support["union_if_wrongly_pooled"], 2)
        self.assertEqual(support["independent_support_if_doubled"], 4)
        self.assertFalse(support["doubled"])
        self.assertNotEqual(support["primary_dates"] + support["original_nq2024_dates"],
                            support["union_if_wrongly_pooled"])

    def test_concordance_and_undefined(self):
        self.assertEqual(concordance(1, 1), "concordant")
        self.assertEqual(concordance(1, -1), "discordant")
        self.assertEqual(concordance(1, 0), "zero_receiver")
        self.assertEqual(concordance(1, None), "undefined")


class IntegratedTinyTables(unittest.TestCase):
    def test_integrated_tiny_nearby_source_event_all_horizons_typed_tables(self):
        start = local_timestamp(date(2020, 1, 6), time(9, 30), NY)
        ym_close = [100.0] * 20 + [110.0] + [109.0] * 69
        ym_high = [100.2] * 20 + [110.0] + [109.2] * 69
        ym_low = [99.8] * 20 + [109.0] + [108.8] * 69
        nq_close = [1000.0] * 90
        ym = _bars("YM", start, ym_close, highs=ym_high, lows=ym_low, volume=3.0, instrument=77)
        nq = _bars("NQ", start, nq_close, highs=[1000.1] * 90, lows=[999.9] * 90, volume=4.0, instrument=11)
        admitted = {"kind": "cross_market_admitted_sources_v1", "sources": []}
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / "out", maximum_total_bytes=64 * 1024 * 1024,
                                     maximum_file_bytes=32 * 1024 * 1024)
            store = ArtifactStore(Path(tmp) / "store")
            result = run(
                protocol=PROTOCOL, admitted=admitted, store=store, outputs=outputs,
                selected_years=[2020],
                fixture_units={
                    ("YM", "primary_corrected", 2020): ym,
                    ("NQ", "primary_corrected", 2020): nq,
                },
                fixture_daily=([], []),
                fixture_dates=[date(2020, 1, 6)],
            )
            self.assertTrue(result["passed"])
            self.assertFalse(result["full_family_complete"])
            for key in ("passed", "refs", "counts", "resources", "partition_measurements", "full_family_complete"):
                self.assertIn(key, result)
            joints = reconstruct_joint_event_rows(result["refs"])
            self.assertTrue(joints)
            kinds = {row["event_kind"] for row in joints}
            self.assertTrue(any(kind.startswith("running") for kind in kinds))
            horizons = {row["horizon_minutes"] for row in joints}
            self.assertEqual(horizons, {1, 5, 15, 30, 60})
            self.assertTrue(all(row.get("local_node_presence") is None for row in joints))
            self.assertIn(1, [row.get("direction") for row in joints])
            self.assertGreaterEqual(sum(1 for row in joints if row.get("no_receiver") is False), 5)
            event_tables = list(read_series_tables(result["refs"]["source_events"]))
            self.assertTrue(event_tables)
            clocks = event_tables[0]
            self.assertEqual(str(clocks.schema.field("source_start_ns").type), "int64")
            self.assertEqual(str(clocks.schema.field("source_known_at_0").type), "int64")
            self.assertEqual(str(clocks.schema.field("source_known_at_60").type), "int64")
            self.assertEqual(str(clocks.schema.field("source_known_at_120").type), "int64")
            label_tables = list(read_series_tables(result["refs"]["receiver_labels"]))
            self.assertTrue(label_tables)
            self.assertEqual(str(label_tables[0].schema.field("label_start_ns").type), "int64")
            self.assertEqual(str(label_tables[0].schema.field("horizon_minutes").type), "int64")
            link_tables = list(read_series_tables(result["refs"]["event_links"]))
            self.assertEqual(str(link_tables[0].schema.field("terminal_log").type), "double")
            self.assertIn("results_md", result["refs"])
            self.assertIn("completeness", result["refs"])
            self.assertIn("file_lookup", result["refs"])
            self.assertIn("cpu_seconds", result["resources"])
            self.assertEqual(result["partition_measurements"][0]["year"], 2020)
            self.assertGreater(result["counts"]["source_events"], 0)
            self.assertGreater(result["counts"]["event_links"], 0)
            self.assertNotEqual(result["counts"]["source_events"], result["counts"]["raw_source_rows"])


class ProductionPathCorrections(unittest.TestCase):
    def test_lag_cache_rejects_stale_price(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        unit = _bars("YM", start, [100.0, 101.0])
        cut = int(unit.end_ns[0]) + 180 * NS
        index, status = last_available(unit, cut, latency_after_end_s=60)
        self.assertEqual(status, "stale")
        self.assertFalse(priced_ok(unit, index, status))

    def test_reference_contract_mismatch_excludes_constant_future(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        closes = [100.0] * 8
        unit = parse_raw_minute_arrays(
            t_ms=[_t_ms(start, i) for i in range(8)],
            open_=closes, high=closes, low=closes, close=closes,
            volume=[1.0] * 8, instrument_id=[1, 1, 2, 2, 2, 2, 2, 2],
            symbol="YM",
        )
        window = future_window(unit, int(unit.start_ns[2]), 5, reference_contract_key="YM:1")
        self.assertEqual(window["status"], "roll")
        self.assertIn("reference_contract_mismatch", window["reasons"])
        self.assertIsNone(window["close"])

    def test_pivot_roll_reset_and_right_two_known_clocks(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        highs = [1.0, 2.0, 10.0, 3.0, 4.0, 20.0]
        lows = [0.5, 1.0, 2.0, 1.5, 1.8, 2.0]
        unit = parse_raw_minute_arrays(
            t_ms=[_t_ms(start, i) for i in range(6)],
            open_=[1, 2, 9, 3, 4, 18], high=highs, low=lows, close=[1, 2, 9, 3, 4, 18],
            volume=[1.0] * 6, instrument_id=[1, 1, 1, 1, 1, 2],
            symbol="YM",
        )
        pivots = confirmed_pivots(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid,
            end_ns=unit.end_ns)
        self.assertFalse(math.isnan(float(pivots["high_level"][4])))
        self.assertTrue(math.isnan(float(pivots["high_level"][5])))
        self.assertFalse(bool(pivots["high_breach"][5]))
        known_end = int(pivots["high_known_end_ns"][4])
        self.assertEqual(pivot_scenario_known(known_end, 0), int(unit.end_ns[4]))
        self.assertEqual(pivot_scenario_known(known_end, 60), int(unit.end_ns[4]) + 60 * NS)
        self.assertEqual(pivot_scenario_known(known_end, 120), int(unit.end_ns[4]) + 120 * NS)

    def test_prior_ratio_missing_day_and_new_contract_and_nq_original_separate(self):
        start = local_timestamp(date(2020, 1, 6), time(15, 50), NY)
        nq_p = _bars("NQ", start, [100.0] * 20, year=2020, variant="primary_corrected")
        nq_o = _bars("NQ", start, [101.0] * 20, year=2020, variant="original_nq2024_sensitivity")
        qqq = _bars("QQQ", start, [10.0] * 20, year=2020)
        admitted = {"kind": "cross_market_admitted_sources_v1", "sources": []}
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / "out", maximum_total_bytes=64 * 1024 * 1024,
                                     maximum_file_bytes=32 * 1024 * 1024)
            store = ArtifactStore(Path(tmp) / "store")
            result = run(
                protocol=PROTOCOL, admitted=admitted, store=store, outputs=outputs,
                selected_years=[2020],
                fixture_units={
                    ("NQ", "primary_corrected", 2020): nq_p,
                    ("NQ", "original_nq2024_sensitivity", 2020): nq_o,
                    ("QQQ", "primary_corrected", 2020): qqq,
                },
                fixture_daily=([], []),
                fixture_dates=[date(2020, 1, 6)],
            )
            tables = list(read_series_tables(result["refs"]["mapping"]))
            rows = tables[0].to_pylist()
            variants = {(row["futures_variant"], row["etf_variant"]) for row in rows}
            self.assertIn(("primary_corrected", "primary_corrected"), variants)
            self.assertIn(("original_nq2024_sensitivity", "primary_corrected"), variants)
            self.assertTrue(all(row["status"] == "undefined" for row in rows))
            self.assertTrue(any(row["reason"] in ("previous_day_missing", "no_prior_intended_date") for row in rows))

    def test_twenty_intended_dates_across_year_and_missing_day(self):
        carry = PriorCarry()
        first = date(2019, 12, 16)
        for offset in range(20):
            carry.push_day(first + timedelta(days=offset), {630: 1.0}, None, False, "NQ:1")
        relative, reason = carry.relative_volume(
            630, 100.0, [first + timedelta(days=offset) for offset in range(20)])
        self.assertIsNone(reason)
        self.assertAlmostEqual(relative, 100.0, places=12)
        missing_universe = [first + timedelta(days=offset) for offset in range(19)]
        missing_universe.append(date(2020, 1, 6))
        empty, why = carry.relative_volume(630, 2.0, missing_universe)
        self.assertIsNone(empty)
        self.assertEqual(why, "missing_prior_date")

    def test_missing_smt_is_null_not_neither(self):
        start = local_timestamp(date(2020, 1, 6), time(9, 30), NY)
        ym = _bars("YM", start, [100.0] * 20, highs=[100.0] * 20, lows=[99.0] * 20)
        nq = _bars("NQ", start + 40 * MINUTE, [1000.0] * 10)
        admitted = {"kind": "cross_market_admitted_sources_v1", "sources": []}
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / "out", maximum_total_bytes=64 * 1024 * 1024,
                                     maximum_file_bytes=32 * 1024 * 1024)
            result = run(
                protocol=PROTOCOL, admitted=admitted, store=ArtifactStore(Path(tmp) / "store"),
                outputs=outputs, selected_years=[2020],
                fixture_units={
                    ("YM", "primary_corrected", 2020): ym,
                    ("NQ", "primary_corrected", 2020): nq,
                },
                fixture_daily=([], []),
                fixture_dates=[date(2020, 1, 6)],
            )
            smt = list(read_series_tables(result["refs"]["smt"]))[0].to_pylist()
            unknown = [row for row in smt if row["breach_state"] == "unknown"]
            self.assertTrue(unknown)
            self.assertTrue(all(row["source_own_breach_high"] is None for row in unknown))
            self.assertFalse(any(row["breach_state"] == "neither" and
                                 row["source_own_breach_high"] is None and
                                 row["receiver_own_breach_high"] is None for row in unknown))

    def test_running_15_vs_60_and_receiver_original_groups_separate(self):
        start = local_timestamp(date(2020, 1, 6), time(9, 30), NY)
        es = _bars("ES", start, [100.0] * 70, highs=[100.0] * 69 + [120.0], lows=[99.0] * 70)
        nq_p = _bars("NQ", start, [1000.0] * 70, year=2020, variant="primary_corrected")
        nq_o = _bars("NQ", start, [1001.0] * 70, year=2020, variant="original_nq2024_sensitivity")
        admitted = {"kind": "cross_market_admitted_sources_v1", "sources": []}
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / "out", maximum_total_bytes=64 * 1024 * 1024,
                                     maximum_file_bytes=32 * 1024 * 1024)
            result = run(
                protocol=PROTOCOL, admitted=admitted, store=ArtifactStore(Path(tmp) / "store"),
                outputs=outputs, selected_years=[2020],
                fixture_units={
                    ("ES", "primary_corrected", 2020): es,
                    ("NQ", "primary_corrected", 2020): nq_p,
                    ("NQ", "original_nq2024_sensitivity", 2020): nq_o,
                },
                fixture_daily=([], []),
                fixture_dates=[date(2020, 1, 6)],
            )
            events = list(read_series_tables(result["refs"]["source_events"]))[0].to_pylist()
            looks = {row["lookback_minutes"] for row in events if row["event_kind"].startswith("running")}
            self.assertEqual(looks, {15, 60})
            links = list(read_series_tables(result["refs"]["event_links"]))[0].to_pylist()
            recv_vars = {row["receiver_variant"] for row in links}
            self.assertIn("primary_corrected", recv_vars)
            self.assertIn("original_nq2024_sensitivity", recv_vars)

    def test_all_missing_metrics_retained(self):
        start = local_timestamp(date(2020, 1, 6), time(9, 30), NY)
        ym = _bars("YM", start, [100.0] * 10)
        nq = _bars("NQ", start, [1000.0] * 10)
        admitted = {"kind": "cross_market_admitted_sources_v1", "sources": []}
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / "out", maximum_total_bytes=64 * 1024 * 1024,
                                     maximum_file_bytes=32 * 1024 * 1024)
            result = run(
                protocol=PROTOCOL, admitted=admitted, store=ArtifactStore(Path(tmp) / "store"),
                outputs=outputs, selected_years=[2020],
                fixture_units={
                    ("YM", "primary_corrected", 2020): ym,
                    ("NQ", "primary_corrected", 2020): nq,
                },
                fixture_daily=([], []),
                fixture_dates=[date(2020, 1, 6)],
            )
            payload = read_json_artifact(result["refs"]["statistics"])
            names = " ".join(payload["groups"])
            for name in ("coverage_own_eligible", "coverage_common", "lookback_logret",
                         "relative_volume", "smt_unknown", "terminal_log", "path_range_log"):
                self.assertIn(name, names)

    def test_stage_crossing_future_excluded(self):
        formation = local_timestamp(date(2022, 12, 30), time(10, 0), NY)
        label = local_timestamp(date(2022, 12, 30), time(10, 5), NY)
        maturity = local_timestamp(date(2023, 1, 3), time(10, 0), NY)
        self.assertFalse(stages_aligned_for_ci(formation, label, maturity, date(2022, 12, 30)))
        self.assertTrue(stages_aligned_for_ci(formation, label, label + MINUTE, date(2022, 12, 30)))

    def test_three_cut_known_clocks(self):
        start_ms = 1_577_880_000_000
        unit = parse_raw_minute_arrays(
            t_ms=[start_ms], open_=[100.0], high=[100.0], low=[100.0], close=[100.0],
            volume=[1.0], instrument_id=[1], symbol="YM",
        )
        clocks = unit.ensure_clocks()
        self.assertEqual(int(clocks[0][0]), int(unit.end_ns[0]))
        self.assertEqual(int(clocks[60][0]), int(unit.end_ns[0]) + 60 * NS)
        self.assertEqual(int(clocks[120][0]), int(unit.end_ns[0]) + 120 * NS)
        self.assertNotEqual(int(clocks[0][0]), int(clocks[60][0]))
        self.assertNotEqual(int(clocks[60][0]), int(clocks[120][0]))

