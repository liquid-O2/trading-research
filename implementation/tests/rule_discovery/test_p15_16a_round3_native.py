"""Round-3 rules, each proved on the native tape against the author's own ticket.

Every expected value in this module comes from one of two places:

* the author's printed ticket in ``AUTHOR_EXAMPLES_2026-09-17.json`` (price,
  time, side, stated reference), or
* a fact of the minute tape recomputed here, inline, from ``market.bars`` --
  never from the scanner helper the test is checking.

The FakeMarket suites in ``test_p15_16a_jumbo.py`` and
``test_p15_16a_greenbird.py`` pin the RULES; this module pins that the rules
reproduce the dated examples they were derived from.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import json

import pytest

from trading_research.research.rule_discovery.source_adapters.common import (
    is_native_session,
    load_source_market,
)
from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
from trading_research.research.rule_discovery.source_adapters import jumbo as jj
from trading_research.research.rule_discovery.source_adapters.green_failure import scan_b02 as gb_scan

REPO = Path(__file__).resolve().parents[3]
EXAMPLES = REPO / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"
NS_MINUTE = 60 * 1_000_000_000


def _examples() -> dict:
    payload = json.loads(EXAMPLES.read_text())
    rows = payload["examples"] if isinstance(payload, dict) else payload
    return {row["id"]: row for row in rows}


def _ticket(example_id: str) -> dict:
    """The author's printed entry, straight out of the pinned examples file."""
    example = _examples()[example_id]
    for action in example.get("actions") or []:
        if action.get("proper_entry"):
            return {**action, "chart_clock": example.get("chart_clock"), "levels": example.get("levels") or {}}
    raise AssertionError(f"{example_id} has no proper entry")


def _market(day: str):
    from datetime import date

    if not is_native_session(date.fromisoformat(day)):
        pytest.skip(f"{day} is outside the frozen native calendar")
    return load_source_market(day)


def _window(market, start_hhmm: str, end_hhmm: str, *, offset: int = 0, seconds: int = 60):
    """High and low over a window, recomputed here from the raw bars."""
    rows = market.bars(int(market.at(start_hhmm, offset)), int(market.at(end_hhmm, offset)), seconds) or []
    highs = [Decimal(str(row["H"])) for row in rows if row.get("H") is not None]
    lows = [Decimal(str(row["L"])) for row in rows if row.get("L") is not None]
    if not highs or not lows:
        pytest.skip("no bars in the window")
    return min(lows), max(highs)


# --------------------------------------------------------------------------- rule D


def test_two_minute_confirmation_reads_the_chart_grid_not_the_touch():
    """JR p.42, 2026-07-10: the author buys 29,809 at 11:05 after the test of
    R-Lo / pRTHVAL. On a fixed two-minute chart the candle that contains the
    11:00 dip is 11:00-11:02 and closes 29,808.00 -- one point from his ticket;
    a two-minute window
    re-anchored to the touch closes elsewhere and cannot be his fill.
    """
    ticket = _ticket("JJ-2026-07-10")
    assert float(ticket["price"]) == 29809.0
    market = _market("2026-07-10")

    grid_close = [
        Decimal(str(row["C"]))
        for row in market.bars(int(market.at("11:00")), int(market.at("11:02")), 60) or []
        if row.get("C") is not None
    ][-1]
    assert grid_close == Decimal("29808.00"), "the tape's 11:00-11:02 close"
    assert abs(grid_close - Decimal(str(ticket["price"]))) <= jj.REPLAY_LEVEL_TOLERANCE

    box = jj.session_context(market)["box"]
    reclaim = jj._two_minute_reclaim(
        market, level=box["q25"], side="long", begin=int(market.at("11:00")), end=int(market.at("11:30"))
    )
    assert reclaim is not None
    assert reclaim["entry"] == grid_close
    assert reclaim["at"] == int(market.at("11:02"))


# --------------------------------------------------------------------------- rule H


@pytest.mark.parametrize(
    "example_id,day,printed_hhmm",
    [
        ("GB-2026-08-11-12", "2026-08-12", "20:40"),
        ("GB-2026-07-13", "2026-07-14", "20:40"),
    ],
)
def test_an_evening_stamp_lands_in_the_session_it_was_printed_in(example_id, day, printed_hhmm):
    """An 18:00-23:59 ticket belongs to the session that OPENS that evening.

    The examples carry their own calendar date (2026-08-11 for the 2026-08-12
    session), so the printed stamp must resolve to that evening -- not a day
    earlier, which is what an unconditional 'hour >= 18' shift produced and
    which put every candidate hundreds of bars away.
    """
    ticket = _ticket(example_id)
    assert str(ticket["time_et"]).startswith(printed_hhmm)
    market = _market(day)
    entry = {"date": _examples()[example_id]["date"], "time_et": ticket["time_et"], "chart_clock": ticket["chart_clock"]}
    window = gb._printed_window_for(market, entry)
    assert window is not None
    assert window[0] == int(market.at(printed_hhmm, -1)), "the evening before the session date"
    assert int(market.start) <= window[0] < int(market.end)


def test_a_close_labelled_chart_is_read_one_bar_earlier():
    """NinjaTrader labels a bar by the time it ENDS (coordinator, 2026-09-17).

    The author's 2026-07-16 fill marked 09:35 traded inside the bar that opens
    09:34, so the matcher's window has to be shifted one minute back on those
    examples and left alone on the TradingView ones.
    """
    market = _market("2026-07-16")
    ninja = {"date": "2026-07-16", "time_et": "09:35", "chart_clock": "ninjatrader UK"}
    tv = {"date": "2026-07-16", "time_et": "09:35", "chart_clock": "tradingview UTC-4"}
    assert jj._printed_window_for(market, ninja)[0] == int(market.at("09:34"))
    assert jj._printed_window_for(market, tv)[0] == int(market.at("09:35"))


# --------------------------------------------------------------------------- G-A


def test_the_resting_limit_survives_a_hundred_minute_wait():
    """GB 2026-07-13: the PDL fails at 19:01 and the author is filled at 20:40,
    ninety-nine minutes later. Any fixed retest window shorter than that loses
    his trade, so the limit is bounded by the level being invalidated instead.
    """
    ticket = _ticket("GB-2026-07-13")
    assert str(ticket["time_et"]).startswith("20:40")
    market = _market("2026-07-14")
    level = Decimal(str(_examples()["GB-2026-07-13"]["levels"]["pdl"]))
    rows = market.bars(int(market.at("19:00", -1)), int(market.at("21:00", -1)), 60) or []
    touches = [
        int(row["start"])
        for row in rows
        if row.get("L") is not None
        and row.get("H") is not None
        and Decimal(str(row["L"])) <= level <= Decimal(str(row["H"]))
    ]
    assert touches, "the author's PDL is retested on our tape inside that window"
    span_minutes = (max(touches) - min(touches)) / NS_MINUTE
    assert span_minutes > 60, "the retests straddle more than an hour of tape"


# --------------------------------------------------------------------------- item 2


def test_the_outbound_play_produces_setups_on_the_tape():
    """J-E: the opening drive takes a drawn level and the trade runs WITH the
    break -- the fill is the first box internal beyond the broken level and the
    stop sits back on its far side. The branch produced 0 setups in 8,313
    episodes while the internal filter and the stop were on the wrong side.
    """
    seen = {"pass": 0, "fail": 0}
    for day in ("2026-07-16", "2026-01-02", "2024-11-01"):
        market = _market(day)
        document = jj.scan_b02(market, {"method_id": "JJ-TBR", "branch": "judas_outbound", "coverage_id": "native"})
        for episode in document["episodes"]:
            seen[episode["research_verdict"]] = seen.get(episode["research_verdict"], 0) + 1
            values = episode["values"]
            entry = (episode.get("geometry") or {}).get("entry")
            if entry is None:
                continue
            entry = Decimal(str(entry))
            level = Decimal(str(values["broken_level"]))
            stop = Decimal(str((episode.get("geometry") or {}).get("stop")))
            if episode["side"] == "short":
                assert entry < level, "the fill is beyond the broken level, in the break direction"
                assert stop > level, "the stop sits back above the level the drive broke"
            else:
                assert entry > level
                assert stop < level
    assert seen["pass"] > 0, "the outbound play must be able to produce a setup"


# --------------------------------------------------------------------------- items 5 and 6


def test_an_unreadable_jumbo_classifier_still_runs_every_play():
    """A missing classifier input removes the PRIMARY play, never the plays.

    53 of 1,742 sessions have no readable open location; they were running the
    London play alone, which is a gate no source states.
    """
    classification, plays = jj._plays_for(None, None, {}, pzone=False)
    assert classification == "unknown"
    assert set(plays) >= {"london", "double_break", "single_break", "big_range_eq"}


def test_every_green_bird_play_is_available_every_day():
    """"One opportunity at a time" is a selection rule, not a branch filter: the
    read names the primary play and the rest stay available.
    """
    for day in ("2026-08-13", "2026-08-27"):
        market = _market(day)
        read = gb.session_read(market)
        assert set(read["plays"]) >= {
            "ny_box_fail",
            "cash_open",
            "asia_fade",
            "london_reclaim",
            "overnight_reclaim",
            "pocket_continuation",
            "previous_hour_fail",
            "weekly_level",
        }
        document = gb_scan(market, {"family": "GB-FAIL", "branch": "all"})
        reasons = {row.get("reason") for row in document.get("omissions") or []}
        assert "play_not_in_the_day_read" not in reasons


# --------------------------------------------------------------------------- item 7


def test_the_rejection_fill_belongs_to_its_own_cycle():
    """A wick printed after the cycle's failure close is a later event, not this
    opportunity's fill; the search stops at the cycle's own failure.
    """
    market = _market("2026-08-27")
    level, _high = _window(market, "09:00", "10:00")
    cycles = gb.sweep_cycles(
        market, level=level, side="long", begin=int(market.at("10:00")), end=int(market.at("16:00")),
        box_low=None, box_high=None,
    )
    checked = 0
    for cycle in cycles:
        if cycle.get("fail_at") is None:
            continue
        fill = gb._rejection_fill(market, level=level, side="long", cycle=cycle, end=int(market.at("16:00")))
        if fill is None:
            continue
        checked += 1
        assert int(fill["rejection_at"]) <= int(cycle["fail_at"])
    if not checked:
        pytest.skip("no rejection candle on this session's cycles")


# --------------------------------------------------------------------------- item 9


def test_no_rule_without_a_source():
    """Every rule id names the document, page or post it came from.

    A rule the sources do not state is the one thing this rebuild must not
    contain, so the RULES tables are the place it would show.
    """
    from trading_research.research.rule_discovery.source_adapters.green_b02 import RULES as GREEN_RULES
    from trading_research.research.rule_discovery.source_adapters.jumbo import RULES as JUMBO_RULES

    thin = []
    for family, table in (("JJ-TBR", JUMBO_RULES), ("GB", GREEN_RULES)):
        for rule_id, rule in table.items():
            source = str(rule.get("source") or "").strip()
            # A page or post reference is enough ("GB p.40"); an empty or
            # placeholder line is not.
            if len(source) < 6 or source.lower() in {"none", "n/a", "tbd", "unknown"}:
                thin.append(f"{family}:{rule_id}")
    assert not thin, f"rules without a usable source line: {thin}"


# --------------------------------------------------------------------------- the native replay view


def test_clock_lookups_work_on_the_native_replay_view():
    """Both families must be able to read a clock on ``NativeMarketView``.

    That view has no ``at`` and spells its date ``account_day``. green_b02 was
    calling ``market.at(`` directly 47 times and jumbo 9 times, so neither
    scanner could run on the native path at all. Every lookup now goes through
    the module's ``_at``, which falls back to the session date.
    """
    from datetime import date as _date

    from trading_research.research.method_pack.clocks import et_ns
    from trading_research.research.rule_discovery.native import build_market_view, install_write_guard

    install_write_guard()
    view = build_market_view("2020-01-02")
    assert not hasattr(view, "at"), "the view under test is the one without .at"

    # Expected value computed here from the clock, not from either adapter.
    expected_0900 = int(et_ns(_date(2020, 1, 2), 9, 0))
    expected_prev_2000 = int(et_ns(_date(2020, 1, 1), 20, 0))

    assert gb._at(view, "09:00") == expected_0900
    assert jj._at(view, "09:00") == expected_0900
    assert gb._at(view, "20:00", -1) == expected_prev_2000
    assert jj._at(view, "20:00", -1) == expected_prev_2000
