"""Options OI report/lifecycle measurement.

Source-clock scenarios only. Verified known_at/received_at/published_at and
position_date stay NULL; causal_feature_eligible is always false. Typed
label_ledger.OIReport / oi_endpoint and measurements.oi_report_proxy.OIReportChanges
require certified clocks and supersedes semantics that these sources do not
provide; this module does not fabricate those fields to call them.

Quotes, IV, flow, Greek exposures, dealer ownership and Context fits remain
separate pending branches.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, time, timedelta
from pathlib import Path
import hashlib
import json
import time as pytime

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.options_oi_statistics import run_statistics


VERSION = "options-oi-report-lifecycle-measurement-v1"
FAMILY = "Research-Options-OI-report-lifecycle-v1"
ADMITTED_KIND = "options_oi_admitted_sources_v1"
CONTRACT_KIND = "options_oi_report_lifecycle_contract_v1"
ZONE = "America/New_York"
DEFAULT_DATA_ROOT = "/workspace/data"
MAX_SOURCE_FILE = 16 * 1024 * 1024
MAX_WORKER_BYTES = 4 * 1024 ** 3
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


def _pa():
    import pyarrow as pa
    return pa


def _pc():
    import pyarrow.compute as pc
    return pc


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


def intended_cash_dates(calendar, first, last):
    if type(first) is str:
        first = date.fromisoformat(first)
    if type(last) is str:
        last = date.fromisoformat(last)
    cut = local_timestamp(date(2026, 9, 4), time(0), calendar.zone)
    out = []
    day = first
    while day <= last:
        if calendar.resolve(day, cut=cut).state != "closed":
            out.append(day)
        day += timedelta(days=1)
    return tuple(out)


def previous_intended(intended, day):
    if type(day) is str:
        day = date.fromisoformat(day)
    prev = None
    for item in intended:
        if item >= day:
            return prev
        prev = item
    return prev if prev is not None and prev < day else None


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
    if type(osi) is not str or len(osi) < 21:
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
    if value is None:
        return None
    try:
        return int(round(float(value) * 1000.0))
    except (TypeError, ValueError, OverflowError):
        return None


def contract_key(chain, osi, expiration, strike, right):
    return (chain, osi, expiration, millistrike(strike), right)


def timestamp_ns_from_arrow(column):
    """Cast Arrow timestamp directly to int64 ns. Never via datetime or float."""
    pa = _pa()
    if column is None:
        return None
    if pa.types.is_timestamp(column.type):
        return column.cast(pa.int64())
    if pa.types.is_integer(column.type):
        return column.cast(pa.int64())
    raise ContractError("ts_event must be an Arrow timestamp or int64 nanoseconds")


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


def seconds_after_eastern_midnight(ts_event_ns, eastern_date):
    if ts_event_ns is None or eastern_date is None:
        return None
    midnight = local_timestamp(date.fromisoformat(eastern_date), time(0), ZONE)
    return (ts_event_ns - midnight) / 1_000_000_000


def sourceclock_asof_eligible(ts_event_ns, request_date, cut_ns, cut_date):
    if ts_event_ns is None or request_date is None:
        return False
    return ts_event_ns <= cut_ns and request_date <= cut_date


def select_asof_observation(observations, cut_ns, cut_date):
    """Last source-clock row at or before the cut. Same-time conflicts stay ambiguous."""
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
    appearance = "continuing"
    if prior is None:
        appearance = "first_observed"
    censor = None
    if right_boundary and current is None:
        censor = "right_source_boundary"
    elif expired and current is None:
        censor = "expired_before_next_request_date"
    elif current is None:
        censor = "missing_next_publication"
    elif prior is None:
        censor = "prior_report_missing"
        if left_boundary:
            censor = "left_source_boundary"
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
    return {
        "censor": censor,
        "delta": delta,
        "abs_delta": None if delta is None else abs(delta),
        "usable_for_statistics": usable_pair,
        "within_stage_stat_eligible": usable_pair and prior_stage is not None and prior_stage == next_stage,
        "within_year_stat_eligible": usable_pair and prior_date[:4] == (next_date[:4] if next_date else ""),
        "appearance": appearance,
        "prior_report_missing": prior is None,
        "listed_on_prior": listed_on_prior,
        "certified_listing_birth": False,
        "intraday_terminal_holdings_identified": False,
        "clock_order_ok": clock_ok,
        "expired_before_next": expired,
        "right_source_boundary": bool(right_boundary and current is None),
        "cross_gap_compressed": False,
    }


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
        return pa.types.is_timestamp(arrow_type) or pa.types.is_integer(arrow_type)
    return True


def _check_schema(table, schema_str, required):
    declared = dict(_schema_fields(schema_str))
    names = set(table.schema.names)
    missing = [name for name in required if name not in names or name not in declared]
    if missing:
        raise IntegrityError("admitted source missing required columns: " + ",".join(missing))
    for name in required:
        field = table.schema.field(name)
        if not _type_ok(field.type, declared[name]):
            raise IntegrityError(f"admitted source column {name} changed type")


def _data_root(protocol):
    root = Path(protocol.get("data_root", DEFAULT_DATA_ROOT)).resolve()
    return root


def _resolve_source_path(protocol, relative):
    if type(relative) is not str or not relative or relative.startswith("/") or ".." in Path(relative).parts:
        raise ContractError("source path must be a relative /workspace/data path")
    root = _data_root(protocol)
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        raise IntegrityError("source path escaped data root")
    return path


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
    if fmt == ".parquet":
        import pyarrow.parquet as pq
        table = pq.read_table(_pa().BufferReader(raw))
    elif fmt == ".json":
        payload = json.loads(raw.decode())
        rows = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
        if type(rows) is not list:
            raise ContractError("JSON source must be a row list")
        table = _pa().Table.from_pylist(rows)
    else:
        raise ContractError("source format must be .parquet or .json")
    required = OI_FIELDS if source["role"] == "open_interest" else CONTRACT_FIELDS
    schema_id = record["schema_id"]
    schemas = protocol.get("admitted_schemas") or {}
    return table, {"path": source["path"], "sha256": digest, "size_bytes": size,
                   "rows": len(table), "file_id": record["file_id"], "schema_id": schema_id,
                   "format": fmt, **({} if not schemas else {})}


def _column(table, name):
    return table.column(name) if name in table.schema.names else None


def parse_source_table(table, *, record, schema_str, intended_index, stages):
    """Parse one source table into compact row tuples. Invalid rows stay with reasons."""
    source = record["source"]
    role = source["role"]
    chain = source["chain"]
    file_id = record["file_id"]
    declared_request = source["request_date"]
    required = OI_FIELDS if role == "open_interest" else CONTRACT_FIELDS
    _check_schema(table, schema_str, required)
    n = len(table)
    symbols = _column(table, "symbol").to_pylist() if _column(table, "symbol") is not None else [None] * n
    osi = _column(table, "osi_symbol").to_pylist()
    rights = _column(table, "right").to_pylist()
    strikes = _column(table, "strike").to_pylist()
    expirations = _date_strings(_column(table, "expiration")).to_pylist()
    request_dates = _date_strings(_column(table, "request_date")).to_pylist()
    if role == "open_interest":
        oi_col = _column(table, "open_interest")
        open_interest = oi_col.cast(_pa().int64()).to_pylist() if oi_col is not None else [None] * n
        ts_col = timestamp_ns_from_arrow(_column(table, "ts_event"))
        ts_event = ts_col.to_pylist()
        east = eastern_date_from_ns(ts_event)
        utc = utc_date_from_ns(ts_event)
    else:
        open_interest = [None] * n
        ts_event = [None] * n
        east = [None] * n
        utc = [None] * n
    rows = []
    for index in range(n):
        reason = None
        right = normalize_right(rights[index])
        exp = expirations[index]
        req = request_dates[index]
        osi_s = osi[index]
        strike = strikes[index]
        parsed = parse_osi(osi_s) if type(osi_s) is str else None
        milli = millistrike(strike)
        if osi_s is None or exp is None or right is None or milli is None:
            reason = "missing_identity_fields"
        elif parsed is None:
            reason = "unparseable_osi"
        elif (parsed["expiration"] != exp or parsed["right"] != right
              or parsed["millistrike"] != milli):
            reason = "strike_or_osi_identity_conflict"
        elif type(symbols[index]) is str and symbols[index] != chain:
            reason = "symbol_chain_mismatch"
        if req != declared_request:
            reason = "wrong_request_date" if reason is None else reason
        oi_value = open_interest[index]
        ts = ts_event[index]
        disposition = "listing" if role == "contracts" else "oi"
        if role == "open_interest":
            if oi_value is None:
                reason = "missing_open_interest" if reason is None else reason
                disposition = "missing_oi"
            elif type(oi_value) is not int:
                reason = "non_integer_open_interest" if reason is None else reason
                disposition = "invalid_oi"
            elif oi_value < 0:
                reason = "negative_open_interest" if reason is None else reason
                disposition = "invalid_negative"
            elif ts is None:
                reason = "missing_clock" if reason is None else reason
                disposition = "missing_clock"
            elif oi_value == 0:
                disposition = "valid_zero"
            else:
                disposition = "valid_positive"
        valid = reason is None
        mismatch = bool(ts is not None and east[index] is not None and req is not None and east[index] != req)
        future = bool(ts is not None and east[index] is not None and req is not None and east[index] > req)
        utc_next = bool(ts is not None and utc[index] is not None and req is not None and utc[index] > req)
        seconds = seconds_after_eastern_midnight(ts, east[index]) if ts is not None else None
        late = bool(seconds is not None and seconds > 15 * 3600)
        dte = None if exp is None or req is None else dte_days(exp, req)
        pos_req = previous_intended(intended_index, req).isoformat() if req and previous_intended(intended_index, req) else None
        pos_evt = None
        if east[index]:
            prev_e = previous_intended(intended_index, east[index])
            pos_evt = prev_e.isoformat() if prev_e else None
        rows.append({
            "file_id": file_id, "row_index": index, "chain": chain, "role": role,
            "request_date": req, "symbol": symbols[index], "osi_symbol": osi_s,
            "expiration": exp, "strike": strike, "right": right, "open_interest": oi_value,
            "ts_event_ns": ts, "parsed_valid": valid, "invalid_reason": reason,
            "disposition": disposition, "event_eastern_date": east[index],
            "event_utc_date": utc[index], "event_local_date_mismatch": mismatch,
            "future_flag": future, "late_flag": late, "utc_next_day_flag": utc_next,
            "seconds_after_eastern_midnight": seconds, "dte": dte,
            "dte_bucket": dte_bucket(dte), "known_at_ns": None, "received_at_ns": None,
            "published_at_ns": None, "position_date": None, "causal_feature_eligible": False,
            "position_date_by_request": pos_req, "position_date_by_event": pos_evt,
            "position_mapping_agrees": pos_req is not None and pos_req == pos_evt,
            "stage": stage_of(req, stages) if req else None,
        })
    return rows


RAW_COLUMNS = (
    "file_id", "row_index", "chain", "role", "request_date", "symbol", "osi_symbol",
    "expiration", "strike", "right", "open_interest", "ts_event_ns", "parsed_valid",
    "invalid_reason", "disposition", "event_eastern_date", "event_utc_date",
    "event_local_date_mismatch", "future_flag", "late_flag", "utc_next_day_flag",
    "seconds_after_eastern_midnight", "dte", "dte_bucket", "known_at_ns",
    "received_at_ns", "published_at_ns", "position_date", "causal_feature_eligible",
    "position_date_by_request", "position_date_by_event", "position_mapping_agrees",
    "stage", "alias_multiplicity", "same_time_conflict",
)


def raw_schema():
    pa = _pa()
    return pa.schema([
        ("file_id", pa.int64()), ("row_index", pa.int64()), ("chain", pa.string()),
        ("role", pa.string()), ("request_date", pa.string()), ("symbol", pa.string()),
        ("osi_symbol", pa.string()), ("expiration", pa.string()), ("strike", pa.float64()),
        ("right", pa.string()), ("open_interest", pa.int64()), ("ts_event_ns", pa.int64()),
        ("parsed_valid", pa.bool_()), ("invalid_reason", pa.string()), ("disposition", pa.string()),
        ("event_eastern_date", pa.string()), ("event_utc_date", pa.string()),
        ("event_local_date_mismatch", pa.bool_()), ("future_flag", pa.bool_()),
        ("late_flag", pa.bool_()), ("utc_next_day_flag", pa.bool_()),
        ("seconds_after_eastern_midnight", pa.float64()), ("dte", pa.int64()),
        ("dte_bucket", pa.string()), ("known_at_ns", pa.int64()), ("received_at_ns", pa.int64()),
        ("published_at_ns", pa.int64()), ("position_date", pa.string()),
        ("causal_feature_eligible", pa.bool_()), ("position_date_by_request", pa.string()),
        ("position_date_by_event", pa.string()), ("position_mapping_agrees", pa.bool_()),
        ("stage", pa.string()), ("alias_multiplicity", pa.int64()),
        ("same_time_conflict", pa.bool_()),
    ])


def report_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("request_date", pa.string()), ("osi_symbol", pa.string()),
        ("expiration", pa.string()), ("strike", pa.float64()), ("right", pa.string()),
        ("first_oi", pa.int64()), ("first_ts_event_ns", pa.int64()),
        ("first_file_id", pa.int64()), ("first_row_index", pa.int64()),
        ("last_oi", pa.int64()), ("last_ts_event_ns", pa.int64()),
        ("last_file_id", pa.int64()), ("last_row_index", pa.int64()),
        ("alias_multiplicity", pa.int64()), ("same_time_conflict", pa.bool_()),
        ("conflict_disposition", pa.string()), ("update_candidate", pa.bool_()),
        ("observed_update_difference", pa.int64()), ("certified_revision", pa.bool_()),
        ("usable_for_statistics", pa.bool_()), ("n_source_rows", pa.int64()),
        ("n_distinct_times", pa.int64()), ("support_observations", pa.int64()),
        ("dte", pa.int64()), ("dte_bucket", pa.string()), ("stage", pa.string()),
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
    ])


def asof_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("cut_date", pa.string()), ("cut_label", pa.string()),
        ("cut_ns", pa.int64()), ("osi_symbol", pa.string()), ("expiration", pa.string()),
        ("strike", pa.float64()), ("right", pa.string()), ("open_interest", pa.int64()),
        ("ts_event_ns", pa.int64()), ("request_date", pa.string()),
        ("file_id", pa.int64()), ("row_index", pa.int64()), ("eligible", pa.bool_()),
        ("age_ns", pa.int64()), ("stale", pa.bool_()), ("ambiguous", pa.bool_()),
        ("causal_feature_eligible", pa.bool_()), ("used_future_report", pa.bool_()),
        ("dte_bucket", pa.string()),
    ])


def lifecycle_schema():
    pa = _pa()
    return pa.schema([
        ("chain", pa.string()), ("policy", pa.string()), ("prior_date", pa.string()),
        ("next_date", pa.string()), ("osi_symbol", pa.string()), ("expiration", pa.string()),
        ("strike", pa.float64()), ("right", pa.string()),
        ("prior_oi", pa.int64()), ("next_oi", pa.int64()),
        ("prior_ts_event_ns", pa.int64()), ("next_ts_event_ns", pa.int64()),
        ("prior_file_id", pa.int64()), ("prior_row_index", pa.int64()),
        ("next_file_id", pa.int64()), ("next_row_index", pa.int64()),
        ("delta", pa.int64()), ("abs_delta", pa.int64()), ("censor", pa.string()),
        ("usable_for_statistics", pa.bool_()), ("within_stage_stat_eligible", pa.bool_()),
        ("within_year_stat_eligible", pa.bool_()), ("appearance", pa.string()),
        ("prior_report_missing", pa.bool_()), ("listed_on_prior", pa.bool_()),
        ("certified_listing_birth", pa.bool_()),
        ("intraday_terminal_holdings_identified", pa.bool_()),
        ("cross_gap_compressed", pa.bool_()), ("dte_bucket", pa.string()),
        ("prior_stage", pa.string()), ("next_stage", pa.string()),
        ("causal_feature_eligible", pa.bool_()),
    ])


def _arrow_table(schema, rows):
    pa = _pa()
    if not rows:
        return schema.empty_table()
    columns = {field.name: [row.get(field.name) for row in rows] for field in schema}
    return pa.table(columns, schema=schema)


class MonthWriter:
    def __init__(self, outputs, prefix, schema, kind):
        self.outputs, self.prefix, self.schema, self.kind = outputs, prefix, schema, kind
        self.key = None
        self.batches = []
        self.refs = []
        self.rows = 0

    def append(self, rows, month_key):
        if not rows:
            return
        if self.key is not None and month_key != self.key:
            self.flush()
        self.key = month_key
        self.batches.append(_arrow_table(self.schema, rows))

    def flush(self):
        if not self.batches:
            self.key = None
            return
        import pyarrow as pa
        import pyarrow.parquet as pq
        table = pa.concat_tables(self.batches)
        name = f"{self.prefix}-{self.key}.parquet"
        stream = self.outputs.create(name)
        try:
            pq.write_table(table, stream, compression="zstd")
        finally:
            stream.close()
        ref = self.outputs.reference(name, kind=self.kind)
        self.refs.append({**ref, "rows": len(table), "month": self.key})
        self.rows += len(table)
        self.batches = []
        self.key = None

    def finish(self):
        self.flush()
        return self.refs


def _month(request_date):
    return request_date[:7] if request_date else "unknown"


def _empty_date(chain, request_date, intended, closed, primary):
    return {
        "chain": chain, "request_date": request_date, "intended": intended,
        "closed": closed, "primary": primary,
        "first": _policy_acc(), "last": _policy_acc(),
        "lifecycle_first_first": _life_acc(), "lifecycle_last_last": _life_acc(),
        "asof": {}, "listing_count": None, "oi_count": None, "oi_zero_count": 0,
        "intersection_count": None, "union_count": None, "listed_without_oi": None,
        "oi_without_listing": None, "listing_denominator_known": False,
        "coverage_listed_with_oi": None, "invalid_row_count": 0,
        "missing_clock_count": 0, "event_local_mismatch_count": 0,
        "future_flag_count": 0, "late_flag_count": 0, "usable_report_count": 0,
        "conflict_report_count": 0, "update_candidate_count": 0, "gt60_dte_retained": 0,
        "by_right": {}, "by_dte": {},
    }


def _policy_acc():
    return {"oi_sum": 0, "oi_n": 0, "zero_n": 0, "seconds_sum": 0.0, "seconds_n": 0,
            "usable_n": 0, "common_n": 0, "common_first_sum": 0, "common_last_sum": 0,
            "paired_diff_sum": 0}


def _life_acc():
    return {"delta_sum": 0, "abs_sum": 0, "n": 0, "n_pos": 0, "n_zero": 0, "n_neg": 0,
            "n_censor_missing": 0, "n_censor_expired": 0, "n_censor_boundary": 0,
            "n_attempts": 0, "n_first_observed": 0, "n_prior_missing": 0,
            "n_stage_cross": 0, "n_year_cross": 0}


def _add_policy(acc, report, policy):
    oi = report[f"{policy}_oi"]
    ts = report[f"{policy}_ts_event_ns"]
    if not report["usable_for_statistics"] or oi is None:
        return
    acc["oi_sum"] += oi
    acc["oi_n"] += 1
    acc["zero_n"] += int(oi == 0)
    acc["usable_n"] += 1
    seconds = report.get(f"{policy}_seconds_after_eastern_midnight")
    if seconds is None and ts is not None:
        east = eastern_date_from_ns([ts])[0]
        seconds = seconds_after_eastern_midnight(ts, east)
    if seconds is not None:
        acc["seconds_sum"] += seconds
        acc["seconds_n"] += 1


def _group_key(row):
    return contract_key(row["chain"], row["osi_symbol"], row["expiration"], row["strike"], row["right"])


def _endpoint(report, policy):
    return {
        "open_interest": report[f"{policy}_oi"],
        "ts_event_ns": report[f"{policy}_ts_event_ns"],
        "file_id": report[f"{policy}_file_id"],
        "row_index": report[f"{policy}_row_index"],
        "usable_for_statistics": report["usable_for_statistics"],
        "expiration": report["expiration"],
        "osi_symbol": report["osi_symbol"],
        "strike": report["strike"],
        "right": report["right"],
        "dte_bucket": report["dte_bucket"],
    }


def _life_row(chain, policy, prior_date, next_date, identity, prior_ep, next_ep, life, prior_stage, next_stage):
    return {
        "chain": chain, "policy": policy, "prior_date": prior_date, "next_date": next_date,
        "osi_symbol": identity[1], "expiration": identity[2],
        "strike": None if identity[3] is None else identity[3] / 1000.0,
        "right": identity[4],
        "prior_oi": None if prior_ep is None else prior_ep["open_interest"],
        "next_oi": None if next_ep is None else next_ep["open_interest"],
        "prior_ts_event_ns": None if prior_ep is None else prior_ep["ts_event_ns"],
        "next_ts_event_ns": None if next_ep is None else next_ep["ts_event_ns"],
        "prior_file_id": None if prior_ep is None else prior_ep["file_id"],
        "prior_row_index": None if prior_ep is None else prior_ep["row_index"],
        "next_file_id": None if next_ep is None else next_ep["file_id"],
        "next_row_index": None if next_ep is None else next_ep["row_index"],
        "delta": life["delta"], "abs_delta": life["abs_delta"], "censor": life["censor"],
        "usable_for_statistics": life["usable_for_statistics"],
        "within_stage_stat_eligible": life["within_stage_stat_eligible"],
        "within_year_stat_eligible": life["within_year_stat_eligible"],
        "appearance": life["appearance"], "prior_report_missing": life["prior_report_missing"],
        "listed_on_prior": life["listed_on_prior"], "certified_listing_birth": False,
        "intraday_terminal_holdings_identified": False, "cross_gap_compressed": False,
        "dte_bucket": None if prior_ep is None else prior_ep.get("dte_bucket"),
        "prior_stage": prior_stage, "next_stage": next_stage, "causal_feature_eligible": False,
    }


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
    elif life["censor"] in {"right_source_boundary", "left_source_boundary"}:
        acc["n_censor_boundary"] += 1
    if not life["within_stage_stat_eligible"] and life["delta"] is not None:
        acc["n_stage_cross"] += 1
    if not life["within_year_stat_eligible"] and life["delta"] is not None:
        acc["n_year_cross"] += 1
    if life["delta"] is None:
        return
    acc["n"] += 1
    acc["delta_sum"] += life["delta"]
    acc["abs_sum"] += life["abs_delta"]
    acc["n_pos"] += int(life["delta"] > 0)
    acc["n_zero"] += int(life["delta"] == 0)
    acc["n_neg"] += int(life["delta"] < 0)


def _validate_admitted(admitted, protocol, selected):
    if not isinstance(admitted, dict) or admitted.get("kind") != ADMITTED_KIND:
        raise ContractError("admitted options_oi_admitted_sources_v1 required")
    sources = admitted.get("sources")
    if type(sources) is not list:
        raise ContractError("admitted sources list required")
    if admitted.get("source_files") != len(sources):
        raise IntegrityError("admitted source_files count does not match sources")
    seen = set()
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
    return sources


def _write_table(outputs, name, table, kind):
    import pyarrow.parquet as pq
    stream = outputs.create(name)
    try:
        pq.write_table(table, stream, compression="zstd")
    finally:
        stream.close()
    return {**outputs.reference(name, kind=kind), "rows": len(table)}


def run(*, protocol: dict, admitted: dict, outputs: BoundedOutputs, selected_dates: list[str] | None = None) -> dict:
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError("registered BoundedOutputs required")
    started_wall = pytime.perf_counter()
    started_cpu = pytime.process_time()
    spec = contract(protocol)
    calendar, calendar_ref = load_calendar(protocol)
    population = spec["population"]
    stages = population["stages"]
    chains = tuple(population["chains"])
    cuts = tuple(spec["clocks"]["asof_cuts_local"])
    intended_all = intended_cash_dates(calendar, population["first_date"], population["last_date"])
    intended_index = intended_all
    if selected_dates is not None:
        if type(selected_dates) is not list or any(type(item) is not str for item in selected_dates):
            raise ContractError("selected_dates must be ISO date strings or None")
        if len(set(selected_dates)) != len(selected_dates):
            raise ContractError("selected_dates contains duplicates")
    sources = _validate_admitted(admitted, protocol, selected_dates)
    schemas = admitted.get("schemas")
    if not isinstance(schemas, dict):
        raise ContractError("admitted schemas mapping required")
    selected_set = None if selected_dates is None else set(selected_dates)
    by_chain = {chain: defaultdict(dict) for chain in chains}
    acquired_dates = {chain: set() for chain in chains}
    for record in sources:
        source = record["source"]
        if selected_set is not None and source["request_date"] not in selected_set:
            continue
        by_chain[source["chain"]][source["request_date"]][source["role"]] = record
        acquired_dates[source["chain"]].add(source["request_date"])
    work_dates = {}
    for chain in chains:
        intended = intended_all if selected_dates is None else tuple(date.fromisoformat(d) for d in selected_dates)
        extra = sorted(acquired_dates[chain] - {d.isoformat() for d in intended})
        work_dates[chain] = tuple(sorted({*intended, *(date.fromisoformat(d) for d in extra)}))
    raw_w = MonthWriter(outputs, "raw", raw_schema(), "options_oi_raw_observations_v1")
    report_w = MonthWriter(outputs, "reports", report_schema(), "options_oi_resolved_reports_v1")
    asof_w = MonthWriter(outputs, "asof", asof_schema(), "options_oi_sourceclock_asof_v1")
    life_w = MonthWriter(outputs, "lifecycle", lifecycle_schema(), "options_oi_lifecycle_v1")
    coverage_rows = []
    date_aggregates = []
    manifest = []
    files_read = rows_read = bytes_read = 0
    source_dates = []
    listing_unknown_chains = set()
    for chain in chains:
        if chain in CHAINS_WITHOUT_LISTING:
            listing_unknown_chains.add(chain)
        intended_labels = {d.isoformat() for d in (intended_all if selected_dates is None else tuple(date.fromisoformat(x) for x in selected_dates))}
        last_selected = max(intended_labels) if intended_labels else None
        first_selected = min(intended_labels) if intended_labels else None
        prev_reports = {}
        prev_listings = set()
        prev_intended_date = None
        carry = {}
        for day in work_dates[chain]:
            label = day.isoformat()
            intended = label in {d.isoformat() for d in intended_all}
            closed = calendar.resolve(day, cut=local_timestamp(date(2026, 9, 4), time(0), calendar.zone)).state == "closed"
            primary = intended and population["first_date"] <= label <= population["last_date"]
            files = by_chain[chain].get(label, {})
            day_rows = []
            for role in ("contracts", "open_interest"):
                record = files.get(role)
                if record is None:
                    continue
                schema_str = schemas.get(record["schema_id"])
                if type(schema_str) is not str:
                    raise IntegrityError("admitted schema_id is not in schemas")
                table, meta = read_admitted_source(protocol, record)
                if record.get("rows") is not None and meta["rows"] != record["rows"]:
                    raise IntegrityError("admitted row count does not match the decoded table")
                files_read += 1
                rows_read += meta["rows"]
                bytes_read += meta["size_bytes"]
                source_dates.append(label)
                manifest.append({
                    "file_id": record["file_id"], "path": record["source"]["path"],
                    "sha256": record["sha256"], "size_bytes": record["source"]["size_bytes"],
                    "chain": chain, "role": role, "request_date": label,
                    "dataset_id": record["source"]["dataset_id"], "schema_id": record["schema_id"],
                    "format": record["format"], "rows_read": meta["rows"],
                })
                day_rows.extend(parse_source_table(
                    table, record=record, schema_str=schema_str,
                    intended_index=intended_index, stages=stages,
                ))
            listings, oi_rows = {}, defaultdict(list)
            for row in day_rows:
                if row["parsed_valid"] and row["role"] == "contracts":
                    listings[_group_key(row)] = row
                if row["role"] == "open_interest" and row["parsed_valid"] and row["open_interest"] is not None:
                    if row["disposition"] in {"valid_zero", "valid_positive"}:
                        oi_rows[_group_key(row)].append(row)
            reports = {}
            for key, group in oi_rows.items():
                resolved = resolve_contract_report(group)
                sample = group[0]
                for row in group:
                    row["alias_multiplicity"] = resolved["alias_multiplicity"]
                    row["same_time_conflict"] = resolved["same_time_conflict"]
                first_east = eastern_date_from_ns([resolved["first_ts_event_ns"]])[0] if resolved["first_ts_event_ns"] is not None else None
                last_east = eastern_date_from_ns([resolved["last_ts_event_ns"]])[0] if resolved["last_ts_event_ns"] is not None else None
                report = {
                    "chain": chain, "request_date": label, "osi_symbol": sample["osi_symbol"],
                    "expiration": sample["expiration"], "strike": sample["strike"],
                    "right": sample["right"], **resolved, "dte": sample["dte"],
                    "dte_bucket": sample["dte_bucket"], "stage": sample["stage"],
                    "causal_feature_eligible": False,
                    "event_eastern_date": sample["event_eastern_date"],
                    "first_seconds_after_eastern_midnight": seconds_after_eastern_midnight(
                        resolved["first_ts_event_ns"], first_east),
                    "last_seconds_after_eastern_midnight": seconds_after_eastern_midnight(
                        resolved["last_ts_event_ns"], last_east),
                }
                reports[key] = report
            for row in day_rows:
                row.setdefault("alias_multiplicity", 1)
                row.setdefault("same_time_conflict", False)
            listing_known = chain not in CHAINS_WITHOUT_LISTING
            listing_present = "contracts" in files
            oi_present = "open_interest" in files
            oi_keys = set(reports)
            list_keys = set(listings) if listing_known and listing_present else set()
            if not listing_known:
                listing_status = "unknown"
                listing_count = None
                denom_known = False
                inter = None
                union = None
                listed_wo = None
                oi_wo = None
                coverage = None
            elif not listing_present:
                listing_status = "absent"
                listing_count = None
                denom_known = False
                inter = None
                union = None
                listed_wo = None
                oi_wo = None
                coverage = None
            else:
                listing_status = "present"
                listing_count = len(list_keys)
                denom_known = True
                inter = len(list_keys & oi_keys)
                union = len(list_keys | oi_keys)
                listed_wo = len(list_keys - oi_keys)
                oi_wo = len(oi_keys - list_keys)
                coverage = None if listing_count == 0 else inter / listing_count
            if not oi_present:
                oi_status = "absent_file"
                oi_count = None
            elif not oi_keys:
                oi_status = "unknown_no_rows"
                oi_count = None
            else:
                oi_status = "present"
                oi_count = len(oi_keys)
            if not listing_known:
                listing_count = None
            zeros = sum(1 for report in reports.values() if report["last_oi"] == 0 or report["first_oi"] == 0)
            gt60 = sum(1 for report in reports.values() if report["dte"] is not None and report["dte"] > 60)
            agg = _empty_date(chain, label, intended, closed, primary)
            agg.update({
                "listing_count": listing_count, "oi_count": oi_count, "oi_zero_count": zeros,
                "intersection_count": inter, "union_count": union, "listed_without_oi": listed_wo,
                "oi_without_listing": oi_wo, "listing_denominator_known": denom_known,
                "coverage_listed_with_oi": coverage,
                "invalid_row_count": sum(1 for row in day_rows if not row["parsed_valid"]),
                "missing_clock_count": sum(1 for row in day_rows if row["disposition"] == "missing_clock"),
                "event_local_mismatch_count": sum(1 for row in day_rows if row["event_local_date_mismatch"]),
                "future_flag_count": sum(1 for row in day_rows if row["future_flag"]),
                "late_flag_count": sum(1 for row in day_rows if row["late_flag"]),
                "usable_report_count": sum(1 for report in reports.values() if report["usable_for_statistics"]),
                "conflict_report_count": sum(1 for report in reports.values() if report["same_time_conflict"]),
                "update_candidate_count": sum(1 for report in reports.values() if report["update_candidate"]),
                "gt60_dte_retained": gt60,
            })
            coverage_rows.append({
                "chain": chain, "request_date": label, "intended": intended, "closed": closed,
                "primary": primary, "listing_file_present": listing_present,
                "oi_file_present": oi_present, "both_files_absent": not listing_present and not oi_present,
                "listing_status": listing_status, "oi_status": oi_status,
                "listing_count": listing_count, "oi_count": oi_count, "oi_zero_count": zeros,
                "intersection_count": inter, "union_count": union, "listed_without_oi": listed_wo,
                "oi_without_listing": oi_wo, "listing_denominator_known": denom_known,
                "coverage_listed_with_oi": coverage,
                "invalid_row_count": agg["invalid_row_count"],
                "missing_clock_count": agg["missing_clock_count"],
                "event_local_mismatch_count": agg["event_local_mismatch_count"],
                "future_flag_count": agg["future_flag_count"], "late_flag_count": agg["late_flag_count"],
                "usable_report_count": agg["usable_report_count"],
                "conflict_report_count": agg["conflict_report_count"],
                "update_candidate_count": agg["update_candidate_count"],
                "gt60_dte_retained": gt60, "vix_listing_unknown": chain in CHAINS_WITHOUT_LISTING,
            })
            asof_rows = []
            if intended:
                prev_cash = previous_intended(intended_index, day)
                stale_before = prev_cash.isoformat() if prev_cash else None
                for cut_label in cuts:
                    cut_at = cut_ns_on(day, cut_label)
                    available = stale = ambiguous = rejected = 0
                    for key, group in oi_rows.items():
                        sample = group[0]
                        picked, status = select_asof_observation(group, cut_at, label)
                        if status == "ok":
                            carry[key] = {
                                "open_interest": picked["open_interest"], "ts_event_ns": picked["ts_event_ns"],
                                "request_date": picked["request_date"], "file_id": picked["file_id"],
                                "row_index": picked["row_index"], "expiration": sample["expiration"],
                                "osi_symbol": sample["osi_symbol"], "strike": sample["strike"],
                                "right": sample["right"], "dte_bucket": sample["dte_bucket"],
                                "ambiguous": False,
                            }
                            ts, oi, fid, ridx = picked["ts_event_ns"], picked["open_interest"], picked["file_id"], picked["row_index"]
                            eligible = True
                            used_future = False
                            is_ambiguous = False
                        else:
                            ts = sample["ts_event_ns"]
                            oi = sample["open_interest"]
                            fid, ridx = sample["file_id"], sample["row_index"]
                            eligible = False
                            used_future = False
                            is_ambiguous = status == "ambiguous"
                            if status == "rejected_future":
                                rejected += 1
                            if status == "ambiguous":
                                ambiguous += 1
                        asof_rows.append({
                            "chain": chain, "cut_date": label, "cut_label": cut_label, "cut_ns": cut_at,
                            "osi_symbol": sample["osi_symbol"], "expiration": sample["expiration"],
                            "strike": sample["strike"], "right": sample["right"],
                            "open_interest": None if not eligible else oi, "ts_event_ns": ts,
                            "request_date": label, "file_id": fid, "row_index": ridx,
                            "eligible": eligible, "age_ns": None if ts is None else cut_at - ts,
                            "stale": bool(eligible and stale_before and picked["request_date"] < stale_before),
                            "ambiguous": is_ambiguous, "causal_feature_eligible": False,
                            "used_future_report": used_future, "dte_bucket": sample["dte_bucket"],
                        })
                    purged = [key for key, held in carry.items()
                              if held.get("expiration") is not None and held["expiration"] < label]
                    for key in purged:
                        del carry[key]
                    for held in carry.values():
                        available += 1
                        ambiguous += int(held.get("ambiguous", False))
                        if stale_before and held["request_date"] < stale_before:
                            stale += 1
                    agg["asof"][cut_label] = {
                        "available": available, "stale": stale, "ambiguous": ambiguous,
                        "rejected_today": rejected, "purged_expired": len(purged),
                    }
            life_rows = []
            if intended and prev_intended_date is not None:
                prior_stage = stage_of(prev_intended_date, stages)
                next_stage = stage_of(label, stages)
                for policy, acc_name in (("first", "lifecycle_first_first"), ("last", "lifecycle_last_last")):
                    seen = set()
                    for key, report in prev_reports.items():
                        prior_ep = _endpoint(report, policy)
                        current = reports.get(key)
                        next_ep = None if current is None else _endpoint(current, policy)
                        life = adjacent_lifecycle(
                            prior_ep, next_ep, prior_date=prev_intended_date, next_date=label,
                            expiration=report["expiration"], last_selected=last_selected,
                            first_selected=first_selected, prior_stage=prior_stage,
                            next_stage=next_stage, listed_on_prior=key in prev_listings if listing_known else None,
                        )
                        life_rows.append(_life_row(
                            chain, f"{policy}_{policy}", prev_intended_date, label, key,
                            prior_ep, next_ep, life, prior_stage, next_stage,
                        ))
                        _tally_life(agg[acc_name], life)
                        seen.add(key)
                    for key, report in reports.items():
                        if key in seen:
                            continue
                        next_ep = _endpoint(report, policy)
                        life = adjacent_lifecycle(
                            None, next_ep, prior_date=prev_intended_date, next_date=label,
                            expiration=report["expiration"], last_selected=last_selected,
                            first_selected=first_selected, prior_stage=prior_stage,
                            next_stage=next_stage, listed_on_prior=False if listing_known else None,
                        )
                        life_rows.append(_life_row(
                            chain, f"{policy}_{policy}", prev_intended_date, label, key,
                            None, next_ep, life, prior_stage, next_stage,
                        ))
                        _tally_life(agg[acc_name], life)
            elif intended and prev_intended_date is None:
                next_stage = stage_of(label, stages)
                for policy, acc_name in (("first", "lifecycle_first_first"), ("last", "lifecycle_last_last")):
                    for key, report in reports.items():
                        next_ep = _endpoint(report, policy)
                        life = adjacent_lifecycle(
                            None, next_ep, prior_date=None, next_date=label,
                            expiration=report["expiration"], last_selected=last_selected,
                            first_selected=first_selected, prior_stage=None,
                            next_stage=next_stage, listed_on_prior=None,
                        )
                        life_rows.append(_life_row(
                            chain, f"{policy}_{policy}", None, label, key,
                            None, next_ep, life, None, next_stage,
                        ))
                        _tally_life(agg[acc_name], life)
            if intended and last_selected == label:
                prior_stage = stage_of(label, stages)
                for policy, acc_name in (("first", "lifecycle_first_first"), ("last", "lifecycle_last_last")):
                    for key, report in reports.items():
                        prior_ep = _endpoint(report, policy)
                        life = adjacent_lifecycle(
                            prior_ep, None, prior_date=label, next_date=None,
                            expiration=report["expiration"], last_selected=last_selected,
                            first_selected=first_selected, prior_stage=prior_stage,
                            next_stage=None, listed_on_prior=key in listings if listing_known else None,
                        )
                        life_rows.append(_life_row(
                            chain, f"{policy}_{policy}", label, None, key,
                            prior_ep, None, life, prior_stage, None,
                        ))
                        _tally_life(agg[acc_name], life)
            for report in reports.values():
                _add_policy(agg["first"], report, "first")
                _add_policy(agg["last"], report, "last")
                if report["usable_for_statistics"] and report["first_oi"] is not None and report["last_oi"] is not None:
                    agg["first"]["common_n"] += 1
                    agg["first"]["common_first_sum"] += report["first_oi"]
                    agg["first"]["common_last_sum"] += report["last_oi"]
                    agg["first"]["paired_diff_sum"] += report["first_oi"] - report["last_oi"]
                    agg["last"]["common_n"] += 1
                    agg["last"]["common_first_sum"] += report["first_oi"]
                    agg["last"]["common_last_sum"] += report["last_oi"]
                    agg["last"]["paired_diff_sum"] += report["first_oi"] - report["last_oi"]
                right_acc = agg["by_right"].setdefault(report["right"] or "unknown", {"first": _policy_acc(), "last": _policy_acc()})
                dte_acc = agg["by_dte"].setdefault(report["dte_bucket"] or "unknown", {"first": _policy_acc(), "last": _policy_acc()})
                _add_policy(right_acc["first"], report, "first")
                _add_policy(right_acc["last"], report, "last")
                _add_policy(dte_acc["first"], report, "first")
                _add_policy(dte_acc["last"], report, "last")
            raw_w.append(day_rows, f"{chain}-{_month(label)}")
            report_w.append(list(reports.values()), f"{chain}-{_month(label)}")
            asof_w.append(asof_rows, f"{chain}-{_month(label)}")
            life_w.append(life_rows, f"{chain}-{_month(label)}")
            if intended:
                prev_reports = reports
                prev_listings = set(listings)
                prev_intended_date = label
            date_aggregates.append(agg)
            day_rows = reports = listings = oi_rows = asof_rows = life_rows = None
    raw_refs = raw_w.finish()
    report_refs = report_w.finish()
    asof_refs = asof_w.finish()
    life_refs = life_w.finish()
    coverage_ref = _write_table(outputs, "coverage.parquet", _arrow_table(coverage_schema(), coverage_rows),
                               "options_oi_coverage_v1")
    aggregates_ref = outputs.json("date-aggregates.json", date_aggregates, kind="options_oi_date_aggregates_v1")
    manifest_ref = outputs.json("source-manifest.json", {
        "kind": "options_oi_source_path_hash_lookup_v1",
        "note": "file_id+row_index recover provenance; source bytes stay in /workspace/data",
        "files": manifest,
    }, kind="options_oi_source_manifest_v1")
    intended_units = sum(
        len(intended_all if selected_dates is None else selected_dates) for _ in chains
    )
    stats = run_statistics(
        date_aggregates, protocol=spec, outputs=outputs,
        intended_all=[d.isoformat() for d in intended_all],
        selected_dates=selected_dates, chains=chains, stages=stages,
        read_counts={
            "source_files_read": files_read, "source_rows_read": rows_read,
            "source_bytes_read": bytes_read, "intended_chain_date_units": intended_units,
        },
    )
    cpu = pytime.process_time() - started_cpu
    wall = pytime.perf_counter() - started_wall
    full_files = sum(item["source_file_count"] for item in spec["source_datasets"])
    full_units = len(intended_all) * len(chains)
    scale = max(files_read or 1, rows_read or 1, intended_units or 1)
    full_scale = max(full_files, full_units, rows_read or 1)
    refs = {
        "calendar": calendar_ref, "source_manifest": manifest_ref, "raw": raw_refs,
        "reports": report_refs, "coverage": coverage_ref, "asof": asof_refs,
        "lifecycle": life_refs, "date_aggregates": aggregates_ref,
        "statistics": stats["refs"]["statistics"], "distributions": stats["refs"]["distributions"],
        "results_md": stats["refs"]["results_md"],
    }
    counts = {
        "source_files_read": files_read, "source_rows_read": rows_read,
        "source_bytes_read": bytes_read, "intended_chain_date_units": intended_units,
        "coverage_rows": len(coverage_rows), "raw_rows": raw_w.rows, "report_rows": report_w.rows,
        "asof_rows": asof_w.rows, "lifecycle_rows": life_w.rows,
        "listing_unknown_chains": sorted(listing_unknown_chains),
        "chains": list(chains),
    }
    return {
        "passed": True,
        "full_family_complete": False,
        "family": FAMILY,
        "version": VERSION,
        "refs": refs,
        "counts": counts,
        "resources": {
            "cpu_seconds": cpu, "wall_seconds": wall, "output_bytes": outputs.written,
            "source_bytes_read": bytes_read, "source_files_read": files_read,
            "source_rows_read": rows_read, "intended_chain_date_units": intended_units,
            "memory_bound_bytes": MAX_WORKER_BYTES, "source_file_bound_bytes": MAX_SOURCE_FILE,
            "full_gate_projection": {
                "scale_read": scale, "scale_full": full_scale, "margin": 1.5,
                "fixed_allowance_seconds": 60,
                "projected_cpu_seconds": cpu * (full_scale / scale) * 1.5 + 60,
                "science_thresholds_unchanged_from_pilot": True,
            },
        },
        "source_dates_processed": sorted(set(source_dates)),
        "selected_dates": selected_dates,
        "remaining_dependencies": list(REMAINING),
        "clock_interpretation": {
            "known_at_ns": None, "received_at_ns": None, "published_at_ns": None,
            "position_date": None, "causal_feature_eligible": False,
            "assumptions": spec["clocks"]["assumptions"],
            "asof": spec["clocks"]["asof"],
        },
    }


__all__ = [
    "VERSION", "adjacent_lifecycle", "contract_key", "cut_ns_on", "dte_bucket",
    "dte_days", "eastern_date_from_ns", "intended_cash_dates", "load_calendar",
    "parse_osi", "previous_intended", "resolve_contract_report", "run",
    "select_asof_observation", "sourceclock_asof_eligible", "stage_of",
    "timestamp_ns_from_arrow", "utc_date_from_ns",
]
