"""C02–C07 printed core fixtures.

Core fixture execution is deliberately hermetic.  Acquired-data audits are a
separate explicit operation; passing a production-looking ``data_root`` here
must not turn the printed synthetic fixture into a production read.
"""

from __future__ import annotations

from fractions import Fraction

from trading_research.research.method_pack.adapters import c03_f1
from trading_research.research.method_pack.clocks import c02_f1
from trading_research.research.method_pack.logic import verdict
from trading_research.research.method_pack.outcomes import c06_f1
from trading_research.research.method_pack.report import c07_f1


def c04_f1() -> dict:
    cases = [
        ("T", True, True, True),
        ("F", True, True, False),
        ("U", True, False, None),
        ("F2", False, False, None),
    ]
    labels = []
    for name, base, cov, seq in cases:
        labels.append(verdict(base, cov, seq))
    p = labels.count("pass")
    f = labels.count("fail")
    u = labels.count("unknown")
    return {
        "verdicts": labels,
        "p": p,
        "f": f,
        "u": u,
        "n": p + f,
        "N": p + f + u,
        "later_target_repairs_fail": False,
    }


def run_core_fixtures(data_root=None) -> list[dict]:
    rows = []
    c02 = c02_f1()
    c02_ok = (
        c02["winter_0930_et_ns"] == c02["winter_1430_utc_ns"]
        and c02["summer_0930_et_ns"] == c02["summer_1330_utc_ns"]
        and c02["range_at_0945_available"] is False
        and c02["range_at_1000"]["H"] == __import__("decimal").Decimal("105")
        and c02["range_at_1000"]["L"] == __import__("decimal").Decimal("100")
        and c02["later_1000_bar_changes_range"] is False
        and c02["five_minute_missing_1002_complete"] is False
        and c02["grouping_five_available_rows_complete"] is False
    )
    rows.append(_row("C02-F1", c02_ok, c02,
                     inputs={"source": "synthetic_c02_clock_fixture", "range": "[09:00,10:00)", "missing_minute": "10:02"},
                     expected={"winter_0930_utc": True, "summer_0930_utc": True, "range_at_0945_available": False,
                               "range_at_1000": {"H": "105", "L": "100"}, "later_1000_bar_changes_range": False,
                               "five_minute_complete": False}))
    # C03-F1 is the printed eight-row adapter fixture and is synthetic by
    # contract.  ``data_root`` is retained only for the runner's API shape.
    c03 = c03_f1()
    c03_ok = bool(c03.get("matches_printed_table"))
    rows.append(_row("C03-F1", c03_ok, c03,
                     inputs={"source": "synthetic_c03_mbp1_trade_rows", "instrument_id": 42004177, "q": "0.25",
                             "qualifying_rows": 8},
                     expected={"buy_volume": 7, "sell_volume": 4, "total": 11, "delta": 3,
                               "first_spread_ticks": "2", "tie_batch_size": 5, "tie_count": 3,
                               "tie_order": "unknown_order"}))
    c04 = c04_f1()
    c04_ok = c04["verdicts"] == ["pass", "fail", "unknown", "fail"] and c04["p"] == 1 and c04["f"] == 2 and c04["u"] == 1 and c04["n"] == 3 and c04["N"] == 4
    rows.append(_row("C04-F1", c04_ok, c04,
                     inputs={"cases": ["pass", "fail", "unknown", "fail"]},
                     expected={"verdicts": ["pass", "fail", "unknown", "fail"], "p": 1, "f": 2, "u": 1,
                               "n": 3, "N": 4}))
    c06 = c06_f1()
    c06_ok = (
        c06["target_first"] == "target_first"
        and c06["invalidation_first"] == "invalidation_first"
        and c06["same_time_unknown"] == "same_time_unknown"
        and c06["pre_decision_high_ignored"] is True
        and c06["censored"] == "censored"
        and c06["gap_unknown"] == "unknown"
    )
    rows.append(_row("C06-F1", c06_ok, c06,
                     inputs={"decision_at": "10:06", "target": "104", "invalidation": "98", "window_end": "10:30"},
                     expected={"target_first": "target_first", "invalidation_first": "invalidation_first",
                               "same_time_unknown": "same_time_unknown", "pre_decision_high_ignored": True,
                               "censored": "censored", "gap_unknown": "unknown"}))
    c07 = c07_f1()
    want_lo = Fraction(2, 3)
    want_hi = Fraction(5, 6)
    c07_ok = (
        c07["n"] == 10 and c07["N"] == 12 and c07["rate"] == 0.8
        and c07["interval_exact"] == [[want_lo.numerator, want_lo.denominator], [want_hi.numerator, want_hi.denominator]]
        and c07["year_n_sum"] == 10
        and c07["empty_rate"] is None and c07["empty_interval"] is None
    )
    rows.append(_row("C07-F1", c07_ok, c07,
                     inputs={"passes": 8, "fails": 2, "unknown": 2, "years": [2024, 2025]},
                     expected={"n": 10, "N": 12, "rate": 0.8,
                               "interval_exact": [[2, 3], [5, 6]], "year_n_sum": 10,
                               "empty_rate": None, "empty_interval": None}))
    return rows


def _row(fid: str, ok: bool, payload: dict, skip_if_missing: bool = False, *, inputs=None, expected=None) -> dict:
    status = "pass" if ok else "fail"
    failures = [] if ok else ["core fixture mismatch"]
    return {
        "id": fid,
        "recipe": fid.split("-")[0],
        "kind": "core",
        "status": status,
        "failures": failures,
        "inputs": inputs or {"fixture": fid, "evidence_mode": "synthetic_fixture"},
        "expected": expected or {"status": "pass"},
        "actual_value": {k: v for k, v in payload.items() if k != "rows"},
        "evidence_mode": "synthetic_fixture",
    }
