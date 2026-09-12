#!/usr/bin/env python3
"""Audit acquired futures windows without scanning the NQ MBP-1 payload.

The audit uses Parquet footer statistics for event bounds and row-group
envelopes.  It reads only:

* the NQ one-minute ``t`` column (4.7 million rows),
* the NQ one-second ``t`` column (128 million rows, streamed), and
* ``t`` at ambiguous MBP-1 ownership boundaries plus ``t,action`` in the
  first/last MBP-1 row group containing a trade.

An observed min/max or row-group envelope is not a continuity claim.  The
generated report keeps nominal partition coverage, observed bounds, and the
limited continuity comparisons separate.
"""

from __future__ import annotations

import argparse
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Iterator, Sequence
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


NS = 1_000_000_000
MS_NS = 1_000_000
MINUTE_NS = 60 * NS
ET = ZoneInfo("America/New_York")
MONTH_RE = re.compile(r"^(\d{4})-(\d{2})\.parquet$")
WEEK_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.parquet$")
YEAR_RE = re.compile(r"^(\d{4})\.parquet$")


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    relative_path: str
    native_unit_ns: int
    partition_kind: str
    bar_duration_ns: int | None = None


NQ_SPECS = (
    DatasetSpec(
        "nq_mbp1",
        "quantpad/cme__nq-continuous-futures__mbp-1",
        1,
        "mixed_monthly_weekly",
    ),
    DatasetSpec(
        "nq_trades",
        "quantpad/cme__nq-continuous-futures__trades",
        1,
        "weekly",
    ),
    DatasetSpec(
        "nq_ohlcv_1s",
        "quantpad/cme__nq-continuous-futures__ohlcv-1s",
        MS_NS,
        "annual",
        NS,
    ),
    DatasetSpec(
        "nq_ohlcv_1m",
        "quantpad/cme__nq-continuous-futures__ohlcv-1m",
        MS_NS,
        "annual",
        MINUTE_NS,
    ),
)


def iso_ns(value: int | None) -> str | None:
    """Render an integer epoch nanosecond exactly, without float conversion."""

    if value is None:
        return None
    seconds, nanos = divmod(int(value), NS)
    stamp = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return stamp.strftime("%Y-%m-%dT%H:%M:%S") + f".{nanos:09d}Z"


def ns_from_aware(value: datetime) -> int:
    utc = value.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = utc - epoch
    return (
        delta.days * 86_400 * NS
        + delta.seconds * NS
        + delta.microseconds * 1_000
    )


def session_bounds_ns(day: date) -> tuple[int, int]:
    """Globex trade date: 18:00 ET prior day through 17:00 ET trade date."""

    start = datetime.combine(day - timedelta(days=1), time(18), tzinfo=ET)
    end = datetime.combine(day, time(17), tzinfo=ET)
    return ns_from_aware(start), ns_from_aware(end)


def trade_date_et(timestamp_ns: int) -> date:
    seconds, nanos = divmod(int(timestamp_ns), NS)
    utc = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(
        microsecond=nanos // 1_000
    )
    local = utc.astimezone(ET)
    return local.date() + timedelta(days=1) if local.hour >= 18 else local.date()


def month_bounds_ns(year: int, month: int) -> tuple[int, int]:
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    return ns_from_aware(start), ns_from_aware(end)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reject_outputs_within_data_root(
    data_root: Path, output_paths: Sequence[Path]
) -> None:
    """Keep generated artifacts outside the immutable acquired-data tree."""

    resolved_root = data_root.resolve()
    invalid = [
        path
        for path in output_paths
        if path.resolve().is_relative_to(resolved_root)
    ]
    if invalid:
        rendered = ", ".join(str(path) for path in invalid)
        raise ValueError(
            "audit outputs must resolve outside --data-root "
            f"({resolved_root}); rejected: {rendered}"
        )


def expected_labels(kind: str, first: str, last: str) -> list[str]:
    """Enumerate inclusive nominal labels between two physical labels."""

    if kind == "annual":
        return [str(year) for year in range(int(first), int(last) + 1)]
    if kind == "monthly":
        year, month = map(int, first.split("-"))
        end_year, end_month = map(int, last.split("-"))
        out: list[str] = []
        while (year, month) <= (end_year, end_month):
            out.append(f"{year:04d}-{month:02d}")
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
        return out
    if kind == "weekly":
        current, end = date.fromisoformat(first), date.fromisoformat(last)
        out = []
        while current <= end:
            out.append(current.isoformat())
            current += timedelta(days=7)
        return out
    raise ValueError(f"unknown partition kind: {kind}")


def coalesce_month_labels(labels: Iterable[str]) -> list[str]:
    values = sorted(set(labels))
    if not values:
        return []
    serials = [int(value[:4]) * 12 + int(value[5:7]) - 1 for value in values]
    runs = coalesce_values(serials, 1)
    def label(serial: int) -> str:
        year, month0 = divmod(serial, 12)
        return f"{year:04d}-{month0 + 1:02d}"
    return [
        label(start) if count == 1 else f"{label(start)} through {label(end)}"
        for start, end, count in runs
    ]


def coalesce_values(values: Iterable[int], step: int) -> list[tuple[int, int, int]]:
    """Return inclusive fixed-step runs as ``(first, last, count)``."""

    runs: list[list[int]] = []
    for value in sorted(set(int(item) for item in values)):
        if runs and value == runs[-1][1] + step:
            runs[-1][1] = value
            runs[-1][2] += 1
        else:
            runs.append([value, value, 1])
    return [tuple(item) for item in runs]


def occupied_minute_keys(
    values_ms: np.ndarray, instruments: np.ndarray
) -> set[tuple[int, int]]:
    """Collapse adjacent 1s rows to occupied minute/instrument keys.

    Repeated non-adjacent runs are harmless because the return value is a set.
    This avoids sorting the entire second-bar batch as structured records.
    """

    if len(values_ms) != len(instruments):
        raise ValueError("timestamp and instrument arrays must have equal length")
    if not len(values_ms):
        return set()
    minute_ns = (values_ms.astype(np.int64) // 60_000) * MINUTE_NS
    instrument_values = instruments.astype(np.int64)
    change = np.empty(len(minute_ns), dtype=bool)
    change[0] = True
    change[1:] = (minute_ns[1:] != minute_ns[:-1]) | (
        instrument_values[1:] != instrument_values[:-1]
    )
    return {
        (int(start), int(instrument))
        for start, instrument in zip(
            minute_ns[change], instrument_values[change], strict=True
        )
    }


def subtract_interval(
    interval: tuple[int, int], cutters: Sequence[tuple[int, int]]
) -> list[tuple[int, int]]:
    pieces = [interval]
    for cut_start, cut_end in cutters:
        next_pieces: list[tuple[int, int]] = []
        for start, end in pieces:
            if cut_end <= start or cut_start >= end:
                next_pieces.append((start, end))
            else:
                if start < cut_start:
                    next_pieces.append((start, min(end, cut_start)))
                if cut_end < end:
                    next_pieces.append((max(start, cut_end), end))
        pieces = [(start, end) for start, end in next_pieces if end > start]
    return pieces


def _partition_label(path: Path) -> tuple[str | None, str | None]:
    for kind, pattern in (
        ("monthly", MONTH_RE),
        ("weekly", WEEK_RE),
        ("annual", YEAR_RE),
    ):
        match = pattern.match(path.name)
        if match:
            return kind, path.stem
    return None, None


def inspect_dataset(data_root: Path, spec: DatasetSpec) -> dict[str, Any]:
    directory = data_root / spec.relative_path
    if not directory.is_dir():
        raise FileNotFoundError(directory)
    files: list[dict[str, Any]] = []
    row_groups: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.parquet")):
        parquet = pq.ParquetFile(path)
        names = parquet.schema_arrow.names
        if "t" not in names:
            raise ValueError(f"{path} lacks t")
        t_index = names.index("t")
        kind, label = _partition_label(path)
        minima: list[int] = []
        maxima: list[int] = []
        missing_stats = 0
        for group_index in range(parquet.num_row_groups):
            group = parquet.metadata.row_group(group_index)
            stats = group.column(t_index).statistics
            if stats is None or stats.min is None or stats.max is None:
                missing_stats += 1
                row_groups.append(
                    {
                        "dataset": spec.key,
                        "path": str(path),
                        "physical_partition_kind": kind,
                        "row_group": group_index,
                        "rows": group.num_rows,
                        "observed_min_ns": None,
                        "observed_max_ns": None,
                        "envelope_end_exclusive_ns": None,
                        "statistics": "missing",
                    }
                )
                continue
            lower = int(stats.min) * spec.native_unit_ns
            upper = int(stats.max) * spec.native_unit_ns
            minima.append(lower)
            maxima.append(upper)
            row_groups.append(
                {
                    "dataset": spec.key,
                    "path": str(path),
                    "physical_partition_kind": kind,
                    "row_group": group_index,
                    "rows": group.num_rows,
                    "observed_min_ns": lower,
                    "observed_max_ns": upper,
                    "envelope_end_exclusive_ns": upper + spec.native_unit_ns,
                    "statistics": "parquet_footer_min_max",
                }
            )
        files.append(
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "rows": parquet.metadata.num_rows,
                "row_groups": parquet.num_row_groups,
                "row_groups_missing_t_statistics": missing_stats,
                "partition_kind": kind,
                "nominal_label": label,
                "observed_min_ns": min(minima) if minima else None,
                "observed_max_ns": max(maxima) if maxima else None,
            }
        )
    observed_min = min(
        (row["observed_min_ns"] for row in files if row["observed_min_ns"] is not None),
        default=None,
    )
    observed_max = max(
        (row["observed_max_ns"] for row in files if row["observed_max_ns"] is not None),
        default=None,
    )
    result = {
        "dataset_id": spec.relative_path,
        "native_t_unit": "ns" if spec.native_unit_ns == 1 else "ms",
        "bar_duration_ns": spec.bar_duration_ns,
        "file_count": len(files),
        "empty_file_count": sum(row["rows"] == 0 for row in files),
        "empty_files": [row["path"] for row in files if row["rows"] == 0],
        "total_bytes": sum(row["bytes"] for row in files),
        "total_rows": sum(row["rows"] for row in files),
        "row_group_count": len(row_groups),
        "row_groups_missing_t_statistics": sum(
            row["statistics"] == "missing" for row in row_groups
        ),
        "observed_first_t_ns": observed_min,
        "observed_first_t_utc": iso_ns(observed_min),
        "observed_last_t_ns": observed_max,
        "observed_last_t_utc": iso_ns(observed_max),
        "bounds_evidence": "minimum/maximum of every Parquet row-group t statistic",
        "internal_continuity_checked": False,
        "files": files,
        "_row_groups": row_groups,
    }
    if spec.partition_kind != "mixed_monthly_weekly" and files:
        labels = [row["nominal_label"] for row in files if row["nominal_label"]]
        expected = expected_labels(spec.partition_kind, min(labels), max(labels))
        result["nominal_partitions"] = {
            "kind": spec.partition_kind,
            "first_label": min(labels),
            "last_label": max(labels),
            "expected_between_physical_endpoints": len(expected),
            "present": len(labels),
            "missing_between_physical_endpoints": sorted(set(expected) - set(labels)),
            "evidence": "physical filenames; says nothing about rows inside non-empty files",
        }
    return result


def _physical_track(
    files: Sequence[dict[str, Any]], kind: str
) -> dict[str, Any]:
    selected = [row for row in files if row["partition_kind"] == kind]
    labels = [row["nominal_label"] for row in selected]
    if not labels:
        return {
            "kind": kind,
            "status": "absent",
            "first_label": None,
            "last_label": None,
            "file_count": 0,
            "rows": 0,
            "row_groups": 0,
            "empty_files": [],
            "missing_between_physical_endpoints": None,
        }
    expected = expected_labels(kind, min(labels), max(labels))
    return {
        "kind": kind,
        "status": "present",
        "first_label": min(labels),
        "last_label": max(labels),
        "file_count": len(selected),
        "rows": sum(row["rows"] for row in selected),
        "row_groups": sum(row["row_groups"] for row in selected),
        "empty_files": [row["path"] for row in selected if row["rows"] == 0],
        "missing_between_physical_endpoints": sorted(set(expected) - set(labels)),
    }


def _count_t_in_interval(path: Path, start_ns: int, end_ns: int) -> dict[str, Any]:
    parquet = pq.ParquetFile(path)
    t_index = parquet.schema_arrow.names.index("t")
    rows = 0
    observed_min: int | None = None
    observed_max: int | None = None
    scanned_groups: list[int] = []
    for group_index in range(parquet.num_row_groups):
        stats = parquet.metadata.row_group(group_index).column(t_index).statistics
        if stats is None or int(stats.max) < start_ns or int(stats.min) >= end_ns:
            continue
        scanned_groups.append(group_index)
        values = parquet.read_row_group(group_index, columns=["t"])["t"]
        mask = pc.and_(
            pc.greater_equal(values, pa.scalar(start_ns, type=values.type)),
            pc.less(values, pa.scalar(end_ns, type=values.type)),
        )
        selected = pc.filter(values, mask)
        if len(selected):
            lower = int(pc.min(selected).as_py())
            upper = int(pc.max(selected).as_py())
            observed_min = lower if observed_min is None else min(observed_min, lower)
            observed_max = upper if observed_max is None else max(observed_max, upper)
            rows += len(selected)
    return {
        "rows": rows,
        "observed_min_ns": observed_min,
        "observed_max_ns": observed_max,
        "row_groups_read": scanned_groups,
    }


def audit_mbp_ownership(mbp: dict[str, Any]) -> dict[str, Any]:
    """Apply monthly precedence, then validate every weekly-exclusive span."""

    files = mbp["files"]
    monthly = [row for row in files if row["partition_kind"] == "monthly"]
    weekly = [row for row in files if row["partition_kind"] == "weekly"]
    monthly_spans: list[tuple[int, int]] = []
    for row in monthly:
        if row["observed_min_ns"] is None or row["observed_max_ns"] is None:
            continue
        match = MONTH_RE.match(Path(row["path"]).name)
        assert match is not None
        nominal_start, nominal_end = month_bounds_ns(
            int(match.group(1)), int(match.group(2))
        )
        start = max(row["observed_min_ns"], nominal_start)
        end = min(row["observed_max_ns"] + 1, nominal_end)
        if end > start:
            monthly_spans.append((start, end))
    monthly_spans.sort()

    candidates: list[dict[str, Any]] = []
    for row in weekly:
        if row["observed_min_ns"] is None or row["observed_max_ns"] is None:
            continue
        source = (row["observed_min_ns"], row["observed_max_ns"] + 1)
        for start, end in subtract_interval(source, monthly_spans):
            validation = _count_t_in_interval(Path(row["path"]), start, end)
            candidates.append(
                {
                    "path": row["path"],
                    "start_ns": start,
                    "start_utc": iso_ns(start),
                    "end_ns_exclusive": end,
                    "end_utc_exclusive": iso_ns(end),
                    "envelope_basis": "weekly observed envelope minus monthly observed envelopes",
                    "targeted_t_scan": validation,
                }
            )
    rows_outside_monthly = sum(
        item["targeted_t_scan"]["rows"] for item in candidates
    )
    return {
        "precedence": "monthly primary; weekly considered only outside monthly observed envelopes",
        "monthly_track": _physical_track(files, "monthly"),
        "weekly_track": _physical_track(files, "weekly"),
        "weekly_exclusive_envelope_candidate_count": len(candidates),
        "weekly_rows_observed_outside_monthly_envelopes": rows_outside_monthly,
        "weekly_exclusive_candidates": candidates,
        "conclusion": (
            "monthly track absent; monthly-primary ownership cannot be evaluated"
            if not monthly
            else (
                "targeted scans found no weekly rows outside monthly observed envelopes"
                if rows_outside_monthly == 0
                else "weekly files contain observed rows outside monthly envelopes"
            )
        ),
        "overlap_identity_checked": False,
        "continuity_checked": False,
        "limitation": (
            "The targeted scans settle whether weekly rows exist outside monthly "
            "envelopes. They do not compare every overlapping weekly row with its "
            "monthly counterpart."
        ),
    }


def load_one_minute_keys(
    data_root: Path,
) -> tuple[list[int], set[int], set[tuple[int, int]]]:
    directory = data_root / NQ_SPECS[-1].relative_path
    starts: list[int] = []
    keys: set[tuple[int, int]] = set()
    for path in sorted(directory.glob("*.parquet")):
        parquet = pq.ParquetFile(path)
        for batch in parquet.iter_batches(
            columns=["t", "instrument_id"], batch_size=1_000_000
        ):
            values = batch.column(0).to_numpy(zero_copy_only=False).astype(np.int64)
            instruments = batch.column(1).to_numpy(zero_copy_only=False).astype(np.int64)
            starts_ns = values * MS_NS
            starts.extend(starts_ns.tolist())
            keys.update(
                (int(start), int(instrument))
                for start, instrument in zip(starts_ns, instruments, strict=True)
            )
    starts.sort()
    return starts, set(starts), keys


def compare_one_second_to_minute(
    data_root: Path,
    minute_start_set: set[int],
    minute_key_set: set[tuple[int, int]],
) -> dict[str, Any]:
    directory = data_root / NQ_SPECS[2].relative_path
    missing_minute_keys: set[tuple[int, int]] = set()
    for path in sorted(directory.glob("*.parquet")):
        parquet = pq.ParquetFile(path)
        for batch in parquet.iter_batches(
            columns=["t", "instrument_id"], batch_size=1_000_000
        ):
            values_ms = batch.column(0).to_numpy(zero_copy_only=False).astype(np.int64)
            instruments = batch.column(1).to_numpy(zero_copy_only=False).astype(np.int64)
            batch_keys = occupied_minute_keys(values_ms, instruments)
            for key in batch_keys:
                if key not in minute_key_set:
                    missing_minute_keys.add(key)
    return summarize_missing_minute_keys(
        missing_minute_keys,
        minute_start_set,
        evidence_level="exact streamed native t/instrument_id column comparison",
    )


def summarize_missing_minute_keys(
    missing_minute_keys: set[tuple[int, int]],
    minute_start_set: set[int],
    *,
    evidence_level: str,
) -> dict[str, Any]:
    missing_minute_starts = {
        key[0] for key in missing_minute_keys if key[0] not in minute_start_set
    }
    runs = coalesce_values(missing_minute_starts, MINUTE_NS)
    session_counts = Counter(trade_date_et(value) for value in missing_minute_starts)
    full_sessions: list[dict[str, Any]] = []
    for day, count in sorted(session_counts.items()):
        start, end = session_bounds_ns(day)
        if count == (end - start) // MINUTE_NS and all(
            value in missing_minute_starts for value in range(start, end, MINUTE_NS)
        ):
            session_keys = [
                key for key in missing_minute_keys if start <= key[0] < end
            ]
            full_sessions.append(
                {
                    "trade_date_et": day.isoformat(),
                    "start_ns": start,
                    "start_utc": iso_ns(start),
                    "end_ns_exclusive": end,
                    "end_utc_exclusive": iso_ns(end),
                    "minute_buckets_present_in_1s_absent_in_1m": count,
                    "missing_minute_instrument_key_count": len(session_keys),
                    "instrument_ids": sorted({key[1] for key in session_keys}),
                }
            )
    full_session_minutes = {
        value
        for item in full_sessions
        for value in range(item["start_ns"], item["end_ns_exclusive"], MINUTE_NS)
    }
    isolated = sorted(missing_minute_starts - full_session_minutes)
    return {
        "comparison": (
            "one-second occupied (minute_start,instrument_id) keys minus one-minute keys"
        ),
        "keys_present_in_1s_absent_in_1m": len(missing_minute_keys),
        "minute_buckets_present_in_1s_absent_in_1m": len(missing_minute_starts),
        "consecutive_runs": [
            {
                "start_ns": start,
                "start_utc": iso_ns(start),
                "last_minute_start_ns": end,
                "last_minute_start_utc": iso_ns(end),
                "minute_count": count,
            }
            for start, end, count in runs
        ],
        "complete_globex_sessions": full_sessions,
        "isolated_minute_count": len(isolated),
        "isolated_minutes": [iso_ns(value) for value in isolated],
        "_missing_keys": sorted(missing_minute_keys),
        "evidence_level": evidence_level,
        "interpretation": (
            "A listed bucket has at least one native 1s bar and no native 1m row. "
            "It is a cross-format discrepancy; session/closure context is retained."
        ),
    }


def load_missing_minute_keys(path: Path) -> set[tuple[int, int]]:
    payload = json.loads(path.read_text())
    return {
        (int(row["minute_start_ns"]), int(row["instrument_id"]))
        for row in payload.get("missing_keys", [])
    }


def endpoint_session_set(row_groups: Sequence[dict[str, Any]]) -> set[date]:
    result: set[date] = set()
    for row in row_groups:
        lower, upper = row["observed_min_ns"], row["observed_max_ns"]
        if lower is not None:
            result.add(trade_date_et(lower))
        if upper is not None:
            result.add(trade_date_et(upper))
    return result


def compare_session_presence(
    datasets: dict[str, dict[str, Any]],
    minute_starts: Sequence[int],
    minute_discrepancies: dict[str, Any],
) -> dict[str, Any]:
    minute_sessions = {trade_date_et(value) for value in minute_starts}
    mbp_monthly_paths = {
        row["path"]
        for row in datasets["nq_mbp1"]["files"]
        if row["partition_kind"] == "monthly"
    }
    mbp_groups = [
        row
        for row in datasets["nq_mbp1"]["_row_groups"]
        if row["path"] in mbp_monthly_paths
    ]
    mbp_sessions = endpoint_session_set(mbp_groups)
    trade_sessions = endpoint_session_set(datasets["nq_trades"]["_row_groups"])
    within_mbp = {
        item
        for item in minute_sessions
        if min(mbp_sessions) <= item <= max(mbp_sessions)
    }
    missing_mbp = sorted(within_mbp - mbp_sessions)
    mbp_without_minute = sorted(mbp_sessions - minute_sessions)
    trade_window = {
        item
        for item in minute_sessions
        if min(trade_sessions) <= item <= max(trade_sessions)
    }
    missing_trade = sorted(trade_window - trade_sessions)
    trade_without_minute = sorted(trade_sessions - minute_sessions)
    full_session_rows = []
    for item in minute_discrepancies["complete_globex_sessions"]:
        day = date.fromisoformat(item["trade_date_et"])
        full_session_rows.append(
            {
                **item,
                "mbp1_endpoint_evidence": day in mbp_sessions,
                "standalone_trade_endpoint_evidence": day in trade_sessions,
            }
        )
    minute_discrepancies["complete_globex_sessions"] = full_session_rows
    return {
        "session_convention": "18:00 ET prior civil date to 17:00 ET trade date",
        "nq_1m_exact_session_count": len(minute_sessions),
        "nq_1m_exact_first_session": min(minute_sessions).isoformat(),
        "nq_1m_exact_last_session": max(minute_sessions).isoformat(),
        "nq_1m_session_count_within_mbp1_endpoint_bounds": len(within_mbp),
        "mbp1_row_group_endpoint_session_count": len(mbp_sessions),
        "mbp1_first_endpoint_session": min(mbp_sessions).isoformat(),
        "mbp1_last_endpoint_session": max(mbp_sessions).isoformat(),
        "one_minute_sessions_without_mbp1_row_group_endpoint": [
            item.isoformat() for item in missing_mbp
        ],
        "mbp1_endpoint_sessions_without_one_minute_rows": [
            item.isoformat() for item in mbp_without_minute
        ],
        "standalone_trade_row_group_endpoint_session_count": len(trade_sessions),
        "one_minute_sessions_without_trade_row_group_endpoint_within_trade_bounds": [
            item.isoformat() for item in missing_trade
        ],
        "trade_endpoint_sessions_without_one_minute_rows": [
            item.isoformat() for item in trade_without_minute
        ],
        "evidence_level": (
            "1m dates are exact from all t values. MBP-1/trades presence is proven "
            "when an actual row-group min or max falls in the session."
        ),
        "absence_limitation": (
            "Row-group endpoints are not an event-level continuity scan. A group "
            "could cross a session without an endpoint inside it; such a session is "
            "not declared missing from endpoint evidence alone."
        ),
    }


def merge_envelopes(
    row_groups: Sequence[dict[str, Any]],
) -> list[tuple[int, int]]:
    values = sorted(
        (row["observed_min_ns"], row["envelope_end_exclusive_ns"])
        for row in row_groups
        if row["observed_min_ns"] is not None
    )
    merged: list[list[int]] = []
    for start, end in values:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(item) for item in merged]


def compare_mbp_envelope_gaps_to_minutes(
    datasets: dict[str, dict[str, Any]], minute_starts: Sequence[int]
) -> dict[str, Any]:
    monthly_paths = {
        row["path"]
        for row in datasets["nq_mbp1"]["files"]
        if row["partition_kind"] == "monthly"
    }
    groups = [
        row
        for row in datasets["nq_mbp1"]["_row_groups"]
        if row["path"] in monthly_paths and row["observed_min_ns"] is not None
    ]
    merged = merge_envelopes(groups)
    gaps_with_bar: list[dict[str, Any]] = []
    gap_count = 0
    for left, right in zip(merged, merged[1:]):
        start, end = left[1], right[0]
        if end <= start:
            continue
        gap_count += 1
        index = bisect_left(minute_starts, start)
        bars: list[int] = []
        while index < len(minute_starts) and minute_starts[index] < end:
            value = minute_starts[index]
            if value >= start and value + MINUTE_NS <= end:
                bars.append(value)
            index += 1
        if bars:
            gaps_with_bar.append(
                {
                    "start_ns": start,
                    "start_utc": iso_ns(start),
                    "end_ns_exclusive": end,
                    "end_utc_exclusive": iso_ns(end),
                    "complete_existing_1m_bars_inside": len(bars),
                    "first_bar_start_utc": iso_ns(bars[0]),
                    "last_bar_start_utc": iso_ns(bars[-1]),
                }
            )
    return {
        "monthly_primary_row_group_count": len(groups),
        "merged_row_group_envelope_count": len(merged),
        "gaps_between_merged_envelopes": gap_count,
        "gaps_containing_a_complete_existing_1m_bar": gaps_with_bar,
        "evidence_level": "Parquet t min/max envelopes compared with every native 1m t",
        "interpretation": (
            "A zero result finds no MBP-1 envelope gap that contains a complete "
            "minute for which the standalone 1m archive has a bar."
        ),
        "continuity_limitation": (
            "Rows inside each row-group min/max envelope were not scanned. Closures, "
            "ordinary inter-event time, and missing events can all lie inside an envelope."
        ),
    }


def mbp_trade_action_edge(path: Path, reverse: bool) -> dict[str, Any]:
    parquet = pq.ParquetFile(path)
    groups: Iterable[int]
    groups = (
        range(parquet.num_row_groups - 1, -1, -1)
        if reverse
        else range(parquet.num_row_groups)
    )
    for group_index in groups:
        table = parquet.read_row_group(group_index, columns=["t", "action"])
        selected = pc.filter(table["t"], pc.equal(table["action"], "T"))
        if len(selected):
            return {
                "path": str(path),
                "row_group_read": group_index,
                "trade_rows_in_row_group": len(selected),
                "first_trade_t_ns": int(pc.min(selected).as_py()),
                "first_trade_t_utc": iso_ns(int(pc.min(selected).as_py())),
                "last_trade_t_ns": int(pc.max(selected).as_py()),
                "last_trade_t_utc": iso_ns(int(pc.max(selected).as_py())),
            }
    raise ValueError(f"no T action in {path}")


def inspect_native_comparison(comparison_dir: Path | None) -> dict[str, Any]:
    if comparison_dir is None:
        return {"status": "not_checked", "reason": "--comparison-dir not supplied"}
    manifest_path = comparison_dir / "manifest.json"
    minute_path = comparison_dir / "native-bar-comparison.json"
    second_path = comparison_dir / "native-second-comparison.json"
    missing = [
        str(path) for path in (manifest_path, minute_path, second_path) if not path.is_file()
    ]
    if missing:
        return {"status": "not_checked", "missing_artifacts": missing}
    manifest = json.loads(manifest_path.read_text())
    minute = json.loads(minute_path.read_text())
    second = json.loads(second_path.read_text())
    plan = manifest.get("plan", {})
    if isinstance(minute, dict):
        minute_fields_equal = int(minute.get("equal_fields", 0))
        minute_fields_compared = (
            minute_fields_equal
            + len(minute.get("unresolved_fields", []))
            + len(minute.get("mismatches", []))
        )
        minute_instruments: set[int] = {
            int(row["instrument_id"])
            for row in (*minute.get("unresolved_fields", []), *minute.get("mismatches", []))
            if row.get("instrument_id") is not None
        }
        start_ns = int(minute["start_ms"]) * MS_NS
        end_ns = int(minute["end_ms_exclusive"]) * MS_NS
    else:
        minute_fields_compared = sum(len(row.get("matches", {})) for row in minute)
        minute_fields_equal = sum(
            value is True
            for row in minute
            for value in row.get("matches", {}).values()
        )
        minute_instruments = {
            int(row["instrument_id"])
            for row in minute
            if row.get("instrument_id") is not None
        }
        start_ns, end_ns = plan.get("start_ns"), plan.get("end_ns")
    minute_instruments.update(
        int(row["instrument_id"])
        for row in (*second.get("unresolved_fields", []), *second.get("mismatches", []))
        if row.get("instrument_id") is not None
    )
    mismatch_fields = Counter(
        str(row.get("field")) for row in second.get("mismatches", [])
    )
    artifacts = manifest.get("artifacts", {})
    return {
        "status": "checked",
        "window": {
            "start_ns": start_ns,
            "start_utc": iso_ns(start_ns),
            "end_ns_exclusive": end_ns,
            "end_utc_exclusive": iso_ns(end_ns),
        },
        "instrument_ids_in_comparison": sorted(minute_instruments),
        "derived_from_mbp1": {
            key: value.get("rows") for key, value in artifacts.items()
        },
        "native_one_minute_fields_equal": minute_fields_equal,
        "native_one_minute_fields_compared": minute_fields_compared,
        "native_one_second_fields_equal": second.get("equal_fields"),
        "native_one_second_fields_unresolved_equal_timestamp_order": len(
            second.get("unresolved_fields", [])
        ),
        "native_one_second_field_mismatches": len(second.get("mismatches", [])),
        "native_one_second_mismatch_fields": dict(sorted(mismatch_fields.items())),
        "one_second_caveat": (
            "The acquired MBP-1 schema lacks ts_recv and sequence. Event-time 1s "
            "bars are valid derived views, but native vendor 1s bins cannot be promised "
            "bit-identical; the supplied comparison retains mismatches and unresolved "
            "equal-timestamp O/C order explicitly."
        ),
        "artifact_paths": {
            "manifest": str(manifest_path),
            "native_one_minute_comparison": str(minute_path),
            "native_one_second_comparison": str(second_path),
        },
        "artifact_sha256": {
            "manifest": sha256_path(manifest_path),
            "native_one_minute_comparison": sha256_path(minute_path),
            "native_one_second_comparison": sha256_path(second_path),
        },
    }


def inspect_completed_recoveries(
    minute_manifest_path: Path | None, tail_manifest_path: Path | None
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if minute_manifest_path is None:
        result["missing_native_minutes_from_native_1s"] = {
            "status": "not_checked",
            "reason": "--minute-recovery-manifest not supplied",
        }
    elif not minute_manifest_path.is_file():
        result["missing_native_minutes_from_native_1s"] = {
            "status": "not_checked",
            "missing_artifact": str(minute_manifest_path),
        }
    else:
        recovered = json.loads(minute_manifest_path.read_text())
        result["missing_native_minutes_from_native_1s"] = {
            "status": "checked",
            "manifest_path": str(minute_manifest_path),
            "manifest_sha256": sha256_path(minute_manifest_path),
            "requested_keys": recovered.get("requested_keys"),
            "recovered_keys": recovered.get("recovered_keys"),
            "unresolved_keys": recovered.get("unresolved_keys"),
            "already_present_keys": recovered.get("already_present_keys"),
            "raw_source_signatures_unchanged": recovered.get(
                "raw_source_signatures_unchanged"
            ),
            "artifact": recovered.get("artifact"),
        }
    if tail_manifest_path is None:
        result["mbp1_event_time_minute_tail"] = {
            "status": "not_checked",
            "reason": "--tail-recovery-manifest not supplied",
        }
    elif not tail_manifest_path.is_file():
        result["mbp1_event_time_minute_tail"] = {
            "status": "not_checked",
            "missing_artifact": str(tail_manifest_path),
        }
    else:
        recovered = json.loads(tail_manifest_path.read_text())
        plan = recovered.get("plan", {})
        result["mbp1_event_time_minute_tail"] = {
            "status": "checked",
            "manifest_path": str(tail_manifest_path),
            "manifest_sha256": sha256_path(tail_manifest_path),
            "requested_start_ns": plan.get("start_ns"),
            "requested_start_utc": iso_ns(plan.get("start_ns")),
            "requested_end_ns_exclusive": plan.get("end_ns"),
            "requested_end_utc_exclusive": iso_ns(plan.get("end_ns")),
            "raw_source_signatures_unchanged": recovered.get(
                "raw_source_signatures_unchanged"
            ),
            "artifact": recovered.get("artifacts", {}).get("ohlcv-1m"),
            "timing_caveat": recovered.get("conventions", {}).get(
                "bar_timestamp_basis"
            ),
        }
    return result


def format_recovery_evidence(
    datasets: dict[str, dict[str, Any]],
    minute_discrepancies: dict[str, Any],
    *,
    comparison_dir: Path | None,
    minute_recovery_manifest: Path | None,
    tail_recovery_manifest: Path | None,
) -> dict[str, Any]:
    monthly = sorted(
        (
            row
            for row in datasets["nq_mbp1"]["files"]
            if row["partition_kind"] == "monthly"
            and row["rows"] > 0
            and row["observed_min_ns"] is not None
        ),
        key=lambda row: (row["observed_min_ns"], row["path"]),
    )
    if not monthly:
        raise ValueError("NQ MBP-1 has no valid observed monthly partition")
    first_edge = mbp_trade_action_edge(Path(monthly[0]["path"]), reverse=False)
    last_edge = mbp_trade_action_edge(Path(monthly[-1]["path"]), reverse=True)
    trades = datasets["nq_trades"]
    one_minute = datasets["nq_ohlcv_1m"]
    one_second = datasets["nq_ohlcv_1s"]
    comparison = inspect_native_comparison(comparison_dir)
    completed_recoveries = inspect_completed_recoveries(
        minute_recovery_manifest, tail_recovery_manifest
    )
    trade_windows: list[dict[str, Any]] = []
    if first_edge["first_trade_t_ns"] < trades["observed_first_t_ns"]:
        trade_windows.append(
            {
                "start_ns": first_edge["first_trade_t_ns"],
                "start_utc": first_edge["first_trade_t_utc"],
                "end_ns_exclusive": trades["observed_first_t_ns"],
                "end_utc_exclusive": trades["observed_first_t_utc"],
                "kind": "standalone_trades_missing_head",
                "coverage_statement": (
                    "MBP-1 T actions and row-group session endpoints exist in this "
                    "range; continuity was not scanned."
                ),
            }
        )
    if last_edge["last_trade_t_ns"] > trades["observed_last_t_ns"]:
        trade_windows.append(
            {
                "start_ns": trades["observed_last_t_ns"] + 1,
                "start_utc": iso_ns(trades["observed_last_t_ns"] + 1),
                "end_ns_inclusive": last_edge["last_trade_t_ns"],
                "end_utc_inclusive": last_edge["last_trade_t_utc"],
                "kind": "standalone_trades_missing_tail",
                "coverage_statement": "A later MBP-1 T action is directly observed.",
            }
        )
    minute_through = one_minute["observed_last_t_ns"] + MINUTE_NS
    second_through = one_second["observed_last_t_ns"] + NS
    return {
        "mbp1_trade_action_edge_evidence": {
            "earliest_file_first_trade_group": first_edge,
            "latest_file_last_trade_group": last_edge,
            "scope_limitation": (
                "Only the boundary groups were scanned. These prove trade-action "
                "presence at the archive edges, not continuous trade coverage."
            ),
        },
        "standalone_trades_absent_but_mbp1_trade_actions_observed": trade_windows,
        "standalone_one_minute_holes_with_lower_level_coverage": minute_discrepancies[
            "complete_globex_sessions"
        ],
        "standalone_bar_common_tail": {
            "one_minute_last_bar_start_utc": one_minute["observed_last_t_utc"],
            "one_minute_observed_through_utc": iso_ns(minute_through),
            "one_second_last_bar_start_utc": one_second["observed_last_t_utc"],
            "one_second_observed_through_utc": iso_ns(second_through),
            "mbp1_last_event_utc": datasets["nq_mbp1"]["observed_last_t_utc"],
            "statement": (
                f"The 1m and 1s exclusive observed endpoints are {iso_ns(minute_through)} "
                f"and {iso_ns(second_through)}. The last MBP-1 event is "
                f"{datasets['nq_mbp1']['observed_last_t_utc']}."
            ),
        },
        "bounded_native_comparison": comparison,
        "completed_recoveries": completed_recoveries,
        "derivability_limit": (
            "MBP-1 supports top-of-book state and T-action executions only. It cannot "
            "recreate deeper book levels, order identities, exchange sequence, or "
            "missing ts_recv. Derived files are new views; retained acquired files "
            "remain unchanged raw sources."
        ),
    }


def other_major_gaps(data_root: Path, audit_month_end: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    rty_listing_context = {
        "first_trade_date": "2017-07-10",
        "source": "https://www.cmegroup.com/media-room/press-releases/2017/7/11/cme_group_announcesfirsttradesafterthereturnoftherussell2000inde.html",
        "interpretation": (
            "The retained CME RTY series began with the July 10, 2017 trade date. "
            "Empty 2010-2016 partitions precede this listing and are not lost RTY "
            "sessions. Definition coverage for the listed 2017-2018 period is a "
            "separate acquisition gap when those years are absent."
        ),
    }
    catalog_path = data_root / "manifests/dataset-catalog.json"
    catalog_by_id: dict[str, dict[str, Any]] = {}
    if catalog_path.is_file():
        catalog = json.loads(catalog_path.read_text())
        catalog_by_id = {
            row["dataset_id"]: row for row in catalog.get("datasets", [])
            if row.get("dataset_id")
        }
    for suffix in ("ohlcv-1m", "statistics"):
        directory = data_root / f"quantpad/cme__rty-continuous-futures__{suffix}"
        if not directory.is_dir():
            continue
        empty = []
        for path in sorted(directory.glob("*.parquet")):
            if pq.ParquetFile(path).metadata.num_rows == 0:
                empty.append(path.name)
        result.append(
            {
                "dataset_id": f"quantpad/cme__rty-continuous-futures__{suffix}",
                "issue": "nominal files with zero rows" if empty else "none",
                "empty_partitions": empty,
                "evidence": "Parquet metadata num_rows == 0",
                "listing_context": rty_listing_context,
            }
        )

    es_dir = data_root / "quantpad/cme__es-continuous-futures__mbp-1"
    present = {path.stem for path in es_dir.glob("*.parquet") if MONTH_RE.match(path.name)}
    es_id = "quantpad/cme__es-continuous-futures__mbp-1"
    if present:
        catalog_row = catalog_by_id.get(es_id, {})
        expected_start = catalog_row.get("expected_start") or min(present)
        if not MONTH_RE.match(f"{expected_start}.parquet"):
            expected_start = min(present)
        expected = expected_labels("monthly", expected_start, audit_month_end)
        missing = sorted(set(expected) - present)
        result.append(
            {
                "dataset_id": es_id,
                "issue": catalog_row.get("status", "physical coverage gaps"),
                "present_months": sorted(present),
                "present_month_ranges": coalesce_month_labels(present),
                "missing_months_through_audit_endpoint": missing,
                "missing_month_ranges": coalesce_month_labels(missing),
                "audit_endpoint": audit_month_end,
                "catalog_known_gaps": catalog_row.get("known_gaps", []),
                "evidence": "physical monthly filenames plus supplied-root dataset catalog",
            }
        )
    definition_id = "quantpad/cme__rty-continuous-futures__definition"
    definition_dir = data_root / definition_id
    if definition_dir.is_dir():
        catalog_row = catalog_by_id.get(definition_id, {})
        result.append(
            {
                "dataset_id": definition_id,
                "issue": catalog_row.get("status", "physical coverage only"),
                "physical_year_labels": sorted(
                    path.stem for path in definition_dir.glob("*.parquet")
                ),
                "catalog_known_gaps": catalog_row.get("known_gaps", []),
                "evidence": "physical filenames and supplied-root dataset catalog",
                "listing_context": rty_listing_context,
            }
        )
    return result


def _json_ready_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in dataset.items() if key != "_row_groups"}


def _write_row_group_artifact(
    path: Path, datasets: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    intervals = []
    for key in ("nq_mbp1", "nq_trades", "nq_ohlcv_1s", "nq_ohlcv_1m"):
        intervals.extend(datasets[key]["_row_groups"])
    payload = {
        "schema": {
            "observed_min_ns": "inclusive Parquet footer t minimum converted to ns",
            "observed_max_ns": "inclusive Parquet footer t maximum converted to ns",
            "envelope_end_exclusive_ns": (
                "observed maximum plus one native timestamp unit; an envelope, not continuity"
            ),
            "physical_partition_kind": "annual, monthly, or weekly filename shape",
        },
        "interval_count": len(intervals),
        "intervals": intervals,
    }
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    return {
        "path": str(path),
        "interval_count": len(intervals),
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
    }


def _write_missing_key_artifact(
    path: Path, discrepancy: dict[str, Any]
) -> dict[str, Any]:
    missing_keys = discrepancy.pop("_missing_keys")
    payload = {
        "schema": {
            "minute_start_ns": "UTC epoch nanoseconds at the minute boundary",
            "minute_start_utc": "same value rendered as exact UTC text",
            "instrument_id": "native acquired continuous-contract instrument_id",
        },
        "evidence": (
            "exact streamed set difference of native OHLCV-1s occupied minute/instrument "
            "keys against native OHLCV-1m keys"
        ),
        "missing_key_count": len(missing_keys),
        "missing_keys": [
            {
                "minute_start_ns": start,
                "minute_start_utc": iso_ns(start),
                "instrument_id": instrument_id,
            }
            for start, instrument_id in missing_keys
        ],
    }
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    return {
        "path": str(path),
        "missing_key_count": len(missing_keys),
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
    }


def supported_mbp1_gap_conclusion(
    mbp: dict[str, Any],
    ownership: dict[str, Any],
    sessions: dict[str, Any],
    envelope: dict[str, Any],
) -> str:
    """Describe only the gap evidence present in the computed audit payload."""

    statements: list[str] = []
    monthly = ownership["monthly_track"]
    if monthly.get("status") == "absent" or monthly.get("file_count", 0) == 0:
        statements.append(
            "The monthly MBP-1 track is absent, so nominal monthly coverage cannot be assessed."
        )
    else:
        missing_labels = monthly.get("missing_between_physical_endpoints")
        if missing_labels:
            statements.append(
                "Missing nominal NQ MBP-1 month labels between the physical endpoints: "
                + ", ".join(missing_labels)
                + "."
            )
        elif missing_labels == []:
            statements.append(
                "No nominal NQ MBP-1 month label is missing between the physical endpoints."
            )
        else:
            statements.append("Nominal monthly label continuity was not assessed.")

    empty_files = mbp.get("empty_files", [])
    if empty_files:
        statements.append(
            f"{len(empty_files)} MBP-1 file(s) are empty: "
            + ", ".join(empty_files)
            + "."
        )
    else:
        statements.append("No empty MBP-1 file was found.")

    missing_stats = int(mbp.get("row_groups_missing_t_statistics", 0))
    if missing_stats:
        statements.append(
            f"{missing_stats} MBP-1 row group(s) lack `t` statistics, so their bounds are unverified."
        )
    else:
        statements.append("No MBP-1 row group with missing `t` statistics was found.")

    missing_endpoint_evidence = sessions.get(
        "one_minute_sessions_without_mbp1_row_group_endpoint", []
    )
    within_count = int(
        sessions.get("nq_1m_session_count_within_mbp1_endpoint_bounds", 0)
    )
    if missing_endpoint_evidence:
        statements.append(
            f"{len(missing_endpoint_evidence)} of {within_count} 1m-observed session(s) "
            "within the MBP-1 endpoint bounds lack an MBP-1 row-group endpoint. "
            "Endpoint absence is weak evidence and these sessions remain unverified; "
            "they are not declared missing."
        )
    elif within_count:
        statements.append(
            f"All {within_count} 1m-observed session(s) within the MBP-1 endpoint "
            "bounds have MBP-1 row-group endpoint evidence."
        )
    else:
        statements.append(
            "No 1m-observed session fell within usable MBP-1 endpoint bounds."
        )

    envelope_groups = int(envelope.get("monthly_primary_row_group_count", 0))
    envelope_hits = envelope.get("gaps_containing_a_complete_existing_1m_bar", [])
    if not envelope_groups:
        statements.append(
            "No monthly-primary row-group envelopes were available for the envelope-gap check."
        )
    elif envelope_hits:
        statements.append(
            f"{len(envelope_hits)} gap(s) between monthly-primary row-group envelopes "
            "contain at least one complete existing 1m bar."
        )
    else:
        statements.append(
            "No gap between monthly-primary row-group envelopes containing a complete "
            "existing 1m bar was found."
        )

    statements.append(
        "Event-level internal continuity was not checked, so this is not proof of a gap-free tape."
    )
    return " ".join(statements)


def mbp_nominal_inventory_text(
    mbp: dict[str, Any], ownership: dict[str, Any]
) -> str:
    """Render physical-track findings without assuming a complete inventory."""

    parts: list[str] = []
    for kind in ("monthly", "weekly"):
        track = ownership[f"{kind}_track"]
        if track.get("status") == "absent" or track.get("file_count", 0) == 0:
            parts.append(f"The {kind} physical track is absent.")
            continue
        part = (
            f"The {kind} physical track has {track['file_count']} files "
            f"({track['first_label']} through {track['last_label']})"
        )
        missing = track.get("missing_between_physical_endpoints")
        if missing:
            part += "; missing labels between those endpoints: " + ", ".join(missing)
        elif missing == []:
            part += "; no label is missing between those endpoints"
        else:
            part += "; label continuity was not assessed"
        empty = track.get("empty_files", [])
        part += (
            "; empty files: " + ", ".join(empty)
            if empty
            else "; no file is empty"
        )
        parts.append(part + ".")
    missing_stats = int(mbp.get("row_groups_missing_t_statistics", 0))
    parts.append(
        f"{missing_stats} MBP-1 row group(s) lack `t` statistics."
        if missing_stats
        else "Every MBP-1 row group has `t` statistics."
    )
    return " ".join(parts)


def nominal_dataset_inventory_text(label: str, dataset: dict[str, Any]) -> str:
    nominal = dataset.get("nominal_partitions")
    if not nominal:
        return f"{label} has no assessable physical nominal partition track."
    text = (
        f"{label} has {nominal['present']} {nominal['kind']} labels from "
        f"{nominal['first_label']} through {nominal['last_label']}"
    )
    missing = nominal.get("missing_between_physical_endpoints")
    if missing:
        text += "; missing labels between those endpoints: " + ", ".join(missing)
    elif missing == []:
        text += "; no label is missing between those endpoints"
    else:
        text += "; label continuity was not assessed"
    empty_count = int(dataset.get("empty_file_count", 0))
    missing_stats = int(dataset.get("row_groups_missing_t_statistics", 0))
    text += f"; {empty_count} empty file(s); {missing_stats} row group(s) missing `t` statistics."
    return text


def build_audit(
    data_root: Path,
    row_group_path: Path,
    missing_key_path: Path,
    *,
    comparison_dir: Path | None = None,
    minute_recovery_manifest: Path | None = None,
    tail_recovery_manifest: Path | None = None,
    reuse_missing_key_artifact: Path | None = None,
    reproduce_command: str | None = None,
) -> dict[str, Any]:
    reject_outputs_within_data_root(
        data_root, (row_group_path, missing_key_path)
    )
    datasets = {spec.key: inspect_dataset(data_root, spec) for spec in NQ_SPECS}
    ownership = audit_mbp_ownership(datasets["nq_mbp1"])
    if ownership["monthly_track"]["status"] == "absent":
        raise ValueError(
            "cannot build acquired-window audit: NQ MBP-1 monthly track is absent"
        )
    datasets["nq_mbp1"]["nominal_partition_tracks"] = {
        "monthly": ownership["monthly_track"],
        "weekly": ownership["weekly_track"],
    }
    minute_starts, minute_start_set, minute_key_set = load_one_minute_keys(data_root)
    if reuse_missing_key_artifact is None:
        minute_discrepancies = compare_one_second_to_minute(
            data_root, minute_start_set, minute_key_set
        )
    else:
        minute_discrepancies = summarize_missing_minute_keys(
            load_missing_minute_keys(reuse_missing_key_artifact),
            minute_start_set,
            evidence_level=(
                "reused exact streamed comparison artifact: "
                f"{reuse_missing_key_artifact} sha256={sha256_path(reuse_missing_key_artifact)}"
            ),
        )
    sessions = compare_session_presence(datasets, minute_starts, minute_discrepancies)
    envelope_check = compare_mbp_envelope_gaps_to_minutes(datasets, minute_starts)
    mbp_gap_conclusion = supported_mbp1_gap_conclusion(
        datasets["nq_mbp1"], ownership, sessions, envelope_check
    )
    recovery = format_recovery_evidence(
        datasets,
        minute_discrepancies,
        comparison_dir=comparison_dir,
        minute_recovery_manifest=minute_recovery_manifest,
        tail_recovery_manifest=tail_recovery_manifest,
    )
    row_groups = _write_row_group_artifact(row_group_path, datasets)
    missing_keys = _write_missing_key_artifact(
        missing_key_path, minute_discrepancies
    )
    minute_discrepancies["missing_key_artifact"] = missing_keys
    manifest_path = data_root / "manifests/dataset-catalog.json"
    source_manifest = (
        {"path": str(manifest_path), "sha256": sha256_path(manifest_path)}
        if manifest_path.is_file()
        else {"path": str(manifest_path), "status": "absent"}
    )
    return {
        "audit_version": "acquired-window-audit-v1",
        "data_root": str(data_root),
        "method": {
            "observed_bounds": "all Parquet t min/max row-group statistics",
            "nominal_partitions": "physical filenames, independently of row count",
            "row_group_intervals": row_groups,
            "missing_one_minute_keys": missing_keys,
            "large_payload_policy": (
                "No whole MBP-1 file was scanned. Only weekly-exclusive boundary "
                "row groups and first/last trade-action boundary groups were read."
            ),
            "continuity_claim": "none unless a specific comparison below says otherwise",
            "reproduce": (
                reproduce_command
                or f"python implementation/tools/audit_acquired_windows.py --data-root {data_root}"
            ),
        },
        "source_manifest": source_manifest,
        "nq": {
            "datasets": {
                key: _json_ready_dataset(value) for key, value in datasets.items()
            },
            "mbp1_ownership": ownership,
            "one_second_vs_one_minute": minute_discrepancies,
            "session_presence": sessions,
            "mbp1_row_group_envelope_check": envelope_check,
            "format_recovery": recovery,
            "supported_mbp1_missing_window_conclusion": mbp_gap_conclusion,
        },
        "other_major_acquired_gaps": other_major_gaps(
            data_root, ownership["monthly_track"]["last_label"]
        ),
        "evidence_levels": {
            "observed": "direct footer statistic or targeted source-column read",
            "declared": "dataset manifest/catalog statement",
            "inferred": "cross-format comparison with stated clock and limits",
            "unchecked": "inside-row-group event continuity and full duplicate equality",
        },
    }


def markdown_report(audit: dict[str, Any]) -> str:
    nq = audit["nq"]
    datasets = nq["datasets"]
    ownership = nq["mbp1_ownership"]
    discrepancy = nq["one_second_vs_one_minute"]
    sessions = nq["session_presence"]
    envelope = nq["mbp1_row_group_envelope_check"]
    recovery = nq["format_recovery"]
    comparison = recovery["bounded_native_comparison"]
    comparison_lines: list[str] = []
    if comparison.get("status") == "checked":
        rows = comparison["derived_from_mbp1"]
        mismatch_fields = ", ".join(
            f"{count} {field}" for field, count in comparison["native_one_second_mismatch_fields"].items()
        ) or "none"
        comparison_lines.extend(
            [
                "The supplied bounded comparison covers "
                f"`{comparison['window']['start_utc']}` through "
                f"`{comparison['window']['end_utc_exclusive']}` (exclusive). It produced "
                f"{rows.get('trades', 0):,} trades, {rows.get('bbo', 0):,} top-of-book "
                f"observations, {rows.get('ohlcv-1s', 0):,} one-second bars, and "
                f"{rows.get('ohlcv-1m', 0):,} one-minute bars. "
                f"{comparison['native_one_minute_fields_equal']:,} of "
                f"{comparison['native_one_minute_fields_compared']:,} minute OHLCV fields "
                "equal the native minute bars.",
                "For native 1s, the supplied comparison records "
                f"{comparison['native_one_second_fields_equal']:,} equal fields, "
                f"{comparison['native_one_second_fields_unresolved_equal_timestamp_order']:,} "
                "unresolved equal-timestamp O/C fields, and "
                f"{comparison['native_one_second_field_mismatches']:,} mismatches "
                f"({mismatch_fields}). {comparison['one_second_caveat']}",
            ]
        )
    else:
        comparison_lines.append(
            "No bounded native comparison was supplied; comparison status is `not_checked`."
        )
    completed = recovery["completed_recoveries"]
    minute_recovery = completed["missing_native_minutes_from_native_1s"]
    tail_recovery = completed["mbp1_event_time_minute_tail"]
    recovery_lines: list[str] = []
    if minute_recovery.get("status") == "checked":
        recovery_lines.append(
            f"The supplied minute-recovery manifest records {minute_recovery['recovered_keys']:,} "
            f"of {minute_recovery['requested_keys']:,} requested keys recovered, "
            f"{len(minute_recovery['unresolved_keys']):,} unresolved, and "
            f"{minute_recovery['already_present_keys']:,} existing keys encountered. "
            "The recovered JSONL SHA-256 is "
            f"`{minute_recovery['artifact']['sha256']}`; raw source signatures unchanged="
            f"{str(minute_recovery['raw_source_signatures_unchanged']).lower()}."
        )
    else:
        recovery_lines.append(
            "No minute-recovery manifest was supplied; recovery status is `not_checked`."
        )
    if tail_recovery.get("status") == "checked":
        recovery_lines.append(
            "The supplied MBP-1 event-time tail manifest covers "
            f"`{tail_recovery['requested_start_utc']}` through "
            f"`{tail_recovery['requested_end_utc_exclusive']}` (exclusive), with "
            f"{tail_recovery['artifact']['rows']:,} non-empty minute bars and SHA-256 "
            f"`{tail_recovery['artifact']['sha256']}`; raw source signatures unchanged="
            f"{str(tail_recovery['raw_source_signatures_unchanged']).lower()}."
        )
    else:
        recovery_lines.append(
            "No MBP-1 tail-recovery manifest was supplied; recovery status is `not_checked`."
        )
    other_gap_lines: list[str] = []
    for item in audit["other_major_acquired_gaps"]:
        dataset_id = item["dataset_id"]
        if item.get("empty_partitions"):
            other_gap_lines.append(
                f"- `{dataset_id}`: zero-row partitions "
                + ", ".join(f"`{name}`" for name in item["empty_partitions"])
                + "."
            )
        elif item.get("missing_month_ranges") is not None:
            ranges = ", ".join(item["missing_month_ranges"]) or "none"
            other_gap_lines.append(
                f"- `{dataset_id}` ({item['issue']}): missing month ranges through "
                f"{item['audit_endpoint']}: {ranges}."
            )
        else:
            notes = "; ".join(item.get("catalog_known_gaps", [])) or "no catalog note"
            labels = ", ".join(item.get("physical_year_labels", [])) or "none"
            other_gap_lines.append(
                f"- `{dataset_id}` ({item['issue']}): physical year labels {labels}; {notes}"
            )
    if any(item.get("listing_context") for item in audit["other_major_acquired_gaps"]):
        other_gap_lines.extend([
            "",
            "CME's [launch announcement](https://www.cmegroup.com/media-room/press-releases/2017/7/11/cme_group_announcesfirsttradesafterthereturnoftherussell2000inde.html) "
            "places the RTY launch at the July 10, 2017 trade date. Empty "
            "2010-2016 RTY files therefore precede this listing; they are not lost "
            "RTY sessions. Any missing RTY definition files from 2017 onward "
            "are a separate acquisition limitation.",
        ])
    trade_window_lines: list[str] = []
    for item in recovery["standalone_trades_absent_but_mbp1_trade_actions_observed"]:
        if item["kind"] == "standalone_trades_missing_head":
            trade_window_lines.append(
                "Standalone trades have no rows from the observed MBP-1 trade-action "
                f"edge `{item['start_utc']}` to `{item['end_utc_exclusive']}` "
                f"(exclusive). {item['coverage_statement']}"
            )
        else:
            trade_window_lines.append(
                "A later MBP-1 trade action is observed from after the standalone trade "
                f"endpoint through `{item['end_utc_inclusive']}` (inclusive). "
                f"{item['coverage_statement']}"
            )
    if not trade_window_lines:
        trade_window_lines.append(
            "No standalone-trade head or tail extension was proven from MBP-1 boundary groups."
        )
    isolated_dates = [value[:10] for value in discrepancy["isolated_minutes"]]
    isolated_range = (
        f"{min(isolated_dates)} through {max(isolated_dates)}"
        if isolated_dates
        else "none"
    )
    incomplete_bounds = [
        label
        for key, label in (
            ("nq_mbp1", "MBP-1"),
            ("nq_trades", "trades"),
            ("nq_ohlcv_1s", "OHLCV-1s"),
            ("nq_ohlcv_1m", "OHLCV-1m"),
        )
        if datasets[key].get("observed_first_t_ns") is None
        or datasets[key].get("observed_last_t_ns") is None
        or datasets[key].get("row_groups_missing_t_statistics", 0)
    ]
    bounds_statement = (
        "All four bounds are the exact extrema of every row-group `t` statistic."
        if not incomplete_bounds
        else (
            "The displayed bounds use available row-group `t` statistics; complete "
            "extrema are unverified for: " + ", ".join(incomplete_bounds) + "."
        )
    )
    ownership_inventory = mbp_nominal_inventory_text(
        datasets["nq_mbp1"], ownership
    )
    if ownership["monthly_track"].get("status") == "absent":
        ownership_scan = (
            "Monthly-primary ownership could not be evaluated because the monthly track is absent."
        )
    elif ownership["weekly_track"].get("status") == "absent":
        ownership_scan = (
            "No weekly physical track is present, so weekly fallback contribution was not evaluated."
        )
    else:
        weekly_rows = ownership["weekly_rows_observed_outside_monthly_envelopes"]
        ownership_scan = (
            "Monthly files have precedence. Subtracting the monthly observed envelopes "
            f"from the weekly envelopes produces {ownership['weekly_exclusive_envelope_candidate_count']} "
            "candidate spans. Targeted `t` scans read the intersecting boundary groups and "
            f"find **{weekly_rows} rows** across those spans. "
            + (
                "The scans found no weekly rows outside the monthly envelopes. "
                if weekly_rows == 0
                else "Weekly files therefore contribute rows outside the monthly envelopes. "
            )
            + "Equality of every overlapping weekly/monthly row was not scanned."
        )
    remaining_inventory = " ".join(
        [
            nominal_dataset_inventory_text("Trades", datasets["nq_trades"]),
            nominal_dataset_inventory_text("OHLCV-1s", datasets["nq_ohlcv_1s"]),
            nominal_dataset_inventory_text("OHLCV-1m", datasets["nq_ohlcv_1m"]),
        ]
    )
    missing_mbp_endpoints = sessions.get(
        "one_minute_sessions_without_mbp1_row_group_endpoint", []
    )
    within_mbp_count = sessions.get(
        "nq_1m_session_count_within_mbp1_endpoint_bounds", 0
    )
    if missing_mbp_endpoints:
        session_statement = (
            f"Of the {within_mbp_count:,} 1m-observed sessions within MBP-1's endpoint "
            f"bounds, {len(missing_mbp_endpoints):,} lack a row-group endpoint in the "
            "session. Endpoint absence does not prove missing rows; those sessions remain unverified."
        )
    elif within_mbp_count:
        session_statement = (
            f"All {within_mbp_count:,} 1m-observed sessions within MBP-1's endpoint "
            "bounds have at least one actual MBP-1 row-group endpoint in the session."
        )
    else:
        session_statement = (
            "No 1m-observed session fell within usable MBP-1 endpoint bounds."
        )
    if envelope.get("monthly_primary_row_group_count", 0):
        envelope_statement = (
            "After merging monthly-primary row-group envelopes, "
            f"{len(envelope['gaps_containing_a_complete_existing_1m_bar'])} gaps contain "
            "a complete standalone 1m bar."
        )
    else:
        envelope_statement = (
            "No monthly-primary row-group envelopes were available for the gap check."
        )
    last_month_label = ownership["monthly_track"].get("last_label")
    last_partition_statement = (
        "The last physical MBP-1 monthly label is "
        f"`{last_month_label}` and the last observed event is "
        f"`{datasets['nq_mbp1']['observed_last_t_utc']}`."
        if last_month_label
        else "No physical MBP-1 monthly label is available."
    )
    lines = [
        "# Acquired futures coverage audit",
        "",
        "This report separates observed timestamps, declared partition scope, and "
        "continuity checks. A file min/max and a row-group min/max are envelopes; they "
        "do not prove that every timestamp or market event inside the envelope exists.",
        "",
        "Reproduce from the repository root:",
        "",
        "```bash",
        audit["method"]["reproduce"],
        "```",
        "",
        "## NQ observed bounds",
        "",
        "| format | files | rows | row groups | empty files | missing `t` stats | first observed `t` UTC | last observed `t` UTC |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for key, label in (
        ("nq_mbp1", "MBP-1"),
        ("nq_trades", "trades"),
        ("nq_ohlcv_1s", "OHLCV-1s"),
        ("nq_ohlcv_1m", "OHLCV-1m"),
    ):
        row = datasets[key]
        lines.append(
            f"| {label} | {row['file_count']:,} | {row['total_rows']:,} | "
            f"{row['row_group_count']:,} | {row['empty_file_count']:,} | "
            f"{row['row_groups_missing_t_statistics']:,} | "
            f"{row['observed_first_t_utc']} | {row['observed_last_t_utc']} |"
        )
    lines.extend(
        [
            "",
            bounds_statement + " "
            "The bar timestamps are bar starts. OHLCV-1m's exclusive observed endpoint is "
            f"{recovery['standalone_bar_common_tail']['one_minute_observed_through_utc']}; "
            "OHLCV-1s's is "
            f"{recovery['standalone_bar_common_tail']['one_second_observed_through_utc']}. "
            "MBP-1's last observed event is "
            f"{datasets['nq_mbp1']['observed_last_t_utc']}.",
            "",
            "The companion row-group artifact contains "
            f"{audit['method']['row_group_intervals']['interval_count']:,} exact footer "
            "interval records and its SHA-256 is "
            f"`{audit['method']['row_group_intervals']['sha256']}`.",
            "",
            "## Nominal partitions and MBP-1 ownership",
            "",
            ownership_inventory,
            "",
            ownership_scan,
            "",
            remaining_inventory + " The first standalone trade event is "
            f"`{datasets['nq_trades']['observed_first_t_utc']}`.",
            "",
            "## Actually incomplete NQ standalone windows",
            "",
            f"An exact streamed comparison finds {discrepancy['minute_buckets_present_in_1s_absent_in_1m']:,} "
            "minute buckets present in OHLCV-1s but absent from OHLCV-1m. "
            f"{len(discrepancy['complete_globex_sessions'])} are complete 18:00–17:00 ET "
            "Globex sessions:",
            "",
        ]
    )
    for item in discrepancy["complete_globex_sessions"]:
        lines.append(
            f"- {item['trade_date_et']}: `{item['start_utc']}` to "
            f"`{item['end_utc_exclusive']}` (exclusive), "
            f"{item['minute_buckets_present_in_1s_absent_in_1m']:,} 1s-occupied minutes; "
            f"MBP-1 endpoint evidence={str(item['mbp1_endpoint_evidence']).lower()}, "
            "standalone-trade endpoint evidence="
            f"{str(item['standalone_trade_endpoint_evidence']).lower()}."
        )
    lines.extend(
        [
            "",
            f"The other {discrepancy['isolated_minute_count']} discrepancies are isolated "
            f"minute starts ({isolated_range}). Many may reflect closure context; the JSON "
            "lists every timestamp so they remain visible rather than being silently called "
            "market gaps.",
            "",
            *trade_window_lines,
            "",
            *comparison_lines,
            "",
            *recovery_lines,
            "",
            "## What the evidence supports about MBP-1 gaps",
            "",
            f"The exact 1m session set contains {sessions['nq_1m_exact_session_count']:,} "
            f"Globex trade dates. {session_statement} {envelope_statement}",
            "",
            nq["supported_mbp1_missing_window_conclusion"],
            "",
            last_partition_statement + " The audit does not invent a "
            "missing interval after that observed bound. Market closures and contract rolls "
            "are not inferred from elapsed UTC time alone.",
            "",
            "## Other major acquired gaps",
            "",
            *other_gap_lines,
            "",
            "Reference/superseded option datasets are outside this compact futures-window "
            "overview. MBP-1 supports depth-one state and trade actions; this audit does not "
            "claim that deeper book or order-level formats can be reconstructed.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("/workspace/data"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "/workspace/implementation/reports/phase1-live/coverage-audit"
        ),
    )
    parser.add_argument(
        "--comparison-dir",
        type=Path,
        help="directory containing manifest.json and native bar comparisons",
    )
    parser.add_argument("--minute-recovery-manifest", type=Path)
    parser.add_argument("--tail-recovery-manifest", type=Path)
    parser.add_argument(
        "--reuse-missing-key-artifact",
        type=Path,
        help="reuse a prior exact missing-one-minute-keys.json instead of rescanning 1s",
    )
    return parser.parse_args()


def reproduce_command(args: argparse.Namespace) -> str:
    values = [
        "python implementation/tools/audit_acquired_windows.py",
        f"--data-root {args.data_root}",
        f"--output-dir {args.output_dir}",
    ]
    for flag, value in (
        ("--comparison-dir", args.comparison_dir),
        ("--minute-recovery-manifest", args.minute_recovery_manifest),
        ("--tail-recovery-manifest", args.tail_recovery_manifest),
    ):
        if value is not None:
            values.append(f"{flag} {value}")
    separator = " " + "\\" + "\n  "
    return separator.join(values)


def main() -> int:
    args = parse_args()
    row_group_path = args.output_dir / "row-group-intervals.json"
    missing_key_path = args.output_dir / "missing-one-minute-keys.json"
    json_path = args.output_dir / "coverage-audit.json"
    markdown_path = args.output_dir / "README.md"
    reject_outputs_within_data_root(
        args.data_root,
        (
            args.output_dir,
            row_group_path,
            missing_key_path,
            json_path,
            markdown_path,
        ),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    audit = build_audit(
        args.data_root,
        row_group_path,
        missing_key_path,
        comparison_dir=args.comparison_dir,
        minute_recovery_manifest=args.minute_recovery_manifest,
        tail_recovery_manifest=args.tail_recovery_manifest,
        reuse_missing_key_artifact=args.reuse_missing_key_artifact,
        reproduce_command=reproduce_command(args),
    )
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    markdown_path.write_text(markdown_report(audit))
    print(f"coverage_json={json_path}")
    print(f"coverage_markdown={markdown_path}")
    print(f"row_group_intervals={row_group_path}")
    print(f"missing_one_minute_keys={missing_key_path}")
    print(
        "nq_mbp1 | "
        f"files={audit['nq']['datasets']['nq_mbp1']['file_count']} | "
        f"rows={audit['nq']['datasets']['nq_mbp1']['total_rows']} | "
        f"first={audit['nq']['datasets']['nq_mbp1']['observed_first_t_utc']} | "
        f"last={audit['nq']['datasets']['nq_mbp1']['observed_last_t_utc']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
