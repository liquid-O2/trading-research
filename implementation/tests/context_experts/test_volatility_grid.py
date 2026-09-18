"""Volatility features and forward-RV targets on the quarter-hour grid.

Expected numbers are the contract's own fixtures (VOLATILITY.md) or plain
arithmetic written out here; the cross-check against ``build_heads`` compares
with the receipt-pinned target implementation, not with this module."""

import json
from dataclasses import replace
from datetime import date
from math import log

import numpy as np
import pytest

from trading_research.errors import ContractError
from trading_research.research.experts import snapshots as sn
from trading_research.research.experts.features import volatility_grid as vg
from trading_research.research.experts.features.volatility import garman_klass
from trading_research.research.experts.labels.volatility import build_heads
from trading_research.research.rule_discovery.native import account_day_window

NS = 1_000_000_000
MIN = 60 * NS
DAY = date(2024, 3, 5)


def _frame(points, minutes):
    """points: [(offset seconds, price)], available when they occur."""
    t = np.array([s * NS for s, _ in points], dtype=np.int64)
    px = np.array([p for _, p in points], dtype=np.float64)
    return vg.build_frame(t, px, t, 0, minutes * MIN)


def test_rv_fixture_100_101_100():
    frame = _frame([(0, 100.0), (60, 101.0), (120, 100.0)], 2)
    value, status = vg.window_rv(frame, 0, 2)
    assert status == "ok"
    assert value == pytest.approx(2 * log(1.01) ** 2, abs=1e-15)


def test_gk_fixture_and_reversed_high_low_is_rejected():
    frame = _frame([(1, 100.0), (20, 110.0), (70, 90.0), (110, 100.0)], 2)
    value, status = vg.window_gk(frame, 0, 2)
    assert status == "ok"
    assert value == pytest.approx(0.5 * log(110 / 90) ** 2, abs=1e-15)
    # negative control: a window whose high (85) sits below its low (90) and its open is refused, not computed
    broken = replace(frame, h=np.full(2, 85.0))
    value, status = vg.window_gk(broken, 0, 2)
    assert value is None and status == "rejected:inconsistent OHLC"
    with pytest.raises(ContractError, match="inconsistent OHLC"):
        garman_klass(100, 90, 110, 100)


def _session(day, prev_close, instrument="A", o=0.01, c=0.02, u=0.03, d=-0.01):
    open_ = prev_close * np.exp(o)
    ohlc = [open_, open_ * np.exp(u), open_ * np.exp(d), open_ * np.exp(c)]
    return {"day": day, "instrument_id": instrument, "ohlc_acct": ohlc, "ohlc_rth": ohlc, "gk_acct": 1e-4, "gk_rth": 1e-4, "rv_rth_strict": 2e-5, "rv_acct_strict": None, "rv_acct_cov": 4e-5, "rv_acct_coverage": 0.99}


def _chain(n, **kwargs):
    out, close = [], 100.0
    for i in range(n):
        s = _session(f"d{i}", close, **kwargs)
        out.append(s)
        close = s["ohlc_acct"][3]
    return out


def test_yang_zhang_n3_fixture_through_the_day_level_inputs():
    # o=.01, c=.02, u=.03, d=-.01 on every day: opening and closing variances 0, RS=.0006
    prior = _chain(4)  # the first session only supplies the preceding close
    out = vg.day_level_inputs(prior, yz_n=3, gk_n=3)
    k = 0.34 / (1.34 + 4 / 2)
    assert out["yz3_acct"] == pytest.approx((1 - k) * 0.0006, abs=1e-15)
    assert out["yz3_acct_n"] == 3
    assert out["log_gk3_mean_acct"] == pytest.approx(log(1e-4 + 1e-12))


def test_yang_zhang_never_bridges_a_contract_change_or_a_failed_day_but_does_span_a_holiday():
    prior = _chain(5)
    prior[2] = {**prior[2], "instrument_id": "B"}  # the roll: d1->d2 and d2->d3 both change contract
    assert [r[0] for r in vg.yz_inputs(prior, "acct")] == ["d1", "d4"]
    holiday = _chain(3)
    holiday.insert(1, None)  # a day without a session between d0 and d1
    assert [r[0] for r in vg.yz_inputs(holiday, "acct")] == ["d1", "d2"]
    failed = _chain(3)
    failed[1] = {"day": "d1", "failed": True}
    assert vg.yz_inputs(failed, "acct") == []


def test_har_inputs_use_prior_complete_days_in_log_units():
    prior = [{**s, "rv_rth_strict": v} for s, v in zip(_chain(6), [1e-5, 2e-5, None, 3e-5, 4e-5, 5e-5])]
    out = vg.day_level_inputs(prior)
    assert out["har_rth_har1"] == pytest.approx(log(5e-5 + 1e-12))
    assert out["har_rth_har5"] == pytest.approx(log(np.mean([1e-5, 2e-5, 3e-5, 4e-5, 5e-5]) + 1e-12))
    assert out["har_rth_har22"] is None and out["har_rth_n"] == 5
    assert out["har_acct_strict_har1"] is None  # no strictly complete account day in the chain
    assert out["har_acct_cov_har1"] == pytest.approx(log(4e-5 + 1e-12))


def _synthetic_day(seed=7):
    start, end = account_day_window(DAY)
    rng = np.random.default_rng(seed)
    t = np.arange(start + NS, end, 2 * NS, dtype=np.int64)  # a midpoint every two seconds from 18:00:01
    px = 18000.0 * np.exp(np.cumsum(rng.normal(0, 2e-5, t.size)))
    px = np.round(px * 8) / 8  # eighth-point midpoints
    avail = t + 1_000_000  # known a millisecond after the event
    return start, end, t, px, avail


def test_future_prices_change_targets_and_never_the_features():
    start, end, t, px, avail = _synthetic_day()
    issue = int(sn.rth_grid(DAY)[2])  # 10:00
    base = vg.compute_day(DAY, t, px, avail)
    later = avail > issue
    shocked = px.copy()
    shocked[later] = px[later] * 1.01 + np.linspace(0, 25, int(later.sum()))
    # a quote whose event precedes the issue time but which only becomes known after it is future too
    late_known = np.flatnonzero((t <= issue) & (t > issue - 10 * NS))
    avail2 = avail.copy()
    avail2[late_known[-1]] = issue + NS
    shocked2 = shocked.copy()
    shocked2[late_known[-1]] = px[late_known[-1]] * 1.05
    base2 = vg.compute_day(DAY, t, px, avail2)
    moved = vg.compute_day(DAY, t, shocked2, avail2)
    rows = {r["issue_ns"]: r for r in base2["rows"]}
    rows_moved = {r["issue_ns"]: r for r in moved["rows"]}
    for ns, row in rows.items():
        if ns <= issue:
            assert json.dumps(vg.feature_view(row), sort_keys=True).encode() == json.dumps(vg.feature_view(rows_moved[ns]), sort_keys=True).encode()
    assert rows[issue]["tgt_rv_15m"] is not None
    assert rows[issue]["tgt_rv_15m"] != rows_moved[issue]["tgt_rv_15m"]
    # positive control: the same shock does reach the features of a later issue time
    after = issue + sn.QUARTER_NS
    assert vg.feature_view(rows[after]) != vg.feature_view(rows_moved[after])
    assert base["rows"][0]["is_holdout"] is False


def test_targets_equal_the_registered_heads_and_a_plain_recomputation():
    start, end, t, px, avail = _synthetic_day(seed=11)
    out = vg.compute_day(DAY, t, px, avail)
    issue = int(sn.rth_grid(DAY)[6])  # 11:00
    row = next(r for r in out["rows"] if r["issue_ns"] == issue)
    heads = {h.name: h for h in build_heads(issue_ns=issue, day=DAY, t_ns=t, mid=px, available_at_ns=avail)}
    for name, head in (("tgt_rv_15m", "rv_15m"), ("tgt_rv_30m", "rv_30m"), ("tgt_rv_60m", "rv_60m"), ("tgt_rv_120m", "rv_120m"), ("tgt_rv_remaining_rth", "remaining_rth")):
        assert row[name] == heads[head].variance
        assert row[f"{name}_known_at_ns"] == heads[head].label_known_at_ns

    def boundary(ns):  # plain Python: the last midpoint known at or before ns, at most five seconds old
        best = None
        for a, e, p in zip(avail.tolist(), t.tolist(), px.tolist()):
            if a > ns:
                break
            if e <= ns and ns - a <= 5 * NS:
                best = p
        return best

    fwd = [boundary(issue + k * MIN) for k in range(16)]
    assert row["tgt_rv_15m"] == pytest.approx(sum(log(b / a) ** 2 for a, b in zip(fwd, fwd[1:])), abs=1e-12)
    back = [boundary(issue - (5 - k) * MIN) for k in range(6)]
    assert row["rv_recent_5m"] == pytest.approx(sum(log(b / a) ** 2 for a, b in zip(back, back[1:])), abs=1e-12)


def test_a_missing_boundary_is_incomplete_and_never_bridged():
    start, end, t, px, avail = _synthetic_day(seed=3)
    issue = int(sn.rth_grid(DAY)[4])  # 10:30
    hole = issue + 7 * MIN
    keep = ~((avail > hole - 8 * NS) & (avail <= hole))  # nothing known in the eight seconds before 10:37
    out = vg.compute_day(DAY, t[keep], px[keep], avail[keep])
    row = next(r for r in out["rows"] if r["issue_ns"] == issue)
    assert row["tgt_rv_15m"] is None and row["tgt_rv_15m_status"] == "missing_boundary_midpoint"
    assert row["tgt_rv_15m_known_at_ns"] is None
    later = next(r for r in out["rows"] if r["issue_ns"] == issue + sn.QUARTER_NS)  # 10:45: the hole is behind it
    assert later["tgt_rv_15m_status"] == "ok"
    assert later["rv_recent_15m"] is None and later["rv_recent_5m_status"] == "ok"
    # the last quarter hour of the account day cannot hold a two-hour horizon
    last = out["rows"][-1]
    assert last["tgt_rv_120m"] is None and last["tgt_rv_120m_status"] == "crosses_account_day_or_close"
    assert out["summary"]["rv_rth_strict"] is None and out["summary"]["rv_rth_coverage"] == pytest.approx(1 - 2 / 390)


def test_holdout_days_are_flagged():
    start, end = account_day_window(date(2026, 4, 1))
    t = np.arange(start + NS, start + 3600 * NS, 2 * NS, dtype=np.int64)
    out = vg.compute_day(date(2026, 4, 1), t, np.full(t.size, 20000.0), t)
    assert all(r["is_holdout"] for r in out["rows"])
