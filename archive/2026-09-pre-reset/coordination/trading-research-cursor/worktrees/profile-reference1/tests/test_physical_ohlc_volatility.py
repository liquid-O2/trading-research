"""Independent fixtures for acquired minute-OHLC physical-volatility measurements.

Expected values are written from the frozen contract equations and literal
arithmetic. They are not copied from the implementation under test.
"""
from datetime import date, time
from pathlib import Path
import math
import unittest

from trading_research.errors import ContractError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.research.ohlc_ranges import MINUTE, MinuteBars
from trading_research.research.physical_ohlc_volatility import (
    FAMILY, PURPOSE, VERSION,
    EXPECTED_ORIGINAL_NQ2024_DATES, EXPECTED_PILOT_DATES,
    EXPECTED_PRIMARY_CASH_DATES_PER_ROOT,
    accepted_pilot_from, ceil_to_minute, close_log_return,
    columns_from_series, computed_partition_record, garman_klass_practical_eq19a,
    history_window_row, history_window_schema, history_window_version,
    interval_estimators, last_published_close,
    measure_remaining, measure_scales, measure_seasonal_cells,
    ohlc_domain_status, overnight_log_gap,
    parkinson_variance, remaining_window_schema, require_protocol,
    realized_variance, rogers_satchell_variance, sample_variance,
    sampled_close_returns, scale_aggregate_schema, seasonal_cell_schema,
    select_partitions, session_bounds, session_measurement_schema,
    signed_semivariances, slice_ohlc, source_version_of, stage_of,
    true_range_ticks, yang_zhang_from_sessions, yang_zhang_k,
)


CALENDAR = Path("/workspace/trading-research/configs/cash-rth-calendar-research-v1.json")
RAW = "NQM20"
M = MINUTE
LN2 = math.log(2.0)


def _columns(rows, *, start0=0):
    result = {key: [] for key in (
        "start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
        "low_ticks", "close_ticks", "volume", "contract_key", "valid")}
    for offset, row in enumerate(rows):
        prices = row[0]
        known = row[1] if len(row) > 1 else start0 + (offset + 1) * M
        contract = row[2] if len(row) > 2 else RAW
        valid = row[3] if len(row) > 3 else True
        start = start0 + offset * M
        values = (start, start + M, known, *prices, 10, contract, valid)
        for key, value in zip(result, values, strict=True):
            result[key].append(value)
    return result


def _lag60(start0, offset):
    return start0 + (offset + 2) * M


def _partition():
    return {
        "root": "NQ", "year": 2020, "variant": "primary_corrected",
        "source_path": "fixture", "source_sha256": "e" * 64,
        "admission_manifest": {"sha256": "f" * 64, "size_bytes": 1, "kind": "m"},
        "canonical_table": {"sha256": "1" * 64, "size_bytes": 1, "kind": "t",
                            "rows": 1, "schema_sha256": "2" * 64},
    }


def _cash(day=date(2020, 1, 6), open_at=2, close_at=3, known_at=1, state="regular"):
    return type("C", (), {"day": day, "state": state, "known_at": known_at,
                          "open_at": open_at, "close_at": close_at})()


def _series(rows, *, start0=0, source_version="independent-physical-vol-fixture-v1"):
    return MinuteBars(_columns(rows, start0=start0), source_version=source_version)


class FormulaFixtures(unittest.TestCase):
    def test_literal_ohlc_100_110_90_105_matches_manual_19a_p_rs(self):
        open_, high, low, close = 100, 110, 90, 105
        hl = math.log(110 / 90)
        co = math.log(105 / 100)
        expected_p = (hl * hl) / (4.0 * LN2)
        expected_gk = 0.5 * hl * hl - (2.0 * LN2 - 1.0) * co * co
        expected_rs = math.log(110 / 100) * math.log(110 / 105) + math.log(90 / 100) * math.log(90 / 105)
        self.assertEqual(ohlc_domain_status(open_, high, low, close), "valid")
        self.assertAlmostEqual(parkinson_variance(high, low)[0], expected_p, places=15)
        self.assertAlmostEqual(garman_klass_practical_eq19a(open_, high, low, close)[0], expected_gk, places=15)
        self.assertAlmostEqual(rogers_satchell_variance(open_, high, low, close)[0], expected_rs, places=15)
        self.assertEqual(parkinson_variance(high, low)[1], "valid")
        self.assertEqual(garman_klass_practical_eq19a(open_, high, low, close)[1], "valid")

    def test_flat_zero_estimators_are_valid_zeros(self):
        for price in (50, 100, 10000):
            estimators = interval_estimators(price, price, price, price)
            self.assertEqual(estimators["ohlc_status"], "valid")
            self.assertEqual(estimators["parkinson"], 0.0)
            self.assertEqual(estimators["garman_klass"], 0.0)
            self.assertEqual(estimators["rogers_satchell"], 0.0)
            self.assertEqual(estimators["log_range"], 0.0)
            self.assertEqual(estimators["price_range_ticks"], 0.0)

    def test_invalid_and_non_positive_domain_never_clipped_to_valid(self):
        self.assertEqual(ohlc_domain_status(100, 90, 110, 105), "invalid_enclosure")
        self.assertEqual(ohlc_domain_status(100, 104, 90, 105), "invalid_enclosure")
        self.assertEqual(ohlc_domain_status(0, 0, 0, 0), "invalid_non_positive")
        self.assertEqual(ohlc_domain_status(-1, 2, -2, 1), "invalid_non_positive")
        self.assertIsNone(garman_klass_practical_eq19a(100, 90, 110, 105)[0])
        self.assertEqual(garman_klass_practical_eq19a(100, 90, 110, 105)[1], "invalid_enclosure")
        open_, high, low, close = 100.0, 200.0, 100.0, 200.0
        value, status = garman_klass_practical_eq19a(open_, high, low, close)
        hl = math.log(2.0)
        expected = 0.5 * hl * hl - (2.0 * LN2 - 1.0) * hl * hl
        self.assertAlmostEqual(value, expected, places=15)
        if expected < 0:
            self.assertEqual(status, "negative_unclipped")
            self.assertLess(value, 0)
        else:
            self.assertEqual(status, "valid")

    def test_scale_times_ten_leaves_log_variances_unchanged(self):
        base = interval_estimators(100, 110, 90, 105)
        scaled = interval_estimators(1000, 1100, 900, 1050)
        for name in ("parkinson", "garman_klass", "rogers_satchell", "log_range", "percentage_range"):
            self.assertAlmostEqual(base[name], scaled[name], places=14)
        self.assertAlmostEqual(scaled["price_range_ticks"], 10 * base["price_range_ticks"], places=12)


class YangZhangAndRvFixtures(unittest.TestCase):
    def test_k_and_sample_variance_use_declared_n_and_ddof_1(self):
        self.assertAlmostEqual(yang_zhang_k(2), 0.34 / (1.34 + 3.0 / 1.0), places=15)
        self.assertAlmostEqual(yang_zhang_k(20), 0.34 / (1.34 + 21.0 / 19.0), places=15)
        self.assertAlmostEqual(yang_zhang_k(60), 0.34 / (1.34 + 61.0 / 59.0), places=15)
        self.assertAlmostEqual(yang_zhang_k(120), 0.34 / (1.34 + 121.0 / 119.0), places=15)
        with self.assertRaises(ContractError):
            yang_zhang_k(1)
        values = (1.0, 3.0, 5.0)
        mean = 3.0
        expected = ((1.0 - mean) ** 2 + (3.0 - mean) ** 2 + (5.0 - mean) ** 2) / 2.0
        self.assertAlmostEqual(sample_variance(values), expected, places=15)
        self.assertIsNone(sample_variance((1.0,)))

    def test_opening_only_gap_has_zero_p_gk_and_positive_yz_open_var(self):
        first = yang_zhang_from_sessions((100,), (100,), (100,), (100,), (100,))
        self.assertEqual(first["status"], "n_le_1")
        result = yang_zhang_from_sessions(
            (100, 110), (100, 110), (100, 110), (100, 110), (100, 100),
        )
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["n_declared"], 2)
        self.assertAlmostEqual(parkinson_variance(110, 110)[0], 0.0, places=15)
        self.assertAlmostEqual(garman_klass_practical_eq19a(110, 110, 110, 110)[0], 0.0, places=15)
        opening = (math.log(100 / 100), math.log(110 / 100))
        mean = sum(opening) / 2.0
        expected_open = ((opening[0] - mean) ** 2 + (opening[1] - mean) ** 2) / 1.0
        self.assertGreater(result["open_var"], 0.0)
        self.assertAlmostEqual(result["open_var"], expected_open, places=15)
        self.assertAlmostEqual(result["close_var"], 0.0, places=15)
        self.assertAlmostEqual(result["rs_mean"], 0.0, places=15)
        k = 0.34 / (1.34 + 3.0)
        self.assertAlmostEqual(result["k"], k, places=15)
        self.assertAlmostEqual(result["yang_zhang"], expected_open, places=15)

    def test_missing_middle_intended_session_does_not_compress_n(self):
        complete = {
            "date": "2020-01-02", "session": "cash_rth", "status": "complete",
            "estimators_valid": True, "contract_key": RAW, "open_ticks": 100,
            "high_ticks": 101, "low_ticks": 99, "close_ticks": 100,
            "previous_close_ticks": 99, "parkinson": 0.0, "garman_klass": 0.0,
            "rogers_satchell": 0.0, "log_range": 0.0, "true_range_ticks": 2.0,
        }
        missing = {
            "date": "2020-01-03", "session": "cash_rth", "status": "missing_input",
            "estimators_valid": False, "contract_key": None, "open_ticks": None,
            "high_ticks": None, "low_ticks": None, "close_ticks": None,
            "previous_close_ticks": None, "parkinson": None, "garman_klass": None,
            "rogers_satchell": None, "log_range": None, "true_range_ticks": None,
        }
        later = dict(complete, date="2020-01-06", previous_close_ticks=None)
        partition = {
            "root": "NQ", "year": 2020, "variant": "primary_corrected",
            "source_path": "x", "source_sha256": "a" * 64,
            "admission_manifest": {"sha256": "b" * 64, "size_bytes": 1, "kind": "m"},
            "canonical_table": {"sha256": "c" * 64, "size_bytes": 1, "kind": "t",
                                "rows": 1, "schema_sha256": "d" * 64},
        }
        cash = type("C", (), {"day": date(2020, 1, 6), "state": "regular",
                              "known_at": 1, "open_at": 2, "close_at": 3})()
        row = history_window_row(later, 2, "measurement_including_current",
                                 [complete, missing, later][-2:], partition, "src", cash)
        self.assertEqual(row["n_declared"], 2)
        self.assertNotEqual(row["n_valid"], 2)
        self.assertFalse(row["applicable"])
        self.assertIsNone(row["yang_zhang"])
        self.assertIsNone(row["mean_true_range_ticks"])
        self.assertIn("missing", row["status"])

    def test_roll_nulls_previous_close_and_gap(self):
        self.assertIsNone(overnight_log_gap(110, None))
        self.assertIsNone(close_log_return(110, None))
        self.assertIsNone(true_range_ticks(110, 90, None))
        self.assertAlmostEqual(overnight_log_gap(110, 100), math.log(1.1), places=15)
        self.assertAlmostEqual(true_range_ticks(110, 90, 80), max(20, 30, 10), places=12)

    def test_semivariances_sum_to_rv_and_exclude_zeros(self):
        returns = (0.1, -0.2, 0.0, 0.3)
        rv, up, down = signed_semivariances(returns)
        expected_rv = 0.1 ** 2 + 0.2 ** 2 + 0.0 + 0.3 ** 2
        self.assertAlmostEqual(rv, expected_rv, places=15)
        self.assertAlmostEqual(up, 0.1 ** 2 + 0.3 ** 2, places=15)
        self.assertAlmostEqual(down, 0.2 ** 2, places=15)
        self.assertAlmostEqual(up + down, rv, places=15)

    def test_alternating_closes_rv_exceeds_terminal_variance(self):
        closes = (100, 110, 100, 110)
        adjacent = (True, True, True)
        returns = sampled_close_returns(closes, adjacent)
        rv = realized_variance(returns)
        terminal = math.log(110 / 100) ** 2
        self.assertGreater(rv, terminal)
        self.assertAlmostEqual(rv, 3.0 * math.log(1.1) ** 2, places=15)
        broken = sampled_close_returns(closes, (True, False, True))
        self.assertEqual(len(broken), 2)
        self.assertAlmostEqual(realized_variance(broken), 2.0 * math.log(1.1) ** 2, places=15)


class ClockAndCalendarFixtures(unittest.TestCase):
    def test_final_bar_known_cut_plus_60s_is_target_begin(self):
        end = 10 * M
        known = end + M
        self.assertEqual(ceil_to_minute(known), known)
        self.assertEqual(ceil_to_minute(end + 1), end + M)
        self.assertEqual(ceil_to_minute(end), end)

    def test_futures_23h_window_is_distinct_from_rth(self):
        calendar = CashCalendar(CALENDAR)
        cash = calendar.resolve(date(2020, 3, 9), cut=local_timestamp(date(2020, 3, 9), time(0), calendar.zone))
        rth0, rth1, _ = session_bounds(cash, "cash_rth", calendar.zone)
        fut0, fut1, _ = session_bounds(cash, "futures_wallclock_18_17", calendar.zone)
        pre0, pre1, _ = session_bounds(cash, "pre_rth_06_0930", calendar.zone)
        self.assertEqual(rth0, cash.open_at)
        self.assertEqual(rth1, cash.close_at)
        self.assertEqual(fut0, local_timestamp(date(2020, 3, 8), time(18, 0), calendar.zone))
        self.assertEqual(fut1, local_timestamp(date(2020, 3, 9), time(17, 0), calendar.zone))
        self.assertEqual((fut1 - fut0) // M, 23 * 60)
        self.assertEqual((rth1 - rth0) // M, 6 * 60 + 30)
        self.assertNotEqual((fut0, fut1), (rth0, rth1))
        self.assertEqual(pre0, local_timestamp(date(2020, 3, 9), time(6, 0), calendar.zone))
        self.assertEqual(pre1, local_timestamp(date(2020, 3, 9), time(9, 30), calendar.zone))

    def test_early_close_and_dst_use_actual_calendar(self):
        calendar = CashCalendar(CALENDAR)
        early = calendar.resolve(date(2020, 11, 27), cut=local_timestamp(date(2020, 11, 27), time(0), calendar.zone))
        self.assertEqual(early.state, "early_close")
        self.assertEqual(early.close_at, local_timestamp(date(2020, 11, 27), time(13, 0), calendar.zone))
        self.assertEqual((early.close_at - early.open_at) // M, 3 * 60 + 30)
        thanksgiving = calendar.resolve(date(2020, 11, 26), cut=local_timestamp(date(2020, 11, 26), time(0), calendar.zone))
        self.assertEqual(thanksgiving.state, "closed")
        before = calendar.resolve(date(2020, 3, 6), cut=local_timestamp(date(2020, 3, 6), time(0), calendar.zone))
        after = calendar.resolve(date(2020, 3, 9), cut=local_timestamp(date(2020, 3, 9), time(0), calendar.zone))
        self.assertNotEqual(before.open_at % (24 * 3600 * 1_000_000_000),
                            after.open_at % (24 * 3600 * 1_000_000_000))
        self.assertEqual(stage_of(date(2020, 6, 1)), "training")
        self.assertEqual(stage_of(date(2023, 6, 1)), "development")
        self.assertEqual(stage_of(date(2025, 6, 1)), "confirmation")


class SchemaAndProtocolFixtures(unittest.TestCase):
    def test_row_schemas_are_nullable_int64_for_ticks_and_timestamps(self):
        import pyarrow as pa
        for schema in (session_measurement_schema(), history_window_schema(),
                       scale_aggregate_schema(), seasonal_cell_schema(), remaining_window_schema()):
            for field in schema:
                self.assertTrue(field.nullable, field.name)
            for name in ("open_ticks", "high_ticks", "low_ticks", "close_ticks",
                         "formation_start_ns", "formation_end_ns", "known_at_ns",
                         "year", "expected_minutes", "observed_minutes"):
                if name in schema.names:
                    self.assertEqual(schema.field(name).type, pa.int64(), name)
            self.assertIn("purpose", schema.names)
            self.assertIn("family_complete", schema.names)
        history = history_window_schema()
        for name in ("source_lineage", "decision_cut_ns", "causal_feature_eligible", "stage_purge"):
            self.assertIn(name, history.names)
        remaining = remaining_window_schema()
        for name in ("join_eligible", "horizon_censored", "observed_input_known_at_ns",
                     "nominal_target_end_ns", "actual_observed_end_ns", "full_target_complete"):
            self.assertIn(name, remaining.names)
        scale = scale_aggregate_schema()
        for name in ("n_full_length_bars", "n_scale_full_complete", "n_short_bars",
                     "scale_full_complete", "mean_garman_klass", "mean_rogers_satchell"):
            self.assertIn(name, scale.names)

    def test_source_hashes_and_purpose_are_preserved_without_context_claim(self):
        partition = {
            "root": "NQ", "year": 2020, "variant": "primary_corrected",
            "source_path": "quantpad/cme__nq-continuous-futures__ohlcv-1m/2020.parquet",
            "source_sha256": "9aefce4864bf0b799d6e1ea8ba60646226a5561d63fda0ba9b84f3c73e2e3714",
            "admission_manifest": {"sha256": "d68bc488a32ea36d22a0fba2fc459a058c0ddefdde571e8fbac3baadce8f8917",
                                   "size_bytes": 1504, "kind": "jumbo_complete_ohlc_admission"},
            "canonical_table": {"sha256": "2fa2edae74cadf9f01e312a30e74024dd56021b32e9d06bb3a99743b40c07e87",
                                "size_bytes": 12772512, "kind": "jumbo_canonical_ohlc_parquet",
                                "rows": 346579, "schema_sha256": "da0eeab2ca0f5dd4a8690b03e00d382e003072b71f06c08474b60c37ef289f45"},
        }
        digest = source_version_of(partition)
        again = source_version_of(partition)
        self.assertEqual(digest, again)
        self.assertEqual(len(digest), 64)
        other = source_version_of({**partition, "year": 2021})
        self.assertNotEqual(digest, other)
        self.assertIn("not a Context", PURPOSE)
        self.assertIn("Location", PURPOSE)
        self.assertFalse(any(token in PURPOSE.lower() for token in ("fitted context", "location quality complete")))
        self.assertEqual(FAMILY, "Research-Physical-OHLC-Volatility-acquired-v1")
        self.assertEqual(VERSION, "physical-ohlc-volatility-acquired-v1")

    def test_original_variant_is_not_an_independent_sample_in_selection(self):
        protocol = {
            "kind": "physical_ohlc_volatility_measurement_contract_v1",
            "version": 1,
            "family": FAMILY,
            "full_family_complete": False,
            "measurement_equations": {
                "garman_klass_practical_eq19a": "0.5ln(H/L)^2-(2ln2-1)ln(C/O)^2",
                "parkinson": "ln(H/L)^2/(4ln2)",
                "rogers_satchell": "ln(H/O)*ln(H/C)+ln(L/O)*ln(L/C)",
                "yang_zhang": "sample_var(log(O/Cprev),ddof1)+k*sample_var(log(C/O),ddof1)+(1-k)*mean(RS); k=.34/(1.34+(n+1)/(n-1)); n>1 contiguous intended sessions",
            },
            "canonical_partitions": [
                {"root": "ES", "year": year, "variant": "primary_corrected"} for year in range(2020, 2027)
            ] + [
                {"root": "NQ", "year": year, "variant": "primary_corrected"} for year in range(2020, 2027)
            ] + [
                {"root": "NQ", "year": 2024, "variant": "original_nq2024_sensitivity"},
            ],
        }
        require_protocol(protocol)
        pilot = select_partitions(protocol, "pilot")
        self.assertEqual(len(pilot), 1)
        self.assertEqual((pilot[0]["root"], pilot[0]["year"], pilot[0]["variant"]),
                         ("NQ", 2020, "primary_corrected"))
        full = select_partitions(protocol, "full", {
            "refs": {"session_measurements": {"path": "/explicit/ref.parquet"}},
            "computed_partitions": [{"root": "NQ", "year": 2020, "variant": "primary_corrected"}],
        })
        self.assertEqual(len(full), 15)
        reused = [row for row in full if row.get("_reuse")]
        originals = [row for row in full if row["variant"] == "original_nq2024_sensitivity"]
        self.assertEqual(len(reused), 1)
        self.assertEqual(reused[0]["year"], 2020)
        self.assertEqual(len(originals), 1)
        self.assertFalse(originals[0].get("_reuse"))
        self.assertEqual(full[-1]["variant"], "original_nq2024_sensitivity")
        with self.assertRaises(ContractError):
            accepted_pilot_from({"accepted_pilot": "search-the-disk"})
        with self.assertRaises(ContractError):
            accepted_pilot_from({"accepted_pilot": {"path": "/tmp/physical-vol-search"}})
        self.assertIsNone(accepted_pilot_from({}))
        self.assertEqual(EXPECTED_PRIMARY_CASH_DATES_PER_ROOT, 1676)
        self.assertEqual(EXPECTED_ORIGINAL_NQ2024_DATES, 252)
        self.assertEqual(EXPECTED_PILOT_DATES, 253)
        record = computed_partition_record(_partition(), "src-version")
        self.assertEqual(record["root"], "NQ")
        self.assertIn("source_sha256", record)
        self.assertIn("canonical_table", record)

    def test_accepted_pilot_does_not_search_disk(self):
        with self.assertRaises(ContractError):
            accepted_pilot_from({"accepted_pilot": {"glob": "**/*physical*"}})
        payload = accepted_pilot_from({
            "accepted_pilot": {
                "refs": {"session_measurements": {"path": "/explicit/ref.parquet"}},
                "computed_partitions": [{"root": "NQ", "year": 2020, "variant": "primary_corrected"}],
                "source_versions": [{"partition": ["NQ", 2020, "primary_corrected"], "source_version": "pilot"}],
            }
        })
        self.assertEqual(payload["refs"]["session_measurements"]["path"], "/explicit/ref.parquet")
        self.assertEqual(payload["source_versions"][0]["source_version"], "pilot")


class MinutePathFixtures(unittest.TestCase):
    def test_missing_interior_bar_is_unknown_not_zero_and_does_not_bridge(self):
        start0 = 1_000 * M
        columns = {key: [] for key in (
            "start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
            "low_ticks", "close_ticks", "volume", "contract_key", "valid")}
        for minute, prices in ((0, (100, 101, 99, 100)), (2, (110, 111, 109, 110))):
            start = start0 + minute * M
            values = (start, start + M, start + 2 * M, *prices, 10, RAW, True)
            for key, value in zip(columns, values, strict=True):
                columns[key].append(value)
        series = MinuteBars(columns, source_version="gapped-fixture")
        cols = columns_from_series(series)
        ohlc, reasons, _, _, expected = slice_ohlc(cols, start0, start0 + 3 * M)
        self.assertIsNone(ohlc)
        self.assertEqual(expected, 3)
        self.assertIn("missing_interior_minutes", reasons)
        self.assertEqual(sampled_close_returns((100, 110), (False,)), ())

    def test_remaining_target_starts_at_last_known_plus_lag(self):
        calendar = CashCalendar(CALENDAR)
        day = date(2020, 1, 2)
        cash = calendar.resolve(day, cut=local_timestamp(day, time(0), calendar.zone))
        open_ns = cash.open_at
        rows = []
        price = 100
        for index in range(30):
            o = price
            c = price + (1 if index % 2 == 0 else -1)
            rows.append(((o, max(o, c) + 1, min(o, c) - 1, c), _lag60(open_ns, index), RAW, True))
            price = c
        series = MinuteBars(_columns(rows, start0=open_ns), source_version="remaining-fixture")
        cols = columns_from_series(series)
        session_row = {"session": "cash_rth", "contract_key": RAW, "window_version": series.window(open_ns, open_ns + 30 * M).version}
        partition = {
            "root": "NQ", "year": 2020, "variant": "primary_corrected",
            "source_path": "fixture", "source_sha256": "e" * 64,
            "admission_manifest": {"sha256": "f" * 64, "size_bytes": 1, "kind": "m"},
            "canonical_table": {"sha256": "1" * 64, "size_bytes": 1, "kind": "t",
                                "rows": 1, "schema_sha256": "2" * 64},
        }
        remaining = measure_remaining(cols, series, cash, session_row, partition, "src", calendar.zone)
        cut5 = [row for row in remaining if row["cut_minutes_after_open"] == 5 and row["target_kind"] == "forward_5"]
        self.assertEqual(len(cut5), 1)
        prefix_last_end = open_ns + 5 * M
        known = prefix_last_end + M
        self.assertEqual(cut5[0]["target_start_ns"], ceil_to_minute(known))
        self.assertEqual(cut5[0]["known_at_ns"], known)
        self.assertEqual(cut5[0]["observed_input_known_at_ns"], known)
        self.assertTrue(cut5[0]["prefix_complete"])
        self.assertEqual(cut5[0]["first_passage_claim"], "none; OHLC extrema only")
        self.assertIn("purpose", cut5[0])
        ref, contract, ref_known = last_published_close(cols, open_ns, prefix_last_end)
        self.assertEqual(contract, RAW)
        self.assertEqual(cut5[0]["reference_close_ticks"], ref)
        self.assertEqual(cut5[0]["reference_known_at_ns"], ref_known)


class SameRangeDifferentTerminal(unittest.TestCase):
    def test_same_high_low_different_close_separates_parkinson_from_close_variance(self):
        a = interval_estimators(100, 110, 90, 100)
        b = interval_estimators(100, 110, 90, 105)
        self.assertAlmostEqual(a["parkinson"], b["parkinson"], places=15)
        self.assertAlmostEqual(a["log_range"], b["log_range"], places=15)
        self.assertNotAlmostEqual(a["garman_klass"], b["garman_klass"], places=12)
        self.assertNotAlmostEqual(math.log(100 / 100) ** 2, math.log(105 / 100) ** 2)


class DomainGapAndTrueRangeFixtures(unittest.TestCase):
    def test_negative_opening_and_closing_gap_are_valid_logs(self):
        self.assertAlmostEqual(overnight_log_gap(90, 100), math.log(0.9), places=15)
        self.assertAlmostEqual(close_log_return(90, 100), math.log(0.9), places=15)
        self.assertLess(overnight_log_gap(90, 100), 0)
        self.assertLess(close_log_return(90, 100), 0)
        self.assertEqual(ohlc_domain_status(90, 90, 100, 100), "invalid_enclosure")

    def test_true_range_prev_above_and_below_range_keeps_gap(self):
        self.assertAlmostEqual(true_range_ticks(110, 90, 120), max(20, 10, 30), places=12)
        self.assertAlmostEqual(true_range_ticks(110, 90, 80), max(20, 30, 10), places=12)
        self.assertEqual(ohlc_domain_status(110, 110, 90, 120), "invalid_enclosure")
        self.assertEqual(ohlc_domain_status(110, 110, 90, 80), "invalid_enclosure")

    def test_negative_opening_yz_is_valid(self):
        result = yang_zhang_from_sessions(
            (100, 90), (100, 90), (100, 90), (100, 90), (100, 100),
        )
        self.assertEqual(result["status"], "valid")
        opening = (math.log(100 / 100), math.log(90 / 100))
        mean = sum(opening) / 2.0
        expected_open = ((opening[0] - mean) ** 2 + (opening[1] - mean) ** 2) / 1.0
        self.assertAlmostEqual(result["open_var"], expected_open, places=15)
        self.assertGreater(result["open_var"], 0.0)


class HistoryLineageAndCausalFixtures(unittest.TestCase):
    def _session(self, day, start, end, known, *, close=100, contract=RAW, year=2020,
                 source="a" * 64, canonical="c" * 64, admission="b" * 64, variant="primary_corrected",
                 window_version="win-a", previous_close=99, tr=2.0):
        return {
            "date": day, "session": "cash_rth", "status": "complete", "estimators_valid": True,
            "contract_key": contract, "open_ticks": 100, "high_ticks": max(101, close), "low_ticks": min(99, close),
            "close_ticks": close, "previous_close_ticks": previous_close,
            "parkinson": 0.0, "garman_klass": 0.0, "rogers_satchell": 0.0, "log_range": 0.0,
            "true_range_ticks": tr, "formation_start_ns": start, "formation_end_ns": end,
            "known_at_ns": known, "window_version": window_version,
            "source_sha256": source, "canonical_table_sha256": canonical,
            "admission_manifest_sha256": admission, "variant": variant, "year": year, "root": "NQ",
            "previous_date": "2019-12-31", "previous_contract_key": contract,
            "previous_close_source_sha256": "p" * 64,
            "previous_close_canonical_table_sha256": "q" * 64,
            "previous_close_admission_manifest_sha256": "r" * 64,
            "previous_close_variant": "primary_corrected", "previous_close_year": 2019,
        }

    def test_feature_prior_ignores_current_price_and_timestamp_mutation(self):
        prior0 = self._session("2020-01-02", 1_000 * M, 1_390 * M, 1_392 * M, window_version="w0")
        prior1 = self._session("2020-01-03", 2_000 * M, 2_390 * M, 2_392 * M, close=110,
                               window_version="w1", previous_close=100, source="s" * 64)
        current = self._session("2020-01-06", 3_000 * M, 3_390 * M, 3_392 * M, close=130,
                                window_version="current-w", previous_close=110)
        cash = _cash(date(2020, 1, 6), open_at=3_000 * M, close_at=3_390 * M)
        first = history_window_row(current, 2, "feature_prior", [prior0, prior1],
                                   _partition(), "src", cash)
        mutated = dict(current, open_ticks=999, high_ticks=1000, low_ticks=1, close_ticks=2,
                       known_at_ns=9_000 * M, window_version="mutated-future",
                       formation_start_ns=3_000 * M, contract_key="NQH21")
        second = history_window_row(mutated, 2, "feature_prior", [prior0, prior1],
                                    _partition(), "src", cash)
        self.assertEqual(first["window_version"], second["window_version"])
        self.assertEqual(first["window_version"], history_window_version("feature_prior", 2, [prior0, prior1]))
        self.assertNotEqual(first["window_version"], current["window_version"])
        self.assertEqual(first["formation_start_ns"], 1_000 * M)
        self.assertEqual(first["formation_end_ns"], 2_390 * M)
        self.assertEqual(first["known_at_ns"], 2_392 * M)
        self.assertEqual(first["contract_key"], RAW)
        self.assertEqual(first["yang_zhang"], second["yang_zhang"])
        self.assertEqual(first["source_lineage"], second["source_lineage"])
        self.assertIn("p" * 64, first["source_lineage"])
        self.assertIn("s" * 64, first["source_lineage"])
        self.assertTrue(first["causal_feature_eligible"])
        self.assertEqual(first["decision_cut_ns"], 3_000 * M)
        self.assertEqual(second["decision_cut_ns"], mutated["formation_start_ns"])
        self.assertEqual(first["date"], second["date"])
        self.assertAlmostEqual(first["mean_true_range_ticks"], 2.0, places=12)

    def test_mean_true_range_uses_declared_n_or_null(self):
        complete = self._session("2020-01-02", 10, 20, 21, tr=4.0)
        other = self._session("2020-01-03", 30, 40, 41, tr=8.0)
        cash = _cash()
        row = history_window_row(other, 2, "measurement_including_current",
                                 [complete, other], _partition(), "src", cash)
        self.assertAlmostEqual(row["mean_true_range_ticks"], 6.0, places=12)
        missing = dict(other, true_range_ticks=None, status="missing_input", estimators_valid=False)
        dropped = history_window_row(other, 2, "measurement_including_current",
                                     [complete, missing], _partition(), "src", cash)
        self.assertIsNone(dropped["mean_true_range_ticks"])


class RemainingCausalFixtures(unittest.TestCase):
    def _rows(self, open_ns, count, *, prices=None, contracts=None, skip=(), known_fn=None):
        rows = []
        for index in range(count):
            if index in skip:
                continue
            o, h, l, c = prices[index] if prices is not None else (100, 101, 99, 100)
            contract = RAW if contracts is None else contracts[index]
            known = (known_fn(index) if known_fn is not None else open_ns + (index + 1) * M)
            rows.append(((o, h, l, c), known, contract, True))
        return rows

    def test_prefix_missing_last_minute_keeps_planned_known_after_cut(self):
        calendar = CashCalendar(CALENDAR)
        day = date(2020, 1, 2)
        cash = calendar.resolve(day, cut=local_timestamp(day, time(0), calendar.zone))
        open_ns = cash.open_at
        series = MinuteBars(_columns(self._rows(open_ns, 4), start0=open_ns),
                            source_version="prefix-missing-last")
        cols = columns_from_series(series)
        session_row = {"session": "cash_rth", "contract_key": RAW, "window_version": "full-future"}
        remaining = measure_remaining(cols, series, cash, session_row, _partition(), "src", calendar.zone)
        cut5 = [row for row in remaining if row["cut_minutes_after_open"] == 5 and row["target_kind"] == "forward_5"]
        self.assertEqual(len(cut5), 1)
        row = cut5[0]
        prefix_end = open_ns + 5 * M
        self.assertEqual(row["prefix_end_ns"], prefix_end)
        self.assertEqual(row["known_at_ns"], prefix_end + M)
        self.assertLess(row["observed_input_known_at_ns"], prefix_end)
        self.assertGreaterEqual(row["target_start_ns"], prefix_end)
        self.assertFalse(row["prefix_complete"])
        self.assertFalse(row["join_eligible"])
        self.assertNotEqual(row["status"], "complete")
        self.assertIn("prefix_incomplete", row["exclusion_reasons"])

    def test_full_session_future_mutation_does_not_change_feature_id_or_version(self):
        calendar = CashCalendar(CALENDAR)
        day = date(2020, 1, 2)
        cash = calendar.resolve(day, cut=local_timestamp(day, time(0), calendar.zone))
        open_ns = cash.open_at
        base = self._rows(open_ns, 20, known_fn=lambda i: _lag60(open_ns, i))
        mutated_prices = [((100, 101, 99, 100) if i < 10 else (200, 210, 190, 205)) for i in range(20)]
        mutated_contracts = [RAW if i < 10 else "NQH20" for i in range(20)]
        series_a = MinuteBars(_columns(base, start0=open_ns), source_version="same-src")
        series_b = MinuteBars(_columns(self._rows(
            open_ns, 20, prices=mutated_prices, contracts=mutated_contracts,
            known_fn=lambda i: _lag60(open_ns, i)), start0=open_ns), source_version="same-src")
        cols_a = columns_from_series(series_a)
        cols_b = columns_from_series(series_b)
        full_a = series_a.window(open_ns, open_ns + 20 * M)
        full_b = series_b.window(open_ns, open_ns + 20 * M)
        self.assertNotEqual(full_a.version, full_b.version)
        row_a = measure_remaining(cols_a, series_a, cash,
                                  {"session": "cash_rth", "contract_key": full_a.contract_key,
                                   "window_version": full_a.version},
                                  _partition(), "src", calendar.zone)
        row_b = measure_remaining(cols_b, series_b, cash,
                                  {"session": "cash_rth", "contract_key": full_b.contract_key,
                                   "window_version": full_b.version},
                                  _partition(), "src", calendar.zone)
        cut_a = [row for row in row_a if row["cut_minutes_after_open"] == 5 and row["target_kind"] == "forward_5"][0]
        cut_b = [row for row in row_b if row["cut_minutes_after_open"] == 5 and row["target_kind"] == "forward_5"][0]
        self.assertEqual(cut_a["feature_id"], cut_b["feature_id"])
        self.assertEqual(cut_a["window_version"], cut_b["window_version"])
        self.assertEqual(cut_a["prefix_window_version"], cut_b["prefix_window_version"])
        self.assertNotEqual(cut_a["window_version"], full_a.version)

    def test_fixed_60_near_close_is_censored_not_complete(self):
        open_ns = 5_000 * M
        close_ns = open_ns + 50 * M
        cash = _cash(date(2020, 1, 2), open_at=open_ns, close_at=close_ns)
        series = MinuteBars(_columns(self._rows(open_ns, 20, known_fn=lambda i: _lag60(open_ns, i)),
                                     start0=open_ns), source_version="near-close")
        cols = columns_from_series(series)
        remaining = measure_remaining(
            cols, series, cash, {"session": "cash_rth", "contract_key": RAW, "window_version": "x"},
            _partition(), "src", "America/New_York")
        row = [item for item in remaining if item["cut_minutes_after_open"] == 5
               and item["target_kind"] == "forward_60"][0]
        self.assertTrue(row["horizon_censored"])
        self.assertGreater(row["nominal_target_end_ns"], close_ns)
        self.assertEqual(row["actual_observed_end_ns"], close_ns)
        self.assertFalse(row["full_target_complete"])
        self.assertFalse(row["join_eligible"])
        self.assertNotEqual(row["status"], "complete")
        cash_close = [item for item in remaining if item["cut_minutes_after_open"] == 5
                      and item["target_kind"] == "actual_cash_close"][0]
        self.assertFalse(cash_close["horizon_censored"])

    def test_all_future_above_reference_down_excursion_is_zero(self):
        calendar = CashCalendar(CALENDAR)
        day = date(2020, 1, 2)
        cash = calendar.resolve(day, cut=local_timestamp(day, time(0), calendar.zone))
        open_ns = cash.open_at
        prices = [(100, 101, 99, 100) if i < 5 else (120, 130, 115, 125) for i in range(20)]
        series = MinuteBars(_columns(self._rows(open_ns, 20, prices=prices,
                                                known_fn=lambda i: _lag60(open_ns, i)), start0=open_ns),
                            source_version="above-ref")
        cols = columns_from_series(series)
        remaining = measure_remaining(
            cols, series, cash, {"session": "cash_rth", "contract_key": RAW, "window_version": "x"},
            _partition(), "src", calendar.zone)
        row = [item for item in remaining if item["cut_minutes_after_open"] == 5
               and item["target_kind"] == "forward_5"][0]
        self.assertEqual(row["reference_close_ticks"], 100)
        self.assertEqual(row["future_down_ticks"], 0)
        self.assertEqual(row["future_down_log"], 0.0)
        self.assertGreater(row["future_up_ticks"], 0)


class ScaleFullLengthFixtures(unittest.TestCase):
    def test_six_full_plus_thirty_short_excludes_short_from_primary(self):
        open_ns = 8_000 * M
        close_ns = open_ns + 390 * M
        rows = []
        for index in range(390):
            if index < 360:
                prices = (100, 101, 99, 100)
            else:
                prices = (100, 200, 50, 100)
            rows.append((prices, _lag60(open_ns, index), RAW, True))
        series = MinuteBars(_columns(rows, start0=open_ns), source_version="rth-390")
        cols = columns_from_series(series)
        cash = _cash(date(2020, 3, 9), open_at=open_ns, close_at=close_ns)
        session_row = {
            "session": "cash_rth", "status": "complete", "contract_key": RAW,
            "window_version": "sess", "formation_start_ns": open_ns, "formation_end_ns": close_ns,
            "known_at_ns": _lag60(open_ns, 389), "parkinson": 0.01, "garman_klass": 0.01,
            "rogers_satchell": 0.01, "expected_minutes": 390, "observed_minutes": 390,
        }
        scales = measure_scales(cols, cash, session_row, _partition(), "src")
        hour = [row for row in scales if row["scale_minutes"] == 60][0]
        self.assertEqual(hour["n_expected_bars"], 7)
        self.assertEqual(hour["n_full_length_bars"], 6)
        self.assertEqual(hour["n_short_bars"], 1)
        self.assertEqual(hour["last_bar_duration_minutes"], 30)
        self.assertFalse(hour["last_bar_full_length"])
        self.assertTrue(hour["scale_full_complete"])
        self.assertEqual(hour["status"], "complete")
        narrow = interval_estimators(100, 101, 99, 100)
        wide = interval_estimators(100, 200, 50, 100)
        self.assertAlmostEqual(hour["mean_parkinson"], narrow["parkinson"], places=12)
        self.assertNotAlmostEqual(hour["observed_mean_parkinson"], hour["mean_parkinson"], places=8)
        mixed = (6.0 * narrow["parkinson"] + wide["parkinson"]) / 7.0
        self.assertAlmostEqual(hour["observed_mean_parkinson"], mixed, places=10)
        five = [row for row in scales if row["scale_minutes"] == 5][0]
        self.assertEqual(five["n_full_length_bars"], 78)
        self.assertEqual(five["n_short_bars"], 0)
        self.assertTrue(five["scale_full_complete"])

    def test_missing_midbar_has_no_full_scale_comparison(self):
        open_ns = 9_000 * M
        close_ns = open_ns + 390 * M
        rows = []
        for index in range(390):
            if 60 <= index < 120:
                continue
            rows.append(((100, 101, 99, 100), _lag60(open_ns, index), RAW, True))
        series = MinuteBars(_columns(rows, start0=open_ns), source_version="missing-mid")
        cols = columns_from_series(series)
        cash = _cash(date(2020, 3, 9), open_at=open_ns, close_at=close_ns)
        session_row = {
            "session": "cash_rth", "status": "complete", "contract_key": RAW,
            "window_version": "sess", "formation_start_ns": open_ns, "formation_end_ns": close_ns,
            "known_at_ns": _lag60(open_ns, 389), "parkinson": 0.01, "garman_klass": 0.01,
            "rogers_satchell": 0.01, "expected_minutes": 390, "observed_minutes": 330,
        }
        hour = [row for row in measure_scales(cols, cash, session_row, _partition(), "src")
                if row["scale_minutes"] == 60][0]
        self.assertFalse(hour["scale_full_complete"])
        self.assertIsNone(hour["mean_parkinson"])
        self.assertIsNone(hour["sampled_close_rv"])
        self.assertNotEqual(hour["status"], "complete")
        self.assertEqual(hour["n_scale_full_complete"], 5)
        self.assertIsNotNone(hour["observed_mean_parkinson"])


class SeasonalAndPairFixtures(unittest.TestCase):
    def test_seasonal_cell_uses_cell_contract_and_window_not_session(self):
        open_ns = 4_000 * M
        close_ns = open_ns + 60 * M
        rows = []
        for index in range(60):
            contract = RAW if index < 30 else "NQH20"
            rows.append(((100, 101, 99, 100), _lag60(open_ns, index), contract, True))
        series = MinuteBars(_columns(rows, start0=open_ns), source_version="cells")
        cols = columns_from_series(series)
        cash = _cash(date(2020, 1, 2), open_at=open_ns, close_at=close_ns)
        session_row = {
            "session": "cash_rth", "status": "complete", "contract_key": "SESSION-FUTURE",
            "window_version": "full-day-future", "formation_start_ns": open_ns,
            "formation_end_ns": close_ns, "known_at_ns": _lag60(open_ns, 59),
        }
        cells = measure_seasonal_cells(cols, cash, session_row, _partition(), "src", series)
        self.assertEqual(len(cells), 2)
        self.assertEqual(cells[0]["contract_key"], RAW)
        self.assertEqual(cells[1]["contract_key"], "NQH20")
        self.assertNotEqual(cells[0]["window_version"], "full-day-future")
        self.assertNotEqual(cells[0]["window_version"], cells[1]["window_version"])
        self.assertNotEqual(cells[0]["contract_key"], session_row["contract_key"])

    def test_original_vs_primary_same_contract_pair_only(self):
        from trading_research.research.physical_ohlc_volatility import build_statistics
        primary = [
            {"date": "2024-01-02", "root": "NQ", "year": 2024, "variant": "primary_corrected",
             "session": "cash_rth", "stage": "development", "garman_klass": 0.2,
             "garman_klass_status": "valid", "contract_key": "NQH24"},
            {"date": "2024-01-03", "root": "NQ", "year": 2024, "variant": "primary_corrected",
             "session": "cash_rth", "stage": "development", "garman_klass": 0.3,
             "garman_klass_status": "valid", "contract_key": "NQM24"},
        ]
        original = [
            {"date": "2024-01-02", "root": "NQ", "year": 2024, "variant": "original_nq2024_sensitivity",
             "session": "cash_rth", "stage": "development", "garman_klass": 0.5,
             "garman_klass_status": "valid", "contract_key": "NQH24"},
            {"date": "2024-01-03", "root": "NQ", "year": 2024, "variant": "original_nq2024_sensitivity",
             "session": "cash_rth", "stage": "development", "garman_klass": 9.0,
             "garman_klass_status": "valid", "contract_key": "NQH24"},
        ]
        stats = build_statistics(primary + original, [], [], [], [], {("NQ", 2024, "primary_corrected"): ["2024-01-02", "2024-01-03"]})
        pair = stats["nq2024_original_vs_primary"]
        self.assertEqual(pair["changed_contract"], 1)
        self.assertEqual(pair["matched_valid_pairs"], 1)
        self.assertEqual(pair["same_raw_contract_pairs"], 1)
        self.assertIn("2024-01-03", pair["changed_contract_dates"])


class FixtureKnownAtFixtures(unittest.TestCase):
    def test_columns_known_at_is_start0_plus_offset_plus_one_minute(self):
        start0 = 1_234_567 * M
        cols = _columns([((100, 101, 99, 100),), ((100, 101, 99, 100),)], start0=start0)
        self.assertEqual(cols["known_at_ns"][0], start0 + 1 * M)
        self.assertEqual(cols["known_at_ns"][1], start0 + 2 * M)
        self.assertNotEqual(cols["known_at_ns"][0], (start0 + 1) * M)
        self.assertEqual(_lag60(start0, 0), start0 + 2 * M)


if __name__ == "__main__":
    unittest.main()
