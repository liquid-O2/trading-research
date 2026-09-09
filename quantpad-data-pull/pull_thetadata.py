#!/usr/bin/env python3
"""High-throughput, resumable ThetaData option-chain downloader.

The Theta Terminal performs vendor transport and exposes localhost REST. This
runner keeps all Pro request slots busy, streams compact CSV to local scratch,
and converts each response to an independent Zstd Parquet file with Polars.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Iterator
from zoneinfo import ZoneInfo

import httpx
import polars as pl


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data" / "thetadata"
MANIFEST_ROOT = ROOT / "manifests"
BASE_URL = "http://127.0.0.1:25503/v3"
SCRATCH_ROOT = Path(os.getenv("THETADATA_SCRATCH", "/tmp/thetadata-ingress"))

SYMBOLS = ("QQQ", "NDXP", "SPXW", "NDX", "SPX", "SPY")
VIX_SYMBOL = "VIX"
PRIORITY_SYMBOLS = ("QQQ", "NDXP", "SPXW")
SECONDARY_SYMBOLS = ("NDX", "SPX", "SPY")
STRIKE_RANGES = {
    "QQQ": 42,
    "NDXP": 70,
    "NDX": 70,
    "SPXW": 90,
    "SPX": 90,
    "SPY": 45,
}
INVALID_VOLUME_CONDITIONS = {
    2, 5, 6, 7, 8, 13, 15, 26, 27, 28, 40, 41, 42, 43, 44, 57, 65
}
NY = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class Task:
    pull: str
    kind: str
    request_date: date
    symbols: tuple[str, ...]
    path: str
    params: tuple[tuple[str, str], ...]
    outputs: tuple[Path, ...]

    @property
    def label(self) -> str:
        return f"{self.pull}:{self.kind}:{','.join(self.symbols)}:{self.request_date}"


@dataclass(frozen=True)
class Downloaded:
    task: Task
    temp_path: Path
    response_bytes: int
    request_seconds: float
    fallback_expirations: int = 0


def output_path(pull: str, kind: str, symbol: str, day: date) -> Path:
    return DATA_ROOT / pull / kind / symbol / str(day.year) / f"{day.isoformat()}.parquet"


def empty_marker(path: Path) -> Path:
    return path.with_suffix(".empty.json")


def is_complete(path: Path) -> bool:
    marker = empty_marker(path)
    if marker.is_file():
        return True
    if not path.is_file() or path.stat().st_size < 100:
        return False
    try:
        pl.read_parquet_schema(path)
        return True
    except Exception:
        return False


def all_complete(task: Task) -> bool:
    return all(is_complete(path) for path in task.outputs)


def business_days(start: date, end: date, full_holidays: set[date]) -> Iterator[date]:
    cursor = start
    while cursor <= end:
        if cursor.weekday() < 5 and cursor not in full_holidays:
            yield cursor
        cursor += timedelta(days=1)


def fetch_full_holidays(start_year: int, end_year: int) -> set[date]:
    holidays: set[date] = set()
    with httpx.Client(timeout=30) as client:
        for year in range(start_year, end_year + 1):
            response = client.get(
                f"{BASE_URL}/calendar/year_holidays",
                params={"year": str(year), "format": "json"},
            )
            response.raise_for_status()
            payload = response.json()
            rows = payload.get("response", payload) if isinstance(payload, dict) else payload
            for row in rows:
                if row.get("type") == "full_close":
                    holidays.add(date.fromisoformat(row["date"]))
    return holidays


def make_task(
    pull: str,
    kind: str,
    day: date,
    symbol: str,
    path: str,
    params: dict[str, str | int],
) -> Task:
    return Task(
        pull=pull,
        kind=kind,
        request_date=day,
        symbols=(symbol,),
        path=path,
        params=tuple((key, str(value)) for key, value in params.items()),
        outputs=(output_path(pull, kind, symbol, day),),
    )


def pull1_tasks(days: Iterable[date]) -> Iterator[Task]:
    for day in days:
        active = tuple(symbol for symbol in SYMBOLS if symbol != "NDXP" or day.year >= 2018)
        for symbol in active:
            yield make_task(
                "pull-1",
                "open-interest",
                day,
                symbol,
                "/option/history/open_interest",
                {"symbol": symbol, "expiration": "*", "date": day.isoformat(), "format": "csv"},
            )
            yield make_task(
                "pull-1",
                "eod",
                day,
                symbol,
                "/option/history/eod",
                {
                    "symbol": symbol,
                    "expiration": "*",
                    "start_date": day.isoformat(),
                    "end_date": day.isoformat(),
                    "format": "csv",
                },
            )

        outputs = tuple(output_path("pull-1", "contracts", symbol, day) for symbol in active)
        yield Task(
            pull="pull-1",
            kind="contracts",
            request_date=day,
            symbols=active,
            path="/option/list/contracts/quote",
            params=(("symbol", ",".join(active)), ("date", day.isoformat()), ("format", "csv")),
            outputs=outputs,
        )


def load_contract_min_dte() -> dict[tuple[str, date], int]:
    pattern = str(DATA_ROOT / "pull-1" / "contracts" / "*" / "*" / "*.parquet")
    try:
        frame = (
            pl.scan_parquet(pattern)
            .select("symbol", "request_date", "expiration")
            .with_columns(
                (pl.col("expiration") - pl.col("request_date"))
                .dt.total_days()
                .alias("dte")
            )
            .filter(pl.col("dte") >= 0)
            .group_by("symbol", "request_date")
            .agg(pl.col("dte").min().alias("min_dte"))
            .collect()
        )
    except (FileNotFoundError, pl.exceptions.ComputeError):
        return {}
    return {
        (row["symbol"], row["request_date"]): int(row["min_dte"])
        for row in frame.iter_rows(named=True)
    }


def has_eligible_contract(
    availability: dict[tuple[str, date], int], symbol: str, day: date, max_dte: int
) -> bool:
    value = availability.get((symbol, day))
    return value is None or value <= max_dte


def pull2_tasks(
    days: Iterable[date], availability: dict[tuple[str, date], int]
) -> Iterator[Task]:
    for symbols in (PRIORITY_SYMBOLS, SECONDARY_SYMBOLS):
        for day in days:
            for symbol in symbols:
                if has_eligible_contract(availability, symbol, day, 14):
                    yield make_task(
                        "pull-2",
                        "quote-dte14",
                        day,
                        symbol,
                        "/option/history/quote",
                        {
                            "symbol": symbol,
                            "expiration": "*",
                            "date": day.isoformat(),
                            "interval": "1m",
                            "max_dte": 14,
                            "strike_range": STRIKE_RANGES[symbol],
                            "format": "csv",
                        },
                    )
                if has_eligible_contract(availability, symbol, day, 60):
                    yield make_task(
                        "pull-2",
                        "quote-dte60-atm10",
                        day,
                        symbol,
                        "/option/history/quote",
                        {
                            "symbol": symbol,
                            "expiration": "*",
                            "date": day.isoformat(),
                            "interval": "1m",
                            "max_dte": 60,
                            "strike_range": 10,
                            "format": "csv",
                        },
                    )


def pull3_tasks(
    days: Iterable[date], availability: dict[tuple[str, date], int]
) -> Iterator[Task]:
    for symbols in (PRIORITY_SYMBOLS, SECONDARY_SYMBOLS):
        for day in days:
            for symbol in symbols:
                if not has_eligible_contract(availability, symbol, day, 7):
                    continue
                yield make_task(
                    "pull-3",
                    "trade-quote-dte7",
                    day,
                    symbol,
                    "/option/history/trade_quote",
                    {
                        "symbol": symbol,
                        "expiration": "*",
                        "date": day.isoformat(),
                        "max_dte": 7,
                        "strike_range": STRIKE_RANGES[symbol],
                        "format": "csv",
                    },
                )


def pull4_tasks(days: Iterable[date]) -> Iterator[Task]:
    """VIX daily OI, followed by its full 60-DTE one-minute surface.

    Keeping the endpoint passes ordered makes each day's OI board available as
    the expiration source if Theta's expiration=* quote path needs fallback.
    """
    materialized_days = tuple(days)
    for day in materialized_days:
        yield make_task(
            "pull-4",
            "open-interest",
            day,
            VIX_SYMBOL,
            "/option/history/open_interest",
            {
                "symbol": VIX_SYMBOL,
                "expiration": "*",
                "date": day.isoformat(),
                "format": "csv",
            },
        )

    for day in materialized_days:
        yield make_task(
            "pull-4",
            "quote-dte60-full-chain",
            day,
            VIX_SYMBOL,
            "/option/history/quote",
            {
                "symbol": VIX_SYMBOL,
                "expiration": "*",
                "date": day.isoformat(),
                "interval": "1m",
                "max_dte": 60,
                "format": "csv",
            },
        )


def parse_et_timestamp(column: str, alias: str) -> pl.Expr:
    return (
        pl.col(column)
        .str.to_datetime(format="%Y-%m-%dT%H:%M:%S%.3f", strict=False)
        .dt.replace_time_zone("America/New_York", ambiguous="earliest", non_existent="null")
        .dt.convert_time_zone("UTC")
        .cast(pl.Datetime("ns", "UTC"))
        .alias(alias)
    )


def normalize(lazy: pl.LazyFrame, task: Task) -> pl.LazyFrame:
    names = set(lazy.collect_schema().names())
    # Theta Terminal terminates successful CSV history responses with one
    # delimiter-only record.  It parses as an all-null row, so remove it before
    # adding request metadata (which would otherwise make the row non-null).
    if "symbol" in names:
        lazy = lazy.filter(pl.col("symbol").is_not_null())
    expressions: list[pl.Expr] = [pl.lit(task.request_date).cast(pl.Date).alias("request_date")]
    drop: list[str] = []

    if "expiration" in names:
        expressions.append(
            pl.col("expiration").str.to_date(format="%Y-%m-%d", strict=False).alias("expiration")
        )

    timestamp_names = {
        "timestamp": "ts_event",
        "trade_timestamp": "ts_event",
        "quote_timestamp": "ts_quote",
        "created": "ts_created",
        "last_trade": "ts_last_trade",
    }
    for source, target in timestamp_names.items():
        if source in names:
            expressions.append(parse_et_timestamp(source, target))
            if source != target:
                drop.append(source)

    if task.kind == "trade-quote-dte7" and "condition" in names:
        expressions.append(
            (~pl.col("condition").is_in(INVALID_VOLUME_CONDITIONS)).alias("valid_for_volume")
        )

    lazy = lazy.with_columns(expressions)
    if drop:
        lazy = lazy.drop(drop)

    if {"symbol", "expiration", "strike", "right"}.issubset(names):
        lazy = lazy.with_columns(
            pl.concat_str(
                [
                    pl.col("symbol").cast(pl.String).str.pad_end(6, " "),
                    pl.col("expiration").dt.strftime("%y%m%d"),
                    pl.col("right").cast(pl.String).str.to_uppercase().str.slice(0, 1),
                    (pl.col("strike") * 1000)
                    .round(0)
                    .cast(pl.Int64)
                    .cast(pl.String)
                    .str.pad_start(8, "0"),
                ]
            ).alias("osi_symbol")
        )
    return lazy


def atomic_sink(lazy: pl.LazyFrame, destination: Path) -> tuple[int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    part = destination.with_suffix(".parquet.part")
    part.unlink(missing_ok=True)
    lazy.sink_parquet(
        part,
        compression="zstd",
        compression_level=1,
        statistics=True,
        row_group_size=250_000,
    )
    rows = int(pl.scan_parquet(part).select(pl.len()).collect().item())
    size = part.stat().st_size
    os.replace(part, destination)
    return rows, size


def write_empty(path: Path, task: Task, reason: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    marker = empty_marker(path)
    marker.write_text(
        json.dumps(
            {
                "status": "empty",
                "pull": task.pull,
                "kind": task.kind,
                "date": task.request_date.isoformat(),
                "reason": reason[:500],
            },
            sort_keys=True,
        )
        + "\n"
    )


def convert_single(downloaded: Downloaded) -> dict:
    task = downloaded.task
    destination = task.outputs[0]
    started = time.perf_counter()
    lazy = pl.scan_csv(downloaded.temp_path, try_parse_dates=False, infer_schema_length=10_000)
    rows, parquet_bytes = atomic_sink(normalize(lazy, task), destination)
    return {
        "rows": rows,
        "parquet_bytes": parquet_bytes,
        "convert_seconds": round(time.perf_counter() - started, 4),
        "outputs": [str(destination)],
    }


def convert_contracts(downloaded: Downloaded) -> dict:
    task = downloaded.task
    started = time.perf_counter()
    frame = pl.read_csv(downloaded.temp_path, try_parse_dates=False, infer_schema_length=10_000)
    output_stats: list[dict] = []
    total_rows = 0
    total_bytes = 0
    for symbol, destination in zip(task.symbols, task.outputs, strict=True):
        subset = frame.filter(pl.col("symbol") == symbol)
        if subset.is_empty():
            write_empty(destination, task, f"No quoted contracts for {symbol}")
            output_stats.append({"symbol": symbol, "rows": 0, "min_dte": None})
            continue
        lazy = normalize(subset.lazy(), task)
        rows, parquet_bytes = atomic_sink(lazy, destination)
        minimum_expiry = subset.select(pl.col("expiration").str.to_date().min()).item()
        minimum_dte = (minimum_expiry - task.request_date).days if minimum_expiry else None
        total_rows += rows
        total_bytes += parquet_bytes
        output_stats.append({"symbol": symbol, "rows": rows, "min_dte": minimum_dte})
    return {
        "rows": total_rows,
        "parquet_bytes": total_bytes,
        "convert_seconds": round(time.perf_counter() - started, 4),
        "outputs": [str(path) for path in task.outputs],
        "contracts": output_stats,
    }


def convert(downloaded: Downloaded) -> dict:
    try:
        if downloaded.task.kind == "contracts":
            return convert_contracts(downloaded)
        return convert_single(downloaded)
    finally:
        downloaded.temp_path.unlink(missing_ok=True)


class Runner:
    def __init__(self, inflight: int, converters: int, retries: int) -> None:
        self.inflight = inflight
        self.converters = converters
        self.retries = retries
        self.manifest_lock = threading.Lock()
        self.completed = 0
        self.skipped = 0
        self.failed = 0
        self.started = time.perf_counter()
        SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
        MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)

    def record(self, task: Task, status: str, **details: object) -> None:
        payload = {
            "recorded_at": datetime.now(tz=NY).isoformat(),
            "status": status,
            "label": task.label,
            "pull": task.pull,
            "kind": task.kind,
            "date": task.request_date.isoformat(),
            "symbols": task.symbols,
            **details,
        }
        manifest = MANIFEST_ROOT / f"thetadata-{task.pull}.jsonl"
        with self.manifest_lock:
            with manifest.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def fallback_expirations(self, task: Task) -> tuple[date, ...]:
        """Return the expirations needed to reproduce one wildcard request."""
        symbol = task.symbols[0]
        candidates = (
            output_path("pull-1", "contracts", symbol, task.request_date),
            output_path(task.pull, "open-interest", symbol, task.request_date),
        )
        source_path = next((path for path in candidates if path.is_file()), None)
        if source_path is None and any(empty_marker(path).is_file() for path in candidates):
            return ()
        if source_path is None:
            raise RuntimeError(
                "cannot split wildcard request; missing contract/expiration source for "
                f"{symbol} {task.request_date}"
            )

        params = dict(task.params)
        max_dte = int(params["max_dte"])
        last_expiration = task.request_date + timedelta(days=max_dte)
        frame = (
            pl.read_parquet(source_path, columns=["expiration"])
            .select(pl.col("expiration").cast(pl.Date).unique().sort())
            .filter(
                pl.col("expiration").is_between(
                    task.request_date, last_expiration, closed="both"
                )
            )
        )
        return tuple(frame.get_column("expiration").to_list())

    async def download_by_expiration(
        self, client: httpx.AsyncClient, task: Task
    ) -> Downloaded | None:
        """Work around Theta's failing expiration=* ClickHouse query path."""
        expirations = self.fallback_expirations(task)
        if not expirations:
            reason = "No eligible expirations in the Pull 1 contract board"
            for output in task.outputs:
                write_empty(output, task, reason)
            self.record(task, "empty", fallback="per-expiration", reason=reason)
            self.completed += 1
            return None

        fd, combined_name = tempfile.mkstemp(
            prefix=f"{task.pull}-{task.kind}-expiration-fallback-",
            suffix=".csv",
            dir=SCRATCH_ROOT,
        )
        os.close(fd)
        combined_path = Path(combined_name)
        started = time.perf_counter()
        response_bytes = 0
        successful_expirations = 0
        header: bytes | None = None

        print(
            f"FALLBACK {task.label}: expiration=* failed; "
            f"fetching {len(expirations)} expirations",
            flush=True,
        )

        try:
            with combined_path.open("wb") as combined:
                for expiration in expirations:
                    params = dict(task.params)
                    params["expiration"] = expiration.isoformat()
                    last_error: Exception | None = None

                    for attempt in range(1, self.retries + 1):
                        fd, part_name = tempfile.mkstemp(
                            prefix=f"{task.pull}-{task.kind}-{expiration}-",
                            suffix=".csv",
                            dir=SCRATCH_ROOT,
                        )
                        os.close(fd)
                        part_path = Path(part_name)
                        try:
                            async with client.stream(
                                "GET", f"{BASE_URL}{task.path}", params=params
                            ) as response:
                                with part_path.open("wb") as part:
                                    async for chunk in response.aiter_bytes(4 * 1024 * 1024):
                                        part.write(chunk)

                                body_size = part_path.stat().st_size
                                if response.status_code == 472:
                                    body = part_path.read_text(errors="replace")[:500]
                                    if body.startswith("No data found"):
                                        last_error = None
                                        break
                                elif response.status_code == 200:
                                    with part_path.open("rb") as part:
                                        part_header = part.readline()
                                        if not part_header:
                                            raise RuntimeError(
                                                f"empty HTTP 200 response for expiration {expiration}"
                                            )
                                        if header is None:
                                            header = part_header
                                            combined.write(part_header)
                                        elif part_header != header:
                                            raise RuntimeError(
                                                f"CSV header changed for expiration {expiration}"
                                            )
                                        shutil.copyfileobj(part, combined, 4 * 1024 * 1024)
                                    response_bytes += body_size
                                    successful_expirations += 1
                                    last_error = None
                                    break
                                else:
                                    body = part_path.read_text(errors="replace")[:500]
                                    raise RuntimeError(
                                        f"HTTP {response.status_code} for expiration "
                                        f"{expiration}: {body}"
                                    )
                        except Exception as exc:
                            last_error = exc
                            if attempt < self.retries:
                                await asyncio.sleep(min(2 ** (attempt - 1), 20))
                        finally:
                            part_path.unlink(missing_ok=True)

                    if last_error is not None:
                        raise last_error

            if successful_expirations == 0:
                reason = "No data found for any eligible expiration"
                for output in task.outputs:
                    write_empty(output, task, reason)
                combined_path.unlink(missing_ok=True)
                self.record(
                    task,
                    "empty",
                    fallback="per-expiration",
                    fallback_expirations=len(expirations),
                    reason=reason,
                )
                self.completed += 1
                return None

            return Downloaded(
                task,
                combined_path,
                response_bytes,
                time.perf_counter() - started,
                fallback_expirations=successful_expirations,
            )
        except Exception:
            combined_path.unlink(missing_ok=True)
            raise

    async def download(self, client: httpx.AsyncClient, task: Task) -> Downloaded | None:
        if all_complete(task):
            self.skipped += 1
            return None

        for attempt in range(1, self.retries + 1):
            fd, temp_name = tempfile.mkstemp(
                prefix=f"{task.pull}-{task.kind}-", suffix=".csv", dir=SCRATCH_ROOT
            )
            os.close(fd)
            temp_path = Path(temp_name)
            started = time.perf_counter()
            try:
                async with client.stream(
                    "GET", f"{BASE_URL}{task.path}", params=dict(task.params)
                ) as response:
                    with temp_path.open("wb") as handle:
                        async for chunk in response.aiter_bytes(4 * 1024 * 1024):
                            handle.write(chunk)
                    elapsed = time.perf_counter() - started
                    size = temp_path.stat().st_size
                    if response.status_code == 200:
                        return Downloaded(task, temp_path, size, elapsed)
                    body = temp_path.read_text(errors="replace")[:500]
                    if response.status_code == 472 and body.startswith("No data found"):
                        for output in task.outputs:
                            write_empty(output, task, body)
                        temp_path.unlink(missing_ok=True)
                        self.record(task, "empty", http_status=472, request_seconds=elapsed)
                        self.completed += 1
                        return None
                    if (
                        response.status_code == 500
                        and body.strip() == "ClickHouse quote query failed"
                        and dict(task.params).get("expiration") == "*"
                    ):
                        temp_path.unlink(missing_ok=True)
                        return await self.download_by_expiration(client, task)
                    raise RuntimeError(f"HTTP {response.status_code}: {body}")
            except Exception as exc:
                temp_path.unlink(missing_ok=True)
                if attempt == self.retries:
                    self.failed += 1
                    self.record(task, "failed", attempt=attempt, error=str(exc))
                    print(f"FAILED {task.label}: {exc}", flush=True)
                    return None
                await asyncio.sleep(min(2 ** (attempt - 1), 20))
        return None

    def progress(self) -> None:
        processed = self.completed + self.skipped + self.failed
        if processed and processed % 100 == 0:
            elapsed = time.perf_counter() - self.started
            rate = processed / elapsed if elapsed else 0.0
            print(
                f"progress processed={processed} completed={self.completed} "
                f"skipped={self.skipped} failed={self.failed} tasks_per_second={rate:.2f}",
                flush=True,
            )

    async def run(self, tasks: Iterable[Task]) -> None:
        task_queue: asyncio.Queue[Task | None] = asyncio.Queue(maxsize=self.inflight * 4)
        conversion_queue: asyncio.Queue[Downloaded | None] = asyncio.Queue(
            maxsize=self.inflight * 2
        )
        limits = httpx.Limits(
            max_connections=self.inflight,
            max_keepalive_connections=self.inflight,
            keepalive_expiry=120,
        )
        timeout = httpx.Timeout(connect=10, read=300, write=300, pool=300)

        async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
            async def producer() -> None:
                for task in tasks:
                    await task_queue.put(task)
                for _ in range(self.inflight):
                    await task_queue.put(None)

            async def downloader() -> None:
                while True:
                    task = await task_queue.get()
                    if task is None:
                        task_queue.task_done()
                        break
                    downloaded = await self.download(client, task)
                    if downloaded is not None:
                        await conversion_queue.put(downloaded)
                    self.progress()
                    task_queue.task_done()

            async def converter() -> None:
                while True:
                    downloaded = await conversion_queue.get()
                    if downloaded is None:
                        conversion_queue.task_done()
                        break
                    try:
                        details = await asyncio.to_thread(convert, downloaded)
                        self.completed += 1
                        self.record(
                            downloaded.task,
                            "downloaded",
                            response_bytes=downloaded.response_bytes,
                            request_seconds=round(downloaded.request_seconds, 4),
                            fallback_expirations=downloaded.fallback_expirations,
                            **details,
                        )
                    except Exception as exc:
                        downloaded.temp_path.unlink(missing_ok=True)
                        self.failed += 1
                        self.record(downloaded.task, "conversion_failed", error=str(exc))
                        print(f"CONVERSION FAILED {downloaded.task.label}: {exc}", flush=True)
                    self.progress()
                    conversion_queue.task_done()

            producer_task = asyncio.create_task(producer())
            downloaders = [asyncio.create_task(downloader()) for _ in range(self.inflight)]
            converters = [asyncio.create_task(converter()) for _ in range(self.converters)]
            await producer_task
            await task_queue.join()
            await asyncio.gather(*downloaders)
            for _ in converters:
                await conversion_queue.put(None)
            await conversion_queue.join()
            await asyncio.gather(*converters)


def cap_tasks(tasks: Iterable[Task], maximum: int | None) -> Iterator[Task]:
    for index, task in enumerate(tasks):
        if maximum is not None and index >= maximum:
            return
        yield task


def task_count(tasks: Iterable[Task]) -> int:
    return sum(1 for _ in tasks)


def completed_history_end() -> date:
    now = datetime.now(tz=NY)
    return now.date() - timedelta(days=1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "run"))
    parser.add_argument(
        "--pull",
        choices=("pull-1", "pull-2", "pull-3", "pull-4", "all"),
        default="all",
    )
    parser.add_argument("--start-date", type=date.fromisoformat)
    parser.add_argument("--end-date", type=date.fromisoformat, default=completed_history_end())
    parser.add_argument("--inflight", type=int, default=16, help="8 active Pro slots + 8 queued")
    parser.add_argument("--converters", type=int, default=8)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--max-tasks", type=int)
    return parser.parse_args()


def build_tasks(pull: str, start: date, end: date, holidays: set[date]) -> Iterable[Task]:
    days = tuple(business_days(start, end, holidays))
    if pull == "pull-1":
        return pull1_tasks(days)
    if pull == "pull-4":
        return pull4_tasks(days)
    availability = load_contract_min_dte()
    if pull == "pull-2":
        return pull2_tasks(days, availability)
    if pull == "pull-3":
        return pull3_tasks(days, availability)
    raise ValueError(pull)


def main() -> int:
    args = parse_args()
    starts = {
        "pull-1": args.start_date or date(2016, 1, 1),
        "pull-2": args.start_date or date(2020, 1, 1),
        "pull-3": args.start_date or date(2020, 1, 1),
        "pull-4": args.start_date or date(2020, 1, 1),
    }
    pulls = ("pull-1", "pull-2", "pull-3", "pull-4") if args.pull == "all" else (args.pull,)
    holidays = fetch_full_holidays(min(starts[p].year for p in pulls), args.end_date.year)

    if args.command == "plan":
        for pull in pulls:
            tasks = cap_tasks(build_tasks(pull, starts[pull], args.end_date, holidays), args.max_tasks)
            print(f"{pull}: {task_count(tasks)} requests")
        return 0

    runner = Runner(args.inflight, args.converters, args.retries)
    for pull in pulls:
        tasks = cap_tasks(build_tasks(pull, starts[pull], args.end_date, holidays), args.max_tasks)
        print(
            f"starting {pull} through {args.end_date} inflight={args.inflight} "
            f"converters={args.converters}",
            flush=True,
        )
        asyncio.run(runner.run(tasks))
    print(
        f"finished completed={runner.completed} skipped={runner.skipped} failed={runner.failed}",
        flush=True,
    )
    return 1 if runner.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
