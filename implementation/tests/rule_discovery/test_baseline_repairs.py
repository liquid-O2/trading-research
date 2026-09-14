"""B0 vs B0.1 repairs. Fixture inputs are ported from the 2026-09-14 reproductions."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal as D

import pytest

from trading_research.research.method_pack.adapters import normalize_mbp1_row
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.event_time import aggregate_events, VERSION, CONTRACT, MINUTE, SECOND
from trading_research.research.method_pack.historical_assembly import absent
from trading_research.research.method_pack.historical_auction_scanners import _control_absence
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.historical_flow import local_observations, scan_sires
from trading_research.research.method_pack.historical_price_scanners import scan_green_failure, scan_green_vwap
from trading_research.research.method_pack.native_discovery import scan_branch
from trading_research.research.method_pack.native_resolution import file_digest
from trading_research.research.rule_discovery.baseline_repairs import (
    BASELINE_REPAIR_VERSION,
    REPAIRS,
    absent_repaired,
    _control_absence_repaired,
    local_observations_repaired,
    scan_branch_repaired,
    scan_green_failure_repaired,
    scan_green_vwap_repaired,
    scan_sires_repaired,
)

DAY = date(2026, 1, 15)
START = clock(DAY - timedelta(days=1), "18:00")
END = clock(DAY, "16:00")
TOUCH = clock(DAY, "10:00")
BAND = [D("99.75"), D("100.25")]


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
            "bid_px": "100",
            "ask_px": "100.25",
            "bid_sz": bid_size,
            "ask_sz": 10,
            **({} if ts_recv is None else {"ts_recv": ts_recv}),
            **kw,
        },
        source_file="repro.parquet",
        source_row=index,
    )
    row["event_id"] = f"{row['source_file']}:{row['source_row']}"
    return row


class Market(HistoricalFeatures):
    def __init__(self, events, records=None):
        events = sorted(events, key=lambda r: r["event_ns"])
        for i, row in enumerate(events):
            row["source_row"] = i
            row["event_id"] = f"repro.parquet:{i}"
        self.events = events
        doc = aggregate_events(events, START, END, 17)
        doc.update(
            schema=VERSION,
            contract_sha256=content_hash(CONTRACT),
            instrument_id=17,
            start_ns=START,
            end_ns=END,
            input_sha256=content_hash(doc),
            plan={"unowned_intervals": []},
        )
        super().__init__(DAY, document=doc, records=records)

    def local(self, start, end, *, book=False):
        return [r for r in self.events if start <= r["event_ns"] < end and (book or r["action"] == "T")]


def _covered(extra=()):
    ev = []
    at = START
    while at < END:
        ev.append(raw(at, 100))
        at += MINUTE
    ev.extend(extra)
    return ev


def _row(method, branch, scanner):
    return {
        "coverage_id": f"{method}:branch:{branch}",
        "method_id": method,
        "branch": branch,
        "extra_unit": False,
        "scanner": scanner,
        "source_definition": {"citation": "test", "wiki_path": "test", "operation": "test"},
        "observation_unit": "market_sequence",
        "assumption_ids": [],
    }


def _p1_chunks(fill_quiet_window):
    ev = [raw(START + i * MINUTE, 100) for i in range(5)]
    ev += [raw(TOUCH + 0 * SECOND, 100, 5, "A"), raw(TOUCH + 1 * SECOND, 100, 5, "A")]
    if fill_quiet_window:
        ev += [raw(TOUCH + 6 * SECOND, 150, 1, "B")]
    ev += [raw(TOUCH + 10 * SECOND, 100, 2, "A"), raw(TOUCH + 11 * SECOND, 100, 2, "A")]
    return Market(ev)


def _chunk_rows(obs):
    return [(int((c["start"] - TOUCH) / SECOND), c["opposing"], c["effort"]) for c in obs["chunks"]]


def test_p1_frozen_skips_empty_window_repaired_records_it():
    quiet = _p1_chunks(False)
    filled = _p1_chunks(True)
    frozen_quiet = _chunk_rows(local_observations(quiet, TOUCH, BAND, "long", book=False))
    frozen_filled = _chunk_rows(local_observations(filled, TOUCH, BAND, "long", book=False))
    assert frozen_quiet == [(0, 10, True), (10, 4, False)]
    assert frozen_filled[0] == (0, 10, True)
    assert frozen_filled[-1] == (10, 4, True)

    repaired_quiet = local_observations_repaired(quiet, TOUCH, BAND, "long", book=False)
    repaired_filled = local_observations_repaired(filled, TOUCH, BAND, "long", book=False)
    quiet_rows = _chunk_rows(repaired_quiet)
    filled_rows = _chunk_rows(repaired_filled)

    def effort_at(rows, offset):
        matched = [effort for off, _opp, effort in rows if off == offset]
        assert matched, rows
        return matched[0]

    assert (5, 0, False) in quiet_rows
    assert effort_at(quiet_rows, 10) is True
    assert effort_at(filled_rows, 10) is True
    assert effort_at(quiet_rows, 10) == effort_at(filled_rows, 10)


def test_p4_frozen_raises_on_empty_path_repaired_records_unknown():
    extra = [raw(clock(DAY, "10:04") + 30 * SECOND, 101, ts_recv=clock(DAY, "10:06"))]
    m = Market(_covered(extra))
    with pytest.raises(ValueError, match="empty"):
        scan_green_failure(m, "nyam_box")
    out = scan_green_failure_repaired(m, "nyam_box")
    assert any(item.get("kind") == "availability" for item in out["omissions"])
    assert out["episodes"]
    assert all(episode["research_verdict"] == "unknown" for episode in out["episodes"])
    assert all(episode["values"]["sweep_high"] is None for episode in out["episodes"])


def test_scan_branch_repaired_never_raises_where_f4_raised():
    extra = [raw(clock(DAY, "10:04") + 30 * SECOND, 101, ts_recv=clock(DAY, "10:06"))]
    m = Market(_covered(extra))
    with pytest.raises(ValueError, match="empty"):
        scan_green_failure(m, "nyam_box")
    row = _row("GB-FAIL", "nyam_box", "trading_research.research.method_pack.historical_price_scanners:scan_green_failure")
    out = scan_branch_repaired(m, row)
    assert out["baseline_version"] == BASELINE_REPAIR_VERSION
    assert out["coverage_id"] == "GB-FAIL:branch:nyam_box"
    assert any(item.get("kind") == "availability" for item in out["omissions"])
    assert out["episodes"]
    assert all(episode["research_verdict"] == "unknown" for episode in out["episodes"])


def test_p6_frozen_collapses_kg1_repaired_enumerates_each_reference(tmp_path):
    levels = [
        {"id": "kg1-a", "known_at": clock(DAY, "09:00"), "instrument_id": 17, "low": "100", "high": "100.5"},
        {"id": "kg1-b", "known_at": clock(DAY, "09:00"), "instrument_id": 17, "low": "120", "high": "120.5"},
    ]
    path = tmp_path / "kg1.json"
    path.write_text(__import__("json").dumps(levels))
    digest = file_digest(path)
    records = {"kg1": [dict(row, evidence_path=str(path), evidence_sha256=digest) for row in levels]}
    extra = []
    at = START
    while at < END:
        extra.append(raw(at, "100.25"))
        at += MINUTE
    for k in range(40):
        extra.append(raw(clock(DAY, "10:00") + k * MINUTE + SECOND, 150))
    for k in range(40):
        extra.append(raw(clock(DAY, "11:00") + k * MINUTE + SECOND, 120.25))
    m = Market(extra, records=records)
    frozen = scan_sires(m, "kg1_retest")
    repaired = scan_sires_repaired(m, "kg1_retest")
    assert sorted({e["reference_id"] for e in frozen["episodes"]}) == ["kg1-a"]
    # The fixture's 150-print minutes still span [120,120.5] because of the 100.25
    # coverage print, so kg1-b's first bar-contact has no exact print. Add an
    # exact 120.25 print at 09:31 so the repaired key can emit kg1-b; frozen
    # still collapses both levels onto kg1-a.
    extra_exact = extra + [raw(clock(DAY, "09:31") + SECOND, 120.25)]
    m2 = Market(extra_exact, records=records)
    frozen2 = scan_sires(m2, "kg1_retest")
    repaired2 = scan_sires_repaired(m2, "kg1_retest")
    assert sorted({e["reference_id"] for e in frozen2["episodes"]}) == ["kg1-a"]
    assert {e["reference_id"] for e in repaired2["episodes"]} >= {"kg1-a", "kg1-b"}


def test_p2_absent_zero_length_and_scan_green_vwap_last_bar():
    m0 = Market([raw(START + i * MINUTE, 100) for i in range(60)])
    t = clock(DAY, "10:00")
    assert m0.coverage(t, t)["observed_scope_complete"] is True
    assert absent(m0, t, t) is False
    assert absent_repaired(m0, t, t) is None

    extra = [raw(clock(DAY, "15:55") + k * MINUTE + SECOND, 105) for k in range(5)]
    m = Market(_covered(extra))
    frozen = scan_green_vwap(m, "asia_london_vwap_return")
    repaired = scan_green_vwap_repaired(m, "asia_london_vwap_return")
    br = frozen["episodes"][0]
    rr = repaired["episodes"][0]
    assert br["values"]["continuation_context"] is False
    assert br["research_verdict"] == "fail"
    assert rr["values"]["continuation_context"] is True
    assert rr["values"]["retest_at"] is None
    assert rr["research_verdict"] == "unknown"


def test_p2_control_absence_zero_length_reconstruct_path():
    class _Zero:
        reconstruct = True

        def bars(self, after, end, *args, **kwargs):
            return []

        def coverage(self, start, end):
            return {"observed_scope_complete": True}

    t = 1609774260000000000
    market = _Zero()
    assert _control_absence(market, t, t, "short") is False
    assert _control_absence_repaired(market, t, t, "short") is None


def test_d1_continuation_context_not_overwritten_by_retest_absence():
    breakout = clock(DAY, "10:00")
    ev = []
    at = START
    while at < END:
        ev.append(raw(at, 105 if at >= breakout else 100))
        at += MINUTE
    for k in range(5):
        ev.append(raw(breakout + k * MINUTE + SECOND, 105))
    m = Market(ev)
    frozen = scan_green_vwap(m, "source_long")
    repaired = scan_green_vwap_repaired(m, "source_long")
    frozen_ep = frozen["episodes"][0]
    repaired_ep = repaired["episodes"][0]
    br = frozen_ep["values"]
    rr = repaired_ep["values"]
    assert br["breakout_close"] > br["asia_high"]
    assert br["breakout_close"] > br["london_high"]
    assert br["retest_at"] is None
    assert br["continuation_context"] is False
    assert frozen_ep["research_verdict"] == "fail"
    assert rr["continuation_context"] is True
    assert rr["retest_at"] is None
    assert repaired_ep["research_verdict"] == "unknown"
    assert repaired_ep["operand_derivations"]["continuation_context"]["operation"] != repaired_ep["operand_derivations"]["retest_at"]["operation"]


def test_p1_flow_episode_repaired_imports_defaultdict():
    m = Market(_covered())
    out = scan_sires_repaired(m, "footprint_confirmed_reaction")
    assert out["branch"] == "footprint_confirmed_reaction"
    assert "episodes" in out


def test_parity_unaffected_branch_matches_native_except_baseline_version():
    m = Market(_covered())
    row = _row("SIRES", "microbalance_break", "trading_research.research.method_pack.historical_flow:scan_sires")
    assert row["coverage_id"] not in {cid for item in REPAIRS.values() for cid in item["branch_ids"]}
    native = scan_branch(m, row)
    repaired = scan_branch_repaired(m, row)
    assert repaired["baseline_version"] == "B0"
    left = {key: value for key, value in repaired.items() if key != "baseline_version"}
    assert left == native


def test_repairs_registry_covers_named_defects():
    assert set(REPAIRS) == {"D1", "P4", "P1", "P6", "P2"}
    assert REPAIRS["D1"]["fixture"] == "repro_d1.py"
    assert REPAIRS["P4"]["fixture"] == "f4_green_failure_empty_path.py"
    assert REPAIRS["P1"]["fixture"] == "f7_previous_chunk_skips_empty.py"
    assert REPAIRS["P6"]["fixture"] == "f3_kg1_reference_collapse.py"
    assert REPAIRS["P2"]["fixture"] == "f2_absent_empty_interval.py"
    assert "GB-VWAP:branch:source_long" in REPAIRS["D1"]["branch_ids"]
    assert "SIRES:branch:kg1_retest" in REPAIRS["P6"]["branch_ids"]
    assert "GB-FAIL:branch:nyam_box" in REPAIRS["P4"]["branch_ids"]
    assert "GB-FAIL:branch:mss_fvg_refinement" in REPAIRS["P4"]["branch_ids"]
