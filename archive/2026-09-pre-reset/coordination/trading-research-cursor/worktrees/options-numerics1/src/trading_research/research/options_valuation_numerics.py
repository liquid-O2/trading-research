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
        "price", "delta", "gamma", "vega", "vanna", "charm", "volga",
        "status", "residual", "error", "coordinate", "held_fixed",
        "volatility_unit", "time_unit", "model_version",
    )

    def __init__(self, price, delta, gamma, vega, vanna, charm, volga,
                 status, residual, error, coordinate, held_fixed):
        self.price = np.asarray(price, dtype=np.float64)
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
        "residual_bid", "residual_mid", "residual_ask",
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
        it = np.nditer(raw, flags=["multi_index", "refs_ok"])
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
    vals = np.asarray(right, dtype=np.int32)
    if np.any((vals != 1) & (vals != -1)):
        raise ContractError("right must be +1 (call) or -1 (put)")
    return np.broadcast_to(vals, shape).copy()


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
        F, K, T, sigma, discount = np.broadcast_arrays(F, K, T, sigma, discount)
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
        price, F, K, T, discount = np.broadcast_arrays(price, F, K, T, discount)
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
            tight = leftover & (np.abs(residual) <= 10.0 * tol)
            status[tight] = STATUS_CONVERGED
            status[leftover & ~tight] = STATUS_NONCONVERGED
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
        tiny_idx = np.zeros(F.shape, dtype=bool)
        tiny_idx[live] = st < 1e-10
        status[tiny_idx] = status[tiny_idx] | FLAG_WEAK_VEGA
    return GreeksResult(
        price, delta, gamma, vega, vanna, charm, volga, status, residual, error,
        COORDINATE_FORWARD,
        ("sigma", "K", "right", "F_held_for_charm", "D_evolves_with_r"),
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


def invert_quote_interval(bid, mid, ask, F, K, T, discount, right, *,
                          volatility_unit=VOLATILITY_UNIT, style="european"):
    """Conditional bid/mid/ask IV. Missing/zero bid does not drop an ask upper bound.

    Market quote interval is distinct from solver price tolerance. A mid inversion
    is never reported as a stand-alone accuracy claim.
    """
    _reject_style(style, "european")
    _reject_vol_unit(volatility_unit)
    bid = _as_float("bid", bid)
    mid = _as_float("mid", mid)
    ask = _as_float("ask", ask)
    F = _as_float("F", F)
    K = _as_float("K", K)
    T = _as_float("T", T)
    discount = _as_float("discount", discount)
    try:
        bid, mid, ask, F, K, T, discount = np.broadcast_arrays(
            bid, mid, ask, F, K, T, discount
        )
    except ValueError as exc:
        raise ContractError("quote interval inputs are not broadcast-compatible") from exc
    right = encode_right(right, F.shape)
    cp = right.astype(np.float64)
    model_lo, model_hi = _european_bounds(F, K, T, discount, cp)
    status = np.full(F.shape, STATUS_CONVERGED, dtype=np.int32)
    have_bid = np.isfinite(bid) & (bid > 0.0)
    zero_bid = np.isfinite(bid) & (bid == 0.0)
    miss_bid = ~np.isfinite(bid)
    have_ask = np.isfinite(ask) & (ask > 0.0)
    miss_ask = ~np.isfinite(ask) | (ask <= 0.0)
    have_mid = np.isfinite(mid) & (mid > 0.0)
    status[zero_bid] |= FLAG_ZERO_BID
    status[miss_bid] |= FLAG_MISSING_BID
    status[miss_ask] |= FLAG_MISSING_ASK
    status[have_ask & ~have_bid & ~zero_bid] |= FLAG_ASK_ONLY
    crossed = have_bid & have_ask & (bid > ask)
    status[crossed] = STATUS_CROSSED_QUOTES | FLAG_POINT_UNDEFINED
    iv_bid = np.full(F.shape, np.nan, dtype=np.float64)
    iv_mid = np.full(F.shape, np.nan, dtype=np.float64)
    iv_ask = np.full(F.shape, np.nan, dtype=np.float64)
    res_b = np.full(F.shape, np.nan, dtype=np.float64)
    res_m = np.full(F.shape, np.nan, dtype=np.float64)
    res_a = np.full(F.shape, np.nan, dtype=np.float64)
    it_acc = np.zeros(F.shape, dtype=np.int32)

    def _side(px, dest_iv, dest_res, mask):
        if not np.any(mask):
            return
        inv = black_iv(px, F, K, T, discount, right)
        dest_iv[mask] = inv.value[mask]
        dest_res[mask] = inv.residual[mask]
        it_acc[mask] = np.maximum(it_acc[mask], inv.iterations[mask])
        flags = (status[mask] | inv.status[mask]) & ~STATUS_MASK
        status[mask] = (status[mask] & STATUS_MASK) | flags

    _side(bid, iv_bid, res_b, have_bid & ~crossed)
    _side(ask, iv_ask, res_a, have_ask & ~crossed)
    _side(mid, iv_mid, res_m, have_mid & ~crossed)
    at_bound_lo = zero_bid & ~crossed
    iv_bid[at_bound_lo] = 0.0
    status[at_bound_lo] = (status[at_bound_lo] & ~STATUS_MASK) | STATUS_ENDPOINT_LOWER
    status[at_bound_lo] |= FLAG_ZERO_BID

    iv_lower = np.full(F.shape, np.nan, dtype=np.float64)
    iv_upper = np.full(F.shape, np.nan, dtype=np.float64)
    iv_lower[have_bid & ~crossed] = iv_bid[have_bid & ~crossed]
    iv_lower[at_bound_lo] = 0.0
    iv_upper[have_ask & ~crossed] = iv_ask[have_ask & ~crossed]
    unbounded = (miss_bid & ~zero_bid & ~have_bid) | miss_ask | crossed
    status[unbounded & ~crossed & miss_bid & have_ask] = (
        (status[unbounded & ~crossed & miss_bid & have_ask] & ~STATUS_MASK) | STATUS_UNBOUNDED_SIDE
    )
    status[unbounded & ~crossed & miss_ask & have_bid] = (
        (status[unbounded & ~crossed & miss_ask & have_bid] & ~STATUS_MASK) | STATUS_UNBOUNDED_SIDE
    )
    point = np.full(F.shape, np.nan, dtype=np.float64)
    defined = have_mid & ~crossed & np.isfinite(iv_mid)
    weak = (status & FLAG_WEAK_VEGA) != 0
    failed_pt = defined & (
        ((status & STATUS_MASK) == STATUS_FAILED_BRACKET)
        | ((status & STATUS_MASK) == STATUS_UNDEFINED_POINT)
        | ((status & STATUS_MASK) == STATUS_ZERO_T)
        | weak
        | ~np.isfinite(iv_lower)
        | ~np.isfinite(iv_upper)
    )
    point[defined & ~failed_pt] = iv_mid[defined & ~failed_pt]
    point_defined = defined & ~failed_pt & np.isfinite(iv_lower) & np.isfinite(iv_upper)
    status[~point_defined] |= FLAG_POINT_UNDEFINED
    undef = ~point_defined & ~crossed
    mask_u = undef & (
        ((status & STATUS_MASK) == STATUS_CONVERGED)
        | ((status & STATUS_MASK) == STATUS_UNBOUNDED_SIDE)
    )
    status[mask_u] = (status[mask_u] & ~STATUS_MASK) | STATUS_UNDEFINED_POINT
    return QuoteIVResult(
        iv_bid=iv_bid, iv_mid=iv_mid, iv_ask=iv_ask,
        iv_lower=iv_lower, iv_upper=iv_upper,
        price_bid=bid, price_mid=mid, price_ask=ask,
        model_price_lower=model_lo, model_price_upper=model_hi,
        point_iv=point, point_defined=point_defined, status=status,
        residual_bid=res_b, residual_mid=res_m, residual_ask=res_a,
        iterations=it_acc,
        solver_price_tolerance=_european_price_tolerance(np.where(have_mid, mid, np.where(have_ask, ask, bid))),
        market_interval=np.stack([bid, ask], axis=-1),
    )


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
                bad = (Tn < 0.0) | (sn < 0.0) | (Fn <= 0.0)
                quoted = black_price(Fn, K, np.maximum(Tn, 0.0), np.maximum(sn, 0.0), Dn, right)
                price[..., i, j, k] = np.where(bad, np.nan, quoted.value)
                st = quoted.status.copy()
                st[bad] = STATUS_INVALID_INPUT | FLAG_NONPOSITIVE_DOMAIN
                status[..., i, j, k] = st
                dFabs = F * rf
                taylor[..., i, j, k] = (
                    core.price + core.delta * dFabs + core.vega * ds + core.charm * dt
                    + 0.5 * core.gamma * dFabs ** 2 + 0.5 * core.volga * ds ** 2
                    + core.vanna * dFabs * ds
                )
    return ResponseCube(
        price=price, status=status, taylor_price=taylor,
        taylor_residual=price - taylor,
        coordinate_relative_shocks=dF, sigma_additive_shocks=dS,
        calendar_seconds=cal, calendar_years=dT, coordinate=COORDINATE_FORWARD,
    )


def american_domain(S, K, T, sigma, r, dividend_amounts=None):
    """Conservative spot domain used to hold the grid fixed across Greek bumps."""
    S = np.asarray(S, dtype=np.float64)
    K = np.asarray(K, dtype=np.float64)
    T = np.asarray(T, dtype=np.float64)
    sigma = np.asarray(sigma, dtype=np.float64)
    r = np.asarray(r, dtype=np.float64)
    S, K, T, sigma, r = np.broadcast_arrays(S, K, T, sigma, r)
    if dividend_amounts is None:
        sumD = np.zeros(S.shape, dtype=np.float64)
    else:
        sumD = np.zeros(S.shape, dtype=np.float64)
        if isinstance(dividend_amounts, (list, tuple)) and S.shape == ():
            sumD = float(np.sum(np.maximum(np.asarray(dividend_amounts, dtype=np.float64), 0.0)))
            sumD = np.asarray(sumD)
        else:
            for amt in np.atleast_1d(dividend_amounts):
                sumD = sumD + np.maximum(np.asarray(amt, dtype=np.float64), 0.0)
    st = np.where((sigma > 0.0) & (T > 0.0), sigma * np.sqrt(T), 0.0)
    span = np.maximum(8.0 * st + np.abs(r) * T + 2.0, 2.0)
    ref = np.maximum(np.maximum(S, K), 1e-12)
    high = ref * np.exp(span) + 2.0 * sumD + ref
    low = np.maximum(np.minimum(ref * np.exp(-span), 0.25 * np.minimum(S, K)), 1e-12)
    high = np.maximum(high, 4.0 * np.maximum(S, K) + 2.0 * sumD)
    return low, high


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
            t = np.asarray([] if t_row is None else t_row, dtype=np.float64).ravel()
            a = np.asarray([] if a_row is None else a_row, dtype=np.float64).ravel()
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
    global _LIBRARY, _PRICE_FN, _IV_FN
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.stat().st_size > NATIVE_MAX_BYTES or digest != sha256:
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
    _LIBRARY, _PRICE_FN, _IV_FN = library, price, iv
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
    S = np.ascontiguousarray(_as_float("S", S), dtype=np.float64)
    K = np.ascontiguousarray(_as_float("K", K), dtype=np.float64)
    T = np.ascontiguousarray(_as_float("T", T), dtype=np.float64)
    r = np.ascontiguousarray(_as_float("r", r), dtype=np.float64)
    try:
        S, K, T, r = np.broadcast_arrays(S, K, T, r)
    except ValueError as exc:
        raise ContractError("American spot inputs are not broadcast-compatible") from exc
    if sigma is not None:
        sigma = np.ascontiguousarray(_as_float("sigma", sigma), dtype=np.float64)
        try:
            S, K, T, sigma, r = np.broadcast_arrays(S, K, T, sigma, r)
        except ValueError as exc:
            raise ContractError("American sigma is not broadcast-compatible") from exc
        if np.any(sigma > SIGMA_BRACKET_HIGH):
            raise ContractError(
                "volatility must be a fraction in [0, 10]; percent units are rejected"
            )
    S = np.ascontiguousarray(S, dtype=np.float64)
    K = np.ascontiguousarray(K, dtype=np.float64)
    T = np.ascontiguousarray(T, dtype=np.float64)
    r = np.ascontiguousarray(r, dtype=np.float64)
    if sigma is not None:
        sigma = np.ascontiguousarray(sigma, dtype=np.float64)
    right = np.ascontiguousarray(encode_right(right, S.shape), dtype=np.int32)
    flat = int(S.size)
    S1 = S.reshape(flat)
    K1 = K.reshape(flat)
    T1 = T.reshape(flat)
    r1 = r.reshape(flat)
    right1 = right.reshape(flat)
    sigma1 = None if sigma is None else sigma.reshape(flat)
    if n_space is None:
        n_space = 128
    if n_time is None:
        n_time = 0
    if domain_low is None or domain_high is None:
        if sigma1 is None:
            lo, hi = american_domain(S1, K1, T1, SIGMA_BRACKET_HIGH, r1, None)
        else:
            lo, hi = american_domain(S1, K1, T1, sigma1, r1, None)
    else:
        lo = np.broadcast_to(_as_float("domain_low", domain_low), S.shape).reshape(flat)
        hi = np.broadcast_to(_as_float("domain_high", domain_high), S.shape).reshape(flat)
    lo = np.ascontiguousarray(lo, dtype=np.float64)
    hi = np.ascontiguousarray(hi, dtype=np.float64)
    if flat == 1 and dividend_times is not None and not _is_ragged(dividend_times):
        off, dt, da, nd = _pack_dividends(1, dividend_times, dividend_amounts)
    elif dividend_times is None:
        off, dt, da, nd = _pack_dividends(flat, None, None)
    else:
        off, dt, da, nd = _pack_dividends(flat, dividend_times, dividend_amounts)
    return {
        "shape": S.shape,
        "S": S1, "K": K1, "T": T1, "sigma": sigma1, "r": r1, "right": right1,
        "off": np.ascontiguousarray(off, dtype=np.int64),
        "dt": np.ascontiguousarray(dt, dtype=np.float64),
        "da": np.ascontiguousarray(da, dtype=np.float64),
        "nd": int(nd),
        "n_space": int(n_space),
        "n_time": int(n_time),
        "lo": lo, "hi": hi,
        "n": flat,
    }


def native_price_batch(S, K, T, sigma, r, right, *,
                       dividend_times=None, dividend_amounts=None,
                       n_space=128, n_time=None,
                       domain_low=None, domain_high=None,
                       volatility_unit=VOLATILITY_UNIT, style="american", multiplier=None):
    """Batch native American prices. One failed row does not rewrite other rows."""
    _require_enabled()
    _reject_style(style, "american")
    _reject_vol_unit(volatility_unit)
    _reject_multiplier(multiplier)
    spec = _batch_core(S, K, T, sigma, r, right, dividend_times, dividend_amounts,
                       n_space, n_time, domain_low, domain_high)
    n = spec["n"]
    price = np.empty(n, dtype=np.float64)
    error = np.empty(n, dtype=np.float64)
    residual = np.empty(n, dtype=np.float64)
    status = np.empty(n, dtype=np.int32)
    iterations = np.empty(n, dtype=np.int32)
    rc = _PRICE_FN(
        n, spec["S"], spec["K"], spec["T"], spec["sigma"], spec["r"], spec["right"],
        spec["off"], spec["nd"], spec["dt"], spec["da"],
        spec["n_space"], spec["n_time"], spec["lo"], spec["hi"],
        price, error, residual, status, iterations,
    )
    if rc != 0:
        status[:] = STATUS_ABI_ERROR
        price[:] = np.nan
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
    price = np.ascontiguousarray(_as_float("price", price), dtype=np.float64)
    spec = _batch_core(S, K, T, None, r, right, dividend_times, dividend_amounts,
                       n_space, n_time, domain_low, domain_high)
    try:
        price = np.broadcast_to(price, spec["shape"]).reshape(spec["n"])
    except ValueError as exc:
        raise ContractError("American IV price is not broadcast-compatible") from exc
    price = np.ascontiguousarray(price, dtype=np.float64)
    n = spec["n"]
    iv = np.empty(n, dtype=np.float64)
    residual = np.empty(n, dtype=np.float64)
    blo = np.empty(n, dtype=np.float64)
    bhi = np.empty(n, dtype=np.float64)
    status = np.empty(n, dtype=np.int32)
    iterations = np.empty(n, dtype=np.int32)
    rc = _IV_FN(
        n, price, spec["S"], spec["K"], spec["T"], spec["r"], spec["right"],
        spec["off"], spec["nd"], spec["dt"], spec["da"],
        spec["n_space"], spec["n_time"], spec["lo"], spec["hi"],
        iv, residual, blo, bhi, status, iterations,
    )
    if rc != 0:
        status[:] = STATUS_ABI_ERROR
        iv[:] = np.nan
    shape = spec["shape"]
    return ArrayResult(
        iv.reshape(shape), status.reshape(shape), residual.reshape(shape),
        iterations.reshape(shape), blo.reshape(shape), bhi.reshape(shape),
        coordinate=COORDINATE_SPOT, unit=VOLATILITY_UNIT,
    )


def _shift_dividends(dividend_times, dT, n):
    if dividend_times is None:
        return None
    if n == 1 and not _is_ragged(dividend_times):
        t = np.asarray(dividend_times, dtype=np.float64) - dT
        return t
    out = []
    rows = dividend_times
    for t_row in rows:
        t = np.asarray([] if t_row is None else t_row, dtype=np.float64) - dT
        out.append(t)
    return out


def american_greeks(S, K, T, sigma, r, right, *,
                    dividend_times=None, dividend_amounts=None,
                    n_space=128, n_time=None,
                    spot_steps=None, vol_steps=None, calendar_years=None,
                    grids=None, volatility_unit=VOLATILITY_UNIT, style="american",
                    multiplier=None):
    """American Greeks from two step sizes and two grids on a fixed S-domain.

    Unstable exercise-boundary derivatives keep their generated values and are
    flagged; they are not clipped into a desired sign.
    """
    _reject_style(style, "american")
    _reject_vol_unit(volatility_unit)
    _reject_multiplier(multiplier)
    base = native_price_batch(
        S, K, T, sigma, r, right,
        dividend_times=dividend_times, dividend_amounts=dividend_amounts,
        n_space=n_space, n_time=n_time,
    )
    S = np.broadcast_to(_as_float("S", S), base.value.shape).copy()
    K = np.broadcast_to(_as_float("K", K), base.value.shape).copy()
    T = np.broadcast_to(_as_float("T", T), base.value.shape).copy()
    sigma = np.broadcast_to(_as_float("sigma", sigma), base.value.shape).copy()
    r = np.broadcast_to(_as_float("r", r), base.value.shape).copy()
    right = encode_right(right, base.value.shape)
    if spot_steps is None:
        spot_steps = (1e-4 * np.maximum(S, 1.0), 2e-4 * np.maximum(S, 1.0))
    if vol_steps is None:
        vol_steps = (1e-4, 2e-4)
    if calendar_years is None:
        calendar_years = (1.0 / 365.0, 2.0 / 365.0)
    if grids is None:
        grids = (int(n_space or 128), int(2 * (n_space or 128)))
    hS1, hS2 = np.broadcast_to(np.asarray(spot_steps[0], dtype=np.float64), S.shape), np.broadcast_to(
        np.asarray(spot_steps[1], dtype=np.float64), S.shape)
    hv1, hv2 = float(vol_steps[0]), float(vol_steps[1])
    ht1, ht2 = float(calendar_years[0]), float(calendar_years[1])
    g0, g1 = int(grids[0]), int(grids[1])
    lo, hi = american_domain(S * 1.05, K, T, sigma + 2.0 * hv2, r, dividend_amounts)
    lo = np.minimum(lo, np.maximum(S - 4.0 * hS2, 1e-8))

    def px(S_, T_, sig_, ns, dT=0.0):
        dtimes = _shift_dividends(dividend_times, dT, S_.size)
        return native_price_batch(
            S_, K, T_, sig_, r, right,
            dividend_times=dtimes, dividend_amounts=dividend_amounts,
            n_space=ns, n_time=None if n_time in (None, 0) else n_time,
            domain_low=lo, domain_high=hi,
        )

    def pair_first(g_a, g_b, scale):
        err = np.abs(g_a - g_b)
        unstable = (~np.isfinite(g_a)) | (~np.isfinite(g_b)) | (err > 0.25 * (1.0 + np.abs(g_a) + np.abs(g_b)))
        return 0.5 * (g_a + g_b), err, unstable

    def bump_spot(h, ns):
        up = px(S + h, T, sigma, ns).value
        dn = px(S - h, T, sigma, ns).value
        mid = px(S, T, sigma, ns).value
        delta = (up - dn) / (2.0 * h)
        gamma = (up - 2.0 * mid + dn) / np.square(h)
        return delta, gamma, mid

    def bump_vol(h, ns):
        up = px(S, T, sigma + h, ns).value
        dn = px(S, T, np.maximum(sigma - h, 0.0), ns).value
        mid = px(S, T, sigma, ns).value
        vega = (up - dn) / (2.0 * h)
        volga = (up - 2.0 * mid + dn) / (h * h)
        d_up = (px(S + hS1, T, sigma + h, ns).value - px(S - hS1, T, sigma + h, ns).value) / (2.0 * hS1)
        d_dn = (px(S + hS1, T, np.maximum(sigma - h, 0.0), ns).value
                - px(S - hS1, T, np.maximum(sigma - h, 0.0), ns).value) / (2.0 * hS1)
        vanna = (d_up - d_dn) / (2.0 * h)
        return vega, volga, vanna

    def bump_cal(h, ns):
        # Calendar +h years: remaining T decreases by h; D/r path is native r.
        up = px(S, T - h, sigma, ns, dT=h)
        dn = px(S, T + h, sigma, ns, dT=-h)
        d_up = (px(S + hS1, T - h, sigma, ns, dT=h).value - px(S - hS1, T - h, sigma, ns, dT=h).value) / (2.0 * hS1)
        d_dn = (px(S + hS1, T + h, sigma, ns, dT=-h).value - px(S - hS1, T + h, sigma, ns, dT=-h).value) / (2.0 * hS1)
        return (d_up - d_dn) / (2.0 * h), up.status, dn.status

    d11, g11, _ = bump_spot(hS1, g0)
    d12, g12, _ = bump_spot(hS2, g0)
    d21, g21, _ = bump_spot(hS1, g1)
    d22, g22, p_ref = bump_spot(hS2, g1)
    delta, e_d0, u_d0 = pair_first(d11, d12, S)
    delta_g, e_d1, u_d1 = pair_first(d21, d22, S)
    delta, e_d, u_d = pair_first(delta, delta_g, S)
    gamma, e_g0, u_g0 = pair_first(g11, g12, S)
    gamma_g, e_g1, u_g1 = pair_first(g21, g22, S)
    gamma, e_g, u_g = pair_first(gamma, gamma_g, S)

    v11, o11, n11 = bump_vol(hv1, g0)
    v12, o12, n12 = bump_vol(hv2, g0)
    v21, o21, n21 = bump_vol(hv1, g1)
    v22, o22, n22 = bump_vol(hv2, g1)
    vega, e_v, u_v = pair_first(pair_first(v11, v12, S)[0], pair_first(v21, v22, S)[0], S)
    e_v = np.maximum(np.abs(v11 - v12), np.abs(v21 - v22))
    u_v = (~np.isfinite(vega)) | (e_v > 0.25 * (1.0 + np.abs(vega)))
    volga, e_o, u_o = pair_first(pair_first(o11, o12, S)[0], pair_first(o21, o22, S)[0], S)
    e_o = np.maximum(np.abs(o11 - o12), np.abs(o21 - o22))
    u_o = (~np.isfinite(volga)) | (e_o > 0.25 * (1.0 + np.abs(volga)))
    vanna, e_n, u_n = pair_first(pair_first(n11, n12, S)[0], pair_first(n21, n22, S)[0], S)
    e_n = np.maximum(np.abs(n11 - n12), np.abs(n21 - n22))
    u_n = (~np.isfinite(vanna)) | (e_n > 0.25 * (1.0 + np.abs(vanna)))

    c11, st_up, st_dn = bump_cal(ht1, g0)
    c12, _, _ = bump_cal(ht2, g0)
    c21, _, _ = bump_cal(ht1, g1)
    c22, _, _ = bump_cal(ht2, g1)
    charm, e_c, u_c = pair_first(pair_first(c11, c12, S)[0], pair_first(c21, c22, S)[0], S)
    e_c = np.maximum(np.abs(c11 - c12), np.abs(c21 - c22))
    cal_bad = (T - ht2 < 0.0)
    u_c = (~np.isfinite(charm)) | (e_c > 0.25 * (1.0 + np.abs(charm))) | cal_bad
    error = np.maximum.reduce([e_d, e_g, e_v, e_o, e_n, e_c, np.abs(p_ref - base.value)])
    residual = np.abs(p_ref - base.value)
    status = base.status.copy()
    unstable = u_d | u_g | u_v | u_o | u_n | u_c
    status[unstable] = (status[unstable] & ~STATUS_MASK) | STATUS_UNSTABLE_GREEK
    status[unstable] |= FLAG_UNSTABLE_GREEK
    # Keep generated derivatives; do not clip.
    return GreeksResult(
        base.value, delta, gamma, vega, vanna, charm, volga, status, residual, error,
        COORDINATE_SPOT,
        ("r", "K", "right", "discrete_dividends", "fixed_space_grid"),
    )
