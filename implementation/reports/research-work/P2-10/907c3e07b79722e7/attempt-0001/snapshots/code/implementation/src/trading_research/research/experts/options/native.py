"""Columnar option-chain and spot planes. Integer ticks. No per-row chain loops."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping
import math
import os
import resource
import time

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.contracts.identity import file_digest
from trading_research.research.contracts.types import Coverage, EvidenceRef, require_ns
from trading_research.research.experts.options.instruments import (
    CASH_DAILY,
    DATA_ROOT,
    DATABENTO,
    ES_1M,
    FUTURES_OPTION_ROOTS,
    NQ_1M,
    OPRA_ROOTS,
    PRICE_CENT,
    QQQ_1M,
    REJECT_BOUNDS,
    REJECT_CROSSED,
    REJECT_EXPIRED,
    REJECT_MISSING,
    REJECT_NAMES,
    REJECT_NEGATIVE,
    REJECT_NO_TS,
    REJECT_OK,
    REJECT_STALE,
    REJECT_WIDE,
    REJECT_ZERO_PX,
    REQUIRED_ROOTS,
    RIGHT_CALL,
    SPY_1M,
    STRIKE_MILLI,
    THETA,
    assumed_oi_available_ns,
    expiry_ns,
    parse_osi,
    previous_regular_session,
    root_spec,
    session_file,
    strike_from_millis,
)
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.session_policy import NQSessionPolicy
from trading_research.research.rule_discovery.native import cgroup_worker_count, memoized_file_digest

NS = 1_000_000_000
MINUTE_NS = 60 * NS
QUOTE_AGE_NS = 60 * NS
SPOT_TICK_AGE_NS = 5 * NS
MINUTE_CLOSE_AGE_NS = 120 * NS
SURFACE_MAX_AGE_NS = 10 * 60 * NS
BUCKET_NS = 5 * MINUTE_NS
MS_NS = 1_000_000
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
VIEW_VERSION = "phase2-option-chain-v1"

_DIGEST_MEMO: dict[str, str] = {}


def digest_path(path: Path | str) -> str:
    resolved = str(Path(path).resolve()) if Path(path).exists() else str(path)
    cached = _DIGEST_MEMO.get(resolved)
    if cached is not None:
        return cached
    if not Path(path).is_file():
        _DIGEST_MEMO[resolved] = EMPTY_SHA256
        return EMPTY_SHA256
    value = memoized_file_digest(path)
    _DIGEST_MEMO[resolved] = value
    return value


def peak_rss_bytes() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss = int(usage.ru_maxrss)
    if rss > 10**10:
        return rss
    return rss * 1024


def worker_count() -> int:
    return cgroup_worker_count()


@dataclass(frozen=True, slots=True)
class QuoteArrays:
    t_ns: np.ndarray
    available_at_ns: np.ndarray
    strike_millis: np.ndarray
    right: np.ndarray
    expiry_ns: np.ndarray
    bid_cents: np.ndarray
    ask_cents: np.ndarray
    bid_sz: np.ndarray
    ask_sz: np.ndarray
    osi: np.ndarray
    osi_code: np.ndarray
    source_row: np.ndarray
    source_path: str
    source_sha256: str
    root: str
    day: str


@dataclass(frozen=True, slots=True)
class ContractArrays:
    strike_millis: np.ndarray
    right: np.ndarray
    expiry_ns: np.ndarray
    osi: np.ndarray
    osi_code: np.ndarray
    request_day: str
    source_path: str
    source_sha256: str
    root: str
    available_at_ns: int


@dataclass(frozen=True, slots=True)
class OIArrays:
    strike_millis: np.ndarray
    right: np.ndarray
    expiry_ns: np.ndarray
    oi: np.ndarray
    osi: np.ndarray
    osi_code: np.ndarray
    vendor_ts_ns: np.ndarray
    effective_session: str
    published_at_ns: int
    available_at_ns: int
    publication_policy: str
    is_assumed_clock: bool
    extra_session_available_at_ns: int
    source_path: str
    source_sha256: str
    root: str


@dataclass(frozen=True, slots=True)
class SpotPrint:
    price: Decimal
    event_ns: int
    available_at_ns: int
    source: str
    age_policy: str
    native: bool
    path: str
    sha256: str
    row_id: str


@dataclass(frozen=True, slots=True)
class SnapshotQuotes:
    strike_millis: np.ndarray
    right: np.ndarray
    expiry_ns: np.ndarray
    bid_cents: np.ndarray
    ask_cents: np.ndarray
    mid: np.ndarray
    osi: np.ndarray
    osi_code: np.ndarray
    available_at_ns: np.ndarray
    reject: np.ndarray
    source_row: np.ndarray
    snapshot_end_ns: int
    root: str
    day: str
    source_path: str
    source_sha256: str


def _empty_i64() -> np.ndarray:
    return np.zeros(0, dtype=np.int64)


def _empty_i8() -> np.ndarray:
    return np.zeros(0, dtype=np.int8)


def _empty_obj() -> np.ndarray:
    return np.zeros(0, dtype=object)


def osi_code_from_column(column: pa.Array | pa.ChunkedArray) -> np.ndarray:
    arr = column.combine_chunks() if isinstance(column, pa.ChunkedArray) else column
    encoded = arr.dictionary_encode()
    indices = encoded.indices
    if indices is None:
        return np.zeros(0, dtype=np.int64)
    return np.asarray(indices.to_numpy(), dtype=np.int64)


def osi_code_array(values: np.ndarray) -> np.ndarray:
    return osi_code_from_column(pa.array(values.tolist(), type=pa.string()))


def _expiry_ns_column(spec, expiration: pa.Array) -> np.ndarray:
    unique = pc.unique(expiration).to_pylist()
    table = {item: expiry_ns(spec, item if isinstance(item, date) else date.fromisoformat(str(item)[:10])) for item in unique}
    out = np.empty(expiration.length(), dtype=np.int64)
    for item, ns in table.items():
        mask = pc.equal(expiration, item)
        np.putmask(out, np.asarray(mask.to_numpy(zero_copy_only=False)), ns)
    return out


def _right_column(right: pa.Array) -> np.ndarray:
    text = pc.utf8_upper(pc.cast(right, pa.string()))
    is_call = pc.or_(pc.equal(text, "CALL"), pc.equal(text, "C"))
    is_put = pc.or_(pc.equal(text, "PUT"), pc.equal(text, "P"))
    call = np.asarray(is_call.to_numpy(zero_copy_only=False))
    put = np.asarray(is_put.to_numpy(zero_copy_only=False))
    if not bool(np.all(call | put)):
        raise ContractError("unexpected option right label")
    return np.where(call, RIGHT_CALL, -RIGHT_CALL).astype(np.int8)


def _strike_millis_from_osi(osi: pa.Array) -> np.ndarray:
    field = pc.utf8_slice_codeunits(osi, 13, 21)
    return np.asarray(pc.cast(field, pa.int64()).to_numpy(), dtype=np.int64)


def _cents_from_float(values: np.ndarray) -> np.ndarray:
    scaled = np.asarray(values, dtype=np.float64) * 100.0
    cents = np.rint(scaled)
    ok = np.isfinite(scaled) & (np.abs(scaled - cents) < 1e-6)
    out = np.where(ok, cents, -1).astype(np.int64)
    return out


def _ts_to_ns(column: pa.Array) -> np.ndarray:
    if column.type == pa.int64():
        return column.to_numpy()
    casted = pc.cast(column, pa.int64())
    return np.asarray(casted.to_numpy(), dtype=np.int64)


def _date_col(column: pa.Array) -> list[date]:
    return [item if isinstance(item, date) else date.fromisoformat(str(item)[:10]) for item in column.to_pylist()]


def load_quote_arrays(root: str, day: date, *, kind: str = "quote_dte14") -> QuoteArrays | None:
    spec = root_spec(root)
    path = session_file(spec, kind, day)
    if path is None or not path.is_file():
        return None
    table = pq.read_table(
        path,
        columns=["strike", "right", "expiration", "bid", "ask", "bid_size", "ask_size", "ts_event", "osi_symbol"],
    )
    n = table.num_rows
    if n == 0:
        return QuoteArrays(
            t_ns=_empty_i64(),
            available_at_ns=_empty_i64(),
            strike_millis=_empty_i64(),
            right=_empty_i8(),
            expiry_ns=_empty_i64(),
            bid_cents=_empty_i64(),
            ask_cents=_empty_i64(),
            bid_sz=_empty_i64(),
            ask_sz=_empty_i64(),
            osi=_empty_obj(),
            osi_code=_empty_i64(),
            source_row=_empty_i64(),
            source_path=str(path),
            source_sha256=digest_path(path),
            root=root,
            day=day.isoformat(),
        )
    osi_col = table.column("osi_symbol")
    osi = np.asarray(osi_col.to_pylist(), dtype=object)
    t_ns = _ts_to_ns(table.column("ts_event"))
    bid = np.asarray(table.column("bid").to_numpy(), dtype=np.float64)
    ask = np.asarray(table.column("ask").to_numpy(), dtype=np.float64)
    bid_sz = np.asarray(table.column("bid_size").to_numpy(), dtype=np.int64)
    ask_sz = np.asarray(table.column("ask_size").to_numpy(), dtype=np.int64)
    strike_millis = _strike_millis_from_osi(osi_col)
    right = _right_column(table.column("right"))
    exp_ns = _expiry_ns_column(spec, table.column("expiration"))
    bid_cents = _cents_from_float(bid)
    ask_cents = _cents_from_float(ask)
    available = t_ns + MINUTE_NS
    return QuoteArrays(
        t_ns=t_ns,
        available_at_ns=available,
        strike_millis=strike_millis,
        right=right,
        expiry_ns=exp_ns,
        bid_cents=bid_cents,
        ask_cents=ask_cents,
        bid_sz=bid_sz,
        ask_sz=ask_sz,
        osi=osi,
        osi_code=osi_code_from_column(osi_col),
        source_row=np.arange(n, dtype=np.int64),
        source_path=str(path),
        source_sha256=digest_path(path),
        root=root,
        day=day.isoformat(),
    )


def _cents_unchecked(value: float) -> int:
    if value is None or not np.isfinite(value):
        return -1
    scaled = Decimal(str(float(value))) / PRICE_CENT
    rounded = scaled.to_integral_value()
    if abs(scaled - rounded) > Decimal("1e-8"):
        return -1
    return int(rounded)


def load_contract_arrays(root: str, day: date, *, available_at_ns: int | None = None) -> ContractArrays | None:
    spec = root_spec(root)
    path = session_file(spec, "contracts", day)
    if path is None or not path.is_file():
        return None
    table = pq.read_table(path, columns=["osi_symbol", "expiration", "right", "strike"])
    osi_col = table.column("osi_symbol")
    osi = np.asarray(osi_col.to_pylist(), dtype=object)
    strike_millis = _strike_millis_from_osi(osi_col)
    right = _right_column(table.column("right"))
    exp_ns = _expiry_ns_column(spec, table.column("expiration"))
    if available_at_ns is None:
        available_at_ns = et_ns(day, 17, 0)
    return ContractArrays(
        strike_millis=strike_millis,
        right=right,
        expiry_ns=exp_ns,
        osi=osi,
        osi_code=osi_code_from_column(osi_col),
        request_day=day.isoformat(),
        source_path=str(path),
        source_sha256=digest_path(path),
        root=root,
        available_at_ns=int(available_at_ns),
    )


def load_oi_available_at(root: str, asof_ns: int, *, day: date) -> OIArrays | None:
    """Latest OI whose assumed publication clock is at or before asof."""
    cursor = previous_regular_session(day)
    for _ in range(10):
        if cursor is None:
            return None
        oi = load_oi_arrays(root, cursor)
        if oi is not None and oi.available_at_ns <= asof_ns:
            return oi
        cursor = previous_regular_session(cursor)
    return None


def load_oi_arrays(root: str, effective: date, *, extra_sessions: int = 0) -> OIArrays | None:
    spec = root_spec(root)
    path = session_file(spec, "oi", effective)
    if path is None or not path.is_file():
        return None
    table = pq.read_table(path, columns=["osi_symbol", "open_interest", "ts_event", "request_date", "expiration"])
    osi_col = table.column("osi_symbol")
    osi = np.asarray(osi_col.to_pylist(), dtype=object)
    n = osi.size
    strike_millis = _strike_millis_from_osi(osi_col)
    right_ch = pc.utf8_slice_codeunits(osi_col, 12, 13)
    right = _right_column(right_ch)
    exp_ns = _expiry_ns_column(spec, table.column("expiration"))
    vendor = _ts_to_ns(table.column("ts_event")) if n else _empty_i64()
    available = assumed_oi_available_ns(effective, extra_sessions=0)
    delayed = assumed_oi_available_ns(effective, extra_sessions=1)
    return OIArrays(
        strike_millis=strike_millis,
        right=right,
        expiry_ns=exp_ns,
        oi=np.asarray(table.column("open_interest").to_numpy(), dtype=np.int64),
        osi=osi,
        osi_code=osi_code_from_column(osi_col),
        vendor_ts_ns=vendor,
        effective_session=effective.isoformat(),
        published_at_ns=available,
        available_at_ns=available if extra_sessions == 0 else delayed,
        publication_policy="assumed_next_regular_session_12et",
        is_assumed_clock=True,
        extra_session_available_at_ns=delayed,
        source_path=str(path),
        source_sha256=digest_path(path),
        root=root,
    )


def filename_date_is_not_availability(oi: OIArrays, asof_ns: int, filename_day: date) -> bool:
    """True when the file's date would leak OI before the assumed publication clock."""
    filename_open = et_ns(filename_day, 0, 0)
    if asof_ns >= oi.available_at_ns:
        return True
    return filename_open <= asof_ns < oi.available_at_ns


def quote_reject_codes(
    bid_cents: np.ndarray,
    ask_cents: np.ndarray,
    available_at_ns: np.ndarray,
    expiry_ns_arr: np.ndarray,
    *,
    asof_ns: int,
    session_close_ns: int,
) -> np.ndarray:
    n = bid_cents.size
    code = np.zeros(n, dtype=np.int8)
    missing = (bid_cents < 0) | (ask_cents < 0)
    code = np.where(missing, REJECT_MISSING, code)
    negative = (~missing) & ((bid_cents < 0) | (ask_cents < 0))
    code = np.where(negative, REJECT_NEGATIVE, code)
    crossed = (~missing) & (ask_cents < bid_cents)
    code = np.where(crossed, REJECT_CROSSED, code)
    no_ts = available_at_ns <= 0
    code = np.where(no_ts, REJECT_NO_TS, code)
    age = asof_ns - available_at_ns
    stale = (code == REJECT_OK) & ((age > QUOTE_AGE_NS) | (available_at_ns > asof_ns))
    code = np.where(stale, REJECT_STALE, code)
    bid = bid_cents.astype(np.float64) * 0.01
    ask = ask_cents.astype(np.float64) * 0.01
    mid = 0.5 * (bid + ask)
    spread = ask - bid
    bound = np.maximum(0.05, 0.20 * np.abs(mid))
    wide = (code == REJECT_OK) & (spread > bound)
    code = np.where(wide, REJECT_WIDE, code)
    expired = (code == REJECT_OK) & ((asof_ns >= expiry_ns_arr) | (asof_ns >= session_close_ns) & (expiry_ns_arr <= session_close_ns))
    code = np.where((code == REJECT_OK) & (asof_ns >= expiry_ns_arr), REJECT_EXPIRED, code)
    zero = (code == REJECT_OK) & ((bid_cents == 0) | (ask_cents == 0))
    code = np.where(zero, REJECT_ZERO_PX, code)
    return code


def last_per_osi(mask: np.ndarray, osi_code: np.ndarray, t_ns: np.ndarray) -> np.ndarray:
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return idx
    codes = osi_code[idx]
    times = t_ns[idx]
    order = np.lexsort((times, codes))
    sorted_codes = codes[order]
    sorted_times = times[order]
    change = np.empty(sorted_codes.size, dtype=np.bool_)
    change[0] = True
    change[1:] = sorted_codes[1:] != sorted_codes[:-1]
    starts = np.flatnonzero(change)
    ends = np.append(starts[1:], sorted_codes.size) - 1
    last = idx[order[ends]]
    return last


def same_timestamp_conflict(mask: np.ndarray, osi_code: np.ndarray, t_ns: np.ndarray, bid: np.ndarray, ask: np.ndarray) -> np.ndarray:
    """True at group ends where the last timestamp has conflicting bid/ask for one osi."""
    idx = np.flatnonzero(mask)
    n = osi_code.size
    flag = np.zeros(n, dtype=np.bool_)
    if idx.size == 0:
        return flag
    codes = osi_code[idx]
    times = t_ns[idx]
    order = np.lexsort((times, codes))
    sorted_idx = idx[order]
    sorted_codes = codes[order]
    sorted_times = times[order]
    change = np.empty(sorted_codes.size, dtype=np.bool_)
    change[0] = True
    change[1:] = sorted_codes[1:] != sorted_codes[:-1]
    starts = np.flatnonzero(change)
    ends = np.append(starts[1:], sorted_codes.size) - 1
    for start, end in zip(starts.tolist(), ends.tolist()):
        last_t = int(sorted_times[end])
        members = []
        j = end
        while j >= start and int(sorted_times[j]) == last_t:
            members.append(int(sorted_idx[j]))
            j -= 1
        if len(members) < 2:
            continue
        bids = {int(bid[i]) for i in members}
        asks = {int(ask[i]) for i in members}
        if len(bids) > 1 or len(asks) > 1:
            flag[members] = True
    return flag


def snapshot_quotes(quotes: QuoteArrays, *, snapshot_end_ns: int, session_close_ns: int) -> SnapshotQuotes:
    require_ns("snapshot_end_ns", snapshot_end_ns)
    window = (quotes.available_at_ns > snapshot_end_ns - QUOTE_AGE_NS) & (quotes.available_at_ns <= snapshot_end_ns)
    last = last_per_osi(window, quotes.osi_code, quotes.available_at_ns)
    if last.size == 0:
        empty = SnapshotQuotes(
            strike_millis=_empty_i64(),
            right=_empty_i8(),
            expiry_ns=_empty_i64(),
            bid_cents=_empty_i64(),
            ask_cents=_empty_i64(),
            mid=np.zeros(0, dtype=np.float64),
            osi=_empty_obj(),
            osi_code=_empty_i64(),
            available_at_ns=_empty_i64(),
            reject=_empty_i8(),
            source_row=_empty_i64(),
            snapshot_end_ns=snapshot_end_ns,
            root=quotes.root,
            day=quotes.day,
            source_path=quotes.source_path,
            source_sha256=quotes.source_sha256,
        )
        return empty
    reject = quote_reject_codes(
        quotes.bid_cents[last],
        quotes.ask_cents[last],
        quotes.available_at_ns[last],
        quotes.expiry_ns[last],
        asof_ns=snapshot_end_ns,
        session_close_ns=session_close_ns,
    )
    bid = quotes.bid_cents[last].astype(np.float64) * 0.01
    ask = quotes.ask_cents[last].astype(np.float64) * 0.01
    mid = np.where(reject == REJECT_OK, 0.5 * (bid + ask), np.nan)
    return SnapshotQuotes(
        strike_millis=quotes.strike_millis[last],
        right=quotes.right[last],
        expiry_ns=quotes.expiry_ns[last],
        bid_cents=quotes.bid_cents[last],
        ask_cents=quotes.ask_cents[last],
        mid=mid,
        osi=quotes.osi[last],
        osi_code=quotes.osi_code[last],
        available_at_ns=quotes.available_at_ns[last],
        reject=reject,
        source_row=quotes.source_row[last],
        snapshot_end_ns=snapshot_end_ns,
        root=quotes.root,
        day=quotes.day,
        source_path=quotes.source_path,
        source_sha256=quotes.source_sha256,
    )


def chain_universe(
    root: str,
    day: date,
    asof_ns: int,
    *,
    quotes: QuoteArrays | None = None,
) -> dict[str, Any]:
    """Universe known by asof: prior contracts plus quotes already available. No lookahead."""
    spec = root_spec(root)
    prior = previous_regular_session(day)
    prior_contracts = None if prior is None else load_contract_arrays(root, prior, available_at_ns=et_ns(prior, 17, 0))
    same_day = load_contract_arrays(root, day, available_at_ns=et_ns(day, 17, 0))
    known_codes: set[int] = set()
    known_osi: list[str] = []
    if prior_contracts is not None and prior_contracts.available_at_ns <= asof_ns:
        known_codes.update(int(x) for x in prior_contracts.osi_code.tolist())
        known_osi.extend(str(x) for x in prior_contracts.osi.tolist())
    first_observed = 0
    observed_future = []
    if quotes is not None:
        seen = last_per_osi(quotes.available_at_ns <= asof_ns, quotes.osi_code, quotes.available_at_ns)
        if seen.size:
            prior_codes = np.fromiter(known_codes, dtype=np.int64, count=len(known_codes)) if known_codes else np.zeros(0, dtype=np.int64)
            new_mask = ~np.isin(quotes.osi_code[seen], prior_codes)
            new_idx = seen[new_mask]
            first_observed = int(new_idx.size)
            known_codes.update(int(c) for c in quotes.osi_code[new_idx].tolist())
            known_osi.extend(str(x) for x in quotes.osi[new_idx].tolist())
            observed_future = [
                {"osi": str(quotes.osi[i]), "first_available_at_ns": int(quotes.available_at_ns[i])}
                for i in new_idx[:8].tolist()
            ]
    lookahead = []
    if same_day is not None and same_day.available_at_ns > asof_ns:
        prior_codes = np.fromiter(known_codes, dtype=np.int64, count=len(known_codes)) if known_codes else np.zeros(0, dtype=np.int64)
        extra = ~np.isin(same_day.osi_code, prior_codes)
        lookahead = [str(x) for x in same_day.osi[extra][:8].tolist()]
        lookahead_count = int(np.count_nonzero(extra))
    else:
        lookahead_count = 0
    return {
        "root": root,
        "day": day.isoformat(),
        "asof_ns": asof_ns,
        "prior_contracts_day": None if prior is None else prior.isoformat(),
        "prior_n": 0 if prior_contracts is None else int(prior_contracts.osi.size),
        "universe_n": len(known_codes),
        "same_day_contracts_n": 0 if same_day is None else int(same_day.osi.size),
        "same_day_available_at_ns": None if same_day is None else same_day.available_at_ns,
        "lookahead_strikes_excluded": lookahead,
        "lookahead_excluded_count": lookahead_count,
        "first_observed_intraday_count": first_observed,
        "scoped_quote_kind": spec.quote_dte14_dir,
        "full_chain_kind": spec.contracts_dir,
    }


def load_minute_bars(path: Path, day: date) -> dict[str, np.ndarray] | None:
    year_path = path / f"{day.year}.parquet"
    if not year_path.is_file():
        return None
    start_ms = et_ns(day - timedelta(days=1), 18, 0) // MS_NS
    end_ms = et_ns(day, 17, 0) // MS_NS
    table = pq.read_table(year_path, columns=["t", "o", "h", "l", "c", "v"], filters=[("t", ">=", start_ms), ("t", "<", end_ms)])
    if table.num_rows == 0:
        return None
    t_ms = np.asarray(table.column("t").to_numpy(), dtype=np.int64)
    return {
        "t_ns": t_ms * MS_NS,
        "available_at_ns": t_ms * MS_NS + MINUTE_NS,
        "o": np.asarray(table.column("o").to_numpy(), dtype=np.float64),
        "h": np.asarray(table.column("h").to_numpy(), dtype=np.float64),
        "l": np.asarray(table.column("l").to_numpy(), dtype=np.float64),
        "c": np.asarray(table.column("c").to_numpy(), dtype=np.float64),
        "v": np.asarray(table.column("v").to_numpy(), dtype=np.float64),
        "path": str(year_path),
        "sha256": digest_path(year_path),
    }


def spot_at(root: str, day: date, asof_ns: int) -> SpotPrint | None:
    spec = root_spec(root)
    if spec.underlying_kind == "cash_index":
        return cash_daily_spot(spec.underlying_id, day, asof_ns)
    folder = {"QQQ": QQQ_1M, "SPY": SPY_1M, "NQ": NQ_1M, "ES": ES_1M}.get(spec.underlying_id if spec.underlying_kind == "etf" else spec.root)
    if spec.root in ("NQ", "ES"):
        folder = NQ_1M if spec.root == "NQ" else ES_1M
    if spec.root in ("QQQ", "SPY"):
        folder = QQQ_1M if spec.root == "QQQ" else SPY_1M
    if folder is None:
        return None
    bars = load_minute_bars(folder, day)
    if bars is None:
        return None
    avail = bars["available_at_ns"]
    ok = (avail <= asof_ns) & ((asof_ns - avail) <= MINUTE_CLOSE_AGE_NS)
    if not np.any(ok):
        return None
    i = int(np.flatnonzero(ok)[-1])
    close = bars["c"][i]
    if not np.isfinite(close):
        return None
    return SpotPrint(
        price=Decimal(str(float(close))),
        event_ns=int(bars["t_ns"][i]),
        available_at_ns=int(avail[i]),
        source=spec.spot_intraday,
        age_policy="completed_native_minute_close",
        native=True,
        path=str(bars["path"]),
        sha256=str(bars["sha256"]),
        row_id=f"{bars['path']}:{i}",
    )


def cash_daily_spot(symbol: str, day: date, asof_ns: int) -> SpotPrint | None:
    path = CASH_DAILY / f"{symbol}.parquet"
    if not path.is_file():
        return None
    table = pq.read_table(path, columns=["date", "close"])
    dates = [item.isoformat() if hasattr(item, "isoformat") else str(item)[:10] for item in table.column("date").to_pylist()]
    closes = table.column("close").to_pylist()
    prior = previous_regular_session(day)
    if prior is None:
        return None
    key = prior.isoformat()
    if key not in dates:
        return None
    i = dates.index(key)
    available = et_ns(prior, 16, 0)
    if asof_ns < available:
        return None
    return SpotPrint(
        price=Decimal(str(float(closes[i]))),
        event_ns=available,
        available_at_ns=available,
        source=f"yahoo__cash-daily {symbol} prior close",
        age_policy="daily_cash_not_intraday",
        native=False,
        path=str(path),
        sha256=digest_path(path),
        row_id=f"{path}:{key}",
    )


def coverage_row(root: str, day: date) -> dict[str, Any]:
    spec = root_spec(root)
    oi_path = session_file(spec, "oi", day)
    q_path = session_file(spec, "quote_dte14", day)
    c_path = session_file(spec, "contracts", day)
    eod_path = session_file(spec, "eod", day)
    q60 = session_file(spec, "quote_dte60", day)
    has_oi = bool(oi_path and oi_path.is_file())
    has_q = bool(q_path and q_path.is_file())
    has_c = bool(c_path and c_path.is_file())
    has_eod = bool(eod_path and eod_path.is_file())
    has_q60 = bool(q60 and q60.is_file())
    full_n = 0
    scoped_n = 0
    if has_c:
        full_n = pq.read_metadata(c_path).num_rows
    if has_q:
        scoped_n = pq.read_metadata(q_path).num_rows
    if spec.definition_unparsed:
        dbn = DATABENTO / f"{spec.databento_prefix}__definition"
        disposition = "unsupported_owned_input"
        reason = "databento_dbn_decoder_unavailable"
    elif spec.underlying_kind == "cash_index" and not spec.native_intraday_spot:
        disposition = "complete_observed_scope" if has_oi and has_c else "partial"
        reason = "cash_index_intraday_spot_absent"
    else:
        disposition = "complete_observed_scope" if has_oi and has_q else ("partial" if has_oi or has_q else "missing")
        reason = "ok" if disposition == "complete_observed_scope" else "scoped_or_missing"
    return {
        "root": root,
        "day": day.isoformat(),
        "underlying_id": spec.underlying_id,
        "oi": has_oi,
        "quote_dte14": has_q,
        "quote_dte60": has_q60,
        "contracts": has_c,
        "eod": has_eod,
        "full_chain_rows": full_n,
        "scoped_quote_rows": scoped_n,
        "native_intraday_spot": spec.native_intraday_spot,
        "scoped_feed": bool(spec.quote_dte14_dir),
        "disposition": disposition,
        "reason": reason,
        "oi_path": None if oi_path is None else str(oi_path),
        "quote_path": None if q_path is None else str(q_path),
        "contracts_path": None if c_path is None else str(c_path),
    }


def search_futures_option_inputs(root: str) -> dict[str, Any]:
    spec = root_spec(root)
    prefix = spec.databento_prefix
    found = []
    for schema in ("definition", "statistics", "ohlcv-1m", "trades"):
        folder = DATABENTO / f"{prefix}__{schema}"
        meta = folder / "metadata.json"
        found.append(
            {
                "schema": schema,
                "path": str(folder),
                "exists": folder.is_dir(),
                "metadata": str(meta) if meta.is_file() else None,
                "metadata_sha256": digest_path(meta) if meta.is_file() else None,
                "file_count": 0 if not folder.is_dir() else len(list(folder.glob("*.dbn.zst"))),
            }
        )
    return {
        "root": root,
        "decoder": "unavailable_databento_python_package",
        "owned": found,
        "disposition": "unsupported_owned_input",
    }


def replay_quote_row(path: str, row_index: int) -> dict[str, Any]:
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
    osi = str(raw["osi_symbol"])
    root, expiry, right, millis = parse_osi(osi)
    ts = raw["ts_event"]
    if hasattr(ts, "timestamp"):
        event_ns = int(ts.timestamp() * 1e9)
    else:
        event_ns = int(ts)
    return {
        "kind": "native",
        "path": path,
        "sha256": digest_path(path),
        "row_id": f"{path}:{row_index}",
        "osi": osi,
        "root": root,
        "expiry": expiry.isoformat(),
        "right": right,
        "strike_millis": millis,
        "bid": raw.get("bid"),
        "ask": raw.get("ask"),
        "event_ns": event_ns,
        "available_at_ns": event_ns + MINUTE_NS,
        "synthetic": False,
    }
