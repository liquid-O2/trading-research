"""The trade tape itself, for the methods that read order flow rather than
candles, and the range bars built from it.

Sires' charts are 40-range charts with the aggressive orders drawn on them
(Origin of the Move p.7: "a B+ short on the 40-range chart"): a bar is forty
ticks of price, however long that takes, so at the open a minute holds many
bars and at lunch one bar can last many minutes. A one-minute candle cannot
order a squeeze, its failure and the retest when all three happen inside three
minutes of 09:30; the range bar can, because it is built from the trades.

Reads the owned weekly trades files (Databento trades schema: ``t`` event time
in ns, ``price``, ``size``, ``side`` where "B" is a buy aggressor and "A" a
sell aggressor, ``instrument_id``); nothing is written. Files begin 2021-08-30.
"""
from __future__ import annotations

import os
from bisect import bisect_right
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    from numba import njit as _njit
except Exception:  # numba absent: the same loop, interpreted

    def _njit(*_args, **_kwargs):
        def wrap(fn):
            return fn

        return wrap


TRADES = "quantpad/cme__nq-continuous-futures__trades"
_CACHE: OrderedDict = OrderedDict()
_FILES: dict[str, list[str]] = {}


def _files(root: Path) -> list[str]:
    key = str(root)
    if key not in _FILES:
        _FILES[key] = sorted(f for f in os.listdir(root) if f.endswith(".parquet")) if root.is_dir() else []
    return _FILES[key]


def _week(root: Path, name: str, instrument_id: int):
    key = (str(root), name, int(instrument_id))
    if key in _CACHE:
        _CACHE.move_to_end(key)
        return _CACHE[key]
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    table = pq.read_table(root / name, columns=["t", "price", "size", "side", "instrument_id"])
    table = table.filter(pc.equal(table["instrument_id"], int(instrument_id)))
    side = np.asarray(table["side"].to_pylist(), dtype="U1")
    value = (table["t"].to_numpy(), table["price"].to_numpy(), table["size"].to_numpy().astype(np.int64), np.where(side == "B", 1, np.where(side == "A", -1, 0)).astype(np.int8))
    _CACHE[key] = value
    while len(_CACHE) > 3:
        _CACHE.popitem(last=False)
    return value


def trades_between(data_root: str, instrument_id: int, start: int, end: int):
    """(t ns, price, size, aggressor sign) of every trade in [start, end) in
    exchange order; aggressor sign +1 buy, -1 sell, 0 unspecified. None when
    no owned file covers the span."""
    root = Path(data_root) / TRADES
    files = _files(root)
    if not files:
        return None
    stamp = lambda ns: datetime.fromtimestamp(ns / 1e9, timezone.utc).strftime("%Y-%m-%d")
    names = [f[:10] for f in files]
    if names[0] > stamp(end):
        return None
    first = max(0, bisect_right(names, stamp(start)) - 1)
    last = max(0, bisect_right(names, stamp(end)) - 1)
    parts = []
    for name in files[first : last + 1]:
        t, px, size, sign = _week(root, name, instrument_id)
        lo, hi = int(np.searchsorted(t, start, side="left")), int(np.searchsorted(t, end, side="left"))
        if hi > lo:
            parts.append((t[lo:hi], px[lo:hi], size[lo:hi], sign[lo:hi]))
    if not parts:
        return None
    return tuple(np.concatenate([p[i] for p in parts]) for i in range(4))


@_njit(cache=True)
def _range_bar_edges(px, span):  # pragma: no cover - compiled
    """Index of the first trade of each range bar: a trade that would stretch
    the running bar beyond ``span`` opens a new one."""
    n = px.shape[0]
    edges = np.empty(n, dtype=np.int64)
    count = 0
    if n == 0:
        return edges[:0]
    edges[0] = 0
    count = 1
    hi = px[0]
    lo = px[0]
    for i in range(1, n):
        p = px[i]
        new_hi = p if p > hi else hi
        new_lo = p if p < lo else lo
        if new_hi - new_lo > span + 1e-9:
            edges[count] = i
            count += 1
            hi = p
            lo = p
        else:
            hi = new_hi
            lo = new_lo
    return edges[:count]


def range_bars(t, px, size, sign, *, ticks: int = 40, tick: float = 0.25) -> list[dict]:
    """Range bars of ``ticks`` ticks from a trade tape. No price is invented:
    a bar holds the trades whose own high-low range fits the span, and the
    trade that would stretch it opens the next bar. Each bar carries its
    volume and its buy and sell aggressor volume; ``start`` is its first
    trade's time, ``end`` and ``known_at`` its last trade's time plus one
    nanosecond (the bar is known complete only when the next bar opens, which
    is ``next_open_at``; the last bar of a tape is incomplete)."""
    from decimal import Decimal

    px = np.ascontiguousarray(px, dtype=np.float64)
    edges = _range_bar_edges(px, float(ticks) * float(tick))
    out = []
    n = len(px)
    for k, a in enumerate(edges):
        b = int(edges[k + 1]) if k + 1 < len(edges) else n
        a = int(a)
        seg = px[a:b]
        sz = size[a:b]
        sg = sign[a:b]
        complete = k + 1 < len(edges)
        out.append(
            {
                "start": int(t[a]),
                "end": int(t[b - 1]) + 1,
                # the moment the bar is known to be finished: the first trade of the next bar
                "known_at": int(t[b]) if complete else None,
                "complete": complete,
                "O": Decimal(str(seg[0])),
                "H": Decimal(str(seg.max())),
                "L": Decimal(str(seg.min())),
                "C": Decimal(str(seg[-1])),
                "V": int(sz.sum()),
                "buy_volume": int(sz[sg > 0].sum()),
                "sell_volume": int(sz[sg < 0].sum()),
                "trades": int(b - a),
            }
        )
    return out
