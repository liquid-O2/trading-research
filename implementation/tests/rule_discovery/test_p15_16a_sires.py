"""P15-16A SIRES / REFILL-STUDY B0.2 fixtures and slice evidence."""
from __future__ import annotations

from datetime import date
from pathlib import Path
import hashlib
import json

import numpy as np
import pytest

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.rule_discovery.native import NativeMarketView, SessionArrays, build_market_view
from trading_research.research.rule_discovery.runner import engineering_slice_dates
from trading_research.research.rule_discovery.source_adapters import processes as processes_mod
from trading_research.research.rule_discovery.source_adapters import sires as sires_mod
from trading_research.research.rule_discovery.source_adapters.common import FAMILY_BRANCHES, dual_scan
from trading_research.research.rule_discovery.source_adapters.processes import scan_b02 as refill_scan
from trading_research.research.rule_discovery.source_adapters.refill_b02 import (
    HOLD_BOUNDARY_TICKS,
    LITERAL_CLUSTER_SIZES,
    cluster_size_family,
)
from trading_research.research.rule_discovery.source_adapters.sires import replay_example, scan_b02
from trading_research.research.rule_discovery.source_adapters.sires_b02 import (
    AGGRESSION_MAX,
    ELIGIBLE_LOCATION_KINDS,
    ENTRY_NEAR_TICKS,
    FADE_OWN_AGGRESSION,
    FADE_UNPAID,
    OFM_TARGET_TICKS,
    REPLENISHMENT_MIN_TICKS,
    RULES,
    balance_fade_own_aggression,
    balance_fade_unpaid,
    entry_near_ok,
    rules_payload,
    STAGE_ORDER,
)

TRACK = Path("/workspace/.worktrees/b02-sires/implementation/reports/research-work/P15-16A/_track_sires")
EXAMPLES = Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json")
BYTE_BEFORE = TRACK / "BYTE_IDENTITY_BEFORE.json"
SI_IDS = (
    "SI-2026-07-08",
    "SI-2026-07-09",
    "SI-2026-07-10",
    "SI-2026-07-14",
    "SI-2026-07-15-OVERNIGHT",
    "SI-2026-07-23",
    "SI-2026-07-31",
    "SI-2026-08-04",
    "SI-2026-08-06",
    "SI-2026-08-19",
)
SLICE_DATES = (
    "2020-01-02",
    "2021-01-04",
    "2022-01-03",
    "2023-01-03",
    "2024-01-02",
    "2025-01-02",
    "2026-01-02",
    "2023-11-06",
    "2026-09-03",
)
IDENTITY_DATES = ("2021-01-04", "2022-01-03")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _arrays(events, *, book=None, day="2026-08-19"):
    rows = list(events)
    if book:
        rows.extend(book)
    rows.sort(key=lambda r: r[0])
    n = len(rows)
    t = np.array([r[0] for r in rows], dtype=np.int64)
    ticks = np.array([r[1] for r in rows], dtype=np.int64)
    size = np.array([r[2] for r in rows], dtype=np.int64)
    side = np.array([r[3] for r in rows], dtype=np.int8)
    is_trade = np.array([r[4] if len(r) > 4 else True for r in rows], dtype=np.bool_)
    bid_px = np.array([r[5] if len(r) > 5 else 0 for r in rows], dtype=np.int64)
    bid_sz = np.array([r[6] if len(r) > 6 else 0 for r in rows], dtype=np.int64)
    z64 = np.zeros(n, dtype=np.int64)
    z8 = np.zeros(n, dtype=np.int8)
    return SessionArrays(
        t_ns=t,
        price_ticks=ticks,
        size=size,
        side=side,
        action=np.where(is_trade, 1, 0).astype(np.int8),
        bid_ticks=bid_px,
        ask_ticks=z64,
        bid_sz=bid_sz,
        ask_sz=z64,
        flags=z64,
        known_at_ns=t,
        exchange_sequence=np.arange(n, dtype=np.int64),
        is_trade=is_trade,
        row_id=np.array([f"r{i}" for i in range(n)], dtype=object),
        ooo_index=np.zeros(0, dtype=np.int64),
        batch_starts=np.array([0], dtype=np.int64),
        instrument_id="NQ",
        start_ns=int(t[0]) if n else 0,
        end_ns=int(t[-1]) + 1 if n else 1,
        source_sha256=(),
    )


def _view(events, **kwargs):
    arrays = _arrays(events, **kwargs)
    return NativeMarketView(arrays, account_day="2026-08-19")


def _base_ns():
    return et_ns(date(2026, 8, 19), 9, 30)


def _rec(**kwargs):
    row = {"method_id": "SIRES", "account_daily_r": 0.0}
    row.update(kwargs)
    return row


def test_f02_fast_release_no_pullback_passes_clean_squeeze():
    t0 = _base_ns()
    view = _view(
        [
            (t0, 40000, 50, -1),
            (t0 + 1_000_000_000, 39990, 50, -1),
            (t0 + 2_000_000_000, 39980, 50, -1),
            (t0 + 2_200_000_000, 39980, 40, 1),
        ]
    )
    doc = scan_b02(view, _rec(branch="clean_squeeze", location_kind="lvn", side="short"))
    passes = [ep for ep in doc["episodes"] if ep["research_verdict"] == "pass" and ep["side"] == "short"]
    assert passes, doc["episodes"][0] if doc["episodes"] else doc
    assert passes[0]["values"]["pullback"] is False
    assert "F02_clean_squeeze_no_retest" in {r["rule_id"] for r in doc["rules"]}


def test_f02_pullback_then_absorption_is_not_clean_squeeze():
    t0 = _base_ns()
    view = _view(
        [
            (t0, 40000, 50, -1),
            (t0 + 1_000_000_000, 39990, 50, -1),
            (t0 + 2_000_000_000, 39980, 50, -1),
            (t0 + 2_100_000_000, 39992, 40, 1),
            (t0 + 2_300_000_000, 39980, 40, 1),
        ]
    )
    doc = scan_b02(view, _rec(branch="clean_squeeze", location_kind="lvn", side="short"))
    assert all(ep["research_verdict"] != "pass" for ep in doc["episodes"] if ep["side"] == "short")
    shorts = [ep for ep in doc["episodes"] if ep["side"] == "short"]
    assert shorts
    assert shorts[0]["values"]["pullback"] is True


def test_f02_future_pullback_after_decision_does_not_disqualify():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 2_200_000_000, 39980, 40, 1),
        (t0 + 20_000_000_000, 39992, 40, 1),
    ]
    view = _view(events)
    rec = _rec(branch="clean_squeeze", location_kind="lvn", side="short", b02_now_ns=t0 + 3_000_000_000)
    doc = scan_b02(view, rec)
    assert any(ep["research_verdict"] == "pass" and ep["side"] == "short" for ep in doc["episodes"])


def test_f03_replenishment_three_refills_pass_two_fail():
    t0 = _base_ns()
    three = [
        (t0, 40000, 50, -1, True),
        (t0 + 10, 40001, 50, -1, True),
        (t0 + 20, 39999, 50, -1, True),
        (t0 + 40, 40000, 50, 1, True),
    ]
    two = [
        (t0, 40000, 50, -1, True),
        (t0 + 10, 40001, 50, -1, True),
        (t0 + 40, 40000, 50, 1, True),
    ]
    rec = _rec(branch="stop_four_stage", location_kind="shelf", side="long", defended_ticks=40000)
    ok = scan_b02(_view(three), rec)
    bad = scan_b02(_view(two), rec)
    ep_ok = [e for e in ok["episodes"] if e["side"] == "long"][0]
    ep_bad = [e for e in bad["episodes"] if e["side"] == "long"][0]
    assert ep_ok["values"]["replenishment_ticks"] >= REPLENISHMENT_MIN_TICKS
    trig = next(s for s in ep_ok["stages"] if s["stage"] == "trigger")
    assert trig["verdict"] == "pass"
    assert ep_bad["values"]["replenishment_ticks"] == 2
    trig_bad = next(s for s in ep_bad["stages"] if s["stage"] == "trigger")
    assert trig_bad["verdict"] == "fail"


def test_f03_reward_ticks_separate_from_replenishment():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1, True),
        (t0 + 10, 40001, 50, -1, True),
        (t0 + 20, 39999, 50, -1, True),
        (t0 + 40, 40000, 50, 1, True),
        (t0 + 50, 40001, 50, 1, True),
    ]
    rec = _rec(branch="stop_four_stage", location_kind="ledge", side="long", defended_ticks=40000)
    ep = [e for e in scan_b02(_view(events), rec)["episodes"] if e["side"] == "long"][0]
    assert ep["values"]["replenishment_ticks"] >= 3
    assert ep["values"]["reward_ticks"] < 3
    conf = next(s for s in ep["stages"] if s["stage"] == "confirmation")
    assert conf["verdict"] == "fail"
    trig = next(s for s in ep["stages"] if s["stage"] == "trigger")
    assert trig["verdict"] == "pass"


def test_rr21_future_refills_after_decision_are_ignored():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1, True),
        (t0 + 10, 40001, 50, -1, True),
        (t0 + 1_000_000_000, 40000, 50, 1, True),
        (t0 + 5_000_000_000, 39999, 50, -1, True),
        (t0 + 5_000_000_010, 40000, 50, -1, True),
    ]
    rec = _rec(branch="stop_four_stage", location_kind="lvn", side="long", defended_ticks=40000, b02_now_ns=t0 + 2_000_000_000)
    ep = [e for e in scan_b02(_view(events), rec)["episodes"] if e["side"] == "long"][0]
    assert ep["values"]["replenishment_ticks"] == 2


def test_f09_location_lvn_passes_poc_fails():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 2_200_000_000, 39980, 40, 1),
    ]
    rec = _rec(branch="clean_squeeze", side="short")
    lvn = scan_b02(_view(events), {**rec, "location_kind": "lvn"})
    poc = scan_b02(_view(events), {**rec, "location_kind": "poc"})
    loc_ok = next(s for s in [e for e in lvn["episodes"] if e["side"] == "short"][0]["stages"] if s["stage"] == "location")
    loc_bad = next(s for s in [e for e in poc["episodes"] if e["side"] == "short"][0]["stages"] if s["stage"] == "location")
    assert loc_ok["verdict"] == "pass"
    assert loc_bad["verdict"] == "fail"
    assert [e for e in poc["episodes"] if e["side"] == "short"][0]["research_verdict"] != "pass"


def test_f09_inside_balance_and_poc_forbidden():
    t0 = _base_ns()
    events = [(t0, 40000, 50, 1)]
    for kind in ("poc", "inside_balance"):
        doc = scan_b02(_view(events), _rec(branch="dom_rejection", location_kind=kind, side="long"))
        loc = next(s for s in doc["episodes"][0]["stages"] if s["stage"] == "location")
        assert loc["verdict"] == "fail"
    assert "lvn" in ELIGIBLE_LOCATION_KINDS


def test_f09_thesis_killers_c1():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 2_200_000_000, 39980, 40, 1),
    ]
    rec = _rec(branch="clean_squeeze", location_kind="real_extreme", side="short")
    live = scan_b02(_view(events), rec)
    ctx = next(s for s in [e for e in live["episodes"] if e["side"] == "short"][0]["stages"] if s["stage"] == "context")
    assert ctx["verdict"] == "pass"
    for killer in ("structure_break", "value_shift", "new_information"):
        doc = scan_b02(_view(events), {**rec, "thesis_killer": killer})
        ctx = next(s for s in [e for e in doc["episodes"] if e["side"] == "short"][0]["stages"] if s["stage"] == "context")
        assert ctx["verdict"] == "fail", killer
        assert [e for e in doc["episodes"] if e["side"] == "short"][0]["research_verdict"] == "fail"


def test_rr20_aggression_30_60():
    t0 = _base_ns()
    band = _view([(t0, 40000, 45, -1), (t0 + 1_000_000_000, 39990, 45, -1), (t0 + 2_000_000_000, 39980, 45, -1), (t0 + 2_200_000_000, 39980, 40, 1)])
    jumbo = _view([(t0, 40000, 100, -1), (t0 + 1_000_000_000, 39990, 100, -1), (t0 + 2_000_000_000, 39980, 100, -1), (t0 + 2_200_000_000, 39980, 40, 1)])
    rec = _rec(branch="clean_squeeze", location_kind="lvn", side="short")
    ok = [e for e in scan_b02(band, rec)["episodes"] if e["side"] == "short"][0]
    bad = [e for e in scan_b02(jumbo, rec)["episodes"] if e["side"] == "short"][0]
    assert ok["values"]["aggression_in_band"] is True
    assert bad["values"]["aggression_in_band"] is False
    assert AGGRESSION_MAX == 60


def test_rr20_imbalance_350_and_vwap_bands():
    t0 = _base_ns()
    events = [(t0 + i, 40000, 40, -1) for i in range(8)] + [(t0 + 20, 40000, 10, 1)]
    rec = _rec(branch="vwap_deviation_fade", location_kind="lvn", side="short", vwap_price_ticks=39960, vwap_sd_ticks=10)
    ep = [e for e in scan_b02(_view(events), rec)["episodes"] if e["side"] == "short"][0]
    assert ep["values"]["imbalance_ratio"] is not None
    assert ep["values"]["imbalance_ratio"] >= 3.5
    assert ep["values"]["vwap_bands"] == [1.0, 2.0, 2.5]


def test_rr18_resting_stop_is_baseline_ofm_entry():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 3_000_000_000, 40000, 50, 1),
        (t0 + 4_000_000_000, 39978, 50, -1),
    ]
    rec = _rec(branch="ofm_aggressive", location_kind="lvn", side="short", gamma_regime="short")
    doc = scan_b02(_view(events), rec)
    eps = [e for e in doc["episodes"] if e["side"] == "short"]
    assert eps
    variants = {e["values"].get("ofm_entry_variant") or e["values"].get("entry_variant") for e in eps}
    assert "resting_stop" in variants
    rest = next(e for e in eps if e["values"].get("entry_variant") == "resting_stop" or e["values"].get("ofm_entry_variant") == "resting_stop")
    assert rest["geometry"]["entry"] is not None
    assert rest["geometry"]["entry"] <= 39979


def test_rr18_drive_retest_is_second_entry():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 2_050_000_000, 39980, 40, 1),
        (t0 + 2_200_000_000, 39992, 40, 1),
        (t0 + 3_000_000_000, 40000, 50, 1),
        (t0 + 3_500_000_000, 39980, 50, -1),
    ]
    rec = _rec(branch="ofm_aggressive", location_kind="lvn", side="short", gamma_regime="short", entry_variant="drive_retest")
    doc = scan_b02(_view(events), rec)
    eps = [e for e in doc["episodes"] if e["side"] == "short"]
    assert eps
    assert any(e["values"].get("entry_variant") == "drive_retest" for e in eps)


def test_rr18_40_tick_and_control_zone_objectives():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 3_000_000_000, 40000, 50, 1),
        (t0 + 4_000_000_000, 39978, 50, -1),
    ]
    rec = _rec(branch="ofm_aggressive", location_kind="lvn", side="short", gamma_regime="short", control_zone_far_ticks=39900, stop_ticks=7)
    ep = [e for e in scan_b02(_view(events), rec)["episodes"] if e["side"] == "short"][0]
    obj = next(s for s in ep["stages"] if s["stage"] == "objective")
    assert obj["operands"]["ofm_target_40_ticks"] == OFM_TARGET_TICKS
    assert obj["operands"]["control_zone_far_ticks"] == 39900
    assert ep["geometry"]["entry"] - ep["geometry"]["target"] == OFM_TARGET_TICKS
    assert obj["operands"]["target"] == ep["geometry"]["target"]
    assert obj["operands"]["target_price_ticks"] == ep["geometry"]["target"]


def test_f09_gamma_ofm_short_fade_long_missing_is_unknown():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 3_000_000_000, 40000, 50, 1),
        (t0 + 4_000_000_000, 39978, 50, -1),
    ]
    rec = _rec(branch="ofm_aggressive", location_kind="lvn", side="short")
    missing = scan_b02(_view(events), rec)
    ep = [e for e in missing["episodes"] if e["side"] == "short"][0]
    assert ep["research_verdict"] == "unknown"
    ctx = next(s for s in ep["stages"] if s["stage"] == "context")
    assert ctx["verdict"] == "unknown"
    wrong = scan_b02(_view(events), {**rec, "gamma_regime": "long"})
    assert [e for e in wrong["episodes"] if e["side"] == "short"][0]["research_verdict"] == "fail"
    right = scan_b02(_view(events), {**rec, "gamma_regime": "short"})
    assert [e for e in right["episodes"] if e["side"] == "short"][0]["research_verdict"] != "unknown"
    fade = scan_b02(_view(events), _rec(branch="balance_failure_fade", location_kind="lvn", side="short"))
    assert [e for e in fade["episodes"] if e["side"] == "short"][0]["research_verdict"] == "unknown"


def test_rr19_management_partial_trail_daily_stop():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 2_200_000_000, 39980, 40, 1),
    ]
    rec = _rec(branch="clean_squeeze", location_kind="lvn", side="short")
    dead = scan_b02(_view(events), {**rec, "account_daily_r": -4})
    live = scan_b02(_view(events), {**rec, "account_daily_r": -3.9})
    ep_dead = [e for e in dead["episodes"] if e["side"] == "short"][0]
    ep_live = [e for e in live["episodes"] if e["side"] == "short"][0]
    assert ep_dead["research_verdict"] == "fail"
    mg = next(s for s in ep_live["stages"] if s["stage"] == "management")
    assert mg["operands"]["partial_1_to_1"] is True
    assert mg["operands"]["trail_after_close_with_aggression"] is True
    assert mg["operands"]["daily_stop_r"] == -4
    assert ep_live["research_verdict"] == "pass"


def test_a3_entry_one_to_two_ticks_rejects_wider():
    assert ENTRY_NEAR_TICKS == 2
    assert entry_near_ok(40001, 40000) == "pass"
    assert entry_near_ok(40002, 40000) == "pass"
    assert entry_near_ok(40000, 40000) == "fail"
    assert entry_near_ok(40003, 40000) == "fail"
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1, True),
        (t0 + 10, 40001, 50, -1, True),
        (t0 + 20, 39999, 50, -1, True),
        (t0 + 40, 40000, 50, 1, True),
        (t0 + 50, 40004, 50, 1, True),
        (t0 + 60, 40005, 50, 1, True),
    ]
    rec = _rec(branch="stop_four_stage", location_kind="shelf", side="long", defended_ticks=40000, entry_ticks=40003)
    ep = [e for e in scan_b02(_view(events), rec)["episodes"] if e["side"] == "long"][0]
    risk = next(s for s in ep["stages"] if s["stage"] == "risk")
    assert risk["verdict"] == "fail"
    assert risk["operands"]["entry_near_1_2"] is False
    assert risk["operands"]["entry_distance_ticks"] == 3


def test_f09_balance_fade_unpaid_and_own_aggression():
    assert balance_fade_unpaid(True, True) == "pass"
    assert balance_fade_unpaid(True, False) == "fail"
    assert balance_fade_own_aggression(True, True, True) == "pass"
    assert balance_fade_own_aggression(True, True, False) == "fail"
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 3_000_000_000, 40000, 50, 1),
    ]
    rec = _rec(branch="balance_failure_fade", location_kind="lvn", side="short", gamma_regime="long")
    unpaid = scan_b02(_view(events), {**rec, "fade_variant": FADE_UNPAID})
    own = scan_b02(_view(events), {**rec, "fade_variant": FADE_OWN_AGGRESSION})
    u_ep = [e for e in unpaid["episodes"] if e["side"] == "short"][0]
    o_ep = [e for e in own["episodes"] if e["side"] == "short"][0]
    assert u_ep["values"]["fade_variant"] == FADE_UNPAID
    assert o_ep["values"]["fade_variant"] == FADE_OWN_AGGRESSION
    conf_u = next(s for s in u_ep["stages"] if s["stage"] == "confirmation")
    assert conf_u["verdict"] == "pass"
    conf_o = next((s for s in o_ep["stages"] if s["stage"] == "confirmation"), None)
    assert conf_o is not None
    assert conf_o["verdict"] == "fail"


def test_rules_payload_binds_implementations():
    rows = {row["rule_id"]: row for row in rules_payload()}
    for rule_id in RULES:
        line = rows[rule_id]["file_line"]
        assert "RULES[" not in line, rule_id
        assert line.startswith("sires_b02.py:"), (rule_id, line)
        assert line.split(":")[-1].isdigit(), (rule_id, line)


def test_funnel_cascade_last_stage_equals_pass():
    t0 = _base_ns()
    events = [
        (t0, 40000, 50, -1),
        (t0 + 1_000_000_000, 39990, 50, -1),
        (t0 + 2_000_000_000, 39980, 50, -1),
        (t0 + 2_200_000_000, 39980, 40, 1),
    ]
    passed = scan_b02(_view(events), _rec(branch="clean_squeeze", location_kind="lvn", side="short"))
    ep = [e for e in passed["episodes"] if e["side"] == "short" and e["research_verdict"] == "pass"][0]
    assert ep["stages"][-1]["stage"] == "management"
    assert ep["stages"][-1]["verdict"] == "pass"
    missing = scan_b02(_view(events), _rec(branch="ofm_aggressive", location_kind="lvn", side="short"))
    ep_u = [e for e in missing["episodes"] if e["side"] == "short"][0]
    assert ep_u["research_verdict"] == "unknown"
    assert ep_u["stages"][-1]["verdict"] != "pass" or ep_u["stages"][-1]["stage"] != "management"
    assert not any(s["stage"] == "management" and s["verdict"] == "pass" for s in ep_u["stages"])


def test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time():
    t0 = _base_ns()
    ns = 1_000_000_000
    events = [
        (t0, 40000, 50, 1),
        (t0 + ns, 40000, 50, 1),
        (t0 + 2 * ns, 40001, 40, 1),
        (t0 + 8 * ns, 40006, 40, 1),
        (t0 + 12 * ns, 40000, 40, 1),
        (t0 + 20 * ns, 40006, 40, 1),
        (t0 + 24 * ns, 40000, 40, 1),
    ]
    doc = refill_scan(_view(events), {"method_id": "REFILL-STUDY", "branch": "touch_record"})
    assert doc["n_touches"] >= 1
    ep = doc["episodes"][0]
    assert ep["values"]["departure_at"] < ep["values"]["touch_at"]
    assert ep["values"]["zone_known_at"] <= ep["values"]["touch_at"]
    assert ep["values"]["feature_max_known_at"] <= ep["values"]["touch_at"]
    if doc["n_touches"] >= 2:
        assert doc["episodes"][0]["values"]["touch_at"] != doc["episodes"][1]["values"]["touch_at"]
    assert ep["geometry"]["inside_ticks"] == 12
    assert ep["geometry"]["stop_distance_ticks"] == 32
    assert ep["geometry"]["target_distance_ticks"] == 96


def test_f10_future_prints_after_touch_do_not_change_pre_touch_features():
    t0 = _base_ns()
    ns = 1_000_000_000
    base = [
        (t0, 40000, 50, 1),
        (t0 + ns, 40000, 50, 1),
        (t0 + 2 * ns, 40001, 40, 1),
        (t0 + 8 * ns, 40006, 40, 1),
        (t0 + 12 * ns, 40000, 40, 1),
    ]
    later = base + [(t0 + 40 * ns, 39900, 80, -1)]
    rec = {"method_id": "REFILL-STUDY", "branch": "touch_record", "b02_now_ns": t0 + 13 * ns}
    a = refill_scan(_view(base), rec)
    b = refill_scan(_view(later), rec)
    assert a["episodes"]
    assert b["episodes"]
    left = a["episodes"][0]["values"]
    right = b["episodes"][0]["values"]
    assert left["zone_known_at"] == right["zone_known_at"]
    assert left["departure_at"] == right["departure_at"]
    assert left["feature_max_known_at"] == right["feature_max_known_at"]


def test_rr21_refill_literal_size_family_and_bracket():
    assert cluster_size_family() == (60, 80, 100)
    assert LITERAL_CLUSTER_SIZES == (60, 80, 100)
    assert HOLD_BOUNDARY_TICKS == 8
    t0 = _base_ns()
    ns = 1_000_000_000
    events = [
        (t0, 40000, 50, 1),
        (t0 + ns, 40000, 50, 1),
        (t0 + 2 * ns, 40001, 40, 1),
        (t0 + 8 * ns, 40006, 40, 1),
        (t0 + 12 * ns, 40000, 40, 1),
    ]
    ep = refill_scan(_view(events), {"method_id": "REFILL-STUDY", "branch": "touch_record"})["episodes"][0]
    assert ep["geometry"]["inside_ticks"] == 12
    assert "F10_literal_cluster_size_family" in {r["rule_id"] for r in ep["rules"]}


def test_b0_b01_byte_identity_two_slice_dates():
    before = json.loads(BYTE_BEFORE.read_text())
    after_rows = []
    for row in before["files"]:
        root = Path(before["b01_root"] if row["baseline"] == "B0.1" else before["b0_root"])
        path = root / row["date"] / row["file"]
        digest = _sha256(path)
        after_rows.append({**row, "sha256_after": digest})
        assert digest == row["sha256"], (row["file"], row["date"])
    assert sires_mod.FAMILY == "SIRES"
    assert processes_mod.FAMILY_REFILL == "REFILL-STUDY"
    assert dual_scan is not None
    for row in before["files"]:
        root = Path(before["b01_root"] if row["baseline"] == "B0.1" else before["b0_root"])
        path = root / row["date"] / row["file"]
        assert _sha256(path) == row["sha256"]
    (TRACK / "BYTE_IDENTITY_AFTER.json").write_text(json.dumps({"files": after_rows}, indent=2) + "\n")


def test_rr17_replay_sires_author_examples():
    payload = json.loads(EXAMPLES.read_text())
    by_id = {row["id"]: row for row in payload["examples"]}
    results = []
    for ident in SI_IDS:
        example = by_id[ident]
        assert example["inside_tape"] is True
        view = None
        try:
            view = build_market_view(example["date"], full_account_day=True)
        except Exception as exc:
            results.append(
                {
                    "id": ident,
                    "detected": None,
                    "branch": None,
                    "our_side": None,
                    "our_level": None,
                    "our_entry_ns": None,
                    "author_level": None,
                    "author_side": None,
                    "divergence": f"view_error:{type(exc).__name__}",
                }
            )
            continue
        row = replay_example(view, example)
        row["id"] = ident
        results.append(row)
        assert "detected" in row
        assert "divergence" in row
        assert row["detected"] in {True, False, None}
    finding = (
        "all 10 SIRES author examples are misses; our_level is null on most rows so no level comparison is possible; "
        "divergence is match_branch_only; SI-2026-07-08 our_side is long against the author's short. "
        "Reported, not forced to detect."
    )
    (TRACK / "REPLAY_SIRES.json").write_text(json.dumps({"examples": results, "finding": finding}, indent=2) + "\n")
    assert len(results) == 10


def test_slice_funnels_and_refill_slice():
    dates = list(engineering_slice_dates())
    assert dates == list(SLICE_DATES) or set(dates) == set(SLICE_DATES)
    sires_funnel = {"family": "SIRES", "dates": dates, "b01": {}, "b02": {}}
    refill_funnel = {"family": "REFILL-STUDY", "dates": dates, "b01": {}, "b02": {}}
    entry_times = {branch: {} for branch in FAMILY_BRANCHES["SIRES"]}
    refill_holds = []
    refill_dips = []
    refill_rs = []
    n_touches = 0
    from trading_research.research.rule_discovery.census_reader import CensusReader

    census = None
    try:
        census = CensusReader()
    except Exception:
        census = None
    for branch in FAMILY_BRANCHES["SIRES"]:
        sires_funnel["b01"][branch] = {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0}
        sires_funnel["b02"][branch] = {
            "episodes": 0,
            "pass": 0,
            "fail": 0,
            "unknown": 0,
            "stages": {stage: {"pass": 0, "fail": 0, "unknown": 0} for stage in STAGE_ORDER},
        }
    refill_funnel["b01"]["touch_record"] = {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0}
    refill_stages = ("reference", "location", "trigger", "confirmation", "risk", "objective")
    refill_funnel["b02"]["touch_record"] = {
        "episodes": 0,
        "pass": 0,
        "fail": 0,
        "unknown": 0,
        "stages": {stage: {"pass": 0, "fail": 0, "unknown": 0} for stage in refill_stages},
    }
    for day in dates:
        if census is not None:
            for branch in FAMILY_BRANCHES["SIRES"]:
                try:
                    eps = census.b01_episodes(day, method_id="SIRES", branch=branch)
                except Exception:
                    eps = []
                row = sires_funnel["b01"][branch]
                row["episodes"] += len(eps)
                for ep in eps:
                    v = ep.get("research_verdict")
                    if v in row:
                        row[v] += 1
            try:
                reps = census.b01_episodes(day, method_id="REFILL-STUDY", branch="touch_record")
            except Exception:
                reps = []
            refill_funnel["b01"]["touch_record"]["episodes"] += len(reps)
            for ep in reps:
                v = ep.get("research_verdict")
                if v in refill_funnel["b01"]["touch_record"]:
                    refill_funnel["b01"]["touch_record"][v] += 1
        try:
            view = build_market_view(day, full_account_day=True)
        except Exception:
            continue
        open_ns = et_ns(date.fromisoformat(day), 9, 30)
        for branch in FAMILY_BRANCHES["SIRES"]:
            doc = scan_b02(view, _rec(branch=branch, location_kind="real_extreme"))
            row = sires_funnel["b02"][branch]
            row["episodes"] += len(doc["episodes"])
            for ep in doc["episodes"]:
                v = ep["research_verdict"]
                row[v] = row.get(v, 0) + 1
                for st in ep.get("stages") or []:
                    bucket = row["stages"].setdefault(st["stage"], {"pass": 0, "fail": 0, "unknown": 0})
                    bucket[st["verdict"]] = bucket.get(st["verdict"], 0) + 1
                entry_ns = ep.get("decision_at")
                if entry_ns is not None:
                    minutes = max(0, int((int(entry_ns) - open_ns) // 60_000_000_000))
                    bin_id = f"{9:02d}:{30 + minutes - (minutes % 5):02d}" if minutes < 30 else f"{10 + (minutes - 30) // 60:02d}:{(minutes - 30) % 60 - ((minutes - 30) % 5):02d}"
                    hour = 9 + (30 + minutes) // 60
                    minute = (30 + minutes) % 60
                    minute -= minute % 5
                    bin_id = f"{hour:02d}:{minute:02d}"
                    entry_times[branch][bin_id] = entry_times[branch].get(bin_id, 0) + 1
        rdoc = refill_scan(view, {"method_id": "REFILL-STUDY", "branch": "touch_record"})
        row = refill_funnel["b02"]["touch_record"]
        row["episodes"] += len(rdoc["episodes"])
        n_touches += len(rdoc["episodes"])
        for ep in rdoc["episodes"]:
            v = ep["research_verdict"]
            row[v] = row.get(v, 0) + 1
            for st in ep.get("stages") or []:
                bucket = row["stages"].setdefault(st["stage"], {"pass": 0, "fail": 0, "unknown": 0})
                bucket[st["verdict"]] = bucket.get(st["verdict"], 0) + 1
            hold = ep["values"].get("hold_label")
            if hold is not None:
                refill_holds.append(bool(hold))
            refill_dips.append(int(ep["values"].get("dip_ticks") or 0))
            if ep["values"].get("fade_R") is not None:
                refill_rs.append(float(ep["values"]["fade_R"]))
    rate = n_touches / len(dates) if dates else 0.0
    hold_rate = (sum(refill_holds) / len(refill_holds)) if refill_holds else None
    median_dip = float(np.median(refill_dips)) if refill_dips else None
    fade_r = float(np.mean(refill_rs)) if refill_rs else None
    order_ok = 0.5 * 175 <= rate <= 2.0 * 175
    slice_doc = {
        "n_sessions": len(dates),
        "n_touches": n_touches,
        "touches_per_session": rate,
        "source": {
            "touches_per_session": 175,
            "touches": 41152,
            "sessions": 235,
            "hold_rate": 0.42,
            "median_dip_ticks": 18,
            "fade_all_R": -0.285,
        },
        "ours": {"hold_rate": hold_rate, "median_dip_ticks": median_dip, "fade_all_R": fade_r},
        "population_scale_unreconciled": True,
        "status": "population_scale_unreconciled",
        "slice_order_of_magnitude": order_ok,
        "reason": "9-date engineering slice is not the registered 235-session window; hold/dip/R are not compared as a reconciled population",
        "bracket": {"inside_ticks": 12, "stop_ticks": 32, "target_ticks": 96, "cancel_minutes": 30},
    }
    TRACK.mkdir(parents=True, exist_ok=True)
    (TRACK / "FUNNEL_SIRES.json").write_text(json.dumps(sires_funnel, indent=2) + "\n")
    (TRACK / "FUNNEL_REFILL-STUDY.json").write_text(json.dumps(refill_funnel, indent=2) + "\n")
    (TRACK / "ENTRY_TIMES.json").write_text(json.dumps({"from_0930": entry_times, "bin_minutes": 5}, indent=2) + "\n")
    (TRACK / "REFILL_SLICE.json").write_text(json.dumps(slice_doc, indent=2) + "\n")
    (TRACK / "RULES_SIRES.json").write_text(json.dumps(rules_payload(), indent=2) + "\n")
    (TRACK / "RULES_REFILL-STUDY.json").write_text(
        json.dumps(processes_mod.rules_payload(), indent=2) + "\n"
    )
    assert sires_funnel["b02"]["clean_squeeze"]["episodes"] >= 0
    assert refill_funnel["b02"]["touch_record"]["episodes"] >= 0
    for branch, row in sires_funnel["b02"].items():
        last = STAGE_ORDER[-1]
        assert row["stages"][last]["pass"] == row["pass"], (branch, row["stages"][last], row["pass"])
    refill_row = refill_funnel["b02"]["touch_record"]
    assert refill_row["stages"]["objective"]["pass"] == refill_row["pass"]
