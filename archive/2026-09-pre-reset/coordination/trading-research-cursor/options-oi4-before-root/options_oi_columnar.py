"""Typed columnar Options OI production path.

Valid rows stay Arrow/NumPy arrays. Reports, lifecycle and intervals are written
from column builders. Compact lifecycle stores report_id links; a public iterator
reconstructs the accepted logical rows for Root parity. Literal helpers stay in
options_oi_measurements.py.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, time, timedelta
from pathlib import Path
import time as pytime

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.options_oi_statistics import finish_measurement_outputs
from trading_research.research.options_oi_measurements import (
    CHAINS_WITHOUT_LISTING, CONTRACT_FIELDS, FAMILY, INTERVAL_RECONSTRUCTION,
    MAX_SOURCE_FILE, MAX_WORKER_BYTES, OI_FIELDS, OUTPUT_SCHEMAS, REMAINING,
    STREAM_ROWS, VERSION, ZONE, _check_schema, _empty_date, _policy_acc,
    _safe_iso_dates, _validate_admitted, asof_aggregate_schema,
    build_calendar_index, contract, coverage_schema, cut_ns_on, dte_bucket,
    dte_days, eastern_date_from_ns, exception_schema, identity_schema,
    intended_cash_dates, interval_schema, lifecycle_schema, load_calendar,
    membership_schema, millistrike, normalize_right, parse_osi,
    read_admitted_source, report_schema, seconds_after_eastern_midnight,
    stage_of, timestamp_ns_from_arrow,
)


COMPACT_REPORT_KIND = "options_oi_resolved_reports_v3"
COMPACT_LIFECYCLE_KIND = "options_oi_lifecycle_v3"
LOGICAL_REPORT_KIND = OUTPUT_SCHEMAS["reports"]
LOGICAL_LIFECYCLE_KIND = OUTPUT_SCHEMAS["lifecycle"]
_EPOCH = date(1970, 1, 1)
_MAX_NS = 9223372036854775807
_REASON_NAMES = (
    None,
    "invalid_expiration",
    "invalid_request_date",
    "missing_identity_fields",
    "inexact_or_nonfinite_strike",
    "unparseable_osi",
    "osi_root_or_symbol_chain_mismatch",
    "strike_or_osi_identity_conflict",
    "wrong_request_date",
    "missing_open_interest",
    "non_integer_open_interest",
    "negative_open_interest",
    "missing_clock",
)


def _pa():
    import pyarrow as pa
    return pa


def _pc():
    import pyarrow.compute as pc
    return pc


def _np():
    import numpy as np
    return np


def _iso_to_days(label):
    return (date.fromisoformat(label) - _EPOCH).days


def _days_to_iso(days):
    return (_EPOCH + timedelta(days=int(days))).isoformat()


def compact_report_schema():
    pa = _pa()
    fields = [("report_id", pa.int64())]
    fields.extend((field.name, field.type) for field in report_schema())
    fields.append(("last_eq_first", pa.bool_()))
    return pa.schema(fields)


def compact_lifecycle_schema():
    pa = _pa()
    return pa.schema([
        ("contract_id", pa.int32()), ("chain", pa.string()),
        ("prior_date", pa.string()), ("next_date", pa.string()),
        ("prior_report_id", pa.int64()), ("next_report_id", pa.int64()),
        ("first_delta", pa.int64()), ("first_abs_delta", pa.int64()),
        ("first_censor", pa.string()), ("first_usable", pa.bool_()),
        ("first_within_stage", pa.bool_()), ("first_within_year", pa.bool_()),
        ("last_delta", pa.int64()), ("last_abs_delta", pa.int64()),
        ("last_censor", pa.string()), ("last_usable", pa.bool_()),
        ("last_within_stage", pa.bool_()), ("last_within_year", pa.bool_()),
        ("appearance", pa.string()), ("listed_on_prior", pa.bool_()),
        ("certified_listing_birth", pa.bool_()),
        ("intraday_terminal_holdings_identified", pa.bool_()),
        ("cross_gap_compressed", pa.bool_()), ("is_boundary", pa.bool_()),
        ("prior_stage", pa.string()), ("next_stage", pa.string()),
        ("causal_feature_eligible", pa.bool_()),
    ])


def _with_storage_meta(schema, logical_kind, physical_kind):
    return schema.with_metadata({
        b"options_oi_storage": b"compact_v3",
        b"options_oi_logical_kind": logical_kind.encode(),
        b"options_oi_physical_kind": physical_kind.encode(),
        b"options_oi_report_prefix": b"reports",
    })


class ArrayWriter:
    """Parquet parts from Arrow tables. No per-row dict.get conversion."""

    def __init__(self, outputs, prefix, schema, kind, batch_rows=STREAM_ROWS):
        self.outputs, self.prefix, self.schema, self.kind = outputs, prefix, schema, kind
        self.batch_rows = batch_rows
        self.chunks, self.chunk_rows, self.refs, self.rows, self.part = [], 0, [], 0, 0

    def write_table(self, table):
        if table is None or len(table) == 0:
            return
        self.chunks.append(table)
        self.chunk_rows += len(table)
        if self.chunk_rows >= self.batch_rows:
            self._flush()

    def write_arrays(self, mapping, schema=None):
        schema = schema or self.schema
        if mapping is None:
            return
        n = None
        for value in mapping.values():
            n = len(value)
            break
        if not n:
            return
        self.write_table(_pa().table(mapping, schema=schema))

    def _flush(self):
        pa = _pa()
        import pyarrow.parquet as pq
        if not self.chunks and self.refs:
            return
        if not self.chunks:
            table = self.schema.empty_table()
        elif len(self.chunks) == 1:
            table = self.chunks[0]
        else:
            table = pa.concat_tables(self.chunks)
        name = f"{self.prefix}-{self.part:04d}.parquet"
        stream = self.outputs.create(name)
        try:
            pq.write_table(table, stream, compression="zstd")
        finally:
            stream.close()
        ref = self.outputs.reference(name, kind=self.kind)
        self.refs.append({**ref, "rows": len(table)})
        self.rows += len(table)
        self.part += 1
        self.chunks, self.chunk_rows = [], 0

    def finish(self):
        if self.chunks or not self.refs:
            self._flush()
        return self.refs


def _as_ref_list(refs):
    if refs is None:
        return []
    if isinstance(refs, dict) and "path" in refs:
        return [refs]
    return list(refs)


def _discover_report_refs(life_refs):
    refs = _as_ref_list(life_refs)
    if not refs:
        return []
    folder = Path(refs[0]["path"]).parent
    return [{"path": str(path), "kind": COMPACT_REPORT_KIND} for path in sorted(folder.glob("reports-*.parquet"))]


def _is_compact_report(table):
    names = set(table.schema.names)
    return "last_eq_first" in names or "report_id" in names and "first_oi" in names


def _is_compact_lifecycle(table):
    names = set(table.schema.names)
    return "prior_report_id" in names and "first_prior_oi" not in names


def _logical_report_row(row):
    if row.get("last_eq_first"):
        row = dict(row)
        row["last_oi"] = row.get("first_oi")
        row["last_ts_event_ns"] = row.get("first_ts_event_ns")
        row["last_file_id"] = row.get("first_file_id")
        row["last_row_index"] = row.get("first_row_index")
    return row


def iter_logical_reports(refs):
    """Bounded iterator of accepted logical report rows (pilot-2 field set)."""
    import pyarrow.parquet as pq
    for ref in _as_ref_list(refs):
        table = pq.read_table(ref["path"])
        for row in table.to_pylist():
            yield _logical_report_row(row) if _is_compact_report(table) else row


def _report_index(report_refs):
    index = {}
    for row in iter_logical_reports(report_refs):
        rid = row.get("report_id")
        if rid is not None:
            index[int(rid)] = row
    return index


def _side_from_report(report, policy, key):
    if report is None:
        return None
    return report.get(f"{policy}_{key}")


def _expand_lifecycle_row(row, reports):
    prior = reports.get(row["prior_report_id"]) if row.get("prior_report_id") is not None else None
    nxt = reports.get(row["next_report_id"]) if row.get("next_report_id") is not None else None
    first_delta, last_delta = row.get("first_delta"), row.get("last_delta")
    return {
        "contract_id": row["contract_id"], "chain": row["chain"],
        "prior_date": row.get("prior_date"), "next_date": row.get("next_date"),
        "first_prior_oi": _side_from_report(prior, "first", "oi"),
        "first_next_oi": _side_from_report(nxt, "first", "oi"),
        "first_prior_ts_event_ns": _side_from_report(prior, "first", "ts_event_ns"),
        "first_next_ts_event_ns": _side_from_report(nxt, "first", "ts_event_ns"),
        "first_prior_file_id": _side_from_report(prior, "first", "file_id"),
        "first_prior_row_index": _side_from_report(prior, "first", "row_index"),
        "first_next_file_id": _side_from_report(nxt, "first", "file_id"),
        "first_next_row_index": _side_from_report(nxt, "first", "row_index"),
        "first_delta": first_delta,
        "first_abs_delta": row.get("first_abs_delta") if first_delta is None else abs(first_delta),
        "first_censor": row.get("first_censor"), "first_usable": row.get("first_usable"),
        "first_within_stage": row.get("first_within_stage"),
        "first_within_year": row.get("first_within_year"),
        "last_prior_oi": _side_from_report(prior, "last", "oi"),
        "last_next_oi": _side_from_report(nxt, "last", "oi"),
        "last_prior_ts_event_ns": _side_from_report(prior, "last", "ts_event_ns"),
        "last_next_ts_event_ns": _side_from_report(nxt, "last", "ts_event_ns"),
        "last_prior_file_id": _side_from_report(prior, "last", "file_id"),
        "last_prior_row_index": _side_from_report(prior, "last", "row_index"),
        "last_next_file_id": _side_from_report(nxt, "last", "file_id"),
        "last_next_row_index": _side_from_report(nxt, "last", "row_index"),
        "last_delta": last_delta,
        "last_abs_delta": row.get("last_abs_delta") if last_delta is None else abs(last_delta),
        "last_censor": row.get("last_censor"), "last_usable": row.get("last_usable"),
        "last_within_stage": row.get("last_within_stage"),
        "last_within_year": row.get("last_within_year"),
        "appearance": row.get("appearance"), "listed_on_prior": row.get("listed_on_prior"),
        "certified_listing_birth": bool(row.get("certified_listing_birth")),
        "intraday_terminal_holdings_identified": bool(row.get("intraday_terminal_holdings_identified")),
        "cross_gap_compressed": bool(row.get("cross_gap_compressed")),
        "is_boundary": row.get("is_boundary"),
        "prior_stage": row.get("prior_stage"), "next_stage": row.get("next_stage"),
        "causal_feature_eligible": False,
    }


def iter_logical_lifecycle(life_refs, report_refs=None):
    """Bounded iterator of accepted logical lifecycle rows via report-ledger join."""
    import pyarrow.parquet as pq
    life_refs = _as_ref_list(life_refs)
    if not life_refs:
        return
        yield
    need_reports = False
    tables = []
    for ref in life_refs:
        table = pq.read_table(ref["path"])
        tables.append(table)
        if _is_compact_lifecycle(table):
            need_reports = True
    reports = _report_index(report_refs if report_refs is not None else _discover_report_refs(life_refs)) if need_reports else {}
    for table in tables:
        rows = table.to_pylist()
        if _is_compact_lifecycle(table):
            for row in rows:
                yield _expand_lifecycle_row(row, reports)
        else:
            for row in rows:
                yield row


def read_logical_parts(refs, report_refs=None):
    """Root/test adapter: expand compact kinds to the accepted logical row schema."""
    refs = _as_ref_list(refs)
    if not refs:
        return []
    import pyarrow.parquet as pq
    kind = refs[0].get("kind")
    if kind == COMPACT_LIFECYCLE_KIND or kind == LOGICAL_LIFECYCLE_KIND:
        return list(iter_logical_lifecycle(refs, report_refs))
    if kind == COMPACT_REPORT_KIND or kind == LOGICAL_REPORT_KIND:
        return list(iter_logical_reports(refs))
    sample = pq.read_table(refs[0]["path"])
    if _is_compact_lifecycle(sample):
        return list(iter_logical_lifecycle(refs, report_refs))
    if _is_compact_report(sample):
        return list(iter_logical_reports(refs))
    rows = []
    for ref in refs:
        rows.extend(pq.read_table(ref["path"]).to_pylist())
    return rows


class DateCodebook:
    def __init__(self):
        self.iso_to_days = {}
        self.days_to_iso = {}

    def days(self, label):
        if label is None:
            return None
        hit = self.iso_to_days.get(label)
        if hit is None:
            hit = _iso_to_days(label)
            self.iso_to_days[label] = hit
            self.days_to_iso[hit] = label
        return hit

    def iso(self, days):
        if days is None:
            return None
        hit = self.days_to_iso.get(int(days))
        if hit is None:
            hit = _days_to_iso(days)
            self.days_to_iso[int(days)] = hit
            self.iso_to_days[hit] = int(days)
        return hit


class ClockMaps:
    def __init__(self):
        self.east = {}
        self.seconds = {}
        self.midnight = {}

    def eastern_labels(self, ts_arr):
        np = _np()
        if len(ts_arr) == 0:
            return np.empty(0, dtype=object)
        uniq, inverse = np.unique(np.asarray(ts_arr, dtype=np.int64), return_inverse=True)
        missing = [int(ts) for ts in uniq if int(ts) not in self.east]
        if missing:
            for ts, label in zip(missing, eastern_date_from_ns(missing)):
                self.east[int(ts)] = label
        mapped = np.empty(len(uniq), dtype=object)
        for i, ts in enumerate(uniq):
            mapped[i] = self.east[int(ts)]
        return mapped[inverse]

    def seconds_after(self, ts_arr, east_labels, midnight_cache):
        np = _np()
        n = len(ts_arr)
        out = np.zeros(n, dtype=np.float64)
        present = np.zeros(n, dtype=bool)
        if n == 0:
            return out, present
        uniq, inverse = np.unique(np.asarray(ts_arr, dtype=np.int64), return_inverse=True)
        east_u = np.empty(len(uniq), dtype=object)
        if east_labels is not None and len(east_labels):
            first = np.zeros(len(uniq), dtype=bool)
            for i, inv in enumerate(inverse):
                if not first[inv]:
                    east_u[inv] = east_labels[i]
                    first[inv] = True
        else:
            for i, ts in enumerate(uniq):
                east_u[i] = self.east.get(int(ts))
        sec_u = np.zeros(len(uniq), dtype=np.float64)
        ok_u = np.zeros(len(uniq), dtype=bool)
        for i, ts in enumerate(uniq):
            east = east_u[i]
            if east is None:
                continue
            key = (int(ts), east)
            hit = self.seconds.get(key)
            if hit is None:
                hit = seconds_after_eastern_midnight(int(ts), east, midnight_cache)
                self.seconds[key] = hit
            if hit is not None:
                sec_u[i] = hit
                ok_u[i] = True
        return sec_u[inverse], ok_u[inverse]

    def request_midnight(self, label, cache):
        hit = cache.get(label)
        if hit is None:
            hit = cut_ns_on(label, "00:00")
            cache[label] = hit
        self.midnight[label] = hit
        return hit


class ChainIdentity:
    """Per-chain unique OSI codebook. Output contract_id values stay unique across chains."""

    def __init__(self, next_id=0):
        self.next_id = int(next_id)
        self.osi_to_cid = {}
        self.exp_iso = []
        self.exp_days = []
        self.pending_cid = []
        self.pending_osi = []
        self.pending_exp = []
        self.pending_milli = []
        self.pending_right = []

    def intern(self, chain, osi, exp_iso, milli, right, dates):
        del chain
        np = _np()
        n = len(osi)
        if n == 0:
            return np.empty(0, dtype=np.int32)
        uniq, first_idx, inverse = np.unique(osi, return_index=True, return_inverse=True)
        cid_u = np.empty(len(uniq), dtype=np.int32)
        for u, symbol in enumerate(uniq):
            cid = self.osi_to_cid.get(symbol)
            idx = int(first_idx[u])
            if cid is None:
                cid = self.next_id
                self.next_id += 1
                self.osi_to_cid[symbol] = cid
                exp = exp_iso[idx]
                self.exp_iso.append(exp)
                self.exp_days.append(-1 if exp is None else dates.days(exp))
                self.pending_cid.append(cid)
                self.pending_osi.append(symbol)
                self.pending_exp.append(exp)
                self.pending_milli.append(int(milli[idx]))
                self.pending_right.append(right[idx])
            cid_u[u] = cid
        return cid_u[inverse]

    def expiration_iso(self, cid):
        return self.exp_iso[int(cid)] if 0 <= int(cid) < len(self.exp_iso) else None

    def expiration_days_array(self, cids, dates):
        del dates
        np = _np()
        if not self.exp_days:
            return np.full(len(cids), -1, dtype=np.int32)
        table = np.asarray(self.exp_days, dtype=np.int32)
        return table[np.asarray(cids, dtype=np.int32)]

    def flush_tables(self, chain):
        pa = _pa()
        if not self.pending_cid:
            return None
        table = pa.table({
            "contract_id": pa.array(self.pending_cid, type=pa.int32()),
            "chain": pa.array([chain] * len(self.pending_cid), type=pa.string()),
            "osi_symbol": pa.array(self.pending_osi, type=pa.string()),
            "expiration": pa.array(self.pending_exp, type=pa.string()),
            "millistrike": pa.array(self.pending_milli, type=pa.int64()),
            "right": pa.array(self.pending_right, type=pa.string()),
        }, schema=identity_schema())
        self.pending_cid = []
        self.pending_osi = []
        self.pending_exp = []
        self.pending_milli = []
        self.pending_right = []
        return table

    def release_keys(self):
        self.osi_to_cid.clear()


def _dictionary_keys(column):
    pa, pc = _pa(), _pc()
    combined = column.combine_chunks()
    encoded = pc.dictionary_encode(combined)
    dictionary = encoded.dictionary
    indices = encoded.indices
    index_n = indices.fill_null(-1).to_numpy()
    nulls = pc.is_null(indices).to_numpy().astype(bool, copy=False)
    return dictionary, index_n.astype("int64"), nulls


def _unique_string_map(column, fn):
    dictionary, index, nulls = _dictionary_keys(column)
    values = dictionary.to_pylist()
    mapped = [None if value is None else fn(value) for value in values]
    return mapped, index, nulls


def _date_column_iso(column, dates):
    pa, pc = _pa(), _pc()
    np = _np()
    n = len(column)
    iso = np.empty(n, dtype=object)
    ok = np.zeros(n, dtype=bool)
    if pa.types.is_date(column.type):
        nulls = pc.is_null(column).to_numpy().astype(bool, copy=False)
        days = column.cast(pa.int32()).fill_null(0).to_numpy()
        uniq = np.unique(days[~nulls]) if n else np.empty(0, dtype=np.int32)
        for value in uniq:
            dates.iso(int(value))
        for i in range(n):
            if nulls[i]:
                continue
            iso[i] = dates.iso(int(days[i]))
            ok[i] = True
        return iso, ok, days
    strings = _pc().cast(column, pa.string()) if not (pa.types.is_string(column.type) or pa.types.is_large_string(column.type)) else column
    uniq, inverse, nulls = _dictionary_keys(strings)
    labels = uniq.to_pylist()
    parsed, parsed_ok = _safe_iso_dates(labels)
    days = np.zeros(n, dtype=np.int32)
    for i in range(n):
        if nulls[i]:
            continue
        item = parsed[int(inverse[i])]
        good = parsed_ok[int(inverse[i])]
        iso[i] = item
        ok[i] = bool(good)
        if good and item is not None:
            days[i] = dates.days(item)
    return iso, ok, days


def _millistrike_column(column):
    pa, pc = _pa(), _pc()
    np = _np()
    n = len(column)
    milli = np.full(n, -1, dtype=np.int64)
    strike_f = np.full(n, np.nan, dtype=np.float64)
    strike_ok = np.zeros(n, dtype=bool)
    nulls = pc.is_null(column).to_numpy().astype(bool, copy=False)
    if pa.types.is_floating(column.type):
        values = column.fill_null(float("nan")).to_numpy(zero_copy_only=False)
        strike_f = np.asarray(values, dtype=np.float64)
        finite = (~nulls) & np.isfinite(strike_f)
        uniq = np.unique(strike_f[finite]) if n else np.empty(0, dtype=np.float64)
        mapped = {float(value): millistrike(float(value)) for value in uniq}
        for i in range(n):
            if not finite[i]:
                continue
            strike_ok[i] = True
            hit = mapped[float(strike_f[i])]
            if hit is not None:
                milli[i] = int(hit)
        return milli, strike_f, strike_ok, nulls
    values = column.to_pylist()
    cache = {}
    for i, value in enumerate(values):
        if value is None:
            continue
        strike_ok[i] = True
        if type(value) is float:
            strike_f[i] = value
        if value not in cache:
            cache[value] = millistrike(value)
        hit = cache[value]
        if hit is not None:
            milli[i] = int(hit)
    return milli, strike_f, strike_ok, nulls


def _osi_unique_parse(dictionary):
    pa, pc = _pa(), _pc()
    values = dictionary.to_pylist()
    n_u = len(values)
    parsed = [parse_osi(value) if type(value) is str else None for value in values]
    length_ok = [False] * n_u
    if n_u and (pa.types.is_string(dictionary.type) or pa.types.is_large_string(dictionary.type)):
        slen = pc.utf8_length(dictionary)
        length_ok = [(slen[i].as_py() is not None and slen[i].as_py() == 21) for i in range(n_u)]
        try:
            roots = pc.utf8_trim(pc.utf8_slice_codeunits(dictionary, 0, 6), characters=" ").to_pylist()
            yymmdd = pc.utf8_slice_codeunits(dictionary, 6, 12).to_pylist()
            cp = pc.utf8_slice_codeunits(dictionary, 12, 13).to_pylist()
            strike_s = pc.utf8_slice_codeunits(dictionary, 13, 21).to_pylist()
        except (TypeError, ValueError, AttributeError):
            return parsed, values
        for i, item in enumerate(parsed):
            if item is None or not length_ok[i]:
                continue
            if roots[i] != item["root"]:
                parsed[i] = None
                continue
            if cp[i] not in ("C", "P") or type(strike_s[i]) is not str or not strike_s[i].isdigit():
                parsed[i] = None
                continue
            if type(yymmdd[i]) is not str or not yymmdd[i].isdigit():
                parsed[i] = None
    return parsed, values


def parse_source_typed(table, *, record, schema_str, prev_map, midnight_cache, dates, clocks):
    """Arrow/NumPy parse. Unique OSI codebook only; no whole-day to_pylist on row columns."""
    pa, pc = _pa(), _pc()
    np = _np()
    source = record["source"]
    role, chain, file_id = source["role"], source["chain"], record["file_id"]
    declared = source["request_date"]
    declared_days = dates.days(declared)
    required = OI_FIELDS if role == "open_interest" else CONTRACT_FIELDS
    _check_schema(table, schema_str, required)
    n = len(table)
    empty = {
        "osi": np.empty(0, dtype=object), "expiration": np.empty(0, dtype=object),
        "millistrike": np.empty(0, dtype=np.int64), "right": np.empty(0, dtype=object),
        "request_date": np.empty(0, dtype=object), "open_interest": np.empty(0, dtype=np.int64),
        "ts_event_ns": np.empty(0, dtype=np.int64), "row_index": np.empty(0, dtype=np.int64),
        "file_id": np.empty(0, dtype=np.int64), "dte": np.empty(0, dtype=np.int64),
        "dte_bucket": np.empty(0, dtype=object), "mismatch": np.empty(0, dtype=bool),
        "future": np.empty(0, dtype=bool), "late": np.empty(0, dtype=bool),
        "map_agree": np.empty(0, dtype=bool), "seconds": np.empty(0, dtype=np.float64),
        "seconds_ok": np.empty(0, dtype=bool),
    }
    if n == 0:
        return empty, _empty_exception_arrays(), n, 0

    osi_dict, osi_idx, osi_null = _dictionary_keys(table.column("osi_symbol"))
    osi_parsed, osi_values = _osi_unique_parse(osi_dict)
    exp_iso, exp_ok, exp_days = _date_column_iso(table.column("expiration"), dates)
    req_iso, req_ok, req_days = _date_column_iso(table.column("request_date"), dates)
    milli, strike_f, strike_present, strike_null = _millistrike_column(table.column("strike"))
    right_mapped, right_idx, right_null = _unique_string_map(table.column("right"), normalize_right)
    if "symbol" in table.schema.names:
        sym_mapped, sym_idx, sym_null = _unique_string_map(table.column("symbol"), lambda value: value if type(value) is str else None)
    else:
        sym_mapped, sym_idx, sym_null = [None], np.zeros(n, dtype=np.int64), np.ones(n, dtype=bool)

    osi_root = np.empty(n, dtype=object)
    osi_exp = np.empty(n, dtype=object)
    osi_right = np.empty(n, dtype=object)
    osi_milli = np.full(n, -1, dtype=np.int64)
    osi_ok = np.zeros(n, dtype=bool)
    osi_str = np.empty(n, dtype=object)
    osi_str[~osi_null] = np.asarray(osi_values, dtype=object)[osi_idx[~osi_null]]
    parsed_u_ok = np.array([item is not None for item in osi_parsed], dtype=bool)
    osi_ok[~osi_null] = parsed_u_ok[osi_idx[~osi_null]]
    if osi_parsed:
        root_u = np.array([None if item is None else item["root"] for item in osi_parsed], dtype=object)
        exp_u = np.array([None if item is None else item["expiration"] for item in osi_parsed], dtype=object)
        right_u = np.array([None if item is None else item["right"] for item in osi_parsed], dtype=object)
        milli_u = np.array([-1 if item is None else int(item["millistrike"]) for item in osi_parsed], dtype=np.int64)
        osi_root[~osi_null] = root_u[osi_idx[~osi_null]]
        osi_exp[~osi_null] = exp_u[osi_idx[~osi_null]]
        osi_right[~osi_null] = right_u[osi_idx[~osi_null]]
        osi_milli[~osi_null] = milli_u[osi_idx[~osi_null]]
    right_arr = np.empty(n, dtype=object)
    right_none_u = np.array([value is None for value in right_mapped], dtype=bool)
    right_arr[~right_null] = np.asarray(right_mapped, dtype=object)[right_idx[~right_null]]
    right_none = right_null.copy()
    right_none[~right_null] = right_none_u[right_idx[~right_null]]
    symbol_mismatch = np.zeros(n, dtype=bool)
    if not np.all(sym_null):
        sym_u = np.array(sym_mapped, dtype=object)
        present = ~sym_null
        symbols = sym_u[sym_idx[present]]
        symbol_mismatch[np.nonzero(present)[0]] = np.array(
            [(type(value) is str and value != chain) for value in symbols], dtype=bool)

    reason = np.zeros(n, dtype=np.int8)

    def take(mask, code):
        sel = (reason == 0) & mask
        reason[sel] = code

    take(~exp_ok, 1)
    take(~req_ok, 2)
    take(osi_null | right_none | (~exp_ok), 3)
    take((~osi_null) & exp_ok & (~right_none) & (milli < 0) & strike_null, 3)
    take((milli < 0) & (~strike_null), 4)
    take((~osi_null) & (~osi_ok), 5)
    take(osi_ok & ((osi_root != chain) | symbol_mismatch), 6)
    take(osi_ok & ((osi_exp != exp_iso) | (osi_right != right_arr) | (osi_milli != milli)), 7)
    take(req_ok & (req_days != declared_days), 8)

    oi_arr = np.zeros(n, dtype=np.int64)
    oi_int_ok = np.ones(n, dtype=bool)
    ts_arr = np.zeros(n, dtype=np.int64)
    ts_ok = np.zeros(n, dtype=bool)
    if role == "open_interest":
        oi_col = table.column("open_interest")
        if pa.types.is_floating(oi_col.type):
            oi_int_ok[:] = False
        elif pa.types.is_integer(oi_col.type):
            oi_null = pc.is_null(oi_col).to_numpy().astype(bool, copy=False)
            oi_arr = oi_col.fill_null(0).cast(pa.int64()).to_numpy()
            take(oi_null, 9)
            take((~oi_null) & (oi_arr < 0), 11)
        else:
            oi_int_ok[:] = False
        if pa.types.is_floating(oi_col.type) or not pa.types.is_integer(oi_col.type):
            take(np.ones(n, dtype=bool), 10)
        ts_col = timestamp_ns_from_arrow(table.column("ts_event"))
        ts_null = pc.is_null(ts_col).to_numpy().astype(bool, copy=False)
        ts_arr = ts_col.fill_null(0).cast(pa.int64()).to_numpy().astype(np.int64, copy=False)
        ts_ok = ~ts_null
        take(~ts_ok, 12)

    invalid = reason > 0
    exceptions = _exception_arrays(
        file_id=file_id, chain=chain, role=role, declared=declared, n=n, invalid=invalid,
        reason=reason, osi_str=osi_str, exp_iso=exp_iso, strike_f=strike_f, strike_present=strike_present,
        right_arr=right_arr, oi_arr=oi_arr, oi_int_ok=oi_int_ok, ts_arr=ts_arr, ts_ok=ts_ok, role_oi=(role == "open_interest"),
    )
    finalize_exceptions(exceptions, req_iso, declared)
    valid = ~invalid
    if not np.any(valid):
        return empty, exceptions, n, 0

    osi_v = osi_str[valid]
    exp_v = exp_iso[valid]
    milli_v = milli[valid]
    right_v = right_arr[valid]
    req_v = req_iso[valid]
    row_v = np.nonzero(valid)[0].astype(np.int64, copy=False)
    fid_v = np.full(int(valid.sum()), int(file_id), dtype=np.int64)
    if role == "open_interest":
        oi_v = oi_arr[valid]
        ts_v = ts_arr[valid]
        east = clocks.eastern_labels(ts_v)
        east_ok = np.fromiter((value is not None for value in east), dtype=bool, count=len(east))
        east_fill = np.array(east, dtype=object)
        east_fill[~east_ok] = req_v[~east_ok]
        mismatch = east_ok & (east_fill != req_v)
        future = east_ok & (east_fill > req_v)
        seconds, seconds_ok = clocks.seconds_after(ts_v, east, midnight_cache)
        late = seconds_ok & (seconds > 15 * 3600)
        req_u, req_inv = np.unique(req_v, return_inverse=True)
        east_u, east_inv = np.unique(east, return_inverse=True)
        pos_req_u = np.array([prev_map.get(label) for label in req_u], dtype=object)
        pos_evt_u = np.array([prev_map.get(label) if label else None for label in east_u], dtype=object)
        pos_req = pos_req_u[req_inv]
        pos_evt = pos_evt_u[east_inv]
        map_agree = (pos_req != None) & (pos_req == pos_evt)  # noqa: E711
        dte_v, bucket_v = _dte_columns(exp_v, req_v)
    else:
        oi_v = np.empty(0, dtype=np.int64)
        ts_v = np.empty(0, dtype=np.int64)
        mismatch = np.empty(0, dtype=bool)
        future = np.empty(0, dtype=bool)
        late = np.empty(0, dtype=bool)
        map_agree = np.empty(0, dtype=bool)
        seconds = np.empty(0, dtype=np.float64)
        seconds_ok = np.empty(0, dtype=bool)
        dte_v, bucket_v = _dte_columns(exp_v, req_v)
    return {
        "osi": osi_v, "expiration": exp_v, "millistrike": milli_v, "right": right_v,
        "request_date": req_v, "open_interest": oi_v, "ts_event_ns": ts_v,
        "row_index": row_v, "file_id": fid_v, "dte": dte_v, "dte_bucket": bucket_v,
        "mismatch": mismatch, "future": future, "late": late, "map_agree": map_agree,
        "seconds": seconds, "seconds_ok": seconds_ok,
    }, exceptions, n, int(valid.sum())


def _dte_columns(exp_iso, req_iso):
    np = _np()
    n = len(exp_iso)
    if n == 0:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=object)
    exp_u, exp_inv = np.unique(np.asarray(exp_iso, dtype=object), return_inverse=True)
    req_u, req_inv = np.unique(np.asarray(req_iso, dtype=object), return_inverse=True)
    dte_grid = np.empty((len(exp_u), len(req_u)), dtype=np.int64)
    bucket_grid = np.empty((len(exp_u), len(req_u)), dtype=object)
    for i, exp in enumerate(exp_u):
        for j, req in enumerate(req_u):
            days = dte_days(exp, req)
            dte_grid[i, j] = days
            bucket_grid[i, j] = dte_bucket(days)
    return dte_grid[exp_inv, req_inv], bucket_grid[exp_inv, req_inv]


def _empty_exception_arrays():
    np = _np()
    return {
        "file_id": np.empty(0, dtype=np.int64), "row_index": np.empty(0, dtype=np.int64),
        "chain": np.empty(0, dtype=object), "role": np.empty(0, dtype=object),
        "request_date": np.empty(0, dtype=object), "invalid_reason": np.empty(0, dtype=object),
        "osi_symbol": np.empty(0, dtype=object), "expiration": np.empty(0, dtype=object),
        "strike": np.empty(0, dtype=np.float64), "strike_valid": np.empty(0, dtype=bool),
        "right": np.empty(0, dtype=object), "open_interest": np.empty(0, dtype=np.int64),
        "oi_valid": np.empty(0, dtype=bool), "ts_event_ns": np.empty(0, dtype=np.int64),
        "ts_valid": np.empty(0, dtype=bool),
    }


def _exception_arrays(*, file_id, chain, role, declared, n, invalid, reason, osi_str, exp_iso,
                      strike_f, strike_present, right_arr, oi_arr, oi_int_ok, ts_arr, ts_ok, role_oi):
    np = _np()
    idx = np.nonzero(invalid)[0]
    k = len(idx)
    if k == 0:
        return _empty_exception_arrays()
    req = np.empty(k, dtype=object)
    strike_valid = np.zeros(k, dtype=bool)
    strike = np.full(k, np.nan, dtype=np.float64)
    oi_valid = np.zeros(k, dtype=bool)
    ts_valid = np.zeros(k, dtype=bool)
    reasons = np.empty(k, dtype=object)
    for j, i in enumerate(idx):
        req_s = exp_iso  # placeholder to keep order; request from caller via declared fallback
        reasons[j] = _REASON_NAMES[int(reason[i])]
        strike_valid[j] = bool(strike_present[i])
        if strike_present[i] and np.isfinite(strike_f[i]):
            strike[j] = float(strike_f[i])
        if role_oi and oi_int_ok[i]:
            oi_valid[j] = True
        if role_oi and ts_ok[i]:
            ts_valid[j] = True
    # request_date: valid iso string or declared
    request = np.empty(k, dtype=object)
    # exp_iso here is expiration; request reconstructed below by the caller arrays
    return {
        "file_id": np.full(k, int(file_id), dtype=np.int64),
        "row_index": idx.astype(np.int64, copy=False),
        "chain": np.full(k, chain, dtype=object),
        "role": np.full(k, role, dtype=object),
        "request_date": request,  # filled by caller
        "invalid_reason": reasons,
        "osi_symbol": osi_str[idx],
        "expiration": exp_iso[idx],
        "strike": strike,
        "strike_valid": strike_valid,
        "right": right_arr[idx],
        "open_interest": oi_arr[idx] if role_oi else np.zeros(k, dtype=np.int64),
        "oi_valid": oi_valid,
        "ts_event_ns": ts_arr[idx] if role_oi else np.zeros(k, dtype=np.int64),
        "ts_valid": ts_valid,
        "_declared": declared,
        "_req_iso": None,
    }


def finalize_exceptions(exc, req_iso, declared):
    """Fill exception request_date: parsed iso when it is a string, else declared."""
    if exc is None or len(exc["file_id"]) == 0:
        return exc
    request = exc["request_date"]
    for j, i in enumerate(exc["row_index"]):
        value = req_iso[int(i)] if req_iso is not None else None
        request[j] = value if type(value) is str else declared
    return exc


def exceptions_to_table(exc):
    pa = _pa()
    n = len(exc["file_id"])
    if n == 0:
        return None
    strike = [float(exc["strike"][i]) if exc["strike_valid"][i] and exc["strike"][i] == exc["strike"][i] else None
              for i in range(n)]
    # Only emit strike when the source value was a float (accepted exception contract).
    strike_out = []
    for i in range(n):
        strike_out.append(strike[i] if exc["strike_valid"][i] else None)
    oi = [int(exc["open_interest"][i]) if exc["oi_valid"][i] else None for i in range(n)]
    ts = [int(exc["ts_event_ns"][i]) if exc["ts_valid"][i] else None for i in range(n)]
    return pa.table({
        "file_id": pa.array(exc["file_id"], type=pa.int64()),
        "row_index": pa.array(exc["row_index"], type=pa.int64()),
        "chain": pa.array(exc["chain"], type=pa.string()),
        "role": pa.array(exc["role"], type=pa.string()),
        "request_date": pa.array(exc["request_date"], type=pa.string()),
        "invalid_reason": pa.array(exc["invalid_reason"], type=pa.string()),
        "osi_symbol": pa.array(exc["osi_symbol"], type=pa.string()),
        "expiration": pa.array(exc["expiration"], type=pa.string()),
        "strike": pa.array(strike_out, type=pa.float64()),
        "right": pa.array(exc["right"], type=pa.string()),
        "open_interest": pa.array(oi, type=pa.int64()),
        "ts_event_ns": pa.array(ts, type=pa.int64()),
    }, schema=exception_schema())


def membership_table(file_id, path, sha256, chain, role, request_date, rows_read, rows_valid, rows_invalid, empty_marker):
    pa = _pa()
    return pa.table({
        "file_id": pa.array([int(file_id)], type=pa.int64()),
        "path": pa.array([path], type=pa.string()),
        "sha256": pa.array([sha256], type=pa.string()),
        "chain": pa.array([chain], type=pa.string()),
        "role": pa.array([role], type=pa.string()),
        "request_date": pa.array([request_date], type=pa.string()),
        "rows_read": pa.array([int(rows_read)], type=pa.int64()),
        "rows_valid": pa.array([int(rows_valid)], type=pa.int64()),
        "rows_invalid": pa.array([int(rows_invalid)], type=pa.int64()),
        "empty_marker": pa.array([bool(empty_marker)], type=pa.bool_()),
    }, schema=membership_schema())


def resolve_reports_typed(contract_id, ts, oi, file_id, row_index):
    """Vector first/last on sorted (cid, ts, fid, row). Conflict = min!=max OI in a time group."""
    np = _np()
    n = len(contract_id)
    empty = {
        "contract_id": np.empty(0, dtype=np.int32),
        "first_oi": np.empty(0, dtype=np.int64), "first_ts": np.empty(0, dtype=np.int64),
        "first_fid": np.empty(0, dtype=np.int64), "first_row": np.empty(0, dtype=np.int64),
        "last_oi": np.empty(0, dtype=np.int64), "last_ts": np.empty(0, dtype=np.int64),
        "last_fid": np.empty(0, dtype=np.int64), "last_row": np.empty(0, dtype=np.int64),
        "has_point": np.empty(0, dtype=bool),
        "alias_multiplicity": np.empty(0, dtype=np.int64),
        "same_time_conflict": np.empty(0, dtype=bool),
        "update_candidate": np.empty(0, dtype=bool),
        "observed_update_difference": np.empty(0, dtype=np.int64),
        "update_valid": np.empty(0, dtype=bool),
        "usable": np.empty(0, dtype=bool),
        "n_source_rows": np.empty(0, dtype=np.int64),
        "n_distinct_times": np.empty(0, dtype=np.int64),
        "support_observations": np.empty(0, dtype=np.int64),
        "last_eq_first": np.empty(0, dtype=bool),
    }
    if n == 0:
        return empty
    cid = np.asarray(contract_id, dtype=np.int32)
    ts_a = np.asarray(ts, dtype=np.int64)
    oi_a = np.asarray(oi, dtype=np.int64)
    fid = np.asarray(file_id, dtype=np.int64)
    rid = np.asarray(row_index, dtype=np.int64)
    order = np.lexsort((rid, fid, ts_a, cid))
    cid, ts_a, oi_a, fid, rid = cid[order], ts_a[order], oi_a[order], fid[order], rid[order]
    same_time = (cid[1:] == cid[:-1]) & (ts_a[1:] == ts_a[:-1])
    gstart = np.concatenate((np.array([0], dtype=np.int64), np.nonzero(~same_time)[0].astype(np.int64) + 1))
    gcount = np.empty(len(gstart), dtype=np.int64)
    gcount[:-1] = gstart[1:] - gstart[:-1]
    gcount[-1] = n - gstart[-1]
    gmin = np.minimum.reduceat(oi_a, gstart)
    gmax = np.maximum.reduceat(oi_a, gstart)
    g_conflict = gmin != gmax
    g_cid = cid[gstart]
    g_ts = ts_a[gstart]
    g_oi = oi_a[gstart]
    g_fid = fid[gstart]
    g_rid = rid[gstart]
    cid_change = np.ones(len(g_cid), dtype=bool)
    cid_change[1:] = g_cid[1:] != g_cid[:-1]
    cstart = np.nonzero(cid_change)[0].astype(np.int64, copy=False)
    n_c = len(cstart)
    ccount = np.empty(n_c, dtype=np.int64)
    ccount[:-1] = cstart[1:] - cstart[:-1]
    ccount[-1] = len(g_cid) - cstart[-1]
    valid = ~g_conflict
    gidx = np.arange(len(g_cid), dtype=np.int64)
    first_pos = np.minimum.reduceat(np.where(valid, gidx, len(g_cid) + 1), cstart)
    last_pos = np.maximum.reduceat(np.where(valid, gidx, np.int64(-1)), cstart)
    has_point = first_pos <= len(g_cid)
    out_cid = g_cid[cstart]
    first_oi = np.zeros(n_c, dtype=np.int64)
    first_ts = np.zeros(n_c, dtype=np.int64)
    first_fid = np.zeros(n_c, dtype=np.int64)
    first_row = np.zeros(n_c, dtype=np.int64)
    last_oi = np.zeros(n_c, dtype=np.int64)
    last_ts = np.zeros(n_c, dtype=np.int64)
    last_fid = np.zeros(n_c, dtype=np.int64)
    last_row = np.zeros(n_c, dtype=np.int64)
    if np.any(has_point):
        fp = first_pos[has_point]
        lp = last_pos[has_point]
        first_oi[has_point] = g_oi[fp]
        first_ts[has_point] = g_ts[fp]
        first_fid[has_point] = g_fid[fp]
        first_row[has_point] = g_rid[fp]
        last_oi[has_point] = g_oi[lp]
        last_ts[has_point] = g_ts[lp]
        last_fid[has_point] = g_fid[lp]
        last_row[has_point] = g_rid[lp]
    conflict = np.logical_or.reduceat(g_conflict, cstart)
    alias = np.maximum.reduceat(gcount, cstart)
    n_times = ccount
    support = np.add.reduceat(valid.astype(np.int64, copy=False), cstart)
    row_count = np.add.reduceat(gcount, cstart)
    update = has_point & (first_ts != last_ts) & (first_oi != last_oi)
    last_eq = (~has_point) | ((first_ts == last_ts) & (first_oi == last_oi) & (first_fid == last_fid) & (first_row == last_row))
    usable = has_point & (~conflict)
    return {
        "contract_id": out_cid.astype(np.int32, copy=False),
        "first_oi": first_oi, "first_ts": first_ts, "first_fid": first_fid, "first_row": first_row,
        "last_oi": last_oi, "last_ts": last_ts, "last_fid": last_fid, "last_row": last_row,
        "has_point": has_point, "alias_multiplicity": alias, "same_time_conflict": conflict,
        "update_candidate": update, "observed_update_difference": last_oi - first_oi,
        "update_valid": update, "usable": usable, "n_source_rows": row_count,
        "n_distinct_times": n_times, "support_observations": support, "last_eq_first": last_eq,
    }


def _last_per_cid(cids, values):
    np = _np()
    if len(cids) == 0:
        return {}
    rev = cids[::-1]
    _, idx = np.unique(rev, return_index=True)
    last = len(cids) - 1 - idx
    return {int(cids[i]): values[i] for i in last}


def _lookup_sorted(sorted_ids, keys):
    np = _np()
    if len(keys) == 0:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=bool)
    if len(sorted_ids) == 0:
        return np.full(len(keys), -1, dtype=np.int64), np.zeros(len(keys), dtype=bool)
    idx = np.searchsorted(sorted_ids, keys)
    ok = idx < len(sorted_ids)
    clipped = np.clip(idx, 0, len(sorted_ids) - 1)
    ok &= sorted_ids[clipped] == keys
    return np.where(ok, idx, np.int64(-1)), ok


def _censor_side(has_prior, has_curr, expired, right_boundary, left_boundary,
                 prior_ts, curr_ts, prior_usable, curr_usable, prior_oi_ok, curr_oi_ok,
                 prior_date, next_date, prior_stage, next_stage):
    np = _np()
    n = len(has_prior)
    censor = np.empty(n, dtype=object)
    clock_ok = np.ones(n, dtype=bool)
    both = has_prior & has_curr
    clock_fail = both & ((~prior_oi_ok) | (~curr_oi_ok) | (prior_ts >= curr_ts))
    clock_ok[clock_fail] = False
    missing_curr = ~has_curr
    censor[missing_curr & right_boundary] = "right_source_boundary"
    censor[missing_curr & (~right_boundary) & expired] = "expired_before_next_request_date"
    censor[missing_curr & (~right_boundary) & (~expired)] = "missing_next_publication"
    missing_prior = has_curr & (~has_prior)
    censor[missing_prior & left_boundary] = "left_source_boundary"
    censor[missing_prior & (~left_boundary)] = "prior_report_missing"
    censor[clock_fail] = "clock_order_violated"
    usable = both & clock_ok & prior_usable & curr_usable & prior_oi_ok & curr_oi_ok
    year_ok = usable & (prior_date is not None) & (next_date is not None)
    if prior_date is not None and next_date is not None:
        year_ok = usable & (prior_date[:4] == next_date[:4])
    else:
        year_ok = np.zeros(n, dtype=bool)
    stage_ok = usable & (prior_stage is not None) & (prior_stage == next_stage)
    is_boundary = (censor == "right_source_boundary") | (censor == "left_source_boundary")
    appearance = np.where(has_prior, "continuing", "first_observed")
    return censor, usable, clock_ok, year_ok, stage_ok, is_boundary, appearance


def join_lifecycle_typed(prev, curr, prev_listings, curr_listings, *, chain, prior_date, next_date,
                         last_selected, first_selected, prior_stage, next_stage, listing_known,
                         identities, dates):
    del curr_listings
    np = _np()
    prev_ids = prev["contract_id"] if prev is not None else np.empty(0, dtype=np.int32)
    curr_ids = curr["contract_id"] if curr is not None else np.empty(0, dtype=np.int32)
    if len(prev_ids) == 0 and len(curr_ids) == 0:
        return None
    all_cids = np.union1d(prev_ids, curr_ids).astype(np.int32, copy=False)
    n = len(all_cids)
    p_idx, has_p = _lookup_sorted(prev_ids, all_cids)
    c_idx, has_c = _lookup_sorted(curr_ids, all_cids)
    exp_days = identities.expiration_days_array(all_cids, dates)
    next_days = -1 if next_date is None else dates.days(next_date)
    expired = (exp_days >= 0) & (next_days >= 0) & (exp_days < next_days)
    right_boundary = (next_date is None) or (last_selected is not None and prior_date == last_selected)
    left_boundary = first_selected is not None and next_date == first_selected
    right_b = np.full(n, bool(right_boundary))
    left_b = np.full(n, bool(left_boundary))

    def take(batch, idx, name, ok):
        arr = np.zeros(n, dtype=np.int64)
        present = np.zeros(n, dtype=bool)
        if batch is not None and np.any(ok):
            arr[ok] = batch[name][idx[ok]]
            if name in {"first_oi", "last_oi", "first_ts", "last_ts"}:
                present[ok] = batch["has_point"][idx[ok]]
            else:
                present[ok] = True
        return arr, present

    def take_bool(batch, idx, name, ok):
        arr = np.zeros(n, dtype=bool)
        if batch is not None and np.any(ok):
            arr[ok] = batch[name][idx[ok]]
        return arr

    p_first_oi, p_first_ok = take(prev, p_idx, "first_oi", has_p)
    p_first_ts, _ = take(prev, p_idx, "first_ts", has_p)
    p_last_oi, p_last_ok = take(prev, p_idx, "last_oi", has_p)
    p_last_ts, _ = take(prev, p_idx, "last_ts", has_p)
    c_first_oi, c_first_ok = take(curr, c_idx, "first_oi", has_c)
    c_first_ts, _ = take(curr, c_idx, "first_ts", has_c)
    c_last_oi, c_last_ok = take(curr, c_idx, "last_oi", has_c)
    c_last_ts, _ = take(curr, c_idx, "last_ts", has_c)
    p_use = take_bool(prev, p_idx, "usable", has_p)
    c_use = take_bool(curr, c_idx, "usable", has_c)
    p_rid, p_rid_ok = take(prev, p_idx, "report_id", has_p) if prev is not None and "report_id" in prev else (np.full(n, -1, dtype=np.int64), has_p)
    c_rid, c_rid_ok = take(curr, c_idx, "report_id", has_c) if curr is not None and "report_id" in curr else (np.full(n, -1, dtype=np.int64), has_c)

    f_censor, f_usable, _, f_year, f_stage, f_bound, appearance = _censor_side(
        has_p, has_c, expired, right_b, left_b, p_first_ts, c_first_ts, p_use, c_use,
        p_first_ok, c_first_ok, prior_date, next_date, prior_stage, next_stage)
    l_censor, l_usable, _, l_year, l_stage, _, _ = _censor_side(
        has_p, has_c, expired, right_b, left_b, p_last_ts, c_last_ts, p_use, c_use,
        p_last_ok, c_last_ok, prior_date, next_date, prior_stage, next_stage)

    f_delta = np.zeros(n, dtype=np.int64)
    l_delta = np.zeros(n, dtype=np.int64)
    f_delta[f_usable] = c_first_oi[f_usable] - p_first_oi[f_usable]
    l_delta[l_usable] = c_last_oi[l_usable] - p_last_oi[l_usable]
    listed = None
    listed_arr = np.zeros(n, dtype=bool)
    listed_valid = np.zeros(n, dtype=bool)
    if listing_known:
        _, listed_arr = _lookup_sorted(np.sort(np.asarray(prev_listings, dtype=np.int32)), all_cids) if len(prev_listings) else (None, np.zeros(n, dtype=bool))
        listed_valid[:] = True
    return {
        "contract_id": all_cids, "has_prior": has_p, "has_curr": has_c,
        "prior_report_id": p_rid, "prior_report_ok": p_rid_ok,
        "next_report_id": c_rid, "next_report_ok": c_rid_ok,
        "first_delta": f_delta, "first_usable": f_usable, "first_censor": f_censor,
        "first_within_stage": f_stage, "first_within_year": f_year,
        "last_delta": l_delta, "last_usable": l_usable, "last_censor": l_censor,
        "last_within_stage": l_stage, "last_within_year": l_year,
        "appearance": appearance, "is_boundary": f_bound,
        "listed_on_prior": listed_arr, "listed_valid": listed_valid,
        "prior_missing": ~has_p,
    }


def lifecycle_to_table(life, *, chain, prior_date, next_date, prior_stage, next_stage):
    if life is None:
        return None
    pa = _pa()
    n = len(life["contract_id"])
    if n == 0:
        return None
    prior_ids = [int(life["prior_report_id"][i]) if life["prior_report_ok"][i] else None for i in range(n)]
    next_ids = [int(life["next_report_id"][i]) if life["next_report_ok"][i] else None for i in range(n)]
    first_delta = [int(life["first_delta"][i]) if life["first_usable"][i] else None for i in range(n)]
    last_delta = [int(life["last_delta"][i]) if life["last_usable"][i] else None for i in range(n)]
    listed = [bool(life["listed_on_prior"][i]) if life["listed_valid"][i] else None for i in range(n)]
    schema = _with_storage_meta(compact_lifecycle_schema(), LOGICAL_LIFECYCLE_KIND, COMPACT_LIFECYCLE_KIND)
    return pa.table({
        "contract_id": pa.array(life["contract_id"], type=pa.int32()),
        "chain": pa.array([chain] * n, type=pa.string()),
        "prior_date": pa.array([prior_date] * n, type=pa.string()),
        "next_date": pa.array([next_date] * n, type=pa.string()),
        "prior_report_id": pa.array(prior_ids, type=pa.int64()),
        "next_report_id": pa.array(next_ids, type=pa.int64()),
        "first_delta": pa.array(first_delta, type=pa.int64()),
        "first_abs_delta": pa.array([None if v is None else abs(v) for v in first_delta], type=pa.int64()),
        "first_censor": pa.array(life["first_censor"], type=pa.string()),
        "first_usable": pa.array(life["first_usable"], type=pa.bool_()),
        "first_within_stage": pa.array(life["first_within_stage"], type=pa.bool_()),
        "first_within_year": pa.array(life["first_within_year"], type=pa.bool_()),
        "last_delta": pa.array(last_delta, type=pa.int64()),
        "last_abs_delta": pa.array([None if v is None else abs(v) for v in last_delta], type=pa.int64()),
        "last_censor": pa.array(life["last_censor"], type=pa.string()),
        "last_usable": pa.array(life["last_usable"], type=pa.bool_()),
        "last_within_stage": pa.array(life["last_within_stage"], type=pa.bool_()),
        "last_within_year": pa.array(life["last_within_year"], type=pa.bool_()),
        "appearance": pa.array(life["appearance"], type=pa.string()),
        "listed_on_prior": pa.array(listed, type=pa.bool_()),
        "certified_listing_birth": pa.array([False] * n, type=pa.bool_()),
        "intraday_terminal_holdings_identified": pa.array([False] * n, type=pa.bool_()),
        "cross_gap_compressed": pa.array([False] * n, type=pa.bool_()),
        "is_boundary": pa.array(life["is_boundary"], type=pa.bool_()),
        "prior_stage": pa.array([prior_stage] * n, type=pa.string()),
        "next_stage": pa.array([next_stage] * n, type=pa.string()),
        "causal_feature_eligible": pa.array([False] * n, type=pa.bool_()),
    }, schema=schema)


def tally_lifecycle(agg, life, prior_date, next_date, prior_stage, next_stage):
    if life is None:
        return
    np = _np()
    n = len(life["contract_id"])
    if n == 0:
        return
    boundary = life["is_boundary"]
    agg["lifecycle_boundary"]["first"]["n_attempts"] += int(boundary.sum())
    agg["lifecycle_boundary"]["last"]["n_attempts"] += int(boundary.sum())
    keep = ~boundary
    if not np.any(keep):
        return
    same_stage = prior_stage is not None and prior_stage == next_stage
    same_year = bool(prior_date and next_date and prior_date[:4] == next_date[:4])
    _tally_mask(agg["lifecycle_all"]["first"], life, "first", keep)
    _tally_mask(agg["lifecycle_all"]["last"], life, "last", keep)
    if same_stage:
        _tally_mask(agg["lifecycle_within_stage"]["first"], life, "first", keep)
        _tally_mask(agg["lifecycle_within_stage"]["last"], life, "last", keep)
    if same_year:
        _tally_mask(agg["lifecycle_within_year"]["first"], life, "first", keep)
        _tally_mask(agg["lifecycle_within_year"]["last"], life, "last", keep)


def _tally_mask(acc, life, side, mask):
    np = _np()
    m = mask
    acc["n_attempts"] += int(m.sum())
    acc["n_first_observed"] += int((m & (life["appearance"] == "first_observed")).sum())
    acc["n_prior_missing"] += int((m & life["prior_missing"]).sum())
    censor = life[f"{side}_censor"]
    acc["n_censor_missing"] += int((m & (censor == "missing_next_publication")).sum())
    acc["n_censor_expired"] += int((m & (censor == "expired_before_next_request_date")).sum())
    usable = m & life[f"{side}_usable"]
    if not np.any(usable):
        return
    delta = life[f"{side}_delta"][usable]
    acc["n"] += int(usable.sum())
    acc["delta_sum"] += int(delta.sum())
    acc["abs_sum"] += int(np.abs(delta).sum())
    acc["n_pos"] += int((delta > 0).sum())
    acc["n_zero"] += int((delta == 0).sum())
    acc["n_neg"] += int((delta < 0).sum())


def finish_day_policies_typed(agg, reports, first_secs, first_ok, last_secs, last_ok, rights, buckets):
    np = _np()
    n = len(reports["contract_id"])
    if n == 0:
        return
    usable = reports["usable"]
    _fill_policy(agg["first"], reports["first_oi"], reports["has_point"], usable, first_secs, first_ok)
    _fill_policy(agg["last"], reports["last_oi"], reports["has_point"], usable, last_secs, last_ok)
    both = usable & reports["has_point"]
    if np.any(both):
        first_sum = int(reports["first_oi"][both].sum())
        last_sum = int(reports["last_oi"][both].sum())
        n_both = int(both.sum())
        diff = first_sum - last_sum
        for acc in (agg["first"], agg["last"]):
            acc["common_n"] += n_both
            acc["common_first_sum"] += first_sum
            acc["common_last_sum"] += last_sum
            acc["paired_diff_sum"] += diff
    _policy_by_key(agg["by_right"], reports, rights, first_secs, first_ok, last_secs, last_ok)
    _policy_by_key(agg["by_dte"], reports, buckets, first_secs, first_ok, last_secs, last_ok)


def _fill_policy(acc, oi, has_point, usable, seconds, seconds_ok):
    np = _np()
    mask = usable & has_point
    if not np.any(mask):
        return
    values = oi[mask]
    acc["oi_sum"] += int(values.sum())
    acc["oi_n"] += int(mask.sum())
    acc["zero_n"] += int((values == 0).sum())
    acc["usable_n"] += int(mask.sum())
    acc["own_n"] += int(mask.sum())
    sec_mask = mask & seconds_ok
    if np.any(sec_mask):
        acc["seconds_sum"] += float(seconds[sec_mask].sum())
        acc["seconds_n"] += int(sec_mask.sum())


def _policy_by_key(store, reports, keys, first_secs, first_ok, last_secs, last_ok):
    np = _np()
    n = len(keys)
    if n == 0:
        return
        labels = np.array([key or "unknown" for key in keys], dtype=object)
    uniq, inverse = np.unique(labels, return_inverse=True)
    usable = reports["usable"]
    has = reports["has_point"]
    for code, name in enumerate(uniq):
        mask = inverse == code
        block = store.setdefault(str(name), {"first": _policy_acc(), "last": _policy_acc()})
        _fill_policy(block["first"], reports["first_oi"], has & mask, usable & mask, first_secs, first_ok)
        _fill_policy(block["last"], reports["last_oi"], has & mask, usable & mask, last_secs, last_ok)


def reports_to_table(reports, *, chain, label, listed, dte, bucket, right, report_ids):
    pa = _pa()
    n = len(reports["contract_id"])
    if n == 0:
        return None
    has = reports["has_point"]
    last_eq = reports["last_eq_first"]
    first_oi = [int(reports["first_oi"][i]) if has[i] else None for i in range(n)]
    first_ts = [int(reports["first_ts"][i]) if has[i] else None for i in range(n)]
    first_fid = [int(reports["first_fid"][i]) if has[i] else None for i in range(n)]
    first_row = [int(reports["first_row"][i]) if has[i] else None for i in range(n)]
    last_oi = [None if last_eq[i] else (int(reports["last_oi"][i]) if has[i] else None) for i in range(n)]
    last_ts = [None if last_eq[i] else (int(reports["last_ts"][i]) if has[i] else None) for i in range(n)]
    last_fid = [None if last_eq[i] else (int(reports["last_fid"][i]) if has[i] else None) for i in range(n)]
    last_row = [None if last_eq[i] else (int(reports["last_row"][i]) if has[i] else None) for i in range(n)]
    update = reports["update_candidate"]
    schema = _with_storage_meta(compact_report_schema(), LOGICAL_REPORT_KIND, COMPACT_REPORT_KIND)
    return pa.table({
        "report_id": pa.array(report_ids, type=pa.int64()),
        "contract_id": pa.array(reports["contract_id"], type=pa.int32()),
        "chain": pa.array([chain] * n, type=pa.string()),
        "request_date": pa.array([label] * n, type=pa.string()),
        "listed": pa.array(listed, type=pa.bool_()),
        "first_oi": pa.array(first_oi, type=pa.int64()),
        "first_ts_event_ns": pa.array(first_ts, type=pa.int64()),
        "first_file_id": pa.array(first_fid, type=pa.int64()),
        "first_row_index": pa.array(first_row, type=pa.int64()),
        "last_oi": pa.array(last_oi, type=pa.int64()),
        "last_ts_event_ns": pa.array(last_ts, type=pa.int64()),
        "last_file_id": pa.array(last_fid, type=pa.int64()),
        "last_row_index": pa.array(last_row, type=pa.int64()),
        "alias_multiplicity": pa.array(reports["alias_multiplicity"], type=pa.int64()),
        "same_time_conflict": pa.array(reports["same_time_conflict"], type=pa.bool_()),
        "conflict_disposition": pa.array(
            ["same_time_no_winner" if reports["same_time_conflict"][i] else "none" for i in range(n)],
            type=pa.string()),
        "update_candidate": pa.array(update, type=pa.bool_()),
        "observed_update_difference": pa.array(
            [int(reports["observed_update_difference"][i]) if update[i] else None for i in range(n)],
            type=pa.int64()),
        "certified_revision": pa.array([False] * n, type=pa.bool_()),
        "usable_for_statistics": pa.array(reports["usable"], type=pa.bool_()),
        "n_source_rows": pa.array(reports["n_source_rows"], type=pa.int64()),
        "n_distinct_times": pa.array(reports["n_distinct_times"], type=pa.int64()),
        "support_observations": pa.array(reports["support_observations"], type=pa.int64()),
        "dte": pa.array(dte, type=pa.int64()),
        "dte_bucket": pa.array(bucket, type=pa.string()),
        "right": pa.array(right, type=pa.string()),
        "causal_feature_eligible": pa.array([False] * n, type=pa.bool_()),
        "last_eq_first": pa.array(last_eq, type=pa.bool_()),
    }, schema=schema)


class TypedAsof:
    """Live arrays + bounded pending. Source-ts order; eligibility = max(ts, request midnight)."""

    def __init__(self, chain, dates, midnight_cache):
        np = _np()
        self.chain = chain
        self.dates = dates
        self.midnight_cache = midnight_cache
        self.p_cid = np.empty(0, dtype=np.int32)
        self.p_ts = np.empty(0, dtype=np.int64)
        self.p_oi = np.empty(0, dtype=np.int64)
        self.p_req = np.empty(0, dtype=object)
        self.p_fid = np.empty(0, dtype=np.int64)
        self.p_row = np.empty(0, dtype=np.int64)
        self.p_exp = np.empty(0, dtype=object)
        self.live_cid = []
        self.live_oi = []
        self.live_oi_ok = []
        self.live_ts = []
        self.live_req = []
        self.live_amb = []
        self.live_exp = []
        self.live_from = []
        self.live_fid = []
        self.live_row = []
        self._index = {}

    def add(self, cids, ts, oi, request_dates, file_id, row_index, expirations):
        np = _np()
        if len(cids) == 0:
            return
        cids = np.asarray(cids, dtype=np.int32)
        ts = np.asarray(ts, dtype=np.int64)
        oi = np.asarray(oi, dtype=np.int64)
        fid = np.asarray(file_id, dtype=np.int64)
        rid = np.asarray(row_index, dtype=np.int64)
        req = np.asarray(request_dates, dtype=object)
        exp = np.asarray(expirations, dtype=object)
        self.p_cid = np.concatenate((self.p_cid, cids))
        self.p_ts = np.concatenate((self.p_ts, ts))
        self.p_oi = np.concatenate((self.p_oi, oi))
        self.p_req = np.concatenate((self.p_req, req))
        self.p_fid = np.concatenate((self.p_fid, fid))
        self.p_row = np.concatenate((self.p_row, rid))
        self.p_exp = np.concatenate((self.p_exp, exp))
        for label in np.unique(req):
            if label is not None and label not in self.midnight_cache:
                self.midnight_cache[label] = cut_ns_on(label, "00:00")

    def _availability(self, ts, req):
        np = _np()
        uniq, inverse = np.unique(np.asarray(req, dtype=object), return_inverse=True)
        mids = np.empty(len(uniq), dtype=np.int64)
        for i, label in enumerate(uniq):
            hit = self.midnight_cache.get(label)
            if hit is None:
                hit = cut_ns_on(label, "00:00")
                self.midnight_cache[label] = hit
            mids[i] = int(hit)
        return np.maximum(np.asarray(ts, dtype=np.int64), mids[inverse])

    def _live_get(self, cid):
        idx = self._index.get(int(cid))
        if idx is None:
            return None
        return {
            "oi": None if not self.live_oi_ok[idx] else int(self.live_oi[idx]),
            "ts": int(self.live_ts[idx]),
            "request_date": self.live_req[idx],
            "ambiguous": bool(self.live_amb[idx]),
            "expiration": self.live_exp[idx],
            "valid_from_ns": int(self.live_from[idx]),
            "file_id": int(self.live_fid[idx]),
            "row_index": int(self.live_row[idx]),
        }

    def _close_row(self, cid, valid_to):
        prev = self._live_get(cid)
        if prev is None:
            return None
        return {
            "contract_id": int(cid), "chain": self.chain,
            "open_interest": prev["oi"], "ts_event_ns": prev["ts"],
            "request_date": prev["request_date"], "file_id": prev["file_id"],
            "row_index": prev["row_index"], "ambiguous": prev["ambiguous"],
            "valid_from_ns": prev["valid_from_ns"], "valid_to_ns": int(valid_to),
            "expiration": prev["expiration"], "causal_feature_eligible": False,
        }

    def _upsert_live(self, cid, oi, oi_ok, ts, req, amb, exp, valid_from, fid, row):
        cid = int(cid)
        idx = self._index.get(cid)
        if idx is None:
            self._index[cid] = len(self.live_cid)
            self.live_cid.append(cid)
            self.live_oi.append(0 if oi is None else int(oi))
            self.live_oi_ok.append(bool(oi_ok))
            self.live_ts.append(int(ts))
            self.live_req.append(req)
            self.live_amb.append(bool(amb))
            self.live_exp.append(exp)
            self.live_from.append(int(valid_from))
            self.live_fid.append(int(fid))
            self.live_row.append(int(row))
            return
        self.live_oi[idx] = 0 if oi is None else int(oi)
        self.live_oi_ok[idx] = bool(oi_ok)
        self.live_ts[idx] = int(ts)
        self.live_req[idx] = req
        self.live_amb[idx] = bool(amb)
        self.live_exp[idx] = exp
        self.live_from[idx] = int(valid_from)
        self.live_fid[idx] = int(fid)
        self.live_row[idx] = int(row)

    def _drop_live(self, cid):
        idx = self._index.pop(int(cid), None)
        if idx is None:
            return
        last = len(self.live_cid) - 1
        if idx != last:
            moved = int(self.live_cid[last])
            self.live_cid[idx] = self.live_cid[last]
            self.live_oi[idx] = self.live_oi[last]
            self.live_oi_ok[idx] = self.live_oi_ok[last]
            self.live_ts[idx] = self.live_ts[last]
            self.live_req[idx] = self.live_req[last]
            self.live_amb[idx] = self.live_amb[last]
            self.live_exp[idx] = self.live_exp[last]
            self.live_from[idx] = self.live_from[last]
            self.live_fid[idx] = self.live_fid[last]
            self.live_row[idx] = self.live_row[last]
            self._index[moved] = idx
        self.live_cid.pop()
        self.live_oi.pop()
        self.live_oi_ok.pop()
        self.live_ts.pop()
        self.live_req.pop()
        self.live_amb.pop()
        self.live_exp.pop()
        self.live_from.pop()
        self.live_fid.pop()
        self.live_row.pop()

    def apply_through(self, cut_ns, cut_date):
        np = _np()
        if len(self.p_cid) == 0:
            return None
        req_u, req_inv = np.unique(self.p_req, return_inverse=True)
        req_ok = np.array([label <= cut_date for label in req_u], dtype=bool)
        eligible = (self.p_ts <= int(cut_ns)) & req_ok[req_inv]
        applied_idx = np.nonzero(eligible)[0]
        still = np.nonzero(~eligible)[0]
        if len(applied_idx) == 0:
            return None
        cid = self.p_cid[applied_idx]
        ts = self.p_ts[applied_idx]
        oi = self.p_oi[applied_idx]
        req = self.p_req[applied_idx]
        fid = self.p_fid[applied_idx]
        rid = self.p_row[applied_idx]
        exp = self.p_exp[applied_idx]
        avail = self._availability(ts, req)
        order = np.lexsort((rid, fid, req, ts, cid, avail))
        cid, ts, oi, req, fid, rid, exp, avail = (
            cid[order], ts[order], oi[order], req[order], fid[order], rid[order], exp[order], avail[order])
        same = (cid[1:] == cid[:-1]) & (ts[1:] == ts[:-1]) & (avail[1:] == avail[:-1])
        starts = np.concatenate((np.array([0], dtype=np.int64), np.nonzero(~same)[0].astype(np.int64) + 1))
        closed_rows = []
        for s, start in enumerate(starts):
            end = starts[s + 1] if s + 1 < len(starts) else len(cid)
            g_cid = int(cid[start])
            g_ts = int(ts[start])
            start_at = int(avail[start])
            g_oi = oi[start:end]
            g_req = req[start:end]
            g_fid = fid[start:end]
            g_rid = rid[start:end]
            g_exp = exp[start:end]
            prev = self._live_get(g_cid)
            if prev is not None and g_ts < prev["ts"]:
                continue
            pick = int(np.lexsort((g_rid, g_fid, g_req))[0])
            ambiguous = bool(g_oi.min() != g_oi.max())
            values = set(int(v) for v in g_oi)
            if prev is not None and g_ts == prev["ts"]:
                ambiguous = ambiguous or prev["ambiguous"] or (prev["oi"] not in values)
                if not ambiguous:
                    continue
            if prev is not None:
                start_at = max(start_at, prev["valid_from_ns"])
                closed_rows.append(self._close_row(g_cid, start_at))
                self._drop_live(g_cid)
            self._upsert_live(
                g_cid,
                None if ambiguous else int(g_oi[pick]),
                not ambiguous,
                g_ts, g_req[pick], ambiguous, g_exp[pick], start_at,
                int(g_fid[pick]), int(g_rid[pick]),
            )
        self.p_cid = self.p_cid[still]
        self.p_ts = self.p_ts[still]
        self.p_oi = self.p_oi[still]
        self.p_req = self.p_req[still]
        self.p_fid = self.p_fid[still]
        self.p_row = self.p_row[still]
        self.p_exp = self.p_exp[still]
        return _interval_table(closed_rows)

    def purge_expired(self, cut_date, cut_midnight_ns):
        closed_rows = []
        for cid in list(self._index):
            state = self._live_get(cid)
            exp = state["expiration"]
            if exp is not None and exp < cut_date:
                closed_rows.append(self._close_row(cid, cut_midnight_ns))
                self._drop_live(cid)
        return _interval_table(closed_rows)

    def open_table(self):
        rows = []
        for cid in self._index:
            prev = self._live_get(cid)
            rows.append({
                "contract_id": int(cid), "chain": self.chain,
                "open_interest": prev["oi"], "ts_event_ns": prev["ts"],
                "request_date": prev["request_date"], "file_id": prev["file_id"],
                "row_index": prev["row_index"], "ambiguous": prev["ambiguous"],
                "valid_from_ns": prev["valid_from_ns"], "valid_to_ns": None,
                "expiration": prev["expiration"], "causal_feature_eligible": False,
            })
        return _interval_table(rows)

    def snapshot_counts(self, cut_ns, cut_date, listing_ids, prev_cash):
        np = _np()
        expired = available = ambiguous = stale = prior_held = 0
        live_ids = []
        for cid, idx in self._index.items():
            exp = self.live_exp[idx]
            if exp is not None and exp < cut_date:
                expired += 1
                continue
            live_ids.append(int(cid))
            if self.live_amb[idx]:
                ambiguous += 1
                continue
            if not self.live_oi_ok[idx]:
                continue
            available += 1
            req = self.live_req[idx]
            if req < cut_date:
                prior_held += 1
            if prev_cash and req < prev_cash:
                stale += 1
        listing = np.unique(np.asarray(listing_ids, dtype=np.int32)) if len(listing_ids) else np.empty(0, dtype=np.int32)
        live_arr = np.unique(np.asarray(live_ids, dtype=np.int32)) if live_ids else np.empty(0, dtype=np.int32)
        listing_only = int(len(np.setdiff1d(listing, live_arr, assume_unique=True))) if len(listing) else 0
        if len(self.p_cid):
            future_mask = (self.p_req == cut_date) & (self.p_ts > int(cut_ns))
            future_today = np.unique(self.p_cid[future_mask]) if np.any(future_mask) else np.empty(0, dtype=np.int32)
        else:
            future_today = np.empty(0, dtype=np.int32)
        universe = np.unique(np.concatenate((live_arr, listing, future_today)))
        n_universe = int(len(universe))
        return {
            "universe": n_universe, "available": available, "ambiguous": ambiguous,
            "stale": stale, "prior_held": prior_held, "future_today": int(len(future_today)),
            "not_available": n_universe - available, "expired": expired,
            "listing_only": listing_only,
            "available_fraction": None if n_universe == 0 else available / n_universe,
        }


def _interval_table(rows):
    pa = _pa()
    if not rows:
        return None
    n = len(rows)
    return pa.table({
        "contract_id": pa.array([row["contract_id"] for row in rows], type=pa.int32()),
        "chain": pa.array([row["chain"] for row in rows], type=pa.string()),
        "open_interest": pa.array([row["open_interest"] for row in rows], type=pa.int64()),
        "ts_event_ns": pa.array([row["ts_event_ns"] for row in rows], type=pa.int64()),
        "request_date": pa.array([row["request_date"] for row in rows], type=pa.string()),
        "file_id": pa.array([row["file_id"] for row in rows], type=pa.int64()),
        "row_index": pa.array([row["row_index"] for row in rows], type=pa.int64()),
        "ambiguous": pa.array([row["ambiguous"] for row in rows], type=pa.bool_()),
        "valid_from_ns": pa.array([row["valid_from_ns"] for row in rows], type=pa.int64()),
        "valid_to_ns": pa.array([row["valid_to_ns"] for row in rows], type=pa.int64()),
        "expiration": pa.array([row["expiration"] for row in rows], type=pa.string()),
        "causal_feature_eligible": pa.array([False] * n, type=pa.bool_()),
    }, schema=interval_schema())


def coverage_table(rows):
    pa = _pa()
    if not rows:
        return coverage_schema().empty_table()
    names = [field.name for field in coverage_schema()]
    return pa.table({name: [row.get(name) for name in names] for name in names}, schema=coverage_schema())


def asof_aggregate_table(chain, label, cut_label, cut_at, counts):
    pa = _pa()
    return pa.table({
        "chain": pa.array([chain], type=pa.string()),
        "cut_date": pa.array([label], type=pa.string()),
        "cut_label": pa.array([cut_label], type=pa.string()),
        "cut_ns": pa.array([int(cut_at)], type=pa.int64()),
        "universe": pa.array([counts["universe"]], type=pa.int64()),
        "available": pa.array([counts["available"]], type=pa.int64()),
        "ambiguous": pa.array([counts["ambiguous"]], type=pa.int64()),
        "stale": pa.array([counts["stale"]], type=pa.int64()),
        "prior_held": pa.array([counts["prior_held"]], type=pa.int64()),
        "future_today": pa.array([counts["future_today"]], type=pa.int64()),
        "not_available": pa.array([counts["not_available"]], type=pa.int64()),
        "expired": pa.array([counts["expired"]], type=pa.int64()),
        "listing_only": pa.array([counts["listing_only"]], type=pa.int64()),
        "available_fraction": pa.array([counts["available_fraction"]], type=pa.float64()),
        "causal_feature_eligible": pa.array([False], type=pa.bool_()),
    }, schema=asof_aggregate_schema())


def _assign_report_ids(reports, next_id):
    np = _np()
    n = len(reports["contract_id"])
    ids = np.arange(next_id, next_id + n, dtype=np.int64)
    reports["report_id"] = ids
    return next_id + n


def _listed_flags(report_cids, listing_ids):
    np = _np()
    n = len(report_cids)
    if n == 0:
        return np.empty(0, dtype=bool)
    if len(listing_ids) == 0:
        return np.zeros(n, dtype=bool)
    _, listed = _lookup_sorted(np.unique(np.asarray(listing_ids, dtype=np.int32)), report_cids)
    return listed


def _concat_parsed(parts, role):
    np = _np()
    if not parts:
        return None
    keys = parts[0].keys()
    out = {}
    for key in keys:
        arrays = [part[key] for part in parts if len(part[key])]
        if not arrays:
            out[key] = parts[0][key]
        else:
            out[key] = np.concatenate(arrays)
    return out


def run_columnar(*, protocol: dict, admitted: dict, outputs: BoundedOutputs,
                 selected_dates: list[str] | None = None) -> dict:
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError("registered BoundedOutputs required")
    started_wall, started_cpu = pytime.perf_counter(), pytime.process_time()
    spec = contract(protocol)
    calendar, calendar_ref = load_calendar(protocol)
    population, stages = spec["population"], spec["population"]["stages"]
    chains, cuts = tuple(population["chains"]), tuple(spec["clocks"]["asof_cuts_local"])
    intended_all = intended_cash_dates(calendar, population["first_date"], population["last_date"])
    intended_labels, prev_map = build_calendar_index(intended_all)
    intended_label_set = set(intended_labels)
    if selected_dates is not None:
        if type(selected_dates) is not list or any(type(item) is not str for item in selected_dates):
            raise ContractError("selected_dates must be ISO date strings or None")
        if len(set(selected_dates)) != len(selected_dates):
            raise ContractError("selected_dates contains duplicates")
    sources, required_ids = _validate_admitted(admitted, protocol, selected_dates)
    schemas = admitted.get("schemas")
    if not isinstance(schemas, dict):
        raise ContractError("admitted schemas mapping required")
    selected_set = None if selected_dates is None else set(selected_dates)
    by_chain = {chain: defaultdict(lambda: defaultdict(list)) for chain in chains}
    acquired_dates = {chain: set() for chain in chains}
    for record in sources:
        source = record["source"]
        if selected_set is not None and source["request_date"] not in selected_set:
            continue
        by_chain[source["chain"]][source["request_date"]][source["role"]].append(record)
        acquired_dates[source["chain"]].add(source["request_date"])
    selected_or_all = intended_all if selected_dates is None else tuple(date.fromisoformat(d) for d in selected_dates)
    work_dates = {}
    for chain in chains:
        extra = acquired_dates[chain] - {d.isoformat() for d in selected_or_all}
        work_dates[chain] = tuple(sorted({*selected_or_all, *(date.fromisoformat(d) for d in extra)}))

    identity_w = ArrayWriter(outputs, "identity", identity_schema(), OUTPUT_SCHEMAS["identity_map"])
    except_w = ArrayWriter(outputs, "exceptions", exception_schema(), OUTPUT_SCHEMAS["exceptions"])
    member_w = ArrayWriter(outputs, "membership", membership_schema(), OUTPUT_SCHEMAS["membership"])
    report_w = ArrayWriter(outputs, "reports",
                           _with_storage_meta(compact_report_schema(), LOGICAL_REPORT_KIND, COMPACT_REPORT_KIND),
                           COMPACT_REPORT_KIND)
    life_w = ArrayWriter(outputs, "lifecycle",
                         _with_storage_meta(compact_lifecycle_schema(), LOGICAL_LIFECYCLE_KIND, COMPACT_LIFECYCLE_KIND),
                         COMPACT_LIFECYCLE_KIND)
    interval_w = ArrayWriter(outputs, "asof-intervals", interval_schema(), OUTPUT_SCHEMAS["asof_intervals"])
    asof_agg_w = ArrayWriter(outputs, "asof-aggregates", asof_aggregate_schema(), OUTPUT_SCHEMAS["asof_aggregates"])

    coverage_rows, date_aggregates, consumed, manifest = [], [], set(), []
    files_read = rows_read = bytes_read = 0
    source_dates, midnight_cache, cut_ns_cache = [], {}, {}
    dates, clocks = DateCodebook(), ClockMaps()
    identities = ChainIdentity()
    next_report_id = 0
    research_cut = local_timestamp(date(2026, 9, 4), time(0), calendar.zone)
    listing_unknown_chains = sorted(CHAINS_WITHOUT_LISTING)
    np = _np()

    for chain in chains:
        asof = TypedAsof(chain, dates, midnight_cache)
        intended_work = set(selected_dates or intended_labels)
        last_selected = max(intended_work) if intended_work else None
        first_selected = min(intended_work) if intended_work else None
        prev_reports, prev_listings, prev_intended_date = None, np.empty(0, dtype=np.int32), None
        listing_known = chain not in CHAINS_WITHOUT_LISTING
        for day in work_dates[chain]:
            label = day.isoformat()
            intended = label in intended_label_set and (selected_set is None or label in selected_set)
            closed = calendar.resolve(day, cut=research_cut).state == "closed"
            primary = intended and population["first_date"] <= label <= population["last_date"]
            files = by_chain[chain].get(label, {})
            listing_parts, oi_parts = [], []
            listing_ids = np.empty(0, dtype=np.int32)
            mismatch_n = future_n = late_n = missing_clock_n = map_agree_n = map_n = 0
            listing_present, oi_present = "contracts" in files, "open_interest" in files
            empty_listing = empty_oi = False
            exception_n = 0
            for role in ("contracts", "open_interest"):
                for record in files.get(role, []):
                    schema_str = schemas.get(record["schema_id"])
                    table, meta = read_admitted_source(protocol, record)
                    if meta["empty_marker"]:
                        schema_str = str(table.schema)
                    elif type(schema_str) is not str:
                        raise IntegrityError("admitted schema_id is not in schemas")
                    if record.get("rows") is not None and meta["rows"] != record["rows"] and not meta["empty_marker"]:
                        raise IntegrityError("admitted row count does not match the decoded table")
                    consumed.add(record["file_id"])
                    files_read += 1
                    rows_read += meta["rows"]
                    bytes_read += meta["size_bytes"]
                    source_dates.append(label)
                    parsed, exc, n_read, n_valid = parse_source_typed(
                        table, record=record, schema_str=schema_str,
                        prev_map=prev_map, midnight_cache=midnight_cache,
                        dates=dates, clocks=clocks,
                    )
                    missing_clock_n += int(np.sum(exc["invalid_reason"] == "missing_clock")) if len(exc["file_id"]) else 0
                    except_table = exceptions_to_table(exc)
                    if except_table is not None:
                        except_w.write_table(except_table)
                        exception_n += len(except_table)
                    member_w.write_table(membership_table(
                        record["file_id"], record["source"]["path"], record["sha256"], chain, role, label,
                        n_read, n_valid, len(exc["file_id"]), meta["empty_marker"],
                    ))
                    manifest.append({
                        "file_id": record["file_id"], "path": record["source"]["path"],
                        "sha256": record["sha256"], "size_bytes": meta["size_bytes"],
                    })
                    if meta["empty_marker"] and role == "contracts":
                        empty_listing = True
                    elif meta["empty_marker"]:
                        empty_oi = True
                    if len(parsed["osi"]) == 0:
                        continue
                    cids = identities.intern(
                        chain, parsed["osi"], parsed["expiration"], parsed["millistrike"],
                        parsed["right"], dates)
                    if role == "contracts":
                        listing_ids = np.concatenate((listing_ids, cids.astype(np.int32, copy=False)))
                        continue
                    parsed = dict(parsed)
                    parsed["contract_id"] = cids.astype(np.int32, copy=False)
                    oi_parts.append(parsed)
                    mismatch_n += int(parsed["mismatch"].sum())
                    future_n += int(parsed["future"].sum())
                    late_n += int(parsed["late"].sum())
                    map_n += int(len(parsed["map_agree"]))
                    map_agree_n += int(parsed["map_agree"].sum())
            ident_table = identities.flush_tables(chain)
            if ident_table is not None:
                identity_w.write_table(ident_table)
            oi = _concat_parsed(oi_parts, "open_interest")
            if oi is None:
                resolved = resolve_reports_typed([], [], [], [], [])
            else:
                resolved = resolve_reports_typed(
                    oi["contract_id"], oi["ts_event_ns"], oi["open_interest"], oi["file_id"], oi["row_index"])
            next_report_id = _assign_report_ids(resolved, next_report_id)
            meta_dte = _last_per_cid(oi["contract_id"], oi["dte"]) if oi is not None else {}
            meta_bucket = _last_per_cid(oi["contract_id"], oi["dte_bucket"]) if oi is not None else {}
            meta_right = _last_per_cid(oi["contract_id"], oi["right"]) if oi is not None else {}
            dte_col = [meta_dte.get(int(cid)) for cid in resolved["contract_id"]]
            bucket_col = [meta_bucket.get(int(cid)) for cid in resolved["contract_id"]]
            right_col = [meta_right.get(int(cid)) for cid in resolved["contract_id"]]
            listed = _listed_flags(resolved["contract_id"], listing_ids)
            report_table = reports_to_table(
                resolved, chain=chain, label=label, listed=listed,
                dte=dte_col, bucket=bucket_col, right=right_col, report_ids=resolved["report_id"],
            )
            if report_table is not None:
                report_w.write_table(report_table)
            oi_keys = set(int(cid) for cid in resolved["contract_id"])
            listed_set = set(int(cid) for cid in listing_ids)
            if not listing_known:
                listing_status, listing_count, denom_known = "unknown", None, False
                inter = union = listed_wo = oi_wo = coverage = None
            elif empty_listing:
                listing_status, listing_count, denom_known = "empty_marker", None, False
                inter = union = listed_wo = oi_wo = coverage = None
            elif not listing_present:
                listing_status, listing_count, denom_known = "absent", None, False
                inter = union = listed_wo = oi_wo = coverage = None
            else:
                listing_status, listing_count, denom_known = "present", len(listed_set), True
                inter, union = len(listed_set & oi_keys), len(listed_set | oi_keys)
                listed_wo, oi_wo = len(listed_set - oi_keys), len(oi_keys - listed_set)
                coverage = None if listing_count == 0 else inter / listing_count
            if empty_oi:
                oi_status, oi_count = "empty_marker", None
            elif not oi_present:
                oi_status, oi_count = "absent_file", None
            elif not oi_keys:
                oi_status, oi_count = "unknown_no_rows", None
            else:
                oi_status, oi_count = "present", len(oi_keys)
            zeros = int(((resolved["has_point"] & ((resolved["first_oi"] == 0) | (resolved["last_oi"] == 0))).sum()))
            gt60 = sum(1 for dte in meta_dte.values() if dte is not None and dte > 60)
            agg = _empty_date(chain, label, intended, closed, primary)
            usable_n = int(resolved["usable"].sum())
            conflict_n = int(resolved["same_time_conflict"].sum())
            update_n = int(resolved["update_candidate"].sum())
            update_diff = int(resolved["observed_update_difference"][resolved["update_candidate"]].sum()) if update_n else 0
            agg.update({
                "listing_count": listing_count, "oi_count": oi_count, "oi_zero_count": zeros,
                "intersection_count": inter, "union_count": union, "listed_without_oi": listed_wo,
                "oi_without_listing": oi_wo, "listing_denominator_known": denom_known,
                "coverage_listed_with_oi": coverage, "invalid_row_count": exception_n,
                "missing_clock_count": missing_clock_n, "event_local_mismatch_count": mismatch_n,
                "future_flag_count": future_n, "late_flag_count": late_n,
                "usable_report_count": usable_n, "conflict_report_count": conflict_n,
                "update_candidate_count": update_n, "update_diff_sum": update_diff,
                "update_n": update_n, "gt60_dte_retained": gt60,
                "position_mapping_agree_count": map_agree_n, "position_mapping_count": map_n,
            })
            coverage_rows.append({
                "chain": chain, "request_date": label, "intended": intended, "closed": closed,
                "primary": primary, "listing_file_present": listing_present,
                "oi_file_present": oi_present,
                "both_files_absent": not listing_present and not oi_present,
                "listing_status": listing_status, "oi_status": oi_status,
                "listing_count": listing_count, "oi_count": oi_count, "oi_zero_count": zeros,
                "intersection_count": inter, "union_count": union, "listed_without_oi": listed_wo,
                "oi_without_listing": oi_wo, "listing_denominator_known": denom_known,
                "coverage_listed_with_oi": coverage, "invalid_row_count": exception_n,
                "missing_clock_count": missing_clock_n, "event_local_mismatch_count": mismatch_n,
                "future_flag_count": future_n, "late_flag_count": late_n,
                "usable_report_count": usable_n, "conflict_report_count": conflict_n,
                "update_candidate_count": update_n, "gt60_dte_retained": gt60,
                "vix_listing_unknown": not listing_known,
                "position_mapping_agree_count": map_agree_n, "position_mapping_count": map_n,
            })
            if oi is not None:
                asof.add(oi["contract_id"], oi["ts_event_ns"], oi["open_interest"],
                         oi["request_date"], oi["file_id"], oi["row_index"], oi["expiration"])
            if intended:
                prev_cash = prev_map.get(label)
                midnight = midnight_cache.get(label)
                if midnight is None:
                    midnight = local_timestamp(day, time(0), ZONE)
                    midnight_cache[label] = midnight
                for cut_label in cuts:
                    key = (label, cut_label)
                    cut_at = cut_ns_cache.get(key)
                    if cut_at is None:
                        cut_at = cut_ns_on(day, cut_label)
                        cut_ns_cache[key] = cut_at
                    closed_intervals = asof.apply_through(cut_at, label)
                    if closed_intervals is not None:
                        interval_w.write_table(closed_intervals)
                    purged = asof.purge_expired(label, midnight)
                    if purged is not None:
                        interval_w.write_table(purged)
                    counts = asof.snapshot_counts(cut_at, label, listing_ids, prev_cash)
                    agg["asof"][cut_label] = counts
                    asof_agg_w.write_table(asof_aggregate_table(chain, label, cut_label, cut_at, counts))
            life_chunks = []
            if intended:
                next_stage = stage_of(label, stages)
                if prev_intended_date is not None:
                    prior_stage = stage_of(prev_intended_date, stages)
                    life_chunks.append((prev_reports, resolved, prev_listings, listing_ids,
                                        prev_intended_date, label, prior_stage, next_stage))
                else:
                    life_chunks.append((None, resolved, np.empty(0, dtype=np.int32), listing_ids,
                                        None, label, None, next_stage))
                if last_selected == label:
                    prior_stage = stage_of(label, stages)
                    life_chunks.append((resolved, None, listing_ids, np.empty(0, dtype=np.int32),
                                        label, None, prior_stage, None))
            for prev_b, curr_b, prev_l, curr_l, pdate, ndate, pstage, nstage in life_chunks:
                life = join_lifecycle_typed(
                    prev_b, curr_b, prev_l, curr_l, chain=chain, prior_date=pdate, next_date=ndate,
                    last_selected=last_selected, first_selected=first_selected,
                    prior_stage=pstage, next_stage=nstage, listing_known=listing_known,
                    identities=identities, dates=dates,
                )
                tally_lifecycle(agg, life, pdate, ndate, pstage, nstage)
                life_table = lifecycle_to_table(life, chain=chain, prior_date=pdate, next_date=ndate,
                                                prior_stage=pstage, next_stage=nstage)
                if life_table is not None:
                    life_w.write_table(life_table)
            if len(resolved["contract_id"]):
                first_secs, first_ok = clocks.seconds_after(resolved["first_ts"], clocks.eastern_labels(resolved["first_ts"]), midnight_cache)
                last_secs, last_ok = clocks.seconds_after(resolved["last_ts"], clocks.eastern_labels(resolved["last_ts"]), midnight_cache)
                first_ok &= resolved["has_point"]
                last_ok &= resolved["has_point"]
                finish_day_policies_typed(agg, resolved, first_secs, first_ok, last_secs, last_ok, right_col, bucket_col)
            if intended:
                prev_reports = resolved
                prev_listings = np.unique(listing_ids.astype(np.int32, copy=False)) if len(listing_ids) else np.empty(0, dtype=np.int32)
                prev_intended_date = label
            date_aggregates.append(agg)
        flushed = asof.apply_through(_MAX_NS, "9999-12-31")
        if flushed is not None:
            interval_w.write_table(flushed)
        opened = asof.open_table()
        if opened is not None:
            interval_w.write_table(opened)
        identities.release_keys()

    reconstruction_payload = {
        "kind": OUTPUT_SCHEMAS["reconstruction"],
        "predicate": INTERVAL_RECONSTRUCTION,
        "output_schemas": OUTPUT_SCHEMAS,
        "identity_map": "contract_id -> chain, osi_symbol, expiration, millistrike, right",
        "valid_rows": "authenticated original /workspace/data files via membership file_id+row_index",
        "storage": {
            "reports": {
                "physical_kind": COMPACT_REPORT_KIND,
                "logical_kind": LOGICAL_REPORT_KIND,
                "layout": "typed_columns_plus_last_eq_first_mask_and_stable_report_id",
                "reconstruct": "trading_research.research.options_oi_columnar.iter_logical_reports",
            },
            "lifecycle": {
                "physical_kind": COMPACT_LIFECYCLE_KIND,
                "logical_kind": LOGICAL_LIFECYCLE_KIND,
                "layout": "prior_report_id/next_report_id plus censor/eligible/delta flags; endpoints from report ledger",
                "reconstruct": "trading_research.research.options_oi_columnar.iter_logical_lifecycle",
                "join": "prior_report_id/next_report_id -> reports.report_id",
            },
            "logical_value_fields": {
                "reports": [field.name for field in report_schema()],
                "lifecycle": [field.name for field in lifecycle_schema()],
                "asof_intervals": [field.name for field in interval_schema()],
            },
            "timing": (
                "valid_from_ns = max(ts_event_ns, request_midnight); "
                "source-clock eligibility requires ts_event_ns <= cut_ns and request_date <= cut_date; "
                "older reobserved clocks never replace a newer live state; "
                "same-clock conflict on a later request invalidates from request midnight; "
                "aliases with the same value do not reset a prior held clock; "
                "pending future rows after the last selected cut are flushed with valid_from in the future; "
                "timestamps are int64 nanoseconds."
            ),
        },
    }
    return finish_measurement_outputs(
        outputs, spec=spec, calendar_ref=calendar_ref, identity_w=identity_w,
        except_w=except_w, member_w=member_w, report_w=report_w, life_w=life_w,
        interval_w=interval_w, asof_agg_w=asof_agg_w,
        coverage_table=coverage_table(coverage_rows),
        coverage_kind=OUTPUT_SCHEMAS["coverage"], date_aggregates=date_aggregates,
        consumed=consumed, required_ids=required_ids, manifest=manifest,
        files_read=files_read, rows_read=rows_read, bytes_read=bytes_read,
        source_dates=source_dates, selected_dates=selected_dates,
        intended_all=intended_all, intended_labels=intended_labels, chains=chains,
        listing_unknown_chains=listing_unknown_chains, started_cpu=started_cpu,
        started_wall=started_wall, reconstruction_payload=reconstruction_payload,
        family=FAMILY, version=VERSION, remaining=REMAINING,
        interval_reconstruction=INTERVAL_RECONSTRUCTION,
        max_worker_bytes=MAX_WORKER_BYTES, max_source_file=MAX_SOURCE_FILE,
    )


__all__ = [
    "COMPACT_LIFECYCLE_KIND", "COMPACT_REPORT_KIND", "ArrayWriter", "ChainIdentity",
    "TypedAsof", "compact_lifecycle_schema", "compact_report_schema",
    "iter_logical_lifecycle", "iter_logical_reports", "join_lifecycle_typed",
    "parse_source_typed", "read_logical_parts", "resolve_reports_typed", "run_columnar",
]
