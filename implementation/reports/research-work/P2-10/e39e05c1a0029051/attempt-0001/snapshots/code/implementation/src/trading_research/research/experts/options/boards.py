"""Native exposure boards with per-board prefix structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.experts.options.instruments import RIGHT_CALL, root_spec
from trading_research.research.experts.options.native import OIArrays, SnapshotQuotes
from trading_research.research.experts.options.pricing import european_greeks_array, implied_vol_array
from trading_research.research.experts.options.surfaces import expiry_bucket, interpolate_delta_iv, nearest_atm_iv, risk_reversal_butterfly
from trading_research.research.method_pack.clocks import et_ns

SCENARIOS = (
    "unsigned_magnitude",
    "call_positive_put_negative",
    "sign_reverse",
    "all_long",
    "all_short",
)

SCENARIO_LABEL = {
    "unsigned_magnitude": "sensitivity_assumption_not_dealer_inventory",
    "call_positive_put_negative": "baseline_proxy_not_known_inventory",
    "sign_reverse": "sensitivity_assumption_not_dealer_inventory",
    "all_long": "sensitivity_assumption_not_dealer_inventory",
    "all_short": "sensitivity_assumption_not_dealer_inventory",
}


def scenario_sign(right: np.ndarray, name: str) -> np.ndarray:
    ones = np.ones(right.shape, dtype=np.float64)
    if name == "unsigned_magnitude":
        return ones
    if name == "call_positive_put_negative":
        return np.where(right > 0, 1.0, -1.0)
    if name == "sign_reverse":
        return np.where(right > 0, -1.0, 1.0)
    if name == "all_long":
        return ones
    if name == "all_short":
        return -ones
    raise ContractError(f"unknown inventory scenario {name}")


def join_oi(snapshot: SnapshotQuotes, oi: OIArrays) -> np.ndarray:
    """OI aligned to snapshot rows. Unmatched OI is 0 with a separate unmatched count."""
    if snapshot.osi_code.size == 0:
        return np.zeros(0, dtype=np.int64)
    if oi.osi_code.size == 0:
        return np.zeros(snapshot.osi_code.size, dtype=np.int64)
    order = np.argsort(oi.osi_code, kind="mergesort")
    codes = oi.osi_code[order]
    values = oi.oi[order]
    idx = np.searchsorted(codes, snapshot.osi_code)
    in_range = idx < codes.size
    hit = np.zeros(snapshot.osi_code.size, dtype=np.bool_)
    hit[in_range] = codes[np.minimum(idx, codes.size - 1)][in_range] == snapshot.osi_code[in_range]
    out = np.zeros(snapshot.osi_code.size, dtype=np.int64)
    out[hit] = values[idx[hit]]
    return out


@dataclass(frozen=True, slots=True)
class BoardArrays:
    strike_millis: np.ndarray
    right: np.ndarray
    expiry_ns: np.ndarray
    osi: np.ndarray
    oi: np.ndarray
    iv: np.ndarray
    mid: np.ndarray
    delta: np.ndarray
    gamma: np.ndarray
    vega: np.ndarray
    vanna: np.ndarray
    signed_gamma: np.ndarray
    abs_gamma: np.ndarray
    prefix_abs_gamma: np.ndarray
    prefix_k_abs_gamma: np.ndarray
    reject: np.ndarray
    scenario: str
    snapshot_end_ns: int
    root: str
    day: str
    underlier: float
    rate: float
    carry: float
    model: str
    american_equivalent_european_approximation: bool
    source_quote: str
    source_oi: str


def build_board(
    snapshot: SnapshotQuotes,
    oi: OIArrays,
    *,
    underlier: float,
    rate: float,
    carry: float,
    asof_ns: int,
    scenario: str = "call_positive_put_negative",
    model: str | None = None,
) -> BoardArrays:
    spec = root_spec(snapshot.root)
    model = model or spec.pricing_model
    model_key = "bsm" if model == "bsm_spot" else "black76"
    american_flag = spec.exercise == "american"
    if american_flag and model_key == "bsm":
        model_key = "bsm"
    n = snapshot.osi_code.size
    oi_aligned = join_oi(snapshot, oi)
    ok = snapshot.reject == 0
    T = np.maximum((snapshot.expiry_ns.astype(np.float64) - float(asof_ns)) / (365.0 * 86400.0 * 1_000_000_000.0), 0.0)
    strike = snapshot.strike_millis.astype(np.float64) * 0.001
    S = np.full(n, float(underlier))
    r = np.full(n, float(rate))
    q = np.full(n, float(carry))
    mid = snapshot.mid.copy()
    sigma, iv_status = implied_vol_array(mid, S, strike, T, r, q, snapshot.right.astype(np.float64), model_key)
    greeks = european_greeks_array(S, strike, T, np.where(np.isfinite(sigma), sigma, 0.2), r, q, snapshot.right.astype(np.float64), model_key)
    live = ok & np.isfinite(sigma) & (T > 0)
    sign = scenario_sign(snapshot.right, scenario)
    n_pos = oi_aligned.astype(np.float64) * sign
    M = float(spec.multiplier)
    U = float(underlier)
    signed_gamma = 0.01 * n_pos * M * U * U * np.where(live, greeks["gamma"], 0.0)
    abs_gamma = np.abs(signed_gamma)
    order = np.argsort(snapshot.strike_millis, kind="mergesort")
    sorted_abs = abs_gamma[order]
    sorted_k = snapshot.strike_millis[order].astype(np.float64) * 0.001
    prefix_abs = np.cumsum(sorted_abs)
    prefix_k = np.cumsum(sorted_k * sorted_abs)
    return BoardArrays(
        strike_millis=snapshot.strike_millis,
        right=snapshot.right,
        expiry_ns=snapshot.expiry_ns,
        osi=snapshot.osi,
        oi=oi_aligned,
        iv=sigma,
        mid=mid,
        delta=np.where(live, greeks["delta"], np.nan),
        gamma=np.where(live, greeks["gamma"], np.nan),
        vega=np.where(live, greeks["vega"], np.nan),
        vanna=np.where(live, greeks["vanna"], np.nan),
        signed_gamma=signed_gamma,
        abs_gamma=abs_gamma,
        prefix_abs_gamma=prefix_abs,
        prefix_k_abs_gamma=prefix_k,
        reject=snapshot.reject,
        scenario=scenario,
        snapshot_end_ns=snapshot.snapshot_end_ns,
        root=snapshot.root,
        day=snapshot.day,
        underlier=U,
        rate=float(rate),
        carry=float(carry),
        model=model_key,
        american_equivalent_european_approximation=american_flag,
        source_quote=snapshot.source_path,
        source_oi=oi.source_path,
    )


def python_signed_gamma(
    oi: list[int] | np.ndarray,
    right: list[int] | np.ndarray,
    gamma: list[float] | np.ndarray,
    multiplier: float,
    underlier: float,
    live: list[bool] | np.ndarray,
    scenario: str,
) -> list[float]:
    """Plain-Python per-contract signed gamma. No NumPy reductions."""
    out: list[float] = []
    for i, contracts in enumerate(list(oi)):
        side = int(right[i])
        if scenario == "unsigned_magnitude":
            sign = 1.0
        elif scenario == "call_positive_put_negative":
            sign = 1.0 if side > 0 else -1.0
        elif scenario == "sign_reverse":
            sign = -1.0 if side > 0 else 1.0
        elif scenario == "all_long":
            sign = 1.0
        elif scenario == "all_short":
            sign = -1.0
        else:
            raise ContractError(f"unknown inventory scenario {scenario}")
        g = float(gamma[i])
        if (not bool(live[i])) or g != g:
            out.append(0.0)
            continue
        n_pos = float(contracts) * sign
        out.append(0.01 * n_pos * multiplier * underlier * underlier * g)
    return out


def python_abs_gamma(signed_gamma: list[float]) -> list[float]:
    """Plain-Python absolute gamma aggregation."""
    return [abs(float(x)) for x in signed_gamma]


def python_exposure_centroid(strike: list[float], abs_gamma: list[float]) -> float | None:
    total = 0.0
    weighted = 0.0
    for k, ag in zip(strike, abs_gamma):
        total += ag
        weighted += k * ag
    if total <= 0:
        return None
    return weighted / total


def python_max_pain_strike(strike: list[float], right: list[int], oi: list[int]) -> dict[str, Any]:
    """Plain-Python max pain. Nested loops over unique strikes."""
    if not strike:
        return {"strike": None, "status": "unavailable"}
    uniq = sorted(set(strike))
    best_k = uniq[0]
    best_pain = None
    for settle in uniq:
        pain = 0.0
        for k, side, qty in zip(strike, right, oi):
            if side > 0:
                pain += max(settle - k, 0.0) * qty
            else:
                pain += max(k - settle, 0.0) * qty
        if best_pain is None or pain < best_pain:
            best_pain = pain
            best_k = settle
    return {"strike": float(best_k), "pain": float(best_pain or 0.0), "status": "ok"}


def exposure_centroid(board: BoardArrays) -> float | None:
    total = float(board.prefix_abs_gamma[-1]) if board.prefix_abs_gamma.size else 0.0
    if total <= 0:
        return None
    return float(board.prefix_k_abs_gamma[-1] / total)


def key_gamma_strike(board: BoardArrays) -> dict[str, Any]:
    if board.signed_gamma.size == 0:
        return {"strike": None, "status": "unavailable"}
    abs_g = np.abs(board.signed_gamma)
    i = int(np.argmax(abs_g))
    if abs_g[i] <= 0:
        return {"strike": None, "status": "unavailable"}
    return {"strike": float(board.strike_millis[i]) * 0.001, "signed_gamma": float(board.signed_gamma[i]), "status": "ok"}


def wall_strike(board: BoardArrays, side: Literal["call", "put"]) -> dict[str, Any]:
    mask = board.right > 0 if side == "call" else board.right < 0
    if not np.any(mask):
        return {"strike": None, "status": "unavailable"}
    idx = np.flatnonzero(mask)
    i = idx[int(np.argmax(np.abs(board.signed_gamma[idx])))]
    if board.signed_gamma[i] == 0:
        return {"strike": None, "status": "unavailable"}
    return {"strike": float(board.strike_millis[i]) * 0.001, "signed_gamma": float(board.signed_gamma[i]), "status": "ok"}


def gamma_flip_strike(board: BoardArrays) -> dict[str, Any]:
    if board.signed_gamma.size == 0:
        return {"strike": None, "status": "unavailable"}
    order = np.argsort(board.strike_millis, kind="mergesort")
    cum = np.cumsum(board.signed_gamma[order])
    strikes = board.strike_millis[order].astype(np.float64) * 0.001
    sign = np.sign(cum)
    change = np.flatnonzero((sign[1:] * sign[:-1]) < 0)
    if change.size == 0:
        return {"strike": None, "status": "unavailable"}
    i = int(change[0])
    return {"strike": float(0.5 * (strikes[i] + strikes[i + 1])), "status": "ok"}


def max_pain_strike(board: BoardArrays) -> dict[str, Any]:
    """Vectorized max-pain via prefix of call/put OI and OI*K."""
    if board.oi.size == 0:
        return {"strike": None, "status": "unavailable"}
    order = np.argsort(board.strike_millis, kind="mergesort")
    k = board.strike_millis[order].astype(np.float64) * 0.001
    oi = board.oi[order].astype(np.float64)
    is_call = board.right[order] > 0
    call_oi = np.where(is_call, oi, 0.0)
    put_oi = np.where(~is_call, oi, 0.0)
    uniq, start = np.unique(k, return_index=True)
    call_at = np.add.reduceat(call_oi, start)
    put_at = np.add.reduceat(put_oi, start)
    k_u = uniq
    csum = np.cumsum(call_at)
    csum_k = np.cumsum(call_at * k_u)
    psum = np.cumsum(put_at[::-1])[::-1]
    psum_k = np.cumsum((put_at * k_u)[::-1])[::-1]
    call_pain = k_u * np.concatenate(([0.0], csum[:-1])) - np.concatenate(([0.0], csum_k[:-1]))
    put_tail_oi = np.concatenate((psum[1:], [0.0]))
    put_tail_k = np.concatenate((psum_k[1:], [0.0]))
    put_pain = put_tail_k - k_u * put_tail_oi
    pain = call_pain + put_pain
    i = int(np.argmin(pain))
    return {"strike": float(k_u[i]), "pain": float(pain[i]), "status": "ok"}


def top_strikes(board: BoardArrays, field: str, n: int = 3) -> list[dict[str, float]]:
    data = {"gamma": board.abs_gamma, "vanna": np.abs(board.vanna * board.oi.astype(np.float64)), "vega": np.abs(board.vega * board.oi.astype(np.float64))}[field]
    if data.size == 0:
        return []
    order = np.argsort(-data, kind="mergesort")[:n]
    return [{"strike": float(board.strike_millis[i]) * 0.001, "value": float(data[i])} for i in order.tolist() if data[i] > 0]


def board_levels(board: BoardArrays, *, asof_ns: int, day: date) -> dict[str, Any]:
    spec = root_spec(board.root)
    live = np.isfinite(board.iv) & (board.reject == 0)
    F = board.underlier
    if np.any(live):
        k = board.strike_millis[live].astype(np.float64) * 0.001
        logm = np.log(k / F)
        atm = nearest_atm_iv(logm, np.abs(board.mid[live]), k, board.iv[live])
        abs_delta = np.abs(board.delta[live])
        call_mask = board.right[live] > 0
        put_mask = board.right[live] < 0
        c25 = interpolate_delta_iv(abs_delta[call_mask], board.iv[live][call_mask], 0.25) if np.any(call_mask) else {"iv": None, "status": "unavailable"}
        p25 = interpolate_delta_iv(abs_delta[put_mask], board.iv[live][put_mask], 0.25) if np.any(put_mask) else {"iv": None, "status": "unavailable"}
        rr_bf = risk_reversal_butterfly(atm.get("iv"), c25.get("iv"), p25.get("iv"))
    else:
        atm = {"iv": None, "status": "unavailable"}
        c25 = {"iv": None, "status": "unavailable"}
        p25 = {"iv": None, "status": "unavailable"}
        rr_bf = {"rr": None, "bf": None, "status": "unavailable"}
    dte = None
    if board.expiry_ns.size:
        min_exp = int(np.min(board.expiry_ns))
        cal = max(0, (min_exp - et_ns(day, 0, 0)) // (86400 * 1_000_000_000))
        tau = (min_exp - asof_ns) / (365.0 * 86400.0 * 1_000_000_000.0)
        dte = expiry_bucket(int(cal) if tau > 0 else -1)
        if tau > 0 and int(cal) == 0:
            dte = "0DTE"
    return {
        "root": board.root,
        "day": board.day,
        "asof_ns": asof_ns,
        "spot": board.underlier,
        "scenario": board.scenario,
        "scenario_label": SCENARIO_LABEL[board.scenario],
        "american_equivalent_european_approximation": board.american_equivalent_european_approximation,
        "model": board.model,
        "key_gamma": key_gamma_strike(board),
        "call_wall": wall_strike(board, "call"),
        "put_wall": wall_strike(board, "put"),
        "gamma_flip": gamma_flip_strike(board),
        "max_pain": max_pain_strike(board),
        "top_gamma": top_strikes(board, "gamma"),
        "top_vanna": top_strikes(board, "vanna"),
        "top_vega": top_strikes(board, "vega"),
        "centroid": exposure_centroid(board),
        "atm_iv": atm,
        "call25": c25,
        "put25": p25,
        "rr_bf": rr_bf,
        "front_bucket": dte,
        "n_contracts": int(board.osi.size),
        "n_live": int(np.count_nonzero(np.isfinite(board.iv) & (board.reject == 0))),
        "n_with_oi": int(np.count_nonzero(board.oi > 0)),
        "n_with_fresh_quote": int(np.count_nonzero(board.reject == 0)),
        "n_rejected": int(np.count_nonzero(board.reject != 0)),
        "signed_gamma_sum": float(np.sum(board.signed_gamma)),
        "abs_gamma_sum": float(np.sum(board.abs_gamma)),
        "oi_sum": int(np.sum(board.oi)),
        "implied_move": None if atm.get("iv") is None else float(board.underlier * atm["iv"] * np.sqrt(max(T_front(board, asof_ns), 0.0))),
        "multiplier": spec.multiplier,
        "underlying_id": spec.underlying_id,
    }


def T_front(board: BoardArrays, asof_ns: int) -> float:
    if board.expiry_ns.size == 0:
        return 0.0
    return max(0.0, (float(np.min(board.expiry_ns)) - asof_ns) / (365.0 * 86400.0 * 1_000_000_000.0))
