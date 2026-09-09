"""Join, status and cohort fixtures for historical option valuation.

Cases exercise study conventions, not the 44 numerical-kernel identities.
One test calls the accepted invert/Black API on a literal European quote.
"""
from datetime import date, time
import unittest

import numpy as np
import pyarrow as pa

from trading_research.errors import ContractError
from trading_research.foundations.calendar import local_timestamp
from trading_research.research.options_historical_valuation import (
    MAX_BOARD_ROWS, NAMED_SCENARIO_PRESETS, ZONE, build_cross_chain_table,
    build_valuation_report, build_valuation_tables, contract_cut_schema,
    cross_chain_schema, default_scenario_contract, empty_valuation_tables,
    expiry_cut_schema, named_scenario_contract, scenario_identity,
    validate_scenario_contract, valuation_coverage_schema,
)
from trading_research.research.options_valuation_numerics import (
    apply_contract_multiplier, black_greeks, black_price, invert_quote_interval,
    years_from_nanoseconds,
)


def _ns(day, hour, minute=0):
    if isinstance(day, str):
        day = date.fromisoformat(day)
    return local_timestamp(day, time(hour, minute), ZONE)


def _board(rows):
    names = (
        "chain", "request_date", "cut_label", "cut_ns", "source_family",
        "contract_id", "osi_symbol", "expiration", "millistrike", "right",
        "dte", "dte_bucket", "bid", "ask", "mid", "bid_size", "ask_size",
        "usable", "quoted", "conflict", "listed", "listing_known",
        "base_class", "ts_event_ns", "sample_age_ns", "oi", "oi_available",
        "oi_ambiguous", "oi_missing", "oi_stale", "oi_expired", "oi_zero",
        "zero_bid", "known_at_ns",
    )
    defaults = {
        "source_family": "near", "dte_bucket": "2-7", "bid_size": 10, "ask_size": 10,
        "usable": True, "quoted": True, "conflict": False, "listed": True,
        "listing_known": True, "base_class": "two_sided", "sample_age_ns": 60 * 10 ** 9,
        "oi": 5, "oi_available": True, "oi_ambiguous": False, "oi_missing": False,
        "oi_stale": False, "oi_expired": False, "oi_zero": False, "zero_bid": False,
        "known_at_ns": 99,
    }
    filled = []
    for row in rows:
        item = dict(defaults)
        item.update(row)
        if item.get("mid") is None and item.get("bid") is not None and item.get("ask") is not None:
            item["mid"] = 0.5 * (item["bid"] + item["ask"])
        filled.append(item)
    arrays = {}
    for name in names:
        values = [row.get(name) for row in filled]
        if name in ("cut_ns", "contract_id", "millistrike", "dte", "bid_size", "ask_size",
                    "ts_event_ns", "sample_age_ns", "oi", "known_at_ns"):
            arrays[name] = pa.array(values, type=pa.int64())
        elif name in ("bid", "ask", "mid"):
            arrays[name] = pa.array(values, type=pa.float64())
        elif name in ("usable", "quoted", "conflict", "listed", "listing_known",
                      "oi_available", "oi_ambiguous", "oi_missing", "oi_stale",
                      "oi_expired", "oi_zero", "zero_bid"):
            arrays[name] = pa.array(values, type=pa.bool_())
        else:
            arrays[name] = pa.array(values, type=pa.string())
    return pa.table(arrays)


def _underlier(rows):
    names = (
        "chain", "request_date", "cut_label", "etf_present", "etf_close",
        "etf_bar_end_ns", "etf_assumption", "cash_close", "cash_date",
        "cash_same_date", "cash_assumption",
    )
    filled = [{
        "etf_present": False, "etf_close": None, "etf_bar_end_ns": None,
        "etf_assumption": None, "cash_close": None, "cash_date": None,
        "cash_same_date": False, "cash_assumption": None, **row,
    } for row in rows]
    return pa.table({
        "chain": pa.array([r["chain"] for r in filled], type=pa.string()),
        "request_date": pa.array([r["request_date"] for r in filled], type=pa.string()),
        "cut_label": pa.array([r["cut_label"] for r in filled], type=pa.string()),
        "etf_present": pa.array([r["etf_present"] for r in filled], type=pa.bool_()),
        "etf_close": pa.array([r["etf_close"] for r in filled], type=pa.float64()),
        "etf_bar_end_ns": pa.array([r["etf_bar_end_ns"] for r in filled], type=pa.int64()),
        "etf_assumption": pa.array([r["etf_assumption"] for r in filled], type=pa.string()),
        "cash_close": pa.array([r["cash_close"] for r in filled], type=pa.float64()),
        "cash_date": pa.array([r["cash_date"] for r in filled], type=pa.string()),
        "cash_same_date": pa.array([r["cash_same_date"] for r in filled], type=pa.bool_()),
        "cash_assumption": pa.array([r["cash_assumption"] for r in filled], type=pa.string()),
    })


def _fred(rows):
    return pa.table({
        "chain": pa.array([r.get("chain") for r in rows], type=pa.string()),
        "request_date": pa.array([r["request_date"] for r in rows], type=pa.string()),
        "cut_label": pa.array([r["cut_label"] for r in rows], type=pa.string()),
        "series_id": pa.array([r.get("series_id", "DGS1") for r in rows], type=pa.string()),
        "tenor_days": pa.array([r.get("tenor_days", 30) for r in rows], type=pa.int64()),
        "obs_date": pa.array([r.get("obs_date", r["request_date"]) for r in rows], type=pa.string()),
        "rate_pct": pa.array([r.get("rate_pct", 1.0) for r in rows], type=pa.float64()),
        "missing_rate": pa.array([r.get("missing_rate", False) for r in rows], type=pa.bool_()),
    })


def _actions(rows):
    if not rows:
        return pa.table({
            "chain": pa.array([], type=pa.string()),
            "request_date": pa.array([], type=pa.string()),
            "symbol": pa.array([], type=pa.string()),
            "ex_date": pa.array([], type=pa.string()),
            "dividend": pa.array([], type=pa.float64()),
        })
    return pa.table({
        "chain": pa.array([r.get("chain") for r in rows], type=pa.string()),
        "request_date": pa.array([r.get("request_date") for r in rows], type=pa.string()),
        "symbol": pa.array([r.get("symbol") for r in rows], type=pa.string()),
        "ex_date": pa.array([r.get("ex_date") for r in rows], type=pa.string()),
        "dividend": pa.array([r.get("dividend") for r in rows], type=pa.float64()),
    })


def _empty_support():
    return pa.table({
        "chain": pa.array([], type=pa.string()),
        "request_date": pa.array([], type=pa.string()),
        "cut_label": pa.array([], type=pa.string()),
    })


def _quote_row(**kwargs):
    req = kwargs.get("request_date", "2021-01-05")
    exp = kwargs.get("expiration", "2021-01-08")
    cut = kwargs.get("cut_label", "10:00")
    hour = 16 if cut == "cash_close" else (10 if cut == "10:00" else 9)
    cut_ns = kwargs.get("cut_ns", _ns(req, hour, 30 if cut == "09:30" else 0))
    return {
        "chain": "SPXW", "request_date": req, "cut_label": cut, "cut_ns": cut_ns,
        "contract_id": 11, "osi_symbol": "SPXW  210108C04000000",
        "expiration": exp, "millistrike": 4000000, "right": "CALL",
        "dte": (date.fromisoformat(exp) - date.fromisoformat(req)).days,
        "bid": 1.0, "ask": 1.2, "ts_event_ns": cut_ns - 60 * 10 ** 9, **kwargs,
    }


class ScenarioContract(unittest.TestCase):
    def test_identity_stable_and_rejects_silent_changes(self):
        a, b = default_scenario_contract(), default_scenario_contract()
        self.assertEqual(scenario_identity(a), scenario_identity(b))
        self.assertFalse(a["certification_claimed"])
        bad = default_scenario_contract()
        bad["rate_assumption"] = "invented"
        with self.assertRaises(ContractError):
            validate_scenario_contract(bad)
        grid = default_scenario_contract()
        grid["american_n_space"] = 256
        with self.assertRaises(ContractError):
            validate_scenario_contract(grid)
        with self.assertRaises(ContractError):
            named_scenario_contract("explode_all")
        self.assertIn("zero_rate", NAMED_SCENARIO_PRESETS)
        changed = named_scenario_contract("zero_rate")
        self.assertEqual(changed["base_assumption"], "default_scenario_contract")
        self.assertIn("rate_assumption", changed["changed_assumption"])


class EmptyAndTypes(unittest.TestCase):
    def test_empty_tables_are_stable(self):
        empty = empty_valuation_tables()
        again = build_valuation_tables(
            _board([]), _empty_support(), _empty_support(), _actions([]),
            scenario_contract=default_scenario_contract(),
        )
        self.assertEqual(empty["contract_cut"].schema, contract_cut_schema())
        self.assertEqual(again["contract_cut"].schema, contract_cut_schema())
        self.assertEqual(again["expiry_cut"].schema, expiry_cut_schema())
        self.assertEqual(again["coverage"].schema, valuation_coverage_schema())
        self.assertEqual(again["contract_cut"].num_rows, 0)
        self.assertEqual(build_cross_chain_table([], scenario_contract=default_scenario_contract()).schema, cross_chain_schema())

    def test_batch_cap_is_the_documented_bound(self):
        self.assertEqual(MAX_BOARD_ROWS, 250000)


class ClockAndStyleCases(unittest.TestCase):
    def test_am_vs_pm_same_timestamp_and_strike(self):
        req, exp = "2021-01-05", "2021-01-08"
        cut_ns = _ns(req, 10)
        board = _board([
            _quote_row(chain="SPX", osi_symbol="SPX   210108C04000000", contract_id=1, cut_ns=cut_ns, ts_event_ns=cut_ns),
            _quote_row(chain="SPXW", osi_symbol="SPXW  210108C04000000", contract_id=2, cut_ns=cut_ns, ts_event_ns=cut_ns),
        ])
        support = _underlier([
            {"chain": "SPX", "request_date": req, "cut_label": "10:00", "cash_close": 3800.0,
             "cash_date": "2021-01-04", "cash_same_date": False,
             "cash_assumption": "prior_available_cash_date_close"},
            {"chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 3800.0,
             "cash_date": "2021-01-04", "cash_same_date": False,
             "cash_assumption": "prior_available_cash_date_close"},
        ])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        rows = {row["chain"]: row for row in out["contract_cut"].to_pylist()}
        self.assertEqual(rows["SPX"]["expiry_clock_id"], "osi_date_0930_et")
        self.assertEqual(rows["SPXW"]["expiry_clock_id"], "osi_date_1600_et")
        self.assertLess(rows["SPX"]["T"], rows["SPXW"]["T"])
        self.assertEqual(rows["SPX"]["expiry_ns"], _ns(exp, 9, 30))
        self.assertEqual(rows["SPXW"]["expiry_ns"], _ns(exp, 16))
        self.assertNotEqual(rows["SPX"]["settlement_class"], rows["SPXW"]["settlement_class"])

    def test_lagged_cash_vs_same_date_close(self):
        req = "2021-01-05"
        board = _board([
            _quote_row(cut_label="10:00", cut_ns=_ns(req, 10), contract_id=1),
            _quote_row(cut_label="cash_close", cut_ns=_ns(req, 16), contract_id=1),
        ])
        support = _underlier([
            {"chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 3900.0,
             "cash_date": "2021-01-04", "cash_same_date": False,
             "cash_assumption": "prior_available_cash_date_close"},
            {"chain": "SPXW", "request_date": req, "cut_label": "cash_close", "cash_close": 4000.0,
             "cash_date": req, "cash_same_date": True,
             "cash_assumption": "retrospective_same_date_close_at_or_after_declared_close"},
        ])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        by_cut = {row["cut_label"]: row for row in out["contract_cut"].to_pylist()}
        self.assertEqual(by_cut["10:00"]["S"], 3900.0)
        self.assertEqual(by_cut["cash_close"]["S"], 4000.0)
        self.assertEqual(by_cut["10:00"]["underlier_assumption"], "prior_available_cash_date_close")
        self.assertEqual(by_cut["cash_close"]["underlier_assumption"], "retrospective_same_date_close_at_or_after_declared_close")

    def test_same_date_cash_is_not_used_before_close(self):
        req = "2021-01-05"
        board = _board([_quote_row(cut_label="10:00", cut_ns=_ns(req, 10))])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
            "cash_date": req, "cash_same_date": True,
            "cash_assumption": "retrospective_same_date_close_at_or_after_declared_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        row = out["contract_cut"].to_pylist()[0]
        self.assertIsNone(row["S"])
        self.assertFalse(row["underlier_ok"])
        self.assertFalse(row["valuation_eligible"])

    def test_future_underlier_is_not_selected(self):
        req = "2021-01-05"
        board = _board([_quote_row(), _quote_row(chain="SPY", osi_symbol="SPY   210108C00400000", contract_id=3, millistrike=400000)])
        support = _underlier([
            {"chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
             "cash_date": "2021-01-06", "cash_same_date": False,
             "cash_assumption": "prior_available_cash_date_close"},
            {"chain": "SPY", "request_date": req, "cut_label": "10:00", "etf_present": True,
             "etf_close": 380.0, "etf_bar_end_ns": _ns(req, 10) + 60 * 10 ** 9,
             "etf_assumption": "latest_complete_one_minute_bar_end_at_or_before_cut"},
        ])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        by_chain = {row["chain"]: row for row in out["contract_cut"].to_pylist()}
        self.assertIsNone(by_chain["SPXW"]["S"])
        self.assertIsNone(by_chain["SPY"]["S"])
        self.assertFalse(by_chain["SPY"]["underlier_ok"])


class QuoteStatusCases(unittest.TestCase):
    def test_ask_only_zero_bid_crossed_and_conflict(self):
        req = "2021-01-05"
        cut_ns = _ns(req, 10)
        board = _board([
            _quote_row(contract_id=1, bid=None, mid=None, ask=2.0, usable=False, zero_bid=True, base_class="one_sided"),
            _quote_row(contract_id=2, millistrike=4010000, bid=0.0, mid=None, ask=2.0, usable=False, zero_bid=True, base_class="one_sided"),
            _quote_row(contract_id=3, millistrike=4020000, bid=2.5, ask=2.0, mid=None, usable=False, base_class="crossed"),
            _quote_row(contract_id=4, millistrike=4030000, bid=1.0, ask=1.2, usable=False, conflict=True, base_class="conflict"),
        ])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        rows = {row["contract_id"]: row for row in out["contract_cut"].to_pylist()}
        self.assertTrue(rows[1]["ask_only"])
        self.assertTrue(rows[1]["valuation_input_ok"])
        self.assertTrue(rows[2]["zero_bid"])
        self.assertTrue(rows[3]["crossed_quotes"])
        self.assertFalse(rows[3]["valuation_input_ok"])
        self.assertIsNone(rows[3]["iv_mid"])
        self.assertTrue(rows[4]["conflict"])
        self.assertIsNone(rows[4]["iv_mid"])
        self.assertEqual(out["coverage"].to_pylist()[0]["n_conflict"], 1)
        self.assertEqual(out["coverage"].to_pylist()[0]["n_crossed"], 1)

    def test_listed_unquoted_stays_in_denominators(self):
        req = "2021-01-05"
        board = _board([
            _quote_row(contract_id=1),
            _quote_row(contract_id=2, millistrike=4010000, quoted=False, usable=False, bid=None, ask=None, mid=None, base_class=None),
        ])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        self.assertEqual(out["contract_cut"].num_rows, 1)
        cov = out["coverage"].to_pylist()[0]
        self.assertEqual(cov["n_board_rows"], 2)
        self.assertEqual(cov["n_quoted"], 1)
        self.assertEqual(cov["n_listed_unquoted"], 1)
        self.assertEqual(out["expiry_cut"].to_pylist()[0]["n_listed_unquoted"], 1)

    def test_near_and_broad_remain_separate(self):
        req = "2021-01-05"
        board = _board([
            _quote_row(contract_id=9, source_family="near", millistrike=4000000),
            _quote_row(contract_id=9, source_family="broad", millistrike=4010000),
        ])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        families = {row["source_family"] for row in out["contract_cut"].to_pylist()}
        self.assertEqual(families, {"near", "broad"})
        expiry = {row["source_family"]: row for row in out["expiry_cut"].to_pylist()}
        self.assertEqual(len(expiry), 2)
        self.assertNotEqual(expiry["near"]["group_seal"], expiry["broad"]["group_seal"])


class AvailabilityAndClocks(unittest.TestCase):
    def test_vix_hole_does_not_drop_spy_and_parity_works_without_spot(self):
        req = "2021-01-05"
        cut_ns = _ns(req, 10)
        board = _board([
            _quote_row(chain="VIX", osi_symbol="VIX   210108C00020000", contract_id=1, millistrike=20000, right="CALL"),
            _quote_row(chain="VIX", osi_symbol="VIX   210108P00020000", contract_id=2, millistrike=20000, right="PUT", bid=0.8, ask=1.0),
            _quote_row(chain="SPY", osi_symbol="SPY   210108C00400000", contract_id=3, millistrike=400000),
        ])
        support = _underlier([{
            "chain": "SPY", "request_date": req, "cut_label": "10:00", "etf_present": True,
            "etf_close": 380.0, "etf_bar_end_ns": cut_ns - 30 * 10 ** 9,
            "etf_assumption": "latest_complete_one_minute_bar_end_at_or_before_cut",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        rows = out["contract_cut"].to_pylist()
        vix = [row for row in rows if row["chain"] == "VIX"]
        spy = [row for row in rows if row["chain"] == "SPY"]
        self.assertEqual(len(vix), 2)
        self.assertEqual(len(spy), 1)
        self.assertEqual(vix[0]["underlier_assumption"], "vix_spot_unavailable")
        self.assertFalse(vix[0]["underlier_ok"])
        self.assertTrue(spy[0]["underlier_ok"])
        self.assertEqual(spy[0]["S"], 380.0)
        self.assertIsNotNone(vix[0]["F_parity"] or vix[1]["F_parity"])
        self.assertIsNone(vix[0]["F_used"])
        self.assertFalse(vix[0]["iv_identified"])

    def test_civil_dte_zero_can_have_positive_T(self):
        req = "2021-01-05"
        board = _board([_quote_row(expiration=req, dte=0, dte_bucket="0")])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        row = out["contract_cut"].to_pylist()[0]
        self.assertEqual(row["dte"], 0)
        self.assertGreater(row["T"], 0.0)
        self.assertEqual(row["expiry_ns"], _ns(req, 16))
        self.assertLess(row["cut_ns"], row["expiry_ns"])

    def test_nanoseconds_above_float53_remain_int64(self):
        req, exp = "2021-01-05", "2021-06-18"
        board = _board([_quote_row(expiration=exp, dte=164, dte_bucket="61+")])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        row = out["contract_cut"].to_pylist()[0]
        self.assertIsInstance(row["cut_ns"], int)
        self.assertIsInstance(row["expiry_ns"], int)
        self.assertGreater(row["cut_ns"], 2 ** 53)
        self.assertGreater(row["expiry_ns"], 2 ** 53)
        self.assertEqual(row["expiry_ns"], _ns(exp, 16))

    def test_null_known_at_stays_null(self):
        board = _board([_quote_row(known_at_ns=123456789)])
        support = _underlier([{
            "chain": "SPXW", "request_date": "2021-01-05", "cut_label": "10:00",
            "cash_close": 4000.0, "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        row = out["contract_cut"].to_pylist()[0]
        self.assertIsNone(row["known_at_ns"])
        self.assertIsNone(row["received_at_ns"])
        self.assertIsNone(row["published_at_ns"])
        self.assertIsNone(row["last_actual_update_ns"])
        self.assertFalse(row["causal_feature_eligible"])
        self.assertEqual(row["model_asof"], "cut")
        self.assertEqual(row["model_asof_ns"], row["cut_ns"])


class NumericsCompatibility(unittest.TestCase):
    def test_accepted_invert_api_on_literal_european_quote(self):
        req, exp = "2021-01-05", "2021-01-08"
        cut_ns = _ns(req, 10)
        expiry_ns = _ns(exp, 16)
        T = float(years_from_nanoseconds(expiry_ns - cut_ns))
        S, K, r = 100.0, 100.0, 0.0
        F = S * np.exp(r * T)
        D = float(np.exp(-r * T))
        mid = float(black_price(F, K, T, 0.2, D, "CALL").value)
        quote = invert_quote_interval(mid * 0.99, mid, mid * 1.01, F, K, T, D, "CALL")
        board = _board([_quote_row(
            millistrike=100000, bid=mid * 0.99, mid=mid, ask=mid * 1.01,
            cut_ns=cut_ns, ts_event_ns=cut_ns,
        )])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": S,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        row = out["contract_cut"].to_pylist()[0]
        self.assertAlmostEqual(row["T"], T, places=12)
        self.assertAlmostEqual(row["F_used"], F, places=12)
        if quote.point_defined.item() and row["iv_identified"]:
            self.assertAlmostEqual(row["iv_mid"], float(quote.iv_mid), places=10)
            greeks = black_greeks(F, K, T, float(quote.iv_mid), D, "CALL", r)
            self.assertAlmostEqual(row["delta"], float(greeks.delta), places=10)
        self.assertIsNone(row["delta_per_contract"])

    def test_multiplier_is_post_solver_only(self):
        seen = {}
        orig = invert_quote_interval

        def wrapped(*args, **kwargs):
            seen["kwargs"] = kwargs
            seen["n_args"] = len(args)
            return orig(*args, **kwargs)

        req, exp = "2021-01-05", "2021-01-08"
        cut_ns = _ns(req, 10)
        T = float(years_from_nanoseconds(_ns(exp, 16) - cut_ns))
        mid = float(black_price(100.0, 100.0, T, 0.2, 1.0, "CALL").value)
        board = _board([_quote_row(
            millistrike=100000, bid=mid * 0.99, mid=mid, ask=mid * 1.01,
            cut_ns=cut_ns, ts_event_ns=cut_ns,
        )])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 100.0,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        from trading_research.research import options_historical_valuation as hv
        hv.invert_quote_interval = wrapped
        try:
            out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                         scenario_contract=named_scenario_contract("multiplier_post_solver"))
        finally:
            hv.invert_quote_interval = orig
        self.assertNotIn("multiplier", seen.get("kwargs", {}))
        row = out["contract_cut"].to_pylist()[0]
        if row["delta"] is not None:
            self.assertAlmostEqual(row["delta_per_contract"], float(apply_contract_multiplier(row["delta"], 100.0)), places=12)


class DividendAndCrossChain(unittest.TestCase):
    def test_etf_dividend_schedule_vs_q0(self):
        captured = []

        def fake_invert(bid, mid, ask, S, K, T, r, right, **kwargs):
            captured.append(kwargs)
            n = np.broadcast_arrays(np.asarray(bid), np.asarray(S))[0].size
            payload = type("P", (), {})()
            payload.iv_bid = np.full(n, 0.2)
            payload.iv_mid = np.full(n, 0.21)
            payload.iv_ask = np.full(n, 0.22)
            payload.iv_lower = np.full(n, 0.2)
            payload.iv_upper = np.full(n, 0.22)
            payload.residual_bid = np.zeros(n)
            payload.residual_mid = np.zeros(n)
            payload.residual_ask = np.zeros(n)
            payload.status = np.zeros(n, dtype=np.int32)
            payload.status_bid = np.zeros(n, dtype=np.int32)
            payload.status_mid = np.zeros(n, dtype=np.int32)
            payload.status_ask = np.zeros(n, dtype=np.int32)
            payload.point_defined = np.ones(n, dtype=bool)
            return payload

        def fake_greeks(S, K, T, sigma, r, right, **kwargs):
            n = np.broadcast_arrays(np.asarray(S), np.asarray(sigma))[0].size
            nan = np.full(n, np.nan)
            return type("G", (), {
                "delta": nan, "gamma": nan, "vega": nan, "vanna": nan,
                "charm": nan, "volga": nan, "theta": nan,
                "status": np.full(n, 12, dtype=np.int32),
            })()

        req = "2021-01-05"
        cut_ns = _ns(req, 10)
        board = _board([_quote_row(chain="QQQ", osi_symbol="QQQ   210108C00320000", millistrike=320000, cut_ns=cut_ns)])
        support = _underlier([{
            "chain": "QQQ", "request_date": req, "cut_label": "10:00", "etf_present": True,
            "etf_close": 320.0, "etf_bar_end_ns": cut_ns - 60 * 10 ** 9,
            "etf_assumption": "latest_complete_one_minute_bar_end_at_or_before_cut",
        }])
        actions = _actions([{"chain": "QQQ", "request_date": req, "symbol": "QQQ", "ex_date": "2021-01-07", "dividend": 0.4}])
        fred = _fred([{"chain": "QQQ", "request_date": req, "cut_label": "10:00", "rate_pct": 1.0, "tenor_days": 7}])
        from trading_research.research import options_historical_valuation as hv
        orig_i, orig_g = hv.invert_american_quote_interval, hv.american_greeks
        hv.invert_american_quote_interval = fake_invert
        hv.american_greeks = fake_greeks
        try:
            scheduled = build_valuation_tables(board, support, fred, actions,
                                               scenario_contract=default_scenario_contract())
            q0 = build_valuation_tables(board, support, fred, actions,
                                        scenario_contract=named_scenario_contract("q0_no_dividend"))
        finally:
            hv.invert_american_quote_interval = orig_i
            hv.american_greeks = orig_g
        self.assertEqual(scheduled["contract_cut"].to_pylist()[0]["dividend_assumption"], "exdate_schedule_not_announcement_pit")
        self.assertEqual(q0["contract_cut"].to_pylist()[0]["dividend_assumption"], "q0_no_dividend")
        self.assertTrue(any(item.get("dividend_times") for item in captured[:1]))
        self.assertTrue(any(not item.get("dividend_times") for item in captured[1:]))

    def test_cross_chain_incompatible_clocks_are_undefined(self):
        req, exp = "2021-01-05", "2021-01-08"
        cut_ns = _ns(req, 10)
        board = _board([
            _quote_row(chain="NDX", osi_symbol="NDX   210108C14000000", contract_id=1, millistrike=14000000),
            _quote_row(chain="NDXP", osi_symbol="NDXP  210108C14000000", contract_id=2, millistrike=14000000),
        ])
        support = _underlier([
            {"chain": "NDX", "request_date": req, "cut_label": "10:00", "cash_close": 12800.0,
             "cash_date": "2021-01-04", "cash_same_date": False,
             "cash_assumption": "prior_available_cash_date_close"},
            {"chain": "NDXP", "request_date": req, "cut_label": "10:00", "cash_close": 12800.0,
             "cash_date": "2021-01-04", "cash_same_date": False,
             "cash_assumption": "prior_available_cash_date_close"},
        ])
        tables = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                        scenario_contract=named_scenario_contract("zero_rate"))
        cross = build_cross_chain_table(tables["expiry_cut"], scenario_contract=named_scenario_contract("zero_rate"))
        nasdaq = [row for row in cross.to_pylist() if row["family_id"] == "nasdaq_family"][0]
        self.assertFalse(nasdaq["cross_comparable"])
        self.assertEqual(nasdaq["undefined_reason"], "incompatible_clock_class")
        self.assertTrue(nasdaq["ndx_present"])
        self.assertTrue(nasdaq["ndxp_present"])
        self.assertFalse(nasdaq["qqq_present"])
        self.assertIsNone(nasdaq["ndx_atm_iv"])

    def test_report_requires_intended_dates_and_keeps_unavailable_statuses(self):
        req = "2021-01-05"
        board = _board([
            _quote_row(bid=2.5, ask=2.0, usable=False, base_class="crossed"),
            _quote_row(contract_id=2, millistrike=4010000, quoted=False, usable=False, bid=None, ask=None, mid=None),
        ])
        support = _underlier([{
            "chain": "SPXW", "request_date": req, "cut_label": "10:00", "cash_close": 4000.0,
            "cash_date": "2021-01-04", "cash_same_date": False,
            "cash_assumption": "prior_available_cash_date_close",
        }])
        out = build_valuation_tables(board, support, _empty_support(), _actions([]),
                                     scenario_contract=named_scenario_contract("zero_rate"))
        with self.assertRaises(ContractError):
            build_valuation_report(out["contract_cut"], out["expiry_cut"], out["coverage"], intended_dates=())
        report = build_valuation_report(
            out["contract_cut"], out["expiry_cut"], out["coverage"],
            intended_dates=["2021-01-05"], scenario_contract=named_scenario_contract("zero_rate"),
        )
        self.assertFalse(report["certification_claimed"])
        self.assertEqual(report["statistics"]["seed"], 20260908)
        self.assertIn("no_context_forecast", report["exclusions"])
        cov = out["coverage"].to_pylist()[0]
        self.assertGreaterEqual(cov["n_crossed"], 1)
        self.assertGreaterEqual(cov["n_listed_unquoted"], 1)
        self.assertIn("n_missing_underlier", cov)
        self.assertIn("n_weak_vega", cov)
        self.assertIn("n_greek_unstable", cov)


if __name__ == "__main__":
    unittest.main()
