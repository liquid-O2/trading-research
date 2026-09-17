"""Green Bird B0.3: one test per ordered defect of FIDELITY_AUDIT_2026-09-17 2.3.

Every expected value comes from the audit's statement of the source or from a
dated ticket, never from the adapter. The old B0.2 track-file digests and the
month-split clock test are retired: they pinned the behaviour this rebuild
replaces.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import json

import pytest

from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
from trading_research.research.rule_discovery.source_adapters.green_failure import (
    RULES as FAIL_RULES,
    scan_b02 as fail_scan,
)
from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import (
    RULES as VWAP_RULES,
)
from trading_research.research.rule_discovery.source_adapters.trade_selection import select_session_trades

from .fake_market import FakeMarket, bar, flat_series

REPO = Path(__file__).resolve().parents[3]
EXAMPLES = REPO / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"
DAY = date(2026, 8, 20)


def _session(day: date = DAY, *, box_high=105, sweep_to=108, fail_close=99, sweep_at="10:20", after=96):
    """A session whose 09:00-10:00 box high is swept after 10:00 and fails back.

    Shaped after the author's own 2026-08-28 sequence: the box is established
    09:00-10:00, the sweep runs beyond its high after 10:00, and price closes
    back inside.
    """
    rows: list = []
    rows += flat_series(day, "18:00", 120, 100, offset=-1)          # 18:00-20:00
    rows += flat_series(day, "20:00", 60, 100, offset=-1)
    rows += [bar(day, "21:00", 100, 110, 100, 100, offset=-1)]      # Asia high 110
    rows += flat_series(day, "21:01", 179, 100, offset=-1)          # to 00:00
    rows += flat_series(day, "00:00", 120, 100)                     # 00:00-02:00
    rows += [bar(day, "02:00", 100, 100, 90, 100)]                  # London low 90
    rows += flat_series(day, "02:01", 179, 100)                     # to 05:00
    rows += flat_series(day, "05:00", 240, 100)                     # to 09:00
    rows += [bar(day, "09:00", 100, box_high, 95, 100)]             # NY box 95..box_high
    rows += flat_series(day, "09:01", 59, 100)                      # to 10:00
    minutes_to_sweep = (int(sweep_at[:2]) - 10) * 60 + int(sweep_at[3:])
    rows += flat_series(day, "10:00", minutes_to_sweep, 100)
    rows += [bar(day, sweep_at, 100, sweep_to, 99, fail_close)]     # the sweep and its failure
    start_minute = int(sweep_at[:2]) * 60 + int(sweep_at[3:]) + 1
    rows += flat_series(day, f"{start_minute // 60:02d}:{start_minute % 60:02d}", 16 * 60 - start_minute, after)
    return FakeMarket(
        str(day),
        rows,
        prior_day={"id": "pd", "low": Decimal("80"), "high": Decimal("120"), "close": Decimal("100"),
                   "open": Decimal("100"), "known_at": 0, "scope": "cme_session_1800_1600"},
        prior_week={"id": "pw", "low": Decimal("60"), "high": Decimal("140"), "close": Decimal("100"), "known_at": 0},
        prior_sessions=[],
    )


def _refs(market):
    refs, _omissions = gb.session_references(market)
    return {ref["kind"]: ref for ref in refs}


def _passes(market, family="GB-FAIL"):
    document = gb.scan_b02(market, {"family": family, "branch": "all"})
    return document, [ep for ep in document["episodes"] if ep["research_verdict"] == "pass"]


# --------------------------------------------------------------------------- G1


@pytest.mark.parametrize("day", [date(2026, 4, 23), date(2026, 8, 12), date(2026, 9, 15), date(2025, 11, 20)])
def test_g1_one_session_clock_each_in_every_month(day):
    """Audit 2.3 G1: Asia is 20:00-00:00 and London 02:00-05:00 in every month
    of the record; the April-August 20:00-23:00 / 03:00-04:30 variants are
    contradicted by the 2026-04-23 and 08-11/12 charts and the digest's card."""
    assert (gb.asia_box_spec(day)["start"], gb.asia_box_spec(day)["end"]) == ("20:00", "00:00")
    assert (gb.london_box_spec(day)["start"], gb.london_box_spec(day)["end"]) == ("02:00", "05:00")


def test_g1_asia_box_spans_midnight_on_the_tape():
    market = _session()
    asia = _refs(market)["asia_box"]
    assert asia["window"] == [market.at("20:00", -1), market.at("00:00")]
    assert asia["high"] == Decimal("110")  # the 21:00 excursion, inside 20:00-00:00


# --------------------------------------------------------------------------- G2


def test_g2_reference_set_is_the_authors_layout():
    """Audit 2.3 G2: references are the 09:00-10:00 box from 10:00, the
    10:00-11:00 box from 11:00, then each completed hour from its close, the
    session boxes, the True Day Open and the prior day / prior week."""
    market = _session()
    kinds = set(_refs(market))
    assert {"asia_box", "london_box", "ny_box_09_10", "ny_box_10_11", "tdo", "prior_day", "prior_week"} <= kinds
    assert {f"hour_box_{hour:02d}" for hour in range(11, 16)} <= kinds


def test_g2_ny_boxes_go_live_at_their_close_not_before():
    market = _session()
    refs = _refs(market)
    assert refs["ny_box_09_10"]["live_from"] == market.at("10:00")
    assert refs["ny_box_10_11"]["live_from"] == market.at("11:00")


def test_g2_ny_session_extreme_and_the_nwog_entry_branch_are_gone():
    """The 2026-09-15 15:35 long was at the 10:00-11:00 box low, not at an
    invented frozen 09:30-11:00 range; the NWOG is an objective (G7)."""
    assert "ny_session_extreme" not in gb.B02_BRANCHES["GB-FAIL"]
    assert "nwog" not in gb.B02_BRANCHES["GB-FAIL"]
    assert ("GB-FAIL", "ny_session_extreme") not in gb.SCANNERS
    assert ("GB-FAIL", "nwog") not in gb.SCANNERS


# --------------------------------------------------------------------------- G3


def test_g3_reference_stays_live_until_swept_with_no_entry_window_filter():
    """Audit 2.3 G3: the entry-window list 00:00-02:00 / 03:00-06:00 /
    09:30-11:30 / 12:45-14:30 / 20:00-23:00 has no source. The 2026-08-27 13:00
    and 2026-09-15 15:35 tickets both sit outside it."""
    assert not hasattr(gb, "in_entry_windows")
    market = _session(sweep_at="14:20")
    _document, passes = _passes(market)
    late = [ep for ep in passes if ep["decision_at"] >= market.at("14:00")]
    assert late, "a 14:20 sweep-and-fail must still be an episode"


def test_g3_five_minute_close_back_through_is_the_trigger():
    """GB p.3: 'I wait for the 5 min close back below the PDL after sweeping
    above it'."""
    market = _session()
    cycles = gb.sweep_cycles(
        market, level=Decimal("105"), side="short",
        begin=market.at("10:00"), end=market.at("16:00"),
        box_low=Decimal("95"), box_high=Decimal("105"),
    )
    assert cycles and cycles[0]["status"] == "failed"
    assert cycles[0]["extreme"] == Decimal("108")
    # the failure is the five-minute bar that closes back through the level
    assert cycles[0]["fail"]["C"] <= Decimal("105")
    assert cycles[0]["fail"]["start"] == market.at("10:20")
    assert cycles[0]["inside_reference"] is True


def test_g3_a_breakout_that_holds_is_not_a_failure():
    """'Break out and hold? I'm looking for continuation.' -- the negative
    control for the sweep-and-fail trigger."""
    market = _session(sweep_to=108, fail_close=107, after=107)
    cycles = gb.sweep_cycles(
        market, level=Decimal("105"), side="short",
        begin=market.at("10:00"), end=market.at("16:00"),
        box_low=Decimal("95"), box_high=Decimal("105"),
    )
    assert cycles and cycles[0]["status"] == "held"


# --------------------------------------------------------------------------- G4


def test_g4_cash_open_objective_is_the_pre_open_retracement():
    """GB p.3: '9:30am manipulation below, reclaim, enter for longs targeting
    retracement into discount, stops at lows'. ``open + 0.5 x sweep depth`` is
    not in the source."""
    market = _session()
    episodes = gb._scan_cash_open(market, *_objectives(market))
    assert episodes
    for episode in episodes:
        first = episode["geometry"]["first_objective"]
        assert first is not None
        stage = next(row for row in episode["stages"] if row["stage"] == "objective")
        assert stage["operands"]["rule"] == "retracement of the pre-open range, then its extreme"


def _objectives(market):
    refs, _omissions = gb.session_references(market)
    return refs, gb.objective_levels(market, refs)


# --------------------------------------------------------------------------- G6


def test_g6_stop_is_beyond_the_sweep_wick_not_one_tick():
    """Audit 2.3 G6: the author's stops are structural, 17-50 points, beyond
    the wick; 2026-09-03 stops on the sweep extreme, 2026-08-31 22 points past
    it. One tick beyond the swept level is not the rule."""
    market = _session()
    _document, passes = _passes(market)
    shorts = [ep for ep in passes if ep["side"] == "short" and ep["values"]["reference_kind"] == "ny_box_09_10"]
    assert shorts
    for episode in shorts:
        assert Decimal(str(episode["geometry"]["stop"])) == Decimal("108") + gb.SWEEP_STOP_BUFFER
        assert Decimal(str(episode["geometry"]["stop"])) - Decimal("105") > Decimal("0.25")


def test_g6_quantity_is_derived_from_the_stop_at_750():
    """Every ticket prints 'Amount: 750' with the quantity derived from the
    stop (4.95 at 25.25 points on 2026-09-15)."""
    assert gb.RISK_DOLLARS == Decimal("750")
    assert gb.derived_quantity(Decimal("25.25")) == Decimal("750") / (Decimal("25.25") * Decimal("2"))
    assert gb.derived_quantity(Decimal("0")) is None


# --------------------------------------------------------------------------- G7


def test_g7_nwog_is_an_objective_rung_not_an_entry_reference():
    market = _session()
    refs, objectives = _objectives(market)
    assert all(ref["kind"] != "nwog" for ref in refs)
    assert "GB-NWOG-objective-only" in gb.RULES


# --------------------------------------------------------------------------- G8


def test_g8_pocket_is_the_impulse_that_made_the_session_extreme_both_directions():
    """Audit 2.3 G8: the leg is the author's measured impulse, either
    direction; the code's single 18:00-00:00 down leg is not the rule."""
    market = _session()
    leg = gb._impulse_leg(market, end_ns=market.at("11:00"))
    assert leg is not None and leg["kind"] in {"up", "down"}
    pocket_up = gb.pocket_in_leg_direction(Decimal("100"), Decimal("200"), "long")
    assert pocket_up == (Decimal("200") - Decimal("61.8"), Decimal("150"))
    pocket_down = gb.pocket_in_leg_direction(Decimal("100"), Decimal("200"), "short")
    assert pocket_down == (Decimal("150"), Decimal("100") + Decimal("61.8"))


def test_g8_pocket_stop_is_beyond_the_zone_not_on_its_50_line():
    market = _session()
    refs, objectives = _objectives(market)
    episodes = gb._scan_golden_pocket(market, refs, objectives, family="GB-FAIL", branch="golden_pocket")
    for episode in episodes:
        stop = episode["geometry"]["stop"]
        if stop is None:
            continue
        pocket = [Decimal(str(value)) for value in episode["values"]["pocket"]]
        side = episode["side"]
        far = gb.far_edge((pocket[0], pocket[1]), side)
        assert Decimal(str(stop)) == (far - gb.SWEEP_STOP_BUFFER if side == "long" else far + gb.SWEEP_STOP_BUFFER)
        near = gb.near_edge((pocket[0], pocket[1]), side)
        assert Decimal(str(stop)) != near


# --------------------------------------------------------------------------- G9


def test_g9_break_and_hold_retest_continuation_exists():
    """Audit 2.3 G9: 'Break out and hold ... pullback ... enter with the move'
    (2026-09-15); 2026-09-10 long on the retest of the broken 09:00-10:00 high."""
    assert "continuation" in gb.B02_BRANCHES["GB-FAIL"]
    assert gb.PLAY_OF_BRANCH["continuation"] == "break_and_hold"
    assert gb.CONTINUATION_HOLD_BARS >= 2


# --------------------------------------------------------------------------- G10


def test_g10_bias_is_recorded_and_never_filters_the_baseline():
    """Audit 2.3 G10: F07's 'prior close versus midpoint + 9-10 box direction'
    is not the author's context; the family baseline is unfiltered."""
    market = _session()
    document, passes = _passes(market)
    assert document["bias"]["filtered"] is False
    assert all(episode["values"]["bias_recorded"] for episode in passes)
    assert all("bias_compatible" not in (episode.get("failed") or []) for episode in passes)


# --------------------------------------------------------------------------- G11


def test_g11_selection_is_at_most_three_entries_and_stops_after_a_full_objective():
    """Audit 2.3 G11 and 2.1 'Frequency': one to three trades a day, 'One
    opportunity at a time', 'Two trades were enough'."""
    market = _session()
    document, _passes_ = _passes(market)
    assert document["selection"]["n_entries"] <= 3

    def episode(decision_at, entry, stop, target, branch="nyam_box"):
        return {
            "research_verdict": "pass",
            "branch": branch,
            "side": "long",
            "decision_at": decision_at,
            "values": {"cycle": decision_at},
            "reference": {"id": f"r{decision_at}"},
            "geometry": {"entry": Decimal(entry), "stop": Decimal(stop), "target": Decimal(target)},
        }

    day = DAY
    bars = [bar(day, "10:00", 100, 130, 100, 130), bar(day, "10:01", 130, 130, 130, 130)]
    first = episode(bars[0]["start"] - 1, "100", "90", "120")
    later = [episode(bars[0]["start"] + n, "100", "90", "120") for n in range(1, 5)]
    result = select_session_trades([first] + later, bars=bars, clock=None, max_entries=3)
    assert result["n_entries"] == 1
    assert result["entries"][0]["outcome"] == "target"
    assert result["skipped"]["after_objective"] == 4


# --------------------------------------------------------------------------- G12


def test_g12_partial_ladder_is_about_25_points():
    """Audit 2.3 G12: the author's rungs are 13.75-32.25 apart; 15 was the old
    baseline."""
    assert gb.LADDER_SPACING == Decimal("25")
    rungs = gb.limit_ladder(Decimal("100"), Decimal("200"), "long")
    gaps = [rungs[i + 1] - rungs[i] for i in range(len(rungs) - 2)]
    assert all(gap == Decimal("25") for gap in gaps)
    assert rungs[-1] == Decimal("200")


# --------------------------------------------------------------------------- G13


def test_g13_no_09_00_09_30_half_box():
    """Audit 2.3 G13: the 2026-08-31 one-minute chart shows the light box still
    painting to 10:00; 'I wait until after 10AM' contradicts a half box."""
    market = _session()
    assert all(ref["kind"] != "ny_box_09_09_30" and "09_30" not in ref["kind"] for ref in _refs(market).values())


# --------------------------------------------------------------------------- the day read


def test_day_read_names_the_play_and_the_scan_runs_only_those_plays():
    """User instruction 2026-09-17: classify the day first and run only the
    plays that day allows."""
    market = _session()
    read = gb.session_read(market)
    assert read["day_model"] in {"sweep_and_fail", "pullback_continuation"}
    assert read["primary_play"] in read["plays"]
    document = gb.scan_b02(market, {"family": "GB-FAIL", "branch": "all"})
    plays = {episode["values"]["play"] for episode in document["episodes"]}
    assert plays <= set(read["plays"])
    skipped = {row["play"] for row in document["omissions"] if row.get("reason") == "play_not_in_the_day_read"}
    assert skipped.isdisjoint(set(read["plays"]))


def test_previous_hour_is_a_pm_reference():
    """GB p.7: 'Optional: previous hour high/low if you are trading later
    hours'. The old adapter ran hours 13 and 14 only."""
    market = _session()
    refs, objectives = _objectives(market)
    episodes = gb._scan_previous_hour(market, refs, objectives)
    for episode in episodes:
        assert episode["stages"][0]["operands"]["reference_live_from"] >= market.at(gb.PREVIOUS_HOUR_FROM)


# --------------------------------------------------------------------------- causality


def test_no_episode_is_decided_before_the_evidence_that_admitted_it():
    """An entry may never be filled before the bar that confirmed it."""
    market = _session()
    document = gb.scan_b02(market, {"family": "GB-FAIL", "branch": "all"})
    assert document["episodes"]
    for episode in document["episodes"]:
        stamps = [row["at_ns"] for row in episode["stages"] if row.get("at_ns") is not None]
        if not stamps:
            continue
        if episode["research_verdict"] == "pass":
            assert episode["decision_at"] >= max(stamps), episode["candidate_id"]
            assert episode["values"]["confirmation_delay_ns"] >= 0


def test_an_entry_priced_before_its_evidence_is_rejected_with_a_named_reason():
    """The negative control for the causality rule."""
    market = _session()
    stages = [
        gb._stage("context", "pass", market.at("10:00")),
        gb._stage("reference", "pass", market.at("10:00")),
        gb._stage("confirmation", "pass", market.at("11:00")),
    ]
    episode = gb._episode(
        market,
        family="GB-FAIL",
        branch="nyam_box",
        side="short",
        stages=stages,
        rules=[],
        decision_at=market.at("10:30"),
        entry=Decimal("100"),
        stop=Decimal("110"),
        target=Decimal("90"),
        reference=None,
        trigger=None,
        values={"confirmation_mode": "five_minute_close"},
        geometry={},
    )
    assert episode["research_verdict"] == "fail"
    assert "causality" in episode["failed"]
    assert any(
        (row.get("operands") or {}).get("reason") == "entry_precedes_evidence" for row in episode["stages"]
    )


# --------------------------------------------------------------------------- contracts


def test_scan_document_keeps_the_pipeline_contract():
    from trading_research.research.rule_discovery.source_adapters.common import episode_status, population_counts

    market = _session()
    document = fail_scan(market, {"family": "GB-FAIL", "branch": "all"})
    counts = population_counts(document)
    assert counts["episodes"] == document["N_observed"]
    assert counts["setup"] == document["p"]
    assert {episode_status(ep) for ep in document["episodes"]} <= {"setup", "no_setup", "data_unavailable", "condition_present", "condition_absent"}
    assert document["baseline_version"] == "B0.3-2026-09-17"


def test_rules_table_is_keyed_by_rule_id_with_a_source_and_a_line():
    for rule_id, row in gb.RULES.items():
        assert row["source"], rule_id
        assert row["kind"] in {"literal", "OD"}
        assert row["file_line"].startswith("green_b02.py"), rule_id
    assert set(FAIL_RULES) <= set(gb.RULES)
    assert set(VWAP_RULES) <= set(gb.RULES)


def test_author_examples_2026_09_17_is_a_superset_of_the_pinned_file():
    pinned = json.loads((REPO / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json").read_text())
    current = json.loads(EXAMPLES.read_text())
    assert {row["id"] for row in pinned["examples"]} == {row["id"] for row in current["examples"]}
    by_id = {row["id"]: row for row in current["examples"]}
    for row in pinned["examples"]:
        after = by_id[row["id"]]
        for key, value in row.items():
            if key in {"actions", "n_proper_entries"}:
                continue
            assert after[key] == value, (row["id"], key)
    marked = [
        action
        for row in current["examples"]
        for action in row.get("actions") or []
        if action.get("proper_entry")
    ]
    assert marked
    assert all(action.get("marked_by") in {"rr_tool", "narration"} for action in marked)
