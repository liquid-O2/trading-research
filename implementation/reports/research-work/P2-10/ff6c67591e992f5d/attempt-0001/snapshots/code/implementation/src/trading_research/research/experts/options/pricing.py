"""European BSM/Black76, American CRR, IV inversion and Greeks.

Phi is 0.5*(1+erf(x/sqrt(2))). Vega is per 1.00 absolute volatility. A one
vol-point shock is 0.01. Integer/Decimal outputs match the Python reference
exactly; float outputs match within 1e-12 relative.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import erf as math_erf
from math import exp, log, pi, sqrt
from typing import Literal

import numpy as np

from trading_research.errors import ContractError

SQRT2 = sqrt(2.0)
INV_SQRT_2PI = 1.0 / sqrt(2.0 * pi)
YEAR_SECONDS = 365 * 86400
IV_LO = 1e-4
IV_HI = 5.0
IV_ITERS = 100
IV_SIGMA_TOL = 1e-8


def erf_array(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    out = np.empty(x.shape, dtype=np.float64)
    flat_in = x.ravel()
    flat_out = out.ravel()
    for i, value in enumerate(flat_in):
        flat_out[i] = math_erf(float(value))
    return out


def phi_cdf(x: np.ndarray | float) -> np.ndarray | float:
    if np.isscalar(x):
        return 0.5 * (1.0 + math_erf(float(x) / SQRT2))
    return 0.5 * (1.0 + erf_array(np.asarray(x, dtype=np.float64) / SQRT2))


def phi_pdf(x: np.ndarray | float) -> np.ndarray | float:
    if np.isscalar(x):
        z = float(x)
        return exp(-0.5 * z * z) * INV_SQRT_2PI
    z = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * z * z) * INV_SQRT_2PI


def tau_years(seconds: float) -> float:
    return float(seconds) / YEAR_SECONDS


@dataclass(frozen=True, slots=True)
class Greeks:
    price: float
    delta: float
    gamma: float
    vega: float
    vanna: float
    model: str
    vega_per_vol_point: float
    flags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class IVResult:
    sigma: float | None
    status: str
    iterations: int
    price_error: float | None
    lo: float
    hi: float


def _require_positive(name: str, value: float) -> float:
    if not np.isfinite(value) or value <= 0:
        raise ContractError(f"{name} must be positive and finite")
    return float(value)


def european_price(
    underlier: float,
    strike: float,
    tau_years: float,
    sigma: float,
    rate: float,
    carry: float,
    right: Literal["call", "put"],
    model: Literal["bsm", "black76"],
) -> float:
    if tau_years <= 0:
        intrinsic = max(underlier - strike, 0.0) if right == "call" else max(strike - underlier, 0.0)
        return float(intrinsic)
    S = _require_positive("underlier", underlier)
    K = _require_positive("strike", strike)
    sig = _require_positive("sigma", sigma)
    sqrt_t = sqrt(tau_years)
    if model == "bsm":
        d1 = (log(S / K) + (rate - carry + 0.5 * sig * sig) * tau_years) / (sig * sqrt_t)
        d2 = d1 - sig * sqrt_t
        df_r = exp(-rate * tau_years)
        df_q = exp(-carry * tau_years)
        call = S * df_q * float(phi_cdf(d1)) - K * df_r * float(phi_cdf(d2))
        put = K * df_r * float(phi_cdf(-d2)) - S * df_q * float(phi_cdf(-d1))
        return call if right == "call" else put
    if model != "black76":
        raise ContractError("model must be bsm or black76")
    F = S
    d1 = (log(F / K) + 0.5 * sig * sig * tau_years) / (sig * sqrt_t)
    d2 = d1 - sig * sqrt_t
    df = exp(-rate * tau_years)
    call = df * (F * float(phi_cdf(d1)) - K * float(phi_cdf(d2)))
    put = df * (K * float(phi_cdf(-d2)) - F * float(phi_cdf(-d1)))
    return call if right == "call" else put


def european_greeks(
    underlier: float,
    strike: float,
    tau_years: float,
    sigma: float,
    rate: float,
    carry: float,
    right: Literal["call", "put"],
    model: Literal["bsm", "black76"],
) -> Greeks:
    if tau_years <= 0 or sigma <= 0:
        raise ContractError("live Greeks require positive time and volatility")
    S = _require_positive("underlier", underlier)
    K = _require_positive("strike", strike)
    sig = _require_positive("sigma", sigma)
    sqrt_t = sqrt(tau_years)
    price = european_price(S, K, tau_years, sig, rate, carry, right, model)
    if model == "bsm":
        d1 = (log(S / K) + (rate - carry + 0.5 * sig * sig) * tau_years) / (sig * sqrt_t)
        d2 = d1 - sig * sqrt_t
        df_q = exp(-carry * tau_years)
        density = float(phi_pdf(d1))
        delta_call = df_q * float(phi_cdf(d1))
        delta = delta_call if right == "call" else df_q * (float(phi_cdf(d1)) - 1.0)
        gamma = df_q * density / (S * sig * sqrt_t)
        vega = S * df_q * density * sqrt_t
        vanna = -df_q * density * d2 / sig
        label = "bsm_spot"
    else:
        F = S
        d1 = (log(F / K) + 0.5 * sig * sig * tau_years) / (sig * sqrt_t)
        d2 = d1 - sig * sqrt_t
        df = exp(-rate * tau_years)
        density = float(phi_pdf(d1))
        delta_call = df * float(phi_cdf(d1))
        delta = delta_call if right == "call" else df * (float(phi_cdf(d1)) - 1.0)
        gamma = df * density / (F * sig * sqrt_t)
        vega = df * F * density * sqrt_t
        vanna = -df * density * d2 / sig
        label = "black76"
    return Greeks(
        price=price,
        delta=delta,
        gamma=gamma,
        vega=vega,
        vanna=vanna,
        model=label,
        vega_per_vol_point=vega * 0.01,
        flags=(),
    )


def european_greeks_array(
    underlier: np.ndarray,
    strike: np.ndarray,
    tau_years: np.ndarray,
    sigma: np.ndarray,
    rate: np.ndarray,
    carry: np.ndarray,
    right: np.ndarray,
    model: str,
) -> dict[str, np.ndarray]:
    """Vectorized BSM/Black76. `right` is +1 call / -1 put. No Python over contracts except erf."""
    S = np.asarray(underlier, dtype=np.float64)
    K = np.asarray(strike, dtype=np.float64)
    T = np.asarray(tau_years, dtype=np.float64)
    sig = np.asarray(sigma, dtype=np.float64)
    r = np.asarray(rate, dtype=np.float64)
    q = np.asarray(carry, dtype=np.float64)
    cp = np.asarray(right, dtype=np.float64)
    sqrt_t = np.sqrt(np.maximum(T, 0.0))
    live = (T > 0) & (sig > 0) & (S > 0) & (K > 0)
    d1 = np.zeros_like(S)
    d2 = np.zeros_like(S)
    if model == "bsm":
        d1[live] = (np.log(S[live] / K[live]) + (r[live] - q[live] + 0.5 * sig[live] ** 2) * T[live]) / (sig[live] * sqrt_t[live])
        d2[live] = d1[live] - sig[live] * sqrt_t[live]
        df_r = np.exp(-r * T)
        df_q = np.exp(-q * T)
        nd1 = phi_cdf(d1)
        nd2 = phi_cdf(d2)
        density = phi_pdf(d1)
        call = S * df_q * nd1 - K * df_r * nd2
        put = K * df_r * phi_cdf(-d2) - S * df_q * phi_cdf(-d1)
        price = np.where(cp > 0, call, put)
        delta = np.where(cp > 0, df_q * nd1, df_q * (nd1 - 1.0))
        gamma = df_q * density / np.maximum(S * sig * sqrt_t, 1e-18)
        vega = S * df_q * density * sqrt_t
        vanna = -df_q * density * d2 / np.maximum(sig, 1e-18)
    elif model == "black76":
        d1[live] = (np.log(S[live] / K[live]) + 0.5 * sig[live] ** 2 * T[live]) / (sig[live] * sqrt_t[live])
        d2[live] = d1[live] - sig[live] * sqrt_t[live]
        df = np.exp(-r * T)
        nd1 = phi_cdf(d1)
        density = phi_pdf(d1)
        call = df * (S * nd1 - K * phi_cdf(d2))
        put = df * (K * phi_cdf(-d2) - S * phi_cdf(-d1))
        price = np.where(cp > 0, call, put)
        delta = np.where(cp > 0, df * nd1, df * (nd1 - 1.0))
        gamma = df * density / np.maximum(S * sig * sqrt_t, 1e-18)
        vega = df * S * density * sqrt_t
        vanna = -df * density * d2 / np.maximum(sig, 1e-18)
    else:
        raise ContractError("model must be bsm or black76")
    intrinsic = np.where(cp > 0, np.maximum(S - K, 0.0), np.maximum(K - S, 0.0))
    price = np.where(live, price, intrinsic)
    zero = np.zeros_like(S)
    return {
        "price": price,
        "delta": np.where(live, delta, zero),
        "gamma": np.where(live, gamma, zero),
        "vega": np.where(live, vega, zero),
        "vanna": np.where(live, vanna, zero),
        "vega_per_vol_point": np.where(live, vega * 0.01, zero),
    }


def python_european_greeks(
    underlier: float,
    strike: float,
    tau_years: float,
    sigma: float,
    rate: float,
    carry: float,
    right: str,
    model: str,
) -> dict[str, float]:
    g = european_greeks(underlier, strike, tau_years, sigma, rate, carry, right, model)  # type: ignore[arg-type]
    return {
        "price": g.price,
        "delta": g.delta,
        "gamma": g.gamma,
        "vega": g.vega,
        "vanna": g.vanna,
        "vega_per_vol_point": g.vega_per_vol_point,
    }


def implied_vol(
    mid: float,
    underlier: float,
    strike: float,
    tau_years: float,
    rate: float,
    carry: float,
    right: Literal["call", "put"],
    model: Literal["bsm", "black76"],
) -> IVResult:
    if not np.isfinite(mid) or mid <= 0:
        return IVResult(None, "no_bracket", 0, None, IV_LO, IV_HI)
    lo_px = european_price(underlier, strike, tau_years, IV_LO, rate, carry, right, model)
    hi_px = european_price(underlier, strike, tau_years, IV_HI, rate, carry, right, model)
    lo, hi = IV_LO, IV_HI
    if not (min(lo_px, hi_px) <= mid <= max(lo_px, hi_px)):
        return IVResult(None, "no_bracket", 0, abs(mid - lo_px), lo, hi)
    last_err = None
    sigma = 0.5 * (lo + hi)
    for i in range(1, IV_ITERS + 1):
        sigma = 0.5 * (lo + hi)
        px = european_price(underlier, strike, tau_years, sigma, rate, carry, right, model)
        last_err = px - mid
        if abs(last_err) <= max(1e-6, 1e-5 * mid) or (hi - lo) <= IV_SIGMA_TOL:
            return IVResult(sigma, "converged", i, last_err, lo, hi)
        if px > mid:
            hi = sigma
        else:
            lo = sigma
    return IVResult(sigma, "max_iter", IV_ITERS, last_err, lo, hi)


def implied_vol_array(
    mid: np.ndarray,
    underlier: np.ndarray,
    strike: np.ndarray,
    tau_years: np.ndarray,
    rate: np.ndarray,
    carry: np.ndarray,
    right: np.ndarray,
    model: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Bisection over arrays. Loop is over the 100 iterations, not over contracts."""
    m = np.asarray(mid, dtype=np.float64)
    S = np.broadcast_to(np.asarray(underlier, dtype=np.float64), m.shape).copy()
    K = np.asarray(strike, dtype=np.float64)
    T = np.asarray(tau_years, dtype=np.float64)
    r = np.broadcast_to(np.asarray(rate, dtype=np.float64), m.shape).copy()
    q = np.broadcast_to(np.asarray(carry, dtype=np.float64), m.shape).copy()
    cp = np.asarray(right, dtype=np.float64)
    lo = np.full(m.shape, IV_LO)
    hi = np.full(m.shape, IV_HI)
    sigma = 0.5 * (lo + hi)
    status = np.full(m.shape, 0, dtype=np.int8)
    lo_g = european_greeks_array(S, K, T, lo, r, q, cp, model)["price"]
    hi_g = european_greeks_array(S, K, T, hi, r, q, cp, model)["price"]
    bracket = (np.minimum(lo_g, hi_g) <= m) & (m <= np.maximum(lo_g, hi_g)) & np.isfinite(m) & (m > 0)
    status = np.where(bracket, 1, 0)
    for _ in range(IV_ITERS):
        sigma = 0.5 * (lo + hi)
        px = european_greeks_array(S, K, T, sigma, r, q, cp, model)["price"]
        err = px - m
        tight = (np.abs(err) <= np.maximum(1e-6, 1e-5 * np.abs(m))) | ((hi - lo) <= IV_SIGMA_TOL)
        done = (~bracket) | tight
        grow = bracket & (~tight) & (px <= m)
        shrink = bracket & (~tight) & (px > m)
        lo = np.where(grow, sigma, lo)
        hi = np.where(shrink, sigma, hi)
        status = np.where(bracket & tight, 2, status)
        if bool(np.all(done)):
            break
    sigma = np.where(status == 2, sigma, np.nan)
    return sigma, status


def american_tree_price(
    underlier: float,
    strike: float,
    tau_years: float,
    sigma: float,
    rate: float,
    carry: float,
    right: Literal["call", "put"],
    *,
    steps: int = 400,
    futures: bool = False,
) -> tuple[float, str]:
    if tau_years <= 0:
        intrinsic = max(underlier - strike, 0.0) if right == "call" else max(strike - underlier, 0.0)
        return float(intrinsic), "expired"
    n = int(steps)
    dt = tau_years / n
    u = exp(sigma * sqrt(dt))
    d = 1.0 / u
    if futures:
        p = (1.0 - d) / (u - d)
    else:
        p = (exp((rate - carry) * dt) - d) / (u - d)
    if not 0.0 <= p <= 1.0:
        return float("nan"), "p_out_of_range"
    disc = exp(-rate * dt)
    spots = np.empty(n + 1, dtype=np.float64)
    j = np.arange(n + 1, dtype=np.float64)
    spots[:] = underlier * (u ** (n - j)) * (d ** j)
    if right == "call":
        value = np.maximum(spots - strike, 0.0)
        intrinsic_at = lambda s: np.maximum(s - strike, 0.0)
    else:
        value = np.maximum(strike - spots, 0.0)
        intrinsic_at = lambda s: np.maximum(strike - s, 0.0)
    for step in range(n - 1, -1, -1):
        spots = underlier * (u ** (step - np.arange(step + 1))) * (d ** np.arange(step + 1))
        cont = disc * (p * value[:-1] + (1.0 - p) * value[1:])
        value = np.maximum(intrinsic_at(spots), cont)
    return float(value[0]), "ok"


def american_numerical_greeks(
    underlier: float,
    strike: float,
    tau_years: float,
    sigma: float,
    rate: float,
    carry: float,
    right: Literal["call", "put"],
    *,
    steps: int,
    futures: bool = False,
) -> dict[str, float]:
    h = max(0.01, 0.001 * underlier)
    v = 0.001 if sigma > 0.001 else sigma / 2.0
    up, _ = american_tree_price(underlier + h, strike, tau_years, sigma, rate, carry, right, steps=steps, futures=futures)
    dn, _ = american_tree_price(underlier - h, strike, tau_years, sigma, rate, carry, right, steps=steps, futures=futures)
    mid, flag = american_tree_price(underlier, strike, tau_years, sigma, rate, carry, right, steps=steps, futures=futures)
    vu, _ = american_tree_price(underlier, strike, tau_years, sigma + v, rate, carry, right, steps=steps, futures=futures)
    vd, _ = american_tree_price(underlier, strike, tau_years, sigma - v, rate, carry, right, steps=steps, futures=futures)
    uuv, _ = american_tree_price(underlier + h, strike, tau_years, sigma + v, rate, carry, right, steps=steps, futures=futures)
    udv, _ = american_tree_price(underlier + h, strike, tau_years, sigma - v, rate, carry, right, steps=steps, futures=futures)
    duv, _ = american_tree_price(underlier - h, strike, tau_years, sigma + v, rate, carry, right, steps=steps, futures=futures)
    ddv, _ = american_tree_price(underlier - h, strike, tau_years, sigma - v, rate, carry, right, steps=steps, futures=futures)
    delta = (up - dn) / (2.0 * h)
    gamma = (up - 2.0 * mid + dn) / (h * h)
    vega = (vu - vd) / (2.0 * v)
    vanna = (uuv - udv - duv + ddv) / (4.0 * h * v)
    return {"price": mid, "delta": delta, "gamma": gamma, "vega": vega, "vanna": vanna, "flag": flag, "steps": float(steps)}


def finite_difference_greeks(
    underlier: float,
    strike: float,
    tau_years: float,
    sigma: float,
    rate: float,
    carry: float,
    right: Literal["call", "put"],
    model: Literal["bsm", "black76"],
    *,
    h: float = 0.01,
    v: float = 0.0001,
) -> dict[str, float]:
    pu = european_price(underlier + h, strike, tau_years, sigma, rate, carry, right, model)
    pd = european_price(underlier - h, strike, tau_years, sigma, rate, carry, right, model)
    pm = european_price(underlier, strike, tau_years, sigma, rate, carry, right, model)
    vu = european_price(underlier, strike, tau_years, sigma + v, rate, carry, right, model)
    vd = european_price(underlier, strike, tau_years, sigma - v, rate, carry, right, model)
    uuv = european_price(underlier + h, strike, tau_years, sigma + v, rate, carry, right, model)
    udv = european_price(underlier + h, strike, tau_years, sigma - v, rate, carry, right, model)
    duv = european_price(underlier - h, strike, tau_years, sigma + v, rate, carry, right, model)
    ddv = european_price(underlier - h, strike, tau_years, sigma - v, rate, carry, right, model)
    return {
        "price": pm,
        "delta": (pu - pd) / (2.0 * h),
        "gamma": (pu - 2.0 * pm + pd) / (h * h),
        "vega": (vu - vd) / (2.0 * v),
        "vanna": (uuv - udv - duv + ddv) / (4.0 * h * v),
    }


def atm_fixture() -> dict[str, float]:
    g = european_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    put = european_price(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "put", "bsm")
    parity = g.price - put
    black = european_price(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "black76")
    return {
        "call": g.price,
        "delta": g.delta,
        "gamma": g.gamma,
        "vega": g.vega,
        "vanna": g.vanna,
        "put": put,
        "parity_c_minus_p": parity,
        "black76_call": black,
        "expected_call": 7.96556746,
        "expected_delta": 0.539827837,
        "expected_gamma": 0.019847627,
        "expected_vega": 39.69525475,
        "expected_vanna": 0.198476274,
    }


def exposure_units(n: float, multiplier: float, underlier: float, greeks: Greeks) -> dict[str, float]:
    delta_notional = n * multiplier * underlier * greeks.delta
    gamma_1pct = 0.01 * n * multiplier * underlier * underlier * greeks.gamma
    vega_1pt = 0.01 * n * multiplier * greeks.vega
    vanna_1pt = 0.01 * n * multiplier * underlier * greeks.vanna
    return {
        "delta_notional": delta_notional,
        "gamma_hedge_notional_per_1pct": gamma_1pct,
        "vega_dollars_per_vol_point": vega_1pt,
        "vanna_delta_notional_per_vol_point": vanna_1pt,
        "multiplier": multiplier,
        "underlier": underlier,
        "n_contracts": n,
    }
