#!/usr/bin/env python3
"""Benchmark one direct calendar-year QuantPad NQ MBP-1 request."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.ipc as ipc
import pyarrow.parquet as pq
from dotenv import load_dotenv

import quantpad_data as qpd


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "data" / "phase-4" / "glbx-mdp3" / "nq-c-0" / "mbp-1-yearly"
MANIFEST_ROOT = ROOT / "manifests" / "nq-mbp1-yearly"


def as_ms(value: datetime) -> int:
    return int(value.timestamp() * 1_000)


def save_manifest(year: int, payload: dict) -> None:
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    destination = MANIFEST_ROOT / f"{year}.json"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, destination)


def run(year: int) -> Path:
    load_dotenv(ROOT / ".env")
    if not os.environ.get("QUANTPAD_API_KEY"):
        raise SystemExit(f"Missing QUANTPAD_API_KEY in {ROOT / '.env'}")

    start = datetime(year, 1, 1, tzinfo=UTC)
    end = datetime(year + 1, 1, 1, tzinfo=UTC)
    start_ns = int(start.timestamp() * 1_000_000_000)
    end_ns = int(end.timestamp() * 1_000_000_000)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_ROOT / f"{year}.parquet"
    partial = OUTPUT_ROOT / f"{year}.parquet.direct.part"
    if output.exists():
        raise RuntimeError(f"Refusing to overwrite existing annual file {output}")
    if partial.exists():
        partial.unlink()

    client = qpd.Client(timeout=120, max_retries=0)
    request_started = time.monotonic()
    response = client._request(
        "GET",
        "/v1/ticks",
        params={
            "symbol": "NQ.c.0",
            "schema": "mbp-1",
            "start": as_ms(start),
            "end": as_ms(end),
            "compression": "zstd",
        },
        timeout=(30, 300),
        stream=True,
    )
    headers_received = time.monotonic()
    response.raw.decode_content = True
    reader = ipc.open_stream(response.raw)
    writer = pq.ParquetWriter(
        partial,
        reader.schema,
        compression="zstd",
        use_dictionary=True,
        write_statistics=True,
    )
    rows = 0
    first_batch_at: float | None = None
    minimum_t: int | None = None
    maximum_t: int | None = None
    next_report = 25_000_000
    try:
        for batch in reader:
            if first_batch_at is None:
                first_batch_at = time.monotonic()
            if batch.num_rows:
                time_column = batch.column(reader.schema.get_field_index("t"))
                batch_min = pc.min(time_column).as_py()
                batch_max = pc.max(time_column).as_py()
                minimum_t = batch_min if minimum_t is None else min(minimum_t, batch_min)
                maximum_t = batch_max if maximum_t is None else max(maximum_t, batch_max)
                writer.write_batch(batch)
                rows += batch.num_rows
                if rows >= next_report:
                    elapsed = time.monotonic() - request_started
                    print(f"{year}: {rows:,} rows in {elapsed:.1f}s", flush=True)
                    next_report += 25_000_000
    finally:
        writer.close()
        response.close()
    completed = time.monotonic()

    metadata = pq.ParquetFile(partial).metadata
    if metadata.num_rows != rows:
        raise RuntimeError(f"Row mismatch: streamed {rows}, Parquet reports {metadata.num_rows}")
    if rows and (minimum_t is None or minimum_t < start_ns or maximum_t >= end_ns):
        raise RuntimeError(
            f"Timestamp bounds outside {start.isoformat()} -> {end.isoformat()}: "
            f"{minimum_t} -> {maximum_t}"
        )
    os.replace(partial, output)

    first = first_batch_at or completed
    payload = {
        "year": year,
        "verified": True,
        "source": "quantpad-direct-yearly-benchmark",
        "symbol": "NQ.c.0",
        "schema": "mbp-1",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "transport_compression": response.headers.get("X-Arrow-Compression"),
        "request_to_headers_seconds": headers_received - request_started,
        "headers_to_first_batch_seconds": first - headers_received,
        "stream_and_write_seconds": completed - first,
        "total_seconds": completed - request_started,
        "output_rows": rows,
        "output_bytes": output.stat().st_size,
        "minimum_t": minimum_t,
        "maximum_t": maximum_t,
        "output": str(output),
        "completed_at": datetime.now(tz=UTC).isoformat(),
    }
    save_manifest(year, payload)
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2021)
    args = parser.parse_args()
    run(args.year)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
