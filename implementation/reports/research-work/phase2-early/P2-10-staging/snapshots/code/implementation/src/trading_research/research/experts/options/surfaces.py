"""ATM, 25-delta, and total-variance term features. No extrapolation."""

from __future__ import annotations

from typing import Any

import numpy as np

from trading_research.errors import ContractError


def nearest_atm_iv(log_moneyness: np.ndarray, spread: np.ndarray, strike: np.ndarray, iv: np.ndarray) -> dict[str, Any]:
    """Nearest ATM by min abs(log(K/F)); ties tighter spread then lower strike."""
    if iv.size == 0:
        return {"iv": None, "index": None, "status": "unavailable"}
    abs_m = np.abs(log_moneyness)
    order = np.lexsort((strike, spread, abs_m))
    i = int(order[0])
    if not np.isfinite(iv[i]):
        return {"iv": None, "index": None, "status": "unavailable"}
    return {"iv": float(iv[i]), "index": i, "status": "ok", "strike": float(strike[i])}


def interpolate_delta_iv(abs_delta: np.ndarray, iv: np.ndarray, target: float = 0.25) -> dict[str, Any]:
    """Linear interpolation in absolute delta between bracketing strikes. No extrapolation."""
    ok = np.isfinite(abs_delta) & np.isfinite(iv)
    if np.count_nonzero(ok) < 2:
        return {"iv": None, "status": "unavailable"}
    x = abs_delta[ok]
    y = iv[ok]
    order = np.argsort(x)
    x = x[order]
    y = y[order]
    below = x <= target
    above = x >= target
    if not np.any(below) or not np.any(above):
        return {"iv": None, "status": "no_bracket"}
    i = int(np.flatnonzero(below)[-1])
    j = int(np.flatnonzero(above)[0])
    if i == j:
        return {"iv": float(y[i]), "status": "ok"}
    w = (target - x[i]) / (x[j] - x[i])
    return {"iv": float(y[i] + w * (y[j] - y[i])), "status": "ok"}


def risk_reversal_butterfly(atm: float | None, call25: float | None, put25: float | None) -> dict[str, Any]:
    if atm is None or call25 is None or put25 is None:
        return {"rr": None, "bf": None, "status": "unavailable"}
    return {"rr": call25 - put25, "bf": 0.5 * (call25 + put25) - atm, "status": "ok"}


def total_variance_interpolate(t1: float, iv1: float, t2: float, iv2: float, t: float) -> dict[str, Any]:
    if t1 <= 0 or t2 <= 0 or t <= 0:
        raise ContractError("term interpolation requires positive T")
    if not (min(t1, t2) <= t <= max(t1, t2)):
        return {"iv": None, "w": None, "status": "no_bracket"}
    w1 = iv1 * iv1 * t1
    w2 = iv2 * iv2 * t2
    slope = (w2 - w1) / (t2 - t1)
    w = w1 + slope * (t - t1)
    forward_var_flag = bool(w2 < w1)
    if w < 0:
        return {"iv": None, "w": w, "status": "negative_variance", "forward_variance_negative": True}
    return {
        "iv": float(np.sqrt(w / t)),
        "w": float(w),
        "term_slope": float(slope),
        "status": "ok",
        "forward_variance_negative": forward_var_flag,
    }


def calendar_day_targets() -> tuple[float, ...]:
    return (7 / 365.0, 30 / 365.0, 90 / 365.0)


def expiry_bucket(calendar_days: float) -> str:
    if calendar_days < 0:
        return "expired"
    if calendar_days == 0:
        return "0DTE"
    if calendar_days <= 7:
        return "1-7"
    if calendar_days <= 30:
        return "8-30"
    if calendar_days <= 90:
        return "31-90"
    return ">90"
