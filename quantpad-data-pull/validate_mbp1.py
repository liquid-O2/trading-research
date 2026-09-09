#!/usr/bin/env python3
"""Validate monthly QuantPad MBP-1 Parquet partitions without loading them whole."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pyarrow.compute as pc
import pyarrow.parquet as pq


MONTH_FILE = re.compile(r"^(\d{4})-(\d{2})\.parquet$")
SIZE_COLUMNS = ("size", "bid_sz", "ask_sz")
PRICE_COLUMNS = ("price", "bid_px", "ask_px")


def month_after(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def month_names(start: str, end: str) -> list[str]:
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    names: list[str] = []
    year, month = sy, sm
    while (year, month) <= (ey, em):
        names.append(f"{year:04d}-{month:02d}.parquet")
        year, month = month_after(year, month)
    return names


def month_bounds_ns(path: Path) -> tuple[int, int]:
    match = MONTH_FILE.fullmatch(path.name)
    if match is None:
        raise ValueError(f"not a monthly partition: {path}")
    year, month = map(int, match.groups())
    next_year, next_month = month_after(year, month)
    start = int(datetime(year, month, 1, tzinfo=UTC).timestamp() * 1_000_000_000)
    end = int(
        datetime(next_year, next_month, 1, tzinfo=UTC).timestamp()
        * 1_000_000_000
    )
    return start, end


def scalar_bool(value: object) -> bool:
    return bool(value.as_py()) if value is not None else False


def validate(args: argparse.Namespace) -> dict[str, object]:
    root = args.path.resolve()
    expected = month_names(args.start_month, args.end_month)
    files = [root / name for name in expected]
    errors: list[str] = []
    warnings: list[str] = []
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        errors.extend(f"missing partition: {path}" for path in missing)
    files = [path for path in files if path.is_file()]

    reference_schema = None
    total_rows = 0
    total_bytes = 0
    total_row_groups = 0
    previous_file_max: int | None = None
    metadata_rows: dict[str, int] = {}
    file_time_ranges: dict[str, tuple[int, int]] = {}
    metadata_started = time.perf_counter()

    for index, path in enumerate(files, start=1):
        try:
            parquet = pq.ParquetFile(path)
            metadata = parquet.metadata
        except Exception as exc:
            errors.append(f"cannot open {path.name}: {type(exc).__name__}: {exc}")
            continue

        schema = parquet.schema_arrow
        if reference_schema is None:
            reference_schema = schema
        elif not schema.equals(reference_schema, check_metadata=False):
            errors.append(f"schema mismatch: {path.name}")

        if metadata.num_rows <= 0:
            errors.append(f"empty partition: {path.name}")
        if metadata.num_row_groups <= 0:
            errors.append(f"no row groups: {path.name}")

        start_ns, end_ns = month_bounds_ns(path)
        t_index = schema.get_field_index("t")
        if t_index < 0:
            errors.append(f"missing t column: {path.name}")
            continue

        file_min: int | None = None
        file_max: int | None = None
        previous_group_max: int | None = None
        null_counts = {name: 0 for name in schema.names}

        for group_index in range(metadata.num_row_groups):
            group = metadata.row_group(group_index)
            if group.num_rows <= 0:
                errors.append(f"empty row group: {path.name}#{group_index}")

            t_stats = group.column(t_index).statistics
            if t_stats is None or not t_stats.has_min_max:
                errors.append(f"missing timestamp statistics: {path.name}#{group_index}")
            else:
                group_min = int(t_stats.min)
                group_max = int(t_stats.max)
                if group_min > group_max:
                    errors.append(f"reversed timestamps: {path.name}#{group_index}")
                if group_min < start_ns or group_max >= end_ns:
                    errors.append(
                        f"timestamp outside partition month: {path.name}#{group_index} "
                        f"[{group_min}, {group_max}]"
                    )
                if previous_group_max is not None and group_min < previous_group_max:
                    errors.append(
                        f"row-group timestamp order violation: {path.name}#{group_index}"
                    )
                previous_group_max = group_max
                file_min = group_min if file_min is None else min(file_min, group_min)
                file_max = group_max if file_max is None else max(file_max, group_max)

            for column_index, name in enumerate(schema.names):
                stats = group.column(column_index).statistics
                if stats is None:
                    warnings.append(
                        f"missing column statistics: {path.name}#{group_index}:{name}"
                    )
                    continue
                null_counts[name] += stats.null_count or 0
                if name in SIZE_COLUMNS and stats.has_min_max and stats.min < 0:
                    errors.append(
                        f"negative {name}: {path.name}#{group_index} min={stats.min}"
                    )
                if name in PRICE_COLUMNS and stats.has_min_max:
                    if not math.isfinite(float(stats.min)) or not math.isfinite(
                        float(stats.max)
                    ):
                        errors.append(
                            f"non-finite {name}: {path.name}#{group_index}"
                        )
                    if stats.min < 0:
                        errors.append(
                            f"negative {name}: {path.name}#{group_index} min={stats.min}"
                        )

        for name, count in null_counts.items():
            if count:
                errors.append(f"null {name} values in {path.name}: {count}")

        if file_min is not None and file_max is not None:
            if previous_file_max is not None and file_min < previous_file_max:
                errors.append(f"monthly timestamp overlap before {path.name}")
            previous_file_max = file_max
            file_time_ranges[path.name] = (file_min, file_max)

        metadata_rows[path.name] = metadata.num_rows
        total_rows += metadata.num_rows
        total_row_groups += metadata.num_row_groups
        total_bytes += path.stat().st_size
        if index % 12 == 0 or index == len(files):
            print(
                f"metadata {index}/{len(files)} files; rows={total_rows}",
                file=sys.stderr,
                flush=True,
            )

    timestamp_rows = 0
    timestamp_reversals = 0
    timestamp_files_with_reversals: set[str] = set()
    maximum_backstep_ns = 0
    sampled_rows = 0
    crossed_books = 0
    maximum_crossed_spread = 0.0
    nonfinite_samples = {name: 0 for name in PRICE_COLUMNS}
    action_values: set[str] = set()
    side_values: set[str] = set()
    scan_started = time.perf_counter()

    for index, path in enumerate(files, start=1):
        try:
            parquet = pq.ParquetFile(path)
            scanned_in_file = 0
            previous_timestamp: int | None = None

            for batch in parquet.iter_batches(
                batch_size=args.batch_size, columns=["t"], use_threads=True
            ):
                values = batch.column(0).to_numpy(zero_copy_only=False)
                if values.size:
                    if previous_timestamp is not None and int(values[0]) < previous_timestamp:
                        timestamp_reversals += 1
                        timestamp_files_with_reversals.add(path.name)
                        maximum_backstep_ns = max(
                            maximum_backstep_ns,
                            previous_timestamp - int(values[0]),
                        )
                    if values.size > 1:
                        reversal_mask = values[1:] < values[:-1]
                        reversal_count = int(np.count_nonzero(reversal_mask))
                        if reversal_count:
                            timestamp_reversals += reversal_count
                            timestamp_files_with_reversals.add(path.name)
                            backsteps = values[:-1][reversal_mask] - values[1:][reversal_mask]
                            maximum_backstep_ns = max(
                                maximum_backstep_ns, int(backsteps.max())
                            )
                    previous_timestamp = int(values[-1])
                scanned_in_file += len(values)

            if scanned_in_file != metadata_rows.get(path.name):
                errors.append(
                    f"timestamp scan row mismatch: {path.name} "
                    f"metadata={metadata_rows.get(path.name)} scanned={scanned_in_file}"
                )
            timestamp_rows += scanned_in_file

            group_count = parquet.metadata.num_row_groups
            sample_count = min(args.sample_row_groups, group_count)
            if sample_count:
                sample_groups = sorted(
                    {
                        round(position * (group_count - 1) / max(sample_count - 1, 1))
                        for position in range(sample_count)
                    }
                )
                for group_index in sample_groups:
                    table = parquet.read_row_group(
                        group_index,
                        columns=[
                            "action",
                            "side",
                            "price",
                            "size",
                            "bid_px",
                            "ask_px",
                            "bid_sz",
                            "ask_sz",
                        ],
                        use_threads=True,
                    )
                    sampled_rows += table.num_rows
                    action_values.update(
                        str(value.as_py()) for value in pc.unique(table["action"])
                    )
                    side_values.update(
                        str(value.as_py()) for value in pc.unique(table["side"])
                    )

                    for name in PRICE_COLUMNS:
                        values = table[name].combine_chunks().to_numpy(zero_copy_only=False)
                        finite = np.isfinite(values)
                        nonfinite_samples[name] += int(np.count_nonzero(~finite))
                        if bool(np.any(values[finite] < 0)):
                            errors.append(
                                f"negative sampled {name}: {path.name}#{group_index}"
                            )
                    for name in SIZE_COLUMNS:
                        values = table[name].combine_chunks().to_numpy(zero_copy_only=False)
                        if bool(np.any(values < 0)):
                            errors.append(
                                f"negative sampled {name}: {path.name}#{group_index}"
                            )

                    bid = table["bid_px"].combine_chunks().to_numpy(zero_copy_only=False)
                    ask = table["ask_px"].combine_chunks().to_numpy(zero_copy_only=False)
                    crossed = (bid > 0) & (ask > 0) & (bid > ask)
                    crossed_books += int(np.count_nonzero(crossed))
                    if bool(np.any(crossed)):
                        maximum_crossed_spread = max(
                            maximum_crossed_spread,
                            float((bid[crossed] - ask[crossed]).max()),
                        )
        except Exception as exc:
            errors.append(f"content scan failed for {path.name}: {type(exc).__name__}: {exc}")

        if index % 6 == 0 or index == len(files):
            print(
                f"content {index}/{len(files)} files; timestamp_rows={timestamp_rows}",
                file=sys.stderr,
                flush=True,
            )

    if crossed_books:
        warnings.append(
            f"sampled crossed top-of-book rows: {crossed_books} of {sampled_rows}"
        )
    if timestamp_reversals:
        warnings.append(
            f"event-time reversals: {timestamp_reversals} of {timestamp_rows}; "
            f"maximum backstep {maximum_backstep_ns} ns"
        )
    if any(nonfinite_samples.values()):
        warnings.append(
            "sampled non-finite prices (empty/reset book states): "
            + ", ".join(f"{name}={count}" for name, count in nonfinite_samples.items())
        )

    return {
        "status": "clean" if not errors else "failed",
        "path": str(root),
        "expected_partitions": len(expected),
        "validated_partitions": len(files),
        "rows": total_rows,
        "timestamp_rows_scanned": timestamp_rows,
        "timestamp_reversals": timestamp_reversals,
        "timestamp_files_with_reversals": sorted(timestamp_files_with_reversals),
        "maximum_timestamp_backstep_ns": maximum_backstep_ns,
        "sampled_full_rows": sampled_rows,
        "row_groups": total_row_groups,
        "bytes": total_bytes,
        "schema": str(reference_schema) if reference_schema is not None else None,
        "actions_seen": sorted(action_values),
        "sides_seen": sorted(side_values),
        "crossed_books_sampled": crossed_books,
        "maximum_crossed_spread": maximum_crossed_spread,
        "nonfinite_price_samples": nonfinite_samples,
        "metadata_seconds": round(scan_started - metadata_started, 3),
        "content_seconds": round(time.perf_counter() - scan_started, 3),
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--start-month", default="2020-01")
    parser.add_argument("--end-month", default="2026-09")
    parser.add_argument("--batch-size", type=int, default=1_048_576)
    parser.add_argument("--sample-row-groups", type=int, default=5)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate(args)
    output = json.dumps(report, indent=2, sort_keys=True)
    print(output)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    return 0 if report["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
