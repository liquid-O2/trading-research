"""Independent Options OI measurement cases. No population run."""
from __future__ import annotations

from datetime import date, datetime, time, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.time import datetime_ns
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.options_oi_measurements import (
    adjacent_lifecycle, contract_key, cut_ns_on, dte_bucket, dte_days,
    eastern_date_from_ns, intended_cash_dates, parse_osi, previous_intended,
    resolve_contract_report, run, select_asof_observation,
    sourceclock_asof_eligible, stage_of, timestamp_ns_from_arrow, utc_date_from_ns,
)
from trading_research.research.options_oi_statistics import date_balanced_point, empty_metric


PROTOCOL = json.loads(Path("/workspace/trading-research/validation/OPTIONS_OI_REPORT_LIFECYCLE_V1.json").read_text())
CALENDAR = CashCalendar(Path(PROTOCOL["cash_calendar"]["path"]))
STAGES = PROTOCOL["population"]["stages"]
ZONE = "America/New_York"
CONTRACT_SCHEMA = (
    "symbol: large_string\nexpiration: date32[day]\nstrike: double\nright: large_string\n"
    "request_date: date32[day]\nosi_symbol: large_string"
)
OI_SCHEMA = (
    "symbol: large_string\nexpiration: date32[day]\nstrike: double\nright: large_string\n"
    "open_interest: int64\nrequest_date: date32[day]\nts_event: timestamp[ns, tz=UTC]\n"
    "osi_symbol: large_string"
)
NDX_OSI = "NDX   200117C03400000"
NDXP_OSI = "NDXP  200117C03400000"
SPX_OSI = "SPX   200117C03400000"
SPXW_OSI = "SPXW  200117C03400000"
VIX_OSI = "VIX   200422C00037500"


def _obs(ts, oi, file_id=1, row=0, request="2020-01-02"):
    return {"ts_event_ns": ts, "open_interest": oi, "file_id": file_id, "row_index": row,
            "request_date": request}


def _endpoint(oi, ts, usable=True, file_id=1, row=0):
    return {"open_interest": oi, "ts_event_ns": ts, "file_id": file_id, "row_index": row,
            "usable_for_statistics": usable}


class IdentityAndParseTests(unittest.TestCase):
    def test_ndx_and_ndxp_identities_are_separate(self):
        ndx = contract_key("NDX", NDX_OSI, "2020-01-17", 3400.0, "CALL")
        ndxp = contract_key("NDXP", NDXP_OSI, "2020-01-17", 3400.0, "CALL")
        self.assertNotEqual(ndx, ndxp)
        self.assertEqual(ndx[0], "NDX")
        self.assertEqual(ndxp[0], "NDXP")

    def test_spx_and_spxw_identities_are_separate(self):
        self.assertNotEqual(
            contract_key("SPX", SPX_OSI, "2020-01-17", 3400.0, "CALL"),
            contract_key("SPXW", SPXW_OSI, "2020-01-17", 3400.0, "CALL"),
        )

    def test_source_file_path_is_not_contract_identity(self):
        key = contract_key("NDX", NDX_OSI, "2020-01-17", 3400.0, "CALL")
        again = contract_key("NDX", NDX_OSI, "2020-01-17", 3400.0, "CALL")
        self.assertEqual(key, again)
        self.assertNotIn("parquet", str(key))
        self.assertNotIn("thetadata", str(key))

    def test_strike_osi_identity_conflict(self):
        parsed = parse_osi(NDX_OSI)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["expiration"], "2020-01-17")
        self.assertEqual(parsed["right"], "CALL")
        self.assertEqual(parsed["millistrike"], 3400000)
        self.assertNotEqual(parsed["millistrike"], 3500000)

    def test_dte_over_60_is_retained_in_61_plus_bucket(self):
        self.assertEqual(dte_days("2020-04-02", "2020-01-02"), 91)
        self.assertEqual(dte_bucket(91), "61+")
        self.assertEqual(dte_bucket(60), "31-60")
        self.assertEqual(dte_bucket(-1), "expired")


class ReportResolutionTests(unittest.TestCase):
    def test_oi_100_to_120_delta_is_20(self):
        resolved = resolve_contract_report([_obs(10, 100, row=0), _obs(20, 120, row=1)])
        self.assertEqual(resolved["first_oi"], 100)
        self.assertEqual(resolved["last_oi"], 120)
        self.assertEqual(resolved["observed_update_difference"], 20)
        self.assertTrue(resolved["update_candidate"])
        self.assertFalse(resolved["certified_revision"])
        self.assertTrue(resolved["usable_for_statistics"])

    def test_zero_is_valid_and_absent_is_not_zero(self):
        zero = resolve_contract_report([_obs(10, 0)])
        self.assertEqual(zero["first_oi"], 0)
        self.assertTrue(zero["usable_for_statistics"])
        absent = resolve_contract_report([])
        self.assertIsNone(absent["first_oi"])
        self.assertIsNone(absent["last_oi"])
        self.assertFalse(absent["usable_for_statistics"])

    def test_same_time_10_vs_20_has_no_winner(self):
        resolved = resolve_contract_report([_obs(10, 10, row=0), _obs(10, 20, row=1)])
        self.assertTrue(resolved["same_time_conflict"])
        self.assertEqual(resolved["conflict_disposition"], "same_time_no_winner")
        self.assertFalse(resolved["usable_for_statistics"])
        self.assertIsNone(resolved["first_oi"])
        self.assertIsNone(resolved["last_oi"])

    def test_exact_alias_count_2_is_not_2_support(self):
        resolved = resolve_contract_report([_obs(10, 7, row=0), _obs(10, 7, row=1)])
        self.assertEqual(resolved["alias_multiplicity"], 2)
        self.assertEqual(resolved["support_observations"], 1)
        self.assertEqual(resolved["n_source_rows"], 2)
        self.assertFalse(resolved["same_time_conflict"])
        self.assertEqual(resolved["first_oi"], 7)

    def test_distinct_time_10_to_20_is_candidate_update_not_revision(self):
        resolved = resolve_contract_report([_obs(10, 10, row=0), _obs(20, 20, row=1)])
        self.assertTrue(resolved["update_candidate"])
        self.assertFalse(resolved["certified_revision"])
        self.assertEqual(resolved["observed_update_difference"], 10)
        self.assertEqual(resolved["conflict_disposition"], "none")


class CalendarClockTests(unittest.TestCase):
    def test_friday_to_monday_previous_intended(self):
        intended = intended_cash_dates(CALENDAR, date(2020, 1, 2), date(2020, 1, 7))
        self.assertEqual(previous_intended(intended, date(2020, 1, 6)), date(2020, 1, 3))
        self.assertIn(date(2020, 1, 3), intended)
        self.assertIn(date(2020, 1, 6), intended)
        self.assertNotIn(date(2020, 1, 4), intended)
        self.assertNotIn(date(2020, 1, 5), intended)

    def test_holiday_previous_intended_skips_closed_day(self):
        intended = intended_cash_dates(CALENDAR, date(2025, 1, 2), date(2025, 1, 10))
        self.assertNotIn(date(2025, 1, 9), intended)
        self.assertEqual(previous_intended(intended, date(2025, 1, 10)), date(2025, 1, 8))

    def test_future_1000_report_rejected_at_0930_cut(self):
        day = date(2020, 1, 2)
        cut = cut_ns_on(day, "09:30")
        late = local_timestamp(day, time(10, 0), ZONE)
        self.assertFalse(sourceclock_asof_eligible(late, "2020-01-02", cut, "2020-01-02"))
        picked, status = select_asof_observation(
            [_obs(late, 15, request="2020-01-02")], cut, "2020-01-02")
        self.assertIsNone(picked)
        self.assertEqual(status, "rejected_future")
        on_cut = local_timestamp(day, time(9, 30), ZONE)
        self.assertTrue(sourceclock_asof_eligible(on_cut, "2020-01-02", cut, "2020-01-02"))

    def test_next_utc_day_event_date_scenario_flag(self):
        ns = datetime_ns(datetime(2020, 1, 3, 0, 30, tzinfo=timezone.utc))
        self.assertEqual(eastern_date_from_ns([ns])[0], "2020-01-02")
        self.assertEqual(utc_date_from_ns([ns])[0], "2020-01-03")
        self.assertNotEqual(utc_date_from_ns([ns])[0], "2020-01-02")

    def test_arrow_large_nanosecond_timestamp_roundtrip_exact(self):
        import pyarrow as pa
        ns = 1_778_066_221_908_000_123
        column = pa.array([ns, None], type=pa.timestamp("ns", tz="UTC"))
        restored = timestamp_ns_from_arrow(column).to_pylist()
        self.assertEqual(restored[0], ns)
        self.assertIsNone(restored[1])


class LifecycleTests(unittest.TestCase):
    def test_expiry_without_next_report_is_censored_not_zero(self):
        life = adjacent_lifecycle(
            _endpoint(40, 10), None, prior_date="2020-01-02", next_date="2020-01-03",
            expiration="2020-01-02", last_selected="2020-01-10", first_selected="2020-01-02",
            prior_stage="training", next_stage="training", listed_on_prior=True,
        )
        self.assertEqual(life["censor"], "expired_before_next_request_date")
        self.assertIsNone(life["delta"])
        self.assertFalse(life["usable_for_statistics"])
        self.assertFalse(life["intraday_terminal_holdings_identified"])

    def test_missing_intended_day_does_not_compress_delta(self):
        monday = adjacent_lifecycle(
            _endpoint(100, 10), None, prior_date="2020-01-02", next_date="2020-01-03",
            expiration="2020-01-17", last_selected="2020-01-06", first_selected="2020-01-02",
            prior_stage="training", next_stage="training", listed_on_prior=True,
        )
        wednesday = adjacent_lifecycle(
            None, _endpoint(120, 30), prior_date="2020-01-03", next_date="2020-01-06",
            expiration="2020-01-17", last_selected="2020-01-06", first_selected="2020-01-02",
            prior_stage="training", next_stage="training", listed_on_prior=False,
        )
        self.assertEqual(monday["censor"], "missing_next_publication")
        self.assertIsNone(monday["delta"])
        self.assertFalse(monday["cross_gap_compressed"])
        self.assertEqual(wednesday["appearance"], "first_observed")
        self.assertIsNone(wednesday["delta"])
        self.assertNotEqual(wednesday.get("delta"), 20)

    def test_stage_crossing_is_preserved_but_excluded_from_within_stage_stats(self):
        life = adjacent_lifecycle(
            _endpoint(100, 10), _endpoint(120, 30),
            prior_date="2022-12-30", next_date="2023-01-03",
            expiration="2023-06-16", last_selected="2023-01-03", first_selected="2022-12-30",
            prior_stage=stage_of("2022-12-30", STAGES), next_stage=stage_of("2023-01-03", STAGES),
            listed_on_prior=True,
        )
        self.assertEqual(life["delta"], 20)
        self.assertEqual(stage_of("2022-12-30", STAGES), "training")
        self.assertEqual(stage_of("2023-01-03", STAGES), "development")
        self.assertFalse(life["within_stage_stat_eligible"])
        self.assertFalse(life["within_year_stat_eligible"])
        self.assertTrue(life["usable_for_statistics"])

    def test_first_observed_is_not_certified_listing_birth(self):
        life = adjacent_lifecycle(
            None, _endpoint(5, 10), prior_date="2020-01-02", next_date="2020-01-03",
            expiration="2020-01-17", last_selected="2020-01-06", first_selected="2020-01-02",
            prior_stage="training", next_stage="training", listed_on_prior=False,
        )
        self.assertEqual(life["appearance"], "first_observed")
        self.assertFalse(life["certified_listing_birth"])
        self.assertTrue(life["prior_report_missing"])


class StatisticsDefinitionTests(unittest.TestCase):
    def test_all_missing_metric_is_undefined_not_zero(self):
        metric = empty_metric(["2020-01-02", "2020-01-03", "2020-01-06"])
        self.assertIsNone(metric["estimate"])
        self.assertNotEqual(metric["estimate"], 0)
        self.assertEqual(metric["missing_date_count"], 3)
        self.assertEqual(metric["actual_valid_date_count"], 0)

    def test_unequal_contract_counts_are_date_balanced(self):
        daily_means = {"2020-01-02": 10.0, "2020-01-03": 0.0}
        event_mass, event_width = 10, 4
        self.assertEqual(date_balanced_point(daily_means), 5.0)
        self.assertEqual(event_mass / event_width, 2.5)
        self.assertNotEqual(date_balanced_point(daily_means), event_mass / event_width)


def _write_parquet(path, table):
    import pyarrow.parquet as pq
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path)
    raw = path.read_bytes()
    return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _contracts(rows):
    import pyarrow as pa
    return pa.table({
        "symbol": pa.array([row[0] for row in rows], type=pa.large_string()),
        "expiration": pa.array([row[1] for row in rows], type=pa.date32()),
        "strike": pa.array([row[2] for row in rows], type=pa.float64()),
        "right": pa.array([row[3] for row in rows], type=pa.large_string()),
        "request_date": pa.array([row[4] for row in rows], type=pa.date32()),
        "osi_symbol": pa.array([row[5] for row in rows], type=pa.large_string()),
    })


def _oi(rows):
    import pyarrow as pa
    return pa.table({
        "symbol": pa.array([row[0] for row in rows], type=pa.large_string()),
        "expiration": pa.array([row[1] for row in rows], type=pa.date32()),
        "strike": pa.array([row[2] for row in rows], type=pa.float64()),
        "right": pa.array([row[3] for row in rows], type=pa.large_string()),
        "open_interest": pa.array([row[4] for row in rows], type=pa.int64()),
        "request_date": pa.array([row[5] for row in rows], type=pa.date32()),
        "ts_event": pa.array([row[6] for row in rows], type=pa.timestamp("ns", tz="UTC")),
        "osi_symbol": pa.array([row[7] for row in rows], type=pa.large_string()),
    })


def _admit(file_id, rel, chain, role, request_date, dataset_id, schema_id, meta):
    return {
        "file_id": file_id,
        "source": {
            "path": rel, "size_bytes": meta["size_bytes"], "chain": chain, "role": role,
            "request_date": request_date, "dataset_id": dataset_id,
        },
        "sha256": meta["sha256"], "rows": None, "schema_id": schema_id, "format": ".parquet",
    }


class EndToEndFixtureTests(unittest.TestCase):
    def _protocol(self, root):
        payload = dict(PROTOCOL)
        payload["data_root"] = str(root)
        return payload

    def _outputs(self, folder):
        return BoundedOutputs(Path(folder) / "out", maximum_total_bytes=32 * 1024 * 1024,
                              maximum_file_bytes=16 * 1024 * 1024)

    def test_two_date_fixture_delta_20_zero_absent_vix_unknown(self):
        import pyarrow.parquet as pq
        day_a, day_b = date(2020, 1, 2), date(2020, 1, 3)
        exp = date(2020, 1, 17)
        vix_exp = date(2020, 4, 22)
        ts_a = local_timestamp(day_a, time(6, 30), ZONE)
        ts_b = local_timestamp(day_b, time(6, 30), ZONE)
        ts_vix = local_timestamp(day_a, time(7, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            ndx_c_a = "thetadata-opra/opra__ndx-options__contracts/2020-01-02.parquet"
            ndx_o_a = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            ndx_c_b = "thetadata-opra/opra__ndx-options__contracts/2020-01-03.parquet"
            ndx_o_b = "thetadata-opra/opra__ndx-options__open-interest/2020-01-03.parquet"
            vix_o = "thetadata-opra/opra__vix-options__open-interest__dte60-full-chain/2020-01-02.parquet"
            listed = [("NDX", exp, 3400.0, "CALL", day_a, NDX_OSI)]
            listed_b = [("NDX", exp, 3400.0, "CALL", day_b, NDX_OSI)]
            oi_a = [("NDX", exp, 3400.0, "CALL", 100, day_a, ts_a, NDX_OSI),
                    ("NDX", date(2020, 1, 10), 100.0, "PUT", 0, day_a, ts_a, "NDX   200110P00100000")]
            oi_b = [("NDX", exp, 3400.0, "CALL", 120, day_b, ts_b, NDX_OSI)]
            vix = [("VIX", vix_exp, 37.5, "CALL", 8, day_a, ts_vix, VIX_OSI)]
            sources = [
                _admit(1, ndx_c_a, "NDX", "contracts", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__contracts", "contracts",
                       _write_parquet(root / ndx_c_a, _contracts(listed))),
                _admit(2, ndx_o_a, "NDX", "open_interest", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / ndx_o_a, _oi(oi_a))),
                _admit(3, ndx_c_b, "NDX", "contracts", "2020-01-03",
                       "thetadata-opra/opra__ndx-options__contracts", "contracts",
                       _write_parquet(root / ndx_c_b, _contracts(listed_b))),
                _admit(4, ndx_o_b, "NDX", "open_interest", "2020-01-03",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / ndx_o_b, _oi(oi_b))),
                _admit(5, vix_o, "VIX", "open_interest", "2020-01-02",
                       "thetadata-opra/opra__vix-options__open-interest__dte60-full-chain", "oi",
                       _write_parquet(root / vix_o, _oi(vix))),
            ]
            admitted = {
                "kind": "options_oi_admitted_sources_v1",
                "source_files": 5,
                "sources": sources,
                "schemas": {"contracts": CONTRACT_SCHEMA, "oi": OI_SCHEMA},
                "source_bytes": sum(item["source"]["size_bytes"] for item in sources),
                "rows_by_role": {"contracts": None, "open_interest": None},
            }
            result = run(
                protocol=self._protocol(root), admitted=admitted,
                outputs=self._outputs(folder), selected_dates=["2020-01-02", "2020-01-03"],
            )
            self.assertTrue(result["passed"])
            self.assertIs(result["full_family_complete"], False)
            self.assertEqual(result["clock_interpretation"]["known_at_ns"], None)
            self.assertIs(result["clock_interpretation"]["causal_feature_eligible"], False)
            self.assertEqual(result["counts"]["source_files_read"], 5)
            self.assertEqual(result["counts"]["intended_chain_date_units"], 14)
            self.assertIn("VIX", result["counts"]["listing_unknown_chains"])
            life = pq.read_table(result["refs"]["lifecycle"][0]["path"]).to_pylist()
            deltas = [row["delta"] for row in life
                      if row["chain"] == "NDX" and row["osi_symbol"] == NDX_OSI and row["delta"] is not None]
            self.assertIn(20, deltas)
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            vix_rows = [row for row in coverage if row["chain"] == "VIX" and row["request_date"] == "2020-01-02"]
            self.assertEqual(len(vix_rows), 1)
            self.assertTrue(vix_rows[0]["vix_listing_unknown"])
            self.assertEqual(vix_rows[0]["listing_status"], "unknown")
            self.assertFalse(vix_rows[0]["listing_denominator_known"])
            self.assertIsNone(vix_rows[0]["coverage_listed_with_oi"])
            ndx_a = [row for row in coverage if row["chain"] == "NDX" and row["request_date"] == "2020-01-02"][0]
            self.assertEqual(ndx_a["oi_zero_count"], 1)
            self.assertEqual(vix_rows[0]["gt60_dte_retained"], 1)
            raw = pq.read_table(result["refs"]["raw"][0]["path"]).to_pylist()
            zeros = [row for row in raw if row["disposition"] == "valid_zero"]
            self.assertEqual(len(zeros), 1)
            self.assertEqual(zeros[0]["open_interest"], 0)
            md = Path(result["refs"]["results_md"]["path"]).read_text()
            self.assertIn("candidate definitions", md.lower())
            self.assertIn("causal_feature_eligible is FALSE", md)

    def test_three_date_missing_middle_does_not_compress(self):
        import pyarrow.parquet as pq
        day_a, day_c = date(2020, 1, 2), date(2020, 1, 6)
        exp = date(2020, 1, 17)
        ts_a = local_timestamp(day_a, time(6, 30), ZONE)
        ts_c = local_timestamp(day_c, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p_a = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            p_c = "thetadata-opra/opra__ndx-options__open-interest/2020-01-06.parquet"
            sources = [
                _admit(1, p_a, "NDX", "open_interest", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_a, _oi([
                           ("NDX", exp, 3400.0, "CALL", 100, day_a, ts_a, NDX_OSI)]))),
                _admit(2, p_c, "NDX", "open_interest", "2020-01-06",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_c, _oi([
                           ("NDX", exp, 3400.0, "CALL", 120, day_c, ts_c, NDX_OSI)]))),
            ]
            admitted = {
                "kind": "options_oi_admitted_sources_v1", "source_files": 2, "sources": sources,
                "schemas": {"oi": OI_SCHEMA}, "source_bytes": sum(s["source"]["size_bytes"] for s in sources),
                "rows_by_role": {"open_interest": None},
            }
            result = run(
                protocol=self._protocol(root), admitted=admitted,
                outputs=self._outputs(folder),
                selected_dates=["2020-01-02", "2020-01-03", "2020-01-06"],
            )
            life = []
            for ref in result["refs"]["lifecycle"]:
                life.extend(pq.read_table(ref["path"]).to_pylist())
            paired = [row for row in life if row["osi_symbol"] == NDX_OSI]
            self.assertTrue(any(row["censor"] == "missing_next_publication" and row["delta"] is None
                                for row in paired))
            self.assertFalse(any(row["delta"] == 20 and row["prior_date"] == "2020-01-02"
                                 and row["next_date"] == "2020-01-06" for row in paired))
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            middle = [row for row in coverage if row["chain"] == "NDX" and row["request_date"] == "2020-01-03"][0]
            self.assertTrue(middle["both_files_absent"])

    def test_hash_mismatch_aborts_before_decode(self):
        day = date(2020, 1, 2)
        ts = local_timestamp(day, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            meta = _write_parquet(root / rel, _oi([
                ("NDX", date(2020, 1, 17), 3400.0, "CALL", 1, day, ts, NDX_OSI)]))
            record = _admit(1, rel, "NDX", "open_interest", "2020-01-02",
                            "thetadata-opra/opra__ndx-options__open-interest", "oi", meta)
            record["sha256"] = "0" * 64
            admitted = {
                "kind": "options_oi_admitted_sources_v1", "source_files": 1, "sources": [record],
                "schemas": {"oi": OI_SCHEMA}, "source_bytes": meta["size_bytes"],
                "rows_by_role": {"open_interest": None},
            }
            with self.assertRaises(IntegrityError):
                run(protocol=self._protocol(root), admitted=admitted,
                    outputs=self._outputs(folder), selected_dates=["2020-01-02"])

    def test_invalid_source_row_is_retained_not_full_abort(self):
        import pyarrow.parquet as pq
        day = date(2020, 1, 2)
        ts = local_timestamp(day, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            table = _oi([
                ("NDX", date(2020, 1, 17), 3400.0, "CALL", 4, day, ts, NDX_OSI),
                ("NDX", date(2020, 1, 17), 3500.0, "CALL", 9, day, ts, NDX_OSI),
            ])
            meta = _write_parquet(root / rel, table)
            admitted = {
                "kind": "options_oi_admitted_sources_v1", "source_files": 1,
                "sources": [_admit(1, rel, "NDX", "open_interest", "2020-01-02",
                                   "thetadata-opra/opra__ndx-options__open-interest", "oi", meta)],
                "schemas": {"oi": OI_SCHEMA}, "source_bytes": meta["size_bytes"],
                "rows_by_role": {"open_interest": None},
            }
            result = run(
                protocol=self._protocol(root), admitted=admitted,
                outputs=self._outputs(folder), selected_dates=["2020-01-02"],
            )
            raw = pq.read_table(result["refs"]["raw"][0]["path"]).to_pylist()
            reasons = {row["invalid_reason"] for row in raw}
            self.assertIn("strike_or_osi_identity_conflict", reasons)
            self.assertTrue(any(row["parsed_valid"] for row in raw))
            self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
