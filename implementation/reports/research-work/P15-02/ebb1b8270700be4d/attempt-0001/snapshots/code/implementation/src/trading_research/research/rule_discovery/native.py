"""Columnar MarketView over owned native events. Does not edit cache-identity modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping
import math
import os

import numpy as np
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
ROLL_PATH = Path("/workspace/data/derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet")
DATA_ROOT = Path("/workspace/data")
PHASE1_CACHE = Path("/workspace/data/derived/phase1-event-time-v2")

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


def _optional_ticks(value: object) -> int:
    if value is None:
        return 0
    return price_to_ticks(value if isinstance(value, Decimal) else Decimal(str(value)))


def _side_code(row: Mapping[str, Any]) -> int:
    if row.get("action") != "T":
        return SIDE_UNKNOWN
    aggressor = row.get("aggressor")
    if aggressor in ("buy", "B", 1, "1"):
        return SIDE_BUY
    if aggressor in ("sell", "A", -1, "-1"):
        return SIDE_SELL
    side = row.get("side")
    if side == "B":
        return SIDE_BUY
    if side == "A":
        return SIDE_SELL
    return SIDE_UNKNOWN


def decode_rows(rows: Iterable[Mapping[str, Any]], *, start_ns: int, end_ns: int, instrument_id: str) -> SessionArrays:
    t_list: list[int] = []
    price_list: list[int] = []
    size_list: list[int] = []
    side_list: list[int] = []
    action_list: list[int] = []
    bid_list: list[int] = []
    ask_list: list[int] = []
    bid_sz_list: list[int] = []
    ask_sz_list: list[int] = []
    flags_list: list[int] = []
    known_list: list[int] = []
    seq_list: list[int] = []
    trade_list: list[bool] = []
    row_list: list[str] = []
    sources: list[str] = []
    seen_sources: set[str] = set()
    previous: int | None = None
    ooo: list[int] = []
    for index, row in enumerate(rows):
        event_ns = int(row["event_ns"])
        if previous is not None and event_ns < previous:
            ooo.append(index)
        previous = event_ns
        is_trade = str(row.get("action") or "").upper() == "T"
        price = row.get("price")
        size = row.get("executed_size")
        if size is None:
            size = row.get("size") or 0
        t_list.append(event_ns)
        price_list.append(0 if price is None or not is_trade else price_to_ticks(price))
        size_list.append(int(size or 0) if is_trade else 0)
        side_list.append(_side_code(row))
        action_list.append(ACTION_TRADE if is_trade else ACTION_OTHER)
        bid_list.append(_optional_ticks(row.get("bid")))
        ask_list.append(_optional_ticks(row.get("ask")))
        bid_sz_list.append(int(row["bid_size"] or 0) if row.get("bid_size") is not None else 0)
        ask_sz_list.append(int(row["ask_size"] or 0) if row.get("ask_size") is not None else 0)
        flags_list.append(int(row.get("flags") or 0))
        known_list.append(int(row.get("known_at") or event_ns))
        sequence = row.get("exchange_sequence")
        seq_list.append(-1 if sequence is None else int(sequence))
        trade_list.append(is_trade)
        source_file = str(row.get("source_file") or "")
        source_row = row.get("source_row")
        row_list.append(f"{source_file}:{source_row}")
        if source_file and source_file not in seen_sources:
            seen_sources.add(source_file)
            sources.append(memoized_file_digest(source_file) if Path(source_file).is_file() else EMPTY_SHA256)
    count = len(t_list)
    t_ns = np.asarray(t_list, dtype=np.int64)
    batch_starts = np.ones(count, dtype=np.bool_)
    if count:
        batch_starts[1:] = t_ns[1:] != t_ns[:-1]
    return SessionArrays(
        t_ns=t_ns,
        price_ticks=np.asarray(price_list, dtype=np.int64),
        size=np.asarray(size_list, dtype=np.int64),
        side=np.asarray(side_list, dtype=np.int8),
        action=np.asarray(action_list, dtype=np.int8),
        bid_ticks=np.asarray(bid_list, dtype=np.int64),
        ask_ticks=np.asarray(ask_list, dtype=np.int64),
        bid_sz=np.asarray(bid_sz_list, dtype=np.int64),
        ask_sz=np.asarray(ask_sz_list, dtype=np.int64),
        flags=np.asarray(flags_list, dtype=np.int64),
        known_at_ns=np.asarray(known_list, dtype=np.int64),
        exchange_sequence=np.asarray(seq_list, dtype=np.int64),
        is_trade=np.asarray(trade_list, dtype=np.bool_),
        row_id=np.asarray(row_list, dtype=object),
        ooo_index=np.asarray(ooo, dtype=np.int64),
        batch_starts=np.asarray(batch_starts, dtype=np.bool_),
        instrument_id=str(instrument_id),
        start_ns=int(start_ns),
        end_ns=int(end_ns),
        source_sha256=tuple(sources),
    )


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
        raise ContractError("coverage window must be positive")
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


def load_session_arrays(day: date | str, *, full_account_day: bool = True, instrument_id: str | int | None = None) -> tuple[SessionArrays, dict[str, Any], list[Any]]:
    day = date.fromisoformat(day) if isinstance(day, str) else day
    policy = NQSessionPolicy()
    start_ns, end_ns = account_day_window(day, policy=policy) if full_account_day else baseline_feature_window(day)
    selection = contract_selection(day)
    chosen = instrument_id if instrument_id is not None else selection["archive"]["instrument_id"]
    plan = plan_window(DATA_ROOT, start_ns, end_ns, ownership=ownership(str(DATA_ROOT)))
    rows = iter_mbp1_window(plan, trades_only=True, instrument_id=chosen)
    arrays = decode_rows(rows, start_ns=start_ns, end_ns=end_ns, instrument_id=str(chosen))
    return arrays, selection, list(plan.get("unowned_intervals") or [])


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


def build_market_view(day: date | str, *, full_account_day: bool = True, instrument_id: str | int | None = None) -> NativeMarketView:
    day = date.fromisoformat(day) if isinstance(day, str) else day
    arrays, selection, unowned = load_session_arrays(day, full_account_day=full_account_day, instrument_id=instrument_id)
    return NativeMarketView(
        arrays,
        unowned=unowned,
        selection=selection,
        account_day=day.isoformat(),
    )


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
