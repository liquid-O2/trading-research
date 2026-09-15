"""Columnar MarketView over owned native events. Does not edit cache-identity modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping
import json
import math
import os
import re

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.contracts.identity import digest, file_digest
from trading_research.research.contracts.types import (
    Bar,
    Coverage,
    CoverageReceipt,
    EvidenceRef,
    NativeBatch,
    NativeTrade,
    QuoteBatch,
)
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.event_cache import contract_at, ownership
from trading_research.research.method_pack.mbp1_views import iter_mbp1_window, plan_window
from trading_research.research.method_pack.session_policy import NQSessionPolicy

NS = 1_000_000_000
MINUTE_NS = 60 * NS
TICK = Decimal("0.25")
TICK_FLOAT = 0.25
ACTION_TRADE = 1
ACTION_OTHER = 0
SIDE_BUY = 1
SIDE_SELL = -1
SIDE_UNKNOWN = 0
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIEW_VERSION = "rule-discovery-market-view-v1"
SEAM_OWNERSHIP = "contiguous_when_empty"
ROLL_PATH = Path("/workspace/data/derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet")
DATA_ROOT = Path("/workspace/data")
PHASE1_CACHE = Path("/workspace/data/derived/phase1-event-time-v2")
MONTHLY_PARQUET = re.compile(r"^(\d{4})-(\d{2})\.parquet$")
# Earliest reference-formation clocks consumed by registry input groups, previous-day 18:00 first.
POPULATION_GROUP_CLOCKS = {
    "overnight_range": (-1, 18, 0),
    "prior_session": (-1, 18, 0),
    "asia": (-1, 20, 0),
    "london": (0, 3, 0),
    "tbr_pre": (0, 6, 0),
    "other_session_20": (-1, 20, 0),
    "other_session_00": (0, 0, 0),
    "other_session_03": (0, 3, 0),
    "prior_hour": (0, 8, 30),
    "cash_open": (0, 9, 30),
    "current_session_executions": (-1, 18, 0),
}

_HASH_MEMO: dict[str, str] = {}
_MANIFEST_MEMO: dict[str, str] = {}


def price_to_ticks(price: Decimal | int | str) -> int:
    value = price if isinstance(price, Decimal) else Decimal(str(price))
    quanta = value / TICK
    if quanta != quanta.to_integral_value():
        raise ContractError("price is not an integer NQ tick")
    return int(quanta)


def ticks_to_decimal(ticks: int) -> Decimal:
    return (Decimal(int(ticks)) * TICK).quantize(TICK)


def memoized_file_digest(path: Path | str) -> str:
    resolved = str(Path(path).resolve())
    cached = _HASH_MEMO.get(resolved)
    if cached is not None:
        return cached
    digest_value = file_digest(resolved)
    _HASH_MEMO[resolved] = digest_value
    return digest_value


def memoized_manifest_hash(payload: Mapping[str, Any]) -> str:
    key = digest(payload)
    _MANIFEST_MEMO[key] = key
    return key


def cgroup_worker_count() -> int:
    quota_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    period_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    if quota_path.is_file() and period_path.is_file():
        quota = int(quota_path.read_text().strip())
        period = int(period_path.read_text().strip())
        if quota > 0 and period > 0:
            return max(1, math.floor(quota / period))
    v2 = Path("/sys/fs/cgroup/cpu.max")
    if v2.is_file():
        text = v2.read_text().strip().split()
        if len(text) == 2 and text[0] != "max":
            return max(1, math.floor(int(text[0]) / int(text[1])))
    return max(1, int(os.cpu_count() or 1))


class CacheWriteBlocked(IntegrityError):
    """A cache miss attempted to write under /workspace/data."""


def install_write_guard() -> Any:
    """Raise if build_event_window would write. Cache hits still read."""
    from trading_research.research.method_pack import event_cache, event_time

    def blocked(*_args: Any, **_kwargs: Any) -> Any:
        raise CacheWriteBlocked("build_event_window write guard: cache miss cannot write under /workspace/data")

    event_cache.build_event_window = blocked  # type: ignore[assignment]
    event_time.build_event_window = blocked  # type: ignore[assignment]
    return blocked


@dataclass(frozen=True, slots=True)
class SessionArrays:
    t_ns: np.ndarray
    price_ticks: np.ndarray
    size: np.ndarray
    side: np.ndarray
    action: np.ndarray
    bid_ticks: np.ndarray
    ask_ticks: np.ndarray
    bid_sz: np.ndarray
    ask_sz: np.ndarray
    flags: np.ndarray
    known_at_ns: np.ndarray
    exchange_sequence: np.ndarray
    is_trade: np.ndarray
    row_id: np.ndarray
    ooo_index: np.ndarray
    batch_starts: np.ndarray
    instrument_id: str
    start_ns: int
    end_ns: int
    source_sha256: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MinuteTables:
    minute_ns: np.ndarray
    bar_present: np.ndarray
    observed_complete: np.ndarray
    known_at_ns: np.ndarray
    schedule_open: np.ndarray
    unowned: np.ndarray
    trade_count: np.ndarray
    volume: np.ndarray


@dataclass(frozen=True, slots=True)
class PrefixSums:
    trade_index: np.ndarray
    t_ns: np.ndarray
    pv: np.ndarray
    volume: np.ndarray
    p2v: np.ndarray
    signed: np.ndarray
    unknown: np.ndarray
    ticks: np.ndarray
    size: np.ndarray


def empty_session_arrays(*, start_ns: int, end_ns: int, instrument_id: str) -> SessionArrays:
    """Columnar empty session; no Python row loop."""
    empty_i64 = np.zeros(0, dtype=np.int64)
    empty_i8 = np.zeros(0, dtype=np.int8)
    empty_bool = np.zeros(0, dtype=np.bool_)
    return SessionArrays(
        t_ns=empty_i64,
        price_ticks=empty_i64,
        size=empty_i64,
        side=empty_i8,
        action=empty_i8,
        bid_ticks=empty_i64,
        ask_ticks=empty_i64,
        bid_sz=empty_i64,
        ask_sz=empty_i64,
        flags=empty_i64,
        known_at_ns=empty_i64,
        exchange_sequence=empty_i64,
        is_trade=empty_bool,
        row_id=np.zeros(0, dtype=object),
        ooo_index=empty_i64,
        batch_starts=empty_bool,
        instrument_id=str(instrument_id),
        start_ns=int(start_ns),
        end_ns=int(end_ns),
        source_sha256=(),
    )


def _ticks_from_decimal_column(column: pa.Array) -> np.ndarray:
    """Integer NQ ticks via decimal128 * 4; never Python float arithmetic."""
    n = len(column)
    if n == 0 or column.null_count == n:
        return np.zeros(n, dtype=np.int64)
    decimal_col = pc.cast(column.fill_null(0), pa.decimal128(15, 4))
    scaled = pc.multiply(decimal_col, pa.scalar(4))
    ticks = pc.cast(pc.floor(scaled), pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64, copy=False)
    ticks = np.where(column.is_null().to_numpy(zero_copy_only=False), 0, ticks)
    return ticks


def _map_dictionary(column: pa.Array, mapping: Mapping[str, int], default: int) -> np.ndarray:
    if len(column) == 0:
        return np.zeros(0, dtype=np.int8)
    as_string = pc.cast(column, pa.string())
    values = as_string.to_numpy(zero_copy_only=False)
    out = np.full(len(values), default, dtype=np.int8)
    for token, code in mapping.items():
        out[values == token] = np.int8(code)
    return out


def decode_arrow_table(
    table: pa.Table,
    *,
    start_ns: int,
    end_ns: int,
    instrument_id: str,
    source_file: str,
    row_offsets: np.ndarray,
) -> SessionArrays:
    names = set(table.column_names)
    time_name = "t" if "t" in names else "ts_event"
    times = table.column(time_name)
    if pa.types.is_timestamp(times.type):
        times = times.cast(pa.timestamp("ns", tz=times.type.tz)).cast(pa.int64())
    t_ns = times.to_numpy(zero_copy_only=False).astype(np.int64, copy=False)
    action = _map_dictionary(table.column("action"), {"T": ACTION_TRADE, "t": ACTION_TRADE}, ACTION_OTHER) if "action" in names else np.zeros(t_ns.size, dtype=np.int8)
    is_trade = action == ACTION_TRADE
    side_codes = np.zeros(t_ns.size, dtype=np.int8)
    if "side" in names:
        raw_side = _map_dictionary(table.column("side"), {"B": SIDE_BUY, "A": SIDE_SELL, "1": SIDE_BUY, "-1": SIDE_SELL}, SIDE_UNKNOWN)
        side_codes = np.where(is_trade, raw_side, SIDE_UNKNOWN)
    price_name = "price" if "price" in names else None
    price_ticks = _ticks_from_decimal_column(table.column(price_name)) if price_name else np.zeros(t_ns.size, dtype=np.int64)
    price_ticks = np.where(is_trade, price_ticks, 0)
    size_name = "size" if "size" in names else None
    size = table.column(size_name).fill_null(0).cast(pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64) if size_name else np.zeros(t_ns.size, dtype=np.int64)
    size = np.where(is_trade, size, 0)
    bid_name = "bid_px" if "bid_px" in names else ("bid" if "bid" in names else None)
    ask_name = "ask_px" if "ask_px" in names else ("ask" if "ask" in names else None)
    bid_ticks = _ticks_from_decimal_column(table.column(bid_name)) if bid_name else np.zeros(t_ns.size, dtype=np.int64)
    ask_ticks = _ticks_from_decimal_column(table.column(ask_name)) if ask_name else np.zeros(t_ns.size, dtype=np.int64)
    bid_sz_name = "bid_sz" if "bid_sz" in names else ("bid_size" if "bid_size" in names else None)
    ask_sz_name = "ask_sz" if "ask_sz" in names else ("ask_size" if "ask_size" in names else None)
    bid_sz = table.column(bid_sz_name).fill_null(0).cast(pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64) if bid_sz_name else np.zeros(t_ns.size, dtype=np.int64)
    ask_sz = table.column(ask_sz_name).fill_null(0).cast(pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64) if ask_sz_name else np.zeros(t_ns.size, dtype=np.int64)
    flags = table.column("flags").fill_null(0).cast(pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64) if "flags" in names else np.zeros(t_ns.size, dtype=np.int64)
    known = t_ns
    if "ts_recv" in names:
        recv = table.column("ts_recv")
        if pa.types.is_timestamp(recv.type):
            recv = recv.cast(pa.timestamp("ns", tz=recv.type.tz)).cast(pa.int64())
        recv_ns = recv.fill_null(0).cast(pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64)
        known = np.maximum(t_ns, recv_ns)
    seq = table.column("exchange_sequence").fill_null(-1).cast(pa.int64()).to_numpy(zero_copy_only=False).astype(np.int64) if "exchange_sequence" in names else np.full(t_ns.size, -1, dtype=np.int64)
    file_name = Path(source_file).name
    row_id = np.array([f"{file_name}:{int(offset)}" for offset in row_offsets], dtype=object)
    ooo = np.flatnonzero(t_ns[1:] < t_ns[:-1]) + 1 if t_ns.size else np.zeros(0, dtype=np.int64)
    batch_starts = np.ones(t_ns.size, dtype=np.bool_)
    if t_ns.size:
        batch_starts[1:] = t_ns[1:] != t_ns[:-1]
    source_hash = memoized_file_digest(source_file) if Path(source_file).is_file() else EMPTY_SHA256
    return SessionArrays(
        t_ns=t_ns,
        price_ticks=price_ticks,
        size=size,
        side=side_codes,
        action=action,
        bid_ticks=bid_ticks,
        ask_ticks=ask_ticks,
        bid_sz=bid_sz,
        ask_sz=ask_sz,
        flags=flags,
        known_at_ns=known,
        exchange_sequence=seq,
        is_trade=is_trade.astype(np.bool_),
        row_id=row_id,
        ooo_index=ooo.astype(np.int64),
        batch_starts=batch_starts,
        instrument_id=str(instrument_id),
        start_ns=int(start_ns),
        end_ns=int(end_ns),
        source_sha256=(source_hash,),
    )


def _concat_session_arrays(parts: list[SessionArrays], *, start_ns: int, end_ns: int, instrument_id: str) -> SessionArrays:
    if not parts:
        return empty_session_arrays(start_ns=start_ns, end_ns=end_ns, instrument_id=instrument_id)
    if len(parts) == 1:
        return parts[0]

    def cat(name: str, dtype) -> np.ndarray:
        return np.concatenate([getattr(part, name) for part in parts]).astype(dtype, copy=False)

    t_ns = cat("t_ns", np.int64)
    batch_starts = np.ones(t_ns.size, dtype=np.bool_)
    if t_ns.size:
        batch_starts[1:] = t_ns[1:] != t_ns[:-1]
    ooo = np.flatnonzero(t_ns[1:] < t_ns[:-1]) + 1 if t_ns.size else np.zeros(0, dtype=np.int64)
    sources: list[str] = []
    seen: set[str] = set()
    for part in parts:
        for digest_value in part.source_sha256:
            if digest_value not in seen:
                seen.add(digest_value)
                sources.append(digest_value)
    return SessionArrays(
        t_ns=t_ns,
        price_ticks=cat("price_ticks", np.int64),
        size=cat("size", np.int64),
        side=cat("side", np.int8),
        action=cat("action", np.int8),
        bid_ticks=cat("bid_ticks", np.int64),
        ask_ticks=cat("ask_ticks", np.int64),
        bid_sz=cat("bid_sz", np.int64),
        ask_sz=cat("ask_sz", np.int64),
        flags=cat("flags", np.int64),
        known_at_ns=cat("known_at_ns", np.int64),
        exchange_sequence=cat("exchange_sequence", np.int64),
        is_trade=cat("is_trade", np.bool_),
        row_id=np.concatenate([part.row_id for part in parts]),
        ooo_index=ooo.astype(np.int64),
        batch_starts=batch_starts,
        instrument_id=str(instrument_id),
        start_ns=int(start_ns),
        end_ns=int(end_ns),
        source_sha256=tuple(sources),
    )


def load_span_arrow(
    path: Path,
    start_ns: int,
    end_ns: int,
    *,
    instrument_id: str | int | None,
    trades_only: bool,
) -> tuple[pa.Table, np.ndarray]:
    parquet = pq.ParquetFile(path)
    names = parquet.schema_arrow.names
    field_name = "t" if "t" in names else "ts_event"
    timestamp_index = names.index(field_name)
    native_type = parquet.schema_arrow.field(field_name).type
    factor = {"s": NS, "ms": 1_000_000, "us": 1_000, "ns": 1}.get(getattr(native_type, "unit", "ns"), 1)
    tables: list[pa.Table] = []
    offsets: list[np.ndarray] = []
    row_offset = 0
    wanted = str(instrument_id) if instrument_id is not None else None
    for group in range(parquet.num_row_groups):
        group_rows = parquet.metadata.row_group(group).num_rows
        statistics = parquet.metadata.row_group(group).column(timestamp_index).statistics
        if statistics is not None and statistics.has_min_max:
            lo, hi = statistics.min_raw, statistics.max_raw
            if int(hi) * factor < start_ns or int(lo) * factor >= end_ns:
                row_offset += group_rows
                continue
        batch = parquet.read_row_group(group)
        times = batch.column(field_name)
        if pa.types.is_timestamp(native_type):
            times = times.cast(pa.timestamp("ns", tz=native_type.tz)).cast(pa.int64())
        else:
            times = pc.multiply(times.cast(pa.int64()), factor)
        mask = pc.and_(pc.greater_equal(times, start_ns), pc.less(times, end_ns))
        if trades_only and "action" in names:
            actions = pc.cast(batch.column("action"), pa.string())
            mask = pc.and_(mask, pc.equal(actions, "T"))
        if wanted is not None and "instrument_id" in names:
            inst = pc.cast(batch.column("instrument_id"), pa.string())
            mask = pc.and_(mask, pc.equal(inst, wanted))
        indices = pc.indices_nonzero(mask)
        if len(indices) == 0:
            row_offset += group_rows
            continue
        selected = batch.filter(mask)
        filtered_times = pc.filter(times, mask)
        selected = selected.set_column(timestamp_index, field_name, filtered_times)
        tables.append(selected)
        physical = pc.add(pc.cast(indices, pa.int64()), pa.scalar(row_offset, type=pa.int64()))
        offsets.append(physical.to_numpy(zero_copy_only=False).astype(np.int64))
        row_offset += group_rows
    if not tables:
        empty = parquet.schema_arrow.empty_table()
        return empty, np.zeros(0, dtype=np.int64)
    return pa.concat_tables(tables), np.concatenate(offsets)


def stitch_monthly_seams(plan: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str]:
    spans = sorted(plan.get("owned_spans") or [], key=lambda item: (int(item["start_ns"]), int(item["end_ns"]), str(item["path"])))
    monthly = [span for span in spans if MONTHLY_PARQUET.match(Path(span["path"]).name)]
    seams: list[tuple[int, int]] = []
    for left, right in zip(monthly, monthly[1:]):
        gap_lo, gap_hi = int(left["end_ns"]), int(right["start_ns"])
        if gap_hi > gap_lo:
            seams.append((gap_lo, gap_hi))
    kept: list[dict[str, Any]] = []
    for item in plan.get("unowned_intervals") or []:
        lo, hi = int(item["start_ns"]), int(item["end_ns"])
        if any(lo >= seam_lo and hi <= seam_hi for seam_lo, seam_hi in seams):
            continue
        kept.append(dict(item))
    return kept, SEAM_OWNERSHIP


def earliest_population_start_ns(day: date, required_groups: Iterable[str], *, account_start_ns: int) -> int:
    starts: list[int] = []
    for group in required_groups:
        clock = POPULATION_GROUP_CLOCKS.get(str(group))
        if clock is None:
            continue
        day_offset, hour, minute = clock
        starts.append(et_ns(day + timedelta(days=day_offset), hour, minute))
    if not starts:
        return int(account_start_ns)
    return min(starts)


def population_coverage(
    view: "NativeMarketView",
    *,
    day: date,
    required_groups: Iterable[str],
    end_ns: int | None = None,
) -> CoverageReceipt:
    start_ns = earliest_population_start_ns(day, required_groups, account_start_ns=view.start_ns)
    return view.coverage(start_ns, view.end_ns if end_ns is None else int(end_ns))


def build_prefix_sums(arrays: SessionArrays) -> PrefixSums:
    trade = np.nonzero(arrays.is_trade)[0]
    if trade.size == 0:
        empty = np.zeros(0, dtype=np.int64)
        return PrefixSums(trade, empty, empty, empty, empty, empty, empty, empty, empty)
    ticks = arrays.price_ticks[trade]
    size = arrays.size[trade]
    side = arrays.side[trade].astype(np.int64)
    known = side != 0
    unknown = np.where(known, 0, size)
    signed = np.where(known, side * size, 0)
    pv = ticks * size
    p2v = ticks * ticks * size
    return PrefixSums(
        trade_index=trade,
        t_ns=arrays.t_ns[trade],
        pv=np.cumsum(pv, dtype=np.int64),
        volume=np.cumsum(size, dtype=np.int64),
        p2v=np.cumsum(p2v, dtype=np.int64),
        signed=np.cumsum(signed, dtype=np.int64),
        unknown=np.cumsum(unknown, dtype=np.int64),
        ticks=ticks,
        size=size,
    )


def _window_bounds(times: np.ndarray, start_ns: int, end_ns: int) -> tuple[int, int]:
    left = int(np.searchsorted(times, start_ns, side="left"))
    right = int(np.searchsorted(times, end_ns, side="left"))
    return left, right


def vwap_from_prefix(prefix: PrefixSums, start_ns: int, end_ns: int) -> tuple[Decimal | None, Decimal | None, int]:
    left, right = _window_bounds(prefix.t_ns, start_ns, end_ns)
    if right <= left:
        return None, None, 0
    volume = int(prefix.volume[right - 1] - (prefix.volume[left - 1] if left else 0))
    if volume <= 0:
        return None, None, 0
    pv = int(prefix.pv[right - 1] - (prefix.pv[left - 1] if left else 0))
    p2v = int(prefix.p2v[right - 1] - (prefix.p2v[left - 1] if left else 0))
    mean_ticks = Decimal(pv) / Decimal(volume)
    second = Decimal(p2v) / Decimal(volume)
    variance = second - mean_ticks * mean_ticks
    if variance < 0:
        variance = Decimal(0)
    price = (mean_ticks * TICK).quantize(TICK)
    dispersion = (variance.sqrt() * TICK)
    return price, dispersion, volume


def cvd_from_prefix(prefix: PrefixSums, start_ns: int, end_ns: int) -> tuple[int, int, int]:
    left, right = _window_bounds(prefix.t_ns, start_ns, end_ns)
    if right <= left:
        return 0, 0, 0
    signed = int(prefix.signed[right - 1] - (prefix.signed[left - 1] if left else 0))
    volume = int(prefix.volume[right - 1] - (prefix.volume[left - 1] if left else 0))
    unknown = int(prefix.unknown[right - 1] - (prefix.unknown[left - 1] if left else 0))
    return signed, volume, unknown


def bars_reduceat(arrays: SessionArrays, start_ns: int, end_ns: int, seconds: int) -> list[dict[str, Any]]:
    width = int(seconds) * NS
    if width <= 0 or end_ns <= start_ns:
        return []
    mask = arrays.is_trade & (arrays.t_ns >= start_ns) & (arrays.t_ns < end_ns)
    if not np.any(mask):
        return []
    t_ns = arrays.t_ns[mask]
    ticks = arrays.price_ticks[mask]
    size = arrays.size[mask]
    side = arrays.side[mask]
    known_at = arrays.known_at_ns[mask]
    buckets = (t_ns - start_ns) // width
    order = np.argsort(buckets, kind="stable")
    buckets = buckets[order]
    ticks = ticks[order]
    size = size[order]
    side = side[order]
    known_at = known_at[order]
    t_ns = t_ns[order]
    change = np.empty(buckets.size, dtype=np.bool_)
    change[0] = True
    change[1:] = buckets[1:] != buckets[:-1]
    starts = np.flatnonzero(change)
    open_ticks = ticks[starts]
    high_ticks = np.maximum.reduceat(ticks, starts)
    low_ticks = np.minimum.reduceat(ticks, starts)
    close_idx = np.empty_like(starts)
    close_idx[:-1] = starts[1:] - 1
    close_idx[-1] = ticks.size - 1
    close_ticks = ticks[close_idx]
    volume = np.add.reduceat(size, starts)
    signed = np.add.reduceat(np.where(side != 0, side.astype(np.int64) * size, 0), starts)
    unknown = np.add.reduceat(np.where(side == 0, size, 0), starts)
    known_close = np.maximum.reduceat(known_at, starts)
    rows = []
    for i, start_i in enumerate(starts):
        bucket = int(buckets[start_i])
        bar_start = start_ns + bucket * width
        bar_end = min(bar_start + width, end_ns)
        rows.append(
            {
                "start_ns": int(bar_start),
                "end_ns": int(bar_end),
                "open_ticks": int(open_ticks[i]),
                "high_ticks": int(high_ticks[i]),
                "low_ticks": int(low_ticks[i]),
                "close_ticks": int(close_ticks[i]),
                "volume": int(volume[i]),
                "signed": int(signed[i]),
                "unknown": int(unknown[i]),
                "known_at_ns": max(int(known_close[i]), int(bar_end)),
            }
        )
    return rows


def python_vwap(ticks: list[int], sizes: list[int]) -> tuple[Decimal | None, Decimal | None, int]:
    volume = 0
    pv = 0
    p2v = 0
    for tick, size in zip(ticks, sizes):
        volume += size
        pv += tick * size
        p2v += tick * tick * size
    if volume <= 0:
        return None, None, 0
    mean = Decimal(pv) / Decimal(volume)
    variance = Decimal(p2v) / Decimal(volume) - mean * mean
    if variance < 0:
        variance = Decimal(0)
    return (mean * TICK).quantize(TICK), variance.sqrt() * TICK, volume


def python_bars(events: list[tuple[int, int, int, int, int]], start_ns: int, end_ns: int, seconds: int) -> list[dict[str, Any]]:
    width = seconds * NS
    grouped: dict[int, list[tuple[int, int, int, int]]] = {}
    for event_ns, ticks, size, side, known_at in events:
        if event_ns < start_ns or event_ns >= end_ns:
            continue
        bucket = (event_ns - start_ns) // width
        grouped.setdefault(bucket, []).append((ticks, size, side, known_at))
    rows = []
    for bucket in sorted(grouped):
        members = grouped[bucket]
        bar_start = start_ns + bucket * width
        bar_end = min(bar_start + width, end_ns)
        open_ticks = members[0][0]
        high_ticks = max(item[0] for item in members)
        low_ticks = min(item[0] for item in members)
        close_ticks = members[-1][0]
        volume = sum(item[1] for item in members)
        signed = sum(item[2] * item[1] for item in members if item[2] != 0)
        unknown = sum(item[1] for item in members if item[2] == 0)
        known_at = max(max(item[3] for item in members), bar_end)
        rows.append(
            {
                "start_ns": bar_start,
                "end_ns": bar_end,
                "open_ticks": open_ticks,
                "high_ticks": high_ticks,
                "low_ticks": low_ticks,
                "close_ticks": close_ticks,
                "volume": volume,
                "signed": signed,
                "unknown": unknown,
                "known_at_ns": known_at,
            }
        )
    return rows


def python_cvd(sizes: list[int], sides: list[int]) -> tuple[int, int, int]:
    signed = 0
    volume = 0
    unknown = 0
    for size, side in zip(sizes, sides):
        volume += size
        if side == 0:
            unknown += size
        else:
            signed += side * size
    return signed, volume, unknown


def account_day_window(day: date, *, policy: NQSessionPolicy | None = None) -> tuple[int, int]:
    policy = policy or NQSessionPolicy()
    start = et_ns(day - timedelta(days=1), 18, 0)
    info = policy.day(day)
    if info.get("state") == "early_close" and info.get("rth_end"):
        hour, minute = map(int, str(info["rth_end"]).split(":"))
        end = et_ns(day, hour, minute)
    else:
        end = et_ns(day, 17, 0)
    return start, end


def baseline_feature_window(day: date) -> tuple[int, int]:
    return et_ns(day - timedelta(days=1), 18, 0), et_ns(day, 16, 0)


@lru_cache(maxsize=1)
def _cached_ownership() -> Mapping[str, Any]:
    return ownership(str(DATA_ROOT))


@lru_cache(maxsize=1)
def load_roll_rows() -> tuple[dict[str, Any], ...]:
    table = pq.read_table(ROLL_PATH)
    return tuple(table.to_pylist())


def archive_contract(day: date) -> dict[str, Any]:
    open_ns = et_ns(day - timedelta(days=1), 18, 0)
    return contract_at(str(DATA_ROOT), open_ns)


def causal_contract(day: date) -> dict[str, Any]:
    cutoff = day + timedelta(days=8)
    eligible = []
    for row in load_roll_rows():
        expiry = row["expiration_ts_utc"]
        expiry_day = expiry.date() if hasattr(expiry, "date") else date.fromisoformat(str(expiry)[:10])
        if expiry_day >= cutoff:
            eligible.append((expiry_day, int(row["instrument_id"]), str(row["raw_symbol"]), row))
    if not eligible:
        raise ContractError(f"no unexpired quarterly NQ contract for {day}")
    eligible.sort(key=lambda item: (item[0], item[1]))
    chosen = eligible[0]
    return {
        "instrument_id": chosen[1],
        "raw_symbol": chosen[2],
        "expiry_date": chosen[0].isoformat(),
        "policy": "nearest_unexpired_quarterly_expiry_at_least_8_calendar_days",
        "identity_use": "causal research roll policy, not a tradable forecast",
    }


def contract_selection(day: date) -> dict[str, Any]:
    archive = archive_contract(day)
    causal = causal_contract(day)
    mismatch = str(archive["instrument_id"]) != str(causal["instrument_id"])
    return {
        "account_day": day.isoformat(),
        "archive": {
            "instrument_id": archive["instrument_id"],
            "raw_symbol": archive.get("raw_symbol"),
            "identity_use": archive.get("identity_use"),
        },
        "causal": causal,
        "contract_policy_mismatch": mismatch,
    }


def _unowned_mask(minute_ns: np.ndarray, unowned: list[Any], width: int) -> np.ndarray:
    mask = np.zeros(minute_ns.size, dtype=np.bool_)
    for span in unowned:
        if isinstance(span, dict):
            a, b = span.get("start_ns"), span.get("end_ns")
        else:
            a, b = span
        if a is None or b is None:
            continue
        a, b = int(a), int(b)
        overlap = (minute_ns < b) & ((minute_ns + width) > a)
        mask |= overlap
    return mask


def build_minute_tables(arrays: SessionArrays, *, policy: NQSessionPolicy, unowned: list[Any]) -> MinuteTables:
    start = arrays.start_ns // MINUTE_NS * MINUTE_NS
    end = ((arrays.end_ns + MINUTE_NS - 1) // MINUTE_NS) * MINUTE_NS
    minutes = np.arange(start, end, MINUTE_NS, dtype=np.int64)
    present = np.zeros(minutes.size, dtype=np.bool_)
    complete = np.zeros(minutes.size, dtype=np.bool_)
    known = np.zeros(minutes.size, dtype=np.int64)
    counts = np.zeros(minutes.size, dtype=np.int64)
    volume = np.zeros(minutes.size, dtype=np.int64)
    if arrays.t_ns.size:
        trade_mask = arrays.is_trade
        buckets = (arrays.t_ns[trade_mask] - start) // MINUTE_NS
        valid = (buckets >= 0) & (buckets < minutes.size)
        buckets = buckets[valid]
        if buckets.size:
            counts = np.bincount(buckets, minlength=minutes.size)
            volume = np.bincount(buckets, weights=arrays.size[trade_mask][valid], minlength=minutes.size).astype(np.int64)
            present = counts > 0
            known_vals = arrays.known_at_ns[trade_mask][valid]
            order = np.argsort(buckets, kind="stable")
            sorted_b = buckets[order]
            sorted_k = known_vals[order]
            change = np.empty(sorted_b.size, dtype=np.bool_)
            change[0] = True
            change[1:] = sorted_b[1:] != sorted_b[:-1]
            starts = np.flatnonzero(change)
            max_k = np.maximum.reduceat(sorted_k, starts)
            known[sorted_b[starts]] = max_k
            complete = present & (known <= minutes + MINUTE_NS)
    schedule = np.zeros(minutes.size, dtype=np.bool_)
    for i, minute in enumerate(minutes.tolist()):
        state = policy.state(int(minute), int(minute) + MINUTE_NS)
        schedule[i] = state == "scheduled_open"
    unowned_mask = _unowned_mask(minutes, unowned, MINUTE_NS)
    return MinuteTables(
        minute_ns=minutes,
        bar_present=present,
        observed_complete=complete,
        known_at_ns=known,
        schedule_open=schedule,
        unowned=unowned_mask,
        trade_count=counts,
        volume=volume,
    )


def coverage_from_minutes(tables: MinuteTables, start_ns: int, end_ns: int, *, calendar_sha256: str, evidence: EvidenceRef) -> CoverageReceipt:
    if end_ns <= start_ns:
        closed = int(start_ns)
        window_evidence = EvidenceRef(
            artifact_sha256=evidence.artifact_sha256,
            row_ids=evidence.row_ids,
            event_start_ns=closed,
            event_end_ns=closed,
            available_at_ns=closed,
            coverage=Coverage.MISSING,
            limitation_ids=tuple(dict.fromkeys([*evidence.limitation_ids, "zero_length_or_unobservable"])),
        )
        return CoverageReceipt(
            start_ns=closed,
            end_ns=closed,
            status=Coverage.MISSING,
            expected_matching_intervals=(),
            observed_intervals=(),
            missing_intervals=(),
            calendar_sha256=calendar_sha256,
            evidence=(window_evidence,),
        )
    left = int(np.searchsorted(tables.minute_ns, start_ns // MINUTE_NS * MINUTE_NS, side="left"))
    right = int(np.searchsorted(tables.minute_ns, end_ns, side="left"))
    expected: list[tuple[int, int]] = []
    observed: list[tuple[int, int]] = []
    missing: list[tuple[int, int]] = []
    for i in range(left, right):
        lo = max(int(tables.minute_ns[i]), start_ns)
        hi = min(int(tables.minute_ns[i]) + MINUTE_NS, end_ns)
        if hi <= lo:
            continue
        if not tables.schedule_open[i]:
            continue
        expected.append((lo, hi))
        unknown = bool(tables.unowned[i]) or not bool(tables.observed_complete[i]) or lo != int(tables.minute_ns[i]) or hi != int(tables.minute_ns[i]) + MINUTE_NS
        if unknown:
            missing.append((lo, hi))
        else:
            observed.append((lo, hi))
    if not expected:
        status = Coverage.MISSING
    elif missing:
        status = Coverage.PARTIAL
    else:
        status = Coverage.COMPLETE
    window_evidence = EvidenceRef(
        artifact_sha256=evidence.artifact_sha256,
        row_ids=evidence.row_ids,
        event_start_ns=start_ns,
        event_end_ns=end_ns,
        available_at_ns=end_ns,
        coverage=status,
        limitation_ids=evidence.limitation_ids,
    )
    return CoverageReceipt(
        start_ns=start_ns,
        end_ns=end_ns,
        status=status,
        expected_matching_intervals=tuple(expected),
        observed_intervals=tuple(observed),
        missing_intervals=tuple(missing),
        calendar_sha256=calendar_sha256,
        evidence=(window_evidence,),
    )


def load_session_arrays(
    day: date | str,
    *,
    full_account_day: bool = True,
    instrument_id: str | int | None = None,
    timing: dict[str, float] | None = None,
) -> tuple[SessionArrays, dict[str, Any], list[Any], str]:
    day = date.fromisoformat(day) if isinstance(day, str) else day
    policy = NQSessionPolicy()
    start_ns, end_ns = account_day_window(day, policy=policy) if full_account_day else baseline_feature_window(day)
    selection = contract_selection(day)
    chosen = instrument_id if instrument_id is not None else selection["archive"]["instrument_id"]
    import time as time_mod

    started = time_mod.monotonic()
    plan = plan_window(DATA_ROOT, start_ns, end_ns, ownership=_cached_ownership())
    unowned, seam_rule = stitch_monthly_seams(plan)
    plan_seconds = time_mod.monotonic() - started
    started = time_mod.monotonic()
    parts: list[SessionArrays] = []
    for span in plan.get("owned_spans") or []:
        path = Path(span["path"])
        table, offsets = load_span_arrow(
            path,
            int(span["start_ns"]),
            int(span["end_ns"]),
            instrument_id=chosen,
            trades_only=True,
        )
        if table.num_rows == 0:
            continue
        parts.append(
            decode_arrow_table(
                table,
                start_ns=start_ns,
                end_ns=end_ns,
                instrument_id=str(chosen),
                source_file=str(path),
                row_offsets=offsets,
            )
        )
    arrays = _concat_session_arrays(parts, start_ns=start_ns, end_ns=end_ns, instrument_id=str(chosen))
    decode_seconds = time_mod.monotonic() - started
    if timing is not None:
        timing["plan_seconds"] = plan_seconds
        timing["decode_seconds"] = decode_seconds
    return arrays, selection, unowned, seam_rule


class NativeMarketView:
    def __init__(
        self,
        arrays: SessionArrays,
        *,
        policy: NQSessionPolicy | None = None,
        unowned: list[Any] | None = None,
        selection: Mapping[str, Any] | None = None,
        account_day: str | None = None,
    ) -> None:
        self.arrays = arrays
        self.policy = policy or NQSessionPolicy()
        self.unowned = list(unowned or [])
        self.selection = dict(selection or {})
        self.account_day = account_day or ""
        self.seam_ownership = SEAM_OWNERSHIP
        self.prefix = build_prefix_sums(arrays)
        self.minutes = build_minute_tables(arrays, policy=self.policy, unowned=self.unowned)
        self.calendar_sha256 = self.policy.sha256
        self.asset_id = f"NQ:{arrays.instrument_id}"
        self.start_ns = arrays.start_ns
        self.end_ns = arrays.end_ns
        source = arrays.source_sha256[0] if arrays.source_sha256 else EMPTY_SHA256
        self._evidence = EvidenceRef(
            artifact_sha256=source,
            row_ids=(),
            event_start_ns=arrays.start_ns,
            event_end_ns=arrays.end_ns,
            available_at_ns=arrays.end_ns,
            coverage=Coverage.COMPLETE if arrays.t_ns.size else Coverage.MISSING,
            limitation_ids=() if arrays.ooo_index.size == 0 else ("out_of_order_timestamps",),
        )

    def executions(self, start_ns: int, end_ns: int) -> Iterator[NativeBatch]:
        if end_ns <= start_ns:
            return
            yield
        arrays = self.arrays
        left = int(np.searchsorted(arrays.t_ns, start_ns, side="left"))
        right = int(np.searchsorted(arrays.t_ns, end_ns, side="left"))
        i = left
        while i < right:
            if not bool(arrays.is_trade[i]):
                i += 1
                continue
            event_ns = int(arrays.t_ns[i])
            j = i + 1
            while j < right and int(arrays.t_ns[j]) == event_ns:
                j += 1
            trades = []
            sequences = []
            available = event_ns
            for k in range(i, j):
                if not bool(arrays.is_trade[k]):
                    continue
                available = max(available, int(arrays.known_at_ns[k]))
                sequences.append(int(arrays.exchange_sequence[k]))
                side = int(arrays.side[k])
                aggressor = None if side == 0 else side
                row_id = str(arrays.row_id[k])
                evidence = EvidenceRef(
                    artifact_sha256=self._evidence.artifact_sha256,
                    row_ids=(row_id,),
                    event_start_ns=event_ns,
                    event_end_ns=event_ns,
                    available_at_ns=int(arrays.known_at_ns[k]),
                    coverage=Coverage.COMPLETE,
                    limitation_ids=(),
                )
                trades.append(
                    NativeTrade(
                        event_id=row_id,
                        asset_id=self.asset_id,
                        event_ns=event_ns,
                        available_at_ns=int(arrays.known_at_ns[k]),
                        price=ticks_to_decimal(int(arrays.price_ticks[k])),
                        quantity=int(arrays.size[k]),
                        aggressor=aggressor,
                        evidence=evidence,
                    )
                )
            if trades:
                unique = [s for s in sequences if s >= 0]
                ordered = len(unique) == len(sequences) and len(set(unique)) == len(unique)
                yield NativeBatch(
                    batch_id=f"{self.arrays.instrument_id}:{event_ns}",
                    event_ns=event_ns,
                    available_at_ns=available,
                    trades=tuple(trades),
                    internal_order_known=bool(ordered),
                )
            i = j

    def quotes(self, start_ns: int, end_ns: int) -> Iterator[QuoteBatch]:
        arrays = self.arrays
        left = int(np.searchsorted(arrays.t_ns, start_ns, side="left"))
        right = int(np.searchsorted(arrays.t_ns, end_ns, side="left"))
        i = left
        while i < right:
            event_ns = int(arrays.t_ns[i])
            j = i + 1
            while j < right and int(arrays.t_ns[j]) == event_ns:
                j += 1
            last = j - 1
            bid_ticks = {int(arrays.bid_ticks[k]) for k in range(i, j) if int(arrays.bid_ticks[k])}
            ask_ticks = {int(arrays.ask_ticks[k]) for k in range(i, j) if int(arrays.ask_ticks[k])}
            ambiguous = len(bid_ticks) > 1 or len(ask_ticks) > 1
            available = max(int(arrays.known_at_ns[k]) for k in range(i, j))
            row_id = str(arrays.row_id[last])
            evidence = EvidenceRef(
                artifact_sha256=self._evidence.artifact_sha256,
                row_ids=(row_id,),
                event_start_ns=event_ns,
                event_end_ns=event_ns,
                available_at_ns=available,
                coverage=Coverage.AMBIGUOUS if ambiguous else Coverage.COMPLETE,
                limitation_ids=("ambiguous_bbo_batch",) if ambiguous else (),
            )
            bid = ticks_to_decimal(int(arrays.bid_ticks[last])) if int(arrays.bid_ticks[last]) else None
            ask = ticks_to_decimal(int(arrays.ask_ticks[last])) if int(arrays.ask_ticks[last]) else None
            yield QuoteBatch(
                batch_id=f"quote:{self.arrays.instrument_id}:{event_ns}",
                asset_id=self.asset_id,
                event_ns=event_ns,
                available_at_ns=available,
                bid=bid,
                ask=ask,
                bid_size=int(arrays.bid_sz[last]) or None,
                ask_size=int(arrays.ask_sz[last]) or None,
                ambiguous=ambiguous,
                evidence=(evidence,),
            )
            i = j

    def coverage(self, start_ns: int, end_ns: int) -> CoverageReceipt:
        return coverage_from_minutes(
            self.minutes,
            start_ns,
            end_ns,
            calendar_sha256=self.calendar_sha256,
            evidence=self._evidence,
        )

    def completed_bars(self, start_ns: int, end_ns: int, seconds: int) -> tuple[Bar, ...]:
        rows = bars_reduceat(self.arrays, start_ns, end_ns, seconds)
        bars = []
        for row in rows:
            coverage = self.coverage(row["start_ns"], row["end_ns"])
            status = coverage.status
            evidence = EvidenceRef(
                artifact_sha256=self._evidence.artifact_sha256,
                row_ids=self._evidence.row_ids,
                event_start_ns=row["start_ns"],
                event_end_ns=row["end_ns"],
                available_at_ns=row["known_at_ns"],
                coverage=status,
                limitation_ids=self._evidence.limitation_ids,
            )
            bars.append(
                Bar(
                    bar_id=f"{VIEW_VERSION}:{self.arrays.instrument_id}:{row['start_ns']}:{row['end_ns']}",
                    asset_id=self.asset_id,
                    start_ns=row["start_ns"],
                    end_ns=row["end_ns"],
                    available_at_ns=row["known_at_ns"],
                    open=ticks_to_decimal(row["open_ticks"]),
                    high=ticks_to_decimal(row["high_ticks"]),
                    low=ticks_to_decimal(row["low_ticks"]),
                    close=ticks_to_decimal(row["close_ticks"]),
                    volume=row["volume"],
                    known_signed_volume=row["signed"],
                    unknown_aggressor_volume=row["unknown"],
                    coverage=status,
                    evidence=(evidence,),
                )
            )
        return tuple(bars)

    def vwap(self, start_ns: int, end_ns: int) -> dict[str, Any]:
        price, dispersion, volume = vwap_from_prefix(self.prefix, start_ns, end_ns)
        return {"price": price, "dispersion": dispersion, "volume": volume, "coverage": self.coverage(start_ns, end_ns)}

    def cvd(self, start_ns: int, end_ns: int) -> dict[str, Any]:
        signed, volume, unknown = cvd_from_prefix(self.prefix, start_ns, end_ns)
        return {"delta": signed, "volume": volume, "unknown": unknown}

    def source_formation_volume(self, start_ns: int, end_ns: int) -> dict[str, Any]:
        """Executed volume of a source formation window on this view."""
        bars = self.completed_bars(start_ns, end_ns, 60)
        volume = int(sum(int(bar.volume) for bar in bars))
        available = max((int(bar.available_at_ns) for bar in bars), default=int(end_ns))
        return {
            "volume": volume,
            "bar_count": len(bars),
            "availability_clock_ns": available,
            "start_ns": int(start_ns),
            "end_ns": int(end_ns),
            "instrument_id": self.arrays.instrument_id,
            "account_day": self.account_day,
        }

    def prior_complete_same_contract_dates(self, n: int = 20) -> list[str]:
        """Prior complete same-contract sessions, newest last. Does not load their tapes."""
        return prior_complete_same_contract_dates(self.account_day, n=n, instrument_id=self.arrays.instrument_id)

    def prior_session_views(self, n: int = 20) -> list["NativeMarketView"]:
        """Load prior complete same-contract session views. Array-first per session."""
        dates = self.prior_complete_same_contract_dates(n)
        return [
            build_market_view(item, full_account_day=True, instrument_id=self.arrays.instrument_id)
            for item in dates
        ]


def _engineering_complete_dates() -> list[str]:
    path = Path("/workspace/implementation/reports/research-work/P15-00/ea9693217cb577cb/attempt-0001/ENGINEERING_DATES.json")
    document = json.loads(path.read_text())
    return [row["date"] for row in document.get("classified_dates", []) if row.get("status") == "complete"]


def prior_complete_same_contract_dates(day: date | str, n: int = 20, instrument_id: str | int | None = None) -> list[str]:
    """Complete same-contract sessions strictly before day, newest last, at most n."""
    day = date.fromisoformat(day) if isinstance(day, str) else day
    wanted = str(instrument_id) if instrument_id is not None else str(contract_selection(day)["archive"]["instrument_id"])
    out: list[str] = []
    for item in _engineering_complete_dates():
        if item >= day.isoformat():
            continue
        prior_day = date.fromisoformat(item)
        inst = str(contract_selection(prior_day)["archive"]["instrument_id"])
        if inst != wanted:
            continue
        out.append(item)
    return out[-int(n) :]


def build_market_view(
    day: date | str,
    *,
    full_account_day: bool = True,
    instrument_id: str | int | None = None,
    timing: dict[str, float] | None = None,
) -> NativeMarketView:
    day = date.fromisoformat(day) if isinstance(day, str) else day
    arrays, selection, unowned, seam_rule = load_session_arrays(
        day,
        full_account_day=full_account_day,
        instrument_id=instrument_id,
        timing=timing,
    )
    view = NativeMarketView(
        arrays,
        unowned=unowned,
        selection=selection,
        account_day=day.isoformat(),
    )
    view.seam_ownership = seam_rule
    return view


def replay_native_row(source_path: str, row_index: int) -> dict[str, Any]:
    path = Path(source_path)
    table = pq.ParquetFile(path)
    remaining = row_index
    raw = None
    for group_index in range(table.num_row_groups):
        group = table.read_row_group(group_index)
        if remaining < group.num_rows:
            raw = group.slice(remaining, 1).to_pylist()[0]
            break
        remaining -= group.num_rows
    if raw is None:
        raise IntegrityError(f"row {row_index} missing from {path}")
    from trading_research.research.method_pack.adapters import normalize_mbp1_row
    from trading_research.research.method_pack.mbp1_views import DATASET

    row = normalize_mbp1_row(raw, dataset_id=DATASET, source_file=str(path), source_row=row_index)
    digest_value = memoized_file_digest(path)
    return {
        "kind": "native",
        "source_path": str(path),
        "source_sha256": digest_value,
        "row_id": f"{path}:{row_index}",
        "event_ns": row["event_ns"],
        "available_at_ns": row["known_at"],
        "price": None if row["price"] is None else str(row["price"]),
        "instrument_id": row["instrument_id"],
        "adapter": "trading_research.research.method_pack.adapters.normalize_mbp1_row",
        "row": row,
    }
