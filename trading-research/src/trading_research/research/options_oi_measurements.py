"""Options OI report/lifecycle measurement (columnar production path).

Source-clock scenarios only. Verified known_at/received_at/published_at and
position_date stay NULL; causal_feature_eligible is always false. Typed
label_ledger.OIReport / oi_endpoint and OIReportChanges are not used.

Valid source rows stay in the authenticated original files (file_id+row_index).
Invalid rows go to an exceptions ledger. As-of state is an interval ledger with
documented reconstruction. Quotes, IV, flow, Greeks, dealer ownership and
Context remain separate.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, time, timedelta
from pathlib import Path
import bisect
import hashlib
import json
import math
import time as pytime

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.options_oi_statistics import finish_measurement_outputs


VERSION = "options-oi-report-lifecycle-measurement-v2"
FAMILY = "Research-Options-OI-report-lifecycle-v1"
ADMITTED_KIND = "options_oi_admitted_sources_v1"
CONTRACT_KIND = "options_oi_report_lifecycle_contract_v1"
ZONE = "America/New_York"
DEFAULT_DATA_ROOT = "/workspace/data"
MAX_SOURCE_FILE = 16 * 1024 * 1024
MAX_WORKER_BYTES = 4 * 1024 ** 3
STREAM_ROWS = 65536
RIGHTS = {"C": "CALL", "P": "PUT", "CALL": "CALL", "PUT": "PUT"}
DTE_BUCKETS = ("expired", "0", "1", "2-7", "8-30", "31-60", "61+")
CHAINS_WITHOUT_LISTING = frozenset({"VIX"})
REMAINING = (
    "quotes_iv_and_greeks_remain_separate",
    "option_flow_and_exposures_remain_separate",
    "futures_options_source_statistics_remain_separate",
    "no_dealer_ownership_or_settlement_multiplier",
    "no_certified_as_known_listing_universe",
    "no_context_fit",
)
CONTRACT_FIELDS = ("symbol", "expiration", "strike", "right", "request_date", "osi_symbol")
OI_FIELDS = CONTRACT_FIELDS + ("open_interest", "ts_event")
INTERVAL_RECONSTRUCTION = (
    "An interval is visible at sourceclock cut_ns on cut_date iff "
    "valid_from_ns <= cut_ns and (valid_to_ns is null or cut_ns < valid_to_ns) "
    "and request_date <= cut_date and (expiration is null or expiration >= cut_date). "
    "Same-time conflict opens an ambiguous interval with no earlier fallback. "
    "Late observations stay pending until a later cut. valid_from_ns is the later of "
    "the source clock and request midnight; older reobserved clocks never replace a newer state. "
    "known_at/received_at/published_at/position_date remain NULL; "
    "causal_feature_eligible is false; ts_event is a model assumption only."
)
OUTPUT_SCHEMAS = {
    "identity_map": "options_oi_identity_map_v2",
    "exceptions": "options_oi_exceptions_v2",
    "membership": "options_oi_membership_v2",
    "reports": "options_oi_resolved_reports_v2",
    "lifecycle": "options_oi_lifecycle_v2",
    "asof_intervals": "options_oi_asof_intervals_v2",
    "asof_aggregates": "options_oi_asof_aggregates_v2",
    "coverage": "options_oi_coverage_v2",
    "reconstruction": "options_oi_asof_reconstruction_v2",
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
    raise ContractError("options OI report/lifecycle contract required")


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


_CALENDAR_DATE_CACHE = {}


def intended_cash_dates(calendar, first, last):
    if type(first) is str:
        first = date.fromisoformat(first)
    if type(last) is str:
        last = date.fromisoformat(last)
    key = (getattr(calendar, "version", None) or id(calendar),
           getattr(calendar, "timezone_version", None),
           first.isoformat(), last.isoformat())
    cached = _CALENDAR_DATE_CACHE.get(key)
    if cached is not None:
        return cached
    cut = local_timestamp(date(2026, 9, 4), time(0), calendar.zone)
    out = []
    day = first
    while day <= last:
        if calendar.resolve(day, cut=cut).state != "closed":
            out.append(day)
        day += timedelta(days=1)
    result = tuple(out)
    _CALENDAR_DATE_CACHE[key] = result
    return result


def previous_intended(intended, day):
    if type(day) is str:
        day = date.fromisoformat(day)
    keys = [item if type(item) is date else date.fromisoformat(item) for item in intended]
    index = bisect.bisect_left(keys, day)
    return keys[index - 1] if index else None


def build_calendar_index(intended):
    labels = [item.isoformat() if type(item) is date else item for item in intended]
    prev = {labels[0]: None} if labels else {}
    for i in range(1, len(labels)):
        prev[labels[i]] = labels[i - 1]
    return tuple(labels), prev


def stage_of(day, stages):
    label = day.isoformat() if type(day) is date else day
    hits = [name for name, bounds in stages.items() if bounds[0] <= label < bounds[1]]
    return hits[0] if len(hits) == 1 else None


def dte_days(expiration, request_date):
    if type(expiration) is str:
        expiration = date.fromisoformat(expiration)
    if type(request_date) is str:
        request_date = date.fromisoformat(request_date)
    return (expiration - request_date).days


def dte_bucket(days):
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
    if days <= 30:
        return "8-30"
    if days <= 60:
        return "31-60"
    return "61+"


def normalize_right(value):
    if type(value) is not str:
        return None
    return RIGHTS.get(value.strip().upper())


def parse_osi(osi):
    if type(osi) is not str or len(osi) != 21:
        return None
    root, yymmdd, cp, strike_s = osi[:6].rstrip(), osi[6:12], osi[12], osi[13:21]
    if not yymmdd.isdigit() or cp not in "CP" or not strike_s.isdigit():
        return None
    yy, mm, dd = int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:6])
    try:
        exp = date(2000 + yy if yy < 80 else 1900 + yy, mm, dd)
    except ValueError:
        return None
    return {"root": root, "expiration": exp.isoformat(), "right": "CALL" if cp == "C" else "PUT",
            "millistrike": int(strike_s), "strike": int(strike_s) / 1000.0}


def millistrike(value):
    if value is None or isinstance(value, bool):
        return None
    if type(value) is int:
        return value * 1000
    if type(value) is not float or not math.isfinite(value):
        return None
    scaled = value * 1000.0
    nearest = int(round(scaled))
    if scaled != float(nearest):
        return None
    return nearest


def contract_key(chain, osi, expiration, strike, right):
    return (chain, osi, expiration, millistrike(strike), right)


def timestamp_ns_from_arrow(column):
    """Cast Arrow timestamp[ns] directly to int64. Never via datetime, float, or us."""
    pa = _pa()
    if column is None:
        return None
    if pa.types.is_timestamp(column.type):
        if column.type.unit != "ns":
            raise ContractError("ts_event unit must be nanoseconds")
        return column.cast(pa.int64())
    raise ContractError("ts_event must be an Arrow timestamp[ns]; integer columns are not a unit")


def _date_strings(column):
    pa, pc = _pa(), _pc()
    if column is None:
        return None
    if pa.types.is_date(column.type):
        return pc.strftime(column, format="%Y-%m-%d")
    if pa.types.is_string(column.type) or pa.types.is_large_string(column.type):
        return column
    raise ContractError("date columns must be Arrow date32 or string")


def eastern_date_from_ns(ns_values):
    pa, pc = _pa(), _pc()
    arr = pa.array(ns_values, type=pa.int64())
    local = arr.cast(pa.timestamp("ns", tz="UTC")).cast(pa.timestamp("ns", tz=ZONE))
    return pc.strftime(local, format="%Y-%m-%d").to_pylist()


def utc_date_from_ns(ns_values):
    pa, pc = _pa(), _pc()
    arr = pa.array(ns_values, type=pa.int64())
    return pc.strftime(arr.cast(pa.timestamp("ns", tz="UTC")), format="%Y-%m-%d").to_pylist()


def _map_unique_int64(values, batch_fn):
    np = _np()
    out = [None] * len(values)
    present = [i for i, value in enumerate(values) if value is not None]
    if not present:
        return out
    arr = np.fromiter((int(values[i]) for i in present), dtype=np.int64, count=len(present))
    uniq, inverse = np.unique(arr, return_inverse=True)
    mapped = batch_fn(uniq.tolist())
    for offset, index in enumerate(present):
        out[index] = mapped[int(inverse[offset])]
    return out


def map_unique_eastern(ts_ns):
    """One Arrow timezone pass over unique timestamps, not per row."""
    return _map_unique_int64(ts_ns, eastern_date_from_ns)


def map_unique_utc(ts_ns):
    return _map_unique_int64(ts_ns, utc_date_from_ns)


def seconds_after_eastern_midnight(ts_event_ns, eastern_date, midnight_cache=None):
    if ts_event_ns is None or eastern_date is None:
        return None
    cache = midnight_cache if midnight_cache is not None else {}
    midnight = cache.get(eastern_date)
    if midnight is None:
        midnight = local_timestamp(date.fromisoformat(eastern_date), time(0), ZONE)
        cache[eastern_date] = midnight
    return (ts_event_ns - midnight) / 1_000_000_000


def sourceclock_asof_eligible(ts_event_ns, request_date, cut_ns, cut_date):
    if ts_event_ns is None or request_date is None:
        return False
    return ts_event_ns <= cut_ns and request_date <= cut_date


def select_asof_observation(observations, cut_ns, cut_date):
    """Literal helper: last conflict-free row at or before the cut. No earlier fallback."""
    eligible = [row for row in observations
                if sourceclock_asof_eligible(row.get("ts_event_ns"), row.get("request_date"), cut_ns, cut_date)]
    if not eligible:
        future = any(row.get("ts_event_ns") is not None and row.get("ts_event_ns") > cut_ns for row in observations)
        return None, "rejected_future" if future else "none"
    last_ts = max(row["ts_event_ns"] for row in eligible)
    at_last = [row for row in eligible if row["ts_event_ns"] == last_ts]
    values = {row["open_interest"] for row in at_last}
    if len(values) != 1:
        return None, "ambiguous"
    return min(at_last, key=lambda row: (row["file_id"], row["row_index"])), "ok"


def cut_ns_on(day, label):
    hour, minute = (int(part) for part in label.split(":"))
    if type(day) is str:
        day = date.fromisoformat(day)
    return local_timestamp(day, time(hour, minute), ZONE)


def resolve_contract_report(observations):
    """First/last source-clock endpoints. Same-time conflicts have no winner."""
    by_time = defaultdict(list)
    missing_clock = 0
    for row in observations:
        ts = row.get("ts_event_ns")
        if ts is None:
            missing_clock += 1
            continue
        by_time[ts].append(row)
    times = sorted(by_time)
    conflict = False
    max_alias = 1
    points = []
    for ts in times:
        rows = by_time[ts]
        values = {row["open_interest"] for row in rows}
        max_alias = max(max_alias, len(rows))
        if len(values) != 1:
            conflict = True
            continue
        pick = min(rows, key=lambda row: (row["file_id"], row["row_index"]))
        points.append((ts, pick["open_interest"], pick["file_id"], pick["row_index"], len(rows)))
    first = points[0] if points else None
    last = points[-1] if points else None
    update = bool(first and last and first[0] != last[0] and first[1] != last[1])
    return {
        "first_oi": None if first is None else first[1],
        "first_ts_event_ns": None if first is None else first[0],
        "first_file_id": None if first is None else first[2],
        "first_row_index": None if first is None else first[3],
        "last_oi": None if last is None else last[1],
        "last_ts_event_ns": None if last is None else last[0],
        "last_file_id": None if last is None else last[2],
        "last_row_index": None if last is None else last[3],
        "alias_multiplicity": max_alias,
        "same_time_conflict": conflict,
        "conflict_disposition": "same_time_no_winner" if conflict else "none",
        "update_candidate": update,
        "observed_update_difference": None if not update else last[1] - first[1],
        "certified_revision": False,
        "usable_for_statistics": bool(first is not None and not conflict),
        "n_source_rows": len(observations),
        "n_distinct_times": len(times),
        "missing_clock_rows": missing_clock,
        "support_observations": len(points),
    }


def adjacent_lifecycle(prior, current, *, prior_date, next_date, expiration, last_selected, first_selected,
                       prior_stage, next_stage, listed_on_prior):
    """Adjacent intended-date first/first and last/last. Gaps are not compressed."""
    expired = expiration is not None and next_date is not None and expiration < next_date
    right_boundary = next_date is None or (last_selected is not None and prior_date == last_selected)
    left_boundary = first_selected is not None and next_date == first_selected and prior is None
    appearance = "first_observed" if prior is None else "continuing"
    censor = None
    if right_boundary and current is None:
        censor = "right_source_boundary"
    elif expired and current is None:
        censor = "expired_before_next_request_date"
    elif current is None:
        censor = "missing_next_publication"
    elif prior is None:
        censor = "left_source_boundary" if left_boundary else "prior_report_missing"
    clock_ok = True
    if prior is not None and current is not None:
        pts, cts = prior.get("ts_event_ns"), current.get("ts_event_ns")
        if pts is None or cts is None or pts >= cts:
            clock_ok = False
            censor = "clock_order_violated"
    usable_pair = bool(
        prior is not None and current is not None and clock_ok
        and prior.get("usable_for_statistics") and current.get("usable_for_statistics")
        and prior.get("open_interest") is not None and current.get("open_interest") is not None
    )
    delta = None if not usable_pair else current["open_interest"] - prior["open_interest"]
    year_ok = bool(usable_pair and prior_date and next_date and prior_date[:4] == next_date[:4])
    return {
        "censor": censor, "delta": delta,
        "abs_delta": None if delta is None else abs(delta),
        "usable_for_statistics": usable_pair,
        "within_stage_stat_eligible": usable_pair and prior_stage is not None and prior_stage == next_stage,
        "within_year_stat_eligible": year_ok,
        "appearance": appearance, "prior_report_missing": prior is None,
        "listed_on_prior": listed_on_prior, "certified_listing_birth": False,
        "intraday_terminal_holdings_identified": False, "clock_order_ok": clock_ok,
        "expired_before_next": expired,
        "right_source_boundary": bool(right_boundary and current is None),
        "cross_gap_compressed": False,
        "is_boundary": censor in {"right_source_boundary", "left_source_boundary"},
    }


def reconstruct_asof_intervals(intervals, cut_ns, cut_date):
    """Exact reconstruction of sourceclock state at cut from the interval ledger."""
    visible = []
    for row in intervals:
        start, end = row.get("valid_from_ns"), row.get("valid_to_ns")
        req, exp = row.get("request_date"), row.get("expiration")
        if start is None or start > cut_ns:
            continue
        if end is not None and cut_ns >= end:
            continue
        if req is None or req > cut_date:
            continue
        if exp is not None and exp < cut_date:
            continue
        visible.append(row)
    return visible


reconstruct_asof = reconstruct_asof_intervals


def _schema_fields(schema_str):
    if type(schema_str) is not str or not schema_str.strip():
        raise ContractError("admitted schema string required")
    fields = []
    for line in schema_str.strip().splitlines():
        if ":" not in line:
            raise ContractError("admitted schema line missing type")
        name, typ = line.split(":", 1)
        fields.append((name.strip(), typ.strip()))
    if len({name for name, _ in fields}) != len(fields):
        raise ContractError("admitted schema has duplicate fields")
    return tuple(fields)


def _type_ok(arrow_type, declared):
    pa = _pa()
    declared = declared.lower()
    if declared.startswith("large_string") or declared == "string":
        return pa.types.is_string(arrow_type) or pa.types.is_large_string(arrow_type)
    if declared.startswith("date32"):
        return pa.types.is_date(arrow_type)
    if declared in {"double", "float64", "float"}:
        return pa.types.is_floating(arrow_type)
    if declared == "int64":
        return pa.types.is_integer(arrow_type)
    if declared.startswith("timestamp"):
        return pa.types.is_timestamp(arrow_type) and arrow_type.unit == "ns"
    return True


def _check_schema(table, schema_str, required):
    declared = dict(_schema_fields(schema_str))
    names = set(table.schema.names)
    missing = [name for name in required if name not in names or name not in declared]
    if missing:
        raise IntegrityError("admitted source missing required columns: " + ",".join(missing))
    for name in required:
        if not _type_ok(table.schema.field(name).type, declared[name]):
            raise IntegrityError(f"admitted source column {name} changed type")


def _data_root(protocol):
    return Path(protocol.get("data_root", DEFAULT_DATA_ROOT)).resolve()


def _resolve_source_path(protocol, relative):
    if type(relative) is not str or not relative or relative.startswith("/") or ".." in Path(relative).parts:
        raise ContractError("source path must be a relative /workspace/data path")
    root = _data_root(protocol)
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        raise IntegrityError("source path escaped data root")
    return path


def _empty_table(role):
    pa = _pa()
    names = OI_FIELDS if role == "open_interest" else CONTRACT_FIELDS
    fields = []
    for name in names:
        if name in {"expiration", "request_date"}:
            fields.append((name, pa.date32()))
        elif name == "strike":
            fields.append((name, pa.float64()))
        elif name == "open_interest":
            fields.append((name, pa.int64()))
        elif name == "ts_event":
            fields.append((name, pa.timestamp("ns", tz="UTC")))
        else:
            fields.append((name, pa.large_string()))
    return pa.schema(fields).empty_table()


def _is_empty_marker(payload, record):
    if record.get("empty_marker") is True or record.get("marker") == "empty":
        return True
    if payload == {}:
        return True
    return isinstance(payload, dict) and payload.get("empty_marker") is True and "rows" not in payload


def read_admitted_source(protocol, record):
    """Read one original file after exact size/hash checks. No CAS copy."""
    source = record["source"]
    path = _resolve_source_path(protocol, source["path"])
    if not path.is_file():
        raise IntegrityError("admitted source file is missing")
    size = path.stat().st_size
    limit = int(contract(protocol).get("resources", {}).get("maximum_source_file_bytes", MAX_SOURCE_FILE))
    if size > limit:
        raise ContractError("source file exceeds the 16MiB per-file bound")
    if size != source["size_bytes"]:
        raise IntegrityError("admitted source size changed before decode")
    raw = path.read_bytes()
    if len(raw) != source["size_bytes"]:
        raise IntegrityError("admitted source size changed during read")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != record["sha256"]:
        raise IntegrityError("admitted source hash changed before decode")
    fmt = record["format"]
    empty = False
    if fmt == ".parquet":
        import pyarrow.parquet as pq
        table = pq.read_table(_pa().BufferReader(raw))
    elif fmt == ".json":
        payload = json.loads(raw.decode())
        if _is_empty_marker(payload, record):
            table = _empty_table(source["role"])
            empty = True
        else:
            rows = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
            if type(rows) is not list:
                raise ContractError("JSON source must be a row list or validated empty marker")
            table = _pa().Table.from_pylist(rows) if rows else _empty_table(source["role"])
    else:
        raise ContractError("source format must be .parquet or .json")
    return table, {"path": source["path"], "sha256": digest, "size_bytes": size,
                   "rows": len(table), "file_id": record["file_id"], "schema_id": record["schema_id"],
                   "format": fmt, "empty_marker": empty}


def identity_schema():
    pa = _pa()
    return pa.schema([
        ("contract_id", pa.int32()), ("chain", pa.string()), ("osi_symbol", pa.string()),
        ("expiration", pa.string()), ("millistrike", pa.int64()), ("right", pa.string()),
    ])


def exception_schema():
    pa = _pa()
    return pa.schema([
        ("file_id", pa.int64()), ("row_index", pa.int64()), ("chain", pa.string()),
        ("role", pa.string()), ("request_date", pa.string()), ("invalid_reason", pa.string()),
        ("osi_symbol", pa.string()), ("expiration", pa.string()), ("strike", pa.float64()),
        ("right", pa.string()), ("open_interest", pa.int64()), ("ts_event_ns", pa.int64()),
    ])


def membership_schema():
    pa = _pa()
    return pa.schema([
        ("file_id", pa.int64()), ("path", pa.string()), ("sha256", pa.string()),
        ("chain", pa.string()), ("role", pa.string()), ("request_date", pa.string()),
        ("rows_read", pa.int64()), ("rows_valid", pa.int64()), ("rows_invalid", pa.int64()),
        ("empty_marker", pa.bool_()),
    ])


def report_schema():
    pa = _pa()
    return pa.schema([
        ("contract_id", pa.int32()), ("chain", pa.string()), ("request_date", pa.string()),
        ("listed", pa.bool_()), ("first_oi", pa.int64()), ("first_ts_event_ns", pa.int64()),
        ("first_file_id", pa.int64()), ("first_row_index", pa.int64()),
        ("last_oi", pa.int64()), ("last_ts_event_ns", pa.int64()),
        ("last_file_id", pa.int64()), ("last_row_index", pa.int64()),
        ("alias_multiplicity", pa.int64()), ("same_time_conflict", pa.bool_()),
        ("conflict_disposition", pa.string()), ("update_candidate", pa.bool_()),
        ("observed_update_difference", pa.int64()), ("certified_revision", pa.bool_()),
        ("usable_for_statistics", pa.bool_()), ("n_source_rows", pa.int64()),
        ("n_distinct_times", pa.int64()), ("support_observations", pa.int64()),
        ("dte", pa.int64()), ("dte_bucket", pa.string()), ("right", pa.string()),
        ("causal_feature_eligible", pa.bool_()),
    ])


def coverage_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("request_date", pa.string()), ("intended", pa.bool_()),
        ("closed", pa.bool_()), ("primary", pa.bool_()),
        ("listing_file_present", pa.bool_()), ("oi_file_present", pa.bool_()),
        ("both_files_absent", pa.bool_()), ("listing_status", pa.string()),
        ("oi_status", pa.string()), ("listing_count", pa.int64()), ("oi_count", pa.int64()),
        ("oi_zero_count", pa.int64()), ("intersection_count", pa.int64()),
        ("union_count", pa.int64()), ("listed_without_oi", pa.int64()),
        ("oi_without_listing", pa.int64()), ("listing_denominator_known", pa.bool_()),
        ("coverage_listed_with_oi", pa.float64()), ("invalid_row_count", pa.int64()),
        ("missing_clock_count", pa.int64()), ("event_local_mismatch_count", pa.int64()),
        ("future_flag_count", pa.int64()), ("late_flag_count", pa.int64()),
        ("usable_report_count", pa.int64()), ("conflict_report_count", pa.int64()),
        ("update_candidate_count", pa.int64()), ("gt60_dte_retained", pa.int64()),
        ("vix_listing_unknown", pa.bool_()),
        ("position_mapping_agree_count", pa.int64()), ("position_mapping_count", pa.int64()),
    ])


def interval_schema():
    pa = _pa()
    return pa.schema([
        ("contract_id", pa.int32()), ("chain", pa.string()),
        ("open_interest", pa.int64()), ("ts_event_ns", pa.int64()),
        ("request_date", pa.string()), ("file_id", pa.int64()), ("row_index", pa.int64()),
        ("ambiguous", pa.bool_()), ("valid_from_ns", pa.int64()), ("valid_to_ns", pa.int64()),
        ("expiration", pa.string()), ("causal_feature_eligible", pa.bool_()),
    ])


def asof_aggregate_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("cut_date", pa.string()), ("cut_label", pa.string()),
        ("cut_ns", pa.int64()), ("universe", pa.int64()), ("available", pa.int64()),
        ("ambiguous", pa.int64()), ("stale", pa.int64()), ("prior_held", pa.int64()),
        ("future_today", pa.int64()), ("not_available", pa.int64()),
        ("expired", pa.int64()), ("listing_only", pa.int64()),
        ("available_fraction", pa.float64()), ("causal_feature_eligible", pa.bool_()),
    ])


def lifecycle_schema():
    pa = _pa()
    return pa.schema([
        ("contract_id", pa.int32()), ("chain", pa.string()),
        ("prior_date", pa.string()), ("next_date", pa.string()),
        ("first_prior_oi", pa.int64()), ("first_next_oi", pa.int64()),
        ("first_prior_ts_event_ns", pa.int64()), ("first_next_ts_event_ns", pa.int64()),
        ("first_prior_file_id", pa.int64()), ("first_prior_row_index", pa.int64()),
        ("first_next_file_id", pa.int64()), ("first_next_row_index", pa.int64()),
        ("first_delta", pa.int64()), ("first_abs_delta", pa.int64()),
        ("first_censor", pa.string()), ("first_usable", pa.bool_()),
        ("first_within_stage", pa.bool_()), ("first_within_year", pa.bool_()),
        ("last_prior_oi", pa.int64()), ("last_next_oi", pa.int64()),
        ("last_prior_ts_event_ns", pa.int64()), ("last_next_ts_event_ns", pa.int64()),
        ("last_prior_file_id", pa.int64()), ("last_prior_row_index", pa.int64()),
        ("last_next_file_id", pa.int64()), ("last_next_row_index", pa.int64()),
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


def _table(schema, rows):
    pa = _pa()
    if not rows:
        return schema.empty_table()
    return pa.table({field.name: [row.get(field.name) for row in rows] for field in schema}, schema=schema)


class StreamWriter:
    def __init__(self, outputs, prefix, schema, kind, batch_rows=STREAM_ROWS):
        self.outputs, self.prefix, self.schema, self.kind = outputs, prefix, schema, kind
        self.batch_rows = batch_rows
        self.buffer, self.refs, self.rows, self.part = [], [], 0, 0

    def append(self, rows):
        if not rows:
            return
        self.buffer.extend(rows)
        if len(self.buffer) >= self.batch_rows:
            self._flush()

    def _flush(self):
        if not self.buffer and self.refs:
            return
        import pyarrow.parquet as pq
        table = _table(self.schema, self.buffer)
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
        self.buffer = []

    def finish(self):
        if self.buffer or not self.refs:
            self._flush()
        return self.refs


class IdentityStore:
    def __init__(self):
        self._key_to_id = {}
        self._pending = []
        self.expiration = {}
        self.next_id = 0

    def intern_many(self, chain, osi, exp, milli, right):
        ids = []
        for item in zip(osi, exp, milli, right):
            key = (chain, item[0], item[1], item[2], item[3])
            cid = self._key_to_id.get(key)
            if cid is None:
                cid = self.next_id
                self.next_id += 1
                self._key_to_id[key] = cid
                self.expiration[cid] = item[1]
                self._pending.append({
                    "contract_id": cid, "chain": chain, "osi_symbol": item[0],
                    "expiration": item[1], "millistrike": item[2], "right": item[3],
                })
            ids.append(cid)
        return ids

    def flush(self, writer):
        writer.append(self._pending)
        self._pending = []


def _safe_iso_dates(values):
    out, ok = [], []
    for value in values:
        if value is None:
            out.append(None)
            ok.append(False)
            continue
        if type(value) is str:
            try:
                parsed = date.fromisoformat(value)
            except ValueError:
                out.append(value)
                ok.append(False)
                continue
            out.append(value)
            ok.append(parsed.isoformat() == value)
            continue
        out.append(None)
        ok.append(False)
    return out, ok


def _oi_integer_values(column):
    pa = _pa()
    if pa.types.is_floating(column.type):
        values = column.to_pylist()
        return values, [False] * len(values)
    if pa.types.is_integer(column.type):
        return column.cast(pa.int64()).to_pylist(), [True] * len(column)
    values = column.to_pylist()
    return values, [False] * len(values)


def parse_source_arrays(table, *, record, schema_str, prev_map, midnight_cache):
    """Unique OSI/timestamp maps; no per-row Arrow or calendar scan."""
    source = record["source"]
    role, chain, file_id = source["role"], source["chain"], record["file_id"]
    declared = source["request_date"]
    required = OI_FIELDS if role == "open_interest" else CONTRACT_FIELDS
    _check_schema(table, schema_str, required)
    n = len(table)
    symbols = table.column("symbol").to_pylist() if "symbol" in table.schema.names else [None] * n
    osi = table.column("osi_symbol").to_pylist()
    rights_raw = table.column("right").to_pylist()
    strikes = table.column("strike").to_pylist()
    expirations, exp_ok = _safe_iso_dates(_date_strings(table.column("expiration")).to_pylist())
    request_dates, req_ok = _safe_iso_dates(_date_strings(table.column("request_date")).to_pylist())
    if role == "open_interest":
        oi_values, oi_int_ok = _oi_integer_values(table.column("open_interest"))
        ts_event = timestamp_ns_from_arrow(table.column("ts_event")).to_pylist()
        east = map_unique_eastern(ts_event)
        utc = map_unique_utc(ts_event)
    else:
        oi_values, oi_int_ok = [None] * n, [True] * n
        ts_event = [None] * n
        east = [None] * n
        utc = [None] * n
    osi_cache, right_cache, milli_cache, second_cache = {}, {}, {}, {}
    parsed = {key: [] for key in (
        "osi", "expiration", "millistrike", "right", "request_date", "open_interest",
        "ts_event_ns", "row_index", "file_id", "dte", "dte_bucket",
        "mismatch", "future", "late", "map_agree", "seconds",
    )}
    exceptions = []
    for index in range(n):
        osi_s = osi[index]
        if osi_s not in osi_cache:
            osi_cache[osi_s] = parse_osi(osi_s) if type(osi_s) is str else None
        cached = osi_cache[osi_s]
        raw_right = rights_raw[index]
        if raw_right not in right_cache:
            right_cache[raw_right] = normalize_right(raw_right)
        right = right_cache[raw_right]
        strike = strikes[index]
        if strike not in milli_cache:
            milli_cache[strike] = millistrike(strike)
        milli = milli_cache[strike]
        exp, req = expirations[index], request_dates[index]
        reason = None
        if not exp_ok[index]:
            reason = "invalid_expiration"
        elif not req_ok[index]:
            reason = "invalid_request_date"
        elif osi_s is None or exp is None or right is None:
            reason = "missing_identity_fields"
        elif milli is None:
            reason = "missing_identity_fields" if strike is None else "inexact_or_nonfinite_strike"
        elif cached is None:
            reason = "unparseable_osi"
        elif cached["root"] != chain or (type(symbols[index]) is str and symbols[index] != chain):
            reason = "osi_root_or_symbol_chain_mismatch"
        elif cached["expiration"] != exp or cached["right"] != right or cached["millistrike"] != milli:
            reason = "strike_or_osi_identity_conflict"
        elif req != declared:
            reason = "wrong_request_date"
        oi_value, ts = oi_values[index], ts_event[index]
        if role == "open_interest" and reason is None:
            if oi_value is None:
                reason = "missing_open_interest"
            elif not oi_int_ok[index] or type(oi_value) is not int:
                reason = "non_integer_open_interest"
            elif oi_value < 0:
                reason = "negative_open_interest"
            elif ts is None:
                reason = "missing_clock"
        if reason is not None:
            exceptions.append({
                "file_id": file_id, "row_index": index, "chain": chain, "role": role,
                "request_date": req if type(req) is str else declared, "invalid_reason": reason,
                "osi_symbol": osi_s, "expiration": exp if type(exp) is str else None,
                "strike": strike if type(strike) is float else None, "right": right,
                "open_interest": oi_value if type(oi_value) is int else None,
                "ts_event_ns": ts if type(ts) is int else None,
            })
            continue
        east_d, utc_d = east[index], utc[index]
        del utc_d
        sec_key = (ts, east_d)
        if sec_key not in second_cache:
            second_cache[sec_key] = seconds_after_eastern_midnight(ts, east_d, midnight_cache)
        seconds = second_cache[sec_key]
        dte = dte_days(exp, req)
        pos_req = prev_map.get(req)
        pos_evt = prev_map.get(east_d) if east_d else None
        parsed["osi"].append(osi_s)
        parsed["expiration"].append(exp)
        parsed["millistrike"].append(milli)
        parsed["right"].append(right)
        parsed["request_date"].append(req)
        parsed["open_interest"].append(oi_value)
        parsed["ts_event_ns"].append(ts)
        parsed["row_index"].append(index)
        parsed["file_id"].append(file_id)
        parsed["dte"].append(dte)
        parsed["dte_bucket"].append(dte_bucket(dte))
        parsed["mismatch"].append(bool(ts is not None and east_d is not None and east_d != req))
        parsed["future"].append(bool(ts is not None and east_d is not None and east_d > req))
        parsed["late"].append(bool(seconds is not None and seconds > 15 * 3600))
        parsed["map_agree"].append(pos_req is not None and pos_req == pos_evt)
        parsed["seconds"].append(seconds)
    return parsed, exceptions, n, len(parsed["osi"])


def resolve_reports_arrays(contract_id, ts, oi, file_id, row_index):
    """Vectorized first/last by sorted (contract, timestamp)."""
    np = _np()
    if len(contract_id) == 0:
        return {}
    cid = np.asarray(contract_id, dtype=np.int32)
    ts_a = np.asarray(ts, dtype=np.int64)
    oi_a = np.asarray(oi, dtype=np.int64)
    fid = np.asarray(file_id, dtype=np.int64)
    rid = np.asarray(row_index, dtype=np.int64)
    order = np.lexsort((rid, fid, ts_a, cid))
    cid, ts_a, oi_a, fid, rid = cid[order], ts_a[order], oi_a[order], fid[order], rid[order]
    reports = {}
    start, n = 0, len(cid)
    while start < n:
        end = start + 1
        while end < n and cid[end] == cid[start]:
            end += 1
        block_ts, block_oi = ts_a[start:end], oi_a[start:end]
        block_fid, block_rid = fid[start:end], rid[start:end]
        conflict, max_alias, points, t0, m = False, 1, [], 0, end - start
        while t0 < m:
            t1 = t0 + 1
            while t1 < m and block_ts[t1] == block_ts[t0]:
                t1 += 1
            max_alias = max(max_alias, t1 - t0)
            if len(set(block_oi[t0:t1].tolist())) != 1:
                conflict = True
            else:
                pick = int(np.lexsort((block_rid[t0:t1], block_fid[t0:t1]))[0])
                points.append((int(block_ts[t0]), int(block_oi[t0 + pick]),
                               int(block_fid[t0 + pick]), int(block_rid[t0 + pick])))
            t0 = t1
        first, last = (points[0] if points else None), (points[-1] if points else None)
        update = bool(first and last and first[0] != last[0] and first[1] != last[1])
        reports[int(cid[start])] = {
            "first_oi": None if first is None else first[1],
            "first_ts_event_ns": None if first is None else first[0],
            "first_file_id": None if first is None else first[2],
            "first_row_index": None if first is None else first[3],
            "last_oi": None if last is None else last[1],
            "last_ts_event_ns": None if last is None else last[0],
            "last_file_id": None if last is None else last[2],
            "last_row_index": None if last is None else last[3],
            "alias_multiplicity": max_alias, "same_time_conflict": conflict,
            "conflict_disposition": "same_time_no_winner" if conflict else "none",
            "update_candidate": update,
            "observed_update_difference": None if not update else last[1] - first[1],
            "certified_revision": False,
            "usable_for_statistics": bool(first is not None and not conflict),
            "n_source_rows": int(m),
            "n_distinct_times": int(len({int(v) for v in block_ts.tolist()})),
            "support_observations": len(points),
        }
        start = end
    return reports


def _life_acc():
    return {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0, "n_neg": 0,
            "n_censor_missing": 0, "n_censor_expired": 0, "n_censor_boundary": 0,
            "n_attempts": 0, "n_first_observed": 0, "n_prior_missing": 0}


def _tally_life(acc, life):
    acc["n_attempts"] += 1
    if life["appearance"] == "first_observed":
        acc["n_first_observed"] += 1
    if life["prior_report_missing"]:
        acc["n_prior_missing"] += 1
    if life["censor"] == "missing_next_publication":
        acc["n_censor_missing"] += 1
    elif life["censor"] == "expired_before_next_request_date":
        acc["n_censor_expired"] += 1
    if life["delta"] is None:
        return
    acc["n"] += 1
    acc["delta_sum"] += life["delta"]
    acc["abs_sum"] += life["abs_delta"]
    acc["n_pos"] += int(life["delta"] > 0)
    acc["n_zero"] += int(life["delta"] == 0)
    acc["n_neg"] += int(life["delta"] < 0)


def _policy_acc():
    return {"oi_sum": 0, "oi_n": 0, "zero_n": 0, "seconds_sum": 0.0, "seconds_n": 0,
            "usable_n": 0, "common_n": 0, "common_first_sum": 0, "common_last_sum": 0,
            "paired_diff_sum": 0, "own_n": 0}


def _add_policy(acc, report, policy, seconds):
    oi = report[f"{policy}_oi"]
    if not report["usable_for_statistics"] or oi is None:
        return
    acc["oi_sum"] += oi
    acc["oi_n"] += 1
    acc["zero_n"] += int(oi == 0)
    acc["usable_n"] += 1
    acc["own_n"] += 1
    if seconds is not None:
        acc["seconds_sum"] += seconds
        acc["seconds_n"] += 1


def _empty_date(chain, request_date, intended, closed, primary):
    bags = {name: {"first": _life_acc(), "last": _life_acc()}
            for name in ("lifecycle_all", "lifecycle_within_stage", "lifecycle_within_year", "lifecycle_boundary")}
    return {
        "chain": chain, "request_date": request_date, "intended": intended,
        "closed": closed, "primary": primary, "first": _policy_acc(), "last": _policy_acc(),
        **bags, "asof": {}, "listing_count": None, "oi_count": None, "oi_zero_count": 0,
        "intersection_count": None, "union_count": None, "listed_without_oi": None,
        "oi_without_listing": None, "listing_denominator_known": False,
        "coverage_listed_with_oi": None, "invalid_row_count": 0,
        "missing_clock_count": 0, "event_local_mismatch_count": 0,
        "future_flag_count": 0, "late_flag_count": 0, "usable_report_count": 0,
        "conflict_report_count": 0, "update_candidate_count": 0, "update_diff_sum": 0,
        "update_n": 0, "gt60_dte_retained": 0, "by_right": {}, "by_dte": {},
        "position_mapping_agree_count": 0, "position_mapping_count": 0,
    }


class AsofTimeline:
    """Pending sourceclock events + live state. Late prints survive past 15:00."""

    def __init__(self, chain):
        self.chain = chain
        self.pending = []
        self.live = {}
        self.open = {}
        self.request_midnights = {}

    def add(self, contract_ids, ts, oi, request_dates, file_id, row_index, expirations):
        for item in zip(contract_ids, ts, oi, request_dates, file_id, row_index, expirations):
            if item[1] is None or item[2] is None:
                continue
            if item[3] not in self.request_midnights:
                self.request_midnights[item[3]] = cut_ns_on(item[3], "00:00")
            self.pending.append(item)

    def apply_through(self, cut_ns, cut_date):
        still, applied = [], []
        for event in self.pending:
            if event[1] <= cut_ns and event[3] <= cut_date:
                applied.append(event)
            else:
                still.append(event)
        self.pending = still
        # A later request can repeat an older source clock. Its eligibility starts
        # at request midnight; it cannot rewrite an earlier interval or replace a
        # newer clock. Resolve same-clock conflicts across request files as well.
        def availability(event):
            return max(event[1], self.request_midnights[event[3]])
        applied.sort(key=lambda e: (availability(e), e[0], e[1], e[3], e[4], e[5]))
        closed = []
        i = 0
        while i < len(applied):
            j = i + 1
            first = applied[i]
            start_at = availability(first)
            while (j < len(applied) and applied[j][0] == first[0]
                   and applied[j][1] == first[1] and availability(applied[j]) == start_at):
                j += 1
            group = applied[i:j]
            cid, ts = first[0], first[1]
            prev = self.open.get(cid)
            if prev is not None and ts < prev["ts_event_ns"]:
                i = j
                continue
            pick = min(group, key=lambda item: (item[3], item[4], item[5]))
            values = {item[2] for item in group}
            ambiguous = len(values) != 1
            if prev is not None and ts == prev["ts_event_ns"]:
                ambiguous = ambiguous or prev["ambiguous"] or prev["open_interest"] not in values
                if not ambiguous:
                    i = j
                    continue
            if prev is not None:
                self.open.pop(cid)
                start_at = max(start_at, prev["valid_from_ns"])
                prev["valid_to_ns"] = start_at
                closed.append(prev)
            state = {
                "contract_id": cid, "chain": self.chain,
                "open_interest": None if ambiguous else pick[2],
                "ts_event_ns": ts, "request_date": pick[3],
                "file_id": pick[4], "row_index": pick[5],
                "ambiguous": ambiguous, "valid_from_ns": start_at, "valid_to_ns": None,
                "expiration": pick[6], "causal_feature_eligible": False,
            }
            self.open[cid] = dict(state)
            self.live[cid] = {
                "oi": state["open_interest"], "ts": ts, "request_date": pick[3],
                "ambiguous": ambiguous, "expiration": pick[6],
            }
            i = j
        return closed

    def purge_expired(self, cut_date, cut_midnight_ns):
        closed = []
        for cid, state in list(self.live.items()):
            exp = state.get("expiration")
            if exp is not None and exp < cut_date:
                prev = self.open.pop(cid, None)
                if prev is not None:
                    prev["valid_to_ns"] = cut_midnight_ns
                    closed.append(prev)
                del self.live[cid]
        return closed

    def snapshot_counts(self, cut_ns, cut_date, listing_ids, prev_cash):
        expired = available = ambiguous = stale = prior_held = 0
        live_ids = set()
        for cid, state in self.live.items():
            exp = state.get("expiration")
            if exp is not None and exp < cut_date:
                expired += 1
                continue
            live_ids.add(cid)
            if state["ambiguous"]:
                ambiguous += 1
                continue
            if state["oi"] is None:
                continue
            available += 1
            if state["request_date"] < cut_date:
                prior_held += 1
            if prev_cash and state["request_date"] < prev_cash:
                stale += 1
        listing = set(listing_ids)
        listing_only = len(listing - live_ids)
        future_today = {event[0] for event in self.pending
                        if event[3] == cut_date and event[1] > cut_ns}
        universe = live_ids | listing | future_today
        return {
            "universe": len(universe), "available": available, "ambiguous": ambiguous,
            "stale": stale, "prior_held": prior_held, "future_today": len(future_today),
            "not_available": len(universe) - available, "expired": expired,
            "listing_only": listing_only,
            "available_fraction": None if not universe else available / len(universe),
        }


def _endpoint(report, policy):
    return {
        "open_interest": report[f"{policy}_oi"], "ts_event_ns": report[f"{policy}_ts_event_ns"],
        "file_id": report[f"{policy}_file_id"], "row_index": report[f"{policy}_row_index"],
        "usable_for_statistics": report["usable_for_statistics"],
    }


def _side(report, policy, key):
    return None if report is None else report.get(f"{policy}_{key}")


def _life_record(chain, cid, prior_date, next_date, prior, current, first_life, last_life,
                 prior_stage, next_stage, listed_prior):
    return {
        "contract_id": cid, "chain": chain, "prior_date": prior_date, "next_date": next_date,
        "first_prior_oi": _side(prior, "first", "oi"), "first_next_oi": _side(current, "first", "oi"),
        "first_prior_ts_event_ns": _side(prior, "first", "ts_event_ns"),
        "first_next_ts_event_ns": _side(current, "first", "ts_event_ns"),
        "first_prior_file_id": _side(prior, "first", "file_id"),
        "first_prior_row_index": _side(prior, "first", "row_index"),
        "first_next_file_id": _side(current, "first", "file_id"),
        "first_next_row_index": _side(current, "first", "row_index"),
        "first_delta": first_life["delta"], "first_abs_delta": first_life["abs_delta"],
        "first_censor": first_life["censor"], "first_usable": first_life["usable_for_statistics"],
        "first_within_stage": first_life["within_stage_stat_eligible"],
        "first_within_year": first_life["within_year_stat_eligible"],
        "last_prior_oi": _side(prior, "last", "oi"), "last_next_oi": _side(current, "last", "oi"),
        "last_prior_ts_event_ns": _side(prior, "last", "ts_event_ns"),
        "last_next_ts_event_ns": _side(current, "last", "ts_event_ns"),
        "last_prior_file_id": _side(prior, "last", "file_id"),
        "last_prior_row_index": _side(prior, "last", "row_index"),
        "last_next_file_id": _side(current, "last", "file_id"),
        "last_next_row_index": _side(current, "last", "row_index"),
        "last_delta": last_life["delta"], "last_abs_delta": last_life["abs_delta"],
        "last_censor": last_life["censor"], "last_usable": last_life["usable_for_statistics"],
        "last_within_stage": last_life["within_stage_stat_eligible"],
        "last_within_year": last_life["within_year_stat_eligible"],
        "appearance": first_life["appearance"], "listed_on_prior": listed_prior,
        "certified_listing_birth": False, "intraday_terminal_holdings_identified": False,
        "cross_gap_compressed": False, "is_boundary": first_life["is_boundary"],
        "prior_stage": prior_stage, "next_stage": next_stage, "causal_feature_eligible": False,
        "_first_life": first_life, "_last_life": last_life,
    }


def _join_lifecycle(prev_reports, reports, prev_listings, listings, *, chain, prior_date, next_date,
                    last_selected, first_selected, prior_stage, next_stage, listing_known, expiration):
    del listings
    rows = []
    prev_ids, curr_ids = sorted(prev_reports), sorted(reports)
    i = j = 0
    while i < len(prev_ids) or j < len(curr_ids):
        if i < len(prev_ids) and (j == len(curr_ids) or prev_ids[i] < curr_ids[j]):
            cid, current, prior = prev_ids[i], None, prev_reports[prev_ids[i]]
            i += 1
        elif j < len(curr_ids) and (i == len(prev_ids) or curr_ids[j] < prev_ids[i]):
            cid, prior, current = curr_ids[j], None, reports[curr_ids[j]]
            j += 1
        else:
            cid = prev_ids[i]
            prior, current = prev_reports[cid], reports[cid]
            i += 1
            j += 1
        listed_prior = (cid in prev_listings) if listing_known else None
        args = dict(prior_date=prior_date, next_date=next_date, expiration=expiration.get(cid),
                    last_selected=last_selected, first_selected=first_selected,
                    prior_stage=prior_stage, next_stage=next_stage, listed_on_prior=listed_prior)
        first_life = adjacent_lifecycle(
            None if prior is None else _endpoint(prior, "first"),
            None if current is None else _endpoint(current, "first"), **args)
        last_life = adjacent_lifecycle(
            None if prior is None else _endpoint(prior, "last"),
            None if current is None else _endpoint(current, "last"), **args)
        rows.append(_life_record(chain, cid, prior_date, next_date, prior, current,
                                 first_life, last_life, prior_stage, next_stage, listed_prior))
    return rows


def _tally_bags(agg, first_life, last_life, prior_date, next_date, prior_stage, next_stage, boundary):
    if boundary:
        agg["lifecycle_boundary"]["first"]["n_attempts"] += 1
        agg["lifecycle_boundary"]["last"]["n_attempts"] += 1
        return
    _tally_life(agg["lifecycle_all"]["first"], first_life)
    _tally_life(agg["lifecycle_all"]["last"], last_life)
    if prior_stage is not None and prior_stage == next_stage:
        _tally_life(agg["lifecycle_within_stage"]["first"], first_life)
        _tally_life(agg["lifecycle_within_stage"]["last"], last_life)
    if prior_date and next_date and prior_date[:4] == next_date[:4]:
        _tally_life(agg["lifecycle_within_year"]["first"], first_life)
        _tally_life(agg["lifecycle_within_year"]["last"], last_life)


def _validate_admitted(admitted, protocol, selected):
    if not isinstance(admitted, dict) or admitted.get("kind") != ADMITTED_KIND:
        raise ContractError("admitted options_oi_admitted_sources_v1 required")
    sources = admitted.get("sources")
    if type(sources) is not list:
        raise ContractError("admitted sources list required")
    if admitted.get("source_files") != len(sources):
        raise IntegrityError("admitted source_files count does not match sources")
    seen, selected_ids = set(), []
    selected_set = None if selected is None else set(selected)
    for record in sources:
        if type(record) is not dict or type(record.get("file_id")) is not int:
            raise ContractError("each admitted source needs an integer file_id")
        if record["file_id"] in seen:
            raise IntegrityError("duplicate admitted file_id")
        seen.add(record["file_id"])
        source = record.get("source")
        if not isinstance(source, dict) or source.get("role") not in {"contracts", "open_interest"}:
            raise ContractError("admitted source role must be contracts or open_interest")
        if source.get("chain") not in contract(protocol)["population"]["chains"]:
            raise ContractError("admitted chain is outside the frozen population")
        if record.get("format") not in {".parquet", ".json"}:
            raise ContractError("admitted format must be .parquet or .json")
        if selected_set is None or source["request_date"] in selected_set:
            selected_ids.append(record["file_id"])
    return sources, selected_ids


def _seconds_for_ts(values, midnight_cache):
    east = map_unique_eastern(values)
    out, memo = [], {}
    for ts, label in zip(values, east):
        key = (ts, label)
        if key not in memo:
            memo[key] = seconds_after_eastern_midnight(ts, label, midnight_cache)
        out.append(memo[key])
    return out


def _finish_day_policies(agg, report_rows, first_secs, last_secs):
    for report, sec_first, sec_last in zip(report_rows, first_secs, last_secs):
        _add_policy(agg["first"], report, "first", sec_first)
        _add_policy(agg["last"], report, "last", sec_last)
        if report["usable_for_statistics"] and report["first_oi"] is not None and report["last_oi"] is not None:
            for acc in (agg["first"], agg["last"]):
                acc["common_n"] += 1
                acc["common_first_sum"] += report["first_oi"]
                acc["common_last_sum"] += report["last_oi"]
                acc["paired_diff_sum"] += report["first_oi"] - report["last_oi"]
        right_acc = agg["by_right"].setdefault(report.get("right") or "unknown",
                                               {"first": _policy_acc(), "last": _policy_acc()})
        dte_acc = agg["by_dte"].setdefault(report.get("dte_bucket") or "unknown",
                                           {"first": _policy_acc(), "last": _policy_acc()})
        _add_policy(right_acc["first"], report, "first", sec_first)
        _add_policy(right_acc["last"], report, "last", sec_last)
        _add_policy(dte_acc["first"], report, "first", sec_first)
        _add_policy(dte_acc["last"], report, "last", sec_last)


def run(*, protocol: dict, admitted: dict, outputs: BoundedOutputs, selected_dates: list[str] | None = None) -> dict:
    from trading_research.research.options_oi_columnar import run_columnar
    return run_columnar(protocol=protocol, admitted=admitted, outputs=outputs, selected_dates=selected_dates)


def _legacy_run(*, protocol: dict, admitted: dict, outputs: BoundedOutputs, selected_dates: list[str] | None = None) -> dict:
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
    identity_w = StreamWriter(outputs, "identity", identity_schema(), OUTPUT_SCHEMAS["identity_map"])
    except_w = StreamWriter(outputs, "exceptions", exception_schema(), OUTPUT_SCHEMAS["exceptions"])
    member_w = StreamWriter(outputs, "membership", membership_schema(), OUTPUT_SCHEMAS["membership"])
    report_w = StreamWriter(outputs, "reports", report_schema(), OUTPUT_SCHEMAS["reports"])
    life_w = StreamWriter(outputs, "lifecycle", lifecycle_schema(), OUTPUT_SCHEMAS["lifecycle"])
    interval_w = StreamWriter(outputs, "asof-intervals", interval_schema(), OUTPUT_SCHEMAS["asof_intervals"])
    asof_agg_w = StreamWriter(outputs, "asof-aggregates", asof_aggregate_schema(), OUTPUT_SCHEMAS["asof_aggregates"])
    coverage_rows, date_aggregates, consumed, manifest = [], [], set(), []
    files_read = rows_read = bytes_read = 0
    source_dates, midnight_cache, cut_ns_cache = [], {}, {}
    identities = IdentityStore()
    research_cut = local_timestamp(date(2026, 9, 4), time(0), calendar.zone)
    listing_unknown_chains = sorted(CHAINS_WITHOUT_LISTING)
    for chain in chains:
        asof = AsofTimeline(chain)
        intended_work = set(selected_dates or intended_labels)
        last_selected = max(intended_work) if intended_work else None
        first_selected = min(intended_work) if intended_work else None
        prev_reports, prev_listings, prev_intended_date = {}, set(), None
        listing_known = chain not in CHAINS_WITHOUT_LISTING
        for day in work_dates[chain]:
            label = day.isoformat()
            intended = label in intended_label_set and (selected_set is None or label in selected_set)
            closed = calendar.resolve(day, cut=research_cut).state == "closed"
            primary = intended and population["first_date"] <= label <= population["last_date"]
            files = by_chain[chain].get(label, {})
            exceptions, listing_ids = [], []
            oi_cid, oi_ts, oi_val, oi_req, oi_fid, oi_row, oi_exp = [], [], [], [], [], [], []
            oi_dte, oi_bucket, oi_right = [], [], []
            mismatch_n = future_n = late_n = missing_clock_n = map_agree_n = map_n = 0
            listing_present, oi_present = "contracts" in files, "open_interest" in files
            empty_listing = empty_oi = False
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
                    parsed, bad, n_read, n_valid = parse_source_arrays(
                        table, record=record, schema_str=schema_str,
                        prev_map=prev_map, midnight_cache=midnight_cache,
                    )
                    exceptions.extend(bad)
                    missing_clock_n += sum(1 for row in bad if row["invalid_reason"] == "missing_clock")
                    member_w.append([{
                        "file_id": record["file_id"], "path": record["source"]["path"],
                        "sha256": record["sha256"], "chain": chain, "role": role,
                        "request_date": label, "rows_read": n_read, "rows_valid": n_valid,
                        "rows_invalid": len(bad), "empty_marker": meta["empty_marker"],
                    }])
                    manifest.append({
                        "file_id": record["file_id"], "path": record["source"]["path"],
                        "sha256": record["sha256"], "size_bytes": meta["size_bytes"],
                    })
                    if meta["empty_marker"] and role == "contracts":
                        empty_listing = True
                    elif meta["empty_marker"]:
                        empty_oi = True
                    if not parsed["osi"]:
                        continue
                    cids = identities.intern_many(
                        chain, parsed["osi"], parsed["expiration"], parsed["millistrike"], parsed["right"])
                    if role == "contracts":
                        listing_ids.extend(cids)
                        continue
                    oi_cid.extend(cids)
                    oi_ts.extend(parsed["ts_event_ns"])
                    oi_val.extend(parsed["open_interest"])
                    oi_req.extend(parsed["request_date"])
                    oi_fid.extend(parsed["file_id"])
                    oi_row.extend(parsed["row_index"])
                    oi_exp.extend(parsed["expiration"])
                    oi_dte.extend(parsed["dte"])
                    oi_bucket.extend(parsed["dte_bucket"])
                    oi_right.extend(parsed["right"])
                    mismatch_n += sum(parsed["mismatch"])
                    future_n += sum(parsed["future"])
                    late_n += sum(parsed["late"])
                    map_n += len(parsed["map_agree"])
                    map_agree_n += sum(parsed["map_agree"])
            except_w.append(exceptions)
            identities.flush(identity_w)
            resolved = resolve_reports_arrays(oi_cid, oi_ts, oi_val, oi_fid, oi_row)
            dte_by_cid, bucket_by_cid, right_by_cid = {}, {}, {}
            for cid, dte, bucket, right in zip(oi_cid, oi_dte, oi_bucket, oi_right):
                dte_by_cid[cid] = dte
                bucket_by_cid[cid] = bucket
                right_by_cid[cid] = right
            listed_set = set(listing_ids)
            report_rows = [{
                "contract_id": cid, "chain": chain, "request_date": label,
                "listed": cid in listed_set, **payload,
                "dte": dte_by_cid.get(cid), "dte_bucket": bucket_by_cid.get(cid),
                "right": right_by_cid.get(cid), "causal_feature_eligible": False,
            } for cid, payload in resolved.items()]
            report_w.append(report_rows)
            oi_keys = set(resolved)
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
            zeros = sum(1 for row in report_rows if row["first_oi"] == 0 or row["last_oi"] == 0)
            gt60 = sum(1 for dte in dte_by_cid.values() if dte is not None and dte > 60)
            agg = _empty_date(chain, label, intended, closed, primary)
            agg.update({
                "listing_count": listing_count, "oi_count": oi_count, "oi_zero_count": zeros,
                "intersection_count": inter, "union_count": union, "listed_without_oi": listed_wo,
                "oi_without_listing": oi_wo, "listing_denominator_known": denom_known,
                "coverage_listed_with_oi": coverage, "invalid_row_count": len(exceptions),
                "missing_clock_count": missing_clock_n, "event_local_mismatch_count": mismatch_n,
                "future_flag_count": future_n, "late_flag_count": late_n,
                "usable_report_count": sum(1 for row in report_rows if row["usable_for_statistics"]),
                "conflict_report_count": sum(1 for row in report_rows if row["same_time_conflict"]),
                "update_candidate_count": sum(1 for row in report_rows if row["update_candidate"]),
                "update_diff_sum": sum((row["observed_update_difference"] or 0)
                                       for row in report_rows if row["update_candidate"]),
                "update_n": sum(1 for row in report_rows if row["update_candidate"]),
                "gt60_dte_retained": gt60,
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
                "coverage_listed_with_oi": coverage, "invalid_row_count": len(exceptions),
                "missing_clock_count": missing_clock_n, "event_local_mismatch_count": mismatch_n,
                "future_flag_count": future_n, "late_flag_count": late_n,
                "usable_report_count": agg["usable_report_count"],
                "conflict_report_count": agg["conflict_report_count"],
                "update_candidate_count": agg["update_candidate_count"],
                "gt60_dte_retained": gt60, "vix_listing_unknown": not listing_known,
                "position_mapping_agree_count": map_agree_n, "position_mapping_count": map_n,
            })
            asof.add(oi_cid, oi_ts, oi_val, oi_req, oi_fid, oi_row, oi_exp)
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
                    closed_intervals.extend(asof.purge_expired(label, midnight))
                    interval_w.append(closed_intervals)
                    counts = asof.snapshot_counts(cut_at, label, listing_ids, prev_cash)
                    agg["asof"][cut_label] = counts
                    asof_agg_w.append([{
                        "chain": chain, "cut_date": label, "cut_label": cut_label, "cut_ns": cut_at,
                        **counts, "causal_feature_eligible": False,
                    }])
            life_rows = []
            if intended:
                next_stage = stage_of(label, stages)
                if prev_intended_date is not None:
                    prior_stage = stage_of(prev_intended_date, stages)
                    life_rows = _join_lifecycle(
                        prev_reports, resolved, prev_listings, listed_set, chain=chain,
                        prior_date=prev_intended_date, next_date=label, last_selected=last_selected,
                        first_selected=first_selected, prior_stage=prior_stage, next_stage=next_stage,
                        listing_known=listing_known, expiration=identities.expiration,
                    )
                else:
                    life_rows = _join_lifecycle(
                        {}, resolved, set(), listed_set, chain=chain, prior_date=None, next_date=label,
                        last_selected=last_selected, first_selected=first_selected, prior_stage=None,
                        next_stage=next_stage, listing_known=listing_known, expiration=identities.expiration,
                    )
                if last_selected == label:
                    prior_stage = stage_of(label, stages)
                    life_rows.extend(_join_lifecycle(
                        resolved, {}, listed_set, set(), chain=chain, prior_date=label, next_date=None,
                        last_selected=last_selected, first_selected=first_selected, prior_stage=prior_stage,
                        next_stage=None, listing_known=listing_known, expiration=identities.expiration,
                    ))
            written_life = []
            for row in life_rows:
                first_life, last_life = row.pop("_first_life"), row.pop("_last_life")
                _tally_bags(agg, first_life, last_life, row["prior_date"], row["next_date"],
                            row["prior_stage"], row["next_stage"], row["is_boundary"])
                written_life.append(row)
            life_w.append(written_life)
            first_secs = _seconds_for_ts([row["first_ts_event_ns"] for row in report_rows], midnight_cache)
            last_secs = _seconds_for_ts([row["last_ts_event_ns"] for row in report_rows], midnight_cache)
            _finish_day_policies(agg, report_rows, first_secs, last_secs)
            if intended:
                prev_reports = resolved
                prev_listings = listed_set
                prev_intended_date = label
            date_aggregates.append(agg)
        # Persist pending future-clock observations too; no selected cut can see
        # an interval before its valid_from/request-date predicate.
        interval_w.append(asof.apply_through(9223372036854775807, "9999-12-31"))
        interval_w.append(list(asof.open.values()))
        identities._key_to_id.clear()
        identities.expiration.clear()
    return finish_measurement_outputs(
        outputs, spec=spec, calendar_ref=calendar_ref, identity_w=identity_w,
        except_w=except_w, member_w=member_w, report_w=report_w, life_w=life_w,
        interval_w=interval_w, asof_agg_w=asof_agg_w,
        coverage_table=_table(coverage_schema(), coverage_rows),
        coverage_kind=OUTPUT_SCHEMAS["coverage"], date_aggregates=date_aggregates,
        consumed=consumed, required_ids=required_ids, manifest=manifest,
        files_read=files_read, rows_read=rows_read, bytes_read=bytes_read,
        source_dates=source_dates, selected_dates=selected_dates,
        intended_all=intended_all, intended_labels=intended_labels, chains=chains,
        listing_unknown_chains=listing_unknown_chains, started_cpu=started_cpu,
        started_wall=started_wall,
        reconstruction_payload={
            "kind": OUTPUT_SCHEMAS["reconstruction"],
            "predicate": INTERVAL_RECONSTRUCTION,
            "output_schemas": OUTPUT_SCHEMAS,
            "identity_map": "contract_id -> chain, osi_symbol, expiration, millistrike, right",
            "valid_rows": "authenticated original /workspace/data files via membership file_id+row_index",
        },
        family=FAMILY, version=VERSION, remaining=REMAINING,
        interval_reconstruction=INTERVAL_RECONSTRUCTION,
        max_worker_bytes=MAX_WORKER_BYTES, max_source_file=MAX_SOURCE_FILE,
    )


def iter_logical_reports(refs):
    from trading_research.research.options_oi_columnar import iter_logical_reports as _fn
    return _fn(refs)


def iter_logical_lifecycle(life_refs, report_refs=None):
    from trading_research.research.options_oi_columnar import iter_logical_lifecycle as _fn
    return _fn(life_refs, report_refs)


def read_logical_parts(refs, report_refs=None):
    from trading_research.research.options_oi_columnar import read_logical_parts as _fn
    return _fn(refs, report_refs)


__all__ = [
    "INTERVAL_RECONSTRUCTION", "OUTPUT_SCHEMAS", "VERSION", "adjacent_lifecycle",
    "build_calendar_index", "contract_key", "cut_ns_on", "dte_bucket", "dte_days",
    "eastern_date_from_ns", "intended_cash_dates", "iter_logical_lifecycle",
    "iter_logical_reports", "load_calendar", "map_unique_eastern",
    "millistrike", "parse_osi", "previous_intended", "read_logical_parts",
    "reconstruct_asof", "reconstruct_asof_intervals", "resolve_contract_report", "run",
    "select_asof_observation", "sourceclock_asof_eligible", "stage_of",
    "timestamp_ns_from_arrow", "utc_date_from_ns",
]



