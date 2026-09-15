"""GK, YZ, HAR/recent RV and session-seasonality features. Interval log-return variance."""

from __future__ import annotations

from math import log
from typing import Any, Sequence

import numpy as np

from trading_research.errors import ContractError

LN2 = log(2.0)
YZ_N = 20
EPS = 1e-12


def garman_klass(open_: float, high: float, low: float, close: float) -> dict[str, Any]:
    if min(open_, high, low, close) <= 0:
        raise ContractError("GK requires positive OHLC")
    if high < max(open_, close) or low > min(open_, close) or high < low:
        raise ContractError("inconsistent OHLC")
    c = log(close / open_)
    rng = log(high / low)
    gk = 0.5 * rng * rng - (2.0 * LN2 - 1.0) * c * c
    flag = None
    if -1e-12 < gk < 0:
        gk = 0.0
        flag = "rounded_tiny_negative"
    if gk < -1e-12:
        raise ContractError("GK variance is materially negative")
    return {"variance": gk, "c": c, "flag": flag, "unit": "interval_log_return_variance"}


def python_garman_klass(open_: float, high: float, low: float, close: float) -> float:
    return float(garman_klass(open_, high, low, close)["variance"])


def yang_zhang(o: Sequence[float], c: Sequence[float], u: Sequence[float], d: Sequence[float]) -> dict[str, Any]:
    o_a = np.asarray(o, dtype=np.float64)
    c_a = np.asarray(c, dtype=np.float64)
    u_a = np.asarray(u, dtype=np.float64)
    d_a = np.asarray(d, dtype=np.float64)
    n = int(o_a.size)
    if n <= 1:
        raise ContractError("YZ requires n>1")
    if o_a.size != c_a.size or o_a.size != u_a.size or o_a.size != d_a.size:
        raise ContractError("YZ input lengths disagree")
    v_o = float(np.sum((o_a - o_a.mean()) ** 2) / (n - 1))
    v_c = float(np.sum((c_a - c_a.mean()) ** 2) / (n - 1))
    rs = u_a * (u_a - c_a) + d_a * (d_a - c_a)
    v_rs = float(rs.mean())
    k = 0.34 / (1.34 + (n + 1) / (n - 1))
    yz = v_o + k * v_c + (1.0 - k) * v_rs
    return {"variance": yz, "k": k, "v_o": v_o, "v_c": v_c, "v_rs": v_rs, "n": n, "unit": "interval_log_return_variance"}


def python_yang_zhang(o: Sequence[float], c: Sequence[float], u: Sequence[float], d: Sequence[float]) -> float:
    return float(yang_zhang(o, c, u, d)["variance"])


def realized_variance(prices: Sequence[float]) -> dict[str, Any]:
    px = np.asarray(prices, dtype=np.float64)
    if px.size < 2:
        raise ContractError("RV needs at least two prices")
    if np.any(px <= 0) or not np.all(np.isfinite(px)):
        raise ContractError("RV prices must be positive and finite")
    r = np.diff(np.log(px))
    return {"variance": float(np.sum(r * r)), "n_returns": int(r.size), "unit": "interval_log_return_variance"}


def python_realized_variance(prices: Sequence[float]) -> float:
    return float(realized_variance(prices)["variance"])


def iv_variance_one_calendar_day(annualized_iv: float) -> dict[str, Any]:
    """Labelled IV scaling feature. Never a realized target."""
    var = (annualized_iv * annualized_iv) / 365.0
    return {"variance": var, "unit": "annualized_iv_to_one_calendar_day_variance", "kind": "iv_scaling_feature"}


def har_inputs(daily_rv: Sequence[float]) -> dict[str, Any]:
    rv = np.asarray(daily_rv, dtype=np.float64)
    if rv.size < 1:
        return {"har1": None, "har5": None, "har22": None, "status": "unavailable"}
    har1 = float(rv[-1])
    har5 = float(rv[-5:].mean()) if rv.size >= 5 else None
    har22 = float(rv[-22:].mean()) if rv.size >= 22 else None
    return {
        "har1": har1,
        "har5": har5,
        "har22": har22,
        "log_har1": None if har1 is None else log(har1 + EPS),
        "log_har5": None if har5 is None else log(har5 + EPS),
        "log_har22": None if har22 is None else log(har22 + EPS),
        "status": "ok" if har22 is not None else "partial",
    }


def recent_rv(prices: Sequence[float], bars: int) -> dict[str, Any] | None:
    px = np.asarray(prices, dtype=np.float64)
    if px.size < bars + 1:
        return None
    return realized_variance(px[-(bars + 1) :])


def future_prices_do_not_enter(current: Sequence[float], future: Sequence[float]) -> bool:
    left = python_realized_variance(current)
    combined = list(current) + list(future)
    right = python_realized_variance(combined[: len(current)])
    return left == right
