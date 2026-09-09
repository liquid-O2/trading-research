"""Acquired minute-OHLC physical-volatility measurements (Deliverable 1).

Computes session Parkinson / practical Garman–Klass (eq. 19a) / Rogers–Satchell,
Yang–Zhang components, sampled close RV, seasonal elapsed-time cells, and
remaining-window observations from admitted canonical minute OHLC. This is a
measurement and descriptive-statistics family. It is not a Context forecast,
Location evaluation, IV study, tape RV/jump classifier, or first-passage path.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import io
import json
import math
import resource
import time as time_mod
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.operations.artifacts import artifact_ref, digest, file_digest
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.jumbo_tables import cash_dates
from trading_research.research.ohlc_ranges import MINUTE, MinuteBars


VERSION = "physical-ohlc-volatility-acquired-v1"
FAMILY = "Research-Physical-OHLC-Volatility-acquired-v1"
PROTOCOL_KIND = "physical_ohlc_volatility_measurement_contract_v1"
PURPOSE = (
    "acquired-minute-ohlc-physical-volatility-measurement; "
    "not a Context forecast or Location evaluation"
)
TICK_POINTS = 0.25
LN2 = math.log(2.0)
FOUR_LN2 = 4.0 * LN2
TWO_LN2_MINUS_1 = 2.0 * LN2 - 1.0
YZ_K_NUMERATOR = 0.34
YZ_K_BASE = 1.34
SESSIONS = ("cash_rth", "futures_wallclock_18_17", "pre_rth_06_0930")
LOOKBACKS = (20, 60, 120)
SCALES = (1, 5, 15, 60)
REMAINING_CUTS = (5, 15, 30, 60, 120, 240)
FORWARD_MINUTES = (5, 15, 60)
ELAPSED_CELL_MINUTES = 30
STAT_QUANTILES = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
STAT_SEED = 20260908
STAT_BLOCK = 5
STAT_REPLICATES = 1000
STAT_CONFIDENCE = 0.95
STAT_MIN_DATES = 100
STAT_MIN_EVENTS = 20
OUTPUT_RESERVE_BYTES = 16 * 1024 * 1024
OUTPUT_MAX_FILE_BYTES = 128 * 1024 * 1024
PILOT_KEY = ("NQ", 2020, "primary_corrected")
STAGES = (
    ("training", date(2020, 1, 1), date(2023, 1, 1)),
    ("development", date(2023, 1, 1), date(2025, 1, 1)),
    ("confirmation", date(2025, 1, 1), date(2026, 9, 3)),
)
POPULATION_FIRST = date(2020, 1, 1)
POPULATION_LAST = date(2026, 9, 2)
EXPECTED_PRIMARY_CASH_DATES_PER_ROOT = 1676
EXPECTED_ORIGINAL_NQ2024_DATES = 252
EXPECTED_PILOT_DATES = 253
DEFAULT_ZONE = "America/New_York"
SOURCE_LAG_NS = MINUTE
GK19A = "0.5ln(H/L)^2-(2ln2-1)ln(C/O)^2"
PARKINSON_EQ = "ln(H/L)^2/(4ln2)"
RS_EQ = "ln(H/O)*ln(H/C)+ln(L/O)*ln(L/C)"
YZ_EQ = "sample_var(log(O/Cprev),ddof1)+k*sample_var(log(C/O),ddof1)+(1-k)*mean(RS); k=.34/(1.34+(n+1)/(n-1)); n>1 contiguous intended sessions"

_SUITE_ACTIVE = False


def _numpy():
    import numpy as np
    return np


def _arrow():
    import pyarrow as pa
    import pyarrow.parquet as pq
    return pa, pq


def ceil_to_minute(ns: int) -> int:
    if type(ns) is not int or ns < 0:
        raise ContractError("ceil_to_minute requires a non-negative integer nanosecond timestamp")
    rem = ns % MINUTE
    return ns if rem == 0 else ns + (MINUTE - rem)


def yang_zhang_k(n: int) -> float:
    if type(n) is not int or n <= 1:
        raise ContractError("Yang–Zhang k is defined only for n>1 contiguous intended sessions")
    return YZ_K_NUMERATOR / (YZ_K_BASE + (n + 1) / (n - 1))


def sample_variance(values) -> float | None:
    seq = tuple(values)
    n = len(seq)
    if n <= 1:
        return None
    mean = math.fsum(seq) / n
    return math.fsum((value - mean) ** 2 for value in seq) / (n - 1)


def ohlc_domain_status(open_, high, low, close) -> str:
    prices = (open_, high, low, close)
    if any(value is None or isinstance(value, bool) or not isinstance(value, (int, float)) for value in prices):
        return "invalid_non_numeric"
    if any(not math.isfinite(float(value)) for value in prices):
        return "invalid_non_finite"
    if any(float(value) <= 0 for value in prices):
        return "invalid_non_positive"
    if float(high) < max(float(open_), float(close)) or float(low) > min(float(open_), float(close)):
        return "invalid_enclosure"
    return "valid"


def positive_finite(value) -> bool:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    number = float(value)
    return math.isfinite(number) and number > 0


def _ln_ratio(numerator, denominator) -> float:
    return math.log(float(numerator) / float(denominator))


def parkinson_variance(high, low) -> tuple[float | None, str]:
    status = ohlc_domain_status(high, high, low, low)
    if status != "valid":
        return None, status
    width = _ln_ratio(high, low)
    return (width * width) / FOUR_LN2, "valid"


def garman_klass_practical_eq19a(open_, high, low, close) -> tuple[float | None, str]:
    """Practical GK (original paper eq. 19a). Negative results stay unclipped."""
    status = ohlc_domain_status(open_, high, low, close)
    if status != "valid":
        return None, status
    hl = _ln_ratio(high, low)
    co = _ln_ratio(close, open_)
    value = 0.5 * hl * hl - TWO_LN2_MINUS_1 * co * co
    if value < 0:
        return value, "negative_unclipped"
    return value, "valid"


def rogers_satchell_variance(open_, high, low, close) -> tuple[float | None, str]:
    status = ohlc_domain_status(open_, high, low, close)
    if status != "valid":
        return None, status
    return (_ln_ratio(high, open_) * _ln_ratio(high, close)
            + _ln_ratio(low, open_) * _ln_ratio(low, close)), "valid"


def interval_estimators(open_, high, low, close) -> dict:
    status = ohlc_domain_status(open_, high, low, close)
    row = {
        "ohlc_status": status,
        "parkinson": None,
        "parkinson_status": status,
        "garman_klass": None,
        "garman_klass_status": status,
        "rogers_satchell": None,
        "rogers_satchell_status": status,
        "price_range_ticks": None,
        "price_range_points": None,
        "percentage_range": None,
        "log_range": None,
    }
    if status != "valid":
        return row
    open_f, high_f, low_f, close_f = map(float, (open_, high, low, close))
    row["price_range_ticks"] = high_f - low_f
    row["price_range_points"] = (high_f - low_f) * TICK_POINTS
    row["percentage_range"] = (high_f - low_f) / open_f
    row["log_range"] = _ln_ratio(high_f, low_f)
    row["parkinson"], row["parkinson_status"] = parkinson_variance(high_f, low_f)
    row["garman_klass"], row["garman_klass_status"] = garman_klass_practical_eq19a(open_f, high_f, low_f, close_f)
    row["rogers_satchell"], row["rogers_satchell_status"] = rogers_satchell_variance(open_f, high_f, low_f, close_f)
    return row


def true_range_ticks(high, low, previous_close) -> float | None:
    if previous_close is None:
        return None
    if not (positive_finite(high) and positive_finite(low) and positive_finite(previous_close)):
        return None
    if float(high) < float(low):
        return None
    high_f, low_f, prev = float(high), float(low), float(previous_close)
    return max(high_f - low_f, abs(high_f - prev), abs(low_f - prev))


def overnight_log_gap(open_, previous_close) -> float | None:
    if previous_close is None:
        return None
    if not (positive_finite(open_) and positive_finite(previous_close)):
        return None
    return _ln_ratio(open_, previous_close)


def close_log_return(close, previous_close) -> float | None:
    if previous_close is None:
        return None
    if not (positive_finite(close) and positive_finite(previous_close)):
        return None
    return _ln_ratio(close, previous_close)


def sampled_close_returns(closes, adjacent_complete) -> tuple[float, ...]:
    if len(closes) != len(adjacent_complete) + 1:
        raise ContractError("sampled close returns need one adjacency flag between consecutive sample closes")
    out = []
    for index, complete in enumerate(adjacent_complete):
        if not complete:
            continue
        left, right = closes[index], closes[index + 1]
        if left is None or right is None or left <= 0 or right <= 0:
            continue
        out.append(_ln_ratio(right, left))
    return tuple(out)


def realized_variance(returns) -> float:
    return math.fsum(value * value for value in returns)


def signed_semivariances(returns) -> tuple[float, float, float]:
    """Zero returns are excluded from both signed sums; they still sit in RV as 0."""
    up = math.fsum(value * value for value in returns if value > 0)
    down = math.fsum(value * value for value in returns if value < 0)
    return realized_variance(returns), up, down


def yang_zhang_from_sessions(opens, highs, lows, closes, previous_closes) -> dict:
    n = len(opens)
    if not (len(highs) == len(lows) == len(closes) == len(previous_closes) == n):
        raise ContractError("Yang–Zhang session columns must have equal length")
    if n <= 1:
        return {"status": "n_le_1", "n_declared": n, "n_valid": 0, "k": None,
                "open_var": None, "close_var": None, "rs_mean": None, "yang_zhang": None}
    opening, close_comp, rs_vals = [], [], []
    for open_, high, low, close, prev in zip(opens, highs, lows, closes, previous_closes, strict=True):
        if not positive_finite(prev) or ohlc_domain_status(open_, high, low, close) != "valid":
            return {"status": "missing_or_invalid_component", "n_declared": n, "n_valid": len(opening),
                    "k": None, "open_var": None, "close_var": None, "rs_mean": None, "yang_zhang": None}
        opening.append(_ln_ratio(open_, prev))
        close_comp.append(_ln_ratio(close, open_))
        rs_vals.append(rogers_satchell_variance(open_, high, low, close)[0])
    k = yang_zhang_k(n)
    open_var = sample_variance(opening)
    close_var = sample_variance(close_comp)
    rs_mean = math.fsum(rs_vals) / n
    return {
        "status": "valid",
        "n_declared": n,
        "n_valid": n,
        "k": k,
        "open_var": open_var,
        "close_var": close_var,
        "rs_mean": rs_mean,
        "yang_zhang": open_var + k * close_var + (1.0 - k) * rs_mean,
    }


def stage_of(day: date) -> str | None:
    for name, start, end in STAGES:
        if start <= day < end:
            return name
    return None


def stage_end(day: date) -> date | None:
    for _, start, end in STAGES:
        if start <= day < end:
            return end
    return None


def partition_key(partition) -> tuple:
    return partition["root"], int(partition["year"]), partition["variant"]


def select_partitions(protocol, mode, accepted_pilot=None) -> list:
    partitions = list(protocol["canonical_partitions"])
    if len(partitions) != 15:
        raise IntegrityError("frozen contract must list all 15 admitted partitions")
    if mode == "pilot":
        chosen = [row for row in partitions if partition_key(row) == PILOT_KEY]
        if len(chosen) != 1:
            raise IntegrityError("pilot selection must be exactly NQ 2020 primary_corrected")
        return chosen
    if mode != "full":
        raise ContractError("packet mode must be pilot or full")
    reused = set()
    if accepted_pilot is not None:
        for row in accepted_pilot.get("computed_partitions") or ():
            reused.add((row["root"], int(row["year"]), row["variant"]))
        if reused and reused != {PILOT_KEY}:
            raise IntegrityError("accepted_pilot may only supply the immutable NQ 2020 primary partition")
    ordered = sorted(partitions, key=lambda row: (
        0 if row["variant"] == "primary_corrected" else 1,
        0 if row["root"] == "NQ" else 1,
        int(row["year"]),
        row["variant"],
    ))
    out = []
    for row in ordered:
        item = dict(row)
        item["_reuse"] = partition_key(row) in reused
        out.append(item)
    return out


def accepted_pilot_from(configuration) -> dict | None:
    if configuration is None:
        return None
    if not isinstance(configuration, dict):
        raise ContractError("packet configuration must be a mapping or omitted")
    value = configuration.get("accepted_pilot")
    if value is None:
        return None
    if not isinstance(value, dict) or "refs" not in value:
        raise ContractError("accepted_pilot must be an explicit ref payload; no disk search is performed")
    return value


def read_canonical_table(store, spec):
    import pyarrow as pa
    import pyarrow.parquet as pq
    table = pq.read_table(pa.BufferReader(store.read(artifact_ref(
        {k: spec[k] for k in ("sha256", "size_bytes", "kind")}))))
    schema_sha = hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest()
    if table.num_rows != spec["rows"] or schema_sha != spec["schema_sha256"]:
        raise IntegrityError("retained admitted table identity differs")
    return table


def read_output_parquet(ref):
    import pyarrow.parquet as pq
    path = Path(ref["path"])
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref["sha256"] or len(raw) != ref["size_bytes"]:
        raise IntegrityError("retained physical-volatility output identity differs")
    table = pq.read_table(path)
    if ref.get("rows") is not None and table.num_rows != ref["rows"]:
        raise IntegrityError("retained physical-volatility output row count differs")
    if ref.get("schema_sha256"):
        schema_sha = hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest()
        if schema_sha != ref["schema_sha256"]:
            raise IntegrityError("retained physical-volatility output schema differs")
    return table


def source_version_of(partition) -> str:
    return digest({
        "source_sha256": partition["source_sha256"],
        "source_path": partition["source_path"],
        "canonical_table": {k: partition["canonical_table"][k]
                            for k in ("sha256", "size_bytes", "kind", "rows", "schema_sha256")},
        "admission_manifest": {k: partition["admission_manifest"][k]
                               for k in ("sha256", "size_bytes", "kind")},
        "variant": partition["variant"],
        "root": partition["root"],
        "year": int(partition["year"]),
    })


def source_version_record(partition, source_version=None) -> dict:
    return {
        "partition": list(partition_key(partition)),
        "source_version": source_version or source_version_of(partition),
        "source_sha256": partition["source_sha256"],
        "canonical_table_sha256": partition["canonical_table"]["sha256"],
        "admission_manifest_sha256": partition["admission_manifest"]["sha256"],
    }


def computed_partition_record(partition, source_version) -> dict:
    return {
        "root": partition["root"],
        "year": int(partition["year"]),
        "variant": partition["variant"],
        "source_path": partition["source_path"],
        "source_sha256": partition["source_sha256"],
        "source_version": source_version,
        "canonical_table": {k: partition["canonical_table"][k]
                            for k in ("sha256", "size_bytes", "kind", "rows", "schema_sha256")},
        "admission_manifest": {k: partition["admission_manifest"][k]
                               for k in ("sha256", "size_bytes", "kind")},
    }


def _compact_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _lineage_item(row, *, role=None) -> dict:
    item = {
        "admission_manifest_sha256": row.get("admission_manifest_sha256"),
        "canonical_table_sha256": row.get("canonical_table_sha256"),
        "contract_key": row.get("contract_key"),
        "root": row.get("root"),
        "source_sha256": row.get("source_sha256"),
        "variant": row.get("variant"),
        "window_version": row.get("window_version"),
        "year": row.get("year"),
    }
    if role is not None:
        item["role"] = role
    previous_date = row.get("previous_date")
    if previous_date is not None:
        item["previous_close_date"] = previous_date
        item["previous_close_admission_manifest_sha256"] = row.get("previous_close_admission_manifest_sha256")
        item["previous_close_canonical_table_sha256"] = row.get("previous_close_canonical_table_sha256")
        item["previous_close_source_sha256"] = row.get("previous_close_source_sha256")
        item["previous_close_variant"] = row.get("previous_close_variant")
        item["previous_close_year"] = row.get("previous_close_year")
    return item


def compact_source_lineage(items) -> str:
    # Window membership is authenticated by window_version. This field lists
    # distinct source/contract inputs, so it stays bounded across 120 sessions.
    seen, keys = [], set()
    for original in items:
        item = {name: value for name, value in original.items()
                if name not in ('window_version', 'previous_close_date')}
        key = _compact_json(item)
        if key not in keys:
            keys.add(key)
            seen.append(item)
    return _compact_json(seen)


def history_window_version(role, lookback, window_rows) -> str:
    return digest({
        "kind": "physical_ohlc_history_window_v1",
        "lookback": lookback,
        "role": role,
        "intended": [
            {
                "admission_manifest_sha256": row.get("admission_manifest_sha256"),
                "canonical_table_sha256": row.get("canonical_table_sha256"),
                "contract_key": row.get("contract_key"),
                "date": row.get("date"),
                "source_sha256": row.get("source_sha256"),
                "variant": row.get("variant"),
                "window_version": row.get("window_version"),
            }
            for row in window_rows
        ],
    })


def _civil_date(ns, zone=DEFAULT_ZONE):
    if ns is None:
        return None
    return datetime.fromtimestamp(int(ns) / 1_000_000_000, timezone.utc).astimezone(ZoneInfo(zone)).date()


def stages_spanned(start_ns, end_ns, zone=DEFAULT_ZONE) -> tuple:
    start_day = _civil_date(start_ns, zone)
    end_day = _civil_date(end_ns, zone)
    if start_day is None or end_day is None:
        return ()
    if end_day < start_day:
        start_day, end_day = end_day, start_day
    names = []
    for name, lo, hi in STAGES:
        if start_day < hi and end_day >= lo:
            names.append(name)
    return tuple(names)


def interval_crosses_stage(start_ns, end_ns, zone=DEFAULT_ZONE) -> bool:
    return len(stages_spanned(start_ns, end_ns, zone)) > 1


def declared_mean(values, n_declared):
    seq = list(values)
    if type(n_declared) is not int or n_declared <= 0 or len(seq) != n_declared:
        return None
    if any(value is None or isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(float(value)) for value in seq):
        return None
    return math.fsum(float(value) for value in seq) / n_declared


def max_or_none(values):
    present = [int(value) for value in values if value is not None]
    return None if not present else max(present)


def excursion_up(high, reference):
    if high is None or reference is None:
        return None
    return max(0, int(high) - int(reference))


def excursion_down(low, reference):
    if low is None or reference is None:
        return None
    return max(0, int(reference) - int(low))


def excursion_up_log(high, reference):
    if not (positive_finite(high) and positive_finite(reference)):
        return None
    return max(0.0, _ln_ratio(high, reference))


def excursion_down_log(low, reference):
    if not (positive_finite(low) and positive_finite(reference)):
        return None
    return max(0.0, _ln_ratio(reference, low))


def session_bounds(cash, session: str, zone: str) -> tuple[int | None, int | None, str | None]:
    if session == "cash_rth":
        if cash.state == "closed":
            return None, None, "closed"
        return cash.open_at, cash.close_at, None
    if session == "futures_wallclock_18_17":
        start = local_timestamp(cash.day - timedelta(days=1), time(18, 0), zone)
        end = local_timestamp(cash.day, time(17, 0), zone)
        return start, end, None
    if session == "pre_rth_06_0930":
        start = local_timestamp(cash.day, time(6, 0), zone)
        end = local_timestamp(cash.day, time(9, 30), zone)
        return start, end, None
    raise ContractError("unknown session identity")


def _string_field(pa, name):
    return pa.field(name, pa.string(), nullable=True)


def _i64_field(pa, name):
    return pa.field(name, pa.int64(), nullable=True)


def _f64_field(pa, name):
    return pa.field(name, pa.float64(), nullable=True)


def _bool_field(pa, name):
    return pa.field(name, pa.bool_(), nullable=True)


def _identity_fields(pa):
    return [
        _string_field(pa, "date"), _string_field(pa, "root"), _i64_field(pa, "year"),
        _string_field(pa, "variant"), _string_field(pa, "session"), _string_field(pa, "stage"),
        _string_field(pa, "cash_state"), _string_field(pa, "status"), _string_field(pa, "exclusion_reasons"),
        _string_field(pa, "contract_key"), _string_field(pa, "source_path"), _string_field(pa, "source_sha256"),
        _string_field(pa, "source_version"), _string_field(pa, "admission_manifest_sha256"),
        _string_field(pa, "canonical_table_sha256"), _string_field(pa, "window_version"),
        _string_field(pa, "purpose"), _bool_field(pa, "family_complete"),
        _i64_field(pa, "formation_start_ns"), _i64_field(pa, "formation_end_ns"),
        _i64_field(pa, "known_at_ns"), _i64_field(pa, "calendar_known_at_ns"),
        _i64_field(pa, "cash_open_ns"), _i64_field(pa, "cash_close_ns"),
        _i64_field(pa, "expected_minutes"), _i64_field(pa, "observed_minutes"),
    ]


def session_measurement_schema():
    pa, _ = _arrow()
    return pa.schema(_identity_fields(pa) + [
        _i64_field(pa, "open_ticks"), _i64_field(pa, "high_ticks"), _i64_field(pa, "low_ticks"),
        _i64_field(pa, "close_ticks"), _i64_field(pa, "previous_close_ticks"),
        _string_field(pa, "previous_date"), _string_field(pa, "previous_contract_key"),
        _string_field(pa, "previous_status"), _f64_field(pa, "price_range_ticks"),
        _f64_field(pa, "price_range_points"), _f64_field(pa, "percentage_range"),
        _f64_field(pa, "log_range"), _f64_field(pa, "true_range_ticks"),
        _f64_field(pa, "overnight_log_gap"), _f64_field(pa, "close_log_return"),
        _f64_field(pa, "parkinson"), _string_field(pa, "parkinson_status"),
        _f64_field(pa, "garman_klass"), _string_field(pa, "garman_klass_status"),
        _f64_field(pa, "rogers_satchell"), _string_field(pa, "rogers_satchell_status"),
        _string_field(pa, "ohlc_status"), _bool_field(pa, "estimators_valid"),
        _string_field(pa, "history_borrow_source_sha256"),
        _string_field(pa, "history_borrow_variant"),
        _string_field(pa, "source_lineage"),
        _string_field(pa, "previous_close_source_sha256"),
        _string_field(pa, "previous_close_canonical_table_sha256"),
        _string_field(pa, "previous_close_admission_manifest_sha256"),
        _string_field(pa, "previous_close_variant"),
        _i64_field(pa, "previous_close_year"),
    ])


def history_window_schema():
    pa, _ = _arrow()
    return pa.schema(_identity_fields(pa) + [
        _string_field(pa, "role"), _i64_field(pa, "lookback"), _i64_field(pa, "n_declared"),
        _i64_field(pa, "n_valid"), _bool_field(pa, "applicable"), _string_field(pa, "history_reasons"),
        _string_field(pa, "window_first_date"), _string_field(pa, "window_last_date"),
        _f64_field(pa, "yang_zhang"), _f64_field(pa, "open_var"), _f64_field(pa, "close_var"),
        _f64_field(pa, "rs_mean"), _f64_field(pa, "k"),
        _f64_field(pa, "mean_true_range_ticks"), _f64_field(pa, "mean_log_range"),
        _f64_field(pa, "mean_parkinson"), _f64_field(pa, "mean_garman_klass"),
        _f64_field(pa, "mean_rogers_satchell"),
        _string_field(pa, "history_borrow_source_sha256"),
        _string_field(pa, "history_borrow_variant"),
        _string_field(pa, "source_lineage"),
        _i64_field(pa, "decision_cut_ns"),
        _bool_field(pa, "causal_feature_eligible"),
        _bool_field(pa, "stage_purge"),
        _string_field(pa, "formation_through_known_at_stage"),
    ])


def scale_aggregate_schema():
    pa, _ = _arrow()
    return pa.schema(_identity_fields(pa) + [
        _i64_field(pa, "scale_minutes"), _i64_field(pa, "n_expected_bars"),
        _i64_field(pa, "n_complete_bars"), _i64_field(pa, "n_adjacent_pairs"),
        _i64_field(pa, "last_bar_duration_minutes"),
        _f64_field(pa, "sampled_close_rv"), _f64_field(pa, "up_semivariance"),
        _f64_field(pa, "down_semivariance"),
        _f64_field(pa, "mean_parkinson"), _f64_field(pa, "sum_parkinson"),
        _f64_field(pa, "mean_garman_klass"), _f64_field(pa, "sum_garman_klass"),
        _f64_field(pa, "mean_rogers_satchell"), _f64_field(pa, "sum_rogers_satchell"),
        _f64_field(pa, "full_session_parkinson"), _f64_field(pa, "full_session_garman_klass"),
        _f64_field(pa, "full_session_rogers_satchell"),
        _i64_field(pa, "n_full_length_bars"), _i64_field(pa, "n_scale_full_complete"),
        _i64_field(pa, "n_short_bars"), _i64_field(pa, "final_short_count"),
        _bool_field(pa, "last_bar_full_length"), _bool_field(pa, "scale_full_complete"),
        _f64_field(pa, "observed_mean_parkinson"), _f64_field(pa, "observed_sum_parkinson"),
        _f64_field(pa, "observed_mean_garman_klass"), _f64_field(pa, "observed_sum_garman_klass"),
        _f64_field(pa, "observed_mean_rogers_satchell"), _f64_field(pa, "observed_sum_rogers_satchell"),
        _f64_field(pa, "observed_sampled_close_rv"),
        _string_field(pa, "units_note"),
    ])


def seasonal_cell_schema():
    pa, _ = _arrow()
    return pa.schema(_identity_fields(pa) + [
        _i64_field(pa, "elapsed_start_minutes"), _i64_field(pa, "elapsed_end_minutes"),
        _i64_field(pa, "actual_duration_minutes"), _i64_field(pa, "cell_index"),
        _f64_field(pa, "range_ticks"), _f64_field(pa, "log_range"),
        _f64_field(pa, "sampled_close_rv"),
    ])


def remaining_window_schema():
    pa, _ = _arrow()
    return pa.schema(_identity_fields(pa) + [
        _i64_field(pa, "cut_minutes_after_open"), _string_field(pa, "target_kind"),
        _string_field(pa, "feature_id"), _string_field(pa, "label_id"),
        _i64_field(pa, "prefix_end_ns"), _i64_field(pa, "target_start_ns"),
        _i64_field(pa, "target_end_ns"), _i64_field(pa, "maturity_at_ns"),
        _i64_field(pa, "observed_input_known_at_ns"), _i64_field(pa, "reference_known_at_ns"),
        _i64_field(pa, "nominal_target_end_ns"), _i64_field(pa, "actual_observed_end_ns"),
        _bool_field(pa, "horizon_censored"), _bool_field(pa, "full_target_complete"),
        _bool_field(pa, "join_eligible"), _i64_field(pa, "observed_target_minutes"),
        _i64_field(pa, "reference_close_ticks"), _string_field(pa, "reference_contract_key"),
        _string_field(pa, "prefix_contract_key"), _string_field(pa, "target_contract_key"),
        _string_field(pa, "prefix_window_version"), _string_field(pa, "source_lineage"),
        _bool_field(pa, "same_contract"), _bool_field(pa, "applicable"),
        _bool_field(pa, "prefix_complete"), _bool_field(pa, "target_complete"),
        _bool_field(pa, "stage_purge"), _string_field(pa, "formation_through_maturity_stage"),
        _i64_field(pa, "future_up_ticks"), _i64_field(pa, "future_down_ticks"),
        _f64_field(pa, "future_up_pct"), _f64_field(pa, "future_down_pct"),
        _f64_field(pa, "future_up_log"), _f64_field(pa, "future_down_log"),
        _i64_field(pa, "terminal_return_ticks"), _f64_field(pa, "terminal_return_log"),
        _f64_field(pa, "observed_rv"), _f64_field(pa, "up_semivariance"),
        _f64_field(pa, "down_semivariance"), _bool_field(pa, "rv_complete"),
        _string_field(pa, "first_passage_claim"),
    ])


def _empty_identity(**extra):
    row = {
        "date": None, "root": None, "year": None, "variant": None, "session": None,
        "stage": None, "cash_state": None, "status": None, "exclusion_reasons": None,
        "contract_key": None, "source_path": None, "source_sha256": None,
        "source_version": None, "admission_manifest_sha256": None,
        "canonical_table_sha256": None, "window_version": None, "purpose": PURPOSE,
        "family_complete": False, "formation_start_ns": None, "formation_end_ns": None,
        "known_at_ns": None, "calendar_known_at_ns": None, "cash_open_ns": None,
        "cash_close_ns": None, "expected_minutes": None, "observed_minutes": None,
    }
    row.update(extra)
    return row


def _attach_partition(row, partition, source_version, cash=None):
    row["root"] = partition["root"]
    row["year"] = int(partition["year"])
    row["variant"] = partition["variant"]
    row["source_path"] = partition["source_path"]
    row["source_sha256"] = partition["source_sha256"]
    row["source_version"] = source_version
    row["admission_manifest_sha256"] = partition["admission_manifest"]["sha256"]
    row["canonical_table_sha256"] = partition["canonical_table"]["sha256"]
    row["purpose"] = PURPOSE
    row["family_complete"] = False
    if cash is not None:
        row["date"] = cash.day.isoformat()
        row["stage"] = stage_of(cash.day)
        row["cash_state"] = cash.state
        row["calendar_known_at_ns"] = cash.known_at
        row["cash_open_ns"] = cash.open_at
        row["cash_close_ns"] = cash.close_at
    return row


def _schema_names(schema):
    return [field.name for field in schema]


def rows_to_table(rows, schema):
    pa, _ = _arrow()
    names = _schema_names(schema)
    if not rows:
        return pa.table({name: pa.array([], type=schema.field(name).type) for name in names}, schema=schema)
    columns = {name: [row.get(name) for row in rows] for name in names}
    return pa.table({name: pa.array(columns[name], type=schema.field(name).type) for name in names}, schema=schema)


def write_parquet(outputs, name, table, *, kind):
    _, pq = _arrow()
    import pyarrow as pa
    with outputs.create(name) as stream:
        pq.write_table(table, stream, compression="zstd", use_dictionary=True,
                       write_statistics=True, row_group_size=65536)
    ref = outputs.reference(name, kind=kind)
    return {
        **ref,
        "rows": table.num_rows,
        "schema_sha256": hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest(),
    }


def columns_from_series(series: MinuteBars):
    np = _numpy()
    n = len(series.start)
    bad = np.frombuffer(series.bad, dtype=np.uint32, count=n + 1)
    return {
        "start": np.frombuffer(series.start, dtype=np.int64, count=n),
        "end": np.frombuffer(series.end, dtype=np.int64, count=n),
        "known": np.frombuffer(series.known, dtype=np.int64, count=n),
        "open": np.frombuffer(series.open, dtype=np.int64, count=n),
        "high": np.frombuffer(series.high, dtype=np.int64, count=n),
        "low": np.frombuffer(series.low, dtype=np.int64, count=n),
        "close": np.frombuffer(series.close, dtype=np.int64, count=n),
        "contract": np.frombuffer(series.contract, dtype=np.int32, count=n),
        "invalid": (np.diff(bad) != 0),
        "contract_names": series.contract_names,
        "source_version": series.source_version,
    }


def _search(starts, value, side="left"):
    np = _numpy()
    return int(np.searchsorted(starts, value, side=side))


def slice_ohlc(cols, start_ns, end_ns):
    lo = _search(cols["start"], start_ns, "left")
    hi = _search(cols["start"], end_ns, "left")
    expected = (end_ns - start_ns) // MINUTE
    reasons = []
    if hi <= lo:
        return None, ("missing_all_minutes",), lo, hi, expected
    if int(cols["start"][lo]) != start_ns:
        reasons.append("missing_first_minute")
    if int(cols["end"][hi - 1]) != end_ns:
        reasons.append("missing_last_minute")
    if hi - lo != expected:
        reasons.append("minute_count_mismatch")
    if hi - lo > 1 and bool((cols["start"][lo + 1:hi] != cols["end"][lo:hi - 1]).any()):
        reasons.append("missing_interior_minutes")
    if bool(cols["invalid"][lo:hi].any()):
        reasons.append("invalid_source_minutes")
    if hi - lo > 1 and bool((cols["contract"][lo + 1:hi] != cols["contract"][lo]).any()):
        reasons.append("raw_contract_transition")
    if reasons:
        return None, tuple(reasons), lo, hi, expected
    return {
        "open": int(cols["open"][lo]),
        "high": int(cols["high"][lo:hi].max()),
        "low": int(cols["low"][lo:hi].min()),
        "close": int(cols["close"][hi - 1]),
        "known_at": int(cols["known"][lo:hi].max()),
        "contract_key": cols["contract_names"][int(cols["contract"][lo])],
        "observed": hi - lo,
    }, (), lo, hi, expected


def last_published_close(cols, start_ns, end_ns):
    lo = _search(cols["start"], start_ns, "left")
    hi = _search(cols["start"], end_ns, "left")
    for index in range(hi - 1, lo - 1, -1):
        if not bool(cols["invalid"][index]):
            return int(cols["close"][index]), cols["contract_names"][int(cols["contract"][index])], int(cols["known"][index])
    return None, None, None


def _iter_scale_bounds(session_start, session_end, scale_minutes):
    step = scale_minutes * MINUTE
    start = session_start
    while start < session_end:
        end = min(start + step, session_end)
        yield start, end, (end - start) // MINUTE
        start = end


def measure_session(series, cols, cash, session, zone, previous, partition, source_version,
                    history_borrow=None):
    start, end, bound_reason = session_bounds(cash, session, zone)
    row = _empty_identity()
    _attach_partition(row, partition, source_version, cash)
    row["session"] = session
    if bound_reason:
        row["status"] = bound_reason
        row["exclusion_reasons"] = bound_reason
        return row
    row["formation_start_ns"] = start
    row["formation_end_ns"] = end
    window = series.window(start, end)
    row["window_version"] = window.version
    row["expected_minutes"] = window.expected_minutes
    row["observed_minutes"] = window.count
    row["contract_key"] = window.contract_key
    if not window.complete:
        row["status"] = "missing_input" if "missing_all_minutes" in window.reasons else "unavailable"
        row["exclusion_reasons"] = ";".join(window.reasons)
        _apply_previous(row, previous, history_borrow)
        return row
    summary = window.summary()
    open_, high, low, close = (summary["open_ticks"], summary["high_ticks"],
                               summary["low_ticks"], summary["close_ticks"])
    row["open_ticks"] = int(open_)
    row["high_ticks"] = int(high)
    row["low_ticks"] = int(low)
    row["close_ticks"] = int(close)
    row["known_at_ns"] = int(summary["available_at_ns"])
    estimators = interval_estimators(open_, high, low, close)
    row.update(estimators)
    _apply_previous(row, previous, history_borrow)
    if row["ohlc_status"] == "valid":
        row["true_range_ticks"] = true_range_ticks(high, low, row["previous_close_ticks"])
        row["overnight_log_gap"] = overnight_log_gap(open_, row["previous_close_ticks"])
        row["close_log_return"] = close_log_return(close, row["previous_close_ticks"])
    row["estimators_valid"] = (
        row["ohlc_status"] == "valid"
        and row["garman_klass_status"] == "valid"
        and row["parkinson_status"] == "valid"
        and row["rogers_satchell_status"] == "valid"
    )
    row["status"] = "complete" if row["estimators_valid"] else row["ohlc_status"]
    row["exclusion_reasons"] = "" if row["status"] == "complete" else row["ohlc_status"]
    return row


def _apply_previous(row, previous, history_borrow):
    row["previous_close_ticks"] = None
    row["previous_date"] = None
    row["previous_contract_key"] = None
    row["previous_status"] = "no_previous_intended_session"
    row["history_borrow_source_sha256"] = None
    row["history_borrow_variant"] = None
    row["previous_close_source_sha256"] = None
    row["previous_close_canonical_table_sha256"] = None
    row["previous_close_admission_manifest_sha256"] = None
    row["previous_close_variant"] = None
    row["previous_close_year"] = None
    lineage = [_lineage_item(row, role="session")]
    if previous is None:
        row["source_lineage"] = compact_source_lineage(lineage)
        return
    row["previous_date"] = previous.get("date")
    row["previous_contract_key"] = previous.get("contract_key")
    row["previous_status"] = previous.get("status") or "unavailable"
    row["previous_close_source_sha256"] = previous.get("source_sha256")
    row["previous_close_canonical_table_sha256"] = previous.get("canonical_table_sha256")
    row["previous_close_admission_manifest_sha256"] = previous.get("admission_manifest_sha256")
    row["previous_close_variant"] = previous.get("variant")
    row["previous_close_year"] = previous.get("year")
    same = (previous.get("status") == "complete"
            and previous.get("contract_key") is not None
            and previous.get("contract_key") == row.get("contract_key")
            and previous.get("close_ticks") is not None)
    if same:
        row["previous_close_ticks"] = int(previous["close_ticks"])
        row["previous_status"] = "complete_same_contract"
    elif previous.get("contract_key") not in (None, row.get("contract_key")):
        row["previous_status"] = "roll_previous_close_null"
    if history_borrow:
        row["history_borrow_source_sha256"] = history_borrow.get("source_sha256")
        row["history_borrow_variant"] = history_borrow.get("variant")
    lineage.append(_lineage_item(previous, role="previous_close"))
    if history_borrow:
        lineage.append({
            "role": "history_borrow",
            "source_sha256": history_borrow.get("source_sha256"),
            "variant": history_borrow.get("variant"),
        })
    row["source_lineage"] = compact_source_lineage(lineage)


def history_window_row(current, lookback, role, window_rows, partition, source_version, cash,
                       history_borrow=None, zone=DEFAULT_ZONE):
    row = _empty_identity()
    _attach_partition(row, partition, source_version, cash)
    row["session"] = current["session"]
    row["role"] = role
    row["lookback"] = lookback
    row["n_declared"] = lookback
    row["window_version"] = history_window_version(role, lookback, window_rows)
    row["formation_start_ns"] = None if not window_rows else window_rows[0].get("formation_start_ns")
    if row["formation_start_ns"] is None and window_rows:
        starts = [item.get("formation_start_ns") for item in window_rows if item.get("formation_start_ns") is not None]
        row["formation_start_ns"] = None if not starts else min(starts)
    row["formation_end_ns"] = None if not window_rows else window_rows[-1].get("formation_end_ns")
    knowns = [item.get("known_at_ns") for item in window_rows]
    row["known_at_ns"] = None if not window_rows or any(value is None for value in knowns) else max(int(value) for value in knowns)
    contracts = {item.get("contract_key") for item in window_rows}
    contracts.discard(None)
    row["contract_key"] = next(iter(contracts)) if len(contracts) == 1 else None
    row["history_borrow_source_sha256"] = None if history_borrow is None else history_borrow.get("source_sha256")
    row["history_borrow_variant"] = None if history_borrow is None else history_borrow.get("variant")
    row["decision_cut_ns"] = current.get("formation_start_ns")
    lineage = [_lineage_item(item) for item in window_rows]
    if window_rows:
        first = window_rows[0]
        lineage.append(_lineage_item({
            **first,
            "source_sha256": first.get("previous_close_source_sha256") or first.get("history_borrow_source_sha256"),
            "canonical_table_sha256": first.get("previous_close_canonical_table_sha256"),
            "admission_manifest_sha256": first.get("previous_close_admission_manifest_sha256"),
            "variant": first.get("previous_close_variant") or first.get("history_borrow_variant"),
            "year": first.get("previous_close_year"),
            "window_version": None,
            "contract_key": first.get("previous_contract_key"),
        }, role="previous_close"))
    if history_borrow:
        lineage.append({"role": "history_borrow", "source_sha256": history_borrow.get("source_sha256"),
                        "variant": history_borrow.get("variant")})
    row["source_lineage"] = compact_source_lineage(lineage)
    spanned = stages_spanned(row["formation_start_ns"], row["known_at_ns"], zone)
    row["formation_through_known_at_stage"] = None if not spanned else ";".join(spanned)
    row["stage_purge"] = len(spanned) > 1
    causal = (role == "feature_prior"
              and row["known_at_ns"] is not None
              and row["decision_cut_ns"] is not None
              and int(row["known_at_ns"]) <= int(row["decision_cut_ns"]))
    row["causal_feature_eligible"] = False
    empty_stats = dict(yang_zhang=None, open_var=None, close_var=None, rs_mean=None, k=None,
                       mean_true_range_ticks=declared_mean(
                           [item.get("true_range_ticks") for item in window_rows], lookback)
                       if len(window_rows) == lookback else None,
                       mean_log_range=None, mean_parkinson=None, mean_garman_klass=None,
                       mean_rogers_satchell=None,
                       window_first_date=None if not window_rows else window_rows[0].get("date"),
                       window_last_date=None if not window_rows else window_rows[-1].get("date"),
                       n_valid=sum(1 for item in window_rows if item.get("status") == "complete"))
    if len(window_rows) < lookback:
        row.update(status="warmup", exclusion_reasons="warmup", applicable=False,
                   history_reasons="warmup", **empty_stats)
        return row
    reasons = []
    valid = []
    contract = None
    for item in window_rows:
        if item.get("status") != "complete" or not item.get("estimators_valid"):
            reasons.append(f"{item.get('date')}:{(item.get('status') or 'unavailable')}")
            continue
        if contract is None:
            contract = item.get("contract_key")
        if item.get("contract_key") != contract:
            reasons.append(f"{item.get('date')}:roll")
            continue
        valid.append(item)
    row["n_valid"] = len(valid)
    row["window_first_date"] = window_rows[0]["date"]
    row["window_last_date"] = window_rows[-1]["date"]
    row["mean_true_range_ticks"] = declared_mean(
        [item.get("true_range_ticks") for item in window_rows], lookback)
    if len(valid) != lookback:
        reason = "missing" if any("missing" in item or "unavailable" in item for item in reasons) else "invalid_or_roll"
        if any(item.endswith(":roll") for item in reasons):
            reason = "roll"
        if any("warmup" in item for item in reasons):
            reason = "warmup"
        row.update(status=reason, exclusion_reasons=";".join(reasons), applicable=False,
                   history_reasons=";".join(reasons) or reason, yang_zhang=None, open_var=None,
                   close_var=None, rs_mean=None, k=None, mean_log_range=None,
                   mean_parkinson=None, mean_garman_klass=None, mean_rogers_satchell=None)
        return row
    yz = yang_zhang_from_sessions(
        [item["open_ticks"] for item in valid],
        [item["high_ticks"] for item in valid],
        [item["low_ticks"] for item in valid],
        [item["close_ticks"] for item in valid],
        [item["previous_close_ticks"] for item in valid],
    )
    usable = yz["status"] == "valid"
    if role == "feature_prior" and not causal:
        usable = False
        reasons.append("known_at_after_decision_cut")
    if row["stage_purge"]:
        reasons.append("stage_purge")
    row["causal_feature_eligible"] = bool(causal and usable and not row["stage_purge"])
    row.update(
        status=yz["status"] if yz["status"] != "valid" or not reasons else "purged_or_ineligible",
        exclusion_reasons="" if usable and not row["stage_purge"] else ";".join(reasons) or yz["status"],
        applicable=usable and not row["stage_purge"],
        history_reasons="" if usable and not row["stage_purge"] else ";".join(reasons) or yz["status"],
        yang_zhang=yz["yang_zhang"],
        open_var=yz["open_var"],
        close_var=yz["close_var"],
        rs_mean=yz["rs_mean"],
        k=yz["k"],
        mean_log_range=declared_mean([item.get("log_range") for item in window_rows], lookback),
        mean_parkinson=declared_mean([item.get("parkinson") for item in window_rows], lookback),
        mean_garman_klass=declared_mean([item.get("garman_klass") for item in window_rows], lookback),
        mean_rogers_satchell=declared_mean([item.get("rogers_satchell") for item in window_rows], lookback),
    )
    return row


def measure_scales(cols, cash, session_row, partition, source_version):
    rows = []
    start, end = session_row.get("formation_start_ns"), session_row.get("formation_end_ns")
    if session_row.get("session") != "cash_rth" or start is None or end is None:
        return rows

    def _est_mean(items, name):
        values = [item[name] for item in items if item[name] is not None and item[name + "_status"] == "valid"]
        return None if not values else math.fsum(values) / len(values)

    def _est_sum(items, name):
        values = [item[name] for item in items if item[name] is not None and item[name + "_status"] == "valid"]
        return None if not values else math.fsum(values)

    for scale in SCALES:
        row = _empty_identity()
        _attach_partition(row, partition, source_version, cash)
        row.update(session="cash_rth", scale_minutes=scale, window_version=session_row.get("window_version"),
                   formation_start_ns=start, formation_end_ns=end, known_at_ns=session_row.get("known_at_ns"),
                   contract_key=session_row.get("contract_key"),
                   full_session_parkinson=session_row.get("parkinson"),
                   full_session_garman_klass=session_row.get("garman_klass"),
                   full_session_rogers_satchell=session_row.get("rogers_satchell"),
                   units_note=("mean is per-scale-interval log-return²; sum is accumulated log-return²; "
                               "full_session_* is one completed RTH interval; primary uses full-length bars only; "
                               "not annualized"))
        bars = []
        last_duration = None
        for bar_start, bar_end, duration in _iter_scale_bounds(start, end, scale):
            last_duration = duration
            ohlc, reasons, _, _, expected = slice_ohlc(cols, bar_start, bar_end)
            full_length = duration == scale
            if ohlc is None or reasons:
                bars.append({"complete": False, "full_length": full_length, "reasons": reasons,
                             "duration": duration, "expected": expected, "close": None,
                             "contract": None, "estimators": None, "end": bar_end, "start": bar_start})
                continue
            estimators = interval_estimators(ohlc["open"], ohlc["high"], ohlc["low"], ohlc["close"])
            bars.append({
                "complete": estimators["ohlc_status"] == "valid",
                "full_length": full_length,
                "reasons": (),
                "duration": duration,
                "expected": expected,
                "close": ohlc["close"],
                "contract": ohlc["contract_key"],
                "estimators": estimators,
                "end": bar_end,
                "start": bar_start,
            })
        full_bars = [bar for bar in bars if bar["full_length"]]
        short_bars = [bar for bar in bars if not bar["full_length"]]
        observed_est = [bar["estimators"] for bar in bars if bar["complete"] and bar["estimators"]]
        full_est = [bar["estimators"] for bar in full_bars if bar["complete"] and bar["estimators"]]
        full_adjacent = []
        full_closes = []
        observed_adjacent = []
        observed_closes = []
        if full_bars:
            full_closes.append(full_bars[0]["close"] if full_bars[0]["complete"] else None)
            for index in range(1, len(full_bars)):
                prev, cur = full_bars[index - 1], full_bars[index]
                pair = (prev["complete"] and cur["complete"]
                        and prev["contract"] == cur["contract"]
                        and prev["end"] == cur["start"]
                        and prev["close"] is not None and cur["close"] is not None)
                full_adjacent.append(pair)
                full_closes.append(cur["close"] if cur["complete"] else None)
        if bars:
            observed_closes.append(bars[0]["close"] if bars[0]["complete"] else None)
            for index in range(1, len(bars)):
                prev, cur = bars[index - 1], bars[index]
                pair = (prev["complete"] and cur["complete"]
                        and prev["contract"] == cur["contract"]
                        and prev["end"] == cur["start"]
                        and prev["close"] is not None and cur["close"] is not None)
                observed_adjacent.append(pair)
                observed_closes.append(cur["close"] if cur["complete"] else None)
        full_returns = sampled_close_returns(full_closes, full_adjacent) if len(full_closes) > 1 else ()
        observed_returns = sampled_close_returns(observed_closes, observed_adjacent) if len(observed_closes) > 1 else ()
        full_rv, full_up, full_down = signed_semivariances(full_returns)
        observed_rv, _, _ = signed_semivariances(observed_returns)
        scale_full_complete = (bool(full_bars) and all(bar["complete"] for bar in full_bars)
                               and len({bar["contract"] for bar in full_bars}) == 1)
        any_observed = any(bar["complete"] for bar in bars)
        row.update(
            n_expected_bars=len(bars),
            n_complete_bars=sum(1 for bar in bars if bar["complete"]),
            n_adjacent_pairs=sum(1 for flag in full_adjacent if flag),
            n_full_length_bars=len(full_bars),
            n_scale_full_complete=sum(1 for bar in full_bars if bar["complete"]),
            n_short_bars=len(short_bars),
            final_short_count=sum(1 for bar in short_bars if True),
            last_bar_duration_minutes=last_duration,
            last_bar_full_length=False if last_duration is None else last_duration == scale,
            scale_full_complete=scale_full_complete,
            sampled_close_rv=None if not scale_full_complete else (0.0 if len(full_bars) == 1 else full_rv),
            up_semivariance=None if not scale_full_complete else (0.0 if len(full_bars) == 1 else full_up),
            down_semivariance=None if not scale_full_complete else (0.0 if len(full_bars) == 1 else full_down),
            mean_parkinson=None if not scale_full_complete else _est_mean(full_est, "parkinson"),
            sum_parkinson=None if not scale_full_complete else _est_sum(full_est, "parkinson"),
            mean_garman_klass=None if not scale_full_complete else _est_mean(full_est, "garman_klass"),
            sum_garman_klass=None if not scale_full_complete else _est_sum(full_est, "garman_klass"),
            mean_rogers_satchell=None if not scale_full_complete else _est_mean(full_est, "rogers_satchell"),
            sum_rogers_satchell=None if not scale_full_complete else _est_sum(full_est, "rogers_satchell"),
            observed_mean_parkinson=_est_mean(observed_est, "parkinson"),
            observed_sum_parkinson=_est_sum(observed_est, "parkinson"),
            observed_mean_garman_klass=_est_mean(observed_est, "garman_klass"),
            observed_sum_garman_klass=_est_sum(observed_est, "garman_klass"),
            observed_mean_rogers_satchell=_est_mean(observed_est, "rogers_satchell"),
            observed_sum_rogers_satchell=_est_sum(observed_est, "rogers_satchell"),
            observed_sampled_close_rv=None if not observed_returns and not any(observed_adjacent) else observed_rv,
            status=("complete" if scale_full_complete and session_row.get("status") == "complete"
                    else ("partial" if any_observed else "unavailable")),
            exclusion_reasons="" if scale_full_complete else "incomplete_or_missing_full_length_scale_bar",
            expected_minutes=session_row.get("expected_minutes"),
            observed_minutes=session_row.get("observed_minutes"),
        )
        rows.append(row)
    return rows


def measure_seasonal_cells(cols, cash, session_row, partition, source_version, series=None):
    rows = []
    start, end = session_row.get("formation_start_ns"), session_row.get("formation_end_ns")
    if session_row.get("session") != "cash_rth" or start is None or end is None:
        return rows
    for index, (bar_start, bar_end, duration) in enumerate(_iter_scale_bounds(start, end, ELAPSED_CELL_MINUTES)):
        row = _empty_identity()
        _attach_partition(row, partition, source_version, cash)
        cell_window = None if series is None else series.window(bar_start, bar_end)
        row.update(session="cash_rth", cell_index=index,
                   elapsed_start_minutes=(bar_start - start) // MINUTE,
                   elapsed_end_minutes=(bar_end - start) // MINUTE,
                   actual_duration_minutes=duration,
                   formation_start_ns=bar_start, formation_end_ns=bar_end,
                   window_version=None if cell_window is None else cell_window.version,
                   contract_key=None if cell_window is None else cell_window.contract_key,
                   expected_minutes=duration, observed_minutes=None)
        ohlc, reasons, lo, hi, expected = slice_ohlc(cols, bar_start, bar_end)
        row["expected_minutes"] = expected
        row["observed_minutes"] = 0 if hi <= lo else hi - lo
        if ohlc is None or reasons:
            if cell_window is None:
                row["window_version"] = digest({
                    "kind": "physical_ohlc_seasonal_cell_v1",
                    "start": bar_start, "end": bar_end, "reasons": reasons,
                    "source_version": cols.get("source_version"),
                })
            row.update(status="unknown_missing_bar", exclusion_reasons=";".join(reasons),
                       range_ticks=None, log_range=None, sampled_close_rv=None,
                       known_at_ns=None, contract_key=None)
            rows.append(row)
            continue
        if cell_window is None:
            row["window_version"] = digest({
                "kind": "physical_ohlc_seasonal_cell_v1",
                "start": bar_start, "end": bar_end, "contract": ohlc["contract_key"],
                "known_at": ohlc["known_at"], "source_version": cols.get("source_version"),
            })
        row["contract_key"] = ohlc["contract_key"]
        estimators = interval_estimators(ohlc["open"], ohlc["high"], ohlc["low"], ohlc["close"])
        closes = [int(cols["close"][i]) if not bool(cols["invalid"][i]) else None for i in range(lo, hi)]
        adjacent = []
        for offset in range(1, hi - lo):
            i0, i1 = lo + offset - 1, lo + offset
            adjacent.append(not bool(cols["invalid"][i0]) and not bool(cols["invalid"][i1])
                            and int(cols["end"][i0]) == int(cols["start"][i1])
                            and int(cols["contract"][i0]) == int(cols["contract"][i1])
                            and closes[offset - 1] is not None and closes[offset] is not None)
        returns = sampled_close_returns(closes, adjacent) if len(closes) > 1 else ()
        rv = None if any(not flag for flag in adjacent) else (0.0 if not returns else realized_variance(returns))
        row.update(
            status="complete" if estimators["ohlc_status"] == "valid" else estimators["ohlc_status"],
            exclusion_reasons="" if estimators["ohlc_status"] == "valid" else estimators["ohlc_status"],
            range_ticks=estimators["price_range_ticks"],
            log_range=estimators["log_range"],
            sampled_close_rv=rv,
            known_at_ns=ohlc["known_at"],
        )
        rows.append(row)
    return rows


def _target_kind(horizon) -> str:
    return "actual_cash_close" if horizon == "actual_cash_close" else f"forward_{horizon}"


def measure_remaining(cols, series, cash, session_row, partition, source_version, zone):
    rows = []
    if session_row.get("session") != "cash_rth" or cash.open_at is None or cash.close_at is None:
        return rows
    open_ns, close_ns = cash.open_at, cash.close_at
    for cut in REMAINING_CUTS:
        intended_prefix_end = open_ns + cut * MINUTE
        cut_after_close = intended_prefix_end > close_ns
        prefix_end = intended_prefix_end
        prefix = series.window(open_ns, prefix_end) if not cut_after_close else series.window(
            open_ns, min(prefix_end, close_ns) if min(prefix_end, close_ns) > open_ns else open_ns + MINUTE)
        if cut_after_close:
            prefix_window = None
            prefix_complete = False
            observed_known = None
            planned_known = None
            prefix_contract = None
            prefix_version = None
        else:
            prefix_window = prefix
            prefix_complete = prefix.complete
            observed_known = int(max(series.known[prefix.left:prefix.right])) if prefix.count else None
            planned_known = prefix_end + SOURCE_LAG_NS
            if observed_known is not None:
                planned_known = max(planned_known, observed_known)
            prefix_contract = prefix.contract_key
            prefix_version = prefix.version
        reference, ref_contract, ref_known = last_published_close(
            cols, open_ns, prefix_end if not cut_after_close else min(prefix_end, close_ns))
        target_start = None if planned_known is None else ceil_to_minute(planned_known)
        feature_id = digest({
            "kind": "physical_ohlc_remaining_feature_v1",
            "version": VERSION,
            "date": cash.day.isoformat(),
            "cut_minutes": cut,
            "source_version": source_version,
            "prefix_window_version": prefix_version,
            "prefix_contract": prefix_contract,
            "reference_contract": ref_contract,
            "reference_close": reference,
            "reference_known_at": ref_known,
            "prefix_end": prefix_end,
            "planned_known_at": planned_known,
            "observed_input_known_at": observed_known,
        })
        feature_lineage = compact_source_lineage([{
            "admission_manifest_sha256": partition["admission_manifest"]["sha256"],
            "canonical_table_sha256": partition["canonical_table"]["sha256"],
            "contract_key": prefix_contract,
            "role": "remaining_prefix",
            "source_sha256": partition["source_sha256"],
            "variant": partition["variant"],
            "window_version": prefix_version,
            "year": int(partition["year"]),
        }])
        for horizon in (*FORWARD_MINUTES, "actual_cash_close"):
            row = _empty_identity()
            _attach_partition(row, partition, source_version, cash)
            reasons = []
            if cut_after_close:
                reasons.append("cut_after_cash_close")
            if not prefix_complete:
                reasons.append("prefix_incomplete")
            if planned_known is None:
                reasons.append("unknown_known_at")
            if reference is None or ref_known is None:
                reasons.append("missing_reference_close")
            if target_start is not None and target_start >= close_ns:
                reasons.append("target_starts_at_or_after_cash_close")
            if horizon == "actual_cash_close":
                nominal_end = close_ns
                horizon_censored = False
            else:
                nominal_end = None if target_start is None else target_start + horizon * MINUTE
                horizon_censored = bool(nominal_end is not None and nominal_end > close_ns)
                if horizon_censored:
                    reasons.append("horizon_censored_past_cash_close")
            observe_end = None
            if target_start is not None and nominal_end is not None and target_start < close_ns:
                observe_end = close_ns if horizon == "actual_cash_close" else min(nominal_end, close_ns)
                if observe_end <= target_start:
                    observe_end = None
            observed = None
            if observe_end is not None:
                observed = series.window(target_start, observe_end)
            target_contract = None if observed is None else observed.contract_key
            same_contract = bool(ref_contract is not None and target_contract == ref_contract
                                 and prefix_contract in (None, ref_contract))
            if observed is not None and not same_contract:
                reasons.append("contract_mismatch")
            full_target = None
            if (target_start is not None and nominal_end is not None and not horizon_censored
                    and target_start < nominal_end):
                full_target = series.window(target_start, nominal_end)
            target_complete = bool(full_target is not None and full_target.complete and not horizon_censored)
            full_target_complete = target_complete
            if horizon == "actual_cash_close":
                full_target_complete = bool(observed is not None and observed.complete)
                target_complete = full_target_complete
            if not target_complete:
                reasons.append("target_incomplete")
            applicable = (not cut_after_close and prefix_complete and planned_known is not None
                          and reference is not None and ref_known is not None
                          and target_start is not None and target_start < close_ns
                          and nominal_end is not None and target_start < nominal_end
                          and not horizon_censored)
            spanned = stages_spanned(open_ns, None if nominal_end is None else nominal_end + MINUTE, zone)
            stage_whole = len(spanned) <= 1
            purged = len(spanned) > 1
            join_eligible = bool(
                prefix_complete and target_complete and same_contract and stage_whole and applicable
            )
            label_id = digest({
                "kind": "physical_ohlc_remaining_label_v1",
                "feature_id": feature_id,
                "target_kind": _target_kind(horizon),
                "target_start": target_start,
                "nominal_target_end": nominal_end,
                "actual_observed_end": observe_end,
                "target_contract": target_contract,
            })
            future_up = future_down = terminal_ticks = None
            future_up_pct = future_down_pct = future_up_log = future_down_log = terminal_log = None
            rv = up = down = None
            rv_complete = False
            observed_minutes = 0 if observed is None else observed.count
            valid_observed = ([] if observed is None or not same_contract else
                [i for i in range(observed.left, observed.right) if not bool(cols['invalid'][i])
                 and cols['contract_names'][int(cols['contract'][i])] == ref_contract])
            if valid_observed and reference is not None:
                high = max(int(series.high[i]) for i in valid_observed)
                low = min(int(series.low[i]) for i in valid_observed)
                close = int(series.close[valid_observed[-1]])
                future_up = excursion_up(high, reference)
                future_down = excursion_down(low, reference)
                if positive_finite(reference):
                    future_up_pct = None if future_up is None else future_up / float(reference)
                    future_down_pct = None if future_down is None else future_down / float(reference)
                future_up_log = excursion_up_log(high, reference)
                future_down_log = excursion_down_log(low, reference)
                terminal_ticks = close - reference
                terminal_log = _ln_ratio(close, reference) if positive_finite(close) and positive_finite(reference) else None
                closes = [int(cols["close"][i]) if not bool(cols["invalid"][i]) else None
                          for i in range(observed.left, observed.right)]
                adjacent = []
                for offset in range(1, observed.right - observed.left):
                    i0, i1 = observed.left + offset - 1, observed.left + offset
                    adjacent.append(not bool(cols["invalid"][i0]) and not bool(cols["invalid"][i1])
                                    and int(cols["end"][i0]) == int(cols["start"][i1])
                                    and int(cols["contract"][i0]) == int(cols["contract"][i1])
                                    and closes[offset - 1] is not None and closes[offset] is not None)
                rv_complete = bool(join_eligible and closes and adjacent and all(adjacent))
                returns = sampled_close_returns(closes, adjacent) if len(closes) > 1 else ()
                if returns:
                    rv, up, down = signed_semivariances(returns)
                elif rv_complete and len(closes) <= 1:
                    rv = up = down = 0.0
                if not join_eligible:
                    rv_complete = False
            status = "not_applicable"
            if cut_after_close or not prefix_complete:
                status = "ineligible"
            elif join_eligible:
                status = "complete"
            elif observed is not None and observed.count:
                status = "observed_incomplete"
            elif not applicable:
                status = "not_applicable"
            row.update(
                session="cash_rth",
                cut_minutes_after_open=cut,
                target_kind=_target_kind(horizon),
                feature_id=feature_id,
                label_id=label_id,
                prefix_end_ns=prefix_end,
                known_at_ns=planned_known,
                observed_input_known_at_ns=observed_known,
                reference_known_at_ns=ref_known,
                target_start_ns=target_start,
                target_end_ns=nominal_end,
                nominal_target_end_ns=nominal_end,
                actual_observed_end_ns=observe_end,
                horizon_censored=horizon_censored,
                full_target_complete=full_target_complete,
                join_eligible=join_eligible,
                observed_target_minutes=observed_minutes,
                maturity_at_ns=None if nominal_end is None else nominal_end + MINUTE,
                reference_close_ticks=reference,
                reference_contract_key=ref_contract,
                prefix_contract_key=prefix_contract,
                target_contract_key=target_contract,
                prefix_window_version=prefix_version,
                source_lineage=feature_lineage,
                contract_key=prefix_contract,
                same_contract=same_contract,
                applicable=applicable,
                prefix_complete=prefix_complete,
                target_complete=target_complete,
                stage_purge=purged,
                formation_through_maturity_stage=None if not spanned else ";".join(spanned),
                future_up_ticks=future_up,
                future_down_ticks=future_down,
                future_up_pct=future_up_pct,
                future_down_pct=future_down_pct,
                future_up_log=future_up_log,
                future_down_log=future_down_log,
                terminal_return_ticks=terminal_ticks,
                terminal_return_log=terminal_log,
                observed_rv=rv,
                up_semivariance=up,
                down_semivariance=down,
                rv_complete=rv_complete,
                first_passage_claim="none; OHLC extrema only",
                status=status,
                exclusion_reasons=";".join(dict.fromkeys(reasons)),
                window_version=prefix_version,
                formation_start_ns=open_ns,
                formation_end_ns=prefix_end,
            )
            rows.append(row)
    return rows


def intended_cash_days(calendar, first, last):
    return cash_dates(calendar, first, last)


def year_bounds(year):
    first = max(date(year, 1, 1), POPULATION_FIRST)
    last = min(date(year, 12, 31), POPULATION_LAST)
    return first, last


def load_year_series(store, partition):
    table = read_canonical_table(store, partition["canonical_table"])
    source_version = source_version_of(partition)
    series = MinuteBars.from_table(table, source_version=source_version)
    return series, columns_from_series(series), source_version


def history_rows_for_date(session_history, current, lookback, partition, source_version, cash,
                          history_borrow=None, zone=DEFAULT_ZONE):
    rows = []
    prior = session_history[:-1]
    including = session_history
    feature_window = prior[-lookback:] if len(prior) >= lookback else prior
    measure_window = including[-lookback:] if len(including) >= lookback else including
    rows.append(history_window_row(current, lookback, "feature_prior", feature_window,
                                   partition, source_version, cash, history_borrow, zone=zone))
    rows.append(history_window_row(current, lookback, "measurement_including_current", measure_window,
                                   partition, source_version, cash, history_borrow, zone=zone))
    return rows


def process_partition(store, calendar, partition, carry, *, history_borrow=None):
    series, cols, source_version = load_year_series(store, partition)
    zone = calendar.zone
    first, last = year_bounds(int(partition["year"]))
    days = intended_cash_days(calendar, first, last)
    session_rows, hist_rows, scale_rows, seasonal_rows, remain_rows = [], [], [], [], []
    variant_key = partition["variant"]
    local_carry = {session: list(carry.get((partition["root"], session, variant_key), []))
                   for session in SESSIONS}
    if partition["variant"] == "original_nq2024_sensitivity":
        for session in SESSIONS:
            borrowed = [row for row in carry.get(("NQ", session, "primary_corrected"), [])
                        if int(row.get("year") or 0) <= 2023]
            local_carry[session] = borrowed[-130:]
    for cash in days:
        for session in SESSIONS:
            previous = local_carry[session][-1] if local_carry[session] else None
            borrow = history_borrow if (previous is not None and previous.get("year") != int(partition["year"])) else None
            if partition["variant"] == "original_nq2024_sensitivity" and previous is not None and previous.get("variant") == "primary_corrected":
                borrow = {"source_sha256": previous.get("source_sha256"), "variant": previous.get("variant")}
            row = measure_session(series, cols, cash, session, zone, previous, partition,
                                  source_version, history_borrow=borrow)
            session_rows.append(row)
            for lookback in LOOKBACKS:
                hist_rows.extend(history_rows_for_date(local_carry[session] + [row], row, lookback,
                                                       partition, source_version, cash, borrow, zone=zone))
            if session == "cash_rth":
                scale_rows.extend(measure_scales(cols, cash, row, partition, source_version))
                seasonal_rows.extend(measure_seasonal_cells(cols, cash, row, partition, source_version, series))
                remain_rows.extend(measure_remaining(cols, series, cash, row, partition, source_version, zone))
            local_carry[session].append(row)
            if len(local_carry[session]) > 130:
                local_carry[session] = local_carry[session][-130:]
    next_carry = {}
    for session in SESSIONS:
        key = (partition["root"], session, partition["variant"])
        next_carry[key] = local_carry[session][-130:]
    return {
        "session": session_rows,
        "history": hist_rows,
        "scale": scale_rows,
        "seasonal": seasonal_rows,
        "remaining": remain_rows,
        "source_version": source_version,
        "carry": next_carry,
        "intended_dates": [day.day.isoformat() for day in days],
    }


def _finite_or_none(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _date_map(rows, field, *, require=None):
    out = {}
    for row in rows:
        day = row.get("date")
        if day is None:
            continue
        if require and not require(row):
            out.setdefault(day, None)
            continue
        value = _finite_or_none(row.get(field))
        out[day] = value
    return out


def _distribution(values):
    np = _numpy()
    arr = np.asarray([value for value in values if value is not None], dtype=np.float64)
    if arr.size == 0:
        return {"count": 0, "mean": None, **{f"q{int(q * 100):02d}": None for q in STAT_QUANTILES}}
    return {
        "count": int(arr.size),
        "mean": float(arr.mean()),
        **{f"q{int(q * 100):02d}": float(np.quantile(arr, q)) for q in STAT_QUANTILES},
    }


def _compact_stat(result):
    for metric in result.get("metrics", {}).values():
        metric.get("bootstrap", {}).pop("replicate_estimates", None)
    for ratio in result.get("ratios", {}).values():
        ratio.get("bootstrap", {}).pop("replicate_estimates", None)
    return result


def _stat_block(metrics, intended):
    if not metrics or not intended:
        return None
    return _compact_stat(observed_date_statistics(
        metrics, intended, estimator="date_mean", seed=STAT_SEED, block_length=STAT_BLOCK,
        replicates=STAT_REPLICATES, confidence=STAT_CONFIDENCE,
        minimum_independent_dates=STAT_MIN_DATES, minimum_events=STAT_MIN_EVENTS,
        _retain_replicate_estimates=False,
    ))


def build_statistics(session_rows, history_rows, scale_rows, seasonal_rows, remaining_rows, intended_by_group):
    groups = {}
    for row in session_rows:
        if row.get("variant") == "original_nq2024_sensitivity":
            continue
        key = (row["root"], row["year"], row["stage"], row["session"], row["variant"])
        groups.setdefault(key, []).append(row)
    statistics = {"kind": "physical_ohlc_volatility_date_statistics_v1", "version": VERSION,
                  "purpose": PURPOSE, "family_complete": False, "units": {
                      "estimators": "log-return squared; mean-per-interval and accumulated sum are distinct",
                      "ranges": "raw ticks (0.25 point) and log(H/L)",
                      "annualization": "none in primary tables",
                  }, "groups": {}, "estimator_differences": {}, "nq2024_original_vs_primary": {},
                  "distributions": {}}
    for key, rows in groups.items():
        root, year, stage, session, variant = key
        intended = intended_by_group.get((root, year, variant)) or sorted({row["date"] for row in rows})
        metrics = {
            "parkinson": _date_map(rows, "parkinson", require=lambda r: r.get("parkinson_status") == "valid"),
            "garman_klass": _date_map(rows, "garman_klass", require=lambda r: r.get("garman_klass_status") == "valid"),
            "rogers_satchell": _date_map(rows, "rogers_satchell", require=lambda r: r.get("rogers_satchell_status") == "valid"),
            "log_range": _date_map(rows, "log_range", require=lambda r: r.get("ohlc_status") == "valid"),
            "true_range_ticks": _date_map(rows, "true_range_ticks"),
            "overnight_log_gap": _date_map(rows, "overnight_log_gap"),
        }
        label = f"root={root}|year={year}|stage={stage}|session={session}|variant={variant}"
        statistics["groups"][label] = _stat_block(metrics, intended)
        statistics["distributions"][label] = {
            name: _distribution(metrics[name].values()) for name in metrics
        }
        gk = metrics["garman_klass"]
        pk = metrics["parkinson"]
        rs = metrics["rogers_satchell"]
        diffs = {
            "gk_minus_parkinson": {day: None if gk.get(day) is None or pk.get(day) is None else gk[day] - pk[day]
                                   for day in intended},
            "gk_minus_rs": {day: None if gk.get(day) is None or rs.get(day) is None else gk[day] - rs[day]
                            for day in intended},
            "parkinson_minus_rs": {day: None if pk.get(day) is None or rs.get(day) is None else pk[day] - rs[day]
                                   for day in intended},
        }
        statistics["estimator_differences"][label] = _stat_block(diffs, intended)
    yz_groups = {}
    for row in history_rows:
        if row.get("variant") == "original_nq2024_sensitivity" or row.get("role") != "measurement_including_current":
            continue
        key = (row["root"], row["year"], row["stage"], row["session"], row["lookback"], row["variant"])
        yz_groups.setdefault(key, []).append(row)
    for key, rows in yz_groups.items():
        root, year, stage, session, lookback, variant = key
        intended = intended_by_group.get((root, year, variant)) or sorted({row["date"] for row in rows})
        label = f"yz|root={root}|year={year}|stage={stage}|session={session}|n={lookback}|variant={variant}"
        metrics = {"yang_zhang": _date_map(rows, "yang_zhang", require=lambda r: r.get("applicable") is True)}
        statistics["groups"][label] = _stat_block(metrics, intended)
        statistics["distributions"][label] = {"yang_zhang": _distribution(metrics["yang_zhang"].values())}
    scale_groups = {}
    for row in scale_rows:
        if row.get("variant") == "original_nq2024_sensitivity":
            continue
        key = (row["root"], row["year"], row["stage"], row["scale_minutes"], row["variant"])
        scale_groups.setdefault(key, []).append(row)
    for key, rows in scale_groups.items():
        root, year, stage, scale, variant = key
        intended = intended_by_group.get((root, year, variant)) or sorted({row["date"] for row in rows})
        label = f"scale|root={root}|year={year}|stage={stage}|minutes={scale}|variant={variant}"
        primary = lambda r: r.get("scale_full_complete") is True and r.get("status") == "complete"
        metrics = {
            "sampled_close_rv": _date_map(rows, "sampled_close_rv", require=primary),
            "mean_parkinson": _date_map(rows, "mean_parkinson", require=primary),
            "sum_parkinson": _date_map(rows, "sum_parkinson", require=primary),
            "mean_garman_klass": _date_map(rows, "mean_garman_klass", require=primary),
            "sum_garman_klass": _date_map(rows, "sum_garman_klass", require=primary),
            "mean_rogers_satchell": _date_map(rows, "mean_rogers_satchell", require=primary),
            "sum_rogers_satchell": _date_map(rows, "sum_rogers_satchell", require=primary),
            "up_semivariance": _date_map(rows, "up_semivariance", require=primary),
            "down_semivariance": _date_map(rows, "down_semivariance", require=primary),
            "full_session_parkinson": _date_map(rows, "full_session_parkinson", require=primary),
            "full_session_garman_klass": _date_map(rows, "full_session_garman_klass", require=primary),
            "full_session_rogers_satchell": _date_map(rows, "full_session_rogers_satchell", require=primary),
        }
        observed = {
            "observed_sampled_close_rv": _date_map(rows, "observed_sampled_close_rv"),
            "observed_mean_parkinson": _date_map(rows, "observed_mean_parkinson"),
            "n_short_bars": _date_map(rows, "n_short_bars"),
        }
        statistics["groups"][label] = _stat_block(metrics, intended)
        statistics["distributions"][label] = {name: _distribution(metrics[name].values()) for name in metrics}
        statistics["distributions"][label + "|partial_observed"] = {
            name: _distribution(observed[name].values()) for name in observed
        }
        diffs = {
            "sum_parkinson_minus_full": {
                day: None if metrics["sum_parkinson"].get(day) is None or metrics["full_session_parkinson"].get(day) is None
                else metrics["sum_parkinson"][day] - metrics["full_session_parkinson"][day]
                for day in intended
            }
        }
        statistics["estimator_differences"][label] = _stat_block(diffs, intended)
    cell_groups = {}
    for row in seasonal_rows:
        if row.get("variant") == "original_nq2024_sensitivity":
            continue
        key = (row["root"], row["year"], row["stage"], row["elapsed_start_minutes"], row["variant"])
        cell_groups.setdefault(key, []).append(row)
    for key, rows in cell_groups.items():
        root, year, stage, elapsed, variant = key
        intended = intended_by_group.get((root, year, variant)) or sorted({row["date"] for row in rows})
        label = f"elapsed|root={root}|year={year}|stage={stage}|start={elapsed}|variant={variant}"
        metrics = {"range_ticks": _date_map(rows, "range_ticks"),
                   "sampled_close_rv": _date_map(rows, "sampled_close_rv")}
        statistics["groups"][label] = _stat_block(metrics, intended)
        statistics["distributions"][label] = {name: _distribution(metrics[name].values()) for name in metrics}
    remain_groups = {}
    for row in remaining_rows:
        if row.get("variant") == "original_nq2024_sensitivity" or row.get("stage_purge"):
            continue
        key = (row["root"], row["year"], row["stage"], row["cut_minutes_after_open"], row["target_kind"], row["variant"])
        remain_groups.setdefault(key, []).append(row)
    for key, rows in remain_groups.items():
        root, year, stage, cut, target, variant = key
        intended = intended_by_group.get((root, year, variant)) or sorted({row["date"] for row in rows})
        label = f"remaining|root={root}|year={year}|stage={stage}|cut={cut}|target={target}|variant={variant}"
        metrics = {
            "future_up_log": _date_map(rows, "future_up_log", require=lambda r: r.get("join_eligible") is True),
            "future_down_log": _date_map(rows, "future_down_log", require=lambda r: r.get("join_eligible") is True),
            "terminal_return_log": _date_map(rows, "terminal_return_log", require=lambda r: r.get("join_eligible") is True),
            "observed_rv": _date_map(rows, "observed_rv", require=lambda r: r.get("rv_complete") is True),
        }
        statistics["groups"][label] = _stat_block(metrics, intended)
        statistics["distributions"][label] = {name: _distribution(metrics[name].values()) for name in metrics}
    primary_2024 = [row for row in session_rows
                    if row.get("root") == "NQ" and row.get("year") == 2024
                    and row.get("variant") == "primary_corrected" and row.get("session") == "cash_rth"]
    original_2024 = [row for row in session_rows
                     if row.get("root") == "NQ" and row.get("year") == 2024
                     and row.get("variant") == "original_nq2024_sensitivity" and row.get("session") == "cash_rth"]
    if primary_2024 and original_2024:
        intended = sorted({row["date"] for row in primary_2024} | {row["date"] for row in original_2024})
        prim = {row["date"]: row for row in primary_2024}
        orig = {row["date"]: row for row in original_2024}
        both = [day for day in intended if day in prim and day in orig]
        same_contract = [
            day for day in both
            if prim[day].get("contract_key") is not None
            and prim[day].get("contract_key") == orig[day].get("contract_key")
        ]
        changed_contract = [
            day for day in both
            if prim[day].get("contract_key") != orig[day].get("contract_key")
        ]
        matched_valid = [
            day for day in same_contract
            if prim[day].get("garman_klass_status") == "valid"
            and orig[day].get("garman_klass_status") == "valid"
        ]
        pair_metrics = {
            "primary_gk": {day: _finite_or_none(prim[day]["garman_klass"]) if prim[day].get("garman_klass_status") == "valid" else None
                           for day in intended if day in prim},
            "original_gk": {day: _finite_or_none(orig[day]["garman_klass"]) if orig[day].get("garman_klass_status") == "valid" else None
                            for day in intended if day in orig},
            "gk_original_minus_primary": {
                day: None if day not in matched_valid
                else float(orig[day]["garman_klass"]) - float(prim[day]["garman_klass"])
                for day in intended
            },
        }
        for name in ("primary_gk", "original_gk"):
            for day in intended:
                pair_metrics[name].setdefault(day, None)
        statistics["nq2024_original_vs_primary"] = {
            "intended_dates": intended,
            "both_present": len(both),
            "same_raw_contract_pairs": len(same_contract),
            "changed_contract": len(changed_contract),
            "changed_contract_dates": changed_contract,
            "matched_valid_pairs": len(matched_valid),
            "primary_only": sum(1 for day in intended if day in prim and day not in orig),
            "original_only": sum(1 for day in intended if day in orig and day not in prim),
            "pooled_as_independent_sample": False,
            "statistics": _stat_block(pair_metrics, intended),
        }
    return statistics


def _fmt_mean(block, name):
    if not block or name not in block.get("metrics", {}):
        return "unavailable"
    metric = block["metrics"][name]
    estimate = metric.get("estimate")
    boot = metric.get("bootstrap") or {}
    support = metric.get("support") or {}
    if estimate is None:
        reasons = ",".join(support.get("reasons") or ()) or "no valid dates"
        return f"undefined ({reasons})"
    lower, upper = boot.get("lower"), boot.get("upper")
    interval = "interval undefined" if lower is None or upper is None else f"[{lower:.8g}, {upper:.8g}]"
    return (f"{estimate:.8g} log-return² date-block mean, 95% {interval}; "
            f"{metric.get('actual_valid_date_count')} valid dates / {block.get('intended_date_count')} intended")


def write_report(session_rows, statistics, refs, counts, tests, mode, reused):
    lines = [
        "# Physical OHLC volatility measurements",
        "",
        f"Family `{FAMILY}` version `{VERSION}`. **family_complete is false.**",
        PURPOSE + ".",
        "",
        "## Scope and remaining limits",
        "",
        f"- Mode: `{mode}`. Reused immutable pilot partitions: {reused}.",
        "- Practical Garman–Klass is original eq. 19a; the full analytic estimator 19 is not computed.",
        "- Yang–Zhang uses hosted-paper sample variance (ddof=1) and k=0.34/(1.34+(n+1)/(n-1)) on contiguous intended sessions; n does not shrink by dropping dates.",
        "- Minute close RV is not tick RV, noise-robust RV, or jump classification.",
        "- Remaining windows store extrema, terminal return and sampled RV. They do not claim first-passage order from OHLC.",
        "- Daily VX/VIX, chain IV, Context fits and Location evaluation remain separate.",
        "",
        "## Units",
        "",
        "- Prices: raw-contract ticks (1 tick = 0.25 index point).",
        "- Range: ticks, points, fraction of open, and ln(H/L).",
        "- GK / Parkinson / Rogers–Satchell / YZ / RV: log-return squared. Mean-per-interval and accumulated sum are distinct and are not annualized.",
        "",
        "## Output tables",
        "",
    ]
    for name, ref in refs.items():
        if not isinstance(ref, dict) or "sha256" not in ref:
            continue
        lines.append(
            f"- `{Path(ref.get('path', name)).name}` ({ref.get('rows', 'n/a')} rows, "
            f"{ref.get('size_bytes', 0)} bytes, SHA-256 `{ref['sha256']}`): {ref.get('kind')}."
        )
    lines.extend(["", "## Counts", ""])
    for key, value in counts.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Date-block means (equal intended-date universe)", ""])
    for label, block in (statistics.get("groups") or {}).items():
        if block is None:
            continue
        if label.startswith("root=") and "|session=cash_rth|" in label:
            lines.append(f"### {label}")
            lines.append(f"- Parkinson: {_fmt_mean(block, 'parkinson')}")
            lines.append(f"- Garman–Klass 19a: {_fmt_mean(block, 'garman_klass')}")
            lines.append(f"- Rogers–Satchell: {_fmt_mean(block, 'rogers_satchell')}")
            lines.append("")
    pair = statistics.get("nq2024_original_vs_primary") or {}
    if pair:
        lines.extend([
            "## Original versus primary NQ 2024",
            "",
            "The original acquisition is a same-calendar sensitivity, not an independent sample.",
            f"- Both present: {pair.get('both_present')}; primary only: {pair.get('primary_only')}; original only: {pair.get('original_only')}.",
            f"- GK original minus primary: {_fmt_mean(pair.get('statistics'), 'gk_original_minus_primary')}",
            "",
        ])
    if tests:
        lines.extend(["## Internal suite", "", f"- tests={tests.get('tests')} passed={tests.get('passed')} "
                     f"failures={tests.get('failures')} errors={tests.get('errors')}", ""])
    lines.extend([
        "## Dispositions retained",
        "",
        "Missing input, invalid OHLC, negative unclipped GK, warmup, roll (previous close NULL), "
        "short sessions, unknown missing bars, not-applicable remaining cuts, and stage-purged labels remain as rows.",
        "",
    ])
    return "\n".join(lines) + "\n"


def require_protocol(protocol):
    if not isinstance(protocol, dict):
        raise ContractError("protocol must be the frozen physical-volatility contract")
    if protocol.get("kind") != PROTOCOL_KIND or protocol.get("version") != 1:
        raise IntegrityError("frozen physical-volatility contract kind/version changed")
    if protocol.get("family") != FAMILY or protocol.get("full_family_complete") is not False:
        raise IntegrityError("frozen physical-volatility family identity changed")
    eq = protocol.get("measurement_equations") or {}
    if eq.get("garman_klass_practical_eq19a") != GK19A or eq.get("parkinson") != PARKINSON_EQ:
        raise IntegrityError("frozen estimator equations changed")
    if eq.get("rogers_satchell") != RS_EQ or eq.get("yang_zhang") != YZ_EQ:
        raise IntegrityError("frozen estimator equations changed")
    if len(protocol.get("canonical_partitions") or ()) != 15:
        raise IntegrityError("frozen contract must list all 15 admitted partitions")
    return protocol


def execute_own_suite():
    global _SUITE_ACTIVE
    if _SUITE_ACTIVE:
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "passed": True,
                "reentered": True, "cpu_seconds": 0.0}
    started = time_mod.process_time()
    _SUITE_ACTIVE = True
    try:
        loader = unittest.defaultTestLoader
        try:
            suite = loader.loadTestsFromName("tests.test_physical_ohlc_volatility")
        except (ImportError, AttributeError):
            import importlib.util
            here = Path(__file__).resolve()
            matches = [candidate for candidate in (
                here.parents[3] / "tests" / "test_physical_ohlc_volatility.py",
                here.parents[2] / "tests" / "test_physical_ohlc_volatility.py",
            ) if candidate.is_file()]
            if not matches:
                raise IntegrityError("physical-volatility own suite is not importable")
            path = matches[0]
            spec = importlib.util.spec_from_file_location("test_physical_ohlc_volatility", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            suite = loader.loadTestsFromModule(module)
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        payload = {
            "tests": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "passed": result.wasSuccessful(),
            "cpu_seconds": time_mod.process_time() - started,
            "report": stream.getvalue(),
        }
        if not payload["passed"]:
            text = payload["report"]
            print(text, flush=True)
            raise IntegrityError(
                "physical-volatility own suite failed before actual data\n" + text
            )
        return payload
    finally:
        _SUITE_ACTIVE = False


def _attempt_id(packet):
    configuration = packet.get("configuration") if isinstance(packet.get("configuration"), dict) else {}
    value = packet.get("attempt_id") or configuration.get("attempt_id")
    if type(value) is not str or not value or any(ch in value for ch in "/\\"):
        raise ContractError("packet requires an explicit attempt_id for bounded outputs")
    return value


def run(*, packet, protocol, root, store):
    started = time_mod.process_time()
    protocol = require_protocol(protocol)
    root = Path(root)
    if not isinstance(packet, dict) or packet.get("mode") not in ("pilot", "full"):
        raise ContractError("packet.mode must be pilot or full")
    mode = packet["mode"]
    configuration = packet.get("configuration") if isinstance(packet.get("configuration"), dict) else {}
    accepted = accepted_pilot_from(configuration)
    calendar_spec = protocol["cash_calendar"]
    calendar_path = Path(calendar_spec["path"])
    if file_digest(calendar_path) != calendar_spec["sha256"]:
        raise IntegrityError("cash calendar identity differs from the frozen contract")
    calendar = CashCalendar(calendar_path)
    tests = None
    if mode == "pilot" or accepted is None:
        tests = execute_own_suite()
    elif accepted.get("tests", {}).get("passed") is True:
        tests = {**accepted["tests"], "reused": True}
    else:
        tests = execute_own_suite()
    outputs = BoundedOutputs(
        root / "reports" / "physical-volatility-runs" / _attempt_id(packet) / "outputs",
        maximum_total_bytes=int(protocol["resources"]["per_attempt_output_bytes"]) - OUTPUT_RESERVE_BYTES,
        maximum_file_bytes=OUTPUT_MAX_FILE_BYTES,
    )
    session_rows, history_rows, scale_rows, seasonal_rows, remaining_rows = [], [], [], [], []
    intended_by_group = {}
    carry = {}
    year_tails = {}
    reused = 0
    computed = 0
    source_versions = []
    computed_partitions = []
    selected = select_partitions(protocol, mode, accepted)
    if accepted is not None:
        session_table = read_output_parquet(accepted["refs"]["session_measurements"])
        history_table = read_output_parquet(accepted["refs"]["history_windows"])
        scale_table = read_output_parquet(accepted["refs"]["scale_aggregates"])
        seasonal_table = read_output_parquet(accepted["refs"]["seasonal_cells"])
        remaining_table = read_output_parquet(accepted["refs"]["remaining_windows"])
        session_rows.extend(session_table.to_pylist())
        history_rows.extend(history_table.to_pylist())
        scale_rows.extend(scale_table.to_pylist())
        seasonal_rows.extend(seasonal_table.to_pylist())
        remaining_rows.extend(remaining_table.to_pylist())
        reused += 1
        for row in session_rows:
            key = (row["root"], row["session"], row["variant"])
            carry.setdefault(key, []).append(row)
        for key, rows in list(carry.items()):
            carry[key] = rows[-130:]
        year_tails[("NQ", 2020)] = {key: list(rows) for key, rows in carry.items()}
        if accepted.get("source_versions"):
            source_versions.extend(list(accepted["source_versions"]))
        else:
            reused_keys = {(row["root"], int(row["year"]), row["variant"])
                           for row in accepted.get("computed_partitions") or ()}
            for spec in protocol["canonical_partitions"]:
                if partition_key(spec) in reused_keys:
                    source_versions.append(source_version_record(spec))
        for row in accepted.get("computed_partitions") or ({"root": "NQ", "year": 2020, "variant": "primary_corrected"},):
            intended_by_group[(row["root"], int(row["year"]), row["variant"])] = sorted({
                item["date"] for item in session_rows
                if item["root"] == row["root"] and int(item["year"]) == int(row["year"])
                and item["variant"] == row["variant"]
            })
    for partition in selected:
        if partition.get("_reuse"):
            continue
        borrow = None
        if partition["variant"] == "original_nq2024_sensitivity":
            borrow = {"source_sha256": next(
                (item["source_sha256"] for item in protocol["canonical_partitions"]
                 if item["root"] == "NQ" and int(item["year"]) == 2023 and item["variant"] == "primary_corrected"),
                None), "variant": "primary_corrected"}
            for session in SESSIONS:
                tail = year_tails.get(("NQ", 2023), {}).get(("NQ", session, "primary_corrected"), [])
                carry[("NQ", session, "primary_corrected")] = list(tail)
        result = process_partition(store, calendar, partition, carry, history_borrow=borrow)
        if partition["variant"] == "primary_corrected":
            year_tails[(partition["root"], int(partition["year"]))] = result["carry"]
        session_rows.extend(result["session"])
        history_rows.extend(result["history"])
        scale_rows.extend(result["scale"])
        seasonal_rows.extend(result["seasonal"])
        remaining_rows.extend(result["remaining"])
        carry.update(result["carry"])
        intended_by_group[(partition["root"], int(partition["year"]), partition["variant"])] = result["intended_dates"]
        source_versions.append(source_version_record(partition, result["source_version"]))
        computed_partitions.append(computed_partition_record(partition, result["source_version"]))
        computed += 1
        del result
    statistics = build_statistics(session_rows, history_rows, scale_rows, seasonal_rows, remaining_rows,
                                  intended_by_group)
    refs = {
        "session_measurements": write_parquet(outputs, "session-measurements.parquet",
                                              rows_to_table(session_rows, session_measurement_schema()),
                                              kind="physical_ohlc_session_measurements_v1"),
        "history_windows": write_parquet(outputs, "history-windows.parquet",
                                         rows_to_table(history_rows, history_window_schema()),
                                         kind="physical_ohlc_history_windows_v1"),
        "scale_aggregates": write_parquet(outputs, "scale-aggregates.parquet",
                                          rows_to_table(scale_rows, scale_aggregate_schema()),
                                          kind="physical_ohlc_scale_aggregates_v1"),
        "seasonal_cells": write_parquet(outputs, "seasonal-cells.parquet",
                                        rows_to_table(seasonal_rows, seasonal_cell_schema()),
                                        kind="physical_ohlc_seasonal_cells_v1"),
        "remaining_windows": write_parquet(outputs, "remaining-windows.parquet",
                                           rows_to_table(remaining_rows, remaining_window_schema()),
                                           kind="physical_ohlc_remaining_windows_v1"),
    }
    counts = {
        "session_rows": len(session_rows),
        "history_rows": len(history_rows),
        "scale_rows": len(scale_rows),
        "seasonal_rows": len(seasonal_rows),
        "remaining_rows": len(remaining_rows),
        "partitions_computed": computed,
        "partitions_reused": reused,
        "intended_date_groups": len(intended_by_group),
        "expected_primary_cash_dates_per_root": EXPECTED_PRIMARY_CASH_DATES_PER_ROOT,
        "expected_original_nq2024_dates": EXPECTED_ORIGINAL_NQ2024_DATES,
        "expected_pilot_dates": EXPECTED_PILOT_DATES,
        "population_cash_dates": len(intended_cash_days(calendar, POPULATION_FIRST, POPULATION_LAST)),
        "partitions_in_protocol": len(protocol["canonical_partitions"]),
        "partitions_seen": len(selected),
        "pilot_dates": len(intended_by_group.get(PILOT_KEY) or ()),
        "original_nq2024_dates": len(intended_by_group.get(("NQ", 2024, "original_nq2024_sensitivity")) or ()),
    }
    if counts['population_cash_dates'] != EXPECTED_PRIMARY_CASH_DATES_PER_ROOT or counts['pilot_dates'] != EXPECTED_PILOT_DATES:
        raise IntegrityError('physical volatility intended-date conservation failed')
    if mode == 'full' and (counts['partitions_seen'] != 15 or counts['original_nq2024_dates'] != EXPECTED_ORIGINAL_NQ2024_DATES):
        raise IntegrityError('physical volatility full source-partition conservation failed')
    refs["statistics"] = outputs.json("statistics.json", statistics, kind="physical_ohlc_volatility_statistics_v1")
    report = write_report(session_rows, statistics, refs, counts, tests, mode, reused)
    with outputs.create("results.md") as stream:
        stream.write(report.encode())
    refs["results"] = outputs.reference("results.md", kind="physical_ohlc_volatility_results_md_v1")
    refs["source_versions"] = outputs.json("source-versions.json", source_versions,
                                           kind="physical_ohlc_source_version_digest_v1")
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    resources = {
        "cpu_seconds": time_mod.process_time() - started,
        "rss_bytes": int(rss * 1024),
        "output_bytes": outputs.written,
        "partitions_computed": computed,
        "partitions_reused": reused,
    }
    return {
        "success": True,
        "output_bytes": outputs.written,
        "refs": refs,
        "counts": counts,
        "resources": resources,
        "family_complete": False,
        "tests": tests,
        "model_fits": 0,
        "context_models_complete": False,
        "location_quality_complete": False,
        "purpose": PURPOSE,
        "scope_ids": list(protocol.get("scope_ids") or ()),
        "computed_partitions": computed_partitions,
        "source_versions": source_versions,
    }


__all__ = [
    "FAMILY", "PURPOSE", "VERSION",
    "EXPECTED_ORIGINAL_NQ2024_DATES", "EXPECTED_PILOT_DATES",
    "EXPECTED_PRIMARY_CASH_DATES_PER_ROOT",
    "accepted_pilot_from", "ceil_to_minute", "close_log_return",
    "columns_from_series", "compact_source_lineage", "computed_partition_record",
    "execute_own_suite", "garman_klass_practical_eq19a",
    "history_window_row", "history_window_schema", "history_window_version",
    "last_published_close", "measure_remaining", "measure_scales",
    "measure_seasonal_cells",
    "interval_estimators", "ohlc_domain_status", "overnight_log_gap",
    "parkinson_variance", "positive_finite", "remaining_window_schema",
    "require_protocol",
    "realized_variance", "rogers_satchell_variance", "run",
    "sample_variance", "sampled_close_returns", "scale_aggregate_schema",
    "seasonal_cell_schema", "select_partitions", "session_bounds",
    "session_measurement_schema", "signed_semivariances", "slice_ohlc",
    "source_version_of", "source_version_record",
    "stage_of", "true_range_ticks", "yang_zhang_from_sessions", "yang_zhang_k",
]
