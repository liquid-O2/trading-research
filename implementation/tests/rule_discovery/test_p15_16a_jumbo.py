"""Jumbo B0.3: one test per ordered defect of FIDELITY_AUDIT_2026-09-17 1.3.

Every expected value comes from the audit's statement of the source, from the
author's own printed tables, or from a dated example -- never from the adapter.
The round-1 B0.2 track-file digests are retired with the behaviour they pinned.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import json

import pytest

from trading_research.research.rule_discovery.source_adapters import jumbo as jj
from trading_research.research.rule_discovery.source_adapters.trade_selection import select_session_trades

# ``test_A01_imports_track_fixtures`` loads this module by file path, with no
# parent package, so the shared fake-market helper is imported both ways.
try:  # pragma: no cover - the path taken depends on how the module is loaded
    from .fake_market import FakeMarket, bar, flat_series
    from .selection_invariants import assert_one_position_at_a_time
except ImportError:  # pragma: no cover
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fake_market import FakeMarket, bar, flat_series
    from selection_invariants import assert_one_position_at_a_time

REPO = Path(__file__).resolve().parents[3]
EXAMPLES = REPO / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"
DAY = date(2026, 8, 20)


def _session(
    day: date = DAY,
    *,
    box_low=21258,
    box_high=21410,
    open_price=21300,
    rth_open=21300,
    prior_low=21100,
    prior_high=21500,
    val=21150,
    vah=21450,
    sweep_to=21180,
    sweep_at="09:41",
):
    """A session shaped after 2025-01-28: the 06:00-09:00 box is 21258-21410,
    the low is swept into the -0.5 projection late in the modal window and
    price reclaims it."""
    width = Decimal(str(box_high)) - Decimal(str(box_low))
    rows: list = []
    rows += flat_series(day, "18:00", 360, open_price, offset=-1)
    # the London box closes at 02:00 (JR pp.16, 63-64) and from 2026 opens at 01:15 (JR p.47): its range is made at 01:30
    rows += flat_series(day, "00:00", 90, open_price)
    rows += [bar(day, "01:30", open_price, open_price + 10, open_price - 10, open_price)]
    rows += flat_series(day, "01:31", 149, open_price)
    # the overnight low sits well below the box low, so a shallow poke at the
    # box edge cannot borrow another drawn level's coincidence
    rows += [bar(day, "04:00", open_price, open_price, box_low - 120, open_price)]
    rows += flat_series(day, "04:01", 119, open_price)
    rows += [bar(day, "06:00", open_price, box_high, box_low, open_price)]
    rows += flat_series(day, "06:01", 179, open_price)          # to 09:00
    sweep_minute = int(sweep_at[:2]) * 60 + int(sweep_at[3:])
    rows += flat_series(day, "09:00", sweep_minute - 9 * 60, rth_open)
    # seven minutes of rejection at the level, then the close back above it:
    # every 2-, 3- or 5-minute grouping of the first block is a rejection block
    # (wick larger than body, the level inside the candle) and every grouping of
    # the second closes beyond it.
    for offset in range(7):
        total = sweep_minute + offset
        rows.append(bar(day, f"{total // 60:02d}:{total % 60:02d}", box_low - 8, box_low, sweep_to, box_low - 3))
    for offset in range(7, 15):
        total = sweep_minute + offset
        rows.append(bar(day, f"{total // 60:02d}:{total % 60:02d}", box_low - 3, box_low + 17, box_low - 3, box_low + 12))
    tail = sweep_minute + 15
    rows += flat_series(day, f"{tail // 60:02d}:{tail % 60:02d}", 16 * 60 - tail, box_low + 20)
    prior = {
        "date": str(day.replace(day=day.day - 1)),
        "id": "d1",
        "low": Decimal(str(prior_low)),
        "high": Decimal(str(prior_high)),
        "open": Decimal(str(prior_low)),
        "close": Decimal(str(prior_high)),
        "known_at": 0,
        "scope": "cme_session_1800_1600",
        "window": None,
    }
    market = FakeMarket(str(day), rows, prior_sessions=[prior])
    market.b02_prior_value = {"vah": Decimal(str(vah)), "val": Decimal(str(val)), "poc": Decimal(str((val + vah) / 2)), "known_at": 0}
    market.width = width
    return market


def _scan(market, branch="all"):
    document = jj.scan_b02(market, {"branch": branch})
    return document, [ep for ep in document["episodes"] if ep["research_verdict"] == "pass"]


# --------------------------------------------------------------------------- geometry


def test_box_geometry_is_the_authors_6_9_range_with_every_internal():
    """Audit 1.1: HIGH, LOW, EQ, the 25%/75% quadrants, the range OPEN and
    CLOSE, frozen at 09:00. 2025-01-28: H 21,410, L 21,258, W 152.5."""
    market = _session()
    box = jj.box_geometry(market, "ny")
    assert (box["low"], box["high"]) == (Decimal("21258"), Decimal("21410"))
    assert box["eq"] == Decimal("21334")
    assert box["q25"] == Decimal("21296")
    assert box["q75"] == Decimal("21372")
    assert box["known_at"] == market.at("09:00")


def test_projection_ladder_matches_the_printed_levels():
    """2025-01-28: H 21,410, L 21,258, W 152.5, -0.5 at 21,182 (drawn 21,180),
    +0.5 at 21,486; 2025-10-01: H 24,805, L 24,720, +0.5 at 24,846."""
    ladder = jj.projection_ladder(21410, 21258)
    width = Decimal("152")
    assert Decimal(ladder["minus_0.5"]) == Decimal("21258") - width / 2
    assert Decimal(ladder["plus_0.5"]) == Decimal("21410") + width / 2
    second = jj.projection_ladder(24805, 24720)
    assert Decimal(second["plus_0.5"]) == Decimal("24805") + Decimal("85") / 2
    assert set(ladder) >= {f"{side}_{m}" for side in ("plus", "minus") for m in ("0.33", "0.5", "0.66", "1", "1.33", "1.66", "2")}


# --------------------------------------------------------------------------- J1


def test_j1_objective_ladder_is_eq_then_range_open_then_the_opposite_edge():
    """Audit 1.3 J1: the objective is EQ, mislabelled ``plus_0_5`` in the old
    adapter. The author's 2026-01-02 table over 2,043 sweeps prints EQ 92.8%,
    range open 86.8%, opposite edge 66.2% for the 09:00-10:00 segment."""
    market = _session()
    box = jj.box_geometry(market, "ny")
    ladder = jj.objective_ladder(box, "long")
    assert [row["name"] for row in ladder] == ["eq", "range_open", "opposite_edge", "half_projection", "extension_band"]
    assert ladder[0]["price"] == box["eq"]
    assert ladder[2]["price"] == box["high"]
    assert ladder[3]["price"] == box["ladder"]["plus_0.5"]
    short = jj.objective_ladder(box, "short")
    assert short[2]["price"] == box["low"]
    assert short[3]["price"] == box["ladder"]["minus_0.5"]


def test_j1_outbound_objective_is_the_real_half_projection():
    """The old adapter's ``plus_0_5`` was ``edge + 0.5 x W`` mislabelled; the
    outbound objective is that projection and says so."""
    market = _session()
    episodes, _omissions = jj._scan_judas_outbound(market)
    box = jj.box_geometry(market, "ny")
    for episode in episodes:
        target = Decimal(str(episode["geometry"]["target"]))
        expected = box["ladder"]["minus_0.5"] if episode["side"] == "short" else box["ladder"]["plus_0.5"]
        assert target == expected


# --------------------------------------------------------------------------- J2


def test_j2_confirmation_runs_from_0900_not_0940():
    """Audit 1.3 J2: the author enters from 09:00 -- 09:03 on 2025-10-13 and
    2026-07-27, 09:32 on 2026-01-09, 09:33 on 2026-02-24, 09:30-09:32 on
    2026-08-28. The 09:40-09:50 window is an operand, not a gate."""
    market = _session(sweep_at="09:05")
    _document, passes = _scan(market, "judas_reversal")
    assert passes, "a 09:05 sweep and reclaim must be admissible"
    early = [ep for ep in passes if ep["decision_at"] < market.at("09:40")]
    assert early
    stage = next(row for row in early[0]["stages"] if row["stage"] == "trigger")
    assert stage["operands"]["in_modal_window"] is False
    assert stage["operands"]["modal_window"] == ["09:40", "09:50"]


def test_j2_modal_window_is_recorded_when_the_sweep_is_inside_it():
    market = _session(sweep_at="09:41")
    _document, passes = _scan(market, "judas_reversal")
    assert passes
    stage = next(row for row in passes[0]["stages"] if row["stage"] == "trigger")
    assert stage["operands"]["in_modal_window"] is True


# --------------------------------------------------------------------------- J3


def test_j3_opening_range_retracement_is_a_sibling_of_the_single_break_case():
    """Audit 1.3 J3: the 15-minute OR mid / quadrant retracement (2026-02-24,
    2026-07-16, 2026-07-21) had no branch. Fidelity pass 8 (JR: "range mid
    provided the entry area", 2026-07-27 09:02): the single-break case from
    09:00 trades the EQ, the purged case from 09:30 adds the quadrants, the
    range open and the 15-minute opening-range lines; the rotation play trades
    the range edges and the prior value edges, never the opening range."""
    market = _session()
    extended, omissions = jj._eq_lines(market, "single_extended")
    assert not omissions
    assert {kind for kind, _px in extended["lines"]} == {"eq"}
    purged, _omissions = jj._eq_lines(market, "single_purged")
    kinds = {kind for kind, _px in purged["lines"]}
    assert {"eq", "q25", "q75", "range_open", "or15_mid", "or15_q25", "or15_q75"} <= kinds
    rotation, _omissions = jj._eq_lines(market, "internal_rotation")
    rotation_kinds = {kind for kind, _px in rotation["lines"]}
    assert not any(kind.startswith("or15") for kind in rotation_kinds)
    # "open inside prior RTH value: range scalps" (2026-07-10): the in-value day
    # is scalped at the range edges too.
    assert {"box_low", "box_high"} <= rotation_kinds


# --------------------------------------------------------------------------- J4


def test_j4_the_location_set_is_every_drawn_liquidity_level():
    """Audit 1.3 J4: the author sweeps the London high, the D-1/D-2 highs, the
    pre-market swing high and the prior RTH levels, not only R-Hi/R-Lo."""
    market = _session()
    box = jj.box_geometry(market, "ny")
    kinds = {row["kind"] for row in jj.drawn_levels(market, box)}
    assert {"box_low", "box_high", "london_low", "london_high", "asia_low", "asia_high", "onl", "onh", "d1_low", "d1_high", "prth_val", "prth_vah"} <= kinds


# --------------------------------------------------------------------------- J5


@pytest.mark.parametrize(
    "depth_fraction,expected",
    [(Decimal("0.2"), "inside_0_0.33"), (Decimal("0.5"), "band_0.33_0.66"), (Decimal("0.9"), "beyond_0.66")],
)
def test_j5_sweep_depth_is_classified_against_the_mean_reversal_band(depth_fraction, expected):
    """Audit 1.3 J5: the author's location is the exhaustion band 0.33-0.66,
    0.5, a P-zone or an overnight extreme -- not any break of the edge."""
    width = Decimal("152")
    assert jj.depth_class(width * depth_fraction, width) == expected


def test_j5_a_shallow_poke_is_still_the_raid_and_its_depth_is_an_operand():
    """JR p.20 (fidelity pass 8): the Judas is any raid of the 6-9 edge that
    fails; how deep it went is recorded for the grading layer, not gated. The
    earlier negative control (a poke short of the 0.33-0.66 band failed at the
    location stage) is retired with that reading."""
    market = _session(sweep_to=21257)  # a poke just below the 21258 low
    document = jj.scan_b02(market, {"branch": "judas_reversal"})
    swept = [
        ep
        for ep in document["episodes"]
        if ep["values"].get("location_kind") == "edge_sweep" and ep["values"].get("reference_kind") == "box_low"
    ]
    assert swept
    stage = next(row for row in swept[0]["stages"] if row["stage"] == "location")
    assert stage["verdict"] == "pass"
    assert stage["operands"]["reason"] is None
    width = Decimal(str(jj.box_geometry(market, "ny")["width"]))
    assert Decimal(str(stage["operands"]["depth_points"])) < width / 3
    assert stage["operands"]["depth_class"] == "inside_0_0.33"


# --------------------------------------------------------------------------- J6 and the day read


def test_j6_the_day_read_is_recorded_with_its_inputs_and_gates_the_plays():
    """Audit 1.3 J6 and the user instruction of 2026-09-17: the day is
    classified before the open and only the plays it allows are run."""
    market = _session()
    context = jj.session_context(market)
    read = context["read"]
    assert set(read["inputs"]) >= {"range_pct", "range_bin", "open_location", "overnight_purged_high", "overnight_purged_low", "edges_still_drawn"}
    # the two outside reads (TBR p.12, pp.22-24) are recorded with their availability, never guessed:
    # the fixture has no prior session to compare ES against, so the sister read must say so
    assert read["sister_index"] == {"available": False} and "sister_index_relative_strength" in read["unavailable_inputs"]
    assert ("news_calendar" in read["unavailable_inputs"]) == (not read["news_week"]["available"])
    document = jj.scan_b02(market, {"branch": "all"})
    assert not [row for row in document["omissions"] if row.get("reason") == "scan_error"], "a branch raised"
    plays = {ep["values"]["play"] for ep in document["episodes"]}
    assert plays <= set(read["plays"])
    # J-C: every play stays available; a branch is left out only by the read
    # condition it needs, and the omission names that condition.
    reasons = {row.get("reason") for row in document["omissions"]}
    assert "play_not_in_the_day_read" not in reasons
    assert ("read_has_no_break_direction" in reasons) == (read["trend_direction"] is None)
    assert ("rotation_needs_inside_value_or_big_range" in reasons) == (not (read["open_inside_value"] or read["big_range"]))


def test_j6_the_classification_chooses_the_primary_play_and_never_empties_the_day():
    """Coordinator guidance J-C, 2026-09-17: the plays are observed, not
    switched by a threshold. "Discard mean reversion and range double breaks
    when these things align" (2026-07-28) chooses which play leads, and the
    author still trades the EQ on any day ("same framework when having a big
    6-9 range > long/short the EQ")."""
    trend = _session(box_low=21000, box_high=21500, open_price=20900, rth_open=20900, prior_low=21200, prior_high=21600, val=21250, vah=21550)
    read = jj.session_context(trend)["read"]
    assert read["classification"] == "single_break"
    assert read["primary_play"] == "single_break"
    assert {"double_break", "single_break", "big_range_eq", "london"} <= set(read["plays"])

    balanced = _session()
    other = jj.session_context(balanced)["read"]
    assert other["classification"] == "double_break"
    assert other["primary_play"] == "double_break"
    assert {"double_break", "single_break", "big_range_eq", "london"} <= set(other["plays"])


def test_j_c_the_single_break_side_follows_the_break_the_session_shows():
    """2026-07-27: "single break behaviour through A period, range mid provided
    the entry area" -- one edge gone, the other untouched, and the trade is the
    break's own direction."""
    trend = _session(box_low=21000, box_high=21500, open_price=20900, rth_open=20900, prior_low=21200, prior_high=21600, val=21250, vah=21550)
    read = jj.session_context(trend)["read"]
    assert read["classification"] == "single_break"
    assert read["trend_direction"] == "short"
    purged, _omissions = jj._eq_lines(trend, "single_purged")
    assert purged["sides"] == ("short",), "the purged case runs the break's own way"
    extended, _omissions = jj._eq_lines(trend, "single_extended")
    assert extended["sides"] == ("long", "short"), "the pre-open EQ case waits for the tape to show the break"
    assert jj.session_context(_session())["read"]["trend_direction"] is None


# --------------------------------------------------------------------------- J7 and J8


def test_j7_london_confirmation_accepts_any_of_the_2m_3m_5m_signatures():
    """Audit 1.3 J7: the old London branch accepted the 3-minute orderblock
    alone; TBR pp.27-29 names 2/3/5-minute orderblocks and the rejection block."""
    rule = jj.RULES["JJ-CONFIRM-any-2m-3m-5m-ob-rb-absorption"]
    assert rule["parameters"]["timeframes"] == [2, 3, 5]
    assert set(rule["parameters"]["signatures"]) == {"orderblock", "rejection_block", "absorption"}


def test_j8_london_trades_the_raid_of_the_london_range_edge():
    """Audit 1.3 J8 read the 2025-10-07 and 2025-10-08 London entries as
    25%-line fills with no edge sweep; on the tape (REPLAY_JJ, fidelity round
    8) both reproduce at the sweep of the London high within 10 points. The
    location is the London edge (or a drawn level live from 02:00), and a
    failure at the location stage never blames the raid itself."""
    market = _session()
    episodes, _omissions = jj._scan_other_session(market)
    assert episodes
    kinds = set()
    for episode in episodes:
        stage = next(row for row in episode["stages"] if row["stage"] == "location")
        kinds.add(stage["operands"]["kind"])
        assert "box_edge_swept" not in stage["operands"]
        assert stage["operands"]["reason"] != "box_edge_swept"
    assert kinds & {"london_high", "london_low"}


# --------------------------------------------------------------------------- J9


@pytest.mark.parametrize(
    "pct,expected",
    [("0.2", "0-0.3"), ("0.42", "0.3-0.5"), ("0.6", "0.5-0.8"), ("1.0", "0.8-1.2"), ("1.5", "1.2+")],
)
def test_j9_range_size_bins_are_the_authors_five(pct, expected):
    """The author's 2026-06-08 table over 3,249 days: 0-0.3 / 0.3-0.5 /
    0.5-0.8 / 0.8-1.2 / 1.2+ percent of price, and his own printed 0.42%."""
    price = Decimal("10000")
    width = price * Decimal(pct) / Decimal("100")
    assert jj.range_class(width, price)["bin"] == expected


def test_j9_the_range_size_bin_is_recorded_on_every_episode_and_in_the_read():
    """Audit 1.3 J9: the old single_extended never read the range size at all.
    It is now an input of the day read and an operand of every episode; after
    the coordinator's J-C it is the primary-play choice, not a gate."""
    market = _session(box_low=21290, box_high=21310)  # a 20-point range, about 0.09%
    read = jj.session_context(market)["read"]
    assert read["inputs"]["range_bin"] == "0-0.3"
    assert read["inputs"]["range_pct"] < Decimal("0.3")
    document = jj.scan_b02(market, {"branch": "all"})
    bins = {ep["stages"][0]["operands"].get("range_bin") for ep in document["episodes"]}
    assert bins == {"0-0.3"}


# --------------------------------------------------------------------------- J10 / J11 / J12


@pytest.mark.parametrize(
    "location,purge,expected",
    [
        ("below_val", {"available": True, "purged_low": True, "purged_high": False}, "short"),
        ("above_vah", {"available": True, "purged_high": True, "purged_low": False}, "long"),
        ("below_val", {"available": True, "purged_low": True, "purged_high": True}, "short"),
        ("inside_value", {"available": True, "purged_low": True, "purged_high": True}, None),
        ("below_val", {"available": False}, "short"),
    ],
)
def test_j10_the_single_break_direction_is_the_purged_side_then_the_open_side(location, purge, expected):
    """Audit 1.3 J10 / JR p.34: the purge continues -- 2026-07-28 opened below
    the prior RTH value low with the overnight low already taken and the day
    was "continuation down". One side purged names the direction; both purged
    or none leaves it to the side of the open outside value; an open inside
    value has no break direction to follow."""
    context = {"range_class": {"pct": Decimal("1.5"), "bin": "1.2+"}, "purge": purge, "open_location": location, "rth_open_location": location, "levels": []}
    read = jj.session_read(_session(), context)
    assert read["classification"] == "single_break"
    assert read["trend_direction"] == expected


def test_j11_single_purged_window_is_the_am_with_0940_0950_as_the_add_window():
    """Audit 1.3 J11: the old window was 09:40-09:50 only; the source has the
    AM expansion with that window as the add."""
    rule = jj.RULES["JJ-SINGLE-PURGED-am-window-and-projection-objective"]
    assert rule["parameters"]["window"] == "09:00-12:00"
    assert rule["parameters"]["add_window"] == ["09:40", "09:50"]


def test_j12_single_purged_objective_is_the_projection_not_the_range_edge():
    """Audit 1.3 J12: targets at the -1 / -1.33 / -1.66 projections."""
    market = _session(box_low=21000, box_high=21500, open_price=20900, rth_open=20900, prior_low=21200, prior_high=21600, val=21250, vah=21550)
    box = jj.box_geometry(market, "ny")
    plan, _omissions = jj._eq_lines(market, "single_purged")
    assert plan["sides"] == ("short",)
    ladder = plan["objective"]["short"]
    names = [rung["name"] for rung in ladder]
    assert {"minus_1", "minus_1.33"} <= set(names)
    assert names[-1] == "minus_1.33", "the far objective is a projection"
    prices = [Decimal(str(rung["price"])) for rung in ladder]
    assert prices == sorted(prices, reverse=True)
    assert prices[-1] == box["ladder"]["minus_1.33"]
    assert prices[-1] not in {box["low"], box["high"]}


# --------------------------------------------------------------------------- J13


def test_j13_sessionstat_is_computed_from_the_tape_when_asked():
    """Audit 1.3 J13: the manual defines the envelope (60-session mean and
    median excursion of the selected clock from that session's open); the old
    adapter treated it as an injected readout."""
    assert jj.SESSIONSTAT_SAMPLE == 60
    market = _session()
    assert jj.sessionstat_envelope(market) is None  # not computed unless asked
    market.jj_sessionstat = True
    market.b02_prior_sessions = []
    assert jj.sessionstat_envelope(market) is None  # fewer than ten windows: no envelope, no guess
    market.sessionstat_box = {"window": ["09:00", "12:00"], "high_mean": Decimal("75.28"), "low_mean": Decimal("37.14"), "sample": 60}
    assert jj.sessionstat_envelope(market)["high_mean"] == Decimal("75.28")


# --------------------------------------------------------------------------- frequency


def test_frequency_selection_takes_the_chosen_play_first_and_keeps_one_position(monkeypatch):
    """Audit 1.1 'Sizing and frequency': one thesis per session, one to four
    round trips. The EXECUTED list is one position at a time with adds and
    flips, bounded per segment, and the day's play leads it in New York. The
    CANDIDATE list is what he chooses from: since 2026-09-18 every admitted
    opportunity once, whatever the day's play (six of his tickets are outside
    the play or past the caps); the gated list of 2026-09-17 stays available
    and the open list must contain it."""
    market = _session()
    document = jj.scan_b02(market, {"branch": "all"})
    assert not [row for row in document["omissions"] if row.get("reason") == "scan_error"], "a branch raised"
    assert {ep["branch"] for ep in document["episodes"]} >= {"single_purged", "internal_rotation"}, "the EQ plays scan on the fixture"
    selection = document["selection"]
    assert selection["primary_play"] == document["day_read"]["primary_play"]
    executed = selection["executed"]
    assert executed["n_round_trips"] <= jj.NY_ROUND_TRIPS + jj.LONDON_ROUND_TRIPS
    assert executed["n_round_trips"] <= executed["n_entries"]
    assert_one_position_at_a_time(executed["entries"])
    new_york = [row for row in executed["entries"] if row["branch"] != "other_session"]
    if new_york and not selection["fallback_play_used"]:
        assert jj.PLAY_OF_BRANCH[new_york[0]["branch"]] == selection["primary_play"], "the day's play leads"

    monkeypatch.setattr(jj, "CANDIDATES_GATE_BY_PLAY", True)
    gated = jj.scan_b02(market, {"branch": "all"})["selection"]
    assert gated["n_entries"] <= jj.NY_ROUND_TRIPS + jj.LONDON_ROUND_TRIPS
    assert gated["executed"]["entries"] == executed["entries"], "the switch does not touch the executed list"
    ident = lambda row: (row["branch"], row["side"], row["decision_at"], str(row["entry"]))
    assert {ident(row) for row in gated["entries"]} <= {ident(row) for row in selection["entries"]}, "opening the list loses no candidate"
    assert selection["n_entries"] > gated["n_entries"], "the fixture has opportunities outside the day's play"


# --------------------------------------------------------------------------- causality


def test_no_episode_is_decided_before_the_evidence_that_admitted_it():
    market = _session()
    document = jj.scan_b02(market, {"branch": "all"})
    assert document["episodes"]
    for episode in document["episodes"]:
        stamps = [row["at_ns"] for row in episode["stages"] if row.get("at_ns") is not None]
        if not stamps or episode["research_verdict"] != "pass":
            continue
        assert episode["decision_at"] >= max(stamps), episode["candidate_id"]
        assert episode["values"]["confirmation_delay_ns"] >= 0


def test_an_entry_priced_before_its_evidence_is_rejected_with_a_named_reason():
    market = _session()
    stages = [
        jj._stage("context", "pass", market.at("09:00")),
        jj._stage("reference", "pass", market.at("09:00")),
        jj._stage("confirmation", "pass", market.at("10:00")),
    ]
    episode = jj._episode(
        market,
        branch="judas_reversal",
        side="long",
        stages=stages,
        decision_at=market.at("09:30"),
        entry=Decimal("100"),
        stop=Decimal("90"),
        target=Decimal("120"),
        reference=None,
        trigger=None,
        values={"reference_px": Decimal("100")},
        geometry={},
    )
    assert episode["research_verdict"] == "fail"
    assert "causality" in episode["failed"]
    assert any((row.get("operands") or {}).get("reason") == "entry_precedes_evidence" for row in episode["stages"])


# --------------------------------------------------------------------------- contracts


def test_scan_document_keeps_the_pipeline_contract():
    from trading_research.research.rule_discovery.source_adapters.common import episode_status, population_counts

    market = _session()
    document = jj.scan_b02(market, {"branch": "all"})
    counts = population_counts(document)
    assert counts["episodes"] == len(document["episodes"])
    assert counts["setup"] == document["p"]
    assert {episode_status(ep) for ep in document["episodes"]} <= {"setup", "no_setup", "data_unavailable"}
    assert document["baseline_version"] == "B0.3-2026-09-17"
    assert document["populations"]["B0.2"]["setup"] == document["p"]


def test_rules_table_is_keyed_by_rule_id_with_a_source():
    rows = jj.rules_payload()
    assert {row["rule_id"] for row in rows} == set(jj.RULES)
    for row in rows:
        assert row["source"]
        # "fitted" is a third, deliberately visible kind: a rule the sources
        # state qualitatively but never quantify, whose threshold was set on
        # named tickets. It must say which ones.
        assert row["kind"] in {"literal", "OD", "fitted"}, rule_id
        if row["kind"] == "fitted":
            assert row.get("fitted") is True, rule_id
            assert row.get("fitted_on"), rule_id
        assert row["file_line"].startswith("source_adapters/jumbo.py")


def test_published_statistics_carry_the_authors_printed_numbers():
    """JR pp.23, 37, 70 and the 2026-01-02 / 2026-06-08 tables."""
    stats = jj.compute_published_statistics(["2025-01-28"])
    assert stats["extended_range_reversal_share"] == 0.8646
    assert stats["reversal_modal_window"] == "09:40-09:50"
    assert stats["retrace_after_low_sweep"]["09:00-10:00"] == {"eq": 0.928, "range_open": 0.868, "range_high": 0.662}
    assert stats["break_classification_all_days"]["double"] == 0.448


def test_first_hour_sweep_classification_matches_the_authors_table():
    """JR p.37: one_side is high_only + low_only; both is a separate bucket."""
    assert jj.classify_first_hour_sweep(True, False) == {"high_only": 1, "low_only": 0, "both": 0, "one_side": 1}
    assert jj.classify_first_hour_sweep(True, True) == {"high_only": 0, "low_only": 0, "both": 1, "one_side": 0}
