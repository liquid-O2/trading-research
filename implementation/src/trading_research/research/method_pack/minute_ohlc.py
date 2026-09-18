"""The open and close the event-time bars withhold.

An event-time bar withholds its open (``open_order_known`` false) when the
bar's first trades share a timestamp, and its close likewise: the event clock
cannot order them. High, low and volume are always present. On the cash
session 6 to 17 percent of one-minute bars carry a withheld open or close, and
code that dropped such bars lost their highs and lows too (2026-07-08 10:27, a
seventy-point flush, vanished from the Sires mechanics).

The owned trades file is in exchange order, which settles it: on every bar
whose open and close the event clock does know, the first and last trade of
the bar in file order equal them exactly (2021-09-15 375/375 and 370/370,
2024-03-05 377/377 and 376/376, 2026-07-08 357/357 and 353/353), and every
withheld value recomputed this way lies inside the bar's own high-low range.
Before the trades files begin (2021-08-30) the vendor's one-minute OHLCV is
used; it agrees with the known opens and closes on 99.6 to 100 percent of bars
but has missing sessions, so it is the fallback, not the source. Where
neither reaches (the tape's last two sessions) a validated API supplement
beside the data root is the last resort.

Nothing is written. A filled value uses only trades inside the bar, so it is
known at the bar's end like the rest of the bar. Filled bars say so
(``open_source`` / ``close_source``); a value that cannot be recomputed, or
that falls outside the bar's high-low range, stays withheld.
"""
from __future__ import annotations

import os
from bisect import bisect_right
from collections import OrderedDict
from decimal import Decimal
from pathlib import Path

import numpy as np

TRADES = "quantpad/cme__nq-continuous-futures__trades"
VENDOR = "quantpad/cme__nq-continuous-futures__ohlcv-1m"
SUPPLEMENT = "data-supplements/quantpad-api__nq__ohlcv-1m"
WEEK_NS = 7 * 86_400 * 1_000_000_000
_TRADE_CACHE: OrderedDict = OrderedDict()
_VENDOR_CACHE: OrderedDict = OrderedDict()
_FILES: dict[str, list[str]] = {}


def _trade_files(root: Path) -> list[str]:
    key = str(root)
    if key not in _FILES:
        _FILES[key] = sorted(f for f in os.listdir(root) if f.endswith(".parquet")) if root.is_dir() else []
    return _FILES[key]


def _trades(root: Path, name: str, instrument_id: int):
    """(timestamps, prices) of one weekly trades file for one instrument, in file order."""
    key = (str(root), name, int(instrument_id))
    if key in _TRADE_CACHE:
        _TRADE_CACHE.move_to_end(key)
        return _TRADE_CACHE[key]
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    table = pq.read_table(root / name, columns=["t", "price", "instrument_id"])
    table = table.filter(pc.equal(table["instrument_id"], int(instrument_id)))
    value = (table["t"].to_numpy(), table["price"].to_numpy())
    _TRADE_CACHE[key] = value
    while len(_TRADE_CACHE) > 3:
        _TRADE_CACHE.popitem(last=False)
    return value


def _from_trades(data_root: str, instrument_id: int, start: int, end: int):
    """(timestamps, prices) of every trade in [start, end), in exchange order, or None when no file covers it."""
    root = Path(data_root) / TRADES
    files = _trade_files(root)
    if not files:
        return None
    from datetime import datetime, timezone

    def stamp(ns: int) -> str:
        return datetime.fromtimestamp(ns / 1e9, timezone.utc).strftime("%Y-%m-%d")

    names = [f[:10] for f in files]
    first = max(0, bisect_right(names, stamp(start)) - 1)
    last = max(0, bisect_right(names, stamp(end)) - 1)
    if names[first] > stamp(end):
        return None
    ts_parts, px_parts = [], []
    for name in files[first : last + 1]:
        ts, px = _trades(root, name, instrument_id)
        lo, hi = int(np.searchsorted(ts, start, side="left")), int(np.searchsorted(ts, end, side="left"))
        if hi > lo:
            ts_parts.append(ts[lo:hi])
            px_parts.append(px[lo:hi])
    if not ts_parts:
        return None
    return np.concatenate(ts_parts), np.concatenate(px_parts)


def _from_vendor(data_root: str, instrument_id: int, year: int):
    """{minute start ns: (open, close)} of the vendor's one-minute bars for one instrument and year."""
    key = (str(data_root), int(instrument_id), int(year))
    if key in _VENDOR_CACHE:
        return _VENDOR_CACHE[key]
    path = Path(data_root) / VENDOR / f"{year}.parquet"
    value: dict[int, tuple[float, float]] = {}
    if path.is_file():
        import pyarrow.compute as pc
        import pyarrow.parquet as pq

        table = pq.read_table(path, columns=["t", "o", "c", "instrument_id"])
        table = table.filter(pc.equal(table["instrument_id"], int(instrument_id)))
        for t, o, c in zip(table["t"].to_numpy(), table["o"].to_numpy(), table["c"].to_numpy()):
            value[int(t) * 1_000_000] = (float(o), float(c))
    _VENDOR_CACHE[key] = value
    while len(_VENDOR_CACHE) > 4:
        _VENDOR_CACHE.popitem(last=False)
    return value


def _from_supplement(data_root: str, instrument_id: int) -> dict[int, tuple[float, float]]:
    """{minute start ns: (open, close)} from the API supplement beside the data
    root (``data-supplements/quantpad-api__nq__ohlcv-1m/*.csv``; see its README):
    the last resort, for spans neither owned source reaches."""
    key = ("supplement", str(data_root), int(instrument_id))
    if key in _VENDOR_CACHE:
        return _VENDOR_CACHE[key]
    import csv

    value: dict[int, tuple[float, float]] = {}
    root = Path(data_root).parent / SUPPLEMENT
    if root.is_dir():
        for path in sorted(root.glob("*.csv")):
            with path.open() as handle:
                for row in csv.DictReader(handle):
                    if int(row["instrument_id"]) == int(instrument_id):
                        value[int(row["t"]) * 1_000_000] = (float(row["o"]), float(row["c"]))
    _VENDOR_CACHE[key] = value
    return value


def fill_withheld(rows: list[dict], *, data_root: str, instrument_id: int) -> list[dict]:
    """``rows`` with every withheld open and close recomputed where the owned
    data settles it. Rows that need nothing are returned as they are; a filled
    row is a copy."""
    need = [i for i, r in enumerate(rows) if r.get("H") is not None and r.get("L") is not None and (r.get("O") is None or r.get("C") is None)]
    if not need:
        return rows
    span_start = min(int(rows[i]["start"]) for i in need)
    span_end = max(int(rows[i]["end"]) for i in need)
    trades = _from_trades(data_root, instrument_id, span_start, span_end)
    out = list(rows)
    for i in need:
        row = dict(rows[i])
        start, end = int(row["start"]), int(row["end"])
        low, high = float(row["L"]), float(row["H"])
        opened = closed = None
        source = None
        if trades is not None:
            ts, px = trades
            a, b = int(np.searchsorted(ts, start, side="left")), int(np.searchsorted(ts, end, side="left"))
            if b > a:
                opened, closed, source = float(px[a]), float(px[b - 1]), "trades_file_order"
        if source is None and end - start == 60_000_000_000:
            from datetime import datetime, timezone

            vendor = _from_vendor(data_root, instrument_id, datetime.fromtimestamp(start / 1e9, timezone.utc).year).get(start)
            if vendor is not None:
                opened, closed, source = vendor[0], vendor[1], "vendor_ohlcv_1m"
            else:
                extra = _from_supplement(data_root, instrument_id).get(start)
                if extra is not None:
                    opened, closed, source = extra[0], extra[1], "quantpad_api_supplement"
        if source is not None:
            if row.get("O") is None and low <= opened <= high:
                row["O"], row["open_source"] = Decimal(str(opened)), source
            if row.get("C") is None and low <= closed <= high:
                row["C"], row["close_source"] = Decimal(str(closed)), source
        out[i] = row
    return out
