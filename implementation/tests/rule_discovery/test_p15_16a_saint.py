"""P15-16A saint-track B0.2 rulings, replay, funnel, and B0/B0.1 byte identity."""
from __future__ import annotations

import inspect
import json
from datetime import date, timedelta
from decimal import Decimal as D
import tempfile
from pathlib import Path

from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.rule_discovery.census_reader import sha256_file
from trading_research.research.rule_discovery.source_adapters.b02_saint_track import (
    AUTHOR_EXAMPLES,
    HASH_DATES,
    REPAIR_DIR,
    SLICE_DATES,
    TRACK_DIR,
    SynthMarket,
    account_day_for_example,
    funnel_counts,
    native_calendar_day,
    outside_native_tape,
    sha256_json,
    synth_bar,
    write_json,
)

TRACK_SHA256 = {
    "FUNNEL_MEMBER-TWO-REASONS.json": "b6c9e313f722f7b9de406c5bb56a43fcc62a57fb369744b3a996113255846860",
    "FUNNEL_SAINT-AMT.json": "badc59dae64539ed50d9c4049483c06e520d5072ffeda9f1610e63e687a5b742",
    "REPLAY_SAINT.json": "47ddf0b3cf8ebb33a74d733d9a2c3c5d292093f88008b392846a3eb6987403f7",
    "RULES_KEANI.json": "d367e2fa89483d8f9f3f79decf3100a28be58777f85753c3cc537788e507cde3",
    "RULES_MEMBER-TWO-REASONS.json": "f9ab96429b5aa871cf199c11c900a85581714dbe22b7ad5fa90f417c113db2ae",
    "RULES_SAINT-AMT.json": "ce357cdfabdefbd29675632fbdceec36be69bb298287e3fdd24319077a2572d3",
    "STATISTICS_SAINT.json": "b70f35a3874075240bcd5f22aa3d25f92cdf665e2d136b60f35c809fe3194c91",
}
from trading_research.research.rule_discovery.source_adapters import keani as keani_mod
from trading_research.research.rule_discovery.source_adapters import member as member_mod
from trading_research.research.rule_discovery.source_adapters import saint as saint_mod
from trading_research.research.rule_discovery.source_adapters.keani import replay_example as keani_replay
from trading_research.research.rule_discovery.source_adapters.keani import scan_b02 as keani_scan
from trading_research.research.rule_discovery.source_adapters.member import replay_example as member_replay
from trading_research.research.rule_discovery.source_adapters.member import scan_b02 as member_scan
from trading_research.research.rule_discovery.source_adapters.saint import replay_example as saint_replay
from trading_research.research.rule_discovery.source_adapters.saint import scan_b02 as saint_scan
from trading_research.research.rule_discovery.source_adapters.common import dual_scan, load_source_market

WORK_DIR = Path(tempfile.gettempdir()) / "p15_16a_gate_out"  # test output, kept out of the evidence tree
WORK_DIR.mkdir(parents=True, exist_ok=True)
DAY = date(2026, 1, 15)
START = clock(DAY - timedelta(days=1), "18:00")
END = clock(DAY, "16:00")
MINUTE = 60_000_000_000
BALANCED = {
    "poc": D("150"),
    "vah": D("180"),
    "val": D("120"),
    "rows": [
        {"price": D("150"), "total_volume": 100},
        {"price": D("151"), "total_volume": 80},
        {"price": D("149"), "total_volume": 80},
        {"price": D("120"), "total_volume": 5},
        {"price": D("180"), "total_volume": 5},
    ],
}
TRENDING = {
    "poc": D("100"),
    "vah": D("200"),
    "val": D("100"),
    "rows": [{"price": D(str(100 + i)), "total_volume": 8} for i in range(0, 101, 4)] + [{"price": D("150"), "total_volume": 1}],
}
DOUBLE = {
    "poc": D("110"),
    "vah": D("185"),
    "val": D("108"),
    "rows": [
        {"price": D("110"), "total_volume": 80},
        {"price": D("111"), "total_volume": 70},
        {"price": D("109"), "total_volume": 70},
        {"price": D("180"), "total_volume": 80},
        {"price": D("179"), "total_volume": 70},
        {"price": D("181"), "total_volume": 70},
        {"price": D("145"), "total_volume": 5},
    ],
}


def _t(hhmm: str, day: date = DAY) -> int:
    return clock(day, hhmm)


def _fill(start_ns: int, n: int, o, h, l, c, *, delta=1, volume=10) -> list[dict]:
    rows = []
    for i in range(n):
        rows.append(synth_bar(start_ns + i * MINUTE, o, h, l, c, delta=delta, volume=volume))
    return rows


def _stage(episode, name):
    for item in episode.get("stages") or []:
        if item.get("stage") == name:
            return item
    return None


def _continuation_bars(*, fast: bool, future_fast: bool = False, second_retest: bool = False) -> list[dict]:
    t0 = _t("09:50")
    bars = _fill(START, 2, 150, 151, 149, 150)
    if fast:
        approach = _fill(t0, 5, 150, 200, 149, 198, delta=20, volume=20)
    else:
        approach = _fill(t0, 5, 199, 200, 198.75, 199.25, delta=1, volume=10)
    brk = synth_bar(t0 + 5 * MINUTE, 199.5, 202, 199, 201.5, delta=5)
    # the shared cycle rule (break_retest.py): after the break price departs
    # (twenty-five points) and the retest is the first bar back within fifteen
    # points of the level from the broken side
    depart = synth_bar(t0 + 6 * MINUTE, 201.5, 226, 201, 225, delta=5)
    retest = synth_bar(t0 + 7 * MINUTE, 225, 225.5, 205, 206, delta=-1)
    rows = bars + approach + [brk, depart, retest]
    if second_retest:
        rows.append(synth_bar(t0 + 8 * MINUTE, 206, 230, 205.5, 229, delta=3))
        rows.append(synth_bar(t0 + 9 * MINUTE, 229, 229.5, 204, 205, delta=-1))
    if future_fast:
        rows.append(synth_bar(t0 + 20 * MINUTE, 150, 200, 149, 198, delta=40, volume=50))
    return rows


def _saint_market(bars, extra_fx=None, **kw):
    fx = {
        "balance": {"low": D("100"), "high": D("200"), "start": START, "known_at": START, "id": "bal", "width": D("100")},
        "profile": extra_fx.pop("profile", BALANCED) if extra_fx else BALANCED,
        "htf_control": "up",
    }
    if extra_fx:
        fx.update(extra_fx)
    return SynthMarket(DAY, bars, start=START, end=END, fixtures=fx, **kw)


def test_F04_arrival_fast_vs_slow():
    slow = saint_scan(_saint_market(_continuation_bars(fast=False)), {"family": "SAINT-AMT", "branch": "continuation_retest"})
    assert slow["episodes"], slow
    conf = _stage(slow["episodes"][0], "confirmation")
    assert conf["operands"]["arrival"] == "slow"
    assert conf["verdict"] == "pass"
    fast_cont = saint_scan(_saint_market(_continuation_bars(fast=True)), {"family": "SAINT-AMT", "branch": "continuation_retest"})
    assert fast_cont["episodes"]
    assert _stage(fast_cont["episodes"][0], "confirmation")["operands"]["arrival"] == "fast"
    assert _stage(fast_cont["episodes"][0], "confirmation")["verdict"] == "fail"
    t0 = _t("09:50")
    trapped_bars = _fill(START, 2, 150, 151, 149, 150) + _fill(t0, 5, 150, 200, 149, 198, delta=20) + [
        synth_bar(t0 + 5 * MINUTE, 120, 121, 98, 99, delta=-8)
    ]
    trapped = saint_scan(_saint_market(trapped_bars), {"family": "SAINT-AMT", "branch": "trapped_buyers_retest"})
    shorts = [e for e in trapped["episodes"] if e["side"] == "short"]
    assert shorts
    assert _stage(shorts[0], "confirmation")["operands"]["arrival"] == "fast"


def test_F04_arrival_ignores_future_bars():
    doc = saint_scan(
        _saint_market(_continuation_bars(fast=False, future_fast=True)),
        {"family": "SAINT-AMT", "branch": "continuation_retest"},
    )
    assert doc["episodes"]
    assert _stage(doc["episodes"][0], "confirmation")["operands"]["arrival"] == "slow"


def test_F04_profile_excludes_trend():
    trend = saint_scan(
        _saint_market(_continuation_bars(fast=False), extra_fx={"profile": TRENDING}),
        {"family": "SAINT-AMT", "branch": "continuation_retest"},
    )
    assert trend["episodes"]
    assert _stage(trend["episodes"][0], "context")["operands"]["shape"] == "trending"
    assert _stage(trend["episodes"][0], "context")["verdict"] == "fail"
    ok = saint_scan(_saint_market(_continuation_bars(fast=False)), {"family": "SAINT-AMT", "branch": "continuation_retest"})
    assert _stage(ok["episodes"][0], "context")["verdict"] == "pass"


def test_F04_alignment_not_from_trade_side():
    doc = saint_scan(
        _saint_market(_continuation_bars(fast=False), extra_fx={"htf_control": "down"}),
        {"family": "SAINT-AMT", "branch": "continuation_retest"},
    )
    assert doc["episodes"]
    ep = doc["episodes"][0]
    assert ep["side"] == "long"
    conf = _stage(ep, "confirmation")
    assert conf["operands"]["htf_control"] == "down"
    assert conf["operands"]["ltf_break"] == "up"
    assert conf["operands"]["alignment_ok"] is False
    assert conf["verdict"] == "fail"


def test_F04_no_literal_stage_pass_stamps():
    src = inspect.getsource(saint_mod).replace(" ", "")
    for name in ("confirmation", "objective", "trigger", "reference"):
        assert f'stage("{name}","pass"' not in src
        assert f"stage('{name}','pass'" not in src


def test_F04_double_shelf_target():
    doc = saint_scan(
        _saint_market(_continuation_bars(fast=False), extra_fx={"profile": DOUBLE}),
        {"family": "SAINT-AMT", "branch": "continuation_retest"},
    )
    assert doc["episodes"]
    ep = [e for e in doc["episodes"] if e["side"] == "long"][0]
    assert (ep.get("values") or {}).get("profile_shape") == "double"
    obj = _stage(ep, "objective")
    assert obj is not None
    assert obj["operands"]["selector"] == "opposite_shelf_near_edge"
    assert D(str(obj["operands"]["target"])) == D("179")
    assert D(str(obj["operands"]["target"])) != D("200")


def test_F05_no_older_auction_gate():
    t0 = _t("10:00")
    bars = _fill(START, 2, 150, 151, 149, 150) + [
        synth_bar(t0, 99, 100, 80, 85, delta=-5),
        synth_bar(t0 + MINUTE, 86, 90, 82, 88, delta=-1),
        synth_bar(t0 + 2 * MINUTE, 87, 91, 83, 87, delta=-1),
        synth_bar(t0 + 3 * MINUTE, 90, 101, 88, 100.5, delta=3),
        synth_bar(t0 + 4 * MINUTE, 140, 151, 139, 150, delta=2),
        synth_bar(t0 + 5 * MINUTE, 150, 151, 149, 150, delta=1),
        synth_bar(t0 + 6 * MINUTE, 150, 151, 149, 150, delta=1),
        synth_bar(t0 + 7 * MINUTE, 150, 151, 149, 150, delta=1),
        synth_bar(t0 + 8 * MINUTE, 150, 151, 149, 150, delta=1),
        synth_bar(t0 + 9 * MINUTE, 150, 151, 149, 150, delta=1),
    ]
    doc = saint_scan(
        _saint_market(bars, extra_fx={"prior_va": {"val": D("80"), "vah": D("95")}}),
        {"family": "SAINT-AMT", "branch": "failed_auction_return"},
    )
    assert doc["episodes"]
    shorts = [e for e in doc["episodes"] if e["side"] == "short"]
    assert shorts
    conf = _stage(shorts[0], "confirmation")
    assert conf["operands"]["older_auction_gate"] is False
    assert shorts[0]["values"]["older_auction_gate"] is False
    assert conf["verdict"] == "pass"


def test_F05_poc_tell_selects_target():
    t0 = _t("10:00")
    fail_bars = _fill(START, 2, 150, 151, 149, 150)
    for i in range(3):
        fail_bars.append(synth_bar(t0 + i * MINUTE, 151, 151, 149, 150, delta=-1))
    fail_doc = saint_scan(_saint_market(fail_bars), {"family": "SAINT-AMT", "branch": "poc_traversal"})
    assert fail_doc["episodes"]
    assert fail_doc["episodes"][0]["values"]["target_edge"] == "VAL"
    push = _fill(START, 2, 150, 151, 149, 150) + [
        synth_bar(t0, 150, 160, 150, 158, delta=10),
        synth_bar(t0 + MINUTE, 157, 158, 149.75, 151, delta=1),
        synth_bar(t0 + 2 * MINUTE, 151, 170, 151, 165, delta=8),
    ]
    push_doc = saint_scan(_saint_market(push), {"family": "SAINT-AMT", "branch": "poc_traversal"})
    assert push_doc["episodes"]
    assert push_doc["episodes"][0]["values"]["target_edge"] == "VAH"
    assert push_doc["episodes"][0]["side"] == "long"


def test_F05_poc_none_open_is_not_a_push():
    """A bar with C/delta but no open is not close-above-open; do not crash or admit VAH."""
    t0 = _t("10:00")
    bars = _fill(START, 2, 150, 151, 149, 150) + [
        synth_bar(t0, 150, 160, 150, 158, delta=10),
        synth_bar(t0 + MINUTE, 157, 158, 149.75, 151, delta=1),
        synth_bar(t0 + 2 * MINUTE, 151, 170, 151, 165, delta=8),
    ]
    for row in bars:
        row["O"] = None
    doc = saint_scan(_saint_market(bars), {"family": "SAINT-AMT", "branch": "poc_traversal"})
    assert doc["episodes"]
    assert doc["episodes"][0]["values"].get("target_edge") != "VAH"


def test_RR22_asia_session_not_ny_only():
    asia_day = date(2026, 8, 11)
    start = clock(date(2026, 8, 10), "18:00")
    end = clock(asia_day, "16:00")
    t = clock(date(2026, 8, 10), "19:51")
    bars = _fill(start, 2, 29750, 29760, 29740, 29750) + _fill(t - 5 * MINUTE, 5, 29741, 29742, 29739, 29740.25) + [
        synth_bar(t, 29740, 29740, 29720, 29725, delta=-8),
        synth_bar(t + MINUTE, 29726, 29741, 29724, 29730, delta=1),
    ]
    market = SynthMarket(
        asia_day,
        bars,
        start=start,
        end=end,
        fixtures={
            "balance": {"low": D("29600"), "high": D("29960"), "start": start, "known_at": start, "id": "asia", "width": D("360")},
            "profile": {"poc": D("29780"), "vah": D("29900"), "val": D("29640"), "rows": [{"price": D("29780"), "total_volume": 100}, {"price": D("29781"), "total_volume": 90}, {"price": D("29779"), "total_volume": 90}]},
            "htf_control": "down",
            "intraday_levels": [D("29740")],
        },
        at_overrides={"09:30": clock(asia_day, "09:30"), "-1:18:00": start},
    )
    doc = saint_scan(market, {"family": "SAINT-AMT", "branch": "continuation_retest"})
    assert doc["episodes"], "Asia 19:51 trigger must be visible when search starts at session open"
    assert doc["episodes"][0]["values"]["asia_session"] is True


def test_RR22_single_retest_only():
    doc = saint_scan(
        _saint_market(_continuation_bars(fast=False, second_retest=True)),
        {"family": "SAINT-AMT", "branch": "continuation_retest"},
    )
    longs = [e for e in doc["episodes"] if e["side"] == "long"]
    assert len(longs) == 1


def test_RR22_long_mirror():
    t0 = _t("10:00")
    bars = _fill(START, 2, 150, 151, 149, 150) + _fill(t0, 5, 102, 103, 100, 101, delta=-20) + [
        synth_bar(t0 + 5 * MINUTE, 199, 202, 198, 201, delta=8),
        synth_bar(t0 + 6 * MINUTE, 201, 201, 199.8, 200, delta=-1),
    ]
    doc = saint_scan(_saint_market(bars), {"family": "SAINT-AMT", "branch": "trapped_buyers_retest"})
    longs = [e for e in doc["episodes"] if e["side"] == "long"]
    assert longs


def test_RR22_asia_range_literal():
    rules = saint_scan(_saint_market(_continuation_bars(fast=False)), {"family": "SAINT-AMT", "branch": "continuation_retest"})["rules"]
    asia = next(r for r in rules if r["rule_id"] == "RR-22-asia-range")
    assert "TRAP p.8" in asia["source"]
    assert asia["kind"] == "literal"
    obj = _stage(saint_scan(_saint_market(_continuation_bars(fast=False)), {"family": "SAINT-AMT", "branch": "continuation_retest"})["episodes"][0], "objective")
    assert obj["operands"]["asia_range_claim"] == "150-160"


def _member_market(*, independent=True, after_1245=True, contact_px=D("100.00")):
    prior_t = clock(DAY - timedelta(days=1), "13:10") if after_1245 else clock(DAY - timedelta(days=1), "10:00")
    t = _t("10:05")
    bars = _fill(START, 2, 100, 101, 99, 100) + [
        synth_bar(t, 100.1, 100.5, 99.5, contact_px, delta=-2),
        synth_bar(t + MINUTE, 100, 100.4, 99.4, 99.6, delta=-1),
    ]
    reaction = {"id": "r1", "side": "high", "price": D("100"), "known_at": prior_t, "at": prior_t, "parent": "reaction"}
    hvn = {"id": "h1", "price": D("100.25"), "known_at": prior_t, "parent": "profile"}
    return SynthMarket(
        DAY,
        bars,
        start=START,
        end=END,
        fixtures={
            "reactions": [reaction],
            "hvns": [hvn],
            "independent": independent,
            "rejection_high": D("100.5"),
            "kg1": [],
        },
    )


def test_F15_no_1245_split():
    doc = member_scan(_member_market(after_1245=True), {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    assert doc["episodes"]
    assert doc["episodes"][0]["values"]["split_1245"] is False
    assert _stage(doc["episodes"][0], "context")["operands"]["split_1245"] is False
    assert doc["episodes"][0]["verdict"] in {"pass", "fail"}
    assert _stage(doc["episodes"][0], "trigger")["verdict"] == "pass"


def test_F15_independence_binds_admission():
    ok = member_scan(_member_market(independent=True), {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    bad = member_scan(_member_market(independent=False), {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    assert ok["episodes"][0]["verdict"] == "pass"
    assert bad["episodes"][0]["verdict"] == "fail"
    assert _stage(bad["episodes"][0], "reference")["verdict"] == "fail"


def test_F15_target_1_5R_and_ticket_conflict():
    doc = member_scan(_member_market(), {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    obj = _stage(doc["episodes"][0], "objective")
    assert obj["operands"]["target_r"] == "1.5"
    assert obj["operands"]["conflicting_evidence"] == [{"ticket": "first", "rr": 1.00}, {"ticket": "second", "rr": 9.60}]
    entry = D(str(doc["episodes"][0]["geometry"]["entry"]))
    stop = D(str(doc["episodes"][0]["geometry"]["stop"]))
    target = D(str(doc["episodes"][0]["geometry"]["target"]))
    assert abs(abs(target - entry) - abs(entry - stop) * D("1.5")) < D("0.01")


def test_F15_stop_above_rejection_high():
    doc = member_scan(_member_market(), {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    risk = _stage(doc["episodes"][0], "risk")
    assert D(str(risk["operands"]["stop"])) > D(str(risk["operands"]["rejection_high"]))
    assert doc["episodes"][0]["values"]["stop_above_rejection_high"] is True


def test_F15_fixed_500_risk():
    doc = member_scan(_member_market(), {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    risk = _stage(doc["episodes"][0], "risk")
    assert risk["operands"]["risk_usd"] == "500"
    assert D(str(risk["operands"]["quantity"])) > 0
    assert risk["operands"]["instrument_transfer"] is True


def test_F15_k10_p13_drawn_directions_negative_control():
    from trading_research.research.rule_discovery.source_adapters.member import K10_P13_CAPTION, K10_P13_DRAWN_DIRECTIONS

    assert K10_P13_DRAWN_DIRECTIONS == ("short", "short", "long")
    assert K10_P13_CAPTION == "three shorts"
    t = _t("10:05")
    bars = _fill(START, 2, 100, 101, 99, 100) + [synth_bar(t, 99.8, 100.2, 99.5, 100.0, delta=2)]
    reaction = {
        "id": "demand",
        "side": "low",
        "price": D("100"),
        "known_at": clock(DAY - timedelta(days=1), "13:10"),
        "at": clock(DAY - timedelta(days=1), "13:10"),
        "parent": "reaction",
    }
    hvn = {"id": "h1", "price": D("100.25"), "known_at": reaction["known_at"], "parent": "profile"}
    market = SynthMarket(
        DAY,
        bars,
        start=START,
        end=END,
        fixtures={"reactions": [reaction], "hvns": [hvn], "independent": True, "kg1": []},
    )
    shorts = member_scan(market, {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    longs = member_scan(market, {"family": "MEMBER-TWO-REASONS", "branch": "planned_return_long"})
    assert shorts["episodes"][0]["verdict"] != "pass"
    assert shorts["episodes"][0]["values"]["k10_p13_drawn_directions"] == ["short", "short", "long"]
    assert longs["episodes"][0]["side"] == "long"
    note = next(r for r in shorts["rules"] if r["rule_id"] == "F15-k10-p13-drawn-directions")
    assert "two SELL" in note["notes"]
    assert "BUY" in note["notes"]


def test_RR23_es_tape_required():
    example = {"id": "MB-2026-07-K10", "instrument": "ES-202609", "inside_tape": False, "expected_detection": {"branch": "member two reasons", "side": "short then long"}}
    out = member_replay(SynthMarket(DAY, [], start=START, end=END), example)
    assert out["detected"] is None
    assert out["divergence"] == "ES tape required"


def _keani_bars(*, break_hhmm="11:30", retest_delay_min=5, reward=True, val_rise=False):
    bars = []
    a0 = _t("09:30")
    for i in range(30):
        bars.append(synth_bar(a0 + i * MINUTE, 105, 106, 104, 105.5, delta=1))
    rej = synth_bar(_t("10:05"), 104, 105, 99.75, 104.5, delta=-1)
    bars.append(rej)
    brk_t = _t(break_hhmm)
    bars.append(synth_bar(brk_t, 108, 110, 107, 109.25, delta=6))
    rt = brk_t + retest_delay_min * MINUTE
    bars.append(synth_bar(rt, 108, 108.25, 107.1, 107.5, delta=-1))
    if reward:
        bars.append(synth_bar(rt + MINUTE, 107.5, 109, 107.4, 108.5, delta=3))
    return bars


def _keani_market(bars, extra=None):
    fx = {
        "prior_vah": D("100"),
        "prior_day_high": D("130"),
        "weekly_high": D("140"),
        "a_period": {"low": D("104"), "high": D("106"), "start": _t("09:30"), "end": _t("10:00"), "coverage": {"observed_scope_complete": True}},
        "developing_profile": {"poc": D("103"), "vah": D("108"), "val": D("102")},
        "imbalance_band": [D("107"), D("108")],
        "profile": {"poc": D("103"), "vah": D("108"), "val": D("102"), "rows": [{"price": D("103"), "total_volume": 10}]},
    }
    if extra:
        fx.update(extra)
    return SynthMarket(
        DAY,
        bars,
        start=START,
        end=END,
        fixtures=fx,
        profiles={(_t("09:30"), _t("11:30"), ".70"): fx["developing_profile"]},
        domain={"O109": {"buy_runs": [{"band": [D("107"), D("108")]}]}},
    )


def test_F16_no_1100_cutoff():
    doc = keani_scan(_keani_market(_keani_bars(break_hhmm="11:30")), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    assert doc["episodes"]
    assert _stage(doc["episodes"][0], "trigger")["verdict"] == "pass"
    assert doc["episodes"][0]["values"]["cutoff_1100"] is False


def test_F16_no_60m_retest_expiry():
    doc = keani_scan(_keani_market(_keani_bars(break_hhmm="10:15", retest_delay_min=90)), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    assert doc["episodes"]
    assert _stage(doc["episodes"][0], "confirmation")["operands"]["expiry_60m"] is False
    assert _stage(doc["episodes"][0], "confirmation")["operands"]["retest"] is True


def test_F16_a_period_0930_1000():
    doc = keani_scan(_keani_market(_keani_bars()), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    assert _stage(doc["episodes"][0], "context")["operands"]["a_period"] == "09:30-10:00"
    assert doc.get("a_period") == ["09:30", "10:00"]


def test_F16_no_developing_val_rise():
    doc = keani_scan(_keani_market(_keani_bars()), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    loc = _stage(doc["episodes"][0], "location")
    assert loc["operands"]["val_rise_required"] is False
    assert loc["verdict"] == "pass"


def test_F16_htf_objective_not_a_width():
    doc = keani_scan(_keani_market(_keani_bars()), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    obj = _stage(doc["episodes"][0], "objective")
    assert obj["operands"]["a_high_plus_a_width"] is False
    assert obj["operands"]["selector"] in {"prior_day_high", "prior_vah", "weekly_high"}
    assert obj["operands"]["selector"] == "prior_day_high"
    assert D(str(obj["operands"]["target"])) == D("130")


def test_F16_p21_or_p22_and_unresolved():
    doc = keani_scan(_keani_market(_keani_bars()), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    rule = next(r for r in doc["rules"] if r["rule_id"] == "F16-rejection-poc-or-prior-vah")
    assert "unresolved" in rule
    assert "AND" in rule["unresolved"]
    assert "OR" in rule["unresolved"]
    loc = _stage(doc["episodes"][0], "location")
    assert loc["operands"]["poc_or_prior_vah"] == "OR"
    assert loc["operands"]["p22_and_unresolved"] is True


def test_F16_three_tick_reward():
    yes = keani_scan(_keani_market(_keani_bars(reward=True)), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    no = keani_scan(_keani_market(_keani_bars(reward=False)), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    assert _stage(yes["episodes"][0], "confirmation")["operands"]["three_tick_reward"] is True
    assert _stage(yes["episodes"][0], "confirmation")["verdict"] == "pass"
    assert _stage(no["episodes"][0], "confirmation")["operands"]["three_tick_reward"] is False
    assert _stage(no["episodes"][0], "confirmation")["verdict"] == "fail"


def test_true_break_ignores_already_beyond_interior_level():
    t0 = _t("10:00")
    bars = _fill(START, 2, 190, 191, 189, 190) + _fill(t0, 5, 199, 200, 198.75, 199.25, delta=1) + [
        synth_bar(t0 + 5 * MINUTE, 199.5, 202, 199, 201.5, delta=5),
        synth_bar(t0 + 6 * MINUTE, 201, 201.25, 199.75, 200, delta=-1),
    ]
    market = _saint_market(bars, extra_fx={"intraday_levels": [D("180")]})
    doc = saint_scan(market, {"family": "SAINT-AMT", "branch": "continuation_retest"})
    longs = [e for e in doc["episodes"] if e["side"] == "long"]
    assert longs
    levels = [D(str((e.get("geometry") or {}).get("break_level"))) for e in longs]
    assert D("200") in levels
    assert D("180") not in levels


def test_htf_control_window_not_inverted():
    t0 = _t("09:50")
    bars = _continuation_bars(fast=False)
    market = _saint_market(bars)
    market.b02_fixtures["balance"]["start"] = t0 + 20 * MINUTE
    market.b02_fixtures["htf_control"] = None
    doc = saint_scan(market, {"family": "SAINT-AMT", "branch": "continuation_retest"})
    assert doc["episodes"]
    conf = _stage(doc["episodes"][0], "confirmation")
    assert conf["operands"]["htf_control"] in {"up", "down"}
    assert conf["operands"]["alignment_ok"] is not None


def test_F10_missing_confirm_at_is_unknown():
    t0 = _t("09:50")
    bars = _fill(START, 2, 150, 151, 149, 150) + _fill(t0, 5, 199, 200, 198.75, 199.25, delta=1) + [
        synth_bar(t0 + 5 * MINUTE, 199.5, 202, 199, 201.5, delta=5),
    ]
    doc = saint_scan(_saint_market(bars), {"family": "SAINT-AMT", "branch": "continuation_retest"})
    assert doc["episodes"]
    conf = _stage(doc["episodes"][0], "confirmation")
    assert conf["operands"]["confirm_at"] is None
    assert conf["operands"]["retest"] is False
    assert conf["verdict"] == "unknown"
    assert doc["episodes"][0]["verdict"] != "pass"


def test_poc_held_retest_can_fail():
    t0 = _t("10:00")
    bars = _fill(START, 2, 150, 151, 149, 150) + [
        synth_bar(t0, 150, 160, 150, 158, delta=10),
        synth_bar(t0 + MINUTE, 157, 158, 149.75, 148, delta=-4),
    ]
    doc = saint_scan(_saint_market(bars), {"family": "SAINT-AMT", "branch": "poc_traversal"})
    assert doc["episodes"]
    conf = _stage(doc["episodes"][0], "confirmation")
    assert conf is not None
    assert conf["operands"].get("held_retest") is False or conf["verdict"] != "pass"
    assert doc["episodes"][0]["verdict"] != "pass" or conf["operands"].get("held_retest") is False


def test_failed_auction_drive_without_return_fails_confirmation():
    t0 = _t("10:00")
    bars = _fill(START, 2, 150, 151, 149, 150) + [
        synth_bar(t0, 99, 100, 80, 85, delta=-5),
        synth_bar(t0 + MINUTE, 86, 90, 82, 88, delta=-1),
        synth_bar(t0 + 2 * MINUTE, 84, 86, 82, 83, delta=-2),
    ]
    doc = saint_scan(
        _saint_market(bars, extra_fx={"prior_va": {"val": D("80"), "vah": D("95")}}),
        {"family": "SAINT-AMT", "branch": "failed_auction_return"},
    )
    shorts = [e for e in doc["episodes"] if e["side"] == "short"]
    assert shorts
    conf = _stage(shorts[0], "confirmation")
    assert conf["operands"]["return"] is False
    assert conf["verdict"] != "pass"
    assert shorts[0]["verdict"] != "pass"


def test_member_touch_without_reaction_fails_trigger():
    prior_t = clock(DAY - timedelta(days=1), "13:10")
    t = _t("10:05")
    bars = _fill(START, 2, 100, 101, 99, 100) + [
        synth_bar(t, 100.0, 100.1, 99.95, 100.05, delta=0),
        synth_bar(t + MINUTE, 100.05, 100.15, 100.0, 100.1, delta=0),
    ]
    reaction = {"id": "r1", "side": "high", "price": D("100"), "known_at": prior_t, "at": prior_t, "parent": "reaction"}
    hvn = {"id": "h1", "price": D("100.25"), "known_at": prior_t, "parent": "profile"}
    market = SynthMarket(
        DAY,
        bars,
        start=START,
        end=END,
        fixtures={"reactions": [reaction], "hvns": [hvn], "independent": True, "kg1": []},
    )
    doc = member_scan(market, {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    assert doc["episodes"]
    trig = _stage(doc["episodes"][0], "trigger")
    assert trig["operands"]["reaction"] is False
    assert trig["verdict"] == "fail"
    assert doc["episodes"][0]["verdict"] != "pass"


def test_member_reaction_not_held_fails_confirmation():
    market = _member_market()
    market.b02_fixtures["held"] = False
    doc = member_scan(market, {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})
    assert _stage(doc["episodes"][0], "trigger")["verdict"] == "pass"
    conf = _stage(doc["episodes"][0], "confirmation")
    assert conf["operands"]["held"] is False
    assert conf["verdict"] == "fail"
    assert doc["episodes"][0]["verdict"] != "pass"


def test_keani_a_low_equal_vah_not_fully_above():
    bars = _keani_bars()
    market = _keani_market(bars, extra={"prior_vah": D("104"), "a_period": {"low": D("104"), "high": D("106"), "start": _t("09:30"), "end": _t("10:00")}})
    doc = keani_scan(market, {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})
    ctx = _stage(doc["episodes"][0], "context")
    assert ctx["operands"]["strict_gt"] is True
    assert ctx["operands"]["fully_above"] is False
    assert ctx["verdict"] == "fail"
    assert doc["episodes"][0]["verdict"] != "pass"


def test_b0_b01_byte_identity():
    hashes = json.loads((TRACK_DIR / "B0_B01_HASHES.json").read_text())
    gz = json.loads((TRACK_DIR / "B0_B01_GZ_HASHES.json").read_text())
    market_by_day = {}
    after = []
    for row in hashes["rows"]:
        day = row["date"]
        if day not in market_by_day:
            market_by_day[day] = load_source_market(day)
        dual = dual_scan(market_by_day[day], row["family"], row["branch"])
        b0 = sha256_json(dual["b0"])
        b01 = sha256_json(dual["b01"])
        assert b0 == row["b0_sha256"], (row["date"], row["family"], row["branch"], "b0")
        assert b01 == row["b01_sha256"], (row["date"], row["family"], row["branch"], "b01")
        after.append({**row, "b0_after": b0, "b01_after": b01})
    for row in gz["rows"]:
        assert sha256_file(Path(row["b0_gz"])) == row["b0_gz_sha256"]
        assert sha256_file(Path(row["b01_gz"])) == row["b01_gz_sha256"]
    write_json(WORK_DIR / "B0_B01_HASHES_AFTER.json", {"rows": after})


def test_RR22_replay_does_not_mutate_market_fixtures():
    market = _saint_market(_continuation_bars(fast=False))
    before = dict(market.b02_fixtures)
    example = {
        "id": "local-inject",
        "date": "2026-01-15",
        "levels": {"balance": [29600, 29960], "intraday_levels": [29740]},
        "actions": [{"action": "sell", "price": 201.5}],
        "expected_detection": {"branch": "continuation_retest", "side": "long"},
    }
    saint_replay(market, example)
    assert market.b02_fixtures == before


def test_replay_writes():
    examples = json.loads(AUTHOR_EXAMPLES.read_text())["examples"]
    saint_rows = [row for row in examples if row.get("family") == "SAINT-AMT"]
    member_rows = [row for row in examples if row.get("family") == "MEMBER-TWO-REASONS"]
    saint_out = []
    loaded = {}
    for example in saint_rows:
        if outside_native_tape(example):
            result = saint_replay(None, example)
            result["id"] = example["id"]
            assert result["detected"] is None
            assert result["divergence"] == "date outside the tape"
            saint_out.append(result)
            continue
        day = account_day_for_example(example) or str(example.get("date"))
        try:
            if day not in loaded:
                loaded[day] = load_source_market(day)
            market = loaded[day]
            before_fx = getattr(market, "b02_fixtures", None)
            result = saint_replay(market, example)
            after_fx = getattr(market, "b02_fixtures", None)
            assert after_fx == before_fx
        except Exception as exc:
            result = {
                "detected": None,
                "branch": (example.get("expected_detection") or {}).get("branch"),
                "our_side": None,
                "our_level": None,
                "our_entry_ns": None,
                "author_level": None,
                "author_side": (example.get("expected_detection") or {}).get("side"),
                "divergence": f"date outside the tape: {exc}",
                "reached_location": False,
                "failing_operand": None,
            }
        result["id"] = example["id"]
        assert "detected" in result
        assert result["detected"] in {True, False, None}
        assert isinstance(result.get("reached_location"), bool)
        if result["detected"] is False:
            assert result.get("failing_operand")
        saint_out.append(result)
    member_out = []
    for example in member_rows:
        result = member_replay(None, example)
        result["id"] = example["id"]
        assert result["detected"] is None
        assert result["divergence"] == "ES tape required"
        member_out.append(result)
    write_json(
        WORK_DIR / "REPLAY_SAINT.json",
        {
            "family": "SAINT-AMT",
            "produced_by": {
                "test": "test_replay_writes",
                "command": "replay_example(load_source_market(example['date']), example)",
                "dates": sorted(loaded),
                "fixture_injection": "FixtureMarket overlay, inner market.b02_fixtures unchanged",
            },
            "examples": saint_out,
        },
    )
    write_json(WORK_DIR / "REPLAY_MEMBER.json", {"family": "MEMBER-TWO-REASONS", "examples": member_out})


def test_funnel_and_statistics_slice():
    from trading_research.research.rule_discovery.source_adapters.common import population_counts

    saint_docs = []
    member_docs = []
    keani_docs = []
    b01_saint = {}
    b01_member = {}
    b01_keani = {}
    poc_n = 0
    poc_hit = 0
    asia_ranges = []
    for day in SLICE_DATES:
        if not native_calendar_day(day):
            continue
        try:
            market = load_source_market(day)
        except Exception as exc:
            saint_docs.append({"branch": "load_error", "episodes": [], "error": str(exc)})
            continue
        for branch in ("continuation_retest", "trapped_buyers_retest", "failed_auction_return", "poc_traversal"):
            doc = saint_scan(market, {"family": "SAINT-AMT", "branch": branch})
            saint_docs.append(doc)
            dual = dual_scan(market, "SAINT-AMT", branch)
            counts = population_counts(dual["b01"])
            b01_saint[branch] = b01_saint.get(branch) or {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0}
            b01_saint[branch]["episodes"] += counts["episodes"]
            b01_saint[branch]["pass"] += counts.get("setup", 0)
            b01_saint[branch]["fail"] += counts.get("no_setup", 0) + counts.get("rejected", 0)
            b01_saint[branch]["unknown"] += counts.get("unknown", 0)
            if branch == "poc_traversal":
                for ep in doc.get("episodes") or []:
                    if (ep.get("values") or {}).get("poc_tell") == "aggressive_through_held_retest":
                        poc_n += 1
                        target = (ep.get("geometry") or {}).get("target")
                        entry = (ep.get("geometry") or {}).get("entry")
                        if target is not None and entry is not None:
                            later = market.bars(int(ep["decision_at"]), int(market.end))
                            if any(r.get("H") is not None and D(str(r["H"])) >= D(str(target)) for r in later):
                                poc_hit += 1
        for branch in ("resistance_short", "planned_return_long"):
            member_docs.append(member_scan(market, {"family": "MEMBER-TWO-REASONS", "branch": branch}))
            dual = dual_scan(market, "MEMBER-TWO-REASONS", branch)
            counts = population_counts(dual["b01"])
            b01_member[branch] = b01_member.get(branch) or {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0}
            b01_member[branch]["episodes"] += counts["episodes"]
            b01_member[branch]["pass"] += counts.get("setup", 0)
            b01_member[branch]["fail"] += counts.get("no_setup", 0) + counts.get("rejected", 0)
            b01_member[branch]["unknown"] += counts.get("unknown", 0)
        keani_docs.append(keani_scan(market, {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"}))
        dual = dual_scan(market, "KEANI-OPEN-ABOVE-VALUE", "source_long")
        counts = population_counts(dual["b01"])
        b01_keani["source_long"] = b01_keani.get("source_long") or {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0}
        b01_keani["source_long"]["episodes"] += counts["episodes"]
        b01_keani["source_long"]["pass"] += counts.get("setup", 0)
        b01_keani["source_long"]["fail"] += counts.get("no_setup", 0) + counts.get("rejected", 0)
        b01_keani["source_long"]["unknown"] += counts.get("unknown", 0)
        try:
            asia_end = market.at("03:00")
            asia_bars = market.bars(market.start, asia_end)
            if asia_bars:
                hi = max(D(str(r["H"])) for r in asia_bars if r.get("H") is not None)
                lo = min(D(str(r["L"])) for r in asia_bars if r.get("L") is not None)
                asia_ranges.append({"date": day, "width": float(hi - lo)})
        except Exception:
            pass

    def pack(family, docs, b01):
        b02 = funnel_counts(docs)
        return {
            "family": family,
            "slice_dates": SLICE_DATES,
            "B0.1": b01,
            "B0.2": b02,
            "fully_above_a_eligible": sum(int(d.get("fully_above_a_eligible") or 0) for d in docs) if family.startswith("KEANI") else None,
        }

    write_json(WORK_DIR / "FUNNEL_SAINT-AMT.json", pack("SAINT-AMT", saint_docs, b01_saint))
    write_json(WORK_DIR / "FUNNEL_MEMBER-TWO-REASONS.json", pack("MEMBER-TWO-REASONS", member_docs, b01_member))
    write_json(WORK_DIR / "FUNNEL_KEANI-OPEN-ABOVE-VALUE.json", pack("KEANI-OPEN-ABOVE-VALUE", keani_docs, b01_keani))
    widths = [row["width"] for row in asia_ranges]
    in_band = [w for w in widths if 150 <= w <= 160]
    write_json(
        WORK_DIR / "STATISTICS_SAINT.json",
        {
            "poc_traverse_80": {
                "source": "AMTL p.9",
                "source_figure": 0.80,
                "slice_n": poc_n,
                "slice_hits": poc_hit,
                "slice_rate": (poc_hit / poc_n) if poc_n else None,
                "definition": "after aggressive POC push with held retest, later high reaches VAH before session end",
            },
            "asia_range": {
                "source": "TRAP p.8",
                "source_figure": [150, 160],
                "source_claim_session": "Asia session (TRAP p.8)",
                "window": "market.start (prior-day 18:00 ET) through 03:00 ET, the whole overnight, not the Asia session box",
                "slice_n": len(widths),
                "median_range": sorted(widths)[len(widths) // 2] if widths else None,
                "fraction_in_150_160": (len(in_band) / len(widths)) if widths else None,
                "per_date": asia_ranges,
            },
        },
    )
    write_json(WORK_DIR / "RULES_SAINT-AMT.json", {"family": "SAINT-AMT", "rules": saint_scan(_saint_market(_continuation_bars(fast=False)), {"family": "SAINT-AMT", "branch": "continuation_retest"})["rules"]})
    write_json(WORK_DIR / "RULES_MEMBER-TWO-REASONS.json", {"family": "MEMBER-TWO-REASONS", "rules": member_scan(_member_market(), {"family": "MEMBER-TWO-REASONS", "branch": "resistance_short"})["rules"]})
    write_json(WORK_DIR / "RULES_KEANI.json", {"family": "KEANI-OPEN-ABOVE-VALUE", "rules": keani_scan(_keani_market(_keani_bars()), {"family": "KEANI-OPEN-ABOVE-VALUE", "branch": "source_long"})["rules"]})
    assert (WORK_DIR / "FUNNEL_SAINT-AMT.json").is_file()
    assert (WORK_DIR / "STATISTICS_SAINT.json").is_file()
    from trading_research.research.rule_discovery.source_adapters.b02_saint_track import STAGE_ORDER

    for path in (
        WORK_DIR / "FUNNEL_SAINT-AMT.json",
        WORK_DIR / "FUNNEL_MEMBER-TWO-REASONS.json",
        WORK_DIR / "FUNNEL_KEANI-OPEN-ABOVE-VALUE.json",
    ):
        payload = json.loads(path.read_text())
        for branch, row in payload["B0.2"].items():
            last = None
            for name in STAGE_ORDER:
                st = row["stages"][name]
                if st["pass"] or st["fail"] or st["unknown"]:
                    last = name
            if last is None:
                continue
            assert row["pass"] <= row["stages"][last]["pass"], (path.name, branch, last, row["pass"], row["stages"][last])


def test_round1_track_files_byte_identical():
    for name, expected in TRACK_SHA256.items():
        actual = sha256_file(TRACK_DIR / name)
        assert actual == expected, (name, actual, expected)
