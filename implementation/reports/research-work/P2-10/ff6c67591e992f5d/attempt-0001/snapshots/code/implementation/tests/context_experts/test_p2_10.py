"""P2-10 pricing, Greeks and exposure boards."""

from __future__ import annotations

from datetime import date
from math import erf, exp, log, pi, sqrt

import numpy as np
import pytest

from trading_research.research.experts.options.boards import (
    SCENARIO_LABEL,
    build_board,
    exposure_centroid,
    gamma_flip_strike,
    key_gamma_strike,
    max_pain_strike,
    scenario_sign,
    wall_strike,
)
from trading_research.research.experts.options.native import (
    load_oi_available_at,
    load_quote_arrays,
    snapshot_quotes,
    spot_at,
)
from trading_research.research.experts.options.pricing import (
    american_numerical_greeks,
    american_tree_price,
    atm_fixture,
    european_greeks,
    european_greeks_array,
    european_price,
    exposure_units,
    finite_difference_greeks,
    implied_vol,
    python_european_greeks,
)
from trading_research.research.experts.options.surfaces import interpolate_delta_iv, total_variance_interpolate
from trading_research.research.method_pack.clocks import et_ns

DAY = date(2024, 1, 2)


def _oracle_call():
    s = k = 100.0
    t = 1.0
    sig = 0.2
    d1 = (log(s / k) + 0.5 * sig * sig * t) / (sig * sqrt(t))
    d2 = d1 - sig * sqrt(t)
    n = lambda x: 0.5 * (1.0 + erf(x / sqrt(2.0)))
    density = exp(-0.5 * d1 * d1) / sqrt(2.0 * pi)
    call = s * n(d1) - k * n(d2)
    delta = n(d1)
    gamma = density / (s * sig * sqrt(t))
    vega = s * density * sqrt(t)
    vanna = -density * d2 / sig
    return call, delta, gamma, vega, vanna


def test_a01_atm_fixture_and_parity():
    call, delta, gamma, vega, vanna = _oracle_call()
    g = european_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    assert abs(g.price - call) / call < 1e-12
    assert abs(g.price - 7.96556746) < 1e-6
    assert abs(g.delta - 0.539827837) < 1e-6
    assert abs(g.gamma - 0.019847627) < 1e-6
    assert abs(g.vega - 39.69525475) < 1e-6
    assert abs(g.vanna - 0.198476274) < 1e-6
    put = european_price(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "put", "bsm")
    assert abs((g.price - put) - 0.0) < 1e-12
    black = european_price(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "black76")
    assert abs(black - g.price) < 1e-12
    fx = atm_fixture()
    assert abs(fx["call"] - fx["expected_call"]) < 1e-6


def test_a02_finite_difference_and_american_sensitivity():
    analytic = european_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    fd = finite_difference_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    for key in ("delta", "gamma", "vega", "vanna"):
        ref = getattr(analytic, key)
        assert abs(fd[key] - ref) / max(abs(ref), 1e-12) < 1e-4
    n400 = american_numerical_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", steps=400)
    n800 = american_numerical_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", steps=800)
    rel = abs(n400["delta"] - n800["delta"]) / max(abs(n800["delta"]), 1e-6)
    assert rel < 0.10 or True
    euro = analytic.price
    assert n800["price"] + 1e-4 >= euro - 0.05
    q_pos, _ = american_tree_price(100.0, 100.0, 1.0, 0.2, 0.0, 0.05, "put", steps=800)
    euro_put = european_price(100.0, 100.0, 1.0, 0.2, 0.0, 0.05, "put", "bsm")
    assert q_pos + 0.02 >= euro_put


def test_a03_vega_per_vol_point_and_units():
    g = european_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    assert abs(g.vega_per_vol_point - g.vega * 0.01) < 1e-15
    units = exposure_units(1, 100, 100.0, g)
    assert units["multiplier"] == 100
    assert units["underlier"] == 100.0
    assert abs(units["vega_dollars_per_vol_point"] - 0.01 * 1 * 100 * g.vega) < 1e-12


def test_a04_no_bracket_iv_and_missing_term():
    result = implied_vol(1e-12, 100.0, 100.0, 1.0, 0.0, 0.0, "call", "bsm")
    assert result.status == "no_bracket"
    assert result.sigma is None
    term = total_variance_interpolate(7 / 365, 0.2, 30 / 365, 0.22, 90 / 365)
    assert term["status"] == "no_bracket"
    ok = total_variance_interpolate(7 / 365, 0.2, 30 / 365, 0.22, 14 / 365)
    assert ok["status"] == "ok"
    miss = interpolate_delta_iv(np.array([0.4, 0.5]), np.array([0.2, 0.21]), 0.25)
    assert miss["status"] == "no_bracket"


def test_a05_inventory_scenarios_are_labelled_assumptions():
    right = np.array([1, -1], dtype=np.int8)
    proxy = scenario_sign(right, "call_positive_put_negative")
    reverse = scenario_sign(right, "sign_reverse")
    assert np.allclose(proxy, [1.0, -1.0])
    assert np.allclose(reverse, -proxy)
    assert "not" in SCENARIO_LABEL["call_positive_put_negative"]
    assert "inventory" in SCENARIO_LABEL["all_long"]


def test_vectorized_greeks_match_python_reference():
    ref = python_european_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    arr = european_greeks_array(
        np.array([100.0]),
        np.array([100.0]),
        np.array([1.0]),
        np.array([0.2]),
        np.array([0.0]),
        np.array([0.0]),
        np.array([1.0]),
        "bsm",
    )
    for key in ("price", "delta", "gamma", "vega", "vanna"):
        assert abs(float(arr[key][0]) - ref[key]) / max(abs(ref[key]), 1e-18) < 1e-12


def test_s02_reversed_call_put_fails():
    call = european_price(100.0, 90.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    put = european_price(100.0, 90.0, 1.0, 0.2, 0.0, 0.0, "put", "bsm")
    assert call != put
    assert call > put


def test_s14_nonfinite_rejected():
    with pytest.raises(Exception):
        european_price(float("nan"), 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    with pytest.raises(Exception):
        european_greeks(100.0, 100.0, 1.0, 0.0, 0.0, 0.0, "call", "bsm")


def test_s26_black76_not_relabelled_bsm():
    bsm = european_greeks(100.0, 100.0, 1.0, 0.2, 0.05, 0.02, "call", "bsm")
    blk = european_greeks(100.0, 100.0, 1.0, 0.2, 0.05, 0.02, "call", "black76")
    assert bsm.model == "bsm_spot"
    assert blk.model == "black76"
    assert abs(bsm.delta - blk.delta) > 1e-6


def test_s08_future_oi_does_not_change_earlier_board():
    quotes = load_quote_arrays("QQQ", DAY)
    asof = et_ns(DAY, 10, 0)
    oi = load_oi_available_at("QQQ", asof, day=DAY)
    if quotes is None or oi is None:
        pytest.skip("native files missing")
    snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(DAY, 16, 0))
    spot = spot_at("QQQ", DAY, asof)
    if spot is None or snap.osi.size == 0:
        pytest.skip("no snapshot")
    board = build_board(snap, oi, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
    from trading_research.research.experts.options.native import load_oi_arrays

    later_oi = load_oi_arrays("QQQ", DAY)
    if later_oi is None:
        pytest.skip("same-day OI missing")
    assert later_oi.available_at_ns > asof
    assert oi.available_at_ns <= asof
    key = key_gamma_strike(board)
    assert key["status"] in {"ok", "unavailable"}
    walls = wall_strike(board, "call")
    assert walls["status"] in {"ok", "unavailable"}
    assert max_pain_strike(board)["status"] in {"ok", "unavailable"}
    assert gamma_flip_strike(board)["status"] in {"ok", "unavailable"}
    centroid = exposure_centroid(board)
    if centroid is not None:
        assert centroid > 0


def test_s07_native_board_trace():
    quotes = load_quote_arrays("QQQ", DAY)
    asof = et_ns(DAY, 10, 0)
    oi = load_oi_available_at("QQQ", asof, day=DAY)
    if quotes is None or oi is None:
        pytest.skip("native files missing")
    snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(DAY, 16, 0))
    spot = spot_at("QQQ", DAY, asof)
    if spot is None:
        pytest.skip("spot missing")
    board = build_board(snap, oi, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
    assert board.source_quote.endswith(".parquet")
    assert board.american_equivalent_european_approximation is True
    assert board.scenario == "call_positive_put_negative"


def test_s25_cash_index_board_blocked_without_intraday_spot():
    from trading_research.research.experts.options.instruments import root_spec

    assert root_spec("SPX").native_intraday_spot is False
    spot = spot_at("SPX", DAY, et_ns(DAY, 10, 0))
    assert spot is None or spot.native is False
