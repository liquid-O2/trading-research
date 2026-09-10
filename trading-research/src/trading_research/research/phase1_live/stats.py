"""Wilson, session bootstrap, paired differences, by-year rows."""

from __future__ import annotations

import math

import numpy as np

BOOTSTRAP_N = 1000
BOOTSTRAP_SEED = 1


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = k / n
    z2 = z * z
    den = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / den
    half = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / den
    return center - half, center + half


def rate_block(k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {
        "k": int(k),
        "n": int(n),
        "rate": None if n <= 0 else k / n,
        "wilson_95": [lo, hi],
    }


def mean_block(values: list[float]) -> dict:
    arr = np.asarray(values, dtype=np.float64)
    n = int(arr.size)
    if n == 0:
        return {"n": 0, "mean": None, "p25": None, "p50": None, "p75": None}
    return {
        "n": n,
        "mean": float(arr.mean()),
        "p25": float(np.percentile(arr, 25)),
        "p50": float(np.percentile(arr, 50)),
        "p75": float(np.percentile(arr, 75)),
    }


def session_bootstrap_rate(flags: np.ndarray, *, n_boot: int = BOOTSTRAP_N, seed: int = BOOTSTRAP_SEED) -> list:
    flags = np.asarray(flags, dtype=np.float64)
    n = int(flags.size)
    if n == 0:
        return [None, None]
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, n, size=(n_boot, n))
    means = flags[draws].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return [float(lo), float(hi)]


def session_bootstrap_mean(values: np.ndarray, *, n_boot: int = BOOTSTRAP_N, seed: int = BOOTSTRAP_SEED) -> list:
    values = np.asarray(values, dtype=np.float64)
    n = int(values.size)
    if n == 0:
        return [None, None]
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, n, size=(n_boot, n))
    means = values[draws].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return [float(lo), float(hi)]


def paired_diff(upgrade: np.ndarray, faithful: np.ndarray) -> dict:
    u = np.asarray(upgrade, dtype=np.float64)
    f = np.asarray(faithful, dtype=np.float64)
    if u.size != f.size:
        raise ValueError("paired difference needs the same sessions")
    d = u - f
    n = int(d.size)
    if n == 0:
        return {"n": 0, "mean": None, "session_bootstrap_95": [None, None]}
    return {
        "n": n,
        "mean": float(d.mean()),
        "session_bootstrap_95": session_bootstrap_mean(d),
    }


def by_year(dates: list[str], flags: np.ndarray) -> dict:
    flags = np.asarray(flags, dtype=np.float64)
    out = {}
    for year in ("2024", "2025", "2026"):
        idx = np.array([d.startswith(year) for d in dates], dtype=bool)
        k = int(flags[idx].sum()) if flags.size else 0
        n = int(idx.sum())
        block = rate_block(k, n)
        block["session_bootstrap_95"] = session_bootstrap_rate(flags[idx]) if n else [None, None]
        out[year] = block
    return out


def status_from_intervals(upgrade_lo, upgrade_hi, faithful_lo, faithful_hi, *, higher_is_better=True) -> str:
    if any(v is None for v in (upgrade_lo, upgrade_hi, faithful_lo, faithful_hi)):
        return "null"
    if upgrade_lo > faithful_hi:
        return "better" if higher_is_better else "worse"
    if upgrade_hi < faithful_lo:
        return "worse" if higher_is_better else "better"
    return "null"
