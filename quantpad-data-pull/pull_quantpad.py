#!/usr/bin/env python3
"""Resumable QuantPad pull based on databento_pull_list.md.

The attached document is treated as a pull specification. QuantPad's live
coverage response is authoritative for availability and plan-clamped dates.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterator

import pyarrow.ipc as ipc
import pyarrow.parquet as pq
from dotenv import load_dotenv

import quantpad_data as qpd


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data"
LOG_ROOT = ROOT / "logs"
MANIFEST_ROOT = ROOT / "manifests"


@dataclass(frozen=True)
class PullSpec:
    id: str
    phase: int
    dataset: str
    symbol: str
    schema: str
    kind: str
    start: str | None = None
    lookback_days: int | None = None
    partition: str = "year"
    roll_adjust: str = "none"
    note: str = ""


# Continuous futures use Databento/QuantPad's open-interest continuation.
# Raw, unadjusted prices are retained; instrument_id makes every roll auditable.
SPECS: tuple[PullSpec, ...] = (
    PullSpec("01-nq-1m", 1, "GLBX.MDP3", "NQ.c.0", "ohlcv-1m", "bars"),
    PullSpec("01-es-1m", 1, "GLBX.MDP3", "ES.c.0", "ohlcv-1m", "bars"),
    PullSpec("01-ym-1m", 1, "GLBX.MDP3", "YM.c.0", "ohlcv-1m", "bars"),
    PullSpec("01-rty-1m", 1, "GLBX.MDP3", "RTY.c.0", "ohlcv-1m", "bars"),
    PullSpec("02-nq-1s", 1, "GLBX.MDP3", "NQ.c.0", "ohlcv-1s", "bars"),
    PullSpec("03-nq-statistics", 1, "GLBX.MDP3", "NQ.c.0", "statistics", "ticks", partition="all"),
    PullSpec("03-es-statistics", 1, "GLBX.MDP3", "ES.c.0", "statistics", "ticks", partition="all"),
    PullSpec("03-ym-statistics", 1, "GLBX.MDP3", "YM.c.0", "statistics", "ticks"),
    PullSpec("03-rty-statistics", 1, "GLBX.MDP3", "RTY.c.0", "statistics", "ticks"),
    PullSpec("04-nq-definition", 1, "GLBX.MDP3", "NQ.c.0", "definition", "ticks"),
    PullSpec("04-es-definition", 1, "GLBX.MDP3", "ES.c.0", "definition", "ticks"),
    PullSpec("04-ym-definition", 1, "GLBX.MDP3", "YM.c.0", "definition", "ticks"),
    PullSpec("04-rty-definition", 1, "GLBX.MDP3", "RTY.c.0", "definition", "ticks"),

    PullSpec("12-qqq-statistics", 2, "OPRA.PILLAR", "QQQ.OPT", "statistics", "ticks", start="2020-01-01", partition="month"),
    PullSpec("12-ndxp-statistics", 2, "OPRA.PILLAR", "NDXP.OPT", "statistics", "ticks", start="2020-01-01", partition="month"),
    PullSpec("12-ndx-statistics", 2, "OPRA.PILLAR", "NDX.OPT", "statistics", "ticks", start="2020-01-01", partition="month", note="Retain the full parent stream; select monthlies at DTE <= 45 when building the contract manifest."),
    PullSpec("13-qqq-definition", 2, "OPRA.PILLAR", "QQQ.OPT", "definition", "ticks", start="2020-01-01", partition="month"),
    PullSpec("13-ndxp-definition", 2, "OPRA.PILLAR", "NDXP.OPT", "definition", "ticks", start="2020-01-01", partition="month"),
    PullSpec("13-ndx-definition", 2, "OPRA.PILLAR", "NDX.OPT", "definition", "ticks", start="2020-01-01", partition="month", note="Retain the full parent stream; select monthlies at DTE <= 45 when building the contract manifest."),
    PullSpec("14-qqq-cbbo-1m", 2, "OPRA.PILLAR", "QQQ.OPT", "cbbo-1m", "ticks", start="2013-01-01", partition="day", note="Live coverage currently starts in 2023."),
    PullSpec("14-ndx-cbbo-1m", 2, "OPRA.PILLAR", "NDX.OPT", "cbbo-1m", "ticks", start="2013-01-01", partition="day", note="Live coverage currently starts in 2023."),
    PullSpec("14-ndxp-cbbo-1m", 2, "OPRA.PILLAR", "NDXP.OPT", "cbbo-1m", "ticks", start="2013-01-01", partition="day", note="Live coverage currently starts in 2023."),
    PullSpec("15-qqq-option-1d", 2, "OPRA.PILLAR", "QQQ.OPT", "ohlcv-1d", "bars", start="2013-01-01"),
    PullSpec("15-ndx-option-1d", 2, "OPRA.PILLAR", "NDX.OPT", "ohlcv-1d", "bars", start="2013-01-01"),
    PullSpec("15-ndxp-option-1d", 2, "OPRA.PILLAR", "NDXP.OPT", "ohlcv-1d", "bars", start="2013-01-01"),
    PullSpec("22-qqq-underlying-1m", 2, "XNAS.ITCH", "QQQ", "ohlcv-1m", "bars", start="2013-01-01"),
    PullSpec("22-spy-underlying-1m", 2, "ARCX.PILLAR", "SPY", "ohlcv-1m", "bars", start="2013-01-01"),

    PullSpec(
        "09-nqopt-definition",
        3,
        "GLBX.MDP3",
        "NQ.FUT.OPT",
        "definition",
        "ticks",
        start="2020-01-01",
        partition="month",
        note="QuantPad payload parent; Databento-style symbology parent is NQ.OPT.",
    ),
    PullSpec(
        "09-nqopt-statistics",
        3,
        "GLBX.MDP3",
        "NQ.FUT.OPT",
        "statistics",
        "ticks",
        start="2020-01-01",
        partition="month",
    ),
    PullSpec(
        "10-nqopt-trades",
        3,
        "GLBX.MDP3",
        "NQ.FUT.OPT",
        "trades",
        "ticks",
        start="2020-01-01",
        partition="day",
        note="Requires per-contract fan-out; QuantPad rejects parent-chain trade payloads.",
    ),
    PullSpec(
        "11-nqopt-1m",
        3,
        "GLBX.MDP3",
        "NQ.FUT.OPT",
        "ohlcv-1m",
        "bars",
        start="2020-01-01",
        partition="month",
        note="Requires per-contract fan-out; QuantPad rejects parent-chain bar payloads.",
    ),
    PullSpec("07-nq-mbp10", 3, "GLBX.MDP3", "NQ.c.0", "mbp-10", "ticks", lookback_days=30, partition="day"),

    PullSpec("05-nq-trades", 4, "GLBX.MDP3", "NQ.c.0", "trades", "ticks", start="2020-01-01", partition="year"),
    PullSpec("06-nq-mbp1", 4, "GLBX.MDP3", "NQ.c.0", "mbp-1", "ticks", start="2020-01-01", partition="month", note="Independent monthly acquisition and storage partitions; do not consolidate."),
    PullSpec("06-es-mbp1", 4, "GLBX.MDP3", "ES.c.0", "mbp-1", "ticks", start="2020-01-01", partition="month", note="Independent monthly acquisition and storage partitions; do not consolidate."),
    PullSpec("08-es-trades", 4, "GLBX.MDP3", "ES.c.0", "trades", "ticks", start="2020-01-01", partition="year", note="Six-year cross-index flow; annual request and storage partitions."),
    PullSpec("08-ym-trades", 4, "GLBX.MDP3", "YM.c.0", "trades", "ticks", start="2020-01-01", partition="year", note="Six-year cross-index flow; annual request and storage partitions."),
    PullSpec("08-rty-trades", 4, "GLBX.MDP3", "RTY.c.0", "trades", "ticks", start="2020-01-01", partition="year", note="Six-year cross-index flow; annual request and storage partitions."),
)


def iso_ms(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return int(parsed.timestamp() * 1000)


def ms_iso(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=UTC).isoformat()


def safe_name(value: str) -> str:
    return value.lower().replace(".", "-").replace("/", "-")


def add_month(value: datetime) -> datetime:
    year = value.year + (1 if value.month == 12 else 0)
    month = 1 if value.month == 12 else value.month + 1
    return datetime(year, month, 1, tzinfo=UTC)


def partition_ranges(start_ms: int, end_ms: int, unit: str) -> Iterator[tuple[int, int, str]]:
    if unit == "all":
        yield start_ms, end_ms, "full"
        return
    start_dt = datetime.fromtimestamp(start_ms / 1000, tz=UTC)
    if unit == "day":
        cursor = datetime(start_dt.year, start_dt.month, start_dt.day, tzinfo=UTC)
    elif unit == "week":
        day = datetime(start_dt.year, start_dt.month, start_dt.day, tzinfo=UTC)
        cursor = day - timedelta(days=day.weekday())
    elif unit == "month":
        cursor = datetime(start_dt.year, start_dt.month, 1, tzinfo=UTC)
    elif unit == "year":
        cursor = datetime(start_dt.year, 1, 1, tzinfo=UTC)
    else:
        raise ValueError(f"Unsupported partition unit: {unit}")

    while int(cursor.timestamp() * 1000) < end_ms:
        if unit == "day":
            next_cursor = cursor.fromtimestamp(cursor.timestamp() + 86400, tz=UTC)
            label = cursor.strftime("%Y-%m-%d")
        elif unit == "week":
            next_cursor = cursor + timedelta(days=7)
            label = cursor.strftime("%Y-%m-%d")
        elif unit == "month":
            next_cursor = add_month(cursor)
            label = cursor.strftime("%Y-%m")
        else:
            next_cursor = datetime(cursor.year + 1, 1, 1, tzinfo=UTC)
            label = cursor.strftime("%Y")
        left = max(start_ms, int(cursor.timestamp() * 1000))
        right = min(end_ms, int(next_cursor.timestamp() * 1000))
        if left < right:
            yield left, right, label
        cursor = next_cursor


class Puller:
    def __init__(self) -> None:
        load_dotenv(ROOT / ".env")
        if not os.getenv("QUANTPAD_API_KEY"):
            raise SystemExit(f"Missing QUANTPAD_API_KEY in {ROOT / '.env'}")
        self.client = qpd.Client(timeout=120, max_retries=5)
        self.coverage_cache: dict[str, dict] = {}
        for directory in (DATA_ROOT, LOG_ROOT, MANIFEST_ROOT):
            directory.mkdir(parents=True, exist_ok=True)

    def coverage(self, symbol: str) -> dict:
        key = symbol.upper()
        if key not in self.coverage_cache:
            self.coverage_cache[key] = self.client.get_coverage(symbol)
        return self.coverage_cache[key]

    def bounds(
        self,
        spec: PullSpec,
        start_override: str | None = None,
        end_override: str | None = None,
    ) -> tuple[int, int, dict]:
        coverage = self.coverage(spec.symbol)
        schemas = {item["schema"]: item for item in coverage.get("schemas", [])}
        entry = schemas.get(spec.schema)
        if entry is None and spec.schema in {"definition", "statistics"}:
            # Futures reference events work even though v1 coverage currently
            # omits them. Use the bar coverage as a conservative date bound.
            entry = schemas.get("ohlcv-1m")
        if not entry or entry.get("coverage_start_ms") is None:
            raise RuntimeError(f"No QuantPad coverage for {spec.symbol} {spec.schema}")

        start_ms = int(entry["coverage_start_ms"])
        end_ms = min(int(entry["coverage_end_ms"]), int(time.time() * 1000))
        if spec.start:
            start_ms = max(start_ms, iso_ms(spec.start))
        if spec.lookback_days:
            start_ms = max(start_ms, end_ms - spec.lookback_days * 86_400_000)
        if start_override:
            start_ms = max(start_ms, iso_ms(start_override))
        if end_override:
            end_ms = min(end_ms, iso_ms(end_override))
        if start_ms >= end_ms:
            raise RuntimeError(
                f"Empty requested range for {spec.id}: "
                f"{ms_iso(start_ms)} -> {ms_iso(end_ms)}"
            )
        return start_ms, end_ms, coverage

    def destination(self, spec: PullSpec, label: str) -> Path:
        folder = (
            DATA_ROOT
            / f"phase-{spec.phase}"
            / safe_name(spec.dataset)
            / safe_name(spec.symbol)
            / safe_name(spec.schema)
        )
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{label}.parquet"

    @staticmethod
    def valid_parquet(path: Path) -> bool:
        if not path.exists() or path.stat().st_size == 0:
            return False
        try:
            pq.ParquetFile(path).metadata
            return True
        except Exception:
            return False

    def record(self, payload: dict) -> None:
        path = MANIFEST_ROOT / "completed.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def download(self, spec: PullSpec, start_ms: int, end_ms: int, label: str) -> dict:
        destination = self.destination(spec, label)
        if self.valid_parquet(destination):
            metadata = pq.ParquetFile(destination).metadata
            return {"status": "skipped", "path": str(destination), "rows": metadata.num_rows}

        partial = destination.with_suffix(destination.suffix + ".part")
        if partial.exists():
            partial.unlink()

        if spec.kind == "bars":
            path = "/v1/bars"
            params = {
                "symbol": spec.symbol,
                "timeframe": spec.schema.removeprefix("ohlcv-"),
                "start": start_ms,
                "end": end_ms,
                "format": "arrow",
                "roll_adjust": spec.roll_adjust,
                "compression": "zstd",
            }
        else:
            path = "/v1/ticks"
            params = {
                "symbol": spec.symbol,
                "schema": spec.schema,
                "start": start_ms,
                "end": end_ms,
                "compression": "zstd",
            }

        # Fail a genuinely stalled connection after five minutes without a
        # byte. Healthy long streams can run for hours; the read timeout resets
        # whenever another Arrow batch arrives.
        response = self.client._request(
            "GET", path, params=params, timeout=(30, 300), stream=True
        )
        response.raw.decode_content = True
        row_count = 0
        writer = None
        try:
            reader = ipc.open_stream(response.raw)
            writer = pq.ParquetWriter(
                partial,
                reader.schema,
                compression="zstd",
                use_dictionary=True,
                write_statistics=True,
            )
            for batch in reader:
                if batch.num_rows:
                    writer.write_batch(batch)
                    row_count += batch.num_rows
        finally:
            if writer is not None:
                writer.close()
            response.close()

        if not partial.exists():
            raise RuntimeError(f"QuantPad returned no Arrow stream for {spec.id} {label}")
        os.replace(partial, destination)
        result = {
            "status": "downloaded",
            "spec_id": spec.id,
            "dataset": spec.dataset,
            "symbol": spec.symbol,
            "schema": spec.schema,
            "start": ms_iso(start_ms),
            "end": ms_iso(end_ms),
            "rows": row_count,
            "bytes": destination.stat().st_size,
            "path": str(destination),
            "completed_at": datetime.now(tz=UTC).isoformat(),
        }
        self.record(result)
        return result

    def plan(
        self,
        specs: list[PullSpec],
        start_override: str | None = None,
        end_override: str | None = None,
    ) -> list[dict]:
        output = []
        for spec in specs:
            try:
                start_ms, end_ms, coverage = self.bounds(
                    spec, start_override, end_override
                )
                ranges = list(partition_ranges(start_ms, end_ms, spec.partition))
                existing = sum(
                    self.valid_parquet(self.destination(spec, label))
                    for _, _, label in ranges
                )
                output.append(
                    {
                        **asdict(spec),
                        "resolved_dataset": coverage.get("dataset"),
                        "effective_start": ms_iso(start_ms),
                        "effective_end": ms_iso(end_ms),
                        "partitions": len(ranges),
                        "complete": existing,
                    }
                )
            except Exception as exc:
                output.append({**asdict(spec), "error": f"{type(exc).__name__}: {exc}"})
        return output


def selected_specs(phases: list[int] | None, ids: list[str] | None) -> list[PullSpec]:
    specs = list(SPECS)
    if phases:
        specs = [spec for spec in specs if spec.phase in phases]
    if ids:
        wanted = set(ids)
        specs = [spec for spec in specs if spec.id in wanted]
        missing = wanted - {spec.id for spec in specs}
        if missing:
            raise SystemExit(f"Unknown spec id(s): {', '.join(sorted(missing))}")
    return specs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "run"))
    parser.add_argument("--phase", type=int, action="append", dest="phases")
    parser.add_argument("--id", action="append", dest="ids")
    parser.add_argument("--max-partitions", type=int)
    parser.add_argument("--partition-retries", type=int, default=2)
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument(
        "--start",
        help="Optional inclusive ISO-8601 lower bound (use a partition boundary)",
    )
    parser.add_argument(
        "--end",
        help="Optional exclusive ISO-8601 upper bound (use a partition boundary)",
    )
    args = parser.parse_args()

    puller = Puller()
    specs = selected_specs(args.phases, args.ids)
    plan = puller.plan(specs, args.start, args.end)
    plan_path = MANIFEST_ROOT / "latest-plan.json"
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    if args.command == "plan":
        print(json.dumps(plan, indent=2))
        return 0

    remaining = args.max_partitions
    failures = 0
    for spec in specs:
        try:
            start_ms, end_ms, _ = puller.bounds(spec, args.start, args.end)
            ranges = partition_ranges(start_ms, end_ms, spec.partition)
            for left, right, label in ranges:
                if remaining is not None and remaining <= 0:
                    return 1 if failures else 0
                print(f"[{spec.id}] {label} {ms_iso(left)} -> {ms_iso(right)}", flush=True)
                for attempt in range(args.partition_retries + 1):
                    try:
                        result = puller.download(spec, left, right, label)
                        print(json.dumps(result, sort_keys=True), flush=True)
                        break
                    except Exception as exc:
                        if attempt < args.partition_retries:
                            delay = min(60, 5 * (2**attempt))
                            print(
                                f"RETRY [{spec.id}] {label} after "
                                f"{type(exc).__name__}: {exc} ({delay}s)",
                                file=sys.stderr,
                                flush=True,
                            )
                            time.sleep(delay)
                            continue
                        failures += 1
                        print(f"ERROR [{spec.id}] {label}: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
                        if not args.keep_going:
                            return 1
                if remaining is not None:
                    remaining -= 1
        except Exception as exc:
            failures += 1
            print(f"ERROR [{spec.id}]: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
            if not args.keep_going:
                return 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
