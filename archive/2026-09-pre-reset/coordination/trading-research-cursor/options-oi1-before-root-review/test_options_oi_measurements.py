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
    INTERVAL_RECONSTRUCTION, adjacent_lifecycle, contract_key, cut_ns_on, dte_bucket,
    dte_days, eastern_date_from_ns, intended_cash_dates, millistrike, parse_osi,
    previous_intended, reconstruct_asof_intervals, resolve_contract_report, run,
    select_asof_observation, sourceclock_asof_eligible, stage_of,
    timestamp_ns_from_arrow, utc_date_from_ns,
)
from trading_research.research.options_oi_statistics import (
    date_balanced_point, empty_metric, run_statistics,
)


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
        self.assertEqual(parsed["root"], "NDX")
        self.assertEqual(parsed["expiration"], "2020-01-17")
        self.assertEqual(parsed["right"], "CALL")
        self.assertEqual(parsed["millistrike"], 3400000)
        self.assertNotEqual(parsed["millistrike"], 3500000)
        self.assertIsNone(parse_osi("NDX   200117C0340000"))
        self.assertEqual(millistrike(3400.0), 3400000)
        self.assertIsNone(millistrike(3400.0001))

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


def _read_parts(refs):
    import pyarrow.parquet as pq
    rows = []
    for ref in refs:
        rows.extend(pq.read_table(ref["path"]).to_pylist())
    return rows


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
            identity = {row["contract_id"]: row for row in _read_parts(result["refs"]["identity_map"])}
            life = _read_parts(result["refs"]["lifecycle"])
            deltas = [row["first_delta"] for row in life
                      if row["chain"] == "NDX" and identity[row["contract_id"]]["osi_symbol"] == NDX_OSI
                      and row["first_delta"] is not None]
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
            reports = _read_parts(result["refs"]["reports"])
            zeros = [row for row in reports if row["first_oi"] == 0 or row["last_oi"] == 0]
            self.assertEqual(len(zeros), 1)
            self.assertEqual(zeros[0]["first_oi"], 0)
            md = Path(result["refs"]["results_md"]["path"]).read_text()
            self.assertIn("causal_feature_eligible is FALSE", md)
            self.assertIn("family is not complete", md.lower())
            self.assertIn("NDX\\|all_period", md)

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
            identity = {row["contract_id"]: row for row in _read_parts(result["refs"]["identity_map"])}
            life = _read_parts(result["refs"]["lifecycle"])
            paired = [row for row in life if identity[row["contract_id"]]["osi_symbol"] == NDX_OSI]
            self.assertTrue(any(row["first_censor"] == "missing_next_publication" and row["first_delta"] is None
                                for row in paired))
            self.assertFalse(any(row["first_delta"] == 20 and row["prior_date"] == "2020-01-02"
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
            exceptions = _read_parts(result["refs"]["exceptions"])
            reasons = {row["invalid_reason"] for row in exceptions}
            self.assertIn("strike_or_osi_identity_conflict", reasons)
            reports = _read_parts(result["refs"]["reports"])
            self.assertTrue(any(row["usable_for_statistics"] for row in reports))
            self.assertTrue(result["passed"])


class IntegratedCorrectionTests(unittest.TestCase):
    def _protocol(self, root):
        payload = dict(PROTOCOL)
        payload["data_root"] = str(root)
        return payload

    def _outputs(self, folder):
        return BoundedOutputs(Path(folder) / "out", maximum_total_bytes=32 * 1024 * 1024,
                              maximum_file_bytes=16 * 1024 * 1024)

    def _admitted(self, sources, schemas=None):
        return {
            "kind": "options_oi_admitted_sources_v1",
            "source_files": len(sources),
            "sources": sources,
            "schemas": schemas or {"contracts": CONTRACT_SCHEMA, "oi": OI_SCHEMA},
            "source_bytes": sum(item["source"]["size_bytes"] for item in sources),
            "rows_by_role": {"contracts": None, "open_interest": None},
        }

    def _run_oi(self, folder, root, sources, dates, schemas=None):
        return run(
            protocol=self._protocol(root), admitted=self._admitted(sources, schemas),
            outputs=self._outputs(folder), selected_dates=dates,
        )

    def test_jan2_after_1500_available_jan3_morning(self):
        import pyarrow.parquet as pq
        day_a, day_b = date(2020, 1, 2), date(2020, 1, 3)
        exp = date(2020, 1, 17)
        ts_late = datetime_ns(datetime(2020, 1, 3, 1, 15, 1, tzinfo=timezone.utc))
        self.assertEqual(eastern_date_from_ns([ts_late])[0], "2020-01-02")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p_a = "thetadata-opra/opra__ndxp-options__open-interest/2020-01-02.parquet"
            sources = [_admit(1, p_a, "NDXP", "open_interest", "2020-01-02",
                              "thetadata-opra/opra__ndxp-options__open-interest", "oi",
                              _write_parquet(root / p_a, _oi([
                                  ("NDXP", exp, 3400.0, "CALL", 55, day_a, ts_late, NDXP_OSI)])))]
            result = self._run_oi(folder, root, sources, ["2020-01-02", "2020-01-03"])
            asof = _read_parts(result["refs"]["asof_aggregates"])
            jan2 = [row for row in asof if row["chain"] == "NDXP" and row["cut_date"] == "2020-01-02"]
            jan3 = [row for row in asof if row["chain"] == "NDXP" and row["cut_date"] == "2020-01-03"
                    and row["cut_label"] == "09:30"]
            self.assertTrue(jan2)
            self.assertTrue(all(row["available"] == 0 for row in jan2))
            self.assertEqual(jan3[0]["available"], 1)
            intervals = _read_parts(result["refs"]["asof_intervals"])
            for cut_label in ("09:30", "10:00", "15:00"):
                cut = cut_ns_on(day_a, cut_label)
                visible = reconstruct_asof_intervals(intervals, cut, "2020-01-02")
                self.assertEqual(sum(1 for row in visible if not row["ambiguous"] and row["open_interest"] is not None), 0)
            visible_next = reconstruct_asof_intervals(intervals, cut_ns_on(day_b, "09:30"), "2020-01-03")
            self.assertEqual(visible_next[0]["open_interest"], 55)
            self.assertIn("valid_from_ns <= cut_ns", INTERVAL_RECONSTRUCTION)
            recon = json.loads(Path(result["refs"]["reconstruction"]["path"]).read_text())
            self.assertEqual(recon["predicate"], INTERVAL_RECONSTRUCTION)

    def test_same_time_conflict_invalidates_prior_asof(self):
        day_a, day_b = date(2020, 1, 2), date(2020, 1, 3)
        exp = date(2020, 1, 17)
        ts_a = local_timestamp(day_a, time(6, 30), ZONE)
        ts_b = local_timestamp(day_b, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p_a = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            p_b = "thetadata-opra/opra__ndx-options__open-interest/2020-01-03.parquet"
            sources = [
                _admit(1, p_a, "NDX", "open_interest", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_a, _oi([("NDX", exp, 3400.0, "CALL", 100, day_a, ts_a, NDX_OSI)]))),
                _admit(2, p_b, "NDX", "open_interest", "2020-01-03",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_b, _oi([
                           ("NDX", exp, 3400.0, "CALL", 10, day_b, ts_b, NDX_OSI),
                           ("NDX", exp, 3400.0, "CALL", 20, day_b, ts_b, NDX_OSI)]))),
            ]
            result = self._run_oi(folder, root, sources, ["2020-01-02", "2020-01-03"])
            asof = _read_parts(result["refs"]["asof_aggregates"])
            later = [row for row in asof if row["cut_date"] == "2020-01-03" and row["chain"] == "NDX"][0]
            self.assertEqual(later["available"], 0)
            self.assertGreaterEqual(later["ambiguous"], 1)
            intervals = _read_parts(result["refs"]["asof_intervals"])
            visible = reconstruct_asof_intervals(intervals, cut_ns_on(day_b, "15:00"), "2020-01-03")
            self.assertTrue(visible)
            self.assertTrue(all(row["ambiguous"] or row["open_interest"] is None for row in visible))

    def test_prior_plus_future_today_counts_one_contract(self):
        day_a, day_b = date(2020, 1, 2), date(2020, 1, 3)
        exp = date(2020, 1, 17)
        ts_a = local_timestamp(day_a, time(6, 30), ZONE)
        ts_b = local_timestamp(day_b, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p_a = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            p_b = "thetadata-opra/opra__ndx-options__open-interest/2020-01-03.parquet"
            sources = [
                _admit(1, p_a, "NDX", "open_interest", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_a, _oi([("NDX", exp, 3400.0, "CALL", 100, day_a, ts_a, NDX_OSI)]))),
                _admit(2, p_b, "NDX", "open_interest", "2020-01-03",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_b, _oi([("NDX", exp, 3400.0, "CALL", 120, day_b, ts_b, NDX_OSI)]))),
            ]
            result = self._run_oi(folder, root, sources, ["2020-01-02", "2020-01-03"])
            asof = [row for row in _read_parts(result["refs"]["asof_aggregates"])
                    if row["chain"] == "NDX" and row["cut_date"] == "2020-01-03" and row["cut_label"] == "09:30"][0]
            self.assertEqual(asof["universe"], 1)
            self.assertEqual(asof["available"], 1)
            self.assertEqual(asof["future_today"], 1)
            self.assertEqual(asof["available"] + asof["future_today"], 2)

    def test_listing_only_zero_available_represented(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p = "thetadata-opra/opra__ndx-options__contracts/2020-01-02.parquet"
            sources = [_admit(1, p, "NDX", "contracts", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__contracts", "contracts",
                              _write_parquet(root / p, _contracts([
                                  ("NDX", exp, 3400.0, "CALL", day, NDX_OSI)])))]
            result = self._run_oi(folder, root, sources, ["2020-01-02"])
            asof = [row for row in _read_parts(result["refs"]["asof_aggregates"])
                    if row["chain"] == "NDX" and row["cut_label"] == "09:30"][0]
            self.assertGreater(asof["universe"], 0)
            self.assertEqual(asof["available"], 0)
            self.assertEqual(asof["available_fraction"], 0.0)
            self.assertGreaterEqual(asof["listing_only"], 1)
            import pyarrow.parquet as pq
            coverage = [row for row in pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
                        if row["chain"] == "NDX"][0]
            self.assertEqual(coverage["listed_without_oi"], 1)

    def test_nanoseconds_above_float53_preserved(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ns = 1_778_066_221_908_000_123
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            sources = [_admit(1, p, "NDX", "open_interest", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__open-interest", "oi",
                              _write_parquet(root / p, _oi([
                                  ("NDX", exp, 3400.0, "CALL", 7, day, ns, NDX_OSI)])))]
            result = self._run_oi(folder, root, sources, ["2020-01-02"])
            reports = _read_parts(result["refs"]["reports"])
            self.assertEqual(reports[0]["first_ts_event_ns"], ns)
            intervals = _read_parts(result["refs"]["asof_intervals"])
            self.assertTrue(any(row["ts_event_ns"] == ns for row in intervals))

    def test_stage_crossing_excludes_delta_from_year_and_stage(self):
        day_a, day_b = date(2022, 12, 30), date(2023, 1, 3)
        exp = date(2023, 6, 16)
        osi = "NDX   230616C03400000"
        ts_a = local_timestamp(day_a, time(6, 30), ZONE)
        ts_b = local_timestamp(day_b, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p_a = "thetadata-opra/opra__ndx-options__open-interest/2022-12-30.parquet"
            p_b = "thetadata-opra/opra__ndx-options__open-interest/2023-01-03.parquet"
            sources = [
                _admit(1, p_a, "NDX", "open_interest", "2022-12-30",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_a, _oi([("NDX", exp, 3400.0, "CALL", 100, day_a, ts_a, osi)]))),
                _admit(2, p_b, "NDX", "open_interest", "2023-01-03",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p_b, _oi([("NDX", exp, 3400.0, "CALL", 120, day_b, ts_b, osi)]))),
            ]
            result = self._run_oi(folder, root, sources, ["2022-12-30", "2023-01-03"])
            life = _read_parts(result["refs"]["lifecycle"])
            self.assertTrue(any(row["first_delta"] == 20 and row["first_within_stage"] is False
                                and row["first_within_year"] is False for row in life))
            groups = json.loads(Path(result["refs"]["statistics"]["path"]).read_text())["groups"]
            all_period = groups["NDX|all_period|first|all|all"]["statistics"]["metrics"]["next_delta"]
            year = groups["NDX|year_2023|first|all|all"]["statistics"]["metrics"]["next_delta"]
            stage = groups["NDX|stage_development|first|all|all"]["statistics"]["metrics"]["next_delta"]
            self.assertEqual(all_period["estimate"], 20)
            self.assertIsNone(year["estimate"])
            self.assertIsNone(stage["estimate"])

    def test_all_missing_metric_kept_and_ratio_does_not_abort(self):
        with tempfile.TemporaryDirectory() as folder:
            outputs = self._outputs(folder)
            rows = [{
                "chain": "NDX", "request_date": "2020-01-02", "intended": True, "primary": True,
                "first": {"oi_sum": 100, "oi_n": 1, "zero_n": 0, "seconds_sum": 0, "seconds_n": 0,
                          "usable_n": 1, "common_n": 0, "common_first_sum": 0, "common_last_sum": 0,
                          "paired_diff_sum": 0, "own_n": 1},
                "last": {"oi_sum": 100, "oi_n": 1, "zero_n": 0, "seconds_sum": 0, "seconds_n": 0,
                         "usable_n": 1, "common_n": 0, "common_first_sum": 0, "common_last_sum": 0,
                         "paired_diff_sum": 0, "own_n": 1},
                "lifecycle_all": {"first": {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0,
                                            "n_neg": 0, "n_censor_missing": 0, "n_censor_expired": 0,
                                            "n_censor_boundary": 0, "n_attempts": 0, "n_first_observed": 0,
                                            "n_prior_missing": 0},
                                  "last": {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0,
                                           "n_neg": 0, "n_censor_missing": 0, "n_censor_expired": 0,
                                           "n_censor_boundary": 0, "n_attempts": 0, "n_first_observed": 0,
                                           "n_prior_missing": 0}},
                "lifecycle_within_stage": {"first": {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0,
                                                     "n_neg": 0, "n_censor_missing": 0, "n_censor_expired": 0,
                                                     "n_censor_boundary": 0, "n_attempts": 0, "n_first_observed": 0,
                                                     "n_prior_missing": 0},
                                           "last": {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0,
                                                    "n_neg": 0, "n_censor_missing": 0, "n_censor_expired": 0,
                                                    "n_censor_boundary": 0, "n_attempts": 0, "n_first_observed": 0,
                                                    "n_prior_missing": 0}},
                "lifecycle_within_year": {"first": {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0,
                                                    "n_neg": 0, "n_censor_missing": 0, "n_censor_expired": 0,
                                                    "n_censor_boundary": 0, "n_attempts": 0, "n_first_observed": 0,
                                                    "n_prior_missing": 0},
                                          "last": {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0,
                                                   "n_neg": 0, "n_censor_missing": 0, "n_censor_expired": 0,
                                                   "n_censor_boundary": 0, "n_attempts": 0, "n_first_observed": 0,
                                                   "n_prior_missing": 0}},
                "asof": {}, "listing_denominator_known": False, "listing_count": None,
                "coverage_listed_with_oi": None, "listed_without_oi": None,
                "usable_report_count": 1, "update_candidate_count": 0, "update_n": 0, "update_diff_sum": 0,
                "position_mapping_count": 0, "position_mapping_agree_count": 0,
                "event_local_mismatch_count": 0, "future_flag_count": 0, "late_flag_count": 0,
                "by_right": {}, "by_dte": {},
            }]
            stats = run_statistics(
                rows, protocol=PROTOCOL, outputs=outputs,
                intended_all=["2020-01-02"], selected_dates=["2020-01-02"],
                chains=["NDX"], stages=STAGES,
            )
            metrics = stats["groups"]["NDX|all_period|first|all|all"]["statistics"]["metrics"]
            self.assertIn("coverage_fraction", metrics)
            self.assertIsNone(metrics["coverage_fraction"]["estimate"])
            ratios = stats["groups"]["NDX|all_period|first|all|all"]["statistics"]["ratios"]
            self.assertIn("common_first_over_last", ratios)
            self.assertIsNone(ratios["common_first_over_last"]["estimate"])

    def test_raw_support_does_not_change_equal_date_ci(self):
        def row(day, oi_sum, oi_n):
            empty_life = {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0, "n_neg": 0,
                          "n_censor_missing": 0, "n_censor_expired": 0, "n_censor_boundary": 0,
                          "n_attempts": 0, "n_first_observed": 0, "n_prior_missing": 0}
            acc = {"oi_sum": oi_sum, "oi_n": oi_n, "zero_n": 0, "seconds_sum": 0, "seconds_n": 0,
                   "usable_n": oi_n, "common_n": 0, "common_first_sum": 0, "common_last_sum": 0,
                   "paired_diff_sum": 0, "own_n": oi_n}
            return {
                "chain": "NDX", "request_date": day, "intended": True, "primary": True,
                "first": acc, "last": dict(acc),
                "lifecycle_all": {"first": dict(empty_life), "last": dict(empty_life)},
                "lifecycle_within_stage": {"first": dict(empty_life), "last": dict(empty_life)},
                "lifecycle_within_year": {"first": dict(empty_life), "last": dict(empty_life)},
                "asof": {}, "listing_denominator_known": False, "listing_count": None,
                "coverage_listed_with_oi": None, "listed_without_oi": None,
                "usable_report_count": oi_n, "update_candidate_count": 0, "update_n": 0, "update_diff_sum": 0,
                "position_mapping_count": 0, "position_mapping_agree_count": 0,
                "event_local_mismatch_count": 0, "future_flag_count": 0, "late_flag_count": 0,
                "by_right": {}, "by_dte": {},
            }

        dates = ["2020-01-02", "2020-01-03"]
        with tempfile.TemporaryDirectory() as folder:
            uneven = run_statistics(
                [row("2020-01-02", 20, 2), row("2020-01-03", 2000, 100)],
                protocol=PROTOCOL, outputs=self._outputs(folder + "/a"),
                intended_all=dates, selected_dates=dates, chains=["NDX"], stages=STAGES,
            )
        with tempfile.TemporaryDirectory() as folder:
            even = run_statistics(
                [row("2020-01-02", 500, 50), row("2020-01-03", 1000, 50)],
                protocol=PROTOCOL, outputs=self._outputs(folder + "/b"),
                intended_all=dates, selected_dates=dates, chains=["NDX"], stages=STAGES,
            )
        left = uneven["groups"]["NDX|all_period|first|all|all"]["statistics"]["metrics"]["oi_level_date_mean"]
        right = even["groups"]["NDX|all_period|first|all|all"]["statistics"]["metrics"]["oi_level_date_mean"]
        self.assertEqual(left["estimate"], 15.0)
        self.assertEqual(right["estimate"], 15.0)
        self.assertEqual(left["bootstrap"]["lower"], right["bootstrap"]["lower"])
        self.assertEqual(left["bootstrap"]["upper"], right["bootstrap"]["upper"])
        self.assertEqual(left["support"]["events"], 102)
        self.assertEqual(right["support"]["events"], 100)

    def test_wrong_root_float_oi_and_fine_strike_are_invalid(self):
        import pyarrow as pa
        day = date(2020, 1, 2)
        ts = local_timestamp(day, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            table = _oi([
                ("NDX", date(2020, 1, 17), 3400.0, "CALL", 4, day, ts, NDXP_OSI),
                ("NDX", date(2020, 1, 17), 3400.0001, "CALL", 5, day, ts, NDX_OSI),
            ])
            meta = _write_parquet(root / p, table)
            result = self._run_oi(folder, root, [_admit(
                1, p, "NDX", "open_interest", "2020-01-02",
                "thetadata-opra/opra__ndx-options__open-interest", "oi", meta)], ["2020-01-02"])
            reasons = {row["invalid_reason"] for row in _read_parts(result["refs"]["exceptions"])}
            self.assertIn("osi_root_or_symbol_chain_mismatch", reasons)
            self.assertIn("inexact_or_nonfinite_strike", reasons)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            float_table = pa.table({
                "symbol": pa.array(["NDX"], type=pa.large_string()),
                "expiration": pa.array([date(2020, 1, 17)], type=pa.date32()),
                "strike": pa.array([3400.0], type=pa.float64()),
                "right": pa.array(["CALL"], type=pa.large_string()),
                "open_interest": pa.array([4.0], type=pa.float64()),
                "request_date": pa.array([day], type=pa.date32()),
                "ts_event": pa.array([ts], type=pa.timestamp("ns", tz="UTC")),
                "osi_symbol": pa.array([NDX_OSI], type=pa.large_string()),
            })
            meta = _write_parquet(root / p, float_table)
            with self.assertRaises(IntegrityError):
                self._run_oi(folder, root, [_admit(
                    1, p, "NDX", "open_interest", "2020-01-02",
                    "thetadata-opra/opra__ndx-options__open-interest", "oi", meta)], ["2020-01-02"])

    def test_multiple_input_files_same_identity_are_consumed(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p1 = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02-a.parquet"
            p2 = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02-b.parquet"
            sources = [
                _admit(1, p1, "NDX", "open_interest", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p1, _oi([("NDX", exp, 3400.0, "CALL", 11, day, ts, NDX_OSI)]))),
                _admit(2, p2, "NDX", "open_interest", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__open-interest", "oi",
                       _write_parquet(root / p2, _oi([("NDX", exp, 3400.0, "CALL", 11, day, ts, NDX_OSI)]))),
            ]
            result = self._run_oi(folder, root, sources, ["2020-01-02"])
            membership = _read_parts(result["refs"]["membership"])
            self.assertEqual(len(membership), 2)
            self.assertEqual({row["file_id"] for row in membership}, {1, 2})
            reports = _read_parts(result["refs"]["reports"])
            self.assertEqual(reports[0]["alias_multiplicity"], 2)
            self.assertEqual(reports[0]["first_oi"], 11)

    def test_interval_reconstruction_matches_three_cuts(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(6, 30), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            p = "thetadata-opra/opra__ndx-options__open-interest/2020-01-02.parquet"
            sources = [_admit(1, p, "NDX", "open_interest", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__open-interest", "oi",
                              _write_parquet(root / p, _oi([
                                  ("NDX", exp, 3400.0, "CALL", 44, day, ts, NDX_OSI)])))]
            result = self._run_oi(folder, root, sources, ["2020-01-02"])
            intervals = _read_parts(result["refs"]["asof_intervals"])
            asof = [row for row in _read_parts(result["refs"]["asof_aggregates"]) if row["chain"] == "NDX"]
            for row in asof:
                visible = reconstruct_asof_intervals(intervals, row["cut_ns"], row["cut_date"])
                available = sum(1 for item in visible if not item["ambiguous"] and item["open_interest"] is not None)
                self.assertEqual(available, row["available"])
                self.assertEqual(visible[0]["open_interest"], 44)


if __name__ == "__main__":
    unittest.main()

