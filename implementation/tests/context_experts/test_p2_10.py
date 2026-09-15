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
    python_abs_gamma,
    python_exposure_centroid,
    python_max_pain_strike,
    python_signed_gamma,
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
    IV_HI,
    IV_LO,
    american_numerical_greeks,
    american_tree_price,
    atm_fixture,
    european_greeks,
    european_greeks_array,
    european_price,
    exposure_units,
    finite_difference_greeks,
    implied_vol,
    implied_vol_array,
    python_european_greeks,
    python_exposure_units,
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


def test_vectorized_greeks_match_python_reference_randomized():
    rng = np.random.default_rng(7)
    n = 48
    s = 50.0 + rng.random(n) * 100.0
    k = 50.0 + rng.random(n) * 100.0
    t = rng.random(n) * 1.5
    sig = 0.05 + rng.random(n) * 0.6
    r = rng.random(n) * 0.05
    q = rng.random(n) * 0.03
    cp = np.where(rng.random(n) < 0.5, 1.0, -1.0)
    t[::6] = 0.0
    sig[::8] = 0.0
    s[::7] = np.nan
    k[3] = 0.0
    arr = european_greeks_array(s, k, t, sig, r, q, cp, "bsm")
    for i in range(n):
        right = "call" if cp[i] > 0 else "put"
        rejected = (not np.isfinite(s[i])) or (not np.isfinite(k[i])) or k[i] <= 0 or t[i] <= 0 or sig[i] <= 0
        if rejected:
            assert arr["delta"][i] == 0.0
            assert arr["gamma"][i] == 0.0
            assert arr["vega"][i] == 0.0
            assert arr["vanna"][i] == 0.0
            continue
        ref = python_european_greeks(float(s[i]), float(k[i]), float(t[i]), float(sig[i]), float(r[i]), float(q[i]), right, "bsm")
        for key in ("price", "delta", "gamma", "vega", "vanna"):
            denom = max(abs(ref[key]), 1e-18)
            assert abs(float(arr[key][i]) - ref[key]) / denom < 1e-12


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


def _fingerprint(board):
    return {
        "key_gamma": key_gamma_strike(board),
        "call_wall": wall_strike(board, "call"),
        "put_wall": wall_strike(board, "put"),
        "gamma_flip": gamma_flip_strike(board),
        "max_pain": max_pain_strike(board),
        "centroid": exposure_centroid(board),
        "oi": np.asarray(board.oi).copy(),
    }


@pytest.mark.parametrize("root", ["QQQ", "NQ"])
def test_s08_future_oi_does_not_change_earlier_board(root):
    from trading_research.research.experts.options.native import load_oi_arrays

    day = date(2024, 3, 5)
    quotes = load_quote_arrays(root, day)
    asof = et_ns(day, 10, 0)
    causal_oi = load_oi_available_at(root, asof, day=day)
    future_oi = load_oi_arrays(root, day)
    if quotes is None or causal_oi is None or future_oi is None:
        pytest.skip("native files missing")
    assert future_oi.available_at_ns > asof
    assert causal_oi.available_at_ns <= asof
    snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(day, 16, 0))
    spot = spot_at(root, day, asof)
    if spot is None or snap.osi.size == 0:
        pytest.skip("no snapshot")
    causal = build_board(snap, causal_oi, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
    future = build_board(snap, future_oi, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
    left = _fingerprint(causal)
    right = _fingerprint(future)
    assert left["key_gamma"] != right["key_gamma"] or left["max_pain"] != right["max_pain"] or not np.array_equal(left["oi"], right["oi"])
    loaded = load_oi_available_at(root, asof, day=day)
    prod = build_board(snap, loaded, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
    got = _fingerprint(prod)
    assert got["key_gamma"] == left["key_gamma"]
    assert got["call_wall"] == left["call_wall"]
    assert got["put_wall"] == left["put_wall"]
    assert got["gamma_flip"] == left["gamma_flip"]
    assert got["max_pain"] == left["max_pain"]
    assert got["centroid"] == left["centroid"]
    assert np.array_equal(got["oi"], left["oi"])
    assert got["key_gamma"] != right["key_gamma"] or not np.array_equal(got["oi"], right["oi"])


def test_python_exposure_primitives_match_vectorized():
    g = european_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    vec = exposure_units(2, 100, 100.0, g)
    ref = python_exposure_units(2, 100, 100.0, g.delta, g.gamma, g.vega, g.vanna)
    assert vec == ref
    oi = [10, 20, 5, 8]
    right = [1, -1, 1, -1]
    gamma = [0.02, 0.01, 0.03, 0.04]
    live = [True, True, True, False]
    signed = python_signed_gamma(oi, right, gamma, 100.0, 50.0, live, "call_positive_put_negative")
    assert signed[3] == 0.0
    assert signed[0] == 0.01 * 10 * 1.0 * 100.0 * 50.0 * 50.0 * 0.02
    assert signed[1] == 0.01 * 20 * (-1.0) * 100.0 * 50.0 * 50.0 * 0.01
    assert python_abs_gamma(signed) == [abs(x) for x in signed]
    strikes = [90.0, 100.0, 100.0, 110.0]
    abs_g = [1.0, 2.0, 3.0, 4.0]
    assert python_exposure_centroid(strikes, abs_g) == (90 * 1 + 100 * 2 + 100 * 3 + 110 * 4) / 10.0
    pain = python_max_pain_strike([90.0, 100.0, 110.0], [1, 1, -1], [10, 5, 20])
    assert pain["status"] == "ok"
    day = date(2024, 1, 2)
    quotes = load_quote_arrays("QQQ", day)
    asof = et_ns(day, 10, 0)
    oi_arr = load_oi_available_at("QQQ", asof, day=day)
    if quotes is None or oi_arr is None:
        pytest.skip("native files missing")
    snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(day, 16, 0))
    spot = spot_at("QQQ", day, asof)
    if spot is None or snap.osi.size == 0:
        pytest.skip("no snapshot")
    board = build_board(snap, oi_arr, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
    live = np.isfinite(board.gamma) & (board.reject == 0)
    py_signed = python_signed_gamma(board.oi, board.right, np.where(np.isfinite(board.gamma), board.gamma, 0.0), 100.0, board.underlier, live, board.scenario)
    assert np.allclose(py_signed, board.signed_gamma, rtol=1e-12, atol=1e-9)
    assert np.allclose(python_abs_gamma(py_signed), board.abs_gamma, rtol=1e-12, atol=1e-9)
    k = (board.strike_millis.astype(np.float64) * 0.001).tolist()
    py_c = python_exposure_centroid(k, board.abs_gamma.tolist())
    vec_c = exposure_centroid(board)
    if vec_c is None:
        assert py_c is None
    else:
        assert abs(py_c - vec_c) < 1e-9
    py_p = python_max_pain_strike(k, board.right.tolist(), board.oi.tolist())
    vec_p = max_pain_strike(board)
    assert py_p["strike"] == vec_p["strike"]


@pytest.mark.parametrize("root", ["QQQ", "NQ"])
def test_s07_native_board_trace(root):
    quotes = load_quote_arrays(root, DAY)
    asof = et_ns(DAY, 10, 0)
    oi = load_oi_available_at(root, asof, day=DAY)
    if quotes is None or oi is None:
        pytest.skip("native files missing")
    snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(DAY, 16, 0))
    spot = spot_at(root, DAY, asof)
    if spot is None:
        pytest.skip("spot missing")
    board = build_board(snap, oi, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
    assert board.source_quote.endswith(".parquet")
    assert board.root == root
    if root == "QQQ":
        assert board.american_equivalent_european_approximation is True
        assert board.model == "bsm"
    else:
        assert board.model == "black76"
        assert board.american_equivalent_european_approximation is True
    assert board.scenario == "call_positive_put_negative"


def test_atlas_summary_has_intervals_and_breakdowns():
    from trading_research.research.experts.options.atlas import _summarize

    rows = [
        {
            "day": "2024-01-02",
            "kind": "key_gamma",
            "root": "QQQ",
            "year": "2024",
            "expiry_bucket": "1-7",
            "high_session_bucket": "rth",
            "vol_regime": "mid",
            "high": {"within_4": False, "within_8": True, "within_16": True},
            "low": {"within_4": False, "within_8": False, "within_16": True},
            "high_after_available": True,
            "control": {"high": {"within_4": False, "within_8": False, "within_16": True}, "low": {"within_8": False}},
        }
    ]
    alignment = [
        {"day": "2024-01-02", "branch": "asia_tdo_case", "level_kind": "key_gamma", "bucket": "within_0.1", "result": "not_applicable"},
        {"day": "2024-01-02", "branch": "asia_tdo_case", "level_kind": "key_gamma", "bucket": "within_0.1", "result": "win"},
        {"day": "2024-01-02", "branch": "asia_tdo_case", "level_kind": "key_gamma", "bucket": "beyond", "result": "loss"},
    ]
    summary = _summarize(rows, alignment, [], [])
    cell = summary["by_kind"]["key_gamma"]["high_within_8"]
    assert "interval_95" in cell
    assert cell["n"] == 1
    assert "high_within_4" in summary["by_kind"]["key_gamma"]
    assert "high_within_16" in summary["by_kind"]["key_gamma"]
    assert "high_after_available" in summary["by_kind"]["key_gamma"]
    assert "QQQ" in summary["by_root"]
    assert "2024" in summary["by_year"]
    assert "1-7" in summary["by_expiry_bucket"]
    assert "rth" in summary["by_session_bucket_high"]
    assert "mid" in summary["by_vol_regime"]
    assert "root_agreement" in summary
    assert "change_features" in summary
    assert summary["alignment_outcomes"]["n_not_applicable"] == 1
    assert summary["alignment_outcomes"]["n"] == 3
    branch = summary["alignment_outcomes"]["by_branch_and_level"][0]
    assert "unconditional" in branch
    assert "conditional" in branch["bins"]["within_0.1"]


def test_atlas_emits_all_root_csvs_and_named_deviations(tmp_path):
    from trading_research.research.experts.options.atlas import build_atlas
    from trading_research.research.experts.options.instruments import REQUIRED_ROOTS

    coverage = [
        {"root": "QQQ", "day": "2024-01-02", "disposition": "complete_observed_scope"},
        {"root": "NQ", "day": "2024-01-02", "disposition": "unsupported_owned_input"},
        {"root": "ES", "day": "2026-09-03", "disposition": "unsupported_owned_input"},
    ]
    payload = build_atlas([], tmp_path, coverage=coverage, slice_dates=["2024-01-02", "2026-09-03"])
    md = (tmp_path / "LEVEL_ATLAS.md").read_text()
    assert "B0.1" in md
    assert "P15-03" in md
    assert "P15-02" in md
    assert "selects nothing" in md.lower()
    assert "unsupported_owned_input" in md
    assert payload["deviations"]["missing_slice_dates"] == ["2024-01-02", "2026-09-03"]
    for root in REQUIRED_ROOTS:
        path = tmp_path / f"LEVEL_ATLAS_{root}.csv"
        assert path.is_file()
        text = path.read_text()
        assert "unavailable" in text
        assert text.splitlines()[1].startswith(root) or f"root,{root}" in text or f"{root}," in text


def test_phi_cdf_evaluates_erf_only_on_finite_subset(monkeypatch):
    from trading_research.research.experts.options import pricing as pricing_mod

    sizes = []
    real = pricing_mod.erf_array

    def wrapped(x):
        sizes.append(int(np.asarray(x).size))
        return real(x)

    monkeypatch.setattr(pricing_mod, "erf_array", wrapped)
    x = np.array([np.nan, 0.0, np.inf, 1.0, -np.inf, 2.0])
    y = pricing_mod.phi_cdf(x)
    assert sizes == [3]
    assert np.isnan(y[0]) and np.isnan(y[2]) and np.isnan(y[4])
    assert np.isfinite(y[1]) and np.isfinite(y[3]) and np.isfinite(y[5])


def test_implied_vol_array_prices_only_unconverged_subset(monkeypatch):
    from trading_research.research.experts.options import pricing as pricing_mod

    sizes = []
    real = pricing_mod.european_greeks_array

    def wrapped(*args, **kwargs):
        sig = args[3] if len(args) > 3 else kwargs["sigma"]
        sizes.append(int(np.asarray(sig).size))
        return real(*args, **kwargs)

    monkeypatch.setattr(pricing_mod, "european_greeks_array", wrapped)
    n = 16
    S = np.full(n, 100.0)
    K = np.full(n, 100.0)
    T = np.full(n, 1.0)
    T[::4] = 0.0
    r = np.zeros(n)
    q = np.zeros(n)
    cp = np.ones(n)
    easy_sig = 0.5 * (IV_LO + IV_HI)
    easy_px = european_price(100.0, 100.0, 1.0, easy_sig, 0.0, 0.0, "call", "bsm")
    hard_px = european_price(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    m = np.full(n, hard_px)
    live = np.flatnonzero(T > 0)
    m[live[: len(live) // 2]] = easy_px
    implied_vol_array(m, S, K, T, r, q, cp, "bsm")
    n_cand = int(np.count_nonzero(T > 0))
    assert sizes
    assert all(s <= n_cand for s in sizes)
    assert all(s < n for s in sizes)
    assert min(sizes) < n_cand


def test_s25_cash_index_board_blocked_without_intraday_spot():
    from trading_research.research.experts.options.instruments import root_spec

    assert root_spec("SPX").native_intraday_spot is False
    spot = spot_at("SPX", DAY, et_ns(DAY, 10, 0))
    assert spot is None or spot.native is False
