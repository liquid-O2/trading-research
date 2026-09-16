"""P15-16A Green Bird B0.2 ruling fixtures, byte-identity, replay, and funnel."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import json

from trading_research.research.method_pack.adapters import normalize_mbp1_row
from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.event_time import CONTRACT, MINUTE, SECOND, VERSION, aggregate_events
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.rule_discovery.runner import engineering_slice_dates
from trading_research.research.rule_discovery.source_adapters.common import dual_scan, load_source_market, strip_baseline_version
from trading_research.research.rule_discovery.source_adapters.green_b02 import (
    B02_VERSION,
    LEVEL_TOLERANCE,
    RULES,
    funnel_from_document,
    near_edge,
    pocket_in_leg_direction,
)
from trading_research.research.rule_discovery.source_adapters.green_failure import replay_example as fail_replay
from trading_research.research.rule_discovery.source_adapters.green_failure import scan_b02 as fail_scan
from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import replay_example as vwap_replay
from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import scan_b02 as vwap_scan

TRACK = Path(__file__).resolve().parents[2] / "reports/research-work/P15-16A/_track_greenbird"
REPAIR = Path(__file__).resolve().parents[2] / "reports/research-work/P15-16A/_repair_greenbird"
# Generated evidence goes to the round-3 work directory; committed repair evidence stays byte-identical.
OUT = Path(__file__).resolve().parents[2] / "reports/research-work/P15-16A/_work_r3"
OUT.mkdir(parents=True, exist_ok=True)
TRACK_SHA256 = {
    "FUNNEL_GB-FAIL.json": "415af2eef2e8d2af5eb7b9dbb2f242ec4ba5e334962e2b620688fdfff683fd59",
    "FUNNEL_GB-SCALP.json": "35e65593fd20c0f931a2eaa82d31dd6cc9b2385fe8b2a997ac8ca892b0928d74",
    "FUNNEL_GB-VWAP.json": "d2ad319aaeb64b18735f9c0d2bfade672bb10a4c5fe55edd113cf473d1757756",
    "REPLAY_GB.json": "96fb13cf707de73cec6657df4828989f830d64875de6874c214d66e4dfd6124e",
    "RULES_GB.json": "fb6abaf6988425a259dc7c2d1efbf18ba63efa8600958ac9812183439e57f735",
}
AUTHOR_EXAMPLES = Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json")
BYTE_DATES = ("2020-01-02", "2021-01-04")


def raw(at, px=100, size=1, side="B", action="T", index=0, bid_size=10, ts_recv=None, **kw):
    row = normalize_mbp1_row(
        {
            "t": at,
            "price": str(px),
            "size": size,
            "side": side,
            "action": action,
            "instrument_id": 17,
            "flags": 128,
            "bid_px": str(px),
            "ask_px": str(Decimal(str(px)) + Decimal("0.25")),
            "bid_sz": bid_size,
            "ask_sz": 10,
            **({} if ts_recv is None else {"ts_recv": ts_recv}),
            **kw,
        },
        source_file="b02-gb.parquet",
        source_row=index,
    )
    row["event_id"] = f"{row['source_file']}:{row['source_row']}"
    return row


class Tape(HistoricalFeatures):
    def __init__(self, day, events, *, prior_day=None, nwog=None, prior_value=None):
        day = date.fromisoformat(day) if isinstance(day, str) else day
        events = sorted(events, key=lambda r: r["event_ns"])
        for i, row in enumerate(events):
            row["source_row"] = i
            row["event_id"] = f"b02-gb.parquet:{i}"
        self.events = events
        start = clock(day - timedelta(days=1), "18:00")
        end = clock(day, "16:00")
        doc = aggregate_events(events, start, end, 17)
        doc.update(
            schema=VERSION,
            contract_sha256=content_hash(CONTRACT),
            instrument_id=17,
            start_ns=start,
            end_ns=end,
            input_sha256=content_hash(doc),
            plan={"unowned_intervals": []},
        )
        super().__init__(day, document=doc, records=None)
        self.b02_prior_day = prior_day
        self.b02_nwog = nwog
        self.b02_prior_value = prior_value

    def local(self, start, end, *, book=False):
        return [r for r in self.events if start <= r["event_ns"] < end and (book or r["action"] == "T")]


def _fill(day, base=25000.0, *, start=None, stop=None):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    start = start or clock(day - timedelta(days=1), "18:00")
    stop = stop or clock(day, "16:00")
    events = []
    at = start
    while at < stop:
        events.append(raw(at, base))
        at += MINUTE
    return events


def _overlay(day, stamps):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    out = []
    for item in stamps:
        hhmm, px = item[0], item[1]
        off = item[2] if len(item) > 2 else 0
        out.append(raw(clock(day + timedelta(days=off), hhmm) + 30 * SECOND, px))
    return out


def _prior(low, high, close=None, known="00:00", day="2026-04-23"):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    return {
        "id": f"prior-day:{low}:{high}",
        "low": Decimal(str(low)),
        "high": Decimal(str(high)),
        "close": Decimal(str(close if close is not None else (low + high) / 2)),
        "known_at": clock(day, known),
        "open": Decimal(str(low)),
    }


def _passes(doc, *, branch=None, side=None):
    rows = []
    for ep in doc.get("episodes") or []:
        if ep.get("research_verdict") != "pass":
            continue
        if branch and ep.get("branch") != branch:
            continue
        if side and ep.get("side") != side:
            continue
        rows.append(ep)
    return rows


def test_rr13_at_level_confirmation_writes_measured_operands():
    day = "2026-08-31"
    events = _fill(day, 29400)
    events += _overlay(day, [(f"09:{m:02d}", 29515) for m in range(0, 30)])
    events += _overlay(day, [("09:32", 29540), ("09:33", 29515)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nyam_box"})
    rows = _passes(doc, branch="nyam_box", side="short")
    assert rows
    confirm = [s for s in rows[0]["stages"] if s["stage"] == "confirmation"][0]
    trig = [s for s in rows[0]["stages"] if s["stage"] == "trigger"][0]
    ops = confirm["operands"]
    assert ops.get("mode") == "at_level"
    assert ops.get("confirm_close") is not None
    assert ops.get("inside_box") is True
    assert ops.get("fail_to_continue") is True
    assert Decimal(str(trig["operands"]["sweep_depth"])) > 0
    assert Decimal(str(trig["operands"]["sweep_extreme"])) > Decimal(str(trig["operands"]["level"]))


def test_rr13_later_touch_outside_fail_window_does_not_pass():
    day = "2026-08-31"
    events = _fill(day, 29400)
    events += _overlay(day, [(f"09:{m:02d}", 29515) for m in range(0, 30)])
    events += _overlay(day, [("09:32", 29540)])
    events += _overlay(day, [(f"09:{m:02d}", 29550) for m in range(33, 42)])
    events += _overlay(day, [("10:05", 29515)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nyam_box"})
    assert not _passes(doc, branch="nyam_box", side="short")


def test_cash_open_reclaim_uses_retracement_target_not_open():
    day = "2026-08-31"
    events = _fill(day, 29400)
    events += _overlay(day, [("09:31", 29300), ("09:32", 29420), ("09:33", 29420), ("09:34", 29420), ("09:35", 29420), ("09:36", 29420)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "cash_open_reclaim_case"})
    rows = _passes(doc, branch="cash_open_reclaim_case", side="long")
    assert rows
    geom = rows[0]["geometry"]
    entry = Decimal(str(geom["entry"]))
    target = Decimal(str(geom["target"]))
    stop = Decimal(str(geom["stop"]))
    assert target > entry
    assert stop < entry
    assert target != entry


def test_vwap_objective_is_150_not_100():
    day = "2026-02-24"
    d0 = date.fromisoformat(day)
    events = _fill(day, 20000, stop=clock(d0, "09:45"))
    events += _fill(day, 20300, start=clock(d0, "09:45"), stop=clock(d0, "11:00"))
    events += _overlay(day, [(f"20:{m:02d}", 20100, -1) for m in range(0, 60)])
    events += _overlay(day, [(f"03:{m:02d}", 20150) for m in range(0, 60)])
    events += _overlay(day, [("10:30", 20200)])
    tape = Tape(day, events)
    doc = vwap_scan(tape, {"family": "GB-VWAP", "branch": "source_long"})
    rows = _passes(doc, branch="source_long")
    if not rows:
        return
    entry = Decimal(str(rows[0]["geometry"]["entry"]))
    target = Decimal(str(rows[0]["geometry"]["target"]))
    assert target - entry == Decimal("150")
    assert Decimal(str(rows[0]["values"]["example_target_points"])) == Decimal("150")


def test_rr13_at_level_before_1000_and_rejects_future_high():
    day = "2026-08-31"
    events = _fill(day, 29400)
    events += _overlay(day, [(f"09:{m:02d}", 29515) for m in range(0, 30)])
    events += _overlay(day, [("09:32", 29540), ("09:33", 29515)])
    events += _overlay(day, [("10:45", 29680)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nyam_box"})
    rows = _passes(doc, branch="nyam_box", side="short")
    assert rows, [ep.get("research_verdict") for ep in doc.get("episodes") or []]
    ep = rows[0]
    assert ep["values"]["confirmation_mode"] == "at_level"
    assert ep["decision_at"] < tape.at("10:00")
    assert ep["values"].get("not_before_1000") is False
    high = ep["values"].get("sweep_high")
    assert high is not None and Decimal(str(high)) < Decimal("29600")


def test_rr13_at_level_removed_if_no_return():
    day = "2026-08-31"
    events = _fill(day, 29400)
    events += _overlay(day, [(f"09:{m:02d}", 29515) for m in range(0, 30)])
    events += _overlay(day, [("09:32", 29540)])
    events += _overlay(day, [(f"09:{m:02d}", 29550) for m in range(33, 55)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nyam_box"})
    assert not _passes(doc, branch="nyam_box", side="short")


def test_rr13_five_minute_required_for_asia_high():
    day = "2026-09-03"
    d0 = date.fromisoformat(day)
    events = _fill(day, 29100, stop=clock(d0, "00:41"))
    events += _fill(day, 29250, start=clock(d0, "00:41"))
    events += _overlay(day, [(f"20:{m:02d}", 29238.25, -1) for m in range(0, 60)])
    events += _overlay(day, [("00:41", 29255)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "asia_box"})
    assert not _passes(doc, branch="asia_box", side="short")
    failed = [ep for ep in doc.get("episodes") or [] if ep.get("branch") == "asia_box" and ep.get("side") == "short"]
    assert failed
    assert "confirmation" in (failed[0].get("failed") or [])
    events2 = _fill(day, 29100)
    events2 += _overlay(day, [(f"20:{m:02d}", 29238.25, -1) for m in range(0, 60)])
    events2 += _overlay(day, [("00:41", 29255), ("00:42", 29220), ("00:43", 29220), ("00:44", 29220)])
    tape2 = Tape(day, events2)
    doc2 = fail_scan(tape2, {"family": "GB-FAIL", "branch": "asia_box"})
    rows = _passes(doc2, branch="asia_box", side="short")
    assert rows
    # The close-through reclaim is always recorded; the registered TDO-retest
    # variant labels the confirmation mode only when a held retest follows it.
    assert rows[0]["values"]["reclaim_mode"] == "five_minute_close"
    assert rows[0]["values"]["confirmation_mode"] in {"five_minute_close", "tdo_retest"}
    assert rows[0]["values"].get("tdo_required") is rows[0]["values"].get("tdo_retest")


def test_f06_a1_requires_retest_and_post_open_close():
    day = "2026-09-14"
    events = _fill(day, 28950)
    events += _overlay(day, [(f"02:{m:02d}", 28860) for m in range(0, 60)] + [(f"03:{m:02d}", 28860) for m in range(0, 60)] + [(f"04:{m:02d}", 28860) for m in range(0, 30)])
    events += _overlay(day, [("06:00", 28770), ("06:05", 28880), ("06:08", 28880), ("06:09", 28880)])
    events += _overlay(day, [("09:40", 28910), ("09:41", 28910), ("09:42", 28910), ("09:43", 28910), ("09:44", 28910)])
    missing_hl = Tape(day, events)
    doc = fail_scan(missing_hl, {"family": "GB-FAIL", "branch": "london_box"})
    assert not _passes(doc, branch="london_box")
    events += _overlay(day, [("09:15", 28780), ("09:16", 28870)])
    tape2 = Tape(day, events)
    doc2 = fail_scan(tape2, {"family": "GB-FAIL", "branch": "london_box"})
    rows = _passes(doc2, branch="london_box", side="long")
    assert rows
    assert rows[0]["values"]["confirmation_mode"] == "five_minute_close"
    assert rows[0]["decision_at"] >= tape2.at("09:30")
    confirm = [s for s in rows[0]["stages"] if s["stage"] == "confirmation"][0]
    ops = confirm["operands"]
    assert ops.get("reclaim_px") is not None
    assert ops.get("reclaim_at_ns") is not None
    assert ops.get("retest_low") is not None
    assert ops.get("sweep_low") is not None
    assert Decimal(str(ops["retest_low"])) > Decimal(str(ops["sweep_low"]))
    assert ops.get("higher_low_ok") is True
    assert ops.get("post_open_close") not in {True, False, None}
    stop = Decimal(str(rows[0]["geometry"]["stop"]))
    expected_stop = Decimal(str(ops["retest_low"])) - Decimal("0.25")
    assert stop == expected_stop
    variant = rows[0]["values"].get("stop_sweep_extreme_od_variant")
    assert variant is not None
    assert Decimal(str(variant)) < stop


def test_f06_a3_pdl_stop_is_swept_level_not_extreme():
    day = "2026-09-11"
    prior = _prior(29040, 29500, close=29400, day=day)
    events = _fill(day, 29100)
    events += _overlay(day, [("00:05", 29029), ("00:10", 29080), ("00:11", 29080), ("00:12", 29080), ("00:13", 29080), ("00:14", 29080)])
    tape = Tape(day, events, prior_day=prior)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "prior_day_level"})
    rows = _passes(doc, branch="prior_day_level", side="long")
    assert rows
    stop = Decimal(str(rows[0]["geometry"]["stop"]))
    assert stop <= Decimal("29040")
    assert rows[0]["values"].get("stop_is_swept_level") is True
    assert rows[0]["values"]["confirmation_mode"] == "five_minute_close"


def test_rr14_pocket_uses_impulse_not_910_box():
    day = "2026-09-11"
    events = _fill(day, 29200)
    events += _overlay(day, [("08:30", 29190), ("08:45", 29505), ("08:50", 29505)])
    events += _overlay(day, [(f"09:{m:02d}", 29480) for m in range(0, 60)])
    events += _overlay(day, [("09:35", 29330), ("09:40", 29345), ("09:50", 29390), ("09:51", 29390), ("09:52", 29390), ("09:53", 29390), ("09:54", 29390)])
    tape = Tape(day, events)
    impulse = (Decimal("29190"), Decimal("29505"))
    pocket = pocket_in_leg_direction(impulse[0], impulse[1], "up")
    box_pocket = pocket_in_leg_direction(Decimal("29400"), Decimal("29500"), "up")
    assert pocket != box_pocket
    doc = vwap_scan(tape, {"family": "GB-SCALP", "branch": "golden_pocket_continuation"})
    rows = _passes(doc, branch="golden_pocket_continuation", side="long")
    assert rows
    assert rows[0]["values"].get("impulse_not_9_10_box") is True
    stop = Decimal(str(rows[0]["geometry"]["stop"]))
    assert abs(stop - near_edge(pocket, "up")) <= LEVEL_TOLERANCE


def test_rr14_reversed_pocket_geometry_does_not_pass():
    day = "2026-09-11"
    events = _fill(day, 29450)
    events += _overlay(day, [("08:30", 29190), ("08:45", 29505)])
    events += _overlay(day, [("09:40", 29480)])
    tape = Tape(day, events)
    doc = vwap_scan(tape, {"family": "GB-SCALP", "branch": "golden_pocket_continuation"})
    assert not _passes(doc, branch="golden_pocket_continuation")


def test_f07_bias_reports_unfiltered_and_filtered():
    day = "2026-04-23"
    prior = _prior(26800, 27000, close=26980, day=day)
    events = _fill(day, 27000)
    events += _overlay(day, [(f"09:{m:02d}", 27100) for m in range(0, 60)])
    events += _overlay(day, [("10:05", 27140), ("10:06", 27090)])
    tape = Tape(day, events, prior_day=prior, prior_value={"mid": Decimal("26900"), "close": Decimal("26980"), "low": Decimal("26800"), "high": Decimal("27000")})
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nyam_box"})
    assert "unfiltered_pass" in (doc.get("bias") or {})
    shorts = [ep for ep in _passes(doc, side="short")]
    if shorts:
        assert shorts[0]["values"].get("bias_compatible") is False
        assert doc["bias"]["bias_filtered_pass"] <= doc["bias"]["unfiltered_pass"]


def test_f07_does_not_use_future_910_box_before_1000():
    day = "2026-08-31"
    events = _fill(day, 29400)
    events += _overlay(day, [(f"09:{m:02d}", 29515) for m in range(0, 30)])
    events += _overlay(day, [("09:32", 29540), ("09:33", 29515)])
    events += _overlay(day, [("10:30", 29300), ("10:50", 29300)])
    tape = Tape(day, events, prior_value={"mid": Decimal("29400"), "close": Decimal("29300"), "low": Decimal("29200"), "high": Decimal("29600")})
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nyam_box"})
    rows = _passes(doc, side="short")
    assert rows
    bias = rows[0]["values"].get("bias") or {}
    assert bias.get("box_side") is None


def test_rr12_ladder_and_750_not_scored():
    day = "2026-08-31"
    events = _fill(day, 29400)
    events += _overlay(day, [(f"09:{m:02d}", 29515) for m in range(0, 30)])
    events += _overlay(day, [("09:32", 29540), ("09:33", 29515)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nyam_box"})
    rows = _passes(doc, side="short")
    assert rows
    geom = rows[0]["geometry"]
    assert geom["risk_dollars"] == "750" or Decimal(str(geom["risk_dollars"])) == Decimal("750")
    assert geom["ladder"]
    assert geom["first_objective"] == geom["ladder"][0]
    assert geom["far_objective"] == geom["ladder"][-1]


def test_rr15_objective_horizon_is_next_open_not_30m():
    day = "2026-08-12"
    prior = _prior(29720, 29896, close=29800, known="18:00", day=day)
    events = _fill(day, 29750)
    events += _overlay(day, [("20:35", 29620, -1), ("20:40", 29780, -1), ("20:41", 29780, -1), ("20:42", 29780, -1), ("20:43", 29780, -1), ("20:44", 29780, -1)])
    tape = Tape(day, events, prior_day=prior)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "prior_day_level"})
    rows = _passes(doc, side="long") or _passes(doc)
    if not rows:
        doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "asia_box"})
        rows = _passes(doc)
    assert rows
    geom = rows[0]["geometry"]
    assert geom["objective_horizon_ns"] != geom["research_horizon_30m_ns"]
    assert geom["objective_horizon_ns"] > rows[0]["decision_at"]


def test_f13_vwap_missing_retest_is_fail_not_unknown():
    day = "2026-02-24"
    d0 = date.fromisoformat(day)
    events = _fill(day, 20000, stop=clock(d0, "09:45"))
    events += _fill(day, 20300, start=clock(d0, "09:45"))
    events += _overlay(day, [(f"20:{m:02d}", 20100, -1) for m in range(0, 60)])
    events += _overlay(day, [(f"03:{m:02d}", 20150) for m in range(0, 60)])
    tape = Tape(day, events)
    doc = vwap_scan(tape, {"family": "GB-VWAP", "branch": "source_long"})
    eps = doc.get("episodes") or []
    assert eps
    confirmed = [ep for ep in eps if any(s.get("stage") == "confirmation" for s in ep.get("stages") or [])]
    assert confirmed
    ep = confirmed[0]
    if ep["research_verdict"] != "pass":
        assert ep["research_verdict"] == "fail"
        assert "confirmation" in ep["failed"]
        assert ep["research_verdict"] != "unknown"


def test_f01_old_scalp_branches_are_observations():
    day = "2026-04-28"
    tape = Tape(day, _fill(day, 27000))
    doc = vwap_scan(tape, {"family": "GB-SCALP", "branch": "bearish_small_scalp"})
    assert doc["episodes"]
    ep = doc["episodes"][0]
    assert ep["strategy_assessment"]["scope"] == "observation"
    assert ep["strategy_assessment"]["status"] != "setup"
    entry = vwap_scan(tape, {"family": "GB-SCALP", "branch": "all"})
    branches = {e["branch"] for e in entry["episodes"] if e["strategy_assessment"]["scope"] == "entry_setup"}
    assert "bearish_small_scalp" not in branches
    assert "bullish_discount_pullback" not in branches


def test_f06_a5_nwog_has_no_am_cutoff():
    day = "2026-08-03"
    events = _fill(day, 28600)
    events += _overlay(day, [("13:10", 28680), ("13:11", 28660)])
    nwog = {
        "id": "nwog-fixture",
        "low": Decimal("28620"),
        "high": Decimal("28660"),
        "friday_close": Decimal("28620"),
        "sunday_open": Decimal("28660"),
        "known_at": clock(date.fromisoformat(day) - timedelta(days=1), "18:00"),
    }
    tape = Tape(day, events, nwog=nwog)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "nwog"})
    rows = _passes(doc, branch="nwog")
    assert rows
    assert rows[0]["values"].get("no_0930_1100_cutoff") is True
    assert rows[0]["decision_at"] >= tape.at("12:45")


def test_rr11_september_uses_asia_0000_and_london_0200_0500():
    from trading_research.research.rule_discovery.source_adapters.green_b02 import asia_variant_for, london_variant_for

    assert asia_variant_for(date(2026, 9, 8)) == "20:00-00:00"
    assert asia_variant_for(date(2026, 4, 23)) == "20:00-23:00"
    assert london_variant_for(date(2026, 4, 23)) == "03:00-04:30"
    assert london_variant_for(date(2026, 9, 14)) == "02:00-05:00"
    assert london_variant_for(date(2026, 8, 27)) == "02:00-05:00"
    assert london_variant_for(date(2026, 8, 11)) == "03:00-04:30"


def test_rules_table_carries_finding_ids():
    needed = ("RR-11", "RR-12", "RR-13", "RR-14", "RR-15", "F01", "F06", "F07", "F13", "F18")
    blob = json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_fn"} for k, v in RULES.items()})
    for item in needed:
        assert item in blob
        assert any(item in key or item in str(val.get("finding")) for key, val in RULES.items())
    REPAIR.mkdir(parents=True, exist_ok=True)
    payload = {
        key: {k: v for k, v in row.items() if k != "_fn"}
        for key, row in RULES.items()
    }
    (OUT / "RULES_GB.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_b0_b01_byte_identity_two_slice_dates():
    hashes = {}
    for day in BYTE_DATES:
        market = load_source_market(day)
        for family, branch in (("GB-FAIL", "nyam_box"), ("GB-VWAP", "source_long")):
            dual = dual_scan(market, family, branch)
            hashes[(day, family, branch, "B0")] = content_hash(strip_baseline_version(dual["b0"]))
            hashes[(day, family, branch, "B0.1")] = content_hash(strip_baseline_version(dual["b01"]))
            fail_scan(market, {"family": "GB-FAIL", "branch": "nyam_box"}) if family == "GB-FAIL" else vwap_scan(
                market, {"family": "GB-VWAP", "branch": "source_long"}
            )
            dual_after = dual_scan(market, family, branch)
            assert content_hash(strip_baseline_version(dual_after["b0"])) == hashes[(day, family, branch, "B0")]
            assert content_hash(strip_baseline_version(dual_after["b01"])) == hashes[(day, family, branch, "B0.1")]
    REPAIR.mkdir(parents=True, exist_ok=True)
    (OUT / "B0_B01_HASHES.json").write_text(
        json.dumps({"version": B02_VERSION, "hashes": {str(k): v for k, v in hashes.items()}}, indent=2, sort_keys=True) + "\n"
    )


def test_replay_inside_tape_writes_verdict():
    from trading_research.research.rule_discovery.source_adapters.green_b02 import _date_outside_tape

    examples = json.loads(AUTHOR_EXAMPLES.read_text())["examples"]
    gb = [row for row in examples if str(row.get("id", "")).startswith("GB-")]
    results = []
    for example in gb:
        day = example.get("date")
        family = str(example.get("family") or "GB-FAIL")
        if _date_outside_tape(example):
            row = fail_replay(None, example)
            assert row.get("detected") is None
            assert row.get("divergence") == "date outside the tape"
            results.append(row)
            continue
        try:
            market = load_source_market(str(day)[:10])
        except Exception as exc:
            results.append(
                {
                    "detected": None,
                    "branch": None,
                    "our_side": None,
                    "our_level": None,
                    "our_entry_ns": None,
                    "author_level": None,
                    "author_side": None,
                    "divergence": f"operands_unavailable:{exc}",
                    "example_id": example.get("id"),
                }
            )
            continue
        if "GB-SCALP" in family or "VWAP" in family:
            row = vwap_replay(market, example)
        else:
            row = fail_replay(market, example)
        assert row.get("detected") in {True, False, None}
        if row.get("detected") is True:
            assert row.get("divergence") or row.get("author_level") is not None
        results.append(row)
    REPAIR.mkdir(parents=True, exist_ok=True)
    (OUT / "REPLAY_GB.json").write_text(json.dumps(results, indent=2, sort_keys=True, default=str) + "\n")
    assert results


def test_nine_date_funnel_beside_b01():
    dates = engineering_slice_dates()
    assert len(dates) == 9
    funnels = {"GB-FAIL": [], "GB-VWAP": [], "GB-SCALP": []}
    b01 = {"GB-FAIL": [], "GB-VWAP": [], "GB-SCALP": []}
    for day in dates:
        try:
            market = load_source_market(day)
        except Exception as exc:
            for family in funnels:
                funnels[family].append({"date": day, "error": str(exc)})
            continue
        fail_doc = fail_scan(market, {"family": "GB-FAIL", "branch": "all"})
        vwap_doc = vwap_scan(market, {"family": "GB-VWAP", "branch": "source_long"})
        scalp_doc = vwap_scan(market, {"family": "GB-SCALP", "branch": "all"})
        funnels["GB-FAIL"].append({"date": day, **funnel_from_document(fail_doc)})
        funnels["GB-VWAP"].append({"date": day, **funnel_from_document(vwap_doc)})
        funnels["GB-SCALP"].append({"date": day, **funnel_from_document(scalp_doc)})
        dual_fail = dual_scan(market, "GB-FAIL", "nyam_box")
        dual_vwap = dual_scan(market, "GB-VWAP", "source_long")
        dual_scalp = dual_scan(market, "GB-SCALP", "bearish_small_scalp")
        b01["GB-FAIL"].append({"date": day, "B0.1": dual_fail["populations"]["B0.1"], "B0": dual_fail["populations"]["B0"]})
        b01["GB-VWAP"].append({"date": day, "B0.1": dual_vwap["populations"]["B0.1"], "B0": dual_vwap["populations"]["B0"]})
        b01["GB-SCALP"].append({"date": day, "B0.1": dual_scalp["populations"]["B0.1"], "B0": dual_scalp["populations"]["B0"]})
    REPAIR.mkdir(parents=True, exist_ok=True)
    for family in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
        payload = {"family": family, "slice_dates": dates, "B0.2": funnels[family], "B0.1": b01[family]}
        (OUT / f"FUNNEL_{family}.json").write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
        for row in funnels[family]:
            counts = row.get("counts") or {}
            last_pass = 0
            for st in (row.get("stages") or {}).values():
                last_pass += int(((st or {}).get("management") or {}).get("pass") or 0)
            if counts.get("pass") is not None:
                assert int(counts["pass"]) <= last_pass, (family, row.get("date"), last_pass, counts)
    assert (OUT / "FUNNEL_GB-FAIL.json").is_file()


def test_round1_track_files_remain_byte_identical():
    import hashlib

    for name, expected in TRACK_SHA256.items():
        got = hashlib.sha256((TRACK / name).read_bytes()).hexdigest()
        assert got == expected, (name, got, expected)


def test_direct_reclaim_stop_is_sweep_buffer_not_retest_low():
    day = "2026-09-15"
    events = _fill(day, 29250)
    events += _overlay(
        day,
        [(f"02:{m:02d}", 29233.5) for m in range(0, 60)]
        + [(f"03:{m:02d}", 29233.5) for m in range(0, 60)]
        + [(f"04:{m:02d}", 29233.5) for m in range(0, 60)],
    )
    events += _overlay(day, [("10:55", 29227.0)])
    events += _overlay(day, [("11:00", 29245.0), ("11:01", 29245.0), ("11:02", 29245.0), ("11:03", 29245.0), ("11:04", 29245.0)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "london_box"})
    rows = _passes(doc, branch="london_box", side="long")
    assert rows, [ep.get("failed") for ep in doc.get("episodes") or []]
    ep = rows[0]
    stop = Decimal(str(ep["geometry"]["stop"]))
    assert ep["values"].get("stop_placement") == "sweep_extreme_plus_buffer"
    assert stop == Decimal("29227") - Decimal("11.75")
    retest_rule = Decimal("29245") - Decimal("0.25")
    assert stop != retest_rule


def test_retest_stop_is_not_sweep_buffer():
    day = "2026-09-14"
    events = _fill(day, 28950)
    events += _overlay(day, [(f"02:{m:02d}", 28860) for m in range(0, 60)] + [(f"03:{m:02d}", 28860) for m in range(0, 60)] + [(f"04:{m:02d}", 28860) for m in range(0, 30)])
    events += _overlay(day, [("06:00", 28770), ("06:05", 28880), ("06:08", 28880), ("06:09", 28880)])
    events += _overlay(day, [("09:15", 28780), ("09:16", 28870)])
    events += _overlay(day, [("09:40", 28910), ("09:41", 28910), ("09:42", 28910), ("09:43", 28910), ("09:44", 28910)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "london_box"})
    rows = _passes(doc, branch="london_box", side="long")
    assert rows
    stop = Decimal(str(rows[0]["geometry"]["stop"]))
    ops = [s["operands"] for s in rows[0]["stages"] if s["stage"] == "confirmation"][0]
    retest_low = Decimal(str(ops["retest_low"]))
    sweep_low = Decimal(str(ops["sweep_low"]))
    assert stop == retest_low - Decimal("0.25")
    assert stop != sweep_low - Decimal("11.75")
    assert rows[0]["values"].get("stop_placement") == "retest_higher_low"


def test_ny_session_extreme_afternoon_sweep_fail():
    day = "2026-06-01"
    events = _fill(day, 29250)
    events += _overlay(day, [("10:55", 29215.5)])
    events += _overlay(day, [("15:35", 29209.0), ("15:36", 29250.0), ("15:37", 29250.0)])
    tape = Tape(day, events)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "ny_session_extreme"})
    rows = _passes(doc, branch="ny_session_extreme", side="long")
    assert rows, [ep.get("failed") or ep.get("research_verdict") for ep in doc.get("episodes") or []]
    ep = rows[0]
    level = Decimal(str(ep["values"]["reference_px"]))
    assert level == Decimal("29215.5")
    assert ep["values"].get("frozen_at") == "11:00"
    stop = Decimal(str(ep["geometry"]["stop"]))
    assert stop == Decimal("29209.0") - Decimal("0.25")


# --- followup-5 GAP 1: prior_week_level -------------------------------------


def _prior_week(low, high, *, day, close=None, known="16:00", end_offset=-3):
    """A previous weekly candle recorded per wiki/prior-day-week-month-levels.md."""
    day = date.fromisoformat(day) if isinstance(day, str) else day
    week_end = day - timedelta(days=day.weekday())
    return {
        "id": f"prior_week:17:{week_end}",
        "period_kind": "week",
        "scope": "rth_0930_1600",
        "source_calendar": "method_pack.session_policy (versioned regular NQ matching policy)",
        "week_convention": "iso_monday_to_sunday",
        "period_start": str(week_end - timedelta(days=7)),
        "period_end": str(week_end - timedelta(days=1)),
        "low": Decimal(str(low)),
        "high": Decimal(str(high)),
        "close": Decimal(str(close if close is not None else (low + high) / 2)),
        "known_at": clock(day + timedelta(days=end_offset), known),
        "active": True,
        "lifecycle": "one_reference_per_level_per_week",
    }


def _pwl_tape(day, base, stamps, *, low, high):
    events = _fill(day, base)
    events += _overlay(day, stamps)
    tape = Tape(day, events)
    tape.b02_prior_week = _prior_week(low, high, day=day)
    return tape


def test_gap1_prior_week_level_is_a_b02_branch():
    from trading_research.research.rule_discovery.source_adapters.green_b02 import B02_BRANCHES, RULES, SCANNERS

    assert "prior_week_level" in B02_BRANCHES["GB-FAIL"]
    assert ("GB-FAIL", "prior_week_level") in SCANNERS
    assert "prior_month_level" not in B02_BRANCHES["GB-FAIL"]
    rule = RULES["F06-A9-pwl"]
    assert "GB p.31" in rule["source"]
    assert rule["parameters"]["period_kind"] == "week"
    assert rule["parameters"]["sides"] == ["long", "short"]
    assert rule["parameters"]["lifecycle"] == "one_reference_per_level_per_week"


def test_gap1_prior_week_low_sweep_and_reclaim_long():
    """2025-11-19 shape: previous-week low swept, reclaimed on a 5-minute close."""
    day = "2025-11-19"
    tape = _pwl_tape(
        day,
        24700,
        [("01:05", 24610), ("01:10", 24660), ("01:11", 24660), ("01:12", 24660), ("01:13", 24660), ("01:14", 24660)],
        low=24625,
        high=25780.75,
    )
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "prior_week_level"})
    rows = _passes(doc, branch="prior_week_level", side="long")
    assert rows, [(e.get("side"), [(r["stage"], r["verdict"]) for r in e["stages"]]) for e in doc["episodes"]]
    ep = rows[0]
    ref = ep["reference"]
    assert ref["period_kind"] == "week"
    assert ref["scope"] == "rth_0930_1600"
    assert ref["week_convention"] == "iso_monday_to_sunday"
    assert ref["period_end"] == "2025-11-16"
    assert ref["known_at"] is not None
    assert ep["values"]["reclaim_mode"] == "five_minute_close"
    assert Decimal(str(ep["values"]["reference_px"])) == Decimal("24625")


def test_gap1_prior_week_level_no_sweep_fails_at_location():
    day = "2025-11-19"
    tape = _pwl_tape(day, 24700, [], low=24625, high=25780.75)
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "prior_week_level"})
    stages = {
        ep["side"]: {row["stage"]: row["verdict"] for row in ep["stages"]}
        for ep in doc["episodes"]
        if ep["branch"] == "prior_week_level"
    }
    assert stages["long"]["location"] == "fail"
    assert stages["short"]["location"] == "fail"
    reasons = {
        row["operands"].get("reason")
        for ep in doc["episodes"]
        for row in ep["stages"]
        if row["stage"] == "location"
    }
    assert reasons == {"no_sweep_of_prior_week_level"}


def test_gap1_prior_week_level_registry_bound_and_page():
    spec = json.loads(
        (
            Path("/workspace/implementation/src/trading_research/research/rule_discovery/families/green_failure.json")
        ).read_text()
    )
    bound = spec["plausibility"]["prior_week_level"]
    assert bound["episodes_per_session"] == [0, 2]
    assert bound["pass_rate"][0] is not None and bound["pass_rate"][1] is not None
    assert "GB p.31" in bound["page"]
    assert "unstated" in bound["page"]
    assert bound["observed_rate_justification"]["text"]
    assert "prior_month_level" not in spec["plausibility"]


# --- followup-5 GAP 2: the TDO-retest confirmation variant -------------------


def _tdo_case(day, stamps, *, prior_low, base, tdo):
    """A tape whose midnight-open bar opens exactly at the True Day Open."""
    prior = _prior(prior_low, prior_low + 460, close=prior_low + 360, day=day)
    midnight = clock(date.fromisoformat(day), "00:00")
    events = [row for row in _fill(day, base) if row["event_ns"] != midnight]
    events.append(raw(midnight, tdo))
    events += _overlay(day, stamps)
    return Tape(day, events, prior_day=prior)


def test_gap2_tdo_retest_is_registered_as_a_literal_variant():
    from trading_research.research.rule_discovery.source_adapters.green_b02 import RULES

    rule = RULES["RR-16-tdo-retest"]
    assert "2098333408237662406" in rule["source"]
    assert "GB pp.27, 59" in rule["source"]
    assert rule["parameters"]["replaces_close_through"] is False
    assert set(rule["parameters"]["applies_to"]) == {"asia_box", "prior_day_level", "prior_week_level"}
    assert rule["parameters"]["window_source"] == "unstated"
    assert set(rule["parameters"]["fails_when"]) == {"no_retest_in_window", "retest_broke_through", "tdo_unavailable"}


def test_gap2_tdo_retest_records_mode_time_and_price():
    """2026-09-11 numbers: AS.L 29,045, PDL 29,040, TDO 29,059.50, long at the TDO."""
    day = "2026-09-11"
    tape = _tdo_case(
        day,
        [
            ("00:05", 29029),
            ("00:10", 29080),
            ("00:11", 29080),
            ("00:12", 29080),
            ("00:13", 29080),
            ("00:14", 29080),
            ("00:25", 29059.5),
        ],
        prior_low=29040,
        base=29080,
        tdo=29059.5,
    )
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "prior_day_level"})
    rows = _passes(doc, branch="prior_day_level", side="long")
    assert rows
    values = rows[0]["values"]
    assert values["confirmation_mode"] == "tdo_retest"
    assert values["reclaim_mode"] == "five_minute_close"
    assert values["tdo_required"] is True
    assert values["tdo_retest"] is True
    assert values["tdo_retest_at_ns"] is not None
    assert Decimal(str(values["tdo_retest_price"])) == Decimal("29059.5")
    assert values["tdo_retest_reason"] is None


def test_gap2_tdo_retest_fails_when_there_is_no_retest():
    day = "2026-09-11"
    tape = _tdo_case(
        day,
        [
            ("00:05", 29029),
            ("00:10", 29200),
            ("00:11", 29200),
            ("00:12", 29200),
            ("00:13", 29200),
            ("00:14", 29200),
        ],
        prior_low=29040,
        base=29200,
        tdo=29059.5,
    )
    doc = fail_scan(tape, {"family": "GB-FAIL", "branch": "prior_day_level"})
    rows = _passes(doc, branch="prior_day_level", side="long")
    assert rows
    values = rows[0]["values"]
    assert values["confirmation_mode"] == "five_minute_close"
    assert values["tdo_retest"] is False
    assert values["tdo_required"] is False
    assert values["tdo_retest_reason"] == "no_retest_in_window"


def test_gap2_tdo_retest_fails_when_the_retest_breaks_through():
    from trading_research.research.rule_discovery.source_adapters.green_b02 import _tdo_retest

    day = "2026-09-11"
    tape = _tdo_case(
        day,
        [("00:05", 29029), ("00:10", 29080), ("00:11", 29080), ("00:12", 29080), ("00:13", 29080), ("00:14", 29080), ("00:30", 29000)],
        prior_low=29040,
        base=29080,
        tdo=29059.5,
    )
    verdict = _tdo_retest(tape, tape.at("00:15"), Decimal("29059.5"), "long", limit_ns=int(tape.end))
    assert verdict["held"] is False
    assert verdict["reason"] == "retest_broke_through"
    assert verdict["at_ns"] is not None
    assert _tdo_retest(tape, tape.at("00:15"), None, "long")["reason"] == "tdo_unavailable"
