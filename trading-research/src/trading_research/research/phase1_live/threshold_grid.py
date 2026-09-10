"""Frozen named threshold grid. No session-fitted k. Discovery then score."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live.compute import TABLE_ROOT, load_rows, save_rows
from trading_research.research.phase1_live.stats import by_year, paired_diff, rate_block, session_bootstrap_rate

GRID_PATH = TABLE_ROOT / "threshold_grid.json"
SOURCE = {
    "bigtrade_ny": 100,
    "bigtrade_ldn": 75,
    "cvd_big": 100,
    "cvd_mid_lo": 20,
    "abs_window_min": 2,
    "abs_ticks": 2,
    "abs_reverse_r": 0.25,
    "abs_reverse_min": 15,
    "absB_reload": 0.5,
    "absB_ms": 500,
    "absB_times": 2,
    "iceberg_k": 1.0,
}


def discovery_dates(all_dates: list[str]) -> tuple[list[str], list[str]]:
    """Pre-2024 if present in the table, else first third of F."""
    pre = [d for d in all_dates if d < "2024-01-01"]
    if pre:
        score = [d for d in all_dates if d >= "2024-01-01"]
        return pre, score
    n = len(all_dates)
    cut = max(1, n // 3)
    return all_dates[:cut], all_dates[cut:]


def freeze_size_grid(sizes: np.ndarray) -> dict:
    sizes = np.asarray(sizes, dtype=np.float64)
    sizes = sizes[np.isfinite(sizes) & (sizes > 0)]
    if sizes.size == 0:
        return {"q50": None, "q75": None, "q90": None, "q99": None, "n": 0}
    qs = np.quantile(sizes, [0.5, 0.75, 0.9, 0.99])
    return {"q50": float(qs[0]), "q75": float(qs[1]), "q90": float(qs[2]), "q99": float(qs[3]), "n": int(sizes.size)}


def attach_rv(rows: list[dict]) -> list[dict]:
    vol = {r["date"]: r for r in (load_rows("vol_F") or [])}
    for r in rows:
        v = vol.get(r["date"], {})
        r["rv20"] = v.get("rv20")
        r["vol_tercile_rv"] = v.get("vol_tercile_rv")
    return rows


def slice_blocks(rows: list[dict], flag_key: str) -> dict:
    elig = [r for r in rows if r.get("eligible")]
    flags = np.array([1.0 if r.get(flag_key) else 0.0 for r in elig], dtype=np.float64)
    dates = [r["date"] for r in elig]
    out = {"by_year": by_year(dates, flags)}
    terc = {}
    for name in ("low", "mid", "high"):
        sub = [r for r in elig if r.get("vol_tercile_rv") == name]
        f = np.array([1.0 if r.get(flag_key) else 0.0 for r in sub], dtype=np.float64)
        block = rate_block(int(f.sum()) if f.size else 0, len(sub))
        block["session_bootstrap_95"] = session_bootstrap_rate(f)
        terc[name] = block
    out["by_rv_tercile"] = terc
    return out
