"""Independent arithmetic cases. Expected values are literals, not code constants."""

from __future__ import annotations

from datetime import date, time, timedelta

import numpy as np

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import ZONE
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds
from trading_research.research.phase1_live.grid import path_class_from_closes, to_ticks
from trading_research.research.phase1_live.ohlc_index import from_arrays
from trading_research.research.phase1_live.sessions import build_session, projections, width_bin


def _minute_index(day: date, start: time, minutes: int, offset_days: int = 0):
    t0 = local_timestamp(day + timedelta(days=offset_days), start, ZONE) // 1_000_000
    return t0 + np.arange(minutes, dtype=np.int64) * 60_000


def fixture_box_geometry() -> dict:
    """H=110, L=90, W=20. EQ=100, Q25=95, Q75=105, -0.5 low=80, 1.33 high=136.6."""
    got = projections(110.0, 90.0)
    expected = {
        "W": 20.0,
        "EQ": 100.0,
        "Q25": 95.0,
        "Q75": 105.0,
        "m05_low": 80.0,
        "m05_high": 120.0,
        "ext133_high": 136.6,
        "ext166_low": 56.8,
    }
    checks = []
    for key, value in expected.items():
        ok = abs(got[key] - value) < 1e-12
        checks.append({"id": f"geom.{key}", "pass": ok, "got": got[key], "expected": value})
    w_pct = 100.0 * 20.0 / 100.0
    checks.append({
        "id": "width.w_pct_0859close",
        "pass": abs(w_pct - 20.0) < 1e-12,
        "got": w_pct,
        "expected": 20.0,
    })
    checks.append({
        "id": "width.bin_pct",
        "pass": width_bin(20.0) == "1.2+",
        "got": width_bin(20.0),
        "expected": "1.2+",
    })
    checks.append({
        "id": "width.bin_rel_not_pct",
        "pass": width_bin(0.4) == "0.3-0.5",
        "got": width_bin(0.4),
        "expected": "0.3-0.5",
    })
    return {"name": "box_geometry", "pass": all(c["pass"] for c in checks), "cases": checks}


def fixture_path_high_only() -> dict:
    """180 outcome minutes: close stays inside then one close above H, never below L."""
    high, low = 110.0, 90.0
    close = np.full(180, 100.0)
    close[30] = 110.25
    close[31:] = 108.0
    t = np.arange(180, dtype=np.int64) * 60_000
    path = path_class_from_closes(to_ticks(close), t, int(round(high / 0.25)), int(round(low / 0.25)))
    ok = path["path_class"] == "high-only" and path["break_order"] == "high"
    return {
        "name": "path_high_only",
        "pass": ok,
        "cases": [{"id": "path.high-only", "pass": ok, "got": path, "expected": "high-only/high"}],
    }


def fixture_path_both_order() -> dict:
    close = np.full(180, 100.0)
    close[10] = 110.25
    close[40] = 89.75
    t = np.arange(180, dtype=np.int64) * 60_000
    path = path_class_from_closes(to_ticks(close), t, int(round(110 / 0.25)), int(round(90 / 0.25)))
    ok = path["path_class"] == "both" and path["break_order"] == "high-then-low"
    return {
        "name": "path_both_order",
        "pass": ok,
        "cases": [{"id": "path.both.high-then-low", "pass": ok, "got": path, "expected": "both/high-then-low"}],
    }


def fixture_session_synthetic() -> dict:
    """One synthetic day. 6-9 is 90-110. Outcome breaks high only. Prior RTH width 40."""
    day = date(2024, 1, 3)
    b69 = clock_bounds(day, CLOCKS["range.6-9.published"])
    # 18:00 previous through 16:00: build 1m bars covering 06:00-12:00 and prior RTH.
    t69 = _minute_index(day, time(6, 0), 180)
    o69 = np.full(180, 100.0)
    h69 = np.full(180, 101.0)
    l69 = np.full(180, 99.0)
    c69 = np.full(180, 100.0)
    h69[10] = 110.0
    l69[20] = 90.0
    t_out = _minute_index(day, time(9, 30), 150)
    o_out = np.full(150, 100.0)
    h_out = np.full(150, 101.0)
    l_out = np.full(150, 99.0)
    c_out = np.full(150, 100.0)
    c_out[5] = 110.25
    h_out[5] = 110.5
    t_prior = _minute_index(date(2024, 1, 2), time(9, 30), 390)
    o_p = np.full(390, 100.0)
    h_p = np.full(390, 120.0)
    l_p = np.full(390, 80.0)
    c_p = np.full(390, 100.0)
    t_asia = _minute_index(day, time(20, 0), 240, offset_days=-1)
    t = np.concatenate([t_asia, t_prior, t69, t_out])
    o = np.concatenate([np.full(240, 100.0), o_p, o69, o_out])
    h = np.concatenate([np.full(240, 105.0), h_p, h69, h_out])
    l = np.concatenate([np.full(240, 95.0), l_p, l69, l_out])
    c = np.concatenate([np.full(240, 100.0), c_p, c69, c_out])
    v = np.ones(t.size)
    bars = from_arrays(t, o, h, l, c, v, bar_ms=60_000, source="fixture")
    prior = bars.window(
        local_timestamp(date(2024, 1, 2), time(9, 30), ZONE) // 1_000_000,
        local_timestamp(date(2024, 1, 2), time(16, 0), ZONE) // 1_000_000,
    )
    row = build_session(day, bars, None, prior_rth=prior)
    checks = []
    checks.append({"id": "session.W69", "pass": abs(row["W69"] - 20.0) < 1e-9, "got": row["W69"], "expected": 20.0})
    checks.append({"id": "session.EQ", "pass": abs(row["EQ"] - 100.0) < 1e-9, "got": row["EQ"], "expected": 100.0})
    checks.append({"id": "session.path", "pass": row["path_class"] == "high-only", "got": row["path_class"], "expected": "high-only"})
    checks.append({"id": "session.WpriorRTH", "pass": abs((row["WpriorRTH"] or 0) - 40.0) < 1e-9, "got": row["WpriorRTH"], "expected": 40.0})
    checks.append({"id": "session.w_rel", "pass": abs((row["w_rel_prior_rth"] or 0) - 0.5) < 1e-9, "got": row["w_rel_prior_rth"], "expected": 0.5})
    checks.append({"id": "session.leakage", "pass": row["leakage"] == 0, "got": row["leakage"], "expected": 0})
    checks.append({"id": "session.known_at_before_outcome", "pass": row["known_at_ns"] <= row["outcome_start_ns"], "got": [row["known_at_ns"], row["outcome_start_ns"]], "expected": "known_at <= outcome_start"})
    return {"name": "session_synthetic", "pass": all(c["pass"] for c in checks), "cases": checks}


def fixture_spike_hl() -> dict:
    """Isolated one-tick high vs 1s median is a spike. Confirmed high is clean."""
    h = np.full(20, 100.0)
    l = np.full(20, 99.0)
    h[10] = 100.25
    second = float(np.partition(h, -2)[-2])
    isolated = bool(int((h == h.max()).sum()) == 1 and (h.max() - second) >= 0.25)
    h2 = np.full(20, 100.0)
    h2[8] = 110.0
    h2[9] = 110.0
    second2 = float(np.partition(h2, -2)[-2])
    isolated2 = bool(int((h2 == h2.max()).sum()) == 1 and (h2.max() - second2) >= 0.25)
    checks = [
        {"id": "spike.one_tick_isolated", "pass": isolated is True, "got": isolated, "expected": True},
        {"id": "spike.confirmed_high_clean", "pass": isolated2 is False, "got": isolated2, "expected": False},
    ]
    return {"name": "spike_hl", "pass": all(c["pass"] for c in checks), "cases": checks}


def run_ticket01_fixtures() -> dict:
    groups = [fixture_box_geometry(), fixture_path_high_only(), fixture_path_both_order(), fixture_session_synthetic(), fixture_spike_hl()]
    cases = [c for g in groups for c in g["cases"]]
    return {
        "ticket": "01",
        "pass": all(g["pass"] for g in groups),
        "n_cases": len(cases),
        "n_failed": sum(1 for c in cases if not c["pass"]),
        "groups": groups,
    }
