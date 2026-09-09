"""Independent numerical fixtures for the O02/O05 valuation kernel.

Expected European prices are literal contract values. American checks use
parity/intrinsic, deterministic exercise extrema, or a pure-Python CRR
reference on small fixtures. Native tests call public enable_native with
root-provided env path/hash and fail if that prerequisite is absent.
"""
from pathlib import Path
import math
import os
import tempfile
import unittest

import numpy as np

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.options_valuation_numerics import (
    ACTUAL365_FIXED_SECONDS,
    COORDINATE_FORWARD,
    COORDINATE_SPOT,
    FLAG_ASK_ONLY,
    FLAG_MISSING_BID,
    FLAG_POINT_UNDEFINED,
    FLAG_WEAK_VEGA,
    FLAG_ZERO_BID,
    NATIVE_ENV_PATH,
    NATIVE_ENV_SHA256,
    STATUS_CONVERGED,
    STATUS_CROSSED_QUOTES,
    STATUS_ENDPOINT_LOWER,
    STATUS_ENDPOINT_UPPER,
    STATUS_FAILED_BRACKET,
    STATUS_SIGMA0_DETERMINISTIC,
    STATUS_UNBOUNDED_SIDE,
    STATUS_UNDEFINED_POINT,
    STATUS_ZERO_T,
    american_greeks,
    american_iv,
    apply_contract_multiplier,
    black_greeks,
    black_iv,
    black_price,
    enable_native,
    has_flag,
    invert_quote_interval,
    invert_american_quote_interval,
    american_response_cube,
    STATUS_UNSTABLE_GREEK,
    STATUS_INVALID_INPUT,
    native_price_batch,
    primary_status,
    response_cube,
    years_from_nanoseconds,
    years_from_seconds,
)


EXPECTED_ATM_R0 = 7.965567455405804
EXPECTED_BS_CALL = 10.450583572185565
EXPECTED_BS_PUT = 5.573526022256971


def _f(x):
    return float(np.asarray(x))


def independent_crr_american(S, K, T, sigma, r, right, n):
    """Small-fixture Cox–Ross–Rubinstein American, not the FD engine."""
    if T <= 0.0:
        return max(right * (S - K), 0.0)
    dt = T / n
    u = math.exp(sigma * math.sqrt(dt))
    dlt = 1.0 / u
    disc = math.exp(-r * dt)
    grow = math.exp(r * dt)
    p = (grow - dlt) / (u - dlt)
    V = [0.0] * (n + 1)
    for j in range(n + 1):
        spot = S * (u ** j) * (dlt ** (n - j))
        V[j] = max(right * (spot - K), 0.0)
    for i in range(n - 1, -1, -1):
        nxt = list(V)
        for j in range(i + 1):
            spot = S * (u ** j) * (dlt ** (i - j))
            cont = disc * (p * nxt[j + 1] + (1.0 - p) * nxt[j])
            V[j] = max(max(right * (spot - K), 0.0), cont)
    return V[0]


def _require_native():
    path = os.environ.get(NATIVE_ENV_PATH)
    digest = os.environ.get(NATIVE_ENV_SHA256)
    if not path or not digest:
        raise AssertionError(
            "registered native prerequisite absent: "
            f"{NATIVE_ENV_PATH} and {NATIVE_ENV_SHA256} must be set by root"
        )
    enable_native(path, digest)
    return path, digest


class EuropeanPriceFixtures(unittest.TestCase):
    def test_atm_forward_r0_call_equals_put(self):
        call = black_price(100.0, 100.0, 1.0, 0.2, 1.0, 1)
        put = black_price(100.0, 100.0, 1.0, 0.2, 1.0, -1)
        self.assertAlmostEqual(_f(call.value), EXPECTED_ATM_R0, places=12)
        self.assertAlmostEqual(_f(put.value), EXPECTED_ATM_R0, places=12)
        self.assertEqual(primary_status(call.status), STATUS_CONVERGED)

    def test_black_scholes_mapping_spot100_r05(self):
        F = 100.0 * math.exp(0.05)
        D = math.exp(-0.05)
        call = black_price(F, 100.0, 1.0, 0.2, D, "call")
        put = black_price(F, 100.0, 1.0, 0.2, D, "put")
        self.assertAlmostEqual(_f(call.value), EXPECTED_BS_CALL, places=12)
        self.assertAlmostEqual(_f(put.value), EXPECTED_BS_PUT, places=12)

    def test_put_call_parity_vectorized(self):
        F = np.array([90.0, 100.0, 110.0])
        K = 100.0
        D = math.exp(-0.05)
        call = black_price(F, K, 1.0, 0.2, D, 1).value
        put = black_price(F, K, 1.0, 0.2, D, -1).value
        np.testing.assert_allclose(call - put, D * (F - K), rtol=0.0, atol=1e-12)

    def test_tiny_t_has_positive_time_value_zero_t_is_payoff(self):
        T_tiny = years_from_seconds(60.0)
        self.assertGreater(T_tiny, 0.0)
        self.assertLess(T_tiny, 1.0 / 365.0)
        tiny = black_price(100.0, 100.0, T_tiny, 0.2, 1.0, 1)
        zero = black_price(100.0, 100.0, 0.0, 0.2, 1.0, 1)
        self.assertGreater(_f(tiny.value), 0.0)
        self.assertEqual(_f(zero.value), 0.0)
        self.assertEqual(primary_status(zero.status), STATUS_ZERO_T)
        iv0 = black_iv(0.0, 100.0, 100.0, 0.0, 1.0, 1)
        self.assertTrue(np.isnan(_f(iv0.value)))
        self.assertEqual(primary_status(iv0.status), STATUS_ZERO_T)
        iv_tiny = black_iv(tiny.value, 100.0, 100.0, T_tiny, 1.0, 1)
        self.assertTrue(np.isfinite(_f(iv_tiny.value)))

    def test_years_from_nanoseconds_does_not_round_0dte(self):
        one_minute_ns = 60 * 10 ** 9
        self.assertAlmostEqual(
            _f(years_from_nanoseconds(one_minute_ns)),
            60.0 / ACTUAL365_FIXED_SECONDS,
            places=16,
        )


class EuropeanIVQuotes(unittest.TestCase):
    def test_roundtrip_and_sorted_bid_mid_ask(self):
        F, K, T, D = 100.0 * math.exp(0.05), 100.0, 1.0, math.exp(-0.05)
        mid_p = EXPECTED_BS_CALL
        bid_p, ask_p = mid_p - 0.15, mid_p + 0.15
        quotes = invert_quote_interval(bid_p, mid_p, ask_p, F, K, T, D, 1)
        self.assertTrue(_f(quotes.iv_bid) <= _f(quotes.iv_mid) <= _f(quotes.iv_ask))
        self.assertTrue(quotes.point_defined)
        back = black_price(F, K, T, quotes.iv_mid, D, 1)
        self.assertAlmostEqual(_f(back.value), mid_p, places=7)
        self.assertNotEqual(quotes.solver_price_tolerance, ask_p - bid_p)

    def test_zero_bid_keeps_ask_upper_bound(self):
        F, K, T, D = 100.0, 100.0, 1.0, 1.0
        ask_p = EXPECTED_ATM_R0 + 0.2
        quotes = invert_quote_interval(0.0, np.nan, ask_p, F, K, T, D, 1)
        self.assertTrue(has_flag(quotes.status, FLAG_ZERO_BID))
        self.assertEqual(_f(quotes.iv_lower), 0.0)
        self.assertTrue(np.isfinite(_f(quotes.iv_ask)))
        self.assertTrue(np.isfinite(_f(quotes.iv_upper)))
        self.assertFalse(bool(np.asarray(quotes.point_defined)))

    def test_ask_only_missing_bid_does_not_drop_upper(self):
        F, K, T, D = 100.0, 100.0, 1.0, 1.0
        ask_p = EXPECTED_ATM_R0
        quotes = invert_quote_interval(np.nan, np.nan, ask_p, F, K, T, D, 1)
        self.assertTrue(has_flag(quotes.status, FLAG_MISSING_BID) or has_flag(quotes.status, FLAG_ASK_ONLY))
        self.assertTrue(np.isfinite(_f(quotes.iv_upper)))
        self.assertTrue(np.isnan(_f(quotes.iv_lower)))
        self.assertTrue(has_flag(quotes.status, FLAG_POINT_UNDEFINED))
        prim = primary_status(quotes.status)
        self.assertIn(prim, (STATUS_UNBOUNDED_SIDE, STATUS_UNDEFINED_POINT))

    def test_crossed_quotes_unavailable(self):
        F, K, T, D = 100.0, 100.0, 1.0, 1.0
        quotes = invert_quote_interval(9.0, 8.5, 8.0, F, K, T, D, 1)
        self.assertEqual(primary_status(quotes.status), STATUS_CROSSED_QUOTES)
        self.assertTrue(np.isnan(_f(quotes.point_iv)))
        self.assertFalse(bool(np.asarray(quotes.point_defined)))

    def test_failed_bracket_above_call_bound(self):
        inv = black_iv(100.0 + 1.0, 100.0, 100.0, 1.0, 1.0, 1)
        self.assertEqual(primary_status(inv.status), STATUS_FAILED_BRACKET)
        self.assertTrue(np.isnan(_f(inv.value)))

    def test_tiny_vega_deep_itm_is_weak_or_undefined(self):
        F, K, T, D = 400.0, 100.0, 1.0, 1.0
        intrinsic = D * (F - K)
        inv = black_iv(intrinsic + 1e-12, F, K, T, D, 1)
        prim = primary_status(inv.status)
        self.assertIn(prim, (STATUS_ENDPOINT_LOWER, STATUS_UNDEFINED_POINT, STATUS_CONVERGED))
        self.assertTrue(
            has_flag(inv.status, FLAG_WEAK_VEGA)
            or prim in (STATUS_ENDPOINT_LOWER, STATUS_UNDEFINED_POINT)
        )

    def test_intrinsic_is_endpoint_not_convergence(self):
        inv = black_iv(0.0, 100.0, 100.0, 1.0, 1.0, 1)
        self.assertEqual(primary_status(inv.status), STATUS_ENDPOINT_LOWER)
        self.assertEqual(_f(inv.value), 0.0)


class InputRejection(unittest.TestCase):
    def test_invalid_shape_is_rejected(self):
        with self.assertRaises(ContractError):
            black_price(np.array([100.0, 101.0]), np.array([100.0, 101.0, 102.0]), 1.0, 0.2, 1.0, 1)

    def test_nonfinite_is_unavailable(self):
        out = black_price(np.nan, 100.0, 1.0, 0.2, 1.0, 1)
        self.assertTrue(np.isnan(_f(out.value)))
        self.assertNotEqual(primary_status(out.status), STATUS_CONVERGED)

    def test_percent_volatility_rejected(self):
        with self.assertRaises(ContractError):
            black_price(100.0, 100.0, 1.0, 20.0, 1.0, 1)
        with self.assertRaises(ContractError):
            black_price(100.0, 100.0, 1.0, 0.2, 1.0, 1, volatility_unit="percent")

    def test_multiplier_not_inside_solver(self):
        with self.assertRaises(ContractError):
            black_price(100.0, 100.0, 1.0, 0.2, 1.0, 1, multiplier=100)
        premium = _f(black_price(100.0, 100.0, 1.0, 0.2, 1.0, 1).value)
        self.assertAlmostEqual(premium, EXPECTED_ATM_R0, places=12)
        self.assertLess(premium, 20.0)
        contract = apply_contract_multiplier(premium, 100)
        self.assertAlmostEqual(_f(contract), 100.0 * EXPECTED_ATM_R0, places=10)

    def test_american_style_rejected_on_black(self):
        with self.assertRaises(ContractError):
            black_price(100.0, 100.0, 1.0, 0.2, 1.0, 1, style="american")
        with self.assertRaises(ContractError):
            black_price(100.0, 100.0, 1.0, 0.2, 1.0, "american")


class EuropeanGreeks(unittest.TestCase):
    def test_forward_coordinate_not_spot(self):
        g = black_greeks(100.0, 100.0, 1.0, 0.2, 1.0, 1, 0.0)
        self.assertEqual(g.coordinate, COORDINATE_FORWARD)
        self.assertNotEqual(g.coordinate, COORDINATE_SPOT)
        self.assertEqual(g.volatility_unit, "fraction")

    def test_analytic_matches_independent_central_differences(self):
        F, K, T, sig, D, r = 100.0 * math.exp(0.05), 100.0, 1.0, 0.2, math.exp(-0.05), 0.05
        g = black_greeks(F, K, T, sig, D, 1, r)
        hF, hs = 1e-4, 1e-5

        def P(Fv=F, Tv=T, sv=sig, Dv=D):
            return _f(black_price(Fv, K, Tv, sv, Dv, 1).value)

        delta_fd = (P(Fv=F + hF) - P(Fv=F - hF)) / (2.0 * hF)
        gamma_fd = (P(Fv=F + hF) - 2.0 * P() + P(Fv=F - hF)) / (hF * hF)
        vega_fd = (P(sv=sig + hs) - P(sv=sig - hs)) / (2.0 * hs)
        volga_fd = (P(sv=sig + hs) - 2.0 * P() + P(sv=sig - hs)) / (hs * hs)
        vanna_fd = (
            P(Fv=F + hF, sv=sig + hs) - P(Fv=F + hF, sv=sig - hs)
            - P(Fv=F - hF, sv=sig + hs) + P(Fv=F - hF, sv=sig - hs)
        ) / (4.0 * hF * hs)
        self.assertAlmostEqual(_f(g.delta), delta_fd, places=6)
        self.assertAlmostEqual(_f(g.gamma), gamma_fd, places=5)
        self.assertAlmostEqual(_f(g.vega), vega_fd, places=5)
        self.assertAlmostEqual(_f(g.volga), volga_fd, places=4)
        self.assertAlmostEqual(_f(g.vanna), vanna_fd, places=4)
        self.assertGreater(_f(g.gamma), 0.0)
        self.assertGreater(_f(g.vega), 0.0)
        self.assertLess(_f(g.delta), _f(black_greeks(F + 1.0, K, T, sig, D, 1, r).delta))

    def test_charm_is_calendar_direction_opposite_remaining_time(self):
        F, K, T, sig, D, r = 100.0, 100.0, 1.0, 0.2, 1.0, 0.05
        g = black_greeks(F, K, T, sig, D, 1, r)
        hF, h = 1e-4, 1e-5

        def delta_at(Tv, Dv):
            up = _f(black_price(F + hF, K, Tv, sig, Dv, 1).value)
            dn = _f(black_price(F - hF, K, Tv, sig, Dv, 1).value)
            return (up - dn) / (2.0 * hF)

        charm_fd = (
            delta_at(T - h, D * math.exp(r * h)) - delta_at(T + h, D * math.exp(-r * h))
        ) / (2.0 * h)
        remaining_fd = (
            delta_at(T + h, D * math.exp(-r * h)) - delta_at(T - h, D * math.exp(r * h))
        ) / (2.0 * h)
        self.assertAlmostEqual(_f(g.charm), charm_fd, places=5)
        self.assertAlmostEqual(_f(g.charm), -remaining_fd, places=5)

    def test_vanna_is_per_vol_fraction_not_percent(self):
        g = black_greeks(100.0, 100.0, 1.0, 0.2, 1.0, 1, 0.0)
        self.assertLess(abs(_f(g.vanna)), 5.0)
        per_contract = apply_contract_multiplier(g.vanna, 100)
        self.assertAlmostEqual(_f(per_contract), 100.0 * _f(g.vanna), places=12)


class ResponseCubeFixtures(unittest.TestCase):
    def test_joint_shocks_mark_nonpositive_domain(self):
        cube = response_cube(100.0, 100.0, 1.0, 0.005, 1.0, 1, 0.0,
                             sigma_additive_shocks=(-0.01, 0.0, 0.01),
                             calendar_seconds=(0, 60))
        self.assertEqual(cube.coordinate, COORDINATE_FORWARD)
        self.assertEqual(cube.price.shape[-3:], (3, 3, 2))
        self.assertTrue(np.any(~np.isfinite(cube.price)))
        self.assertTrue(np.any(np.isfinite(cube.taylor_residual)))


class AmericanNative(unittest.TestCase):
    def test_native_prerequisite_is_visible(self):
        _require_native()

    def test_enable_native_rejects_unregistered_bytes(self):
        _require_native()
        with tempfile.TemporaryDirectory() as parent:
            child = Path(parent) / "fixture-native"
            child.mkdir()
            fake = child / "not-the-library.so"
            fake.write_bytes(b"not-a-registered-native")
            with self.assertRaises(IntegrityError):
                enable_native(str(fake), "0" * 64)

    def test_hash_mismatch_on_registered_path(self):
        path, _digest = _require_native()
        with self.assertRaises(IntegrityError):
            enable_native(path, "0" * 64)
        _require_native()

    def test_no_dividend_call_r_positive_agrees_with_european(self):
        _require_native()
        S, K, r, T, sig = 100.0, 100.0, 0.05, 1.0, 0.2
        F = S * math.exp(r * T)
        D = math.exp(-r * T)
        eu = _f(black_price(F, K, T, sig, D, 1).value)
        am = native_price_batch(S, K, T, sig, r, 1)
        self.assertEqual(am.coordinate, COORDINATE_SPOT)
        err = 0.0 if am.error is None or not np.isfinite(_f(am.error)) else _f(am.error)
        self.assertEqual(primary_status(am.status), STATUS_CONVERGED)
        self.assertLessEqual(err, .005)
        self.assertLessEqual(abs(_f(am.value) - eu), .005)
        self.assertLessEqual(_f(am.residual), 1.1e-8)

    def test_american_put_above_european_and_independent_crr(self):
        _require_native()
        S, K, r, T, sig = 100.0, 100.0, 0.05, 1.0, 0.2
        F = S * math.exp(r * T)
        D = math.exp(-r * T)
        eu = _f(black_price(F, K, T, sig, D, -1).value)
        am = native_price_batch(S, K, T, sig, r, -1)
        price = _f(am.value)
        self.assertGreaterEqual(price + 1e-8, eu)
        self.assertGreaterEqual(price + 1e-8, max(K - S, 0.0))
        crr_a = independent_crr_american(S, K, T, sig, r, -1, 401)
        crr_b = independent_crr_american(S, K, T, sig, r, -1, 801)
        crr_err = abs(crr_b - crr_a)
        grid = 0.0 if am.error is None or not np.isfinite(_f(am.error)) else _f(am.error)
        self.assertEqual(primary_status(am.status), STATUS_CONVERGED)
        self.assertLessEqual(grid, .005)
        self.assertLessEqual(abs(price - crr_b), crr_err + .005)
        self.assertLessEqual(_f(am.residual), 1.1e-8)

    def test_zero_vol_discrete_dividend_call_exercises_before_drop(self):
        _require_native()
        S, K, T, r, sig = 110.0, 100.0, 0.1, 0.0, 0.0
        am = native_price_batch(
            S, K, T, sig, r, 1,
            dividend_times=np.array([0.05]), dividend_amounts=np.array([20.0]),
        )
        eu = _f(black_price(S - 20.0, K, T, 0.0, 1.0, 1).value)
        self.assertEqual(eu, 0.0)
        self.assertAlmostEqual(_f(am.value), 10.0, places=6)
        self.assertEqual(primary_status(am.status), STATUS_SIGMA0_DETERMINISTIC)

    def test_negative_rate_deterministic_extrema(self):
        _require_native()
        S, K, T, r = 100.0, 90.0, 1.0, -0.05
        euro_call = max(S - K * math.exp(-r * T), 0.0)
        exercise_call = S - K
        self.assertGreater(exercise_call, euro_call)
        am_call = native_price_batch(S, K, T, 0.0, r, 1)
        self.assertAlmostEqual(_f(am_call.value), exercise_call, places=6)
        S_p, K_p = 100.0, 110.0
        euro_put = max(K_p * math.exp(-r * T) - S_p, 0.0)
        exercise_put = K_p - S_p
        self.assertGreater(euro_put, exercise_put)
        am_put = native_price_batch(S_p, K_p, T, 0.0, r, -1)
        self.assertAlmostEqual(_f(am_put.value), euro_put, places=6)

    def test_positive_vol_dividend_lower_bound_and_monotonicity(self):
        _require_native()
        S, K, T, r, sig = 110.0, 100.0, 0.1, 0.0, 0.2
        eu = _f(black_price(S - 20.0, K, T, sig, 1.0, 1).value)
        am20 = native_price_batch(
            S, K, T, sig, r, 1,
            dividend_times=np.array([0.05]), dividend_amounts=np.array([20.0]),
        )
        am10 = native_price_batch(
            S, K, T, sig, r, 1,
            dividend_times=np.array([0.05]), dividend_amounts=np.array([10.0]),
        )
        grid = 0.0
        if am20.error is not None and np.isfinite(_f(am20.error)):
            grid = max(grid, _f(am20.error))
        if am10.error is not None and np.isfinite(_f(am10.error)):
            grid = max(grid, _f(am10.error))
        self.assertGreaterEqual(_f(am20.value) + max(grid, 1e-3), max(10.0, eu))
        self.assertGreaterEqual(_f(am10.value) + max(grid, 1e-3), _f(am20.value) - max(grid, 1e-3))
        self.assertGreater(_f(am20.value), eu)

    def test_multiple_dividend_jumps_zero_vol(self):
        _require_native()
        am = native_price_batch(
            110.0, 100.0, 0.2, 0.0, 0.0, 1,
            dividend_times=np.array([0.05, 0.15]),
            dividend_amounts=np.array([10.0, 10.0]),
        )
        self.assertAlmostEqual(_f(am.value), 10.0, places=6)
        eu = _f(black_price(90.0, 100.0, 0.2, 0.0, 1.0, 1).value)
        self.assertEqual(eu, 0.0)

    def test_batch_row_error_does_not_corrupt_neighbor(self):
        _require_native()
        S = np.array([100.0, -1.0, 100.0])
        K = np.array([100.0, 100.0, 100.0])
        T = np.array([1.0, 1.0, 1.0])
        sig = np.array([0.2, 0.2, 0.2])
        r = np.array([0.05, 0.05, 0.05])
        right = np.array([1, 1, 1], dtype=np.int32)
        out = native_price_batch(S, K, T, sig, r, right)
        self.assertTrue(np.isfinite(out.value[0]))
        self.assertTrue(np.isfinite(out.value[2]))
        self.assertTrue(np.isnan(out.value[1]) or primary_status(out.status[1]) != STATUS_CONVERGED)

    def test_american_iv_roundtrip_and_refined_error_reported(self):
        _require_native()
        priced = native_price_batch(100.0,100.0,1.0,.2,.05,-1)
        self.assertEqual(primary_status(priced.status),STATUS_CONVERGED)
        inv=american_iv(priced.value,100.0,100.0,1.0,.05,-1)
        self.assertEqual(primary_status(inv.status),STATUS_CONVERGED)
        self.assertLess(abs(_f(inv.value)-.2),1e-6)
        self.assertLessEqual(_f(inv.error),.005)
        self.assertLessEqual(abs(_f(inv.residual)),1e-6)
        independent=independent_crr_american(100,100,1,_f(inv.value),.05,-1,801)
        finer=independent_crr_american(100,100,1,_f(inv.value),.05,-1,1601)
        self.assertLessEqual(abs(_f(priced.value)-finer),abs(independent-finer)+.005)

    def test_american_greeks_against_analytic_no_dividend_call(self):
        _require_native()
        g=american_greeks(100.,100.,1.,.2,.05,1)
        self.assertEqual(g.coordinate,COORDINATE_SPOT)
        eu=black_greeks(100*math.exp(.05),100,1,.2,math.exp(-.05),1,.05)
        expectations={'delta':_f(eu.delta)*math.exp(.05),
                      'gamma':_f(eu.gamma)*math.exp(.10),'vega':_f(eu.vega),
                      'vanna':_f(eu.vanna)*math.exp(.05),'volga':_f(eu.volga)}
        # Spot-fixed calendar theta follows F=S exp(rT), so F also declines.
        expectations['theta']=_f(eu.theta)-.05*100*math.exp(.05)*_f(eu.delta)
        for name in ('delta','gamma','vega','theta'):
            self.assertEqual(primary_status(g.greek_status[name]),STATUS_CONVERGED,(name,g.raw_greeks[name]))
            error=_f(g.greek_errors[name])
            self.assertLessEqual(abs(_f(getattr(g,name))-expectations[name]),max(error*2,1e-4))
        self.assertGreater(_f(g.gamma),.01)
        self.assertGreater(_f(g.vega),30)
        self.assertEqual(g.raw_greeks['gamma'].shape,(3,2))
        self.assertEqual(g.grid_differences['gamma'].shape,(2,2))
        for name in expectations:
            if primary_status(g.greek_status[name]) != STATUS_CONVERGED:
                self.assertTrue(np.isnan(_f(getattr(g,name))))

    def test_intrinsic_american_iv_is_not_unique_point(self):
        _require_native()
        inv=american_iv(20.,80.,100.,1.,.05,-1)
        self.assertEqual(primary_status(inv.status),STATUS_ENDPOINT_LOWER)
        self.assertTrue(has_flag(inv.status,FLAG_WEAK_VEGA))

    def test_negative_rate_call_matches_independent_exercise_reference(self):
        _require_native()
        am=native_price_batch(100.,90.,1.,.2,-.05,1)
        a=independent_crr_american(100,90,1,.2,-.05,1,401)
        b=independent_crr_american(100,90,1,.2,-.05,1,801)
        self.assertEqual(primary_status(am.status),STATUS_CONVERGED)
        self.assertLessEqual(_f(am.error),.005)
        self.assertLessEqual(_f(am.residual),1.1e-8)
        self.assertGreaterEqual(_f(am.value),10.)
        self.assertLessEqual(abs(_f(am.value)-b),abs(b-a)+.005)

    def test_invalid_dividends_are_not_silently_zero(self):
        _require_native()
        for time in (-.1,0.,1.1,float('nan')):
            out=native_price_batch(100.,100.,1.,.2,.05,1,dividend_times=[time],dividend_amounts=[1.])
            self.assertEqual(primary_status(out.status),STATUS_INVALID_INPUT)
            self.assertTrue(np.isnan(_f(out.value)))
        with self.assertRaises(ContractError):
            native_price_batch([100.,100.],100.,1.,.2,.05,1,
                               dividend_times=[None,[]],dividend_amounts=[None,[]])
        a=native_price_batch(110.,100.,.2,0.,0.,1,dividend_times=[.15,.05,.05],dividend_amounts=[5.,5.,5.])
        self.assertAlmostEqual(_f(a.value),10.,places=12)

    def test_american_broadcast_price_and_right_only(self):
        _require_native()
        source=native_price_batch(100.,100.,1.,.2,.05,[1,-1])
        self.assertEqual(source.value.shape,(2,))
        self.assertEqual(native_price_batch(100.,100.,1.,.2,.05,1).value.shape,())
        inverse=american_iv(source.value,100.,100.,1.,.05,[1,-1])
        np.testing.assert_allclose(inverse.value,[.2,.2],atol=1e-6,rtol=0)

    def test_american_interval_and_calendar_response(self):
        _require_native()
        mid=_f(native_price_batch(100.,100.,1.,.2,.05,-1).value)
        q=invert_american_quote_interval(mid-.05,mid,mid+.05,100.,100.,1.,.05,-1)
        self.assertTrue(bool(q.point_defined))
        self.assertEqual(primary_status(q.status_mid),STATUS_CONVERGED)
        self.assertLessEqual(_f(q.error_mid),.005)
        self.assertLess(_f(q.iv_lower),_f(q.iv_upper))
        c=american_response_cube(100.,100.,1.,.2,.05,1,
                                coordinate_relative_shocks=(0.,),sigma_additive_shocks=(0.,),calendar_seconds=(0.,60.))
        self.assertAlmostEqual(_f(c.price[0,0,0]),_f(c.taylor_price[0,0,0]),places=10)
        self.assertTrue(np.isfinite(_f(c.taylor_residual[0,0,1])))
        self.assertLess(abs(_f(c.taylor_residual[0,0,1])),1e-4)

    def test_native_absent_is_dependency_not_skip(self):
        path = os.environ.get(NATIVE_ENV_PATH)
        digest = os.environ.get(NATIVE_ENV_SHA256)
        if not path or not digest:
            raise AssertionError(
                "registered native prerequisite absent: "
                f"{NATIVE_ENV_PATH} and {NATIVE_ENV_SHA256} must be set by root"
            )


class CorrectedBoundaryFixtures(unittest.TestCase):
    def test_right_fraction_rejected_and_empty_supported(self):
        with self.assertRaises(ContractError):black_price(100.,100.,1.,.2,1.,1.5)
        self.assertEqual(black_price(100.,100.,1.,.2,1.,['call','put']).value.shape,(2,))
        self.assertEqual(black_price(np.array([]),100.,1.,.2,1.,np.array([],dtype=str)).value.size,0)

    def test_finite_bracket_failure_cannot_return_iv(self):
        t=years_from_seconds(1.)
        price=_f(black_price(100.,100.,t,10.,1.,1).value)+.01
        inv=black_iv(price,100.,100.,t,1.,1)
        self.assertEqual(primary_status(inv.status),STATUS_FAILED_BRACKET)
        self.assertTrue(np.isnan(_f(inv.value)))

    def test_quote_statuses_and_infeasible_sides(self):
        below=invert_quote_interval(1.,2.,3.,110.,100.,1.,1.,1)
        self.assertEqual(primary_status(below.status),STATUS_FAILED_BRACKET)
        self.assertEqual(primary_status(below.status_ask),STATUS_FAILED_BRACKET)
        self.assertTrue(np.isnan(_f(below.iv_upper)))
        negative=invert_quote_interval(-1.,5.,10.,100.,100.,1.,1.,1)
        self.assertEqual(primary_status(negative.status),STATUS_INVALID_INPUT)
        outside=invert_quote_interval(5.,9.,8.,100.,100.,1.,1.,1)
        self.assertEqual(primary_status(outside.status),STATUS_INVALID_INPUT)
        broad=invert_quote_interval(0.,10.5,12.,110.,100.,1.,1.,1)
        self.assertEqual(_f(broad.iv_lower),0.)
        self.assertTrue(np.isfinite(_f(broad.iv_upper)))

    def test_calendar_price_taylor_uses_theta(self):
        cube=response_cube(100.,100.,1.,.2,1.,1,.05,
                           coordinate_relative_shocks=(0.,),sigma_additive_shocks=(0.,),calendar_seconds=(0.,60.))
        self.assertAlmostEqual(_f(cube.price[0,0,0]),_f(cube.taylor_price[0,0,0]),places=12)
        self.assertLess(abs(_f(cube.taylor_residual[0,0,1])),1e-9)
        g=black_greeks(100.,100.,1.,.2,1.,1,.05)
        dt=years_from_seconds(60.)
        self.assertAlmostEqual(_f(cube.taylor_price[0,0,1]),_f(g.price+g.theta*dt),places=12)


if __name__ == "__main__":
    unittest.main()
