"""Independent options quote-quality fixtures. Each case goes through actual run()."""
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
from trading_research.operations.artifacts import ArtifactStore
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.options_oi_measurements import (
    coverage_schema as oi_coverage_schema, cut_ns_on, identity_schema,
    interval_schema, report_schema,
)
from trading_research.research.options_quote_measurements import (
    ALL_CUTS, BASE_CLASSES, FAMILY, INTERVAL_RECONSTRUCTION, LOCAL_ID_BASE, VERSION,
    combine_partition_results, implementation_hashes, quote_dte_bucket, run,
    scientific_hash, utc_cut_ns,
)
from trading_research.research.options_quote_statistics import (
    PRESPECIFIED, date_balanced_point, raw_mean,
)


PROTOCOL = json.loads(Path("/workspace/trading-research/validation/OPTIONS_QUOTE_QUALITY_SUPPORT_V1.json").read_text())
CALENDAR = CashCalendar(Path(PROTOCOL["cash_calendar"]["path"]))
ZONE = "America/New_York"
NDX_OSI = "NDX   200117C03400000"
NDX_PUT = "NDX   200117P03400000"
QQQ_OSI = "QQQ   200117C00200000"
VIX_OSI = "VIX   200422C00037500"
QUOTE_SCHEMA = (
    "symbol: large_string\nexpiration: date32[day]\nstrike: double\nright: large_string\n"
    "bid_size: int64\nask_size: int64\nbid_exchange: int64\nask_exchange: int64\n"
    "bid_condition: int64\nask_condition: int64\nbid: double\nask: double\n"
    "request_date: date32[day]\nts_event: timestamp[ns, tz=UTC]\nosi_symbol: large_string"
)
CASH_SCHEMA = (
    "date: date32[day]\nsymbol: large_string\nopen: double\nhigh: double\n"
    "low: double\nclose: double\nadjusted_close: double\nvolume: double"
)
ETF_SCHEMA = "t: int64\no: double\nh: double\nl: double\nc: double\nv: double\ninstrument_id: int32"
FRED_SCHEMA = (
    "date: date32[day]\nseries_id: large_string\ntenor_days: int64\n"
    "rate_pct: double\nrealtime_start: date32[day]\nrealtime_end: date32[day]"
)
ACTION_SCHEMA = "ex_date: date32[day]\ndividend: double\nsplit_ratio: double\nsymbol: large_string"


def _write_parquet(path, table, row_group_size=None):
    import pyarrow.parquet as pq
    path.parent.mkdir(parents=True, exist_ok=True)
    if row_group_size is None:
        pq.write_table(table, path)
    else:
        pq.write_table(table, path, row_group_size=row_group_size)
    raw = path.read_bytes()
    return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "rows": len(table)}


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))
    raw = path.read_bytes()
    return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "rows": 0}


def _quotes(rows):
    import pyarrow as pa
    return pa.table({
        "symbol": pa.array([row[0] for row in rows], type=pa.large_string()),
        "expiration": pa.array([row[1] for row in rows], type=pa.date32()),
        "strike": pa.array([row[2] for row in rows], type=pa.float64()),
        "right": pa.array([row[3] for row in rows], type=pa.large_string()),
        "bid_size": pa.array([row[4] for row in rows], type=pa.int64()),
        "ask_size": pa.array([row[5] for row in rows], type=pa.int64()),
        "bid_exchange": pa.array([row[6] for row in rows], type=pa.int64()),
        "ask_exchange": pa.array([row[7] for row in rows], type=pa.int64()),
        "bid_condition": pa.array([row[8] for row in rows], type=pa.int64()),
        "ask_condition": pa.array([row[9] for row in rows], type=pa.int64()),
        "bid": pa.array([row[10] for row in rows], type=pa.float64()),
        "ask": pa.array([row[11] for row in rows], type=pa.float64()),
        "request_date": pa.array([row[12] for row in rows], type=pa.date32()),
        "ts_event": pa.array([row[13] for row in rows], type=pa.timestamp("ns", tz="UTC")),
        "osi_symbol": pa.array([row[14] for row in rows], type=pa.large_string()),
    })


def _q(symbol, exp, strike, right, bid_sz, ask_sz, bid_ex, ask_ex, bid_c, ask_c,
       bid, ask, req, ts, osi):
    return (symbol, exp, strike, right, bid_sz, ask_sz, bid_ex, ask_ex, bid_c, ask_c,
            bid, ask, req, ts, osi)


def _admit(file_id, rel, chain, family, request_date, dataset_id, schema_id, meta, role="quote",
           fmt=".parquet", marker=None):
    source = {
        "path": rel, "size_bytes": meta["size_bytes"], "chain": chain, "role": role,
        "source_family": family, "request_date": request_date, "dataset_id": dataset_id,
    }
    rec = {
        "file_id": file_id, "source": source, "sha256": meta["sha256"],
        "rows": meta.get("rows"), "schema_id": schema_id, "format": fmt,
    }
    if marker is not None:
        rec["marker"] = marker
    return rec


def _read_parts(refs):
    import pyarrow.parquet as pq
    if refs is None:
        return []
    if isinstance(refs, dict) and "path" in refs:
        refs = [refs]
    rows = []
    for ref in refs:
        rows.extend(pq.read_table(ref["path"]).to_pylist())
    return rows


def _near_quoted(rows, cut="10:00"):
    return [row for row in rows if row["cut_label"] == cut and row.get("source_family") == "near"
            and row.get("quoted")]


class QuoteFixtureCase(unittest.TestCase):
    def _protocol(self, root):
        payload = dict(PROTOCOL)
        payload["data_root"] = str(root)
        return payload

    def _outputs(self, folder, name="out"):
        return BoundedOutputs(Path(folder) / name, maximum_total_bytes=32 * 1024 * 1024,
                              maximum_file_bytes=16 * 1024 * 1024)

    def _store(self, folder, name="cas"):
        return ArtifactStore(Path(folder) / name)

    def _admitted(self, sources, schemas=None):
        return {
            "kind": "options_quote_admitted_sources_v1",
            "source_files": len(sources),
            "sources": sources,
            "schemas": schemas or {"quote_1m": QUOTE_SCHEMA},
            "samples": {},
        }

    def _oi_coverage_table(self, dates, chain, *, listing_file_present=True,
                           listing_status="present", listing_denominator_known=True,
                           listing_count=1):
        import pyarrow as pa
        schema = oi_coverage_schema()
        rows = []
        for day in dates:
            row = {name: None for name in schema.names}
            row.update({
                "chain": chain, "request_date": day, "intended": True,
                "closed": False, "primary": True,
                "listing_file_present": listing_file_present,
                "oi_file_present": True, "both_files_absent": not listing_file_present,
                "listing_status": listing_status, "oi_status": "present",
                "listing_count": listing_count if listing_file_present else None,
                "oi_count": 1, "oi_zero_count": 0, "intersection_count": 1 if listing_file_present else 0,
                "union_count": 1, "listed_without_oi": 0, "oi_without_listing": 0,
                "listing_denominator_known": listing_denominator_known,
                "coverage_listed_with_oi": 1.0 if listing_file_present else None,
                "invalid_row_count": 0, "missing_clock_count": 0,
                "event_local_mismatch_count": 0, "future_flag_count": 0,
                "late_flag_count": 0, "usable_report_count": 1,
                "conflict_report_count": 0, "update_candidate_count": 0,
                "gt60_dte_retained": 0, "vix_listing_unknown": chain == "VIX",
                "position_mapping_agree_count": 0, "position_mapping_count": 0,
            })
            rows.append(row)
        return pa.table({name: [row[name] for row in rows] for name in schema.names}, schema=schema)

    def _oi_population(self, folder, *, chain="NDX", osi=NDX_OSI, exp="2020-01-17",
                       milli=3400000, right="CALL", cid=1, dates=None, listed=True,
                       intervals=None, first_oi=10, last_oi=None,
                       listing_file_present=True, listing_status="present",
                       listing_denominator_known=True):
        import pyarrow as pa
        import pyarrow.parquet as pq
        dates = dates or ["2020-01-02"]
        ident = pa.table({
            "contract_id": pa.array([cid], type=pa.int32()),
            "chain": pa.array([chain]), "osi_symbol": pa.array([osi]),
            "expiration": pa.array([exp]), "millistrike": pa.array([milli], type=pa.int64()),
            "right": pa.array([right]),
        }, schema=identity_schema())
        ident_path = Path(folder) / "oi-identity.parquet"
        pq.write_table(ident, ident_path)
        reports = []
        for day in dates:
            reports.append({
                "contract_id": cid, "chain": chain, "request_date": day, "listed": listed,
                "first_oi": first_oi, "first_ts_event_ns": 1, "first_file_id": 1,
                "first_row_index": 0, "last_oi": last_oi, "last_ts_event_ns": None,
                "last_file_id": None, "last_row_index": None, "alias_multiplicity": 1,
                "same_time_conflict": False, "conflict_disposition": "none",
                "update_candidate": False, "observed_update_difference": None,
                "certified_revision": False, "usable_for_statistics": True,
                "n_source_rows": 1, "n_distinct_times": 1, "support_observations": 1,
                "dte": 15, "dte_bucket": "15-30", "right": right,
                "causal_feature_eligible": False,
            })
        report_table = pa.table({name: [row[name] for row in reports] for name in report_schema().names},
                                schema=report_schema())
        report_path = Path(folder) / "oi-reports.parquet"
        pq.write_table(report_table, report_path)
        if intervals is None:
            intervals = [{
                "contract_id": cid, "chain": chain, "open_interest": first_oi,
                "ts_event_ns": cut_ns_on(date.fromisoformat(dates[0]), "06:30"),
                "request_date": dates[0], "file_id": 1, "row_index": 0,
                "ambiguous": False,
                "valid_from_ns": cut_ns_on(date.fromisoformat(dates[0]), "06:30"),
                "valid_to_ns": None, "expiration": exp, "causal_feature_eligible": False,
            }]
        interval_table = pa.table(
            {name: [row.get(name) for row in intervals] for name in interval_schema().names},
            schema=interval_schema(),
        )
        interval_path = Path(folder) / "oi-intervals.parquet"
        pq.write_table(interval_table, interval_path)
        cov_table = self._oi_coverage_table(
            dates, chain, listing_file_present=listing_file_present,
            listing_status=listing_status, listing_denominator_known=listing_denominator_known,
            listing_count=1 if listed else 0,
        )
        cov_path = Path(folder) / "oi-coverage.parquet"
        pq.write_table(cov_table, cov_path)

        def _ref(path, kind, rows):
            raw = path.read_bytes()
            return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                    "size_bytes": len(raw), "kind": kind, "rows": rows}

        return {
            "passed": True,
            "family": "Research-Options-OI-report-lifecycle-v1",
            "version": "options-oi-report-lifecycle-measurement-v2",
            "refs": {
                "identity_map": [_ref(ident_path, "options_oi_identity_map_v2", 1)],
                "reports": [_ref(report_path, "options_oi_resolved_reports_v2", len(reports))],
                "asof_intervals": [_ref(interval_path, "options_oi_asof_intervals_v2", len(intervals))],
                "coverage": [_ref(cov_path, "options_oi_coverage_v2", len(dates))],
            },
        }

    def _run(self, folder, root, sources, dates, chains, oi=None, schemas=None):
        return run(
            protocol=self._protocol(root), admitted=self._admitted(sources, schemas),
            oi_population=oi, store=self._store(folder),
            outputs=self._outputs(folder), selected_dates=dates, selected_chains=chains,
        )

    def test_dte_buckets_are_quote_protocol_not_oi(self):
        self.assertEqual(quote_dte_bucket(0), "0")
        self.assertEqual(quote_dte_bucket(1), "1")
        self.assertEqual(quote_dte_bucket(7), "2-7")
        self.assertEqual(quote_dte_bucket(8), "8-14")
        self.assertEqual(quote_dte_bucket(14), "8-14")
        self.assertEqual(quote_dte_bucket(15), "15-30")
        self.assertEqual(quote_dte_bucket(30), "15-30")
        self.assertEqual(quote_dte_bucket(31), "31-60")
        self.assertEqual(quote_dte_bucket(61), "61+")
        self.assertEqual(quote_dte_bucket(-1), "expired")
        self.assertNotEqual(quote_dte_bucket(20), "8-30")

    def test_bad_right_and_osi_mismatch_are_invalid_identity(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "PUT", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
                _q("NDX", exp, 3500.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            self.assertTrue(result["passed"])
            self.assertIs(result["full_family_complete"], False)
            self.assertIs(result["joined_coverage_complete"], False)
            self.assertIs(result["clock_interpretation"]["causal_feature_eligible"], False)
            exceptions = _read_parts(result["refs"]["exceptions"])
            reasons = {row["invalid_reason"] for row in exceptions}
            self.assertIn("strike_or_osi_identity_conflict", reasons)
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            classes = {row["base_class"] for row in board}
            self.assertIn("invalid_identity", classes)
            self.assertIn("two_sided", classes)
            self.assertTrue(any(row["invalid_reason"] and row["file_id"] == 1 and row["row_index_start"] is not None
                                for row in exceptions))
            valid = [row for row in board if row["base_class"] == "two_sided"]
            invalid = [row for row in board if row["base_class"] == "invalid_identity"]
            self.assertTrue(valid)
            self.assertTrue(invalid)
            self.assertTrue(all(row["identity_resolved"] for row in valid))
            self.assertTrue(all(not row["identity_resolved"] and row["contract_id"] == 0 for row in invalid))

    def test_zero_ask_only_locked_crossed_sizes_and_nonfinite(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            inf = float("inf")
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 0.0, 1.2, day, ts, NDX_OSI),
                _q("NDX", exp, 3410.0, "CALL", 10, 10, 1, 1, 50, 50, 1.2, 0.0, day, ts, "NDX   200117C03410000"),
                _q("NDX", exp, 3420.0, "CALL", 10, 10, 1, 1, 50, 50, 1.5, 1.5, day, ts, "NDX   200117C03420000"),
                _q("NDX", exp, 3430.0, "CALL", 10, 10, 1, 1, 50, 50, 2.0, 1.0, day, ts, "NDX   200117C03430000"),
                _q("NDX", exp, 3440.0, "CALL", 0, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, "NDX   200117C03440000"),
                _q("NDX", exp, 3450.0, "CALL", -1, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, "NDX   200117C03450000"),
                _q("NDX", exp, 3460.0, "CALL", 10, 10, 1, 1, 50, 50, inf, 1.2, day, ts, "NDX   200117C03460000"),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            by_osi = {row["osi_symbol"]: row for row in board}
            self.assertEqual(by_osi[NDX_OSI]["base_class"], "one_sided")
            self.assertTrue(by_osi[NDX_OSI]["zero_bid"])
            self.assertEqual(by_osi["NDX   200117C03410000"]["base_class"], "one_sided")
            self.assertTrue(by_osi["NDX   200117C03410000"]["zero_ask"])
            self.assertEqual(by_osi["NDX   200117C03420000"]["base_class"], "locked")
            self.assertTrue(by_osi["NDX   200117C03420000"]["usable"])
            self.assertEqual(by_osi["NDX   200117C03430000"]["base_class"], "crossed")
            self.assertFalse(by_osi["NDX   200117C03430000"]["usable"])
            self.assertEqual(by_osi["NDX   200117C03440000"]["base_class"], "two_sided")
            self.assertTrue(by_osi["NDX   200117C03440000"]["nonpositive_size"])
            self.assertFalse(by_osi["NDX   200117C03440000"]["usable"])
            self.assertTrue(by_osi["NDX   200117C03450000"]["negative_size"])
            self.assertEqual(by_osi["NDX   200117C03460000"]["base_class"], "invalid_numeric")
            self.assertTrue(by_osi["NDX   200117C03460000"]["nonfinite_price"])

    def test_condition_zero_all_zero_then_condition_50_valid(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts0 = local_timestamp(day, time(9, 30), ZONE)
        ts1 = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 0, 0, 0, 0, 0, 0, 0.0, 0.0, day, ts0, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 12, 1, 1, 50, 50, 1.0, 1.2, day, ts1, NDX_OSI),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            quality = _read_parts(result["refs"]["source_quality"])
            self.assertTrue(any(row["raw_all_zero"] >= 1 and row["raw_condition_zero"] >= 1 for row in quality))
            self.assertTrue(any(row["raw_two_sided"] >= 1 for row in quality))
            board_0930 = _near_quoted(_read_parts(result["refs"]["cut_board"]), "09:30")
            board_1000 = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            self.assertTrue(any(row["base_class"] == "all_zero" and row["condition_zero"] for row in board_0930))
            self.assertTrue(any(row["base_class"] == "two_sided" and row["usable"] for row in board_1000))

    def test_near_broad_alias_multiplicity_two_one_union_row(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            near = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            broad = "thetadata-opra/opra__ndx-options__quote-1m__dte60/2020-01-02.parquet"
            row = _q("NDX", exp, 3400.0, "CALL", 10, 10, 5, 5, 50, 50, 1.25, 1.35, day, ts, NDX_OSI)
            sources = [
                _admit(1, near, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / near, _quotes([row]))),
                _admit(2, broad, "NDX", "broad", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte60__atm10",
                       "quote_1m", _write_parquet(root / broad, _quotes([row]))),
            ]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            aliases = [row for row in _read_parts(result["refs"]["alias_conflict"])
                       if row["source_family"] == "union"]
            self.assertTrue(any(row["max_multiplicity"] == 2 and row["payload_equal_groups"] >= 1
                                and not row["example_conflict"] and row["alias_row_mass"] == 2
                                for row in aliases))
            union = [row for row in _read_parts(result["refs"]["cut_board"])
                     if row["source_family"] == "union" and row["cut_label"] == "10:00" and row["quoted"]]
            self.assertEqual(len(union), 1)
            self.assertEqual(union[0]["alias_multiplicity"], 2)
            self.assertFalse(union[0]["conflict"])
            self.assertEqual(union[0]["bid"], 1.25)

    def test_payload_conflict_has_no_winner(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            near = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            broad = "thetadata-opra/opra__ndx-options__quote-1m__dte60/2020-01-02.parquet"
            a = _q("NDX", exp, 3400.0, "CALL", 10, 10, 5, 5, 50, 50, 1.25, 1.35, day, ts, NDX_OSI)
            b = _q("NDX", exp, 3400.0, "CALL", 10, 10, 5, 5, 50, 50, 1.40, 1.50, day, ts, NDX_OSI)
            sources = [
                _admit(1, near, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / near, _quotes([a]))),
                _admit(2, broad, "NDX", "broad", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte60__atm10",
                       "quote_1m", _write_parquet(root / broad, _quotes([b]))),
            ]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            union = [row for row in _read_parts(result["refs"]["cut_board"])
                     if row["source_family"] == "union" and row["cut_label"] == "10:00" and row["quoted"]]
            self.assertEqual(len(union), 1)
            self.assertTrue(union[0]["conflict"])
            self.assertEqual(union[0]["base_class"], "conflict")
            self.assertFalse(union[0]["usable"])
            self.assertIsNone(union[0]["bid"])
            self.assertIsNone(union[0]["ask"])
            self.assertIsNone(union[0]["mid"])
            self.assertIsNone(union[0]["spread"])
            self.assertIsNotNone(union[0]["diagnostic_bid"])

    def test_newest_conflict_masks_older_valid(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts_old = local_timestamp(day, time(9, 45), ZONE)
        ts_new = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts_old, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 2.0, 2.2, day, ts_new, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 3.0, 3.2, day, ts_new, NDX_OSI),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            self.assertEqual(len(board), 1)
            self.assertTrue(board[0]["conflict"])
            self.assertNotEqual(board[0]["bid"], 1.0)
            self.assertFalse(board[0]["usable"])

    def test_nanoseconds_over_2_53_roundtrip_and_wrong_unit_rejects(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        big = 9_007_199_254_740_992 + 12345
        self.assertGreater(big, 2 ** 53)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            import pyarrow as pa
            exact = local_timestamp(day, time(10, 0), ZONE) + 123
            self.assertGreater(exact, 2 ** 53)
            table = pa.table({
                "symbol": pa.array(["NDX"], type=pa.large_string()),
                "expiration": pa.array([exp], type=pa.date32()),
                "strike": pa.array([3400.0]),
                "right": pa.array(["CALL"], type=pa.large_string()),
                "bid_size": pa.array([10], type=pa.int64()),
                "ask_size": pa.array([10], type=pa.int64()),
                "bid_exchange": pa.array([1], type=pa.int64()),
                "ask_exchange": pa.array([1], type=pa.int64()),
                "bid_condition": pa.array([50], type=pa.int64()),
                "ask_condition": pa.array([50], type=pa.int64()),
                "bid": pa.array([1.0]), "ask": pa.array([1.2]),
                "request_date": pa.array([day], type=pa.date32()),
                "ts_event": pa.array([exact], type=pa.timestamp("ns", tz="UTC")),
                "osi_symbol": pa.array([NDX_OSI], type=pa.large_string()),
            })
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            self.assertTrue(any(row["ts_event_ns"] == exact for row in board))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            import pyarrow as pa
            bad = pa.table({
                "symbol": pa.array(["NDX"], type=pa.large_string()),
                "expiration": pa.array([exp], type=pa.date32()),
                "strike": pa.array([3400.0]),
                "right": pa.array(["CALL"], type=pa.large_string()),
                "bid_size": pa.array([10], type=pa.int64()),
                "ask_size": pa.array([10], type=pa.int64()),
                "bid_exchange": pa.array([1], type=pa.int64()),
                "ask_exchange": pa.array([1], type=pa.int64()),
                "bid_condition": pa.array([50], type=pa.int64()),
                "ask_condition": pa.array([50], type=pa.int64()),
                "bid": pa.array([1.0]), "ask": pa.array([1.2]),
                "request_date": pa.array([day], type=pa.date32()),
                "ts_event": pa.array([1_577_880_000_000_000], type=pa.timestamp("us", tz="UTC")),
                "osi_symbol": pa.array([NDX_OSI], type=pa.large_string()),
            })
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, bad))]
            with self.assertRaises(IntegrityError):
                self._run(folder, root, sources, ["2020-01-02"], ["NDX"])

    def test_unsorted_contract_major_row_groups_do_not_reset_run(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        t0 = local_timestamp(day, time(9, 31), ZONE)
        t1 = local_timestamp(day, time(9, 32), ZONE)
        t2 = local_timestamp(day, time(9, 33), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            osi_b = "NDX   200117C03410000"
            rows = [
                _q("NDX", exp, 3410.0, "CALL", 10, 10, 1, 1, 50, 50, 2.0, 2.2, day, t2, osi_b),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, t1, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, t0, NDX_OSI),
            ]
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, _quotes(rows), row_group_size=1))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            board = [row for row in _near_quoted(_read_parts(result["refs"]["cut_board"]))
                     if row["osi_symbol"] == NDX_OSI]
            self.assertEqual(len(board), 1)
            self.assertEqual(board[0]["run_lower_bound_ns"], t0)
            self.assertEqual(board[0]["ts_event_ns"], t1)
            self.assertTrue(board[0]["run_continuity_observed"])
            self.assertNotEqual(board[0]["sample_age_ns"], board[0]["unchanged_payload_age_ns"])

    def test_sample_age_and_payload_age_diverge_and_gap_breaks_run(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        t0 = local_timestamp(day, time(9, 31), ZONE)
        t1 = local_timestamp(day, time(9, 32), ZONE)
        t_gap = local_timestamp(day, time(9, 50), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, t0, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, t1, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, t_gap, NDX_OSI),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            self.assertEqual(len(board), 1)
            self.assertEqual(board[0]["ts_event_ns"], t_gap)
            self.assertEqual(board[0]["run_lower_bound_ns"], t_gap)
            self.assertEqual(board[0]["sample_age_ns"], board[0]["unchanged_payload_age_ns"])
            self.assertFalse(board[0]["run_continuity_observed"])

    def test_missing_near_file_vs_json_empty_marker_and_vix_listing_unknown(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        vix_exp = date(2020, 4, 22)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            broad = "thetadata-opra/opra__ndx-options__quote-1m__dte60/2020-01-02.parquet"
            marker = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-03.empty.json"
            vix = "thetadata-opra/opra__vix-options__quote-1m__dte60-full-chain/2020-01-02.parquet"
            sources = [
                _admit(1, broad, "NDX", "broad", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte60__atm10",
                       "quote_1m", _write_parquet(root / broad, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)]))),
                _admit(2, marker, "NDX", "near", "2020-01-03",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_json(root / marker, {"empty_marker": True}),
                       fmt=".json", marker="empty"),
                _admit(3, vix, "VIX", "vix_full", "2020-01-02",
                       "thetadata-opra/opra__vix-options__quote-1m__dte60-full-chain",
                       "quote_1m", _write_parquet(root / vix, _quotes([
                           _q("VIX", vix_exp, 37.5, "CALL", 4, 4, 1, 1, 50, 50, 2.0, 2.5, day, ts, VIX_OSI)]))),
            ]
            result = self._run(folder, root, sources, ["2020-01-02", "2020-01-03"], ["NDX", "VIX"])
            import pyarrow.parquet as pq
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            missing_near = [row for row in coverage if row["chain"] == "NDX" and row["request_date"] == "2020-01-02"
                            and row["source_family"] == "near"]
            empty_near = [row for row in coverage if row["chain"] == "NDX" and row["request_date"] == "2020-01-03"
                          and row["source_family"] == "near"]
            self.assertTrue(missing_near)
            self.assertTrue(all(row["missing_file"] and not row["empty_marker"] for row in missing_near))
            self.assertTrue(empty_near)
            self.assertTrue(all(row["empty_marker"] and not row["missing_file"] for row in empty_near))
            vix_rows = [row for row in coverage if row["chain"] == "VIX"]
            self.assertTrue(vix_rows)
            self.assertTrue(all(row["vix_listing_unknown"] and not row["listing_known"] for row in vix_rows))

    def test_early_close_1500_not_applicable_and_dst_vs_15utc(self):
        winter = date(2020, 1, 2)
        early = date(2020, 11, 27)
        exp = date(2020, 12, 18)
        osi = "NDX   201218C03400000"
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            sources = []
            fid = 1
            for day in (winter, early):
                rel = f"thetadata-opra/opra__ndx-options__quote-1m__dte14/{day.isoformat()}.parquet"
                ts = local_timestamp(day, time(10, 0), ZONE)
                sources.append(_admit(
                    fid, rel, "NDX", "near", day.isoformat(),
                    "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                    "quote_1m", _write_parquet(root / rel, _quotes([
                        _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, osi)])),
                ))
                fid += 1
            result = self._run(folder, root, sources, ["2020-01-02", "2020-11-27"], ["NDX"])
            import pyarrow.parquet as pq
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            early_1500 = [row for row in coverage if row["request_date"] == "2020-11-27"
                          and row["cut_label"] == "15:00"]
            self.assertTrue(early_1500)
            self.assertTrue(all(row["cut_status"] == "not_applicable" and row["early_close"]
                                and row["cut_applicable"] is False for row in early_1500))
            utc_cut = utc_cut_ns(winter, "15:00")
            local_1500 = cut_ns_on(winter, "15:00")
            self.assertNotEqual(utc_cut, local_1500)
            board = _read_parts(result["refs"]["cut_board"])
            winter_utc = [row for row in board if row["request_date"] == "2020-01-02"
                          and row["cut_label"] == "15:00_utc" and row["source_family"] == "near"]
            winter_local = [row for row in board if row["request_date"] == "2020-01-02"
                            and row["cut_label"] == "15:00" and row["source_family"] == "near"]
            self.assertTrue(winter_utc)
            self.assertTrue(winter_local)
            self.assertEqual(winter_utc[0]["cut_ns"], utc_cut)
            self.assertEqual(winter_local[0]["cut_ns"], local_1500)

    def test_date_only_cash_cannot_leak_future_close(self):
        import pyarrow as pa
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            quote = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            cash = "free-sources/yahoo__cash-daily__normalized/ndx.parquet"
            cash_table = pa.table({
                "date": pa.array([date(2020, 1, 2), date(2020, 1, 3)], type=pa.date32()),
                "symbol": pa.array(["NDX", "NDX"], type=pa.large_string()),
                "open": pa.array([100.0, 110.0]), "high": pa.array([101.0, 111.0]),
                "low": pa.array([99.0, 109.0]), "close": pa.array([100.5, 999.0]),
                "adjusted_close": pa.array([100.4, 998.0]), "volume": pa.array([1.0, 1.0]),
            })
            sources = [
                _admit(1, quote, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / quote, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)]))),
                _admit(2, cash, "NDX", "cash_daily", "2020-01-02",
                       "free-sources/yahoo__cash-daily__normalized",
                       "cash_daily", _write_parquet(root / cash, cash_table), role="underlier_daily"),
            ]
            schemas = {"quote_1m": QUOTE_SCHEMA, "cash_daily": CASH_SCHEMA}
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"], schemas=schemas)
            support = _read_parts(result["refs"]["underlier_support"])
            before_close = [row for row in support if row["cut_label"] in {"09:30", "10:00", "15:00"}]
            at_close = [row for row in support if row["cut_label"] == "cash_close"]
            self.assertTrue(before_close)
            self.assertTrue(all(row["cash_close"] != 999.0 for row in before_close))
            self.assertTrue(all(row["cash_same_date"] is False or row["cash_close"] is None
                                for row in before_close))
            self.assertTrue(at_close)
            self.assertTrue(all(row["cash_close"] == 100.5 and row["cash_same_date"]
                                and row["cash_adjusted_close"] == 100.4 for row in at_close))
            self.assertTrue(all(row["causal_feature_eligible"] is False for row in support))
            self.assertEqual(len({(row["chain"], row["cut_label"]) for row in support}), len(support))

    def test_two_oi_updates_around_morning_cut_and_ambiguous_latest(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            early = cut_ns_on(day, "06:30")
            late = cut_ns_on(day, "10:05")
            intervals = [
                {"contract_id": 1, "chain": "NDX", "open_interest": 40,
                 "ts_event_ns": early, "request_date": "2020-01-02", "file_id": 9,
                 "row_index": 0, "ambiguous": False, "valid_from_ns": early,
                 "valid_to_ns": late, "expiration": "2020-01-17",
                 "causal_feature_eligible": False},
                {"contract_id": 1, "chain": "NDX", "open_interest": 80,
                 "ts_event_ns": late, "request_date": "2020-01-02", "file_id": 9,
                 "row_index": 1, "ambiguous": False, "valid_from_ns": late,
                 "valid_to_ns": None, "expiration": "2020-01-17",
                 "causal_feature_eligible": False},
                {"contract_id": 2, "chain": "NDX", "open_interest": 5,
                 "ts_event_ns": early, "request_date": "2020-01-02", "file_id": 9,
                 "row_index": 2, "ambiguous": True, "valid_from_ns": early,
                 "valid_to_ns": None, "expiration": "2020-01-17",
                 "causal_feature_eligible": False},
            ]
            oi = self._oi_population(folder, intervals=intervals, first_oi=40)
            import pyarrow as pa
            import pyarrow.parquet as pq
            ident = pq.read_table(oi["refs"]["identity_map"][0]["path"])
            extra = pa.table({
                "contract_id": pa.array([2], type=pa.int32()),
                "chain": pa.array(["NDX"]), "osi_symbol": pa.array([NDX_PUT]),
                "expiration": pa.array(["2020-01-17"]),
                "millistrike": pa.array([3400000], type=pa.int64()),
                "right": pa.array(["PUT"]),
            }, schema=identity_schema())
            merged = pa.concat_tables([ident, extra])
            ident_path = Path(folder) / "oi-identity.parquet"
            pq.write_table(merged, ident_path)
            raw = ident_path.read_bytes()
            oi["refs"]["identity_map"] = [{
                "path": str(ident_path), "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw), "kind": "options_oi_identity_map_v2", "rows": 2,
            }]
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, _quotes([
                                  _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
                                  _q("NDX", exp, 3400.0, "PUT", 10, 10, 1, 1, 50, 50, 1.1, 1.3, day, ts, NDX_PUT),
                              ])))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"], oi=oi)
            board = [row for row in _read_parts(result["refs"]["cut_board"]) if row["source_family"] == "near"]
            morning = [row for row in board if row["osi_symbol"] == NDX_OSI and row["cut_label"] == "09:30"]
            later = [row for row in board if row["osi_symbol"] == NDX_OSI and row["cut_label"] == "10:00"]
            self.assertTrue(morning)
            self.assertEqual(morning[0]["oi"], 40)
            self.assertTrue(later)
            self.assertEqual(later[0]["oi"], 40)
            after = [row for row in board if row["osi_symbol"] == NDX_OSI and row["cut_label"] == "15:00"]
            self.assertTrue(after)
            self.assertEqual(after[0]["oi"], 80)
            amb = [row for row in board if row["osi_symbol"] == NDX_PUT and row["cut_label"] == "10:00"]
            self.assertTrue(amb)
            self.assertTrue(amb[0]["oi_ambiguous"])
            self.assertIsNone(amb[0]["oi"])

    def test_unlisted_quoted_listed_unquoted_and_zero_oi_weight_undefined(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            oi = self._oi_population(folder, listed=True, first_oi=0)
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, _quotes([
                                  _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
                                  _q("NDX", exp, 3600.0, "CALL", 10, 10, 1, 1, 50, 50, 0.5, 0.7, day, ts,
                                     "NDX   200117C03600000"),
                              ])))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"], oi=oi)
            self.assertTrue(result["joined_coverage_complete"])
            board = [row for row in _read_parts(result["refs"]["cut_board"])
                     if row["cut_label"] == "10:00" and row["source_family"] == "near"]
            listed_quoted = [row for row in board if row["osi_symbol"] == NDX_OSI]
            quoted_unlisted = [row for row in board if row["osi_symbol"] == "NDX   200117C03600000"]
            listed_unquoted = [row for row in board if row["listed"] is True and not row["quoted"]]
            self.assertTrue(listed_quoted)
            self.assertTrue(listed_quoted[0]["listed"])
            self.assertTrue(listed_quoted[0]["oi_zero"])
            self.assertTrue(quoted_unlisted)
            self.assertIs(quoted_unlisted[0]["listed"], False)
            self.assertGreaterEqual(quoted_unlisted[0]["contract_id"], LOCAL_ID_BASE)
            self.assertEqual(listed_unquoted, [])
            import pyarrow.parquet as pq
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            ten = [row for row in coverage if row["cut_label"] == "10:00" and row["source_family"] == "near"]
            self.assertTrue(ten)
            self.assertIsNone(ten[0]["oi_weighted_quoted_fraction"])
            self.assertEqual(ten[0]["oi_zero_count"], 1)

    def test_invalid_exceptions_remain_addressed_and_clock_null_roundtrip(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
                _q("NDX", exp, 3400.0, "X", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            exceptions = _read_parts(result["refs"]["exceptions"])
            self.assertTrue(exceptions)
            self.assertTrue(all(row["file_id"] is not None and row["row_index_start"] is not None
                                for row in exceptions))
            board = _read_parts(result["refs"]["cut_board"])
            quoted = [row for row in board if row["quoted"]]
            self.assertTrue(quoted)
            self.assertTrue(all(row["received_at_ns"] is None and row["published_at_ns"] is None
                                and row["known_at_ns"] is None and row["last_actual_update_ns"] is None
                                and row["actual_update_age_unknown"] and row["causal_feature_eligible"] is False
                                for row in quoted))
            import pyarrow.parquet as pq
            board_refs = result["refs"]["cut_board"]
            board_path = board_refs[0]["path"] if isinstance(board_refs, list) else board_refs["path"]
            restored = pq.read_table(board_path)
            self.assertTrue(restored.column("received_at_ns").null_count == len(restored)
                            or all(value is None for value in restored.column("received_at_ns").to_pylist()))
            md = Path(result["refs"]["results_md"]["path"]).read_text()
            self.assertIn("causal_feature_eligible is FALSE", md)
            self.assertIn("not complete", md.lower())
            self.assertIn("raw quotation rows", md)
            self.assertIn("Full metric tables", md)
            reconstruction = json.loads(Path(result["refs"]["reconstruction"]["path"]).read_text())
            self.assertIn("ts_event_ns", reconstruction["predicate"])
            self.assertEqual(reconstruction["clocks"]["causal_feature_eligible"], False)
            self.assertIn("sort_id", reconstruction["sort"])
            self.assertEqual(reconstruction["local_id_namespace"]["unresolved"], 0)
            self.assertGreaterEqual(reconstruction["local_id_namespace"]["base"], LOCAL_ID_BASE)

    def test_unequal_quote_counts_give_independent_date_and_raw_means(self):
        day_a, day_b = date(2020, 1, 2), date(2020, 1, 3)
        exp = date(2020, 1, 17)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel_a = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            rel_b = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-03.parquet"
            ts_a = local_timestamp(day_a, time(10, 0), ZONE)
            ts_b = local_timestamp(day_b, time(10, 0), ZONE)
            sources = [
                _admit(1, rel_a, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / rel_a, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 10.0, 10.2, day_a, ts_a, NDX_OSI)]))),
                _admit(2, rel_b, "NDX", "near", "2020-01-03",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / rel_b, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day_b, ts_b, NDX_OSI),
                           _q("NDX", exp, 3410.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day_b, ts_b,
                              "NDX   200117C03410000"),
                           _q("NDX", exp, 3420.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day_b, ts_b,
                              "NDX   200117C03420000"),
                       ]))),
            ]
            result = self._run(folder, root, sources, ["2020-01-02", "2020-01-03"], ["NDX"])
            aggregates = json.loads(Path(result["refs"]["date_aggregates"]["path"]).read_text())
            by_day = {row["request_date"]: row for row in aggregates if row["chain"] == "NDX"}
            self.assertIn("2020-01-02", by_day)
            self.assertIn("2020-01-03", by_day)
            daily = {"2020-01-02": by_day["2020-01-02"]["mean_bid"],
                     "2020-01-03": by_day["2020-01-03"]["mean_bid"]}
            date_mean = date_balanced_point(daily)
            event_mean = raw_mean(
                (by_day["2020-01-02"]["raw_bid_sum"] or 0) + (by_day["2020-01-03"]["raw_bid_sum"] or 0),
                (by_day["2020-01-02"]["raw_bid_n"] or 0) + (by_day["2020-01-03"]["raw_bid_n"] or 0),
            )
            self.assertNotEqual(date_mean, event_mean)
            groups = result["groups"]
            ndx = groups["NDX|all_period|all|all|all|all"]["statistics"]["metrics"]["mean_bid"]
            self.assertEqual(ndx.get("raw_mean"), event_mean)
            self.assertAlmostEqual(ndx.get("estimate"), date_mean)
            self.assertIn("raw_quantiles", ndx)
            self.assertIn("date_quantiles", ndx)
            self.assertNotEqual(ndx["raw_quantiles"].get("0.5"), ndx["date_quantiles"].get("0.5"))
            half = groups["NDX|all_period|all|all|all|all"]["statistics"]["metrics"]["known_half_fraction"]
            unit = groups["NDX|all_period|all|all|all|all"]["statistics"]["metrics"]["known_unit_fraction"]
            self.assertEqual(half.get("estimate"), 0.5)
            self.assertEqual(unit.get("estimate"), 1.0)

    def test_mutated_source_hash_fails_before_decode(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            path = root / rel
            meta = _write_parquet(path, _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)]))
            path.write_bytes(path.read_bytes() + b"\x00")
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", meta)]
            with self.assertRaises(IntegrityError):
                self._run(folder, root, sources, ["2020-01-02"], ["NDX"])

    def test_combine_two_chains_matches_fresh_and_rejects_duplicate_ownership(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            ndx = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            qqq = "thetadata-opra/opra__qqq-options__quote-1m__dte14/2020-01-02.parquet"
            ndx_src = [_admit(1, ndx, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / ndx, _quotes([
                                  _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)])))]
            qqq_src = [_admit(2, qqq, "QQQ", "near", "2020-01-02",
                              "thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42",
                              "quote_1m", _write_parquet(root / qqq, _quotes([
                                  _q("QQQ", exp, 200.0, "CALL", 8, 8, 1, 1, 50, 50, 0.4, 0.5, day, ts, QQQ_OSI)])))]
            admitted_both = self._admitted(ndx_src + qqq_src)
            r_ndx = run(protocol=self._protocol(root), admitted=admitted_both,
                        oi_population=None, store=self._store(folder, "cas-ndx"),
                        outputs=self._outputs(folder, "out-ndx"),
                        selected_dates=["2020-01-02"], selected_chains=["NDX"])
            r_qqq = run(protocol=self._protocol(root), admitted=admitted_both,
                        oi_population=None, store=self._store(folder, "cas-qqq"),
                        outputs=self._outputs(folder, "out-qqq"),
                        selected_dates=["2020-01-02"], selected_chains=["QQQ"])
            fresh = run(protocol=self._protocol(root), admitted=admitted_both,
                        oi_population=None, store=self._store(folder, "cas-both"),
                        outputs=self._outputs(folder, "out-both"),
                        selected_dates=["2020-01-02"], selected_chains=["NDX", "QQQ"])
            combined = combine_partition_results(
                protocol=self._protocol(root), results=[r_ndx, r_qqq],
                outputs=self._outputs(folder, "out-combine"), load_reference=None,
            )
            self.assertEqual(combined["protocol_scientific_hash"], fresh["protocol_scientific_hash"])
            self.assertEqual(combined["implementation_hashes"], implementation_hashes())
            self.assertEqual(set(combined["selected_chains"]), {"NDX", "QQQ"})
            self.assertEqual(combined["counts"]["source_rows_read"], fresh["counts"]["source_rows_read"])
            self.assertEqual(combined["counts"]["source_files_read"], fresh["counts"]["source_files_read"])
            self.assertIn("NDX|all_period|all|all|all|all", combined["groups"])
            self.assertIn("QQQ|all_period|all|all|all|all", combined["groups"])
            self.assertEqual(
                combined["groups"]["NDX|all_period|all|all|all|all"]["statistics"]["metrics"]["raw_row_count"]["estimate"],
                fresh["groups"]["NDX|all_period|all|all|all|all"]["statistics"]["metrics"]["raw_row_count"]["estimate"],
            )
            self.assertIsNotNone(combined["refs"].get("cut_board"))
            self.assertIsNotNone(combined["refs"].get("source_manifest"))
            with self.assertRaises(IntegrityError):
                combine_partition_results(
                    protocol=self._protocol(root), results=[r_ndx, r_ndx],
                    outputs=self._outputs(folder, "out-dup"), load_reference=None,
                )
            mixed = dict(r_qqq)
            mixed["protocol_scientific_hash"] = "0" * 64
            with self.assertRaises(IntegrityError):
                combine_partition_results(
                    protocol=self._protocol(root), results=[r_ndx, mixed],
                    outputs=self._outputs(folder, "out-mixed"), load_reference=None,
                )
            failed = dict(r_qqq)
            failed["passed"] = False
            with self.assertRaises(IntegrityError):
                combine_partition_results(
                    protocol=self._protocol(root), results=[r_ndx, failed],
                    outputs=self._outputs(folder, "out-failed"), load_reference=None,
                )

    def test_null_oi_population_cannot_pass_joined_coverage(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, _quotes([
                                  _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)])))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"], oi=None)
            self.assertIs(result["joined_coverage_complete"], False)
            import pyarrow.parquet as pq
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            self.assertTrue(all(row["listing_unavailable"] and row["oi_unavailable"] for row in coverage))
            self.assertEqual(result["family"], FAMILY)
            self.assertEqual(result["version"], VERSION)
            reconstruction = json.loads(Path(result["refs"]["reconstruction"]["path"]).read_text())
            self.assertIn("ts_event_ns", reconstruction["predicate"])
            self.assertIn("file_id", reconstruction["predicate"])
            self.assertEqual(reconstruction["clocks"]["actual_update_age_unknown"], True)
            self.assertEqual(len(ALL_CUTS), 5)
            self.assertEqual(len(BASE_CLASSES), 9)
            self.assertEqual(scientific_hash(self._protocol(root)), result["protocol_scientific_hash"])
            self.assertEqual(result["resources"]["fixture_cpu_seconds"], 0.0)
            self.assertIn("source_parse_dedup_board_cpu_seconds", result["resources"])
            self.assertIn("oi_support_load_cpu_seconds", result["resources"])
            self.assertIn("statistics_cpu_seconds", result["resources"])

    def test_etf_int32_bar_start_does_not_leak_current_minute(self):
        import pyarrow as pa
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        cut = cut_ns_on(day, "10:00")
        t_eligible = (cut - 60_000_000_000) // 1_000_000
        t_current = cut // 1_000_000
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            quote = "thetadata-opra/opra__qqq-options__quote-1m__dte14/2020-01-02.parquet"
            etf = "quantpad/nasdaq__qqq-etf__ohlcv-1m/2020-01-02.parquet"
            etf_table = pa.table({
                "t": pa.array([t_eligible, t_current], type=pa.int64()),
                "o": pa.array([10.0, 99.0]), "h": pa.array([11.0, 99.0]),
                "l": pa.array([9.0, 99.0]), "c": pa.array([10.5, 99.0]),
                "v": pa.array([100.0, 1.0]),
                "instrument_id": pa.array([6424, 6424], type=pa.int32()),
            })
            sources = [
                _admit(1, quote, "QQQ", "near", "2020-01-02",
                       "thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42",
                       "quote_1m", _write_parquet(root / quote, _quotes([
                           _q("QQQ", exp, 200.0, "CALL", 8, 8, 1, 1, 50, 50, 0.4, 0.5, day, ts, QQQ_OSI)]))),
                _admit(2, etf, None, "etf_1m", None,
                       "quantpad/nasdaq__qqq-etf__ohlcv-1m",
                       "etf_1m", _write_parquet(root / etf, etf_table), role="qqq_minute"),
            ]
            schemas = {"quote_1m": QUOTE_SCHEMA, "etf_1m": ETF_SCHEMA}
            result = self._run(folder, root, sources, ["2020-01-02"], ["QQQ"], schemas=schemas)
            support = [row for row in _read_parts(result["refs"]["underlier_support"])
                       if row["cut_label"] == "10:00"]
            self.assertTrue(support)
            self.assertEqual(support[0]["etf_instrument_id"], 6424)
            self.assertEqual(support[0]["etf_close"], 10.5)
            self.assertNotEqual(support[0]["etf_close"], 99.0)
            self.assertEqual(support[0]["etf_bar_end_ns"], t_eligible * 1_000_000 + 60_000_000_000)
            self.assertLessEqual(support[0]["etf_bar_end_ns"], cut)
            self.assertEqual(result["counts"]["support_files_read"], 1)

    def test_fred_all_tenors_null_and_latest_independent_dates(self):
        import pyarrow as pa
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            quote = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            fred = "free-sources/fred__usd-rates/fred.parquet"
            fred_table = pa.table({
                "date": pa.array([date(2020, 1, 2), date(2020, 1, 1), date(2019, 12, 31)], type=pa.date32()),
                "series_id": pa.array(["DFF", "DGS1", "DGS10"], type=pa.large_string()),
                "tenor_days": pa.array([1, 365, 3650], type=pa.int64()),
                "rate_pct": pa.array([1.55, 1.60, None], type=pa.float64()),
                "realtime_start": pa.array([date(2020, 1, 2), date(2020, 1, 1), date(2019, 12, 31)], type=pa.date32()),
                "realtime_end": pa.array([date(2020, 1, 2), date(2020, 1, 1), date(2019, 12, 31)], type=pa.date32()),
            })
            action = "free-sources/corporate-actions/ndx.parquet"
            action_table = pa.table({
                "ex_date": pa.array([date(2020, 1, 2), date(2019, 12, 15)], type=pa.date32()),
                "dividend": pa.array([0.4, None], type=pa.float64()),
                "split_ratio": pa.array([None, 2.0], type=pa.float64()),
                "symbol": pa.array(["NDX", "NDX"], type=pa.large_string()),
            })
            sources = [
                _admit(1, quote, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / quote, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)]))),
                _admit(2, fred, None, "fred", None, "free-sources/fred__usd-rates",
                       "fred", _write_parquet(root / fred, fred_table), role="rates"),
                _admit(3, action, "NDX", "corporate_actions", None,
                       "free-sources/corporate-actions",
                       "actions", _write_parquet(root / action, action_table), role="corporate_actions"),
            ]
            schemas = {"quote_1m": QUOTE_SCHEMA, "fred": FRED_SCHEMA, "actions": ACTION_SCHEMA}
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"], schemas=schemas)
            fred_rows = [row for row in _read_parts(result["refs"]["fred_support"])
                         if row["cut_label"] == "10:00"]
            series = {row["series_id"]: row for row in fred_rows}
            self.assertEqual(set(series), {"DFF", "DGS1", "DGS10"})
            self.assertEqual(series["DFF"]["obs_date"], "2020-01-02")
            self.assertEqual(series["DGS1"]["obs_date"], "2020-01-01")
            self.assertEqual(series["DGS10"]["obs_date"], "2019-12-31")
            self.assertTrue(series["DGS10"]["missing_rate"])
            self.assertIsNone(series["DGS10"]["rate_pct"])
            actions = [row for row in _read_parts(result["refs"]["action_support"])
                       if row["cut_label"] == "10:00"]
            self.assertEqual(len(actions), 2)
            self.assertTrue(all(row["announcement_known_at_ns"] is None for row in actions))

    def test_oi_coverage_missing_listing_is_not_zero(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            oi = self._oi_population(
                folder, listed=True, first_oi=0,
                listing_file_present=False, listing_status="missing",
                listing_denominator_known=False,
            )
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, _quotes([
                                  _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)])))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"], oi=oi)
            import pyarrow.parquet as pq
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            ten = [row for row in coverage if row["cut_label"] == "10:00" and row["source_family"] == "near"]
            self.assertTrue(ten)
            self.assertFalse(ten[0]["listing_known"])
            self.assertIsNone(ten[0]["listed_count"])
            self.assertEqual(ten[0]["listing_status"], "missing")
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            self.assertTrue(all(row["listed"] is None for row in board))

    def test_mutated_support_hash_fails_before_decode(self):
        import pyarrow as pa
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            quote = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            cash = "free-sources/yahoo__cash-daily__normalized/ndx.parquet"
            cash_table = pa.table({
                "date": pa.array([date(2020, 1, 2)], type=pa.date32()),
                "symbol": pa.array(["NDX"], type=pa.large_string()),
                "open": pa.array([100.0]), "high": pa.array([101.0]),
                "low": pa.array([99.0]), "close": pa.array([100.5]),
                "adjusted_close": pa.array([100.4]), "volume": pa.array([1.0]),
            })
            path = root / cash
            meta = _write_parquet(path, cash_table)
            path.write_bytes(path.read_bytes() + b"\x00")
            sources = [
                _admit(1, quote, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / quote, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)]))),
                _admit(2, cash, "NDX", "cash_daily", "2020-01-02",
                       "free-sources/yahoo__cash-daily__normalized",
                       "cash_daily", meta, role="underlier_daily"),
            ]
            schemas = {"quote_1m": QUOTE_SCHEMA, "cash_daily": CASH_SCHEMA}
            with self.assertRaises(IntegrityError):
                self._run(folder, root, sources, ["2020-01-02"], ["NDX"], schemas=schemas)

    def test_same_family_alias_then_later_contract_keeps_own_run_start(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        t0 = local_timestamp(day, time(9, 31), ZONE)
        t1 = local_timestamp(day, time(9, 40), ZONE)
        osi_b = "NDX   200117C03410000"
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, t0, NDX_OSI),
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, t0, NDX_OSI),
                _q("NDX", exp, 3410.0, "CALL", 10, 10, 1, 1, 50, 50, 2.0, 2.2, day, t1, osi_b),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            by_osi = {row["osi_symbol"]: row for row in board}
            self.assertEqual(by_osi[NDX_OSI]["alias_multiplicity"], 2)
            self.assertEqual(by_osi[NDX_OSI]["run_lower_bound_ns"], t0)
            self.assertEqual(by_osi[osi_b]["run_lower_bound_ns"], t1)
            self.assertEqual(by_osi[osi_b]["run_start_row_index"], 2)
            self.assertFalse(by_osi[osi_b]["run_continuity_observed"])

    def test_within_family_conflict_stays_conflict_when_cross_family_matches(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            near = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            broad = "thetadata-opra/opra__ndx-options__quote-1m__dte60/2020-01-02.parquet"
            a = _q("NDX", exp, 3400.0, "CALL", 10, 10, 5, 5, 50, 50, 1.25, 1.35, day, ts, NDX_OSI)
            b = _q("NDX", exp, 3400.0, "CALL", 10, 10, 5, 5, 50, 50, 9.00, 9.10, day, ts, NDX_OSI)
            sources = [
                _admit(1, near, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / near, _quotes([a, b]))),
                _admit(2, broad, "NDX", "broad", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte60__atm10",
                       "quote_1m", _write_parquet(root / broad, _quotes([a]))),
            ]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            union = [row for row in _read_parts(result["refs"]["cut_board"])
                     if row["source_family"] == "union" and row["cut_label"] == "10:00" and row["quoted"]]
            self.assertEqual(len(union), 1)
            self.assertTrue(union[0]["conflict"])
            self.assertIsNone(union[0]["bid"])

    def test_null_versus_zero_payload_is_conflict(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            near = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            broad = "thetadata-opra/opra__ndx-options__quote-1m__dte60/2020-01-02.parquet"
            a = _q("NDX", exp, 3400.0, "CALL", None, 10, 5, 5, 50, 50, 1.25, 1.35, day, ts, NDX_OSI)
            b = _q("NDX", exp, 3400.0, "CALL", 0, 10, 5, 5, 50, 50, 1.25, 1.35, day, ts, NDX_OSI)
            sources = [
                _admit(1, near, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / near, _quotes([a]))),
                _admit(2, broad, "NDX", "broad", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte60__atm10",
                       "quote_1m", _write_parquet(root / broad, _quotes([b]))),
            ]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            union = [row for row in _read_parts(result["refs"]["cut_board"])
                     if row["source_family"] == "union" and row["cut_label"] == "10:00" and row["quoted"]]
            self.assertEqual(len(union), 1)
            self.assertTrue(union[0]["conflict"])
            self.assertTrue(union[0]["bid_size_null"] or union[0]["alias_multiplicity"] == 2)
            self.assertIsNone(union[0]["mid"])

    def test_future_original_request_date_is_not_substituted(self):
        day = date(2020, 1, 2)
        future = date(2020, 1, 3)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, future, ts, NDX_OSI),
                _q("NDX", exp, 3410.0, "CALL", 10, 10, 1, 1, 50, 50, 2.0, 2.2, day, ts,
                   "NDX   200117C03410000"),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            self.assertTrue(all(row["osi_symbol"] != NDX_OSI for row in board))
            self.assertTrue(any(row["osi_symbol"] == "NDX   200117C03410000" for row in board))
            quality = _read_parts(result["refs"]["source_quality"])
            self.assertEqual(sum(row["raw_rows"] for row in quality), 2)
            self.assertTrue(any(row["raw_request_date_mismatch"] >= 1 for row in quality))

    def test_unknown_right_group_reconciles_to_all_input_rows(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = _quotes([
                _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
                _q("NDX", exp, 3400.0, "PUT", 10, 10, 1, 1, 50, 50, 1.1, 1.3, day, ts, NDX_PUT),
                _q("NDX", exp, 3400.0, "X", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI),
            ])
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            quality = _read_parts(result["refs"]["source_quality"])
            self.assertEqual(sum(row["raw_rows"] for row in quality), 3)
            self.assertTrue(any(row["right"] == "unknown" for row in quality))

    def test_multiplicity_greater_than_two_is_summed(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            row = _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, _quotes([row, row, row])))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            aliases = [row for row in _read_parts(result["refs"]["alias_conflict"])
                       if row["source_family"] == "near"]
            self.assertTrue(any(row["max_multiplicity"] == 3 and row["alias_row_mass"] == 3
                                for row in aliases))
            board = _near_quoted(_read_parts(result["refs"]["cut_board"]))
            self.assertEqual(board[0]["alias_multiplicity"], 3)

    def test_same_cut_different_sample_timestamps_are_not_paired(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts_a = local_timestamp(day, time(9, 50), ZONE)
        ts_b = local_timestamp(day, time(9, 55), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            near = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            broad = "thetadata-opra/opra__ndx-options__quote-1m__dte60/2020-01-02.parquet"
            sources = [
                _admit(1, near, "NDX", "near", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                       "quote_1m", _write_parquet(root / near, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 5, 5, 50, 50, 1.25, 1.35, day, ts_a, NDX_OSI)]))),
                _admit(2, broad, "NDX", "broad", "2020-01-02",
                       "thetadata-opra/opra__ndx-options__quote-1m__dte60__atm10",
                       "quote_1m", _write_parquet(root / broad, _quotes([
                           _q("NDX", exp, 3400.0, "CALL", 10, 10, 5, 5, 50, 50, 1.25, 1.35, day, ts_b, NDX_OSI)]))),
            ]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            aggregates = json.loads(Path(result["refs"]["date_aggregates"]["path"]).read_text())
            paired = aggregates[0]["paired_near_broad"]
            self.assertEqual(paired["common"], 0)
            self.assertGreaterEqual(paired["unmatched_sample_clocks"], 1)

    def test_all_fraction_metrics_stay_in_unit_interval(self):
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, _quotes([
                                  _q("NDX", exp, 3400.0, "CALL", 10, 10, 1, 1, 50, 50, 1.0, 1.2, day, ts, NDX_OSI)])))]
            result = self._run(folder, root, sources, ["2020-01-02"], ["NDX"])
            for name, block in result["groups"].items():
                metrics = block["statistics"]["metrics"]
                for metric, payload in metrics.items():
                    if not metric.endswith("_fraction"):
                        continue
                    value = payload.get("estimate")
                    if value is None:
                        continue
                    self.assertGreaterEqual(value, 0.0, msg=f"{name}:{metric}")
                    self.assertLessEqual(value, 1.0, msg=f"{name}:{metric}")
            self.assertIn("usable_fraction", PRESPECIFIED)
            self.assertIn("sample_stale_60_fraction", PRESPECIFIED)
            self.assertIn("payload_stale_900_fraction", PRESPECIFIED)

    def test_inexact_floating_integer_payload_is_rejected(self):
        import pyarrow as pa
        day = date(2020, 1, 2)
        exp = date(2020, 1, 17)
        ts = local_timestamp(day, time(10, 0), ZONE)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            table = pa.table({
                "symbol": pa.array(["NDX"], type=pa.large_string()),
                "expiration": pa.array([exp], type=pa.date32()),
                "strike": pa.array([3400.0]),
                "right": pa.array(["CALL"], type=pa.large_string()),
                "bid_size": pa.array([10.0], type=pa.float64()),
                "ask_size": pa.array([10], type=pa.int64()),
                "bid_exchange": pa.array([1], type=pa.int64()),
                "ask_exchange": pa.array([1], type=pa.int64()),
                "bid_condition": pa.array([50], type=pa.int64()),
                "ask_condition": pa.array([50], type=pa.int64()),
                "bid": pa.array([1.0]), "ask": pa.array([1.2]),
                "request_date": pa.array([day], type=pa.date32()),
                "ts_event": pa.array([ts], type=pa.timestamp("ns", tz="UTC")),
                "osi_symbol": pa.array([NDX_OSI], type=pa.large_string()),
            })
            sources = [_admit(1, rel, "NDX", "near", "2020-01-02",
                              "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                              "quote_1m", _write_parquet(root / rel, table))]
            with self.assertRaises(IntegrityError):
                self._run(folder, root, sources, ["2020-01-02"], ["NDX"])

    def test_combine_disjoint_dates_same_chain_and_rejects_corrupt_artifacts(self):
        day_a, day_b = date(2020, 1, 2), date(2020, 1, 3)
        exp = date(2020, 1, 17)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            rel_a = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-02.parquet"
            rel_b = "thetadata-opra/opra__ndx-options__quote-1m__dte14/2020-01-03.parquet"
            ts_a = local_timestamp(day_a, time(10, 0), ZONE)
            ts_b = local_timestamp(day_b, time(10, 0), ZONE)
            src_a = [_admit(1, rel_a, "NDX", "near", "2020-01-02",
                            "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                            "quote_1m", _write_parquet(root / rel_a, _quotes([
                                _q("NDX", exp, 3600.0, "CALL", 10, 10, 1, 1, 50, 50, 4.0, 4.2, day_a, ts_a,
                                   "NDX   200117C03600000")])))]
            src_b = [_admit(2, rel_b, "NDX", "near", "2020-01-03",
                            "thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70",
                            "quote_1m", _write_parquet(root / rel_b, _quotes([
                                _q("NDX", exp, 3600.0, "CALL", 10, 10, 1, 1, 50, 50, 5.0, 5.2, day_b, ts_b,
                                   "NDX   200117C03600000")])))]
            admitted_both = self._admitted(src_a + src_b)
            r_a = run(protocol=self._protocol(root), admitted=admitted_both,
                      oi_population=None, store=self._store(folder, "cas-a"),
                      outputs=self._outputs(folder, "out-a"),
                      selected_dates=["2020-01-02"], selected_chains=["NDX"])
            r_b = run(protocol=self._protocol(root), admitted=admitted_both,
                      oi_population=None, store=self._store(folder, "cas-b"),
                      outputs=self._outputs(folder, "out-b"),
                      selected_dates=["2020-01-03"], selected_chains=["NDX"])
            fresh = run(protocol=self._protocol(root), admitted=admitted_both,
                        oi_population=None, store=self._store(folder, "cas-fresh"),
                        outputs=self._outputs(folder, "out-fresh"),
                        selected_dates=["2020-01-02", "2020-01-03"], selected_chains=["NDX"])
            combined = combine_partition_results(
                protocol=self._protocol(root), results=[r_a, r_b],
                outputs=self._outputs(folder, "out-year"), load_reference=None,
            )
            self.assertEqual(combined["counts"]["source_rows_read"], fresh["counts"]["source_rows_read"])
            self.assertEqual(
                combined["groups"]["NDX|all_period|all|all|all|all"]["statistics"]["metrics"]["raw_row_count"]["estimate"],
                fresh["groups"]["NDX|all_period|all|all|all|all"]["statistics"]["metrics"]["raw_row_count"]["estimate"],
            )
            ids_a = {row["contract_id"] for row in _near_quoted(_read_parts(r_a["refs"]["cut_board"]))}
            ids_b = {row["contract_id"] for row in _near_quoted(_read_parts(r_b["refs"]["cut_board"]))}
            self.assertEqual(ids_a, ids_b)
            self.assertTrue(all(cid >= LOCAL_ID_BASE for cid in ids_a))
            corrupt = dict(r_b)
            cov = dict(r_b["refs"]["coverage"])
            cov["sha256"] = "0" * 64
            corrupt["refs"] = dict(r_b["refs"])
            corrupt["refs"]["coverage"] = cov
            with self.assertRaises(IntegrityError):
                combine_partition_results(
                    protocol=self._protocol(root), results=[r_a, corrupt],
                    outputs=self._outputs(folder, "out-corrupt-cov"), load_reference=None,
                )
            board_bad = dict(r_b)
            board_ref = r_b["refs"]["cut_board"]
            board_item = dict(board_ref[0] if isinstance(board_ref, list) else board_ref)
            board_item["sha256"] = "1" * 64
            board_bad["refs"] = dict(r_b["refs"])
            board_bad["refs"]["cut_board"] = [board_item] if isinstance(board_ref, list) else board_item
            with self.assertRaises(IntegrityError):
                combine_partition_results(
                    protocol=self._protocol(root), results=[r_a, board_bad],
                    outputs=self._outputs(folder, "out-corrupt-board"), load_reference=None,
                )
            man_bad = dict(r_b)
            man = dict(r_b["refs"]["source_manifest"])
            man["sha256"] = "2" * 64
            man_bad["refs"] = dict(r_b["refs"])
            man_bad["refs"]["source_manifest"] = man
            with self.assertRaises(IntegrityError):
                combine_partition_results(
                    protocol=self._protocol(root), results=[r_a, man_bad],
                    outputs=self._outputs(folder, "out-corrupt-manifest"), load_reference=None,
                )
            missing = dict(r_a)
            missing["selected_dates"] = ["2020-01-02", "2020-01-03"]
            with self.assertRaises(IntegrityError):
                combine_partition_results(
                    protocol=self._protocol(root), results=[missing],
                    outputs=self._outputs(folder, "out-missing-date"), load_reference=None,
                )


if __name__ == "__main__":
    unittest.main()
