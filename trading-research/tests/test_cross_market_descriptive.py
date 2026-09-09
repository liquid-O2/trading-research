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
    close_to_close_logreturn, confirmed_pivots, confirmed_pivots_reference,
    contemporaneous_ratio, daily_observation_clock, futures_session_bounds,
    grid_cuts, join_status_name, lagged_mapping_residual, last_available,
    parse_raw_minute_arrays, pivot_scenario_known, priced_ok,
    running_breaches, running_references, scenario_known_at, session_label,
    utc_datetime, volume_unit_for,
)
from trading_research.research.cross_market_descriptive import (
    STAT_METRIC_BATCH, _SeriesWriter, _add_cell, _empty_group, add_day_flags, add_day_values,
    concordance, date_cells_for_ci, excursion_bundle, future_window,
    group_key, independent_date_support, pair_timing_rows,
    reconstruct_joint_event_rows, restore_event_counts, run,
    source_event_schema, stages_aligned_for_ci, summarize_groups,
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
    def test_identical_source_minute_aliases_keep_original_addresses_and_volume(self):
        from trading_research.errors import IntegrityError
        from trading_research.research.cross_market_alignment import unit_quality_row
        args = dict(t_ms=[1_600_000_020_000] * 3 + [1_600_000_080_000],
            open_=[100., 100., 100., 101.], high=[102.] * 4, low=[99.] * 4,
            close=[101.] * 4, volume=[7.] * 3 + [11.], instrument_id=[1] * 4,
            symbol='SPY', file_id=27, year=2026)
        unit = parse_raw_minute_arrays(**args)
        self.assertEqual(len(unit), 2)
        self.assertEqual(unit.source_row_count, 4)
        self.assertEqual(unit.identical_source_aliases, ((1, 0), (2, 0)))
        self.assertEqual(unit.volume.tolist(), [7., 11.])
        quality = unit_quality_row(unit)
        self.assertEqual(quality['source_rows'], 4)
        self.assertEqual(quality['identical_source_alias_rows'], 2)
        self.assertEqual(quality['identical_source_aliases'][1], {'row_index': 2, 'first_row_index': 0})
        with self.assertRaisesRegex(IntegrityError, 'conflicting same-time'):
            parse_raw_minute_arrays(**{**args, 'volume': [7., 8., 7., 11.]})
        with self.assertRaisesRegex(IntegrityError, 'conflicting same-time'):
            parse_raw_minute_arrays(**{**args, 'instrument_id': [1, 2, 1, 1]})
        with self.assertRaisesRegex(IntegrityError, 'timestamps decrease'):
            parse_raw_minute_arrays(**{**args, 't_ms': [1_600_000_080_000] + [1_600_000_020_000] * 3})

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
        self.assertEqual(scenario_known_at(baseline["known_at_ns"], 60), late["known_at_ns"])
        self.assertNotEqual(scenario_known_at(baseline["known_at_ns"], 60), baseline["known_at_ns"])

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
            primary = [r for r in joints if r["source_start_ns"] == start + 20 * MINUTE and r["event_kind"] == "running_high" and r["lag_s"] == 60]
            self.assertEqual(len(primary), 5)
            self.assertTrue(all(r["terminal_log"] == 0.0 and r["future_status"] == "complete" for r in primary))
            self.assertTrue(all(r["receiver_ref_start_ns"] == start + 20 * MINUTE for r in primary))
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
        cut = int(unit.end_ns[0]) + 240 * NS
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
            self.assertTrue(all(row["source_own_breach_high"] is None or row["receiver_own_breach_high"] is None for row in unknown))
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


class RootReviewRegression(unittest.TestCase):
    def test_missing_opposition_cannot_establish_source_only(self):
        from trading_research.research.cross_market_descriptive import _breach_state
        self.assertEqual(_breach_state(True, False, True, False, False, False), 'unknown')
        self.assertEqual(_breach_state(False, True, False, False, True, False), 'unknown')
        self.assertEqual(_breach_state(True, True, True, False, False, False), 'source_only')

    def test_mapping_missing_current_day_does_not_reuse_older_close(self):
        from trading_research.research.cross_market_alignment import freeze_previous_closing_ratio
        first = date(2020, 1, 6)
        start = local_timestamp(first, time(15, 50), NY)
        source = _bars('QQQ', start, [10.] * 10)
        receiver = _bars('NQ', start, [100.] * 10)
        cal = CashCalendar(CALENDAR)
        missing_day = date(2020, 1, 7)
        cash = cal.resolve(missing_day, cut=local_timestamp(missing_day, time(0), NY))
        self.assertIsNone(freeze_previous_closing_ratio(source, receiver, cash))

    def test_prior_rth_scale_does_not_compress_missing_day(self):
        carry=PriorCarry()
        carry.push_day(date(2020,1,6), {}, .2, True, 'NQ:1')
        carry.push_day(date(2020,1,7), {}, None, False, 'NQ:1')
        self.assertIsNone(carry.prior_rth_scale('NQ:1', [date(2020,1,7)]))


def _pivot_fields_equal(test, left, right):
    import numpy as np
    for name in left:
        a, b = left[name], right[name]
        if getattr(a, "dtype", None) is not None and a.dtype == object:
            test.assertEqual(list(a), list(b), name)
        elif getattr(a, "dtype", None) is not None and a.dtype == np.bool_:
            test.assertTrue(np.array_equal(a, b), name)
        elif getattr(a, "dtype", None) is not None and np.issubdtype(a.dtype, np.floating):
            test.assertTrue(np.allclose(a, b, equal_nan=True), name)
        else:
            test.assertTrue(np.array_equal(a, b), name)


class PerformanceRepairRegression(unittest.TestCase):
    def test_vector_pivots_match_literal_gap_roll_tie(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        highs = [1.0, 2.0, 10.0, 3.0, 4.0, 10.0, 1.0, 2.0, 12.0, 3.0, 4.0, 20.0]
        lows = [0.4, 0.9, 2.0, 1.4, 1.7, 2.0, 0.3, 0.8, 1.1, 1.0, 1.2, 1.5]
        closes = [1, 2, 9, 3, 4, 8, 1, 2, 11, 3, 4, 18]
        t_ms = [_t_ms(start, i) for i in range(12)]
        t_ms[6:] = [value + 60_000 for value in t_ms[6:]]
        unit = parse_raw_minute_arrays(
            t_ms=t_ms, open_=closes, high=highs, low=lows, close=closes,
            volume=[1.0] * 12, instrument_id=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            symbol="YM",
        )
        kwargs = dict(
            high=unit.high, low=unit.low, start_ns=unit.start_ns,
            instrument_id=unit.instrument_id, valid=unit.valid, end_ns=unit.end_ns,
            contract_key=None,
        )
        vector = confirmed_pivots(**kwargs)
        literal = confirmed_pivots_reference(**kwargs)
        _pivot_fields_equal(self, vector, literal)
        self.assertTrue(math.isnan(float(vector["high_level"][2])))
        self.assertFalse(math.isnan(float(vector["high_level"][4])))
        self.assertTrue(math.isnan(float(vector["high_level"][6])))
        self.assertTrue(math.isnan(float(vector["high_level"][11])))
        tie_highs = [1.0, 2.0, 5.0, 5.0, 4.0, 3.0]
        tie_lows = [0.5, 1.0, 2.0, 2.0, 1.8, 1.5]
        tied = _bars("NQ", start, [1, 2, 5, 5, 4, 3], highs=tie_highs, lows=tie_lows)
        tie_kwargs = dict(
            high=tied.high, low=tied.low, start_ns=tied.start_ns,
            instrument_id=tied.instrument_id, valid=tied.valid, known_at=tied.known_at_ns,
        )
        _pivot_fields_equal(self, confirmed_pivots(**tie_kwargs), confirmed_pivots_reference(**tie_kwargs))

    def test_typed_batch_writer_null_and_int64_clocks(self):
        clock = 2 ** 53 + 777
        self.assertGreater(clock, 2 ** 53)
        self.assertNotEqual(int(float(clock)), clock)
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / "out", maximum_total_bytes=8 * 1024 * 1024,
                                     maximum_file_bytes=4 * 1024 * 1024)
            writer = _SeriesWriter(outputs, "source-events", source_event_schema())
            writer.add_columns({
                "event_id": [1],
                "date": ["2020-01-06"],
                "year": [2020],
                "stage": ["training"],
                "session": ["cash_rth"],
                "source_symbol": ["YM"],
                "source_variant": ["primary_corrected"],
                "event_kind": ["running_high"],
                "lookback_minutes": [15],
                "direction": [1],
                "source_start_ns": [clock],
                "source_end_ns": [clock + MINUTE],
                "source_known_at_0": [clock + MINUTE],
                "source_known_at_60": [clock + 2 * MINUTE],
                "source_known_at_120": [clock + 3 * MINUTE],
                "formation_start_ns": [clock],
                "formation_end_ns": [clock + MINUTE],
                "anchor_ns": [clock],
                "source_close": [100.0],
                "source_file_id": [1],
                "source_instrument_id": [7],
                "source_contract_key": ["YM:7"],
                "actual_received_at_ns": [0],
            }, length=1, nulls={"actual_received_at_ns": [True]})
            writer.add({
                "event_id": 2, "date": "2020-01-06", "year": 2020, "stage": "training",
                "session": "cash_rth", "source_symbol": "YM", "source_variant": "primary_corrected",
                "event_kind": "running_low", "lookback_minutes": 15, "direction": -1,
                "source_start_ns": None, "source_end_ns": None, "source_known_at_0": None,
                "source_known_at_60": None, "source_known_at_120": None,
                "formation_start_ns": None, "formation_end_ns": None, "anchor_ns": None,
                "source_close": None, "source_file_id": 1, "source_instrument_id": None,
                "source_contract_key": None, "actual_received_at_ns": None,
            })
            ref = writer.finish()
            table = list(read_series_tables(ref))[0]
            self.assertEqual(str(table.schema.field("source_start_ns").type), "int64")
            rows = table.to_pylist()
            self.assertEqual(rows[0]["source_start_ns"], clock)
            self.assertIsNone(rows[0]["actual_received_at_ns"])
            self.assertIsNone(rows[1]["source_start_ns"])
            self.assertIsNone(rows[1]["source_close"])

    def test_vector_joins_match_scalar_last_available(self):
        start = local_timestamp(date(2020, 1, 6), time(10, 0), NY)
        unit = _bars("ES", start, [100.0, 101.0, 102.0, 103.0])
        known = unit.known_for(60)
        cuts = [
            int(known[0] - MINUTE),
            int(known[0]),
            int((known[1] + known[2]) // 2),
            int(unit.end_ns[0] + 240 * NS),
            int(known[-1] + MINUTE),
        ]
        idx, status = backward_join_indices(known, cuts, unit.end_ns)
        for i, cut in enumerate(cuts):
            got_i, got_s = last_available(unit, cut, latency_after_end_s=60)
            if got_i is None:
                self.assertEqual(int(idx[i]), -1)
                self.assertEqual(join_status_name(int(status[i])), got_s)
            else:
                self.assertEqual(int(idx[i]), int(got_i))
                self.assertEqual(join_status_name(int(status[i])), got_s)

    def test_grouping_day_values_match_cell_reference(self):
        key = group_key(
            metric="terminal_log", source="YM", receiver="NQ",
            source_variant="primary_corrected", receiver_variant="primary_corrected",
            year=2020, stage="training", session="cash_rth", lookback=15,
            event_kind="running_high", lag=60, horizon=5)
        batches = {
            "2020-01-06": [0.1, None, 0.3, float("nan")],
            "2020-01-07": [None, None],
            "2020-01-08": [0.0, -0.2],
        }
        vector = _empty_group()
        literal = _empty_group()
        store_v = {key: vector}
        store_l = {key: literal}
        for day, values in batches.items():
            add_day_values(store_v, key, day, values)
            for value in values:
                _add_cell(store_l, key, day, value)
        self.assertEqual(dict(store_v[key]["count"]), dict(store_l[key]["count"]))
        self.assertEqual(store_v[key]["count"]["2020-01-06"], 2)
        self.assertNotIn("2020-01-07", store_v[key]["count"])
        self.assertAlmostEqual(store_v[key]["sum"]["2020-01-06"], store_l[key]["sum"]["2020-01-06"], places=15)
        self.assertAlmostEqual(store_v[key]["sum"]["2020-01-08"], -0.2, places=15)
        flags_v = _empty_group()
        flags_l = _empty_group()
        add_day_flags({key: flags_v}, key, "2020-01-06", [True, False, True])
        for value in (1.0, 0.0, 1.0):
            _add_cell({key: flags_l}, key, "2020-01-06", value)
        self.assertEqual(flags_v["count"]["2020-01-06"], 3)
        self.assertEqual(flags_v["sum"]["2020-01-06"], flags_l["sum"]["2020-01-06"])


class RootVectorEndToEndParity(unittest.TestCase):
    def test_all_day_tables_and_date_counts_match_retained_scalar(self):
        import collections
        import trading_research.research.cross_market_descriptive as cm
        class Capture:
            def __init__(self, schema): self.schema, self.rows = schema, []
            def add(self, row): self.rows.append({f.name: row.get(f.name) for f in self.schema})
            def add_columns(self, data, *, length, nulls=None):
                nulls = nulls or {}
                for i in range(length):
                    row = {}
                    for f in self.schema:
                        col = data.get(f.name)
                        value = None if col is None or (f.name in nulls and nulls[f.name][i]) else col[i]
                        if value is not None and hasattr(value, 'item'): value = value.item()
                        if isinstance(value, float) and not math.isfinite(value): value = None
                        row[f.name] = value
                    self.rows.append(row)
            add_arrays = add_columns
            def extend(self, rows):
                for row in rows:self.add(row)
        day = date(2020, 1, 6)
        start = local_timestamp(day, time(9, 30), NY)
        units = {}
        for symbol, base, variant in [('YM',100,'primary_corrected'),('NQ',1000,'primary_corrected'),
                                     ('ES',500,'primary_corrected'),('NQ',1001,'original_nq2024_sensitivity'),
                                     ('QQQ',100,'primary_corrected')]:
            closes = [base + (i % 9) * .1 + i * .01 for i in range(80)]
            unit = _bars(symbol, start, closes, variant=variant)
            units[(symbol,variant,2020)] = unit
        schemas = {'cuts':cm.aligned_cut_schema(), 'smt':cm.smt_schema(), 'lookbacks':cm.lookback_schema(),
                   'mapping':cm.mapping_schema(), 'source_events':cm.source_event_schema(),
                   'receiver_labels':cm.receiver_label_schema(), 'event_links':cm.event_link_schema(),
                   'contrasts':cm.contrast_schema()}
        results=[]
        for method in (cm.process_year_reference, cm.process_year):
            writers={key:Capture(schema) for key,schema in schemas.items()}
            groups=collections.defaultdict(cm._empty_group)
            method(year=2020,units=units,calendar=CashCalendar(CALENDAR),writers=writers,groups=groups,
                   intended_dates=[],carry={},variant_dates={},fixture_dates=[day],event_seq=[1],label_ids={'_next':1})
            results.append((writers,groups))
        def norm(value):
            if isinstance(value,float):return round(value,12)
            return value
        for name in schemas:
            expected=collections.Counter(tuple(norm(r[f.name]) for f in schemas[name]) for r in results[0][0][name].rows)
            actual=collections.Counter(tuple(norm(r[f.name]) for f in schemas[name]) for r in results[1][0][name].rows)
            if expected!=actual:
                self.fail(name+' logical mismatch: '+repr(list((expected-actual).items())[:2])+' vs '+repr(list((actual-expected).items())[:2]))
        self.assertEqual(set(results[0][1]),set(results[1][1]))
        for key in results[0][1]:
            a,b=results[0][1][key],results[1][1][key]
            self.assertEqual(dict(a['count']),dict(b['count']),repr(key))
            for label,total in a['sum'].items():self.assertAlmostEqual(total,b['sum'][label],places=10,msg=repr(key))

    def test_writer_batch_overflow_preserves_pre_shift_int64_values(self):
        import numpy as np
        import trading_research.research.cross_market_descriptive as cm
        with tempfile.TemporaryDirectory() as folder:
            outputs=BoundedOutputs(Path(folder)/'out',maximum_total_bytes=32*1024**2,maximum_file_bytes=16*1024**2)
            writer=cm._SeriesWriter(outputs,'overflow',cm.source_event_schema())
            clocks=np.arange(cm.CHUNK+37,dtype=np.int64)+1600000000000000001
            writer.add_columns({'source_start_ns':clocks},length=len(clocks))
            ref=writer.finish()
            values=[v for t in read_series_tables(ref) for v in t['source_start_ns'].to_pylist()]
            self.assertEqual(values,clocks.tolist())


TABLE_NAMES = (
    "cuts", "lookbacks", "smt", "mapping", "source_events",
    "receiver_labels", "event_links", "contrasts", "date_agg", "daily",
)


def _cash_row(day, symbol, ret):
    return {
        "date": day.isoformat() if isinstance(day, date) else day,
        "symbol": symbol,
        "close": 100.0,
        "adjusted_close": 100.0,
        "raw_log_return": ret,
        "adjusted_log_return": ret,
        "in_primary_cohort": True,
        "file_id": 1,
        "source_sha256": "a" * 64,
        "date_order_ok": True,
        "duplicate": False,
        "gap_not_compressed": True,
    }


def _assert_same_group_stat(test, left, right):
    import trading_research.research.cross_market_descriptive as cm
    test.assertEqual(cm._jsonable(left), cm._jsonable(right))


def _logical_date_agg(rows):
    return {(
        row["date"], row["year"], row["stage"], row["session"],
        row["source_symbol"], row["receiver_symbol"],
        row["source_variant"], row["receiver_variant"],
        row["metric"], row["sum"], row["event_count"], row["date_mean"],
        row["horizon_minutes"], row["lag_s"], row["lookback_minutes"],
        row["event_kind"],
    ) for row in rows}


def _table_rows(ref):
    rows = []
    for table in read_series_tables(ref):
        rows.extend(table.to_pylist())
    return rows


class StatisticalMemoryRepair(unittest.TestCase):
    def test_batched_summarize_matches_unbatched_including_unequal_counts(self):
        import trading_research.research.cross_market_descriptive as cm
        dates = ["2020-01-06", "2020-01-07", "2020-01-08", "2020-01-09",
                 "2020-01-10", "2020-01-13", "2020-01-14", "2020-01-15"]
        groups = {}
        n_metrics = STAT_METRIC_BATCH + 40
        self.assertGreater(n_metrics, STAT_METRIC_BATCH)
        for i in range(n_metrics):
            key = group_key(
                metric=f"batch_metric_{i}", source="YM", receiver="NQ",
                source_variant="primary_corrected", receiver_variant="primary_corrected",
                year=2020, stage="training", session="cash_rth", lookback=15,
                event_kind="running_high", lag=60, horizon=5)
            payload = _empty_group()
            for j, day in enumerate(dates):
                if i == 0:
                    count = 100 if j else 1
                    payload["sum"][day] = 1.0 if j == 0 else 0.0
                    payload["count"][day] = count
                else:
                    payload["sum"][day] = float(i + j)
                    payload["count"][day] = 10
            groups[key] = payload
        empty_key = group_key(
            metric="named_undefined_empty", source="YM", receiver="NQ",
            source_variant="primary_corrected", receiver_variant="primary_corrected",
            year=2020, stage="training", session="cash_rth", lookback=15,
            event_kind="running_high", lag=60, horizon=5)
        groups[empty_key] = _empty_group()
        missing_key = group_key(
            metric="named_undefined_no_intended", source="YM", receiver="NQ",
            source_variant="primary_corrected", receiver_variant="primary_corrected",
            year=2020, stage="training", session="cash_rth", lookback=None,
            event_kind=None, lag=None, horizon=None)
        groups[missing_key] = _empty_group()
        intended = {key: list(dates) for key in groups if key != missing_key}
        calls = {"n": 0}
        original = cm._moving_weights

        def counted(*args, **kwargs):
            calls["n"] += 1
            return original(*args, **kwargs)

        cm._moving_weights = counted
        try:
            batched = summarize_groups(groups, intended, batch_size=STAT_METRIC_BATCH)
            small = summarize_groups(groups, intended, batch_size=32)
            unbatched = summarize_groups(groups, intended, batch_size=max(n_metrics, 1))
        finally:
            cm._moving_weights = original
        self.assertEqual(calls["n"], 3)
        self.assertEqual(set(batched), set(groups))
        self.assertEqual(set(small), set(groups))
        self.assertEqual(set(unbatched), set(groups))
        for key in groups:
            _assert_same_group_stat(self, batched[key], unbatched[key])
            _assert_same_group_stat(self, small[key], unbatched[key])
        unequal = next(key for key in groups if key[0] == "batch_metric_0")
        self.assertEqual(batched[unequal]["actual_valid_event_count"], 1 + 100 * (len(dates) - 1))
        self.assertAlmostEqual(batched[unequal]["statistics"]["estimate"], 1.0 / len(dates), places=12)
        self.assertNotAlmostEqual(
            batched[unequal]["statistics"]["estimate"],
            1.0 / batched[unequal]["actual_valid_event_count"], places=6)
        self.assertEqual(batched[empty_key]["status"], "undefined")
        self.assertEqual(batched[missing_key]["status"], "undefined")
        self.assertEqual(batched[unequal]["statistics"]["bootstrap"]["denominator"], "valid_dates")
        self.assertEqual(batched[unequal]["statistics"]["bootstrap"]["replicates"], 1000)
        self.assertEqual(batched[unequal]["statistics"]["bootstrap"]["seed"], 20260908)
        self.assertEqual(batched[unequal]["statistics"]["bootstrap"]["block_length"], 5)

    def test_public_json_roundtrip_utf8_null_and_named_undefined(self):
        import trading_research.research.cross_market_descriptive as cm
        key = group_key(
            metric="utf8_null_undefined", source="YM", receiver="NQ",
            source_variant="primary_corrected", receiver_variant="primary_corrected",
            year=2020, stage="training", session="cash_rth", lookback=None,
            event_kind=None, lag=None, horizon=None)
        payload = {
            "status": "undefined",
            "reason": "no_matches\x00utf8",
            "actual_valid_event_count": 0,
            "actual_valid_date_count": 0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(
                Path(tmp) / "out", maximum_total_bytes=8 * 1024 * 1024,
                maximum_file_bytes=4 * 1024 * 1024)
            stream = outputs.create("statistics.json")
            stream.write(cm._statistics_json_header())
            cm._statistics_json_append(stream, {key: payload}, True)
            stream.write(cm._statistics_json_footer({
                "primary_dates": 0, "original_nq2024_dates": 0,
                "union_if_wrongly_pooled": 0, "independent_support_if_doubled": 0,
                "doubled": False,
            }))
            stream.close()
            ref = outputs.reference("statistics.json", kind="cross_market_statistics_v1")
            loaded = read_json_artifact(ref)
            self.assertEqual(loaded["kind"], "cross_market_date_statistics_v1")
            self.assertEqual(loaded["seed"], 20260908)
            self.assertIn(str(key), loaded["groups"])
            self.assertEqual(loaded["groups"][str(key)]["status"], "undefined")
            self.assertEqual(loaded["groups"][str(key)]["reason"], "no_matches\x00utf8")
            raw = Path(ref["path"]).read_bytes()
            self.assertIn(b"\\u0000", raw)
            self.assertTrue(raw.decode("utf-8"))

    def test_two_year_tables_groups_and_statistics_match_carry_accounted_runs(self):
        import collections
        import trading_research.research.cross_market_descriptive as cm
        day20 = date(2020, 1, 6)
        day21 = date(2021, 1, 4)
        start20 = local_timestamp(day20, time(9, 30), NY)
        start21 = local_timestamp(day21, time(9, 30), NY)

        def units_for(start, year, ym=100.0, nq=1000.0, qqq=10.0):
            ym_close = [ym] * 20 + [ym * 1.1] + [ym * 1.09] * 69
            nq_close = [nq] * 90
            qqq_close = [qqq] * 90
            return {
                ("YM", "primary_corrected", year): _bars(
                    "YM", start, ym_close, highs=[c + 0.2 for c in ym_close],
                    lows=[c - 0.2 for c in ym_close], volume=3.0, instrument=77, year=year),
                ("NQ", "primary_corrected", year): _bars(
                    "NQ", start, nq_close, highs=[c + 0.1 for c in nq_close],
                    lows=[c - 0.1 for c in nq_close], volume=4.0, instrument=11, year=year),
                ("QQQ", "primary_corrected", year): _bars(
                    "QQQ", start, qqq_close, year=year),
            }

        units20 = units_for(start20, 2020)
        units21 = units_for(start21, 2021, ym=110.0, nq=1100.0, qqq=11.0)
        units_both = {**units20, **units21}
        daily = (
            [_cash_row(day20, "QQQ", 0.01), _cash_row(day21, "QQQ", 0.02)],
            [],
        )
        admitted = {"kind": "cross_market_admitted_sources_v1", "sources": []}
        with tempfile.TemporaryDirectory() as tmp:
            def _run(years, units, dates, folder):
                outputs = BoundedOutputs(
                    Path(tmp) / folder, maximum_total_bytes=64 * 1024 * 1024,
                    maximum_file_bytes=32 * 1024 * 1024)
                return run(
                    protocol=PROTOCOL, admitted=admitted,
                    store=ArtifactStore(Path(tmp) / f"{folder}-store"),
                    outputs=outputs, selected_years=years,
                    fixture_units=units, fixture_daily=daily, fixture_dates=dates,
                )

            joint = _run([2020, 2021], units_both, [day20, day21], "joint")
            only20 = _run([2020], units20, [day20], "y20")
            only21 = _run([2021], units21, [day21], "y21")
            for result in (joint, only20, only21):
                self.assertTrue(result["passed"])
                for name in TABLE_NAMES:
                    self.assertIn(name, result["refs"])
                self.assertIn("source_read", result["resources"]["phases"])
                self.assertIn("measurement", result["resources"]["phases"])
                self.assertIn("date_output", result["resources"]["phases"])
                self.assertIn("stats", result["resources"]["phases"])
                self.assertIn("report", result["resources"]["phases"])
            joint_stats = read_json_artifact(joint["refs"]["statistics"])
            stats20 = read_json_artifact(only20["refs"]["statistics"])
            stats21 = read_json_artifact(only21["refs"]["statistics"])
            self.assertEqual(joint_stats["kind"], "cross_market_date_statistics_v1")
            self.assertEqual(joint_stats["seed"], 20260908)
            self.assertEqual(set(stats20["groups"]), {key for key in joint_stats["groups"] if ", 2020," in key})
            for key, payload in stats20["groups"].items():
                self.assertEqual(payload, joint_stats["groups"][key])
                self.assertNotIn(", 2021,", key)
            self.assertTrue(any(", 2021," in key for key in joint_stats["groups"]))
            self.assertTrue(any("daily_raw_log_return" in key and ", 2020," in key for key in joint_stats["groups"]))
            self.assertTrue(any("daily_raw_log_return" in key and ", 2021," in key for key in joint_stats["groups"]))
            self.assertFalse(any("daily_raw_log_return" in key and ", 2021," in key for key in stats20["groups"]))
            undefined = [key for key, payload in joint_stats["groups"].items()
                         if payload.get("status") == "undefined"]
            self.assertTrue(undefined)
            raw = Path(joint["refs"]["statistics"]["path"]).read_bytes()
            raw.decode("utf-8")
            date20_joint = _logical_date_agg(
                [row for row in _table_rows(joint["refs"]["date_agg"]) if row["year"] == 2020])
            date20_only = _logical_date_agg(_table_rows(only20["refs"]["date_agg"]))
            self.assertEqual(date20_joint, date20_only)
            events20_joint = [row for row in reconstruct_joint_event_rows(joint["refs"])
                              if row.get("date") == "2020-01-06"]
            events20_only = reconstruct_joint_event_rows(only20["refs"])
            def _event_sig(row):
                return (
                    row.get("event_kind"), row.get("horizon_minutes"), row.get("lag_s"),
                    row.get("source_symbol"), row.get("receiver_symbol"),
                    row.get("source_start_ns"), row.get("terminal_log"),
                    row.get("future_status"),
                )
            self.assertEqual(
                collections.Counter(_event_sig(row) for row in events20_joint),
                collections.Counter(_event_sig(row) for row in events20_only))
            carry = {"rel": {}, "ratio": {}}
            intended_all = []
            variant_dates = {}
            event_seq = [1]
            label_ids = {"_next": 1}
            calendar = CashCalendar(CALENDAR)

            class Capture:
                def __init__(self, schema):
                    self.schema, self.rows = schema, []
                def add(self, row):
                    self.rows.append({field.name: row.get(field.name) for field in self.schema})
                def add_columns(self, data, *, length, nulls=None):
                    nulls = nulls or {}
                    for i in range(length):
                        row = {}
                        for field in self.schema:
                            col = data.get(field.name)
                            value = None if col is None or (field.name in nulls and nulls[field.name][i]) else col[i]
                            if value is not None and hasattr(value, "item"):
                                value = value.item()
                            if isinstance(value, float) and not math.isfinite(value):
                                value = None
                            row[field.name] = value
                        self.rows.append(row)
                add_arrays = add_columns
                def extend(self, rows):
                    for row in rows:
                        self.add(row)

            schemas = {
                "cuts": cm.aligned_cut_schema(), "smt": cm.smt_schema(),
                "lookbacks": cm.lookback_schema(), "mapping": cm.mapping_schema(),
                "source_events": cm.source_event_schema(),
                "receiver_labels": cm.receiver_label_schema(),
                "event_links": cm.event_link_schema(), "contrasts": cm.contrast_schema(),
            }
            writers = {name: Capture(schema) for name, schema in schemas.items()}
            groups = collections.defaultdict(cm._empty_group)
            cm._add_daily_groups_for_year(groups, daily[0], 2020)
            cm.process_year(
                year=2020, units=units20, calendar=calendar, writers=writers,
                groups=groups, intended_dates=intended_all, carry=carry,
                variant_dates=variant_dates, fixture_dates=[day20],
                event_seq=event_seq, label_ids=label_ids)
            intended_map = cm._group_intended(
                groups, sorted(set(intended_all)),
                cm._calendar_dates_by_year_stage(sorted(set(intended_all))))
            seq20 = summarize_groups(groups, intended_map)
            for key, payload in seq20.items():
                self.assertEqual(cm._jsonable(payload), stats20["groups"][str(key)])
            groups.clear()
            writers21 = {name: Capture(schema) for name, schema in schemas.items()}
            cm._add_daily_groups_for_year(groups, daily[0], 2021)
            cm.process_year(
                year=2021, units=units21, calendar=calendar, writers=writers21,
                groups=groups, intended_dates=intended_all, carry=carry,
                variant_dates=variant_dates, fixture_dates=[day21],
                event_seq=event_seq, label_ids=label_ids)
            intended_map21 = cm._group_intended(
                groups, sorted(set(intended_all)),
                cm._calendar_dates_by_year_stage(sorted(set(intended_all))))
            seq21 = summarize_groups(groups, intended_map21)
            for key, payload in seq21.items():
                self.assertIn(str(key), joint_stats["groups"])
                self.assertEqual(cm._jsonable(payload), joint_stats["groups"][str(key)])
            mapping21_joint = [row for row in _table_rows(joint["refs"]["mapping"]) if row["year"] == 2021]
            mapping21_only = _table_rows(only21["refs"]["mapping"])
            self.assertTrue(mapping21_joint)
            self.assertTrue(mapping21_only)
            self.assertNotEqual(
                collections.Counter((row["status"], row["reason"]) for row in mapping21_joint),
                collections.Counter((row["status"], row["reason"]) for row in mapping21_only))
            events21_joint = [row for row in reconstruct_joint_event_rows(joint["refs"])
                              if row.get("date") == "2021-01-04"]
            events21_only = reconstruct_joint_event_rows(only21["refs"])
            self.assertTrue(events21_joint)
            self.assertTrue(events21_only)
            self.assertGreater(
                min(int(row["event_id"]) for row in events21_joint),
                max(int(row["event_id"]) for row in events20_only))
            self.assertEqual(min(int(row["event_id"]) for row in events21_only), 1)
