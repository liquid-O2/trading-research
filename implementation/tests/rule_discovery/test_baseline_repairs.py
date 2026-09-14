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
from trading_research.research.method_pack.historical_auction_scanners import scan_keani, scan_saint
from trading_research.research.method_pack.historical_flow import local_observations, scan_sires, scan_microbalance
from trading_research.research.method_pack.historical_price_scanners import scan_green_failure, scan_green_vwap, scan_jumbo
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
    scan_jumbo_repaired,
    scan_keani_repaired,
    scan_microbalance_repaired,
    scan_saint_repaired,
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
    row = _row("GB-SCALP", "bearish_small_scalp", "trading_research.research.method_pack.historical_process_scanners:scan_scalp")
    assert row["coverage_id"] not in {cid for item in REPAIRS.values() for cid in item["branch_ids"]}
    native = scan_branch(m, row)
    repaired = scan_branch_repaired(m, row)
    assert repaired["baseline_version"] == "B0"
    left = {key: value for key, value in repaired.items() if key != "baseline_version"}
    assert left == native


def test_repairs_registry_covers_named_defects():
    assert set(REPAIRS) == {"D1", "P4", "P1", "P6", "P2", "C1", "C2", "C3", "C4", "C5", "C7"}
    assert REPAIRS["D1"]["fixture"] == "repro_d1.py"
    assert REPAIRS["P4"]["fixture"] == "f4_green_failure_empty_path.py"
    assert REPAIRS["P1"]["fixture"] == "f7_previous_chunk_skips_empty.py"
    assert REPAIRS["P6"]["fixture"] == "f3_kg1_reference_collapse.py"
    assert REPAIRS["P2"]["fixture"] == "f2_absent_empty_interval.py"
    assert "GB-VWAP:branch:source_long" in REPAIRS["D1"]["branch_ids"]
    assert "SIRES:branch:kg1_retest" in REPAIRS["P6"]["branch_ids"]
    assert "GB-FAIL:branch:nyam_box" in REPAIRS["P4"]["branch_ids"]
    assert "GB-FAIL:branch:mss_fvg_refinement" in REPAIRS["P4"]["branch_ids"]
    assert REPAIRS["C1"]["fixture"] == "f1_judas_reversal_sweep_window.py"
    assert REPAIRS["C2"]["fixture"] == "f2_single_breakout_action_window.py"
    assert REPAIRS["C3"]["fixture"] == "f3_gbfail_five_minute_reclaim_window.py"
    assert REPAIRS["C4"]["fixture"] == "f4_keani_rejection_level.py"
    assert REPAIRS["C5"]["fixture"] == "f6_microbalance_thesis_direction.py"
    assert REPAIRS["C7"]["fixture"] == "f7_constant_operand_census.py"
    assert "JJ-TBR:branch:judas_reversal" in REPAIRS["C1"]["branch_ids"]
    assert "JJ-TBR:branch:single_extended" in REPAIRS["C2"]["branch_ids"]
    assert "GB-FAIL:branch:nyam_box" in REPAIRS["C3"]["branch_ids"]
    assert "KEANI-OPEN-ABOVE-VALUE:branch:source_long" in REPAIRS["C4"]["branch_ids"]
    assert "SIRES:branch:microbalance_break" in REPAIRS["C5"]["branch_ids"]
    assert "GB-FAIL:branch:nyam_box" in REPAIRS["C7"]["branch_ids"]


def _at(text):
    return clock(DAY, text)


def _stage_details(episode, name):
    for stage in episode.get("stages") or []:
        if stage["stage"] == name:
            return stage.get("details") or {}
    return {}


class _NoPriorMarket(Market):
    def prior(self, kind="day"):
        return {
            "kind": kind,
            "sessions": [],
            "omissions": [{"reason": "fixture: no prior session supplied"}],
            "scope_complete": False,
            "range": None,
        }


def _judas_session(sweep_text):
    ev = []
    at = START
    while at < END:
        ev.append(raw(at, 100))
        at += MINUTE
    ev += [raw(_at("07:00"), 101.0), raw(_at("08:00"), 99.0)]
    s = _at(sweep_text)
    ev += [raw(s + 1, 101.5), raw(s + 2, 101.75)]
    for k in range(1, 9):
        ev.append(raw(s + k * 30 * SECOND, D("100.5") - D(".25") * k))
    return ev


def test_c1_frozen_misses_0935_sweep_repaired_accepts_it():
    source = Market(_judas_session("09:35"))
    admissible = Market(_judas_session("09:42"))
    frozen_source = scan_jumbo(source, "judas_reversal")
    frozen_ok = scan_jumbo(admissible, "judas_reversal")
    repaired_source = scan_jumbo_repaired(source, "judas_reversal")
    repaired_ok = scan_jumbo_repaired(admissible, "judas_reversal")
    assert frozen_source["N_observed"] == 0
    assert frozen_ok["N_observed"] == 2
    assert repaired_source["N_observed"] == 2
    assert repaired_ok["N_observed"] == 2
    for episode in repaired_source["episodes"]:
        assert episode["values"]["sweep_at"] is not None
        assert _at("09:30") <= episode["values"]["sweep_at"] < _at("09:40")
        assert episode["values"]["source_time_window"] is True
        assert _stage_details(episode, "contact")["sweep_in_reversal_window"] is False
    for episode in repaired_ok["episodes"]:
        assert _at("09:40") <= episode["values"]["sweep_at"] < _at("09:50")
        assert _stage_details(episode, "contact")["sweep_in_reversal_window"] is True


def _c2_session():
    ev = []
    for t in range(_at("06:00"), _at("09:00"), 60 * SECOND):
        ev.append(raw(t, 101.0 if (t // (60 * SECOND)) % 2 else 99.0))
    ev += [raw(t, 101.5) for t in range(_at("09:00"), _at("16:00"), 60 * SECOND)]
    ev += [raw(_at("14:00") + i, 100.0) for i in range(1, 4)]
    return Market(ev)


def test_c2_frozen_keeps_afternoon_eq_repaired_excludes_after_1000():
    m = _c2_session()
    for branch in ("single_extended", "single_purged", "internal_rotation"):
        frozen = scan_jumbo(m, branch)
        repaired = scan_jumbo_repaired(m, branch)
        assert frozen["N_observed"] > 0
        assert any(
            episode["values"]["touch_at"] is not None and episode["values"]["touch_at"] >= _at("10:00")
            for episode in frozen["episodes"]
        )
        assert repaired["N_observed"] == 0 or all(
            episode["values"]["touch_at"] is None or episode["values"]["touch_at"] < _at("10:00")
            for episode in repaired["episodes"]
        )


def _gbfail_session(reclaim_in_sweep_candle):
    ev = [raw(t, 100.0) for t in range(_at("06:00"), _at("09:00"), 60 * SECOND)]
    for t in range(_at("09:00"), _at("10:00"), 60 * SECOND):
        ev.append(raw(t, 101.0 if (t // (60 * SECOND)) % 2 else 99.0))
    ev += [raw(t, 100.0) for t in range(_at("10:10"), _at("16:00"), 60 * SECOND)]
    ev += [raw(_at("10:01"), 102.0), raw(_at("10:02"), 102.5)]
    if reclaim_in_sweep_candle:
        ev += [raw(_at("10:03"), 100.0), raw(_at("10:04"), 100.0)]
        ev += [raw(t, 100.0) for t in range(_at("10:05"), _at("10:10"), 60 * SECOND)]
    else:
        ev += [raw(t, 101.5) for t in range(_at("10:03"), _at("10:05"), 60 * SECOND)]
        ev += [raw(t, 100.0) for t in range(_at("10:05"), _at("10:10"), 60 * SECOND)]
    return Market(ev)


def _short_episode(document):
    return next(episode for episode in document["episodes"] if episode["side"] == "short")


def test_c3_frozen_reads_sweep_candle_repaired_takes_next_reclaim():
    later = _gbfail_session(False)
    inside = _gbfail_session(True)
    frozen_later = _short_episode(scan_green_failure(later, "nyam_box"))
    repaired_later = _short_episode(scan_green_failure_repaired(later, "nyam_box"))
    frozen_inside = _short_episode(scan_green_failure(inside, "nyam_box"))
    repaired_inside = _short_episode(scan_green_failure_repaired(inside, "nyam_box"))
    assert frozen_later["research_verdict"] == "fail"
    assert D(str(frozen_later["values"]["confirm_close"])) == D("101.5")
    assert frozen_inside["research_verdict"] == "pass"
    assert D(str(frozen_inside["values"]["confirm_close"])) == D("100.0")
    assert D(str(repaired_later["values"]["confirm_close"])) == D("100.0")
    assert _stage_details(repaired_later, "five_minute_reclaim")["confirm_bar_offset"] == 1
    assert repaired_later["values"]["confirm_at"] > frozen_later["values"]["confirm_at"]
    assert repaired_later["research_verdict"] == "pass"
    assert D(str(repaired_inside["values"]["confirm_close"])) == D("100.0")
    assert _stage_details(repaired_inside, "five_minute_reclaim")["confirm_bar_offset"] == 0
    assert repaired_inside["research_verdict"] == "pass"


def _keani_session(dip=None):
    bell = [
        (101.5, 20), (101.75, 40), (102.0, 80), (102.25, 120), (102.5, 160), (102.75, 200), (103.0, 240),
        (103.25, 200), (103.5, 160), (103.75, 120), (104.0, 80), (104.25, 40), (104.5, 20),
    ]
    apx = [99.75, 100.0, 100.0, 100.25]
    ev = [raw(t, 100.0) for t in range(_at("06:00"), _at("09:30"), 60 * SECOND)]
    for i, t in enumerate(range(_at("09:30"), _at("10:00"), 10 * SECOND)):
        ev.append(raw(t, apx[i % 4], size=2))
    for i, (px, sz) in enumerate(bell):
        ev.append(raw(_at("10:00") + i * 60 * SECOND, px, size=sz))
    for t in range(_at("10:13"), _at("10:31"), 60 * SECOND):
        ev.append(raw(t, 104.75, size=1))
    if dip is not None:
        ev += [raw(_at("10:31") + 1, 104.75), raw(_at("10:31") + 2, D(str(dip))), raw(_at("10:31") + 3, 105.0)]
    for t in range(_at("10:32"), _at("16:00"), 60 * SECOND):
        ev.append(raw(t, 105.25, size=1))
    return _NoPriorMarket(ev)


def test_c4_frozen_needs_val_repaired_accepts_developing_poc():
    profile = _keani_session().profile(_at("09:30"), _at("10:31"))
    poc, val = profile["poc"], profile["val"]
    frozen_poc = scan_keani(_keani_session(float(poc)), "source_long")["episodes"][0]
    frozen_val = scan_keani(_keani_session(float(val)), "source_long")["episodes"][0]
    repaired_poc = scan_keani_repaired(_keani_session(float(poc)), "source_long")["episodes"][0]
    assert frozen_poc["values"]["source_rejection_observed"] is False
    assert frozen_val["values"]["source_rejection_observed"] is True
    assert repaired_poc["values"]["source_rejection_observed"] is True
    assert repaired_poc["geometry"]["rejection_level"] == "developing_poc"
    assert _stage_details(repaired_poc, "developing_value_rejection")["rejection_level"] == "developing_poc"


def _balance(identity, lo, hi, start, end):
    return {
        "id": identity,
        "low": D(str(lo)),
        "high": D(str(hi)),
        "width": D(str(hi)) - D(str(lo)),
        "start": start,
        "end": end,
        "known_at": end,
        "pivots": [{"id": identity + ":p%d" % i} for i in range(4)],
        "selection": "A2-BALANCE",
    }


def _microbalance_events():
    ev = [raw(t, 100.0) for t in range(_at("06:00"), _at("10:00"), 60 * SECOND)]
    ev += [raw(_at("10:00") + i * SECOND, 102.0) for i in range(5)]
    ev += [raw(t, 102.0) for t in range(_at("10:01"), _at("10:30"), 60 * SECOND)]
    ev += [raw(_at("10:30") + i * SECOND, 97.0) for i in range(5)]
    ev += [raw(t, 97.0) for t in range(_at("10:31"), _at("16:00"), 60 * SECOND)]
    return ev


def test_c5_frozen_both_directions_true_repaired_uses_larger_balance_half():
    ev = _microbalance_events()
    htf = _balance("balance:htf", 90, 110, _at("06:00"), _at("08:00"))
    centered = _balance("balance:micro", 99, 101, _at("08:30"), _at("09:00"))
    frozen = scan_microbalance(Market(ev), "microbalance_break", [htf, centered])
    repaired_centered = scan_microbalance_repaired(Market(ev), "microbalance_break", [htf, centered])
    assert {e["side"]: e["values"]["breakout_in_thesis_direction"] for e in frozen["episodes"]} == {"long": True, "short": True}
    assert all(e["values"]["breakout_in_thesis_direction"] is None for e in repaired_centered["episodes"])
    lower = _balance("balance:micro-low", 98, 99, _at("08:30"), _at("09:00"))
    # Lower-half micro 98-99 (mid 98.5 of HTF 90-110) is broken long by 102 and short by 97.
    repaired_lower = scan_microbalance_repaired(Market(ev), "microbalance_break", [htf, lower])
    by_side = {e["side"]: e["values"]["breakout_in_thesis_direction"] for e in repaired_lower["episodes"]}
    assert by_side.get("long") is True
    assert by_side.get("short") is False


def _c7_kind(episode, operand):
    kinds = _stage_details(episode, "baseline_repair").get("literal_operand_kind")
    if isinstance(kinds, dict):
        return kinds.get(operand)
    return kinds


def _saint_pass_session():
    """Overnight HTF 5-minute balance, narrower LTF 1-minute balance, then a
    long continuation: break the LTF high, later same-boundary retest, two
    buy-body control minutes. Coverage after the break stays above the hold
    line so minute fills do not invalidate same_boundary_retest_held."""
    htf = [104, 105, 110, 106, 104, 100, 103, 106, 110.25, 106, 103, 100.25, 103, 105]
    ltf = [102, 102.5, 104, 103, 102, 100.5, 102, 103, 104.1, 103, 102, 100.6, 102, 103]
    ev = []
    at = START
    while at < _at("09:40"):
        ev.append(raw(at, 103.0))
        at += MINUTE
    while at < END:
        ev.append(raw(at, 105.5))
        at += MINUTE
    htf_start = _at("06:00")
    for i, px in enumerate(htf):
        ev.append(raw(htf_start + i * 5 * MINUTE + SECOND, px, size=4))
    ltf_start = _at("08:00")
    for i, px in enumerate(ltf):
        ev.append(raw(ltf_start + i * MINUTE + 2 * SECOND, px, size=3))
    ev += [
        raw(_at("09:40") + 10 * SECOND, 103.5, size=2, side="B"),
        raw(_at("09:40") + 40 * SECOND, 105.5, size=8, side="B"),
        raw(_at("09:44") + 10 * SECOND, 104.1, size=3, side="A"),
        raw(_at("09:44") + 40 * SECOND, 104.2, size=2, side="B"),
        raw(_at("09:45") + 10 * SECOND, 104.3, size=2, side="B"),
        raw(_at("09:45") + 40 * SECOND, 105.6, size=8, side="B"),
        raw(_at("09:46") + 10 * SECOND, 104.8, size=2, side="B"),
        raw(_at("09:46") + 40 * SECOND, 105.8, size=8, side="B"),
    ]
    return Market(ev)


def test_c7_saint_pass_becomes_unknown():
    m = _saint_pass_session()
    frozen = scan_saint(m, "continuation_retest")
    repaired = scan_saint_repaired(m, "continuation_retest")
    frozen_passes = [e for e in frozen["episodes"] if e["research_verdict"] == "pass"]
    assert frozen_passes, (frozen["N_observed"], [e["research_verdict"] for e in frozen["episodes"]], [e.get("failed") for e in frozen["episodes"]], [e.get("unknown") for e in frozen["episodes"]])
    repaired_by_id = {e["candidate_id"]: e for e in repaired["episodes"]}
    for episode in frozen_passes:
        corrected = repaired_by_id[episode["candidate_id"]]
        assert episode["values"]["arrival_read_recorded"] is True
        assert corrected["values"]["arrival_read_recorded"] is None
        assert corrected["values"]["alignment_ok"] is None
        assert corrected["values"]["profile_allows_trade"] is None
        assert corrected["research_verdict"] == "unknown"
        unevaluated = _stage_details(corrected, "baseline_repair")["unevaluated_operand"]
        assert "arrival_read_recorded" in unevaluated
        assert "alignment_ok" in unevaluated
        assert "profile_allows_trade" in unevaluated


def test_c7_by_construction_keeps_frozen_value_and_kind():
    gb = _gbfail_session(True)
    frozen_gb = _short_episode(scan_green_failure(gb, "nyam_box"))
    repaired_gb = _short_episode(scan_green_failure_repaired(gb, "nyam_box"))
    assert repaired_gb["values"]["source_session_allowed"] is True
    assert repaired_gb["values"]["source_session_allowed"] == frozen_gb["values"]["source_session_allowed"]
    assert _c7_kind(repaired_gb, "source_session_allowed") == "by_construction"
    assert repaired_gb["values"]["bias_recorded"] == frozen_gb["values"]["bias_recorded"]
    assert _stage_details(repaired_gb, "baseline_repair")["context_direction_unevaluated"] is True

    outbound = Market(_judas_session("09:35"))
    frozen_out = scan_jumbo(outbound, "judas_outbound")["episodes"]
    repaired_out = scan_jumbo_repaired(outbound, "judas_outbound")["episodes"]
    assert frozen_out and repaired_out
    assert repaired_out[0]["values"]["exit_window_recorded"] is True
    assert repaired_out[0]["values"]["exit_window_recorded"] == frozen_out[0]["values"]["exit_window_recorded"]
    assert repaired_out[0]["values"]["location_touched"] is True
    assert _c7_kind(repaired_out[0], "exit_window_recorded") == "by_construction"
    assert _c7_kind(repaired_out[0], "location_touched") == "by_construction"

    other = scan_jumbo_repaired(outbound, "other_session")
    if other["episodes"]:
        assert other["episodes"][0]["values"]["source_clock_verified"] is True
        assert other["episodes"][0]["values"]["source_case_verified"] is True
        assert _c7_kind(other["episodes"][0], "source_clock_verified") == "by_construction"
        assert _c7_kind(other["episodes"][0], "source_case_verified") == "by_construction"

    ev = _microbalance_events()
    htf = _balance("balance:htf", 90, 110, _at("06:00"), _at("08:00"))
    lower = _balance("balance:micro-low", 98, 99, _at("08:30"), _at("09:00"))
    frozen_mb = scan_microbalance(Market(ev), "microbalance_break", [htf, lower])
    repaired_mb = scan_microbalance_repaired(Market(ev), "microbalance_break", [htf, lower])
    frozen_long = next(e for e in frozen_mb["episodes"] if e["side"] == "long")
    repaired_long = next(e for e in repaired_mb["episodes"] if e["side"] == "long")
    assert repaired_long["values"]["microbalance_frozen"] is True
    assert repaired_long["values"]["microbalance_frozen"] == frozen_long["values"]["microbalance_frozen"]
    assert _c7_kind(repaired_long, "microbalance_frozen") == "by_construction"

    vwap = Market(_covered([raw(clock(DAY, "15:55") + k * MINUTE + SECOND, 105) for k in range(5)]))
    frozen_vw = scan_green_vwap(vwap, "asia_london_vwap_return")["episodes"][0]
    repaired_vw = scan_green_vwap_repaired(vwap, "asia_london_vwap_return")["episodes"][0]
    assert frozen_vw["values"]["vwap_reset_verified"] is True
    assert repaired_vw["values"]["vwap_reset_verified"] is True
    assert _c7_kind(repaired_vw, "vwap_reset_verified") == "operational_assumption"
    assert _stage_details(repaired_vw, "baseline_repair")["assumption_id"] == "A2-GB-CLOCK"


def test_c7_structural_class_keeps_literal_false_and_records_it():
    m = _gbfail_session(True)
    frozen = _short_episode(scan_green_failure(m, "nyam_box"))
    repaired = _short_episode(scan_green_failure_repaired(m, "nyam_box"))
    assert frozen["research_verdict"] == "pass"
    assert frozen["values"]["pocket_required"] is False
    assert frozen["values"]["retracement_entry"] is False
    assert repaired["values"]["pocket_required"] is False
    assert repaired["values"]["retracement_entry"] is False
    recorded = _stage_details(repaired, "baseline_repair")["structural_not_required"]
    assert "pocket_required" in recorded
    assert "retracement_entry" in recorded
    assert repaired["research_verdict"] == "pass"


def test_c7_gb_fail_and_sires_passes_preserved():
    m = _gbfail_session(True)
    frozen = _short_episode(scan_green_failure(m, "nyam_box"))
    repaired = _short_episode(scan_green_failure_repaired(m, "nyam_box"))
    assert frozen["research_verdict"] == "pass"
    assert repaired["research_verdict"] == "pass"

    ev = _microbalance_events()
    htf = _balance("balance:htf", 90, 110, _at("06:00"), _at("08:00"))
    lower = _balance("balance:micro-low", 98, 99, _at("08:30"), _at("09:00"))
    frozen_mb = scan_microbalance(Market(ev), "microbalance_break", [htf, lower])
    repaired_mb = scan_microbalance_repaired(Market(ev), "microbalance_break", [htf, lower])
    frozen_long = next(e for e in frozen_mb["episodes"] if e["side"] == "long")
    repaired_long = next(e for e in repaired_mb["episodes"] if e["side"] == "long")
    repaired_short = next(e for e in repaired_mb["episodes"] if e["side"] == "short")
    assert frozen_long["research_verdict"] == "pass"
    assert repaired_long["research_verdict"] == "pass"
    assert repaired_short["values"]["breakout_in_thesis_direction"] is False
    assert repaired_short["research_verdict"] == "fail"


def test_c3_mss_fvg_emits_when_parent_pass_returns():
    inside = _gbfail_session(True)
    later = _gbfail_session(False)
    frozen_inside = scan_green_failure(inside, "mss_fvg_refinement")
    repaired_inside = scan_green_failure_repaired(inside, "mss_fvg_refinement")
    frozen_later = scan_green_failure(later, "mss_fvg_refinement")
    repaired_later = scan_green_failure_repaired(later, "mss_fvg_refinement")
    assert any(e["research_verdict"] == "pass" for e in scan_green_failure_repaired(inside, "nyam_box")["episodes"])
    assert repaired_inside["N_observed"] == frozen_inside["N_observed"] == 1
    assert frozen_later["N_observed"] == 0
    assert any(e["research_verdict"] == "pass" for e in scan_green_failure_repaired(later, "nyam_box")["episodes"])
    assert repaired_later["N_observed"] == 1
