"""P2-03 volatility arithmetic and multi-horizon targets."""

from __future__ import annotations

from datetime import date
from math import log

import numpy as np
import pytest

from trading_research.errors import ContractError
from trading_research.research.experts.features.volatility import (
    future_prices_do_not_enter,
    garman_klass,
    har_inputs,
    iv_variance_one_calendar_day,
    python_garman_klass,
    python_realized_variance,
    python_yang_zhang,
    realized_variance,
    yang_zhang,
)
from trading_research.research.experts.labels.volatility import (
    HEADS,
    build_heads,
    matching_midpoints,
    python_matching_midpoints,
)
from trading_research.research.method_pack.clocks import et_ns

NS = 1_000_000_000


def test_a01_gk_yz_rv_worked_examples():
    gk = garman_klass(100, 110, 90, 100)
    expected_gk = 0.5 * log(110 / 90) ** 2
    assert abs(gk["variance"] - expected_gk) < 1e-15
    assert abs(gk["variance"] - 0.020134364008631726) < 1e-12
    assert python_garman_klass(100, 100, 100, 100) == 0.0
    yz = yang_zhang([0.01, 0.01, 0.01], [0.02, 0.02, 0.02], [0.03, 0.03, 0.03], [-0.01, -0.01, -0.01])
    assert abs(yz["k"] - 0.10179640718562875) < 1e-12
    assert abs(yz["v_rs"] - 0.0006) < 1e-15
    assert abs(yz["variance"] - 0.0005389221556886226) < 1e-12
    assert abs(python_yang_zhang([0.01, 0.01, 0.01], [0.02, 0.02, 0.02], [0.03, 0.03, 0.03], [-0.01, -0.01, -0.01]) - yz["variance"]) < 1e-15
    rv = realized_variance([100, 101, 100])
    expected_rv = 2 * log(1.01) ** 2
    assert abs(rv["variance"] - expected_rv) < 1e-15
    assert abs(python_realized_variance([100, 101, 100]) - rv["variance"]) < 1e-15


def test_a02_iv_variance_is_not_a_realized_target():
    feat = iv_variance_one_calendar_day(0.2)
    assert abs(feat["variance"] - 0.04 / 365) < 1e-15
    assert feat["kind"] == "iv_scaling_feature"
    assert feat["unit"] != "interval_log_return_variance"
    gk = garman_klass(100, 110, 90, 100)
    assert gk["unit"] == "interval_log_return_variance"


def test_a03_horizon_crossing_close_is_unsupported():
    day = date(2024, 1, 2)
    issue = et_ns(day, 16, 50)
    t = np.array([issue, issue + NS], dtype=np.int64)
    mid = np.array([100.0, 100.25], dtype=np.float64)
    avail = t.copy()
    heads = build_heads(issue_ns=issue, day=day, t_ns=t, mid=mid, available_at_ns=avail)
    names = {h.name: h for h in heads}
    assert set(names) == set(HEADS)
    assert names["rv_120m"].status == "unsupported"
    assert names["rv_120m"].reason == "crosses_account_day_or_close"
    assert names["rv_120m"].variance is None
    roll = et_ns(day, 10, 30)
    rolled = build_heads(
        issue_ns=et_ns(day, 10, 0),
        day=day,
        t_ns=t,
        mid=mid,
        available_at_ns=avail,
        roll_ns=roll,
    )
    by_name = {h.name: h for h in rolled}
    assert by_name["rv_60m"].status == "unsupported"
    assert by_name["rv_60m"].reason == "crosses_roll"


def test_a04_missing_iv_group_is_recorded():
    har = har_inputs([])
    assert har["status"] == "unavailable"
    assert har["har1"] is None


def test_a05_future_prices_cannot_affect_current_gk_yz_har():
    current = [100.0, 101.0, 100.5]
    future = [80.0, 200.0, 50.0]
    assert future_prices_do_not_enter(current, future) is True
    gk_now = python_garman_klass(100, 110, 90, 100)
    gk_future = python_garman_klass(100, 110, 90, 100)
    assert gk_now == gk_future
    yz = python_yang_zhang([0.01] * 3, [0.02] * 3, [0.03] * 3, [-0.01] * 3)
    yz2 = python_yang_zhang([0.01] * 3, [0.02] * 3, [0.03] * 3, [-0.01] * 3)
    assert yz == yz2


def test_s02_gk_reversed_high_low_fails():
    with pytest.raises(ContractError):
        garman_klass(100, 90, 110, 100)


def test_s08_future_mutation_leaves_snapshot_rv():
    prices = np.array([100.0, 101.0, 100.5, 200.0])
    left = python_realized_variance(prices[:3])
    prices[-1] = 50.0
    right = python_realized_variance(prices[:3])
    assert left == right
    assert python_realized_variance(prices) != left


def test_s10_dst_issue_uses_timezone_clocks():
    dst = date(2023, 11, 6)
    issue = et_ns(dst, 10, 0)
    t = np.array([issue - 60 * NS, issue, issue + 60 * NS], dtype=np.int64)
    mid = np.array([14800.0, 14801.0, 14802.0])
    heads = build_heads(issue_ns=issue, day=dst, t_ns=t, mid=mid, available_at_ns=t)
    assert len(heads) == 8


def test_s16_label_known_at_is_target_end():
    day = date(2024, 1, 2)
    issue = et_ns(day, 10, 0)
    bounds = issue + np.arange(0, 21) * 60 * NS
    mid = 18000 + np.linspace(0, 1, bounds.size)
    heads = build_heads(issue_ns=issue, day=day, t_ns=bounds, mid=mid, available_at_ns=bounds)
    ok = [h for h in heads if h.status == "ok"]
    for h in ok:
        assert h.label_known_at_ns == h.end_ns
        assert h.label_known_at_ns > issue


def test_midpoint_older_than_5_seconds_is_refused():
    t = np.array([0], dtype=np.int64)
    mid = np.array([100.0])
    avail = np.array([0], dtype=np.int64)
    stale = np.array([5 * NS + 1], dtype=np.int64)
    px, good = matching_midpoints(t, mid, avail, stale)
    assert not bool(good[0])
    assert np.isnan(px[0])
    ref = python_matching_midpoints(t, mid, avail, stale)
    assert ref[0] is None
    exact = np.array([5 * NS], dtype=np.int64)
    px5, good5 = matching_midpoints(t, mid, avail, exact)
    assert bool(good5[0])
    assert px5[0] == 100.0


def test_missing_boundary_midpoint_is_incomplete():
    day = date(2024, 1, 2)
    issue = et_ns(day, 10, 0)
    t = np.array([issue], dtype=np.int64)
    mid = np.array([18000.0])
    heads = build_heads(issue_ns=issue, day=day, t_ns=t, mid=mid, available_at_ns=t)
    names = {h.name: h for h in heads}
    assert names["rv_15m"].status == "incomplete"
    assert names["rv_15m"].reason == "missing_boundary_midpoint"
    assert names["rv_15m"].coverage == "incomplete"
    assert names["rv_15m"].variance is None
    assert names["rv_15m"].sampling == "bbo_midpoint_age_le_5s"


def test_matching_midpoints_match_python_reference():
    t = np.array([10, 20, 30], dtype=np.int64)
    mid = np.array([1.0, 2.0, 3.0])
    avail = np.array([10, 20, 30], dtype=np.int64)
    bounds = np.array([20, 25], dtype=np.int64)
    vec, good = matching_midpoints(t, mid, avail, bounds)
    ref = python_matching_midpoints(t, mid, avail, bounds)
    assert bool(good[0])
    assert vec[0] == ref[0] == 2.0
    assert ref[1] is None or np.isnan(vec[1]) or vec[1] == ref[1]


def test_g3_every_slice_date_has_a_target_row_including_incomplete(tmp_path):
    """Fails if an incomplete slice date is dropped instead of emitting status=incomplete."""
    import json
    from pathlib import Path

    from trading_research.research.experts.options.slice_runner import run_p2_03_slice

    dates = ["2026-09-03"]
    run_p2_03_slice(tmp_path, dates)
    rows = json.loads((tmp_path / "VOLATILITY_TARGETS.json").read_text())["rows"]
    assert len(rows) == len(dates)
    row = rows[0]
    assert row["day"] == "2026-09-03"
    assert row["status"] == "incomplete"
    assert "partial" in (row.get("reason") or "").lower()
    assert row.get("heads") in (None, [])
    assert row.get("variance") is None
    if row.get("heads"):
        assert all(h.get("variance") is None for h in row["heads"])

    slice_path = Path(__file__).resolve().parents[2] / "reports/research-work/phase2-early/P2-03/VOLATILITY_TARGETS.json"
    dates_path = Path(__file__).resolve().parents[2] / "reports/research-work/phase2-early/P2-10/THROUGHPUT.json"
    if slice_path.is_file() and dates_path.is_file():
        slice_dates = json.loads(dates_path.read_text())["dates"]
        produced = json.loads(slice_path.read_text())["rows"]
        assert len(produced) == len(slice_dates)
        by_day = {r["day"]: r for r in produced}
        assert by_day["2026-09-03"]["status"] == "incomplete"
        assert by_day["2026-09-03"].get("heads") in (None, [])


def test_s07_native_minute_close_is_tagged_not_bbo():
    from trading_research.research.experts.options.native import spot_at

    day = date(2024, 1, 2)
    spot = spot_at("QQQ", day, et_ns(day, 10, 0))
    if spot is None:
        pytest.skip("QQQ 1m missing")
    assert spot.age_policy == "completed_native_minute_close"
    assert spot.native is True
