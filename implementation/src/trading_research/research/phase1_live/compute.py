"""Build retained per-session tables for slice F and L."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds
from trading_research.research.phase1_live.ohlc_index import OHLC1M, OHLC1S, load_years, years_for_dates
from trading_research.research.phase1_live.sessions import build_session, prior_rth_window, vol_elapsed_end_ms
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.grid import path_class_from_closes, to_ticks
from trading_research.research.phase1_live import TICK

TABLE_ROOT = Path("/workspace/implementation/reports/phase1-live/_tables")
KEEP = (
    "date", "year", "eligible", "drop_coverage", "failure", "n_1s", "expected_1s",
    "missing_1s", "n_1m_box", "n_1m_outcome", "H", "L", "open", "close", "EQ", "Q25",
    "Q75", "W69", "volume", "close_0859", "open_0930", "w_pct_0859close", "w_pct_0930open",
    "WpriorRTH", "w_rel_prior_rth", "width_bin_pct", "width_bin_rel", "prior_rth_high",
    "prior_rth_low", "asia_high", "asia_low", "london_high", "london_low", "path_class",
    "break_order", "first_high_break_ms", "first_low_break_ms", "judas", "judas_m05",
    "extended", "compressed", "purged", "day_type", "midretrace", "known_at_ns",
    "outcome_start_ns", "leakage", "m05_touch_ms", "m05_side", "reversal_bin",
    "non_touch_m05", "source_bar_ms",
)


def _compact(row: dict) -> dict:
    out = {k: row.get(k) for k in KEEP}
    out["eligible"] = bool(out["eligible"])
    return out


def build_slice(slice_id: str, *, use_1s: bool) -> list[dict]:
    calendar = load_calendar()
    dates = list(slice_dates(calendar, slice_id))
    years = years_for_dates(dates)
    bars_1m = load_years(OHLC1M, years)
    bars_1s = None
    if use_1s:
        s_years = [y for y in years if (OHLC1S / f"{y}.parquet").is_file()]
        if s_years:
            # Year-chunked: load one 1s year at a time inside the session loop via a cache.
            bars_1s = _OneYearCache(OHLC1S)
    rows = []
    prev = None
    for i, day in enumerate(dates):
        prior = prior_rth_window(day, bars_1m, prev, None)
        source_1s = bars_1s.get(day) if bars_1s is not None else None
        row = build_session(day, bars_1m, source_1s, prior_rth=prior)
        rows.append(_compact(row))
        prev = day
        if (i + 1) % 250 == 0:
            print(f"  {slice_id} sessions {i+1}/{len(dates)}", flush=True)
    if bars_1s is not None:
        bars_1s.close()
    return rows


class _OneYearCache:
    def __init__(self, root: Path):
        self.root = root
        self.year = None
        self.bars = None

    def get(self, day: date):
        year = day.year
        if year != self.year:
            path = self.root / f"{year}.parquet"
            if not path.is_file():
                self.year, self.bars = year, None
                return None
            self.bars = load_years(self.root, [year])
            self.year = year
        return self.bars

    def close(self):
        self.bars = None


def add_vol_elapsed(rows: list[dict], slice_id: str) -> list[dict]:
    """Upgrade range.6-9.vol-elapsed from 1m cumulative volume. Causal 60-session median."""
    calendar = load_calendar()
    dates = {d.isoformat(): d for d in slice_dates(calendar, slice_id)}
    years = years_for_dates(list(dates.values()))
    bars = load_years(OHLC1M, years)
    volumes = []
    out = []
    for row in rows:
        day = dates[row["date"]]
        b69 = clock_bounds(day, CLOCKS["range.6-9.published"])
        box = bars.window(b69["start_ms"], b69["end_ms"])
        median = float(np.median(volumes[-60:])) if len(volumes) >= 20 else (float(np.median(volumes)) if volumes else None)
        end_ms = vol_elapsed_end_ms(box, median, b69["start_ms"], b69["end_ms"])
        alt = bars.window(b69["start_ms"], end_ms)
        out_w = bars.window(b69["outcome_start_ms"], b69["outcome_end_ms"])
        failure = alt["high"] is None or alt["low"] is None or alt["high"] <= alt["low"]
        path = {"path_class": None, "break_order": None}
        if not failure and out_w["n"]:
            path = path_class_from_closes(
                to_ticks(out_w["c"]), out_w["t"],
                int(round(alt["high"] / TICK)), int(round(alt["low"] / TICK)),
            )
        volumes.append(box["volume"])
        out.append({
            "date": row["date"],
            "year": row["year"],
            "eligible": row["eligible"] and not failure,
            "path_class": path.get("path_class"),
            "break_order": path.get("break_order"),
            "H": None if failure else alt["high"],
            "L": None if failure else alt["low"],
            "W": None if failure else alt["high"] - alt["low"],
            "end_ms": end_ms,
            "median_volume": median,
            "volume": box["volume"],
            "known_at_ns": end_ms * 1_000_000,
            "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0 if end_ms * 1_000_000 <= row["outcome_start_ns"] else 1,
            "failure": failure,
            "drop_coverage": row["drop_coverage"],
            "missing_1s": row["missing_1s"],
            "non_touch_m05": row["non_touch_m05"],
        })
    return out


def save_rows(name: str, rows: list[dict]) -> Path:
    import pyarrow as pa
    import pyarrow.parquet as pq
    TABLE_ROOT.mkdir(parents=True, exist_ok=True)
    path = TABLE_ROOT / f"{name}.parquet"
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path, compression="zstd")
    return path


def load_rows(name: str) -> list[dict]:
    import pyarrow.parquet as pq
    path = TABLE_ROOT / f"{name}.parquet"
    if not path.is_file():
        return []
    return pq.read_table(path).to_pylist()
