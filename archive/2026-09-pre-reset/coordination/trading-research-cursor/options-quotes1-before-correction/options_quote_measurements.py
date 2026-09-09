"""Acquired options quote-quality, coverage and underlier/rate/action support.

Quote quality only. Missing, invalid and conflicting quotes are never treated
as prices. Source-clock sampling is exact; received/published/known and last
actual NBBO update stay NULL. Causal features are not eligible.

Valid quotation rows stay in the authenticated original files
(file_id+row_index). Cut boards store the observed as-of payload and run
evidence. Arbitrary minute history is reconstructed from those files plus the
sort/dedup rule; this module does not copy an interval tape of every quote
change.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import hashlib
import json
import math
import time as pytime

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.time import datetime_ns
from trading_research.operations.artifacts import ArtifactStore, canonical_json, digest, file_digest
from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact
from trading_research.research.options_oi_columnar import (
    ArrayWriter, ClockMaps, DateCodebook, _date_column_iso, _dictionary_keys,
    _millistrike_column, _osi_unique_parse, _unique_string_map,
)
from trading_research.research.options_oi_measurements import (
    CHAINS_WITHOUT_LISTING, RIGHTS, ZONE, _check_schema, _resolve_source_path,
    _schema_fields, _type_ok, build_calendar_index, cut_ns_on, dte_days,
    identity_schema, intended_cash_dates, millistrike, normalize_right,
    parse_osi, previous_intended, reconstruct_asof_intervals, stage_of,
    timestamp_ns_from_arrow,
)
from trading_research.research.options_quote_statistics import finish_quote_outputs


VERSION = "options-quote-quality-support-measurement-v1"
FAMILY = "Research-Options-Quote-Quality-Support-acquired-v1"
ADMITTED_KIND = "options_quote_admitted_sources_v1"
CONTRACT_KIND = "options_quote_quality_support_contract_v1"
DEFAULT_DATA_ROOT = "/workspace/data"
MAX_SOURCE_FILE = 128 * 1024 * 1024
MAX_WORKER_BYTES = 8 * 1024 ** 3
STREAM_ROWS = 65536
NS = 1_000_000_000
MINUTE_NS = 60 * NS
GAP_BREAK_NS = 60 * NS
STALE_THRESHOLDS = (60, 300, 900)
QUOTE_FAMILIES = ("near", "broad", "vix_full")
SUPPORT_FAMILIES = ("cash_daily", "etf_1m", "fred", "corporate_actions")
QUOTE_ROLES = frozenset({"quote", "quotes", "quote_1m"})
SUPPORT_ROLES = frozenset({
    "underlier_daily", "cash_daily", "underlier_minute", "etf_1m",
    "rates", "fred", "corporate_actions", "actions",
})
BASE_CLASSES = (
    "invalid_identity", "invalid_clock", "invalid_numeric", "conflict",
    "all_zero", "one_sided", "crossed", "locked", "two_sided",
)
QUALITY_FLAGS = (
    "condition_zero", "nonpositive_size", "negative_size", "zero_bid", "zero_ask",
    "negative_price", "nonfinite_price", "session_outside", "request_date_mismatch",
)
DTE_BUCKETS = ("expired", "0", "1", "2-7", "8-14", "15-30", "31-60", "61+")
LOCAL_CUTS = ("09:30", "10:00", "15:00", "cash_close")
UTC_CUTS = ("15:00_utc",)
ALL_CUTS = LOCAL_CUTS + UTC_CUTS
PAYLOAD_INT_FIELDS = ("bid_size", "ask_size", "bid_exchange", "ask_exchange",
                      "bid_condition", "ask_condition")
QUOTE_REQUIRED = (
    "symbol", "expiration", "strike", "right", "bid_size", "ask_size",
    "bid_exchange", "ask_exchange", "bid_condition", "ask_condition",
    "bid", "ask", "request_date", "ts_event", "osi_symbol",
)
REMAINING = (
    "iv_greeks_and_surfaces_remain_separate",
    "trade_signing_exposure_and_holdings_remain_separate",
    "vix_implied_surface_and_futures_options_remain_separate",
    "no_actual_receipt_or_last_nbbo_update_clock",
    "no_intraday_cash_ndx_spx_vix_in_this_block",
    "no_historical_rate_pit_vintage",
    "no_context_fit",
)
INTERVAL_RECONSTRUCTION = (
    "A quotation row is visible at retrospective sourceclock cut_ns on cut_date "
    "iff ts_event_ns <= cut_ns and request_date <= cut_date and the eastern "
    "session date of ts_event_ns equals cut_date (no prior-session carry, no "
    "future quote). The newest eligible identity+time is the as-of state. A "
    "current conflict or invalid_identity/clock/numeric row suppresses any "
    "older valid quote; there is no fallback search. Alias: same identity+time "
    "and identical bid/ask/size/exchange/condition is one event with "
    "multiplicity. Conflict: same identity+time and any payload difference has "
    "no winner. Source-family populations are deduplicated before union. "
    "sample_age_ns = cut_ns - latest sampled ts_event_ns. "
    "unchanged_payload_age_ns = cut_ns - first observed ts_event_ns of the "
    "current identical 8-field payload run. A gap > 60s, invalid row or "
    "conflict breaks the run. received_at/published_at/known_at/"
    "last_actual_update stay NULL; causal_feature_eligible is false; "
    "actual update age is unknown. Original files plus this sort/dedup rule "
    "reconstruct any sampled minute; this module does not store every quote "
    "change."
)
OUTPUT_SCHEMAS = {
    "admission": "options_quote_file_admission_v1",
    "exceptions": "options_quote_exceptions_v1",
    "alias_conflict": "options_quote_alias_conflict_v1",
    "cut_board": "options_quote_cut_board_v1",
    "source_quality": "options_quote_source_quality_v1",
    "coverage": "options_quote_coverage_v1",
    "underlier_support": "options_quote_underlier_support_v1",
    "date_aggregates": "options_quote_date_aggregates_v1",
    "reconstruction": "options_quote_reconstruction_v1",
    "identity_match": "options_quote_identity_match_v1",
}


def _pa():
    import pyarrow as pa
    return pa


def _pc():
    import pyarrow.compute as pc
    return pc


def _np():
    import numpy as np
    return np


def contract(protocol):
    if not isinstance(protocol, dict):
        raise ContractError("protocol mapping required")
    if protocol.get("kind") == CONTRACT_KIND:
        return protocol
    inner = protocol.get("contract")
    if isinstance(inner, dict) and inner.get("kind") == CONTRACT_KIND:
        return inner
    raise ContractError("options quote quality/support contract required")


def load_calendar(protocol):
    spec = contract(protocol)["cash_calendar"]
    path = Path(spec["path"])
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if spec.get("sha256") and sha != spec["sha256"]:
        raise IntegrityError("cash calendar bytes changed")
    if spec.get("size_bytes") is not None and len(raw) != spec["size_bytes"]:
        raise IntegrityError("cash calendar size changed")
    return CashCalendar(path), {"path": str(path), "sha256": sha, "size_bytes": len(raw)}


def quote_dte_bucket(days):
    if days is None:
        return None
    if days < 0:
        return "expired"
    if days == 0:
        return "0"
    if days == 1:
        return "1"
    if days <= 7:
        return "2-7"
    if days <= 14:
        return "8-14"
    if days <= 30:
        return "15-30"
    if days <= 60:
        return "31-60"
    return "61+"


def utc_cut_ns(day, label="15:00"):
    hour, minute = (int(part) for part in label.split(":"))
    if type(day) is str:
        day = date.fromisoformat(day)
    return datetime_ns(datetime(day.year, day.month, day.day, hour, minute, tzinfo=timezone.utc))


def implementation_hashes():
    here = Path(__file__).resolve()
    stats = here.with_name("options_quote_statistics.py")
    return {
        "options_quote_measurements.py": file_digest(here),
        "options_quote_statistics.py": file_digest(stats),
        "version": VERSION,
    }


def scientific_hash(protocol):
    spec = dict(contract(protocol))
    spec.pop("data_root", None)
    return digest(spec)


def _empty_quote_table():
    pa = _pa()
    return pa.schema([
        ("symbol", pa.large_string()), ("expiration", pa.date32()),
        ("strike", pa.float64()), ("right", pa.large_string()),
        ("bid_size", pa.int64()), ("ask_size", pa.int64()),
        ("bid_exchange", pa.int64()), ("ask_exchange", pa.int64()),
        ("bid_condition", pa.int64()), ("ask_condition", pa.int64()),
        ("bid", pa.float64()), ("ask", pa.float64()),
        ("request_date", pa.date32()),
        ("ts_event", pa.timestamp("ns", tz="UTC")),
        ("osi_symbol", pa.large_string()),
    ]).empty_table()


def _is_empty_marker(payload, record):
    if record.get("empty_marker") is True or record.get("marker") == "empty":
        return True
    if payload == {}:
        return True
    return isinstance(payload, dict) and payload.get("empty_marker") is True and "rows" not in payload


def _source_family(record):
    source = record["source"]
    family = source.get("source_family")
    if family:
        return family
    dataset = source.get("dataset_id") or ""
    if "dte14" in dataset or "strike-range" in dataset:
        return "near"
    if "dte60-full-chain" in dataset or "vix-options__quote" in dataset:
        return "vix_full"
    if "dte60" in dataset or "atm10" in dataset:
        return "broad"
    if "yahoo__cash-daily" in dataset:
        return "cash_daily"
    if "ohlcv-1m" in dataset or "etf__ohlcv" in dataset:
        return "etf_1m"
    if "fred__usd-rates" in dataset:
        return "fred"
    if "corporate-actions" in dataset:
        return "corporate_actions"
    role = source.get("role")
    if role in QUOTE_ROLES:
        return "near"
    if role in {"underlier_daily", "cash_daily"}:
        return "cash_daily"
    if role in {"underlier_minute", "etf_1m"}:
        return "etf_1m"
    if role in {"rates", "fred"}:
        return "fred"
    if role in {"corporate_actions", "actions"}:
        return "corporate_actions"
    raise ContractError("admitted source_family could not be classified")


def _is_quote_record(record):
    source = record["source"]
    family = _source_family(record)
    if family in QUOTE_FAMILIES:
        return True
    return source.get("role") in QUOTE_ROLES


def _is_support_record(record):
    return _source_family(record) in SUPPORT_FAMILIES or record["source"].get("role") in SUPPORT_ROLES


def admission_schema():
    pa = _pa()
    return pa.schema([
        ("file_id", pa.int64()), ("path", pa.string()), ("sha256", pa.string()),
        ("dataset_id", pa.string()), ("chain", pa.string()),
        ("source_family", pa.string()), ("role", pa.string()),
        ("request_date", pa.string()), ("bytes", pa.int64()),
        ("rows", pa.int64()), ("schema_id", pa.string()),
        ("empty_marker", pa.bool_()), ("format", pa.string()),
    ])


def exception_schema():
    pa = _pa()
    return pa.schema([
        ("file_id", pa.int64()), ("row_index_start", pa.int64()),
        ("row_index_end", pa.int64()), ("n_rows", pa.int64()),
        ("chain", pa.string()), ("source_family", pa.string()),
        ("request_date", pa.string()), ("invalid_reason", pa.string()),
        ("osi_symbol", pa.string()), ("expiration", pa.string()),
        ("strike", pa.float64()), ("right", pa.string()),
        ("ts_event_ns", pa.int64()),
    ])


def alias_conflict_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("request_date", pa.string()),
        ("source_family", pa.string()), ("contract_id", pa.int32()),
        ("ts_event_ns", pa.int64()), ("multiplicity", pa.int64()),
        ("payload_equal", pa.bool_()), ("conflict", pa.bool_()),
        ("file_id", pa.int64()), ("row_index", pa.int64()),
        ("alias_file_id", pa.int64()), ("alias_row_index", pa.int64()),
        ("family_a", pa.string()), ("family_b", pa.string()),
    ])


def cut_board_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("request_date", pa.string()),
        ("cut_label", pa.string()), ("cut_ns", pa.int64()),
        ("source_family", pa.string()), ("contract_id", pa.int32()),
        ("osi_symbol", pa.string()), ("expiration", pa.string()),
        ("millistrike", pa.int64()), ("right", pa.string()),
        ("dte", pa.int64()), ("dte_bucket", pa.string()),
        ("bid", pa.float64()), ("ask", pa.float64()),
        ("bid_size", pa.int64()), ("ask_size", pa.int64()),
        ("bid_exchange", pa.int64()), ("ask_exchange", pa.int64()),
        ("bid_condition", pa.int64()), ("ask_condition", pa.int64()),
        ("mid", pa.float64()), ("spread", pa.float64()),
        ("relative_spread", pa.float64()),
        ("base_class", pa.string()),
        ("usable", pa.bool_()), ("conflict", pa.bool_()),
        ("condition_zero", pa.bool_()), ("nonpositive_size", pa.bool_()),
        ("negative_size", pa.bool_()), ("zero_bid", pa.bool_()),
        ("zero_ask", pa.bool_()), ("negative_price", pa.bool_()),
        ("nonfinite_price", pa.bool_()), ("session_outside", pa.bool_()),
        ("request_date_mismatch", pa.bool_()),
        ("ts_event_ns", pa.int64()),
        ("sample_age_ns", pa.int64()), ("unchanged_payload_age_ns", pa.int64()),
        ("sample_stale_60", pa.bool_()), ("sample_stale_300", pa.bool_()),
        ("sample_stale_900", pa.bool_()),
        ("payload_stale_60", pa.bool_()), ("payload_stale_300", pa.bool_()),
        ("payload_stale_900", pa.bool_()),
        ("run_continuity_observed", pa.bool_()),
        ("run_lower_bound_ns", pa.int64()),
        ("file_id", pa.int64()), ("row_index", pa.int64()),
        ("run_start_file_id", pa.int64()), ("run_start_row_index", pa.int64()),
        ("alias_file_id", pa.int64()), ("alias_row_index", pa.int64()),
        ("alias_multiplicity", pa.int64()),
        ("listed", pa.bool_()), ("listing_known", pa.bool_()),
        ("quoted", pa.bool_()), ("oi", pa.int64()),
        ("oi_available", pa.bool_()), ("oi_ambiguous", pa.bool_()),
        ("oi_missing", pa.bool_()), ("oi_stale", pa.bool_()),
        ("oi_expired", pa.bool_()), ("oi_zero", pa.bool_()),
        ("received_at_ns", pa.int64()), ("published_at_ns", pa.int64()),
        ("known_at_ns", pa.int64()), ("last_actual_update_ns", pa.int64()),
        ("actual_update_age_unknown", pa.bool_()),
        ("causal_feature_eligible", pa.bool_()),
        ("cut_status", pa.string()),
    ])


def source_quality_schema():
    pa = _pa()
    fields = [
        ("chain", pa.string()), ("request_date", pa.string()),
        ("source_family", pa.string()), ("right", pa.string()),
        ("dte_bucket", pa.string()),
        ("raw_rows", pa.int64()), ("unique_events", pa.int64()),
        ("missing_bid", pa.int64()), ("missing_ask", pa.int64()),
        ("missing_bid_size", pa.int64()), ("missing_ask_size", pa.int64()),
        ("missing_ts", pa.int64()),
    ]
    for name in BASE_CLASSES:
        fields.append((f"raw_{name}", pa.int64()))
        fields.append((f"unique_{name}", pa.int64()))
    for name in QUALITY_FLAGS:
        fields.append((f"raw_{name}", pa.int64()))
        fields.append((f"unique_{name}", pa.int64()))
    return pa.schema(fields)


def coverage_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("request_date", pa.string()),
        ("cut_label", pa.string()), ("source_family", pa.string()),
        ("intended", pa.bool_()), ("closed", pa.bool_()),
        ("early_close", pa.bool_()), ("session_state", pa.string()),
        ("file_present", pa.bool_()), ("empty_marker", pa.bool_()),
        ("missing_file", pa.bool_()), ("cut_status", pa.string()),
        ("listed_count", pa.int64()), ("quoted_count", pa.int64()),
        ("listed_unquoted", pa.int64()), ("quoted_unlisted", pa.int64()),
        ("usable_count", pa.int64()), ("conflict_count", pa.int64()),
        ("invalid_count", pa.int64()), ("all_zero_count", pa.int64()),
        ("one_sided_count", pa.int64()), ("crossed_count", pa.int64()),
        ("locked_count", pa.int64()), ("two_sided_count", pa.int64()),
        ("oi_available_count", pa.int64()), ("oi_missing_count", pa.int64()),
        ("oi_ambiguous_count", pa.int64()), ("oi_zero_count", pa.int64()),
        ("oi_amount_unknown", pa.int64()), ("oi_total_available", pa.int64()),
        ("oi_weighted_quoted_fraction", pa.float64()),
        ("listing_known", pa.bool_()), ("vix_listing_unknown", pa.bool_()),
        ("listing_unavailable", pa.bool_()), ("oi_unavailable", pa.bool_()),
        ("gt60_dte_listed", pa.int64()),
        ("no_sample", pa.int64()),
        ("causal_feature_eligible", pa.bool_()),
    ])


def underlier_support_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("request_date", pa.string()),
        ("cut_label", pa.string()), ("cut_ns", pa.int64()),
        ("etf_present", pa.bool_()), ("etf_symbol", pa.string()),
        ("etf_t_ns", pa.int64()), ("etf_open", pa.float64()),
        ("etf_high", pa.float64()), ("etf_low", pa.float64()),
        ("etf_close", pa.float64()), ("etf_volume", pa.float64()),
        ("etf_age_ns", pa.int64()), ("etf_gap", pa.bool_()),
        ("etf_assumption", pa.string()),
        ("cash_symbol", pa.string()), ("cash_date", pa.string()),
        ("cash_close", pa.float64()), ("cash_adjusted_close", pa.float64()),
        ("cash_same_date", pa.bool_()), ("cash_assumption", pa.string()),
        ("vix_cash_unavailable", pa.bool_()),
        ("fred_date", pa.string()), ("fred_series_id", pa.string()),
        ("fred_tenor_days", pa.int64()), ("fred_rate_pct", pa.float64()),
        ("fred_realtime_start", pa.string()), ("fred_realtime_end", pa.string()),
        ("fred_historical_known", pa.string()), ("fred_present", pa.bool_()),
        ("action_symbol", pa.string()), ("action_ex_date", pa.string()),
        ("action_dividend", pa.float64()), ("action_split_ratio", pa.float64()),
        ("action_announcement_known", pa.bool_()),
        ("action_future_exdate", pa.bool_()),
        ("causal_feature_eligible", pa.bool_()),
    ])


def identity_match_schema():
    pa = _pa()
    return pa.schema([
        ("contract_id", pa.int32()), ("chain", pa.string()),
        ("osi_symbol", pa.string()), ("expiration", pa.string()),
        ("millistrike", pa.int64()), ("right", pa.string()),
        ("oi_matched", pa.bool_()),
    ])


def _table(schema, rows):
    pa = _pa()
    if not rows:
        return schema.empty_table()
    return pa.table({field.name: [row.get(field.name) for field in schema] for field in schema},
                    schema=schema)


def _validate_admitted(admitted, protocol, selected_dates, selected_chains):
    if not isinstance(admitted, dict) or admitted.get("kind") != ADMITTED_KIND:
        raise ContractError("admitted options_quote_admitted_sources_v1 required")
    sources = admitted.get("sources")
    if type(sources) is not list:
        raise ContractError("admitted sources list required")
    if admitted.get("source_files") is not None and admitted["source_files"] != len(sources):
        raise IntegrityError("admitted source_files count does not match sources")
    chains = set(contract(protocol)["population"]["chains"])
    if selected_chains is not None:
        extra = set(selected_chains) - chains
        if extra:
            raise ContractError("selected_chains outside the frozen population")
    seen, selected_ids = set(), []
    date_set = None if selected_dates is None else set(selected_dates)
    chain_set = None if selected_chains is None else set(selected_chains)
    for record in sources:
        if type(record) is not dict or type(record.get("file_id")) is not int:
            raise ContractError("each admitted source needs an integer file_id")
        if record["file_id"] in seen:
            raise IntegrityError("duplicate admitted file_id")
        seen.add(record["file_id"])
        source = record.get("source")
        if not isinstance(source, dict):
            raise ContractError("admitted source mapping required")
        if source.get("chain") not in chains and not _is_support_record(record):
            raise ContractError("admitted chain is outside the frozen population")
        if record.get("format") not in {".parquet", ".json"}:
            raise ContractError("admitted format must be .parquet or .json")
        req = source.get("request_date")
        chain = source.get("chain")
        date_ok = date_set is None or req is None or req in date_set or _is_support_record(record)
        chain_ok = chain_set is None or chain is None or chain in chain_set or _is_support_record(record)
        if date_ok and chain_ok:
            selected_ids.append(record["file_id"])
    return sources, selected_ids


def _authenticate_source(protocol, record):
    source = record["source"]
    path = _resolve_source_path(protocol, source["path"])
    if not path.is_file():
        raise IntegrityError("admitted source file is missing")
    size = path.stat().st_size
    limit = int(contract(protocol).get("resources", {}).get("maximum_source_file_bytes", MAX_SOURCE_FILE))
    if size > limit:
        raise ContractError("source file exceeds the registered per-file bound")
    if size != source["size_bytes"]:
        raise IntegrityError("admitted source size changed before decode")
    raw = path.read_bytes()
    if len(raw) != source["size_bytes"]:
        raise IntegrityError("admitted source size changed during read")
    digest_hex = hashlib.sha256(raw).hexdigest()
    if digest_hex != record["sha256"]:
        raise IntegrityError("admitted source hash changed before decode")
    return path, raw, size, digest_hex


def read_admitted_quote(protocol, record, schemas):
    """Read one quote file after exact size/hash checks. Projected Arrow only."""
    pa = _pa()
    path, raw, size, digest_hex = _authenticate_source(protocol, record)
    fmt = record["format"]
    empty = False
    if fmt == ".json":
        payload = json.loads(raw.decode())
        if _is_empty_marker(payload, record):
            table = _empty_quote_table()
            empty = True
        else:
            rows = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
            if type(rows) is not list:
                raise ContractError("JSON source must be a row list or validated empty marker")
            table = pa.Table.from_pylist(rows) if rows else _empty_quote_table()
    elif fmt == ".parquet":
        import pyarrow.parquet as pq
        table = pq.read_table(pa.BufferReader(raw), columns=list(QUOTE_REQUIRED))
    else:
        raise ContractError("source format must be .parquet or .json")
    if not empty:
        schema_str = schemas.get(record["schema_id"])
        if type(schema_str) is not str:
            raise IntegrityError("admitted schema_id is not in schemas")
        _check_quote_clock_schema(table, schema_str)
        _check_schema(table, schema_str, QUOTE_REQUIRED)
    if record.get("rows") is not None and not empty and len(table) != record["rows"]:
        raise IntegrityError("admitted row count does not match the decoded table")
    return table, {
        "path": record["source"]["path"], "sha256": digest_hex, "size_bytes": size,
        "rows": len(table), "file_id": record["file_id"],
        "schema_id": record.get("schema_id"), "format": fmt, "empty_marker": empty,
    }


def _check_quote_clock_schema(table, schema_str):
    declared = dict(_schema_fields(schema_str))
    if "ts_event" not in table.schema.names:
        raise IntegrityError("admitted source missing ts_event")
    ts_type = table.schema.field("ts_event").type
    pa = _pa()
    if not pa.types.is_timestamp(ts_type):
        raise IntegrityError("ts_event must be an Arrow timestamp[ns]")
    if ts_type.unit != "ns":
        raise IntegrityError("ts_event unit must be nanoseconds")
    zone = getattr(ts_type, "tz", None)
    if zone not in (None, "UTC"):
        raise IntegrityError("ts_event timezone must be UTC")
    declared_ts = (declared.get("ts_event") or "").lower()
    if "timestamp" in declared_ts and "us" in declared_ts and "ns" not in declared_ts:
        raise IntegrityError("ts_event unit must be nanoseconds")


def read_admitted_support(protocol, record):
    path, raw, size, digest_hex = _authenticate_source(protocol, record)
    fmt = record["format"]
    pa = _pa()
    if fmt == ".json":
        payload = json.loads(raw.decode())
        rows = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
        table = pa.Table.from_pylist(rows) if rows else pa.table({})
    elif fmt == ".parquet":
        import pyarrow.parquet as pq
        table = pq.read_table(pa.BufferReader(raw))
    else:
        raise ContractError("support format must be .parquet or .json")
    return table, {
        "path": record["source"]["path"], "sha256": digest_hex, "size_bytes": size,
        "rows": len(table), "file_id": record["file_id"], "empty_marker": False,
        "format": fmt,
    }


def _int64_column(column, fill=0):
    pa, pc = _pa(), _pc()
    nulls = pc.is_null(column).to_numpy(zero_copy_only=False).astype(bool, copy=False)
    if pa.types.is_integer(column.type):
        values = column.fill_null(fill).cast(pa.int64()).to_numpy(zero_copy_only=False).astype("int64", copy=False)
        return values, nulls
    if pa.types.is_floating(column.type):
        raw = column.fill_null(float("nan")).to_numpy(zero_copy_only=False)
        values = _np().zeros(len(column), dtype="int64")
        finite = ~nulls & _np().isfinite(raw)
        values[finite] = raw[finite].astype("int64")
        return values, nulls | ~finite
    raise IntegrityError("integer quote column changed type")


def _float_column(column):
    pc = _pc()
    nulls = pc.is_null(column).to_numpy(zero_copy_only=False).astype(bool, copy=False)
    values = column.fill_null(float("nan")).to_numpy(zero_copy_only=False)
    return _np().asarray(values, dtype="float64"), nulls


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
            if exp is None or req is None:
                dte_grid[i, j] = -999
                bucket_grid[i, j] = None
            else:
                days = dte_days(exp, req)
                dte_grid[i, j] = days
                bucket_grid[i, j] = quote_dte_bucket(days)
    return dte_grid[exp_inv, req_inv], bucket_grid[exp_inv, req_inv]


class QuoteCodebook:
    """Match quote identity to OI contract_id once; local ids only when unmatched."""

    def __init__(self, oi_lookup=None, next_id=0):
        self.oi_lookup = oi_lookup or {}
        self.local = {}
        self.next_id = int(next_id)
        self.pending = []

    def intern(self, chain, osi, exp, milli, right):
        np = _np()
        n = len(osi)
        if n == 0:
            return np.empty(0, dtype=np.int32), np.empty(0, dtype=bool)
        keys = np.empty(n, dtype=object)
        for i in range(n):
            exp_i = exp[i]
            if hasattr(exp_i, "isoformat"):
                exp_i = exp_i.isoformat()
            keys[i] = (chain, osi[i], exp_i, int(milli[i]), right[i])
        uniq, inverse = np.unique(keys, return_inverse=True)
        cid_u = np.empty(len(uniq), dtype=np.int32)
        matched_u = np.zeros(len(uniq), dtype=bool)
        for u, key in enumerate(uniq):
            hit = self.oi_lookup.get(key)
            if hit is None:
                hit = self.local.get(key)
                if hit is None:
                    hit = self.next_id
                    self.next_id += 1
                    self.local[key] = hit
                    self.pending.append((hit, *key))
                matched_u[u] = False
            else:
                cid_u[u] = int(hit)
                matched_u[u] = True
                continue
            cid_u[u] = int(hit)
        return cid_u[inverse], matched_u[inverse]

    def flush_tables(self, chain):
        pa = _pa()
        rows = [item for item in self.pending if item[1] == chain]
        self.pending = [item for item in self.pending if item[1] != chain]
        if not rows:
            return None
        return pa.table({
            "contract_id": pa.array([row[0] for row in rows], type=pa.int32()),
            "chain": pa.array([row[1] for row in rows], type=pa.string()),
            "osi_symbol": pa.array([row[2] for row in rows], type=pa.string()),
            "expiration": pa.array([row[3] for row in rows], type=pa.string()),
            "millistrike": pa.array([row[4] for row in rows], type=pa.int64()),
            "right": pa.array([row[5] for row in rows], type=pa.string()),
            "oi_matched": pa.array([False] * len(rows), type=pa.bool_()),
        }, schema=identity_match_schema())


def parse_quote_typed(table, *, record, schema_str, dates, clocks, session_open_ns, session_close_ns):
    """Arrow/NumPy quote parse. Unique OSI/date codebook only; no day to_pylist."""
    pa, pc = _pa(), _pc()
    np = _np()
    source = record["source"]
    chain, file_id = source["chain"], record["file_id"]
    declared = source["request_date"]
    declared_days = dates.days(declared)
    family = _source_family(record)
    n = len(table)
    empty = _empty_parsed(np)
    if n == 0:
        return empty, _empty_exception_arrays(), n

    osi_dict, osi_idx, osi_null = _dictionary_keys(table.column("osi_symbol"))
    osi_parsed, osi_values = _osi_unique_parse(osi_dict, clocks.osi)
    exp_iso, exp_ok, exp_days = _date_column_iso(table.column("expiration"), dates)
    req_iso, req_ok, req_days = _date_column_iso(table.column("request_date"), dates)
    milli, strike_f, strike_present, strike_null = _millistrike_column(table.column("strike"))
    right_mapped, right_idx, right_null = _unique_string_map(table.column("right"), normalize_right)
    if "symbol" in table.schema.names:
        sym_mapped, sym_idx, sym_null = _unique_string_map(
            table.column("symbol"), lambda value: value if type(value) is str else None)
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
        symbol_mismatch[np.nonzero(present)[0]] = (symbols != chain)

    identity_invalid = (
        (~exp_ok) | (~req_ok) | osi_null | right_none | ((milli < 0) & (~strike_null))
        | ((~osi_null) & (~osi_ok))
        | (osi_ok & ((osi_root != chain) | symbol_mismatch))
        | (osi_ok & ((osi_exp != exp_iso) | (osi_right != right_arr) | (osi_milli != milli)))
    )
    identity_reason = np.empty(n, dtype=object)
    identity_reason[:] = None
    identity_reason[~exp_ok] = "invalid_expiration"
    identity_reason[(identity_reason == None) & (~req_ok)] = "invalid_request_date"  # noqa: E711
    identity_reason[(identity_reason == None) & (osi_null | right_none)] = "missing_identity_fields"
    identity_reason[(identity_reason == None) & (milli < 0) & (~strike_null)] = "inexact_or_nonfinite_strike"
    identity_reason[(identity_reason == None) & (~osi_null) & (~osi_ok)] = "unparseable_osi"
    identity_reason[(identity_reason == None) & osi_ok & ((osi_root != chain) | symbol_mismatch)] = (
        "osi_root_or_symbol_chain_mismatch")
    identity_reason[(identity_reason == None) & osi_ok & (
        (osi_exp != exp_iso) | (osi_right != right_arr) | (osi_milli != milli))] = "strike_or_osi_identity_conflict"

    ts_col = table.column("ts_event")
    ts_ok = np.zeros(n, dtype=bool)
    ts_arr = np.zeros(n, dtype=np.int64)
    clock_reason = np.empty(n, dtype=object)
    clock_reason[:] = None
    try:
        ts_cast = timestamp_ns_from_arrow(ts_col)
        ts_null = pc.is_null(ts_cast).to_numpy(zero_copy_only=False).astype(bool, copy=False)
        ts_arr = ts_cast.fill_null(0).cast(pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64, copy=False)
        ts_ok = ~ts_null
        clock_reason[~ts_ok] = "missing_clock"
    except (ContractError, IntegrityError) as exc:
        clock_reason[:] = "wrong_timestamp_unit_or_zone"
        raise IntegrityError(str(exc)) from exc

    bid, bid_null = _float_column(table.column("bid"))
    ask, ask_null = _float_column(table.column("ask"))
    bid_size, bid_size_null = _int64_column(table.column("bid_size"))
    ask_size, ask_size_null = _int64_column(table.column("ask_size"))
    bid_ex, _ = _int64_column(table.column("bid_exchange"))
    ask_ex, _ = _int64_column(table.column("ask_exchange"))
    bid_cond, _ = _int64_column(table.column("bid_condition"))
    ask_cond, _ = _int64_column(table.column("ask_condition"))

    finite_bid = (~bid_null) & np.isfinite(bid)
    finite_ask = (~ask_null) & np.isfinite(ask)
    nonfinite_price = (~finite_bid) | (~finite_ask)
    negative_price = (finite_bid & (bid < 0)) | (finite_ask & (ask < 0))
    invalid_numeric = nonfinite_price | negative_price
    zero_bid = finite_bid & (bid == 0)
    zero_ask = finite_ask & (ask == 0)
    negative_size = ((~bid_size_null) & (bid_size < 0)) | ((~ask_size_null) & (ask_size < 0))
    nonpositive_size = bid_size_null | ask_size_null | (bid_size <= 0) | (ask_size <= 0)
    condition_zero = (bid_cond == 0) | (ask_cond == 0)
    req_mismatch = req_ok & (req_days != declared_days)
    session_outside = np.zeros(n, dtype=bool)
    if session_open_ns is not None and session_close_ns is not None:
        session_outside = ts_ok & ((ts_arr < session_open_ns) | (ts_arr >= session_close_ns))

    base = np.empty(n, dtype=object)
    base[:] = None
    all_zero = finite_bid & finite_ask & (bid == 0) & (ask == 0)
    one_sided = finite_bid & finite_ask & (((bid == 0) & (ask > 0)) | ((ask == 0) & (bid > 0)))
    crossed = finite_bid & finite_ask & (bid > 0) & (ask > 0) & (ask < bid)
    locked = finite_bid & finite_ask & (bid > 0) & (ask == bid)
    two_sided = finite_bid & finite_ask & (bid > 0) & (ask > bid)
    base[identity_invalid] = "invalid_identity"
    remain = base == None  # noqa: E711
    base[remain & (~ts_ok)] = "invalid_clock"
    remain = base == None  # noqa: E711
    base[remain & invalid_numeric] = "invalid_numeric"
    remain = base == None  # noqa: E711
    base[remain & all_zero] = "all_zero"
    remain = base == None  # noqa: E711
    base[remain & one_sided] = "one_sided"
    remain = base == None  # noqa: E711
    base[remain & crossed] = "crossed"
    remain = base == None  # noqa: E711
    base[remain & locked] = "locked"
    remain = base == None  # noqa: E711
    base[remain & two_sided] = "two_sided"
    remain = base == None  # noqa: E711
    base[remain] = "invalid_numeric"

    usable = (
        (~identity_invalid) & ts_ok & finite_bid & finite_ask
        & (bid > 0) & (ask >= bid) & (bid_size > 0) & (ask_size > 0)
    )
    dte_v, bucket_v = _dte_columns(exp_iso, np.where(req_ok, req_iso, declared))
    east = clocks.eastern_labels(ts_arr) if n else np.empty(0, dtype=object)
    row_index = np.arange(n, dtype=np.int64)
    return {
        "file_id": np.full(n, int(file_id), dtype=np.int64),
        "row_index": row_index,
        "chain": np.array([chain] * n, dtype=object),
        "source_family": np.array([family] * n, dtype=object),
        "declared": np.array([declared] * n, dtype=object),
        "osi": osi_str,
        "expiration": exp_iso,
        "millistrike": milli,
        "right": right_arr,
        "request_date": req_iso,
        "ts_event_ns": ts_arr,
        "ts_ok": ts_ok,
        "bid": bid, "ask": ask,
        "bid_size": bid_size, "ask_size": ask_size,
        "bid_exchange": bid_ex, "ask_exchange": ask_ex,
        "bid_condition": bid_cond, "ask_condition": ask_cond,
        "bid_null": bid_null, "ask_null": ask_null,
        "bid_size_null": bid_size_null, "ask_size_null": ask_size_null,
        "base_class": base,
        "usable": usable,
        "identity_invalid": identity_invalid,
        "identity_reason": identity_reason,
        "clock_reason": clock_reason,
        "condition_zero": condition_zero,
        "nonpositive_size": nonpositive_size,
        "negative_size": negative_size,
        "zero_bid": zero_bid, "zero_ask": zero_ask,
        "negative_price": negative_price,
        "nonfinite_price": nonfinite_price,
        "session_outside": session_outside,
        "request_date_mismatch": req_mismatch,
        "dte": dte_v, "dte_bucket": bucket_v,
        "east": east,
        "strike": strike_f,
    }, _exception_from_parsed(n, file_id, chain, family, declared, identity_invalid, identity_reason,
                              ts_ok, clock_reason, osi_str, exp_iso, strike_f, right_arr, ts_arr), n


def _empty_parsed(np):
    return {
        "file_id": np.empty(0, dtype=np.int64), "row_index": np.empty(0, dtype=np.int64),
        "chain": np.empty(0, dtype=object), "source_family": np.empty(0, dtype=object),
        "declared": np.empty(0, dtype=object), "osi": np.empty(0, dtype=object),
        "expiration": np.empty(0, dtype=object), "millistrike": np.empty(0, dtype=np.int64),
        "right": np.empty(0, dtype=object), "request_date": np.empty(0, dtype=object),
        "ts_event_ns": np.empty(0, dtype=np.int64), "ts_ok": np.empty(0, dtype=bool),
        "bid": np.empty(0, dtype=np.float64), "ask": np.empty(0, dtype=np.float64),
        "bid_size": np.empty(0, dtype=np.int64), "ask_size": np.empty(0, dtype=np.int64),
        "bid_exchange": np.empty(0, dtype=np.int64), "ask_exchange": np.empty(0, dtype=np.int64),
        "bid_condition": np.empty(0, dtype=np.int64), "ask_condition": np.empty(0, dtype=np.int64),
        "bid_null": np.empty(0, dtype=bool), "ask_null": np.empty(0, dtype=bool),
        "bid_size_null": np.empty(0, dtype=bool), "ask_size_null": np.empty(0, dtype=bool),
        "base_class": np.empty(0, dtype=object), "usable": np.empty(0, dtype=bool),
        "identity_invalid": np.empty(0, dtype=bool), "identity_reason": np.empty(0, dtype=object),
        "clock_reason": np.empty(0, dtype=object),
        "condition_zero": np.empty(0, dtype=bool), "nonpositive_size": np.empty(0, dtype=bool),
        "negative_size": np.empty(0, dtype=bool), "zero_bid": np.empty(0, dtype=bool),
        "zero_ask": np.empty(0, dtype=bool), "negative_price": np.empty(0, dtype=bool),
        "nonfinite_price": np.empty(0, dtype=bool), "session_outside": np.empty(0, dtype=bool),
        "request_date_mismatch": np.empty(0, dtype=bool),
        "dte": np.empty(0, dtype=np.int64), "dte_bucket": np.empty(0, dtype=object),
        "east": np.empty(0, dtype=object), "strike": np.empty(0, dtype=np.float64),
    }


def _empty_exception_arrays():
    np = _np()
    return {
        "file_id": np.empty(0, dtype=np.int64), "row_index": np.empty(0, dtype=np.int64),
        "reason": np.empty(0, dtype=object), "osi": np.empty(0, dtype=object),
        "expiration": np.empty(0, dtype=object), "strike": np.empty(0, dtype=np.float64),
        "right": np.empty(0, dtype=object), "ts_event_ns": np.empty(0, dtype=np.int64),
        "chain": np.empty(0, dtype=object), "source_family": np.empty(0, dtype=object),
        "request_date": np.empty(0, dtype=object),
    }


def _exception_from_parsed(n, file_id, chain, family, declared, identity_invalid, identity_reason,
                           ts_ok, clock_reason, osi, exp, strike, right, ts):
    np = _np()
    invalid = identity_invalid | (~ts_ok)
    if not np.any(invalid):
        return _empty_exception_arrays()
    reason = np.empty(n, dtype=object)
    reason[:] = None
    reason[identity_invalid] = identity_reason[identity_invalid]
    reason[(~identity_invalid) & (~ts_ok)] = clock_reason[(~identity_invalid) & (~ts_ok)]
    return {
        "file_id": np.full(int(invalid.sum()), int(file_id), dtype=np.int64),
        "row_index": np.nonzero(invalid)[0].astype(np.int64, copy=False),
        "reason": reason[invalid],
        "osi": osi[invalid], "expiration": exp[invalid],
        "strike": strike[invalid], "right": right[invalid],
        "ts_event_ns": ts[invalid],
        "chain": np.array([chain] * int(invalid.sum()), dtype=object),
        "source_family": np.array([family] * int(invalid.sum()), dtype=object),
        "request_date": np.array([declared] * int(invalid.sum()), dtype=object),
    }


def _concat_parsed(parts):
    np = _np()
    if not parts:
        return _empty_parsed(np)
    out = {}
    for key in parts[0]:
        arrays = [part[key] for part in parts if len(part[key])]
        out[key] = np.concatenate(arrays) if arrays else parts[0][key]
    return out


def _payload_equal(parsed, i, j):
    np = _np()
    if parsed["bid"][i] != parsed["bid"][j] and not (
            np.isnan(parsed["bid"][i]) and np.isnan(parsed["bid"][j])):
        return False
    if parsed["ask"][i] != parsed["ask"][j] and not (
            np.isnan(parsed["ask"][i]) and np.isnan(parsed["ask"][j])):
        return False
    return (
        parsed["bid_size"][i] == parsed["bid_size"][j]
        and parsed["ask_size"][i] == parsed["ask_size"][j]
        and parsed["bid_exchange"][i] == parsed["bid_exchange"][j]
        and parsed["ask_exchange"][i] == parsed["ask_exchange"][j]
        and parsed["bid_condition"][i] == parsed["bid_condition"][j]
        and parsed["ask_condition"][i] == parsed["ask_condition"][j]
    )


def _payload_equal_vec(parsed, left, right):
    np = _np()
    bid_eq = (parsed["bid"][left] == parsed["bid"][right]) | (
        np.isnan(parsed["bid"][left]) & np.isnan(parsed["bid"][right]))
    ask_eq = (parsed["ask"][left] == parsed["ask"][right]) | (
        np.isnan(parsed["ask"][left]) & np.isnan(parsed["ask"][right]))
    return (
        bid_eq & ask_eq
        & (parsed["bid_size"][left] == parsed["bid_size"][right])
        & (parsed["ask_size"][left] == parsed["ask_size"][right])
        & (parsed["bid_exchange"][left] == parsed["bid_exchange"][right])
        & (parsed["ask_exchange"][left] == parsed["ask_exchange"][right])
        & (parsed["bid_condition"][left] == parsed["bid_condition"][right])
        & (parsed["ask_condition"][left] == parsed["ask_condition"][right])
    )


def sort_and_dedup(parsed, contract_id):
    """Sort by contract+exact ns. Dedup identical payloads; conflict has no winner.

    Row-group boundaries must not reset a contract run: callers concatenate the
    projected day before this function.
    """
    np = _np()
    n = len(contract_id)
    if n == 0:
        empty = {key: parsed[key] for key in parsed}
        empty.update({
            "contract_id": contract_id, "keep": np.empty(0, dtype=bool),
            "conflict": np.empty(0, dtype=bool), "multiplicity": np.empty(0, dtype=np.int64),
            "alias_file_id": np.empty(0, dtype=np.int64),
            "alias_row_index": np.empty(0, dtype=np.int64),
            "run_start": np.empty(0, dtype=np.int64),
            "run_continuity": np.empty(0, dtype=bool),
            "run_start_file_id": np.empty(0, dtype=np.int64),
            "run_start_row_index": np.empty(0, dtype=np.int64),
        })
        return empty
    order = np.lexsort((parsed["row_index"], parsed["file_id"], parsed["ts_event_ns"], contract_id))
    parsed = {key: value[order] for key, value in parsed.items()}
    cid = contract_id[order]
    ts = parsed["ts_event_ns"]
    keep = np.ones(n, dtype=bool)
    conflict = np.zeros(n, dtype=bool)
    multiplicity = np.ones(n, dtype=np.int64)
    alias_fid = np.full(n, -1, dtype=np.int64)
    alias_row = np.full(n, -1, dtype=np.int64)
    group = np.zeros(n, dtype=np.int64)
    if n > 1:
        group[1:] = np.cumsum((cid[1:] != cid[:-1]) | (ts[1:] != ts[:-1]))
    starts = np.r_[0, np.flatnonzero(np.diff(group)) + 1]
    ends = np.r_[starts[1:], n]
    for start, end in zip(starts.tolist(), ends.tolist()):
        if end - start == 1:
            continue
        idx = np.arange(start, end)
        first = idx[0]
        eq = _payload_equal_vec(parsed, np.full(end - start, first), idx)
        multiplicity[first] = end - start
        if bool(np.all(eq)):
            keep[idx[1:]] = False
            if end - start > 1:
                alias_fid[first] = parsed["file_id"][idx[1]]
                alias_row[first] = parsed["row_index"][idx[1]]
        else:
            conflict[idx] = True
            keep[idx[1:]] = False
            parsed["base_class"][first] = "conflict"
            parsed["usable"][first] = False
            if end - start > 1:
                alias_fid[first] = parsed["file_id"][idx[1]]
                alias_row[first] = parsed["row_index"][idx[1]]
    parsed["contract_id"] = cid
    parsed["keep"] = keep
    parsed["conflict"] = conflict
    parsed["multiplicity"] = multiplicity
    parsed["alias_file_id"] = alias_fid
    parsed["alias_row_index"] = alias_row
    return _annotate_payload_runs(parsed)


def _annotate_payload_runs(parsed):
    np = _np()
    n = len(parsed["contract_id"])
    run_start = np.arange(n, dtype=np.int64)
    continuity = np.ones(n, dtype=bool)
    if n == 0:
        parsed["run_start"] = run_start
        parsed["run_continuity"] = continuity
        parsed["run_start_file_id"] = np.empty(0, dtype=np.int64)
        parsed["run_start_row_index"] = np.empty(0, dtype=np.int64)
        return parsed
    cid = parsed["contract_id"]
    ts = parsed["ts_event_ns"]
    kept = parsed["keep"]
    invalid = parsed["identity_invalid"] | (~parsed["ts_ok"]) | parsed["conflict"]
    live = np.flatnonzero(kept)
    if len(live) == 0:
        parsed["run_start"] = run_start
        parsed["run_continuity"] = continuity
        parsed["run_start_file_id"] = parsed["file_id"]
        parsed["run_start_row_index"] = parsed["row_index"]
        return parsed
    lc = cid[live]
    lt = ts[live]
    li = invalid[live]
    same_contract = np.zeros(len(live), dtype=bool)
    same_contract[1:] = lc[1:] == lc[:-1]
    same_payload = np.zeros(len(live), dtype=bool)
    if len(live) > 1:
        same_payload[1:] = _payload_equal_vec(parsed, live[1:], live[:-1])
    gap = np.zeros(len(live), dtype=bool)
    if len(live) > 1:
        gap[1:] = (lt[1:] - lt[:-1]) > GAP_BREAK_NS
    prev_invalid = np.zeros(len(live), dtype=bool)
    if len(live) > 1:
        prev_invalid[1:] = li[:-1]
    brk = (~same_contract) | (~same_payload) | gap | li | prev_invalid
    brk[0] = True
    run_id = np.cumsum(brk)
    first = np.r_[True, run_id[1:] != run_id[:-1]]
    start_pos = np.maximum.accumulate(np.where(first, np.arange(len(live)), 0))
    live_start = live[start_pos]
    live_cont = np.ones(len(live), dtype=bool)
    live_cont[1:] = (~gap[1:]) & same_payload[1:] & same_contract[1:] & (~li[1:]) & (~prev_invalid[1:])
    live_cont[0] = True
    run_start[live] = live_start
    continuity[live] = live_cont
    kept_idx = np.where(kept, np.arange(n), -1)
    kept_idx = np.maximum.accumulate(kept_idx)
    inherit = (~kept) & (kept_idx >= 0)
    run_start[inherit] = run_start[kept_idx[inherit]]
    continuity[inherit] = continuity[kept_idx[inherit]]
    parsed["run_start"] = run_start
    parsed["run_continuity"] = continuity
    parsed["run_start_file_id"] = parsed["file_id"][run_start]
    parsed["run_start_row_index"] = parsed["row_index"][run_start]
    return parsed


def take_kept(parsed):
    np = _np()
    keep = parsed["keep"]
    return {key: value[keep] if hasattr(value, "__len__") and len(value) == len(keep) else value
            for key, value in parsed.items()}


def union_families(family_parsed):
    """Dedup each source family, then union overlapping identity+time rows."""
    np = _np()
    owned = {}
    alias_rows = []
    for family, parsed in family_parsed.items():
        if parsed is None or len(parsed.get("contract_id", [])) == 0:
            continue
        kept = take_kept(parsed)
        owned[family] = kept
        conflict_mask = kept["conflict"]
        multi = kept["multiplicity"] > 1
        for i in np.flatnonzero(multi | conflict_mask).tolist():
            alias_rows.append({
                "chain": kept["chain"][i], "request_date": kept["declared"][i],
                "source_family": family, "contract_id": int(kept["contract_id"][i]),
                "ts_event_ns": int(kept["ts_event_ns"][i]),
                "multiplicity": int(kept["multiplicity"][i]),
                "payload_equal": not bool(kept["conflict"][i]),
                "conflict": bool(kept["conflict"][i]),
                "file_id": int(kept["file_id"][i]), "row_index": int(kept["row_index"][i]),
                "alias_file_id": int(kept["alias_file_id"][i]) if kept["alias_file_id"][i] >= 0 else None,
                "alias_row_index": int(kept["alias_row_index"][i]) if kept["alias_row_index"][i] >= 0 else None,
                "family_a": family, "family_b": family,
            })
    if "near" in owned and "broad" in owned:
        union, extra = _union_two(owned["near"], owned["broad"])
        owned["union"] = union
        alias_rows.extend(extra)
    elif "near" in owned:
        owned["union"] = owned["near"]
    elif "broad" in owned:
        owned["union"] = owned["broad"]
    elif "vix_full" in owned:
        owned["union"] = owned["vix_full"]
    return owned, alias_rows


def _union_two(near, broad):
    np = _np()
    n_a, n_b = len(near["contract_id"]), len(broad["contract_id"])
    keys_a = np.stack((near["contract_id"].astype(np.int64), near["ts_event_ns"]), axis=1)
    keys_b = np.stack((broad["contract_id"].astype(np.int64), broad["ts_event_ns"]), axis=1)
    # Structured unique keys for exact common identity+time.
    dtype = np.dtype([("c", np.int64), ("t", np.int64)])
    ka = np.empty(n_a, dtype=dtype)
    kb = np.empty(n_b, dtype=dtype)
    ka["c"], ka["t"] = keys_a[:, 0], keys_a[:, 1]
    kb["c"], kb["t"] = keys_b[:, 0], keys_b[:, 1]
    order_a = np.argsort(ka, order=("c", "t"))
    order_b = np.argsort(kb, order=("c", "t"))
    ka_s, kb_s = ka[order_a], kb[order_b]
    ia = ib = 0
    used_a = np.zeros(n_a, dtype=bool)
    used_b = np.zeros(n_b, dtype=bool)
    pick_src = []
    pick_idx = []
    extra = []
    while ia < n_a and ib < n_b:
        if ka_s[ia] == kb_s[ib]:
            a = int(order_a[ia])
            b = int(order_b[ib])
            used_a[a] = True
            used_b[b] = True
            eq = _payload_rows_equal(near, a, broad, b)
            if eq:
                pick_src.append("near")
                pick_idx.append((a, b))
                extra.append({
                    "chain": near["chain"][a], "request_date": near["declared"][a],
                    "source_family": "union", "contract_id": int(near["contract_id"][a]),
                    "ts_event_ns": int(near["ts_event_ns"][a]),
                    "multiplicity": 2, "payload_equal": True, "conflict": False,
                    "file_id": int(near["file_id"][a]), "row_index": int(near["row_index"][a]),
                    "alias_file_id": int(broad["file_id"][b]),
                    "alias_row_index": int(broad["row_index"][b]),
                    "family_a": "near", "family_b": "broad",
                })
            else:
                pick_src.append("conflict")
                pick_idx.append((a, b))
                extra.append({
                    "chain": near["chain"][a], "request_date": near["declared"][a],
                    "source_family": "union", "contract_id": int(near["contract_id"][a]),
                    "ts_event_ns": int(near["ts_event_ns"][a]),
                    "multiplicity": 2, "payload_equal": False, "conflict": True,
                    "file_id": int(near["file_id"][a]), "row_index": int(near["row_index"][a]),
                    "alias_file_id": int(broad["file_id"][b]),
                    "alias_row_index": int(broad["row_index"][b]),
                    "family_a": "near", "family_b": "broad",
                })
            ia += 1
            ib += 1
        elif ka_s[ia] < kb_s[ib]:
            ia += 1
        else:
            ib += 1
    union = _merge_union_rows(near, broad, used_a, used_b, pick_src, pick_idx)
    return union, extra


def _payload_rows_equal(left, i, right, j):
    np = _np()
    if left["bid"][i] != right["bid"][j] and not (np.isnan(left["bid"][i]) and np.isnan(right["bid"][j])):
        return False
    if left["ask"][i] != right["ask"][j] and not (np.isnan(left["ask"][i]) and np.isnan(right["ask"][j])):
        return False
    return (
        left["bid_size"][i] == right["bid_size"][j]
        and left["ask_size"][i] == right["ask_size"][j]
        and left["bid_exchange"][i] == right["bid_exchange"][j]
        and left["ask_exchange"][i] == right["ask_exchange"][j]
        and left["bid_condition"][i] == right["bid_condition"][j]
        and left["ask_condition"][i] == right["ask_condition"][j]
    )


def _merge_union_rows(near, broad, used_a, used_b, pick_src, pick_idx):
    np = _np()
    keys = [key for key in near if hasattr(near[key], "__len__")]
    blocks = []
    only_a = np.flatnonzero(~used_a)
    only_b = np.flatnonzero(~used_b)
    if len(only_a):
        blocks.append({key: near[key][only_a] for key in keys})
    if len(only_b):
        blocks.append({key: broad[key][only_b] for key in keys})
    for src, idx in zip(pick_src, pick_idx):
        a, b = idx
        if src == "near":
            row = {key: np.asarray([near[key][a]]) for key in keys}
            row["multiplicity"] = np.array([2], dtype=np.int64)
            row["alias_file_id"] = np.array([broad["file_id"][b]], dtype=np.int64)
            row["alias_row_index"] = np.array([broad["row_index"][b]], dtype=np.int64)
            blocks.append(row)
        else:
            row = {key: np.asarray([near[key][a]]) for key in keys}
            row["conflict"] = np.array([True])
            row["usable"] = np.array([False])
            row["base_class"] = np.array(["conflict"], dtype=object)
            row["multiplicity"] = np.array([2], dtype=np.int64)
            row["alias_file_id"] = np.array([broad["file_id"][b]], dtype=np.int64)
            row["alias_row_index"] = np.array([broad["row_index"][b]], dtype=np.int64)
            blocks.append(row)
    if not blocks:
        return {key: near[key][:0] for key in keys}
    out = {}
    for key in keys:
        out[key] = np.concatenate([block[key] for block in blocks])
    order = np.lexsort((out["row_index"], out["file_id"], out["ts_event_ns"], out["contract_id"]))
    out = {key: value[order] for key, value in out.items()}
    return _annotate_payload_runs({**out, "keep": np.ones(len(out["contract_id"]), dtype=bool)})


def _stale_flags(age_ns):
    if age_ns is None:
        return None, None, None
    seconds = age_ns / NS
    return seconds > 60, seconds > 300, seconds > 900


def select_cut_rows(parsed, *, cut_ns, cut_date, session_open_ns):
    """Newest eligible row per contract. Current conflict/invalid suppresses older valid."""
    np = _np()
    if parsed is None or len(parsed.get("contract_id", [])) == 0:
        return None
    ts = parsed["ts_event_ns"]
    req = parsed["declared"]
    east = parsed["east"]
    eligible = parsed["ts_ok"] & (ts <= cut_ns) & (req <= cut_date) & (east == cut_date)
    if session_open_ns is not None:
        eligible = eligible & (ts >= session_open_ns)
    if not np.any(eligible):
        return None
    idx = np.flatnonzero(eligible)
    cid = parsed["contract_id"][idx]
    order = np.lexsort((-parsed["row_index"][idx], -parsed["file_id"][idx], -ts[idx], cid))
    idx = idx[order]
    cid = parsed["contract_id"][idx]
    first = np.r_[True, cid[1:] != cid[:-1]]
    chosen = idx[first]
    return chosen


def _mid_spread(bid, ask):
    if bid is None or ask is None:
        return None, None, None
    if not (math.isfinite(bid) and math.isfinite(ask)):
        return None, None, None
    mid = (bid + ask) / 2.0
    spread = ask - bid
    rel = None if mid <= 0 else spread / mid
    return mid, spread, rel


class OIJoinAdapter:
    """Bounded per-chain projected arrays. Not a 93-million-row Python dict."""

    def __init__(self, oi_population):
        self.available = oi_population is not None
        self.listing_unavailable = oi_population is None
        self.identity = {}
        self.by_id = {}
        self.reports = {}
        self.intervals = {}
        self._asof_index = {}
        self.max_id = 0
        self.oi_ref = None
        if oi_population is None:
            return
        if not isinstance(oi_population, dict):
            raise ContractError("oi_population must be an authenticated OI result or null")
        refs = oi_population.get("refs") or {}
        self.oi_ref = {
            "family": oi_population.get("family"),
            "version": oi_population.get("version"),
            "identity_map": refs.get("identity_map"),
            "reports": refs.get("reports"),
            "asof_intervals": refs.get("asof_intervals"),
        }
        self._load_identity(refs.get("identity_map"))
        self._load_reports(refs.get("reports"))
        self._load_intervals(refs.get("asof_intervals"))

    def _as_refs(self, value):
        if value is None:
            return []
        if isinstance(value, dict) and "path" in value:
            return [value]
        return list(value)

    def _read_projected(self, refs, columns):
        import pyarrow.parquet as pq
        tables = []
        for ref in self._as_refs(refs):
            path = Path(ref["path"])
            if ref.get("sha256") and file_digest(path) != ref["sha256"]:
                raise IntegrityError("OI artifact hash changed")
            if ref.get("size_bytes") is not None and path.stat().st_size != ref["size_bytes"]:
                raise IntegrityError("OI artifact size changed")
            available = set(pq.ParquetFile(path).schema_arrow.names)
            use = [name for name in columns if name in available]
            tables.append(pq.read_table(path, columns=use))
        if not tables:
            return None
        return _pa().concat_tables(tables, promote_options="default")

    def _load_identity(self, refs):
        table = self._read_projected(refs, ["contract_id", "chain", "osi_symbol", "expiration",
                                           "millistrike", "right"])
        if table is None or len(table) == 0:
            return
        cid = table.column("contract_id").to_numpy(zero_copy_only=False)
        chain = table.column("chain").to_pylist()
        osi = table.column("osi_symbol").to_pylist()
        exp = table.column("expiration").to_pylist()
        milli = table.column("millistrike").to_numpy(zero_copy_only=False)
        right = table.column("right").to_pylist()
        lookup = {}
        by_id = {}
        for i in range(len(table)):
            exp_i = exp[i]
            if hasattr(exp_i, "isoformat"):
                exp_i = exp_i.isoformat()
            lookup[(chain[i], osi[i], exp_i, int(milli[i]), right[i])] = int(cid[i])
            by_id[int(cid[i])] = {
                "osi_symbol": osi[i], "expiration": exp_i,
                "millistrike": int(milli[i]), "right": right[i],
            }
            if int(cid[i]) > self.max_id:
                self.max_id = int(cid[i])
        self.identity = lookup
        self.by_id = by_id

    def _load_reports(self, refs):
        table = self._read_projected(refs, [
            "contract_id", "chain", "request_date", "listed",
            "first_oi", "last_oi", "last_eq_first", "dte",
        ])
        if table is None or len(table) == 0:
            return
        cid = table.column("contract_id").to_numpy(zero_copy_only=False).astype("int32")
        chain = table.column("chain").to_pylist()
        req = table.column("request_date").to_pylist()
        listed = table.column("listed").to_numpy(zero_copy_only=False) if "listed" in table.schema.names else None
        by = defaultdict(lambda: {"cid": [], "listed": []})
        for i in range(len(table)):
            key = (chain[i], req[i])
            by[key]["cid"].append(int(cid[i]))
            flag = True if listed is None else bool(listed[i])
            by[key]["listed"].append(flag)
        np = _np()
        self.reports = {key: {
            "cid": np.asarray(val["cid"], dtype=np.int32),
            "listed": np.asarray(val["listed"], dtype=bool),
        } for key, val in by.items()}

    def _load_intervals(self, refs):
        table = self._read_projected(refs, [
            "contract_id", "chain", "open_interest", "ts_event_ns", "request_date",
            "ambiguous", "valid_from_ns", "valid_to_ns", "expiration",
        ])
        if table is None or len(table) == 0:
            return
        chain = table.column("chain").to_pylist()
        by = defaultdict(list)
        rows = table.to_pylist() if len(table) < 50000 else None
        if rows is not None:
            for row in rows:
                by[row["chain"]].append(row)
        else:
            for i in range(len(table)):
                row = {name: table.column(name)[i].as_py() for name in table.schema.names}
                by[row["chain"]].append(row)
        self.intervals = dict(by)

    def listed_ids(self, chain, request_date):
        np = _np()
        if chain in CHAINS_WITHOUT_LISTING:
            return None
        if not self.available:
            return None
        rec = self.reports.get((chain, request_date))
        if rec is None:
            return np.empty(0, dtype=np.int32)
        return rec["cid"][rec["listed"]]

    def identity_fields(self, contract_id):
        return self.by_id.get(int(contract_id), {})

    def asof_oi(self, chain, contract_id, cut_ns, cut_date, prev_cash):
        if not self.available:
            return {
                "oi": None, "available": False, "ambiguous": False, "missing": True,
                "stale": False, "expired": False, "zero": False,
            }
        cache_key = (chain, None if cut_ns is None else int(cut_ns), cut_date)
        index = self._asof_index.get(cache_key)
        if index is None:
            visible = reconstruct_asof_intervals(self.intervals.get(chain) or [], cut_ns, cut_date)
            index = defaultdict(list)
            for row in visible:
                index[int(row["contract_id"])].append(row)
            self._asof_index[cache_key] = index
        hits = index.get(int(contract_id), [])
        if not hits:
            return {
                "oi": None, "available": False, "ambiguous": False, "missing": True,
                "stale": False, "expired": False, "zero": False,
            }
        if any(row.get("ambiguous") for row in hits) or len({row.get("open_interest") for row in hits}) != 1:
            return {
                "oi": None, "available": False, "ambiguous": True, "missing": False,
                "stale": False, "expired": False, "zero": False,
            }
        row = hits[0]
        oi = row.get("open_interest")
        expired = row.get("expiration") is not None and row["expiration"] < cut_date
        stale = bool(prev_cash and row.get("request_date") and row["request_date"] < prev_cash)
        return {
            "oi": oi, "available": oi is not None and not expired,
            "ambiguous": False, "missing": oi is None,
            "stale": stale, "expired": expired, "zero": oi == 0,
        }


class SupportStore:
    """Parse admitted support files once. No future fill. No invented VIX cash."""

    def __init__(self):
        self.cash = defaultdict(dict)
        self.etf = defaultdict(lambda: {"t": [], "o": [], "h": [], "l": [], "c": [], "v": []})
        self.fred = []
        self.actions = []
        self.vix_cash_declared = False

    def add_table(self, family, table, record):
        if family == "cash_daily":
            self._add_cash(table)
        elif family == "etf_1m":
            self._add_etf(table)
        elif family == "fred":
            self._add_fred(table)
        elif family == "corporate_actions":
            self._add_actions(table, record)

    def _add_cash(self, table):
        names = set(table.schema.names)
        date_col = "date" if "date" in names else "request_date"
        symbol_col = "symbol" if "symbol" in names else None
        dates = table.column(date_col).to_pylist()
        symbols = table.column(symbol_col).to_pylist() if symbol_col else [None] * len(table)
        close = table.column("close").to_pylist() if "close" in names else [None] * len(table)
        adj = table.column("adjusted_close").to_pylist() if "adjusted_close" in names else [None] * len(table)
        for i in range(len(table)):
            label = dates[i].isoformat() if hasattr(dates[i], "isoformat") else dates[i]
            self.cash[str(symbols[i])][label] = {
                "close": close[i], "adjusted_close": adj[i],
            }

    def _add_etf(self, table):
        names = set(table.schema.names)
        t = table.column("t").to_numpy(zero_copy_only=False).astype("int64")
        inst = table.column("instrument_id").to_pylist() if "instrument_id" in names else ["UNKNOWN"] * len(table)
        o = table.column("o").to_numpy(zero_copy_only=False) if "o" in names else None
        h = table.column("h").to_numpy(zero_copy_only=False) if "h" in names else None
        l = table.column("l").to_numpy(zero_copy_only=False) if "l" in names else None
        c = table.column("c").to_numpy(zero_copy_only=False) if "c" in names else None
        v = table.column("v").to_numpy(zero_copy_only=False) if "v" in names else None
        for i in range(len(table)):
            key = str(inst[i])
            self.etf[key]["t"].append(int(t[i]) * 1_000_000)
            self.etf[key]["o"].append(None if o is None else float(o[i]))
            self.etf[key]["h"].append(None if h is None else float(h[i]))
            self.etf[key]["l"].append(None if l is None else float(l[i]))
            self.etf[key]["c"].append(None if c is None else float(c[i]))
            self.etf[key]["v"].append(None if v is None else float(v[i]))

    def _add_fred(self, table):
        names = set(table.schema.names)
        for row in table.to_pylist():
            label = row.get("date")
            if hasattr(label, "isoformat"):
                label = label.isoformat()
            self.fred.append({
                "date": label,
                "series_id": row.get("series_id"),
                "tenor_days": row.get("tenor_days"),
                "rate_pct": row.get("rate_pct"),
                "realtime_start": row.get("realtime_start").isoformat() if hasattr(row.get("realtime_start"), "isoformat") else row.get("realtime_start"),
                "realtime_end": row.get("realtime_end").isoformat() if hasattr(row.get("realtime_end"), "isoformat") else row.get("realtime_end"),
            })

    def _add_actions(self, table, record):
        symbol = record["source"].get("chain") or record["source"].get("symbol")
        for row in table.to_pylist():
            ex = row.get("ex_date") or row.get("date")
            if hasattr(ex, "isoformat"):
                ex = ex.isoformat()
            self.actions.append({
                "symbol": row.get("symbol") or symbol,
                "ex_date": ex,
                "dividend": row.get("dividend"),
                "split_ratio": row.get("split_ratio"),
            })

    def finalize(self):
        np = _np()
        for key, bag in self.etf.items():
            if not bag["t"]:
                continue
            order = np.argsort(np.asarray(bag["t"], dtype=np.int64), kind="stable")
            for field in ("t", "o", "h", "l", "c", "v"):
                bag[field] = [bag[field][int(i)] for i in order.tolist()]
        self.fred.sort(key=lambda row: (row["date"] or "", row.get("series_id") or "", row.get("tenor_days") or -1))
        self.actions.sort(key=lambda row: (row.get("ex_date") or "", row.get("symbol") or ""))

    def cash_at(self, symbol, cut_date, *, at_or_after_close, prior_date):
        if symbol is None:
            return None
        series = self.cash.get(symbol) or {}
        if at_or_after_close and cut_date in series:
            row = series[cut_date]
            return {**row, "date": cut_date, "same_date": True,
                    "assumption": "retrospective_same_date_close_at_or_after_declared_close"}
        if prior_date and prior_date in series:
            row = series[prior_date]
            return {**row, "date": prior_date, "same_date": False,
                    "assumption": "prior_available_cash_date_close"}
        earlier = [label for label in series if label < cut_date]
        if not earlier:
            return None
        label = max(earlier)
        if not at_or_after_close and label == cut_date:
            return None
        row = series[label]
        return {**row, "date": label, "same_date": label == cut_date,
                "assumption": "prior_available_cash_date_close"}

    def etf_at(self, symbol, cut_ns):
        bag = self.etf.get(symbol)
        if not bag or not bag["t"]:
            return None
        np = _np()
        ts = np.asarray(bag["t"], dtype=np.int64)
        idx = int(np.searchsorted(ts, cut_ns, side="right") - 1)
        if idx < 0:
            return None
        age = cut_ns - int(ts[idx])
        complete = all(bag[field][idx] is not None and math.isfinite(bag[field][idx])
                       for field in ("o", "h", "l", "c"))
        if not complete:
            return None
        gap = False
        if idx + 1 < len(ts) and int(ts[idx + 1]) <= cut_ns:
            gap = True
        if age > MINUTE_NS:
            gap = True
        return {
            "t_ns": int(ts[idx]), "open": bag["o"][idx], "high": bag["h"][idx],
            "low": bag["l"][idx], "close": bag["c"][idx], "volume": bag["v"][idx],
            "age_ns": age, "gap": gap,
            "assumption": "latest_complete_one_minute_bar_at_or_before_cut",
        }

    def fred_at(self, cut_date):
        eligible = [row for row in self.fred if row["date"] is not None and row["date"] <= cut_date]
        if not eligible:
            return None
        first = min(row["date"] for row in self.fred if row["date"] is not None)
        if cut_date < first:
            return None
        latest_date = max(row["date"] for row in eligible)
        rows = [row for row in eligible if row["date"] == latest_date]
        rows.sort(key=lambda row: (row.get("series_id") or "", row.get("tenor_days") or -1))
        row = rows[0]
        return {**row, "historical_known": "UNKNOWN", "present": True}

    def action_at(self, symbol, cut_date):
        rows = [row for row in self.actions if (symbol is None or row.get("symbol") == symbol)]
        past = [row for row in rows if row.get("ex_date") and row["ex_date"] <= cut_date]
        future = [row for row in rows if row.get("ex_date") and row["ex_date"] > cut_date]
        chosen = max(past, key=lambda row: row["ex_date"]) if past else None
        if chosen is None:
            return {
                "symbol": symbol, "ex_date": None, "dividend": None, "split_ratio": None,
                "announcement_known": False, "future_exdate": bool(future),
            }
        return {
            "symbol": chosen.get("symbol") or symbol,
            "ex_date": chosen["ex_date"],
            "dividend": chosen.get("dividend"),
            "split_ratio": chosen.get("split_ratio"),
            "announcement_known": False,
            "future_exdate": False,
        }


def _cash_symbol(chain):
    return {"NDX": "NDX", "NDXP": "NDX", "QQQ": "QQQ", "SPX": "SPX",
            "SPXW": "SPX", "SPY": "SPY", "VIX": None}.get(chain)


def _etf_symbol(chain):
    return {"QQQ": "QQQ", "SPY": "SPY"}.get(chain)


def _compress_exceptions(exc, chain, family, declared):
    np = _np()
    if exc is None or len(exc["file_id"]) == 0:
        return []
    order = np.lexsort((exc["row_index"], exc["file_id"]))
    fid = exc["file_id"][order]
    row = exc["row_index"][order]
    reason = exc["reason"][order]
    osi = exc["osi"][order]
    exp = exc["expiration"][order]
    strike = exc["strike"][order]
    right = exc["right"][order]
    ts = exc["ts_event_ns"][order]
    rows = []
    start = 0
    n = len(fid)
    while start < n:
        end = start + 1
        while (end < n and fid[end] == fid[start] and reason[end] == reason[start]
               and row[end] == row[end - 1] + 1):
            end += 1
        rows.append({
            "file_id": int(fid[start]), "row_index_start": int(row[start]),
            "row_index_end": int(row[end - 1]), "n_rows": end - start,
            "chain": chain, "source_family": family, "request_date": declared,
            "invalid_reason": reason[start],
            "osi_symbol": osi[start], "expiration": exp[start],
            "strike": None if not math.isfinite(float(strike[start])) else float(strike[start]),
            "right": right[start],
            "ts_event_ns": int(ts[start]) if ts[start] else None,
        })
        start = end
    return rows


def _quality_counts(parsed, unique=False):
    np = _np()
    if parsed is None or len(parsed.get("base_class", [])) == 0:
        return {name: 0 for name in BASE_CLASSES + QUALITY_FLAGS}
    mask = parsed["keep"] if unique and "keep" in parsed else np.ones(len(parsed["base_class"]), dtype=bool)
    cls = parsed["base_class"][mask]
    out = {name: int(np.sum(cls == name)) for name in BASE_CLASSES}
    for name in QUALITY_FLAGS:
        out[name] = int(np.sum(parsed[name][mask])) if name in parsed else 0
    return out


def _source_quality_rows(parsed, chain, declared, family):
    np = _np()
    if parsed is None or len(parsed.get("base_class", [])) == 0:
        return []
    rights = parsed["right"]
    buckets = parsed["dte_bucket"]
    rows = []
    for right in sorted({value for value in rights.tolist() if value is not None} or [None]):
        for bucket in sorted({value for value in buckets.tolist() if value is not None} or [None]):
            mask = np.ones(len(rights), dtype=bool)
            if right is not None:
                mask &= rights == right
            if bucket is not None:
                mask &= buckets == bucket
            if not np.any(mask):
                continue
            subset = {key: value[mask] if hasattr(value, "__len__") and len(value) == len(mask) else value
                      for key, value in parsed.items()}
            raw = _quality_counts(subset, unique=False)
            unique = _quality_counts(subset, unique=True)
            row = {
                "chain": chain, "request_date": declared, "source_family": family,
                "right": right, "dte_bucket": bucket,
                "raw_rows": int(mask.sum()),
                "unique_events": int(subset["keep"].sum()) if "keep" in subset else int(mask.sum()),
                "missing_bid": int(np.sum(subset["bid_null"])),
                "missing_ask": int(np.sum(subset["ask_null"])),
                "missing_bid_size": int(np.sum(subset["bid_size_null"])),
                "missing_ask_size": int(np.sum(subset["ask_size_null"])),
                "missing_ts": int(np.sum(~subset["ts_ok"])),
            }
            for name in BASE_CLASSES:
                row[f"raw_{name}"] = raw[name]
                row[f"unique_{name}"] = unique[name]
            for name in QUALITY_FLAGS:
                row[f"raw_{name}"] = raw[name]
                row[f"unique_{name}"] = unique[name]
            rows.append(row)
    return rows


def _cut_status(*, early_na, missing_file, empty_marker, quoted):
    if early_na:
        return "not_applicable"
    if missing_file:
        return "missing_file"
    if empty_marker:
        return "empty_marker"
    if quoted:
        return "quoted"
    return "no_sample"


def _board_row(*, chain, declared, cut_label, cut_ns, family, parsed, index, oi_state,
               listed, listing_known, cut_status, prev_cash):
    bid = float(parsed["bid"][index]) if math.isfinite(float(parsed["bid"][index])) else None
    ask = float(parsed["ask"][index]) if math.isfinite(float(parsed["ask"][index])) else None
    mid, spread, rel = _mid_spread(bid, ask)
    ts = int(parsed["ts_event_ns"][index]) if parsed["ts_ok"][index] else None
    sample_age = None if ts is None else cut_ns - ts
    run_i = int(parsed["run_start"][index])
    run_ts = int(parsed["ts_event_ns"][run_i]) if parsed["ts_ok"][run_i] else None
    payload_age = None if run_ts is None else cut_ns - run_ts
    s60, s300, s900 = _stale_flags(sample_age)
    p60, p300, p900 = _stale_flags(payload_age)
    cls = parsed["base_class"][index]
    conflict = bool(parsed["conflict"][index] or cls == "conflict")
    usable = bool(parsed["usable"][index] and not conflict)
    return {
        "chain": chain, "request_date": declared, "cut_label": cut_label, "cut_ns": cut_ns,
        "source_family": family, "contract_id": int(parsed["contract_id"][index]),
        "osi_symbol": parsed["osi"][index], "expiration": parsed["expiration"][index],
        "millistrike": int(parsed["millistrike"][index]), "right": parsed["right"][index],
        "dte": int(parsed["dte"][index]) if parsed["dte"][index] != -999 else None,
        "dte_bucket": parsed["dte_bucket"][index],
        "bid": bid, "ask": ask,
        "bid_size": int(parsed["bid_size"][index]), "ask_size": int(parsed["ask_size"][index]),
        "bid_exchange": int(parsed["bid_exchange"][index]),
        "ask_exchange": int(parsed["ask_exchange"][index]),
        "bid_condition": int(parsed["bid_condition"][index]),
        "ask_condition": int(parsed["ask_condition"][index]),
        "mid": mid, "spread": spread, "relative_spread": rel,
        "base_class": cls, "usable": usable, "conflict": conflict,
        "condition_zero": bool(parsed["condition_zero"][index]),
        "nonpositive_size": bool(parsed["nonpositive_size"][index]),
        "negative_size": bool(parsed["negative_size"][index]),
        "zero_bid": bool(parsed["zero_bid"][index]),
        "zero_ask": bool(parsed["zero_ask"][index]),
        "negative_price": bool(parsed["negative_price"][index]),
        "nonfinite_price": bool(parsed["nonfinite_price"][index]),
        "session_outside": bool(parsed["session_outside"][index]),
        "request_date_mismatch": bool(parsed["request_date_mismatch"][index]),
        "ts_event_ns": ts, "sample_age_ns": sample_age,
        "unchanged_payload_age_ns": payload_age,
        "sample_stale_60": s60, "sample_stale_300": s300, "sample_stale_900": s900,
        "payload_stale_60": p60, "payload_stale_300": p300, "payload_stale_900": p900,
        "run_continuity_observed": bool(parsed["run_continuity"][index]),
        "run_lower_bound_ns": run_ts,
        "file_id": int(parsed["file_id"][index]), "row_index": int(parsed["row_index"][index]),
        "run_start_file_id": int(parsed["run_start_file_id"][index]),
        "run_start_row_index": int(parsed["run_start_row_index"][index]),
        "alias_file_id": int(parsed["alias_file_id"][index]) if parsed["alias_file_id"][index] >= 0 else None,
        "alias_row_index": int(parsed["alias_row_index"][index]) if parsed["alias_row_index"][index] >= 0 else None,
        "alias_multiplicity": int(parsed["multiplicity"][index]),
        "listed": listed, "listing_known": listing_known,
        "quoted": True,
        "oi": oi_state["oi"], "oi_available": oi_state["available"],
        "oi_ambiguous": oi_state["ambiguous"], "oi_missing": oi_state["missing"],
        "oi_stale": oi_state["stale"], "oi_expired": oi_state["expired"],
        "oi_zero": oi_state["zero"],
        "received_at_ns": None, "published_at_ns": None, "known_at_ns": None,
        "last_actual_update_ns": None, "actual_update_age_unknown": True,
        "causal_feature_eligible": False, "cut_status": cut_status,
    }


def _listed_unquoted_row(*, chain, declared, cut_label, cut_ns, family, contract_id,
                         listing_known, oi_state, cut_status, identity=None):
    identity = identity or {}
    exp = identity.get("expiration")
    dte = dte_days(exp, declared) if exp and declared else None
    return {
        "chain": chain, "request_date": declared, "cut_label": cut_label, "cut_ns": cut_ns,
        "source_family": family, "contract_id": int(contract_id),
        "osi_symbol": identity.get("osi_symbol"), "expiration": exp,
        "millistrike": identity.get("millistrike"), "right": identity.get("right"),
        "dte": dte, "dte_bucket": quote_dte_bucket(dte),
        "bid": None, "ask": None, "bid_size": None, "ask_size": None,
        "bid_exchange": None, "ask_exchange": None, "bid_condition": None, "ask_condition": None,
        "mid": None, "spread": None, "relative_spread": None,
        "base_class": None, "usable": False, "conflict": False,
        "condition_zero": False, "nonpositive_size": False, "negative_size": False,
        "zero_bid": False, "zero_ask": False, "negative_price": False,
        "nonfinite_price": False, "session_outside": False, "request_date_mismatch": False,
        "ts_event_ns": None, "sample_age_ns": None, "unchanged_payload_age_ns": None,
        "sample_stale_60": None, "sample_stale_300": None, "sample_stale_900": None,
        "payload_stale_60": None, "payload_stale_300": None, "payload_stale_900": None,
        "run_continuity_observed": None, "run_lower_bound_ns": None,
        "file_id": None, "row_index": None, "run_start_file_id": None,
        "run_start_row_index": None, "alias_file_id": None, "alias_row_index": None,
        "alias_multiplicity": None,
        "listed": True if listing_known else None, "listing_known": listing_known,
        "quoted": False, "oi": oi_state["oi"], "oi_available": oi_state["available"],
        "oi_ambiguous": oi_state["ambiguous"], "oi_missing": oi_state["missing"],
        "oi_stale": oi_state["stale"], "oi_expired": oi_state["expired"],
        "oi_zero": oi_state["zero"],
        "received_at_ns": None, "published_at_ns": None, "known_at_ns": None,
        "last_actual_update_ns": None, "actual_update_age_unknown": True,
        "causal_feature_eligible": False, "cut_status": cut_status,
    }


def _support_row(chain, declared, cut_label, cut_ns, support, *, at_close, prior_date):
    cash_sym = _cash_symbol(chain)
    etf_sym = _etf_symbol(chain)
    etf = support.etf_at(etf_sym, cut_ns) if etf_sym else None
    cash = support.cash_at(cash_sym, declared, at_or_after_close=at_close, prior_date=prior_date) if cash_sym else None
    fred = support.fred_at(declared)
    action_sym = etf_sym or cash_sym
    action = support.action_at(action_sym, declared)
    return {
        "chain": chain, "request_date": declared, "cut_label": cut_label, "cut_ns": cut_ns,
        "etf_present": etf is not None, "etf_symbol": etf_sym,
        "etf_t_ns": None if etf is None else etf["t_ns"],
        "etf_open": None if etf is None else etf["open"],
        "etf_high": None if etf is None else etf["high"],
        "etf_low": None if etf is None else etf["low"],
        "etf_close": None if etf is None else etf["close"],
        "etf_volume": None if etf is None else etf["volume"],
        "etf_age_ns": None if etf is None else etf["age_ns"],
        "etf_gap": None if etf is None else etf["gap"],
        "etf_assumption": None if etf is None else etf["assumption"],
        "cash_symbol": cash_sym,
        "cash_date": None if cash is None else cash["date"],
        "cash_close": None if cash is None else cash["close"],
        "cash_adjusted_close": None if cash is None else cash["adjusted_close"],
        "cash_same_date": None if cash is None else cash["same_date"],
        "cash_assumption": None if cash is None else cash["assumption"],
        "vix_cash_unavailable": chain == "VIX",
        "fred_date": None if fred is None else fred["date"],
        "fred_series_id": None if fred is None else fred["series_id"],
        "fred_tenor_days": None if fred is None else fred["tenor_days"],
        "fred_rate_pct": None if fred is None else fred["rate_pct"],
        "fred_realtime_start": None if fred is None else fred["realtime_start"],
        "fred_realtime_end": None if fred is None else fred["realtime_end"],
        "fred_historical_known": "UNKNOWN",
        "fred_present": fred is not None,
        "action_symbol": None if action is None else action["symbol"],
        "action_ex_date": None if action is None else action["ex_date"],
        "action_dividend": None if action is None else action["dividend"],
        "action_split_ratio": None if action is None else action["split_ratio"],
        "action_announcement_known": False,
        "action_future_exdate": False if action is None else action["future_exdate"],
        "causal_feature_eligible": False,
    }


def _coverage_row(*, chain, declared, cut_label, family, intended, session, missing_file,
                  empty_marker, early_na, board_rows, listing_known, listing_unavailable,
                  oi_unavailable, listed_ids):
    np = _np()
    quoted = [row for row in board_rows if row["quoted"]]
    listed_quoted = [row for row in quoted if row["listed"] is True]
    quoted_unlisted = [row for row in quoted if row["listed"] is False]
    listed_unquoted = [row for row in board_rows if row["listed"] is True and not row["quoted"]]
    oi_avail = [row for row in board_rows if row["oi_available"]]
    oi_missing = [row for row in board_rows if row["oi_missing"]]
    oi_amb = [row for row in board_rows if row["oi_ambiguous"]]
    oi_zero = [row for row in board_rows if row["oi_zero"]]
    total = sum(int(row["oi"]) for row in oi_avail if row["oi"] is not None and row["oi"] >= 0)
    quoted_oi = sum(int(row["oi"]) for row in listed_quoted if row["oi_available"] and row["oi"] is not None and row["oi"] >= 0)
    weighted = None if total <= 0 else quoted_oi / total
    classes = {name: 0 for name in BASE_CLASSES}
    for row in quoted:
        if row["base_class"] in classes:
            classes[row["base_class"]] += 1
    return {
        "chain": chain, "request_date": declared, "cut_label": cut_label,
        "source_family": family, "intended": intended,
        "closed": session.state == "closed", "early_close": session.state == "early_close",
        "session_state": session.state,
        "file_present": not missing_file, "empty_marker": empty_marker,
        "missing_file": missing_file,
        "cut_status": _cut_status(early_na=early_na, missing_file=missing_file,
                                  empty_marker=empty_marker, quoted=bool(quoted)),
        "listed_count": None if not listing_known else (0 if listed_ids is None else int(len(listed_ids))),
        "quoted_count": len(quoted),
        "listed_unquoted": len(listed_unquoted),
        "quoted_unlisted": len(quoted_unlisted),
        "usable_count": sum(1 for row in quoted if row["usable"]),
        "conflict_count": classes["conflict"],
        "invalid_count": classes["invalid_identity"] + classes["invalid_clock"] + classes["invalid_numeric"],
        "all_zero_count": classes["all_zero"], "one_sided_count": classes["one_sided"],
        "crossed_count": classes["crossed"], "locked_count": classes["locked"],
        "two_sided_count": classes["two_sided"],
        "oi_available_count": len(oi_avail), "oi_missing_count": len(oi_missing),
        "oi_ambiguous_count": len(oi_amb), "oi_zero_count": len(oi_zero),
        "oi_amount_unknown": sum(1 for row in board_rows if row["oi"] is None and row["oi_missing"]),
        "oi_total_available": total,
        "oi_weighted_quoted_fraction": weighted,
        "listing_known": listing_known, "vix_listing_unknown": chain in CHAINS_WITHOUT_LISTING,
        "listing_unavailable": listing_unavailable, "oi_unavailable": oi_unavailable,
        "gt60_dte_listed": sum(1 for row in board_rows if row.get("dte_bucket") == "61+" and row["listed"] is True),
        "no_sample": 0 if quoted else 1,
        "causal_feature_eligible": False,
    }


def _date_aggregate(chain, declared, intended, session, family_quality, coverage_rows, board_rows, support_rows):
    raw_rows = sum(row["raw_rows"] for row in family_quality)
    unique_events = sum(row["unique_events"] for row in family_quality)
    quotes = [row for row in board_rows if row["quoted"]]
    usable = [row for row in quotes if row["usable"] and row["mid"] is not None]
    bids = [row["bid"] for row in usable if row["bid"] is not None]
    asks = [row["ask"] for row in usable if row["ask"] is not None]
    mids = [row["mid"] for row in usable if row["mid"] is not None and row["mid"] > 0]
    spreads = [row["spread"] for row in usable if row["spread"] is not None]
    rels = [row["relative_spread"] for row in usable if row["relative_spread"] is not None]
    sample_ages = [row["sample_age_ns"] / NS for row in quotes if row["sample_age_ns"] is not None]
    payload_ages = [row["unchanged_payload_age_ns"] / NS for row in quotes
                    if row["unchanged_payload_age_ns"] is not None]
    return {
        "chain": chain, "request_date": declared, "intended": intended,
        "session_state": session.state,
        "raw_rows": raw_rows, "unique_events": unique_events,
        "cut_board_rows": len(board_rows),
        "quoted_contracts": len({row["contract_id"] for row in quotes}),
        "listed_contracts": len({row["contract_id"] for row in board_rows if row["listed"] is True}),
        "oi_matched_contracts": len({row["contract_id"] for row in board_rows if row["oi_available"]}),
        "usable_quotes": len(usable),
        "mean_bid": None if not bids else sum(bids) / len(bids),
        "mean_ask": None if not asks else sum(asks) / len(asks),
        "mean_mid": None if not mids else sum(mids) / len(mids),
        "mean_spread": None if not spreads else sum(spreads) / len(spreads),
        "mean_relative_spread": None if not rels else sum(rels) / len(rels),
        "mean_sample_age_s": None if not sample_ages else sum(sample_ages) / len(sample_ages),
        "mean_payload_age_s": None if not payload_ages else sum(payload_ages) / len(payload_ages),
        "raw_bid_sum": sum(bids), "raw_bid_n": len(bids),
        "quality": family_quality, "coverage": coverage_rows, "support": support_rows,
        "by_cut": {label: {
            "quoted": sum(1 for row in quotes if row["cut_label"] == label),
            "usable": sum(1 for row in usable if row["cut_label"] == label),
            "conflict": sum(1 for row in quotes if row["cut_label"] == label and row["conflict"]),
            "listed_unquoted": sum(1 for row in board_rows if row["cut_label"] == label and row["listed"] is True and not row["quoted"]),
        } for label in ALL_CUTS},
        "by_right": {},
        "by_dte": {},
        "paired_near_broad": _paired_stats(board_rows),
    }


def _paired_stats(board_rows):
    near = {(row["contract_id"], row["cut_label"]): row for row in board_rows
            if row["source_family"] == "near" and row["quoted"]}
    broad = {(row["contract_id"], row["cut_label"]): row for row in board_rows
             if row["source_family"] == "broad" and row["quoted"]}
    common = set(near) & set(broad)
    agree = 0
    conflict = 0
    for key in common:
        a, b = near[key], broad[key]
        if a["conflict"] or b["conflict"]:
            conflict += 1
            continue
        if a["bid"] == b["bid"] and a["ask"] == b["ask"] and a["bid_size"] == b["bid_size"] and a["ask_size"] == b["ask_size"]:
            agree += 1
        else:
            conflict += 1
    return {
        "common": len(common), "agree": agree, "conflict": conflict,
        "near_only": len(set(near) - set(broad)), "broad_only": len(set(broad) - set(near)),
    }


def run(*, protocol, admitted, oi_population, store, outputs, selected_dates=None,
        selected_chains=None):
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError("registered BoundedOutputs required")
    if store is not None and not isinstance(store, ArtifactStore):
        raise ContractError("store must be an existing ArtifactStore")
    started_wall, started_cpu = pytime.perf_counter(), pytime.process_time()
    spec = contract(protocol)
    calendar, calendar_ref = load_calendar(protocol)
    population, stages = spec["population"], spec["population"]["stages"]
    chains = tuple(population["chains"])
    if selected_chains is not None:
        if type(selected_chains) is not list or any(type(item) is not str for item in selected_chains):
            raise ContractError("selected_chains must be chain-name strings or None")
        if len(set(selected_chains)) != len(selected_chains):
            raise ContractError("selected_chains contains duplicates")
        work_chains = tuple(selected_chains)
    else:
        work_chains = chains
    intended_all = intended_cash_dates(calendar, population["first_date"], population["last_date"])
    intended_labels, prev_map = build_calendar_index(intended_all)
    intended_label_set = set(intended_labels)
    if selected_dates is not None:
        if type(selected_dates) is not list or any(type(item) is not str for item in selected_dates):
            raise ContractError("selected_dates must be ISO date strings or None")
        if len(set(selected_dates)) != len(selected_dates):
            raise ContractError("selected_dates contains duplicates")
    sources, required_ids = _validate_admitted(admitted, protocol, selected_dates, selected_chains)
    schemas = admitted.get("schemas")
    if not isinstance(schemas, dict):
        raise ContractError("admitted schemas mapping required")
    selected_set = None if selected_dates is None else set(selected_dates)
    impl_hashes = implementation_hashes()
    sci_hash = scientific_hash(protocol)
    binding = {
        "protocol_scientific_hash": sci_hash,
        "implementation_hashes": impl_hashes,
        "selected_dates": selected_dates,
        "selected_chains": list(work_chains),
        "admitted_kind": admitted.get("kind"),
        "admitted_source_files": admitted.get("source_files"),
        "oi_ref": None if oi_population is None else {
            "family": oi_population.get("family"), "version": oi_population.get("version"),
            "refs": {name: (oi_population.get("refs") or {}).get(name)
                     for name in ("identity_map", "reports", "asof_intervals", "coverage")},
        },
    }
    if store is not None:
        store.put_json(binding, kind="options_quote_run_binding_v1")

    oi_cpu = pytime.process_time()
    oi_join = OIJoinAdapter(oi_population)
    support = SupportStore()
    quote_by = {chain: defaultdict(lambda: defaultdict(list)) for chain in work_chains}
    support_records = []
    for record in sources:
        if _is_support_record(record):
            support_records.append(record)
            continue
        if not _is_quote_record(record):
            raise ContractError("admitted source is neither quote nor declared support")
        source = record["source"]
        if source["chain"] not in work_chains:
            continue
        if selected_set is not None and source["request_date"] not in selected_set:
            continue
        quote_by[source["chain"]][source["request_date"]][_source_family(record)].append(record)
    for record in support_records:
        table, meta = read_admitted_support(protocol, record)
        support.add_table(_source_family(record), table, record)
    support.finalize()
    oi_support_cpu = pytime.process_time() - oi_cpu

    admit_w = ArrayWriter(outputs, "admission", admission_schema(), OUTPUT_SCHEMAS["admission"])
    except_w = ArrayWriter(outputs, "exceptions", exception_schema(), OUTPUT_SCHEMAS["exceptions"])
    alias_w = ArrayWriter(outputs, "alias-conflict", alias_conflict_schema(), OUTPUT_SCHEMAS["alias_conflict"])
    board_w = ArrayWriter(outputs, "cut-board", cut_board_schema(), OUTPUT_SCHEMAS["cut_board"])
    quality_w = ArrayWriter(outputs, "source-quality", source_quality_schema(), OUTPUT_SCHEMAS["source_quality"])
    support_w = ArrayWriter(outputs, "underlier-support", underlier_support_schema(), OUTPUT_SCHEMAS["underlier_support"])
    ident_w = ArrayWriter(outputs, "identity-match", identity_match_schema(), OUTPUT_SCHEMAS["identity_match"])

    codebook = QuoteCodebook(oi_join.identity, next_id=oi_join.max_id + 1)
    dates, clocks = DateCodebook(), ClockMaps()
    coverage_rows, date_aggregates, consumed, manifest = [], [], set(), []
    files_read = rows_read = bytes_read = 0
    source_dates = []
    research_cut = local_timestamp(date(2026, 9, 4), time(0), calendar.zone)
    parse_cpu_start = pytime.process_time()
    np = _np()
    selected_or_all = intended_all if selected_dates is None else tuple(date.fromisoformat(d) for d in selected_dates)

    for chain in work_chains:
        listing_known = chain not in CHAINS_WITHOUT_LISTING and oi_join.available
        for day in selected_or_all:
            label = day.isoformat()
            intended = label in intended_label_set
            session = calendar.resolve(day, cut=research_cut)
            closed = session.state == "closed"
            files = quote_by[chain].get(label, {})
            family_parsed = {}
            family_meta = {}
            day_exceptions = []
            quality_rows = []
            for family in QUOTE_FAMILIES:
                records = files.get(family, [])
                if not records:
                    family_meta[family] = {"present": False, "empty": False, "rows": 0}
                    continue
                parts, empty_any = [], False
                for record in records:
                    table, meta = read_admitted_quote(protocol, record, schemas)
                    consumed.add(record["file_id"])
                    files_read += 1
                    rows_read += meta["rows"]
                    bytes_read += meta["size_bytes"]
                    source_dates.append(label)
                    manifest.append({
                        "file_id": record["file_id"], "path": record["source"]["path"],
                        "sha256": record["sha256"], "size_bytes": meta["size_bytes"],
                        "chain": chain, "source_family": family,
                        "request_date": label, "rows": meta["rows"],
                        "empty_marker": meta["empty_marker"],
                    })
                    admit_w.write_table(_table(admission_schema(), [{
                        "file_id": record["file_id"], "path": record["source"]["path"],
                        "sha256": record["sha256"], "dataset_id": record["source"].get("dataset_id"),
                        "chain": chain, "source_family": family,
                        "role": record["source"].get("role") or "quote",
                        "request_date": label, "bytes": meta["size_bytes"],
                        "rows": meta["rows"], "schema_id": record.get("schema_id"),
                        "empty_marker": meta["empty_marker"], "format": record["format"],
                    }]))
                    if meta["empty_marker"]:
                        empty_any = True
                        continue
                    parsed, exc, n_read = parse_quote_typed(
                        table, record=record, schema_str=schemas.get(record["schema_id"]),
                        dates=dates, clocks=clocks,
                        session_open_ns=session.open_at, session_close_ns=session.close_at,
                    )
                    day_exceptions.extend(_compress_exceptions(exc, chain, family, label))
                    if len(parsed["osi"]):
                        parts.append(parsed)
                if not parts:
                    family_meta[family] = {"present": True, "empty": empty_any, "rows": 0}
                    family_parsed[family] = None
                    continue
                merged = _concat_parsed(parts)
                cid, matched = codebook.intern(
                    chain, merged["osi"], merged["expiration"], merged["millistrike"], merged["right"])
                merged["oi_matched"] = matched
                family_parsed[family] = sort_and_dedup(merged, cid)
                family_meta[family] = {"present": True, "empty": empty_any,
                                       "rows": len(merged["base_class"])}
                quality_rows.extend(_source_quality_rows(family_parsed[family], chain, label, family))
            owned, alias_rows = union_families(family_parsed)
            if alias_rows:
                alias_w.write_table(_table(alias_conflict_schema(), alias_rows))
            if day_exceptions:
                except_w.write_table(_table(exception_schema(), day_exceptions))
            if quality_rows:
                quality_w.write_table(_table(source_quality_schema(), quality_rows))
            ident_table = codebook.flush_tables(chain)
            if ident_table is not None:
                ident_w.write_table(ident_table)

            listed_ids = oi_join.listed_ids(chain, label)
            prev_cash = prev_map.get(label)
            day_boards = []
            day_coverage = []
            day_support = []
            expected_own = ("vix_full",) if chain == "VIX" else ("near", "broad")
            families_for_cuts = list(expected_own)
            if "union" in owned or chain != "VIX":
                families_for_cuts.append("union")
            for cut_label in ALL_CUTS:
                if cut_label == "cash_close":
                    cut_at = session.close_at
                    early_na = session.state == "closed" or cut_at is None
                elif cut_label == "15:00_utc":
                    cut_at = utc_cut_ns(day, "15:00")
                    early_na = session.state == "closed"
                elif cut_label == "15:00" and session.state == "early_close":
                    cut_at = cut_ns_on(day, "15:00")
                    early_na = True
                else:
                    cut_at = None if session.state == "closed" else cut_ns_on(day, cut_label)
                    early_na = session.state == "closed" or cut_at is None
                at_close = cut_label == "cash_close" and not early_na
                for family in families_for_cuts:
                    missing = not family_meta.get(family, {}).get("present", False) and family != "union"
                    empty_marker = bool(family_meta.get(family, {}).get("empty"))
                    parsed = owned.get(family)
                    chosen = None if early_na or parsed is None else select_cut_rows(
                        parsed, cut_ns=cut_at, cut_date=label, session_open_ns=session.open_at)
                    board = []
                    quoted_ids = set()
                    if chosen is not None and not early_na:
                        for index in chosen.tolist():
                            cid = int(parsed["contract_id"][index])
                            quoted_ids.add(cid)
                            listed = None
                            if listing_known and listed_ids is not None:
                                listed = bool(np.any(listed_ids == cid)) if len(listed_ids) else False
                            elif chain in CHAINS_WITHOUT_LISTING:
                                listed = None
                            oi_state = oi_join.asof_oi(chain, cid, cut_at, label, prev_cash)
                            board.append(_board_row(
                                chain=chain, declared=label, cut_label=cut_label, cut_ns=cut_at,
                                family=family, parsed=parsed, index=index, oi_state=oi_state,
                                listed=listed, listing_known=listing_known,
                                cut_status=_cut_status(early_na=False, missing_file=missing,
                                                       empty_marker=empty_marker, quoted=True),
                                prev_cash=prev_cash,
                            ))
                    if listing_known and listed_ids is not None and not early_na:
                        for cid in listed_ids.tolist():
                            if int(cid) in quoted_ids:
                                continue
                            oi_state = oi_join.asof_oi(chain, int(cid), cut_at, label, prev_cash)
                            board.append(_listed_unquoted_row(
                                chain=chain, declared=label, cut_label=cut_label, cut_ns=cut_at,
                                family=family, contract_id=int(cid), listing_known=True,
                                oi_state=oi_state,
                                cut_status=_cut_status(early_na=False, missing_file=missing,
                                                       empty_marker=empty_marker, quoted=False),
                                identity=oi_join.identity_fields(int(cid)),
                            ))
                    if board:
                        board_w.write_table(_table(cut_board_schema(), board))
                    day_boards.extend(board)
                    day_coverage.append(_coverage_row(
                        chain=chain, declared=label, cut_label=cut_label, family=family,
                        intended=intended, session=session, missing_file=missing,
                        empty_marker=empty_marker, early_na=early_na, board_rows=board,
                        listing_known=listing_known,
                        listing_unavailable=oi_join.listing_unavailable,
                        oi_unavailable=not oi_join.available,
                        listed_ids=listed_ids,
                    ))
                    if not early_na and cut_at is not None:
                        day_support.append(_support_row(
                            chain, label, cut_label, cut_at, support,
                            at_close=at_close, prior_date=prev_cash,
                        ))
            if day_coverage:
                coverage_rows.extend(day_coverage)
            if day_support:
                support_w.write_table(_table(underlier_support_schema(), day_support))
            date_aggregates.append(_date_aggregate(
                chain, label, intended, session, quality_rows, day_coverage, day_boards, day_support,
            ))

    parse_cpu = pytime.process_time() - parse_cpu_start
    leftover = required_ids and (consumed != set(required_ids))
    if leftover:
        unread = set(required_ids) - consumed
        unread_quote = []
        for record in sources:
            if record["file_id"] in unread and _is_quote_record(record):
                unread_quote.append(record["file_id"])
        if unread_quote:
            raise IntegrityError("membership does not match all selected admitted quote records")
    reconstruction = {
        "kind": OUTPUT_SCHEMAS["reconstruction"],
        "predicate": INTERVAL_RECONSTRUCTION,
        "output_schemas": OUTPUT_SCHEMAS,
        "sort": "contract_id, ts_event_ns, file_id, row_index",
        "dedup": "source_family then union; identical 8-field payload is alias; difference is conflict with no winner",
        "storage": "cut boards plus source/hash ledger reconstruct sampled history; interval tape is not required",
        "clocks": {
            "ts_event_ns": "exact recorded sampling/source clock",
            "received_at_ns": None, "published_at_ns": None, "known_at_ns": None,
            "last_actual_update_ns": None, "causal_feature_eligible": False,
            "actual_update_age_unknown": True,
        },
    }
    return finish_quote_outputs(
        outputs, spec=spec, calendar_ref=calendar_ref,
        admit_w=admit_w, except_w=except_w, alias_w=alias_w, board_w=board_w,
        quality_w=quality_w, support_w=support_w, ident_w=ident_w,
        coverage_rows=coverage_rows, date_aggregates=date_aggregates,
        consumed=consumed, required_ids=required_ids, manifest=manifest,
        files_read=files_read, rows_read=rows_read, bytes_read=bytes_read,
        source_dates=source_dates, selected_dates=selected_dates,
        selected_chains=list(work_chains), intended_all=intended_all,
        intended_labels=intended_labels, chains=work_chains,
        started_cpu=started_cpu, started_wall=started_wall,
        reconstruction_payload=reconstruction,
        family=FAMILY, version=VERSION, remaining=REMAINING,
        sci_hash=sci_hash, impl_hashes=impl_hashes, binding=binding,
        oi_identity=binding["oi_ref"],
        parse_cpu=parse_cpu, oi_support_cpu=oi_support_cpu,
        listing_unknown_chains=sorted(CHAINS_WITHOUT_LISTING),
        joined_coverage_complete=bool(oi_join.available) and not oi_join.listing_unavailable,
        max_worker_bytes=int(spec.get("resources", {}).get("memory_bytes", MAX_WORKER_BYTES)),
        max_source_file=int(spec.get("resources", {}).get("maximum_source_file_bytes", MAX_SOURCE_FILE)),
    )


def _load_result_json(ref, load_reference):
    if load_reference is not None:
        return load_reference(ref)
    if isinstance(ref, dict) and ref.get("encoding") == "canonical-json-zstd-v1":
        return read_json_artifact(ref)
    path = Path(ref["path"])
    if ref.get("sha256") and file_digest(path) != ref["sha256"]:
        raise IntegrityError("referenced result artifact hash changed")
    return json.loads(path.read_text())


def combine_partition_results(*, protocol, results, outputs, load_reference):
    """Authenticate complete chain partitions and combine without re-reading quotes."""
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError("registered BoundedOutputs required")
    if type(results) is not list or len(results) < 1:
        raise ContractError("combine requires a list of partition results")
    spec = contract(protocol)
    sci = scientific_hash(protocol)
    impl = implementation_hashes()
    owned = {}
    combined_dates = []
    combined_chains = []
    coverage_all, aggregates_all = [], []
    counts = defaultdict(int)
    oi_ref = None
    group_refs = {}
    for result in results:
        if not isinstance(result, dict):
            raise ContractError("each partition result must be a mapping")
        if result.get("protocol_scientific_hash") != sci:
            raise IntegrityError("partition protocol scientific hash does not match")
        if result.get("implementation_hashes") != impl:
            raise IntegrityError("partition implementation hashes do not match")
        dates = list(result.get("selected_dates") or [])
        chains = list(result.get("selected_chains") or [])
        if not chains:
            raise ContractError("partition result must bind selected_chains")
        for chain in chains:
            for day in dates:
                key = (chain, day)
                if key in owned:
                    raise IntegrityError("duplicate chain/date ownership")
                owned[key] = True
        if oi_ref is None:
            oi_ref = result.get("oi_population_identity")
        elif result.get("oi_population_identity") != oi_ref:
            raise IntegrityError("mixed OI population identities")
        refs = result.get("refs") or {}
        if refs.get("date_aggregates"):
            aggregates_all.extend(_load_result_json(refs["date_aggregates"], load_reference))
        if refs.get("coverage"):
            import pyarrow.parquet as pq
            coverage_all.append(pq.read_table(refs["coverage"]["path"]))
        for name in ("source_files_read", "source_rows_read", "source_bytes_read",
                     "cut_board_rows", "exception_rows", "coverage_rows"):
            counts[name] += int((result.get("counts") or {}).get(name) or 0)
        if refs.get("statistics"):
            for chain in chains:
                if chain in group_refs:
                    raise IntegrityError("duplicate chain statistics ownership")
                group_refs[chain] = refs["statistics"]
        combined_dates.extend(dates)
        combined_chains.extend(chains)
    combined_dates = sorted(set(combined_dates))
    combined_chains = [chain for chain in spec["population"]["chains"] if chain in set(combined_chains)]
    intended_all = intended_cash_dates(*((load_calendar(protocol)[0], spec["population"]["first_date"],
                                         spec["population"]["last_date"])))
    intended_labels = [day.isoformat() for day in intended_all]
    from trading_research.research.options_quote_statistics import run_statistics
    if coverage_all:
        import pyarrow.parquet as pq
        coverage = _pa().concat_tables(coverage_all)
        stream = outputs.create("coverage.parquet")
        try:
            pq.write_table(coverage, stream, compression="zstd")
        finally:
            stream.close()
        coverage_ref = {**outputs.reference("coverage.parquet", kind=OUTPUT_SCHEMAS["coverage"]),
                        "rows": len(coverage)}
    else:
        coverage_ref = None
    aggregates_ref = outputs.json("date-aggregates.json", aggregates_all,
                                  kind=OUTPUT_SCHEMAS["date_aggregates"])
    stats = run_statistics(
        aggregates_all, protocol=spec, outputs=outputs,
        intended_all=intended_labels, selected_dates=combined_dates,
        chains=combined_chains, stages=spec["population"]["stages"],
        read_counts=dict(counts), output_refs={"coverage": coverage_ref, "groups": group_refs},
        group_refs=group_refs,
    )
    binding = {
        "protocol_scientific_hash": sci,
        "implementation_hashes": impl,
        "selected_dates": combined_dates,
        "selected_chains": combined_chains,
        "oi_ref": oi_ref,
        "partition_count": len(results),
        "combined": True,
    }
    return {
        "passed": True,
        "full_family_complete": False,
        "family": FAMILY,
        "version": VERSION,
        "protocol_scientific_hash": sci,
        "implementation_hashes": impl,
        "selected_dates": combined_dates,
        "selected_chains": combined_chains,
        "oi_population_identity": oi_ref,
        "refs": {
            "coverage": coverage_ref,
            "date_aggregates": aggregates_ref,
            "statistics": stats["refs"]["statistics"],
            "distributions": stats["refs"]["distributions"],
            "results_md": stats["refs"]["results_md"],
            "chain_groups": group_refs,
        },
        "counts": dict(counts),
        "groups": stats["groups"],
        "binding": binding,
        "remaining_dependencies": list(REMAINING),
    }


__all__ = [
    "ALL_CUTS", "BASE_CLASSES", "CONTRACT_KIND", "DTE_BUCKETS", "FAMILY",
    "INTERVAL_RECONSTRUCTION", "OUTPUT_SCHEMAS", "QUALITY_FLAGS", "VERSION",
    "combine_partition_results", "contract", "implementation_hashes",
    "load_calendar", "quote_dte_bucket", "run", "scientific_hash", "utc_cut_ns",
]
