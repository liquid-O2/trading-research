"""Numpy window index over QuantPad OHLCV parquet. t is bar-start UTC ms."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

OHLC1M = Path("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1m")
OHLC1S = Path("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1s")
SISTERS_1M = {
    "ES": Path("/workspace/data/quantpad/cme__es-continuous-futures__ohlcv-1m"),
    "YM": Path("/workspace/data/quantpad/cme__ym-continuous-futures__ohlcv-1m"),
    "RTY": Path("/workspace/data/quantpad/cme__rty-continuous-futures__ohlcv-1m"),
}


@dataclass
class BarIndex:
    t: np.ndarray
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    v: np.ndarray
    source: str
    bar_ms: int

    def window(self, start_ms: int, end_ms: int) -> dict:
        i0 = int(np.searchsorted(self.t, start_ms, "left"))
        i1 = int(np.searchsorted(self.t, end_ms, "left"))
        n = i1 - i0
        expected = max(0, (end_ms - start_ms) // self.bar_ms)
        if n <= 0:
            return {
                "n": 0, "expected": expected, "missing": expected,
                "open": None, "high": None, "low": None, "close": None,
                "volume": 0.0, "open_ticks": None, "high_ticks": None,
                "low_ticks": None, "close_ticks": None,
                "t": self.t[0:0], "o": self.o[0:0], "h": self.h[0:0],
                "l": self.l[0:0], "c": self.c[0:0], "v": self.v[0:0],
            }
        sl = slice(i0, i1)
        high = float(self.h[sl].max())
        low = float(self.l[sl].min())
        open_px = float(self.o[i0])
        close_px = float(self.c[i1 - 1])
        return {
            "n": n,
            "expected": expected,
            "missing": max(0, expected - n),
            "open": open_px,
            "high": high,
            "low": low,
            "close": close_px,
            "volume": float(self.v[sl].sum()),
            "open_ticks": int(round(open_px / 0.25)),
            "high_ticks": int(round(high / 0.25)),
            "low_ticks": int(round(low / 0.25)),
            "close_ticks": int(round(close_px / 0.25)),
            "t": self.t[sl],
            "o": self.o[sl],
            "h": self.h[sl],
            "l": self.l[sl],
            "c": self.c[sl],
            "v": self.v[sl],
        }


def _read_year(path: Path) -> BarIndex:
    import pyarrow.parquet as pq
    table = pq.read_table(path, columns=["t", "o", "h", "l", "c", "v"])
    t = table.column("t").to_numpy()
    order = np.argsort(t, kind="mergesort")
    bar_ms = 1000 if "ohlcv-1s" in str(path.parent) else 60_000
    return BarIndex(
        t=t[order].astype(np.int64, copy=False),
        o=table.column("o").to_numpy()[order].astype(np.float64, copy=False),
        h=table.column("h").to_numpy()[order].astype(np.float64, copy=False),
        l=table.column("l").to_numpy()[order].astype(np.float64, copy=False),
        c=table.column("c").to_numpy()[order].astype(np.float64, copy=False),
        v=table.column("v").to_numpy()[order].astype(np.float64, copy=False),
        source=str(path),
        bar_ms=bar_ms,
    )


def load_years(root: Path, years: list[int]) -> BarIndex:
    parts = []
    for year in years:
        path = root / f"{year}.parquet"
        if not path.is_file():
            continue
        parts.append(_read_year(path))
    if not parts:
        raise FileNotFoundError(f"no parquet years {years} under {root}")
    if len(parts) == 1:
        return parts[0]
    t = np.concatenate([p.t for p in parts])
    order = np.argsort(t, kind="mergesort")
    return BarIndex(
        t=t[order],
        o=np.concatenate([p.o for p in parts])[order],
        h=np.concatenate([p.h for p in parts])[order],
        l=np.concatenate([p.l for p in parts])[order],
        c=np.concatenate([p.c for p in parts])[order],
        v=np.concatenate([p.v for p in parts])[order],
        source=",".join(p.source for p in parts),
        bar_ms=parts[0].bar_ms,
    )


def years_for_dates(dates) -> list[int]:
    years = sorted({d.year for d in dates})
    if dates and min(d.month for d in dates if d.year == years[0]) == 1:
        pass
    first = dates[0]
    if first.month == 1 and first.day <= 2:
        years = [first.year - 1, *years] if first.year - 1 not in years else years
    # Asia windows start the prior evening, so include the year before the first date.
    extra = dates[0].year - 1
    if extra not in years:
        years = [extra, *years]
    return years


def from_arrays(t, o, h, l, c, v, *, bar_ms: int, source="fixture") -> BarIndex:
    t = np.asarray(t, dtype=np.int64)
    return BarIndex(
        t=t,
        o=np.asarray(o, dtype=np.float64),
        h=np.asarray(h, dtype=np.float64),
        l=np.asarray(l, dtype=np.float64),
        c=np.asarray(c, dtype=np.float64),
        v=np.asarray(v, dtype=np.float64),
        source=source,
        bar_ms=bar_ms,
    )
