#!/usr/bin/env python3
"""Consolidate completed NQ MBP-1 weekly Parquet files by calendar year."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "data" / "phase-4" / "glbx-mdp3" / "nq-c-0" / "mbp-1"
OUTPUT_ROOT = ROOT / "data" / "phase-4" / "glbx-mdp3" / "nq-c-0" / "mbp-1-yearly"
MANIFEST_ROOT = ROOT / "manifests" / "nq-mbp1-yearly"
FIRST_YEAR = 2020


def utc_ns(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000_000)


def expected_week_paths(year: int) -> list[Path]:
    year_start = datetime(year, 1, 1, tzinfo=UTC)
    year_end = datetime(year + 1, 1, 1, tzinfo=UTC)
    cursor = year_start - timedelta(days=year_start.weekday())
    paths: list[Path] = []
    while cursor < year_end:
        paths.append(SOURCE_ROOT / f"{cursor:%Y-%m-%d}.parquet")
        cursor += timedelta(days=7)
    return paths


def valid_parquet(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    try:
        pq.ParquetFile(path).metadata
        return True
    except Exception:
        return False


def output_is_verified(year: int) -> bool:
    output = OUTPUT_ROOT / f"{year}.parquet"
    manifest_path = MANIFEST_ROOT / f"{year}.json"
    if not valid_parquet(output) or not manifest_path.is_file():
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metadata = pq.ParquetFile(output).metadata
    return (
        manifest.get("verified") is True
        and manifest.get("output_rows") == metadata.num_rows
        and manifest.get("output_bytes") == output.stat().st_size
    )


def write_manifest(year: int, payload: dict) -> None:
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    destination = MANIFEST_ROOT / f"{year}.json"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, destination)


def consolidate(year: int, *, batch_rows: int = 250_000) -> Path:
    paths = expected_week_paths(year)
    missing = [path for path in paths if not valid_parquet(path)]
    if missing:
        raise RuntimeError(
            f"{year} is not complete; {len(missing)} weekly files missing or invalid "
            f"(first: {missing[0].name})"
        )

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_ROOT / f"{year}.parquet"
    partial = output.with_suffix(".parquet.part")
    if partial.exists():
        partial.unlink()

    start_ns = utc_ns(datetime(year, 1, 1, tzinfo=UTC))
    end_ns = utc_ns(datetime(year + 1, 1, 1, tzinfo=UTC))
    schema = pq.ParquetFile(paths[0]).schema_arrow
    if "t" not in schema.names:
        raise RuntimeError(f"Source schema for {paths[0]} has no t column")

    source_rows = 0
    output_rows = 0
    minimum_t: int | None = None
    maximum_t: int | None = None
    writer = pq.ParquetWriter(
        partial,
        schema,
        compression="zstd",
        use_dictionary=True,
        write_statistics=True,
    )
    try:
        for index, path in enumerate(paths, start=1):
            parquet = pq.ParquetFile(path)
            source_rows += parquet.metadata.num_rows
            for batch in parquet.iter_batches(batch_size=batch_rows):
                time_column = batch.column(schema.get_field_index("t"))
                mask = pc.and_(
                    pc.greater_equal(time_column, pa.scalar(start_ns, type=pa.int64())),
                    pc.less(time_column, pa.scalar(end_ns, type=pa.int64())),
                )
                selected = batch.filter(mask)
                if selected.num_rows == 0:
                    continue
                selected_t = selected.column(schema.get_field_index("t"))
                batch_min = pc.min(selected_t).as_py()
                batch_max = pc.max(selected_t).as_py()
                minimum_t = batch_min if minimum_t is None else min(minimum_t, batch_min)
                maximum_t = batch_max if maximum_t is None else max(maximum_t, batch_max)
                writer.write_batch(selected)
                output_rows += selected.num_rows
            if index % 10 == 0 or index == len(paths):
                print(f"{year}: processed {index}/{len(paths)} weekly files", flush=True)
    finally:
        writer.close()

    metadata = pq.ParquetFile(partial).metadata
    if metadata.num_rows != output_rows:
        raise RuntimeError(
            f"{year} row-count mismatch: writer tracked {output_rows}, "
            f"Parquet reports {metadata.num_rows}"
        )
    if output_rows and (minimum_t is None or minimum_t < start_ns or maximum_t >= end_ns):
        raise RuntimeError(f"{year} output timestamp bounds are invalid")

    os.replace(partial, output)
    payload = {
        "year": year,
        "verified": True,
        "source_files": len(paths),
        "source_rows_including_boundary_overlap": source_rows,
        "output_rows": output_rows,
        "output_bytes": output.stat().st_size,
        "minimum_t": minimum_t,
        "maximum_t": maximum_t,
        "output": str(output),
        "completed_at": datetime.now(tz=UTC).isoformat(),
    }
    write_manifest(year, payload)
    print(f"{year}: wrote {output_rows} rows to {output}", flush=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("once", "watch"))
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--year", type=int, action="append", dest="years")
    args = parser.parse_args()

    completed_calendar_years = list(range(FIRST_YEAR, datetime.now(tz=UTC).year))
    targets = args.years or completed_calendar_years
    invalid = [year for year in targets if year not in completed_calendar_years]
    if invalid:
        raise SystemExit(f"Only completed calendar years are eligible: {invalid}")

    while True:
        pending = [year for year in targets if not output_is_verified(year)]
        if not pending:
            print("All requested calendar years are consolidated and verified", flush=True)
            return 0
        made_progress = False
        for year in pending:
            missing = [path for path in expected_week_paths(year) if not valid_parquet(path)]
            if missing:
                print(
                    f"{year}: waiting for {len(missing)} weekly files; first {missing[0].name}",
                    flush=True,
                )
                continue
            consolidate(year)
            made_progress = True
        if args.command == "once":
            return 0 if made_progress else 1
        if not made_progress:
            time.sleep(max(30, args.poll_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
