"""O02/O05 numerical kernel: Black inversion/Greeks and native American FD.

This module is the frozen numerical contract in OPTIONS_VALUATION_NUMERICS_V1.
It is not a surface, source adapter, quote join, or family completion. Import
does not compile, spawn processes, or touch acquired data. Root builds the C++
shared library and authenticates it with enable_native(path, sha256).
"""
from __future__ import annotations

import ctypes
import hashlib
import math
from pathlib import Path

import numpy as np
from scipy.special import ndtr

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError


MODEL_VERSION = "options_valuation_numerics_v1"
CONTRACT_KIND = "options_valuation_numerics_contract_v1"
VOLATILITY_UNIT = "fraction"
PRICE_UNIT = "premium_per_underlying_unit"
TIME_UNIT = "actual365fixed_year"
COORDINATE_FORWARD = "forward"
COORDINATE_SPOT = "spot"

NATIVE_ENV_PATH = "TR_OPTIONS_VALUATION_NATIVE_PATH"
NATIVE_ENV_SHA256 = "TR_OPTIONS_VALUATION_NATIVE_SHA256"
NATIVE_MAX_BYTES = 16 * 1024 ** 2
NATIVE_BUILD_FLAGS = (
    "/usr/bin/g++",
    "-O3",
    "-std=c++17",
    "-pipe",
    "-shared",
    "-fPIC",
    "-fno-fast-math",
    "-ffp-contract=off",
)
NATIVE_ABI = (
    "american_price_batch",
    "american_iv_batch",
)

SIGMA_BRACKET_LOW = 0.0
SIGMA_BRACKET_HIGH = 10.0
EUROPEAN_MAX_ITERATIONS = 100
AMERICAN_MAX_ITERATIONS = 80
ACTUAL365_FIXED_SECONDS = 365.0 * 86400.0
ACTUAL365_FIXED_NS = ACTUAL365_FIXED_SECONDS * 1e9
INV_SQRT_2PI = 0.39894228040143267793994605993438

STATUS_CONVERGED = 0
STATUS_ENDPOINT_LOWER = 1
STATUS_ENDPOINT_UPPER = 2
STATUS_FAILED_BRACKET = 3
STATUS_ZERO_T = 4
STATUS_INVALID_INPUT = 5
STATUS_NONCONVERGED = 6
STATUS_CROSSED_QUOTES = 7
STATUS_UNBOUNDED_SIDE = 8
STATUS_UNDEFINED_POINT = 9
STATUS_DOMAIN_ERROR = 10
STATUS_SIGMA0_DETERMINISTIC = 11
STATUS_UNSTABLE_GREEK = 12
STATUS_GRID_INCONSISTENT = 13
STATUS_NATIVE_UNAVAILABLE = 14
STATUS_ABI_ERROR = 15
STATUS_MASK = 0xFF
FLAG_WEAK_VEGA = 1 << 8
FLAG_UNSTABLE_GREEK = 1 << 9
FLAG_GRID_ERROR = 1 << 10
FLAG_NONPOSITIVE_DOMAIN = 1 << 11
FLAG_ASK_ONLY = 1 << 12
FLAG_ZERO_BID = 1 << 13
FLAG_MISSING_BID = 1 << 14
FLAG_MISSING_ASK = 1 << 15
FLAG_POINT_UNDEFINED = 1 << 16

CALENDAR_SECONDS_DEFAULT = (0, 60)
COORDINATE_RELATIVE_SHOCKS_DEFAULT = (-0.01, 0.0, 0.01)
SIGMA_ADDITIVE_SHOCKS_DEFAULT = (-0.01, 0.0, 0.01)

_LIBRARY = None
_PRICE_FN = None
_IV_FN = None
_SINGLE_PRICE_FN = None


def primary_status(code):
    return int(code) & STATUS_MASK


def has_flag(code, flag):
    return bool(int(code) & int(flag))


def years_from_nanoseconds(dt_ns):
    """Exact nanosecond span over Actual/365 Fixed. Does not round 0DTE to days."""
    return np.asarray(dt_ns, dtype=np.float64) / ACTUAL365_FIXED_NS


def years_from_seconds(dt_seconds):
    return np.asarray(dt_seconds, dtype=np.float64) / ACTUAL365_FIXED_SECONDS


class ArrayResult:
    """Broadcast-shaped solver record. Unavailable entries stay NaN."""

    __slots__ = (
        "value", "status", "residual", "iterations",
        "bracket_low", "bracket_high", "error", "coordinate", "unit",
        "model_version",
    )

    def __init__(self, value, status, residual, iterations,
                 bracket_low=None, bracket_high=None, error=None,
                 coordinate=None, unit=PRICE_UNIT):
        self.value = np.asarray(value)
        self.status = np.asarray(status, dtype=np.int32)
        self.residual = np.asarray(residual, dtype=np.float64)
        self.iterations = np.asarray(iterations, dtype=np.int32)
        self.bracket_low = None if bracket_low is None else np.asarray(bracket_low, dtype=np.float64)
        self.bracket_high = None if bracket_high is None else np.asarray(bracket_high, dtype=np.float64)
        self.error = None if error is None else np.asarray(error, dtype=np.float64)
        self.coordinate = coordinate
        self.unit = unit
        self.model_version = MODEL_VERSION


class GreeksResult:
    __slots__ = (
        "price", "delta", "gamma", "vega", "vanna", "charm", "volga", "theta",
        "greek_errors", "greek_status", "greek_units", "step_differences", "grid_differences", "raw_greeks",
        "status", "residual", "error", "coordinate", "held_fixed",
        "volatility_unit", "time_unit", "model_version",
    )

    def __init__(self, price, delta, gamma, vega, vanna, charm, volga,
                 status, residual, error, coordinate, held_fixed, theta=None,
                 greek_errors=None, greek_status=None, step_differences=None, grid_differences=None, raw_greeks=None):
        self.price = np.asarray(price, dtype=np.float64)
        self.theta = np.full(self.price.shape, np.nan) if theta is None else np.asarray(theta, dtype=np.float64)
        names = ('delta', 'gamma', 'vega', 'vanna', 'charm', 'volga', 'theta')
        self.greek_errors = greek_errors or {name: np.zeros(self.price.shape) for name in names}
        self.greek_status = greek_status or {name: np.asarray(status, dtype=np.int32).copy() for name in names}
        self.greek_units = {'delta':'premium/underlying', 'gamma':'premium/underlying^2',
                            'vega':'premium/vol_fraction', 'volga':'premium/vol_fraction^2',
                            'vanna':'premium/underlying/vol_fraction',
                            'charm':'premium/underlying/calendar_year', 'theta':'premium/calendar_year'}
        self.step_differences = step_differences or {}
        self.grid_differences = grid_differences or {}
        self.raw_greeks = raw_greeks or {}
        self.delta = np.asarray(delta, dtype=np.float64)
        self.gamma = np.asarray(gamma, dtype=np.float64)
        self.vega = np.asarray(vega, dtype=np.float64)
        self.vanna = np.asarray(vanna, dtype=np.float64)
        self.charm = np.asarray(charm, dtype=np.float64)
        self.volga = np.asarray(volga, dtype=np.float64)
        self.status = np.asarray(status, dtype=np.int32)
        self.residual = np.asarray(residual, dtype=np.float64)
        self.error = np.asarray(error, dtype=np.float64)
        self.coordinate = coordinate
        self.held_fixed = held_fixed
        self.volatility_unit = VOLATILITY_UNIT
        self.time_unit = TIME_UNIT
        self.model_version = MODEL_VERSION


class QuoteIVResult:
    __slots__ = (
        "iv_bid", "iv_mid", "iv_ask", "iv_lower", "iv_upper",
        "price_bid", "price_mid", "price_ask",
        "model_price_lower", "model_price_upper",
        "point_iv", "point_defined", "status",
        "residual_bid", "residual_mid", "residual_ask", "status_bid", "status_mid", "status_ask",
        "error_bid", "error_mid", "error_ask", "coordinate",
        "iterations", "solver_price_tolerance", "market_interval",
        "model_version",
    )

    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)
        self.model_version = MODEL_VERSION


class ResponseCube:
    __slots__ = (
        "price", "status", "taylor_price", "taylor_residual",
        "coordinate_relative_shocks", "sigma_additive_shocks", "calendar_seconds",
        "calendar_years", "coordinate", "model_version",
    )

    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)
        self.model_version = MODEL_VERSION


def _as_float(name, value):
    if isinstance(value, np.ma.MaskedArray):
        raise ContractError(f"{name} is null/masked and is not replaced by a default")
    arr = np.asarray(value, dtype=np.float64)
    return arr


def _finite_positive(name, arr, allow_zero=False):
    if allow_zero:
        bad = ~np.isfinite(arr) | (arr < 0.0)
    else:
        bad = ~np.isfinite(arr) | (arr <= 0.0)
    return bad


def encode_right(right, shape):
    raw = np.asarray(right)
    if raw.shape == () and raw.dtype == object and raw.item() is None:
        raise ContractError("right is null")
    if raw.dtype.kind in "OSU":
        mapped = np.empty(raw.shape, dtype=np.int32)
        it = np.nditer(raw, flags=["multi_index", "refs_ok", "zerosize_ok"])
        for item in it:
            token = item.item()
            if token is None:
                raise ContractError("right is null")
            key = str(token).strip().lower()
            if key in ("c", "call", "1", "+1"):
                mapped[it.multi_index] = 1
            elif key in ("p", "put", "-1"):
                mapped[it.multi_index] = -1
            else:
                raise ContractError(
                    f"unsupported option right {token!r}; European Black accepts call/put only"
                )
        return np.broadcast_to(mapped, shape).copy()
    vals = np.asarray(right)
    if np.any((vals != 1) & (vals != -1)):
        raise ContractError("right must be +1 (call) or -1 (put)")
    return np.broadcast_to(vals.astype(np.int32), shape).copy()


def _reject_multiplier(multiplier):
    if multiplier is not None:
        raise ContractError(
            "per-contract multiplication is apply_contract_multiplier; "
            "solver premium stays per underlying unit"
        )


def _reject_style(style, allowed):
    if style != allowed:
        raise ContractError(f"{allowed} kernel rejected style {style!r}")


def _reject_vol_unit(volatility_unit):
    if volatility_unit != VOLATILITY_UNIT:
        raise ContractError(
            "volatility must be a fraction per sqrt(365-day year); percent units are rejected"
        )


def _prepare_black(F, K, T, sigma, discount, right, *, volatility_unit, style, multiplier):
    _reject_style(style, "european")
    _reject_vol_unit(volatility_unit)
    _reject_multiplier(multiplier)
    F = _as_float("F", F)
    K = _as_float("K", K)
    T = _as_float("T", T)
    sigma = _as_float("sigma", sigma)
    discount = _as_float("discount", discount)
    try:
        F, K, T, sigma, discount, _ = np.broadcast_arrays(F, K, T, sigma, discount, np.asarray(right))
    except ValueError as exc:
        raise ContractError("F, K, T, sigma, discount are not broadcast-compatible") from exc
    if np.any(sigma > SIGMA_BRACKET_HIGH):
        raise ContractError(
            "volatility must be a fraction in [0, 10]; percent units are rejected"
        )
    right = encode_right(right, F.shape)
    return F.copy(), K.copy(), T.copy(), sigma.copy(), discount.copy(), right


def _norm_pdf(z):
    return INV_SQRT_2PI * np.exp(-0.5 * np.square(z))


def _black_undiscounted(F, K, T, sigma, cp):
    """OTM-stable undiscounted Black using put-call parity on the deep wing."""
    out = np.full(F.shape, np.nan, dtype=np.float64)
    valid = np.isfinite(F) & np.isfinite(K) & np.isfinite(T) & np.isfinite(sigma)
    valid &= (F > 0.0) & (K > 0.0) & (T >= 0.0) & (sigma >= 0.0)
    st = sigma * np.sqrt(np.maximum(T, 0.0))
    degenerate = valid & ((T == 0.0) | (st == 0.0))
    out[degenerate] = np.maximum(cp[degenerate] * (F[degenerate] - K[degenerate]), 0.0)
    live = valid & ~degenerate
    if not np.any(live):
        return out
    x = np.log(F[live] / K[live])
    s = st[live]
    d1 = x / s + 0.5 * s
    d2 = d1 - s
    # OTM option is well-conditioned; ITM uses parity.
    otm_put = F[live] >= K[live]
    put = K[live] * ndtr(-d2) - F[live] * ndtr(-d1)
    call = F[live] * ndtr(d1) - K[live] * ndtr(d2)
    call = np.where(otm_put, put + (F[live] - K[live]), call)
    put = np.where(~otm_put, call - (F[live] - K[live]), put)
    out[live] = np.where(cp[live] > 0, call, put)
    return out


def _european_bounds(F, K, T, discount, cp):
    lower = discount * np.maximum(cp * (F - K), 0.0)
    upper = discount * np.where(cp > 0, F, K)
    return lower, upper


def _european_price_tolerance(price):
    return np.maximum(1e-8, 1e-8 * np.abs(price))


def black_price(F, K, T, sigma, discount, right, *,
                volatility_unit=VOLATILITY_UNIT, style="european", multiplier=None):
    """Vectorized Black forward price. F-partials are not computed here."""
    F, K, T, sigma, discount, right = _prepare_black(
        F, K, T, sigma, discount, right,
        volatility_unit=volatility_unit, style=style, multiplier=multiplier,
    )
    status = np.full(F.shape, STATUS_CONVERGED, dtype=np.int32)
    residual = np.zeros(F.shape, dtype=np.float64)
    iterations = np.zeros(F.shape, dtype=np.int32)
    bad = _finite_positive("F", F) | _finite_positive("K", K)
    bad |= ~np.isfinite(T) | (T < 0.0)
    bad |= ~np.isfinite(discount) | (discount <= 0.0)
    bad |= ~np.isfinite(sigma) | (sigma < 0.0)
    percent = sigma > SIGMA_BRACKET_HIGH
    status[bad | percent] = STATUS_INVALID_INPUT
    value = np.full(F.shape, np.nan, dtype=np.float64)
    ok = ~bad & ~percent
    if np.any(ok):
        und = _black_undiscounted(F, K, T, sigma, right.astype(np.float64))
        value[ok] = discount[ok] * und[ok]
        zero_t = ok & (T == 0.0)
        status[zero_t] = STATUS_ZERO_T
        sig0 = ok & (T > 0.0) & (sigma == 0.0)
        status[sig0] = STATUS_ENDPOINT_LOWER
    return ArrayResult(value, status, residual, iterations, coordinate=COORDINATE_FORWARD)


def black_iv(price, F, K, T, discount, right, *,
             volatility_unit=VOLATILITY_UNIT, style="european", multiplier=None):
    """Bracketed Black IV on [0, 10]. Endpoints are not labelled as convergence."""
    _reject_style(style, "european")
    _reject_vol_unit(volatility_unit)
    _reject_multiplier(multiplier)
    price = _as_float("price", price)
    F = _as_float("F", F)
    K = _as_float("K", K)
    T = _as_float("T", T)
    discount = _as_float("discount", discount)
    try:
        price, F, K, T, discount, _ = np.broadcast_arrays(price, F, K, T, discount, np.asarray(right))
    except ValueError as exc:
        raise ContractError("price, F, K, T, discount are not broadcast-compatible") from exc
    right = encode_right(right, F.shape)
    shape = F.shape
    iv = np.full(shape, np.nan, dtype=np.float64)
    status = np.full(shape, STATUS_INVALID_INPUT, dtype=np.int32)
    residual = np.full(shape, np.nan, dtype=np.float64)
    iterations = np.zeros(shape, dtype=np.int32)
    blo = np.full(shape, SIGMA_BRACKET_LOW, dtype=np.float64)
    bhi = np.full(shape, SIGMA_BRACKET_HIGH, dtype=np.float64)
    cp = right.astype(np.float64)
    lower, upper = _european_bounds(F, K, T, discount, cp)
    valid = np.isfinite(price) & np.isfinite(F) & np.isfinite(K) & np.isfinite(T) & np.isfinite(discount)
    valid &= (F > 0.0) & (K > 0.0) & (T >= 0.0) & (discount > 0.0) & (price >= 0.0)
    status[~valid] = STATUS_INVALID_INPUT
    zero = valid & (T == 0.0)
    status[zero] = STATUS_ZERO_T
    residual[zero] = price[zero] - lower[zero]
    live = valid & ~zero
    below = live & (price < lower - 1e-14)
    above = live & (price >= upper)
    status[below | above] = STATUS_FAILED_BRACKET
    residual[below] = price[below] - lower[below]
    residual[above] = price[above] - upper[above]
    live = live & ~below & ~above
    tol = _european_price_tolerance(price)
    at_lo = live & (price <= lower + tol)
    status[at_lo] = STATUS_ENDPOINT_LOWER
    iv[at_lo] = 0.0
    residual[at_lo] = price[at_lo] - lower[at_lo]
    live = live & ~at_lo
    if np.any(live):
        hi = np.full(shape, SIGMA_BRACKET_HIGH, dtype=np.float64)
        p_hi = black_price(F, K, T, hi, discount, right).value
        at_hi = live & (price >= p_hi - tol)
        weak_hi = at_hi & ((p_hi - lower) <= 2.0 * np.maximum(tol, 1e-12))
        status[at_hi] = STATUS_ENDPOINT_UPPER
        status[weak_hi] = status[weak_hi] | FLAG_WEAK_VEGA
        iv[at_hi] = SIGMA_BRACKET_HIGH
        residual[at_hi] = p_hi[at_hi] - price[at_hi]
        over = live & (price > p_hi + tol)
        status[over] = STATUS_FAILED_BRACKET
        iv[over] = np.nan
        live = live & ~at_hi & ~over
        lo = np.zeros(shape, dtype=np.float64)
        mid = np.full(shape, 0.2, dtype=np.float64)
        active = live.copy()
        for step in range(EUROPEAN_MAX_ITERATIONS):
            if not np.any(active):
                break
            mid = 0.5 * (lo + hi)
            p_mid = black_price(F, K, T, mid, discount, right).value
            res = p_mid - price
            residual[active] = res[active]
            iterations[active] = step + 1
            go_lo = active & (p_mid < price)
            go_hi = active & ~go_lo
            lo = np.where(go_lo, mid, lo)
            hi = np.where(go_hi, mid, hi)
            blo[active] = lo[active]
            bhi[active] = hi[active]
            done = active & (np.abs(res) <= tol)
            iv[done] = mid[done]
            status[done] = STATUS_CONVERGED
            active = active & ~done & ((hi - lo) > 1e-14)
        leftover = live & (status == STATUS_INVALID_INPUT)
        if np.any(leftover):
            iv[leftover] = 0.5 * (lo[leftover] + hi[leftover])
            p_last = black_price(F, K, T, iv, discount, right).value
            residual[leftover] = p_last[leftover] - price[leftover]
            tight = leftover & (np.abs(residual) <= tol)
            status[tight] = STATUS_CONVERGED
            status[leftover & ~tight] = STATUS_NONCONVERGED
            iv[leftover & ~tight] = np.nan
        identified = live & ((status & STATUS_MASK) == STATUS_CONVERGED)
        if np.any(identified):
            greeks = black_greeks(F, K, T, iv, discount, right, r=0.0)
            vega = np.abs(greeks.vega)
            weak = identified & (vega <= _european_price_tolerance(price) / 0.05)
            status[weak] = status[weak] | FLAG_WEAK_VEGA
            undef = weak & (vega <= 1e-16)
            iv[undef] = np.nan
            status[undef] = STATUS_UNDEFINED_POINT | FLAG_WEAK_VEGA | FLAG_POINT_UNDEFINED
    return ArrayResult(iv, status, residual, iterations, blo, bhi, coordinate=COORDINATE_FORWARD,
                       unit=VOLATILITY_UNIT)


def black_greeks(F, K, T, sigma, discount, right, r, *,
                 volatility_unit=VOLATILITY_UNIT, style="european", multiplier=None):
    """Analytic Black F-partials. Delta/gamma are forward coordinates, never spot.

    Calendar charm holds F and sigma fixed. Remaining T decreases as calendar
    increases; independently stated D,r evolve as D_new = D * exp(-r * dT)
    with dT the change in remaining time.
    """
    F, K, T, sigma, discount, right = _prepare_black(
        F, K, T, sigma, discount, right,
        volatility_unit=volatility_unit, style=style, multiplier=multiplier,
    )
    r = _as_float("r", r)
    try:
        F, K, T, sigma, discount, r, right = np.broadcast_arrays(
            F, K, T, sigma, discount, r, right
        )
    except ValueError as exc:
        raise ContractError("greeks inputs are not broadcast-compatible") from exc
    right = np.asarray(right, dtype=np.int32)
    price = black_price(F, K, T, sigma, discount, right).value
    status = np.full(F.shape, STATUS_CONVERGED, dtype=np.int32)
    residual = np.zeros(F.shape, dtype=np.float64)
    error = np.zeros(F.shape, dtype=np.float64)
    delta = np.full(F.shape, np.nan, dtype=np.float64)
    gamma = np.full(F.shape, np.nan, dtype=np.float64)
    vega = np.full(F.shape, np.nan, dtype=np.float64)
    vanna = np.full(F.shape, np.nan, dtype=np.float64)
    charm = np.full(F.shape, np.nan, dtype=np.float64)
    volga = np.full(F.shape, np.nan, dtype=np.float64)
    theta = np.full(F.shape, np.nan, dtype=np.float64)
    bad = _finite_positive("F", F) | _finite_positive("K", K)
    bad |= ~np.isfinite(T) | (T < 0.0) | ~np.isfinite(discount) | (discount <= 0.0)
    bad |= ~np.isfinite(sigma) | (sigma < 0.0) | (sigma > SIGMA_BRACKET_HIGH)
    bad |= ~np.isfinite(r)
    status[bad] = STATUS_INVALID_INPUT
    zero = ~bad & (T == 0.0)
    status[zero] = STATUS_ZERO_T
    deg = ~bad & ~zero & (sigma == 0.0)
    status[deg] = STATUS_ENDPOINT_LOWER
    live = ~bad & ~zero & (sigma > 0.0)
    if np.any(live):
        st = sigma[live] * np.sqrt(T[live])
        d1 = (np.log(F[live] / K[live]) + 0.5 * sigma[live] ** 2 * T[live]) / st
        d2 = d1 - st
        cp = right[live].astype(np.float64)
        D = discount[live]
        n = _norm_pdf(d1)
        Ncp = ndtr(cp * d1)
        delta[live] = D * cp * Ncp
        gamma[live] = D * n / (F[live] * st)
        vega[live] = D * F[live] * n * np.sqrt(T[live])
        vanna[live] = -D * n * d2 / sigma[live]
        volga[live] = vega[live] * d1 * d2 / sigma[live]
        # d(delta)/dT_remaining at stated D,r; charm is calendar = -that.
        charm[live] = r[live] * delta[live] + D * n * d2 / (2.0 * T[live])
        theta[live] = r[live] * price[live] - D * F[live] * n * sigma[live] / (2.0 * np.sqrt(T[live]))
        tiny_idx = np.zeros(F.shape, dtype=bool)
        tiny_idx[live] = st < 1e-10
        status[tiny_idx] = status[tiny_idx] | FLAG_WEAK_VEGA
    return GreeksResult(
        price, delta, gamma, vega, vanna, charm, volga, status, residual, error,
        COORDINATE_FORWARD,
        ("sigma", "K", "right", "F_held_for_charm", "D_evolves_with_r"), theta=theta,
    )


def apply_contract_multiplier(values, multiplier, *,
                              source_unit="per_underlying_unit",
                              result_unit="per_contract"):
    """Unit-tagged per-contract scale. Not applied inside Black or American premia."""
    if source_unit != "per_underlying_unit" or result_unit != "per_contract":
        raise ContractError(
            "apply_contract_multiplier only maps per_underlying_unit -> per_contract"
        )
    x = _as_float("values", values)
    m = _as_float("multiplier", multiplier)
    if np.any(~np.isfinite(m) | (m <= 0.0)):
        raise ContractError("multiplier must be a positive finite contract factor")
    try:
        x, m = np.broadcast_arrays(x, m)
    except ValueError as exc:
        raise ContractError("values and multiplier are not broadcast-compatible") from exc
    return np.asarray(x * m, dtype=np.float64)


def _quote_interval_result(bid, mid, ask, model_lo, model_hi, valid_model, inverter,
                           tolerance, coordinate):
    shape = bid.shape
    inversions = [inverter(px) for px in (bid, mid, ask)]
    ib, im, ia = inversions
    permitted = (STATUS_CONVERGED, STATUS_ENDPOINT_LOWER, STATUS_ENDPOINT_UPPER)
    def certified(inv):
        return np.isfinite(inv.value) & np.isin(inv.status & STATUS_MASK, permitted)
    cb, cm, ca = (certified(inv) for inv in inversions)
    finite_bid, finite_mid, finite_ask = (np.isfinite(px) for px in (bid, mid, ask))
    missing_bid, missing_ask = ~finite_bid, ~finite_ask
    zero_bid = finite_bid & (bid == 0.0)
    crossed = finite_bid & finite_ask & (bid > ask)
    invalid = ~valid_model | (finite_bid & (bid < 0.0)) | (finite_ask & (ask < 0.0))
    invalid |= finite_mid & ((mid < 0.0) | (finite_bid & (mid < bid)) | (finite_ask & (mid > ask)))
    status = np.full(shape, STATUS_UNDEFINED_POINT, dtype=np.int32)
    status[missing_bid] |= FLAG_MISSING_BID
    status[missing_ask] |= FLAG_MISSING_ASK
    status[missing_bid & finite_ask] |= FLAG_ASK_ONLY
    status[zero_bid] |= FLAG_ZERO_BID
    ivs = [np.where(mask, inv.value, np.nan) for mask,inv in zip((cb,cm,ca),inversions)]
    ivs[0] = np.where(zero_bid & valid_model, 0.0, ivs[0])
    lower = np.where(finite_bid & (bid <= model_lo), 0.0, np.where(cb, ib.value, np.nan))
    upper = np.where(ca, ia.value, np.nan)
    empty = finite_ask & (ask < model_lo) | finite_bid & (bid > model_hi)
    bounds_ok = np.isfinite(lower) & np.isfinite(upper) & (lower <= upper)
    mid_ok = cm & ((im.status & STATUS_MASK) == STATUS_CONVERGED) & ((im.status & FLAG_WEAK_VEGA) == 0)
    defined = finite_bid & finite_mid & finite_ask & bounds_ok & mid_ok
    defined &= (im.value >= lower) & (im.value <= upper) & ~invalid & ~crossed & ~empty
    status[defined] = (status[defined] & ~STATUS_MASK) | STATUS_CONVERGED
    unbounded = ~bounds_ok & ~empty & ~invalid & ~crossed
    status[unbounded] = (status[unbounded] & ~STATUS_MASK) | STATUS_UNBOUNDED_SIDE
    # Preserve a numerical failure as such; every side also retains its own status.
    for inv, present in ((ib, finite_bid & (bid > model_lo)), (im,finite_mid), (ia,finite_ask)):
        failed = present & ~np.isin(inv.status & STATUS_MASK, permitted) & ~defined & ~empty
        status[failed] = (status[failed] & ~STATUS_MASK) | (inv.status[failed] & STATUS_MASK)
    status[empty] = STATUS_FAILED_BRACKET
    status[invalid] = STATUS_INVALID_INPUT
    status[crossed] = STATUS_CROSSED_QUOTES
    status[~defined] |= FLAG_POINT_UNDEFINED
    void = invalid | crossed | empty
    lower[void], upper[void] = np.nan, np.nan
    for iv in ivs: iv[void] = np.nan
    errors = [np.full(shape,np.nan) if inv.error is None else inv.error for inv in inversions]
    return QuoteIVResult(
        iv_bid=ivs[0], iv_mid=ivs[1], iv_ask=ivs[2], iv_lower=lower, iv_upper=upper,
        price_bid=bid, price_mid=mid, price_ask=ask, model_price_lower=model_lo, model_price_upper=model_hi,
        point_iv=np.where(defined, im.value, np.nan), point_defined=defined, status=status,
        residual_bid=ib.residual, residual_mid=im.residual, residual_ask=ia.residual,
        status_bid=ib.status, status_mid=im.status, status_ask=ia.status,
        error_bid=errors[0], error_mid=errors[1], error_ask=errors[2], coordinate=coordinate,
        iterations=sum(inv.iterations for inv in inversions), solver_price_tolerance=tolerance,
        market_interval=np.stack((bid,ask),axis=-1))


def invert_quote_interval(bid, mid, ask, F, K, T, discount, right, *,
                          volatility_unit=VOLATILITY_UNIT, style="european"):
    """Conditional quote interval with separate side diagnostics and numerical error."""
    _reject_style(style, 'european'); _reject_vol_unit(volatility_unit)
    try:
        bid,mid,ask,F,K,T,discount,_ = np.broadcast_arrays(
            *[_as_float('quote input',x) for x in (bid,mid,ask,F,K,T,discount)],np.asarray(right))
    except ValueError as exc:
        raise ContractError('quote interval inputs are not broadcast-compatible') from exc
    cp = encode_right(right,F.shape)
    lower = black_price(F,K,T,0.0,discount,cp)
    _,upper = _european_bounds(F,K,T,discount,cp)
    valid = np.isfinite(lower.value) & (T > 0.0)
    return _quote_interval_result(bid,mid,ask,lower.value,upper,valid,
        lambda px:black_iv(px,F,K,T,discount,cp),
        _european_price_tolerance(np.where(np.isfinite(mid),mid,ask)), COORDINATE_FORWARD)


def invert_american_quote_interval(bid, mid, ask, S, K, T, r, right, *,
                                   dividend_times=None, dividend_amounts=None, n_space=128, n_time=None):
    """American conditional interval; q=0 with the stated discrete cash schedule."""
    try:
        bid,mid,ask,S,K,T,r,_ = np.broadcast_arrays(
            *[_as_float('quote input',x) for x in (bid,mid,ask,S,K,T,r)],np.asarray(right))
    except ValueError as exc:
        raise ContractError('American quote inputs are not broadcast-compatible') from exc
    options = dict(dividend_times=dividend_times,dividend_amounts=dividend_amounts,n_space=n_space,n_time=n_time)
    cp = encode_right(right,S.shape)
    lower = native_price_batch(S,K,T,0.0,r,cp,**options)
    upper = np.where(cp > 0,S,K*np.maximum(1.0,np.exp(-r*T)))
    valid = np.isfinite(lower.value) & (T > 0.0)
    tol = np.maximum(1e-6,1e-8*np.maximum(1.0,np.abs(np.where(np.isfinite(mid),mid,ask))))
    return _quote_interval_result(bid,mid,ask,lower.value,upper,valid,
        lambda px:american_iv(px,S,K,T,r,cp,**options),tol,COORDINATE_SPOT)


def _calendar_discount(discount, r, d_remaining):
    return np.asarray(discount, dtype=np.float64) * np.exp(-np.asarray(r, dtype=np.float64) * d_remaining)


def response_cube(F, K, T, sigma, discount, right, r, *,
                  coordinate_relative_shocks=COORDINATE_RELATIVE_SHOCKS_DEFAULT,
                  sigma_additive_shocks=SIGMA_ADDITIVE_SHOCKS_DEFAULT,
                  calendar_seconds=CALENDAR_SECONDS_DEFAULT,
                  style="european", volatility_unit=VOLATILITY_UNIT, multiplier=None):
    """Full joint Black repricing at the frozen shock lattice. No cross-contract mix."""
    _reject_multiplier(multiplier)
    core = black_greeks(F, K, T, sigma, discount, right, r,
                        volatility_unit=volatility_unit, style=style)
    F = np.broadcast_to(_as_float("F", F), core.price.shape).copy()
    K = np.broadcast_to(_as_float("K", K), core.price.shape).copy()
    T = np.broadcast_to(_as_float("T", T), core.price.shape).copy()
    sigma = np.broadcast_to(_as_float("sigma", sigma), core.price.shape).copy()
    discount = np.broadcast_to(_as_float("discount", discount), core.price.shape).copy()
    r = np.broadcast_to(_as_float("r", r), core.price.shape).copy()
    right = encode_right(right, core.price.shape)
    dF = np.asarray(coordinate_relative_shocks, dtype=np.float64)
    dS = np.asarray(sigma_additive_shocks, dtype=np.float64)
    cal = np.asarray(calendar_seconds, dtype=np.float64)
    dT = years_from_seconds(cal)
    shape = core.price.shape + (dF.size, dS.size, cal.size)
    price = np.full(shape, np.nan, dtype=np.float64)
    status = np.full(shape, STATUS_INVALID_INPUT, dtype=np.int32)
    taylor = np.full(shape, np.nan, dtype=np.float64)
    for i, rf in enumerate(dF):
        for j, ds in enumerate(dS):
            for k, dt in enumerate(dT):
                Fn = F * (1.0 + rf)
                sn = sigma + ds
                Tn = T - dt
                Dn = _calendar_discount(discount, r, -dt)
                bad = (Tn < 0.0) | (sn < 0.0) | (sn > 10) | (Fn <= 0.0)
                quoted = black_price(Fn, K, np.maximum(Tn, 0.0), np.where(sn > 10,np.nan,np.maximum(sn,0.0)), Dn, right)
                price[..., i, j, k] = np.where(bad, np.nan, quoted.value)
                st = quoted.status.copy()
                st[bad] = STATUS_INVALID_INPUT | FLAG_NONPOSITIVE_DOMAIN
                status[..., i, j, k] = st
                dFabs = F * rf
                taylor[..., i, j, k] = (
                    core.price + core.delta * dFabs + core.vega * ds + core.theta * dt
                    + 0.5 * core.gamma * dFabs ** 2 + 0.5 * core.volga * ds ** 2
                    + core.vanna * dFabs * ds + core.charm * dFabs * dt
                )
    return ResponseCube(
        price=price, status=status, taylor_price=taylor,
        taylor_residual=price - taylor,
        coordinate_relative_shocks=dF, sigma_additive_shocks=dS,
        calendar_seconds=cal, calendar_years=dT, coordinate=COORDINATE_FORWARD,
    )


def american_domain(S, K, T, sigma, r, dividend_amounts=None):
    """Strike-centered log domain; caller fixes this domain across derivative bumps."""
    S, K, T, sigma, r = np.broadcast_arrays(*map(lambda v: np.asarray(v, dtype=np.float64), (S,K,T,sigma,r)))
    if dividend_amounts is None:
        cash = np.zeros(S.shape)
    elif S.size == 1:
        cash = np.full(S.shape, np.asarray(dividend_amounts, dtype=np.float64).sum())
    else:
        if len(dividend_amounts) != S.size:
            raise ContractError('per-row dividend amounts must match domain batch')
        cash = np.asarray([np.asarray(row, dtype=np.float64).sum() for row in dividend_amounts]).reshape(S.shape)
    st = sigma * np.sqrt(np.maximum(T, 0.0))
    span = np.maximum(7.0 * st, 1e-4) + np.abs(r - 0.5 * sigma**2) * T
    span += np.maximum(np.abs(np.log(S / K)), np.log1p(cash / np.minimum(S, K)))
    return K * np.exp(-np.minimum(span, 690.0)), K * np.exp(np.minimum(span, 690.0))


def _pack_dividends(n, dividend_times, dividend_amounts):
    if dividend_times is None and dividend_amounts is None:
        offsets = np.zeros(n + 1, dtype=np.int64)
        return offsets, np.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.float64), 0
    if dividend_times is None or dividend_amounts is None:
        raise ContractError("dividend times and amounts must be stated together")
    times = []
    amounts = []
    offsets = [0]
    if n == 1 and np.ndim(dividend_times) == 1 and not _is_ragged(dividend_times):
        t = np.asarray(dividend_times, dtype=np.float64).ravel()
        a = np.asarray(dividend_amounts, dtype=np.float64).ravel()
        if t.size != a.size:
            raise ContractError("dividend times/amounts length mismatch")
        times.extend(t.tolist())
        amounts.extend(a.tolist())
        offsets.append(len(times))
    else:
        if len(dividend_times) != n or len(dividend_amounts) != n:
            raise ContractError("per-row dividend CSR length must match the batch")
        for t_row, a_row in zip(dividend_times, dividend_amounts):
            if t_row is None or a_row is None:
                raise ContractError("unknown dividend row is not known zero")
            t = np.asarray(t_row, dtype=np.float64).ravel()
            a = np.asarray(a_row, dtype=np.float64).ravel()
            if t.size != a.size:
                raise ContractError("dividend times/amounts length mismatch")
            times.extend(t.tolist())
            amounts.extend(a.tolist())
            offsets.append(len(times))
    n_div = len(times)
    if n_div == 0:
        return np.asarray(offsets, dtype=np.int64), np.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.float64), 0
    return (
        np.asarray(offsets, dtype=np.int64),
        np.asarray(times, dtype=np.float64),
        np.asarray(amounts, dtype=np.float64),
        n_div,
    )


def _is_ragged(seq):
    if isinstance(seq, np.ndarray) and seq.dtype != object and seq.ndim == 1:
        return False
    return isinstance(seq, (list, tuple)) and any(isinstance(x, (list, tuple, np.ndarray)) for x in seq)


def enable_native(path, sha256):
    """Authenticate a root-built shared library and bind the C ABI. No compile."""
    global _LIBRARY, _PRICE_FN, _IV_FN, _SINGLE_PRICE_FN
    path = Path(path)
    if not path.is_file() or path.stat().st_size > NATIVE_MAX_BYTES:
        raise IntegrityError("native binary absent or exceeds registered bound")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != sha256:
        raise IntegrityError("compiled American valuation artifact differs from its registered build")
    library = ctypes.CDLL(str(path))
    in_f = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    out_f = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS, WRITEABLE")
    in_i32 = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
    out_i32 = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS, WRITEABLE")
    in_i64 = np.ctypeslib.ndpointer(dtype=np.int64, flags="C_CONTIGUOUS")
    price = library.american_price_batch
    price.argtypes = [
        ctypes.c_int64,
        in_f, in_f, in_f, in_f, in_f, in_i32,
        in_i64, ctypes.c_int64, in_f, in_f,
        ctypes.c_int32, ctypes.c_int32,
        in_f, in_f,
        out_f, out_f, out_f, out_i32, out_i32,
    ]
    price.restype = ctypes.c_int
    iv = library.american_iv_batch
    iv.argtypes = [
        ctypes.c_int64,
        in_f, in_f, in_f, in_f, in_f, in_i32,
        in_i64, ctypes.c_int64, in_f, in_f,
        ctypes.c_int32, ctypes.c_int32,
        in_f, in_f,
        out_f, out_f, out_f, out_f, out_i32, out_i32,
    ]
    iv.restype = ctypes.c_int
    single = library.american_price_single_grid_batch
    single.argtypes, single.restype = price.argtypes, price.restype
    _LIBRARY, _PRICE_FN, _IV_FN, _SINGLE_PRICE_FN = library, price, iv, single
    return digest


def native_enabled():
    return _PRICE_FN is not None


def _require_enabled():
    if _PRICE_FN is None or _IV_FN is None:
        raise DependencyUnavailable(
            "native American library is not enabled; root must compile and call enable_native"
        )


def _batch_core(S, K, T, sigma, r, right, dividend_times, dividend_amounts,
                n_space, n_time, domain_low, domain_high):
    arrays = [_as_float(name, value) for name, value in (('S',S),('K',K),('T',T),('r',r))]
    if sigma is not None:
        arrays.append(_as_float('sigma', sigma))
    try:
        broadcast = np.broadcast_arrays(*arrays, np.asarray(right))
    except ValueError as exc:
        raise ContractError('American inputs are not broadcast-compatible') from exc
    shape = broadcast[0].shape
    S, K, T, r = [np.ascontiguousarray(v, dtype=np.float64).reshape(-1) for v in broadcast[:4]]
    sig = None if sigma is None else np.ascontiguousarray(broadcast[4], dtype=np.float64).reshape(-1)
    if sig is not None and np.any(sig > SIGMA_BRACKET_HIGH):
        raise ContractError('volatility must be a fraction in [0,10]')
    rights = np.ascontiguousarray(encode_right(right, shape), dtype=np.int32).reshape(-1)
    n = S.size
    ns, nt = (128 if n_space is None else n_space), (0 if n_time is None else n_time)
    if int(ns) != ns or int(nt) != nt or not 32 <= ns <= 2048 or not 0 <= nt <= 8192:
        raise ContractError('invalid bounded American grid')
    if (domain_low is None) != (domain_high is None):
        raise ContractError('both domain bounds must be stated')
    if domain_low is None:
        lo, hi = np.full(n, np.nan), np.full(n, np.nan)
    else:
        lo = np.ascontiguousarray(np.broadcast_to(_as_float('domain_low',domain_low),shape)).reshape(-1)
        hi = np.ascontiguousarray(np.broadcast_to(_as_float('domain_high',domain_high),shape)).reshape(-1)
    off, dt, da, nd = _pack_dividends(n, dividend_times, dividend_amounts)
    if np.any(np.diff(off) > 8701):
        raise ContractError('per-row dividend count exceeds native bound')
    # Sort each known schedule; duplicate instants are a single summed cash jump.
    for row in range(n):
        start, end = off[row:row+2]
        order = np.argsort(dt[start:end], kind='stable')
        dt[start:end], da[start:end] = dt[start:end][order], da[start:end][order]
    return {'shape':shape, 'S':S, 'K':K, 'T':T, 'r':r, 'sigma':sig, 'right':rights,
            'off':off, 'dt':dt, 'da':da, 'nd':nd, 'n':n, 'n_space':int(ns), 'n_time':int(nt),
            'lo':lo, 'hi':hi}


def native_price_batch(S, K, T, sigma, r, right, *,
                       dividend_times=None, dividend_amounts=None,
                       n_space=128, n_time=None,
                       domain_low=None, domain_high=None,
                       volatility_unit=VOLATILITY_UNIT, style="american", multiplier=None, _single_grid=False):
    """Batch native American prices. One failed row does not rewrite other rows."""
    _require_enabled()
    _reject_style(style, "american")
    _reject_vol_unit(volatility_unit)
    _reject_multiplier(multiplier)
    spec = _batch_core(S, K, T, sigma, r, right, dividend_times, dividend_amounts,
                       n_space, n_time, domain_low, domain_high)
    n = spec["n"]
    price = np.full(n, np.nan, dtype=np.float64)
    error = np.full(n, np.nan, dtype=np.float64)
    residual = np.full(n, np.nan, dtype=np.float64)
    status = np.full(n, STATUS_INVALID_INPUT, dtype=np.int32)
    iterations = np.zeros(n, dtype=np.int32)
    price_function = _SINGLE_PRICE_FN if _single_grid else _PRICE_FN
    rc = price_function(
        n, spec["S"], spec["K"], spec["T"], spec["sigma"], spec["r"], spec["right"],
        spec["off"], spec["nd"], spec["dt"], spec["da"],
        spec["n_space"], spec["n_time"], spec["lo"], spec["hi"],
        price, error, residual, status, iterations,
    )
    if rc != 0:
        status[:] = STATUS_ABI_ERROR
        price[:] = np.nan
    certified = np.isin(status & STATUS_MASK, (STATUS_CONVERGED, STATUS_ZERO_T, STATUS_SIGMA0_DETERMINISTIC))
    price[~certified] = np.nan
    shape = spec["shape"]
    return ArrayResult(
        price.reshape(shape), status.reshape(shape), residual.reshape(shape),
        iterations.reshape(shape), error=error.reshape(shape),
        coordinate=COORDINATE_SPOT,
    )


def american_iv(price, S, K, T, r, right, *,
                dividend_times=None, dividend_amounts=None,
                n_space=128, n_time=None,
                domain_low=None, domain_high=None,
                volatility_unit=VOLATILITY_UNIT, style="american", multiplier=None):
    """American IV via C++ bracketed iterations on the same FD engine."""
    _require_enabled()
    _reject_style(style, "american")
    _reject_vol_unit(volatility_unit)
    _reject_multiplier(multiplier)
    try:
        price, S, K, T, r, _ = np.broadcast_arrays(_as_float('price',price), _as_float('S',S),
            _as_float('K',K), _as_float('T',T), _as_float('r',r), np.asarray(right))
    except ValueError as exc:
        raise ContractError('American IV inputs are not broadcast-compatible') from exc
    spec = _batch_core(S, K, T, None, r, right, dividend_times, dividend_amounts,
                       n_space, n_time, domain_low, domain_high)
    try:
        price = np.broadcast_to(price, spec["shape"]).reshape(spec["n"])
    except ValueError as exc:
        raise ContractError("American IV price is not broadcast-compatible") from exc
    price = np.ascontiguousarray(price, dtype=np.float64)
    n = spec["n"]
    iv = np.full(n, np.nan, dtype=np.float64)
    residual = np.full(n, np.nan, dtype=np.float64)
    blo = np.full(n, np.nan, dtype=np.float64)
    bhi = np.full(n, np.nan, dtype=np.float64)
    status = np.full(n, STATUS_INVALID_INPUT, dtype=np.int32)
    iterations = np.zeros(n, dtype=np.int32)
    rc = _IV_FN(
        n, price, spec["S"], spec["K"], spec["T"], spec["r"], spec["right"],
        spec["off"], spec["nd"], spec["dt"], spec["da"],
        spec["n_space"], spec["n_time"], spec["lo"], spec["hi"],
        iv, residual, blo, bhi, status, iterations,
    )
    if rc != 0:
        status[:] = STATUS_ABI_ERROR
        iv[:] = np.nan
    shape = spec['shape']
    # Independently reprice returned volatilities; grid error is distinct from IV residual.
    repriced = native_price_batch(S, K, T, iv.reshape(shape), r, right,
        dividend_times=dividend_times, dividend_amounts=dividend_amounts,
        n_space=n_space, n_time=n_time, domain_low=domain_low, domain_high=domain_high)
    error = repriced.error.reshape(-1)
    accepted = np.isin(status & STATUS_MASK, (STATUS_CONVERGED, STATUS_ENDPOINT_LOWER, STATUS_ENDPOINT_UPPER))
    tolerance = np.maximum(1e-6, 1e-8 * np.maximum(1.0, np.abs(price)))
    reprice_residual = repriced.value.reshape(-1) - price
    certified = np.isfinite(reprice_residual) & (np.abs(reprice_residual) <= tolerance)
    bad = accepted & ~certified
    status[bad] = STATUS_NONCONVERGED | FLAG_GRID_ERROR
    residual[accepted] = reprice_residual[accepted]
    iv[~accepted | bad] = np.nan
    return ArrayResult(
        iv.reshape(shape), status.reshape(shape), residual.reshape(shape),
        iterations.reshape(shape), blo.reshape(shape), bhi.reshape(shape), error=error.reshape(shape),
        coordinate=COORDINATE_SPOT, unit=VOLATILITY_UNIT,
    )


def american_greeks(S, K, T, sigma, r, right, *,
                    dividend_times=None, dividend_amounts=None,
                    n_space=128, n_time=None, spot_steps=None, vol_steps=None,
                    calendar_years=None, grids=None, volatility_unit=VOLATILITY_UNIT,
                    style="american", multiplier=None):
    """Spot derivatives with independent grids and two finite-difference steps.

    Each derivative has its own dimensional error and status. Values failing
    the final grid/step comparison are unavailable; raw diagnostics are separate.
    """
    _reject_style(style,'american'); _reject_vol_unit(volatility_unit); _reject_multiplier(multiplier)
    spec = _batch_core(S,K,T,sigma,r,right,dividend_times,dividend_amounts,n_space,n_time,None,None)
    base = native_price_batch(S,K,T,sigma,r,right,dividend_times=dividend_times,
                              dividend_amounts=dividend_amounts,n_space=n_space,n_time=n_time)
    shape,n = spec['shape'],spec['n']
    grids = tuple(grids or (128,256,512))
    if len(grids) < 2 or len(set(grids)) != len(grids) or list(grids) != sorted(grids):
        raise ContractError('at least two increasing independent grids required')
    if any(type(g) is not int or g < 32 or g > 2048 for g in grids):
        raise ContractError('invalid independent Greek grid')
    names = ('delta','gamma','vega','vanna','charm','volga','theta')
    values = {name:np.full(n,np.nan) for name in names}
    errors = {name:np.full(n,np.nan) for name in names}
    statuses = {name:np.full(n,STATUS_UNSTABLE_GREEK,dtype=np.int32) for name in names}
    raw = {name:np.full((n,len(grids),2),np.nan) for name in names}
    step_diff = {name:np.full((n,len(grids)),np.nan) for name in names}
    grid_diff = {name:np.full((n,len(grids)-1,2),np.nan) for name in names}
    abs_tol = dict(delta=1e-4,gamma=1e-6,vega=1e-3,vanna=1e-4,charm=1e-4,volga=1e-3,theta=1e-3)
    rel_tol = dict(delta=.02,gamma=.03,vega=.02,vanna=.05,charm=.05,volga=.05,theta=.02)
    price_error = base.error.reshape(-1).copy()
    max_residual = base.residual.reshape(-1).copy()
    def two_steps(given,defaults,row):
        if given is None: return defaults
        if len(given) != 2: raise ContractError('exactly two derivative step sizes required')
        return tuple(float(np.broadcast_to(np.asarray(v,dtype=np.float64),shape).reshape(-1)[row]) for v in given)
    for row in range(n):
        sv,kv,tv,vv,rv = (float(spec[k][row]) for k in ('S','K','T','sigma','r'))
        cp = int(spec['right'][row])
        start,end = spec['off'][row:row+2]
        times,amounts = spec['dt'][start:end],spec['da'][start:end]
        if not np.isfinite(base.value.reshape(-1)[row]) or tv <= 0 or vv <= 0:
            for name in names: statuses[name][row] = int(base.status.reshape(-1)[row]) if tv <= 0 else STATUS_UNSTABLE_GREEK
            continue
        hs = two_steps(spot_steps,(sv*.001,sv*.002),row)
        hv2 = min(.002,vv/4)
        hv = two_steps(vol_steps,(hv2/2,hv2),row)
        ht2 = min(2/365,tv/4,float(times.min()/4) if times.size else tv/4)
        ht = two_steps(calendar_years,(ht2/2,ht2),row)
        if any(not (0 < pair[0] < pair[1]) for pair in (hs,hv,ht)):
            raise ContractError('positive increasing two-step sizes required')
        if sv <= hs[1] or vv <= hv[1] or vv+hv[1] > 10 or tv <= ht[1] or (times.size and times.min() <= ht[1]):
            continue
        low,high = american_domain(sv+hs[1],kv,tv+ht[1],vv+hv[1],rv,amounts)
        cache = {}
        def px(grid,spot=0.,vol=0.,calendar=0.):
            key=(grid,spot,vol,calendar)
            if key not in cache:
                result=native_price_batch(sv+spot,kv,tv-calendar,vv+vol,rv,cp,
                    dividend_times=times-calendar,dividend_amounts=amounts,
                    n_space=grid,n_time=grid if n_time in (None,0) else int(n_time*grid/grids[0]),
                    domain_low=low,domain_high=high,_single_grid=True)
                cache[key]=float(result.value)
                if np.isfinite(float(result.residual)):
                    max_residual[row]=max(max_residual[row],float(result.residual))
            return cache[key]
        for gi,grid in enumerate(grids):
            center=px(grid)
            for si,(h,v,t) in enumerate(zip(hs,hv,ht)):
                up,dn=px(grid,spot=h),px(grid,spot=-h)
                vu,vd=px(grid,vol=v),px(grid,vol=-v)
                tu,td=px(grid,calendar=t),px(grid,calendar=-t)
                raw['delta'][row,gi,si]=(up-dn)/(2*h)
                raw['gamma'][row,gi,si]=(up-2*center+dn)/(h*h)
                raw['vega'][row,gi,si]=(vu-vd)/(2*v)
                raw['volga'][row,gi,si]=(vu-2*center+vd)/(v*v)
                raw['theta'][row,gi,si]=(tu-td)/(2*t)
                raw['vanna'][row,gi,si]=(px(grid,h,v)-px(grid,h,-v)-px(grid,-h,v)+px(grid,-h,-v))/(4*h*v)
                raw['charm'][row,gi,si]=(px(grid,h,calendar=t)-px(grid,-h,calendar=t)
                    -px(grid,h,calendar=-t)+px(grid,-h,calendar=-t))/(4*h*t)
        if np.isfinite(px(grids[-1])):
            price_error[row]=max(price_error[row],abs(px(grids[-1])-base.value.reshape(-1)[row]))
        for name in names:
            estimates=raw[name][row]
            step_diff[name][row]=np.abs(estimates[:,0]-estimates[:,1])
            grid_diff[name][row]=np.abs(estimates[1:]-estimates[:-1])
            if not np.all(np.isfinite(estimates)): continue
            value=estimates[-1,0]
            error=max(step_diff[name][row,-1],float(grid_diff[name][row,-1].max()))
            errors[name][row]=error
            if error <= abs_tol[name]+rel_tol[name]*abs(value):
                values[name][row]=value
                statuses[name][row]=STATUS_CONVERGED
    overall=base.status.reshape(-1).copy()
    unstable=np.zeros(n,dtype=bool)
    for name in names: unstable |= statuses[name] != STATUS_CONVERGED
    overall[unstable & np.isfinite(base.value.reshape(-1))]=STATUS_UNSTABLE_GREEK|FLAG_UNSTABLE_GREEK
    return GreeksResult(base.value,*(values[name].reshape(shape) for name in names[:6]),
        overall.reshape(shape),max_residual.reshape(shape),price_error.reshape(shape),COORDINATE_SPOT,
        ('r','K','right','known_discrete_cash_schedule','spot_held_for_calendar','fixed_space_domain'),
        theta=values['theta'].reshape(shape),
        greek_errors={name:errors[name].reshape(shape) for name in names},
        greek_status={name:statuses[name].reshape(shape) for name in names},
        step_differences={name:step_diff[name].reshape(shape+(len(grids),)) for name in names},
        grid_differences={name:grid_diff[name].reshape(shape+(len(grids)-1,2)) for name in names},
        raw_greeks={name:raw[name].reshape(shape+(len(grids),2)) for name in names})


def american_response_cube(S,K,T,sigma,r,right,*,dividend_times=None,dividend_amounts=None,
                            coordinate_relative_shocks=COORDINATE_RELATIVE_SHOCKS_DEFAULT,
                            sigma_additive_shocks=SIGMA_ADDITIVE_SHOCKS_DEFAULT,
                            calendar_seconds=CALENDAR_SECONDS_DEFAULT,n_space=128,n_time=None):
    """Full American repricing; calendar shocks remove elapsed cash dividends."""
    core=american_greeks(S,K,T,sigma,r,right,dividend_times=dividend_times,
                         dividend_amounts=dividend_amounts,n_space=n_space,n_time=n_time)
    spec=_batch_core(S,K,T,sigma,r,right,dividend_times,dividend_amounts,n_space,n_time,None,None)
    shape=spec['shape'];coord=np.asarray(coordinate_relative_shocks,dtype=float)
    vols=np.asarray(sigma_additive_shocks,dtype=float);seconds=np.asarray(calendar_seconds,dtype=float)
    years=years_from_seconds(seconds); outshape=shape+(len(coord),len(vols),len(years))
    prices=np.full(outshape,np.nan);statuses=np.full(outshape,STATUS_INVALID_INPUT,dtype=np.int32)
    taylor=np.full(outshape,np.nan)
    def contribution(value,shock):
        return np.where(np.asarray(shock)==0,0.0,value*shock)
    for i,relative in enumerate(coord):
        ds=spec['S'].reshape(shape)*relative
        for j,dv in enumerate(vols):
            for k,dt in enumerate(years):
                times,amounts=[],[]
                for row in range(spec['n']):
                    a,b=spec['off'][row:row+2]; shifted=spec['dt'][a:b]-dt
                    keep=shifted>0;times.append(shifted[keep]);amounts.append(spec['da'][a:b][keep])
                if spec['n']==1: times,amounts=times[0],amounts[0]
                result=native_price_batch((spec['S']*(1+relative)).reshape(shape),spec['K'].reshape(shape),
                    (spec['T']-dt).reshape(shape),np.where(spec['sigma']+dv > 10,np.nan,spec['sigma']+dv).reshape(shape),spec['r'].reshape(shape),
                    spec['right'].reshape(shape),dividend_times=times,dividend_amounts=amounts,
                    n_space=n_space,n_time=n_time)
                prices[...,i,j,k]=result.value;statuses[...,i,j,k]=result.status
                taylor[...,i,j,k]=core.price+contribution(core.delta,ds)+contribution(core.vega,dv)
                taylor[...,i,j,k]+=contribution(core.theta,dt)+contribution(core.gamma,.5*ds*ds)
                taylor[...,i,j,k]+=contribution(core.volga,.5*dv*dv)+contribution(core.vanna,ds*dv)
                taylor[...,i,j,k]+=contribution(core.charm,ds*dt)
    return ResponseCube(price=prices,status=statuses,taylor_price=taylor,taylor_residual=prices-taylor,
        coordinate_relative_shocks=coord,sigma_additive_shocks=vols,calendar_seconds=seconds,
        calendar_years=years,coordinate=COORDINATE_SPOT)
